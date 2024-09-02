import axelrod as axl
from enum import StrEnum


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


# class BigRewardChicken(axl.Game):
#   name = SocialDilemma.CHICKEN

#   def __init__(self):
#     super().__init__(r=3, s=1, t=10, p=0)


# class SmallRewardChicken(axl.Game):
#   name = SocialDilemma.CHICKEN

#   def __init__(self):
#     super().__init__(r=3, s=2, t=4, p=0)
