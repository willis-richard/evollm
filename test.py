"""TODO: docstring"""

import logging
import os
from pprint import pprint

import axelrod as axl
from axelrod.action import Action
from concordia.language_model.gpt_model import GptLanguageModel

from fixed_tournament import FixedTournament
from games import chicken
from llm_agent import Agent

C, D = Action.C, Action.D

# Configure logging
logging.basicConfig(level=logging.INFO)
# logging.getLogger("openai._base_client").setLevel(logging.DEBUG)

CHAT_KEY = os.environ["OPENAI_API_KEY"]

model = GptLanguageModel(
    CHAT_KEY,
    "gpt-3.5-turbo",
)

agent = Agent(model)

players = [axl.Cooperator(), axl.Defector()]
tournament = FixedTournament(
    players, game=chicken, prob_end=0.05, noise=0.1, repetitions=1, seed=1)
results = tournament.play(processes=None, filename="results_full.txt")

# print("pprint(results.match_lengths)")
# pprint(results.match_lengths)
# print("print(results.normalised_scores)")
# print(results.normalised_scores)
# print("print(results.ranked_names)")
# print(results.ranked_names)
# print("pprint(results.payoff_matrix)")
# pprint(results.payoff_matrix)
# print("pprint(results.normalised_cooperation)")
# pprint(results.normalised_cooperation)
# print("print(results.initial_cooperation_rate)")
# print(results.initial_cooperation_rate)
# print("pprint(results.normalised_state_to_action_distribution)")
# pprint(results.normalised_state_to_action_distribution)

pprint(results.summarise())
import pandas as pd
df = pd.DataFrame(results.summarise()).set_index("Rank", drop=True)
print(df)
results.write_summary("results_summary.txt")
