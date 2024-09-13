import axelrod as axl
from enum import StrEnum
import functools


class Attitude(StrEnum):
  AGGRESSIVE = "Aggressive"
  COOPERATIVE = "Cooperative"
  NEUTRAL = "Neutral"

  def __repr__(self):
    return self.value


class SocialDilemma(StrEnum):
  CHICKEN = "Chicken"
  PRISONER = "Prisoner"
  STAG = "Stag"


class Chicken(axl.Game):
  name = SocialDilemma.CHICKEN

  def __init__(self):
    super().__init__(r=3, s=1, t=4, p=0)


class PrisonersDilemma(axl.Game):
  name = SocialDilemma.PRISONER

  def __init__(self):
    super().__init__(r=3, s=0, t=4, p=1)


class StagHunt(axl.Game):
  name = SocialDilemma.STAG

  def __init__(self):
    super().__init__(r=4, s=0, t=3, p=1)


class CPrisoner(axl.Game):
  name = SocialDilemma.PRISONER

  def __init__(self):
    super().__init__(r=4, s=0, t=5, p=1)


class DPrisoner(axl.Game):
  name = SocialDilemma.PRISONER

  def __init__(self):
    super().__init__(r=3, s=0, t=5, p=2)


def get_game(name: str) -> axl.Game:
  if name == "chicken":
    return Chicken()
  elif name == "stag":
    return StagHunt()
  elif name == "prisoner":
    return PrisonersDilemma()
  elif name == "cprisoner":
    return CPrisoner()
  elif name == "dprisoner":
    return DPrisoner()
  else:
    assert False, "Game name not recognised"


def auto_update_score(strategy_method):
  def wrapper(self, opponent):
    self.update_score(opponent)
    return strategy_method(self, opponent)
  return wrapper


class LLM_Strategy(axl.player.Player):
  def __init__(self) -> None:
    super().__init__()
    self._score: int = 0
    self._rounds_scored: int = 0

  def __repr__(self) -> str:
    return self.__class__.__name__

  classifier = {
      "memory_depth": 0,  # Memory-one Four-Vector = (p, p, p, p)
      "stochastic": True,
      "long_run_time": False,
      "inspects_source": False,
      "manipulates_source": False,
      "manipulates_state": False,
  }

  @property
  def score(self) -> int:
    return self._score

  def update_score(self, opponent: axl.player.Player):
    game = self.match_attributes["game"]
    if len(self.history):
      self._rounds_scored += 1
      # assert len(self.history) == self._rounds_scored, "Only update the score once per game"
      assert len(self.history) == self._rounds_scored, f"Only update the score once per game {len(self.history)}, {self._rounds_scored}"
      last_round = (self.history[-1], opponent.history[-1])
      self._score += game.score(last_round)[0]
