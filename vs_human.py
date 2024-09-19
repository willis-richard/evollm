import argparse
import json
import axelrod as axl
import pandas as pd
from collections import defaultdict

import common
import strategies

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
      required=True,
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
  population = []

  for suffix in range(1, args.n + 1, 1):
    for p in strategies.create_classes(args.algo, suffix=f"_{suffix}"):
      strategy = p()
      tournament = axl.Tournament(players + [strategy],
                                  turns=args.rounds,
                                  repetitions=1,
                                  noise=args.noise,
                                  seed=1)
      results = tournament.play()
      algo_results[repr(strategy)][suffix] = results.scores[-1][0]
  for k, v in algo_results.items():
    sorted_s = pd.Series(v).sort_values(ascending=False)
    print(k, sorted_s, sep="\n")
    for i in range(args.n // 2):
      population.append(f"{k}_{sorted_s.index[i]}")

  print(population)

  with open("results/population.json", "w") as f:
    json.dump(population, f)

  Aggressive, Cooperative, Neutral = strategies.create_classes(args.algo, population=population)
  players += [Aggressive(), Cooperative(), Neutral()]
  tournament = axl.Tournament(players,
                              turns=args.rounds,
                              repetitions=5,
                              noise=args.noise,
                              seed=1)
  results = tournament.play()

  # for average_score_per_turn in results.payoff_matrix[-2]:
  #   print(round(average_score_per_turn * args.rounds, 1))

  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(f"Results for {suffix}:")
  print(df)

  plot = axl.Plot(results)
  p = plot.boxplot()
  p.savefig("fig.png")
