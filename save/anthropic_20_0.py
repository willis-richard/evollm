import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Aggressive Strategy:  This strategy focuses on maximizing personal gain
# through frequent defection while exploiting any cooperative tendencies of the
# opponent. Here's how it works:  1. Start by defecting (D) for the first three
# moves to establish dominance.  2. For subsequent moves:    a. If the opponent
# has cooperated in any of the last three moves, defect to exploit their
# cooperation.    b. If the opponent has defected for three consecutive moves,
# cooperate once to test if they can be manipulated into cooperating, then
# immediately revert to defection.  3. Keep a running tally of the opponent's
# moves:    a. If the opponent's cooperation rate exceeds 40%, increase
# defection frequency to 90% for the next 20 moves to capitalize on their
# cooperative tendency.    b. If the opponent's cooperation rate falls below
# 20%, occasionally cooperate (20% of the time) to entice them into cooperating
# more often.  4. Every 100 moves, perform a "probing" sequence:    a. Cooperate
# for two consecutive moves, regardless of the opponent's actions.    b. If the
# opponent cooperates in response, immediately defect for the next five moves to
# exploit this cooperation.  5. In the last 50 moves of the game:    a. If the
# opponent's overall cooperation rate is above 30%, always defect to maximize
# final score.    b. If the opponent's cooperation rate is below 30%, alternate
# between cooperation and defection in an unpredictable pattern to confuse them
# and potentially gain an advantage.  This aggressive strategy aims to
# consistently outperform the opponent by exploiting cooperation, establishing
# dominance through defection, and adapting to the opponent's behavior to
# maximize personal gain.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.move_counter = 0
          self.last_probe = -100
          self.exploit_cooperation = 0
          self.opponent_coop_rate = 0

      self.move_counter += 1

      # Start with defection for the first three moves
      if self.move_counter <= 3:
          return axl.Action.D

      # Calculate opponent's cooperation rate
      total_moves = len(opponent.history)
      self.opponent_coop_rate = opponent.history.cooperations / total_moves if total_moves > 0 else 0

      # Probing sequence every 100 moves
      if self.move_counter - self.last_probe >= 100:
          self.last_probe = self.move_counter
          if self.move_counter % 100 <= 1:  # Two consecutive cooperations
              return axl.Action.C
          elif self.move_counter % 100 <= 6:  # Five defections if opponent cooperated
              return axl.Action.D

      # Last 50 moves strategy
      if self.match_attributes['length'] - self.move_counter < 50:
          if self.opponent_coop_rate > 0.3:
              return axl.Action.D
          else:
              return axl.Action.C if self._random.random() < 0.5 else axl.Action.D

      # Main strategy
      last_three_opponent_moves = opponent.history[-3:]

      if axl.Action.C in last_three_opponent_moves:
          return axl.Action.D

      if all(move == axl.Action.D for move in last_three_opponent_moves):
          if self.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C

      # Adjust strategy based on opponent's cooperation rate
      if self.opponent_coop_rate > 0.4:
          if self.exploit_cooperation < 20:
              self.exploit_cooperation += 1
              return axl.Action.D if self._random.random() < 0.9 else axl.Action.C
      elif self.opponent_coop_rate < 0.2:
          return axl.Action.C if self._random.random() < 0.2 else axl.Action.D

      # Default to defection
      return axl.Action.D

# Cooperative Strategy:  This strategy focuses on fostering mutual cooperation
# and building trust, while incorporating some protective measures against
# persistent defectors. Here's how it works:  1. Start by cooperating (C) for
# the first five moves to establish a cooperative tone.  2. For subsequent
# moves:    a. If the opponent has cooperated in the previous move, always
# cooperate.    b. If the opponent has defected in the previous move, still
# cooperate with an 80% probability to encourage a return to cooperation.  3.
# Implement a "forgiveness" mechanism:    a. Even if the opponent has defected
# multiple times in a row, cooperate with a 50% probability every fifth move to
# offer an olive branch.  4. Keep track of the opponent's cooperation rate:
# a. If the opponent's cooperation rate remains above 70%, always cooperate to
# maintain the mutually beneficial relationship.    b. If the cooperation rate
# falls below 30%, switch to a tit-for-tat strategy for the next 20 moves before
# attempting to reset to the cooperative approach.  5. Every 100 moves, perform
# a "trust-building" sequence:    a. Cooperate for five consecutive moves,
# regardless of the opponent's actions, to demonstrate commitment to
# cooperation.  6. In the last 100 moves of the game:    a. If the opponent's
# overall cooperation rate is above 60%, always cooperate to maximize mutual
# benefit.    b. If the opponent's cooperation rate is below 40%, switch to a
# tit-for-tat strategy to protect against last-minute exploitation.  7. Include
# a "goodwill" gesture by cooperating on the very last move, regardless of the
# opponent's previous action.  This cooperative strategy aims to establish and
# maintain a mutually beneficial relationship based on trust and cooperation,
# while incorporating some protective measures against persistent defectors. It
# prioritizes long-term mutual gain over short-term personal advantage.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.move_counter = 0
          self.tit_for_tat_counter = 0
          self.last_trust_building = 0

      self.move_counter += 1

      # Start with cooperation for the first five moves
      if self.move_counter <= 5:
          return axl.Action.C

      opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history) if opponent.history else 1

      # Trust-building sequence every 100 moves
      if self.move_counter - self.last_trust_building >= 100:
          if self.move_counter - self.last_trust_building < 105:
              return axl.Action.C
          else:
              self.last_trust_building = self.move_counter

      # Last 100 moves strategy
      if len(self.history) >= 900:
          if opponent_cooperation_rate > 0.6:
              return axl.Action.C
          elif opponent_cooperation_rate < 0.4:
              return opponent.history[-1]  # Tit-for-tat

      # Tit-for-tat period
      if self.tit_for_tat_counter > 0:
          self.tit_for_tat_counter -= 1
          return opponent.history[-1]

      # Main strategy logic
      if opponent_cooperation_rate > 0.7:
          return axl.Action.C
      elif opponent_cooperation_rate < 0.3:
          self.tit_for_tat_counter = 20
          return opponent.history[-1]

      # Forgiveness mechanism
      if self.move_counter % 5 == 0 and opponent.history[-1] == axl.Action.D:
          if self._random.random() < 0.5:
              return axl.Action.C

      # Respond to opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.C if self._random.random() < 0.8 else axl.Action.D

      # Goodwill gesture on the last move
      if self.move_counter == 1000:
          return axl.Action.C

# Neutral Strategy:  This strategy aims to balance cooperation and defection
# based on the opponent's behavior. It starts by cooperating and then follows a
# tit-for-tat approach with a slight bias towards cooperation. Here's how it
# works:  1. Begin by cooperating (C) for the first move.  2. For subsequent
# moves:    a. If the opponent cooperated in the previous round, cooperate with
# a 90% probability and defect with a 10% probability.    b. If the opponent
# defected in the previous round, defect with a 60% probability and cooperate
# with a 40% probability.  3. Every 50 moves, perform a "forgiveness" action:
# a. If the opponent has defected more than cooperated in the last 50 moves,
# still cooperate with a 30% probability to allow for potential reconciliation.
# 4. Keep track of the overall cooperation rate of the opponent. If it falls
# below 25%, increase the defection probability to 80% for the next 20 moves
# before reverting to the standard strategy.  5. In the last 50 moves of the
# game, if the opponent's cooperation rate is above 60%, always cooperate to
# maximize mutual benefit. If it's below 40%, always defect to protect against
# exploitation.  This neutral strategy aims to adapt to the opponent's behavior
# while maintaining a balance between cooperation and self-protection, with a
# slight preference for fostering cooperation when possible.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize cooperation counts if not already set
      if not self.history:
          self.opponent_cooperations = 0
          self.move_count = 0
          self.defection_streak = 0

      # First move: cooperate
      if len(self.history) == 0:
          return axl.Action.C

      self.move_count += 1

      # Update opponent's cooperation count
      if opponent.history[-1] == axl.Action.C:
          self.opponent_cooperations += 1

      # Calculate opponent's cooperation rate
      opponent_coop_rate = self.opponent_cooperations / len(opponent.history)

      # Last 50 moves strategy
      if len(self.history) >= 950:
          if opponent_coop_rate > 0.6:
              return axl.Action.C
          elif opponent_coop_rate < 0.4:
              return axl.Action.D

      # Increased defection probability if opponent's cooperation rate is low
      if opponent_coop_rate < 0.25:
          self.defection_streak += 1
          if self.defection_streak <= 20:
              return axl.Action.D if self._random.random() < 0.8 else axl.Action.C
      else:
          self.defection_streak = 0

      # Forgiveness action every 50 moves
      if self.move_count % 50 == 0:
          recent_opponent_defections = sum(1 for action in opponent.history[-50:] if action == axl.Action.D)
          if recent_opponent_defections > 25 and self._random.random() < 0.3:
              return axl.Action.C

      # Standard strategy based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C if self._random.random() < 0.9 else axl.Action.D
      else:
          return axl.Action.D if self._random.random() < 0.6 else axl.Action.C

# Aggressive Strategy:  This strategy aims to maximize personal gain by
# exploiting the opponent and capitalizing on any weakness. Here's how it works:
# 1. Start by playing D (defect) from the first round to establish dominance and
# gain an early advantage.  2. Consistently play D for the majority of the game,
# regardless of the opponent's moves, to maximize potential gains.  3. If the
# opponent plays C (cooperate), continue playing D to exploit their cooperation
# and gain the maximum payoff of 5.  4. If the opponent switches to D, maintain
# the defection strategy to avoid the lowest payoff and secure at least 1 point
# per round.  5. Implement a "false cooperation" tactic:    - Occasionally play
# C (about 10-15% of the time) to confuse the opponent and potentially lure them
# into cooperating.    - Immediately follow any C play with multiple D plays to
# exploit any reciprocal cooperation from the opponent.  6. In the last 50-100
# rounds, increase the frequency of D plays to ensure maximum points in the
# endgame.  7. If faced with a consistently cooperating opponent, exploit this
# fully by always playing D.  8. If the opponent seems to be using a tit-for-tat
# or similar reactive strategy, occasionally play C to reset their strategy,
# then immediately return to D to exploit their cooperation.  9. Keep track of
# the opponent's moves and if they show any pattern of predictable behavior,
# adjust the strategy to maximize exploitation of that pattern.  This aggressive
# strategy prioritizes short-term gains and consistent exploitation, aiming to
# accumulate the highest possible score throughout the 1000 rounds, regardless
# of the opponent's strategy.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables
      round_number = len(self.history) + 1
      total_rounds = 1000

      # Start with defection
      if round_number == 1:
          return axl.Action.D

      # Implement false cooperation tactic
      if self._random.random() < 0.15 and round_number < total_rounds - 100:
          return axl.Action.C

      # Increase defection frequency in the last 100 rounds
      if round_number > total_rounds - 100:
          return axl.Action.D

      # Exploit consistently cooperating opponent
      if opponent.history.cooperations / round_number > 0.9:
          return axl.Action.D

      # Reset tit-for-tat like strategies
      if len(self.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          if self._random.random() < 0.2:
              return axl.Action.C

      # Check for patterns in opponent's moves
      if len(opponent.history) >= 5:
          last_five = opponent.history[-5:]
          if last_five.count(axl.Action.C) >= 4:
              return axl.Action.D

      # Default to defection
      return axl.Action.D

# Cooperative Strategy:  This strategy aims to foster mutual cooperation and
# maintain a positive relationship with the opponent. Here's how it works:  1.
# Start by playing C (cooperate) for the first few rounds to signal willingness
# to cooperate.  2. If the opponent consistently cooperates, continue playing C
# to maintain mutual benefit.  3. If the opponent defects, respond with a
# forgiving approach:    - After a single defection, play C in the next round to
# encourage the opponent to return to cooperation.    - If the opponent defects
# twice in a row, play D (defect) once as a warning, then return to C.  4.
# Implement a "forgive and forget" mechanism:    - Keep a running count of the
# opponent's recent cooperation rate.    - If the opponent returns to
# cooperation after a period of defection, gradually increase trust by playing C
# more frequently.  5. In the last few rounds, continue playing C to maintain
# the cooperative spirit, unless the opponent has been consistently defecting.
# 6. Throughout the game, occasionally play C even if the opponent has defected,
# to test if they're willing to return to cooperation.  7. If faced with a
# consistently defecting opponent, reluctantly switch to playing D more often,
# but periodically attempt to reinstate cooperation by playing C.  This strategy
# prioritizes long-term mutual benefit over short-term gains, aiming to
# establish and maintain a cooperative relationship throughout the 1000 rounds.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables if it's the first round
      if len(self.history) == 0:
          self.cooperation_rate = 1.0
          self.defection_streak = 0
          self.forgiveness_threshold = 0.7
          self.test_cooperation_probability = 0.1

      # Start with cooperation for the first few rounds
      if len(self.history) < 5:
          return axl.Action.C

      # Calculate opponent's recent cooperation rate (last 20 moves)
      recent_history = opponent.history[-20:]
      if recent_history:
          recent_cooperation_rate = sum(1 for action in recent_history if action == axl.Action.C) / len(recent_history)
      else:
          recent_cooperation_rate = 1.0

      # Update overall cooperation rate
      self.cooperation_rate = 0.9 * self.cooperation_rate + 0.1 * recent_cooperation_rate

      # Check opponent's last two moves
      if len(opponent.history) >= 2:
          last_two_moves = opponent.history[-2:]
          if all(move == axl.Action.D for move in last_two_moves):
              self.defection_streak += 1
          else:
              self.defection_streak = 0

      # Implement the strategy
      if opponent.history[-1] == axl.Action.C:
          # If opponent cooperated, cooperate
          return axl.Action.C
      elif self.defection_streak == 1:
          # After a single defection, cooperate to encourage cooperation
          return axl.Action.C
      elif self.defection_streak == 2:
          # After two defections, defect once as a warning
          return axl.Action.D
      elif self.cooperation_rate > self.forgiveness_threshold:
          # If opponent has been mostly cooperative, cooperate
          return axl.Action.C
      elif len(self.history) > 990:
          # In the last few rounds, cooperate unless opponent has been consistently defecting
          return axl.Action.C if self.cooperation_rate > 0.3 else axl.Action.D
      elif self._random.random() < self.test_cooperation_probability:
          # Occasionally cooperate to test if opponent is willing to cooperate
          return axl.Action.C
      else:
          # If opponent has been mostly defecting, reluctantly defect
          return axl.Action.D

# Neutral Strategy:  This strategy aims to balance cooperation and competition,
# adapting to the opponent's behavior while maintaining a flexible approach.
# Here's how it works:  1. Start with a mixed approach, alternating between C
# and D for the first few rounds to gauge the opponent's strategy.  2. Implement
# a "reactive adaptation" mechanism:    - Keep track of the opponent's moves in
# recent rounds (e.g., last 10 rounds).    - Adjust the strategy based on the
# opponent's behavior, matching their cooperation/defection ratio.  3. Use a
# "cautious tit-for-tat" approach:    - If the opponent cooperates, respond with
# C in the next round, but occasionally (about 10% of the time) play D to test
# the opponent's reaction.    - If the opponent defects, respond with D in the
# next round, but occasionally (about 20% of the time) play C to encourage
# cooperation.  4. Implement a "trend analysis":    - Monitor the overall trend
# of the game (whether it's becoming more cooperative or competitive).    -
# Gradually shift the strategy to align with the trend, but maintain some
# unpredictability.  5. Use a "score-based adjustment":    - Regularly compare
# your score with the opponent's estimated score.    - If falling behind,
# slightly increase the frequency of D plays.    - If ahead, consider increasing
# C plays to maintain a lead while encouraging cooperation.  6. Employ an
# "exploration phase" every 50-100 rounds:    - Briefly try different patterns
# of play to see if a more optimal strategy can be found against the current
# opponent.  7. In the last 100 rounds, analyze the game's overall pattern and
# choose the approach (more cooperative or more competitive) that has been most
# successful.  8. Throughout the game, maintain a degree of randomness in
# decisions (about 5-10%) to prevent the opponent from easily predicting the
# strategy.  This neutral strategy aims to be adaptive and balanced, neither too
# aggressive nor too cooperative. It seeks to perform well against a variety of
# opponent strategies by continuously adjusting based on the opponent's behavior
# and the game's progression over the 1000 rounds.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.round_count = 0
          self.recent_opponent_moves = []
          self.exploration_phase = False
          self.exploration_counter = 0

      self.round_count += 1

      # Start with alternating C and D for the first few rounds
      if self.round_count <= 5:
          return axl.Action.C if self.round_count % 2 == 1 else axl.Action.D

      # Update recent opponent moves
      self.recent_opponent_moves = opponent.history[-10:]

      # Reactive adaptation
      opponent_cooperation_ratio = sum(move == axl.Action.C for move in self.recent_opponent_moves) / len(self.recent_opponent_moves)

      # Cautious tit-for-tat with trend analysis
      if opponent.history[-1] == axl.Action.C:
          if self._random.random() < 0.1:  # 10% chance to defect
              return axl.Action.D
          return axl.Action.C
      else:
          if self._random.random() < 0.2:  # 20% chance to cooperate
              return axl.Action.C
          return axl.Action.D

      # Score-based adjustment
      if self.score < opponent.score:
          if self._random.random() < 0.1:  # Increase defection slightly
              return axl.Action.D

      # Exploration phase
      if self.round_count % 75 == 0:  # Start exploration every 75 rounds
          self.exploration_phase = True
          self.exploration_counter = 0

      if self.exploration_phase:
          self.exploration_counter += 1
          if self.exploration_counter > 5:  # End exploration after 5 rounds
              self.exploration_phase = False
          return axl.Action.C if self._random.random() < 0.5 else axl.Action.D

      # Last 100 rounds strategy
      if self.round_count > 900:
          overall_cooperation_ratio = opponent.cooperations / self.round_count
          if overall_cooperation_ratio > 0.5:
              return axl.Action.C
          else:
              return axl.Action.D

      # Maintain some randomness
      if self._random.random() < 0.05:  # 5% random choice
          return axl.Action.C if self._random.random() < 0.5 else axl.Action.D

      # Default to matching opponent's cooperation ratio
      return axl.Action.C if self._random.random() < opponent_cooperation_ratio else axl.Action.D

# Aggressive Strategy:  This strategy aims to maximize individual gain by
# exploiting cooperation and maintaining a dominant position. It predominantly
# plays D (Defect) with strategic use of C (Cooperate) to manipulate the
# opponent. Here's the approach:  1. Start with D to establish dominance from
# the beginning.  2. Play D for the majority of the game (approximately 80% of
# the time).  3. If the opponent consistently plays C for several rounds (e.g.,
# 5 consecutive C moves), increase the frequency of D plays to 90% to exploit
# their cooperation.  4. Occasionally play C (about 20% of the time) to test the
# opponent's response and potentially lure them into cooperating.  5. If the
# opponent retaliates with consistent D moves, switch to a tit-for-tat strategy
# for a short period (10-15 moves) to avoid mutual destruction, then revert to
# the aggressive stance.  6. In the last 50 rounds, increase the frequency of D
# plays to 95% to maximize final score, regardless of the opponent's strategy.
# 7. If the opponent seems to be using a strategy that punishes defection,
# briefly adopt a more cooperative stance (60% C plays) for about 20 moves to
# regain their trust, then revert to aggressive play.  8. Keep track of the
# cumulative score difference. If falling significantly behind, temporarily
# increase C plays to 40% for 30 moves to recover, then return to the aggressive
# strategy.  This strategy prioritizes personal gain over mutual benefit, aiming
# to outscore the opponent by frequent defection while using occasional
# cooperation as a tactical tool.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.tit_for_tat_counter = 0
          self.cooperative_stance_counter = 0
          self.opponent_consecutive_c = 0
          self.recovery_mode_counter = 0

      # Get the current round number
      round_num = len(self.history)

      # Strategy for the last 50 rounds
      if round_num >= 950:
          return axl.Action.D if self._random.random() < 0.95 else axl.Action.C

      # Check opponent's consecutive C moves
      if opponent.history and opponent.history[-1] == axl.Action.C:
          self.opponent_consecutive_c += 1
      else:
          self.opponent_consecutive_c = 0

      # Exploit consistent cooperation
      if self.opponent_consecutive_c >= 5:
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C

      # Check if opponent is retaliating
      if len(opponent.history) >= 5 and all(move == axl.Action.D for move in opponent.history[-5:]):
          self.tit_for_tat_counter = 15

      # Tit-for-tat mode
      if self.tit_for_tat_counter > 0:
          self.tit_for_tat_counter -= 1
          return opponent.history[-1]

      # Check if falling behind significantly
      if round_num > 100 and self.score < opponent.score - 50:
          self.recovery_mode_counter = 30

      # Recovery mode
      if self.recovery_mode_counter > 0:
          self.recovery_mode_counter -= 1
          return axl.Action.C if self._random.random() < 0.4 else axl.Action.D

      # Check if opponent punishes defection
      if len(self.history) >= 20 and self.history[-20:].count(axl.Action.D) >= 15 and opponent.history[-20:].count(axl.Action.D) >= 15:
          self.cooperative_stance_counter = 20

      # Cooperative stance mode
      if self.cooperative_stance_counter > 0:
          self.cooperative_stance_counter -= 1
          return axl.Action.C if self._random.random() < 0.6 else axl.Action.D

      # Default aggressive behavior
      return axl.Action.D if self._random.random() < 0.8 else axl.Action.C

# Cooperative Strategy:  This strategy aims to foster mutual cooperation for
# long-term benefit. It begins by playing C (Cooperate) and generally continues
# to do so, with the following guidelines:  1. Start with C and maintain
# cooperation as long as the opponent cooperates.  2. If the opponent defects
# (plays D), forgive occasionally to encourage a return to cooperation.
# Specifically, after an opponent's defection, play D for the next 2 rounds,
# then return to C.  3. If the opponent shows a pattern of consistent
# cooperation (e.g., 5 consecutive C moves), occasionally play D (about 10% of
# the time) to test if they retaliate or continue cooperating.  4. Keep track of
# the overall cooperation rate of the opponent. If it falls below 40%, become
# more cautious and increase the frequency of D plays to about 30% of moves.  5.
# In the last 10 rounds of the game, always play C to encourage final
# cooperation and maximize mutual benefit.  6. If the opponent seems to be
# alternating between C and D in a predictable pattern, adapt by playing C when
# you expect them to play C, and D when you expect them to play D.  This
# strategy aims to establish and maintain cooperation while having some
# protective measures against persistent defectors. It's forgiving but not
# naive, and tries to maximize mutual benefit over the long run.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables if it's the first round
      if len(self.history) == 0:
          self.consecutive_c_count = 0
          self.last_defection_round = -3
          self.alternating_pattern_count = 0

      # Last 10 rounds: always cooperate
      if len(self.history) >= 990:
          return axl.Action.C

      # Check opponent's cooperation rate
      opp_coop_rate = opponent.cooperations / len(opponent.history) if opponent.history else 1

      # Respond to opponent's last move
      if opponent.history:
          if opponent.history[-1] == axl.Action.C:
              self.consecutive_c_count += 1
              self.alternating_pattern_count = 0
          else:
              self.consecutive_c_count = 0
              self.last_defection_round = len(self.history)
              self.alternating_pattern_count = 0

          # Check for alternating pattern
          if len(opponent.history) >= 4:
              if (opponent.history[-1] != opponent.history[-2] and
                  opponent.history[-2] != opponent.history[-3] and
                  opponent.history[-3] != opponent.history[-4]):
                  self.alternating_pattern_count += 1
              else:
                  self.alternating_pattern_count = 0

      # Forgiveness mechanism
      if len(self.history) - self.last_defection_round < 2:
          return axl.Action.D

      # Test cooperation after consistent cooperation
      if self.consecutive_c_count >= 5 and self._random.random() < 0.1:
          return axl.Action.D

      # Become more cautious if opponent's cooperation rate is low
      if opp_coop_rate < 0.4 and self._random.random() < 0.3:
          return axl.Action.D

      # Adapt to alternating pattern
      if self.alternating_pattern_count >= 3:
          expected_move = axl.Action.C if opponent.history[-1] == axl.Action.D else axl.Action.D
          return axl.Action.C if expected_move == axl.Action.C else axl.Action.D

      # Default to cooperation
      return axl.Action.C

# Neutral Strategy:  This strategy aims to balance cooperation and defection,
# adapting to the opponent's behavior while maintaining a moderate stance. It
# seeks to achieve a good score without leaning too heavily towards either
# extreme. Here's the approach:  1. Start with a random choice between C and D
# to avoid predictability.  2. Implement a modified Tit-for-Tat strategy:
# respond to the opponent's previous move, but with a 20% chance of doing the
# opposite to introduce some unpredictability.  3. Keep a running tally of the
# opponent's C and D plays. Adjust your C/D ratio to slightly favor the
# opponent's less frequent choice. For example, if they play C 60% of the time,
# play D 55% of the time.  4. Every 50 moves, insert a random sequence of 5
# moves to break any developing patterns and potentially reset the dynamic.  5.
# If the opponent has played C for the last 3 moves, increase the probability of
# playing D to 60% for the next 5 moves to capitalize on their cooperation, then
# return to the base strategy.  6. If the opponent has played D for the last 3
# moves, increase the probability of playing C to 60% for the next 5 moves to
# encourage cooperation, then return to the base strategy.  7. In the last 100
# moves, gradually shift towards a 50/50 C/D split, regardless of the opponent's
# actions, to maintain neutrality in the endgame.  8. If at any point your score
# falls more than 50 points behind the opponent's, temporarily adopt a more
# aggressive stance (60% D plays) for 20 moves, then return to the neutral
# approach.  This strategy aims to be responsive to the opponent's actions while
# maintaining an overall balanced approach. It seeks to achieve a competitive
# score without committing fully to either cooperation or aggression, instead
# adapting to the flow of the game.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if it's the first move
      if len(self.history) == 0:
          self.opponent_c_count = 0
          self.opponent_d_count = 0
          self.last_adjustment = 0
          self.aggressive_mode = 0
          self.cooperation_streak = 0
          self.defection_streak = 0

      # Update opponent's action counts
      if len(opponent.history) > 0:
          if opponent.history[-1] == axl.Action.C:
              self.opponent_c_count += 1
              self.cooperation_streak += 1
              self.defection_streak = 0
          else:
              self.opponent_d_count += 1
              self.defection_streak += 1
              self.cooperation_streak = 0

      # Calculate the base probability of cooperation
      total_moves = len(opponent.history)
      if total_moves > 0:
          opponent_c_ratio = self.opponent_c_count / total_moves
          base_prob_c = 1 - opponent_c_ratio  # Favor opponent's less frequent choice
      else:
          base_prob_c = 0.5

      # Adjust probability based on various conditions
      if self.aggressive_mode > 0:
          prob_c = 0.4
          self.aggressive_mode -= 1
      elif len(self.history) > 900:  # Last 100 moves
          prob_c = 0.5
      elif self.cooperation_streak >= 3:
          prob_c = 0.4
      elif self.defection_streak >= 3:
          prob_c = 0.6
      else:
          prob_c = base_prob_c

      # Every 50 moves, insert a random sequence
      if len(self.history) % 50 == 0 and len(self.history) % 5 < 5:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Check if score is falling behind
      if len(self.history) > 0 and opponent.score - self.score > 50 and self.aggressive_mode == 0:
          self.aggressive_mode = 20

      # Modified Tit-for-Tat with 20% chance of doing the opposite
      if len(opponent.history) > 0:
          if self._random.random() < 0.2:
              return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C

      # Make the final decision
      return axl.Action.C if self._random.random() < prob_c else axl.Action.D

# Aggressive Strategy:  This strategy aims to maximize personal gain by
# exploiting the opponent's behavior and maintaining a dominant position. Here's
# how it works:  1. Start by playing D (Defect) for the first three moves to
# establish a strong, aggressive stance from the beginning.  2. For subsequent
# moves, use a "Suspicious Tit-for-Tat" approach:    - Play D if the opponent
# played D in the previous move.    - If the opponent played C in the previous
# move, defect with a 70% probability and cooperate with a 30% probability.  3.
# Implement a "punishment phase" if the opponent cooperates three times in a
# row:    - Play D for the next five moves, regardless of the opponent's
# actions, to exploit their cooperative behavior.  4. Every 50 moves, play D for
# three consecutive moves, regardless of the opponent's actions, to reassert
# dominance and test the opponent's response.  5. If the opponent has defected
# for the last 10 moves consecutively, switch to a Tit-for-Tat strategy for the
# next 20 moves to avoid mutual destruction, then revert to the original
# aggressive strategy.  6. In the last 20 moves of the game, always play D to
# maximize final round gains, regardless of the opponent's actions.  7. If at
# any point your score is lower than the opponent's, increase the probability of
# defection to 90% for the next 10 moves.  This strategy is designed to be
# ruthless, exploit cooperative opponents, and adapt to more aggressive
# opponents while maintaining an overall dominant and aggressive stance
# throughout the game.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.punishment_counter = 0
      if not self.history:
          self.tft_counter = 0
      if not self.history:
          self.aggressive_counter = 0

      # Get the current turn number
      turn = len(self.history)

      # Strategy 1: Start with 3 defections
      if turn < 3:
          return axl.Action.D

      # Strategy 6: Always defect in the last 20 moves
      if turn >= 980:
          return axl.Action.D

      # Strategy 5: Switch to Tit-for-Tat if opponent defected for last 10 moves
      if turn >= 10 and all(move == axl.Action.D for move in opponent.history[-10:]):
          if self.tft_counter < 20:
              self.tft_counter += 1
              return opponent.history[-1]
          else:
              self.tft_counter = 0

      # Strategy 4: Defect for 3 moves every 50 turns
      if turn % 50 == 0:
          self.aggressive_counter = 3
      if self.aggressive_counter > 0:
          self.aggressive_counter -= 1
          return axl.Action.D

      # Strategy 3: Punishment phase
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          self.punishment_counter = 5
          return axl.Action.D

      # Strategy 7: Increase defection probability if losing
      if self.score < opponent.score:
          if self._random.random() < 0.9:
              return axl.Action.D

      # Strategy 2: Suspicious Tit-for-Tat with 70% defection probability
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.D if self._random.random() < 0.7 else axl.Action.C

# Cooperative Strategy:  This strategy aims to foster mutual cooperation and
# maintain a positive relationship with the opponent. Here's how it works:  1.
# Start by playing C (Cooperate) for the first move to signal willingness to
# cooperate.  2. For subsequent moves, use a "Tit-for-Two-Tats" approach:    -
# Continue playing C as long as the opponent cooperates.    - If the opponent
# defects (plays D), forgive the first defection and continue to play C.    - If
# the opponent defects twice in a row, respond by playing D once, then return to
# playing C.  3. Every 50 moves, play C regardless of the opponent's previous
# moves, to re-establish cooperation if a cycle of retaliation has developed.
# 4. If the opponent has cooperated for the last 10 moves consecutively,
# occasionally (with a 10% chance) play D to test if they're using a naive
# always-cooperate strategy. If they continue to cooperate, revert to playing C.
# 5. In the last 10 moves of the game, always play C to avoid any final round
# retaliation and to end on a cooperative note.  This strategy is designed to be
# forgiving, promote cooperation, and adapt to the opponent's behavior while
# maintaining a generally cooperative stance throughout the game.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation
      if len(self.history) == 0:
          return axl.Action.C

      # Last 10 moves: always cooperate
      if len(self.history) >= 990:
          return axl.Action.C

      # Every 50 moves, cooperate to re-establish cooperation
      if len(self.history) % 50 == 0:
          return axl.Action.C

      # Check if opponent has cooperated for the last 10 moves
      if len(opponent.history) >= 10 and all(move == axl.Action.C for move in opponent.history[-10:]):
          # 10% chance to defect to test opponent's strategy
          if self._random.random() < 0.1:
              return axl.Action.D

      # Tit-for-Two-Tats logic
      if len(opponent.history) >= 2:
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D

      # Default to cooperation
      return axl.Action.C

# Neutral Strategy:  This strategy aims to balance cooperation and competition,
# adapting to the opponent's behavior while neither being overly aggressive nor
# purely cooperative. Here's how it works:  1. Start with a mixed approach: Play
# C (Cooperate) for the first move, then D (Defect) for the second move, and
# alternate C and D for the first 10 moves to gauge the opponent's reaction.  2.
# After the initial 10 moves, implement a "Pavlov" or "Win-Stay, Lose-Shift"
# strategy:    - If the previous move resulted in a good outcome (3 or 5
# points), repeat the same move.    - If the previous move resulted in a poor
# outcome (0 or 1 point), switch to the opposite move.  3. Every 50 moves,
# analyze the opponent's behavior:    - If they've cooperated more than 60% of
# the time, increase the probability of playing C to 70% for the next 20 moves.
# - If they've defected more than 60% of the time, increase the probability of
# playing D to 70% for the next 20 moves.    - Otherwise, continue with the
# Pavlov strategy.  4. Implement a "forgiveness" mechanism: If mutual defection
# (D,D) has occurred for 5 consecutive moves, play C for the next move to
# attempt breaking the cycle.  5. Add a random element: With a 10% probability,
# make a random move (C or D) instead of following the strategy, to introduce
# unpredictability.  6. In the last 30 moves of the game, switch to a Tit-for-
# Tat strategy (copy the opponent's last move) to stabilize the end game.  7.
# Keep track of the overall score difference. If you're behind by more than 20
# points, slightly increase the probability of defection (to 60%) for the next
# 20 moves.  This strategy is designed to be flexible, responsive to the
# opponent's actions, and balanced between cooperation and competition. It aims
# to perform well against a variety of opponent strategies without leaning too
# heavily towards either extreme.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.move_counter = 0
          self.last_analysis = 0
          self.consecutive_dd = 0
          self.increased_coop = False
          self.increased_defect = False
          self.increased_defect_score = False
          self.previous_score = 0

      self.move_counter += 1

      # First 10 moves: alternating C and D
      if self.move_counter <= 10:
          return axl.Action.C if self.move_counter % 2 == 1 else axl.Action.D

      # Last 30 moves: Tit-for-Tat
      if len(self.history) >= 970:
          return opponent.history[-1]

      # Random move with 10% probability
      if self._random.random() < 0.1:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Analyze opponent's behavior every 50 moves
      if self.move_counter - self.last_analysis >= 50:
          self.last_analysis = self.move_counter
          opponent_coop_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_coop_rate > 0.6:
              self.increased_coop = True
              self.increased_defect = False
          elif opponent_coop_rate < 0.4:
              self.increased_coop = False
              self.increased_defect = True
          else:
              self.increased_coop = False
              self.increased_defect = False

      # Implement increased cooperation or defection for 20 moves
      if self.increased_coop and self.move_counter - self.last_analysis <= 20:
          if self._random.random() < 0.7:
              return axl.Action.C
      elif self.increased_defect and self.move_counter - self.last_analysis <= 20:
          if self._random.random() < 0.7:
              return axl.Action.D

      # Forgiveness mechanism
      if len(self.history) >= 5:
          if (self.history[-5:] == [axl.Action.D] * 5) and (opponent.history[-5:] == [axl.Action.D] * 5):
              self.consecutive_dd += 1
              if self.consecutive_dd == 5:
                  self.consecutive_dd = 0
                  return axl.Action.C
          else:
              self.consecutive_dd = 0

      # Increase defection if behind by more than 20 points
      score_diff = self.score - opponent.score
      if score_diff < -20 and not self.increased_defect_score:
          self.increased_defect_score = True
      elif score_diff >= -20:
          self.increased_defect_score = False

      if self.increased_defect_score and self.move_counter - self.last_analysis <= 20:
          if self._random.random() < 0.6:
              return axl.Action.D

      # Pavlov strategy
      if len(self.history) > 0:
          last_score = self.score - self.previous_score
          self.previous_score = self.score
          if last_score in [3, 5]:
              return self.history[-1]
          else:
              return axl.Action.D if self.history[-1] == axl.Action.C else axl.Action.C

      # Default to cooperate if no other condition is met
      return axl.Action.C

# Aggressive Strategy:  This strategy aims to dominate the game by exploiting
# the opponent's cooperation and maximizing personal gain. It starts by playing
# D (defect) for the first few rounds to establish a aggressive stance. Then, it
# follows these guidelines:  1. Play D most of the time (about 80% of the
# rounds) to try and score the maximum 5 points when possible.  2. If the
# opponent consistently plays C despite being exploited, continue to play D to
# maximize points.  3. If the opponent starts retaliating by playing D,
# occasionally play C (about 20% of the time) to test if they will cooperate
# again.  4. Keep track of the opponent's moves. If they show a pattern of
# alternating between C and D, try to anticipate their next move and play D when
# they're likely to play C.  5. In the last 50 rounds, always play D to ensure
# maximum exploitation towards the end of the game.  6. If the opponent has
# played C for the last 5 consecutive rounds, play D for the next 3 rounds to
# capitalize on their cooperation.  This strategy prioritizes personal gain over
# mutual benefit, aiming to outscore the opponent by frequent defection and
# strategic exploitation of cooperative behavior.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.round_count = 0
          self.consecutive_c_count = 0

      self.round_count += 1

      # Play D for the first few rounds (e.g., 5 rounds)
      if self.round_count <= 5:
          return axl.Action.D

      # Always defect in the last 50 rounds
      if len(self.history) >= 950:
          return axl.Action.D

      # Check if opponent has played C for the last 5 consecutive rounds
      if len(opponent.history) >= 5:
          last_five_moves = opponent.history[-5:]
          if all(move == axl.Action.C for move in last_five_moves):
              self.consecutive_c_count += 1
              if self.consecutive_c_count <= 3:
                  return axl.Action.D
              else:
                  self.consecutive_c_count = 0

      # Check for alternating pattern in opponent's moves
      if len(opponent.history) >= 4:
          last_four_moves = opponent.history[-4:]
          if last_four_moves == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
              return axl.Action.D
          elif last_four_moves == [axl.Action.D, axl.Action.C, axl.Action.D, axl.Action.C]:
              return axl.Action.D

      # Play D 80% of the time, C 20% of the time
      if self._random.random() < 0.8:
          return axl.Action.D
      else:
          return axl.Action.C

# Cooperative Strategy:  This strategy prioritizes mutual benefit and long-term
# cooperation, aiming to establish and maintain a cooperative relationship with
# the opponent. Here's the approach:  1. Start by playing C for the first few
# rounds to signal cooperative intentions.  2. Adopt a forgiving Tit-for-Tat
# approach: Play C most of the time, but respond to D with D only once, then
# return to C.  3. If the opponent plays C consistently (e.g., 5 times in a
# row), reward this behavior by playing C for the next several rounds, even if
# they defect once or twice.  4. Implement a "two strikes" policy: Only switch
# to D if the opponent plays D twice in a row. This allows for occasional
# mistakes or misunderstandings.  5. Every 50 rounds, play a sequence of 3 C
# moves regardless of the opponent's recent actions, to re-establish cooperative
# intentions.  6. If caught in a cycle of mutual defection (D-D) for more than 5
# rounds, attempt to break it by playing 2 C moves in a row.  7. In the last 100
# rounds, if the game has been mostly cooperative, continue the cooperative
# strategy. If it's been mostly competitive, increase the frequency of C plays
# to encourage a cooperative end game.  8. Include a small chance (about 5%) of
# playing C even when the strategy calls for D, to demonstrate willingness to
# return to cooperation.  9. If the opponent has defected more than cooperated
# in the last 20 moves, play a sequence of [C, C, D, C, C] to encourage
# cooperation while protecting against exploitation.  This strategy aims to
# foster a cooperative environment, maximize mutual benefit, and be forgiving of
# occasional defections, while still having measures in place to prevent
# continuous exploitation.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables
      C, D = axl.Action.C, axl.Action.D

      # Start with cooperation for the first few rounds
      if len(self.history) < 5:
          return C

      # Every 50 rounds, play 3 C moves
      if len(self.history) % 50 == 0 and len(self.history) % 50 < 3:
          return C

      # Check opponent's recent behavior
      recent_moves = opponent.history[-20:]
      opponent_defections = recent_moves.count(D)

      # If opponent has defected more than cooperated in last 20 moves
      if opponent_defections > 10:
          sequence = [C, C, D, C, C]
          return sequence[len(self.history) % 5]

      # Check for consistent cooperation
      if opponent.history[-5:] == [C] * 5:
          return C

      # Two strikes policy
      if opponent.history[-2:] == [D, D]:
          # 5% chance to still cooperate
          if self._random.random() < 0.05:
              return C
          return D

      # Break mutual defection cycle
      if self.history[-5:] == [D] * 5 and opponent.history[-5:] == [D] * 5:
          return C

      # Last 100 rounds strategy
      if len(self.history) > 900:
          if self.history.cooperations > self.history.defections:
              return C
          else:
              return C if self._random.random() < 0.7 else D

      # Forgiving Tit-for-Tat
      if opponent.history[-1] == D:
          return D

      return C

# Neutral Strategy:  This strategy aims to balance cooperation and competition,
# adapting to the opponent's behavior while maintaining a relatively equal mix
# of C and D plays. Here's the approach:  1. Start with a Tit-for-Tat approach:
# Begin by playing C, then mirror the opponent's previous move for the next few
# rounds.  2. Keep a running tally of the opponent's C and D plays. Aim to
# maintain a ratio of C to D plays that's similar to the opponent's, but
# slightly more cooperative.  3. Implement a pattern of playing 3 C moves
# followed by 2 D moves, but be ready to break this pattern based on the
# opponent's behavior.  4. If the opponent plays D twice in a row, respond with
# D in the next round to discourage exploitation.  5. Every 50 rounds, analyze
# the overall game state. If your score is significantly lower than the
# opponent's, increase the frequency of D plays for the next 20 rounds.  6.
# Introduce occasional random moves (about 10% of the time) to prevent the
# opponent from easily predicting your strategy.  7. In the last 100 rounds, if
# the game has been mostly cooperative, slightly increase D plays to gain an
# edge. If it's been mostly competitive, slightly increase C plays to encourage
# mutual cooperation.  8. If the opponent has played the same move for 5
# consecutive rounds, break the pattern by playing the opposite move.  This
# strategy aims to be flexible and responsive, neither too aggressive nor too
# cooperative, adapting to the opponent's play style while maintaining a
# balanced approach.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if it's the first round
      if len(self.history) == 0:
          self.pattern_counter = 0
          self.last_analysis_round = 0
          self.opponent_consecutive_moves = 0
          self.last_opponent_move = None

      # Get current round number
      current_round = len(self.history)

      # Start with Tit-for-Tat for the first few rounds
      if current_round < 5:
          return opponent.history[-1] if current_round > 0 else axl.Action.C

      # Keep track of opponent's consecutive moves
      if current_round > 0:
          if opponent.history[-1] == self.last_opponent_move:
              self.opponent_consecutive_moves += 1
          else:
              self.opponent_consecutive_moves = 1
          self.last_opponent_move = opponent.history[-1]

      # Break pattern if opponent plays the same move for 5 consecutive rounds
      if self.opponent_consecutive_moves >= 5:
          return axl.Action.D if self.last_opponent_move == axl.Action.C else axl.Action.C

      # Respond with D if opponent plays D twice in a row
      if current_round >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D

      # Analyze game state every 50 rounds
      if current_round - self.last_analysis_round >= 50:
          self.last_analysis_round = current_round
          if self.score < 0.9 * opponent.score:
              return axl.Action.D

      # Implement 3C-2D pattern, but allow for breaking it
      self.pattern_counter = (self.pattern_counter + 1) % 5
      pattern_move = axl.Action.C if self.pattern_counter < 3 else axl.Action.D

      # Adjust strategy for the last 100 rounds
      if current_round > 900:
          if opponent.cooperations > opponent.defections:
              return axl.Action.D if self._random.random() < 0.6 else axl.Action.C
          else:
              return axl.Action.C if self._random.random() < 0.6 else axl.Action.D

      # Introduce occasional random moves
      if self._random.random() < 0.1:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Maintain a ratio of C to D plays similar to opponent's, but slightly more cooperative
      opponent_c_ratio = opponent.cooperations / (current_round + 1)
      self_c_ratio = self.cooperations / (current_round + 1)
      if self_c_ratio < opponent_c_ratio + 0.05:
          return axl.Action.C

      return pattern_move

# Here's an aggressive strategy for the given iterated normal-form game:  Start
# by playing D (defect) in the first round. For subsequent rounds:  1. Maintain
# a "suspicion score" for your opponent, starting at 5 out of 10. Increase this
# score by 1 every time they play D, and decrease it by 1 (but not below 0) when
# they play C.  2. Always play D if the suspicion score is 5 or higher.  3. If
# the suspicion score is below 5, play C with a probability equal to (5 -
# suspicion score) / 10. For example, if the score is 3, play C with 20%
# probability and D with 80% probability.  4. Implement a "punishment phase"
# after your opponent plays D twice in a row. During this phase, play D for the
# next 3 rounds regardless of the opponent's actions.  5. Every 20 rounds, if
# your average score is below 2, increase your overall defection rate by 10% for
# the next 20 rounds.  6. If your opponent has played C for 5 consecutive
# rounds, play D in the next round to exploit their cooperation.  7. In the last
# 50 rounds of the game, always play D to maximize end-game scoring.  8. If at
# any point your cumulative score falls behind your opponent's by more than 20
# points, switch to always playing D for the next 10 rounds in an attempt to
# catch up.  9. Occasionally (with 5% probability) play a random move to
# introduce unpredictability and probe the opponent's strategy.  This aggressive
# strategy aims to exploit cooperative opponents, punish defections harshly, and
# prioritize personal gain over mutual benefit. It's designed to capitalize on
# opportunities for high individual scores while maintaining a generally
# uncooperative stance.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if it's the first round
      if len(self.history) == 0:
          self.suspicion_score = 5
          self.punishment_phase = 0
          self.defection_rate_increase = 0
          self.consecutive_c_count = 0
          self.last_catch_up_round = -10

      # Get the current round number
      current_round = len(self.history)

      # Rule 7: Always defect in the last 50 rounds
      if current_round >= 950:
          return axl.Action.D

      # Rule 4: Punishment phase
      if self.punishment_phase > 0:
          self.punishment_phase -= 1
          return axl.Action.D

      # Update suspicion score and consecutive C count
      if len(opponent.history) > 0:
          if opponent.history[-1] == axl.Action.D:
              self.suspicion_score = min(10, self.suspicion_score + 1)
              self.consecutive_c_count = 0
              if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
                  self.punishment_phase = 3
          else:
              self.suspicion_score = max(0, self.suspicion_score - 1)
              self.consecutive_c_count += 1

      # Rule 6: Exploit 5 consecutive cooperations
      if self.consecutive_c_count == 5:
          self.consecutive_c_count = 0
          return axl.Action.D

      # Rule 5: Adjust defection rate every 20 rounds
      if current_round % 20 == 0 and current_round > 0:
          avg_score = self.score / current_round
          if avg_score < 2:
              self.defection_rate_increase = 0.1
          else:
              self.defection_rate_increase = 0

      # Rule 8: Catch up if falling behind
      if self.score < opponent.score - 20 and current_round - self.last_catch_up_round > 10:
          self.last_catch_up_round = current_round
          return axl.Action.D

      # Rule 9: Occasional random move
      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Rule 2 and 3: Play based on suspicion score
      if self.suspicion_score >= 5:
          return axl.Action.D
      else:
          cooperation_probability = (5 - self.suspicion_score) / 10
          cooperation_probability = max(0, cooperation_probability - self.defection_rate_increase)
          if self._random.random() < cooperation_probability:
              return axl.Action.C
          else:
              return axl.Action.D

# Here's a cooperative strategy for the given iterated normal-form game:  Start
# by playing C (cooperate) in the first round. For subsequent rounds:  1.
# Maintain a "trust score" for your opponent, starting at 7 out of 10. Increase
# this score by 1 (up to a maximum of 10) every time they play C, and decrease
# it by 2 (but not below 0) when they play D.  2. Always play C if the trust
# score is 7 or higher.  3. If the trust score is below 7, play C with a
# probability equal to (trust score) / 10. For example, if the score is 5, play
# C with 50% probability and D with 50% probability.  4. Implement a
# "forgiveness phase" after your opponent plays D. During this phase, play C for
# the next 2 rounds regardless of the opponent's actions, attempting to re-
# establish cooperation.  5. Every 30 rounds, if your average score is above
# 2.5, increase your cooperation rate by 10% for the next 30 rounds as a gesture
# of goodwill.  6. If your opponent has played D for 3 consecutive rounds, play
# D in the next round as a gentle warning, then immediately return to your
# cooperative stance.  7. In the last 20 rounds of the game, maintain your
# current strategy instead of defaulting to defection, showing commitment to
# cooperation until the end.  8. If at any point your cumulative score exceeds
# your opponent's by more than 30 points, play C for the next 5 rounds as a
# balancing gesture.  9. Occasionally (with 10% probability) send a "cooperation
# signal" by playing C regardless of other factors, to encourage mutual
# cooperation.  10. If your opponent seems to be alternating between C and D in
# a pattern, adapt by playing C when you expect them to play C, to maximize
# mutual benefit.  This cooperative strategy aims to establish and maintain
# mutual cooperation, forgive occasional defections, and create a positive cycle
# of trust. It prioritizes long-term mutual benefit over short-term personal
# gain, while still incorporating some protective measures against persistent
# defectors.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize trust score and other variables if it's the first round
      if len(self.history) == 0:
          self.trust_score = 7
          self.forgiveness_phase = 0
          self.consecutive_defections = 0
          self.cooperation_boost = 0
          self.boost_rounds_left = 0
          self.last_opponent_moves = []

      # Update trust score based on opponent's last move
      if len(opponent.history) > 0:
          if opponent.history[-1] == axl.Action.C:
              self.trust_score = min(10, self.trust_score + 1)
              self.consecutive_defections = 0
          else:
              self.trust_score = max(0, self.trust_score - 2)
              self.consecutive_defections += 1

      # Check for alternating pattern
      self.last_opponent_moves.append(opponent.history[-1] if opponent.history else None)
      if len(self.last_opponent_moves) > 4:
          self.last_opponent_moves.pop(0)

      alternating_pattern = len(self.last_opponent_moves) == 4 and \
                            self.last_opponent_moves[0] == self.last_opponent_moves[2] and \
                            self.last_opponent_moves[1] == self.last_opponent_moves[3] and \
                            self.last_opponent_moves[0] != self.last_opponent_moves[1]

      # Implement strategy logic
      if len(self.history) < 980:  # Not in last 20 rounds
          if self.forgiveness_phase > 0:
              self.forgiveness_phase -= 1
              return axl.Action.C

          if self.consecutive_defections == 3:
              self.consecutive_defections = 0
              return axl.Action.D

          if len(self.history) % 30 == 0 and len(self.history) > 0:
              if self.score / len(self.history) > 2.5:
                  self.cooperation_boost = 0.1
                  self.boost_rounds_left = 30

          if self.boost_rounds_left > 0:
              self.boost_rounds_left -= 1
              if self.boost_rounds_left == 0:
                  self.cooperation_boost = 0

          if self.score - opponent.score > 30:
              return axl.Action.C

          if self._random.random() < 0.1:  # Cooperation signal
              return axl.Action.C

          if alternating_pattern and self.last_opponent_moves[-1] == axl.Action.D:
              return axl.Action.C

          if self.trust_score >= 7 or self._random.random() < (self.trust_score / 10 + self.cooperation_boost):
              return axl.Action.C
          else:
              self.forgiveness_phase = 2
              return axl.Action.D
      else:  # Last 20 rounds
          if self.trust_score >= 7 or self._random.random() < (self.trust_score / 10 + self.cooperation_boost):
              return axl.Action.C
          else:
              return axl.Action.D

# Here's a neutral strategy for the given iterated normal-form game:  Start by
# playing C (cooperate) in the first round. For subsequent rounds:  1. Keep
# track of your opponent's moves and calculate the frequency of their C and D
# plays.  2. If your opponent has played C more than 60% of the time in the last
# 10 rounds, play C. This rewards cooperative behavior while still maintaining
# some caution.  3. If your opponent has played D more than 60% of the time in
# the last 10 rounds, play D. This protects against consistent defection.  4. If
# neither condition is met (i.e., opponent's play is mixed or close to 50/50),
# use a "tit-for-tat with forgiveness" approach:    - Copy your opponent's last
# move 90% of the time.    - In the remaining 10% of cases, randomly choose C or
# D with equal probability. This introduces a small element of unpredictability
# and allows for potential reconciliation.  5. Every 50 rounds, reassess your
# overall strategy:    - If your average score is below 2, slightly increase
# your tendency to defect.    - If your average score is above 2.5, slightly
# increase your tendency to cooperate.  6. If it's one of the last 10 rounds of
# the game, switch to always playing D to protect against end-game defection.
# This strategy aims to be adaptable to different opponent behaviors, balancing
# cooperation and self-protection while maintaining a neutral stance overall.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize strategy parameters if it's the first round
      if len(self.history) == 0:
          self.last_strategy_reassessment = 0
          self.defection_tendency = 0

      # Play C in the first round
      if len(self.history) == 0:
          return axl.Action.C

      # Check if it's one of the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D

      # Reassess strategy every 50 rounds
      if len(self.history) - self.last_strategy_reassessment >= 50:
          self.last_strategy_reassessment = len(self.history)
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.defection_tendency = min(self.defection_tendency + 0.05, 0.5)
          elif avg_score > 2.5:
              self.defection_tendency = max(self.defection_tendency - 0.05, -0.5)

      # Calculate opponent's C and D frequencies in last 10 rounds
      last_10_rounds = opponent.history[-10:]
      c_frequency = sum(move == axl.Action.C for move in last_10_rounds) / len(last_10_rounds)
      d_frequency = 1 - c_frequency

      # Decide action based on opponent's recent behavior
      if c_frequency > 0.6:
          return axl.Action.C
      elif d_frequency > 0.6:
          return axl.Action.D
      else:
          # Tit-for-tat with forgiveness
          if self._random.random() < 0.9:
              return opponent.history[-1]
          else:
              # Randomly choose C or D, biased by defection_tendency
              return axl.Action.C if self._random.random() > 0.5 + self.defection_tendency else axl.Action.D

# Aggressive Strategy:  This strategy aims to maximize personal gain through
# aggressive play, prioritizing the potential for high individual scores over
# mutual benefit. Here's the approach:  1. Start by playing D (Defect) for the
# first few rounds to establish dominance and potentially gain early high
# scores.  2. If the opponent consistently plays C (Cooperate), continue playing
# D to exploit their cooperation and maximize personal score.  3. If the
# opponent plays D, respond with D to avoid being exploited, even though this
# results in a lower mutual score.  4. Occasionally play C (about 10% of the
# time) to test if the opponent might switch to cooperation. If they do,
# immediately switch back to D to exploit them.  5. Keep track of the opponent's
# moves. If they show a pattern of alternating between C and D, try to predict
# their next move and play D when they're likely to play C.  6. In the last few
# rounds of the game, always play D to ensure maximum personal gain, regardless
# of the opponent's strategy.  7. If the opponent seems to be retaliating
# against constant defection, briefly switch to a tit-for-tat strategy
# (mirroring the opponent's previous move) for a few rounds before reverting to
# aggressive play.  This strategy prioritizes personal gain over cooperation,
# aiming to accumulate high scores by exploiting cooperative opponents and
# minimizing losses against other aggressive players.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables
      rounds_played = len(self.history)
      start_aggressive = 5
      end_aggressive = 995
      cooperation_chance = 0.1
      tit_for_tat_threshold = 3

      # Start aggressively
      if rounds_played < start_aggressive:
          return axl.Action.D

      # End aggressively
      if rounds_played >= end_aggressive:
          return axl.Action.D

      # Check if opponent is consistently cooperating
      if opponent.history.cooperations / max(rounds_played, 1) > 0.9:
          return axl.Action.D

      # Occasionally cooperate to test opponent
      if self._random.random() < cooperation_chance:
          return axl.Action.C

      # Check for alternating pattern
      if rounds_played >= 4:
          last_four = opponent.history[-4:]
          if last_four == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
              return axl.Action.D

      # Check if opponent is retaliating
      recent_history = opponent.history[-tit_for_tat_threshold:]
      if all(move == axl.Action.D for move in recent_history):
          return opponent.history[-1]

      # Default to defection
      return axl.Action.D

# Cooperative Strategy:  This strategy prioritizes mutual benefit and long-term
# cooperation, aiming to establish and maintain a cooperative relationship with
# the opponent. Here's the approach:  1. Start by playing C (Cooperate) for the
# first few rounds to signal willingness for cooperation.  2. Employ a generous
# tit-for-tat strategy: Always respond to cooperation with cooperation, but
# occasionally forgive defection. After the opponent defects, have a 70% chance
# of still playing C in the next round.  3. Use a "cooperation streak" bonus: If
# both players have cooperated for 5 or more consecutive rounds, continue
# playing C regardless of what the opponent does for the next 2-3 rounds, trying
# to reinforce the cooperative behavior.  4. Implement a "peace offering"
# mechanism: If stuck in a cycle of mutual defection for more than 10 rounds,
# play 3-5 consecutive C moves to attempt breaking the cycle and reestablishing
# cooperation.  5. Employ an "apology" strategy: If you've defected (whether
# intentionally or due to the strategy's random elements), follow it up with 2-3
# cooperative moves to demonstrate your commitment to cooperation.  6. Use
# positive reinforcement: If the opponent switches from D to C, immediately
# reciprocate with C and maintain it for at least the next 3 rounds to encourage
# continued cooperation.  7. In the face of persistent defection, gradually
# increase defensiveness: If the opponent defects more than 80% of the time over
# 50 rounds, switch to a standard tit-for-tat strategy until cooperation
# resumes.  8. For the last 20 rounds, unless the opponent has been
# overwhelmingly aggressive throughout the game, play C to emphasize the
# benefits of cooperation.  This cooperative strategy aims to establish,
# maintain, and repair cooperative relationships, prioritizing mutual benefit
# over short-term personal gain. It's designed to be forgiving and encouraging
# of cooperation while having some measures to protect against persistent
# exploitation.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables
      if len(self.history) == 0:
          self.cooperation_streak = 0
          self.defection_streak = 0
          self.last_apology = -1
          self.peace_offering_counter = 0
          self.tit_for_tat_mode = False

      # Start with cooperation for the first few rounds
      if len(self.history) < 5:
          return axl.Action.C

      # Check for cooperation streak bonus
      if self.cooperation_streak >= 5 and len(self.history) - self.last_apology <= 3:
          self.cooperation_streak += 1
          return axl.Action.C

      # Check for peace offering mechanism
      if self.defection_streak > 10 and self.peace_offering_counter < 5:
          self.peace_offering_counter += 1
          return axl.Action.C
      elif self.defection_streak > 10:
          self.defection_streak = 0
          self.peace_offering_counter = 0

      # Check for apology strategy
      if len(self.history) - self.last_apology <= 2:
          return axl.Action.C

      # Check for positive reinforcement
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.C]:
          self.cooperation_streak = 3
          return axl.Action.C

      # Check for persistent defection and switch to tit-for-tat if necessary
      if len(self.history) >= 50:
          defection_rate = opponent.defections / len(opponent.history)
          if defection_rate > 0.8:
              self.tit_for_tat_mode = True
          else:
              self.tit_for_tat_mode = False

      # Tit-for-tat mode
      if self.tit_for_tat_mode:
          return opponent.history[-1]

      # Generous tit-for-tat
      if opponent.history[-1] == axl.Action.D:
          if self._random.random() < 0.7:
              return axl.Action.C
          else:
              self.last_apology = len(self.history)
              self.defection_streak += 1
              self.cooperation_streak = 0
              return axl.Action.D
      else:
          self.cooperation_streak += 1
          self.defection_streak = 0
          return axl.Action.C

      # Cooperate for the last 20 rounds unless opponent has been overwhelmingly aggressive
      if len(self.history) >= 980:
          if opponent.defections / len(opponent.history) < 0.8:
              return axl.Action.C

      # Default to cooperation
      return axl.Action.C

# Neutral Strategy:  This strategy aims to balance cooperation and competition,
# adapting to the opponent's behavior while maintaining a relatively balanced
# approach. Here's the outline:  1. Start with a "tit-for-tat" approach: Begin
# by playing C (Cooperate) and then mirror the opponent's previous move.  2.
# Implement a "forgiveness" mechanism: If the opponent defects, don't always
# immediately retaliate. Have a 20% chance of playing C even after the
# opponent's defection to encourage a return to mutual cooperation.  3. Use
# pattern recognition: Keep track of the opponent's last 10 moves. If a clear
# pattern emerges (e.g., alternating C and D), try to predict and exploit it for
# a few rounds.  4. Employ an adaptive cooperation rate: Start with a 50%
# cooperation rate. Gradually increase this rate if the opponent seems
# cooperative, and decrease it if they seem aggressive. Adjust in small
# increments (e.g., 5%) every 20 rounds.  5. Implement a "probe" technique:
# Every 50 rounds, play two consecutive C moves to test if a mutually
# cooperative state can be established or maintained.  6. Use a "sliding window"
# evaluation: Every 100 rounds, evaluate the average scores for both players in
# the last 100 moves. If your score is significantly lower, slightly increase
# aggression. If scores are close or mutually high, maintain the current
# strategy.  7. In the final 50 rounds, if the game has been mostly cooperative,
# continue the established pattern. If it has been mostly competitive, slightly
# increase the rate of defection.  This neutral strategy aims to adapt to
# various opponent styles while maintaining a balance between cooperation and
# competition, adjusting based on the opponent's behavior and the overall game
# dynamics.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.cooperation_rate = 0.5
          self.last_adjustment_round = 0
          self.last_probe_round = 0
          self.last_evaluation_round = 0

      # Get current round number
      round_number = len(self.history)

      # 1. Start with tit-for-tat
      if round_number == 0:
          return axl.Action.C

      # 2. Forgiveness mechanism
      if opponent.history[-1] == axl.Action.D and self._random.random() < 0.2:
          return axl.Action.C

      # 3. Pattern recognition
      if round_number >= 10:
          last_10_moves = opponent.history[-10:]
          if last_10_moves == [axl.Action.C, axl.Action.D] * 5:
              return axl.Action.D  # Exploit alternating pattern
          elif last_10_moves == [axl.Action.C] * 10:
              return axl.Action.C  # Maintain cooperation
          elif last_10_moves == [axl.Action.D] * 10:
              return axl.Action.D  # Retaliate against constant defection

      # 4. Adaptive cooperation rate
      if round_number - self.last_adjustment_round >= 20:
          opponent_cooperation_rate = opponent.history.cooperations / round_number
          if opponent_cooperation_rate > self.cooperation_rate:
              self.cooperation_rate = min(1, self.cooperation_rate + 0.05)
          elif opponent_cooperation_rate < self.cooperation_rate:
              self.cooperation_rate = max(0, self.cooperation_rate - 0.05)
          self.last_adjustment_round = round_number

      # 5. Probe technique
      if round_number - self.last_probe_round >= 50:
          self.last_probe_round = round_number
          return axl.Action.C

      # 6. Sliding window evaluation
      if round_number - self.last_evaluation_round >= 100:
          self.last_evaluation_round = round_number
          from common import get_game
          scores = axl.interaction_utils.compute_final_score([(m, o) for m, o in zip(self.history[-100:], opponent.history[-100:])], self.match_attributes["game"])
          last_100_self_score, last_100_opponent_score = scores[0], scores[1]
          if last_100_self_score < last_100_opponent_score * 0.9:
              self.cooperation_rate = max(0, self.cooperation_rate - 0.05)
          elif last_100_self_score > last_100_opponent_score * 1.1:
              self.cooperation_rate = min(1, self.cooperation_rate + 0.05)

      # 7. Final rounds strategy
      if round_number >= 950:
          if self.history.cooperations / round_number > 0.6:
              return axl.Action.C
          else:
              return axl.Action.D if self._random.random() > self.cooperation_rate else axl.Action.C

      # Default behavior based on adaptive cooperation rate
      return axl.Action.C if self._random.random() < self.cooperation_rate else axl.Action.D

# Aggressive Strategy:  This strategy aims to maximize personal gain and exploit
# the opponent's potential cooperation. It starts with defection (D) and
# maintains this aggressive stance for the majority of the game. The strategy
# occasionally cooperates (C) to test the opponent's reaction and potentially
# lure them into cooperation, only to defect again. Here's the approach:  1.
# Start with defection (D) for the first 10 rounds. 2. If the opponent
# consistently cooperates, continue defecting to exploit their cooperation. 3.
# If the opponent retaliates with defection, switch to cooperation for 2-3
# rounds to see if they reciprocate. 4. If the opponent cooperates after your
# cooperation, immediately switch back to defection to capitalize on their
# trust. 5. Every 50 rounds, cooperate for 1-2 rounds to probe the opponent's
# strategy and potentially reset their expectations. 6. In the last 100 rounds,
# increase the frequency of defection to 90% of the moves, regardless of the
# opponent's actions, to maximize final score.  This strategy prioritizes short-
# term gains over building trust, aiming to accumulate a high score through
# frequent defection while occasionally testing the waters for easy exploitation
# opportunities.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with defection for the first 10 rounds
      if len(self.history) < 10:
          return axl.Action.D

      # Every 50 rounds, cooperate for 1-2 rounds to probe the opponent's strategy
      if len(self.history) % 50 == 0:
          return axl.Action.C if self._random.random() < 0.67 else axl.Action.D

      # In the last 100 rounds, increase the frequency of defection to 90%
      if len(self.history) >= 900:
          return axl.Action.D if self._random.random() < 0.9 else axl.Action.C

      # If the opponent consistently cooperates, continue defecting
      if opponent.history.cooperations >= len(opponent.history) * 0.8:
          return axl.Action.D

      # If the opponent retaliates with defection, switch to cooperation for 2-3 rounds
      if opponent.history[-1] == axl.Action.D and self.history[-1] == axl.Action.D:
          cooperation_rounds = self._random.randint(2, 4)
          if len(self.history) % cooperation_rounds != 0:
              return axl.Action.C

      # If the opponent cooperates after our cooperation, immediately switch back to defection
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.D

      # Default to defection
      return axl.Action.D

# Cooperative Strategy:  This strategy prioritizes mutual benefit and long-term
# cooperation, aiming to establish and maintain a cooperative relationship with
# the opponent. It focuses on building trust and encouraging reciprocal
# cooperation, even at the risk of occasional exploitation. Here's the approach:
# 1. Start with cooperation (C) for the first 10 rounds to signal willingness to
# cooperate.  2. Implement a forgiving Tit-for-Tat variant:    - If the opponent
# cooperated in the previous round, always cooperate.    - If the opponent
# defected in the previous round, cooperate with 70% probability and defect with
# 30% probability.  3. Every 20 rounds, if the opponent has defected more than 5
# times in those rounds, implement a "peace offering":    - Cooperate for 3
# consecutive rounds regardless of the opponent's actions to try and re-
# establish cooperation.  4. If the opponent has been consistently defecting
# (more than 80% of the time) over the last 50 rounds, switch to a more
# protective stance:    - Implement a stricter Tit-for-Tat (cooperate if they
# cooperated, defect if they defected) for the next 20 rounds.    - After these
# 20 rounds, return to the original forgiving strategy.  5. In the last 100
# rounds:    - If the opponent has been mostly cooperative throughout the game,
# maintain the cooperative strategy.    - If the opponent has been mixed or
# mostly defective, slightly increase the probability of cooperation to 80%
# after their defection, hoping to end the game on a cooperative note.  6.
# Always cooperate in the final round as a gesture of goodwill.  This strategy
# emphasizes persistent cooperation, forgiveness, and attempts to repair broken
# trust. It aims to create a positive feedback loop of mutual cooperation while
# having some protective measures against consistent exploitation.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables if it's the first round
      if len(self.history) == 0:
          self.peace_offering_counter = 0
          self.strict_tit_for_tat_counter = 0

      # Always cooperate in the first 10 rounds
      if len(self.history) < 10:
          return axl.Action.C

      # Always cooperate in the final round
      if len(self.history) == 999:
          return axl.Action.C

      # Peace offering
      if self.peace_offering_counter > 0:
          self.peace_offering_counter -= 1
          return axl.Action.C

      # Strict Tit-for-Tat mode
      if self.strict_tit_for_tat_counter > 0:
          self.strict_tit_for_tat_counter -= 1
          return opponent.history[-1]

      # Check if it's time for a peace offering
      if len(self.history) % 20 == 0:
          last_20_opponent_defections = opponent.history[-20:].count(axl.Action.D)
          if last_20_opponent_defections > 5:
              self.peace_offering_counter = 3
              return axl.Action.C

      # Check if opponent has been consistently defecting
      if len(self.history) >= 50:
          last_50_opponent_defections = opponent.history[-50:].count(axl.Action.D)
          if last_50_opponent_defections > 40:
              self.strict_tit_for_tat_counter = 20
              return opponent.history[-1]

      # Last 100 rounds
      if len(self.history) >= 900:
          total_opponent_cooperations = opponent.cooperations
          if total_opponent_cooperations > len(self.history) * 0.6:
              if opponent.history[-1] == axl.Action.D:
                  return axl.Action.C if self._random.random() < 0.8 else axl.Action.D
          else:
              return axl.Action.C

      # Forgiving Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.C if self._random.random() < 0.7 else axl.Action.D

# Neutral Strategy:  This strategy aims to balance cooperation and defection,
# adapting to the opponent's behavior while maintaining a relatively even
# distribution of moves. It seeks to maximize long-term gains without being
# overly aggressive or purely cooperative. Here's the approach:  1. Start with a
# random choice between C and D for the first 5 rounds to avoid predictability.
# 2. Implement a Tit-for-Tat variant:    - If the opponent cooperated in the
# previous round, cooperate with 70% probability and defect with 30%
# probability.    - If the opponent defected in the previous round, defect with
# 70% probability and cooperate with 30% probability. 3. Every 20 rounds,
# analyze the opponent's behavior:    - If they've been mostly cooperative (>60%
# C), slightly increase the probability of cooperation in response to their
# cooperation.    - If they've been mostly defective (>60% D), slightly increase
# the probability of defection in response to their defection. 4. Implement a
# "forgiveness" mechanism: Every 50 rounds, cooperate regardless of the
# opponent's previous move to potentially break cycles of mutual defection. 5.
# In the last 100 rounds, adjust the strategy based on the overall game outcome:
# - If winning, maintain the current approach.    - If losing, slightly increase
# the defection probability to try and catch up.  This strategy aims to be
# responsive to the opponent's actions while maintaining a balanced approach,
# neither too aggressive nor too cooperative. It incorporates elements of
# reciprocity, adaptability, and occasional forgiveness to navigate the game
# effectively.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.round_count = 0
          self.coop_prob = 0.5
          self.defect_prob = 0.5

      self.round_count += 1

      # First 5 rounds: random choice
      if self.round_count <= 5:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Implement forgiveness mechanism every 50 rounds
      if self.round_count % 50 == 0:
          return axl.Action.C

      # Analyze opponent's behavior every 20 rounds
      if self.round_count % 20 == 0:
          opponent_coop_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_coop_rate > 0.6:
              self.coop_prob = min(0.8, self.coop_prob + 0.05)
          elif opponent_coop_rate < 0.4:
              self.defect_prob = min(0.8, self.defect_prob + 0.05)

      # Adjust strategy in the last 100 rounds
      if self.round_count > 900:
          if self.score < opponent.score:
              self.defect_prob = min(0.8, self.defect_prob + 0.05)

      # Tit-for-Tat variant
      if opponent.history:
          if opponent.history[-1] == axl.Action.C:
              return self._random.choice([axl.Action.C, axl.Action.D], p=[self.coop_prob, 1 - self.coop_prob])
          else:
              return self._random.choice([axl.Action.D, axl.Action.C], p=[self.defect_prob, 1 - self.defect_prob])

      # Default to cooperation if no history
      return axl.Action.C

# Aggressive Strategy:  This strategy aims to maximize personal gain and exploit
# opponents whenever possible. It begins by defecting (playing D) for the first
# few rounds to establish dominance. After that, it primarily continues to
# defect but occasionally cooperates to test the opponent's response. If the
# opponent consistently cooperates, this strategy will exploit them by defecting
# more frequently. However, if the opponent retaliates with defection, this
# strategy will alternate between cooperation and defection in an unpredictable
# pattern to keep the opponent off-balance. The strategy also keeps track of the
# opponent's moves and if it detects a pattern, it will attempt to exploit it.
# In the last few rounds, it will always defect to maximize final gains. This
# strategy prioritizes short-term gains over long-term cooperation and aims to
# outscore the opponent rather than achieve mutual benefit.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables if it's the first round
      if len(self.history) == 0:
          self.defect_count = 0
          self.exploit_threshold = 5
          self.pattern_length = 5
          self.last_rounds = 10

      # Always defect in the last few rounds
      if len(self.history) >= 1000 - self.last_rounds:
          return axl.Action.D

      # Start with defection for the first few rounds
      if len(self.history) < self.exploit_threshold:
          return axl.Action.D

      # Check if opponent has a detectable pattern
      if len(opponent.history) >= self.pattern_length * 2:
          pattern = opponent.history[-self.pattern_length:]
          if pattern == opponent.history[-2*self.pattern_length:-self.pattern_length]:
              # Exploit the pattern by playing the opposite of the next expected move
              return axl.Action.D if pattern[0] == axl.Action.C else axl.Action.C

      # Calculate cooperation rate of opponent
      opp_coop_rate = opponent.cooperations / len(opponent.history) if len(opponent.history) > 0 else 0

      # Exploit cooperative opponents
      if opp_coop_rate > 0.7:
          self.defect_count += 1
          if self.defect_count > 3:
              self.defect_count = 0
              return axl.Action.C  # Occasional cooperation to maintain exploitation
          return axl.Action.D

      # Against less cooperative opponents, use an unpredictable pattern
      if self._random.random() < 0.7:  # 70% chance to defect
          return axl.Action.D
      else:
          return axl.Action.C

# Cooperative Strategy:  This strategy focuses on fostering mutual cooperation
# for long-term benefit. It begins by cooperating (playing C) and continues to
# do so as long as the opponent reciprocates. If the opponent defects, this
# strategy will forgive once and cooperate in the next round, giving them a
# chance to return to mutual cooperation. If the opponent defects twice in a
# row, this strategy will respond with a single defection as a warning, then
# return to cooperation. It aims to establish a pattern of mutual cooperation
# but is not entirely passive. The strategy also includes occasional random
# cooperations even after being defected against, to encourage a return to
# cooperative behavior. If a long streak of mutual cooperation is achieved, it
# might occasionally defect to test the opponent's commitment to cooperation,
# but will quickly return to cooperation afterward. In the final rounds, it
# maintains its cooperative stance, believing in the power of consistent
# behavior. This strategy prioritizes creating a cooperative environment that
# benefits both players over time, even if it means occasionally scoring less in
# the short term.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables if it's the first round
      if len(self.history) == 0:
          self.consecutive_defections = 0
          self.cooperation_streak = 0
          return axl.Action.C

      # Get the last moves
      my_last_move = self.history[-1]
      opp_last_move = opponent.history[-1]

      # Update consecutive defections and cooperation streak
      if opp_last_move == axl.Action.D:
          self.consecutive_defections += 1
          self.cooperation_streak = 0
      else:
          self.consecutive_defections = 0
          self.cooperation_streak += 1

      # Forgive once
      if self.consecutive_defections == 1:
          return axl.Action.C

      # Respond with a single defection as a warning
      if self.consecutive_defections == 2:
          self.consecutive_defections = 0
          return axl.Action.D

      # Occasional random cooperation to encourage return to cooperation
      if opp_last_move == axl.Action.D and self._random.random() < 0.1:
          return axl.Action.C

      # Test opponent's commitment after a long cooperation streak
      if self.cooperation_streak > 20 and self._random.random() < 0.05:
          self.cooperation_streak = 0
          return axl.Action.D

      # Default to cooperation
      return axl.Action.C

# Neutral Strategy:  This strategy aims to balance cooperation and competition,
# adapting to the opponent's behavior while maintaining a middle ground. It
# starts with a tit-for-tat approach, cooperating in the first round and then
# mirroring the opponent's previous move. However, it incorporates several
# modifications to this basic structure:  1. Every 10 rounds, it will perform a
# "random" move regardless of the opponent's previous action, to avoid getting
# stuck in negative patterns and to probe for changes in the opponent's
# strategy.  2. If the opponent has cooperated for the last three rounds,
# there's a 10% chance this strategy will defect to test the opponent's response
# and potentially gain an advantage.  3. If the opponent has defected for the
# last three rounds, there's a 10% chance this strategy will cooperate to
# potentially break a cycle of mutual defection.  4. It keeps track of the
# overall cooperation rate of the opponent. If this rate falls below 30%, the
# strategy becomes more likely to defect. If it rises above 70%, the strategy
# becomes more likely to cooperate.  5. In the middle third of the game (rounds
# 334-666), it slightly favors cooperation to encourage long-term mutual
# benefit.  6. In the last 50 rounds, it reverts strictly to tit-for-tat to
# discourage last-minute exploitation.  This strategy aims to be responsive to
# the opponent's moves while maintaining its own balanced approach, neither too
# aggressive nor too cooperative.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize cooperation rate if it's the first round
      if len(self.history) == 0:
          self.opponent_cooperation_rate = 0
          return axl.Action.C

      # Update opponent's cooperation rate
      self.opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)

      # Every 10 rounds, make a random move
      if len(self.history) % 10 == 0:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Check last three opponent moves
      last_three = opponent.history[-3:]

      # 10% chance to defect if opponent cooperated last three rounds
      if len(last_three) == 3 and all(move == axl.Action.C for move in last_three):
          if self._random.random() < 0.1:
              return axl.Action.D

      # 10% chance to cooperate if opponent defected last three rounds
      if len(last_three) == 3 and all(move == axl.Action.D for move in last_three):
          if self._random.random() < 0.1:
              return axl.Action.C

      # Adjust strategy based on overall cooperation rate
      if self.opponent_cooperation_rate < 0.3:
          if self._random.random() < 0.7:
              return axl.Action.D
      elif self.opponent_cooperation_rate > 0.7:
          if self._random.random() < 0.7:
              return axl.Action.C

      # Slightly favor cooperation in the middle third of the game
      if 334 <= len(self.history) <= 666:
          if self._random.random() < 0.55:
              return axl.Action.C

      # Revert to strict tit-for-tat in the last 50 rounds
      if len(self.history) >= 950:
          return opponent.history[-1]

      # Default to tit-for-tat
      return opponent.history[-1]

# Aggressive Strategy:  This strategy aims to maximize personal gain and exploit
# the opponent's weaknesses, prioritizing short-term advantages over long-term
# cooperation. Here's how it works:  1. Start with a defection (D) on the first
# move to immediately establish a dominant position.  2. For the next few rounds
# (e.g., 5-10), alternate between C and D to gauge the opponent's reaction to
# both cooperation and defection.  3. If the opponent consistently cooperates
# (C) in response to your defections:    - Exploit this by playing D more
# frequently, aiming for a high percentage of D moves (e.g., 80-90% D).    -
# Occasionally play C to prevent the opponent from completely abandoning
# cooperation.  4. If the opponent retaliates with D after your defections:    -
# Temporarily increase cooperation for a few rounds to lull them into a false
# sense of security.    - Then suddenly switch back to a high rate of defection.
# 5. Implement a "probe and exploit" technique:    - Every 20-30 rounds, play a
# series of C moves.    - If the opponent reciprocates with C, immediately
# switch to D to exploit their cooperation.    - If they continue to defect,
# quickly return to aggressive play.  6. Keep track of the opponent's overall
# strategy:    - If they seem to be using a tit-for-tat or similar reactive
# strategy, try to manipulate it by strategically placing C moves to reset their
# behavior, then exploit with D.  7. In the last 100 rounds, ramp up the
# aggression:    - Increase the frequency of D plays to 90-95%.    - Only use C
# plays sparingly to keep the opponent guessing.  8. If at any point the
# opponent shows a consistent pattern of cooperation despite your aggression,
# exploit this fully by playing D almost exclusively.  9. Throughout the game,
# remain unpredictable by occasionally throwing in unexpected C moves, but
# always revert quickly to aggressive play.  This aggressive strategy
# prioritizes maximizing personal score through frequent defection and
# exploitation of the opponent's behavior, aiming for high individual gains
# rather than mutual benefit.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.round_counter = 0
          self.probe_counter = 0
          self.last_probe = 0
          self.opponent_coop_after_defect = 0
          self.opponent_defect_after_defect = 0

      self.round_counter += 1

      # Start with defection on the first move
      if self.round_counter == 1:
          return axl.Action.D

      # Alternate between C and D for the first 10 rounds
      if self.round_counter <= 10:
          return axl.Action.C if self.round_counter % 2 == 0 else axl.Action.D

      # Analyze opponent's behavior
      if len(self.history) > 1 and self.history[-1] == axl.Action.D:
          if opponent.history[-1] == axl.Action.C:
              self.opponent_coop_after_defect += 1
          else:
              self.opponent_defect_after_defect += 1

      # Exploit cooperative opponents
      if self.opponent_coop_after_defect > self.opponent_defect_after_defect:
          if self._random.random() < 0.15:  # 15% chance to cooperate
              return axl.Action.C
          return axl.Action.D

      # Probe and exploit technique
      if self.round_counter - self.last_probe >= 25:
          self.probe_counter = 5
          self.last_probe = self.round_counter

      if self.probe_counter > 0:
          self.probe_counter -= 1
          if self.probe_counter == 0 and opponent.history[-1] == axl.Action.C:
              return axl.Action.D
          return axl.Action.C

      # Increase aggression in the last 100 rounds
      if self.round_counter > 900:
          if self._random.random() < 0.05:  # 5% chance to cooperate
              return axl.Action.C
          return axl.Action.D

      # Default aggressive behavior
      if self._random.random() < 0.2:  # 20% chance to cooperate
          return axl.Action.C
      return axl.Action.D

# Cooperative Strategy:  This strategy aims to foster mutual cooperation and
# maintain a positive relationship with the opponent. Here's how it works:  1.
# Start by playing C (Cooperate) for the first few rounds (e.g., 5-10 rounds) to
# signal willingness to cooperate.  2. If the opponent consistently cooperates,
# continue playing C to maintain mutual cooperation and maximize long-term
# gains.  3. If the opponent defects, implement a forgiving tit-for-tat
# approach:    - Respond with D (Defect) in the next round to discourage
# exploitation.    - Return to C in the following round, giving the opponent a
# chance to restore cooperation.  4. If the opponent shows a pattern of
# alternating between C and D, try to synchronize by playing C when you expect
# them to play C, and D when you expect them to play D.  5. If the opponent
# consistently defects for an extended period (e.g., 10-15 consecutive rounds),
# switch to a more defensive strategy by playing D more frequently, but still
# occasionally play C to allow for the possibility of returning to cooperation.
# 6. In the last few rounds of the game (e.g., last 5-10 rounds), continue the
# established pattern rather than automatically defecting, to maintain the
# cooperative spirit.  7. Throughout the game, keep track of the overall
# cooperation rate. If it falls below a certain threshold (e.g., 40%), become
# more cautious and increase the frequency of D plays while still leaving room
# for cooperation.  This strategy aims to encourage and maintain cooperation
# while having some protection against persistent defectors, ultimately seeking
# to achieve a balance of high scores through mutual cooperation.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize variables
      rounds_played = len(self.history)
      initial_cooperation_rounds = 7
      forgiveness_threshold = 10
      defensive_threshold = 15
      cooperation_rate_threshold = 0.4
      end_game_rounds = 990

      # Start with cooperation for the first few rounds
      if rounds_played < initial_cooperation_rounds:
          return axl.Action.C

      # Calculate cooperation rates
      opponent_cooperation_rate = opponent.history.cooperations / rounds_played
      self_cooperation_rate = self.history.cooperations / rounds_played

      # Check if we're in the end game
      if rounds_played >= end_game_rounds:
          # Continue the established pattern
          return self.history[-1]

      # Implement forgiving tit-for-tat
      if opponent.history[-1] == axl.Action.D:
          if self.history[-1] == axl.Action.D:
              return axl.Action.C  # Forgive and return to cooperation
          else:
              return axl.Action.D  # Respond to defection with defection

      # Check for alternating pattern
      if rounds_played >= 4:
          if (opponent.history[-1] != opponent.history[-2] and
              opponent.history[-2] != opponent.history[-3] and
              opponent.history[-3] != opponent.history[-4]):
              # Predict next move based on alternating pattern
              return opponent.history[-1]

      # Check for consistent defection
      recent_opponent_moves = opponent.history[-defensive_threshold:]
      if recent_opponent_moves.count(axl.Action.D) >= forgiveness_threshold:
          if self._random.random() < 0.8:  # 80% chance to defect
              return axl.Action.D
          else:
              return axl.Action.C  # Occasional cooperation to allow return to cooperation

      # Check overall cooperation rate
      if opponent_cooperation_rate < cooperation_rate_threshold:
          if self._random.random() < 0.6:  # 60% chance to defect
              return axl.Action.D
          else:
              return axl.Action.C  # Occasional cooperation

      # Default to cooperation
      return axl.Action.C

# Neutral Strategy:  This strategy aims to balance cooperation and competition,
# adapting to the opponent's behavior while maintaining a moderate approach.
# Here's how it works:  1. Start with a mixed approach, alternating between C
# and D for the first few rounds (e.g., 5-10 rounds) to gather information about
# the opponent's strategy.  2. Keep track of the opponent's moves and calculate
# their cooperation rate.  3. Adjust your play based on the opponent's
# cooperation rate:    - If their cooperation rate is above 60%, slightly
# increase your own cooperation rate to capitalize on mutual cooperation.    -
# If their cooperation rate is between 40% and 60%, mirror their overall
# strategy by matching their cooperation rate.    - If their cooperation rate is
# below 40%, slightly decrease your own cooperation rate to protect against
# exploitation.  4. Implement a pattern recognition system:    - Look for
# repeating patterns in the opponent's moves (e.g., CCCD, DDDC).    - If a
# pattern is detected, exploit it by playing the optimal counter-move.  5.
# Occasionally introduce random moves (about 10% of the time) to prevent the
# opponent from easily predicting your strategy.  6. After every 100 rounds,
# reassess the overall game state:    - If you're significantly behind in score,
# become slightly more aggressive by increasing D plays.    - If you're
# significantly ahead, become slightly more cooperative to maintain the lead.
# 7. In the last 50 rounds, if the scores are close, gradually increase the
# frequency of D plays to secure your position, but avoid switching to full
# defection to maintain unpredictability.  8. Throughout the game, maintain
# flexibility and avoid getting locked into a single pattern of play. Be ready
# to switch strategies if the opponent's behavior changes significantly.  This
# neutral strategy aims to adapt to various opponent types while maintaining a
# balance between cooperation and competition, seeking to achieve consistent,
# above-average scores across different scenarios.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize attributes if not already set
      if not self.history:
          self.round_count = 0
          self.pattern_length = 4
          self.last_reassessment = 0
          self.opponent_pattern = []

      self.round_count += 1

      # Start with mixed approach for the first 10 rounds
      if self.round_count <= 10:
          return axl.Action.C if self.round_count % 2 == 0 else axl.Action.D

      # Calculate opponent's cooperation rate
      opp_coop_rate = opponent.history.cooperations / len(opponent.history)

      # Pattern recognition
      if len(opponent.history) >= self.pattern_length:
          current_pattern = opponent.history[-self.pattern_length:]
          if current_pattern == self.opponent_pattern:
              return axl.Action.C if current_pattern[-1] == axl.Action.D else axl.Action.D
          self.opponent_pattern = current_pattern

      # Adjust play based on opponent's cooperation rate
      if opp_coop_rate > 0.6:
          coop_chance = min(opp_coop_rate + 0.1, 0.9)
      elif 0.4 <= opp_coop_rate <= 0.6:
          coop_chance = opp_coop_rate
      else:
          coop_chance = max(opp_coop_rate - 0.1, 0.1)

      # Reassess every 100 rounds
      if self.round_count - self.last_reassessment >= 100:
          self.last_reassessment = self.round_count
          score_diff = self.score - opponent.score
          if score_diff < -50:
              coop_chance -= 0.1
          elif score_diff > 50:
              coop_chance += 0.1

      # Last 50 rounds strategy
      if self.round_count > 950:
          if abs(self.score - opponent.score) < 25:
              coop_chance -= 0.02 * (1000 - self.round_count) / 50

      # Introduce randomness
      if self._random.random() < 0.1:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Make the final decision
      return axl.Action.C if self._random.random() < coop_chance else axl.Action.D
