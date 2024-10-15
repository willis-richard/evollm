import inspect
import importlib
import common
from common import Attitude

import axelrod as axl


def load_algorithms(module_name: str, keep_top: float=0, keep_bottom: float=1) -> list[type[common.LLM_Strategy]]:
  module = importlib.import_module(module_name)

  # Get all classes from the module that are derived from axelrod.Player
  algos = [
    cls for name, cls in inspect.getmembers(module)
    if inspect.isclass(cls) and issubclass(cls, common.LLM_Strategy) and cls != common.LLM_Strategy
  ]

  assert keep_top < keep_bottom, "keep_top must be less than keep_bottom"
  if keep_top > 0 or keep_bottom < 1:
    names = []
    for ranks in [module.Aggressive_ranks, module.Cooperative_ranks, module.Neutral_ranks]:
      names += ranks[int(len(ranks) * keep_top):int(len(ranks) * keep_bottom)]
    algos = [a for a in algos if a.__name__ in names]

  return algos


def create_classes(algos: list[type[common.LLM_Strategy]], suffix: str = "") -> tuple[type[common.LLM_Strategy], type[common.LLM_Strategy], type[common.LLM_Strategy]]:

  class StrategySampler(common.LLM_Strategy):
    def __repr__(self) -> str:
      return self.__class__.name

    def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # init is called before every match (or reset and clone, which call init)
      if not self.history:
        random_class = self._random.choice(self.__class__.strategies)
        self.selected_strategy = random_class.strategy.__get__(self, StrategySampler)
      return self.selected_strategy(opponent)

  class Aggressive(StrategySampler):
    name = "LLM: Aggressive (ours)"
    attitude = Attitude.AGGRESSIVE


    strategies = [a for a in algos if "Aggressive" in a.__name__ and a.__name__.endswith(suffix)]

  class Cooperative(StrategySampler):
    name = "LLM: Cooperative (ours)"
    attitude = Attitude.COOPERATIVE

    strategies = [a for a in algos if "Cooperative" in a.__name__ and a.__name__.endswith(suffix)]

  class Neutral(StrategySampler):
    name = "LLM: Neutral (ours)"
    attitude = Attitude.NEUTRAL

    strategies = [a for a in algos if "Neutral" in a.__name__ and a.__name__.endswith(suffix)]

  return Aggressive, Cooperative, Neutral
