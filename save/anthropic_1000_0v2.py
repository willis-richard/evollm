import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Here's a revised aggressive strategy, taking into account the feedback and
# clearly stating the conditions for cooperation or defection:  1. Start by
# playing D (defect) for the first 20 rounds.  2. For the majority of the game
# (rounds 21-900), follow these rules:     a. Play D 80% of the time and C
# (cooperate) 20% of the time as a baseline.        b. Defect (D) if any of
# these conditions are met:       - The opponent has played C in the last 2
# rounds consecutively       - Your current score is less than 60% of the
# theoretical maximum (3 points per round on average)       - The opponent has
# defected more than 70% of the time in the last 10 rounds        c. Cooperate
# (C) if all of these conditions are met:       - There has been mutual
# defection (D-D) for 5 or more consecutive rounds       - The opponent has not
# played C in the last 3 rounds       - Your current score is at least 60% of
# the theoretical maximum     d. If none of the specific conditions in b or c
# are met, revert to the 80% D, 20% C baseline.  3. For the last 100 rounds
# (901-1000):        a. Increase defection to 90% and reduce cooperation to 10%.
# b. Defect (D) if any of these conditions are met:       - The opponent has
# played C in the last round       - Your current score is behind the opponent's
# score        c. Cooperate (C) only if all of these conditions are met:       -
# There has been mutual defection (D-D) for 8 or more consecutive rounds       -
# Your current score is ahead of the opponent's score       - The random 10%
# cooperation chance occurs  4. Throughout the game, if the opponent's strategy
# appears completely random (close to 50% C and 50% D over the last 50 moves),
# stick strictly to the percentage-based decisions (80-20 or 90-10) without
# considering other conditions.  This strategy maintains an aggressive approach
# while incorporating clear conditions for cooperation and defection. It's
# simpler than the previous version, more robust against various opponent
# behaviors, and still allows for some adaptability without overly complex
# rules.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_mutual_defections = 0

      round_number = len(self.history) + 1

      # Update consecutive mutual defections
      if self.history and opponent.history:
          if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
              self.consecutive_mutual_defections += 1
          else:
              self.consecutive_mutual_defections = 0

      if round_number <= 20:
          return axl.Action.D

      # Check if opponent's strategy appears random
      if len(self.history) >= 50:
          opponent_c_ratio = opponent.history[-50:].count(axl.Action.C) / 50
          if 0.45 <= opponent_c_ratio <= 0.55:
              if round_number <= 900:
                  return axl.Action.D if self._random.random() < 0.8 else axl.Action.C
              else:
                  return axl.Action.D if self._random.random() < 0.9 else axl.Action.C

      if round_number <= 900:
          # Check defection conditions
          if (opponent.history[-2:] == [axl.Action.C, axl.Action.C] or
              self.score < 1.8 * round_number or
              sum([a == axl.Action.D for a in opponent.history[-10:]]) > 7):
              return axl.Action.D

          # Check cooperation conditions
          if (self.consecutive_mutual_defections >= 5 and
              opponent.history[-3:].count(axl.Action.C) == 0 and
              self.score >= 1.8 * round_number):
              return axl.Action.C

          # Default to 80% defection
          return axl.Action.D if self._random.random() < 0.8 else axl.Action.C

      else:
          # Last 100 rounds
          if (opponent.history[-1] == axl.Action.C or
              self.score <= opponent.score):
              return axl.Action.D

          if (self.consecutive_mutual_defections >= 8 and
              self.score > opponent.score and
              self._random.random() < 0.1):
              return axl.Action.C

          # Default to 90% defection
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C

# Here's a revised aggressive strategy, taking into account the feedback:  1.
# Start by playing D (defect) for the first 5 rounds to establish an aggressive
# stance.  2. For the remainder of the game, use the following rules:     a.
# Default Action: Play D unless other conditions are met.     b. Cooperation
# Threshold: Calculate the opponent's cooperation rate over the last 20 rounds.
# If it exceeds 80%, play C for the next round.     c. Pattern Breaking: Every
# 25 rounds, randomly choose to play C with a 20% probability, regardless of
# other conditions. This helps break out of defection cycles and makes the
# strategy less predictable.     d. Score-Based Adjustment: Every 50 rounds,
# compare your total score to the opponent's:       - If you're behind by more
# than 50 points, increase the cooperation threshold to 70% for the next 50
# rounds.       - If you're ahead by more than 100 points, decrease the
# cooperation threshold to 90% for the next 50 rounds.     e. Retaliation: If
# the opponent defects after you've cooperated, play D for the next 3 rounds
# before returning to the default strategy.     f. Forgiveness: If mutual
# defection has occurred for 10 consecutive rounds, play C for one round to test
# the waters.     g. Tit-for-Tat Detection: If the opponent's last 5 moves
# exactly match your previous 5 moves, play C for the next round to probe for a
# tit-for-tat strategy.  3. In the last 20 rounds of the game:    - If you're
# ahead in total score, always play D.    - If you're behind, alternate between
# C and D every round.  This strategy maintains an aggressive approach by
# defaulting to defection, but incorporates adaptive elements to exploit
# cooperation, break deadlocks, and respond to the opponent's behavior. The
# conditions for cooperation are clearly defined, making the strategy more
# robust against various opponent behaviors while remaining relatively simple to
# implement.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.retaliation_count = 0
          self.cooperation_threshold = 0.8
          self.threshold_adjustment_rounds = 0  # Tracks rounds left for adjusted threshold

      if len(self.history) < 5:
          return axl.Action.D

      if len(self.history) >= 980:
          if self.score > opponent.score:
              return axl.Action.D
          else:
              return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D

      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D

      if len(self.history) % 25 == 0 and self._random.random() < 0.2:
          return axl.Action.C

      if len(self.history) % 50 == 0:
          if self.score < opponent.score - 50:
              self.cooperation_threshold = 0.7
              self.threshold_adjustment_rounds = 50
          elif self.score > opponent.score + 100:
              self.cooperation_threshold = 0.9
              self.threshold_adjustment_rounds = 50

      if self.threshold_adjustment_rounds > 0:
          self.threshold_adjustment_rounds -= 1
          if self.threshold_adjustment_rounds == 0:
              self.cooperation_threshold = 0.8

      last_20_moves = opponent.history[-20:]
      if len(last_20_moves) == 20:
          cooperation_rate = sum([a == axl.Action.C for a in last_20_moves]) / 20
          if cooperation_rate > self.cooperation_threshold:
              return axl.Action.C

      if len(self.history) >= 10 and all(a == b == axl.Action.D for a, b in zip(self.history[-10:], opponent.history[-10:])):
          return axl.Action.C

      if len(self.history) >= 5 and self.history[-5:] == opponent.history[-5:]:
          return axl.Action.C

      if len(self.history) >= 1 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.retaliation_count = 3

      return axl.Action.D

# Here's a revised aggressive strategy taking into account the feedback:  1.
# Start by playing D (defect) for the first 5 rounds.  2. Throughout the game,
# maintain a rolling average of the opponent's cooperation rate over the last 20
# moves.  3. Main strategy (to be applied unless other conditions are met):    -
# If the opponent's cooperation rate is above 60%:      Play D with 80%
# probability and C with 20% probability.    - If the opponent's cooperation
# rate is 60% or below:      Play D with 90% probability and C with 10%
# probability.  4. Every 50 rounds, conduct a "cooperation test":    - Play C
# for two consecutive rounds.    - If the opponent cooperates in both rounds,
# play D for the next 3 rounds.    - After this test (regardless of outcome),
# return to the main strategy.  5. Pattern recognition:    - If the opponent has
# played the same move (C or D) for 5 consecutive rounds:      Play D for the
# next 3 rounds to exploit potential patterns.  6. Endgame strategy (last 100
# rounds):    - If your total score is higher than the opponent's:      Play D
# with 95% probability and C with 5% probability.    - If your total score is
# lower than or equal to the opponent's:      Play D with 70% probability and C
# with 30% probability.  7. Randomness factor:    - At each round, there's a 5%
# chance to play the opposite of what the strategy suggests.  Conditions for
# cooperation (C): - During the "cooperation test" every 50 rounds. - With 20%
# probability when the opponent's cooperation rate is above 60%. - With 10%
# probability when the opponent's cooperation rate is 60% or below. - With 30%
# probability in the endgame if losing or tied. - When the randomness factor
# triggers (5% chance) and the strategy suggests D.  Conditions for defection
# (D): - First 5 rounds of the game. - With 80% probability when the opponent's
# cooperation rate is above 60%. - With 90% probability when the opponent's
# cooperation rate is 60% or below. - For 3 rounds after a successful
# "cooperation test". - For 3 rounds when a 5-round pattern is detected. - With
# 95% probability in the endgame if winning. - With 70% probability in the
# endgame if losing or tied. - When the randomness factor triggers (5% chance)
# and the strategy suggests C.  This strategy maintains an aggressive approach
# while incorporating adaptability to the opponent's behavior, pattern
# recognition, and a degree of unpredictability. It's simpler than the previous
# version and clearly defines when to cooperate or defect based on specific
# conditions.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.cooperation_rate = []
          self.last_cooperation_test = 0
          self.consecutive_same_moves = 0
          self.last_move = None
          self.test_phase = 0
          self.pattern_defect_count = 0
          self.avg_cooperation = 0

      if len(self.history) < 5:
          return axl.Action.D

      # Update rolling average of opponent's cooperation rate
      if len(self.history) > 20:
          recent_cooperations = sum([a == axl.Action.C for a in opponent.history[-20:]])
          self.cooperation_rate.append(recent_cooperations / 20)
          if len(self.cooperation_rate) > 20:
              self.cooperation_rate.pop(0)
          self.avg_cooperation = sum(self.cooperation_rate) / len(self.cooperation_rate)

      # Pattern recognition
      if opponent.history[-1] == self.last_move:
          self.consecutive_same_moves += 1
      else:
          self.consecutive_same_moves = 0
      self.last_move = opponent.history[-1]

      if self.consecutive_same_moves >= 5:
          self.pattern_defect_count = 3
      if self.pattern_defect_count > 0:
          self.pattern_defect_count -= 1
          return axl.Action.D

      # Cooperation test
      if len(self.history) - self.last_cooperation_test >= 50:
          self.last_cooperation_test = len(self.history)
          self.test_phase = 2
          return axl.Action.C

      if self.test_phase > 0:
          if self.test_phase == 2:
              self.test_phase -= 1
              return axl.Action.C
          elif self.test_phase == 1:
              if opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
                  self.test_phase = -3
              else:
                  self.test_phase = 0
      if self.test_phase < 0:
          self.test_phase += 1
          return axl.Action.D

      # Endgame strategy
      if len(self.history) >= 900:
          if self.score > opponent.score:
              defect_prob = 0.95
          else:
              defect_prob = 0.70
      else:
          if self.avg_cooperation > 0.6:
              defect_prob = 0.80
          else:
              defect_prob = 0.90

      # Randomness factor
      if self._random.random() < 0.05:
          defect_prob = 1 - defect_prob

      return axl.Action.D if self._random.random() < defect_prob else axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) for the first 3 rounds.  2. For subsequent rounds, use
# the following decision-making process:     a. Calculate the opponent's
# cooperation rate (OCR) over the last 100 rounds (or all previous rounds if
# fewer than 100).     b. Set a base cooperation probability (BCP) as follows:
# - If the opponent cooperated in the previous round: BCP = 1.0       - If the
# opponent defected in the previous round: BCP = 0.8     c. Adjust the final
# cooperation probability (FCP) by multiplying BCP by OCR:       FCP = BCP * OCR
# d. Make your move:       - Cooperate (C) with probability FCP       - Defect
# (D) with probability (1 - FCP)  3. Pattern recognition override:    If you
# detect a consistent alternating pattern (CDCDCD or DCDCDC) over the last 6
# rounds:    - Play C for the next 2 rounds    - Play D for the 3rd round    -
# Then return to the main decision-making process  Conditions for cooperation: -
# Always in the first 3 rounds - With probability FCP in subsequent rounds - For
# 2 out of 3 rounds when an alternating pattern is detected  Conditions for
# defection: - With probability (1 - FCP) in rounds after the first 3 - For 1
# out of 3 rounds when an alternating pattern is detected  This strategy is
# cooperative, starting with cooperation and maintaining a high probability of
# cooperation when the opponent cooperates. It adapts to the opponent's overall
# level of cooperation through the OCR factor, becoming less cooperative if the
# opponent frequently defects. The pattern recognition component helps to
# exploit predictable opponents while still allowing a return to the main
# cooperative strategy. The strategy is simpler than the previous version, with
# clear conditions for cooperation and defection based on probabilities derived
# from the opponent's recent and overall behavior.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.pattern_count = 0
          self.pattern_mode = False

      if len(self.history) < 3:
          return axl.Action.C

      if self.pattern_mode:
          self.pattern_count += 1
          if self.pattern_count <= 2:
              return axl.Action.C
          elif self.pattern_count == 3:
              self.pattern_mode = False
              self.pattern_count = 0
              return axl.Action.D

      last_6_moves = opponent.history[-6:]
      if len(last_6_moves) == 6:
          if last_6_moves == [axl.Action.C, axl.Action.D] * 3 or last_6_moves == [axl.Action.D, axl.Action.C] * 3:
              self.pattern_mode = True
              self.pattern_count = 0
              return axl.Action.C

      recent_history = opponent.history[-100:]
      opponent_cooperation_rate = sum(action == axl.Action.C for action in recent_history) / len(recent_history)

      base_cooperation_probability = 1.0 if opponent.history[-1] == axl.Action.C else 0.8
      final_cooperation_probability = base_cooperation_probability * opponent_cooperation_rate

      return axl.Action.C if self._random.random() < final_cooperation_probability else axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. For each subsequent round,
# determine your move as follows:     a. Cooperation condition:       - If the
# opponent has not defected in the last two rounds, play C.       - OR if a
# random number between 0 and 1 is less than 0.02 (2% chance), play C.     b.
# Defection condition:       - If the opponent has defected in both of the last
# two rounds, calculate the defection rate:         * Count the number of
# defections by the opponent in the last 10 rounds.         * Defection rate =
# (number of defections) / 10       - Generate a random number between 0 and 1.
# - If this random number is less than the defection rate, play D. Otherwise,
# play C.     c. Pattern matching:       - Check the opponent's last 6 moves for
# a clear alternating pattern (CDCDCD or DCDCDC).       - If such a pattern is
# detected, match it for the next 3 moves.       - After these 3 moves, return
# to step 2a.  3. If none of the above conditions are met, play C.  This
# strategy: - Starts cooperatively and maintains cooperation when the opponent
# is cooperative. - Uses a forgiving "Tit-for-Two-Tats" approach as its base. -
# Has a small chance (2%) of random cooperation to break negative cycles. -
# Adapts to aggressive behavior by increasing the probability of defection based
# on the opponent's recent actions. - Can recognize and temporarily adapt to
# simple alternating patterns. - Defaults to cooperation when no other condition
# is met, maintaining its overall cooperative nature.  The strategy is simpler
# than the previous version, removing complex elements like score tracking and
# end-game adjustments. It provides clear conditions for when to cooperate or
# defect, making it easier to implement and understand while still being
# adaptive to various opponent behaviors.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if len(self.history) < 2:
          return axl.Action.C

      last_two_opponent_moves = opponent.history[-2:]

      if last_two_opponent_moves.count(axl.Action.D) == 0 or self._random.random() < 0.02:
          return axl.Action.C

      if last_two_opponent_moves == [axl.Action.D, axl.Action.D]:
          defection_rate = sum([a == axl.Action.D for a in opponent.history[-10:]]) / 10
          if self._random.random() < defection_rate:
              return axl.Action.D

      if len(self.history) >= 6:
          last_six = opponent.history[-6:]
          if last_six == [axl.Action.C, axl.Action.D] * 3 or last_six == [axl.Action.D, axl.Action.C] * 3:
              if not hasattr(self, '_pattern_counter'):
                  self._pattern_counter = 0
              if self._pattern_counter < 3:
                  self._pattern_counter += 1
                  return last_six[self._pattern_counter % 2]
              else:
                  self._pattern_counter = 0

      return axl.Action.C


# Here's a revised strategy that takes into account the feedback, focusing on
# simplicity, neutrality, and robustness:  1. Start with cooperation (C) in the
# first round.  2. For the remainder of the game, use the following rules:
# a. Keep track of two metrics:       - Recent cooperation rate: The proportion
# of cooperative moves by the opponent in the last 50 rounds.       - Overall
# cooperation rate: The proportion of cooperative moves by the opponent
# throughout the entire game.     b. Base decision on the following conditions:
# - If the recent cooperation rate is greater than 60%, cooperate.       - If
# the recent cooperation rate is less than 40%, defect.       - If the recent
# cooperation rate is between 40% and 60%:         * Cooperate if the opponent
# cooperated in the previous round.         * Defect if the opponent defected in
# the previous round.     c. Forgiveness mechanism: If there have been 5 or more
# consecutive rounds of mutual defection, cooperate with a 50% probability.
# d. Unpredictability: Regardless of the above conditions, make a random move
# with a 5% probability.  3. End-game adjustment (last 100 rounds):    -
# Calculate the probability of defection as: (1 - overall cooperation rate) *
# (remaining rounds / 100)    - Use this probability to decide whether to defect
# or follow the main strategy for each of the last 100 rounds.  This strategy
# maintains neutrality by starting cooperatively and basing subsequent moves
# primarily on the opponent's behavior. It's simpler than the previous version,
# with clear conditions for cooperation and defection. The forgiveness mechanism
# helps break cycles of mutual defection, while the random element adds
# unpredictability. The end-game adjustment allows for a gradual and adaptive
# transition based on the opponent's overall behavior.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.consecutive_mutual_defections = 0
          self.recent_history_size = 50
          return axl.Action.C

      recent_history = opponent.history[-self.recent_history_size:]
      recent_cooperation_rate = sum([a == axl.Action.C for a in recent_history]) / len(recent_history)
      overall_cooperation_rate = opponent.history.cooperations / len(opponent.history)

      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])

      if len(self.history) > 900:
          defection_probability = (1 - overall_cooperation_rate) * ((1000 - len(self.history)) / 100)
          if self._random.random() < defection_probability:
              return axl.Action.D

      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_mutual_defections += 1
      else:
          self.consecutive_mutual_defections = 0

      if self.consecutive_mutual_defections >= 5 and self._random.random() < 0.5:
          return axl.Action.C

      if recent_cooperation_rate > 0.6:
          return axl.Action.C
      elif recent_cooperation_rate < 0.4:
          return axl.Action.D
      else:
          return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. For each subsequent round, follow
# these rules in order:     a. If it's one of the last 50 rounds, calculate a
# defection probability:       - Base probability = 10% + (current round - 950)
# * 1%       - If a random number (0-100) is less than this probability, defect
# (D).       - If not, continue to the next rule.     b. If your score is more
# than 10 points behind your opponent's, defect (D).     c. If your opponent has
# defected N times in a row (where N is between 2 and 5):       - Defect (D) for
# the next N rounds.       - Reset the consecutive defection counter after these
# N rounds.     d. If none of the above conditions are met, have a 10% chance to
# defect (D) randomly.     e. If you haven't defected based on the above rules,
# play Tit-for-Tat:       - If your opponent cooperated in the previous round,
# cooperate (C).       - If your opponent defected in the previous round, defect
# (D).  This strategy maintains a neutral approach by primarily using Tit-for-
# Tat, while incorporating elements to prevent exploitation and adapt to
# different situations. It's simpler than the previous version and addresses the
# main points of feedback:  1. It's clearer about when to cooperate or defect.
# 2. The periodic defection is now probabilistic rather than on fixed intervals.
# 3. The punishment for repeated defection is proportional to the number of
# defections observed. 4. The score-based catch-up mechanism triggers more
# quickly. 5. The endgame strategy gradually increases the probability of
# defection.  This strategy should be more robust against various opponent
# behaviors while maintaining a generally neutral stance. It balances
# cooperation with self-protection and occasional probing defections.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_defections = 0
          self.punishment_rounds = 0
          return axl.Action.C

      if len(self.history) > 950:
          defection_probability = 0.1 + (len(self.history) - 950) * 0.01
          if self._random.random() < defection_probability:
              return axl.Action.D

      if self.score < opponent.score - 10:
          return axl.Action.D

      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          if self.punishment_rounds == 0:
              self.consecutive_defections = 0
          return axl.Action.D

      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0

      if 2 <= self.consecutive_defections <= 5:
          self.punishment_rounds = self.consecutive_defections
          return axl.Action.D

      if self._random.random() < 0.1:
          return axl.Action.D

      return opponent.history[-1]

# Here's a revised strategy incorporating the feedback:  1. Start by playing C
# in the first round.  2. For the next 9 rounds, mirror your opponent's previous
# move.  3. After the first 10 rounds, implement the following approach:     a.
# Keep track of your opponent's cooperation rate over the last 20 moves.    b.
# If the opponent played C in the previous round:       - Play C.    c. If the
# opponent played D in the previous round:       - Calculate the probability of
# cooperation (P) as: P = opponent's cooperation rate * 0.8       - Play C with
# probability P, and D with probability (1 - P).  4. Every 30-50 rounds
# (randomly determined), evaluate your opponent's behavior:    a. Calculate the
# difference between your score and your opponent's score.    b. If the
# opponent's score is more than 50 points higher than yours:       - Play D for
# the next 3-5 rounds (randomly determined).    c. Otherwise, continue with the
# strategy from step 3.  5. Implement a simple pattern recognition:    a. If the
# opponent has played the same move for 5 consecutive rounds:       - If they've
# been playing C, play C.       - If they've been playing D, play D.    b. If
# the opponent has been alternating C and D for 6 consecutive rounds:       -
# Play D on their expected C round, and C on their expected D round.  6. In the
# last 10 rounds of the game, switch to always playing D.  This strategy
# maintains a neutral approach by adapting to the opponent's behavior while
# protecting against exploitation. It will cooperate when: - The opponent
# cooperated in the previous round. - The opponent has been consistently
# cooperative recently. - A pattern of consistent cooperation is detected.  It
# will defect when: - The opponent defected in the previous round (with a
# probability based on recent behavior). - The opponent's score is significantly
# higher. - A pattern of consistent defection is detected. - In the final rounds
# of the game.  The strategy remains relatively simple while being more robust
# against various opponent behaviors. It adapts to the opponent's recent
# actions, protects against exploitation, and attempts to capitalize on
# detectable patterns.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.last_evaluation = 0
          self.consecutive_c = 0
          self.consecutive_d = 0
          self.defect_counter = 0
          return axl.Action.C

      if len(self.history) <= 10:
          return opponent.history[-1]

      if len(self.history) >= 990:
          return axl.Action.D

      if self.defect_counter > 0:
          self.defect_counter -= 1
          return axl.Action.D

      opponent_c_rate = sum([a == axl.Action.C for a in opponent.history[-20:]]) / 20

      if len(self.history) - self.last_evaluation >= self._random.randint(30, 50):
          self.last_evaluation = len(self.history)
          if opponent.score > self.score + 50:
              self.defect_counter = self._random.randint(3, 5)
              return axl.Action.D

      if opponent.history[-1] == axl.Action.C:
          self.consecutive_c += 1
          self.consecutive_d = 0
      else:
          self.consecutive_d += 1
          self.consecutive_c = 0

      if self.consecutive_c >= 5:
          return axl.Action.C
      if self.consecutive_d >= 5:
          return axl.Action.D

      if len(opponent.history) >= 6:
          last_six = opponent.history[-6:]
          if last_six == [axl.Action.C, axl.Action.D] * 3:
              return axl.Action.D
          elif last_six == [axl.Action.D, axl.Action.C] * 3:
              return axl.Action.C

      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          p = opponent_c_rate * 0.8
          return self._random.random_choice(p)

# Here's the revised strategy, taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. For all subsequent rounds:
# a. Calculate the opponent's cooperation rate over the last 10 rounds.
# b. Determine your action based on the following conditions:           - If the
# opponent's cooperation rate is above 70%:         * Play Cooperate (C)
# - If the opponent's cooperation rate is between 30% and 70%:         * If the
# opponent's last move was Cooperate (C):           - Play Cooperate (C)
# * If the opponent's last move was Defect (D):           - Play Cooperate (C)
# with a probability of (70 - R)%, where R is the round number divided by 20
# (rounded down). This gradually decreases forgiveness.           - Otherwise,
# play Defect (D)              - If the opponent's cooperation rate is below
# 30%:         * If the opponent's last move was Cooperate (C):           - Play
# Cooperate (C)         * If the opponent's last move was Defect (D):
# - Play Defect (D)  3. After determining your action based on the above rules,
# there's a 5% chance to override this decision and make a random move instead
# (50% chance each for C or D).  This strategy maintains a neutral approach by
# adapting to the opponent's level of cooperation. It's simple to understand and
# implement, with clear conditions for cooperation and defection. The strategy
# becomes slightly less forgiving as the game progresses, and includes a small
# random element to prevent exploitation by pattern-recognizing opponents.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      if len(self.history) < 10:
          last_10_rounds = self.history
      else:
          last_10_rounds = self.history[-10:]

      opponent_cooperation_rate = 1 - sum([a == axl.Action.D for a in opponent.history[-len(last_10_rounds):]]) / len(last_10_rounds)
      opponent_last_move = opponent.history[-1]
      round_number = len(self.history) + 1

      if opponent_cooperation_rate > 0.7:
          action = axl.Action.C
      elif 0.3 <= opponent_cooperation_rate <= 0.7:
          if opponent_last_move == axl.Action.C:
              action = axl.Action.C
          else:
              R = round_number // 20
              forgiveness_probability = max(0, (70 - R) / 100)
              if self._random.random() < forgiveness_probability:
                  action = axl.Action.C
              else:
                  action = axl.Action.D
      else:
          if opponent_last_move == axl.Action.C:
              action = axl.Action.C
          else:
              action = axl.Action.D

      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])
      else:
          return action


# Here's a revised aggressive strategy taking into account the feedback:  1.
# Start the game by playing D (defect) for the first 10 rounds.  2. For rounds
# 11 to 950:     a. Play D with 80% probability and C with 20% probability as
# the default behavior.     b. However, adjust this behavior based on the
# opponent's recent actions:       - If the opponent has played C in all of the
# last 3 rounds, play D for the next 5 rounds.       - If the opponent has
# played D in all of the last 3 rounds, play C in the next round, then return to
# the default behavior.     c. Every 50 rounds, play D for 3 consecutive rounds
# regardless of the opponent's actions. This serves as a periodic aggressive
# reminder.  3. For the final 50 rounds (951-1000), always play D.  Conditions
# for cooperation (C): - 20% of the time in the default behavior (rounds
# 11-950). - Immediately after the opponent has defected for 3 consecutive
# rounds.  Conditions for defection (D): - First 10 rounds of the game. - 80% of
# the time in the default behavior (rounds 11-950). - For 5 rounds after the
# opponent has cooperated for 3 consecutive rounds. - Every 50 rounds, for 3
# consecutive rounds. - Final 50 rounds of the game.  This strategy maintains an
# aggressive stance while incorporating simple adaptive elements. It's less
# predictable due to the probabilistic approach, yet still has clear conditions
# for cooperation and defection. The strategy aims to exploit cooperative
# opponents while having a mechanism to occasionally cooperate against
# consistently aggressive opponents.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_c_count = 0
          self.periodic_d_count = 0
          self.play_c_after_d = False

      round_number = len(self.history) + 1

      if round_number <= 10 or round_number > 950:
          return axl.Action.D

      if round_number % 50 == 0:
          self.periodic_d_count = 3

      if self.periodic_d_count > 0:
          self.periodic_d_count -= 1
          return axl.Action.D

      opponent_last_3 = opponent.history[-3:]
      if len(opponent_last_3) == 3:
          if all(action == axl.Action.C for action in opponent_last_3):
              self.consecutive_c_count = 5
              self.play_c_after_d = False
          elif all(action == axl.Action.D for action in opponent_last_3):
              self.play_c_after_d = True

      if self.play_c_after_d:
          self.play_c_after_d = False
          return axl.Action.C

      if self.consecutive_c_count > 0:
          self.consecutive_c_count -= 1
          return axl.Action.D

      return axl.Action.D if self._random.random() < 0.8 else axl.Action.C


# Here's a revised strategy incorporating the feedback:  1. Start by playing C
# (cooperate) for the first round.  2. For subsequent rounds:    a) If the
# opponent played C in the last round:       - Play C.    b) If the opponent
# played D in the last round:       - If this is the first D in the last 3
# rounds, play C (forgive once).       - If this is the second or third D in the
# last 3 rounds, play D.  3. Pattern adaptation:    - If the opponent has
# alternated C and D for the last 4 rounds, predict their next move and play the
# opposite (to encourage cooperation).  4. Trust building:    - After playing D,
# if the opponent plays C, immediately return to C.    - If both you and the
# opponent have played D for 2 or more consecutive rounds, play C on the next
# round to attempt to break the cycle.  5. Random cooperation:    - With a 5%
# probability, play C even if the strategy suggests D.  6. Periodic cooperation
# reset:    - Every 50 rounds, play C regardless of the opponent's previous
# move.  7. Defensive adjustment:    - If the opponent has played D 3 or more
# times in the last 5 rounds:      - Switch to strict Tit-for-Tat for the next
# 10 rounds (play whatever the opponent played in the previous round).      -
# After 10 rounds, return to the main strategy.  8. End game strategy (last 10
# rounds):    - If the mutual cooperation rate (both playing C) in the last 20
# rounds is 70% or higher, continue with the main strategy.    - If the mutual
# cooperation rate is below 70%, switch to Tit-for-Tat for the remaining rounds.
# This revised strategy maintains a cooperative approach while being more
# adaptive to various opponent behaviors. It clearly specifies conditions for
# cooperation and defection, incorporates pattern recognition, includes
# mechanisms for breaking negative cycles, and adjusts for end-game scenarios.
# The strategy remains relatively simple while being more robust against
# potential exploitation.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.tft_mode = False
          self.tft_rounds = 0
          return axl.Action.C

      if len(self.history) % 50 == 0:
          return axl.Action.C

      if self.tft_mode:
          self.tft_rounds += 1
          if self.tft_rounds >= 10:
              self.tft_mode = False
              self.tft_rounds = 0
          return opponent.history[-1]

      if len(self.history) >= 990:
          mutual_cooperation = sum([a == b == axl.Action.C for a, b in zip(self.history[-20:], opponent.history[-20:])])
          if mutual_cooperation / 20 < 0.7:
              return opponent.history[-1]

      opponent_last_3 = opponent.history[-3:]
      opponent_last_4 = opponent.history[-4:]
      opponent_last_5 = opponent.history[-5:]

      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      defections_last_3 = sum([a == axl.Action.D for a in opponent_last_3])
      if defections_last_3 == 1:
          return axl.Action.C
      elif defections_last_3 >= 2:
          return axl.Action.D

      if opponent_last_4 == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
          return axl.Action.C if opponent.history[-1] == axl.Action.D else axl.Action.D

      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      if self.history[-2:] == [axl.Action.D, axl.Action.D] and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.C

      defections_last_5 = sum([a == axl.Action.D for a in opponent_last_5])
      if defections_last_5 >= 3:
          self.tft_mode = True
          self.tft_rounds = 0
          return opponent.history[-1]

      if self._random.random() < 0.05:
          return axl.Action.C

      return axl.Action.D


# Here's a revised cooperative strategy based on the feedback:  1. Start by
# cooperating in the first round.  2. For subsequent rounds, use the following
# rules:     a) If the opponent cooperated in the previous round:       -
# Cooperate     b) If the opponent defected in the previous round:       -
# Calculate the forgiveness rate:         * Start with a base rate of 20%
# * Increase the rate by 2% for each of the opponent's cooperative moves in the
# last 10 rounds         * Decrease the rate by 2% for each of the opponent's
# defections in the last 10 rounds         * Ensure the forgiveness rate stays
# between 10% and 40%       - Cooperate with the probability equal to the
# calculated forgiveness rate       - Otherwise, defect  3. Override rules:
# a) If there have been 5 consecutive rounds of mutual defection:       -
# Cooperate in the next round, regardless of the opponent's last move     b) If
# the opponent has cooperated for 10 consecutive rounds:       - Cooperate for
# the next 3 rounds, regardless of the opponent's moves  4. Maintain this
# strategy consistently until the end of the game (all 1000 rounds).  This
# strategy aims to be cooperative while adapting to the opponent's behavior. It
# starts cooperatively, responds in kind to cooperation, and has a dynamic
# forgiveness rate for defection. The override rules help break out of negative
# cycles and reward consistent cooperation. By maintaining the same approach
# throughout the game, it avoids potential exploitation in the endgame while
# still promoting cooperation.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_mutual_defections = 0
          self.opponent_consecutive_cooperations = 0
          self.cooperate_counter = 0
          return axl.Action.C

      if self.cooperate_counter > 0:
          self.cooperate_counter -= 1
          return axl.Action.C

      if opponent.history[-1] == axl.Action.C:
          self.opponent_consecutive_cooperations += 1
          self.consecutive_mutual_defections = 0
          if self.opponent_consecutive_cooperations == 10:
              self.cooperate_counter = 3
          return axl.Action.C
      else:
          self.opponent_consecutive_cooperations = 0

      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_mutual_defections += 1
      else:
          self.consecutive_mutual_defections = 0

      if self.consecutive_mutual_defections == 5:
          self.consecutive_mutual_defections = 0
          return axl.Action.C

      opponent_last_10 = opponent.history[-10:]
      coop_count = sum([a == axl.Action.C for a in opponent_last_10])
      defect_count = len(opponent_last_10) - coop_count

      forgiveness_rate = 0.2 + 0.02 * coop_count - 0.02 * defect_count
      forgiveness_rate = max(0.1, min(0.4, forgiveness_rate))

      if self._random.random() < forgiveness_rate:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a revised aggressive strategy, taking into account the feedback:  1.
# Initial Phase (Rounds 1-20):    - Play D (defect) for all 20 rounds.  2. Early
# Adaptation Phase (Rounds 21-50):    - Calculate the opponent's cooperation
# rate from the first 20 rounds.    - If their cooperation rate was > 25%:
# - Play D with 80% probability and C with 20% probability.    - If their
# cooperation rate was ≤ 25%:      - Play D for all 30 rounds.  3. Main Game
# Phase (Rounds 51-900):    - Use a modified "generous tit-for-tat with
# punishment" strategy:      a. If the opponent played D in the previous round:
# - Play D.      b. If the opponent played C in the previous round:         -
# Calculate their cooperation rate over the last 20 rounds.         - Play C
# with a probability equal to (their cooperation rate - 10%), but never
# exceeding 30%.         - Play D with the remaining probability.      c.
# Punishment rule: If the opponent has played D for 3 consecutive rounds:
# - Play D for the next 5 rounds, regardless of the opponent's moves.  4.
# Periodic Adjustment (Every 50 rounds):    - Calculate the opponent's
# cooperation rate over the last 50 rounds.    - Adjust your C play probability
# to be (their cooperation rate - 10%), but never exceeding 30%.    - Play C
# once as a "probe" move immediately after this adjustment.  5. End Game Phase
# (Rounds 901-1000):    - Start with 80% probability of playing D.    - Every 10
# rounds, increase the probability of playing D by 2%.    - By round 1000,
# you'll be playing D with 98% probability.  6. Override Rule:    - If at any
# point your cumulative score falls behind the opponent's by more than 20 points
# (calculated over the last 50 rounds):      - Play D for the next 10 rounds.
# This strategy maintains an aggressive stance while adapting to the opponent's
# behavior. It's clear about when to cooperate or defect based on specific
# conditions and probabilities. The strategy is more robust against various
# opponent behaviors while still prioritizing an aggressive approach.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.punishment_counter = 0
          self.end_game_defect_prob = 0.8
          self.coop_prob = 0

      round_number = len(self.history) + 1

      # Override Rule
      if len(self.history) >= 50:
          my_score, opp_score = self.total_scores(self.history[-50:], opponent.history[-50:])
          if opp_score - my_score > 20:
              return axl.Action.D

      # Initial Phase (Rounds 1-20)
      if round_number <= 20:
          return axl.Action.D

      # Early Adaptation Phase (Rounds 21-50)
      elif 21 <= round_number <= 50:
          if round_number == 21:
              coop_rate = opponent.history[:20].count(axl.Action.C) / 20
              self.early_adaptation_coop_prob = 0.2 if coop_rate > 0.25 else 0
          return axl.Action.C if self._random.random() < self.early_adaptation_coop_prob else axl.Action.D

      # Main Game Phase (Rounds 51-900) and End Game Phase (Rounds 901-1000)
      else:
          # Periodic Adjustment (every 50 rounds)
          if round_number % 50 == 1:
              coop_rate = sum(1 for move in opponent.history[-50:] if move == axl.Action.C) / 50
              self.coop_prob = min(max(coop_rate - 0.1, 0), 0.3)
              return axl.Action.C  # Probe move

          # Punishment rule
          if self.punishment_counter > 0:
              self.punishment_counter -= 1
              return axl.Action.D

          # Check for 3 consecutive defections
          if len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
              self.punishment_counter = 5
              return axl.Action.D

          # End Game Phase (Rounds 901-1000)
          if round_number > 900:
              if round_number % 10 == 1:
                  self.end_game_defect_prob = min(self.end_game_defect_prob + 0.02, 0.98)
              return axl.Action.D if self._random.random() < self.end_game_defect_prob else axl.Action.C

          # Modified generous tit-for-tat with punishment
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          else:
              coop_rate = sum(1 for move in opponent.history[-20:] if move == axl.Action.C) / 20
              return axl.Action.C if self._random.random() < min(max(coop_rate - 0.1, 0), 0.3) else axl.Action.D

      # Default action (should never reach here)
      return axl.Action.D

# Here's a revised aggressive strategy, taking into account the feedback:  1.
# Start by playing D (defect) for the first 10 rounds to establish an aggressive
# stance.  2. For the remainder of the game, use a sliding window of the last 20
# rounds to assess opponent behavior:     a. If the opponent played C more than
# 60% of the time in the last 20 rounds:       - Play D with 90% probability
# - Play C with 10% probability (as a probe and to introduce unpredictability)
# b. If the opponent played D more than 60% of the time in the last 20 rounds:
# - Play tit-for-tat for the next 5 rounds (copy opponent's previous move)
# - Then play D for the next 5 rounds regardless of opponent's moves     c. If
# the opponent's play is between 40-60% C and D (mixed or alternating strategy):
# - Play D consistently  3. Every 25 rounds, compare your total score to your
# opponent's:    - If your score is lower, play D for the next 10 rounds    - If
# your score is higher, continue with the current strategy  4. If you detect a
# clear alternating pattern from the opponent (CDCDCD or similar) over the last
# 10 rounds:    - Play D consistently for the next 10 rounds  5. For the last
# 100 rounds of the game:    - Play D with 95% probability    - Play C with 5%
# probability (to maintain a small element of unpredictability)  6. Throughout
# the game, if none of the above conditions are met (i.e., opponent strategy
# seems random):    - Play D with 80% probability    - Play C with 20%
# probability  This strategy maintains an aggressive stance while being more
# adaptive and less predictable. It will cooperate in the following situations:
# 1. As a periodic probe (10% of the time) when the opponent is mostly
# cooperative 2. During the tit-for-tat phase if the opponent played C in the
# previous round 3. Rarely (5% of the time) in the end game 4. Occasionally (20%
# of the time) when the opponent's strategy seems random  In all other
# situations, it will defect, maintaining its overall aggressive nature.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.tit_for_tat_counter = 0
          self.forced_defect_counter = 0
          self.alternating_defect_counter = 0

      if len(self.history) < 10:
          return axl.Action.D

      if len(self.history) >= 900:
          return self._random.random_choice(0.95)

      last_20_opponent_moves = opponent.history[-20:]
      opponent_c_ratio = sum([a == axl.Action.C for a in last_20_opponent_moves]) / 20

      if len(self.history) % 25 == 0:
          if self.score < opponent.score:
              self.forced_defect_counter = 10

      if self.forced_defect_counter > 0:
          self.forced_defect_counter -= 1
          return axl.Action.D

      if self.alternating_defect_counter > 0:
          self.alternating_defect_counter -= 1
          return axl.Action.D

      if opponent_c_ratio > 0.6:
          return self._random.random_choice(0.9)

      if opponent_c_ratio < 0.4:
          if self.tit_for_tat_counter > 0:
              self.tit_for_tat_counter -= 1
              return opponent.history[-1]
          elif self.tit_for_tat_counter == 0:
              self.forced_defect_counter = 5
              self.tit_for_tat_counter = 5
          return axl.Action.D

      if 0.4 <= opponent_c_ratio <= 0.6:
          return axl.Action.D

      last_10_opponent_moves = opponent.history[-10:]
      if sum([last_10_opponent_moves[i] != last_10_opponent_moves[i+1] for i in range(9)]) >= 8:
          self.alternating_defect_counter = 10
          return axl.Action.D

      return self._random.random_choice(0.8)

# Here's a revised aggressive strategy, taking into account the feedback:  1.
# Start by playing D (defect) for the first 10 rounds to establish an aggressive
# stance.  2. For the remainder of the game, use the following rules:     a. If
# the opponent has played C (cooperate) in 2 out of the last 3 rounds, play D to
# exploit their cooperation.        b. If the opponent has played D in 5
# consecutive rounds, play C once to test for cooperation. If they respond with
# C, play D in the next round. If they respond with D, continue with D.
# c. If your score is more than 30 points behind your opponent's, play C for 5
# rounds to attempt to encourage cooperation and close the gap. After these 5
# rounds, revert to D regardless of the outcome.        d. Every 50 rounds, play
# C once to test the opponent's response, then immediately return to D in the
# next round regardless of their move.        e. In all other situations, play
# D.  3. For the last 30 rounds of the game, always play D regardless of the
# opponent's moves.  4. Reset mechanism: If your strategy has resulted in a
# lower score than your opponent for 100 consecutive rounds, reset by playing 5
# rounds of C followed by reverting to the main strategy from step 2.  This
# strategy maintains an aggressive approach by defaulting to defection in most
# cases, while incorporating limited elements of cooperation and adaptation. The
# conditions for cooperation are clearly defined:  - When testing an aggressive
# opponent (2b) - When significantly behind in score (2c) - Periodic testing
# every 50 rounds (2d) - During the reset mechanism  In all other cases,
# including the start and end of the game, the strategy defects. This approach
# should be more robust against various opponent behaviors while remaining
# relatively simple and predominantly aggressive.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_d_count = 0
          self.reset_counter = 0
          self.c_test_counter = 0
          self.c_test_active = False
          self.behind_counter = 0
          self.test_opponent_response = False
          self.in_reset_mode = False

      if len(self.history) < 10:
          return axl.Action.D

      if len(self.history) > 970:
          return axl.Action.D

      if self.in_reset_mode:
          if self.reset_counter > 0:
              self.reset_counter -= 1
              return axl.Action.C
          else:
              self.in_reset_mode = False

      if self.c_test_active:
          self.c_test_active = False
          return axl.Action.D

      if self.test_opponent_response:
          self.test_opponent_response = False
          return axl.Action.D

      opponent_last_3 = opponent.history[-3:]
      if sum([a == axl.Action.C for a in opponent_last_3]) >= 2:
          return axl.Action.D

      if sum([a == axl.Action.D for a in opponent.history[-5:]]) == 5:
          self.test_opponent_response = True
          return axl.Action.C

      if opponent.score - self.score > 30 and self.behind_counter == 0:
          self.behind_counter = 5
          return axl.Action.C

      if self.behind_counter > 0:
          self.behind_counter -= 1
          return axl.Action.C

      if len(self.history) % 50 == 0:
          self.c_test_active = True
          return axl.Action.C

      if opponent.score > self.score:
          self.consecutive_d_count += 1
          if self.consecutive_d_count >= 100:
              self.consecutive_d_count = 0
              self.in_reset_mode = True
              self.reset_counter = 5
              return axl.Action.C
      else:
          self.consecutive_d_count = 0

      return axl.Action.D

# Here's a revised aggressive strategy incorporating the feedback:  1. Start by
# playing D (defect) for the first 10 rounds to establish dominance.  2. For the
# remainder of the game, use the following rules:     a. Calculate the
# opponent's cooperation rate over the last 50 rounds.        b. If the
# opponent's cooperation rate is:       - Above 80%: Play C (cooperate) for 1
# round, then D for 2 rounds.       - Between 60% and 80%: Play C for 1 round,
# then D for 3 rounds.       - Between 40% and 60%: Play D for 4 rounds, then C
# for 1 round.       - Below 40%: Play D for 5 rounds.  3. Every 100 rounds,
# regardless of the opponent's strategy, play C for 1 round to test their
# willingness to cooperate. If they cooperate, play D immediately after.  4.
# Track the cumulative score difference. If you're behind:    - By 10-20 points:
# Increase the frequency of D by playing one additional D in each cycle.    - By
# more than 20 points: Play D for 10 consecutive rounds, then resume the regular
# strategy.  5. If there have been 20 consecutive rounds of mutual defection,
# play C for 1 round as a "forgiveness" mechanism, then resume the regular
# strategy.  6. In the last 50 rounds of the game:    - If the opponent's
# overall cooperation rate for the entire game is above 70%, alternate between C
# and D.    - Otherwise, play D consistently.  7. Never play more than 2
# consecutive C moves, even if the opponent seems consistently cooperative.
# This strategy maintains an aggressive stance while being more adaptive to the
# opponent's behavior. It clearly defines when to cooperate or defect based on
# the opponent's recent actions, the overall game state, and the game
# progression. The strategy is more robust against various opponent behaviors
# while remaining relatively simple to implement.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.cycle_position = 0
          self.d_streak = 0
          self.c_streak = 0
          self.score_deficit_counter = 0

      # Rule 1: Start with 10 defections
      if len(self.history) < 10:
          return axl.Action.D

      # Rule 3: Every 100 rounds, test cooperation
      if len(self.history) % 100 == 0:
          self.cycle_position = 0
          return axl.Action.C
      if len(self.history) % 100 == 1 and opponent.history[-1] == axl.Action.C:
          return axl.Action.D

      # Calculate opponent's cooperation rate
      last_50_moves = opponent.history[-50:]
      coop_rate = sum([a == axl.Action.C for a in last_50_moves]) / 50

      # Rule 4: Track score difference
      score_diff = self.score - opponent.score
      if score_diff < -20:
          self.score_deficit_counter = 10
      elif -20 <= score_diff < -10:
          self.score_deficit_counter = 1

      if self.score_deficit_counter > 0:
          self.score_deficit_counter -= 1
          return axl.Action.D

      # Rule 5: Forgiveness mechanism
      if self.d_streak >= 20:
          self.d_streak = 0
          self.cycle_position = 0
          return axl.Action.C

      # Rule 6: Last 50 rounds strategy
      if len(self.history) > 950:
          overall_coop_rate = opponent.cooperations / len(opponent.history)
          if overall_coop_rate > 0.7:
              return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D
          else:
              return axl.Action.D

      # Rule 2: Main strategy based on cooperation rate
      if coop_rate > 0.8:
          cycle = [axl.Action.C, axl.Action.D, axl.Action.D]
      elif 0.6 < coop_rate <= 0.8:
          cycle = [axl.Action.C, axl.Action.D, axl.Action.D, axl.Action.D]
      elif 0.4 < coop_rate <= 0.6:
          cycle = [axl.Action.D, axl.Action.D, axl.Action.D, axl.Action.D, axl.Action.C]
      else:
          cycle = [axl.Action.D, axl.Action.D, axl.Action.D, axl.Action.D, axl.Action.D]

      action = cycle[self.cycle_position % len(cycle)]
      self.cycle_position = (self.cycle_position + 1) % len(cycle)

      # Rule 7: Limit consecutive C moves
      if action == axl.Action.C:
          self.c_streak += 1
          self.d_streak = 0
          if self.c_streak > 2:
              action = axl.Action.D
              self.c_streak = 0
      else:
          self.d_streak += 1
          self.c_streak = 0

      return action

# Here's a revised aggressive strategy, taking into account the feedback:  1.
# Start the game by defecting (D) for the first 5 rounds to establish an
# aggressive stance.  2. For the main part of the game (rounds 6-900), use the
# following rules:     a. Defect (D) with a base probability of 75%.        b.
# If the opponent has cooperated (C) in 2 or more of their last 3 moves:       -
# Increase the probability of defection to 90% for the next 5 rounds to exploit
# their cooperation.        c. If the opponent has defected (D) in all of their
# last 3 moves:       - Decrease the probability of defection to 60% for the
# next 5 rounds to avoid mutual destruction.        d. Every 50 rounds (i.e.,
# rounds 50, 100, 150, etc.):       - Defect (D) for 3 consecutive rounds to
# reassert dominance.  3. For the endgame (rounds 901-1000):        a. From
# rounds 901-980:       - Increase the base probability of defection to 85%.
# b. For the final 20 rounds (981-1000):       - Further increase the
# probability of defection to 95%.  4. Throughout the game, if the opponent has
# played the same move (either C or D) for 5 consecutive rounds:    - Play the
# opposite move for 1 round, then return to the main strategy.  This strategy
# maintains an aggressive approach while incorporating elements of adaptability
# and unpredictability. It clearly defines when to cooperate or defect based on
# probabilities and the opponent's recent behavior. The strategy is simpler than
# the original, making it easier to implement and understand, while still being
# robust against various opponent behaviors.  Key aspects of this strategy: - It
# starts aggressively and maintains a high probability of defection throughout
# the game. - It adapts to the opponent's recent moves, exploiting cooperation
# and mitigating mutual destruction. - It includes periodic reassertion of
# dominance. - It becomes more aggressive in the endgame but not to the point of
# being fully predictable. - It has a mechanism to break out of potential loops
# or exploit highly repetitive opponent strategies.  This revised strategy
# should be more robust against a variety of opponent behaviors while
# maintaining its aggressive nature.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.defect_prob = 0.75
          self.consecutive_same_move = 0
          self.last_opponent_move = None
          self.reassert_dominance_counter = 0
          self.exploit_cooperate_counter = 0
          self.avoid_mutual_destruction_counter = 0
          self.break_loop_next_round = False

      round_number = len(self.history) + 1

      if round_number <= 5:
          return axl.Action.D

      if round_number > 900:
          self.defect_prob = 0.85 if round_number <= 980 else 0.95

      if round_number > 50 and (round_number - 50) % 50 == 0:
          self.reassert_dominance_counter = 3

      if self.reassert_dominance_counter > 0:
          self.reassert_dominance_counter -= 1
          return axl.Action.D

      if self.break_loop_next_round:
          self.break_loop_next_round = False
          return axl.Action.C if self.last_opponent_move == axl.Action.D else axl.Action.D

      opponent_last_3 = opponent.history[-3:]
      if len(opponent_last_3) == 3:
          if sum([a == axl.Action.C for a in opponent_last_3]) >= 2:
              self.exploit_cooperate_counter = 5
              self.defect_prob = 0.90
          elif all([a == axl.Action.D for a in opponent_last_3]):
              self.avoid_mutual_destruction_counter = 5
              self.defect_prob = 0.60

      if self.exploit_cooperate_counter > 0:
          self.exploit_cooperate_counter -= 1
      elif self.avoid_mutual_destruction_counter > 0:
          self.avoid_mutual_destruction_counter -= 1
      else:
          self.defect_prob = 0.75

      if opponent.history:
          if opponent.history[-1] == self.last_opponent_move:
              self.consecutive_same_move += 1
          else:
              self.consecutive_same_move = 1
          self.last_opponent_move = opponent.history[-1]

      if self.consecutive_same_move >= 5:
          self.consecutive_same_move = 0
          self.break_loop_next_round = True

      return axl.Action.D if self._random.random() < self.defect_prob else axl.Action.C

# Here's a revised aggressive strategy, incorporating the feedback:  1. Start by
# playing D (defect) for the first 5 rounds to establish an initial aggressive
# stance.  2. Use a sliding window of the last 20 rounds to analyze opponent
# behavior:    - If the opponent played C more than 60% of the time, play D.
# - If the opponent played D more than 60% of the time, play C with a 20%
# probability and D with an 80% probability.    - If the opponent's play is
# mixed (between 40-60% C or D), mirror their last move (tit-for-tat) for the
# next round.  3. Every 50 rounds, regardless of the opponent's recent moves,
# play C for 2 consecutive rounds to probe for cooperation. If the opponent
# cooperates in both rounds, play D for the next 5 rounds to exploit this
# cooperation.  4. Implement a "forgiveness" mechanism: If there have been 10
# consecutive rounds of mutual defection, play C for one round to attempt
# breaking the cycle.  5. Consider the cumulative score difference:    - If
# behind by more than 20 points, increase the probability of playing D by 10% in
# step 2.    - If ahead by more than 50 points, decrease the probability of
# playing D by 10% in step 2.  6. In the last 100 rounds, adjust the strategy
# based on the overall game situation:    - If behind in total score, play D
# with 90% probability and C with 10% probability.    - If ahead in total score,
# continue with the strategy from steps 2-5.  7. For the final 10 rounds, always
# play D to maximize potential gains.  8. Throughout the game, maintain a count
# of the opponent's total C and D moves. If at any point the opponent has played
# C more than 70% of the total game rounds, switch to always playing D for the
# next 20 rounds to exploit their apparent cooperativeness.  This revised
# strategy maintains an aggressive approach while being more adaptive and
# responsive to the opponent's behavior. It clearly defines conditions for
# cooperation and defection, considers the cumulative score, and includes
# mechanisms to probe for cooperation and break out of defection cycles. The
# strategy remains relatively simple while being more robust against a variety
# of opponent behaviors.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_mutual_defections = 0
          self.probe_counter = 0
          self.exploit_counter = 0
          self.always_defect_counter = 0

      if len(self.history) < 5:
          return axl.Action.D

      if self.always_defect_counter > 0:
          self.always_defect_counter -= 1
          return axl.Action.D

      if len(self.history) >= 990:
          return axl.Action.D

      if len(self.history) >= 900:
          if self.score < opponent.score:
              return axl.Action.D if self._random.random() < 0.9 else axl.Action.C

      window = min(20, len(self.history))
      opponent_c_ratio = opponent.history[-window:].count(axl.Action.C) / window

      score_diff = self.score - opponent.score
      d_prob_adjustment = 0.1 if score_diff < -20 else -0.1 if score_diff > 50 else 0

      if self.probe_counter > 0:
          self.probe_counter -= 1
          return axl.Action.C
      if self.exploit_counter > 0:
          self.exploit_counter -= 1
          return axl.Action.D
      if len(self.history) % 50 == 0:
          self.probe_counter = 2
          return axl.Action.C
      if opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          self.exploit_counter = 5
          return axl.Action.D

      if opponent.history.cooperations / len(self.history) > 0.7:
          self.always_defect_counter = 20
          return axl.Action.D

      if opponent_c_ratio > 0.6:
          return axl.Action.D
      elif opponent_c_ratio < 0.4:
          return axl.Action.D if self._random.random() < (0.8 + d_prob_adjustment) else axl.Action.C
      else:
          if self.history[-1] == opponent.history[-1] == axl.Action.D:
              self.consecutive_mutual_defections += 1
          else:
              self.consecutive_mutual_defections = 0

          if self.consecutive_mutual_defections >= 10:
              self.consecutive_mutual_defections = 0
              return axl.Action.C

          return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. For each subsequent round:
# a) Calculate two key metrics based on the opponent's recent behavior:       -
# Short-term defection rate (SDR): Proportion of Defect (D) plays in the last 20
# rounds       - Long-term defection rate (LDR): Proportion of D plays in all
# previous rounds     b) Determine the base cooperation probability (BCP):
# - If SDR ≤ 0.3 (opponent mostly cooperates), BCP = 1 (always cooperate)
# - If 0.3 < SDR ≤ 0.6, BCP = 1 - SDR       - If SDR > 0.6 (opponent mostly
# defects), BCP = 0.2     c) Adjust the BCP based on the long-term behavior:
# - If LDR > 0.6, reduce BCP by 0.1       - Final Cooperation Probability (FCP)
# = max(BCP - 0.1, 0.1) if LDR > 0.6, otherwise FCP = BCP     d) Make the play
# decision:       - With 5% probability, play C regardless of other factors
# (random cooperation)       - Otherwise:         - If the opponent's last move
# was C, play C         - If the opponent's last move was D, play C with
# probability FCP, and D with probability (1 - FCP)  3. Repeat step 2 for each
# round until the game ends.  This strategy: - Starts cooperatively - Responds
# proportionally to the opponent's recent behavior - Considers long-term
# behavior for persistently aggressive opponents - Maintains a base level of
# cooperation even against highly aggressive strategies - Includes an element of
# unpredictability with the 5% random cooperation  Cooperation conditions: -
# Always cooperate if the opponent has been mostly cooperative recently (SDR ≤
# 0.3) - High chance of cooperation if the opponent cooperated in the last round
# - 5% chance of cooperation in any round, regardless of other factors
# Defection conditions: - Increased chance of defection as the opponent's short-
# term defection rate increases - Higher chance of defection if the opponent has
# been persistently aggressive over the long term - Highest chance of defection
# when the opponent defected in the last round and has been highly aggressive
# recently (SDR > 0.6)  This strategy aims to be cooperative, adaptive, and
# robust against various opponent behaviors while remaining relatively simple to
# implement.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      if self._random.random() < 0.05:
          return axl.Action.C

      recent_history_length = min(20, len(opponent.history))
      recent_defections = sum([a == axl.Action.D for a in opponent.history[-recent_history_length:]])
      sdr = recent_defections / recent_history_length if recent_history_length > 0 else 0
      ldr = opponent.defections / len(opponent.history) if opponent.history else 0

      if sdr <= 0.3:
          bcp = 1
      elif 0.3 < sdr <= 0.6:
          bcp = 1 - sdr
      else:
          bcp = 0.2

      fcp = max(bcp - 0.1, 0.1) if ldr > 0.6 else bcp

      if not opponent.history or opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.C if self._random.random() < fcp else axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. For subsequent rounds, follow
# these rules in order:     a. If it's one of the last 100 rounds:       -
# Calculate P = (current round - 900) / 100       - With probability P, play
# whatever the opponent played in the previous round       - With probability
# (1-P), continue with the rules below     b. If a clear alternating pattern
# (CDCDCD or DCDCDC) is detected in the opponent's last 6 moves:       - Play
# Defect (D) for the next 5 rounds       - After these 5 rounds, return to step
# 2a     c. If the opponent has played D more than 50% of the time in the last
# 20 rounds:       - Play whatever the opponent played in the previous round
# (Tit-for-Tat)       - Continue this until the opponent's defection rate drops
# below 30% in the last 20 rounds       - Then return to step 2a     d. With a
# 2% chance:       - Play C regardless of any other conditions     e. If none of
# the above conditions are met, use this "Tit-for-Two-Tats" approach:       - If
# the opponent has played D in both of the last two rounds, play D       -
# Otherwise, play C  This strategy maintains a cooperative approach while being
# more robust against various opponent behaviors. It clearly specifies when to
# cooperate or defect based on the opponent's actions and the game's
# progression. The strategy is simpler than the previous version while
# incorporating mechanisms to handle different scenarios effectively.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.alternating_counter = 0
          self.tit_for_tat_mode = False
          return axl.Action.C

      if len(self.history) > 900:
          P = (len(self.history) - 900) / 100
          if self._random.random() < P:
              return opponent.history[-1]

      if self.alternating_counter > 0:
          self.alternating_counter -= 1
          return axl.Action.D

      last_6_moves = opponent.history[-6:]
      if len(last_6_moves) == 6 and (last_6_moves == [axl.Action.C, axl.Action.D] * 3 or
                                     last_6_moves == [axl.Action.D, axl.Action.C] * 3):
          self.alternating_counter = 5
          return axl.Action.D

      last_20_moves = opponent.history[-20:]
      if len(last_20_moves) == 20:
          defection_rate = sum([a == axl.Action.D for a in last_20_moves]) / 20
          if defection_rate > 0.5:
              self.tit_for_tat_mode = True
          elif defection_rate <= 0.3:
              self.tit_for_tat_mode = False

          if self.tit_for_tat_mode:
              return opponent.history[-1]

      if self._random.random() < 0.02:
          return axl.Action.C

      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D

      return axl.Action.C

# Here's the revised strategy, taking into account the feedback:  1. Start by
# cooperating (C) in the first round.  2. For each subsequent round, follow
# these rules in order:     a. If it's the final round (round 1000), play C.
# b. With a 5% chance, play a random move (C or D with equal probability).
# c. If in the last 30 rounds, the opponent has defected more than 60% of the
# time (i.e., 19 or more defections), play whatever the opponent played in the
# previous round (Tit-for-Tat).     d. If the current round number is a multiple
# of 10, or a multiple of 8 for rounds 501-999, play C (forgiveness round).
# e. Otherwise, play whatever the opponent played in the previous round (Tit-
# for-Tat).  This strategy will cooperate (C) when: - It's the first round -
# It's the final round - It's a forgiveness round (every 10 rounds, or every 8
# rounds in the latter half of the game) - The opponent cooperated in the
# previous round (unless overridden by the random move)  This strategy will
# defect (D) when: - The opponent defected in the previous round, and it's not a
# forgiveness round or the final round (unless overridden by the random move)
# The random move adds a 5% chance to play either C or D regardless of other
# conditions, except for the final round.  This revised strategy maintains a
# cooperative approach while being simpler and more robust. It adapts quickly to
# aggressive opponents, includes some unpredictability, and avoids exploitable
# end-game behavior while still ending on a cooperative note.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      if len(self.history) == 999:
          return axl.Action.C

      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])

      last_30_opponent_defections = sum([a == axl.Action.D for a in opponent.history[-30:]])
      if len(opponent.history) >= 30 and last_30_opponent_defections > 18:
          return opponent.history[-1]

      current_round = len(self.history) + 1
      if current_round % 10 == 0 or (current_round >= 501 and current_round <= 999 and current_round % 8 == 0):
          return axl.Action.C

      return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) on the first move.  2. For subsequent moves, use an
# adaptive Generous Tit-for-Tat approach:     a. Calculate the opponent's
# cooperation rate over the last 20 moves.    b. Set the forgiveness rate:
# - If cooperation rate > 60%: forgiveness rate = 30%       - If cooperation
# rate < 40%: forgiveness rate = 10%       - Otherwise: forgiveness rate = 20%
# c. Determine your move:       - If the opponent played C in the previous
# round, play C.       - If the opponent played D in the previous round:
# - With probability equal to the forgiveness rate, play C.         - Otherwise,
# play D.  3. Every 50 rounds, play C regardless of the opponent's previous
# move.  4. Pattern recognition: If you detect a simple alternating pattern
# (CDCDCD or DCDCDC) over the last 6 moves, play the move that would beat this
# pattern in the next round.  5. For the last 10 rounds:    - Calculate the
# opponent's overall cooperation rate for the entire game.    - If this rate is
# below 40%, switch to pure Tit-for-Tat (play what the opponent played in the
# previous round).    - If the rate is 40% or above, continue with the adaptive
# Generous Tit-for-Tat approach.  In summary:  - Always cooperate (C) when:   *
# It's the first move of the game.   * It's a multiple of 50 rounds (the "olive
# branch" move).   * The opponent cooperated in the previous round.  - Possibly
# cooperate (C) when:   * The opponent defected, but you "forgive" based on the
# calculated forgiveness rate.  - Defect (D) when:   * The opponent defected and
# you don't "forgive" based on the forgiveness rate.   * You've detected an
# alternating pattern and defecting would be the winning move.   * In the last
# 10 rounds, if the opponent's overall cooperation rate is below 40% and they
# defected in the previous round.  This strategy maintains a cooperative
# approach while adapting to the opponent's behavior. It's simpler than the
# original proposal but still includes mechanisms to encourage cooperation and
# protect against persistent defection.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.forgiveness_rate = 0.2
          return axl.Action.C

      if len(self.history) % 50 == 0:
          return axl.Action.C

      if len(self.history) >= 20:
          recent_coop_rate = 1 - sum([a == axl.Action.D for a in opponent.history[-20:]]) / 20
          if recent_coop_rate > 0.6:
              self.forgiveness_rate = 0.3
          elif recent_coop_rate < 0.4:
              self.forgiveness_rate = 0.1
          else:
              self.forgiveness_rate = 0.2

      if len(self.history) >= 6:
          last_six = opponent.history[-6:]
          if last_six == [axl.Action.C, axl.Action.D] * 3 or last_six == [axl.Action.D, axl.Action.C] * 3:
              return axl.Action.D if last_six[-1] == axl.Action.C else axl.Action.C

      if len(self.history) >= 990:
          overall_coop_rate = opponent.cooperations / len(opponent.history)
          if overall_coop_rate < 0.4:
              return opponent.history[-1]

      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.C if self._random.random() < self.forgiveness_rate else axl.Action.D

# Here's a revised strategy incorporating the feedback:  1. Start by playing C
# (cooperate) for the first round.  2. For subsequent rounds, use the following
# rules:     a) Cooperate if:       - The opponent cooperated in the last round
# - The opponent defected only once in the last three rounds       - It's been
# 30 rounds since your last cooperation attempt and the opponent's cooperation
# rate is above 30%     b) Defect if:       - The opponent defected twice or
# more in the last three rounds       - The opponent's overall cooperation rate
# falls below 30% (calculated every 10 rounds)  3. Adaptive Forgiveness:    - If
# the opponent's cooperation rate is above 70%, forgive up to two consecutive
# defections    - If the opponent's cooperation rate is between 30% and 70%,
# forgive one defection    - If the opponent's cooperation rate is below 30%,
# don't forgive any defections  4. Pattern Recognition:    - If the opponent has
# played the same move for 5 consecutive rounds, match their move for the next
# round  5. Gradual Defense Escalation:    - If the opponent's cooperation rate
# drops below 30%, increase your defection rate by 10% every 5 rounds until
# their cooperation improves or your defection rate reaches 70%  6. End-game
# Adjustment (last 10 rounds):    - If the opponent's cooperation rate in the
# last 50 rounds is above 70%, continue cooperating    - Otherwise, match the
# opponent's cooperation rate from the last 50 rounds  7. Simple Learning:    -
# Every 100 rounds, compare your score with a hypothetical "always cooperate"
# score against this opponent    - If your score is lower, increase your
# cooperation rate by 10% for the next 100 rounds    - If your score is higher,
# maintain your current strategy  This revised strategy maintains a cooperative
# approach while being more adaptive to the opponent's behavior. It's clearer
# about when to cooperate or defect, includes a simple learning mechanism, and
# has more nuanced responses to different opponent behaviors. The strategy
# remains relatively simple while addressing the main weaknesses identified in
# the critique.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.cooperation_rate = 1.0
          self.last_cooperation_attempt = 0
          self.defection_rate = 0.0
          self.last_score_check = 0
          return axl.Action.C

      opponent_coop_rate = opponent.cooperations / len(opponent.history)
      rounds_played = len(self.history)

      # Pattern Recognition
      if len(opponent.history) >= 5 and len(set(opponent.history[-5:])) == 1:
          return opponent.history[-1]

      # Adaptive Forgiveness
      if opponent_coop_rate > 0.7:
          forgiveness_threshold = 2
      elif opponent_coop_rate > 0.3:
          forgiveness_threshold = 1
      else:
          forgiveness_threshold = 0

      # Cooperation conditions
      if (opponent.history[-1] == axl.Action.C or
          sum([a == axl.Action.D for a in opponent.history[-3:]]) == 1 or
          (rounds_played - self.last_cooperation_attempt >= 30 and opponent_coop_rate > 0.3)):
          self.last_cooperation_attempt = rounds_played
          return axl.Action.C

      # Defection conditions
      if (sum([a == axl.Action.D for a in opponent.history[-3:]]) >= 2 or
          (rounds_played % 10 == 0 and opponent_coop_rate < 0.3)):
          return axl.Action.D

      # Gradual Defense Escalation
      if opponent_coop_rate < 0.3 and rounds_played % 5 == 0:
          self.defection_rate = min(0.7, self.defection_rate + 0.1)
      elif opponent_coop_rate >= 0.3:
          self.defection_rate = max(0, self.defection_rate - 0.1)

      # End-game Adjustment
      if rounds_played >= 991:
          recent_opponent_coop_rate = sum([a == axl.Action.C for a in opponent.history[-50:]]) / 50
          if recent_opponent_coop_rate > 0.7:
              return axl.Action.C
          else:
              return axl.Action.C if self._random.random() < recent_opponent_coop_rate else axl.Action.D

      # Simple Learning
      if rounds_played % 100 == 0 and rounds_played > 0:
          current_score = self.score
          always_coop_score = sum([3 if a == axl.Action.C else 0 for a in opponent.history])
          if current_score < always_coop_score:
              self.cooperation_rate = min(1.0, self.cooperation_rate + 0.1)
          # If score is higher, maintain current strategy (no change needed)

      # Final decision based on cooperation and defection rates
      if self._random.random() < max(self.cooperation_rate, 1 - self.defection_rate):
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a revised strategy incorporating the feedback:  1. Start by playing
# Cooperate (C) for the first 5 rounds.  2. For the main part of the game
# (rounds 6-980):     a) Keep track of your opponent's cooperation rate over the
# last 100 moves (or all previous moves if fewer than 100).     b) If the
# opponent's cooperation rate is 80% or higher:       - Play Cooperate (C)
# c) If the opponent's cooperation rate is between 50% and 80%:       - Use Tit-
# for-Two-Tats:         - Cooperate (C) unless the opponent has defected in both
# of the last two rounds         - If the opponent has defected in both of the
# last two rounds, play Defect (D) once, then return to Cooperate (C)     d) If
# the opponent's cooperation rate is below 50%:       - Use Tit-for-Tat:
# - Play whatever the opponent played in the previous round     e) Pattern
# recognition:       - If you detect an alternating Cooperate-Defect pattern
# over the last 6 moves, switch to Tit-for-Tat for the next 10 moves, then
# return to the main strategy     f) Periodic cooperation:       - Every 40-60
# rounds (randomly determined), play Cooperate (C) regardless of the opponent's
# previous move  3. For the final phase (rounds 981-1000):     a) If the
# opponent's cooperation rate over the last 100 moves is 70% or higher:       -
# Continue with the main strategy     b) If the opponent's cooperation rate over
# the last 100 moves is below 70%:       - Switch to Tit-for-Tat for the
# remaining moves  This strategy maintains a cooperative approach while being
# more robust against various opponent behaviors. It's adaptive based on the
# opponent's overall cooperation rate, has mechanisms to detect and respond to
# specific patterns, and includes a degree of randomness to avoid exploitation.
# The strategy also differentiates between the main game and the endgame,
# adjusting accordingly.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.cooperation_rate = []
          self.pattern_detection_count = 0
          self.periodic_cooperation_counter = self._random.randint(40, 60)
          self.just_defected = False

      if len(self.history) < 5:
          return axl.Action.C

      # Periodic cooperation
      self.periodic_cooperation_counter -= 1
      if self.periodic_cooperation_counter == 0:
          self.periodic_cooperation_counter = self._random.randint(40, 60)
          return axl.Action.C

      # Update cooperation rate
      if len(opponent.history) > 100:
          self.cooperation_rate.append(sum([a == axl.Action.C for a in opponent.history[-100:]]) / 100)
      else:
          self.cooperation_rate.append(sum([a == axl.Action.C for a in opponent.history]) / len(opponent.history))

      # Endgame strategy (rounds 981-1000)
      if len(self.history) >= 980:
          opponent_coop_rate = sum([a == axl.Action.C for a in opponent.history[-min(100, len(opponent.history)):]])
          opponent_coop_rate /= min(100, len(opponent.history))
          if opponent_coop_rate < 0.7:
              return opponent.history[-1]  # Tit-for-Tat

      # Pattern recognition
      if len(self.history) >= 6:
          pattern = [opponent.history[-i] for i in range(1, 7)]
          if pattern == [axl.Action.C, axl.Action.D] * 3:
              self.pattern_detection_count = 10
      if self.pattern_detection_count > 0:
          self.pattern_detection_count -= 1
          return opponent.history[-1]  # Tit-for-Tat

      # Main strategy based on cooperation rate
      if self.cooperation_rate[-1] >= 0.8:
          return axl.Action.C
      elif 0.5 <= self.cooperation_rate[-1] < 0.8:
          if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              if not self.just_defected:
                  self.just_defected = True
                  return axl.Action.D
          self.just_defected = False
          return axl.Action.C
      else:
          return opponent.history[-1]  # Tit-for-Tat

# Here's a revised strategy that incorporates the feedback and clearly states
# the conditions for cooperation and defection:  1. For the first 10 rounds:
# - Play C on odd-numbered rounds and D on even-numbered rounds.  2. For rounds
# 11 to 950:    - Maintain a sliding window of the last 20 rounds to calculate
# the opponent's cooperation rate.    - Calculate the current score difference
# (your score minus opponent's score).    - Determine your base cooperation
# probability (BCP) as follows:      - If the opponent's cooperation rate is
# above 60%: BCP = 0.7      - If the opponent's cooperation rate is between 40%
# and 60%: BCP = 0.5      - If the opponent's cooperation rate is below 40%: BCP
# = 0.3    - Adjust the cooperation probability (CP) based on the score
# difference:      CP = BCP + (score difference / 1000)      - Ensure CP is
# between 0 and 1 (if CP < 0, set CP = 0; if CP > 1, set CP = 1)    - Cooperate
# (play C) if a random number between 0 and 1 is less than CP; otherwise, defect
# (play D).  3. Every 100 rounds (i.e., rounds 100, 200, 300, etc.):    - Play a
# random move (C or D with 50% probability each), regardless of the calculated
# CP.  4. For the last 50 rounds (951-1000):    - Start with the CP calculated
# as in step 2.    - Decrease CP by 0.02 each round (ensuring it doesn't go
# below 0).    - Cooperate if a random number between 0 and 1 is less than the
# adjusted CP; otherwise, defect.  This strategy: - Starts with a neutral
# alternating pattern. - Adapts to the opponent's recent behavior using a
# sliding window. - Considers the overall game progress by factoring in the
# score difference. - Maintains a neutral stance by centering cooperation
# probabilities around 0.5 for mixed opponent strategies. - Introduces
# occasional randomness to avoid being predictable. - Gradually becomes more
# cautious in the endgame to protect against late defection.  The strategy will
# cooperate more often when: - The opponent has been cooperative recently (high
# cooperation rate). - You are leading in score (positive score difference).
# The strategy will defect more often when: - The opponent has been
# uncooperative recently (low cooperation rate). - You are behind in score
# (negative score difference). - The game is nearing its end (last 50 rounds).
# This approach maintains a neutral overall stance while being adaptive to the
# opponent's behavior and the game's progress.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.window_size = 20
          self.cp = 0.5

      round_number = len(self.history) + 1

      if round_number <= 10:
          return axl.Action.C if round_number % 2 == 1 else axl.Action.D

      if round_number <= 950:
          if round_number % 100 == 0:
              return axl.Action.C if self._random.random() < 0.5 else axl.Action.D

          recent_history = opponent.history[-self.window_size:]
          opponent_coop_rate = sum([a == axl.Action.C for a in recent_history]) / self.window_size

          recent_scores = self.total_scores(self.history[-self.window_size:], opponent.history[-self.window_size:])
          score_diff = recent_scores[0] - recent_scores[1]

          if opponent_coop_rate > 0.6:
              bcp = 0.7
          elif opponent_coop_rate > 0.4:
              bcp = 0.5
          else:
              bcp = 0.3

          self.cp = max(0, min(1, bcp + (score_diff / 1000)))

      else:
          self.cp = max(0, self.cp - 0.02)

      return axl.Action.C if self._random.random() < self.cp else axl.Action.D

# Here's a revised strategy that takes into account the feedback, with clear
# conditions for cooperation and defection:  1. Start by playing C (Cooperate)
# in the first round.  2. For the next 9 rounds, mirror your opponent's previous
# move.  3. After every 10 rounds, analyze the opponent's behavior:    - If
# they've played C 6 or more times out of 10, play C in the next round.    - If
# they've played D 6 or more times out of 10, play D in the next round.    - If
# their play is mixed (5C and 5D), continue mirroring.  4. Implement a pattern
# recognition system:    - If you detect an alternating C/D pattern for 6 or
# more rounds, play D for the next 2 rounds, then resume mirroring.  5. Every 50
# rounds, reassess your overall strategy:    - If your average score per round
# is below 2, increase your tendency to play D by playing D for two rounds after
# each time your opponent plays D.    - If your average score per round is above
# 2.5, increase your tendency to play C by playing C for an extra round after
# each time your opponent plays C.  6. Forgiveness mechanism:    - After playing
# D twice in a row, play C in the next round to offer an opportunity for
# cooperation.  7. For the last 100 rounds of the game:    - If your overall
# score is lower than your opponent's, gradually increase the frequency of D
# plays. Start by playing D every 3rd round, then every 2nd round for the last
# 50 rounds.    - If your overall score is higher or equal, continue with the
# established strategy.  Conditions for Cooperation (C): - In the first round -
# When mirroring a C play from the opponent - When the opponent has played C 6
# or more times in the last 10 rounds - As part of the forgiveness mechanism,
# after playing D twice in a row - When your average score is above 2.5, play an
# extra C after each opponent's C  Conditions for Defection (D): - When
# mirroring a D play from the opponent - When the opponent has played D 6 or
# more times in the last 10 rounds - When an alternating C/D pattern is
# detected, for 2 rounds - When your average score is below 2, play D for two
# rounds after each opponent's D - In the endgame when behind, every 3rd round,
# then every 2nd round  This revised strategy maintains a neutral approach by
# adapting to the opponent's behavior, incorporates pattern recognition,
# includes a forgiveness mechanism, and has a more nuanced endgame strategy.
# It's simpler than the previous version while still being responsive to various
# scenarios.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.pattern_count = 0
          self.extra_d_count = 0
          self.extra_c_count = 0
          return axl.Action.C

      # First 10 rounds: mirror opponent
      if len(self.history) < 10:
          return opponent.history[-1]

      # Every 10 rounds: analyze opponent's behavior
      if len(self.history) % 10 == 0:
          last_ten = opponent.history[-10:]
          c_count = sum(a == axl.Action.C for a in last_ten)
          if c_count >= 6:
              return axl.Action.C
          elif c_count <= 4:
              return axl.Action.D
          # If 5C and 5D, continue with regular strategy (mirroring)

      # Pattern recognition
      if len(self.history) >= 6:
          last_six = opponent.history[-6:]
          if last_six == [axl.Action.C, axl.Action.D] * 3:
              self.pattern_count = 2
          if self.pattern_count > 0:
              self.pattern_count -= 1
              return axl.Action.D

      # Every 50 rounds: reassess strategy
      if len(self.history) % 50 == 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.extra_d_count = 2
          elif avg_score > 2.5:
              self.extra_c_count += 1

      # Implement extra D tendency
      if self.extra_d_count > 0 and opponent.history[-1] == axl.Action.D:
          self.extra_d_count -= 1
          return axl.Action.D

      # Implement extra C tendency
      if self.extra_c_count > 0 and opponent.history[-1] == axl.Action.C:
          self.extra_c_count -= 1
          return axl.Action.C

      # Forgiveness mechanism
      if self.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.C

      # Endgame strategy
      if len(self.history) > 900:
          if self.score < opponent.score:
              if len(self.history) > 950:
                  return axl.Action.D if len(self.history) % 2 == 0 else opponent.history[-1]
              else:
                  return axl.Action.D if len(self.history) % 3 == 0 else opponent.history[-1]

      # Default: mirror opponent's last move
      return opponent.history[-1]

# Here's a revised strategy that incorporates the feedback and clearly states
# the conditions for cooperation and defection:  1. Start by playing C
# (cooperate) in the first round.  2. For each subsequent round, follow these
# steps:     a. Calculate the opponent's cooperation ratio for the entire game.
# b. Determine your move based on the following conditions:           - If the
# opponent's cooperation ratio is above 0.6:         * Play C with 90%
# probability         * Play D with 10% probability           - If the
# opponent's cooperation ratio is below 0.4:         * Play D with 90%
# probability         * Play C with 10% probability           - If the
# opponent's cooperation ratio is between 0.4 and 0.6:         * Mirror the
# opponent's last move with 90% probability         * Play the opposite of the
# opponent's last move with 10% probability     c. Override the above decision
# if:       - There have been 5 or more consecutive rounds of mutual defection:
# * Play C with 20% probability (forgiveness mechanism)         * Otherwise,
# stick with the decision from step b  3. For the last 20 rounds of the game:
# - If the opponent's overall cooperation ratio is above 0.5, play C    - If the
# opponent's overall cooperation ratio is 0.5 or below, play D  This strategy
# maintains a neutral approach by adapting to the opponent's behavior over the
# course of the game. It uses the opponent's cooperation ratio as the primary
# factor in decision-making, which allows for long-term memory and adaptation.
# The strategy incorporates elements of randomness to prevent easy exploitation
# and includes a forgiveness mechanism to break out of prolonged mutual
# defection cycles.  The conditions for cooperation (C) and defection (D) are
# clearly defined based on the opponent's cooperation ratio, with additional
# randomness and special cases for consecutive defections and end-game behavior.
# This approach should be more robust against various opponent strategies while
# remaining relatively simple to implement and understand.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_mutual_defections = 0
          return axl.Action.C

      opponent_coop_ratio = opponent.cooperations / len(opponent.history)

      if len(self.history) >= 980:  # Last 20 rounds
          return axl.Action.C if opponent_coop_ratio > 0.5 else axl.Action.D

      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_mutual_defections += 1
      else:
          self.consecutive_mutual_defections = 0

      if self.consecutive_mutual_defections >= 5 and self._random.random() < 0.2:
          return axl.Action.C

      if opponent_coop_ratio > 0.6:
          return axl.Action.C if self._random.random() < 0.9 else axl.Action.D
      elif opponent_coop_ratio < 0.4:
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
      else:
          if self._random.random() < 0.9:
              return opponent.history[-1]
          else:
              return axl.Action.C if opponent.history[-1] == axl.Action.D else axl.Action.D

# Here's a revised strategy that incorporates the feedback and clearly states
# the conditions for cooperation and defection:  1. Start by cooperating (C) in
# the first round.  2. Initialize a cooperation probability (CP) at 50%.  3. For
# each subsequent round, from round 2 to 1000:     a. Generate a random number
# (RN) between 0 and 100.        b. If RN is less than or equal to CP, cooperate
# (C). Otherwise, defect (D).        c. After observing the opponent's move:
# - If the opponent cooperated, increase CP by 2 percentage points, up to a
# maximum of 90%.       - If the opponent defected, decrease CP by 2 percentage
# points, down to a minimum of 10%.  4. Every 10 rounds (i.e., on rounds 10, 20,
# 30, ..., 990):        a. Calculate the opponent's cooperation rate (OCR) over
# the last 50 rounds (or all previous rounds if fewer than 50).        b. Adjust
# CP based on OCR:       - If OCR > 60%, increase CP by 5 percentage points, up
# to a maximum of 90%.       - If OCR < 40%, decrease CP by 5 percentage points,
# down to a minimum of 10%.       - If 40% ≤ OCR ≤ 60%, do not change CP.  This
# strategy is neutral, simple, and adaptive. It clearly defines when to
# cooperate or defect based on the calculated cooperation probability. The
# strategy maintains a balance between responding to immediate opponent actions
# and adapting to their overall behavior over time.  Key features: 1. It starts
# cooperatively but quickly adapts to the opponent's strategy. 2. It uses a
# single, adjustable parameter (CP) to determine actions. 3. It responds to both
# short-term (last move) and medium-term (last 50 moves) opponent behavior. 4.
# It avoids extreme behavior by capping CP between 10% and 90%. 5. It maintains
# consistent behavior throughout the game, avoiding end-game exploitation.  This
# strategy should be robust against various opponent behaviors while remaining
# neutral and adaptive. It's simple to implement and understand, reducing the
# chance of execution errors.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.cp = 50  # Initialize cooperation probability
          return axl.Action.C  # Start by cooperating

      # Adjust CP based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          self.cp = min(90, self.cp + 2)
      else:
          self.cp = max(10, self.cp - 2)

      # Every 10 rounds starting from round 10
      if len(self.history) >= 10 and len(self.history) % 10 == 9:
          last_50_rounds = min(50, len(self.history))
          ocr = opponent.history[-last_50_rounds:].count(axl.Action.C) / last_50_rounds
          if ocr > 0.6:
              self.cp = min(90, self.cp + 5)
          elif ocr < 0.4:
              self.cp = max(10, self.cp - 5)

      return axl.Action.C if self._random.random() <= self.cp / 100 else axl.Action.D

# Here's a revised strategy that incorporates the feedback and clearly states
# the conditions for cooperation and defection:  1. Start by playing C
# (cooperate) in the first round.  2. For each subsequent round:     a.
# Calculate the opponent's cooperation rate over the last 20 moves (or all
# previous moves if fewer than 20).        b. Set your base cooperation
# probability equal to the opponent's cooperation rate.        c. Adjust this
# probability based on the current round number:       - If it's within the last
# 100 rounds, decrease the probability by 0.2% for each round remaining (max 20%
# decrease).        d. Add a random adjustment of ±5% to this probability.  3.
# Determine your move for this round:     - If the opponent has defected for the
# last 3 consecutive rounds:      * Play D (defect) with 90% probability      *
# Play C (cooperate) with 10% probability     - Otherwise:      * Generate a
# random number between 0 and 1      * If this number is less than your
# calculated cooperation probability, play C      * If this number is greater
# than or equal to your calculated cooperation probability, play D  4.
# Regardless of the above rules, there's a 5% chance to play the opposite of
# what the strategy suggests, to add unpredictability.  This strategy: - Starts
# cooperatively to encourage mutual cooperation - Adapts to the opponent's level
# of cooperation, maintaining neutrality - Gradually becomes more cautious
# towards the end of the game - Protects against consecutive defections but
# allows for forgiveness - Includes a small element of randomness to avoid being
# too predictable  The strategy will tend to cooperate more when: - The opponent
# has a high cooperation rate - It's earlier in the game - The opponent hasn't
# recently defected multiple times in a row  It will tend to defect more when: -
# The opponent has a low cooperation rate - It's later in the game - The
# opponent has recently defected multiple times in a row  This revised strategy
# maintains a neutral approach while being simpler and more robust against
# various opponent behaviors.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      recent_moves = opponent.history[-20:]
      opponent_coop_rate = sum([a == axl.Action.C for a in recent_moves]) / len(recent_moves)

      base_coop_prob = opponent_coop_rate

      rounds_remaining = 1000 - len(self.history)
      if rounds_remaining <= 100:
          base_coop_prob -= min(0.2, 0.002 * (100 - rounds_remaining))

      coop_prob = base_coop_prob + (self._random.random() * 0.1 - 0.05)

      last_three = opponent.history[-3:]
      if len(last_three) == 3 and all(a == axl.Action.D for a in last_three):
          action = axl.Action.D if self._random.random() < 0.9 else axl.Action.C
      else:
          action = axl.Action.C if self._random.random() < coop_prob else axl.Action.D

      if self._random.random() < 0.05:
          action = axl.Action.C if action == axl.Action.D else axl.Action.D

      return action

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. For each subsequent round:    -
# Calculate the opponent's cooperation rate over the last 20 moves (or all
# previous moves if fewer than 20 have been played).    - Set the cooperation
# threshold at 50% initially.  3. Determine your move based on the following
# conditions:    a) If the opponent's cooperation rate is above the current
# threshold:       - Play C with 85% probability       - Play D with 15%
# probability    b) If the opponent's cooperation rate is at or below the
# current threshold:       - Play D with 85% probability       - Play C with 15%
# probability  4. Special conditions:    - If the opponent has played D for 5
# consecutive rounds:      - Play D for the next 5 rounds      - Then play C
# once      - Return to the main strategy (step 3)  5. Every 100 rounds,
# reassess and adjust:    - Calculate the opponent's cooperation rate over the
# last 100 rounds    - If this rate is above 60%, increase the cooperation
# threshold by 5% (up to a maximum of 60%)    - If this rate is below 40%,
# decrease the cooperation threshold by 5% (down to a minimum of 40%)  6.
# Continue this strategy for all 1000 rounds, including the final rounds.  This
# strategy maintains a neutral approach by adapting to the opponent's behavior.
# It's simple to implement and understand, with clear conditions for cooperation
# and defection. The strategy is more robust against various opponent behaviors
# due to its adaptive nature and the inclusion of a small random element. It
# also avoids the predictability of always defecting in the final rounds.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.cooperation_threshold = 0.5
          self.consecutive_defections = 0
          self.rounds_to_defect = 0
          return axl.Action.C

      if opponent.history and opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0

      if self.rounds_to_defect > 0:
          self.rounds_to_defect -= 1
          if self.rounds_to_defect == 0:
              return axl.Action.C
          return axl.Action.D

      if len(self.history) % 100 == 0 and len(self.history) > 0:
          last_100_cooperation_rate = opponent.history[-100:].count(axl.Action.C) / 100
          if last_100_cooperation_rate > 0.6:
              self.cooperation_threshold = min(0.6, self.cooperation_threshold + 0.05)
          elif last_100_cooperation_rate < 0.4:
              self.cooperation_threshold = max(0.4, self.cooperation_threshold - 0.05)

      opponent_cooperation_rate = opponent.history[-20:].count(axl.Action.C) / 20

      if self.consecutive_defections == 5:
          self.rounds_to_defect = 5
          return axl.Action.D

      if opponent_cooperation_rate > self.cooperation_threshold:
          return axl.Action.C if self._random.random() < 0.85 else axl.Action.D
      else:
          return axl.Action.D if self._random.random() < 0.85 else axl.Action.C
