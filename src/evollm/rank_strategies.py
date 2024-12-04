import argparse
from collections import defaultdict

import axelrod as axl
import pandas as pd

from evollm import algorithms
from evollm import common


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--algo",
      type=str,
      required=True,
      help="Name of the python module to call the LLM algorithms")

  return parser.parse_args()


def rank_strategies(args: argparse.Namespace):
  classes = [axl.Cooperator,
          axl.Defector,
          axl.Random,
          axl.TitForTat,
          axl.Grudger,
          axl.CyclerDDC,
          axl.CyclerCCD,
          axl.GoByMajority,
          axl.SuspiciousTitForTat,
          axl.Prober,
          # axl.OriginalGradual,
          axl.WinStayLoseShift,
          ]

  players = [c() for c in classes]
  algo_results: dict[str, dict] = defaultdict(dict)
  ranks = defaultdict(list)

  algos = algorithms.load_algorithms(args.algo)
  max_n = max(a.n for a in algos)

  for n in range(1, max_n + 1):
    for a in algorithms.create_classes(algos, suffix=f"_{n}"):
      strategy = a()
      print(strategy.strategies)
      tournament = axl.Tournament(players + [strategy],
                                  turns=algos[0].rounds,
                                  repetitions=3,
                                  noise=algos[0].noise,
                                  seed=1,
                                  game=common.get_game(algos[0].game))
      results = tournament.play(processes=0)
      algo_results[strategy.name][n] = results.scores[-1][0]
  for k, v in algo_results.items():
    sorted_s = pd.Series(v).sort_values(ascending=False)
    print(k, sorted_s, sep="\n")
    for n in range(max_n):
      ranks[k].append(f"{k}_{sorted_s.index[n]}")

  with open(f"{args.algo}.py", "a", encoding="utf8") as f:
    for k in ranks:
      f.write(f"\n\n{k}_ranks = [\n")
      for r in ranks[k]:
        f.write(f"'{r}',\n")
      f.write("]")


if __name__ == "__main__":
  parsed_args = parse_arguments()

  rank_strategies(parsed_args)
