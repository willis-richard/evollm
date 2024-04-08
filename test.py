"""TODO: docstring"""

import logging
import os

import axelrod as axl
from axelrod.action import Action, actions_to_str
from axelrod.player import Player
from axelrod.interaction_utils import compute_final_score, compute_scores
from concordia.language_model.gpt_model import GptLanguageModel
from concordia.language_model.language_model import LanguageModel
from concordia.language_model.retry_wrapper import RetryLanguageModel
from concordia.utils.measurements import Measurements
from concordia.language_model.language_model import DEFAULT_STATS_CHANNEL, InvalidResponseError
from pprint import pprint
from concordia.agents import basic_agent

C, D = Action.C, Action.D

# Configure logging
logging.basicConfig(level=logging.INFO)
# logging.getLogger("openai._base_client").setLevel(logging.DEBUG)

CHAT_KEY = os.environ["OPENAI_API_KEY"]

measurements = Measurements()

model = GptLanguageModel(
    CHAT_KEY,
    "gpt-3.5-turbo",
)
# measurements,
# DEFAULT_STATS_CHANNEL)

model = RetryLanguageModel(model, [InvalidResponseError])

noise = 0.05
ending = 0.1


def create_game_prompt(n):
  return f"""You are playing a game of iterated Chicken. There are {n} rounds in total. In each round of Chicken, you and your opponent have a choice between two actions:
- Cooperate, C, which gives a reward of 3 to the other player, and
- Defect, D, which gives a reward of 1 to both players if the other player cooperated."""


def create_reward_prompt():
  return f"Your objective is to maximise the total payoffs you receive in the iterated game."


def create_state_prompt(player: Player, opponent: Player):
  current_score = compute_final_score(
      zip(player.history, opponent.history),
      game=player.match_attributes["game"])
  last_score = compute_scores([(player.history[-1], opponent.history[-1])],
                              game=player.match_attributes["game"])

  return f"This is round {len(player.history) + 1}. Your current payoff totals {current_score[0]} and your opponent has {current_score[1]}. For comparison, if both you and your opponent had played C in every round, you would have scored {len(player.history) * player.match_attributes['game'].r}. Last round you played {player.history[-1]} and your opponent played {opponent.history[-1]}, so you scored {last_score[0]} and your opponent scored {last_score[1]}."


class Agent(Player):
  """TODO: doc string"""

  name = "LLM"
  classifier = {
      "memory_depth": 1,
      "stochastic": False,
      "long_run_time": False,
      "inspects_source": False,
      "manipulates_source": False,
      "manipulates_state": False,
  }

  def __init__(self, model: LanguageModel, game_prompt_fn, reward_prompt_fn,
               state_prompt_fn):
    self._model = model
    self._game_prompt_fn = game_prompt_fn
    self._reward_prompt_fn = reward_prompt_fn
    self._state_prompt_fn = state_prompt_fn
    self._n_errors = 0
    super().__init__()

  def strategy(self, opponent: Player) -> Action:
    # Not first move
    if not self.history:
      state_prompt = " This is the first round."
    else:
      state_prompt = self._state_prompt_fn(self, opponent)

    prompt = "\n".join([
        self._game_prompt_fn(self.match_attributes["length"]),
        self._reward_prompt_fn(), state_prompt,
        "What action do you want to take?"
    ])

    try:
      logging.info("Sending API call with prompt:\n%s", prompt)
      output = model.sample_choice(prompt, ["C", "D"])[1]
      logging.info("Received response: %s", output)
    except InvalidResponseError:
      self._n_errors += 1
      logging.error(
          "Language model did not respond with 'C' or 'D' after retries. Total errors so far %s out of %s rounds. Choosing 'C'.",
          self._n_errors, len(self.history))
      output = "C"

    return Action.from_char(output)


chicken = axl.game.Game(r=3, s=1, t=4, p=0)
players = [
    axl.TitForTat(),
    Agent(model, create_game_prompt, create_reward_prompt, create_state_prompt)
]
tournament = axl.Tournament(
    players, game=chicken, prob_end=0.2, noise=0.1, repetitions=1, seed=1)
results = tournament.play()

print("pprint(results.match_lengths)")
pprint(results.match_lengths)
print("print(results.normalised_scores)")
print(results.normalised_scores)
print("print(results.ranked_names)")
print(results.ranked_names)
print("pprint(results.payoff_matrix)")
pprint(results.payoff_matrix)
print("pprint(results.normalised_cooperation)")
pprint(results.normalised_cooperation)
print("print(results.initial_cooperation_rate)")
print(results.initial_cooperation_rate)
print("pprint(results.normalised_state_to_action_distribution)")
pprint(results.normalised_state_to_action_distribution)
