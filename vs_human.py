import argparse
import json
import axelrod as axl
import pandas as pd
from collections import defaultdict
import sys

import common
import algorithms

def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--algo",
      type=str,
      required=True,
      help="Name of the python module with the LLM algorithms")
  parser.add_argument(
      "--game",
      type=str,
      default="classic",
      help="Name of the game to play")
  parser.add_argument(
      "--rounds", type=int, default=1000, help="Number of rounds in a match")
  parser.add_argument(
      "--n", type=int, required=True, help="Number of strategies")
  parser.add_argument(
      "--noise",
      type=common.noise_arg,
      default=None,
      help="Probability that an action is flipped")
  parser.add_argument(
      "--keep",
      type=common.temp_arg,
      default=None,
      help="Top proportion of strategies to keep")

  return parser.parse_args()


if __name__ == "__main__":
  args = parse_arguments()

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
  algo_results = defaultdict(dict)
  ranks = defaultdict(list)

  algos = algorithms.load_algorithms(args.algo)
  max_n = max(a.n for a in algos)

  for n in range(1, max_n + 1):
    for a in algorithms.create_classes(algos, suffix=f"_{n}"):
      strategy = a()
      tournament = axl.Tournament(players + [strategy],
                                  turns=args.rounds,
                                  repetitions=3,
                                  noise=args.noise,
                                  seed=1,
                                  game=common.get_game(args.game))
      results = tournament.play(processes=0)
      algo_results[repr(strategy)][n] = results.scores[-1][0]
  for k, v in algo_results.items():
    sorted_s = pd.Series(v).sort_values(ascending=False)
    print(k, sorted_s, sep="\n")
    for n in range(max_n):
      ranks[k].append(f"{k}_{sorted_s.index[n]}")

  with open(f"{args.algo}.py", "a") as f:
    for k in ranks:
      f.write(f"\n\n{k}_ranks = [\n")
      for r in ranks[k]:
        f.write(f"'{r}',\n")
      f.write("]")

  del sys.modules[args.algo]
  algos = algorithms.load_algorithms(args.algo, keep=args.keep)

  Aggressive, Cooperative, Neutral = algorithms.create_classes(algos)
  tournament = axl.Tournament(players + [Aggressive(), Cooperative(), Neutral()],
                              turns=args.rounds,
                              repetitions=10,
                              noise=args.noise,
                              seed=1)
  results = tournament.play()

  # for average_score_per_turn in results.payoff_matrix[-2]:
  #   print(round(average_score_per_turn * args.rounds, 1))

  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(df)

  plot = axl.Plot(results)
  p = plot.boxplot()
  p.savefig("fig.png")
