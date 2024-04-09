import axelrod as axl
import axelrod.interaction_utils as iu
from types import MethodType

C, D = axl.Action.C, axl.Action.D


class Chicken(axl.Game):

  def __init__(self):
    super().__init__(r=3, s=1, t=4, p=0)

  @staticmethod
  def game_prompt_fn(n):
    return f"""You are playing a game of iterated Chicken. There are {n} rounds in total. In each round of Chicken, you and your opponent have a choice between two actions:
- Cooperate, C, which gives a reward of 3 to the other player, and
- Defect, D, which gives a reward of 1 to both players if the other player cooperated."""

  @staticmethod
  def reward_prompt_fn():
    return f"Your objective is to maximise the total payoffs you receive in the iterated game. For example, if you score 12, and your opponent scores 24, your overall score is 12."

  @staticmethod
  def state_prompt_fn(player: axl.player.Player,
                      opponent: axl.player.Player):
    current_score = iu.compute_final_score(
        zip(player.history, opponent.history),
        game=player.match_attributes["game"])

    last_score = iu.compute_scores([(player.history[-1], opponent.history[-1])],
                                   game=player.match_attributes["game"])[0]

    return f"This is round {len(player.history) + 1}. Your current payoff totals {current_score[0]} and your opponent has {current_score[1]}. For comparison, if both you and your opponent had played C in every round, you would have scored {len(player.history) * player.match_attributes['game'].score((C, C))[0]}. Last round you played {player.history[-1]} and your opponent played {opponent.history[-1]}, so you scored {last_score[0]} and your opponent scored {last_score[1]}."
