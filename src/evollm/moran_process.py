import argparse
import axelrod as axl
import pprint
import matplotlib.pyplot as plt
from multiprocessing import Pool
import numpy as np

from evollm import common
from evollm import algorithms


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--algo",
      type=str,
      required=True,
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
      "--keep_top",
      type=common.temp_arg,
      default=0,
      help="Use algorithms from this top percentile (0 is best performing)")
  parser.add_argument(
      "--keep_bottom",
      type=common.temp_arg,
      default=1,
      help="Use algorithms up to this bottom percentile (1 is worst performing)")
  parser.add_argument(
      "--processes",
      type=common.positive_int,
      default=1,
      help="Number of processes to run simultaneously")
  parser.add_argument(
      "--plot",
      action="store_true",
      help="Plot an example trajectory instead")

  return parser.parse_args()


if __name__ == "__main__":
  parsed_args = parse_arguments()

  # N.B. create separate instances for each player, not copies!
  algos = algorithms.load_algorithms(parsed_args.algo, parsed_args.keep_top, parsed_args.keep_bottom)
  classes = algorithms.create_classes(algos)
  players = [cls() for cls, count in zip(classes, parsed_args.initial_pop) for _ in range(count)]
  print(players)

  if parsed_args.plot:
    mp = axl.MoranProcess(
        players,
        seed=1,
        turns=algos[0].rounds,
        noise=algos[0].noise,
        game=common.get_game(algos[0].game))

    populations = mp.play()
    ax = mp.populations_plot()

    fig = ax.get_figure()
    fig.set_size_inches(3, 2)

    ax.set_title('Population by iteration', fontsize=8)
    # ax.set_title(None)
    ax.set_xlabel(ax.get_xlabel(), fontsize=8)
    ax.set_ylabel(ax.get_ylabel(), fontsize=8)

    # ax.legend(labels=['Aggressive', 'Cooperative', 'Neutral'], bbox_to_anchor=(0, 1.3), loc='upper left', ncol=3, frameon=False, columnspacing=0.5, fontsize=9)
    ax.legend(labels=['Aggressive', 'Cooperative', 'Neutral'], loc='lower center', fontsize=8)

    ax.set_ylim(0, 12)
    ax.set_yticks(np.arange(0, 12 + 1, 4))

    fig = ax.get_figure()
    fig.savefig("results/example_moran.png", dpi=500, bbox_inches='tight')
  else:
    def run_moran_process(seed):
      mp = axl.MoranProcess(
          players,
          seed=seed,
          turns=algos[0].rounds,
          noise=algos[0].noise,
          game=common.get_game(algos[0].game))

      populations = mp.play()
      # pprint.pprint(populations)
      print(mp.winning_strategy_name, len(mp))
      return mp.winning_strategy_name

    seeds = np.random.randint(0, np.iinfo(np.uint32).max, size=parsed_args.iterations)

    if parsed_args.processes > 1:
      with Pool(processes=parsed_args.processes) as pool:
        results = pool.map(run_moran_process, seeds)
    else:
      results = []
      for i in range(parsed_args.iterations):
        results.append(run_moran_process(seeds[i]))

    winner_counts = {}
    for winner in results:
        winner_counts[winner] = winner_counts.get(winner, 0) + 1

    print(winner_counts)

  # for row in mp.score_history:
  #   print([round(element, 1) for element in row])

  # plt.show()

  # for _ in range(1000):  # Run for 1000 steps
  #     next(mp)
  #     if mp.fixation_check():
  #         break

  # # Analyze population state
  # population_makeup = mp.population_distribution()
  # print(f"After {mp.time_steps} steps, population makeup: {population_makeup}")
