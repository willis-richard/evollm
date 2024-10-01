import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Here's the revised strategy, taking into account the feedback:  1. Initial
# moves:    - Play D (defect) for the first two rounds.    - Play C (cooperate)
# on the third round.  2. Main strategy (from round 4 to 990):    Apply the
# following rules in order:     a. If the opponent has defected 3 or more times
# in the last 5 moves:       - Play D for the next 5 moves.       - After these
# 5 moves, play C once (as a forgiveness move).     b. If the opponent has
# defected in both of their last two moves:       - Play D.     c. Otherwise:
# - Play C.  3. End game (last 10 rounds, 991-1000):    - Always play D.  This
# strategy: - Starts aggressively to establish dominance. - Quickly allows for
# cooperation if the opponent is willing. - Responds firmly to consistent
# defection. - Provides a mechanism for returning to cooperation after
# punishment. - Exploits the known endpoint of the game.  The order of
# conditions ensures that the strategy responds appropriately to different
# opponent behaviors, prioritizing punishment of frequent defection, then
# responding to immediate defection, and defaulting to cooperation when the
# opponent seems cooperative.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.defect_count = 0
          self.forgiveness_move = False

      if len(self.history) < 2:
          return axl.Action.D
      elif len(self.history) == 2:
          return axl.Action.C
      elif len(self.history) >= 990:
          return axl.Action.D

      if self.defect_count > 0:
          self.defect_count -= 1
          if self.defect_count == 0:
              self.forgiveness_move = True
          return axl.Action.D

      if self.forgiveness_move:
          self.forgiveness_move = False
          return axl.Action.C

      recent_history = opponent.history[-5:] if len(opponent.history) >= 5 else opponent.history[:]
      opponent_recent_defections = recent_history.count(axl.Action.D)

      if opponent_recent_defections >= 3:
          self.defect_count = 5
          return axl.Action.D

      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D

      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. For each subsequent round,
# evaluate the following conditions in order:     a) If it's one of the last 20
# rounds (981-1000), play D with a probability of (current round number - 980) /
# 20. This creates a gradual increase in defection probability for the end game.
# b) If the opponent has played D twice in a row in the last two rounds, play D.
# c) If the opponent has alternated perfectly between C and D for the last 6
# rounds, play D for this round and the next round.     d) If you're in a round
# number that's a multiple of 50 ± a random number between 0 and 5 (e.g., round
# 48, 50, or 52), play C regardless of the opponent's recent moves. This is the
# "olive branch" mechanism.     e) Calculate the opponent's C to D ratio for the
# last 50 moves. If this ratio is below 0.4, play D with a probability of 1 -
# (ratio * 2). For example, if the ratio is 0.3, play D with a 40% probability.
# f) If the opponent has played C for the last 8 out of 10 rounds, play C for
# this round and the next round to reward sustained cooperation.  3. If none of
# the above conditions are met, default to the following "Adaptive Tit-for-Tat"
# behavior:    - Keep track of the number of times the opponent has defected
# after you cooperated (let's call this number N).    - Play C unless the
# opponent has played D for N consecutive rounds.    - If the opponent has
# played D for N consecutive rounds, play D once, then revert to C.    - Start
# with N = 2, and adjust N up or down by 1 (minimum 1, maximum 4) every 50
# rounds based on whether the opponent's overall C ratio is above or below 0.6.
# This strategy maintains the cooperative nature of the original while
# addressing the identified weaknesses. It's more adaptive to various opponent
# behaviors, has a more nuanced end-game approach, and includes mechanisms to
# deal with alternating strategies and gradual shifts in opponent behavior. The
# conditions are ordered to prioritize important situational responses while
# defaulting to a flexible tit-for-tat approach.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.N = 2
          self.last_N_adjustment = 0
          self.play_d_next = False
          self.play_c_next = False
          self.revert_to_c = False
          return axl.Action.C

      current_round = len(self.history) + 1

      # End game strategy
      if current_round > 980:
          defect_probability = (current_round - 980) / 20
          return self._random.random_choice(1 - defect_probability)

      if current_round % 50 == 0:
          overall_c_ratio = opponent.cooperations / len(opponent.history)
          if overall_c_ratio > 0.6:
            self.N = max(1, self.N - 1)
          else:
            self.N = min(4, self.N + 1)

      # Check for play_d_next or play_c_next from previous round
      if self.play_d_next:
          self.play_d_next = False
          return axl.Action.D
      if self.play_c_next:
          self.play_c_next = False
          return axl.Action.C

      # Opponent played D twice in a row
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D

      # Opponent alternated perfectly between C and D for the last 6 rounds
      if len(opponent.history) >= 6 and opponent.history[-6:] == [axl.Action.C, axl.Action.D] * 3:
          self.play_d_next = True
          return axl.Action.D

      # "Olive branch" mechanism
      if current_round % (50 + self._random.randint(low=-5, high=5)):
          return axl.Action.C

      # Calculate opponent's C to D ratio for last 50 moves
      if len(opponent.history) >= 50:
          recent_moves = opponent.history[-50:]
          c_ratio = recent_moves.count(axl.Action.C) / 50
          if c_ratio < 0.4:
              defect_probability = 1 - (c_ratio * 2)
              return self._random.random_choice(1 - defect_probability)

      # Reward sustained cooperation
      if len(opponent.history) >= 10 and opponent.history[-10:].count(axl.Action.C) >= 8:
          self.play_c_next = True
          return axl.Action.C

      # Adaptive Tit-for-Tat
      if all(move == axl.Action.D for move in opponent.history[-self.N:]):
          self.play_c_next = True
          return axl.Action.D

      return axl.Action.C

# Certainly. Here's a revised strategy that incorporates the feedback and
# clearly outlines the conditions for cooperation and defection:  1. Start by
# playing C (cooperate) in the first round.  2. For each subsequent round,
# follow these rules in order:     a. If it's the final round (round 1000), play
# D (defect).        b. If there has been mutual defection (D-D) for the last 10
# consecutive rounds, play C for this round only.        c. If it's a multiple
# of 5 rounds (i.e., rounds 5, 10, 15, etc.), evaluate the opponent's last 5
# moves:       - If the opponent played C 3 or more times out of the last 5
# rounds, play C.       - If the opponent played D 3 or more times out of the
# last 5 rounds, play D.        d. If none of the above conditions are met,
# mirror the opponent's most recent move (play C if they played C, or D if they
# played D).  This strategy maintains neutrality by primarily mirroring the
# opponent's moves while incorporating adaptive elements to respond to
# consistent behavior patterns. It's simpler than the original proposal and
# addresses the main points of feedback:  1. It uses a shorter evaluation period
# (5 rounds instead of 10) to be more responsive to recent changes in opponent
# behavior. 2. It removes the overly complex triggers and periodic cooperation
# tests. 3. It includes a mechanism to break out of prolonged mutual defection
# cycles. 4. It maintains the end-game protection but limits it to only the
# final round to preserve neutrality for longer.  This strategy should perform
# well against a variety of opponent behaviors, encouraging cooperation when
# possible, protecting against exploitation, and adapting to changes in the
# opponent's strategy. It's simple enough to be easily implemented while still
# incorporating key strategic elements for optimizing performance in the
# iterated game.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      if len(self.history) == 999:  # Final round (1000th round)
          return axl.Action.D

      if len(self.history) >= 10:
          last_10_moves = list(zip(self.history[-10:], opponent.history[-10:]))
          if all(move == (axl.Action.D, axl.Action.D) for move in last_10_moves):
              return axl.Action.C

      if len(self.history) % 5 == 4 and len(self.history) >= 5:  # Every 5th round, starting from 5th
          opponent_last_5 = opponent.history[-5:]
          if opponent_last_5.count(axl.Action.C) >= 3:
              return axl.Action.C
          else:
              return axl.Action.D

      return opponent.history[-1]

# Here's the revised strategy, taking into account the feedback and clearly
# stating the conditions for cooperation or defection:  1. For the first 20
# rounds: Always defect (D).  2. For rounds 21 to 900:     a. If the opponent's
# defection rate over the last 30 rounds exceeds 80%:       - Defect (D) for the
# next 10 rounds.     b. Otherwise, base your move on the opponent's previous
# move:       - If the opponent defected (D) in the previous round:         *
# Always defect (D).       - If the opponent cooperated (C) in the previous
# round:         * Calculate your defection probability:           - Start with
# a base 60% chance to defect.           - If you're behind in total score,
# increase this by 10%.           - If you're ahead in total score, decrease
# this by 5%.           - Ensure the final probability is between 55% and 70%.
# * Randomly choose to defect (D) or cooperate (C) based on this probability.
# c. Regardless of the above, on each turn:       - With a 5% chance, override
# the above decisions and defect (D) for this round and the next two rounds
# (3-round probe).  3. For the last 100 rounds (901-1000):    - Calculate your
# defection probability:      * Start at 80% for round 901.      * Increase by
# 0.2% each round.    - Randomly choose to defect (D) or cooperate (C) based on
# this probability.  This strategy: - Starts aggressively with all-D play. -
# Maintains a generally aggressive stance with a bias towards defection. -
# Punishes highly defective opponents with all-D play. - Adapts to the game
# state by adjusting defection probability based on score difference. - Includes
# unpredictable aggressive probes. - Gradually transitions to all-D play in the
# endgame.  The conditions are ordered from most specific (initial rounds, high
# opponent defection rate) to more general (based on opponent's last move), with
# the random probe as an override condition. The endgame strategy is applied
# last, replacing all previous conditions in the final rounds.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.probe_counter = 0
          self.high_defection_counter = 0

      turn = len(self.history)

      # First 20 rounds: Always defect
      if turn < 20:
          return axl.Action.D

      # Last 100 rounds: Increasing defection probability
      if turn >= 900:
          defect_prob = 0.8 + (turn - 900) * 0.002
          return self._random.random_choice(1 - defect_prob)

      if self.high_defection_counter > 0:
          self.high_defection_counter -= 1
          return axl.Action.D

      # Check for 3-round probe
      if self.probe_counter > 0:
          self.probe_counter -= 1
          return axl.Action.D

      # 5% chance to start a 3-round probe
      if self._random.random() < 0.05:
          self.probe_counter = 2
          return axl.Action.D

      # Check opponent's defection rate over last 30 rounds
      if turn >= 30:
          recent_defections = opponent.history[-30:].count(axl.Action.D)
          if recent_defections / 30 > 0.8:
              self.high_defection_counter = 10
              return axl.Action.D

      # Base decision on opponent's previous move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          # Calculate defection probability
          defect_prob = 0.6
          if self.score < opponent.score:
              defect_prob += 0.1
          else:
              defect_prob -= 0.05
          return self._random.random_choice(1 - defect_prob)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. For each subsequent round, make
# decisions in the following order:     a. If it's one of the last 10 rounds of
# the game:       - Cooperate with 90% probability.       - Defect with 10%
# probability.     b. If the opponent has defected in more than 80% of the last
# 20 moves:       - Play Tit-for-Tat for the next 20 moves (copy the opponent's
# last move).       - After these 20 moves, return to the main strategy.     c.
# If it's a multiple of 40 rounds (e.g., round 40, 80, 120...):       - Play
# Cooperate (C) regardless of the opponent's recent actions.     d. Calculate
# the opponent's cooperation rate in the last 10 moves.     e. If the opponent's
# last move was Cooperate:       - Cooperate.     f. If the opponent's last move
# was Defect:       - If the opponent's cooperation rate is 70% or higher:
# * Cooperate with 80% probability.         * Defect with 20% probability.
# - If the opponent's cooperation rate is between 30% and 70%:         *
# Cooperate with 50% probability.         * Defect with 50% probability.       -
# If the opponent's cooperation rate is below 30%:         * Cooperate with 20%
# probability.         * Defect with 80% probability.  3. If none of the above
# conditions are met, Cooperate.  This revised strategy maintains simplicity
# while addressing the main points of feedback:  1. It remains cooperative
# overall but adapts to the opponent's behavior. 2. It handles aggressive
# opponents more effectively by considering recent cooperation rates. 3. It
# deals better with alternating strategies by using probabilistic responses
# based on recent behavior. 4. It includes a simple end-game strategy that's
# less exploitable. 5. The "olive branch" (now every 40 rounds) is maintained
# but simplified.  The strategy is clear about when it will cooperate or defect,
# with conditions ordered from most specific (end-game) to most general (default
# cooperation). This approach allows for adaptive play while maintaining a
# cooperative bias and protecting against exploitation.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.tft_counter = 0
          return axl.Action.C

      if len(self.history) > 990:
          return self._random.random_choice(0.9)

      if self.tft_counter > 0:
          self.tft_counter -= 1
          return opponent.history[-1]

      if len(opponent.history) >= 20 and opponent.history[-20:].count(axl.Action.D) / 20 > 0.8:
          self.tft_counter = 19
          return opponent.history[-1]

      if len(self.history) % 40 == 0:
          return axl.Action.C

      if len(opponent.history) >= 10:
          opp_coop_rate = opponent.history[-10:].count(axl.Action.C) / 10
      else:
          opp_coop_rate = opponent.history.cooperations / len(opponent.history) if opponent.history else 1

      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          if opp_coop_rate >= 0.7:
              return self._random.random_choice(0.8)
          elif 0.3 <= opp_coop_rate < 0.7:
              return self._random.random_choice(0.5)
          else:
              return self._random.random_choice(0.2)

      return axl.Action.C

# Here's a revised strategy that takes into account the feedback and aims to be
# clearer, simpler, and more neutral:  1. Start the game with a mixed strategy:
# Play C (cooperate) with 50% probability and D (defect) with 50% probability
# for the first 5 rounds.  2. After the initial 5 rounds, and for every
# subsequent round:     a. Calculate the opponent's cooperation rate over the
# last 5 rounds.        b. If the opponent's cooperation rate is:       - Above
# 60%: Play C       - Below 40%: Play D       - Between 40% and 60%: Use a mixed
# strategy - Play C with probability equal to the opponent's cooperation rate,
# and D with the remaining probability.  3. Every 50 rounds, reassess and
# adjust:        a. Calculate your average score per round for the last 50
# rounds.        b. If your average score is:       - Below 2: Decrease all
# cooperation thresholds by 5 percentage points (e.g., 60% becomes 55%, 40%
# becomes 35%)       - Above 3: Increase all cooperation thresholds by 5
# percentage points       - Between 2 and 3: Keep thresholds unchanged  4. For
# the last 20 rounds of the game:        a. If your total score is higher than
# the opponent's, continue with the current strategy.        b. If your total
# score is lower than the opponent's:       - Play D if the score difference is
# more than 50 points       - Otherwise, play the mixed strategy from step 2b
# This revised strategy addresses the previous issues by: - Starting neutrally
# with a 50/50 mixed strategy - Using shorter (5-round) analysis periods for
# quicker adaptation - Providing clear conditions for cooperation, defection,
# and mixed play - Implementing more frequent reassessments (every 50 rounds) -
# Adjusting thresholds based on performance - Incorporating a simple end-game
# strategy  The strategy remains relatively simple while being more responsive
# to opponent behavior and maintaining a more neutral stance throughout the
# game.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.upper_threshold = 0.6
          self.lower_threshold = 0.4
          self.reassessment_counter = 0

      if len(self.history) < 5:
          return self._random.random_choice(0.5)

      opponent_coop_rate = opponent.history[-5:].count(axl.Action.C) / 5

      self.reassessment_counter += 1
      if self.reassessment_counter == 50:
          self.reassessment_counter = 0
          avg_score = self.total_scores(self.history[-50:], opponent.history[-50:])[0] / 50
          if avg_score < 2:
              self.upper_threshold = max(0, self.upper_threshold - 0.05)
              self.lower_threshold = max(0, self.lower_threshold - 0.05)
          elif avg_score > 3:
              self.upper_threshold = min(1, self.upper_threshold + 0.05)
              self.lower_threshold = min(1, self.lower_threshold + 0.05)

      if len(self.history) >= 980:
          if self.score < opponent.score - 50:
              return axl.Action.D
          else:
              return self._random.random_choice(opponent_coop_rate)

      if opponent_coop_rate > self.upper_threshold:
          return axl.Action.C
      elif opponent_coop_rate < self.lower_threshold:
          return axl.Action.D
      else:
          return self._random.random_choice(opponent_coop_rate)

# Here's a revised strategy incorporating the feedback:  1. Initial Probing
# (First 10 rounds):    - Play D-C-D-C-D-C-D-C-D-C    This pattern helps gather
# information about the opponent's strategy while maintaining an aggressive
# stance.  2. Main Strategy (Rounds 11-980):    Apply the following rules in
# order:     a. If opponent has defected in the last 3 rounds, play D.        b.
# If your score is behind the opponent's estimated score by:       - 20-39
# points: Play D with 60% probability, otherwise C.       - 40+ points: Play D
# with 80% probability, otherwise C.        c. If you've played C for the last 5
# rounds, play D (prevents exploitation).        d. If opponent has cooperated
# in the last 2 rounds, play C.        e. Otherwise, play D.  3. Periodic
# Aggression:    Every 30-50 rounds (randomize this interval), play D for 2
# consecutive rounds regardless of other conditions. This maintains
# unpredictability.  4. Pattern Break:    If the same pattern of plays (both
# yours and opponent's) has repeated for 10+ rounds, break it by playing the
# opposite of your last move.  5. Endgame (Last 20 rounds):    - If your score
# is higher, always play D.    - If your score is lower:      - Play C if the
# opponent cooperated in the previous round.      - Otherwise, play D.  This
# strategy: - Starts with a mixed approach to gather information. - Maintains an
# overall aggressive stance but allows for cooperation. - Adapts based on the
# score difference and opponent's recent moves. - Includes periodic aggression
# and pattern-breaking to avoid predictability. - Has a nuanced endgame approach
# based on the score difference.  The strategy is simpler than the previous
# version while incorporating key improvements. It's more adaptive to the
# opponent's behavior and the game state, maintains aggression when needed, but
# also allows for cooperative periods to maximize points against cooperative
# opponents.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.periodic_aggression_counter = self._random.randint(30, 50)
          self.periodic_aggression_plays = 0
          self.last_ten_moves = []

      ENDGAME_START = 980

      # Initial Probing (First 10 rounds)
      if len(self.history) < 10:
          return axl.Action.D if len(self.history) % 2 == 0 else axl.Action.C

      # Periodic Aggression
      if self.periodic_aggression_plays > 0:
          self.periodic_aggression_plays -= 1
          return axl.Action.D
      self.periodic_aggression_counter -= 1
      if self.periodic_aggression_counter <= 0:
          self.periodic_aggression_counter = self._random.randint(30, 50)
          self.periodic_aggression_plays = 2
          return axl.Action.D

      # Endgame (Last 20 rounds)
      if len(self.history) >= ENDGAME_START:
          if self.score > opponent.score:
              return axl.Action.D
          else:
              return opponent.history[-1]

      # Pattern Break
      if len(set(self.history[-10:])) == 1 and len(set(opponent.history[-10:])):
          return self.history[-1].flip()

      # Main Strategy
      if opponent.history[-3:].count(axl.Action.D) >= 1:
          return axl.Action.D

      score_diff = opponent.score - self.score
      if 20 <= score_diff < 40 and self._random.random() < 0.6:
          return axl.Action.D
      elif score_diff >= 40 and self._random.random() < 0.8:
          return axl.Action.D

      if self.history[-5:].count(axl.Action.C) == 5:
          return axl.Action.D

      if opponent.history[-2:].count(axl.Action.C) >= 1:
          return axl.Action.C

      return axl.Action.D

# Here's the revised strategy, taking into account the feedback and focusing on
# clear conditions for cooperation or defection:  1. Start by playing Cooperate
# (C) in the first round.  2. For each subsequent round, follow these steps in
# order:     a. If this is one of the last 10 rounds of the game, play C.     b.
# If this is one of two "olive branch" moves (occurring every 50 rounds), play
# C.     c. Calculate the opponent's cooperation rate over the last 20 moves (or
# all previous moves if fewer than 20).     d. Based on the opponent's
# cooperation rate, set the forgiveness probability P:       - If rate > 80%,
# set P = 0.8       - If 60% < rate ≤ 80%, set P = 0.7       - If 40% < rate ≤
# 60%, set P = 0.6       - If rate ≤ 40%, set P = 0.5     e. If the opponent
# played C in the previous round, play C.     f. If the opponent played D in the
# previous round:       - Generate a random number R between 0 and 1.       - If
# R < P, play C (forgiving the defection).       - If R ≥ P, play D (retaliating
# against the defection).  This strategy maintains a cooperative approach while
# adapting to the opponent's behavior. It's simple, clearly defines when to
# cooperate or defect, and adjusts its forgiveness rate based on the opponent's
# recent actions. The strategy remains generous but becomes more cautious
# against consistently aggressive opponents.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      if len(self.history) > 990:
          return axl.Action.C

      if len(self.history) % 50 == 0 or len(self.history) % 50 == 1:
          return axl.Action.C

      recent_history = opponent.history[-20:] if len(opponent.history) >= 20 else opponent.history[:]
      cooperation_rate = recent_history.count(axl.Action.C) / len(recent_history)

      if cooperation_rate > 0.8:
          forgiveness_probability = 0.8
      elif 0.6 < cooperation_rate <= 0.8:
          forgiveness_probability = 0.7
      elif 0.4 < cooperation_rate <= 0.6:
          forgiveness_probability = 0.6
      else:
          forgiveness_probability = 0.5

      return axl.Action.C if opponent.history[-1] == axl.Action.C else self._random.random_choice(forgiveness_probability)

# Here's the revised strategy, taking into account the feedback and focusing on
# clear conditions for cooperation and defection:  1. Start by cooperating (C)
# in the first round.  2. For each subsequent round, follow these rules in
# order:     a. Random Move: With a 5% probability, play a random move (C or D
# with equal probability). If this occurs, skip the remaining steps for this
# round.     b. Retaliation: If the opponent defected in the previous round,
# defect (D) with an 80% probability. If you choose not to defect here,
# cooperate (C) instead.     c. Forgiveness: If you've defected for 5
# consecutive rounds, cooperate (C) for this round.     d. Cooperation: If none
# of the above conditions are met, cooperate (C).  3. Every 5 rounds, evaluate
# the opponent's recent behavior:     a. If they've cooperated 4-5 times out of
# the last 5 rounds, continue with the current strategy.     b. If they've
# cooperated 2-3 times out of the last 5 rounds, continue with the current
# strategy but increase the forgiveness rate in step 2b to 30% (i.e., defect
# with 70% probability after opponent's defection).     c. If they've cooperated
# 0-1 times out of the last 5 rounds, defect (D) for the next 5 rounds,
# overriding all other rules except 2a.  4. Maintain a rolling average of your
# score over the last 20 rounds. If this average drops below 2 at any point,
# defect (D) for the next round before reverting to the main strategy.  This
# strategy is simpler and clearer about when to cooperate or defect. It
# maintains a neutral stance by starting cooperatively and adapting to the
# opponent's behavior. The random move element adds unpredictability, while the
# retaliation and forgiveness mechanisms allow for both protection against
# exploitation and the possibility of returning to mutual cooperation. The
# periodic evaluation and score-based adjustment provide additional adaptability
# to various opponent strategies.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_defections = 0
          self.defect_next_5_rounds = 0
          self.increased_forgiveness = False
          return axl.Action.C

      if self._random.random() < 0.05:
          return self._random.random_choice()

      if self.defect_next_5_rounds > 0:
          self.defect_next_5_rounds -= 1
          self.consecutive_defections += 1
          return axl.Action.D

      if len(self.history) % 5 == 0:
          recent_cooperations = opponent.history[-5:].count(axl.Action.C)
          if recent_cooperations <= 1:
              self.defect_next_5_rounds = 5
              return axl.Action.D
          elif recent_cooperations <= 3:
              self.increased_forgiveness = True
          else:
              self.increased_forgiveness = False

      if len(self.history) >= 20:
          recent_scores = self.total_scores(self.history[-20:], opponent.history[-20:])[0] / 20
          if recent_scores < 2:
              self.consecutive_defections += 1
              return axl.Action.D

      if self.consecutive_defections >= 5:
          self.consecutive_defections = 0
          return axl.Action.C

      if opponent.history[-1] == axl.Action.D:
          defect_prob = 0.7 if self.increased_forgiveness else 0.8
          if self._random.random() < defect_prob:
              self.consecutive_defections += 1
              return axl.Action.D
          else:
              self.consecutive_defections = 0
              return axl.Action.C

      self.consecutive_defections = 0
      return axl.Action.C

# Certainly. Here's the revised strategy, taking into account the feedback and
# clearly stating the conditions for cooperation or defection:  1. Start the
# game by playing D (defect) for the first 10 rounds.  2. From round 11 onwards,
# for each round, apply the following decision rules in order:     a. If this is
# one of the last 20 rounds of the game, play D.        b. If there's a 10%
# random chance (roll a 1 on a 10-sided die), play D.        c. If the opponent
# has played D for the last 5 consecutive rounds, play D for this round and the
# next 9 rounds (10 rounds total).        d. If the opponent has played the same
# move (either C or D) for the last 3 rounds, play D.        e. If the opponent
# has played D in either of the last 2 rounds, play D.        f. If none of the
# above conditions are met (which means the opponent has played C for the last 2
# rounds), play C.  This strategy maintains an aggressive stance while being
# adaptive to the opponent's behavior. It's simpler than the previous version,
# with clear conditions for when to cooperate or defect. The order of the
# conditions ensures that the most important or overriding factors (end-game,
# random defection, punishing long defection streaks) are considered first,
# followed by more nuanced responses to the opponent's recent moves.  To
# summarize the strategy's behavior: - It starts aggressively. - It has a
# consistent element of unpredictability with the 10% random defection. - It
# punishes sustained defection from the opponent. - It exploits detectable
# patterns in the opponent's play. - It's generally retaliatory, defecting if
# the opponent has recently defected. - It cautiously cooperates only when the
# opponent has recently been cooperative. - It finishes the game with pure
# defection.  This strategy should perform well against a wide range of opponent
# behaviors while maintaining its aggressive nature.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      INITIAL_DEFECT_ROUNDS = 10
      ENDGAME_ROUNDS = 20
      RANDOM_DEFECT_PROBABILITY = 0.1
      OPPONENT_DEFECT_STREAK = 5
      DEFECT_STREAK_DURATION = 10
      OPPONENT_SAME_MOVE_STREAK = 3
      RECENT_ROUNDS_CHECK = 2
      TOTAL_ROUNDS = 1000

      current_round = len(self.history)

      self.defect_count = getattr(self, 'defect_count', 0)
      self.last_defection_round = getattr(self, 'last_defection_round', -1)

      # First 10 rounds: Defect
      if current_round < INITIAL_DEFECT_ROUNDS:
          return axl.Action.D

      # Last 20 rounds: Defect
      if current_round >= TOTAL_ROUNDS - ENDGAME_ROUNDS:
          return axl.Action.D

      # 10% chance of random defection
      if self._random.random() < RANDOM_DEFECT_PROBABILITY:
          return axl.Action.D

      # If opponent defected for last 5 rounds, defect for 10 rounds
      if opponent.history[-OPPONENT_DEFECT_STREAK:].count(axl.Action.D) == OPPONENT_DEFECT_STREAK:
          self.defect_count = DEFECT_STREAK_DURATION
          self.last_defection_round = current_round

      # If we're in a defection streak, continue defecting
      if current_round - self.last_defection_round < self.defect_count:
          return axl.Action.D

      # If opponent played the same move for the last 3 rounds, defect
      if len(set(opponent.history[-OPPONENT_SAME_MOVE_STREAK:])) == 1:
          return axl.Action.D

      # If opponent defected in either of the last 2 rounds, defect
      if axl.Action.D in opponent.history[-RECENT_ROUNDS_CHECK:]:
          return axl.Action.D

      # If none of the above conditions are met, cooperate
      return axl.Action.C

# Here's a revised strategy incorporating the feedback:  1. Start by playing
# Cooperate (C) for the first 5 moves. This establishes an initial cooperative
# reputation.  2. For the remainder of the game, follow these rules in order:
# a. If it's one of the last 100 rounds, calculate the probability of defection
# as: (current round number - 900) / 100. Play D with this probability, and C
# otherwise. This creates a gradual transition to more frequent defection in the
# end game.     b. If the opponent has defected for 5 or more consecutive
# rounds, play D for a number of rounds equal to the opponent's current
# defection streak (up to a maximum of 10 rounds). This implements a dynamic
# punishment system.     c. If it's a multiple of 50 rounds (50, 100, 150,
# etc.), play C. This serves as a periodic "olive branch."     d. If it's a
# multiple of 100 rounds (100, 200, 300, etc.), play D. This acts as an
# occasional probing move.     e. Calculate the opponent's cooperation rate over
# the last 50 moves. If this rate is below 30%, play D with 70% probability and
# C with 30% probability.     f. If the opponent played C in the previous round,
# play C.     g. If the opponent played D in the previous round, play D with a
# probability equal to (1 - opponent's overall cooperation rate), and C
# otherwise. This implements adaptive forgiveness.     h. If none of the above
# conditions are met, play C.  This strategy maintains a cooperative bias while
# being more adaptive to opponent behavior. It starts cooperatively, implements
# dynamic punishment for persistent defection, gradually increases defection
# towards the end game, and adjusts its forgiveness based on the opponent's
# overall behavior. The periodic cooperative and defective moves help in
# relationship reset and strategy probing, respectively.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defection_streak = 0
          self.punishment_rounds = 0

      if len(self.history) < 5:
          return axl.Action.C

      if len(self.history) > 900:
          defect_prob = (len(self.history) - 900) / 100
          return self._random.random_choice(1 - defect_prob)

      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D

      if opponent.history[-5:].count(axl.Action.D) >= 5:
          self.defection_streak = min(opponent.history[::-1].index(axl.Action.C), 10)
          self.punishment_rounds = self.defection_streak
          return axl.Action.D

      if len(self.history) % 50 == 0:
          return axl.Action.C

      if len(self.history) % 100 == 0:
          return axl.Action.D

      recent_coop_rate = opponent.history[-50:].count(axl.Action.C) / 50
      if recent_coop_rate < 0.3:
          return self._random.random_choice(0.3)

      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      overall_coop_rate = opponent.cooperations / len(opponent.history)
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(overall_coop_rate)

      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) for the first round.  2. For each subsequent round,
# calculate the cooperation rate of your opponent over the last 20 rounds (or
# all previous rounds if fewer than 20 have been played).  3. Determine your
# action for the current round based on the following conditions, checked in
# order:     a. If you're in the last 50 rounds of the game:       - Calculate
# your defection probability as: (current round number - 950) / 50       - Play
# D with this probability, otherwise play C     b. If the opponent has played D
# for the last 3 consecutive rounds:       - Play D with 70% probability, C with
# 30% probability     c. If the opponent's cooperation rate is:       - 70% or
# higher: Play C       - Between 30% and 70%: Play C with probability equal to
# their cooperation rate       - Below 30%: Play D with 70% probability, C with
# 30% probability  4. If none of the above conditions are met (which should only
# happen in the first few rounds), play Tit-for-Tat (copy the opponent's last
# move).  This revised strategy addresses the main points of feedback:  - It's
# simpler, with fewer distinct phases and rules. - It's more responsive to the
# opponent's behavior by using a rolling average. - It removes the exploitable
# "olive branch" concept. - It clarifies the conditions for cooperation and
# defection, ordering them by priority. - It adapts more smoothly to changes in
# the opponent's behavior. - The endgame strategy is more gradual and starts
# earlier.  This strategy aims to play neutrally by closely mirroring the
# opponent's cooperation level in most cases, while protecting against
# exploitation and adapting to end-game considerations. It should perform
# reasonably well against a variety of opponent strategies while remaining
# relatively simple to implement and understand.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      rounds_played = len(self.history)
      last_20_rounds = min(20, rounds_played)
      recent_coop_rate = opponent.history[-last_20_rounds:].count(axl.Action.C) / last_20_rounds

      if rounds_played > 950:
          defect_prob = (rounds_played - 950) / 50
          return self._random.random_choice(1 - defect_prob)

      if rounds_played >= 3 and opponent.history[-3:].count(axl.Action.D) == 3:
          return self._random.random_choice(0.3)

      if recent_coop_rate >= 0.7:
          return axl.Action.C
      elif 0.3 <= recent_coop_rate < 0.7:
          return self._random.random_choice(recent_coop_rate)
      elif recent_coop_rate < 0.3:
          return self._random.random_choice(0.3)

      return opponent.history[-1]

# Here's a revised, simpler, and more aggressive strategy that takes into
# account the feedback:  1. Start by playing D (defect) for the first 5 rounds.
# 2. For rounds 6-950, use the following rules in order:     a. If the opponent
# has defected 3 or more times in the last 5 rounds, play D for the next 10
# rounds.        b. If it's not one of those 10 punishment rounds, use this
# modified Tit-for-Tat approach:       - If the opponent played C in the
# previous round, play C with 70% probability and D with 30% probability.
# - If the opponent played D in the previous round, play D.  3. For the last 50
# rounds (951-1000), always play D.  This strategy is more aggressive and
# simpler than the previous version. Here's how it addresses the main points of
# feedback:  - It starts aggressively but for a shorter period, allowing quicker
# adaptation. - It uses a short-term memory (last 5 rounds) to quickly punish
# defection. - The Tit-for-Tat portion is less generous, playing D 30% of the
# time even after opponent's cooperation. - It has a clear and aggressive end-
# game strategy. - It removes complex elements like long-term defection rate
# tracking, probing, and conditions based on long streaks of mutual cooperation.
# - The rules are ordered clearly, with the punishment condition taking
# precedence.  This strategy should perform well against a variety of opponent
# behaviors: - It can quickly adapt to and punish consistent defectors. - It can
# establish cooperation with cooperative opponents while still occasionally
# exploiting them. - It's less vulnerable to alternating strategies due to its
# short-term memory and punishment mechanism. - It maximizes gains in the end-
# game by always defecting in the last 50 rounds.  The strategy remains
# aggressive throughout, with a clear bias towards defection, while still
# allowing for some cooperation if the opponent is consistently cooperative.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.punishment_rounds = 0

      round_number = len(self.history) + 1

      # First 5 rounds: always defect
      if round_number <= 5:
          return axl.Action.D

      # Last 50 rounds: always defect
      if round_number > 950:
          return axl.Action.D

      # Check if we're in a punishment phase
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D

      # Check if opponent has defected 3 or more times in the last 5 rounds
      if opponent.history[-5:].count(axl.Action.D) >= 3:
          self.punishment_rounds = 10
          return axl.Action.D

      # Modified Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.7)
      else:
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. For subsequent rounds, follow
# these rules in order:     a. If the opponent has defected more than 60% of the
# time in the last 20 moves:       - Play Tit-for-Tat for the next 20 moves
# (copy opponent's last move).       - After 20 moves, return to the main
# strategy.     b. If it's a multiple of 40-60 rounds (randomly chosen at the
# start of the game):       - Play Cooperate for this round, regardless of the
# opponent's recent actions.     c. If the opponent has cooperated in their last
# move:       - Cooperate with 95% probability.       - Defect with 5%
# probability (to introduce unpredictability).     d. If the opponent has
# defected in their last move, but cooperated in the move before that:       -
# Cooperate (forgiving a single defection).     e. If the opponent has defected
# in their last two moves:       - Defect for this move only.     f. In any
# other case:       - Cooperate.  3. Forgiveness Mechanism:     - Keep track of
# the opponent's cooperation rate over the last 50 moves.    - If this rate
# improves by 20% or more compared to the previous 50 moves, play Cooperate for
# the next 2 moves regardless of other conditions.  This strategy maintains a
# cooperative approach while addressing the main points of feedback:  - It's
# still relatively simple and primarily cooperative. - It adapts more quickly to
# aggressive opponents by lowering the defection threshold from 70% to 60%. -
# The "olive branch" is now semi-random (every 40-60 rounds) to reduce
# predictability. - A small random element is introduced to make the strategy
# less exploitable. - The forgiveness mechanism allows for recovery from periods
# of mutual defection. - The special behavior for the last 10 rounds has been
# removed. - It takes into account the payoff structure by generally favoring
# cooperation, which has a higher potential payoff.  This revised strategy
# should perform well against a wide range of opponent behaviors while
# maintaining its cooperative nature and adapting to both aggressive and
# changing strategies.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.random_round = self._random.randint(40, 60)
          self.tit_for_tat_counter = 0
          self.last_100_coop_rate = [0, 0]  # [previous 50, current 50]
          self.forgiveness_counter = 0

      if not self.history:
          return axl.Action.C

      if len(self.history) % 50 == 0:
          current_coop_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if len(self.history) >= 100:
              if current_coop_rate > self.last_100_coop_rate[0] * 1.2:
                  self.forgiveness_counter = 2
          self.last_100_coop_rate[0] = self.last_100_coop_rate[1]
          self.last_100_coop_rate[1] = current_coop_rate

      if self.forgiveness_counter > 0:
          self.forgiveness_counter -= 1
          return axl.Action.C

      if self.tit_for_tat_counter > 0:
          self.tit_for_tat_counter -= 1
          return opponent.history[-1]

      if len(self.history) >= 20 and opponent.history[-20:].count(axl.Action.D) / 20 > 0.6:
          self.tit_for_tat_counter = 20
          return opponent.history[-1]

      if len(self.history) % self.random_round == 0:
          self.random_round = self._random.randint(40, 60)
          return axl.Action.C

      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.95)

      if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.C:
          return axl.Action.C

      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D

      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. For the next 8-12 rounds
# (randomly determined at the start of each evaluation period), use Tit-for-Tat:
# copy your opponent's previous move.  3. After each evaluation period, assess
# your opponent's behavior:    a. Calculate the opponent's cooperation rate (CR)
# for the last period.    b. If CR ≥ 0.7, continue with Tit-for-Tat for the next
# period.    c. If 0.3 < CR < 0.7, adopt a mixed strategy for the next period:
# - Play C with probability equal to the CR       - Play D with probability
# equal to (1 - CR)    d. If CR ≤ 0.3, adopt a defensive strategy for the next
# period:       - Play D with probability 0.8       - Play C with probability
# 0.2  4. Override rules:    a. If the opponent has played D three times in a
# row, switch to the defensive strategy (80% D, 20% C) for the next 5 rounds,
# then return to step 3.    b. Every 100 rounds, offer an "olive branch":
# - Play C for one round       - If the opponent responded with C, play C again;
# otherwise, play D    c. If you detect a simple pattern in the opponent's last
# 10 moves (e.g., always D, alternating C and D), counter it in the next round
# by playing the move that maximizes your payoff against that pattern.  5. End-
# game strategy (last 10 rounds):    a. Continue using the strategy from step 3,
# but modify it as follows:    b. After each of your moves, increase your
# probability of playing D by 0.05    c. However, if the opponent plays C,
# decrease your probability of playing D by 0.025 in the next round (minimum
# probability of D is 0.5)  6. Decision order:    Always check the conditions in
# this order and apply the first one that matches:    1. End-game strategy (if
# in last 10 rounds)    2. Override rules    3. Current period strategy (Tit-
# for-Tat, mixed, or defensive)  This revised strategy maintains a neutral
# approach while being more adaptive and less exploitable. It takes into account
# the opponent's behavior over varying periods, responds to immediate threats,
# offers controlled opportunities for cooperation, and includes a more nuanced
# end-game approach. The clear decision order helps prevent conflicts between
# different parts of the strategy.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.evaluation_period = self._random.randint(8, 13)
          self.period_moves = 0
          self.current_strategy = "tit_for_tat"
          self.defensive_rounds = 0
          self.d_probability = 0
          self.mixed_c_prob = 0.5

      self.period_moves += 1

      # End-game strategy
      if len(self.history) >= 990:
          if len(self.history) == 990:
              self.d_probability = 0.05
          else:
              self.d_probability = min(1, self.d_probability + 0.05)
              if opponent.history[-1] == axl.Action.C:
                  self.d_probability = max(0.5, self.d_probability - 0.025)
          return self._random.random_choice(1 - self.d_probability)

      # Override rules
      if len(self.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          self.defensive_rounds = 5
          self.current_strategy = "defensive"

      if self.defensive_rounds > 0:
          self.defensive_rounds -= 1
          return self._random.random_choice(0.2)

      if len(self.history) % 100 == 0:
          return axl.Action.C
      elif len(self.history) % 100 == 1:
          return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D

      # Pattern detection
      if len(self.history) >= 10:
          pattern = opponent.history[-10:]
          if all(move == axl.Action.D for move in pattern):
              return axl.Action.D
          elif all(move == axl.Action.C for move in pattern):
              return axl.Action.C
          elif pattern == [axl.Action.C, axl.Action.D] * 5:
              return axl.Action.D
          elif pattern == [axl.Action.D, axl.Action.C] * 5:
              return axl.Action.C

      # Evaluation period strategy
      if self.period_moves >= self.evaluation_period:
          cr = opponent.history[-self.evaluation_period:].count(axl.Action.C) / self.evaluation_period
          if cr >= 0.7:
              self.current_strategy = "tit_for_tat"
          elif 0.3 < cr < 0.7:
              self.current_strategy = "mixed"
              self.mixed_c_prob = cr
          else:
              self.current_strategy = "defensive"
          self.period_moves = 0
          self.evaluation_period = self._random.randint(8, 13)

      if self.current_strategy == "tit_for_tat":
          return opponent.history[-1]
      elif self.current_strategy == "mixed":
          return self._random.random_choice(self.mixed_c_prob)
      else:  # defensive
          return self._random.random_choice(0.2)

# Here's the revised strategy, taking into account the feedback and focusing on
# clear conditions for cooperation and defection:  1. Start with Tit-for-Tat for
# the first 10 rounds:    - In round 1, cooperate.    - For rounds 2-10, play
# what the opponent played in the previous round.  2. For the remainder of the
# game (rounds 11-1000), use the following rules in order:     a. If it's a
# multiple of 100th round (100, 200, 300, etc.), play a random move (50% chance
# to cooperate, 50% to defect).     b. If the opponent defected in the previous
# round, always defect.     c. If the opponent cooperated in the previous round,
# base your decision on a cooperation probability (CP):       - Start with CP =
# 70%       - Cooperate with probability CP, defect with probability (100% - CP)
# d. After each round, update the CP based on the opponent's last 20 moves:
# - If the opponent cooperated 16 or more times out of the last 20 (80%+),
# decrease CP by 5%       - If the opponent defected 16 or more times out of the
# last 20 (80%+), decrease CP by 10%       - Otherwise, increase CP by 2%
# - Always keep CP between 20% and 80%  3. For the last 50 rounds (951-1000):
# - Follow the same rules as above, but after each round, additionally decrease
# CP by 1%    - CP can go below 20% in this phase, but not below 0%  This
# strategy: - Starts with a brief Tit-for-Tat phase to gauge the opponent -
# Maintains an overall aggressive stance by always defecting after opponent's
# defection - Adapts to the opponent's strategy by adjusting cooperation
# probability - Includes periodic random moves to prevent predictability -
# Gradually increases aggression in the endgame  The strategy is simpler than
# the previous version, with clear conditions for cooperation and defection. It
# behaves aggressively overall but can adapt to both cooperative and aggressive
# opponents. The continuous adjustment of cooperation probability allows for
# smoother adaptation compared to the previous version's step changes.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.cp = 0.7
          self.last_20_moves = []

      round_number = len(self.history) + 1

      # First 10 rounds: Tit-for-Tat
      if round_number <= 10:
          return opponent.history[-1] if opponent.history else axl.Action.C

      # Random move on multiples of 100
      if round_number % 100 == 0:
          return self._random.random_choice()

      # Defect if opponent defected in the previous round
      if opponent.history[-1] == axl.Action.D:
          action = axl.Action.D
      else:
          # Cooperate based on cooperation probability
          action = self._random.random_choice(self.cp)

      # Update last 20 moves
      self.last_20_moves.append(opponent.history[-1])
      if len(self.last_20_moves) > 20:
          self.last_20_moves.pop(0)

      # Update cooperation probability if we have at least 20 moves
      if len(self.last_20_moves) == 20:
          coop_count = self.last_20_moves.count(axl.Action.C)
          # Decrease CP if opponent is very cooperative (>80%)
          if coop_count > 16:
              self.cp = max(0.2, self.cp - 0.05)
          # Decrease CP if opponent is very defective (>80%)
          elif coop_count < 4:
              self.cp = max(0.2, self.cp - 0.1)
          # Increase CP if opponent is mixed
          else:
              self.cp = min(0.8, self.cp + 0.02)

      # Last 50 rounds
      if round_number > 950:
          self.cp = max(0, self.cp - 0.01)

      return action

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C for the first round.  2. For subsequent rounds, follow these rules
# in order:     a. If it's one of the last 50 rounds (951-1000), use the core
# strategy (step 2b) without any additional cooperative moves.     b. Core
# strategy (Adaptive Tit-for-Tat):       - If the opponent played C in the
# previous round, play C.       - If the opponent played D in the previous
# round:         * Calculate the opponent's overall cooperation rate.         *
# Play C with a probability equal to the opponent's cooperation rate, otherwise
# play D.     c. If you've played 50 rounds since your last "olive branch" move,
# play C regardless of the opponent's last move.     d. If the opponent has
# defected for 5 consecutive rounds, enter "Cautious Mode" for the next 10
# rounds:       - In this mode, play D with 90% probability and C with 10%
# probability.       - After 10 rounds, return to the core strategy.  3. Every
# 100 rounds, perform these adjustments:        a. Calculate your average score
# per round and your opponent's average score per round.        b. If your
# average score is more than 1 point lower than your opponent's:       - In the
# core strategy, reduce the probability of playing C after opponent's D by 10
# percentage points (but never below 5%).        c. If your average score is
# higher than or equal to your opponent's:       - In the core strategy,
# increase the probability of playing C after opponent's D by 5 percentage
# points (but never above the opponent's cooperation rate).  4. Keep a running
# count of successful cooperative moves (where both players played C). If this
# count drops below 20% of total moves played, for the next 20 rounds:    -
# Decrease the probability of playing C after opponent's D by half in the core
# strategy.    - Skip the "olive branch" move.  This strategy maintains the
# cooperative nature while being more adaptive to the opponent's behavior. It
# orders the conditions clearly, prioritizing end-game behavior, then the core
# strategy, followed by periodic cooperation attempts and responses to
# consistent defection. The adjustments based on score comparison and
# cooperation success rate allow the strategy to become more or less cooperative
# as needed, without losing its fundamental Tit-for-Tat basis.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.olive_branch_counter = 0
          self.cautious_mode_counter = 0
          self.c_after_d_prob = 1.0
          self.successful_cooperations = 0
          self.low_coop_counter = 0
          return axl.Action.C

      round_number = len(self.history) + 1
      opponent_last_move = opponent.history[-1]

      # Update successful cooperations counter
      if self.history[-1] == axl.Action.C and opponent_last_move == axl.Action.C:
          self.successful_cooperations += 1

      # Last 50 rounds
      if round_number > 950:
          if opponent_last_move == axl.Action.C:
              return axl.Action.C
          else:
              opp_coop_rate = opponent.history.cooperations / len(opponent.history)
              return self._random.random_choice(opp_coop_rate)

      # Core strategy (Adaptive Tit-for-Tat)
      if opponent_last_move == axl.Action.C:
          core_action = axl.Action.C
      else:
          opp_coop_rate = opponent.history.cooperations / len(opponent.history)
          core_action = self._random.random_choice(min(self.c_after_d_prob, opp_coop_rate))

      # Olive branch
      if self.olive_branch_counter >= 50 and self.low_coop_counter == 0:
          self.olive_branch_counter = 0
          return axl.Action.C
      self.olive_branch_counter += 1

      # Cautious mode
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.cautious_mode_counter = 10
      if self.cautious_mode_counter > 0:
          self.cautious_mode_counter -= 1
          return self._random.random_choice(0.1)

      # Periodic adjustments
      if round_number % 100 == 0:
          my_score, opp_score = self.total_scores(self.history, opponent.history)
          my_avg_score = my_score / round_number
          opp_avg_score = opp_score / round_number
          if my_avg_score < opp_avg_score - 1:
              self.c_after_d_prob = max(0.05, self.c_after_d_prob - 0.1)
          elif my_avg_score >= opp_avg_score:
              self.c_after_d_prob = min(opp_coop_rate, self.c_after_d_prob + 0.05)

      # Cooperation success rate check
      if self.successful_cooperations < 0.2 * round_number:
          self.c_after_d_prob /= 2
          self.olive_branch_counter = 0
          self.low_coop_counter = 20
      if self.low_coop_counter > 0:
          self.low_coop_counter -= 1

      return core_action

# Certainly. Here's a rewritten strategy that incorporates the feedback and
# clearly outlines the conditions for cooperation and defection:  1. Start by
# playing C (cooperate) in the first round.  2. For all subsequent rounds,
# evaluate the following conditions in order:     a. If the opponent has
# defected in 2 or more of the last 3 rounds:       - Play D (defect)     b.
# Otherwise, if it's a multiple of 50th round (i.e., round 50, 100, 150, etc.):
# - Calculate the ratio of C to D plays by your opponent in the last 50 rounds
# - If they've played C more than 60% of the time, play C       - If they've
# played D more than 60% of the time, play D       - If their C/D ratio is
# between 40% and 60%, mirror their last move     c. If none of the above
# conditions are met:       - Mirror the opponent's last move (play C if they
# played C, play D if they played D)  3. Repeat step 2 for all rounds, including
# the final rounds of the game.  This strategy: - Starts cooperatively to
# encourage mutual cooperation - Quickly punishes short streaks of defection to
# discourage exploitation - Adapts to longer-term behavior every 50 rounds -
# Maintains neutrality by primarily mirroring the opponent's moves - Treats all
# rounds equally, including the end game - Is simple and easy to implement -
# Clearly defines when to cooperate or defect based on specific conditions  This
# approach should perform well against a variety of opponent strategies while
# maintaining a generally neutral stance.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      if len(self.history) >= 3:
          last_three = opponent.history[-3:]
          if last_three.count(axl.Action.D) >= 2:
              return axl.Action.D

      if len(self.history) % 50 == 0:
          COOPERATION_THRESHOLD = 0.6
          DEFECTION_THRESHOLD = 0.4
          last_fifty = opponent.history[-50:]
          c_ratio = last_fifty.count(axl.Action.C) / len(last_fifty)
          if c_ratio > COOPERATION_THRESHOLD:
              return axl.Action.C
          elif c_ratio < DEFECTION_THRESHOLD:
              return axl.Action.D
          else:
              return opponent.history[-1]

      return opponent.history[-1]

# Certainly. Here's a revised, clearer strategy that incorporates the feedback:
# 1. Start the game with a baseline strategy of playing Defect (D) 80% of the
# time and Cooperate (C) 20% of the time.  2. For each round, determine your
# move in the following order:     a. If it's one of the last 100 rounds
# (901-1000), play D 95% of the time and C 5% of the time.        b. If the
# opponent has played the same move (either C or D) for the last 3 consecutive
# rounds, play D for this round.        c. If you're at a multiple of 50 rounds
# (50, 100, 150, etc.), reassess the opponent's recent strategy:       - If
# they've cooperated more than 60% of the time in the last 50 rounds, play D 90%
# of the time for the next 50 rounds.       - If they've defected more than 80%
# of the time in the last 50 rounds, play D 95% of the time for the next 50
# rounds.       - Otherwise, maintain the baseline 80% D, 20% C ratio for the
# next 50 rounds.        d. If none of the above conditions are met, stick to
# the current D/C ratio as determined by the most recent reassessment.  3. When
# the strategy calls for playing D or C a certain percentage of the time, use a
# random number generator to make the decision for each individual round,
# ensuring the specified probability over time.  This strategy: - Maintains an
# overall aggressive stance - Adapts to the opponent's behavior every 50 rounds
# - Exploits obvious patterns in the opponent's play - Becomes more aggressive
# in the endgame - Is simpler and clearer than the original proposal - Avoids
# unreachable conditions or complex initial phases - Provides a clear hierarchy
# for decision-making in each round  The strategy should perform well against a
# variety of opponent behaviors while maintaining its aggressive nature. It's
# adaptable enough to exploit cooperative opponents and protect against highly
# aggressive ones, while still leaving room for occasional cooperation to
# potentially trigger reciprocity.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.baseline_defect_prob = 0.8
          self.current_defect_prob = self.baseline_defect_prob

      round_number = len(self.history) + 1

      # Last 100 rounds (901-1000)
      if 900 < round_number <= 1000:
          return self._random.random_choice(0.95)

      # Check for opponent's last 3 moves
      if len(opponent.history) >= 3 and len(set(opponent.history[-3:])) == 1:
          return axl.Action.D

      # Reassess every 50 rounds, including round 50
      if round_number % 50 == 0 and round_number >= 50:
          last_50_opponent_moves = opponent.history[-50:]
          opponent_coop_ratio = last_50_opponent_moves.count(axl.Action.C) / 50

          if opponent_coop_ratio > 0.6:
              self.current_defect_prob = 0.9
          elif opponent_coop_ratio < 0.2:  # This is equivalent to defecting more than 80%
              self.current_defect_prob = 0.95
          else:
              self.current_defect_prob = self.baseline_defect_prob

      # self._random.random_choice(p) returns Defect with probability p
      return self._random.random_choice(self.current_defect_prob)

# Here's a revised strategy taking into account the feedback:  1. Start with the
# sequence C, C, C, D to probe the opponent's initial behavior.  2. For the rest
# of the game, use the following decision process in order:     a. If it's one
# of the last 10 rounds of the game, mirror your opponent's previous move
# exactly.     b. If you're in a mutual defection cycle (D-D) for 3 or more
# consecutive rounds:       - Play C with a 50% probability       - Otherwise,
# continue with the steps below     c. Assess the opponent's cooperation rate
# over the last 20 moves:       - If their cooperation rate is above 80%, play C
# - If their cooperation rate is below 20%, play D       - Otherwise, continue
# with the steps below     d. Check if the opponent's last move was C:       -
# If yes, play C       - If no, continue with the step below     e. Play a
# "generous tit-for-tat" move:       - Play C with a probability equal to the
# opponent's overall cooperation rate       - Otherwise, play D  3. After each
# move, update your records of:    - The opponent's overall cooperation rate
# - The opponent's last 20 moves    - The current streak of mutual defections
# (if any)  This strategy maintains simplicity while addressing the main points
# of feedback:  - It starts with a probing sequence to gauge the opponent's
# initial strategy. - It uses adaptive probabilities based on the opponent's
# cooperation rate. - It implements a sliding window (last 20 moves) for
# continuous evaluation. - It has a specific end-game strategy. - It has a more
# nuanced approach to breaking out of mutual defection cycles. - It maintains a
# cooperative bias while protecting against consistent defection. - It avoids
# complex pattern recognition while still adapting to the opponent's overall
# behavior.  The strategy remains fundamentally cooperative but includes
# mechanisms to protect against exploitation and adapt to various opponent
# behaviors.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.opponent_cooperation_rate = 0
          self.opponent_last_20_moves = []
          self.last_20_cooperations = 0
          self.mutual_defection_streak = 0

      if len(self.history) < 4:
          return [axl.Action.C, axl.Action.C, axl.Action.C, axl.Action.D][len(self.history)]

      # Update opponent's cooperation rate
      self.opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)

      # Update opponent's last 20 moves
      if len(self.opponent_last_20_moves) == 20:
          if self.opponent_last_20_moves.pop(0) == axl.Action.C:
              self.last_20_cooperations -= 1
      self.opponent_last_20_moves.append(opponent.history[-1])
      if opponent.history[-1] == axl.Action.C:
          self.last_20_cooperations += 1

      # Update mutual defection streak
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.mutual_defection_streak += 1
      elif opponent.history[-1] == axl.Action.C:
          self.mutual_defection_streak = 0

      # Last 10% of rounds
      if len(self.history) >= 0.9 * self.match_attributes['length']:
          return opponent.history[-1]

      # Break mutual defection cycle
      if self.mutual_defection_streak >= 3:
          return self._random.random_choice(0.5)

      # Assess opponent's recent cooperation rate
      recent_coop_rate = self.last_20_cooperations / len(self.opponent_last_20_moves)
      if recent_coop_rate > 0.8:
          return axl.Action.C
      elif recent_coop_rate < 0.2:
          return axl.Action.D

      # Check opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # Generous Tit-for-Tat
      return self._random.random_choice(self.opponent_cooperation_rate)

# Certainly. Here's a revised strategy that takes into account the feedback and
# clearly outlines the conditions for cooperation and defection:  1. Start by
# playing C (cooperate) in the first round.  2. For each subsequent round,
# follow these steps in order:     a. Calculate the opponent's cooperation rate
# over the last 20 moves (or all previous moves if fewer than 20).     b.
# Determine the round number (1 to 1000).     c. If it's one of the last 50
# rounds (951-1000):       - Adjust the lower threshold: 30% + (round number -
# 950) * 0.8%       - Adjust the upper threshold: 70% - (round number - 950) *
# 0.8%     d. Otherwise, use fixed thresholds:       - Lower threshold: 30%
# - Upper threshold: 70%     e. Make a decision:       - If the opponent's
# cooperation rate is above the upper threshold, play C.       - If the
# opponent's cooperation rate is below the lower threshold, play D.       - If
# the opponent's cooperation rate is between the thresholds, mirror their last
# move.     f. With a 5% chance, regardless of the above decision, randomly
# choose to play C or D instead.  3. Play the move determined by step 2.  This
# strategy is simpler and clearer about when it will cooperate or defect. It
# maintains a neutral stance by mirroring behavior when the opponent's
# cooperation rate is moderate, while adapting to more extreme behaviors. The
# gradual threshold adjustment in the final rounds provides a smoother end-game
# strategy. The small random element adds unpredictability to prevent
# exploitation by pattern-recognizing opponents.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      round_number = len(self.history) + 1
      recent_history = opponent.history[-20:] if len(opponent.history) >= 20 else opponent.history
      coop_rate = recent_history.cooperations / len(recent_history) if recent_history else 0

      if round_number > 950:
          lower_threshold = 0.3 + (round_number - 950) * 0.008
          upper_threshold = 0.7 - (round_number - 950) * 0.008
      else:
          lower_threshold = 0.3
          upper_threshold = 0.7

      if self._random.random() < 0.05:
          return self._random.random_choice()

      if coop_rate > upper_threshold:
          return axl.Action.C
      elif coop_rate < lower_threshold:
          return axl.Action.D
      else:
          return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing D (defect) for the first 5 rounds.  2. For the remaining 995 rounds,
# follow these rules in order:     a. If it's a multiple of 100th round (100,
# 200, 300, etc.), play C (cooperate). This periodic cooperation allows for
# potential mutual cooperation without being too exploitable.     b. If the
# opponent has played C for the last 3 consecutive rounds, play C. This rewards
# consistent cooperation from the opponent.     c. If the opponent played D in
# the last round, play D. This punishes defection and protects against
# exploitation.     d. If none of the above conditions are met, play D with 80%
# probability and C with 20% probability. This maintains an overall aggressive
# stance while allowing for some unpredictability and occasional cooperation.
# This strategy is simpler and clearer, while still maintaining an aggressive
# approach. It adapts to the opponent's recent behavior, periodically allows for
# cooperation, and is less exploitable than the previous version. The conditions
# are ordered to prioritize periodic cooperation attempts, reward consistent
# cooperation, protect against defection, and default to a mostly aggressive
# stance.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if len(self.history) < 5:
          return axl.Action.D

      if len(self.history) % 100 == 99:
          return axl.Action.C

      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C

      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      return self._random.random_choice(0.2)

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing Cooperate (C) for the first round.  2. For each subsequent round,
# evaluate the following conditions in order:     a. If you're in the last 20
# rounds of the game (rounds 981-1000):       - Play C if the opponent's
# cooperation rate in the last 50 rounds is 60% or higher.       - Otherwise,
# play D.     b. If the opponent has played D for 5 consecutive rounds:       -
# Play D for the next 3 rounds, then continue with the strategy.     c.
# Calculate the opponent's overall cooperation rate (OCR) for all previous
# rounds.     d. If the opponent played C in the previous round:       - Play C.
# e. If the opponent played D in the previous round:       - Play C with a
# probability of OCR + 10% (capped at 90%).       - Play D with the remaining
# probability.     f. If none of the above conditions are met (which should be
# rare):       - Play C.  3. Every 50 rounds, perform the following analysis:
# - If the opponent's cooperation rate in the last 50 rounds is:      - Above
# 90%: Increase your cooperation probability by 5% for the next 50 rounds.
# - Below 40%: Decrease your cooperation probability by 5% for the next 50
# rounds.      - Between 40% and 90%: No change.    - These adjustments are
# cumulative but capped at +/- 15% from the base probabilities.  This revised
# strategy addresses the previous critiques by: 1. Remaining simple and
# generally cooperative. 2. Eliminating ambiguous conditions. 3. Adapting to the
# opponent's overall behavior through the OCR. 4. Providing a more nuanced
# response to different levels of cooperation/defection. 5. Removing the
# exploitable always-cooperate behavior in the final rounds. 6. Implementing a
# sliding scale for adjusting cooperation probabilities.  The strategy remains
# cooperative but is more adaptive to various opponent behaviors. It's designed
# to encourage cooperation while being able to protect against consistent
# defection and respond to changes in the opponent's strategy over time.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.cooperation_adjustment = 0
          self.defect_counter = 0
          return axl.Action.C

      if len(self.history) >= 981:
          opponent_coop_rate = opponent.history[-50:].count(axl.Action.C) / 50
          return axl.Action.C if opponent_coop_rate >= 0.6 else axl.Action.D

      if len(opponent.history) >= 5 and all(move == axl.Action.D for move in opponent.history[-5:]):
          self.defect_counter = 3
      if self.defect_counter > 0:
          self.defect_counter -= 1
          return axl.Action.D

      ocr = opponent.history.cooperations / len(opponent.history)

      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      if opponent.history[-1] == axl.Action.D:
          coop_prob = min(0.9, ocr + 0.1 + self.cooperation_adjustment)
          return self._random.random_choice(coop_prob)

      if len(self.history) % 50 == 0:
          opponent_coop_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if opponent_coop_rate > 0.9:
              self.cooperation_adjustment = min(0.15, self.cooperation_adjustment + 0.05)
          elif opponent_coop_rate < 0.4:
              self.cooperation_adjustment = max(-0.15, self.cooperation_adjustment - 0.05)

      return axl.Action.C

# Here's the revised strategy, taking into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. For each subsequent round,
# follow these rules in order:     a. If it's one of the last 10 rounds
# (991-1000), play D (defect).        b. If it's a multiple of 50 rounds (50,
# 100, 150, etc.), play C as a forgiveness mechanism.        c. Calculate the
# opponent's cooperation rate over the last 20 moves.        d. If the
# cooperation rate is below 40%:       - If the opponent has defected in the
# last two consecutive moves, play D.       - Otherwise, play C.        e. If
# the cooperation rate is 40% or above:       - Play whatever the opponent
# played in the previous round (Tit-for-Tat).  3. If none of the above
# conditions are met (which should never happen, but just in case), play C.
# This strategy maintains neutrality while being simpler and more adaptive. It
# clearly defines when to cooperate or defect based on the opponent's recent
# behavior and the stage of the game. The order of conditions ensures that end-
# game behavior and periodic forgiveness take precedence, followed by adaptive
# play based on the opponent's cooperation rate.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if len(self.history) == 0:
          return axl.Action.C

      current_round = len(self.history) + 1

      if current_round > 990:
          return axl.Action.D

      if current_round % 50 == 0:
          return axl.Action.C

      last_20_moves = opponent.history[-20:]
      cooperation_rate = last_20_moves.count(axl.Action.C) / len(last_20_moves) if len(last_20_moves) > 0 else 1

      if cooperation_rate < 0.4:
          if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
          else:
              return axl.Action.C

      if cooperation_rate >= 0.4:
          return opponent.history[-1]

      return axl.Action.C

# Here's a revised, simplified, and more effective aggressive strategy, taking
# into account the feedback:  1. Initial Phase (First 5 rounds): Always Defect
# (D) to establish an aggressive stance.  2. Main Phase (Rounds 6-995):    a.
# Defect (D) if ANY of these conditions are true:       - The opponent defected
# in either of the last two rounds       - It's a "probe round" (every 10th
# round, to maintain unpredictability)       - Random defection triggered (10%
# chance each round)     b. Cooperate (C) if ALL of these conditions are true:
# - The opponent cooperated in the last two rounds       - It's not a "probe
# round"       - Random defection was not triggered  3. Punishment Phase:    If
# the opponent defects three or more times in any five-round window, enter a
# punishment phase:    - Defect (D) for the next three rounds, regardless of the
# opponent's moves    - After these three rounds, return to the Main Phase rules
# 4. End Game (Last 5 rounds): Always Defect (D) to maximize final payoff  This
# strategy operates as follows: - It starts aggressively and maintains a bias
# towards defection throughout the game. - It quickly punishes defection but
# allows for the possibility of returning to cooperation. - It incorporates
# unpredictability through probe rounds and random defections. - It simplifies
# decision-making by having clear, prioritized conditions for defection and
# cooperation. - It ends with a short all-defection phase to capitalize on end-
# game dynamics.  This revised strategy addresses the main points of feedback: -
# It's simpler and easier to implement while remaining aggressive. - It removes
# complex elements like the adaptive adjustment. - It shortens the punishment
# phase for faster recovery. - It reduces the end-game defection phase to only
# the last 5 rounds. - It introduces randomness to be less predictable. - It
# maintains a clear bias towards defection while allowing for cooperation when
# the opponent consistently cooperates.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.punishment_counter = 0

      round_number = len(self.history) + 1

      # Initial Phase (First 5 rounds)
      if round_number <= 5:
          return axl.Action.D

      # End Game (Last 5 rounds)
      if round_number > 995:
          return axl.Action.D

      # Punishment Phase
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D

      # Check for entering Punishment Phase
      if len(self.history) >= 5:
          for i in range(len(self.history) - 4):
              recent_defections = opponent.history[i:i+5].count(axl.Action.D)
              if recent_defections >= 3:
                  self.punishment_counter = 3
                  return axl.Action.D

      # Main Phase (Rounds 6-995)
      if (opponent.history[-2:].count(axl.Action.C) != 2 or
          round_number % 10 == 0 or
          self._random.random() < 0.1):
          return axl.Action.D
      return axl.Action.C

# Here's a revised strategy that incorporates the feedback while maintaining
# simplicity and cooperative behavior:  1. Start by playing Cooperate (C) for
# the first round.  2. For subsequent rounds, evaluate the following conditions
# in order:     a. If this is the last 50 rounds of the game, play Cooperate
# (C).        b. If stuck in mutual defection for more than 5 rounds, play
# Cooperate (C) as an "olive branch".        c. If the opponent has defected in
# both of the last two rounds, play Defect (D).        d. If the opponent's
# defection rate over the last 20 rounds exceeds 60%, play whatever the opponent
# played in the previous round (Tit-for-Tat).        e. If none of the above
# conditions are met, play Cooperate (C).  3. Every 100 rounds, regardless of
# the above conditions, play Cooperate (C) as a periodic "olive branch".  4.
# With a 5% probability on any given turn (except for conditions 1, 3, and 2a),
# play Defect (D) instead of the move determined by the above rules. This
# introduces a small element of unpredictability.  This strategy: - Starts
# cooperatively and maintains a generally cooperative stance. - Adapts to
# aggressive opponents by matching their behavior when necessary. - Offers
# frequent opportunities to re-establish cooperation. - Protects against end-
# game exploitation. - Introduces a small degree of unpredictability to probe
# opponent strategies. - Simplifies the decision-making process while addressing
# the main weaknesses of the previous version.  The order of conditions ensures
# that the strategy responds appropriately to different game states and opponent
# behaviors, prioritizing cooperation and protection against exploitation. The
# strategy remains relatively simple while incorporating key improvements
# suggested in the feedback.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.mutual_defection_count = 0
          return axl.Action.C

      if len(self.history) % 100 == 0:
          return axl.Action.C

      if len(self.history) >= 950:
          return axl.Action.C

      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.mutual_defection_count += 1
      else:
          self.mutual_defection_count = 0

      if self.mutual_defection_count > 5:
          return axl.Action.C

      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D

      if len(opponent.history) >= 20:
          defection_rate = opponent.history[-20:].count(axl.Action.D) / 20
          if defection_rate > 0.6:
              return opponent.history[-1]

      if self._random.random() < 0.05:
          return axl.Action.D

      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) in the first round.  2. For subsequent rounds, follow
# these rules in order:     a. If it's the final (1000th) round, play Defect
# (D).     b. If the opponent has played D for the last 3 consecutive rounds,
# play D.     c. If the opponent's overall cooperation rate (total C moves /
# total moves) is below 30%, play D.     d. If the last round was a mutual
# defection (D,D), there's a 5% chance to play C. If this results in (C,D),
# reduce this forgiveness chance to 1% for the next 10 rounds.     e. Every 5
# rounds, evaluate the opponent's behavior in those 5 rounds:       - If they've
# cooperated 4-5 times, play Tit-for-Tat (copy opponent's last move).       - If
# they've cooperated 2-3 times, play Tit-for-Tat with a 10% chance of D when the
# opponent's last move was C.       - If they've cooperated 0-1 times, play Tit-
# for-Tat with a 20% chance of D when the opponent's last move was C.     f. If
# none of the above conditions are met, play Tit-for-Tat (copy opponent's last
# move).  This strategy maintains simplicity while incorporating the key
# improvements: - It starts cooperatively but has mechanisms to protect against
# exploitation. - It adapts quickly to the opponent's recent behavior (5-round
# evaluations). - It considers the opponent's overall behavior (cooperation
# rate). - It includes a simple forgiveness mechanism that becomes more cautious
# if exploited. - It protects against end-game exploitation by defecting in the
# final round.  The rules are ordered to prioritize protection against
# consistent defection, then consider overall opponent behavior, then recent
# behavior, and finally default to Tit-for-Tat. This order ensures that the
# strategy responds appropriately to different opponent behaviors while
# maintaining a generally neutral stance.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.forgiveness_chance = 0.05
          self.forgiveness_countdown = 0
          return axl.Action.C

      # Final round
      if len(self.history) == 999:
          return axl.Action.D

      # Opponent defected last 3 rounds
      if opponent.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.D

      # Opponent's overall cooperation rate below 30%
      if opponent.cooperations / len(opponent.history) < 0.3:
          return axl.Action.D

      # Forgiveness mechanism
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          if self._random.random() < self.forgiveness_chance:
              if self.forgiveness_chance == 0.05:
                  self.forgiveness_chance = 0.01
                  self.forgiveness_countdown = 10
              return axl.Action.C

      if self.forgiveness_countdown > 0:
          self.forgiveness_countdown -= 1
          if self.forgiveness_countdown == 0:
              self.forgiveness_chance = 0.05

      # 5-round evaluation
      if len(self.history) % 5 == 0:
          recent_cooperations = opponent.history[-5:].count(axl.Action.C)
          if recent_cooperations >= 4:
              return opponent.history[-1]
          elif recent_cooperations >= 2:
              return self._random.random_choice(0.9) if opponent.history[-1] == axl.Action.C else axl.Action.D
          else:
              return self._random.random_choice(0.8) if opponent.history[-1] == axl.Action.C else axl.Action.D

      # Default to Tit-for-Tat
      return opponent.history[-1]

# Certainly. Here's a revised, clearer strategy that incorporates the feedback:
# 1. Start by playing D (Defect) for the first 5 rounds.  2. After the first 5
# rounds, maintain a rolling count of the opponent's C (Cooperate) plays in the
# last 20 moves. Update this count after each round.  3. For each round from the
# 6th to the 975th, make decisions in the following order:     a. If it's the
# last move of every 10-round block (i.e., round number mod 10 = 0), there's a
# 20% chance to play the opposite of what the following rules would suggest. If
# this condition triggers, ignore the rest of the rules and play the opposite
# move.        b. If the opponent has played C for the last 5 consecutive
# rounds, play D for this round and the next.        c. If the opponent's C
# count in the last 20 moves is 14 or higher (70% or more), play C.        d. In
# all other cases, play D.  4. For the last 25 rounds (rounds 976-1000), always
# play D.  This strategy: - Starts aggressively with 5 rounds of defection. -
# Primarily defects unless the opponent shows a high rate of cooperation. -
# Includes unpredictability through occasional random moves. - Probes for
# exploitability when the opponent seems consistently cooperative. - Ends with
# aggressive defection.  The strategy is simple, with clear conditions for
# cooperation and defection. It maintains an overall aggressive stance while
# allowing for cooperation with consistently cooperative opponents. The order of
# conditions ensures that the unpredictability factor and exploitation of highly
# cooperative opponents take precedence over the general cooperation threshold.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.next_move = None

      if len(self.history) < 5:
          return axl.Action.D

      if len(self.history) >= 975:
          return axl.Action.D

      recent_history = opponent.history[-20:] if len(opponent.history) >= 20 else opponent.history[:]
      cooperation_rate = recent_history[-20:].count(axl.Action.C) / len(recent_history)

      if self.next_move is not None:
          proposed_move = self.next_move
          self.next_move = None
      elif all(move == axl.Action.C for move in opponent.history[-5:]):
          self.next_move = axl.Action.D
          proposed_move = axl.Action.D
      elif cooperation_rate >= 0.7:
          proposed_move = axl.Action.C
      else:
          proposed_move = axl.Action.D

      if len(self.history) % 10 == 0 and self._random.random() < 0.2:
          proposed_move.flip()
          if self.next_move:
              self.next_move.flip()

      return proposed_move

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing Cooperate (C) for the first round.  2. For rounds 2-5, use Tit-for-Tat
# (mirror your opponent's previous move).  3. From round 6 onwards, use the
# following rules in order:     a. If you're in a mutual defection cycle for
# more than 10 rounds, play C to attempt breaking the cycle.        b. If your
# opponent has cooperated in the last 3 rounds, play C.        c. If your
# opponent has defected in the last 3 rounds, play D.        d. If your
# opponent's last 3 moves were mixed:       - Calculate their overall
# cooperation rate throughout the game.       - Play C with a probability equal
# to their cooperation rate.  4. Forgiveness rule: If the opponent has been
# defecting but then cooperates twice in a row, immediately play C on the next
# move.  5. Exploitation protection: If at any point your average score per
# round falls below 2 (which is less than the mutual cooperation payoff), switch
# to always playing D for the next 10 rounds, then return to the main strategy.
# 6. Long-term memory: Every 50 rounds, recalculate the opponent's overall
# cooperation rate. If it's above 70%, play C for the next round regardless of
# recent moves.  7. End-game adjustment: In the last 10 rounds, continue with
# the main strategy but decrease the probability of cooperation by 10% each
# round. This makes end-game defection less predictable while still protecting
# against exploitation.  This revised strategy maintains a cooperative approach
# while addressing the critiques: - It's still relatively simple and primarily
# cooperative. - It clarifies behavior in early rounds. - It adapts better to
# various opponent strategies by considering overall cooperation rates. - It
# includes a forgiveness mechanism to break defection cycles. - It has a more
# flexible end-game approach. - It uses probabilistic decisions to be less
# predictable. - It maintains long-term memory of the opponent's behavior.  The
# strategy will cooperate in situations where the opponent shows consistent
# cooperation or when trying to reestablish cooperation after defection cycles.
# It will defect when the opponent shows consistent defection, when protecting
# against exploitation, or with increasing probability in the end-game. In mixed
# situations, it uses probabilistic decision-making based on the opponent's
# overall behavior.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.mutual_defection_count = 0
          self.exploitation_protection = 0
          return axl.Action.C

      if len(self.history) < 5:
          return opponent.history[-1]

      if self.score / len(self.history) < 2:
          self.exploitation_protection = 10
          return axl.Action.D

      if self.exploitation_protection > 0:
          self.exploitation_protection -= 1
          return axl.Action.D

      if len(self.history) >= 10 and all(move == axl.Action.D for move in self.history[-10:]) and all(move == axl.Action.D for move in opponent.history[-10:]):
          self.mutual_defection_count += 1
          if self.mutual_defection_count > 10:
              self.mutual_defection_count = 0
              return axl.Action.C
      else:
          self.mutual_defection_count = 0

      if all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C

      if all(move == axl.Action.D for move in opponent.history[-3:]):
          return axl.Action.D

      if opponent.history[-2:] == [axl.Action.C, axl.Action.C] and self.history[-1] == axl.Action.D:
          return axl.Action.C

      if len(self.history) % 50 == 0:
          if opponent.cooperations / len(opponent.history) > 0.7:
              return axl.Action.C

      if len(self.history) >= 990:
          rounds_left = 1000 - len(self.history)
          cooperation_probability = max(0, 1 - (0.1 * (10 - rounds_left)))
          return self._random.random_choice(cooperation_probability)

      if len(set(opponent.history[-3:])) > 1:
          opponent_cooperation_rate = opponent.cooperations / len(opponent.history)
          return self._random.random_choice(opponent_cooperation_rate)

      return opponent.history[-1]  # Tit-for-Tat as default

# Here's a rewritten strategy that takes into account the feedback, with clear
# conditions for cooperation and defection:  1. Start by playing C (cooperate)
# in the first round.  2. For each subsequent round, evaluate the following
# conditions in order:     a. If the opponent has defected in the last 3
# consecutive rounds, play D (defect).        b. If there have been 2
# consecutive rounds of mutual defection (both you and the opponent played D),
# play C to attempt to break the cycle.        c. Calculate the rolling average
# of the opponent's last 10 moves:       - If the average shows 7 or more
# cooperations (70% or higher), play C.       - If the average shows 7 or more
# defections (70% or higher), play D.        d. If none of the above conditions
# are met, play Tit-for-Tat (copy the opponent's last move).  3. Repeat step 2
# for all remaining rounds of the game.  This strategy aims to: - Start
# cooperatively - Respond quickly to aggressive behavior - Attempt to break
# cycles of mutual defection - Adapt to the opponent's recent behavior - Default
# to a neutral Tit-for-Tat strategy when the opponent's behavior is mixed  The
# strategy is simple, maintains neutrality, and should be responsive to changes
# in the opponent's behavior without being overly complex or exploitable.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C

      opponent_history_len = len(opponent.history)
      self_history_len = len(self.history)

      if opponent_history_len >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          return axl.Action.D

      if self_history_len >= 2 and opponent_history_len >= 2:
          if all(move == axl.Action.D for move in self.history[-2:]) and all(move == axl.Action.D for move in opponent.history[-2:]):
              return axl.Action.C

      if opponent_history_len > 0:
          last_n = min(10, opponent_history_len)
          opponent_last_n = opponent.history[-last_n:]
          cooperation_rate = opponent_last_n.count(axl.Action.C) / last_n
          if cooperation_rate >= 0.7:
              return axl.Action.C
          elif cooperation_rate <= 0.3:
              return axl.Action.D

      return opponent.history[-1]
