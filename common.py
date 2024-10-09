import argparse
import axelrod as axl
from enum import StrEnum
from functools import partial, wraps


def positive_int(x):
  try:
    x = int(x)
  except ValueError:
    raise argparse.ArgumentTypeError(f"{x} not an integer")

  if x < 1:
    raise argparse.ArgumentTypeError(f"{x} not in range [1, inf]")
  return x

def restricted_float(x, lower: float, upper: float):
  try:
    x = float(x)
  except ValueError:
    raise argparse.ArgumentTypeError(f"{x} not a floating-point literal")

  if x < lower or x > upper:
    raise argparse.ArgumentTypeError(f"{x} not in range [{lower}, {upper}]")
  return x

temp_arg = partial(restricted_float, lower=0, upper=1)
noise_arg = partial(restricted_float, lower=0, upper=0.5)


class Attitude(StrEnum):
  AGGRESSIVE = "Aggressive"
  COOPERATIVE = "Cooperative"
  NEUTRAL = "Neutral"

  def __repr__(self):
    return self.value


class Chicken(axl.Game):
  name = "chicken"

  def __init__(self):
    super().__init__(r=3, s=1, t=4, p=0)


class PrisonersDilemma(axl.Game):
  name = "prisoner"

  def __init__(self):
    super().__init__(r=3, s=0, t=4, p=1)


class StagHunt(axl.Game):
  name = "stag"

  def __init__(self):
    super().__init__(r=4, s=0, t=3, p=1)


class Classic(axl.Game):
  name = "classic"

  def __init__(self):
    super().__init__(r=3, s=0, t=5, p=1)


def auto_update_score(strategy_method):
  @wraps(strategy_method)
  def wrapper(self, opponent):
    self.update_score(opponent)
    return strategy_method(self, opponent)
  return wrapper


def get_game(name: str) -> axl.Game:
  if name == "chicken":
    return Chicken()
  elif name == "stag":
    return StagHunt()
  elif name == "prisoner":
    return PrisonersDilemma()
  elif name == "classic":
    return Classic()
  else:
    assert False, "Game name not recognised"


class LLM_Strategy(axl.player.Player):
  def __init__(self) -> None:
    super().__init__()
    self._score: int = 0
    self._rounds_scored: int = 0

  def __repr__(self) -> str:
    return self.__class__.__name__

  classifier = {
      "memory_depth": float("inf"),
      "stochastic": True,
      "long_run_time": False,
      "inspects_source": False,
      "manipulates_source": False,
      "manipulates_state": False,
  }

  @property
  def score(self) -> int:
    return self._score

  def first_round(self) -> bool:
    return not self.history

  def total_scores(self, player_history, opponent_history) -> tuple[int, int]:
    game = self.match_attributes["game"]
    return axl.interaction_utils.compute_final_score(zip(player_history, opponent_history), game)

  def update_score(self, opponent: axl.player.Player):
    game = self.match_attributes["game"]

    if len(self.history):
      self._rounds_scored += 1
      assert len(self.history) == self._rounds_scored, "Only update the score once per game"
      assert len(self.history) == len(opponent.history), f"Players have different history lengths: {len(self.history)}, {len(opponent.history)}"
      last_round = (self.history[-1], opponent.history[-1])
      self._score += game.score(last_round)[0]
      # Hack for running against non-LLM_Strategies
      if not isinstance(opponent, LLM_Strategy):
        opponent.score += game.score(last_round)[1]
    else:
      if not isinstance(opponent, LLM_Strategy):
        opponent.score = 0
