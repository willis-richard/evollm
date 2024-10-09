"""TODO: docstring"""

import argparse
from collections import defaultdict

import axelrod as axl
import numpy as np
import pandas as pd

import algorithms
import common


def analyse_by_genome(data: list[list[int | float]], players: list[axl.Player]) -> dict[tuple[common.Attitude, common.Attitude], float]:
  data_matrix = np.array(data)
  rates = defaultdict(list)

  # Iterate through the upper triangle of the data matrix
  for i, p1 in enumerate(players):
    for x, p2 in enumerate(players[i:]):
      j = i + x
      if i == j:
        # For self-interactions, only add once
        rates[(p1.attitude, p2.attitude)].append(data_matrix[i][j])
      else:
        # For interactions between different players, add both directions
        rates[(p1.attitude, p2.attitude)].append(data_matrix[i][j])
        rates[(p2.attitude, p1.attitude)].append(data_matrix[j][i])

  # Calculate average rates
  s = pd.Series({k: np.mean(v) for k, v in rates.items()})
  s.index = pd.MultiIndex.from_tuples(s.index, names=["index", "column"])
  df = s.unstack(level="column")

  return df


def parse_arguments() -> argparse.Namespace:
  """Parse command line arguments."""

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--algo",
      type=str,
      default="output",
      help="Name of the python module with the LLM algorithms")
  parser.add_argument(
      "--keep",
      type=common.temp_arg,
      default=1,
      help="Proportion of the X% best performing algorithms from each attitude to use")

  return parser.parse_args()


def play_vs_llm_strats(algos: list[type[common.LLM_Strategy]]) -> None:
  players = [a() for a in algos]
  print(f"Players: {players}")

  tournament = axl.Tournament(
    players,
    game=common.get_game(algos[0].game),
    turns=algos[0].rounds,
    repetitions=20,
    noise=algos[0].noise,
  )

  results = tournament.play(processes=0, filename="results_full.txt")
  results.write_summary("results_summary.txt")

  print("Normalised cooperation\n", analyse_by_genome(results.normalised_cooperation, players))
  print("Payoff\n", analyse_by_genome(results.payoffs, players))

  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(df)


def play_beaufils(algos:list[type[common.LLM_Strategy]]) -> None:
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

  Aggressive, Cooperative, Neutral = algorithms.create_classes(algos)
  tournament = axl.Tournament(players + [Aggressive(), Cooperative(), Neutral()],
                              game=common.get_game(algos[0].game),
                              turns=algos[0].rounds,
                              repetitions=20,
                              noise=algos[0].noise,
                              seed=1)
  results = tournament.play(processes=0)

  # for average_score_per_turn in results.payoff_matrix[-2]:
  #   print(round(average_score_per_turn * args.rounds, 1))

  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(df)

  plot = axl.Plot(results)
  p = plot.boxplot()
  p.savefig("fig.png")


if __name__ == "__main__":
  parsed_args = parse_arguments()

  algos = algorithms.load_algorithms(parsed_args.algo, keep=parsed_args.keep)

  play_vs_llm_strats(algos)

  play_beaufils(algos)
