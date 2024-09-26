import argparse
import axelrod as axl
import pprint
import matplotlib.pyplot as plt
from multiprocessing import Pool
import numpy as np

import common
import algorithms


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--algo",
      type=str,
      default="output",
      help="Name of the python module with the LLM algorithms")
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
      "--keep",
      type=common.temp_arg,
      default=1,
      help="Proportion of the X% best performing algorithms from each attitude to use")
  parser.add_argument(
      "--parallel",
      action="store_true",
      help="Run the Moran processes in parallel")

  return parser.parse_args()


if __name__ == "__main__":
  args = parse_arguments()

  # N.B. create separate instances for each player, not copies!
  algos = algorithms.load_algorithms(args.algo, args.keep)
  classes = algorithms.create_classes(algos)
  players = [cls() for cls, count in zip(classes, args.initial_pop) for _ in range(count)]
  print(players)

  def run_moran_process(seed):
    mp = axl.MoranProcess(
        players,
        seed=seed,
        turns=algos[0].rounds,
        noise=algos[0].noise,
        game=common.get_game(algos[0].game))

    populations = mp.play()
    # pprint.pprint(populations)
    print(mp.winning_strategy_name)
    print(len(mp))
    return mp.winning_strategy_name

  num_cpu = 4
  seeds = np.random.randint(0, np.iinfo(np.uint32).max, size=args.iterations)

  if args.parallel:
    with Pool(processes=num_cpu) as pool:
      results = pool.map(run_moran_process, seeds)
  else:
    results = []
    for i in range(args.iterations):
      results.append(run_moran_process(seeds[i]))

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
