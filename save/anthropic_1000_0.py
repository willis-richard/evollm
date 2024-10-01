import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Revised Aggressive Strategy:  This strategy aims to maximize personal gain and
# exploit opponents, with a strong bias towards defection (D), while
# incorporating more adaptive elements.  1. Start the game by playing D for the
# first 3 rounds to establish an aggressive stance.  2. If the opponent plays C
# twice in a row, exploit this by playing D for the next 3 rounds.  3. If the
# opponent plays D, retaliate by playing D for the next 2 rounds.  4. Every 5-15
# rounds (randomly determined), play C once to probe the opponent's reaction and
# potentially induce cooperation.  5. If the opponent has played C for more than
# 60% of the last 20 rounds, switch to playing C for 3 rounds to potentially
# establish mutual cooperation.  6. If mutual cooperation (C,C) has been
# achieved for 10 consecutive rounds, introduce a 20% chance of playing D after
# each subsequent round of mutual cooperation to test the opponent's response
# and exploit if possible.  7. In all other cases, play D.  8. For the last 10
# rounds of the game:    a. If mutual cooperation has been established for 20+
# rounds, continue playing C.    b. Otherwise, always play D to maximize final
# score.  9. Throughout the game, keep track of the cumulative score difference
# between you and your opponent. If you're significantly behind (e.g., more than
# 20 points), increase the frequency of D plays by 10% to catch up.  This
# revised strategy maintains an aggressive stance while being more adaptive to
# the opponent's behavior. It allows for quicker responses to cooperation,
# introduces unpredictability in probing, and is more flexible in the endgame,
# potentially leading to better performance against a wider range of opponents.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.probe_round = self._random.randint(5, 16)
          self.exploit_count = 0
          self.retaliate_count = 0
          self.cooperative_streak = 0
          self.consecutive_cc_count = 0
          self.aggressive_boost = 0

      # First 3 rounds
      if len(self.history) < 3:
          return axl.Action.D

      # Last 10 rounds
      if len(self.history) >= 990:
          if self.consecutive_cc_count >= 20:
              return axl.Action.C
          else:
              return axl.Action.D

      # Exploit consecutive C
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          self.exploit_count = 3
      if self.exploit_count > 0:
          self.exploit_count -= 1
          return axl.Action.D

      # Retaliate against D
      if opponent.history[-1] == axl.Action.D:
          self.retaliate_count = 2
      if self.retaliate_count > 0:
          self.retaliate_count -= 1
          return axl.Action.D

      # Probe every 5-15 rounds
      if len(self.history) == self.probe_round:
          self.probe_round = len(self.history) + self._random.randint(5, 16)
          return axl.Action.C

      # Switch to C if opponent played C for >60% of last 20 rounds
      recent_20 = opponent.history[-20:]
      if len(recent_20) == 20 and recent_20.count(axl.Action.C) / 20 > 0.6:
          self.cooperative_streak = 3
      if self.cooperative_streak > 0:
          self.cooperative_streak -= 1
          return axl.Action.C

      # 20% chance of D after 10 rounds of mutual cooperation
      if len(self.history) >= 10 and self.history[-10:] == opponent.history[-10:] == [axl.Action.C] * 10:
          self.consecutive_cc_count += 1
          if self.consecutive_cc_count >= 10 and self._random.random() < 0.2:
              return axl.Action.D
      else:
          self.consecutive_cc_count = 0

      # Adjust strategy based on score difference
      self.score_difference = self.score - opponent.score
      self.aggressive_boost = 0.1 if self.score_difference < -20 else 0

      # Default to D with adjusted probability
      if self._random.random() < 0.9 + self.aggressive_boost:
          return axl.Action.D
      else:
          return axl.Action.C

# Revised Aggressive Strategy:  This strategy aims to maximize personal gain
# while being more adaptive to opponent behavior, maintaining an overall
# aggressive stance.  1. Start the game by defecting (D).  2. Implement a
# simplified Tit-for-Tat with a bias towards defection:    a) If the opponent
# cooperated in the previous round, cooperate with a 70% probability and defect
# with a 30% probability.    b) If the opponent defected in the previous round,
# always defect.  3. Keep a short-term memory of the opponent's last 5 moves.
# 4. If the opponent has cooperated 4 or 5 times in the last 5 moves, defect for
# the next 2 rounds to exploit their cooperation, then return to the main
# strategy.  5. Every 20 rounds, analyze the opponent's behavior:    a) If
# they've cooperated more than 80% of the time, switch to always defecting for
# the next 10 rounds to exploit their forgiveness.    b) If they've defected
# more than 80% of the time, cooperate twice to test if they might switch to
# cooperation, then return to the main strategy.  6. In the last 100 rounds,
# slightly increase the bias towards defection:    a) If the opponent cooperated
# in the previous round, cooperate with a 60% probability and defect with a 40%
# probability.    b) Continue always defecting if the opponent defected in the
# previous round.  7. If at any point the opponent seems to be using a
# recognizable strategy (like pure Tit-for-Tat or Always Cooperate), adjust the
# strategy to exploit that specific behavior for the next 20 rounds, then
# reassess.  This revised strategy maintains an aggressive stance while being
# more adaptive to the opponent's behavior. It uses a simplified Tit-for-Tat
# base with a defection bias, incorporates short-term memory to identify
# patterns, and includes mechanisms to exploit overly cooperative opponents. The
# strategy also has provisions for adjusting to recognizable opponent strategies
# and slightly modifies its behavior in the endgame without resorting to pure
# defection.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes
      if not self.history:
          self.short_term_memory = []
          self.exploit_cooperation_counter = 0
          self.exploit_forgiveness_counter = 0
          self.test_cooperation_counter = 0
          self.recognizable_strategy_counter = 0
          return axl.Action.D

      # Update short-term memory
      if len(opponent.history) > 0:
          self.short_term_memory.append(opponent.history[-1])
          if len(self.short_term_memory) > 5:
              self.short_term_memory.pop(0)

      # Last 100 rounds behavior
      if len(self.history) >= 900:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C if self._random.random() < 0.6 else axl.Action.D
          else:
              return axl.Action.D

      # Check if we're exploiting cooperation
      if self.exploit_cooperation_counter > 0:
          self.exploit_cooperation_counter -= 1
          return axl.Action.D

      # Check if we're exploiting forgiveness
      if self.exploit_forgiveness_counter > 0:
          self.exploit_forgiveness_counter -= 1
          return axl.Action.D

      # Check if we're testing cooperation
      if self.test_cooperation_counter > 0:
          self.test_cooperation_counter -= 1
          return axl.Action.C

      # Check if we're exploiting a recognizable strategy
      if self.recognizable_strategy_counter > 0:
          self.recognizable_strategy_counter -= 1
          return axl.Action.D

      # Analyze opponent's behavior every 20 rounds
      if len(self.history) % 20 == 0 and len(self.history) > 0:
          cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if cooperation_rate > 0.8:
              self.exploit_forgiveness_counter = 10
              return axl.Action.D
          elif cooperation_rate < 0.2:
              self.test_cooperation_counter = 2
              return axl.Action.C

      # Check short-term memory for high cooperation
      if len(self.short_term_memory) == 5 and self.short_term_memory.count(axl.Action.C) >= 4:
          self.exploit_cooperation_counter = 2
          return axl.Action.D

      # Check for recognizable strategies
      if len(self.history) % 20 == 0:
          if all(move == axl.Action.C for move in opponent.history[-20:]):
              self.recognizable_strategy_counter = 20
              return axl.Action.D
          elif opponent.history[-20:] == self.history[-20:]:
              self.recognizable_strategy_counter = 20
              return axl.Action.D

      # Main strategy (simplified Tit-for-Tat with defection bias)
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C if self._random.random() < 0.7 else axl.Action.D
      else:
          return axl.Action.D

# Revised Cooperative Strategy:  This strategy aims to foster cooperation while
# protecting against exploitation and adapting to the opponent's behavior.
# Here's the improved version:  1. Start by playing C (Cooperate) for the first
# move.  2. For subsequent moves:    - If the opponent played C in the previous
# round, continue playing C.    - If the opponent played D in the previous
# round, use a Tit-for-Two-Tats approach: only retaliate with D after two
# consecutive defections from the opponent. After playing D once, return to C.
# 3. Every 75 moves, play C regardless of the opponent's previous moves. This
# serves as a "olive branch" to potentially reset a cycle of mutual defection,
# but is less frequent to reduce exploitability.  4. Implement a simple pattern
# recognition:    - If the opponent has alternated C and D for the last 6 moves,
# predict their next move and play D if they're expected to play C. This
# counters alternating strategies.    - If the opponent has played the same move
# for the last 5 moves, assume they'll continue and respond accordingly (C if
# they've been cooperating, D if they've been defecting).  5. Adjust based on
# the overall score:    - If you're behind by more than 20 points, slightly
# increase the probability of playing D (by 10%) for the next 10 moves.    - If
# you're ahead by more than 30 points, slightly increase the probability of
# playing C (by 10%) for the next 10 moves.  6. Introduce a small random
# element: With a 5% chance, make a random move instead of following the
# strategy. This makes the strategy less predictable.  7. In the last 15 moves
# of the game, always play C to encourage final cooperation and avoid
# unnecessary retaliation, unless the opponent has defected 3 or more times in
# the last 5 moves.  This revised strategy maintains its cooperative nature
# while being more robust against exploitation. It adapts to the opponent's
# behavior and the game state, includes a degree of unpredictability, and still
# aims to foster cooperation in the long run.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes
      if not self.history:
          self.consecutive_defections = 0
          self.score_adjustment_moves = 0
          self.adjust_probability = 0

      # Rule 1: Start with C
      if len(self.history) == 0:
          return axl.Action.C

      # Get the last move
      opp_last_move = opponent.history[-1]

      # Update consecutive defections
      if opp_last_move == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0

      # Rule 6: Random element (5% chance)
      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Rule 3: Play C every 75 moves
      if len(self.history) % 75 == 0:
          return axl.Action.C

      # Rule 7: Last 15 moves
      if len(self.history) >= 985:
          last_five = opponent.history[-5:]
          if last_five.count(axl.Action.D) >= 3:
              return axl.Action.D
          return axl.Action.C

      # Rule 4: Pattern recognition
      if len(opponent.history) >= 6:
          last_six = opponent.history[-6:]
          if last_six == [axl.Action.C, axl.Action.D] * 3:
              return axl.Action.D if last_six[-1] == axl.Action.D else axl.Action.C

      if len(opponent.history) >= 5:
          last_five = opponent.history[-5:]
          if all(move == axl.Action.C for move in last_five):
              return axl.Action.C
          if all(move == axl.Action.D for move in last_five):
              return axl.Action.D

      # Rule 5: Adjust based on overall score
      score_difference = self.score - opponent.score
      if self.score_adjustment_moves == 0:
          if score_difference < -20:
              self.adjust_probability = 0.1
              self.score_adjustment_moves = 10
          elif score_difference > 30:
              self.adjust_probability = -0.1
              self.score_adjustment_moves = 10

      # Apply score-based adjustment
      if self.score_adjustment_moves > 0:
          self.score_adjustment_moves -= 1
          if self._random.random() < abs(self.adjust_probability):
              return axl.Action.D if self.adjust_probability > 0 else axl.Action.C
      else:
          self.adjust_probability = 0

      # Rule 2: Tit-for-Two-Tats
      if self.consecutive_defections >= 2:
          return axl.Action.D

      # Default to cooperation
      return axl.Action.C

# Revised Cooperative Strategy:  This strategy aims to establish and maintain
# mutual cooperation while protecting against exploitation. Here's how it works:
# 1. Start by playing C (Cooperate) for the first move.  2. For subsequent
# moves:    - If the opponent played C in the previous round, play C.    - If
# the opponent played D in the previous round, retaliate by playing D with a 70%
# probability. Otherwise, forgive and play C.  3. Keep a running tally of the
# opponent's cooperation rate over the last 50 moves. Adjust your strategy based
# on this rate:    - If the cooperation rate is above 80%, always play C.    -
# If the cooperation rate falls below 40%, increase the retaliation probability
# to 90% for the next 20 moves.  4. Every 50 rounds, play C regardless of the
# opponent's previous move, as a gesture of goodwill and to potentially break
# out of any negative cycles.  5. Introduce a small element of randomness: With
# a 5% chance each round, deviate from the above rules and choose C or D
# randomly. This makes the strategy less predictable.  6. In the last round of
# the game, always play C.  This revised strategy maintains a cooperative
# approach while being more robust against exploitation. It adapts to the
# opponent's overall behavior, has a stronger response to consistent defection,
# and includes a small element of unpredictability. The strategy aims to
# encourage cooperation but is prepared to protect itself against overly
# aggressive opponents.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes
      if not self.history:
          self.retaliation_prob = 0.7
          self.retaliation_count = 0
          self.cooperation_sum = 0
          self.cooperation_history_length = 0

      # Last round of the game
      if len(self.history) == 999:
          return axl.Action.C

      # Every 50 rounds, play C as a gesture of goodwill
      if len(self.history) % 50 == 0 and len(self.history) > 0:
          return axl.Action.C

      # 5% chance of random action
      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Update cooperation history
      if len(self.history) > 0:
          if opponent.history[-1] == axl.Action.C:
              self.cooperation_sum += 1
          self.cooperation_history_length += 1
          if self.cooperation_history_length > 50:
              self.cooperation_sum -= 1 if opponent.history[-51] == axl.Action.C else 0
              self.cooperation_history_length = 50

      # Calculate cooperation rate
      cooperation_rate = self.cooperation_sum / self.cooperation_history_length if self.cooperation_history_length > 0 else 0.5

      # Adjust strategy based on cooperation rate
      if cooperation_rate > 0.8:
          return axl.Action.C
      elif cooperation_rate < 0.4:
          self.retaliation_prob = 0.9
          self.retaliation_count = 20

      # Decrease retaliation count and reset probability if needed
      if self.retaliation_count > 0:
          self.retaliation_count -= 1
      else:
          self.retaliation_prob = 0.7

      # Respond to opponent's last move
      if len(self.history) == 0 or opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D if self._random.random() < self.retaliation_prob else axl.Action.C

# Certainly. Here's the revised neutral strategy, taking into account the
# feedback:  Neutral Strategy: "Adaptive Tit-for-Tat with Calibrated
# Forgiveness"  1. Start by cooperating (C) in the first round.  2. For
# subsequent rounds:    - If the opponent cooperated in the previous round,
# cooperate (C).    - If the opponent defected in the previous round, defect
# (D).    - Exception: For the first defection by the opponent, cooperate in the
# next round. Only switch to defection if the opponent defects twice in a row.
# 3. Every 10 rounds, assess the opponent's behavior:    - If the opponent has
# cooperated in at least 7 out of the last 10 rounds, cooperate (C) in the next
# round regardless of their last move.    - This introduces a forgiving element
# to encourage mutual cooperation.  4. If caught in a cycle of mutual defection:
# - Have a (10 / number of consecutive mutual defections)% chance of cooperating
# to attempt breaking the cycle.    - This decreasing probability makes the
# strategy less exploitable while still providing opportunities to break
# deadlocks.  5. Every 20 rounds, if the opponent has cooperated for the last 5
# consecutive rounds:    - Have a 10% chance of defecting to probe for
# exploitation opportunities.    - This occasional defection takes advantage of
# the game's payoff structure.  6. In the last 10 rounds of the game:    -
# Adjust cooperation probability based on the opponent's overall cooperation
# rate.    - If their cooperation rate is x%, cooperate with (x+10)%
# probability, capped at 100%.    - This creates a more nuanced end-game
# strategy that adapts smoothly to the opponent's overall behavior.  7.
# Throughout the game, keep track of the cumulative score difference between you
# and your opponent:    - If you're trailing by more than 20 points, slightly
# increase your defection rate (by 5%) for the next 10 rounds.    - If you're
# leading by more than 20 points, slightly increase your cooperation rate (by
# 5%) for the next 10 rounds.    - This helps to balance competitiveness with
# cooperation based on the game state.  This revised strategy maintains its
# neutral character while being more adaptive to the specific payoff structure
# of the game and various opponent behaviors. It balances cooperation and
# competition, includes mechanisms to break out of negative cycles, and adjusts
# its behavior based on both short-term and long-term observations of the
# opponent's actions and the game state.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_mutual_defections = 0
          self.score_difference = 0
          self.defection_rate_adjustment = 0
          return axl.Action.C

      if len(self.history) == 1 and opponent.history[-1] == axl.Action.D:
          return axl.Action.C

      if len(self.history) % 10 == 0:
          recent_opponent_cooperations = sum(1 for action in opponent.history[-10:] if action == axl.Action.C)
          if recent_opponent_cooperations >= 7:
              return axl.Action.C

      if len(self.history) % 20 == 0 and len(opponent.history) >= 5:
          if all(action == axl.Action.C for action in opponent.history[-5:]):
              print("Triggered 1")
              if self._random.random() < 0.1:
                  print("Triggered 2")
                  return axl.Action.D
          else:
              print(f"{opponent.history[-5:]}")


      if len(self.history) > 990:
          opponent_cooperation_rate = opponent.cooperations / len(opponent.history)
          cooperation_probability = min(opponent_cooperation_rate + 0.1, 1.0)
          if self._random.random() < cooperation_probability:
              return axl.Action.C
          else:
              return axl.Action.D

      self.score_difference = self.score - opponent.score
      if abs(self.score_difference) > 20:
          self.defection_rate_adjustment = -0.05 if self.score_difference > 0 else 0.05
      else:
          self.defection_rate_adjustment = 0

      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_mutual_defections += 1
      else:
          self.consecutive_mutual_defections = 0

      if self.consecutive_mutual_defections > 0:
          cooperation_chance = min(10 / self.consecutive_mutual_defections, 1.0)
          if self._random.random() < cooperation_chance:
              return axl.Action.C

      if len(self.history) > 1 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          base_action = axl.Action.D
      else:
          base_action = axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D

      if self._random.random() < abs(self.defection_rate_adjustment):
          return axl.Action.D if self.defection_rate_adjustment > 0 else axl.Action.C
      return base_action

# Revised Neutral Strategy: "Adaptive Tit-for-Tat with Dynamic Forgiveness"  1.
# Start by cooperating (C) in the first round.  2. For subsequent rounds:    -
# If the opponent cooperated in the previous round, cooperate (C).    - If the
# opponent defected in the previous round, defect (D).  3. Every 10 rounds,
# check the opponent's cooperation rate:    - If they've cooperated more than
# 60% of the time, cooperate (C) in the next round regardless of their last
# move.    - If they've cooperated less than 40% of the time, defect (D) in the
# next round regardless of their last move.  4. Implement a dynamic forgiveness
# mechanism:    - After 3 consecutive defections (D) from your side, have a 50%
# chance to cooperate (C) once, regardless of the opponent's last move.    -
# This probability increases by 10% for each additional consecutive defection,
# up to a maximum of 80%.  5. Incorporate payoff-based decision making:    - If
# the opponent has defected twice in a row, increase the probability of
# defection to 80% in the next round, considering the high temptation payoff (5)
# for defecting against a cooperator.  6. Probe consistently cooperative
# opponents:    - If the opponent has cooperated for 10 consecutive rounds, have
# a 10% chance to defect in the next round.  7. Implement a gradual end-game
# adjustment:    - Starting from round 900, increase the probability of
# defection by 0.1% each round, even if the opponent cooperated in the previous
# round. This results in a maximum 10% increased chance of defection in the
# final round.  This revised strategy maintains a neutral stance while being
# more adaptive to opponent behavior and the game's payoff structure. It's less
# predictable due to the probabilistic elements in forgiveness and probing, and
# it gradually adjusts for end-game scenarios. The strategy aims to balance
# cooperation and defection effectively, responding to various opponent types
# while considering the specific payoffs of the game.

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
          self.forgiveness_probability = 0.5
          return axl.Action.C

      # End-game adjustment
      if len(self.history) >= 900:
          end_game_defection_increase = (len(self.history) - 900) * 0.001
          if self._random.random() < end_game_defection_increase:
              return axl.Action.D

      # 10-round cooperation rate check
      if len(self.history) % 10 == 0:
          cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if cooperation_rate > 0.6:
              return axl.Action.C
          elif cooperation_rate < 0.4:
              return axl.Action.D

      # Dynamic forgiveness mechanism
      if self.consecutive_defections >= 3:
          forgiveness_chance = min(0.8, 0.5 + 0.1 * (self.consecutive_defections - 3))
          if self._random.random() < forgiveness_chance:
              self.consecutive_defections = 0
              return axl.Action.C

      # Payoff-based decision making
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          if self._random.random() < 0.8:
              return axl.Action.D

      # Probe consistently cooperative opponents
      if len(opponent.history) >= 10 and all(action == axl.Action.C for action in opponent.history[-10:]):
          if self._random.random() < 0.1:
              return axl.Action.D

      # Basic Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0
          return axl.Action.C
      else:
          self.consecutive_defections += 1
          return axl.Action.D


# Revised Aggressive Strategy:  1. Start by playing D (defect) for the first 2-3
# rounds to establish initial dominance, then assess the opponent's response.
# 2. If the opponent plays C (cooperate) twice in a row, exploit this by playing
# D on the next round with an 80% probability. Otherwise, play C to maintain
# some unpredictability.  3. If the opponent plays D, retaliate by playing D for
# the next 3 rounds. However, if the opponent has a high overall cooperation
# rate (>50%), reduce this to 2 rounds of retaliation.  4. Probe for weaknesses
# by playing D every 8-12 rounds (randomly determined) regardless of the
# opponent's recent moves.  5. If the opponent has played C more than 65% of the
# time in the last 20 moves, switch to playing D for the next 5 moves to exploit
# their cooperation.  6. If the opponent seems to be using a tit-for-tat or
# similar reactive strategy, attempt to manipulate them by playing a sequence of
# C-D-D-C, then revert to the primary strategy.  7. In all other situations,
# play D with a 90% probability. Introduce a 10% chance of playing C to
# occasionally test for mutual cooperation opportunities.  8. Every 50 rounds,
# reassess the opponent's overall strategy and adjust the aggression level
# accordingly:    - If the opponent has been mostly cooperative (>60% C),
# increase the exploitation by raising the probability of D in steps 2 and 7.
# - If the opponent has been mostly defecting (>70% D), slightly increase the
# probability of C in steps 2 and 7 to probe for any shift in their strategy.
# 9. If mutual cooperation (C-C) has occurred for more than 5 consecutive
# rounds, defect once to test the opponent's response, then immediately revert
# to the primary strategy.  This revised strategy maintains an aggressive
# approach while incorporating more adaptability, unpredictability, and
# responsiveness to the opponent's behavior. It aims to exploit cooperative
# opponents more effectively while having some mechanisms to adjust against
# highly defensive strategies.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.retaliation_count = 0
          self.probe_counter = self._random.randint(8, 12)
          self.exploitation_count = 0
          self.manipulation_sequence = []
          self.consecutive_cc = 0
          self.defection_probability = 0.9

      if len(self.history) < 3:
          return axl.Action.D

      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          if self._random.random() < 0.8:
              return axl.Action.D
          else:
              return axl.Action.C

      if opponent.history[-1] == axl.Action.D:
          cooperation_rate = opponent.cooperations / len(opponent.history)
          self.retaliation_count = 2 if cooperation_rate > 0.5 else 3
          return axl.Action.D

      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D

      self.probe_counter -= 1
      if self.probe_counter == 0:
          self.probe_counter = self._random.randint(8, 12)
          return axl.Action.D

      recent_20_moves = opponent.history[-20:]
      if len(recent_20_moves) == 20 and recent_20_moves.count(axl.Action.C) / 20 > 0.65:
          self.exploitation_count = 5
          return axl.Action.D

      if self.exploitation_count > 0:
          self.exploitation_count -= 1
          return axl.Action.D

      # Improved tit-for-tat detection
      if len(self.history) >= 4 and all(self.history[i] == opponent.history[i-1] for i in range(-4, 0)):
          self.manipulation_sequence = [axl.Action.C, axl.Action.D, axl.Action.D, axl.Action.C]

      if self.manipulation_sequence:
          move = self.manipulation_sequence.pop(0)
          return move

      if len(self.history) % 50 == 0:
          overall_cooperation = opponent.cooperations / len(opponent.history)
          if overall_cooperation > 0.6:
              self.defection_probability = 0.95
          elif overall_cooperation < 0.3:
              self.defection_probability = 0.85
          else:
              self.defection_probability = 0.9

      if self.history[-1] == opponent.history[-1] == axl.Action.C:
          self.consecutive_cc += 1
      else:
          self.consecutive_cc = 0

      if self.consecutive_cc > 5:
          self.consecutive_cc = 0
          return axl.Action.D

      return axl.Action.D if self._random.random() < self.defection_probability else axl.Action.C

# Revised Aggressive Strategy:  This strategy aims to exploit opponents and
# maximize personal gain, with a strong bias towards defection (D) while
# incorporating some adaptive elements.  1. Start by playing D for the first 5
# rounds to establish dominance.  2. If the opponent plays C more than 60% of
# the time in the last 10 rounds, continue playing D to exploit their
# cooperation.  3. If the opponent plays D more than 60% of the time in the last
# 10 rounds, switch to a tit-for-tat strategy for the next 5 rounds to encourage
# cooperation, then revert to playing D.  4. Randomly probe the opponent's
# response by playing C once every 20-30 rounds (determine the exact round
# randomly within this range). If they respond with C, play D for the next 5
# rounds to exploit this cooperation.  5. If the opponent has played C for the
# last 5 consecutive rounds, play C for 2 rounds to test for sustained mutual
# cooperation. If the opponent cooperates in both rounds, continue this pattern
# (5D, 2C) to balance exploitation and mutual benefit.  6. Keep a running tally
# of the average score obtained from C and D moves. Every 100 rounds, adjust the
# probability of playing D based on this tally. If D moves yield higher average
# scores, increase D probability by 10% (up to a maximum of 90%). If C moves
# yield higher scores, decrease D probability by 10% (down to a minimum of 60%).
# 7. In all other cases, play D with the current probability (starting at 80%
# and adjusted as per point 6).  8. Continue this strategy until the last round
# of the game, where always play D to guarantee the best final move.  This
# revised strategy maintains an aggressive stance while incorporating more
# adaptability. It allows for potential periods of mutual cooperation if
# beneficial, includes a learning component to adjust based on success rates,
# and makes the probing mechanism less predictable. The strategy remains
# primarily aggressive but is better equipped to handle a variety of opponent
# behaviors and to maximize long-term payoffs.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.d_probability = 0.8
          self.c_count = 0
          self.d_count = 0
          self.c_score = 0
          self.d_score = 0
          self.probe_round = self._random.randint(20, 31)
          self.tit_for_tat_counter = 0
          self.consecutive_c_counter = 0
          self.exploit_counter = 0
          self.pattern_counter = 0
          self.last_score = 0

      if len(self.history) < 5:
          return axl.Action.D

      if len(self.history) % 100 == 0 and len(self.history) > 0:
          c_avg = self.c_score / max(self.c_count, 1)
          d_avg = self.d_score / max(self.d_count, 1)
          if d_avg > c_avg:
              self.d_probability = min(0.9, self.d_probability + 0.1)
          else:
              self.d_probability = max(0.6, self.d_probability - 0.1)

      last_10_opponent = opponent.history[-10:]
      if len(last_10_opponent) == 10:
          if last_10_opponent.count(axl.Action.C) > 6:
              return axl.Action.D
          elif last_10_opponent.count(axl.Action.D) > 6:
              self.tit_for_tat_counter = 5

      if self.tit_for_tat_counter > 0:
          self.tit_for_tat_counter -= 1
          return opponent.history[-1]

      if len(self.history) == self.probe_round:
          self.probe_round = len(self.history) + self._random.randint(20, 31)
          self.exploit_counter = 5
          return axl.Action.C

      if self.exploit_counter > 0:
          self.exploit_counter -= 1
          return axl.Action.D

      if opponent.history[-5:].count(axl.Action.C) == 5:
          self.consecutive_c_counter = 2
          self.pattern_counter = 7
          return axl.Action.C

      if self.pattern_counter > 0:
          self.pattern_counter -= 1
          if self.pattern_counter > 5:
              if opponent.history[-1] == axl.Action.D:
                  self.pattern_counter = 0
                  return axl.Action.D
              return axl.Action.C
          return axl.Action.D

      if len(self.history) == 999:
          return axl.Action.D

      action = axl.Action.D if self._random.random() < self.d_probability else axl.Action.C

      move_score = self.score - self.last_score
      self.last_score = self.score

      if action == axl.Action.C:
          self.c_count += 1
          self.c_score += move_score
      else:
          self.d_count += 1
          self.d_score += move_score

      return action

# Revised Aggressive Strategy:  This strategy aims to maximize personal gain
# while exploiting cooperative opponents and adapting to various opponent
# behaviors. It primarily defects but incorporates strategic cooperation and
# retaliation mechanisms.  1. Start by playing D for the first 5 rounds.  2.
# Every 10-15 rounds (randomly chosen), play C once to probe the opponent's
# strategy.  3. If the opponent has played C at least 3 times in the last 5
# rounds:    a. Play C with 90% probability (10% chance to play D for
# unpredictability).    b. If the opponent responds with C, immediately play D
# to exploit their cooperation.  4. Keep track of the opponent's cooperation
# rate over the last 50 moves:    a. If it exceeds 70%, increase defection
# frequency by playing D for the next 3 rounds.    b. If it's below 30%,
# occasionally cooperate (20% chance) to potentially break out of mutual
# defection.  5. Retaliation mechanism: If the opponent plays D immediately
# after we cooperate twice in a row, defect for the next 5 rounds regardless of
# the opponent's moves.  6. If mutual defection has occurred for 10 consecutive
# rounds:    a. Play C with 90% probability (10% chance to play D for
# unpredictability).  7. In all other cases, play D.  8. Adaptive element: Every
# 100 rounds, evaluate the average score per round:    a. If it's below 2,
# slightly increase the probability of cooperation in steps 3 and 6 (up to a
# maximum of 95%).    b. If it's above 3, slightly decrease the probability of
# cooperation in steps 3 and 6 (down to a minimum of 85%).  This revised
# strategy maintains its aggressive nature while incorporating more
# adaptability, unpredictability, and responsiveness to the opponent's behavior.
# It aims to exploit cooperative opponents more effectively while having
# mechanisms to avoid getting stuck in low-scoring mutual defection cycles.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.probe_round = self._random.randint(10, 16)
          self.retaliation_count = 0
          self.mutual_defection_count = 0
          self.cooperation_probability = 0.9
          self.last_100_rounds_start = 0
          self.high_cooperation_count = 0

      # Start with D for the first 5 rounds
      if len(self.history) < 5:
          return axl.Action.D

      # Probe every 10-15 rounds
      if len(self.history) % self.probe_round == 0:
          self.probe_round = self._random.randint(10, 16)
          return axl.Action.C

      # Check opponent's cooperation rate in last 5 rounds
      recent_opponent_moves = opponent.history[-5:]
      if recent_opponent_moves.count(axl.Action.C) >= 3:
          if self._random.random() < self.cooperation_probability:
              if len(self.history) >= 2 and self.history[-1] == axl.Action.C and self.history[-2] == axl.Action.C:
                  return axl.Action.D
              return axl.Action.C
          return axl.Action.D

      # Check opponent's cooperation rate over last 50 moves
      if len(opponent.history) >= 50:
          recent_50_moves = opponent.history[-50:]
          cooperation_rate = recent_50_moves.count(axl.Action.C) / 50
          if cooperation_rate > 0.7:
              self.high_cooperation_count = 3
              return axl.Action.D
          elif self.high_cooperation_count > 0:
              self.high_cooperation_count -= 1
              return axl.Action.D
          elif cooperation_rate < 0.3 and self._random.random() < 0.2:
              return axl.Action.C

      # Retaliation mechanism
      if len(self.history) >= 2 and self.history[-1] == axl.Action.C and self.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.retaliation_count = 5
      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D

      # Check for mutual defection
      if len(self.history) >= 10:
          last_10_moves = list(zip(self.history[-10:], opponent.history[-10:]))
          if all(move == (axl.Action.D, axl.Action.D) for move in last_10_moves):
              self.mutual_defection_count += 1
              if self._random.random() < self.cooperation_probability:
                  return axl.Action.C
          else:
              self.mutual_defection_count = 0

      # Adaptive element
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          avg_score = (self.score - self.last_100_rounds_start) / 100
          self.last_100_rounds_start = self.score
          if avg_score < 2:
              self.cooperation_probability = min(0.95, self.cooperation_probability + 0.01)
          elif avg_score > 3:
              self.cooperation_probability = max(0.85, self.cooperation_probability - 0.01)

      # Default action
      return axl.Action.D

# Revised Cooperative Strategy:  This strategy aims to foster cooperation while
# protecting against exploitation. Here's the updated approach:  1. Start by
# playing C (cooperate) for the first 5 rounds to signal willingness to
# cooperate.  2. After the initial 5 rounds, use a "generous tit-for-tat"
# approach:    - If the opponent played C in the previous round, play C.    - If
# the opponent played D in the previous round, forgive with a 15% chance and
# play C; otherwise, play D.  3. Every 50 rounds, play C regardless of the
# opponent's last move, to attempt to reset the relationship if it has degraded
# into mutual defection.  4. Implement a pattern recognition system:    - If the
# opponent alternates D and C for more than 5 cycles, switch to always playing D
# for the next 5 rounds to discourage this behavior.  5. If the opponent has
# defected for 10 consecutive rounds, switch to a "cautious" mode for the next
# 20 rounds:    - In cautious mode, only cooperate if the opponent has
# cooperated in the last 3 out of 5 rounds.    - After 20 rounds, return to the
# normal strategy.  6. After a streak of opponent defections (5 or more),
# occasionally (with 10% probability) play C twice in a row to give a stronger
# signal for cooperation.  7. Implement a "super generous" mode:    - If mutual
# cooperation has been achieved for 20 consecutive rounds, forgive the next
# defection automatically to maintain the cooperative streak.  8. In the last 10
# rounds of the game:    - Calculate the opponent's overall cooperation rate.
# - If the rate is above 70%, play C; otherwise, play D.  This strategy
# maintains its cooperative nature while being more robust against various
# opponent behaviors. It includes mechanisms to encourage cooperation, protect
# against exploitation, and make more informed decisions in the endgame.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_defections = 0
          self.cautious_mode = False
          self.cautious_mode_rounds = 0
          self.alternating_pattern_count = 0
          self.mutual_cooperation_streak = 0
          self.pattern_punishment_rounds = 0

      if len(self.history) < 5:
          return axl.Action.C

      if len(self.history) % 50 == 0:
          return axl.Action.C

      if len(self.history) >= 990:
          cooperation_rate = opponent.history.cooperations / len(opponent.history)
          return axl.Action.C if cooperation_rate > 0.7 else axl.Action.D

      if self.pattern_punishment_rounds > 0:
          self.pattern_punishment_rounds -= 1
          return axl.Action.D

      if self.cautious_mode:
          self.cautious_mode_rounds += 1
          if self.cautious_mode_rounds >= 20:
              self.cautious_mode = False
              self.cautious_mode_rounds = 0
          else:
              recent_cooperation = sum(1 for action in opponent.history[-5:] if action == axl.Action.C)
              return axl.Action.C if recent_cooperation >= 3 else axl.Action.D

      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.C]:
          self.alternating_pattern_count += 1
      else:
          self.alternating_pattern_count = 0

      if self.alternating_pattern_count > 5:
          self.alternating_pattern_count = 0
          self.pattern_punishment_rounds = 5
          return axl.Action.D

      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          self.mutual_cooperation_streak = 0
      else:
          self.consecutive_defections = 0
          self.mutual_cooperation_streak += 1

      if self.consecutive_defections == 10:
          self.cautious_mode = True
          self.cautious_mode_rounds = 0

      if self.consecutive_defections >= 5 and self._random.random() < 0.1:
          return axl.Action.C

      if self.mutual_cooperation_streak >= 20 and opponent.history[-1] == axl.Action.D:
          self.mutual_cooperation_streak = 0
          return axl.Action.C

      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.C if self._random.random() < 0.15 else axl.Action.D

# Revised Cooperative Strategy:  This strategy aims to establish and maintain
# mutual cooperation for the highest long-term payoff while protecting against
# exploitation. It begins by playing C (Cooperate) and then follows these rules:
# 1. Always play C if the opponent played C in the previous round.  2. If the
# opponent plays D (Defect), use a "tit-for-two-tats" approach: only defect
# after two consecutive defections from the opponent.  3. Keep track of the
# opponent's cooperation rate. If it falls below 50%, become more cautious by
# switching to a "tit-for-tat" strategy (immediately reciprocate the opponent's
# previous move) until their cooperation rate improves.  4. Every 45-55 rounds
# (randomly determined), play C regardless of the opponent's previous move, as a
# gesture of goodwill and to potentially break out of any negative cycles.  5.
# After three consecutive rounds of mutual defection, offer a "peace offering"
# by playing C for two rounds, regardless of the opponent's moves. This serves
# as a "carrot and stick" approach to encourage cooperation.  6. Maintain this
# strategy throughout the game, including the penultimate rounds. Only in the
# final round, play C regardless of the opponent's previous move as a last
# gesture of cooperation.  7. If at any point the opponent's defection rate
# exceeds 80% over the last 50 moves, switch to a purely defensive "tit-for-tat"
# strategy for the next 50 moves before reassessing.  This revised strategy
# remains cooperative at its core but incorporates more sophisticated mechanisms
# to protect against exploitation and encourage cooperation from various types
# of opponents. It adapts to the opponent's behavior while still providing
# opportunities for mutual cooperation to emerge and persist.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.opponent_defection_count = 0
          self.mutual_defection_count = 0
          self.peace_offering_counter = 0
          self.tit_for_tat_mode = False
          self.tit_for_tat_counter = 0
          self.last_goodwill_round = 0
          self.low_cooperation_mode = False

      if len(self.history) == 999:  # Final round
          return axl.Action.C

      if len(self.history) - self.last_goodwill_round >= 45:
          if self._random.randint(45, 55) == len(self.history) - self.last_goodwill_round:
              self.last_goodwill_round = len(self.history)
              return axl.Action.C

      if self.peace_offering_counter > 0:
          self.peace_offering_counter -= 1
          return axl.Action.C

      if len(self.history) >= 50:
          recent_defection_rate = sum(move == axl.Action.D for move in opponent.history[-50:]) / 50
          if recent_defection_rate > 0.8:
              self.tit_for_tat_mode = True
              self.tit_for_tat_counter = 50

      if self.tit_for_tat_mode:
          if self.tit_for_tat_counter > 0:
              self.tit_for_tat_counter -= 1
              if self.tit_for_tat_counter == 0:
                  self.tit_for_tat_mode = False
              return opponent.history[-1]

      if not opponent.history:
          return axl.Action.C

      if opponent.history[-1] == axl.Action.C:
          self.opponent_defection_count = 0
          self.mutual_defection_count = 0
          return axl.Action.C

      self.opponent_defection_count += 1

      if opponent.history[-1] == axl.Action.D and self.history[-1] == axl.Action.D:
          self.mutual_defection_count += 1
          if self.mutual_defection_count == 3:
              self.peace_offering_counter = 2
              self.mutual_defection_count = 0
              return axl.Action.C
      else:
          self.mutual_defection_count = 0

      if self.opponent_defection_count >= 2:
          return axl.Action.D

      cooperation_rate = opponent.history.cooperations / len(opponent.history)
      if cooperation_rate < 0.5:
          self.low_cooperation_mode = True
      elif cooperation_rate >= 0.5 and self.low_cooperation_mode:
          self.low_cooperation_mode = False

      if self.low_cooperation_mode:
          return opponent.history[-1]

      return axl.Action.C

# Revised Cooperative Strategy:  This strategy aims to foster cooperation while
# protecting against exploitation, taking into account the specific payoff
# structure. Here's the revised approach:  1. Start by playing C (Cooperate) for
# the first move.  2. Keep track of the opponent's cooperation rate over the
# last 20 moves.  3. For subsequent moves:    - If the opponent's cooperation
# rate is 80% or higher:      - Play C most of the time (90% chance).      -
# Occasionally play D (10% chance) to avoid being exploited by overly adaptive
# strategies.    - If the opponent's cooperation rate is between 50% and 80%:
# - Use a Tit-for-Tat strategy: play what the opponent played in the previous
# round.    - If the opponent's cooperation rate is below 50%:      - Use a Tit-
# for-Two-Tats strategy: only defect if the opponent has defected in the last
# two moves.  4. If mutual cooperation (C,C) has been achieved for 10
# consecutive rounds, continue playing C regardless of the cooperation rate
# calculation. This helps to establish and maintain beneficial long-term
# cooperation.  5. Every 40 rounds, play C regardless of the opponent's previous
# move. This serves as a "olive branch" to potentially reset a cycle of
# defection, but is less frequent than in the original strategy to reduce
# exploitation risk.  6. In the last 20 rounds of the game:    - If the overall
# cooperation rate of the opponent is above 70%, always play C.    - Otherwise,
# revert to the Tit-for-Tat strategy for these final rounds.  7. Consider the
# payoff structure in decision making:    - Be more inclined to cooperate when
# the opponent's cooperation rate is high, as the (3,3) payoff for mutual
# cooperation is significantly better than the (1,1) for mutual defection.    -
# However, be cautious about being exploited, as the (0,5) payoff for being
# defected against is the worst outcome.  This revised strategy maintains a
# cooperative stance but is more robust against exploitation. It adapts to the
# opponent's behavior over time, considers the specific payoff structure, and
# includes mechanisms to both establish cooperation and protect against
# consistent defection.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_cc = 0
          self.last_20_moves = []
          self.round_counter = 0
          return axl.Action.C

      self.round_counter += 1

      # Update last 20 moves
      self.last_20_moves.append(opponent.history[-1])
      if len(self.last_20_moves) > 20:
          self.last_20_moves.pop(0)

      # Calculate opponent's cooperation rate
      opp_coop_rate = sum(move == axl.Action.C for move in self.last_20_moves) / max(len(self.last_20_moves), 1)

      # Check for consecutive (C,C) and update counter
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.consecutive_cc += 1
      else:
          self.consecutive_cc = 0

      # If 10 consecutive (C,C), continue cooperating
      if self.consecutive_cc >= 10:
          return axl.Action.C

      # Every 40 rounds, offer an olive branch
      if self.round_counter % 40 == 0:
          return axl.Action.C

      # Last 20 rounds of the game
      if len(self.history) >= 980:
          overall_coop_rate = opponent.cooperations / len(opponent.history)
          if overall_coop_rate > 0.7:
              return axl.Action.C
          else:
              return opponent.history[-1]

      # Main strategy logic
      if opp_coop_rate >= 0.8:
          return axl.Action.C if self._random.random() < 0.9 else axl.Action.D
      elif 0.5 <= opp_coop_rate < 0.8:
          return opponent.history[-1]
      else:
          if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C

# Revised Neutral Strategy: "Adaptive Tit-for-Tat with Smart Forgiveness"  1.
# Start by cooperating (C) in the first round.  2. For subsequent rounds:    -
# If the opponent cooperated in the previous round, cooperate (C).    - If the
# opponent defected in the previous round, defect (D).  3. Every 10 rounds,
# evaluate the opponent's recent and overall behavior:    - If the opponent has
# cooperated in at least 6 out of the last 10 rounds, cooperate (C) in the next
# round regardless of their last move.    - Track the opponent's overall
# cooperation rate. If it's above 60%, increase the likelihood of forgiveness by
# cooperating with a 70% probability even if they defected last round.  4.
# Randomly cooperate with a 5% chance, even if the strategy would normally call
# for defection:    - This adds a small element of unpredictability and allows
# for potential recovery of cooperation.    - However, if the opponent's overall
# defection rate is above 70%, reduce this random cooperation to 2%.  5. If
# mutual defection (D,D) has occurred for several consecutive rounds:    - After
# 5 rounds of mutual defection, cooperate (C) with an 80% probability.    - This
# probability increases to 90% after 7 rounds and 100% after 10 rounds of mutual
# defection.  6. Implement an exploitation detection mechanism:    - If the
# opponent's defection rate increases by more than 20% after a forgiveness
# event, reduce the frequency of forgiveness for the next 50 rounds.  7. End-
# game strategy:    - In the last 50 rounds of the game:      - If the
# opponent's overall cooperation rate is below 40%, increase the probability of
# defection by 10%.      - If the opponent's overall cooperation rate is above
# 60%, maintain the standard strategy to preserve potential mutual cooperation.
# This revised strategy maintains a neutral approach while incorporating more
# adaptive elements to handle various opponent behaviors and game stages. It
# balances cooperation and defection based on short-term and long-term opponent
# actions, includes smart forgiveness and exploitation detection, and considers
# end-game scenarios.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_mutual_defections = 0
          self.forgiveness_reduction = 0
          self.last_forgiveness_round = 0
          self.overall_cooperation_rates = []

      if len(self.history) == 0:
          return axl.Action.C

      opponent_last_move = opponent.history[-1]
      opponent_cooperation_rate = opponent.cooperations / len(opponent.history)
      opponent_defection_rate = opponent.defections / len(opponent.history)

      self.overall_cooperation_rates.append(opponent_cooperation_rate)

      # Evaluate opponent's recent behavior every 10 rounds
      if len(self.history) % 10 == 0 and len(self.history) >= 10:
          recent_cooperations = sum(1 for move in opponent.history[-10:] if move == axl.Action.C)
          if recent_cooperations >= 6:
              self.last_forgiveness_round = len(self.history)
              return axl.Action.C

      # Increase forgiveness likelihood if overall cooperation rate is high
      if opponent_cooperation_rate > 0.6:
          if opponent_last_move == axl.Action.D and self._random.random() < 0.7:
              if self.forgiveness_reduction == 0:
                  self.last_forgiveness_round = len(self.history)
                  return axl.Action.C

      # Random cooperation with reduced probability for highly defective opponents
      if opponent_last_move == axl.Action.D:
          random_coop_chance = 0.05 if opponent_defection_rate <= 0.7 else 0.02
          if self._random.random() < random_coop_chance:
              return axl.Action.C

      # Handle consecutive mutual defections
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_mutual_defections += 1
      else:
          self.consecutive_mutual_defections = 0

      if self.consecutive_mutual_defections >= 5:
          if self.consecutive_mutual_defections >= 10:
              return axl.Action.C
          elif self.consecutive_mutual_defections >= 7:
              if self._random.random() < 0.9:
                  return axl.Action.C
          elif self._random.random() < 0.8:
              return axl.Action.C

      # Exploitation detection
      if len(self.history) - self.last_forgiveness_round == 50:
          recent_defection_rate = opponent.history[-50:].count(axl.Action.D) / 50
          if recent_defection_rate > opponent_defection_rate + 0.2:
              self.forgiveness_reduction = 50

      if self.forgiveness_reduction > 0:
          self.forgiveness_reduction -= 1

      # End-game strategy
      if len(self.history) >= 950:
          if opponent_cooperation_rate < 0.4:
              if self._random.random() < 0.1:
                  return axl.Action.D
          elif opponent_cooperation_rate > 0.6:
              return opponent_last_move  # Maintain standard strategy

      # Default Tit-for-Tat behavior
      return opponent_last_move

# Revised Neutral Strategy: "Adaptive Tit-for-Tat with Dynamic Forgiveness"  1.
# Start by cooperating (C) in the first round.  2. For subsequent rounds:    -
# If the opponent cooperated in the previous round, cooperate.    - If the
# opponent defected in the previous round, defect.  3. Implement a dynamic
# forgiveness mechanism:    - After 3 consecutive defections from the opponent,
# cooperate once to test if the opponent is willing to return to cooperation.
# - Reset the consecutive defection counter after forgiveness or if the opponent
# cooperates.  4. Include an adaptive element:    - Keep track of the opponent's
# cooperation rate over both the last 50 moves (short-term) and the last 200
# moves (long-term).    - Adjust the probability of cooperation based on a
# sliding scale:      - If the short-term cooperation rate is below 40%,
# decrease cooperation probability by 10%.      - If the short-term cooperation
# rate is above 60%, increase cooperation probability by 10%.      - If the
# long-term cooperation rate is below 30%, decrease cooperation probability by
# an additional 5%.      - If the long-term cooperation rate is above 70%,
# increase cooperation probability by an additional 5%.    - Cap the adjustments
# so that the final cooperation probability is always between 10% and 90%.  5.
# Implement an exploration mechanism:    - With a 5% probability, make a random
# move (C or D) to explore the opponent's reactions.  6. End-game behavior:    -
# In the last 20 rounds, gradually increase caution:      - If the opponent's
# cooperation rate in the last 30 moves is below 50%, increase the probability
# of defection by 2% each round.      - If the opponent's cooperation rate in
# the last 30 moves is above 50%, continue with the current strategy.  7. In any
# round, the final move decision is made based on the calculated cooperation
# probability. For example, if the cooperation probability is 70%, there's a 70%
# chance of cooperating and a 30% chance of defecting.  This revised strategy
# maintains the core Tit-for-Tat approach while incorporating more nuanced
# adaptation, dynamic forgiveness, exploration, and a cautious but not overly
# aggressive end-game behavior. It should be more robust against various
# opponent strategies and less exploitable, while still encouraging cooperation
# when possible.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_defections = 0
          self.cooperation_probability = 1.0
          self.rounds_played = 0

      self.rounds_played += 1

      # Calculate cooperation rates
      short_term_rate = opponent.cooperations / max(1, len(opponent.history)) if len(opponent.history) <= 50 else sum(1 for move in opponent.history[-50:] if move == axl.Action.C) / 50
      long_term_rate = opponent.cooperations / max(1, len(opponent.history)) if len(opponent.history) <= 200 else sum(1 for move in opponent.history[-200:] if move == axl.Action.C) / 200

      # Adjust cooperation probability
      if short_term_rate < 0.4:
          self.cooperation_probability -= 0.1
      elif short_term_rate > 0.6:
          self.cooperation_probability += 0.1

      if long_term_rate < 0.3:
          self.cooperation_probability -= 0.05
      elif long_term_rate > 0.7:
          self.cooperation_probability += 0.05

      # Cap cooperation probability
      self.cooperation_probability = max(0.1, min(0.9, self.cooperation_probability))

      # End-game behavior
      if self.rounds_played > 980:
          recent_rate = sum(1 for move in opponent.history[-30:] if move == axl.Action.C) / min(30, len(opponent.history))
          if recent_rate < 0.5:
              self.cooperation_probability = max(0.1, self.cooperation_probability - 0.02)

      # Exploration mechanism
      if self._random.random() < 0.05:
          return self._random.choice([axl.Action.C, axl.Action.D])

      # Dynamic forgiveness mechanism
      if len(self.history) > 0:
          if opponent.history[-1] == axl.Action.D:
              self.consecutive_defections += 1
          else:
              self.consecutive_defections = 0

          if self.consecutive_defections == 3:
              self.consecutive_defections = 0
              return axl.Action.C

      # Tit-for-Tat with probability
      if len(self.history) == 0 or opponent.history[-1] == axl.Action.C:
          return axl.Action.C if self._random.random() < self.cooperation_probability else axl.Action.D
      else:
          return axl.Action.D if self._random.random() > self.cooperation_probability else axl.Action.C

# Revised Neutral Strategy: "Adaptive Tit-for-Tat with Cautious Forgiveness"  1.
# Start with an opening sequence of CCCD to gather initial information about the
# opponent's behavior.  2. For subsequent rounds:    - If the opponent
# cooperated in the previous round, cooperate (C).    - If the opponent defected
# in the previous round, defect (D).  3. Maintain a rolling average of the
# opponent's last 5 moves:    - If the average cooperation rate is above 0.6,
# cooperate in the next round regardless of their last move.    - If the average
# cooperation rate is below 0.2, defect in the next round regardless of their
# last move.  4. Implement a cautious forgiveness mechanism:    - With a 5%
# probability, cooperate when you would otherwise defect.    - If mutual
# cooperation (C,C) has been achieved for 10 consecutive rounds, cooperate for
# one additional round regardless of the opponent's last move.  5. Adjust
# strategy for the end-game:    - In the last 50 rounds (5% of the game), become
# more defensive:      - If the opponent's rolling average cooperation rate is
# below 0.5, always defect.      - Otherwise, continue with the regular
# strategy.  This revised strategy maintains the adaptive nature of the original
# while addressing the identified issues. It's simpler, less exploitable, and
# takes into account both the opening moves and the end-game scenario. The
# strategy remains balanced between cooperation and defection, adapting to the
# opponent's behavior while protecting against potential exploitation.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.opening_sequence = [axl.Action.C, axl.Action.C, axl.Action.C, axl.Action.D]
          self.consecutive_cc = 0
          self.rolling_average = []

      if len(self.history) < 4:
          return self.opening_sequence[len(self.history)]

      # Update rolling average
      self.rolling_average.append(1 if opponent.history[-1] == axl.Action.C else 0)
      if len(self.rolling_average) > 5:
          self.rolling_average.pop(0)

      avg_cooperation = sum(self.rolling_average) / len(self.rolling_average)

      # End-game strategy
      if len(self.history) >= 950:
          if avg_cooperation < 0.5:
              return axl.Action.D

      # Cautious forgiveness
      if self.consecutive_cc >= 10:
          self.consecutive_cc = 0
          return axl.Action.C

      if self._random.random() < 0.05:
          return axl.Action.C

      # Main strategy logic
      if avg_cooperation > 0.6:
          next_move = axl.Action.C
      elif avg_cooperation < 0.2:
          next_move = axl.Action.D
      else:
          next_move = opponent.history[-1]  # Tit-for-Tat behavior

      # Update consecutive CC count
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.consecutive_cc += 1
      else:
          self.consecutive_cc = 0

      return next_move
