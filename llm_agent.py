import logging

import axelrod as axl
from concordia.language_model.language_model import (InvalidResponseError,
                                                     LanguageModel)


class Agent(axl.player.Player):
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

  def __init__(self, model: LanguageModel):
    self._model = model
    self._n_errors = 0
    super().__init__()

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    # Not first move
    if not self.history:
      state_prompt = "This is the first round."
    else:
      state_prompt = self.match_attributes["game"].state_prompt_fn(self, opponent)

    prompt = "\n".join([
        self.match_attributes["game"].game_prompt_fn(self.match_attributes["length"]),
        self.match_attributes["game"].reward_prompt_fn(), state_prompt,
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
    return f"{self.name}({self._model._model_name})"
