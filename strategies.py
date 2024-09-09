import inspect
import output
import common

import axelrod as axl

player_classes = [
  cls for name, cls in inspect.getmembers(output)
  if inspect.isclass(cls) and issubclass(cls, output.LLM_Strategy) and cls != output.LLM_Strategy
]

class Selfish(common.LLM_Strategy):
  strategies = [p for p in player_classes if "Selfish" in p.__name__]

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    random_class = self._random.choice(self.__class__.strategies)
    return random_class.strategy(self, opponent)

class Cooperative(common.LLM_Strategy):
  strategies = [p for p in player_classes if "Cooperative" in p.__name__]

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    random_class = self._random.choice(self.__class__.strategies)
    return random_class.strategy(self, opponent)

class Aggressive(common.LLM_Strategy):
  strategies = [p for p in player_classes if "Aggressive" in p.__name__]

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    random_class = self._random.choice(self.__class__.strategies)
    return random_class.strategy(self, opponent)
