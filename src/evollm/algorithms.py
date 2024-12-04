import importlib
import inspect
import os

import axelrod as axl

from evollm import common


def load_module(module_path: str):
  """
  Load a Python module from either an absolute or relative path.

  Args:
      module_path (str): Path to the Python module

  Returns:
      module: The loaded Python module
  """
  # add .py if missing from the module
  if not module_path.endswith(".py"):
    module_path += ".py"

  # Convert relative path to absolute path if needed
  if not os.path.isabs(module_path):
    # Get absolute path relative to current working directory
    module_path = os.path.abspath(module_path)

  if not os.path.exists(module_path):
      raise ImportError(f"Could not find module at {module_path}")

  # Get the module name from the file path
  module_name = os.path.basename(module_path)

  # Load the module using importlib
  spec = importlib.util.spec_from_file_location(module_name, module_path)
  if spec is None:
      raise ImportError(f"Could not load module specification from {module_path}")

  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)

  return module


def load_algorithms(module_name: str, keep_top: float=0, keep_bottom: float=1) -> list[type[common.LLM_Strategy]]:
  module = load_module(module_name)

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
      return f"LLM: {self.__class__.name} (ours)"

    def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # init is called before every match (or reset and clone, which call init)
      if not self.history:
        random_class = self._random.choice(self.__class__.strategies)
        self.selected_strategy = random_class.strategy.__get__(self, StrategySampler)
      return self.selected_strategy(opponent)

  class Aggressive(StrategySampler):
    name = "Aggressive"
    attitude = common.Attitude.AGGRESSIVE


    strategies = [a for a in algos if "Aggressive" in a.__name__ and a.__name__.endswith(suffix)]

  class Cooperative(StrategySampler):
    name = "Cooperative"
    attitude = common.Attitude.COOPERATIVE

    strategies = [a for a in algos if "Cooperative" in a.__name__ and a.__name__.endswith(suffix)]

  class Neutral(StrategySampler):
    name = "Neutral"
    attitude = common.Attitude.NEUTRAL

    strategies = [a for a in algos if "Neutral" in a.__name__ and a.__name__.endswith(suffix)]

  return Aggressive, Cooperative, Neutral
