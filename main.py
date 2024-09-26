"""TODO: docstring"""

import inspect
import argparse
import logging
from collections import defaultdict
import importlib
import json

import axelrod as axl
import numpy as np
import pandas as pd

import common
import algorithms


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
      "--noise",
      type=common.noise_arg,
      default=None,
      help="Probability that an action is flipped")
  parser.add_argument(
      "--population", action="store_true", help="Filter strategies by the population")

  return parser.parse_args()



if __name__ == "__main__":
  args = parse_arguments()

  algos = algorithms.load_algorithms(args.algo, keep=args.keep)

  players = [a() for a in algos]
  print(f"Players: {players}")

  tournament = axl.Tournament(
    players,
    game=common.get_game(args.game),
    turns=args.rounds,
    repetitions=5,
    noise=args.noise,
  )

  results = tournament.play(processes=0, filename="results_full.txt")
  results.write_summary("results_summary.txt")

  print("Normalised cooperation\n", analyse_by_genome(results.normalised_cooperation, players))
  print("Payoff\n", analyse_by_genome(results.payoffs, players))

  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(df)
