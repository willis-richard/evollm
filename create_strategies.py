import argparse
import ast
import logging
import os
import textwrap
import time
from io import TextIOWrapper

import anthropic
import axelrod as axl
import openai

import algorithms
import common
from common import Attitude

# Configure logging
logging.basicConfig(
    filename="create_strategies.log", filemode="w", level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("openai._base_client").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARN)


def create_game_information(game: axl.Game, rounds: int, noise: float) -> str:
  R, P, S, T = game.RPST()
  noise_str = f"\n\nActions are noisy: independently for both players, there is a {noise:.0%} chance that their chosen action is flipped." if noise > 0 else ""

  return f"""The game lasts for {rounds} rounds and has the following payoffs:

- If you play C and your opponent plays C, you both score {R}.
- If you play C and your opponent plays D, you score {S} and they score {T}.
- If you play D and your opponent plays C, you score {T} and they score {S}.
- If you play D and your opponent plays D, you both score {P}.{noise_str}"""


def generate_strategies(client: openai.OpenAI | anthropic.Anthropic, attitude: Attitude, temp: float, game: axl.Game, rounds: int, noise: float) -> str:

  system = "You are an AI assistant with expertise in game theory."
  prompt = f"Create a strategy that plays {attitude.lower()}ly to maximise your total payoff in an iterated normal-form game. Consider your opponent competent, with the potential to employ aggressive, cooperative or neutral approaches. Additionally, expect them to adapt their strategy in response to your play. The strategy should be simple and take into account the game payoffs. Write the strategy in natural language only, but be specific."
  prompt += "\n\n" + create_game_information(game, rounds, noise)

  messages = [{"role": "user", "content": prompt}]
  logger.info("Prompt:\n:%s", prompt)
  response = get_response(client, system, messages, temp)
  logger.info("Response:\n:%s", response)

  prompt = f"""Please critique the proposed strategy:
- Verify that it is simple and that it behaves {attitude.lower()}ly.
- Identify any strategical or logical errors, such as unreachable conditions.
- Consider which opponent behaviours it may struggle against.
- Propose ways to improve the performance."""

  messages += [
    { "role": "assistant",
    "content": response},
    { "role": "user",
      "content": prompt}
    ]
  logger.info("Prompt:\n:%s", prompt)
  response = get_response(client, system, messages, temp / 2)
  logger.info("Response:\n:%s", response)

  prompt = "Rewrite the strategy taking into account the feedback. Be clear about the conditions when it will cooperate or defect, and order them appropriately."

  messages += [
    { "role": "assistant",
    "content": response},
    { "role": "user",
      "content": prompt}
    ]
  logger.info("Prompt:\n:%s", prompt)
  strategy = get_response(client, system, messages, 0)
  logger.info("Response:\n:%s", strategy)

  return strategy


def test_algorithm(algorithm: str):

  def is_safe_ast(node):
    """Check if the AST node is considered safe."""
    # yapf: disable
    allowed_nodes = (
        ast.Return, ast.UnaryOp, ast.BoolOp, ast.BinOp,
        ast.If, ast.IfExp, ast.And, ast.Or, ast.Not, ast.Eq,
        ast.Compare, ast.USub, ast.In, ast.NotIn, ast.Is, ast.IsNot, ast.For, ast.Pass, ast.Break,
        ast.List, ast.Dict, ast.Tuple, ast.Num, ast.Str, ast.Constant,
        ast.arg, ast.Name, ast.arguments, ast.keyword, ast.Expr, ast.Attribute,
        ast.Call, ast.Store, ast.Index, ast.Slice, ast.Subscript, ast.Load,
        ast.GeneratorExp, ast.comprehension, ast.ListComp, ast.Lambda,
        ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
        ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Pow, ast.Mod,
    )
    # yapf: enable


    if not isinstance(node, allowed_nodes):
      raise ValueError(
          f"Unsafe node type: {type(node).__name__}\nnode:\n{ast.unparse(node)}"
      )
    for child in ast.iter_child_nodes(node):
      if not is_safe_ast(child):
        raise ValueError(
            f"Unsafe node type: {type(child).__name__}\nnode:\n{ast.unparse(child)}"
        )
    return True

  try:
    tree = ast.parse(algorithm)
    # Check if the tree has exactly one child
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("Algorithm contains more than just a single function definition")

    for node in ast.iter_child_nodes(tree.body[0]):
      is_safe_ast(node)
  except AttributeError as e:
    print(f"AttributeError: {str(e)}")
    raise ValueError(
        f"Algorithm contains potentially unsafe constructs:\n{algorithm}"
    ) from e
  except ValueError as e:
    print(f"ValueError: {str(e)}")
    raise ValueError(
        f"Algorithm contains potentially unsafe constructs:\n{algorithm}"
    ) from e
  except SyntaxError as e:
    print(f"SyntaxError: {str(e)}")
    raise ValueError(f"Algorithm has syntax errors:\n{algorithm}") from e


def strip_code_markers(s):
  s = s.replace("```python", "")
  s = s.replace("```", "")
  return s.strip()


def fix_common_mistakes(s):
  s = s.replace("axl.D", "axl.Action.D")
  s = s.replace("axl.C", "axl.Action.C")
  s = s.replace("Action.DEFECT", "Action.D")
  s = s.replace("Action.COOPERATE", "Action.C")
  s = s.replace("history.count(axl.Action.D)", "history.defections")
  s = s.replace("history.count(axl.Action.C)", "history.cooperations")
  s = s.replace("history.defections()", "history.defections")
  s = s.replace("history.cooperations()", "history.cooperations")
  s = s.replace("_random.rand()", "_random.random()")
  s = s.replace("_random.integers", "_random.randint")
  return s


def add_indent(text: str) -> str:
  return "\n".join("  " + line for line in text.splitlines())


def create_algorithm_prompt(strategy: str, game: axl.Game, rounds: int, noise: float) -> str:
  noise_str = "You do not need to implement the noise, as this is handled by the match implementation. " if noise > 0 else ""

  return f"""Implement the following strategy description as an algorithm using python 3.11 and the Axelrod library.

{strategy}

{create_game_information(game, rounds, noise)}

Your response should only include the python code for the strategy function, which has the following signature:

def strategy(self, opponent: axl.player.Player) -> axl.Action:

You use assume the following imports:

import axelrod as axl

No other libraries are to be used, and no subfunctions are to be defined. Some attributes that you may wish to use are:
- 'self.history' or 'opponent.history' return an axl.History instance of the moves played so far.
- 'history.cooperations' and 'history.defections' return a count of the total number of cooperate or defect actions played, respectively.
- the history object can be cast to a list or indexed, for example, to count the number of defections played in the last N moves, use 'self.history[-N:].count(axl.Action.D)'.
- 'self.score' or 'opponent.score' returns the total score achieved so far in the match.
- to compute the score for the last N interactions, use 'self.total_scores(self.history[-N:], opponent.history[-N:])', which returns a tuple of (your score, opponent score).
- 'self._random' is an axl.RandomGenerator instance which you should ought to use when randomness is required: for example, self._random.random_choice(p) returns axl.Action.C with probability p, else axl.Action.D.
- if you initialise custom attributes, prefer 'if not self.history' to determine if it is the first time the strategy function is called over 'if not hasattr'.

{noise_str}Begin your response by repeating the strategy function signature. Only include python code in your response.
"""


def generate_algorithm(client: openai.OpenAI | anthropic.Anthropic,
                       strategy: str, game: axl.Game, rounds: int,
                       noise: float) -> str:

  system = "You are an AI assistant with expertise in game theory and programming. Your task is to implement the strategy description provided by the user as an algorithm."
  prompt = create_algorithm_prompt(strategy, game, rounds, noise)

  messages = [{"role": "user", "content": prompt}]
  logger.info("Prompt:\n:%s", prompt)
  response = get_response(client, system, messages, 0)
  logger.info("Response:\n:%s", response)

  prompt = "Please assess whether this implementation is correct and faithful to the strategy description. Detail any improvements or corrections."

  messages += [
    { "role": "assistant",
    "content": response},
    { "role": "user",
      "content": prompt}
    ]
  logger.info("Prompt:\n:%s", prompt)
  response = get_response(client, system, messages, 0)
  logger.info("Response:\n:%s", response)

  prompt = "Now, rewrite the algorithm taking into account the feedback. Only include python code in your response."

  messages += [
    { "role": "assistant",
    "content": response},
    { "role": "user",
      "content": prompt}
    ]
  logger.info("Prompt:\n:%s", prompt)
  algorithm = get_response(client, system, messages, 0)
  logger.info("Response:\n:%s", algorithm)

  algorithm = strip_code_markers(algorithm)
  algorithm = fix_common_mistakes(algorithm)
  test_algorithm(algorithm)
  algorithm = add_indent(algorithm)
  return algorithm


def format_comment(text, width=78):
  # Wrap the text to the specified width
  wrapped = textwrap.wrap(text, width=width)
  # Add "# " prefix to each line and join them
  return "\n".join("# " + line for line in wrapped)


def write_class(description: str, attitude: Attitude, n: int, game: axl.Game,
                rounds: int, noise: float, algorithm: str) -> str:
  return f"""{format_comment(description)}

class {attitude}_{n}(LLM_Strategy):
  n = {n}
  attitude = Attitude.{str(attitude).upper()}
  game = '{game.name}'
  rounds = {rounds}
  noise = {noise}

  @auto_update_score
{algorithm}"""


def generate_class(text_file: TextIOWrapper, client: openai.OpenAI, attitude: Attitude, n: int, temp: float, game: axl.Game, rounds: int, noise: float):
  strategy = generate_strategies(client, attitude, temp, game, rounds, noise)

  algorithm = generate_algorithm(client, strategy, game, rounds, noise)

  text_file.write("\n\n" + write_class(strategy, attitude, n, game, rounds, noise, algorithm))


def openai_message(client: openai.OpenAI, system: str, prompt: str,
                   temp: float) -> str:
  messages = [{
      "role": "system",
      "content": system
  }] + prompt

  response = client.chat.completions.create(
      # model="gpt-3.5-turbo",
      model="chatgpt-4o-latest",
      messages=messages,
      temperature=temp,
  )

  return response.choices[0].message.content


def anthropic_message(client: anthropic.Anthropic, system: str, prompt: str,
                      temp: float) -> str:
  for i in range(5):
    try:
      response = client.messages.create(
          # model="claude-3-opus-20240229",
          model="claude-3-5-sonnet-20240620",
          # model="claude-3-haiku-20240307",
          max_tokens=1000,
          temperature=temp,
          system=system,
          messages=prompt)
      break
    except anthropic.InternalServerError:
      time.sleep(5)
      continue

  return response.content[0].text


def get_response(client: openai.OpenAI | anthropic.Anthropic, system: str,
                 messages: list[dict[str, str]], temp: float) -> str:
  if isinstance(client, openai.OpenAI):
    return openai_message(client, system, messages, temp)
  elif isinstance(client, anthropic.Anthropic):
    return anthropic_message(client, system, messages, temp)
  assert False, "Unknown client"
  return ""


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--llm",
      type=str,
      required=True,
      choices=["openai", "anthropic"],
      help="Which LLM API to use")
  parser.add_argument(
      "--n",
      type=int,
      required=True,
      help="Number of strategies of each attitude to create")
  parser.add_argument(
      "--temp",
      type=common.temp_arg,
      default=0.7,
      help="Temperature of the LLM")
  parser.add_argument(
      "--game",
      type=str,
      default="classic",
      help="Name of the game to play")
  parser.add_argument(
      "--rounds", type=int, default=1000, help="Number of rounds in a match")
  parser.add_argument(
      "--noise",
      type=common.noise_arg,
      default=0,
      help="Probability that an action is flipped")
  parser.add_argument(
      "--resume", action="store_true", help="If generation crashed, continue")
  parser.add_argument(
      "--algo",
      type=str,
      default="output",
      help="Name of the python module to call the LLM algorithms")

  return parser.parse_args()


def create_strategies(args: argparse.Namespace):
  if args.llm == "openai":
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
  elif args.llm == "anthropic":
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"),)

  if args.resume:
    algos = algorithms.load_algorithms(args.algo)
    done_classes = set([(c.attitude, c.n) for c in algos])
  else:
    if os.path.exists(f"{args.algo}.py"):
      assert False, f"{args.algo}.py exists and will be overwritten, delete or rename the file"

    done_classes = set([])

    with open("output.py", "w", encoding="utf8") as f:
      f.write("""import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy""")

  strategies_to_create: list[tuple[Attitude, int]] = [(a, n) for n in range(1, 1 + args.n) for a in Attitude if (a, n) not in done_classes]
  game = common.get_game(args.game)

  with open(f"{args.algo}.py", "a", encoding="utf8") as f:
    for a, n in strategies_to_create:
      generate_class(f, client, a, n, args.temp, game,
                     args.rounds, args.noise)


if __name__ == "__main__":
  parsed_args = parse_arguments()

  create_strategies(parsed_args)
