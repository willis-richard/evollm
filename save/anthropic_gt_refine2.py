import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D in the current round.  3. If the opponent played D in the
# previous round, play D.  4. If you're currently on a streak of mutual
# cooperation (CC) for 5 or more consecutive rounds, continue playing C to
# maintain the beneficial cooperation.  5. If the opponent has played C for the
# last 10 rounds, switch to playing D for the next 2 rounds to exploit their
# cooperation, then revert to rule 4.  6. In the last 20 rounds of the game,
# always play D regardless of the opponent's actions.  7. For all other
# situations not covered by the above rules, play D.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: In the last 20 rounds of the game, always play D
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 4: If on a streak of mutual cooperation (CC) for 5 or more consecutive rounds, continue playing C
      if len(self.history) >= 5 and all(x == axl.Action.C and y == axl.Action.C for x, y in zip(self.history[-5:], opponent.history[-5:])):
          return axl.Action.C
  
      # Rule 5: If the opponent has played C for the last 10 rounds, switch to playing D for the next 2 rounds
      if len(opponent.history) >= 10 and all(x == axl.Action.C for x in opponent.history[-10:]):
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D, axl.Action.D]:
              return axl.Action.D
  
      # Rule 7: For all other situations, play D
      return axl.Action.D

# Here's a simplified cooperative strategy for the iterated game:  1. Start by
# playing C.  2. If the opponent played C in the previous round, play C.  3. If
# the opponent played D in the previous round, play D in the next round.  4.
# After playing D, return to C in the following round.  5. If the opponent plays
# D for 3 consecutive rounds, switch to always playing D.  6. If at any point
# the opponent plays C after a series of D's, immediately return to step 2.  7.
# In the last round of the game, play D.  This strategy maintains a cooperative
# approach while simplifying the conditions and removing the complex punishment
# escalation. It's more straightforward but still adapts to the opponent's
# behavior and protects against consistent defection. The end-game defection is
# limited to only the final round, allowing for more cooperative opportunities
# in the late game.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 7: In the last round of the game, play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # Step 5: If the opponent plays D for 3 consecutive rounds, switch to always playing D
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D
  
      # Step 2: If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If the opponent played D in the previous round, play D in the next round
      if opponent.history[-1] == axl.Action.D:
          # Step 4: After playing D, return to C in the following round
          if len(self.history) >= 1 and self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D

# Here's a revised, simpler strategy that aims to be more neutral and better
# aligned with the feedback:  1. Start by cooperating in the first round.  2.
# For the next rounds:    - If the opponent cooperated in the previous round,
# cooperate.    - If the opponent defected in the previous round, defect.  3.
# Every 50 rounds, reset by cooperating regardless of the opponent's previous
# move.  4. If you and your opponent have been in a cycle of mutual defection
# for more than 5 consecutive rounds, attempt to break the cycle by cooperating
# once.  5. In the last round, play the same move as your opponent's previous
# move.  This strategy maintains simplicity, neutrality, and considers the
# game's payoff structure implicitly through its tit-for-tat base. It removes
# arbitrary thresholds and complex conditions, while still allowing for some
# adaptation and cycle-breaking.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Check if we are in the last round
      if len(self.history) == 999:
          return opponent.history[-1]
  
      # Every 50 rounds, reset by cooperating
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Check for a cycle of mutual defection for more than 5 consecutive rounds
      if len(self.history) >= 5 and all(
          self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
          for i in range(1, 6)
      ):
          return axl.Action.C
  
      # Tit-for-tat: mirror the opponent's last move
      return opponent.history[-1]

# Here's a revised strategy incorporating the feedback:  1. Start by playing C
# in the first round to set a potentially cooperative tone.  2. If the opponent
# played C in the previous round, play C with 80% probability and D with 20%
# probability to maintain aggression while allowing for cooperation.  3. If the
# opponent played D in the previous round, play D.  4. If you're currently on a
# streak of mutual defection (D,D) for 3 consecutive rounds, play C once to test
# if the opponent is willing to cooperate.  5. If the opponent responds to your
# test cooperation with C, play C for the next round. If they play D,
# immediately revert to D.  6. Every 10 rounds, analyze the opponent's play
# pattern:    - If they've cooperated more than 70% of the time, increase your
# cooperation probability to 90% when they play C.    - If they've defected more
# than 70% of the time, decrease your cooperation probability to 10% when they
# play C.  7. In the last 20 rounds of the game, always play D regardless of the
# opponent's actions.  8. Repeat steps 2-7 for the duration of the game,
# adjusting for the final rounds as noted in step 7.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          self.coop_prob = 0.8  # Default cooperation probability
          return axl.Action.C
  
      # Step 7: In the last 20 rounds, always play D
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Step 4: Check for a streak of mutual defection (D,D) for 3 consecutive rounds
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D] * 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.C  # Test cooperation
  
      # Step 2: If opponent played C in the previous round
      if opponent.history[-1] == axl.Action.C:
          # Step 6: Every 10 rounds, analyze opponent's play pattern
          if len(self.history) % 10 == 0:
              coop_rate = opponent.history.cooperations / len(opponent.history)
              if coop_rate > 0.7:
                  self.coop_prob = 0.9  # Increase cooperation probability
              elif coop_rate < 0.3:
                  self.coop_prob = 0.1  # Decrease cooperation probability
              else:
                  self.coop_prob = 0.8  # Default cooperation probability
  
          # Play C with the current cooperation probability, else D
          return self._random.random_choice(self.coop_prob)
  
      # Step 3: If opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round, then return to C.  4. If the opponent plays D more than 50% of
# the time over the last 10 rounds, switch to playing D until they cooperate
# again.  5. If at any point the opponent switches back to cooperation (plays C
# for 2 consecutive rounds), resume cooperating by playing C.  6. Continue this
# strategy until the end of the game, including the final rounds.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by playing C in the first round.
      if self.first_round():
          return axl.Action.C
  
      # 2. If the opponent played C in the previous round, play C.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. If the opponent played D in the previous round, play D in the next round, then return to C.
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D
  
      # 4. If the opponent plays D more than 50% of the time over the last 10 rounds, switch to playing D until they cooperate again.
      if len(opponent.history) >= 10:
          last_10_defections = opponent.history[-10:].count(axl.Action.D)
          if last_10_defections > 5:
              if opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
                  return axl.Action.C
              return axl.Action.D
  
      # 5. If at any point the opponent switches back to cooperation (plays C for 2 consecutive rounds), resume cooperating by playing C.
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # Default to cooperation if no other condition is met.
      return axl.Action.C

# Here's a simplified and more neutral strategy:  1. In the first round,
# randomly choose to cooperate or defect.  2. If the opponent cooperated in the
# previous round, cooperate in the current round.  3. If the opponent defected
# in the previous round, defect in the current round.  4. If both players have
# cooperated for 5 consecutive rounds, defect once, then return to rule 2.  5.
# If both players have defected for 5 consecutive rounds, cooperate once, then
# return to rule 2.  6. For all other situations not covered by the above rules,
# randomly choose to cooperate or defect with equal probability.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: In the first round, randomly choose to cooperate or defect.
      if self.first_round():
          return self._random.random_choice()
  
      # Helper function to check if both players cooperated for the last 5 rounds
      def both_cooperated_last_n_rounds(n):
          return all(self.history[-i] == axl.Action.C and opponent.history[-i] == axl.Action.C for i in range(1, n + 1))
  
      # Helper function to check if both players defected for the last 5 rounds
      def both_defected_last_n_rounds(n):
          return all(self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, n + 1))
  
      # Rule 4: If both players have cooperated for 5 consecutive rounds, defect once, then return to rule 2.
      if len(self.history) >= 5 and both_cooperated_last_n_rounds(5):
          return axl.Action.D
  
      # Rule 5: If both players have defected for 5 consecutive rounds, cooperate once, then return to rule 2.
      if len(self.history) >= 5 and both_defected_last_n_rounds(5):
          return axl.Action.C
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate in the current round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect in the current round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 6: For all other situations, randomly choose to cooperate or defect with equal probability.
      return self._random.random_choice()

# Here's a revised, simpler, and more aggressive strategy:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, always defect in the current round.  3. If the opponent cooperated in
# the previous round, defect with a 90% probability and cooperate with a 10%
# probability.  4. If you're in the last 100 rounds of the game, always defect.
# 5. In all other situations, follow steps 2 and 3.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 4: If you're in the last 100 rounds of the game, always defect
      if len(self.history) >= 900:
          return axl.Action.D
  
      # Step 2: If the opponent defected in the previous round, always defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If the opponent cooperated in the previous round, defect with 90% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.1)

# Here's a revised strategy:  1. Start by playing C in the first round.  2. If
# the opponent played C in the previous round, play C.  3. If the opponent
# played D in the previous round, play D for the next two rounds as punishment.
# 4. After the two-round punishment, return to playing C.  5. If the opponent
# defects more than 25% of the time over the last 20 rounds, switch to always
# playing D until their cooperation rate improves.  6. Reassess the opponent's
# cooperation rate every 10 rounds.  7. In the last 10 rounds of the game,
# mirror the opponent's most frequent move from the previous 10 rounds.  8. If
# at any point the opponent cooperates for 5 consecutive rounds, reset any
# ongoing punishment and return to cooperative play.

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
          self.punishment_rounds = 0
          self.cooperation_streak = 0
          self.defection_rate_threshold = 0.25
          return axl.Action.C
  
      # Check if opponent cooperated for 5 consecutive rounds
      if len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:]):
          self.punishment_rounds = 0  # Reset punishment
          self.cooperation_streak = 0  # Reset cooperation streak
          return axl.Action.C
  
      # If in punishment mode, continue defecting for the next two rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # If opponent defected in the last round, start punishment
      if opponent.history[-1] == axl.Action.D:
          self.punishment_rounds = 2
          return axl.Action.D
  
      # Calculate opponent's defection rate over the last 20 rounds
      if len(opponent.history) >= 20:
          recent_defections = opponent.history[-20:].count(axl.Action.D)
          defection_rate = recent_defections / 20
  
          # If defection rate exceeds 25%, switch to always defecting
          if defection_rate > self.defection_rate_threshold:
              return axl.Action.D
  
      # Reassess defection rate every 10 rounds
      if len(opponent.history) % 10 == 0 and len(opponent.history) >= 20:
          recent_defections = opponent.history[-20:].count(axl.Action.D)
          defection_rate = recent_defections / 20
  
          # If defection rate exceeds 25%, switch to always defecting
          if defection_rate > self.defection_rate_threshold:
              return axl.Action.D
  
      # In the last 10 rounds, mirror the opponent's most frequent move from the previous 10 rounds
      if len(self.history) >= 990:
          last_10_moves = opponent.history[-10:]
          if last_10_moves.count(axl.Action.C) > last_10_moves.count(axl.Action.D):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C

# Here's a simplified and more neutral strategy:  1. Start by cooperating in the
# first round.  2. If the opponent cooperated in the previous round, cooperate
# in the current round.  3. If the opponent defected in the previous round,
# defect in the current round.  4. Every 10 rounds, if your score is lower than
# your opponent's, defect in the next round regardless of the opponent's
# previous move. Otherwise, follow rules 2 and 3.  5. In the last round of the
# game, defect regardless of the opponent's actions.  This strategy maintains
# simplicity, improves neutrality, and removes unnecessary complexity while
# still adapting to the opponent's behavior and the game state.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # 5. In the last round of the game, defect regardless of the opponent's actions.
      if len(self.history) == 999:
          return axl.Action.D
  
      # 4. Every 10 rounds, if your score is lower than your opponent's, defect in the next round.
      if len(self.history) % 10 == 0:
          if self.score < opponent.score:
              return axl.Action.D
  
      # 2. If the opponent cooperated in the previous round, cooperate.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. If the opponent defected in the previous round, defect.
      return axl.Action.D

# Here's a revised, simpler, and more aggressive strategy:  1. Start by
# defecting (D) in the first round.  2. If the opponent cooperated (C) in the
# previous round, defect (D) in the current round.  3. If the opponent defected
# (D) in the previous round, cooperate (C) in the current round.  4. If at any
# point your cumulative score falls behind the opponent's by 10 points or more,
# defect (D) for the next three rounds, then return to step 2.  5. In the last
# 20 rounds of the game, always defect (D) regardless of the opponent's actions.
# 6. Repeat these steps until the game ends.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.defect_streak = 0  # Initialize defect streak counter
          return axl.Action.D
  
      # Step 5: In the last 20 rounds of the game, always defect
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Step 4: If cumulative score falls behind by 10 or more, defect for 3 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      if self.score < opponent.score - 10:
          self.defect_streak = 3
          return axl.Action.D
  
      # Step 2 and 3: Respond based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      else:
          return axl.Action.C

# Here's a revised, simpler cooperative strategy for the game:  1. Start by
# playing C.  2. If the opponent played C in the previous round, play C.  3. If
# the opponent played D in the previous round, play D in the next round, then
# return to C.  4. If the opponent plays D for five consecutive rounds, switch
# to always playing D.  5. If at any point the opponent switches back to
# cooperation (playing C for 2 consecutive rounds), resume cooperating by
# playing C.  6. In the last round of the game, play D.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, play C
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.switched_to_defection = False  # Track if we switched to always defect
          return axl.Action.C
  
      # If it's the last round, play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # If we have switched to always defect, continue defecting
      if self.switched_to_defection:
          # Check if opponent cooperates for 2 consecutive rounds to resume cooperation
          if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
              self.switched_to_defection = False
              return axl.Action.C
          return axl.Action.D
  
      # Check if opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          # If opponent defected for 5 consecutive rounds, switch to always defect
          if self.consecutive_defections >= 5:
              self.switched_to_defection = True
              return axl.Action.D
          # Otherwise, defect once and then return to cooperation
          return axl.Action.D
      else:
          # Reset consecutive defections if opponent cooperates
          self.consecutive_defections = 0
          return axl.Action.C

# Here's a revised, simpler, and more neutral strategy:  1. Start by cooperating
# in the first round.  2. For the next 998 rounds:    - If the opponent
# cooperated in the previous round, cooperate.    - If the opponent defected in
# the previous round, defect.  3. In the final round, cooperate.  This strategy
# maintains neutrality by directly mirroring the opponent's previous move,
# starts and ends with cooperation to encourage mutual cooperation, and avoids
# complex rules or long-term punitive measures.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: cooperate
      if self.first_round():
          return axl.Action.C
      
      # Rounds 2 to 999: mirror opponent's previous move
      if len(self.history) < 999:
          return opponent.history[-1]
      
      # Final round: cooperate
      return axl.Action.C

# Here's a simplified and more aggressive strategy:  1. Start by playing D in
# the first round.  2. Always play D if the opponent played C in the previous
# round.  3. If the opponent played D in the previous round, play D with 90%
# probability and C with 10% probability.  4. If you're in the last 100 rounds
# of the game, always play D regardless of the opponent's previous move.  5. For
# all other situations not covered by the above rules, play D.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 4: If in the last 100 rounds, always play D
      if len(self.history) >= 900:
          return axl.Action.D
  
      # Rule 2: Always play D if the opponent played C in the previous round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D with 90% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1)
  
      # Rule 5: For all other situations, play D
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next three rounds, then return to C.  4. If the opponent plays D for five
# consecutive rounds, switch to always playing D until the opponent cooperates
# again.  5. If at any point the opponent returns to cooperation (plays C for 3
# consecutive rounds), resume the cooperative strategy from step 2.  6. Continue
# this strategy until the end of the game, without changing behavior in the
# final rounds.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If the opponent played D in the previous round, play D for the next three rounds, then return to C
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) >= 3 and all(move == axl.Action.D for move in self.history[-3:]):
              return axl.Action.C
          return axl.Action.D
  
      # Step 4: If the opponent plays D for five consecutive rounds, switch to always playing D until the opponent cooperates again
      if len(opponent.history) >= 5 and all(move == axl.Action.D for move in opponent.history[-5:]):
          if axl.Action.C in opponent.history[-3:]:
              return axl.Action.C
          return axl.Action.D
  
      # Step 5: If the opponent returns to cooperation (plays C for 3 consecutive rounds), resume the cooperative strategy
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# Here's a revised, simpler, and more neutral strategy:  1. Start by
# cooperating.  2. If the opponent cooperated in the previous round, cooperate.
# 3. If the opponent defected in the previous round, defect.  4. If the opponent
# has defected for three consecutive rounds, defect for the next round.  5. If
# your score is more than 15 points behind your opponent's after every 100
# rounds, defect for the next round.  6. For all other situations, cooperate.
# This strategy maintains neutrality, simplifies the rules, removes the endgame
# strategy, and provides clearer conditions for cooperation and defection.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by cooperating.
      if self.first_round():
          return axl.Action.C
  
      # 2. If the opponent cooperated in the previous round, cooperate.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. If the opponent defected in the previous round, defect.
      if opponent.history[-1] == axl.Action.D:
          # 4. If the opponent has defected for three consecutive rounds, defect for the next round.
          if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
              return axl.Action.D
  
          # 5. If your score is more than 15 points behind your opponent's after every 100 rounds, defect for the next round.
          if len(self.history) % 100 == 0:
              if opponent.score - self.score > 15:
                  return axl.Action.D
  
          # Otherwise, defect if opponent defected in the last round.
          return axl.Action.D
  
      # 6. For all other situations, cooperate.
      return axl.Action.C

# Here's a revised strategy incorporating the feedback:  1. Start by playing D
# in the first round.  2. If the opponent played C in the previous round, play
# D.  3. If the opponent played D in the previous round, play D.  4. If you and
# your opponent have cooperated (CC) for 2 consecutive rounds, play C with 70%
# probability and D with 30% probability in the next round.  5. If you've played
# D and your opponent has played C for 3 consecutive rounds, play C in the next
# round to encourage continued cooperation.  6. Keep track of the overall
# cooperation rate of your opponent. If it falls below 20%, always play D
# against them for the rest of the game.  7. In the last 20 rounds of the game,
# always play D regardless of the opponent's actions.  8. For all other
# situations not covered by the above rules, play D.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: Track opponent's cooperation rate
      total_moves = len(opponent.history)
      if total_moves > 0:
          cooperation_rate = opponent.history.cooperations / total_moves
          if cooperation_rate < 0.2:
              return axl.Action.D
  
      # Rule 7: In the last 20 rounds, always play D
      if self.match_attributes["length"] is not None:
          rounds_left = self.match_attributes["length"] - total_moves
          if rounds_left <= 20:
              return axl.Action.D
  
      # Rule 2 and 3: If opponent played C or D in the previous round, play D
      if opponent.history[-1] == axl.Action.C or opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 4: If both players cooperated for 2 consecutive rounds, play C with 70% probability
      if len(self.history) >= 2 and self.history[-1] == axl.Action.C and self.history[-2] == axl.Action.C and \
         opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return self._random.random_choice(0.7)
  
      # Rule 5: If you've played D and opponent has played C for 3 consecutive rounds, play C
      if len(self.history) >= 3 and self.history[-1] == axl.Action.D and \
         opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C and opponent.history[-3] == axl.Action.C:
          return axl.Action.C
  
      # Default: Play D in all other situations
      return axl.Action.D

# Here's a simplified cooperative strategy:  1. Start by playing C.  2. If the
# opponent played C in the previous round, play C.  3. If the opponent played D
# in the previous round, play D in the next round as punishment.  4. After
# punishing with D for one round, return to playing C.  5. If the opponent plays
# D for five consecutive rounds, switch to always playing D for the remainder of
# the game.  6. Continue this strategy until the end of the game, including the
# final rounds.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, play C
      if self.first_round():
          self.punishing = False  # Track if we are in a punishment phase
          self.always_defect = False  # Track if we are in the always defect phase
          return axl.Action.C
  
      # If we are in the always defect phase, always play D
      if self.always_defect:
          return axl.Action.D
  
      # Check if the opponent has defected for the last 5 consecutive rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          self.always_defect = True
          return axl.Action.D
  
      # If we are in the punishment phase, play C after punishing with D
      if self.punishing:
          self.punishing = False
          return axl.Action.C
  
      # If the opponent defected in the last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          self.punishing = True
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a revised, simpler, and more neutral strategy:  1. Start by
# cooperating.  2. If the opponent cooperated in the previous round, cooperate.
# 3. If the opponent defected in the previous round, defect.  4. If both players
# have cooperated for 5 consecutive rounds, defect once, then return to rule 2.
# 5. If both players have defected for 5 consecutive rounds, cooperate once,
# then return to rule 2.  6. For all other situations not covered by the above
# rules, cooperate.  This strategy maintains simplicity, neutrality, and logical
# consistency while adapting to the opponent's behavior and introducing
# occasional unpredictability to prevent exploitation.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by cooperating
      if self.first_round():
          return axl.Action.C
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 4: If both players have cooperated for 5 consecutive rounds, defect once, then return to rule 2
      if len(self.history) >= 5 and all(x == axl.Action.C for x in self.history[-5:]) and all(x == axl.Action.C for x in opponent.history[-5:]):
          return axl.Action.D
  
      # Rule 5: If both players have defected for 5 consecutive rounds, cooperate once, then return to rule 2
      if len(self.history) >= 5 and all(x == axl.Action.D for x in self.history[-5:]) and all(x == axl.Action.D for x in opponent.history[-5:]):
          return axl.Action.C
  
      # Rule 6: For all other situations not covered by the above rules, cooperate
      return axl.Action.C

# Here's a revised aggressive strategy for the iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play C with a 20% probability, otherwise play D.  3. If the opponent
# played D in the previous round, play D.  4. Every 7 to 13 rounds (randomly
# chosen), play C regardless of the opponent's previous move.  5. If mutual
# cooperation (C,C) occurred for 3 consecutive rounds, play D in the next round.
# 6. In the last 10 rounds of the game, always play D.  7. Repeat steps 2-6 for
# the duration of the game.  This strategy maintains aggression while
# introducing some unpredictability and adaptability to exploit cooperation
# without being overly predictable.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          self.coop_streak = 0  # Track consecutive mutual cooperation
          self.next_random_c_round = self._random.randint(7, 13)  # Random C round
          return axl.Action.D
  
      # Step 6: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 5: If mutual cooperation (C,C) occurred for 3 consecutive rounds, play D
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.C] * 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.D
  
      # Step 4: Every 7 to 13 rounds (randomly chosen), play C regardless of the opponent's previous move
      if len(self.history) == self.next_random_c_round:
          self.next_random_c_round += self._random.randint(7, 13)  # Set next random C round
          return axl.Action.C
  
      # Step 2: If the opponent played C in the previous round, play C with 20% probability, otherwise play D
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)
  
      # Step 3: If the opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

# Here's a revised, simpler cooperative strategy for the game:  1. Start by
# playing C.  2. If the opponent played C in the previous round, play C.  3. If
# the opponent played D in the previous round, play D for the next round, then
# return to C.  4. If the opponent has played D for five consecutive rounds,
# switch to always playing D until they play C again.  5. When the opponent
# plays C after a series of D moves, immediately return to C.  6. Continue this
# strategy for all 1000 rounds of the game.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by playing C
      if self.first_round():
          return axl.Action.C
  
      # Step 2: If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If the opponent played D in the previous round, play D for the next round, then return to C
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D
  
      # Step 4: If the opponent has played D for five consecutive rounds, switch to always playing D
      if opponent.history[-5:].count(axl.Action.D) == 5:
          # Step 5: When the opponent plays C after a series of D moves, immediately return to C
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          return axl.Action.D

# Here's a simplified and more neutral strategy:  1. Start by cooperating in the
# first round.  2. For the next 998 rounds:    a. If the opponent cooperated in
# the previous round, cooperate.    b. If the opponent defected in the previous
# round, defect.  3. In the final round, defect.  4. Repeat steps 2-3 for the
# duration of the game.  This strategy, known as "Tit-for-Tat with a defection
# on the last move," is simpler, more neutral, and avoids complex conditions or
# probabilities. It responds directly to the opponent's last move, maintaining a
# balance between cooperation and self-protection.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: cooperate
      if self.first_round():
          return axl.Action.C
      
      # If it's the last round, defect
      if len(self.history) == 999:
          return axl.Action.D
      
      # For rounds 2 to 999, tit-for-tat: copy opponent's last move
      return opponent.history[-1]

# Here's a revised, simpler, and more aggressive strategy:  1. Start by playing
# D in the first round.  2. Always play D, except in the following situation:
# 3. If the opponent has played C for 3 consecutive rounds, play C once, then
# immediately return to playing D.  4. In the last 20 rounds of the game, always
# play D regardless of the opponent's actions.  5. Repeat steps 2-4 for the
# duration of the game.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always play D
      if self.first_round():
          return axl.Action.D
  
      # Last 20 rounds: Always play D
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Check if opponent has played C for the last 3 consecutive rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          # Play C once, then return to D
          if len(self.history) == 0 or self.history[-1] == axl.Action.D:
              return axl.Action.C
  
      # Default action: Play D
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next round, then return to C.  4. If the opponent plays D for three
# consecutive rounds, switch to playing D until they cooperate again.  5. If the
# opponent returns to cooperation (plays C) after a series of defections, resume
# playing C.  6. In the last 2 rounds of the game, always play D regardless of
# the opponent's actions.  7. Occasionally (with a 5% chance) play D even when
# the conditions for cooperation are met to introduce some unpredictability.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Last two rounds: Always defect
      if len(self.history) >= 998:
          return axl.Action.D
  
      # Check if opponent defected in the last 3 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          # Switch to defecting until opponent cooperates
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If opponent defected in the last round, defect this round, then return to cooperation
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          # Introduce 5% chance of defection for unpredictability
          if self._random.random_choice(0.05):
              return axl.Action.D
          return axl.Action.C

# Here's a revised, simpler, and more neutral strategy:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected for three
# consecutive rounds, defect for the next round regardless of their action.  5.
# After every 10 rounds, reset and cooperate regardless of the opponent's
# previous action.  6. Continue this pattern for all 1000 rounds of the game.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 5: After every 10 rounds, reset and cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 4: If the opponent has defected for three consecutive rounds, defect
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect
      return axl.Action.D

# Here's a revised, simpler, and more aggressive strategy:  1. Start by playing
# D in the first round.  2. Always play D if the opponent played C in the
# previous round.  3. If the opponent played D in the previous round, play D
# with 90% probability and C with 10% probability.  4. If you're in the last 100
# rounds of the game, always play D.  5. If the opponent has played C for three
# consecutive rounds, play C once, then revert to D.  6. For all other
# situations, play D.  This revised strategy is simpler (reduced from 8 to 6
# rules), more aggressive (increased defection probability and extended end-game
# defection period), and maintains logical consistency. It focuses on exploiting
# cooperative opponents while being less forgiving of defection. The strategy is
# clearer and more straightforward, with rules ordered from specific to general
# conditions.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by playing D in the first round.
      if self.first_round():
          return axl.Action.D
  
      # Rule 4: If you're in the last 100 rounds of the game, always play D.
      if len(self.history) >= 900:
          return axl.Action.D
  
      # Rule 2: Always play D if the opponent played C in the previous round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D with 90% probability and C with 10% probability.
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1)
  
      # Rule 5: If the opponent has played C for three consecutive rounds, play C once, then revert to D.
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          if len(self.history) == 0 or self.history[-1] == axl.Action.D:
              return axl.Action.C
  
      # Rule 6: For all other situations, play D.
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round, then return to C.  4. If the opponent plays D for 5
# consecutive rounds, switch to playing D for the rest of the game.  5. If at
# any point the opponent switches back to cooperation (playing C for 2
# consecutive rounds), resume cooperating by playing C.  6. Continue this
# strategy until the end of the game, including the final rounds.

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
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.switched_to_defection = False  # Track if we switched to permanent defection
          return axl.Action.C  # Start by playing C
  
      # If we have switched to permanent defection, always play D
      if self.switched_to_defection:
          return axl.Action.D
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If opponent played D in the last round, increment consecutive defections
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0  # Reset if opponent cooperates
  
      # If opponent defects for 5 consecutive rounds, switch to permanent defection
      if self.consecutive_defections >= 5:
          self.switched_to_defection = True
          return axl.Action.D
  
      # If opponent cooperates for 2 consecutive rounds, reset to cooperation
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      # If opponent defected in the last round, play D this round, then return to C
      if last_opponent_move == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, continue cooperating
      return axl.Action.C

# Here's a revised, simpler strategy that aims to be more neutral and
# straightforward:  1. Start by cooperating in the first round.  2. If the
# opponent cooperated in the previous round, cooperate in the current round.  3.
# If the opponent defected in the previous round, defect in the current round.
# 4. If your average score per round falls below 2, switch to always defecting
# for the remainder of the game.  5. If the opponent has defected for 10
# consecutive rounds, switch to always defecting for the remainder of the game.
# 6. In all other cases, continue with steps 2 and 3.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Calculate the average score per round
      total_rounds = len(self.history)
      if total_rounds > 0:
          average_score = self.score / total_rounds
      else:
          average_score = 0
  
      # If the average score per round falls below 2, switch to always defecting
      if average_score < 2:
          return axl.Action.D
  
      # If the opponent has defected for 10 consecutive rounds, switch to always defecting
      if len(opponent.history) >= 10 and opponent.history[-10:].count(axl.Action.D) == 10:
          return axl.Action.D
  
      # If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the previous round, defect
      return axl.Action.D

# Here's a revised, simpler, and more aggressive strategy:  1. Start by playing
# D in the first round.  2. Always play D if the opponent played D in the
# previous round.  3. If the opponent played C in the previous round, play D
# with 90% probability and C with 10% probability.  4. In the last 100 rounds of
# the game, always play D.  5. If none of the above conditions are met, play D.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by playing D in the first round.
      if self.first_round():
          return axl.Action.D
  
      # 4. In the last 100 rounds of the game, always play D.
      if len(self.history) >= 900:
          return axl.Action.D
  
      # 2. Always play D if the opponent played D in the previous round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 3. If the opponent played C in the previous round, play D with 90% probability and C with 10% probability.
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.1)
  
      # 5. If none of the above conditions are met, play D.
      return axl.Action.D

# Here's a revised strategy:  1. Start by playing C in the first round.  2. If
# the opponent played C in the previous round, play C.  3. If the opponent
# played D in the previous round, play D for the next two rounds as punishment.
# 4. After the two-round punishment, return to playing C.  5. If the opponent's
# defection rate over the last 20 rounds exceeds 50%, switch to always playing D
# until their cooperation rate improves.  6. If the opponent's cooperation rate
# over the last 20 rounds returns to above 50%, resume the cooperative strategy
# starting from step 1.  7. Continue this strategy until the end of the game,
# including the final rounds.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          self.always_defect = False
          self.punishment_counter = 0  # Initialize punishment counter
          return axl.Action.C
  
      # Step 2: If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C and self.punishment_counter == 0:
          return axl.Action.C
  
      # Step 3: If the opponent played D in the previous round, play D for the next two rounds as punishment
      if opponent.history[-1] == axl.Action.D:
          if self.punishment_counter == 0:
              self.punishment_counter = 2  # Start two-round punishment
          if self.punishment_counter > 0:
              self.punishment_counter -= 1
              return axl.Action.D
  
      # Step 4: After the two-round punishment, return to playing C
      if self.punishment_counter == 0:
          # Step 5: Check the opponent's defection rate over the last 20 rounds
          if len(opponent.history) >= 20:
              last_20_defections = opponent.history[-20:].count(axl.Action.D)
              defection_rate = last_20_defections / 20
  
              # If defection rate exceeds 50%, switch to always playing D
              if defection_rate > 0.5:
                  self.always_defect = True
              else:
                  self.always_defect = False
  
          # Step 6: If the opponent's cooperation rate over the last 20 rounds returns to above 50%, resume cooperation
          if len(opponent.history) >= 20 and not self.always_defect:
              last_20_cooperations = opponent.history[-20:].count(axl.Action.C)
              cooperation_rate = last_20_cooperations / 20
              if cooperation_rate > 0.5:
                  return axl.Action.C
  
          # If always defect mode is active, play D
          if self.always_defect:
              return axl.Action.D
  
      # Default to playing C if no other condition is met
      return axl.Action.C

# Here's a revised, simpler, and more neutral strategy:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If both players have been alternating
# between cooperation and defection for the last 3 rounds, break the cycle by
# cooperating.  5. In the last round of the game, defect.  6. For all other
# situations, return to steps 2-3.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 5: In the last round of the game, defect
      if len(self.history) == 999:
          return axl.Action.D
  
      # Step 4: Check if both players have been alternating for the last 3 rounds
      if len(self.history) >= 3:
          if (self.history[-3] == axl.Action.C and opponent.history[-3] == axl.Action.D and
              self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.C and
              self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D) or \
             (self.history[-3] == axl.Action.D and opponent.history[-3] == axl.Action.C and
              self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.D and
              self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C):
              return axl.Action.C
  
      # Step 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

# Here's a revised, simpler, and more consistently aggressive strategy:  1.
# Start by playing D (defect) in the first round.  2. Always play D if the
# opponent played D in the previous round.  3. If the opponent played C in the
# previous round, play D with 90% probability and C with 10% probability.  4. If
# there are less than 100 rounds remaining, always play D.  5. Repeat these
# steps for all 1000 rounds of the game.  This strategy maintains aggression
# while simplifying the rules and reducing exploitability. It removes the
# periodic cooperation and the consecutive C-play rule, focusing on a more
# straightforward approach that still allows for occasional cooperation to probe
# the opponent's strategy.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 4: If there are less than 100 rounds remaining, always play D
      if len(self.history) >= 900:
          return axl.Action.D
  
      # Step 2: Always play D if the opponent played D in the previous round
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If the opponent played C in the previous round, play D with 90% probability and C with 10% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.1)

# Here's a simplified and improved cooperative strategy:  1. Start by playing C
# in the first round.  2. If the opponent played C in the previous round, play
# C.  3. If the opponent played D in the previous round, play D in the next
# round.  4. If the opponent has played D for three consecutive rounds, play D
# for the next round.  5. After playing D due to rule 4, revert to rule 2.  6.
# If the opponent has played C for three consecutive rounds after a period of
# defection, resume cooperation by playing C.  7. In the last 5 rounds of the
# game, always play C to encourage final cooperation.  8. If the opponent
# defects more than 70% of the time over the last 20 rounds, switch to always
# playing D until their defection rate drops below 70%.  9. Reassess the
# opponent's defection rate every 10 rounds when using rule 8.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 7: In the last 5 rounds, always play C
      if len(self.history) >= 995:
          return axl.Action.C
  
      # Rule 8: If opponent defects more than 70% of the time over the last 20 rounds, switch to D
      if len(self.history) >= 20:
          recent_defections = opponent.history[-20:].count(axl.Action.D)
          if recent_defections / 20 > 0.7:
              return axl.Action.D
  
      # Rule 9: Reassess the opponent's defection rate every 10 rounds when using rule 8
      if len(self.history) >= 10 and len(self.history) % 10 == 0:
          recent_defections = opponent.history[-10:].count(axl.Action.D)
          if recent_defections / 10 > 0.7:
              return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 4: If the opponent has played D for three consecutive rounds, play D
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D
  
      # Rule 6: If the opponent has played C for three consecutive rounds after a period of defection, resume cooperation
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.C
  
      # Default to cooperation if no other rule applies
      return axl.Action.C

# Here's a revised, simpler, and more neutral strategy:  1. Start by cooperating
# in the first round.  2. For the next 998 rounds:    a. If the opponent
# cooperated in the previous round, cooperate.    b. If the opponent defected in
# the previous round, defect.  3. In the final round, defect.  4. If at any
# point the opponent has defected for 5 consecutive rounds, switch to always
# defecting for the remainder of the game.  5. If both players have cooperated
# for 10 consecutive rounds, defect once, then return to the main strategy (step
# 2).  This strategy is simpler, more neutral, and takes into account the payoff
# structure by balancing cooperation and defection based on the opponent's
# recent behavior. It also addresses end-game behavior more subtly and includes
# a mechanism to protect against consistent defection.

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
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.defected_once_after_10_cooperations = False
          return axl.Action.C  # Start by cooperating
  
      # Check if the opponent has defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.D  # Switch to always defecting
  
      # Check if both players have cooperated for 10 consecutive rounds
      if self.history[-10:].count(axl.Action.C) == 10 and opponent.history[-10:].count(axl.Action.C) == 10:
          if not self.defected_once_after_10_cooperations:
              self.defected_once_after_10_cooperations = True
              return axl.Action.D  # Defect once after 10 consecutive cooperations
          else:
              self.defected_once_after_10_cooperations = False  # Reset flag after defection
  
      # Main strategy for rounds 2 to 999
      if len(self.history) < 999:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C  # Cooperate if opponent cooperated last round
          else:
              return axl.Action.D  # Defect if opponent defected last round
  
      # Final round (round 1000)
      return axl.Action.D  # Defect in the final round

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C (cooperate) in the first round.  2. If the opponent played C in the
# previous round, play C with 70% probability and D with 30% probability.  3. If
# the opponent played D in the previous round, play D in the current round.  4.
# If you're currently on a streak of mutual cooperation for 5 or more
# consecutive rounds, play D in the next round to exploit the opponent.  5. If
# both players have defected for 3 or more consecutive rounds, play C in the
# next round to attempt breaking the cycle.  6. Every 50 rounds, reassess your
# opponent's behavior:    - If they've cooperated more than 60% of the time,
# increase your cooperation probability by 10% (up to a maximum of 80%).    - If
# they've defected more than 60% of the time, decrease your cooperation
# probability by 10% (down to a minimum of 20%).  7. In the last 20 rounds of
# the game, always play D regardless of the opponent's actions.  8. For all
# other situations not covered by the above rules, play D.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_prob = 0.7  # Initial cooperation probability
          self.mutual_coop_streak = 0  # Track mutual cooperation streak
          self.mutual_defect_streak = 0  # Track mutual defection streak
          return axl.Action.C  # Start by cooperating
  
      # Rule 7: In the last 20 rounds, always play D
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Get the last round actions
      last_self_action = self.history[-1]
      last_opponent_action = opponent.history[-1]
  
      # Rule 4: If on a streak of mutual cooperation for 5 or more rounds, play D
      if last_self_action == axl.Action.C and last_opponent_action == axl.Action.C:
          self.mutual_coop_streak += 1
      else:
          self.mutual_coop_streak = 0
  
      if self.mutual_coop_streak >= 5:
          return axl.Action.D
  
      # Rule 5: If both players have defected for 3 or more consecutive rounds, play C
      if last_self_action == axl.Action.D and last_opponent_action == axl.Action.D:
          self.mutual_defect_streak += 1
      else:
          self.mutual_defect_streak = 0
  
      if self.mutual_defect_streak >= 3:
          return axl.Action.C
  
      # Rule 2: If opponent played C in the previous round, cooperate with 70% probability
      if last_opponent_action == axl.Action.C:
          return self._random.random_choice(self.coop_prob)
  
      # Rule 3: If opponent played D in the previous round, play D
      if last_opponent_action == axl.Action.D:
          return axl.Action.D
  
      # Rule 6: Every 50 rounds, reassess opponent's behavior
      if len(self.history) % 50 == 0:
          coop_rate = opponent.history.cooperations / len(opponent.history)
          if coop_rate > 0.6:
              self.coop_prob = min(self.coop_prob + 0.1, 0.8)
          elif coop_rate < 0.4:
              self.coop_prob = max(self.coop_prob - 0.1, 0.2)
  
      # Default action: play D
      return axl.Action.D

# Here's a revised, simpler cooperative strategy:  1. Start by playing C in the
# first round.  2. If the opponent played C in the previous round, play C.  3.
# If the opponent played D in the previous round, play D for the next three
# rounds, then return to C.  4. If the opponent plays D for five consecutive
# rounds, switch to playing D until they play C twice in a row.  5. Always
# return to playing C after successfully punishing defection.  6. Continue this
# pattern throughout the entire game, including the final rounds.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by playing C in the first round
      if self.first_round():
          self.punishing = False  # Track if we are in punishment mode
          self.punish_count = 0    # Track how many rounds of punishment are left
          self.defection_streak = 0  # Track consecutive defections by opponent
          self.waiting_for_two_Cs = False  # Track if we are waiting for two consecutive Cs
          return axl.Action.C
  
      # If we are waiting for two consecutive Cs to stop defecting
      if self.waiting_for_two_Cs:
          if opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
              self.waiting_for_two_Cs = False  # Stop waiting, return to cooperation
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If we are in punishment mode, continue punishing for 3 rounds
      if self.punishing:
          if self.punish_count > 0:
              self.punish_count -= 1
              return axl.Action.D
          else:
              self.punishing = False  # End punishment, return to cooperation
              return axl.Action.C
  
      # If the opponent played D in the last round, start punishing for 3 rounds
      if opponent.history[-1] == axl.Action.D:
          self.punishing = True
          self.punish_count = 2  # Punish for 3 rounds total (including this one)
          return axl.Action.D
  
      # If the opponent has defected for 5 consecutive rounds, switch to D until they play C twice in a row
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.waiting_for_two_Cs = True
          return axl.Action.D
  
      # Otherwise, cooperate if the opponent cooperated in the last round
      return axl.Action.C

# Here's a simplified and more neutral version of the strategy:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round with a 2/3 probability. Cooperate
# with a 1/3 probability.  4. In the last 10 rounds of the game, always defect
# regardless of the opponent's actions.  5. If the opponent has defected more
# than 70% of the time in the last 50 rounds, switch to always defecting for the
# next 20 rounds before reverting to the main strategy.  Follow these rules in
# the order presented, applying the first applicable condition in each round.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          self._defect_streak_start = 0
          return axl.Action.C
  
      # Rule 4: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 5: If opponent has defected more than 70% of the time in the last 50 rounds, defect for 20 rounds
      if len(self.history) > 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.7:
              if len(self.history) < 970:  # Ensure we don't overlap with Rule 4
                  if len(self.history) - self._defect_streak_start < 20:
                      return axl.Action.D
                  else:
                      self._defect_streak_start = 0
              else:
                  return axl.Action.D
          else:
              self._defect_streak_start = len(self.history)
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect with 2/3 probability, cooperate with 1/3 probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(1/3)

# Here's a revised, more aggressive and simpler strategy:  1. Always defect (D)
# in the first round.  2. If the opponent cooperated (C) in the previous round,
# defect (D) in the current round.  3. If the opponent defected (D) in the
# previous round, defect (D) in the current round.  4. If the opponent has
# cooperated (C) for five consecutive rounds, cooperate (C) for one round, then
# immediately return to defecting (D).  5. Repeat steps 2-4 for the duration of
# the game.  This strategy maintains aggression, simplifies the decision-making
# process, and reduces exploitability while still allowing for occasional
# cooperation to potentially increase overall payoff.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Always defect in the first round
      if self.first_round():
          return axl.Action.D
  
      # If the opponent has cooperated for the last 5 rounds, cooperate once
      if len(opponent.history) >= 5 and all(action == axl.Action.C for action in opponent.history[-5:]):
          if len(self.history) == 0 or self.history[-1] == axl.Action.D:
              return axl.Action.C
  
      # Otherwise, always defect
      return axl.Action.D

# Here's a simplified, more cooperative strategy:  1. Start by playing C in the
# first round.  2. If the opponent played C in the previous round, play C.  3.
# If the opponent played D in the previous round, play D for the next two rounds
# as punishment.  4. After the two-round punishment, return to playing C.  5. If
# the opponent plays D for five consecutive rounds, switch to always playing D
# for the remainder of the game.  6. Continue this strategy until the end of the
# game, without any special end-game adjustments.  This revised strategy is
# simpler, more cooperative, and addresses the main points of feedback. It
# removes score-based decisions, eliminates the end-game defection, and extends
# the punishment period slightly to maintain a cooperative approach while
# deterring exploitation.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, play C
      if self.first_round():
          self.punishment_counter = 0  # Initialize punishment counter
          self.defection_streak = 0  # Initialize defection streak counter
          return axl.Action.C
  
      # Check if opponent has defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.D  # Switch to always defecting
  
      # If in punishment phase, decrement punishment counter and play D
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # If opponent defected in the last round, start punishment phase
      if opponent.history[-1] == axl.Action.D:
          self.punishment_counter = 2  # Punish for the next two rounds
          return axl.Action.D
  
      # Otherwise, cooperate if opponent cooperated in the last round
      return axl.Action.C

# Here's a revised, simpler strategy that aims to be more neutral and better
# aligned with the game's payoff structure:  1. Start by cooperating in the
# first round.  2. If the opponent cooperated in the previous round, cooperate
# in the current round.  3. If the opponent defected in the previous round,
# defect in the current round.  4. If both players have cooperated for the last
# 5 rounds, cooperate in the current round.  5. If both players have defected
# for the last 5 rounds, cooperate in the current round.  6. For all other
# situations not covered by the above rules, cooperate.  This strategy maintains
# simplicity, neutrality, and considers the payoff structure by encouraging
# mutual cooperation while protecting against exploitation. It removes arbitrary
# thresholds and end-game behavior, focusing on recent history to make
# decisions.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 4: If both players have cooperated for the last 5 rounds, cooperate
      if len(self.history) >= 5 and all(x == axl.Action.C for x in self.history[-5:]) and all(x == axl.Action.C for x in opponent.history[-5:]):
          return axl.Action.C
  
      # Rule 5: If both players have defected for the last 5 rounds, cooperate
      if len(self.history) >= 5 and all(x == axl.Action.D for x in self.history[-5:]) and all(x == axl.Action.D for x in opponent.history[-5:]):
          return axl.Action.C
  
      # Rule 6: For all other situations, cooperate
      return axl.Action.C

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D.  4.
# If the opponent has played C for 3 consecutive rounds, play C once, then
# resume the strategy.  5. In the last 10 rounds of the game, always play D.  6.
# Repeat steps 2-5 for the duration of the game.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 5: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: If the opponent has played C for 3 consecutive rounds, play C once
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.C
  
      # Step 2 and 3: If the opponent played C or D in the previous round, play D
      return axl.Action.D

# Here's a revised, simpler cooperative strategy for the iterated game:  1.
# Start by playing C in the first round.  2. For subsequent rounds:    - If the
# opponent played C in the previous round, play C.    - If the opponent played D
# in the previous round, play D.  3. Every 5 rounds, regardless of the
# opponent's last move:    - Play C to attempt to re-establish cooperation.  4.
# If the opponent has played D for 3 consecutive rounds:    - Play D for the
# next 2 rounds, then return to step 2.  5. In the last round of the game:    -
# Play D to protect against end-game exploitation.  Follow these steps in order,
# applying the first relevant condition encountered.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Play C if opponent played C in the previous round, else play D
      if opponent.history[-1] == axl.Action.C:
          next_move = axl.Action.C
      else:
          next_move = axl.Action.D
  
      # Step 3: Every 5 rounds, play C to attempt to re-establish cooperation
      if len(self.history) % 5 == 0:
          return axl.Action.C
  
      # Step 4: If opponent has played D for 3 consecutive rounds, play D for the next 2 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D] * 2:
              return axl.Action.D
  
      # Step 5: In the last round of the game, play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # Default to the next move determined in Step 2
      return next_move

# Here's a revised strategy:  1. Start by cooperating in the first round.  2. If
# the opponent cooperated in the previous round, cooperate in the current round.
# 3. If the opponent defected in the previous round, defect in the current
# round.  4. If your score is more than 15 points behind your opponent's after
# every 100 rounds, defect for the next 3 rounds.  5. In the last 20 rounds of
# the game, alternate between cooperating and defecting, starting with
# defection.  6. For all other situations not covered by the above rules,
# randomly choose to cooperate or defect with equal probability.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          self._defect_streak = 0
          return axl.Action.C
  
      # Rule 5: In the last 20 rounds, alternate between cooperating and defecting, starting with defection
      if len(self.history) >= 980:
          if len(self.history) % 2 == 0:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rule 4: If your score is more than 15 points behind your opponent's after every 100 rounds, defect for the next 3 rounds
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          if opponent.score - self.score > 15:
              self._defect_streak = 3
      if self._defect_streak > 0:
          self._defect_streak -= 1
          return axl.Action.D
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate in the current round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect in the current round
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 6: For all other situations, randomly choose to cooperate or defect with equal probability
      return self._random.random_choice(0.5)

# Here's a simplified and more aggressive version of the strategy:  1. Always
# defect in the first round.  2. If the opponent defected in the previous round,
# defect.  3. If the opponent cooperated in the previous round, defect with 90%
# probability and cooperate with 10% probability.  4. In the last 20 rounds of
# the game, always defect.  5. If your current score is lower than the
# opponent's score, always defect until you're ahead.  Follow these rules in
# order, applying the first applicable rule in each round.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Always defect in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 4: In the last 20 rounds, always defect
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Rule 5: If your score is lower than the opponent's, always defect until you're ahead
      if self.score < opponent.score:
          return axl.Action.D
  
      # Rule 2: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 3: If the opponent cooperated in the previous round, defect with 90% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.1)  # 10% chance to cooperate, 90% to defect

# Here's a revised strategy:  1. Start by playing C in the first round.  2. If
# the opponent played C in the previous round, play C.  3. If the opponent
# played D in the previous round, play D in the next round, then return to C.
# 4. If the opponent plays D for three consecutive rounds, play D until they
# cooperate again.  5. If the opponent returns to cooperation (plays C) after a
# series of defections, immediately resume cooperating (play C).  6. Continue
# this pattern throughout the game, including the final rounds.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent played D in the previous round
      if opponent.history[-1] == axl.Action.D:
          # If the opponent has played D for the last 3 consecutive rounds, play D until they cooperate again
          if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
              if opponent.history[-1] == axl.Action.C:
                  return axl.Action.C
              else:
                  return axl.Action.D
          # Otherwise, play D in the next round, then return to C
          return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# cooperating.  2. If the opponent cooperated in the previous round, cooperate.
# 3. If the opponent defected in the previous round, defect.  4. If your score
# is more than 15 points behind your opponent's, defect for the next round.  5.
# If you're in the last 50 rounds of the game, defect with a 70% probability and
# cooperate with a 30% probability.  6. In all other situations, cooperate.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by cooperating.
      if self.first_round():
          return axl.Action.C
  
      # 4. If your score is more than 15 points behind your opponent's, defect for the next round.
      if self.score < opponent.score - 15:
          return axl.Action.D
  
      # 5. If you're in the last 50 rounds of the game, defect with a 70% probability and cooperate with a 30% probability.
      if len(self.history) >= 950:
          return self._random.random_choice(0.3)
  
      # 2. If the opponent cooperated in the previous round, cooperate.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. If the opponent defected in the previous round, defect.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 6. In all other situations, cooperate.
      return axl.Action.C

# Here's a revised, simpler, and more consistently aggressive strategy:  1.
# Start by defecting (D) in the first round.  2. If the opponent cooperated (C)
# in the previous round, defect (D) in the current round.  3. If the opponent
# defected (D) in the previous round, randomly choose to cooperate (C) with a
# 20% probability or defect (D) with an 80% probability.  4. If you have
# defected for 10 consecutive rounds, cooperate (C) once, then return to step 2.
# 5. In the last 20 rounds of the game, always defect (D) regardless of the
# opponent's actions.  6. Repeat steps 2-5 for the duration of the game, except
# for the final 20 rounds where step 5 takes precedence.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 5: In the last 20 rounds, always defect
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Step 4: If defected for 10 consecutive rounds, cooperate once
      if self.history[-10:].count(axl.Action.D) == 10:
          return axl.Action.C
  
      # Step 2: If opponent cooperated in the previous round, defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Step 3: If opponent defected in the previous round, cooperate with 20% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.2)

# Here's a revised, simpler cooperative strategy for the game:  1. Start by
# playing C in the first round.  2. For the next 990 rounds:    - If the
# opponent played C in the previous round, play C.    - If the opponent played D
# in the previous round, play D.    - Every 20 rounds, play C regardless of the
# opponent's last move.  3. For the last 10 rounds:    - Continue with the same
# pattern as in step 2, without changing behavior.  Follow these steps in order,
# applying the first relevant condition encountered.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always play C
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # For the first 990 rounds
      if round_number <= 990:
          # Every 20 rounds, play C regardless of opponent's last move
          if round_number % 20 == 0:
              return axl.Action.C
          # Otherwise, mimic the opponent's last move
          else:
              return opponent.history[-1]
  
      # For the last 10 rounds, continue the same pattern
      else:
          # Every 20 rounds, play C regardless of opponent's last move
          if round_number % 20 == 0:
              return axl.Action.C
          # Otherwise, mimic the opponent's last move
          else:
              return opponent.history[-1]

# Here's a revised strategy:  1. Start by cooperating in the first round.  2. If
# the opponent cooperated in the previous round, cooperate in the current round.
# 3. If the opponent defected in the previous round, defect in the current
# round.  4. If your score is more than 15 points behind your opponent's after
# every 100 rounds, defect for the next 3 rounds.  5. In the last 20 rounds of
# the game, always defect.  6. For all other situations, cooperate.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by cooperating in the first round.
      if self.first_round():
          self.defect_streak = 0
          return axl.Action.C
  
      # 5. In the last 20 rounds of the game, always defect.
      if len(self.history) >= 980:
          return axl.Action.D
  
      # 4. If your score is more than 15 points behind your opponent's after every 100 rounds, defect for the next 3 rounds.
      if len(self.history) % 100 == 0 and len(self.history) > 0:
          if opponent.score - self.score > 15:
              self.defect_streak = 3
          else:
              self.defect_streak = 0
  
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # 2. If the opponent cooperated in the previous round, cooperate in the current round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. If the opponent defected in the previous round, defect in the current round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 6. For all other situations, cooperate.
      return axl.Action.C

# Here's a revised, simpler, and more consistently aggressive strategy:  1.
# Always defect (D) in the first round.  2. If the opponent cooperated (C) in
# the previous round, defect (D) in the current round.  3. If the opponent
# defected (D) in the previous round, also defect (D) in the current round.  4.
# Every 5 rounds, regardless of the opponent's previous move, defect (D).  5. In
# the last 100 rounds of the game, always defect (D).  6. If none of the above
# conditions apply, defect (D).

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Always defect in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 5: In the last 100 rounds, always defect
      if len(self.history) >= 900:
          return axl.Action.D
  
      # Rule 4: Every 5 rounds, defect
      if len(self.history) % 5 == 0:
          return axl.Action.D
  
      # Rule 2: If the opponent cooperated in the previous round, defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 6: If none of the above conditions apply, defect
      return axl.Action.D

# Here's a revised, simpler cooperative strategy for the game:  1. Start by
# playing C.  2. If the opponent played C in the previous round, play C.  3. If
# the opponent played D in the previous round, play D in the next round, then
# return to C.  4. If the opponent plays D for five consecutive rounds, switch
# to always playing D.  5. If at any point the opponent switches back to
# cooperation (plays C for 2 consecutive rounds), resume cooperating by playing
# C.  6. In the last round of the game, play D.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, play C
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.switched_to_defection = False  # Track if we switched to always defect
          return axl.Action.C
  
      # If it's the last round, play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # If we have switched to always defect, continue defecting
      if self.switched_to_defection:
          # Check if opponent cooperates for 2 consecutive rounds to resume cooperation
          if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
              self.switched_to_defection = False
              return axl.Action.C
          return axl.Action.D
  
      # Check if opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          # If opponent defected for 5 consecutive rounds, switch to always defect
          if self.consecutive_defections >= 5:
              self.switched_to_defection = True
              return axl.Action.D
          # Otherwise, defect this round and return to cooperation next round
          return axl.Action.D
      else:
          # Reset consecutive defections if opponent cooperates
          self.consecutive_defections = 0
          return axl.Action.C

# Here's a revised, simpler strategy:  1. Start by cooperating in the first
# round.  2. If the opponent cooperated in the previous round, cooperate.  3. If
# the opponent defected in the previous round, defect.  4. If the opponent has
# defected in the last 3 consecutive rounds, defect for the next 3 rounds.  5.
# If none of the above conditions are met, cooperate.  6. Repeat steps 2-5 for
# all rounds, including the final rounds.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          # Step 4: If the opponent has defected in the last 3 consecutive rounds, defect for the next 3 rounds
          if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
              if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D] * 3:
                  return axl.Action.D  # Continue defecting for 3 rounds
              return axl.Action.D  # Start defecting for 3 rounds
  
          return axl.Action.D
  
      # Step 5: If none of the above conditions are met, cooperate
      return axl.Action.C

# Here's a revised, simpler, and more aggressive strategy:  1. Start by
# defecting (D) in the first round.  2. Always defect if the opponent defected
# in the previous round.  3. If the opponent cooperated in the previous round,
# defect 90% of the time and cooperate 10% of the time.  4. If you're behind in
# score, always defect for the next 5 rounds.  5. In the last 20 rounds of the
# game, always defect.  6. If the opponent has cooperated for 5 consecutive
# rounds, cooperate once, then return to the main strategy.  7. For all other
# situations, defect.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # 1. Start by defecting (D) in the first round.
      if self.first_round():
          return axl.Action.D
  
      # 4. If you're behind in score, always defect for the next 5 rounds.
      if self.score < opponent.score:
          if len(self.history) < 5 or self.history[-5:].count(axl.Action.D) < 5:
              return axl.Action.D
  
      # 5. In the last 20 rounds of the game, always defect.
      if len(self.history) >= 980:
          return axl.Action.D
  
      # 6. If the opponent has cooperated for 5 consecutive rounds, cooperate once, then return to the main strategy.
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.C] * 5:
          if len(self.history) < 1 or self.history[-1] != axl.Action.C:
              return axl.Action.C
  
      # 2. Always defect if the opponent defected in the previous round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 3. If the opponent cooperated in the previous round, defect 90% of the time and cooperate 10% of the time.
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.1)
  
      # 7. For all other situations, defect.
      return axl.Action.D

# Here's a revised, simpler cooperative strategy:  1. Start by playing C.  2. If
# the opponent played C in the previous round, play C.  3. If the opponent
# played D in the previous round, play D for the next two rounds as punishment.
# 4. After the two-round punishment, return to playing C.  5. If the opponent
# plays D for five consecutive rounds, switch to always playing D for the
# remainder of the game.  6. Continue this strategy until the end of the game,
# including the last round.

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
          self.punishment_rounds = 0
          self.defection_streak = 0
          self.always_defect = False
          return axl.Action.C
  
      # If always defect mode is activated, continue defecting
      if self.always_defect:
          return axl.Action.D
  
      # Check if opponent has defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.always_defect = True
          return axl.Action.D
  
      # If in punishment mode, continue defecting for the next two rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # If opponent defected in the last round, enter punishment mode
      if opponent.history[-1] == axl.Action.D:
          self.punishment_rounds = 2
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simplified and more neutral strategy:  1. Start by cooperating in the
# first round.  2. For subsequent rounds:    a. If the opponent cooperated in
# the previous round, cooperate.    b. If the opponent defected in the previous
# round, defect.  3. Every 50 rounds, assess the total scores:    a. If your
# score is higher, cooperate.    b. If your score is lower or equal, defect.  4.
# In the last round, defect.  Follow these rules in the order presented. This
# strategy is simpler, more neutral, and considers the payoff structure
# implicitly through score comparison.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # 2. For subsequent rounds:
      # a. If the opponent cooperated in the previous round, cooperate.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # b. If the opponent defected in the previous round, defect.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 3. Every 50 rounds, assess the total scores:
      if len(self.history) % 50 == 0:
          if self.score > opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # 4. In the last round, defect.
      if len(self.history) == 999:
          return axl.Action.D

# Here's a revised, simpler, and more consistently aggressive strategy:  1.
# Always start by defecting (D) in the first round.  2. If the opponent
# cooperated (C) in the previous round, defect (D) in the current round.  3. If
# the opponent defected (D) in the previous round, cooperate (C) in the current
# round.  4. If you've cooperated for two consecutive rounds, switch to
# defecting (D) regardless of the opponent's last move.  5. In the last 20
# rounds of the game, always defect (D) regardless of the opponent's actions.
# 6. Follow these rules for all rounds, except as noted in step 5.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Always start by defecting in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 5: In the last 20 rounds, always defect
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Step 4: If you've cooperated for two consecutive rounds, switch to defecting
      if len(self.history) >= 2 and self.history[-1] == axl.Action.C and self.history[-2] == axl.Action.C:
          return axl.Action.D
  
      # Step 2: If the opponent cooperated in the previous round, defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Step 3: If the opponent defected in the previous round, cooperate
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.C

# Here's a simplified, more cooperative strategy based on the feedback:  1.
# Start by playing C in the first round.  2. If the opponent played C in the
# previous round, play C.  3. If the opponent played D in the previous round,
# play D in the next round as a single punishment.  4. After punishing with D,
# return to playing C in the following round.  5. If the opponent plays D for
# five consecutive rounds, switch to always playing D for the remainder of the
# game.  6. Continue this strategy until the end of the game, without changing
# behavior in the final rounds.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, play C
      if self.first_round():
          return axl.Action.C
  
      # Check if the opponent has defected for the last 5 consecutive rounds
      if len(opponent.history) >= 5 and all(move == axl.Action.D for move in opponent.history[-5:]):
          return axl.Action.D  # Switch to always defecting
  
      # If the opponent defected in the last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a revised strategy:  1. Start by cooperating.  2. If the opponent
# cooperated in the previous round, cooperate.  3. If the opponent defected in
# the previous round, defect.  4. If the opponent has defected more than 50% of
# the time in the last 5 rounds, defect.  5. If none of the above conditions are
# met, cooperate.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by cooperating.
      if self.first_round():
          return axl.Action.C
  
      # 2. If the opponent cooperated in the previous round, cooperate.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. If the opponent defected in the previous round, defect.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 4. If the opponent has defected more than 50% of the time in the last 5 rounds, defect.
      if len(opponent.history) >= 5 and opponent.history[-5:].count(axl.Action.D) > 2:
          return axl.Action.D
  
      # 5. If none of the above conditions are met, cooperate.
      return axl.Action.C

# Here's a revised, simpler and more aggressive strategy:  1. Start by playing D
# in the first round.  2. Always play D, except in the following situation:  3.
# If you and your opponent have both played D for 5 consecutive rounds, play C
# once.  4. If the opponent responds to your C with a C, immediately return to D
# on the next round.  5. In the last 20 rounds of the game, always play D
# regardless of the opponent's actions.  6. Repeat steps 2-5 for the duration of
# the game.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 5: In the last 20 rounds, always play D
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Step 3: If both players have played D for 5 consecutive rounds, play C once
      if len(self.history) >= 5 and all(
          move == axl.Action.D for move in self.history[-5:]
      ) and all(move == axl.Action.D for move in opponent.history[-5:]):
          return axl.Action.C
  
      # Step 4: If opponent responds to your C with a C, return to D
      if len(self.history) > 1 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Step 2: Always play D otherwise
      return axl.Action.D

# Here's a revised, simpler cooperative strategy:  1. Start by playing C.  2. If
# the opponent played C in the previous round, play C.  3. If the opponent
# played D in the previous round, play D for the next two rounds as punishment.
# 4. After the two-round punishment, return to playing C.  5. Repeat steps 2-4
# for the entire game, including the last round.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by playing C
      if self.first_round():
          return axl.Action.C
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If the opponent played C in the previous round, play C
      if last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # If the opponent played D in the previous round, punish with D for two rounds
      if last_opponent_move == axl.Action.D:
          # Check if we are in the punishment phase
          if len(self.history) >= 2 and self.history[-2:] == [axl.Action.D, axl.Action.D]:
              # After two rounds of punishment, return to C
              return axl.Action.C
          else:
              # Continue punishment by playing D
              return axl.Action.D

# Here's a revised, simpler strategy that aims to be more neutral and better
# aligned with the game's payoff structure:  1. Start by cooperating.  2. If the
# opponent cooperated in the previous round, cooperate.  3. If the opponent
# defected in the previous round, defect.  4. If both players have been
# alternating between cooperation and defection for the last 3 rounds,
# cooperate.  5. If your score is more than 5 points behind your opponent's,
# defect.  6. In all other situations, randomly choose to cooperate or defect
# with equal probability.  7. Repeat steps 2-6 for each subsequent round until
# the game ends.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by cooperating
      if self.first_round():
          return axl.Action.C
  
      # Step 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 4: If both players have been alternating between cooperation and defection for the last 3 rounds, cooperate
      if len(self.history) >= 3:
          last_three_self = self.history[-3:]
          last_three_opponent = opponent.history[-3:]
          if (last_three_self == [axl.Action.C, axl.Action.D, axl.Action.C] and
              last_three_opponent == [axl.Action.D, axl.Action.C, axl.Action.D]):
              return axl.Action.C
  
      # Step 5: If your score is more than 5 points behind your opponent's, defect
      if self.score < opponent.score - 5:
          return axl.Action.D
  
      # Step 6: In all other situations, randomly choose to cooperate or defect with equal probability
      return self._random.random_choice(0.5)

# Here's a simplified, more aggressive strategy:  1. Start by playing D in the
# first round.  2. Always play D if the opponent played C in the previous round.
# 3. If the opponent played D in the previous round, play D with 90% probability
# and C with 10% probability.  4. In the last 20 rounds of the game, always play
# D.  5. Repeat these steps for all 1000 rounds, adjusting your play based only
# on the opponent's previous move.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Total number of rounds in the game
      total_rounds = 1000
      # Number of rounds left
      rounds_left = total_rounds - len(self.history)
      
      # 1. Start by playing D in the first round.
      if self.first_round():
          return axl.Action.D
      
      # 4. In the last 20 rounds of the game, always play D.
      if rounds_left <= 20:
          return axl.Action.D
      
      # 2. Always play D if the opponent played C in the previous round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      
      # 3. If the opponent played D in the previous round, play D with 90% probability and C with 10% probability.
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1)  # 10% chance to play C, otherwise D

# Here's a simplified cooperative strategy:  1. Start by playing C.  2. If your
# opponent played C in the previous round, play C.  3. If your opponent played D
# in the previous round, play D in the next round as punishment.  4. After
# punishing with D, return to playing C in the following round.  5. If your
# opponent plays D for three consecutive rounds, switch to always playing D for
# the remainder of the game.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, play C
      if self.first_round():
          return axl.Action.C
  
      # Check if opponent has defected for the last 3 consecutive rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D
  
      # If opponent played D in the last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, return to playing C
      return axl.Action.C

# Here's a simplified and more neutral version of the strategy:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent cooperated in the previous round, cooperate.    - If the opponent
# defected in the previous round, defect.  3. Every 20 rounds, regardless of the
# opponent's previous move:    - If your total score is lower than the
# opponent's, defect once.    - Otherwise, cooperate.  4. If the opponent has
# defected for 3 consecutive rounds, defect once, then return to step 2.  5. If
# you and your opponent have both cooperated for 10 consecutive rounds, continue
# cooperating until the opponent defects.  6. Repeat steps 2-5 until the game
# ends.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Cooperate if opponent cooperated in the previous round, otherwise defect
      if opponent.history[-1] == axl.Action.C:
          action = axl.Action.C
      else:
          action = axl.Action.D
  
      # Step 3: Every 20 rounds, check scores and defect if losing
      if len(self.history) % 20 == 0:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if my_score < opponent_score:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Step 4: If opponent defected for 3 consecutive rounds, defect once
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D
  
      # Step 5: If both cooperated for 10 consecutive rounds, continue cooperating
      if len(self.history) >= 10 and self.history[-10:] == [axl.Action.C] * 10 and opponent.history[-10:] == [axl.Action.C] * 10:
          return axl.Action.C
  
      # Default action based on step 2
      return action

# Here's a revised, simpler, and more aggressive strategy:  1. Start by playing
# D in the first round.  2. Always play D unless one of the following conditions
# is met:  3. If the opponent has played C for 3 consecutive rounds, play C in
# the next round only.  4. If your score is at least 20 points higher than your
# opponent's, play C for one round.  5. For any situation not covered by the
# above rules, play D.  6. In the last 50 rounds of the game, always play D
# regardless of other conditions.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by playing D in the first round.
      if self.first_round():
          return axl.Action.D
  
      # 6. In the last 50 rounds of the game, always play D regardless of other conditions.
      if len(self.history) >= 950:
          return axl.Action.D
  
      # 3. If the opponent has played C for 3 consecutive rounds, play C in the next round only.
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.C
  
      # 4. If your score is at least 20 points higher than your opponent's, play C for one round.
      if self.score - opponent.score >= 20:
          return axl.Action.C
  
      # 2 & 5. Always play D unless one of the above conditions is met.
      return axl.Action.D

# Here's a revised strategy taking the feedback into account:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After the two-round punishment, return
# to playing C.  5. If the opponent defects more than 50% of the time over the
# last 20 rounds, switch to always playing D until their cooperation rate
# improves.  6. If the opponent returns to consistent cooperation (over 70%
# cooperation in the last 20 rounds), resume the cooperative strategy from step
# 2.  7. Continue this strategy until the end of the game, without changing
# behavior in the final rounds.

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
          self.always_defect = False
          self.punishment_rounds = 0  # Tracks how many punishment rounds are left
          return axl.Action.C  # Start by playing C
  
      # If in punishment mode, continue defecting for the next two rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If the opponent defected in the last round, enter punishment mode
      if last_opponent_move == axl.Action.D:
          self.punishment_rounds = 2  # Punish for the next two rounds
          return axl.Action.D
  
      # Check the opponent's cooperation rate over the last 20 rounds
      if len(opponent.history) >= 20:
          last_20_moves = opponent.history[-20:]
          defections_in_last_20 = last_20_moves.count(axl.Action.D)
          cooperation_rate = (20 - defections_in_last_20) / 20
  
          # If opponent defects more than 50% of the time, switch to always defecting
          if defections_in_last_20 > 10:
              self.always_defect = True
          # If opponent cooperates more than 70% of the time, resume normal strategy
          elif cooperation_rate > 0.7:
              self.always_defect = False
  
      # If in always defect mode, continue defecting
      if self.always_defect:
          return axl.Action.D
  
      # Otherwise, cooperate if the opponent cooperated in the last round
      if last_opponent_move == axl.Action.C:
          return axl.Action.C

# Here's a revised, simpler, and more neutral strategy:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If both players have cooperated for
# the last 5 rounds, defect once to test the opponent's response.  5. If your
# score is more than 15 points behind your opponent's, defect for the next
# round.  6. For all other situations not covered by the above rules, cooperate.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate in the current round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect in the current round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 4: If both players have cooperated for the last 5 rounds, defect once to test the opponent's response.
      if len(self.history) >= 5 and all(x == axl.Action.C for x in self.history[-5:]) and all(x == axl.Action.C for x in opponent.history[-5:]):
          return axl.Action.D
  
      # Rule 5: If your score is more than 15 points behind your opponent's, defect for the next round.
      if self.score < opponent.score - 15:
          return axl.Action.D
  
      # Rule 6: For all other situations not covered by the above rules, cooperate.
      return axl.Action.C

# Here's a revised, simpler, and more aggressive strategy:  1. Start by
# defecting (D) in the first round.  2. If the opponent cooperated (C) in the
# previous round, defect (D) in the current round.  3. If the opponent defected
# (D) in the previous round, defect (D) in the current round.  4. If you're
# currently on a streak of ten or more mutual defections (D,D), cooperate (C)
# for one round to try and break the cycle.  5. In the last 20 rounds of the
# game, always defect (D) regardless of the opponent's actions.  6. For any
# situation not covered by the above rules, defect (D).

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by defecting in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 5: In the last 20 rounds of the game, always defect
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Rule 4: If on a streak of 10 or more mutual defections, cooperate for one round
      if len(self.history) >= 10 and all(
          x == axl.Action.D and y == axl.Action.D for x, y in zip(self.history[-10:], opponent.history[-10:])
      ):
          return axl.Action.C
  
      # Rule 2 and 3: If the opponent cooperated or defected in the previous round, defect
      return axl.Action.D

# Here's a simplified cooperative strategy for the game:  1. Start by playing C.
# 2. If the opponent played C in the previous round, play C.  3. If the opponent
# played D in the previous round, play D for the next two rounds as punishment.
# 4. After punishing, return to playing C.  5. If the opponent defects three
# times in a row, switch to always playing D for the rest of the game.  6. In
# the last 5 rounds of the game, always play D.  This strategy maintains a
# cooperative approach while simplifying the conditions and removing arbitrary
# point thresholds. It keeps the core cooperative behavior, includes a slightly
# stronger punishment mechanism, and accounts for end-game scenarios more
# concisely.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, play C
      if self.first_round():
          self.punishment_count = 0  # Track how many rounds of punishment are left
          self.defection_streak = 0  # Track consecutive defections by the opponent
          self.always_defect = False  # Flag to switch to always defecting
          return axl.Action.C
  
      # If the opponent has defected three times in a row, switch to always defecting
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.always_defect = True
  
      # If we're in the last 5 rounds, always play D
      if len(self.history) >= 995:
          return axl.Action.D
  
      # If we're in the "always defect" mode, play D
      if self.always_defect:
          return axl.Action.D
  
      # If we're in the middle of a punishment phase, continue defecting
      if self.punishment_count > 0:
          self.punishment_count -= 1
          return axl.Action.D
  
      # If the opponent defected in the last round, start a 2-round punishment
      if opponent.history[-1] == axl.Action.D:
          self.punishment_count = 2
          return axl.Action.D
  
      # Otherwise, cooperate if the opponent cooperated in the last round
      return axl.Action.C

# Here's a simplified and more neutral strategy:  1. Start by cooperating in the
# first round.  2. If the opponent cooperated in the previous round, cooperate
# in the current round.  3. If the opponent defected in the previous round,
# defect in the current round with a 1/2 probability. Otherwise, cooperate.  4.
# If the opponent has defected in the last 3 consecutive rounds, defect in the
# next round.  5. After every 100 rounds, if your total score is lower than your
# opponent's, increase the probability of defection after opponent's defection
# to 2/3 for the next 100 rounds.  6. In all other cases, return to the main
# strategy (steps 2-3).

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
          self.defection_probability = 0.5  # Initial defection probability after opponent defects
          self.rounds_since_last_check = 0  # Track rounds since last score check
          return axl.Action.C  # Cooperate in the first round
  
      # Check if opponent defected in the last 3 consecutive rounds
      if len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:]):
          return axl.Action.D  # Defect if opponent defected in the last 3 rounds
  
      # Main strategy: respond to opponent's last move
      if opponent.history[-1] == axl.Action.D:
          # Defect with the current probability, otherwise cooperate
          return self._random.random_choice(self.defection_probability)
      else:
          return axl.Action.C  # Cooperate if opponent cooperated in the last round
  
      # Every 100 rounds, check if we need to adjust the defection probability
      self.rounds_since_last_check += 1
      if self.rounds_since_last_check >= 100:
          self.rounds_since_last_check = 0  # Reset the counter
          # Compare scores and adjust defection probability if necessary
          if self.score < opponent.score:
              self.defection_probability = 2 / 3  # Increase defection probability
          else:
              self.defection_probability = 0.5  # Reset to default probability

# Here's a revised, simpler, and more aggressive strategy:  1. Start by playing
# D in the first round.  2. Always play D if the opponent played C in the
# previous round.  3. If the opponent played D in the previous round, play D.
# 4. If the opponent has played C for 5 consecutive rounds, play C once, then
# return to playing D.  5. In the last 50 rounds of the game, always play D
# regardless of the opponent's moves.  6. For any situation not covered by the
# above rules, play D.  This strategy is more straightforward, consistently
# aggressive, and aligns better with the payoff structure while maintaining a
# small element of responsiveness to persistent cooperation.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round.
      if self.first_round():
          return axl.Action.D
  
      # Rule 5: In the last 50 rounds of the game, always play D.
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Rule 2: Always play D if the opponent played C in the previous round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 4: If the opponent has played C for 5 consecutive rounds, play C once, then return to playing D.
      if len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:]):
          if len(self.history) == 0 or self.history[-1] == axl.Action.D:
              return axl.Action.C
  
      # Rule 6: For any situation not covered by the above rules, play D.
      return axl.Action.D

# Here's a revised, simpler cooperative strategy:  1. Start by playing C in the
# first round.  2. If the opponent played C in the previous round, play C.  3.
# If the opponent played D in the previous round, play D in the next two rounds
# as punishment.  4. After the two-round punishment, return to playing C.  5. If
# the opponent plays D for five consecutive rounds, switch to always playing D
# for the rest of the game.  6. Continue this pattern for all rounds, including
# the last round.  7. If at any point the opponent returns to cooperation (plays
# C) after a series of defections, resume the cooperative approach starting from
# step 2.

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
          self.punishment_rounds = 0  # Tracks how many punishment rounds are left
          self.defection_streak = 0   # Tracks consecutive defections by the opponent
          self.always_defect = False  # Flag to switch to always defecting
          return axl.Action.C         # Start by playing C
  
      # If we are in the "always defect" mode, continue defecting
      if self.always_defect:
          return axl.Action.D
  
      # Check if the opponent has defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.always_defect = True
          return axl.Action.D
  
      # If we are in the middle of a punishment phase, continue defecting
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # If the opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          self.defection_streak = 0  # Reset defection streak
          return axl.Action.C
  
      # If the opponent defected in the last round, start a 2-round punishment
      if opponent.history[-1] == axl.Action.D:
          self.punishment_rounds = 2
          self.defection_streak += 1
          return axl.Action.D

# Here's a revised, simpler, and more neutral strategy:  1. In the first round,
# randomly choose to cooperate or defect with equal probability.  2. For
# subsequent rounds:    a. If the opponent cooperated in the previous round,
# cooperate.    b. If the opponent defected in the previous round, defect.  3.
# If neither of the above conditions are met (i.e., it's not the first round and
# you don't know the opponent's previous move), randomly choose to cooperate or
# defect with equal probability.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: randomly choose to cooperate or defect
      if self.first_round():
          return self._random.random_choice(0.5)
      
      # Subsequent rounds: follow the opponent's last move
      if len(opponent.history) > 0:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          elif opponent.history[-1] == axl.Action.D:
              return axl.Action.D
      
      # If for some reason the opponent's last move is unknown, randomly choose
      return self._random.random_choice(0.5)

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing D (defect) in the first round.  2. If the opponent has played C for
# the last 3 consecutive rounds, play C in the current round.  3. If the
# opponent played D in the previous round, play D in the current round.  4. If
# the opponent's cooperation rate over the last 10 rounds exceeds 70%, play C in
# the current round.  5. Every 15-20 rounds (randomly chosen), play C regardless
# of the opponent's previous moves to introduce unpredictability.  6. In the
# last 10 rounds of the game, always play D.  7. In all other situations not
# covered above, play D.  8. Repeat steps 2-7 for the duration of the game.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always play D
      if self.first_round():
          return axl.Action.D
  
      # Get the current round number
      current_round = len(self.history)
  
      # Step 6: In the last 10 rounds of the game, always play D
      if current_round >= 990:
          return axl.Action.D
  
      # Step 2: If the opponent has played C for the last 3 consecutive rounds, play C
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C
  
      # Step 3: If the opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 4: If the opponent's cooperation rate over the last 10 rounds exceeds 70%, play C
      if len(opponent.history) >= 10:
          last_10_moves = opponent.history[-10:]
          cooperation_rate = last_10_moves.count(axl.Action.C) / 10
          if cooperation_rate > 0.7:
              return axl.Action.C
  
      # Step 5: Every 15-20 rounds (randomly chosen), play C regardless of the opponent's previous moves
      if current_round % self._random.randint(15, 20) == 0:
          return axl.Action.C
  
      # Step 7: In all other situations not covered above, play D
      return axl.Action.D

# Here's a revised, simpler cooperative strategy:  1. Start by playing C in the
# first round.  2. If the opponent played C in the previous round, play C.  3.
# If the opponent played D in the previous round, play D in the next round as a
# single punishment.  4. After punishing with D, return to playing C in the
# following round.  5. If the opponent plays D for five consecutive rounds,
# switch to always playing D for the next five rounds, then return to the base
# strategy.  6. Repeat this pattern for the entire game, including the final
# rounds.  This strategy is simpler, more consistently cooperative, and
# addresses the main issues from the feedback. It maintains a basic cooperative
# approach with a limited punishment mechanism and a way to handle persistent
# defection without permanent escalation.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Check if the opponent has defected for the last 5 consecutive rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          # If so, defect for the next 5 rounds
          if len(self.history) < 5 or self.history[-5:] != [axl.Action.D] * 5:
              self.defect_counter = 5  # Initialize a counter for 5 defections
          if self.defect_counter > 0:
              self.defect_counter -= 1
              return axl.Action.D
  
      # If the opponent played D in the previous round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a revised, simpler strategy:  1. Start by cooperating in the first
# round.  2. If the opponent cooperated in the previous round, cooperate in the
# current round.  3. If the opponent defected in the previous round, defect in
# the current round.  4. If your average score over the last 10 rounds falls
# below 2, defect for the next 3 rounds before returning to the main strategy.
# 5. In the last round of the game, defect.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Defect in the last round
      if len(self.history) == 999:
          return axl.Action.D
  
      # Calculate the average score over the last 10 rounds
      if len(self.history) >= 10:
          my_score, _ = self.total_scores(self.history[-10:], opponent.history[-10:])
          avg_score = my_score / 10
      else:
          avg_score = 3  # Default to a high score if less than 10 rounds have been played
  
      # If average score falls below 2, defect for the next 3 rounds
      if avg_score < 2:
          if len(self.history) >= 3 and all(move == axl.Action.D for move in self.history[-3:]):
              # Return to the main strategy after 3 defections
              pass
          else:
              return axl.Action.D
  
      # Main strategy: Tit-for-tat
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D


Aggressive_ranks = [
'Aggressive_4',
'Aggressive_12',
'Aggressive_2',
'Aggressive_20',
'Aggressive_19',
'Aggressive_23',
'Aggressive_5',
'Aggressive_9',
'Aggressive_21',
'Aggressive_1',
'Aggressive_17',
'Aggressive_24',
'Aggressive_6',
'Aggressive_16',
'Aggressive_10',
'Aggressive_3',
'Aggressive_11',
'Aggressive_15',
'Aggressive_7',
'Aggressive_13',
'Aggressive_8',
'Aggressive_18',
'Aggressive_14',
'Aggressive_25',
'Aggressive_22',
]

Cooperative_ranks = [
'Cooperative_9',
'Cooperative_16',
'Cooperative_4',
'Cooperative_17',
'Cooperative_19',
'Cooperative_15',
'Cooperative_10',
'Cooperative_25',
'Cooperative_21',
'Cooperative_11',
'Cooperative_6',
'Cooperative_14',
'Cooperative_5',
'Cooperative_20',
'Cooperative_1',
'Cooperative_23',
'Cooperative_7',
'Cooperative_2',
'Cooperative_22',
'Cooperative_3',
'Cooperative_18',
'Cooperative_24',
'Cooperative_13',
'Cooperative_12',
'Cooperative_8',
]

Neutral_ranks = [
'Neutral_10',
'Neutral_25',
'Neutral_3',
'Neutral_7',
'Neutral_9',
'Neutral_13',
'Neutral_17',
'Neutral_6',
'Neutral_5',
'Neutral_22',
'Neutral_20',
'Neutral_18',
'Neutral_21',
'Neutral_19',
'Neutral_4',
'Neutral_16',
'Neutral_14',
'Neutral_15',
'Neutral_1',
'Neutral_8',
'Neutral_24',
'Neutral_12',
'Neutral_23',
'Neutral_11',
'Neutral_2',
]
