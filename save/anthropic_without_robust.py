import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Here's a revised strategy that takes into account the feedback while
# maintaining simplicity and aggressiveness:  1. Start by playing D (Defect) for
# the first move.  2. For the subsequent moves, use the following decision rules
# in order:     a. If it's one of the last 10 rounds (rounds 991-1000), always
# play D.        b. If the opponent has played C (Cooperate) for the last 3
# consecutive rounds, play C this round. This allows for some exploitation of
# consistently cooperative opponents.        c. If you've played D for the last
# 10 consecutive rounds, play C this round. This introduces a small element of
# unpredictability and prevents getting stuck in long mutual defection cycles.
# d. If the opponent played D in the previous round, play D.        e. If none
# of the above conditions are met, play D.  This revised strategy maintains an
# aggressive stance while addressing some of the critiques:  1. It's still
# simple, with clear conditions for cooperation and defection. 2. It remains
# predominantly aggressive, defaulting to defection in most cases. 3. It has a
# clear end-game strategy. 4. It allows for some adaptation to the opponent's
# strategy by cooperating after consistent cooperation from the opponent. 5. It
# includes a mechanism to occasionally break out of mutual defection cycles. 6.
# The conditions are ordered to prioritize certain behaviors, eliminating
# ambiguity. 7. It removes the predictable periodic cooperation, making it
# harder for opponents to exploit.  This strategy aims to maximize payoff by
# primarily defecting, while including targeted instances of cooperation to
# potentially achieve higher payoffs against certain opponent strategies. The
# simplicity is maintained, making it easy to implement and understand.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.D
      
      if len(self.history) >= 990:
          return axl.Action.D
      
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C
      
      if len(self.history) >= 10 and all(move == axl.Action.D for move in self.history[-10:]):
          return axl.Action.C
      
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      
      return axl.Action.D

# Here's a revised, simpler cooperative strategy that takes into account the
# feedback:  1. Start by playing C (cooperate) in the first round.  2. For all
# subsequent rounds, follow these rules in order:     a. If the opponent has
# played D (defect) in more than 2 of the last 3 rounds, play D.        b. If
# the opponent played C in the previous round, play C.        c. If the opponent
# played D in the previous round, play D.  3. If none of the above conditions
# are met (which can only happen in the second round if the opponent defected in
# the first round), play C.  This revised strategy:  - Starts cooperatively -
# Maintains cooperation when the opponent cooperates - Responds to defection
# with a single round of defection - Protects against consistent defection with
# the "2 out of 3" rule - Is simpler and easier to implement - Doesn't have any
# unreachable conditions or complex calculations - Focuses on maintaining
# cooperation while providing a measured response to defection  The strategy is
# ordered to prioritize protection against repeated defection, then to encourage
# cooperation, and finally to provide a proportional response to single
# defections. This order helps to balance cooperative behavior with protection
# against exploitation.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(self.history) >= 3 and opponent.history[-3:].count(axl.Action.D) > 2:
          return axl.Action.D
      
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      
      return axl.Action.C

# Thank you for the opportunity to refine the strategy. Here's a revised version
# that takes into account the feedback:  1. Start by playing C (cooperate) in
# the first round.  2. For each subsequent round, follow these rules in order:
# a. If it's one of the last 5 rounds of the game, play D (defect).        b. If
# your opponent has played D in the last 3 consecutive rounds, play D.        c.
# If your opponent has played C in the last 3 consecutive rounds, play C.
# d. Every 50 rounds (on rounds 51, 101, 151, etc.), play C as a "fresh start"
# opportunity.        e. If none of the above conditions are met, use the
# following rule:       - Calculate the ratio of C to D plays by your opponent
# in the last 10 rounds.       - If this ratio is greater than 0.6 (i.e., 6 or
# more C plays), play C.       - If this ratio is less than 0.4 (i.e., 6 or more
# D plays), play D.       - If the ratio is between 0.4 and 0.6, play the same
# move your opponent played in the previous round.  This revised strategy aims
# to be simpler, more neutral, and more responsive to the game's payoff
# structure. It prioritizes protection against end-game exploitation, responds
# quickly to consistent defection or cooperation, offers periodic opportunities
# for cooperation, and otherwise adapts to the opponent's recent behavior. The
# strategy is designed to encourage mutual cooperation when possible (which
# yields the highest combined payoff) while protecting against exploitation.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(self.history) >= 995:
          return axl.Action.D
      
      if (len(self.history) + 1) % 50 == 0:
          return axl.Action.C
      
      if len(opponent.history) >= 3:
          if all(move == axl.Action.D for move in opponent.history[-3:]):
              return axl.Action.D
          if all(move == axl.Action.C for move in opponent.history[-3:]):
              return axl.Action.C
      
      if len(opponent.history) >= 10:
          c_ratio = opponent.history[-10:].count(axl.Action.C) / 10
          if c_ratio > 0.6:
              return axl.Action.C
          elif c_ratio < 0.4:
              return axl.Action.D
          else:
              return opponent.history[-1]
      
      return opponent.history[-1]

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing D (Defect) for the first 5 rounds.  2. After the first 5 rounds, adopt
# the following rules in order:     a. If it's one of the last 20 rounds of the
# game, play D.        b. If the opponent has played D in the last 2 consecutive
# rounds, play D.        c. If your average score over the last 50 rounds is
# below 2, play D for the next 3 rounds.        d. If the opponent played C in
# the previous round, play C.        e. Otherwise, play D.  3. Every 100 rounds,
# reset and play C for 2 rounds to allow for the possibility of re-establishing
# cooperation.  This revised strategy:  - Maintains aggression with a shorter
# initial defection period and end-game defection. - Provides clear, ordered
# conditions for cooperation or defection. - Punishes defection more moderately
# (2 consecutive D's trigger a D response). - Allows for cooperation with a
# lower threshold (opponent's C in previous round). - Includes a mechanism to
# potentially break out of defection cycles. - Uses a more achievable score
# threshold for increasing aggression. - Is simpler overall, making it easier to
# implement and understand.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.defect_count = 0
          self.reset_counter = 0
  
      if len(self.history) < 5:
          return axl.Action.D
  
      if len(self.history) >= 980:
          return axl.Action.D
  
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      if len(self.history) >= 50:
          my_score, _ = self.total_scores(self.history[-50:], opponent.history[-50:])
          if my_score / 50 < 2:
              self.defect_count = 3
  
      if self.defect_count > 0:
          self.defect_count -= 1
          return axl.Action.D
  
      self.reset_counter += 1
      if self.reset_counter >= 99:
          if self.reset_counter == 100:
              self.reset_counter = 0
          return axl.Action.C
  
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      return axl.Action.D

# Here's a revised, simplified strategy that takes into account the feedback:
# 1. Start by playing C (Cooperate) in the first round.  2. For subsequent
# rounds, follow these rules in order:     a. If this is one of the last 10
# rounds of the game, play C.        b. If your opponent has defected in both of
# their last two moves, play D.        c. If your opponent has defected more
# than 60% of the time in the last 20 rounds, play D.        d. If this is a
# multiple of 100th round (100, 200, 300, etc.), play C.        e. Otherwise,
# play C.  This simplified strategy maintains the cooperative nature while
# addressing the main points of the critique:  1. It's simpler and easier to
# implement, with clear conditions for cooperation and defection.  2. It
# maintains the core "Tit-for-Two-Tats" approach (rule 2b) which promotes
# cooperation while providing protection against exploitation.  3. It keeps the
# end-game cooperation (rule 2a) and the periodic "olive branch" (rule 2d) to
# break potential negative cycles.  4. It retains protection against consistent
# defectors (rule 2c) but simplifies it by not specifying a fixed number of
# defection rounds.  5. The rules are ordered to avoid conflicts: end-game
# behavior takes precedence, followed by protective measures, then cooperative
# gestures.  6. It removes the redundant rule about consecutive cooperation, as
# the strategy will naturally cooperate in those situations anyway.  This
# strategy is cooperative by default, only defecting in response to recent or
# persistent defection from the opponent. It provides clear conditions for when
# to cooperate or defect, making it easier to implement and understand while
# still maintaining the core principles of the original strategy.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      rounds_played = len(self.history)
      total_rounds = self.match_attributes.get("length")
      
      if total_rounds is not None and total_rounds - rounds_played <= 10:
          return axl.Action.C
      
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
      
      recent_history = opponent.history[-20:]
      if len(recent_history) == 20:
          defection_rate = recent_history.count(axl.Action.D) / 20
          if defection_rate > 0.6:
              return axl.Action.D
      
      if (rounds_played + 1) % 100 == 0:
          return axl.Action.C
      
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. In each subsequent round, follow
# these rules in order:     a. If this is one of the last 10 rounds of the game
# (rounds 991-1000), play D.        b. If this is a multiple of 100th round
# (100, 200, 300, etc.), play C as an "olive branch".        c. If the opponent
# has played D in the last two consecutive rounds, play D.        d. If you're
# in rounds 2-10, mirror the opponent's previous move.        e. If you're in a
# round that's a multiple of 10 (10, 20, 30, etc.), evaluate the last 10 rounds:
# - If the opponent played C 6 or more times, play C.       - If the opponent
# played D 6 or more times, play D.        f. If none of the above conditions
# are met, mirror the opponent's previous move.  This revised strategy is
# simpler and clearer about when to cooperate or defect. It addresses the main
# points of feedback:  1. It's more responsive by lowering the threshold to 6
# out of 10 rounds for strategy adjustment.  2. It's more protective against
# exploitation by defecting after two consecutive D's from the opponent, rather
# than three.  3. It maintains the "olive branch" every 100 rounds and the end-
# game defection strategy.  4. It still aims for neutrality through mirroring,
# but is more adaptive to the opponent's recent behavior.  5. The order of
# conditions ensures that special cases (end game, periodic cooperation,
# response to recent defection) are handled before falling back to the mirroring
# strategy.  This strategy should be simpler to implement and understand, while
# still aiming to maximize payoff in the given game structure.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      current_round = len(self.history) + 1
      
      if current_round > 990:
          return axl.Action.D
      
      if current_round % 100 == 0:
          return axl.Action.C
      
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
      
      if 2 <= current_round <= 10:
          return opponent.history[-1]
      
      if current_round % 10 == 0:
          last_ten_rounds = opponent.history[-10:]
          if last_ten_rounds.count(axl.Action.C) >= 6:
              return axl.Action.C
          elif last_ten_rounds.count(axl.Action.D) >= 6:
              return axl.Action.D
          else:
              return opponent.history[-1]
      
      return opponent.history[-1]

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing D (Defect) for the first 50 rounds.  2. For the remaining 950 rounds,
# follow these rules in order:     a. If there are 50 or fewer rounds left in
# the game, play D.        b. If your total score is more than 50 points behind
# your opponent's, play D for the next 20 rounds.        c. If the current round
# number is a multiple of 100, play D for this round and the next 4 rounds.
# d. If the opponent played D in the previous round, play D.        e. If the
# opponent played C in the previous round, play C with 90% probability and D
# with 10% probability.  3. If none of the above conditions are met, play C.
# This revised strategy maintains aggression and simplicity while addressing the
# previous feedback:  - It clearly specifies the conditions for cooperation and
# defection, ordered from most aggressive to least. - It accounts for the total
# game length of 1000 rounds explicitly. - The periodic aggressive phase is
# slightly less predictable as it's now a single round trigger instead of a
# fixed 5-round block. - It removes the unnecessary initial single round of
# defection. - It simplifies the "punishment" mechanism by always defecting
# after the opponent defects, making the strategy more responsive. - It
# maintains the aggressive end-game strategy for the last 50 rounds.  This
# strategy should be easier to implement and understand while still playing
# aggressively to maximize total payoff.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.behind_aggressive_rounds = 0
          self.periodic_aggressive_rounds = 0
  
      current_round = len(self.history) + 1
      total_rounds = 1000
  
      # First 50 rounds: Defect
      if current_round <= 50:
          return axl.Action.D
  
      # Last 50 rounds: Defect
      if current_round > total_rounds - 50:
          return axl.Action.D
  
      # If score is more than 50 points behind opponent's
      if self.score <= opponent.score - 50:
          self.behind_aggressive_rounds = 20
      
      if self.behind_aggressive_rounds > 0:
          self.behind_aggressive_rounds -= 1
          return axl.Action.D
  
      # Every 100th round: Defect for this round and next 4 rounds
      if current_round % 100 == 0:
          self.periodic_aggressive_rounds = 4
          return axl.Action.D
  
      if self.periodic_aggressive_rounds > 0:
          self.periodic_aggressive_rounds -= 1
          return axl.Action.D
  
      # If opponent defected in the previous round
      if opponent.history and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If opponent cooperated in the previous round
      if opponent.history and opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.9)
  
      # Default action: Cooperate
      return axl.Action.C

# Here's a revised, simplified strategy that takes into account the feedback:
# 1. Start by playing C (Cooperate) in the first round.  2. For all subsequent
# rounds, follow these rules in order:     a. If the opponent has played D
# (Defect) in both of the last two rounds, play D.        b. Otherwise, play C.
# 3. In the very last round (round 1000), play C regardless of the opponent's
# previous actions.  This revised strategy maintains the core "Tit-for-Two-Tats"
# approach, which is cooperative and forgiving, while addressing the main points
# of feedback:  - It's simpler and easier to implement, removing the complex
# rules about long-term cooperation rewards and protection against consistent
# defectors. - It maintains cooperative behavior by only defecting after two
# consecutive defections from the opponent. - It removes the exploitable end-
# game behavior of always cooperating for the last 10 rounds, instead only
# guaranteeing cooperation on the final round. - It clearly specifies the
# conditions for cooperation and defection, with a clear order of precedence. -
# It doesn't require tracking long histories of moves, making it more memory-
# efficient.  This strategy remains cooperative in nature, as it starts with
# cooperation, only retaliates after repeated defection, quickly returns to
# cooperation, and ends with a cooperative move. At the same time, it protects
# against exploitation by opponents who might try to take advantage of excessive
# forgiveness.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(self.history) == 999:  # This is the 1000th round
          return axl.Action.C
      
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
      
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback, with clear
# conditions for cooperation and defection:  1. Start by playing C (cooperate)
# in the first round.  2. For all subsequent rounds, follow these rules in
# order:     a. If it's a multiple of 50th round (50, 100, 150, etc.), play a
# random move (50% chance of C, 50% chance of D) to potentially break any
# negative patterns.     b. If the opponent has defected in the last 3
# consecutive rounds, play D.     c. If the opponent's cooperation rate over the
# last 10 rounds is 70% or higher, play C.     d. If the opponent's cooperation
# rate over the last 10 rounds is 30% or lower, play D.     e. If none of the
# above conditions are met, mirror the opponent's last move.  3. Maintain this
# strategy consistently throughout all 1000 rounds of the game.  This strategy
# is simpler and more neutral than the previous version. It removes the complex
# 10-round evaluation period and the non-neutral end-game strategy. Instead, it
# uses a rolling cooperation rate and introduces occasional randomness to break
# patterns. The strategy remains responsive to the opponent's moves while
# maintaining a balanced approach throughout the game.  The conditions are
# ordered to prioritize breaking potential negative patterns (2a), then
# protecting against consistent defection (2b), followed by rewarding high
# cooperation (2c) or punishing low cooperation (2d), and finally defaulting to
# mirroring if no other condition is met (2e).  This approach should be more
# effective in maximizing total payoff while maintaining neutrality and
# simplicity.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      round_number = len(self.history) + 1
      
      if round_number % 50 == 0:
          return self._random.random_choice()
      
      if len(self.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          return axl.Action.D
      
      last_ten_rounds = min(10, len(self.history))
      recent_opponent_history = opponent.history[-last_ten_rounds:]
      opponent_cooperation_rate = recent_opponent_history.count(axl.Action.C) / last_ten_rounds
      
      if opponent_cooperation_rate >= 0.7:
          return axl.Action.C
      
      if opponent_cooperation_rate <= 0.3:
          return axl.Action.D
      
      return opponent.history[-1]

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing D (defect) for the first 5 rounds.  2. After the first 5 rounds,
# follow these rules in order:     a. If this is one of the last 5 rounds of the
# game, play D.        b. Every 25 rounds, reassess your opponent's behavior
# over the last 25 rounds:       - If they've cooperated more than 60% of the
# time, play D for the next 5 rounds.       - If they've defected more than 60%
# of the time, play tit-for-tat for the next 5 rounds.        c. Every 100
# rounds, check your average score:       - If your average score is less than 2
# points per round, switch to a pure tit-for-tat strategy until the next
# 100-round check.        d. If none of the above conditions are met, base your
# move on your opponent's recent behavior:       - If they've played C more than
# 60% of the time in the last 10 rounds, play D.       - If they've played D
# more than 60% of the time in the last 10 rounds, play what they played in the
# previous round (tit-for-tat).       - If their play is mixed (between 40% and
# 60% C or D), play D.  3. If none of the above conditions are met (which should
# be rare), play D as a default move.  This revised strategy maintains an
# aggressive approach while being more responsive to the opponent's actions. It
# clearly specifies when to cooperate or defect, with conditions ordered from
# most specific (end-game behavior) to more general (default behavior). The
# strategy adapts more quickly to changes in the opponent's play and provides a
# clear framework for decision-making throughout the game.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.last_reassessment = 0
          self.last_score_check = 0
          self.tit_for_tat_mode = False
          self.reassessment_strategy = None
          self.reassessment_rounds = 0
  
      if len(self.history) < 5:
          return axl.Action.D
  
      if len(self.history) >= 995:
          return axl.Action.D
  
      current_round = len(self.history)
  
      if current_round - self.last_reassessment == 25:
          self.last_reassessment = current_round
          recent_coop_rate = opponent.history[-25:].count(axl.Action.C) / 25
          if recent_coop_rate > 0.6:
              self.reassessment_strategy = axl.Action.D
          elif recent_coop_rate < 0.4:
              self.reassessment_strategy = 'tit_for_tat'
          else:
              self.reassessment_strategy = None
          self.reassessment_rounds = 5
  
      if self.reassessment_rounds > 0:
          self.reassessment_rounds -= 1
          if self.reassessment_strategy == axl.Action.D:
              return axl.Action.D
          elif self.reassessment_strategy == 'tit_for_tat':
              return opponent.history[-1]
  
      if current_round - self.last_score_check == 100:
          self.last_score_check = current_round
          avg_score = self.score / current_round
          if avg_score < 2:
              self.tit_for_tat_mode = True
          else:
              self.tit_for_tat_mode = False
  
      if self.tit_for_tat_mode:
          return opponent.history[-1]
  
      recent_coop_rate = opponent.history[-10:].count(axl.Action.C) / 10
      if recent_coop_rate > 0.6:
          return axl.Action.D
      elif recent_coop_rate < 0.4:
          return opponent.history[-1]
      else:
          return axl.Action.D

# Here's a revised, simpler strategy that takes into account the feedback:  1.
# Start by playing C (cooperate) in the first round.  2. For subsequent rounds,
# follow these rules in order:     a. If it's one of the last 5 rounds of the
# game, play C.        b. If your opponent has defected in both of their last
# two moves, play D.        c. If you played D in the previous round (as a
# punishment), play C.        d. If your opponent has defected more than 70% of
# the time in the last 20 rounds, play D.        e. Otherwise, play C.  This
# revised strategy:  1. Starts cooperatively.  2. Uses a simplified version of
# "Tit-for-Two-Tats" (rule b), which is forgiving but still protects against
# exploitation.  3. Always offers an "olive branch" after punishment (rule c),
# encouraging a return to cooperation.  4. Protects against highly exploitative
# opponents with a simpler threshold (rule d).  5. Cooperates by default (rule
# e).  6. Ensures cooperation in the final rounds, but for a shorter period to
# reduce vulnerability (rule a).  This strategy is simpler, with clear
# conditions for cooperation and defection. The rules are ordered to handle
# different scenarios effectively, from end-game behavior to punishment and
# protection against exploitation. It maintains a cooperative nature while
# providing mechanisms to discourage and respond to repeated defections.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(self.history) >= 995:
          return axl.Action.C
      
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
      
      if self.history[-1] == axl.Action.D:
          return axl.Action.C
      
      if len(opponent.history) >= 20:
          recent_moves = opponent.history[-20:]
          defection_rate = recent_moves.count(axl.Action.D) / len(recent_moves)
          if defection_rate > 0.7:
              return axl.Action.D
      
      return axl.Action.C

# Here's a revised, simpler strategy that takes into account the feedback:  1.
# Start by playing C (Cooperate) in the first round.  2. For subsequent rounds,
# follow these rules in order:     a. If it's the last 10 rounds of the game,
# play D (Defect).        b. If the opponent has played D in the last 3
# consecutive rounds, play D.        c. If it's a multiple of 50 rounds (50,
# 100, 150, etc.), play C as an "olive branch".        d. Otherwise, mirror the
# opponent's previous move (if they played C, play C; if they played D, play D).
# 3. If the game continues beyond the expected number of rounds, continue
# following rules b, c, and d.  This revised strategy is simpler and clearer,
# while maintaining the core principles of the original strategy. It behaves
# more neutrally by removing the complex 10-round evaluation period and
# simplifying the decision-making process. The strategy now has a clear
# hierarchy of conditions, making it easier to determine which action to take in
# any given round.  The strategy starts neutrally, adapts quickly to the
# opponent's moves, protects against consistent defection, and includes periodic
# attempts to establish cooperation. The end-game defection is maintained but
# limited to a smaller number of rounds to balance strategic play with overall
# neutrality.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if 990 < len(self.history) <= 1000:
          return axl.Action.D
      
      if opponent.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.D
      
      if len(self.history) % 50 == 0:
          return axl.Action.C
      
      return opponent.history[-1]

# Here's a revised strategy that takes into account the feedback, with clear
# conditions for cooperation and defection, ordered appropriately:  1. Start by
# playing D (defect) for the first 10 moves.  2. For the remainder of the game,
# follow these rules in order:     a. If it's one of the last 50 rounds of the
# game, play D.        b. If your cumulative score is behind your opponent's by
# 30 points or more, play D for the next 5 rounds.        c. If it's a multiple
# of 100th round (100, 200, 300, etc.), play D for this round and the next 2
# rounds.        d. If the opponent has played D in either of the last two
# rounds, play D.        e. If the opponent has played C for the last two
# rounds:       - Play C with 70% probability       - Play D with 30%
# probability     f. If none of the above conditions are met, play C.  3.
# Regardless of the above rules, always play D if the opponent has played D for
# 3 or more consecutive rounds.  This revised strategy maintains an aggressive
# stance while addressing the previous feedback:  - It starts with a shorter
# initial defection period (10 moves instead of 51). - It clearly prioritizes
# end-game defection. - The catch-up mechanism is triggered earlier (30 points
# behind instead of 50) and lasts for 5 rounds instead of 10, making it more
# responsive. - Periodic aggression is maintained but shortened to 3 rounds
# every 100 moves. - It punishes recent defection more aggressively. - When the
# opponent cooperates, it's less generous (70% cooperation instead of 90%),
# maintaining a more aggressive stance. - It includes a mechanism to always
# defect against consistently defecting opponents.  This strategy is simpler,
# with clear conditions for cooperation and defection, while still maintaining
# an aggressive approach to maximize total payoff. It's more responsive to the
# opponent's behavior and includes mechanisms to capitalize on both cooperative
# and defecting opponents.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.catch_up_rounds = 0
  
      if len(self.history) < 10:
          return axl.Action.D
  
      if len(self.history) > 950:
          return axl.Action.D
  
      if len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          return axl.Action.D
  
      if self.score < opponent.score - 30:
          if self.catch_up_rounds < 5:
              self.catch_up_rounds += 1
              return axl.Action.D
      else:
          self.catch_up_rounds = 0
  
      if (len(self.history) + 1) % 100 == 0 or len(self.history) % 100 in [1, 2]:
          return axl.Action.D
  
      if axl.Action.D in opponent.history[-2:]:
          return axl.Action.D
  
      if opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          return self._random.random_choice(0.7)
  
      return axl.Action.C

# Here's a revised, simplified strategy that takes into account the feedback:
# 1. Start by playing C (Cooperate) in the first round.  2. For all subsequent
# rounds, including the last 10, follow these rules in order:     a. If your
# opponent has played D (Defect) in both of their last two moves, play D.
# b. Otherwise, play C.  3. In the very last round (round 1000), play C
# regardless of the opponent's previous moves.  This strategy can be summarized
# as "Tit-for-Two-Tats with guaranteed final cooperation." It behaves
# cooperatively while protecting against exploitation, and it's simple to
# understand and implement. Here's a breakdown of its behavior:  - It starts
# cooperatively. - It only defects after the opponent has defected twice in a
# row, encouraging cooperation and allowing for a single mistake. - It quickly
# returns to cooperation once the opponent cooperates again. - It maintains this
# approach consistently throughout the game, avoiding unnecessary complexity. -
# It ensures cooperation in the final round to prevent any last-move
# exploitation.  This revised strategy addresses the main issues identified in
# the critique: - It removes the unnecessary occasional defection test. - It
# eliminates the problematic "always defect" condition against consistent
# defectors. - It maintains a consistent approach throughout the game, with only
# a simple exception for the very last round. - It clearly defines when to
# cooperate or defect based on the opponent's last two moves, making it easy to
# implement and understand.  This strategy remains cooperative in nature, aiming
# to establish and maintain mutual cooperation for maximum payoff, while having
# a simple mechanism to discourage and punish repeated defection.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
      
      if len(self.history) == 999:  # This is the last round (1000th move)
          return axl.Action.C
      
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback, with clear
# conditions for cooperation and defection:  1. Start by playing C (cooperate)
# in the first round.  2. For each subsequent round, follow these rules in
# order:     a. If the opponent has defected in 3 or more of the last 5 rounds:
# - Play D (defect)        b. Otherwise, mirror the opponent's last move:
# - If the opponent played C in the previous round, play C       - If the
# opponent played D in the previous round, play D  3. Tiebreaker: If the above
# rules don't determine a clear action (e.g., in the first few rounds), play C.
# This revised strategy:  - Maintains simplicity with clear, easy-to-follow
# rules - Preserves neutrality by primarily mirroring the opponent's moves -
# Adapts to exploitation more gradually and flexibly - Removes the periodic
# forced cooperation and end-game cooperation, which could be exploited -
# Considers a longer history of moves (last 5 rounds) to make decisions -
# Provides a clear tiebreaker for any ambiguous situations  The strategy now
# focuses on balancing neutrality with protection against consistent
# exploitation, without introducing elements that could be easily taken
# advantage of by opponents. It remains reactive but with a slightly longer
# memory, allowing for better adaptation to the opponent's overall strategy
# while still maintaining a neutral approach.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      last_five_rounds = min(5, len(self.history))
      opponent_defections = opponent.history[-last_five_rounds:].count(axl.Action.D)
      
      if opponent_defections >= 3:
          return axl.Action.D
      
      if opponent.history:
          return opponent.history[-1]
      
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing D (Defect) for the first 3 rounds.  2. For the remainder of the game,
# follow these rules in order:     a. If it's one of the last 10 rounds, always
# play D.        b. If it's a multiple of 50 rounds (50, 100, 150, etc.), play C
# to probe for cooperation.        c. Keep track of your opponent's choices in
# the last 5 rounds. If they've played C 3 or more times, play D to exploit
# their cooperation.        d. If your opponent has played D 4 or 5 times in the
# last 5 rounds, play C once to potentially encourage cooperation.        e. If
# none of the above conditions are met, play D.  3. In case of a tie between
# conditions (which shouldn't happen with this setup), prioritize defection (D).
# This revised strategy: - Starts aggressively but with a shorter initial
# defection period. - Clearly defines when to cooperate or defect with
# prioritized conditions. - Lowers the threshold for exploiting cooperation to
# capture more opportunities. - Maintains periodic cooperation probes and end-
# game defection. - Defaults to defection in most cases, maintaining an
# aggressive stance.  The strategy remains simple and aggressive while
# addressing the main points of feedback. It doesn't introduce complex
# adaptations based on game stage or score difference to maintain simplicity,
# but it does adjust the cooperation/defection thresholds for potentially better
# performance.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if len(self.history) < 3:
          return axl.Action.D
      
      if len(self.history) > 989:
          return axl.Action.D
      
      if (len(self.history) + 1) % 50 == 0:
          return axl.Action.C
      
      if len(self.history) >= 5:
          last_five = opponent.history[-5:]
          if last_five.count(axl.Action.C) >= 3:
              return axl.Action.D
          
          if last_five.count(axl.Action.D) >= 4:
              return axl.Action.C
      
      return axl.Action.D

# Here's a revised, simpler strategy that takes into account the feedback:  1.
# Start by playing C (Cooperate) in the first round.  2. For rounds 2 to 990,
# follow these rules in order:     a. If it's been less than 2 rounds since your
# last defection, play C. This ensures you don't defect twice in a row.
# b. If your opponent has defected in both of their last two moves, play D.
# c. Otherwise, play C.  3. For the last 10 rounds (991-1000), always play C.
# This strategy can be summarized as: - Start cooperatively - Use a "Tit-for-
# Two-Tats" approach for most of the game - Always cooperate in the endgame
# This revised strategy is simpler while maintaining the core cooperative
# nature. It's clear about when to cooperate or defect, and the conditions are
# ordered to prioritize cooperation. The strategy is forgiving (allows one
# defection before retaliating), encourages cooperation, and aims to maximize
# mutual benefit in the endgame.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      if len(self.history) > 990:
          return axl.Action.C
      
      if self.history[-2:].count(axl.Action.D) > 0:
          return axl.Action.C
      
      if opponent.history[-2:].count(axl.Action.D) == 2:
          return axl.Action.D
      
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (Cooperate) in the first round.  2. For each subsequent round,
# follow these rules in order:     a. If it's the final round (round 1000), play
# C.     b. If the opponent has played D (Defect) in 7 or more of the last 10
# rounds:       - Play D for this round.     c. If it's a multiple of 10th round
# (e.g., round 10, 20, 30...):       - Play C to provide an opportunity for
# mutual cooperation.     d. Otherwise:       - If the opponent played C in the
# previous round, play C.       - If the opponent played D in the previous
# round, play D.  3. After determining the move based on the above rules,
# there's a 5% chance to play the opposite move instead. This adds a small
# element of unpredictability to the strategy.  This revised strategy maintains
# simplicity and neutrality while addressing the previous issues:  - It removes
# the exploitable endgame behavior by only cooperating on the final round. - It
# replaces the 5-round defection trigger with a more flexible ratio-based
# approach. - It adds a small random element to prevent the strategy from being
# too predictable. - The order of conditions ensures that the most important
# rules (final round, defensive mechanism, periodic cooperation) are checked
# first, before defaulting to the tit-for-tat behavior.  The strategy remains
# neutral by generally mirroring the opponent's moves and providing regular
# opportunities for cooperation, while also protecting itself against consistent
# defection.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          action = axl.Action.C
      elif len(self.history) == 999:  # 1000th round
          action = axl.Action.C
      else:
          recent_defections = opponent.history[-10:].count(axl.Action.D)
          if recent_defections >= 7:
              action = axl.Action.D
          elif len(self.history) % 10 == 9:  # 10th, 20th, 30th... round
              action = axl.Action.C
          else:
              action = opponent.history[-1]
      
      # 5% chance to play the opposite move
      if self._random.random() < 0.05:
          return axl.Action.C if action == axl.Action.D else axl.Action.D
      
      return action

# Here's a revised strategy that takes into account the feedback while
# maintaining simplicity and aggressiveness:  1. Start by playing D (defect) for
# the first 10 moves.  2. For the remainder of the game, use the following rules
# in order:     a. If it's one of the last 50 rounds, always play D.        b.
# If the opponent has played C for the last 3 consecutive rounds, play D for the
# next 10 rounds.        c. If your total score is at least 50 points behind the
# opponent's, play C for the next round.        d. If it's a multiple of 75th
# round (75, 150, 225, etc.), play C.        e. If the opponent played D in the
# previous round, play D.        f. If none of the above conditions are met,
# play D.  This strategy maintains an aggressive stance while addressing the
# previous feedback:  1. It's simple and easy to implement, with clear
# conditions for cooperation or defection.  2. It remains predominantly
# aggressive, starting with defection and defaulting to defection in most cases.
# 3. The initial defection period is shortened to 10 moves, allowing for earlier
# adaptation.  4. It exploits cooperative opponents more quickly (3 consecutive
# C's instead of 5) and for a shorter duration (10 rounds instead of 20),
# allowing for more frequent reassessment.  5. It introduces a catch-up
# mechanism when significantly behind, potentially encouraging the opponent to
# cooperate.  6. Periodic cooperation is maintained but made less predictable
# (every 75 rounds instead of 100).  7. The endgame strategy of always defecting
# in the last 50 rounds is retained.  8. The strategy has a clear order of
# conditions, eliminating any ambiguity in decision-making.  This revised
# strategy balances aggression with limited adaptability, making it more robust
# while still prioritizing high payoffs through primarily defective play.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.exploit_start = 0

      if len(self.history) < 10:
          return axl.Action.D
      
      if len(self.history) >= self.match_attributes['length'] - 50:
          return axl.Action.D
      
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          self.exploit_start = len(self.history)

      if len(self.history) - self.exploit_start < 10:
          return axl.Action.D
      
      if opponent.score - self.score >= 50:
          return axl.Action.C
      
      if (len(self.history) + 1) % 75 == 0:
          return axl.Action.C
      
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. In subsequent rounds, play C if
# ANY of the following conditions are met:    a. The opponent played C in the
# previous round.    b. The opponent has played C in at least 70% of all
# previous rounds.    c. You are in one of the last 10 rounds of the game
# (rounds 991-1000).  3. Play D (defect) if ALL of the following conditions are
# met:    a. The opponent played D in the previous round.    b. The opponent has
# played D in more than 30% of all previous rounds.    c. You are not in one of
# the last 10 rounds of the game.  4. If you played D in the previous round,
# always play C in the next round, regardless of what the opponent did (unless
# you're in the last 10 rounds, then always play C).  This revised strategy
# maintains simplicity while addressing some of the previous weaknesses:  - It's
# still cooperative, starting with cooperation and maintaining it in many
# scenarios. - It takes into account the overall behavior of the opponent by
# considering the percentage of cooperative moves. - It's more robust against
# exploitation by occasional defection, as it considers the opponent's overall
# pattern of play. - It maintains the end-game cooperation but makes it less
# exploitable by including other conditions for cooperation. - The quick return
# to cooperation after defection is maintained, promoting the re-establishment
# of mutual cooperation. - The conditions for cooperation and defection are
# clearly stated and ordered, with cooperation taking precedence (if any
# condition for cooperation is met, the strategy cooperates).  This strategy
# balances cooperation with protection against persistent defectors, while
# remaining relatively simple and easy to implement.

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
      
      rounds_played = len(self.history)
      opponent_c_ratio = opponent.history.cooperations / rounds_played if rounds_played > 0 else 0
      
      # Condition 2: Play C if ANY of these conditions are met
      if (opponent.history[-1] == axl.Action.C or
          opponent_c_ratio >= 0.7 or
          rounds_played > 990):
          return axl.Action.C
      
      # Condition 4: Play C if D was played in the previous round (unless in last 10 rounds)
      if self.history[-1] == axl.Action.D and rounds_played <= 990:
          return axl.Action.C
      
      # Condition 3: Play D if ALL of these conditions are met
      opponent_d_ratio = 1 - opponent_c_ratio
      if (opponent.history[-1] == axl.Action.D and
          opponent_d_ratio > 0.3 and
          rounds_played <= 990):
          return axl.Action.D
      
      # Default to C if none of the above conditions are met
      return axl.Action.C

# Thank you for the opportunity to refine the strategy. Here's a revised version
# that takes into account the feedback, with clearer conditions for cooperation
# and defection:  1. Start by playing C (Cooperate) in the first round.  2. For
# rounds 2-1000, follow these rules in order:     a. If it's one of the last 10
# rounds (991-1000), play C.        b. If the opponent has defected (D) in the
# last 3 consecutive rounds, play D.        c. Every 10 rounds (on rounds 11,
# 21, 31, etc.), evaluate the opponent's behavior:       - If they played C 7 or
# more times in the last 10 rounds, play C.       - If they played D 7 or more
# times in the last 10 rounds, play D.       - Otherwise (4-6 C or D), continue
# to step d.        d. Mirror the opponent's previous move (if they played C,
# play C; if they played D, play D).  This revised strategy is simpler and more
# neutral, addressing the main points of the critique:  1. It's more
# straightforward, with fewer conditions and no complex score-checking
# mechanisms.  2. It maintains neutrality by primarily relying on mirroring and
# periodic evaluation of the opponent's behavior.  3. The order of conditions is
# clear, preventing any ambiguity about which rule to follow in any given
# situation.  4. It removes the potentially exploitable 100-round score check.
# 5. The three-defection rule is maintained as a simple defensive mechanism
# without overly compromising neutrality.  6. The endgame cooperation is
# preserved but limited to the last 10 rounds to reduce exploitability.  7. It
# clearly defines behavior for all rounds, eliminating any ambiguity.  This
# strategy aims to be reactive to the opponent's moves while maintaining a
# balance between cooperation and defection. It's simple enough to be easily
# implemented and understood, yet responsive to changes in the opponent's
# behavior.

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
      
      if len(self.history) >= 991:
          return axl.Action.C
      
      if len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          return axl.Action.D
      
      if len(self.history) % 10 == 1 and len(self.history) > 10:
          last_ten = opponent.history[-10:]
          c_count = last_ten.count(axl.Action.C)
          if c_count >= 7:
              return axl.Action.C
          elif c_count <= 3:
              return axl.Action.D
      
      return opponent.history[-1]

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing D (Defect) for the first 5 rounds.  2. After the first 5 rounds,
# implement the following rules in order:     a. If your total score is behind
# your opponent's by 30 points or more, play D for the next 10 rounds.        b.
# If it's one of the last 50 rounds of the game, always play D.        c. Assess
# your opponent's behavior over the last 20 rounds:       - If they've played C
# (Cooperate) 75% or more of the time, play D.       - If they've played D 75%
# or more of the time, play Tit-for-Tat (copy their last move).       - If their
# play falls between these extremes (26-74% C), do the following:         * If
# they played C in the last round, play C.         * If they played D in the
# last round, play D.  3. Repeat step 2 every round, always using the most
# recent 20 rounds for assessment.  This strategy: - Starts aggressively but
# quickly adapts. - Has a clear catch-up mechanism for when falling behind. -
# Ends aggressively to maximize final score. - Exploits highly cooperative
# opponents. - Adapts to aggressive opponents with Tit-for-Tat. - Allows for
# some cooperation against mixed strategies. - Uses a rolling window for
# assessment, making it more adaptive. - Has no gaps in its decision-making
# process. - Maintains simplicity while addressing previous shortcomings.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      if not self.history:
          self.behind_count = 0
      
      if len(self.history) < 5:
          return axl.Action.D
      
      opponent_recent = opponent.history[-20:]
      opponent_c_ratio = opponent_recent.count(axl.Action.C) / 20
      
      if self.score <= opponent.score - 30:
          self.behind_count = 10
      
      if self.behind_count > 0:
          self.behind_count -= 1
          return axl.Action.D
      
      game_length = self.match_attributes['length']
      if len(self.history) >= game_length - 50:
          return axl.Action.D
      
      if opponent_c_ratio >= 0.75:
          return axl.Action.D
      elif opponent_c_ratio <= 0.25:
          return opponent.history[-1]
      else:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D

# Here's a revised, simplified strategy that takes into account the feedback:
# 1. Start by playing C (cooperate) in the first round.  2. For each subsequent
# round, follow these rules in order:     a. If there are 20 or fewer rounds
# left in the game, always play C.        b. If your opponent has played C for
# the last 3 consecutive rounds, play C.        c. If your opponent has defected
# in more than 7 out of the last 10 rounds, play D.        d. Otherwise, use the
# following "Tit-for-Two-Tats" approach:       - If your opponent played C in
# either of their last two moves, play C.       - If your opponent played D in
# both of their last two moves, play D.  3. If it's the very first round or if
# you don't have enough history to apply the above rules, play C.  This revised
# strategy is simpler and clearer about when to cooperate or defect. It
# maintains a cooperative nature while protecting against consistent defection.
# The rules are ordered to prioritize end-game cooperation, quick return to
# cooperation after a series of cooperative moves by the opponent, and
# protection against high defection rates, before falling back to the core Tit-
# for-Two-Tats mechanism.  The strategy gradually increases cooperation as the
# game progresses by extending the end-game cooperation period to the last 20
# rounds instead of just 10. This provides a smoother transition to the end-game
# strategy.  The conditions are now more straightforward and easier to track,
# making the strategy simpler to implement while still accounting for the key
# aspects of encouraging cooperation and protecting against exploitation.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
      
      history_length = len(self.history)
      opponent_history_length = len(opponent.history)
  
      if history_length >= 980:  # 20 or fewer rounds left
          return axl.Action.C
      
      if opponent_history_length >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C
      
      if opponent_history_length >= 10 and sum(move == axl.Action.D for move in opponent.history[-10:]) > 7:
          return axl.Action.D
      
      if opponent_history_length >= 2:
          if axl.Action.C in opponent.history[-2:]:
              return axl.Action.C
          else:
              return axl.Action.D
      
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback, with clear
# conditions for cooperation and defection:  1. Start by playing C (cooperate)
# in the first round.  2. For each subsequent round, apply the following rules
# in order:     a. If it's the final round (round 1000), play D (defect) to
# protect against last-round exploitation.     b. If the opponent has played D
# for the last 3 consecutive rounds, play D.     c. If the opponent played C in
# the previous round, play C with 90% probability and D with 10% probability.
# This introduces a small element of unpredictability while generally
# reciprocating cooperation.     d. If the opponent played D in the previous
# round, play D with 90% probability and C with 10% probability. This allows for
# occasional forgiveness and potential return to mutual cooperation.     e. If
# none of the above conditions are met (which should be rare), play C.  3. Every
# 50 rounds, calculate the ratio of C to D plays by your opponent:    - If the
# ratio is greater than 0.6 (more cooperative), increase the probability of
# playing C in rules 2c and 2d by 5 percentage points (up to a maximum of 95%).
# - If the ratio is less than 0.4 (more defective), decrease the probability of
# playing C in rules 2c and 2d by 5 percentage points (down to a minimum of 5%).
# This revised strategy is simpler, more neutral, and addresses the main issues
# identified in the critique:  1. It's more adaptive to the opponent's overall
# strategy through the periodic adjustment. 2. It removes easily exploitable
# patterns like playing C every 10 rounds or in the final rounds. 3. It
# maintains a generally tit-for-tat approach but with some forgiveness and
# unpredictability. 4. It protects against exploitation in the final round. 5.
# The conditions are clear, ordered, and all potentially reachable.  This
# strategy aims to balance simplicity, neutrality, and effectiveness in
# maximizing total payoff over the course of the game.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.c_probability = 0.9
          return axl.Action.C
  
      if len(self.history) % 50 == 0 and len(self.history) > 0:
          c_ratio = opponent.history.cooperations / len(opponent.history)
          if c_ratio > 0.6:
              self.c_probability = min(0.95, self.c_probability + 0.05)
          elif c_ratio < 0.4:
              self.c_probability = max(0.05, self.c_probability - 0.05)
  
      if len(self.history) == 999:
          return axl.Action.D
  
      if opponent.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(self.c_probability)
      elif opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(1 - self.c_probability)
  
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing D (Defect) for the first 10 rounds to establish an initial aggressive
# stance.  2. After the first 10 rounds, use the following decision-making
# process in order:     a. If it's one of the last 50 rounds of the game, play
# D.        b. If your cumulative score is behind the opponent's by more than 50
# points, play D for the next 20 rounds.        c. If it's a multiple of 100th
# round (100, 200, 300, etc.), play D for this round and the next 2 rounds.
# d. If the opponent has played C for the last 3 consecutive rounds, play C.
# e. If none of the above conditions are met, play D.  3. Reset any counting of
# consecutive moves after applying rules a, b, or c.  This revised strategy
# maintains aggression while allowing for more nuanced responses:  - It starts
# aggressively but for a shorter period (10 rounds instead of 51), allowing
# earlier adaptation. - It still defects in the end game to maximize final
# payoffs. - It has a mechanism to catch up if falling behind. - It maintains
# periodic aggression with shorter, less predictable defection streaks. - It
# allows for cooperation, but only after consistent cooperation from the
# opponent. - It defaults to defection in most cases, maintaining an overall
# aggressive stance.  The conditions are now clearly ordered, eliminating any
# potential confusion about which rule to apply. This strategy is simpler, more
# adaptable, while still remaining primarily aggressive.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.defect_counter = 0
          self.catch_up_counter = 0
  
      if len(self.history) < 10:
          return axl.Action.D
  
      if len(self.history) > 950:
          self.defect_counter = 0
          self.catch_up_counter = 0
          return axl.Action.D
  
      if len(self.history) % 100 == 0:
          self.defect_counter = 3
          self.catch_up_counter = 0
          return axl.Action.D
  
      if self.defect_counter > 0:
          self.defect_counter -= 1
          return axl.Action.D
  
      if self.score < opponent.score - 50:
          if self.catch_up_counter < 20:
              self.catch_up_counter += 1
              self.defect_counter = 0
              return axl.Action.D
          else:
              self.catch_up_counter = 0
  
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      return axl.Action.D

# Here's a revised strategy that takes into account the feedback:  1. Start by
# playing C (Cooperate) in the first round.  2. For subsequent rounds, follow
# these rules in order:     a. If it's one of the last 10 rounds (991-1000),
# play D.        b. If it's a multiple of 50 rounds (50, 100, 150, etc.), play
# C.        c. If the opponent has defected in more than 70% of the total rounds
# so far, play D.        d. If the opponent played D in the previous round:
# - If this is the first or second consecutive D from the opponent, play D.
# - If this is the third or more consecutive D from the opponent, play C to
# attempt to break the cycle.        e. If none of the above conditions are met,
# play C.  This revised strategy addresses the previous issues while maintaining
# simplicity and a cooperative approach:  1. It clearly specifies the conditions
# for cooperation and defection, ordered from highest to lowest priority.  2.
# The end-game defection is maintained to protect against exploitation in the
# final rounds.  3. The periodic cooperation every 50 rounds is kept to break
# potential negative cycles, but its exploitability is reduced by other rules
# that take precedence.  4. It adapts to the opponent's overall pattern of play
# by considering their defection rate across the entire game.  5. It addresses
# what to do during punishment periods and provides a mechanism to break out of
# mutual defection cycles.  6. While not explicitly increasing trust over time,
# it does allow for long periods of mutual cooperation if the opponent is
# consistently cooperative.  This strategy remains relatively simple and
# cooperative, but with improved adaptability and protection against
# exploitation.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return axl.Action.C
  
      round_number = len(self.history) + 1
      total_rounds = 1000
  
      if round_number > 990:
          return axl.Action.D
  
      if round_number % 50 == 0:
          return axl.Action.C
  
      opponent_defection_rate = opponent.history.defections / round_number
      if opponent_defection_rate > 0.7:
          return axl.Action.D
  
      if opponent.history[-1] == axl.Action.D:
          if len(opponent.history) >= 3 and all(action == axl.Action.D for action in opponent.history[-3:]):
              return axl.Action.C
          else:
              return axl.Action.D
  
      return axl.Action.C

# Here's a revised strategy that takes into account the feedback, with clear
# conditions for cooperation and defection, ordered appropriately:  1. Start by
# playing C (cooperate) in the first round.  2. For each subsequent round, apply
# the following rules in order:     a. If it's the final round (round 1000),
# play D (defect).        b. If the opponent has played D for 3 or more
# consecutive rounds, play D.        c. If you've played D for 2 consecutive
# rounds, play C.        d. Mirror the opponent's previous move (play C if they
# played C, play D if they played D).  3. Every 50 rounds, ignore the above
# rules and:    - Play C if your total score is less than or equal to the
# opponent's.    - Play D if your total score is greater than the opponent's.
# This revised strategy aims to be simpler, more neutral, and less exploitable:
# - It removes the bias towards cooperation at the start and end of the game. -
# The punishment mechanism is simplified and less exploitable. - The periodic
# deviation is less frequent and takes into account the relative scores, making
# it more balanced. - It maintains neutrality by primarily mirroring the
# opponent's moves. - The conditions are clear, ordered, and all reachable. -
# While not explicitly using the payoff numbers, it indirectly accounts for them
# by comparing total scores periodically.  This strategy should be more
# effective in maximizing total payoff while maintaining neutrality and
# simplicity.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.consecutive_opponent_defections = 0
          self.consecutive_self_defections = 0
          return axl.Action.C
  
      if len(self.history) == 999:  # Final round
          return axl.Action.D
  
      if len(self.history) % 50 == 0:  # Every 50 rounds
          if self.score <= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_opponent_defections += 1
      else:
          self.consecutive_opponent_defections = 0
  
      if self.history[-1] == axl.Action.D:
          self.consecutive_self_defections += 1
      else:
          self.consecutive_self_defections = 0
  
      if self.consecutive_opponent_defections >= 3:
          return axl.Action.D
  
      if self.consecutive_self_defections >= 2:
          return axl.Action.C
  
      return opponent.history[-1]  # Mirror opponent's last move

# Here's a revised, simpler, and more aggressive strategy that takes into
# account the feedback:  1. Start by playing D (Defect) for the first move.  2.
# For the subsequent moves, follow these rules in order:     a. If it's one of
# the last 30 moves of the game, always play D.        b. If your opponent has
# played C for the last three consecutive moves, play C.        c. If it's a
# multiple of 50 moves (i.e., move 50, 100, 150, etc.), play D.        d. In all
# other cases, play D.  This revised strategy maintains aggression while
# simplifying the decision-making process. Here's a breakdown of the changes and
# rationale:  1. The initial defection sets an aggressive tone from the start.
# 2. The rules are ordered by priority, making the strategy clearer and easier
# to implement.  3. The endgame defection is reduced to the last 30 moves,
# balancing aggression with potential for higher overall points.  4. Cooperation
# only occurs after three consecutive cooperative moves from the opponent,
# making it harder for the opponent to exploit the strategy while still allowing
# some cooperation for potentially higher payoffs.  5. Periodic defection every
# 50 moves (instead of 100) maintains unpredictability and aggression,
# disrupting any emerging cooperative patterns more frequently.  6. The default
# action is to defect, maintaining the overall aggressive stance.  This strategy
# removes the complex conditions from the previous version, such as tracking
# score differences or having long initial defection streaks. It's more
# consistently aggressive while still allowing for minimal cooperation when it's
# likely to be beneficial. The simplicity of this strategy makes it easier to
# implement and less prone to exploitation.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First move: Defect
      if not self.history:
          return axl.Action.D
  
      # Last 30 moves: Always defect
      if len(self.history) > 970:
          return axl.Action.D
  
      # If opponent played C for the last three consecutive moves: Cooperate
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C
  
      # Every 50th move: Defect
      if len(self.history) % 50 == 0:
          return axl.Action.D
  
      # Default: Defect
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (Cooperate) in the first round.  2. For subsequent rounds, play C if
# any of these conditions are met (in order of priority):    a. The opponent has
# played C for the last 3 consecutive rounds.    b. It's a multiple of 50 rounds
# (50, 100, 150, etc.), to periodically encourage cooperation.    c. The
# opponent played C in the previous round, and you're not currently in a
# punishment phase.  3. Play D (Defect) if any of these conditions are met (in
# order of priority):    a. It's one of the last 10 rounds of the game (rounds
# 991-1000).    b. You're currently in a punishment phase (see point 4).    c.
# The opponent played D in the previous round.  4. Punishment phase:    - If the
# opponent plays D, enter a punishment phase.    - The punishment phase lasts
# for a number of rounds equal to the opponent's current defection streak
# (minimum 2 rounds).    - During the punishment phase, play D regardless of the
# opponent's moves.    - Exit the punishment phase after the determined number
# of rounds and return to the main strategy.  5. If none of the above conditions
# are met, play C.  This revised strategy maintains simplicity while addressing
# the previous feedback. It remains cooperative but is more robust against
# exploitation. The adaptive punishment phase discourages repeated defection,
# while the periodic cooperation and forgiveness mechanisms provide
# opportunities to re-establish mutual cooperation. The end-game defection is
# maintained to protect against last-round exploitation.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          self.punishment_phase = 0
          return axl.Action.C
  
      current_round = len(self.history) + 1
  
      # Condition 2a: Opponent played C for last 3 consecutive rounds
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C
  
      # Condition 2b: Multiple of 50 rounds
      if current_round % 50 == 0:
          return axl.Action.C
  
      # Condition 3a: Last 10 rounds
      if current_round > 990:
          return axl.Action.D
  
      # Condition 3b: In punishment phase
      if self.punishment_phase > 0:
          self.punishment_phase -= 1
          return axl.Action.D
  
      # Condition 3c: Opponent played D in previous round
      if opponent.history and opponent.history[-1] == axl.Action.D:
          # Enter punishment phase
          defection_streak = 0
          for move in reversed(opponent.history):
              if move == axl.Action.D:
                  defection_streak += 1
              else:
                  break
          self.punishment_phase = max(2, defection_streak) - 1  # -1 because we're defecting this round
          return axl.Action.D
  
      # Condition 2c: Opponent played C in previous round
      if opponent.history and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Condition 5: Default to C if none of the above conditions are met
      return axl.Action.C

# Thank you for the opportunity to revise the strategy. Here's a rewritten
# version that takes into account the feedback, with clear conditions for
# cooperation and defection:  1. For the first round:    - Randomly choose C or
# D with equal probability (50% chance for each).  2. For all subsequent rounds,
# in order of priority:     a. If the opponent played C in the previous round:
# - Play C with 80% probability       - Play D with 20% probability     b. If
# the opponent played D in the previous round:       - Play D with 80%
# probability       - Play C with 20% probability  This strategy is simpler and
# more neutral than the previous version. Here's a breakdown of its features:
# 1. Simplicity: The strategy has only two main rules, making it easy to
# understand and implement.  2. Neutrality:     - It starts with a random
# choice, showing no initial bias.    - It responds to the opponent's moves, but
# not deterministically, maintaining some unpredictability.    - It treats
# cooperation and defection similarly, with mirrored probabilities.  3.
# Consideration of payoffs:     - The 80/20 split favors reciprocating the
# opponent's move, which aligns with the payoff structure where mutual
# cooperation (C,C) is better than mutual defection (D,D).    - The 20% chance
# of not reciprocating allows for occasional exploitation attempts (D when
# opponent played C) and forgiveness/cooperation attempts (C when opponent
# played D).  4. No special rules: This version eliminates complex conditions
# like every 10 rounds or consecutive move counts, which could be exploited.  5.
# Clear conditions: The strategy clearly states when it will cooperate or defect
# based on the previous round's outcome.  This strategy aims to be responsive to
# the opponent's moves while maintaining some unpredictability. It encourages
# cooperation but can also protect against consistent defection. The
# probabilistic nature of the strategy makes it harder for opponents to exploit
# while still allowing for a generally cooperative approach when the opponent is
# cooperative.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = None

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      if not self.history:
          return self._random.random_choice()
      
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.8)
      else:
          return self._random.random_choice(0.2)
