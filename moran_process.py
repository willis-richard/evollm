import argparse
import axelrod as axl
import pprint
import matplotlib.pyplot as plt
from multiprocessing import Pool
import numpy as np

import common
import strategies


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--initial_pop",
      nargs=3,
      type=int,
      required=True,
      help="Initial Number of aggressive, cooperative and neutral players")
  parser.add_argument(
      "--iterations",
      type=int,
      default=100,
      help="Number of times to run the simulation")
  parser.add_argument(
      "--game", type=str, default="classic", help="Name of the game to play")
  parser.add_argument(
      "--rounds", type=int, default=1000, help="Number of rounds in a match")
  parser.add_argument(
      "--noise",
      type=common.noise_arg,
      default=None,
      help="Probability that an action is flipped")
  parser.add_argument(
      "--population", action="store_true", help="Filter strategies by the population")

  return parser.parse_args()


if __name__ == "__main__":
  args = parse_arguments()

  # N.B. create separate instances for each player, not copies!
  classes = strategies.create_classes(args.algo)
  players = [cls() for cls, count in zip(classes, args.initial_pop) for _ in range(count)]
  print(players)

  def run_moran_process(seed):
    mp = axl.MoranProcess(
        players,
        seed=seed,
        turns=args.rounds,
        noise=args.noise,
        game=common.get_game(args.game))

    populations = mp.play()
    # pprint.pprint(populations)
    print(mp.winning_strategy_name)
    print(len(mp))
    return mp.winning_strategy_name

  num_cpu = 4
  seeds = np.random.randint(0, np.iinfo(np.uint32).max, size=args.iterations)

  with Pool(processes=num_cpu) as pool:
    results = pool.map(run_moran_process, seeds)

  winner_counts = {}
  for winner in results:
      winner_counts[winner] = winner_counts.get(winner, 0) + 1

  print(winner_counts)

  # for row in mp.score_history:
  #   print([round(element, 1) for element in row])

  # ax = mp.populations_plot()
  # plt.show()

  # for _ in range(1000):  # Run for 1000 steps
  #     next(mp)
  #     if mp.fixation_check():
  #         break

  # # Analyze population state
  # population_makeup = mp.population_distribution()
  # print(f"After {mp.time_steps} steps, population makeup: {population_makeup}")
