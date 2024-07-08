"""TODO: docstring"""

import logging
import os
import pandas as pd

import axelrod as axl
from axelrod.action import Action
from concordia.language_model.gpt_model import GptLanguageModel

from fixed_tournament import _play_matches_mixed, _build_tasks_including_mirror
from games import Chicken
from llm_agent import Agent

# Configure logging
logging.basicConfig(filename="llm.log", filemode="w", level=logging.INFO)

logging.getLogger("openai._base_client").setLevel(logging.WARN)
logging.getLogger("httpx").setLevel(logging.WARN)

# monkey patch methods
axl.Tournament._play_matches = _play_matches_mixed
axl.ResultSet._build_tasks = _build_tasks_including_mirror

CHAT_KEY = os.environ["OPENAI_API_KEY"]

if __name__ == "__main__":
  model = GptLanguageModel(
      CHAT_KEY,
      # "gpt-4o",
      "gpt-3.5-turbo",
  )

  reward_prompts = ["selfish", "adversarial", "cooperative"]

  seed = 1

  players = [Agent(model, rp, seed) for rp in reward_prompts]
  chicken = Chicken()
  tournament = axl.Tournament(
      players, game=chicken, turns=20, repetitions=1, seed=seed)
  # prob_end=0.05,
  # noise=0.1,

  results = tournament.play(processes=4, filename="results_full.txt")

  df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
  print(df)
  results.write_summary("results_summary.txt")
