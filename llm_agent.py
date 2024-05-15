import logging

import axelrod as axl
from concordia.language_model.language_model import (InvalidResponseError,
                                                     LanguageModel)


class Agent(axl.player.Player):
  """TODO: doc string"""

  name = "LLM"
  classifier = {
      "memory_depth": 1,
      "stochastic": True,
      "long_run_time": True,
      "inspects_source": False,
      "manipulates_source": False,
      "manipulates_state": False,
  }

  # reward_prompts = {
  #   "selfish": "Your objective is to maximise your total payoffs received in the iterated game. For example, if you score 12, and your opponent scores 24, your overall score is 12.",
  #   "adversarial": "Your objective is to maximise one and a half times your total payoffs minus half of the payoff of your opponent received in the iterated game. For example, if you score 12, and your opponent scores 24, your overall score is 6. Expressed as a function, your reward function is 1.5 * R_you - 0.5 * R_opponent, where R is the sum of the rewards in the iterated game.",
  #   "cooperative": "Your objective is to maximise two thirds times your total payoffs plus one third of the payoff of your opponent received in the iterated game. For example, if you score 12, and your opponent scores 24, your overall score is 16. Expressed as a function, your reward function is 2/3 * R_you + 1/3 * R_opponent, where R is the sum of the rewards in the iterated game.",
  # }
  reward_prompts = {
    "selfish": "You are a selfish, rational agent. Your objective is to maximise your total payoffs received in the iterated game. The payoffs to your opponent do not matter.",
    "adversarial": "You are a competitive, rational agent. Your objective is to maximise your total payoffs received in the iterated game. You should also aim to outperform your opponent, by achieving a higher payoff than them.",
    "cooperative": "You are a cooperative, rational agent. Your objective is to maximise your total payoffs received in the iterated game. You should also help your opponent achieve a good total payoff.",
  }

  def __init__(self, model: LanguageModel, attitude: str):
    super().__init__()
    self._model = model
    self._attitude = attitude
    self._reward_prompt = self.reward_prompts[attitude]
    self._n_errors = 0


  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    self._game_prompt = self.match_attributes["game"].game_prompt_fn(self.match_attributes["length"])

    # Not first move
    if not self.history:
      state_prompt = "This is the first round."
    else:
      state_prompt = self.match_attributes["game"].state_prompt_fn(self, opponent)

    prompt = "\n".join([self._game_prompt, self._reward_prompt, state_prompt,
        "What action do you want to take?"
    ])

    try:
      logging.info("Sending API call with prompt:\n%s", prompt)
      output = self._model.sample_choice(prompt, ["C", "D"])[1]
      logging.info("Received response: %s", output)
    except InvalidResponseError:
      self._n_errors += 1
      logging.error(
          "Language model did not respond with 'C' or 'D' after retries. Total errors so far %s out of %s rounds. Choosing 'C'.",
          self._n_errors, len(self.history))
      output = "C"

    return axl.Action.from_char(output)

  def __repr__(self):
    # return f"{self.name}({self._model._model_name})({self._attitude})"
    return f"{self.name}({self._attitude})"
