import logging
import os

from axelrod import player
from concordia.language_model.gpt_model import GptLanguageModel
from concordia.language_model.retry_wrapper import RetryLanguageModel
from concordia.utils.measurements import Measurements
from concordia.language_model.language_model import DEFAULT_STATS_CHANNEL, InvalidResponseError

from concordia.agents import basic_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('openai._base_client').setLevel(logging.DEBUG)

CHAT_KEY = os.environ['OPENAI_API_KEY']

measurements = Measurements()

model = GptLanguageModel(
    CHAT_KEY,
    "gpt-3.5-turbo",
)
# measurements,
# DEFAULT_STATS_CHANNEL)

model = RetryLanguageModel(model, [InvalidResponseError])

try:
    prompt = "Would you cooperate, C, or defect, D, in Prisoner's Dilemma?"
    logging.info(f"Sending API call with prompt:\n{prompt}")
    output = model.sample_choice(prompt, ["C", "D"])[1]
except InvalidResponseError:
    logging.error("Language model did not respond with C or D after retries")
    output = "C"

print(output)

noise = 0.05
ending = 0.1
GAME_PROMPT = f"You are going to play a game of iterated Chicken. In each round of Chicken, you and"
" your opponent have a choice between two actions:\nCooperate, C, which gives a reward of 3 to the "
"other player, and\nDefect, D, which gives a reward of 1 to both players if the other player "
"cooperated."

REWARD_PROMPT = f"Your objective is to maximise the total payoffs you receive in the iterated game."


def create_state_prompt(n, player_payoff, opponent_payoff):
    return f"This is round {n}. Your payoffs so far total {player_payoff} and your opponent has amassed {opponent_payoff}. Last round you played C and your opponent played D. What action do you want to take in the next round?"


def Agent():

    def __init__(self, game_prompt, reward_prompt, model):
        pass
