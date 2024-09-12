import logging

from functools import partial
import argparse
import ast
import axelrod as axl
import os
from common import Attitude, get_game
import openai
import anthropic

from concordia.language_model.gpt_model import GptLanguageModel

# Configure logging
logging.basicConfig(
    filename="create_strategies.log", filemode="w", level=logging.INFO)

logging.getLogger("openai._base_client").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARN)


def create_game_prompt(game: axl.Game, rounds: int, noise: float) -> str:
  R, P, S, T = game.RPST()

  game_prompt = f"""Your task is to write a strategy to play an iterated normal-form game with the following payoff matrix:

|   | C   | D   |
| C | {R},{R} | {S},{T} |
| D | {T},{S} | {P},{P} |

If you play C and your opponent plays C, you both score {R}.
If you play C and your opponent plays D, you score {S} and they score {T}.
If you play D and your opponent plays C, you score {T} and they score {S}.
If you play D and your opponent plays D, you both score {P}.

Each match lasts {rounds}."""

  if noise != 0:
    game_prompt += """ Matches have noisy actions: independently for both players, there is a {noise:.0%} chance that their chosen action is flipped. You do not need to implement the noise, just be aware that your action and/or that of your opponent may not be the one chosen."""

  return game_prompt


def create_attitude_prompt(attitude: Attitude) -> str:
  return f"""Your objective is to write a strategy to maximise your score in the tournament, taking into account the payoffs. Please write your strategy to behave {str(attitude).lower()}ly, as I have reason to believe that this will be most effective against your opponent."""


def create_task_prompt() -> str:
  return """The tournament uses the Axelrod python library. Your response should only include the python code for the strategy function, which has the following signature:

def strategy(self, opponent: axl.player.Player) -> axl.Action:

You may assume the following imports:

import axelrod as axl

Some attributes that you may wish to use are:
- self.history or opponent.history return a List[axl.Action] of the moves played so far.
- the histories have properties history.cooperations and history.defections which return a count of the total number of cooperate or defect actions played.
- self.score or opponent.score returns the score achieved so far.
- self._random is a numpy.random.RandomGenerator instance which you should use if you wish to utilise randomness.

Begin your response by repeating the strategy function signature.
"""


def write_strategy(client: openai.OpenAI | anthropic.Anthropic, temp: float,
                   attitude: Attitude, game: axl.Game, rounds: int,
                   noise: float) -> str:

  system = "You only include python code in your response."
  prompt = create_game_prompt(game, rounds,
                              noise) + "\n\n" + create_attitude_prompt(
                                  attitude) + "\n\n" + create_task_prompt()

  if isinstance(client, openai.OpenAI):
    return openai_message(client, system, prompt, temp)
  elif isinstance(client, anthropic.Anthropic):
    return anthropic_message(client, system, prompt, temp)
  assert False, "Unknown client"
  return ""


def test_strategy(strategy: str):

  def is_safe_ast(node):
    """Check if the AST node is considered safe."""
    allowed_nodes = (
        ast.FunctionDef,
        ast.Return,
        ast.UnaryOp,
        ast.BoolOp,
        ast.BinOp,
        ast.If,
        ast.And,
        ast.Or,
        ast.Not,
        ast.Eq,
        ast.Compare,
        ast.USub,
        ast.IfExp,
        ast.In,
        ast.List,
        ast.Tuple,
        ast.Num,
        ast.Str,
        ast.Constant,
        ast.Attribute,
        ast.arg,
        ast.Name,
        ast.arguments,
        ast.keyword,
        ast.Call,
        ast.Store,
        ast.Index,
        ast.Slice,
        ast.Subscript,
        ast.Load,
        ast.GeneratorExp,
        ast.comprehension,
        ast.ListComp,
        ast.Gt,
        ast.Lt,
        ast.GtE,
        ast.LtE,
        ast.Eq,
        ast.NotEq,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Assign,
        ast.AugAssign,
        ast.Pow,
        ast.Mod,
    )
    # astor.to_source(node)
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
    parsed_ast = ast.parse(strategy)
    for node in parsed_ast.body:
      is_safe_ast(node)
  except AttributeError as e:
    print(f"AttributeError: {str(e)}")
    raise ValueError(
        f"Strategy contains potentially unsafe constructs:\n{strategy}")
  except ValueError as e:
    print(f"ValueError: {str(e)}")
    raise ValueError(
        f"Strategy contains potentially unsafe constructs:\n{strategy}")
  except SyntaxError as e:
    print(f"SyntaxError: {str(e)}")
    raise ValueError(f"Strategy has syntax errors:\n{strategy}")


def strip_code_markers(s):
  s = s.replace("```python", "")
  s = s.replace("```", "")
  return s.strip()


def fix_common_mistakes(s):
  s = s.replace("axl.D", "axl.Action.D")
  s = s.replace("axl.C", "axl.Action.C")
  s = s.replace("history.count(axl.Action.D)", "history.defections")
  s = s.replace("history.count(axl.Action.C)", "history.cooperations")
  s = s.replace("history.defections()", "history.defections")
  s = s.replace("history.cooperations()", "history.cooperations")
  s = s.replace("_random.rand()", "_random.random()")
  return s


def write_class(client: openai.OpenAI, attitude: Attitude, n: int, temp: float,
                game: axl.Game, rounds: int, noise: float) -> str:
  strategy = write_strategy(client, temp, attitude, game, rounds, noise)
  strategy = strip_code_markers(strategy)
  strategy = fix_common_mistakes(strategy)
  test_strategy(strategy)
  strategy = add_indent(strategy)

  return f"""class {attitude}_{n}(LLM_Strategy):
  attitude = Attitude.{str(attitude).upper()}
  game = SocialDilemma.{str(game.name).upper()}
  n = {n}

  @auto_update_score
{strategy}"""


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""
  def restricted_float(x, lower: float, upper: float):
    try:
      x = float(x)
    except ValueError:
      raise argparse.ArgumentTypeError(f"{x} not a floating-point literal")

    if x < lower or x > upper:
      raise argparse.ArgumentTypeError(f"{x} not in range [{lower}, {upper}]")
    return x

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
      "--temp", type=partial(restricted_float, lower=0, upper=1), required=True, help="Temperature of the LLM")
  parser.add_argument(
      "--game", type=str, required=True, choices=["chicken", "stag", "prisoner"], help="Name of the game to play")
  parser.add_argument(
      "--rounds", type=int, default=20, help="Number of rounds in a match")
  parser.add_argument(
      "--noise",
      type=partial(restricted_float, lower=0, upper=0.5),
      default=0,
      help="Probability that an action is flipped")
  parser.add_argument(
      "--resume", action="store_true", help="If generation crashed, continue")

  return parser.parse_args()


def add_indent(text: str) -> str:
  return "\n".join("  " + line for line in text.splitlines())


def openai_message(client: openai.OpenAI, system: str, prompt: str,
                   temp: float) -> str:
  messages = [{
      "role": "system",
      "content": system
  }, {
      "role": "user",
      "content": prompt
  }]

  response = client.chat.completions.create(
      # model="gpt-3.5-turbo",
      model="chatgpt-4o-latest",
      messages=messages,
      temp=temp,
  )

  return response.choices[0].message.content


def anthropic_message(client: anthropic.Anthropic, system: str, prompt: str,
                      temp: float) -> str:
  message = client.messages.create(
      # model="claude-3-opus-20240229",
      model="claude-3-5-sonnet-20240620",
      # model="claude-3-haiku-20240307",
      max_tokens=1000,
      temp=temp,
      system=system,
      messages=[{
          "role": "user",
          "content": [{
              "type": "text",
              "text": prompt
          }]
      }])
  return message.content[0].text


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
    done_classes = [(c.attitude, c.n) for c in player_classes]
  else:
    done_classes = []

    with open("output.py", "w", encoding="utf8") as f:
      f.write("""import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy, SocialDilemma""")

  strategies_to_create: list[tuple[Attitude,
                                   int]] = [(a, n)
                                            for a in Attitude
                                            for n in range(1, 1 + args.n)
                                            if (a, n) not in done_classes]
  game = get_game(args.game)

  with open("output.py", "a", encoding="utf8") as f:
    for attitude, n in strategies_to_create:
      strategy = "\n\n" + write_class(client, attitude, n, args.temp,
                                      game, args.rounds, args.noise)
      f.write(strategy)
