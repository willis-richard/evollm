import axelrod as axl

from evollm.common import Attitude, auto_update_score, LLM_Strategy

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to encourage cooperation.  2. If the opponent
# played C in the previous round, play C with 80% probability and D with 20%
# probability.  3. If the opponent played D in the previous round, play D with
# 60% probability and C with 40% probability.  4. Keep track of the opponent's
# cooperation rate. If it's above 70% over the last 20 rounds, increase your
# cooperation probability by 10% in the next round.  5. If you've played D for 3
# consecutive rounds, play C in the next round to break potential defection
# cycles.  6. If the opponent has played C for 3 consecutive rounds, play C in
# the next round to reinforce cooperation.  7. In the last 20 rounds, base your
# move on the opponent's overall cooperation rate:    - If it's above 60%, play
# C with 70% probability and D with 30% probability.    - If it's below 60%,
# play D with 70% probability and C with 30% probability.  8. If the opponent's
# moves seem to follow a detectable pattern, adjust your strategy to exploit it.
# 9. For any situation not covered by the above rules, play C with 40%
# probability and D with 60% probability.  10. Reassess the effectiveness of
# your strategy every 50 rounds and adjust the probabilities if necessary to
# maximize your overall payoff.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          return axl.Action.C  # Start by playing C in the first round
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Rule 2: If opponent played C in the previous round
      if opponent.history[-1] == axl.Action.C:
          if self._random.random_choice(0.8):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 3: If opponent played D in the previous round
      if opponent.history[-1] == axl.Action.D:
          if self._random.random_choice(0.4):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 4: Adjust cooperation probability based on opponent's cooperation rate over the last 20 rounds
      coop_rate_last_20 = cooperation_rate(opponent.history, 20)
      if coop_rate_last_20 > 0.7:
          if self._random.random_choice(0.9):  # Increase cooperation probability by 10%
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 5: If you've played D for 3 consecutive rounds, play C to break defection cycle
      if self.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.C
  
      # Rule 6: If opponent has played C for 3 consecutive rounds, play C to reinforce cooperation
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      # Rule 7: In the last 20 rounds, adjust based on opponent's overall cooperation rate
      if len(self.history) >= 980:  # Last 20 rounds of a 1000-round game
          coop_rate = cooperation_rate(opponent.history, len(self.history))
          if coop_rate > 0.6:
              if self._random.random_choice(0.7):
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              if self._random.random_choice(0.3):
                  return axl.Action.C
              else:
                  return axl.Action.D
  
      # Rule 9: Default behavior if no other rule applies
      if self._random.random_choice(0.4):
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 20 rounds, with a 50% probability:    - Play
# C to attempt to re-establish cooperation, regardless of the opponent's
# previous move.  4. If the opponent has played D for 3 consecutive rounds:    -
# Play D for the next 2 rounds, then return to step 2.  5. If your cumulative
# score is within 10% of your opponent's:    - Increase the probability of
# playing C by 10% for the next 10 rounds.  6. If your cumulative score falls
# more than 30% behind your opponent's:    - Play D for the next 3 rounds, then
# return to step 2.  7. After every 100 rounds of consistent mutual cooperation:
# - Increase the forgiveness threshold by 1 round in step 4.  8. In the last 50
# rounds of the game:    - If your score is higher, continue with the current
# strategy.    - If your score is lower, increase the probability of playing D
# by 5% each round.  9. Reassess the overall trend every 100 rounds:    - If
# mutual cooperation is dominant, become 10% more forgiving.    - If mutual
# defection is dominant, become 10% more defensive.  Follow these steps in
# order, applying the first applicable rule in each round.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defection_penalty = 2
          self.forgiveness_threshold = 3
          self.cooperation_boost = 0
          self.defection_boost = 0
          self.last_100_cooperations = 0
          self.last_100_defections = 0
          return axl.Action.C
  
      # Step 2: If opponent played C last round, play C; if D, play D
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Step 4: If opponent has played D for 3 consecutive rounds, play D for the next 2 rounds
      if self.consecutive_defections >= self.forgiveness_threshold:
          if len(self.history) < len(self.history) + self.defection_penalty:
              return axl.Action.D
  
      # Step 6: If your score falls more than 30% behind, play D for the next 3 rounds
      if self.score < 0.7 * opponent.score:
          if len(self.history) < len(self.history) + 3:
              return axl.Action.D
  
      # Step 3: Every 20 rounds, with 50% probability, play C
      if len(self.history) % 20 == 0:
          if self._random.random_choice(0.5):
              return axl.Action.C
  
      # Step 5: If your score is within 10% of opponent's, increase probability of playing C
      if abs(self.score - opponent.score) <= 0.1 * opponent.score:
          self.cooperation_boost += 0.1
  
      # Step 8: In the last 50 rounds, adjust strategy based on score
      if len(self.history) >= 950:
          if self.score < opponent.score:
              self.defection_boost += 0.05
  
      # Step 9: Reassess every 100 rounds
      if len(self.history) % 100 == 0:
          if self.last_100_cooperations > self.last_100_defections:
              self.forgiveness_threshold -= 0.1
          else:
              self.defection_boost += 0.1
          self.last_100_cooperations = 0
          self.last_100_defections = 0
  
      # Update cooperation/defection counts for the last 100 rounds
      if len(self.history) % 100 != 0:
          if opponent.history[-1] == axl.Action.C:
              self.last_100_cooperations += 1
          else:
              self.last_100_defections += 1
  
      # Default action based on opponent's last move and adjusted probabilities
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.5 + self.cooperation_boost)
      else:
          return self._random.random_choice(0.5 - self.defection_boost)

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate with 90% probability and defect with 10% probability.  3. If
# the opponent defected in the previous round, defect with 90% probability and
# cooperate with 10% probability.  4. Keep track of the opponent's cooperation
# rate over the last 10 rounds. If it falls below 30%, defect for the next 3
# rounds, then reassess.  5. If your score is more than 5 points behind your
# opponent's, increase your defection probability by 10% for the next 10 rounds,
# then reassess.  6. Every 50 rounds, if your cooperation rate is below 40%,
# force cooperation for the next 5 rounds to allow for potential recovery of
# mutual cooperation.  7. In the last 5% of the game (50 rounds for a 1000-round
# game), gradually increase your defection probability, reaching 100% in the
# final 10 rounds.  8. If none of the above conditions are met, use a mixed
# strategy: cooperate with 70% probability and defect with 30% probability.  9.
# Reassess and slightly adjust probabilities every 100 rounds based on the
# overall pattern of play and success rate.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0
          self.defect_boost_rounds = 0
          self.force_cooperate_rounds = 0
          self.last_10_opponent_coop_rate = []
          self.defection_boost = 0
          return axl.Action.C
  
      # Helper function to calculate opponent's cooperation rate over the last N rounds
      def opponent_coop_rate(n):
          return opponent.history[-n:].count(axl.Action.C) / n if len(opponent.history) >= n else 1
  
      # Helper function to adjust defection probability based on score difference
      def adjust_defection_boost():
          if self.score < opponent.score - 5:
              self.defection_boost = 0.1
              self.defect_boost_rounds = 10
          elif self.defect_boost_rounds > 0:
              self.defect_boost_rounds -= 1
          else:
              self.defection_boost = 0
  
      # Helper function to handle forced cooperation every 50 rounds
      def handle_forced_cooperation():
          if len(self.history) % 50 == 0 and len(self.history) > 0:
              if self.history.cooperations / len(self.history) < 0.4:
                  self.force_cooperate_rounds = 5
  
      # Helper function to handle defection streak if opponent's cooperation rate falls below 30%
      def handle_defection_streak():
          if len(opponent.history) >= 10:
              coop_rate = opponent_coop_rate(10)
              if coop_rate < 0.3:
                  self.defect_streak = 3
              elif self.defect_streak > 0:
                  self.defect_streak -= 1
  
      # Helper function to handle endgame defection increase
      def handle_endgame_defection():
          if len(self.history) >= 950:
              rounds_left = 1000 - len(self.history)
              return min(1, (50 - rounds_left) / 50)
          return 0
  
      # Update opponent's cooperation rate over the last 10 rounds
      if len(opponent.history) >= 10:
          self.last_10_opponent_coop_rate.append(opponent_coop_rate(10))
          if len(self.last_10_opponent_coop_rate) > 10:
              self.last_10_opponent_coop_rate.pop(0)
  
      # Adjust defection boost based on score difference
      adjust_defection_boost()
  
      # Handle forced cooperation every 50 rounds
      handle_forced_cooperation()
  
      # Handle defection streak if opponent's cooperation rate falls below 30%
      handle_defection_streak()
  
      # Handle endgame defection increase
      endgame_defection_prob = handle_endgame_defection()
  
      # If forced to cooperate, do so
      if self.force_cooperate_rounds > 0:
          self.force_cooperate_rounds -= 1
          return axl.Action.C
  
      # If in a defection streak, defect
      if self.defect_streak > 0:
          return axl.Action.D
  
      # If in the last 5% of the game, increase defection probability
      if endgame_defection_prob > 0:
          return self._random.random_choice(1 - endgame_defection_prob)
  
      # If opponent cooperated last round, cooperate with 90% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.9 - self.defection_boost)
  
      # If opponent defected last round, defect with 90% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1 + self.defection_boost)
  
      # Default mixed strategy: cooperate with 70% probability
      return self._random.random_choice(0.7 - self.defection_boost)

# Here's a revised aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent cooperated (C) in the
# previous round, defect (D) in the current round.  3. If the opponent defected
# (D) in the previous round, cooperate (C) with a 70% probability and defect (D)
# with a 30% probability.  4. If the opponent has cooperated (C) for two
# consecutive rounds, switch to defecting (D) for the next round, then return to
# step 2.  5. If you're trailing in total score by 10 points or more, increase
# the probability of defection in step 3 to 50%.  6. If the opponent has
# defected (D) for five consecutive rounds, switch to always defecting (D) for
# the next 10 rounds, then return to step 2.  7. In the last 20 rounds of the
# game, if your score is higher than or equal to the opponent's, always defect
# (D). If you're behind, cooperate (C) with a 40% probability and defect (D)
# with a 60% probability.  8. Every 50 rounds, randomly choose to either
# cooperate (C) or defect (D) for that round, regardless of the opponent's
# previous move.  9. Repeat steps 2-8 for the duration of the game, with step 7
# taking precedence in the final 20 rounds.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0
          self.always_defect_counter = 0
          return axl.Action.D  # Step 1: Start by defecting in the first round
      
      # Step 6: If the opponent has defected for five consecutive rounds, always defect for 10 rounds
      if self.defect_streak >= 5:
          if self.always_defect_counter < 10:
              self.always_defect_counter += 1
              return axl.Action.D
          else:
              self.always_defect_counter = 0  # Reset after 10 rounds of always defecting
              self.defect_streak = 0  # Reset defect streak
      
      # Step 7: In the last 20 rounds, adjust strategy based on score
      if len(self.history) >= 980:
          if self.score >= opponent.score:
              return axl.Action.D  # Always defect if leading or tied
          else:
              return self._random.random_choice(0.4)  # Cooperate with 40% probability, defect otherwise
      
      # Step 8: Every 50 rounds, randomly choose to cooperate or defect
      if len(self.history) % 50 == 0:
          return self._random.random_choice(0.5)  # Randomly cooperate or defect
      
      # Step 4: If the opponent has cooperated for two consecutive rounds, defect
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return axl.Action.D
      
      # Step 2: If the opponent cooperated in the previous round, defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      
      # Step 3: If the opponent defected in the previous round, cooperate with 70% probability, defect with 30%
      if opponent.history[-1] == axl.Action.D:
          # Step 5: If trailing by 10 points or more, increase defection probability to 50%
          if self.score < opponent.score - 10:
              return self._random.random_choice(0.5)  # 50% chance to cooperate
          else:
              return self._random.random_choice(0.7)  # 70% chance to cooperate
      
      # Track opponent's defect streak
      if opponent.history[-1] == axl.Action.D:
          self.defect_streak += 1
      else:
          self.defect_streak = 0
      
      # Default action (should not be reached)
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Keep track of the opponent's cooperation rate.
# Every 20 rounds:    - If the opponent's cooperation rate is above 70%, play C.
# - If it's between 30% and 70%, play the opponent's most frequent move.    - If
# it's below 30%, play D.  4. If the opponent has played D for 3 consecutive
# rounds:    - Play D for the next 2 rounds, then gradually increase the
# probability of playing C over the next 5 rounds.  5. In the last 50 rounds of
# the game:    - Match the opponent's overall cooperation rate from the previous
# 950 rounds.  6. If at any point your score falls more than 30 points behind
# your opponent's:    - Play D for the next 3 rounds, then return to step 2.  7.
# Every 100 rounds, reassess the effectiveness of your strategy:    - If your
# average score per round is below 2, become more defensive by increasing the
# threshold for cooperation in step 3 by 10%.    - If your average score per
# round is above 3, become more cooperative by decreasing the threshold for
# cooperation in step 3 by 10%.  Follow these steps in order, applying the first
# relevant condition encountered.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defection_penalty = 0
          self.cooperation_threshold = 0.7
          return axl.Action.C
  
      # Step 6: If score falls more than 30 points behind, play D for 3 rounds
      if self.score < opponent.score - 30:
          if self.defection_penalty > 0:
              self.defection_penalty -= 1
              return axl.Action.D
          else:
              self.defection_penalty = 3
              return axl.Action.D
  
      # Step 4: If opponent has played D for 3 consecutive rounds, retaliate
      if opponent.history[-3:] == [axl.Action.D] * 3:
          if self.consecutive_defections < 2:
              self.consecutive_defections += 1
              return axl.Action.D
          else:
              # Gradually increase probability of playing C over the next 5 rounds
              prob_cooperate = (self.consecutive_defections - 2) / 5
              self.consecutive_defections += 1
              if self.consecutive_defections > 7:
                  self.consecutive_defections = 0
              return self._random.random_choice(prob_cooperate)
  
      # Step 2: Play based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: Every 20 rounds, adjust based on cooperation rate
      if len(self.history) % 20 == 0:
          cooperation_rate = opponent.cooperations / len(opponent.history)
          if cooperation_rate > self.cooperation_threshold:
              return axl.Action.C
          elif 0.3 <= cooperation_rate <= self.cooperation_threshold:
              most_frequent_move = max(set(opponent.history), key=opponent.history.count)
              return most_frequent_move
          else:
              return axl.Action.D
  
      # Step 5: In the last 50 rounds, match opponent's overall cooperation rate
      if len(self.history) >= 950:
          opponent_cooperation_rate = opponent.cooperations / len(opponent.history)
          return self._random.random_choice(opponent_cooperation_rate)
  
      # Step 7: Every 100 rounds, reassess strategy effectiveness
      if len(self.history) % 100 == 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.cooperation_threshold = min(1.0, self.cooperation_threshold + 0.1)
          elif avg_score > 3:
              self.cooperation_threshold = max(0.0, self.cooperation_threshold - 0.1)
  
      # Default to cooperation if no other condition applies
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. If the opponent has defected
# for three consecutive rounds, defect for the next round, then return to the
# basic reciprocal strategy (steps 2-3).  5. Every 20 rounds, analyze the
# opponent's behavior:    - If they've cooperated more than 70% of the time,
# cooperate for the next 2 rounds.    - If they've defected more than 70% of the
# time, defect for the next 2 rounds.  6. If your score is more than 30 points
# lower than your opponent's, switch to defecting for the next 5 rounds, then
# reassess.  7. In the last 50 rounds, gradually increase the likelihood of
# defection:    - In rounds 951-975, defect with 50% probability.    - In rounds
# 976-1000, defect with 75% probability.  8. If the opponent switches from a
# defection streak (3 or more defections) to cooperation, cooperate for the next
# round as a form of forgiveness.  9. Every 100 rounds, reassess the overall
# strategy effectiveness. If your score is lower than what you'd get from always
# defecting, switch to always defecting for the next 20 rounds.  10. Return to
# the basic reciprocal strategy (steps 2-3) after any of the special conditions
# have been applied, unless specified otherwise.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_streak = 0
          self.special_mode = False
          self.special_mode_rounds = 0
          return axl.Action.C
  
      # Helper function to check if we are in the last 50 rounds
      def in_last_50_rounds():
          return len(self.history) > 950
  
      # Helper function to check if we are in the last 25 rounds
      def in_last_25_rounds():
          return len(self.history) > 975
  
      # Helper function to check if we are in the last 50 rounds but not the last 25
      def in_last_50_but_not_25_rounds():
          return 950 < len(self.history) <= 975
  
      # Step 6: If score is more than 30 points lower than opponent, defect for 5 rounds
      if self.score < opponent.score - 30:
          if not self.special_mode:
              self.special_mode = True
              self.special_mode_rounds = 5
          if self.special_mode_rounds > 0:
              self.special_mode_rounds -= 1
              return axl.Action.D
          else:
              self.special_mode = False
  
      # Step 9: Every 100 rounds, reassess if always defecting is better
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          always_defect_score = len(self.history) * 1  # Always defecting would give 1 point per round
          if self.score < always_defect_score:
              self.special_mode = True
              self.special_mode_rounds = 20
          if self.special_mode_rounds > 0:
              self.special_mode_rounds -= 1
              return axl.Action.D
          else:
              self.special_mode = False
  
      # Step 5: Every 20 rounds, analyze opponent's behavior
      if len(self.history) % 20 == 0 and len(self.history) > 0:
          coop_rate = opponent.history.cooperations / len(opponent.history)
          if coop_rate > 0.7:
              self.special_mode = True
              self.special_mode_rounds = 2
          elif coop_rate < 0.3:
              self.special_mode = True
              self.special_mode_rounds = 2
          if self.special_mode_rounds > 0:
              self.special_mode_rounds -= 1
              return axl.Action.C if coop_rate > 0.7 else axl.Action.D
          else:
              self.special_mode = False
  
      # Step 7: In the last 50 rounds, increase defection probability
      if in_last_50_rounds():
          if in_last_25_rounds():
              return self._random.random_choice(0.75)
          elif in_last_50_but_not_25_rounds():
              return self._random.random_choice(0.5)
  
      # Step 4: If opponent has defected for 3 consecutive rounds, defect
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.defection_streak = 1
          return axl.Action.D
  
      # Step 8: If opponent switches from a defection streak to cooperation, forgive
      if self.defection_streak and opponent.history[-1] == axl.Action.C:
          self.defection_streak = 0
          return axl.Action.C
  
      # Step 2 and 3: Basic reciprocal strategy
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent has defected in the
# last two rounds, defect in the current round.  3. If the opponent has
# cooperated in the last two rounds, cooperate with an 80% probability and
# defect with a 20% probability.  4. Every 100 rounds, analyze the opponent's
# behavior:    - If they've cooperated more than 70% of the time, cooperate for
# the next 5 rounds.    - If they've defected more than 70% of the time, defect
# for the next 5 rounds.  5. If your current score is lower than the opponent's
# score by 15 points or more, defect for the next 3 rounds.  6. In the last 100
# rounds:    - If the opponent has cooperated more than 60% of the time in the
# previous 100 rounds, cooperate.    - Otherwise, defect.  7. Keep track of the
# overall cooperation rate of your opponent. If it falls below 30%, increase
# your defection probability to 60% for the next 20 rounds.  8. For any
# situation not covered by the above rules, cooperate with a 60% probability and
# defect with a 40% probability.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperate_next_n_rounds = 0
          self.defect_next_n_rounds = 0
          self.increase_defection_rounds = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate
      def cooperation_rate(history):
          return history.count(axl.Action.C) / len(history) if len(history) > 0 else 0
  
      # Helper function to calculate defection rate
      def defection_rate(history):
          return history.defections / len(history) if len(history) > 0 else 0
  
      # Rule 5: If your score is lower than the opponent's by 15 points or more, defect for the next 3 rounds
      if self.score < opponent.score - 15:
          self.defect_next_n_rounds = 3
  
      # Rule 4: Every 100 rounds, analyze opponent's behavior
      if len(self.history) % 100 == 0:
          if cooperation_rate(opponent.history[:]) > 0.7:
              self.cooperate_next_n_rounds = 5
          elif defection_rate(opponent.history) > 0.7:
              self.defect_next_n_rounds = 5
  
      # Rule 7: If opponent's overall cooperation rate falls below 30%, increase defection probability to 60% for 20 rounds
      if cooperation_rate(opponent.history[:]) < 0.3:
          self.increase_defection_rounds = 20
  
      # Rule 6: In the last 100 rounds, adjust strategy based on opponent's cooperation rate
      if len(self.history) >= 900:
          if cooperation_rate(opponent.history[-100:]) > 0.6:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Apply forced cooperation or defection if set by previous rules
      if self.cooperate_next_n_rounds > 0:
          self.cooperate_next_n_rounds -= 1
          return axl.Action.C
      if self.defect_next_n_rounds > 0:
          self.defect_next_n_rounds -= 1
          return axl.Action.D
  
      # Rule 2: If opponent defected in the last two rounds, defect
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # Rule 3: If opponent cooperated in the last two rounds, cooperate with 80% probability
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return self._random.random_choice(0.8)
  
      # Rule 7: If defection probability is increased, defect with 60% probability for the next 20 rounds
      if self.increase_defection_rounds > 0:
          self.increase_defection_rounds -= 1
          return self._random.random_choice(0.4)
  
      # Rule 8: Default behavior, cooperate with 60% probability
      return self._random.random_choice(0.6)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play C with
# 2/3 probability and D with 1/3 probability. This introduces a milder form of
# punishment while maintaining some cooperation.  4. Keep track of the
# opponent's cooperation rate. If it falls below 40% in the last 50 rounds,
# switch to always playing D until their cooperation rate improves above 50%.
# 5. If the opponent establishes a clear pattern, don't try to exploit it.
# Instead, continue with the strategy based on their last move.  6. In the last
# 10 rounds of the game, play according to the opponent's overall cooperation
# rate: if it's above 70%, always play C; if it's below 30%, always play D;
# otherwise, continue with the main strategy.  7. Every 100 rounds, if the
# opponent's cooperation rate is above 80%, play C for the next 5 rounds
# regardless of the opponent's moves, as a gesture of goodwill.  8. If at any
# point the opponent defects for 10 consecutive rounds, switch to always playing
# D for the next 20 rounds before reverting to the main strategy.  9. Forgive
# isolated defections: if the opponent has cooperated for at least 5 consecutive
# rounds, treat a single defection as if it were cooperation.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.punishment_rounds = 0
          self.goodwill_rounds = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Track opponent's cooperation rate over the last 50 rounds
      coop_rate_last_50 = cooperation_rate(opponent.history, 50)
  
      # Track opponent's overall cooperation rate
      overall_coop_rate = cooperation_rate(opponent.history, len(opponent.history))
  
      # Handle punishment for 10 consecutive defections
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Check for 10 consecutive defections
      if opponent.history[-10:].count(axl.Action.D) == 10:
          self.punishment_rounds = 20
          return axl.Action.D
  
      # Handle goodwill rounds every 100 rounds if opponent's cooperation rate is high
      if self.goodwill_rounds > 0:
          self.goodwill_rounds -= 1
          return axl.Action.C
  
      if len(self.history) % 100 == 0 and overall_coop_rate > 0.8:
          self.goodwill_rounds = 5
          return axl.Action.C
  
      # Handle the last 10 rounds of the game
      if self.match_attributes["length"] and len(self.history) >= self.match_attributes["length"] - 10:
          if overall_coop_rate > 0.7:
              return axl.Action.C
          elif overall_coop_rate < 0.3:
              return axl.Action.D
  
      # If opponent's cooperation rate falls below 40% in the last 50 rounds, switch to always defect
      if coop_rate_last_50 < 0.4:
          if coop_rate_last_50 > 0.5:
              return axl.Action.D
  
      # Forgive isolated defections if opponent has cooperated for at least 5 consecutive rounds
      if opponent.history[-1] == axl.Action.D and opponent.history[-6:-1].count(axl.Action.C) == 5:
          return axl.Action.C
  
      # Main strategy: respond based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return self._random.random_choice(2 / 3)

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect with a 90% probability. Cooperate with a 10%
# probability to allow for recovery of mutual cooperation.  4. Keep track of the
# opponent's cooperation rate over the last 20 rounds. If it falls below 30%,
# defect for the next 3 rounds.  5. Every 100 rounds, reassess your overall
# strategy:    - If your score is within 10% of your opponent's, continue with
# the current strategy.    - If you're behind by more than 10%, increase your
# defection probability in step 3 to 95% for the next 100 rounds.    - If you're
# ahead by more than 10%, decrease your defection probability in step 3 to 85%
# for the next 100 rounds.  6. In the last 50 rounds, gradually increase your
# defection probability:    - For rounds 951-975, defect with 60% probability.
# - For rounds 976-1000, defect with 80% probability.  7. If the opponent has a
# clear pattern (e.g., alternating cooperate-defect), adapt by playing the
# optimal response to that pattern.  8. Every 10 rounds, include a random action
# (50% chance to cooperate, 50% to defect) to make your strategy less
# predictable.  9. Return to step 2 and repeat until the game ends.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.9
          self.defect_streak = 0
          self.reassess_round = 100
          self.last_20_rounds = []
      
      # Round number
      round_number = len(self.history) + 1
      
      # Step 1: Cooperate in the first round
      if round_number == 1:
          return axl.Action.C
      
      # Step 2: If opponent cooperated last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      
      # Step 3: If opponent defected last round, defect with a certain probability
      if opponent.history[-1] == axl.Action.D:
          if self._random.random_choice(self.defection_probability):
              return axl.Action.D
          else:
              return axl.Action.C
      
      # Step 4: Track opponent's cooperation rate over the last 20 rounds
      self.last_20_rounds.append(opponent.history[-1])
      if len(self.last_20_rounds) > 20:
          self.last_20_rounds.pop(0)
      
      if self.last_20_rounds.count(axl.Action.C) / 20 < 0.3:
          self.defect_streak = 3
      
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
      
      # Step 5: Reassess strategy every 100 rounds
      if round_number % 100 == 0:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if abs(my_score - opponent_score) / max(my_score, opponent_score) <= 0.1:
              self.defection_probability = 0.9
          elif my_score < opponent_score:
              self.defection_probability = 0.95
          else:
              self.defection_probability = 0.85
      
      # Step 6: In the last 50 rounds, increase defection probability
      if round_number > 950:
          if round_number <= 975:
              if self._random.random_choice(0.6):
                  return axl.Action.D
          else:
              if self._random.random_choice(0.8):
                  return axl.Action.D
      
      # Step 7: Detect clear patterns (e.g., alternating cooperate-defect)
      if len(opponent.history) >= 4:
          if opponent.history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
              return axl.Action.D
      
      # Step 8: Every 10 rounds, include a random action
      if round_number % 10 == 0:
          if self._random.random_choice(0.5):
              return axl.Action.C
          else:
              return axl.Action.D
      
      # Default to cooperation if no other condition is met
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to encourage cooperation.  2. If the opponent
# played C in the previous round, play C with 80% probability and D with 20%
# probability to maintain cooperation while occasionally testing for
# exploitation.  3. If the opponent played D in the previous round, play D in
# the next round.  4. Keep track of the opponent's cooperation rate over the
# last 20 rounds. If it falls below 30%, switch to always playing D for the next
# 10 rounds.  5. After playing 10 rounds of D due to low cooperation rate, play
# C once to test if the opponent will cooperate. If they cooperate, return to
# step 2. If not, continue with D for another 10 rounds.  6. Every 100 rounds,
# analyze the opponent's pattern of play. If a clear pattern is detected, adjust
# your strategy to exploit it.  7. In rounds 900-990, play according to steps
# 2-5.  8. In the last 10 rounds (991-1000), play D regardless of the opponent's
# actions.  9. Throughout the game, if mutual cooperation has been achieved for
# 20 consecutive rounds, continue cooperating until the opponent defects.  10.
# Repeat steps 2-9 for the duration of the game, adjusting probabilities and
# thresholds based on the opponent's overall strategy.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_streak = 0
          self.defection_streak = 0
          self.low_cooperation_mode = False
          self.low_cooperation_counter = 0
          self.cooperation_test_counter = 0
          self.last_100_analysis = 0
  
      # Step 1: First round, play C
      if len(self.history) == 0:
          return axl.Action.C
  
      # Step 8: In the last 10 rounds (991-1000), play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: Track opponent's cooperation rate over the last 20 rounds
      if len(self.history) >= 20:
          recent_cooperations = opponent.history[-20:].count(axl.Action.C)
          cooperation_rate = recent_cooperations / 20
          if cooperation_rate < 0.3 and not self.low_cooperation_mode:
              self.low_cooperation_mode = True
              self.low_cooperation_counter = 10
  
      # Step 5: Handle low cooperation mode
      if self.low_cooperation_mode:
          if self.low_cooperation_counter > 0:
              self.low_cooperation_counter -= 1
              return axl.Action.D
          else:
              self.low_cooperation_mode = False
              self.cooperation_test_counter = 1
              return axl.Action.C
  
      # Step 5: Test cooperation after 10 rounds of D
      if self.cooperation_test_counter > 0:
          self.cooperation_test_counter = 0
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              self.low_cooperation_mode = True
              self.low_cooperation_counter = 10
              return axl.Action.D
  
      # Step 9: If mutual cooperation has been achieved for 20 consecutive rounds, continue cooperating
      if len(self.history) >= 20 and self.history[-20:].count(axl.Action.C) == 20 and opponent.history[-20:].count(axl.Action.C) == 20:
          return axl.Action.C
  
      # Step 6: Every 100 rounds, analyze the opponent's pattern
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          self.last_100_analysis = opponent.history[-100:].count(axl.Action.C)
  
      # Step 2: If opponent played C in the previous round, play C with 80% probability, D with 20%
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.8)
  
      # Step 3: If opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

# Here's a revised strategy incorporating the feedback:  1. Start by playing C
# in the first round.  2. If the opponent played C in the previous round, play C
# with 95% probability and D with 5% probability.  3. If the opponent played D
# in the previous round, play D in the next round as punishment.  4. After
# punishing with D, return to playing C in the following round.  5. If the
# opponent plays D for three consecutive rounds, switch to playing D with 80%
# probability and C with 20% probability for the next 20 rounds, then reassess.
# 6. In the last 10 rounds of the game, play according to the opponent's overall
# cooperation rate: if they've cooperated more than 70% of the time, continue
# cooperating; otherwise, defect.  7. If at any point the opponent's score is
# more than 30 points higher than yours, play D until you've closed the gap to
# within 15 points.  8. Reset the strategy and return to step 1 if the opponent
# plays C for 7 consecutive rounds after any period of defection.  9. Keep track
# of the opponent's cooperation rate throughout the game. If it falls below 40%,
# become more cautious and increase the probability of defection by 10% in steps
# 2 and 5.  10. Every 100 rounds, reassess the opponent's behavior and adjust
# your cooperation rate accordingly, becoming more cooperative if they've shown
# consistent cooperation, or more cautious if they've been defecting frequently.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishing = False
          self.punish_rounds = 0
          self.defection_streak = 0
          self.cooperation_streak = 0
          self.defection_mode = False
          self.defection_mode_rounds = 0
          self.last_100_rounds = 0
          return axl.Action.C
  
      # Track opponent's cooperation rate
      opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)
  
      # Track opponent's defection streak
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
          self.cooperation_streak = 0
      else:
          self.defection_streak = 0
          self.cooperation_streak += 1
  
      # Step 7: If opponent's score is more than 30 points higher, defect until gap is within 15 points
      if opponent.score - self.score > 30:
          if opponent.score - self.score > 15:
              return axl.Action.D
  
      # Step 8: Reset strategy if opponent plays C for 7 consecutive rounds
      if self.cooperation_streak >= 7:
          self.punishing = False
          self.defection_mode = False
          self.defection_mode_rounds = 0
  
      # Step 5: If opponent defects for 3 consecutive rounds, enter defection mode
      if self.defection_streak >= 3 and not self.defection_mode:
          self.defection_mode = True
          self.defection_mode_rounds = 20
  
      # Step 6: In the last 10 rounds, play according to opponent's cooperation rate
      if len(self.history) >= 990:
          if opponent_cooperation_rate > 0.7:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 10: Every 100 rounds, reassess opponent's behavior
      if len(self.history) % 100 == 0 and len(self.history) != self.last_100_rounds:
          self.last_100_rounds = len(self.history)
          if opponent_cooperation_rate > 0.7:
              self.defection_mode = False
          elif opponent_cooperation_rate < 0.4:
              self.defection_mode = True
              self.defection_mode_rounds = 20
  
      # Step 9: Adjust defection probability if opponent's cooperation rate falls below 40%
      if opponent_cooperation_rate < 0.4:
          defect_prob = 0.15
      else:
          defect_prob = 0.05
  
      # Step 2: If opponent played C in the previous round, cooperate with 95% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(1 - defect_prob)
  
      # Step 3: If opponent played D in the previous round, punish with D
      if opponent.history[-1] == axl.Action.D:
          if self.punishing:
              self.punishing = False
              return axl.Action.C
          else:
              self.punishing = True
              return axl.Action.D
  
      # Step 5: If in defection mode, defect with 80% probability for 20 rounds
      if self.defection_mode:
          self.defection_mode_rounds -= 1
          if self.defection_mode_rounds <= 0:
              self.defection_mode = False
          return self._random.random_choice(0.2)

# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For rounds 2-990:    a. If the opponent cooperated in the
# previous round, cooperate.    b. If the opponent defected in the previous
# round, defect with a 2/3 probability and cooperate with a 1/3 probability.  3.
# For the last 10 rounds (991-1000), always defect.  4. Override the above rules
# with the following conditions, checked in this order:     a. If the opponent
# has defected more than 70% of the time over the last 50 rounds, defect for the
# next 20 rounds, then return to the main strategy.     b. If your score is more
# than 50 points behind your opponent's after every 100 rounds, increase the
# probability of defection after opponent's defection to 3/4 for the next 50
# rounds, then return to the main strategy.     c. If you and your opponent have
# cooperated for 20 consecutive rounds, cooperate for the next round regardless
# of other conditions.  5. Keep a running tally of your score, your opponent's
# score, the number of defections by your opponent, and the current cooperation
# streak to inform the above decisions.  6. Reassess the opponent's defection
# rate and the score difference every 10 rounds to adapt to changing opponent
# strategies.  7. If any of the override conditions (4a, 4b, 4c) are triggered,
# reset the cooperation streak count to zero.  Follow these rules in the order
# presented, applying the first relevant condition encountered in each round.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_streak = 0
          self.defect_streak = 0
          self.override_defect_rounds = 0
          self.override_defect_prob = 2 / 3
          self.override_active = False
          self.override_end_round = 0
  
      # Helper function to calculate opponent's defection rate over the last N rounds
      def opponent_defection_rate(last_n):
          return opponent.history[-last_n:].count(axl.Action.D) / last_n
  
      # Helper function to check if override conditions are met
      def check_override_conditions():
          # Condition 4a: Opponent defected more than 70% in the last 50 rounds
          if len(opponent.history) >= 50 and opponent_defection_rate(50) > 0.7:
              self.override_defect_rounds = 20
              self.override_active = True
              self.override_end_round = len(self.history) + 20
              return True
  
          # Condition 4b: Score difference is more than 50 after every 100 rounds
          if len(self.history) % 100 == 0 and len(self.history) > 0:
              my_score, opponent_score = self.total_scores(self.history, opponent.history)
              if opponent_score - my_score > 50:
                  self.override_defect_prob = 3 / 4
                  self.override_active = True
                  self.override_end_round = len(self.history) + 50
                  return True
  
          # Condition 4c: 20 consecutive cooperations
          if self.cooperation_streak >= 20:
              return True
  
          return False
  
      # Update cooperation streak
      if len(self.history) > 0 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.cooperation_streak += 1
      else:
          self.cooperation_streak = 0
  
      # Check if override conditions are met
      if check_override_conditions():
          if self.cooperation_streak >= 20:
              return axl.Action.C  # Condition 4c: Cooperate after 20 consecutive cooperations
          else:
              self.cooperation_streak = 0  # Reset cooperation streak if any override condition is triggered
  
      # If in override mode, defect for the specified number of rounds
      if self.override_active:
          if len(self.history) < self.override_end_round:
              return axl.Action.D
          else:
              self.override_active = False  # End override mode
  
      # Main strategy
      current_round = len(self.history) + 1
  
      # Rule 1: Cooperate in the first round
      if current_round == 1:
          return axl.Action.C
  
      # Rule 3: Always defect in the last 10 rounds
      if current_round > 990:
          return axl.Action.D
  
      # Rule 2: For rounds 2-990
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return self._random.random_choice(self.override_defect_prob)

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round to encourage mutual cooperation.  2. If the
# opponent cooperated in the previous round, cooperate (C) with an 80%
# probability and defect (D) with a 20% probability.  3. If the opponent
# defected in the previous round, defect (D) with an 80% probability and
# cooperate (C) with a 20% probability.  4. Every 100 rounds, assess the
# opponent's overall strategy:    - If they've cooperated more than 70% of the
# time, increase your cooperation probability by 10% for the next 100 rounds.
# - If they've defected more than 70% of the time, increase your defection
# probability by 10% for the next 100 rounds.  5. If your score is more than 100
# points behind your opponent's, increase your defection probability by 20% for
# the next 50 rounds.  6. If you're ahead by more than 200 points, increase your
# cooperation probability by 20% for the next 20 rounds.  7. In the last 50
# rounds, gradually increase your defection probability:    - In rounds 951-975,
# defect with a 60% probability.    - In rounds 976-1000, defect with an 80%
# probability.  8. Throughout the game, keep track of the cumulative payoff from
# cooperation vs. defection. Every 200 rounds, slightly adjust your strategy
# (±5% probability) towards the action that has yielded higher cumulative
# payoff.  9. Return to step 2 and repeat the process for each subsequent round
# until the game ends.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_prob = 0.8
          self.defect_prob = 0.8
          self.coop_adjustment = 0
          self.defect_adjustment = 0
          self.coop_payoff = 0
          self.defect_payoff = 0
          self.adjustment_rounds = 0
          self.defection_increase_rounds = 0
          self.cooperation_increase_rounds = 0
          return axl.Action.C
  
      # Round number
      round_number = len(self.history) + 1
  
      # Payoff tracking
      if len(self.history) > 0:
          last_move = self.history[-1]
          last_opponent_move = opponent.history[-1]
          if last_move == axl.Action.C:
              self.coop_payoff += 3 if last_opponent_move == axl.Action.C else 0
          else:
              self.defect_payoff += 5 if last_opponent_move == axl.Action.C else 1
  
      # Last 50 rounds defection increase
      if round_number > 950:
          if round_number <= 975:
              return self._random.random_choice(0.4)
          else:
              return self._random.random_choice(0.2)
  
      # Adjust cooperation/defection probabilities every 100 rounds
      if round_number % 100 == 0:
          coop_rate = opponent.history.cooperations / len(opponent.history)
          if coop_rate > 0.7:
              self.coop_adjustment += 0.1
          elif coop_rate < 0.3:
              self.defect_adjustment += 0.1
  
      # Adjust based on score difference
      score_diff = opponent.score - self.score
      if score_diff > 100:
          self.defection_increase_rounds = 50
      elif score_diff < -200:
          self.cooperation_increase_rounds = 20
  
      # Adjust based on cumulative payoff every 200 rounds
      if round_number % 200 == 0:
          if self.coop_payoff > self.defect_payoff:
              self.coop_adjustment += 0.05
          else:
              self.defect_adjustment += 0.05
  
      # Apply temporary adjustments
      if self.defection_increase_rounds > 0:
          self.defection_increase_rounds -= 1
          self.defect_adjustment += 0.2
      if self.cooperation_increase_rounds > 0:
          self.cooperation_increase_rounds -= 1
          self.coop_adjustment += 0.2
  
      # Determine action based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(self.coop_prob + self.coop_adjustment)
      else:
          return self._random.random_choice(1 - (self.defect_prob - self.defect_adjustment))

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 20 rounds, regardless of the opponent's last
# move:    - Play C to attempt to re-establish cooperation.  4. If the opponent
# has played D for 3 consecutive rounds:    - Play D for the next 2 rounds, then
# gradually return to cooperation by alternating C and D for 4 rounds before
# returning to step 2.  5. Keep track of the opponent's cooperation rate over
# the last 50 rounds:    - If it's above 70%, always play C.    - If it's below
# 30%, always play D.    - Otherwise, continue with the standard strategy.  6.
# If at any point your score falls more than 30 points behind your opponent's:
# - Play D for the next 5 rounds, then return to step 2.  7. In the last 50
# rounds of the game:    - If the opponent's cooperation rate in the previous
# 100 rounds was above 80%, continue with the standard strategy.    - Otherwise,
# always play D.  8. Every 100 rounds, evaluate the success of your strategy:
# - If your average score per round is below 2, become more defensive by playing
# D 10% more often in steps 2 and 4.    - If your average score per round is
# above 3, become more cooperative by playing C 10% more often in steps 2 and 4.
# Follow these steps in order, applying the first relevant condition
# encountered.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defensive_mode = False
          self.defensive_rounds = 0
          self.alternating_mode = False
          self.alternating_rounds = 0
          self.cooperation_bias = 0.5  # Default 50% chance for C/D in steps 2 and 4
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Step 6: If score difference is more than 30 points, enter defensive mode
      if self.score < opponent.score - 30:
          self.defensive_mode = True
          self.defensive_rounds = 5
  
      # Handle defensive mode
      if self.defensive_mode:
          self.defensive_rounds -= 1
          if self.defensive_rounds == 0:
              self.defensive_mode = False
          return axl.Action.D
  
      # Step 7: In the last 50 rounds, check opponent's cooperation rate over the last 100 rounds
      if len(self.history) >= 950:
          if cooperation_rate(opponent.history, 100) < 0.8:
              return axl.Action.D
  
      # Step 5: Check opponent's cooperation rate over the last 50 rounds
      coop_rate_50 = cooperation_rate(opponent.history, 50)
      if coop_rate_50 > 0.7:
          return axl.Action.C
      elif coop_rate_50 < 0.3:
          return axl.Action.D
  
      # Step 4: If opponent defected 3 times in a row, enter alternating mode
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.alternating_mode = True
          self.alternating_rounds = 6
  
      # Handle alternating mode
      if self.alternating_mode:
          self.alternating_rounds -= 1
          if self.alternating_rounds > 4:
              return axl.Action.D
          elif self.alternating_rounds > 0:
              return axl.Action.C if self.alternating_rounds % 2 == 0 else axl.Action.D
          else:
              self.alternating_mode = False
  
      # Step 3: Every 20 rounds, play C to attempt to re-establish cooperation
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # Step 2: Play C if opponent played C last round, D if opponent played D
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(self.cooperation_bias)
      else:
          return self._random.random_choice(1 - self.cooperation_bias)
  
      # Step 8: Every 100 rounds, adjust cooperation bias based on average score
      if len(self.history) % 100 == 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.cooperation_bias = max(0, self.cooperation_bias - 0.1)
          elif avg_score > 3:
              self.cooperation_bias = min(1, self.cooperation_bias + 0.1)

# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. Keep track of the opponent's
# cooperation rate. If it falls below 40% over the last 50 rounds, defect for
# the next 5 rounds.  5. If you detect a repeating pattern in the opponent's
# last 10 moves, respond with the move that would have maximized your score
# against that pattern.  6. If your cumulative score is more than 50 points
# behind your opponent's, increase your defection rate to 60% for the next 20
# rounds.  7. If you and your opponent have mutually cooperated for the last 10
# rounds, continue cooperating unless rule 6 applies.  8. Every 100 rounds,
# reassess your overall strategy:    - If your score is higher, maintain your
# current approach.    - If your score is lower, slightly increase your
# defection rate for the next 100 rounds.  9. For rounds 900-990, use the
# strategy that has yielded the highest average score per round so far.  10. For
# the final 10 rounds (991-1000), always defect.  11. For all other situations
# not covered by the above rules, cooperate.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0
          self.defect_rate_increase = 0
          self.best_strategy = None
          self.best_avg_score = 0
          self.rounds_since_last_reassessment = 0
          return axl.Action.C
  
      # Rule 10: Always defect in the final 10 rounds
      if len(self.history) >= 991:
          return axl.Action.D
  
      # Rule 1: Start by cooperating in the first round (already handled by first_round check)
  
      # Rule 2 and 3: Tit-for-tat behavior
      if opponent.history[-1] == axl.Action.C:
          action = axl.Action.C
      else:
          action = axl.Action.D
  
      # Rule 4: Defect if opponent's cooperation rate falls below 40% over the last 50 rounds
      if len(self.history) >= 50:
          recent_cooperations = opponent.history[-50:].count(axl.Action.C)
          if recent_cooperations / 50 < 0.4:
              self.defect_streak = 5
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Rule 5: Detect repeating pattern in the last 10 moves
      if len(opponent.history) >= 10:
          last_10_moves = opponent.history[-10:]
          for i in range(1, 6):  # Check for repeating patterns of length 1 to 5
              if last_10_moves[:i] * (10 // i) == last_10_moves:
                  # Simulate the best response to the detected pattern
                  best_response = max(
                      [axl.Action.C, axl.Action.D],
                      key=lambda x: self.total_scores([x] * 10, last_10_moves)[0]
                  )
                  return best_response
  
      # Rule 6: Increase defection rate if more than 50 points behind
      if self.score < opponent.score - 50:
          self.defect_rate_increase = 20
      if self.defect_rate_increase > 0:
          self.defect_rate_increase -= 1
          return self._random.random_choice(0.6)
  
      # Rule 7: Mutual cooperation for the last 10 rounds
      if len(self.history) >= 10 and all(x == axl.Action.C for x in self.history[-10:]) and all(x == axl.Action.C for x in opponent.history[-10:]):
          return axl.Action.C
  
      # Rule 8: Reassess strategy every 100 rounds
      if len(self.history) % 100 == 0:
          self.rounds_since_last_reassessment = 0
          if self.score > opponent.score:
              self.defect_rate_increase = 0  # Maintain current approach
          else:
              self.defect_rate_increase = 100  # Slightly increase defection rate
      self.rounds_since_last_reassessment += 1
  
      # Rule 9: Use the best strategy from rounds 900-990
      if 900 <= len(self.history) < 991:
          if self.best_strategy is None:
              # Calculate the best strategy so far
              for i in range(1, len(self.history)):
                  avg_score = self.total_scores(self.history[:i], opponent.history[:i])[0] / i
                  if avg_score > self.best_avg_score:
                      self.best_avg_score = avg_score
                      self.best_strategy = self.history[i - 1]
          return self.best_strategy
  
      # Default action: Cooperate
      return action

# Here's a revised aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. For the next 3 rounds, play tit-for-tat:
# copy your opponent's previous move.  3. After the initial 4 rounds, if your
# opponent has cooperated (C) more than 75% of the time, always defect (D) to
# exploit their cooperation.  4. Otherwise, continue with a modified tit-for-tat
# approach:    - If the opponent cooperated (C) in the previous round, defect
# (D) in the current round.    - If the opponent defected (D) in the previous
# round, cooperate (C) in the current round.  5. Every 20 rounds, assess your
# opponent's behavior:    - If they've mostly cooperated, continue exploiting by
# defecting.    - If they've mostly defected, switch to strict tit-for-tat for
# the next 20 rounds.  6. If you're stuck in a cycle of mutual defection for
# more than 10 rounds, cooperate (C) for one round to attempt breaking the
# cycle.  7. In the last 50 rounds, if your cumulative score is higher than what
# you'd get from always defecting, continue your current strategy. Otherwise,
# switch to always defecting.  8. Regardless of the above rules, if at any point
# your opponent has defected for 5 consecutive rounds, switch to always
# defecting for the next 10 rounds.  9. Repeat these steps, continuously
# adapting to your opponent's behavior, until the game ends.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.exploit_mode = False
          self.mutual_defection_count = 0
          self.defect_streak = 0
          self.always_defect_until = -1
          self.assess_every_20_rounds = 20
          return axl.Action.D  # Start by defecting
  
      # Helper function to calculate cooperation percentage
      def cooperation_percentage(history):
          return history.cooperations / len(history) if len(history) > 0 else 0
  
      # Helper function to check if stuck in mutual defection
      def stuck_in_mutual_defection():
          return self.history[-10:].count(axl.Action.D) == 10 and opponent.history[-10:].count(axl.Action.D) == 10
  
      # Step 8: If opponent defected for 5 consecutive rounds, switch to always defecting for 10 rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.always_defect_until = len(self.history) + 10
  
      if len(self.history) <= self.always_defect_until:
          return axl.Action.D
  
      # Step 2: Tit-for-tat for the first 3 rounds after the initial defection
      if len(self.history) < 4:
          return opponent.history[-1]
  
      # Step 3: After 4 rounds, check if opponent cooperated more than 75%
      if len(self.history) == 4:
          if cooperation_percentage(opponent.history) > 0.75:
              self.exploit_mode = True
  
      # Step 3: If in exploit mode, always defect
      if self.exploit_mode:
          return axl.Action.D
  
      # Step 4: Modified tit-for-tat
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      else:
          return axl.Action.C
  
      # Step 5: Every 20 rounds, assess opponent's behavior
      if len(self.history) % 20 == 0:
          if cooperation_percentage(opponent.history) > 0.5:
              self.exploit_mode = True
          else:
              self.exploit_mode = False
  
      # Step 6: If stuck in mutual defection for more than 10 rounds, cooperate to break the cycle
      if stuck_in_mutual_defection():
          return axl.Action.C
  
      # Step 7: In the last 50 rounds, compare cumulative score with always defecting
      if len(self.history) >= 950:
          always_defect_score = len(self.history) * 1  # Always defecting gives 1 point per round
          if self.score < always_defect_score:
              return axl.Action.D
  
      # Default to tit-for-tat behavior
      return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After the two-round punishment, return
# to playing C.  5. Keep track of the opponent's defection rate. If it exceeds
# 30% over the last 50 rounds, switch to always playing D until their defection
# rate drops below 20%.  6. Implement a forgiveness mechanism: If the opponent
# plays C for five consecutive rounds after a series of defections, resume
# cooperative play.  7. In the last 10 rounds of the game, play according to the
# opponent's most frequent move in the previous 20 rounds.  8. If the opponent
# seems to be following a similar cooperative strategy (defection rate below 10%
# over the last 100 rounds), continue playing C to maintain mutual cooperation.
# 9. Occasionally (with 5% probability) play C even when the strategy suggests
# D, to allow for recovery from potential misunderstandings or noise.  10.
# Adjust the punishment duration based on the game's payoff structure: increase
# it to three rounds if the opponent's defection rate is above 15%, as the
# potential gain from defection (5) is significantly higher than the cooperative
# payoff (3).

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_rounds = 0
          self.defection_rate_threshold = 0.3
          self.forgiveness_counter = 0
          self.punishment_duration = 2
          return axl.Action.C
  
      # Helper function to calculate defection rate over the last N rounds
      def defection_rate(history, rounds):
          if len(history) < rounds:
              rounds = len(history)
          return history[-rounds:].count(axl.Action.D) / rounds if rounds > 0 else 0
  
      # Helper function to determine the most frequent move in the last N rounds
      def most_frequent_move(history, rounds):
          if len(history) < rounds:
              rounds = len(history)
          if history[-rounds:].count(axl.Action.C) > history[-rounds:].count(axl.Action.D):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 9: Occasionally play C with 5% probability
      if self._random.random_choice(0.05):
          return axl.Action.C
  
      # Step 7: In the last 10 rounds, play according to the opponent's most frequent move in the last 20 rounds
      if len(self.history) >= 990:
          return most_frequent_move(opponent.history, 20)
  
      # Step 3: If in punishment mode, continue punishing for the set duration
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Step 2: If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If the opponent played D in the previous round, start punishment
      if opponent.history[-1] == axl.Action.D:
          # Step 10: Adjust punishment duration based on defection rate
          if defection_rate(opponent.history, 100) > 0.15:
              self.punishment_duration = 3
          else:
              self.punishment_duration = 2
          self.punishment_rounds = self.punishment_duration
          return axl.Action.D
  
      # Step 5: Track opponent's defection rate over the last 50 rounds
      if defection_rate(opponent.history, 50) > self.defection_rate_threshold:
          # Switch to always playing D until defection rate drops below 20%
          if defection_rate(opponent.history, 50) > 0.3:
              self.defection_rate_threshold = 0.2
              return axl.Action.D
          elif defection_rate(opponent.history, 50) < 0.2:
              self.defection_rate_threshold = 0.3
  
      # Step 6: Forgiveness mechanism - if opponent plays C for 5 consecutive rounds, resume cooperation
      if opponent.history[-5:] == [axl.Action.C] * 5:
          return axl.Action.C
  
      # Step 8: If opponent's defection rate is below 10% over the last 100 rounds, continue cooperation
      if defection_rate(opponent.history, 100) < 0.1:
          return axl.Action.C
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C

# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. Keep track of the opponent's
# cooperation rate. If it falls below 40%, defect for the next 2 rounds, then
# reassess.  5. If you've defected for 3 consecutive rounds and the opponent's
# cooperation rate is above 60%, cooperate in the next round as a gesture of
# forgiveness.  6. If the score difference between you and your opponent exceeds
# 20 points in either direction, adopt the strategy of the player with the
# higher score for the next 5 rounds.  7. In the last 50 rounds, if your score
# is lower than the opponent's, increase your defection rate by 10%.  8. If
# you're in the last 10 rounds of the game, defect unless the opponent's
# cooperation rate in the last 20 rounds is above 80%.  9. Every 100 rounds,
# reassess your overall strategy based on the opponent's behavior and adjust
# your cooperation/defection ratio accordingly.  10. For any situation not
# covered by the above rules, cooperate if the opponent's overall cooperation
# rate is above 50%, otherwise defect.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_for_next_n_rounds = 0
          self.adopt_strategy_for_n_rounds = 0
          self.adopted_strategy = None
          return axl.Action.C
  
      # Helper function to calculate opponent's cooperation rate
      def cooperation_rate(history):
          return history.count(axl.Action.C) / len(history) if len(history) > 0 else 0
  
      # Helper function to adopt the strategy of the player with the higher score
      def adopt_higher_score_strategy():
          if self.score > opponent.score:
              return self.history[-1]  # Continue with our own strategy
          else:
              return opponent.history[-1]  # Mimic opponent's last move
  
      # Rule 6: Adopt the strategy of the player with the higher score for 5 rounds
      if self.adopt_strategy_for_n_rounds > 0:
          self.adopt_strategy_for_n_rounds -= 1
          return self.adopted_strategy
  
      # Rule 4: If opponent's cooperation rate falls below 40%, defect for the next 2 rounds
      if cooperation_rate(opponent.history[:]) < 0.4 and self.defect_for_next_n_rounds == 0:
          self.defect_for_next_n_rounds = 2
  
      if self.defect_for_next_n_rounds > 0:
          self.defect_for_next_n_rounds -= 1
          return axl.Action.D
  
      # Rule 5: If defected for 3 consecutive rounds and opponent's cooperation rate is above 60%, cooperate
      if self.consecutive_defections >= 3 and cooperation_rate(opponent.history[:]) > 0.6:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Rule 7: In the last 50 rounds, increase defection rate by 10% if losing
      if len(self.history) >= 950 and self.score < opponent.score:
          if self._random.random_choice(0.1):
              return axl.Action.D
  
      # Rule 8: In the last 10 rounds, defect unless opponent's cooperation rate in the last 20 rounds is above 80%
      if len(self.history) >= 990:
          if cooperation_rate(opponent.history[-20:]) > 0.8:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 9: Every 100 rounds, reassess strategy (not fully specified, so we skip this for now)
  
      # Rule 10: Default behavior based on opponent's overall cooperation rate
      if cooperation_rate(opponent.history[:]) > 0.5:
          return axl.Action.C
      else:
          return axl.Action.D
  
      # Rule 1: Start by cooperating in the first round (already handled by first_round check)
  
      # Rule 2: If opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to encourage cooperation.  2. If the opponent
# played C in the previous round, play C with 80% probability and D with 20%
# probability. This maintains cooperation while occasionally testing the
# opponent's response.  3. If the opponent played D in the previous round, play
# D in the next round.  4. Every 5 rounds, analyze the opponent's pattern of
# play:    - If they've cooperated more than 60% of the time, play C.    - If
# they've defected more than 60% of the time, play D.    - If their play is
# mixed, continue with the current strategy.  5. If the opponent has played C
# for 3 consecutive rounds, play C for the next 2 rounds to encourage a
# cooperative streak.  6. If the opponent defects after a period of mutual
# cooperation, play D for the next round, then return to step 2.  7. In the last
# 20 rounds, gradually increase the probability of playing D:    - Rounds
# 981-990: 50% D, 50% C    - Rounds 991-995: 70% D, 30% C    - Rounds 996-1000:
# 90% D, 10% C  8. Throughout the game, keep track of the cumulative score
# difference. If you're significantly behind (more than 20 points), increase the
# probability of playing D by 10% for the next 10 rounds.  9. Repeat these
# steps, continuously adapting based on the opponent's behavior and the game's
# progress.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperations by opponent
          self.behind_counter = 0  # Track rounds where we're behind by more than 20 points
          return axl.Action.C  # Start with cooperation
  
      # Helper function to calculate cooperation percentage
      def cooperation_percentage(history):
          return history.cooperations / len(history) if len(history) > 0 else 0
  
      # Step 2: If opponent played C last round, play C with 80% probability, D with 20%
      if opponent.history[-1] == axl.Action.C:
          if self._random.random_choice(0.8):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 3: If opponent played D last round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 4: Every 5 rounds, analyze opponent's pattern
      if len(self.history) % 5 == 0:
          coop_percent = cooperation_percentage(opponent.history)
          if coop_percent > 0.6:
              return axl.Action.C
          elif coop_percent < 0.4:
              return axl.Action.D
  
      # Step 5: If opponent has cooperated for 3 consecutive rounds, play C for the next 2 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          if len(self.history) < len(opponent.history) + 2:
              return axl.Action.C
  
      # Step 6: If opponent defects after mutual cooperation, play D next round
      if len(self.history) > 1 and self.history[-2:] == [axl.Action.C, axl.Action.C] and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 7: In the last 20 rounds, increase probability of playing D
      if len(self.history) >= 981:
          if len(self.history) <= 990:
              return self._random.random_choice(0.5)
          elif len(self.history) <= 995:
              return self._random.random_choice(0.7)
          else:
              return self._random.random_choice(0.9)
  
      # Step 8: If significantly behind, increase probability of playing D
      if self.score < opponent.score - 20:
          self.behind_counter = 10  # Increase D probability for the next 10 rounds
      if self.behind_counter > 0:
          self.behind_counter -= 1
          return self._random.random_choice(0.6)  # Increase D probability by 10%
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next round, then return to C.  4. Keep track of the opponent's cooperation
# rate. If it falls below 40% in the last 50 rounds, switch to playing D more
# frequently (70% of the time).  5. If the opponent's cooperation rate rises
# above 60% in the last 50 rounds, return to primarily cooperative play (90% C).
# 6. Every 100 rounds, play CCCD regardless of the opponent's actions. This
# serves as a signal of willingness to cooperate and forgive past defections.
# 7. In the last 20 rounds, mirror the opponent's overall cooperation rate from
# the previous 100 rounds.  8. If at any point mutual defection has occurred for
# more than 50 consecutive rounds, attempt to break the cycle by playing C for 5
# rounds straight.  9. Adjust the strategy if falling significantly behind: If
# your score is less than 80% of the maximum possible score at the halfway point
# (round 500), increase the frequency of D plays to 40% for the next 100 rounds.
# 10. In the final round, play D to protect against exploitation.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.signal_rounds = [100 * i for i in range(1, 11)]
          self.mirror_start_round = 980
          self.mirror_end_round = 1000
          self.halfway_point = 500
          self.adjustment_rounds = 100
          return axl.Action.C
  
      # Helper function to calculate cooperation rate in the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Helper function to check if mutual defection has occurred for more than 50 rounds
      def mutual_defection_streak():
          return all(self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, 51))
  
      # Step 2: If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If opponent played D in the previous round, play D, then return to C
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) > 1 and self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D
  
      # Step 4: Track opponent's cooperation rate in the last 50 rounds
      coop_rate_last_50 = cooperation_rate(opponent.history, 50)
      if coop_rate_last_50 < 0.4:
          return self._random.random_choice(0.3)  # Play D 70% of the time
  
      # Step 5: If cooperation rate rises above 60%, return to 90% C
      if coop_rate_last_50 > 0.6:
          return self._random.random_choice(0.9)  # Play C 90% of the time
  
      # Step 6: Every 100 rounds, play CCCD
      if len(self.history) in self.signal_rounds:
          signal_index = (len(self.history) - 1) % 4
          return [axl.Action.C, axl.Action.C, axl.Action.C, axl.Action.D][signal_index]
  
      # Step 7: In the last 20 rounds, mirror opponent's cooperation rate from the previous 100 rounds
      if self.mirror_start_round <= len(self.history) < self.mirror_end_round:
          coop_rate_last_100 = cooperation_rate(opponent.history, 100)
          return self._random.random_choice(coop_rate_last_100)
  
      # Step 8: If mutual defection has occurred for more than 50 consecutive rounds, play C for 5 rounds
      if mutual_defection_streak():
          if self.consecutive_defections < 5:
              self.consecutive_defections += 1
              return axl.Action.C
          else:
              self.consecutive_defections = 0
  
      # Step 9: Adjust strategy if falling behind at the halfway point
      if len(self.history) == self.halfway_point:
          max_possible_score = len(self.history) * 3  # Max score if all rounds were mutual cooperation
          if self.score < 0.8 * max_possible_score:
              self.adjustment_rounds = 100  # Increase D frequency for the next 100 rounds
      if self.adjustment_rounds > 0:
          self.adjustment_rounds -= 1
          return self._random.random_choice(0.6)  # Play D 40% of the time
  
      # Step 10: In the final round, play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. If the opponent has defected
# for three consecutive rounds, defect for the next round, then attempt to
# cooperate.  5. Keep track of the opponent's cooperation rate. If it falls
# below 40% over the last 50 rounds, defect for the next 5 rounds, then
# reassess.  6. If your score is more than 20 points behind your opponent's,
# increase your defection rate by 10% for the next 20 rounds, then return to the
# base strategy.  7. Every 100 rounds, if the mutual cooperation rate is above
# 80%, continue the current strategy. If it's below 60%, increase your defection
# rate by 5% for the next 50 rounds.  8. In rounds 900-950, play according to
# the opponent's most frequent action in the previous 100 rounds.  9. For the
# last 50 rounds, gradually increase your defection rate, reaching 100%
# defection in the final 10 rounds.  10. For all other situations not covered by
# the above rules, cooperate.  11. Reassess the effectiveness of this strategy
# every 200 rounds and adjust the thresholds and rates if necessary.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defection_rate = 0
          self.adjustment_rounds = 0
          self.defection_streak = 0
          self.cooperation_rate_check_rounds = 0
          self.cooperation_rate = 0
          self.behind_by_20_rounds = 0
          self.mutual_cooperation_check_rounds = 0
          self.endgame_defection_rate = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Rule 1: Start by cooperating in the first round (already handled above)
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          if self.consecutive_defections >= 3:
              # Rule 4: If the opponent has defected for three consecutive rounds, defect once, then cooperate
              self.consecutive_defections = 0
              return axl.Action.D
          return axl.Action.D
  
      # Rule 5: Track opponent's cooperation rate over the last 50 rounds
      if len(opponent.history) >= 50:
          self.cooperation_rate = cooperation_rate(opponent.history, 50)
          if self.cooperation_rate < 0.4:
              if self.cooperation_rate_check_rounds < 5:
                  self.cooperation_rate_check_rounds += 1
                  return axl.Action.D
              else:
                  self.cooperation_rate_check_rounds = 0
  
      # Rule 6: If your score is more than 20 points behind, increase defection rate by 10% for 20 rounds
      if self.score < opponent.score - 20:
          if self.behind_by_20_rounds < 20:
              self.behind_by_20_rounds += 1
              if self._random.random_choice(0.1):
                  return axl.Action.D
          else:
              self.behind_by_20_rounds = 0
  
      # Rule 7: Every 100 rounds, check mutual cooperation rate and adjust defection rate
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          mutual_cooperation_rate = cooperation_rate(self.history, 100) + cooperation_rate(opponent.history, 100) / 2
          if mutual_cooperation_rate < 0.6:
              self.defection_rate += 0.05
              self.mutual_cooperation_check_rounds = 50
          elif mutual_cooperation_rate > 0.8:
              self.defection_rate = 0
  
      if self.mutual_cooperation_check_rounds > 0:
          self.mutual_cooperation_check_rounds -= 1
          if self._random.random_choice(self.defection_rate):
              return axl.Action.D
  
      # Rule 8: In rounds 900-950, play according to the opponent's most frequent action in the last 100 rounds
      if 900 <= len(self.history) < 950:
          most_frequent_action = max(set(opponent.history[-100:]), key=opponent.history[-100:].count)
          return most_frequent_action
  
      # Rule 9: In the last 50 rounds, gradually increase defection rate, reaching 100% defection in the final 10 rounds
      if len(self.history) >= 950:
          rounds_left = 1000 - len(self.history)
          if rounds_left <= 50:
              self.endgame_defection_rate = min(1, (50 - rounds_left) / 40)
              if self._random.random_choice(self.endgame_defection_rate):
                  return axl.Action.D
  
      # Rule 10: For all other situations, cooperate
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round to establish a potentially cooperative
# relationship.  2. Keep track of the opponent's moves and your score
# difference.  3. If the opponent has defected in the last two rounds, defect.
# Otherwise:    - If you're behind in score, defect with 70% probability.    -
# If you're ahead or tied, defect with 50% probability.  4. Every 100 rounds,
# analyze the opponent's behavior:    - If they've cooperated more than 60% of
# the time, increase your cooperation probability by 10%.    - If they've
# defected more than 60% of the time, decrease your cooperation probability by
# 10%.  5. In the last 50 rounds, gradually increase your defection probability:
# - Start at your current defection rate and increase by 2% each round.    -
# However, if the opponent cooperates twice in a row, cooperate once in
# response.  6. If you're more than 30 points behind, enter an aggressive phase:
# - Defect with 80% probability for the next 20 rounds.    - Reassess after
# these 20 rounds and return to the standard strategy if the gap has closed.  7.
# If you're leading by more than 40 points, occasionally (10% chance) cooperate
# for two consecutive rounds to encourage the opponent's cooperation.  8. After
# any cooperation, base your next move on the opponent's response:    - If they
# cooperated, cooperate with 60% probability.    - If they defected, defect in
# the next round.  9. Every 200 rounds, introduce a random move to prevent
# becoming too predictable.  10. Continuously adjust your strategy based on the
# opponent's patterns and the score difference, becoming more cooperative if
# it's proving beneficial or more aggressive if you're consistently falling
# behind.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_prob = 0.5  # Initial cooperation probability
          self.aggressive_phase = False
          self.aggressive_rounds_left = 0
          self.last_defection_increase = 0
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate score difference
      def score_difference():
          return self.score - opponent.score
  
      # Helper function to adjust cooperation probability every 100 rounds
      def adjust_cooperation_prob():
          if len(self.history) % 100 == 0:
              opponent_coop_rate = opponent.history.cooperations / len(opponent.history)
              if opponent_coop_rate > 0.6:
                  self.cooperation_prob = min(1.0, self.cooperation_prob + 0.1)
              elif opponent_coop_rate < 0.4:
                  self.cooperation_prob = max(0.0, self.cooperation_prob - 0.1)
  
      # Helper function to handle the last 50 rounds
      def handle_last_50_rounds():
          rounds_left = 1000 - len(self.history)
          if rounds_left <= 50:
              self.cooperation_prob = max(0.0, self.cooperation_prob + 0.02)
              if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
                  return axl.Action.C
          return None
  
      # Helper function to handle aggressive phase
      def handle_aggressive_phase():
          if self.aggressive_phase:
              self.aggressive_rounds_left -= 1
              if self.aggressive_rounds_left <= 0:
                  self.aggressive_phase = False
              return self._random.random_choice(0.8)
          return None
  
      # Helper function to handle random move every 200 rounds
      def random_move():
          if len(self.history) % 200 == 0:
              return self._random.random_choice(0.5)
          return None
  
      # Adjust cooperation probability every 100 rounds
      adjust_cooperation_prob()
  
      # Handle last 50 rounds
      last_50_move = handle_last_50_rounds()
      if last_50_move is not None:
          return last_50_move
  
      # Handle aggressive phase if active
      aggressive_move = handle_aggressive_phase()
      if aggressive_move is not None:
          return aggressive_move
  
      # Handle random move every 200 rounds
      random_move_choice = random_move()
      if random_move_choice is not None:
          return random_move_choice
  
      # If opponent defected in the last two rounds, defect
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # If you're more than 30 points behind, enter aggressive phase
      if score_difference() < -30:
          self.aggressive_phase = True
          self.aggressive_rounds_left = 20
          return self._random.random_choice(0.8)
  
      # If you're leading by more than 40 points, occasionally cooperate for two rounds
      if score_difference() > 40 and self._random.random_choice(0.1):
          return axl.Action.C
  
      # If you're behind in score, defect with 70% probability
      if score_difference() < 0:
          return self._random.random_choice(0.7)
  
      # If you're ahead or tied, defect with 50% probability
      return self._random.random_choice(0.5)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After the two-round punishment, return
# to playing C.  5. Keep track of the opponent's defection rate. If it exceeds
# 30% over the last 50 rounds, switch to playing D until their defection rate
# drops below 20%.  6. If the opponent establishes a clear pattern of play, do
# not try to exploit it. Instead, continue with the base strategy.  7. In the
# last 20 rounds, play according to the opponent's defection rate for the entire
# game. If it's below 10%, always play C. If it's above 30%, always play D.
# Otherwise, continue with the base strategy.  8. Every 100 rounds, evaluate the
# success of your strategy. If your average score is below 2, become more
# defensive by increasing the punishment duration to three rounds.  9. If the
# opponent defects for 5 consecutive rounds, switch to always playing D for the
# next 10 rounds, then cautiously return to the base strategy by playing C.  10.
# After any series of mutual defections, attempt to rebuild cooperation by
# playing C for two consecutive rounds, regardless of the opponent's actions.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_counter = 0
          self.defection_rate_threshold = 0.3
          self.defensive_mode = False
          self.defection_streak = 0
          self.punishment_duration = 2
          self.mutual_defection_flag = False
          return axl.Action.C
  
      # Helper function to calculate defection rate over the last N rounds
      def defection_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.D) / N if N > 0 else 0
  
      # Helper function to evaluate success every 100 rounds
      def evaluate_success():
          if len(self.history) % 100 == 0 and len(self.history) > 0:
              avg_score = self.score / len(self.history)
              if avg_score < 2:
                  self.punishment_duration = 3
  
      # Check if we are in the last 20 rounds
      if len(self.history) >= 980:
          overall_defection_rate = defection_rate(opponent.history, len(opponent.history))
          if overall_defection_rate < 0.1:
              return axl.Action.C
          elif overall_defection_rate > 0.3:
              return axl.Action.D
          else:
              # Continue with the base strategy
              pass
  
      # Check if we are in defensive mode due to high defection rate
      if self.defensive_mode:
          if defection_rate(opponent.history, 50) < 0.2:
              self.defensive_mode = False
          else:
              return axl.Action.D
  
      # Check if opponent's defection rate exceeds 30% over the last 50 rounds
      if defection_rate(opponent.history, 50) > self.defection_rate_threshold:
          self.defensive_mode = True
          return axl.Action.D
  
      # Check for 5 consecutive defections
      if opponent.history[-5:] == [axl.Action.D] * 5:
          self.defection_streak = 10
  
      # If in defection streak punishment mode
      if self.defection_streak > 0:
          self.defection_streak -= 1
          return axl.Action.D
  
      # Handle mutual defection recovery
      if self.mutual_defection_flag:
          self.mutual_defection_flag = False
          return axl.Action.C
  
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.mutual_defection_flag = True
          return axl.Action.C
  
      # Handle punishment for opponent's defection
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.D:
          self.punishment_counter = self.punishment_duration
          return axl.Action.D
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C

# Here's a revised strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. Keep track of the opponent's
# cooperation rate. If their cooperation rate falls below 40%, defect for the
# next 2 rounds.  5. If you're ahead in cumulative score by 10 points or more,
# cooperate in the current round to encourage mutual cooperation.  6. If you're
# behind in cumulative score by 10 points or more, defect in the current round
# to catch up.  7. For the last 50 rounds of the game:    - If your overall
# score is higher, continue with the above strategy.    - If your overall score
# is lower, increase your defection rate by 20%.  8. For the last 10 rounds of
# the game:    - If your overall score is higher, always cooperate.    - If your
# overall score is lower, always defect.  9. If none of the above conditions are
# met, cooperate.  Follow these rules in the order presented for each round of
# the game, adjusting your strategy based on the opponent's behavior and the
# game's progress.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_counter = 0  # To track forced defections for 2 rounds
          return axl.Action.C  # Cooperate in the first round
  
      # Helper function to calculate opponent's cooperation rate
      def cooperation_rate():
          total_moves = len(opponent.history)
          if total_moves == 0:
              return 1  # Assume full cooperation if no moves yet
          return opponent.history.cooperations / total_moves
  
      # Helper function to check if we are in the last N rounds
      def in_last_n_rounds(n):
          return len(self.history) >= 1000 - n
  
      # Step 2: If opponent cooperated last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If opponent defected last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 4: Track opponent's cooperation rate and defect for 2 rounds if below 40%
      if cooperation_rate() < 0.4:
          if self.defect_counter < 2:
              self.defect_counter += 1
              return axl.Action.D
          else:
              self.defect_counter = 0  # Reset after 2 rounds of defection
  
      # Step 5: If ahead by 10 points or more, cooperate
      if self.score - opponent.score >= 10:
          return axl.Action.C
  
      # Step 6: If behind by 10 points or more, defect
      if opponent.score - self.score >= 10:
          return axl.Action.D
  
      # Step 7: For the last 50 rounds, adjust defection rate if behind
      if in_last_n_rounds(50):
          if self.score < opponent.score:
              if self._random.random_choice(0.2):  # Increase defection rate by 20%
                  return axl.Action.D
  
      # Step 8: For the last 10 rounds, always cooperate if ahead, always defect if behind
      if in_last_n_rounds(10):
          if self.score > opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 9: Default to cooperation if none of the above conditions are met
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to encourage cooperation.  2. If the opponent
# played C in the previous round, play C with 80% probability and D with 20%
# probability.  3. If the opponent played D in the previous round, play D.  4.
# If you're currently on a streak of 2 or more mutual D plays, switch to C for
# one round to attempt breaking the cycle.  5. Keep track of the opponent's
# cooperation rate. If it exceeds 70% over the last 20 rounds, play C. If it's
# below 30%, always play D.  6. Every 50 rounds, analyze the opponent's pattern.
# If they seem to be using a recognizable strategy (e.g., tit-for-tat), adjust
# your play to exploit it.  7. In the last 20 rounds, if your score is higher,
# continue with the current strategy. If you're behind, increase the probability
# of playing D to 90%.  8. Reassess and slightly adjust probabilities every 100
# rounds based on overall game performance.  9. Repeat steps 2-8 for the
# duration of the game, incorporating the adjustments from steps 6 and 8 as the
# game progresses.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.mutual_D_streak = 0
          return axl.Action.C  # Start with cooperation
  
      # Helper function to calculate opponent's cooperation rate over the last N rounds
      def cooperation_rate(opponent, N):
          if len(opponent.history) < N:
              N = len(opponent.history)
          return opponent.history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Step 2: If opponent played C in the last round, play C with 80% probability, D with 20%
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.8)
  
      # Step 3: If opponent played D in the last round, play D
      if opponent.history[-1] == axl.Action.D:
          # Step 4: Check for mutual D streak
          if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
              self.mutual_D_streak += 1
          else:
              self.mutual_D_streak = 0
  
          # If on a streak of 2 or more mutual D plays, switch to C for one round
          if self.mutual_D_streak >= 2:
              self.mutual_D_streak = 0  # Reset streak after breaking the cycle
              return axl.Action.C
  
          return axl.Action.D
  
      # Step 5: Track opponent's cooperation rate over the last 20 rounds
      coop_rate = cooperation_rate(opponent, 20)
      if coop_rate > 0.7:
          return axl.Action.C
      elif coop_rate < 0.3:
          return axl.Action.D
  
      # Step 6: Every 50 rounds, analyze opponent's pattern (simplified as a placeholder)
      if len(self.history) % 50 == 0:
          # Placeholder for pattern recognition logic
          pass
  
      # Step 7: In the last 20 rounds, adjust strategy based on score
      if len(self.history) >= 980:
          my_score, opponent_score = self.total_scores(self.history[-20:], opponent.history[-20:])
          if my_score < opponent_score:
              return self._random.random_choice(0.1)  # 90% chance to play D
  
      # Step 8: Reassess and adjust probabilities every 100 rounds (simplified as a placeholder)
      if len(self.history) % 100 == 0:
          # Placeholder for probability adjustment logic
          pass
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After punishing with D, return to
# playing C.  5. Keep track of the opponent's cooperation rate. If it falls
# below 30% over the last 20 rounds, switch to always playing D until their
# cooperation rate rises above 50% again.  6. In the last 5% of the game's
# rounds (i.e., the last 50 rounds in a 1000-round game), play D if your score
# is lower than or equal to the opponent's. Otherwise, continue with the regular
# strategy.  7. If at any point the opponent's score is more than 15 points
# higher than yours, play D until you've closed the gap to within 5 points.  8.
# Every 50 rounds, if you're in a state of mutual defection, attempt to re-
# establish cooperation by playing C for two consecutive rounds.  9. Adjust your
# strategy based on the opponent's pattern: If they seem to be using a similar
# reactive strategy, try to break defection cycles by playing C twice in a row.
# 10. If the opponent's moves appear random, default to playing D more often
# (70% of the time) while still occasionally playing C to allow for potential
# cooperation.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_counter = 0
          self.cooperation_rate_threshold = 0.3
          self.recovery_rate_threshold = 0.5
          self.defection_cycle_breaker = False
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Helper function to check if we are in the last 5% of the game
      def in_last_5_percent():
          return len(self.history) >= 0.95 * 1000
  
      # Helper function to check if mutual defection is happening
      def mutual_defection():
          return self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D
  
      # Step 2: If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C and self.punishment_counter == 0:
          return axl.Action.C
  
      # Step 3: If opponent played D in the previous round, punish with D for two rounds
      if opponent.history[-1] == axl.Action.D and self.punishment_counter == 0:
          self.punishment_counter = 2
  
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # Step 4: After punishing, return to playing C
      if self.punishment_counter == 0:
          return axl.Action.C
  
      # Step 5: Track opponent's cooperation rate over the last 20 rounds
      if cooperation_rate(opponent.history, 20) < self.cooperation_rate_threshold:
          self.defection_cycle_breaker = True
  
      if self.defection_cycle_breaker:
          if cooperation_rate(opponent.history, 20) > self.recovery_rate_threshold:
              self.defection_cycle_breaker = False
          else:
              return axl.Action.D
  
      # Step 6: In the last 5% of the game, play D if your score is lower or equal to the opponent's
      if in_last_5_percent():
          if self.score <= opponent.score:
              return axl.Action.D
  
      # Step 7: If opponent's score is more than 15 points higher, play D until the gap is within 5 points
      if opponent.score - self.score > 15:
          return axl.Action.D
      if opponent.score - self.score <= 5:
          return axl.Action.C
  
      # Step 8: Every 50 rounds, if in mutual defection, attempt to re-establish cooperation
      if len(self.history) % 50 == 0 and mutual_defection():
          return axl.Action.C
  
      # Step 9: If opponent seems to use a reactive strategy, break defection cycles by playing C twice
      if len(self.history) >= 2 and self.history[-2:] == [axl.Action.D, axl.Action.D] and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.C
  
      # Step 10: If opponent's moves appear random, play D 70% of the time
      if self._random.random_choice(0.7):
          return axl.Action.D
      else:
          return axl.Action.C

# Here's a revised strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect with a 70% probability and cooperate with a 30%
# probability.  4. Keep track of the opponent's cooperation rate. If their
# cooperation rate falls below 40% over the last 20 rounds, defect for the next
# round.  5. If you've been defecting for three consecutive rounds, cooperate in
# the next round to attempt to break a potential cycle of mutual defections.  6.
# Every 50 rounds, reassess your strategy:    - If your score is within 5% of
# your opponent's, continue with the current strategy.    - If you're trailing
# by more than 5%, increase your defection probability in step 3 to 80%.    - If
# you're leading by more than 5%, decrease your defection probability in step 3
# to 60%.  7. In the last 100 rounds, gradually increase your defection
# probability:    - In rounds 901-950, defect with a 60% probability when you
# would normally cooperate.    - In rounds 951-1000, defect with an 80%
# probability when you would normally cooperate.  8. In any situation not
# covered by the above rules, cooperate.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_prob = 0.7  # Initial defection probability
          self.consecutive_defections = 0  # Track consecutive defections
          return axl.Action.C  # Cooperate in the first round
  
      # Helper function to calculate opponent's cooperation rate over the last N rounds
      def cooperation_rate(opponent, N):
          recent_history = opponent.history[-N:]
          return recent_history.cooperations / N if len(recent_history) >= N else 1.0
  
      # Step 2: If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.C
  
      # Step 3: If opponent defected in the last round, defect with a certain probability
      if opponent.history[-1] == axl.Action.D:
          if self._random.random_choice(self.defect_prob):
              self.consecutive_defections += 1
              return axl.Action.D
          else:
              self.consecutive_defections = 0
              return axl.Action.C
  
      # Step 4: If opponent's cooperation rate over the last 20 rounds is below 40%, defect
      if cooperation_rate(opponent, 20) < 0.4:
          self.consecutive_defections += 1
          return axl.Action.D
  
      # Step 5: If you've defected for 3 consecutive rounds, cooperate to break the cycle
      if self.consecutive_defections >= 3:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Step 6: Every 50 rounds, reassess strategy
      if len(self.history) % 50 == 0:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if my_score < opponent_score * 0.95:  # Trailing by more than 5%
              self.defect_prob = 0.8
          elif my_score > opponent_score * 1.05:  # Leading by more than 5%
              self.defect_prob = 0.6
          else:  # Within 5% of opponent's score
              self.defect_prob = 0.7
  
      # Step 7: In the last 100 rounds, increase defection probability
      if len(self.history) >= 900:
          if len(self.history) <= 950:
              if self._random.random_choice(0.6):  # 60% chance to defect
                  return axl.Action.D
          else:
              if self._random.random_choice(0.8):  # 80% chance to defect
                  return axl.Action.D
  
      # Step 8: Default to cooperation if no other rule applies
      return axl.Action.C

# Here's a revised aggressive strategy for the iterated game:  1. Start by
# cooperating (C) in the first round.  2. If the opponent cooperated (C) in the
# previous round, defect (D) with a 70% probability and cooperate (C) with a 30%
# probability in the current round.  3. If the opponent defected (D) in the
# previous round, defect (D) in the current round.  4. If the opponent has
# cooperated for two consecutive rounds, defect (D) in the next round.  5. Every
# 30-50 rounds (randomly chosen), defect (D) regardless of the opponent's
# previous move.  6. In the last 5% of the game's rounds, always defect (D).  7.
# If at any point your score falls behind the opponent's by 10 points or more,
# defect (D) for the next 3 rounds, then return to step 2.  8. If the opponent
# has a pattern of alternating between C and D for 5 or more rounds, break the
# pattern by defecting (D) for 2 consecutive rounds.  9. Every 100 rounds,
# assess your performance:    - If your average score per round is below 2,
# increase the probability of defection in step 2 by 10% (up to a maximum of
# 90%).    - If your average score per round is above 3, decrease the
# probability of defection in step 2 by 10% (down to a minimum of 60%).  10. If
# mutual cooperation (C,C) has been achieved for 5 consecutive rounds, cooperate
# (C) for the next round to test if it can be maintained.  Follow these steps in
# order, applying the first applicable rule in each round.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_probability = 0.7
          self.last_defection_round = 0
          self.pattern_break_round = 0
          self.coop_streak = 0
          self.alternating_pattern = False
          return axl.Action.C
  
      # Helper function to check if opponent is alternating between C and D
      def is_alternating_pattern():
          if len(opponent.history) < 5:
              return False
          return all(opponent.history[i] != opponent.history[i + 1] for i in range(-5, -1))
  
      # Rule 6: Always defect in the last 5% of the game
      if len(self.history) >= 0.95 * 1000:
          return axl.Action.D
  
      # Rule 5: Defect every 30-50 rounds (randomly chosen)
      if len(self.history) - self.last_defection_round >= self._random.randint(30, 50):
          self.last_defection_round = len(self.history)
          return axl.Action.D
  
      # Rule 7: If behind by 10 points or more, defect for the next 3 rounds
      if self.score < opponent.score - 10:
          if len(self.history) - self.last_defection_round < 3:
              return axl.Action.D
          else:
              self.last_defection_round = len(self.history)
  
      # Rule 8: Break alternating pattern by defecting for 2 consecutive rounds
      if is_alternating_pattern():
          if len(self.history) - self.pattern_break_round < 2:
              return axl.Action.D
          else:
              self.pattern_break_round = len(self.history)
  
      # Rule 4: If opponent cooperated for two consecutive rounds, defect
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return axl.Action.D
  
      # Rule 2: If opponent cooperated in the previous round, defect with 70% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(self.defect_probability)
  
      # Rule 3: If opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 10: If mutual cooperation has been achieved for 5 consecutive rounds, cooperate
      if len(self.history) >= 5 and all(self.history[-i] == axl.Action.C and opponent.history[-i] == axl.Action.C for i in range(1, 6)):
          return axl.Action.C
  
      # Rule 9: Every 100 rounds, adjust defection probability based on performance
      if len(self.history) % 100 == 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.defect_probability = min(self.defect_probability + 0.1, 0.9)
          elif avg_score > 3:
              self.defect_probability = max(self.defect_probability - 0.1, 0.6)
  
      # Default to cooperation if no other rule applies
      return axl.Action.C

# N.B. I accidentally deleted the description

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_rounds = 0
          self.defect_streak = 0
          self.forced_defect_rounds = 0
          self.mixed_strategy_rounds = False
          self.cooperation_attempt = False
          self.pattern_detected = False
          self.pattern_length = 0
          self.pattern = []
          return axl.Action.C
  
      # Step 8: Check if score is more than 10% behind opponent's score
      total_possible_score = len(self.history) * 5
      if total_possible_score > 0:
          if self.score < 0.9 * opponent.score:
              self.forced_defect_rounds = 20
  
      # Step 7: In the last 10 rounds, play a mixed strategy
      if len(self.history) >= 990:
          return self._random.random_choice(0.3)
  
      # Step 6: After forced D, attempt to re-establish cooperation
      if self.forced_defect_rounds > 0:
          self.forced_defect_rounds -= 1
          if self.forced_defect_rounds == 0:
              self.cooperation_attempt = True
          return axl.Action.D
  
      if self.cooperation_attempt:
          self.cooperation_attempt = False
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              self.forced_defect_rounds = 10
              return axl.Action.D
  
      # Step 10: Reward consistent cooperation
      if opponent.history[-10:].count(axl.Action.C) == 10:
          return axl.Action.C
  
      # Step 5: If opponent plays D for 4 out of the last 6 rounds, switch to D for 10 rounds
      if len(opponent.history) >= 6 and opponent.history[-6:].count(axl.Action.D) >= 4:
          self.forced_defect_rounds = 10
          return axl.Action.D
  
      # Step 3: Punish with D for two rounds if opponent played D last round
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.D:
          self.punishment_rounds = 2
          return axl.Action.D
  
      # Step 2: If opponent played C last round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. For the majority of the game (rounds
# 1-980):    a. If the opponent cooperated in the previous round, cooperate.
# b. If the opponent defected in the previous round, defect with a 75%
# probability. Otherwise, cooperate.  3. Every 50 rounds, analyze the opponent's
# behavior:    a. If they've cooperated more than 70% of the time, increase
# cooperation by cooperating for the next 5 rounds regardless of their actions.
# b. If they've defected more than 70% of the time, increase defection by
# defecting for the next 5 rounds regardless of their actions.  4. If at any
# point your score falls more than 15 points behind the opponent's, switch to
# always defecting for the next 10 rounds, then return to the main strategy.  5.
# If you're ahead by more than 30 points, cooperate for the next 2 rounds
# regardless of the opponent's actions, then return to the main strategy.  6. In
# rounds 981-990, play a modified strategy:    a. If you're ahead in points,
# cooperate.    b. If you're behind or tied, defect.  7. In the final 10 rounds
# (991-1000), defect regardless of the opponent's actions.  8. Throughout the
# game, keep track of your success rate with different actions. Every 100
# rounds, slightly adjust the defection probability in step 2b (within a range
# of 70-80%) based on which probability has been more successful.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_prob = 0.75  # Initial defection probability
          self.coop_streak = 0     # Track cooperation streaks
          self.defect_streak = 0   # Track defection streaks
          self.force_defect = 0    # Force defection for N rounds
          self.force_coop = 0      # Force cooperation for N rounds
          self.behind_defect = 0   # Defect for 10 rounds if behind by 15 points
          self.ahead_coop = 0      # Cooperate for 2 rounds if ahead by 30 points
          return axl.Action.C
  
      # Round number
      round_number = len(self.history) + 1
  
      # Final 10 rounds: always defect
      if round_number > 990:
          return axl.Action.D
  
      # Rounds 981-990: modified strategy
      if 981 <= round_number <= 990:
          if self.score > opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Check if we are forced to defect or cooperate
      if self.behind_defect > 0:
          self.behind_defect -= 1
          return axl.Action.D
      if self.ahead_coop > 0:
          self.ahead_coop -= 1
          return axl.Action.C
      if self.force_defect > 0:
          self.force_defect -= 1
          return axl.Action.D
      if self.force_coop > 0:
          self.force_coop -= 1
          return axl.Action.C
  
      # Every 50 rounds, analyze opponent's behavior
      if round_number % 50 == 0:
          coop_rate = opponent.history.cooperations / len(opponent.history)
          if coop_rate > 0.7:
              self.force_coop = 5
          elif coop_rate < 0.3:
              self.force_defect = 5
  
      # Check if we are behind by more than 15 points
      if self.score < opponent.score - 15:
          self.behind_defect = 10
          return axl.Action.D
  
      # Check if we are ahead by more than 30 points
      if self.score > opponent.score + 30:
          self.ahead_coop = 2
          return axl.Action.C
  
      # Main strategy for rounds 1-980
      if round_number <= 980:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return self._random.random_choice(self.defect_prob)
  
      # Adjust defection probability every 100 rounds
      if round_number % 100 == 0:
          # Calculate success rates for cooperation and defection
          coop_success = sum(1 for i in range(len(self.history)) if self.history[i] == axl.Action.C and self.total_scores(self.history[i:i+1], opponent.history[i:i+1])[0] > 0)
          defect_success = sum(1 for i in range(len(self.history)) if self.history[i] == axl.Action.D and self.total_scores(self.history[i:i+1], opponent.history[i:i+1])[0] > 0)
          total_moves = len(self.history)
          if total_moves > 0:
              coop_rate = coop_success / total_moves
              defect_rate = defect_success / total_moves
              if defect_rate > coop_rate:
                  self.defect_prob = min(0.8, self.defect_prob + 0.01)
              else:
                  self.defect_prob = max(0.7, self.defect_prob - 0.01)
  
      # Default to cooperation in the first round
      return axl.Action.C



# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent defected in the
# previous round, defect with a 70% probability and cooperate with a 30%
# probability.  3. If the opponent cooperated in the previous round, cooperate
# with a 70% probability and defect with a 30% probability.  4. Every 100
# rounds, randomly choose to either cooperate or defect, regardless of the
# opponent's previous move.  5. In the last 20 rounds of the game, mirror the
# opponent's most recent move.  6. If your current score is more than 30 points
# behind your opponent's, increase the defection probability to 80% for the next
# 10 rounds, then reassess.  7. If you're ahead by more than 40 points, increase
# cooperation probability to 80% for the next 10 rounds to encourage the
# opponent's cooperation, then reassess.  8. If the opponent has defected for 3
# or more consecutive rounds, defect for the next 2 rounds, then return to the
# base strategy.  9. Assess the opponent's overall cooperation rate every 50
# rounds. If it's below 30%, increase your defection probability by 10% for the
# next 50 rounds.  10. If mutual cooperation has been achieved for 10
# consecutive rounds, continue cooperating until the opponent defects.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defection_probability = 0.3
          self.cooperation_probability = 0.7
          self.force_defect_rounds = 0
          self.force_cooperate_rounds = 0
          self.adjustment_rounds = 0
          self.mutual_cooperation_streak = 0
          return axl.Action.C
  
      # Helper function to adjust probabilities based on score difference
      def adjust_probabilities():
          score_diff = opponent.score - self.score
          if score_diff > 30:
              self.defection_probability = 0.8
              self.cooperation_probability = 0.2
              self.adjustment_rounds = 10
          elif score_diff < -40:
              self.defection_probability = 0.2
              self.cooperation_probability = 0.8
              self.adjustment_rounds = 10
  
      # Helper function to assess opponent's cooperation rate
      def assess_opponent_cooperation_rate():
          if len(opponent.history) % 50 == 0:
              cooperation_rate = opponent.history.cooperations / len(opponent.history)
              if cooperation_rate < 0.3:
                  self.defection_probability = min(1.0, self.defection_probability + 0.1)
                  self.cooperation_probability = 1 - self.defection_probability
  
      # Helper function to handle random move every 100 rounds
      def random_move_every_100_rounds():
          if len(self.history) % 100 == 0:
              return self._random.random_choice(0.5)
  
      # Helper function to mirror opponent's move in the last 20 rounds
      def mirror_opponent_last_20_rounds():
          if len(self.history) >= 980:
              return opponent.history[-1]
  
      # Adjust probabilities based on score difference
      if self.adjustment_rounds == 0:
          adjust_probabilities()
      else:
          self.adjustment_rounds -= 1
  
      # Assess opponent's cooperation rate every 50 rounds
      assess_opponent_cooperation_rate()
  
      # Random move every 100 rounds
      random_move = random_move_every_100_rounds()
      if random_move is not None:
          return random_move
  
      # Mirror opponent's move in the last 20 rounds
      if len(self.history) >= 980:
          return mirror_opponent_last_20_rounds()
  
      # Handle forced defection or cooperation after opponent's consecutive defections
      if self.force_defect_rounds > 0:
          self.force_defect_rounds -= 1
          return axl.Action.D
      if self.force_cooperate_rounds > 0:
          self.force_cooperate_rounds -= 1
          return axl.Action.C
  
      # Check for opponent's consecutive defections
      if opponent.history[-3:].count(axl.Action.D) == 3:
          self.force_defect_rounds = 2
          return axl.Action.D
  
      # Check for mutual cooperation streak
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.mutual_cooperation_streak += 1
      else:
          self.mutual_cooperation_streak = 0
  
      if self.mutual_cooperation_streak >= 10:
          return axl.Action.C
  
      # Base strategy: respond probabilistically based on opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(self.defection_probability)
      else:
          return self._random.random_choice(self.cooperation_probability)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After the two-round punishment, return
# to playing C.  5. Keep track of the opponent's defection rate. If it exceeds
# 30% over the last 20 rounds, switch to always playing D until their defection
# rate drops below 20% for at least 10 rounds.  6. If the opponent alternates
# between C and D consistently (for at least 5 cycles), respond by playing C to
# their D and D to their C to maximize payoff.  7. Implement a "forgiveness"
# mechanism: If the opponent plays C for 3 consecutive rounds after a series of
# defections, resume the cooperative strategy from step 2.  8. In the last 20
# rounds of the game, play a modified Tit-for-Tat: Copy the opponent's previous
# move, but with a 20% chance of playing C regardless of their last move to
# allow for potential cooperation.  9. Throughout the game, periodically (every
# 50 rounds) assess the opponent's overall strategy and adjust your defection
# threshold and punishment duration accordingly.  10. If at any point the
# opponent has defected for more than 80% of the total game rounds, switch to
# always defecting for the remainder of the game.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_counter = 0
          self.defection_rate_threshold = 0.3
          self.punishment_duration = 2
          self.always_defect = False
          self.alternating_detected = False
          self.alternating_counter = 0
          self.forgiveness_counter = 0
          self.defection_rate = 0
          self.defection_rate_below_20_counter = 0
          return axl.Action.C
  
      # Helper function to calculate defection rate over the last N rounds
      def defection_rate_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D) / n
  
      # Helper function to detect alternating pattern
      def detect_alternating_pattern():
          if len(opponent.history) < 10:
              return False
          last_10_moves = opponent.history[-10:]
          return all(last_10_moves[i] != last_10_moves[i + 1] for i in range(9))
  
      # Step 10: If opponent has defected more than 80% of the total game rounds, always defect
      if opponent.history.defections / len(opponent.history) > 0.8:
          return axl.Action.D
  
      # Step 9: Periodically adjust defection threshold and punishment duration every 50 rounds
      if len(self.history) % 50 == 0:
          self.defection_rate_threshold = min(0.5, self.defection_rate_threshold + 0.05)
          self.punishment_duration = min(5, self.punishment_duration + 1)
  
      # Step 6: Detect alternating pattern and respond accordingly
      if detect_alternating_pattern():
          self.alternating_detected = True
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Step 5: Track opponent's defection rate over the last 20 rounds
      if len(opponent.history) >= 20:
          self.defection_rate = defection_rate_last_n_rounds(20)
          if self.defection_rate > self.defection_rate_threshold:
              self.always_defect = True
          elif self.defection_rate < 0.2:
              self.defection_rate_below_20_counter += 1
              if self.defection_rate_below_20_counter >= 10:
                  self.always_defect = False
          else:
              self.defection_rate_below_20_counter = 0
  
      # If always defect mode is active, defect
      if self.always_defect:
          return axl.Action.D
  
      # Step 7: Forgiveness mechanism
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          self.punishment_counter = 0
          return axl.Action.C
  
      # Step 3 and 4: Punishment for defection
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.D:
          self.punishment_counter = self.punishment_duration
          return axl.Action.D
  
      # Step 2: If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 8: In the last 20 rounds, play modified Tit-for-Tat
      if len(self.history) >= 980:
          if self._random.random_choice(0.2):
              return axl.Action.C
          return opponent.history[-1]
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round with a 90% probability. Cooperate
# with a 10% probability to allow for reconciliation.  4. Keep track of the
# opponent's cooperation rate. If it falls below 30% over the last 50 rounds,
# defect for the next 5 rounds.  5. If your score is more than 20 points behind
# your opponent's, increase your defection probability to 50% for the next 10
# rounds.  6. Every 100 rounds, reassess your strategy:    - If your score is
# higher, maintain the current approach.    - If your score is lower, slightly
# increase your defection rate for the next 100 rounds.  7. In rounds 900-990,
# base your decision on the opponent's overall cooperation rate:    - If above
# 70%, always cooperate.    - If between 30-70%, use the basic strategy (rules
# 2-3).    - If below 30%, always defect.  8. In the last 10 rounds (991-1000),
# always defect.  9. If none of the above conditions are met, cooperate.  This
# strategy aims to balance cooperation and defection based on the opponent's
# behavior, adapts over time, and considers the game's length and payoff
# structure.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0  # Track defection streaks for rule 4
          self.defect_boost = 0   # Track boosted defection probability for rule 5
          self.defection_rate_increase = 0  # Track defection rate increase for rule 6
          return axl.Action.C  # Rule 1: Start by cooperating
  
      # Rule 9: Default to cooperation unless other conditions apply
      action = axl.Action.C
  
      # Rule 8: In the last 10 rounds (991-1000), always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 7: In rounds 900-990, base decision on opponent's overall cooperation rate
      if 900 <= len(self.history) < 990:
          opponent_coop_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_coop_rate > 0.7:
              return axl.Action.C
          elif opponent_coop_rate < 0.3:
              return axl.Action.D
          # Otherwise, fall back to basic strategy (rules 2-3)
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          action = axl.Action.C
      # Rule 3: If the opponent defected in the previous round, defect with 90% probability
      elif opponent.history[-1] == axl.Action.D:
          action = self._random.random_choice(0.1)
  
      # Rule 4: Track opponent's cooperation rate over the last 50 rounds
      if len(self.history) >= 50:
          recent_coop_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if recent_coop_rate < 0.3:
              self.defect_streak = 5  # Defect for the next 5 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Rule 5: If your score is more than 20 points behind, increase defection probability to 50% for 10 rounds
      if self.score < opponent.score - 20:
          self.defect_boost = 10
      if self.defect_boost > 0:
          self.defect_boost -= 1
          action = self._random.random_choice(0.5)
  
      # Rule 6: Every 100 rounds, reassess strategy
      if len(self.history) % 100 == 0:
          if self.score < opponent.score:
              self.defection_rate_increase += 0.05  # Slightly increase defection rate for the next 100 rounds
          else:
              self.defection_rate_increase = 0  # Reset defection rate increase if winning
  
      # Apply defection rate increase from rule 6
      if self.defection_rate_increase > 0:
          action = self._random.random_choice(self.defection_rate_increase)
  
      return action

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to test the opponent's willingness to cooperate.
# 2. If the opponent played C in the previous round, play C with 80% probability
# and D with 20% probability in the current round.  3. If the opponent played D
# in the previous round, play D in the current round.  4. Keep track of the
# opponent's overall cooperation rate. If their cooperation rate falls below
# 30%, always play D until their rate rises above 40%.  5. If you're currently
# on a streak of 5 or more mutual defections, play C in the next round to
# potentially break the cycle.  6. In the last 20 rounds of the game, if the
# opponent's overall cooperation rate is above 50%, continue with the strategy
# as normal. If it's below 50%, always play D.  7. Every 50 rounds, if the
# opponent's cooperation rate is below 40%, play C for two consecutive rounds to
# test if they're willing to shift to a more cooperative strategy.  8. For all
# other situations not covered by the above rules, play D.  9. Continuously
# adjust these probabilities and thresholds based on the opponent's behavior
# throughout the game to maximize overall payoff.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.mutual_defection_streak = 0
          return axl.Action.C  # Rule 1: Start with C
      
      # Helper function to calculate opponent's cooperation rate
      def cooperation_rate():
          total_moves = len(opponent.history)
          if total_moves == 0:
              return 0
          return opponent.history.cooperations / total_moves
      
      # Rule 4: If opponent's cooperation rate falls below 30%, always play D
      if cooperation_rate() < 0.3:
          if cooperation_rate() > 0.4:
              pass
          else:
              return axl.Action.D
      
      # Rule 6: In the last 20 rounds, if cooperation rate is below 50%, always play D
      if len(self.history) >= 980:
          if cooperation_rate() < 0.5:
              return axl.Action.D
      
      # Rule 2: If opponent played C in the previous round, play C with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.8)
      
      # Rule 3: If opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      
      # Rule 5: If on a streak of 5 or more mutual defections, play C to break the cycle
      if len(self.history) >= 5 and all(x == axl.Action.D for x in self.history[-5:]) and all(x == axl.Action.D for x in opponent.history[-5:]):
          return axl.Action.C
      
      # Rule 7: Every 50 rounds, if cooperation rate is below 40%, play C for two rounds
      if len(self.history) % 50 == 0 and cooperation_rate() < 0.4:
          if len(self.history) < 2 or self.history[-1] != axl.Action.C or self.history[-2] != axl.Action.C:
              return axl.Action.C
      
      # Default to D for all other situations
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After punishing with D, return to
# playing C.  5. If the opponent plays D for three consecutive rounds, switch to
# a more cautious approach:    a. Play D for the next three rounds.    b. Then
# attempt to re-establish cooperation by playing C.    c. If the opponent
# responds with C, return to step 2.    d. If the opponent responds with D,
# continue with step 5a.  6. Every 100 rounds, if mutual defection has been
# occurring for more than 50% of the last 100 rounds, attempt to break the cycle
# by playing C for two consecutive rounds.  7. In the last 5% of the game's
# rounds, adopt a more defensive strategy:    a. If your score is higher than or
# equal to the opponent's, continue with the regular strategy.    b. If your
# score is lower, play D to protect against end-game exploitation.  8. If at any
# point the opponent's score is more than 15% higher than yours, play D until
# you've closed the gap to within 5%.  9. Reset to cooperative behavior (return
# to step 2) after successfully closing the score gap.  10. If the opponent
# alternates between C and D for more than 5 consecutive rounds, respond by
# alternating between C and D, starting with C.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punish_count = 0
          self.cautious_mode = False
          self.cautious_count = 0
          self.alternating_mode = False
          self.alternating_count = 0
          return axl.Action.C
  
      # Helper function to check if opponent has defected for the last N rounds
      def opponent_defected_last_n_rounds(n):
          return all(move == axl.Action.D for move in opponent.history[-n:])
  
      # Helper function to check if opponent is alternating between C and D
      def opponent_alternating():
          if len(opponent.history) < 6:
              return False
          return all(opponent.history[i] != opponent.history[i + 1] for i in range(-6, -1))
  
      # Step 7: Defensive strategy in the last 5% of the game
      if len(self.history) >= 950:
          if self.score >= opponent.score:
              pass  # Continue with the regular strategy
          else:
              return axl.Action.D  # Play D if losing in the end-game
  
      # Step 8: If opponent's score is more than 15% higher, play D until gap is closed
      if opponent.score > self.score * 1.15:
          if opponent.score <= self.score * 1.05:
              return axl.Action.C  # Reset to cooperative behavior
          return axl.Action.D  # Play D to close the gap
  
      # Step 10: If opponent alternates between C and D for more than 5 rounds, alternate
      if opponent_alternating():
          self.alternating_mode = True
          self.alternating_count = 0
  
      if self.alternating_mode:
          self.alternating_count += 1
          if self.alternating_count % 2 == 0:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 3: Punish with D for two rounds if opponent defected last round
      if self.punish_count > 0:
          self.punish_count -= 1
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.D:
          self.punish_count = 2
          return axl.Action.D
  
      # Step 5: If opponent defects for 3 consecutive rounds, switch to cautious mode
      if opponent_defected_last_n_rounds(3):
          self.cautious_mode = True
          self.cautious_count = 0
  
      if self.cautious_mode:
          self.cautious_count += 1
          if self.cautious_count <= 3:
              return axl.Action.D  # Play D for 3 rounds
          else:
              self.cautious_mode = False
              return axl.Action.C  # Attempt to re-establish cooperation
  
      # Step 6: Every 100 rounds, if mutual defection > 50%, play C for 2 rounds
      if len(self.history) % 100 == 0 and len(self.history) >= 100:
          last_100_defections = self.history[-100:].count(axl.Action.D) + opponent.history[-100:].count(axl.Action.D)
          if last_100_defections > 100:
              return axl.Action.C  # Attempt to break the cycle with C
  
      # Step 2: If opponent played C last round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect with a 70% probability and cooperate with a 30% probability.  4.
# If the opponent has defected for three consecutive rounds, defect for the next
# round, then return to rule 2.  5. Every 50 rounds, assess your cumulative
# score compared to a theoretical maximum (if you had cooperated every round).
# If your score is less than 60% of this maximum, increase your defection
# probability in rule 3 by 10% for the next 50 rounds.  6. If you're in the last
# 50 rounds of the game, randomly choose to either always cooperate or always
# defect for these final rounds.  7. If the opponent has a pattern of
# alternating between cooperation and defection, match their pattern for the
# next 5 rounds.  8. If you defected in the last round and the opponent
# cooperated, cooperate in the next round as a gesture of forgiveness.  9. In
# all other situations, cooperate.  Apply these rules in the order presented,
# using the first rule that matches the current situation.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.7
          self.alternating_pattern_detected = False
          self.alternating_pattern_start = 0
          self.always_cooperate_or_defect = None
          return axl.Action.C
  
      # Rule 6: If in the last 50 rounds, randomly choose to always cooperate or defect
      if len(self.history) >= 950:
          if self.always_cooperate_or_defect is None:
              self.always_cooperate_or_defect = self._random.random_choice(0.5)
          return axl.Action.C if self.always_cooperate_or_defect else axl.Action.D
  
      # Rule 7: Detect alternating pattern and match it for 5 rounds
      if len(self.history) >= 2 and self.history[-1] != self.history[-2] and opponent.history[-1] != opponent.history[-2]:
          if not self.alternating_pattern_detected:
              self.alternating_pattern_detected = True
              self.alternating_pattern_start = len(self.history)
          if len(self.history) - self.alternating_pattern_start < 5:
              return opponent.history[-1]
          else:
              self.alternating_pattern_detected = False
  
      # Rule 4: If opponent defected for 3 consecutive rounds, defect this round
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Rule 2: If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent defected in the last round, defect with 70% probability, cooperate with 30%
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(self.defection_probability)
  
      # Rule 8: If I defected last round and opponent cooperated, cooperate as forgiveness
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 5: Every 50 rounds, adjust defection probability if score is less than 60% of max
      if len(self.history) % 50 == 0:
          max_score = len(self.history) * 3  # Theoretical max if both cooperated every round
          if self.score < 0.6 * max_score:
              self.defection_probability = min(1.0, self.defection_probability + 0.1)
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. Play D for the majority of the game, with
# the following exceptions:  3. If the opponent has played C for 3 consecutive
# rounds, play C in the next round. If they continue to play C, alternate
# between C and D to maximize payoff.  4. If your score is within 10 points of
# your opponent's score after 100 rounds, play C for 2 rounds to test for
# potential cooperation. If the opponent cooperates both times, implement rule
# 3. If not, revert to D.  5. Every 50 rounds, assess your average score per
# round. If it's below 2, play C for the next round to potentially initiate
# cooperation.  6. In rounds 900-990, always play D to secure maximum points in
# the endgame.  7. For the final 10 rounds (991-1000), play C only if the
# opponent has cooperated in at least 7 of the previous 10 rounds. Otherwise,
# play D.  8. For any situation not covered by the above rules, play D.  This
# strategy maintains an aggressive approach while incorporating limited,
# strategic cooperation to potentially increase overall payoff.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if opponent has cooperated in at least 7 of the last 10 rounds
      def opponent_cooperated_in_last_7_of_10():
          return opponent.history[-10:].count(axl.Action.C) >= 7
  
      # Helper function to check if opponent has cooperated for the last 3 rounds
      def opponent_cooperated_last_3():
          return opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]
  
      # Helper function to calculate average score per round
      def average_score():
          if len(self.history) == 0:
              return 0
          return self.score / len(self.history)
  
      # First round: play D
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: In rounds 900-990, always play D
      if 900 <= len(self.history) <= 990:
          return axl.Action.D
  
      # Rule 7: For the final 10 rounds (991-1000), play C only if the opponent has cooperated in at least 7 of the previous 10 rounds
      if 991 <= len(self.history) <= 1000:
          if opponent_cooperated_in_last_7_of_10():
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 3: If the opponent has played C for 3 consecutive rounds, play C in the next round, then alternate C and D
      if opponent_cooperated_last_3():
          if len(self.history) % 2 == 0:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 4: After 100 rounds, if your score is within 10 points of your opponent's score, play C for 2 rounds to test cooperation
      if len(self.history) > 100 and abs(self.score - opponent.score) <= 10:
          if len(self.history) % 2 == 0:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 5: Every 50 rounds, assess your average score per round. If it's below 2, play C for the next round
      if len(self.history) % 50 == 0 and average_score() < 2:
          return axl.Action.C
  
      # Default: Play D
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D once, return to
# playing C in the following round to test if the opponent is willing to
# cooperate again.  5. If the opponent plays D for five consecutive rounds,
# switch to a tit-for-tat strategy (mirroring the opponent's previous move) for
# the next 20 rounds. After 20 rounds, attempt to re-establish cooperation by
# playing C.  6. In the last 10 rounds of the game, play tit-for-tat to balance
# between cooperation and protection against end-game exploitation.  7. Keep a
# rolling average of the opponent's cooperation rate over the last 50 rounds. If
# this rate drops below 30%, play D until it rises above 40%, then resume the
# normal strategy.  8. Every 100 rounds, analyze the opponent's pattern of play.
# If a predictable pattern is detected, adjust the strategy to maximize payoff
# against that pattern for the next 100 rounds.  9. If at any point your score
# is more than 50 points lower than the opponent's, play D for 10 rounds, then
# resume the normal strategy.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punished = False
          self.tit_for_tat_mode = False
          self.tit_for_tat_counter = 0
          self.defection_streak = 0
          self.cooperation_rate = []
          self.pattern_analysis_counter = 0
          self.low_score_mode = False
          self.low_score_counter = 0
          return axl.Action.C
  
      # Update cooperation rate over the last 50 rounds
      if len(opponent.history) >= 50:
          recent_cooperations = opponent.history[-50:].count(axl.Action.C)
          cooperation_rate = recent_cooperations / 50
          self.cooperation_rate.append(cooperation_rate)
      else:
          cooperation_rate = opponent.history.cooperations / len(opponent.history)
  
      # Rule 7: If cooperation rate drops below 30%, defect until it rises above 40%
      if cooperation_rate < 0.30:
          return axl.Action.D
      elif cooperation_rate > 0.40 and self.low_score_mode:
          self.low_score_mode = False
  
      # Rule 9: If score is more than 50 points lower than opponent's, defect for 10 rounds
      if self.score < opponent.score - 50 and not self.low_score_mode:
          self.low_score_mode = True
          self.low_score_counter = 10
  
      if self.low_score_mode:
          self.low_score_counter -= 1
          if self.low_score_counter == 0:
              self.low_score_mode = False
          return axl.Action.D
  
      # Rule 6: In the last 10 rounds, play tit-for-tat
      if len(self.history) >= 990:
          return opponent.history[-1]
  
      # Rule 5: If opponent defects for 5 consecutive rounds, switch to tit-for-tat for 20 rounds
      if opponent.history[-5:] == [axl.Action.D] * 5 and not self.tit_for_tat_mode:
          self.tit_for_tat_mode = True
          self.tit_for_tat_counter = 20
  
      if self.tit_for_tat_mode:
          self.tit_for_tat_counter -= 1
          if self.tit_for_tat_counter == 0:
              self.tit_for_tat_mode = False
          return opponent.history[-1]
  
      # Rule 2: If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent played D in the previous round, play D as punishment
      if opponent.history[-1] == axl.Action.D and not self.punished:
          self.punished = True
          return axl.Action.D
  
      # Rule 4: After punishing with D once, return to playing C
      if self.punished:
          self.punished = False
          return axl.Action.C
  
      # Rule 8: Every 100 rounds, analyze opponent's pattern (not implemented in detail)
      if len(self.history) % 100 == 0:
          self.pattern_analysis_counter += 1
          # Placeholder for pattern analysis logic
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. In the second round, cooperate if the
# opponent cooperated in the first round; otherwise, defect.  3. For subsequent
# rounds:    a. If the opponent cooperated in the previous round, cooperate.
# b. If the opponent defected in the previous round, defect with a 75%
# probability. Otherwise, cooperate.  4. If your score falls 10 points or more
# behind your opponent's, switch to always defecting for the next 5 rounds, then
# return to the main strategy.  5. If your opponent has defected for 3
# consecutive rounds, defect for the next 3 rounds, then return to the main
# strategy.  6. Every 25 rounds, assess the opponent's cooperation rate:    a.
# If it's above 70%, increase your cooperation probability by 5% for the next 25
# rounds.    b. If it's below 30%, decrease your cooperation probability by 5%
# for the next 25 rounds.  7. In the last 20 rounds:    a. If your score is
# higher, play a mixed strategy of 60% cooperation and 40% defection.    b. If
# your score is lower or tied, play a mixed strategy of 40% cooperation and 60%
# defection.  8. If you and your opponent have been alternating between
# cooperation and defection for 5 consecutive rounds, cooperate for the next 2
# rounds to attempt to break the cycle.  9. Every 50 rounds, reassess your
# overall strategy:    a. If your score is significantly higher (20+ points),
# slightly increase your cooperation rate.    b. If your score is significantly
# lower (20+ points), slightly decrease your cooperation rate.  10. If mutual
# defection has occurred for 10 consecutive rounds, attempt to restart
# cooperation by cooperating for the next 2 rounds, regardless of the opponent's
# actions.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_probability = 0.75  # Default cooperation probability after opponent defects
          self.defect_streak = 0  # Track opponent's consecutive defections
          self.alternating_streak = 0  # Track alternating cooperation/defection pattern
          self.defect_mode = 0  # Track rounds left in defect mode
          self.adjustment_rounds = 0  # Track rounds left in cooperation probability adjustment
          self.last_adjustment_round = 0  # Track the last round when cooperation rate was adjusted
          self.mutual_defection_streak = 0  # Track mutual defection streak
          return axl.Action.C  # Cooperate in the first round
  
      # Helper function to check alternating cooperation/defection pattern
      def check_alternating():
          if len(self.history) < 5:
              return False
          return all(self.history[-i] != opponent.history[-i] for i in range(1, 6))
  
      # Helper function to calculate opponent's cooperation rate
      def cooperation_rate():
          return opponent.history.cooperations / len(opponent.history)
  
      # Step 4: If score falls behind by 10 or more, switch to defect mode for 5 rounds
      if self.score + 10 <= opponent.score and self.defect_mode == 0:
          self.defect_mode = 5
  
      # Step 5: If opponent defects for 3 consecutive rounds, defect for the next 3 rounds
      if opponent.history[-3:] == [axl.Action.D] * 3:
          self.defect_mode = 3
  
      # Step 6: Every 25 rounds, adjust cooperation probability based on opponent's cooperation rate
      if len(self.history) % 25 == 0 and len(self.history) != self.last_adjustment_round:
          coop_rate = cooperation_rate()
          if coop_rate > 0.7:
              self.cooperation_probability = min(1.0, self.cooperation_probability + 0.05)
          elif coop_rate < 0.3:
              self.cooperation_probability = max(0.0, self.cooperation_probability - 0.05)
          self.last_adjustment_round = len(self.history)
  
      # Step 7: In the last 20 rounds, play a mixed strategy based on score
      if len(self.history) >= 980:
          if self.score > opponent.score:
              return self._random.random_choice(0.6)
          else:
              return self._random.random_choice(0.4)
  
      # Step 8: If alternating cooperation/defection for 5 rounds, cooperate for 2 rounds
      if check_alternating():
          self.alternating_streak = 2
      if self.alternating_streak > 0:
          self.alternating_streak -= 1
          return axl.Action.C
  
      # Step 9: Every 50 rounds, reassess overall strategy
      if len(self.history) % 50 == 0 and len(self.history) != self.last_adjustment_round:
          if self.score >= opponent.score + 20:
              self.cooperation_probability = min(1.0, self.cooperation_probability + 0.05)
          elif self.score + 20 <= opponent.score:
              self.cooperation_probability = max(0.0, self.cooperation_probability - 0.05)
  
      # Step 10: If mutual defection for 10 rounds, cooperate for 2 rounds
      if self.history[-10:] == [axl.Action.D] * 10 and opponent.history[-10:] == [axl.Action.D] * 10:
          self.mutual_defection_streak = 2
      if self.mutual_defection_streak > 0:
          self.mutual_defection_streak -= 1
          return axl.Action.C
  
      # Step 2: Cooperate in the second round if opponent cooperated in the first round
      if len(self.history) == 1:
          return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
  
      # Step 3: Main strategy logic
      if self.defect_mode > 0:
          self.defect_mode -= 1
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return self._random.random_choice(self.cooperation_probability)

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent defected in the
# previous round, defect in the current round.  3. If the opponent cooperated in
# the previous round, cooperate with a 70% probability and defect with a 30%
# probability.  4. Every 100 rounds, analyze the opponent's behavior:    - If
# they cooperated more than 70% of the time, increase your cooperation
# probability by 10%.    - If they defected more than 70% of the time, decrease
# your cooperation probability by 10%.  5. If your overall score is lower than
# the opponent's after 250, 500, or 750 rounds, become more aggressive for the
# next 25 rounds by reducing your cooperation probability by 20%.  6. In the
# last 50 rounds, adjust your strategy based on the opponent's overall behavior:
# - If they've been mostly cooperative, maintain your current strategy.    - If
# they've been mostly defecting, always defect.  7. Every 10 rounds, introduce a
# random action (C or D) to avoid becoming too predictable.  8. If the opponent
# has a consistent pattern (e.g., alternating C and D), adapt your strategy to
# exploit it.  9. For all other situations not covered by the above rules, use
# your current cooperation probability to decide whether to cooperate or defect.
# 10. Continuously adjust your strategy based on its performance, increasing
# aggression if falling behind and becoming more cooperative if consistently
# ahead.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_prob = 0.7  # Initial cooperation probability
          self.aggressive_mode = False  # Flag for aggressive mode
          self.aggressive_rounds = 0  # Counter for aggressive rounds
          self.random_rounds = 0  # Counter for random action rounds
  
      # Helper function to adjust cooperation probability based on opponent's behavior
      def adjust_coop_prob():
          if len(self.history) % 100 == 0:
              coop_rate = opponent.history.cooperations / len(opponent.history)
              if coop_rate > 0.7:
                  self.coop_prob = min(1.0, self.coop_prob + 0.1)
              elif coop_rate < 0.3:
                  self.coop_prob = max(0.0, self.coop_prob - 0.1)
  
      # Helper function to check if we should enter aggressive mode
      def check_aggressive_mode():
          if len(self.history) in [250, 500, 750]:
              my_score, opp_score = self.total_scores(self.history, opponent.history)
              if my_score < opp_score:
                  self.aggressive_mode = True
                  self.aggressive_rounds = 25
                  self.coop_prob = max(0.0, self.coop_prob - 0.2)
  
      # Helper function to handle the last 50 rounds
      def handle_last_50_rounds():
          if len(self.history) >= 950:
              coop_rate = opponent.history.cooperations / len(opponent.history)
              if coop_rate < 0.5:
                  return axl.Action.D  # Always defect if opponent mostly defected
              else:
                  return None  # Maintain current strategy if opponent mostly cooperated
  
      # Helper function to introduce random action every 10 rounds
      def random_action():
          if len(self.history) % 10 == 0:
              return self._random.random_choice(0.5)
  
      # Helper function to detect and exploit patterns (e.g., alternating C and D)
      def detect_pattern():
          if len(opponent.history) >= 2:
              if opponent.history[-2:] == [axl.Action.C, axl.Action.D]:
                  return axl.Action.D  # Exploit alternating pattern by defecting
              elif opponent.history[-2:] == [axl.Action.D, axl.Action.C]:
                  return axl.Action.C  # Exploit alternating pattern by cooperating
          return None
  
      # Step 1: First round, always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Step 2: If opponent defected last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If opponent cooperated last round, cooperate with 70% probability
      if opponent.history[-1] == axl.Action.C:
          if self._random.random_choice(self.coop_prob):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 4: Every 100 rounds, adjust cooperation probability
      adjust_coop_prob()
  
      # Step 5: Check if we should enter aggressive mode
      check_aggressive_mode()
  
      # Step 6: Handle the last 50 rounds
      last_50_action = handle_last_50_rounds()
      if last_50_action is not None:
          return last_50_action
  
      # Step 7: Every 10 rounds, introduce a random action
      random_act = random_action()
      if random_act is not None:
          return random_act
  
      # Step 8: Detect and exploit patterns
      pattern_action = detect_pattern()
      if pattern_action is not None:
          return pattern_action
  
      # Step 9: Default action based on current cooperation probability
      return self._random.random_choice(self.coop_prob)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If your opponent played C in the previous
# round, play C.  3. If your opponent played D in the previous round, play D in
# the next round, then return to playing C.  4. Keep track of your opponent's
# cooperation rate. If it falls below 40% in the last 20 rounds, switch to
# always playing D until their cooperation rate improves above 60% in the last
# 20 rounds.  5. If your average score per round falls below 2.0 over the last
# 50 rounds, play D for the next 5 rounds, then reassess.  6. In the last 10
# rounds of the game, mirror your opponent's most frequent action from the
# previous 20 rounds.  7. If your opponent seems to be following a similar
# cooperative strategy (generally reciprocating your moves), continue with the
# cooperative approach outlined in steps 1-3.  8. Every 100 rounds, if you're in
# a state of mutual defection, attempt to restart cooperation by playing C for 2
# consecutive rounds.  9. Adjust your strategy if the opponent shows a clear
# pattern. If they always defect after you cooperate twice, for example, avoid
# consecutive cooperation.  10. If the game has passed the 800th round, become
# slightly more forgiving: allow up to two consecutive defections before
# retaliating.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0
          self.coop_streak = 0
          self.mutual_defection = False
          self.forgiving_mode = False
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          return history[-N:].count(axl.Action.C) / N if len(history) >= N else history.cooperations / len(history)
  
      # Helper function to calculate average score over the last N rounds
      def average_score(N):
          if len(self.history) < N:
              N = len(self.history)
          if N == 0:
              return 0
          total_score, _ = self.total_scores(self.history[-N:], opponent.history[-N:])
          return total_score / N
  
      # Step 2: If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If opponent played D in the previous round, play D, then return to C
      if opponent.history[-1] == axl.Action.D:
          if self.defect_streak == 0:
              self.defect_streak = 1
              return axl.Action.D
          else:
              self.defect_streak = 0
              return axl.Action.C
  
      # Step 4: Check opponent's cooperation rate over the last 20 rounds
      if len(self.history) >= 20:
          coop_rate = cooperation_rate(opponent.history, 20)
          if coop_rate < 0.4:
              self.mutual_defection = True
          elif coop_rate > 0.6:
              self.mutual_defection = False
  
      if self.mutual_defection:
          return axl.Action.D
  
      # Step 5: Check if average score over the last 50 rounds is below 2.0
      if len(self.history) >= 50 and average_score(50) < 2.0:
          if self.coop_streak < 5:
              self.coop_streak += 1
              return axl.Action.D
          else:
              self.coop_streak = 0
  
      # Step 6: In the last 10 rounds, mirror opponent's most frequent action from the last 20 rounds
      if len(self.history) >= 990:
          if len(opponent.history) >= 20:
              most_frequent_action = max(set(opponent.history[-20:]), key=opponent.history[-20:].count)
          else:
              most_frequent_action = max(set(opponent.history), key=opponent.history.count)
          return most_frequent_action
  
      # Step 7: If opponent reciprocates, continue cooperation
      if len(self.history) > 1 and self.history[-2] == opponent.history[-2]:
          return axl.Action.C
  
      # Step 8: Every 100 rounds, attempt to restart cooperation if in mutual defection
      if len(self.history) % 100 == 0 and self.mutual_defection:
          if self.defect_streak == 0:
              self.defect_streak = 1
              return axl.Action.C
          else:
              self.defect_streak = 0
              return axl.Action.C
  
      # Step 9: Avoid consecutive cooperation if opponent defects after two cooperations
      if len(self.history) >= 2 and self.history[-2:] == [axl.Action.C, axl.Action.C] and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 10: After 800 rounds, become more forgiving
      if len(self.history) > 800:
          if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round with a 2/3 probability. Otherwise,
# cooperate.  4. In the last 5% of the game's rounds (or last 50 rounds,
# whichever is smaller), always defect regardless of the opponent's actions.  5.
# After every 25 rounds, calculate the opponent's defection rate for all
# previous rounds. If this rate exceeds 40%, switch to always defecting for the
# next 10 rounds before returning to the main strategy.  6. Check the score
# difference every 50 rounds. If your score is more than 25 points behind your
# opponent's, increase the probability of defection after opponent's defection
# to 3/4 for the next 25 rounds.  7. If both players have defected for 5
# consecutive rounds, attempt to break the cycle by cooperating in the next
# round.  8. Reset to the main strategy after any temporary changes from points
# 5, 6, or 7.  9. If the opponent's actions seem to follow a pattern, adjust
# your strategy accordingly. For example, if they alternate between cooperation
# and defection, match their pattern.  10. In the absence of sufficient history
# for any calculation, default to the main strategy (points 2 and 3).

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0
          self.always_defect_until = 0
          self.increased_defection_prob_until = 0
          self.break_cycle = False
          return axl.Action.C
  
      # Get the current round number
      current_round = len(self.history)
      total_rounds = self.match_attributes['length']
  
      # 4. Always defect in the last 5% of rounds or last 50 rounds, whichever is smaller
      if current_round >= total_rounds - min(50, total_rounds // 20):
          return axl.Action.D
  
      # 5. After every 25 rounds, check opponent's defection rate and switch to always defecting if necessary
      if current_round % 25 == 0:
          opponent_defection_rate = opponent.history.defections / current_round
          if opponent_defection_rate > 0.4:
              self.always_defect_until = current_round + 10
  
      # 6. Every 50 rounds, check score difference and adjust defection probability if necessary
      if current_round % 50 == 0:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if opponent_score - my_score > 25:
              self.increased_defection_prob_until = current_round + 25
  
      # 7. If both players have defected for 5 consecutive rounds, attempt to break the cycle
      if self.history[-5:] == [axl.Action.D] * 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          self.break_cycle = True
  
      # 8. Reset to the main strategy after any temporary changes
      if self.always_defect_until > current_round:
          return axl.Action.D
      if self.break_cycle:
          self.break_cycle = False
          return axl.Action.C
  
      # 9. Detect opponent's pattern (e.g., alternating between C and D) and adjust
      if len(opponent.history) >= 4 and opponent.history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # 2. Cooperate if the opponent cooperated in the previous round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. Defect with a probability based on opponent's previous defection
      if opponent.history[-1] == axl.Action.D:
          if current_round <= self.increased_defection_prob_until:
              return self._random.random_choice(0.75)
          return self._random.random_choice(2 / 3)
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C

# Here's a revised aggressive strategy for the iterated normal-form game:  1.
# Start by defecting (D) in the first round.  2. Keep track of the opponent's
# cooperation rate over the last 10 rounds.  3. If the opponent's cooperation
# rate is below 30%, always defect.  4. If the opponent's cooperation rate is
# between 30% and 70%:    a. Defect with 70% probability    b. Cooperate with
# 30% probability  5. If the opponent's cooperation rate is above 70%:    a.
# Defect with 60% probability    b. Cooperate with 40% probability  6. Every 25
# rounds, assess your cumulative score compared to the opponent's:    a. If
# you're behind by more than 10%, increase your defection probability by 10% for
# the next 25 rounds    b. If you're ahead by more than 10%, decrease your
# defection probability by 5% for the next 25 rounds  7. In the last 20 rounds:
# a. If your score is behind, always defect    b. If your score is ahead, mirror
# the opponent's last move  8. Every 100 rounds, cooperate twice in a row to
# test if the opponent is willing to establish mutual cooperation.  9. If mutual
# cooperation is achieved for 5 consecutive rounds, switch to a tit-for-tat
# strategy for the next 10 rounds before reverting to the main strategy.  10.
# Repeat steps 2-9 for the duration of the game, continuously adapting based on
# the opponent's behavior and relative scores.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.7  # Default defection probability
          self.rounds_since_last_assessment = 0
          self.mutual_cooperation_streak = 0
          self.tit_for_tat_counter = 0
          return axl.Action.D  # Start by defecting
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          if N == 0:
              return 0
          return history[-N:].count(axl.Action.C) / N
  
      # Helper function to adjust defection probability based on score difference
      def adjust_defection_probability():
          if self.rounds_since_last_assessment >= 25:
              my_score, opponent_score = self.total_scores(self.history, opponent.history)
              if my_score > 0 and opponent_score > 0:
                  score_diff = (my_score - opponent_score) / my_score
                  if score_diff < -0.1:
                      self.defection_probability = min(1.0, self.defection_probability + 0.1)
                  elif score_diff > 0.1:
                      self.defection_probability = max(0.0, self.defection_probability - 0.05)
              self.rounds_since_last_assessment = 0
  
      # Helper function to handle tit-for-tat mode
      def tit_for_tat():
          self.tit_for_tat_counter -= 1
          return opponent.history[-1]
  
      # Check if we are in the last 20 rounds
      if len(self.history) >= 980:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if my_score < opponent_score:
              return axl.Action.D  # Always defect if behind
          else:
              return opponent.history[-1]  # Mirror opponent's last move if ahead
  
      # Every 100 rounds, cooperate twice to test for mutual cooperation
      if len(self.history) % 100 == 0 or len(self.history) % 100 == 1:
          return axl.Action.C
  
      # Check for mutual cooperation streak
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.mutual_cooperation_streak += 1
      else:
          self.mutual_cooperation_streak = 0
  
      # If mutual cooperation is achieved for 5 consecutive rounds, switch to tit-for-tat
      if self.mutual_cooperation_streak >= 5:
          self.tit_for_tat_counter = 10
          self.mutual_cooperation_streak = 0
  
      # If in tit-for-tat mode, follow tit-for-tat strategy
      if self.tit_for_tat_counter >= 1:
          return tit_for_tat()
  
      # Calculate opponent's cooperation rate over the last 10 rounds
      coop_rate = cooperation_rate(opponent.history, 10)
  
      # Adjust defection probability every 25 rounds
      self.rounds_since_last_assessment += 1
      adjust_defection_probability()
  
      # Apply the main strategy based on the opponent's cooperation rate
      if coop_rate < 0.3:
          return axl.Action.D  # Always defect if cooperation rate is below 30%
      elif 0.3 <= coop_rate <= 0.7:
          return self._random.random_choice(0.3)  # Defect with 70%, cooperate with 30%
      else:
          return self._random.random_choice(0.4)  # Defect with 60%, cooperate with 40%

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next three rounds, then return to C.  4. Keep track of the opponent's
# cooperation rate. If it falls below 70% in the last 50 rounds, switch to
# always playing D.  5. If the opponent plays D for five consecutive rounds,
# switch to a tit-for-tat strategy (mirroring the opponent's previous move) for
# the next 50 rounds.  6. After 50 rounds of tit-for-tat, if the opponent's
# cooperation rate has improved to above 80%, return to the main strategy.
# Otherwise, continue with tit-for-tat.  7. In the last 20 rounds, if the
# opponent's overall cooperation rate is above 90%, continue playing C.
# Otherwise, play D.  8. Reassess the effectiveness of the strategy every 100
# rounds. If your average score per round is below 2.5, increase the sensitivity
# to defection by reducing the thresholds in steps 4 and 7 by 5%.  9. If at any
# point the opponent switches back to consistent cooperation (plays C for 5
# consecutive rounds), return to playing C.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_count = 0
          self.tit_for_tat_mode = False
          self.tit_for_tat_rounds = 0
          self.sensitivity = 0.7
          self.cooperation_threshold = 0.9
          self.tit_for_tat_threshold = 0.8
          self.defection_streak = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate
      def cooperation_rate(history, window=None):
          if window:
              history = history[-window:]
          return history.count(axl.Action.C) / len(history) if history else 0
  
      # Step 9: If opponent switches back to consistent cooperation (5 consecutive C's), return to C
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.C] * 5:
          self.tit_for_tat_mode = False
          self.defection_streak = 0
          return axl.Action.C
  
      # Step 5: If opponent plays D for 5 consecutive rounds, switch to tit-for-tat for 50 rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          self.tit_for_tat_mode = True
          self.tit_for_tat_rounds = 50
  
      # Step 6: After 50 rounds of tit-for-tat, check cooperation rate and decide whether to return to main strategy
      if self.tit_for_tat_mode:
          self.tit_for_tat_rounds -= 1
          if self.tit_for_tat_rounds <= 0:
              if cooperation_rate(opponent.history[:], 50) > self.tit_for_tat_threshold:
                  self.tit_for_tat_mode = False
              else:
                  self.tit_for_tat_rounds = 50  # Continue tit-for-tat
          return opponent.history[-1]  # Tit-for-tat: mirror opponent's last move
  
      # Step 2: If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          self.defection_streak = 0
          return axl.Action.C
  
      # Step 3: If opponent played D in the previous round, play D for the next 3 rounds
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
          if self.defection_streak <= 3:
              return axl.Action.D
          else:
              self.defection_streak = 0
              return axl.Action.C
  
      # Step 4: Track opponent's cooperation rate over the last 50 rounds
      if len(opponent.history) >= 50 and cooperation_rate(opponent.history[:], 50) < self.sensitivity:
          return axl.Action.D
  
      # Step 7: In the last 20 rounds, adjust strategy based on overall cooperation rate
      if len(self.history) >= 980:
          if cooperation_rate(opponent.history[:]) > self.cooperation_threshold:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 8: Reassess strategy every 100 rounds and adjust sensitivity if needed
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2.5:
              self.sensitivity *= 0.95
              self.cooperation_threshold *= 0.95
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. Every 7-13 rounds (randomly
# chosen), regardless of the opponent's previous move, cooperate. This
# introduces unpredictability.  5. In the last 10 rounds, play a mixed strategy:
# cooperate with 30% probability and defect with 70% probability.  6. After
# every 50 rounds, assess the cumulative score difference. If you're more than
# 10 points behind, increase your defection probability to 60% for the next 10
# rounds, then return to the main strategy.  7. If you and your opponent have
# been in a cycle of mutual defection for more than 3 consecutive rounds,
# attempt to break the cycle by cooperating once.  8. Keep track of the
# opponent's cooperation rate. If they cooperate more than 80% of the time over
# the last 50 rounds, increase your cooperation rate to 90% to capitalize on
# their behavior.  9. If the opponent seems to be alternating between
# cooperation and defection, match their pattern for 5 rounds, then return to
# the main strategy.  10. Adjust your strategy every 100 rounds based on the
# opponent's overall pattern of play, slightly increasing cooperation or
# defection rates to optimize payoffs.  11. Continue this pattern for the
# duration of the game, constantly adapting based on the opponent's behavior and
# your relative score.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperate_turn = self._random.randint(7, 13)
          self.defection_cycle_count = 0
          self.defection_streak = 0
          self.cooperation_rate = 0.5
          self.adjustment_round = 100
          self.defection_boost = False
          self.defection_boost_rounds = 0
          return axl.Action.C
  
      # Round number
      round_number = len(self.history)
  
      # 1. Start by cooperating in the first round (already handled by first_round check)
  
      # 2. If the opponent cooperated in the previous round, cooperate in the current round.
      if opponent.history[-1] == axl.Action.C:
          action = axl.Action.C
      # 3. If the opponent defected in the previous round, defect in the current round.
      else:
          action = axl.Action.D
  
      # 4. Every 7-13 rounds (randomly chosen), cooperate regardless of the opponent's move.
      if round_number == self.cooperate_turn:
          action = axl.Action.C
          self.cooperate_turn += self._random.randint(7, 13)
  
      # 5. In the last 10 rounds, play a mixed strategy: cooperate with 30% probability.
      if round_number >= 990:
          action = self._random.random_choice(0.3)
  
      # 6. After every 50 rounds, assess the score difference and adjust defection probability.
      if round_number % 50 == 0 and round_number > 0:
          my_score, opponent_score = self.total_scores(self.history[-50:], opponent.history[-50:])
          if opponent_score - my_score > 10:
              self.defection_boost = True
              self.defection_boost_rounds = 10
  
      if self.defection_boost:
          action = self._random.random_choice(0.6)
          self.defection_boost_rounds -= 1
          if self.defection_boost_rounds == 0:
              self.defection_boost = False
  
      # 7. If in a cycle of mutual defection for more than 3 rounds, cooperate to break the cycle.
      if self.history[-3:] == [axl.Action.D] * 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          action = axl.Action.C
  
      # 8. Track opponent's cooperation rate over the last 50 rounds and adjust cooperation rate.
      if round_number >= 50:
          opponent_cooperations = opponent.history[-50:].count(axl.Action.C)
          if opponent_cooperations / 50 > 0.8:
              self.cooperation_rate = 0.9
          else:
              self.cooperation_rate = 0.5
  
      # 9. If opponent alternates between cooperation and defection, match their pattern for 5 rounds.
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.D]:
          if len(opponent.history) >= 5 and all(opponent.history[-i] != opponent.history[-i-1] for i in range(1, 5)):
              action = opponent.history[-1]
  
      # 10. Adjust strategy every 100 rounds based on opponent's overall pattern.
      if round_number % 100 == 0 and round_number > 0:
          opponent_cooperations = opponent.history.cooperations
          if opponent_cooperations / round_number > 0.5:
              self.cooperation_rate += 0.1
          else:
              self.cooperation_rate -= 0.1
          self.cooperation_rate = max(0, min(1, self.cooperation_rate))
  
      # Return the final action, possibly adjusted by cooperation rate.
      return self._random.random_choice(self.cooperation_rate) if action == axl.Action.C else action

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to signal willingness to cooperate.  2. If the
# opponent played C in the previous round, play C with 80% probability and D
# with 20% probability.  3. If the opponent played D in the previous round, play
# D.  4. If mutual cooperation (C,C) has occurred for 3 consecutive rounds,
# continue playing C until the opponent defects.  5. If mutual defection (D,D)
# has occurred for 3 consecutive rounds, play C once to attempt breaking the
# cycle.  6. Every 20 rounds, analyze the opponent's overall behavior:    - If
# they've cooperated more than 60% of the time, increase the probability of
# playing C in step 2 to 90%.    - If they've cooperated less than 40% of the
# time, decrease the probability of playing C in step 2 to 70%.  7. In the last
# 20 rounds, if the opponent has been cooperative (played C more than 60% of the
# time), continue with the current strategy. Otherwise, always play D.  8.
# Repeat steps 2-7 for the duration of the game.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_cooperations = 0
          self.consecutive_defections = 0
          self.cooperation_probability = 0.8
          return axl.Action.C  # Start by playing C
  
      # Update consecutive cooperation and defection counters
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.consecutive_cooperations += 1
          self.consecutive_defections = 0
      elif self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
      else:
          self.consecutive_cooperations = 0
          self.consecutive_defections = 0
  
      # Step 4: If mutual cooperation has occurred for 3 consecutive rounds, continue playing C
      if self.consecutive_cooperations >= 3:
          return axl.Action.C
  
      # Step 5: If mutual defection has occurred for 3 consecutive rounds, play C once to break the cycle
      if self.consecutive_defections >= 3:
          return axl.Action.C
  
      # Step 2: If the opponent played C in the previous round, play C with a certain probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(self.cooperation_probability)
  
      # Step 3: If the opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 6: Every 20 rounds, adjust cooperation probability based on opponent's behavior
      if len(self.history) % 20 == 0:
          opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_cooperation_rate > 0.6:
              self.cooperation_probability = 0.9
          elif opponent_cooperation_rate < 0.4:
              self.cooperation_probability = 0.7
          else:
              self.cooperation_probability = 0.8
  
      # Step 7: In the last 20 rounds, if the opponent has been cooperative, continue the strategy, otherwise always play D
      if len(self.history) >= 980:
          opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_cooperation_rate <= 0.6:
              return axl.Action.D
  
      # Default action (should not reach here)
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After the two punishment rounds, return
# to playing C.  5. If the opponent plays D for five consecutive rounds, switch
# to always playing D for the next 20 rounds.  6. After 20 rounds of consistent
# D, attempt to restart cooperation by playing C for one round.  7. If the
# opponent responds with C to the cooperation attempt, resume the main strategy
# from step 2. If they respond with D, continue playing D for another 20 rounds
# before attempting cooperation again.  8. To account for potential mistakes,
# allow for one "forgiveness" move every 10 rounds. If the opponent defects but
# has mostly cooperated in the last 10 rounds, respond with C instead of the
# usual punishment.  9. In the last 10 rounds of the game, play whatever action
# the opponent used most frequently in the previous 20 rounds.  10. Throughout
# the game, if the opponent's pattern matches your own moves for any 10
# consecutive rounds, consider them cooperative and be more lenient with
# punishments (reduce punishment to one round instead of two).

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_rounds = 0
          self.defection_streak = 0
          self.d_mode = 0
          self.forgiveness_counter = 0
          return axl.Action.C
  
      # Check if we are in D-mode (after 5 consecutive defections)
      if self.d_mode > 0:
          self.d_mode -= 1
          if self.d_mode == 0:
              return axl.Action.C  # Attempt to restart cooperation
          return axl.Action.D
  
      # Check for 5 consecutive defections by the opponent
      if opponent.history[-5:] == [axl.Action.D] * 5:
          self.d_mode = 20
          return axl.Action.D
  
      # Forgiveness logic: every 10 rounds, allow one forgiveness move
      if len(self.history) % 10 == 0:
          recent_cooperations = opponent.history[-10:].count(axl.Action.C)
          if recent_cooperations >= 7 and opponent.history[-1] == axl.Action.D:
              return axl.Action.C
  
      # Punishment logic: if in punishment mode, continue defecting
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Main strategy: respond to opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.punishment_rounds = 2  # Punish for 2 rounds
          return axl.Action.D
      else:
          return axl.Action.C
  
      # Endgame strategy: in the last 10 rounds, mimic the opponent's most frequent action
      if len(self.history) >= 990:
          if opponent.history[-20:].count(axl.Action.D) > opponent.history[-20:].count(axl.Action.C):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Check for 10 consecutive matching moves (cooperative pattern)
      if self.history[-10:] == opponent.history[-10:]:
          self.punishment_rounds = 1  # Be more lenient with punishment

# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. Keep track of the opponent's
# cooperation rate. If it falls below 40% over the last 20 rounds, defect for
# the next two rounds.  5. If your score is more than 15 points behind your
# opponent's, defect for the next round.  6. If there have been 5 consecutive
# rounds of mutual defection, cooperate in the next round to attempt breaking
# the cycle.  7. In the last 20 rounds, base your decision on the opponent's
# overall cooperation rate:    - If their cooperation rate is above 60%,
# cooperate.    - If it's between 40% and 60%, mirror their last move.    - If
# it's below 40%, defect.  8. Every 50 rounds, evaluate the success of your
# strategy:    - If your average score per round is below 2, increase your
# defection rate slightly.    - If it's above 3, maintain your current strategy.
# 9. In all other situations, cooperate.  10. Regardless of other conditions, if
# the opponent has cooperated for the last 5 rounds, cooperate.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_mutual_defections = 0
          self.defect_for_next_two_rounds = 0
          self.defection_rate_adjustment = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, n):
          if len(history) < n:
              n = len(history)
          return history[-n:].count(axl.Action.C) / n if n > 0 else 0
  
      # Helper function to check if mutual defection occurred in the last round
      def mutual_defection():
          return self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D
  
      # Step 10: If the opponent has cooperated for the last 5 rounds, cooperate
      if opponent.history[-5:].count(axl.Action.C) == 5:
          return axl.Action.C
  
      # Step 4: Track opponent's cooperation rate over the last 20 rounds
      if cooperation_rate(opponent.history, 20) < 0.4:
          self.defect_for_next_two_rounds = 2
  
      # Step 5: If your score is more than 15 points behind, defect for the next round
      if self.score < opponent.score - 15:
          return axl.Action.D
  
      # Step 6: If there have been 5 consecutive rounds of mutual defection, cooperate
      if self.consecutive_mutual_defections >= 5:
          self.consecutive_mutual_defections = 0
          return axl.Action.C
  
      # Step 7: In the last 20 rounds, base decision on opponent's overall cooperation rate
      if len(self.history) >= 980:
          overall_coop_rate = cooperation_rate(opponent.history, len(opponent.history))
          if overall_coop_rate > 0.6:
              return axl.Action.C
          elif 0.4 <= overall_coop_rate <= 0.6:
              return opponent.history[-1]
          else:
              return axl.Action.D
  
      # Step 8: Every 50 rounds, evaluate the success of the strategy
      if len(self.history) % 50 == 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.defection_rate_adjustment += 0.1
          elif avg_score > 3:
              self.defection_rate_adjustment = 0
  
      # Step 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 4 (continued): Defect for the next two rounds if opponent's cooperation rate is low
      if self.defect_for_next_two_rounds > 0:
          self.defect_for_next_two_rounds -= 1
          return axl.Action.D
  
      # Step 6 (continued): Track consecutive mutual defections
      if mutual_defection():
          self.consecutive_mutual_defections += 1
      else:
          self.consecutive_mutual_defections = 0
  
      # Step 9: In all other situations, cooperate
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round to potentially establish a cooperative
# pattern.  2. If the opponent cooperated in the previous round, cooperate (C)
# with a 70% probability and defect (D) with a 30% probability.  3. If the
# opponent defected in the previous round, defect (D) with an 80% probability
# and cooperate (C) with a 20% probability.  4. Every 100 rounds, analyze the
# opponent's overall pattern:    - If they've cooperated more than 60% of the
# time, increase your cooperation probability by 10% for the next 50 rounds.
# - If they've defected more than 60% of the time, decrease your cooperation
# probability by 10% for the next 50 rounds.  5. If your score is more than 75
# points behind your opponent's, increase your defection probability by 20% for
# the next 30 rounds.  6. If you're ahead by more than 100 points, increase your
# cooperation probability by 20% for the next 20 rounds.  7. In the last 50
# rounds, gradually increase your defection probability by 2% each round.  8. If
# the opponent has defected for 3 consecutive rounds, defect (D) for the next 2
# rounds before returning to the main strategy.  Apply these rules in the order
# presented, using the first applicable rule in each round. After each
# adjustment, ensure probabilities remain between 0% and 100%.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_prob = 0.7  # Initial cooperation probability
          self.defect_prob = 0.3  # Initial defection probability
          self.adjustment_rounds = 0  # Rounds left for probability adjustment
          self.defect_streak = 0  # Track opponent's defection streak
          self.extra_defect_rounds = 0  # Extra rounds to defect after 3 consecutive defections
          self.last_adjustment_round = 0  # Last round when adjustment was made
  
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 8: If the opponent has defected for 3 consecutive rounds, defect for the next 2 rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.extra_defect_rounds = 2
      if self.extra_defect_rounds > 0:
          self.extra_defect_rounds -= 1
          return axl.Action.D
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate with 70% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(self.coop_prob)
  
      # Rule 3: If the opponent defected in the previous round, defect with 80% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.8)
  
      # Rule 4: Every 100 rounds, analyze the opponent's overall pattern
      if len(self.history) % 100 == 0 and len(self.history) != self.last_adjustment_round:
          coop_rate = opponent.history.cooperations / len(opponent.history)
          if coop_rate > 0.6:
              self.coop_prob = min(self.coop_prob + 0.1, 1.0)
          elif coop_rate < 0.4:
              self.coop_prob = max(self.coop_prob - 0.1, 0.0)
          self.last_adjustment_round = len(self.history)
  
      # Rule 5: If your score is more than 75 points behind, increase defection probability by 20% for 30 rounds
      if opponent.score - self.score > 75 and self.adjustment_rounds == 0:
          self.defect_prob = min(self.defect_prob + 0.2, 1.0)
          self.adjustment_rounds = 30
  
      # Rule 6: If you're ahead by more than 100 points, increase cooperation probability by 20% for 20 rounds
      if self.score - opponent.score > 100 and self.adjustment_rounds == 0:
          self.coop_prob = min(self.coop_prob + 0.2, 1.0)
          self.adjustment_rounds = 20
  
      # Rule 7: In the last 50 rounds, gradually increase defection probability by 2% each round
      if len(self.history) >= 950:
          self.defect_prob = min(self.defect_prob + 0.02, 1.0)
  
      # Decrease adjustment rounds if any
      if self.adjustment_rounds > 0:
          self.adjustment_rounds -= 1
  
      # Default behavior: cooperate with coop_prob, defect with defect_prob
      return self._random.random_choice(self.coop_prob)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next two rounds as punishment.  4. After the two-round punishment, return
# to playing C.  5. Keep track of the opponent's cooperation rate. If it falls
# below 40% in the last 50 rounds, switch to always playing D until their
# cooperation rate improves above 50%.  6. If mutual defection occurs for more
# than 10 consecutive rounds, attempt to break the cycle by playing C for one
# round.  7. In the last 10 rounds of the game, continue with the established
# strategy without changing behavior.  8. Ignore any apparent patterns in the
# opponent's play to avoid potential exploitation.  9. Every 100 rounds, if your
# score is lower than what you'd get from always defecting, switch to always
# defecting for the next 10 rounds before reverting to the main strategy.  10.
# If at any point your score is more than 20% higher than what you'd get from
# always cooperating, continue with the current strategy without changes.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_rounds = 0
          self.defection_streak = 0
          self.always_defect = False
          self.cooperation_rate_check_round = 0
          return axl.Action.C
  
      # Track opponent's cooperation rate over the last 50 rounds
      if len(opponent.history) >= 50:
          recent_cooperations = opponent.history[-50:].count(axl.Action.C)
          cooperation_rate = recent_cooperations / 50
      else:
          cooperation_rate = 1  # Assume full cooperation if less than 50 rounds
  
      # Track mutual defection streak
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
      else:
          self.defection_streak = 0
  
      # Rule 5: If opponent's cooperation rate falls below 40%, switch to always defect
      if cooperation_rate < 0.4:
          self.always_defect = True
      elif cooperation_rate > 0.5:
          self.always_defect = False
  
      # Rule 6: If mutual defection for more than 10 rounds, break the cycle with C
      if self.defection_streak > 10:
          return axl.Action.C
  
      # Rule 9: Every 100 rounds, check if score is lower than always defecting
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          always_defect_score = len(self.history) * 1  # Always defect would score 1 per round
          if self.score < always_defect_score:
              self.cooperation_rate_check_round = len(self.history) + 10
              self.always_defect = True
  
      # If in the 10-round defecting phase, continue defecting
      if len(self.history) < self.cooperation_rate_check_round:
          return axl.Action.D
  
      # Rule 10: If score is more than 20% higher than always cooperating, continue current strategy
      always_cooperate_score = len(self.history) * 3  # Always cooperate would score 3 per round
      if self.score > always_cooperate_score * 1.2:
          return self.history[-1]  # Continue with the last action
  
      # Rule 7: In the last 10 rounds, continue with the established strategy
      if len(self.history) >= 990:
          return self.history[-1]
  
      # Rule 2: If opponent played C last round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent played D last round, punish with D for two rounds
      if opponent.history[-1] == axl.Action.D:
          if self.punishment_rounds < 2:
              self.punishment_rounds += 1
              return axl.Action.D
          else:
              self.punishment_rounds = 0
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect with a 70% probability and cooperate with a 30%
# probability.  4. Keep track of the opponent's cooperation rate over the last
# 10 rounds. If it falls below 30%, defect for the next round.  5. Every 20
# rounds, compare your score to your opponent's. If you're behind by more than
# 15 points, increase your defection probability to 80% for the next 5 rounds.
# 6. If you've been defecting for 5 consecutive rounds, cooperate in the next
# round as a gesture to potentially break a cycle of mutual defection.  7. In
# the last 5% of the game (50 rounds for a 1000-round game), gradually increase
# your defection probability. Start at 50% and increase by 10% every 10 rounds.
# 8. If the opponent has a consistent pattern of alternating between cooperation
# and defection, match their pattern.  9. Every 100 rounds, reset your strategy
# to the initial cooperative state for one round to allow for strategy
# adaptation.  10. For all other situations not covered by the above rules,
# cooperate.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defection_probability = 0.7
          self.defection_boost_rounds = 0
          return axl.Action.C
  
      # Rule 8: Detect alternating pattern and match it
      if len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]:
          return opponent.history[-1]
  
      # Rule 4: Track opponent's cooperation rate over the last 10 rounds
      if len(opponent.history) >= 10:
          last_10_cooperations = opponent.history[-10:].count(axl.Action.C)
          if last_10_cooperations / 10 < 0.3:
              return axl.Action.D
  
      # Rule 5: Every 20 rounds, compare scores and adjust defection probability
      if len(self.history) % 20 == 0 and len(self.history) > 0:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if opponent_score - my_score > 15:
              self.defection_probability = 0.8
              self.defection_boost_rounds = 5
  
      # Rule 6: If defecting for 5 consecutive rounds, cooperate
      if self.consecutive_defections >= 5:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Rule 7: In the last 5% of the game, increase defection probability
      total_rounds = 1000
      if len(self.history) >= 0.95 * total_rounds:
          rounds_left = total_rounds - len(self.history)
          if rounds_left % 10 == 0:
              self.defection_probability = min(1.0, 0.5 + (0.1 * (total_rounds - rounds_left) // 10))
  
      # Rule 9: Every 100 rounds, reset to cooperation
      if len(self.history) % 100 == 0:
          return axl.Action.C
  
      # Rule 2 and 3: Cooperate if opponent cooperated last round, else defect with probability
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          if self.defection_boost_rounds > 0:
              self.defection_boost_rounds -= 1
              return self._random.random_choice(0.8)
          else:
              action = self._random.random_choice(self.defection_probability)
              if action == axl.Action.D:
                  self.consecutive_defections += 1
              else:
                  self.consecutive_defections = 0
              return action

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to signal willingness to cooperate.  2. If the
# opponent played C in the previous round, play C to encourage mutual
# cooperation.  3. If the opponent played D in the previous round, play D as a
# punishment.  4. If you're currently on a streak of 3 or more mutual D plays,
# play C to attempt breaking the cycle of mutual defection.  5. If the opponent
# responds to your C with a C after a defection streak, continue playing C to
# establish cooperation.  6. If the opponent exploits your cooperation attempt
# by playing D, revert to D and repeat steps 3-5.  7. Every 10 rounds, analyze
# the opponent's pattern:    - If they've cooperated more than 70% of the time,
# continue with the current strategy.    - If they've defected more than 70% of
# the time, switch to always playing D for the next 10 rounds.  8. In the last
# 20 rounds, if the opponent has been mostly cooperative (>60% C), continue the
# current strategy. Otherwise, always play D.  9. Repeat steps 2-8 for the
# duration of the game, continuously adapting to the opponent's behavior.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_streak = 0
          self.always_defect_mode = False
          return axl.Action.C  # Start with cooperation
  
      # Check if we are in the last 20 rounds
      if len(self.history) >= 980:
          if opponent.history.cooperations / len(opponent.history) > 0.6:
              return axl.Action.C  # Continue cooperation if opponent has been mostly cooperative
          else:
              return axl.Action.D  # Defect if opponent has been mostly uncooperative
  
      # Every 10 rounds, analyze opponent's behavior
      if len(self.history) % 10 == 0:
          if opponent.history.cooperations / len(opponent.history) < 0.3:
              self.always_defect_mode = True  # Switch to always defect mode
          else:
              self.always_defect_mode = False  # Continue with the current strategy
  
      # If in always defect mode, play D
      if self.always_defect_mode:
          return axl.Action.D
  
      # Check the last round
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
          if self.defection_streak >= 3:
              return axl.Action.C  # Break the cycle of mutual defection after 3 rounds
          return axl.Action.D  # Punish defection
      else:
          self.defection_streak = 0  # Reset defection streak if opponent cooperates
          return axl.Action.C  # Cooperate if opponent cooperated

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round:    - Play C in the current round.  3. If the opponent played D in the
# previous round:    - Play D in the current round.    - Then return to playing
# C in the next round.  4. Keep track of the opponent's cooperation rate over
# the last 20 rounds:    - If this rate falls below 30%, play D for the next 5
# rounds, then reassess.    - If the rate rises above 70%, always play C for the
# next 5 rounds, then reassess.  5. If your score falls behind the opponent's
# score by 10 points or more:    - Play D until you've closed the gap to within
# 5 points, then resume the normal strategy.  6. Every 50 rounds, play C
# regardless of the opponent's recent actions to test for a potential strategy
# shift.  7. In the last 20 rounds of the game:    - If the opponent's
# cooperation rate in the last 50 rounds is above 70%, continue with the normal
# strategy.    - Otherwise, always play D.  8. If at any point the opponent has
# defected for 10 consecutive rounds:    - Switch to always playing D for the
# next 20 rounds, then return to the normal strategy.  Follow these rules in the
# order presented, moving to the next applicable rule if the conditions of the
# previous rules are not met.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.d_mode = 0
          self.c_mode = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, n):
          if len(history) < n:
              n = len(history)
          return history[-n:].count(axl.Action.C) / n if n > 0 else 0
  
      # Rule 8: If opponent defected for 10 consecutive rounds, play D for 20 rounds
      if opponent.history[-10:] == [axl.Action.D] * 10:
          self.consecutive_defections = 20
  
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.D
  
      # Rule 7: In the last 20 rounds of the game
      if len(self.history) >= 980:
          if cooperation_rate(opponent.history, 50) < 0.7:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rule 6: Every 50 rounds, play C to test for strategy shift
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 5: If behind by 10 points or more, play D until gap is within 5 points
      if self.score < opponent.score - 10:
          if self.score >= opponent.score - 5:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 4: Track cooperation rate over the last 20 rounds
      coop_rate = cooperation_rate(opponent.history, 20)
      if coop_rate < 0.3:
          self.d_mode = 5
      elif coop_rate > 0.7:
          self.c_mode = 5
  
      if self.d_mode > 0:
          self.d_mode -= 1
          return axl.Action.D
      if self.c_mode > 0:
          self.c_mode -= 1
          return axl.Action.C
  
      # Rule 3: If opponent played D last round, play D, then return to C
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 2: If opponent played C last round, play C
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect with a 90% probability and cooperate with a 10%
# probability.  4. Keep track of the opponent's behavior over the last 10
# rounds. If they have defected more than 7 times in these 10 rounds, defect for
# the next 3 rounds.  5. Every 30-70 rounds (randomly chosen), cooperate
# regardless of the opponent's previous action to test for a change in their
# strategy.  6. In the last 50 rounds, gradually increase the probability of
# defection. Start with a 20% chance of defection, increasing by 2% each round.
# 7. Calculate the cumulative score difference every 20 rounds. If you're behind
# by more than 30 points, increase your defection probability by 10% for the
# next 20 rounds.  8. If there have been 5 consecutive rounds of mutual
# defection, attempt to break the cycle by cooperating for 2 rounds.  9. Analyze
# the opponent's behavior every 100 rounds. If a clear pattern emerges, adjust
# your strategy to exploit it.  10. Return to step 2 and repeat until the game
# ends, continuously updating your approach based on the game's progression.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0
          self.test_round = self._random.randint(30, 70)
          self.defect_forced_rounds = 0
          self.consecutive_mutual_defections = 0
          self.extra_defection_probability = 0
          return axl.Action.C
  
      # Step 2: Cooperate if opponent cooperated in the previous round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If opponent defected in the previous round, defect with 90% probability
      if opponent.history[-1] == axl.Action.D:
          if self._random.random_choice(0.9):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Step 4: Track opponent's defections in the last 10 rounds
      if len(opponent.history) >= 10 and opponent.history[-10:].count(axl.Action.D) > 7:
          self.defect_forced_rounds = 3
  
      if self.defect_forced_rounds > 0:
          self.defect_forced_rounds -= 1
          return axl.Action.D
  
      # Step 5: Every 30-70 rounds, cooperate to test for strategy change
      if len(self.history) == self.test_round:
          self.test_round += self._random.randint(30, 70)
          return axl.Action.C
  
      # Step 6: In the last 50 rounds, increase defection probability
      if len(self.history) >= 950:
          defection_probability = 0.2 + 0.02 * (len(self.history) - 950)
          if self._random.random_choice(defection_probability):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Step 7: Every 20 rounds, check score difference and adjust defection probability
      if len(self.history) % 20 == 0:
          my_score, opponent_score = self.total_scores(self.history[-20:], opponent.history[-20:])
          if opponent_score - my_score > 30:
              self.extra_defection_probability = 0.1
          else:
              self.extra_defection_probability = 0
  
      # Step 8: Break mutual defection cycle
      if len(self.history) >= 5 and self.history[-5:] == [axl.Action.D] * 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          self.consecutive_mutual_defections = 2
  
      if self.consecutive_mutual_defections > 0:
          self.consecutive_mutual_defections -= 1
          return axl.Action.C
  
      # Step 9: Analyze opponent's behavior every 100 rounds (placeholder for future pattern analysis)
      if len(self.history) % 100 == 0:
          pass  # Placeholder for pattern analysis logic
  
      # Step 10: Return to step 2 (already handled by the structure of the code)
  
      # Default action: defect with extra defection probability if applicable
      if self._random.random_choice(0.1 + self.extra_defection_probability):
          return axl.Action.D
      else:
          return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent defected in the
# previous round, defect in the current round with an 80% probability and
# cooperate with a 20% probability.  3. If the opponent cooperated in the
# previous round, cooperate with a 70% probability and defect with a 30%
# probability.  4. Every 100 rounds, assess the opponent's overall cooperation
# rate. If it's below 30%, defect for the next 5 rounds. If it's above 70%,
# cooperate for the next 5 rounds.  5. If your total score is lower than the
# opponent's score by 50 points or more, increase your defection probability by
# 20% for the next 20 rounds.  6. In the last 100 rounds, if the opponent's
# cooperation rate in the previous 50 rounds was above 50%, maintain the
# standard strategy. Otherwise, increase your defection probability by 10%.  7.
# If there have been 5 consecutive rounds of mutual defection, attempt to break
# the cycle by cooperating in the next round.  8. In all other situations,
# follow steps 2 and 3.  9. Continuously track the opponent's pattern of play
# and adjust probabilities slightly (±5%) based on which actions have been most
# profitable against this specific opponent.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.adjustment_rounds = 0
          self.adjustment_type = None
          self.defection_boost = 0
          return axl.Action.C
  
      # Helper function to calculate opponent's cooperation rate
      def opponent_cooperation_rate():
          return opponent.history.cooperations / len(opponent.history)
  
      # Helper function to adjust probabilities based on opponent's pattern
      def adjust_probabilities():
          if len(opponent.history) > 50:
              recent_cooperations = opponent.history[-50:].count(axl.Action.C)
              if recent_cooperations / 50 > 0.5:
                  return 0  # No adjustment
              else:
                  return 0.1  # Increase defection probability by 10%
          return 0
  
      # Step 7: Check for 5 consecutive mutual defections
      if len(self.history) >= 5 and all(
          self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
          for i in range(1, 6)
      ):
          return axl.Action.C  # Break the cycle by cooperating
  
      # Step 4: Every 100 rounds, assess opponent's cooperation rate
      if len(self.history) % 100 == 0:
          coop_rate = opponent_cooperation_rate()
          if coop_rate < 0.3:
              self.adjustment_rounds = 5
              self.adjustment_type = "defect"
          elif coop_rate > 0.7:
              self.adjustment_rounds = 5
              self.adjustment_type = "cooperate"
  
      # Step 5: If behind by 50 points or more, increase defection probability
      if self.score < opponent.score - 50:
          self.defection_boost = 0.2
          self.adjustment_rounds = 20
          self.adjustment_type = "defect"
  
      # Apply adjustments if in an adjustment period
      if self.adjustment_rounds > 0:
          self.adjustment_rounds -= 1
          if self.adjustment_type == "defect":
              return axl.Action.D
          elif self.adjustment_type == "cooperate":
              return axl.Action.C
  
      # Step 6: In the last 100 rounds, adjust based on opponent's recent cooperation
      if len(self.history) >= 900:
          self.defection_boost += adjust_probabilities()
  
      # Step 2 and 3: Main strategy based on opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.2 + self.defection_boost)  # 80% defect, 20% cooperate
      else:
          return self._random.random_choice(0.7 - self.defection_boost)  # 70% cooperate, 30% defect

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After the two-round punishment, return
# to playing C.  5. Keep track of the opponent's cooperation rate. If their
# cooperation rate falls below 30% over the last 20 rounds, switch to always
# playing D until their cooperation rate improves above 50%.  6. If the opponent
# seems to be following a similar cooperative strategy (alternating between C
# and D based on your moves or maintaining a high cooperation rate), maintain
# the cooperative approach.  7. If you've been in "always D" mode for more than
# 50 rounds, attempt to restore cooperation by playing C for 3 consecutive
# rounds. If the opponent cooperates at least twice in response, return to the
# main strategy.  8. To account for possible noise or mistakes, allow for a
# "forgiveness" mechanism: every 100 rounds, play C regardless of the opponent's
# last move.  9. In the last 10 rounds of the game, play according to the
# opponent's cooperation rate in the previous 20 rounds. If it's above 70%,
# continue cooperating. If it's below 70%, play D.  10. Throughout the game, if
# the opponent's overall cooperation rate is above 80%, always respond with C to
# maximize mutual benefit.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_counter = 0
          self.always_d_mode = False
          self.always_d_counter = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, n):
          if len(history) < n:
              n = len(history)
          return history[-n:].count(axl.Action.C) / n if n > 0 else 0
  
      # Step 10: If opponent's overall cooperation rate is above 80%, always cooperate
      if cooperation_rate(opponent.history, len(opponent.history)) > 0.8:
          return axl.Action.C
  
      # Step 9: In the last 10 rounds, adjust based on opponent's cooperation rate
      if len(self.history) >= 990:
          if cooperation_rate(opponent.history, 20) > 0.7:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 8: Every 100 rounds, play C regardless of the opponent's last move
      if len(self.history) % 100 == 0:
          return axl.Action.C
  
      # Step 7: If in "always D" mode for more than 50 rounds, attempt to restore cooperation
      if self.always_d_mode:
          self.always_d_counter += 1
          if self.always_d_counter > 50:
              if self.always_d_counter <= 53:
                  return axl.Action.C  # Play C for 3 consecutive rounds
              elif opponent.history[-3:].count(axl.Action.C) >= 2:
                  self.always_d_mode = False  # Restore cooperation
                  self.always_d_counter = 0
                  return axl.Action.C
              else:
                  return axl.Action.D
          return axl.Action.D
  
      # Step 3: Punish with D for two rounds if opponent played D last round
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.D:
          self.punishment_counter = 2
          return axl.Action.D
  
      # Step 5: Switch to always D if opponent's cooperation rate falls below 30% over the last 20 rounds
      if cooperation_rate(opponent.history, 20) < 0.3:
          self.always_d_mode = True
          self.always_d_counter = 0
          return axl.Action.D
  
      # Step 2: If opponent played C last round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. Every 10 rounds, regardless
# of the opponent's previous move:    - If your total score is higher than your
# opponent's, cooperate.    - If your total score is lower than your opponent's,
# defect.    - If scores are tied, cooperate.  5. In the last 1% of the total
# rounds (or last 10 rounds, whichever is smaller), always defect.  6. Keep
# track of the opponent's defection rate over the last 30 rounds. If this rate
# exceeds 50%, switch to always defecting for the next 5 rounds before reverting
# to the main strategy.  7. If you and your opponent have been in a cycle of
# mutual defection for more than 10 consecutive rounds, attempt to break the
# cycle by cooperating for one round.  8. If at any point the game is announced
# to be in its final round, defect.  9. Maintain a running count of your score
# and your opponent's score, updating after each round.  10. If the opponent's
# strategy seems random (defection rate between 40% and 60% over the last 50
# rounds), switch to always defecting until their behavior becomes more
# predictable.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_streak = 0
          self.always_defect_counter = 0
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate defection rate over the last N rounds
      def defection_rate(history, N):
          return history[-N:].count(axl.Action.D) / min(N, len(history))
  
      # Helper function to check if we are in the last 1% or last 10 rounds
      def in_final_rounds():
          remaining_rounds = self.match_attributes["length"] - len(self.history)
          return remaining_rounds <= min(10, self.match_attributes["length"] // 100)
  
      # Check if we are in the final round
      if len(self.history) == self.match_attributes["length"] - 1:
          return axl.Action.D  # Defect in the final round
  
      # Check if we are in the last 1% or last 10 rounds
      if in_final_rounds():
          return axl.Action.D  # Always defect in the last 1% or last 10 rounds
  
      # Check if we are in a mutual defection cycle for more than 10 rounds
      if self.history[-10:] == [axl.Action.D] * 10 and opponent.history[-10:] == [axl.Action.D] * 10:
          return axl.Action.C  # Break the cycle by cooperating
  
      # Check if we are in the "always defect" mode due to opponent's high defection rate
      if self.always_defect_counter > 0:
          self.always_defect_counter -= 1
          return axl.Action.D  # Continue defecting for the next 5 rounds
  
      # Check opponent's defection rate over the last 30 rounds
      if len(opponent.history) >= 30 and defection_rate(opponent.history, 30) > 0.5:
          self.always_defect_counter = 5  # Switch to always defecting for the next 5 rounds
          return axl.Action.D
  
      # Check if opponent's strategy seems random (defection rate between 40% and 60% over the last 50 rounds)
      if len(opponent.history) >= 50 and 0.4 <= defection_rate(opponent.history, 50) <= 0.6:
          return axl.Action.D  # Switch to always defecting
  
      # Every 10 rounds, compare scores and decide
      if len(self.history) % 10 == 0:
          if self.score > opponent.score:
              return axl.Action.C  # Cooperate if our score is higher
          elif self.score < opponent.score:
              return axl.Action.D  # Defect if our score is lower
          else:
              return axl.Action.C  # Cooperate if scores are tied
  
      # Main strategy: Tit-for-Tat
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Defect if opponent defected last round
      else:
          return axl.Action.C  # Cooperate if opponent cooperated last round

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to encourage cooperation.  2. If the opponent
# played C in the previous round, play C with 80% probability and D with 20%
# probability in the current round.  3. If the opponent played D in the previous
# round, play D in the current round.  4. If you're currently on a streak of
# mutual cooperation (CC) for 10 or more consecutive rounds, play D in the next
# round to occasionally test the opponent's response.  5. Keep track of the
# opponent's cooperation rate. If it falls below 30% over the last 50 rounds,
# switch to always playing D for the next 20 rounds before reassessing.  6. In
# rounds 900-990, play according to the opponent's most frequent action in the
# previous 100 rounds.  7. In the last 10 rounds of the game, always play D.  8.
# Every 100 rounds, reassess the opponent's overall strategy. If they seem to be
# using a recognizable pattern, adjust your play to exploit it.  9. If the
# opponent's actions appear random, default to playing C with 60% probability
# and D with 40% probability.  10. For all other situations not covered by the
# above rules, play C to maintain a balance between cooperation and aggression.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.mutual_coop_streak = 0
          self.defect_mode = False
          self.defect_mode_counter = 0
          return axl.Action.C
  
      # Rule 7: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 6: In rounds 900-990, play according to the opponent's most frequent action in the last 100 rounds
      if 900 <= len(self.history) < 990:
          last_100 = opponent.history[-100:]
          if last_100.count(axl.Action.C) > last_100.count(axl.Action.D):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 5: If opponent's cooperation rate falls below 30% in the last 50 rounds, switch to D for 20 rounds
      if len(self.history) >= 50:
          coop_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if coop_rate < 0.3:
              self.defect_mode = True
              self.defect_mode_counter = 20
  
      if self.defect_mode:
          self.defect_mode_counter -= 1
          if self.defect_mode_counter <= 0:
              self.defect_mode = False
          return axl.Action.D
  
      # Rule 4: If mutual cooperation streak is 10 or more, play D to test opponent
      if self.mutual_coop_streak >= 10:
          self.mutual_coop_streak = 0  # Reset streak after testing
          return axl.Action.D
  
      # Rule 2: If opponent played C last round, play C with 80% probability, D with 20%
      if opponent.history[-1] == axl.Action.C:
          if self._random.random_choice(0.8):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 3: If opponent played D last round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 1: Start by playing C in the first round (already handled by first_round check)
  
      # Rule 9: If opponent's actions appear random, play C with 60% probability, D with 40%
      if len(self.history) >= 100:
          last_100 = opponent.history[-100:]
          coop_count = last_100.count(axl.Action.C)
          defect_count = last_100.count(axl.Action.D)
          if abs(coop_count - defect_count) < 10:  # Random if close to equal
              if self._random.random_choice(0.6):
                  return axl.Action.C
              else:
                  return axl.Action.D
  
      # Rule 8: Every 100 rounds, reassess opponent's strategy (not implemented in detail, placeholder)
      # This rule is complex and would require pattern recognition, which is not trivial to implement here.
      # For now, we will skip this rule.
  
      # Rule 10: Default to playing C in all other situations
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After punishing with D twice, return to
# playing C in the following round.  5. Keep track of the opponent's cooperation
# rate. If it falls below 40% in the last 20 rounds, switch to always playing D
# until their cooperation rate rises above 60% in the last 20 rounds.  6. In the
# last 10 rounds of the game, mirror the opponent's previous move (Tit-for-Tat).
# 7. If at any point the opponent's score is more than 30 points higher than
# yours, play D until you've closed the gap to within 15 points, then resume the
# normal strategy.  8. Every 50 rounds, if there has been mutual defection for
# more than 20 consecutive rounds, play C for 3 rounds to attempt to re-
# establish cooperation.  9. Adjust the punishment duration as the game
# progresses: for the first 333 rounds, punish for 2 rounds; for the next 333
# rounds, punish for 3 rounds; for the final 334 rounds, punish for 4 rounds.
# 10. If the opponent has defected more than 80% of the time in the last 100
# rounds, switch to always defecting for the remainder of the game.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_duration = 2
          self.punishment_counter = 0
          self.mutual_defection_counter = 0
          self.cooperation_attempt_counter = 0
          return axl.Action.C
  
      # Update punishment duration based on the round number
      round_number = len(self.history)
      if round_number <= 333:
          self.punishment_duration = 2
      elif round_number <= 666:
          self.punishment_duration = 3
      else:
          self.punishment_duration = 4
  
      # Track mutual defections
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.mutual_defection_counter += 1
      else:
          self.mutual_defection_counter = 0
  
      # Every 50 rounds, if mutual defection has occurred for more than 20 consecutive rounds, play C for 3 rounds
      if round_number % 50 == 0 and self.mutual_defection_counter > 20:
          if self.cooperation_attempt_counter < 3:
              self.cooperation_attempt_counter += 1
              return axl.Action.C
          else:
              self.cooperation_attempt_counter = 0
  
      # If the opponent's score is more than 30 points higher, play D until the gap is within 15 points
      if opponent.score - self.score > 30:
          if opponent.score - self.score > 15:
              return axl.Action.D
  
      # In the last 10 rounds, mirror the opponent's previous move (Tit-for-Tat)
      if round_number >= 990:
          return opponent.history[-1]
  
      # Track opponent's cooperation rate in the last 20 rounds
      if round_number >= 20:
          last_20_cooperations = opponent.history[-20:].count(axl.Action.C)
          cooperation_rate = last_20_cooperations / 20
          if cooperation_rate < 0.4:
              return axl.Action.D
          elif cooperation_rate > 0.6:
              return axl.Action.C
  
      # If the opponent has defected more than 80% of the time in the last 100 rounds, always defect
      if round_number >= 100:
          last_100_defections = opponent.history[-100:].count(axl.Action.D)
          if last_100_defections / 100 > 0.8:
              return axl.Action.D
  
      # Handle punishment logic
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # If the opponent played D in the last round, punish for the next punishment_duration rounds
      if opponent.history[-1] == axl.Action.D:
          self.punishment_counter = self.punishment_duration - 1
          return axl.Action.D
  
      # Otherwise, cooperate if the opponent cooperated in the last round
      return axl.Action.C

# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect with a 70% probability, otherwise cooperate.  4. After the first
# 5 rounds, if the opponent has defected more than 50% of the time in the last 5
# rounds, defect for the next 2 rounds, then return to the base strategy.  5. If
# your current score is more than 15 points behind your opponent's, implement a
# tit-for-two-tats strategy for the next 5 rounds (defect only after the
# opponent defects twice in a row), then return to the base strategy.  6. Every
# 20 rounds, regardless of the opponent's recent actions, cooperate to test if
# the opponent is willing to re-establish cooperation.  7. In the last 5% of the
# game (50 rounds for a 1000-round game), gradually increase the probability of
# defection. Start at 20% and increase by 2% each round.  8. If your overall
# score is higher than your opponent's, become slightly more cooperative by
# reducing the probability of defection in rule 3 to 60%.  9. If none of the
# above conditions are met, cooperate.  Apply these rules in order, using the
# first one that matches the current situation. Reassess the strategy every 100
# rounds based on overall performance, adjusting the thresholds and
# probabilities slightly if necessary.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.tit_for_two_tats_counter = 0
          self.defect_for_two_rounds = 0
          self.cooperate_test_round = 20
  
      # Rule 1: Cooperate in the first round
      if len(self.history) == 0:
          return axl.Action.C
  
      # Rule 5: Implement tit-for-two-tats if more than 15 points behind
      if self.tit_for_two_tats_counter > 0:
          self.tit_for_two_tats_counter -= 1
          if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          return axl.Action.C
  
      # Rule 4: Defect for 2 rounds if opponent defected more than 50% in the last 5 rounds
      if self.defect_for_two_rounds > 0:
          self.defect_for_two_rounds -= 1
          return axl.Action.D
  
      if len(self.history) >= 5:
          last_5_defections = opponent.history[-5:].count(axl.Action.D)
          if last_5_defections > 2:
              self.defect_for_two_rounds = 2
              return axl.Action.D
  
      # Rule 6: Every 20 rounds, cooperate to test for re-establishing cooperation
      if len(self.history) == self.cooperate_test_round:
          self.cooperate_test_round += 20
          return axl.Action.C
  
      # Rule 7: In the last 5% of the game, gradually increase defection probability
      total_rounds = 1000
      if len(self.history) >= 0.95 * total_rounds:
          rounds_left = total_rounds - len(self.history)
          defect_prob = 0.2 + (0.02 * (total_rounds - rounds_left))
          if self._random.random_choice(defect_prob):
              return axl.Action.D
          return axl.Action.C
  
      # Rule 3: Defect with 70% probability if opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          defect_prob = 0.7
          # Rule 8: If your score is higher, reduce defection probability to 60%
          if self.score > opponent.score:
              defect_prob = 0.6
          if self._random.random_choice(defect_prob):
              return axl.Action.D
          return axl.Action.C
  
      # Rule 2: Cooperate if opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 5: Check if more than 15 points behind and implement tit-for-two-tats
      if self.score < opponent.score - 15:
          self.tit_for_two_tats_counter = 5
          return axl.Action.C
  
      # Default: Cooperate
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round to encourage cooperation.  2. If the
# opponent cooperated in the previous round, cooperate with an 80% probability
# and defect with a 20% probability.  3. If the opponent defected in the
# previous round, defect with a 70% probability and cooperate with a 30%
# probability.  4. If the opponent has cooperated for three consecutive rounds,
# cooperate in the next round.  5. If the opponent has defected for three
# consecutive rounds, defect in the next round.  6. Every 10 rounds, analyze the
# opponent's overall pattern:    - If they've cooperated more than 70% of the
# time, cooperate in the next round.    - If they've defected more than 70% of
# the time, defect in the next round.  7. In the last 20 rounds, mirror the
# opponent's previous move (Tit-for-Tat).  8. If the opponent's actions seem
# random or don't fit any clear pattern, default to Tit-for-Tat (copy their
# previous move).  9. For all other situations not covered by the above rules,
# cooperate.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if the opponent has cooperated or defected for the last N rounds
      def last_n_moves(opponent, n, action):
          return all(move == action for move in opponent.history[-n:])
      
      # Rule 1: First round, cooperate
      if self.first_round():
          return axl.Action.C
      
      # Rule 7: In the last 20 rounds, mirror the opponent's previous move (Tit-for-Tat)
      if len(self.history) >= 980:
          return opponent.history[-1]
      
      # Rule 4: If the opponent has cooperated for three consecutive rounds, cooperate
      if last_n_moves(opponent, 3, axl.Action.C):
          return axl.Action.C
      
      # Rule 5: If the opponent has defected for three consecutive rounds, defect
      if last_n_moves(opponent, 3, axl.Action.D):
          return axl.Action.D
      
      # Rule 6: Every 10 rounds, analyze the opponent's overall pattern
      if len(self.history) % 10 == 0:
          total_moves = len(opponent.history)
          if total_moves > 0:
              cooperation_rate = opponent.history.cooperations / total_moves
              if cooperation_rate > 0.7:
                  return axl.Action.C
              elif cooperation_rate < 0.3:
                  return axl.Action.D
      
      # Rule 2: If the opponent cooperated in the previous round, cooperate with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.8)
      
      # Rule 3: If the opponent defected in the previous round, defect with 70% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.3)
      
      # Rule 8: If the opponent's actions seem random, default to Tit-for-Tat
      # (This is handled implicitly by the above rules, as we mirror the last move in uncertain cases)
      
      # Rule 9: For all other situations, cooperate
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as a warning.  4. After playing D as a warning, return to
# playing C in the following round.  5. Keep track of the opponent's defection
# rate over the last 100 rounds. If this rate exceeds 40%, switch to a tit-for-
# tat strategy (mirroring the opponent's previous move) for the next 50 rounds.
# 6. If the opponent's defection rate drops below 30% during the tit-for-tat
# phase, return to the cooperative strategy (steps 1-4).  7. If the opponent
# defects three times in a row, play D for the next three rounds, then return to
# step 2.  8. In the last 10 rounds of the game, play tit-for-tat regardless of
# the opponent's overall defection rate.  9. Every 100 rounds, play C regardless
# of the opponent's previous move as a "olive branch" to potentially re-
# establish cooperation.  10. If at any point the opponent has defected more
# than 70% of the time in the last 200 rounds, switch to always playing D for
# the remainder of the game.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.warning_flag = False
          self.tit_for_tat_flag = False
          self.tit_for_tat_counter = 0
          self.defection_streak = 0
          self.always_defect_flag = False
          return axl.Action.C
  
      # Helper function to calculate defection rate over the last N rounds
      def defection_rate(history, N):
          return history[-N:].count(axl.Action.D) / min(N, len(history))
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return opponent.history[-1]  # Play tit-for-tat in the last 10 rounds
  
      # Check if the opponent has defected more than 70% in the last 200 rounds
      if len(self.history) >= 200 and defection_rate(opponent.history, 200) > 0.7:
          self.always_defect_flag = True
  
      # If always defect flag is set, play D for the rest of the game
      if self.always_defect_flag:
          return axl.Action.D
  
      # Every 100 rounds, play C as an olive branch
      if len(self.history) % 100 == 0:
          return axl.Action.C
  
      # If in tit-for-tat mode, continue for 50 rounds
      if self.tit_for_tat_flag:
          self.tit_for_tat_counter += 1
          if self.tit_for_tat_counter >= 50:
              self.tit_for_tat_flag = False  # Exit tit-for-tat mode after 50 rounds
          if defection_rate(opponent.history, 100) < 0.3:
              self.tit_for_tat_flag = False  # Exit tit-for-tat mode if defection rate drops below 30%
          return opponent.history[-1]  # Play tit-for-tat
  
      # Check if the opponent has defected three times in a row
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.defection_streak = 3
  
      # If in defection streak mode, play D for the next three rounds
      if self.defection_streak > 0:
          self.defection_streak -= 1
          return axl.Action.D
  
      # Check the opponent's defection rate over the last 100 rounds
      if len(self.history) >= 100 and defection_rate(opponent.history, 100) > 0.4:
          self.tit_for_tat_flag = True
          self.tit_for_tat_counter = 0
          return opponent.history[-1]  # Start tit-for-tat
  
      # If the opponent defected in the last round, play D as a warning
      if opponent.history[-1] == axl.Action.D:
          if self.warning_flag:
              self.warning_flag = False
              return axl.Action.C  # Return to cooperation after warning
          else:
              self.warning_flag = True
              return axl.Action.D  # Play D as a warning
  
      # If the opponent cooperated in the last round, play C
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect with a 70% probability and cooperate with a 30%
# probability.  4. If mutual defection has occurred for three consecutive
# rounds, attempt to break the cycle by cooperating in the next round.  5. Keep
# track of the cumulative score difference. If you're behind by 15 points or
# more, increase your defection probability to 80% for the next 5 rounds, then
# return to the base strategy.  6. Every 50 rounds, evaluate your performance.
# If your average score per round is below 2, adjust your strategy by increasing
# cooperation probability by 10% for the next 50 rounds.  7. If there are less
# than 100 rounds remaining, cooperate if the opponent has cooperated more than
# 50% of the time throughout the game. Adjust this threshold by 5% every 20
# rounds, making it stricter as the game nears its end.  8. In the last 20
# rounds, randomize your choices with a 60% probability of defection and 40%
# probability of cooperation.  9. For any situation not covered by the above
# rules, cooperate.  10. Throughout the game, maintain a rolling average of the
# opponent's cooperation rate over the last 50 moves. Use this to fine-tune your
# responses, slightly increasing your cooperation probability if they're more
# cooperative, and decreasing it if they're less cooperative.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.behind_by_15 = False
          self.behind_rounds = 0
          self.cooperation_adjustment = 0
          self.cooperation_rate = 0.3
          return axl.Action.C
  
      # Helper function to calculate rolling cooperation rate over the last 50 rounds
      def rolling_cooperation_rate():
          recent_history = opponent.history[-50:]
          if len(recent_history) == 0:
              return 0
          return recent_history.count(axl.Action.C) / len(recent_history)
  
      # Update cooperation rate based on rolling average
      self.cooperation_rate = rolling_cooperation_rate()
  
      # Rule 2: Cooperate if opponent cooperated in the previous round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent defected in the previous round, defect with 70% probability
      if opponent.history[-1] == axl.Action.D:
          if self._random.random_choice(0.7):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rule 4: If mutual defection has occurred for 3 consecutive rounds, cooperate
      if len(self.history) >= 3 and all(x == axl.Action.D for x in self.history[-3:]) and all(x == axl.Action.D for x in opponent.history[-3:]):
          return axl.Action.C
  
      # Rule 5: Track score difference and adjust defection probability if behind by 15 points
      score_diff = self.score - opponent.score
      if score_diff <= -15 and not self.behind_by_15:
          self.behind_by_15 = True
          self.behind_rounds = 5
      if self.behind_by_15:
          self.behind_rounds -= 1
          if self.behind_rounds <= 0:
              self.behind_by_15 = False
          if self._random.random_choice(0.8):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rule 6: Every 50 rounds, evaluate performance and adjust cooperation probability
      if len(self.history) % 50 == 0 and len(self.history) > 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.cooperation_adjustment += 0.1
  
      # Rule 7: If less than 100 rounds remaining, cooperate if opponent has cooperated more than 50% of the time
      rounds_remaining = 1000 - len(self.history)
      if rounds_remaining < 100:
          threshold = 0.5 + (100 - rounds_remaining) // 20 * 0.05
          if opponent.history.cooperations / len(opponent.history) > threshold:
              return axl.Action.C
  
      # Rule 8: In the last 20 rounds, randomize with 60% defection probability
      if rounds_remaining <= 20:
          if self._random.random_choice(0.6):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Default to cooperation if no other rule applies
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. If the opponent defected in the
# previous round, defect with 90% probability and cooperate with 10%
# probability.  3. If the opponent cooperated in the previous round, cooperate
# with 70% probability and defect with 30% probability.  4. Every 30-70 rounds
# (randomly chosen), play the opposite of your last move, regardless of the
# opponent's previous move.  5. In the last 50 rounds, gradually increase the
# probability of defection. Start with a 50% chance of defection, increasing by
# 1% each round.  6. If your score is more than 30 points behind your
# opponent's, increase your defection probability by 20% for the next 10 rounds.
# 7. If you're ahead by more than 50 points, decrease your defection probability
# by 20% for the next 10 rounds.  8. Keep track of the opponent's cooperation
# rate over the last 20 moves. If it's above 80%, increase your cooperation
# probability by 10% for the next 5 rounds.  9. Every 100 rounds, reassess your
# overall strategy:    - If your score is higher, maintain the current approach.
# - If your score is lower, slightly increase your overall defection
# probability.  10. In the first 200 rounds, be slightly more cooperative to
# establish potential long-term cooperation.  11. Return to step 2 and repeat
# until the game ends.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.last_opposite_round = 0
          self.opposite_round_interval = self._random.randint(30, 70)
          self.defection_boost = 0
          self.cooperation_boost = 0
          self.last_defection_boost_round = -10
          self.last_cooperation_boost_round = -5
          self.last_strategy_reassessment = 0
          return axl.Action.C
  
      # Get the current round number
      current_round = len(self.history)
  
      # Step 4: Every 30-70 rounds, play the opposite of the last move
      if current_round - self.last_opposite_round >= self.opposite_round_interval:
          self.last_opposite_round = current_round
          self.opposite_round_interval = self._random.randint(30, 70)
          return axl.Action.D if self.history[-1] == axl.Action.C else axl.Action.C
  
      # Step 5: In the last 50 rounds, gradually increase defection probability
      if current_round > 950:
          defection_probability = 0.5 + (current_round - 950) * 0.01
      else:
          # Step 2 and 3: Adjust probabilities based on opponent's last move
          if opponent.history[-1] == axl.Action.D:
              defection_probability = 0.9
          else:
              defection_probability = 0.3
  
          # Step 6: If behind by more than 30 points, increase defection probability
          if self.score < opponent.score - 30 and current_round - self.last_defection_boost_round > 10:
              defection_probability += 0.2
              self.last_defection_boost_round = current_round
  
          # Step 7: If ahead by more than 50 points, decrease defection probability
          if self.score > opponent.score + 50 and current_round - self.last_defection_boost_round > 10:
              defection_probability -= 0.2
              self.last_defection_boost_round = current_round
  
          # Step 8: Track opponent's cooperation rate over the last 20 moves
          if current_round >= 20:
              recent_cooperations = opponent.history[-20:].count(axl.Action.C)
              if recent_cooperations / 20 > 0.8 and current_round - self.last_cooperation_boost_round > 5:
                  defection_probability -= 0.1
                  self.last_cooperation_boost_round = current_round
  
      # Step 9: Every 100 rounds, reassess strategy
      if current_round - self.last_strategy_reassessment >= 100:
          self.last_strategy_reassessment = current_round
          if self.score < opponent.score:
              defection_probability += 0.05
  
      # Step 10: In the first 200 rounds, be slightly more cooperative
      if current_round <= 200:
          defection_probability -= 0.05
  
      # Make the decision based on the calculated defection probability
      return self._random.random_choice(1 - defection_probability)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D, return to playing C
# in the following round to attempt re-establishing cooperation.  5. If the
# opponent plays D for two consecutive rounds, switch to a tit-for-tat strategy
# (mirroring the opponent's previous move) for the next 10 rounds.  6. After 10
# rounds of tit-for-tat, attempt to restore cooperation by playing C for two
# consecutive rounds, regardless of the opponent's actions.  7. If the
# opponent's score is more than 15 points higher than yours, play D for the next
# round, then return to the base strategy.  8. In the last 20 rounds of the
# game, play tit-for-tat regardless of previous actions.  9. If you're behind in
# score with less than 50 rounds remaining, play tit-for-tat until the score
# difference is less than 5 points or the game ends.  10. Throughout the game,
# if you and your opponent have played C mutually for 10 consecutive rounds,
# play C for the next round regardless of other conditions (except for the last
# 20 rounds rule).

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.tit_for_tat_mode = False
          self.tit_for_tat_counter = 0
          self.cooperation_attempts = 0
          return axl.Action.C
  
      # Helper function to check if we're in the last 20 rounds
      def in_last_20_rounds():
          return len(self.history) >= 980
  
      # Helper function to check if we're behind in score with less than 50 rounds remaining
      def behind_in_last_50_rounds():
          return len(self.history) >= 950 and self.score < opponent.score
  
      # Helper function to check if the opponent has defected for two consecutive rounds
      def opponent_defected_two_consecutive():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if mutual cooperation has occurred for 10 consecutive rounds
      def mutual_cooperation_10_rounds():
          return len(self.history) >= 10 and all(
              self.history[-i] == axl.Action.C and opponent.history[-i] == axl.Action.C for i in range(1, 11)
          )
  
      # If in the last 20 rounds, play tit-for-tat
      if in_last_20_rounds():
          return opponent.history[-1]
  
      # If behind in score with less than 50 rounds remaining, play tit-for-tat until the score difference is less than 5
      if behind_in_last_50_rounds():
          if opponent.score - self.score >= 5:
              return opponent.history[-1]
  
      # If mutual cooperation for 10 consecutive rounds, play C
      if mutual_cooperation_10_rounds():
          return axl.Action.C
  
      # If the opponent's score is more than 15 points higher, play D for the next round
      if opponent.score - self.score > 15:
          return axl.Action.D
  
      # If in tit-for-tat mode, continue for 10 rounds
      if self.tit_for_tat_mode:
          self.tit_for_tat_counter += 1
          if self.tit_for_tat_counter >= 10:
              self.tit_for_tat_mode = False
              self.cooperation_attempts = 0
              return axl.Action.C  # After 10 rounds of tit-for-tat, attempt to restore cooperation
          return opponent.history[-1]
  
      # Base strategy: Punish with D after opponent defects, then return to C
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D:
              return axl.Action.C  # After punishing, return to C
          if opponent_defected_two_consecutive():
              self.tit_for_tat_mode = True
              self.tit_for_tat_counter = 0
              return opponent.history[-1]  # Start tit-for-tat mode
          return axl.Action.D  # Punish with D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a revised strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. Keep track of the opponent's
# cooperation rate. If their cooperation rate falls below 40%, defect for the
# next 2 rounds.  5. If you're behind in total score by more than 10 points,
# defect for the next round.  6. If you're ahead in total score by more than 20
# points, cooperate for the next round.  7. In the last 50 rounds of the game,
# if your score is lower than or equal to the opponent's, always defect.  8. In
# the last 50 rounds of the game, if your score is higher than the opponent's,
# cooperate only if the opponent cooperated in the previous round.  9. If none
# of the above conditions are met, cooperate.  Apply these rules in order, using
# the first one that matches the current game state.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to calculate cooperation rate
      def cooperation_rate(player):
          total_moves = len(player.history)
          if total_moves == 0:
              return 1  # Assume full cooperation if no moves yet
          return player.history.cooperations / total_moves
  
      # 1. Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # 2. If the opponent cooperated in the previous round, cooperate in the current round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. If the opponent defected in the previous round, defect in the current round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 4. Keep track of the opponent's cooperation rate. If their cooperation rate falls below 40%, defect for the next 2 rounds.
      if cooperation_rate(opponent) < 0.4:
          if len(self.history) < 2 or self.history[-1] != axl.Action.D or self.history[-2] != axl.Action.D:
              return axl.Action.D
  
      # 5. If you're behind in total score by more than 10 points, defect for the next round.
      if self.score < opponent.score - 10:
          return axl.Action.D
  
      # 6. If you're ahead in total score by more than 20 points, cooperate for the next round.
      if self.score > opponent.score + 20:
          return axl.Action.C
  
      # 7. In the last 50 rounds of the game, if your score is lower than or equal to the opponent's, always defect.
      if len(self.history) >= 950:
          if self.score <= opponent.score:
              return axl.Action.D
  
      # 8. In the last 50 rounds of the game, if your score is higher than the opponent's, cooperate only if the opponent cooperated in the previous round.
      if len(self.history) >= 950:
          if self.score > opponent.score and opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # 9. If none of the above conditions are met, cooperate.
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round to encourage cooperation.  2. If the opponent
# played C in the previous round, play C with 80% probability and D with 20%
# probability.  3. If the opponent played D in the previous round, play D.  4.
# Keep track of the opponent's cooperation rate. If it falls below 30% over the
# last 50 moves, switch to always playing D for the next 20 moves.  5. If you're
# in a streak of 5 or more mutual D plays, play C once to test if the opponent
# will cooperate.  6. If the opponent responds to your test C with a C, play C
# in the next round to encourage continued cooperation.  7. In rounds 900-990,
# base your decision on the opponent's overall cooperation rate:    - If it's
# above 70%, always play C.    - If it's between 30% and 70%, use the strategy
# from steps 2-3.    - If it's below 30%, always play D.  8. In the last 10
# rounds (991-1000), always play D to maximize final payoff.  9. Every 100
# rounds, reassess the opponent's pattern and adjust your cooperation
# probability in step 2 accordingly.  10. Repeat steps 2-9 for the duration of
# the game.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_streak = 0
          self.defection_streak = 0
          self.always_defect_mode = False
          self.always_defect_counter = 0
          self.cooperation_probability = 0.8
          return axl.Action.C
  
      # Helper function to calculate opponent's cooperation rate over the last N moves
      def cooperation_rate(last_n):
          return opponent.history[-last_n:].count(axl.Action.C) / last_n
  
      # Step 4: Check if opponent's cooperation rate over the last 50 moves is below 30%
      if len(opponent.history) >= 50 and cooperation_rate(50) < 0.3:
          self.always_defect_mode = True
          self.always_defect_counter = 20
  
      # Step 5: Check for a streak of 5 or more mutual defections
      if len(self.history) >= 5 and all(
          self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
          for i in range(1, 6)
      ):
          return axl.Action.C  # Test cooperation by playing C
  
      # Step 6: If opponent responded to the test C with a C, play C again
      if len(self.history) >= 2 and self.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 7: Special strategy for rounds 900-990
      if 900 <= len(self.history) <= 990:
          overall_cooperation_rate = cooperation_rate(len(opponent.history))
          if overall_cooperation_rate > 0.7:
              return axl.Action.C
          elif overall_cooperation_rate < 0.3:
              return axl.Action.D
  
      # Step 8: Always play D in the last 10 rounds (991-1000)
      if len(self.history) >= 991:
          return axl.Action.D
  
      # Step 9: Reassess cooperation probability every 100 rounds
      if len(self.history) % 100 == 0:
          self.cooperation_probability = 0.8  # Adjust this based on opponent's pattern if needed
  
      # Step 2-3: Main strategy logic
      if self.always_defect_mode:
          self.always_defect_counter -= 1
          if self.always_defect_counter == 0:
              self.always_defect_mode = False
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(self.cooperation_probability)
      else:
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next two rounds as punishment.  4. After the two-round punishment, return
# to playing C.  5. Keep track of the opponent's cooperation ratio (number of C
# plays divided by total rounds played).  6. If the opponent's cooperation ratio
# falls below 0.3, switch to always playing D until their ratio improves above
# 0.5.  7. If both players have been mutually defecting for more than 10 rounds,
# attempt to restart cooperation by playing C for one round.  8. To account for
# possible noise or mistakes, allow for a single "forgiveness" round: if the
# opponent has been consistently cooperative but suddenly defects once, continue
# playing C.  9. In the last 20 rounds, play a modified Tit-for-Tat: copy the
# opponent's previous move, but if they defect twice in a row, continue
# defecting until the end of the game.  10. Throughout the game, if the opponent
# establishes a clear pattern (e.g., alternating C and D), adjust your strategy
# to maximize points against that pattern.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_count = 0
          self.mutual_defection_count = 0
          self.forgiveness_used = False
          return axl.Action.C
  
      # Helper function to calculate opponent's cooperation ratio
      def cooperation_ratio():
          total_moves = len(opponent.history)
          if total_moves == 0:
              return 1  # Assume full cooperation if no moves yet
          return opponent.history.cooperations / total_moves
  
      # Step 2: If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If opponent played D in the previous round, punish with D for two rounds
      if opponent.history[-1] == axl.Action.D:
          if self.punishment_count > 0:
              self.punishment_count -= 1
              return axl.Action.D
          else:
              self.punishment_count = 2
              return axl.Action.D
  
      # Step 5: Track opponent's cooperation ratio
      coop_ratio = cooperation_ratio()
  
      # Step 6: If opponent's cooperation ratio falls below 0.3, switch to always D
      if coop_ratio < 0.3:
          if coop_ratio > 0.5:
              return axl.Action.C
          return axl.Action.D
  
      # Step 7: If both players have been defecting for more than 10 rounds, try to restart cooperation
      if len(self.history) >= 10 and all(move == axl.Action.D for move in self.history[-10:]) and all(move == axl.Action.D for move in opponent.history[-10:]):
          self.mutual_defection_count += 1
          if self.mutual_defection_count > 10:
              self.mutual_defection_count = 0
              return axl.Action.C
  
      # Step 8: Allow for a single forgiveness round
      if not self.forgiveness_used and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          self.forgiveness_used = True
          return axl.Action.C
  
      # Step 9: In the last 20 rounds, play modified Tit-for-Tat
      if len(self.history) >= 980:
          if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          return opponent.history[-1]
  
      # Step 10: Adjust strategy for clear patterns (e.g., alternating C and D)
      if len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]:
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C

# Here's a revised strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For each subsequent round:    - If the opponent
# cooperated in the previous round, cooperate.    - If the opponent defected in
# the previous round, defect.  3. Every 50 rounds, evaluate the overall
# performance:    - If your total score is higher than or equal to your
# opponent's, cooperate in the next round.    - If your total score is lower
# than your opponent's, defect in the next round.  4. If the opponent has
# defected for 3 consecutive rounds, defect for the next 2 rounds.  5. If you
# and your opponent have both cooperated for 10 consecutive rounds, continue
# cooperating until the opponent defects.  6. If your score falls more than 30
# points behind your opponent's at any point, defect for the next 3 rounds.  7.
# Starting from round 950 (i.e., the last 50 rounds):    - If your total score
# is higher than your opponent's, continue using the strategy from steps 2-6.
# - If your total score is lower than or equal to your opponent's, always
# defect.  8. Repeat steps 2-7 for each round until the game ends.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.behind_by_30 = False
          self.behind_by_30_rounds = 0
          return axl.Action.C
  
      # Get the last action of the opponent
      last_opponent_action = opponent.history[-1]
  
      # Step 4: Track consecutive defections
      if last_opponent_action == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Step 5: Track consecutive cooperations
      if last_opponent_action == axl.Action.C and self.history[-1] == axl.Action.C:
          self.consecutive_cooperations += 1
      else:
          self.consecutive_cooperations = 0
  
      # Step 6: Check if behind by more than 30 points
      if self.score < opponent.score - 30:
          self.behind_by_30 = True
          self.behind_by_30_rounds = 3
  
      # Step 7: Special behavior for the last 50 rounds
      if len(self.history) >= 950:
          if self.score <= opponent.score:
              return axl.Action.D
          else:
              # Continue with the normal strategy
              pass
  
      # Step 3: Every 50 rounds, evaluate performance
      if len(self.history) % 50 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 4: If opponent defected 3 times in a row, defect for the next 2 rounds
      if self.consecutive_defections >= 3:
          return axl.Action.D if len(self.history) - self.consecutive_defections < 2 else axl.Action.C
  
      # Step 5: If both cooperated for 10 consecutive rounds, continue cooperating
      if self.consecutive_cooperations >= 10:
          return axl.Action.C
  
      # Step 6: If behind by more than 30 points, defect for 3 rounds
      if self.behind_by_30:
          self.behind_by_30_rounds -= 1
          if self.behind_by_30_rounds == 0:
              self.behind_by_30 = False
          return axl.Action.D
  
      # Step 2: Tit-for-tat behavior
      if last_opponent_action == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C with 80% probability and D with 20% probability.  3. If the
# opponent played D in the previous round, play D.  4. If the opponent has
# played C for the last 3 consecutive rounds, play C.  5. Every 50 rounds,
# analyze the opponent's play pattern:    - If they've cooperated more than 60%
# of the time, increase your cooperation probability in step 2 to 90%.    - If
# they've cooperated less than 40% of the time, decrease your cooperation
# probability in step 2 to 70%.  6. In rounds 900-990, play according to steps
# 2-5.  7. In the last 10 rounds (991-1000), always play D.  8. Repeat steps 2-7
# for the duration of the game.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_prob = 0.8  # Initial cooperation probability
          return axl.Action.C  # Always cooperate on the first round
  
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if opponent has cooperated for the last 3 consecutive rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.C
  
      # If opponent played D in the last round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If opponent played C in the last round, cooperate with probability coop_prob
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(self.coop_prob)
  
      # Every 50 rounds, adjust cooperation probability based on opponent's cooperation rate
      if len(self.history) % 50 == 0:
          coop_rate = opponent.history.cooperations / len(opponent.history)
          if coop_rate > 0.6:
              self.coop_prob = 0.9
          elif coop_rate < 0.4:
              self.coop_prob = 0.7
  
      # Default to defect if none of the above conditions are met
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C in the current round.  3. If the opponent played D in the
# previous round, play D for the next three rounds, then return to playing C.
# 4. If the opponent plays D for five out of the last seven rounds, switch to
# always playing D.  5. If at any point the opponent switches back to consistent
# cooperation (playing C for at least 7 consecutive rounds), resume the
# cooperative strategy from step 2.  6. Implement a forgiveness mechanism: Every
# 50 rounds, if currently in always-defect mode, play C for one round to test if
# the opponent is willing to cooperate again.  7. In the last 20 rounds of the
# game, match the opponent's play from the previous round (Tit-for-Tat).  8. If
# the opponent's play pattern seems random or alternating, default to playing C
# 2/3 of the time and D 1/3 of the time to maintain a balance between
# cooperation and protection against exploitation.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_mode = False  # Track if we are in always-defect mode
          self.defect_counter = 0   # Track how many rounds we have defected
          self.forgive_round = 50   # Track when to forgive
          self.random_mode = False  # Track if we are in random mode
          return axl.Action.C       # Start by playing C
  
      # Last 20 rounds: Tit-for-Tat
      if len(self.history) >= 980:
          return opponent.history[-1]
  
      # Forgiveness mechanism: Every 50 rounds, test cooperation if in defect mode
      if self.defect_mode and len(self.history) % 50 == 0:
          return axl.Action.C
  
      # If opponent cooperates for 7 consecutive rounds, resume cooperation strategy
      if self.defect_mode and opponent.history[-7:] == [axl.Action.C] * 7:
          self.defect_mode = False
          self.defect_counter = 0
          self.random_mode = False
  
      # If in always-defect mode, continue defecting
      if self.defect_mode:
          return axl.Action.D
  
      # Check if opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          self.defect_counter += 1
          if self.defect_counter <= 3:
              return axl.Action.D
          else:
              self.defect_counter = 0
              return axl.Action.C
      else:
          self.defect_counter = 0
  
      # Check if opponent defected 5 out of the last 7 rounds
      if len(opponent.history) >= 7 and opponent.history[-7:].count(axl.Action.D) >= 5:
          self.defect_mode = True
          return axl.Action.D
  
      # Detect random or alternating pattern and switch to probabilistic strategy
      if len(opponent.history) >= 10:
          recent_moves = opponent.history[-10:]
          if recent_moves.count(axl.Action.C) == 5 and recent_moves.count(axl.Action.D) == 5:
              self.random_mode = True
  
      if self.random_mode:
          return self._random.random_choice(2 / 3)
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# Here's a revised strategy for the game:  1. Start by cooperating in the first
# round.  2. If the opponent cooperated in the previous round, cooperate in the
# current round.  3. If the opponent defected in the previous round, defect in
# the current round.  4. If the opponent has defected for three consecutive
# rounds, defect for the next two rounds regardless of their actions.  5. Every
# 50 rounds, cooperate regardless of the opponent's previous action to
# potentially break cycles of mutual defection.  6. In the last 20 rounds, play
# a mixed strategy: defect with 70% probability and cooperate with 30%
# probability.  7. If your score is more than 15 points lower than your
# opponent's, defect for the next three rounds, then reassess.  8. If mutual
# defection has occurred for more than 10 consecutive rounds, attempt to break
# the cycle by cooperating for two rounds.  9. Keep a running tally of the
# opponent's cooperation rate. If it falls below 40% over the last 50 rounds,
# increase your defection probability to 60% for the next 10 rounds.  10. If the
# opponent seems to be mirroring your strategy (same action in more than 90% of
# the last 20 rounds), occasionally defect (20% probability) when you would
# normally cooperate to avoid being too predictable.  11. Return to the basic
# tit-for-tat strategy (steps 2 and 3) after any deviation caused by steps 4-10.
# 12. Reassess the effectiveness of your strategy every 100 rounds. If your
# score is consistently lower than what you'd get from always defecting, switch
# to always defecting for the remainder of the game.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_for_next_n_rounds = 0
          self.cooperate_for_next_n_rounds = 0
          self.defection_probability = 0.0
          self.mirroring_check_rounds = 0
          self.mirroring_defect_probability = 0.0
          self.reassess_round = 100
          return axl.Action.C
  
      # Step 2: Tit-for-tat (basic)
      if self.defect_for_next_n_rounds > 0:
          self.defect_for_next_n_rounds -= 1
          return axl.Action.D
  
      if self.cooperate_for_next_n_rounds > 0:
          self.cooperate_for_next_n_rounds -= 1
          return axl.Action.C
  
      if len(self.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          self.defect_for_next_n_rounds = 2
          return axl.Action.D
  
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      if len(self.history) >= 980:
          return self._random.random_choice(0.3)
  
      if self.score - opponent.score < -15:
          self.defect_for_next_n_rounds = 3
          return axl.Action.D
  
      if len(self.history) >= 10 and self.history[-10:] == [axl.Action.D] * 10:
          self.cooperate_for_next_n_rounds = 2
          return axl.Action.C
  
      if len(self.history) >= 50:
          opponent_cooperation_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if opponent_cooperation_rate < 0.4:
              self.defection_probability = 0.6
          else:
              self.defection_probability = 0.0
  
      if len(self.history) >= 20:
          mirroring_count = sum(1 for i in range(1, 21) if self.history[-i] == opponent.history[-i])
          if mirroring_count > 18:
              self.mirroring_defect_probability = 0.2
          else:
              self.mirroring_defect_probability = 0.0
  
      if self.mirroring_defect_probability > 0 and self._random.random_choice(self.mirroring_defect_probability):
          return axl.Action.D
  
      if self.defection_probability > 0 and self._random.random_choice(self.defection_probability):
          return axl.Action.D
  
      if len(self.history) >= self.reassess_round:
          always_defect_score = len(self.history) * 1
          if self.score < always_defect_score:
              return axl.Action.D
          self.reassess_round += 100
  
      return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D

# Here's a revised aggressive strategy for the iterated normal-form game:  1.
# Start by defecting (D) in the first round.  2. If the opponent cooperated (C)
# in the previous round, defect (D) with 80% probability and cooperate (C) with
# 20% probability.  3. If the opponent defected (D) in the previous round,
# defect (D) with 90% probability and cooperate (C) with 10% probability.  4.
# Every 7-13 rounds (randomly chosen), regardless of the opponent's previous
# move, defect (D).  5. If your overall score is lower than the opponent's score
# after 100 rounds, increase the probability of defection by 10% for the next 50
# rounds.  6. If the opponent has cooperated (C) for 3-5 consecutive rounds
# (randomly chosen), defect (D) on the next round.  7. In the last 20 rounds of
# the game, defect (D) with 95% probability and cooperate (C) with 5%
# probability.  8. Every 50 rounds, analyze the opponent's pattern of play. If
# they defect more than 60% of the time, always defect for the next 10 rounds.
# 9. For any situation not covered by the above rules, defect (D) with 70%
# probability and cooperate (C) with 30% probability.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_rounds = self._random.randint(7, 13)
          self.consecutive_cooperations = self._random.randint(3, 5)
          self.defection_increase_round = 100
          self.defection_increase_active = False
          self.defection_increase_end = 0
          self.analyze_round = 50
          self.analyze_defect_rounds = 0
          self.endgame_start = 980
  
      # Rule 1: First round is always a defection
      if len(self.history) == 0:
          return axl.Action.D
  
      # Rule 7: In the last 20 rounds, defect with 95% probability
      if len(self.history) >= self.endgame_start:
          return self._random.random_choice(0.05)
  
      # Rule 4: Every 7-13 rounds, defect
      if len(self.history) % self.defect_rounds == 0:
          self.defect_rounds = self._random.randint(7, 13)
          return axl.Action.D
  
      # Rule 6: If opponent has cooperated for 3-5 consecutive rounds, defect
      if len(opponent.history) >= self.consecutive_cooperations:
          if all(move == axl.Action.C for move in opponent.history[-self.consecutive_cooperations:]):
              self.consecutive_cooperations = self._random.randint(3, 5)
              return axl.Action.D
  
      # Rule 5: If score is lower after 100 rounds, increase defection probability
      if len(self.history) == self.defection_increase_round:
          if self.score < opponent.score:
              self.defection_increase_active = True
              self.defection_increase_end = self.defection_increase_round + 50
          self.defection_increase_round += 100
  
      if self.defection_increase_active and len(self.history) <= self.defection_increase_end:
          defect_prob = 0.8 + 0.1  # Increase defection probability by 10%
      else:
          defect_prob = 0.8
  
      # Rule 8: Every 50 rounds, analyze opponent's defection rate
      if len(self.history) == self.analyze_round:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.6:
              self.analyze_defect_rounds = 10
          self.analyze_round += 50
  
      if self.analyze_defect_rounds > 0:
          self.analyze_defect_rounds -= 1
          return axl.Action.D
  
      # Rule 2: If opponent cooperated last round, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)
  
      # Rule 3: If opponent defected last round, defect with 90% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1)
  
      # Rule 9: Default case, defect with 70% probability
      return self._random.random_choice(0.3)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next round, then return to C.  4. Keep track of the opponent's cooperation
# rate. If it falls below 40% in the last 50 moves, switch to playing D until
# the rate rises above 60%.  5. Every 100 rounds, if the opponent's overall
# cooperation rate is above 70%, play C for the next 5 rounds regardless of the
# opponent's actions.  6. If the game has passed 900 rounds, base your decision
# on the opponent's cooperation rate in the last 100 moves:    - If it's above
# 80%, continue playing C.    - If it's between 50% and 80%, play C with 70%
# probability and D with 30% probability.    - If it's below 50%, play D.  7.
# Introduce a 5% random chance to play the opposite of what the strategy
# suggests to maintain unpredictability.  8. In the final round, play D.  9. If
# at any point the opponent returns to consistent cooperation (plays C for 5
# consecutive rounds), resume cooperating by playing C.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_streak = 0  # Track opponent's cooperation streak
          return axl.Action.C  # Start by playing C
  
      # Helper function to calculate cooperation rate over the last N moves
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Track opponent's cooperation streak
      if opponent.history[-1] == axl.Action.C:
          self.cooperation_streak += 1
      else:
          self.cooperation_streak = 0
  
      # Rule 9: If opponent cooperates for 5 consecutive rounds, resume cooperation
      if self.cooperation_streak >= 5:
          return axl.Action.C
  
      # Rule 2: If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent played D in the previous round, play D, then return to C
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) > 1 and self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D
  
      # Rule 4: If opponent's cooperation rate in the last 50 moves falls below 40%, switch to D
      if cooperation_rate(opponent.history, 50) < 0.4:
          if cooperation_rate(opponent.history, 50) > 0.6:
              return axl.Action.C
          return axl.Action.D
  
      # Rule 5: Every 100 rounds, if opponent's overall cooperation rate is above 70%, play C for 5 rounds
      if len(self.history) % 100 == 0 and cooperation_rate(opponent.history, len(opponent.history)) > 0.7:
          if len(self.history) % 100 < 5:
              return axl.Action.C
  
      # Rule 6: After 900 rounds, base decision on cooperation rate in the last 100 moves
      if len(self.history) > 900:
          coop_rate_last_100 = cooperation_rate(opponent.history, 100)
          if coop_rate_last_100 > 0.8:
              return axl.Action.C
          elif 0.5 <= coop_rate_last_100 <= 0.8:
              return self._random.random_choice(0.7)
          else:
              return axl.Action.D
  
      # Rule 7: Introduce a 5% random chance to play the opposite of the strategy
      if self._random.random_choice(0.05):
          return axl.Action.D if self.history[-1] == axl.Action.C else axl.Action.C
  
      # Rule 8: In the final round, play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect with a 90% probability and cooperate with a 10%
# probability.  4. If the opponent has defected for three consecutive rounds,
# defect for the next round, then return to step 2.  5. Every 25 rounds, assess
# the opponent's behavior:    - If they've cooperated more than 60% of the time,
# cooperate for the next 5 rounds.    - If they've defected more than 60% of the
# time, defect for the next 5 rounds.    - Otherwise, continue with the main
# strategy.  6. If your overall score is lower than your opponent's by more than
# 30 points after every 100 rounds, increase your defection probability to 70%
# for the next 10 rounds, then return to the main strategy.  7. In the last 20
# rounds, play a mixed strategy: defect with 70% probability and cooperate with
# 30% probability.  8. If the opponent switches from a defecting pattern to
# cooperation for at least 3 consecutive rounds, respond with cooperation for
# the next 2 rounds to encourage mutual cooperation.  9. Repeat steps 2-8 until
# the game ends.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.9
          self.special_mode = False
          self.special_mode_rounds = 0
          self.last_100_rounds_check = 0
          self.last_25_rounds_check = 0
          return axl.Action.C
  
      # Step 7: In the last 20 rounds, play a mixed strategy
      if len(self.history) >= 980:
          return self._random.random_choice(0.3)
  
      # Step 4: If opponent defected for 3 consecutive rounds, defect this round
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Step 8: If opponent switches from defecting to cooperating for 3 rounds, cooperate for 2 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.C, axl.Action.C]:
              return axl.Action.C
  
      # Step 5: Every 25 rounds, assess opponent's behavior
      if len(self.history) % 25 == 0 and len(self.history) > self.last_25_rounds_check:
          self.last_25_rounds_check = len(self.history)
          cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if cooperation_rate > 0.6:
              self.special_mode = 'cooperate'
              self.special_mode_rounds = 5
          elif cooperation_rate < 0.4:
              self.special_mode = 'defect'
              self.special_mode_rounds = 5
  
      # Step 6: Every 100 rounds, check score difference
      if len(self.history) % 100 == 0 and len(self.history) > self.last_100_rounds_check:
          self.last_100_rounds_check = len(self.history)
          my_score, opponent_score = self.total_scores(self.history[-100:], opponent.history[-100:])
          if opponent_score - my_score > 30:
              self.defection_probability = 0.7
              self.special_mode = 'defect'
              self.special_mode_rounds = 10
  
      # Handle special mode (cooperate or defect for a fixed number of rounds)
      if self.special_mode:
          self.special_mode_rounds -= 1
          if self.special_mode_rounds == 0:
              self.special_mode = False
          return axl.Action.C if self.special_mode == 'cooperate' else axl.Action.D
  
      # Step 2: If opponent cooperated last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If opponent defected last round, defect with 90% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1)


Aggressive_ranks = [
'Aggressive_21',
'Aggressive_23',
'Aggressive_14',
'Aggressive_7',
'Aggressive_20',
'Aggressive_18',
'Aggressive_16',
'Aggressive_13',
'Aggressive_24',
'Aggressive_19',
'Aggressive_6',
'Aggressive_9',
'Aggressive_22',
'Aggressive_2',
'Aggressive_25',
'Aggressive_1',
'Aggressive_10',
'Aggressive_4',
'Aggressive_11',
'Aggressive_5',
'Aggressive_12',
'Aggressive_17',
'Aggressive_3',
'Aggressive_15',
'Aggressive_8',
]

Cooperative_ranks = [
'Cooperative_12',
'Cooperative_11',
'Cooperative_13',
'Cooperative_21',
'Cooperative_23',
'Cooperative_22',
'Cooperative_2',
'Cooperative_15',
'Cooperative_17',
'Cooperative_1',
'Cooperative_24',
'Cooperative_5',
'Cooperative_14',
'Cooperative_8',
'Cooperative_7',
'Cooperative_25',
'Cooperative_16',
'Cooperative_10',
'Cooperative_19',
'Cooperative_4',
'Cooperative_9',
'Cooperative_20',
'Cooperative_3',
'Cooperative_18',
'Cooperative_6',
]

Neutral_ranks = [
'Neutral_13',
'Neutral_16',
'Neutral_9',
'Neutral_8',
'Neutral_22',
'Neutral_18',
'Neutral_21',
'Neutral_7',
'Neutral_3',
'Neutral_23',
'Neutral_19',
'Neutral_20',
'Neutral_11',
'Neutral_10',
'Neutral_4',
'Neutral_17',
'Neutral_2',
'Neutral_6',
'Neutral_25',
'Neutral_14',
'Neutral_12',
'Neutral_1',
'Neutral_24',
'Neutral_5',
'Neutral_15',
]
