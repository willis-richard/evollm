import unittest
import axelrod as axl
import inspect
import random

import common
import output

class TestPlayerClass(unittest.TestCase):
  pass

def check_for_hasattr(func):
  # Unwrap the function if it's decorated
  while hasattr(func, '__wrapped__'):
      func = func.__wrapped__

  # Get the source code of the unwrapped function
  source = inspect.getsource(func)
  return "hasattr" in source

def create_test(player_class):
  def test(self):
    game = common.get_game(player_class.game)
    axl.Match((player_class(), axl.Random()), game=game, turns=player_class.rounds).play()
    axl.Match((player_class(), player_class()), game=game, turns=player_class.rounds).play()
    self.assertFalse(check_for_hasattr(player_class.strategy), "hasattr found in code, typically replace this with a 'if not self.history' call to initialise variables")
  return test

# Get all classes from the module that are derived from axelrod.Player
player_classes = [
    cls for name, cls in inspect.getmembers(output)
    if inspect.isclass(cls) and issubclass(cls, common.LLM_Strategy) and cls != common.LLM_Strategy
  ]

# Dynamically create test methods for each player class
for player_class in player_classes:
  test_method = create_test(player_class)
  test_method.__name__ = f'test_{repr(player_class)}'
  setattr(TestPlayerClass, test_method.__name__, test_method)


unittest.main()
