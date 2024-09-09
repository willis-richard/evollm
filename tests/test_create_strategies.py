import unittest
import axelrod as axl
import inspect
import random

import output

# Monkey patch on a score attribute for random.

def score_getter(self):
  return random.randint(0, 80)

axl.Random.score = property(score_getter)

class TestPlayerClass(unittest.TestCase):
  pass

def create_test(player_class):
  def test(self):
    axl.Match((player_class(), axl.Random()), turns=20).play()
    axl.Match((player_class(), player_class()), turns=20).play()
  return test

# Get all classes from the module that are derived from axelrod.Player
player_classes = [
    cls for name, cls in inspect.getmembers(output)
    if inspect.isclass(cls) and issubclass(cls, output.LLM_Strategy) and cls != output.LLM_Strategy
]


# Dynamically create test methods for each player class
for i, player_class in enumerate(player_classes):
  test_method = create_test(player_class)
  test_method.__name__ = f'test_{repr(player_class)}'
  setattr(TestPlayerClass, test_method.__name__, test_method)

if __name__ == '__main__':
  unittest.main()
