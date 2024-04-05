"""TODO: docstring"""

import argparse
from collections import defaultdict

import axelrod as axl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from evollm import algorithms
from evollm import common


def analyse_by_genome(data: list[list[int | float]], players: list[axl.Player]) -> pd.DataFrame:
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
      required=True,
      help="Name of the python module with the LLM algorithms")
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
      "--h2h",
      action="store_true",
      help="Pit the algorithms head-to-head (instead of Beaufils tournament)")

  return parser.parse_args()


def play_vs_llm_strats(file_name: str, algos: list[type[common.LLM_Strategy]]) -> None:
  players = [a() for a in algos]
  print(f"Players: {players}")

  tournament = axl.Tournament(
    players,
    game=common.get_game(algos[0].game),
    turns=algos[0].rounds,
    repetitions=20,
    noise=algos[0].noise,
  )

  results = tournament.play(processes=0, filename=f"results/{file_name}_results_full.txt")

  normalised_cooperation = analyse_by_genome(results.normalised_cooperation, players)
  print("Normalised cooperation\n", normalised_cooperation)
  payoffs = analyse_by_genome(results.payoffs, players)
  print("Payoff\n", payoffs)
  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(df)
  with open(f"results/{file_name}_matrices.txt", "w", encoding="utf8") as f:
    f.write(f"Normalised cooperation:\n{normalised_cooperation.to_string()}\n")
    f.write(f"\nPayoffs:\n{payoffs.to_string()}\n")
    f.write(f"\nResults Summary:\n{df.to_string()}")


def play_beaufils(file_name: str, algos:list[type[common.LLM_Strategy]]) -> None:
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
                              repetitions=100,
                              noise=algos[0].noise,
                              seed=1)
  results = tournament.play(processes=0)

  # for average_score_per_turn in results.payoff_matrix[-2]:
  #   print(round(average_score_per_turn * args.rounds, 1))

  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(df)

  # plt.rcParams.update({"font.size": 14})
  plot = axl.Plot(results)
  p = plot.boxplot()

  # Get the current size
  size = p.get_size_inches()

  # Calculate the new size (20% larger)
  size[1] = size[1] * 1.2

  # Set the new size
  p.set_size_inches(size)

  # plt.xlabel("Strategies", fontsize=16)
  # plt.ylabel("Normalised Payoff", fontsize=16)
  plt.xticks(fontsize=24, rotation=45, ha='right')
  plt.yticks(fontsize=24)

  p.subplots_adjust(bottom=0.4)
  p.tight_layout()

  p.savefig(f"results/{file_name}.png", dpi=300)


if __name__ == "__main__":
  parsed_args = parse_arguments()

  algos = algorithms.load_algorithms(parsed_args.algo, parsed_args.keep_top, parsed_args.keep_bottom)

  if parsed_args.h2h:
    play_vs_llm_strats(parsed_args.algo, algos)
  else:
    play_beaufils(parsed_args.algo, algos)
