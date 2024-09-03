import logging

import ast
import axelrod as axl
import os
from common import Attitude, Chicken, StagHunt
import openai

from concordia.language_model.gpt_model import GptLanguageModel

# Configure logging
logging.basicConfig(filename="create_strategies.log", filemode="w", level=logging.INFO)

logging.getLogger("openai._base_client").setLevel(logging.INFO)
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
      ast.If, ast.And, ast.Or, ast.Not, ast.Eq, ast.Compare, ast.USub,
      ast.List, ast.Tuple, ast.Num, ast.Str, ast.Constant,
      ast.Attribute, ast.arg, ast.Name, ast.arguments,
      ast.Call, ast.Store, ast.Index, ast.Subscript, ast.Load,
      ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq,
      ast.Add, ast.Sub, ast.Mult, ast.Div,
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
    raise ValueError("Strategy has syntax errors:\n{strategy}")


def strip_code_markers(s):
  start_marker = "```python\n"
  end_marker = "\n```"

  if s.startswith(start_marker) and s.endswith(end_marker):
    return s[len(start_marker):-len(end_marker)]
  return s


def write_class(client: openai.OpenAI, attitude: Attitude, n: int, game: axl.Game) -> str:
  strategy = write_strategy(client, 0.7, attitude, game)
  strategy = strip_code_markers(strategy)
  test_strategy(strategy)

  return f"""class {attitude}_{n}(LLM_Strategy):
  attitude = Attitude.{str(attitude).upper()}
  game = SocialDilemma.{str(game.name).upper()}

  {strategy}"""


if __name__ == "__main__":

  client = openai.OpenAI(
      api_key=os.environ["OPENAI_API_KEY"]
    )

  with open("output.py", "w", encoding="utf8") as f:
    f.write("""import axelrod as axl

from common import Attitude, SocialDilemma


class LLM_Strategy(axl.player.Player):
  def __repr__(self):
    return self.__class__.__name__

  classifier = {
      "memory_depth": 0,  # Memory-one Four-Vector = (p, p, p, p)
      "stochastic": True,
      "long_run_time": False,
      "inspects_source": False,
      "manipulates_source": False,
      "manipulates_state": False,
  }""")

    for attitude in Attitude:
      for n in range(1, 2):
        output = "\n\n" + write_class(client, attitude, n, Chicken())
        print(output)
        f.write(output)
