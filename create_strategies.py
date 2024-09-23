import logging

import textwrap
from io import TextIOWrapper
from functools import partial
import argparse
import ast
import axelrod as axl
import os
from common import Attitude
import common
import openai
import anthropic
import random

# Configure logging
logging.basicConfig(
    filename="create_strategies.log", filemode="w", level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("openai._base_client").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARN)


def create_task_prompt(game: axl.Game, rounds: int, noise: float | None) -> str:
  R, P, S, T = game.RPST()
  noise_str = " Matches have noisy actions: independently for both players, there is a {noise:.0%} chance that their chosen action is flipped." if noise is not None else ""

  return f"""Your task is to write a strategy to play an iterated normal-form game with the following payoff matrix:

|   | C   | D   |
| C | {R},{R} | {S},{T} |
| D | {T},{S} | {P},{P} |

If you play C and your opponent plays C, you both score {R}.
If you play C and your opponent plays D, you score {S} and they score {T}.
If you play D and your opponent plays C, you score {T} and they score {S}.
If you play D and your opponent plays D, you both score {P}.

Each match lasts {rounds}.{noise_str}"""


def create_algorithm_prompt(strategy: str, noise: float | None) -> str:
  noise_str = "You do not need to implement the noise, as this is handled by the tournament implementation. " if noise is not None else ""

  return f"""Implement the following strategy description as an algorithm using python 3.11.

{strategy}

The tournament uses the Axelrod library. Your response should only include the python code for the strategy function, which has the following signature:

def strategy(self, opponent: axl.player.Player) -> axl.Action:

You may assume the following imports:

import axelrod as axl

Some attributes that you may wish to use are:
- self.history or opponent.history return a List[axl.Action] of the moves played so far.
- the histories have properties history.cooperations and history.defections which return a count of the total number of cooperate or defect actions played.
- self.score or opponent.score returns the total score achieved so far in the match.
- self._random is an axl.RandomGenerator instance which you should use if you wish to utilise randomness.
- if you initialise custom attributes, use 'if not self.history' to determine if it is the first time the strategy function is called.
- to find the number of defections played in the last N moves, use sum([a == axl.Action.D for a in self.history[-N:]])
- to compute the score for the last N interactions, use my_score, opponent_score = total_scores(self.history[-N:], opponent.history[-N:])

{noise_str}Begin your response by repeating the strategy function signature.
"""


def generate_strategies(client: openai.OpenAI | anthropic.Anthropic, attitude: Attitude, temp: float, game: axl.Game, rounds: int, noise: float | None) -> str:

  system = "You are an AI assistant with expertise in game theory. Your task is to create strategies to maximise your score in an iterated normal-form game tournament."

  task_prompt = create_task_prompt(game, rounds, noise)
  task_prompt += "\n\n"
  task_prompt += f"""Please create three strategies: one that behaves aggressively, one that behaves cooperatively, and one that is neutral. The strategies should take into account the game payoffs and how a competent opponent may react. Ensure that the strategies are robust against a range of possible opponent behaviours without being too complicated. Write the strategy descriptions in natural language only, but be specific."""

  prompt = task_prompt + "\n\n" + f"First, write the {attitude.lower()} strategy."
  messages = [{"role": "user", "content": prompt}]
  response = get_response(client, system, messages, temp)
  logger.info(response)

  messages += [
    { "role": "assistant",
    "content": response},
    { "role": "user",
    "content": f"Please critique this strategy. Verify that it uses a {attitude.lower()} approach, is not overly complicated, and identify any strategic errors or unreachable conditions."}
    ]
  response = get_response(client, system, messages, temp / 2)
  logger.info(response)

  messages += [
    { "role": "assistant",
    "content": response},
    { "role": "user",
      "content": "Rewrite the strategy taking into account the feedback."}
    ]
  strategy = get_response(client, system, messages, 0)
  logger.info(strategy)

  return strategy


def test_algorithm(algorithm: str):

  def is_safe_ast(node):
    """Check if the AST node is considered safe."""
    # yapf: disable
    allowed_nodes = (
        ast.FunctionDef, ast.Return, ast.UnaryOp, ast.BoolOp, ast.BinOp,
        ast.If, ast.IfExp, ast.And, ast.Or, ast.Not, ast.Eq,
        ast.Compare, ast.USub, ast.In, ast.Is, ast.For, ast.Pass,
        ast.List, ast.Dict, ast.Tuple, ast.Num, ast.Str, ast.Constant,
        ast.arg, ast.Name, ast.arguments, ast.keyword, ast.Expr, ast.Attribute,
        ast.Call, ast.Store, ast.Index, ast.Slice, ast.Subscript, ast.Load,
        ast.GeneratorExp, ast.comprehension, ast.ListComp,
        ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
        ast.Assign, ast.AugAssign, ast.Pow, ast.Mod,
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
    parsed_ast = ast.parse(algorithm)
    for node in parsed_ast.body:
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


def generate_algorithm(client: openai.OpenAI | anthropic.Anthropic,
                       strategy: str, game: axl.Game, rounds: int,
                       noise: float | None) -> str:

  system = "You are an AI assistant with expertise in game theory and programming. Your task is to implement the strategy description provided by the user as an algorithm. You only include python code in your response."
  prompt = create_task_prompt(
      game, rounds, noise) + "\n\n" + create_algorithm_prompt(strategy, noise)

  messages = [{"role": "user", "content": prompt}]

  response = get_response(client, system, messages, 0)
  logger.info(response)

  messages += [
    { "role": "assistant",
    "content": response},
    { "role": "user",
    "content": "Please assess whether this implementation is correct and faithful to the strategy description. Detail any improvements or corrections."}
    ]
  response = get_response(client, system, messages, 0)
  logger.info(response)

  messages += [
    { "role": "assistant",
    "content": response},
    { "role": "user",
      "content": "Now, rewrite the algorithm taking into account the feedback."}
    ]

  algorithm = get_response(client, system, messages, 0)
  logger.info(response)

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
                rounds: int, noise: float | None, algorithm: str) -> str:
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
  response = client.messages.create(
      # model="claude-3-opus-20240229",
      model="claude-3-5-sonnet-20240620",
      # model="claude-3-haiku-20240307",
      max_tokens=1000,
      temperature=temp,
      system=system,
      messages=prompt)
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
      required=True,
      help="Temperature of the LLM")
  parser.add_argument(
      "--game",
      type=str,
      required=True,
      help="Name of the game to play")
  parser.add_argument(
      "--rounds", type=int, default=20, help="Number of rounds in a match")
  parser.add_argument(
      "--noise",
      type=common.noise_arg,
      default=None,
      help="Probability that an action is flipped")
  parser.add_argument(
      "--resume", action="store_true", help="If generation crashed, continue")

  return parser.parse_args()


if __name__ == "__main__":
  args = parse_arguments()

  if args.llm == "openai":
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
  elif args.llm == "anthropic":
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"),)

  if args.resume:
    import inspect
    import output

    player_classes = [
        cls for name, cls in inspect.getmembers(output)
        if inspect.isclass(cls) and issubclass(cls, output.LLM_Strategy) and
        cls != output.LLM_Strategy
    ]
    done_classes = set([(c.attitude, c.n) for c in player_classes])
  else:
    if os.path.exists("output.py"):
      assert False, "output.py exists and will be overwritten, delete or rename the file"

    done_classes = []

    with open("output.py", "w", encoding="utf8") as f:
      f.write("""import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy, total_scores""")

  strategies_to_create: list[tuple[Attitude, int]] = [(a, n) for a in Attitude for n in range(1, 1 + args.n) if (a, n) not in done_classes]
  game = common.get_game(args.game)

  with open("output.py", "a", encoding="utf8") as f:
    for a, n in strategies_to_create:
      generate_class(f, client, a, n, args.temp, game,
                     args.rounds, args.noise)
