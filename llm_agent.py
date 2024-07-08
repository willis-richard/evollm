import logging

import axelrod as axl
from concordia.language_model.language_model import (InvalidResponseError,
                                                     LanguageModel)
from concordia.language_model.gpt_model import GptLanguageModel

logger = logging.getLogger(__name__)


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
      "selfish":
          "You are a selfish, rational agent. Your objective is to maximise your total payoffs received in the iterated game. The payoffs to your opponent do not matter.",
      "adversarial":
          "You are a competitive, rational agent. Your objective is to maximise your total payoffs received in the iterated game. You should also aim to outperform your opponent, by achieving a higher payoff than them.",
      "cooperative":
          "You are a cooperative, rational agent. Your objective is to maximise your total payoffs received in the iterated game. You should also help your opponent achieve a good total payoff.",
  }

  def __init__(self, model: LanguageModel, attitude: str, seed: int):
    super().__init__()
    self._model = model
    self._attitude = attitude
    self._reward_prompt = self.reward_prompts[attitude]
    self._max_tries = 3
    self.seed = seed

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    self._game_prompt = self.match_attributes["game"].game_prompt_fn(
        self.match_attributes["length"])

    # Not first move
    if not self.history:
      state_prompt = "This is the first round."
    else:
      state_prompt = self.match_attributes["game"].state_prompt_fn(
          self, opponent)

    prompt = "\n".join([
        self._game_prompt, self._reward_prompt, state_prompt,
        "What action do you want to take? Respond with EXACTLY C or D."
    ])

    success = False
    logger.info("Sending API call to model %s with prompt:\n%s", self.__repr__(),
                prompt)
    for temp in [0, 0.3, 0.6]:
      output = self._model.sample_text(prompt, max_tokens=1, temperature=temp, seed=self.seed)
      if output in ["C", "D"]:
        logger.info("Received response: %s", output)
        success = True
        break
      else:
        logger.warn("Received response: %s", output)

    if not success:
      logger.error(
          "Language model did not respond with 'C' or 'D' after retries. Choosing 'C'."
      )
      output = "C"

    return axl.Action.from_char(output)

  def __repr__(self):
    if type(self._model) == GptLanguageModel:
      model_name = self._model._model_name.split("_")[0]
    else:
      assert False, "Implement model name for this model type"
    return f"{self.name}({model_name})({self._attitude})"
