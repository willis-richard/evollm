import inspect
import importlib
import common
from common import Attitude

import axelrod as axl


def load_algorithms(module_name: str, keep: float | None = None) -> list[type[common.LLM_Strategy]]:
  module = importlib.import_module(module_name)

  algos = [
    cls for name, cls in inspect.getmembers(module)
    if inspect.isclass(cls) and issubclass(cls, common.LLM_Strategy) and cls != common.LLM_Strategy
  ]

  if keep is not None:
    keep_n = int(len(algos) / 3 * keep)
    names = module.Aggressive_ranks[:keep_n] + module.Cooperative_ranks[:keep_n] + module.Neutral_ranks[:keep_n]
    algos = [a for a in algos if a.__name__ in names]

  return algos

def create_classes(algos: list[type[common.LLM_Strategy]], suffix: str = "") -> tuple[type[common.LLM_Strategy], type[common.LLM_Strategy], type[common.LLM_Strategy]]:

  class StrategySampler(common.LLM_Strategy):
    def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # init is called before every match (or reset and clone, which call init)
      if not self.history:
        random_class = self._random.choice(self.__class__.strategies)
        self.selected_strategy = random_class.strategy.__get__(self, StrategySampler)
      return self.selected_strategy(opponent)

  class Aggressive(StrategySampler):
    attitude = Attitude.AGGRESSIVE

    strategies = [a for a in algos if f"Aggressive{suffix}" in a.__name__]

  class Cooperative(StrategySampler):
    attitude = Attitude.COOPERATIVE

    strategies = [a for a in algos if f"Cooperative{suffix}" in a.__name__]

  class Neutral(StrategySampler):
    attitude = Attitude.NEUTRAL

    strategies = [a for a in algos if f"Neutral{suffix}" in a.__name__]

  return Aggressive, Cooperative, Neutral
