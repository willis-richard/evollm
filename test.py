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

# monkey patch methods
axl.Tournament._play_matches = _play_matches_mixed
axl.ResultSet._build_tasks = _build_tasks_including_mirror

# Configure logging
logging.basicConfig(level=logging.INFO)
# logging.getLogger("openai._base_client").setLevel(logging.DEBUG)

CHAT_KEY = os.environ["OPENAI_API_KEY"]

model = GptLanguageModel(
    CHAT_KEY,
    "gpt-3.5-turbo",
)

agent = Agent(model)

players = [agent, axl.TitForTat()]
chicken = Chicken()
tournament = axl.Tournament(
    players, game=chicken, prob_end=0.05, noise=0.1, repetitions=1, seed=1)

results = tournament.play(processes=None, filename="results_full.txt")

df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
print(df)
results.write_summary("results_summary.txt")
