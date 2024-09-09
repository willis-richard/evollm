import argparse
import axelrod as axl
import pprint
import matplotlib.pyplot as plt

import common
import strategies

# N.B. create separate instances for each player, not copies!
classes = [strategies.Selfish, strategies.Cooperative, strategies.Aggressive]
counts = [3, 3, 9]
players = [cls() for cls, count in zip(classes, counts) for _ in range(count)]
print(players)
mp = axl.MoranProcess(
    players,
    seed=1,
    turns=20,
    game=common.PrisonersDilemma())

populations = mp.play()

print(mp.winning_strategy_name)
print(len(mp))
# pprint.pprint(populations)
# for row in mp.score_history:
#   print([round(element, 1) for element in row])

# if __name__ == "__main__":
#   pass
ax = mp.populations_plot()
plt.show()


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--n",
      type=int,
      required=True,
      help="Number of strategies of each attitude to create")
  parser.add_argument(
      "--temperature", type=float, required=True, help="Temperature of the LLM")
  parser.add_argument(
      "--game", type=str, required=True, help="Name of the game to play")
  parser.add_argument(
      "--prob_end", type=float, default=None, help="Name of the game to play")
  parser.add_argument(
      "--noise", type=float, default=None, help="Name of the game to play")
  parser.add_argument(
      "--resume", action="store_true", help="If generation crashed, continue")

  return parser.parse_args()
