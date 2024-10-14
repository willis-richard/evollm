import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy



# Here's a simple aggressive strategy for the described iterated game:  1. Start
# by defecting (D) in the first round.  2. If the opponent defected in the
# previous round, defect in the current round.  3. If the opponent cooperated in
# the previous round, defect with 80% probability and cooperate with 20%
# probability.  4. If you've defected for 5 consecutive rounds and your opponent
# has cooperated for all of those rounds, cooperate in the next round.  5. In
# the last 10 rounds of the game, always defect regardless of the opponent's
# actions.  6. If your current score is significantly lower than your opponent's
# (more than 20 points behind), increase the probability of defection to 90% for
# the next 10 rounds.  7. Reset to the base strategy after those 10 rounds or if
# the score difference becomes less than 20 points.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.defection_boost = 0         # Track rounds with increased defection probability
          return axl.Action.D
  
      # Step 5: In the last 10 rounds of the game, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 6: If your score is significantly lower than your opponent's, increase defection probability
      if self.defection_boost > 0:
          self.defection_boost -= 1
          if self._random.random_choice(0.9):
              return axl.Action.D
          else:
              return axl.Action.C
      elif self.score + 20 < opponent.score:
          self.defection_boost = 10
          if self._random.random_choice(0.9):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Step 2: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D
  
      # Step 3: If the opponent cooperated in the previous round, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          if self._random.random_choice(0.8):
              self.consecutive_defections += 1
              return axl.Action.D
          else:
              self.consecutive_defections = 0
              return axl.Action.C
  
      # Step 4: If you've defected for 5 consecutive rounds and the opponent has cooperated for all of those rounds, cooperate
      if self.consecutive_defections >= 5 and all(opponent.history[-5:] == [axl.Action.C] * 5):
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Default to defect if no other condition is met
      return axl.Action.D



# Here's a simple cooperative strategy for the game:  1. Start by playing C in
# the first round.  2. In subsequent rounds:    - Play C if the opponent played
# C in the previous round.    - Play D if the opponent played D in the previous
# round.  3. Every 10 rounds, forgive any defection and play C regardless of the
# opponent's last move.  4. If the opponent has defected more than 60% of the
# time in the last 50 rounds, switch to always playing D for the next 10 rounds
# before returning to the main strategy.  5. In the last 10 rounds of the game,
# always play D to protect against end-game defection.  6. If your score falls
# more than 100 points behind your opponent's at any point, switch to always
# playing D for the next 20 rounds before returning to the main strategy.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      FORGIVENESS_ROUND_INTERVAL = 10
      DEFECT_THRESHOLD = 0.6
      DEFECT_PENALTY_ROUNDS = 10
      SCORE_DIFFERENCE_THRESHOLD = 100
      SCORE_PENALTY_ROUNDS = 20
      LAST_ROUNDS = 10
      TOTAL_ROUNDS = 1000
      LOOKBACK_ROUNDS = 50
  
      # First round: always cooperate
      if self.first_round():
          self.defect_penalty_counter = 0  # Counter for defect penalty rounds
          self.score_penalty_counter = 0   # Counter for score penalty rounds
          return axl.Action.C
  
      # If in the last 10 rounds, always defect
      if len(self.history) >= TOTAL_ROUNDS - LAST_ROUNDS:
          return axl.Action.D
  
      # If in defect penalty mode, always defect for the next DEFECT_PENALTY_ROUNDS
      if self.defect_penalty_counter > 0:
          self.defect_penalty_counter -= 1
          return axl.Action.D
  
      # If in score penalty mode, always defect for the next SCORE_PENALTY_ROUNDS
      if self.score_penalty_counter > 0:
          self.score_penalty_counter -= 1
          return axl.Action.D
  
      # Check if the opponent has defected more than 60% in the last 50 rounds
      if len(opponent.history) >= LOOKBACK_ROUNDS:
          recent_defections = opponent.history[-LOOKBACK_ROUNDS:].count(axl.Action.D)
          if recent_defections / LOOKBACK_ROUNDS > DEFECT_THRESHOLD:
              self.defect_penalty_counter = DEFECT_PENALTY_ROUNDS
              return axl.Action.D
  
      # Check if the score difference is more than 100 points
      if self.score - opponent.score < -SCORE_DIFFERENCE_THRESHOLD:
          self.score_penalty_counter = SCORE_PENALTY_ROUNDS
          return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % FORGIVENESS_ROUND_INTERVAL == 0:
          return axl.Action.C
  
      # Default behavior: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. In subsequent rounds:    - Cooperate if the opponent
# cooperated in the previous round.    - Defect if the opponent defected in the
# previous round.  3. Every 10 rounds, regardless of the opponent's last move:
# - Cooperate if your total score is higher than or equal to the opponent's.
# - Defect if your total score is lower than the opponent's.  4. If you notice a
# consistent pattern of the opponent always defecting for 5 or more consecutive
# rounds:    - Switch to always defecting for the next 5 rounds.    - After
# these 5 rounds, return to the main strategy (points 2 and 3).  5. In the last
# 10 rounds of the game:    - Always defect, regardless of the opponent's
# actions.  6. If at any point your score falls behind the opponent's by 20
# points or more:    - Defect for the next 3 rounds, then return to the main
# strategy.  Follow these rules in the order presented, applying the first
# relevant condition in each round.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      SCORE_THRESHOLD = 20
      DEFECT_STREAK_THRESHOLD = 5
      DEFECT_PENALTY_ROUNDS = 3
      DEFECT_RETALIATION_ROUNDS = 5
      TOTAL_ROUNDS = 1000
      FINAL_ROUNDS_THRESHOLD = 10
      CHECK_SCORE_INTERVAL = 10
  
      # First round: Cooperate
      if self.first_round():
          self.defect_streak = 0  # Track opponent's defect streak
          self.penalty_rounds = 0  # Track penalty rounds for falling behind
          self.retaliation_rounds = 0  # Track retaliation rounds for opponent's defect streak
          return COOPERATE
  
      # Last 10 rounds: Always defect
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS_THRESHOLD:
          return DEFECT
  
      # If in penalty rounds for falling behind by 20 points or more, defect for 3 rounds
      if self.penalty_rounds > 0:
          self.penalty_rounds -= 1
          return DEFECT
  
      # If in retaliation rounds for opponent's defect streak, defect for 5 rounds
      if self.retaliation_rounds > 0:
          self.retaliation_rounds -= 1
          return DEFECT
  
      # Check if opponent has defected for 5 or more consecutive rounds
      if opponent.history[-DEFECT_STREAK_THRESHOLD:].count(DEFECT) == DEFECT_STREAK_THRESHOLD:
          self.retaliation_rounds = DEFECT_RETALIATION_ROUNDS
          return DEFECT
  
      # Every 10 rounds, compare scores and decide whether to cooperate or defect
      if len(self.history) % CHECK_SCORE_INTERVAL == 0:
          if self.score >= opponent.score:
              return COOPERATE
          else:
              return DEFECT
  
      # If score difference is 20 or more, defect for the next 3 rounds
      if opponent.score - self.score >= SCORE_THRESHOLD:
          self.penalty_rounds = DEFECT_PENALTY_ROUNDS
          return DEFECT
  
      # Default strategy: Cooperate if opponent cooperated last round, otherwise defect
      if opponent.history[-1] == COOPERATE:
          return COOPERATE
      else:
          return DEFECT



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous move.  5. In the last 10
# rounds of the game, always defect.  6. If your current score is significantly
# lower than your opponent's (more than 50 points behind), switch to always
# defecting for the next 20 rounds.  7. If you've cooperated for 3 consecutive
# rounds, defect in the next round regardless of the opponent's actions.  8. If
# the opponent has cooperated for 5 consecutive rounds, cooperate once, then
# return to the main strategy.  Follow these rules in the order presented,
# defaulting to defection if no specific condition is met.

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
          self.consecutive_cooperations = 0
          self.consecutive_opponent_cooperations = 0
          self.always_defect_counter = 0
          return axl.Action.D  # Start by defecting
  
      # Rule 6: If significantly behind in score, switch to always defecting for 20 rounds
      if self.always_defect_counter > 0:
          self.always_defect_counter -= 1
          return axl.Action.D
  
      if self.score < opponent.score - 50:
          self.always_defect_counter = 20
          return axl.Action.D
  
      # Rule 7: If cooperated for 3 consecutive rounds, defect
      if self.consecutive_cooperations >= 3:
          self.consecutive_cooperations = 0
          return axl.Action.D
  
      # Rule 8: If opponent cooperated for 5 consecutive rounds, cooperate once
      if self.consecutive_opponent_cooperations >= 5:
          self.consecutive_opponent_cooperations = 0
          return axl.Action.C
  
      # Rule 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 2 and 3: Respond based on opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          # 80% chance to defect, 20% chance to cooperate
          return self._random.random_choice(0.2)
  
      # Default to defection if no other rule applies
      return axl.Action.D



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before returning to the main strategy.  5. In the last 10
# rounds of the game, always play D to protect against end-game defection.  6.
# Ignore any isolated defections, as they may be due to noise. Only respond to
# defection if the opponent has defected twice in a row.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      FORGIVENESS_ROUND_INTERVAL = 10
      DEFECT_THRESHOLD = 0.6
      DEFECT_MONITOR_WINDOW = 50
      DEFECT_PENALTY_ROUNDS = 10
      END_GAME_THRESHOLD = 10
      TOTAL_ROUNDS = 1000
  
      # First round: always cooperate
      if self.first_round():
          self.penalty_rounds = 0  # Track penalty rounds for defect punishment
          return axl.Action.C
  
      # Last 10 rounds: always defect
      if len(self.history) >= TOTAL_ROUNDS - END_GAME_THRESHOLD:
          return axl.Action.D
  
      # If in penalty rounds, always defect
      if self.penalty_rounds > 0:
          self.penalty_rounds -= 1
          return axl.Action.D
  
      # Check if opponent has defected more than 60% in the last 50 rounds
      if len(opponent.history) >= DEFECT_MONITOR_WINDOW:
          recent_defections = opponent.history[-DEFECT_MONITOR_WINDOW:].count(axl.Action.D)
          if recent_defections / DEFECT_MONITOR_WINDOW > DEFECT_THRESHOLD:
              self.penalty_rounds = DEFECT_PENALTY_ROUNDS
              return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % FORGIVENESS_ROUND_INTERVAL == 0:
          return axl.Action.C
  
      # Respond to opponent's last move
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
      elif opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. Keep track of your opponent's actions throughout the
# game.  3. If your opponent has cooperated in at least 60% of the previous
# rounds, cooperate.  4. If your opponent has defected in at least 60% of the
# previous rounds, defect.  5. If your opponent's cooperation rate is between
# 40% and 60%, copy their last move.  6. Every 50 rounds, regardless of the
# opponent's actions, cooperate once to test for a potential shift in their
# strategy.  7. In the last 10 rounds of the game, always defect to maximize
# final payoff.  8. If at any point your average score per round falls below
# 1.5, switch to always defecting for the next 20 rounds before reverting to the
# main strategy.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 0.6
      DEFECTION_THRESHOLD = 0.4
      SCORE_THRESHOLD = 1.5
      DEFECT_PERIOD = 20
      TEST_PERIOD = 50
      FINAL_ROUNDS = 10
      TOTAL_ROUNDS = 1000
  
      # First round: cooperate
      if self.first_round():
          self.defect_counter = 0  # Track rounds of forced defection
          return axl.Action.C
  
      # If in forced defection mode, defect for the next 20 rounds
      if self.defect_counter > 0:
          self.defect_counter -= 1
          return axl.Action.D
  
      # Calculate cooperation rate of opponent
      total_rounds = len(opponent.history)
      opponent_cooperations = opponent.history.cooperations
      opponent_defections = opponent.history.defections
      cooperation_rate = opponent_cooperations / total_rounds if total_rounds > 0 else 0
  
      # Check if we are in the last 10 rounds
      if total_rounds >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return axl.Action.D
  
      # Every 50 rounds, cooperate to test for strategy shift
      if total_rounds % TEST_PERIOD == 0:
          return axl.Action.C
  
      # If opponent cooperates at least 60% of the time, cooperate
      if cooperation_rate >= COOPERATION_THRESHOLD:
          return axl.Action.C
  
      # If opponent defects at least 60% of the time, defect
      if cooperation_rate <= 1 - DEFECTION_THRESHOLD:
          return axl.Action.D
  
      # If cooperation rate is between 40% and 60%, copy opponent's last move
      if DEFECTION_THRESHOLD < cooperation_rate < COOPERATION_THRESHOLD:
          return opponent.history[-1]
  
      # Calculate average score per round
      total_score = self.score
      average_score = total_score / total_rounds if total_rounds > 0 else 0
  
      # If average score falls below 1.5, defect for the next 20 rounds
      if average_score < SCORE_THRESHOLD:
          self.defect_counter = DEFECT_PERIOD
          return axl.Action.D
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous move.  5. In the last 10
# rounds of the game, always defect.  6. If your current score is significantly
# lower than your opponent's (more than 50 points behind), switch to always
# defecting for the next 20 rounds.  7. If you're ahead by more than 100 points,
# cooperate for the next 5 rounds to avoid appearing too aggressive.  8. Return
# to step 2 and repeat until the game ends.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are in "always defect" mode
          self.coop_streak = 0    # Track how many rounds we are in "always cooperate" mode
          return axl.Action.D
  
      # Step 6: If significantly behind, switch to always defecting for 20 rounds
      if self.score < opponent.score - 50:
          self.defect_streak = 20
  
      # Step 7: If ahead by more than 100 points, cooperate for the next 5 rounds
      if self.score > opponent.score + 100:
          self.coop_streak = 5
  
      # Handle defect streak (Step 6)
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Handle coop streak (Step 7)
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 2 and 3: Defect if opponent defected last round, otherwise defect with 80% probability
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return self._random.random_choice(0.2)  # 20% chance to cooperate, 80% to defect



# Here's a simple cooperative strategy for the iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play C if you played D in the
# previous round (to correct for potential noise).    - Play D if the opponent
# has played D twice in a row.  3. If you've played D due to condition 2c,
# return to playing C in the next round unless the opponent plays D again.  4.
# Every 50 rounds, play C regardless of the opponent's previous move to
# encourage cooperation.  5. In the last 10 rounds of the game, always play D to
# protect against end-game defection.  6. If at any point the opponent has
# defected more than 60% of the time in the last 20 moves, switch to always
# playing D for the next 10 moves before returning to the main strategy.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: play C
      if self.first_round():
          self.defect_streak = 0  # Track how many times opponent defected in a row
          self.always_defect_counter = 0  # Track how many rounds to always defect
          return axl.Action.C
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if we are in the "always defect" mode
      if self.always_defect_counter > 0:
          self.always_defect_counter -= 1
          return axl.Action.D
  
      # Every 50 rounds, play C to encourage cooperation
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Check if opponent has defected more than 60% of the time in the last 20 moves
      if len(self.history) >= 20:
          recent_defections = opponent.history[-20:].count(axl.Action.D)
          if recent_defections / 20 > 0.6:
              self.always_defect_counter = 10
              return axl.Action.D
  
      # Main strategy logic
      if opponent.history[-1] == axl.Action.D:
          self.defect_streak += 1
      else:
          self.defect_streak = 0
  
      if self.defect_streak >= 2:
          return axl.Action.D
  
      if self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      return axl.Action.D



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent cooperated in
# the previous round, cooperate.    - If the opponent defected in the previous
# round, defect.  3. Every 10 rounds, forgive the opponent's last defection and
# cooperate regardless of their previous move.  4. If your score falls more than
# 20 points behind your opponent's score, defect for the next 5 rounds, then
# return to the main strategy.  5. In the last 10 rounds of the game, always
# defect.  6. Throughout the game, keep track of the opponent's cooperation
# rate. If it falls below 30%, switch to always defecting for the remainder of
# the game.  7. If you notice a clear pattern in the opponent's play (e.g.,
# alternating between cooperation and defection), adapt your strategy to exploit
# this pattern.  8. Given the 10% noise factor, don't overreact to single
# instances of unexpected behavior. Consider the opponent's overall trend rather
# than individual moves.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.forgive_round = 10  # Next round to forgive
          self.defect_streak = 0  # Track defect streak when behind
          self.always_defect = False  # Switch to always defect if opponent's cooperation rate is low
          self.pattern_detected = False  # Track if a pattern is detected
          return axl.Action.C  # Start by cooperating
  
      # Round number
      round_number = len(self.history) + 1
  
      # Check if we are in the last 10 rounds
      if round_number > 990:
          return axl.Action.D  # Always defect in the last 10 rounds
  
      # Check if we are more than 20 points behind the opponent
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D  # Continue defecting for the next 5 rounds
  
      if self.score < opponent.score - 20:
          self.defect_streak = 5  # Defect for the next 5 rounds
          return axl.Action.D
  
      # Check opponent's cooperation rate
      if opponent.history.cooperations / round_number < 0.3:
          self.always_defect = True  # Switch to always defect if cooperation rate is below 30%
  
      if self.always_defect:
          return axl.Action.D  # Always defect if cooperation rate is too low
  
      # Forgive every 10 rounds
      if round_number == self.forgive_round:
          self.forgive_round += 10  # Set next forgiveness round
          return axl.Action.C  # Forgive and cooperate
  
      # Detect simple patterns (e.g., alternating between C and D)
      if not self.pattern_detected and round_number > 4:
          recent_moves = opponent.history[-4:]
          if recent_moves == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
              self.pattern_detected = True  # Detected alternating pattern
  
      if self.pattern_detected:
          # Exploit alternating pattern by defecting when opponent is expected to cooperate
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Main strategy: Tit-for-Tat with forgiveness
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Defect if opponent defected last round
      else:
          return axl.Action.C  # Cooperate if opponent cooperated last round



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect in the current round.  3. If the opponent cooperated in the
# previous round, defect with 80% probability and cooperate with 20%
# probability.  4. Every 50 rounds, cooperate for one round regardless of the
# opponent's previous action.  5. If your current score is lower than the
# opponent's score by 10 points or more, defect for the next 5 rounds regardless
# of the opponent's actions.  6. In the last 10 rounds of the game, always
# defect.  7. If none of the above conditions are met, defect.  This strategy
# maintains an aggressive stance while occasionally allowing for cooperation to
# potentially trigger reciprocal cooperation from the opponent.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # 1. Start by defecting in the first round.
      if self.first_round():
          self.defect_streak = 0  # Initialize a counter for forced defections
          return axl.Action.D
  
      # 6. In the last 10 rounds of the game, always defect.
      if len(self.history) >= 990:
          return axl.Action.D
  
      # 5. If your current score is lower than the opponent's score by 10 points or more, defect for the next 5 rounds.
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
      elif self.score + 10 <= opponent.score:
          self.defect_streak = 5
          return axl.Action.D
  
      # 4. Every 50 rounds, cooperate for one round regardless of the opponent's previous action.
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # 2. If the opponent defected in the previous round, defect in the current round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 3. If the opponent cooperated in the previous round, defect with 80% probability and cooperate with 20% probability.
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)
  
      # 7. If none of the above conditions are met, defect.
      return axl.Action.D



# Here's a simple cooperative strategy for the game:  1. Start by playing C in
# the first round.  2. For subsequent rounds:    - Play C if the opponent played
# C in the previous round.    - Play D if the opponent played D in the previous
# round.  3. Every 10 rounds, forgive any defection and play C regardless of the
# opponent's last move.  4. If the opponent has defected more than 60% of the
# time in the last 50 rounds, switch to always playing D for the next 20 rounds
# before returning to the main strategy.  5. In the last 10 rounds of the game,
# always play D to protect against end-game defection.  6. Throughout the game,
# if you notice a consistent pattern of the opponent alternating between C and
# D, match their pattern by playing D when they play C and C when they play D.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to detect alternating pattern
      def is_alternating_pattern():
          if len(opponent.history) < 2:
              return False
          for i in range(1, len(opponent.history)):
              if opponent.history[i] == opponent.history[i - 1]:
                  return False
          return True
  
      # First round: always cooperate
      if self.first_round():
          self.defection_streak = 0  # Track defection streak for rule 4
          self.always_defect_counter = 0  # Track rounds of always defecting
          return axl.Action.C
  
      # Rule 6: If opponent alternates between C and D, match their pattern
      if is_alternating_pattern():
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Rule 4: If opponent defected more than 60% in the last 50 rounds, play D for 20 rounds
      if len(opponent.history) >= 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.6:
              if self.always_defect_counter < 20:
                  self.always_defect_counter += 1
                  return axl.Action.D
              else:
                  self.always_defect_counter = 0  # Reset after 20 rounds of defection
  
      # Rule 5: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 3: Every 10 rounds, forgive and play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 2: Play C if opponent played C last round, else play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:     a. If the opponent cooperated
# in the previous round, cooperate.        b. If the opponent defected in the
# previous round, defect with a 70% probability and cooperate with a 30%
# probability.  3. Every 10 rounds, regardless of the opponent's previous
# action:        a. If your average score is below 2, increase the defection
# probability to 80% for the next 10 rounds.        b. If your average score is
# above 2.5, decrease the defection probability to 60% for the next 10 rounds.
# 4. If the opponent has defected for 3 consecutive rounds, defect for the next
# 2 rounds regardless of their actions.  5. In the last 50 rounds of the game,
# increase the defection probability by 10% compared to the current level.  6.
# Always return to the base strategy (point 2) after any temporary adjustments.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_probability = 0.7
          self.consecutive_defections = 0
          self.force_defect_rounds = 0
          return axl.Action.C
  
      # Helper function to calculate average score
      def average_score():
          if len(self.history) == 0:
              return 0
          return self.score / len(self.history)
  
      # Check if we are in the last 50 rounds
      if len(self.history) >= 950:
          self.defection_probability = min(1.0, self.defection_probability + 0.1)
  
      # Check if opponent has defected for 3 consecutive rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.force_defect_rounds = 2
  
      # If we are in forced defection mode, defect for the next 2 rounds
      if self.force_defect_rounds > 0:
          self.force_defect_rounds -= 1
          return axl.Action.D
  
      # Every 10 rounds, adjust defection probability based on average score
      if len(self.history) % 10 == 0:
          avg_score = average_score()
          if avg_score < 2:
              self.defection_probability = 0.8
          elif avg_score > 2.5:
              self.defection_probability = 0.6
          else:
              self.defection_probability = 0.7
  
      # Base strategy: cooperate if opponent cooperated last round, otherwise defect with probability
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return self._random.random_choice(1 - self.defection_probability)



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous action.  5. In the last
# 10 rounds of the game, always defect.  6. If your current score is
# significantly lower than your opponent's (more than 50 points behind), switch
# to always defecting for the next 20 rounds.  7. If you're ahead by more than
# 100 points, cooperate for the next 5 rounds to avoid triggering retaliation.
# 8. Return to step 2 and repeat for the duration of the game.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are in "always defect" mode
          self.coop_streak = 0    # Track how many rounds we are in "always cooperate" mode
          return axl.Action.D
  
      # Step 6: If significantly behind, switch to always defecting for 20 rounds
      if self.score < opponent.score - 50:
          self.defect_streak = 20
  
      # Step 7: If ahead by more than 100 points, cooperate for the next 5 rounds
      if self.score > opponent.score + 100:
          self.coop_streak = 5
  
      # Handle defect streak (Step 6)
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Handle coop streak (Step 7)
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 2: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If the opponent cooperated in the previous round, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)  # 20% chance to cooperate, 80% to defect



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before returning to the main strategy.  5. In the last 10
# rounds of the game, always play D to protect against end-game defection.  6.
# If your score falls more than 50 points behind your opponent's at any point,
# switch to always playing D for the next 20 rounds before returning to the main
# strategy.  7. Ignore single, isolated defections, as they may be due to noise.
# Only count a defection if the opponent plays D twice in a row.

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
          self.defection_streak = 0  # Track consecutive defections
          self.defection_mode = False  # Track if we are in defection mode
          self.defection_mode_counter = 0  # Counter for defection mode duration
          return axl.Action.C  # Start by playing C
  
      # Helper function to check if opponent defected more than 60% in the last 50 rounds
      def opponent_defection_rate():
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          return recent_defections / min(50, len(opponent.history)) > 0.6
  
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 990
  
      # Helper function to check if we are more than 50 points behind
      def score_difference_too_large():
          return (opponent.score - self.score) > 50
  
      # Handle defection mode (always play D for a set number of rounds)
      if self.defection_mode:
          self.defection_mode_counter -= 1
          if self.defection_mode_counter <= 0:
              self.defection_mode = False  # Exit defection mode after the set duration
          return axl.Action.D
  
      # Check if we are in the last 10 rounds
      if in_last_10_rounds():
          return axl.Action.D  # Always play D in the last 10 rounds
  
      # Check if we are more than 50 points behind
      if score_difference_too_large():
          self.defection_mode = True
          self.defection_mode_counter = 20  # Defect for the next 20 rounds
          return axl.Action.D
  
      # Check if opponent defected more than 60% of the time in the last 50 rounds
      if opponent_defection_rate():
          self.defection_mode = True
          self.defection_mode_counter = 10  # Defect for the next 10 rounds
          return axl.Action.D
  
      # Check for isolated defections (ignore single defections)
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.defection_streak += 1
      else:
          self.defection_streak = 0
  
      # Every 10 rounds, forgive any defection and play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Main strategy: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the given iterated normal-form game:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    a. If the
# opponent has cooperated in the last 3 rounds, cooperate.    b. If the opponent
# has defected in the last 3 rounds, defect.    c. If the opponent's actions
# have been mixed in the last 3 rounds:       - Cooperate if you've scored more
# points than the opponent over the last 5 rounds.       - Defect if you've
# scored fewer points than the opponent over the last 5 rounds.       - If the
# scores are tied over the last 5 rounds, cooperate.  3. Every 50 rounds,
# regardless of the opponent's recent actions:    a. If your overall score is
# higher than the opponent's, cooperate for the next round.    b. If your
# overall score is lower than the opponent's, defect for the next round.    c.
# If the overall scores are tied, cooperate for the next round.  4. In the last
# 10 rounds of the game, always defect.  5. If at any point you're unsure about
# the opponent's last action due to noise, assume they cooperated.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Define actions for convenience
      C, D = axl.Action.C, axl.Action.D
  
      # 1. Start by cooperating in the first round
      if self.first_round():
          return C
  
      # 4. In the last 10 rounds of the game, always defect
      if len(self.history) >= 990:
          return D
  
      # Helper function to check the opponent's last 3 actions
      def last_n_actions(n, action):
          return opponent.history[-n:].count(action) == n
  
      # Helper function to calculate scores over the last N rounds
      def score_last_n_rounds(n):
          return self.total_scores(self.history[-n:], opponent.history[-n:])
  
      # 2. For subsequent rounds:
      if len(opponent.history) >= 3:
          # a. If the opponent has cooperated in the last 3 rounds, cooperate
          if last_n_actions(3, C):
              return C
          # b. If the opponent has defected in the last 3 rounds, defect
          elif last_n_actions(3, D):
              return D
          # c. If the opponent's actions have been mixed in the last 3 rounds:
          else:
              # Cooperate if you've scored more points than the opponent over the last 5 rounds
              if len(self.history) >= 5:
                  my_score, opp_score = score_last_n_rounds(5)
                  if my_score > opp_score:
                      return C
                  elif my_score < opp_score:
                      return D
                  else:
                      return C
              else:
                  return C  # Default to cooperation if less than 5 rounds have been played
  
      # 3. Every 50 rounds, check the overall score
      if len(self.history) % 50 == 0:
          if self.score > opponent.score:
              return C
          elif self.score < opponent.score:
              return D
          else:
              return C
  
      # 5. If unsure about the opponent's last action due to noise, assume they cooperated
      if opponent.history[-1] is None:
          return C
  
      # Default to cooperation if no other condition is met
      return C



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous move.  5. In the last 10
# rounds of the game, always defect.  6. If your current score is significantly
# lower than your opponent's (more than 50 points behind), switch to always
# defecting for the next 20 rounds.  7. If you're ahead by more than 100 points,
# cooperate for the next 5 rounds to avoid triggering retaliation.  8. Return to
# step 2 and repeat for the duration of the game.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # First round: always defect
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are in "always defect" mode
          self.coop_streak = 0    # Track how many rounds we are in "always cooperate" mode
          return axl.Action.D
      
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
      
      # Check if we are in a "defect streak" due to being behind by more than 50 points
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
      
      # Check if we are in a "cooperate streak" due to being ahead by more than 100 points
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
      
      # Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
      
      # If behind by more than 50 points, switch to always defecting for the next 20 rounds
      if self.score < opponent.score - 50:
          self.defect_streak = 20
          return axl.Action.D
      
      # If ahead by more than 100 points, cooperate for the next 5 rounds
      if self.score > opponent.score + 100:
          self.coop_streak = 5
          return axl.Action.C
      
      # If opponent defected in the last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      
      # If opponent cooperated in the last round, defect with 80% probability, cooperate with 20% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)



# Here's a simple cooperative strategy for the described game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before returning to the main strategy.  5. In the last 10
# rounds of the game, always play D to protect against end-game defection.  6.
# If your score is significantly lower than your opponent's (more than 50 points
# behind) after 100 rounds, switch to always playing D for 20 rounds before
# returning to the main strategy.  7. Account for noise by being slightly more
# forgiving: if the opponent's defection rate is between 5% and 15% over the
# last 50 rounds, continue playing C.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to calculate defection rate over the last N rounds
      def defection_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.D) / N if N > 0 else 0
  
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return self.match_attributes['length'] is not None and self.match_attributes['length'] - len(self.history) <= 10
  
      # First round: always cooperate
      if self.first_round():
          self.defect_mode = 0  # Tracks if we are in a forced defection mode
          return axl.Action.C
  
      # If in the last 10 rounds, always defect
      if in_last_10_rounds():
          return axl.Action.D
  
      # Every 10 rounds, forgive and play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Check if we are in a forced defection mode
      if self.defect_mode > 0:
          self.defect_mode -= 1
          return axl.Action.D
  
      # Calculate defection rate over the last 50 rounds
      last_50_defection_rate = defection_rate(opponent.history, 50)
  
      # If opponent defected more than 60% in the last 50 rounds, switch to D for 10 rounds
      if last_50_defection_rate > 0.6:
          self.defect_mode = 10
          return axl.Action.D
  
      # If opponent's defection rate is between 5% and 15%, be forgiving and play C
      if 0.05 <= last_50_defection_rate <= 0.15:
          return axl.Action.C
  
      # If after 100 rounds, we are more than 50 points behind, defect for 20 rounds
      if len(self.history) > 100:
          my_score, opponent_score = self.total_scores(self.history[-100:], opponent.history[-100:])
          if opponent_score - my_score > 50:
              self.defect_mode = 20
              return axl.Action.D
  
      # Main strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent cooperated in
# the previous round, cooperate.    - If the opponent defected in the previous
# round, defect.  3. Every 10 rounds, regardless of the opponent's previous
# action:    - If your total score is higher than or equal to the opponent's,
# cooperate.    - If your total score is lower than the opponent's, defect.  4.
# If the opponent has defected for 3 consecutive rounds, defect for the next 2
# rounds regardless of their actions.  5. If you're in the last 50 rounds of the
# game, always defect.  6. Reset to step 1 after every 100 rounds.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      ROUNDS_IN_GAME = 1000
      RESET_INTERVAL = 100
      DEFECT_THRESHOLD = 3
      DEFECT_PENALTY = 2
      LAST_ROUNDS_THRESHOLD = 50
      SCORE_CHECK_INTERVAL = 10
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_penalty_counter = 0
          return COOPERATE
  
      # Check if we are in the last 50 rounds of the game
      if len(self.history) >= ROUNDS_IN_GAME - LAST_ROUNDS_THRESHOLD:
          return DEFECT
  
      # Reset every 100 rounds
      if len(self.history) % RESET_INTERVAL == 0:
          self.consecutive_defections = 0
          self.defect_penalty_counter = 0
          return COOPERATE
  
      # Handle the penalty for opponent defecting 3 times in a row
      if self.defect_penalty_counter > 0:
          self.defect_penalty_counter -= 1
          return DEFECT
  
      # Track consecutive defections by the opponent
      if opponent.history[-1] == DEFECT:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # If opponent defected 3 times in a row, defect for the next 2 rounds
      if self.consecutive_defections >= DEFECT_THRESHOLD:
          self.defect_penalty_counter = DEFECT_PENALTY
          return DEFECT
  
      # Every 10 rounds, compare scores and decide action
      if len(self.history) % SCORE_CHECK_INTERVAL == 0:
          if self.score >= opponent.score:
              return COOPERATE
          else:
              return DEFECT
  
      # Default behavior: mirror the opponent's last action
      if opponent.history[-1] == COOPERATE:
          return COOPERATE
      else:
          return DEFECT



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D with
# 90% probability and C with 10% probability.  4. Every 50 rounds, play C once
# regardless of the opponent's previous move.  5. In the last 10 rounds of the
# game, always play D.  6. If your current score is significantly lower than
# your opponent's (more than 50 points behind), play D for the next 10 rounds
# regardless of the opponent's moves.  7. If you're ahead by more than 100
# points, play C for one round, then revert to the main strategy.  8. Repeat
# these steps for all 1000 rounds, adjusting your play based on the most recent
# round's outcome.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: play D
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are forced to defect
          return axl.Action.D
  
      # Get the current round number
      current_round = len(self.history) + 1
      total_rounds = 1000
  
      # Rule 6: If significantly behind, defect for the next 10 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      if self.score < opponent.score - 50:
          self.defect_streak = 10
          return axl.Action.D
  
      # Rule 7: If ahead by more than 100 points, play C once
      if self.score > opponent.score + 100:
          return axl.Action.C
  
      # Rule 5: In the last 10 rounds, always play D
      if current_round > total_rounds - 10:
          return axl.Action.D
  
      # Rule 4: Every 50 rounds, play C once
      if current_round % 50 == 0:
          return axl.Action.C
  
      # Rule 2 and 3: Based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      elif opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1)  # 10% chance to play C, 90% to play D



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before returning to the main strategy.  5. In the last 10
# rounds of the game, always play D to protect against end-game defection.  6.
# If your score falls below 40% of the maximum possible score at any point,
# switch to always playing D for the remainder of the game.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      MAX_SCORE_PER_ROUND = 5
      COOP_SCORE = 3
      MAX_ROUNDS = 1000
      FORGIVENESS_INTERVAL = 10
      DEFECT_THRESHOLD = 0.6
      DEFECT_PENALTY_ROUNDS = 10
      LAST_ROUNDS = 10
      SCORE_THRESHOLD = 0.4
      SCORE_WINDOW = 50
  
      # First round: always cooperate
      if self.first_round():
          self.penalty_rounds = 0  # Track penalty rounds for defecting opponent
          return axl.Action.C
  
      # If in penalty rounds, always defect
      if self.penalty_rounds > 0:
          self.penalty_rounds -= 1
          return axl.Action.D
  
      # If in the last 10 rounds, always defect
      if len(self.history) >= MAX_ROUNDS - LAST_ROUNDS:
          return axl.Action.D
  
      # Calculate the maximum possible score so far
      max_possible_score = len(self.history) * MAX_SCORE_PER_ROUND
  
      # Check if score has fallen below 40% of the maximum possible score
      if self.score < SCORE_THRESHOLD * max_possible_score:
          return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % FORGIVENESS_INTERVAL == 0:
          return axl.Action.C
  
      # Check if opponent has defected more than 60% in the last 50 rounds
      if len(opponent.history) >= SCORE_WINDOW:
          recent_defections = opponent.history[-SCORE_WINDOW:].count(axl.Action.D)
          if recent_defections / SCORE_WINDOW > DEFECT_THRESHOLD:
              self.penalty_rounds = DEFECT_PENALTY_ROUNDS
              return axl.Action.D
  
      # Main strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - Cooperate if the opponent
# cooperated in the previous round.    - Defect if the opponent defected in the
# previous round.  3. Every 10 rounds, ignore the opponent's last move and
# cooperate.  4. If your score is significantly lower than your opponent's (more
# than 20 points behind) after 100 rounds:    - Increase the frequency of
# defection by defecting twice after each of the opponent's defections.    -
# Return to the base strategy once the score difference is less than 10 points.
# 5. In the last 50 rounds of the game:    - If your score is higher than your
# opponent's, always cooperate.    - If your score is lower, always defect.  6.
# Ignore any single round where the outcome seems inconsistent with the
# opponent's general behavior, as it may be due to the 10% noise factor.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Subfunction to check if we are in the last 50 rounds
      def in_last_50_rounds():
          return len(self.history) >= 950
  
      # Subfunction to check if we are in a "cooperate every 10 rounds" situation
      def cooperate_every_10_rounds():
          return len(self.history) % 10 == 0
  
      # Subfunction to check if we are significantly behind in score
      def significantly_behind():
          return self.score < opponent.score - 20
  
      # Subfunction to check if we are less than 10 points behind
      def less_than_10_points_behind():
          return self.score >= opponent.score - 10
  
      # Subfunction to handle the base strategy
      def base_strategy():
          if len(self.history) == 0:
              return axl.Action.C  # Cooperate in the first round
          elif opponent.history[-1] == axl.Action.C:
              return axl.Action.C  # Cooperate if opponent cooperated last round
          else:
              return axl.Action.D  # Defect if opponent defected last round
  
      # Subfunction to handle the increased defection frequency
      def increased_defection_strategy():
          if len(self.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D  # Defect twice after opponent defects twice
          return base_strategy()
  
      # Subfunction to handle the last 50 rounds strategy
      def last_50_rounds_strategy():
          if self.score > opponent.score:
              return axl.Action.C  # Always cooperate if we are ahead
          else:
              return axl.Action.D  # Always defect if we are behind
  
      # Main strategy logic
      if self.first_round():
          return axl.Action.C  # Cooperate in the first round
  
      if in_last_50_rounds():
          return last_50_rounds_strategy()
  
      if len(self.history) >= 100:
          if significantly_behind():
              return increased_defection_strategy()
          elif less_than_10_points_behind():
              return base_strategy()
  
      if cooperate_every_10_rounds():
          return axl.Action.C  # Cooperate every 10 rounds
  
      return base_strategy()



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, cooperate
# with a 20% probability and defect with an 80% probability.  4. Every 50
# rounds, defect regardless of the opponent's previous action.  5. In the last
# 10 rounds of the game, always defect.  6. If your current score is lower than
# the opponent's score by 20 points or more, always defect until you catch up or
# the game ends.  7. If you're ahead by 50 points or more, cooperate for one
# round, then return to the main strategy.  8. If the opponent has cooperated
# for 5 consecutive rounds, cooperate for one round, then return to the main
# strategy.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to check if the opponent has cooperated for the last 5 rounds
      def opponent_cooperated_last_n_rounds(n):
          return len(opponent.history) >= n and all(action == axl.Action.C for action in opponent.history[-n:])
  
      # First round: always defect
      if self.first_round():
          return axl.Action.D
  
      # Every 50 rounds, defect
      if len(self.history) % 50 == 0:
          return axl.Action.D
  
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # If the opponent defected in the last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent has cooperated for 5 consecutive rounds, cooperate for one round
      if opponent_cooperated_last_n_rounds(5):
          return axl.Action.C
  
      # If you're behind by 20 points or more, always defect
      if self.score < opponent.score - 20:
          return axl.Action.D
  
      # If you're ahead by 50 points or more, cooperate for one round
      if self.score >= opponent.score + 50:
          return axl.Action.C
  
      # If the opponent cooperated in the last round, cooperate with 20% probability, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)
  
      # Default action: defect
      return axl.Action.D



# Here's a simple cooperative strategy for the game:  1. Start by playing C in
# the first round.  2. In subsequent rounds:    - Play C if the opponent played
# C in the previous round.    - Play D if the opponent played D in the previous
# round.  3. Every 50 rounds, play C regardless of the opponent's previous move
# to encourage cooperation.  4. If the opponent has played D for 5 consecutive
# rounds, switch to always playing D for the next 10 rounds before reverting to
# the main strategy.  5. In the last 10 rounds of the game, always play D to
# protect against end-game defection.  6. If your score falls more than 50
# points behind your opponent's at any point, switch to always playing D until
# the score difference is less than 20 points.  7. If noise is suspected (i.e.,
# if the opponent's behavior seems inconsistent), be more forgiving:    - Allow
# up to 2 unexpected D moves before retaliating.    - Return to cooperation
# after a single C move from the opponent.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.retaliation_mode = False    # Track if we are in retaliation mode
          self.retaliation_counter = 0     # Track how long we stay in retaliation mode
          self.unexpected_defections = 0   # Track unexpected defections for noise handling
          return axl.Action.C              # Start by playing C
  
      # Handle retaliation mode (after 5 consecutive defections)
      if self.retaliation_mode:
          self.retaliation_counter += 1
          if self.retaliation_counter >= 10:
              self.retaliation_mode = False  # Exit retaliation mode after 10 rounds
          return axl.Action.D  # Always play D in retaliation mode
  
      # Check if we are in the last 10 rounds of the game
      if len(self.history) >= 990:
          return axl.Action.D  # Always play D in the last 10 rounds
  
      # Check if we are more than 50 points behind the opponent
      if self.score < opponent.score - 50:
          self.behind_mode = True  # Switch to always playing D
      elif self.score >= opponent.score - 20:
          self.behind_mode = False  # Exit behind mode if the score difference is less than 20
  
      if getattr(self, 'behind_mode', False):
          return axl.Action.D  # Always play D if we are in behind mode
  
      # Check for noise (unexpected defections)
      if opponent.history[-1] == axl.Action.D and self.history[-1] == axl.Action.C:
          self.unexpected_defections += 1
      else:
          self.unexpected_defections = 0  # Reset if opponent cooperates
  
      if self.unexpected_defections > 2:
          return axl.Action.D  # Retaliate after 2 unexpected defections
  
      # Return to cooperation after a single C move from the opponent
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Check for 5 consecutive defections by the opponent
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.retaliation_mode = True
          self.retaliation_counter = 0
          return axl.Action.D  # Enter retaliation mode
  
      # Every 50 rounds, play C to encourage cooperation
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Default behavior: mirror the opponent's last move
      return opponent.history[-1]



# Here's a simple strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent cooperated in
# the previous round, cooperate.    - If the opponent defected in the previous
# round, defect with a 70% probability and cooperate with a 30% probability.  3.
# Every 10 rounds, regardless of the opponent's previous action:    - Cooperate
# to test if the opponent is willing to return to mutual cooperation.  4. If the
# opponent has defected for 5 consecutive rounds:    - Switch to always
# defecting for the next 5 rounds before returning to the main strategy.  5. In
# the last 10 rounds of the game:    - Always defect to protect against end-game
# exploitation.  6. Throughout the game, keep track of the overall cooperation
# rate of the opponent:    - If their cooperation rate falls below 40%, increase
# the probability of defection after opponent defection to 90%.    - If their
# cooperation rate rises above 60%, decrease the probability of defection after
# opponent defection to 50%.  7. Adjust for noise by being slightly more
# forgiving:    - If the opponent's action seems inconsistent with their recent
# pattern, assume it might be due to noise and don't change your strategy for
# that single round.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_mode = False
          self.defect_mode_counter = 0
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate opponent's cooperation rate
      def cooperation_rate():
          total_moves = len(opponent.history)
          if total_moves == 0:
              return 1  # Assume full cooperation if no moves yet
          return opponent.history.cooperations / total_moves
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D  # Always defect in the last 10 rounds
  
      # Check if we are in defect mode (after 5 consecutive defections)
      if self.defect_mode:
          self.defect_mode_counter += 1
          if self.defect_mode_counter >= 5:
              self.defect_mode = False  # Exit defect mode after 5 rounds
          return axl.Action.D  # Always defect in defect mode
  
      # Check for 5 consecutive defections by the opponent
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.defect_mode = True
          self.defect_mode_counter = 0
          return axl.Action.D  # Enter defect mode and defect
  
      # Every 10 rounds, cooperate to test for mutual cooperation
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Adjust defection probability based on opponent's cooperation rate
      coop_rate = cooperation_rate()
      if coop_rate < 0.4:
          defect_prob = 0.9
      elif coop_rate > 0.6:
          defect_prob = 0.5
      else:
          defect_prob = 0.7
  
      # If the opponent defected last round, defect with a certain probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(1 - defect_prob)
  
      # Otherwise, cooperate if the opponent cooperated last round
      return axl.Action.C



# Here's a simple aggressive strategy for the given iterated normal-form game:
# 1. Start by defecting (D) in the first round.  2. If the opponent defected in
# the previous round, defect (D) in the current round.  3. If the opponent
# cooperated in the previous round, defect (D) with 80% probability and
# cooperate (C) with 20% probability.  4. If you have defected for 5 consecutive
# rounds, cooperate (C) once, then return to steps 2-4.  5. If your overall
# score is significantly lower than your opponent's (more than 20% difference),
# switch to always defecting (D) for the next 10 rounds, then return to steps
# 2-5.  6. In the last 50 rounds of the game, always defect (D) regardless of
# the opponent's actions.  7. Follow these steps for the entire 1000 rounds,
# adjusting your strategy based on the opponent's most recent action and the
# overall game state.

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
          self.consecutive_defections = 0
          self.always_defect_counter = 0
          return axl.Action.D  # Start by defecting
  
      # If we are in the last 50 rounds, always defect
      if len(self.history) >= 950:
          return axl.Action.D
  
      # If we are in the "always defect" mode, continue defecting for 10 rounds
      if self.always_defect_counter > 0:
          self.always_defect_counter -= 1
          return axl.Action.D
  
      # Check if we have defected for 5 consecutive rounds
      if self.consecutive_defections >= 5:
          self.consecutive_defections = 0  # Reset the counter after cooperating
          return axl.Action.C  # Cooperate once after 5 consecutive defections
  
      # Check if our score is significantly lower than the opponent's
      if self.score < opponent.score * 0.8:
          self.always_defect_counter = 10  # Switch to always defecting for 10 rounds
          return axl.Action.D
  
      # Get the opponent's last action
      last_opponent_action = opponent.history[-1]
  
      # If the opponent defected in the last round, defect
      if last_opponent_action == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D
  
      # If the opponent cooperated in the last round, defect with 80% probability
      if last_opponent_action == axl.Action.C:
          if self._random.random_choice(0.8):
              self.consecutive_defections += 1
              return axl.Action.D
          else:
              self.consecutive_defections = 0  # Reset the counter if we cooperate
              return axl.Action.C



# Here's a simple cooperative strategy for the described game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if your
# opponent played C in the previous round.    - Play D if your opponent played D
# in the previous two consecutive rounds.    - Play C if your opponent played D
# in the previous round but C in the round before that.  3. If your opponent
# defects three times in a row, switch to always playing D for the next 10
# rounds.  4. After those 10 rounds of punishment, return to the strategy
# described in step 2.  5. In the last 10 rounds of the game, always play D
# regardless of the opponent's actions.  6. Throughout the game, keep track of
# the overall cooperation rate of your opponent. If it falls below 40%, switch
# to always playing D for the remainder of the game.  7. If you notice a
# consistent pattern of alternating C and D from your opponent, match their
# pattern but play D when they play C and C when they play D.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_rounds = 0  # Track punishment rounds
          self.always_defect = False  # Track if we are in always defect mode
          self.opponent_cooperation_rate = 0  # Track opponent's cooperation rate
          self.opponent_pattern = []  # Track opponent's last two moves for pattern detection
          return axl.Action.C  # Start by playing C
  
      # Update opponent's cooperation rate
      total_moves = len(opponent.history)
      self.opponent_cooperation_rate = opponent.history.cooperations / total_moves
  
      # If opponent's cooperation rate falls below 40%, switch to always defect
      if self.opponent_cooperation_rate < 0.4:
          self.always_defect = True
  
      # If we are in always defect mode, play D
      if self.always_defect:
          return axl.Action.D
  
      # If we are in punishment mode, continue defecting for 10 rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Check for opponent's pattern of alternating C and D
      if len(opponent.history) >= 2:
          last_two_moves = opponent.history[-2:]
          if last_two_moves == [axl.Action.C, axl.Action.D] or last_two_moves == [axl.Action.D, axl.Action.C]:
              # Match their pattern but invert the actions
              return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # If opponent defected three times in a row, enter punishment mode
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.punishment_rounds = 10
          return axl.Action.D
  
      # In the last 10 rounds of the game, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Follow the main strategy rules
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
      elif len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.D]:
          return axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent cooperated in
# the previous round, cooperate.    - If the opponent defected in the previous
# round, defect.  3. Every 10 rounds, regardless of the opponent's previous
# action:    - If your total score is higher than or equal to the opponent's,
# cooperate.    - If your total score is lower than the opponent's, defect.  4.
# If the opponent has defected for 3 consecutive rounds, defect for the next 2
# rounds regardless of their actions.  5. If you're in the last 50 rounds of the
# game, always defect.  6. Reset to step 1 if there have been 5 consecutive
# rounds where both players' actions were different.

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
          self.consecutive_different_actions = 0
          self.defect_for_next_two = 0
          return axl.Action.C
  
      # Check if we are in the last 50 rounds
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Check if opponent has defected for 3 consecutive rounds
      if opponent.history[-3:] == [axl.Action.D] * 3:
          self.defect_for_next_two = 2
  
      # If we are in the "defect for next two rounds" phase
      if self.defect_for_next_two > 0:
          self.defect_for_next_two -= 1
          return axl.Action.D
  
      # Check if it's every 10th round
      if len(self.history) % 10 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Check if there have been 5 consecutive rounds where actions were different
      if len(self.history) >= 5 and all(self.history[-i] != opponent.history[-i] for i in range(1, 6)):
          self.consecutive_different_actions += 1
      else:
          self.consecutive_different_actions = 0
  
      if self.consecutive_different_actions >= 5:
          self.consecutive_different_actions = 0
          return axl.Action.C
  
      # Follow Tit-for-Tat logic
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous move.  5. In the last 10
# rounds of the game, always defect.  6. If your current score is significantly
# lower than your opponent's (more than 50 points behind), switch to always
# defecting for the next 20 rounds.  7. If you're ahead by more than 100 points,
# cooperate for the next 5 rounds to avoid triggering retaliation.  8. Return to
# step 2 and repeat for each round of the game.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are in "always defect" mode
          self.coop_streak = 0    # Track how many rounds we are in "always cooperate" mode
          return axl.Action.D
  
      # Step 6: If significantly behind, switch to always defecting for 20 rounds
      if self.score < opponent.score - 50:
          self.defect_streak = 20
  
      # Step 7: If ahead by more than 100 points, cooperate for the next 5 rounds
      if self.score > opponent.score + 100:
          self.coop_streak = 5
  
      # Handle defect streak (always defect for 20 rounds)
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Handle coop streak (always cooperate for 5 rounds)
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: Every 50 rounds, cooperate once regardless of the opponent's move
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 2: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If the opponent cooperated in the previous round, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)



# Here's a simple cooperative strategy for the described game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before returning to the main strategy.  5. In the last 10
# rounds of the game, always play D to protect against end-game defection.  6.
# If your score falls more than 100 points behind your opponent's at any point,
# switch to always playing D for the next 20 rounds before returning to the main
# strategy.  7. Ignore any isolated defections, assuming they might be due to
# the 10% noise factor. Only count consecutive defections when considering
# retaliation or forgiveness.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      FORGIVENESS_ROUND_INTERVAL = 10
      DEFECT_THRESHOLD = 0.6
      DEFECT_PENALTY_ROUNDS = 10
      SCORE_DIFFERENCE_THRESHOLD = 100
      SCORE_PENALTY_ROUNDS = 20
      END_GAME_ROUNDS = 10
      LOOKBACK_ROUNDS = 50
      TOTAL_ROUNDS = 1000
  
      # First round: always cooperate
      if self.first_round():
          self.penalty_rounds = 0  # Track penalty rounds for defection
          self.score_penalty_rounds = 0  # Track penalty rounds for score difference
          return axl.Action.C
  
      # Check if we are in penalty rounds due to opponent's defection rate
      if self.penalty_rounds > 0:
          self.penalty_rounds -= 1
          return axl.Action.D
  
      # Check if we are in penalty rounds due to score difference
      if self.score_penalty_rounds > 0:
          self.score_penalty_rounds -= 1
          return axl.Action.D
  
      # End-game strategy: always defect in the last 10 rounds
      if len(self.history) >= TOTAL_ROUNDS - END_GAME_ROUNDS:
          return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % FORGIVENESS_ROUND_INTERVAL == 0:
          return axl.Action.C
  
      # Check if the opponent has defected more than 60% in the last 50 rounds
      if len(opponent.history) >= LOOKBACK_ROUNDS:
          recent_defections = opponent.history[-LOOKBACK_ROUNDS:].count(axl.Action.D)
          if recent_defections / LOOKBACK_ROUNDS > DEFECT_THRESHOLD:
              self.penalty_rounds = DEFECT_PENALTY_ROUNDS
              return axl.Action.D
  
      # Check if we are more than 100 points behind the opponent
      if self.score - opponent.score < -SCORE_DIFFERENCE_THRESHOLD:
          self.score_penalty_rounds = SCORE_PENALTY_ROUNDS
          return axl.Action.D
  
      # Main strategy: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C



# Here's a simple strategy for the described iterated game:  1. Start by
# cooperating in the first round.  2. Keep track of your opponent's actions and
# calculate their cooperation rate.  3. If your opponent's cooperation rate is
# above 70%, cooperate.  4. If your opponent's cooperation rate is below 30%,
# defect.  5. If your opponent's cooperation rate is between 30% and 70%, mirror
# their last move.  6. Every 50 rounds, cooperate regardless of the opponent's
# actions to allow for potential reconciliation.  7. In the last 10 rounds of
# the game, always defect to maximize final payoff.  8. If your overall score
# falls more than 20% below the theoretical average (2 points per round), switch
# to always defecting for the next 20 rounds before reverting to the main
# strategy.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 0.7
      DEFECTION_THRESHOLD = 0.3
      RECONCILIATION_ROUND = 50
      FINAL_ROUNDS = 10
      DEFECT_PENALTY_THRESHOLD = 0.8
      DEFECT_PENALTY_DURATION = 20
      THEORETICAL_AVERAGE_SCORE = 2
  
      # First round: cooperate
      if self.first_round():
          self.defect_penalty_counter = 0  # Initialize penalty counter
          return axl.Action.C
  
      # Calculate opponent's cooperation rate
      total_moves = len(opponent.history)
      if total_moves > 0:
          cooperation_rate = opponent.history.cooperations / total_moves
      else:
          cooperation_rate = 1  # Assume full cooperation if no moves yet
  
      # Check if we are in the penalty phase (always defect for 20 rounds)
      if self.defect_penalty_counter > 0:
          self.defect_penalty_counter -= 1
          return axl.Action.D
  
      # Check if we are in the final 10 rounds
      if total_moves >= 1000 - FINAL_ROUNDS:
          return axl.Action.D
  
      # Every 50 rounds, cooperate for reconciliation
      if total_moves % RECONCILIATION_ROUND == 0:
          return axl.Action.C
  
      # Check if our score is more than 20% below the theoretical average
      expected_score = THEORETICAL_AVERAGE_SCORE * total_moves
      if self.score < DEFECT_PENALTY_THRESHOLD * expected_score:
          self.defect_penalty_counter = DEFECT_PENALTY_DURATION
          return axl.Action.D
  
      # Main strategy based on opponent's cooperation rate
      if cooperation_rate > COOPERATION_THRESHOLD:
          return axl.Action.C
      elif cooperation_rate < DEFECTION_THRESHOLD:
          return axl.Action.D
      else:
          # Mirror opponent's last move
          return opponent.history[-1]



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D with
# 90% probability and C with 10% probability.  4. If you're currently on a
# streak of mutual cooperation (CC) for 3 or more consecutive rounds, play D to
# exploit the opponent.  5. Every 50 rounds, play C once to test if the opponent
# is willing to cooperate.  6. In the last 10 rounds of the game, always play D
# to maximize final payoff.  7. If the opponent has played D for 10 consecutive
# rounds, play C once to attempt breaking the cycle.  8. For all other
# situations not covered by the above rules, play D.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by playing D in the first round.
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: In the last 10 rounds of the game, always play D.
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 7: If the opponent has played D for 10 consecutive rounds, play C once to attempt breaking the cycle.
      if len(opponent.history) >= 10 and all(move == axl.Action.D for move in opponent.history[-10:]):
          return axl.Action.C
  
      # Rule 5: Every 50 rounds, play C once to test if the opponent is willing to cooperate.
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 4: If you're currently on a streak of mutual cooperation (CC) for 3 or more consecutive rounds, play D.
      if len(self.history) >= 3 and all(self.history[-i] == axl.Action.C and opponent.history[-i] == axl.Action.C for i in range(1, 4)):
          return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play D.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D with 90% probability and C with 10% probability.
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1)
  
      # Rule 8: For all other situations not covered by the above rules, play D.
      return axl.Action.D



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before returning to the main strategy.  5. In the last 10
# rounds of the game, always play D to protect against end-game defection.  6.
# If your score falls below 40% of the maximum possible score at any point,
# switch to always playing D for the remainder of the game.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      MAX_SCORE_PER_ROUND = 5
      COOP_SCORE = 3
      MAX_ROUNDS = 1000
      FORGIVE_INTERVAL = 10
      DEFECT_THRESHOLD = 0.6
      DEFECT_PENALTY_ROUNDS = 10
      LAST_ROUNDS = 10
      SCORE_THRESHOLD = 0.4
      SCORE_WINDOW = 50
  
      # First round: always cooperate
      if self.first_round():
          self.defect_penalty_counter = 0  # Track penalty rounds after 60% defection
          return axl.Action.C
  
      # If in penalty mode (after 60% defection), always defect for the next 10 rounds
      if self.defect_penalty_counter > 0:
          self.defect_penalty_counter -= 1
          return axl.Action.D
  
      # If in the last 10 rounds, always defect
      if len(self.history) >= MAX_ROUNDS - LAST_ROUNDS:
          return axl.Action.D
  
      # Check if score is below 40% of the maximum possible score
      max_possible_score = len(self.history) * MAX_SCORE_PER_ROUND
      if max_possible_score > 0 and self.score / max_possible_score < SCORE_THRESHOLD:
          return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % FORGIVE_INTERVAL == 0:
          return axl.Action.C
  
      # Check if opponent has defected more than 60% in the last 50 rounds
      if len(opponent.history) >= SCORE_WINDOW:
          recent_defections = opponent.history[-SCORE_WINDOW:].count(axl.Action.D)
          if recent_defections / SCORE_WINDOW > DEFECT_THRESHOLD:
              self.defect_penalty_counter = DEFECT_PENALTY_ROUNDS
              return axl.Action.D
  
      # Main strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C



# Here's a simple strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent cooperated in
# the previous round, cooperate.    - If the opponent defected in the previous
# round, defect.  3. Every 10 rounds, regardless of the opponent's previous
# action:    - If your total score is higher than or equal to the opponent's,
# cooperate.    - If your total score is lower than the opponent's, defect.  4.
# If you've defected for 3 consecutive rounds, cooperate in the next round.  5.
# In the last 10 rounds of the game, always defect.  6. If at any point your
# score falls behind the opponent's by 20 points or more, defect for the next 5
# rounds before returning to the main strategy.  Follow these rules in the order
# presented, applying the first applicable rule in each round.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.behind_by_20 = False  # Track if behind by 20 points
          self.behind_by_20_rounds = 0  # Track rounds of defecting after falling behind by 20 points
          return axl.Action.C
  
      # Rule 6: If behind by 20 points or more, defect for the next 5 rounds
      if self.behind_by_20:
          self.behind_by_20_rounds += 1
          if self.behind_by_20_rounds <= 5:
              return axl.Action.D
          else:
              self.behind_by_20 = False  # Reset after 5 rounds of defecting
  
      if self.score < opponent.score - 20:
          self.behind_by_20 = True
          self.behind_by_20_rounds = 1
          return axl.Action.D
  
      # Rule 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If defected for 3 consecutive rounds, cooperate
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.C
  
      # Rule 3: Every 10 rounds, compare scores
      if len(self.history) % 10 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 2: Tit-for-tat behavior
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple aggressive strategy for the given iterated normal-form game:
# 1. Start by defecting (D) in the first round.  2. If the opponent defected in
# the previous round, defect in the current round.  3. If the opponent
# cooperated in the previous round, defect with 80% probability and cooperate
# with 20% probability.  4. Every 50 rounds, cooperate once regardless of the
# opponent's previous action.  5. In the last 10 rounds of the game, always
# defect.  6. If your score is significantly lower than your opponent's (more
# than 50 points behind), switch to always defecting for the next 20 rounds.  7.
# If you're ahead by more than 100 points, cooperate for 5 consecutive rounds to
# potentially increase your lead further.  8. Return to the main strategy after
# any temporary changes in steps 6 or 7.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: always defect
      if self.first_round():
          self.temp_defect_rounds = 0  # Track rounds for step 6
          self.temp_coop_rounds = 0    # Track rounds for step 7
          return axl.Action.D
  
      # Step 6: If significantly behind, defect for 20 rounds
      if self.temp_defect_rounds > 0:
          self.temp_defect_rounds -= 1
          return axl.Action.D
  
      # Step 7: If significantly ahead, cooperate for 5 rounds
      if self.temp_coop_rounds > 0:
          self.temp_coop_rounds -= 1
          return axl.Action.C
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 2: If opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If opponent cooperated in the previous round, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)
  
      # Step 6: Check if significantly behind (more than 50 points)
      if self.score < opponent.score - 50:
          self.temp_defect_rounds = 20
          return axl.Action.D
  
      # Step 7: Check if significantly ahead (more than 100 points)
      if self.score > opponent.score + 100:
          self.temp_coop_rounds = 5
          return axl.Action.C
  
      # Default action: defect
      return axl.Action.D



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, forgive any D plays by the
# opponent and play C regardless of their last move.  4. If the opponent has
# played D for 3 consecutive rounds, switch to playing D for the next 3 rounds
# before reverting to the main strategy.  5. In the last 10 rounds of the game,
# always play C to encourage final cooperation.  6. If your own score falls
# below 40% of the maximum possible score at any point, switch to always playing
# D for the remainder of the game.  This strategy aims to promote cooperation
# while protecting against consistent defection, accounting for the possibility
# of noise in action execution.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      MAX_ROUNDS = 1000
      FORGIVENESS_INTERVAL = 10
      CONSECUTIVE_D_THRESHOLD = 3
      DEFECT_PENALTY_ROUNDS = 3
      COOPERATION_SCORE = 3
      DEFECTION_SCORE = 5
      MAX_POSSIBLE_SCORE = MAX_ROUNDS * COOPERATION_SCORE
      SCORE_THRESHOLD = 0.4 * MAX_POSSIBLE_SCORE
      FINAL_ROUNDS = 10
  
      # First round: always cooperate
      if self.first_round():
          self.defect_penalty_counter = 0  # Track penalty rounds after 3 consecutive defections
          return axl.Action.C
  
      # If score falls below 40% of the maximum possible score, always defect
      if self.score < SCORE_THRESHOLD:
          return axl.Action.D
  
      # Last 10 rounds: always cooperate
      if len(self.history) >= MAX_ROUNDS - FINAL_ROUNDS:
          return axl.Action.C
  
      # If in penalty phase (after 3 consecutive defections by opponent), defect for 3 rounds
      if self.defect_penalty_counter > 0:
          self.defect_penalty_counter -= 1
          return axl.Action.D
  
      # Check for 3 consecutive defections by the opponent
      if opponent.history[-CONSECUTIVE_D_THRESHOLD:] == [axl.Action.D] * CONSECUTIVE_D_THRESHOLD:
          self.defect_penalty_counter = DEFECT_PENALTY_ROUNDS - 1  # Start penalty phase
          return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % FORGIVENESS_INTERVAL == 0:
          return axl.Action.C
  
      # Main strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. For subsequent rounds:    - If the opponent cooperated
# in the previous round, cooperate.    - If the opponent defected in the
# previous round, defect.  3. Every 10 rounds, regardless of the opponent's
# previous action:    - If your total score is higher than or equal to your
# opponent's, cooperate.    - If your total score is lower than your opponent's,
# defect.  4. If you've defected for 3 consecutive rounds, cooperate in the next
# round regardless of the opponent's previous action.  5. In the last 10 rounds
# of the game, always defect.  6. If at any point your score falls behind your
# opponent's by 20 points or more, defect for the next 5 rounds before returning
# to the main strategy.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      TOTAL_ROUNDS = 1000
      DEFECT_THRESHOLD = 20
      CONSECUTIVE_DEFECT_LIMIT = 3
      DEFECT_PENALTY_ROUNDS = 5
      FINAL_ROUNDS = 10
      CHECK_ROUND_INTERVAL = 10
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defects = 0
          self.defect_penalty_counter = 0
          return COOPERATE
  
      # Handle the last 10 rounds: always defect
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return DEFECT
  
      # Handle defect penalty if behind by 20 points or more
      if self.defect_penalty_counter > 0:
          self.defect_penalty_counter -= 1
          return DEFECT
  
      # Check if we are behind by 20 points or more
      if self.score <= opponent.score - DEFECT_THRESHOLD:
          self.defect_penalty_counter = DEFECT_PENALTY_ROUNDS - 1
          return DEFECT
  
      # Check if we have defected for 3 consecutive rounds
      if self.consecutive_defects >= CONSECUTIVE_DEFECT_LIMIT:
          self.consecutive_defects = 0  # Reset the counter
          return COOPERATE
  
      # Every 10 rounds, check the score and decide
      if len(self.history) % CHECK_ROUND_INTERVAL == 0:
          if self.score >= opponent.score:
              return COOPERATE
          else:
              return DEFECT
  
      # Main strategy: Tit-for-Tat
      if opponent.history[-1] == COOPERATE:
          action = COOPERATE
      else:
          action = DEFECT
  
      # Track consecutive defections
      if action == DEFECT:
          self.consecutive_defects += 1
      else:
          self.consecutive_defects = 0
  
      return action



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous move.  5. In the last 10
# rounds of the game, always defect.  6. If your current score is significantly
# lower than your opponent's (more than 20 points behind), increase the
# probability of defection to 90% for the next 10 rounds.  7. If you're ahead by
# more than 50 points, cooperate for the next 5 rounds to avoid triggering
# retaliation.  8. If there's a streak of mutual cooperation for more than 10
# rounds, defect once to test the opponent's response.  9. If the opponent seems
# to be using a tit-for-tat strategy (mimicking your previous move), switch to
# alternating between cooperation and defection for the next 10 rounds.  10. In
# case of any doubt or if none of the above conditions are met, default to
# defection.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if opponent is playing Tit-for-Tat
      def is_tit_for_tat():
          if len(self.history) < 2:
              return False
          return all(self.history[i] == opponent.history[i - 1] for i in range(1, len(self.history)))
  
      # First round: always defect
      if self.first_round():
          self.defection_streak = 0  # Track defection streak for condition 6
          self.cooperation_streak = 0  # Track cooperation streak for condition 8
          self.alternating_mode = False  # Track if alternating mode is active for condition 9
          self.alternating_counter = 0  # Counter for alternating mode
          return axl.Action.D
  
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Every 50 rounds: cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Check if we are significantly behind (more than 20 points)
      if self.score < opponent.score - 20:
          self.defection_streak = 10  # Increase defection probability for the next 10 rounds
  
      # Check if we are significantly ahead (more than 50 points)
      if self.score > opponent.score + 50:
          self.cooperation_streak = 5  # Cooperate for the next 5 rounds
  
      # Handle defection streak (condition 6)
      if self.defection_streak > 0:
          self.defection_streak -= 1
          return self._random.random_choice(0.9)
  
      # Handle cooperation streak (condition 7)
      if self.cooperation_streak > 0:
          self.cooperation_streak -= 1
          return axl.Action.C
  
      # Check for mutual cooperation streak (condition 8)
      if len(self.history) >= 10 and self.history[-10:] == [axl.Action.C] * 10 and opponent.history[-10:] == [axl.Action.C] * 10:
          return axl.Action.D
  
      # Check if opponent is playing Tit-for-Tat (condition 9)
      if is_tit_for_tat():
          self.alternating_mode = True
          self.alternating_counter = 10
  
      # Handle alternating mode (condition 9)
      if self.alternating_mode:
          if self.alternating_counter > 0:
              self.alternating_counter -= 1
              return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D
          else:
              self.alternating_mode = False
  
      # Default behavior: defect with 80% probability if opponent cooperated last round
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)
  
      # Otherwise, defect if opponent defected last round
      return axl.Action.D



# Here's a simple cooperative strategy for the given game:  1. Start by playing
# C in the first round.  2. In subsequent rounds:    - Play C if the opponent
# played C in the previous round.    - Play D if the opponent played D in the
# previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before reverting to the main strategy.  5. In the last 10
# rounds of the game, always play D.  6. If your score is significantly lower
# than your opponent's (more than 100 points behind) after 500 rounds, switch to
# always playing D for the remainder of the game.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Subfunction to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 990
  
      # Subfunction to check if we are more than 100 points behind after 500 rounds
      def significantly_behind():
          if len(self.history) >= 500:
              return (opponent.score - self.score) > 100
          return False
  
      # Subfunction to check if opponent defected more than 60% in the last 50 rounds
      def opponent_defected_more_than_60_percent():
          if len(self.history) >= 50:
              last_50_defections = opponent.history[-50:].count(axl.Action.D)
              return last_50_defections / 50 > 0.6
          return False
  
      # Subfunction to check if we are in a forgiveness round (every 10 rounds)
      def forgiveness_round():
          return len(self.history) % 10 == 0
  
      # First round: always cooperate
      if self.first_round():
          self.defect_mode = None  # Initialize defect mode to None
          return axl.Action.C
  
      # If in the last 10 rounds, always play D
      if in_last_10_rounds():
          return axl.Action.D
  
      # If significantly behind after 500 rounds, switch to always defecting
      if significantly_behind():
          return axl.Action.D
  
      # If opponent defected more than 60% in the last 50 rounds, switch to defect mode for 10 rounds
      if opponent_defected_more_than_60_percent():
          if self.defect_mode is None:
              self.defect_mode = 10  # Set defect mode for the next 10 rounds
  
      # If in defect mode, decrement the counter and play D
      if self.defect_mode is not None:
          self.defect_mode -= 1
          if self.defect_mode == 0:
              self.defect_mode = None  # Reset defect mode after 10 rounds
          return axl.Action.D
  
      # Every 10 rounds, forgive and play C
      if forgiveness_round():
          return axl.Action.C
  
      # Otherwise, follow tit-for-tat: play C if opponent played C, else play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent has
# cooperated in the last 3 rounds, cooperate.    - If the opponent has defected
# in the last 3 rounds, defect.    - If the opponent's actions have been mixed
# in the last 3 rounds:      a. If your score is higher than or equal to the
# opponent's, cooperate.      b. If your score is lower than the opponent's,
# defect.  3. Every 50 rounds, regardless of recent history:    - If your
# overall score is higher than the opponent's, cooperate.    - If your overall
# score is lower than the opponent's, defect.  4. In the last 10 rounds of the
# game, always defect.  5. If at any point your score falls behind the
# opponent's by more than 50 points, defect for the next 5 rounds, then return
# to the main strategy.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # First round: Cooperate
      if self.first_round():
          self.defect_streak = 0  # Track defect streak for rule 5
          return axl.Action.C
  
      # Rule 5: If behind by more than 50 points, defect for 5 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
      elif self.score < opponent.score - 50:
          self.defect_streak = 5
          return axl.Action.D
  
      # Rule 4: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 3: Every 50 rounds, compare scores
      if len(self.history) % 50 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 2: Check the last 3 rounds of the opponent
      if len(opponent.history) >= 3:
          last_3_opponent_moves = opponent.history[-3:]
          if last_3_opponent_moves.count(axl.Action.C) == 3:
              return axl.Action.C
          elif last_3_opponent_moves.count(axl.Action.D) == 3:
              return axl.Action.D
          else:
              # Mixed actions: Compare scores
              if self.score >= opponent.score:
                  return axl.Action.C
              else:
                  return axl.Action.D
  
      # Default to cooperate if not enough history
      return axl.Action.C



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous action.  5. In the last
# 10 rounds of the game, always defect.  6. If your current score is
# significantly lower than your opponent's (more than 50 points behind), switch
# to always defecting for the next 20 rounds.  7. If you're ahead by more than
# 100 points, cooperate for the next 5 rounds to avoid appearing too aggressive.
# 8. Return to the main strategy after any temporary changes in steps 6 or 7.

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
          self.temp_defect_rounds = 0  # Tracks rounds of forced defection (step 6)
          self.temp_coop_rounds = 0    # Tracks rounds of forced cooperation (step 7)
          return axl.Action.D  # Step 1: Start by defecting
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 6: If significantly behind, defect for the next 20 rounds
      if self.temp_defect_rounds > 0:
          self.temp_defect_rounds -= 1
          return axl.Action.D
      elif self.score + 50 < opponent.score:
          self.temp_defect_rounds = 20
          return axl.Action.D
  
      # Step 7: If significantly ahead, cooperate for the next 5 rounds
      if self.temp_coop_rounds > 0:
          self.temp_coop_rounds -= 1
          return axl.Action.C
      elif self.score > opponent.score + 100:
          self.temp_coop_rounds = 5
          return axl.Action.C
  
      # Step 4: Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 2 and 3: Main strategy
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Step 2: Defect if opponent defected last round
      else:
          # Step 3: Defect with 80% probability, cooperate with 20% probability
          return self._random.random_choice(0.2)



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before returning to the main strategy.  5. In the last 10
# rounds of the game, always play D to protect against end-game defection.  6.
# If your score falls below 40% of the maximum possible score at any point,
# switch to always playing D for the remainder of the game.  This strategy aims
# to encourage cooperation while protecting against consistent defection and
# accounting for the noisy action environment.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      MAX_SCORE_PER_ROUND = 5
      COOP_SCORE = 3
      MAX_SCORE = MAX_SCORE_PER_ROUND * len(self.history)
      THRESHOLD_SCORE = 0.4 * MAX_SCORE
      FORGIVENESS_ROUND = 10
      DEFECT_THRESHOLD = 0.6
      DEFECT_PENALTY_ROUNDS = 10
      LAST_ROUNDS = 10
      LOOKBACK_ROUNDS = 50
  
      # First round: always cooperate
      if self.first_round():
          self.penalty_rounds = 0  # Track penalty rounds for defection punishment
          return axl.Action.C
  
      # If in penalty rounds, always defect
      if self.penalty_rounds > 0:
          self.penalty_rounds -= 1
          return axl.Action.D
  
      # If in the last 10 rounds, always defect
      if len(self.history) >= 1000 - LAST_ROUNDS:
          return axl.Action.D
  
      # Check if score has fallen below 40% of the maximum possible score
      if self.score < THRESHOLD_SCORE:
          return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % FORGIVENESS_ROUND == 0:
          return axl.Action.C
  
      # Check if opponent has defected more than 60% in the last 50 rounds
      if len(opponent.history) >= LOOKBACK_ROUNDS:
          recent_defections = opponent.history[-LOOKBACK_ROUNDS:].count(axl.Action.D)
          if recent_defections / LOOKBACK_ROUNDS > DEFECT_THRESHOLD:
              self.penalty_rounds = DEFECT_PENALTY_ROUNDS
              return axl.Action.D
  
      # Main strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C



# Here's a simple strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent cooperated in
# the previous round, cooperate.    - If the opponent defected in the previous
# round, defect.  3. Every 10 rounds, regardless of the opponent's previous
# action:    - If your total score is higher than or equal to the opponent's,
# cooperate.    - If your total score is lower than the opponent's, defect.  4.
# If you've defected for 3 consecutive rounds, cooperate in the next round.  5.
# In the last 10 rounds of the game, always defect.  6. If at any point your
# score falls behind the opponent's by 20 points or more, defect for the next 5
# rounds before returning to the main strategy.  Follow these rules in the order
# presented, applying the first applicable rule in each round.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.defect_for_5_rounds = 0  # Track if we need to defect for 5 rounds
          return axl.Action.C
  
      # Rule 6: If score falls behind by 20 or more, defect for 5 rounds
      if self.defect_for_5_rounds > 0:
          self.defect_for_5_rounds -= 1
          return axl.Action.D
      elif self.score < opponent.score - 20:
          self.defect_for_5_rounds = 5
          return axl.Action.D
  
      # Rule 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If defected for 3 consecutive rounds, cooperate
      if self.consecutive_defections >= 3:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Rule 3: Every 10 rounds, check scores and decide
      if len(self.history) % 10 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 2: Tit-for-tat behavior
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D
      else:
          self.consecutive_defections = 0
          return axl.Action.C



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect in the next round.  3. If the opponent cooperated in the
# previous round, defect with an 80% probability and cooperate with a 20%
# probability in the next round.  4. Every 50 rounds, cooperate for one round
# regardless of the opponent's previous action.  5. In the last 10 rounds of the
# game, always defect.  6. If your current score is significantly lower than
# your opponent's (more than 50 points behind), switch to always defecting for
# the next 20 rounds before returning to the main strategy.  7. If you're ahead
# by more than 100 points, cooperate for the next 5 rounds before returning to
# the main strategy.  8. If there's a streak of mutual cooperation for more than
# 10 rounds, defect in the next round to test the opponent's response.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we've been defecting due to score difference
          self.coop_streak = 0    # Track mutual cooperation streak
          return axl.Action.D      # Start by defecting
  
      # Get the current round number
      round_number = len(self.history)
  
      # Rule 5: In the last 10 rounds, always defect
      if round_number >= 990:
          return axl.Action.D
  
      # Rule 6: If significantly behind, defect for 20 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
      elif self.score < opponent.score - 50:
          self.defect_streak = 20
          return axl.Action.D
  
      # Rule 7: If ahead by more than 100 points, cooperate for 5 rounds
      if self.score > opponent.score + 100:
          if round_number % 5 != 0:  # Cooperate for 5 rounds
              return axl.Action.C
  
      # Rule 8: If mutual cooperation streak > 10, defect to test opponent
      if self.coop_streak > 10:
          self.coop_streak = 0  # Reset streak after testing
          return axl.Action.D
  
      # Rule 4: Every 50 rounds, cooperate for one round
      if round_number % 50 == 0:
          return axl.Action.C
  
      # Rule 2 and 3: Respond based on opponent's last action
      if opponent.history[-1] == axl.Action.D:
          self.coop_streak = 0  # Reset cooperation streak
          return axl.Action.D
      else:
          self.coop_streak += 1  # Increment cooperation streak
          return self._random.random_choice(0.2)  # 80% defect, 20% cooperate



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any previous defection and
# play C regardless of the opponent's last move.  4. If the opponent has
# defected more than 60% of the time in the last 50 rounds, switch to always
# playing D for the next 10 rounds before reverting to the main strategy.  5. In
# the last 10 rounds of the game, always play D to protect against end-game
# defection.  6. Throughout the game, if you notice a consistent pattern of the
# opponent alternating between C and D, match their pattern by playing D when
# you expect them to play C, and C when you expect them to play D.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to detect alternating pattern
      def is_alternating(history):
          if len(history) < 4:
              return False
          return all(history[i] != history[i + 1] for i in range(len(history) - 1))
  
      # First round: always cooperate
      if self.first_round():
          self.defection_streak = 0  # Track defection streaks
          self.alternating_detected = False  # Track if alternating pattern is detected
          return axl.Action.C
  
      # Check for alternating pattern
      if not self.alternating_detected and is_alternating(opponent.history):
          self.alternating_detected = True
  
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # If opponent has defected more than 60% in the last 50 rounds, defect for 10 rounds
      if len(opponent.history) >= 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.6:
              if self.defection_streak < 10:
                  self.defection_streak += 1
                  return axl.Action.D
              else:
                  self.defection_streak = 0  # Reset after 10 rounds of defection
  
      # If alternating pattern is detected, play the opposite of the expected move
      if self.alternating_detected:
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Default behavior: mirror opponent's last move
      return opponent.history[-1]



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. Keep track of your opponent's actions and your own
# actions throughout the game.  3. Cooperate if your opponent has cooperated in
# the majority of the last 10 rounds.  4. Defect if your opponent has defected
# in the majority of the last 10 rounds.  5. If there's an equal number of
# cooperations and defections in the last 10 rounds, cooperate.  6. Ignore any
# streaks of 3 or fewer unexpected actions, as these may be due to noise.  7. If
# you notice a sudden change in your opponent's behavior lasting more than 3
# rounds, adapt your strategy accordingly.  8. In the last 10 rounds of the
# game, always defect to maximize your final score.  9. If at any point your
# average score per round falls below 1.5, switch to always defecting for the
# next 20 rounds, then return to the main strategy.  10. Reassess your strategy
# every 100 rounds and adjust if necessary based on your opponent's overall
# behavior.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      ROUNDS_TO_CHECK = 10
      DEFECT_THRESHOLD = 1.5
      DEFECT_PERIOD = 20
      REASSESS_PERIOD = 100
      FINAL_ROUNDS = 10
      STREAK_THRESHOLD = 3
  
      # First round: cooperate
      if self.first_round():
          self.defect_mode = False  # Track if we are in defect mode due to low score
          self.defect_mode_counter = 0  # Counter for defect mode duration
          return COOPERATE
  
      # If in defect mode, defect for the next 20 rounds
      if self.defect_mode:
          self.defect_mode_counter += 1
          if self.defect_mode_counter >= DEFECT_PERIOD:
              self.defect_mode = False  # Exit defect mode after 20 rounds
          return DEFECT
  
      # Check if we are in the last 10 rounds of the game
      if len(self.history) >= 1000 - FINAL_ROUNDS:
          return DEFECT
  
      # Check if the average score per round has fallen below 1.5
      if len(self.history) > 0:
          average_score = self.score / len(self.history)
          if average_score < DEFECT_THRESHOLD:
              self.defect_mode = True
              self.defect_mode_counter = 0
              return DEFECT
  
      # Get the last 10 rounds of opponent's actions
      recent_opponent_actions = opponent.history[-ROUNDS_TO_CHECK:]
  
      # If there are fewer than 10 rounds, just cooperate
      if len(recent_opponent_actions) < ROUNDS_TO_CHECK:
          return COOPERATE
  
      # Count the number of cooperations and defections in the last 10 rounds
      cooperations = recent_opponent_actions.count(COOPERATE)
      defections = recent_opponent_actions.count(DEFECT)
  
      # Ignore streaks of 3 or fewer unexpected actions
      if len(set(recent_opponent_actions[-STREAK_THRESHOLD:])) == 1:
          # If the last 3 actions are the same, consider it a streak and ignore it
          return COOPERATE
  
      # Cooperate if the opponent cooperated in the majority of the last 10 rounds
      if cooperations > defections:
          return COOPERATE
  
      # Defect if the opponent defected in the majority of the last 10 rounds
      if defections > cooperations:
          return DEFECT
  
      # If there's an equal number of cooperations and defections, cooperate
      return COOPERATE



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous move.  5. In the last 10
# rounds of the game, always defect.  6. If your current score is significantly
# lower than your opponent's (more than 50 points behind), switch to always
# defecting for the next 20 rounds.  7. If you're ahead by more than 100 points,
# cooperate for the next 5 rounds to avoid appearing too aggressive.  8. Return
# to the main strategy after any temporary changes in steps 6 or 7.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always defect
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are in a defect streak (step 6)
          self.coop_streak = 0    # Track how many rounds we are in a cooperation streak (step 7)
          return axl.Action.D
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 6: If significantly behind, switch to always defecting for 20 rounds
      if self.score < opponent.score - 50:
          if self.defect_streak < 20:
              self.defect_streak += 1
              return axl.Action.D
          else:
              self.defect_streak = 0  # Reset after 20 rounds of defecting
  
      # Step 7: If ahead by more than 100 points, cooperate for the next 5 rounds
      if self.score > opponent.score + 100:
          if self.coop_streak < 5:
              self.coop_streak += 1
              return axl.Action.C
          else:
              self.coop_streak = 0  # Reset after 5 rounds of cooperating
  
      # Step 4: Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 2 and 3: Main strategy
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Defect if opponent defected last round
      else:
          # Defect with 80% probability, cooperate with 20% probability
          return self._random.random_choice(0.2)



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous two consecutive rounds.    - Play C if the opponent played D
# in the previous round but C in the round before that.  3. Every 50 rounds,
# play C regardless of the opponent's previous actions to encourage cooperation.
# 4. If your score is significantly lower than your opponent's (more than 50
# points difference) after 250 rounds, switch to always playing D for the next
# 50 rounds, then return to the main strategy.  5. In the last 10 rounds of the
# game, always play D to protect against end-game defection.  6. Ignore single
# instances of defection, attributing them to the 10% noise factor.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 990
  
      # Helper function to check if we are in the next 50 rounds after 250 rounds
      def in_next_50_rounds_after_250():
          return 250 <= len(self.history) < 300
  
      # Helper function to check if the score difference is significant
      def significant_score_difference():
          return (opponent.score - self.score) > 50
  
      # First round: always play C
      if self.first_round():
          return axl.Action.C
  
      # Last 10 rounds: always play D
      if in_last_10_rounds():
          return axl.Action.D
  
      # After 250 rounds, if the score difference is significant, play D for the next 50 rounds
      if len(self.history) >= 250 and significant_score_difference() and in_next_50_rounds_after_250():
          return axl.Action.D
  
      # Every 50 rounds, play C to encourage cooperation
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Main strategy logic
      if len(opponent.history) >= 2:
          # Play D if the opponent played D in the last two consecutive rounds
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          # Play C if the opponent played D in the previous round but C in the round before that
          elif opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
      # Play C if the opponent played C in the previous round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Default to playing C if none of the above conditions are met
      return axl.Action.C



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent has
# cooperated in the last 3 rounds, cooperate.    - If the opponent has defected
# in the last 3 rounds, defect.    - If the opponent's actions have been mixed
# in the last 3 rounds:      a. If you've scored more points than the opponent
# overall, cooperate.      b. If you've scored fewer points than the opponent
# overall, defect.      c. If scores are tied, randomly choose to cooperate or
# defect with equal probability.  3. Every 50 rounds, regardless of recent
# history:    - If your overall score is higher than your opponent's, cooperate.
# - If your overall score is lower than your opponent's, defect.    - If scores
# are tied, continue with the strategy from point 2.  4. In the last 10 rounds
# of the game, always defect.  5. If at any point you notice a consistent
# pattern in your opponent's play (e.g., always cooperating, alternating, etc.),
# adjust your strategy to exploit it while being cautious of potential noise-
# induced errors.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if opponent has cooperated or defected in the last 3 rounds
      def last_three_rounds():
          if len(opponent.history) < 3:
              return None  # Not enough history to make a decision based on last 3 rounds
          last_three = opponent.history[-3:]
          if last_three.count(axl.Action.C) == 3:
              return axl.Action.C  # Opponent cooperated in the last 3 rounds
          elif last_three.count(axl.Action.D) == 3:
              return axl.Action.D  # Opponent defected in the last 3 rounds
          else:
              return "mixed"  # Mixed actions in the last 3 rounds
  
      # Helper function to compare scores
      def compare_scores():
          if self.score > opponent.score:
              return axl.Action.C  # Cooperate if you're ahead
          elif self.score < opponent.score:
              return axl.Action.D  # Defect if you're behind
          else:
              # Random choice if scores are tied
              return self._random.random_choice(0.5)
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Every 50 rounds, compare scores and act accordingly
      if len(self.history) % 50 == 0:
          return compare_scores()
  
      # Check the last 3 rounds of the opponent
      last_three = last_three_rounds()
      if last_three == axl.Action.C:
          return axl.Action.C  # Cooperate if opponent cooperated in the last 3 rounds
      elif last_three == axl.Action.D:
          return axl.Action.D  # Defect if opponent defected in the last 3 rounds
      elif last_three == "mixed":
          # Mixed actions in the last 3 rounds, compare scores
          return compare_scores()
  
      # Default action (should not reach here)
      return axl.Action.C



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, always defect in the next round.  3. If the opponent cooperated in the
# previous round, defect with 80% probability and cooperate with 20% probability
# in the next round.  4. If you've defected for 5 consecutive rounds and the
# opponent has cooperated for all of those rounds, cooperate in the next round.
# 5. In the last 10 rounds of the game, always defect regardless of the
# opponent's actions.  6. If at any point your cumulative score falls behind the
# opponent's by 20 points or more, switch to always defecting for the next 10
# rounds before reverting to the main strategy.  7. Repeat steps 2-6 for the
# duration of the game, adjusting as necessary for the final rounds as per step
# 5.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_opponent_cooperations = 0
          self.always_defect_counter = 0
          return axl.Action.D  # Start by defecting
  
      # Step 6: If behind by 20 points or more, switch to always defecting for 10 rounds
      if self.always_defect_counter > 0:
          self.always_defect_counter -= 1
          return axl.Action.D
  
      if self.score < opponent.score - 20:
          self.always_defect_counter = 10
          return axl.Action.D
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: If defected for 5 consecutive rounds and opponent cooperated in all of them, cooperate
      if self.consecutive_defections >= 5 and self.consecutive_opponent_cooperations == 5:
          self.consecutive_defections = 0
          self.consecutive_opponent_cooperations = 0
          return axl.Action.C
  
      # Step 2 and 3: Respond based on opponent's last action
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          self.consecutive_opponent_cooperations = 0
          return axl.Action.D
      else:
          self.consecutive_opponent_cooperations += 1
          self.consecutive_defections = 0
          # Defect with 80% probability, cooperate with 20% probability
          return self._random.random_choice(0.2)



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's previous move.  4. If the opponent has defected
# more than 60% of the time in the last 50 rounds, switch to always playing D
# for the next 10 rounds before reverting to the main strategy.  5. In the last
# 10 rounds of the game, always play D.  6. If your score is significantly lower
# than your opponent's (more than 100 points difference) after 500 rounds,
# switch to always playing D for the remainder of the game.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          self.defection_streak = 0  # Track defection streaks
          self.punishment_rounds = 0  # Track rounds of punishment
          return axl.Action.C
  
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # If score difference is more than 100 after 500 rounds, always defect
      if len(self.history) > 500 and (opponent.score - self.score) > 100:
          return axl.Action.D
  
      # If in punishment mode, always defect for 10 rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Check if opponent has defected more than 60% in the last 50 rounds
      if len(self.history) >= 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.6:
              self.punishment_rounds = 10  # Enter punishment mode for 10 rounds
              return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Main strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C



# Here's a simple strategy for the iterated game described:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - Cooperate if
# the opponent cooperated in the previous round.    - Defect if the opponent
# defected in the previous round.  3. Every 10 rounds, regardless of the
# opponent's previous action:    - Cooperate to test if the opponent is willing
# to restore cooperation.  4. If the opponent has defected for 5 consecutive
# rounds:    - Switch to always defecting for the next 10 rounds.    - After 10
# rounds of defection, return to the base strategy (points 2 and 3).  5. In the
# last 10 rounds of the game:    - Always defect to protect against end-game
# exploitation.  6. Throughout the game, keep a running score of your total
# points:    - If your score is significantly lower than expected (more than 20%
# below the average possible score), switch to always defecting for 20 rounds
# before returning to the base strategy.  7. Remember that actions are noisy:
# - Don't overreact to a single defection, as it might be due to noise.    - If
# an opponent's action seems inconsistent with their recent behavior, assume it
# might be noise and stick to your current strategy for one more round.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_mode = 0
          self.total_rounds = 1000
          self.last_10_rounds_defect = False
          return axl.Action.C
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= self.total_rounds - 10:
          self.last_10_rounds_defect = True
  
      # Always defect in the last 10 rounds
      if self.last_10_rounds_defect:
          return axl.Action.D
  
      # Check if we are in defect mode (after 5 consecutive defections)
      if self.defect_mode > 0:
          self.defect_mode -= 1
          if self.defect_mode == 0:
              self.consecutive_defections = 0  # Reset after defect mode ends
          return axl.Action.D
  
      # Check if the opponent has defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.defect_mode = 10  # Switch to defect mode for 10 rounds
          return axl.Action.D
  
      # Every 10 rounds, cooperate to test for cooperation restoration
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Check if our score is significantly lower than expected
      expected_score = len(self.history) * 3  # Average score if both cooperate
      if self.score < 0.8 * expected_score:
          self.defect_mode = 20  # Switch to defect mode for 20 rounds
          return axl.Action.D
  
      # Cooperate if the opponent cooperated in the last round, otherwise defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D with
# 90% probability and C with 10% probability.  4. If you're currently on a
# streak of mutual cooperation (CC) for 3 or more consecutive rounds, play D to
# exploit the opponent.  5. Every 50 rounds, play C regardless of the opponent's
# previous move, to probe for potential cooperation.  6. In the last 10 rounds
# of the game, always play D to maximize final payoffs.  7. If the opponent has
# played D for 10 consecutive rounds, play C once to test if they might switch
# to cooperation.  8. For all other situations not covered by the above rules,
# play D.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by playing D in the first round.
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: In the last 10 rounds of the game, always play D.
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 7: If the opponent has played D for 10 consecutive rounds, play C once to test.
      if len(opponent.history) >= 10 and opponent.history[-10:] == [axl.Action.D] * 10:
          return axl.Action.C
  
      # Rule 5: Every 50 rounds, play C to probe for cooperation.
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 4: If on a streak of mutual cooperation (CC) for 3 or more rounds, play D.
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.C] * 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play D.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D with 90% probability, C with 10%.
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1)
  
      # Rule 8: For all other situations, play D.
      return axl.Action.D



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before reverting to the main strategy.  5. In the last 10
# rounds of the game, always play D to protect against end-game defection.  6.
# Ignore any isolated defections, treating them as potential noise. Only respond
# to defection if the opponent defects twice in a row.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          self.defection_streak = 0  # Track consecutive defections
          self.punishment_mode = False  # Track if we're in punishment mode
          self.punishment_counter = 0  # Track how many rounds of punishment are left
          return axl.Action.C
  
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if we are in punishment mode
      if self.punishment_mode:
          self.punishment_counter -= 1
          if self.punishment_counter <= 0:
              self.punishment_mode = False  # End punishment mode after 10 rounds
          return axl.Action.D
  
      # Check if opponent has defected more than 60% in the last 50 rounds
      if len(self.history) >= 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.6:
              self.punishment_mode = True
              self.punishment_counter = 10
              return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Respond to opponent's last move
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D  # Respond to two consecutive defections
      elif opponent.history[-1] == axl.Action.C:
          return axl.Action.C  # Cooperate if opponent cooperated last round
      else:
          return axl.Action.D  # Defect if opponent defected last round



# Here's a simple strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent cooperated in the previous round, cooperate.    - If the opponent
# defected in the previous round, defect.  3. Every 10 rounds, regardless of the
# opponent's previous action:    - If your total score is higher than or equal
# to the opponent's, cooperate.    - If your total score is lower than the
# opponent's, defect.  4. If you've defected for 3 consecutive rounds, cooperate
# in the next round regardless of the opponent's previous action.  5. In the
# last 10 rounds of the game, always defect.  6. If at any point your score
# falls behind the opponent's by 20 points or more, defect for the next 5 rounds
# before returning to the main strategy.  7. If you notice a clear pattern in
# the opponent's play (e.g., always cooperating or alternating), adjust your
# strategy to exploit it for 5 rounds before returning to the main strategy.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      ROUNDS_TO_DEFECT_IF_BEHIND = 5
      DEFECT_THRESHOLD = 20
      LAST_ROUNDS_TO_DEFECT = 10
      CONSECUTIVE_DEFECTS_TO_COOPERATE = 3
      CHECK_ROUND_INTERVAL = 10
      TOTAL_ROUNDS = 1000
  
      # First round: Cooperate
      if self.first_round():
          self.consecutive_defects = 0  # Track consecutive defections
          self.defect_for_n_rounds = 0  # Track forced defections due to score difference
          return COOPERATE
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= TOTAL_ROUNDS - LAST_ROUNDS_TO_DEFECT:
          return DEFECT
  
      # If we are forced to defect for N rounds due to score difference
      if self.defect_for_n_rounds > 0:
          self.defect_for_n_rounds -= 1
          return DEFECT
  
      # Check if we have defected for 3 consecutive rounds
      if self.history[-CONSECUTIVE_DEFECTS_TO_COOPERATE:].count(DEFECT) == CONSECUTIVE_DEFECTS_TO_COOPERATE:
          return COOPERATE
  
      # Every 10 rounds, check the score difference
      if len(self.history) % CHECK_ROUND_INTERVAL == 0:
          if self.score >= opponent.score:
              return COOPERATE
          else:
              return DEFECT
  
      # Check if we are behind by 20 points or more
      if self.score < opponent.score - DEFECT_THRESHOLD:
          self.defect_for_n_rounds = ROUNDS_TO_DEFECT_IF_BEHIND - 1  # Set to defect for the next 5 rounds
          return DEFECT
  
      # Main strategy: Tit-for-tat
      if opponent.history[-1] == COOPERATE:
          return COOPERATE
      else:
          return DEFECT



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous action.  5. In the last
# 10 rounds of the game, always defect.  6. If your current score is
# significantly lower than your opponent's (more than 20 points behind), switch
# to always defecting for the next 10 rounds.  7. If you've defected for 5
# consecutive rounds and your opponent has cooperated in all of them, cooperate
# once.  8. After cooperating, immediately return to defecting in the next
# round.  9. If both you and your opponent have cooperated for 3 consecutive
# rounds, defect in the next round.  10. In all other situations not covered by
# the above rules, defect.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by defecting in the first round
      if self.first_round():
          self.defect_for_10_rounds = None
          self.consecutive_defections = 0  # Track consecutive defections
          self.cooperated_after_5_defects = False  # Track cooperation after 5 defections
          return axl.Action.D
  
      # Rule 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 6: If your score is significantly lower than your opponent's, switch to always defecting for 10 rounds
      if self.score < opponent.score - 20:
          if not self.defect_for_10_rounds:
              self.defect_for_10_rounds = 10  # Start defecting for 10 rounds
          if self.defect_for_10_rounds > 0:
              self.defect_for_10_rounds -= 1
              return axl.Action.D
      else:
          self.defect_for_10_rounds = None  # Reset if no longer behind by 20 points
  
      # Rule 4: Every 50 rounds, cooperate once regardless of the opponent's previous action
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 7: If you've defected for 5 consecutive rounds and opponent cooperated in all of them, cooperate once
      if self.consecutive_defections >= 5 and opponent.history[-5:].count(axl.Action.C) == 5:
          self.consecutive_defections = 0  # Reset consecutive defections
          self.cooperated_after_5_defects = True
          return axl.Action.C
  
      # Rule 9: If both you and your opponent have cooperated for 3 consecutive rounds, defect in the next round
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.C] * 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.D
  
      # Rule 2: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 3: If the opponent cooperated in the previous round, defect with 80% probability, cooperate with 20%
      if opponent.history[-1] == axl.Action.C:
          if self._random.random_choice(0.2):
              return axl.Action.C
          return axl.Action.D
  
      # Rule 8: After cooperating, immediately return to defecting in the next round
      if self.cooperated_after_5_defects:
          self.cooperated_after_5_defects = False
          return axl.Action.D
  
      # Default: Defect in all other situations
      return axl.Action.D



# Here's a simple cooperative strategy for the described game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive the opponent's last
# defection (if any) and play C regardless of their previous move.  4. If the
# opponent has defected more than 60% of the time in the last 20 rounds, switch
# to always playing D for the next 10 rounds.  5. After playing D for 10 rounds
# due to rule 4, return to the base strategy (rules 2 and 3).  6. In the last 10
# rounds of the game, always play D to protect against end-game defection.  7.
# If your score is significantly lower than expected (more than 30% below the
# average cooperative score) after 100 rounds, switch to always playing D for
# the remainder of the game.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      COOPERATIVE_SCORE = 3  # Expected score for mutual cooperation
      TOTAL_ROUNDS = 1000
      FORGIVENESS_INTERVAL = 10
      DEFECT_THRESHOLD = 0.6
      DEFECT_PENALTY_ROUNDS = 10
      SCORE_THRESHOLD = 0.7  # 30% below cooperative score
  
      # First round: always cooperate
      if self.first_round():
          self.penalty_rounds = 0  # Track penalty rounds due to rule 4
          return COOPERATE
  
      # Rule 6: In the last 10 rounds, always defect
      if len(self.history) >= TOTAL_ROUNDS - 10:
          return DEFECT
  
      # Rule 7: If score is significantly lower than expected after 100 rounds, always defect
      if len(self.history) >= 100:
          expected_score = COOPERATIVE_SCORE * len(self.history)
          if self.score < SCORE_THRESHOLD * expected_score:
              return DEFECT
  
      # Rule 4: If opponent defected more than 60% in the last 20 rounds, switch to D for 10 rounds
      if self.penalty_rounds > 0:
          self.penalty_rounds -= 1
          return DEFECT
      elif len(self.history) >= 20:
          recent_defections = opponent.history[-20:].count(DEFECT)
          if recent_defections / 20 > DEFECT_THRESHOLD:
              self.penalty_rounds = DEFECT_PENALTY_ROUNDS - 1  # Start penalty rounds
              return DEFECT
  
      # Rule 3: Every 10 rounds, forgive and play C
      if len(self.history) % FORGIVENESS_INTERVAL == 0:
          return COOPERATE
  
      # Rule 2: Base strategy - Tit for Tat
      if opponent.history[-1] == COOPERATE:
          return COOPERATE
      else:
          return DEFECT



# Here's a simple strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - Cooperate if the opponent
# cooperated in the previous round.    - Defect if the opponent defected in the
# previous round.  3. Every 10 rounds, regardless of the opponent's last move:
# - Cooperate to potentially reset a cycle of mutual defection.  4. If you've
# defected for 3 consecutive rounds:    - Cooperate in the next round to break
# potential deadlock.  5. If your average score over the last 50 rounds falls
# below 2:    - Increase defection frequency by defecting every other round for
# the next 20 rounds.  6. If your opponent has cooperated for 5 consecutive
# rounds:    - Cooperate for the next 2 rounds, regardless of their actions.  7.
# In the last 10 rounds of the game:    - Always defect to maximize final
# payoff.  Follow these rules in the order presented, applying the first
# applicable condition in each round.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      ROUNDS_TO_CHECK = 50
      DEFECT_STREAK = 3
      COOP_STREAK = 5
      DEFECT_FREQUENCY_ROUNDS = 20
      LAST_ROUNDS = 10
      RESET_ROUND_INTERVAL = 10
  
      # First round: Cooperate
      if self.first_round():
          self.defect_streak = 0
          self.defect_frequency_mode = False
          self.defect_frequency_counter = 0
          return COOPERATE
  
      # 1. Cooperate if opponent cooperated last round, defect if they defected
      if opponent.history[-1] == COOPERATE:
          action = COOPERATE
      else:
          action = DEFECT
  
      # 2. Every 10 rounds, cooperate to reset potential mutual defection
      if len(self.history) % RESET_ROUND_INTERVAL == 0:
          action = COOPERATE
  
      # 3. If defected for 3 consecutive rounds, cooperate to break deadlock
      if self.history[-DEFECT_STREAK:] == [DEFECT] * DEFECT_STREAK:
          action = COOPERATE
  
      # 4. If average score over last 50 rounds is below 2, increase defection frequency
      if len(self.history) >= ROUNDS_TO_CHECK:
          my_score, _ = self.total_scores(self.history[-ROUNDS_TO_CHECK:], opponent.history[-ROUNDS_TO_CHECK:])
          avg_score = my_score / ROUNDS_TO_CHECK
          if avg_score < 2 and not self.defect_frequency_mode:
              self.defect_frequency_mode = True
              self.defect_frequency_counter = DEFECT_FREQUENCY_ROUNDS
  
      if self.defect_frequency_mode:
          if self.defect_frequency_counter > 0:
              self.defect_frequency_counter -= 1
              if self.defect_frequency_counter % 2 == 0:
                  action = DEFECT
          else:
              self.defect_frequency_mode = False
  
      # 5. If opponent cooperated for 5 consecutive rounds, cooperate for next 2 rounds
      if opponent.history[-COOP_STREAK:] == [COOPERATE] * COOP_STREAK:
          if len(self.history) < len(opponent.history) + 2:
              action = COOPERATE
  
      # 6. In the last 10 rounds, always defect
      if len(self.history) >= 1000 - LAST_ROUNDS:
          action = DEFECT
  
      # Update defect streak counter
      if action == DEFECT:
          self.defect_streak += 1
      else:
          self.defect_streak = 0
  
      return action



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect (D) in the current round.  3. If the opponent cooperated in the
# previous round, defect (D) with 80% probability and cooperate (C) with 20%
# probability.  4. Every 50 rounds, cooperate (C) once, regardless of the
# opponent's previous move.  5. If your current score is significantly lower
# than your opponent's (more than 20 points behind), switch to always defecting
# (D) for the next 10 rounds.  6. In the last 50 rounds of the game, always
# defect (D) regardless of the opponent's moves.  7. If none of the above
# conditions are met, defect (D).

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always defect
      if self.first_round():
          self.defect_mode = False  # Initialize defect mode for score difference
          self.defect_mode_counter = 0  # Counter for defect mode duration
          return axl.Action.D
  
      # Last 50 rounds: Always defect
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Check if we are in defect mode (due to score difference)
      if self.defect_mode:
          self.defect_mode_counter += 1
          if self.defect_mode_counter <= 10:
              return axl.Action.D
          else:
              self.defect_mode = False  # Reset defect mode after 10 rounds
  
      # Every 50 rounds: Cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Check if our score is significantly lower than the opponent's
      if self.score < opponent.score - 20:
          self.defect_mode = True
          self.defect_mode_counter = 1
          return axl.Action.D
  
      # If opponent defected last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If opponent cooperated last round, defect with 80% probability, cooperate with 20% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)
  
      # Default action: Defect
      return axl.Action.D



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play C if you played D in the
# previous round (to correct for potential noise).    - Play D if the opponent
# has played D twice in a row.  3. If you've played D due to condition 2c,
# return to playing C in the next round unless the opponent plays D again.  4.
# If the opponent seems to be consistently defecting (playing D more than 70% of
# the time over the last 20 rounds), switch to always playing D for the next 10
# rounds, then return to step 2.  5. In the last 10 rounds of the game, always
# play D to protect against end-game defection.  6. Throughout the game, keep
# track of the overall cooperation rate. If it falls below 50% for an extended
# period (e.g., 100 rounds), consider switching to an always-defect strategy for
# the remainder of the game.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0  # Track consecutive defections by opponent
          self.defect_mode = False  # Track if we are in defect mode
          self.defect_mode_counter = 0  # Counter for defect mode duration
          return axl.Action.C  # Start by cooperating
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 1
  
      # Step 5: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: If opponent defects more than 70% of the time in the last 20 rounds, switch to D for 10 rounds
      if not self.defect_mode and len(opponent.history) >= 20:
          if cooperation_rate(opponent.history, 20) < 0.3:
              self.defect_mode = True
              self.defect_mode_counter = 10
  
      # If in defect mode, play D for the next 10 rounds
      if self.defect_mode:
          self.defect_mode_counter -= 1
          if self.defect_mode_counter == 0:
              self.defect_mode = False  # Exit defect mode after 10 rounds
          return axl.Action.D
  
      # Step 6: If overall cooperation rate falls below 50% for 100 rounds, switch to always defect
      if len(self.history) >= 100 and cooperation_rate(opponent.history, 100) < 0.5:
          return axl.Action.D
  
      # Step 2: Play C if opponent played C in the previous round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 2: Play C if we played D in the previous round (to correct for noise)
      if self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Step 2: Play D if opponent has played D twice in a row
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # Default to cooperation
      return axl.Action.C



# Here's a simple strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:     a. If the opponent has
# cooperated in the last 3 rounds, cooperate.        b. If the opponent has
# defected in the last 3 rounds, defect.        c. If the opponent's actions
# have been mixed in the last 3 rounds:       - Cooperate if you've defected
# more times than your opponent over the entire game so far.       - Defect if
# your opponent has defected more times than you over the entire game so far.
# - If the number of defections is equal, cooperate.  3. Every 50 rounds,
# cooperate regardless of the opponent's recent actions.  4. In the last 10
# rounds of the game, always defect.  5. If at any point your score falls behind
# your opponent's by more than 20 points, defect for the next 5 rounds before
# returning to the main strategy.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          self.defect_for_next_5 = None
          return axl.Action.C
  
      # Get the last 3 rounds of opponent's history
      last_3_opponent_moves = opponent.history[-3:]
  
      # Rule 3: Every 50 rounds, cooperate
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 4: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 5: If behind by more than 20 points, defect for the next 5 rounds
      if self.score < opponent.score - 20:
          if not self.defect_for_next_5:
              self.defect_for_next_5 = 5
          if self.defect_for_next_5 > 0:
              self.defect_for_next_5 -= 1
              return axl.Action.D
      else:
          self.defect_for_next_5 = None
  
      # Rule 2a: If opponent cooperated in the last 3 rounds, cooperate
      if last_3_opponent_moves.count(axl.Action.D) == 0 and len(last_3_opponent_moves) == 3:
          return axl.Action.C
  
      # Rule 2b: If opponent defected in the last 3 rounds, defect
      if last_3_opponent_moves.count(axl.Action.D) == 3:
          return axl.Action.D
  
      # Rule 2c: Mixed actions in the last 3 rounds
      if len(last_3_opponent_moves) == 3:
          # Count total defections so far
          my_defections = self.history.defections
          opponent_defections = opponent.history.defections
  
          if my_defections >= opponent_defections:
              return axl.Action.C
          elif opponent_defections > my_defections:
              return axl.Action.D

      return axl.Action.C



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous move.  5. In the last 10
# rounds of the game, always defect.  6. If your current score is significantly
# lower than your opponent's (more than 50 points behind), switch to always
# defecting for the next 20 rounds.  7. If you're ahead by more than 100 points,
# cooperate for the next 5 rounds to avoid appearing too aggressive.  8. If the
# opponent has cooperated for 5 consecutive rounds, cooperate once and then
# return to the main strategy.  9. In case of any uncertainty due to noise,
# assume the opponent defected and proceed accordingly.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 990
  
      # Helper function to check if we are in a round that is a multiple of 50
      def every_50_rounds():
          return len(self.history) % 50 == 0
  
      # Helper function to check if the opponent has cooperated for the last 5 rounds
      def opponent_cooperated_last_5():
          return len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:])
  
      # Helper function to check if we are significantly behind
      def significantly_behind():
          return self.score < opponent.score - 50
  
      # Helper function to check if we are significantly ahead
      def significantly_ahead():
          return self.score > opponent.score + 100
  
      # Helper function to switch to always defecting for the next 20 rounds
      def switch_to_always_defect():
          if not self.defect_for_next_20:
              self.defect_for_next_20 = 20
          return self.defect_for_next_20 > 0
  
      # Helper function to cooperate for the next 5 rounds if ahead
      def cooperate_for_next_5():
          if not self.cooperate_for_next_5:
              self.cooperate_for_next_5 = 5
          return self.cooperate_for_next_5 > 0
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_for_next_20 = 0
          self.cooperate_for_next_5 = 0
          return axl.Action.D
  
      # If we are in the last 10 rounds, always defect
      if in_last_10_rounds():
          return axl.Action.D
  
      # If we are significantly behind, switch to always defecting for the next 20 rounds
      if significantly_behind():
          self.defect_for_next_20 = 20
  
      # If we are significantly ahead, cooperate for the next 5 rounds
      if significantly_ahead():
          self.cooperate_for_next_5 = 5
  
      # If we are in the "always defect" mode, decrement the counter and defect
      if switch_to_always_defect():
          self.defect_for_next_20 -= 1
          return axl.Action.D
  
      # If we are in the "cooperate for next 5 rounds" mode, decrement the counter and cooperate
      if cooperate_for_next_5():
          self.cooperate_for_next_5 -= 1
          return axl.Action.C
  
      # If the opponent has cooperated for the last 5 rounds, cooperate once
      if opponent_cooperated_last_5():
          return axl.Action.C
  
      # Every 50 rounds, cooperate once regardless of the opponent's previous move
      if every_50_rounds():
          return axl.Action.C
  
      # If the opponent defected in the last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent cooperated in the last round, defect with 80% probability, cooperate with 20% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)



# Here's a simple cooperative strategy for the described game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before reverting to the main strategy.  5. In the last 10
# rounds of the game, always play D.  6. If your score is significantly lower
# than your opponent's (more than 100 points behind) after 500 rounds, switch to
# always playing D for the remainder of the game.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          self.defection_streak = 0  # Track defection streaks
          self.switch_to_defection = False  # Track if we are in a defection phase
          return axl.Action.C
  
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if we are more than 100 points behind after 500 rounds
      if len(self.history) > 500 and (opponent.score - self.score) > 100:
          return axl.Action.D
  
      # Check if we are in a defection phase (after opponent defected > 60% in last 50 rounds)
      if self.switch_to_defection:
          if self.defection_streak < 10:
              self.defection_streak += 1
              return axl.Action.D
          else:
              self.switch_to_defection = False  # End defection phase after 10 rounds
  
      # Check if opponent defected more than 60% in the last 50 rounds
      if len(self.history) >= 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.6:
              self.switch_to_defection = True
              self.defection_streak = 1
              return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Main strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent has
# cooperated in the last 3 rounds, cooperate.    - If the opponent has defected
# in the last 3 rounds, defect.    - If the opponent's actions have been mixed
# in the last 3 rounds:      a. If your score is higher than or equal to the
# opponent's, cooperate.      b. If your score is lower than the opponent's,
# defect.  3. Every 50 rounds, regardless of recent history:    - If your
# overall score is higher than the opponent's, cooperate.    - If your overall
# score is lower than the opponent's, defect.  4. In the last 10 rounds of the
# game, always defect.  5. If at any point your score falls behind the
# opponent's by 20 points or more, defect for the next 5 rounds, then return to
# the main strategy.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          self.defect_streak = 0  # Track defect streak after falling behind by 20 points
          return axl.Action.C
  
      # Check if we are in the last 10 rounds of the game
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Every 50 rounds, check the overall score and cooperate/defect accordingly
      if len(self.history) % 50 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If we are in a defect streak after falling behind by 20 points
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Check if we have fallen behind by 20 points or more
      if self.score < opponent.score - 20:
          self.defect_streak = 5  # Defect for the next 5 rounds
          return axl.Action.D
  
      # Look at the opponent's last 3 moves
      if len(opponent.history) >= 3:
          last_three = opponent.history[-3:]
          if last_three.count(axl.Action.C) == 3:
              return axl.Action.C
          elif last_three.count(axl.Action.D) == 3:
              return axl.Action.D
          else:
              # Mixed actions in the last 3 rounds
              if self.score >= opponent.score:
                  return axl.Action.C
              else:
                  return axl.Action.D
  
      # Default to cooperation if there is not enough history
      return axl.Action.C



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous action.  5. In the last
# 10 rounds of the game, always defect.  6. If your current score is
# significantly lower than your opponent's (more than 50 points behind), switch
# to always defecting for the next 20 rounds.  7. If you're ahead by more than
# 100 points, cooperate for the next 5 rounds to avoid triggering retaliation.
# 8. Return to step 2 and repeat for each round of the game.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are in "always defect" mode
          self.coop_streak = 0    # Track how many rounds we are in "always cooperate" mode
          return axl.Action.D
  
      # Step 6: If significantly behind, switch to always defecting for 20 rounds
      if self.score < opponent.score - 50:
          self.defect_streak = 20
  
      # Step 7: If ahead by more than 100 points, cooperate for the next 5 rounds
      if self.score > opponent.score + 100:
          self.coop_streak = 5
  
      # Handle defect streak (always defect for 20 rounds)
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Handle coop streak (always cooperate for 5 rounds)
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 2: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If the opponent cooperated in the previous round, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)



# Here's a simple cooperative strategy for the game:  1. Start by playing C in
# the first round.  2. In subsequent rounds:    - Play C if the opponent played
# C in the previous round.    - Play D if the opponent played D in the previous
# round.  3. Every 10 rounds, forgive any defection and play C regardless of the
# opponent's last move.  4. If the opponent has defected more than 60% of the
# time in the last 50 rounds, switch to always playing D for the next 10 rounds
# before returning to the main strategy.  5. In the last 10 rounds of the game,
# always play D.  6. If your score is significantly lower than your opponent's
# (more than 50 points difference) after 100 rounds, switch to always playing D
# for 20 rounds before returning to the main strategy.  7. Ignore single,
# isolated defections, assuming they might be due to noise. Only count
# consecutive defections or multiple defections within a short period as
# intentional.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_streak = 0  # Track consecutive defections
          self.forgive_round = 0  # Track when to forgive
          self.always_defect_until = 0  # Track when to stop always defecting
          self.switch_to_defect_until = 0  # Track when to stop defecting after score difference
          return axl.Action.C  # Start by playing C
  
      # Get the current round number
      current_round = len(self.history)
  
      # Rule 7: Ignore single, isolated defections
      if opponent.history[-1] == axl.Action.D:
          if current_round > 1 and opponent.history[-2] == axl.Action.D:
              self.defection_streak += 1
          else:
              self.defection_streak = 1
      else:
          self.defection_streak = 0
  
      # Rule 5: In the last 10 rounds, always play D
      if current_round >= 990:
          return axl.Action.D
  
      # Rule 4: If opponent defected more than 60% in the last 50 rounds, switch to D for 10 rounds
      if current_round > 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.6:
              self.always_defect_until = current_round + 10
  
      if current_round <= self.always_defect_until:
          return axl.Action.D
  
      # Rule 6: If score difference is more than 50 after 100 rounds, switch to D for 20 rounds
      if current_round > 100:
          my_score, opponent_score = self.total_scores(self.history[-100:], opponent.history[-100:])
          if opponent_score - my_score > 50:
              self.switch_to_defect_until = current_round + 20
  
      if current_round <= self.switch_to_defect_until:
          return axl.Action.D
  
      # Rule 3: Every 10 rounds, forgive any defection and play C
      if current_round % 10 == 0:
          return axl.Action.C
  
      # Rule 2: Play C if opponent played C in the previous round, else play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. For subsequent rounds:    - If the opponent cooperated in
# the previous round, cooperate.    - If the opponent defected in the previous
# round, defect.  3. Every 10 rounds, regardless of the opponent's previous
# action:    - If your total score is higher than or equal to your opponent's,
# cooperate.    - If your total score is lower than your opponent's, defect.  4.
# If you've defected for 3 consecutive rounds, cooperate in the next round.  5.
# In the last 10 rounds of the game, always defect.  6. If at any point your
# score falls behind your opponent's by 20 points or more, defect for the next 5
# rounds before returning to the main strategy.  7. If you notice a clear
# pattern in your opponent's play (e.g., always cooperating or alternating),
# adjust your strategy to exploit it for 5 rounds before returning to the main
# strategy.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Subfunction to detect a clear pattern in opponent's play
      def detect_pattern():
          if len(opponent.history) < 5:
              return None
          # Check if opponent always cooperates
          if all(action == axl.Action.C for action in opponent.history[-5:]):
              return axl.Action.D
          # Check if opponent alternates between C and D
          if all(opponent.history[i] != opponent.history[i + 1] for i in range(-5, -1)):
              return axl.Action.D
          return None
  
      # First round: Cooperate
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.defect_for_5_rounds = 0     # Track if we need to defect for 5 rounds
          self.exploit_pattern = None      # Track if we are exploiting a pattern
          return axl.Action.C
  
      # If we are exploiting a pattern, follow it for 5 rounds
      if self.exploit_pattern is not None:
          if len(self.history) % 5 == 0:
              self.exploit_pattern = None  # Stop exploiting after 5 rounds
          else:
              return self.exploit_pattern
  
      # If we are in the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # If we are defecting for 5 rounds due to score difference
      if self.defect_for_5_rounds > 0:
          self.defect_for_5_rounds -= 1
          return axl.Action.D
  
      # Check if we need to defect for 5 rounds due to score difference
      if (self.score - opponent.score) < -20:
          self.defect_for_5_rounds = 5
          return axl.Action.D
  
      # Every 10 rounds, check the score and decide
      if len(self.history) % 10 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If we defected for 3 consecutive rounds, cooperate
      if self.consecutive_defections >= 3:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Detect a pattern in opponent's play and exploit it
      pattern_action = detect_pattern()
      if pattern_action is not None:
          self.exploit_pattern = pattern_action
          return pattern_action
  
      # Main strategy: Tit-for-tat
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D
      else:
          self.consecutive_defections = 0
          return axl.Action.C



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D with
# 90% probability and C with 10% probability.  4. If your score is significantly
# lower than your opponent's (more than 20 points behind), play D for the next 5
# rounds regardless of the opponent's actions.  5. Every 50 rounds, play C once
# to test if the opponent is willing to cooperate.  6. In the last 10 rounds of
# the game, always play D.  7. If the opponent has played C for 5 consecutive
# rounds, play C once, then revert to the main strategy.  8. Repeat these steps
# for the duration of the game, adjusting your actions based on the opponent's
# most recent move and the overall game state.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_cooperations = 0  # Track consecutive cooperations by opponent
          self.behind_counter = 0  # Track rounds to play D when behind
          return axl.Action.D  # Start by playing D
  
      # Check if we are significantly behind
      if self.score < opponent.score - 20:
          self.behind_counter = 5  # Play D for the next 5 rounds
  
      # If we are in the "behind" mode, decrement the counter and play D
      if self.behind_counter > 0:
          self.behind_counter -= 1
          return axl.Action.D
  
      # Check if we are in the last 10 rounds of the game
      if len(self.history) >= 990:
          return axl.Action.D  # Always play D in the last 10 rounds
  
      # Every 50 rounds, play C once to test cooperation
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Track opponent's consecutive cooperations
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_cooperations += 1
      else:
          self.consecutive_cooperations = 0
  
      # If opponent has cooperated for 5 consecutive rounds, play C once
      if self.consecutive_cooperations >= 5:
          self.consecutive_cooperations = 0  # Reset after playing C
          return axl.Action.C
  
      # Main strategy logic based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D  # Play D if opponent played C last round
      else:
          # Play D with 90% probability, C with 10% probability if opponent played D
          return self._random.random_choice(0.1)



# Here's a simple cooperative strategy for the given iterated normal-form game:
# 1. Start by playing C in the first round.  2. In subsequent rounds:    - If
# the opponent played C in the previous round, play C.    - If the opponent
# played D in the previous round, play D.  3. Every 10 rounds, forgive any
# defections and play C regardless of the opponent's previous move.  4. If the
# opponent has defected more than 60% of the time in the last 50 rounds, switch
# to always playing D for the next 10 rounds before reverting to the main
# strategy.  5. In the last 10 rounds of the game, always play D to protect
# against end-game defection.  6. If your own score is significantly lower than
# expected (less than 1.5 points per round on average over the last 100 rounds),
# switch to always playing D for the next 20 rounds before reverting to the main
# strategy.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      FORGIVENESS_ROUND_INTERVAL = 10
      DEFECT_THRESHOLD = 0.6
      DEFECT_PENALTY_ROUNDS = 10
      LOW_SCORE_THRESHOLD = 1.5
      LOW_SCORE_PENALTY_ROUNDS = 20
      LAST_ROUNDS = 10
      TOTAL_ROUNDS = 1000
  
      # First round: always cooperate
      if self.first_round():
          self.defect_penalty_counter = 0
          self.low_score_penalty_counter = 0
          return axl.Action.C
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= TOTAL_ROUNDS - LAST_ROUNDS:
          return axl.Action.D
  
      # Check if we are in a penalty phase due to opponent's defections
      if self.defect_penalty_counter > 0:
          self.defect_penalty_counter -= 1
          return axl.Action.D
  
      # Check if we are in a penalty phase due to low score
      if self.low_score_penalty_counter > 0:
          self.low_score_penalty_counter -= 1
          return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % FORGIVENESS_ROUND_INTERVAL == 0:
          return axl.Action.C
  
      # Check if opponent has defected more than 60% in the last 50 rounds
      if len(opponent.history) >= 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > DEFECT_THRESHOLD:
              self.defect_penalty_counter = DEFECT_PENALTY_ROUNDS
              return axl.Action.D
  
      # Check if our score is significantly lower than expected
      if len(self.history) >= 100:
          recent_scores = self.total_scores(self.history[-100:], opponent.history[-100:])
          if recent_scores[0] / 100 < LOW_SCORE_THRESHOLD:
              self.low_score_penalty_counter = LOW_SCORE_PENALTY_ROUNDS
              return axl.Action.D
  
      # Main strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the described iterated game:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent has cooperated in the last 3 rounds, cooperate.    - If the opponent
# has defected in the last 3 rounds, defect.    - If the opponent's last 3 moves
# are mixed:      a. Calculate the opponent's cooperation rate over the last 10
# rounds.      b. If their cooperation rate is 60% or higher, cooperate.      c.
# If their cooperation rate is below 60%, defect.  3. Every 50 rounds,
# regardless of the opponent's recent actions:    - Cooperate for one round to
# test if the opponent is willing to reciprocate cooperation.  4. If you're in
# the last 10 rounds of the game:    - Always defect to maximize final payoff.
# 5. If you detect a consistent pattern in the opponent's play over 20 rounds:
# - Adjust your strategy to exploit the pattern by playing the optimal response.
# 6. Reset your strategy to step 1 if you notice a significant change in the
# opponent's behavior that doesn't fit their previous pattern.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Step 1: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N
  
      # Step 2: Check the opponent's last 3 moves
      if len(opponent.history) >= 3:
          last_3_moves = opponent.history[-3:]
          if last_3_moves.count(axl.Action.C) == 3:
              return axl.Action.C  # Opponent cooperated in the last 3 rounds
          elif last_3_moves.count(axl.Action.D) == 3:
              return axl.Action.D  # Opponent defected in the last 3 rounds
          else:
              # Mixed moves in the last 3 rounds, calculate cooperation rate over the last 10 rounds
              coop_rate = cooperation_rate(opponent.history, 10)
              if coop_rate >= 0.6:
                  return axl.Action.C  # Cooperate if cooperation rate is 60% or higher
              else:
                  return axl.Action.D  # Defect if cooperation rate is below 60%
  
      # Step 3: Every 50 rounds, cooperate to test opponent's willingness to reciprocate
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 4: In the last 10 rounds, always defect
      if self.match_attributes["length"] and len(self.history) >= self.match_attributes["length"] - 10:
          return axl.Action.D
  
      # Step 5: Detect a consistent pattern in the opponent's play over 20 rounds
      if len(opponent.history) >= 20:
          last_20_moves = opponent.history[-20:]
          if last_20_moves.count(axl.Action.C) == 20:
              return axl.Action.D  # Exploit by defecting if opponent always cooperates
          elif last_20_moves.count(axl.Action.D) == 20:
              return axl.Action.C  # Cooperate if opponent always defects (Tit-for-Tat-like)
  
      # Step 6: Reset strategy if opponent's behavior changes significantly
      if len(opponent.history) >= 20:
          last_10_moves = opponent.history[-10:]
          previous_10_moves = opponent.history[-20:-10]
          if last_10_moves != previous_10_moves:
              return axl.Action.C  # Reset to cooperation if behavior changes
  
      # Default action: Cooperate
      return axl.Action.C



# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect.  3. If the opponent cooperated in the previous round, defect
# with 80% probability and cooperate with 20% probability.  4. Every 50 rounds,
# cooperate once regardless of the opponent's previous action.  5. In the last
# 10 rounds of the game, always defect.  6. If your current score is
# significantly lower than your opponent's (more than 50 points behind), switch
# to always defecting for the next 20 rounds.  7. If you're ahead by more than
# 100 points, cooperate for the next 5 rounds to avoid appearing too aggressive.
# 8. Return to the main strategy after any temporary changes in steps 6 or 7.

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
          self.defect_streak = 0  # Track how many rounds we are in a defect streak (step 6)
          self.coop_streak = 0    # Track how many rounds we are in a cooperation streak (step 7)
          return axl.Action.D
  
      # Step 6: If significantly behind, switch to always defecting for 20 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Step 7: If ahead by more than 100 points, cooperate for the next 5 rounds
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Check score difference
      score_diff = opponent.score - self.score
      if score_diff > 50:
          self.defect_streak = 20  # Switch to defecting for 20 rounds
          return axl.Action.D
      elif score_diff < -100:
          self.coop_streak = 5  # Cooperate for the next 5 rounds
          return axl.Action.C
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: Every 50 rounds, cooperate once
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 2 and 3: Main strategy
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Defect if opponent defected last round
      else:
          # Defect with 80% probability, cooperate with 20% probability
          return self._random.random_choice(0.2)



# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - Play C if the
# opponent played C in the previous round.    - Play D if the opponent played D
# in the previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before reverting to the main strategy.  5. In the last 10
# rounds of the game, always play D.  6. Ignore single, isolated defections,
# treating them as potential noise. Only respond to defections that occur in two
# consecutive rounds.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          self.defection_streak = 0  # Track consecutive defections
          self.punishment_mode = False  # Track if we are in punishment mode
          self.punishment_counter = 0  # Track how many rounds of punishment are left
          return axl.Action.C
  
      # Last 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if we are in punishment mode
      if self.punishment_mode:
          self.punishment_counter += 1
          if self.punishment_counter >= 10:
              self.punishment_mode = False  # End punishment after 10 rounds
          return axl.Action.D
  
      # Check if we should enter punishment mode
      if len(self.history) >= 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.6:
              self.punishment_mode = True
              self.punishment_counter = 0
              return axl.Action.D
  
      # Every 10 rounds, forgive and cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Respond to opponent's last move
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D  # Respond to two consecutive defections
      elif opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Respond to a single defection
      else:
          return axl.Action.C  # Cooperate if opponent cooperated last round



# Here's a simple strategy for the described game:  1. Start by cooperating in
# the first round.  2. Keep track of your opponent's actions over the last 10
# rounds.  3. If your opponent has cooperated 7 or more times out of the last 10
# rounds, cooperate.  4. If your opponent has cooperated 3 or fewer times out of
# the last 10 rounds, defect.  5. If your opponent has cooperated 4 to 6 times
# out of the last 10 rounds, randomly choose to cooperate or defect with equal
# probability.  6. In the last 10 rounds of the game, always defect regardless
# of the opponent's actions.  7. If there aren't enough previous rounds to apply
# the above rules (i.e., in the first 10 rounds), cooperate.  8. Ignore any
# perceived noise in actions and treat the observed actions as the opponent's
# true intentions.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # 6. In the last 10 rounds of the game, always defect regardless of the opponent's actions.
      if len(self.history) >= 990:
          return axl.Action.D
  
      # 7. If there aren't enough previous rounds to apply the above rules (i.e., in the first 10 rounds), cooperate.
      if len(self.history) < 10:
          return axl.Action.C
  
      # 2. Keep track of your opponent's actions over the last 10 rounds.
      last_10_opponent_moves = opponent.history[-10:]
  
      # 3. If your opponent has cooperated 7 or more times out of the last 10 rounds, cooperate.
      cooperations = last_10_opponent_moves.count(axl.Action.C)
      if cooperations >= 7:
          return axl.Action.C
  
      # 4. If your opponent has cooperated 3 or fewer times out of the last 10 rounds, defect.
      if cooperations <= 3:
          return axl.Action.D
  
      # 5. If your opponent has cooperated 4 to 6 times out of the last 10 rounds, randomly choose to cooperate or defect with equal probability.
      if 4 <= cooperations <= 6:
          return self._random.random_choice(0.5)



# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, always defect in the next round.  3. If the opponent cooperated in the
# previous round, defect with 80% probability and cooperate with 20% probability
# in the next round.  4. If you're currently on a streak of three or more mutual
# cooperations, defect in the next round to exploit the opponent's trust.  5. If
# the opponent has cooperated for the last five rounds consecutively, switch to
# always defecting for the next three rounds to maximize payoff.  6. If you've
# been defecting for 10 consecutive rounds and the opponent has been
# consistently cooperating, cooperate once to encourage their continued
# cooperation, then resume the strategy from step 2.  7. In the last 50 rounds
# of the game, always defect regardless of the opponent's actions to maximize
# final payoff.  8. Follow these rules in order, applying the first one that
# matches the current situation.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.defect_streak = 0  # Track consecutive defections
          self.mutual_coop_streak = 0  # Track mutual cooperations
          self.exploit_mode = 0  # Track rounds of exploitation after 5 cooperations
          return axl.Action.D
  
      # Step 7: In the last 50 rounds, always defect
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Step 2: If the opponent defected in the previous round, always defect
      if opponent.history[-1] == axl.Action.D:
          self.mutual_coop_streak = 0  # Reset mutual cooperation streak
          self.defect_streak += 1
          return axl.Action.D
  
      # Step 3: If the opponent cooperated in the previous round, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          self.defect_streak = 0  # Reset defect streak
          self.mutual_coop_streak += 1
          if self._random.random_choice(0.2):
              return axl.Action.C
          return axl.Action.D
  
      # Step 4: If on a streak of 3 or more mutual cooperations, defect to exploit trust
      if self.mutual_coop_streak >= 3:
          self.mutual_coop_streak = 0  # Reset after exploitation
          return axl.Action.D
  
      # Step 5: If opponent has cooperated for the last 5 rounds, defect for the next 3 rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.C] * 5:
          if self.exploit_mode < 3:
              self.exploit_mode += 1
              return axl.Action.D
          else:
              self.exploit_mode = 0  # Reset exploit mode after 3 defections
  
      # Step 6: If defecting for 10 consecutive rounds and opponent cooperated, cooperate once
      if self.defect_streak >= 10 and opponent.history[-10:].count(axl.Action.C) == 10:
          self.defect_streak = 0  # Reset defect streak after cooperation
          return axl.Action.C
  
      # Default to defect if no other rule applies
      return axl.Action.D



# Here's a simple cooperative strategy for the given game:  1. Start by playing
# C in the first round.  2. In subsequent rounds:    - Play C if the opponent
# played C in the previous round.    - Play D if the opponent played D in the
# previous round.  3. Every 10 rounds, forgive any defection and play C
# regardless of the opponent's last move.  4. If the opponent has defected more
# than 60% of the time in the last 50 rounds, switch to always playing D for the
# next 10 rounds before returning to the main strategy.  5. In the last 10
# rounds of the game, always play D to protect against end-game defection.  6.
# If your score is significantly lower than your opponent's (more than 50 points
# behind) after 100 rounds, switch to always playing D for 20 rounds before
# returning to the main strategy.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 990
  
      # Helper function to check if we should forgive defection every 10 rounds
      def forgive_defection():
          return len(self.history) % 10 == 0
  
      # Helper function to check if opponent defected more than 60% in the last 50 rounds
      def opponent_defected_more_than_60_percent():
          if len(opponent.history) < 50:
              return False
          last_50 = opponent.history[-50:]
          return last_50.count(axl.Action.D) / 50 > 0.6
  
      # Helper function to check if we are significantly behind in score after 100 rounds
      def significantly_behind_in_score():
          if len(self.history) < 100:
              return False
          return (opponent.score - self.score) > 50
  
      # First round: always cooperate
      if self.first_round():
          self.defect_mode = None  # Custom attribute to track defect mode
          return axl.Action.C
  
      # If in the last 10 rounds, always play D
      if in_last_10_rounds():
          return axl.Action.D
  
      # If opponent defected more than 60% in the last 50 rounds, switch to D for 10 rounds
      if opponent_defected_more_than_60_percent():
          if self.defect_mode is None:
              self.defect_mode = 10  # Set defect mode for 10 rounds
          if self.defect_mode > 0:
              self.defect_mode -= 1
              return axl.Action.D
  
      # If significantly behind in score after 100 rounds, switch to D for 20 rounds
      if significantly_behind_in_score():
          if self.defect_mode is None:
              self.defect_mode = 20  # Set defect mode for 20 rounds
          if self.defect_mode > 0:
              self.defect_mode -= 1
              return axl.Action.D
  
      # If in defect mode, continue defecting
      if self.defect_mode is not None and self.defect_mode > 0:
          self.defect_mode -= 1
          return axl.Action.D
  
      # Every 10 rounds, forgive any defection and play C
      if forgive_defection():
          return axl.Action.C
  
      # Main strategy: play C if opponent played C last round, otherwise play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D



# Here's a simple strategy for the iterated normal-form game:  1. Start by
# cooperating in the first round.  2. In subsequent rounds:    - If the opponent
# cooperated in the previous round, cooperate.    - If the opponent defected in
# the previous round, defect.  3. Every 10 rounds, regardless of the opponent's
# previous action:    - If your total score is higher than or equal to your
# opponent's, cooperate.    - If your total score is lower than your opponent's,
# defect.  4. If you've defected for 3 consecutive rounds, cooperate in the next
# round regardless of the opponent's previous action.  5. In the last 10 rounds
# of the game, always defect.  6. If at any point your score falls behind your
# opponent's by 20 points or more, defect for the next 5 rounds before returning
# to the main strategy.  7. If you notice a clear pattern in your opponent's
# play (e.g., always cooperating or alternating), adapt your strategy to exploit
# it for 5 rounds before returning to the main strategy.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Subfunction to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 990
  
      # Subfunction to check if we have defected for 3 consecutive rounds
      def defected_three_consecutive():
          return len(self.history) >= 3 and all(move == axl.Action.D for move in self.history[-3:])
  
      # Subfunction to check if we are behind by 20 points or more
      def behind_by_20_points():
          return self.score < opponent.score - 20
  
      # Subfunction to check if we are in a multiple of 10 rounds
      def every_10_rounds():
          return len(self.history) % 10 == 0
  
      # Subfunction to detect a clear pattern in the opponent's play
      def detect_pattern():
          if len(opponent.history) >= 4:
              # Check for always cooperating
              if all(move == axl.Action.C for move in opponent.history[-4:]):
                  return "always_cooperating"
              # Check for alternating pattern
              if opponent.history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
                  return "alternating"
          return None
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0  # Track consecutive defections
          self.behind_defect_count = 0  # Track rounds of forced defections when behind by 20 points
          self.pattern_exploit_count = 0  # Track rounds of exploiting a detected pattern
          return axl.Action.C  # Start by cooperating
  
      # If we are in the last 10 rounds, always defect
      if in_last_10_rounds():
          return axl.Action.D
  
      # If we are behind by 20 points or more, defect for the next 5 rounds
      if behind_by_20_points():
          if self.behind_defect_count < 5:
              self.behind_defect_count += 1
              return axl.Action.D
          else:
              self.behind_defect_count = 0  # Reset after 5 rounds of defecting
  
      # If we are exploiting a pattern, continue for 5 rounds
      if self.pattern_exploit_count > 0:
          self.pattern_exploit_count -= 1
          if self.detected_pattern == "always_cooperating":
              return axl.Action.D  # Exploit by defecting
          elif self.detected_pattern == "alternating":
              return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D  # Exploit alternating pattern
  
      # Detect a pattern in the opponent's play
      pattern = detect_pattern()
      if pattern:
          self.detected_pattern = pattern
          self.pattern_exploit_count = 5  # Exploit for 5 rounds
  
      # If we have defected for 3 consecutive rounds, cooperate
      if defected_three_consecutive():
          self.defect_streak = 0  # Reset defect streak
          return axl.Action.C
  
      # Every 10 rounds, compare scores and decide
      if every_10_rounds():
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Main strategy: Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          action = axl.Action.C
      else:
          action = axl.Action.D
  
      # Track defect streak
      if action == axl.Action.D:
          self.defect_streak += 1
      else:
          self.defect_streak = 0
  
      return action
