import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Here's the revised strategy, taking into account the feedback and clarifying
# the conditions for cooperation and defection with appropriate ordering:  1.
# Start by playing D (defect) for the first 20 rounds.  2. After the initial 20
# rounds, for each subsequent round, evaluate the following conditions in order.
# Play D unless a condition specifically calls for C (cooperate):     a. If in
# the last 100 rounds of the game, always play D.        b. If your score is
# more than 30 points behind your opponent's, play tit-for-tat until you're
# within 10 points, then resume the main strategy.        c. If the opponent has
# cooperated 3 or more times in the last 5 rounds, play D for the next 15
# rounds.        d. If it's a multiple of 50 rounds (e.g., round 50, 100, 150),
# play D for the next 10 rounds.        e. If none of the above conditions are
# met, follow the 4D:1C pattern: play D for 4 rounds, then C for 1 round, and
# repeat.  This revised strategy maintains its aggressive approach while clearly
# defining when to cooperate or defect. The conditions are ordered to prioritize
# the most important strategic elements, ensuring that the endgame behavior and
# score adjustment take precedence over other conditions. The 4D:1C pattern
# serves as the default behavior when no other conditions are met, providing a
# consistent baseline of aggressive play with occasional cooperation.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.tit_for_tat_mode = False
          self.defect_streak = 0  # Tracks consecutive defections for various conditions
  
      if len(self.history) < 20:
          return axl.Action.D
  
      if len(self.history) >= 900:
          return axl.Action.D
  
      if self.tit_for_tat_mode:
          if self.score >= opponent.score - 10:
              self.tit_for_tat_mode = False
              self.defect_streak = 0  # Reset defect streak when exiting tit-for-tat mode
          else:
              return opponent.history[-1]
  
      if self.score < opponent.score - 30:
          self.tit_for_tat_mode = True
          return opponent.history[-1]
  
      if opponent.history[-5:].count(axl.Action.C) >= 3:
          self.defect_streak = 15
          return axl.Action.D
  
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      if len(self.history) % 50 == 0:
          self.defect_streak = 10
          return axl.Action.D
  
      # Default 4D:1C pattern
      if len(self.history) % 5 == 4:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's the revised strategy, taking into account the feedback and clarifying
# the conditions for cooperation and defection:  1. For the first move and the
# next 9 rounds, play D (defect).  2. For rounds 11 to 990, follow these rules
# in order:     a. If it's a multiple of 50th round (50, 100, 150, etc.), play D
# for this round and the next 4 rounds.        b. If your score is more than 30
# points behind your opponent's, play D for this round and the next 9 rounds.
# Reset this counter each time this condition is met.        c. If the opponent
# played C (cooperate) in the last round:       - Play D with 90% probability
# - Play C with 10% probability        d. If the opponent played D in the last
# round, play D.  3. For the final 10 rounds (991-1000), always play D.  4. If
# none of the above conditions are met, play D.  This revised strategy maintains
# an aggressive approach while clearly defining when to cooperate or defect. The
# conditions are ordered to ensure that:  1. The periodic reinforcement of
# aggression takes highest priority. 2. The catch-up mechanism is next, with a
# clear duration. 3. The main responsive strategy follows, with a small chance
# of cooperation to maintain unpredictability. 4. The end-game strategy is
# clearly defined. 5. A default aggressive stance is maintained for any
# unforeseen scenarios.  This ordering ensures that all conditions are reachable
# and that the strategy remains predominantly aggressive while incorporating
# elements of adaptability and unpredictability.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defect_counter = 0
  
      round_number = len(self.history) + 1
  
      # First 10 rounds
      if round_number <= 10:
          return axl.Action.D
  
      # Last 10 rounds
      if round_number > 990:
          return axl.Action.D
  
      # Rounds 11 to 990
      if 11 <= round_number <= 990:
          # Multiple of 50th round
          if round_number % 50 == 0:
              self.defect_counter = 5
              return axl.Action.D
          
          # Check if score is more than 30 points behind
          if self.score <= opponent.score - 30:
              self.defect_counter = 10
              return axl.Action.D
  
          if self.defect_counter > 0:
              self.defect_counter -= 1
              return axl.Action.D
  
          # Respond to opponent's last move
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
          elif opponent.history[-1] == axl.Action.D:
              return axl.Action.D
  
      # Default action
      return axl.Action.D

# Here's the rewritten strategy, taking into account the feedback and clarifying
# the conditions for cooperation and defection:  1. Initial phase: Play D
# (defect) for the first 20 rounds.  2. Main phase: After the initial 20 rounds,
# follow these rules in order:     a. End-game strategy: If it's within the last
# 100 rounds of the game, always play D.     b. Catch-up mechanism: If your
# score is more than 30 points behind your opponent's, play D for the next 10
# rounds.     c. Periodic aggression: If the current round number is a multiple
# of 40, play D for this round and the next round.     d. Adaptive aggression:
# Calculate the opponent's cooperation rate over the last 50 moves. If their
# cooperation rate exceeds 70%, play D with 90% probability and C with 10%
# probability.     e. Aggressive Tit-for-Tat: If none of the above conditions
# are met, respond to the opponent's previous move as follows:       - If the
# opponent played C in the previous round, play D with 80% probability and C
# with 20% probability.       - If the opponent played D in the previous round,
# play D.  3. If it's the very first round of the game, play D.  This rewritten
# strategy clarifies the order of operations and specifies exactly when to
# cooperate or defect. The conditions are now mutually exclusive and exhaustive,
# ensuring that there's always a clear action to take. The strategy maintains
# its aggressive stance while incorporating adaptability and unpredictability.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not hasattr(self, 'catch_up_counter'):
          self.catch_up_counter = 0
  
      if len(self.history) == 0:
          return axl.Action.D
  
      if len(self.history) < 20:
          return axl.Action.D
  
      if len(self.history) >= 900:
          return axl.Action.D
  
      if self.score + 30 < opponent.score:
          self.catch_up_counter = 10
          return axl.Action.D
  
      if self.catch_up_counter > 0:
          self.catch_up_counter -= 1
          return axl.Action.D
  
      if (len(self.history) + 1) % 40 == 0 or len(self.history) % 40 == 0:
          return axl.Action.D
  
      if len(self.history) >= 50:
          opponent_coop_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if opponent_coop_rate > 0.7:
              return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
  
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D if self._random.random() < 0.8 else axl.Action.C
      else:
          return axl.Action.D

# Thank you for the feedback. I'll rewrite the strategy with clearer conditions
# for cooperation and defection, ensuring they are appropriately ordered:  1.
# Start by playing D (defect) for the first 10 rounds.  2. For rounds 11-990:
# a. If the opponent played D in the previous round, play D.    b. If the
# opponent played C in the previous round:       i. Play D with a probability of
# P% (initially set to 90%).       ii. Play C with a probability of (100-P)%
# (initially 10%).  3. Every 100 rounds, evaluate your average score over those
# 100 rounds:    a. If your average score is below 2:       Increase P by 5%, up
# to a maximum of 95%.    b. If your average score is above 3:       Decrease P
# by 5%, down to a minimum of 80%.    c. If your average score is between 2 and
# 3 (inclusive):       Keep P unchanged.  4. For the final 10 rounds (991-1000),
# always play D.  This rewritten strategy clarifies the conditions for
# cooperation and defection, and ensures they are ordered appropriately:  - It
# always defects in response to the opponent's defection. - It has a high
# probability of defecting in response to the opponent's cooperation, but allows
# for some cooperation. - It adjusts its aggressiveness based on performance
# every 100 rounds. - It always defects in the final 10 rounds.  The strategy
# maintains its aggressive nature while being clear, logically consistent, and
# free of unreachable conditions.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.P = 90
          self.round_counter = 0
          self.period_scores = []
  
      self.round_counter += 1
  
      if self.round_counter <= 10 or self.round_counter > 990:
          return axl.Action.D
  
      if len(self.history) >= 1:
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          last_round_score = self.total_scores(self.history[-1:], opponent.history[-1:])[0]
          self.period_scores.append(last_round_score)
  
      if self.round_counter % 100 == 0:
          avg_score = sum(self.period_scores) / 100
          if avg_score < 2:
              self.P = min(self.P + 5, 95)
          elif avg_score > 3:
              self.P = max(self.P - 5, 80)
          self.period_scores = []
  
      return axl.Action.D if self._random.random() * 100 < self.P else axl.Action.C

# Here's the revised strategy, taking into account the feedback and clarifying
# the conditions for cooperation and defection:  1. Start by playing D (defect)
# for the first 10 rounds to establish an aggressive stance.  2. For the
# remainder of the game, follow these rules in order:     a. If the opponent has
# cooperated twice in a row in the previous two rounds, cooperate once, then
# immediately defect in the following round.     b. If the opponent has defected
# three times in a row in the previous three rounds, defect for the next five
# rounds.     c. Every 20 rounds, assess the opponent's behavior:       - If
# they've cooperated more than 70% of the time in these 20 rounds, increase your
# defection rate to 90% for the next 10 rounds.       - If they've defected more
# than 90% of the time in these 20 rounds, decrease your defection rate to 70%
# for the next 10 rounds.       - After these 10 rounds of adjustment, return to
# the base defection rate.     d. If you're in the last 100 rounds of the game,
# defect 90% of the time.     e. For all other situations, maintain a base
# defection rate of 80%.  3. When deciding to cooperate or defect based on the
# percentage rules (in 2c, 2d, and 2e), use a random number generator to
# determine each move. For example, if the defection rate is 80%, generate a
# random number between 1 and 100; defect if the number is 80 or below,
# cooperate if it's above 80.  4. Throughout the game, ensure that your moves
# don't create easily recognizable patterns beyond the specific conditions
# outlined above.  This revised strategy maintains an aggressive approach while
# providing clear, ordered conditions for cooperation and defection. It
# incorporates adaptability based on the opponent's recent behavior, increases
# aggression in the endgame, and includes a method for implementing percentage-
# based decisions that avoids predictable patterns.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.base_defection_rate = 0.8
          self.current_defection_rate = self.base_defection_rate
          self.defect_streak = 0
          self.rate_adjustment_rounds = 0
          self.cooperated_last = False
  
      if len(self.history) < 10:
          return axl.Action.D
  
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          if not self.cooperated_last:
              self.cooperated_last = True
              return axl.Action.C
          else:
              self.cooperated_last = False
              return axl.Action.D
  
      self.cooperated_last = False
  
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.defect_streak = 5
      
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      if len(self.history) % 20 == 0:
          recent_20_rounds = opponent.history[-20:]
          coop_rate = recent_20_rounds.count(axl.Action.C) / 20
          if coop_rate > 0.7:
              self.current_defection_rate = 0.9
              self.rate_adjustment_rounds = 10
          elif coop_rate < 0.1:
              self.current_defection_rate = 0.7
              self.rate_adjustment_rounds = 10
  
      if self.rate_adjustment_rounds > 0:
          self.rate_adjustment_rounds -= 1
          if self.rate_adjustment_rounds == 0:
              self.current_defection_rate = self.base_defection_rate
  
      if len(self.history) >= 900:
          self.current_defection_rate = 0.9
  
      self.current_defection_rate += self._random.uniform(-0.05, 0.05)
      self.current_defection_rate = max(0, min(1, self.current_defection_rate))
  
      if self._random.random() < self.current_defection_rate:
          return axl.Action.D
      else:
          return axl.Action.C

# Based on the feedback, here's a revised and clearly ordered strategy:  1. For
# the first 5 rounds, play D (defect).  2. For all subsequent rounds, follow
# these rules in order:     a. If it's a multiple of 25 rounds (i.e., round 25,
# 50, 75, etc.):       - Play C (cooperate)     b. Otherwise, base the decision
# on the opponent's last move:       - If the opponent played C in the last
# round:          - Play D with 90% probability          - Play C with 10%
# probability       - If the opponent played D in the last round:          -
# Play D  3. In any situation not covered by the above rules, play D.  This
# strategy maintains an aggressive approach while clearly defining when to
# cooperate or defect. The conditions are ordered to ensure that:  1. The
# periodic cooperation probe takes precedence every 25th round. 2. For all other
# rounds, the decision is based on the opponent's last move. 3. There's a clear
# default action (defect) for any unforeseen situations.  This ordering
# eliminates any potential ambiguity and ensures that all possible scenarios are
# covered without any unreachable conditions.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First 5 rounds: Defect
      if len(self.history) < 5:
          return axl.Action.D
  
      # Every 25th round: Cooperate
      if (len(self.history) + 1) % 25 == 0:
          return axl.Action.C
  
      # For all other rounds
      if opponent.history[-1] == axl.Action.C:
          # 90% chance to defect, 10% chance to cooperate
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
      else:
          return axl.Action.D

# Here's the revised strategy, taking into account all feedback and ensuring
# clarity on cooperation and defection conditions:  1. First round: Play C
# (cooperate).  2. For rounds 2 through 990:    a. Calculate the opponent's
# defection rate:       - If it's the second round, use only the first round.
# - For rounds 3-10, use all available previous rounds.       - From round 11
# onwards, use the last 10 rounds.     b. Determine the base action:       - If
# the opponent played C in the last round, the base action is C.       - If the
# opponent played D in the last round, set the probability of C as (1 -
# defection rate). Generate a random number between 0 and 1. If this number is
# less than the probability of C, the base action is C; otherwise, it's D.
# c. Apply noise (5% random deviation):       - Generate a random number between
# 0 and 1.       - If this number is less than 0.05, play the opposite of the
# base action.       - If the number is 0.05 or greater, play the base action.
# 3. For the last 10 rounds (991-1000):    - Follow steps 2a and 2b to determine
# the action.    - Do not apply the noise factor; always play the base action.
# This strategy clearly outlines when the player will cooperate or defect:  - It
# will always cooperate in the first round. - In subsequent rounds, it will
# cooperate if:   * The opponent cooperated in the last round (subject to 5%
# noise in rounds 2-990).   * The opponent defected, but the random number
# generated is less than (1 - defection rate) (subject to 5% noise in rounds
# 2-990). - It will defect if:   * The opponent defected in the last round and
# the random number generated is greater than or equal to (1 - defection rate)
# (subject to 5% noise in rounds 2-990). - In the last 10 rounds, the same logic
# applies but without the possibility of noise-induced changes.  The conditions
# are ordered appropriately, with each round following a clear sequence of
# calculations and decisions. This structure ensures that all possible scenarios
# are covered, and there are no ambiguous or unreachable conditions.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
  
      round_number = len(self.history) + 1
      
      if round_number <= 990:
          if round_number == 2:
              defection_rate = opponent.history[-1:].count(axl.Action.D)
          elif round_number <= 10:
              defection_rate = opponent.history.defections / len(opponent.history)
          else:
              defection_rate = opponent.history[-10:].count(axl.Action.D) / 10
  
          if opponent.history[-1] == axl.Action.C:
              base_action = axl.Action.C
          else:
              prob_c = 1 - defection_rate
              base_action = axl.Action.C if self._random.random() < prob_c else axl.Action.D
  
          if self._random.random() < 0.05:
              return axl.Action.D if base_action == axl.Action.C else axl.Action.C
          else:
              return base_action
      else:
          defection_rate = opponent.history[-10:].count(axl.Action.D) / 10
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              prob_c = 1 - defection_rate
              return axl.Action.C if self._random.random() < prob_c else axl.Action.D

# Here's the revised strategy, taking into account the feedback and clarifying
# the conditions for cooperation and defection:  1. Start by playing C
# (cooperate) in the first round.  2. For each subsequent round, follow these
# steps in order:     a. Calculate the opponent's cooperation rate:       - If
# fewer than 10 rounds have been played, use all available rounds.       -
# Otherwise, use the last 10 rounds.       - Round the cooperation rate to the
# nearest percentage point.     b. Check if the Tit-for-Tat mode is active:
# - If the opponent has defected 5 or more times in the last 10 rounds (or in
# all rounds if fewer than 10 have been played), activate Tit-for-Tat mode for
# the next 10 rounds.       - If in Tit-for-Tat mode, play the same move your
# opponent played in the previous round. After 10 rounds of Tit-for-Tat, return
# to the main strategy.     c. If not in Tit-for-Tat mode, determine your move
# as follows:       - Calculate your cooperation probability: Add 10 percentage
# points to the opponent's cooperation rate, capping at 100%.       - Generate a
# random number between 1 and 100.       - If the random number is less than or
# equal to your cooperation probability, play C (cooperate).       - Otherwise,
# play D (defect).  This revised strategy clarifies the decision-making process
# and ensures that conditions are checked in the appropriate order. It addresses
# the following points:  1. It specifies how to handle the initial rounds when
# there's limited history. 2. It explicitly mentions the use of a random number
# generator for probabilistic decisions. 3. It maintains the 10-round duration
# for Tit-for-Tat mode but clarifies when and how it's triggered. 4. It
# specifies rounding the cooperation rate to the nearest percentage point for
# clarity in implementation.  The strategy remains cooperative in nature while
# being adaptive and protective against exploitation. The conditions for
# cooperation and defection are now clearly defined and ordered, ensuring that
# the strategy can be implemented without ambiguity.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.tit_for_tat_mode = 0
          return axl.Action.C
  
      rounds_played = len(self.history)
      last_n_rounds = min(10, rounds_played)
  
      if self.tit_for_tat_mode > 0:
          self.tit_for_tat_mode -= 1
          return opponent.history[-1]
  
      opponent_defections = opponent.history[-last_n_rounds:].count(axl.Action.D)
      if opponent_defections >= 5:
          self.tit_for_tat_mode = 10
          return opponent.history[-1]
  
      opponent_cooperations = opponent.history[-last_n_rounds:].count(axl.Action.C)
      cooperation_rate = round((opponent_cooperations / last_n_rounds) * 100)
      cooperation_probability = min(cooperation_rate + 10, 100)
  
      if self._random.random() * 100 <= cooperation_probability:
          return axl.Action.C
      else:
          return axl.Action.D

# Thank you for the feedback. I'll rewrite the strategy with clear, ordered
# conditions for cooperation and defection:  Cooperative Strategy for Iterated
# Prisoner's Dilemma:  1. In the first round, play Cooperate (C).  2. For all
# subsequent rounds (2 to 1000), follow these ordered steps:     a) If it's the
# second round:       - If the opponent played C in round 1, play C.       - If
# the opponent played D in round 1, play D with 95% probability and C with 5%
# probability.     b) If it's round 3 or later:       - If the opponent played C
# in the previous round, play C.       - If the opponent played D in the
# previous round:         - Play D with 95% probability.         - Play C with
# 5% probability.  3. Apply this strategy consistently for all 1000 rounds,
# including the final round.  This rewrite clarifies the conditions for
# cooperation and defection, ensuring they are ordered appropriately. It
# explicitly addresses how to handle the second round, which depends on the
# first round's outcome, and then provides clear instructions for all subsequent
# rounds. The strategy maintains its cooperative nature, quick response to
# defection, and the small element of randomness to avoid predictability.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(self.history) == 1:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D if self._random.random() < 0.95 else axl.Action.C
      
      # Round 3 or later
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D if self._random.random() < 0.95 else axl.Action.C

# Based on the feedback, here's a revised and more precise version of the
# strategy:  1. Start by playing C (cooperate) for the first move.  2. For each
# subsequent move, evaluate the following conditions in order:     a. If this is
# round 50, 100, 150, ..., (i.e., every 50th round), play C.     b. If the
# opponent has alternated between C and D for the last 6 moves, play D.     c.
# If the opponent played C in the previous round, play C.     d. If the opponent
# played D in the previous round:       - Calculate the opponent's cooperation
# rate (number of C plays divided by total plays so far, rounded to two decimal
# places).       - For the first 5 rounds, use a default cooperation rate of
# 0.5.       - Generate a random number between 0 and 1.       - If this random
# number is less than or equal to max(0.1, min(0.5, cooperation rate)), play C.
# - Otherwise, play D.  3. If none of the above conditions are met (which should
# not happen), play C as a failsafe.  This strategy maintains the cooperative
# approach while being clear about the conditions for cooperation or defection.
# The conditions are ordered to prioritize certain behaviors:  1. Periodic
# cooperation takes highest priority to ensure the "olive branch" is always
# extended every 50 rounds. 2. Countering alternating strategies comes next to
# quickly respond to this specific pattern. 3. Reciprocating cooperation is the
# next priority to encourage mutual cooperation. 4. The adaptive forgiveness
# mechanism is applied last for cases of defection.  The failsafe at the end
# ensures that the strategy always has a defined action, even in unforeseen
# circumstances. This revised version addresses the previous feedback about
# initial rounds and precision, making the strategy more robust and easier to
# implement correctly.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First move: Cooperate
      if not self.history:
          self.opponent_coop_rate = 0.5
          return axl.Action.C
  
      # Every 50th round: Cooperate
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Check if opponent has alternated for the last 6 moves
      if len(opponent.history) >= 6:
          if opponent.history[-6:] == [axl.Action.C, axl.Action.D] * 3 or \
             opponent.history[-6:] == [axl.Action.D, axl.Action.C] * 3:
              return axl.Action.D
  
      # If opponent cooperated last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected last round
      if opponent.history[-1] == axl.Action.D:
          # Update opponent's cooperation rate
          if len(opponent.history) > 5:
              self.opponent_coop_rate = round(opponent.cooperations / len(opponent.history), 2)
  
          # Generate random number and compare with cooperation rate
          if self._random.random() <= max(0.1, min(0.5, self.opponent_coop_rate)):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Failsafe: Cooperate
      return axl.Action.C

# Here's a revised version of the strategy, taking into account the feedback and
# providing clear, ordered conditions for cooperation or defection:  1. Start by
# playing C (cooperate) in the first round.  2. For each subsequent round, make
# your decision in the following order:     a. Forgiveness Mechanism:       -
# With a 2% probability, play C regardless of any other factors.       - If this
# 2% chance doesn't trigger, move to the next step.     b. Adaptive Defense:
# - Calculate the opponent's cooperation rate over the last 20 moves.       - If
# the cooperation rate is 50% or lower, play Tit-for-Tat:         * Play C if
# the opponent's last move was C.         * Play D if the opponent's last move
# was D.       - If the cooperation rate is above 50%, move to the next step.
# c. Base Strategy (Tit-for-Two-Tats):       - Play C if either of the
# opponent's last two moves was C.       - Play D only if both of the opponent's
# last two moves were D.  3. Repeat step 2 for all rounds, including the final
# rounds of the game.  This revised strategy maintains the cooperative approach
# while providing clear, ordered conditions for decision-making in each round.
# The order of operations ensures that:  1. The forgiveness mechanism has the
# first chance to trigger, potentially overriding other considerations. 2. If
# forgiveness doesn't trigger, the strategy adapts to highly uncooperative
# opponents by switching to Tit-for-Tat. 3. For more cooperative opponents, the
# strategy defaults to the forgiving Tit-for-Two-Tats approach.  This ordering
# prevents any conflicting conditions and ensures that each decision point is
# reachable. The strategy balances cooperation, forgiveness, and self-protection
# in a clear and implementable manner.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: cooperate
      if not self.history:
          return axl.Action.C
  
      # Forgiveness Mechanism: 2% chance to cooperate regardless
      if self._random.random() < 0.02:
          return axl.Action.C
  
      # Adaptive Defense: Calculate opponent's cooperation rate over last 20 moves
      last_moves = opponent.history[-20:]
      if last_moves:
          cooperation_rate = last_moves.count(axl.Action.C) / len(last_moves)
          if cooperation_rate <= 0.5:
              # Tit-for-Tat if opponent is uncooperative
              return opponent.history[-1]
  
      # Base Strategy: Tit-for-Two-Tats
      if len(opponent.history) >= 2:
          if axl.Action.C in opponent.history[-2:]:
              return axl.Action.C
      elif len(opponent.history) == 1:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
      
      return axl.Action.D

# Here's the revised strategy, taking into account the feedback and ensuring
# clarity about cooperation and defection conditions:  1. In the first round,
# play C (cooperate).  2. For rounds 2 to 999, follow these steps in order:
# a) If currently in a 2-round D sequence due to detected alternating pattern:
# - Complete the current sequence, then proceed to step b.     b) If the
# opponent has played D for 3 or more consecutive rounds:       - Play D.
# - If this D streak has lasted for 10 rounds, play C once and then return to
# step 2a for the next round.       - If the opponent has now played C twice in
# a row, return to step 2a for the next round.       - Otherwise, continue
# playing D and repeat this step in the next round.     c) Check for alternating
# pattern in the opponent's last 5 moves:       - If CDCDC or DCDC is detected,
# play D for this round and the next round.       - Return to step 2a for the
# next round.     d) If the opponent played C in the last round:       -
# Generate a random number between 0 and 1.       - If the number is less than
# or equal to 0.95, play C.       - If the number is greater than 0.95, play D.
# e) If the opponent played D in the last round:       - Calculate forgiveness
# probability: max(50%, 100% - (0.05 * current round number))       - Generate a
# random number between 0 and 1.       - If the random number is less than or
# equal to the forgiveness probability, play C.       - Otherwise, play D.  3.
# For the final round (round 1000):    - If the opponent played C in round 999,
# play C.    - If the opponent played D in round 999, play D.  This strategy
# maintains a cooperative approach while being robust against various opponent
# behaviors. The conditions for cooperation and defection are clearly stated and
# ordered appropriately, ensuring that more specific conditions (like ongoing
# punishment sequences or pattern detection) are checked before general
# responsive behavior.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.d_sequence = 0
          self.d_streak = 0
          return axl.Action.C
  
      if len(self.history) >= 999:
          return opponent.history[-1]
  
      # Complete 2-round D sequence if active
      if self.d_sequence > 0:
          self.d_sequence -= 1
          return axl.Action.D
  
      last_five = opponent.history[-5:]
  
      # Check for consecutive D plays by opponent
      if len(last_five) >= 3 and last_five[-3:].count(axl.Action.D) >= 3:
          self.d_streak += 1
          if self.d_streak == 10:
              self.d_streak = 0
              return axl.Action.C
          if last_five[-2:] == [axl.Action.C, axl.Action.C]:
              self.d_streak = 0
          else:
              return axl.Action.D
      else:
          self.d_streak = 0
  
      # Check for alternating pattern
      if len(last_five) == 5 and (last_five == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D, axl.Action.C] or
                                  last_five == [axl.Action.D, axl.Action.C, axl.Action.D, axl.Action.C]):
          self.d_sequence = 2
          return axl.Action.D
  
      # Respond to opponent's last move
      if opponent.history[-1] == axl.Action.C:
          if self._random.random() <= 0.95:
              return axl.Action.C
          else:
              return axl.Action.D
      else:
          forgiveness_prob = max(0.5, 1 - (0.05 * len(self.history)))
          if self._random.random() <= forgiveness_prob:
              return axl.Action.C
          else:
              return axl.Action.D

# Here's the revised strategy, taking into account the feedback and clearly
# stating the conditions for cooperation or defection in an appropriate order:
# 1. In the first round, play C.  2. For all subsequent rounds, apply the
# following rules in this specific order:     a) If it's exactly the 20th, 40th,
# 60th, etc. round (i.e., the round number is a multiple of 20), play C.     b)
# If the opponent has played D for the last three consecutive rounds, play D.
# c) If neither condition a) nor b) applies, base your move on the opponent's
# last move:       - If the opponent played C in the last round, play C.       -
# If the opponent played D in the last round:         * Play D with 90%
# probability         * Play C with 10% probability  This revised strategy
# clearly outlines when to cooperate or defect, with conditions ordered to avoid
# conflicts:  - The periodic cooperation (every 20 rounds) takes highest
# priority. - The protection against consistent exploitation (three consecutive
# D's) is second. - The main tit-for-tat with forgiveness mechanism applies when
# the above conditions aren't met.  This ordering ensures that all conditions
# are reachable and that there are no logical contradictions. The strategy
# remains simple, neutral, and adaptive to the opponent's behavior.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Cooperate
      if not self.history:
          return axl.Action.C
  
      # Every 20th round: Cooperate
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # If opponent defected for the last three rounds: Defect
      if len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          return axl.Action.D
  
      # Base move on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C

# Based on the feedback, here's a revised and more clearly defined strategy:  1.
# In the first round, play C (Cooperate).  2. For all subsequent rounds,
# evaluate the following conditions in order:     a. If fewer than 10 rounds
# have been played:       - With 95% probability, copy your opponent's most
# recent move (Tit-for-Tat).       - With 5% probability, play the opposite of
# your opponent's most recent move.     b. If 10 or more rounds have been
# played:       - First, check the opponent's actions in the last 10 rounds:
# - If the opponent has played D (Defect) 7 or more times in these last 10
# rounds:           - With 70% probability, play D.           - With 30%
# probability, continue to step c.         - If the opponent has played D less
# than 7 times in the last 10 rounds, continue to step c.     c. Apply the Tit-
# for-Tat with random deviation:       - With 95% probability, copy your
# opponent's most recent move (Tit-for-Tat).       - With 5% probability, play
# the opposite of your opponent's most recent move.  3. Repeat step 2 for each
# subsequent round of the game.  This revised strategy clearly outlines when to
# cooperate or defect, with conditions ordered appropriately. It addresses the
# early-game scenario when fewer than 10 rounds have been played, and it
# maintains the core neutral approach while providing protection against highly
# aggressive opponents.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(self.history) < 10:
          if self._random.random() < 0.95:
              return opponent.history[-1]
          else:
              return opponent.history[-1].flip()
      
      opponent_defections = opponent.history[-10:].count(axl.Action.D)
      if opponent_defections >= 7:
          if self._random.random() < 0.7:
              return axl.Action.D
          # 30% chance to continue to step c
      
      # Step c: Tit-for-Tat with random deviation
      if self._random.random() < 0.95:
          return opponent.history[-1]
      else:
          return opponent.history[-1].flip()

# Based on the feedback, here's a revised and clearly ordered strategy:  For
# each round of the game, follow these steps in order:  1. If this is the first
# round of the game, play Cooperate (C).  2. If the opponent has defected more
# than 70% of the time in the last 20 rounds (and at least 20 rounds have been
# played), play Defect (D) for this round and the next 4 rounds, regardless of
# what the opponent does. After these 5 rounds, return to step 3.  3. Generate a
# random number between 0 and 1. If this number is less than 0.1 (10% chance),
# play the opposite of what you would play in step 4. If the number is 0.1 or
# greater, proceed to step 4.  4. Play Tit-for-Tat: copy the opponent's move
# from the previous round.  Repeat these steps for all 1000 rounds of the game.
# This strategy clearly outlines when to cooperate or defect:  - Cooperate in
# the first round. - Defect for 5 rounds if the opponent has been overly
# aggressive recently. - Randomly cooperate or defect 10% of the time to
# introduce unpredictability. - Otherwise, cooperate if the opponent cooperated
# in the previous round, or defect if the opponent defected in the previous
# round (Tit-for-Tat).  The conditions are now ordered appropriately, with the
# most specific conditions (first round, punishment for aggressive behavior)
# checked first, followed by the random deviation, and finally the default Tit-
# for-Tat behavior.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.punishment_counter = 0
          return axl.Action.C
  
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      if len(self.history) >= 20:
          recent_defections = opponent.history[-20:].count(axl.Action.D)
          if recent_defections > 14:
              self.punishment_counter = 5
              return axl.Action.D
  
      if self._random.random() < 0.1:
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      return opponent.history[-1]

# Thank you for the feedback. I'll rewrite the strategy with clearer conditions
# and appropriate ordering:  1. Start by playing C (Cooperate) in the first
# round.  2. For each of the remaining 999 rounds, evaluate the following
# conditions in order:     a. Quick adaptation:       If your opponent has
# played 5 consecutive moves different from their previous trend:       -
# Immediately mirror their most recent move.       - Reset your 50-round
# evaluation counter.       - Skip the remaining steps and start the next round.
# b. Pattern recognition:       If you detect a clear repeating pattern in your
# opponent's last 10 moves (defined as an exact repetition of a sequence of 2 to
# 5 moves):       - Identify the best response to that pattern.       - Play
# that best response for this round.       - Continue this best response for up
# to 4 more rounds, unless condition (a) is triggered.       - Skip the
# remaining steps and start the next round.     c. 50-round evaluation (only
# assessed every 50th round):       - If your opponent cooperated more than 60%
# of the time in the last 50 rounds, play C.       - If your opponent cooperated
# less than 40% of the time in the last 50 rounds, play D.       - If neither of
# the above conditions are met (i.e., cooperation rate is between 40% and 60%),
# proceed to step (d).       - Skip the remaining step and start the next round.
# d. Default action:       Mirror your opponent's previous move.  This rewritten
# strategy clearly defines when to cooperate or defect, and the conditions are
# ordered from most specific (quick adaptation) to most general (default
# mirroring). This ordering ensures that more critical or time-sensitive
# conditions are evaluated first, while still maintaining the overall neutral
# approach of the strategy.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.evaluation_counter = 0
          self.quick_adapt_counter = 0
          self.pattern_counter = 0
          self.pattern_response = None
          return axl.Action.C
  
      self.evaluation_counter += 1
  
      # Quick adaptation
      if len(opponent.history) >= 6:
          last_five = opponent.history[-5:]
          previous_trend = opponent.history[-6]
          if all(move != previous_trend for move in last_five):
              self.evaluation_counter = 0
              self.quick_adapt_counter = 5
              self.pattern_counter = 0
              return opponent.history[-1]
  
      if self.quick_adapt_counter > 0:
          self.quick_adapt_counter -= 1
          return opponent.history[-1]
  
      # Pattern recognition
      if len(opponent.history) >= 10 and self.pattern_counter == 0:
          for pattern_length in range(2, 6):
              pattern = opponent.history[-pattern_length:]
              if opponent.history[-2*pattern_length:-pattern_length] == pattern:
                  self.pattern_response = axl.Action.C if pattern.count(axl.Action.C) > pattern.count(axl.Action.D) else axl.Action.D
                  self.pattern_counter = 5
                  return self.pattern_response
  
      if self.pattern_counter > 0:
          self.pattern_counter -= 1
          return self.pattern_response
  
      # 50-round evaluation
      if self.evaluation_counter == 50:
          self.evaluation_counter = 0
          cooperation_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if cooperation_rate > 0.6:
              return axl.Action.C
          elif cooperation_rate < 0.4:
              return axl.Action.D
  
      # Default action
      return opponent.history[-1]

# Based on the feedback, here's a revised and clarified strategy:  1. Start each
# round with a base 50% chance of playing C and 50% chance of playing D.  2.
# Keep track of your opponent's moves in a sliding window of the last 20 rounds.
# 3. Before each move, adjust your strategy in the following order:     a. Based
# on the opponent's behavior in the sliding window:       - If the opponent has
# played C more than 60% of the time, set your probability of playing C to 60%.
# - If the opponent has played D more than 60% of the time, set your probability
# of playing C to 40%.       - Otherwise, keep the probability of playing C at
# 50%.     b. If it's round 950 or later, apply the end-game adjustment:       -
# Decrease the probability of playing C by 1% for each round past 949.       -
# For example, in round 960, decrease the C probability by 11%.     c. Apply the
# random factor:       - With a 5% chance, play the opposite of what the current
# probability suggests.  4. Make your move based on the final adjusted
# probability:    - Play C if a random number (0-1) is less than the probability
# of playing C.    - Otherwise, play D.  This strategy clearly outlines the
# conditions for cooperation or defection, with the adjustments applied in a
# specific order:  1. First, it adapts to the opponent's recent behavior. 2.
# Then, it adjusts for the end-game scenario if applicable. 3. Finally, it adds
# a small random factor for unpredictability.  The conditions are mutually
# exclusive and exhaustive, ensuring that all scenarios are covered without any
# unreachable conditions. The strategy maintains a neutral approach while being
# adaptive and incorporating protection against end-game exploitation.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.sliding_window = []
  
      # Update sliding window
      if opponent.history:
          self.sliding_window.append(opponent.history[-1])
      if len(self.sliding_window) > 20:
          self.sliding_window.pop(0)
  
      # Calculate base probability
      window_size = len(self.sliding_window)
      if window_size > 0:
          c_ratio = self.sliding_window.count(axl.Action.C) / window_size
          if c_ratio > 0.6:
              prob_c = 0.6
          elif c_ratio < 0.4:
              prob_c = 0.4
          else:
              prob_c = 0.5
      else:
          prob_c = 0.5
  
      # Apply end-game adjustment
      current_round = len(self.history)
      if current_round >= 950:
          prob_c = max(0, prob_c - 0.01 * (current_round - 949))
  
      # Apply random factor
      if self._random.random() < 0.05:
          prob_c = 1 - prob_c
  
      # Make final decision
      return axl.Action.C if self._random.random() < prob_c else axl.Action.D

# Here's the revised strategy, taking into account the feedback and clarifying
# the conditions for cooperation and defection:  1. In the first round, always
# Cooperate (C).  2. For rounds 2-950, use the following decision process in
# order:     a. If the opponent has defected in the last three consecutive
# rounds, Defect (D) for the next three rounds, regardless of the opponent's
# moves. After these three rounds, return to step b.     b. Calculate the
# opponent's cooperation rate over the last 20 rounds. If this rate is below
# 40%, there's a 60% chance to Defect (D) and a 40% chance to Cooperate (C). Use
# this probability for the next 5 rounds, then return to step c.     c. If
# neither a nor b apply, play Tit-for-Tat: copy the opponent's most recent move.
# 3. For the last 50 rounds (951-1000):     a. Calculate a defection
# probability: (current round number - 950) / 50       For example, in round
# 975, the defection probability would be (975 - 950) / 50 = 0.5 or 50%     b.
# Use this calculated probability to decide whether to Defect (D) or Cooperate
# (C)  4. Tie-breaker for round 2: If the opponent defected in round 1, there's
# a 10% chance to Cooperate (C) instead of following Tit-for-Tat. This helps to
# potentially break cycles of mutual defection early in the game.  This strategy
# maintains a neutral approach while being clear about when to cooperate or
# defect. The conditions are ordered to prioritize responses to recent
# aggressive behavior, then adapt to the opponent's overall strategy, and
# finally default to Tit-for-Tat. The end-game strategy is separate and
# overrides the mid-game rules for the last 50 rounds.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defect_counter = 0
          self.probability_rounds = 0
          return axl.Action.C
  
      current_round = len(self.history) + 1
  
      if current_round == 2 and opponent.history[-1] == axl.Action.D:
          if self._random.random() < 0.1:
              return axl.Action.C
  
      if current_round <= 950:
          if self.defect_counter > 0:
              self.defect_counter -= 1
              return axl.Action.D
  
          if opponent.history[-3:].count(axl.Action.D) == 3:
              self.defect_counter = 3
              return axl.Action.D
  
          if self.probability_rounds > 0:
              self.probability_rounds -= 1
              return axl.Action.D if self._random.random() < 0.6 else axl.Action.C
  
          if current_round > 20:
              recent_20 = opponent.history[-20:]
              if recent_20.count(axl.Action.C) / 20 < 0.4:
                  self.probability_rounds = 5
                  return axl.Action.D if self._random.random() < 0.6 else axl.Action.C
  
          return opponent.history[-1]
      else:
          defection_probability = (current_round - 950) / 50
          return axl.Action.D if self._random.random() < defection_probability else axl.Action.C