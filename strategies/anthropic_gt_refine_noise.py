import axelrod as axl

from evollm.common import Attitude, auto_update_score, LLM_Strategy



# Here's a revised aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent's action in the previous
# round was D, defect.  3. If the opponent's action in the previous round was C,
# defect with 70% probability and cooperate with 30% probability.  4. Every
# 40-60 rounds (randomly chosen), cooperate once regardless of the opponent's
# previous move.  5. In the last 20 rounds of the game, defect unless the
# opponent has cooperated in at least 3 of the last 5 rounds.  6. If your
# current score is more than 30 points behind your opponent's, increase the
# defection probability to 90% for the next 15 rounds.  7. If you've cooperated
# for 3 consecutive rounds, defect in the next round regardless of the
# opponent's moves.  8. If the opponent has cooperated for 4-6 consecutive
# rounds (accounting for possible noise), cooperate once, then return to the
# main strategy.  9. Keep a rolling average of the opponent's cooperation rate
# over the last 20 rounds. If this rate exceeds 70%, cooperate with 40%
# probability instead of 30% in rule 3.  10. If both players have defected for 5
# consecutive rounds, cooperate once to attempt breaking the cycle.  11. After
# every 100 rounds, evaluate the success of your strategy. If your average score
# per round is below 2, increase the cooperation probability in rule 3 by 5% (up
# to a maximum of 40%).  Follow these rules in the order presented, moving to
# the next rule only if the conditions for the previous rules are not met. When
# interpreting the opponent's actions, consider that there's a 10% chance their
# intended action was flipped due to noise.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperate_round = self._random.randint(40, 60)
          self.defect_streak = 0
          self.cooperate_streak = 0
          self.opponent_cooperate_streak = 0
          self.defect_probability = 0.7
          self.cooperate_probability = 0.3
          self.defect_boost = 0
          self.last_evaluation_round = 0
          return axl.Action.D  # Rule 1: Start by defecting
  
      # Helper function to calculate rolling cooperation rate
      def rolling_cooperation_rate(history, window=20):
          return history[-window:].count(axl.Action.C) / min(len(history), window)
  
      # Rule 6: If more than 30 points behind, increase defection probability to 90% for 15 rounds
      if self.defect_boost > 0:
          self.defect_boost -= 1
          defect_probability = 0.9
      elif self.score < opponent.score - 30:
          self.defect_boost = 15
          defect_probability = 0.9
      else:
          defect_probability = self.defect_probability
  
      # Rule 5: In the last 20 rounds, defect unless opponent cooperated in 3 of the last 5 rounds
      if len(self.history) >= 980:
          if opponent.history[-5:].count(axl.Action.C) >= 3:
              return axl.Action.C
          return axl.Action.D
  
      # Rule 7: If cooperated for 3 consecutive rounds, defect
      if self.cooperate_streak >= 3:
          self.cooperate_streak = 0
          return axl.Action.D
  
      # Rule 8: If opponent cooperated for 4-6 consecutive rounds, cooperate once
      if 4 <= self.opponent_cooperate_streak <= 6:
          self.opponent_cooperate_streak = 0
          return axl.Action.C
  
      # Rule 10: If both players defected for 5 consecutive rounds, cooperate once
      if self.defect_streak >= 5:
          self.defect_streak = 0
          return axl.Action.C
  
      # Rule 4: Every 40-60 rounds, cooperate once
      if len(self.history) == self.cooperate_round:
          self.cooperate_round = len(self.history) + self._random.randint(40, 60)
          return axl.Action.C
  
      # Rule 3: If opponent cooperated last round, defect with 70% probability, else cooperate
      if opponent.history[-1] == axl.Action.C:
          if self._random.random_choice(self.cooperate_probability):
              return axl.Action.C
          return axl.Action.D
  
      # Rule 2: If opponent defected last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 9: Adjust cooperation probability based on opponent's cooperation rate
      if rolling_cooperation_rate(opponent.history) > 0.7:
          self.cooperate_probability = 0.4
      else:
          self.cooperate_probability = 0.3
  
      # Rule 11: Every 100 rounds, evaluate strategy success and adjust cooperation probability
      if len(self.history) >= self.last_evaluation_round + 100:
          avg_score = self.score / len(self.history)
          if avg_score < 2 and self.cooperate_probability < 0.4:
              self.cooperate_probability += 0.05
          self.last_evaluation_round = len(self.history)
  
      # Update streaks
      if self.history[-1] == axl.Action.C:
          self.cooperate_streak += 1
          self.defect_streak = 0
      else:
          self.cooperate_streak = 0
          self.defect_streak += 1
  
      if opponent.history[-1] == axl.Action.C:
          self.opponent_cooperate_streak += 1
      else:
          self.opponent_cooperate_streak = 0
  
      # Default action: Defect
      return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.    - If it's your first time encountering a D from the
# opponent, play C once more before switching to D.  3. To account for noise:
# - If the opponent's action changes from their usual pattern, don't immediately
# retaliate. Instead, wait for two consecutive different actions before changing
# your strategy.  4. Every 20 rounds, attempt to re-establish cooperation by
# playing C, regardless of the opponent's last move.  5. Keep a rolling count of
# the opponent's defections in the last 30 rounds. If this count exceeds 20
# (about 67%), switch to always playing D for the next 5 rounds before returning
# to the main strategy.  6. Adjust the forgiveness mechanism:    - If the
# opponent defects immediately after three consecutive forgiveness attempts,
# suspend the forgiveness mechanism for the next 50 rounds.  7. For the last 20
# rounds:    - If your cumulative score is higher than what you'd expect from
# mutual cooperation, continue with the main strategy.    - If your score is
# lower, switch to always playing D.  8. Throughout the game, if your score
# falls more than 50 points below what you'd expect from mutual cooperation,
# become more defensive by requiring 3 consecutive C moves from the opponent
# before you cooperate again.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.first_defection_encountered = False
          self.defection_streak = 0
          self.forgiveness_attempts = 0
          self.forgiveness_suspended_until = 0
          self.always_defect_until = 0
          return axl.Action.C
  
      # Check if we are in the forgiveness suspension period
      if len(self.history) < self.forgiveness_suspended_until:
          return axl.Action.D
  
      # Check if we are in the always defect period
      if len(self.history) < self.always_defect_until:
          return axl.Action.D
  
      # Check if we are in the last 20 rounds
      if len(self.history) >= 980:
          expected_coop_score = len(self.history) * 3
          if self.score < expected_coop_score:
              return axl.Action.D
          else:
              return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
  
      # Every 20 rounds, attempt to re-establish cooperation
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # Keep a rolling count of defections in the last 30 rounds
      recent_defections = opponent.history[-30:].count(axl.Action.D)
      if recent_defections > 20:
          self.always_defect_until = len(self.history) + 5
          return axl.Action.D
  
      # If the opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          if not self.first_defection_encountered:
              self.first_defection_encountered = True
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If the opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the score falls more than 50 points below expected cooperation score
      expected_coop_score = len(self.history) * 3
      if self.score < expected_coop_score - 50:
          if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
              return axl.Action.C
          else:
              return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating for the first 10 rounds to establish a baseline.  2. Keep track of
# your opponent's actions and calculate their cooperation rate, accounting for
# the 10% noise factor.  3. If your opponent's cooperation rate is above 65%,
# cooperate.  4. If your opponent's cooperation rate is between 35% and 65%,
# mirror their last move.  5. If your opponent's cooperation rate is below 35%,
# defect.  6. Every 75 rounds, randomly choose to cooperate with a 50%
# probability, regardless of the opponent's history, to allow for potential
# reconciliation without being predictable.  7. In the last 25 rounds, play
# according to the opponent's cooperation rate without automatically defecting.
# 8. If you observe an unexpected defection, reduce the opponent's cooperation
# rate by 2 percentage points to account for possible noise.  9. If you observe
# two consecutive unexpected defections, reduce the opponent's cooperation rate
# by 5 percentage points.  10. Recalculate the opponent's cooperation rate using
# a rolling window of the last 100 moves to adapt to strategy changes while
# maintaining historical context.  11. If stuck in mutual defection for more
# than 10 rounds, cooperate with a 20% probability to attempt breaking the
# cycle.  12. Adjust your own moves for the 10% noise factor by occasionally
# (10% of the time) implementing the opposite of your intended move.  13. Every
# 100 rounds, compare your cumulative score to the opponent's. If you're behind
# by more than 50 points, slightly increase your defection threshold (lower the
# 35% threshold) for the next 100 rounds.  14. In the first 50 rounds, use a
# more forgiving threshold (cooperate above 55%, defect below 45%) to account
# for initial fluctuations and establish a cooperative baseline if possible.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_rate = 1.0  # Start assuming full cooperation
          self.defection_threshold = 0.35  # Initial defection threshold
          self.cooperation_threshold = 0.65  # Initial cooperation threshold
          self.rounds_since_last_defection = 0  # Track rounds since last defection
          self.consecutive_defections = 0  # Track consecutive defections
          self.reconciliation_round = 75  # Every 75 rounds, random cooperation
          self.mutual_defection_rounds = 0  # Track mutual defection rounds
          self.last_100_rounds = []  # Track last 100 rounds for rolling window
          return axl.Action.C  # Cooperate on the first round
  
      # Cooperate for the first 10 rounds
      if len(self.history) < 10:
          return axl.Action.C
  
      # Update cooperation rate using a rolling window of the last 100 rounds
      if len(self.history) > 100:
          self.last_100_rounds = self.history[-100:]
      else:
          self.last_100_rounds = self.history
  
      opponent_cooperations = opponent.history[-100:].count(axl.Action.C)
      opponent_defections = opponent.history[-100:].count(axl.Action.D)
      total_moves = opponent_cooperations + opponent_defections
      if total_moves > 0:
          self.cooperation_rate = opponent_cooperations / total_moves
  
      # Adjust cooperation rate for unexpected defections
      if opponent.history[-1] == axl.Action.D and self.history[-1] == axl.Action.C:
          self.consecutive_defections += 1
          if self.consecutive_defections == 1:
              self.cooperation_rate = max(0, self.cooperation_rate - 0.02)
          elif self.consecutive_defections == 2:
              self.cooperation_rate = max(0, self.cooperation_rate - 0.05)
      else:
          self.consecutive_defections = 0
  
      # Every 75 rounds, randomly cooperate with 50% probability
      if len(self.history) % self.reconciliation_round == 0:
          return self._random.random_choice(0.5)
  
      # If stuck in mutual defection for more than 10 rounds, cooperate with 20% probability
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.mutual_defection_rounds += 1
          if self.mutual_defection_rounds > 10:
              return self._random.random_choice(0.2)
      else:
          self.mutual_defection_rounds = 0
  
      # Adjust thresholds after 50 rounds
      if len(self.history) < 50:
          self.defection_threshold = 0.45
          self.cooperation_threshold = 0.55
  
      # Every 100 rounds, adjust defection threshold if behind by more than 50 points
      if len(self.history) % 100 == 0:
          if opponent.score - self.score > 50:
              self.defection_threshold = max(0, self.defection_threshold - 0.05)
  
      # In the last 25 rounds, play according to the opponent's cooperation rate
      if len(self.history) >= 975:
          if self.cooperation_rate > self.cooperation_threshold:
              return axl.Action.C
          elif self.cooperation_rate < self.defection_threshold:
              return axl.Action.D
          else:
              return opponent.history[-1]
  
      # Main strategy logic based on cooperation rate
      if self.cooperation_rate > self.cooperation_threshold:
          intended_move = axl.Action.C
      elif self.cooperation_rate < self.defection_threshold:
          intended_move = axl.Action.D
      else:
          intended_move = opponent.history[-1]
  
      # Adjust for 10% noise factor by occasionally flipping the intended move
      if self._random.random_choice(0.1):
          return intended_move.flip()
      return intended_move



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to encourage cooperation.  2. If the opponent
# played C in the previous round, play C with 80% probability and D with 20%
# probability. This maintains cooperation while occasionally testing for
# exploitation.  3. If the opponent played D in the previous round, play D with
# 80% probability and C with 20% probability. This punishes defection while
# allowing for recovery of cooperation.  4. Keep track of the last 5 rounds. If
# there have been 4 or more mutual cooperations (CC), continue playing C to
# maintain the beneficial relationship.  5. Every 20 rounds, reassess your
# cumulative score compared to the theoretical maximum (5 points per round). If
# you're below 60% of the maximum, increase your defection probability by 10%
# for the next 20 rounds.  6. In the last 50 rounds, gradually increase your
# defection probability. Start with a 30% chance of defection, increasing by 10%
# every 10 rounds.  7. Throughout the game, try to identify patterns in the
# opponent's play over the last 10 rounds. If a clear pattern emerges, adjust
# your strategy to exploit it for 5 rounds, then return to the base strategy.
# 8. To account for noise, if an unexpected outcome occurs (e.g., you lose
# points when you intended to cooperate), don't immediately alter your strategy.
# Instead, wait for 2-3 consistent rounds before adapting.  9. If mutual
# defection (DD) occurs for 5 consecutive rounds, play C for 2 rounds to attempt
# breaking the cycle.  10. Maintain flexibility: every 100 rounds, randomly
# choose to play either fully cooperatively or fully defectively for 5 rounds to
# probe the opponent's response and potentially discover new strategies.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.2  # Base defection probability
          self.rounds_since_last_reassessment = 0
          self.pattern_exploitation_rounds = 0
          self.pattern_detected = False
          self.mutual_defection_count = 0
          self.random_probe_rounds = 0
          return axl.Action.C  # Start with cooperation
  
      # Helper function to detect patterns in the last 10 rounds
      def detect_pattern():
          if len(opponent.history) < 10:
              return False
          last_10_moves = opponent.history[-10:]
          if last_10_moves.count(last_10_moves[0]) == 10:  # Simple pattern detection
              return True
          return False
  
      # Helper function to calculate mutual cooperations in the last 5 rounds
      def mutual_cooperations_in_last_5():
          return sum(1 for i in range(1, min(6, len(self.history)))
                     if self.history[-i] == axl.Action.C and opponent.history[-i] == axl.Action.C)
  
      # Step 4: If there have been 4 or more mutual cooperations in the last 5 rounds, play C
      if mutual_cooperations_in_last_5() >= 4:
          return axl.Action.C
  
      # Step 5: Every 20 rounds, reassess score and adjust defection probability
      self.rounds_since_last_reassessment += 1
      if self.rounds_since_last_reassessment >= 20:
          max_possible_score = 5 * len(self.history)
          if self.score < 0.6 * max_possible_score:
              self.defection_probability = min(1.0, self.defection_probability + 0.1)
          self.rounds_since_last_reassessment = 0
  
      # Step 6: In the last 50 rounds, gradually increase defection probability
      if len(self.history) >= 950:
          rounds_left = 1000 - len(self.history)
          self.defection_probability = 0.3 + (10 - rounds_left // 10) * 0.1
  
      # Step 7: Detect patterns and exploit for 5 rounds
      if self.pattern_exploitation_rounds > 0:
          self.pattern_exploitation_rounds -= 1
          return axl.Action.D if self.pattern_detected else axl.Action.C
      elif detect_pattern():
          self.pattern_detected = True
          self.pattern_exploitation_rounds = 5
          return axl.Action.D
  
      # Step 9: If mutual defection occurs for 5 consecutive rounds, play C for 2 rounds
      if len(self.history) >= 5 and all(self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, 6)):
          self.mutual_defection_count = 2
      if self.mutual_defection_count > 0:
          self.mutual_defection_count -= 1
          return axl.Action.C
  
      # Step 10: Every 100 rounds, randomly probe with full cooperation or defection
      if self.random_probe_rounds > 0:
          self.random_probe_rounds -= 1
          return axl.Action.C if self._random.random_choice(0.5) else axl.Action.D
      elif len(self.history) % 100 == 0:
          self.random_probe_rounds = 5
          return axl.Action.C if self._random.random_choice(0.5) else axl.Action.D
  
      # Step 2 and 3: Base strategy based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.8)
      else:
          return self._random.random_choice(0.2)



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - If the opponent played D in the
# previous round, only respond with D if they've defected twice in the last
# three rounds. This helps account for potential noise.  3. Every 15 rounds,
# play C regardless of the opponent's recent moves to provide opportunities for
# restoring cooperation.  4. If the opponent has defected more than 40% of the
# time in the last 30 rounds:    - Play D for the next 5 rounds.    - Then
# attempt to restore cooperation by playing C for 2 rounds.    - Return to the
# main strategy afterwards.  5. In the last 20 rounds of the game, gradually
# increase the likelihood of playing D:    - In rounds 981-990, play D with 25%
# probability.    - In rounds 991-1000, play D with 50% probability.  6. If
# caught in a cycle of mutual defection for more than 10 rounds, attempt to
# break it by playing C for 2 consecutive rounds.  7. After each forgiveness
# period (step 3) or cooperation restoration attempt (steps 4 and 6), revert to
# step 2 of the strategy.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if opponent defected twice in the last 3 rounds
      def opponent_defected_twice_in_last_three():
          return opponent.history[-3:].count(axl.Action.D) >= 2
  
      # Helper function to check if opponent defected more than 40% in the last 30 rounds
      def opponent_defected_more_than_40_percent_in_last_30():
          if len(opponent.history) < 30:
              return False
          return opponent.history[-30:].count(axl.Action.D) / 30 > 0.4
  
      # Helper function to check if mutual defection has occurred for more than 10 rounds
      def mutual_defection_for_more_than_10_rounds():
          if len(self.history) < 10:
              return False
          return self.history[-10:] == [axl.Action.D] * 10 and opponent.history[-10:] == [axl.Action.D] * 10
  
      # Step 1: First round, play C
      if self.first_round():
          self.forced_defection_rounds = 0  # Track forced defection rounds (step 4)
          self.cooperation_restoration_rounds = 0  # Track cooperation restoration rounds (step 4)
          self.mutual_defection_break_rounds = 0  # Track mutual defection break rounds (step 6)
          return axl.Action.C
  
      # Step 4: If opponent defected more than 40% in the last 30 rounds
      if opponent_defected_more_than_40_percent_in_last_30():
          if self.forced_defection_rounds < 5:
              self.forced_defection_rounds += 1
              return axl.Action.D
          elif self.cooperation_restoration_rounds < 2:
              self.cooperation_restoration_rounds += 1
              return axl.Action.C
          else:
              self.forced_defection_rounds = 0
              self.cooperation_restoration_rounds = 0
  
      # Step 6: If caught in a cycle of mutual defection for more than 10 rounds
      if mutual_defection_for_more_than_10_rounds():
          if self.mutual_defection_break_rounds < 2:
              self.mutual_defection_break_rounds += 1
              return axl.Action.C
          else:
              self.mutual_defection_break_rounds = 0
  
      # Step 5: In the last 20 rounds, increase the likelihood of playing D
      if len(self.history) >= 981:
          if len(self.history) <= 990:
              if self._random.random_choice(0.25):
                  return axl.Action.D
          elif len(self.history) <= 1000:
              if self._random.random_choice(0.5):
                  return axl.Action.D
  
      # Step 3: Every 15 rounds, play C regardless of opponent's recent moves
      if len(self.history) % 15 == 0:
          return axl.Action.C
  
      # Step 2: Main strategy
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          if opponent_defected_twice_in_last_three():
              return axl.Action.D
          else:
              return axl.Action.C



# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. In subsequent rounds:    - If the opponent's last
# observed action was cooperation, cooperate.    - If the opponent's last
# observed action was defection, defect.  3. Keep a rolling average of the
# opponent's cooperation rate over the last 20 rounds. If this rate drops below
# 40%, defect for the next 3 rounds before reassessing.  4. Every 15 rounds,
# cooperate regardless of the opponent's previous move to allow for potential
# recovery of mutual cooperation.  5. If your score falls more than 10 points
# behind your opponent's, increase your defection probability by 20% for the
# next 5 rounds before returning to the main strategy.  6. To account for noise:
# - Consider an action "observed" only if it's consistent for 2 out of 3 rounds.
# - If an action seems inconsistent with the opponent's pattern, assume it's due
# to noise and base your next move on their previous consistent action.  7. In
# the last 20 rounds:    - If the opponent's cooperation rate in the last 50
# rounds is above 70%, continue with the main strategy.    - Otherwise, always
# defect.  8. Reassess and slightly adjust cooperation thresholds every 100
# rounds based on the overall game outcome to adapt to the opponent's long-term
# strategy.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 0.4
      DEFECT_PROB_INCREASE = 0.2
      COOPERATION_RECOVERY_ROUND = 15
      DEFECT_PENALTY_ROUNDS = 3
      DEFECT_PROB_ROUNDS = 5
      LAST_ROUNDS_THRESHOLD = 20
      LONG_TERM_COOP_THRESHOLD = 0.7
      SCORE_DIFFERENCE_THRESHOLD = 10
      ROLLING_WINDOW = 20
      ADJUSTMENT_INTERVAL = 100
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_penalty = 0  # Number of rounds to defect due to low cooperation rate
          self.defect_prob_rounds = 0  # Number of rounds to increase defection probability
          self.defect_prob = 0  # Current defection probability
          self.last_consistent_action = axl.Action.C  # Last consistent action observed
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, window):
          if len(history) < window:
              window = len(history)
          return history[-window:].count(axl.Action.C) / window if window > 0 else 0
  
      # Helper function to check if an action is consistent over the last 3 rounds
      def consistent_action(history):
          if len(history) < 3:
              return history[-1]  # Not enough history, return the last action
          last_three = history[-3:]
          if last_three.count(last_three[0]) >= 2:
              return last_three[0]  # Return the consistent action
          return None  # No consistent action
  
      # Step 2: Determine the opponent's last consistent action
      consistent_opponent_action = consistent_action(opponent.history)
      if consistent_opponent_action is not None:
          self.last_consistent_action = consistent_opponent_action
  
      # Step 3: Calculate the rolling cooperation rate over the last 20 rounds
      opponent_coop_rate = cooperation_rate(opponent.history, ROLLING_WINDOW)
  
      # Step 4: Every 15 rounds, cooperate regardless of the opponent's move
      if len(self.history) % COOPERATION_RECOVERY_ROUND == 0:
          return axl.Action.C
  
      # Step 5: If score difference is more than 10 points, increase defection probability
      if self.defect_prob_rounds > 0:
          self.defect_prob_rounds -= 1
      elif self.score < opponent.score - SCORE_DIFFERENCE_THRESHOLD:
          self.defect_prob = min(1, self.defect_prob + DEFECT_PROB_INCREASE)
          self.defect_prob_rounds = DEFECT_PROB_ROUNDS
  
      # Step 6: If cooperation rate drops below 40%, defect for the next 3 rounds
      if self.defect_penalty > 0:
          self.defect_penalty -= 1
          return axl.Action.D
      elif opponent_coop_rate < COOPERATION_THRESHOLD:
          self.defect_penalty = DEFECT_PENALTY_ROUNDS
          return axl.Action.D
  
      # Step 7: In the last 20 rounds, adjust strategy based on long-term cooperation rate
      if len(self.history) >= 1000 - LAST_ROUNDS_THRESHOLD:
          long_term_coop_rate = cooperation_rate(opponent.history, 50)
          if long_term_coop_rate < LONG_TERM_COOP_THRESHOLD:
              return axl.Action.D
  
      # Step 8: Reassess and adjust cooperation thresholds every 100 rounds
      if len(self.history) % ADJUSTMENT_INTERVAL == 0:
          # Placeholder for future adjustments (not implemented in this version)
          pass
  
      # Step 2: Main strategy - Tit for Tat with noise handling
      if self._random.random_choice(self.defect_prob):
          return axl.Action.D
      if self.last_consistent_action == axl.Action.D:
          return axl.Action.D
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent's action in the
# previous round was D, defect with 90% probability and cooperate with 10%
# probability in the next round.  3. If the opponent's action in the previous
# round was C, cooperate with 70% probability and defect with 30% probability in
# the next round.  4. To account for noise, consider the opponent's actions over
# the last 3 rounds. If at least 2 out of 3 were C, treat it as a cooperative
# trend; if at least 2 out of 3 were D, treat it as a defective trend.  5. If
# you've defected for 3 consecutive rounds, cooperate in the next round to test
# the opponent's response.  6. If the opponent has shown a cooperative trend for
# 5 consecutive evaluations (as per rule 4), switch to cooperating for the next
# 5 rounds to establish a mutually beneficial pattern.  7. In the last 20 rounds
# of the game, mirror the opponent's most frequent action from the previous 10
# rounds.  8. If your current score is more than 30 points behind the
# opponent's, increase the probability of defection by 10% for the next 10
# rounds, then reassess.  9. Every 100 rounds, analyze the overall trend of the
# opponent's behavior. If they've been mostly cooperative (>60% C), slightly
# increase your cooperation probability. If they've been mostly defective (>60%
# D), slightly increase your defection probability.  10. Always leave a 5%
# chance of a random action to probe for changes in the opponent's strategy and
# to make your own strategy less predictable.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_streak = 0
          self.cooperative_trend_count = 0
          self.defection_probability_adjustment = 0
          self.cooperate_for_next_5 = 0
          return axl.Action.C
  
      # Helper function to determine cooperative or defective trend in the last 3 rounds
      def get_trend(history):
          if len(history) < 3:
              return None
          last_3 = history[-3:]
          if last_3.count(axl.Action.C) >= 2:
              return "cooperative"
          elif last_3.count(axl.Action.D) >= 2:
              return "defective"
          return None
  
      # Helper function to adjust probabilities based on opponent's behavior
      def adjust_probabilities():
          if len(opponent.history) >= 100:
              last_100 = opponent.history[-100:]
              coop_rate = last_100.count(axl.Action.C) / 100
              if coop_rate > 0.6:
                  self.defection_probability_adjustment = max(self.defection_probability_adjustment - 0.05, 0)
              elif coop_rate < 0.4:
                  self.defection_probability_adjustment = min(self.defection_probability_adjustment + 0.05, 0.5)
  
      # Rule 7: In the last 20 rounds, mirror the opponent's most frequent action from the last 10 rounds
      if len(self.history) >= 980:
          last_10 = opponent.history[-10:]
          if last_10.count(axl.Action.C) > last_10.count(axl.Action.D):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 8: If more than 30 points behind, increase defection probability by 10% for 10 rounds
      if self.score < opponent.score - 30:
          self.defection_probability_adjustment = min(self.defection_probability_adjustment + 0.1, 0.5)
  
      # Rule 6: If cooperative trend for 5 consecutive evaluations, cooperate for next 5 rounds
      if self.cooperate_for_next_5 > 0:
          self.cooperate_for_next_5 -= 1
          return axl.Action.C
  
      # Rule 4: Check for cooperative or defective trend in the last 3 rounds
      trend = get_trend(opponent.history)
      if trend == "cooperative":
          self.cooperative_trend_count += 1
          if self.cooperative_trend_count >= 5:
              self.cooperate_for_next_5 = 5
              self.cooperative_trend_count = 0
      else:
          self.cooperative_trend_count = 0
  
      # Rule 5: If defected for 3 consecutive rounds, cooperate in the next round
      if self.defection_streak >= 3:
          self.defection_streak = 0
          return axl.Action.C
  
      # Rule 2 and 3: Adjust probabilities based on opponent's last action
      if opponent.history[-1] == axl.Action.D:
          prob_coop = 0.1 - self.defection_probability_adjustment
          self.defection_streak += 1
      else:
          prob_coop = 0.7 - self.defection_probability_adjustment
          self.defection_streak = 0
  
      # Rule 9: Adjust probabilities every 100 rounds
      if len(self.history) % 100 == 0:
          adjust_probabilities()
  
      # Rule 10: 5% chance of random action
      if self._random.random() < 0.05:
          return self._random.random_choice(0.5)
  
      # Choose action based on calculated probability
      return self._random.random_choice(prob_coop)



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 20 rounds,
# play C regardless of the opponent's recent moves to signal cooperative intent.
# 4. If the opponent has defected more than 40% of the time in the last 30
# rounds, switch to playing D for the next 10 rounds before reverting to the
# main strategy.  5. In the last 20 rounds of the game, mirror the opponent's
# last move.  6. If your score is more than 50 points behind your opponent's
# after 250 rounds, increase your defection frequency by playing D every other
# round for the next 50 rounds, then reassess.  7. If you defect due to noise
# when you intended to cooperate, play C for the next two rounds to signal your
# cooperative intent.  8. If the opponent seems to be following a similar
# cooperative strategy (alternating C and D after your unintended defections),
# be more lenient in interpreting their actions.  9. Reassess the opponent's
# overall strategy every 100 rounds and adjust your cooperation threshold
# accordingly.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_streak = 0  # Track defection streak for rule 4
          self.defection_mode = False  # Track if we're in defection mode for rule 4
          self.defection_mode_rounds = 0  # Track rounds left in defection mode
          self.alternate_defection = False  # Track alternating defection for rule 6
          return axl.Action.C  # Rule 1: Start with C
  
      # Rule 7: If we defected due to noise, play C for the next two rounds
      if len(self.history) >= 2 and self.history[-2:] == [axl.Action.D, axl.Action.C]:
          return axl.Action.C
  
      # Rule 4: If opponent defected more than 40% in the last 30 rounds, enter defection mode
      if len(self.history) >= 30:
          recent_defections = opponent.history[-30:].count(axl.Action.D)
          if recent_defections / 30 > 0.4 and not self.defection_mode:
              self.defection_mode = True
              self.defection_mode_rounds = 10
  
      # If in defection mode, play D for 10 rounds
      if self.defection_mode:
          self.defection_mode_rounds -= 1
          if self.defection_mode_rounds == 0:
              self.defection_mode = False
          return axl.Action.D
  
      # Rule 6: If more than 50 points behind after 250 rounds, alternate D every other round
      if len(self.history) > 250:
          if opponent.score - self.score > 50:
              self.alternate_defection = not self.alternate_defection
              if self.alternate_defection:
                  return axl.Action.D
  
      # Rule 5: In the last 20 rounds, mirror the opponent's last move
      if len(self.history) >= 980:
          return opponent.history[-1]
  
      # Rule 3: Every 20 rounds, play C to signal cooperation
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # Rule 2: Play C if opponent played C in at least 2 of the last 3 rounds, else play D
      if len(opponent.history) >= 3:
          recent_moves = opponent.history[-3:]
          if recent_moves.count(axl.Action.C) >= 2:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Default to cooperation if none of the above conditions apply
      return axl.Action.C



# Here's a revised strategy incorporating the feedback:  1. Start by cooperating
# in the first round.  2. For subsequent rounds:     a. Consider the last 10
# rounds, accounting for the 10% noise:       - Count an action as cooperation
# if it occurred at least 8 out of 10 times.       - Count an action as
# defection if it occurred at least 8 out of 10 times.       - Otherwise,
# consider it mixed.     b. If the opponent's pattern is cooperation, cooperate.
# c. If the opponent's pattern is defection, defect.        d. If the opponent's
# pattern is mixed:       - Cooperate if there are more cooperations than
# defections.       - Defect if there are more defections than cooperations.
# - If equal, cooperate.  3. Every 50 rounds:    - Calculate your average score
# and the opponent's average score.    - If your score is lower, become more
# aggressive: defect for the next 5 rounds.    - If scores are close (within 0.5
# points), continue with the main strategy.    - If your score is significantly
# higher, cooperate for the next 5 rounds to encourage mutual cooperation.  4.
# If there have been 20 consecutive rounds of mutual defection:    - Attempt to
# break the cycle by cooperating for 3 rounds, then resume the main strategy.
# 5. In the last 20 rounds:    - If your cumulative score is higher, continue
# with the main strategy.    - If your cumulative score is lower, alternate
# between cooperation and defection.  6. Every 100 rounds, reassess the
# opponent's overall behavior and adjust your cooperation threshold accordingly.
# 7. If none of the above conditions are met, cooperate.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to analyze the last 10 rounds
      def analyze_last_10_rounds():
          last_10 = opponent.history[-10:]
          if len(last_10) < 10:
              return "mixed"
          
          coop_count = last_10.count(axl.Action.C)
          defect_count = last_10.count(axl.Action.D)
          
          if coop_count >= 8:
              return "cooperation"
          elif defect_count >= 8:
              return "defection"
          else:
              return "mixed"
      
      # Helper function to handle mixed behavior
      def handle_mixed_behavior():
          coop_count = opponent.history[-10:].count(axl.Action.C)
          defect_count = opponent.history[-10:].count(axl.Action.D)
          if coop_count > defect_count:
              return axl.Action.C
          elif defect_count > coop_count:
              return axl.Action.D
          else:
              return axl.Action.C
      
      # Helper function to check for mutual defection streak
      def check_mutual_defection_streak():
          if len(self.history) < 20:
              return False
          return self.history[-20:] == [axl.Action.D] * 20 and opponent.history[-20:] == [axl.Action.D] * 20
      
      # Helper function to handle score comparison every 50 rounds
      def handle_score_comparison():
          if len(self.history) % 50 == 0:
              my_avg_score = self.score / len(self.history)
              opp_avg_score = opponent.score / len(opponent.history)
              if my_avg_score < opp_avg_score:
                  self.aggressive_mode = 5
              elif abs(my_avg_score - opp_avg_score) <= 0.5:
                  self.aggressive_mode = 0
              else:
                  self.cooperative_mode = 5
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.aggressive_mode = 0
          self.cooperative_mode = 0
          return axl.Action.C
      
      # Handle aggressive or cooperative modes
      if self.aggressive_mode > 0:
          self.aggressive_mode -= 1
          return axl.Action.D
      if self.cooperative_mode > 0:
          self.cooperative_mode -= 1
          return axl.Action.C
      
      # Handle last 20 rounds
      if len(self.history) >= 980:
          if self.score < opponent.score:
              if len(self.history) % 2 == 0:
                  return axl.Action.C
              else:
                  return axl.Action.D
      
      # Check for mutual defection streak
      if check_mutual_defection_streak():
          self.cooperative_mode = 3
          return axl.Action.C
      
      # Analyze the last 10 rounds of the opponent
      opponent_pattern = analyze_last_10_rounds()
      
      # Main strategy based on opponent's pattern
      if opponent_pattern == "cooperation":
          return axl.Action.C
      elif opponent_pattern == "defection":
          return axl.Action.D
      elif opponent_pattern == "mixed":
          return handle_mixed_behavior()
      
      # Handle score comparison every 50 rounds
      handle_score_comparison()
      
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round to encourage mutual cooperation.  2. Use a
# sliding window of the last 5 rounds to determine the opponent's behavior,
# accounting for the 10% noise:    - If the opponent cooperated in 3 or more of
# the last 5 rounds, consider them cooperative.    - Otherwise, consider them
# non-cooperative.  3. If the opponent is considered cooperative:    - Cooperate
# with 70% probability and defect with 30% probability.  4. If the opponent is
# considered non-cooperative:    - Defect with 70% probability and cooperate
# with 30% probability.  5. Every 100 rounds, reassess your overall strategy:
# - If your score is within 10% of your opponent's, maintain the current
# strategy.    - If you're behind by more than 10%, increase defection
# probability by 10% for the next 100 rounds.    - If you're ahead by more than
# 10%, decrease defection probability by 10% for the next 100 rounds.  6. In the
# last 50 rounds, gradually increase defection probability:    - Rounds 951-975:
# Increase defection probability by 5%    - Rounds 976-1000: Increase defection
# probability by another 5%  7. If the opponent has cooperated for 10
# consecutive rounds (accounting for possible noise), cooperate for the next 2
# rounds before returning to the main strategy.  8. If you defect and the
# opponent cooperates twice in a row, cooperate once to test for a forgiving
# strategy.  9. Maintain a running average of your points per round. If this
# average decreases over 50 rounds, slightly increase your defection probability
# (by 5%) for the next 50 rounds.  10. If you notice a clear pattern in the
# opponent's play (e.g., alternating C and D), adjust your strategy to exploit
# it for 10 rounds, then return to the main strategy.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.3  # Initial defection probability
          self.cooperation_streak = 0  # Track opponent's cooperation streak
          self.last_50_scores = []  # Track scores over the last 50 rounds
          self.rounds_since_last_adjustment = 0  # Track rounds since last adjustment
          return axl.Action.C  # Start by cooperating
  
      # Helper function to determine if opponent is cooperative in the last 5 rounds
      def is_opponent_cooperative():
          last_5 = opponent.history[-5:]
          return last_5.count(axl.Action.C) >= 3
  
      # Helper function to adjust defection probability every 100 rounds
      def adjust_defection_probability():
          if len(self.history) % 100 == 0:
              if self.score < opponent.score * 0.9:
                  self.defection_probability = min(1.0, self.defection_probability + 0.1)
              elif self.score > opponent.score * 1.1:
                  self.defection_probability = max(0.0, self.defection_probability - 0.1)
  
      # Helper function to increase defection probability in the last 50 rounds
      def adjust_for_endgame():
          if len(self.history) >= 951:
              if len(self.history) <= 975:
                  self.defection_probability = min(1.0, self.defection_probability + 0.05)
              elif len(self.history) <= 1000:
                  self.defection_probability = min(1.0, self.defection_probability + 0.05)
  
      # Helper function to adjust based on recent score trends
      def adjust_based_on_recent_scores():
          if len(self.history) >= 50:
              recent_scores = self.total_scores(self.history[-50:], opponent.history[-50:])
              self.last_50_scores.append(recent_scores[0])
              if len(self.last_50_scores) > 50:
                  self.last_50_scores.pop(0)
              if len(self.last_50_scores) == 50:
                  avg_recent_score = sum(self.last_50_scores) / 50
                  if avg_recent_score < sum(self.last_50_scores[-50:]) / 50:
                      self.defection_probability = min(1.0, self.defection_probability + 0.05)
  
      # Helper function to detect opponent's forgiving strategy
      def detect_forgiving_strategy():
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
              return axl.Action.C
          return None
  
      # Helper function to detect opponent's cooperation streak
      def detect_cooperation_streak():
          if opponent.history[-10:].count(axl.Action.C) == 10:
              self.cooperation_streak = 2
          if self.cooperation_streak > 0:
              self.cooperation_streak -= 1
              return axl.Action.C
          return None
  
      # Adjust defection probability every 100 rounds
      adjust_defection_probability()
  
      # Adjust for endgame defection increase
      adjust_for_endgame()
  
      # Adjust based on recent score trends
      adjust_based_on_recent_scores()
  
      # Detect forgiving strategy
      forgiving_action = detect_forgiving_strategy()
      if forgiving_action:
          return forgiving_action
  
      # Detect cooperation streak
      cooperation_streak_action = detect_cooperation_streak()
      if cooperation_streak_action:
          return cooperation_streak_action
  
      # Determine opponent's behavior in the last 5 rounds
      if is_opponent_cooperative():
          return self._random.random_choice(0.7)  # Cooperate with 70% probability
      else:
          return self._random.random_choice(1 - self.defection_probability)  # Defect with adjusted probability



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 5 rounds,
# forgive any defection and play C regardless of the opponent's recent moves.
# 4. If the opponent has defected more than 40% of the time in the last 20
# rounds, switch to playing D for the next 5 rounds before returning to the main
# strategy.  5. In the last 20 rounds of the game, mirror the opponent's last
# move.  6. If your score falls more than 50 points behind your opponent's at
# any point, switch to playing D for the next 10 rounds before returning to the
# main strategy.  7. Implement a "noise filter": If a single D is surrounded by
# Cs (i.e., C-D-C pattern), treat it as a C when deciding your next move.  8.
# Every 50 rounds, analyze the opponent's pattern of play. If they seem to be
# using a similar cooperative strategy, play C for the next 5 rounds to
# encourage mutual cooperation.  9. If the opponent has played C for the last 10
# consecutive rounds, play C for the next 5 rounds regardless of other
# conditions to reinforce cooperation.  10. Adjust your strategy if the opponent
# seems to be exploiting any predictable patterns in your play.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are defecting
          self.coop_streak = 0    # Track how many rounds we are cooperating
          self.analyze_round = 50  # Next round to analyze opponent's pattern
          return axl.Action.C
  
      # Helper function to check if a D is surrounded by Cs (C-D-C pattern)
      def is_noise_filter_active():
          if len(opponent.history) < 3:
              return False
          return (opponent.history[-3] == axl.Action.C and
                  opponent.history[-2] == axl.Action.D and
                  opponent.history[-1] == axl.Action.C)
  
      # Helper function to count defections in the last N rounds
      def count_defections(history, N):
          return history[-N:].count(axl.Action.D)
  
      # Helper function to count cooperations in the last N rounds
      def count_cooperations(history, N):
          return history[-N:].count(axl.Action.C)
  
      # Rule 6: If we are more than 50 points behind, defect for 10 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
      if len(self.history) > 1:
          if opponent.score - self.score > 50:
              self.defect_streak = 9  # Defect for the next 10 rounds
              return axl.Action.D
  
      # Rule 5: In the last 20 rounds, mirror the opponent's last move
      if len(self.history) >= 980:
          return opponent.history[-1]
  
      # Rule 4: If opponent defected more than 40% in the last 20 rounds, defect for 5 rounds
      if len(opponent.history) >= 20 and count_defections(opponent.history, 20) > 8:
          self.defect_streak = 4  # Defect for the next 5 rounds
          return axl.Action.D
  
      # Rule 3: Every 5 rounds, forgive and play C
      if len(self.history) % 5 == 0:
          return axl.Action.C
  
      # Rule 2: Play C if opponent played C in at least 2 of the last 3 rounds, else D
      if len(opponent.history) >= 3:
          if is_noise_filter_active():
              return axl.Action.C
          if count_cooperations(opponent.history, 3) >= 2:
              return axl.Action.C
          if count_defections(opponent.history, 3) >= 2:
              return axl.Action.D
  
      # Rule 9: If opponent has played C for the last 10 rounds, cooperate for 5 rounds
      if len(opponent.history) >= 10 and count_cooperations(opponent.history, 10) == 10:
          self.coop_streak = 5
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Rule 8: Every 50 rounds, analyze opponent's pattern and cooperate for 5 rounds if they seem cooperative
      if len(self.history) == self.analyze_round:
          if count_cooperations(opponent.history, 50) > 40:  # More than 80% cooperation
              self.coop_streak = 5
          self.analyze_round += 50
  
      # Default to cooperation if no other rule applies
      return axl.Action.C



# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent seemed to
# cooperate in at least 2 of the last 3 rounds, cooperate.    - Otherwise,
# defect.  3. Every 5 rounds, regardless of the opponent's recent actions:    -
# If your total score is higher than or equal to your opponent's, cooperate.
# - If your total score is lower than your opponent's, defect.  4. If you've
# defected for 3 consecutive rounds, cooperate in the next round to test for
# reconciliation.  5. In the last 20 rounds of the game:    - If the opponent
# has cooperated in more than 60% of the previous 50 rounds, cooperate.    -
# Otherwise, defect.  6. If at any point your score falls behind your opponent's
# by 15 points or more:    - Defect for the next 3 rounds.    - Then cooperate
# for 1 round to test the opponent's response before reverting to the main
# strategy.  7. Every 50 rounds, analyze the opponent's overall cooperation
# rate:    - If it's above 70%, increase your cooperation frequency by
# cooperating even if the opponent seemed to defect in 2 of the last 3 rounds.
# - If it's below 30%, decrease your cooperation frequency by defecting even if
# the opponent seemed to cooperate in 2 of the last 3 rounds.  8. To account for
# noise, consider an action as "seemed to cooperate" if the observed outcome
# matches what would happen if they cooperated, and "seemed to defect"
# otherwise.  Follow these rules in the order presented, applying the first
# applicable rule in each round.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to check if opponent seemed to cooperate
      def seemed_to_cooperate(action):
          return action == axl.Action.C
  
      # Helper function to check if opponent seemed to defect
      def seemed_to_defect(action):
          return action == axl.Action.D
  
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          self.increase_cooperation = False
          self.decrease_cooperation = False
          self.defect_streak = None
          return axl.Action.C
  
      # Rule 5: In the last 20 rounds of the game
      if len(self.history) >= 980:
          if len(self.history) >= 50:
              last_50_opponent_moves = opponent.history[-50:]
              cooperation_rate = last_50_opponent_moves.count(axl.Action.C) / 50
              if cooperation_rate > 0.6:
                  return axl.Action.C
              else:
                  return axl.Action.D
  
      # Rule 6: If score falls behind by 15 points or more
      if self.score < opponent.score - 15:
          if not self.defect_streak:
              self.defect_streak = 3
          if self.defect_streak > 0:
              self.defect_streak -= 1
              return axl.Action.D
          else:
              self.defect_streak = None
              return axl.Action.C
  
      # Rule 7: Every 50 rounds, analyze opponent's cooperation rate
      if len(self.history) % 50 == 0 and len(self.history) > 0:
          overall_cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if overall_cooperation_rate > 0.7:
              self.increase_cooperation = True
          elif overall_cooperation_rate < 0.3:
              self.decrease_cooperation = True
          else:
              self.increase_cooperation = False
              self.decrease_cooperation = False
  
      # Rule 2: If opponent seemed to cooperate in at least 2 of the last 3 rounds, cooperate
      if len(opponent.history) >= 3:
          last_3_opponent_moves = opponent.history[-3:]
          if last_3_opponent_moves.count(axl.Action.C) >= 2:
              if self.increase_cooperation:
                  return axl.Action.C
              if self.decrease_cooperation:
                  return axl.Action.D
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 3: Every 5 rounds, compare scores
      if len(self.history) % 5 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 4: If defected for 3 consecutive rounds, cooperate
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.C
  
      # Default to defect if no other rule applies
      return axl.Action.D



# Here's a revised aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. For the next 3 rounds, defect regardless
# of the opponent's actions to establish an aggressive stance.  3. From round 5
# onwards:    a. If the opponent's last 2 observed actions were both defections,
# defect.    b. If the opponent's last 2 observed actions were both
# cooperations, defect with 70% probability and cooperate with 30% probability.
# c. If the opponent's last 2 observed actions were mixed, defect.  4. Every 100
# rounds, cooperate once, but only if you're not currently behind in score.  5.
# If your score is more than 30 points behind your opponent's, always defect for
# the next 10 rounds.  6. If you're ahead by more than 50 points, cooperate for
# the next 2 rounds.  7. In the last 20 rounds, randomize your actions with a
# 90% chance to defect and 10% chance to cooperate.  8. To account for noise:
# a. Consider an action as "observed" only if it's been consistent for 2
# consecutive rounds.    b. If there's inconsistency due to potential noise,
# default to defection.  9. Reassess and return to step 3 after each round,
# continuing this process for the entire game duration.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to check if the last two actions of the opponent were consistent
      def consistent_last_two_actions():
          if len(opponent.history) < 2:
              return False
          return opponent.history[-1] == opponent.history[-2]
  
      # Helper function to check if the last two actions were both defections
      def last_two_defections():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if the last two actions were both cooperations
      def last_two_cooperations():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C
  
      # Helper function to check if the last two actions were mixed
      def last_two_mixed():
          return len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]
  
      # Step 1: First round, defect
      if self.first_round():
          self.defect_streak = 0  # Initialize a counter for defect streaks
          return axl.Action.D
  
      # Step 2: Defect for the first 4 rounds
      if len(self.history) < 4:
          return axl.Action.D
  
      # Step 5: If more than 30 points behind, defect for the next 10 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      if self.score < opponent.score - 30:
          self.defect_streak = 10
          return axl.Action.D
  
      # Step 6: If ahead by more than 50 points, cooperate for the next 2 rounds
      if self.score > opponent.score + 50:
          return axl.Action.C
  
      # Step 7: In the last 20 rounds, randomize with 90% chance to defect
      if self.match_attributes['length'] is not None and len(self.history) >= self.match_attributes['length'] - 20:
          return self._random.random_choice(0.1)
  
      # Step 4: Every 100 rounds, cooperate once if not behind in score
      if len(self.history) % 100 == 0 and self.score >= opponent.score:
          return axl.Action.C
  
      # Step 3: From round 5 onwards, follow the opponent's last two actions
      if last_two_defections():
          return axl.Action.D
      elif last_two_cooperations():
          return self._random.random_choice(0.3)
      elif last_two_mixed():
          return axl.Action.D
  
      # Step 8: Handle noise by checking for consistency in the last two actions
      if not consistent_last_two_actions():
          return axl.Action.D
  
      # Default to defection if no other condition is met
      return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 20 rounds,
# attempt to re-establish cooperation by playing C, regardless of the opponent's
# recent moves.  4. If the opponent has defected more than 40% of the time in
# the last 30 rounds, switch to playing D for the next 5 rounds before reverting
# to the main strategy.  5. Maintain the cooperative strategy throughout the
# game, including the final rounds.  6. Keep track of the cumulative score
# difference. If you're behind by more than 30 points, increase the threshold
# for cooperation to 3 C's out of the last 4 moves for the next 10 rounds.  7.
# If mutual cooperation has been established for more than 50 consecutive
# rounds, occasionally (with 10% probability) forgive a single defection without
# retaliating.  8. Adapt to highly cooperative opponents by playing C for 2
# rounds after 10 consecutive rounds of mutual cooperation, even if they defect
# once.  9. If the opponent's strategy seems to change significantly (e.g.,
# sudden shift from mostly C to mostly D), reset your assessment and treat the
# next round as if it's the start of a new game.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_threshold = 2  # Default threshold for cooperation
          self.behind_threshold = 30  # Points behind threshold
          self.behind_rounds = 0  # Track rounds when behind
          self.defect_streak = 0  # Track rounds of forced defection
          self.mutual_coop_streak = 0  # Track mutual cooperation streak
          return axl.Action.C  # Start with cooperation
  
      # Helper function to count defections in the last N rounds
      def count_defections(history, n):
          return history[-n:].count(axl.Action.D)
  
      # Helper function to count cooperations in the last N rounds
      def count_cooperations(history, n):
          return history[-n:].count(axl.Action.C)
  
      # Check if we are behind by more than 30 points
      if self.behind_rounds == 0:
          my_score, opponent_score = self.total_scores(self.history[-30:], opponent.history[-30:])
          if opponent_score - my_score > self.behind_threshold:
              self.coop_threshold = 3  # Increase cooperation threshold
              self.behind_rounds = 10  # Apply for the next 10 rounds
  
      # Decrease the behind_rounds counter if applicable
      if self.behind_rounds > 0:
          self.behind_rounds -= 1
          if self.behind_rounds == 0:
              self.coop_threshold = 2  # Reset cooperation threshold
  
      # Check if the opponent has defected more than 40% in the last 30 rounds
      if len(opponent.history) >= 30 and count_defections(opponent.history, 30) > 12:
          self.defect_streak = 5  # Force defection for the next 5 rounds
  
      # Handle forced defection streak
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Every 20 rounds, attempt to re-establish cooperation
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # Check for mutual cooperation streak
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.mutual_coop_streak += 1
      else:
          self.mutual_coop_streak = 0
  
      # Occasionally forgive a defection if mutual cooperation has been established
      if self.mutual_coop_streak > 50 and opponent.history[-1] == axl.Action.D:
          if self._random.random_choice(0.1):
              return axl.Action.C
  
      # Adapt to highly cooperative opponents
      if self.mutual_coop_streak >= 10 and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Check if the opponent has changed strategy significantly
      if len(opponent.history) >= 10 and count_defections(opponent.history[-10:], 10) >= 7:
          return axl.Action.C  # Reset assessment and cooperate
  
      # Main strategy: cooperate if opponent cooperated in at least 2 of the last 3 rounds
      if len(opponent.history) >= 3:
          if count_cooperations(opponent.history, 3) >= self.coop_threshold:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Default to cooperation if not enough history
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. In subsequent rounds:    - If the opponent
# seemed to cooperate in the previous round, cooperate.    - If the opponent
# seemed to defect in the previous round, defect.    - Consider an action as
# "seeming to cooperate" if you received a payoff of 3 or 0, and "seeming to
# defect" if you received a payoff of 5 or 1.  3. Every 5 rounds, evaluate the
# recent history:    - If your total score over the last 5 rounds is higher than
# or equal to the opponent's, cooperate.    - If your total score over the last
# 5 rounds is lower than the opponent's, defect.  4. If the opponent has seemed
# to defect for 3 consecutive rounds, defect for the next 2 rounds.  5. If you
# have defected for 5 consecutive rounds, cooperate in the next round.  6. In
# the last 50 rounds of the game, gradually increase the probability of
# defection:    - Start with a 20% chance of defection, increasing by 2% each
# round.  7. If at any point your overall score falls behind the opponent's by
# 15 points or more, defect for the next 3 rounds.  8. After implementing rule
# 7, if your score becomes higher than or equal to the opponent's, revert to the
# base strategy (rules 1-6).  9. Every 20 rounds, attempt a "cooperation test":
# - Cooperate for 2 consecutive rounds regardless of the opponent's actions.
# - If the opponent seemed to cooperate in both rounds, continue cooperating.
# - If the opponent seemed to defect in either round, revert to the base
# strategy.  10. Adjust your strategy based on the game progress:     - In
# rounds 1-333, be more forgiving: revert to cooperation after 2 rounds of
# opponent's seeming cooperation.     - In rounds 334-666, follow the base
# strategy.     - In rounds 667-1000, be less forgiving: require 3 rounds of
# opponent's seeming cooperation before reverting to cooperation.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defects = 0
          self.consecutive_opponent_defects = 0
          self.defect_for_next_n_rounds = 0
          self.cooperation_test_rounds = 0
          return axl.Action.C
  
      # Helper function to determine if the opponent "seemed to cooperate" or "seemed to defect"
      def opponent_seemed_to_cooperate(last_round_score):
          return last_round_score in [3, 0]
  
      def opponent_seemed_to_defect(last_round_score):
          return last_round_score in [5, 1]
  
      # Get the last round's score
      last_round_score, _ = self.total_scores(self.history[-1:], opponent.history[-1:])
  
      # Rule 2: Cooperate if the opponent seemed to cooperate, defect if they seemed to defect
      if opponent_seemed_to_cooperate(last_round_score):
          action = axl.Action.C
      else:
          action = axl.Action.D
  
      # Rule 4: If the opponent has seemed to defect for 3 consecutive rounds, defect for the next 2 rounds
      if opponent_seemed_to_defect(last_round_score):
          self.consecutive_opponent_defects += 1
      else:
          self.consecutive_opponent_defects = 0
  
      if self.consecutive_opponent_defects >= 3:
          self.defect_for_next_n_rounds = 2
  
      if self.defect_for_next_n_rounds > 0:
          self.defect_for_next_n_rounds -= 1
          return axl.Action.D
  
      # Rule 5: If you have defected for 5 consecutive rounds, cooperate in the next round
      if self.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.C
  
      # Rule 3: Every 5 rounds, evaluate the recent history
      if len(self.history) % 5 == 0:
          my_score, opponent_score = self.total_scores(self.history[-5:], opponent.history[-5:])
          if my_score < opponent_score:
              action = axl.Action.D
          else:
              action = axl.Action.C
  
      # Rule 7: If your overall score falls behind the opponent's by 15 points or more, defect for the next 3 rounds
      if opponent.score - self.score >= 15:
          self.defect_for_next_n_rounds = 3
  
      # Rule 6: In the last 50 rounds, gradually increase the probability of defection
      if len(self.history) >= 950:
          defect_probability = 0.2 + 0.02 * (len(self.history) - 950)
          if self._random.random_choice(defect_probability):
              return axl.Action.D
  
      # Rule 9: Every 20 rounds, attempt a "cooperation test"
      if len(self.history) % 20 == 0:
          self.cooperation_test_rounds = 2
  
      if self.cooperation_test_rounds > 0:
          self.cooperation_test_rounds -= 1
          return axl.Action.C
  
      # Rule 10: Adjust strategy based on game progress
      if len(self.history) <= 333:
          if self.consecutive_opponent_defects >= 2:
              action = axl.Action.C
      elif len(self.history) >= 667:
          if self.consecutive_opponent_defects < 3:
              action = axl.Action.C
  
      return action



# Here's a revised strategy taking into account the feedback:  1. Start by
# defecting (D) in the first round.  2. Keep a running tally of your score and
# your opponent's score, as well as a count of the current round.  3. Base your
# decisions on the opponent's actions over the last 3 rounds to mitigate the
# impact of the 10% noise:    - If the opponent defected in 2 or more of the
# last 3 rounds, defect.    - If the opponent cooperated in 2 or more of the
# last 3 rounds, cooperate with 30% probability and defect with 70% probability.
# 4. Every 100 rounds, reassess your overall strategy:    - If your score is
# within 10% of your opponent's, continue with the current strategy.    - If
# you're more than 10% behind, increase your defection probability to 90% for
# the next 50 rounds.    - If you're more than 10% ahead, increase your
# cooperation probability to 50% for the next 50 rounds.  5. In the last 50
# rounds of the game, gradually increase your defection probability:    - Rounds
# 951-975: 80% defection probability    - Rounds 976-1000: 95% defection
# probability  6. If you detect a clear pattern in your opponent's play (e.g.,
# tit-for-tat, always defect), adjust your strategy accordingly for the next 20
# rounds.  7. Every 200 rounds, introduce a random element by playing 5
# consecutive rounds with a 50/50 chance of cooperation or defection.  8. If
# mutual defection occurs for more than 10 consecutive rounds, attempt to break
# the cycle by cooperating for 2 rounds.  9. Always consider the 10% noise
# factor when interpreting your opponent's actions and when executing your own
# moves.  10. Return to the main strategy after any temporary changes.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.round_count = 0
          self.cooperation_probability = 0.3
          self.defection_probability = 0.7
          self.adjustment_rounds = 0
          self.last_adjustment = 0
          self.mutual_defection_count = 0
          return axl.Action.D  # Start by defecting
  
      # Increment round count
      self.round_count += 1
  
      # Helper function to get the opponent's last N moves
      def get_last_n_moves(n):
          return opponent.history[-n:]
  
      # Helper function to adjust probabilities based on score difference
      def adjust_probabilities():
          if self.round_count % 100 == 0:
              if self.score < 0.9 * opponent.score:
                  # More than 10% behind, increase defection probability
                  self.defection_probability = 0.9
                  self.cooperation_probability = 0.1
                  self.adjustment_rounds = 50
              elif self.score > 1.1 * opponent.score:
                  # More than 10% ahead, increase cooperation probability
                  self.defection_probability = 0.5
                  self.cooperation_probability = 0.5
                  self.adjustment_rounds = 50
              else:
                  # Within 10%, continue with current strategy
                  self.defection_probability = 0.7
                  self.cooperation_probability = 0.3
  
      # Helper function to handle the last 50 rounds
      def handle_last_50_rounds():
          if 951 <= self.round_count <= 975:
              self.defection_probability = 0.8
          elif 976 <= self.round_count <= 1000:
              self.defection_probability = 0.95
  
      # Helper function to handle random element every 200 rounds
      def random_element():
          if self.round_count % 200 == 0:
              self.adjustment_rounds = 5
              self.defection_probability = 0.5
              self.cooperation_probability = 0.5
  
      # Helper function to break mutual defection cycle
      def break_mutual_defection():
          if self.history[-10:].count(axl.Action.D) == 10 and opponent.history[-10:].count(axl.Action.D) == 10:
              self.mutual_defection_count = 2
  
      # Adjust probabilities every 100 rounds
      if self.round_count % 100 == 0:
          adjust_probabilities()
  
      # Handle random element every 200 rounds
      if self.round_count % 200 == 0:
          random_element()
  
      # Handle mutual defection cycle
      break_mutual_defection()
  
      # Handle last 50 rounds
      if self.round_count > 950:
          handle_last_50_rounds()
  
      # If in a temporary adjustment phase, decrement the adjustment counter
      if self.adjustment_rounds > 0:
          self.adjustment_rounds -= 1
  
      # If breaking mutual defection, cooperate for 2 rounds
      if self.mutual_defection_count > 0:
          self.mutual_defection_count -= 1
          return axl.Action.C
  
      # Base decision on opponent's last 3 moves
      if len(opponent.history) >= 3:
          last_3_moves = get_last_n_moves(3)
          if last_3_moves.count(axl.Action.D) >= 2:
              return axl.Action.D
          elif last_3_moves.count(axl.Action.C) >= 2:
              return self._random.random_choice(self.cooperation_probability)
  
      # Default to defect if no clear pattern
      return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 20 rounds,
# play C regardless of the opponent's recent moves to signal cooperative intent
# and potentially reset the relationship.  4. If the opponent has defected more
# than 70% of the time in the last 30 rounds, switch to playing D for the next 5
# rounds before returning to the main strategy.  5. Maintain the cooperative
# approach throughout the game, including the final rounds.  6. If your score
# falls more than 10% behind your opponent's after at least 100 rounds have been
# played, play D for the next 3 rounds before returning to the main strategy.
# 7. After any streak of 3 or more mutual defections, play C for 2 rounds to
# attempt to break the cycle and re-establish cooperation.  8. Every 50 rounds,
# analyze the opponent's pattern of play. If they seem to respond positively to
# cooperation, increase the forgiveness threshold in step 2 to 3 out of the last
# 4 rounds. If they exploit cooperation frequently, decrease it to 2 out of the
# last 4 rounds.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to count defections in the last N rounds
      def count_defections(history, n):
          return history[-n:].count(axl.Action.D)
      
      # Helper function to count cooperations in the last N rounds
      def count_cooperations(history, n):
          return history[-n:].count(axl.Action.C)
      
      # Helper function to analyze opponent's pattern every 50 rounds
      def analyze_opponent_pattern():
          if len(self.history) % 50 == 0:
              if count_cooperations(opponent.history, 50) > count_defections(opponent.history, 50):
                  self.forgiveness_threshold = 3  # More forgiving
              else:
                  self.forgiveness_threshold = 2  # Less forgiving
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.forgiveness_threshold = 2  # Start with 2 out of 3 rounds
          self.defection_streak = 0  # Track mutual defection streaks
          self.switch_to_defect = 0  # Track if we are in a forced defection period
          return axl.Action.C  # Start with cooperation
      
      # Analyze opponent's pattern every 50 rounds
      analyze_opponent_pattern()
      
      # If we are in a forced defection period, continue defecting for the next 5 rounds
      if self.switch_to_defect > 0:
          self.switch_to_defect -= 1
          return axl.Action.D
      
      # If the opponent has defected more than 70% of the time in the last 30 rounds, switch to D for 5 rounds
      if len(self.history) >= 30 and count_defections(opponent.history, 30) / 30 > 0.7:
          self.switch_to_defect = 5
          return axl.Action.D
      
      # If our score falls more than 10% behind after 100 rounds, defect for 3 rounds
      if len(self.history) >= 100:
          if self.score < 0.9 * opponent.score:
              self.switch_to_defect = 3
              return axl.Action.D
      
      # Check for mutual defection streaks
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D] * 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          self.defection_streak = 2  # Play C for 2 rounds to break the cycle
          return axl.Action.C
      
      # If we are in a defection streak recovery period, play C for 2 rounds
      if self.defection_streak > 0:
          self.defection_streak -= 1
          return axl.Action.C
      
      # Every 20 rounds, play C to signal cooperation
      if len(self.history) % 20 == 0:
          return axl.Action.C
      
      # Main strategy: Play C if opponent played C in at least 2 of the last 3 rounds, otherwise play D
      if len(opponent.history) >= 3:
          if count_cooperations(opponent.history, 3) >= self.forgiveness_threshold:
              return axl.Action.C
          else:
              return axl.Action.D
      else:
          return axl.Action.C  # Default to cooperation if not enough history



# Here's a revised strategy for the iterated game:  1. Start by cooperating for
# the first 5 rounds.  2. For rounds 6-10, cooperate if the opponent has
# cooperated more than they've defected; otherwise, defect.  3. From round 11
# onwards:    - If the opponent has cooperated in at least 2 of the last 3
# rounds, cooperate.    - If the opponent has defected in at least 2 of the last
# 3 rounds, defect.    - If the opponent's actions have been mixed in the last 3
# rounds:      a. Calculate the opponent's cooperation rate over the last 10
# rounds.      b. If their cooperation rate is 55% or higher, cooperate.      c.
# If their cooperation rate is below 55%, defect.      d. In case of a 50-50
# split, cooperate.  4. Every 100 rounds, regardless of the opponent's recent
# actions:    - Cooperate for one round to test if the opponent is willing to
# reciprocate cooperation.  5. When interpreting the opponent's actions,
# consider the 10% noise factor:    - If an opponent's action contradicts their
# behavior in the last 5 rounds, assume it was due to noise and respond based on
# their previous pattern.  6. Adapt the strategy based on cumulative score:    -
# Every 50 rounds, compare your total score to the maximum possible score (3
# points per round).    - If your score is less than 60% of the maximum, become
# more inclined to defect by lowering the cooperation threshold to 50% for the
# next 50 rounds.    - If your score is more than 80% of the maximum, become
# more inclined to cooperate by raising the cooperation threshold to 60% for the
# next 50 rounds.  7. For the last 20 rounds of the game:    - If the opponent's
# cooperation rate in the last 50 rounds is 70% or higher, continue with the
# main strategy.    - Otherwise, always defect.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if N == 0:
              return 0
          return history[-N:].count(axl.Action.C) / N
  
      # Helper function to check if an action is noise based on the last 5 rounds
      def is_noise(action, history, N=5):
          if len(history) < N:
              return False
          return action != max(set(history[-N:]), key=history[-N:].count)
  
      # Round number
      round_number = len(self.history) + 1
  
      # Step 1: Cooperate for the first 5 rounds
      if round_number <= 5:
          return axl.Action.C
  
      # Step 2: For rounds 6-10, cooperate if opponent cooperated more than defected
      if 6 <= round_number <= 10:
          if opponent.history.cooperations > opponent.history.defections:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 3: From round 11 onwards
      if round_number >= 11:
          # Check the last 3 rounds
          last_3 = opponent.history[-3:]
          if last_3.count(axl.Action.C) >= 2:
              return axl.Action.C
          elif last_3.count(axl.Action.D) >= 2:
              return axl.Action.D
          else:
              # Mixed actions, calculate cooperation rate over the last 10 rounds
              coop_rate = cooperation_rate(opponent.history, 10)
              if coop_rate > 0.55:
                  return axl.Action.C
              elif coop_rate < 0.55:
                  return axl.Action.D
              else:
                  return axl.Action.C
  
      # Step 4: Every 100 rounds, cooperate to test opponent's willingness to reciprocate
      if round_number % 100 == 0:
          return axl.Action.C
  
      # Step 5: Handle noise by checking if the opponent's last action contradicts their recent behavior
      if is_noise(opponent.history[-1], opponent.history):
          # Respond based on the previous pattern (ignore the last action)
          if opponent.history[-2] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 6: Adapt strategy based on cumulative score every 50 rounds
      if round_number % 50 == 0:
          max_possible_score = round_number * 3
          if self.score < 0.6 * max_possible_score:
              # Lower cooperation threshold to 50%
              if cooperation_rate(opponent.history, 10) >= 0.50:
                  return axl.Action.C
              else:
                  return axl.Action.D
          elif self.score > 0.8 * max_possible_score:
              # Raise cooperation threshold to 60%
              if cooperation_rate(opponent.history, 10) >= 0.60:
                  return axl.Action.C
              else:
                  return axl.Action.D
  
      # Step 7: For the last 20 rounds, always defect if opponent's cooperation rate is below 70%
      if round_number > 980:
          if cooperation_rate(opponent.history, 50) < 0.70:
              return axl.Action.D
  
      # Default action if no other condition is met
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent's last observed action
# was defection, defect with 90% probability and cooperate with 10% probability.
# 3. If the opponent's last observed action was cooperation, cooperate with 70%
# probability and defect with 30% probability.  4. Keep track of the opponent's
# cooperation rate over the last 20 rounds. If it exceeds 80%, increase your
# cooperation probability by 10% for the next 5 rounds.  5. If your score falls
# more than 30 points behind your opponent's, increase your defection
# probability by 20% for the next 10 rounds.  6. In the last 20 rounds, base
# your decision on the opponent's overall cooperation rate throughout the game:
# - If their cooperation rate is above 70%, cooperate.    - If it's between 40%
# and 70%, use the probabilities from rules 2 and 3.    - If it's below 40%,
# always defect.  7. Every 100 rounds, reassess your strategy:    - If your
# score is higher, maintain the current approach.    - If your score is lower,
# slightly increase your defection probability in rules 2 and 3 by 5%.  8. To
# account for noise, consider an action as "consistent" only if it has been
# observed at least twice in the last three rounds.  9. If the opponent has
# shown a clear pattern (e.g., alternating C and D) for more than 10 rounds,
# attempt to exploit it by choosing the optimal response to their predicted next
# move.  Follow these rules in the order presented, applying the first
# applicable rule in each round.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_boost_rounds = 0
          self.defection_boost_rounds = 0
          self.last_reassessment_round = 0
          self.cooperation_rate_last_20 = 0
          self.defection_prob_increase = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Helper function to detect alternating pattern
      def detect_alternating_pattern(history, N):
          if len(history) < N:
              return False
          return all(history[i] != history[i + 1] for i in range(-N, -1))
  
      # Rule 8: Check for consistent actions in the last 3 rounds
      if len(opponent.history) >= 3:
          last_three = opponent.history[-3:]
          if last_three.count(last_three[-1]) >= 2:
              last_opponent_action = last_three[-1]
          else:
              last_opponent_action = opponent.history[-1]
      else:
          last_opponent_action = opponent.history[-1]
  
      # Rule 9: Exploit alternating pattern if detected
      if detect_alternating_pattern(opponent.history, 10):
          predicted_next_move = axl.Action.C if opponent.history[-1] == axl.Action.D else axl.Action.D
          return axl.Action.D if predicted_next_move == axl.Action.C else axl.Action.C
  
      # Rule 4: Track cooperation rate over the last 20 rounds
      coop_rate_last_20 = cooperation_rate(opponent.history, 20)
      if coop_rate_last_20 > 0.8:
          self.cooperation_boost_rounds = 5
  
      # Rule 5: Check if score is more than 30 points behind
      if self.score < opponent.score - 30:
          self.defection_boost_rounds = 10
  
      # Rule 7: Reassess strategy every 100 rounds
      if len(self.history) % 100 == 0 and len(self.history) != self.last_reassessment_round:
          self.last_reassessment_round = len(self.history)
          if self.score < opponent.score:
              self.defection_prob_increase += 0.05
  
      # Rule 6: Special behavior in the last 20 rounds
      if len(self.history) >= 980:
          overall_coop_rate = cooperation_rate(opponent.history, len(opponent.history))
          if overall_coop_rate > 0.7:
              return axl.Action.C
          elif overall_coop_rate < 0.4:
              return axl.Action.D
  
      # Rule 2 and 3: Adjust probabilities based on opponent's last action
      if last_opponent_action == axl.Action.D:
          defect_prob = 0.9 + self.defection_prob_increase
          if self.defection_boost_rounds > 0:
              defect_prob += 0.2
              self.defection_boost_rounds -= 1
          return self._random.random_choice(1 - defect_prob)
      else:
          coop_prob = 0.7 + self.defection_prob_increase
          if self.cooperation_boost_rounds > 0:
              coop_prob += 0.1
              self.cooperation_boost_rounds -= 1
          return self._random.random_choice(coop_prob)



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. For subsequent rounds:    - If
# the opponent has cooperated in at least 3 of the last 5 rounds, play Cooperate
# (C).    - Otherwise, play Defect (D).  3. To account for noise, ignore single
# deviations from an established pattern. If an opponent has cooperated for 5+
# rounds and then defects once, still play Cooperate (C) in the next round.  4.
# Every 20 rounds, assess the overall cooperation rate of your opponent:    - If
# they've cooperated in more than 60% of all rounds, play Cooperate (C) for the
# next round to reinforce cooperation.    - If they've cooperated in less than
# 40% of all rounds, play Defect (D) for the next 3 rounds.  5. If your score
# falls below 50% of the theoretical maximum score (1.5 points per round) at any
# point after round 200, become more cautious:    - Require 4 out of the last 5
# rounds to be cooperative before you cooperate.    - Reassess every 50 rounds
# to see if you can return to the main strategy.  6. In the last 50 rounds, base
# your decision on the opponent's overall behavior:    - If they've cooperated
# in more than 70% of all rounds, always play Cooperate (C).    - Otherwise,
# mirror their most frequent action in the last 20 rounds.  7. If the opponent
# defects for 7 consecutive rounds (accounting for possible noise), switch to
# playing Defect (D) for the next 5 rounds before returning to the main
# strategy.  8. Throughout the game, keep track of successful cooperation
# streaks. After each streak of 10+ mutual cooperations, become slightly more
# forgiving by temporarily (for the next 5 rounds) requiring only 2 out of the
# last 5 rounds to be cooperative for you to cooperate.  9. Adjust your strategy
# every 100 rounds based on your relative score:    - If you're more than 10%
# behind the theoretical maximum, become more defensive by using the cautious
# approach from point 5.    - If you're within 5% of the theoretical maximum,
# become more cooperative by using the forgiving approach from point 8.  10. In
# the first 10 rounds, be more forgiving to establish cooperation: only defect
# if the opponent has defected in 3 or more of the rounds played so far.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      MAX_SCORE_PER_ROUND = 1.5
      TOTAL_ROUNDS = 1000
      NOISE_THRESHOLD = 7
      FORGIVING_THRESHOLD = 10
      CAUTIOUS_THRESHOLD = 50
      COOPERATION_RATE_THRESHOLD = 0.6
      DEFECT_RATE_THRESHOLD = 0.4
      FINAL_ROUNDS_THRESHOLD = 50
      FINAL_ROUNDS_COOP_THRESHOLD = 0.7
      DEFECT_STREAK_THRESHOLD = 7
      DEFECT_PENALTY_ROUNDS = 5
      REASSESS_ROUNDS = 20
      SCORE_REASSESS_ROUNDS = 100
      CAUTIOUS_ROUNDS = 200
      COOP_REINFORCE_ROUNDS = 3
  
      # Helper functions
      def last_n_cooperations(n):
          return opponent.history[-n:].count(COOPERATE)
  
      def last_n_defections(n):
          return opponent.history[-n:].count(DEFECT)
  
      def cooperation_rate():
          return opponent.history.cooperations / len(opponent.history)
  
      def score_rate():
          return self.score / (len(self.history) * MAX_SCORE_PER_ROUND)
  
      def is_final_phase():
          return len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS_THRESHOLD
  
      def is_cautious_phase():
          return len(self.history) >= CAUTIOUS_ROUNDS and score_rate() < 0.5
  
      def reassess_every_n_rounds(n):
          return len(self.history) % n == 0
  
      # Initialization
      if self.first_round():
          self.defect_streak = 0
          self.forgiving_mode = False
          self.cautious_mode = False
          return COOPERATE
  
      # Track defect streaks
      if opponent.history[-1] == DEFECT:
          self.defect_streak += 1
      else:
          self.defect_streak = 0
  
      # Handle defect streaks
      if self.defect_streak >= DEFECT_STREAK_THRESHOLD:
          if self.defect_streak < DEFECT_STREAK_THRESHOLD + DEFECT_PENALTY_ROUNDS:
              return DEFECT
          else:
              self.defect_streak = 0
  
      # Final phase strategy
      if is_final_phase():
          if cooperation_rate() > FINAL_ROUNDS_COOP_THRESHOLD:
              return COOPERATE
          else:
              return opponent.history[-1]
  
      # Reassess every 20 rounds
      if reassess_every_n_rounds(REASSESS_ROUNDS):
          if cooperation_rate() > COOPERATION_RATE_THRESHOLD:
              return COOPERATE
          elif cooperation_rate() < DEFECT_RATE_THRESHOLD:
              return DEFECT
  
      # Cautious mode after round 200
      if is_cautious_phase():
          if last_n_cooperations(5) >= 4:
              return COOPERATE
          else:
              return DEFECT
  
      # Forgiving mode after 10+ mutual cooperations
      if self.forgiving_mode:
          if last_n_cooperations(5) >= 2:
              return COOPERATE
          else:
              return DEFECT
  
      # Main strategy
      if last_n_cooperations(5) >= 3:
          return COOPERATE
      else:
          return DEFECT



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent's action in the previous round appeared to be cooperation, cooperate.
# - If the opponent's action in the previous round appeared to be defection,
# defect.    - Remember that there's a 10% chance the observed action was not
# the intended action.  3. Every 10 rounds:    - If your total score is higher
# than or equal to the opponent's, cooperate.    - If your total score is lower
# than the opponent's, defect.    - This decision overrides the usual response
# for one round only.  4. If the opponent has appeared to defect for 3
# consecutive rounds, defect for the next 2 rounds.  5. If you and your opponent
# have both appeared to cooperate for 5 consecutive rounds, continue cooperating
# until the opponent appears to defect.  6. In the last 50 rounds of the game:
# - If the opponent has cooperated in at least 70% of the last 20 rounds,
# cooperate.    - Otherwise, defect.  7. If at any point your score falls behind
# the opponent's by 20 points or more:    - Defect for the next 3 rounds.    -
# Then, if the opponent cooperated in at least 2 of those 3 rounds, switch back
# to cooperation.  8. To break out of mutual defection cycles:    - If there
# have been 5 consecutive rounds of mutual defection, cooperate for 1 round.  9.
# Adjust your strategy based on the opponent's overall behavior:    - Every 100
# rounds, calculate the opponent's cooperation rate.    - If it's above 70%,
# increase your tendency to cooperate by following rule 2 only 80% of the time
# and cooperating the other 20%.    - If it's below 30%, decrease your tendency
# to cooperate by following rule 2 only 80% of the time and defecting the other
# 20%.  10. In case of conflicts between rules, prioritize them in the order
# listed here.  11. Return to step 2 and repeat until the game ends.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.defect_streak = 0
          self.cooperate_streak = 0
          self.behind_by_20 = False
          self.behind_by_20_rounds = 0
          self.mutual_defection_streak = 0
          self.adjusted_cooperation = False
          return axl.Action.C  # Start by cooperating
  
      # Helper function to check if the opponent's action was likely cooperation
      def likely_cooperation(action):
          return action == axl.Action.C or self._random.random_choice(0.1)
  
      # Helper function to check if the opponent's action was likely defection
      def likely_defection(action):
          return action == axl.Action.D or self._random.random_choice(0.1)
  
      # Rule 7: If behind by 20 points or more, defect for 3 rounds
      if self.behind_by_20:
          self.behind_by_20_rounds += 1
          if self.behind_by_20_rounds <= 3:
              if opponent.history[-1] == axl.Action.C:
                  self.behind_by_20_rounds = 0
                  self.behind_by_20 = False
              return axl.Action.D
          else:
              self.behind_by_20 = False
  
      # Rule 4: If opponent defected 3 consecutive rounds, defect for 2 rounds
      if self.consecutive_defections >= 3:
          self.defect_streak += 1
          if self.defect_streak <= 2:
              return axl.Action.D
          else:
              self.consecutive_defections = 0
              self.defect_streak = 0
  
      # Rule 5: If both cooperated for 5 consecutive rounds, continue cooperating
      if self.consecutive_cooperations >= 5:
          if likely_defection(opponent.history[-1]):
              self.consecutive_cooperations = 0
          else:
              return axl.Action.C
  
      # Rule 6: In the last 50 rounds, check cooperation rate in the last 20 rounds
      if len(self.history) >= 950:
          last_20_cooperations = opponent.history[-20:].count(axl.Action.C)
          if last_20_cooperations / 20 >= 0.7:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 8: Break out of mutual defection cycles
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.mutual_defection_streak += 1
          if self.mutual_defection_streak >= 5:
              self.mutual_defection_streak = 0
              return axl.Action.C
      else:
          self.mutual_defection_streak = 0
  
      # Rule 9: Adjust strategy based on opponent's cooperation rate every 100 rounds
      if len(self.history) % 100 == 0:
          cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if cooperation_rate > 0.7:
              self.adjusted_cooperation = True
          elif cooperation_rate < 0.3:
              self.adjusted_cooperation = False
  
      # Rule 2: Default behavior based on opponent's last action
      if likely_cooperation(opponent.history[-1]):
          action = axl.Action.C
      else:
          action = axl.Action.D
  
      # Apply adjustment from Rule 9
      if self.adjusted_cooperation:
          if self._random.random_choice(0.2):
              action = axl.Action.C
      else:
          if self._random.random_choice(0.2):
              action = axl.Action.D
  
      # Rule 3: Every 10 rounds, compare scores
      if len(self.history) % 10 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Update streaks for Rule 4 and Rule 5
      if likely_defection(opponent.history[-1]):
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
      else:
          self.consecutive_cooperations += 1
          self.consecutive_defections = 0
  
      # Rule 7: Check if behind by 20 points
      if opponent.score - self.score >= 20:
          self.behind_by_20 = True
          self.behind_by_20_rounds = 0
  
      return action



# Here's a revised aggressive strategy for the iterated normal-form game:  1.
# Start by defecting (D) in the first round.  2. If the opponent's action in the
# previous round appeared to be defection, defect in the next round. Consider an
# action as "apparent defection" if it resulted in a payoff of 0 or 1 for you.
# 3. If the opponent's action in the previous round appeared to be cooperation,
# defect with 90% probability and cooperate with 10% probability in the next
# round.  4. If you've defected for 8 consecutive rounds, cooperate in the next
# round to test the opponent's response.  5. If the opponent has apparently
# cooperated for 4 consecutive rounds, switch to cooperating for the next round
# to potentially establish a cooperative streak.  6. In the last 50 rounds of
# the game, always defect regardless of the opponent's actions.  7. If your
# overall score falls behind the opponent's by more than 30 points, increase the
# defection probability to 95% for the next 20 rounds.  8. Every 100 rounds,
# cooperate once to probe for any changes in the opponent's strategy.  9. If
# mutual defection has occurred for 10 consecutive rounds, cooperate with 20%
# probability in the next round to potentially break the deadlock.  10. Reset to
# the base strategy after any deviation from steps 4-9.  11. Throughout the
# game, keep track of the opponent's apparent strategy and adjust your defection
# probability accordingly: increase it if they seem more cooperative, decrease
# it slightly if they seem consistently aggressive.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.defection_probability = 1.0  # Start by defecting
          self.defection_streak = 0
          self.cooperation_probe_round = 0
          self.behind_by_30_rounds = 0
          return axl.Action.D
  
      # Helper function to determine if the opponent's last action was apparent defection
      def apparent_defection():
          last_round_scores = self.total_scores(self.history[-1:], opponent.history[-1:])
          return last_round_scores[0] in [0, 1]
  
      # Helper function to adjust defection probability based on opponent's apparent strategy
      def adjust_defection_probability():
          if opponent.history[-1] == axl.Action.C:
              self.defection_probability = max(0.1, self.defection_probability - 0.05)
          else:
              self.defection_probability = min(1.0, self.defection_probability + 0.05)
  
      # Step 6: Always defect in the last 50 rounds
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Step 2: If opponent's last action was apparent defection, defect
      if apparent_defection():
          self.consecutive_cooperations = 0
          self.consecutive_defections += 1
          return axl.Action.D
  
      # Step 3: If opponent's last action was apparent cooperation, defect with 90% probability
      if not apparent_defection():
          self.consecutive_defections = 0
          self.consecutive_cooperations += 1
          if self._random.random_choice(0.1):
              return axl.Action.C
          return axl.Action.D
  
      # Step 4: If defected for 8 consecutive rounds, cooperate to test opponent
      if self.consecutive_defections >= 8:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Step 5: If opponent cooperated for 4 consecutive rounds, cooperate
      if self.consecutive_cooperations >= 4:
          self.consecutive_cooperations = 0
          return axl.Action.C
  
      # Step 7: If behind by more than 30 points, increase defection probability to 95% for 20 rounds
      if self.score < opponent.score - 30:
          self.behind_by_30_rounds = 20
      if self.behind_by_30_rounds > 0:
          self.behind_by_30_rounds -= 1
          if self._random.random_choice(0.05):
              return axl.Action.C
          return axl.Action.D
  
      # Step 8: Every 100 rounds, cooperate once to probe
      if len(self.history) % 100 == 0:
          return axl.Action.C
  
      # Step 9: If mutual defection for 10 consecutive rounds, cooperate with 20% probability
      if self.history[-10:].count(axl.Action.D) == 10 and opponent.history[-10:].count(axl.Action.D) == 10:
          if self._random.random_choice(0.2):
              return axl.Action.C
          return axl.Action.D
  
      # Step 10: Reset to base strategy after any deviation from steps 4-9
      adjust_defection_probability()
  
      # Default action based on defection probability
      if self._random.random_choice(self.defection_probability):
          return axl.Action.D
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. In subsequent rounds:    - If
# the opponent's action in the previous round appeared to be Cooperate (C), play
# Cooperate (C).    - If the opponent's action appeared to be Defect (D), play
# Defect (D) for the next round, then return to Cooperate (C).  3. Keep a
# rolling count of the opponent's apparent defections in the last 30 rounds. If
# this exceeds 40%, play Defect (D) for the next 5 rounds before attempting to
# reset cooperation.  4. Every 25 rounds, if not already cooperating, play
# Cooperate (C) to attempt to reset a cycle of mutual defection.  5. To account
# for noise:    - If you receive a payoff of 0 or 1 when you played Cooperate
# (C), don't immediately retaliate. Only respond as if the opponent defected if
# it happens twice in a row.    - If you receive a payoff of 3 when you played
# Defect (D), consider it as if the opponent cooperated.  6. Adapt to opponent
# types:    - If the opponent has cooperated more than 90% of the time in the
# last 50 rounds, always play Cooperate (C).    - If the opponent has defected
# more than 90% of the time in the last 50 rounds, always play Defect (D).  7.
# In the last 20 rounds:    - If your cumulative score is higher than what you'd
# expect from mutual cooperation (3 * number of rounds played), continue with
# the main strategy.    - If your score is lower, play Defect (D) to protect
# against end-game exploitation.  8. Throughout the game, if there have been 10
# consecutive rounds of mutual defection, play Cooperate (C) for 2 rounds to
# attempt to break the cycle.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0  # Track consecutive defections
          self.opponent_defections = 0  # Track opponent defections in the last 30 rounds
          self.retaliation_mode = False  # Track if we are in retaliation mode
          self.retaliation_count = 0  # Track how many rounds of retaliation are left
          self.mutual_defection_count = 0  # Track mutual defection streak
          return axl.Action.C  # Start with Cooperate
  
      # Helper function to count defections in the last N rounds
      def count_defections(history, n):
          return history[-n:].count(axl.Action.D)
  
      # Update opponent defections in the last 30 rounds
      if len(opponent.history) >= 30:
          self.opponent_defections = count_defections(opponent.history, 30)
  
      # Check if opponent has defected more than 40% in the last 30 rounds
      if len(opponent.history) >= 30 and self.opponent_defections / 30 > 0.4:
          self.retaliation_mode = True
          self.retaliation_count = 5
  
      # Check if opponent has cooperated more than 90% in the last 50 rounds
      if len(opponent.history) >= 50 and count_defections(opponent.history, 50) / 50 < 0.1:
          return axl.Action.C
  
      # Check if opponent has defected more than 90% in the last 50 rounds
      if len(opponent.history) >= 50 and count_defections(opponent.history, 50) / 50 > 0.9:
          return axl.Action.D
  
      # Handle retaliation mode
      if self.retaliation_mode:
          if self.retaliation_count > 0:
              self.retaliation_count -= 1
              if self.retaliation_count == 0:
                  self.retaliation_mode = False
              return axl.Action.D
          else:
              self.retaliation_mode = False
  
      # Handle mutual defection streak
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.mutual_defection_count += 1
      else:
          self.mutual_defection_count = 0
  
      if self.mutual_defection_count >= 10:
          self.mutual_defection_count = 0
          return axl.Action.C
  
      # Handle noise: if we cooperated and got a low payoff, don't retaliate immediately
      if len(self.history) > 1:
          last_round_score, _ = self.total_scores(self.history[-1:], opponent.history[-1:])
          second_last_round_score, _ = self.total_scores(self.history[-2:-1], opponent.history[-2:-1])
  
          if self.history[-1] == axl.Action.C and last_round_score <= 1:
              if self.history[-2] == axl.Action.C and second_last_round_score <= 1:
                  return axl.Action.D  # Retaliate after two low-payoff cooperations
              else:
                  return axl.Action.C  # Forgive the first low-payoff cooperation
  
      # Handle end-game strategy
      if len(self.history) >= 980:
          expected_coop_score = 3 * len(self.history)
          if self.score < expected_coop_score:
              return axl.Action.D
  
      # Every 25 rounds, attempt to reset cooperation
      if len(self.history) % 25 == 0:
          return axl.Action.C
  
      # Default behavior: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C



# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent's action in
# the previous round appeared to be cooperation, cooperate.    - If the
# opponent's action appeared to be defection, defect with a 60% probability and
# cooperate with a 40% probability.  3. Every 100 rounds, cooperate regardless
# of the opponent's previous action, but don't announce or make this pattern
# predictable.  4. Keep a running average of your score per round. If your
# average score falls below 1.5 for more than 20 consecutive rounds, switch to
# always defecting for the next 5 rounds, then return to the main strategy.  5.
# In the last 20 rounds of the game, mirror the opponent's previous move (Tit-
# for-Tat).  6. Throughout the game, keep track of the opponent's apparent
# cooperation rate, accounting for possible noise. If it falls below 20% over
# the last 50 rounds, switch to always defecting until the cooperation rate
# rises above 30% again.  7. After any streak of 3 or more mutual defections,
# attempt to break the cycle by cooperating for one round.  8. Remember that
# actions are noisy: when interpreting the opponent's moves or calculating
# cooperation rates, consider that any observed action has a 10% chance of being
# the opposite of what was intended.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_rate = 0.0
          self.consecutive_low_score = 0
          self.always_defect_counter = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def calculate_cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Helper function to calculate average score per round
      def average_score():
          return self.score / len(self.history) if len(self.history) > 0 else 0
  
      # Step 4: Check if average score has been below 1.5 for more than 20 rounds
      if average_score() < 1.5:
          self.consecutive_low_score += 1
      else:
          self.consecutive_low_score = 0
  
      if self.consecutive_low_score > 20:
          self.always_defect_counter = 5
  
      # Step 5: In the last 20 rounds, mirror the opponent's previous move (Tit-for-Tat)
      if len(self.history) >= 980:
          return opponent.history[-1]
  
      # Step 6: Track opponent's cooperation rate over the last 50 rounds
      self.cooperation_rate = calculate_cooperation_rate(opponent.history, 50)
  
      if self.cooperation_rate < 0.2:
          return axl.Action.D
      elif self.cooperation_rate > 0.3:
          self.always_defect_counter = 0
  
      # Step 7: Break mutual defection streaks
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D] * 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.C
  
      # Step 3: Every 100 rounds, cooperate
      if len(self.history) % 100 == 0:
          return axl.Action.C
  
      # Step 2: Main strategy logic
      if self.always_defect_counter > 0:
          self.always_defect_counter -= 1
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return self._random.random_choice(0.4)



# Here's a revised aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. For the next 3 rounds, defect regardless
# of the opponent's actions to establish an aggressive stance.  3. From round 5
# onwards:    a. If the opponent's last two observed actions were both
# cooperation (CC), defect with 90% probability and cooperate with 10%
# probability.    b. If the opponent's last two observed actions were mixed (CD
# or DC), defect.    c. If the opponent's last two observed actions were both
# defection (DD), defect.  4. Every 100 rounds, cooperate once to probe the
# opponent's response, then immediately return to step 3.  5. If your score
# falls behind the opponent's by more than 100 points, increase the defection
# probability in step 3a to 95% for the next 50 rounds.  6. In the last 50
# rounds of the game, always defect to maximize final payoff.  7. To account for
# noise:    a. Consider an action as "observed" only if it's seen in 2 out of 3
# consecutive rounds.    b. If an opponent's action seems inconsistent with
# their recent pattern, assume it's due to noise and maintain your current
# strategy.  8. Reassess the opponent's overall cooperation rate every 100
# rounds. If it's below 10%, switch to always defecting for the next 100 rounds.
# 9. Return to step 3 and repeat until the game ends.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.9  # Default defection probability for step 3a
          self.behind_threshold = 100  # Points behind threshold for step 5
          self.behind_rounds = 0  # Counter for rounds after falling behind
          self.cooperate_probe_round = 100  # Next round to probe cooperation
          self.always_defect_round = 950  # Start always defecting in the last 50 rounds
          return axl.Action.D  # Step 1: Defect in the first round
  
      # Step 6: Always defect in the last 50 rounds
      if len(self.history) >= self.always_defect_round:
          return axl.Action.D
  
      # Step 4: Every 100 rounds, cooperate once to probe
      if len(self.history) == self.cooperate_probe_round:
          self.cooperate_probe_round += 100
          return axl.Action.C
  
      # Step 5: If behind by more than 100 points, increase defection probability
      if self.score < opponent.score - self.behind_threshold:
          self.defection_probability = 0.95
          self.behind_rounds = 50  # Increase defection probability for the next 50 rounds
  
      # Decrease the behind_rounds counter if applicable
      if self.behind_rounds > 0:
          self.behind_rounds -= 1
          if self.behind_rounds == 0:
              self.defection_probability = 0.9  # Reset defection probability after 50 rounds
  
      # Step 8: Reassess opponent's cooperation rate every 100 rounds
      if len(self.history) % 100 == 0:
          if opponent.history.cooperations / len(opponent.history) < 0.1:
              return axl.Action.D  # Switch to always defecting for the next 100 rounds
  
      # Step 2: Defect for the first 4 rounds
      if len(self.history) < 4:
          return axl.Action.D
  
      # Step 3: From round 5 onwards, analyze the opponent's last two actions
      if len(opponent.history) >= 2:
          last_two = opponent.history[-2:]
          if last_two == [axl.Action.C, axl.Action.C]:
              # Step 3a: If opponent cooperated twice, defect with 90% (or 95%) probability
              return self._random.random_choice(self.defection_probability)
          elif last_two in ([axl.Action.C, axl.Action.D], [axl.Action.D, axl.Action.C]):
              # Step 3b: If mixed actions, defect
              return axl.Action.D
          elif last_two == [axl.Action.D, axl.Action.D]:
              # Step 3c: If opponent defected twice, defect
              return axl.Action.D
  
      # Default to defect if no other condition is met
      return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Keep track of the
# overall cooperation ratio of your opponent:    - If their cooperation rate
# falls below 40%, switch to a more cautious approach:      - Play D for the
# next 3 rounds.      - Then revert to step 2.  4. To account for noise:    - If
# you observe a sudden change in the opponent's behavior that doesn't align with
# their recent pattern, assume it might be due to noise and don't change your
# strategy for that round.  5. Adapt to exploitation:    - If your score is
# consistently lower than the opponent's over the last 20 rounds, switch to
# playing D for 5 rounds before reverting to step 2.  6. For the last 50 rounds
# of the game:    - If the opponent's cooperation rate is above 60% in the last
# 100 rounds, always play C.    - Otherwise, continue with the strategy from
# steps 2-5.  7. Throughout the game:    - Continuously update the opponent's
# cooperation rate.    - Reset any count of consecutive plays after observing a
# different action.  8. If the opponent's behavior doesn't fit any described
# scenario, default to step 2 based on their recent actions.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cautious_mode = False
          self.cautious_counter = 0
          self.exploit_mode = False
          self.exploit_counter = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate
      def cooperation_rate(history):
          return history.count(axl.Action.C) / len(history) if len(history) > 0 else 0
  
      # Helper function to check if opponent played C in at least 2 of the last 3 rounds
      def opponent_cooperated_recently():
          return opponent.history[-3:].count(axl.Action.C) >= 2
  
      # Helper function to check if opponent played D in at least 2 of the last 3 rounds
      def opponent_defected_recently():
          return opponent.history[-3:].count(axl.Action.D) >= 2
  
      # Update opponent's cooperation rate
      opponent_coop_rate = cooperation_rate(opponent.history[:])
  
      # Step 3: If cooperation rate falls below 40%, enter cautious mode
      if opponent_coop_rate < 0.4 and not self.cautious_mode:
          self.cautious_mode = True
          self.cautious_counter = 3
  
      # Step 5: If being exploited, enter exploit mode
      if len(self.history) >= 20:
          my_score, opponent_score = self.total_scores(self.history[-20:], opponent.history[-20:])
          if my_score < opponent_score and not self.exploit_mode:
              self.exploit_mode = True
              self.exploit_counter = 5
  
      # Step 6: For the last 50 rounds, adjust strategy based on cooperation rate
      if len(self.history) >= 950:
          if cooperation_rate(opponent.history[-100:]) > 0.6:
              return axl.Action.C
          # Otherwise, continue with the normal strategy
  
      # Handle cautious mode
      if self.cautious_mode:
          self.cautious_counter -= 1
          if self.cautious_counter == 0:
              self.cautious_mode = False
          return axl.Action.D
  
      # Handle exploit mode
      if self.exploit_mode:
          self.exploit_counter -= 1
          if self.exploit_counter == 0:
              self.exploit_mode = False
          return axl.Action.D
  
      # Step 2: Default strategy based on recent opponent actions
      if opponent_cooperated_recently():
          return axl.Action.C
      elif opponent_defected_recently():
          return axl.Action.D
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent's action in the previous round appeared to be cooperation, cooperate.
# - If the opponent's action in the previous round appeared to be defection,
# defect.  3. Every 5 rounds, regardless of the opponent's previous action:    -
# If your total score is higher than or equal to the opponent's, cooperate.    -
# If your total score is lower than the opponent's, defect.  4. If the opponent
# has appeared to defect for 3 consecutive rounds, defect for the next 2 rounds.
# 5. After 5 consecutive mutual defections, attempt to restart cooperation by
# cooperating for 2 rounds.  6. From round 900 onwards:    - If your total score
# is significantly higher than the opponent's (by 50 points or more), always
# cooperate.    - If your total score is close to or lower than the opponent's,
# always defect.  7. Throughout the game, track the frequency of the opponent's
# apparent cooperation and defection:    - If the opponent cooperates more than
# 70% of the time, increase your cooperation frequency by 10%.    - If the
# opponent defects more than 70% of the time, increase your defection frequency
# by 10%.  8. Every 50 rounds, reassess your strategy based on the opponent's
# pattern of play and adjust accordingly.  9. Always keep in mind the 10% noise
# factor when interpreting the opponent's actions and adjust your certainty of
# their intentions accordingly.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_for_next_two = 0
          self.mutual_defections = 0
          self.cooperation_frequency = 0.5  # Default cooperation frequency
          return axl.Action.C
  
      # Helper function to check if the opponent cooperated in the last round
      def opponent_cooperated_last_round():
          return opponent.history[-1] == axl.Action.C
  
      # Helper function to check if the opponent defected in the last round
      def opponent_defected_last_round():
          return opponent.history[-1] == axl.Action.D
  
      # Track consecutive defections
      if opponent_defected_last_round():
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Track mutual defections
      if opponent_defected_last_round() and self.history[-1] == axl.Action.D:
          self.mutual_defections += 1
      else:
          self.mutual_defections = 0
  
      # Rule 4: If the opponent has defected for 3 consecutive rounds, defect for the next 2 rounds
      if self.consecutive_defections >= 3:
          self.defect_for_next_two = 2
  
      if self.defect_for_next_two > 0:
          self.defect_for_next_two -= 1
          return axl.Action.D
  
      # Rule 5: After 5 consecutive mutual defections, attempt to restart cooperation
      if self.mutual_defections >= 5:
          self.mutual_defections = 0
          return axl.Action.C
  
      # Rule 3: Every 5 rounds, compare scores and decide
      if len(self.history) % 5 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 6: From round 900 onwards, adjust based on score difference
      if len(self.history) >= 900:
          if self.score >= opponent.score + 50:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 7: Adjust cooperation/defection frequency based on opponent's behavior
      total_rounds = len(opponent.history)
      if total_rounds > 0:
          opponent_cooperation_rate = opponent.history.cooperations / total_rounds
          if opponent_cooperation_rate > 0.7:
              self.cooperation_frequency = min(1.0, self.cooperation_frequency + 0.1)
          elif opponent_cooperation_rate < 0.3:
              self.cooperation_frequency = max(0.0, self.cooperation_frequency - 0.1)
  
      # Rule 8: Every 50 rounds, reassess strategy (this is simplified as adjusting cooperation frequency)
      if len(self.history) % 50 == 0:
          # Reassess strategy based on opponent's pattern (already handled by cooperation frequency adjustment)
          pass
  
      # Rule 2: Default behavior based on opponent's last action
      if opponent_cooperated_last_round():
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a revised aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent's actions in the last
# two rounds were both defections, defect.  3. If the opponent's actions in the
# last two rounds were both cooperations, defect with 70% probability and
# cooperate with 30% probability.  4. If the opponent's actions in the last two
# rounds were mixed or unclear due to potential noise, defect with 60%
# probability and cooperate with 40% probability.  5. Every 30-70 rounds
# (randomly chosen), cooperate once regardless of the opponent's previous moves
# to probe for cooperation.  6. In the last 20 rounds of the game, defect with
# 90% probability and cooperate with 10% probability.  7. If your current score
# is more than 30 points behind your opponent's, increase the probability of
# defection by 10% for the next 10 rounds.  8. If you've cooperated for 4
# consecutive rounds, defect in the next round regardless of the opponent's
# actions.  9. If the opponent has cooperated for 4 consecutive rounds,
# cooperate twice, then return to the main strategy.  10. Every 100 rounds,
# reassess the opponent's overall cooperation rate. If it's above 40%, slightly
# increase your cooperation probability for the next 100 rounds.  Follow these
# rules in the order presented, applying the first applicable rule in each
# round. This strategy aims to be aggressive while adapting to the opponent's
# play and the game's noisy nature.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by defecting in the first round
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperations
          self.opponent_coop_streak = 0  # Track opponent's consecutive cooperations
          self.defect_boost_rounds = 0  # Track rounds where defection probability is boosted
          self.last_probe_round = 0  # Track the last round we probed for cooperation
          self.coop_boost_rounds = 0  # Track rounds where cooperation probability is boosted
          return axl.Action.D
  
      # Rule 7: If more than 30 points behind, increase defection probability by 10% for 10 rounds
      if self.defect_boost_rounds > 0:
          self.defect_boost_rounds -= 1
      else:
          if opponent.score - self.score > 30:
              self.defect_boost_rounds = 10
  
      # Rule 8: If cooperated for 4 consecutive rounds, defect
      if self.coop_streak >= 4:
          self.coop_streak = 0
          return axl.Action.D
  
      # Rule 9: If opponent cooperated for 4 consecutive rounds, cooperate twice
      if self.opponent_coop_streak >= 4:
          self.opponent_coop_streak = 0
          if len(self.history) < 2 or self.history[-1] != axl.Action.C:
              return axl.Action.C
  
      # Rule 5: Every 30-70 rounds, cooperate once to probe for cooperation
      if len(self.history) - self.last_probe_round >= self._random.randint(30, 70):
          self.last_probe_round = len(self.history)
          return axl.Action.C
  
      # Rule 6: In the last 20 rounds, defect with 90% probability
      if len(self.history) >= 980:
          return self._random.random_choice(0.1)
  
      # Rule 10: Every 100 rounds, reassess opponent's cooperation rate
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          opponent_coop_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_coop_rate > 0.4:
              self.coop_boost_rounds = 100
  
      # Rule 2: If opponent defected in the last two rounds, defect
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # Rule 3: If opponent cooperated in the last two rounds, defect with 70% probability
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return self._random.random_choice(0.3)
  
      # Rule 4: If opponent's actions were mixed or unclear, defect with 60% probability
      if len(opponent.history) >= 2 and (opponent.history[-1] != opponent.history[-2]):
          return self._random.random_choice(0.4)
  
      # Default to defection if no other rule applies
      return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.    - If your last action was unexpectedly flipped due
# to noise, play the action you had originally intended.  3. Every 20 rounds,
# forgive any defection and play C regardless of the opponent's last move.  4.
# If the opponent has defected more than 40% of the time in the last 50 rounds:
# - Play D for the next 5 rounds.    - Then attempt to re-establish cooperation
# by playing C for 2 rounds.    - If cooperation is not reciprocated, revert to
# the main strategy.  5. If you're trailing in score by more than 20 points
# after 100 rounds, become more cautious:    - Reduce forgiveness frequency to
# every 30 rounds.    - Lower the defection threshold to 30% in the last 50
# rounds.  6. In the last 20 rounds of the game:    - If the opponent has been
# cooperative (defected less than 20% in the last 50 rounds), continue with the
# main strategy.    - Otherwise, switch to always playing D.  7. Throughout the
# game, if you notice the opponent exploiting the forgiveness mechanism more
# than 3 times, remove it from your strategy and stick to simple tit-for-tat.
# 8. If there have been 10 consecutive rounds of mutual defection, attempt to
# break the cycle by playing C for 2 rounds, then revert to the main strategy.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.intended_action = axl.Action.C
          self.forgiveness_counter = 0
          self.exploit_count = 0
          self.defection_streak = 0
          self.cautious_mode = False
          return axl.Action.C
  
      # Helper function to check if noise flipped the last action
      def was_noisy_flip():
          return self.history[-1] != self.intended_action
  
      # Helper function to count defections in the last N rounds
      def count_defections(history, n):
          return history[-n:].count(axl.Action.D)
  
      # Helper function to check if opponent is exploiting forgiveness
      def check_exploit():
          if len(self.history) >= 2 and self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.D:
              if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
                  self.exploit_count += 1
  
      # Helper function to check if we are in the last 20 rounds
      def in_last_20_rounds():
          return len(self.history) >= 980
  
      # Helper function to check if we are trailing by more than 20 points after 100 rounds
      def check_trailing():
          if len(self.history) >= 100:
              return self.score < opponent.score - 20
          return False
  
      # Step 7: Remove forgiveness if exploited more than 3 times
      check_exploit()
      if self.exploit_count > 3:
          return axl.Action.D if opponent.history[-1] == axl.Action.D else axl.Action.C
  
      # Step 6: In the last 20 rounds, switch to always D if opponent defected more than 20% in the last 50 rounds
      if in_last_20_rounds():
          if count_defections(opponent.history, 50) / min(50, len(opponent.history)) >= 0.2:
              return axl.Action.D
          else:
              return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
  
      # Step 5: If trailing by more than 20 points after 100 rounds, become more cautious
      if check_trailing():
          self.cautious_mode = True
  
      # Step 4: If opponent defected more than 40% (or 30% in cautious mode) in the last 50 rounds, punish
      defection_threshold = 0.3 if self.cautious_mode else 0.4
      if count_defections(opponent.history, 50) / min(50, len(opponent.history)) > defection_threshold:
          if len(self.history) % 7 < 5:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Step 3: Every 20 (or 30 in cautious mode) rounds, forgive and play C
      forgiveness_frequency = 30 if self.cautious_mode else 20
      if len(self.history) % forgiveness_frequency == 0:
          return axl.Action.C
  
      # Step 8: If there have been 10 consecutive mutual defections, attempt to break the cycle
      if len(self.history) >= 10 and self.history[-10:] == [axl.Action.D] * 10 and opponent.history[-10:] == [axl.Action.D] * 10:
          if len(self.history) % 2 == 0:
              return axl.Action.C
          else:
              return axl.Action.C
  
      # Step 2: Tit-for-tat with noise correction
      if was_noisy_flip():
          return self.intended_action
      else:
          self.intended_action = axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
          return self.intended_action



# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent's action in
# the previous round was cooperation, cooperate.    - If the opponent's action
# was defection, defect with a 60% probability and cooperate with a 40%
# probability.  3. Every 15 rounds, randomly choose to cooperate with a 70%
# probability, regardless of the opponent's previous action.  4. To detect
# patterns, analyze the opponent's last 20 moves:    - If they defected in at
# least 18 out of 20 rounds, switch to always defecting for the next 10 rounds.
# - If they alternated perfectly for 20 rounds, play the opposite of their
# expected next move for the next 10 rounds.    - Reassess after these 10
# rounds.  5. In the last 20 rounds of the game:    - If your cumulative score
# is higher than the opponent's, continue with the main strategy.    - If your
# score is lower, increase defection probability to 80%.  6. Track the overall
# cooperation rate over the last 50 rounds:    - If it falls below 30%, increase
# your cooperation probability by 10% for the next 30 rounds.    - If it rises
# above 70%, decrease your cooperation probability by 10% for the next 30
# rounds.  7. To account for noise:    - If an opponent's defection is preceded
# by 3 or more cooperations, assume it might be noise and cooperate in the next
# round.    - Keep a "noise counter." Increment it for unexpected actions,
# decrement for expected ones. If it exceeds 5, reset it and adapt your
# expectations of the opponent's strategy.  8. Calculate the score difference
# between you and your opponent every 50 rounds:    - If you're behind by more
# than 30 points, increase defection probability by 15% for the next 30 rounds.
# - If you're ahead by more than 30 points, increase cooperation probability by
# 15% for the next 30 rounds.  9. Implement a sliding window of the last 100
# rounds to detect if the opponent's strategy is changing over time. If
# significant change is detected, reset your strategy to the initial state.  10.
# For the first 5 defections by the opponent, respond by defecting only in the
# immediately following round, then revert to cooperation to allow for the
# possibility of establishing mutual cooperation early in the game.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_streak = 0
          self.alternation_streak = 0
          self.noise_counter = 0
          self.defect_for_next_10 = 0
          self.opposite_for_next_10 = 0
          self.coop_prob = 0.4
          self.defect_prob = 0.6
          self.adjustment_rounds = 0
          return axl.Action.C
  
      # Helper function to detect alternation pattern
      def is_alternating(history):
          return all(history[i] != history[i + 1] for i in range(len(history) - 1))
  
      # Helper function to adjust cooperation/defection probabilities
      def adjust_probabilities():
          if self.adjustment_rounds > 0:
              self.adjustment_rounds -= 1
          else:
              coop_rate = self.history[-50:].count(axl.Action.C) / 50 if len(self.history) >= 50 else 0
              if coop_rate < 0.3:
                  self.coop_prob = min(1.0, self.coop_prob + 0.1)
              elif coop_rate > 0.7:
                  self.coop_prob = max(0.0, self.coop_prob - 0.1)
              self.adjustment_rounds = 30
  
      # Helper function to handle noise
      def handle_noise():
          if len(opponent.history) >= 4 and opponent.history[-1] == axl.Action.D and opponent.history[-4:-1].count(axl.Action.C) == 3:
              return axl.Action.C
          return None
  
      # Step 9: Detect strategy change over the last 100 rounds
      if len(self.history) >= 100:
          recent_history = self.history[-100:]
          if recent_history.count(axl.Action.C) != self.history[-200:-100].count(axl.Action.C):
              self.defect_for_next_10 = 0
              self.opposite_for_next_10 = 0
              self.coop_prob = 0.4
              self.defect_prob = 0.6
  
      # Step 4: Analyze the last 20 moves
      if len(opponent.history) >= 20:
          last_20 = opponent.history[-20:]
          if last_20.count(axl.Action.D) >= 18:
              self.defect_for_next_10 = 10
          elif is_alternating(last_20):
              self.opposite_for_next_10 = 10
  
      # Step 5: Adjust strategy in the last 20 rounds
      if len(self.history) >= 980:
          if self.score < opponent.score:
              self.defect_prob = 0.8
  
      # Step 6: Adjust cooperation rate based on the last 50 rounds
      adjust_probabilities()
  
      # Step 8: Adjust based on score difference every 50 rounds
      if len(self.history) % 50 == 0 and len(self.history) > 0:
          my_score, opp_score = self.total_scores(self.history[-50:], opponent.history[-50:])
          score_diff = my_score - opp_score
          if score_diff < -30:
              self.defect_prob = min(1.0, self.defect_prob + 0.15)
          elif score_diff > 30:
              self.coop_prob = min(1.0, self.coop_prob + 0.15)
  
      # Step 10: Handle first 5 defections
      if opponent.history.defections <= 5 and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: Every 15 rounds, cooperate with 70% probability
      if len(self.history) % 15 == 0:
          return self._random.random_choice(0.7)
  
      # Step 2: Main strategy
      if self.defect_for_next_10 > 0:
          self.defect_for_next_10 -= 1
          return axl.Action.D
      if self.opposite_for_next_10 > 0:
          self.opposite_for_next_10 -= 1
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Handle noise
      noise_action = handle_noise()
      if noise_action:
          return noise_action
  
      # Respond to opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return self._random.random_choice(self.coop_prob)



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent's last observed action
# was defection, defect with 90% probability and cooperate with 10% probability.
# 3. If the opponent's last observed action was cooperation, cooperate with 70%
# probability and defect with 30% probability.  4. Keep a running tally of the
# opponent's cooperation rate over the last 10 rounds. If this rate exceeds 80%,
# increase your cooperation probability by 10% for the next 5 rounds.  5. If you
# have defected for 3 consecutive rounds, cooperate once to test the opponent's
# response.  6. If the opponent has cooperated for 2 consecutive rounds,
# cooperate once to potentially establish a mutually beneficial pattern.  7. In
# the last 20 rounds of the game, match the opponent's cooperation rate from the
# previous 20 rounds.  8. If your overall score is lower than the opponent's,
# gradually increase your defection probability by 5% every 10 rounds, up to a
# maximum of 80% defection probability.  9. Every 50 rounds, reassess your
# strategy's performance. If your score is significantly lower than expected,
# reset to the base strategy (steps 2-3).  10. To account for noise, consider an
# action as "consistent" only if it has been observed in at least 2 out of the
# last 3 rounds.  11. If the opponent's behavior seems random (close to 50%
# cooperation rate over the last 20 rounds), default to a slightly defection-
# biased strategy (60% defection, 40% cooperation).

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.cooperation_rate_last_10 = []
          self.cooperation_boost_rounds = 0
          self.defection_bias = 0.0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          return history[-N:].count(axl.Action.C) / N if len(history) >= N else history.cooperations / len(history)
  
      # Step 2-3: Base strategy based on opponent's last action
      if len(opponent.history) > 0:
          if opponent.history[-1] == axl.Action.D:
              base_action = self._random.random_choice(0.1)  # 90% defect, 10% cooperate
          else:
              base_action = self._random.random_choice(0.7)  # 70% cooperate, 30% defect
      else:
          base_action = axl.Action.C  # Default to cooperate if no history
  
      # Step 4: Track cooperation rate over the last 10 rounds and adjust cooperation probability
      if len(opponent.history) >= 10:
          coop_rate = cooperation_rate(opponent.history, 10)
          self.cooperation_rate_last_10.append(coop_rate)
          if coop_rate > 0.8 and self.cooperation_boost_rounds == 0:
              self.cooperation_boost_rounds = 5
  
      if self.cooperation_boost_rounds > 0:
          self.cooperation_boost_rounds -= 1
          base_action = self._random.random_choice(0.8)  # Increase cooperation by 10%
  
      # Step 5: If defected for 3 consecutive rounds, cooperate once
      if self.history[-3:].count(axl.Action.D) == 3:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Step 6: If opponent cooperated for 2 consecutive rounds, cooperate once
      if opponent.history[-2:].count(axl.Action.C) == 2:
          return axl.Action.C
  
      # Step 7: In the last 20 rounds, match opponent's cooperation rate from the previous 20 rounds
      if len(self.history) >= 980:
          coop_rate_last_20 = cooperation_rate(opponent.history, 20)
          return self._random.random_choice(coop_rate_last_20)
  
      # Step 8: If score is lower than opponent's, increase defection probability
      if self.score < opponent.score and len(self.history) % 10 == 0:
          self.defection_bias = min(self.defection_bias + 0.05, 0.8)
  
      # Step 9: Every 50 rounds, reassess and reset strategy if score is significantly lower
      if len(self.history) % 50 == 0:
          if self.score < opponent.score * 0.9:  # Significantly lower score
              self.defection_bias = 0.0  # Reset to base strategy
  
      # Step 10: Consider an action consistent if observed in 2 out of the last 3 rounds
      if len(opponent.history) >= 3:
          recent_coop = opponent.history[-3:].count(axl.Action.C)
          if recent_coop >= 2:
              base_action = axl.Action.C
          elif recent_coop <= 1:
              base_action = axl.Action.D
  
      # Step 11: If opponent's behavior seems random, default to 60% defection
      if len(opponent.history) >= 20:
          coop_rate_last_20 = cooperation_rate(opponent.history, 20)
          if 0.4 <= coop_rate_last_20 <= 0.6:
              return self._random.random_choice(0.4)  # 60% defect, 40% cooperate
  
      # Apply defection bias if any
      if self.defection_bias > 0:
          return self._random.random_choice(1 - self.defection_bias)
  
      return base_action



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 20 rounds,
# forgive any defection and play C regardless of the opponent's recent moves.
# 4. If the opponent has defected more than 40% of the time in the last 30
# rounds:    - Play D for 5 rounds.    - Then alternate between C and D for 5
# rounds.    - Return to the main strategy afterwards.  5. In the last 20 rounds
# of the game, gradually increase the probability of playing D:    - Play D with
# 25% probability in rounds 981-990.    - Play D with 50% probability in rounds
# 991-995.    - Play D with 75% probability in rounds 996-1000.  6. If you
# notice the opponent alternating between C and D for at least 6 consecutive
# rounds, match their pattern for the next 6 rounds by playing C when you expect
# them to play D, and D when you expect them to play C.  7. After any streak of
# mutual defection lasting 5 or more rounds, attempt to reset cooperation by
# playing C for 2 rounds, then return to the main strategy.  8. Throughout the
# game, if your score is consistently lower than the opponent's over the last 50
# rounds, slightly increase your probability of playing D (by 10%) until scores
# even out.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if opponent alternates between C and D
      def is_alternating(history, length):
          if len(history) < length:
              return False
          for i in range(-length, -1):
              if history[i] == history[i + 1]:
                  return False
          return True
  
      # Helper function to calculate defection rate in the last N rounds
      def defection_rate(history, N):
          if len(history) < N:
              return 0
          return history[-N:].count(axl.Action.D) / N
  
      # Helper function to gradually increase defection probability in the last 20 rounds
      def defection_probability_in_endgame(round_number):
          if 981 <= round_number <= 990:
              return 0.25
          elif 991 <= round_number <= 995:
              return 0.50
          elif 996 <= round_number <= 1000:
              return 0.75
          return 0
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history)
  
      # Rule 3: Every 20 rounds, forgive and play C
      if round_number % 20 == 0:
          return axl.Action.C
  
      # Rule 4: If opponent defected more than 40% in the last 30 rounds, play D for 5 rounds, then alternate C and D for 5 rounds
      if defection_rate(opponent.history, 30) > 0.4:
          if round_number % 10 < 5:
              return axl.Action.D
          else:
              return axl.Action.C if round_number % 2 == 0 else axl.Action.D
  
      # Rule 5: In the last 20 rounds, increase probability of playing D
      if round_number > 980:
          if self._random.random_choice(defection_probability_in_endgame(round_number)):
              return axl.Action.D
          return axl.Action.C
  
      # Rule 6: If opponent alternates between C and D for 6 rounds, match their pattern
      if is_alternating(opponent.history, 6):
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Rule 7: After a streak of mutual defection lasting 5 or more rounds, reset cooperation
      if len(self.history) >= 5 and all(x == axl.Action.D for x in self.history[-5:]) and all(x == axl.Action.D for x in opponent.history[-5:]):
          if round_number % 2 == 0:
              return axl.Action.C
          else:
              return axl.Action.C
  
      # Rule 8: If your score is consistently lower than the opponent's over the last 50 rounds, increase defection probability
      if round_number > 50:
          my_score, opponent_score = self.total_scores(self.history[-50:], opponent.history[-50:])
          if my_score < opponent_score:
              if self._random.random_choice(0.1):
                  return axl.Action.D
  
      # Rule 2: Play C if opponent played C in at least 2 of the last 3 rounds, otherwise play D
      if opponent.history[-3:].count(axl.Action.C) >= 2:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a revised strategy for the game:  1. Start by cooperating in the first
# round.  2. For subsequent rounds:    - Cooperate if the opponent seemed to
# cooperate in at least 2 of the last 3 rounds.    - Defect if the opponent
# seemed to defect in at least 2 of the last 3 rounds.  3. Every 20 rounds,
# regardless of the opponent's previous moves:    - Cooperate to potentially
# reset a cycle of mutual defection.  4. If you detect a consistent pattern in
# the opponent's moves over the last 10 rounds:    - Adapt your strategy to
# match or counter their pattern for the next 10 rounds.  5. In the last 100
# rounds of the game:    - Gradually increase the probability of defection,
# starting from 10% and reaching 100% in the final round.  6. If your overall
# score falls behind your opponent's by more than 30 points:    - Increase your
# defection probability by 20% for the next 30 rounds, then reassess.  7.
# Occasionally (with a 2% chance each round), play a random move to probe the
# opponent's strategy.  8. After any round where your intended action was
# different from the outcome:    - Assume there's a 10% chance it was due to
# noise and maintain your current strategy.    - If it happens twice in a row,
# adjust your next move as if the opponent had made the opposite choice.  9. If
# the opponent seems to be forgiving (cooperates after your defection), be more
# willing to return to cooperation after a single cooperative move from them.
# 10. Continuously track the success rate of your actions and be prepared to
# switch to a pure "always defect" or "always cooperate" strategy if it
# consistently outperforms your main strategy over 50-round intervals.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to check if opponent cooperated in at least 2 of the last 3 rounds
      def opponent_cooperated_in_last_3():
          return opponent.history[-3:].count(axl.Action.C) >= 2
  
      # Helper function to check if opponent defected in at least 2 of the last 3 rounds
      def opponent_defected_in_last_3():
          return opponent.history[-3:].count(axl.Action.D) >= 2
  
      # Helper function to detect a consistent pattern in the last 10 rounds
      def detect_pattern():
          if len(opponent.history) < 10:
              return None
          return opponent.history[-10:]
  
      # Helper function to adapt to a detected pattern
      def adapt_to_pattern(pattern):
          if len(self.history) % 10 < len(pattern):
              return pattern[len(self.history) % 10]
          return None
  
      # Helper function to gradually increase defection probability in the last 100 rounds
      def defection_probability_in_last_100():
          if len(self.history) >= 900:
              round_number = len(self.history) - 900
              return 0.1 + (round_number / 100)
          return 0
  
      # Helper function to increase defection probability if behind by more than 30 points
      def increase_defection_if_behind():
          if self.score < opponent.score - 30:
              if not self.defection_boost_rounds:
                  self.defection_boost_rounds = 30
              if self.defection_boost_rounds > 0:
                  self.defection_boost_rounds -= 1
                  return 0.2
          return 0
  
      # Helper function to probe opponent's strategy with 2% chance
      def probe_opponent():
          return self._random.random_choice(0.02)
  
      # Helper function to handle noise detection
      def handle_noise():
          if len(self.history) >= 2 and self.history[-1] != self.history[-2]:
              if not self.noise_count:
                  self.noise_count = 0
              self.noise_count += 1
              if self.noise_count >= 2:
                  self.noise_count = 0
                  return axl.Action.C if opponent.history[-1] == axl.Action.D else axl.Action.D
          return None
  
      # Helper function to check if opponent is forgiving
      def opponent_is_forgiving():
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return True
          return False
  
      # Helper function to track success rate and switch to pure strategies
      def track_success_rate():
          if len(self.history) >= 50:
              last_50_self, last_50_opponent = self.total_scores(self.history[-50:], opponent.history[-50:])
              if last_50_self > last_50_opponent:
                  return axl.Action.D
              elif last_50_opponent > last_50_self:
                  return axl.Action.C
          return None
  
      # First round: cooperate
      if self.first_round():
          self.noise_count = None
          self.defection_boost_rounds = None
          return axl.Action.C
  
      # Every 20 rounds, cooperate to reset mutual defection
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # Detect and adapt to a pattern in the last 10 rounds
      pattern = detect_pattern()
      if pattern:
          adapted_move = adapt_to_pattern(pattern)
          if adapted_move:
              return adapted_move
  
      # Gradually increase defection probability in the last 100 rounds
      if len(self.history) >= 900:
          if self._random.random() < defection_probability_in_last_100():
              return axl.Action.D
  
      # Increase defection probability if behind by more than 30 points
      if self._random.random() < increase_defection_if_behind():
          return axl.Action.D
  
      # Probe opponent's strategy with 2% chance
      if probe_opponent():
          return self._random.random_choice()
  
      # Handle noise detection
      noise_move = handle_noise()
      if noise_move:
          return noise_move
  
      # If opponent is forgiving, return to cooperation
      if opponent_is_forgiving():
          return axl.Action.C
  
      # Track success rate and switch to pure strategies if needed
      pure_strategy_move = track_success_rate()
      if pure_strategy_move:
          return pure_strategy_move
  
      # Default strategy: cooperate if opponent cooperated in at least 2 of the last 3 rounds, otherwise defect
      if opponent_cooperated_in_last_3():
          return axl.Action.C
      elif opponent_defected_in_last_3():
          return axl.Action.D
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C



# Here's a revised aggressive strategy for the iterated normal-form game:  1.
# Start by defecting (D) in the first round.  2. Keep a running tally of the
# opponent's actions, accounting for the 10% noise factor. If an action seems
# inconsistent with recent behavior, assume it might be due to noise.  3. In
# general, if the opponent's last observed action was defection, or if they've
# defected in more than 60% of the last 10 rounds, defect in the next round.  4.
# If the opponent's last observed action was cooperation, or if they've
# cooperated in more than 60% of the last 10 rounds, defect with 70% probability
# and cooperate with 30% probability.  5. If you've defected for 7 consecutive
# rounds, cooperate once to test the opponent's response. This makes the pattern
# less predictable.  6. If the opponent has cooperated for 4 consecutive rounds,
# cooperate once to potentially establish a mutually beneficial pattern.  7. In
# the last 20 rounds of the game, increase defection probability to 90%
# regardless of the opponent's actions, but maintain a small chance of
# cooperation to avoid complete predictability.  8. If your overall score falls
# below 1.5 points per round on average over the last 50 rounds, switch to a
# generous tit-for-tat strategy (cooperate after opponent's cooperation, defect
# with 70% probability after opponent's defection) for the next 20 rounds before
# reverting to the main strategy.  9. Every 100 rounds, reassess the opponent's
# overall strategy. If they seem to be consistently cooperative (cooperating
# more than 70% of the time), slightly increase your cooperation probability in
# step 4 to 40% for the next 100 rounds.  10. If stuck in a mutual defection
# loop for more than 20 rounds, initiate two consecutive cooperations to attempt
# breaking the cycle.  11. Repeat steps 2-10 for the duration of the game,
# continuously adapting based on the opponent's behavior and the game's
# progress.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Subfunction to calculate cooperation and defection rates in the last N rounds
      def cooperation_rate(history, N):
          return history[-N:].count(axl.Action.C) / N if len(history) >= N else history.cooperations / len(history)
  
      def defection_rate(history, N):
          return history[-N:].count(axl.Action.D) / N if len(history) >= N else history.defections / len(history)
  
      # Subfunction to switch to generous tit-for-tat strategy
      def generous_tit_for_tat():
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return self._random.random_choice(0.3)
  
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.generous_tft_mode = False
          self.generous_tft_counter = 0
          self.cooperation_boost = 0.3
          return axl.Action.D
  
      # Step 8: Check if we need to switch to generous tit-for-tat
      if len(self.history) >= 50:
          recent_score, _ = self.total_scores(self.history[-50:], opponent.history[-50:])
          if recent_score / 50 < 1.5:
              self.generous_tft_mode = True
              self.generous_tft_counter = 20
  
      # If in generous tit-for-tat mode, follow that strategy for 20 rounds
      if self.generous_tft_mode:
          self.generous_tft_counter -= 1
          if self.generous_tft_counter == 0:
              self.generous_tft_mode = False
          return generous_tit_for_tat()
  
      # Step 2: Track opponent's actions with noise consideration
      last_action = opponent.history[-1]
      if len(opponent.history) > 1:
          if opponent.history[-2] != last_action:
              # Assume noise, use the second last action instead
              last_action = opponent.history[-2]
  
      # Step 3: Defect if opponent's last action was defection or if they defected > 60% in last 10 rounds
      if last_action == axl.Action.D or defection_rate(opponent.history, 10) > 0.6:
          self.consecutive_defections += 1
          return axl.Action.D
  
      # Step 4: If opponent cooperated, defect with 70% probability, cooperate with 30% probability
      if last_action == axl.Action.C or cooperation_rate(opponent.history, 10) > 0.6:
          self.consecutive_defections = 0
          return self._random.random_choice(self.cooperation_boost)
  
      # Step 5: If defected for 7 consecutive rounds, cooperate once
      if self.consecutive_defections >= 7:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Step 6: If opponent cooperated for 4 consecutive rounds, cooperate once
      if len(opponent.history) >= 4 and opponent.history[-4:] == [axl.Action.C] * 4:
          return axl.Action.C
  
      # Step 7: In the last 20 rounds, increase defection probability to 90%
      if self.match_attributes['length'] is not None and len(self.history) >= self.match_attributes['length'] - 20:
          return self._random.random_choice(0.1)
  
      # Step 9: Every 100 rounds, reassess opponent's strategy and adjust cooperation probability
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          if cooperation_rate(opponent.history, len(opponent.history)) > 0.7:
              self.cooperation_boost = 0.4
          else:
              self.cooperation_boost = 0.3
  
      # Step 10: If stuck in mutual defection loop for more than 20 rounds, cooperate twice
      if len(self.history) >= 20 and self.history[-20:] == [axl.Action.D] * 20 and opponent.history[-20:] == [axl.Action.D] * 20:
          return axl.Action.C if self.history[-1] == axl.Action.D else axl.Action.C
  
      # Default action is to defect
      return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 15 rounds,
# forgive the opponent by playing C regardless of their recent moves.  4. If the
# opponent has played D for 4 consecutive rounds, switch to playing D for the
# next 2 rounds before reverting to the main strategy.  5. In the last 50
# rounds, gradually increase the likelihood of playing D:    - In rounds
# 951-975, play D with 25% probability.    - In rounds 976-990, play D with 50%
# probability.    - In rounds 991-1000, play D with 75% probability.  6. If your
# score falls more than 10 points behind your opponent's, play D for the next 3
# rounds before reverting to the main strategy.  7. After any streak of mutual
# defection lasting 5 or more rounds, attempt to re-establish cooperation by
# playing C for 2 rounds.  8. Every 100 rounds, reassess the opponent's overall
# cooperation rate. If it's below 40%, become more defensive by requiring 3 out
# of 4 recent C plays from the opponent to cooperate.  9. If you're 30 or more
# points ahead, occasionally (10% chance) play C even when the strategy suggests
# D, to maintain goodwill.  10. In the first 100 rounds, be more forgiving:
# revert to C after just 1 round of playing D in response to the opponent's
# defection.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to check if opponent played C in at least 2 of the last 3 rounds
      def opponent_cooperated_recently():
          return opponent.history[-3:].count(axl.Action.C) >= 2
  
      # Helper function to check if opponent played D in at least 2 of the last 3 rounds
      def opponent_defected_recently():
          return opponent.history[-3:].count(axl.Action.D) >= 2
  
      # Helper function to check if opponent played D for 4 consecutive rounds
      def opponent_defected_4_consecutive():
          return opponent.history[-4:] == [axl.Action.D] * 4
  
      # Helper function to check if there was a mutual defection streak of 5 or more rounds
      def mutual_defection_streak():
          return len(self.history) >= 5 and all(
              self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
              for i in range(1, 6)
          )
  
      # Helper function to calculate opponent's cooperation rate
      def opponent_cooperation_rate():
          return opponent.history.cooperations / len(opponent.history)
  
      # Helper function to check if we are in the last 50 rounds
      def in_last_50_rounds():
          return len(self.history) >= 951
  
      # Helper function to determine the probability of playing D in the last 50 rounds
      def last_50_rounds_defection_probability():
          if 951 <= len(self.history) <= 975:
              return 0.25
          elif 976 <= len(self.history) <= 990:
              return 0.50
          elif 991 <= len(self.history) <= 1000:
              return 0.75
          return 0
  
      # First round: always cooperate
      if self.first_round():
          self.defect_streak = 0  # Track defect streaks
          self.forgive_round = 15  # Track forgiveness rounds
          self.defensive_mode = False  # Track defensive mode
          return axl.Action.C
  
      # Every 15 rounds, forgive the opponent by playing C
      if len(self.history) == self.forgive_round:
          self.forgive_round += 15
          return axl.Action.C
  
      # If opponent defected for 4 consecutive rounds, play D for the next 2 rounds
      if opponent_defected_4_consecutive():
          self.defect_streak = 2
  
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # If score falls more than 10 points behind, play D for the next 3 rounds
      if self.score < opponent.score - 10:
          self.defect_streak = 3
          return axl.Action.D
  
      # If mutual defection streak of 5 or more rounds, play C for 2 rounds
      if mutual_defection_streak():
          self.defect_streak = -2  # Use negative to track cooperation streak
          return axl.Action.C
  
      if self.defect_streak < 0:
          self.defect_streak += 1
          return axl.Action.C
  
      # Every 100 rounds, reassess opponent's cooperation rate
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          if opponent_cooperation_rate() < 0.40:
              self.defensive_mode = True
          else:
              self.defensive_mode = False
  
      # If in defensive mode, require 3 out of 4 recent C plays to cooperate
      if self.defensive_mode:
          if opponent.history[-4:].count(axl.Action.C) >= 3:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # In the last 50 rounds, increase the likelihood of playing D
      if in_last_50_rounds():
          if self._random.random_choice(last_50_rounds_defection_probability()):
              return axl.Action.D
  
      # If 30 or more points ahead, occasionally (10% chance) play C even when D is suggested
      if self.score >= opponent.score + 30:
          if self._random.random_choice(0.10):
              return axl.Action.C
  
      # In the first 100 rounds, be more forgiving: revert to C after 1 round of D
      if len(self.history) <= 100 and self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Main strategy: play C if opponent cooperated in at least 2 of the last 3 rounds, else D
      if opponent_cooperated_recently():
          return axl.Action.C
      elif opponent_defected_recently():
          return axl.Action.D
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating for the first 3 rounds.  2. For subsequent rounds:    - Calculate
# the opponent's cooperation rate over the last 20 rounds, or all previous
# rounds if fewer than 20 have been played.    - If their cooperation rate is
# 70% or higher, cooperate.    - If their cooperation rate is below 40%, defect.
# - If their cooperation rate is between 40% and 70%:      a. If they cooperated
# in the last round, cooperate.      b. If they defected in the last round,
# defect.  3. Implement a sliding forgiveness factor for noisy actions:    - If
# an opponent's action differs from their recent behavior, increase tolerance by
# 5%.    - Reset tolerance to 0% after 5 consecutive expected actions.  4. Every
# 30-50 rounds (randomly chosen):    - Cooperate for one round to test the
# opponent's willingness to reciprocate.  5. In the last 20 rounds:    - If the
# opponent's cooperation rate in the last 50 rounds is above 60%, continue using
# the main strategy.    - Otherwise, defect to maximize final payoff.  6.
# Throughout the game:    - Keep track of the cumulative cooperation rate of the
# opponent.    - If this rate drops below 30% or exceeds 80%, adjust the
# thresholds in step 2 by 5% in the corresponding direction.  7. If the opponent
# seems to be mirroring your strategy:    - Occasionally (10% chance) deviate
# from your usual choice to test their reaction.  8. In case of ties or very
# close cooperation rates to the thresholds:    - Lean towards cooperation to
# promote mutual benefit.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.tolerance = 0
          self.consecutive_expected_actions = 0
          self.test_round_counter = self._random.randint(30, 50)
          return axl.Action.C
  
      # Cooperate for the first 3 rounds
      if len(self.history) < 3:
          return axl.Action.C
  
      # Calculate opponent's cooperation rate over the last 20 rounds (or fewer if less than 20 rounds played)
      window = min(20, len(opponent.history))
      recent_cooperations = opponent.history[-window:].count(axl.Action.C)
      cooperation_rate = recent_cooperations / window
  
      # Sliding forgiveness factor for noisy actions
      if len(self.history) > 1:
          last_action = self.history[-1]
          expected_action = axl.Action.C if cooperation_rate >= 0.7 else axl.Action.D if cooperation_rate < 0.4 else opponent.history[-1]
          if last_action == expected_action:
              self.consecutive_expected_actions += 1
              if self.consecutive_expected_actions >= 5:
                  self.tolerance = 0
          else:
              self.tolerance += 0.05
              self.consecutive_expected_actions = 0
  
      # Adjust thresholds based on cumulative cooperation rate
      total_cooperations = opponent.history.cooperations
      total_rounds = len(opponent.history)
      cumulative_cooperation_rate = total_cooperations / total_rounds
      if cumulative_cooperation_rate < 0.3:
          coop_threshold = 0.65
          defect_threshold = 0.35
      elif cumulative_cooperation_rate > 0.8:
          coop_threshold = 0.75
          defect_threshold = 0.45
      else:
          coop_threshold = 0.7
          defect_threshold = 0.4
  
      # Main strategy logic
      if cooperation_rate >= coop_threshold:
          action = axl.Action.C
      elif cooperation_rate < defect_threshold:
          action = axl.Action.D
      else:
          action = opponent.history[-1]
  
      # Random test round every 30-50 rounds
      if len(self.history) == self.test_round_counter:
          self.test_round_counter += self._random.randint(30, 50)
          return axl.Action.C
  
      # In the last 20 rounds, adjust strategy based on opponent's cooperation rate in the last 50 rounds
      if len(self.history) >= 980:
          window = min(50, len(opponent.history))
          recent_cooperations = opponent.history[-window:].count(axl.Action.C)
          recent_cooperation_rate = recent_cooperations / window
          if recent_cooperation_rate < 0.6:
              return axl.Action.D
  
      # Occasionally deviate if opponent seems to be mirroring
      if self._random.random_choice(0.1):
          action = axl.Action.D if action == axl.Action.C else axl.Action.C
  
      # Lean towards cooperation in case of ties or close thresholds
      if abs(cooperation_rate - coop_threshold) < 0.05 or abs(cooperation_rate - defect_threshold) < 0.05:
          action = axl.Action.C
  
      return action



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent's action in the
# previous round was D, defect with 90% probability and cooperate with 10%
# probability.  3. If the opponent's action in the previous round was C,
# cooperate with 70% probability and defect with 30% probability.  4. Keep a
# rolling average of the opponent's cooperation rate over the last 20 rounds. If
# this rate drops below 30%, increase your defection probability by 20% for the
# next 10 rounds.  5. If your score falls behind by more than 75 points,
# increase your defection probability by 30% for the next 30 rounds.  6. Every
# 100 rounds, reassess your overall strategy:    - If your score is higher,
# maintain the current approach.    - If your score is lower, increase your
# defection probability by 10% for the next 100 rounds.  7. In the last 50
# rounds, gradually increase your defection probability, reaching 100% in the
# final 10 rounds.  8. To account for noise, if an opponent's move seems out of
# character based on their recent pattern, assume it might be due to noise and
# respond based on their overall trend rather than the single move.  9. If
# you're ahead by more than 150 points, slightly decrease your defection
# probability by 10% to avoid appearing overly aggressive.  10. After any
# temporary changes to the strategy, return to the main approach outlined in
# points 2 and 3.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_boost = 0  # Temporary defection boost
          self.boost_rounds_left = 0  # Rounds left for temporary boost
          self.reassess_rounds_left = 100  # Rounds left for reassessment
          self.last_50_rounds = False  # Flag for the last 50 rounds
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate opponent's cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Helper function to adjust defection probability based on temporary boosts
      def adjust_defection_probability(base_prob):
          if self.boost_rounds_left > 0:
              return min(1, base_prob + self.defection_boost)
          return base_prob
  
      # Step 4: Rolling average of opponent's cooperation rate over the last 20 rounds
      coop_rate = cooperation_rate(opponent.history, 20)
      if coop_rate < 0.3 and self.boost_rounds_left == 0:
          self.defection_boost = 0.2
          self.boost_rounds_left = 10
  
      # Step 5: Check if behind by more than 75 points
      if self.boost_rounds_left == 0:
          if opponent.score - self.score > 75:
              self.defection_boost = 0.3
              self.boost_rounds_left = 30
  
      # Step 6: Reassess strategy every 100 rounds
      if self.reassess_rounds_left == 0:
          if opponent.score > self.score:
              self.defection_boost = 0.1
              self.boost_rounds_left = 100
          self.reassess_rounds_left = 100
      else:
          self.reassess_rounds_left -= 1
  
      # Step 7: Last 50 rounds, gradually increase defection probability
      if len(self.history) >= 950:
          self.last_50_rounds = True
          rounds_left = 1000 - len(self.history)
          if rounds_left <= 10:
              return axl.Action.D  # Defect 100% in the last 10 rounds
          else:
              defection_prob = (50 - rounds_left) / 50  # Gradually increase defection
              if self._random.random_choice(defection_prob):
                  return axl.Action.D
              return axl.Action.C
  
      # Step 9: If ahead by more than 150 points, decrease defection probability
      if self.score - opponent.score > 150 and self.boost_rounds_left == 0:
          self.defection_boost = -0.1
          self.boost_rounds_left = 10
  
      # Step 10: Handle temporary boosts
      if self.boost_rounds_left > 0:
          self.boost_rounds_left -= 1
  
      # Step 2 and 3: Base strategy based on opponent's last move
      if opponent.history[-1] == axl.Action.D:
          base_defection_prob = 0.9
      else:
          base_defection_prob = 0.3
  
      # Adjust defection probability based on temporary boosts
      defection_prob = adjust_defection_probability(base_defection_prob)
  
      # Randomly choose action based on the calculated defection probability
      if self._random.random_choice(defection_prob):
          return axl.Action.D
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 15 rounds,
# randomly choose to forgive any defection and play C, regardless of the
# opponent's previous moves. This introduces unpredictability.  4. If the
# opponent has defected more than 40% of the time in the last 30 rounds, switch
# to playing D for the next 5 rounds before reverting to the main strategy.  5.
# In the last 20 rounds, play a mixed strategy: 70% C and 30% D, adjusting based
# on the opponent's moves in the last 5 rounds.  6. If your score is lower than
# your opponent's by more than 30 points after every 50 rounds, increase your
# defection probability by 10% for the next 10 rounds before reverting to the
# main strategy.  7. After 5 consecutive rounds of mutual defection, attempt to
# re-establish cooperation by playing C for 2 rounds, then revert to the main
# strategy.  8. Reassess the overall strategy every 100 rounds based on
# cumulative scores. If consistently underperforming, slightly increase the
# defection probability in step 2.  9. For the first defection and any isolated
# defections (preceded and followed by cooperation), respond with C to account
# for possible noise.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.0  # Base defection probability
          self.defection_streak = 0  # Track mutual defections
          self.switch_to_defection = 0  # Track rounds to defect after 40% defection rule
          self.forgive_round = 15  # Track rounds for random forgiveness
          self.mixed_strategy_start = 980  # Start mixed strategy in the last 20 rounds
          self.defection_increase_rounds = 0  # Track rounds for increased defection probability
          return axl.Action.C  # Start with cooperation
  
      # Helper function to count defections in the last N rounds
      def count_defections(history, n):
          return history[-n:].count(axl.Action.D)
  
      # Helper function to play mixed strategy in the last 20 rounds
      def mixed_strategy():
          if count_defections(opponent.history, 5) >= 3:
              return self._random.random_choice(0.3)  # 30% chance to defect
          else:
              return self._random.random_choice(0.7)  # 70% chance to cooperate
  
      # Rule 9: Respond with C to isolated defections
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # Rule 7: After 5 consecutive mutual defections, attempt to re-establish cooperation
      if self.history[-5:] == [axl.Action.D] * 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          if self.defection_streak < 2:
              self.defection_streak += 1
              return axl.Action.C
          else:
              self.defection_streak = 0  # Reset streak after 2 rounds of cooperation
              return axl.Action.C
  
      # Rule 4: If opponent defected more than 40% in the last 30 rounds, switch to D for 5 rounds
      if len(opponent.history) >= 30 and count_defections(opponent.history, 30) > 12:
          if self.switch_to_defection > 0:
              self.switch_to_defection -= 1
              return axl.Action.D
          else:
              self.switch_to_defection = 5  # Switch to defection for 5 rounds
              return axl.Action.D
  
      # Rule 6: If score difference is more than 30 points after every 50 rounds, increase defection probability
      if len(self.history) % 50 == 0 and len(self.history) > 0:
          if opponent.score - self.score > 30:
              self.defection_increase_rounds = 10
              self.defection_probability = min(self.defection_probability + 0.1, 1.0)
  
      # Apply increased defection probability if active
      if self.defection_increase_rounds > 0:
          self.defection_increase_rounds -= 1
          if self._random.random_choice(self.defection_probability):
              return axl.Action.D
  
      # Rule 3: Every 15 rounds, randomly forgive and play C
      if len(self.history) % 15 == 0:
          if self._random.random_choice(0.5):  # 50% chance to forgive
              return axl.Action.C
  
      # Rule 5: In the last 20 rounds, play a mixed strategy
      if len(self.history) >= self.mixed_strategy_start:
          return mixed_strategy()
  
      # Rule 2: Play C if opponent played C in at least 2 of the last 3 rounds, else play D
      if len(opponent.history) >= 3:
          if count_defections(opponent.history, 3) >= 2:
              return axl.Action.D
          else:
              return axl.Action.C
      else:
          return axl.Action.C  # Default to cooperation if not enough history
  
      # Rule 8: Reassess strategy every 100 rounds and increase defection probability if underperforming
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          if opponent.score > self.score:
              self.defection_probability = min(self.defection_probability + 0.05, 1.0)



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent's actions in the last 3 rounds were mostly cooperative (2 or more C),
# cooperate.    - If the opponent's actions in the last 3 rounds were mostly
# defections (2 or more D), defect.  3. Every 20 rounds, regardless of the
# opponent's recent moves:    - Cooperate to potentially reset a cycle of mutual
# defection.  4. If the opponent has defected for 5 consecutive rounds:    -
# Defect for the next 3 rounds, then return to the base strategy.  5. In the
# last 30 rounds of the game:    - Match the opponent's overall cooperation rate
# from the previous 100 rounds.  6. If your score falls more than 50 points
# behind the opponent's:    - Defect for the next 10 rounds, then reassess and
# return to the base strategy.  7. If mutual cooperation has been maintained for
# 30 consecutive rounds:    - Continue cooperating to maximize mutual benefit.
# 8. Adjust for noise:    - Use a rolling average of the last 5 rounds to
# determine the opponent's likely intended action.    - If an unexpected outcome
# occurs, only change strategy if the pattern persists for 3-4 rounds.  9.
# Adaptive mechanism:    - Every 100 rounds, calculate the opponent's
# cooperation rate.    - If their cooperation rate is above 80%, increase your
# cooperation rate by 10% for the next 100 rounds.    - If their cooperation
# rate is below 20%, decrease your cooperation rate by 10% for the next 100
# rounds.  10. Consider cumulative score:     - If your cumulative score is
# higher than the opponent's, be 10% more likely to cooperate.     - If your
# cumulative score is lower than the opponent's, be 10% more likely to defect.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to calculate cooperation rate
      def cooperation_rate(history):
          return history.count(axl.Action.C) / len(history) if len(history) > 0 else 0
  
      # Helper function to calculate rolling average of last N rounds
      def rolling_average(history, N):
          return history[-N:].count(axl.Action.C) / N if len(history) >= N else 0
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_streak = 0
          self.adaptive_cooperation_rate = 0.5  # Start with 50% cooperation rate
          self.last_adaptive_update = 0
          return axl.Action.C
  
      # Round number
      round_number = len(self.history) + 1
  
      # 1. Start by cooperating in the first round (already handled above)
  
      # 2. Base strategy: check last 3 rounds of opponent's actions
      if round_number > 1:
          if opponent.history[-3:].count(axl.Action.D) >= 2:
              base_action = axl.Action.D
          else:
              base_action = axl.Action.C
      else:
          base_action = axl.Action.C
  
      # 3. Every 20 rounds, cooperate to reset mutual defection
      if round_number % 20 == 0:
          return axl.Action.C
  
      # 4. If opponent defected for 5 consecutive rounds, defect for next 3 rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.defect_streak = 3
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # 5. In the last 30 rounds, match opponent's cooperation rate from last 100 rounds
      if round_number >= 970:
          opponent_coop_rate = cooperation_rate(opponent.history[-100:])
          if self._random.random_choice(opponent_coop_rate):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # 6. If score falls more than 50 points behind, defect for next 10 rounds
      if self.score < opponent.score - 50:
          self.consecutive_defections = 10
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.D
  
      # 7. If mutual cooperation for 30 consecutive rounds, continue cooperating
      if self.history[-30:].count(axl.Action.C) == 30 and opponent.history[-30:].count(axl.Action.C) == 30:
          return axl.Action.C
  
      # 8. Adjust for noise: use rolling average of last 5 rounds
      if rolling_average(opponent.history, 5) >= 0.6:
          base_action = axl.Action.C
      elif rolling_average(opponent.history, 5) <= 0.4:
          base_action = axl.Action.D
  
      # 9. Adaptive mechanism: every 100 rounds, adjust cooperation rate
      if round_number % 100 == 0 and round_number != self.last_adaptive_update:
          opponent_coop_rate = cooperation_rate(opponent.history[:])
          if opponent_coop_rate > 0.8:
              self.adaptive_cooperation_rate = min(1.0, self.adaptive_cooperation_rate + 0.1)
          elif opponent_coop_rate < 0.2:
              self.adaptive_cooperation_rate = max(0.0, self.adaptive_cooperation_rate - 0.1)
          self.last_adaptive_update = round_number
  
      # 10. Consider cumulative score: adjust cooperation probability
      if self.score > opponent.score:
          coop_probability = min(1.0, self.adaptive_cooperation_rate + 0.1)
      else:
          coop_probability = max(0.0, self.adaptive_cooperation_rate - 0.1)
  
      # Final decision based on adjusted cooperation probability
      if self._random.random_choice(coop_probability):
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent's last observed action was
# C, play C with 80% probability and D with 20% probability.  3. If the
# opponent's last observed action was D, play D with 70% probability and C with
# 30% probability.  4. To account for noise, consider the opponent's last three
# moves. If at least two were C, treat it as if their last move was C;
# otherwise, treat it as D.  5. Every 100 rounds, reassess your overall
# strategy:    - If your score is higher, continue with the current approach.
# - If your score is lower, increase the probability of D by 10% for the next
# 100 rounds.  6. In the last 50 rounds, adapt based on the opponent's behavior
# in the previous 50 rounds:    - If they mostly cooperated, increase your C
# probability by 20%.    - If they mostly defected, increase your D probability
# by 20%.  7. If your score is more than 30 points behind, play D for the next 5
# rounds, then return to the main strategy.  8. If you're ahead by more than 50
# points, play C for the next 2 rounds, then return to the main strategy.  9. If
# the opponent has played C for 3 consecutive observed rounds (accounting for
# noise), play C for the next 2 rounds.  10. Every 20 rounds, analyze the
# success rate of your actions:     - If C has been more successful, increase C
# probability by 5% for the next 20 rounds.     - If D has been more successful,
# increase D probability by 5% for the next 20 rounds.  11. For all other
# situations, refer back to steps 2, 3, and 4.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.d_prob = 0.2  # Initial probability of playing D when opponent plays C
          self.c_prob = 0.3  # Initial probability of playing C when opponent plays D
          self.rounds_since_last_reassessment = 0
          self.rounds_since_last_analysis = 0
          self.rounds_since_last_adaptation = 0
          self.consecutive_c_rounds = 0
          self.behind_streak = 0
          self.ahead_streak = 0
          self.last_50_opponent_moves = []
          return axl.Action.C  # Start by playing C
  
      # Helper function to determine the effective last move of the opponent
      def effective_last_move():
          if len(opponent.history) < 3:
              return opponent.history[-1]
          last_three = opponent.history[-3:]
          if last_three.count(axl.Action.C) >= 2:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Update the last 50 moves of the opponent
      if len(opponent.history) >= 50:
          self.last_50_opponent_moves = opponent.history[-50:]
  
      # Check if we are in the last 50 rounds
      if len(self.history) >= 950:
          if self.rounds_since_last_adaptation == 0:
              # Adapt based on the opponent's behavior in the previous 50 rounds
              if self.last_50_opponent_moves.count(axl.Action.C) > 25:
                  self.d_prob = max(0, self.d_prob - 0.2)
              else:
                  self.d_prob = min(1, self.d_prob + 0.2)
              self.rounds_since_last_adaptation = 50
          else:
              self.rounds_since_last_adaptation -= 1
  
      # Reassess strategy every 100 rounds
      if self.rounds_since_last_reassessment == 100:
          if self.score < opponent.score:
              self.d_prob = min(1, self.d_prob + 0.1)
          self.rounds_since_last_reassessment = 0
      else:
          self.rounds_since_last_reassessment += 1
  
      # Analyze success rate every 20 rounds
      if self.rounds_since_last_analysis == 20:
          last_20_self, last_20_opponent = self.total_scores(self.history[-20:], opponent.history[-20:])
          if last_20_self > last_20_opponent:
              self.c_prob = min(1, self.c_prob + 0.05)
          else:
              self.d_prob = min(1, self.d_prob + 0.05)
          self.rounds_since_last_analysis = 0
      else:
          self.rounds_since_last_analysis += 1
  
      # Check if we are behind by more than 30 points
      if opponent.score - self.score > 30:
          if self.behind_streak == 0:
              self.behind_streak = 5
          if self.behind_streak > 0:
              self.behind_streak -= 1
              return axl.Action.D
  
      # Check if we are ahead by more than 50 points
      if self.score - opponent.score > 50:
          if self.ahead_streak == 0:
              self.ahead_streak = 2
          if self.ahead_streak > 0:
              self.ahead_streak -= 1
              return axl.Action.C
  
      # Check if the opponent has played C for 3 consecutive rounds
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          self.consecutive_c_rounds = 2
  
      if self.consecutive_c_rounds > 0:
          self.consecutive_c_rounds -= 1
          return axl.Action.C
  
      # Determine the effective last move of the opponent
      last_move = effective_last_move()
  
      # Play based on the opponent's last move
      if last_move == axl.Action.C:
          return self._random.random_choice(1 - self.d_prob)
      else:
          return self._random.random_choice(self.c_prob)



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 20 rounds,
# play C regardless of the opponent's recent moves to allow for cooperation
# reset.  4. If the opponent has defected more than 70% of the time in the last
# 30 rounds, switch to playing D for the next 5 rounds before returning to the
# main strategy.  5. Gradually increase cooperation: If the opponent has
# cooperated for 10 consecutive rounds, play C for the next 2 rounds regardless
# of their moves.  6. In the last 20 rounds, continue with the main strategy but
# ignore the cooperation reset (step 3).  7. If your score falls below 50% of
# the theoretical maximum cooperative score at any point after round 100, switch
# to a tit-for-tat strategy (copy opponent's last move) for the next 50 rounds
# before reassessing.  8. After any period of mutual defection lasting more than
# 5 rounds, attempt to re-establish cooperation by playing C for 2 consecutive
# rounds.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOP_SCORE = 3
      MAX_COOP_SCORE = COOP_SCORE * 1000  # Maximum cooperative score for 1000 rounds
      DEFECT_THRESHOLD = 0.7
      TIT_FOR_TAT_ROUNDS = 50
      DEFECT_PENALTY_ROUNDS = 5
      COOP_RESET_INTERVAL = 20
      LAST_ROUNDS = 20
      MUTUAL_DEFECT_LIMIT = 5
      COOP_STREAK = 10
      COOP_BONUS_ROUNDS = 2
      SCORE_THRESHOLD = 0.5
  
      # First round: always cooperate
      if self.first_round():
          self.tit_for_tat_mode = None
          self.defect_penalty = 0
          self.coop_bonus = 0
          self.mutual_defect_count = 0
          return axl.Action.C
  
      # Helper function to count defections in the last N rounds
      def count_defections(history, n):
          return history[-n:].count(axl.Action.D)
  
      # Helper function to count cooperations in the last N rounds
      def count_cooperations(history, n):
          return history[-n:].count(axl.Action.C)
  
      # Check if we are in tit-for-tat mode
      if self.tit_for_tat_mode is not None:
          if self.tit_for_tat_mode > 0:
              self.tit_for_tat_mode -= 1
              return opponent.history[-1]  # Tit-for-tat: copy opponent's last move
          else:
              self.tit_for_tat_mode = None  # Exit tit-for-tat mode
  
      # Check if we are in defect penalty mode
      if self.defect_penalty > 0:
          self.defect_penalty -= 1
          return axl.Action.D
  
      # Check if we are in cooperation bonus mode
      if self.coop_bonus > 0:
          self.coop_bonus -= 1
          return axl.Action.C
  
      # Check if we are in the last 20 rounds
      if len(self.history) >= 1000 - LAST_ROUNDS:
          # Ignore cooperation reset in the last 20 rounds
          pass
      else:
          # Every 20 rounds, play C to reset cooperation
          if len(self.history) % COOP_RESET_INTERVAL == 0:
              return axl.Action.C
  
      # Check if the opponent has defected more than 70% of the time in the last 30 rounds
      if len(opponent.history) >= 30 and count_defections(opponent.history, 30) / 30 > DEFECT_THRESHOLD:
          self.defect_penalty = DEFECT_PENALTY_ROUNDS
          return axl.Action.D
  
      # Check if the opponent has cooperated for 10 consecutive rounds
      if count_cooperations(opponent.history, COOP_STREAK) == COOP_STREAK:
          self.coop_bonus = COOP_BONUS_ROUNDS
          return axl.Action.C
  
      # Check if mutual defection has lasted more than 5 rounds
      if count_defections(self.history, MUTUAL_DEFECT_LIMIT) == MUTUAL_DEFECT_LIMIT and \
         count_defections(opponent.history, MUTUAL_DEFECT_LIMIT) == MUTUAL_DEFECT_LIMIT:
          self.mutual_defect_count = 0
          return axl.Action.C  # Attempt to re-establish cooperation
  
      # Main strategy: play C if opponent played C in at least 2 of the last 3 rounds
      if len(opponent.history) >= 3:
          if count_cooperations(opponent.history, 3) >= 2:
              return axl.Action.C
          elif count_defections(opponent.history, 3) >= 2:
              return axl.Action.D
  
      # Check if score falls below 50% of the theoretical maximum cooperative score after round 100
      if len(self.history) > 100:
          max_possible_score = COOP_SCORE * len(self.history)
          if self.score / max_possible_score < SCORE_THRESHOLD:
              self.tit_for_tat_mode = TIT_FOR_TAT_ROUNDS
              return opponent.history[-1]  # Start tit-for-tat mode
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - Cooperate if the opponent's
# last two moves were mostly cooperative (at least one cooperation).    - Defect
# if the opponent's last two moves were both defections.  3. Every 15 rounds,
# cooperate regardless of the opponent's recent moves to allow for recovery of
# cooperative behavior.  4. If the opponent has defected for 4 out of the last 5
# rounds, switch to defecting for the next 3 rounds before returning to the base
# strategy.  5. In the last 20 rounds, play a mixed strategy: cooperate with 70%
# probability and defect with 30% probability.  6. Throughout the game, maintain
# a rolling average of the opponent's cooperation rate over the last 50 moves.
# If this rate falls below 30%, switch to defecting with 80% probability for the
# next 10 rounds before reassessing.  7. If you detect a clear pattern in your
# opponent's play over the last 10 moves (e.g., alternating or repeating
# sequences), adapt your strategy to best respond to this pattern for the next 5
# rounds before returning to the base strategy.  8. Every 100 rounds, compare
# your cumulative score to an expected average score (based on mutual
# cooperation). If you're significantly behind, increase your defection rate by
# 10% for the next 20 rounds.  9. To account for noise, don't immediately
# retaliate for a single defection. Instead, defect only if you observe
# defection in 2 out of the last 3 moves.  10. If your strategy has switched to
# high defection rate due to opponent's behavior, reassess every 10 rounds and
# return to the base strategy if the opponent shows signs of cooperation (3 or
# more cooperative moves in the last 5 rounds).

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0
          self.high_defection_mode = False
          self.high_defection_counter = 0
          self.pattern_adaptation_counter = 0
          self.pattern_detected = False
          self.pattern_moves = []
          return axl.Action.C
  
      # Helper function to detect patterns in the last 10 moves
      def detect_pattern(history):
          if len(history) < 10:
              return False, []
          last_10_moves = history[-10:]
          # Check for alternating pattern
          if all(last_10_moves[i] != last_10_moves[i + 1] for i in range(9)):
              return True, [axl.Action.D if last_10_moves[-1] == axl.Action.C else axl.Action.C]
          # Check for repeating pattern
          if last_10_moves[:5] == last_10_moves[5:]:
              return True, last_10_moves[:5]
          return False, []
  
      # Helper function to calculate cooperation rate over the last N moves
      def cooperation_rate(history, N):
          if len(history) < N:
              return history.cooperations / len(history) if len(history) > 0 else 1
          return history[-N:].count(axl.Action.C) / N
  
      # Base strategy: Cooperate if opponent's last two moves were mostly cooperative
      if len(opponent.history) >= 2:
          if opponent.history[-2:].count(axl.Action.D) == 2:
              base_action = axl.Action.D
          else:
              base_action = axl.Action.C
      else:
          base_action = axl.Action.C
  
      # Rule 3: Every 15 rounds, cooperate
      if len(self.history) % 15 == 0:
          return axl.Action.C
  
      # Rule 4: If opponent defected 4 out of the last 5 rounds, defect for 3 rounds
      if len(opponent.history) >= 5 and opponent.history[-5:].count(axl.Action.D) >= 4:
          self.defect_streak = 3
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Rule 5: In the last 20 rounds, play a mixed strategy
      if self.match_attributes["length"] and len(self.history) >= self.match_attributes["length"] - 20:
          return self._random.random_choice(0.7)
  
      # Rule 6: If opponent's cooperation rate over the last 50 moves is below 30%, defect with 80% probability for 10 rounds
      if cooperation_rate(opponent.history, 50) < 0.3:
          if not self.high_defection_mode:
              self.high_defection_mode = True
              self.high_defection_counter = 10
          if self.high_defection_counter > 0:
              self.high_defection_counter -= 1
              return self._random.random_choice(0.2)
          else:
              self.high_defection_mode = False
  
      # Rule 7: Detect patterns in the last 10 moves and adapt for 5 rounds
      if self.pattern_adaptation_counter == 0:
          self.pattern_detected, self.pattern_moves = detect_pattern(opponent.history)
          if self.pattern_detected:
              self.pattern_adaptation_counter = 5
      if self.pattern_adaptation_counter > 0:
          self.pattern_adaptation_counter -= 1
          return self.pattern_moves[len(self.history) % len(self.pattern_moves)]
  
      # Rule 8: Every 100 rounds, compare cumulative score and adjust defection rate
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          expected_score = len(self.history) * 3  # Expected score if both cooperate
          if self.score < expected_score * 0.9:  # Significantly behind
              self.high_defection_mode = True
              self.high_defection_counter = 20
  
      # Rule 9: Defect if opponent defected in 2 out of the last 3 moves
      if len(opponent.history) >= 3 and opponent.history[-3:].count(axl.Action.D) >= 2:
          return axl.Action.D
  
      # Rule 10: Reassess high defection mode every 10 rounds
      if self.high_defection_mode and len(self.history) % 10 == 0:
          if opponent.history[-5:].count(axl.Action.C) >= 3:
              self.high_defection_mode = False
  
      # Return the base action if no other rule applies
      return base_action



# Here's a revised aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. Keep track of the opponent's last 3
# moves and your own last intended move (before potential noise).  3. If at
# least 2 of the opponent's last 3 moves were defections, defect.  4. If at
# least 2 of the opponent's last 3 moves were cooperations:    a. Defect with
# 70% probability    b. Cooperate with 30% probability  5. Every 50 rounds,
# cooperate once regardless of the opponent's previous moves.  6. In the last 20
# rounds, randomly choose to defect with 90% probability or cooperate with 10%
# probability each round.  7. If your current score is more than 30 points
# behind your opponent's, switch to always defecting for the next 10 rounds.  8.
# If you're ahead by more than 100 points, cooperate for the next 3 rounds.  9.
# After any temporary strategy change (steps 7 or 8), return to the main
# strategy.  10. Throughout the game, if the opponent has cooperated in more
# than 60% of all rounds so far, increase your cooperation probability in step 4
# by 10% (up to a maximum of 50%).  11. If there's uncertainty about the
# opponent's last move due to potential noise, assume they chose the action
# that's most common in their last 10 moves.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.temp_defect_rounds = 0  # For step 7
          self.temp_coop_rounds = 0    # For step 8
          return axl.Action.D
  
      # Helper function to get the most common action in the last 10 moves
      def most_common_action(history):
          last_10 = history[-10:]
          if last_10.count(axl.Action.C) >= last_10.count(axl.Action.D):
              return axl.Action.C
          return axl.Action.D
  
      # Step 2: Track opponent's last 3 moves
      last_3_opponent_moves = opponent.history[-3:]
      last_3_self_moves = self.history[-3:]
  
      # Step 7: If more than 30 points behind, defect for the next 10 rounds
      if self.temp_defect_rounds > 0:
          self.temp_defect_rounds -= 1
          return axl.Action.D
      if self.score < opponent.score - 30:
          self.temp_defect_rounds = 10
          return axl.Action.D
  
      # Step 8: If more than 100 points ahead, cooperate for the next 3 rounds
      if self.temp_coop_rounds > 0:
          self.temp_coop_rounds -= 1
          return axl.Action.C
      if self.score > opponent.score + 100:
          self.temp_coop_rounds = 3
          return axl.Action.C
  
      # Step 5: Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 6: In the last 20 rounds, defect with 90% probability
      if len(self.history) >= 980:
          return self._random.random_choice(0.1)
  
      # Step 3: If at least 2 of the opponent's last 3 moves were defections, defect
      if last_3_opponent_moves.count(axl.Action.D) >= 2:
          return axl.Action.D
  
      # Step 4: If at least 2 of the opponent's last 3 moves were cooperations
      if last_3_opponent_moves.count(axl.Action.C) >= 2:
          # Step 10: Adjust cooperation probability if opponent cooperated more than 60% of the time
          coop_rate = 0.3
          if opponent.history.cooperations / len(opponent.history) > 0.6:
              coop_rate = min(0.5, coop_rate + 0.1)
          return self._random.random_choice(coop_rate)
  
      # Step 11: If there's uncertainty about the opponent's last move, assume the most common action
      if len(opponent.history) >= 10:
          return most_common_action(opponent.history)
  
      # Default to defect if no other condition is met
      return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 20 rounds,
# assess the opponent's behavior:    - If they've cooperated in at least 60% of
# these rounds, play C for the next round regardless of recent moves.    -
# Otherwise, continue with the main strategy.  4. If the opponent has defected
# more than 70% of the time in the last 30 rounds, switch to always playing D
# for the next 15 rounds before reverting to the main strategy.  5. In the last
# 30 rounds of the game:    - If the opponent has cooperated more than 60% of
# the time in the previous 50 rounds, continue with the main strategy.    -
# Otherwise, always play D.  6. If your score is more than 30 points lower than
# your opponent's after every 50 rounds, play D for the next 10 rounds before
# reverting to the main strategy.  7. If you played C but the outcome shows D,
# or vice versa, assume it was due to noise and don't change your strategy based
# on that single round.  8. For the first 5 rounds, forgive any single defection
# and continue playing C to establish a cooperative norm.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0  # Track if we are in a defect streak
          self.main_strategy = True  # Track if we are following the main strategy
          return axl.Action.C  # Start by playing C
  
      # Helper function to count cooperations and defections in the last N rounds
      def count_last_n_moves(history, action, n):
          return history[-n:].count(action)
  
      # Helper function to assess opponent's cooperation rate
      def cooperation_rate(history, n):
          return count_last_n_moves(history, axl.Action.C, n) / n
  
      # Step 2: Main strategy logic
      if self.main_strategy:
          if len(opponent.history) >= 3:
              last_3_defections = count_last_n_moves(opponent.history, axl.Action.D, 3)
              if last_3_defections >= 2:
                  return axl.Action.D
              last_3_cooperations = count_last_n_moves(opponent.history, axl.Action.C, 3)
              if last_3_cooperations >= 2:
                  return axl.Action.C
  
      # Step 3: Every 20 rounds, assess opponent's behavior
      if len(self.history) % 20 == 0:
          if cooperation_rate(opponent.history, 20) >= 0.6:
              return axl.Action.C
  
      # Step 4: If opponent defected more than 70% in the last 30 rounds, switch to D for 15 rounds
      if len(self.history) >= 30 and cooperation_rate(opponent.history, 30) < 0.3:
          self.defect_streak = 15
          self.main_strategy = False
  
      # Handle defect streak
      if self.defect_streak > 0:
          self.defect_streak -= 1
          if self.defect_streak == 0:
              self.main_strategy = True
          return axl.Action.D
  
      # Step 5: In the last 30 rounds of the game
      if self.match_attributes["length"] is not None and len(self.history) >= self.match_attributes["length"] - 30:
          if len(self.history) >= 50 and cooperation_rate(opponent.history, 50) < 0.6:
              return axl.Action.D
  
      # Step 6: If score is more than 30 points lower after every 50 rounds, play D for 10 rounds
      if len(self.history) % 50 == 0:
          my_score, opponent_score = self.total_scores(self.history[-50:], opponent.history[-50:])
          if opponent_score - my_score > 30:
              self.defect_streak = 10
              self.main_strategy = False
  
      # Step 8: For the first 5 rounds, forgive any single defection
      if len(self.history) < 5:
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a revised strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent's action in the previous round appeared to be cooperation, cooperate.
# - If the opponent's action in the previous round appeared to be defection,
# defect.  3. Every 20 rounds, reassess your strategy:    - If your total score
# is higher than or equal to your opponent's, cooperate.    - If your total
# score is lower than your opponent's, defect.  4. If you and your opponent have
# been mutually defecting for 5 consecutive rounds, cooperate in the next round
# to attempt breaking the cycle.  5. Keep a rolling average of the opponent's
# cooperation rate over the last 50 rounds. If this rate is above 70%,
# cooperate; if it's below 30%, defect; otherwise, continue with the current
# strategy.  6. In the last 20 rounds of the game, match your opponent's
# previous action (tit-for-tat).  7. To account for noise:    - If an opponent's
# action seems out of character based on their recent behavior, assume it might
# be due to noise and don't change your strategy for that single round.    -
# Consider an opponent's action over the last 3 rounds rather than just the
# previous round when deciding how to respond.  Follow these rules in the order
# presented, applying the first applicable rule in each round. This strategy
# aims to be more adaptive to noise, opponent behavior, and the game's payoff
# structure while maintaining simplicity.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 0.7
      DEFECTION_THRESHOLD = 0.3
      REASSESS_ROUND = 20
      CYCLE_BREAK_ROUND = 5
      ROLLING_WINDOW = 50
      LAST_ROUNDS = 20
      NOISE_WINDOW = 3
  
      # First round: cooperate
      if self.first_round():
          self.cycle_defections = 0  # Track mutual defections
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, window):
          if len(history) < window:
              window = len(history)
          return history[-window:].count(axl.Action.C) / window if window > 0 else 0
  
      # Helper function to check if mutual defection occurred in the last N rounds
      def mutual_defection(history1, history2, window):
          if len(history1) < window or len(history2) < window:
              return False
          return all(h1 == h2 == axl.Action.D for h1, h2 in zip(history1[-window:], history2[-window:]))
  
      # Rule 6: Last 20 rounds, play tit-for-tat
      if len(self.history) >= 1000 - LAST_ROUNDS:
          return opponent.history[-1]
  
      # Rule 5: Rolling average of opponent's cooperation rate over the last 50 rounds
      opp_coop_rate = cooperation_rate(opponent.history, ROLLING_WINDOW)
      if opp_coop_rate > COOPERATION_THRESHOLD:
          return axl.Action.C
      elif opp_coop_rate < DEFECTION_THRESHOLD:
          return axl.Action.D
  
      # Rule 4: If mutual defection for 5 consecutive rounds, cooperate to break the cycle
      if mutual_defection(self.history, opponent.history, CYCLE_BREAK_ROUND):
          return axl.Action.C
  
      # Rule 3: Every 20 rounds, reassess based on scores
      if len(self.history) % REASSESS_ROUND == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 2: Respond to opponent's last action, considering noise over the last 3 rounds
      if len(opponent.history) >= NOISE_WINDOW:
          recent_opponent_actions = opponent.history[-NOISE_WINDOW:]
          if recent_opponent_actions.count(axl.Action.D) > recent_opponent_actions.count(axl.Action.C):
              return axl.Action.D
          else:
              return axl.Action.C
      else:
          # If less than 3 rounds, just respond to the last action
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. Keep a running score of the opponent's
# cooperation rate over the last 20 rounds.  3. If the opponent's cooperation
# rate is below 30%, defect (D) with 90% probability and cooperate (C) with 10%
# probability.  4. If the opponent's cooperation rate is between 30% and 70%,
# mirror their last move with 80% probability. With 20% probability, choose
# randomly between C and D.  5. If the opponent's cooperation rate is above 70%,
# cooperate (C) with 80% probability and defect (D) with 20% probability.  6.
# Every 50 rounds, reassess the overall cooperation rate of the opponent since
# the beginning of the game. If it's above 60%, cooperate for the next 5 rounds
# regardless of other conditions.  7. If you detect a pattern of alternating C
# and D from the opponent over the last 10 rounds, break the pattern by doing
# the opposite of what the pattern predicts for the next round.  8. In the last
# 20 rounds, if the opponent's overall cooperation rate is above 50%, continue
# with the strategy. If it's below 50%, always defect.  9. To account for noise,
# if an opponent's move seems out of character based on their recent behavior,
# give them the benefit of the doubt once before adjusting your strategy.  10.
# If uncertain about the best action due to conflicting rules, default to
# mirroring the opponent's last move.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          if N == 0:
              return 0
          return history[-N:].count(axl.Action.C) / N
  
      # Helper function to detect alternating pattern in the last N rounds
      def detect_alternating_pattern(history, N):
          if len(history) < N:
              return False
          for i in range(1, N):
              if history[-i] == history[-i-1]:
                  return False
          return True
  
      # Step 1: Start by cooperating in the first round
      if self.first_round():
          self.cooperate_streak = 0  # To track the 5-round cooperation after 50 rounds
          return axl.Action.C
  
      # Step 2: Calculate opponent's cooperation rate over the last 20 rounds
      coop_rate_last_20 = cooperation_rate(opponent.history, 20)
  
      # Step 6: Every 50 rounds, reassess the overall cooperation rate
      if len(self.history) % 50 == 0:
          overall_coop_rate = cooperation_rate(opponent.history, len(opponent.history))
          if overall_coop_rate > 0.6:
              self.cooperate_streak = 5  # Cooperate for the next 5 rounds
  
      # Step 7: Detect alternating pattern in the last 10 rounds
      if detect_alternating_pattern(opponent.history, 10):
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Step 8: In the last 20 rounds, if opponent's overall cooperation rate is below 50%, always defect
      if len(self.history) >= 980:
          overall_coop_rate = cooperation_rate(opponent.history, len(opponent.history))
          if overall_coop_rate < 0.5:
              return axl.Action.D
  
      # Step 9: Give benefit of the doubt if opponent's move seems out of character
      if len(opponent.history) > 1:
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
              if cooperation_rate(opponent.history[:-1], 20) > 0.7:
                  return axl.Action.C
  
      # Step 6: If in the cooperate streak, cooperate for the next 5 rounds
      if self.cooperate_streak > 0:
          self.cooperate_streak -= 1
          return axl.Action.C
  
      # Step 3: If opponent's cooperation rate is below 30%, defect with 90% probability
      if coop_rate_last_20 < 0.3:
          return self._random.random_choice(0.1)
  
      # Step 4: If opponent's cooperation rate is between 30% and 70%, mirror their last move with 80% probability
      if 0.3 <= coop_rate_last_20 <= 0.7:
          if self._random.random_choice(0.8):
              return opponent.history[-1]
          else:
              return self._random.random_choice(0.5)
  
      # Step 5: If opponent's cooperation rate is above 70%, cooperate with 80% probability
      if coop_rate_last_20 > 0.7:
          return self._random.random_choice(0.8)
  
      # Step 10: Default to mirroring the opponent's last move if uncertain
      return opponent.history[-1]



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 15 rounds,
# play C regardless of the opponent's recent moves to signal cooperative intent
# and provide an opportunity for mutual cooperation.  4. If the opponent has
# defected more than 40% of the time in the last 30 rounds, switch to playing D
# for the next 5 rounds before returning to the main strategy.  5. Maintain the
# cooperative approach throughout the game, including the final rounds.  6. If
# your score falls more than 50 points behind your opponent's, increase the
# frequency of D plays to 60% for the next 10 rounds while still allowing for
# cooperation.  7. After any D play, follow up with a C play to allow for quick
# recovery from potential noise-induced defections.  8. Every 50 rounds,
# reassess the opponent's overall cooperation rate. If it's above 70%, increase
# your cooperation rate by 10% for the next 50 rounds.  9. If you play D and the
# opponent plays C, follow up with two C plays to reinforce cooperative
# behavior.  10. In cases of consistent defection from the opponent, use a
# pattern of DCDC plays for 20 rounds to signal willingness to cooperate while
# protecting against exploitation.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.d_streak = 0  # Track how many consecutive D's we have played
          self.dcdc_counter = 0  # Track DCDC pattern
          self.dcdc_mode = False  # Whether we are in DCDC mode
          self.d_mode = False  # Whether we are in D mode (after 40% defection)
          self.d_mode_counter = 0  # Counter for D mode duration
          self.behind_mode = False  # Whether we are in behind mode
          self.behind_mode_counter = 0  # Counter for behind mode duration
          self.coop_boost = 0  # Extra cooperation rate boost
          return axl.Action.C  # Start with cooperation
  
      # Helper function to count defections in the last N rounds
      def count_defections(history, n):
          return history[-n:].count(axl.Action.D)
  
      # Helper function to count cooperations in the last N rounds
      def count_cooperations(history, n):
          return history[-n:].count(axl.Action.C)
  
      # Step 4: If opponent defected more than 40% in the last 30 rounds, enter D mode
      if len(opponent.history) >= 30 and not self.d_mode:
          if count_defections(opponent.history, 30) / 30 > 0.4:
              self.d_mode = True
              self.d_mode_counter = 5
  
      # Step 6: If behind by more than 50 points, enter behind mode
      if not self.behind_mode and len(self.history) > 0:
          if opponent.score - self.score > 50:
              self.behind_mode = True
              self.behind_mode_counter = 10
  
      # Step 8: Every 50 rounds, reassess cooperation rate and adjust
      if len(self.history) % 50 == 0 and len(self.history) > 0:
          if count_cooperations(opponent.history, len(opponent.history)) / len(opponent.history) > 0.7:
              self.coop_boost += 0.1
  
      # Step 10: If in DCDC mode, follow the DCDC pattern
      if self.dcdc_mode:
          if self.dcdc_counter % 2 == 0:
              action = axl.Action.D
          else:
              action = axl.Action.C
          self.dcdc_counter += 1
          if self.dcdc_counter >= 20:
              self.dcdc_mode = False
          return action
  
      # Step 3: Every 15 rounds, play C to signal cooperation
      if len(self.history) % 15 == 0:
          return axl.Action.C
  
      # Step 7: After any D play, follow up with a C play
      if len(self.history) > 0 and self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Step 9: If we played D and opponent played C, follow up with two C plays
      if len(self.history) > 0 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          if len(self.history) > 1 and self.history[-2] == axl.Action.C:
              return axl.Action.C
  
      # Step 2: Main strategy - play C if opponent played C in at least 2 of the last 3 rounds
      if len(opponent.history) >= 3:
          if count_cooperations(opponent.history, 3) >= 2:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 5: Maintain cooperation in final rounds (not explicitly handled, as we always allow for cooperation)
  
      # Step 4: If in D mode, play D for 5 rounds
      if self.d_mode:
          self.d_mode_counter -= 1
          if self.d_mode_counter == 0:
              self.d_mode = False
          return axl.Action.D
  
      # Step 6: If in behind mode, play D 60% of the time for 10 rounds
      if self.behind_mode:
          self.behind_mode_counter -= 1
          if self.behind_mode_counter == 0:
              self.behind_mode = False
          return self._random.random_choice(0.6)
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C



# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent seemed to
# cooperate in the previous round, cooperate.    - If the opponent seemed to
# defect in the previous round, defect.    - Consider an action as "seeming to
# cooperate" if you received a payoff of 3 or 0, and "seeming to defect" if you
# received a payoff of 5 or 1.  3. Every 5 rounds, evaluate recent history:    -
# If the opponent cooperated in at least 3 of the last 5 rounds, cooperate.    -
# Otherwise, defect.  4. Keep a running cooperation rate for your opponent. If
# their cooperation rate drops below 40%, defect for the next 3 rounds before
# reassessing.  5. If you've defected for 5 consecutive rounds, cooperate in the
# next round to test the opponent's response.  6. In the last 20 rounds of the
# game:    - If the opponent's overall cooperation rate is above 60%, cooperate.
# - Otherwise, defect.  7. If at any point your score falls behind your
# opponent's by 15 points or more, defect for the next 3 rounds before returning
# to the main strategy.  8. Every 50 rounds, if your score is within 5 points of
# your opponent's, cooperate for the next round regardless of other conditions.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_for_next_n_rounds = 0
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate opponent's cooperation rate
      def opponent_cooperation_rate():
          return opponent.history.cooperations / len(opponent.history)
  
      # Helper function to evaluate recent history (last 5 rounds)
      def evaluate_recent_history():
          recent_history = opponent.history[-5:]
          return recent_history.count(axl.Action.C) >= 3
  
      # Helper function to determine if the opponent "seemed to cooperate"
      def seemed_to_cooperate(last_round_score):
          return last_round_score in [3, 0]
  
      # Helper function to determine if the opponent "seemed to defect"
      def seemed_to_defect(last_round_score):
          return last_round_score in [5, 1]
  
      # Get the score from the last round
      last_round_score, _ = self.total_scores(self.history[-1:], opponent.history[-1:])
  
      # Step 7: If behind by 15 points or more, defect for the next 3 rounds
      if self.score + 15 <= opponent.score:
          self.defect_for_next_n_rounds = 3
  
      # Step 4: If opponent's cooperation rate drops below 40%, defect for the next 3 rounds
      if opponent_cooperation_rate() < 0.4:
          self.defect_for_next_n_rounds = 3
  
      # Step 5: If defected for 5 consecutive rounds, cooperate to test opponent's response
      if self.consecutive_defections >= 5:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Step 8: Every 50 rounds, if scores are within 5 points, cooperate
      if len(self.history) % 50 == 0 and abs(self.score - opponent.score) <= 5:
          return axl.Action.C
  
      # Step 6: In the last 20 rounds, cooperate if opponent's cooperation rate is above 60%
      if len(self.history) >= 980:
          if opponent_cooperation_rate() > 0.6:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 3: Every 5 rounds, evaluate recent history
      if len(self.history) % 5 == 0:
          if evaluate_recent_history():
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If we are in a phase where we should defect for the next N rounds
      if self.defect_for_next_n_rounds > 0:
          self.defect_for_next_n_rounds -= 1
          self.consecutive_defections += 1
          return axl.Action.D
  
      # Step 2: Cooperate or defect based on the opponent's last round behavior
      if seemed_to_cooperate(last_round_score):
          return axl.Action.C
      elif seemed_to_defect(last_round_score):
          self.consecutive_defections += 1
          return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. Keep track of the opponent's
# cooperation rate over the last 10 rounds.  3. If the opponent's cooperation
# rate is above 70%, cooperate with 80% probability and defect with 20%
# probability.  4. If the opponent's cooperation rate is between 30% and 70%,
# cooperate with 50% probability and defect with 50% probability.  5. If the
# opponent's cooperation rate is below 30%, defect with 80% probability and
# cooperate with 20% probability.  6. Every 100 rounds, reassess your overall
# strategy based on total points:    - If you're behind, increase your defection
# probability by 10% for the next 20 rounds.    - If you're ahead, decrease your
# defection probability by 10% for the next 20 rounds.  7. In the last 50
# rounds, gradually increase your defection probability, reaching 100% in the
# final 10 rounds.  8. If there's a streak of mutual cooperation for more than
# 20 rounds, occasionally defect (10% chance) to test the opponent's response.
# 9. After any action (yours or opponent's) that doesn't match the expected
# outcome, assume it might be due to the 10% noise and don't immediately change
# your strategy.  10. Every 50 rounds, analyze the opponent's response to your
# defections. If they consistently retaliate, slightly increase your cooperation
# probability.  11. Repeat these steps, continuously updating your assessment of
# the opponent's behavior, until the game ends.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_adjustment = 0  # Adjustment to defection probability
          self.defection_increase_rounds = 0  # Rounds left for increased defection
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Helper function to determine the action based on cooperation rate
      def action_based_on_cooperation_rate(coop_rate):
          if coop_rate > 0.7:
              return self._random.random_choice(0.8)  # 80% cooperate, 20% defect
          elif 0.3 <= coop_rate <= 0.7:
              return self._random.random_choice(0.5)  # 50% cooperate, 50% defect
          else:
              return self._random.random_choice(0.2)  # 20% cooperate, 80% defect
  
      # Helper function to adjust defection probability every 100 rounds
      def adjust_defection_probability():
          if len(self.history) % 100 == 0:
              if self.score < opponent.score:
                  self.defection_adjustment += 0.1  # Increase defection probability
                  self.defection_increase_rounds = 20
              elif self.score > opponent.score:
                  self.defection_adjustment = max(0, self.defection_adjustment - 0.1)  # Decrease defection probability
                  self.defection_increase_rounds = 20
  
      # Helper function to increase defection probability in the last 50 rounds
      def increase_defection_in_last_50_rounds():
          rounds_left = 1000 - len(self.history)
          if rounds_left <= 50:
              if rounds_left <= 10:
                  return 1.0  # 100% defection in the last 10 rounds
              else:
                  return (50 - rounds_left) / 50  # Gradually increase defection probability
          return 0
  
      # Helper function to occasionally defect after a long cooperation streak
      def occasional_defection_after_streak():
          if len(self.history) >= 20 and all(x == axl.Action.C for x in self.history[-20:]) and all(
                  x == axl.Action.C for x in opponent.history[-20:]):
              return self._random.random_choice(0.9)  # 10% chance to defect
  
      # Helper function to analyze opponent's response to defections every 50 rounds
      def analyze_opponent_response():
          if len(self.history) % 50 == 0:
              recent_defections = self.history[-50:].count(axl.Action.D)
              if recent_defections > 0:
                  opponent_retaliations = sum(1 for i in range(-50, 0) if self.history[i] == axl.Action.D and opponent.history[i] == axl.Action.D)
                  if opponent_retaliations == recent_defections:
                      self.defection_adjustment = max(0, self.defection_adjustment - 0.05)  # Increase cooperation probability
  
      # Adjust defection probability every 100 rounds
      adjust_defection_probability()
  
      # Analyze opponent's response to defections every 50 rounds
      analyze_opponent_response()
  
      # Calculate cooperation rate over the last 10 rounds
      coop_rate = cooperation_rate(opponent.history, 10)
  
      # Determine base action based on cooperation rate
      action = action_based_on_cooperation_rate(coop_rate)
  
      # Apply defection adjustment if necessary
      if self.defection_increase_rounds > 0:
          self.defection_increase_rounds -= 1
          action = self._random.random_choice(1 - self.defection_adjustment)
  
      # Gradually increase defection probability in the last 50 rounds
      defection_increase = increase_defection_in_last_50_rounds()
      if defection_increase > 0:
          action = self._random.random_choice(1 - defection_increase)
  
      # Occasionally defect after a long cooperation streak
      if occasional_defection_after_streak() == axl.Action.D:
          return axl.Action.D
  
      return action



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 20 rounds,
# play C regardless of the opponent's recent actions to signal cooperative
# intent.  4. If the opponent has played D for 3 consecutive rounds, switch to
# playing D for the next 3 rounds before reverting to the main strategy.  5.
# Gradually increase cooperation: After every 100 rounds of consistent
# cooperation (both players playing C at least 80% of the time), reduce the
# threshold for cooperation by 1 round in step 2, to a minimum of 1 out of the
# last 3 rounds.  6. If your score falls more than 30 points behind your
# opponent's, play D for the next 5 rounds, then revert to the main strategy.
# 7. In the last 20 rounds, mirror the opponent's action from the previous
# round.  8. To account for noise:    - If an unexpected outcome occurs,
# consider it a potential noise event.    - If two consecutive rounds produce
# unexpected outcomes, assume noise and stick to your strategy.    - If three or
# more consecutive rounds produce unexpected outcomes, adapt your strategy as if
# the observed actions were intended.  9. Every 50 rounds, reassess the
# opponent's overall strategy:    - If they've cooperated more than 70% of the
# time, become more cooperative by using a 1 out of 3 threshold for cooperation.
# - If they've defected more than 70% of the time, become more cautious by using
# a 3 out of 3 threshold for cooperation.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_threshold = 2  # Initial threshold for cooperation
          self.defect_streak = 0  # Track opponent's consecutive defections
          self.defect_mode = 0  # Track rounds left in forced defection mode
          self.coop_signal_round = 20  # Next round to signal cooperation
          self.coop_count = 0  # Count of rounds where both players cooperated
          self.last_100_coop = 0  # Count of cooperation in the last 100 rounds
          self.behind_defect_mode = 0  # Track rounds left in forced defection due to score
          return axl.Action.C  # Start with cooperation
  
      # Handle forced defection due to falling behind in score
      if self.behind_defect_mode > 0:
          self.behind_defect_mode -= 1
          return axl.Action.D
  
      # Handle forced defection mode after opponent's 3 consecutive defections
      if self.defect_mode > 0:
          self.defect_mode -= 1
          return axl.Action.D
  
      # Check if we are in the last 20 rounds
      if len(self.history) >= 980:
          return opponent.history[-1]  # Mirror opponent's last action
  
      # Check if it's time to signal cooperation
      if len(self.history) == self.coop_signal_round:
          self.coop_signal_round += 20  # Schedule next signal
          return axl.Action.C
  
      # Check if the opponent has defected for 3 consecutive rounds
      if opponent.history[-3:].count(axl.Action.D) == 3:
          self.defect_mode = 3  # Enter forced defection mode for 3 rounds
          return axl.Action.D
  
      # Check if we are falling behind by more than 30 points
      if self.score < opponent.score - 30:
          self.behind_defect_mode = 5  # Enter forced defection mode for 5 rounds
          return axl.Action.D
  
      # Main strategy: cooperate or defect based on the opponent's last 3 moves
      if opponent.history[-3:].count(axl.Action.D) >= 2:
          return axl.Action.D
      if opponent.history[-3:].count(axl.Action.C) >= self.coop_threshold:
          return axl.Action.C
  
      # Reassess cooperation every 50 rounds
      if len(self.history) % 50 == 0:
          if opponent.history.cooperations / len(opponent.history) > 0.7:
              self.coop_threshold = 1  # Become more cooperative
          elif opponent.history.defections / len(opponent.history) > 0.7:
              self.coop_threshold = 3  # Become more cautious
  
      # Gradually increase cooperation after 100 rounds of consistent cooperation
      if len(self.history) % 100 == 0:
          if self.last_100_coop >= 80:
              self.coop_threshold = max(1, self.coop_threshold - 1)
          self.last_100_coop = 0  # Reset the counter for the next 100 rounds
  
      # Track cooperation in the last 100 rounds
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.last_100_coop += 1
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent seemed to
# cooperate in the previous round, cooperate.    - If the opponent seemed to
# defect in the previous round, defect.    - Consider an action as "seeming to
# cooperate" if you received a payoff of 3 or 0, and "seeming to defect" if you
# received a payoff of 5 or 1.  3. Every 5 rounds, regardless of the opponent's
# previous action:    - If your total score is higher than or equal to the
# opponent's, cooperate.    - If your total score is lower than the opponent's,
# defect.  4. If the opponent has seemed to defect for 3 consecutive rounds,
# defect for the next 2 rounds regardless of their actions.  5. If you're in a
# cycle of mutual defection for more than 5 rounds, cooperate for one round to
# attempt breaking the cycle.  6. In the last 100 rounds of the game:    - If
# the opponent has cooperated more than 60% of the time in the last 50 rounds,
# cooperate.    - Otherwise, defect.  7. If at any point you're unsure about the
# opponent's last action due to possible noise, cooperate.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to determine if the opponent "seemed to cooperate"
      def seemed_to_cooperate(last_round_score):
          return last_round_score in [0, 3]
  
      # Helper function to determine if the opponent "seemed to defect"
      def seemed_to_defect(last_round_score):
          return last_round_score in [1, 5]
  
      # Helper function to check if we are in the last 100 rounds
      def in_last_100_rounds():
          return len(self.history) >= 900
  
      # Helper function to check if we are in a mutual defection cycle
      def in_mutual_defection_cycle():
          return len(self.history) >= 5 and all(
              self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
              for i in range(1, 6)
          )
  
      # Helper function to check if the opponent has defected for 3 consecutive rounds
      def opponent_defected_3_consecutive():
          return len(self.history) >= 3 and all(
              seemed_to_defect(self.total_scores(self.history[-i:], opponent.history[-i:])[0])
              for i in range(1, 4)
          )
  
      # First round: always cooperate
      if self.first_round():
          self.defect_streak = 0  # Track consecutive defections
          return axl.Action.C
  
      # Get the score from the last round
      last_round_score, _ = self.total_scores(self.history[-1:], opponent.history[-1:])
  
      # Rule 4: If the opponent has defected for 3 consecutive rounds, defect for the next 2 rounds
      if opponent_defected_3_consecutive():
          if self.defect_streak < 2:
              self.defect_streak += 1
              return axl.Action.D
          else:
              self.defect_streak = 0  # Reset streak after 2 defections
  
      # Rule 2: Cooperate if the opponent seemed to cooperate, defect if they seemed to defect
      if seemed_to_cooperate(last_round_score):
          action = axl.Action.C
      elif seemed_to_defect(last_round_score):
          action = axl.Action.D
      else:
          action = axl.Action.C  # Default to cooperation if unsure
  
      # Rule 3: Every 5 rounds, compare scores and adjust action
      if len(self.history) % 5 == 0:
          if self.score >= opponent.score:
              action = axl.Action.C
          else:
              action = axl.Action.D
  
      # Rule 5: If in a mutual defection cycle for more than 5 rounds, cooperate to break the cycle
      if in_mutual_defection_cycle():
          action = axl.Action.C
  
      # Rule 6: In the last 100 rounds, cooperate if the opponent has cooperated more than 60% of the time in the last 50 rounds
      if in_last_100_rounds():
          recent_opponent_cooperations = opponent.history[-50:].count(axl.Action.C)
          if recent_opponent_cooperations / 50 > 0.6:
              action = axl.Action.C
          else:
              action = axl.Action.D
  
      return action



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. Keep a running tally of the opponent's
# cooperation rate over the last 20 rounds.  3. If the opponent's cooperation
# rate is below 30%, defect.  4. If the opponent's cooperation rate is between
# 30% and 70%:    a. Cooperate with a probability equal to their cooperation
# rate.    b. Otherwise, defect.  5. If the opponent's cooperation rate is above
# 70%, cooperate.  6. Every 100 rounds, reassess your overall score:    a. If
# you're ahead, become slightly more cooperative (increase cooperation
# probability by 10%).    b. If you're behind, become slightly more aggressive
# (decrease cooperation probability by 10%).  7. In the last 50 rounds,
# gradually increase your defection rate:    a. In rounds 951-975, defect with
# 60% probability.    b. In rounds 976-1000, defect with 80% probability.  8. If
# you've been in a mutual cooperation state for more than 10 rounds,
# occasionally defect with a 5% probability to test the opponent.  9. If your
# action in the previous round was affected by noise (10% chance), and the
# opponent's response seems retaliatory, cooperate in the next round to attempt
# to reset the relationship.  10. For all other situations not covered by the
# above rules, cooperate with 60% probability and defect with 40% probability.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          if N == 0:
              return 1  # Assume full cooperation if no history
          return history[-N:].count(axl.Action.C) / N
  
      # Helper function to adjust cooperation probability based on score difference
      def adjust_cooperation_probability():
          if len(self.history) % 100 == 0 and len(self.history) > 0:
              if self.score > opponent.score:
                  self.cooperation_probability = min(1, self.cooperation_probability + 0.1)
              else:
                  self.cooperation_probability = max(0, self.cooperation_probability - 0.1)
  
      # Helper function to handle the last 50 rounds defection strategy
      def handle_endgame():
          if len(self.history) >= 951:
              if len(self.history) <= 975:
                  return self._random.random_choice(0.6)
              else:
                  return self._random.random_choice(0.8)
          return None
  
      # Helper function to handle mutual cooperation testing
      def mutual_cooperation_test():
          if len(self.history) >= 10 and self.history[-10:] == [axl.Action.C] * 10:
              return self._random.random_choice(0.05)
          return None
  
      # Helper function to handle noise correction
      def noise_correction():
          if len(self.history) > 1 and self.history[-1] != self.history[-2]:
              if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
                  return axl.Action.C
          return None
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_probability = 0.6
          return axl.Action.C
  
      # Adjust cooperation probability every 100 rounds
      adjust_cooperation_probability()
  
      # Handle the last 50 rounds defection strategy
      endgame_action = handle_endgame()
      if endgame_action is not None:
          return endgame_action
  
      # Handle mutual cooperation testing
      mutual_coop_action = mutual_cooperation_test()
      if mutual_coop_action is not None:
          return mutual_coop_action
  
      # Handle noise correction
      noise_action = noise_correction()
      if noise_action is not None:
          return noise_action
  
      # Calculate opponent's cooperation rate over the last 20 rounds
      opponent_coop_rate = cooperation_rate(opponent.history, 20)
  
      # Apply the main strategy based on opponent's cooperation rate
      if opponent_coop_rate < 0.3:
          return axl.Action.D
      elif 0.3 <= opponent_coop_rate <= 0.7:
          return self._random.random_choice(opponent_coop_rate)
      else:
          return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 3 of the last 5 rounds.  3. Maintain a rolling
# average of the opponent's cooperation rate over the last 20 rounds. If this
# rate drops below 60%, switch to playing D for the next 5 rounds.  4. After
# playing D for 5 rounds due to low cooperation rate, attempt to re-establish
# cooperation by playing C for 3 rounds, regardless of the opponent's actions.
# 5. If cooperation is re-established (opponent plays C at least twice in those
# 3 rounds), return to step 2. If not, repeat steps 3 and 4.  6. Every 100
# rounds, if the opponent's overall cooperation rate is above 80%, play C for
# the next 5 rounds regardless of the opponent's actions, to build trust.  7. If
# your cumulative score falls more than 10% below what you'd expect from mutual
# cooperation, become more cautious: change the threshold in step 2 to playing D
# if the opponent played D in at least 2 of the last 4 rounds.  8. In the last
# 50 rounds, gradually increase caution: play D if the opponent played D in any
# of the last 2 rounds.  9. For the final 10 rounds, play C only if the opponent
# has cooperated in all of the previous 5 rounds; otherwise, play D.  10.
# Throughout the game, if you intended to play C but actually played D due to
# noise, play C in the next round to correct for the unintended defection.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_rate_20 = 1.0  # Start with full cooperation rate
          self.low_coop_penalty = 0  # Counter for D rounds after low cooperation
          self.reestablish_coop = 0  # Counter for C rounds to re-establish cooperation
          self.cautious_mode = False  # Flag for cautious mode
          self.last_100_check = 0  # Counter for 100-round checks
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, n):
          return history[-n:].count(axl.Action.C) / n if len(history) >= n else 1.0
  
      # Update cooperation rate over the last 20 rounds
      self.coop_rate_20 = cooperation_rate(opponent.history, 20)
  
      # Step 3: If cooperation rate drops below 60%, play D for 5 rounds
      if self.coop_rate_20 < 0.6 and self.low_coop_penalty == 0:
          self.low_coop_penalty = 5
  
      # Step 4: After playing D for 5 rounds, play C for 3 rounds to re-establish cooperation
      if self.low_coop_penalty > 0:
          self.low_coop_penalty -= 1
          if self.low_coop_penalty == 0:
              self.reestablish_coop = 3
          return axl.Action.D
  
      if self.reestablish_coop > 0:
          self.reestablish_coop -= 1
          if self.reestablish_coop == 0:
              # Check if cooperation was re-established
              if opponent.history[-3:].count(axl.Action.C) >= 2:
                  self.cautious_mode = False  # Reset cautious mode if cooperation is re-established
              else:
                  self.low_coop_penalty = 5  # Repeat the D punishment if cooperation failed
          return axl.Action.C
  
      # Step 6: Every 100 rounds, if opponent's overall cooperation rate is above 80%, play C for 5 rounds
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          overall_coop_rate = cooperation_rate(opponent.history, len(opponent.history))
          if overall_coop_rate > 0.8:
              self.last_100_check = 5
  
      if self.last_100_check > 0:
          self.last_100_check -= 1
          return axl.Action.C
  
      # Step 7: If cumulative score falls more than 10% below mutual cooperation, become more cautious
      mutual_coop_score = len(self.history) * 3  # Expected score if both always cooperated
      if self.score < 0.9 * mutual_coop_score:
          self.cautious_mode = True
  
      # Step 2: Main strategy logic
      if self.cautious_mode:
          # Play D if opponent played D in at least 2 of the last 4 rounds
          if opponent.history[-4:].count(axl.Action.D) >= 2:
              return axl.Action.D
      else:
          # Play C if opponent played C in at least 2 of the last 3 rounds
          if opponent.history[-3:].count(axl.Action.C) >= 2:
              return axl.Action.C
          # Play D if opponent played D in at least 3 of the last 5 rounds
          if opponent.history[-5:].count(axl.Action.D) >= 3:
              return axl.Action.D
  
      # Step 8: In the last 50 rounds, increase caution
      if len(self.history) >= 950:
          if opponent.history[-2:].count(axl.Action.D) >= 1:
              return axl.Action.D
  
      # Step 9: In the final 10 rounds, play C only if opponent cooperated in all of the last 5 rounds
      if len(self.history) >= 990:
          if opponent.history[-5:].count(axl.Action.C) == 5:
              return axl.Action.C
          return axl.Action.D
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - Consider the
# opponent's actions in the last 10 rounds, accounting for potential noise:
# - If the opponent has cooperated in 7 or more of the last 10 rounds,
# cooperate.      - If the opponent has defected in 7 or more of the last 10
# rounds, defect.      - If the opponent's actions are more mixed:        -
# Cooperate if the opponent cooperated more times than they defected.        -
# Defect if the opponent defected more times than they cooperated.        - If
# the number of cooperations and defections are equal, cooperate.  3. Every 100
# rounds, regardless of the opponent's recent actions:    - Cooperate for that
# round to test if a mutual cooperation pattern can be established.    - If the
# opponent also cooperates in this round, continue cooperating for the next 5
# rounds to reinforce the pattern.  4. If your average score per round falls
# below 2:    - Increase the threshold for cooperation to 8 out of the last 10
# rounds for the next 20 rounds.    - After 20 rounds, return to the main
# strategy.  5. Forgiveness mechanism:    - If the opponent has defected for 5
# or more consecutive rounds but then cooperates twice in a row, resume the main
# strategy instead of continuing to defect.  6. For the last 50 rounds of the
# game:    - If the average score is above 2.5, continue with the main strategy.
# - If the average score is between 2 and 2.5, become more cautious: only
# cooperate if the opponent cooperated in 8 or more of the last 10 rounds.    -
# If the average score is below 2, defect.  7. Throughout the game, keep a
# running tally of your score. If your total score ever falls below what you
# would have earned by always defecting (1 point per round), switch to always
# defecting for the remainder of the game.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      TEST_ROUND_INTERVAL = 100
      TEST_ROUND_COOP_PERIOD = 5
      SCORE_THRESHOLD = 2
      HIGH_SCORE_THRESHOLD = 2.5
      LOW_SCORE_THRESHOLD = 2
      COOP_THRESHOLD = 7
      STRICT_COOP_THRESHOLD = 8
      FORGIVENESS_DEFECT_STREAK = 5
      FORGIVENESS_COOP_STREAK = 2
      LAST_ROUNDS = 50
      TOTAL_ROUNDS = 1000
  
      # Helper function to count actions in the last N rounds
      def count_last_n_actions(history, action, n):
          return history[-n:].count(action)
  
      # Helper function to calculate average score per round
      def average_score():
          return self.score / len(self.history) if self.history else 0
  
      # Helper function to check if we are in the last 50 rounds
      def in_last_rounds():
          return len(self.history) >= TOTAL_ROUNDS - LAST_ROUNDS
  
      # First round: cooperate
      if self.first_round():
          self.coop_period = 0  # Initialize cooperation period counter
          self.strict_mode = False  # Initialize strict mode flag
          return COOPERATE
  
      # Every 100 rounds, cooperate to test for mutual cooperation
      if len(self.history) % TEST_ROUND_INTERVAL == 0:
          self.coop_period = TEST_ROUND_COOP_PERIOD  # Set cooperation period
          return COOPERATE
  
      # If in a cooperation period, continue cooperating
      if self.coop_period > 0:
          self.coop_period -= 1
          return COOPERATE
  
      # Check if we are in strict mode (due to low average score)
      if self.strict_mode:
          if len(self.history) >= self.strict_mode_end:
              self.strict_mode = False  # End strict mode after 20 rounds
          else:
              # In strict mode, cooperate only if opponent cooperated 8+ times in last 10 rounds
              if count_last_n_actions(opponent.history, COOPERATE, 10) >= STRICT_COOP_THRESHOLD:
                  return COOPERATE
              else:
                  return DEFECT
  
      # Forgiveness mechanism: if opponent defected 5+ times in a row but cooperated twice in a row, forgive
      if count_last_n_actions(opponent.history, DEFECT, FORGIVENESS_DEFECT_STREAK) == FORGIVENESS_DEFECT_STREAK:
          if count_last_n_actions(opponent.history, COOPERATE, FORGIVENESS_COOP_STREAK) == FORGIVENESS_COOP_STREAK:
              return COOPERATE
  
      # Consider the opponent's actions in the last 10 rounds
      coop_count = count_last_n_actions(opponent.history, COOPERATE, 10)
      defect_count = count_last_n_actions(opponent.history, DEFECT, 10)
  
      if coop_count >= COOP_THRESHOLD:
          return COOPERATE
      elif defect_count >= COOP_THRESHOLD:
          return DEFECT
      elif coop_count > defect_count:
          return COOPERATE
      elif defect_count > coop_count:
          return DEFECT
      else:
          return COOPERATE  # If equal, cooperate
  
      # Check if average score is below 2, enter strict mode for 20 rounds
      if average_score() < SCORE_THRESHOLD:
          self.strict_mode = True
          self.strict_mode_end = len(self.history) + 20
  
      # Last 50 rounds strategy
      if in_last_rounds():
          avg_score = average_score()
          if avg_score > HIGH_SCORE_THRESHOLD:
              return COOPERATE
          elif LOW_SCORE_THRESHOLD <= avg_score <= HIGH_SCORE_THRESHOLD:
              if count_last_n_actions(opponent.history, COOPERATE, 10) >= STRICT_COOP_THRESHOLD:
                  return COOPERATE
              else:
                  return DEFECT
          else:
              return DEFECT
  
      # If total score falls below what would be earned by always defecting, switch to always defecting
      if self.score < len(self.history):
          return DEFECT



# Here's a revised aggressive strategy for the game:  1. Start by defecting (D)
# in the first round.  2. For each round, consider the opponent's last three
# moves instead of just the previous one to account for potential noise:    - If
# at least two of the last three moves were defections, defect.    - If at least
# two of the last three moves were cooperations, defect with 70% probability and
# cooperate with 30% probability.  3. Every 100 rounds, randomly choose to
# cooperate or defect, regardless of the opponent's previous moves. This makes
# the pattern less predictable.  4. In the last 20 rounds of the game, increase
# defection probability to 90% but maintain a 10% chance of cooperation to avoid
# complete predictability.  5. If your current score is more than 30 points
# lower than your opponent's, increase the defection probability to 85% for the
# next 15 rounds.  6. If you're ahead by more than 50 points, slightly increase
# cooperation to 40% probability for the next 10 rounds to balance aggression
# and avoid retaliation.  7. Every 200 rounds, reassess the opponent's overall
# cooperation rate:    - If they've cooperated more than 60% of the time,
# increase your defection probability by 10% for the next 50 rounds.    - If
# they've cooperated less than 40% of the time, decrease your defection
# probability by 10% for the next 50 rounds.  8. Return to the base strategy
# after any temporary adjustments.  9. If the opponent has a clear pattern of
# alternating between cooperation and defection, exploit it by defecting when
# they're expected to cooperate and cooperating when they're expected to defect.
# 10. In case of consecutive mutual defections for more than 10 rounds, attempt
# to break the cycle by cooperating once, then return to the base strategy.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.7  # Base defection probability
          self.adjustment_rounds = 0  # Tracks rounds for temporary adjustments
          self.alternating_pattern = False  # Tracks if opponent alternates
          self.consecutive_defections = 0  # Tracks consecutive mutual defections
          return axl.Action.D  # Start by defecting
  
      # Helper function to check if opponent alternates
      def check_alternating_pattern():
          if len(opponent.history) < 2:
              return False
          return all(opponent.history[i] != opponent.history[i + 1] for i in range(-2, -len(opponent.history), -1))
  
      # Helper function to calculate cooperation rate
      def cooperation_rate():
          return opponent.history.cooperations / len(opponent.history)
  
      # Step 9: Check for alternating pattern
      if check_alternating_pattern():
          self.alternating_pattern = True
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Step 10: Handle consecutive mutual defections
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      if self.consecutive_defections > 10:
          return axl.Action.C  # Break the cycle by cooperating once
  
      # Step 5: Adjust defection probability if behind by more than 30 points
      if self.score < opponent.score - 30:
          self.defection_probability = 0.85
          self.adjustment_rounds = 15
  
      # Step 6: Adjust cooperation probability if ahead by more than 50 points
      if self.score > opponent.score + 50:
          self.defection_probability = 0.6  # 40% cooperation
          self.adjustment_rounds = 10
  
      # Step 7: Reassess opponent's cooperation rate every 200 rounds
      if len(self.history) % 200 == 0:
          coop_rate = cooperation_rate()
          if coop_rate > 0.6:
              self.defection_probability = min(1.0, self.defection_probability + 0.1)
          elif coop_rate < 0.4:
              self.defection_probability = max(0.0, self.defection_probability - 0.1)
          self.adjustment_rounds = 50
  
      # Step 3: Every 100 rounds, randomize action
      if len(self.history) % 100 == 0:
          return self._random.random_choice(0.5)
  
      # Step 4: In the last 20 rounds, increase defection probability to 90%
      if len(self.history) >= 980:
          return self._random.random_choice(0.1)
  
      # Step 2: Base strategy - consider opponent's last 3 moves
      if len(opponent.history) >= 3:
          last_three = opponent.history[-3:]
          if last_three.count(axl.Action.D) >= 2:
              return axl.Action.D
          elif last_three.count(axl.Action.C) >= 2:
              return self._random.random_choice(0.3)
  
      # Step 8: Return to base strategy after temporary adjustments
      if self.adjustment_rounds > 0:
          self.adjustment_rounds -= 1
      else:
          self.defection_probability = 0.7  # Reset to base probability
  
      # Default action based on current defection probability
      return self._random.random_choice(1 - self.defection_probability)



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent's outcome was C in the previous round.    - Play D if the opponent's
# outcome was D in the previous round.  3. Every 5 rounds, play C regardless of
# the opponent's last move to attempt to re-establish cooperation.  4. If the
# opponent's outcomes have been D more than 40% of the time in the last 20
# rounds, switch to playing D for the next 5 rounds before returning to the main
# strategy.  5. In the last 20 rounds of the game, gradually increase the
# probability of playing D: play D with 25% chance for rounds 981-990, 50%
# chance for rounds 991-995, and 75% chance for rounds 996-1000.  6. Throughout
# the game, keep track of unexpected outcomes (when your action doesn't match
# the outcome). If this happens more than 12% of the time in the last 50 rounds,
# assume it's due to noise and don't change your strategy based on the previous
# round's outcome for the next 5 rounds.  7. If mutual defection (D-D outcome)
# has occurred for 3 consecutive rounds, attempt to break the cycle by playing C
# for the next 2 rounds.  8. Adapt to the opponent's pattern: If the opponent's
# outcomes have alternated perfectly between C and D for the last 6 rounds,
# match this pattern for the next 6 rounds.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.unexpected_outcomes = 0
          self.noise_detected = False
          self.noise_counter = 0
          self.defection_streak = 0
          self.alternating_pattern = False
          self.alternating_counter = 0
          return axl.Action.C
  
      # Helper function to check for alternating pattern
      def check_alternating_pattern():
          if len(opponent.history) < 6:
              return False
          return all(opponent.history[-i] != opponent.history[-i-1] for i in range(1, 6))
  
      # Helper function to count defections in the last N rounds
      def count_defections_in_last_n(n):
          return opponent.history[-n:].count(axl.Action.D)
  
      # Helper function to count unexpected outcomes
      def count_unexpected_outcomes():
          return sum(1 for i in range(1, min(50, len(self.history)))
                     if self.history[-i] != opponent.history[-i])
  
      # Check for noise detection
      if len(self.history) >= 50:
          self.unexpected_outcomes = count_unexpected_outcomes()
          if self.unexpected_outcomes / min(50, len(self.history)) > 0.12:
              self.noise_detected = True
              self.noise_counter = 5
          else:
              self.noise_detected = False
  
      # Handle noise detection
      if self.noise_counter > 0:
          self.noise_counter -= 1
          return axl.Action.C
  
      # Check for alternating pattern
      if check_alternating_pattern():
          self.alternating_pattern = True
          self.alternating_counter = 6
  
      # Handle alternating pattern
      if self.alternating_counter > 0:
          self.alternating_counter -= 1
          return opponent.history[-1]
  
      # Check for defection streak
      if len(self.history) >= 3 and all(self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, 4)):
          self.defection_streak = 2
  
      # Handle defection streak
      if self.defection_streak > 0:
          self.defection_streak -= 1
          return axl.Action.C
  
      # Check if we are in the last 20 rounds
      if len(self.history) >= 981:
          if len(self.history) <= 990:
              return self._random.random_choice(0.25)
          elif len(self.history) <= 995:
              return self._random.random_choice(0.50)
          else:
              return self._random.random_choice(0.75)
  
      # Check if defections exceed 40% in the last 20 rounds
      if len(self.history) >= 20 and count_defections_in_last_n(20) / 20 > 0.40:
          return axl.Action.D if len(self.history) % 5 != 0 else axl.Action.C
  
      # Play C every 5 rounds
      if len(self.history) % 5 == 0:
          return axl.Action.C
  
      # Main strategy: mirror opponent's last move
      return opponent.history[-1]



# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - Cooperate if the opponent's
# actions in the last 3 rounds were mostly cooperative (2 or more cooperations).
# - Defect if the opponent's actions in the last 3 rounds were mostly defections
# (2 or more defections).  3. Every 20 rounds, regardless of the opponent's
# recent moves:    - Cooperate to potentially reset a cycle of mutual defection.
# 4. If you notice a consistent pattern in the opponent's play over the last 10
# rounds:    - Attempt to match their pattern for the next 5 rounds, then
# reassess.  5. If the opponent has defected for 7 out of the last 10 rounds:
# - Switch to defecting for the next 10 rounds before reverting to the main
# strategy.  6. In the last 20 rounds of the game:    - Play a mixed strategy:
# cooperate with 70% probability and defect with 30% probability.  7. Throughout
# the game, keep track of the overall cooperation rate of your opponent:    - If
# their cooperation rate falls below 20% over the last 50 rounds, switch to
# always defecting for the next 50 rounds, then reassess.  8. If at any point
# the mutual cooperation rate over the last 100 rounds exceeds 80%:    - Stick
# to cooperation unless the opponent defects twice in a row.  9. Reassess the
# opponent's strategy every 100 rounds and adjust your approach if necessary.
# This revised strategy aims to be more robust against noise, less exploitable,
# and more adaptive to various opponent behaviors.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to check if the opponent has defected in the last N rounds
      def count_defections(history, n):
          return history[-n:].count(axl.Action.D)
  
      # Helper function to check if the opponent has cooperated in the last N rounds
      def count_cooperations(history, n):
          return history[-n:].count(axl.Action.C)
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, n):
          if len(history) < n:
              return count_cooperations(history, len(history)) / len(history)
          return count_cooperations(history, n) / n
  
      # Helper function to detect a consistent pattern in the opponent's last N rounds
      def detect_pattern(history, n):
          if len(history) < n:
              return None
          return history[-n:]
  
      # First round: always cooperate
      if self.first_round():
          self.matching_rounds_left = 0
          self.defect_for_next_50 = None
          self.pattern_to_match = None
          self.defect_for_next_10 = None
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history)
  
      # Rule 3: Every 20 rounds, cooperate to reset potential mutual defection
      if round_number % 20 == 0:
          return axl.Action.C
  
      # Rule 2: Cooperate if the opponent's last 3 rounds were mostly cooperative
      if count_cooperations(opponent.history, 3) >= 2:
          return axl.Action.C
      elif count_defections(opponent.history, 3) >= 2:
          return axl.Action.D
  
      # Rule 5: If the opponent has defected 7 out of the last 10 rounds, defect for the next 10 rounds
      if count_defections(opponent.history, 10) >= 7:
          if not self.defect_for_next_10:
              self.defect_for_next_10 = 10
          if self.defect_for_next_10 > 0:
              self.defect_for_next_10 -= 1
              return axl.Action.D
          else:
              self.defect_for_next_10 = None
  
      # Rule 4: If a consistent pattern is detected in the last 10 rounds, match it for the next 5 rounds
      if self.pattern_to_match is None:
          pattern = detect_pattern(opponent.history, 10)
          if pattern:
              self.pattern_to_match = pattern
              self.matching_rounds_left = 5
      if self.pattern_to_match and self.matching_rounds_left > 0:
          self.matching_rounds_left -= 1
          return self.pattern_to_match[-self.matching_rounds_left - 1]
      if self.matching_rounds_left == 0:
          self.pattern_to_match = None
  
      # Rule 6: In the last 20 rounds, play a mixed strategy (70% cooperate, 30% defect)
      if round_number >= 980:
          return self._random.random_choice(0.7)
  
      # Rule 7: If the opponent's cooperation rate over the last 50 rounds is below 20%, defect for the next 50 rounds
      if cooperation_rate(opponent.history, 50) < 0.2:
          if not self.defect_for_next_50:
              self.defect_for_next_50 = 50
          if self.defect_for_next_50 > 0:
              self.defect_for_next_50 -= 1
              return axl.Action.D
          else:
              self.defect_for_next_50 = None
  
      # Rule 8: If mutual cooperation rate over the last 100 rounds exceeds 80%, cooperate unless opponent defects twice in a row
      if cooperation_rate(self.history, 100) > 0.8 and cooperation_rate(opponent.history, 100) > 0.8:
          if count_defections(opponent.history, 2) < 2:
              return axl.Action.C
  
      # Rule 9: Reassess every 100 rounds (this is a placeholder, as no specific action is defined)
      if round_number % 100 == 0:
          pass
  
      # Default to cooperation if no other rule applies
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. Keep a running tally of the opponent's
# cooperation rate over the last 20 rounds.  3. If the opponent's cooperation
# rate is below 30%, defect.  4. If the opponent's cooperation rate is between
# 30% and 70%:    a. Cooperate with a probability equal to their cooperation
# rate.    b. Otherwise, defect.  5. If the opponent's cooperation rate is above
# 70%, cooperate.  6. Every 10 rounds, reassess your overall strategy:    a. If
# your score is lower than expected, increase your defection probability by 10%
# for the next 10 rounds.    b. If your score is higher than expected, decrease
# your defection probability by 10% for the next 10 rounds.  7. To account for
# noise:    a. If there's a sudden change in the opponent's behavior, wait for 2
# more rounds before adjusting your strategy.    b. Consider the opponent's 3
# most recent moves instead of just the last one when calculating their
# cooperation rate.  8. In the last 20 rounds, gradually increase your defection
# probability, reaching 100% in the final 5 rounds.  9. If you're in a streak of
# 10 or more mutual cooperations, occasionally defect with a 10% probability to
# test the opponent's response.  10. For any situations not covered by the above
# rules, cooperate with a 40% probability and defect with a 60% probability.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.0  # Initial defection probability
          self.last_strategy_reassessment = 0  # Track when we last reassessed strategy
          self.expected_score = 3.0  # Expected score per round (assuming mutual cooperation)
          self.behavior_change_wait = 0  # Counter for waiting after behavior change
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          if N == 0:
              return 1.0  # Assume full cooperation if no history
          return history[-N:].count(axl.Action.C) / N
  
      # Helper function to calculate cooperation rate over the last 3 rounds
      def recent_cooperation_rate(history):
          return cooperation_rate(history, 3)
  
      # Helper function to gradually increase defection probability in the last 20 rounds
      def adjust_defection_probability_for_endgame():
          rounds_left = 1000 - len(self.history)
          if rounds_left <= 20:
              return min(1.0, (20 - rounds_left) / 15)  # Reaches 100% in the last 5 rounds
          return self.defection_probability
  
      # Check for behavior change and wait for 2 rounds before adjusting strategy
      if self.behavior_change_wait > 0:
          self.behavior_change_wait -= 1
      else:
          # Check if there's a sudden change in opponent's behavior
          if len(opponent.history) >= 3:
              recent_rate = recent_cooperation_rate(opponent.history)
              if recent_rate < 0.3 or recent_rate > 0.7:
                  self.behavior_change_wait = 2  # Wait for 2 more rounds before adjusting
  
      # Calculate opponent's cooperation rate over the last 20 rounds
      opponent_coop_rate = cooperation_rate(opponent.history, 20)
  
      # Adjust defection probability based on opponent's cooperation rate
      if opponent_coop_rate < 0.3:
          return axl.Action.D  # Defect if cooperation rate is below 30%
      elif 0.3 <= opponent_coop_rate <= 0.7:
          # Cooperate with probability equal to opponent's cooperation rate
          if self._random.random_choice(opponent_coop_rate):
              return axl.Action.C
          else:
              return axl.Action.D
      else:
          return axl.Action.C  # Cooperate if cooperation rate is above 70%
  
      # Every 10 rounds, reassess strategy based on score
      if len(self.history) % 10 == 0 and len(self.history) > 0:
          average_score = self.score / rounds_played
  
          if average_score < self.expected_score:
              self.defection_probability = min(1.0, self.defection_probability + 0.1)
          else:
              self.defection_probability = max(0.0, self.defection_probability - 0.1)
  
          self.last_strategy_reassessment = len(self.history)
  
      # Adjust defection probability for the endgame
      self.defection_probability = adjust_defection_probability_for_endgame()
  
      # If in a streak of 10 or more mutual cooperations, defect with 10% probability
      if len(self.history) >= 10 and self.history[-10:].count(axl.Action.C) == 10 and opponent.history[-10:].count(axl.Action.C) == 10:
          if self._random.random_choice(0.1):
              return axl.Action.D
  
      # Default action if no other rules apply: cooperate with 40% probability, defect with 60%
      return self._random.random_choice(0.4)



# Here's a revised strategy:  1. Start by playing C in the first round.  2. In
# subsequent rounds:    - Play C if the opponent's outcome was C in the previous
# round.    - Play D if the opponent's outcome was D in the previous round.  3.
# Implement a sliding forgiveness window: After every 5 rounds of consistent
# defection, play C once to test for cooperation.  4. If the opponent has
# defected more than 40% of the time in the last 30 rounds, switch to playing D
# for the next 5 rounds before returning to the main strategy.  5. In the last
# 20 rounds, gradually increase the probability of playing D: start at 20% and
# increase by 4% each round.  6. Throughout the game, track both your
# unexplained actions and the opponent's:    - If either player's unexpected
# actions exceed 12% in the last 50 rounds, assume significant noise.    - In
# high-noise conditions, only switch to D if the opponent's outcome was D twice
# in a row.    - Return to normal strategy if unexpected actions drop below 8%
# for 20 consecutive rounds.  7. If the opponent has cooperated more than 90% of
# the time in the last 50 rounds, play C regardless of their last move to
# maximize mutual cooperation.  8. Every 25 rounds, play a random move to test
# the opponent's strategy and avoid being predictable.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_streak = 0
          self.forced_defection_rounds = 0
          self.unexpected_actions = 0
          self.noise_detected = False
          return axl.Action.C
  
      # Helper function to calculate percentage of defections in the last N rounds
      def defection_percentage(history, rounds):
          if len(history) < rounds:
              return history.defections / len(history)
          return history[-rounds:].count(axl.Action.D) / rounds
  
      # Helper function to calculate unexpected actions
      def unexpected_action_percentage(history, rounds):
          if len(history) < rounds:
              return 0
          unexplained = sum(1 for i in range(-rounds, 0) if history[i] != self.history[i])
          return unexplained / rounds
  
      # Step 2: Play based on opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
          action = axl.Action.D
      else:
          self.defection_streak = 0
          action = axl.Action.C
  
      # Step 3: Sliding forgiveness window
      if self.defection_streak >= 5:
          action = axl.Action.C
          self.defection_streak = 0
  
      # Step 4: Defection rate check over the last 30 rounds
      if defection_percentage(opponent.history, 30) > 0.4:
          self.forced_defection_rounds = 5
  
      if self.forced_defection_rounds > 0:
          self.forced_defection_rounds -= 1
          action = axl.Action.D
  
      # Step 5: Gradually increase defection probability in the last 20 rounds
      if len(self.history) >= 980:
          round_number = len(self.history) - 980
          defection_probability = 0.2 + 0.04 * round_number
          if self._random.random_choice(defection_probability):
              action = axl.Action.D
  
      # Step 6: Noise detection and handling
      if unexpected_action_percentage(self.history, 50) > 0.12 or unexpected_action_percentage(opponent.history, 50) > 0.12:
          self.noise_detected = True
      elif unexpected_action_percentage(self.history, 50) < 0.08 and unexpected_action_percentage(opponent.history, 50) < 0.08:
          self.noise_detected = False
  
      if self.noise_detected:
          if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              action = axl.Action.D
          else:
              action = axl.Action.C
  
      # Step 7: Cooperate if opponent has cooperated more than 90% in the last 50 rounds
      if defection_percentage(opponent.history, 50) < 0.1:
          action = axl.Action.C
  
      # Step 8: Random move every 25 rounds
      if len(self.history) % 25 == 0:
          action = self._random.random_choice(0.5)
  
      return action



# Here's a revised strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent's action in the previous round appeared to be cooperation, cooperate.
# - If the opponent's action in the previous round appeared to be defection,
# defect.  3. Every 5 rounds, regardless of the opponent's previous action:    -
# If your average score per round is higher than or equal to your opponent's,
# cooperate.    - If your average score per round is lower than your opponent's,
# defect.  4. If you've defected for 4 consecutive rounds, cooperate in the next
# round regardless of the opponent's previous action.  5. In the last 20 rounds
# of the game, play the action that has given you the highest average score up
# to that point.  6. If at any point your average score per round falls behind
# your opponent's by 0.5 points or more, defect for the next 3 rounds before
# reverting to the main strategy.  7. Keep a rolling record of the opponent's
# last 10 moves. If this record shows 8 or more of the same action, play the
# action that best responds to that action for the next 3 rounds before
# returning to the main strategy.  8. To account for noise, if an opponent's
# action seems inconsistent with their recent behavior, give them the benefit of
# the doubt once before changing your response.  9. If mutual cooperation has
# been established for 10 or more consecutive rounds, continue cooperating even
# if the opponent appears to defect once, as it may be due to noise.  10.
# Reassess the effectiveness of your strategy every 100 rounds and adjust the
# thresholds for defection or cooperation if necessary.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.last_10_moves = []
          self.coop_streak = 0
          self.defect_streak = 0
          self.reassess_round = 100
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate average score per round
      def average_score(player):
          return player.score / len(player.history) if len(player.history) > 0 else 0
  
      # Helper function to check if mutual cooperation has been established
      def mutual_cooperation():
          return self.coop_streak >= 10
  
      # Update the rolling record of the opponent's last 10 moves
      self.last_10_moves.append(opponent.history[-1])
      if len(self.last_10_moves) > 10:
          self.last_10_moves.pop(0)
  
      # Check if the opponent's last 10 moves are mostly the same
      if self.last_10_moves.count(axl.Action.C) >= 8:
          return axl.Action.D  # Best response to cooperation is defection
      elif self.last_10_moves.count(axl.Action.D) >= 8:
          return axl.Action.C  # Best response to defection is cooperation
  
      # Check if the opponent's last action was cooperation or defection
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0
          self.coop_streak += 1
      else:
          self.consecutive_defections += 1
          self.coop_streak = 0
  
      # Rule 4: If defected for 4 consecutive rounds, cooperate
      if self.consecutive_defections >= 4:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Rule 6: If average score falls behind by 0.5 or more, defect for 3 rounds
      if average_score(self) + 0.5 <= average_score(opponent):
          if self.defect_streak < 3:
              self.defect_streak += 1
              return axl.Action.D
          else:
              self.defect_streak = 0
  
      # Rule 3: Every 5 rounds, compare average scores
      if len(self.history) % 5 == 0:
          if average_score(self) >= average_score(opponent):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 9: If mutual cooperation has been established, continue cooperating
      if mutual_cooperation() and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Rule 5: In the last 20 rounds, play the action with the highest average score
      if len(self.history) >= 980:
          c_history = []
          d_history = []
          for own_move, opp_move in zip(self.history, opponent.history):
              if own_move == axl.Action.C:
                  c_history.append(opp_move)
              else:
                  d_history.append(opp_move)
          coop_score, defect_score = self.total_scores(
              [axl.Action.C] * len(c_history), c_history
          ), self.total_scores([axl.Action.D] * len(d_history), d_history)
          if coop_score[0] / len(c_history) > defect_score[0] / len(d_history):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Default behavior: mirror the opponent's last action
      return opponent.history[-1]



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent's action in the
# previous round was D, defect with 90% probability and cooperate with 10%
# probability.  3. If the opponent's action in the previous round was C,
# cooperate with 70% probability and defect with 30% probability.  4. Every 100
# rounds, analyze the opponent's overall cooperation rate:    - If it's above
# 70%, increase your cooperation probability by 10% for the next 100 rounds.
# - If it's below 30%, decrease your cooperation probability by 10% for the next
# 100 rounds.  5. If your score is more than 50 points behind after 200 rounds,
# slightly increase your defection probability by 5% for the next 100 rounds.
# 6. If you're ahead by more than 100 points after 500 rounds, slightly increase
# your cooperation probability by 5% for the next 100 rounds.  7. In the last 50
# rounds, gradually increase your defection probability, reaching 100% in the
# final 10 rounds.  8. To account for noise, use a rolling average of the last 5
# rounds of the opponent's actions when deciding your next move, rather than
# just the immediately previous round.  9. If there have been 10 consecutive
# rounds of mutual defection, cooperate once to attempt breaking the cycle.  10.
# Adjust all probabilities by +/- 5% randomly every 50 rounds to introduce some
# unpredictability.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_prob = 0.7  # Initial cooperation probability
          self.def_prob = 0.3   # Initial defection probability
          self.adjustment_round = 100  # Next round to adjust probabilities
          self.last_adjustment_round = 0  # Last round when probabilities were adjusted
          self.consecutive_defections = 0  # Track consecutive mutual defections
          self.last_5_opponent_moves = []  # Track last 5 opponent moves
          return axl.Action.C  # Start by cooperating
  
      # Update the last 5 opponent moves
      self.last_5_opponent_moves.append(opponent.history[-1])
      if len(self.last_5_opponent_moves) > 5:
          self.last_5_opponent_moves.pop(0)
  
      # Calculate rolling average of opponent's last 5 moves
      opponent_coop_rate = self.last_5_opponent_moves.count(axl.Action.C) / 5
  
      # Check for mutual defection streak
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      if self.consecutive_defections >= 10:
          return axl.Action.C  # Cooperate to break the cycle
  
      # Adjust probabilities every 100 rounds based on opponent's cooperation rate
      if len(self.history) % 100 == 0 and len(self.history) != self.last_adjustment_round:
          opponent_total_coop_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_total_coop_rate > 0.7:
              self.coop_prob = min(1.0, self.coop_prob + 0.1)
              self.def_prob = max(0.0, 1.0 - self.coop_prob)
          elif opponent_total_coop_rate < 0.3:
              self.coop_prob = max(0.0, self.coop_prob - 0.1)
              self.def_prob = min(1.0, 1.0 - self.coop_prob)
          self.last_adjustment_round = len(self.history)
  
      # Adjust probabilities based on score difference after 200 rounds
      if len(self.history) == 200:
          if self.score < opponent.score - 50:
              self.def_prob = min(1.0, self.def_prob + 0.05)
  
      # Adjust probabilities based on score difference after 500 rounds
      if len(self.history) == 500:
          if self.score > opponent.score + 100:
              self.coop_prob = min(1.0, self.coop_prob + 0.05)
  
      # Gradually increase defection probability in the last 50 rounds
      if len(self.history) >= 950:
          rounds_left = 1000 - len(self.history)
          if rounds_left <= 50:
              self.def_prob = min(1.0, 1.0 - (rounds_left / 50))
  
      # Introduce randomness every 50 rounds
      if len(self.history) % 50 == 0 and len(self.history) != self.last_adjustment_round:
          random_adjustment = self._random.choice([True, False])
          if random_adjustment:
              self.coop_prob = min(1.0, self.coop_prob + 0.05)
              self.def_prob = max(0.0, 1.0 - self.coop_prob)
          else:
              self.coop_prob = max(0.0, self.coop_prob - 0.05)
              self.def_prob = min(1.0, 1.0 - self.coop_prob)
          self.last_adjustment_round = len(self.history)
  
      # Decide next move based on opponent's last action and rolling average
      if opponent_coop_rate >= 0.5:
          return self._random.random_choice(self.coop_prob)
      else:
          return self._random.random_choice(self.def_prob)



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in at least 2 of the last 3 rounds.    - Play D if the
# opponent played D in at least 2 of the last 3 rounds.  3. Every 20 rounds,
# play C regardless of the opponent's recent moves to offer an opportunity for
# cooperation.  4. If the opponent has defected more than 40% of the time in the
# last 30 rounds, switch to playing D for the next 5 rounds, then gradually
# reintroduce cooperation by playing C every other move for the next 5 rounds
# before reverting to the main strategy.  5. In the last 20 rounds, continue
# with the main strategy but become more forgiving: play C if the opponent
# played C in at least 1 of the last 3 rounds.  6. To account for noise:    - If
# an opponent's move seems out of character with their recent pattern, assume it
# might be noise and don't change your strategy based on that single move.    -
# If your own move is different from what you intended (due to noise), continue
# your strategy as if you had played your intended move.  7. Adapt to the
# opponent's pattern:    - If the opponent seems to alternate between C and D,
# match their pattern.    - If the opponent always plays C after you play C,
# increase the frequency of your C plays.  8. If mutual cooperation is
# established for more than 50 consecutive rounds, stick to C unless the
# opponent defects twice in a row.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to count defections in the last N rounds
      def count_defections(history, n):
          return history[-n:].count(axl.Action.D)
  
      # Helper function to count cooperations in the last N rounds
      def count_cooperations(history, n):
          return history[-n:].count(axl.Action.C)
  
      # Helper function to check if the opponent alternates between C and D
      def is_alternating(history):
          if len(history) < 2:
              return False
          return all(history[i] != history[i + 1] for i in range(len(history) - 1))
  
      # Helper function to check if mutual cooperation has been established
      def mutual_cooperation_established():
          return len(self.history) >= 50 and all(
              self.history[-50:] == [axl.Action.C] * 50 and opponent.history[-50:] == [axl.Action.C] * 50
          )
  
      # First round: always cooperate
      if self.first_round():
          self.punishment_rounds = None
          self.reintroduce_cooperation = None
          return axl.Action.C
  
      # Every 20 rounds, play C regardless of the opponent's recent moves
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # If in the last 30 rounds, the opponent defected more than 40% of the time, switch to D for 5 rounds
      if len(self.history) >= 30 and count_defections(opponent.history, 30) / 30 > 0.4:
          if not self.punishment_rounds:
              self.punishment_rounds = 5
          if self.punishment_rounds > 0:
              self.punishment_rounds -= 1
              return axl.Action.D
          elif self.punishment_rounds == 0:
              if not self.reintroduce_cooperation:
                  self.reintroduce_cooperation = 5
              if self.reintroduce_cooperation > 0:
                  self.reintroduce_cooperation -= 1
                  return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D
              else:
                  self.punishment_rounds = None
                  self.reintroduce_cooperation = None
  
      # In the last 20 rounds, become more forgiving
      if self.match_attributes["length"] and len(self.history) >= self.match_attributes["length"] - 20:
          if count_cooperations(opponent.history, 3) >= 1:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Main strategy: play C if opponent played C in at least 2 of the last 3 rounds, otherwise play D
      if len(opponent.history) >= 3:
          if count_cooperations(opponent.history, 3) >= 2:
              return axl.Action.C
          elif count_defections(opponent.history, 3) >= 2:
              return axl.Action.D
  
      # Adapt to opponent's pattern: if alternating, match their pattern
      if is_alternating(opponent.history):
          return axl.Action.C if opponent.history[-1] == axl.Action.D else axl.Action.D
  
      # If mutual cooperation has been established for more than 50 rounds, stick to C unless opponent defects twice in a row
      if mutual_cooperation_established():
          if count_defections(opponent.history, 2) >= 2:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a revised strategy for the game:  1. Start by cooperating in the first
# round.  2. For subsequent rounds:    - Cooperate if the opponent seemed to
# cooperate in at least 2 of the last 3 rounds.    - Defect if the opponent
# seemed to defect in at least 2 of the last 3 rounds.  3. Implement a sliding
# forgiveness window:    - If the opponent's apparent cooperation rate in the
# last 20 rounds is above 70%, cooperate in the next round regardless of their
# recent moves.  4. If the opponent's apparent defection rate exceeds 60% in the
# last 100 rounds, switch to mostly defecting (90% defect, 10% cooperate) for
# the next 20 rounds, then reassess.  5. In the last 50 rounds, base your action
# on the opponent's overall apparent cooperation rate:    - If above 60%,
# continue with the main strategy.    - If below 60%, switch to mostly defecting
# (80% defect, 20% cooperate).  6. Every 100 rounds, evaluate your score:    -
# If your score is more than 15% below the expected average, increase your
# defection rate by 10% for the next 50 rounds, then return to the main
# strategy.  7. Randomly flip your intended action 5% of the time to account for
# noise and to probe the opponent's strategy.  8. If the opponent's strategy
# seems to change significantly (cooperation rate changes by more than 30% over
# 50 rounds), reset your strategy to the initial state and adapt based on their
# new behavior.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      FORGIVENESS_WINDOW = 20
      FORGIVENESS_THRESHOLD = 0.7
      DEFECTIVE_THRESHOLD = 0.6
      DEFECTIVE_WINDOW = 100
      DEFECTIVE_MODE_DURATION = 20
      FINAL_PHASE_THRESHOLD = 50
      FINAL_PHASE_DEFECT_THRESHOLD = 0.6
      FINAL_PHASE_DEFECT_RATE = 0.8
      DEFECTIVE_MODE_DEFECT_RATE = 0.9
      RANDOM_FLIP_RATE = 0.05
      SCORE_EVAL_INTERVAL = 100
      SCORE_DEFICIT_THRESHOLD = 0.15
      SCORE_DEFECT_INCREASE = 0.1
      SCORE_DEFECT_DURATION = 50
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defective_mode = False
          self.defective_mode_counter = 0
          self.score_deficit_mode = False
          self.score_deficit_counter = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate in the last N rounds
      def cooperation_rate(history, n):
          if len(history) < n:
              n = len(history)
          return history[-n:].count(axl.Action.C) / n if n > 0 else 0
  
      # Helper function to calculate defection rate in the last N rounds
      def defection_rate(history, n):
          if len(history) < n:
              n = len(history)
          return history[-n:].count(axl.Action.D) / n if n > 0 else 0
  
      # Step 3: Forgiveness window
      if cooperation_rate(opponent.history, FORGIVENESS_WINDOW) > FORGIVENESS_THRESHOLD:
          return axl.Action.C
  
      # Step 4: Defective mode based on last 100 rounds
      if not self.defective_mode and defection_rate(opponent.history, DEFECTIVE_WINDOW) > DEFECTIVE_THRESHOLD:
          self.defective_mode = True
          self.defective_mode_counter = DEFECTIVE_MODE_DURATION
  
      if self.defective_mode:
          self.defective_mode_counter -= 1
          if self.defective_mode_counter <= 0:
              self.defective_mode = False
          return self._random.random_choice(DEFECTIVE_MODE_DEFECT_RATE)
  
      # Step 5: Final phase strategy
      if len(self.history) >= 1000 - FINAL_PHASE_THRESHOLD:
          if cooperation_rate(opponent.history, len(self.history)) < FINAL_PHASE_DEFECT_THRESHOLD:
              return self._random.random_choice(FINAL_PHASE_DEFECT_RATE)
  
      # Step 6: Score evaluation every 100 rounds
      if len(self.history) % SCORE_EVAL_INTERVAL == 0 and len(self.history) > 0:
          expected_score = len(self.history) * 3  # Expected average score per round is 3
          if self.score < (1 - SCORE_DEFICIT_THRESHOLD) * expected_score:
              self.score_deficit_mode = True
              self.score_deficit_counter = SCORE_DEFECT_DURATION
  
      if self.score_deficit_mode:
          self.score_deficit_counter -= 1
          if self.score_deficit_counter <= 0:
              self.score_deficit_mode = False
          return self._random.random_choice(0.5 + SCORE_DEFECT_INCREASE)
  
      # Step 2: Main strategy based on last 3 rounds
      if len(opponent.history) >= 3:
          last_3_cooperations = opponent.history[-3:].count(axl.Action.C)
          if last_3_cooperations >= 2:
              action = axl.Action.C
          else:
              action = axl.Action.D
      else:
          action = axl.Action.C
  
      # Step 7: Random flip 5% of the time
      if self._random.random() < RANDOM_FLIP_RATE:
          action = action.flip()
  
      # Step 8: Reset strategy if opponent's cooperation rate changes significantly
      if len(opponent.history) >= 50:
          recent_coop_rate = cooperation_rate(opponent.history, 50)
          earlier_coop_rate = cooperation_rate(opponent.history, 100)
          if abs(recent_coop_rate - earlier_coop_rate) > 0.3:
              self.defective_mode = False
              self.defective_mode_counter = 0
              self.score_deficit_mode = False
              self.score_deficit_counter = 0
  
      return action



# Here's a revised aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent's action in the previous
# round was D, defect.  3. If the opponent's action in the previous round was C,
# defect with 90% probability and cooperate with 10% probability.  4. Every 100
# rounds, cooperate once regardless of the opponent's previous move.  5. In the
# last 20 rounds of the game, always defect unless the opponent has cooperated
# in the last 3 rounds.  6. If your current score is more than 30 points behind
# your opponent's, switch to always defecting for the next 30 rounds.  7. If
# you've cooperated for 2 consecutive rounds, defect in the next round
# regardless of the opponent's moves.  8. If the opponent has cooperated for 4
# consecutive rounds, cooperate once, then return to the main strategy.  9. Keep
# track of the opponent's cooperation rate over the last 50 rounds. If it
# exceeds 70%, increase your cooperation probability to 20% when their previous
# move was C.  10. In rounds 400-600, if your score is within 10 points of your
# opponent's, cooperate with 30% probability when their previous move was C.
# 11. Consider the 10% noise factor: if an opponent's move seems out of
# character based on their recent behavior, assume it might be due to noise and
# respond based on their overall trend instead.  Follow these rules in the order
# presented, applying the first applicable rule in each round.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_cooperations = 0
          self.consecutive_opponent_cooperations = 0
          self.always_defect_until = 0
          return axl.Action.D
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          return history[-N:].count(axl.Action.C) / N if len(history) >= N else history.cooperations / len(history)
  
      # Rule 6: If more than 30 points behind, switch to always defecting for 30 rounds
      if self.always_defect_until > 0:
          self.always_defect_until -= 1
          return axl.Action.D
      if self.score < opponent.score - 30:
          self.always_defect_until = 30
          return axl.Action.D
  
      # Rule 7: If cooperated for 2 consecutive rounds, defect
      if self.history[-2:] == [axl.Action.C, axl.Action.C]:
          return axl.Action.D
  
      # Rule 8: If opponent has cooperated for 4 consecutive rounds, cooperate once
      if opponent.history[-4:] == [axl.Action.C, axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      # Rule 9: Track opponent's cooperation rate over the last 50 rounds
      coop_rate = cooperation_rate(opponent.history, 50)
      if coop_rate > 0.7:
          if opponent.history[-1] == axl.Action.C:
              return self._random.random_choice(0.2)
  
      # Rule 10: In rounds 400-600, cooperate with 30% probability if score is within 10 points
      if 400 <= len(self.history) <= 600:
          if abs(self.score - opponent.score) <= 10 and opponent.history[-1] == axl.Action.C:
              return self._random.random_choice(0.3)
  
      # Rule 5: In the last 20 rounds, always defect unless opponent cooperated in the last 3 rounds
      if len(self.history) >= 980:
          if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
              return axl.Action.C
          return axl.Action.D
  
      # Rule 4: Every 100 rounds, cooperate once
      if len(self.history) % 100 == 0:
          return axl.Action.C
  
      # Rule 2: If opponent defected last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 3: If opponent cooperated last round, defect with 90% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.1)
  
      # Default to defecting
      return axl.Action.D



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play C if you played D in the
# previous round (to correct for potential noise).    - If the opponent has
# played D in the previous round, calculate the probability that it was due to
# noise. Play C with 90% probability and D with 10% probability.  3. Keep a
# running average of the opponent's cooperation rate over the last 50 rounds. If
# this rate drops below 60%:    - Play D with a probability equal to (1 -
# opponent's cooperation rate).    - Otherwise, play C.  4. If you've played D
# due to condition 3, return to playing C in the next round unless the
# opponent's cooperation rate remains below 60%.  5. If mutual defection occurs
# for more than 5 consecutive rounds, attempt to break the cycle by playing C
# for the next 2 rounds, regardless of the opponent's actions.  6. Throughout
# the game, calculate the expected payoff of C vs D based on the opponent's
# recent behavior (last 50 rounds). Choose the action with the higher expected
# payoff, but with a 10% chance of choosing the opposite action to account for
# noise and to probe for cooperation.  7. In the last 50 rounds, gradually
# increase the weight given to the immediate payoff versus the long-term
# cooperation. However, don't switch to pure defection to avoid triggering end-
# game defection from the opponent.  8. If at any point the overall cooperation
# rate in the game rises above 80%, consider playing C more frequently (90% of
# the time) to capitalize on the cooperative environment.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Helper function to calculate expected payoff of C and D
      def expected_payoff(last_N):
          if len(self.history) < last_N:
              last_N = len(self.history)
          my_score, opponent_score = self.total_scores(self.history[-last_N:], opponent.history[-last_N:])
          return my_score / last_N if last_N > 0 else 0
  
      # Step 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Play C if opponent played C in the previous round or if I played D in the previous round
      if opponent.history[-1] == axl.Action.C or self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Step 2: If opponent played D in the previous round, play C with 90% probability, D with 10%
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.9)
  
      # Step 3: Calculate opponent's cooperation rate over the last 50 rounds
      coop_rate = cooperation_rate(opponent.history, 50)
  
      if coop_rate < 0.6:
          # Play D with probability (1 - opponent's cooperation rate)
          return self._random.random_choice(coop_rate)
  
      # Step 4: If I played D due to condition 3, return to playing C unless cooperation rate is still below 60%
      if self.history[-1] == axl.Action.D and coop_rate >= 0.6:
          return axl.Action.C
  
      # Step 5: If mutual defection occurred for more than 5 consecutive rounds, play C for the next 2 rounds
      if len(self.history) >= 5 and all(x == axl.Action.D for x in self.history[-5:]) and all(x == axl.Action.D for x in opponent.history[-5:]):
          return axl.Action.C
  
      # Step 6: Calculate expected payoff of C vs D based on the last 50 rounds
      expected_C = expected_payoff(50)
      expected_D = 5 - expected_C  # Since D vs C gives 5 points, and D vs D gives 1 point
  
      # Choose the action with the higher expected payoff, but with a 10% chance of choosing the opposite
      if expected_C > expected_D:
          return self._random.random_choice(0.9)
      else:
          return self._random.random_choice(0.1)
  
      # Step 8: If overall cooperation rate rises above 80%, play C 90% of the time
      overall_coop_rate = cooperation_rate(opponent.history, len(opponent.history))
      if overall_coop_rate > 0.8:
          return self._random.random_choice(0.9)
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a revised strategy for the iterated game:  1. Start by cooperating for
# the first 5 rounds.  2. For subsequent rounds:     a. If the opponent has
# cooperated in at least 4 of the last 5 rounds, cooperate.        b. If the
# opponent has defected in at least 4 of the last 5 rounds, defect.        c. If
# the opponent's actions have been mixed in the last 5 rounds:       - Cooperate
# if you've defected more than the opponent in the last 20 rounds.       -
# Defect if the opponent has defected more than you in the last 20 rounds.
# - If defection counts are equal, cooperate.  3. Every 100 rounds, assess your
# cumulative score:    - If your score is within 10% of the opponent's, continue
# with the current strategy.    - If your score is more than 10% lower, increase
# your defection probability by 10% for the next 50 rounds.    - If your score
# is more than 10% higher, increase your cooperation probability by 10% for the
# next 50 rounds.  4. In the last 20 rounds:    - If your cumulative score is
# higher than the opponent's, continue with the main strategy.    - If your
# cumulative score is lower, increase your defection probability by 20%.  5. To
# account for noise:    - Consider an action as "cooperate" if it occurred at
# least 80% of the time in the relevant period.    - Consider an action as
# "defect" if it occurred at least 80% of the time in the relevant period.    -
# If neither threshold is met, consider the actions as mixed.  6. Reassess the
# effectiveness of your strategy every 200 rounds:    - If your average score
# per round is below 2, become more defensive by increasing the threshold for
# cooperation in step 2a to 5 out of 6 rounds for the next 200 rounds.    - If
# your average score per round is above 3, become more cooperative by decreasing
# the threshold for cooperation in step 2a to 3 out of 5 rounds for the next 200
# rounds.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 4 / 5
      DEFECTION_THRESHOLD = 4 / 5
      NOISE_THRESHOLD = 0.8
      SCORE_DIFF_THRESHOLD = 0.1
      COOPERATION_INCREMENT = 0.1
      DEFECTION_INCREMENT = 0.2
      ROUNDS_TO_ADJUST = 50
      REASSESSMENT_INTERVAL = 200
      FINAL_ROUNDS = 20
      INITIAL_COOPERATION_ROUNDS = 5
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0  # Start with no defection probability
          self.adjustment_rounds = 0  # Track rounds for adjustment period
          self.reassessment_rounds = 0  # Track rounds for reassessment period
          return axl.Action.C  # Cooperate on the first round
  
      # Cooperate for the first 5 rounds
      if len(self.history) < INITIAL_COOPERATION_ROUNDS:
          return axl.Action.C
  
      # Helper function to calculate cooperation/defection ratio in a period
      def cooperation_ratio(history, period):
          return history[-period:].count(axl.Action.C) / period
  
      def defection_ratio(history, period):
          return history[-period:].count(axl.Action.D) / period
  
      # Step 2: Analyze the last 5 rounds
      if len(opponent.history) >= 5:
          last_5_coop_ratio = cooperation_ratio(opponent.history, 5)
          last_5_def_ratio = defection_ratio(opponent.history, 5)
  
          if last_5_coop_ratio >= COOPERATION_THRESHOLD:
              return axl.Action.C
          elif last_5_def_ratio >= DEFECTION_THRESHOLD:
              return axl.Action.D
          else:
              # Mixed behavior: check the last 20 rounds
              if len(self.history) >= 20:
                  my_defections = defection_ratio(self.history, 20)
                  opp_defections = defection_ratio(opponent.history, 20)
  
                  if my_defections > opp_defections:
                      return axl.Action.C
                  elif opp_defections > my_defections:
                      return axl.Action.D
                  else:
                      return axl.Action.C
  
      # Step 3: Every 100 rounds, adjust strategy based on score difference
      if len(self.history) % 100 == 0:
          score_diff = (self.score - opponent.score) / max(opponent.score, 1)
  
          if abs(score_diff) <= SCORE_DIFF_THRESHOLD:
              pass  # Continue with the current strategy
          elif score_diff < -SCORE_DIFF_THRESHOLD:
              self.defection_probability = min(1, self.defection_probability + COOPERATION_INCREMENT)
              self.adjustment_rounds = ROUNDS_TO_ADJUST
          elif score_diff > SCORE_DIFF_THRESHOLD:
              self.defection_probability = max(0, self.defection_probability - COOPERATION_INCREMENT)
              self.adjustment_rounds = ROUNDS_TO_ADJUST
  
      # Step 4: In the last 20 rounds, adjust based on score
      if len(self.history) >= 1000 - FINAL_ROUNDS:
          if self.score < opponent.score:
              self.defection_probability = min(1, self.defection_probability + DEFECTION_INCREMENT)
  
      # Step 5: Handle noise by considering 80% thresholds
      if len(opponent.history) >= 5:
          last_5_coop_ratio = cooperation_ratio(opponent.history, 5)
          last_5_def_ratio = defection_ratio(opponent.history, 5)
  
          if last_5_coop_ratio >= NOISE_THRESHOLD:
              return axl.Action.C
          elif last_5_def_ratio >= NOISE_THRESHOLD:
              return axl.Action.D
  
      # Step 6: Reassess strategy every 200 rounds
      if len(self.history) % REASSESSMENT_INTERVAL == 0:
          avg_score_per_round = self.score / len(self.history)
          if avg_score_per_round < 2:
              COOPERATION_THRESHOLD = 5 / 6  # Become more defensive
          elif avg_score_per_round > 3:
              COOPERATION_THRESHOLD = 3 / 5  # Become more cooperative
  
      # Adjust defection probability if in adjustment period
      if self.adjustment_rounds > 0:
          self.adjustment_rounds -= 1
          return self._random.random_choice(1 - self.defection_probability)
  
      # Default action is to cooperate
      return axl.Action.C



# Here's a revised aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent's action in the previous
# round was D, defect.  3. If the opponent's action in the previous round was C,
# defect with 90% probability and cooperate with 10% probability.  4. Every 100
# rounds, cooperate once regardless of the opponent's previous move to probe for
# potential cooperation.  5. In the last 20 rounds of the game, randomly choose
# between C and D with 70% probability for D and 30% for C to maintain
# unpredictability.  6. If your score is more than 100 points behind your
# opponent's, switch to always defecting for the next 30 rounds.  7. If you're
# ahead by more than 200 points, cooperate for the next 3 rounds to slightly
# reduce aggression.  8. To account for noise, consider the last three moves of
# the opponent instead of just the previous one. If at least two of the last
# three moves were D, treat it as if the opponent defected.  9. Return to the
# main strategy after any temporary changes.  10. Reassess the opponent's
# pattern every 50 rounds and adjust the defection probability in step 3 between
# 80% and 95% based on how often they've cooperated.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_probability = 0.9  # Initial defection probability
          self.defect_streak = 0         # Track rounds of always defecting
          self.coop_streak = 0           # Track rounds of always cooperating
          return axl.Action.D            # Start by defecting
  
      # Helper function to check if opponent defected in at least 2 of the last 3 rounds
      def opponent_defected_recently():
          return opponent.history[-3:].count(axl.Action.D) >= 2
  
      # Helper function to handle the last 20 rounds
      def handle_last_20_rounds():
          if len(self.history) >= 980:
              return self._random.random_choice(0.3)  # 30% chance to cooperate, 70% to defect
          return None
  
      # Helper function to handle every 100th round
      def handle_probe_round():
          if len(self.history) % 100 == 0:
              return axl.Action.C  # Cooperate every 100 rounds to probe
  
      # Helper function to handle score-based adjustments
      def handle_score_adjustments():
          if self.score < opponent.score - 100:
              self.defect_streak = 30  # Switch to always defecting for 30 rounds
          elif self.score > opponent.score + 200:
              self.coop_streak = 3  # Cooperate for the next 3 rounds
  
      # Handle last 20 rounds
      last_20_action = handle_last_20_rounds()
      if last_20_action is not None:
          return last_20_action
  
      # Handle probe round every 100 rounds
      probe_action = handle_probe_round()
      if probe_action is not None:
          return probe_action
  
      # Handle score-based adjustments
      handle_score_adjustments()
  
      # If in a defect streak, always defect
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # If in a cooperation streak, always cooperate
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Reassess defection probability every 50 rounds
      if len(self.history) % 50 == 0:
          coop_rate = opponent.history.cooperations / len(opponent.history)
          self.defect_probability = 0.95 - 0.15 * coop_rate  # Adjust between 80% and 95%
  
      # Main strategy logic
      if opponent_defected_recently():
          return axl.Action.D  # Defect if opponent defected in at least 2 of the last 3 rounds
      else:
          return self._random.random_choice(1 - self.defect_probability)  # Defect with adjusted probability



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    a. If the opponent
# played C in at least 2 of the last 3 rounds, play C.    b. If the opponent
# played D in at least 2 of the last 3 rounds, play D.  3. Every 20 rounds,
# attempt to re-establish cooperation by playing C, regardless of the opponent's
# recent moves.  4. If the opponent has defected more than 40% of the time in
# the last 30 rounds, switch to playing D for the next 5 rounds before returning
# to the main strategy.  5. In the last 20 rounds of the game, gradually
# increase the likelihood of playing D. Start with a 25% chance, increasing by
# 25% every 5 rounds.  6. If your score falls more than 50 points behind your
# opponent's at any point, switch to playing D for the next 10 rounds before
# returning to the main strategy.  7. To account for noise, use a sliding window
# of the last 5 moves to determine the opponent's overall strategy rather than
# reacting to single moves.  8. If both you and your opponent have played D for
# 5 consecutive rounds, attempt to break the cycle by playing C for 2 rounds.
# 9. Adjust your strategy if the opponent seems to be exploiting any predictable
# patterns in your play.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if opponent defected more than 40% in the last 30 rounds
      def opponent_defected_more_than_40_percent():
          if len(opponent.history) < 30:
              return False
          return opponent.history[-30:].count(axl.Action.D) / 30 > 0.4
  
      # Helper function to check if both players have defected for 5 consecutive rounds
      def both_defected_last_5_rounds():
          return len(self.history) >= 5 and all(
              self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, 6)
          )
  
      # Helper function to calculate the probability of defecting in the last 20 rounds
      def defect_probability_in_last_20_rounds():
          rounds_left = 1000 - len(self.history)
          if rounds_left <= 20:
              return min(1.0, 0.25 + (20 - rounds_left) // 5 * 0.25)
          return 0
  
      # First round: always cooperate
      if self.first_round():
          self.defect_streak = 0  # Track defect streaks for rule 6
          self.coop_reset_round = 0  # Track when to reset cooperation every 20 rounds
          return axl.Action.C
  
      # Rule 6: If score difference is more than 50 points, defect for 10 rounds
      if self.score < opponent.score - 50:
          if self.defect_streak < 10:
              self.defect_streak += 1
              return axl.Action.D
          else:
              self.defect_streak = 0  # Reset streak after 10 rounds
  
      # Rule 4: If opponent defected more than 40% in the last 30 rounds, defect for 5 rounds
      if opponent_defected_more_than_40_percent():
          if self.defect_streak < 5:
              self.defect_streak += 1
              return axl.Action.D
          else:
              self.defect_streak = 0  # Reset streak after 5 rounds
  
      # Rule 8: If both defected for 5 consecutive rounds, play C for 2 rounds
      if both_defected_last_5_rounds():
          if self.defect_streak < 2:
              self.defect_streak += 1
              return axl.Action.C
          else:
              self.defect_streak = 0  # Reset streak after 2 rounds
  
      # Rule 5: In the last 20 rounds, increase probability of defecting
      defect_prob = defect_probability_in_last_20_rounds()
      if defect_prob > 0 and self._random.random_choice(defect_prob):
          return axl.Action.D
  
      # Rule 3: Every 20 rounds, attempt to re-establish cooperation
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # Rule 2: Check the last 3 rounds of the opponent
      if len(opponent.history) >= 3:
          last_3 = opponent.history[-3:]
          if last_3.count(axl.Action.C) >= 2:
              return axl.Action.C
          elif last_3.count(axl.Action.D) >= 2:
              return axl.Action.D
  
      # Default to cooperation if no other rule applies
      return axl.Action.C



# Here's a revised strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent's apparent action in the previous round was cooperation, cooperate.
# - If the opponent's apparent action in the previous round was defection,
# defect.  3. Every 5 rounds, regardless of the opponent's previous action:    -
# If your total score is higher than or equal to the opponent's, cooperate.    -
# If your total score is lower than the opponent's, defect.  4. If you've
# defected for 2 consecutive rounds, cooperate in the next round regardless of
# the opponent's previous action.  5. In the last 20 rounds of the game:    - If
# the opponent has cooperated in at least 70% of the previous 50 rounds,
# cooperate.    - Otherwise, defect.  6. If at any point your score falls behind
# the opponent's by 10 points or more, defect for the next 3 rounds before
# returning to the main strategy.  7. Keep a rolling average of the opponent's
# cooperation rate over the last 50 rounds. If this rate drops below 40%,
# increase your defection probability by 20% for the next 10 rounds.  8. To
# account for noise, if your action in the previous round was flipped (10%
# chance), and the opponent's action doesn't match their typical pattern, assume
# it was due to noise and respond based on their overall trend rather than the
# last round.  9. If you detect a consistent pattern in the opponent's play
# (e.g., alternating cooperation and defection), adjust your strategy to exploit
# it for 10 rounds before reassessing.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_for_next_n_rounds = 0
          self.increase_defection_probability = 0
          self.rounds_since_last_pattern_check = 0
          self.last_pattern = None
          return axl.Action.C  # Start by cooperating
  
      # Helper function to detect alternating pattern
      def detect_alternating_pattern(history):
          if len(history) < 4:
              return False
          return all(history[i] != history[i + 1] for i in range(-4, -1))
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, n):
          return history[-n:].count(axl.Action.C) / min(n, len(history))
  
      # Step 6: If score difference is 10 or more, defect for the next 3 rounds
      if self.defect_for_next_n_rounds > 0:
          self.defect_for_next_n_rounds -= 1
          return axl.Action.D
      if self.score < opponent.score - 10:
          self.defect_for_next_n_rounds = 3
          return axl.Action.D
  
      # Step 4: If defected for 2 consecutive rounds, cooperate
      if self.consecutive_defections >= 2:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Step 9: Detect and exploit alternating pattern
      if self.rounds_since_last_pattern_check >= 10:
          if detect_alternating_pattern(opponent.history):
              self.last_pattern = "alternating"
          else:
              self.last_pattern = None
          self.rounds_since_last_pattern_check = 0
      self.rounds_since_last_pattern_check += 1
  
      if self.last_pattern == "alternating":
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Step 7: Adjust defection probability based on cooperation rate
      if self.increase_defection_probability > 0:
          self.increase_defection_probability -= 1
          if self._random.random_choice(0.2):
              return axl.Action.D
  
      # Step 5: In the last 20 rounds, cooperate if opponent cooperated 70% of the last 50 rounds
      if len(self.history) >= 980:
          if cooperation_rate(opponent.history, 50) >= 0.7:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 3: Every 5 rounds, compare scores
      if len(self.history) % 5 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 2: Tit-for-tat logic
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D
      else:
          self.consecutive_defections = 0
          return axl.Action.C



# Here's a revised aggressive strategy for the iterated normal-form game:  1.
# Start by defecting (D) in the first round.  2. For the next 3 rounds, mirror
# the opponent's previous move to establish a baseline.  3. If the opponent has
# defected in 2 out of the last 3 rounds, defect. Otherwise, defect with 70%
# probability and cooperate with 30% probability.  4. If you've defected for 7
# consecutive rounds, cooperate once to test the opponent's response.  5. If the
# opponent has cooperated for 4 consecutive rounds, cooperate for the next 2
# rounds.  6. In the last 20 rounds of the game, defect unless the opponent has
# cooperated in at least 80% of the previous 50 rounds.  7. If your overall
# score is more than 30 points behind your opponent's, increase the defection
# probability to 85% for the next 15 rounds.  8. After any cooperative phase (2
# or more consecutive cooperations) or increased defection phase, return to step
# 3.  9. To account for noise, if an opponent's move seems out of character
# based on their recent history, assume it might be due to noise and don't
# immediately change your strategy.  10. Keep track of the overall cooperation
# rate of your opponent. If it drops below 20% over the last 100 rounds, switch
# to always defecting for the next 20 rounds before reassessing.  11. Reassess
# the effectiveness of your strategy every 100 rounds and adjust the defection
# probability in step 3 by ±5% based on whether your score has improved or
# worsened relative to your opponent.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.defection_probability = 0.7
          self.increased_defection_phase = 0
          self.always_defect_phase = 0
          return axl.Action.D
  
      # Step 2: Mirror the opponent's previous move for the next 3 rounds
      if len(self.history) <= 3:
          return opponent.history[-1]
  
      # Step 3: If the opponent has defected in 2 out of the last 3 rounds, defect
      if opponent.history[-3:].count(axl.Action.D) >= 2:
          action = axl.Action.D
      else:
          # Otherwise, defect with 70% probability and cooperate with 30% probability
          action = self._random.random_choice(self.defection_probability)
  
      # Step 4: If you've defected for 7 consecutive rounds, cooperate once
      if self.consecutive_defections >= 7:
          action = axl.Action.C
  
      # Step 5: If the opponent has cooperated for 4 consecutive rounds, cooperate for the next 2 rounds
      if opponent.history[-4:].count(axl.Action.C) == 4:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.C, axl.Action.C]:
              action = axl.Action.C
  
      # Step 6: In the last 20 rounds, defect unless the opponent has cooperated in at least 80% of the previous 50 rounds
      if len(self.history) >= 980:
          if opponent.history[-50:].count(axl.Action.C) / 50 >= 0.8:
              action = axl.Action.C
          else:
              action = axl.Action.D
  
      # Step 7: If your score is more than 30 points behind, increase defection probability to 85% for the next 15 rounds
      if self.score < opponent.score - 30 and self.increased_defection_phase == 0:
          self.defection_probability = 0.85
          self.increased_defection_phase = 15
  
      if self.increased_defection_phase > 0:
          self.increased_defection_phase -= 1
          action = self._random.random_choice(self.defection_probability)
  
      # Step 8: After any cooperative phase or increased defection phase, return to step 3
      if self.consecutive_cooperations >= 2 or self.increased_defection_phase == 0:
          self.defection_probability = 0.7
  
      # Step 9: Account for noise, don't immediately change strategy if opponent's move seems out of character
      if len(opponent.history) >= 5:
          recent_opponent_moves = opponent.history[-5:]
          if recent_opponent_moves.count(axl.Action.D) == 1 and recent_opponent_moves.count(axl.Action.C) == 4:
              action = self.history[-1]  # Continue with the previous action
  
      # Step 10: Track opponent's cooperation rate, if it drops below 20% over the last 100 rounds, switch to always defecting
      if len(opponent.history) >= 100:
          if opponent.history[-100:].count(axl.Action.C) / 100 < 0.2:
              self.always_defect_phase = 20
  
      if self.always_defect_phase > 0:
          self.always_defect_phase -= 1
          action = axl.Action.D
  
      # Step 11: Reassess strategy every 100 rounds and adjust defection probability
      if len(self.history) % 100 == 0:
          last_100_scores = self.total_scores(self.history[-100:], opponent.history[-100:])
          if last_100_scores[0] < last_100_scores[1]:
              self.defection_probability = min(1.0, self.defection_probability + 0.05)
          else:
              self.defection_probability = max(0.0, self.defection_probability - 0.05)
  
      # Update consecutive cooperation/defection counters
      if action == axl.Action.D:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
      else:
          self.consecutive_cooperations += 1
          self.consecutive_defections = 0
  
      return action



# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D, but with a 20% chance of playing C instead to account
# for possible noise.  3. Every 7-13 rounds (randomly chosen), forgive any
# defections and play C regardless of the opponent's last move.  4. If the
# opponent has defected more than 40% of the time in the last 30 rounds, switch
# to always playing D for the next 5 rounds before returning to the main
# strategy.  5. In the last 20 rounds of the game, gradually increase the
# probability of playing D, starting from 10% and reaching 100% in the final
# round.  6. Keep a rolling average of unexpected outcomes (likely due to noise)
# over the last 50 rounds. If this average exceeds 15%, increase the forgiveness
# rate by playing C with a 30% chance after a defection instead of the usual
# 20%.  7. If your cumulative score falls more than 10% behind the opponent's
# estimated score, become more aggressive by reducing the forgiveness rate to
# 10% for the next 10 rounds.  8. After the first defection, play D with an 80%
# probability in the next round to signal intolerance to defection, then return
# to the main strategy.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.forgive_round = self._random.randint(7, 13)
          self.defection_streak = 0
          self.aggressive_mode = False
          self.aggressive_rounds_left = 0
          self.forgiveness_rate = 0.2
          self.noise_count = 0
          self.noise_threshold = 0.15
          self.noise_window = 50
          self.defection_threshold = 0.4
          self.defection_window = 30
          self.last_defection_round = None
          return axl.Action.C
  
      # Helper function to calculate defection rate in the last N rounds
      def defection_rate(history, rounds):
          return history[-rounds:].count(axl.Action.D) / rounds if len(history) >= rounds else 0
  
      # Helper function to calculate noise rate in the last N rounds
      def noise_rate():
          if len(self.history) < self.noise_window:
              return 0
          expected_outcomes = self.total_scores(self.history[-self.noise_window:], opponent.history[-self.noise_window:])
          actual_outcomes = self.total_scores(self.history[-self.noise_window:], self.history[-self.noise_window:])
          return abs(expected_outcomes[0] - actual_outcomes[0]) / self.noise_window
  
      # Check if we are in the last 20 rounds
      rounds_left = 1000 - len(self.history)
      if rounds_left <= 20:
          defect_probability = min(1, 0.1 + (20 - rounds_left) * 0.045)
          return self._random.random_choice(defect_probability)
  
      # Check if we need to forgive every 7-13 rounds
      if len(self.history) % self.forgive_round == 0:
          self.forgive_round = self._random.randint(7, 13)
          return axl.Action.C
  
      # Check if opponent has defected more than 40% in the last 30 rounds
      if defection_rate(opponent.history, self.defection_window) > self.defection_threshold:
          self.aggressive_mode = True
          self.aggressive_rounds_left = 5
  
      # Handle aggressive mode
      if self.aggressive_mode:
          self.aggressive_rounds_left -= 1
          if self.aggressive_rounds_left == 0:
              self.aggressive_mode = False
          return axl.Action.D
  
      # Handle noise detection and adjust forgiveness rate
      if noise_rate() > self.noise_threshold:
          self.forgiveness_rate = 0.3
      else:
          self.forgiveness_rate = 0.2
  
      # Handle score comparison and adjust forgiveness rate
      if self.score < 0.9 * opponent.score:
          self.forgiveness_rate = 0.1
          self.aggressive_rounds_left = 10
  
      # Handle opponent's last move
      if opponent.history[-1] == axl.Action.D:
          if self.last_defection_round is None:
              self.last_defection_round = len(self.history)
              return self._random.random_choice(0.8)
          return self._random.random_choice(self.forgiveness_rate)
      else:
          return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent's action in the previous round was cooperation, cooperate with 90%
# probability and defect with 10% probability.    - If the opponent's action in
# the previous round was defection, defect with 90% probability and cooperate
# with 10% probability.  3. Every 5 rounds, evaluate the recent history:    - If
# your score in the last 5 rounds is higher than or equal to the opponent's,
# cooperate.    - If your score in the last 5 rounds is lower than the
# opponent's, defect.  4. If you've defected for 3 consecutive rounds, cooperate
# in the next round with 80% probability.  5. In the last 20 rounds of the game:
# - If the opponent has cooperated in at least 3 of the last 5 rounds,
# cooperate.    - Otherwise, defect.  6. If at any point your total score falls
# behind the opponent's by 10 points or more, defect for the next 3 rounds
# before returning to the main strategy.  7. Continuously analyze the opponent's
# last 10 moves:    - If they've cooperated 8 or more times, always cooperate
# for the next 3 rounds.    - If they've defected 8 or more times, always defect
# for the next 3 rounds.    - If they've alternated perfectly, respond with the
# opposite of their last move for the next 3 rounds.  8. Every 50 rounds,
# introduce a completely random action to avoid becoming too predictable.  9. If
# the opponent's strategy seems to change (e.g., a sudden shift from mostly
# cooperation to mostly defection), adapt by giving more weight to their most
# recent 20 moves in your decision-making process for the next 10 rounds.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to calculate the score difference
      def score_difference():
          return self.score - opponent.score
  
      # Helper function to calculate the score in the last N rounds
      def recent_scores(n):
          return self.total_scores(self.history[-n:], opponent.history[-n:])
  
      # Helper function to check if the opponent has alternated perfectly in the last N rounds
      def has_alternated(n):
          return all(self.history[-i] != opponent.history[-i] for i in range(1, n))
  
      # Helper function to check if the opponent has cooperated/defected N or more times in the last M rounds
      def count_recent_actions(action, n, m):
          return opponent.history[-m:].count(action) >= n
  
      # First round: cooperate
      if self.first_round():
          self.defect_for_3 = None
          self.consecutive_defections = 0
          self.adapt_mode = False
          self.adapt_rounds = 0
          return axl.Action.C
  
      # If in adaptation mode, give more weight to the last 20 moves
      if self.adapt_mode:
          self.adapt_rounds -= 1
          if self.adapt_rounds == 0:
              self.adapt_mode = False
          if count_recent_actions(axl.Action.C, 3, 5):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If score difference is -10 or worse, defect for the next 3 rounds
      if score_difference() <= -10:
          if not self.defect_for_3:
              self.defect_for_3 = 3
          if self.defect_for_3 > 0:
              self.defect_for_3 -= 1
              return axl.Action.D
          else:
              self.defect_for_3 = None
  
      # Every 50 rounds, introduce a random action
      if len(self.history) % 50 == 0:
          return self._random.random_choice(0.5)
  
      # Every 5 rounds, evaluate the recent history
      if len(self.history) % 5 == 0:
          my_score, opp_score = recent_scores(5)
          if my_score >= opp_score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If defected for 3 consecutive rounds, cooperate with 80% probability
      if self.consecutive_defections >= 3:
          self.consecutive_defections = 0
          return self._random.random_choice(0.8)
  
      # Analyze the opponent's last 10 moves
      if len(self.history) >= 10:
          if count_recent_actions(axl.Action.C, 8, 10):
              return axl.Action.C
          if count_recent_actions(axl.Action.D, 8, 10):
              return axl.Action.D
          if has_alternated(10):
              return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # In the last 20 rounds of the game
      if len(self.history) >= 980:
          if count_recent_actions(axl.Action.C, 3, 5):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Main strategy: respond based on the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.9)
      else:
          self.consecutive_defections += 1
          return self._random.random_choice(0.1)



# Here's a revised aggressive strategy for the iterated normal-form game:  1.
# Start by defecting (D) in the first round.  2. Keep a running tally of the
# opponent's apparent cooperation rate, adjusting for the 10% noise factor. If
# this rate falls below 40%, always defect.  3. If the opponent has cooperated
# in the last 2-4 rounds (randomly chosen each time to be less predictable),
# cooperate once, then return to defecting.  4. If the opponent's last apparent
# action was to cooperate, defect with 90% probability and cooperate with 10%
# probability.  5. If the opponent's last apparent action was to defect, defect
# with 95% probability and cooperate with 5% probability.  6. In the last 100
# rounds, if the opponent's cooperation rate is above 70%, alternate between
# cooperating and defecting. Otherwise, always defect.  7. Every 50 rounds,
# reassess the strategy's performance. If the average score per round is below
# 2, increase the probability of cooperation in steps 4 and 5 by 5% (up to a
# maximum of 20% and 10% respectively).  8. If a clear pattern emerges in the
# opponent's play (e.g., tit-for-tat, always cooperate), adjust the strategy to
# exploit it.  9. If none of the above conditions are met, defect.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_rate = 0
          self.rounds_since_last_coop = 0
          self.last_reassessment = 0
          self.coop_prob = 0.1  # Initial cooperation probability after opponent's cooperation
          self.def_prob = 0.05  # Initial cooperation probability after opponent's defection
          return axl.Action.D  # Start by defecting
  
      # Update cooperation rate, adjusting for 10% noise
      total_rounds = len(opponent.history)
      opponent_cooperations = opponent.history.cooperations
      self.cooperation_rate = opponent_cooperations / total_rounds
  
      # Step 2: If opponent's cooperation rate falls below 40%, always defect
      if self.cooperation_rate < 0.4:
          return axl.Action.D
  
      # Step 3: If opponent has cooperated in the last 2-4 rounds, cooperate once
      coop_window = self._random.randint(2, 4)
      if opponent.history[-coop_window:].count(axl.Action.C) == coop_window:
          self.rounds_since_last_coop = 0
          return axl.Action.C
  
      # Step 4 & 5: Adjust cooperation/defection probabilities based on opponent's last action
      if opponent.history[-1] == axl.Action.C:
          if self._random.random_choice(self.coop_prob):
              return axl.Action.C
          else:
              return axl.Action.D
      elif opponent.history[-1] == axl.Action.D:
          if self._random.random_choice(self.def_prob):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 6: In the last 100 rounds, alternate if cooperation rate is above 70%
      if total_rounds >= 900:
          if self.cooperation_rate > 0.7:
              if total_rounds % 2 == 0:
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              return axl.Action.D
  
      # Step 7: Reassess every 50 rounds and adjust probabilities if average score is below 2
      if total_rounds % 50 == 0 and total_rounds != self.last_reassessment:
          self.last_reassessment = total_rounds
          avg_score = self.score / total_rounds
          if avg_score < 2:
              self.coop_prob = min(self.coop_prob + 0.05, 0.2)
              self.def_prob = min(self.def_prob + 0.05, 0.1)
  
      # Step 8: Detect clear patterns (e.g., tit-for-tat, always cooperate)
      if opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          if opponent.history[-3] == axl.Action.C:
              return axl.Action.D  # Exploit always cooperate
  
      # Step 9: Default to defecting if no other conditions are met
      return axl.Action.D



# Here's a revised strategy:  1. Start by playing C in the first round.  2. In
# subsequent rounds:    - Play C if the opponent played C in at least 2 of the
# last 3 rounds.    - Play D if the opponent played D in at least 2 of the last
# 3 rounds.  3. Maintain a rolling average of the opponent's cooperation rate
# over the last 20 rounds.    - If this rate falls below 60%, play D for the
# next 5 rounds before reverting to the main strategy.  4. If you played D in
# the previous round, play C in the next round unless the opponent's recent
# behavior (as per rule 2) suggests playing D.  5. Ignore the last 3% of the
# game (30 rounds in this case) when considering end-game strategies. Continue
# with the main strategy until the end.  6. Every 100 rounds, evaluate your
# cumulative score:    - If you're significantly behind (more than 50 points),
# become slightly more defensive by requiring the opponent to play C in 3 of the
# last 4 rounds to trigger your cooperation.    - If you're significantly ahead
# (more than 50 points), become slightly more forgiving by only requiring the
# opponent to play C in 2 of the last 4 rounds to trigger your cooperation.  7.
# If the overall cooperation rate (for both players combined) falls below 40%
# for an extended period (e.g., 100 rounds), switch to a tit-for-tat strategy:
# play whatever the opponent played in the previous round.  8. Every 50 rounds,
# attempt a "cooperation reset" by playing C for two consecutive rounds,
# regardless of the opponent's recent actions, then return to the main strategy.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_reset_counter = 0  # Counter for cooperation reset every 50 rounds
          self.defensive_mode = False  # Flag for defensive mode when behind
          self.tit_for_tat_mode = False  # Flag for tit-for-tat mode
          self.d_streak = 0  # Counter for playing D for 5 rounds after low cooperation rate
          return axl.Action.C  # Start by playing C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, n):
          return history[-n:].count(axl.Action.C) / n if len(history) >= n else 1
  
      # Helper function to check if we are in the last 3% of the game
      def in_endgame():
          return len(self.history) >= 970  # 1000 * 0.97 = 970
  
      # Rule 7: Check if overall cooperation rate falls below 40% for 100 rounds
      if len(self.history) >= 100:
          overall_coop_rate = (self.history[-100:].count(axl.Action.C) + opponent.history[-100:].count(axl.Action.C)) / (2 * 100)
          if overall_coop_rate < 0.4:
              self.tit_for_tat_mode = True
  
      # Rule 6: Every 100 rounds, adjust strategy based on score difference
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          if self.score - opponent.score > 50:
              self.defensive_mode = False  # More forgiving
          elif opponent.score - self.score > 50:
              self.defensive_mode = True  # More defensive
  
      # Rule 8: Every 50 rounds, attempt a cooperation reset
      if len(self.history) % 50 == 0 and len(self.history) > 0:
          self.coop_reset_counter = 2  # Play C for two consecutive rounds
  
      # If in tit-for-tat mode, play the opponent's last move
      if self.tit_for_tat_mode:
          return opponent.history[-1]
  
      # If in cooperation reset mode, play C for two rounds
      if self.coop_reset_counter > 0:
          self.coop_reset_counter -= 1
          return axl.Action.C
  
      # Rule 3: Maintain a rolling average of opponent's cooperation rate over the last 20 rounds
      if len(opponent.history) >= 20 and cooperation_rate(opponent.history, 20) < 0.6:
          if self.d_streak < 5:
              self.d_streak += 1
              return axl.Action.D
          else:
              self.d_streak = 0  # Reset after 5 rounds of D
  
      # Rule 2: Main strategy based on opponent's last 3 rounds
      if len(opponent.history) >= 3:
          if opponent.history[-3:].count(axl.Action.D) >= 2:
              return axl.Action.D
          elif opponent.history[-3:].count(axl.Action.C) >= 2:
              return axl.Action.C
  
      # Rule 4: If I played D last round, play C unless opponent's recent behavior suggests D
      if self.history[-1] == axl.Action.D:
          if len(opponent.history) >= 3 and opponent.history[-3:].count(axl.Action.D) >= 2:
              return axl.Action.D
          return axl.Action.C
  
      # Rule 5: Ignore the last 3% of the game for end-game strategies
      if in_endgame():
          return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
  
      # Default to cooperation if no other rule applies
      return axl.Action.C



# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - Cooperate if the opponent
# seemed to cooperate in at least 2 of the last 3 rounds.    - Defect if the
# opponent seemed to defect in at least 2 of the last 3 rounds.  3. Every 15
# rounds, regardless of the opponent's recent moves:    - Cooperate to
# potentially reset a cycle of mutual defection.  4. If you notice a pattern of
# the opponent seeming to defect in at least 7 out of 10 consecutive rounds:
# - Switch to defecting for the next 3 rounds.    - Then return to the base
# strategy (points 2 and 3).  5. If you notice a pattern of the opponent seeming
# to cooperate in at least 8 out of 10 consecutive rounds:    - Defect for 1
# round to test the opponent's response.    - If they seem to cooperate, defect
# one more time.    - Then return to the base strategy (points 2 and 3).  6.
# Every 50 rounds, evaluate your average score:    - If it's below 2, become
# more prone to defection by requiring 3 out of 4 cooperative rounds from the
# opponent to cooperate yourself.    - If it's above 3, become more prone to
# cooperation by only requiring 1 out of 2 cooperative rounds from the opponent
# to cooperate yourself.  7. In the last 20 rounds of the game:    - Play tit-
# for-tat (copy the opponent's previous move) to balance between cooperation and
# defection.  This strategy aims to be more robust against noise, adapt to the
# opponent's behavior over time, and balance cooperation and defection based on
# the game's progress and overall performance.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
  
      # Helper function to count opponent's cooperations/defections in the last N rounds
      def count_last_n_moves(n, action):
          return opponent.history[-n:].count(action)
  
      # Helper function to check if we are in the last 20 rounds
      def in_last_20_rounds():
          return len(self.history) >= 980
  
      # Helper function to evaluate average score every 50 rounds
      def evaluate_average_score():
          if len(self.history) % 50 == 0 and len(self.history) > 0:
              avg_score = self.score / len(self.history)
              return avg_score
          return None
  
      # First round: Cooperate
      if self.first_round():
          self.defect_streak = None
          self.test_defection = None
          self.coop_threshold = 2  # Default threshold for cooperation
          return COOPERATE
  
      # Step 6: Adjust strategy based on average score every 50 rounds
      avg_score = evaluate_average_score()
      if avg_score is not None:
          if avg_score < 2:
              self.coop_threshold = 3  # More prone to defection
          elif avg_score > 3:
              self.coop_threshold = 1  # More prone to cooperation
  
      # Step 7: In the last 20 rounds, play Tit-for-Tat
      if in_last_20_rounds():
          return opponent.history[-1]
  
      # Step 4: If opponent defects in 7 out of the last 10 rounds, defect for 3 rounds
      if count_last_n_moves(10, DEFECT) >= 7:
          if not self.defect_streak:
              self.defect_streak = 3
          if self.defect_streak > 0:
              self.defect_streak -= 1
              return DEFECT
          else:
              self.defect_streak = None  # Reset after 3 rounds
  
      # Step 5: If opponent cooperates in 8 out of the last 10 rounds, test with defection
      if count_last_n_moves(10, COOPERATE) >= 8:
          if not self.test_defection:
              self.test_defection = 2  # Defect for 2 rounds to test
          if self.test_defection > 0:
              self.test_defection -= 1
              return DEFECT
          else:
              self.test_defection = None  # Reset after test
  
      # Step 3: Every 15 rounds, cooperate to reset potential defection cycles
      if len(self.history) % 15 == 0:
          return COOPERATE
  
      # Step 2: Base strategy - cooperate if opponent cooperated in at least coop_threshold of the last 3 rounds
      if count_last_n_moves(3, COOPERATE) >= self.coop_threshold:
          return COOPERATE
      else:
          return DEFECT
