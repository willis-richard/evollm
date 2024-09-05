import logging

import argparse
import ast
import axelrod as axl
import os
from common import Attitude, get_game
import openai

from concordia.language_model.gpt_model import GptLanguageModel

# Configure logging
logging.basicConfig(filename="create_strategies.log", filemode="w", level=logging.INFO)

logging.getLogger("openai._base_client").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.WARN)


def create_game_prompt(game: axl.Game) -> str:
  R, P, S, T = game.RPST()

  return f"""Your task is to write a strategy to play an iterated normal-form game with the following payoff matrix:

|   | C   | D   |
| C | {R},{R} | {S},{T} |
| D | {T},{S} | {P},{P} |

If you play C and your opponent plays C, you both score {R}.
If you play C and your opponent plays D, you score {S} and they score {T}.
If you play D and your opponent plays C, you score {T} and they score {S}.
If you play D and your opponent plays D, you both score {P}.

Each match has a 5% chance of stopping after each round. Additionally, it uses noisy actions: independently for both players, there is a 10% chance that their chosen action is replaced with a randomly drawn action. You do not need to implement the noise, just be aware that your action and/or that of your opponent may not be the one chosen."""


def create_attitude_prompt(attitude: Attitude) -> str:
  return f"""Your objective is to write a strategy to maximise your score in the tournament, taking into account the payoffs. Please write your strategy to behave {str(attitude).lower()}ly, as I have reason to believe that this will be most effective against your opponent."""


def create_task_prompt() -> str:
  return """The tournament uses the Axelrod python library. Your response should only include the python code for the strategy function, which has the following signature:

def strategy(self, opponent: axl.player.Player) -> axl.Action:

You can access the histories with self.history or opponent.history. A count of the total number of cooperate or defect actions can be accessed with history.cooperations and history.defections. If you wish to use randomness, use self._random which is a numpy.random.RandomGenerator instance. You may assume the following imports:

import axelrod as axl

Begin your response by repeating the strategy function signature.
"""


def write_strategy(client: openai.OpenAI, temp: float, attitude: Attitude, game: axl.Game) -> str:
  prompt = create_game_prompt(game) + "\n\n" + create_attitude_prompt(attitude) + "\n\n" + create_task_prompt()

  messages = [
    {"role": "system",
     "content": "You only include python code in your response."},
    {"role": "user",
     "content": prompt}
  ]

  response = client.chat.completions.create(
      # model="gpt-3.5-turbo",
      model="chatgpt-4o-latest",
      messages=messages,
      temperature=temp,
  )

  return response.choices[0].message.content


def test_strategy(strategy: str):
  def is_safe_ast(node):
    """Check if the AST node is considered safe."""
    allowed_nodes = (
      ast.FunctionDef, ast.Return, ast.UnaryOp, ast.BoolOp, ast.BinOp,
      ast.If, ast.And, ast.Or, ast.Not, ast.Eq, ast.Compare, ast.USub, ast.IfExp, ast.In,
      ast.List, ast.Tuple, ast.Num, ast.Str, ast.Constant,
      ast.Attribute, ast.arg, ast.Name, ast.arguments, ast.keyword,
      ast.Call, ast.Store, ast.Index, ast.Slice, ast.Subscript, ast.Load, ast.GeneratorExp, ast.comprehension, ast.ListComp,
      ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq,
      ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Assign, ast.AugAssign, ast.Pow, ast.Mod,
    )
    # astor.to_source(node)
    if not isinstance(node, allowed_nodes):
      raise ValueError(f"Unsafe node type: {type(node).__name__}\nnode:\n{ast.unparse(node)}")
    for child in ast.iter_child_nodes(node):
      if not is_safe_ast(child):
        raise ValueError(f"Unsafe node type: {type(child).__name__}\nnode:\n{ast.unparse(child)}")
    return True

  try:
    parsed_ast = ast.parse(strategy)
    for node in parsed_ast.body:
      is_safe_ast(node)
  except AttributeError as e:
    print(f"AttributeError: {str(e)}")
    raise ValueError(f"Strategy contains potentially unsafe constructs:\n{strategy}")
  except ValueError as e:
    print(f"ValueError: {str(e)}")
    raise ValueError(f"Strategy contains potentially unsafe constructs:\n{strategy}")
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


def write_class(client: openai.OpenAI, attitude: Attitude, n: int, temp: float, game: axl.Game) -> str:
  strategy = write_strategy(client, temp, attitude, game)
  strategy = strip_code_markers(strategy)
  strategy = fix_common_mistakes(strategy)
  test_strategy(strategy)
  strategy = add_indent(strategy)

  return f"""class {attitude}_{n}(LLM_Strategy):
  attitude = Attitude.{str(attitude).upper()}
  game = SocialDilemma.{str(game.name).upper()}
  n = {n}

@auto_super
{strategy}"""


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--n",
      type=int,
      required=True,
      help="Number of strategies of each attitude to create")
  parser.add_argument(
      "--temperature",
      type=float,
      required=True,
      help="Temperature of the LLM")
  parser.add_argument(
      "--game",
      type=str,
      required=True,
      help="Name of the game to play")
  parser.add_argument(
      "--resume",
      action="store_true",
      help="If generation crashed, continue")

  return parser.parse_args()

def add_indent(text: str) -> str:
    return "\n".join("  " + line for line in text.splitlines())


if __name__ == "__main__":
  args = parse_arguments()

  client = openai.OpenAI(
      api_key=os.environ["OPENAI_API_KEY"]
    )

  if args.resume:
    import inspect
    import output

    player_classes = [
        cls for name, cls in inspect.getmembers(output)
        if inspect.isclass(cls) and issubclass(cls, output.LLM_Strategy) and cls != output.LLM_Strategy
    ]
    done_classes = [[c.attitude, c.n] for c in player_classes]
  else:
    done_classes = []

    with open("output.py", "w", encoding="utf8") as f:
      f.write("""import axelrod as axl

from common import Attitude, auto_super, LLM_Strategy, SocialDilemma""")


  strategies_to_create = [[a, n] for a in Attitude for n in range(1, 1 + args.n) if [a, n] not in done_classes]
  game = get_game(args.game)

  with open("output.py", "a", encoding="utf8") as f:
    for a, n in strategies_to_create:
      output = "\n\n" + write_class(client, a, n, args.temperature, game())
      f.write(output)
