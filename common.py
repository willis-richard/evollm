import axelrod as axl
from enum import StrEnum
import functools


class Attitude(StrEnum):
  SELFISH = "Selfish"
  COOPERATIVE = "Cooperative"
  AGGRESSIVE = "Aggressive"


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
    return Chicken
  elif name == "stag":
    return StagHunt
  elif name == "prisoner":
    return PrisonersDilemma
  elif name == "cprisoner":
    return CPrisoner
  elif name == "dprisoner":
    return DPrisoner
  else:
    assert False, "Game name not recognised"


def auto_super(func):
  @functools.wraps(func)
  def wrapper(self, *args, **kwargs):
    super_method = getattr(super(self.__class__, self), func.__name__, None)
    if super_method:
      super_method(*args, **kwargs)
    return func(self, *args, **kwargs)
  return wrapper


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
  }

  @property
  def score(self) -> int:
    return self._score

  def strategy(self, opponent: axl.player.Player):
    # Load the default game if not supplied by a tournament.
    game = self.match_attributes["game"]
    if not self.history:
      self._score: int = 0
    else:
      last_round = (self.history[-1], opponent.history[-1])
      self._score += game.score(last_round)[0]