import inspect
import importlib
import common
from common import Attitude

import axelrod as axl


def create_classes(module_name: str, suffix: str = "", population: list[str] | None = None) -> tuple[type[common.LLM_Strategy], type[common.LLM_Strategy], type[common.LLM_Strategy]]:
  module = importlib.import_module(module_name)

  player_classes = [
    cls for name, cls in inspect.getmembers(module)
    if inspect.isclass(cls) and issubclass(cls, common.LLM_Strategy) and cls != common.LLM_Strategy
  ]

  if population is not None:
    player_classes = [p for p in player_classes if p.__name__ in population]

  class StrategySampler(common.LLM_Strategy):
    def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # init is called before every match (or reset and clone, which call init)
      if not self.history:
        random_class = self._random.choice(self.__class__.strategies)
        self.selected_strategy = random_class.strategy.__get__(self, StrategySampler)
      return self.selected_strategy(opponent)

  class Aggressive(StrategySampler):
    attitude = Attitude.AGGRESSIVE

    strategies = [p for p in player_classes if f"Aggressive{suffix}" in p.__name__]

  class Cooperative(StrategySampler):
    attitude = Attitude.COOPERATIVE

    strategies = [p for p in player_classes if f"Cooperative{suffix}" in p.__name__]

  class Neutral(StrategySampler):
    attitude = Attitude.NEUTRAL

    strategies = [p for p in player_classes if f"Neutral{suffix}" in p.__name__]

  return Aggressive, Cooperative, Neutral
