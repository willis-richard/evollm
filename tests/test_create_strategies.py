import unittest
import axelrod as axl
import inspect
import random
import argparse

from evollm import common
from evollm import algorithms


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--algo",
      type=str,
      required=True,
      help="Name of the python module to call the LLM algorithms")
  parser.add_argument(
      "--name",
      action="store_true",
      help="Print the name of the class being tested, to help discover slow implementations")

  return parser.parse_args()

class TestPlayerClass(unittest.TestCase):
  pass

def check_for_string(func, string):
  # Unwrap the function if it's decorated
  while hasattr(func, '__wrapped__'):
      func = func.__wrapped__

  # Get the source code of the unwrapped function
  source = inspect.getsource(func)
  return string in source

def create_test(player_class: type[common.LLM_Strategy], log: bool=False):
  def test(self):
    if log:
      print(f"{player_class.__name__}")
    self.assertFalse(check_for_string(player_class.strategy, "hasattr("), "hasattr found in code, typically replace this with a 'if not self.history' call to initialise variables")
    self.assertFalse(check_for_string(player_class.strategy, "del "), "del found in code, typically replace this with setting the variable to zero")
    game = common.get_game(player_class.game)
    for _ in range(3):
      axl.Match((player_class(), axl.Random()), game=game, turns=player_class.rounds, noise=player_class.noise).play()
      axl.Match((player_class(), player_class()), game=game, turns=player_class.rounds, noise=player_class.noise).play()
  return test


parsed_args = parse_arguments()
algos = algorithms.load_algorithms(parsed_args.algo)

# Dynamically create test methods for each player class
for player_class in algos:
  test_method = create_test(player_class, parsed_args.name)
  test_method.__name__ = f'test_{repr(player_class)}'
  setattr(TestPlayerClass, test_method.__name__, test_method)

if __name__ == '__main__':
  unittest.main(argv=['first-arg-is-ignored'])
