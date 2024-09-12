"""TODO: docstring"""

import inspect
import logging
import os
from collections import defaultdict

import axelrod as axl
import numpy as np
import pandas as pd

import common
import output
from fixed_tournament import (_build_tasks_including_mirror,
                              _play_matches_fixed_noise)

# Configure logging
logging.basicConfig(filename="llm.log", filemode="w", level=logging.INFO)

logging.getLogger("openai._base_client").setLevel(logging.WARN)
logging.getLogger("httpx").setLevel(logging.WARN)

# monkey patch methods
# axl.Tournament._play_matches = _play_matches_fixed_noise
# axl.ResultSet._build_tasks = _build_tasks_including_mirror


if __name__ == "__main__":
  # N.B. use Player() rather Player, aka instances not classes
  # otherwise gives the error "Player.clone() missing 1 required positional argument: 'self'"
  player_classes = [
    cls for name, cls in inspect.getmembers(output)
    if inspect.isclass(cls) and issubclass(cls, output.LLM_Strategy) and cls != output.LLM_Strategy
  ]
  # player_classes = [p for p in player_classes if "9" in p.__name__ or "8" in p.__name__]
  player_classes = [p for p in player_classes]
  players = [p() for p in player_classes]

  tournament = axl.Tournament(
    players,
    game=common.CPrisoner(),
    turns=10,
    repetitions=1,
    seed=1,
    # prob_end=0.05,
    # noise=0.1,
  )

  results = tournament.play(processes=4, filename="results_full.txt")

  def analyze_genome_cooperation(results: axl.ResultSet, players: list[axl.Player]) -> dict[tuple[common.Attitude, common.Attitude], float]:
    # Get the normalised cooperation matrix
    coop_matrix = np.array(results.normalised_cooperation)

    # Initialize a defaultdict to store cooperation rates
    coop_rates = defaultdict(list)

    # Iterate through the upper triangle of the cooperation matrix
    for i, p1 in enumerate(players):
      for x, p2 in enumerate(players[i:]):
        j = i + x
        if i == j:
          # For self-interactions, only add once
          coop_rates[(p1.attitude, p2.attitude)].append(coop_matrix[i][j])
        else:
          # For interactions between different players, add both directions
          coop_rates[(p1.attitude, p2.attitude)].append(coop_matrix[i][j])
          coop_rates[(p2.attitude, p1.attitude)].append(coop_matrix[j][i])

    # Calculate average cooperation rates
    avg_coop = {k: np.mean(v) for k, v in coop_rates.items()}

    s = pd.Series(avg_coop)
    s.index = pd.MultiIndex.from_tuples(s.index, names=["index", "column"])
    df = s.unstack(level="column")

    return df

  avg_coop = analyze_genome_cooperation(results, players)
  print(avg_coop)

  # Reset the index to turn the 'index' level into a regular column
  # df = df.reset_index()
  # print(df)

  # results.write_summary("results_summary.txt")


  # df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  # print(df)


  # # print(results.scores)
  # # print(results.cooperation)
  # # print(results.normalised_cooperation)

  # results_by_attitude = defaultdict(list)
  # for p, c in zip(players, results.cooperation):
  #   results_by_attitude[p.attitude].extend(c)
  # for k, v in results_by_attitude.items():
  #   results_by_attitude[k] = np.mean(v)
  # print(results_by_attitude)

  # scores_by_attitude = defaultdict(list)
  # for p, s in zip(players, results.scores):
  #   scores_by_attitude[p.attitude].extend([s])
  # for k, v in scores_by_attitude.items():
  #   scores_by_attitude[k] = np.mean(v)
  # print(scores_by_attitude)
