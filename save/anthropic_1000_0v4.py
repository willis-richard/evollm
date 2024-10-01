import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing D (defect) for the first 5 rounds to establish an aggressive stance.
# 2. For the remaining 995 rounds, evaluate the opponent's behavior every 10
# rounds and apply the following rules in order:     a. If it's the last 50
# rounds of the game, play D with 95% probability and C with 5% probability to
# maintain aggression while introducing slight unpredictability.     b. If the
# opponent has cooperated in 70% or more of the last 20 rounds, play D to
# exploit their cooperation.     c. If the opponent has defected in 70% or more
# of the last 20 rounds, play D to avoid being exploited.     d. If there has
# been mutual defection (both players playing D) for the last 10 consecutive
# rounds, play C once to test if the opponent is willing to cooperate, then
# revert to D in the next round regardless of the opponent's response.     e. If
# the opponent's moves show a detectable pattern over the last 20 rounds (e.g.,
# alternating C and D), play the move that best exploits this pattern in the
# next round.     f. If none of the above conditions are met, play D with 90%
# probability and C with 10% probability to maintain an aggressive stance while
# occasionally testing for cooperation and introducing unpredictability.  3.
# After each move, update the record of the opponent's behavior for future
# evaluation.  This strategy: - Maintains an overall aggressive approach -
# Adapts more quickly to the opponent's behavior (every 10 rounds) - Exploits
# highly cooperative opponents - Protects against highly aggressive opponents -
# Occasionally attempts to break out of mutual defection cycles - Tries to
# exploit detectable patterns in the opponent's play - Introduces an element of
# unpredictability to avoid being exploited - Has a slightly different endgame
# strategy that maintains aggression but isn't entirely predictable  The
# conditions are ordered from most specific to most general, ensuring that the
# most appropriate action is taken based on the current game state and opponent
# behavior.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.pattern_buffer = []
          self.mutual_defection_count = 0
          return axl.Action.D
  
      history_length = len(self.history)
  
      if history_length < 5:
          return axl.Action.D
  
      if history_length >= 950:
          return self._random.random_choice(0.95)
  
      if history_length % 10 == 0:
          last_20_opponent = opponent.history[-20:]
          opponent_coop_rate = last_20_opponent.count(axl.Action.C) / 20
  
          if opponent_coop_rate >= 0.7:
              return axl.Action.D
  
          if opponent_coop_rate <= 0.3:
              return axl.Action.D
  
          if self.mutual_defection_count >= 10:
              self.mutual_defection_count = 0
              return axl.Action.C
  
          self.pattern_buffer = last_20_opponent[-10:]
          if len(set(self.pattern_buffer)) <= 2:
              if self.pattern_buffer == [axl.Action.C, axl.Action.D] * 5 or self.pattern_buffer == [axl.Action.D, axl.Action.C] * 5:
                  return axl.Action.D
              elif self.pattern_buffer == [axl.Action.C] * 10:
                  return axl.Action.D
              elif self.pattern_buffer == [axl.Action.D] * 10:
                  return axl.Action.D
  
      if self.mutual_defection_count == 1:
          return axl.Action.D
  
      if history_length > 0 and self.history[-1] == opponent.history[-1] == axl.Action.D:
          self.mutual_defection_count += 1
      else:
          self.mutual_defection_count = 0
  
      return self._random.random_choice(0.9)

# Here's a revised strategy incorporating the feedback:  1. Start by playing
# Cooperate (C) for the first move.  2. For the subsequent moves, follow these
# rules in order:     a. If it's one of the last 100 rounds:       - Calculate
# the opponent's cooperation rate over the entire game.       - If their
# cooperation rate is above 70%, play C.       - If their cooperation rate is
# between 40% and 70%, use strict Tit-for-Tat (copy their last move).       - If
# their cooperation rate is below 40%, play D.     b. If the opponent has
# defected for 5 or more consecutive rounds:       - Play D for a number of
# rounds equal to their consecutive defections (up to a maximum of 10 rounds).
# - After this punishment period, play C once as an "olive branch" before
# returning to the main strategy.     c. If it's a random "olive branch" round
# (1% chance each round, but not during punishment or end-game phases):       -
# Play C regardless of the opponent's previous move.     d. Otherwise, use a
# modified Tit-for-Tat strategy:       - If the opponent played C in the
# previous round, play C.       - If the opponent played D in the previous
# round:         * Calculate the opponent's defection rate over the last 10
# rounds.         * Play D with a probability equal to this defection rate
# (e.g., if they defected in 3 of the last 10 rounds, play D with 30%
# probability).         * Otherwise, play C.  3. Throughout the game, maintain
# these counters:    - Opponent's overall cooperation rate    - Opponent's
# defection rate in the last 10 rounds    - Number of consecutive defections by
# the opponent  This revised strategy maintains a cooperative approach while
# being more adaptive to the opponent's behavior. It's more robust against
# various opponent strategies:  - It handles aggressive opponents better by
# scaling the defection probability based on recent behavior. - It adapts to the
# overall game state by considering the opponent's cooperation rate, especially
# in the end game. - It includes a more flexible "olive branch" mechanism. - It
# has a stronger, adaptive punishment for consistent defection. - It maintains
# simplicity by using clear, ordered conditions for decision-making.  The
# strategy remains fundamentally cooperative but can adjust its level of
# forgiveness and retaliation based on the opponent's actions, making it more
# robust against a variety of opponent behaviors.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_defections = 0
          self.punishment_rounds = 0
          self.round_count = 0
          return axl.Action.C
  
      self.round_count += 1
  
      if self.round_count > 900:
          coop_rate = opponent.cooperations / len(opponent.history)
          if coop_rate > 0.7:
              return axl.Action.C
          elif coop_rate > 0.4:
              return opponent.history[-1]
          else:
              return axl.Action.D
  
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      if self.punishment_rounds == 0 and self.consecutive_defections >= 5:
          self.consecutive_defections = 0
          return axl.Action.C
  
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      if self.consecutive_defections >= 5:
          self.punishment_rounds = min(self.consecutive_defections, 10)
          return axl.Action.D
  
      if self._random.random() < 0.01 and self.punishment_rounds == 0:
          return axl.Action.C
  
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          recent_defection_rate = opponent.defections - opponent.history[-11:-1].count(axl.Action.D)
          recent_defection_rate /= 10
          if self._random.random() < recent_defection_rate:
              return axl.Action.D
          else:
              return axl.Action.C

# Here's a revised strategy that incorporates the feedback:  1. Start by playing
# C (cooperate) for the first round.  2. For each subsequent round, evaluate the
# opponent's behavior using a sliding window of the last 20 rounds (or all
# previous rounds if fewer than 20 have been played). Calculate the opponent's
# cooperation rate as the percentage of C plays in this window.  3. Maintain a
# long-term cooperation rate of the opponent across all rounds played.  4.
# Determine your action for the current round based on the following conditions,
# checked in order:     a) If it's the final 100 rounds of the game:       -
# Calculate a defection probability: (current round number - 900) / 200       -
# Play D with this probability, otherwise proceed to the next condition     b)
# If the opponent's recent cooperation rate (from step 2) is trending downward
# by more than 10% compared to their long-term rate:       - Play D with 80%
# probability, C with 20% probability     c) If the opponent's recent
# cooperation rate is 80% or higher:       - Play C with 90% probability, D with
# 10% probability     d) If the opponent's recent cooperation rate is between
# 60% and 80%:       - Play C with 80% probability, D with 20% probability
# e) If the opponent's recent cooperation rate is between 40% and 60%:       -
# Play C with 60% probability, D with 40% probability     f) If the opponent's
# recent cooperation rate is between 20% and 40%:       - Play C with 40%
# probability, D with 60% probability     g) If the opponent's recent
# cooperation rate is below 20%:       - Play C with 20% probability, D with 80%
# probability  5. Every 50 rounds, regardless of the opponent's behavior, play C
# once as a "forgiveness" mechanism to test if the opponent's strategy has
# changed.  6. If the total score difference between you and your opponent
# exceeds 100 points in either direction:    - If you're winning, increase the
# probability of C in conditions c-g by 10%    - If you're losing, decrease the
# probability of C in conditions c-g by 10%  This strategy maintains simplicity
# while addressing the main points of feedback:  - It uses a sliding window for
# evaluation, making it more responsive to changes. - It considers both recent
# and long-term behavior. - It implements a gradual endgame strategy. - It uses
# a more continuous scale for opponent behavior assessment. - It includes a
# forgiveness mechanism. - It adjusts based on the overall score difference.
# The strategy remains neutral by adapting to the opponent's level of
# cooperation, but it's now more robust against various opponent behaviors and
# changes in strategy.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.long_term_coop_rate = 0
          self.total_rounds = 0
          return axl.Action.C
  
      self.total_rounds += 1
      window_size = min(20, len(self.history))
      recent_window = opponent.history[-window_size:]
      recent_coop_rate = recent_window.count(axl.Action.C) / window_size
  
      self.long_term_coop_rate = ((self.long_term_coop_rate * (self.total_rounds - 1)) + 
                                  (1 if opponent.history[-1] == axl.Action.C else 0)) / self.total_rounds
  
      if self.total_rounds > 900:
          defect_prob = (self.total_rounds - 900) / 200
          if self._random.random() < defect_prob:
              return axl.Action.D
  
      score_diff = self.score - opponent.score
      score_adjustment = 0.1 if abs(score_diff) > 100 else 0
  
      if self.total_rounds % 50 == 0:
          return axl.Action.C
  
      if recent_coop_rate < self.long_term_coop_rate - 0.1:
          return self._random.choice([axl.Action.D] * 8 + [axl.Action.C] * 2)
  
      if recent_coop_rate >= 0.8:
          coop_prob = 0.9
      elif 0.6 <= recent_coop_rate < 0.8:
          coop_prob = 0.8
      elif 0.4 <= recent_coop_rate < 0.6:
          coop_prob = 0.6
      elif 0.2 <= recent_coop_rate < 0.4:
          coop_prob = 0.4
      else:
          coop_prob = 0.2
  
      if score_diff > 100:
          coop_prob = min(1, coop_prob + score_adjustment)
      elif score_diff < -100:
          coop_prob = max(0, coop_prob - score_adjustment)
  
      return self._random.choice([axl.Action.C if self._random.random() < coop_prob else axl.Action.D])

# Here's a revised, simplified strategy that takes into account the feedback:
# 1. Start by playing D (defect) for the first 5 rounds to establish an
# aggressive stance.  2. For the remainder of the game, use the following
# decision-making process in order:     a. If it's one of the last 50 rounds and
# the opponent has cooperated in more than 60% of all previous rounds:       -
# Play D with 90% probability, and C with 10% probability.     b. If the
# opponent has played the same move for the last 3 rounds:       - Play D if
# they've been playing C.       - Play C if they've been playing D.     c. If
# the opponent has alternated moves for the last 4 rounds:       - Play the move
# that would benefit you most (D if they're about to play C, C if they're about
# to play D).     d. Calculate the opponent's cooperation rate over the last 20
# rounds:       - If their cooperation rate is 70% or higher, play C.       - If
# their cooperation rate is below 30%, play D.       - If their cooperation rate
# is between 30% and 70%:         * Play what the opponent played in the
# previous round (tit-for-tat).     e. If none of the above conditions are met
# (i.e., in early rounds or when the opponent's strategy is unclear):       -
# Play D with 80% probability, and C with 20% probability.  3. Every 50 rounds,
# regardless of the above conditions, play C once to test for potential
# cooperation shifts in the opponent's strategy.  4. If at any point your
# average score per round falls below 1.5, reset the strategy by playing 5
# rounds of D followed by 1 round of C, then resume the main strategy.  This
# revised strategy maintains an aggressive approach while being simpler and more
# adaptable. It prioritizes exploiting predictable patterns, responds to the
# opponent's level of cooperation, and includes mechanisms for testing
# cooperation and resetting if underperforming. The conditions are ordered to
# handle specific scenarios first before moving to more general responses.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.reset_counter = 0
          self.in_reset = False
  
      total_rounds = len(self.history)
  
      if self.in_reset:
          self.reset_counter += 1
          if self.reset_counter <= 5:
              return axl.Action.D
          elif self.reset_counter == 6:
              self.in_reset = False
              return axl.Action.C
  
      if total_rounds < 5:
          return axl.Action.D
  
      if total_rounds > 950 and opponent.cooperations / total_rounds > 0.6:
          return self._random.random_choice(0.9)
  
      last_three = opponent.history[-3:]
      if len(last_three) == 3 and len(set(last_three)) == 1:
          return axl.Action.D if last_three[0] == axl.Action.C else axl.Action.C
  
      last_four = opponent.history[-4:]
      if len(last_four) == 4 and all(last_four[i] != last_four[i+1] for i in range(3)):
          return axl.Action.D if last_four[-1] == axl.Action.C else axl.Action.C
  
      recent_twenty = opponent.history[-20:]
      if len(recent_twenty) == 20:
          coop_rate = recent_twenty.count(axl.Action.C) / 20
          if coop_rate >= 0.7:
              return axl.Action.C
          elif coop_rate < 0.3:
              return axl.Action.D
          else:
              return opponent.history[-1]
  
      if (total_rounds + 1) % 50 == 0:
          return axl.Action.C
  
      if self.score / total_rounds < 1.5 and total_rounds > 0:
          self.in_reset = True
          self.reset_counter = 0
          return axl.Action.D
  
      return self._random.random_choice(0.8)

# Here's a revised strategy that incorporates the feedback:  1. Initialize:    -
# Set opponent_cooperation_score = 0.5    - Set forgiveness_rate = 0.1    - Set
# last_10_moves = [] (empty list to track opponent's last 10 moves)  2. For each
# round:     a. If it's the first 3 rounds:       - Play C     b. Else if it's
# one of the last 100 rounds:       - Decrease forgiveness_rate by 0.001 each
# round (minimum 0)     c. Else if the opponent has played D for 10 consecutive
# rounds:       - Play D for a number of rounds equal to (10 -
# opponent_cooperation_score * 10), rounded down       - Then return to the main
# strategy     d. Else if the current round number is divisible by 50:       -
# Play C     e. Else:       - If the opponent played C in the previous round:
# - Play C       - If the opponent played D in the previous round:         -
# Generate a random number between 0 and 1         - If the random number <
# forgiveness_rate:           - Play C         - Else:           - Play D  3.
# After each round:    - Update last_10_moves with the opponent's most recent
# move    - Calculate opponent_cooperation_score as the proportion of C moves in
# last_10_moves    - Adjust forgiveness_rate:      - If
# opponent_cooperation_score > 0.7, increase forgiveness_rate by 0.01 (maximum
# 0.2)      - If opponent_cooperation_score < 0.3, decrease forgiveness_rate by
# 0.01 (minimum 0.05)  This revised strategy maintains the cooperative approach
# while addressing the identified weaknesses:  1. It reduces the initial
# cooperative rounds to 3, limiting early exploitation. 2. The forgiveness rate
# is now adaptive, based on the opponent's recent behavior. 3. The strategy
# gradually reduces forgiveness in the last 100 rounds instead of abruptly
# removing it. 4. It incorporates a simple form of pattern recognition by
# tracking the opponent's last 10 moves. 5. The adaptive forgiveness rate and
# cooperation score help deal with random players. 6. The "suspicious" mode
# duration is now based on the opponent's overall cooperation score. 7. The
# strategy now has a longer-term memory through the opponent_cooperation_score.
# This strategy remains relatively simple while being more robust against
# various opponent behaviors. It maintains its cooperative nature when
# appropriate but can adapt to more aggressive or erratic opponents when
# necessary.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.opponent_cooperation_score = 0.5
          self.forgiveness_rate = 0.1
          self.last_10_moves = []
          self.suspicious_mode = 0
  
      if opponent.history:
          self.last_10_moves.append(opponent.history[-1])
          if len(self.last_10_moves) > 10:
              self.last_10_moves.pop(0)
          self.opponent_cooperation_score = self.last_10_moves.count(axl.Action.C) / len(self.last_10_moves)
  
      if self.opponent_cooperation_score > 0.7:
          self.forgiveness_rate = min(0.2, self.forgiveness_rate + 0.01)
      elif self.opponent_cooperation_score < 0.3:
          self.forgiveness_rate = max(0.05, self.forgiveness_rate - 0.01)
  
      if len(self.history) < 3:
          return axl.Action.C
      elif len(self.history) > 900:
          self.forgiveness_rate = max(0, self.forgiveness_rate - 0.001)
  
      if self.suspicious_mode > 0:
          self.suspicious_mode -= 1
          return axl.Action.D
      elif opponent.history[-10:].count(axl.Action.D) == 10:
          self.suspicious_mode = int(10 - self.opponent_cooperation_score * 10)
          return axl.Action.D
      elif len(self.history) % 50 == 0:
          return axl.Action.C
      elif not opponent.history or opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif self._random.random() < self.forgiveness_rate:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's the revised strategy, taking into account the feedback:  1. Start by
# playing D (defect) for the first 5 rounds to establish an aggressive stance.
# 2. For the remainder of the game, use the following decision-making process in
# order:     a. Forgiveness mechanism: If you've played D for 3 consecutive
# rounds, play C in the next round regardless of the opponent's previous move.
# b. Pattern exploitation: If the opponent has played the same move for 3
# consecutive rounds, play D.     c. Random move: With a 5% probability, play a
# random move (50/50 chance of C or D).     d. Tit-for-Tat with defection bias:
# - If the opponent played D in the previous round, play D.       - If the
# opponent played C in the previous round:         - Play C with 70% probability
# - Play D with 30% probability  3. Endgame strategy (starting from round 900):
# - Calculate the defection probability as: (current round - 900) / 75    - This
# probability increases linearly from 0% at round 900 to 100% at round 975    -
# Play D with this calculated probability, otherwise follow the main strategy
# This strategy maintains an aggressive approach while being simpler and more
# robust. It clearly defines when to cooperate or defect, with conditions
# ordered from most specific to most general. The strategy adapts to opponent
# behavior, includes unpredictability, and has a smoother transition to the
# endgame phase.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_defections = 0
  
      INITIAL_DEFECTIONS = 5
      FORGIVENESS_THRESHOLD = 3
      PATTERN_LENGTH = 3
      RANDOM_MOVE_PROB = 0.05
      COOPERATION_PROB = 0.7
      ENDGAME_START = 900
      ENDGAME_DURATION = 75
  
      if len(self.history) < INITIAL_DEFECTIONS:
          self.consecutive_defections += 1
          return axl.Action.D
  
      if self.consecutive_defections >= FORGIVENESS_THRESHOLD:
          self.consecutive_defections = 0
          return axl.Action.C
  
      if len(self.history) >= ENDGAME_START:
          defection_probability = (len(self.history) - ENDGAME_START) / ENDGAME_DURATION
          if self._random.random() < defection_probability:
              self.consecutive_defections += 1
              return axl.Action.D
  
      if len(opponent.history) >= PATTERN_LENGTH and len(set(opponent.history[-PATTERN_LENGTH:])) == 1:
          self.consecutive_defections += 1
          return axl.Action.D
  
      if self._random.random() < RANDOM_MOVE_PROB:
          action = self._random.choice([axl.Action.C, axl.Action.D])
          self.consecutive_defections = self.consecutive_defections + 1 if action == axl.Action.D else 0
          return action
  
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D
      else:
          if self._random.random() < COOPERATION_PROB:
              self.consecutive_defections = 0
              return axl.Action.C
          else:
              self.consecutive_defections += 1
              return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) for the first 5 rounds.  2. For the remainder of the
# game, use the following decision-making process in order:     a. If the
# opponent has defected 5 or more times in the last 10 rounds:       - Play
# Defect (D) with 90% probability       - Play Cooperate (C) with 10%
# probability     b. If it's a multiple of 50 rounds (50, 100, 150, etc.):
# - Play Cooperate (C) regardless of the opponent's previous move     c. If the
# game is in the last 100 rounds:       - Calculate the opponent's overall
# cooperation rate       - Play Cooperate (C) with a probability equal to the
# opponent's cooperation rate       - Play Defect (D) with the remaining
# probability     d. For all other situations:       - If the opponent played
# Cooperate (C) in the previous round, play Cooperate (C)       - If the
# opponent played Defect (D) in the previous round:         * Play Defect (D)
# with 95% probability         * Play Cooperate (C) with 5% probability  3.
# Throughout the game, keep track of the total score difference between you and
# your opponent. If you are behind by more than 50 points:    - Increase the
# probability of Defect (D) in step 2d to 98% when the opponent's previous move
# was Defect  This revised strategy maintains a cooperative approach while being
# more robust against various opponent behaviors. It's simpler than the previous
# version, with clearer conditions for cooperation and defection. The strategy
# adapts to aggressive opponents, has a mechanism for breaking out of negative
# cycles, and adjusts its behavior in the endgame. The score tracking component
# allows for some risk-taking when significantly behind.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.behind_threshold = 50
          self.endgame_rounds = 100
          self.rounds = 1000
  
      if len(self.history) < 5:
          return axl.Action.C
  
      if len(self.history) >= 10 and opponent.history[-10:].count(axl.Action.D) >= 5:
          return self._random.random_choice(0.9)
  
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      if len(self.history) >= self.rounds - self.endgame_rounds:
          opp_coop_rate = opponent.cooperations / len(opponent.history)
          return self._random.random_choice(opp_coop_rate)
  
      score_diff = self.score - opponent.score
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          defect_prob = 0.98 if score_diff < -self.behind_threshold else 0.95
          return self._random.random_choice(defect_prob)

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first 2 rounds to signal initial willingness to
# cooperate.  2. For each subsequent round, follow these rules in order:     a.
# If the opponent has defected more than 80% of the time in the last 20 rounds,
# play D.        b. If it's a multiple of 15 rounds (i.e., round 15, 30, 45,
# etc.), play C regardless of the opponent's previous move. This serves as a
# "forgiveness" mechanism.        c. If you detect a clear alternating pattern
# (CDCDCD or DCDCDC) in the opponent's last 6 moves, play the move that would
# benefit you most in response to continuing this pattern.        d. If none of
# the above conditions are met, play Tit-for-Tat: copy the opponent's previous
# move.  3. Throughout the game, maintain a rolling average of the opponent's
# cooperation rate over the last 20 moves.  4. In the last 50 rounds of the
# game:    - If the opponent's rolling cooperation rate is below 30%, always
# play D.    - Otherwise, continue with the strategy as described in step 2.
# This strategy aims to: - Start cooperatively but quickly adapt to the
# opponent's behavior. - Generally play Tit-for-Tat, which is simple and
# effective. - Defend against highly aggressive strategies by switching to
# constant defection when needed. - Offer periodic opportunities to return to
# cooperation through the forgiveness mechanism. - Exploit simple patterns when
# detected. - Adjust to more aggressive play in the endgame if the opponent has
# been uncooperative.  The strategy remains relatively simple while addressing
# the main weaknesses identified in the critique. It maintains a neutral
# approach by generally mirroring the opponent's behavior, but includes
# mechanisms to protect against exploitation and to promote cooperation when
# possible.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.rolling_cooperation_rate = 0
          self.cooperation_count = 0
  
      if len(self.history) < 2:
          return axl.Action.C
  
      # Update rolling cooperation rate
      if len(self.history) >= 20:
          self.cooperation_count += int(opponent.history[-1] == axl.Action.C)
          self.cooperation_count -= int(opponent.history[-20] == axl.Action.C)
          self.rolling_cooperation_rate = self.cooperation_count / 20
      elif len(self.history) > 0:
          self.cooperation_count += int(opponent.history[-1] == axl.Action.C)
          self.rolling_cooperation_rate = self.cooperation_count / len(self.history)
  
      # Rule a: Check if opponent defected more than 80% in last 20 rounds
      if len(self.history) >= 20 and opponent.history[-20:].count(axl.Action.D) > 16:
          return axl.Action.D
  
      # Rule b: Forgiveness mechanism
      if len(self.history) % 15 == 0:
          return axl.Action.C
  
      # Rule c: Detect alternating pattern
      if len(opponent.history) >= 6:
          last_6 = opponent.history[-6:]
          if last_6 == [axl.Action.C, axl.Action.D] * 3:
              return axl.Action.D
          elif last_6 == [axl.Action.D, axl.Action.C] * 3:
              return axl.Action.C
  
      # Last 50 rounds behavior
      if len(self.history) >= 950:
          if self.rolling_cooperation_rate < 0.3:
              return axl.Action.D
  
      # Rule d: Tit-for-Tat
      return opponent.history[-1]

# Here's a revised strategy that takes into account the feedback:  1. Start
# aggressively: Play D (defect) for the first 10 rounds.  2. After the initial
# 10 rounds, adopt a modified Tit-for-Tat strategy as the base:    - Generally,
# play what the opponent played in the previous round.    - However, with a 10%
# chance, play D regardless of the opponent's last move.  3. Adjust the strategy
# based on recent opponent behavior and score difference:    - Every 20 rounds,
# analyze the opponent's moves in the last 50 rounds (or all previous rounds if
# less than 50 have been played).    - If the opponent has played D more than
# 60% of the time in this window, increase the chance of playing D to 20% for
# the next 20 rounds.    - If the opponent has played C more than 60% of the
# time in this window, decrease the chance of playing D to 5% for the next 20
# rounds.    - If your score is more than 50 points behind the opponent's,
# increase the chance of playing D by an additional 5% for the next 20 rounds.
# 4. End-game strategy:    - In the last 150 rounds, gradually increase the
# frequency of D plays:      - Rounds 851-900: 20% chance of playing D
# regardless of opponent's last move.      - Rounds 901-950: 30% chance of
# playing D regardless of opponent's last move.      - Rounds 951-1000: 50%
# chance of playing D regardless of opponent's last move.  5. Random probing:
# Throughout the game (except for the first 10 rounds), there's a 5% chance of
# playing a random move (C or D with equal probability), overriding all other
# conditions.  Conditions for cooperation (C) in order of precedence: 1. Always
# cooperate if it's one of the first 10 rounds (0% chance). 2. Cooperate if the
# random probe (5% chance) selects C. 3. Cooperate if the opponent cooperated in
# the previous round AND the random defection chance (which varies between 5-20%
# based on opponent behavior and score difference) doesn't trigger.  Conditions
# for defection (D) in order of precedence: 1. Always defect if it's one of the
# first 10 rounds (100% chance). 2. Defect if the random probe (5% chance)
# selects D. 3. Defect if the opponent defected in the previous round. 4. Defect
# if the random defection chance triggers (varies between 5-50% based on game
# stage, opponent behavior, and score difference).  This revised strategy
# maintains an aggressive stance while being more adaptive and robust against
# various opponent behaviors. It's simpler than the original proposal but still
# incorporates key elements like initial aggression, adaptation to opponent
# behavior, score-based adjustments, and an end-game strategy.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.defect_chance = 0.1
          self.last_adjustment = 0
          self.score_adjustment_counter = 0
  
      if len(self.history) < 10:
          return axl.Action.D
  
      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])
  
      if len(self.history) % 20 == 0 and len(self.history) > self.last_adjustment:
          self.last_adjustment = len(self.history)
          self.score_adjustment_counter = 0
          recent_history = opponent.history[-min(50, len(opponent.history)):]
          defect_ratio = recent_history.count(axl.Action.D) / len(recent_history)
          
          if defect_ratio > 0.6:
              self.defect_chance = 0.2
          elif defect_ratio < 0.4:
              self.defect_chance = 0.05
          else:
              self.defect_chance = 0.1
  
          if (opponent.score - self.score) > 50:
              self.defect_chance += 0.05
              self.score_adjustment_counter = 20
  
      if self.score_adjustment_counter > 0:
          self.score_adjustment_counter -= 1
          if self.score_adjustment_counter == 0:
              self.defect_chance = max(0.1, self.defect_chance - 0.05)
  
      if len(self.history) > 850:
          if len(self.history) > 950:
              self.defect_chance = 0.5
          elif len(self.history) > 900:
              self.defect_chance = 0.3
          else:
              self.defect_chance = 0.2
  
      if self._random.random() < self.defect_chance:
          return axl.Action.D
  
      return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) for the first round.  2. For subsequent rounds, use the
# following decision process in order:     a. If this is one of the last 50
# rounds of the game:       - Calculate a "defection probability" as (current
# round number - 950) / 50       - Play Defect (D) with this probability,
# otherwise play Cooperate (C)     b. If the opponent has defected in the last
# round:       - Play Defect (D)     c. If the opponent has cooperated in the
# last round and your "suspicion score" (explained below) is less than 3:
# - Play Cooperate (C)     d. If it has been between 40-60 rounds since the last
# "cooperation test":       - Play Cooperate (C) and reset the count for the
# next test     e. If the opponent's overall cooperation rate is above 90% and a
# random number between 0-100 is less than 5:       - Play Defect (D) to
# occasionally test for higher payoff     f. Otherwise:       - Play Cooperate
# (C)  3. After each round, update a "suspicion score" for the opponent:    - If
# the opponent defected, increase the score by 1    - If the opponent
# cooperated, decrease the score by 0.5    - Keep the score between 0 and 5  4.
# Track the opponent's overall cooperation rate throughout the game.  This
# strategy maintains a cooperative approach while being more responsive to the
# opponent's behavior. It uses a "Tit-for-Tat" core (responding to the last
# move) but modifies this based on the suspicion score, allowing for some
# forgiveness and adaptation to the opponent's overall behavior.  The strategy
# is more robust against various opponent types: - It responds quickly to
# defection but can still forgive and return to cooperation. - It's less
# exploitable by alternating strategies due to the suspicion score. - It adapts
# to the opponent's overall behavior through the cooperation rate tracking. -
# The end-game strategy is more gradual and less predictable. - The cooperation
# test is now randomized to be less exploitable. - The occasional defection
# against highly cooperative opponents is less frequent and only triggered when
# the opponent has been very cooperative overall.  This revised strategy should
# perform well against a range of opponent behaviors while remaining relatively
# simple and primarily cooperative.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.suspicion_score = 0
          self.last_test_round = 0
          self.cooperation_rate = 1.0
  
      if len(self.history) == 0:
          return axl.Action.C
  
      current_round = len(self.history) + 1
  
      # End-game strategy
      if current_round > 950:
          defection_probability = (current_round - 950) / 50
          if self._random.random() < defection_probability:
              return axl.Action.D
  
      # Response to opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.C and self.suspicion_score < 3:
          return axl.Action.C
  
      # Cooperation test
      if 40 <= current_round - self.last_test_round <= 60:
          self.last_test_round = current_round
  
      # Update cooperation rate
      self.cooperation_rate = ((len(opponent.history) - 1) * self.cooperation_rate + 
                               (1 if opponent.history[-1] == axl.Action.C else 0)) / len(opponent.history)
  
      # Occasional defection against highly cooperative opponents
      if self.cooperation_rate > 0.9 and self._random.random() < 0.05:
          return axl.Action.D
  
      # Update suspicion score
      if opponent.history[-1] == axl.Action.D:
          self.suspicion_score = min(5, self.suspicion_score + 1)
      else:
          self.suspicion_score = max(0, self.suspicion_score - 0.5)
  
      # Default action
      return axl.Action.C

# Here's the revised strategy, taking into account the feedback and clearly
# stating the conditions for cooperation and defection:  1. Start by playing C
# (cooperate) in the first round.  2. For each subsequent round, follow these
# steps in order:     a. If it's the final round (round 1000), play D (defect).
# b. If it's one of the last 50 rounds (951-999), calculate a decreasing
# cooperation probability:       - Cooperation probability = (1000 - current
# round number) / 50       - Play C with this probability, otherwise play D.
# c. If the opponent has defected for the last 3 consecutive rounds:       -
# Play D for the next 2 rounds, then return to the main strategy.     d. If
# there has been mutual defection for the last 10 or more rounds, and the
# current round number is divisible by 20:       - Play C as an "olive branch."
# e. For all other situations, use the main strategy:       - Calculate the
# opponent's cooperation rate over the last 50 rounds (or all previous rounds if
# fewer than 50).       - Set your cooperation probability to: min(1, max(0,
# (opponent's cooperation rate - 0.4) * 2))       - Play C with this
# probability, otherwise play D.  This strategy maintains simplicity and
# neutrality while incorporating the suggested improvements. It addresses end-
# game behavior, includes a measured response to consecutive defections, offers
# occasional forgiveness, and uses a sliding scale for cooperation based on the
# opponent's recent behavior. The conditions are ordered to prioritize specific
# situations before falling back on the main probabilistic approach.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      FINAL_ROUND = 1000
      ENDGAME_START = 950
      CONSECUTIVE_DEFECTIONS = 3
      MUTUAL_DEFECTION_STREAK = 10
      OLIVE_BRANCH_INTERVAL = 20
      COOPERATION_RATE_OFFSET = 0.4
      COOPERATION_RATE_MULTIPLIER = 2
  
      if not self.history:
          self.defect_counter = 0
          return axl.Action.C
  
      current_round = len(self.history) + 1
  
      if current_round == FINAL_ROUND:
          return axl.Action.D
  
      if current_round > ENDGAME_START:
          coop_prob = (FINAL_ROUND - current_round) / (FINAL_ROUND - ENDGAME_START)
          return axl.Action.C if self._random.random() < coop_prob else axl.Action.D
  
      if self.defect_counter > 0:
          self.defect_counter -= 1
          return axl.Action.D
  
      if len(opponent.history) >= CONSECUTIVE_DEFECTIONS and all(move == axl.Action.D for move in opponent.history[-CONSECUTIVE_DEFECTIONS:]):
          self.defect_counter = 2
          return axl.Action.D
  
      if len(self.history) >= MUTUAL_DEFECTION_STREAK and all(self.history[i] == opponent.history[i] == axl.Action.D for i in range(-MUTUAL_DEFECTION_STREAK, 0)):
          if current_round % OLIVE_BRANCH_INTERVAL == 0:
              return axl.Action.C
  
      last_50_moves = min(50, len(opponent.history))
      opponent_coop_rate = opponent.history[-last_50_moves:].count(axl.Action.C) / last_50_moves
      coop_prob = min(1, max(0, (opponent_coop_rate - COOPERATION_RATE_OFFSET) * COOPERATION_RATE_MULTIPLIER))
      return axl.Action.C if self._random.random() < coop_prob else axl.Action.D

# Here's the revised strategy, taking into account the feedback:  1. Start by
# playing D (defect) for the first 5 rounds.  2. For the remaining rounds,
# determine your move in the following order:     a. If it's the last 100 rounds
# of the game:       - Calculate a defection probability: 20% + (current round -
# 900) * 0.3%       - Randomly defect with this probability       - If you don't
# defect based on this probability, continue to the next conditions     b. Every
# 10 rounds (on rounds divisible by 10):       - Calculate the opponent's
# cooperation ratio for the last 10 rounds       - If the ratio is above 70%,
# play D       - If the ratio is below 40%, set a "low cooperation flag" for the
# next 10 rounds       - If you defect based on this condition, skip the
# remaining conditions     c. If the "low cooperation flag" is set:       -
# Randomly defect with 20% probability       - If you don't defect based on this
# probability, continue to the next condition     d. Randomly defect with 10%
# probability     e. If you haven't defected based on any of the above
# conditions:       - Play the same move your opponent played in the previous
# round (Tit-for-Tat)  3. Always play D on the final round of the game.  This
# strategy: - Starts aggressively - Uses Tit-for-Tat as its base - Maintains an
# element of unpredictability with random defections - Adapts to the opponent's
# level of cooperation - Becomes increasingly aggressive towards the end of the
# game - Is clear about when to cooperate or defect, with conditions ordered
# from most specific to most general  The strategy balances aggression with
# reactivity, making it robust against various opponent behaviors while still
# aiming to maximize total payoff.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.low_cooperation_flag = False
          self.flag_counter = 0
  
      if len(self.history) < 5:
          return axl.Action.D
  
      if len(self.history) >= 900:
          if len(self.history) == 999:
              return axl.Action.D
          defection_probability = 0.2 + (len(self.history) - 900) * 0.003
          if self._random.random() < defection_probability:
              return axl.Action.D
  
      if len(self.history) % 10 == 0:
          opponent_cooperation_ratio = opponent.history[-10:].count(axl.Action.C) / 10
          if opponent_cooperation_ratio > 0.7:
              return axl.Action.D
          elif opponent_cooperation_ratio < 0.4:
              self.low_cooperation_flag = True
              self.flag_counter = 10
  
      if self.low_cooperation_flag:
          if self._random.random() < 0.2:
              return axl.Action.D
          self.flag_counter -= 1
          if self.flag_counter == 0:
              self.low_cooperation_flag = False
  
      if self._random.random() < 0.1:
          return axl.Action.D
  
      return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) for the first round.  2. For each subsequent round,
# evaluate the following conditions in order:     a. If it's one of the last 20
# rounds of the game:       - Mirror the opponent's last move (Tit-for-Tat).
# b. If the opponent has defected more than 60% of the time in the last 30
# moves:       - Defect with 80% probability, Cooperate with 20% probability.
# c. If the opponent has cooperated more than 90% of the time in the last 50
# moves:       - Cooperate with 90% probability, Defect with 10% probability.
# d. If it's been between 45-55 rounds since the last "reset" move:       -
# Cooperate and mark this as a "reset" move.     e. If the opponent has defected
# twice in the last three moves:       - Defect.     f. Otherwise:       -
# Cooperate.  3. Throughout the game, maintain a running tally of the score
# difference between you and your opponent. Every 100 rounds, adjust the
# strategy:     - If you're significantly behind (more than 50 points):
# Increase the defection probability in step 2c to 20% and decrease the
# cooperation probability in step 2b to 10%.        - If you're significantly
# ahead (more than 50 points):      Decrease the defection probability in step
# 2c to 5% and increase the cooperation probability in step 2b to 30%.  4. Start
# with a forgiveness threshold of 2 defections in 3 moves (as in step 2e). Every
# 200 rounds, if your score is lower than your opponent's, decrease this
# threshold by 1 (to a minimum of 1 defection in 3 moves). If your score is
# higher, increase it by 1 (to a maximum of 3 defections in 3 moves).  This
# revised strategy: - Maintains a cooperative approach while being more adaptive
# to opponent behavior. - Uses a sliding window for analyzing recent opponent
# moves. - Adjusts its behavior based on the game stage (early, mid, late game).
# - Incorporates score difference to fine-tune aggressiveness. - Includes a
# self-adjusting forgiveness threshold. - Reduces predictability through
# probabilistic decisions and variable intervals. - Clearly defines conditions
# for cooperation and defection, ordered from most specific to most general.
# This strategy should be more robust against a variety of opponent behaviors
# while still encouraging cooperation when possible.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.reset_round = 0
          self.forgiveness_threshold = 2
          self.last_score_adjustment = 0
          self.last_forgiveness_adjustment = 0
          self.defection_prob_2c = 0.1
          self.cooperation_prob_2b = 0.2
  
      if len(self.history) == 0:
          return axl.Action.C
  
      if len(self.history) > 980:
          return opponent.history[-1]
  
      opponent_defection_rate = opponent.history[-30:].count(axl.Action.D) / 30 if len(opponent.history) >= 30 else 0
      opponent_cooperation_rate = opponent.history[-50:].count(axl.Action.C) / 50 if len(opponent.history) >= 50 else 1
  
      if opponent_defection_rate > 0.6:
          return axl.Action.D if self._random.random() < (1 - self.cooperation_prob_2b) else axl.Action.C
  
      if opponent_cooperation_rate > 0.9:
          return axl.Action.C if self._random.random() < (1 - self.defection_prob_2c) else axl.Action.D
  
      if 45 <= len(self.history) - self.reset_round <= 55:
          self.reset_round = len(self.history)
          return axl.Action.C
  
      if opponent.history[-3:].count(axl.Action.D) >= self.forgiveness_threshold:
          return axl.Action.D
  
      if len(self.history) % 100 == 0:
          score_diff = self.score - opponent.score
          if score_diff < -50:
              self.defection_prob_2c = 0.2
              self.cooperation_prob_2b = 0.1
          elif score_diff > 50:
              self.defection_prob_2c = 0.05
              self.cooperation_prob_2b = 0.3
          else:
              self.defection_prob_2c = 0.1
              self.cooperation_prob_2b = 0.2
  
      if len(self.history) % 200 == 0:
          if self.score < opponent.score:
              self.forgiveness_threshold = max(1, self.forgiveness_threshold - 1)
          else:
              self.forgiveness_threshold = min(3, self.forgiveness_threshold + 1)
  
      return axl.Action.C

# Here's a revised strategy that incorporates the feedback while maintaining
# simplicity and a neutral approach:  1. Start by playing C (cooperate) for the
# first round.  2. For the next 29 rounds, mirror your opponent's previous move.
# This allows for better early-game adaptation and information gathering.  3.
# After the first 30 rounds, and then every 10 rounds thereafter, calculate a
# weighted cooperation score for your opponent:    - Give the most recent 10
# moves a weight of 3    - Give the previous 10 moves a weight of 2    - Give
# the 10 moves before that a weight of 1    - Calculate the weighted average of
# C plays  4. For each round, make your decision in the following order:     a)
# If you're in the last 50 rounds of the game:       - Calculate a "defection
# probability" as (51 - remaining rounds) / 50       - With this probability,
# play D; otherwise, proceed to the next condition     b) If your opponent has
# played D for 3 consecutive rounds:       - Play D for a random number of
# rounds between 3 and 7       - After this punishment phase, return to the main
# strategy     c) If it's a probing round (10% chance):       - Play a random
# move (50% C, 50% D)     d) Otherwise, base your decision on the weighted
# cooperation score:       - If the score is 65% or higher, play C       - If
# the score is between 50% and 65%, play C with probability equal to the score
# - If the score is below 50%, play D  5. Every 50 rounds, calculate the
# cumulative score difference between you and your opponent. Adjust the
# cooperation thresholds:    - If you're ahead, increase the lower threshold to
# 55% and the upper threshold to 70%    - If you're behind, decrease the lower
# threshold to 45% and the upper threshold to 60%  6. At all times, keep track
# of the expected value (EV) of C and D based on the opponent's recent behavior:
# - If the EV of D is more than 1.5 times the EV of C, override the above rules
# and play D    - If the EV of C is more than 1.5 times the EV of D, override
# the above rules and play C  This revised strategy maintains a neutral approach
# while being more adaptive and robust. It starts cooperatively, adjusts based
# on the opponent's behavior, and incorporates elements to handle various
# opponent strategies. The strategy is more responsive to recent moves, less
# predictable, and takes into account the game's payoff structure in its
# decision-making process.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.lower_threshold = 0.50
          self.upper_threshold = 0.65
          self.ev_c = 3
          self.ev_d = 3
          self.punishment_end = 0
          return axl.Action.C
  
      if len(self.history) <= 30:
          return opponent.history[-1]
  
      recent = sum(opp_move == axl.Action.C for opp_move in opponent.history[-10:]) * 3
      previous = sum(opp_move == axl.Action.C for opp_move in opponent.history[-20:-10]) * 2
      oldest = sum(opp_move == axl.Action.C for opp_move in opponent.history[-30:-20])
      weighted_score = (recent + previous + oldest) / 60
  
      if len(self.history) >= 950:
          defection_prob = (1001 - len(self.history)) / 50
          if self._random.random() < defection_prob:
              return axl.Action.D
  
      if len(self.history) > self.punishment_end:
          if opponent.history[-3:].count(axl.Action.D) == 3:
              self.punishment_end = len(self.history) + self._random.randint(3, 7)
              return axl.Action.D
      elif len(self.history) <= self.punishment_end:
          return axl.Action.D
  
      if self._random.random() < 0.1:
          return self._random.choice([axl.Action.C, axl.Action.D])
  
      if weighted_score >= self.upper_threshold:
          action = axl.Action.C
      elif weighted_score >= self.lower_threshold:
          action = axl.Action.C if self._random.random() < weighted_score else axl.Action.D
      else:
          action = axl.Action.D
  
      if len(self.history) % 50 == 0:
          score_diff = self.score - opponent.score
          if score_diff > 0:
              self.lower_threshold = 0.55
              self.upper_threshold = 0.70
          else:
              self.lower_threshold = 0.45
              self.upper_threshold = 0.60
  
      recent_actions = opponent.history[-30:]
      c_count = recent_actions.count(axl.Action.C)
      d_count = recent_actions.count(axl.Action.D)
      self.ev_c = (c_count * 3 + d_count * 0) / 30
      self.ev_d = (c_count * 5 + d_count * 1) / 30
  
      if self.ev_d > 1.5 * self.ev_c:
          return axl.Action.D
      elif self.ev_c > 1.5 * self.ev_d:
          return axl.Action.C
  
      return action

# Here's the revised strategy, taking into account the feedback:  1. Start with
# a base probability of playing D (defect) 75% of the time and C (cooperate) 25%
# of the time.  2. For each round, determine the action based on the following
# conditions, in order:     a. If this is one of the last 100 rounds:       -
# Increase the probability of D by 0.5% each round, reaching 100% D for the
# final 20 rounds.     b. If the opponent has defected in the last two
# consecutive rounds:       - Play D for the next two rounds, then return to the
# base probability.     c. If currently behind in cumulative score by 20 points
# or more:       - Increase the probability of D to 90% until the score
# difference is less than 20.     d. Calculate the opponent's cooperation rate
# over the last 10 rounds:       - If the rate is above 50%, adjust the base
# probabilities:         * For every 10% above 50%, increase the C probability
# by 5% (up to a maximum of 40% C probability).       - If the rate is 50% or
# below, revert to the original 75% D, 25% C probabilities.  3. If none of the
# above conditions are met, use the current base probabilities to determine the
# action.  4. After each round, update the rolling statistics:    - Opponent's
# last two moves    - Cumulative score difference    - Opponent's cooperation
# rate over the last 10 rounds  This revised strategy maintains an aggressive
# approach while being more adaptive and less predictable. It clearly defines
# when to cooperate or defect based on specific conditions, ordered by priority.
# The strategy remains relatively simple while addressing the main weaknesses
# identified in the critique.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.base_d_prob = 0.75
          self.coop_rate_window = 10
  
      rounds_played = len(self.history)
      total_rounds = 1000
  
      # Condition a: Last 100 rounds
      if rounds_played >= total_rounds - 100:
          d_prob = min(1.0, self.base_d_prob + 0.005 * (rounds_played - (total_rounds - 100)))
          if rounds_played >= total_rounds - 20:
              return axl.Action.D
  
      # Condition b: Opponent defected last two rounds
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Condition c: Behind in cumulative score
      score_diff = self.score - opponent.score
      if score_diff <= -20:
          d_prob = 0.90
      else:
          # Condition d: Opponent's cooperation rate
          if len(opponent.history) >= self.coop_rate_window:
              coop_rate = opponent.history[-self.coop_rate_window:].count(axl.Action.C) / self.coop_rate_window
              if coop_rate > 0.5:
                  c_prob_increase = min(0.15, ((coop_rate - 0.5) / 0.1) * 0.05)
                  d_prob = max(0.60, self.base_d_prob - c_prob_increase)
              else:
                  d_prob = self.base_d_prob
          else:
              d_prob = self.base_d_prob
  
      return axl.Action.D if self._random.random() < d_prob else axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Initial
# Probing (first 4 rounds):    Play C, D, C, D in that order to gauge the
# opponent's initial strategy.  2. Main Strategy (rounds 5-950):    Use a
# modified Tit-for-Tat with memory and adaptation:     a. Calculate the
# opponent's cooperation rate over the last 20 moves.     b. If the opponent's
# cooperation rate is above 70%:       - Play C if the opponent played C in any
# of the last 2 moves.       - Otherwise, play D with 90% probability and C with
# 10% probability.     c. If the opponent's cooperation rate is between 30% and
# 70%:       - Play C if the opponent played C in the last move.       -
# Otherwise, play D with 90% probability and C with 10% probability.     d. If
# the opponent's cooperation rate is below 30%:       - Play D with 80%
# probability and C with 20% probability.  3. Defensive Mechanism:    If the
# opponent has played D for 3 consecutive rounds, switch to defensive mode for
# the next 5 rounds:    - Play D with 90% probability and C with 10%
# probability.  4. Periodic Cooperation:    Every 30-50 rounds (randomly
# determined), play C regardless of the opponent's previous moves.  5. Breaking
# Defection Cycles:    If there have been 10 consecutive rounds of mutual
# defection, play C for 2 rounds in a row.  6. End-game Strategy (rounds
# 951-1000):    Adjust the strategy based on the opponent's overall cooperation
# rate throughout the game:     a. If the opponent's overall cooperation rate is
# above 60%:       - Continue with the main strategy.     b. If the opponent's
# overall cooperation rate is between 40% and 60%:       - Play D with 30%
# probability when you would normally play C.     c. If the opponent's overall
# cooperation rate is below 40%:       - Play D with 60% probability when you
# would normally play C.  Execution Order: 1. For the first 4 rounds, follow the
# Initial Probing strategy. 2. For rounds 5-1000:    - First, check if it's time
# for Periodic Cooperation.    - If not, check if the Defensive Mechanism should
# be activated.    - If not, check if the Breaking Defection Cycles condition is
# met.    - If none of the above, follow the Main Strategy.    - For rounds
# 951-1000, apply the End-game Strategy modifications to the Main Strategy.
# This revised strategy maintains a cooperative approach while being more
# adaptive to different opponent behaviors. It starts with a probing phase, uses
# a longer memory for decision-making, adapts to the opponent's overall
# cooperation rate, and includes mechanisms to break out of negative cycles. The
# end-game strategy is more nuanced and based on the opponent's behavior
# throughout the game.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.consecutive_d_count = 0
          self.defensive_mode_rounds = 0
          self.mutual_defection_count = 0
          self.last_periodic_cooperation = 0
          self.next_periodic_cooperation = self._random.randint(30, 50)
  
      if len(self.history) < 4:
          return [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D][len(self.history)]
  
      overall_coop_rate = opponent.cooperations / len(opponent.history)
  
      if len(self.history) - self.last_periodic_cooperation >= self.next_periodic_cooperation:
          self.last_periodic_cooperation = len(self.history)
          self.next_periodic_cooperation = self._random.randint(30, 50)
          return axl.Action.C
  
      if self.defensive_mode_rounds > 0:
          self.defensive_mode_rounds -= 1
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
  
      if opponent.history[-3:].count(axl.Action.D) == 3:
          self.defensive_mode_rounds = 5
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
  
      if self.history[-10:] == [axl.Action.D] * 10 and opponent.history[-10:] == [axl.Action.D] * 10:
          self.mutual_defection_count += 1
          if self.mutual_defection_count <= 2:
              return axl.Action.C
          else:
              self.mutual_defection_count = 0
      else:
          self.mutual_defection_count = 0
  
      recent_coop_rate = opponent.history[-20:].count(axl.Action.C) / 20
  
      if recent_coop_rate > 0.7:
          if axl.Action.C in opponent.history[-2:]:
              action = axl.Action.C
          else:
              action = axl.Action.D if self._random.random() < 0.9 else axl.Action.C
      elif 0.3 <= recent_coop_rate <= 0.7:
          if opponent.history[-1] == axl.Action.C:
              action = axl.Action.C
          else:
              action = axl.Action.D if self._random.random() < 0.9 else axl.Action.C
      else:
          action = axl.Action.D if self._random.random() < 0.8 else axl.Action.C
  
      if len(self.history) >= 950:
          if overall_coop_rate > 0.6:
              return action
          elif 0.4 <= overall_coop_rate <= 0.6:
              if self._random.random() < 0.3:
                  return axl.Action.D
          else:
              if self._random.random() < 0.6:
                  return axl.Action.D
  
      return action

# Here's a revised strategy that takes into account the feedback:  1. For each
# round, evaluate the opponent's behavior based on their last 50 moves (or all
# previous moves if fewer than 50 rounds have been played).  2. Determine your
# action for the current round based on the following conditions, in order:
# a. If it's the first round, play C to initiate with a cooperative signal.
# b. If you're in the last 50 rounds of the game, increase the probability of
# playing D by 2% each round (starting from your base strategy). This gradual
# shift protects against end-game exploitation while remaining less predictable.
# c. If the opponent has played D more than 60% of the time in the evaluation
# period, play D to protect against exploitation.     d. If the opponent has
# played C more than 60% of the time in the evaluation period, play C to
# maintain cooperation.     e. If the opponent's play is mixed (between 40% and
# 60% C), use a "generous Tit-for-Tat" approach:       - If the opponent's last
# move was C, play C.       - If the opponent's last move was D, play C with a
# 20% probability, otherwise play D.     f. If none of the above conditions are
# met (which may happen in early rounds), play C.  3. Every 10 rounds,
# regardless of the above conditions, play C with a 10% probability. This
# "forgiveness" mechanism allows for the possibility of shifting to mutual
# cooperation even against seemingly aggressive opponents.  4. If you detect a
# alternating pattern of C and D from the opponent over the last 6 moves, break
# the pattern by playing the opposite of what the pattern predicts for the next
# move.  This strategy maintains a neutral approach by adapting to the
# opponent's behavior without being overly aggressive or purely cooperative.
# It's simpler than the previous version, with clear conditions for cooperation
# and defection. The strategy is more robust against various opponent behaviors,
# including those that alternate between cooperation and defection, and it
# allows for quicker adaptation to changes in opponent strategy.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.end_game_shift = 0
  
      if len(self.history) == 0:
          return axl.Action.C
  
      evaluation_period = min(50, len(self.history))
      opponent_recent_moves = opponent.history[-evaluation_period:]
      opponent_c_ratio = opponent_recent_moves.count(axl.Action.C) / evaluation_period
  
      if len(self.history) >= 950:
          self.end_game_shift = min(1, self.end_game_shift + 0.02)
  
      if len(self.history) % 10 == 0 and self._random.random() < 0.1:
          return axl.Action.C
  
      if len(self.history) >= 6:
          last_6_moves = opponent.history[-6:]
          if last_6_moves == [axl.Action.C, axl.Action.D] * 3:
              return axl.Action.D
          elif last_6_moves == [axl.Action.D, axl.Action.C] * 3:
              return axl.Action.C
  
      if opponent_c_ratio <= 0.4:
          return axl.Action.D
      elif opponent_c_ratio >= 0.6:
          return axl.Action.C
      else:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              defect_prob = 0.8 + self.end_game_shift
              return axl.Action.D if self._random.random() < defect_prob else axl.Action.C
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing D (defect) for the first 10 rounds to establish a clear aggressive
# stance.  2. After the initial 10 rounds, adopt a modified tit-for-tat strategy
# with the following rules, applied in order:     a. If it's one of the last 100
# rounds, increase the probability of defection linearly. At round 900, have a
# 0% chance of defecting (beyond the normal strategy); at the final round, have
# a 100% chance of defecting. For example, at round 950, have a 50% chance of
# defecting regardless of other conditions.     b. If it's a multiple of 50
# rounds (50, 100, 150, etc.), play C to probe for cooperation and potentially
# break defection cycles.     c. If the opponent has defected in the last two
# rounds, play D.     d. If the opponent cooperated in the last round, play C.
# e. If none of the above conditions are met, play D.  3. Throughout the game,
# maintain a rolling average of the opponent's cooperation rate over the last 50
# moves. Use this information as follows:     - If the cooperation rate drops
# below 30%, play D for the next 5 rounds before returning to the main strategy.
# This punishes highly aggressive opponents.    - If the cooperation rate rises
# above 70%, play C for the next 2 rounds before returning to the main strategy.
# This rewards highly cooperative opponents.  This strategy is aggressive yet
# adaptive. It starts aggressively, uses a forgiving variant of tit-for-tat as
# its core, probes for cooperation periodically, adjusts based on the opponent's
# overall behavior, and becomes increasingly aggressive towards the end of the
# game. The conditions for cooperation and defection are clearly stated and
# ordered, making the strategy easier to implement and understand.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.cooperation_rate = [1 if opponent.history and opponent.history[-1] == axl.Action.C else 0]
          self.punishment_counter = 0
          self.reward_counter = 0
  
      if len(self.history) < 10:
          return axl.Action.D
  
      # Update rolling average of opponent's cooperation rate
      self.cooperation_rate.append(1 if opponent.history[-1] == axl.Action.C else 0)
      if len(self.cooperation_rate) > 50:
          self.cooperation_rate.pop(0)
  
      # Check if we're in the last 100 rounds
      if len(self.history) >= 900:
          defect_probability = (len(self.history) - 900) / 100
          if self._random.random() < defect_probability:
              return axl.Action.D
  
      # Check if it's a multiple of 50 rounds
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Check opponent's cooperation rate
      avg_cooperation_rate = sum(self.cooperation_rate) / len(self.cooperation_rate)
      if avg_cooperation_rate < 0.3:
          self.punishment_counter = 5
          return axl.Action.D
      elif avg_cooperation_rate > 0.7:
          self.reward_counter = 2
          return axl.Action.C
  
      # Check if we're in punishment mode
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # Check if we're in reward mode
      if self.reward_counter > 0:
          self.reward_counter -= 1
          return axl.Action.C
  
      # Modified Tit-for-Tat logic
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
      elif opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) for the first round.  2. For the next 4 rounds, use Tit-
# for-Tat: copy your opponent's previous move.  3. After the first 5 rounds and
# for the remainder of the game, use the following decision process in order:
# a. Calculate the rolling average of your opponent's cooperation over the last
# 20 moves (or all previous moves if fewer than 20 have been played).     b. If
# it's a multiple of 25 rounds (25, 50, 75, etc.), play Cooperate as an "olive
# branch" move, regardless of other conditions.     c. If you're in the last 20
# rounds of the game:       - If the opponent's rolling average cooperation rate
# is above 50%, continue with the strategy below.       - If it's 50% or below,
# play Defect.     d. If the opponent has cooperated in the last two rounds,
# play Cooperate.     e. If the opponent's rolling average cooperation rate is
# above 50%:       - If the opponent defected in the last round, play Defect.
# - Otherwise, play Cooperate.     f. If the opponent's rolling average
# cooperation rate is 50% or below:       - If the opponent defected in the last
# two rounds, play Defect.       - Otherwise, play Cooperate.  This revised
# strategy is simpler and more adaptive. It maintains a cooperative approach
# while protecting against exploitation. The strategy will cooperate in the
# following main scenarios:  - As an "olive branch" every 25 rounds - When the
# opponent has cooperated in the last two rounds - When the opponent is
# generally cooperative (>50% cooperation rate) and didn't defect in the last
# round - When the opponent is less cooperative (≤50% cooperation rate) but
# didn't defect in the last two rounds  It will defect primarily when:  - The
# opponent is generally cooperative but defected in the last round (Tit-for-Tat)
# - The opponent is less cooperative and defected in the last two rounds (Tit-
# for-Two-Tats) - In the end game if the opponent has not been generally
# cooperative  This strategy is more robust against various opponent behaviors,
# adapts quickly to changes, and maintains a balance between cooperation and
# protection against exploitation.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.last_20_moves = []
  
      if len(self.history) < 5:
          if not self.history:
              return axl.Action.C
          else:
              return opponent.history[-1]
  
      self.last_20_moves.append(opponent.history[-1])
      if len(self.last_20_moves) > 20:
          self.last_20_moves.pop(0)
  
      opponent_coop_rate = self.last_20_moves.count(axl.Action.C) / len(self.last_20_moves)
  
      if len(self.history) % 25 == 0:
          return axl.Action.C
  
      if len(self.history) >= 980:
          if opponent_coop_rate <= 0.5:
              return axl.Action.D
  
      if opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      if opponent_coop_rate > 0.5:
          return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
      else:
          return axl.Action.D if opponent.history[-2:] == [axl.Action.D, axl.Action.D] else axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. For each subsequent round,
# follow these steps in order:     a. Calculate the opponent's defection rate
# over the last 10 rounds.        b. Set your base cooperation probability to
# (100% - opponent's defection rate).       For example, if the opponent
# defected 3 out of the last 10 rounds, your base cooperation probability is
# 70%.        c. If your cumulative score is more than 20 points behind your
# opponent's, reduce your cooperation probability by 10%.        d. Apply a 5%
# random factor: With a 5% chance, flip your intended move (C to D or D to C).
# 3. Make your move:    - Generate a random number between 0 and 1.    - If this
# number is less than your final cooperation probability, play C. Otherwise,
# play D.  4. Exception: Always play D if the opponent has played D in both of
# the last two rounds, regardless of other factors. This maintains the core of
# the Tit-for-Two-Tats strategy.  This strategy is simple, neutral, and
# addresses the main points of feedback: - It adapts quickly to the opponent's
# recent behavior using a 10-round window. - It incorporates cumulative score
# consideration. - It includes a small random element to reduce predictability.
# - It maintains the Tit-for-Two-Tats core for basic protection against
# exploitation.  The strategy is clear about when it will cooperate or defect,
# with conditions ordered from general (based on opponent's recent behavior) to
# specific (the Tit-for-Two-Tats exception). This approach allows for both
# adaptability to various opponent strategies and protection against consistent
# exploitation.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
  
      last_10_rounds = min(10, len(self.history))
      opponent_defection_rate = opponent.history[-last_10_rounds:].count(axl.Action.D) / last_10_rounds
      base_cooperation_prob = 1 - opponent_defection_rate
  
      if self.score < opponent.score - 20:
          base_cooperation_prob -= 0.1
  
      intended_move = axl.Action.C if self._random.random() < base_cooperation_prob else axl.Action.D
  
      if self._random.random() < 0.05:
          intended_move = axl.Action.C if intended_move == axl.Action.D else axl.Action.D
  
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      return intended_move

# Here's a revised strategy incorporating the feedback:  1. Start by playing D
# (defect) for the first 5 rounds.  2. After the first 5 rounds, evaluate the
# opponent's behavior:     a. If the opponent played C (cooperate) 3 or more
# times, switch to "adaptive tit-for-tat":       - Play what the opponent played
# in the previous round.       - With a 20% probability every 5-15 rounds
# (randomly determined), play C regardless of the opponent's last move.     b.
# If the opponent played D 3 or more times, continue playing D for the next 15
# rounds.  3. Every 30 rounds, re-evaluate the opponent's behavior over the last
# 50 rounds, giving more weight to recent actions:    - Calculate a cooperation
# score: (number of C plays) + 2 * (number of C plays in last 20 rounds)    - If
# the cooperation score is 35 or higher, switch to "adaptive tit-for-tat" (as
# described in 2a).    - If the cooperation score is below 35, play D for the
# next 20 rounds.  4. Check for alternating patterns every 10 rounds:    - If
# the opponent has been strictly alternating between C and D for the last 8+
# rounds, play D for the next 10 rounds.  5. Exploration phase: Every 100
# rounds, if not in "adaptive tit-for-tat" mode, play C for 2 consecutive rounds
# to test the opponent's response.  6. End game behavior (last 50 rounds):    -
# Calculate the probability of defection as: (current round number - 950) / 50
# - In each round, defect with this probability; otherwise, continue with the
# current strategy.  7. Always defect in the final round.  Conditions for
# cooperation: - When in "adaptive tit-for-tat" mode and the opponent cooperated
# in the previous round. - During the random forgiveness in "adaptive tit-for-
# tat" mode (20% chance every 5-15 rounds). - During the exploration phase every
# 100 rounds. - In the end game, when the random factor doesn't trigger
# defection.  Conditions for defection: - In the first 5 rounds. - When the
# opponent has been aggressive (as defined in steps 2b and 3). - When an
# alternating pattern is detected. - With increasing probability in the end
# game. - Always in the final round.  This revised strategy maintains an
# aggressive stance while being more adaptive and robust against various
# opponent behaviors. It incorporates quicker evaluation periods, pattern
# detection, periodic exploration, and a smoother transition to end-game
# behavior.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.adaptive_tft = False
          self.defect_count = 0
          self.last_evaluation = 0
          self.last_pattern_check = 0
          self.last_exploration = 0
          self.random_forgiveness = 0
          self.last_forgiveness = 0
          self.exploration_count = 0
  
      current_round = len(self.history)
  
      # First 5 rounds
      if current_round < 5:
          return axl.Action.D
  
      # Evaluate opponent's behavior after first 5 rounds
      if current_round == 5:
          if opponent.history.cooperations >= 3:
              self.adaptive_tft = True
              self.random_forgiveness = self._random.randint(5, 16)
          else:
              self.defect_count = 15
  
      # Re-evaluate every 30 rounds
      if current_round - self.last_evaluation >= 30:
          self.last_evaluation = current_round
          recent_history = opponent.history[-50:]
          coop_score = recent_history.count(axl.Action.C) + 2 * opponent.history[-20:].count(axl.Action.C)
          if coop_score >= 35:
              self.adaptive_tft = True
              self.random_forgiveness = self._random.randint(5, 16)
          else:
              self.adaptive_tft = False
              self.defect_count = 20
  
      # Check for alternating patterns every 10 rounds
      if current_round - self.last_pattern_check >= 10:
          self.last_pattern_check = current_round
          if len(opponent.history) >= 8:
              last_8 = opponent.history[-8:]
              if all(last_8[i] != last_8[i+1] for i in range(7)):
                  self.adaptive_tft = False
                  self.defect_count = 10
  
      # Exploration phase every 100 rounds
      if current_round - self.last_exploration >= 100 and not self.adaptive_tft:
          if self.exploration_count < 2:
              self.exploration_count += 1
              return axl.Action.C
          else:
              self.last_exploration = current_round
              self.exploration_count = 0
  
      # End game behavior
      if current_round > 950:
          defect_prob = (current_round - 950) / 50
          if self._random.random() < defect_prob:
              return axl.Action.D
  
      # Final round
      if current_round == 999:
          return axl.Action.D
  
      # Adaptive Tit-for-Tat behavior
      if self.adaptive_tft:
          if current_round - self.last_forgiveness >= self.random_forgiveness:
              self.last_forgiveness = current_round
              self.random_forgiveness = self._random.randint(5, 16)
              if self._random.random() < 0.2:
                  return axl.Action.C
          return opponent.history[-1]
  
      # Defect count
      if self.defect_count > 0:
          self.defect_count -= 1
          return axl.Action.D
  
      # Default to opponent's last move
      return opponent.history[-1]

# Here's a revised strategy incorporating the feedback:  1. Start by playing
# Cooperate (C) for the first round.  2. For subsequent rounds, use the
# following decision-making process in order:     a. If this is round 950 or
# later (last 50 rounds):       - If the opponent has defected more than 30% of
# the time in the previous 900 rounds, always Defect (D).       - Otherwise,
# continue with the strategy below.     b. If the opponent has defected in more
# than 70% of the last 100 rounds:       - Play D for the next 10 rounds, then
# return to the main strategy.     c. If the last 20 rounds show a trend of
# increasing defection (e.g., defection rate in last 10 rounds is higher than in
# previous 10):       - Play D for the next 5 rounds, then return to the main
# strategy.     d. If you're in a streak of mutual cooperation for 10 or more
# rounds:       - 90% of the time: Continue playing C.       - 10% of the time:
# Play D as a test. If the opponent responds with C, immediately return to C.
# e. If it's a multiple of 50 rounds (50, 100, 150, etc.):       - Play C
# regardless of the opponent's previous moves.     f. If the opponent's moves
# appear random (close to 50% C and 50% D over the last 30 rounds):       -
# Always play C for the next 10 rounds, then reassess.     g. Main Tit-for-Two-
# Tats strategy:       - If the opponent has played D in the last two
# consecutive rounds, play D.       - Otherwise, play C.     h. Controlled
# randomness:       - 5% of the time, ignore all above rules and play the
# opposite of what the strategy suggests.  3. Throughout the game, maintain a
# long-term memory:    - Track the opponent's overall defection rate.    - If in
# rounds 400-600, and the overall defection rate is less than 20%, occasionally
# play D (10% chance each round) to potentially increase payoff.  This revised
# strategy maintains a cooperative approach while being more robust against
# various opponent behaviors. It adapts to aggressive, cooperative, or random
# play, includes elements of long-term memory and controlled randomness, and
# adjusts its behavior in different stages of the game. The conditions are
# ordered to prioritize end-game considerations, responses to recent aggressive
# behavior, and special situations before falling back to the core Tit-for-Two-
# Tats strategy.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defection_streak = 0
          self.cooperation_streak = 0
          self.random_opponent_streak = 0
          self.test_defection = False
          return axl.Action.C
  
      round_number = len(self.history) + 1
      opponent_history = opponent.history
  
      # End game strategy
      if round_number >= 950:
          if opponent.defections / 900 > 0.3:
              return axl.Action.D
  
      # Check for high defection rate in last 100 rounds
      if len(opponent_history) >= 100:
          recent_defection_rate = opponent_history[-100:].count(axl.Action.D) / 100
          if recent_defection_rate > 0.7:
              self.defection_streak = 10
      
      if self.defection_streak > 0:
          self.defection_streak -= 1
          self.cooperation_streak = 0
          return axl.Action.D
  
      # Check for increasing defection trend
      if len(opponent_history) >= 20:
          last_10_defections = opponent_history[-10:].count(axl.Action.D)
          prev_10_defections = opponent_history[-20:-10].count(axl.Action.D)
          if last_10_defections > prev_10_defections:
              self.defection_streak = 5
              self.cooperation_streak = 0
              return axl.Action.D
  
      # Check for mutual cooperation streak
      if len(self.history) >= 10:
          if all(move == axl.Action.C for move in opponent_history[-10:]) and all(move == axl.Action.C for move in self.history[-10:]):
              self.cooperation_streak += 1
              if self.cooperation_streak >= 10:
                  if self.test_defection:
                      self.test_defection = False
                      if opponent_history[-1] == axl.Action.C:
                          return axl.Action.C
                  elif self._random.random() < 0.1:
                      self.test_defection = True
                      return axl.Action.D
          else:
              self.cooperation_streak = 0
  
      # Play C every 50 rounds
      if round_number % 50 == 0:
          return axl.Action.C
  
      # Check for random opponent
      if len(opponent_history) >= 30:
          defection_rate = opponent_history[-30:].count(axl.Action.D) / 30
          if 0.4 <= defection_rate <= 0.6:
              if self.random_opponent_streak > 0:
                  self.random_opponent_streak -= 1
                  return axl.Action.C
              elif self.random_opponent_streak == 0:
                  self.random_opponent_streak = 10
                  return axl.Action.C
  
      # Main Tit-for-Two-Tats strategy
      if len(opponent_history) >= 2 and opponent_history[-2:] == [axl.Action.D, axl.Action.D]:
          action = axl.Action.D
      else:
          action = axl.Action.C
  
      # Controlled randomness
      if self._random.random() < 0.05:
          action = axl.Action.C if action == axl.Action.D else axl.Action.D
  
      # Long-term memory strategy
      if 400 <= round_number <= 600:
          overall_defection_rate = opponent.defections / len(opponent_history)
          if overall_defection_rate < 0.2 and self._random.random() < 0.1:
              return axl.Action.D
  
      return action

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For the next 9 rounds, mirror
# your opponent's previous move.  3. For the remaining rounds, use the following
# decision-making process in order:     a. Maintain a sliding window of the last
# 20 moves.        b. Calculate the opponent's cooperation rate (CR) within this
# window.        c. If the opponent has played D twice in a row, play D in the
# next round (tit-for-two-tats).        d. If it's one of the last 10 rounds of
# the game, play D with a probability of (n/10), where n is the number of rounds
# left (e.g., 0.5 for the 5th last round).        e. Otherwise, determine your
# play based on the opponent's CR:       - If CR ≥ 0.7, play C with 80%
# probability and D with 20% probability.       - If CR ≤ 0.3, play D with 80%
# probability and C with 20% probability.       - If 0.3 < CR < 0.7, play C with
# probability equal to the CR, and D with probability (1 - CR).  4. Every 10
# rounds, add a small random adjustment (-0.05 to +0.05) to your cooperation
# probability to introduce unpredictability.  This revised strategy addresses
# the previous critiques by: - Using a continuous sliding window for more
# frequent and recent opponent assessment. - Implementing a tit-for-two-tats
# approach for a balance of forgiveness and protection against exploitation. -
# Creating a more gradual shift in cooperation probabilities based on the
# opponent's behavior. - Adding a small random element to increase
# unpredictability. - Maintaining a neutral stance when the opponent's behavior
# is balanced. - Clearly defining conditions for cooperation and defection,
# ordered from most specific to most general.  The strategy remains relatively
# simple while being more adaptive and robust against various opponent
# behaviors. It maintains a neutral approach when the opponent's behavior is
# mixed, becomes more cooperative when faced with a cooperative opponent, and
# more defensive when faced with an aggressive opponent.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.adjustment = 0
          return axl.Action.C
  
      if len(self.history) <= 10:
          return opponent.history[-1]
  
      window = self.history[-20:]
      opponent_window = opponent.history[-20:]
      cr = opponent_window.count(axl.Action.C) / len(opponent_window)
  
      if len(self.history) % 10 == 0:
          self.adjustment = self._random.uniform(-0.05, 0.05)
  
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      total_rounds = self.match_attributes["length"]
      rounds_left = total_rounds - len(self.history)
      if rounds_left <= 10:
          if self._random.random() < rounds_left / 10:
              return axl.Action.D
  
      if cr >= 0.7:
          coop_prob = 0.8
      elif cr <= 0.3:
          coop_prob = 0.2
      else:
          coop_prob = cr + self.adjustment
  
      coop_prob = max(0, min(1, coop_prob))
  
      if self._random.random() < coop_prob:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's the revised strategy, taking into account the feedback:  1. Start by
# playing D (defect) for the first 10 rounds to establish an aggressive stance.
# 2. For the remaining rounds, use the following decision-making process in
# order:     a. If you're behind by 30 or more points, play D for the next 30
# rounds.        b. If you're in the last 100 rounds of the game (rounds
# 901-1000), always play D.        c. If the opponent has cooperated for 5
# consecutive rounds, play D once to test their response.        d. If the
# opponent played D in the previous round, play D.        e. If the opponent
# played C in the previous round:       - Play D with 70% probability       -
# Play C with 30% probability  3. Additionally, track if the opponent seems to
# be alternating between C and D. If a clear alternating pattern is detected
# over 10 rounds, always play D against this pattern.  4. As the game
# progresses, gradually increase the probability of playing D after the
# opponent's cooperation:    - From rounds 1-333: Use the 70% D / 30% C split as
# described above    - From rounds 334-666: Increase to 80% D / 20% C    - From
# rounds 667-900: Increase to 90% D / 10% C    - Rounds 901-1000: Always D (as
# per rule 2b)  This strategy maintains an aggressive approach throughout the
# game while being simpler and more robust. It clearly defines when to cooperate
# or defect, with defection being the dominant choice. The strategy adapts to
# the opponent's behavior, exploits consistent cooperation, and becomes
# increasingly aggressive as the game progresses.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_c_count = 0
          self.alternating_pattern_count = 0
          self.defect_count = 0
          self.last_opponent_action = None
          return axl.Action.D
  
      if len(self.history) < 10:
          return axl.Action.D
  
      if opponent.score - self.score >= 30 and self.defect_count == 0:
          self.defect_count = 30
      
      if self.defect_count > 0:
          self.defect_count -= 1
          return axl.Action.D
  
      if len(self.history) > 900:
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_c_count += 1
      else:
          self.consecutive_c_count = 0
  
      if self.consecutive_c_count == 5:
          self.consecutive_c_count = 0
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      if len(opponent.history) > 1:
          if opponent.history[-1] != opponent.history[-2]:
              self.alternating_pattern_count += 1
          else:
              self.alternating_pattern_count = 0
  
      if self.alternating_pattern_count >= 10:
          return axl.Action.D
  
      defect_probability = 0.7
      if 333 < len(self.history) <= 666:
          defect_probability = 0.8
      elif 666 < len(self.history) <= 900:
          defect_probability = 0.9
  
      return axl.Action.D if self._random.random() < defect_probability else axl.Action.C

# Here's a revised strategy incorporating the feedback:  1. Start by playing C
# (cooperate) for the first 5 rounds to signal willingness to cooperate.  2. For
# each subsequent round, evaluate the following conditions in order:     a. If
# it's one of the last 20 rounds of the game:       - Calculate the opponent's
# cooperation rate over the last 50 rounds.       - If the rate is above 70%,
# play C.       - If the rate is between 30% and 70%, play the opponent's last
# move (Tit-for-Tat).       - If the rate is below 30%, play D.     b. If the
# opponent has played D more than 70% of the time in the last 30 rounds:       -
# Play Tit-for-Tat for the next 20 rounds (play whatever the opponent played in
# the previous round).     c. If it's a randomly selected round (5% chance each
# round):       - Play C to encourage cooperation or break out of negative
# cycles.     d. If the opponent's cooperation rate over the last 100 rounds is
# above 90%:       - 90% of the time play C, 10% of the time play D (to
# occasionally test the opponent).     e. If none of the above conditions are
# met, use a modified Tit-for-Two-Tats approach:       - If the opponent has
# played D in both of the last two rounds, play D.       - Otherwise, play C.
# 3. Every 100 rounds, calculate the overall cooperation rate of both players:
# - If both rates are above 60%, continue with the current strategy.    - If
# your rate is significantly higher (>20% difference), slightly increase the
# defensiveness by changing the Tit-for-Two-Tats threshold to the last three
# rounds instead of two for the next 100 rounds.  4. Keep track of the total
# score difference between you and your opponent:    - If you're behind by more
# than 50 points, increase the random C play chance to 10% for the next 50
# rounds to potentially encourage more mutual cooperation.  This revised
# strategy maintains a cooperative approach while being more adaptive to various
# opponent behaviors. It includes mechanisms to handle the end-game, deal with
# highly aggressive or highly cooperative opponents, and occasionally probe the
# opponent's strategy. The order of conditions ensures that more specific
# situations are handled first, with the default behavior being a modified Tit-
# for-Two-Tats approach.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.defensive_mode = False
          self.random_c_chance = 0.05
          self.tft_counter = 0
          self.defective_threshold = 2
  
      if len(self.history) < 5:
          return axl.Action.C
  
      if len(self.history) > 980:
          last_50_opp = opponent.history[-50:]
          coop_rate = last_50_opp.count(axl.Action.C) / len(last_50_opp)
          if coop_rate > 0.7:
              return axl.Action.C
          elif coop_rate > 0.3:
              return opponent.history[-1]
          else:
              return axl.Action.D
  
      last_30_opp = opponent.history[-30:]
      if len(last_30_opp) >= 30 and last_30_opp.count(axl.Action.D) / len(last_30_opp) > 0.7:
          self.tft_counter = 20
          return opponent.history[-1]
  
      if self.tft_counter > 0:
          self.tft_counter -= 1
          return opponent.history[-1]
  
      if self._random.random() < self.random_c_chance:
          return axl.Action.C
  
      last_100_opp = opponent.history[-100:]
      if len(last_100_opp) == 100 and last_100_opp.count(axl.Action.C) / 100 > 0.9:
          return axl.Action.D if self._random.random() < 0.1 else axl.Action.C
  
      if len(self.history) % 100 == 0 and len(self.history) >= 100:
          my_coop_rate = self.history[-100:].count(axl.Action.C) / 100
          opp_coop_rate = opponent.history[-100:].count(axl.Action.C) / 100
          if my_coop_rate > 0.6 and opp_coop_rate > 0.6:
              self.defensive_mode = False
              self.defective_threshold = 2
          elif my_coop_rate - opp_coop_rate > 0.2:
              self.defensive_mode = True
              self.defective_threshold = 3
  
      if len(self.history) % 50 == 0 and len(self.history) >= 50:
          score_diff = self.score - opponent.score
          if score_diff < -50:
              self.random_c_chance = 0.1
          else:
              self.random_c_chance = 0.05
  
      recent_opponent_actions = opponent.history[-self.defective_threshold:]
      if len(recent_opponent_actions) == self.defective_threshold and all(action == axl.Action.D for action in recent_opponent_actions):
          return axl.Action.D
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. For the
# first round, randomly choose to play C or D with equal probability.  2. For
# the next 9 rounds, mirror your opponent's previous move.  3. After the initial
# 10 rounds, maintain a running average of your opponent's cooperation rate
# (CR). Update this after each round.  4. For the remaining rounds, determine
# your action based on the following conditions, checked in order:     a. If the
# opponent has played D for the last three consecutive rounds, play D.        b.
# If you're significantly behind in total score (more than 50 points), play D
# with 70% probability and C with 30% probability.        c. If it's one of the
# last 5 rounds of the game, play D.        d. Otherwise, set your cooperation
# probability (CP) based on the opponent's cooperation rate (CR):       - CP =
# 0.5 + (CR - 0.5) * 0.5       This formula creates a sliding scale where:
# - If CR = 0, then CP = 0.25       - If CR = 0.5, then CP = 0.5       - If CR =
# 1, then CP = 0.75     e. Add a small random adjustment to CP, between -0.05
# and +0.05.        f. Play C with probability CP, and D with probability (1 -
# CP).  5. Every 50 rounds, check if there's a simple pattern in the opponent's
# last 10 moves:    - If it's "always defect", set CP to 0.1 for the next 10
# rounds.    - If it's "always cooperate", set CP to 0.9 for the next 10 rounds.
# - If it's alternating C and D, mirror this pattern for the next 10 rounds.  6.
# After punishing defection (step 4a) or adjusting for patterns (step 5),
# gradually return to the standard CP calculation over the next 5 rounds.  This
# revised strategy maintains simplicity while addressing the main points of
# feedback. It starts neutrally, adapts to the opponent's behavior using a
# sliding scale, includes protection against exploitation, considers the score
# difference, adds a small random element for unpredictability, and incorporates
# basic pattern recognition. The strategy remains primarily neutral but can
# shift towards cooperation or defection based on the opponent's actions.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.opponent_cr = 0
          self.pattern_check_round = 0
          self.pattern_adjustment = 0
          self.post_punishment_rounds = 0
          self.alternating_counter = 0
          return self._random.random_choice()
  
      if len(self.history) < 10:
          return opponent.history[-1]
  
      self.opponent_cr = opponent.cooperations / len(opponent.history)
  
      if len(self.history) % 50 == 0:
          self.pattern_check_round = len(self.history)
          last_10 = opponent.history[-10:]
          if all(move == axl.Action.D for move in last_10):
              self.pattern_adjustment = -0.4
          elif all(move == axl.Action.C for move in last_10):
              self.pattern_adjustment = 0.4
          elif last_10 == [axl.Action.C, axl.Action.D] * 5:
              self.alternating_counter = 10
  
      if self.alternating_counter > 0:
          self.alternating_counter -= 1
          return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D
  
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.post_punishment_rounds = 5
          return axl.Action.D
  
      if opponent.score - self.score > 50:
          return axl.Action.D if self._random.random() < 0.7 else axl.Action.C
  
      if len(self.history) > 995:
          return axl.Action.D
  
      cp = 0.5 + (self.opponent_cr - 0.5) * 0.5
  
      if self.post_punishment_rounds > 0:
          cp = 0.3 + (cp - 0.3) * (5 - self.post_punishment_rounds) / 5
          self.post_punishment_rounds -= 1
      elif len(self.history) - self.pattern_check_round < 10:
          cp += self.pattern_adjustment
      else:
          adjustment_factor = (len(self.history) - self.pattern_check_round - 10) / 5
          cp += self.pattern_adjustment * max(0, 1 - adjustment_factor)
  
      cp += self._random.uniform(-0.05, 0.05)
      cp = max(0, min(1, cp))
  
      return axl.Action.C if self._random.random() < cp else axl.Action.D

# Here's the revised strategy, taking into account the feedback and focusing on
# clear conditions for cooperation and defection:  1. Start by playing D
# (defect) for the first 3 rounds.  2. After the initial 3 rounds, use the
# following decision-making process in order:     a. If this is one of the last
# 20 rounds of the game, play D.     b. If the opponent has defected 5 times in
# a row, play D for the next 10 rounds.     c. If the opponent has cooperated
# for the last 5 consecutive rounds, play D for this round only.     d. If it's
# a multiple of 25 rounds (25th, 50th, 75th, etc.):       - Calculate the ratio
# of opponent's C to D plays in the last 25 rounds.       - If this ratio is
# above 0.7, play D for this round only.       - If this ratio is below 0.3,
# play D for the next 5 rounds.     e. If the opponent has played C for the last
# 2 consecutive rounds, play C.     f. Otherwise, play D.  3. Repeat step 2 for
# each subsequent round until the game ends.  This strategy maintains an
# aggressive approach while being adaptive to the opponent's behavior. It's
# simpler than the original proposal and provides clear conditions for when to
# cooperate or defect. The order of conditions ensures that more specific or
# time-sensitive rules are checked first, with the general tit-for-tat-like
# behavior serving as a default.  The strategy is aggressive in several ways: -
# It starts with defection. - It quickly punishes repeated defection. - It
# occasionally exploits consistent cooperation. - It becomes fully aggressive in
# the endgame. - It defaults to defection unless the opponent has shown very
# recent cooperation.  At the same time, it allows for cooperation with
# consistently cooperative opponents and can adapt to changes in the opponent's
# strategy throughout the game.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defect_counter = 0
  
      if self.defect_counter > 0:
          self.defect_counter -= 1
          return axl.Action.D
  
      if len(self.history) < 3:
          return axl.Action.D
  
      if len(self.history) > 980:
          return axl.Action.D
  
      if len(opponent.history) >= 5 and all(action == axl.Action.D for action in opponent.history[-5:]):
          self.defect_counter = 10
          return axl.Action.D
  
      if len(opponent.history) >= 5 and all(action == axl.Action.C for action in opponent.history[-5:]):
          return axl.Action.D
  
      if len(self.history) % 25 == 0 and len(self.history) >= 25:
          last_25_actions = opponent.history[-25:]
          c_ratio = last_25_actions.count(axl.Action.C) / 25
          if c_ratio > 0.7:
              return axl.Action.D
          elif c_ratio < 0.3:
              self.defect_counter = 5
              return axl.Action.D
  
      if len(opponent.history) >= 2 and all(action == axl.Action.C for action in opponent.history[-2:]):
          return axl.Action.C
  
      return axl.Action.D

# Here's a revised strategy incorporating the feedback:  1. Start by playing
# Cooperate (C) for the first round.  2. For each subsequent round, evaluate the
# following conditions in order:     a. If it's one of the last 30 rounds:
# - If the opponent has defected more than 60% of the time in the last 30
# rounds, play Defect (D).       - Otherwise, continue with the main strategy
# below.     b. If the opponent has defected more than 70% of the time in the
# last 100 rounds, or more than 60% in the last 30 rounds:       - Use Tit-for-
# Tat for the next 50 rounds (play what the opponent played in the previous
# round).     c. If the last 10 rounds have all been mutual defections:       -
# Play Cooperate (C) for the next 2 rounds to attempt to break the cycle.     d.
# If it's a multiple of 47 rounds (instead of fixed 50):       - Play Cooperate
# (C) as an "olive branch", regardless of recent history.     e. If the
# opponent's last 20 moves appear random (close to 50/50 split between C and D):
# - Play Tit-for-Tat for the next 20 rounds.     f. For all other situations,
# use a modified Tit-for-Two-Tats approach:       - If the opponent played
# Cooperate (C) in either of the last two rounds, play Cooperate (C).       - If
# the opponent played Defect (D) in both of the last two rounds, play Defect
# (D).  3. Every 73 rounds, regardless of the above conditions:    - Play Defect
# (D) once to probe the opponent's strategy, then return to the main strategy.
# This revised strategy maintains a cooperative approach while addressing the
# previously identified weaknesses:  - It adapts to end-game scenarios with a
# more cautious approach. - It includes both long-term and short-term
# evaluations of the opponent's defection rate. - It has a specific mechanism to
# break out of mutual defection cycles. - It uses variable intervals for "olive
# branch" and probing moves to be less predictable. - It includes a way to
# detect and respond to random play. - It maintains the core Tit-for-Two-Tats
# strategy for generally cooperative play.  The strategy remains relatively
# simple while being more robust against various opponent behaviors. The
# conditions are ordered to prioritize adapting to the opponent's recent
# behavior and the game stage, falling back to the standard cooperative strategy
# when no special conditions are met.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.tft_counter = 0
          self.coop_counter = 0
          return axl.Action.C
  
      if len(self.history) >= 970:
          if opponent.history[-30:].count(axl.Action.D) / 30 > 0.6:
              return axl.Action.D
  
      if len(self.history) >= 100:
          if opponent.history[-100:].count(axl.Action.D) / 100 > 0.7 or opponent.history[-30:].count(axl.Action.D) / 30 > 0.6:
              self.tft_counter = 50
              return opponent.history[-1]
  
      if self.tft_counter > 0:
          self.tft_counter -= 1
          return opponent.history[-1]
  
      if len(self.history) >= 10:
          if all(move == axl.Action.D for move in self.history[-10:]) and all(move == axl.Action.D for move in opponent.history[-10:]):
              self.coop_counter = 2
              return axl.Action.C
  
      if self.coop_counter > 0:
          self.coop_counter -= 1
          return axl.Action.C
  
      if len(self.history) % 47 == 0:
          return axl.Action.C
  
      if len(self.history) >= 20:
          opponent_last_20 = opponent.history[-20:]
          if 9 <= opponent_last_20.count(axl.Action.C) <= 11:
              self.tft_counter = 20
              return opponent.history[-1]
  
      if len(self.history) >= 2:
          if axl.Action.C in opponent.history[-2:]:
              return axl.Action.C
          else:
              return axl.Action.D
  
      if len(self.history) % 73 == 0:
          return axl.Action.D
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start with
# alternating C and D for the first 6 rounds (C, D, C, D, C, D) to gather
# initial information while protecting against exploitation.  2. For the next 44
# rounds, use a Tit-for-Tat strategy (mirror your opponent's previous move).  3.
# After these initial 50 rounds, and every 25 rounds thereafter, assess your
# opponent's behavior based on their last 25 moves:    - If they've played C
# more than 75% of the time, consider them cooperative.    - If they've played D
# more than 75% of the time, consider them aggressive.    - Otherwise, consider
# them neutral.  4. For each round, determine your move based on the following
# conditions, checked in order:     a) If the opponent has played D three or
# more times in the last 4 moves:       - Play D with 90% probability, C with
# 10% probability.     b) If you're in the last 100 rounds of the game:       -
# Increase the probability of playing D by 0.5% each round, starting from your
# base probability.     c) If the opponent is classified as cooperative:       -
# Play C with 85% probability, D with 15% probability.     d) If the opponent is
# classified as aggressive:       - Play D with 85% probability, C with 15%
# probability.     e) If the opponent is classified as neutral:       - Play C
# with 65% probability, D with 35% probability.     f) If none of the above
# conditions are met (shouldn't occur, but as a fallback):       - Play C and D
# with equal probability (50/50).  5. After playing D in response to condition
# (a), play C once to allow for cooperation to re-emerge.  6. Adjust the base
# probabilities in conditions (c), (d), and (e) by ±5% based on the cumulative
# score difference between you and your opponent. If you're ahead, increase the
# probability of C; if behind, increase the probability of D.  7. Every 100
# rounds, check for simple patterns in your opponent's last 20 moves (e.g.,
# always D, alternating C/D). If a clear pattern is detected, adjust your
# strategy to best respond to that pattern for the next 10 rounds before
# reverting to the main strategy.  This revised strategy maintains a neutral
# approach while being more adaptive and robust. It starts cautiously, uses
# shorter assessment periods, includes a forgiveness mechanism, adapts to score
# differences, and has a more nuanced end-game approach. The clear ordering of
# conditions ensures that the most important factors (recent defection, end-
# game, opponent classification) are considered in an appropriate sequence.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.opponent_type = "neutral"
          self.last_d_response = False
          self.pattern_detected = False
          self.pattern_counter = 0
  
      if len(self.history) < 6:
          return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D
  
      if 6 <= len(self.history) < 50:
          return opponent.history[-1]
  
      if len(self.history) % 25 == 0:
          last_25_moves = opponent.history[-25:]
          coop_ratio = last_25_moves.count(axl.Action.C) / 25
          if coop_ratio > 0.75:
              self.opponent_type = "cooperative"
          elif coop_ratio < 0.25:
              self.opponent_type = "aggressive"
          else:
              self.opponent_type = "neutral"
  
      if len(self.history) % 100 == 0:
          last_20_moves = opponent.history[-20:]
          if all(move == axl.Action.D for move in last_20_moves):
              self.pattern_detected = "all_defect"
          elif all(move == axl.Action.C for move in last_20_moves):
              self.pattern_detected = "all_cooperate"
          elif all(last_20_moves[i] != last_20_moves[i+1] for i in range(0, 19, 2)):
              self.pattern_detected = "alternating"
          else:
              self.pattern_detected = False
          self.pattern_counter = 10
  
      if self.pattern_detected and self.pattern_counter > 0:
          self.pattern_counter -= 1
          if self.pattern_detected == "all_defect":
              return axl.Action.D
          elif self.pattern_detected == "all_cooperate":
              return axl.Action.C
          elif self.pattern_detected == "alternating":
              return axl.Action.D if len(self.history) % 2 == 0 else axl.Action.C
  
      if opponent.history[-4:].count(axl.Action.D) >= 3:
          if self.last_d_response:
              self.last_d_response = False
              return axl.Action.C
          self.last_d_response = True
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
  
      score_diff = self.score - opponent.score
      prob_adjustment = min(max(-0.05, score_diff / 100), 0.05)
  
      if self.opponent_type == "cooperative":
          coop_prob = 0.85 + prob_adjustment
          return axl.Action.C if self._random.random() < coop_prob else axl.Action.D
      elif self.opponent_type == "aggressive":
          defect_prob = 0.85 - prob_adjustment
          return axl.Action.D if self._random.random() < defect_prob else axl.Action.C
      elif self.opponent_type == "neutral":
          coop_prob = 0.65 + prob_adjustment
          return axl.Action.C if self._random.random() < coop_prob else axl.Action.D
  
      if len(self.history) > 900:
          defect_prob = 0.35 + 0.005 * (len(self.history) - 900)
          return axl.Action.D if self._random.random() < defect_prob else axl.Action.C
  
      return axl.Action.C if self._random.random() < 0.5 else axl.Action.D

# Here's a revised strategy that takes into account the feedback, with clear
# conditions for cooperation and defection:  1. Start by playing D (defect) for
# the first 10 rounds.  2. For the remaining rounds, follow these rules in
# order:     a. If it's the last 100 rounds of the game:       - Play D every
# 3rd round.       - For other rounds, play what your opponent played in the
# previous round.     b. If your opponent has played C for the last 3
# consecutive rounds:       - Play D for the next 2 rounds.     c. If it's a
# multiple of 50 rounds (50, 100, 150, etc.):       - Calculate your average
# score per round.       - If it's below 2.5, play D for the next 10 rounds.
# d. If it's a multiple of 4 rounds (4, 8, 12, etc.):       - Play D.     e. For
# all other situations:       - Play what your opponent played in the previous
# round (tit-for-tat).  This strategy maintains an aggressive stance while
# adapting to the opponent's behavior:  - It starts aggressively with 10 rounds
# of defection. - It exploits consistently cooperative opponents (rule b). - It
# has a mechanism to break out of low-scoring cycles (rule c). - It maintains
# unpredictability with periodic defection (rule d). - It responds in kind to
# the opponent's moves most of the time (rule e). - It increases aggression in
# the endgame (rule a).  The rules are ordered to prioritize certain behaviors:
# - Endgame strategy takes precedence. - Exploiting consistent cooperation is
# next. - Periodic checks and adjustments follow. - The base tit-for-tat
# strategy is used when no other conditions are met.  This strategy is simpler
# than the original, easier to implement, and more robust against various
# opponent behaviors. It maintains aggression while allowing for cooperation and
# adaptation.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defect_counter = 0
      
      if len(self.history) < 10:
          return axl.Action.D
  
      if len(self.history) >= 990:
          if (len(self.history) + 1) % 3 == 0:
              return axl.Action.D
          return opponent.history[-1]
  
      if self.defect_counter > 0:
          self.defect_counter -= 1
          return axl.Action.D
  
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          self.defect_counter = 2
          return axl.Action.D
  
      if (len(self.history) + 1) % 50 == 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2.5:
              self.defect_counter = 10
              return axl.Action.D
  
      if (len(self.history) + 1) % 4 == 0:
          return axl.Action.D
  
      return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) for the first round.  2. For each subsequent round,
# evaluate the following conditions in order:     a. If it's one of the last 10
# rounds, play Defect (D) with a probability of (n/10), where n is the number of
# remaining rounds. For example, in the last round, always defect; in the fifth-
# to-last round, defect with 50% probability.     b. If it's a multiple of 50
# rounds (except for the last 10 rounds), play C to attempt to reset
# cooperation.     c. Calculate the opponent's cooperation rate over the last 20
# moves. If this rate is below 40%, switch to Tit-for-Tat mode: copy the
# opponent's last move.     d. If in Tit-for-Tat mode and the opponent's
# cooperation rate over the last 20 moves exceeds 60%, exit this mode and
# continue with the regular strategy.     e. If the opponent has defected in
# both of the last two rounds, play D.     f. With a 5% probability, make a
# random move (C or D with equal probability) to explore the opponent's
# strategy.     g. If none of the above conditions are met, play C.  3. Keep
# track of any patterns in the opponent's play (e.g., alternating C and D, or
# playing C twice followed by D). If a clear pattern emerges over at least 10
# rounds, adjust your strategy to exploit it for the next 5 rounds, then return
# to the regular strategy.  This revised strategy maintains a cooperative
# approach while addressing the weaknesses identified in the critique. It's more
# adaptive to the opponent's behavior, includes a mechanism for exploration and
# pattern recognition, and makes the end-game less predictable. The conditions
# are ordered to prioritize important decision points (end-game, periodic
# cooperation attempts, and response to recent opponent behavior) while still
# defaulting to cooperation in most cases.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.tit_for_tat_mode = False
          self.pattern_detection = []
          self.pattern_exploitation = 0
          self.exploit_action = None
  
      total_rounds = 1000
      current_round = len(self.history) + 1
      remaining_rounds = total_rounds - current_round + 1
  
      if remaining_rounds <= 10:
          if self._random.random() < remaining_rounds / 10:
              return axl.Action.D
  
      if current_round % 50 == 0 and remaining_rounds > 10:
          return axl.Action.C
  
      recent_moves = opponent.history[-20:]
      if len(recent_moves) == 20:
          cooperation_rate = recent_moves.count(axl.Action.C) / 20
          if cooperation_rate < 0.4:
              self.tit_for_tat_mode = True
          elif cooperation_rate > 0.6:
              self.tit_for_tat_mode = False
  
      if self.tit_for_tat_mode:
          return opponent.history[-1]
  
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])
  
      if len(opponent.history) >= 10:
          self.pattern_detection.append(opponent.history[-1])
          if len(self.pattern_detection) > 10:
              self.pattern_detection.pop(0)
          
          if len(self.pattern_detection) == 10:
              for i in range(1, 6):
                  if self.pattern_detection[:i] * (10 // i) == self.pattern_detection:
                      self.pattern_exploitation = 5
                      pattern = self.pattern_detection[:i]
                      self.exploit_action = axl.Action.D if pattern[(len(self.history) + 1) % len(pattern)] == axl.Action.C else axl.Action.C
                      break
  
      if self.pattern_exploitation > 0:
          self.pattern_exploitation -= 1
          return self.exploit_action
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For the next 19 rounds, mirror
# your opponent's previous move.  3. After the first 20 rounds, and then
# continuously using a rolling 20-round window:    Calculate the frequency of
# your opponent's C plays:    - If > 80%: classify as very cooperative    - If
# 60-80%: classify as cooperative    - If 40-60%: classify as neutral    - If
# 20-40%: classify as aggressive    - If < 20%: classify as very aggressive  4.
# Based on the classification, set your base cooperation rate:    - Very
# cooperative: 95% C    - Cooperative: 80% C    - Neutral: 60% C    -
# Aggressive: 30% C    - Very aggressive: 10% C  5. Adjust your next move based
# on the following conditions, checked in order:    a) If it's one of the last
# 15 rounds:       - If you're behind in total score, always play D       - If
# you're ahead, play your base cooperation rate        b) If the opponent has
# played D for the last 3 rounds:       Play D for 1 to 3 rounds (randomly
# chosen), then return to base rate        c) If you've played D for the last 2
# rounds:       Play C with 90% probability, regardless of base rate        d)
# If none of the above conditions are met:       Play C with probability equal
# to your current base cooperation rate  6. Every 50 rounds, with a 10% chance:
# Randomly adjust your base cooperation rates by ±5% for each classification
# (keeping within 0-100% bounds) to explore potentially better strategies.  This
# revised strategy: - Uses a longer initial assessment period - Implements a
# sliding window for continuous behavior assessment - Has more nuanced opponent
# classifications - Includes a sophisticated end-game approach - Adds a small
# random factor for exploration - Maintains a neutral baseline for neutral
# opponents - Includes a mechanism to break out of mutual defection cycles -
# Orders the conditions clearly for when to cooperate or defect  The strategy
# remains relatively simple while addressing the main points of feedback, making
# it more robust against various opponent types and adaptive to changing
# behaviors.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.base_rates = {
              'very_cooperative': 0.95,
              'cooperative': 0.80,
              'neutral': 0.60,
              'aggressive': 0.30,
              'very_aggressive': 0.10
          }
          self.last_adjustment = 0
          self.defection_counter = 0
          self.coop_count = 0
          return axl.Action.C
  
      if len(self.history) < 20:
          return opponent.history[-1]
  
      self.coop_count += int(opponent.history[-1] == axl.Action.C)
      if len(self.history) >= 20:
          self.coop_count -= int(opponent.history[-20] == axl.Action.C)
  
      opponent_c_freq = self.coop_count / 20
  
      if opponent_c_freq > 0.8:
          classification = 'very_cooperative'
      elif opponent_c_freq > 0.6:
          classification = 'cooperative'
      elif opponent_c_freq > 0.4:
          classification = 'neutral'
      elif opponent_c_freq > 0.2:
          classification = 'aggressive'
      else:
          classification = 'very_aggressive'
  
      base_rate = self.base_rates[classification]
  
      if len(self.history) >= 985:
          if self.score < opponent.score:
              return axl.Action.D
          else:
              return axl.Action.C if self._random.random() < base_rate else axl.Action.D
  
      if opponent.history[-3:].count(axl.Action.D) == 3 and self.defection_counter == 0:
          self.defection_counter = self._random.randint(1, 3)
  
      if self.defection_counter > 0:
          self.defection_counter -= 1
          return axl.Action.D
  
      if self.history[-2:].count(axl.Action.D) == 2:
          return axl.Action.C if self._random.random() < 0.9 else axl.Action.D
  
      if len(self.history) - self.last_adjustment >= 50 and self._random.random() < 0.1:
          self.last_adjustment = len(self.history)
          for key in self.base_rates:
              adjustment = self._random.uniform(-0.05, 0.05)
              self.base_rates[key] = max(0, min(1, self.base_rates[key] + adjustment))
  
      return axl.Action.C if self._random.random() < base_rate else axl.Action.D

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing D (defect) for the first 5 rounds to establish an initial aggressive
# stance.  2. For the remainder of the game, use the following decision-making
# process in order:     a. If it's one of the last 50 rounds, play D with 70%
# probability and C with 30% probability.     b. If the opponent has defected in
# the last 3 rounds consecutively, play D with 90% probability and C with 10%
# probability (forgiveness mechanism).     c. If the opponent's overall
# cooperation rate (calculated as a rolling average of their last 50 moves) is:
# - Above 70%: Play D (exploit their cooperation)       - Between 40% and 70%:
# Play Tit-for-Tat (copy their last move)       - Below 40%: Play D with 80%
# probability and C with 20% probability     d. If none of the above conditions
# are met, play a modified Tit-for-Tat:       - If the opponent's last move was
# C, play C       - If the opponent's last move was D, play D with 80%
# probability and C with 20% probability  3. Override rules:     - Every 30-50
# rounds (randomly determined), play D for 2 consecutive rounds regardless of
# other conditions. This serves as an aggressive probe.    - If your own score
# is lagging behind the opponent's by more than 20 points (based on an estimate
# from recent rounds), increase the probability of playing D by an additional
# 10% in all cases for the next 10 rounds.  This strategy maintains an
# aggressive approach while being more adaptive and less predictable. It takes
# into account the opponent's recent and overall behavior, includes a
# forgiveness mechanism to break out of mutual defection cycles, and adjusts
# based on the game's progress and score difference. The conditions are ordered
# to prioritize end-game strategy, response to recent defections, overall
# opponent behavior, and then default to a modified Tit-for-Tat approach.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.aggressive_probe_counter = 0
          self.last_probe_round = 0
          self.score_lag_counter = 0
  
      current_round = len(self.history)
  
      # First 5 rounds: Defect
      if current_round < 5:
          return axl.Action.D
  
      # Last 50 rounds
      if current_round > 950:
          return self._random.random_choice(0.7)
  
      # Check for consecutive defections in last 3 rounds
      if opponent.history[-3:].count(axl.Action.D) == 3:
          return self._random.random_choice(0.9)
  
      # Calculate opponent's cooperation rate (last 50 moves or all if fewer)
      recent_history = opponent.history[-50:] if len(opponent.history) > 50 else opponent.history[:]
      coop_rate = recent_history.count(axl.Action.C) / len(recent_history)
  
      # Adjust strategy based on cooperation rate
      if coop_rate > 0.7:
          action = axl.Action.D
      elif 0.4 <= coop_rate <= 0.7:
          action = opponent.history[-1]
      elif coop_rate < 0.4:
          action = self._random.random_choice(0.8)
      else:
          # Modified Tit-for-Tat
          if opponent.history[-1] == axl.Action.C:
              action = axl.Action.C
          else:
              action = self._random.random_choice(0.8)
  
      # Aggressive probe
      if current_round - self.last_probe_round >= self._random.randint(30, 51):
          self.aggressive_probe_counter = 2
          self.last_probe_round = current_round
  
      if self.aggressive_probe_counter > 0:
          self.aggressive_probe_counter -= 1
          return axl.Action.D
  
      # Check score difference
      if self.score < opponent.score - 20:
          self.score_lag_counter = 10
  
      if self.score_lag_counter > 0:
          self.score_lag_counter -= 1
          defect_probability = 0.9 if action == axl.Action.D else 0.8
          return self._random.random_choice(defect_probability)
  
      return action

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing cooperatively (C) for the first 5 rounds to signal willingness to
# cooperate.  2. For the remainder of the game, use the following decision
# process in order:     a. If this is the final round (1000th), play D.     b.
# If the opponent has defected in 8 or more of the last 10 rounds, enter a
# defensive mode:       - Play D with 80% probability and C with 20%
# probability.       - Stay in this mode for 20 rounds or until the opponent
# cooperates 3 times in a row.     c. If not in defensive mode, use a modified
# Tit-for-Tat approach:       - If the opponent played C in the previous round,
# play C.       - If the opponent played D in the previous round:         * Play
# D with a probability of 90%.         * Play C with a probability of 10%
# (forgiveness).     d. Every 40-60 rounds (randomly determined), play C
# regardless of the opponent's last move. This serves as an "olive branch" to
# potentially break cycles of mutual defection.  3. Adaptive elements:    -
# Track the opponent's cooperation rate over the entire game.    - Every 100
# rounds, adjust the strategy:      * If the opponent's overall cooperation rate
# is above 70%, increase the forgiveness rate by 5% (up to a maximum of 25%).
# * If the opponent's overall cooperation rate is below 30%, decrease the
# forgiveness rate by 5% (down to a minimum of 5%).  4. End-game adjustment:
# - In the last 50 rounds, if the opponent's overall cooperation rate is below
# 50%, gradually increase the probability of defection by 1% each round.    - If
# the opponent's overall cooperation rate is 50% or above, continue with the
# standard strategy until the final round.  This revised strategy maintains a
# cooperative approach while being more adaptive and robust against various
# opponent behaviors. It clearly defines conditions for cooperation and
# defection, with more aggressive responses to consistently uncooperative
# opponents and more forgiving behavior towards cooperative ones. The strategy
# also includes elements to break out of negative cycles and adapts its
# forgiveness rate based on the opponent's overall behavior.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.defensive_mode = False
          self.defensive_count = 0
          self.consecutive_c = 0
          self.forgiveness_rate = 0.1
          self.last_olive_branch = 0
          self.next_olive_branch = self._random.randint(40, 60)
  
      if len(self.history) < 5:
          return axl.Action.C
  
      if len(self.history) == 999:
          return axl.Action.D
  
      if len(self.history) - self.last_olive_branch >= self.next_olive_branch:
          self.last_olive_branch = len(self.history)
          self.next_olive_branch = self._random.randint(40, 60)
          return axl.Action.C
  
      if self.defensive_mode:
          self.defensive_count += 1
          if opponent.history[-1] == axl.Action.C:
              self.consecutive_c += 1
          else:
              self.consecutive_c = 0
  
          if self.defensive_count >= 20 or self.consecutive_c >= 3:
              self.defensive_mode = False
              self.defensive_count = 0
              self.consecutive_c = 0
          else:
              return axl.Action.D if self._random.random() < 0.8 else axl.Action.C
  
      if opponent.history[-10:].count(axl.Action.D) >= 8:
          self.defensive_mode = True
          return axl.Action.D
  
      if len(self.history) % 100 == 0:
          coop_rate = opponent.cooperations / len(opponent.history)
          if coop_rate > 0.7:
              self.forgiveness_rate = min(0.25, self.forgiveness_rate + 0.05)
          elif coop_rate < 0.3:
              self.forgiveness_rate = max(0.05, self.forgiveness_rate - 0.05)
  
      if len(self.history) >= 950:
          coop_rate = opponent.cooperations / len(opponent.history)
          if coop_rate < 0.5:
              defect_prob = 0.9 + (len(self.history) - 950) * 0.01
              if self._random.random() < defect_prob:
                  return axl.Action.D
  
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D if self._random.random() > self.forgiveness_rate else axl.Action.C

# Here's a revised strategy that takes into account the feedback while
# maintaining a neutral approach and simplifying the decision-making process:
# 1. Start by playing C (cooperate) for the first round.  2. For each subsequent
# round, follow these steps in order:     a. If the opponent has played D for
# the last 3 consecutive rounds, play D.        b. If your cumulative score is
# more than 30 points behind your opponent's, play D.        c. If you're in the
# last 50 rounds of the game and the opponent's overall cooperation rate is
# below 40%, play D.        d. If none of the above conditions are met, mirror
# the opponent's previous move.  3. Every 20 rounds, with a 5% chance, play a
# random move instead of following the above rules. This serves as a probing
# mechanism and adds unpredictability.  4. Maintain a rolling average of the
# opponent's cooperation rate over the last 50 moves, updated each round. This
# rolling average is used for the calculations in step 2c.  5. If at any point
# the opponent cooperates for 5 consecutive rounds, reset any ongoing D streaks
# and return to mirroring (unless other conditions in step 2 apply).  This
# strategy: - Starts cooperatively but is prepared to defend against
# exploitation. - Uses mirroring as its default behavior, maintaining a neutral
# approach. - Responds to short-term aggressive behavior (3 consecutive D's). -
# Has a score catch-up mechanism with a lower threshold. - Adapts to long-term
# behavior in the endgame. - Includes a forgiveness mechanism to allow a return
# to cooperation. - Uses a rolling average for more responsive adaptation. -
# Incorporates occasional random moves for probing and unpredictability.  The
# strategy is simpler than the previous version, with clear conditions for
# cooperation and defection. It maintains its core neutral approach through
# mirroring while being more robust against various opponent strategies. The
# order of conditions ensures that short-term threats and significant score
# deficits are addressed before considering long-term behavior, with mirroring
# as the default when no special conditions are met.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.rolling_coop_rate = 0
          self.coop_count = 0
          self.round_count = 0
          self.consecutive_d_count = 0
          self.consecutive_c_count = 0
  
      if not self.history:
          return axl.Action.C
  
      if len(self.history) % 20 == 0 and self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])
  
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_c_count += 1
          self.consecutive_d_count = 0
      else:
          self.consecutive_c_count = 0
          self.consecutive_d_count += 1
  
      if self.consecutive_c_count == 5:
          self.consecutive_d_count = 0
  
      self.round_count += 1
      if opponent.history[-1] == axl.Action.C:
          self.coop_count += 1
      if self.round_count > 50:
          self.coop_count -= self.history[-51] == opponent.history[-51] == axl.Action.C
      self.rolling_coop_rate = self.coop_count / min(50, self.round_count)
  
      if self.consecutive_d_count >= 3:
          return axl.Action.D
  
      if opponent.score - self.score > 30:
          return axl.Action.D
  
      if len(self.history) > 950 and self.rolling_coop_rate < 0.4:
          return axl.Action.D
  
      return opponent.history[-1]

# Here's a rewritten strategy that takes into account the feedback, with clear
# conditions for cooperation and defection, ordered appropriately:  1. For the
# first 20 rounds: Always defect (D).  2. For rounds 21-950:    a. If the
# opponent defected in the previous round: Defect (D).    b. If the opponent
# cooperated in the previous round:       - With 70% probability: Defect (D).
# - With 30% probability: Cooperate (C).    c. Exception: Every 100th round
# (100, 200, 300, etc.):       - Cooperate (C) for this round and the next.
# - On the round immediately following these two cooperative rounds:         -
# If the opponent cooperated in both previous rounds: Defect (D).         -
# Otherwise: Follow rules 2a and 2b.  3. For the last 50 rounds (951-1000):
# Always defect (D).  This strategy maintains an aggressive approach while being
# simple and clear about when to cooperate or defect. It's ordered to prioritize
# defection in most cases, with limited cooperation to test and potentially
# exploit cooperative opponents. The end-game strategy is explicitly aggressive
# to maximize final payoffs.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if len(self.history) < 20:
          return axl.Action.D
      
      if len(self.history) >= 950:
          return axl.Action.D
      
      current_round = len(self.history) + 1
      
      if current_round % 100 == 0 or current_round % 100 == 1:
          return axl.Action.C
      
      if current_round % 100 == 2:
          if opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
              return axl.Action.D
          else:
              if opponent.history[-1] == axl.Action.D:
                  return axl.Action.D
              if self._random.random() < 0.7:
                  return axl.Action.D
              else:
                  return axl.Action.C
      
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      
      if self._random.random() < 0.7:
          return axl.Action.D
      else:
          return axl.Action.C

# Here's a revised strategy that incorporates the feedback:  1. Start by playing
# Cooperate (C) for the first 3 rounds to signal willingness to cooperate.  2.
# After the initial 3 rounds, use the following decision-making process in
# order:     a. If it's one of the last 10 rounds of the game:       - If you're
# behind in total score, play Defect (D).       - If you're ahead or tied,
# continue with the strategy below.     b. If the opponent has defected more
# than 60% of the time in the last 15 rounds:       - Play D for the next 5
# rounds.       - Then return to step 2c.     c. Use a modified "Tit-for-Two-
# Tats" approach:       - If the opponent's last two moves were both D, play D.
# - Otherwise, play C.     d. Override the above decisions with a 5%
# probability:       - If the decision was to play C, play D instead.       - If
# the decision was to play D, play C instead.       This "probe" helps gather
# information about the opponent's strategy.  3. Maintain a "grudge" counter:
# - Increment by 1 for each opponent defection.    - Decrement by 1 (but not
# below 0) for each opponent cooperation.    - If the grudge counter exceeds 10,
# always play D for the next 3 rounds, then reset the counter to 5.  4. Every 40
# rounds, if there have been at least 5 mutual defections in the last 10 rounds:
# - Play C regardless of other conditions (except end-game).    - This serves as
# an "olive branch" to potentially reset a cycle of mutual defection.  5. Adjust
# forgiveness:    - Track the opponent's cooperation rate over the last 50
# moves.    - If it's above 70%, be more forgiving: in step 2c, only play D if
# the opponent's last three moves were all D.    - If it's below 30%, be less
# forgiving: in step 2c, play D if either of the opponent's last two moves was
# D.  This strategy maintains a cooperative approach while being more robust
# against various opponent behaviors. It adapts to the opponent's level of
# cooperation, includes mechanisms to break out of defection cycles, and adjusts
# its end-game behavior based on the overall score. The clear conditions for
# cooperation and defection, ordered by priority, make the strategy more
# straightforward to implement and understand.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.grudge_counter = 0
          self.defect_streak = 0
  
      if len(self.history) < 3:
          return axl.Action.C
  
      if len(self.history) > 990:
          if self.score <= opponent.score:
              return axl.Action.D
  
      recent_15 = opponent.history[-15:]
      if len(recent_15) == 15 and recent_15.count(axl.Action.D) / 15 > 0.6:
          self.defect_streak = 5
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      if self.grudge_counter > 10:
          if len(self.history) % 3 < 3:
              return axl.Action.D
          else:
              self.grudge_counter = 5
  
      if len(self.history) % 40 == 0 and len(self.history) >= 40:
          last_10 = list(zip(self.history[-10:], opponent.history[-10:]))
          mutual_defections = sum(1 for a, b in last_10 if a == axl.Action.D and b == axl.Action.D)
          if mutual_defections >= 5:
              return axl.Action.C
  
      recent_50 = opponent.history[-50:]
      if len(recent_50) == 50:
          coop_rate = recent_50.count(axl.Action.C) / 50
          if coop_rate > 0.7:
              decision = axl.Action.D if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D] else axl.Action.C
          elif coop_rate < 0.3:
              decision = axl.Action.D if axl.Action.D in opponent.history[-2:] else axl.Action.C
          else:
              decision = axl.Action.D if opponent.history[-2:] == [axl.Action.D, axl.Action.D] else axl.Action.C
      else:
          decision = axl.Action.D if opponent.history[-2:] == [axl.Action.D, axl.Action.D] else axl.Action.C
  
      if opponent.history[-1] == axl.Action.D:
          self.grudge_counter += 1
      elif self.grudge_counter > 0:
          self.grudge_counter -= 1
  
      if self._random.random() < 0.05:
          decision = axl.Action.D if decision == axl.Action.C else axl.Action.C
  
      return decision

# Here's a revised strategy that incorporates the feedback:  1. Start by playing
# C (cooperate) for the first 5 rounds to establish an initial cooperative
# stance.  2. Throughout the game, maintain two records:    - Long-term record:
# The percentage of C and D plays by the opponent over all previous rounds.    -
# Short-term record: The percentage of C and D plays by the opponent in the last
# 20 rounds.  3. From round 6 onwards, make your decision in the following
# order:     a. Pattern recognition:       - If the opponent has played an
# alternating pattern (CDCDCD or DCDCDC) for the last 6 rounds, play the move
# that beats their next expected move.       - If the opponent has played Tit-
# for-Tat for the last 6 rounds, play C.     b. Score-based adjustment:       -
# If your score is more than 50 points behind the opponent's, lower the
# cooperation threshold to 55% for the next 20 rounds.     c. Recent behavior
# response:       - If the opponent's short-term C percentage is above 65%, play
# C.       - If the opponent's short-term D percentage is above 65%, play D.
# d. Long-term behavior response:       - If the opponent's long-term C
# percentage is above 60%, play C.       - If the opponent's long-term D
# percentage is above 60%, play D.     e. Neutral stance:       - If none of the
# above conditions are met, randomly choose C or D with equal probability.  4.
# Probing mechanism:    - With a 5% probability, ignore the above rules and play
# a random move (C or D with equal probability).  5. Forgiveness mechanism:    -
# If you and your opponent have both played D for the last 5 rounds, play C once
# to attempt breaking the cycle.  6. End-game adjustment (last 50 rounds):    -
# Lower the cooperation thresholds by 5% in steps c and d above.  7. Update both
# short-term and long-term records after each round.  This revised strategy
# maintains a neutral approach while being more responsive to various opponent
# behaviors. It prioritizes reacting to clear patterns and recent behavior,
# adjusts based on score difference, and includes mechanisms for probing and
# forgiveness. The conditions for cooperation and defection are clearly stated
# and ordered from most specific to most general, allowing for a more nuanced
# response to the opponent's actions.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.long_term_c = 0
          self.long_term_d = 0
          self.short_term_c = 0
          self.short_term_d = 0
          self.cooperation_threshold = 0.60
          self.defection_threshold = 0.60
          self.lowered_threshold_rounds = 0
  
      if len(self.history) < 5:
          return axl.Action.C
  
      if len(self.history) >= 950:  # End-game adjustment
          self.cooperation_threshold = max(self.cooperation_threshold - 0.05, 0.55)
          self.defection_threshold = max(self.defection_threshold - 0.05, 0.55)
  
      # Update records
      self.long_term_c = opponent.history.cooperations
      self.long_term_d = opponent.history.defections
      self.short_term_c = opponent.history[-20:].count(axl.Action.C)
      self.short_term_d = opponent.history[-20:].count(axl.Action.D)
  
      # Probing mechanism
      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])
  
      # Forgiveness mechanism
      if len(self.history) >= 5 and all(move == axl.Action.D for move in self.history[-5:]) and all(move == axl.Action.D for move in opponent.history[-5:]):
          return axl.Action.C
  
      # Pattern recognition
      if len(self.history) >= 6:
          if opponent.history[-6:] == [axl.Action.C, axl.Action.D] * 3:
              return axl.Action.D
          elif opponent.history[-6:] == [axl.Action.D, axl.Action.C] * 3:
              return axl.Action.C
          elif opponent.history[-6:] == self.history[-7:-1]:
              return axl.Action.C
  
      # Score-based adjustment
      if opponent.score - self.score > 50:
          self.cooperation_threshold = 0.55
          self.lowered_threshold_rounds = 20
  
      # Recent behavior response
      short_term_total = self.short_term_c + self.short_term_d
      if short_term_total > 0:
          if self.short_term_c / short_term_total > 0.65:
              return axl.Action.C
          elif self.short_term_d / short_term_total > 0.65:
              return axl.Action.D
  
      # Update cooperation threshold
      if self.lowered_threshold_rounds > 0:
          self.lowered_threshold_rounds -= 1
      else:
          self.cooperation_threshold = 0.60
  
      # Long-term behavior response
      long_term_total = self.long_term_c + self.long_term_d
      if long_term_total > 0:
          if self.long_term_c / long_term_total > self.cooperation_threshold:
              return axl.Action.C
          elif self.long_term_d / long_term_total > self.defection_threshold:
              return axl.Action.D
  
      # Neutral stance
      return self._random.choice([axl.Action.C, axl.Action.D])

# Here's the revised strategy, taking into account the feedback:  1. Initial
# Phase (Rounds 1-5):    - Always defect (D) for the first 5 rounds.  2. Main
# Phase (Rounds 6-900):    - Use a modified Tit-for-Tat approach with the
# following conditions, checked in order:      a. If the opponent has defected
# in the last 3 consecutive rounds, defect (D) for the next 5 rounds.      b. If
# it's not one of those 5 punishment rounds, play the same move the opponent
# played in the previous round (classic Tit-for-Tat).      c. Regardless of the
# above, randomly defect (D) with a 10% probability each round.  3. End Game
# Phase (Rounds 901-1000):    - Continue with the modified Tit-for-Tat approach,
# but increase the random defection probability:      a. For rounds 901-950,
# randomly defect with a 30% probability.      b. For rounds 951-1000, randomly
# defect with a 50% probability.  This strategy will defect (D) when: - It's in
# the initial 5 rounds - The opponent has defected for 3 consecutive rounds
# (triggering 5 rounds of defection) - It's mirroring the opponent's defection
# from the previous round - The random defection probability triggers (10% in
# main phase, 30% or 50% in end game)  It will cooperate (C) when: - It's
# mirroring the opponent's cooperation from the previous round - It's not in the
# initial 5 rounds, not in a punishment period, and the random defection doesn't
# trigger  This strategy maintains an aggressive stance through initial
# defection, punishment for repeated defection, and increasing random
# defections. It's simple, adaptable, and robust against various opponent
# behaviors while still allowing for cooperation when beneficial.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.punishment_rounds = 0
  
      round_number = len(self.history) + 1
  
      # Initial Phase (Rounds 1-5)
      if round_number <= 5:
          return axl.Action.D
  
      # Check if in punishment mode
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Check for 3 consecutive defections
      if len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          self.punishment_rounds = 5
          return axl.Action.D
  
      # Determine the phase and set random defection probability
      if round_number <= 900:
          random_defect_prob = 0.1
      elif round_number <= 950:
          random_defect_prob = 0.3
      else:
          random_defect_prob = 0.5
  
      # Modified Tit-for-Tat (default behavior)
      action = opponent.history[-1]
  
      # Random defection check
      if self._random.random() < random_defect_prob:
          action = axl.Action.D
  
      return action

# Here's a revised strategy incorporating the feedback:  1. Start by playing
# cooperatively (C) for the first 5 rounds to signal willingness to cooperate.
# 2. Throughout the game, maintain a rolling cooperation rate of your opponent
# over the last 20 rounds.  3. For each round from 6 to 990, play according to
# these ordered conditions:     a. If it's a "probe round" (1% chance), randomly
# choose C or D to test opponent's reaction.        b. If it's an "olive branch
# round" (every 45-55 rounds, randomly determined), play C.        c. If the
# opponent's cooperation rate is below 30%, enter "defensive mode":       - Play
# D for the next 10 rounds       - Then return to the main strategy        d. If
# the opponent defected in the last round AND defected in the round before that,
# play D.        e. If the opponent defected only in the last round, forgive
# with a probability equal to their cooperation rate. If forgiving, play C;
# otherwise, play D.        f. If none of the above conditions are met, play C.
# 4. For the final 10 rounds (991-1000):    - If the opponent's overall
# cooperation rate is above 70%, continue with the main strategy.    - If the
# opponent's overall cooperation rate is between 30% and 70%, play Tit-for-Tat
# (copy their last move).    - If the opponent's overall cooperation rate is
# below 30%, play D.  This strategy: - Starts cooperatively - Adapts to the
# opponent's behavior using their cooperation rate - Includes occasional probing
# moves to test the opponent - Has a flexible "olive branch" mechanism to break
# defection cycles - Responds more quickly to exploitation while still allowing
# for forgiveness - Adjusts the end-game strategy based on the opponent's
# overall behavior - Maintains a primarily cooperative approach while
# incorporating defensive measures against persistent defectors  The ordered
# conditions ensure that the strategy responds appropriately to different
# situations, with more critical conditions (like defensive mode) taking
# precedence over standard cooperative play.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.match_length = self.match_attributes['length']
          self.olive_branch_counter = self._random.randint(45, 55)
          self.defensive_mode_counter = 0
  
      if len(self.history) < 5:
          return axl.Action.C
  
      if len(self.history) > 20:
          opponent_coop_rate = opponent.history[-20:].count(axl.Action.C) / 20
      else:
          opponent_coop_rate = opponent.cooperations / len(opponent.history)
  
      if len(self.history) >= self.match_length - 10:
          overall_coop_rate = opponent.cooperations / len(opponent.history)
          if overall_coop_rate > 0.7:
              pass  # Continue with main strategy
          elif 0.3 <= overall_coop_rate <= 0.7:
              return opponent.history[-1]
          else:
              return axl.Action.D
  
      if self.defensive_mode_counter > 0:
          self.defensive_mode_counter -= 1
          return axl.Action.D
  
      if opponent_coop_rate < 0.3:
          self.defensive_mode_counter = 10
          return axl.Action.D
  
      if self._random.random() < 0.01:
          return self._random.choice([axl.Action.C, axl.Action.D])
  
      self.olive_branch_counter -= 1
      if self.olive_branch_counter == 0:
          self.olive_branch_counter = self._random.randint(45, 55)
          return axl.Action.C
  
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.D:
          if self._random.random() < opponent_coop_rate:
              return axl.Action.C
          else:
              return axl.Action.D
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For rounds 2-20, use Tit-for-
# Tat: play what your opponent played in the previous round.  3. From round 21
# onwards, calculate the opponent's cooperation rate every 20 rounds. This rate
# is based on their moves in the last 100 rounds (or all previous rounds if
# fewer than 100 have been played).  4. After calculating the cooperation rate,
# decide your next move based on the following conditions, checked in this
# order:     a. If the game is in the last 100 rounds:       - Increase the
# probability of playing D by 0.5% each round.       - If this probability
# exceeds the opponent's cooperation rate, play D; otherwise, proceed to the
# next conditions.     b. If the opponent has played C for the last 3
# consecutive rounds:       - Play C (to encourage cooperation streaks).     c.
# If the opponent's cooperation rate is 65% or higher:       - Play C with 95%
# probability, D with 5% probability.     d. If the opponent's cooperation rate
# is between 35% and 65%:       - Mirror the opponent's last move with 90%
# probability.       - Play the opposite of the opponent's last move with 10%
# probability.     e. If the opponent's cooperation rate is below 35%:       -
# Play D with 90% probability, C with 10% probability.  5. Forgiveness
# Mechanism: Regardless of the above conditions, if you have played D for 10
# consecutive rounds:    - Play C for the next round to allow for recovery from
# mutual defection.  6. Pattern Recognition: If you detect that the opponent has
# alternated C and D for the last 6 moves:    - Play D for the next 2 rounds to
# counter this strategy.  This revised strategy maintains a neutral approach
# while addressing the main points of feedback: - It starts simply with Tit-for-
# Tat. - It adapts more frequently by recalculating every 20 rounds. - It uses a
# forgiveness mechanism to break cycles of mutual defection. - It implements a
# gradual end-game transition. - It includes a basic pattern recognition
# component. - It incorporates small probabilities of "mistakes" to handle noise
# and reduce predictability.  The strategy remains relatively simple while being
# more robust against various opponent behaviors. The conditions are clearly
# stated and ordered to prioritize certain behaviors (like end-game
# considerations and encouraging cooperation streaks) over others.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.consecutive_d = 0
          self.last_cooperation_rate = 0
          self.last_calculation_round = 0
          return axl.Action.C
  
      if len(self.history) <= 20:
          return opponent.history[-1]
  
      if len(self.history) - self.last_calculation_round >= 20:
          self.last_calculation_round = len(self.history)
          cooperation_history = opponent.history[-100:] if len(opponent.history) > 100 else opponent.history[:]
          self.last_cooperation_rate = cooperation_history.count(axl.Action.C) / len(cooperation_history)
  
      # Forgiveness Mechanism
      if self.consecutive_d >= 10:
          self.consecutive_d = 0
          return axl.Action.C
  
      # Pattern Recognition
      if len(opponent.history) >= 6 and opponent.history[-6:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
          self.consecutive_d += 1
          return axl.Action.D
  
      # End-game strategy
      if self.match_attributes["length"] - len(self.history) <= 100:
          end_game_defect_prob = min(0.005 * (len(self.history) - (self.match_attributes["length"] - 100)), 1)
          if self._random.random() < end_game_defect_prob and self._random.random() > self.last_cooperation_rate:
              self.consecutive_d += 1
              return axl.Action.D
  
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          self.consecutive_d = 0
          return axl.Action.C
  
      if self.last_cooperation_rate >= 0.65:
          if self._random.random() < 0.95:
              self.consecutive_d = 0
              return axl.Action.C
          else:
              self.consecutive_d += 1
              return axl.Action.D
  
      if 0.35 <= self.last_cooperation_rate < 0.65:
          if self._random.random() < 0.9:
              if opponent.history[-1] == axl.Action.C:
                  self.consecutive_d = 0
                  return axl.Action.C
              else:
                  self.consecutive_d += 1
                  return axl.Action.D
          else:
              if opponent.history[-1] == axl.Action.C:
                  self.consecutive_d += 1
                  return axl.Action.D
              else:
                  self.consecutive_d = 0
                  return axl.Action.C
  
      if self.last_cooperation_rate < 0.35:
          if self._random.random() < 0.9:
              self.consecutive_d += 1
              return axl.Action.D
          else:
              self.consecutive_d = 0
              return axl.Action.C
  
      # Default to Tit-for-Tat if no condition is met
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_d = 0
          return axl.Action.C
      else:
          self.consecutive_d += 1
          return axl.Action.D

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing D (defect) for the first 5 rounds to establish an aggressive stance.
# 2. For the remainder of the game, use a sliding window of the last 20 moves to
# determine the opponent's behavior. Calculate the percentage of C (cooperative)
# moves in this window.  3. Base your moves on the following conditions, checked
# in this order:     a. If it's one of the last 50 rounds of the game:       -
# If the opponent's cooperation rate in the sliding window is > 70%, play D to
# exploit their cooperation.       - Otherwise, play C if the round number is
# odd, and D if it's even, to mix cooperation and defection unpredictably.
# b. If the opponent's cooperation rate in the sliding window is < 30%:       -
# Play D 90% of the time.       - Play C 10% of the time to occasionally test
# for a change in the opponent's strategy.     c. If the opponent's cooperation
# rate in the sliding window is between 30% and 70%:       - Play Tit-for-Tat
# (copy the opponent's last move).     d. If the opponent's cooperation rate in
# the sliding window is > 70%:       - Play D 70% of the time to exploit their
# cooperation.       - Play C 30% of the time to encourage continued
# cooperation.  4. Every 50 rounds, regardless of the above conditions:    - If
# your total score is higher than what you'd have if every round was mutual
# cooperation (3 points), play D for this round to increase your lead.    - If
# your total score is lower, play C for this round to encourage mutual
# cooperation.  5. Add controlled randomness: On 5% of moves, chosen randomly,
# ignore the above rules and:    - Play C if the last move was D.    - Play D if
# the last move was C.  This revised strategy maintains an aggressive stance
# while being simpler and more adaptable. It uses a sliding window for quicker
# adaptation, includes controlled randomness to be less predictable, and has a
# more nuanced endgame approach. The strategy exploits cooperative opponents
# more effectively while still allowing for cooperation when beneficial. The
# conditions are clearly ordered and specify when to cooperate or defect in each
# situation.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.sliding_window = 20
          self.endgame_rounds = 50
          self.exploit_threshold = 0.7
          self.defensive_threshold = 0.3
          self.mutual_cooperation_payoff = 3
  
      if len(self.history) < 5:
          return axl.Action.D
  
      window = min(self.sliding_window, len(self.history))
      opponent_c_rate = opponent.history[-window:].count(axl.Action.C) / window
  
      if len(self.history) % 50 == 0:
          if self.score > self.mutual_cooperation_payoff * len(self.history):
              return axl.Action.D
          else:
              return axl.Action.C
  
      if self._random.random() < 0.05:
          return axl.Action.C if self.history[-1] == axl.Action.D else axl.Action.D
  
      if len(self.history) > 1000 - self.endgame_rounds:
          if opponent_c_rate > self.exploit_threshold:
              return axl.Action.D
          else:
              return axl.Action.C if len(self.history) % 2 == 1 else axl.Action.D
  
      if opponent_c_rate < self.defensive_threshold:
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
  
      if self.defensive_threshold <= opponent_c_rate <= self.exploit_threshold:
          return opponent.history[-1]
  
      if opponent_c_rate > self.exploit_threshold:
          return axl.Action.D if self._random.random() < 0.7 else axl.Action.C
  
      return opponent.history[-1]

# Here's a revised strategy that incorporates the feedback:  1. Start with a
# cautious cooperation approach:    - Play C for the first 3 rounds.    - If the
# opponent plays D in any of these rounds, switch to step 2 immediately.  2.
# After the initial phase, use the following decision-making process for each
# round:     a. Check for end-game condition:       - If in the last 30-70
# rounds (randomly determined at the start of the game):         - Play D with
# 70% probability, C with 30% probability.         - Skip the rest of the steps.
# b. Check for random play:       - If the opponent's last 10 moves have close
# to 50% C and 50% D:         - Play D with 60% probability, C with 40%
# probability.         - Skip the rest of the steps.     c. Pattern recognition:
# - If a clear pattern of 3-5 moves is detected in the opponent's recent play:
# - If the pattern suggests the next move is C, play C.         - If the pattern
# suggests the next move is D, play D.         - Skip the rest of the steps.
# d. Evaluate recent opponent behavior (based on last 20 moves):       - If
# opponent cooperated > 70% of the time:         - Play C with 95% probability,
# D with 5% probability.       - If opponent defected > 70% of the time:
# - Play D with 90% probability, C with 10% probability.       - Otherwise
# (mixed strategy):         - Use the Tit-for-Tat with forgiveness approach:
# - If opponent's last move was C, play C.           - If opponent's last move
# was D:             - Play D with 90% probability, C with 10% probability.  3.
# Payoff-based adjustment:    - Every 10 rounds, calculate the average payoff
# per round.    - If the average payoff is < 1.5:      - Increase the
# probability of playing D in step 2d by 5% (capped at 95%).    - If the average
# payoff is > 2.5:      - Decrease the probability of playing D in step 2d by 5%
# (minimum 5%).  This revised strategy addresses the previous weaknesses by: 1.
# Reducing vulnerability to early exploitation with a shorter initial
# cooperation phase. 2. Implementing a rolling window for opponent behavior
# evaluation. 3. Randomizing the end-game strategy onset. 4. Adding basic
# pattern recognition. 5. Incorporating payoff consideration in decision-making.
# 6. Adding a mechanism to detect and respond to random play. 7. Considering
# longer-term consequences through payoff-based adjustments.  The strategy
# remains relatively simple while being more robust against various opponent
# behaviors. It maintains a cooperative approach when beneficial but can adapt
# to more aggressive or random opponents when necessary.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.end_game_start = self._random.randint(930, 970)
          self.d_probability = 0.9
  
      if len(self.history) < 3:
          if opponent.history and opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          return axl.Action.C
  
      if len(self.history) >= self.end_game_start:
          return self._random.random_choice(0.7)
  
      recent_opponent_moves = opponent.history[-10:]
      coop_rate_10 = recent_opponent_moves.count(axl.Action.C) / 10
      if 0.45 <= coop_rate_10 <= 0.55:
          return self._random.random_choice(0.6)
  
      for pattern_length in range(3, 6):
          pattern = opponent.history[-pattern_length:]
          if opponent.history[-2*pattern_length:-pattern_length] == pattern:
              next_move = pattern[0]
              return next_move
  
      recent_20_moves = opponent.history[-20:]
      coop_rate = recent_20_moves.count(axl.Action.C) / 20
  
      if coop_rate > 0.7:
          return self._random.random_choice(0.05)
      elif coop_rate < 0.3:
          return self._random.random_choice(1 - self.d_probability)
      else:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return self._random.random_choice(self.d_probability)
  
      if len(self.history) % 10 == 0:
          avg_payoff = sum(self.total_scores(self.history[-10:], opponent.history[-10:])[0]) / 10
          if avg_payoff < 1.5:
              self.d_probability = min(0.95, self.d_probability + 0.05)
          elif avg_payoff > 2.5:
              self.d_probability = max(0.05, self.d_probability - 0.05)
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For the next 9 rounds, mirror
# your opponent's previous move.  3. After the initial 10 rounds, maintain a
# running cooperation rate (CR) for your opponent, calculated as: (number of C
# plays) / (total number of rounds played).  4. For each subsequent round,
# determine your play as follows (in order of priority):     a. Endgame
# consideration: If there are 10 or fewer rounds left, play D.     b. Probing:
# Every 20 rounds, play a "probe" move:       - If CR > 0.6, play D       - If
# CR < 0.4, play C       - If 0.4 ≤ CR ≤ 0.6, randomly choose C or D     c.
# Punishment phase: If the opponent has played D in the last 2-4 rounds
# (randomly determined at the start of each punishment phase), play D.     d.
# Standard play: Based on the current CR:       - If CR > 0.7, play C with 90%
# probability, D with 10%       - If CR < 0.3, play D with 90% probability, C
# with 10%       - If 0.3 ≤ CR < 0.5, play D with 60% probability, C with 40%
# - If 0.5 ≤ CR ≤ 0.7, play C with 60% probability, D with 40%  5. After each
# round:    a. Update the opponent's CR.    b. If in a punishment phase,
# decrease the remaining punishment rounds by 1.  This strategy addresses the
# previous critiques by: - Using a continuous measure (CR) instead of discrete
# categories - Adapting more quickly to opponent's behavior - Including probing
# moves to test opponent responses - Making the punishment phase less
# predictable - Considering the entire history of play through the CR -
# Implementing a clear endgame strategy  The strategy remains relatively simple
# and maintains a neutral approach, leaning slightly towards cooperation or
# defection based on the opponent's behavior. It's designed to be adaptive and
# more robust against various opponent strategies while still being
# straightforward to implement.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.cr = 0
          self.punishment_rounds = 0
          self.punishment_duration = 0
          self.probe_counter = 0
  
      # Initial rounds (1-10)
      if len(self.history) < 10:
          return opponent.history[-1] if opponent.history else axl.Action.C
  
      # Update cooperation rate
      self.cr = opponent.cooperations / len(opponent.history)
      self.probe_counter += 1
  
      # Endgame consideration
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Probing
      if self.probe_counter == 20:
          self.probe_counter = 0
          if self.cr > 0.6:
              return axl.Action.D
          elif self.cr < 0.4:
              return axl.Action.C
          else:
              return self._random.random_choice(0.5)
  
      # Punishment phase
      if opponent.history[-4:].count(axl.Action.D) >= 2 and self.punishment_rounds == 0:
          self.punishment_duration = self._random.randint(2, 4)
          self.punishment_rounds = self.punishment_duration
          return axl.Action.D
  
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Standard play
      if self.cr > 0.7:
          return self._random.random_choice(0.9)
      elif self.cr < 0.3:
          return self._random.random_choice(0.1)
      elif 0.3 <= self.cr < 0.5:
          return self._random.random_choice(0.4)
      else:
          return self._random.random_choice(0.6)

# Here's the revised strategy, taking into account the feedback:  1. Start by
# playing D (defect) for the first 5 rounds to establish an aggressive stance.
# 2. After the first 5 rounds, for each subsequent round:     a. If both players
# have defected for 3 consecutive rounds, play C (cooperate) once to break the
# cycle.     b. Otherwise, base the decision on the opponent's previous move:
# - If the opponent played C in the previous round:         * Play C with 75%
# probability and D with 25% probability.       - If the opponent played D in
# the previous round:         * Play D.  3. Adjustment based on recent history:
# - Every 10 rounds, calculate the proportion of C plays by the opponent in
# their last 20 moves.    - If this proportion is less than 30%, decrease the
# probability of playing C after opponent's C to 60% for the next 10 rounds.
# - If this proportion is more than 70%, increase the probability of playing C
# after opponent's C to 90% for the next 10 rounds.  4. Endgame strategy:    -
# Starting from round 900 (90% of the game), gradually increase the probability
# of defection.    - For each round n from 900 to 1000, the probability of
# defection is: (n - 900) / 100.    - This results in a 0% chance of defection
# at round 900, increasing linearly to a 100% chance of defection at round 1000.
# This strategy maintains an aggressive approach while being simpler and more
# adaptable. It starts aggressively, uses a modified Tit-for-Tat with a bias
# towards defection, adjusts based on recent opponent behavior, includes a
# forgiveness mechanism, and implements a gradual shift towards defection in the
# endgame. The conditions for cooperation and defection are clearly stated and
# ordered from most specific to most general.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.consecutive_defections = 0
          self.c_probability = 0.75
          self.adjustment_round = 0
  
      current_round = len(self.history)
  
      # Start with defection for the first 5 rounds
      if current_round < 5:
          return axl.Action.D
  
      # Check for 3 consecutive defections
      if (len(self.history) >= 3 and
          self.history[-3:].count(axl.Action.D) == 3 and
          opponent.history[-3:].count(axl.Action.D) == 3):
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      if self.consecutive_defections == 3:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Adjust strategy every 10 rounds
      if current_round % 10 == 0 and current_round > 20:
          opponent_c_ratio = opponent.history[-20:].count(axl.Action.C) / 20
          if opponent_c_ratio < 0.3:
              self.c_probability = 0.6
          elif opponent_c_ratio > 0.7:
              self.c_probability = 0.9
          else:
              self.c_probability = 0.75
          self.adjustment_round = current_round
      elif current_round - self.adjustment_round == 10:
          self.c_probability = 0.75  # Reset after 10 rounds of adjustment
  
      # Endgame strategy
      if current_round >= 900:
          defect_probability = (current_round - 900) / 100
          if self._random.random() < defect_probability:
              return axl.Action.D
  
      # Base decision on opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C if self._random.random() < self.c_probability else axl.Action.D
      else:
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. For subsequent rounds, use the
# following decision process in order:     a. If it's the last round of the
# game, play Defect (D).     b. If the opponent has played Defect (D) more than
# 70% of the time in the last 100 rounds (or all previous rounds if fewer than
# 100 have been played), enter a defensive mode for the next 50 rounds:       -
# In defensive mode, play Defect (D) 70% of the time and Cooperate (C) 30% of
# the time, randomly distributed.       - After 50 rounds in defensive mode,
# return to the main strategy.     c. If not in defensive mode, use a modified
# "Tit-for-Two-Tats" approach:       - If the opponent played Cooperate (C) in
# the previous round, play Cooperate (C).       - If the opponent played Defect
# (D) in the previous round, calculate the probability of defecting as:
# P(Defect) = min(0.9, number of consecutive opponent defections * 0.3)       -
# Generate a random number between 0 and 1. If this number is less than
# P(Defect), play Defect (D). Otherwise, play Cooperate (C).     d. If none of
# the above conditions are met, play Cooperate (C).  3. Throughout the game,
# maintain a record of the opponent's move patterns (e.g., alternating C and D,
# or cycles of CCD). If a clear pattern emerges and persists for at least 20
# rounds:    - If the pattern ends with the opponent's Defect (D), play Defect
# (D) on the round where the opponent is expected to Defect.    - Otherwise,
# play according to the main strategy.  This revised strategy maintains a
# cooperative approach while being more adaptive and robust against various
# opponent behaviors. It uses a sliding window for analyzing opponent behavior,
# incorporates a probabilistic approach to defection, and includes pattern
# recognition. The strategy remains relatively simple while addressing the main
# weaknesses identified in the critique.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.defensive_mode = 0
          self.consecutive_defections = 0
          self.pattern_count = {}
  
      if len(self.history) == 999:  # Last round
          return axl.Action.D
  
      if len(self.history) >= 100:
          defect_rate = opponent.history[-100:].count(axl.Action.D) / 100
      else:
          defect_rate = opponent.history.defections / len(opponent.history) if opponent.history else 0
  
      if defect_rate > 0.7:
          self.defensive_mode = 50
  
      if self.defensive_mode > 0:
          self.defensive_mode -= 1
          return axl.Action.D if self._random.random() < 0.7 else axl.Action.C
  
      # Pattern recognition
      if len(opponent.history) > 20:
          for pattern_length in range(2, 11):  # Check patterns up to length 10
              pattern = tuple(opponent.history[-pattern_length:])
              if opponent.history[-20:] == pattern * (20 // pattern_length):
                  self.pattern_count[pattern] = self.pattern_count.get(pattern, 0) + 1
                  if self.pattern_count[pattern] >= 20:
                      if pattern[-1] == axl.Action.D:
                          return axl.Action.D
              else:
                  self.pattern_count[pattern] = 0
  
      # Modified Tit-for-Two-Tats
      if len(opponent.history) > 0:
          if opponent.history[-1] == axl.Action.C:
              self.consecutive_defections = 0
              return axl.Action.C
          else:
              self.consecutive_defections += 1
              p_defect = min(0.9, self.consecutive_defections * 0.3)
              if self._random.random() < p_defect:
                  return axl.Action.D
  
      return axl.Action.C

# Here's a revised strategy that incorporates the feedback while maintaining
# simplicity and a neutral approach:  1. Start with a cautious approach:    -
# Play C for the first 3 rounds.    - For rounds 4-10, play tit-for-tat (copy
# opponent's last move).  2. From round 11 onwards, maintain a sliding window of
# the last 100 moves (or all moves if fewer than 100 have been played).
# Calculate the opponent's cooperation rate within this window.  3. Base your
# decision on the opponent's recent cooperation rate:    - If their cooperation
# rate is above 60%, play C.    - If their cooperation rate is below 40%, play
# D.    - If their cooperation rate is between 40% and 60%:      a) Generally
# play C.      b) However, every 30 rounds, play D as a "probe" move.  4.
# Implement a forgiveness mechanism:    - If currently playing D due to low
# opponent cooperation, reassess every 20 rounds.    - If the opponent's
# cooperation rate in the last 20 rounds is above 50%, switch back to C.  5. Add
# unpredictability:    - With a 5% chance, play the opposite of what the
# strategy suggests.  6. Pattern recognition (simple version):    - If the
# opponent has played D for the last 5 consecutive moves, play D regardless of
# their overall cooperation rate.    - If the opponent has played C for the last
# 5 consecutive moves, play C regardless of their overall cooperation rate.  7.
# Learning mechanism:    - Track the success rate of C and D moves separately.
# - Every 100 rounds, if the success rate of C is significantly higher than D
# (>10% difference), lower the cooperation threshold by 5% (minimum 35%).    -
# If the success rate of D is significantly higher than C (>10% difference),
# raise the cooperation threshold by 5% (maximum 65%).  8. Continue this
# strategy until the end of the game, without special end-game behavior.
# Decision Priority Order: 1. Pattern recognition (5 consecutive same moves) 2.
# Unpredictability (5% random choice) 3. Forgiveness mechanism (if applicable)
# 4. Probe move (if applicable) 5. Main cooperation rate-based decision  This
# revised strategy addresses the initial vulnerability, adapts more quickly to
# changes, includes probing and pattern recognition, removes rigid end-game
# behavior, and adds elements of learning and unpredictability. It maintains a
# neutral approach by basing decisions primarily on the opponent's recent
# behavior while including mechanisms to encourage cooperation and protect
# against exploitation.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.cooperation_threshold = 0.6
          self.defection_threshold = 0.4
          self.probe_counter = 0
          self.forgiveness_counter = 0
          self.c_success = 0
          self.d_success = 0
          self.c_count = 0
          self.d_count = 0
  
      if len(self.history) < 3:
          return axl.Action.C
  
      if len(self.history) < 10:
          return opponent.history[-1]
  
      window = min(100, len(self.history))
      opp_coop_rate = opponent.history[-window:].count(axl.Action.C) / window
  
      # 1. Pattern recognition
      last_5_moves = opponent.history[-5:]
      if all(move == axl.Action.D for move in last_5_moves):
          return axl.Action.D
      if all(move == axl.Action.C for move in last_5_moves):
          return axl.Action.C
  
      # 2. Unpredictability
      if self._random.random() < 0.05:
          return axl.Action.D if self.history[-1] == axl.Action.C else axl.Action.C
  
      # 3. Forgiveness mechanism
      if self.history[-1] == axl.Action.D:
          self.forgiveness_counter += 1
          if self.forgiveness_counter >= 20:
              self.forgiveness_counter = 0
              if opponent.history[-20:].count(axl.Action.C) / 20 > 0.5:
                  return axl.Action.C
      else:
          self.forgiveness_counter = 0
  
      # 4. Probe move
      self.probe_counter += 1
      if self.probe_counter >= 30:
          self.probe_counter = 0
          return axl.Action.D
  
      # 5. Main cooperation rate-based decision
      if opp_coop_rate > self.cooperation_threshold:
          decision = axl.Action.C
      elif opp_coop_rate < self.defection_threshold:
          decision = axl.Action.D
      else:
          decision = axl.Action.C
  
      # Learning mechanism
      last_move = self.history[-1]
      opp_last_move = opponent.history[-1]
      if last_move == axl.Action.C:
          self.c_count += 1
          self.c_success += 3 if opp_last_move == axl.Action.C else 0
      else:
          self.d_count += 1
          self.d_success += 5 if opp_last_move == axl.Action.C else 1
  
      if len(self.history) % 100 == 0 and self.c_count > 0 and self.d_count > 0:
          c_success_rate = self.c_success / self.c_count
          d_success_rate = self.d_success / self.d_count
          if c_success_rate > d_success_rate + 0.1:
              self.cooperation_threshold = max(0.35, self.cooperation_threshold - 0.05)
              self.defection_threshold = max(0.15, self.defection_threshold - 0.05)
          elif d_success_rate > c_success_rate + 0.1:
              self.cooperation_threshold = min(0.85, self.cooperation_threshold + 0.05)
              self.defection_threshold = min(0.65, self.defection_threshold + 0.05)
  
      return decision

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing D (defect) for the first 10 rounds to establish an aggressive stance.
# 2. After the first 10 rounds, implement the following decision-making process
# in order:     a. If the opponent has played C for the last 3 consecutive
# rounds, play D to exploit their cooperation.        b. If there have been
# mutual defections (DD) for the last 5 rounds, play C once to test if
# cooperation can be re-established.        c. If the opponent has alternated C
# and D for the last 6 moves, play D on their expected C and C on their expected
# D.        d. If none of the above conditions are met, use a modified tit-for-
# tat strategy:       - If the opponent played C in the previous round, play C.
# - If the opponent played D in the previous round, play D.  3. Every 30 rounds,
# calculate your average score for these rounds:    - If your average score is
# below 2, play D for the next 3 rounds regardless of the opponent's moves.    -
# If your average score is above 3, play one round of C regardless of the
# opponent's last move.  4. In the last 100 rounds, adjust the strategy based on
# the score difference:    - If you're ahead by more than 50 points, always play
# D to secure your lead.    - If you're behind by more than 50 points, alternate
# between C and D to try to catch up.    - If the score difference is within 50
# points, continue with the main strategy (steps 2-3).  5. In the final 10
# rounds, always play D regardless of other conditions.  This revised strategy
# maintains an aggressive approach while being simpler and more responsive to
# the opponent's behavior. It includes clear conditions for cooperation and
# defection, ordered from most specific to most general. The strategy now has
# mechanisms to exploit patterns, test for cooperation after prolonged mutual
# defection, and adapt based on the game's progress and score difference. The
# end-game strategy is more dynamic, basing decisions on the current standing
# rather than predetermined moves.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.last_30_rounds_start = 0
          self.play_d_count = 0
          self.play_c_once = False
  
      if len(self.history) < 10:
          return axl.Action.D
  
      if len(self.history) >= 990:
          return axl.Action.D
  
      if len(self.history) >= 900:
          score_diff = self.score - opponent.score
          if score_diff > 50:
              return axl.Action.D
          elif score_diff < -50:
              return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D
  
      if self.play_d_count > 0:
          self.play_d_count -= 1
          return axl.Action.D
  
      if self.play_c_once:
          self.play_c_once = False
          return axl.Action.C
  
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.D
  
      if self.history[-5:] == [axl.Action.D] * 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.C
  
      if len(self.history) >= 6:
          last_6_opponent = opponent.history[-6:]
          if last_6_opponent == [axl.Action.C, axl.Action.D] * 3:
              return axl.Action.D
          elif last_6_opponent == [axl.Action.D, axl.Action.C] * 3:
              return axl.Action.C
  
      if (len(self.history) - self.last_30_rounds_start) == 30:
          my_score, _ = self.total_scores(self.history[-30:], opponent.history[-30:])
          avg_score = my_score / 30
          self.last_30_rounds_start = len(self.history)
          if avg_score < 2:
              self.play_d_count = 3
              return axl.Action.D
          elif avg_score > 3:
              self.play_c_once = True
              return axl.Action.C
  
      return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing cooperatively (C) for the first 3 rounds to signal willingness to
# cooperate.  2. For the remainder of the game, use the following decision
# process in order:     a. If it's one of the last 50 rounds, increase the
# probability of defection:       - Calculate P(defect) = (current round - 950)
# / 100       - Play D with probability P(defect), otherwise play C     b. If
# the opponent has defected in the last two consecutive rounds:       - Play D
# c. If it's a multiple of 50 rounds (50, 100, 150, etc.):       - Play C (to
# attempt to re-establish cooperation)     d. If the opponent's defection rate
# in the last 20 rounds exceeds 70%:       - Play D for the next 5 rounds, then
# return to the main strategy     e. If it's a "probe" round (with 5%
# probability):       - Play D to test opponent's response     f. In all other
# cases:       - Play C  3. Throughout the game, maintain a rolling window of
# the last 20 moves to calculate the opponent's recent cooperation rate.  This
# strategy is primarily cooperative but includes mechanisms to protect against
# exploitation and adapt to different opponent behaviors. It starts
# cooperatively, generally plays a "Tit-for-Two-Tats" approach, but includes
# periodic cooperation attempts, defensive measures against aggressive
# opponents, occasional probing defections, and a gradual shift towards more
# defection in the endgame.  The strategy is simpler than the previous version,
# removing the complex score tracking element. It's more robust against various
# opponent types, including aggressive, cooperative, neutral, and random
# players. The ordered decision process ensures clear conditions for cooperation
# or defection, making the strategy easier to implement and understand.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defection_streak_remaining = 0
          self.last_defection_streak_start = 0
  
      current_round = len(self.history) + 1
  
      # First 3 rounds: cooperate
      if current_round <= 3:
          return axl.Action.C
  
      # Last 50 rounds: increase probability of defection
      if current_round > 950:
          p_defect = (current_round - 950) / 100
          if self._random.random() < p_defect:
              return axl.Action.D
  
      # Opponent defected in last two consecutive rounds
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Every 50 rounds: cooperate
      if current_round % 50 == 0:
          return axl.Action.C
  
      # Check opponent's defection rate in last 20 rounds
      recent_defections = opponent.history[-20:].count(axl.Action.D)
      if recent_defections > 14 and self.defection_streak_remaining == 0:  # More than 70% defections
          self.defection_streak_remaining = 5
          self.last_defection_streak_start = current_round
  
      # Play defection streak
      if self.defection_streak_remaining > 0:
          self.defection_streak_remaining -= 1
          return axl.Action.D
  
      # Probe round (5% probability)
      if self._random.random() < 0.05:
          return axl.Action.D
  
      # Default: cooperate
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start with
# a neutral opening: Alternate between C and D for the first 10 moves.  2. For
# the remainder of the game, use the following decision-making process in order:
# a. If it's one of the last 10 rounds of the game, play D.     b. Assess the
# opponent's behavior over the last 20 moves:       - If they've played C 14 or
# more times (70%+), consider them cooperative.       - If they've played D 14
# or more times (70%+), consider them aggressive.       - Otherwise, consider
# them neutral.     c. Based on the assessment, set a base cooperation
# probability:       - If cooperative: 70% C       - If aggressive: 30% C
# - If neutral: 50% C     d. Adjust the cooperation probability based on recent
# opponent behavior:       - For each of the opponent's consecutive D moves (up
# to 3), reduce the cooperation probability by 10%.       - For each of the
# opponent's consecutive C moves (up to 3), increase the cooperation probability
# by 10%.     e. Add a small random variation to the final cooperation
# probability (±5%).     f. Generate a random number between 0 and 1. If it's
# less than or equal to the final cooperation probability, play C; otherwise,
# play D.  3. Repeat steps 2b-2f for each move, continuously adapting to the
# opponent's behavior.  This strategy: - Starts neutrally - Continuously
# assesses the opponent's recent behavior - Adapts to changes in the opponent's
# strategy - Responds proportionally to consecutive cooperation or defection -
# Maintains an element of unpredictability - Protects against end-game
# exploitation  The strategy is simple in concept but adaptive in practice. It
# maintains a neutral approach by starting with alternating moves and using a
# 50% cooperation rate for neutral opponents. The conditions for cooperation or
# defection are clear and ordered, with end-game behavior taking precedence,
# followed by an assessment of recent opponent behavior, and finally a
# probabilistic decision based on that assessment.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.opening_moves = [axl.Action.C, axl.Action.D] * 5
  
      if len(self.history) < 10:
          return self.opening_moves[len(self.history)]
  
      if len(self.history) >= 990:
          return axl.Action.D
  
      recent_opponent_moves = opponent.history[-20:]
      opponent_c_count = recent_opponent_moves.count(axl.Action.C)
  
      if opponent_c_count >= 14:
          base_coop_prob = 0.7
      elif opponent_c_count <= 6:
          base_coop_prob = 0.3
      else:
          base_coop_prob = 0.5
  
      consecutive_d = 0
      consecutive_c = 0
      for move in reversed(opponent.history[-3:]):
          if move == axl.Action.D:
              consecutive_d += 1
              if consecutive_c > 0:
                  break
          elif move == axl.Action.C:
              consecutive_c += 1
              if consecutive_d > 0:
                  break
          else:
              break
  
      coop_prob = base_coop_prob - (consecutive_d * 0.1) + (consecutive_c * 0.1)
      coop_prob += self._random.uniform(-0.05, 0.05)
      coop_prob = max(0, min(1, coop_prob))
  
      return axl.Action.C if self._random.random() <= coop_prob else axl.Action.D

# Here's a revised strategy that takes into account the feedback:  1. Start with
# a mixed approach for the first 10 rounds:    - Play D with 70% probability and
# C with 30% probability.    This maintains an aggressive stance while testing
# the waters.  2. From round 11 onwards, implement the following core strategy:
# a. Always defect (D) if any of these conditions are met (in order of
# priority):       - It's one of the last 100 rounds of the game.       - The
# opponent has defected in the last 2 rounds.       - You're behind in total
# score and the difference is more than 50 points.       - A random number
# (1-100) is less than or equal to your current defection rate (starts at 70).
# b. Otherwise, cooperate (C).  3. Adjust your defection rate every 25 rounds
# based on the opponent's behavior in those rounds:    - If opponent cooperated
# > 60%: Increase defection rate by 5 percentage points (max 85%).    - If
# opponent cooperated < 40%: Decrease defection rate by 5 percentage points (min
# 55%).    - Otherwise: Move defection rate 2 percentage points towards 70%.  4.
# Implement a "surprise detection" mechanism:    - If the opponent's cooperation
# rate in the last 10 rounds differs by more than 30 percentage points from
# their cooperation rate in the previous 40 rounds, immediately set your
# defection rate to 80% for the next 10 rounds.  5. "Forgiveness" mechanism:
# - If there have been 10 consecutive rounds of mutual defection, cooperate for
# 1 round, then return to the core strategy.  6. Long-term adaptation:    -
# Every 100 rounds, calculate the opponent's overall cooperation rate.    - If
# it's above 55%, increase your base defection rate by 2 percentage points (max
# 80%).    - If it's below 45%, decrease your base defection rate by 2
# percentage points (min 60%).  7. Randomness injection:    - Every 50 rounds,
# for a single round, ignore all other rules and choose C or D with 50/50
# probability.  This revised strategy maintains an aggressive approach while
# addressing the previously identified weaknesses. It's more adaptable to
# various opponent behaviors, includes both short-term and long-term memory, and
# has mechanisms to break out of negative cycles. The clear prioritization of
# conditions for defection allows for decisive action while still incorporating
# an element of unpredictability.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defection_rate = 70
          self.base_defection_rate = 70
          self.last_adjustment = 0
          self.consecutive_mutual_defections = 0
          self.surprise_mode_rounds = 0
  
      current_round = len(self.history)
      total_rounds = self.match_attributes["length"]
  
      # First 10 rounds
      if current_round < 10:
          return axl.Action.D if self._random.random() < 0.7 else axl.Action.C
  
      # Adjust defection rate every 25 rounds
      if current_round % 25 == 0 and current_round > self.last_adjustment:
          opponent_coop_rate = opponent.history[-25:].count(axl.Action.C) / 25
          if opponent_coop_rate > 0.6:
              self.defection_rate = min(85, self.defection_rate + 5)
          elif opponent_coop_rate < 0.4:
              self.defection_rate = max(55, self.defection_rate - 5)
          else:
              self.defection_rate += 2 if self.defection_rate < 70 else -2
          self.last_adjustment = current_round
  
      # Surprise detection
      if current_round >= 50:
          recent_coop_rate = opponent.history[-10:].count(axl.Action.C) / 10
          previous_coop_rate = opponent.history[-50:-10].count(axl.Action.C) / 40
          if abs(recent_coop_rate - previous_coop_rate) > 0.3:
              self.surprise_mode_rounds = 10
  
      if self.surprise_mode_rounds > 0:
          self.surprise_mode_rounds -= 1
          self.defection_rate = 80
  
      # Long-term adaptation
      if current_round % 100 == 0:
          overall_coop_rate = opponent.cooperations / current_round
          if overall_coop_rate > 0.55:
              self.base_defection_rate = min(80, self.base_defection_rate + 2)
          elif overall_coop_rate < 0.45:
              self.base_defection_rate = max(60, self.base_defection_rate - 2)
          self.defection_rate = max(self.defection_rate, self.base_defection_rate)
  
      # Randomness injection
      if current_round % 50 == 0:
          return axl.Action.C if self._random.random() < 0.5 else axl.Action.D
  
      # Forgiveness mechanism
      if self.consecutive_mutual_defections >= 10:
          self.consecutive_mutual_defections = 0
          return axl.Action.C
  
      # Core strategy
      if (
          (total_rounds is not None and current_round > total_rounds - 100) or
          opponent.history[-2:].count(axl.Action.D) == 2 or
          self.score < opponent.score - 50 or
          self._random.random() * 100 <= self.defection_rate
      ):
          if len(self.history) > 1 and (self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D):
              self.consecutive_mutual_defections += 1
          else:
              self.consecutive_mutual_defections = 0
          return axl.Action.D
      else:
          self.consecutive_mutual_defections = 0
          return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing cooperatively (C) for the first 5 rounds to signal willingness to
# cooperate.  2. For each subsequent round, evaluate the following conditions in
# order:     a. If it's one of the last 50 rounds, calculate the probability of
# defection as (current round - 950) / 50. Play D with this probability,
# otherwise play C.     b. If the opponent has defected in both of the last two
# rounds, play D.     c. If the opponent's defection rate over the last 30
# rounds exceeds 60%, play D.     d. If your total score is more than 30 points
# behind the opponent's, play D.     e. If the current round number is divisible
# by 40, play C to encourage cooperation.     f. If none of the above conditions
# are met, play C.  3. Learning mechanism: After every 100 rounds, update the
# defection threshold:    - If your score is higher than the opponent's,
# increase the threshold by 5% (up to a maximum of 70%).    - If your score is
# lower, decrease the threshold by 5% (down to a minimum of 50%).  4. Pattern
# recognition: Keep track of the opponent's last 10 moves. If a repeating
# pattern is detected (e.g., CDCD or CCD), respond with the move that would have
# maximized your score against that pattern.  This strategy maintains a
# cooperative approach while being more adaptive to various opponent behaviors:
# - It starts cooperatively and generally favors cooperation. - It responds to
# immediate defection (condition b) and sustained aggressive behavior (condition
# c). - It has a mechanism to catch up if falling behind (condition d). - It
# periodically encourages cooperation (condition e). - The end-game strategy is
# more nuanced, gradually increasing the probability of defection. - The
# learning mechanism allows for long-term adaptation to the opponent's overall
# strategy. - The pattern recognition system helps counter predictable opponent
# strategies.  The strategy is still relatively simple, with clear conditions
# for cooperation and defection, ordered from most specific to most general. It
# should be more robust against a variety of opponent behaviors while
# maintaining its cooperative nature.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defection_threshold = 0.6
          self.pattern = []
  
      if len(self.history) < 5:
          return axl.Action.C
  
      if len(self.history) > 950:
          defect_prob = (len(self.history) - 950) / 50
          if self._random.random() < defect_prob:
              return axl.Action.D
  
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      recent_defection_rate = opponent.history[-30:].count(axl.Action.D) / 30
      if recent_defection_rate > self.defection_threshold:
          return axl.Action.D
  
      if self.score < opponent.score - 30:
          return axl.Action.D
  
      if len(self.history) % 40 == 0:
          return axl.Action.C
  
      self.pattern.append(opponent.history[-1])
      if len(self.pattern) > 10:
          self.pattern.pop(0)
      
      pattern_length = min(5, len(self.pattern))
      for i in range(2, pattern_length + 1):
          if self.pattern[-i:] * 2 == self.pattern[-2*i:]:
              best_response = axl.Action.D if axl.Action.D in self.pattern[-i:] else axl.Action.C
              return best_response
  
      if len(self.history) % 100 == 0:
          if self.score > opponent.score:
              self.defection_threshold = min(0.7, self.defection_threshold * 1.05)
          else:
              self.defection_threshold = max(0.5, self.defection_threshold * 0.95)
  
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. For each subsequent round, determine
# your move in the following order:     a. If it's the last 20 rounds of the
# game:       - Calculate a defection probability: (current round - 980) * 5%
# - Randomly choose to defect (D) based on this probability       - If not
# defecting based on this probability, continue to the next conditions     b. If
# the opponent has defected in the last 3 consecutive rounds:       - Defect (D)
# c. If it's a multiple of 20 rounds (i.e., round 20, 40, 60, etc.):       -
# Calculate the opponent's cooperation rate over the last 20 rounds       - If
# the cooperation rate is above 70%, cooperate (C)       - If the cooperation
# rate is below 30%, defect (D)       - If the rate is between 30% and 70%,
# continue to the next condition     d. If the opponent defected in the previous
# round:       - Defect (D) with 90% probability       - Cooperate (C) with 10%
# probability (forgiveness factor)     e. If none of the above conditions are
# met:       - Cooperate (C)  This strategy: - Starts cooperatively - Uses a
# modified Tit-for-Tat approach with a forgiveness factor - Adapts to consistent
# opponent behavior every 20 rounds - Protects against long streaks of
# exploitation - Gradually increases defection probability in the endgame -
# Defaults to cooperation when no other conditions are met  The strategy remains
# relatively simple while addressing the main points of feedback. It maintains a
# generally neutral approach but can adapt to both cooperative and aggressive
# opponents. The conditions are ordered to prioritize endgame considerations,
# protection against exploitation, periodic behavior assessment, and then the
# core Tit-for-Tat mechanism.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
  
      current_round = len(self.history) + 1
      
      # Endgame strategy
      if current_round > 980:
          defection_probability = (current_round - 980) * 0.05
          if self._random.random() < defection_probability:
              return axl.Action.D
      
      # Check for opponent's consecutive defections
      if len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          return axl.Action.D
      
      # Periodic assessment of opponent's behavior
      if len(self.history) >= 20:
          cooperation_rate = opponent.history[-20:].count(axl.Action.C) / 20
          if cooperation_rate > 0.7:
              return axl.Action.C
          elif cooperation_rate < 0.3:
              return axl.Action.D
      
      # Modified Tit-for-Tat with forgiveness
      if opponent.history and opponent.history[-1] == axl.Action.D:
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
      
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback, with clear
# conditions for cooperation and defection:  1. Start the game by playing D
# (defect) for the first 10 rounds.  2. For rounds 11-950, follow these rules in
# order:     a. If the opponent has played C for 3 or more consecutive rounds,
# play D.        b. If mutual defection (D,D) has occurred in more than 80% of
# the last 50 rounds, play C for the next 2 rounds to attempt breaking the
# cycle.        c. If the opponent played C in the last round:       - Play D
# with 90% probability       - Play C with 10% probability        d. If the
# opponent played D in the last round:       - Play D with 80% probability
# - Play C with 20% probability  3. For the final 50 rounds (951-1000), always
# play D.  This strategy: - Starts aggressively - Exploits consistent
# cooperation - Attempts to break out of unproductive mutual defection cycles -
# Maintains an overall aggressive stance while allowing for some cooperation -
# Introduces controlled randomness to be less predictable - Finishes with pure
# defection to maximize end-game payoff  The strategy is simpler than the
# original, maintains its aggressive nature, and is more robust against various
# opponent behaviors. The conditions for cooperation and defection are clearly
# stated and ordered by priority.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.consecutive_c_count = 0
          self.mutual_defection_c_counter = 0
  
      if len(self.history) < 10:
          return axl.Action.D
  
      if len(self.history) >= 950:
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_c_count += 1
      else:
          self.consecutive_c_count = 0
  
      if self.consecutive_c_count >= 3:
          return axl.Action.D
  
      if len(self.history) >= 50:
          last_50_mutual_defections = sum(
              1 for a, b in zip(self.history[-50:], opponent.history[-50:])
              if a == axl.Action.D and b == axl.Action.D
          )
          if last_50_mutual_defections > 40:
              if self.mutual_defection_c_counter < 2:
                  self.mutual_defection_c_counter += 1
                  return axl.Action.C
              else:
                  self.mutual_defection_c_counter = 0
  
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
      else:
          return axl.Action.D if self._random.random() < 0.8 else axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing cooperatively (C) for the first 5 rounds to signal willingness to
# cooperate.  2. For the remainder of the game, make decisions based on the
# following conditions, checked in this order:     a. If it's one of the last 20
# rounds, play D.        b. If the opponent's overall cooperation rate is below
# 40%, play D.        c. If it's a "forced cooperation" round, play C. These
# occur randomly every 40-60 rounds.        d. If the opponent has defected in 3
# out of the last 5 rounds, play D.        e. If the opponent has played D twice
# in a row, play D.        f. Otherwise, play C.  3. Throughout the game, keep
# track of the following:    - Opponent's overall cooperation rate    -
# Opponent's moves in the last 5 rounds    - Number of rounds since last "forced
# cooperation"  This revised strategy maintains a cooperative approach while
# addressing the main points of feedback:  1. It's still relatively simple and
# easy to understand. 2. It's more robust against aggressive opponents by
# lowering the threshold for switching to defection (40% instead of 30%). 3. The
# periodic forced cooperation is now randomized to avoid exploitation. 4. The
# end-game strategy is less predictable, starting anytime in the last 20 rounds
# instead of exactly the last 10. 5. It's more adaptive to the opponent's recent
# behavior by considering the last 5 rounds, not just the last 2. 6. It's less
# vulnerable to alternating strategies by considering the overall defection rate
# in the last 5 rounds.  While this strategy doesn't explicitly use the payoff
# values, it's designed with the given payoff structure in mind, balancing the
# risk of being exploited with the potential rewards of cooperation. The
# strategy remains fundamentally cooperative but with stronger protections
# against persistent defectors and potential exploiters.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.forced_coop_counter = 0
          self.forced_coop_interval = self._random.randint(40, 60)
          self.opp_cooperations = 0
  
      # First 5 rounds: cooperate
      if len(self.history) < 5:
          return axl.Action.C
  
      # Update opponent's cooperation count
      if len(opponent.history) > len(self.history) - 1:
          if opponent.history[-1] == axl.Action.C:
              self.opp_cooperations += 1
  
      # Last 20 rounds: defect
      if len(self.history) > 980:
          return axl.Action.D
  
      # Check opponent's cooperation rate
      opp_coop_rate = self.opp_cooperations / len(opponent.history)
      if opp_coop_rate < 0.4:
          return axl.Action.D
  
      # Forced cooperation
      self.forced_coop_counter += 1
      if self.forced_coop_counter >= self.forced_coop_interval:
          self.forced_coop_counter = 0
          self.forced_coop_interval = self._random.randint(40, 60)
          return axl.Action.C
  
      # Check recent opponent behavior
      if opponent.history[-5:].count(axl.Action.D) >= 3:
          return axl.Action.D
  
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Default to cooperation
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For each subsequent round,
# evaluate the following conditions in order:     a. If this is one of the last
# 20 rounds of the game:       - Calculate a defection probability: (current
# round number - 980) / 20       - Play D with this probability, otherwise play
# C     b. If the opponent has defected in both of the last two rounds:       -
# Play D     c. If the opponent's defection rate over the last 20 moves is
# greater than 60%:       - Play D with 80% probability, otherwise play C     d.
# If the current round number is between 40-60 rounds since the last
# "cooperation test":       - Play C (as a cooperation test)       - Reset the
# cooperation test counter     e. If a random number between 0 and 1 is less
# than 0.05 (5% chance):       - Play C for this round and the next round (to
# signal strong cooperation intention)       - Skip the next round's decision
# f. If the opponent's moves appear random (between 40% and 60% cooperation rate
# over the last 50 moves):       - Play D with 55% probability, otherwise play C
# g. If none of the above conditions are met:       - Play C  3. Keep track of
# the following:    - Opponent's moves in the last two rounds    - Opponent's
# defection rate over the last 20 moves    - Rounds since last cooperation test
# - Opponent's overall cooperation rate  This strategy maintains a neutral
# approach while addressing the weaknesses identified in the critique. It's more
# adaptive to different opponent behaviors, introduces some randomness to avoid
# exploitation, and gradually transitions to a more defensive stance in the
# endgame. The conditions are ordered to prioritize protection against
# exploitation while still maintaining opportunities for cooperation.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.cooperation_test_counter = 0
          self.skip_next_round = False
          self.last_test_round = 0
          return axl.Action.C
  
      if self.skip_next_round:
          self.skip_next_round = False
          return axl.Action.C
  
      current_round = len(self.history) + 1
      
      # Condition a: Last 20 rounds
      if current_round > 980:
          defection_probability = (current_round - 980) / 20
          if self._random.random() < defection_probability:
              return axl.Action.D
      
      # Condition b: Opponent defected in both of the last two rounds
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
      
      # Calculate opponent's recent defection rate
      if len(opponent.history) >= 20:
          recent_defection_rate = opponent.history[-20:].count(axl.Action.D) / 20
          
          # Condition c: Opponent's defection rate over last 20 moves > 60%
          if recent_defection_rate > 0.6:
              if self._random.random() < 0.8:
                  return axl.Action.D
      
      # Condition d: Cooperation test
      if current_round - self.last_test_round >= 40 and current_round - self.last_test_round <= 60:
          self.last_test_round = current_round
          return axl.Action.C
      
      # Condition e: Random cooperation signal
      if self._random.random() < 0.05:
          self.skip_next_round = True
          return axl.Action.C
      
      # Condition f: Opponent appears random
      if len(opponent.history) >= 50:
          cooperation_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if 0.4 <= cooperation_rate <= 0.6:
              if self._random.random() < 0.55:
                  return axl.Action.D
      
      # Condition g: Default to cooperation
      return axl.Action.C

# Here's the revised strategy, taking into account the feedback:  1. Start by
# playing D (defect) for the first 10 rounds.  2. For rounds 11-800, follow
# these rules in order:    a. If the opponent has played C in the last two
# rounds, play D.    b. If the opponent has played D in the last three rounds,
# play C.    c. If your average score over the last 100 rounds is below 1.5,
# play C with 25% probability for the next 20 rounds.    d. Otherwise, play D
# with 85% probability and C with 15% probability.  3. For rounds 801-1000
# (endgame), follow these rules in order:    a. If the opponent played C in the
# previous round, play D.    b. Otherwise, play D with 90% probability and C
# with 10% probability.  This strategy: - Starts aggressively - Maintains a high
# level of aggression throughout the game - Exploits consistent cooperation from
# the opponent - Occasionally attempts to break cycles of mutual defection -
# Adapts if performing poorly - Increases aggression in the endgame - Is simpler
# and more straightforward than the original proposal - Clearly defines
# conditions for cooperation and defection - Orders the conditions to prioritize
# responses to opponent behavior

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.endgame_started = False
          self.adaptation_counter = 0
  
      round_number = len(self.history) + 1
  
      if round_number <= 10:
          return axl.Action.D
  
      if round_number > 800 and not self.endgame_started:
          self.endgame_started = True
          self.adaptation_counter = 0
  
      if self.endgame_started:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
  
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          return axl.Action.D
  
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.C
  
      if self.adaptation_counter > 0:
          self.adaptation_counter -= 1
          return axl.Action.C if self._random.random() < 0.25 else axl.Action.D
  
      if self.adaptation_counter == 0 and len(self.history) >= 100:
          last_100_scores = self.total_scores(self.history[-100:], opponent.history[-100:])
          average_score = last_100_scores[0] / 100
          if average_score < 1.5:
              self.adaptation_counter = 20
              return axl.Action.C if self._random.random() < 0.25 else axl.Action.D
  
      return axl.Action.D if self._random.random() < 0.85 else axl.Action.C

# Here's a revised strategy incorporating the feedback:  1. Start by playing
# Cooperate (C) for the first 5 rounds.  2. For the remainder of the game, use
# the following decision process in order:     a. If it's one of the last 100
# rounds, increase the probability of Defect (D) by 0.5% for each round closer
# to the end, capped at 25%. This means in the very last round, there's a 25%
# chance of playing D regardless of other factors.     b. With a 3% probability,
# play a random move (C or D with equal likelihood) to probe the opponent's
# strategy.     c. If the opponent has played D more than 60% of the time in the
# last 30 rounds, switch to Tit-for-Tat for the next 30 rounds:       - Mirror
# the opponent's previous move exactly.     d. If you detect a consistent
# alternating C-D pattern from the opponent over the last 6 moves, play D.
# e. If it has been between 40 to 60 rounds since the last "olive branch"
# (determined randomly within this range), play C regardless of other factors.
# f. Apply a modified Tit-for-Two-Tats rule:       - Play C unless the opponent
# has played D in both of their last two moves.       - If the opponent played D
# in their last two moves, play D.     g. If none of the above conditions are
# met, play C.  3. Throughout the game, maintain a weighted history of the
# opponent's moves, with more recent moves given higher weight. Use this to
# adjust the threshold in step 2c, lowering it if the opponent has been
# consistently aggressive over the long term.  This strategy aims to: - Start
# cooperatively and maintain cooperation when possible. - Protect against
# exploitation by adapting to aggressive opponents. - Break deadlocks with
# periodic olive branches. - Probe the opponent's strategy occasionally. -
# Recognize and counter simple patterns like alternating C-D. - Gradually become
# more cautious towards the end of the game. - Maintain long-term memory of the
# opponent's behavior to inform decisions.  The order of conditions ensures that
# end-game adjustments and probing moves take precedence, followed by
# adaptations to opponent behavior, pattern recognition, periodic cooperation
# attempts, and finally the core Tit-for-Two-Tats strategy.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.weighted_history = []
          self.last_olive_branch = 0
          self.tit_for_tat_mode = 0
          self.next_olive_branch = self._random.randint(40, 60)
      
      round_number = len(self.history)
      
      # Update weighted history
      self.weighted_history.append((opponent.history[-1] if opponent.history else None, round_number))
      if len(self.weighted_history) > 100:
          self.weighted_history.pop(0)
      
      # First 5 rounds: Cooperate
      if round_number < 5:
          return axl.Action.C
      
      # Last 100 rounds: Increase probability of Defect
      if round_number > 900:
          defect_prob = min(0.25, (round_number - 900) * 0.005)
          if self._random.random() < defect_prob:
              return axl.Action.D
      
      # 3% chance of random move
      if self._random.random() < 0.03:
          return self._random.choice([axl.Action.C, axl.Action.D])
      
      # Check if opponent has played D more than threshold in weighted history
      total_weight = sum(weight for _, weight in self.weighted_history)
      weighted_defect_rate = sum(weight for move, weight in self.weighted_history if move == axl.Action.D) / total_weight
      threshold = 0.6 - 0.1 * (weighted_defect_rate - 0.5)  # Adjust threshold based on long-term behavior
      
      if weighted_defect_rate > threshold:
          self.tit_for_tat_mode = 30
      
      if self.tit_for_tat_mode > 0:
          self.tit_for_tat_mode -= 1
          return opponent.history[-1]
      
      # Detect alternating C-D pattern
      if len(opponent.history) >= 6:
          if all(opponent.history[-i] != opponent.history[-(i+1)] for i in range(1, 6, 2)):
              return axl.Action.D
      
      # Olive branch
      if round_number - self.last_olive_branch >= self.next_olive_branch:
          self.last_olive_branch = round_number
          self.next_olive_branch = self._random.randint(40, 60)
          return axl.Action.C
      
      # Modified Tit-for-Two-Tats
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
      
      # Default to Cooperate
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For each subsequent round, make
# a decision based on the following ordered conditions:     a. If it's the final
# round, play D (defect).     b. If the opponent has played D for the last 3
# consecutive rounds, play D with 80% probability and C with 20% probability.
# c. Every 20 rounds, play a "probe" move: randomly choose C or D with equal
# probability.     d. Calculate the opponent's cooperation rate over the last 50
# rounds (or all previous rounds if fewer than 50 have been played).     e.
# Based on the opponent's cooperation rate:       - If the rate is 70% or
# higher, play C with 80% probability and D with 20% probability.       - If the
# rate is 30% or lower, play D with 80% probability and C with 20% probability.
# - If the rate is between 30% and 70%, play C with 60% probability and D with
# 40% probability.     f. Adjust the probabilities based on the cumulative score
# difference:       - If you're behind by 50 points or more, increase the
# probability of D by 10 percentage points.       - If you're ahead by 50 points
# or more, increase the probability of C by 10 percentage points.     g. If none
# of the above conditions are met, play C with 60% probability and D with 40%
# probability.  3. After each round, update the rolling statistics (opponent's
# cooperation rate and cumulative score difference).  This revised strategy
# addresses the previous critiques by: - Using a rolling window to assess the
# opponent's behavior, making it more adaptive. - Introducing more randomness to
# prevent easy exploitation. - Implementing a more nuanced response to
# defection. - Incorporating the game's payoff structure through the cumulative
# score adjustment. - Adding periodic "probe" moves to gather information about
# the opponent's strategy. - Simplifying the end-game behavior to a single
# defection on the final round.  The strategy maintains a neutral approach by
# defaulting to a 60/40 split between cooperation and defection when the
# opponent's behavior is unclear. It's also more robust against various opponent
# strategies while remaining relatively simple to understand and implement.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.opponent_coop_rate = 0
          self.cumulative_score_diff = 0
          return axl.Action.C
  
      HISTORY_WINDOW = 50
      HIGH_COOP_THRESHOLD = 0.7
      LOW_COOP_THRESHOLD = 0.3
      SCORE_DIFF_THRESHOLD = 50
      PROB_ADJUSTMENT = 0.1
      DEFAULT_COOP_PROB = 0.6
  
      if len(self.history) == 999:  # Final round
          return axl.Action.D
  
      if len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          return self._random.random_choice(0.8)
  
      if len(self.history) % 20 == 0:
          return self._random.random_choice(0.5)
  
      recent_history = min(HISTORY_WINDOW, len(opponent.history))
      self.opponent_coop_rate = opponent.history[-recent_history:].count(axl.Action.C) / recent_history
  
      if self.opponent_coop_rate >= HIGH_COOP_THRESHOLD:
          coop_prob = 0.8
      elif self.opponent_coop_rate <= LOW_COOP_THRESHOLD:
          coop_prob = 0.2
      else:
          coop_prob = DEFAULT_COOP_PROB
  
      self.cumulative_score_diff = self.score - opponent.score
      if self.cumulative_score_diff <= -SCORE_DIFF_THRESHOLD:
          coop_prob = max(0, coop_prob - PROB_ADJUSTMENT)
      elif self.cumulative_score_diff >= SCORE_DIFF_THRESHOLD:
          coop_prob = min(1, coop_prob + PROB_ADJUSTMENT)
  
      return self._random.random_choice(coop_prob)


# Here's a revised strategy that takes into account the feedback, with clear
# conditions for cooperation and defection:  1. Start by playing Cooperate (C)
# for the first round.  2. For rounds 2-10, use Tit-for-Tat: play what your
# opponent played in the previous round.  3. From round 11 onwards, use the
# following decision process in order:     a. If this is one of the last 20
# rounds of the game (rounds 981-1000):       - Play the move your opponent used
# most frequently in the previous 20 rounds.       - If there's a tie, play C.
# b. If your opponent has defected in any of the last 3 rounds:       - Play
# Defect (D).     c. If you've been mutually defecting for the last 5 rounds:
# - Play C (as a "forgiveness" mechanism to potentially restart cooperation).
# d. Otherwise:       - Play C.  4. Every 50 rounds (at rounds 50, 100, 150,
# etc.), perform this check:    - Calculate your average score for the last 50
# rounds.    - If this average is below 2:      - Play D for the next 5 rounds,
# regardless of other conditions (except for the end-game strategy in 3a).    -
# After these 5 rounds (or immediately if the average was 2 or higher), return
# to using the decision process in step 3.  This strategy maintains a neutral
# approach by starting cooperatively and then adapting based on the opponent's
# behavior. It's simple to understand and implement, with clear conditions for
# when to cooperate or defect. The strategy is more responsive to aggressive
# play than the original version, while still allowing for the possibility of
# returning to cooperation after a period of mutual defection. The end-game
# strategy is less predictable, and the periodic reassessment allows for long-
# term adaptation to the opponent's overall strategy.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.last_check_round = 0
          self.defect_count = 0
          return axl.Action.C
  
      current_round = len(self.history)
  
      # Rounds 2-10: Tit-for-Tat
      if 1 <= current_round <= 9:
          return opponent.history[-1]
  
      # Last 20 rounds (981-1000)
      if current_round > 980:
          opponent_last_20 = opponent.history[-20:]
          c_count = opponent_last_20.count(axl.Action.C)
          d_count = opponent_last_20.count(axl.Action.D)
          return axl.Action.C if c_count >= d_count else axl.Action.D
  
      # Check every 50 rounds
      if current_round - self.last_check_round >= 50:
          self.last_check_round = current_round
          last_50_score = self.total_scores(self.history[-50:], opponent.history[-50:])[0]
          if last_50_score / 50 < 2:
              self.defect_count = 5
          else:
              self.defect_count = 0
  
      # Play Defect for 5 rounds if average score was low
      if self.defect_count > 0:
          self.defect_count -= 1
          return axl.Action.D
  
      # Defect if opponent defected in last 3 rounds
      if opponent.history[-3:].count(axl.Action.D) > 0:
          return axl.Action.D
  
      # Forgiveness mechanism
      if self.history[-5:] == [axl.Action.D] * 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.C
  
      # Otherwise, cooperate (covers condition 3d)
      return axl.Action.C