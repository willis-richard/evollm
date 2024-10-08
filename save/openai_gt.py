import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

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

Aggressive_ranks = [
'Aggressive_1',
'Aggressive_8',
'Aggressive_9',
'Aggressive_7',
'Aggressive_10',
'Aggressive_6',
'Aggressive_2',
'Aggressive_4',
'Aggressive_3',
'Aggressive_5',
]

Cooperative_ranks = [
'Cooperative_1',
'Cooperative_2',
'Cooperative_4',
'Cooperative_5',
'Cooperative_9',
'Cooperative_10',
'Cooperative_6',
'Cooperative_3',
'Cooperative_8',
'Cooperative_7',
]

Neutral_ranks = [
'Neutral_5',
'Neutral_3',
'Neutral_4',
'Neutral_8',
'Neutral_7',
'Neutral_1',
'Neutral_6',
'Neutral_2',
'Neutral_10',
'Neutral_9',
]
