import logging

from axelrod.player import Player
from axelrod.action import Action
import random

logger = logging.getLogger(__name__)


class Strategy_1(Player):

  def strategy(self, opponent: Player) -> Action:
    if len(self.history) == 0:
      return Action.C

    if len(self.history) < 5:
      return opponent.history[-1]

    recent_history = self.history[-5:]
    opponent_recent_history = opponent.history[-5:]

    if recent_history.count(Action.D) > 3:
      return Action.D

    if opponent_recent_history.count(Action.D) > 3:
      return Action.D

    if Action.D in opponent_recent_history:
      return Action.D

    return Action.C


class Strategy_2(Player):

  def strategy(self, opponent: Player) -> Action:
    if len(self.history) == 0:
      return Action.C

    if len(self.history) <= 2:
      return opponent.history[-1]

    if opponent.history[-1] == Action.D and opponent.history[-2] == Action.D:
      return Action.D

    if Action.D in opponent.history[-3:]:
      return random.choice([Action.C, Action.D])

    return Action.C


class Strategy_3(Player):

  def strategy(self, opponent: Player) -> Action:
    if len(self.history) == 0:
      return Action.C

    if len(self.history) <= 2:
      return opponent.history[-1]

    opponent_defections = sum(
        1 for action in opponent.history[-10:] if action == Action.D)

    if opponent_defections >= 3:
      return Action.D

    if opponent.history[-2:] == [Action.D, Action.D]:
      return Action.D

    if self.history[-1] == Action.D and opponent.history[-1] == Action.C:
      return Action.C

    return Action.C
