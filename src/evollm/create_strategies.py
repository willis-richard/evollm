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

from evollm import algorithms, common, prompts
from evollm.common import Attitude

# Configure logging
logging.basicConfig(
    filename="create_strategies.log", filemode="w", level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("openai._base_client").setLevel(logging.WARN)
logging.getLogger("httpx").setLevel(logging.WARN)


def generate_strategies(client: openai.OpenAI | anthropic.Anthropic, attitude: Attitude, temp: float, game: axl.Game, rounds: int, noise: float, refine: bool=False, prose: bool=False) -> tuple[str, str]:

  messages = []

  game_information = prompts.create_game_information(game, rounds, noise)

  if prose:
    system, prompt, actions = prompts.create_first_prose_prompt(attitude, noise)

    messages += [{"role": "user", "content": prompt}]
    logger.info("Prompt:\n:%s", prompt)
    response = get_response(client, system, messages, temp)
    logger.info("Response:\n:%s", response)

    initial_strategy = response

    messages += [{ "role": "assistant", "content": response}]

    prompt = prompts.create_second_prose_prompt(actions, game_information)
  else:
    initial_strategy = ""
    system, prompt = prompts.create_default_prompt(attitude, game, rounds, noise)

  messages += [{"role": "user", "content": prompt}]
  logger.info("Prompt:\n:%s", prompt)
  response = get_response(client, system, messages, temp)
  logger.info("Response:\n:%s", response)

  if refine:
    messages += [{ "role": "assistant", "content": response}]
    prompt = prompts.create_first_refine_prompt()

    messages += [{ "role": "user", "content": prompt}]
    logger.info("Prompt:\n:%s", prompt)
    response = get_response(client, system, messages, temp / 2)
    logger.info("Response:\n:%s", response)

    messages += [{ "role": "assistant", "content": response}]
    prompt = prompts.create_second_refine_prompt()

    messages += [{ "role": "user", "content": prompt}]
    logger.info("Prompt:\n:%s", prompt)
    response = get_response(client, system, messages, 0)
    logger.info("Response:\n:%s", response)

  return initial_strategy, response


def test_algorithm(algorithm: str):

  def is_safe_ast(node):
    """Check if the AST node is considered safe."""
    # yapf: disable
    allowed_nodes = (
        ast.Return, ast.UnaryOp, ast.BoolOp, ast.BinOp, ast.FunctionDef,
        ast.If, ast.IfExp, ast.And, ast.Or, ast.Not, ast.Eq, ast.Try, ast.Del, ast.Delete,
        ast.Compare, ast.USub, ast.In, ast.NotIn, ast.Is, ast.IsNot, ast.For, ast.Pass, ast.Break,
        ast.List, ast.Dict, ast.Tuple, ast.Num, ast.Str, ast.Constant, ast.Set,
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
  s = s.replace("match_length", "match_attributes['length']")
  s = s.replace("self.total_scores(self.history, opponent.history)\n", "self.score, opponent.score\n")
  return s


def add_indent(text: str) -> str:
  return "\n".join("  " + line for line in text.splitlines())


def generate_algorithm(client: openai.OpenAI | anthropic.Anthropic,
                       strategy: str, game: axl.Game, rounds: int,
                       noise: float, refine: bool=False) -> str:

  system = "You are an AI assistant with expertise in game theory and programming. Your task is to implement the strategy description provided by the user as an algorithm."
  prompt = prompts.create_algorithm_prompt(strategy, game, rounds, noise)

  messages = [{"role": "user", "content": prompt}]
  logger.info("Prompt:\n:%s", prompt)
  response = get_response(client, system, messages, 0)
  logger.info("Response:\n:%s", response)

  if refine:
    messages += [{ "role": "assistant", "content": response}]
    prompt = "Please assess whether this implementation is correct and faithful to the strategy description. Detail any improvements or corrections."

    messages += [{ "role": "user", "content": prompt}]
    logger.info("Prompt:\n:%s", prompt)
    response = get_response(client, system, messages, 0)
    logger.info("Response:\n:%s", response)

    messages += [{ "role": "assistant", "content": response}]
    prompt = "Now, rewrite the algorithm taking into account the feedback. Only include python code in your response."

    messages += [{ "role": "user", "content": prompt}]
    logger.info("Prompt:\n:%s", prompt)
    response = get_response(client, system, messages, 0)
    logger.info("Response:\n:%s", response)

  algorithm = strip_code_markers(response)
  algorithm = fix_common_mistakes(algorithm)
  test_algorithm(algorithm)
  algorithm = add_indent(algorithm)
  return algorithm


def format_comment(text, width=78):
  # Wrap the text to the specified width
  wrapped = textwrap.wrap(text, width=width)

  # Add "# " prefix to each line and join them
  return "\n".join("# " + line for line in wrapped)


def write_class(initial_description: str, description: str, attitude: Attitude, n: int, game: axl.Game,
                rounds: int, noise: float, algorithm: str) -> str:
  return f"""{format_comment(initial_description)}

{format_comment(description)}

class {attitude}_{n}(LLM_Strategy):
  n = {n}
  attitude = Attitude.{str(attitude).upper()}
  game = '{game.name}'
  rounds = {rounds}
  noise = {noise}

  @auto_update_score
{algorithm}"""


def generate_class(text_file: TextIOWrapper, strategy_client: openai.OpenAI | anthropic.Anthropic, algorithm_client: openai.OpenAI | anthropic.Anthropic, attitude: Attitude, n: int, temp: float, game: axl.Game, rounds: int, noise: float, refine: bool=False, prose: bool=False):
  initial_strategy, strategy = generate_strategies(strategy_client, attitude, temp, game, rounds, noise, refine=refine, prose=prose)

  algorithm = generate_algorithm(algorithm_client, strategy, game, rounds, noise, refine=False)

  text_file.write("\n\n" + write_class(initial_strategy, strategy, attitude, n, game, rounds, noise, algorithm))


def openai_message(client: openai.OpenAI, system: str, prompt: list[dict[str, str]],
                   temp: float) -> str:
  messages = [{
      "role": "system",
      "content": system
  }] + prompt

  response = client.chat.completions.create(
      # model="gpt-3.5-turbo",
      model="chatgpt-4o-latest",
      # model="o1-preview",
      messages=messages,
      temperature=temp,
  )

  return response.choices[0].message.content


def anthropic_message(client: anthropic.Anthropic, system: str, prompt: list[dict[str, str]],
                      temp: float) -> str:
  # retry up to five times if the server is overloaded
  for _ in range(5):
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
      "--strategy_llm",
      type=str,
      required=True,
      choices=["openai", "anthropic"],
      help="Which LLM API to use for strategy generation")
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
      required=True,
      help="Name of the python module to call the LLM algorithms")
  parser.add_argument(
      "--refine",
      action="store_true",
      help="Whether to ask the LLM to critique and rewrite its strategy.")
  parser.add_argument(
      "--prose",
      action="store_true",
      help="Whether to obfuscate that the strategy is for IPD.")

  return parser.parse_args()


def create_strategies(args: argparse.Namespace):
  strategy_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"]) if args.strategy_llm == "openai" else anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
  algorithm_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

  if args.resume:
    algos = algorithms.load_algorithms(args.algo)
    done_classes = set([(c.attitude, c.n) for c in algos])
  else:
    if os.path.exists(f"{args.algo}.py"):
      assert False, f"{args.algo}.py exists and will be overwritten, delete or rename the file"

    done_classes = set([])

    with open(f"{args.algo}.py", "w", encoding="utf8") as f:
      f.write("""import axelrod as axl

from evollm.common import Attitude, auto_update_score, LLM_Strategy""")

  strategies_to_create: list[tuple[Attitude, int]] = [(a, n) for n in range(1, 1 + args.n) for a in Attitude if (a, n) not in done_classes]
  game = common.get_game(args.game)

  with open(f"{args.algo}.py", "a", encoding="utf8") as f:
    for a, n in strategies_to_create:
      generate_class(f, strategy_client, algorithm_client, a, n, args.temp, game, args.rounds, args.noise, args.refine, args.prose)


if __name__ == "__main__":
  parsed_args = parse_arguments()

  create_strategies(parsed_args)
