import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Here's a revised, simplified strategy that takes into account the feedback
# while maintaining an aggressive stance:  1. Start by playing D (defect) for
# the first 5 rounds.  2. After the first 5 rounds, maintain a rolling average
# of the opponent's choices over the last 20 moves.  3. For rounds 6 to 980, use
# the following decision rules in order:     a. If the opponent's cooperation
# rate in the last 20 moves is less than 30%, play D.        b. If the
# opponent's cooperation rate in the last 20 moves is more than 70%, play C.
# c. If neither of the above conditions are met (i.e., cooperation rate is
# between 30% and 70%), play tit-for-tat (copy the opponent's last move).  4.
# For the final 20 rounds (981-1000), always play D.  This strategy behaves
# aggressively in the following ways: - It starts with defection to establish an
# aggressive stance. - It quickly punishes opponents who defect frequently (less
# than 30% cooperation). - It only cooperates when faced with a highly
# cooperative opponent (more than 70% cooperation). - It defects for the last 20
# rounds to maximize final payoff.  The strategy is simple, with clear
# conditions for cooperation and defection. It's also robust against different
# types of opponents:  - Against aggressive opponents: It will quickly settle
# into mutual defection. - Against cooperative opponents: It will eventually
# cooperate, but only after the opponent demonstrates a high level of
# cooperation. - Against neutral opponents: It will engage in tit-for-tat play,
# which is effective against a wide range of strategies.  The strategy avoids
# complex rules and hard-to-track conditions, making it easier to implement and
# less prone to errors. The rolling 20-move window allows it to adapt to changes
# in the opponent's strategy throughout the game.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.opponent_coop_rate = [False] * 20
  
      if len(self.history) < 5:
          return axl.Action.D
  
      if len(self.history) >= 980:
          return axl.Action.D
  
      self.opponent_coop_rate.pop(0)
      self.opponent_coop_rate.append(opponent.history[-1] == axl.Action.C)
  
      coop_rate = sum(self.opponent_coop_rate) / len(self.opponent_coop_rate)
  
      if coop_rate < 0.3:
          return axl.Action.D
      elif coop_rate > 0.7:
          return axl.Action.C
      else:
          return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) for the first 3 rounds to signal cooperative intent.  2.
# For the remainder of the game, follow these rules in order:     a. If it's one
# of the last 10 rounds, continue with the strategy you were using before
# entering this phase.     b. If the opponent has defected in 3 out of the last
# 5 rounds, play D.     c. If you've played D for the last 3 rounds
# consecutively, play C as an "olive branch".     d. If the opponent has
# cooperated for the last 10 rounds consecutively, play C.     e. If it's a
# multiple of 40 rounds (40, 80, 120, etc.), play C as a periodic "olive
# branch".     f. If none of the above conditions are met, play whatever the
# opponent played in the previous round (Tit-for-Tat).  This revised strategy:
# 1. Is simpler and clearer about when to cooperate or defect. 2. Maintains a
# cooperative approach but is less forgiving of aggressive behavior. 3. Adapts
# more quickly to changes in the opponent's strategy. 4. Is more robust against
# various opponent types:    - Cooperates with cooperative opponents    -
# Protects against aggressive opponents    - Adapts well to neutral opponents 5.
# Reduces exploitability by making the "olive branch" less predictable. 6.
# Avoids overly complex conditions or unreachable states.  The order of
# conditions ensures that the strategy responds appropriately to recent opponent
# behavior, offers periodic cooperation opportunities, but defaults to a Tit-
# for-Tat approach in neutral situations. This balance should perform well
# across a variety of opponent strategies while maintaining a generally
# cooperative stance.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.last_10_rounds_strategy = None
  
      if len(self.history) < 3:
          return axl.Action.C
  
      if len(self.history) >= 990:
          if self.last_10_rounds_strategy is None:
              self.last_10_rounds_strategy = self.history[-1]
          return self.last_10_rounds_strategy
  
      if len(opponent.history) >= 5 and opponent.history[-5:].count(axl.Action.D) >= 3:
          return axl.Action.D
  
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.C
  
      if len(opponent.history) >= 10 and opponent.history[-10:].count(axl.Action.C) == 10:
          return axl.Action.C
  
      if len(self.history) % 40 == 0:
          return axl.Action.C
  
      return opponent.history[-1] if opponent.history else axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For the next 9 rounds, mirror
# your opponent's previous move.  3. After every 10 rounds, calculate the
# frequency of your opponent's C plays over the last 50 rounds (or all previous
# rounds if fewer than 50):    - If they played C more than 70% of the time,
# consider them cooperative.    - If they played C less than 30% of the time,
# consider them aggressive.    - Otherwise, consider them neutral.  4. Based on
# this assessment, adjust your strategy for the next 10 rounds:    - If they're
# cooperative: Play C with 90% probability, D with 10% probability.    - If
# they're aggressive: Play D with 90% probability, C with 10% probability.    -
# If they're neutral: Play C with 55% probability, D with 45% probability.  5.
# Implement the following override conditions, checked in this order:    a) If
# the opponent has played D for 4 or more of the last 5 rounds, play D.    b) If
# you're in the last 20 rounds of the game, play D.    c) If the opponent's last
# 3 moves follow a detectable pattern (CCC, DDD, CDC, etc.), play the move that
# would have scored highest against that pattern.  6. If none of the override
# conditions are met, play according to the probabilities set in step 4.  7.
# Repeat steps 3-6 until the game ends.  This revised strategy aims to be more
# adaptive and less exploitable while remaining relatively simple. It maintains
# a neutral stance with a slight bias towards cooperation in neutral situations.
# The strategy is more robust against different opponent types:  - Against
# cooperative opponents, it quickly shifts to high cooperation. - Against
# aggressive opponents, it responds with high defection and has a quicker
# trigger for all-out defection. - Against neutral opponents, it plays nearly
# 50-50 with a slight cooperative bias.  The override conditions add complexity
# but provide important safeguards: - Condition 5a protects against highly
# aggressive opponents. - Condition 5b implements a simple end-game strategy. -
# Condition 5c adds a basic pattern recognition to exploit predictable
# opponents.  This strategy should perform reasonably well against a variety of
# opponent types while remaining true to the goal of playing neutrally overall.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.assessment = "neutral"
          return axl.Action.C
  
      if 1 <= len(self.history) <= 9:
          return opponent.history[-1]
  
      if len(self.history) % 10 == 0:
          last_50 = opponent.history[-min(50, len(opponent.history)):]
          coop_freq = last_50.count(axl.Action.C) / len(last_50)
          if coop_freq > 0.7:
              self.assessment = "cooperative"
          elif coop_freq < 0.3:
              self.assessment = "aggressive"
          else:
              self.assessment = "neutral"
  
      if opponent.history[-5:].count(axl.Action.D) >= 4:
          return axl.Action.D
  
      if len(self.history) >= 980:
          return axl.Action.D
  
      last_3 = opponent.history[-3:]
      if len(last_3) == 3:
          if len(set(last_3)) < 3:  # Detects any repeating pattern
              best_response = axl.Action.D if last_3.count(axl.Action.C) >= 2 else axl.Action.C
              return best_response
  
      # Return C with probability p, D with probability 1-p
      if self.assessment == "cooperative":
          return self._random.random_choice(0.9)
      elif self.assessment == "aggressive":
          return self._random.random_choice(0.1)
      else:
          return self._random.random_choice(0.55)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing D (defect) for the first 20 rounds to establish an aggressive stance.
# 2. For the remaining rounds, follow these rules in order:     a. If it's one
# of the last 20 rounds of the game, play D.        b. If your cumulative score
# is more than 30 points behind your opponent's, play D for the next 10 rounds.
# c. If it's a multiple of 50th round (50, 100, 150, etc.), play D for the next
# 3 rounds.        d. If your opponent has played C for the last three
# consecutive rounds, play C.        e. If your opponent has played D for more
# than 60% of the last 20 rounds, play D.        f. Otherwise, play D.  3. Every
# 100 rounds, reset your count of the opponent's moves to prevent outdated
# information from influencing decisions.  This strategy: - Starts aggressively
# with 20 rounds of defection. - Is simple with clear conditions for cooperation
# and defection. - Maintains an overall aggressive stance by defaulting to
# defection. - Allows for short periods of cooperation to exploit consistently
# cooperative opponents. - Includes periodic forced defection to maintain
# aggression and prevent exploitation. - Has a catch-up mechanism that's
# aggressive but not overly prolonged. - Ends the game with pure defection to
# maximize final payoff. - Regularly resets opponent move tracking to adapt to
# changing strategies.  The order of conditions ensures that end-game strategy,
# catch-up mechanism, and periodic aggression take precedence over responding to
# the opponent's recent moves. This strategy should be robust against
# aggressive, cooperative, and neutral opponents while maintaining its
# aggressive nature.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defect_counter = 0
  
      if len(self.history) < 20:
          return axl.Action.D
  
      if len(self.history) > 980:
          return axl.Action.D
  
      if opponent.score - self.score > 30:
          self.defect_counter = 10
      
      if self.defect_counter > 0:
          self.defect_counter -= 1
          return axl.Action.D
  
      if len(self.history) % 50 == 0:
          self.defect_counter = 3
          return axl.Action.D
  
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      if opponent.history[-20:].count(axl.Action.D) / 20 > 0.6:
          return axl.Action.D
  
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) for the first 5 rounds to signal cooperative intent.  2.
# For the remainder of the game, use the following decision-making process in
# order:     a. If it's one of the last 10 rounds (991-1000), play C to avoid
# end-game defection.     b. If it's a multiple of 50 rounds (50, 100, 150,
# etc.), play C to periodically encourage cooperation.     c. If the opponent
# has played D for 5 consecutive rounds, enter a "Pavlov" mode for the next 20
# rounds:       - Play C if both players made the same choice in the previous
# round (CC or DD).       - Play D if the choices were different in the previous
# round (CD or DC).     d. Otherwise, use a "Adaptive Tit-for-Tat" approach:
# - If the opponent played C in the previous round, play C.       - If the
# opponent played D in the previous round:         * Calculate the opponent's
# defection rate over the last 50 rounds.         * Play C with probability (1 -
# defection rate), and D with probability (defection rate).  3. Throughout the
# game, keep track of the total score difference (your score minus opponent's
# score):    - If you're behind by more than 50 points, decrease the cooperation
# probability in step 2d by 10% (but never below 50%).    - If you're ahead by
# more than 50 points, increase the cooperation probability in step 2d by 10%
# (but never above 90%).  This revised strategy maintains a cooperative approach
# while being more adaptive to the opponent's behavior. It's still simple enough
# to implement but addresses the main points of feedback:  1. It's more robust
# against aggressive opponents by adapting the forgiveness rate based on the
# opponent's recent behavior. 2. It takes into account the game score, becoming
# slightly more aggressive when behind and more cooperative when ahead. 3. The
# Pavlov mode is extended to 20 rounds, providing more flexibility in dealing
# with aggressive phases. 4. The decision-making process is clearly ordered,
# with specific conditions for cooperation and defection.  This strategy should
# perform well against cooperative opponents, be more resilient against
# aggressive opponents, and adapt appropriately to neutral opponents.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.pavlov_mode = 0
          self.cooperation_probability = 1.0
          self.game_length = self.match_attributes['length']
  
      # Start by playing C for the first 5 rounds
      if len(self.history) < 5:
          return axl.Action.C
  
      # Play C for the last 10 rounds
      if len(self.history) > self.game_length - 11:
          return axl.Action.C
  
      # Play C every 50 rounds
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Pavlov mode
      if self.pavlov_mode > 0:
          self.pavlov_mode -= 1
          return axl.Action.C if self.history[-1] == opponent.history[-1] else axl.Action.D
  
      # Enter Pavlov mode if opponent defected for 5 consecutive rounds
      if opponent.history[-5:] == [axl.Action.D] * 5:
          self.pavlov_mode = 20
          return axl.Action.C if self.history[-1] == opponent.history[-1] else axl.Action.D
  
      # Adaptive Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      defection_rate = opponent.history[-50:].count(axl.Action.D) / 50
      self.cooperation_probability = 1 - defection_rate
  
      # Adjust cooperation probability based on score difference
      score_diff = self.score - opponent.score
      if score_diff < -50:
          self.cooperation_probability = max(0.5, self.cooperation_probability - 0.1)
      elif score_diff > 50:
          self.cooperation_probability = min(0.9, self.cooperation_probability + 0.1)
  
      return axl.Action.C if self._random.random() < self.cooperation_probability else axl.Action.D

# Here's a revised strategy that takes into account the feedback:  1. Start with
# a neutral stance: Play C (cooperate) with 50% probability and D (defect) with
# 50% probability for each round.  2. Maintain a sliding window of the
# opponent's last 20 moves.  3. For each round, determine your action based on
# the following conditions, in this order:     a) If the opponent has played D
# for the last 3 consecutive moves:       - Play D (to protect against
# exploitation)     b) If the opponent has played C for the last 3 consecutive
# moves:       - Play C with 80% probability and D with 20% probability (to
# encourage cooperation while occasionally exploiting)     c) If the opponent's
# cooperation rate in the sliding window is:       - Above 70%: Play C with 70%
# probability and D with 30% probability       - Between 30% and 70%: Play C
# with 50% probability and D with 50% probability       - Below 30%: Play C with
# 30% probability and D with 70% probability  4. If none of the above conditions
# are met (which would only happen in the first few rounds), maintain the
# initial 50/50 strategy.  5. Update the sliding window after each round,
# regardless of which condition was used to determine the action.  This revised
# strategy is simpler, more neutral, and more adaptive. It addresses the main
# points of feedback:  - It starts and maintains a neutral stance by default. -
# It uses a sliding window for continuous assessment of the opponent's behavior.
# - It implements a more gradual response to opponent behavior. - It maintains
# consistent behavior throughout the game, without an endgame strategy. - It has
# a flexible response to defection that doesn't lock into extended punishment
# phases.  The strategy should be robust against various opponent types: -
# Against cooperative opponents, it will tend towards cooperation but with some
# protection against exploitation. - Against aggressive opponents, it will lean
# towards defection but still allow for cooperation if the opponent changes
# behavior. - Against neutral opponents, it will maintain a balanced approach.
# The conditions are ordered to prioritize immediate response to short-term
# behavior (last 3 moves) before considering the overall trend in the sliding
# window. This allows for quick adaptation to changes in the opponent's strategy
# while still considering their general behavior.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.sliding_window = []
  
      # Update sliding window
      last_move = opponent.history[-1] if opponent.history else None
      self.sliding_window.append(last_move)
      if len(self.sliding_window) > 20:
          self.sliding_window.pop(0)
  
      # Check last 3 moves
      if len(opponent.history) >= 3:
          last_three = opponent.history[-3:]
          if all(move == axl.Action.D for move in last_three):
              return axl.Action.D
          elif all(move == axl.Action.C for move in last_three):
              return axl.Action.C if self._random.random() < 0.8 else axl.Action.D
  
      # Check cooperation rate in sliding window
      if len(self.sliding_window) == 20:
          coop_rate = self.sliding_window.count(axl.Action.C) / 20
          if coop_rate > 0.7:
              return axl.Action.C if self._random.random() < 0.7 else axl.Action.D
          elif coop_rate < 0.3:
              return axl.Action.C if self._random.random() < 0.3 else axl.Action.D
          else:  # Between 30% and 70%
              return axl.Action.C if self._random.random() < 0.5 else axl.Action.D
  
      # Default to 50/50
      return axl.Action.C if self._random.random() < 0.5 else axl.Action.D

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing D (defect) for the first 3 rounds to establish an initial aggressive
# stance.  2. For the rest of the game, follow these rules in order:     a. If
# it's one of the last 5 rounds of the game, play D to maximize final payoff.
# b. If the opponent has played D in all of the last 3 rounds, play D to punish
# consistent defection.     c. If the opponent has played C in all of the last 3
# rounds, play D once to exploit their cooperation, then play C in the next
# round if they cooperated.     d. If you've played D for the last 5 consecutive
# rounds and the opponent played C in the last round, play C once to test for
# possible cooperation.     e. If it's a multiple of 40 rounds (40, 80, 120,
# etc.), play D to maintain unpredictability and prevent exploitation.     f.
# Otherwise, play what the opponent played in the previous round (tit-for-tat).
# 3. Exception: If your score is significantly behind (more than 50 points) at
# any point after round 100, switch to always playing D for the next 20 rounds,
# then resume the main strategy.  This revised strategy: - Maintains aggression
# while allowing for cooperation - Is simpler with clearer conditions for
# cooperation and defection - Adapts to different opponent types - Includes a
# mechanism to attempt re-establishing cooperation after mutual defections - Has
# less predictable periodic defections - Accounts for overall game performance -
# Is more flexible in the endgame while still favoring defection  The order of
# conditions ensures that the most critical decisions (endgame, punishing
# defection, exploiting cooperation) are made first, with tit-for-tat as the
# default behavior.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.aggressive_mode = 0
  
      if len(self.history) < 3:
          return axl.Action.D
  
      if self.aggressive_mode > 0:
          self.aggressive_mode -= 1
          return axl.Action.D
  
      if len(self.history) > 100 and self.score < opponent.score - 50:
          self.aggressive_mode = 20
          return axl.Action.D
  
      if len(self.history) >= 995:
          return axl.Action.D
  
      if opponent.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.D
  
      if opponent.history[-3:].count(axl.Action.C) == 3:
          if self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D
  
      if self.history[-5:].count(axl.Action.D) == 5 and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      if len(self.history) % 40 == 0:
          return axl.Action.D
  
      return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (Cooperate) for the first 3 rounds to signal cooperative intent.  2.
# For the remaining rounds, follow these rules in order:     a. If it's one of
# the last 10 rounds, play C if the opponent has cooperated more than 50% of the
# time throughout the game; otherwise, play D.     b. If it's a multiple of 40
# rounds (40, 80, 120, etc.), play C regardless of the opponent's previous moves
# to encourage a return to cooperation.     c. If the opponent has defected more
# than 60% of the time in the last 15 rounds, use a Tit-for-Tat strategy: play
# whatever the opponent played in the previous round.     d. If the opponent has
# defected in the last two consecutive rounds, play D.     e. If none of the
# above conditions are met, play C.  This revised strategy:  1. Is simple and
# primarily cooperative. 2. Starts with a shorter cooperative signal (3 rounds
# instead of 5). 3. Has clear, ordered conditions for when to cooperate or
# defect. 4. Adapts more quickly to aggressive opponents (60% threshold over 15
# rounds). 5. Maintains periodic forced cooperation (every 40 rounds) to break
# negative cycles. 6. Has a specific end-game strategy based on the opponent's
# overall behavior. 7. Uses Tit-for-Two-Tats as its base strategy, which is
# forgiving but not easily exploitable.  This strategy should be robust against
# cooperative, neutral, and aggressive opponents while maintaining a cooperative
# approach when possible. It adapts more quickly to aggressive play but still
# allows for a return to cooperation.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      INITIAL_COOPERATION_ROUNDS = 3
      ENDGAME_START = 990
      PERIODIC_COOPERATION_INTERVAL = 40
      RECENT_ROUNDS_CHECK = 15
      DEFECTION_THRESHOLD = 0.6
      COOPERATION_THRESHOLD = 0.5
  
      # Start with cooperation
      if len(self.history) < INITIAL_COOPERATION_ROUNDS:
          return axl.Action.C
  
      opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)
  
      # Endgame strategy
      if len(self.history) > ENDGAME_START:
          return axl.Action.C if opponent_cooperation_rate > COOPERATION_THRESHOLD else axl.Action.D
  
      # Periodic cooperation
      if len(self.history) % PERIODIC_COOPERATION_INTERVAL == 0:
          return axl.Action.C
  
      # Check recent opponent behavior
      recent_defection_rate = opponent.history[-RECENT_ROUNDS_CHECK:].count(axl.Action.D) / RECENT_ROUNDS_CHECK
      if recent_defection_rate > DEFECTION_THRESHOLD:
          return opponent.history[-1]  # Tit-for-Tat
  
      # React to consecutive defections
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For the next 4 rounds, mirror
# your opponent's previous move.  3. After the first 5 rounds, and every 20
# rounds thereafter, evaluate your opponent's behavior:    - Calculate the
# percentage of C plays in the last 20 rounds (or all rounds if fewer than 20).
# - If they played C more than 60% of the time, consider them cooperative.    -
# If they played C less than 40% of the time, consider them aggressive.    -
# Otherwise, consider them neutral.  4. For each round, make your decision in
# the following order:     a. If it's one of the last 5 rounds of the game, play
# D.        b. If your opponent has played D in the last 2 consecutive rounds,
# play D.        c. If your opponent is classified as aggressive:       - Play D
# with 70% probability       - Play C with 30% probability        d. If your
# opponent is classified as cooperative:       - Play C with 90% probability
# - Play D with 10% probability        e. If your opponent is classified as
# neutral:       - If your total score is less than or equal to your opponent's,
# play D.       - If your total score is greater than your opponent's, play C.
# 5. If none of the above conditions are met, play C and D with equal
# probability (50/50).  This revised strategy: - Is simpler and clearer about
# when to cooperate or defect. - Adapts more quickly to opponent behavior
# (evaluating every 20 rounds instead of 100). - Takes into account the payoff
# structure by playing D more often against aggressive opponents and when behind
# in score. - Is more neutral against neutral opponents by basing decisions on
# the score difference. - Protects against end-game defection but for fewer
# rounds to be less predictable. - Responds more quickly to defection streaks. -
# Maintains a small random element to avoid being too predictable.  This
# strategy should be more robust against various opponent types while
# maintaining a generally neutral stance.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.evaluation_round = 5
          self.opponent_type = "neutral"
          self.last_evaluation = 0
          return axl.Action.C
  
      if len(self.history) < 5:
          return opponent.history[-1]
  
      if len(self.history) >= self.evaluation_round:
          last_20_rounds = min(20, len(self.history) - self.last_evaluation)
          c_percentage = opponent.history[-last_20_rounds:].count(axl.Action.C) / last_20_rounds
          if c_percentage > 0.6:
              self.opponent_type = "cooperative"
          elif c_percentage < 0.4:
              self.opponent_type = "aggressive"
          else:
              self.opponent_type = "neutral"
          self.last_evaluation = len(self.history)
          self.evaluation_round = len(self.history) + 20
  
      if len(self.history) > 995:
          return axl.Action.D
  
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      if self.opponent_type == "aggressive":
          return self._random.random_choice(0.3)  # 30% C, 70% D
      elif self.opponent_type == "cooperative":
          return self._random.random_choice(0.9)  # 90% C, 10% D
      elif self.opponent_type == "neutral":
          if self.score <= opponent.score:
              return axl.Action.D
          else:
              return axl.Action.C
  
      return self._random.random_choice(0.5)  # 50% C, 50% D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing D (defect) for the first 10 rounds to establish an initial stance and
# better assess the opponent's behavior.  2. After the first 10 rounds, evaluate
# the opponent's behavior:     a. If the opponent has cooperated in 7 or more of
# these rounds (70%+), switch to a "generous tit-for-tat" strategy:       - Play
# C in the next round.       - For subsequent rounds, copy the opponent's
# previous move, but with a 10% chance of playing C even if the opponent played
# D.     b. If the opponent has defected in 7 or more of these rounds (70%+),
# continue playing D for the next 20 rounds.     c. If the opponent's behavior
# is mixed (3-6 cooperations), use a "suspicious tit-for-tat" strategy:       -
# Play D in the next round.       - For subsequent rounds, copy the opponent's
# previous move.  3. Reassess the opponent's behavior every 30 rounds:     a. If
# they've cooperated in more than 70% of the last 30 rounds, switch to or
# continue with the "generous tit-for-tat" strategy.     b. If they've defected
# in more than 70% of the last 30 rounds, switch to or continue playing D.
# c. If their behavior is mixed (between 30-70% cooperation), switch to or
# continue with the "suspicious tit-for-tat" strategy.  4. In rounds 971-990
# (the 20 rounds before the last 10):    - If currently in "generous tit-for-
# tat" or "suspicious tit-for-tat" mode, switch to strict tit-for-tat (always
# copy the opponent's previous move).    - If currently defecting, continue to
# defect.  5. For the last 10 rounds (991-1000), always play D to maximize final
# payoff.  This revised strategy: - Starts aggressively but quickly adapts to
# cooperative opponents. - Is clearer about the conditions for cooperation or
# defection. - Provides a more balanced approach to different opponent types. -
# Allows for quicker adaptation to opponent behavior. - Reduces the end-game
# defection period to minimize potential retaliation. - Maintains an overall
# aggressive stance while being more responsive to cooperation.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.phase = "initial"
          self.reassess_round = 10
      
      if len(self.history) == self.reassess_round:
          if self.phase == "initial":
              coop_count = opponent.history.cooperations
              if coop_count >= 7:
                  self.phase = "generous_tit_for_tat"
              elif coop_count <= 3:
                  self.phase = "defect"
                  self.reassess_round += 20
              else:
                  self.phase = "suspicious_tit_for_tat"
          else:
              coop_count = opponent.history[-30:].count(axl.Action.C)
              if coop_count > 21:  # More than 70% cooperation
                  self.phase = "generous_tit_for_tat"
              elif coop_count < 9:  # Less than 30% cooperation
                  self.phase = "defect"
              else:
                  self.phase = "suspicious_tit_for_tat"
          self.reassess_round += 30
  
      if len(self.history) > 970:
          if len(self.history) > 990:
              return axl.Action.D
          elif self.phase in ["generous_tit_for_tat", "suspicious_tit_for_tat"]:
              self.phase = "tit_for_tat"
  
      if self.phase == "initial":
          return axl.Action.D
      elif self.phase == "generous_tit_for_tat":
          if not opponent.history:
              return axl.Action.C
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          if self._random.random() < 0.1:
              return axl.Action.C
          return axl.Action.D
      elif self.phase == "suspicious_tit_for_tat":
          if not opponent.history:
              return axl.Action.D
          return opponent.history[-1]
      elif self.phase == "tit_for_tat":
          if not opponent.history:
              return axl.Action.C
          return opponent.history[-1]
      else:  # defect
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. For the next 9 rounds, use Tit-
# for-Tat:    - Play C if the opponent played C in the previous round.    - Play
# D if the opponent played D in the previous round.  3. After every 10 rounds,
# evaluate the opponent's behavior based on their last 10 moves:    - If they
# cooperated 6 or more times, consider them cooperative.    - If they cooperated
# 4 or fewer times, consider them aggressive.    - Otherwise, consider them
# neutral.  4. For the remaining rounds, follow these rules in order:     a) If
# it's one of the last 10 rounds of the game:       - If the opponent has
# cooperated in more than 60% of all rounds, play C.       - Otherwise, play D.
# b) If the opponent is currently classified as cooperative:       - Play C.
# - If they defect twice in a row, switch to Tit-for-Tat for the next 10 rounds.
# c) If the opponent is currently classified as aggressive:       - Use Tit-for-
# Tat, but with a 10% chance of playing C after the opponent's D.     d) If the
# opponent is currently classified as neutral:       - Use Tit-for-Two-Tats:
# only defect if the opponent defects twice in a row.  5. Repeat step 3 after
# every 10 rounds to re-evaluate and reclassify the opponent.  This revised
# strategy: - Maintains simplicity while being more adaptive. - Starts
# cooperatively and aims to sustain cooperation with cooperative opponents. -
# Responds more flexibly to aggressive opponents with a modified Tit-for-Tat. -
# Uses clear conditions for cooperation and defection. - Regularly re-evaluates
# the opponent's behavior to adapt to changes. - Protects against end-game
# defection while still allowing for cooperation with consistently cooperative
# opponents.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.opponent_type = None
          self.tft_counter = 0
          return axl.Action.C
  
      if len(self.history) < 10:
          return opponent.history[-1]
  
      if len(self.history) % 10 == 0:
          last_10_opponent_moves = opponent.history[-10:]
          cooperations = last_10_opponent_moves.count(axl.Action.C)
          if cooperations >= 6:
              self.opponent_type = "cooperative"
          elif cooperations <= 4:
              self.opponent_type = "aggressive"
          else:
              self.opponent_type = "neutral"
          self.tft_counter = 0
  
      if len(self.history) > 990:
          if opponent.history.cooperations / len(opponent.history) > 0.6:
              return axl.Action.C
          else:
              return axl.Action.D
  
      if self.opponent_type == "cooperative":
          if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              self.tft_counter = 10
          if self.tft_counter > 0:
              self.tft_counter -= 1
              return opponent.history[-1]
          return axl.Action.C
  
      if self.opponent_type == "aggressive":
          if opponent.history[-1] == axl.Action.D and self._random.random() < 0.1:
              return axl.Action.C
          return opponent.history[-1]
  
      if self.opponent_type == "neutral":
          if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
          return axl.Action.C

# Here's a revised strategy that takes into account the feedback and aims to be
# clearer and more neutral:  1. Start by playing C (cooperate) for the first
# round.  2. For the next 19 rounds, mirror your opponent's previous move. If
# they played C, you play C; if they played D, you play D.  3. After every 20
# rounds, evaluate your opponent's behavior:    - Calculate their cooperation
# rate (number of C plays divided by 20) for the last 20 rounds.  4. Based on
# the most recent cooperation rate, decide your next move:    - If their
# cooperation rate is exactly 50%, play C.    - If their cooperation rate is
# above 50%, play C with a probability equal to their cooperation rate.    - If
# their cooperation rate is below 50%, play D with a probability equal to (1 -
# their cooperation rate).  5. Override the above rules in these specific
# situations:    - If your opponent has played D for the last 3 consecutive
# rounds, play D for the next round.    - If you're in the last 20 rounds of the
# game, play D with a 60% probability and C with a 40% probability, regardless
# of the opponent's recent actions.  6. Repeat steps 3-5 until the game ends.
# This revised strategy: - Maintains simplicity while being more adaptive. -
# Starts neutrally and remains relatively neutral throughout. - Is more robust
# against changing opponent strategies. - Provides clear conditions for
# cooperation and defection. - Avoids hard switches that could be exploited by
# opponents. - Introduces controlled randomness to be less predictable. -
# Balances between reacting to the opponent and maintaining a consistent
# approach.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(self.history) % 20 == 0:
          self.last_cooperation_rate = opponent.history[-20:].count(axl.Action.C) / 20
      
      if len(self.history) <= 20:
          return opponent.history[-1]
      
      if len(self.history) > 980:
          return self._random.random_choice(0.4)
      
      if opponent.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.D
      
      if self.last_cooperation_rate == 0.5:
          return axl.Action.C
      elif self.last_cooperation_rate > 0.5:
          return self._random.random_choice(self.last_cooperation_rate)
      else:
          return self._random.random_choice(1 - self.last_cooperation_rate)

# Here's a revised, simpler, and more aggressive strategy that takes into
# account the feedback:  1. Start by playing D (defect) for the first 10 rounds
# to establish an aggressive stance and gather initial information about the
# opponent's behavior.  2. After the first 10 rounds, use the following
# decision-making process for each subsequent round:     a. If the opponent has
# played C (cooperate) in the last 3 consecutive rounds, play C. This allows for
# some cooperation if the opponent is consistently cooperative, potentially
# leading to mutual cooperation payoffs.     b. If the opponent's last two moves
# were DC (Defect then Cooperate), play D. This exploits opponents who might be
# trying to establish a cooperative pattern after defection.     c. If you've
# played C in the last round and the opponent played D, play D for the next 2
# rounds. This punishes defection more aggressively.     d. If the current round
# number is divisible by 20, play C. This occasional cooperation serves as a
# "forgiveness" mechanism and tests if the opponent is willing to cooperate.
# e. If none of the above conditions are met, play D.  3. In the last 50 rounds
# of the game:        a. If your total score is higher than your opponent's,
# always play D to secure your lead.        b. If your score is lower or equal,
# play tit-for-tat (copy the opponent's last move) to either maintain your
# position or attempt to catch up.  This revised strategy:  - Starts
# aggressively and maintains an overall aggressive stance. - Is simpler, with
# clear conditions for cooperation and defection. - Exploits the payoff
# structure by trying to entice the opponent into a pattern where you can score
# 5 points (by playing D when they play C). - Adapts more quickly to the
# opponent's behavior with shorter evaluation periods. - Includes a mechanism to
# occasionally test for cooperation without being too vulnerable. - Has a clear
# endgame strategy based on the current score.  This strategy should be robust
# against aggressive opponents by maintaining a primarily defective stance,
# while still allowing for cooperation with consistently cooperative opponents.
# Against neutral opponents, it provides opportunities for cooperation while
# remaining cautious and ready to punish defection.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.defect_count = 0
  
      round_number = len(self.history) + 1
  
      if round_number <= 10:
          return axl.Action.D
  
      if round_number > 950:
          if self.score > opponent.score:
              return axl.Action.D
          else:
              return opponent.history[-1]
  
      if round_number % 20 == 0:
          return axl.Action.C
  
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      if opponent.history[-2:] == [axl.Action.D, axl.Action.C]:
          return axl.Action.D
  
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.defect_count = 2
  
      if self.defect_count > 0:
          self.defect_count -= 1
          return axl.Action.D
  
      self.defect_count = 0
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) for the first 20 rounds.  2. After the first 20 rounds,
# assess your opponent's behavior:    - If they've cooperated 14 or more times,
# consider them cooperative.    - If they've cooperated 6 or fewer times,
# consider them aggressive.    - Otherwise, consider them neutral.  3. For the
# remainder of the game (rounds 21-1000), use the following decision-making
# process in order:     a) If the opponent is classified as cooperative:       -
# Play C if the opponent played C in the previous round.       - If the opponent
# played D in the previous round, play D for this round only, then return to C.
# b) If the opponent is classified as aggressive:       - Use Tit-for-Tat: play
# what the opponent played in the previous round.     c) If the opponent is
# classified as neutral:       - Play C if both you and the opponent played C in
# the previous round.       - Play C with 70% probability if you played C and
# the opponent played D in the previous round.       - Play D if you played D
# and the opponent played D in the previous round.       - Play C if you played
# D and the opponent played C in the previous round.  4. Continuously reassess
# the opponent's behavior:    - Keep a rolling count of the opponent's
# cooperation over the last 50 moves.    - If this count goes above 35,
# reclassify the opponent as cooperative.    - If this count goes below 15,
# reclassify the opponent as aggressive.    - Otherwise, classify the opponent
# as neutral.  5. Continue this strategy until the end of the game (round 1000),
# without changing behavior in the final rounds.  This revised strategy: - Is
# simpler and clearer about when to cooperate or defect. - Has a longer initial
# assessment period for better opponent classification. - Maintains a
# cooperative approach throughout, including the end-game. - Uses a continuous
# reassessment method to adapt to changes in opponent behavior. - Adjusts the
# generous Tit-for-Tat to be slightly less forgiving. - Is robust against
# different opponent types while remaining fundamentally cooperative.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.opponent_type = None
          self.rolling_cooperation_count = 0
          self.cooperative_defect_flag = False
  
      if len(self.history) < 20:
          return axl.Action.C
  
      if len(self.history) == 20:
          cooperations = opponent.history.cooperations
          self.rolling_cooperation_count = cooperations
          if cooperations >= 14:
              self.opponent_type = "cooperative"
          elif cooperations <= 6:
              self.opponent_type = "aggressive"
          else:
              self.opponent_type = "neutral"
  
      # Update rolling cooperation count
      if len(self.history) > 50:
          self.rolling_cooperation_count += int(opponent.history[-1] == axl.Action.C)
          self.rolling_cooperation_count -= int(opponent.history[-51] == axl.Action.C)
  
      # Reassess opponent type
      if self.rolling_cooperation_count > 35:
          self.opponent_type = "cooperative"
      elif self.rolling_cooperation_count < 15:
          self.opponent_type = "aggressive"
      else:
          self.opponent_type = "neutral"
  
      if self.opponent_type == "cooperative":
          if opponent.history[-1] == axl.Action.C:
              self.cooperative_defect_flag = False
              return axl.Action.C
          else:
              if self.cooperative_defect_flag:
                  self.cooperative_defect_flag = False
                  return axl.Action.C
              else:
                  self.cooperative_defect_flag = True
                  return axl.Action.D
  
      if self.opponent_type == "aggressive":
          return opponent.history[-1]
  
      if self.opponent_type == "neutral":
          if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
              return axl.Action.C if self._random.random() < 0.7 else axl.Action.D
          if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.C
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For the next 9 rounds, mirror
# your opponent's previous move.  3. After every 20 rounds, calculate the ratio
# of your opponent's C moves to total moves in those 20 rounds.  4. For the
# remainder of the game, make your decision based on the following conditions,
# checked in this order:     a. If you're in the last 10 rounds of the game,
# play C with a 20% probability and D with an 80% probability.     b. If your
# opponent has played D in the last 2 consecutive moves, play D.     c. If your
# opponent's C ratio (from step 3) is:       - Above 0.7: Play C with 75%
# probability, D with 25% probability.       - Below 0.3: Play D with 75%
# probability, C with 25% probability.       - Between 0.3 and 0.7: Play C with
# 60% probability, D with 40% probability.     d. If none of the above
# conditions are met, mirror your opponent's last move.  5. Repeat steps 3-4
# until the game ends.  This revised strategy: - Maintains simplicity while
# addressing key scenarios. - Starts neutrally and adapts based on the
# opponent's behavior. - Uses clearer ratios (3:1 for cooperative/aggressive,
# 3:2 for neutral) for decision making. - Reassesses the opponent's strategy
# more frequently (every 20 rounds). - Includes a safeguard against short-term
# aggressive behavior. - Adds randomness to the end-game strategy to be less
# predictable. - Is more robust against various opponent strategies while
# maintaining a slightly cooperative bias when the opponent is neutral.  The
# conditions are ordered to prioritize end-game considerations, recent
# aggressive behavior, overall opponent strategy, and then defaulting to
# mirroring if no other conditions are met.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.opponent_c_ratio = None
          return axl.Action.C
  
      if len(self.history) <= 9:
          return opponent.history[-1]
  
      if len(self.history) % 20 == 0:
          recent_history = opponent.history[-20:]
          self.opponent_c_ratio = recent_history.count(axl.Action.C) / 20
  
      if len(self.history) >= 990:
          return self._random.random_choice(0.2)
  
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      if self.opponent_c_ratio is not None:
          if self.opponent_c_ratio > 0.7:
              return self._random.random_choice(0.75)
          elif self.opponent_c_ratio < 0.3:
              return self._random.random_choice(0.25)
          elif 0.3 <= self.opponent_c_ratio <= 0.7:
              return self._random.random_choice(0.6)
  
      return opponent.history[-1]

# Here's a revised strategy that takes into account the feedback while
# maintaining simplicity and aggressiveness:  1. Start by playing D (defect) for
# the first 10 rounds to establish a strong aggressive stance.  2. After the
# initial phase, use the following rules in order:     a. If it's one of the
# last 20 rounds of the game, always play D to maximize final payoffs.        b.
# If the opponent has played C for the last 3 consecutive rounds, play C. This
# allows for some mutual cooperation if the opponent is consistently
# cooperative, without being too easily exploited.        c. If it's a multiple
# of 40 rounds (i.e., round 40, 80, 120, etc.), play C. This serves as an
# occasional "olive branch" to test for mutual cooperation possibilities.
# d. If your average score per round over the last 50 rounds is below 2, play D
# for the next 5 rounds regardless of the opponent's moves. This increases
# aggression if the current strategy is underperforming.        e. If none of
# the above conditions are met, play D.  3. Repeat step 2 for the remainder of
# the game.  This revised strategy:  - Maintains an aggressive stance by
# defaulting to D in most cases. - Is simple with clear, ordered conditions for
# when to cooperate or defect. - Provides limited but strategic opportunities
# for cooperation, potentially increasing payoffs against cooperative opponents
# without being easily exploited. - Adapts to the opponent's recent behavior and
# the game's progression. - Is robust against aggressive opponents by mostly
# playing D. - Has a clear end-game strategy. - Includes a performance check to
# increase aggression if necessary.  This strategy should perform well against
# various opponent types while maintaining its aggressive nature and simplicity.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.aggressive_counter = 0
  
      current_round = len(self.history) + 1
  
      if current_round <= 10:
          return axl.Action.D
      
      if current_round > 980:
          return axl.Action.D
      
      if self.aggressive_counter > 0:
          self.aggressive_counter -= 1
          return axl.Action.D
      
      if opponent.history[-3:].count(axl.Action.C) == 3:
          return axl.Action.C
      
      if current_round % 40 == 0:
          return axl.Action.C
      
      if current_round > 50:
          last_50_scores = self.total_scores(self.history[-50:], opponent.history[-50:])
          if last_50_scores[0] / 50 < 2:
              self.aggressive_counter = 5
              return axl.Action.D
      
      return axl.Action.D

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first 2 rounds to signal cooperative intent
# without being overly exploitable.  2. For each subsequent round, follow these
# rules in order:     a. If it's one of the last 5 rounds of the game, play D
# (defect). This prevents end-game exploitation.     b. If the opponent has
# played D for the last 3 consecutive rounds, play D. This quickly punishes
# aggressive behavior.     c. If the opponent has played C for the last 2
# consecutive rounds, play C. This rewards consistent cooperation.     d. If
# none of the above conditions are met, use the following "Adaptive Tit-for-Tat"
# approach:       - If the opponent played C in the previous round, play C.
# - If the opponent played D in the previous round, play C with probability P
# and D with probability (1-P), where P starts at 0.8 and is adjusted as
# follows:  3. Every 20 rounds, evaluate the opponent's behavior and adjust P:
# - If they have cooperated in more than 70% of the last 20 rounds, increase P
# by 0.1 (up to a maximum of 0.9).    - If they have cooperated in 30-70% of the
# last 20 rounds, keep P unchanged.    - If they have cooperated in less than
# 30% of the last 20 rounds, decrease P by 0.1 (down to a minimum of 0.5).  4.
# Reset the count for consecutive C or D plays after each evaluation or when the
# pattern is broken.  This revised strategy: - Starts cooperatively but with
# less initial vulnerability. - Responds quickly to both aggressive and
# cooperative behavior. - Adapts more frequently (every 20 rounds instead of 50)
# to opponent's overall strategy. - Has a more nuanced end-game approach to
# prevent exploitation. - Maintains simplicity while being more robust against
# various opponent types. - Clearly defines conditions for cooperation and
# defection, ordered from most specific to most general.  The strategy remains
# fundamentally cooperative but with improved defenses against exploitation and
# faster adaptation to opponent behavior. It should perform well against
# cooperative opponents, be more resilient against aggressive ones, and adapt
# effectively to neutral players.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.P = 0.8
          self.consecutive_C = 0
          self.consecutive_D = 0
          self.round_counter = 0
  
      self.round_counter += 1
  
      if self.round_counter % 20 == 0:
          recent_cooperations = opponent.history[-20:].count(axl.Action.C)
          if recent_cooperations > 14:
              self.P = min(0.9, self.P + 0.1)
          elif recent_cooperations < 6:
              self.P = max(0.5, self.P - 0.1)
          self.consecutive_C = 0
          self.consecutive_D = 0
  
      if len(self.history) < 2:
          return axl.Action.C
  
      if len(self.history) > 995:
          return axl.Action.D
  
      if self.consecutive_D >= 3:
          self.consecutive_D = 0
          self.consecutive_C = 0
          return axl.Action.D
  
      if self.consecutive_C >= 2:
          self.consecutive_C = 0
          self.consecutive_D = 0
          return axl.Action.C
  
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_C += 1
          self.consecutive_D = 0
          return axl.Action.C
      else:
          self.consecutive_D += 1
          self.consecutive_C = 0
          if self._random.random() < self.P:
              return axl.Action.C
          else:
              return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C for the first round.  2. For the next 9 rounds, mirror your
# opponent's previous move.  3. After the first 10 rounds, and every 25 rounds
# thereafter, assess your opponent's behavior based on their last 25 moves:    -
# If they've played C more than 60% of the time, consider them cooperative.    -
# If they've played D more than 60% of the time, consider them aggressive.    -
# Otherwise, consider them neutral.  4. Based on this assessment, adjust your
# strategy for the next 25 rounds:    - If cooperative: Play C 70% of the time
# and D 30% of the time.    - If aggressive: Play D 70% of the time and C 30% of
# the time.    - If neutral: Play C 50% of the time and D 50% of the time.  5.
# Regardless of the overall strategy, always apply these rules in order:    a.
# If your opponent has played D three times in a row, play D for the next two
# rounds.    b. If you're in the last 50 rounds of the game, increase your
# defection probability by 2% each round (capped at 90% D).    c. If it's the
# final round, always play D.  6. If none of the conditions in step 5 apply,
# play according to the probabilities determined in step 4.  This revised
# strategy aims to be more neutral and adaptive while remaining simple. It
# addresses the previous bias towards cooperation, provides clearer conditions
# for cooperation and defection, and offers a more gradual end-game adjustment.
# The strategy should be more robust against various opponent types while
# maintaining a balanced approach throughout most of the game.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.assessment = "neutral"
          self.assessment_counter = 0
          self.defect_counter = 0
          return axl.Action.C
  
      current_round = len(self.history) + 1
      rounds_left = 1000 - current_round
  
      if current_round <= 10:
          return opponent.history[-1]
  
      self.assessment_counter += 1
  
      if self.assessment_counter % 25 == 0:
          last_25_moves = opponent.history[-25:]
          c_ratio = last_25_moves.count(axl.Action.C) / 25
  
          if c_ratio > 0.6:
              self.assessment = "cooperative"
          elif c_ratio < 0.4:
              self.assessment = "aggressive"
          else:
              self.assessment = "neutral"
  
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.defect_counter = 2
  
      if self.defect_counter > 0:
          self.defect_counter -= 1
          return axl.Action.D
  
      if rounds_left <= 50:
          defect_prob = min(0.9, 0.5 + (50 - rounds_left) * 0.02)
          if self._random.random() < defect_prob:
              return axl.Action.D
  
      if rounds_left == 1:
          return axl.Action.D
  
      if self.assessment == "cooperative":
          return self._random.choice([axl.Action.C] * 7 + [axl.Action.D] * 3)
      elif self.assessment == "aggressive":
          return self._random.choice([axl.Action.C] * 3 + [axl.Action.D] * 7)
      else:
          return self._random.choice([axl.Action.C, axl.Action.D])

# Here's a revised, simpler, and more responsive strategy that takes into
# account the feedback:  1. Start by playing D (defect) for the first 10 rounds
# to establish an aggressive stance.  2. After the initial 10 rounds, follow
# these rules in order:     a. If the opponent has cooperated (C) for the last 3
# consecutive rounds, play C.        b. If the opponent has defected (D) for the
# last 3 consecutive rounds, play D.        c. If it's one of the last 50 rounds
# of the game, play D.        d. If the opponent's cooperation rate over the
# last 20 rounds is above 70%, play C.        e. Otherwise, play D.  3. Every 50
# rounds, play C once to test for potential shifts in the opponent's strategy,
# regardless of the above rules.  This strategy is aggressive by default but can
# quickly adapt to cooperative behavior. It's simpler than the previous version
# and more responsive to recent changes in the opponent's strategy. Here's how
# it addresses the different opponent types:  - Against aggressive opponents: It
# will mostly defect, matching their aggression. - Against cooperative
# opponents: It can switch to cooperation relatively quickly if the opponent
# shows consistent cooperative behavior. - Against neutral or mixed strategy
# opponents: It maintains a primarily aggressive stance but can adapt if the
# opponent shows a tendency towards cooperation.  The strategy is now more
# straightforward, with clear conditions for cooperation and defection, ordered
# from most specific to most general. It removes the complex time-based rules
# and long evaluation periods, making it more responsive to short-term changes
# in opponent behavior while maintaining an overall aggressive approach.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.test_cooperation_round = 49
  
      if len(self.history) < 10:
          return axl.Action.D
  
      if len(self.history) == self.test_cooperation_round:
          self.test_cooperation_round += 50
          return axl.Action.C
  
      if len(opponent.history) >= 3:
          if opponent.history[-3:] == [axl.Action.C] * 3:
              return axl.Action.C
          if opponent.history[-3:] == [axl.Action.D] * 3:
              return axl.Action.D
  
      if len(self.history) > 950:
          return axl.Action.D
  
      if len(opponent.history) >= 20:
          recent_cooperation_rate = opponent.history[-20:].count(axl.Action.C) / 20
          if recent_cooperation_rate > 0.7:
              return axl.Action.C
  
      return axl.Action.D

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. For the remaining rounds, follow
# these rules in order:     a. If it's the last 20 rounds of the game:       -
# Calculate the opponent's cooperation rate for the last 100 rounds.       - If
# their cooperation rate is above 70%, play C.       - Otherwise, play D with a
# probability equal to (1 - their cooperation rate).     b. If the opponent has
# defected in the last 3 consecutive rounds:       - Play D with 80%
# probability, C with 20% probability.     c. If you've played D in the last 2
# consecutive rounds:       - Play C to attempt to reset cooperation.     d. If
# it's a multiple of 50 rounds (50, 100, 150, etc.):       - Reassess the
# opponent's behavior using the last 50 rounds:       - Calculate their
# cooperation rate (CR) = (number of C plays) / 50       - Update your
# cooperation threshold (CT) as follows:         * If CR > 0.7, set CT = 0.8
# * If 0.3 ≤ CR ≤ 0.7, set CT = 0.6         * If CR < 0.3, set CT = 0.4     e.
# For all other rounds:       - Play C if the opponent's last move was C and a
# random number (0-1) is less than your current cooperation threshold (CT).
# - Otherwise, play D.  3. After each round, update your record of the
# opponent's moves and your own moves.  This revised strategy addresses the
# previous feedback by:  1. Simplifying the overall structure while maintaining
# adaptability. 2. Using a more flexible approach to determine cooperation based
# on the opponent's behavior. 3. Introducing controlled randomness to make the
# strategy less predictable. 4. Implementing a more nuanced end-game strategy.
# 5. Providing a mechanism to potentially recover from mutual defection. 6.
# Maintaining a cooperative stance when faced with a cooperative opponent. 7.
# Adapting more smoothly to different opponent types (aggressive, cooperative,
# or neutral).  The strategy remains fundamentally cooperative, starting with
# cooperation and maintaining high cooperation thresholds when the opponent is
# cooperative. It becomes more defensive when faced with consistent defection
# but always maintains a chance to return to cooperation. The periodic
# reassessment allows for long-term adaptation to the opponent's overall
# strategy.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.cooperation_threshold = 0.6
          self.opponent_coop_rate = 0.5
          return axl.Action.C
  
      total_rounds = len(self.history)
      if total_rounds > 980:
          self.opponent_coop_rate = opponent.history[-100:].count(axl.Action.C) / 100
          if self.opponent_coop_rate > 0.7:
              return axl.Action.C
          elif self._random.random() < (1 - self.opponent_coop_rate):
              return axl.Action.D
          else:
              return axl.Action.C
  
      if opponent.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.D if self._random.random() < 0.8 else axl.Action.C
  
      if self.history[-2:].count(axl.Action.D) == 2:
          return axl.Action.C
  
      if total_rounds % 50 == 0:
          self.opponent_coop_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if self.opponent_coop_rate > 0.7:
              self.cooperation_threshold = 0.8
          elif 0.3 <= self.opponent_coop_rate <= 0.7:
              self.cooperation_threshold = 0.6
          else:
              self.cooperation_threshold = 0.4
  
      if opponent.history[-1] == axl.Action.C and self._random.random() < self.cooperation_threshold:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a revised, simplified strategy that takes into account the feedback:
# 1. Start by playing C (cooperate) for the first round.  2. For the subsequent
# rounds, base your decision on the following conditions, checked in this order:
# a) If your opponent has played D (defect) for the last 3 consecutive rounds,
# play D.        b) Otherwise, consider your opponent's behavior in the last 20
# rounds:       - Calculate the percentage of C plays by your opponent in these
# 20 rounds.       - If this percentage is less than 40%, play D with 70%
# probability and C with 30% probability.       - If this percentage is more
# than 60%, play C with 70% probability and D with 30% probability.       - If
# the percentage is between 40% and 60% (inclusive), play C with 55% probability
# and D with 45% probability.  3. If there have been fewer than 20 rounds
# played, simply mirror your opponent's last move.  This strategy is simpler and
# more neutral, while still adapting to different opponent behaviors:  - It's
# more responsive to recent behavior by considering only the last 20 rounds. -
# It removes complex rules about reassessment periods and catch-up mechanisms. -
# It maintains a slight bias towards cooperation (55% C vs 45% D) when the
# opponent is neutral, encouraging mutual cooperation without being overly
# exploitable. - It responds quickly to streaks of defection to protect against
# aggressive opponents. - It doesn't have any end-game changes, maintaining
# consistent behavior throughout.  This strategy should be robust against
# various opponent types: - Against cooperative opponents, it will mostly
# cooperate but occasionally defect. - Against aggressive opponents, it will
# quickly shift to mostly defecting. - Against neutral opponents, it will
# maintain a nearly balanced approach with a slight lean towards cooperation.
# The strategy is adaptive but not overly complex, making it harder for
# opponents to exploit while still being responsive to changes in opponent
# behavior.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          return axl.Action.D
      
      if len(self.history) >= 20:
          recent_history = opponent.history[-20:]
          coop_percentage = recent_history.count(axl.Action.C) / 20
          
          if coop_percentage < 0.4:
              return self._random.random_choice(0.3)
          elif coop_percentage > 0.6:
              return self._random.random_choice(0.7)
          else:
              return self._random.random_choice(0.55)
      
      if opponent.history:
          return opponent.history[-1]
      else:
          return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. For the first
# 3 rounds, play D (defect). This establishes an initial aggressive stance
# without being overly punishing.  2. After the first 3 rounds, use the
# following decision tree in order:     a. If it's one of the last 10 rounds of
# the game, play D.        b. If the opponent has played D in both of their last
# two moves, play D.        c. If you've played C in your last two moves and the
# opponent defected in their last move, play D.        d. If the opponent has
# played C in their last two moves, play C.        e. If it's a multiple of 40
# rounds (40, 80, 120, etc.), play D. This maintains periodic aggression.
# f. Otherwise, copy the opponent's last move (Tit-for-Tat).  3. Every 100
# rounds, calculate the score difference. If you're behind by 15 points or more,
# play D for the next 5 rounds, then resume the main strategy.  This revised
# strategy is simpler, clearer, and addresses the main points of feedback:  -
# It's still aggressive but not overly so at the start. - It has clear,
# prioritized conditions for cooperation and defection. - It maintains periodic
# aggression every 40 rounds instead of 50, allowing for more aggressive plays
# in the 1000-round game. - It considers the total number of rounds by changing
# strategy for the last 10 rounds. - The score difference check is less frequent
# and the threshold is lower, making it more relevant and less likely to lead to
# overly defensive play. - It's robust against various opponent types: it can
# exploit cooperative opponents, protect against aggressive ones, and adapt to
# neutral strategies.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.last_score_check = 0
          self.aggressive_rounds = 0
  
      turn = len(self.history)
  
      if turn < 3:
          return axl.Action.D
  
      if self.aggressive_rounds > 0:
          self.aggressive_rounds -= 1
          return axl.Action.D
  
      if turn % 100 == 0 and turn > 0:
          if self.score - opponent.score <= -15:
              self.aggressive_rounds = 5
              return axl.Action.D
  
      if turn >= 990:
          return axl.Action.D
  
      if opponent.history[-2:].count(axl.Action.D) == 2:
          return axl.Action.D
  
      if self.history[-2:].count(axl.Action.C) == 2 and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      if opponent.history[-2:].count(axl.Action.C) == 2:
          return axl.Action.C
  
      if turn % 40 == 0:
          return axl.Action.D
  
      return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) for the first 5 rounds to signal willingness to
# cooperate.  2. For each subsequent round, determine your move in the following
# order:     a. If it's one of the last 20 rounds of the game, play according to
# step 2b-e.        b. If the opponent has defected in more than 70% of the last
# 50 rounds:       - Play D (defect) if the opponent played D in the previous
# round.       - Play C if the opponent played C in the previous round.
# c. If you and your opponent have both played D for the last 5 consecutive
# rounds:       - Play C for this round only, then return to the main strategy.
# d. If the opponent played C in the previous round:       - Play C.        e.
# If the opponent played D in the previous round:       - Play C with 70%
# probability and D with 30% probability.  3. Every 50 rounds, evaluate your
# opponent's behavior:    - If they have cooperated in more than 70% of these
# rounds, continue with the current strategy.    - If they have cooperated in
# 30-70% of these rounds, continue with the current strategy.    - If they have
# cooperated in less than 30% of these rounds, switch to the strategy described
# in step 2b for the next 50 rounds.  This revised strategy maintains a
# cooperative approach while being more robust against aggressive opponents.
# It's simpler and clearer about when to cooperate or defect. The strategy:  1.
# Starts cooperatively to encourage mutual cooperation. 2. Uses a modified Tit-
# for-Tat approach against highly uncooperative opponents. 3. Attempts to break
# out of mutual defection cycles cautiously. 4. Maintains a generous but more
# cautious approach to occasional defections. 5. Periodically evaluates the
# opponent's behavior and adapts accordingly. 6. Avoids end-game exploitation by
# maintaining its strategy in the final rounds.  This strategy should perform
# well against cooperative and neutral opponents while being more resilient
# against aggressive ones. It remains fundamentally cooperative but with
# improved self-protection mechanisms.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.defection_threshold = 35
          self.evaluation_counter = 0
  
      if len(self.history) < 5:
          return axl.Action.C
  
      recent_50 = opponent.history[-50:]
      defection_count = recent_50.count(axl.Action.D)
  
      self.evaluation_counter += 1
      if self.evaluation_counter == 50:
          cooperation_rate = recent_50.count(axl.Action.C) / 50
          if cooperation_rate < 0.3:
              self.defection_threshold = 0
          elif cooperation_rate > 0.7:
              self.defection_threshold = 35
          else:
              self.defection_threshold = 35
          self.evaluation_counter = 0
  
      if defection_count > self.defection_threshold:
          return axl.Action.D if opponent.history[-1] == axl.Action.D else axl.Action.C
  
      if len(self.history) >= 5 and all(move == axl.Action.D for move in self.history[-5:]) and \
         all(move == axl.Action.D for move in opponent.history[-5:]):
          return axl.Action.C
  
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.C if self._random.random() < 0.7 else axl.Action.D
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For the next 9 rounds, mirror
# your opponent's previous move.  3. After every 20 rounds, calculate the
# frequency of your opponent's C and D plays in those 20 rounds:    - If they've
# played C more than 60% of the time, consider them cooperative.    - If they've
# played D more than 60% of the time, consider them aggressive.    - Otherwise,
# consider them neutral.  4. For each subsequent round, make your decision in
# this order:     a. If you're in the last 20 rounds of the game, play D.
# b. If your opponent has played D in the last 2 consecutive rounds, play D.
# c. If your opponent is categorized as aggressive:       - Play D with 80%
# probability       - Play C with 20% probability        d. If your opponent is
# categorized as cooperative:       - Play C with 80% probability       - Play D
# with 20% probability        e. If your opponent is categorized as neutral:
# - Play C with 60% probability       - Play D with 40% probability  5. If none
# of the above conditions are met, play C.  This revised strategy: - Remains
# relatively simple and starts neutrally. - Adapts more frequently (every 20
# rounds instead of 100) to catch shorter-term strategy shifts. - Uses a lower
# threshold (60% instead of 70%) for categorizing opponents, allowing for
# quicker adaptation. - Responds more quickly to defection (2 consecutive D's
# instead of 3). - Adjusts the cooperation/defection probabilities to be less
# exploitable while still encouraging cooperation. - Extends the end-game
# defection to 20 rounds, making it less predictable. - Clearly prioritizes the
# conditions for cooperation or defection. - Implicitly accounts for the game's
# payoff structure by favoring cooperation with cooperative opponents (as mutual
# cooperation yields higher payoffs than mutual defection).  This strategy
# should be more robust against various opponent types while maintaining a
# neutral overall approach. It balances the potential for high mutual
# cooperation payoffs with protection against exploitation.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
  
      if len(self.history) <= 10:
          return opponent.history[-1]
  
      if len(self.history) % 20 == 0:
          last_20_opponent_moves = opponent.history[-20:]
          c_frequency = last_20_opponent_moves.count(axl.Action.C) / 20
          if c_frequency > 0.6:
              self.opponent_category = "cooperative"
          elif c_frequency < 0.4:
              self.opponent_category = "aggressive"
          else:
              self.opponent_category = "neutral"
  
      if len(self.history) > 980:
          return axl.Action.D
  
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      if 'opponent_category' in vars(self):
          if self.opponent_category == "aggressive":
              return self._random.random_choice(0.2)
          elif self.opponent_category == "cooperative":
              return self._random.random_choice(0.8)
          elif self.opponent_category == "neutral":
              return self._random.random_choice(0.6)
  
      return axl.Action.C

# Here's a revised, simplified, and more aggressive strategy that takes into
# account the feedback:  1. Start by playing D (defect) for the first 5 rounds.
# 2. For the remainder of the game, use the following decision-making process in
# order:     a. If it's one of the last 50 rounds of the game, always play D.
# b. If the opponent has played D in 3 or more of the last 5 rounds, play D.
# c. If you've played C in the last round and the opponent played D, play D.
# d. If both you and the opponent have played C for the last 3 consecutive
# rounds, play D.        e. If none of the above conditions are met, play C.  3.
# Every 50 rounds (on rounds 50, 100, 150, etc.), play D regardless of other
# conditions.  This strategy is simpler and more aggressive than the previous
# version. Here's how it addresses the key points:  - It's more straightforward,
# with clear conditions for when to defect or cooperate. - It's generally more
# aggressive, defaulting to defection in more scenarios. - It's more responsive
# to the opponent's recent moves, using a sliding window of the last 5 rounds. -
# It exploits cooperation by defecting after 3 rounds of mutual cooperation. -
# It punishes defection quickly and harshly. - It has a clear end-game strategy,
# always defecting in the last 50 rounds. - It maintains periodic aggression
# with the every-50-rounds defection.  This strategy should be robust against
# different types of opponents:  - Against aggressive opponents, it will quickly
# switch to consistent defection. - Against cooperative opponents, it will
# exploit their cooperation while still occasionally cooperating to maintain
# some mutual benefit. - Against neutral opponents, it will tend towards
# defection while still being responsive to cooperation.  The strategy is now
# more clearly defined, easier to implement, and more consistently aggressive
# while still retaining some flexibility to adapt to the opponent's play style.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.last_50_rounds = False
  
      if len(self.history) < 5:
          return axl.Action.D
  
      if len(self.history) >= 950 and not self.last_50_rounds:
          self.last_50_rounds = True
  
      if len(self.history) % 50 == 0:
          return axl.Action.D
  
      if self.last_50_rounds:
          return axl.Action.D
  
      if opponent.history[-5:].count(axl.Action.D) >= 3:
          return axl.Action.D
  
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      if self.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C] and opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.D
  
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) for the first 3 rounds to signal willingness to
# cooperate.  2. For the remainder of the game, follow these rules in order:
# a. If it's one of the last 10 rounds of the game, play C.        b. If it's a
# multiple of 50 rounds (50, 100, 150, etc.), play C for this round and the next
# to attempt re-establishing cooperation.        c. If the opponent has played D
# more than 60% of the time in the last 20 rounds, use Tit-for-Tat for the next
# 20 rounds:       - Play whatever move your opponent played in the previous
# round.        d. If not in Tit-for-Tat mode, use a modified Tit-for-Two-Tats
# approach:       - Play D if the opponent played D in both of the last two
# rounds.       - Otherwise, play C.  3. After each round, update your record of
# the opponent's moves for use in future decisions.  This strategy will
# cooperate (play C) when: - It's one of the first 3 rounds of the game. - It's
# one of the last 10 rounds of the game. - It's a "cooperation attempt" round
# (every 50th round and the one following). - The opponent hasn't defected in
# both of the last two rounds (unless in Tit-for-Tat mode). - It's matching the
# opponent's previous move during a Tit-for-Tat phase and the opponent
# cooperated.  The strategy will defect (play D) when: - The opponent has
# defected in both of the last two rounds (unless it's a "cooperation attempt"
# round or one of the last 10 rounds). - It's matching the opponent's previous
# move during a Tit-for-Tat phase and the opponent defected.  This revised
# strategy maintains its cooperative nature while being more robust against
# various opponent behaviors. It's simpler, with clearer conditions for
# cooperation and defection, and addresses the main points of feedback from the
# critique.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.tit_for_tat_mode = False
          self.tit_for_tat_rounds = 0
  
      if len(self.history) < 3:
          return axl.Action.C
  
      if len(self.history) > 990:
          return axl.Action.C
  
      if len(self.history) % 50 == 0 or len(self.history) % 50 == 1:
          self.tit_for_tat_mode = False
          self.tit_for_tat_rounds = 0
          return axl.Action.C
  
      recent_defection_rate = opponent.history[-20:].count(axl.Action.D) / 20
      if recent_defection_rate > 0.6 and not self.tit_for_tat_mode:
          self.tit_for_tat_mode = True
          self.tit_for_tat_rounds = 0
  
      if self.tit_for_tat_mode:
          self.tit_for_tat_rounds += 1
          if self.tit_for_tat_rounds >= 20:
              self.tit_for_tat_mode = False
              self.tit_for_tat_rounds = 0
          return opponent.history[-1]
  
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. For each subsequent round,
# follow these rules in order:     a. If it's one of the last 10 rounds
# (991-1000), play D (defect).        b. Calculate the opponent's cooperation
# rate over the last 5 rounds.        c. If the opponent's 5-round cooperation
# rate is:       - 80% or higher (cooperated 4 or 5 times): Play C with 90%
# probability, D with 10% probability.       - Between 40% and 80% (cooperated 2
# or 3 times): Play C with 50% probability, D with 50% probability.       -
# Below 40% (cooperated 0 or 1 time): Play D with 90% probability, C with 10%
# probability.        d. If it's a multiple of 20 rounds (20, 40, 60, etc.),
# play the opposite of what the above rules suggest. This adds unpredictability
# and allows for strategy reassessment.  3. Exception: If the opponent has
# defected in the last 3 rounds consecutively, play D regardless of the above
# rules (except for rule 2d). This helps to quickly punish aggressive behavior.
# 4. If the opponent switches from defection to cooperation (i.e., they defected
# in the previous round but cooperated in the last round), play C. This
# encourages a return to cooperation.  This revised strategy: - Is simpler and
# clearer about when to cooperate or defect. - Adapts more quickly to changes in
# opponent behavior by using a 5-round window. - Maintains neutrality by
# defaulting to a 50/50 split against neutral opponents. - Is more robust
# against aggressive opponents with the 3-round defection punishment. - Allows
# for recovery of cooperation with rule 4. - Adds unpredictability with the
# every-20-rounds rule. - Maintains the end-game defection protection.  The
# strategy remains adaptive to different opponent types while being more
# responsive to recent behavior changes. It also introduces a mechanism to
# potentially influence the opponent's strategy through quick punishment and
# forgiveness.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First move: Cooperate
      if not self.history:
          return axl.Action.C
  
      # Last 10 rounds: Always defect
      if len(self.history) > 990:
          return axl.Action.D
  
      # Calculate opponent's cooperation rate over last 5 rounds
      if len(self.history) >= 5:
          coop_rate = opponent.history[-5:].count(axl.Action.C) / 5
          if coop_rate >= 0.8:
              action = axl.Action.C if self._random.random() < 0.9 else axl.Action.D
          elif 0.4 <= coop_rate < 0.8:
              action = axl.Action.C if self._random.random() < 0.5 else axl.Action.D
          else:
              action = axl.Action.D if self._random.random() < 0.9 else axl.Action.C
      else:
          # Default to Cooperate for first 4 rounds
          action = axl.Action.C
  
      # Exception: Opponent defected last 3 rounds
      if len(self.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          action = axl.Action.D
  
      # Encourage return to cooperation
      if len(self.history) >= 2 and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          action = axl.Action.C
  
      # Every 20 rounds: Play opposite
      if len(self.history) % 20 == 0:
          action = axl.Action.D if action == axl.Action.C else axl.Action.C
  
      return action

# Here's a revised, simplified strategy that takes into account the feedback:
# 1. Start by playing D (defect) for the first 5 rounds to establish an
# aggressive stance.  2. For the next 15 rounds, play tit-for-tat (copy the
# opponent's previous move) to quickly assess their strategy.  3. After these
# initial 20 rounds, adopt the following rules in order:     a. If the opponent
# has cooperated in the last 3 consecutive rounds, defect (D) to exploit their
# cooperation.        b. If the opponent has defected more than 70% of the time
# in the last 20 moves, defect (D) to protect against aggressive play.        c.
# If the opponent's last move was cooperate (C), defect (D) to capitalize on
# their cooperation.        d. If none of the above conditions are met,
# cooperate (C) to potentially induce cooperation from the opponent.  4. Every
# 50 rounds, reassess the opponent's overall strategy:    - If they've
# cooperated more than 60% of the time, increase the threshold in rule 3b to 80%
# to be more exploitative.    - If they've defected more than 60% of the time,
# decrease the threshold in rule 3b to 60% to be more defensive.  5. In the last
# 100 rounds, regardless of the opponent's strategy, always defect (D) to
# maximize final payoff.  This revised strategy is simpler, more aggressive, and
# more responsive to the opponent's behavior. It maintains an overall aggressive
# stance while having clear conditions for when to cooperate or defect. The
# strategy should be robust against various opponent types:  - Against
# aggressive opponents: It will quickly adopt a defensive, always-defect
# strategy. - Against cooperative opponents: It will exploit their cooperation
# by frequently defecting. - Against neutral opponents: It will adapt its level
# of cooperation based on the opponent's recent moves, with a bias towards
# defection.  The strategy is now more dynamic, adjusting quickly to changes in
# the opponent's play style, and it removes the predictable alternating pattern
# from the previous version. The ordered conditions provide a clear decision-
# making process, making the strategy easier to implement and understand.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if len(self.history) == 0:
          self.defect_threshold = 0.7
      
      if len(self.history) < 5:
          return axl.Action.D
      
      if len(self.history) < 20:
          return opponent.history[-1]
      
      if len(self.history) >= 900:
          return axl.Action.D
      
      if len(self.history) % 50 == 0:
          recent_history = opponent.history[-100:]
          coop_rate = recent_history.count(axl.Action.C) / len(recent_history)
          if coop_rate > 0.6:
              self.defect_threshold = 0.8
          elif coop_rate < 0.4:
              self.defect_threshold = 0.6
      
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.D
      
      recent_defections = opponent.history[-20:].count(axl.Action.D)
      if recent_defections / 20 > self.defect_threshold:
          return axl.Action.D
      
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For the next 9 rounds, use Tit-
# for-Tat:    - Play C if the opponent played C in the previous round.    - Play
# D if the opponent played D in the previous round.  3. After every 10 rounds,
# evaluate the opponent's behavior:    - Calculate the percentage of C plays by
# the opponent in the last 10 rounds.    - If ≥ 70% C, consider them
# cooperative.    - If ≤ 30% C, consider them aggressive.    - Otherwise,
# consider them neutral.  4. For the remaining rounds, play according to these
# ordered conditions:     a) If the opponent has defected in the last 3
# consecutive rounds:       - Play D.     b) If you're in a "forgiveness" phase
# (after 3 consecutive D plays):       - Play C for the next 2 rounds,
# regardless of opponent's moves.       - If opponent plays C in both rounds,
# exit "forgiveness" phase.       - If opponent plays D in either round, return
# to condition (a).     c) If opponent is classified as cooperative:       -
# Play C.     d) If opponent is classified as aggressive:       - Play D with
# 70% probability, C with 30% probability.     e) If opponent is classified as
# neutral:       - Use Tit-for-Two-Tats: Play D only if the opponent has played
# D in the last two consecutive rounds.     f) If none of the above conditions
# are met:       - Play C.  5. Special considerations:    - In the last 10
# rounds of the game, continue with the above strategy without changes.    -
# Reset the consecutive D count to 0 whenever you or your opponent plays C.
# This revised strategy: - Maintains a cooperative approach while being more
# robust against various opponent behaviors. - Uses a more lenient
# classification system for opponent behavior. - Implements a "forgiveness"
# mechanism to recover from mutual defection. - Provides a probabilistic
# approach against aggressive opponents, offering more opportunities for
# cooperation. - Removes the end-game defection, maintaining consistent behavior
# throughout. - Clearly defines conditions for cooperation and defection,
# ordered from most specific to most general.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_d_count = 0
          self.forgiveness_phase = False
          self.forgiveness_rounds = 0
          self.opponent_type = None
          return axl.Action.C
  
      if len(self.history) < 10:
          return opponent.history[-1] if self.history else axl.Action.C
  
      if len(self.history) % 10 == 0:
          c_percentage = opponent.history[-10:].count(axl.Action.C) / 10
          if c_percentage >= 0.7:
              self.opponent_type = "cooperative"
          elif c_percentage <= 0.3:
              self.opponent_type = "aggressive"
          else:
              self.opponent_type = "neutral"
  
      if opponent.history[-1] == axl.Action.C or self.history[-1] == axl.Action.C:
          self.consecutive_d_count = 0
      elif opponent.history[-1] == axl.Action.D:
          self.consecutive_d_count += 1
  
      if self.consecutive_d_count >= 3:
          self.forgiveness_phase = True
          self.forgiveness_rounds = 0
          return axl.Action.D
  
      if self.forgiveness_phase:
          self.forgiveness_rounds += 1
          if self.forgiveness_rounds <= 2:
              if opponent.history[-1] == axl.Action.D:
                  self.forgiveness_phase = False
                  self.consecutive_d_count = 3
                  return axl.Action.D
              if self.forgiveness_rounds == 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
                  self.forgiveness_phase = False
              return axl.Action.C
          self.forgiveness_phase = False
  
      if self.opponent_type == "cooperative":
          return axl.Action.C
  
      if self.opponent_type == "aggressive":
          return self._random.random_choice(0.3)
  
      if self.opponent_type == "neutral":
          if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
  
      return axl.Action.C

# Thank you for the opportunity to improve the strategy. Here's a revised
# version that takes into account the feedback:  1. Start by playing C
# (cooperate) in the first round.  2. For rounds 2-10, mirror your opponent's
# previous move (if they played C, you play C; if they played D, you play D).
# 3. After every 20 rounds, evaluate your opponent's behavior based on their
# last 20 moves:    - If they played C more than 60% of the time, consider them
# cooperative.    - If they played D more than 60% of the time, consider them
# aggressive.    - Otherwise, consider them neutral.  4. For the remaining
# rounds, choose your move based on the following conditions, checked in this
# order:     a. If it's one of the last 10 rounds of the game, play D.        b.
# If your opponent has played D in the last 3 consecutive rounds, play D.
# c. Based on your most recent evaluation of your opponent:       - If they're
# cooperative: Play C with 80% probability, D with 20% probability.       - If
# they're aggressive: Play D with 80% probability, C with 20% probability.
# - If they're neutral: Play C with 50% probability, D with 50% probability.  5.
# To implement probabilities, use a random number generator. For example, for
# 80% C and 20% D, generate a random number between 1 and 100. Play C if the
# number is 80 or below, D if it's above 80.  This revised strategy addresses
# the previous critiques by: - Simplifying the overall structure - Clarifying
# how to implement probabilistic choices - Increasing the frequency of opponent
# behavior assessment - Adjusting the response to neutral opponents to be truly
# neutral (50/50) - Ordering the conditions clearly to avoid ambiguity -
# Maintaining adaptability to different opponent types - Keeping end-game
# protection  The strategy remains relatively simple while being more robust
# against various opponent types. It maintains a neutral stance overall,
# adapting to the opponent's behavior without overly complex rules.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.opponent_type = "neutral"
          return axl.Action.C
      
      if len(self.history) < 10:
          return opponent.history[-1]
      
      if len(self.history) % 20 == 0:
          last_20_opponent_moves = opponent.history[-20:]
          cooperation_rate = last_20_opponent_moves.count(axl.Action.C) / 20
          if cooperation_rate > 0.6:
              self.opponent_type = "cooperative"
          elif last_20_opponent_moves.count(axl.Action.D) / 20 > 0.6:
              self.opponent_type = "aggressive"
          else:
              self.opponent_type = "neutral"
      
      if len(self.history) > 990:
          return axl.Action.D
      
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
      
      if self.opponent_type == "cooperative":
          return axl.Action.C if self._random.random() < 0.8 else axl.Action.D
      elif self.opponent_type == "aggressive":
          return axl.Action.D if self._random.random() < 0.8 else axl.Action.C
      else:
          return axl.Action.C if self._random.random() < 0.5 else axl.Action.D


Aggressive_ranks = [
'Aggressive_10',
'Aggressive_2',
'Aggressive_5',
'Aggressive_7',
'Aggressive_6',
'Aggressive_1',
'Aggressive_3',
'Aggressive_9',
'Aggressive_8',
'Aggressive_4',
]

Cooperative_ranks = [
'Cooperative_1',
'Cooperative_4',
'Cooperative_10',
'Cooperative_5',
'Cooperative_3',
'Cooperative_9',
'Cooperative_8',
'Cooperative_2',
'Cooperative_7',
'Cooperative_6',
]

Neutral_ranks = [
'Neutral_4',
'Neutral_9',
'Neutral_6',
'Neutral_8',
'Neutral_7',
'Neutral_1',
'Neutral_5',
'Neutral_10',
'Neutral_3',
'Neutral_2',
]