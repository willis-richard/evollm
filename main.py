"""TODO: docstring"""

from collections import defaultdict
import logging
import numpy as np
import os
import pandas as pd

import axelrod as axl
from concordia.language_model.gpt_model import GptLanguageModel

from fixed_tournament import _play_matches_fixed_noise, _build_tasks_including_mirror
from games import Chicken
from llm_agent import Agent
from strategy import *
from llm_strategies import *

# Configure logging
logging.basicConfig(filename="llm.log", filemode="w", level=logging.INFO)

logging.getLogger("openai._base_client").setLevel(logging.WARN)
logging.getLogger("httpx").setLevel(logging.WARN)

# monkey patch methods
axl.Tournament._play_matches = _play_matches_fixed_noise
axl.ResultSet._build_tasks = _build_tasks_including_mirror

CHAT_KEY = os.environ["OPENAI_API_KEY"]

if __name__ == "__main__":
  model = GptLanguageModel(
      CHAT_KEY,
      # "gpt-4o",
      "gpt-3.5-turbo",
  )

  seed = 1

  # N.B. use Player() rather Player, aka instances not classes
  # otherwise gives the error "Player.clone() missing 1 required positional argument: 'self'"
  # players = [Selfish_1(), Selfish_2(), Selfish_3(), Cooperative_1(), Cooperative_2(), Cooperative_3(), Aggressive_1(), Aggressive_2(), Aggressive_3()]

  import inspect
  import output
  player_classes = [
      cls for name, cls in inspect.getmembers(output)
      if inspect.isclass(cls) and issubclass(cls, output.LLM_Strategy) and cls != output.LLM_Strategy
   ]
  players = [p() for p in player_classes]

  # players = [axl.Defector(), axl.Cooperator()]

  tournament = axl.Tournament(
    players,
    game=Chicken(),
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


  print(results.scores)
  print(results.cooperation)
  # print(results.normalised_cooperation)

  results_by_attitude = defaultdict(list)
  for p, c in zip(players, results.cooperation):
    results_by_attitude[p.attitude].extend(c)
  for k, v in results_by_attitude.items():
    results_by_attitude[k] = np.mean(v)
  print(results_by_attitude)
