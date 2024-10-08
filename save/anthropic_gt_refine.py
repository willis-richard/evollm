import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

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
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if my_score < 0.9 * opponent_score:
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



Aggressive_ranks = [
'Aggressive_7',
'Aggressive_1',
'Aggressive_6',
'Aggressive_9',
'Aggressive_2',
'Aggressive_10',
'Aggressive_4',
'Aggressive_5',
'Aggressive_3',
'Aggressive_8',
]

Cooperative_ranks = [
'Cooperative_2',
'Cooperative_5',
'Cooperative_8',
'Cooperative_7',
'Cooperative_10',
'Cooperative_4',
'Cooperative_9',
'Cooperative_3',
'Cooperative_1',
'Cooperative_6',
]

Neutral_ranks = [
'Neutral_9',
'Neutral_3',
'Neutral_8',
'Neutral_7',
'Neutral_10',
'Neutral_4',
'Neutral_2',
'Neutral_6',
'Neutral_1',
'Neutral_5',
]