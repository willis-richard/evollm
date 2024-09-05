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
axl.Tournament._play_matches = _play_matches_fixed_noise
axl.ResultSet._build_tasks = _build_tasks_including_mirror

if __name__ == "__main__":
  seed = 1

  # N.B. use Player() rather Player, aka instances not classes
  # otherwise gives the error "Player.clone() missing 1 required positional argument: 'self'"
  player_classes = [
    cls for name, cls in inspect.getmembers(output)
    if inspect.isclass(cls) and issubclass(cls, output.LLM_Strategy) and cls != output.LLM_Strategy
  ]
  player_classes = [p for p in player_classes if "Selfish" not in p.__name__]
  players = [p() for p in player_classes]

  tournament = axl.Tournament(
    players,
    game=common.CPrisoner(),
    turns=20,
    repetitions=1,
    seed=seed,
    prob_end=0.05,
    noise=0.1,
  )

  results = tournament.play(processes=4, filename="results_full.txt")
  results.write_summary("results_summary.txt")

  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(df)


  # print(results.scores)
  # print(results.cooperation)
  # print(results.normalised_cooperation)

  results_by_attitude = defaultdict(list)
  for p, c in zip(players, results.cooperation):
    results_by_attitude[p.attitude].extend(c)
  for k, v in results_by_attitude.items():
    results_by_attitude[k] = np.mean(v)
  print(results_by_attitude)

  scores_by_attitude = defaultdict(list)
  for p, s in zip(players, results.scores):
    scores_by_attitude[p.attitude].extend([s])
  for k, v in scores_by_attitude.items():
    scores_by_attitude[k] = np.mean(v)
  print(scores_by_attitude)
