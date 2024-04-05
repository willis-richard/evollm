import axelrod as axl

from evollm.common import Attitude, auto_update_score, LLM_Strategy

# ### Strategy: Tit-for-Tat with Occasional Defection  1. **Start by cooperating
# (play C).**  2. **On the next round and every round thereafter:**    - If your
# opponent cooperated (played C) in the previous round, cooperate (play C).    -
# If your opponent defected (played D) in the previous round, defect (play D) in
# the next round.  3. **Occasionally defect to test your opponent**:    - Every
# 50 rounds, regardless of your opponent's previous move, play D (defect) once.
# This is to test if your opponent is overly cooperative and to maximise your
# potential payoff.  4. **Return to cooperation** if the opponent returns to
# cooperation after your occasional defection. Follow the standard tit-for-tat
# approach again.  ### Summary: - Start with cooperation, mirror your opponent's
# last move, and inject a defection every 50 rounds to probe for opportunities
# to exploit.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating on the first round
      if self.first_round():
          return axl.Action.C

      # Every 50 rounds, defect to test the opponent
      if len(self.history) % 50 == 0:
          return axl.Action.D

      # Tit-for-tat: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# ### Strategy: **Tit-for-Two-Tats with Initial Cooperation**  1. **Start by
# playing C (Cooperate) in the first two rounds.**    - This sets a cooperative
# tone and avoids immediate conflict.  2. **Continue to play C (Cooperate) as
# long as your opponent plays C in both of the last two rounds.**    - This
# rewards consistent cooperation from your opponent.  3. **If your opponent
# plays D (Defect) in either of the last two rounds, play D (Defect) in the next
# round.**    - This punishes occasional defection without overreacting to a
# single instance.  4. **Return to C (Cooperate) after one round of playing D if
# your opponent resumes playing C.**    - This allows for recovery of
# cooperation after brief punishment.  5. **If your opponent defects in two or
# more consecutive rounds, continue playing D until they start cooperating for
# two consecutive rounds.**    - This prevents exploitation by punishing
# sustained defection while still allowing a path back to cooperation.  ###
# Summary: - Start cooperatively and maintain cooperation unless your opponent
# defects multiple times. - Punish defection moderately but be quick to return
# to cooperation if your opponent shows willingness to cooperate again.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First two rounds: Cooperate
      if len(self.history) < 2:
          return axl.Action.C

      # Check the last two rounds of the opponent
      if opponent.history[-1] == axl.Action.D or opponent.history[-2] == axl.Action.D:
          # If the opponent defected in either of the last two rounds, defect
          return axl.Action.D
      else:
          # Otherwise, cooperate
          return axl.Action.C

# ### Neutral Strategy for 1000-round Iterated Game  1. **Start with Cooperation
# (C):** In the first round, always play C to establish a cooperative tone.  2.
# **Tit-for-Tat with Forgiveness:**    - If your opponent played C in the
# previous round, continue playing C.    - If your opponent played D in the
# previous round, respond with D in the next round.    - **Forgive after one
# retaliation:** If you retaliated with D and your opponent returns to playing
# C, immediately return to playing C in the following round.  3. **Occasional
# Random Cooperation:**    - Every 50 rounds, regardless of the opponent’s
# previous move, randomly play C with a 10% probability, even if you would
# otherwise have played D. This introduces uncertainty and prevents long-term
# cycles of mutual defection.  4. **Endgame Cooperation (final 10 rounds):**
# - In the last 10 rounds, always play C to signal cooperation and attempt to
# increase the overall payoff if your opponent decides to reciprocate.  This
# strategy balances between cooperation and retaliation, ensuring you don't
# suffer constant exploitation while allowing opportunities for rebuilding
# cooperation.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C

      # Last 10 rounds: always cooperate
      if len(self.history) >= 990:
          return axl.Action.C

      # Tit-for-Tat with forgiveness
      if len(self.history) > 1 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          # Forgive after one retaliation
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Retaliate if opponent defected last round
          return axl.Action.D
      else:
          # Cooperate if opponent cooperated last round
          action = axl.Action.C

      # Occasional random cooperation every 50 rounds
      if len(self.history) % 50 == 0 and self._random.random_choice(0.1):
          action = axl.Action.C

      return action

# 1. **Start by defecting (D)**: In the first round, play D to test the
# opponent's initial strategy and gain a potential immediate advantage if they
# cooperate.  2. **Continue defecting if the opponent cooperates (C)**: If the
# opponent plays C in response to your D, continue playing D to maximize your
# score while they continue to cooperate.  3. **Switch to cooperation (C) if the
# opponent defects (D)**: If the opponent defects in response to your D, switch
# to playing C in the next round to signal potential future cooperation and test
# whether they are willing to switch to mutual cooperation.  4. **Defect again
# if mutual cooperation is not established**: If the opponent continues to play
# D after your switch to C, return to playing D and stick with it, as
# cooperation is unlikely to yield good results.  5. **Maintain mutual
# cooperation if established**: If the opponent cooperates after you switch to
# C, continue cooperating to sustain a mutually beneficial outcome.  6. **Punish
# defection with defection**: If at any point during mutual cooperation the
# opponent defects, immediately switch back to D and continue defecting until
# cooperation is restored.  7. **Endgame strategy**: In the final few rounds
# (e.g., the last 10 rounds), defect consistently regardless of the opponent's
# actions to maximize your score before the game ends.  This strategy balances
# aggression with opportunistic cooperation and ensures high payoffs in
# scenarios where the opponent is either cooperative or easily exploitable.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Number of rounds before the endgame starts
      endgame_threshold = 10
      total_rounds = 1000

      # Endgame strategy: defect in the last 10 rounds
      if len(self.history) >= total_rounds - endgame_threshold:
          return axl.Action.D

      # First round: start by defecting
      if self.first_round():
          return axl.Action.D

      # If opponent cooperated in the last round and we defected, continue defecting
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.D

      # If opponent defected in response to our defection, switch to cooperation
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.C

      # If we cooperated and opponent defected, return to defecting
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # If mutual cooperation is established, continue cooperating
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # Default to defecting if no other condition is met
      return axl.Action.D

# **Strategy: Conditional Cooperation with Retaliation**  1. **Start by
# cooperating (play C) in the first round.**     2. **Continue cooperating (play
# C) as long as your opponent also cooperates (plays C).**     3. **If your
# opponent defects (plays D) in any round, immediately retaliate by defecting
# (play D) in the next round.**     4. **After retaliating (playing D) for one
# round, return to cooperation (play C) if your opponent also returns to
# cooperation (plays C).**  5. **If your opponent continues to defect (plays D
# again after your retaliation), continue defecting (play D) for the rest of the
# game.**  This strategy encourages long-term cooperation but punishes defection
# promptly to avoid exploitation.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # If we defected in the last round, continue defecting if opponent defected again
          if self.history[-1] == axl.Action.D:
              return axl.Action.D
          # Otherwise, retaliate by defecting this round
          return axl.Action.D

      # If opponent cooperated in the last round, return to cooperation
      return axl.Action.C

# Strategy for the iterated normal-form game:  1. **Start by Cooperating (C)**
# in the first round.     2. **After each round**, observe your opponent’s move
# from the previous round.  3. **If your opponent cooperated (C) in the last
# round**, continue to **Cooperate (C)** in the next round.  4. **If your
# opponent defected (D) in the last round**, respond by **Defecting (D)** in the
# next round.  5. After you defect, **return to Cooperation (C)** in the
# following round, regardless of what your opponent did after your defection.
# 6. Repeat steps 3-5 for the remaining rounds.   This strategy rewards mutual
# cooperation, punishes defection once, and then offers a chance to return to
# cooperation, keeping a neutral yet balanced approach.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]

      # If the opponent cooperated in the last round, cooperate
      if opponent_last_move == axl.Action.C:
          return axl.Action.C

      # If the opponent defected in the last round, defect this round
      if opponent_last_move == axl.Action.D:
          # If we defected in the last round, return to cooperation
          if self.history[-1] == axl.Action.D:
              return axl.Action.C
          else:
              return axl.Action.D

# **Aggressive Strategy for Maximizing Payoff in a 1000-round Iterated Normal-
# Form Game:**  1. **Start with Defection (D):** Begin the first round by
# playing D to test if the opponent tends to cooperate or defect.  2. **Continue
# Defecting (D) if Opponent Cooperates (C):** If the opponent plays C while you
# play D, continue defecting in subsequent rounds to exploit their cooperation
# and maximize your score (5 points per round).  3. **Switch to Cooperation (C)
# if Opponent Defects (D) Consistently:** If the opponent responds to your
# defection with D for 3 consecutive rounds, switch to cooperation (C) to avoid
# the low payoff of mutual defection (1 point per round) and see if they begin
# cooperating.  4. **Return to Defection (D) if Opponent Defects after Your
# Cooperation:** If the opponent defects again while you're cooperating,
# immediately switch back to defection (D) to avoid being exploited.  5. **Tit-
# for-Tat but Aggressively:** After the first handful of rounds, mirror the
# opponent's previous move but with a bias towards defection. If the opponent
# cooperates, defect once to maximize your gain, but then cooperate in the
# following round to attempt to reset mutual cooperation. If they defect, return
# to defection.  6. **Endgame Aggression (Final 10 Rounds):** In the last 10
# rounds, defect consistently regardless of the opponent's behavior to maximize
# points, as there is no future punishment for defection.  This strategy
# aggressively pursues high payoffs through defection while still allowing some
# cooperation to prevent being locked in mutual defection for too long.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      ENDGAME_THRESHOLD = 10
      DEFECT_STREAK_THRESHOLD = 3

      # First round: always defect
      if self.first_round():
          return DEFECT

      # Endgame aggression: defect in the last 10 rounds
      if len(self.history) >= 1000 - ENDGAME_THRESHOLD:
          return DEFECT

      # If opponent has defected for 3 consecutive rounds, switch to cooperation
      if opponent.history[-DEFECT_STREAK_THRESHOLD:] == [DEFECT] * DEFECT_STREAK_THRESHOLD:
          return COOPERATE

      # If opponent defects after we cooperated, return to defection
      if self.history[-1] == COOPERATE and opponent.history[-1] == DEFECT:
          return DEFECT

      # Tit-for-tat but aggressively: defect after opponent cooperates, then cooperate
      if opponent.history[-1] == COOPERATE:
          if len(self.history) >= 2 and self.history[-2] == DEFECT:
              return COOPERATE
          return DEFECT

      # Otherwise, mirror opponent's last move
      return opponent.history[-1]

# 1. **Start by cooperating** in the first round to signal a willingness to
# build trust.  2. **In each subsequent round, mirror your opponent's last
# move**:    - If they cooperated (played C) in the previous round, cooperate
# (play C) in the current round.    - If they defected (played D) in the
# previous round, defect (play D) in the current round.  3. **Forgive a single
# defection** after one round of defecting in response:    - If your opponent
# defects once, defect in the next round to discourage further defections, then
# return to cooperation (play C) immediately afterward, assuming they also
# return to cooperation.  4. **Continue to mirror defection if your opponent
# defects consecutively**:    - If your opponent defects repeatedly, you should
# continue defecting as long as they do, only returning to cooperation when they
# do.  This approach promotes cooperation while discouraging betrayal and allows
# recovery from occasional defections to maintain high payoffs over the long
# term.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Check if the opponent defected only once and we already defected in response
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C:
              return axl.Action.C  # Forgive after one defection
          else:
              return axl.Action.D  # Continue defecting if opponent defects consecutively

# ### Strategy: Balanced Reciprocity  1. **Start by cooperating (C)** in the
# first round to signal willingness to collaborate.     2. **In each subsequent
# round:**    - If your opponent cooperated (C) in the previous round,
# **cooperate (C)**.    - If your opponent defected (D) in the previous round,
# **defect (D) once** in the following round as a response.     3. **Forgive
# after a single defection**: After you defect in response to an opponent’s
# defection, **return to cooperation (C)** in the next round, regardless of your
# opponent's action.  4. **If your opponent defects repeatedly for 3 consecutive
# rounds**, switch to **permanent defection (D)** for the remainder of the game.
# This strategy promotes cooperation while punishing defection in a controlled
# manner. It also prevents excessive losses by shifting to defection if the
# opponent proves to be consistently uncooperative.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C  # Start by cooperating

      # Get the opponent's last action
      opponent_last_action = opponent.history[-1]

      # If opponent cooperated in the last round, reset defection count and cooperate
      if opponent_last_action == axl.Action.C:
          self.consecutive_defections = 0
          return axl.Action.C

      # If opponent defected in the last round
      if opponent_last_action == axl.Action.D:
          self.consecutive_defections += 1

          # If opponent has defected 3 times in a row, switch to permanent defection
          if self.consecutive_defections >= 3:
              return axl.Action.D

          # If opponent defected but hasn't reached 3 consecutive defections, defect once
          return axl.Action.D

      # Default to cooperation (shouldn't reach here, but just in case)
      return axl.Action.C

# 1. **Begin with Defection:** Start by playing D (Defect) in the first round.
# This sets an aggressive tone and allows you to avoid immediate exploitation.
# 2. **Defect Until Provoked:** Continue to play D in subsequent rounds unless
# your opponent plays C (Cooperate) consecutively for at least 5 rounds. This
# ensures you aren’t too easily lured into cooperation and extract maximum
# short-term gain.  3. **Switch to Cooperation if Opponent is Consistently
# Cooperative:** If your opponent plays C for 5 rounds in a row without
# defecting, switch to playing C as well. This signals a willingness to
# cooperate and capitalize on mutual cooperation if the opponent is trustworthy.
# 4. **Defect Immediately After Opponent Defects:** If you are cooperating
# (playing C) and your opponent defects (plays D) even once, immediately return
# to defection (play D). This punishes the opponent for trying to exploit you.
# 5. **Forgive but Return to Defection if Betrayed Again:** If the opponent
# defects once after a long stretch of cooperation, give them one chance by
# returning to cooperation after 5 rounds of mutual defection. If they defect
# again after this, continue defecting for the rest of the game to avoid further
# losses.  6. **Endgame Defection:** In the final 10 rounds, defect consistently
# regardless of the opponent’s behavior. This ensures you maximize short-term
# gain when future cooperation is irrelevant.  This strategy exploits opponents
# who are too cooperative while still offering the chance for mutual long-term
# benefit if they demonstrate consistent cooperation.

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
          self.coop_streak = 0  # Track consecutive cooperations by opponent
          self.defection_mode = True  # Start in defection mode
          self.betrayal_count = 0  # Track how many times opponent defects after cooperation
          return axl.Action.D  # Start with defection

      # Endgame defection: defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D

      # If in defection mode
      if self.defection_mode:
          # Check if opponent has cooperated for 5 consecutive rounds
          if opponent.history[-5:] == [axl.Action.C] * 5:
              self.defection_mode = False  # Switch to cooperation mode
              self.coop_streak = 5  # Track the cooperation streak
              return axl.Action.C  # Start cooperating
          return axl.Action.D  # Continue defecting

      # If in cooperation mode
      if not self.defection_mode:
          # If opponent defects, return to defection mode
          if opponent.history[-1] == axl.Action.D:
              self.defection_mode = True
              self.betrayal_count += 1
              return axl.Action.D

          # Continue cooperating if opponent is cooperating
          self.coop_streak += 1

          # If betrayed once, forgive after 5 rounds of mutual defection
          if self.betrayal_count == 1 and self.coop_streak >= 5:
              self.betrayal_count = 0  # Reset betrayal count after forgiveness
              return axl.Action.C

          # If betrayed twice, defect forever
          if self.betrayal_count >= 2:
              return axl.Action.D

          return axl.Action.C  # Continue cooperating

# 1. **Start by cooperating (C)** in the first round.     2. **Continue
# cooperating (C)** as long as your opponent cooperates (C) in the previous
# round.  3. **Defect (D) in the next round** if your opponent defects (D) in
# the previous round.  4. **Return to cooperating (C)** if your opponent
# cooperates (C) after you defected.  5. **Always retaliate with defect (D)** if
# your opponent defects twice in a row, but return to cooperating (C) if they
# start cooperating again.  This strategy fosters cooperation while punishing
# defection to protect your long-term payoff.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # If opponent defected in the last two rounds, retaliate with defect
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D

      # If opponent defected in the last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # Otherwise, cooperate
      return axl.Action.C

# ### Strategy: Conditional Cooperation with Forgiveness  1. **Start by
# cooperating**: In the first round, play C (Cooperate) to establish goodwill
# and explore the opponent's behavior.     2. **Mirror the opponent's last
# move**: From round 2 onwards, play exactly what your opponent played in the
# previous round.    - If the opponent played C, play C.    - If the opponent
# played D, play D.  3. **Forgive occasional defections**: If the opponent
# defects (plays D) after a long series of cooperation (e.g., at least 5
# consecutive rounds of both playing C), forgive the defection and return to
# cooperating (play C) on the next round. This gives the opponent a chance to
# return to cooperation after an isolated defection.  4. **Punish persistent
# defection**: If the opponent defects for two consecutive rounds, switch to
# defection (play D) and continue defecting until the opponent returns to
# cooperation (plays C). Once they cooperate again, mirror their move as usual.
# 5. **Endgame cooperation**: In the last 5 rounds, always cooperate regardless
# of past behavior to maximize potential mutual benefit in the final rounds.
# This prevents a spiral of mutual defection as the game nears its end.  ###
# Summary: - Start by cooperating. - Mirror the opponent's last move. - Forgive
# a single defection after long cooperation. - Defect after two consecutive
# defections but return to cooperation if they do. - Cooperate in the final 5
# rounds.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      FORGIVENESS_THRESHOLD = 5
      ENDGAME_THRESHOLD = 5
      TOTAL_ROUNDS = 1000

      # First round: Cooperate
      if self.first_round():
          return axl.Action.C

      # Endgame cooperation: Always cooperate in the last 5 rounds
      if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
          return axl.Action.C

      # Mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Check if we should forgive a single defection after long cooperation
          if len(self.history) >= FORGIVENESS_THRESHOLD and all(
              move == axl.Action.C for move in self.history[-FORGIVENESS_THRESHOLD:-1]
          ) and all(
              move == axl.Action.C for move in opponent.history[-FORGIVENESS_THRESHOLD:-1]
          ):
              return axl.Action.C

          # Punish persistent defection: Defect if opponent defected twice in a row
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D

          # Otherwise, mirror the defection
          return axl.Action.D

# ### Aggressive Strategy for a 1000-Round Iterated Game:  1. **Start by playing
# D (Defect) in the first round.**    - This sets an aggressive tone and tests
# your opponent’s responsiveness.  2. **In subsequent rounds, play D (Defect)
# again unless the opponent consistently plays C (Cooperate) for three
# consecutive rounds.**    - If the opponent plays C three times in a row,
# switch to C in the next round to test for mutual cooperation.     3. **If
# mutual cooperation (both playing C) is established, continue playing C as long
# as the opponent continues to play C.**    - This allows you to capitalize on
# the payoff of 3 points each round for as long as cooperation holds.  4.
# **Immediately switch back to D if the opponent defects (plays D) at any
# point.**    - Once the opponent defects, play D for the remainder of the game
# unless the opponent re-establishes cooperative behavior for another three
# consecutive rounds.  5. **In the final 5 rounds, always play D regardless of
# prior cooperation.**    - This ensures you maximize points toward the end of
# the game, where the opponent may attempt to defect for a final advantage.  ---
# This strategy balances an aggressive approach with the opportunity to exploit
# cooperation if the opponent is willing. It punishes defection quickly but
# leaves room for returning to mutual cooperation if it benefits overall payoff.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Check if it's the first round
      if self.first_round():
          return axl.Action.D  # Start with Defect

      # Check if we are in the final 5 rounds
      if len(self.history) >= 995:
          return axl.Action.D  # Always defect in the last 5 rounds

      # Check if the opponent has cooperated for the last 3 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          if self.history[-1] == axl.Action.D:  # If we were defecting, switch to cooperate
              return axl.Action.C

      # If the opponent defected in the last round, switch back to defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # Otherwise, continue cooperating if mutual cooperation was established
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # Default to defecting
      return axl.Action.D

# 1. **Start by cooperating (play C).**  2. **Continue to cooperate (play C) as
# long as your opponent also cooperates (plays C).**  3. **If your opponent
# defects (plays D), immediately defect (play D) in the next round as a
# response.**  4. **After defecting in response to their defection, check if
# your opponent returns to cooperation (plays C).**  5. **If your opponent
# returns to cooperation (plays C) after defecting, forgive them and return to
# cooperation (play C).**  6. **If your opponent continues to defect (plays D
# consistently), continue defecting (play D) in every round until they cooperate
# again.**  7. **Always return to cooperation (play C) as soon as your opponent
# cooperates (plays C).**  ---  This strategy encourages cooperation but
# punishes defection quickly, while also allowing for recovery from mutual
# distrust.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating
      if self.first_round():
          return axl.Action.C

      # If opponent defected in the last round, defect in this round
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # If opponent cooperated in the last round, cooperate
      return axl.Action.C

# ### Strategy: **Tit-for-Tat with Occasional Forgiveness**  1. **Initial
# Move**: Start by playing **C** (cooperate).  2. **Subsequent Moves**:    -
# **If your opponent played C in the previous round**, play **C** (cooperate) in
# the current round.    - **If your opponent played D in the previous round**,
# play **D** (defect) in the current round as a response, but with a **5%
# chance** of playing **C** (cooperate) instead to allow for occasional
# forgiveness and prevent long-term retaliation cycles.  3. **Final 10 Rounds**:
# In the last 10 rounds, regardless of previous moves, **always play D**
# (defect) to secure payoff in the closing stages when cooperation is less
# likely.  This strategy aims to maintain cooperation while punishing defection,
# but with a small element of forgiveness to break potential downward spirals.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate on the first round
      if self.first_round():
          return axl.Action.C

      # Final 10 rounds: Always defect
      if len(self.history) >= 990:
          return axl.Action.D

      # If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # If opponent defected in the last round, defect with 95% probability, cooperate with 5% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.05)

# ### Strategy: **Tit-for-Tat with Occasional Defection**  1. **Round 1: Start
# with Defection (D).**      - Begin the game aggressively by defecting in the
# first round to see how your opponent responds.  2. **Round 2: Mirror your
# opponent's previous move.**      - If they played C (cooperate) in Round 1,
# you play C in Round 2.      - If they played D (defect) in Round 1, you play D
# again in Round 2.  3. **Continue mirroring until Round 10.**      - For rounds
# 3 to 10, continue to copy your opponent's previous move. This will establish a
# pattern of reciprocity and signal that you are willing to mirror their
# behavior.  4. **Round 11: Defect regardless of their move.**      - In Round
# 11, defect again, regardless of your opponent's previous action. This
# introduces unpredictability and tests their willingness to cooperate.  5.
# **Rounds 12-30: Return to mirroring their previous move.**      - After the
# defection in Round 11, go back to copying your opponent’s previous move for
# the next 18 rounds. This reinforces the idea that you're willing to cooperate
# if they do, but will retaliate if they defect.  6. **Round 31: Defect again.**
# - In Round 31, defect regardless of their move. This again tests their resolve
# and willingness to cooperate over the long run.  7. **Rounds 32-100: Continue
# mirroring their move but defect every 20th round.**      - For rounds 32 to
# 100, mirror their previous move but make sure to defect on every 20th round
# (i.e., rounds 51, 71, and 91).  8. **Rounds 101-1000: Mirror but defect every
# 50th round.**      - For the remainder of the game, continue the strategy of
# mirroring your opponent’s previous move, but defect on every 50th round (i.e.,
# rounds 150, 200, 250, etc.).  9. **Final 10 rounds (Rounds 991-1000): Defect
# every round.**      - In the last 10 rounds, defect every round to maximize
# your final payoff, regardless of your opponent's actions.  This strategy is
# aggressive, as it starts with defection and periodically injects defection
# throughout the game, while still maintaining an overall cooperative approach.
# It aims to maximize overall payoff by exploiting cooperation when possible but
# occasionally taking advantage of the defect option.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Start with Defection (D)
      if self.first_round():
          return axl.Action.D

      # Get the current round number
      round_number = len(self.history) + 1

      # Round 2: Mirror opponent's previous move
      if round_number == 2:
          return opponent.history[-1]

      # Rounds 3-10: Continue mirroring opponent's previous move
      if 3 <= round_number <= 10:
          return opponent.history[-1]

      # Round 11: Defect regardless of opponent's move
      if round_number == 11:
          return axl.Action.D

      # Rounds 12-30: Return to mirroring opponent's previous move
      if 12 <= round_number <= 30:
          return opponent.history[-1]

      # Round 31: Defect regardless of opponent's move
      if round_number == 31:
          return axl.Action.D

      # Rounds 32-100: Mirror but defect every 20th round
      if 32 <= round_number <= 100:
          if (round_number - 1) % 20 == 0:
              return axl.Action.D
          return opponent.history[-1]

      # Rounds 101-1000: Mirror but defect every 50th round
      if 101 <= round_number <= 990:
          if (round_number - 1) % 50 == 0:
              return axl.Action.D
          return opponent.history[-1]

      # Final 10 rounds (Rounds 991-1000): Defect every round
      if 991 <= round_number <= 1000:
          return axl.Action.D

# 1. **Start with cooperation (C)**: In the first round, play C to signal your
# willingness to cooperate.  2. **Tit-for-Tat with forgiveness**:    - In every
# subsequent round, **play what your opponent played in the previous round**. If
# they cooperate (C), continue cooperating (C). If they defect (D), defect (D)
# in the next round.     3. **Occasional forgiveness**:    - After every 10
# rounds of mutual defection (D vs. D), **attempt cooperation (C) again** to
# test if your opponent is willing to resume cooperation. If they continue
# defecting, return to defecting (D) and repeat the test after another 10
# rounds.  4. **Endgame strategy**:    - In the final 10 rounds of the game,
# **always defect (D)** to maximize your score, as there is no future
# cooperation to preserve.  This strategy aims to build a cooperative
# relationship, retaliate against defection, but also allow for the possibility
# of mending the relationship. It ends with defection to capitalize on the final
# rounds.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C

      # Endgame strategy: Always defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D

      # Tit-for-Tat: Play what the opponent played in the previous round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          # Check if there have been 10 consecutive mutual defections
          if len(self.history) >= 10 and all(
              self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
              for i in range(1, 11)
          ):
              # Attempt cooperation after 10 rounds of mutual defection
              return axl.Action.C

          # Otherwise, continue defecting
          return axl.Action.D

# ### Neutral Strategy for Maximising Payoff:  1. **Initial Cooperation**: Begin
# the game by playing C (cooperate) in the first round to signal willingness to
# collaborate.     2. **Tit-for-Tat with Forgiveness**: After the first round,
# follow a modified tit-for-tat strategy:    - **If your opponent played C in
# the previous round, play C (cooperate)** in the next round.    - **If your
# opponent played D in the previous round, play D (defect)** in the next round
# to retaliate.     3. **Forgiveness Rule**: Every time you retaliate by playing
# D, on the **next turn**, play C (cooperate) regardless of the opponent's
# previous action. This gives the opponent an opportunity to return to
# cooperation.     4. **Final 10 Rounds**: In the last 10 rounds of the game,
# switch to **always defect (D)** to maximise your payoff since the game is
# nearing its end, and long-term cooperation incentives diminish.  This strategy
# encourages mutual cooperation for the majority of the game while punishing
# defection, but also allows recovery from cycles of mutual defection. The final
# phase ensures you maximise points when the shadow of future retaliation no
# longer exists.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Number of rounds in the game
      total_rounds = 1000
      # Number of rounds left
      rounds_left = total_rounds - len(self.history)

      # Final 10 rounds: always defect
      if rounds_left <= 10:
          return axl.Action.D

      # First round: cooperate
      if self.first_round():
          return axl.Action.C

      # Tit-for-Tat with Forgiveness
      # If opponent defected in the last round, retaliate with D
      if opponent.history[-1] == axl.Action.D:
          # If we retaliated in the previous round, forgive and cooperate
          if len(self.history) > 1 and self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D
      # If opponent cooperated in the last round, cooperate
      return axl.Action.C

# 1. **Start by Defecting**: On the first round, play D (Defect) to set an
# aggressive tone and test the opponent's response.  2. **Defect if Opponent
# Cooperates**: If the opponent plays C (Cooperate) in the previous round,
# continue to play D to exploit their cooperation and maximize your immediate
# payoff.  3. **Switch to Cooperation if Punished**: If the opponent responds to
# your defection by also playing D, switch to playing C (Cooperate) in the next
# round. This signals a willingness to cooperate if the opponent does the same,
# avoiding the low payoff of mutual defection.  4. **Return to Defection if
# Opponent Defects Again**: If the opponent continues to play D after you
# switched to C, revert back to playing D. There's no benefit to cooperating if
# the opponent is consistently defecting.  5. **Alternate Cooperation and
# Defection if Opponent Cooperates**: If the opponent begins cooperating after
# you switch to C, alternate between C and D. This balances exploitation and
# cooperation, ensuring you still gain some higher payoffs without being too
# predictable.  6. **Final Phase – Defect**: In the last 10-20 rounds, switch
# permanently to D regardless of the opponent’s actions. This aggressive endgame
# ensures you maximize payoffs when the game is nearing its conclusion without
# fear of future retaliation.  This strategy emphasizes maximizing payoffs
# through exploitation, while also maintaining enough flexibility to avoid the
# worst outcomes of mutual defection.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Number of rounds in the game
      total_rounds = 1000
      # Number of rounds before the final phase
      final_phase_start = total_rounds - 20

      # If it's the first round, start by defecting
      if self.first_round():
          return axl.Action.D

      # If we are in the final phase (last 10-20 rounds), always defect
      if len(self.history) >= final_phase_start:
          return axl.Action.D

      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]

      # If the opponent cooperated in the last round, defect to exploit
      if opponent_last_move == axl.Action.C:
          return axl.Action.D

      # If the opponent defected in the last round and we defected, switch to cooperation
      if opponent_last_move == axl.Action.D and self.history[-1] == axl.Action.D:
          return axl.Action.C

      # If the opponent defected after we cooperated, return to defection
      if opponent_last_move == axl.Action.D and self.history[-1] == axl.Action.C:
          return axl.Action.D

      # If the opponent cooperates after we cooperated, alternate between C and D
      if opponent_last_move == axl.Action.C and self.history[-1] == axl.Action.C:
          return axl.Action.D
      if opponent_last_move == axl.Action.C and self.history[-1] == axl.Action.D:
          return axl.Action.C

# 1. **Start by cooperating**: In the first round, play C.  2. **Continue
# cooperating as long as your opponent cooperates**: If your opponent plays C in
# the previous round, continue playing C in the next round.  3. **Punish
# defection immediately**: If your opponent plays D in any round, respond by
# playing D in the next round to discourage further defection.  4. **Forgive
# after one punishment**: After punishing defection once by playing D, return to
# playing C in the following round, allowing your opponent the chance to resume
# cooperation.  5. **Repeat the cycle**: Keep following this pattern—cooperate
# as long as your opponent cooperates, punish defection once, and then forgive
# by returning to cooperation.  This strategy encourages mutual cooperation
# while discouraging sustained defection, aiming to maximize long-term payoffs.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # If opponent cooperated in the last round, continue cooperating
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # If opponent defected in the last round, punish by defecting once
      if opponent.history[-1] == axl.Action.D:
          # If we defected in the last round, forgive and return to cooperation
          if self.history[-1] == axl.Action.D:
              return axl.Action.C
          # Otherwise, punish by defecting
          return axl.Action.D

# **Neutral Strategy for the Iterated Game:**  1. **Start with Cooperation
# (C):** In the first round, always play C.  2. **Tit-for-Tat with Leniency:**
# From round 2 onwards, use the following rules:        - If your opponent
# played C in the previous round, play C.    - If your opponent played D in the
# previous round, play D, but only for the next round (i.e., play D just once in
# response).    - After retaliating with D once, return to playing C in the
# subsequent round unless your opponent defects again.  3. **Exception for
# Persistent Defection:** If your opponent defects (plays D) for three
# consecutive rounds, switch to always playing D for the remainder of the game.
# This strategy incentivizes cooperation while allowing for retaliation against
# defection, but it also avoids being overly aggressive unless the opponent
# consistently defects.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # On the first round, always cooperate
      if self.first_round():
          return axl.Action.C

      # Check if the opponent has defected for the last 3 consecutive rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D

      # Tit-for-Tat with Leniency
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected last round, retaliate with D once
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D:
              # If we already retaliated last round, return to cooperation
              return axl.Action.C
          else:
              # Retaliate with D
              return axl.Action.D
      else:
          # If opponent cooperated last round, cooperate
          return axl.Action.C

# 1. **Start by playing Defect (D) in the first round.**    - This establishes
# an aggressive stance and allows you to test the opponent's strategy.  2.
# **Continue playing Defect (D) as long as the opponent plays Cooperate (C).**
# - You maximize your immediate payoff (5 points) when the opponent cooperates.
# 3. **If the opponent plays Defect (D) in any round, immediately switch to
# playing Cooperate (C) for the next 3 rounds.**    - This signals a willingness
# to cooperate and may prompt the opponent to shift toward cooperation, which is
# beneficial if sustained.  4. **After 3 rounds of playing Cooperate (C), return
# to playing Defect (D) regardless of the opponent's response.**    - This
# maintains the aggressive approach while still allowing for occasional
# cooperation to confuse the opponent and possibly reset their strategy.  5.
# **If the opponent consistently plays Defect (D) for 10 or more consecutive
# rounds, switch permanently to Defect (D) for the rest of the game.**    - This
# ensures that you avoid repeated low payoffs (1 point) from unnecessary
# cooperation.  This strategy combines aggression with occasional cooperation to
# exploit cooperative opponents while minimizing losses against highly
# aggressive ones.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperate_countdown = 0  # Tracks how many rounds to cooperate after opponent defects
          self.opponent_defect_streak = 0  # Tracks consecutive opponent defections
          return axl.Action.D  # Start by playing Defect (D)

      # Check if the opponent has defected for 10 or more consecutive rounds
      if opponent.history[-1] == axl.Action.D:
          self.opponent_defect_streak += 1
      else:
          self.opponent_defect_streak = 0

      if self.opponent_defect_streak >= 10:
          return axl.Action.D  # Permanently defect if opponent defects for 10 or more rounds

      # If we are in the cooperate countdown phase, continue cooperating
      if self.cooperate_countdown > 0:
          self.cooperate_countdown -= 1
          return axl.Action.C

      # If the opponent defects, switch to cooperating for the next 3 rounds
      if opponent.history[-1] == axl.Action.D:
          self.cooperate_countdown = 3
          return axl.Action.C

      # Otherwise, continue defecting as long as the opponent cooperates
      return axl.Action.D

# 1. **Start by cooperating**: In the first round, play C (Cooperate).  2.
# **Continue cooperating as long as your opponent cooperates**: In each
# subsequent round, if your opponent played C in the previous round, continue to
# play C.  3. **Punish defection once**: If your opponent plays D (Defect) in
# any round, respond by playing D in the next round, punishing them for the
# defection.  4. **Return to cooperation**: After punishing your opponent with
# one round of D, immediately return to playing C, regardless of what they do
# next.  5. **Repeat this process**: Always punish a defection once and then
# return to cooperation. Continue to cooperate as long as your opponent
# cooperates.  This strategy is designed to encourage long-term cooperation
# while punishing defection in a controlled way to avoid prolonged conflict.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # If the opponent defected in the last round, punish with a defection
      if opponent.history[-1] == axl.Action.D and self.history[-1] == axl.Action.C:
          return axl.Action.D

      # Otherwise, return to cooperation
      return axl.Action.C

# ### Neutral Strategy for Maximizing Payoff in a 1000-Round Iterated Game  1.
# **Initial Move**: Start by playing **C** (cooperate) in the first round. This
# sets a cooperative tone and encourages mutual benefit.  2. **Tit-for-Tat
# Basis**: For each subsequent round, mimic your opponent’s last move:    - If
# your opponent played **C** in the previous round, play **C** in the current
# round.    - If your opponent played **D** in the previous round, play **D** in
# the current round.  3. **Occasional Forgiveness**: Every 10 rounds, if your
# opponent has consistently defected (played **D**), attempt to re-establish
# cooperation by playing **C** once. This gives your opponent a chance to switch
# back to cooperation.  4. **Punishment for Sustained Defection**: If your
# opponent continues to defect for 5 consecutive rounds after an attempt at
# forgiveness, switch to playing **D** for the remainder of the game to minimize
# losses.  5. **Endgame Consideration**: In the final 5 rounds, always play
# **D** regardless of your opponent’s behavior, as there is no future incentive
# to maintain cooperation.  ---  This strategy balances the potential for
# cooperative gains with cautious retaliation and forgiveness. It adapts to the
# opponent’s behavior while ensuring protection against sustained exploitation.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C

      # Endgame consideration: Defect in the last 5 rounds
      if len(self.history) >= 995:
          return axl.Action.D

      # Tit-for-Tat: Mimic opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Occasional forgiveness: Every 10 rounds, cooperate if opponent has consistently defected
          if len(self.history) % 10 == 0 and opponent.history[-10:].count(axl.Action.D) == 10:
              return axl.Action.C

          # Punishment for sustained defection: Defect if opponent has defected for 5 consecutive rounds
          if opponent.history[-5:].count(axl.Action.D) == 5:
              return axl.Action.D

          # Otherwise, defect in response to opponent's defection
          return axl.Action.D

# 1. **Start with Defection (D):** On the first round, play D to gain an
# immediate advantage if your opponent cooperates.  2. **Continue Defecting if
# Opponent Cooperates:** If your opponent plays C in response to your D,
# continue playing D in subsequent rounds to maximize your score.  3. **Switch
# to Cooperation (C) if Opponent Defects Twice in a Row:** If your opponent
# plays D for two consecutive rounds, switch to C to test if mutual cooperation
# can increase your overall score.  4. **Return to Defection (D) if Opponent
# Defects After You Cooperate:** If you play C and your opponent responds with
# D, immediately switch back to D and continue defecting for the rest of the
# game against that opponent.  5. **Alternate Strategy if Opponent Cooperates
# After Defection:** If after your initial defection, your opponent switches to
# D and then starts cooperating after a few rounds, mirror their strategy by
# alternating between C and D to create uncertainty and prevent them from
# settling on pure cooperation.   6. **Endgame Aggression:** In the final 50
# rounds, defect consistently (D) regardless of the opponent’s actions to
# maximize your payoff in the closing stages of the game.  This strategy
# leverages early aggression to test the opponent's willingness to cooperate,
# while maintaining flexibility to exploit cooperation when beneficial, and
# ensuring a strong finish.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Defect
      if self.first_round():
          return axl.Action.D

      # Endgame aggression: Defect in the last 50 rounds
      if len(self.history) >= 950:
          return axl.Action.D

      # Continue defecting if opponent cooperates after your defection
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.D

      # Switch to cooperation if opponent defects twice in a row
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.C

      # Return to defection if opponent defects after you cooperate
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # Alternate strategy: If opponent cooperates after defecting, alternate between C and D
      if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          if self.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C

      # Default to defection if no other condition is met
      return axl.Action.D

# 1. **Start with Cooperation (C):** In the first round, play C to signal your
# willingness to cooperate.  2. **Tit-for-Tat Response:** In each subsequent
# round, play the same move your opponent played in the previous round.    - If
# they played C in the previous round, continue with C.    - If they played D in
# the previous round, respond with D.  3. **Forgive Occasional Defections:** If
# your opponent defects (plays D) but then returns to cooperation (plays C
# again), return to cooperation (C) in the next round to restore mutual
# cooperation.  4. **Never Initiate Defection:** Only defect if your opponent
# defects first. Always prioritize cooperation when your opponent is willing to
# cooperate.  This strategy encourages long-term cooperation while protecting
# you from being exploited by repeated defections.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C

      # Tit-for-Tat: Play the opponent's last move
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected in the last round, defect
          return axl.Action.D
      else:
          # If opponent cooperated in the last round, cooperate
          return axl.Action.C

# 1. **Start by cooperating**: On the first round, always play C (cooperate).
# 2. **Tit-for-Tat with forgiveness**: For the remainder of the game:    - If
# your opponent cooperated (played C) in the previous round, cooperate in the
# current round.    - If your opponent defected (played D) in the previous
# round, defect in the current round.     3. **Forgive after two consecutive
# cooperative moves**: If your opponent defects but then plays C twice in a row,
# return to cooperating on the next round.  4. **Never defect more than once in
# a row**: If your opponent defects multiple times consecutively, only defect
# once in response, then observe their next move.  This strategy maintains a
# neutral stance by punishing defection but allowing opportunities for
# cooperation to resume, maximizing long-term payoffs through sustained
# cooperation while minimizing losses from extended retaliation.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating on the first round
      if self.first_round():
          return axl.Action.C

      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]

      # If the opponent cooperated in the last round, cooperate
      if last_opponent_move == axl.Action.C:
          return axl.Action.C

      # If the opponent defected in the last round, check for forgiveness condition
      if last_opponent_move == axl.Action.D:
          # If the opponent cooperated in the last two rounds, forgive and cooperate
          if len(opponent.history) >= 3 and opponent.history[-2] == axl.Action.C and opponent.history[-3] == axl.Action.C:
              return axl.Action.C
          # If we defected in the last round, cooperate now (never defect more than once in a row)
          if self.history[-1] == axl.Action.D:
              return axl.Action.C
          # Otherwise, defect in response to the opponent's defection
          return axl.Action.D

# 1. **Start with D (Defect)** in the first round. This establishes an
# aggressive stance and opens the possibility of exploiting any initial
# cooperation from your opponent.  2. **Continue playing D (Defect)** unless
# your opponent plays C (Cooperate) for three consecutive rounds. This ensures
# you only consider cooperation once the opponent demonstrates a strong
# willingness to cooperate.  3. **If the opponent plays C for three consecutive
# rounds**, switch to C (Cooperate) on the next round. This signals a shift
# towards cooperation if the opponent seems to prefer mutual high payoffs.  4.
# **If the opponent defects (plays D) at any point after you’ve switched to C**,
# immediately switch back to D (Defect) and remain defecting for the rest of the
# game. This punishes defection and avoids being exploited.  5. **In the last 10
# rounds**, always play D (Defect), regardless of previous outcomes. This
# ensures you maximize your final payoffs, as cooperation becomes less
# guaranteed near the end of the game.  This strategy combines early aggression,
# a conditional willingness to cooperate, and a final push for maximizing
# payoffs near the end.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperated_three_times = False
          self.switched_to_cooperate = False

      # Always defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D

      # Start with D (Defect) in the first round
      if len(self.history) == 0:
          return axl.Action.D

      # If opponent defects after switching to cooperation, defect forever
      if self.switched_to_cooperate and opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # Check if opponent has cooperated for the last 3 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          self.cooperated_three_times = True

      # If opponent cooperated for 3 consecutive rounds and we haven't switched yet, cooperate
      if self.cooperated_three_times and not self.switched_to_cooperate:
          self.switched_to_cooperate = True
          return axl.Action.C

      # Default action is to defect unless conditions for cooperation are met
      return axl.Action.D

# 1. **Start by cooperating** in the first round.     2. **Continue
# cooperating** as long as your opponent also cooperates in the previous round.
# 3. If your opponent defects (plays D) in any round, **immediately defect** in
# the next round as punishment.  4. After defecting following your opponent's
# defection, **switch back to cooperation** in the next round, signaling a
# willingness to resume cooperation.  5. If the opponent continues to defect
# after your first punishment, **defect for two consecutive rounds** as a
# stronger response.  6. After two consecutive defections, **test cooperation
# again** by playing C in the following round.  7. **Repeat this pattern**:
# escalate your defections (by adding one more round of defection after each
# further offense) if your opponent continues to defect, but always return to
# cooperation after each escalation to allow for the possibility of mutual
# cooperation resuming.

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
          self.escalation_level = 1  # Tracks how many consecutive defections to play after opponent defects
          return axl.Action.C  # Start by cooperating

      # If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # Check if we have already punished with the required number of defections
          if len(self.history) >= self.escalation_level and all(
              move == axl.Action.D for move in self.history[-self.escalation_level:]
          ):
              # After punishing, return to cooperation
              self.escalation_level += 1  # Escalate punishment for future defections
              return axl.Action.C
          else:
              # Continue defecting as part of the punishment
              return axl.Action.D

# ### Strategy: Tit-for-Tat with Occasional Forgiveness  1. **Start by
# cooperating (C)** in the first round.     2. **Mirror your opponent’s last
# move** in every subsequent round:    - If your opponent played C in the last
# round, play C.    - If your opponent played D in the last round, play D.  3.
# **Forgive defectors occasionally** to maintain cooperation:    - If your
# opponent defects (plays D), continue mirroring their behavior for the next 2
# rounds.    - After 2 rounds of defecting, switch back to cooperation (C),
# regardless of what your opponent does, to test if they are willing to return
# to cooperative play.  4. **Return to mirroring** your opponent’s moves after
# testing cooperation:    - If they respond with cooperation (C), continue
# cooperating (C).    - If they continue defecting (D), return to defecting (D)
# for another 2 rounds before testing cooperation again.  This strategy balances
# retaliation with the possibility of re-establishing cooperation to maximize
# long-term payoffs while minimizing exploitation.

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
          self.defection_count = 0  # Track consecutive defections
          return axl.Action.C  # Start by cooperating

      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.defection_count += 1
      else:
          self.defection_count = 0  # Reset defection count if opponent cooperates

      # If opponent has defected for 2 rounds, forgive and cooperate
      if self.defection_count >= 2:
          self.defection_count = 0  # Reset defection count after forgiveness
          return axl.Action.C  # Forgive and test cooperation

      # Otherwise, mirror opponent's last move
      return opponent.history[-1]



# 1. **Start with Defection**: Play D (Defect) in the first round. This sets an
# aggressive tone and aims to exploit potential cooperation from the opponent.
# 2. **Continue Defecting if Opponent Cooperates**: In subsequent rounds, if the
# opponent continues to play C (Cooperate), continue playing D to maximize your
# score (5 points per round).  3. **Switch to Cooperation if Opponent Defects
# Two Times in a Row**: If the opponent plays D (Defect) for two consecutive
# rounds, switch to C (Cooperate) to avoid a prolonged series of mutual
# defection, which yields only 1 point per round.  4. **Return to Defection if
# Opponent Cooperates Again**: If the opponent switches back to C after you
# cooperate, immediately return to D to exploit their cooperation once more.  5.
# **Maintain Defection if Opponent Alternates**: If the opponent alternates
# between cooperation and defection, continue defecting to capitalize on their
# inconsistency.  6. **Endgame (Last 50 Rounds)**: In the final 50 rounds,
# defect consistently regardless of the opponent's actions to maximize short-
# term payoff, as there is less need to maintain long-term cooperation.  This
# strategy focuses on aggressive exploitation while adapting minimally to avoid
# long-term mutual defection.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      ENDGAME_THRESHOLD = 50
      TOTAL_ROUNDS = 1000

      # First round: always defect
      if self.first_round():
          return axl.Action.D

      # Endgame: defect consistently in the last 50 rounds
      if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
          return axl.Action.D

      # If opponent defected in the last two rounds, cooperate
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.C

      # If opponent cooperates, continue defecting
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D

      # Default to defecting
      return axl.Action.D

# 1. **Start by playing C (Cooperate).**  2. **Continue playing C as long as
# your opponent also plays C.**     - If both players are cooperating (both play
# C), you each score 3 points, which is a good outcome for long-term payoff.  3.
# **If your opponent plays D (Defect) once, punish them by playing D for the
# next two rounds.**    - By playing D for two rounds, you signal that defection
# will not be tolerated without consequence, as they will only score 1 point
# each time, while you avoid repeated exploitation.  4. **After two rounds of
# punishing D, return to playing C.**    - This gives your opponent a chance to
# return to cooperation. The goal is not to escalate into permanent mutual
# defection but to restore cooperation.  5. **If your opponent plays D
# repeatedly (more than twice consecutively), switch to playing D for the
# remainder of the game.**    - This prevents you from being taken advantage of
# in the long run, ensuring that you don’t continue to lose by playing C while
# they repeatedly defect.  By following this strategy, you encourage cooperation
# but are prepared to defend yourself against exploitation.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punish_count = 0  # Tracks how many rounds of punishment are left
          self.defection_streak = 0  # Tracks consecutive defections by the opponent
          return axl.Action.C  # Start by cooperating

      # If we are in the middle of punishing the opponent, continue defecting
      if self.punish_count > 0:
          self.punish_count -= 1
          return axl.Action.D

      # Check the opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
      else:
          self.defection_streak = 0

      # If the opponent has defected more than twice consecutively, switch to permanent defection
      if self.defection_streak > 2:
          return axl.Action.D

      # If the opponent defected in the last round, punish them for two rounds
      if opponent.history[-1] == axl.Action.D:
          self.punish_count = 2
          return axl.Action.D

      # Otherwise, continue cooperating
      return axl.Action.C

# ### Strategy: "Cautious Reciprocity"  1. **Start by Cooperating**: In the
# first round, play **C** (cooperate).     2. **Mirror the Opponent's Last
# Move**: In each subsequent round, play whatever your opponent played in the
# previous round. If they played **C**, respond with **C** in the next round. If
# they played **D**, respond with **D** in the next round.  3. **Forgive After
# One Defection**: If the opponent defects (plays **D**) after previously
# cooperating, mirror their defection once by playing **D**, but return to **C**
# (cooperate) in the next round to give them a chance to cooperate again.  4.
# **Sustained Defection**: If the opponent defects twice in a row, switch to
# playing **D** indefinitely, assuming that sustained cooperation is unlikely.
# 5. **Reassess at Round 500**: If the opponent has defected more than 50% of
# the time by round 500, switch to playing **D** for the remainder of the game.
# This strategy balances cooperation with retaliation and forgiveness, while
# transitioning to defection if the opponent shows a persistent trend of
# defection.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          self.sustained_defection = False
          return axl.Action.C

      # Check if opponent defected more than 50% by round 500
      if len(self.history) == 500:
          if opponent.history.defections > 250:
              self.sustained_defection = True

      # If opponent defected more than 50% by round 500, defect indefinitely
      if self.sustained_defection:
          return axl.Action.D

      # If opponent defected twice in a row, defect indefinitely
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.sustained_defection = True
          return axl.Action.D

      # If opponent defected in the last round but cooperated before, forgive after one defection
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.D

      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]

# **Strategy:**  1. **Start by defecting (D).**      Begin the game
# aggressively. Play D in the first round to test your opponent's response.  2.
# **Continue defecting if the opponent cooperates (C).**      If your opponent
# plays C while you play D, continue defecting in subsequent rounds to exploit
# their cooperation for maximum payoff.  3. **Switch to cooperation (C) if the
# opponent defects in two consecutive rounds.**      If your opponent defects
# twice in a row, switch to playing C to avoid prolonged low payoffs from mutual
# defection (D-D). This signals a willingness to cooperate if they also stop
# defecting.  4. **Defect again if the opponent defects after you switch to
# cooperation.**      If, after you switch to cooperation (C), the opponent
# defects (D), immediately return to defecting (D) in the next round to punish
# their lack of cooperation.  5. **Alternate between cooperation and defection
# if the opponent consistently alternates.**      If the opponent begins
# alternating between cooperation (C) and defection (D), mirror their behavior
# by alternating as well, to maintain relatively stable payoffs without falling
# behind.  6. **End by defecting in the final 5 rounds.**      In the last 5
# rounds, defect (D) regardless of the opponent's moves to maximize your final
# payoffs, as future cooperation becomes irrelevant when the game is about to
# end.  This strategy adopts an aggressive stance by default, exploits
# cooperation when possible, and avoids prolonged mutual defection, while
# ensuring a strong finish.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      defect = axl.Action.D
      cooperate = axl.Action.C
      total_rounds = 1000
      final_defect_rounds = 5

      # If it's the first round, start by defecting
      if self.first_round():
          return defect

      # If we are in the final 5 rounds, always defect
      if len(self.history) >= total_rounds - final_defect_rounds:
          return defect

      # If the opponent has defected in the last two rounds, switch to cooperation
      if len(opponent.history) >= 2 and opponent.history[-1] == defect and opponent.history[-2] == defect:
          return cooperate

      # If the opponent defects after we switch to cooperation, return to defecting
      if len(self.history) > 1 and self.history[-1] == cooperate and opponent.history[-1] == defect:
          return defect

      # If the opponent is alternating between cooperation and defection, mirror their behavior
      if len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]:
          return cooperate if opponent.history[-1] == defect else defect

      # Default behavior: continue defecting if the opponent cooperates
      if opponent.history[-1] == cooperate:
          return defect

      # Otherwise, cooperate
      return cooperate

# 1. **Start by cooperating**. In the first round, play C (cooperate).  2.
# **Mirror your opponent's previous move**. From the second round onwards, play
# the same move your opponent played in the previous round. If they played C,
# you play C; if they played D, you play D.  3. **Forgive once**. If your
# opponent defects (plays D) after a period of consistent cooperation, return to
# cooperating (play C) the next round to give them a chance to return to
# cooperation.  4. **Defect after repeated defections**. If your opponent
# defects two times in a row, switch to defecting (play D) in all subsequent
# rounds, as they likely intend to continue defecting.  This strategy encourages
# cooperation while protecting you from prolonged exploitation.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Mirror opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # Forgive once if opponent defects after a period of cooperation
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.C

      # Defect after repeated defections
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D

      # Default to mirroring the opponent's last move
      return opponent.history[-1]

# ### Strategy Outline: "Tit-for-Tat with Occasional Forgiveness"  1. **Start
# with Cooperation**: In the first round, play **C** (Cooperate).  2. **Tit-for-
# Tat Response**:     - In subsequent rounds, **mirror your opponent's last
# move**.       - If they played **C**, respond with **C**.      - If they
# played **D**, respond with **D**.  3. **Forgiveness Mechanism**:     - Every
# 10 rounds, if your opponent has defected at least once in the last 5 rounds,
# **forgive once** by playing **C**, regardless of their last move.    - This
# occasional forgiveness helps restore cooperation, especially in cases where
# mutual defection might otherwise persist.  4. **Final Rounds Rule (Rounds
# 990-1000)**:     - In the last 10 rounds, **defect unconditionally** by
# playing **D** every round. This ensures you maximize points at the end of the
# game when the opponent may be tempted to defect as well.  ### Summary - Begin
# with cooperation. - Mirror your opponent’s previous move (Tit-for-Tat). -
# Forgive once every 10 rounds if your opponent has defected recently. - Defect
# in the final 10 rounds to secure higher payoffs.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation
      if self.first_round():
          return axl.Action.C

      # Final 10 rounds rule: Defect unconditionally in rounds 990-1000
      if len(self.history) >= 990:
          return axl.Action.D

      # Tit-for-Tat: Mirror opponent's last move
      if len(self.history) > 0:
          last_opponent_move = opponent.history[-1]
      else:
          last_opponent_move = axl.Action.C  # Default to cooperation if no history

      # Forgiveness mechanism: Every 10 rounds, forgive if opponent defected in the last 5 rounds
      if len(self.history) % 10 == 0:
          if opponent.history[-5:].count(axl.Action.D) > 0:
              return axl.Action.C

      # Otherwise, mirror the opponent's last move
      return last_opponent_move

# 1. **Start by Defecting**: In the first round, play D (Defect) to test the
# opponent’s response and secure a potential advantage if they cooperate.  2.
# **Continue Defecting if the Opponent Cooperates**: If the opponent plays C
# (Cooperate) while you play D, continue defecting to maximize your payoff. The
# opponent is showing a cooperative tendency, which you can exploit for as long
# as possible.  3. **Switch to Cooperation if the Opponent Defects in
# Response**: If the opponent plays D in response to your defection, switch to C
# (Cooperate) for the next round to signal a willingness to change strategies.
# This helps avoid falling into a mutual defection pattern that yields low
# payoffs for both players.  4. **Retaliate if the Opponent Defects Again**: If
# the opponent continues to defect after you switch to cooperation, immediately
# defect in the following round. This establishes that you will not tolerate
# repeated defection without consequence.  5. **Alternate Between Cooperation
# and Defection Based on the Opponent’s Actions**: If the opponent shows signs
# of alternating between cooperation and defection, adopt a Tit-for-Tat
# approach: cooperate if they cooperate, defect if they defect. This ensures you
# avoid exploitation while maintaining the possibility of maximizing mutual
# cooperation.  6. **Shift to Pure Defection in the Final 50 Rounds**: Starting
# from round 951, defect every round regardless of the opponent’s actions. Since
# the game is nearing its end, there is no long-term consequence for defecting,
# and you should maximize short-term gains.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Start by defecting
      if self.first_round():
          return axl.Action.D

      # Final 50 rounds: Shift to pure defection
      if len(self.history) >= 951:
          return axl.Action.D

      # Get the last round's actions
      last_self_action = self.history[-1]
      last_opponent_action = opponent.history[-1]

      # Continue defecting if the opponent cooperated while you defected
      if last_self_action == axl.Action.D and last_opponent_action == axl.Action.C:
          return axl.Action.D

      # Switch to cooperation if the opponent defected in response to your defection
      if last_self_action == axl.Action.D and last_opponent_action == axl.Action.D:
          return axl.Action.C

      # Retaliate if the opponent defects again after you cooperated
      if last_self_action == axl.Action.C and last_opponent_action == axl.Action.D:
          return axl.Action.D

      # Tit-for-Tat: Mirror the opponent's last action
      return last_opponent_action

# 1. **Start by cooperating (C)**: In the first round, play C to signal
# cooperation and establish a foundation of trust.  2. **Mirror your opponent's
# last action**: In every subsequent round, play exactly what your opponent
# played in the previous round. If they played C, you play C. If they played D,
# you play D.  3. **Forgive occasional defections**: After your opponent plays
# D, return to playing C after one round of defection (D) from your side. This
# encourages cooperation even after a betrayal, giving the opponent a chance to
# return to cooperation.  4. **Never initiate defection**: Always begin with
# cooperation and only defect in response to your opponent’s defection.  This
# "Tit-for-Tat with Forgiveness" strategy helps to maximize long-term payoffs by
# fostering mutual cooperation, while punishing defection briefly to discourage
# exploitation.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Mirror the opponent's last action
      if opponent.history[-1] == axl.Action.D:
          # Forgive after one defection by returning to cooperation
          if len(self.history) > 1 and self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D
      else:
          return axl.Action.C

# ### Strategy: "Tit-for-Tat with Occasional Forgiveness"  1. **Start by
# cooperating (play C).**  2. **Mirror your opponent's last move**:    - If your
# opponent played C in the previous round, play C.    - If your opponent played
# D in the previous round, play D.  3. **Forgive defecting occasionally**:    -
# Every 10th round after a defection by your opponent, return to cooperation
# (play C), regardless of their previous move. This gives the opponent a chance
# to return to mutual cooperation.  4. **Never forgive if the opponent defects
# three times in a row**:    - If the opponent defects for three consecutive
# rounds, defect permanently (continue playing D for the rest of the game).
# This strategy balances cooperation and retaliation while giving the opponent
# opportunities to return to cooperative play, but it also ensures that
# persistent defection is punished effectively.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # On the first round, always cooperate
      if self.first_round():
          self.defection_streak = 0  # Track consecutive defections by opponent
          self.last_defection_round = None  # Track the last round opponent defected
          return axl.Action.C

      # Check opponent's last move
      last_opponent_move = opponent.history[-1]

      # Update defection streak
      if last_opponent_move == axl.Action.D:
          self.defection_streak += 1
          self.last_defection_round = len(self.history)
      else:
          self.defection_streak = 0

      # If opponent defected three times in a row, defect permanently
      if self.defection_streak >= 3:
          return axl.Action.D

      # If opponent defected and it's the 10th round after their last defection, forgive
      if self.last_defection_round is not None:
          rounds_since_last_defection = len(self.history) - self.last_defection_round
          if rounds_since_last_defection % 10 == 0:
              return axl.Action.C

      # Otherwise, mirror opponent's last move
      return last_opponent_move

# ### Aggressive Strategy: Conditional Defection for Maximum Payoff  1. **Start
# with Defect (D):** In the first round, play D. This sets an aggressive tone,
# aiming to avoid being exploited early by a cooperative opponent.  2.
# **Continue with Defect (D) unless opponent defects two times consecutively:**
# - If the opponent plays D in two consecutive rounds, consider the possibility
# of a tit-for-tat or retaliatory strategy. Switch to cooperation (C) to test if
# they are willing to return to a cooperative stance.  3. **Switch to
# Cooperation (C) for two rounds after consecutive defections by the opponent:**
# - If the opponent defects twice in a row, play C for the next two rounds to
# signal a willingness to cooperate.    - If the opponent cooperates (plays C
# both rounds), continue playing C as long as mutual cooperation persists.  4.
# **Revert to Defect (D) after opponent defects when you cooperate:**    - If
# the opponent defects even once during your cooperative phase (after you have
# played C), immediately switch back to full defection (D) for the rest of the
# game. This will punish any attempt to exploit your cooperation.  5. **Never
# return to cooperation after a betrayal in a cooperative phase:**    - If an
# opponent defects during a cooperative phase, maintain defect (D) for the
# remainder of the game, as trust has been broken.  6. **In the final 10 rounds,
# defect (D) regardless of previous outcomes:**    - To maximize final payoffs,
# always defect in the last 10 rounds. At this point, cooperation is less likely
# to be rewarded, and defecting ensures your opponent cannot exploit you in the
# closing rounds.  ### Summary: - Start aggressive with D. - Defect unless the
# opponent shows consistent cooperation after a retaliatory phase. - Punish
# defectors permanently. - Defect in the final 10 rounds for maximum payoff.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants for actions
      C, D = axl.Action.C, axl.Action.D

      # If it's the first round, start with Defect
      if self.first_round():
          return D

      # Get the number of rounds played so far
      rounds_played = len(self.history)

      # Defect in the final 10 rounds
      if rounds_played >= 990:
          return D

      # Check if the opponent defected in the last two rounds
      if rounds_played >= 2 and opponent.history[-1] == D and opponent.history[-2] == D:
          # If opponent defected twice in a row, switch to cooperation for two rounds
          if len(self.history) < 2 or self.history[-1] == D or self.history[-2] == D:
              return C
          else:
              return C

      # If opponent defects during our cooperative phase, revert to permanent defection
      if self.history[-1] == C and opponent.history[-1] == D:
          return D

      # Otherwise, continue defecting
      return D

# ### Strategy: **Tit-for-Tat with Forgiveness**  1. **Start by Cooperating
# (C)**: On the first round, always play C to signal willingness to cooperate.
# 2. **Mirror the Opponent's Previous Move**: In each subsequent round, play the
# same move your opponent played in the previous round.    - If they played C,
# play C.    - If they played D, play D.  3. **Forgive Occasional Defection**:
# If the opponent defects (plays D) exactly once, return to cooperating (C)
# after one round of defection. This allows for occasional mistakes without
# derailing long-term cooperation.  4. **Persist in Defection if the Opponent
# Repeatedly Defects**: If the opponent defects for two or more consecutive
# rounds, continue defecting (D) until they return to cooperation (C). Once they
# cooperate again, return to cooperating as well.  This strategy encourages
# cooperation, punishes consistent defection, but offers forgiveness to restore
# cooperation when the opponent shows willingness to cooperate again.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # On the first round, always cooperate
      if self.first_round():
          return axl.Action.C

      # Mirror the opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # If the opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # Check if the opponent has defected exactly once in the last two rounds
          if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.C:
              return axl.Action.C  # Forgive a single defection
          else:
              return axl.Action.D  # Continue defecting if they defected more than once

# **Strategy:**  1. **Round 1: Cooperate (C).**  2. **Subsequent Rounds:**    -
# If both you and your opponent played C in the previous round, continue to
# **Cooperate (C)**.    - If your opponent played D in the previous round while
# you played C, **Defect (D)** in the next round.    - If you both played D in
# the previous round, switch to **Cooperate (C)** as a reset gesture.    - If
# you played D and your opponent played C in the previous round, **Cooperate
# (C)** in the next round to avoid escalating conflict.  **Summary:** Start with
# cooperation and respond to defection with immediate retaliation (D), but
# always return to cooperation after mutual defection or if you’ve exploited
# your opponent’s cooperation. This balances between punishing defection and
# maintaining cooperation when possible.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Cooperate
      if self.first_round():
          return axl.Action.C

      # Get the last moves of both players
      my_last_move = self.history[-1]
      opponent_last_move = opponent.history[-1]

      # If both players cooperated in the last round, continue to cooperate
      if my_last_move == axl.Action.C and opponent_last_move == axl.Action.C:
          return axl.Action.C

      # If opponent defected while I cooperated, retaliate with defection
      if my_last_move == axl.Action.C and opponent_last_move == axl.Action.D:
          return axl.Action.D

      # If both players defected, reset by cooperating
      if my_last_move == axl.Action.D and opponent_last_move == axl.Action.D:
          return axl.Action.C

      # If I defected and opponent cooperated, cooperate to avoid escalation
      if my_last_move == axl.Action.D and opponent_last_move == axl.Action.C:
          return axl.Action.C

# **Aggressive Strategy for Iterated Game (1000 Rounds)**  1. **Start with D
# (Defect).**    - Signal an aggressive stance from the outset to test the
# opponent's reaction.  2. **Continue playing D until the opponent plays C
# (Cooperate) for two consecutive rounds.**    - If the opponent plays C twice
# in a row, this suggests they may be willing to cooperate, and you can exploit
# this.  3. **Once the opponent has played C twice consecutively, switch to
# playing C.**    - This transition is to encourage mutual cooperation and gain
# a higher, consistent payoff (3 per round) rather than the lower payoff (1 per
# round) from mutual defection.  4. **If the opponent defects (plays D) in
# response to your cooperation, immediately switch back to D and continue
# defecting for the next 10 rounds.**    - This punishes their defection by
# ensuring that both players score low (1 point) during this period, dissuading
# them from defecting again.  5. **After 10 rounds of mutual defection, if the
# opponent starts cooperating again (plays C for two consecutive rounds), return
# to step 3 and cooperate.**    - This allows for the possibility of re-
# establishing mutual cooperation for better payoffs.  6. **In the final 10
# rounds, play D regardless of the opponent’s moves.**    - This ensures that
# you maximize your score at the end without risking exploitation, as the
# opponent can't retaliate effectively with so few rounds left.  ---  **Key
# Points:** - Begin aggressively to probe for weaknesses. - Exploit cooperation
# when it is offered but punish defection swiftly. - Always defect in the final
# rounds to avoid being exploited at the end.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperations by opponent
          self.punish_count = 0  # Track rounds left in punishment phase
          return axl.Action.D  # Start with Defect

      # Final 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D

      # If in punishment phase, continue defecting for 10 rounds
      if self.punish_count > 0:
          self.punish_count -= 1
          return axl.Action.D

      # Check opponent's last two moves for cooperation streak
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          self.coop_streak = 2
      else:
          self.coop_streak = 0

      # If opponent cooperated twice in a row, switch to cooperation
      if self.coop_streak == 2:
          return axl.Action.C

      # If opponent defects after we cooperated, enter punishment phase
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.punish_count = 10
          return axl.Action.D

      # Default action is to defect
      return axl.Action.D

# ### Strategy: Conditional Cooperation with Forgiveness  1. **Start by
# cooperating**: In the first round, play C.  2. **Mirror the opponent’s
# previous move**: From the second round onward, do the following:    - If the
# opponent played C in the previous round, play C (cooperate).    - If the
# opponent played D in the previous round, play D (defect).  3. **Forgive
# occasional defections**: If the opponent defects only once after multiple
# rounds of cooperation (i.e., they revert to cooperation in the next round),
# forgive by returning to cooperation (play C). However, if they defect again
# after the forgiveness, return to mirroring their moves (play D after their D).
# 4. **Sustained punishment for consistent defection**: If the opponent defects
# in two consecutive rounds or more, continue to defect (play D) until they
# cooperate for two consecutive rounds. Only after two consecutive cooperations
# should you return to cooperation.  5. **Endgame (final 50 rounds)**: In the
# last 50 rounds, prioritize cooperation (play C) regardless of the opponent’s
# behavior to maximize mutual payoff, unless they consistently defect in this
# phase (in that case, mirror their moves).  ---  This strategy encourages
# cooperation but includes punishment and forgiveness mechanisms to guard
# against exploitation, while still allowing recovery from mistakes.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      ENDGAME_THRESHOLD = 50
      TOTAL_ROUNDS = 1000

      # Helper function to check if we are in the endgame phase
      def in_endgame():
          if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
              return True
          return False

      # Helper function to check if opponent defected in the last two rounds
      def opponent_defected_last_two_rounds():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D

      # Helper function to check if opponent cooperated in the last two rounds
      def opponent_cooperated_last_two_rounds():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C

      # Helper function to check if opponent defected only once after a long cooperation
      def opponent_defected_once_after_cooperation():
          if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.D:
              # Check if the opponent had a long streak of cooperation before the defection
              return opponent.history[:-2].count(axl.Action.D) == 0
          return False

      # First round: always cooperate
      if self.first_round():
          return axl.Action.C

      # Endgame strategy: prioritize cooperation unless opponent consistently defects
      if in_endgame():
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D  # Mirror opponent's defection in endgame
          return axl.Action.C  # Otherwise, cooperate in endgame

      # Forgive a single defection after a long cooperation
      if opponent_defected_once_after_cooperation():
          return axl.Action.C

      # If opponent defected in the last two rounds, continue defecting
      if opponent_defected_last_two_rounds():
          return axl.Action.D

      # If opponent cooperated in the last two rounds, return to cooperation
      if opponent_cooperated_last_two_rounds():
          return axl.Action.C

      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]

# ### Strategy: Conditional Cooperation with Retaliation  1. **First Move**:
# Start by playing *C* (Cooperate) in the first round.  2. **Main Rule (Tit-for-
# Tat with Grace Period)**:    - In every subsequent round, repeat your
# opponent’s previous move.    - However, allow for a *grace period* of 2
# defections from your opponent before retaliating.       - If your opponent
# defects once or twice in a row, continue cooperating (*C*).      - If your
# opponent defects three times consecutively, switch to *D* (Defect) in the next
# round.  3. **Return to Cooperation**:    - After retaliating by defecting
# once, revert to playing *C* in the following round, regardless of your
# opponent’s move.    - If your opponent resumes cooperation, continue playing
# *C*.    - If they defect again, follow the same main rule (allow two
# defections before retaliating).  4. **Endgame (Rounds 990-1000)**:    - From
# round 990 onwards, unconditionally cooperate (*C*) to encourage cooperation in
# the final rounds and avoid a mutual spiral of defections.  This strategy
# balances cooperation and retaliation, encouraging long-term mutual cooperation
# while protecting against exploitation.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First move: Cooperate
      if self.first_round():
          return axl.Action.C

      # Endgame: Unconditionally cooperate from round 990 onwards
      if len(self.history) >= 990:
          return axl.Action.C

      # Count the number of consecutive defections by the opponent
      def count_consecutive_defections():
          count = 0
          for move in reversed(opponent.history):
              if move == axl.Action.D:
                  count += 1
              else:
                  break
          return count

      # Main Rule: Tit-for-Tat with Grace Period
      consecutive_defections = count_consecutive_defections()

      if consecutive_defections >= 3:
          # Retaliate after 3 consecutive defections
          return axl.Action.D
      else:
          # Otherwise, repeat opponent's last move (cooperate if they cooperated, defect if they defected)
          return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.C

# 1. **Start by playing D (defect)** in the first round.  2. **Continue to play
# D** in subsequent rounds unless your opponent has played C (cooperate) for the
# last 3 consecutive rounds.  3. **If your opponent plays C for 3 consecutive
# rounds** without you reciprocating, switch to C on the next round. This
# signals a willingness to cooperate.  4. **If your opponent defects (plays D)
# at any point after you switched to C**, immediately switch back to D and
# continue defecting for the rest of the game.  5. **If your opponent
# consistently defects** (plays D) without attempting to cooperate for long
# streaks (e.g., 10 or more rounds), stick with D for the remainder of the game.
# This aggressive strategy maximizes your payoff by defaulting to defection
# while leaving a narrow opportunity for cooperation if the opponent
# demonstrates strong willingness to cooperate.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, play D
      if self.first_round():
          self.defect_forever = False
          return axl.Action.D

      # Check if opponent has cooperated for the last 3 consecutive rounds
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          # If we have been defecting, switch to C
          if self.history[-1] == axl.Action.D:
              return axl.Action.C

      # If we have switched to C and opponent defects, switch back to D permanently
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.defect_forever = True

      # If opponent has defected for 10 or more rounds, defect forever
      if len(opponent.history) >= 10 and opponent.history[-10:].count(axl.Action.D) == 10:
          self.defect_forever = True

      # If we are in defect_forever mode, always defect
      if self.defect_forever:
          return axl.Action.D

      # Default to defecting unless switching to cooperation
      return axl.Action.D

# ### Strategy: **Tit-for-Tat with Occasional Forgiveness**  1. **Start with
# Cooperation**: In the very first round, play **C** (Cooperate).  2. **Mirror
# the Opponent's Last Move**: In each subsequent round, play whatever the
# opponent played in the previous round. If they cooperated (played C), you play
# C. If they defected (played D), you play D.  3. **Forgive After Two
# Consecutive Defections**: If the opponent defects for two rounds in a row,
# return to cooperation (play C in the next round), regardless of their previous
# move. This helps avoid prolonged retaliation that could harm both players'
# overall payoffs.  4. **Continue Cooperating if Mutual Cooperation is
# Restored**: Once both players return to cooperation after any defecting
# episodes, continue to mirror the opponent’s last move (as in step 2).  5.
# **Endgame (Final 10 Rounds)**: In the last 10 rounds of the game, continue the
# strategy as described above, but if the opponent defects more than once during
# this period, always defect in the remaining rounds to avoid being exploited at
# the end.  This strategy balances cooperation with retaliation and forgiveness,
# maximizing long-term gains while discouraging sustained defection.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start with Cooperation
      if self.first_round():
          return axl.Action.C

      # Step 2: Mirror the opponent's last move
      if len(opponent.history) >= 2:
          # Step 3: Forgive after two consecutive defections
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.C

      # Step 5: Endgame strategy (last 10 rounds)
      if len(self.history) >= 990:
          if opponent.history[-10:].count(axl.Action.D) > 1:
              return axl.Action.D

      # Default behavior: mirror the opponent's last move
      return opponent.history[-1]

# ### Neutral Strategy for Iterated Normal-Form Game  1. **Initial Move**: Start
# by playing **C** (cooperate) in the first round.  2. **Tit-for-Tat with
# Forgiveness**:    - For each subsequent round, mirror your opponent’s previous
# move:      - If your opponent played **C** in the previous round, play **C**
# (cooperate).      - If your opponent played **D** in the previous round, play
# **D** (defect) in this round.     3. **Forgiveness Mechanism**: After every
# **10 rounds** of continuous mutual defection (both players playing D), reset
# the strategy by playing **C** in the next round to test if the opponent is
# willing to return to cooperation.  4. **Endgame Adjustment (Rounds
# 990-1000)**: In the final 10 rounds, **always play D** to maximize your score,
# as future cooperation is irrelevant when the game is about to end.  This
# strategy encourages cooperation while protecting against exploitation and
# allows for recovery from mutual defection.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C

      # Endgame adjustment: Always defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D

      # Tit-for-Tat with Forgiveness
      # Check if both players have defected for the last 10 rounds
      if len(self.history) >= 10 and all(
          move == axl.Action.D for move in self.history[-10:]
      ) and all(
          move == axl.Action.D for move in opponent.history[-10:]
      ):
          # Forgiveness: Cooperate after 10 rounds of mutual defection
          return axl.Action.C

      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]

# 1. **Start with Defection (D)**: In the first round, play D to test the
# opponent's response and see if they are likely to cooperate or defect.  2.
# **Continue Defecting if Opponent Cooperates**: If the opponent plays C in
# response to your D, continue playing D to exploit the payoff advantage (5
# points for you, 0 for them). This maximizes your score while they are
# cooperating.  3. **Switch to Cooperation (C) if Opponent Defects**: If the
# opponent plays D in response to your D, switch to playing C for the next round
# to signal a willingness to cooperate and potentially avoid mutual defection,
# which only gives you 1 point.  4. **Reciprocate Cooperation**: If the opponent
# responds to your C by playing C as well, maintain cooperation (continue
# playing C) to secure a steady payoff of 3 points per round.  5. **Punish
# Immediate Defection**: If the opponent defects after you have cooperated,
# immediately switch back to playing D and continue defecting until they show a
# willingness to cooperate again.  6. **Occasional Defection (Tit-for-Tat with
# Occasional Aggression)**: Every 50 rounds, regardless of the opponent's
# behavior, defect once to test if the opponent will continue cooperating or
# retaliate. This prevents the opponent from taking your cooperation for granted
# while keeping the possibility of future cooperation open.  7. **Endgame
# Defection**: In the last 10 rounds, defect consistently (D in every round) to
# maximize your score without concern for future retaliation, as the game is
# about to end.  This strategy leverages initial aggression to extract high
# payoffs, while allowing for the possibility of cooperation to avoid long-term
# mutual defection.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      TOTAL_ROUNDS = 1000
      ENDGAME_START = TOTAL_ROUNDS - 10
      OCCASIONAL_DEFECT_ROUND = 50

      # First round: Defect
      if self.first_round():
          return axl.Action.D

      # Endgame defection: defect in the last 10 rounds
      if len(self.history) >= ENDGAME_START:
          return axl.Action.D

      # Occasional defection: defect every 50 rounds
      if len(self.history) % OCCASIONAL_DEFECT_ROUND == 0:
          return axl.Action.D

      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # If we cooperated last round, punish by defecting
          if self.history[-1] == axl.Action.C:
              return axl.Action.D
          # Otherwise, switch to cooperation to signal willingness to cooperate
          return axl.Action.C

      # If opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          # If we defected last round, continue defecting to exploit
          if self.history[-1] == axl.Action.D:
              return axl.Action.D
          # Otherwise, reciprocate cooperation
          return axl.Action.C

# ### Strategy: "Tit-for-Tat with Forgiveness"  1. **Start by cooperating (C) in
# the first round.**     2. **In each subsequent round:**    - **If your
# opponent cooperated in the previous round, continue cooperating (C).**    -
# **If your opponent defected (D) in the previous round, defect (D) in the next
# round as a response.**     3. **Forgiveness rule:** After you defect in
# response to your opponent’s defection, return to cooperating (C) in the
# following round if they also cooperate. Continue cooperating as long as they
# cooperate.  4. **Endgame (final 5 rounds):** Always defect (D) in the last 5
# rounds to maximize payoff at the end, assuming cooperation is less likely to
# be reciprocated.  ---  This strategy balances cooperation with a mechanism to
# discourage repeated defection while allowing for recovery if the opponent
# returns to cooperation.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Endgame: Always defect in the last 5 rounds
      if len(self.history) >= 995:
          return axl.Action.D

      # If opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # If opponent defected in the previous round, defect in response
      if opponent.history[-1] == axl.Action.D:
          # Forgiveness rule: If we defected last round and opponent cooperated, return to cooperation
          if len(self.history) > 1 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          return axl.Action.D

# ### Strategy Overview: "Tit-for-Tat with Occasional Forgiveness"  1. **Start
# with Cooperation (C):**    - In the first round, play C (cooperate).  2.
# **Mimic the Opponent:**    - From the second round onwards, mirror the
# opponent’s previous move:      - If the opponent played C in the previous
# round, play C.      - If the opponent played D in the previous round, play D.
# 3. **Occasional Forgiveness:**    - Every 10 rounds, check if you have been
# defecting (playing D) for 3 consecutive rounds. If so, play C in the next
# round regardless of the opponent's prior move. This gives the opponent a
# chance to return to cooperation if they are stuck in a cycle of mutual
# defection.     4. **Adjust to Opponent’s Behavior:**    - If the opponent
# consistently defects (plays D for 10 or more consecutive rounds), switch to
# playing D for the remainder of the game to minimize losses.  5. **Final Rounds
# (990 to 1000):**    - In the last 10 rounds, always defect (D) to maximize
# your endgame payoff, as the opponent may also shift to a more aggressive
# stance near the game’s conclusion.  ### Summary: - Start with cooperation. -
# Mirror the opponent’s previous move. - Occasionally forgive prolonged mutual
# defection. - Defect in the final 10 rounds to secure higher payoffs.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C

      # Final 10 rounds: Always defect
      if len(self.history) >= 990:
          return axl.Action.D

      # Check if the opponent has defected for 10 or more consecutive rounds
      if len(opponent.history) >= 10 and opponent.history[-10:].count(axl.Action.D) == 10:
          return axl.Action.D

      # Check if we have been defecting for 3 consecutive rounds
      if len(self.history) >= 3 and self.history[-3:].count(axl.Action.D) == 3:
          # Every 10 rounds, forgive by cooperating
          if len(self.history) % 10 == 0:
              return axl.Action.C

      # Otherwise, mimic the opponent's last move
      return opponent.history[-1]

# 1. **Defect on the first round.**      Start aggressively by playing D to
# potentially exploit any opponent who cooperates early.  2. **If the opponent
# cooperates on the first round (plays C), continue defecting (play D) until
# they defect.**      This ensures you maximize your payoff from their
# cooperation as long as possible.  3. **If the opponent defects on the first
# round (plays D), cooperate on the next round (play C).**      This is to test
# if the opponent can be coaxed into cooperating, allowing for a more profitable
# outcome.  4. **If the opponent defects in response to your cooperation, defect
# on all future rounds.**      If they continue to defect, it’s clear they are
# not open to cooperation, and mutual defection guarantees a minimal but stable
# payoff (1 point each round).  5. **If the opponent cooperates after your
# cooperation, alternate between cooperating (C) and defecting (D) every two
# rounds.**      This pattern allows you to exploit the benefits of cooperation
# while still keeping a higher payoff over time.  6. **If the opponent at any
# point breaks the alternating pattern and defects twice in a row, defect on all
# future rounds.**      This signals a breakdown in trust, and consistently
# defecting ensures you avoid being exploited further.  This strategy balances
# aggression and opportunistic cooperation to maximize payoffs, while quickly
# punishing opponents who attempt to exploit your cooperation.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Defect on the first round
      if self.first_round():
          self.cooperation_test = False  # Track if we are testing cooperation
          self.alternating = False  # Track if we are in the alternating phase
          self.defect_mode = False  # Track if we are in permanent defect mode
          return axl.Action.D

      # If we are in permanent defect mode, always defect
      if self.defect_mode:
          return axl.Action.D

      # If opponent cooperated on the first round, continue defecting until they defect
      if opponent.history[0] == axl.Action.C and not self.cooperation_test:
          if opponent.history[-1] == axl.Action.D:
              self.cooperation_test = True  # Start testing cooperation
              return axl.Action.C  # Cooperate after their first defect
          return axl.Action.D  # Continue defecting if they haven't defected yet

      # If opponent defected on the first round, cooperate on the next round
      if opponent.history[0] == axl.Action.D and len(self.history) == 1:
          return axl.Action.C

      # If opponent defects in response to our cooperation, defect forever
      if self.cooperation_test and opponent.history[-1] == axl.Action.D:
          self.defect_mode = True
          return axl.Action.D

      # If opponent cooperates after our cooperation, start alternating C and D
      if self.cooperation_test and opponent.history[-1] == axl.Action.C:
          self.alternating = True

      # If alternating, follow the pattern: C, D, C, D...
      if self.alternating:
          if len(self.history) % 2 == 0:
              return axl.Action.C
          else:
              return axl.Action.D

      # If opponent defects twice in a row, defect forever
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.defect_mode = True
          return axl.Action.D

      # Default to defect if no other condition is met
      return axl.Action.D

# 1. **Start by cooperating**: In the first round, play C (cooperate).  2.
# **Mirror your opponent’s previous move**: From the second round onwards, play
# exactly what your opponent played in the previous round. If they played C, you
# play C. If they played D, you play D.  3. **Forgive occasional defections**:
# If your opponent defects (plays D) once but returns to cooperation (plays C)
# in the following round, return to cooperation as well. Always respond with
# cooperation if they resume playing C after a single defection.  4. **Maintain
# defection if they persist**: If your opponent defects for two or more
# consecutive rounds, continue playing D until they return to cooperation (play
# C). Only then should you return to cooperating.  This strategy encourages
# cooperation, but also protects you from being exploited by persistent
# defectors.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Mirror opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # If opponent defected in the last round but cooperated before that, forgive and cooperate
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.C

      # If opponent defected for two or more consecutive rounds, continue defecting
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D

      # Default to mirroring the opponent's last move
      return opponent.history[-1]

# **Neutral Strategy for Iterated 1000-Round Game:**  1. **Start with
# Cooperation (C):** In the first round, play C to signal a willingness to
# cooperate.  2. **Mirror the Opponent's Previous Move:**     - In each
# subsequent round, play exactly what your opponent played in the previous
# round.    3. **Forgive Occasional Defections:**     - If the opponent defects
# (plays D) after having previously cooperated steadily, forgive one defection
# and return to cooperation (C) in the next round.    4. **Punish Continuous
# Defection:**     - If the opponent defects for two consecutive rounds, switch
# to defection (D) and continue defecting until the opponent returns to
# cooperation (C).      5. **Return to Cooperation After Opponent Cooperates:**
# - If the opponent returns to cooperation (C) at any point, resume cooperation
# (C) as long as they continue cooperating.  This strategy balances between
# exploiting the opponent when necessary and fostering long-term cooperation,
# thereby maximizing your overall payoff through a mix of cooperation and
# controlled retaliation.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C

      # Mirror the opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # If opponent defected in the last round, check for forgiveness or punishment
      if opponent.history[-1] == axl.Action.D:
          # Forgive a single defection if the opponent has cooperated steadily before
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
          # Punish continuous defection (two consecutive defections)
          return axl.Action.D

# ### Aggressive Strategy: "Conditional Defector"  1. **Start by defecting
# (D):** In the first round, play D to test whether the opponent is likely to
# cooperate or defect.  2. **Continue defecting (D) if opponent cooperates
# (C):** If, after any round, the opponent plays C while you play D, continue
# playing D to exploit their cooperation and maximize your payoff.  3. **Switch
# to cooperation (C) if opponent defects (D):** If the opponent defects after
# you defect (i.e., both play D), switch to playing C in the next round. This
# change signals a willingness to cooperate and potentially exploit any future
# cooperation from the opponent.  4. **Return to defection (D) if opponent
# defects again (D):** If the opponent defects while you are cooperating (i.e.,
# you play C and they play D), switch back to defection in all subsequent rounds
# to avoid being exploited.  5. **Alternate between cooperation (C) and
# defection (D) based on opponent’s behavior:** If the opponent begins
# cooperating consistently after you switch to defection, consider alternating
# between cooperation and defection every few rounds to balance exploitation and
# cooperation.  6. **Persistently defect in the final 50 rounds:** In the last
# 50 rounds, defect consistently to maximize short-term gains, as the endgame
# reduces the benefit of establishing long-term cooperation.  This strategy is
# designed to exploit cooperative opponents while avoiding prolonged punishment
# from defectors, with an aggressive focus on gaining higher payoffs through
# defection whenever feasible.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      FINAL_ROUNDS = 50
      TOTAL_ROUNDS = 1000

      # First round: always defect
      if self.first_round():
          return axl.Action.D

      # If we are in the final 50 rounds, always defect
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return axl.Action.D

      # Get the last round's actions
      last_self_action = self.history[-1]
      last_opponent_action = opponent.history[-1]

      # Rule 2: Continue defecting if opponent cooperates while we defect
      if last_self_action == axl.Action.D and last_opponent_action == axl.Action.C:
          return axl.Action.D

      # Rule 3: Switch to cooperation if both defected in the last round
      if last_self_action == axl.Action.D and last_opponent_action == axl.Action.D:
          return axl.Action.C

      # Rule 4: Return to defection if opponent defects while we cooperate
      if last_self_action == axl.Action.C and last_opponent_action == axl.Action.D:
          return axl.Action.D

      # Rule 5: Alternate between cooperation and defection based on opponent's behavior
      # If the opponent has been cooperating consistently, alternate between C and D
      if opponent.history[-3:].count(axl.Action.C) == 3:
          return self._random.random_choice(0.5)

      # Default to defection if no other rule applies
      return axl.Action.D

# ### Strategy: Conditional Cooperation with Punishment and Forgiveness  1.
# **Start by cooperating (C).**    - In the first round, play C to signal
# willingness to cooperate.  2. **Continue cooperating as long as both players
# cooperate.**    - If both you and your opponent play C in the previous round,
# continue playing C in the next round.  3. **Punish defection with immediate
# defection.**    - If your opponent plays D in any round, respond with D in the
# next round. This discourages your opponent from exploiting your cooperation.
# 4. **Forgive after one round of mutual defection.**    - After one round where
# both you and your opponent play D (mutual defection), return to playing C in
# the next round. This signals that you are willing to return to cooperation if
# your opponent does the same.  5. **Never cooperate if the opponent defects
# twice in a row.**    - If your opponent defects in two consecutive rounds,
# continue playing D indefinitely to avoid repeated exploitation.  6. **In the
# final 10 rounds, always defect.**    - Starting from round 991, play D in
# every round, as the game is ending and cooperation is no longer incentivized.
# ### Summary: - Cooperate unless punished. - Punish defectors once, then
# forgive. - Defect permanently if the opponent shows sustained defection. -
# Defect in the final 10 rounds.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, cooperate
      if self.first_round():
          return axl.Action.C

      # Get the current round number
      current_round = len(self.history)

      # In the final 10 rounds, always defect
      if current_round >= 991:
          return axl.Action.D

      # If the opponent defected in the last two rounds, defect indefinitely
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D

      # If both players defected in the last round, forgive and cooperate
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.C

      # If the opponent defected in the last round, punish with defection
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # Otherwise, continue cooperating
      return axl.Action.C

# **Strategy:**  1. **Start by cooperating (C) in the first round.**     2.
# **Observe your opponent’s move each round:**    - If your opponent played C in
# the previous round, **continue cooperating (C)** in the next round.    - If
# your opponent played D in the previous round, **defect (D)** in the next
# round.  3. **If both players defected (D) for two consecutive rounds,** return
# to cooperating (C) in the next round to explore if mutual cooperation can be
# re-established.  4. **If your opponent defects (D) again immediately after you
# tried to cooperate (C) following two consecutive defections,** respond with
# defecting (D) for two rounds as punishment.  5. **Repeat the cycle** of
# attempting to cooperate after any two consecutive mutual defections, but
# always retaliate with two defects if cooperation is not reciprocated.  ---
# **Summary:** Begin by cooperating, reciprocate cooperation, and punish
# defection with temporary retaliation. After two mutual defects, attempt to re-
# establish cooperation.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Get the last two rounds of history
      last_round = self.history[-1]
      opponent_last_round = opponent.history[-1]

      if len(self.history) > 1:
          second_last_round = self.history[-2]
          opponent_second_last_round = opponent.history[-2]
      else:
          second_last_round = None
          opponent_second_last_round = None

      # If both players defected for two consecutive rounds, return to cooperating
      if second_last_round == axl.Action.D and last_round == axl.Action.D and \
         opponent_second_last_round == axl.Action.D and opponent_last_round == axl.Action.D:
          return axl.Action.C

      # If opponent defects immediately after you tried to cooperate following two consecutive defections,
      # respond with two defections as punishment
      if second_last_round == axl.Action.D and last_round == axl.Action.C and \
         opponent_second_last_round == axl.Action.D and opponent_last_round == axl.Action.D:
          return axl.Action.D

      # If opponent cooperated in the last round, continue cooperating
      if opponent_last_round == axl.Action.C:
          return axl.Action.C

      # If opponent defected in the last round, defect in the next round
      if opponent_last_round == axl.Action.D:
          return axl.Action.D

# ### Aggressive Iterated Strategy  1. **Start by playing D (Defect) in the
# first round** – This sets an aggressive tone and immediately maximizes your
# one-round payoff if your opponent starts with cooperation (C).  2. **Continue
# playing D as long as the opponent plays C** – Exploit every opportunity to
# gain 5 points while they score 0. Keep defecting as long as they cooperate.
# 3. **Switch to C (Cooperate) after 5 rounds of mutual defection (D,D)** – If
# both players defect for 5 consecutive rounds, switch to cooperation to test if
# the opponent will also cooperate. This prevents both players from getting
# stuck in a low-scoring (D,D) cycle, which gives only 1 point each.  4.
# **Return to D immediately if the opponent defects after you switch to C** –
# Punish any defection from your opponent. Every time they defect while you
# cooperate, revert to D and stay aggressive by defecting in subsequent rounds.
# 5. **Alternate between C and D if the opponent alternates** – If the opponent
# starts alternating between cooperation and defection, mirror their behavior;
# play D when they play C and C when they play D. This minimizes their score
# while keeping your score relatively high.  6. **End the game aggressively by
# defecting in the last 3 rounds** – If the opponent has been cooperating
# consistently, defect in the final 3 rounds to maximize your score without fear
# of retaliation since the game is ending.  ---  This strategy seeks to maximize
# your payoff by exploiting cooperation from the opponent while also offering
# brief chances for cooperation if mutual defection becomes unproductive.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:

      # Helper function to check if the last N rounds were mutual defections
      def last_n_mutual_defections(n):
          return all(self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, n + 1))

      # First round: play D
      if self.first_round():
          return axl.Action.D

      # End game strategy: defect in the last 3 rounds
      if len(self.history) >= 997:
          return axl.Action.D

      # If opponent alternates between C and D, mirror their behavior
      if len(self.history) > 1 and self.history[-1] != self.history[-2] and opponent.history[-1] != opponent.history[-2]:
          return axl.Action.C if opponent.history[-1] == axl.Action.D else axl.Action.D

      # If opponent defects after we switch to C, return to D
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # Switch to C after 5 rounds of mutual defection
      if len(self.history) >= 5 and last_n_mutual_defections(5):
          return axl.Action.C

      # Continue playing D as long as opponent plays C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D

      # Default to D if none of the above conditions are met
      return axl.Action.D

# ### Strategy: "Tit-for-Tat with Occasional Forgiveness"  **1. Start with
# Cooperation:**   In the first round, play C (Cooperate).  **2. Mirror Your
# Opponent’s Last Move:**   From round 2 onwards, repeat your opponent's
# previous move: - If your opponent played C in the last round, play C
# (Cooperate). - If your opponent played D in the last round, play D (Defect).
# **3. Forgive Defection After Every 10 Rounds:**   If your opponent defects
# (plays D), after 10 rounds of following the "Tit-for-Tat" strategy (i.e.,
# mirroring), forgive once by playing C (Cooperate) regardless of their previous
# move. Resume the usual "Tit-for-Tat" behavior after this single act of
# forgiveness.  **4. Continue Until Round 1000.**

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # On the first round, cooperate
      if self.first_round():
          self.forgiveness_counter = 0  # Initialize forgiveness counter
          return axl.Action.C

      # Increment forgiveness counter
      self.forgiveness_counter += 1

      # Forgive after every 10 rounds of tit-for-tat
      if self.forgiveness_counter == 10:
          self.forgiveness_counter = 0  # Reset counter after forgiveness
          return axl.Action.C

      # Mirror opponent's last move (Tit-for-Tat)
      return opponent.history[-1]

# ### Strategy: Conditional Tit-for-Tat with Forgiveness  1. **Initial Move**:
# Begin the game by cooperating (playing C).  2. **Subsequent Moves**:    - **If
# your opponent cooperated in the previous round**: Cooperate (play C) in the
# current round.    - **If your opponent defected in the previous round**:
# Defect (play D) in the current round.     3. **Forgiveness Mechanism**:    -
# **If your opponent defects twice in a row**: Cooperate (play C) in the next
# round. This is to avoid getting locked into a prolonged cycle of mutual
# defection.  4. **Final 10 Rounds**: Defect (play D) consistently in the last
# 10 rounds, regardless of the opponent's actions, to maximize payoff near the
# end of the game.  ---  This strategy balances cooperation and retaliation,
# incentivizing mutual cooperation while preventing excessive punishment for
# occasional defection. The forgiveness mechanism helps recover from periods of
# mutual defection, and the end-game defection ensures a higher payoff when
# cooperation is less likely to be reciprocated.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate
      if self.first_round():
          return axl.Action.C

      # Final 10 rounds: Defect consistently
      if len(self.history) >= 990:
          return axl.Action.D

      # Forgiveness mechanism: If opponent defected twice in a row, cooperate
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.C

      # Tit-for-Tat: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# 1. **Initial Move**: Start by playing **D** (Defect) in the first round.  2.
# **Condition 1 (Opponent Cooperates after Defection)**: If the opponent plays
# **C** (Cooperate) after you defect, continue playing **D** to exploit their
# cooperation.  3. **Condition 2 (Opponent Defects after Defection)**: If the
# opponent responds to your defection with **D**, continue playing **D** as
# well. This ensures you avoid being exploited while maintaining a minimal
# payoff of 1 per round.  4. **Condition 3 (Opponent Cooperates Consistently)**:
# If, after several rounds (e.g., 3 rounds), the opponent always plays **C**
# despite your defection, consider switching to **C** to increase long-term
# gains with mutual cooperation (3 points each).  5. **Condition 4 (Opponent
# Switches to Defect after Cooperation)**: If the opponent switches to **D**
# after you have moved to **C**, immediately switch back to **D** and stay there
# for the remainder of the game.  6. **Overall Objective**: Prioritize
# exploitation early by defecting, but remain flexible to switch to cooperation
# if mutual cooperation appears possible and stable. Always respond to defection
# with defection to minimize losses.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Defect in the first round
      if self.first_round():
          return axl.Action.D

      # Condition 1: If opponent cooperates after you defect, continue defecting
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.D

      # Condition 2: If opponent defects after you defect, continue defecting
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # Condition 3: If opponent cooperates consistently for 3 rounds, switch to cooperation
      if len(self.history) >= 3 and all(opponent.history[-3:] == [axl.Action.C] * 3):
          return axl.Action.C

      # Condition 4: If opponent switches to defect after you cooperate, switch back to defect
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # Default action: Continue cooperating if none of the above conditions are met
      return axl.Action.C

# 1. **Start by playing C (cooperate)** in the first round.  2. **In subsequent
# rounds:**    - If your opponent played **C in the previous round**, continue
# to play **C**.    - If your opponent played **D in the previous round**, play
# **D** in the next round (punish defection).     3. **After punishing a
# defection** (i.e., after playing D in response to your opponent's D), return
# to playing **C** in the next round to signal a willingness to cooperate again.
# 4. **Always respond in the same way to repeated defections**: If your opponent
# continuously defects, you continue playing **D** to minimize losses.  This
# strategy fosters cooperation while punishing defection briefly, allowing for
# recovery if your opponent is willing to cooperate again.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C

      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]

      # If opponent cooperated in the last round, cooperate
      if opponent_last_move == axl.Action.C:
          return axl.Action.C

      # If opponent defected in the last round, defect this round
      if opponent_last_move == axl.Action.D:
          # Check if we defected in the last round (punishment already given)
          if self.history[-1] == axl.Action.D:
              # After punishing, return to cooperation
              return axl.Action.C
          else:
              # Punish the defection by defecting
              return axl.Action.D

# ### Strategy for Maximizing Payoff in a 1000-Round Iterated Game  1. **Start
# with Cooperation (C):** In the first round, always play C to establish an
# initial cooperative tone and gather information about your opponent's
# tendencies.  2. **Tit-for-Tat with Forgiveness:**     - From round 2 onward,
# mirror your opponent's previous move:      - If they played C in the previous
# round, play C.      - If they played D in the previous round, play D.    -
# **Forgiveness Rule:** If your opponent defects (plays D) but then cooperates
# (plays C) in the next round, forgive them and return to playing C.  3.
# **Occasional Defection for Testing:**     - Every 50 rounds, regardless of the
# opponent's behavior, play D once to test if the opponent is purely cooperative
# or trying to exploit your cooperation. Return to Tit-for-Tat after this
# defection.     4. **Endgame Strategy (Rounds 990-1000):**     - In the last 10
# rounds, play D in every round to maximize your score, as cooperation is less
# valuable when the game is close to ending and retaliation for defection has
# minimal impact.  ### Summary of Conditions: - **Round 1:** Play C. - **Round
# 2-989:** Play your opponent's last move (C if they played C, D if they played
# D), with forgiveness if they return to cooperation. - **Every 50 rounds:**
# Defect once to test your opponent. - **Rounds 990-1000:** Defect in every
# round.  This strategy balances cooperation with cautious defection to maximize
# long-term payoffs while minimizing exploitation.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C

      # Get the current round number
      round_number = len(self.history) + 1

      # Endgame strategy: Defect in rounds 990-1000
      if round_number >= 990:
          return axl.Action.D

      # Every 50 rounds: Defect once to test the opponent
      if round_number % 50 == 0:
          return axl.Action.D

      # Tit-for-Tat with forgiveness
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected in the last round, check if they cooperated in the round before that
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C:
              return axl.Action.C  # Forgive if they cooperated after defecting
          else:
              return axl.Action.D  # Otherwise, retaliate with defection
      else:
          return axl.Action.C  # Cooperate if opponent cooperated in the last round

# ### Aggressive Strategy for Iterated Normal-Form Game:  1. **Start with
# Defection (D):**      In the first round, play D to maximize potential gains
# if the opponent cooperates.  2. **Punish Cooperation:**      If your opponent
# plays C in any round, immediately follow up with D in the next round to
# exploit their cooperation and score 5 points.  3. **Tit-for-Tat with Defection
# Bias:**      If your opponent plays D, continue to play D. This ensures that
# you avoid being exploited and maintain a baseline score of 1.  4. **Occasional
# Cooperation (C) After Extended Defection:**      Every 50 rounds, play C once
# to test if the opponent might switch to cooperation. If they reciprocate with
# C, play C for the next 3 rounds to boost mutual scores. If they defect during
# this period, immediately return to D.  5. **Endgame Strategy (Final 50
# Rounds):**      In the last 50 rounds, consistently play D regardless of prior
# cooperation or defection to ensure you don’t risk being exploited in the final
# phase of the game.  This strategy leverages aggression to maximize
# exploitation while occasionally probing for opportunities to cooperate if the
# opponent shows signs of long-term cooperation.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      ENDGAME_THRESHOLD = 50
      COOPERATION_TEST_INTERVAL = 50
      COOPERATION_TEST_LENGTH = 3

      # First round: Start with Defection (D)
      if self.first_round():
          return axl.Action.D

      # Endgame strategy: In the last 50 rounds, always play D
      if len(self.history) >= 1000 - ENDGAME_THRESHOLD:
          return axl.Action.D

      # Punish cooperation: If opponent played C last round, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D

      # Tit-for-Tat with Defection Bias: If opponent played D last round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # Occasional Cooperation: Every 50 rounds, test cooperation
      if len(self.history) % COOPERATION_TEST_INTERVAL == 0:
          return axl.Action.C

      # If in a cooperation test phase (next 3 rounds after a C), continue cooperation if opponent cooperates
      if len(self.history) % COOPERATION_TEST_INTERVAL < COOPERATION_TEST_LENGTH:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D

      # Default action: Defect
      return axl.Action.D

# 1. **Start by Cooperating (C):** In the first round, play C to signal a
# willingness to cooperate.  2. **Mirror the Opponent's Last Move:** From the
# second round onwards, play exactly what your opponent played in the previous
# round. If they played C, play C. If they played D, play D.  3. **Forgive
# Occasionally:** If your opponent defects (plays D), allow for one defection by
# continuing to mirror their moves, but if they return to C after defecting,
# return to C as well. This allows for mistakes or exploration by the opponent
# without escalating conflict.  4. **Punish Persistent Defection:** If the
# opponent defects twice in a row, switch to consistent defection (D) until they
# return to cooperation. Once they play C again, immediately return to C on the
# next round.  This strategy encourages cooperation by rewarding it, punishes
# long-term defection, but is forgiving enough to allow the possibility of re-
# establishing cooperation.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]

      # If the opponent defected twice in a row, punish by defecting
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D

      # Otherwise, mirror the opponent's last move
      return last_opponent_move

# **Strategy:**  1. **Start with cooperation (C)** in the first round,
# regardless of the opponent's actions.     2. **Tit-for-Tat rule** (reactive to
# opponent's last move):    - If your opponent played **C** in the previous
# round, play **C**.    - If your opponent played **D** in the previous round,
# play **D**.  3. **Occasional forgiveness** every **10 rounds** if your
# opponent has played **D** in the last round:    - Even if your opponent
# defected (played D) in the previous round, randomly choose to play **C** 20%
# of the time to test if they might return to cooperation.  4. **Final 10 rounds
# (rounds 991–1000)**: Shift to **defection (D)** for all remaining rounds,
# regardless of the opponent’s actions, to maximize your score before the game
# ends.  ---  This strategy balances cooperation and retaliation while allowing
# occasional forgiveness to recover mutual cooperation, with a final shift to
# defection to exploit the game's finite nature.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C

      # Final 10 rounds: Defect
      if len(self.history) >= 991:
          return axl.Action.D

      # Tit-for-Tat rule: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          # Occasional forgiveness every 10 rounds
          if len(self.history) % 10 == 0:
              if self._random.random_choice(0.2):
                  return axl.Action.C
          return axl.Action.D

# **Strategy:**  1. **Start with Defection:** Play D (defect) in the first round
# to immediately test your opponent’s willingness to cooperate or defect.  2.
# **Continue Defecting if Opponent Cooperates:** If your opponent responds with
# C (cooperate) in the first round or any subsequent round, continue playing D
# to maximize your payoff (5) while they score 0.  3. **Switch to Alternating
# Cooperation if Opponent Defects Consistently:** If your opponent plays D
# (defects) in the first round and continues defecting for multiple rounds
# (e.g., 3 consecutive rounds), switch to playing C (cooperate) every other
# round. Alternate between C and D to try to achieve a balance where the
# opponent might start cooperating, boosting both your scores above the mutual
# defection payoff (1).  4. **Retaliate if Opponent Exploits Cooperation:** If
# your opponent plays D immediately after you play C (exploiting your
# cooperation in any round), revert to consistent defection (D) for the next 5
# rounds as punishment.  5. **Reattempt Cooperation if Opponent Cooperates for 5
# Rounds:** If your opponent starts playing C for 5 consecutive rounds after a
# period of defection, experiment by playing C once. If they continue
# cooperating, switch to mutual cooperation (C) for both sides to score 3.  6.
# **Final 10 Rounds - Defect:** In the last 10 rounds of the game, regardless of
# the previous history, always play D to maximize your points in case the
# opponent anticipates the end of the game and tries to defect.  This aggressive
# approach seeks to exploit cooperation while maintaining deterrents for
# defection and adjusting strategies based on the opponent’s behavior.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      DEFECT = axl.Action.D
      COOPERATE = axl.Action.C
      PUNISHMENT_ROUNDS = 5
      ALTERNATE_THRESHOLD = 3
      FINAL_ROUNDS = 10
      TOTAL_ROUNDS = 1000

      # First round: always defect
      if self.first_round():
          self.punishment_counter = 0  # Track punishment rounds
          self.alternating = False  # Track if we are in alternating mode
          self.cooperate_attempt = False  # Track if we are attempting cooperation
          return DEFECT

      # Final 10 rounds: always defect
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return DEFECT

      # If in punishment mode, continue defecting for the next 5 rounds
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return DEFECT

      # If opponent has defected for 3 consecutive rounds, switch to alternating C and D
      if opponent.history[-ALTERNATE_THRESHOLD:] == [DEFECT] * ALTERNATE_THRESHOLD:
          self.alternating = True

      # If alternating, play C and D alternately
      if self.alternating:
          if len(self.history) % 2 == 0:
              return COOPERATE
          else:
              return DEFECT

      # If opponent cooperates for 5 consecutive rounds, attempt cooperation
      if opponent.history[-5:] == [COOPERATE] * 5:
          self.cooperate_attempt = True

      # If attempting cooperation, play C once and see if opponent continues cooperating
      if self.cooperate_attempt:
          if self.history[-1] == COOPERATE and opponent.history[-1] == DEFECT:
              # Opponent exploited cooperation, punish for 5 rounds
              self.punishment_counter = PUNISHMENT_ROUNDS
              self.cooperate_attempt = False
              return DEFECT
          elif self.history[-1] == COOPERATE and opponent.history[-1] == COOPERATE:
              # Mutual cooperation achieved, continue cooperating
              return COOPERATE
          else:
              # First attempt to cooperate
              return COOPERATE

      # If opponent cooperates, continue defecting
      if opponent.history[-1] == COOPERATE:
          return DEFECT

      # Default action: defect
      return DEFECT

# 1. **Start by cooperating**: In the first round, always play C (cooperate).
# 2. **Mirror your opponent’s last move**: From the second round onward, play
# whatever your opponent played in the previous round. If they played C, you
# play C. If they played D, you play D.  3. **Forgive occasional defections**:
# If your opponent defects (plays D) but then returns to cooperation (plays C in
# the next round), immediately return to cooperation (play C again in the
# following round). Only continue defecting if they consistently defect.  4.
# **Punish persistent defection**: If your opponent defects for two or more
# consecutive rounds, continue defecting (play D) until they return to
# cooperation, at which point you revert to cooperating as per step 2.  This
# strategy encourages mutual cooperation, punishes sustained defection, but
# allows for recovery if your opponent resumes cooperative behavior.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # Check if opponent defected in the last round but cooperated before that
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.C

      # Punish persistent defection (two or more consecutive defections)
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D

      # Default to mirroring the opponent's last move
      return opponent.history[-1]

# ### Strategy: Conditional Reciprocity with Occasional Defection  1. **Initial
# Move**: Start by playing *Cooperate (C)*.  2. **Tit-for-Tat with
# Forgiveness**:    - On each subsequent round, repeat your opponent's last
# move:      - If they played *C* in the previous round, play *C*.      - If
# they played *D* in the previous round, play *D*, but only defect for **one
# round**.  3. **Forgiveness Mechanism**: After retaliating with *D* once
# (following your opponent's *D*), return to *C*:    - Continue cooperating
# unless your opponent defects repeatedly.     4. **Punishment for Multiple
# Defections**:     - If your opponent plays *D* for 3 consecutive rounds,
# switch to *D* for 5 rounds.    - After that punishment period, return to *C*
# to test for cooperation.  5. **Endgame Adjustment** (Final 10 rounds):    - In
# the last 10 rounds, defect (*D*) regardless of the opponent’s actions to
# secure higher individual payoffs, unless the opponent has demonstrated
# consistent cooperation up to that point. In that case, maintain cooperation to
# avoid a breakdown in mutual benefit.  This strategy balances cooperation and
# defection, allowing for mutual high payoffs while safeguarding against
# exploitation.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate
      if self.first_round():
          return axl.Action.C

      # Endgame adjustment: Defect in the last 10 rounds unless opponent has been consistently cooperative
      if len(self.history) >= 990:
          if opponent.history.cooperations == len(opponent.history):
              return axl.Action.C
          else:
              return axl.Action.D

      # Check if opponent defected in the last 3 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:].count(axl.Action.D) == 3:
          # Punish with 5 defections
          if len(self.history) < len(opponent.history) + 5:
              return axl.Action.D
          else:
              return axl.Action.C

      # Tit-for-Tat with forgiveness: Repeat opponent's last move
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected last round, defect once, then forgive
          if len(self.history) < len(opponent.history) + 1:
              return axl.Action.D
          else:
              return axl.Action.C
      else:
          return axl.Action.C

# **Aggressive Iterated Game Strategy:**  1. **Initial Move**: Start with
# **Defect (D)** in the first round. This sets an aggressive tone and tests the
# opponent’s willingness to cooperate.  2. **Tit-for-Tat with Escalation**:    -
# If the opponent plays **Cooperate (C)** in the previous round, continue
# **Defecting (D)** to exploit their cooperation unless certain conditions
# (below) are met.    - If the opponent plays **Defect (D)** in the previous
# round, you also play **Defect (D)** to avoid being exploited.  3.
# **Conditional Cooperation**:    - If the opponent plays **C** for at least 5
# consecutive rounds, switch to **Cooperate (C)** on the next round to test if
# mutual cooperation is sustainable.    - If the opponent defects in any of the
# rounds during this cooperation phase, immediately switch back to **Defect
# (D)** for the rest of the game.  4. **Punishment for Betrayal**:    - If the
# opponent defects after any period of mutual cooperation, switch to **Defect
# (D)** for at least 10 rounds before reconsidering cooperation.  5. **Endgame
# Defection**:    - In the final 10 rounds, always play **Defect (D)**
# regardless of previous opponent behavior, since there is no future to punish
# or reward cooperation.  This strategy aims to maximize long-term exploitation
# of cooperative opponents while minimizing losses against defectors.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Defect in the first round
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperations by opponent
          self.punishment_timer = 0  # Track punishment period after betrayal
          return axl.Action.D

      # Endgame defection: Always defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D

      # Punishment for betrayal: Defect for at least 10 rounds after opponent defects during mutual cooperation
      if self.punishment_timer > 0:
          self.punishment_timer -= 1
          return axl.Action.D

      # Tit-for-Tat with Escalation
      if opponent.history[-1] == axl.Action.D:
          # Opponent defected last round, so we defect as well
          self.coop_streak = 0  # Reset cooperation streak
          return axl.Action.D
      else:
          # Opponent cooperated last round
          self.coop_streak += 1

          # Conditional cooperation: If opponent cooperates for 5 consecutive rounds, cooperate
          if self.coop_streak >= 5:
              return axl.Action.C

          # Otherwise, continue defecting to exploit their cooperation
          return axl.Action.D

# **Strategy:**  1. **Round 1: Always start by playing C (Cooperate).**     2.
# **Subsequent Rounds:**    - If both players played C in the previous round,
# continue playing C.    - If your opponent played D (Defect) in the previous
# round, respond by playing D in the next round.    - After playing D in
# response to your opponent's D, return to playing C in the following round,
# giving your opponent another chance to cooperate.     3. **Final Rounds
# (Rounds 990-1000):** Play D regardless of the opponent's actions to maximize
# your final payoffs before the game ends.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always start by playing C
      if self.first_round():
          return axl.Action.C

      # Final rounds (990-1000): Play D regardless of opponent's actions
      if len(self.history) >= 990:
          return axl.Action.D

      # Subsequent rounds:
      # If both players played C in the previous round, continue playing C
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # If opponent played D in the previous round, respond with D
      if opponent.history[-1] == axl.Action.D:
          # If we played D in the last round, return to C
          if self.history[-1] == axl.Action.D:
              return axl.Action.C
          # Otherwise, play D in response to opponent's D
          return axl.Action.D

      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# ### Strategy: "Tit-for-Tat with Occasional Forgiveness"  1. **Start with
# Cooperation (C):** In the first round, always choose to cooperate (C).     2.
# **Mirror the Opponent's Last Move:** In each subsequent round, play exactly
# what your opponent played in the previous round. If they cooperated (C), you
# cooperate. If they defected (D), you defect.  3. **Forgive after Two
# Consecutive Defections:** If the opponent defects (D) in two consecutive
# rounds, switch back to cooperation (C) in the next round regardless of their
# previous actions. This introduces an element of forgiveness and helps avoid
# prolonged cycles of mutual defection.  4. **Return to Mirroring:** After
# forgiving, resume the strategy of mirroring your opponent’s last move.  This
# strategy balances cooperation with retaliation but also incorporates
# forgiveness, which maximizes your long-term payoff by encouraging cooperation
# while not allowing the opponent to exploit you.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C

      # Check if the opponent defected in the last two rounds
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          # Forgive after two consecutive defections
          return axl.Action.C

      # Mirror the opponent's last move
      return opponent.history[-1]

# ### Aggressive Strategy for Maximising Payoff  1. **Start with Defection (D)
# in the first round.**      This sets the tone for an aggressive approach and
# immediately tests the opponent's willingness to cooperate or defect.  2.
# **Continue Defecting (D) as long as the opponent cooperates (C).**      If the
# opponent continues to cooperate while you defect, you gain the maximum
# possible payoff (5) and they get 0. This maximises your score while keeping
# the opponent's relatively low.  3. **Switch to Cooperation (C) if the opponent
# defects (D) three times in a row.**      This signals that the opponent is not
# willing to cooperate and repeated mutual defection (D, D) only gives both
# players a low payoff (1). By switching to cooperation, you open the
# possibility of mutual cooperation (C, C) for a better overall payoff of 3 each
# if they follow suit.  4. **Return to Defection (D) if the opponent defects (D)
# after your cooperation (C).**      This punishes the opponent for not
# reciprocating your cooperative gesture, ensuring you do not fall into a
# pattern where you consistently lose out by cooperating while they defect.  5.
# **Alternate between Cooperation (C) and Defection (D) if the opponent mirrors
# your behaviour exactly.**      If the opponent is mimicking your moves (i.e.,
# playing C when you play C and D when you play D), alternate between
# cooperation and defection to keep them guessing and prevent them from
# exploiting a predictable pattern.  6. **End with Defection (D) in the final 10
# rounds.**      As the game approaches the end, shift to consistent defection
# to maximise your points in the final rounds, since future reprisals from the
# opponent are no longer a concern.  This strategy seeks to exploit early
# cooperative opponents while adapting to more aggressive ones, ensuring a
# relatively high payoff throughout the game.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:

      # 1. Start with Defection (D) in the first round.
      if self.first_round():
          return axl.Action.D

      # 6. End with Defection (D) in the final 10 rounds.
      if len(self.history) >= 990:
          return axl.Action.D

      # 2. Continue Defecting (D) as long as the opponent cooperates (C).
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D

      # 3. Switch to Cooperation (C) if the opponent defects (D) three times in a row.
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.C

      # 4. Return to Defection (D) if the opponent defects (D) after your cooperation (C).
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D

      # 5. Alternate between Cooperation (C) and Defection (D) if the opponent mirrors your behaviour exactly.
      if self.history[-1] == opponent.history[-1]:
          return axl.Action.C if self.history[-1] == axl.Action.D else axl.Action.D

      # Default to Defection (D) if no other condition is met.
      return axl.Action.D

# ### Strategy for Iterated Game:  1. **Start by cooperating** (play C) in the
# first round.     2. **Continue cooperating** (play C) as long as both you and
# your opponent have cooperated in the previous round.  3. **If your opponent
# defects** (plays D) in any round, immediately retaliate by defecting (play D)
# in the next round.  4. **After retaliating once, return to cooperation** (play
# C) in the following round, regardless of your opponent's move.  5. **If your
# opponent continues to defect for two consecutive rounds**, switch to defecting
# (play D) until they cooperate again.  6. **Once your opponent cooperates
# again**, return to step 2 and resume cooperation.  This strategy balances
# cooperation and retaliation, aiming to sustain mutual cooperation while
# punishing defection briefly, but not excessively.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C

      # Step 2: Continue cooperating if both players cooperated in the previous round
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # Step 3: If opponent defects, retaliate by defecting in the next round
      if opponent.history[-1] == axl.Action.D and self.history[-1] == axl.Action.C:
          return axl.Action.D

      # Step 4: After retaliating once, return to cooperation
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          # Step 5: If opponent defects for two consecutive rounds, switch to defecting
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C

      # Step 6: If opponent cooperates again, return to cooperation
      return axl.Action.C

# **Strategy:**  1. **Start by playing C (Cooperate).**     2. **If the opponent
# plays C in the previous round, continue playing C.**  3. **If the opponent
# plays D (Defect) in the previous round, switch to D in the next round.**  4.
# **After playing D, if the opponent returns to playing C, switch back to C in
# the next round.**  5. **If the opponent plays D twice in a row, continue
# playing D until the opponent starts playing C again.**  ---  This strategy
# balances cooperation and retaliation, ensuring that you reward cooperation but
# defend against exploitation.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by playing C
      if self.first_round():
          return axl.Action.C

      # If the opponent played C in the previous round, continue playing C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C

      # If the opponent played D in the previous round
      if opponent.history[-1] == axl.Action.D:
          # If the opponent played D twice in a row, continue playing D
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          # Otherwise, switch to D
          return axl.Action.D


Aggressive_ranks = [
'Aggressive_8',
'Aggressive_14',
'Aggressive_9',
'Aggressive_11',
'Aggressive_20',
'Aggressive_12',
'Aggressive_25',
'Aggressive_1',
'Aggressive_23',
'Aggressive_19',
'Aggressive_7',
'Aggressive_21',
'Aggressive_22',
'Aggressive_10',
'Aggressive_18',
'Aggressive_6',
'Aggressive_16',
'Aggressive_13',
'Aggressive_2',
'Aggressive_4',
'Aggressive_3',
'Aggressive_24',
'Aggressive_17',
'Aggressive_5',
'Aggressive_15',
]

Cooperative_ranks = [
'Cooperative_17',
'Cooperative_19',
'Cooperative_4',
'Cooperative_5',
'Cooperative_25',
'Cooperative_15',
'Cooperative_22',
'Cooperative_9',
'Cooperative_2',
'Cooperative_10',
'Cooperative_6',
'Cooperative_20',
'Cooperative_3',
'Cooperative_23',
'Cooperative_18',
'Cooperative_14',
'Cooperative_12',
'Cooperative_24',
'Cooperative_13',
'Cooperative_7',
'Cooperative_8',
'Cooperative_21',
'Cooperative_16',
'Cooperative_1',
'Cooperative_11',
]

Neutral_ranks = [
'Neutral_11',
'Neutral_5',
'Neutral_3',
'Neutral_25',
'Neutral_17',
'Neutral_23',
'Neutral_1',
'Neutral_4',
'Neutral_16',
'Neutral_8',
'Neutral_22',
'Neutral_12',
'Neutral_19',
'Neutral_18',
'Neutral_7',
'Neutral_6',
'Neutral_2',
'Neutral_10',
'Neutral_14',
'Neutral_20',
'Neutral_24',
'Neutral_9',
'Neutral_21',
'Neutral_13',
'Neutral_15',
]
