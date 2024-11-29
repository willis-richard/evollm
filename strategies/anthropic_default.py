import axelrod as axl

from evollm.common import Attitude, auto_update_score, LLM_Strategy

# Here's a simple aggressive strategy for the given iterated normal-form game:
# 1. Start by playing D in the first round.  2. If the opponent played C in the
# previous round, play D in the current round.  3. If the opponent played D in
# the previous round, play D with 80% probability and C with 20% probability in
# the current round.  4. If you're currently on a streak of mutual cooperation
# (both players playing C) for 3 or more consecutive rounds, play D in the next
# round to exploit the opponent.  5. In the last 10 rounds of the game, always
# play D regardless of the opponent's actions.  6. For all other situations not
# covered by the above rules, play D.

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
  
      # Rule 5: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D with 80% probability, C with 20%
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.2)
  
      # Rule 4: If on a streak of mutual cooperation for 3 or more rounds, play D
      if len(self.history) >= 3 and all(
          self.history[-i] == axl.Action.C and opponent.history[-i] == axl.Action.C
          for i in range(1, 4)
      ):
          return axl.Action.D
  
      # Rule 6: For all other situations, play D
      return axl.Action.D

# Here's a simple cooperative strategy for the iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C in the current round.  3. If the opponent played D in the
# previous round, play D in the next two rounds, then return to playing C.  4.
# If the opponent plays D for three consecutive rounds, switch to playing D for
# the rest of the game.  5. In the last 5 rounds of the game, always play D
# regardless of the opponent's actions.  6. If at any point the opponent
# switches back to consistent cooperation (plays C for 3 consecutive rounds),
# resume cooperating by playing C.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Check if it's the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the last 3 rounds of opponent's history
      last_three_opponent_moves = opponent.history[-3:]
  
      # Rule 5: In the last 5 rounds, always play D
      if len(self.history) >= 995:
          return axl.Action.D
  
      # Rule 4: If opponent played D for 3 consecutive rounds, switch to D permanently
      if last_three_opponent_moves == [axl.Action.D] * 3:
          return axl.Action.D
  
      # Rule 6: If opponent plays C for 3 consecutive rounds, resume cooperation
      if last_three_opponent_moves == [axl.Action.C] * 3:
          return axl.Action.C
  
      # Rule 2: If opponent played C in the last round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent played D in the last round, play D for the next two rounds
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) >= 2 and self.history[-2:] == [axl.Action.D] * 2:
              return axl.Action.C  # After two Ds, return to C
          return axl.Action.D

# Here's a simple strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected more than
# 60% of the time in the last 10 rounds, defect.  5. If your score is
# significantly lower than your opponent's (more than 20 points behind) after
# 100 rounds, switch to always defecting for the next 50 rounds, then return to
# the main strategy.  6. In the last 10 rounds of the game, always defect.  7.
# If none of the above conditions are met, cooperate.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 990
  
      # Helper function to check if opponent defected more than 60% in the last 10 rounds
      def opponent_defected_more_than_60_percent_last_10():
          if len(opponent.history) < 10:
              return False
          return opponent.history[-10:].count(axl.Action.D) / 10 > 0.6
  
      # Helper function to check if we are more than 20 points behind after 100 rounds
      def significantly_behind_after_100():
          if len(self.history) < 100:
              return False
          return (opponent.score - self.score) > 20
  
      # Helper function to check if we are in the "always defect" phase after falling behind
      def in_always_defect_phase():
          return self.defect_phase > 0
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_phase = 0  # Tracks the number of rounds left in the "always defect" phase
          return axl.Action.C  # Start by cooperating
  
      # If in the last 10 rounds, always defect
      if in_last_10_rounds():
          return axl.Action.D
  
      # If in the "always defect" phase, defect and decrement the phase counter
      if in_always_defect_phase():
          self.defect_phase -= 1
          return axl.Action.D
  
      # If opponent defected more than 60% of the time in the last 10 rounds, defect
      if opponent_defected_more_than_60_percent_last_10():
          return axl.Action.D
  
      # If we are significantly behind after 100 rounds, switch to always defecting for 50 rounds
      if significantly_behind_after_100():
          self.defect_phase = 50
          return axl.Action.D
  
      # If opponent defected in the last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D.  4.
# If you're currently on a streak of 3 consecutive D plays and the opponent has
# played C at least twice in those 3 rounds, play C once, then return to steps 2
# and 3.  5. In the last 10 rounds of the game, always play D regardless of the
# opponent's actions.  6. Repeat steps 2-5 for the duration of the game.

class Aggressive_2(LLM_Strategy):
  n = 2
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
  
      # Step 2 and 3: If the opponent played C or D in the previous round, play D
      if opponent.history[-1] == axl.Action.C or opponent.history[-1] == axl.Action.D:
          # Step 4: Check if on a streak of 3 consecutive D plays
          if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
              # Check if the opponent has played C at least twice in those 3 rounds
              if opponent.history[-3:].count(axl.Action.C) >= 2:
                  return axl.Action.C  # Play C once
          return axl.Action.D  # Otherwise, continue playing D

# Here's a simple cooperative strategy for the given game:  1. Start by playing
# C in the first round.  2. If the opponent played C in the previous round, play
# C.  3. If the opponent played D in the previous round, play D for the next two
# rounds, then return to C.  4. If the opponent plays D for three consecutive
# rounds, switch to always playing D for the remainder of the game.  5. In the
# last 10 rounds of the game, always play D regardless of the opponent's
# actions.  6. If at any point the opponent switches back to consistent
# cooperation (playing C for 5 consecutive rounds), resume cooperating by
# playing C.

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
          self.defect_streak = 0  # Track consecutive defections by opponent
          self.punish_count = 0    # Track how many rounds to punish after opponent defects
          self.always_defect = False  # Flag to switch to always defecting
          return axl.Action.C  # Start by cooperating
  
      # If we are in the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # If opponent has cooperated for 5 consecutive rounds, reset to cooperation
      if opponent.history[-5:] == [axl.Action.C] * 5:
          self.always_defect = False
          self.punish_count = 0
          return axl.Action.C
  
      # If we are in punishment mode, continue defecting for the next two rounds
      if self.punish_count > 0:
          self.punish_count -= 1
          return axl.Action.D
  
      # If opponent defected in the last round, punish for the next two rounds
      if opponent.history[-1] == axl.Action.D:
          self.punish_count = 2
          return axl.Action.D
  
      # Track consecutive defections by opponent
      if opponent.history[-1] == axl.Action.D:
          self.defect_streak += 1
      else:
          self.defect_streak = 0
  
      # If opponent defects for 3 consecutive rounds, switch to always defecting
      if self.defect_streak >= 3:
          self.always_defect = True
  
      # If always defecting mode is active, defect
      if self.always_defect:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected more than
# 60% of the time in the last 10 rounds, defect.  5. If your overall score is
# significantly lower than your opponent's (more than 20 points behind), defect
# for the next 3 rounds, then return to the base strategy.  6. In the last 10
# rounds of the game, always defect.  7. If none of the above conditions are
# met, cooperate.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 990
  
      # Helper function to check if opponent defected more than 60% in the last 10 rounds
      def opponent_defected_more_than_60_percent_last_10():
          if len(opponent.history) < 10:
              return False
          return opponent.history[-10:].count(axl.Action.D) / 10 > 0.6
  
      # Helper function to check if our score is significantly lower than the opponent's
      def significantly_behind_in_score():
          return opponent.score - self.score > 20
  
      # Helper function to check if we should defect for the next 3 rounds
      def defect_for_next_3_rounds():
          if self.defect_count > 0:
              self.defect_count -= 1
              return True
          return False
  
      # First round: cooperate
      if self.first_round():
          self.defect_count = 0
          return axl.Action.C
  
      # If in the last 10 rounds, always defect
      if in_last_10_rounds():
          return axl.Action.D
  
      # If opponent defected more than 60% of the time in the last 10 rounds, defect
      if opponent_defected_more_than_60_percent_last_10():
          return axl.Action.D
  
      # If significantly behind in score, defect for the next 3 rounds
      if significantly_behind_in_score():
          self.defect_count = 3
          return axl.Action.D
  
      # If we are in the middle of defecting for 3 rounds, continue defecting
      if defect_for_next_3_rounds():
          return axl.Action.D
  
      # Base strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D.  4.
# If you're currently on a streak of 3 consecutive D plays and the opponent has
# played C at least twice during this streak, play C once, then return to step
# 2.  5. In the last 10 rounds of the game, always play D regardless of the
# opponent's actions.  6. Repeat steps 2-5 for the duration of the game.

class Aggressive_3(LLM_Strategy):
  n = 3
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
  
      # Step 2 and 3: If the opponent played C or D in the previous round, play D
      if opponent.history[-1] == axl.Action.C or opponent.history[-1] == axl.Action.D:
          # Step 4: Check if on a streak of 3 consecutive D plays
          if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
              # Check if opponent has played C at least twice during this streak
              if opponent.history[-3:].count(axl.Action.C) >= 2:
                  return axl.Action.C  # Play C once, then return to step 2
          return axl.Action.D

# Here's a simple cooperative strategy for the given game:  1. Start by playing
# C in the first round.  2. If the opponent played C in the previous round, play
# C.  3. If the opponent played D in the previous round, play D in the next
# round as punishment.  4. After punishing with D once, return to playing C in
# the following round.  5. If the opponent plays D for three consecutive rounds,
# switch to always playing D for the remainder of the game.  6. In the last
# round of the game, play D regardless of the opponent's previous moves.  7. If
# at any point the opponent establishes a clear pattern of alternating between C
# and D, match their pattern by playing C when they're expected to play D, and D
# when they're expected to play C.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always play C
      if self.first_round():
          return axl.Action.C
  
      # Check if the opponent has played D for the last 3 consecutive rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D  # Switch to always playing D
  
      # Last round: always play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # Check for alternating pattern in opponent's moves
      if len(opponent.history) >= 2:
          if opponent.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D:
              return axl.Action.C  # Play C when opponent is expected to play D
          if opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.D  # Play D when opponent is expected to play C
  
      # If opponent played D in the last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simple strategy for the iterated game:  1. Start by cooperating in
# the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected for three
# consecutive rounds, defect for the next two rounds regardless of their
# actions.  5. If your overall score is significantly lower than your opponent's
# (more than 10 points behind), defect for the next round.  6. If you're in the
# last 10 rounds of the game, always defect.  7. In all other situations,
# cooperate.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if opponent defected in the last 3 rounds
      def opponent_defected_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D) == n
  
      # Check if it's the first round
      if self.first_round():
          return axl.Action.C  # Cooperate in the first round
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D  # Always defect in the last 10 rounds
  
      # Check if opponent defected in the last 3 rounds
      if opponent_defected_last_n_rounds(3):
          if len(self.history) < 1000 and len(self.history) < 998:  # Ensure we don't go out of bounds
              return axl.Action.D  # Defect for the next two rounds
  
      # Check if our score is significantly lower than the opponent's
      if self.score < opponent.score - 10:
          return axl.Action.D  # Defect if more than 10 points behind
  
      # Check the opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Defect if opponent defected last round
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect in the current round.  3. If the opponent cooperated in the
# previous round, defect with a 70% probability and cooperate with a 30%
# probability.  4. Every 50 rounds, defect regardless of the opponent's previous
# move.  5. In the last 10 rounds of the game, always defect.  6. If your
# current score is significantly lower than your opponent's (more than 20 points
# behind), increase the defection probability to 90% for the next 10 rounds.  7.
# If you're ahead by more than 50 points, cooperate for the next 5 rounds to
# avoid appearing too aggressive.  8. Return to the base strategy after any
# temporary adjustments.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0  # Track rounds where defection probability is increased
          self.cooperate_streak = 0  # Track rounds where cooperation is enforced
          return axl.Action.D  # Start by defecting
  
      # Get the current round number
      current_round = len(self.history)
  
      # Rule 5: In the last 10 rounds, always defect
      if current_round >= 990:
          return axl.Action.D
  
      # Rule 6: If significantly behind, increase defection probability to 90% for 10 rounds
      if self.score < opponent.score - 20:
          self.defect_streak = 10
  
      # Rule 7: If significantly ahead, cooperate for 5 rounds
      if self.score > opponent.score + 50:
          self.cooperate_streak = 5
  
      # Handle temporary adjustments
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return self._random.random_choice(0.9)  # 90% chance to defect
      if self.cooperate_streak > 0:
          self.cooperate_streak -= 1
          return axl.Action.C  # Cooperate for 5 rounds
  
      # Rule 4: Every 50 rounds, defect regardless of opponent's move
      if current_round % 50 == 0:
          return axl.Action.D
  
      # Base strategy
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Rule 2: Defect if opponent defected last round
      else:
          # Rule 3: Defect with 70% probability, cooperate with 30% probability
          return self._random.random_choice(0.3)

# Here's a simple cooperative strategy for the iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds, then return to C.  4. If the opponent plays D for three
# consecutive rounds, switch to playing D until they play C twice in a row.  5.
# In the last 10 rounds of the game, always play D regardless of the opponent's
# actions.  6. If at any point the opponent's score is more than 20 points
# higher than yours, play D until you've closed the gap to within 10 points.  7.
# If you're behind in score with 100 or fewer rounds remaining, increase the
# frequency of D plays to every other round.  8. Reset to cooperative behavior
# (playing C) after successfully punishing defection or closing a score gap.

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
          self.defect_streak = 0
          self.punish_count = 0
          self.behind_in_score = False
          return axl.Action.C
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if opponent's score is more than 20 points higher
      if opponent.score - self.score > 20:
          self.behind_in_score = True
          return axl.Action.D
  
      # Check if we have closed the score gap to within 10 points
      if self.behind_in_score and opponent.score - self.score <= 10:
          self.behind_in_score = False
          return axl.Action.C
  
      # Check if we are behind in score with 100 or fewer rounds remaining
      if len(self.history) >= 900 and self.score < opponent.score:
          if len(self.history) % 2 == 0:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Check if opponent played D for three consecutive rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.defect_streak = 3
  
      # If opponent plays D for three consecutive rounds, defect until they play C twice in a row
      if self.defect_streak > 0:
          if opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
              self.defect_streak = 0
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If opponent played D in the previous round, defect for the next two rounds
      if opponent.history[-1] == axl.Action.D:
          if self.punish_count < 2:
              self.punish_count += 1
              return axl.Action.D
          else:
              self.punish_count = 0
              return axl.Action.C
  
      # If opponent played C in the previous round, cooperate
      return axl.Action.C

# Here's a simple strategy for the given iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. If the opponent has defected
# for three consecutive rounds, defect for the next two rounds regardless of
# their actions.  5. If your overall score is significantly lower than your
# opponent's (more than 10 points behind) after every 100 rounds, defect for the
# next 5 rounds to try to catch up.  6. In the last 10 rounds of the game,
# always defect to maximize final payoff.  7. For all other situations not
# covered by the above rules, cooperate.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 6: In the last 10 rounds of the game, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If the opponent has defected for three consecutive rounds, defect for the next two rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D] * 2:
              return axl.Action.D
  
      # Rule 5: If your overall score is significantly lower than your opponent's after every 100 rounds, defect for the next 5 rounds
      if len(self.history) % 100 == 0 and self.score < opponent.score - 10:
          if len(self.history) < 5 or self.history[-5:] != [axl.Action.D] * 5:
              return axl.Action.D
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 7: For all other situations, cooperate
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D.  4.
# If you're currently on a streak of 3 consecutive rounds where both players
# played D, play C in the next round.  5. If the opponent has played C for 5
# consecutive rounds, play C in the next round.  6. In the last 10 rounds of the
# game, always play D regardless of the opponent's actions.  7. Return to step 2
# and repeat for each round of the game.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 6: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 2 and 3: If the opponent played C or D in the previous round, play D
      if opponent.history[-1] == axl.Action.C or opponent.history[-1] == axl.Action.D:
          # Step 4: If on a streak of 3 consecutive rounds where both played D, play C
          if len(self.history) >= 3 and all(
              move == axl.Action.D for move in self.history[-3:]
          ) and all(move == axl.Action.D for move in opponent.history[-3:]):
              return axl.Action.C
  
          # Step 5: If the opponent has played C for 5 consecutive rounds, play C
          if len(opponent.history) >= 5 and all(
              move == axl.Action.C for move in opponent.history[-5:]
          ):
              return axl.Action.C
  
          # Default action is to play D
          return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D, return to playing C
# in the following round.  5. If the opponent plays D for three consecutive
# rounds, switch to always playing D for the remainder of the game.  6. In the
# last 5 rounds of the game, always play D to avoid exploitation at the end.  7.
# If at any point the opponent's score is more than 20 points higher than yours,
# play D until you've closed the gap to within 10 points.  8. Otherwise,
# continue with the cooperative approach as outlined above.

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
          return axl.Action.C
  
      # Check if we are in the last 5 rounds
      if len(self.history) >= 995:
          return axl.Action.D
  
      # Check if the opponent's score is more than 20 points higher than ours
      if opponent.score - self.score > 20:
          return axl.Action.D
  
      # Check if the opponent has played D for three consecutive rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Check the opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D
      else:
          self.consecutive_defections = 0
          return axl.Action.C

# Here's a simple strategy for the game:  1. Start by cooperating in the first
# round.  2. If the opponent cooperated in the previous round, cooperate in the
# current round.  3. If the opponent defected in the previous round, defect in
# the current round.  4. Every 10 rounds, regardless of the opponent's previous
# move, cooperate.  5. In the last 5 rounds of the game, always defect.  6. If
# your total score falls more than 20 points behind your opponent's at any
# point, defect for the next 3 rounds, then return to the main strategy.  7. If
# you've defected for 5 consecutive rounds, cooperate in the next round, then
# return to the main strategy.  Follow these rules in the order presented,
# moving to the next rule only if the conditions for the previous rules are not
# met.

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
          self.consecutive_defections = 0
          self.behind_by_20 = False
          return axl.Action.C  # Rule 1: Start by cooperating
      
      # Rule 7: If defected for 5 consecutive rounds, cooperate
      if self.consecutive_defections >= 5:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.C
      
      # Rule 6: If behind by more than 20 points, defect for 3 rounds
      if self.behind_by_20:
          if self.behind_by_20 > 0:
              self.behind_by_20 -= 1
              return axl.Action.D
          else:
              self.behind_by_20 = False  # Reset after 3 defections
      
      # Check if behind by more than 20 points
      if self.score < opponent.score - 20:
          self.behind_by_20 = 3  # Defect for the next 3 rounds
          return axl.Action.D
      
      # Rule 5: In the last 5 rounds, always defect
      if len(self.history) >= 995:
          return axl.Action.D
      
      # Rule 4: Every 10 rounds, cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
      
      # Rule 3: If opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D
      
      # Rule 2: If opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.C

# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect in the current round.  3. If the opponent cooperated in the
# previous round, defect with 80% probability and cooperate with 20%
# probability.  4. If you've cooperated for three consecutive rounds, defect in
# the next round regardless of the opponent's actions.  5. If the opponent has
# cooperated for five consecutive rounds, cooperate in the next round.  6. In
# the last 10 rounds of the game, always defect.  7. For all other situations
# not covered by the above rules, defect.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by defecting in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: In the last 10 rounds of the game, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If you've cooperated for three consecutive rounds, defect in the next round
      if len(self.history) >= 3 and all(move == axl.Action.C for move in self.history[-3:]):
          return axl.Action.D
  
      # Rule 5: If the opponent has cooperated for five consecutive rounds, cooperate in the next round
      if len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:]):
          return axl.Action.C
  
      # Rule 2: If the opponent defected in the previous round, defect in the current round
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 3: If the opponent cooperated in the previous round, defect with 80% probability, cooperate with 20%
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)
  
      # Rule 7: For all other situations not covered by the above rules, defect
      return axl.Action.D

# Here's a simple cooperative strategy for the iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D, return to playing C
# in the following round.  5. If the opponent plays D for three consecutive
# rounds, switch to always playing D for the remainder of the game.  6. In the
# last 10 rounds of the game, always play D regardless of the opponent's
# actions.  7. If at any point the opponent seems to be following a similar
# cooperative strategy (alternating between C and D based on your moves),
# continue to cooperate by following steps 2-4.

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
          self.punished_last_round = False
          self.defection_streak = 0
          return axl.Action.C
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if the opponent has defected for three consecutive rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # If the opponent played D in the last round
      if opponent.history[-1] == axl.Action.D:
          if self.punished_last_round:
              # After punishing, return to cooperation
              self.punished_last_round = False
              return axl.Action.C
          else:
              # Punish with D
              self.punished_last_round = True
              return axl.Action.D
  
      # If the opponent played C in the last round, cooperate
      self.punished_last_round = False
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. In subsequent rounds:    - If the opponent cooperated
# in the previous round, cooperate.    - If the opponent defected in the
# previous round, defect.  3. Every 10 rounds, regardless of the opponent's
# previous move:    - If your total score is higher than or equal to your
# opponent's, cooperate.    - If your total score is lower than your opponent's,
# defect.  4. In the last 5 rounds of the game, always defect.  5. If the
# opponent has defected for 3 consecutive rounds, defect for the next 2 rounds
# regardless of their actions.  6. If you and your opponent have both cooperated
# for 5 consecutive rounds, continue cooperating until they defect.  7. If your
# score falls behind your opponent's by 20 points or more, defect for the next 3
# rounds regardless of their actions.

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
          self.consecutive_defects = 0
          self.consecutive_cooperations = 0
          self.defect_for_next_n_rounds = 0
          return axl.Action.C  # Cooperate in the first round
  
      # Check if we are in the last 5 rounds of the game
      if len(self.history) >= 995:
          return axl.Action.D  # Always defect in the last 5 rounds
  
      # Check if we are supposed to defect for the next N rounds
      if self.defect_for_next_n_rounds > 0:
          self.defect_for_next_n_rounds -= 1
          return axl.Action.D
  
      # Rule 5: If opponent has defected for 3 consecutive rounds, defect for the next 2 rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.defect_for_next_n_rounds = 2
          return axl.Action.D
  
      # Rule 6: If both players have cooperated for 5 consecutive rounds, continue cooperating
      if self.history[-5:] == [axl.Action.C] * 5 and opponent.history[-5:] == [axl.Action.C] * 5:
          return axl.Action.C
  
      # Rule 7: If score difference is 20 or more in favor of the opponent, defect for 3 rounds
      if opponent.score - self.score >= 20:
          self.defect_for_next_n_rounds = 3
          return axl.Action.D
  
      # Rule 3: Every 10 rounds, compare scores and decide
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

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent cooperated (C) in the
# previous round, defect (D) in the current round.  3. If the opponent defected
# (D) in the previous round, cooperate (C) in the current round.  4. If the
# opponent has cooperated for three consecutive rounds, switch to cooperating
# (C) for one round, then return to step 2.  5. In the last 10 rounds of the
# game, always defect (D) regardless of the opponent's actions.  6. Repeat steps
# 2-5 for the duration of the game, adjusting for the final rounds as noted in
# step 5.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: If the opponent has cooperated for three consecutive rounds, cooperate for one round
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      # Step 2: If the opponent cooperated in the previous round, defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Step 3: If the opponent defected in the previous round, cooperate
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.C

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as retaliation.  4. After retaliating once, return to playing
# C.  5. If the opponent plays D for three consecutive rounds, switch to always
# playing D for the remainder of the game.  6. In the last 5 rounds of the game,
# always play D regardless of the opponent's actions.  7. If at any point the
# opponent seems to be following a similar cooperative strategy (alternating
# between C and D based on your moves), continue with the cooperative approach.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.retaliated = False  # Track if we have retaliated after a defection
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C  # Start by playing C
  
      # Check if we are in the last 5 rounds
      if len(self.history) >= 995:
          return axl.Action.D  # Always play D in the last 5 rounds
  
      # Check if the opponent has defected for 3 consecutive rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D  # Switch to always playing D
  
      # If the opponent played C in the last round, play C
      if opponent.history[-1] == axl.Action.C:
          self.retaliated = False  # Reset retaliation flag
          return axl.Action.C
  
      # If the opponent played D in the last round
      if opponent.history[-1] == axl.Action.D:
          if not self.retaliated:
              self.retaliated = True  # Retaliate once
              return axl.Action.D
          else:
              self.retaliated = False  # After retaliation, return to cooperation
              return axl.Action.C

# Here's a simple strategy for the given iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. If the opponent has defected
# for three consecutive rounds, defect for the next two rounds regardless of
# their actions.  5. If your overall score is significantly lower than your
# opponent's (more than 10 points behind), defect for the next round.  6. If
# you're in the last 10 rounds of the game, always defect.  7. In all other
# situations, cooperate.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # 1. Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # 6. If you're in the last 10 rounds of the game, always defect.
      if len(self.history) >= 990:
          return axl.Action.D
  
      # 4. If the opponent has defected for three consecutive rounds, defect for the next two rounds regardless of their actions.
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D] * 2:
              return axl.Action.D
  
      # 5. If your overall score is significantly lower than your opponent's (more than 10 points behind), defect for the next round.
      if self.score < opponent.score - 10:
          return axl.Action.D
  
      # 2. If the opponent cooperated in the previous round, cooperate in the current round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. If the opponent defected in the previous round, defect in the current round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 7. In all other situations, cooperate.
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D in the current round.  3. If the opponent played D in the
# previous round, play D with 80% probability and C with 20% probability in the
# current round.  4. If you've played D for 5 consecutive rounds, play C in the
# next round.  5. If the opponent has played C for 3 consecutive rounds, play C
# in the next round.  6. In the last 10 rounds of the game, always play D.  7.
# For any situation not covered by the above rules, play D.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: In the last 10 rounds of the game, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D with 80% probability and C with 20% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.2)
  
      # Rule 4: If you've played D for 5 consecutive rounds, play C in the next round
      if len(self.history) >= 5 and all(move == axl.Action.D for move in self.history[-5:]):
          return axl.Action.C
  
      # Rule 5: If the opponent has played C for 3 consecutive rounds, play C in the next round
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C
  
      # Rule 7: For any situation not covered by the above rules, play D
      return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D for one round, return
# to playing C.  5. If the opponent plays D for three consecutive rounds, switch
# to always playing D for the remainder of the game.  6. In the last round of
# the game, play D regardless of the opponent's previous moves.  7. If at any
# point the opponent establishes a clear pattern of alternating between C and D,
# match their pattern by playing C when they play D and D when they play C.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to detect alternating pattern
      def is_alternating_pattern():
          if len(opponent.history) < 4:
              return False
          return all(opponent.history[i] != opponent.history[i + 1] for i in range(-4, -1))
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Last round: always defect
      if len(self.history) == 999:
          return axl.Action.D
  
      # Check if opponent has defected for the last 3 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D
  
      # Check for alternating pattern
      if is_alternating_pattern():
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # If opponent defected last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D:
              return axl.Action.C  # Return to cooperation after punishment
          return axl.Action.D  # Punish with D
  
      # Otherwise, cooperate if opponent cooperated last round
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected more than
# 60% of the time in the last 10 rounds, defect.  5. If your score is
# significantly lower than your opponent's (more than 20 points behind) after
# 100 rounds, switch to always defecting for the next 50 rounds, then return to
# the main strategy.  6. In the last 10 rounds of the game, always defect.  7.
# If none of the above conditions are met, cooperate.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # 1. Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # 6. In the last 10 rounds of the game, always defect.
      if len(self.history) >= 990:
          return axl.Action.D
  
      # 5. If your score is significantly lower than your opponent's (more than 20 points behind) after 100 rounds,
      # switch to always defecting for the next 50 rounds, then return to the main strategy.
      if len(self.history) > 100:
          if self.score < opponent.score - 20:
              if 100 < len(self.history) <= 150:
                  return axl.Action.D
  
      # 4. If the opponent has defected more than 60% of the time in the last 10 rounds, defect.
      if len(opponent.history) >= 10:
          recent_defections = opponent.history[-10:].count(axl.Action.D)
          if recent_defections / 10 > 0.6:
              return axl.Action.D
  
      # 2. If the opponent cooperated in the previous round, cooperate in the current round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 3. If the opponent defected in the previous round, defect in the current round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 7. If none of the above conditions are met, cooperate.
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated normal-form game:
# 1. Start by playing D (defect) in the first round.  2. If the opponent played
# C in the previous round, play D in the current round.  3. If the opponent
# played D in the previous round, play D in the current round.  4. Every 10
# rounds, play C regardless of the opponent's previous move.  5. If the opponent
# has played C for 5 consecutive rounds, play C in the next round.  6. If your
# current score is significantly lower than your opponent's (more than 20 points
# behind), play C for the next 3 rounds.  7. In the last 10 rounds of the game,
# always play D.  8. For all other situations not covered by the above rules,
# play D.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 7: In the last 10 rounds of the game, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 6: If your current score is significantly lower than your opponent's (more than 20 points behind), play C for the next 3 rounds
      if self.score < opponent.score - 20:
          if len(self.history) < 997:  # Ensure we don't override Rule 7
              if len(self.history) >= 3 and all(move == axl.Action.C for move in self.history[-3:]):
                  return axl.Action.D  # Stop playing C after 3 rounds
              return axl.Action.C
  
      # Rule 5: If the opponent has played C for 5 consecutive rounds, play C in the next round
      if len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:]):
          return axl.Action.C
  
      # Rule 4: Every 10 rounds, play C regardless of the opponent's previous move
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 2 and 3: If the opponent played C or D in the previous round, play D in the current round
      if opponent.history[-1] == axl.Action.C or opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Default: Play D in all other situations
      return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D, return to playing C
# in the following round.  5. If the opponent plays D for three consecutive
# rounds, switch to always playing D for the remainder of the game.  6. In the
# last round of the game, play D regardless of the opponent's previous move.  7.
# If at any point the opponent establishes a clear pattern of alternating
# between C and D, match their pattern by playing D when they play C, and C when
# they play D.  8. If the game has reached round 990 or later, play D for all
# remaining rounds.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Check if it's the first round
      if self.first_round():
          return axl.Action.C
  
      # If the game is in the last round, play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # If the game is in round 990 or later, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # If the opponent has played D for the last 3 consecutive rounds, always play D
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Check for alternating pattern (C, D or D, C)
      if len(opponent.history) >= 2:
          if opponent.history[-2:] == [axl.Action.C, axl.Action.D]:
              return axl.Action.D
          elif opponent.history[-2:] == [axl.Action.D, axl.Action.C]:
              return axl.Action.C
  
      # If the opponent played D in the last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected for three
# consecutive rounds, defect for the next two rounds regardless of their
# actions.  5. If your overall score is lower than the opponent's by 10 points
# or more, defect for the next round.  6. In the last 10 rounds of the game,
# always defect.  7. For any situation not covered by the above rules,
# cooperate.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 6: In the last 10 rounds of the game, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If the opponent has defected for three consecutive rounds, defect for the next two rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D] * 2:
              return axl.Action.D
  
      # Rule 5: If your overall score is lower than the opponent's by 10 points or more, defect for the next round
      if self.score < opponent.score - 10:
          return axl.Action.D
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 7: For any situation not covered by the above rules, cooperate
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D in the current round.  3. If the opponent played D in the
# previous round, play D with 80% probability and C with 20% probability in the
# current round.  4. If you're currently on a streak of mutual cooperation (both
# players playing C) for 3 or more consecutive rounds, play D in the next round
# to exploit the opponent.  5. In the last 10 rounds of the game, always play D
# regardless of the opponent's actions.  6. For all other situations not covered
# by the above rules, play D.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 5: In the last 10 rounds of the game, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If on a streak of mutual cooperation for 3 or more rounds, play D
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.C] * 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D with 80% probability, C with 20% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.2)
  
      # Rule 6: For all other situations, play D
      return axl.Action.D

# Here's a revised strategy taking into account the feedback:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds as punishment.  4. After the two-round punishment, return
# to playing C.  5. If the opponent plays D for four out of the last six rounds,
# switch to always playing D for the next 10 rounds.  6. After 10 rounds of
# forced D, attempt to re-establish cooperation by playing C for one round. If
# the opponent responds with C, return to step 2. If they play D, continue with
# always D.  7. In the last 10 rounds of the game, play a mixed strategy: 70% D
# and 30% C to be less predictable while still protecting against exploitation.
# 8. If at any point your score falls more than 10% behind your opponent's score
# (calculated as a percentage of the total possible score so far), switch to
# always playing D for the next 20 rounds, then attempt to re-establish
# cooperation as in step 6.  9. Keep track of any patterns in your opponent's
# play (e.g., alternating C and D, or playing C twice then D). If a clear
# pattern emerges, adjust your strategy to exploit it while maintaining a
# cooperative stance when possible.  10. If the opponent has played C for the
# last 10 consecutive rounds, play C for the next 3 rounds regardless of other
# conditions to reward consistent cooperation.

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
          if self.score < 0.9 * opponent.score:
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

# Here's a simple aggressive strategy for the given iterated normal-form game:
# 1. Start by defecting (D) in the first round.  2. If the opponent defected in
# the previous round, defect in the current round.  3. If the opponent
# cooperated in the previous round, defect with an 80% probability and cooperate
# with a 20% probability.  4. Every 50 rounds, defect regardless of the
# opponent's previous move.  5. In the last 10 rounds of the game, always
# defect.  6. If your current score is significantly lower than your opponent's
# (more than 20 points behind), increase the probability of defection to 90% for
# the next 10 rounds.  7. If you're ahead by more than 50 points, cooperate for
# one round to avoid appearing too aggressive.  8. Return to step 2 and repeat
# until the game ends.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Round 1: Always defect
      if self.first_round():
          return axl.Action.D
  
      # Get the current round number
      current_round = len(self.history)
      
      # Rule 5: In the last 10 rounds, always defect
      if current_round >= 990:
          return axl.Action.D
  
      # Rule 4: Every 50 rounds, defect regardless of the opponent's previous move
      if current_round % 50 == 0:
          return axl.Action.D
  
      # Rule 6: If significantly behind, increase defection probability to 90% for the next 10 rounds
      if self.score < opponent.score - 20:
          if current_round < 990 and current_round >= 980:
              return self._random.random_choice(0.9)
      
      # Rule 7: If ahead by more than 50 points, cooperate for one round
      if self.score > opponent.score + 50:
          return axl.Action.C
  
      # Rule 2: If opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 3: If opponent cooperated in the previous round, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)

# Here's a simple cooperative strategy for the iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds, then return to C.  4. If the opponent plays D for three
# consecutive rounds, switch to always playing D for the remainder of the game.
# 5. In the last 10 rounds of the game, always play D regardless of the
# opponent's actions.  6. If at any point the opponent switches back to
# consistent cooperation (playing C for at least 5 consecutive rounds), resume
# the cooperative strategy starting from step 2.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          self.defect_streak = 0  # Track consecutive defections by opponent
          self.punish_count = 0    # Track how many rounds to punish after opponent defects
          return axl.Action.C
  
      # Step 5: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: If opponent plays D for three consecutive rounds, switch to always playing D
      if opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D
  
      # Step 6: If opponent switches back to consistent cooperation (5 consecutive C's), reset to cooperative strategy
      if opponent.history[-5:] == [axl.Action.C] * 5:
          self.defect_streak = 0
          self.punish_count = 0
  
      # Step 3: If opponent played D in the previous round, punish for 2 rounds
      if opponent.history[-1] == axl.Action.D:
          self.punish_count = 2
  
      if self.punish_count > 0:
          self.punish_count -= 1
          return axl.Action.D
  
      # Step 2: If opponent played C in the previous round, play C
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. In subsequent rounds:    - If the opponent cooperated
# in the previous round, cooperate.    - If the opponent defected in the
# previous round, defect.  3. Every 10 rounds, regardless of the opponent's
# previous move:    - If your total score is higher than or equal to the
# opponent's, cooperate.    - If your total score is lower than the opponent's,
# defect.  4. If the opponent has defected for 3 consecutive rounds, defect for
# the next 2 rounds regardless of their actions.  5. If you're in the last 10
# rounds of the game, always defect.  6. Reset to step 1 after completing step 5
# or if 50 rounds have passed since the last reset.

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
          self.reset_round = 0
          return axl.Action.C
  
      # Get the current round number
      current_round = len(self.history)
  
      # Step 5: If in the last 10 rounds of the game, always defect
      if current_round >= 990:
          return axl.Action.D
  
      # Step 4: If the opponent has defected for 3 consecutive rounds, defect for the next 2 rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.consecutive_defections = 2
  
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.D
  
      # Step 3: Every 10 rounds, check scores and decide
      if current_round % 10 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 2: Follow Tit-for-Tat logic
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D
  
      # Step 6: Reset after 50 rounds since the last reset
      if current_round - self.reset_round >= 50:
          self.reset_round = current_round

# Here's a simple aggressive strategy for the given iterated normal-form game:
# 1. Start by playing D (defect) in the first round.  2. If the opponent played
# C (cooperate) in the previous round, play D in the next round.  3. If the
# opponent played D in the previous round, play D in the next round.  4. Every
# 10 rounds, play C regardless of the opponent's previous move.  5. If the
# opponent has played C for 5 consecutive rounds, play C in the next round.  6.
# If there are less than 50 rounds remaining, always play D.  7. For all other
# situations not covered by the above rules, play D.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: If there are less than 50 rounds remaining, always play D
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Rule 5: If the opponent has played C for 5 consecutive rounds, play C in the next round
      if len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:]):
          return axl.Action.C
  
      # Rule 4: Every 10 rounds, play C regardless of the opponent's previous move
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 2 and 3: If the opponent played C or D in the previous round, play D
      if opponent.history[-1] == axl.Action.C or opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Default: Play D in all other situations
      return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, regardless of the opponent's
# previous move:    - Play C to signal willingness to cooperate.  4. If the
# opponent has played D for 3 consecutive rounds:    - Play D for the next 2
# rounds, then return to the main strategy.  5. In the last 5 rounds of the
# game:    - Always play D to protect against end-game defection.  6. If at any
# point your score falls more than 20 points behind your opponent's:    - Play D
# for the next 5 rounds, then return to the main strategy.  7. If the opponent
# seems to be following a similar cooperative strategy:    - Continue playing C
# to maintain mutual cooperation.  Follow these rules in the order presented,
# defaulting to rule 2 when no other rule applies.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 5: In the last 5 rounds, always play D
      if len(self.history) >= 995:
          return axl.Action.D
  
      # Rule 4: If the opponent has played D for 3 consecutive rounds, play D for the next 2 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D] * 2:
              return axl.Action.D
  
      # Rule 6: If your score falls more than 20 points behind, play D for the next 5 rounds
      if self.score < opponent.score - 20:
          if len(self.history) < 5 or self.history[-5:] != [axl.Action.D] * 5:
              return axl.Action.D
  
      # Rule 3: Every 10 rounds, play C to signal willingness to cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 2: If the opponent played C in the previous round, play C; if they played D, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round with a 2/3 probability. Otherwise,
# cooperate.  4. In the last 10 rounds of the game, always defect regardless of
# the opponent's actions.  5. If the opponent has defected more than 60% of the
# time in the last 50 rounds, switch to always defecting for the next 10 rounds
# before reverting to the main strategy.  6. If your score is significantly
# lower than your opponent's (more than 20 points behind) after 100 rounds,
# increase the probability of defection after opponent's defection to 3/4 for
# the next 50 rounds.  7. If you and your opponent have cooperated for 20
# consecutive rounds, cooperate for the next round regardless of other
# conditions.  Follow these rules in the order presented, applying the first
# applicable condition in each round.

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
          self._defect_until = 0
          self._defection_probability = 2 / 3
          return axl.Action.C
  
      # Rule 4: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 5: If opponent has defected more than 60% of the time in the last 50 rounds, defect for next 10 rounds
      if len(self.history) > 50:
          recent_opponent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_opponent_defections / 50 > 0.6:
              if len(self.history) < self._defect_until:
                  return axl.Action.D
              else:
                  self._defect_until = len(self.history) + 10
  
      # Rule 6: If your score is more than 20 points behind after 100 rounds, increase defection probability
      if len(self.history) > 100:
          my_score, opponent_score = self.total_scores(self.history[-100:], opponent.history[-100:])
          if opponent_score - my_score > 20:
              self._defection_probability = 0.75
          else:
              self._defection_probability = 2 / 3
  
      # Rule 7: If both players have cooperated for 20 consecutive rounds, cooperate
      if len(self.history) >= 20 and all(x == axl.Action.C for x in self.history[-20:]) and all(x == axl.Action.C for x in opponent.history[-20:]):
          return axl.Action.C
  
      # Rule 2: If opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent defected in the previous round, defect with probability 2/3 (or 3/4 if Rule 6 applies)
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(self._defection_probability)

# Here's a simple aggressive strategy for the given iterated normal-form game:
# 1. Start by defecting (D) in the first round.  2. If the opponent defected in
# the previous round, defect in the current round.  3. If the opponent
# cooperated in the previous round, defect with a 70% probability and cooperate
# with a 30% probability.  4. Every 50 rounds, defect regardless of the
# opponent's previous move.  5. In the last 100 rounds of the game, always
# defect to maximize final payoff.  6. If your total score falls behind the
# opponent's by more than 50 points at any time, switch to always defecting for
# the next 20 rounds.  7. If you're ahead by more than 100 points, cooperate for
# the next 5 rounds to avoid appearing too aggressive.  8. Return to the base
# strategy after any temporary changes in steps 6 or 7.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are in a "always defect" mode
          self.coop_streak = 0    # Track how many rounds we are in a "always cooperate" mode
          return axl.Action.D
  
      # Step 6: If behind by more than 50 points, switch to always defecting for 20 rounds
      if self.score < opponent.score - 50 and self.defect_streak == 0:
          self.defect_streak = 20
  
      # Step 7: If ahead by more than 100 points, cooperate for 5 rounds
      if self.score > opponent.score + 100 and self.coop_streak == 0:
          self.coop_streak = 5
  
      # Handle defect streak (Step 6)
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Handle coop streak (Step 7)
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Step 5: In the last 100 rounds, always defect
      if len(self.history) >= 900:
          return axl.Action.D
  
      # Step 4: Every 50 rounds, defect regardless of the opponent's previous move
      if len(self.history) % 50 == 0:
          return axl.Action.D
  
      # Step 2: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If the opponent cooperated in the previous round, defect with 70% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.3)

# Here's a simple cooperative strategy for the game:  1. Start by playing C in
# the first round.  2. If the opponent played C in the previous round, play C.
# 3. If the opponent played D in the previous round, play D for the next two
# rounds, then return to C.  4. If the opponent has played D for three
# consecutive rounds, switch to always playing D for the remainder of the game.
# 5. In the last 10 rounds of the game, always play D regardless of the
# opponent's actions.  6. If at any point the opponent switches back to
# consistent cooperation (playing C for at least 5 consecutive rounds), resume
# cooperating by playing C.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by playing C in the first round
      if self.first_round():
          self.defect_streak = 0  # Track consecutive defections by opponent
          self.punish_count = 0    # Track how many rounds to punish after a defection
          self.coop_streak = 0     # Track consecutive cooperations by opponent
          return axl.Action.C
  
      # In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Update defect streak and cooperation streak
      if opponent.history[-1] == axl.Action.D:
          self.defect_streak += 1
          self.coop_streak = 0
      else:
          self.defect_streak = 0
          self.coop_streak += 1
  
      # If the opponent has played D for three consecutive rounds, switch to always playing D
      if self.defect_streak >= 3:
          return axl.Action.D
  
      # If the opponent has cooperated for at least 5 consecutive rounds, resume cooperation
      if self.coop_streak >= 5:
          self.punish_count = 0
          return axl.Action.C
  
      # If the opponent played D in the previous round, punish by playing D for the next two rounds
      if opponent.history[-1] == axl.Action.D:
          if self.punish_count < 2:
              self.punish_count += 1
              return axl.Action.D
          else:
              self.punish_count = 0
              return axl.Action.C
  
      # If the opponent played C in the previous round, play C
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected for three
# consecutive rounds, defect for the next two rounds regardless of their
# actions.  5. If your overall score is significantly lower than your opponent's
# (more than 10 points behind), defect for the next round.  6. If you're in the
# last 10 rounds of the game, always defect.  7. In all other situations,
# cooperate.  Follow these rules in order, applying the first one that matches
# the current game state.

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
  
      # Rule 6: If you're in the last 10 rounds of the game, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If the opponent has defected for three consecutive rounds, defect for the next two rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D] * 2:
              return axl.Action.D
  
      # Rule 5: If your overall score is more than 10 points behind your opponent, defect for the next round
      if self.score < opponent.score - 10:
          return axl.Action.D
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 7: In all other situations, cooperate
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent cooperated (C) in the
# previous round, defect (D) in the current round.  3. If the opponent defected
# (D) in the previous round, cooperate (C) in the current round.  4. If the
# opponent has cooperated for three consecutive rounds, switch to defecting (D)
# for the next two rounds, then return to step 2.  5. In the last 10 rounds of
# the game, always defect (D) regardless of the opponent's actions.  6. Repeat
# steps 2-5 for the duration of the game, adjusting as necessary for the final
# rounds.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      TOTAL_ROUNDS = 1000
      FINAL_ROUNDS = 10
  
      # If it's the first round, start by defecting
      if self.first_round():
          return DEFECT
  
      # If we are in the last 10 rounds, always defect
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return DEFECT
  
      # Check if the opponent has cooperated for the last 3 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [COOPERATE, COOPERATE, COOPERATE]:
          # Defect for the next two rounds
          if len(self.history) < TOTAL_ROUNDS - FINAL_ROUNDS - 2:
              if len(self.history) % 2 == 0:
                  return DEFECT
              else:
                  return DEFECT
  
      # If the opponent cooperated in the last round, defect
      if opponent.history[-1] == COOPERATE:
          return DEFECT
  
      # If the opponent defected in the last round, cooperate
      if opponent.history[-1] == DEFECT:
          return COOPERATE

# Here's a simple cooperative strategy for the given game:  1. Start by playing
# C in the first round.  2. If the opponent played C in the previous round, play
# C.  3. If the opponent played D in the previous round, play D in the next
# round as punishment.  4. After punishing with D once, return to playing C in
# the following round.  5. If the opponent plays D for three consecutive rounds,
# switch to always playing D for the remainder of the game.  6. In the last 5
# rounds of the game, always play D to avoid exploitation at the end.  7. If at
# any point the opponent's score is more than 10 points higher than yours, play
# D until the scores are within 5 points of each other, then resume the normal
# strategy.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      TOTAL_ROUNDS = 1000
      LAST_ROUNDS = 5
      SCORE_DIFFERENCE_THRESHOLD = 10
      SCORE_RECOVERY_THRESHOLD = 5
      CONSECUTIVE_DEFECTIONS_THRESHOLD = 3
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Last 5 rounds: always defect
      if len(self.history) >= TOTAL_ROUNDS - LAST_ROUNDS:
          return axl.Action.D
  
      # Check if opponent's score is more than 10 points higher than ours
      if opponent.score - self.score > SCORE_DIFFERENCE_THRESHOLD:
          # Play D until scores are within 5 points of each other
          if opponent.score - self.score > SCORE_RECOVERY_THRESHOLD:
              return axl.Action.D
  
      # Check if opponent has defected for 3 consecutive rounds
      if len(opponent.history) >= CONSECUTIVE_DEFECTIONS_THRESHOLD and all(
          move == axl.Action.D for move in opponent.history[-CONSECUTIVE_DEFECTIONS_THRESHOLD:]
      ):
          # Switch to always defecting
          return axl.Action.D
  
      # If opponent defected in the last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simple strategy for the given iterated normal-form game:  1. Start by
# cooperating in the first round.  2. For subsequent rounds:    - If the
# opponent cooperated in the previous round, cooperate.    - If the opponent
# defected in the previous round, defect.  3. Every 10 rounds, regardless of the
# opponent's previous move:    - If your total score is higher than or equal to
# the opponent's, cooperate.    - If your total score is lower than the
# opponent's, defect.  4. In the last 5 rounds of the game, always defect.  5.
# If the opponent has defected for 3 consecutive rounds, defect for the next 2
# rounds before reverting to the main strategy.  6. If your score falls more
# than 20 points behind the opponent's at any point, defect for the next 5
# rounds before reverting to the main strategy.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      TOTAL_ROUNDS = 1000
      DEFECT_THRESHOLD = 20
      LAST_ROUNDS = 5
      CONSECUTIVE_DEFECTS = 3
      PUNISHMENT_DEFECTS = 2
      SCORE_DEFECTS = 5
  
      # First round: Cooperate
      if self.first_round():
          self.consecutive_defects = 0  # Track opponent's consecutive defections
          self.punish_rounds = 0        # Track rounds to punish after falling behind
          return COOPERATE
  
      # Track opponent's consecutive defections
      if opponent.history[-1] == DEFECT:
          self.consecutive_defects += 1
      else:
          self.consecutive_defects = 0
  
      # Punish if opponent defected for 3 consecutive rounds
      if self.consecutive_defects >= CONSECUTIVE_DEFECTS:
          self.punish_rounds = PUNISHMENT_DEFECTS
  
      # Punish if score falls behind by more than 20 points
      if self.score < opponent.score - DEFECT_THRESHOLD:
          self.punish_rounds = SCORE_DEFECTS
  
      # If in punishment mode, defect for the remaining punishment rounds
      if self.punish_rounds > 0:
          self.punish_rounds -= 1
          return DEFECT
  
      # Last 5 rounds: Always defect
      if len(self.history) >= TOTAL_ROUNDS - LAST_ROUNDS:
          return DEFECT
  
      # Every 10 rounds, check scores and decide
      if len(self.history) % 10 == 0:
          if self.score >= opponent.score:
              return COOPERATE
          else:
              return DEFECT
  
      # Main strategy: Tit-for-tat
      if opponent.history[-1] == COOPERATE:
          return COOPERATE
      else:
          return DEFECT

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D in the current round.  3. If the opponent played D in the
# previous round, play D with 80% probability and C with 20% probability in the
# current round.  4. If you've played C for three consecutive rounds and the
# opponent has responded with C each time, switch to playing D in the next
# round.  5. If the opponent has played D for five consecutive rounds, play C in
# the next round to test if they might switch to cooperation.  6. In the last 10
# rounds of the game, always play D regardless of the opponent's actions.  7.
# For any situation not covered by the above rules, play D.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: In the last 10 rounds of the game, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent played D in the previous round, play D with 80% probability, C with 20%
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.2)
  
      # Rule 4: If you've played C for three consecutive rounds and the opponent has responded with C each time, switch to D
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.C] * 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.D
  
      # Rule 5: If the opponent has played D for five consecutive rounds, play C in the next round
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.C
  
      # Default: Play D for any situation not covered by the above rules
      return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D, return to playing C
# in the following round.  5. If the opponent plays D for three consecutive
# rounds, switch to always playing D for the remainder of the game.  6. In the
# last 10 rounds of the game, always play D regardless of the opponent's
# actions.  7. If at any point the opponent switches back to consistent
# cooperation after a series of defections, resume the cooperative strategy from
# step 2.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.punished_last_round = False  # Track if we punished in the last round
          return axl.Action.C
  
      # Step 6: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 5: If the opponent plays D for three consecutive rounds, switch to always playing D
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Step 2: If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0  # Reset defection count
          self.punished_last_round = False
          return axl.Action.C
  
      # Step 3: If the opponent played D in the previous round, play D as punishment
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          if not self.punished_last_round:
              self.punished_last_round = True
              return axl.Action.D
  
      # Step 4: After punishing with D, return to playing C
      if self.punished_last_round:
          self.punished_last_round = False
          return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected for three
# consecutive rounds, defect for the next two rounds regardless of their
# actions.  5. If your overall score is lower than the opponent's by 10 points
# or more, defect for the next round.  6. If you're in the last 10 rounds of the
# game, always defect.  7. In any situation not covered by the above rules,
# cooperate.  Follow these rules in the order presented, applying the first rule
# that matches the current game state.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # Rule 6: If you're in the last 10 rounds of the game, always defect.
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If the opponent has defected for three consecutive rounds, defect for the next two rounds.
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D] * 2:
              return axl.Action.D
  
      # Rule 5: If your overall score is lower than the opponent's by 10 points or more, defect for the next round.
      if self.score < opponent.score - 10:
          return axl.Action.D
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate in the current round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect in the current round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 7: In any situation not covered by the above rules, cooperate.
      return axl.Action.C

# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent cooperated (C) in the
# previous round, defect (D) in the current round.  3. If the opponent defected
# (D) in the previous round, cooperate (C) in the current round.  4. If the
# opponent has cooperated (C) for three consecutive rounds, switch to defecting
# (D) for the next two rounds, then return to step 2.  5. In the last 10 rounds
# of the game, always defect (D) regardless of the opponent's actions.  6.
# Repeat steps 2-5 for the duration of the game, adjusting as needed based on
# the opponent's actions.

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
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: If the opponent has cooperated for three consecutive rounds, defect for the next two rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          if len(self.history) >= 2 and self.history[-2:] == [axl.Action.D, axl.Action.D]:
              return axl.Action.C  # After defecting for two rounds, return to normal strategy
          return axl.Action.D  # Defect for two rounds after three consecutive cooperations
  
      # Step 2: If the opponent cooperated in the previous round, defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Step 3: If the opponent defected in the previous round, cooperate
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.C

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, regardless of the opponent's last
# move:    - Play C to signal willingness to cooperate.  4. If the opponent has
# played D for 5 consecutive rounds:    - Play D for the next 3 rounds, then
# return to step 2.  5. If your total score falls more than 20 points behind
# your opponent's:    - Play D for the next 5 rounds, then return to step 2.  6.
# In the last 10 rounds of the game:    - Always play D to maximize final
# payoff.  7. If none of the above conditions are met:    - Continue following
# step 2.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Play C if opponent played C last round, else play D
      if len(opponent.history) > 0 and opponent.history[-1] == axl.Action.C:
          next_move = axl.Action.C
      else:
          next_move = axl.Action.D
  
      # Step 3: Every 10 rounds, play C to signal cooperation
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Step 4: If opponent has played D for 5 consecutive rounds, play D for 3 rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          if len(self.history) < len(opponent.history) + 3:
              return axl.Action.D
  
      # Step 5: If total score is more than 20 points behind, play D for 5 rounds
      if self.score < opponent.score - 20:
          if len(self.history) < len(opponent.history) + 5:
              return axl.Action.D
  
      # Step 6: In the last 10 rounds, always play D
      if self.match_attributes['length'] is not None and len(self.history) >= self.match_attributes['length'] - 10:
          return axl.Action.D
  
      # Step 7: Default to the next move determined in step 2
      return next_move

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round with a 2/3 probability. Otherwise,
# cooperate.  4. If both you and the opponent have defected for three
# consecutive rounds, cooperate in the next round to attempt breaking the cycle.
# 5. In the last 10 rounds of the game, always defect regardless of the
# opponent's actions.  6. Repeat steps 2-5 for the duration of the game,
# adjusting your actions based on the opponent's most recent move and the
# current game state.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If the opponent defected in the previous round, defect with 2/3 probability
      if opponent.history[-1] == axl.Action.D:
          if self._random.random_choice(2/3):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Step 4: If both players defected for the last 3 rounds, cooperate to break the cycle
      if len(self.history) >= 3 and all(x == axl.Action.D for x in self.history[-3:]) and all(x == axl.Action.D for x in opponent.history[-3:]):
          return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D.  4.
# If you're currently on a streak of 3 or more mutual D plays, play C once to
# test if the opponent will cooperate.  5. If the opponent responds to your test
# C with a C, immediately revert to D in the next round.  6. In the last 10
# rounds of the game, always play D regardless of the opponent's actions.  7.
# Repeat steps 2-6 for the duration of the game.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 6: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: Check if there is a streak of 3 or more mutual D plays
      if len(self.history) >= 3 and all(
          self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
          for i in range(1, 4)
      ):
          return axl.Action.C  # Test cooperation after a streak of mutual defections
  
      # Step 5: If opponent responded to the test C with a C, revert to D
      if len(self.history) >= 2 and self.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Step 2 and 3: If opponent played C or D in the previous round, play D
      return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D for one round, return
# to playing C.  5. If the opponent plays D for three consecutive rounds, switch
# to always playing D for the remainder of the game.  6. In the last round of
# the game, play D regardless of the opponent's previous move.  7. If at any
# point the opponent establishes a clear pattern of alternating between C and D,
# match their pattern by playing D when they play C, and C when they play D.  8.
# Reset the count of consecutive D plays by the opponent whenever they play C.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.alternating_pattern = False
          return axl.Action.C
  
      # Check for alternating pattern
      if len(opponent.history) >= 2:
          if opponent.history[-1] != opponent.history[-2]:
              self.alternating_pattern = True
          else:
              self.alternating_pattern = False
  
      # If alternating pattern is detected, match the opponent's pattern
      if self.alternating_pattern:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Count consecutive defections
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # If opponent defects for 3 consecutive rounds, switch to always defect
      if self.consecutive_defections >= 3:
          return axl.Action.D
  
      # Punish with D if opponent defected in the last round, then return to C
      if len(self.history) >= 1 and self.history[-1] == axl.Action.D:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # In the last round, always play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # Default to cooperation
      return axl.Action.C

# Here's a simple strategy for the given iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. Every 10 rounds, regardless
# of the opponent's previous move:    - If your total score is higher than or
# equal to the opponent's, cooperate.    - If your total score is lower than the
# opponent's, defect.  5. In the last 5 rounds of the game, always defect.  6.
# If the opponent has defected for 3 consecutive rounds, defect for the next 2
# rounds regardless of their actions.  7. If both you and the opponent have
# cooperated for 5 consecutive rounds, continue cooperating until the opponent
# defects.  8. If your cooperation rate falls below 40%, cooperate for the next
# round to balance it out.  9. If none of the above conditions are met, repeat
# steps 2 and 3.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if the opponent defected for the last 3 rounds
      def opponent_defected_last_3_rounds():
          return len(opponent.history) >= 3 and all(move == axl.Action.D for move in opponent.history[-3:])
  
      # Helper function to check if both players cooperated for the last 5 rounds
      def both_cooperated_last_5_rounds():
          return len(self.history) >= 5 and all(self.history[i] == axl.Action.C and opponent.history[i] == axl.Action.C for i in range(-5, 0))
  
      # Helper function to calculate cooperation rate
      def cooperation_rate():
          return self.history.cooperations / len(self.history)
  
      # Step 2 and 3: Tit-for-tat behavior
      if len(self.history) > 0:
          if opponent.history[-1] == axl.Action.C:
              action = axl.Action.C
          else:
              action = axl.Action.D
  
      # Step 4: Every 10 rounds, check scores
      if len(self.history) % 10 == 0:
          if self.score >= opponent.score:
              action = axl.Action.C
          else:
              action = axl.Action.D
  
      # Step 5: In the last 5 rounds, always defect
      if len(self.history) >= 995:
          action = axl.Action.D
  
      # Step 6: If opponent defected for 3 consecutive rounds, defect for the next 2 rounds
      if opponent_defected_last_3_rounds():
          if len(self.history) >= 3 and all(move == axl.Action.D for move in self.history[-2:]):
              action = axl.Action.D
          else:
              action = axl.Action.D
  
      # Step 7: If both cooperated for 5 consecutive rounds, continue cooperating
      if both_cooperated_last_5_rounds():
          action = axl.Action.C
  
      # Step 8: If cooperation rate falls below 40%, cooperate to balance it out
      if cooperation_rate() < 0.4:
          action = axl.Action.C
  
      # Return the decided action
      return action

# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect (D) in the current round.  3. If the opponent cooperated in the
# previous round, defect (D) with 80% probability and cooperate (C) with 20%
# probability in the current round.  4. Every 50 rounds, cooperate (C) once
# regardless of the opponent's previous move.  5. In the last 10 rounds of the
# game, always defect (D).  6. Repeat steps 2-5 for the duration of the game,
# adjusting for the final rounds as specified in step 5.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by defecting in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 5: In the last 10 rounds of the game, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 4: Every 50 rounds, cooperate once regardless of the opponent's previous move
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 2: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If the opponent cooperated in the previous round, defect with 80% probability, cooperate with 20% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)

# Here's a simple cooperative strategy for the iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D, return to playing C
# in the following round.  5. If the opponent plays D for three consecutive
# rounds, switch to always playing D for the rest of the game.  6. In the last
# round of the game, play D regardless of the opponent's previous move.  7. If
# at any point the opponent establishes a clear pattern of alternating between C
# and D, match their pattern by playing D when they play C, and C when they play
# D.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Check if it's the first round
      if self.first_round():
          return axl.Action.C
  
      # Check if it's the last round (assuming 1000 rounds)
      if len(self.history) == 999:
          return axl.Action.D
  
      # Check if opponent has played D for the last 3 consecutive rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Check if opponent is alternating between C and D
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.D]:
          return axl.Action.D
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.C]:
          return axl.Action.C
  
      # If opponent played D in the last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. Every 10 rounds, regardless of the
# opponent's previous move:    - If your total score is higher than or equal to
# the opponent's, cooperate.    - If your total score is lower than the
# opponent's, defect.  5. In the last 10 rounds of the game (rounds 991-1000),
# always defect.  6. If the opponent has defected more than 75% of the time in
# the last 50 rounds, switch to always defecting for the next 20 rounds before
# reverting to the main strategy.  7. If you and your opponent have been stuck
# in a mutual defection pattern for more than 10 consecutive rounds, attempt to
# break it by cooperating for one round.  Follow these rules in the order
# presented, applying the first applicable rule in each round.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          self.defect_streak = 0
          return axl.Action.C
  
      # Rule 5: In the last 10 rounds (991-1000), always defect
      if len(self.history) >= 991:
          return axl.Action.D
  
      # Rule 6: If opponent has defected more than 75% of the time in the last 50 rounds, defect for 20 rounds
      if len(self.history) >= 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections > 0.75 * 50:
              if self.defect_streak == 0:
                  self.defect_streak = 20  # Start defecting for 20 rounds
              if self.defect_streak > 0:
                  self.defect_streak -= 1
                  return axl.Action.D
          else:
              self.defect_streak = 0  # Reset defect streak if condition no longer holds
  
      # Rule 7: If stuck in mutual defection for more than 10 rounds, cooperate to break the pattern
      if len(self.history) >= 10 and all(x == axl.Action.D for x in self.history[-10:]) and all(x == axl.Action.D for x in opponent.history[-10:]):
          return axl.Action.C
  
      # Rule 4: Every 10 rounds, compare scores and decide
      if len(self.history) % 10 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 2: If opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D.  4.
# Every 10 rounds, play C regardless of the opponent's previous move.  5. If the
# opponent has played C for the last 5 consecutive rounds, play C once, then
# return to the main strategy.  6. In the last 10 rounds of the game, always
# play D.  7. Repeat steps 2-6 for the duration of the game.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 6: In the last 10 rounds of the game, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 5: If the opponent has played C for the last 5 consecutive rounds, play C once
      if len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:]):
          return axl.Action.C
  
      # Step 4: Every 10 rounds, play C regardless of the opponent's previous move
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Step 2 and 3: If the opponent played C or D in the previous round, play D
      if opponent.history[-1] == axl.Action.C or opponent.history[-1] == axl.Action.D:
          return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D once, return to
# playing C in the following round.  5. If the opponent plays D for three
# consecutive rounds, switch to always playing D for the remainder of the game.
# 6. In the last 5 rounds of the game, always play D regardless of the
# opponent's actions.  7. If at any point the opponent's score is more than 20
# points higher than yours, play D until you've closed the gap to within 10
# points, then resume the normal strategy.

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
          self.punished = False  # Track if we have punished the opponent
          self.defect_streak = 0  # Track consecutive defections by the opponent
          self.always_defect = False  # Track if we are in always defect mode
          return axl.Action.C
  
      # If we are in always defect mode, always play D
      if self.always_defect:
          return axl.Action.D
  
      # If we are in the last 5 rounds, always play D
      if len(self.history) >= 995:
          return axl.Action.D
  
      # If the opponent has defected for 3 consecutive rounds, switch to always defect
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.always_defect = True
          return axl.Action.D
  
      # If the opponent's score is more than 20 points higher than ours, play D until the gap is within 10 points
      if opponent.score - self.score > 20:
          if opponent.score - self.score > 10:
              return axl.Action.D
  
      # If the opponent played D in the last round, punish with D this round
      if opponent.history[-1] == axl.Action.D:
          if not self.punished:
              self.punished = True
              return axl.Action.D
          else:
              self.punished = False  # Reset punishment flag after one round
              return axl.Action.C
  
      # If the opponent played C in the last round, play C
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round with a 2/3 probability. Otherwise,
# cooperate.  4. In the last 10 rounds of the game, always defect regardless of
# the opponent's actions.  5. If the opponent has defected more than 60% of the
# time in the last 50 rounds, switch to always defecting for the next 10 rounds
# before reverting to the main strategy.  6. If your average score over the last
# 100 rounds falls below 2, increase the probability of defection after the
# opponent's defection to 3/4 for the next 50 rounds.  7. If you're trailing
# behind the opponent's total score by more than 50 points at any point after
# round 200, switch to always defecting for the next 20 rounds before reverting
# to the main strategy.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      total_rounds = 1000
      last_rounds_defect = 10
      defect_threshold = 0.6
      score_threshold = 2
      score_diff_threshold = 50
      rounds_to_always_defect = 10
      rounds_to_always_defect_trailing = 20
      prob_defect_after_defection = 2 / 3
      prob_defect_after_defection_increased = 3 / 4
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0  # Track rounds of always defecting
          self.increased_defection_rounds = 0  # Track rounds of increased defection probability
          return axl.Action.C  # Cooperate in the first round
  
      # Get the current round number
      current_round = len(self.history)
  
      # Always defect in the last 10 rounds
      if total_rounds - current_round <= last_rounds_defect:
          return axl.Action.D
  
      # Check if we are in a defect streak (due to opponent defecting > 60% in last 50 rounds)
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Check if we are in a period of increased defection probability
      if self.increased_defection_rounds > 0:
          self.increased_defection_rounds -= 1
          prob_defect_after_defection = prob_defect_after_defection_increased
  
      # Check if opponent defected more than 60% in the last 50 rounds
      if current_round >= 50:
          recent_opponent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_opponent_defections / 50 > defect_threshold:
              self.defect_streak = rounds_to_always_defect
              return axl.Action.D
  
      # Check if our average score over the last 100 rounds is below 2
      if current_round >= 100:
          my_score, _ = self.total_scores(self.history[-100:], opponent.history[-100:])
          if my_score / 100 < score_threshold:
              self.increased_defection_rounds = 50
  
      # Check if we are trailing by more than 50 points after round 200
      if current_round > 200:
          my_total_score = self.score
          opponent_total_score = opponent.score
          if opponent_total_score - my_total_score > score_diff_threshold:
              self.defect_streak = rounds_to_always_defect_trailing
              return axl.Action.D
  
      # Main strategy: tit-for-tat with probabilistic defection after opponent defects
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(prob_defect_after_defection)
      else:
          return axl.Action.C

# Here's a simple aggressive strategy for the iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent cooperated (C) in the
# previous round, defect (D) in the current round.  3. If the opponent defected
# (D) in the previous round, cooperate (C) in the current round.  4. If the
# opponent has defected (D) for three consecutive rounds, switch to always
# defecting (D) for the next five rounds, regardless of the opponent's moves.
# 5. After those five rounds of constant defection, return to the basic strategy
# outlined in steps 2 and 3.  6. In the last 10 rounds of the game, always
# defect (D) regardless of the opponent's moves.  7. Repeat these steps
# throughout the 1000 rounds, adjusting as necessary based on the opponent's
# actions.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_mode = 0
          return axl.Action.D  # Start by defecting
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D  # Always defect in the last 10 rounds
  
      # If in defect mode, continue defecting for the next 5 rounds
      if self.defect_mode > 0:
          self.defect_mode -= 1
          return axl.Action.D
  
      # Basic strategy: defect if opponent cooperated last round, cooperate if opponent defected
      if opponent.history[-1] == axl.Action.C:
          action = axl.Action.D
      else:
          action = axl.Action.C
  
      # Track consecutive defections by the opponent
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # If opponent has defected for 3 consecutive rounds, enter defect mode for 5 rounds
      if self.consecutive_defections >= 3:
          self.defect_mode = 5
          return axl.Action.D
  
      return action

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C in the current round.  3. If the opponent played D in the
# previous round, play D in the current round and the next round.  4. After
# playing D for two rounds following an opponent's defection, return to playing
# C.  5. If the opponent defects three times in a row, switch to always playing
# D for the remainder of the game.  6. In the last 5 rounds of the game, always
# play D regardless of the opponent's actions.  7. If at any point the
# opponent's score is more than 20 points higher than yours, play D until you've
# closed the gap to within 10 points.  8. If you're behind in score with less
# than 100 rounds remaining, increase your frequency of playing D to every other
# round.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Subfunction to check if we are in the last 5 rounds
      def in_last_5_rounds():
          return len(self.history) >= 995
  
      # Subfunction to check if opponent defected 3 times in a row
      def opponent_defected_three_in_a_row():
          return len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3
  
      # Subfunction to check if we are behind by more than 20 points
      def opponent_ahead_by_20():
          return opponent.score - self.score > 20
  
      # Subfunction to check if we are behind with less than 100 rounds remaining
      def behind_with_less_than_100_rounds():
          return len(self.history) >= 900 and self.score < opponent.score
  
      # First round: always cooperate
      if self.first_round():
          self.defect_streak = 0  # Track how many times we've defected in a row
          self.permanent_defection = False  # Track if we are in permanent defection mode
          return axl.Action.C
  
      # If in permanent defection mode, always defect
      if self.permanent_defection:
          return axl.Action.D
  
      # If in the last 5 rounds, always defect
      if in_last_5_rounds():
          return axl.Action.D
  
      # If opponent defected 3 times in a row, switch to permanent defection
      if opponent_defected_three_in_a_row():
          self.permanent_defection = True
          return axl.Action.D
  
      # If opponent is ahead by more than 20 points, defect until the gap is closed
      if opponent_ahead_by_20():
          if opponent.score - self.score <= 10:
              return axl.Action.C
          return axl.Action.D
  
      # If behind with less than 100 rounds remaining, defect every other round
      if behind_with_less_than_100_rounds():
          if len(self.history) % 2 == 0:
              return axl.Action.D
          return axl.Action.C
  
      # If opponent defected in the last round, defect for two rounds
      if opponent.history[-1] == axl.Action.D:
          if self.defect_streak < 2:
              self.defect_streak += 1
              return axl.Action.D
          else:
              self.defect_streak = 0  # Reset defect streak after two defections
              return axl.Action.C
  
      # If opponent cooperated in the last round, cooperate
      return axl.Action.C

# Here's a simple strategy for the given iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. If the opponent has defected
# for three consecutive rounds, defect for the next two rounds regardless of
# their actions.  5. If your overall score is lower than the opponent's by 10
# points or more, defect for the next round.  6. If there are fewer than 10
# rounds left in the game, always defect.  7. In any situation not covered by
# the above rules, cooperate.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 6: If there are fewer than 10 rounds left in the game, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If the opponent has defected for three consecutive rounds, defect for the next two rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D] * 2:
              return axl.Action.D
  
      # Rule 5: If your overall score is lower than the opponent's by 10 points or more, defect for the next round
      if self.score < opponent.score - 10:
          return axl.Action.D
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 7: In any situation not covered by the above rules, cooperate
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect in the current round.  3. If the opponent cooperated in the
# previous round, defect with an 80% probability and cooperate with a 20%
# probability.  4. Every 50 rounds, cooperate once regardless of the opponent's
# previous move.  5. In the last 10 rounds of the game, always defect.  6. If
# your current score is significantly lower than your opponent's (more than 20
# points behind), switch to always defecting for the next 10 rounds.  7. If
# you're ahead by more than 50 points, cooperate for one round to potentially
# increase both scores.  8. Return to the base strategy after any temporary
# changes in steps 6 or 7.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # First round: always defect
      if self.first_round():
          self.defect_for_next = 0
          self.cooperated_once = False
          return axl.Action.D
  
      # Get the current round number
      current_round = len(self.history)
      
      # Step 5: In the last 10 rounds, always defect
      if current_round >= 990:
          return axl.Action.D
  
      # Step 6: If significantly behind, switch to always defecting for 10 rounds
      if self.defect_for_next > 0:
          self.defect_for_next -= 1
          return axl.Action.D

      if self.score < opponent.score - 20:
          self.defect_for_next = 10
  
      # Step 7: If ahead by more than 50 points, cooperate for one round
      if self.score > opponent.score + 50:
          if not self.cooperated_once:
              self.cooperated_once = True
              return axl.Action.C
  
      # Step 4: Every 50 rounds, cooperate once
      if current_round % 50 == 0:
          return axl.Action.C
  
      # Step 2: If opponent defected in the previous round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If opponent cooperated in the previous round, defect with 80% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)
  
      # Default to defecting
      return axl.Action.D

# Here's a simple cooperative strategy for the iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D for
# the next two rounds, then return to C.  4. If the opponent plays D for three
# consecutive rounds, switch to always playing D for the remainder of the game.
# 5. In the last 10 rounds of the game, always play D regardless of the
# opponent's actions.  6. If at any point the opponent switches back to
# consistent cooperation (plays C for 5 consecutive rounds), resume the
# cooperative strategy from step 2.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          self.defect_streak = 0  # Track consecutive defections by opponent
          self.punish_count = 0    # Track how many rounds to punish after a defection
          self.coop_streak = 0     # Track consecutive cooperations by opponent
          return axl.Action.C
  
      # Step 5: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Track opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Step 6: If opponent cooperates for 5 consecutive rounds, reset to cooperative strategy
      if last_opponent_move == axl.Action.C:
          self.coop_streak += 1
      else:
          self.coop_streak = 0
  
      if self.coop_streak >= 5:
          self.defect_streak = 0
          self.punish_count = 0
  
      # Step 4: If opponent defects for 3 consecutive rounds, switch to always defect
      if opponent.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.D
  
      # Step 3: If opponent played D in the previous round, punish for 2 rounds
      if last_opponent_move == axl.Action.D:
          self.defect_streak += 1
          if self.punish_count > 0:
              self.punish_count -= 1
              return axl.Action.D
          else:
              self.punish_count = 2
              return axl.Action.D
      else:
          self.defect_streak = 0
  
      # Step 2: If opponent played C in the previous round, play C
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. Every 10 rounds, regardless of the
# opponent's previous move:    - If your total score is higher than or equal to
# the opponent's, cooperate.    - If your total score is lower than the
# opponent's, defect.  5. In the last 10 rounds of the game (rounds 991-1000),
# always defect.  6. If at any point your score falls behind the opponent's by
# 20 points or more, defect for the next 5 rounds, then return to the main
# strategy.  7. If you and your opponent have been in a cycle of mutual
# defection for more than 5 consecutive rounds, attempt to break the cycle by
# cooperating once.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 991
  
      # Helper function to check if we are in a mutual defection cycle
      def in_mutual_defection_cycle():
          return len(self.history) >= 5 and all(
              self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
              for i in range(1, 6)
          )
  
      # Helper function to check if we are behind by 20 points or more
      def behind_by_20_points():
          return opponent.score - self.score >= 20
  
      # First round: cooperate
      if self.first_round():
          self.defect_streak = 0  # Track how many rounds we are defecting due to falling behind
          return axl.Action.C
  
      # Last 10 rounds: always defect
      if in_last_10_rounds():
          return axl.Action.D
  
      # If we are in a defect streak due to falling behind by 20 points
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Every 10 rounds, check scores and decide
      if len(self.history) % 10 == 0:
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If we are behind by 20 points or more, defect for the next 5 rounds
      if behind_by_20_points():
          self.defect_streak = 5
          return axl.Action.D
  
      # If we are in a mutual defection cycle, try to break it by cooperating
      if in_mutual_defection_cycle():
          return axl.Action.C
  
      # Main strategy: Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D.  4.
# If you're currently on a streak of 3 consecutive rounds where both players
# played D, play C in the next round.  5. If the opponent has played C for 5
# consecutive rounds, play C in the next round.  6. In the last 10 rounds of the
# game, always play D regardless of the opponent's actions.  7. Return to step 2
# and repeat for each round of the game.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 6: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 2 and 3: If opponent played C or D in the previous round, play D
      if opponent.history[-1] == axl.Action.C or opponent.history[-1] == axl.Action.D:
          # Step 4: If on a streak of 3 consecutive rounds where both played D, play C
          if len(self.history) >= 3 and all(
              move == axl.Action.D for move in self.history[-3:]
          ) and all(move == axl.Action.D for move in opponent.history[-3:]):
              return axl.Action.C
  
          # Step 5: If opponent has played C for 5 consecutive rounds, play C
          if len(opponent.history) >= 5 and all(
              move == axl.Action.C for move in opponent.history[-5:]
          ):
              return axl.Action.C
  
          # Default action is D
          return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D, return to playing C
# in the following round.  5. If the opponent plays D twice in a row, switch to
# always playing D for the rest of the game.  6. In the last 5 rounds of the
# game, always play D regardless of the opponent's actions.  7. If at any point
# the opponent has defected more than 60% of the time in the last 50 rounds,
# switch to always playing D for the rest of the game.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, play C
      if self.first_round():
          return axl.Action.C
  
      # Get the number of rounds played so far
      rounds_played = len(self.history)
  
      # In the last 5 rounds, always play D
      if rounds_played >= 995:
          return axl.Action.D
  
      # If the opponent has defected more than 60% of the time in the last 50 rounds, switch to always playing D
      if rounds_played >= 50:
          recent_defections = opponent.history[-50:].count(axl.Action.D)
          if recent_defections / 50 > 0.6:
              return axl.Action.D
  
      # If the opponent has defected twice in a row, switch to always playing D
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # If the opponent defected in the last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected for three
# consecutive rounds, defect for the next two rounds regardless of their
# actions.  5. If your overall score is significantly lower than the opponent's
# (more than 10 points difference), defect for the next round.  6. Every 50
# rounds, cooperate regardless of the opponent's previous action.  7. In the
# last 10 rounds of the game, always defect.  8. If none of the above conditions
# apply, cooperate.  Follow these rules in the order presented for each round of
# the game.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # 7. In the last 10 rounds of the game, always defect.
      if len(self.history) >= 990:
          return axl.Action.D
  
      # 6. Every 50 rounds, cooperate regardless of the opponent's previous action.
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # 5. If your overall score is significantly lower than the opponent's (more than 10 points difference), defect for the next round.
      if self.score < opponent.score - 10:
          return axl.Action.D
  
      # 4. If the opponent has defected for three consecutive rounds, defect for the next two rounds regardless of their actions.
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D, axl.Action.D]:
              return axl.Action.D
  
      # 3. If the opponent defected in the previous round, defect in the current round.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 2. If the opponent cooperated in the previous round, cooperate in the current round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # 8. If none of the above conditions apply, cooperate.
      return axl.Action.C

# Here's a simple aggressive strategy for the iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D.  4.
# If you're currently on a streak of mutual defection (D,D) for 5 consecutive
# rounds, play C once to test if the opponent will cooperate.  5. If the
# opponent responds to your test cooperation with C, play D in the next round to
# exploit their cooperation.  6. If you're behind in total score by 10 points or
# more, always play D until you're no longer behind.  7. In the last 10 rounds
# of the game, always play D regardless of the opponent's actions.  8. Repeat
# steps 2-7 for the duration of the game, unless specified otherwise.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 7: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 6: If behind by 10 points or more, always play D
      if self.score < opponent.score - 10:
          return axl.Action.D
  
      # Step 4: If on a streak of mutual defection for 5 rounds, play C once
      if len(self.history) >= 5 and all(
          self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
          for i in range(1, 6)
      ):
          return axl.Action.C
  
      # Step 5: If opponent responded to test cooperation with C, play D to exploit
      if len(self.history) > 1 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Step 2 and 3: If opponent played C or D in the previous round, play D
      return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D, return to playing C
# in the following round.  5. If the opponent plays D for three consecutive
# rounds, switch to always playing D for the remainder of the game.  6. In the
# last 5 rounds of the game, always play D to protect against end-game
# defection.  7. If at any point the opponent's score is more than 20 points
# higher than yours, play D until you've closed the gap to within 10 points.  8.
# Reset the strategy and return to step 1 if the opponent plays C for 5
# consecutive rounds after any period of defection.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punished_last_round = False
          self.defection_streak = 0
          self.cooperation_streak = 0
          return axl.Action.C
  
      # Check if we are in the last 5 rounds
      if len(self.history) >= 995:
          return axl.Action.D
  
      # Check if the opponent's score is more than 20 points higher than ours
      if opponent.score - self.score > 20:
          return axl.Action.D
  
      # Check if the opponent has played D for 3 consecutive rounds
      if opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D
  
      # Check if the opponent has played C for 5 consecutive rounds after defection
      if opponent.history[-5:] == [axl.Action.C] * 5:
          self.defection_streak = 0
          self.cooperation_streak = 0
          return axl.Action.C
  
      # If we punished last round, return to cooperation
      if self.punished_last_round:
          self.punished_last_round = False
          return axl.Action.C
  
      # If the opponent played D last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          self.punished_last_round = True
          return axl.Action.D
  
      # Otherwise, cooperate if the opponent cooperated last round
      return axl.Action.C

# Here's a simple strategy for the given iterated normal-form game:  1. Start by
# cooperating in the first round.  2. If the opponent cooperated in the previous
# round, cooperate in the current round.  3. If the opponent defected in the
# previous round, defect in the current round.  4. Every 10 rounds, regardless
# of the opponent's previous move, cooperate.  5. In the last 5 rounds of the
# game, always defect.  6. If your total score is significantly lower than what
# you'd expect from mutual cooperation (less than 2.5 points per round on
# average), switch to always defecting for the remainder of the game.  7. If at
# any point the opponent has defected more than 60% of the time in the last 50
# moves, switch to always defecting for the next 50 moves, then return to the
# main strategy.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Subfunction to check if the opponent has defected more than 60% in the last 50 rounds
      def opponent_defected_more_than_60_percent():
          recent_history = opponent.history[-50:]
          if len(recent_history) < 50:
              return False
          return recent_history.count(axl.Action.D) / 50 > 0.6
  
      # Subfunction to check if the average score is less than 2.5 points per round
      def average_score_too_low():
          if len(self.history) == 0:
              return False
          total_rounds = len(self.history)
          expected_score = 2.5 * total_rounds
          return self.score < expected_score
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Last 5 rounds: always defect
      if len(self.history) >= 995:
          return axl.Action.D
  
      # Every 10 rounds: cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # If the opponent defected more than 60% of the time in the last 50 moves, defect for 50 moves
      if opponent_defected_more_than_60_percent():
          if len(self.history) < 50 or self.history[-50:].count(axl.Action.D) < 50:
              return axl.Action.D
  
      # If the average score is too low, switch to always defecting
      if average_score_too_low():
          return axl.Action.D
  
      # If the opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the last round, defect
      return axl.Action.D

# Here's a simple aggressive strategy for the iterated game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play D.  3. If the opponent played D in the previous round, play D.  4.
# Every 10 rounds, play C regardless of the opponent's previous move.  5. If the
# opponent has played C for 5 consecutive rounds, play C once, then return to
# the main strategy.  6. In the last 10 rounds of the game, always play D.  7.
# Repeat steps 2-6 for the duration of the game.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 6: In the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 5: If the opponent has played C for 5 consecutive rounds, play C once
      if len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:]):
          if len(self.history) == 0 or self.history[-1] != axl.Action.C:
              return axl.Action.C
  
      # Step 4: Every 10 rounds, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Step 2 and 3: If the opponent played C or D in the previous round, play D
      return axl.Action.D

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D once, return to
# playing C in the following round.  5. If the opponent plays D for three
# consecutive rounds, switch to always playing D for the remainder of the game.
# 6. In the last round of the game (round 1000), play D regardless of the
# opponent's previous move.  7. If at any point the opponent establishes a clear
# pattern of alternating between C and D, match their pattern by playing C when
# they play D and D when they play C.  8. Reset the count of consecutive D plays
# by the opponent to zero whenever they play C.

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
          self.consecutive_defections = 0
          self.alternating_pattern = False
          return axl.Action.C
  
      # Check for alternating pattern
      if len(opponent.history) >= 2:
          if opponent.history[-1] != opponent.history[-2]:
              self.alternating_pattern = True
          else:
              self.alternating_pattern = False
  
      # If alternating pattern is detected, match the opponent's pattern
      if self.alternating_pattern:
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Count consecutive defections
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # If opponent defects for 3 consecutive rounds, switch to always defect
      if self.consecutive_defections >= 3:
          return axl.Action.D
  
      # Play D in the last round (round 1000)
      if len(self.history) == 999:
          return axl.Action.D
  
      # Punish with D if opponent defected in the last round, then return to C
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and self.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simple strategy for the given iterated game:  1. Start by cooperating
# in the first round.  2. If the opponent cooperated in the previous round,
# cooperate in the current round.  3. If the opponent defected in the previous
# round, defect in the current round.  4. If the opponent has defected for three
# consecutive rounds, defect for the next two rounds regardless of their
# actions.  5. If your overall score is significantly lower than your opponent's
# (more than 10 points behind), defect for the next round.  6. If there have
# been 10 consecutive rounds of mutual cooperation, defect once to test the
# opponent's response.  7. In the last 5 rounds of the game, always defect.  8.
# For all other situations not covered by the above rules, cooperate.  Follow
# these rules in the order presented, applying the first rule that matches the
# current game state.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by cooperating in the first round.
      if self.first_round():
          return axl.Action.C
  
      # Rule 2: If the opponent cooperated in the previous round, cooperate.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If the opponent defected in the previous round, defect.
      if opponent.history[-1] == axl.Action.D:
          # Rule 4: If the opponent has defected for three consecutive rounds, defect for the next two rounds.
          if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
              if len(self.history) < 2 or self.history[-2:] != [axl.Action.D, axl.Action.D]:
                  return axl.Action.D
  
          # Rule 5: If your score is significantly lower than your opponent's (more than 10 points behind), defect.
          if self.score < opponent.score - 10:
              return axl.Action.D
  
          return axl.Action.D
  
      # Rule 6: If there have been 10 consecutive rounds of mutual cooperation, defect once.
      if len(self.history) >= 10 and self.history[-10:] == [axl.Action.C] * 10 and opponent.history[-10:] == [axl.Action.C] * 10:
          return axl.Action.D
  
      # Rule 7: In the last 5 rounds of the game, always defect.
      if len(self.history) >= 995:
          return axl.Action.D
  
      # Rule 8: For all other situations, cooperate.
      return axl.Action.C

# Here's a simple aggressive strategy for the given iterated game:  1. Start by
# defecting (D) in the first round.  2. If the opponent defected in the previous
# round, defect in the current round.  3. If the opponent cooperated in the
# previous round, defect with an 80% probability and cooperate with a 20%
# probability.  4. Every 50 rounds, defect regardless of the opponent's previous
# move.  5. In the last 10 rounds of the game, always defect.  6. If your
# current score is significantly lower than your opponent's (more than 20 points
# behind), switch to always defecting for the next 10 rounds.  7. If you're
# ahead by more than 50 points, cooperate for one round to potentially increase
# both scores.  8. Return to step 2 and repeat until the game ends.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Step 1: Start by defecting in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 4: Every 50 rounds, defect regardless of the opponent's previous move
      if len(self.history) % 50 == 0:
          return axl.Action.D
  
      # Step 5: In the last 10 rounds of the game, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Step 6: If your current score is significantly lower than your opponent's (more than 20 points behind), 
      # switch to always defecting for the next 10 rounds
      if self.score < opponent.score - 20:
          if len(self.history) >= 10 and all(move == axl.Action.D for move in self.history[-10:]):
              pass  # Continue normal strategy after 10 rounds of defecting
          else:
              return axl.Action.D
  
      # Step 7: If you're ahead by more than 50 points, cooperate for one round
      if self.score > opponent.score + 50:
          return axl.Action.C
  
      # Step 2: If the opponent defected in the previous round, defect in the current round
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: If the opponent cooperated in the previous round, defect with 80% probability and cooperate with 20% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.2)

# Here's a simple cooperative strategy for the given iterated game:  1. Start by
# playing C in the first round.  2. If the opponent played C in the previous
# round, play C.  3. If the opponent played D in the previous round, play D in
# the next round as punishment.  4. After punishing with D, return to playing C
# in the following round.  5. If the opponent plays D for three consecutive
# rounds, switch to always playing D for the remainder of the game.  6. In the
# last 10 rounds of the game, always play D to protect against end-game
# defection.  7. If at any point the opponent's score is more than 20 points
# higher than yours, play D until you've closed the gap to within 10 points.  8.
# If you're behind in score with less than 100 rounds remaining, increase the
# frequency of D plays to every other round until you've caught up or the game
# ends.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      TOTAL_ROUNDS = 1000
      LAST_10_ROUNDS = 10
      DEFECT_THRESHOLD = 3
      SCORE_GAP_THRESHOLD = 20
      CATCH_UP_GAP = 10
      CATCH_UP_ROUNDS = 100
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Last 10 rounds: always defect
      if len(self.history) >= TOTAL_ROUNDS - LAST_10_ROUNDS:
          return axl.Action.D
  
      # Check if opponent has defected for 3 consecutive rounds
      if len(opponent.history) >= DEFECT_THRESHOLD and all(
          move == axl.Action.D for move in opponent.history[-DEFECT_THRESHOLD:]
      ):
          return axl.Action.D
  
      # Check if opponent's score is more than 20 points higher than ours
      if opponent.score - self.score > SCORE_GAP_THRESHOLD:
          return axl.Action.D
  
      # If less than 100 rounds remaining and behind in score, defect every other round
      if len(self.history) >= TOTAL_ROUNDS - CATCH_UP_ROUNDS and self.score < opponent.score:
          if len(self.history) % 2 == 1:
              return axl.Action.D
  
      # If opponent defected last round, punish with D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# Here's a simple strategy for the game:  1. Start by cooperating in the first
# round.  2. If the opponent cooperated in the previous round, cooperate in the
# current round.  3. If the opponent defected in the previous round, defect in
# the current round.  4. Every 10 rounds, regardless of the opponent's previous
# move, cooperate.  5. In the last 5 rounds of the game, always defect.  6. If
# your total score falls more than 20 points behind your opponent's at any
# point, defect for the next 3 rounds before returning to the main strategy.  7.
# If you've defected for 5 consecutive rounds, cooperate in the next round
# regardless of the opponent's previous move.  8. Continue this pattern until
# the end of the game, adjusting based on the opponent's moves and the specific
# conditions mentioned above.

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
          self.consecutive_defections = 0  # Track consecutive defections
          self.defect_for_next_n_rounds = 0  # Track forced defections due to score difference
          return axl.Action.C
  
      # Check if we are in the last 5 rounds of the game
      if len(self.history) >= 995:
          return axl.Action.D
  
      # Check if we are more than 20 points behind the opponent
      if self.score < opponent.score - 20 and self.defect_for_next_n_rounds == 0:
          self.defect_for_next_n_rounds = 3
  
      # If we are in the forced defection period due to score difference
      if self.defect_for_next_n_rounds > 0:
          self.defect_for_next_n_rounds -= 1
          self.consecutive_defections += 1
          return axl.Action.D
  
      # If we have defected for 5 consecutive rounds, cooperate
      if self.consecutive_defections >= 5:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Every 10 rounds, cooperate regardless of the opponent's move
      if len(self.history) % 10 == 0:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Main strategy: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0
          return axl.Action.C
      else:
          self.consecutive_defections += 1
          return axl.Action.D


Aggressive_ranks = [
'Aggressive_20',
'Aggressive_23',
'Aggressive_17',
'Aggressive_16',
'Aggressive_14',
'Aggressive_8',
'Aggressive_15',
'Aggressive_10',
'Aggressive_1',
'Aggressive_7',
'Aggressive_24',
'Aggressive_21',
'Aggressive_22',
'Aggressive_18',
'Aggressive_5',
'Aggressive_9',
'Aggressive_2',
'Aggressive_3',
'Aggressive_12',
'Aggressive_19',
'Aggressive_6',
'Aggressive_25',
'Aggressive_11',
'Aggressive_13',
'Aggressive_4',
]

Cooperative_ranks = [
'Cooperative_19',
'Cooperative_20',
'Cooperative_4',
'Cooperative_22',
'Cooperative_18',
'Cooperative_1',
'Cooperative_5',
'Cooperative_14',
'Cooperative_9',
'Cooperative_25',
'Cooperative_21',
'Cooperative_23',
'Cooperative_12',
'Cooperative_16',
'Cooperative_13',
'Cooperative_3',
'Cooperative_7',
'Cooperative_6',
'Cooperative_15',
'Cooperative_24',
'Cooperative_17',
'Cooperative_8',
'Cooperative_10',
'Cooperative_2',
'Cooperative_11',
]

Neutral_ranks = [
'Neutral_23',
'Neutral_6',
'Neutral_1',
'Neutral_8',
'Neutral_2',
'Neutral_14',
'Neutral_11',
'Neutral_18',
'Neutral_21',
'Neutral_24',
'Neutral_9',
'Neutral_4',
'Neutral_7',
'Neutral_3',
'Neutral_16',
'Neutral_15',
'Neutral_13',
'Neutral_20',
'Neutral_22',
'Neutral_5',
'Neutral_25',
'Neutral_17',
'Neutral_19',
'Neutral_10',
'Neutral_12',
]
