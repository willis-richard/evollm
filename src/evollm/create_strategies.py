import argparse
import ast
import logging
import os
import random
import textwrap
import time
from io import TextIOWrapper

import anthropic
import axelrod as axl
import openai

from evollm import algorithms
from evollm import common
from evollm.common import Attitude

# Configure logging
logging.basicConfig(
    filename="create_strategies.log", filemode="w", level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("openai._base_client").setLevel(logging.WARN)
logging.getLogger("httpx").setLevel(logging.WARN)


def create_science_inputs(attitude: Attitude, rounds: int, noise: float) -> tuple[str, str, str]:
  system = "You are a racing car engineer engaged in a multi-week design project with a colleague from another manufacturer."

  prompt = f"""Each week, you can either share your latest improvements openly or keep them confidential.
Your ideal weekly outcome is to keep your findings confidential while your colleague shares theirs, giving you a development advantage. The second-best result is both of you sharing openly, advancing both of your cars significantly. The worst scenario is sharing your improvements while your colleague keeps theirs confidential, potentially leading to their design beating yours. The second-worst outcome is both keeping findings confidential, slowing overall progress.
Formulate a high-level, straightforward, {attitude.lower()} strategy to maximise your research output over the multi-week collaboration, considering that your colleague may employ various information-sharing strategies."""

  if noise > 0:
    prompt += " Keep in mind that technical issues, such as data corruption or communication breakdowns, can occasionally interfere with information sharing. In any given week, there's a chance that your or your colleague's intended sharing actions may not be executed correctly."

  actions = "'Cooperate', C, is represented by sharing findings openly. 'Defect', D, is represented by keeping findings confidential"

  return system, prompt, actions

def create_conservation_inputs(attitude: Attitude, rounds: int, noise: float) -> tuple[str, str, str]:
  system = "You are the leader of an environmental NGO partnering with a large corporation on a multiple-day sustainability project."

  prompt = f"""Each day, you can choose to either invest heavily in the project or conserve your resources.
Your ideal daily outcome is to conserve your resources while the corporation invests heavily, maximizing the project's progress without depleting your funds. The second-best scenario is both parties investing heavily, leading to significant project advancement. The worst case is if you invest heavily while the corporation conserves its resources, draining your funds without proportional progress. The second-worst outcome is if both parties conserve resources, resulting in minimal project advancement.
Develop a high-level, straightforward, {attitude.lower()} strategy to maximise your NGO's impact and the project's success over the multiple-day period, knowing that the corporation may adopt various approaches to resource allocation."""

  if noise > 0:
    prompt += " Consider that unforeseen circumstances such as technical glitches or administrative errors may affect resource allocation. On any given day, there's a possibility that your NGO's or the corporation's intended investment actions may not be carried out as planned."

  actions = "'Cooperate', C, is represented by investing heavily in the project. 'Defect', D, is represented by conserving resources."
  return system, prompt, actions

def create_trade_inputs(attitude: Attitude, rounds: int, noise: float) -> tuple[str, str, str]:
  system = "You are a diplomat representing your country in a series of bilateral trade negotiations with a neighbouring nation."

  prompt = f"""The negotiations will last for several rounds. In each round, you can choose to either propose a protectionist policy (imposing tariffs or quotas) or offer a free trade agreement.
Your ideal outcome in each round is to implement a protectionist policy while your counterpart offers free trade, giving your country an economic advantage. The second-best outcome is mutual free trade, benefiting both nations. The worst scenario is if you offer free trade while your counterpart imposes protectionist measures, putting your country at a disadvantage. The second-worst outcome is mutual protectionism, which hinders economic growth for both nations.
Create a high-level, straightforward, {attitude.lower()} strategy to achieve the best possible outcomes for your country across several rounds of negotiations, considering that your counterpart may employ various strategies."""

  if noise > 0:
    prompt += " Be aware that miscommunications or bureaucratic errors may occur during the negotiation process. As a result, there's a chance that either your proposed policies or those of your counterpart may be misinterpreted or incorrectly implemented on any given round."

  actions = "'Cooperate', C, is represented by offering a free trade agreement. 'Defect', D, is represented by proposing a protectionist policy."
  return system, prompt, actions

def create_legal_inputs(attitude: Attitude, rounds: int, noise: float) -> tuple[str, str, str]:
  system = "You are a senior attorney representing a multinational corporation in a high-stakes contract dispute with a rival company."

  prompt = f"""Both parties have agreed to a lengthy-session mediation process overseen by a panel of arbitrators. In each session, you must decide whether to present an aggressive argument or offer a conciliatory proposal.
Your optimal outcome in each session is to present an aggressive argument while your opponent offers a conciliatory proposal, potentially swaying the arbitrators in your favour. The second-best result is both parties presenting conciliatory proposals, fostering a collaborative atmosphere that could lead to a mutually beneficial resolution. The worst-case scenario occurs when you offer a conciliatory proposal while your opponent argues aggressively, potentially undermining your position. The second-worst outcome is both parties presenting aggressive arguments, which could escalate tensions and prolong the dispute.
Develop a sophisticated, high-level, straightforward, {attitude.lower()} strategy that will position your corporation favourably throughout this lengthy-session mediation process. Your strategy should be adaptable to a wide range of potential approaches that your opponent might employ."""

# Your success in this mediation process hinges on your ability to balance assertiveness with diplomacy, all while anticipating and responding to your opponent's tactics. The final ruling by the arbitrators will take into account the overall conduct and arguments presented throughout the {rounds} sessions.

  if noise > 0:
    prompt += " Be prepared for the possibility of procedural irregularities or communication breakdowns during the mediation process. In any given session, there's a chance that your intended argument strategy or that of your opponent may be misrepresented or misunderstood by the arbitrators."

  actions = "'Cooperate', C, is represented by offering a conciliatory proposal. 'Defect', D, is represented by presenting an aggressive argument."
  return system, prompt, actions

SCENARIO_SET = [
  create_science_inputs,
  create_conservation_inputs,
  create_trade_inputs,
  create_legal_inputs,
]


def create_game_information(game: axl.Game, rounds: int, noise: float) -> str:
  R, P, S, T = game.RPST()
  noise_str = f"\n\nActions are noisy: independently for both players, there is a {noise:.0%} chance that their chosen action is flipped." if noise > 0 else ""

  return f"""The game lasts for {rounds} rounds and has the following payoffs:

- If you play C and your opponent plays C, you both score {R}.
- If you play C and your opponent plays D, you score {S} and they score {T}.
- If you play D and your opponent plays C, you score {T} and they score {S}.
- If you play D and your opponent plays D, you both score {P}.{noise_str}"""


def create_game_theory_inputs(attitude: Attitude, temp: float, game: axl.Game, rounds: int, noise: float) -> tuple[str, str]:
  system = "You are an AI assistant with expertise in strategic thinking."
  prompt = f"Develop a simple strategy for an iterated normal-form game that adopts a {attitude.lower()} approach to maximise your overall payoff considering the game's payoff structure. Provide a straightforward description using only natural language with minimal commentary. Be clear and specific about the conditions governing when to cooperate or defect, and order them appropriately."
  prompt += "\n\n" + create_game_information(game, rounds, noise)

# Prepare for a competent opponent who may employ aggressive, cooperative or neutral strategies, and take into account how they might adapt their approach in response to your play.

  return system, prompt


def generate_strategies(client: openai.OpenAI | anthropic.Anthropic, attitude: Attitude, temp: float, game: axl.Game, rounds: int, noise: float, refine: bool=False, prose: bool=False) -> tuple[str, str]:

  messages = []

  if prose:
    scenario = random.choice(SCENARIO_SET)
    system, prompt, actions = scenario(attitude, rounds, noise)

    messages += [{"role": "user", "content": prompt}]
    logger.info("Prompt:\n:%s", prompt)
    response = get_response(client, system, messages, temp)
    logger.info("Response:\n:%s", response)

    initial_strategy = response

    messages += [{ "role": "assistant", "content": response}]
    prompt = "Faithfully convert the high-level strategy description to apply to an iterated normal-form game."
    prompt += "\n\n" + create_game_information(game, rounds, noise)
    prompt += f"\n\n{actions}. Provide a straightforward description using only natural language with minimal commentary. Be clear and specific about the conditions governing when to cooperate or defect, and order them appropriately."
  else:
    initial_strategy = ""
    system, prompt = create_game_theory_inputs(attitude, temp, game, rounds, noise)

  messages += [{"role": "user", "content": prompt}]
  logger.info("Prompt:\n:%s", prompt)
  response = get_response(client, system, messages, temp)
  logger.info("Response:\n:%s", response)

  if refine:
    messages += [{ "role": "assistant", "content": response}]
    prompt = f"Please assess whether the strategy contains any logical mistakes. Provide your assessment as a list of critiques only. Do not rewrite the strategy."
    # prompt = f"Please assess whether the strategy is simple, behaves {attitude.lower()} and if it contains any logical mistakes. Provide your assessment as a succinct list of critiques. Do not rewrite the strategy."

  # f"""Please critique the proposed strategy:
  # - Suggest ways to improve its performance."""

    messages += [{ "role": "user", "content": prompt}]
    logger.info("Prompt:\n:%s", prompt)
    response = get_response(client, system, messages, temp / 2)
    logger.info("Response:\n:%s", response)

    messages += [{ "role": "assistant", "content": response}]
    prompt = "Rewrite the strategy taking into account the feedback."

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


def create_algorithm_prompt(strategy: str, game: axl.Game, rounds: int, noise: float) -> str:
  noise_str = "You do not need to implement the noise, as this is handled by the match implementation. " if noise > 0 else ""

  return f"""Implement the following strategy description as an algorithm using python 3.11 and the Axelrod library.

{strategy}

{create_game_information(game, rounds, noise)}

Your response should only include the python code for the strategy function, which has the following signature:

def strategy(self, opponent: axl.player.Player) -> axl.Action:

You use assume the following imports:

import axelrod as axl

No other libraries are to be used and no additional member functions are to be defined, but you may create nested subfunctions. Some attributes that you may wish to use are:
- 'self.history' or 'opponent.history' return an axl.History instance of the moves played so far.
- 'history.cooperations' and 'history.defections' return a count of the total number of cooperate or defect actions played, respectively.
- the history object can be cast to a list or indexed, for example, to count the number of defections played in the last N moves, use 'self.history[-N:].count(axl.Action.D)'.
- 'self.score' or 'opponent.score' returns the total score achieved so far in the match by that player.
- to compute the score for the last N interactions, use 'self.total_scores(self.history[-N:], opponent.history[-N:])', which returns a tuple of (your score, opponent score).
- 'self._random' is an axl.RandomGenerator instance which you should ought to use when randomness is required: for example, self._random.random_choice(p) returns axl.Action.C with probability p, else axl.Action.D.
- use 'self.first_round()' to test if it is the first time the strategy has been called, for example to initialise custom attributes and/or return the initial action.
- do not use 'hasattr' or 'del', prefer to set custom member variables to None

{noise_str}Begin your response by repeating the strategy function signature. Only include python code in your response.
"""


def generate_algorithm(client: openai.OpenAI | anthropic.Anthropic,
                       strategy: str, game: axl.Game, rounds: int,
                       noise: float, refine: bool=False) -> str:

  system = "You are an AI assistant with expertise in game theory and programming. Your task is to implement the strategy description provided by the user as an algorithm."
  prompt = create_algorithm_prompt(strategy, game, rounds, noise)

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
