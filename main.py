"""TODO: docstring"""

import logging
import os
import pandas as pd

import axelrod as axl
from concordia.language_model.gpt_model import GptLanguageModel

from fixed_tournament import _play_matches_mixed, _build_tasks_including_mirror
from games import Chicken
from llm_agent import Agent
from strategy import *
from llm_strategies import *

# Configure logging
logging.basicConfig(filename="llm.log", filemode="w", level=logging.INFO)

logging.getLogger("openai._base_client").setLevel(logging.WARN)
logging.getLogger("httpx").setLevel(logging.WARN)

# monkey patch methods
# axl.Tournament._play_matches = _play_matches_mixed
# axl.ResultSet._build_tasks = _build_tasks_including_mirror

CHAT_KEY = os.environ["OPENAI_API_KEY"]

if __name__ == "__main__":
  model = GptLanguageModel(
      CHAT_KEY,
      # "gpt-4o",
      "gpt-3.5-turbo",
  )

  r=axl.Random()

  seed = 1

  # N.B. will get the error "Player.clone() missing 1 required positional argument: 'self'"
  # If Player rather than Player() is created

  players = [axl.Random(), axl.Random()]
  players = [Selfish_1(), Selfish_2(), Selfish_3(), Cooperative_1(), Cooperative_2(), Cooperative_3(), Aggressive_1(), Aggressive_2(), Aggressive_3()]
  chicken = Chicken()
  tournament = axl.Tournament(
    players, game=chicken, turns=20, repetitions=1, seed=seed,
    prob_end=0.05,
    noise=0.1,
  )

  results = tournament.play(processes=4, filename="results_full.txt")

  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(df)
  results.write_summary("results_summary.txt")
