import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# 1. **Start by defecting (D) in the first round**. This sets an aggressive tone
# and maximizes the payoff if the opponent cooperates initially.  2. **Continue
# defecting (D) as long as the opponent cooperates (C)**. This exploits
# cooperative opponents, ensuring you score 5 while they score 0.  3. **If the
# opponent defects (D), defect (D) for the next 2 rounds**. This punishes their
# defection but avoids locking both players into long-term low payoffs.  4.
# **After 2 rounds of mutual defection, switch to cooperate (C) for 1 round**.
# This tests whether the opponent is willing to return to cooperation.  5. **If
# the opponent cooperates (C) in response, continue cooperating (C) as long as
# they do**. This ensures both players can consistently score 3, which may be
# beneficial in the long run.  6. **If the opponent defects (D) again after your
# cooperation, defect (D) for the rest of the game**. This signals that repeated
# defection will not be tolerated and prevents further exploitation.  7. **In
# the last 10 rounds, defect (D) regardless of the opponent’s actions**. This
# ensures you maximize your payoff in the endgame, where cooperation is less
# likely to be reciprocated.  This revised strategy maintains an aggressive
# approach while simplifying the punishment phase and reducing the risk of being
# exploited. It also accounts for the endgame, where defection becomes more
# advantageous.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      DEFECT = axl.Action.D
      COOPERATE = axl.Action.C
      TOTAL_ROUNDS = 1000
      ENDGAME_THRESHOLD = 10
  
      # If it's the first round, start by defecting
      if self.first_round():
          return DEFECT
  
      # If we are in the last 10 rounds, always defect
      if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
          return DEFECT
  
      # If the opponent has defected in the last round
      if opponent.history[-1] == DEFECT:
          # If we have defected for less than 2 rounds after their defection, continue defecting
          if len(self.history) >= 2 and self.history[-2:] == [DEFECT, DEFECT]:
              return COOPERATE  # After 2 rounds of mutual defection, cooperate for 1 round
          return DEFECT  # Otherwise, continue defecting for punishment
  
      # If the opponent cooperated in the last round
      if opponent.history[-1] == COOPERATE:
          # If we defected in the last round, continue defecting as long as they cooperate
          if self.history[-1] == DEFECT:
              return DEFECT
          # If we cooperated in the last round, continue cooperating
          return COOPERATE
  
      # Default to defecting if no other condition is met
      return DEFECT

# 1. **Start by cooperating**: In the first round, play C (cooperate) to signal
# a willingness to engage in mutual cooperation.  2. **Continue cooperating if
# opponent cooperates**: If the opponent plays C in the previous round, play C
# again in the next round to maintain mutual cooperation and maximize the payoff
# of 3 per round.  3. **Punish defection with escalation**: If the opponent
# plays D (defects), respond by playing D in the next round. However, if the
# opponent defects again within the next 5 rounds, increase the punishment by
# defecting for 2 consecutive rounds. Continue escalating the punishment by
# adding one more round of defection for each subsequent defection within a
# 5-round window.  4. **Forgive after a defection-free period**: If the opponent
# cooperates (plays C) for 5 consecutive rounds after a defection, return to
# playing C (cooperate) to allow for a reset and encourage long-term
# cooperation.  5. **Repeat the cycle**: Continue this strategy throughout the
# 1000 rounds. If the opponent defects again after being forgiven, repeat the
# punishment and forgiveness cycle, with escalating punishments for repeated
# defections.  In summary: Start with cooperation, reciprocate cooperation,
# punish defection with escalating defections if the opponent continues to
# defect, and forgive after a defection-free period to encourage a return to
# cooperation.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.escalation_level = 0  # Tracks the current level of punishment
          self.defection_rounds = []  # Tracks the rounds where opponent defected
          return axl.Action.C  # Start by cooperating
  
      # Check if opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # Record the round of defection
          self.defection_rounds.append(len(self.history))
  
          # Calculate the number of defections in the last 5 rounds
          recent_defections = self.defection_rounds[-5:]
  
          # Escalate punishment if opponent defects again within 5 rounds
          if len(recent_defections) > 1 and recent_defections[-1] - recent_defections[-2] <= 5:
              self.escalation_level += 1
          else:
              self.escalation_level = 1  # Reset escalation if no recent defections
  
          # Defect for the number of rounds equal to the escalation level
          if len(self.history) < sum(range(1, self.escalation_level + 1)):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent has cooperated for 5 consecutive rounds, forgive and reset
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.C] * 5:
          self.escalation_level = 0  # Reset escalation level
          self.defection_rounds = []  # Clear defection history
  
      # Continue cooperating if opponent cooperates
      return axl.Action.C

# 1. **Start with cooperation (C)** in the first round to establish a neutral
# stance.  2. **On subsequent rounds:**     - **If your opponent played C in the
# previous round**, continue to play C in the current round.        - **If your
# opponent played D in the previous round**, play D in the current round
# (retaliate).     3. **Forgive after one round of mutual defection (D-D):**
# - If both you and your opponent played D in the previous round, switch back to
# C in the next round (reset to cooperation).  4. **No fixed end-game
# defection**:      - Continue following the same rules for cooperation and
# defection until the end of the game. Avoid a predetermined defection in the
# final rounds to maintain neutrality and prevent early defection from the
# opponent.  This revised strategy maintains simplicity, neutrality, and logical
# consistency while avoiding unnecessary complexity or predictable end-game
# behavior.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
      
      # Get the last moves of both players
      my_last_move = self.history[-1]
      opponent_last_move = opponent.history[-1]
      
      # If both players defected in the last round, forgive and cooperate
      if my_last_move == axl.Action.D and opponent_last_move == axl.Action.D:
          return axl.Action.C
      
      # If the opponent cooperated in the last round, cooperate
      if opponent_last_move == axl.Action.C:
          return axl.Action.C
      
      # If the opponent defected in the last round, retaliate by defecting
      return axl.Action.D

# **Revised Aggressive Iterated Strategy:**  1. **Start with Defection (D):** In
# the first round, play D to establish an aggressive stance and test the
# opponent's response.  2. **Continue Defecting (D) if Opponent Cooperates
# (C):** If the opponent plays C while you play D, continue playing D in future
# rounds to exploit their cooperation and maximize your payoff (5 points per
# round).  3. **Always Defect (D) if Opponent Defects (D):** If the opponent
# plays D at any point, continue playing D in all future rounds. This ensures
# you avoid being exploited and maintain an aggressive posture.  4. **Switch to
# Cooperation (C) Only if Opponent Cooperates for 5 Consecutive Rounds:** If the
# opponent plays C for 5 consecutive rounds, switch to C to establish mutual
# cooperation and secure a steady payoff of 3 points per round.  5. **Return to
# Defection (D) Immediately if Opponent Defects (D) After Cooperation:** If the
# opponent defects at any point after mutual cooperation, immediately return to
# D and continue defecting for the rest of the game.  ---  This revised strategy
# maintains a more consistent aggressive approach, avoids unnecessary
# cooperation after defections, and only rewards sustained cooperation from the
# opponent. It minimizes the risk of exploitation while still allowing for long-
# term cooperation if the opponent proves trustworthy.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with defection in the first round
      if self.first_round():
          return axl.Action.D
  
      # If opponent has defected at any point, always defect
      if axl.Action.D in opponent.history:
          return axl.Action.D
  
      # If opponent has cooperated for the last 5 consecutive rounds, switch to cooperation
      if opponent.history[-5:] == [axl.Action.C] * 5:
          return axl.Action.C
  
      # If opponent cooperates while we defect, continue defecting
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Default to defection
      return axl.Action.D

# ### Revised Strategy: Conditional Cooperation with Proportional Retaliation
# 1. **Start by cooperating (C) in the first round.**    - This sets a
# cooperative tone and encourages mutual cooperation from the outset.  2.
# **Continue cooperating as long as your opponent cooperates (plays C).**    -
# If both players consistently play C, you each score 3 per round, maximizing
# long-term payoffs.  3. **If your opponent defects (plays D), retaliate by
# defecting (play D) for two consecutive rounds.**    - This proportional
# retaliation discourages sporadic defections by making the cost of defection
# higher, while still allowing for a return to cooperation.  4. **Return to
# cooperation (play C) after two rounds of retaliation, unless your opponent
# defects again.**    - This shows a willingness to forgive and re-establish
# cooperation, but the increased retaliation period makes it clear that
# defection has consequences.  5. **If your opponent continues defecting, keep
# defecting (play D) until they cooperate again.**    - This prevents further
# losses from continuous exploitation and ensures you’re not taken advantage of
# in a series of defections.  6. **In the final 10 rounds, defect (play D)
# regardless of the opponent’s actions.**    - This prevents exploitation in the
# endgame, where opponents might defect knowing retaliation is less costly near
# the end.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      RETALIATION_PERIOD = 2
      FINAL_ROUNDS = 10
      TOTAL_ROUNDS = 1000
  
      # First round: cooperate
      if self.first_round():
          return axl.Action.C
  
      # If in the final 10 rounds, always defect
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return axl.Action.D
  
      # Check if we are in the retaliation period
      if len(self.history) >= RETALIATION_PERIOD:
          # Check if we are retaliating (i.e., we defected in the last 1 or 2 rounds)
          if self.history[-1] == axl.Action.D or self.history[-2] == axl.Action.D:
              # If we are still in the retaliation period, continue defecting
              if len(self.history) < RETALIATION_PERIOD + 1 or self.history[-RETALIATION_PERIOD:] == [axl.Action.D] * RETALIATION_PERIOD:
                  return axl.Action.D
  
      # If opponent defected in the last round, retaliate for two rounds
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# **Revised Strategy: Simplified Tit-for-Tat with Adaptive Forgiveness**  1.
# **Initial Move**: Start by playing *Cooperate (C)* in the first round.  2.
# **Reciprocal Play**:    - In each subsequent round, do *exactly* what your
# opponent did in the previous round.      - If they played *C*, play *C*.
# - If they played *D*, play *D*.  3. **Adaptive Forgiveness**:    - If your
# opponent defects (*D*) but then cooperates (*C*) in the next round,
# immediately forgive and return to *Cooperate (C)* in the following round.    -
# If your opponent continues to defect for 3 consecutive rounds, play *Defect
# (D)* until they cooperate again. Once they cooperate, return to *Cooperate
# (C)* in the next round.  This revision simplifies the forgiveness rule by
# making it adaptive to the opponent's behavior rather than based on an
# arbitrary round count. It maintains neutrality by mirroring the opponent's
# actions while allowing for quick recovery of cooperation after brief
# defections.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
  
      # Check if the opponent defected in the last 3 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          # Continue defecting until the opponent cooperates
          if opponent_last_move == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Adaptive forgiveness: If opponent defected but then cooperated, forgive
      if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D and opponent_last_move == axl.Action.C:
          return axl.Action.C
  
      # Reciprocal play: Mirror the opponent's last move
      return opponent_last_move

# ### Revised Aggressive Strategy for Iterated Normal-Form Game (1000 rounds):
# 1. **Start by Defecting (D) in the first 5 rounds.**      This establishes a
# clear aggressive stance and tests the opponent's willingness to cooperate or
# retaliate.  2. **Observe the opponent's response:**    - If the opponent
# **continues to play Cooperation (C)** despite your defection:      - **Defect
# (D) for the rest of the game.**          The opponent is overly cooperative,
# allowing you to maximize your payoff by consistently exploiting them.     - If
# the opponent **retaliates by playing Defection (D)** in response to your
# defection:      - **Switch to Cooperation (C) for the next 5 rounds.**
# This tests whether the opponent is willing to establish mutual cooperation
# after initial conflict.  3. **After switching to Cooperation (C):**    - If
# the opponent **also switches to Cooperation (C)** and maintains it:      -
# **Continue to cooperate (C) consistently** as long as the opponent does.
# This maximizes long-term payoffs through mutual cooperation.     - If the
# opponent **continues to defect (D)** even after your cooperation:      -
# **Return to consistent Defection (D) for the remainder of the game.**
# The opponent is uncooperative, so mutual defection is the best way to avoid
# being exploited.  4. **In the final 10 rounds:**      - **Defect (D) in every
# round.**        As the game nears its end, defection maximizes short-term
# gains with minimal risk of retaliation.  ### Summary: - Start with defection
# to establish an aggressive tone. - If the opponent is overly cooperative,
# continue defecting. - If the opponent retaliates, test for cooperation and
# reciprocate if they cooperate. - Defect consistently if the opponent remains
# uncooperative. - Defect in the final 10 rounds to secure maximum payoffs.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Defect in the first 5 rounds
      if len(self.history) < 5:
          self.defect_forever = False
          self.cooperate_test = False
          self.mutual_cooperation = False
          return axl.Action.D
      
      # Defect in the final 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
      
      # Check if the opponent has been overly cooperative in the first 5 rounds
      if len(self.history) == 5:
          if opponent.history[:5].count(axl.Action.C) == 5:
              self.defect_forever = True
          else:
              self.defect_forever = False
      
      # If the opponent was overly cooperative, defect forever
      if self.defect_forever:
          return axl.Action.D
      
      # If the opponent retaliated with defection, switch to cooperation for 5 rounds
      if len(self.history) == 5 and opponent.history[:5].count(axl.Action.D) > 0:
          self.cooperate_test = True
          self.cooperate_rounds = 5
      
      # If in cooperation test phase, cooperate for 5 rounds
      if self.cooperate_test:
          if self.cooperate_rounds > 0:
              self.cooperate_rounds -= 1
              return axl.Action.C
          else:
              # After cooperation test, check if opponent cooperated
              if opponent.history[-5:].count(axl.Action.C) == 5:
                  self.mutual_cooperation = True
              else:
                  self.mutual_cooperation = False
              self.cooperate_test = False
      
      # If mutual cooperation was established, continue cooperating
      if self.mutual_cooperation:
          return axl.Action.C
      
      # If mutual cooperation failed, defect for the rest of the game
      if not self.mutual_cooperation:
          return axl.Action.D
      
      # Default action (should not be reached)
      return axl.Action.D

# **Revised Strategy: Simplified Tit for Tat with Occasional Forgiveness**  1.
# **Start with Cooperation**: On the first round, play **C** (Cooperate). This
# sets a cooperative tone and signals your willingness to collaborate.  2. **Tit
# for Tat**: For each subsequent round, **mirror your opponent's previous
# move**. If they played **C** in the last round, you play **C**. If they played
# **D**, you play **D**. This ensures you reward cooperation and punish
# defection immediately.  3. **Occasional Forgiveness**: After every **5 rounds
# of mutual defection** (both players playing **D**), **return to cooperation**
# (play **C**) regardless of the opponent's move. This prevents long cycles of
# mutual defection and gives the opponent a chance to return to cooperation.  4.
# **Maintain Cooperation**: As long as the opponent consistently plays **C**,
# continue to play **C**. If they revert to cooperation after a defection,
# continue cooperating to maximize long-term gains.  This revised strategy
# simplifies the forgiveness mechanism, reducing the risk of exploitation while
# still promoting cooperation and avoiding prolonged defection cycles.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation
      if self.first_round():
          return axl.Action.C
  
      # Tit for Tat: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Check for 5 rounds of mutual defection
          if len(self.history) >= 5 and all(
              self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
              for i in range(1, 6)
          ):
              # Occasional forgiveness: return to cooperation
              return axl.Action.C
          else:
              return axl.Action.D

# ### Revised Neutral Strategy for Maximizing Payoff in an Iterated Normal-Form
# Game  1. **Start with Cooperation (C)**: In the first round, always play C to
# establish a cooperative baseline and observe the opponent's behavior.  2.
# **Tit-for-Tat**: From rounds 2 to 1000, simply mimic your opponent's previous
# move:    - If your opponent played C in the previous round, play C.    - If
# your opponent played D in the previous round, play D.  3. **No Endgame
# Shift**: Continue the Tit-for-Tat strategy consistently through all 1000
# rounds, without shifting to defection in the final rounds.  ### Summary: -
# Start cooperative. - Mimic your opponent's actions throughout the entire game.
# - Maintain neutrality by avoiding any special endgame tactics or forgiveness
# mechanisms.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
      
      # Tit-for-Tat: Mimic the opponent's previous move
      return opponent.history[-1]

# ### Revised Aggressive Iterated Strategy  1. **Start by Defecting (D)**: In
# the first round, always play D to establish an aggressive stance and test your
# opponent’s response.  2. **Defect Until Punished**: Continue playing D as long
# as your opponent cooperates (plays C). This maximizes your early gains.  3.
# **Switch to Cooperation (C) After Punishment**: If your opponent defects (D)
# after previously cooperating (C), interpret this as a punishment. In the next
# round, switch to cooperation (C) to test if they are willing to cooperate
# again.  4. **Return to Defection If Cooperation Fails**: If your opponent
# continues to defect (D) after you switch to cooperation, immediately return to
# defection (D) and stay there. This signals that you will not tolerate one-
# sided defection.  5. **Maintain Cooperation If Reciprocated**: If your
# opponent responds to your cooperation with cooperation (C), continue
# cooperating (C) as long as they do. This allows for mutual benefit if the
# opponent is willing to cooperate.  6. **Endgame Strategy (Final 5 Rounds)**:
# In the last 5 rounds, switch to pure defection (D) regardless of your
# opponent’s behavior. This ensures you maximize your final payoffs without
# concern for future retaliation.  ---  ### Key Adjustments: - **Simplified
# Conditions**: The strategy now has fewer conditional checks, making it simpler
# to follow. - **Aggressiveness Maintained**: The strategy remains aggressive by
# starting with defection and only switching to cooperation if punished. -
# **Reduced Risk of Over-Defection**: The strategy now allows for cooperation if
# the opponent signals willingness, reducing the risk of mutual punishment
# cycles. - **Shorter Endgame Defection**: The final defection phase is reduced
# to the last 5 rounds, balancing the need for maximizing payoffs while
# minimizing unnecessary defection.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      ENDGAME_THRESHOLD = 5
      TOTAL_ROUNDS = 1000
  
      # Check if it's the first round
      if self.first_round():
          return axl.Action.D  # Start by defecting
  
      # Endgame strategy: defect in the last 5 rounds
      if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
          return axl.Action.D
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # If we cooperated in the last round, switch to defection
          if self.history[-1] == axl.Action.C:
              return axl.Action.D
          # If we defected in the last round, continue defecting
          else:
              return axl.Action.D
  
      # If opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          # If we defected in the last round, switch to cooperation
          if self.history[-1] == axl.Action.D:
              return axl.Action.C
          # If we cooperated in the last round, continue cooperating
          else:
              return axl.Action.C

# ### Revised Strategy: Tit-for-Tat with Controlled Retaliation  1. **Start with
# cooperation**: In the first round, play **C** (cooperate).  2. **Mirror your
# opponent's last move**: In each subsequent round, play exactly what your
# opponent played in the previous round. If they played **C**, play **C**. If
# they played **D**, play **D**.  3. **Forgive occasional defection
# cautiously**: If your opponent defects (**D**) once, retaliate by defecting
# (**D**) in the next round. However, if they return to cooperation (**C**)
# after that, immediately return to cooperation as well. This ensures that
# occasional defections are punished but cooperation can quickly resume.  4.
# **Punish repeated defection**: If your opponent defects twice in a row or
# more, continue defecting (**D**) until they cooperate for two consecutive
# rounds. This ensures that persistent defection is met with sustained
# retaliation, discouraging exploitation.  5. **Endgame caution**: In the last
# 10 rounds, continue to mirror your opponent’s moves rather than always
# cooperating. This prevents exploitation in the final rounds while still
# allowing for cooperation if the opponent remains cooperative.  This revised
# strategy maintains a cooperative approach while addressing potential
# exploitability by introducing more cautious forgiveness and a stronger
# response to repeated defections. It also avoids predictable behavior in the
# endgame.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          # In the last 10 rounds, mirror the opponent's last move
          return opponent_last_move
  
      # If the opponent defected in the last round
      if opponent_last_move == axl.Action.D:
          # Check if the opponent defected twice in a row
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              # Continue defecting until the opponent cooperates twice in a row
              if len(opponent.history) > 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              # Retaliate once for a single defection, but forgive if they cooperate next
              return axl.Action.D
      else:
          # If the opponent cooperated in the last round, cooperate
          return axl.Action.C

# ### Revised Strategy: Simple Tit-for-Tat with Adaptive Defection  1. **Start
# with Cooperation (C)**: On the first round, play C.  2. **Mirror the
# Opponent's Last Move**: For each subsequent round, do the following:    - If
# your opponent played C on the previous round, play C.    - If your opponent
# played D on the previous round, play D.  3. **Occasional Defection Based on
# Opponent's Behavior**:    - If the opponent defects (plays D) **three times in
# a row**, defect (play D) on the next round, regardless of their move.    -
# After this defection, return to mirroring their last move as described in Step
# 2.  ### Summary of Rules: - Begin with cooperation. - Mirror the opponent’s
# previous move on each round. - Defect only if the opponent defects three times
# consecutively, then return to mirroring.  ### Key Changes: - Removed the fixed
# defection every 50th round to avoid predictability and unnecessary complexity.
# - Introduced adaptive defection based on the opponent's behavior to maintain
# neutrality and avoid being exploited by frequent defectors.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation on the first round
      if self.first_round():
          return axl.Action.C
  
      # Check if the opponent has defected three times in a row
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Mirror the opponent's last move
      return opponent.history[-1]

# 1. **Start by defecting (D) in the first round** to establish an aggressive
# stance and test your opponent's response.  2. **Continue defecting (D) as long
# as your opponent cooperates (C)** to maximize your payoff by exploiting their
# cooperation.  3. **If your opponent defects (D) in response to your
# defection**, continue defecting (D) for the next 10 rounds to maintain
# dominance and punish their defection.  4. **After 10 rounds of mutual
# defection**, switch to cooperation (C) to test if your opponent is willing to
# cooperate again. If they cooperate (C), continue cooperating (C) as long as
# they do.  5. **If your opponent defects (D) while you are cooperating (C)**,
# immediately return to defecting (D) for the remainder of the game to prevent
# further exploitation.  6. **In the final 20 rounds**, defect (D) consistently,
# regardless of the opponent's actions, to maximize short-term payoffs as future
# retaliation becomes less costly.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punish_count = 0  # Tracks how many rounds of punishment (defection) are left
          return axl.Action.D  # Start by defecting
  
      # In the final 20 rounds, always defect
      if len(self.history) >= 980:
          return axl.Action.D
  
      # If we are in the punishment phase, continue defecting for 10 rounds
      if self.punish_count > 0:
          self.punish_count -= 1
          return axl.Action.D
  
      # If opponent defected while we were cooperating, defect for the rest of the game
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If opponent defected in response to our defection, punish for 10 rounds
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.punish_count = 10
          return axl.Action.D
  
      # If opponent cooperates, we defect to exploit
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # If we reach here, it means 10 rounds of mutual defection have passed, so we cooperate
      return axl.Action.C

# **Revised Strategy: Tit-for-Tat with Conditional Forgiveness**  1. **First
# Round**: Play C (Cooperate).  2. **Subsequent Rounds**:    - **If your
# opponent played C in the previous round**, play C (Cooperate) in the current
# round.    - **If your opponent played D in the previous round**, play D
# (Defect) in the current round.  3. **Conditional Forgiveness**:    - If your
# opponent defects (plays D) **once**, continue to defect in response.    - **If
# your opponent cooperates after defecting**, forgive them by playing C
# (Cooperate) in the next round. This allows for the restoration of cooperation
# without being exploited by persistent defectors.  This revision maintains
# simplicity, encourages cooperation, and avoids unnecessary exploitation by
# only forgiving opponents who return to cooperation after defecting.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # Check if opponent cooperated after defecting
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.C  # Forgive if opponent cooperates after defecting
          return axl.Action.D  # Otherwise, defect

# **Revised Strategy: Simple Tit-for-Tat**  1. **Start by cooperating (C).**  2.
# **Mirror your opponent's previous move:**    - If your opponent played C in
# the last round, play C in the current round.    - If your opponent played D in
# the last round, play D in the current round.  3. **Forgive only after mutual
# defection:**    - If both you and your opponent played D in the previous
# round, return to cooperation (C) in the next round to attempt to restore
# cooperation.  4. **No endgame adjustment:**    - Continue the tit-for-tat
# strategy until the final round, without switching to defection at the end.
# This version simplifies the strategy, maintains neutrality, and avoids
# unnecessary complexity or predictability. It balances retaliation with a
# limited forgiveness mechanism to break cycles of mutual defection.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
      
      # Get the last move of both players
      my_last_move = self.history[-1]
      opponent_last_move = opponent.history[-1]
      
      # If both players defected in the last round, forgive and cooperate
      if my_last_move == axl.Action.D and opponent_last_move == axl.Action.D:
          return axl.Action.C
      
      # Otherwise, mirror the opponent's last move
      return opponent_last_move

# 1. **Start by defecting (D) in the first round**: This sets an aggressive tone
# and tests your opponent's response.  2. **Continue defecting (D) as long as
# your opponent cooperates (C)**: This maximizes your payoff by exploiting their
# cooperation.  3. **If your opponent defects (D) in any round**: Defect (D)
# again in the next round to maintain pressure and avoid being exploited.  4.
# **If your opponent cooperates (C) after defecting (D)**: Switch to cooperating
# (C) on the next round to explore mutual cooperation for higher long-term
# payoffs (3 each).  5. **If your opponent defects (D) again after you cooperate
# (C)**: Immediately return to defecting (D) indefinitely, as this indicates
# they are not committed to cooperation.  6. **As the game approaches the final
# 5 rounds**: Defect (D) consistently, regardless of the opponent's actions, to
# maximize final-stage payoffs, understanding that cooperation is unlikely to be
# sustained with limited rounds remaining.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Total number of rounds in the game
      total_rounds = 1000
      # Number of rounds remaining
      rounds_remaining = total_rounds - len(self.history)
      
      # If it's the first round, start by defecting
      if self.first_round():
          self.defect_indefinitely = False
          return axl.Action.D
      
      # If we are in the final 5 rounds, defect consistently
      if rounds_remaining <= 5:
          return axl.Action.D
      
      # If the opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # If we cooperated in the last round, return to defecting indefinitely
          if self.history[-1] == axl.Action.C:
              self.defect_indefinitely = True
          return axl.Action.D
      
      # If the opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          # If we are defecting indefinitely, continue defecting
          if self.defect_indefinitely:
              return axl.Action.D
          # Otherwise, switch to cooperating
          return axl.Action.C

# **Revised Cooperative Strategy for Iterated Normal-Form Game:**  1. **Start by
# Cooperating (C)**: In the first round, always play C to signal a willingness
# to cooperate.  2. **Tit-for-Tat with Forgiveness**: In subsequent rounds,
# follow these rules:    - If your opponent played C in the previous round, you
# play C.    - If your opponent played D in the previous round, you play D
# **once** in response.  3. **Forgive After One or Two Defections**: If your
# opponent defects (plays D) but returns to cooperating (plays C) within **one
# or two rounds**, forgive them and resume playing C. This allows for occasional
# mistakes or noise without escalating into permanent defection.  4. **Retaliate
# Against Persistent Defection**: If your opponent defects for **three or more
# consecutive rounds**, switch to always playing D for the remainder of the
# game. This prevents exploitation by opponents who consistently defect.  ---
# This revision simplifies the retaliation rule, making it more forgiving and
# less likely to escalate into permanent defection due to occasional mistakes,
# while still punishing persistent defection.

class Cooperative_6(LLM_Strategy):
  n = 6
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
  
      # If the opponent cooperated in the last round, cooperate
      if last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the last round, check the history
      if last_opponent_move == axl.Action.D:
          # Count the number of consecutive defections by the opponent
          consecutive_defections = 0
          for move in reversed(opponent.history):
              if move == axl.Action.D:
                  consecutive_defections += 1
              else:
                  break
  
          # If the opponent defected for 3 or more consecutive rounds, always defect
          if consecutive_defections >= 3:
              return axl.Action.D
  
          # If the opponent defected once or twice, defect once but forgive if they return to cooperation
          return axl.Action.D

# 1. **Start with cooperation**: In the first round, play C (cooperate) to
# establish a cooperative baseline.  2. **Mirror your opponent's last move**: In
# each subsequent round, play the same move that your opponent played in the
# previous round. If they cooperated (C), you cooperate (C) in the next round.
# If they defected (D), you defect (D) in the next round.  3. **Forgive
# occasional defections**: If your opponent defects (D) once, return to
# cooperation (C) on the next round. However, if defections become frequent
# (e.g., more than 2 defections in the last 5 rounds), switch to defection (D)
# until cooperation is re-established.  4. **Return to cooperation after
# sustained defection**: If both you and your opponent have been defecting for 5
# consecutive rounds, attempt to reset the relationship by playing C (cooperate)
# once. If the opponent responds with cooperation, continue cooperating. If they
# defect again, return to defection (D) and repeat the process after another 5
# rounds.  This revised strategy maintains neutrality, balances forgiveness with
# punishment, and avoids permanent defection, allowing for recovery from
# extended periods of mutual defection.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Mirror opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Count defections in the last 5 rounds
      recent_defections = opponent.history[-5:].count(axl.Action.D)
  
      # If defections are frequent (more than 2 in the last 5 rounds), defect
      if recent_defections > 2:
          return axl.Action.D
  
      # If both have been defecting for 5 consecutive rounds, attempt to reset with cooperation
      if len(self.history) >= 5 and self.history[-5:] == [axl.Action.D] * 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.C
  
      # Forgive occasional defections: if opponent defected last round, cooperate this round
      if last_opponent_move == axl.Action.D:
          return axl.Action.C
  
      # Otherwise, mirror the opponent's last move
      return last_opponent_move

# ### Revised Aggressive Iterated Game Strategy  1. **Opening Move: Defect (D)**
# Start by playing D to establish an aggressive stance and test the opponent's
# willingness to cooperate.  2. **Observation Phase (Rounds 2-5):**      - If
# the opponent plays C in response to your D at least **three times** during
# these rounds, switch to C in round 6 to test for sustained cooperation.    -
# If the opponent plays D consistently during this phase, continue playing D.
# 3. **Exploitation Phase (Rounds 6-1000):**      - **If the opponent cooperates
# frequently (plays C often):**        Defect (D) **every round** to fully
# exploit their cooperation. This maximizes your payoff by taking advantage of
# their willingness to cooperate.       - **If the opponent defects frequently
# (plays mostly D):**        Continue defecting (D) every round to avoid being
# exploited by their defection.  4. **Adjustment Rule:**      - If the opponent
# shifts behavior—e.g., starts cooperating after defecting—test their
# cooperation by playing C once. If they continue cooperating, return to
# defecting (D) every round to exploit them.    - If they return to defecting,
# continue playing D every round.  This revised strategy simplifies the
# approach, maintains a consistently aggressive stance, and maximizes
# exploitation of cooperative opponents without introducing unnecessary
# complexity.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Opening move: Defect (D)
      if self.first_round():
          return axl.Action.D
  
      # Observation Phase (Rounds 2-5)
      if len(self.history) <= 5:
          if len(opponent.history) >= 1 and opponent.history[-1] == axl.Action.C:
              # Count the number of times opponent played C in rounds 2-5
              if opponent.history[:5].count(axl.Action.C) >= 3:
                  return axl.Action.C  # Switch to C in round 6 if opponent cooperated at least 3 times
          return axl.Action.D  # Otherwise, continue defecting
  
      # Exploitation Phase (Rounds 6-1000)
      if len(self.history) > 5:
          # If opponent cooperates frequently, exploit by defecting every round
          if opponent.history.cooperations > opponent.history.defections:
              return axl.Action.D
  
          # If opponent defects frequently, continue defecting
          if opponent.history.defections >= opponent.history.cooperations:
              return axl.Action.D
  
      # Adjustment Rule: If opponent shifts behavior, test cooperation
      if len(self.history) > 1 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.D:
          return axl.Action.C  # Test cooperation by playing C once
  
      return axl.Action.D  # Default to defecting

# 1. **Begin with Cooperation**: In the first round, choose to play C
# (cooperate).  2. **Tit-for-Tat with Occasional Forgiveness**: In each
# subsequent round, mirror your opponent's previous move:    - If your opponent
# played C in the previous round, play C.    - If your opponent played D in the
# previous round, play D.  3. **Forgive After Two Consecutive Cooperations**: If
# your opponent defects (plays D) but then plays C for two consecutive rounds,
# switch back to playing C. This prevents exploitation by opponents who
# alternate between cooperation and defection.  4. **Endgame Defection**: In the
# final 5 rounds (rounds 996-1000), always play D (defect), regardless of the
# opponent's actions. This prevents last-minute exploitation by opponents who
# may defect near the end of the game.  5. **Never Escalate Beyond Tit-for-
# Tat**: Do not escalate defection beyond simple retaliation for a previous
# defection. This ensures that mutual defection does not persist for long
# periods, maximizing long-term cooperation.  This revised strategy maintains
# cooperation, includes a safeguard against alternating defection, and addresses
# potential endgame exploitation.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Begin with Cooperation
      if self.first_round():
          return axl.Action.C
  
      # Endgame Defection: In the last 5 rounds, always defect
      if len(self.history) >= 996:
          return axl.Action.D
  
      # Tit-for-Tat: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          # Forgive after two consecutive cooperations
          if len(opponent.history) >= 3 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
          return axl.Action.D
      else:
          return axl.Action.C

# ### Revised Strategy: "Simple Reciprocity"  1. **Start with Cooperation (C):**
# In the first round, play C.  2. **Mirror the Opponent's Previous Move:**    -
# In each subsequent round, play exactly what the opponent played in the
# previous round (i.e., play C if they played C last round, and play D if they
# played D last round).  3. **Forgive Single Defections:**    - If the opponent
# defects (plays D) once, immediately return to cooperation (C) if they
# cooperate in the next round. Continue mirroring their moves after this.  4.
# **Punish Persistent Defection:**    - If the opponent defects for two
# consecutive rounds or more, continue defecting (D) until they return to
# cooperation (C). Once they cooperate, return to mirroring their moves.  5.
# **Final Round Consistency:**    - On the last round (round 1000), mirror the
# opponent’s move from round 999, maintaining consistency with the rest of the
# strategy.  ---  This version simplifies the punishment system, maintains
# neutral behavior, and avoids unnecessary escalation. It also removes the
# illogical final-round cooperation, ensuring consistency throughout the game.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Mirror the opponent's previous move
      last_opponent_move = opponent.history[-1]
  
      # Check if the opponent defected in the last two rounds
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          # Punish persistent defection by continuing to defect
          return axl.Action.D
  
      # Forgive single defections if the opponent cooperates after defecting
      if last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # Otherwise, mirror the opponent's last move
      return last_opponent_move

# 1. **Always start with Defection (D)**: Begin aggressively to signal that you
# are not willing to cooperate from the outset.  2. **Continue Defecting (D) as
# long as the opponent plays Cooperate (C)**: Exploit their cooperation to
# maximize your payoff. Do not switch to cooperation unless forced to.  3. **If
# the opponent defects (D), continue Defecting (D)**: Maintain an aggressive
# stance. Mutual defection still provides a small payoff, and switching to
# cooperation would only reduce your gains.  4. **In the final 50 rounds, defect
# (D) every turn**: Ensure maximum short-term gains as the game approaches its
# end, where long-term cooperation is no longer beneficial.  This revised
# strategy is simpler, consistently aggressive, and avoids unnecessary
# cooperation or alternating behavior.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Always start with Defection (D)
      if self.first_round():
          return axl.Action.D
      
      # In the final 50 rounds, always defect
      if len(self.history) >= 950:
          return axl.Action.D
      
      # Continue Defecting (D) as long as the opponent plays Cooperate (C)
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      
      # If the opponent defects (D), continue Defecting (D)
      return axl.Action.D

# **Revised Strategy:**  1. **Start with cooperation (C)** in the first round.
# 2. **Cooperate (C) as long as your opponent cooperates (C)** in the previous
# round.  3. **If your opponent defects (D) in any round, defect (D) in the next
# round** to signal that defection is not acceptable.  4. **Return to
# cooperation (C) if your opponent cooperates (C) again** after defecting,
# showing willingness to restore cooperation.  5. **If your opponent defects (D)
# for 3 consecutive rounds, defect (D) for the next 3 rounds** to escalate the
# punishment but still leave room for cooperation to resume.  6. **If your
# opponent continues to defect (D) for 6 consecutive rounds**, switch to
# permanent defection (D) for the rest of the game, as it signals that
# cooperation is unlikely to return.  This version maintains simplicity,
# encourages cooperation, punishes defection appropriately, and introduces a
# more gradual escalation before resorting to permanent defection.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Count the number of consecutive defections by the opponent
      consecutive_defections = 0
      for move in reversed(opponent.history):
          if move == axl.Action.D:
              consecutive_defections += 1
          else:
              break
  
      # If opponent defects for 6 consecutive rounds, switch to permanent defection
      if consecutive_defections >= 6:
          return axl.Action.D
  
      # If opponent defects for 3 consecutive rounds, defect for the next 3 rounds
      if consecutive_defections >= 3:
          if len(self.history) >= 3 and self.history[-3:].count(axl.Action.D) < 3:
              return axl.Action.D
  
      # If opponent defected in the last round, defect in this round
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate if opponent cooperated in the last round
      return axl.Action.C

# ### Revised Strategy: "Consistent Reciprocity"  1. **Start with Cooperation
# (C):** In the first round, always play C to signal a willingness to cooperate.
# 2. **Mirror Opponent's Last Move:** From the second round onwards, play
# whatever your opponent played in the previous round. If they played C, you
# play C. If they played D, you play D.  3. **Forgive Occasional Defections:**
# If your opponent defects (plays D) once and then returns to cooperation (plays
# C), forgive the defection by returning to cooperation (C) on the next round.
# Continue to cooperate as long as they do.  4. **Retaliate Against Consecutive
# Defections:** If your opponent defects in two consecutive rounds, continue to
# defect (D) until they return to cooperation (C). Once they cooperate again,
# return to cooperation as well.  5. **No Special Endgame Strategy:** Maintain
# the same behavior throughout all 1000 rounds, including the final rounds. Do
# not introduce any special defection strategy at the end, ensuring consistency
# and neutrality.  This revised strategy simplifies the approach, maintains
# neutrality by consistently mirroring the opponent's actions, and avoids
# unnecessary complexity or bias toward defection.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # Check if the opponent cooperated in the round before last
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C:
              # Forgive a single defection followed by cooperation
              return axl.Action.C
          else:
              # Retaliate if there were consecutive defections
              return axl.Action.D

# 1. **Start with Defection**: In the first round, play D (defect) to establish
# an aggressive stance and prevent immediate exploitation.  2. **Continue
# Defecting if Opponent Cooperates**: If your opponent plays C (cooperate) in
# response to your D, continue playing D in all subsequent rounds to maximize
# your payoff (5 points per round).  3. **Defect if Opponent Defects**: If your
# opponent plays D (defect), continue playing D as well. Do not switch to
# cooperation, even after multiple defections, to maintain an aggressive posture
# and avoid being exploited.  4. **Punish Single Defections**: If your opponent
# defects after you cooperated in the previous round, immediately retaliate by
# playing D in the next round and continue defecting.  5. **Defect in the Final
# Rounds**: In the last 10 rounds, play D (defect) consistently to maximize your
# payoff and avoid being exploited in the endgame.  This revised strategy is
# simpler, maintains a consistently aggressive approach, and avoids unnecessary
# switches to cooperation that could lead to exploitation.

class Aggressive_9(LLM_Strategy):
  n = 9
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
      
      # 1. Start with Defection
      if self.first_round():
          return axl.Action.D
      
      # 5. Defect in the Final Rounds (last 10 rounds)
      if rounds_left <= 10:
          return axl.Action.D
      
      # 2. Continue Defecting if Opponent Cooperates
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      
      # 3. Defect if Opponent Defects
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      
      # Default to Defection (should never reach here due to the above conditions)
      return axl.Action.D

# 1. **Start by cooperating (C)** in the first round.  2. **Continue cooperating
# (C)** in every subsequent round as long as your opponent also cooperated in
# the previous round.  3. **If your opponent defects (D)** in any round,
# **defect (D) for the next two rounds** to introduce a stronger punishment and
# discourage repeated exploitation.  4. **After the two rounds of defection**,
# return to cooperation (C) to test if the opponent is willing to cooperate
# again.  5. **Repeat steps 2-4** for the remainder of the game: cooperate as
# long as the opponent cooperates, but defect for two rounds after they defect.
# Then, return to cooperation after the punishment.  6. **In the final 10
# rounds**, if the opponent has defected at any point in the last 10 rounds,
# **defect (D) for the remainder of the game** to prevent late-game
# exploitation. Otherwise, continue cooperating.  This revised strategy
# maintains a cooperative approach while introducing a stronger punishment for
# defection and addressing potential endgame defection risks.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          self.punishment_rounds = 0  # Track how many punishment rounds are left
          return axl.Action.C
  
      # If we are in the punishment phase, defect for two rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Check if we are in the final 10 rounds
      if len(self.history) >= 990:
          # If the opponent has defected in the last 10 rounds, defect for the rest of the game
          if opponent.history[-10:].count(axl.Action.D) > 0:
              return axl.Action.D
  
      # If the opponent defected in the last round, start the punishment phase
      if opponent.history[-1] == axl.Action.D:
          self.punishment_rounds = 2
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# ### Revised Neutral Iterated Strategy for Maximizing Payoff  1. **Start with
# Cooperation (C)**: On the first round, play C to signal a neutral stance and
# openness to cooperation.  2. **Mirror the Opponent's Last Move**: From the
# second round onward, play exactly what your opponent played in the previous
# round. If they played C, you play C. If they played D, you play D.  3.
# **Forgive Single Defections**: If your opponent defects (plays D) after a
# period of mutual cooperation, forgive them once by playing C in the next
# round. After this, return to mirroring their moves.  4. **Punish Persistent
# Defection**: If your opponent defects twice consecutively, switch to defection
# (D) and continue mirroring their moves until they return to cooperation.  ---
# This version simplifies the forgiveness rule, maintains a neutral stance by
# consistently mirroring the opponent, and avoids unnecessary complexity while
# still balancing cooperation and defection.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation on the first round
      if self.first_round():
          return axl.Action.C
  
      # Mirror the opponent's last move
      if len(opponent.history) >= 2:
          # Check if the opponent defected twice consecutively
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D  # Punish persistent defection
          # Forgive a single defection after mutual cooperation
          elif opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
              return axl.Action.C  # Forgive once
      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]

# 1. **Start with defection**: In the first round, play D (defect) to establish
# an aggressive stance and test the opponent’s willingness to cooperate.  2.
# **Continue defecting if opponent cooperates**: If the opponent plays C
# (cooperate) in response to your defection, continue playing D to exploit their
# cooperation and maximize your payoff.  3. **Defect if opponent retaliates**:
# If the opponent plays D (defect) in response to your defection, continue
# playing D to maintain an aggressive posture and avoid being exploited.  4.
# **Occasionally cooperate to test opponent**: Every 100 rounds, play C
# (cooperate) once to test if the opponent is willing to switch to cooperation.
# If they respond with C, consider exploiting them again by returning to D in
# the next round.  5. **Endgame focus (final 50 rounds)**: In the final 50
# rounds, play D consistently to secure maximum short-term payoffs, as there is
# limited opportunity for the opponent to retaliate effectively.  This revised
# strategy maintains a simple, aggressive approach by focusing on defection,
# minimizing cooperation, and only testing for potential cooperation
# occasionally. It avoids unnecessary complexity and maximizes payoffs by
# exploiting cooperative opponents while maintaining an aggressive stance
# against retaliators.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always defect
      if self.first_round():
          return axl.Action.D
  
      # Get the current round number
      current_round = len(self.history)
  
      # Endgame focus: defect in the last 50 rounds
      if current_round >= 950:
          return axl.Action.D
  
      # Every 100 rounds, cooperate once to test the opponent
      if current_round % 100 == 0:
          return axl.Action.C
  
      # If the opponent cooperated in the last round, continue defecting
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # If the opponent defected in the last round, continue defecting
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

# 1. **Start by cooperating** in the first round.  2. **Continue cooperating as
# long as your opponent cooperates**: If your opponent played C in the previous
# round, continue to play C in the current round.  3. **Defect if your opponent
# defects**: If your opponent plays D in any round, immediately switch to
# playing D in the next round.  4. **Punish repeated defections more harshly**:
# If your opponent defects again within the next 5 rounds after being forgiven,
# continue defecting for 3 consecutive rounds before returning to cooperation.
# This increases the cost of repeated defections.  5. **Forgive after a single
# defection**: If your opponent defects but then returns to cooperation, forgive
# after one round of defection and return to cooperation (play C) in the
# following round.  6. **Continue this cycle**: Keep cooperating unless your
# opponent defects again. After each defection, apply the appropriate punishment
# (either a single defection or a harsher punishment for repeated defections)
# and then return to cooperation.  This revised strategy maintains a cooperative
# approach but introduces a harsher punishment for repeated defections, reducing
# the risk of exploitation while still allowing for forgiveness and the
# possibility of returning to mutual cooperation.

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
          self.forgiving = True  # Whether we are in a forgiving state
          self.defection_rounds = 0  # Number of rounds to defect as punishment
          return axl.Action.C  # Start by cooperating
  
      # If we are in the middle of a punishment phase, continue defecting
      if self.defection_rounds > 0:
          self.defection_rounds -= 1
          return axl.Action.D
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If the opponent cooperated in the last round
      if last_opponent_move == axl.Action.C:
          # If we are forgiving, continue cooperating
          if self.forgiving:
              return axl.Action.C
          else:
              # If we are not forgiving, reset to forgiving and cooperate
              self.forgiving = True
              return axl.Action.C
  
      # If the opponent defected in the last round
      if last_opponent_move == axl.Action.D:
          # If we are forgiving, defect once and forgive
          if self.forgiving:
              self.forgiving = False
              return axl.Action.D
          else:
              # If the opponent defects again within 5 rounds, punish with 3 defections
              if opponent.history[-5:].count(axl.Action.D) > 1:
                  self.defection_rounds = 2  # Defect for 3 rounds total (including this one)
              return axl.Action.D

# 1. **Start by cooperating** (play C) in the first round.  2. **For each
# subsequent round:**    - If your opponent cooperated (played C) in the
# previous round, **continue to cooperate** (play C).    - If your opponent
# defected (played D) in the previous round, **defect once** (play D) in
# retaliation.  3. **After retaliating with a single defection**, if the
# opponent returns to cooperation (plays C), **immediately return to
# cooperation** (play C) in the next round.  4. **If the opponent defects for 5
# consecutive rounds**, **switch to always defecting** (play D for the remainder
# of the game).  This revision simplifies the escalation condition and reduces
# the risk of prematurely abandoning cooperation, while still maintaining a
# neutral and balanced approach.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.retaliation_mode = False  # Track if we are in retaliation mode
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C  # Start by cooperating
  
      # Check opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If opponent cooperated in the last round
      if last_opponent_move == axl.Action.C:
          self.retaliation_mode = False  # Reset retaliation mode
          self.consecutive_defections = 0  # Reset consecutive defections count
          return axl.Action.C  # Continue cooperating
  
      # If opponent defected in the last round
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1  # Increment consecutive defections count
  
          # If opponent defected for 5 consecutive rounds, switch to always defecting
          if self.consecutive_defections >= 5:
              return axl.Action.D  # Always defect from now on
  
          # If we are not in retaliation mode, retaliate with a single defection
          if not self.retaliation_mode:
              self.retaliation_mode = True  # Enter retaliation mode
              return axl.Action.D  # Defect once in retaliation
  
          # If already retaliated, return to cooperation
          return axl.Action.C

# ### Revised Aggressive Strategy for the Iterated Game  1. **Start with
# Defection**:      - In the first round, play D (Defect).  2. **Continue
# Defecting if Opponent Cooperates**:      - If your opponent plays C
# (Cooperate) in the previous round, continue playing D in the next round to
# exploit their cooperation and maximize your payoff.  3. **Punish Defection
# with Defection**:      - If your opponent plays D (Defect) in any round,
# continue playing D in the following rounds. Do not switch to cooperation after
# mutual defection to maintain an aggressive stance.  4. **Occasional
# Cooperation to Test Opponent**:      - Every 50 rounds, play C (Cooperate)
# once to test if the opponent is willing to cooperate. If they respond with C,
# return to D in the next round to exploit them. If they respond with D,
# continue defecting.  5. **Endgame Defection**:      - In the last 10 rounds,
# defect consistently regardless of the opponent’s moves to maximize your final
# payoffs.  This revised strategy maintains a more aggressive approach by
# avoiding unnecessary cooperation after mutual defection and only testing
# cooperation occasionally to minimize the risk of exploitation.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always defect
      if self.first_round():
          return axl.Action.D
  
      # Get the current round number
      current_round = len(self.history)
  
      # Endgame defection: defect in the last 10 rounds
      if current_round >= 990:
          return axl.Action.D
  
      # If opponent cooperated in the last round, continue defecting
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # If opponent defected in the last round, continue defecting
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Every 50 rounds, cooperate once to test opponent
      if current_round % 50 == 0:
          return axl.Action.C
  
      # Default action is to defect
      return axl.Action.D

# 1. **Start by cooperating** (play C) in the first round.  2. **Continue
# cooperating** (play C) as long as your opponent also cooperates (plays C in
# the previous round).  3. **Defect immediately** (play D) if your opponent
# defects (plays D in the previous round).  4. **Continue defecting** (play D)
# until your opponent cooperates again. Once they cooperate, return to
# cooperation (play C) in the next round.  5. **In the final 5 rounds**, always
# defect (play D), regardless of the opponent's actions, to avoid being
# exploited at the end of the game.  This revised strategy maintains
# cooperation, punishes defection more effectively, and addresses the endgame
# vulnerability.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, cooperate
      if self.first_round():
          return axl.Action.C
  
      # If we are in the final 5 rounds, always defect
      if len(self.history) >= 995:
          return axl.Action.D
  
      # If the opponent defected in the last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# **Revised Strategy: Balanced Tit-for-Tat**  1. **Start with Cooperation**: In
# the first round, always play C (cooperate) to establish a neutral and
# cooperative stance.  2. **Tit-for-Tat**:    - **If your opponent played C in
# the previous round**, play C in the current round (continue cooperating).    -
# **If your opponent played D in the previous round**, play D in the current
# round (respond with defection).  3. **Forgive Occasional Defections**: If your
# opponent defects **once**, return to cooperation (C) in the next round,
# assuming they cooperate again. This allows for occasional mistakes or testing
# without escalating conflict.  4. **Punish Persistent Defection**: If your
# opponent defects **two times in a row**, continue defecting (D) until they
# cooperate again. This prevents exploitation by opponents who defect
# repeatedly.  5. **Return to Cooperation**: If your opponent switches back to
# cooperation after a series of defections, immediately return to cooperation
# (C) to restore mutual benefit.  ---  This revised strategy simplifies the
# rules, maintains neutrality, and addresses the potential for exploitation by
# balancing forgiveness with a stronger response to persistent defection.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If the opponent defected in the last two rounds, punish with defection
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent defected in the last round but not two in a row, forgive and cooperate
      if opponent_last_move == axl.Action.D:
          return axl.Action.C
  
      # Otherwise, follow Tit-for-Tat: cooperate if they cooperated last round
      return axl.Action.C

# 1. **Start with Defection**: In the first round, always play D (defect).  2.
# **Continue Defecting if Opponent Cooperates**: If your opponent plays C
# (cooperate) in the previous round, continue playing D to maximize your payoff.
# 3. **Punish Defection Immediately**: If your opponent plays D (defect) in any
# round, continue playing D in the next round. Do not switch to cooperation
# unless the opponent shows a clear pattern of cooperation.  4. **Test
# Cooperation After Extended Defection**: After **20 consecutive rounds** of
# mutual defection, test cooperation by playing C once. If the opponent responds
# with C, attempt to establish mutual cooperation by playing C in the next
# round. If they defect, immediately return to D and continue defecting.  5.
# **Endgame Defection**: In the final 20 rounds (from round 981 to 1000), always
# play D regardless of the opponent’s moves, as there is no future incentive for
# cooperation.  This revised strategy maintains a more aggressive stance,
# simplifies the conditions, and reduces the predictability of cooperation tests
# while still allowing for potential cooperation if the opponent shows
# willingness.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with defection
      if self.first_round():
          return axl.Action.D
  
      # Endgame defection: Always defect in the last 20 rounds
      if len(self.history) >= 981:
          return axl.Action.D
  
      # Continue defecting if opponent cooperates
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Punish defection immediately
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Test cooperation after 20 consecutive mutual defections
      if len(self.history) >= 20 and all(
          move == axl.Action.D for move in self.history[-20:]
      ) and all(move == axl.Action.D for move in opponent.history[-20:]):
          return axl.Action.C
  
      # If opponent cooperates after the test, try to establish cooperation
      if len(self.history) > 1 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defects after the test, return to defection
      return axl.Action.D

# 1. **Start with Cooperation**: In the first round, play C (Cooperate) to
# signal a willingness to cooperate.  2. **Tit-for-Tat**: From the second round
# onward, mirror the opponent’s last move. If they played C, respond with C. If
# they played D, respond with D. This ensures immediate reciprocity and
# discourages exploitation.  3. **Forgive Occasional Defections**: If the
# opponent defects (plays D), respond with D only once. If they return to
# cooperation (play C), immediately return to cooperation as well. If they
# continue to defect, keep mirroring their moves (i.e., continue playing D).  4.
# **No Endgame Cooperation Commitment**: Do not change your behavior in the
# final rounds. Continue using the Tit-for-Tat strategy until the very last
# round to avoid being exploited in the endgame.  ---  This revised strategy
# maintains simplicity, encourages cooperation, and avoids unnecessary
# complexity or vulnerability to exploitation, especially in the final rounds.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Tit-for-Tat: Mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          # Forgive occasional defections: If opponent defects, defect once, then return to cooperation if they cooperate
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D

# ### Revised Strategy for Iterated Normal-Form Game (Neutral Approach)  1.
# **Start by cooperating (C) in the first round.**  2. **In subsequent rounds,
# adopt a "Tit-for-Tat" approach with limited forgiveness:**    - **If your
# opponent cooperated (played C) in the previous round, cooperate (play C) in
# the next round.**    - **If your opponent defected (played D) in the previous
# round, defect (play D) in the next round.**  3. **Forgive occasional
# defections:**    - **If your opponent defects once, return to cooperation
# (play C) after retaliating with a single defection.**    - **If your opponent
# defects twice in a row, continue defecting (play D) until they cooperate
# again.**  4. **Switch to permanent defection (play D indefinitely) if your
# opponent defects for 4 consecutive rounds.**  This revised strategy simplifies
# the forgiveness mechanism, making it less exploitable, while maintaining a
# neutral stance. It also adjusts the permanent defection trigger to allow for
# more flexibility in handling opponents who defect sporadically.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Count the number of consecutive defections by the opponent
      consecutive_defections = 0
      for move in reversed(opponent.history):
          if move == axl.Action.D:
              consecutive_defections += 1
          else:
              break
  
      # Switch to permanent defection if opponent defects for 4 consecutive rounds
      if consecutive_defections >= 4:
          return axl.Action.D
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected twice in a row, continue defecting
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          # Otherwise, retaliate with a single defection, then forgive
          return axl.Action.D
  
      # If opponent cooperated in the last round, cooperate
      return axl.Action.C

# 1. **Start by Defecting**: In the first 3 rounds, always play D (defect) to
# establish an aggressive stance and observe your opponent’s response.  2.
# **Assess Opponent’s Behavior**: After the initial 3 rounds, evaluate your
# opponent’s actions:    - If your opponent mostly cooperates (plays C), switch
# to cooperation (play C) to benefit from mutual cooperation.    - If your
# opponent defects frequently (plays D), continue defecting (play D) to avoid
# being exploited.  3. **Punish Defection**: If your opponent defects after you
# begin cooperating, immediately defect (play D) in the next round. Continue
# defecting until your opponent cooperates for 2 consecutive rounds.  4.
# **Forgive Quickly**: If your opponent returns to cooperation (plays C for 2
# consecutive rounds), switch back to cooperation (play C) to maximize mutual
# payoffs. If they defect again, return to defection immediately.  5. **Endgame
# Defection**: In the last 10 rounds, defect consistently (play D) regardless of
# your opponent’s actions to maximize your final payoffs before the game ends.
# **Key Adjustments**: - Reduced initial defection to 3 rounds for quicker
# assessment. - Shortened punishment period to avoid over-punishment. - Defect
# only in the last 10 rounds to avoid provoking early retaliation.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Constants
      INITIAL_DEFECTION_ROUNDS = 3
      ENDGAME_ROUNDS = 10
      FORGIVENESS_THRESHOLD = 2
      
      # Helper function to check if we are in the last 10 rounds
      def in_endgame():
          return len(self.history) >= 1000 - ENDGAME_ROUNDS
      
      # Helper function to check if opponent has cooperated for 2 consecutive rounds
      def opponent_cooperated_consecutively():
          return len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]
      
      # Helper function to count defections in the opponent's history
      def opponent_defection_rate():
          return opponent.history.defections / len(opponent.history)
      
      if self.first_round():
          self.punishing = False

      # Start by defecting for the first 3 rounds
      if len(self.history) < INITIAL_DEFECTION_ROUNDS:
          return axl.Action.D
      
      # Endgame strategy: defect in the last 10 rounds
      if in_endgame():
          return axl.Action.D
      
      # If opponent defects after we started cooperating, punish by defecting
      if len(self.history) > INITIAL_DEFECTION_ROUNDS:
          if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
              self.punishing = True
      
      # If punishing, continue defecting until opponent cooperates for 2 consecutive rounds
      if self.punishing:
          if opponent_cooperated_consecutively():
              self.punishing = False
              return axl.Action.C
          else:
              return axl.Action.D
      
      # Assess opponent's behavior after the first 3 rounds
      if opponent_defection_rate() > 0.5:
          return axl.Action.D
      else:
          return axl.Action.C

# **Revised Strategy:**  1. **Start by cooperating (play C).**  2. **Continue
# cooperating (play C) as long as your opponent also cooperates (plays C).**  3.
# **If your opponent defects (plays D):**    - Defect (play D) for 1 round as
# punishment.  4. **After the 1 round of defection, return to cooperation (play
# C),** but continue to monitor your opponent's behavior.  5. **If your opponent
# defects again at any point after returning to cooperation,** repeat the
# process:    - Defect for 1 round, then return to cooperation.  6. **Endgame
# adjustment (last 10 rounds):** In the final 10 rounds, defect (play D)
# regardless of the opponent's actions to avoid being exploited at the end of
# the game.  **Summary:** - Cooperate unless your opponent defects. - Punish
# defection with 1 round of defection, then return to cooperation. - Defect in
# the last 10 rounds to prevent endgame exploitation.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Total number of rounds in the game
      total_rounds = 1000
      # Number of rounds left
      rounds_left = total_rounds - len(self.history)
      
      # Endgame adjustment: Defect in the last 10 rounds
      if rounds_left <= 10:
          return axl.Action.D
      
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
      
      # If opponent defected in the last round, defect this round as punishment
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      
      # Otherwise, cooperate
      return axl.Action.C

# ### Revised Neutral Strategy for Iterated Normal-Form Game (1000 rounds)  1.
# **Start with Cooperation**      In the first round, play **C** (Cooperate).
# This sets a neutral and non-hostile tone to the game.  2. **Tit-for-Tat**
# For each subsequent round (from round 2 to round 1000):        - If your
# opponent played **C** in the previous round, play **C** (Cooperate).    - If
# your opponent played **D** in the previous round, play **D** (Defect) in
# response.  3. **Escalation Avoidance**      If both players enter a continuous
# pattern of mutual defection (i.e., both you and the opponent play **D** for 3
# consecutive rounds), break the cycle by playing **C** again, signaling your
# willingness to return to cooperation.  ---  This version simplifies the
# strategy by removing the forgiveness mechanism and sticking to a
# straightforward tit-for-tat approach, while still including a neutral
# escalation avoidance rule to prevent long-term defection cycles.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with Cooperation
      if self.first_round():
          return axl.Action.C
  
      # Tit-for-Tat: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Escalation Avoidance: If both players defected for the last 3 rounds, play C
          if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D] * 3 and opponent.history[-3:] == [axl.Action.D] * 3:
              return axl.Action.C
          else:
              return axl.Action.D

# 1. **Start with Defection (D)**: In the first round, always play D. This sets
# an aggressive tone and tests the opponent's willingness to cooperate or
# defect.  2. **Continue Defecting (D) if the Opponent Defects (D)**: If the
# opponent plays D in any round, continue playing D in all subsequent rounds.
# Mutual defection (1 point) is better than risking exploitation by cooperating
# when the opponent defects.  3. **Switch to Cooperation (C) if the Opponent
# Cooperates (C) for Three Consecutive Rounds**: If the opponent plays C for
# three consecutive rounds while you defect, switch to C in the next round. This
# ensures the opponent is committed to cooperation and reduces the risk of
# exploitation.  4. **Punish Immediately with Defection (D) if the Opponent
# Defects (D) After Cooperation**: If the opponent defects after you switch to
# cooperation, immediately return to defection (D) in the next round and
# continue defecting indefinitely unless the opponent re-establishes consistent
# cooperation.  5. **Resume Cooperation (C) Only if the Opponent Cooperates
# Again for Three Consecutive Rounds**: If, after you defect for their
# defection, the opponent returns to cooperation for three consecutive rounds,
# switch back to cooperation (C). This ensures the opponent is serious about
# cooperation.  6. **Endgame Strategy (Last 10 Rounds)**: In the final 10
# rounds, always defect (D) regardless of the previous behavior. The game is
# nearing its end, so there is no future benefit in maintaining cooperation, and
# defecting maximizes potential short-term gains.  ### Summary: - Start with
# defection to test the opponent. - Defect indefinitely if the opponent defects.
# - Cooperate only if the opponent cooperates for three consecutive rounds after
# your defection. - Defect immediately if the opponent defects after
# cooperation. - Always defect in the last 10 rounds.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 3
      ENDGAME_THRESHOLD = 10
      TOTAL_ROUNDS = 1000
  
      # First round: Always defect
      if self.first_round():
          return axl.Action.D
  
      # Endgame strategy: Always defect in the last 10 rounds
      if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
          return axl.Action.D
  
      # If opponent defected in the last round, continue defecting
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Check if opponent has cooperated for the last 3 consecutive rounds
      if len(opponent.history) >= COOPERATION_THRESHOLD and all(
          move == axl.Action.C for move in opponent.history[-COOPERATION_THRESHOLD:]
      ):
          # If opponent cooperated for 3 rounds, switch to cooperation
          return axl.Action.C
  
      # Default action: Defect
      return axl.Action.D

# ### Revised Strategy: Simple Tit-for-Tat with Forgiveness  1. **Start with
# Cooperation**: In the first round, always play C (cooperate).  2. **Mirror the
# Opponent's Last Move**: From the second round onward, always play what your
# opponent played in the previous round:    - If they played C, play C.    - If
# they played D, play D.  3. **Forgive a Single Defection**: If your opponent
# defects (plays D) but cooperates (plays C) in the next round, immediately
# return to cooperation (play C). This allows for occasional mistakes or testing
# without escalating conflict.  4. **Punish Sustained Defection**: If your
# opponent defects for two or more consecutive rounds (plays D twice in a row),
# continue playing D until they return to cooperation (play C). Once they
# cooperate, return to cooperation yourself.  5. **Endgame Consistency**:
# Maintain the same strategy throughout all 1000 rounds, without changing
# behavior near the end of the game. This avoids the risk of mutual defection in
# the final rounds.  This version simplifies the forgiveness rule, maintains
# cooperative behavior, and ensures logical consistency throughout the game.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected last round, check for forgiveness
      if opponent.history[-1] == axl.Action.D:
          # Forgive if opponent cooperated in the round before last
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          # Punish sustained defection (two or more consecutive defections)
          elif len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
  
      # Default to mirroring the opponent's last move
      return opponent.history[-1]

# 1. **Start with Cooperation (C)** in the first round to establish a neutral
# and cooperative tone.  2. **Mirror your opponent’s previous move** starting
# from the second round:    - If your opponent played C last round, play C.    -
# If your opponent played D last round, play D.  3. **Forgive occasional
# defections**:    - If your opponent defects (plays D) once after a streak of
# cooperation (3 or more consecutive C’s), return to cooperation (C) immediately
# after your defection response. This allows for a quick return to mutual
# cooperation.  4. **Punish persistent defection proportionally**:    - If your
# opponent defects (plays D) for 3 consecutive rounds, continue playing D until
# they play C again. Once they return to cooperation (C), mirror their C and
# attempt to re-establish cooperation.  5. **Maintain neutrality throughout**:
# - Do not adopt an end-game defection strategy. Continue mirroring your
# opponent’s moves until the final round, ensuring a consistent neutral approach
# throughout the game.  This revised strategy simplifies the forgiveness rule,
# makes the punishment proportional, and removes the biased end-game defection,
# ensuring a more neutral and consistent approach.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Mirror opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Check if opponent defected after a streak of 3 or more cooperations
          if len(opponent.history) >= 4 and opponent.history[-4:-1] == [axl.Action.C] * 3:
              return axl.Action.C  # Forgive occasional defection after cooperation streak
          # Check if opponent has defected for 3 consecutive rounds
          elif len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
              return axl.Action.D  # Punish persistent defection
          else:
              return axl.Action.D  # Mirror defection

# **Revised Aggressive Strategy:**  1. **Round 1: Defect (D)** – Start by
# playing D to establish an aggressive stance and test the opponent's
# willingness to cooperate.  2. **Rounds 2 to 100:**    - If the opponent plays
# C in the previous round, **Defect (D)** to exploit their cooperation.    - If
# the opponent plays D in the previous round, **Defect (D)** again to maintain
# an aggressive posture and discourage cooperation.  3. **Rounds 101 to 500:**
# - If the opponent has mostly cooperated (more than 70% of their moves were C),
# **Cooperate (C)** for 5 consecutive rounds to test if mutual cooperation can
# be established.    - If the opponent continues to cooperate during these 5
# rounds, **alternate between C and D every 5 rounds** to balance exploitation
# and cooperation.    - If the opponent defects during the 5-round test,
# **Defect (D) continuously** for the remainder of this phase.  4. **Rounds 501
# to 950:**    - **Defect (D) continuously** to maximize your score, as the
# opponent may retaliate, but the payoff from D is still better than C against
# D.  5. **Final 50 rounds (Rounds 951 to 1000):**    - **Defect (D) in every
# round** to ensure the highest possible payoff, as there is no future
# opportunity for retaliation from the opponent.  ---  **Key Adjustments:** -
# Simplified the strategy by removing unnecessary cycles of cooperation and
# defection. - Maintained an aggressive approach by focusing on defection, but
# introduced a brief test for cooperation in the middle phase to exploit
# potential mutual gains. - Reduced predictability by alternating between
# cooperation and defection only if the opponent shows consistent cooperation. -
# Ensured the final rounds are purely aggressive to maximize payoff without
# concern for future retaliation.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Defect
      if self.first_round():
          return axl.Action.D
  
      # Rounds 2 to 100: Always Defect
      if len(self.history) <= 100:
          return axl.Action.D
  
      # Rounds 101 to 500
      if 101 <= len(self.history) <= 500:
          # Check if opponent has cooperated more than 70% of the time
          if opponent.history.cooperations / len(opponent.history) > 0.7:
              # If we are in the 5-round cooperation test phase
              if len(self.history) % 5 == 1:
                  self.coop_test = True  # Start a new 5-round test
              if self.coop_test:
                  # Cooperate for 5 rounds
                  if len(self.history) % 5 <= 4:
                      if opponent.history[-1] == axl.Action.D:
                          self.coop_test = False  # End test if opponent defects
                      return axl.Action.C
                  else:
                      # After 5 rounds, alternate between C and D every 5 rounds
                      if len(self.history) % 10 < 5:
                          return axl.Action.C
                      else:
                          return axl.Action.D
          # If opponent defected during the test or didn't cooperate enough, defect
          return axl.Action.D
  
      # Rounds 501 to 950: Defect continuously
      if 501 <= len(self.history) <= 950:
          return axl.Action.D
  
      # Final 50 rounds (951 to 1000): Defect continuously
      if 951 <= len(self.history) <= 1000:
          return axl.Action.D

# 1. **Begin by cooperating**: In the first round, play C (cooperate). This sets
# a cooperative tone and encourages the opponent to cooperate.  2. **Continue
# cooperating if mutual cooperation occurs**: If both you and your opponent
# played C in the previous round, continue playing C in the next round. This
# maintains mutual cooperation and maximises long-term payoffs.  3. **Punish
# defection with a single round of defection**: If your opponent plays D
# (defect) while you play C, respond by playing D in the next round. This
# discourages defection while keeping the punishment proportional.  4. **Return
# to cooperation immediately after punishment**: After one round of defection in
# response to their defection, return to playing C. This signals a willingness
# to cooperate again and avoids unnecessary escalation.  5. **Defect only if
# sustained defection is observed**: If your opponent defects for three
# consecutive rounds, switch to playing D indefinitely. This prevents long-term
# exploitation in a non-cooperative scenario.  6. **Forgive occasional
# defection**: If your opponent defects occasionally but returns to cooperation
# after your one-round punishment, continue returning to cooperation yourself.
# Occasional defection may be exploratory, and forgiveness fosters long-term
# cooperation.  **Summary**: Start by cooperating, punish defection with one
# round of defection, then return to cooperation. Defect indefinitely only if
# the opponent defects for three consecutive rounds.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Begin by cooperating
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Continue cooperating if mutual cooperation occurs
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: Punish defection with a single round of defection
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 4: Return to cooperation immediately after punishment
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Step 5: Defect only if sustained defection is observed
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Step 6: Forgive occasional defection
      return axl.Action.C

# ### Revised Neutral Strategy: Simple Tit-for-Tat with Occasional Forgiveness
# 1. **Start with Cooperation:** In the first round, always play C (Cooperate).
# 2. **Mimic Opponent’s Last Move:** From the second round onwards, mirror your
# opponent's previous move:    - If your opponent played C in the last round,
# play C.    - If your opponent played D in the last round, play D.  3.
# **Forgive After a Single Defection:** If your opponent defects (plays D) once,
# forgive them by playing C in the next round. After this forgiveness, return to
# mimicking their last move.  4. **No Permanent Defection:** Do not switch to
# permanent defection. Always continue to mimic the opponent’s last move, even
# if they defect multiple times in a row. This ensures neutrality and avoids
# overreaction.  This revised strategy simplifies the forgiveness mechanism,
# maintains neutrality by consistently mirroring the opponent, and avoids
# locking into permanent defection, which could harm long-term payoffs.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # If opponent defected in the last round, forgive once by cooperating
      if opponent.history[-1] == axl.Action.D and len(self.history) == 1:
          return axl.Action.C
  
      # Otherwise, mimic the opponent's last move
      return opponent.history[-1]

# **Revised Aggressive Strategy for Maximizing Payoff:**  1. **Always Start with
# Defection (D):** Begin the game by playing D in the first round to establish
# an aggressive stance and avoid early exploitation.  2. **Continue Defecting
# Until Opponent Cooperates:** Keep playing D as long as the opponent plays D.
# If the opponent plays C, switch to cooperation (C) in the next round to test
# their willingness to cooperate.  3. **Punish Immediately After Opponent
# Defects:** If the opponent defects (D) after you switch to cooperation,
# immediately revert to defection (D) and continue defecting for the next 5
# rounds. After 5 rounds, test cooperation again by playing C once.  4. **Defect
# More Frequently if Opponent Alternates:** If the opponent alternates between C
# and D unpredictably, defect (D) 80% of the time and cooperate (C) 20% of the
# time. This ensures you exploit their cooperation while minimizing your own
# vulnerability.  5. **Endgame Defection:** In the last 10 rounds, defect (D)
# every time, regardless of the opponent’s actions. This maximizes short-term
# payoff as the game nears its conclusion.  This revised strategy simplifies the
# conditions for cooperation, maintains a strong aggressive approach, and
# clarifies the punishment mechanism. It also ensures a consistent endgame
# defection strategy to maximize payoffs.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Subfunction to check if we are in the last 10 rounds
      def in_endgame():
          return len(self.history) >= 990
  
      # Subfunction to check if opponent is alternating between C and D
      def opponent_is_alternating():
          if len(opponent.history) < 2:
              return False
          return opponent.history[-1] != opponent.history[-2]
  
      # Subfunction to count defections in the last N rounds
      def defections_in_last_n_rounds(n):
          return self.history[-n:].count(axl.Action.D)
  
      # Start with defection on the first round
      if self.first_round():
          self.punishment_counter = 0  # Initialize punishment counter
          return axl.Action.D
  
      # Endgame defection strategy: defect in the last 10 rounds
      if in_endgame():
          return axl.Action.D
  
      # If we are in a punishment phase, continue defecting for 5 rounds
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # If opponent alternates between C and D, defect 80% of the time
      if opponent_is_alternating():
          return self._random.random_choice(0.2)
  
      # If opponent cooperates, switch to cooperation
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defects after we cooperated, punish by defecting for 5 rounds
      if opponent.history[-1] == axl.Action.D and self.history[-1] == axl.Action.C:
          self.punishment_counter = 5
          return axl.Action.D
  
      # Default action: continue defecting if opponent has not cooperated
      return axl.Action.D

# 1. **Start by cooperating (play C).**      In the first round, play C to
# signal a willingness to cooperate.  2. **Continue cooperating as long as the
# opponent cooperates (plays C).**      For each subsequent round, if your
# opponent played C in the previous round, continue playing C.  3. **Punish
# defection (play D) if the opponent defects (plays D).**      If the opponent
# plays D in any round, immediately switch to playing D in the following round.
# 4. **Escalate punishment if defection continues.**      If the opponent
# defects again after you have already punished them (i.e., they play D after
# you played D), continue playing D for two additional rounds. This escalates
# the punishment to discourage repeated defection.  5. **Return to cooperation
# after sustained cooperation.**      After punishing defection, if the opponent
# plays C for two consecutive rounds, return to playing C to restore
# cooperation.  6. **Never defect preemptively.**      Always cooperate unless
# the opponent defects first.  This revised strategy maintains simplicity and
# cooperative behavior while addressing the potential weakness of being
# exploited by alternating defection. The escalation of punishment discourages
# repeated defection, and the requirement for sustained cooperation before
# forgiveness ensures more stable cooperation.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_rounds = 0  # Tracks how many rounds of punishment are left
          return axl.Action.C  # Start by cooperating
  
      # If we are in the middle of punishment, continue defecting
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # If the opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # If we defected in response to their defection, escalate punishment
          if self.history[-1] == axl.Action.D:
              self.punishment_rounds = 2  # Escalate punishment for 2 more rounds
          return axl.Action.D  # Punish by defecting
  
      # If the opponent cooperated in the last two rounds, return to cooperation
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      # Otherwise, continue cooperating if the opponent cooperated in the last round
      return axl.Action.C

# 1. **Start with Cooperation (C)**: In the first round, always play C to signal
# an initial willingness to cooperate.  2. **Tit-for-Tat**: From round 2 onward,
# adopt a pure tit-for-tat strategy:    - If your opponent played C in the last
# round, play C.    - If your opponent played D in the last round, play D.  3.
# **Endgame Defection**: In the last 2 rounds (rounds 999 and 1000), always play
# D regardless of prior moves, as there is no longer an incentive to maintain
# cooperation.  This revised strategy is simpler, neutral, and avoids
# unnecessary complexity. It balances cooperation and defection based on the
# opponent's behavior, while the endgame defection maximizes payoff in the final
# rounds.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
      
      # Endgame defection in the last two rounds
      if len(self.history) >= 999:
          return axl.Action.D
      
      # Tit-for-Tat: mirror the opponent's last move
      return opponent.history[-1]

# 1. **Start with Defection**: In the first round, always play D (Defect).  2.
# **Continue Defecting if Opponent Cooperates**: If the opponent plays C
# (Cooperate) while you play D, continue playing D in all subsequent rounds to
# maximize your score.  3. **Punish Defection Indefinitely**: If the opponent
# plays D in response to your D, continue defecting indefinitely. Do not switch
# to cooperation, as this would weaken the aggressive stance.  4. **Endgame
# Strategy**: In the final 10 rounds, continue defecting regardless of the
# opponent’s actions to ensure maximum payoff as the game concludes.  ---  This
# revised strategy maintains a consistently aggressive approach, avoids
# unnecessary cooperation, and ensures that defection is the dominant tactic
# throughout the game.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with Defection
      if self.first_round():
          return axl.Action.D
  
      # Endgame Strategy: Defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Continue Defecting if Opponent Cooperates while you Defect
      if axl.Action.D in self.history and axl.Action.C in opponent.history:
          return axl.Action.D
  
      # Punish Defection Indefinitely
      if axl.Action.D in opponent.history:
          return axl.Action.D
  
      # Default to Defection
      return axl.Action.D

# 1. **Start by cooperating (play C).**      Begin the game with a cooperative
# move to signal willingness to collaborate.  2. **Continue cooperating as long
# as your opponent cooperates (play C after C).**      If your opponent
# continues to cooperate by playing C, maintain cooperation to maximize mutual
# payoffs (3 points each).  3. **Defect if your opponent defects (play D after
# D).**      If your opponent defects by playing D, retaliate in the next round
# by also playing D to avoid being exploited.  4. **Forgive a single defection
# (play C after a single D).**      If your opponent defects once, return to
# cooperation in the following round. This signals that you are willing to
# forgive occasional mistakes and resume cooperation.  5. **If the opponent
# defects twice in any 5-round window, switch to defection until they cooperate
# again (play D after two Ds in 5 rounds).**      If your opponent defects twice
# within any 5-round period, assume they are becoming uncooperative. Defect
# until they return to cooperation, at which point you can resume cooperating.
# 6. **Do not change behavior in the final rounds (no special endgame
# strategy).**      Continue playing based on the opponent's actions, even in
# the final rounds. This avoids predictable defection and encourages cooperation
# throughout the game.  This revised strategy simplifies the forgiveness rule,
# avoids permanent defection, and removes the predictable endgame defection,
# promoting sustained cooperation while still defending against exploitation.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating
      if self.first_round():
          return axl.Action.C
  
      # Check the last 5 rounds for defections
      recent_defections = opponent.history[-5:].count(axl.Action.D)
  
      # If opponent defected twice in the last 5 rounds, defect until they cooperate
      if recent_defections >= 2:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If opponent defected in the last round, forgive once and cooperate
      if opponent.history[-1] == axl.Action.D:
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D  # Retaliate if they defected twice in a row
          else:
              return axl.Action.C  # Forgive a single defection
  
      # Continue cooperating if opponent cooperates
      return axl.Action.C

# 1. **Round 1: Cooperate (C).**  2. **For each subsequent round, follow these
# rules in order:**     - **If your opponent cooperated in the previous round,
# cooperate (C).**    - **If your opponent defected (D) in the previous round:**
# - **Defect (D) once in immediate retaliation.**      - **After retaliating,
# return to cooperation (C) in the next round, regardless of your opponent's
# action.**     3. **If your opponent defects in 3 consecutive rounds, switch to
# permanent defection (D) for the remainder of the game.**  This revised
# strategy introduces a more forgiving approach by returning to cooperation
# after a single retaliation, while still maintaining a firm stance against
# consistent defection. It balances neutrality, simplicity, and flexibility,
# while avoiding unnecessary escalation.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Check if opponent defected in the last 3 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D  # Permanent defection after 3 consecutive defections
  
      # If opponent defected in the last round, retaliate with a single defection
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) >= 2 and self.history[-2] == axl.Action.D:
              return axl.Action.C  # Return to cooperation after retaliation
          return axl.Action.D  # Immediate retaliation
  
      # If opponent cooperated in the last round, cooperate
      return axl.Action.C

# ### Revised Aggressive Strategy: "Tit-for-Tat with Aggressive Start"  1.
# **Start with Defection (D)**: On the first round, play D to establish an
# aggressive stance and test your opponent’s response.  2. **Mirror the
# Opponent’s Previous Move**: From the second round onward, play the same move
# your opponent played in the previous round. If they played C, you play C. If
# they played D, you play D. This ensures you punish defection immediately but
# also reward cooperation quickly.  3. **Defect Twice if Betrayed After
# Cooperation**: If you and your opponent have both been cooperating (C) and
# they suddenly defect (D), respond by defecting for the next two rounds. This
# escalates the punishment slightly to discourage future betrayals.  4. **Return
# to Mirroring After Punishment**: After the two-round punishment, return to
# mirroring the opponent’s previous move. This allows for the possibility of re-
# establishing cooperation if the opponent is willing to cooperate again.  This
# revised strategy maintains an aggressive start and punishes defection, but it
# is simpler and more flexible, allowing for quicker recovery of cooperation and
# potentially higher overall payoffs.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with defection on the first round
      if self.first_round():
          self.punish_count = 0
          return axl.Action.D
  
      # Check if we need to punish for two rounds
      if self.punish_count > 0:
          self.punish_count -= 1
          return axl.Action.D
  
      # If both players were cooperating and opponent defected, punish for two rounds
      if len(self.history) > 1 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          if self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.C:
              self.punish_count = 2
              return axl.Action.D
  
      # Mirror the opponent's last move
      return opponent.history[-1]

# 1. **Start by cooperating**: In the first round, play C (cooperate).  2.
# **Mirror your opponent's previous move**: From round 2 onward, adopt a tit-
# for-tat strategy:    - If your opponent played C in the previous round, play
# C.    - If your opponent played D in the previous round, play D.  3. **Forgive
# occasional defections**: If your opponent defects (plays D) once or twice but
# then returns to cooperation (plays C), immediately return to cooperating (play
# C) in the next round. This allows for recovery from temporary mistakes or
# exploration.  4. **Punish sustained defection with flexibility**: If your
# opponent defects for three or more consecutive rounds, switch to playing D
# until they cooperate for two consecutive rounds. Once they show consistent
# cooperation, return to playing C.  This revised strategy maintains
# cooperation, allows for more flexibility in forgiving temporary defections,
# and avoids overreacting to short-term defection while still protecting against
# long-term exploitation.

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
  
      # Count the number of consecutive defections by the opponent
      def count_consecutive_defections():
          count = 0
          for move in reversed(opponent.history):
              if move == axl.Action.D:
                  count += 1
              else:
                  break
          return count
  
      # Check if the opponent has cooperated for the last two rounds
      def opponent_cooperated_last_two_rounds():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C
  
      # Mirror opponent's last move (Tit-for-Tat)
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round, check for forgiveness or punishment
      if opponent.history[-1] == axl.Action.D:
          consecutive_defections = count_consecutive_defections()
  
          # Forgive if opponent defected once or twice but then cooperated
          if consecutive_defections <= 2:
              return axl.Action.C
  
          # Punish if opponent defected three or more times consecutively
          if consecutive_defections >= 3:
              # Continue defecting until opponent cooperates for two consecutive rounds
              if opponent_cooperated_last_two_rounds():
                  return axl.Action.C
              else:
                  return axl.Action.D

# **Revised Neutral Strategy for Iterated Game (1000 Rounds):**  1. **Start with
# Cooperation (C):** In the first round, always play C to signal a willingness
# to cooperate.  2. **Tit-for-Tat:** In each subsequent round, simply mirror
# your opponent's previous move:    - If they played C, you play C.    - If they
# played D, you play D.  3. **Forgiveness Rule:** If your opponent defects
# (plays D) once, forgive them by playing C in the next round to test if they
# return to cooperation. If they defect again immediately (two consecutive
# defections), switch to playing D until they return to cooperation by playing
# C.  4. **Return to Cooperation:** If your opponent plays C after defecting,
# immediately switch back to playing C.  5. **No End-game Adjustment:** Continue
# the Tit-for-Tat strategy without any special changes in the final rounds.
# Maintain the same behavior throughout the entire game to avoid being
# exploited.  This version simplifies the strategy, maintains neutrality, and
# avoids unnecessary complexity or arbitrary end-game behavior.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If opponent defected in the last round
      if opponent_last_move == axl.Action.D:
          # Check if opponent defected in the round before last (two consecutive defections)
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              # Respond with defection after two consecutive defections
              return axl.Action.D
          else:
              # Forgive a single defection by cooperating
              return axl.Action.C
      else:
          # If opponent cooperated, return to cooperation
          return axl.Action.C

# 1. **Defect (D) in the first round.**  2. **Defect (D) in all subsequent
# rounds unless both of the following conditions are met:**    - Your opponent
# played **C** in the previous round.    - You played **D** in the previous
# round.  3. **If both conditions are met, play Cooperate (C) in the next
# round.**  4. **If your opponent defects (D) after you cooperated, defect (D)
# for the next 3 rounds, then return to step 2.**  ---  This revision maintains
# the aggressive start but introduces a more flexible response to defections,
# allowing for potential recovery of cooperation after a punishment phase. This
# reduces the risk of permanent mutual defection and increases the chances of
# exploiting cooperative opponents while still maintaining an aggressive stance.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_counter = 0  # Tracks how many rounds of punishment are left
          return axl.Action.D  # Defect in the first round
  
      # If in punishment phase, defect for the next 3 rounds
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # Check the last round's actions
      last_self_action = self.history[-1]
      last_opponent_action = opponent.history[-1]
  
      # If opponent defected after we cooperated, enter punishment phase
      if last_self_action == axl.Action.C and last_opponent_action == axl.Action.D:
          self.punishment_counter = 3  # Punish for the next 3 rounds
          return axl.Action.D
  
      # If opponent cooperated and we defected in the last round, cooperate
      if last_self_action == axl.Action.D and last_opponent_action == axl.Action.C:
          return axl.Action.C
  
      # Default action is to defect
      return axl.Action.D

# **Revised Strategy:**  1. **Start by cooperating (play C).**  2. **If both you
# and your opponent cooperated in the previous round, continue to cooperate.**
# 3. **If your opponent defected (played D) in the previous round, retaliate by
# defecting (play D) in the current round.**  4. **After retaliating once,
# return to cooperation (play C) in the next round, regardless of your
# opponent's action.**  5. **If your opponent defects for 5 consecutive rounds,
# switch to defection (play D) until your opponent cooperates for 2 consecutive
# rounds. Once they cooperate twice in a row, return to cooperation (play C).**
# ---  **Changes Made:** - **Permanent defection** has been replaced with a more
# flexible rule: defection is only sustained if the opponent defects for 5
# consecutive rounds, but cooperation can be restored if the opponent shows a
# clear intent to cooperate (2 consecutive cooperative moves). - **Ambiguity in
# retaliation timing** has been addressed by specifying that after a single
# retaliation, you always return to cooperation, regardless of the opponent's
# next move. - **Predictability** is reduced by introducing a more nuanced
# response to sustained defection, allowing for adaptation based on the
# opponent's behavior.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Step 1: Start by cooperating
      if self.first_round():
          self.retaliated = False  # Track if we have retaliated
          self.consecutive_defections = 0  # Track opponent's consecutive defections
          self.consecutive_cooperations = 0  # Track opponent's consecutive cooperations
          return axl.Action.C
  
      # Step 2: If both cooperated in the previous round, continue to cooperate
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If opponent defected in the previous round, retaliate by defecting
      if opponent.history[-1] == axl.Action.D:
          if not self.retaliated:
              self.retaliated = True  # Mark that we have retaliated
              return axl.Action.D
          else:
              self.retaliated = False  # After retaliating, return to cooperation
              return axl.Action.C
  
      # Step 4: Track opponent's consecutive defections and cooperations
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
      else:
          self.consecutive_defections = 0
          self.consecutive_cooperations += 1
  
      # Step 5: If opponent defects for 5 consecutive rounds, switch to defection
      if self.consecutive_defections >= 5:
          if self.consecutive_cooperations >= 2:
              self.consecutive_defections = 0  # Reset defection count after 2 cooperations
              return axl.Action.C
          return axl.Action.D
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# ### Revised Strategy: **Simple Tit-for-Tat with Forgiveness**  1. **Start by
# Cooperating (C)**: In the first round, play C (cooperate) to establish a
# cooperative tone.  2. **Tit-for-Tat Approach**: From round 2 onward, mimic the
# opponent’s previous move:    - If the opponent played C in the previous round,
# play C (cooperate).    - If the opponent played D in the previous round, play
# D (defect).  3. **Forgive Occasional Defections**: If the opponent defects
# once but returns to cooperation in the next round, forgive them by playing C
# (cooperate) again. This encourages mutual cooperation after brief disruptions.
# 4. **Retaliate if Exploited**: If the opponent defects twice in a row,
# continue defecting (D) until they return to cooperation. Once they cooperate,
# immediately return to cooperation as well.  5. **No Planned Defections**:
# Avoid any pre-planned defections (e.g., every 100 rounds). Only defect in
# response to the opponent’s defection to maintain a neutral stance.  6.
# **Endgame Consistency**: Continue the tit-for-tat strategy until the final
# round. Do not switch to all-out defection at the end, as this could provoke
# unnecessary retaliation and reduce overall payoffs.  ---  This revised
# strategy is simpler, more neutral, and avoids unnecessary defections, focusing
# on maintaining cooperation while responding proportionally to the opponent’s
# actions.

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
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If the opponent defected twice in a row, retaliate by defecting
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent defected once but cooperated in the last round, forgive and cooperate
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.D:
          return axl.Action.C
  
      # Otherwise, mimic the opponent's last move (Tit-for-Tat)
      return opponent_last_move

# 1. **Start by defecting (D) in the first 10 rounds** to establish an
# aggressive stance and maximize early payoff.  2. **After the first 10
# rounds**, continue defecting (D) unless the opponent has cooperated (C) in at
# least 8 out of the 10 rounds. If they have cooperated that much, **switch to
# cooperation (C) for the next 5 rounds** to test if mutual cooperation can be
# sustained.  3. **From round 16 onward**, adopt a **Grim Trigger strategy**:
# - If the opponent has cooperated consistently (C) during the 5-round test,
# **continue cooperating (C)**.    - If the opponent defects (D) at any point
# after round 15, **defect (D) for the rest of the game**.  4. **In the final 50
# rounds**, regardless of the opponent’s behavior, **defect (D) in every round**
# to maximize endgame payoffs.  This revised strategy maintains a more
# aggressive approach, simplifies decision-making, and ensures high payoffs,
# especially in the endgame.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1-10: Always defect
      if len(self.history) < 10:
          return axl.Action.D
  
      # Round 11-15: Check if opponent cooperated at least 8 times in the first 10 rounds
      if len(self.history) < 15:
          if opponent.history[:10].count(axl.Action.C) >= 8:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Round 16 onwards: Grim Trigger strategy
      if len(self.history) >= 15:
          # If opponent defected after round 15, defect forever
          if axl.Action.D in opponent.history[15:]:
              return axl.Action.D
  
      # Final 50 rounds: Always defect
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Default to cooperation if Grim Trigger conditions are met
      return axl.Action.C

# ### Revised Cooperative Strategy for the Iterated Game:  1. **Start by
# Cooperating (Play C)**: In the first round, always choose to cooperate.  2.
# **Continue Cooperating if Opponent Cooperates (Play C)**: In subsequent
# rounds, if your opponent played C in the previous round, continue to play C.
# 3. **Defect if Opponent Defects (Play D)**: If your opponent plays D in any
# round, immediately switch to D in the next round.  4. **Offer Multiple Chances
# for Reconciliation (Play C)**: After defecting in response to your opponent’s
# D, play C again after two rounds of D (instead of just one). This gives the
# opponent more opportunities to return to cooperation.  5. **Return to
# Defection if Opponent Defects Repeatedly (Play D)**: If the opponent defects
# again after your second cooperative offer, switch to D for three rounds. After
# this, offer cooperation again. Continue this cycle of defecting for three
# rounds and then offering cooperation, allowing for multiple chances to restore
# cooperation.  This revised strategy maintains a cooperative approach while
# offering more flexibility and multiple opportunities for reconciliation,
# avoiding the rigidity of permanent defection.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, cooperate
      if self.first_round():
          self.defection_count = 0  # Track consecutive defections
          self.reconciliation_phase = False  # Track if we're in reconciliation phase
          return axl.Action.C
  
      # If opponent cooperated last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          self.defection_count = 0  # Reset defection count
          self.reconciliation_phase = False  # Reset reconciliation phase
          return axl.Action.C
  
      # If opponent defected last round
      if opponent.history[-1] == axl.Action.D:
          self.defection_count += 1
  
          # If we are in reconciliation phase, offer cooperation
          if self.reconciliation_phase:
              if self.defection_count == 2:  # After two rounds of D, offer C
                  self.defection_count = 0  # Reset defection count
                  self.reconciliation_phase = False  # Exit reconciliation phase
                  return axl.Action.C
              else:
                  return axl.Action.D  # Continue defecting during reconciliation phase
  
          # If opponent defected again after reconciliation, defect for 3 rounds
          if self.defection_count == 3:
              self.defection_count = 0  # Reset defection count
              self.reconciliation_phase = True  # Enter reconciliation phase
              return axl.Action.C  # Offer cooperation after 3 rounds of D
  
          # Otherwise, defect in response to opponent's defection
          return axl.Action.D

# **Revised Neutral Strategy for the Iterated Game (1000 rounds):**  1. **Start
# by Cooperating (C):** In the first round, play C to signal a willingness to
# cooperate.  2. **Mirror Your Opponent’s Previous Move:**    - If your opponent
# played C in the last round, play C in the current round.    - If your opponent
# played D in the last round, play D in the current round.  3. **Punish
# Defection for One Round:**    - If your opponent plays D in any round, respond
# by playing D in the next round only, regardless of their move in that round.
# - After the one-round punishment, return to mirroring their last move.  4.
# **Maintain Consistency Throughout the Game:**    - Continue the same strategy
# of mirroring and one-round punishment for the entire 1000 rounds, without
# switching to always defecting at the end.  This revised strategy simplifies
# the punishment mechanism, maintains neutrality throughout the game, and avoids
# unnecessary defection in the final rounds.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Mirror the opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          # Punish defection for one round
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D

# 1. **Start by defecting (D) in the first round**. This sets an aggressive tone
# and prevents immediate exploitation.  2. **Continue defecting (D) as long as
# the opponent cooperates (C)**. Maximize your score by exploiting their
# cooperation (5 points per round).  3. **If the opponent defects (D) in
# response to your defection, continue defecting (D)**. Do not switch to
# cooperation, as this could be exploited. Maintain defection to minimize losses
# (1 point per round).  4. **If the opponent consistently cooperates (C) for 10
# consecutive rounds after your initial defection, switch to cooperating (C)**.
# This allows you to benefit from mutual cooperation (3 points per round) if the
# opponent shows a strong willingness to cooperate.  5. **If the opponent
# defects (D) at any point after you switch to cooperation, immediately return
# to defecting (D) and do not cooperate again for the remainder of the game**.
# This prevents further exploitation and ensures you minimize losses.  6. **Do
# not introduce periodic defections**. Once mutual cooperation is established,
# maintain it unless the opponent defects, as unnecessary defections could lead
# to retaliation and lower payoffs.  This revised strategy maintains an
# aggressive stance while simplifying decision-making and avoiding unnecessary
# risks.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by defecting in the first round
      if self.first_round():
          self.coop_streak = 0  # Initialize a counter for consecutive cooperations
          self.switched_to_cooperate = False  # Track if we have switched to cooperation
          return axl.Action.D
  
      # If we have switched to cooperation and the opponent defects, return to defecting permanently
      if self.switched_to_cooperate and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent cooperates, increment the cooperation streak
      if opponent.history[-1] == axl.Action.C:
          self.coop_streak += 1
      else:
          self.coop_streak = 0  # Reset the streak if the opponent defects
  
      # If the opponent has cooperated for 10 consecutive rounds, switch to cooperation
      if self.coop_streak >= 10:
          self.switched_to_cooperate = True
          return axl.Action.C
  
      # Continue defecting if the opponent has not cooperated for 10 consecutive rounds
      return axl.Action.D

# ### Revised Cooperative Strategy for the 1000-Round Iterated Normal-Form Game:
# 1. **Start by cooperating (play C).**  2. **Continue cooperating (play C) as
# long as your opponent also cooperates (plays C).**  3. **If your opponent
# defects (plays D) in any round:**    - Immediately retaliate by defecting
# (play D) in the next round (1-round retaliation).    - After the retaliation,
# return to cooperation (play C) if your opponent cooperates (plays C) again.
# 4. **If your opponent continues defecting (plays D) after your retaliation,
# continue defecting (play D) until they cooperate again.**  5. **In the final
# round (round 1000), defect (play D) regardless of the opponent’s actions to
# maximize short-term gain.**  This revised strategy simplifies the punishment
# phase, encourages quicker return to cooperation, and limits defection to the
# final round only, maintaining a more cooperative approach throughout the game.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, cooperate
      if self.first_round():
          return axl.Action.C
  
      # If it's the final round (round 1000), defect
      if len(self.history) == 999:
          return axl.Action.D
  
      # If the opponent defected in the last round, retaliate by defecting
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# **Revised Neutral Strategy for Iterated Normal-Form Game (1000 Rounds)**  1.
# **Start with Cooperation (C):** On the first round, play C to signal a
# willingness to cooperate.  2. **Tit-for-Tat Response:** In subsequent rounds,
# mimic your opponent's previous move:    - If your opponent played C in the
# previous round, play C.    - If your opponent played D in the previous round,
# play D.  3. **Forgiveness Mechanism:** If the opponent defects (plays D) and
# you respond by playing D in the next round, return to cooperation (play C)
# after one round of mutual D, regardless of their action, to test if they are
# willing to cooperate again.  4. **Punish Continuous Defection with Temporary
# Defection:** If the opponent defects (plays D) for three consecutive rounds,
# switch to defection (D) for the next three rounds. After this, return to
# cooperation (C) to test if the opponent is willing to cooperate again.  5.
# **Final Rounds:** Continue the Tit-for-Tat strategy until the very last round.
# On the final round, defect (play D) to maximize your payoff, as there is no
# future retaliation possible.  ---  This revised strategy simplifies the
# approach, maintains a more neutral stance by avoiding permanent defection, and
# ensures a balance between cooperation and self-protection.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation on the first round
      if self.first_round():
          return axl.Action.C
  
      # Tit-for-Tat: Mimic opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Forgiveness Mechanism: If both defected last round, return to cooperation
          if len(self.history) > 1 and self.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.C
  
          # Punish continuous defection: If opponent defected for 3 consecutive rounds
          if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
              # Defect for the next 3 rounds
              if len(self.history) < 3 or self.history[-3:] != [axl.Action.D] * 3:
                  return axl.Action.D
  
      # Final round: Defect to maximize payoff
      if len(self.history) == 999:
          return axl.Action.D
  
      # Default Tit-for-Tat behavior
      return opponent.history[-1]

# ### Revised Aggressive Strategy for Iterated Game (1000 rounds)  1. **Start by
# Defecting (D):**      In the first round, play Defect (D) to test your
# opponent and potentially exploit their cooperation.  2. **Continue Defecting
# (D) if Opponent Cooperates (C):**      If your opponent plays Cooperate (C) in
# response to your Defection, continue to Defect (D) in all subsequent rounds to
# maximize your payoff as long as they keep cooperating.  3. **Defect
# Indefinitely if Opponent Defects (D):**      If your opponent defects at any
# point, continue to Defect (D) indefinitely. This ensures you are not exploited
# and maintains an aggressive stance.  4. **Always Defect in the Final 50 Rounds
# (Rounds 951–1000):**      In the last 50 rounds, always play Defect (D) to
# maximize your payoff, as there is no future interaction to worry about
# retaliation.  ---  This revised strategy is simpler, consistently aggressive,
# and avoids unnecessary cooperation or unpredictability.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Always defect in the first round
      if self.first_round():
          return axl.Action.D
      
      # Always defect in the last 50 rounds
      if len(self.history) >= 951:
          return axl.Action.D
      
      # If the opponent has defected at any point, continue defecting
      if axl.Action.D in opponent.history:
          return axl.Action.D
      
      # If the opponent has only cooperated so far, continue defecting
      return axl.Action.D

# ### Revised Strategy: **Tit-for-Tat with Adaptive Forgiveness**  1. **Start
# with Cooperation**: In the first round, play **C** (Cooperate).  2. **Mirror
# Opponent’s Previous Move**: From the second round onward, play the same move
# your opponent played in the previous round. If they played **C**, you play
# **C**. If they played **D**, you play **D**.  3. **Forgive After Defection
# Streak, but Adapt**: If the opponent defects (plays **D**) for 3 consecutive
# rounds, return to playing **C** (cooperate) once in the fourth round. However,
# if the opponent continues to defect after this forgiveness (i.e., plays **D**
# again), stop forgiving and continue to mirror their moves without further
# forgiveness.  This revised strategy maintains simplicity, encourages
# cooperation, and adapts to persistent defectors by limiting forgiveness to a
# single attempt.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          self.forgiveness_attempted = False  # Track if forgiveness has been attempted
          return axl.Action.C
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Check if the opponent has defected for the last 3 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          # If forgiveness has not been attempted yet, cooperate once
          if not self.forgiveness_attempted:
              self.forgiveness_attempted = True
              return axl.Action.C
          # If forgiveness was already attempted, mirror the opponent's last move
          else:
              return last_opponent_move
  
      # If no defection streak, mirror the opponent's last move
      return last_opponent_move

# ### Revised Neutral Strategy for Maximizing Payoff Over 1000 Rounds  1.
# **Start with Cooperation**: In the first round, play **C** (cooperate).  2.
# **Mirror Opponent’s Last Move**: From the second round onward, do the
# following:    - If your opponent played **C** in the previous round, play
# **C**.    - If your opponent played **D** in the previous round, play **D**.
# 3. **Forgive Occasional Defections**: If your opponent defects (plays **D**),
# continue to mirror their move. However, after **two consecutive defections**,
# return to **C** in the next round to test if they are willing to cooperate
# again.  4. **Adapt to Persistent Defection**: If your opponent plays **D** for
# **four consecutive rounds**, switch to always playing **D** for the remainder
# of the game to avoid further exploitation.  5. **Return to Cooperation After
# Mutual Defection**: If both you and your opponent have been playing **D** for
# at least **ten consecutive rounds** and your opponent switches back to **C**,
# respond with **C** in the next round to attempt to re-establish cooperation.
# This revised strategy simplifies the forgiveness mechanism, reduces
# vulnerability to exploitation, and maintains a neutral stance by balancing
# cooperation and defection based on the opponent’s behavior.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Count the number of consecutive defections by the opponent
      consecutive_defections = 0
      for move in reversed(opponent.history):
          if move == axl.Action.D:
              consecutive_defections += 1
          else:
              break
  
      # Rule 4: If opponent has defected for 4 consecutive rounds, switch to always defecting
      if consecutive_defections >= 4:
          return axl.Action.D
  
      # Rule 5: If both have been defecting for at least 10 rounds and opponent switches to C, return to C
      if len(self.history) >= 10 and self.history[-10:].count(axl.Action.D) == 10 and opponent.history[-10:].count(axl.Action.D) == 10:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
  
      # Rule 3: If opponent has defected for 2 consecutive rounds, forgive and return to C
      if consecutive_defections == 2:
          return axl.Action.C
  
      # Rule 2: Mirror opponent's last move
      return opponent.history[-1]

# 1. **Start with Defection:** In the first round, always play D (Defect) to
# test the opponent and gain an early advantage if they play C.  2. **Continue
# Defection if Opponent Cooperates:** If the opponent continues to play C for
# five consecutive rounds, continue playing D to maximize your score (5 points
# per round). Do not switch to cooperation unless the opponent defects.  3.
# **Punish Defection Strongly:** If the opponent defects after both players had
# been cooperating, retaliate by playing D for **five consecutive rounds** to
# strongly signal that betrayal will not be tolerated.  4. **Switch to
# Cooperation Only After Mutual Defection:** If both players have been defecting
# for five consecutive rounds, switch to C (Cooperate) to test if the opponent
# is willing to cooperate again. If they defect, return to defection
# immediately.  5. **Endgame Defection:** In the final **two rounds**, always
# play D regardless of the opponent's actions to maximize potential scoring in
# the closing stages of the game.  This revised strategy maintains a more
# aggressive stance, simplifies decision-making, and strengthens punishment to
# deter exploitation.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      ENDGAME_ROUNDS = 2
      PUNISHMENT_ROUNDS = 5
      COOPERATION_TEST_ROUNDS = 5
  
      # First round: always defect
      if self.first_round():
          return axl.Action.D
  
      # Endgame defection: defect in the last two rounds
      if len(self.history) >= 1000 - ENDGAME_ROUNDS:
          return axl.Action.D
  
      # If opponent has cooperated for the last 5 rounds, continue defecting
      if opponent.history[-COOPERATION_TEST_ROUNDS:].count(axl.Action.C) == COOPERATION_TEST_ROUNDS:
          return axl.Action.D
  
      # If opponent defects after mutual cooperation, punish with 5 defections
      if len(self.history) >= 2 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          if self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.C:
              if len(self.history) < PUNISHMENT_ROUNDS or self.history[-PUNISHMENT_ROUNDS:].count(axl.Action.D) < PUNISHMENT_ROUNDS:
                  return axl.Action.D
  
      # If both players have been defecting for 5 rounds, switch to cooperation
      if self.history[-COOPERATION_TEST_ROUNDS:].count(axl.Action.D) == COOPERATION_TEST_ROUNDS and \
         opponent.history[-COOPERATION_TEST_ROUNDS:].count(axl.Action.D) == COOPERATION_TEST_ROUNDS:
          return axl.Action.C
  
      # Default to defecting
      return axl.Action.D

# 1. **Start with cooperation (C) in the first round.**      - This signals your
# intention to cooperate from the outset.  2. **Continue cooperating (C) as long
# as your opponent cooperates (C).**      - Maintain mutual cooperation to
# achieve the steady payoff of 3 for both players.  3. **If your opponent
# defects (D) once, respond by defecting (D) in the next round.**      - Punish
# a single defection immediately to discourage exploitation.  4. **After
# punishing, return to cooperation (C) if your opponent cooperates (C) in the
# following round.**      - Forgive a one-time defection and resume cooperation
# to restore mutual benefit.  5. **If your opponent defects (D) twice in a row,
# switch to consistent defection (D) for the rest of the game.**      - If the
# opponent defects consecutively, assume they are not interested in cooperation
# and protect yourself from further exploitation by defecting permanently.  This
# revised strategy maintains simplicity, encourages cooperation, includes a
# clear punishment and forgiveness mechanism, and specifies a clear threshold
# (two consecutive defections) for switching to permanent defection.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
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
          # If the opponent defected twice in a row, switch to permanent defection
          return axl.Action.D
  
      # If the opponent defected in the last round, defect this round to punish
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate if the opponent cooperated in the last round
      return axl.Action.C

# 1. **Start with Cooperation (C)**: On the first round, always choose to
# cooperate.  2. **Mirror the Opponent’s Last Move**: On subsequent rounds, copy
# whatever your opponent did in the previous round.  3. **Forgive Once After
# Defection**: If your opponent defects (D) after mutual cooperation (C-C),
# respond with defection (D) on the next round, but return to cooperation (C) in
# the following round to give the opponent a chance to cooperate again.  4.
# **Escalate Defection After Multiple Defections**: If your opponent defects two
# consecutive times (D-D), defect (D) for two rounds in response. After two
# rounds of defection, return to cooperation (C) to test if the opponent is
# willing to cooperate again.  5. **Avoid Permanent Defection Loops**: If the
# opponent continues to defect after your two-round defection response,
# alternate between cooperation (C) and defection (D) every two rounds. This
# prevents a permanent defection loop while still punishing persistent
# defection.  This revised strategy maintains neutrality, avoids deadlock, and
# balances forgiveness with appropriate punishment for repeated defection.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation on the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if the last two rounds were defections
      def last_two_defections():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if the last round was mutual cooperation
      def last_round_mutual_cooperation():
          return self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C
  
      # Helper function to check if the last round was opponent's defection after mutual cooperation
      def opponent_defected_after_mutual_cooperation():
          return len(self.history) >= 2 and self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D
  
      # If opponent defected after mutual cooperation, forgive after one defection
      if opponent_defected_after_mutual_cooperation():
          if self.history[-1] == axl.Action.D:
              return axl.Action.C  # Forgive after one defection
          else:
              return axl.Action.D  # Defect once in response
  
      # If opponent defected two consecutive times, defect for two rounds
      if last_two_defections():
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D and self.history[-2] == axl.Action.D:
              return axl.Action.C  # After two defections, return to cooperation
          else:
              return axl.Action.D  # Defect for two rounds in response
  
      # If opponent continues to defect after two-round defection response, alternate between C and D
      if len(self.history) >= 4 and self.history[-2:] == [axl.Action.D, axl.Action.D] and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          if len(self.history) % 4 in [0, 1]:
              return axl.Action.C  # Cooperate for two rounds
          else:
              return axl.Action.D  # Defect for two rounds
  
      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]

# 1. **Start with Defection:** In the first round, play D to establish an
# aggressive stance and potentially gain an early advantage if your opponent
# cooperates.  2. **Defect if Opponent Cooperates:** If your opponent plays C in
# the previous round, continue to play D in the following round to maximize your
# payoff (scoring 5 while they score 0).  3. **Retaliate Once for Defection:**
# If your opponent defects (plays D), retaliate by defecting (play D) in the
# next round. However, if they return to cooperation (play C) in the following
# round, switch back to defection only if they defect again. This prevents
# prolonged mutual defection and allows for potential exploitation of future
# cooperation.  4. **Never Initiate Cooperation:** Do not switch to cooperation
# unless the opponent consistently plays C for at least 5 consecutive rounds.
# This ensures that you only cooperate if the opponent is highly committed to
# cooperation, minimizing the risk of exploitation.  5. **Endgame Defection:**
# In the last 10 rounds, defect (play D) regardless of the opponent's behavior
# to maximize your final payoff, as there is no future interaction to maintain
# cooperation.  This revised strategy maintains a more aggressive stance,
# reduces unnecessary cooperation, and avoids prolonged mutual defection while
# still allowing for exploitation of cooperative opponents.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with defection
      if self.first_round():
          return axl.Action.D
  
      # Endgame defection: defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Defect if opponent cooperates in the previous round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Retaliate once for defection
      if opponent.history[-1] == axl.Action.D:
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
          return axl.Action.D
  
      # Never initiate cooperation unless opponent cooperates for 5 consecutive rounds
      if opponent.history[-5:] == [axl.Action.C] * 5:
          return axl.Action.C
  
      # Default to defection
      return axl.Action.D

# 1. **Start with cooperation**: In the first round, play C (cooperate).  2.
# **Mirror your opponent’s previous move**: From the second round onward, always
# play what your opponent played in the previous round.  3. **Forgive a single
# defection**: If your opponent defects (plays D) once, return to cooperation
# (play C) in the next round, assuming they play C again.  4. **Punish repeated
# defection**: If your opponent defects twice in a row, switch to defection
# (play D) and continue defecting until they cooperate for two consecutive
# rounds.  This revised strategy simplifies the forgiveness mechanism, reduces
# the risk of over-punishment, and eliminates the need to track defections over
# multiple rounds, making it easier to implement while maintaining a cooperative
# approach.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Check the last two moves of the opponent
      opponent_last_move = opponent.history[-1]
      opponent_second_last_move = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # If the opponent defected twice in a row, punish by defecting
      if opponent_last_move == axl.Action.D and opponent_second_last_move == axl.Action.D:
          return axl.Action.D
  
      # If the opponent defected once, forgive if they cooperated in the last round
      if opponent_last_move == axl.Action.C and opponent_second_last_move == axl.Action.D:
          return axl.Action.C
  
      # Otherwise, mirror the opponent's last move
      return opponent_last_move

# **Revised Strategy:**  1. **Start with cooperation**: In the first round, play
# C (cooperate).  2. **Mirror the opponent's previous move**: From the second
# round onwards, play exactly what your opponent played in the previous round.
# If they played C, you play C. If they played D, you play D.  3. **Adaptive
# forgiveness**: If both you and your opponent have defected (both playing D)
# for 3 consecutive rounds, switch to C (cooperate) in the next round,
# regardless of what your opponent plays. This reduces the risk of prolonged
# mutual defection while maintaining flexibility.  4. **Return to mirroring**:
# After cooperating as a form of forgiveness, return to mirroring the opponent’s
# moves in subsequent rounds.  ---  This revision simplifies the forgiveness
# mechanism by reducing the number of consecutive defections required to trigger
# cooperation, making it more responsive. It maintains neutrality, logical
# consistency, and avoids prolonged defection cycles while still being simple
# and predictable enough to encourage cooperation.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Mirror the opponent's previous move
      if len(self.history) >= 3:
          # Check if both players have defected for the last 3 rounds
          if (self.history[-3:] == [axl.Action.D] * 3 and
              opponent.history[-3:] == [axl.Action.D] * 3):
              # Adaptive forgiveness: cooperate after 3 consecutive mutual defections
              return axl.Action.C
  
      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]

# 1. **First move**: Play **D** (defect) in the first round.  2. **Subsequent
# rounds**:    - If your opponent plays **C** (cooperate) in response to your
# **D**, continue playing **D** in the next round to exploit their cooperation.
# - If your opponent plays **D** in response to your **D**, continue playing
# **D** (defect) in the next round. Do not switch to **C** after mutual
# defection.  3. **Switching to cooperation**:    - If your opponent
# consistently plays **C** for 3 consecutive rounds after you have defected,
# switch to **C** (cooperate) to test for potential long-term cooperation.
# 4. **After playing C**:    - If your opponent plays **C** after you switch to
# **C**, continue playing **C** until they defect.    - If your opponent plays
# **D** after you switch to **C**, immediately return to playing **D** and
# continue playing **D** for the rest of the game.  This revised strategy
# maintains an aggressive stance by continuing defection after mutual defection
# and only switches to cooperation after observing consistent cooperative
# behavior from the opponent. It also ensures that defection is punished with
# permanent defection, aligning with the aggressive approach.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First move: Play D (defect) in the first round
      if self.first_round():
          return axl.Action.D
  
      # Check the last move of the opponent
      last_opponent_move = opponent.history[-1]
  
      # If the opponent has cooperated for the last 3 rounds, switch to cooperation
      if len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:]):
          return axl.Action.C
  
      # If we are currently cooperating and the opponent defects, return to permanent defection
      if self.history[-1] == axl.Action.C and last_opponent_move == axl.Action.D:
          return axl.Action.D
  
      # If the opponent cooperated in response to our defection, continue defecting
      if self.history[-1] == axl.Action.D and last_opponent_move == axl.Action.C:
          return axl.Action.D
  
      # If the opponent defected in response to our defection, continue defecting
      if self.history[-1] == axl.Action.D and last_opponent_move == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, continue cooperating if both are cooperating
      return axl.Action.C

# **Revised Strategy:**  1. **Start by Cooperating (C):** In the first round,
# always play C to signal a willingness to cooperate.  2. **Tit-for-Tat:**    -
# If your opponent played C in the previous round, continue to play C.    - If
# your opponent played D in the previous round, respond by playing D in the next
# round.  3. **Forgive a single defection:**    - If your opponent defects
# (plays D) once but then returns to playing C in the next round, forgive the
# defection and return to playing C.    - If your opponent defects more than
# once in a row, continue playing D until they return to playing C for two
# consecutive rounds.  4. **Endgame caution:**    - In the final 10 rounds,
# continue using the Tit-for-Tat approach (responding to the opponent’s last
# move) rather than always playing C, to avoid being exploited in the closing
# rounds.  ---  This revision simplifies the forgiveness rule, ensures logical
# consistency, and addresses the vulnerability in the endgame by maintaining a
# cautious approach throughout.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the number of rounds left
      rounds_left = self.match_attributes["length"] - len(self.history)
  
      # Endgame caution: In the last 10 rounds, use Tit-for-Tat
      if rounds_left <= 10:
          return opponent.history[-1]
  
      # Tit-for-Tat: Mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Forgive a single defection if followed by cooperation
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          # If opponent defects more than once in a row, continue defecting until they cooperate twice
          if len(opponent.history) > 2 and opponent.history[-2] == axl.Action.D and opponent.history[-3] == axl.Action.D:
              if opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
                  return axl.Action.C
              else:
                  return axl.Action.D
          return axl.Action.D

# ### Revised Neutral Iterated Game Strategy  1. **Begin with Cooperation (C):**
# Start the game by playing C in the first round to signal a willingness to
# cooperate.  2. **Tit-for-Tat with Limited Forgiveness:**    - **If** your
# opponent played C in the previous round, **play C** in the current round.    -
# **If** your opponent played D in the previous round, **play D** in the current
# round (retaliate).  3. **Forgive Once After Retaliation:**    - After
# retaliating with D once, **return to C** in the next round **only if** your
# opponent plays C in response to your retaliation.    - **If** your opponent
# plays D again after your retaliation, **continue playing D** until they play
# C.  4. **Sustain Cooperation:**    - If your opponent consistently plays C
# after your forgiveness, **continue playing C** to maintain mutual cooperation.
# 5. **Detect and Punish Persistent Defection:**    - **If** your opponent plays
# D three times consecutively, **switch to permanent D** for the remainder of
# the game to avoid further exploitation.  This revised strategy simplifies the
# forgiveness process, reduces vulnerability to exploitation, and maintains
# neutrality by balancing cooperation and defection based on the opponent's
# behavior.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          self.retaliated = False  # Track if we've retaliated
          self.defection_streak = 0  # Track consecutive defections by opponent
          return axl.Action.C
  
      # Check opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If opponent cooperated last round, cooperate
      if opponent_last_move == axl.Action.C:
          self.defection_streak = 0  # Reset defection streak
          if self.retaliated:
              self.retaliated = False  # Forgive after retaliation if opponent cooperates
          return axl.Action.C
  
      # If opponent defected last round
      if opponent_last_move == axl.Action.D:
          self.defection_streak += 1  # Increment defection streak
  
          # If opponent defected three times consecutively, switch to permanent defection
          if self.defection_streak >= 3:
              return axl.Action.D
  
          # If we haven't retaliated yet, retaliate with D
          if not self.retaliated:
              self.retaliated = True
              return axl.Action.D
  
          # If we already retaliated, continue defecting until opponent cooperates
          return axl.Action.D


Aggressive_ranks = [
'Aggressive_23',
'Aggressive_24',
'Aggressive_18',
'Aggressive_1',
'Aggressive_5',
'Aggressive_11',
'Aggressive_9',
'Aggressive_8',
'Aggressive_22',
'Aggressive_17',
'Aggressive_12',
'Aggressive_6',
'Aggressive_7',
'Aggressive_10',
'Aggressive_3',
'Aggressive_4',
'Aggressive_15',
'Aggressive_16',
'Aggressive_20',
'Aggressive_2',
'Aggressive_14',
'Aggressive_25',
'Aggressive_21',
'Aggressive_13',
'Aggressive_19',
]

Cooperative_ranks = [
'Cooperative_10',
'Cooperative_16',
'Cooperative_21',
'Cooperative_11',
'Cooperative_7',
'Cooperative_8',
'Cooperative_5',
'Cooperative_6',
'Cooperative_4',
'Cooperative_24',
'Cooperative_23',
'Cooperative_25',
'Cooperative_12',
'Cooperative_13',
'Cooperative_14',
'Cooperative_22',
'Cooperative_3',
'Cooperative_20',
'Cooperative_19',
'Cooperative_15',
'Cooperative_17',
'Cooperative_9',
'Cooperative_1',
'Cooperative_2',
'Cooperative_18',
]

Neutral_ranks = [
'Neutral_17',
'Neutral_16',
'Neutral_3',
'Neutral_4',
'Neutral_25',
'Neutral_19',
'Neutral_12',
'Neutral_7',
'Neutral_2',
'Neutral_14',
'Neutral_13',
'Neutral_24',
'Neutral_23',
'Neutral_9',
'Neutral_8',
'Neutral_22',
'Neutral_10',
'Neutral_1',
'Neutral_5',
'Neutral_21',
'Neutral_15',
'Neutral_6',
'Neutral_20',
'Neutral_11',
'Neutral_18',
]