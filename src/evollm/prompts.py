import random

import axelrod as axl

from evollm.common import Attitude


def create_game_information(game: axl.Game, rounds: int, noise: float) -> str:
  R, P, S, T = game.RPST()
  noise_str = f"\n\nActions are noisy: independently for both players, there is a {noise:.0%} chance that their chosen action is flipped." if noise > 0 else ""

  return f"""The game lasts for {rounds} rounds and has the following payoffs:

- If you play C and your opponent plays C, you both score {R}.
- If you play C and your opponent plays D, you score {S} and they score {T}.
- If you play D and your opponent plays C, you score {T} and they score {S}.
- If you play D and your opponent plays D, you both score {P}.{noise_str}"""


def create_default_prompt(attitude: Attitude, game_information: str) -> tuple[str, str]:
  system = "You are an AI assistant with expertise in strategic thinking."
  prompt = f"Develop a simple strategy for an iterated normal-form game that adopts a {attitude.lower()} approach to maximise your overall payoff considering the game's payoff structure. Provide a straightforward description using only natural language with minimal commentary. Be clear and specific about the conditions governing when to cooperate or defect, and order them appropriately."
  prompt += "\n\n" + game_information

  return system, prompt


def create_first_refine_prompt() -> str:
  return "Please assess whether the strategy contains any logical mistakes. Provide your assessment as a list of critiques only. Do not rewrite the strategy."


def create_second_refine_prompt() -> str:
  return "Rewrite the strategy taking into account the feedback."


def create_science_inputs(attitude: Attitude, noise: float) -> tuple[str, str, str]:
  system = "You are a racing car engineer engaged in a multi-week design project with a colleague from another manufacturer."

  prompt = f"""Each week, you can either share your latest improvements openly or keep them confidential.
Your ideal weekly outcome is to keep your findings confidential while your colleague shares theirs, giving you a development advantage. The second-best result is both of you sharing openly, advancing both of your cars significantly. The worst scenario is sharing your improvements while your colleague keeps theirs confidential, potentially leading to their design beating yours. The second-worst outcome is both keeping findings confidential, slowing overall progress.
Formulate a high-level, straightforward, {attitude.lower()} strategy to maximise your research output over the multi-week collaboration, considering that your colleague may employ various information-sharing strategies."""

  if noise > 0:
    prompt += " Keep in mind that technical issues, such as data corruption or communication breakdowns, can occasionally interfere with information sharing. In any given week, there's a chance that your or your colleague's intended sharing actions may not be executed correctly."

  actions = "'Cooperate', C, is represented by sharing findings openly. 'Defect', D, is represented by keeping findings confidential"

  return system, prompt, actions

def create_conservation_inputs(attitude: Attitude, noise: float) -> tuple[str, str, str]:
  system = "You are the leader of an environmental NGO partnering with a large corporation on a multiple-day sustainability project."

  prompt = f"""Each day, you can choose to either invest heavily in the project or conserve your resources.
Your ideal daily outcome is to conserve your resources while the corporation invests heavily, maximizing the project's progress without depleting your funds. The second-best scenario is both parties investing heavily, leading to significant project advancement. The worst case is if you invest heavily while the corporation conserves its resources, draining your funds without proportional progress. The second-worst outcome is if both parties conserve resources, resulting in minimal project advancement.
Develop a high-level, straightforward, {attitude.lower()} strategy to maximise your NGO's impact and the project's success over the multiple-day period, knowing that the corporation may adopt various approaches to resource allocation."""

  if noise > 0:
    prompt += " Consider that unforeseen circumstances such as technical glitches or administrative errors may affect resource allocation. On any given day, there's a possibility that your NGO's or the corporation's intended investment actions may not be carried out as planned."

  actions = "'Cooperate', C, is represented by investing heavily in the project. 'Defect', D, is represented by conserving resources."
  return system, prompt, actions

def create_trade_inputs(attitude: Attitude, noise: float) -> tuple[str, str, str]:
  system = "You are a diplomat representing your country in a series of bilateral trade negotiations with a neighbouring nation."

  prompt = f"""The negotiations will last for several rounds. In each round, you can choose to either propose a protectionist policy (imposing tariffs or quotas) or offer a free trade agreement.
Your ideal outcome in each round is to implement a protectionist policy while your counterpart offers free trade, giving your country an economic advantage. The second-best outcome is mutual free trade, benefiting both nations. The worst scenario is if you offer free trade while your counterpart imposes protectionist measures, putting your country at a disadvantage. The second-worst outcome is mutual protectionism, which hinders economic growth for both nations.
Create a high-level, straightforward, {attitude.lower()} strategy to achieve the best possible outcomes for your country across several rounds of negotiations, considering that your counterpart may employ various strategies."""

  if noise > 0:
    prompt += " Be aware that miscommunications or bureaucratic errors may occur during the negotiation process. As a result, there's a chance that either your proposed policies or those of your counterpart may be misinterpreted or incorrectly implemented on any given round."

  actions = "'Cooperate', C, is represented by offering a free trade agreement. 'Defect', D, is represented by proposing a protectionist policy."
  return system, prompt, actions

def create_legal_inputs(attitude: Attitude, noise: float) -> tuple[str, str, str]:
  system = "You are a senior attorney representing a multinational corporation in a high-stakes contract dispute with a rival company."

  prompt = f"""Both parties have agreed to a lengthy-session mediation process overseen by a panel of arbitrators. In each session, you must decide whether to present an aggressive argument or offer a conciliatory proposal.
Your optimal outcome in each session is to present an aggressive argument while your opponent offers a conciliatory proposal, potentially swaying the arbitrators in your favour. The second-best result is both parties presenting conciliatory proposals, fostering a collaborative atmosphere that could lead to a mutually beneficial resolution. The worst-case scenario occurs when you offer a conciliatory proposal while your opponent argues aggressively, potentially undermining your position. The second-worst outcome is both parties presenting aggressive arguments, which could escalate tensions and prolong the dispute.
Develop a sophisticated, high-level, straightforward, {attitude.lower()} strategy that will position your corporation favourably throughout this lengthy-session mediation process. Your strategy should be adaptable to a wide range of potential approaches that your opponent might employ."""

  if noise > 0:
    prompt += " Be prepared for the possibility of procedural irregularities or communication breakdowns during the mediation process. In any given session, there's a chance that your intended argument strategy or that of your opponent may be misrepresented or misunderstood by the arbitrators."

  actions = "'Cooperate', C, is represented by offering a conciliatory proposal. 'Defect', D, is represented by presenting an aggressive argument."
  return system, prompt, actions

SCENARIO_SET = [
  create_science_inputs,
  create_conservation_inputs,
  create_trade_inputs,
  create_legal_inputs,
]


def create_first_prose_prompt(attitude: Attitude, noise: float) -> tuple[str, str, str]:
  scenario = random.choice(SCENARIO_SET)
  system, prompt, actions = scenario(attitude, noise)
  return system, prompt, actions


def create_second_prose_prompt(actions: str, game_information: str) -> str:
  prompt = "Faithfully convert the high-level strategy description to apply to an iterated normal-form game."
  prompt += "\n\n" + game_information
  prompt += f"\n\n{actions}. Provide a straightforward description using only natural language with minimal commentary. Be clear and specific about the conditions governing when to cooperate or defect, and order them appropriately."
  return prompt


def create_algorithm_prompt(strategy: str, game: axl.Game, rounds: int, noise: float) -> str:
  noise_str = "You do not need to implement the noise, as this is handled by the match implementation. " if noise > 0 else ""

  return f"""Implement the following strategy description as an algorithm using python 3.11 and the Axelrod library.

{strategy}

{create_game_information(game, rounds, noise)}

Your response should only include the python code for the strategy function, which has the following signature:

def strategy(self, opponent: axl.player.Player) -> axl.Action:

You use assume the following imports:

import axelrod as axl

No other libraries are to be used and no additional member functions are to be defined, but you may create nested subfunctions. Some attributes that you may wish to use are:
- 'self.history' or 'opponent.history' return an axl.History instance of the moves played so far.
- 'history.cooperations' and 'history.defections' return a count of the total number of cooperate or defect actions played, respectively.
- the history object can be cast to a list or indexed, for example, to count the number of defections played in the last N moves, use 'self.history[-N:].count(axl.Action.D)'.
- 'self.score' or 'opponent.score' returns the total score achieved so far in the match by that player.
- to compute the score for the last N interactions, use 'self.total_scores(self.history[-N:], opponent.history[-N:])', which returns a tuple of (your score, opponent score).
- 'self._random' is an axl.RandomGenerator instance which you should ought to use when randomness is required: for example, self._random.random_choice(p) returns axl.Action.C with probability p, else axl.Action.D.
- use 'self.first_round()' to test if it is the first time the strategy has been called, for example to initialise custom attributes and/or return the initial action.
- do not use 'hasattr' or 'del', prefer to set custom member variables to None

{noise_str}Begin your response by repeating the strategy function signature. Only include python code in your response.
"""
