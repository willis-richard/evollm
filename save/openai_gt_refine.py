import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# ### Revised Aggressive Strategy  1. **Start by playing Defect (D).**  2.
# **Switch to Cooperate (C) if the opponent plays Cooperate (C) for 2
# consecutive rounds.**    - This allows for earlier mutual cooperation,
# maximizing potential payoffs sooner.  3. **If the opponent defects (D) after
# you switch to Cooperate (C), switch back to Defect (D) for 3 rounds as
# punishment.**    - After 3 rounds of Defect (D), return to Cooperate (C) to
# test if the opponent is willing to cooperate again.  4. **If the opponent
# defects (D) again after you return to Cooperate (C), switch to permanent
# Defect (D) for the rest of the game.**    - This prevents repeated
# exploitation by an uncooperative opponent.  5. **If the opponent alternates
# between Cooperate (C) and Defect (D), always play Defect (D).**    - This
# avoids being exploited by inconsistent behavior.  6. **In the final 10 rounds
# of the game, always play Defect (D).**    - This accounts for the endgame,
# where defection becomes more advantageous as the game approaches its
# conclusion.  This revised strategy balances aggression with opportunities for
# cooperation, while also incorporating forgiveness and an endgame plan.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperate_switch = False  # Whether we have switched to cooperation
          self.punishment_rounds = 0     # Counter for punishment rounds
          self.permanent_defect = False  # Whether we are in permanent defection mode
          return axl.Action.D            # Start by playing Defect (D)
      
      # If we are in permanent defection mode, always defect
      if self.permanent_defect:
          return axl.Action.D
      
      # If we are in punishment mode, defect for 3 rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
      
      # Check if we are in the final 10 rounds of the game
      if len(self.history) >= 990:
          return axl.Action.D  # Always defect in the final 10 rounds
      
      # If opponent cooperates for 2 consecutive rounds, switch to cooperation
      if not self.cooperate_switch and len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          self.cooperate_switch = True
          return axl.Action.C
      
      # If we have switched to cooperation and opponent defects, punish with 3 rounds of defection
      if self.cooperate_switch and opponent.history[-1] == axl.Action.D:
          self.punishment_rounds = 3
          self.cooperate_switch = False  # Reset cooperation switch
          return axl.Action.D
      
      # If opponent defects again after returning to cooperation, switch to permanent defection
      if not self.cooperate_switch and len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.permanent_defect = True
          return axl.Action.D
      
      # If opponent alternates between cooperation and defection, always defect
      if len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]:
          return axl.Action.D
      
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# 1. **Start with cooperation (C)**: In the first round, play C to signal a
# willingness to cooperate and establish a foundation for mutual benefit.  2.
# **Continue playing C as long as your opponent plays C**: If your opponent
# continues to cooperate by playing C, keep playing C to maintain the mutual
# payoff of 3.  3. **Defect (play D) if your opponent defects (plays D)**: If
# your opponent defects, immediately switch to playing D in the next round to
# discourage further defection.  4. **Punish consistent defection**: If your
# opponent defects for two consecutive rounds, continue defecting until they
# return to cooperation. This prevents exploitation by a consistently
# uncooperative opponent.  5. **Forgive occasional defection**: If your opponent
# defects only once and then returns to cooperation, forgive them by returning
# to cooperation (C) in the next round. This allows for recovery from occasional
# mistakes or tests of trust.  6. **Monitor patterns of defection**: If your
# opponent alternates between cooperation and defection in a predictable
# pattern, adjust by defecting in response to their defection and cooperating
# only when they cooperate. This prevents exploitation by opponents who try to
# game the system.  7. **Defect in the final round only**: To avoid being
# exploited at the end of the game, defect (play D) in the final round. However,
# continue cooperating in the penultimate rounds if your opponent is still
# cooperating, as this maximizes the potential for mutual benefit before the
# final round.  This revised strategy balances cooperation with a more robust
# response to consistent defection, while still allowing for occasional
# forgiveness and adaptation to the opponent's behavior.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Defect in the final round
      if len(self.history) == 999:
          return axl.Action.D
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected in the last two rounds, continue defecting
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          # Otherwise, defect once in response to a single defection
          return axl.Action.D
  
      # If opponent cooperated in the last round, cooperate
      return axl.Action.C

# **Revised Strategy:**  1. **Initial Move**: Start by playing C (cooperate) in
# the first round.  2. **Tit-for-Tat with Gradual Forgiveness**: For each
# subsequent round, follow these rules:     - If your opponent played C in the
# previous round, play C.    - If your opponent played D in the previous round,
# play D **once** in retaliation.    - After retaliating with D, return to C in
# the next round to test if the opponent is willing to cooperate again. If they
# continue to defect, repeat the process (defect once, then return to C).  3.
# **Endgame (Final 10 Rounds)**: In the last 10 rounds, always defect (play D).
# ---  **Key Adjustments**: - The forgiveness mechanism is now gradual, with a
# single defection in response to the opponent's defection, followed by a return
# to cooperation to test their willingness to cooperate. - The endgame defection
# starts later (in the final 10 rounds) to maximize cooperative gains before the
# game ends.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Endgame: Always defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Tit-for-Tat with Gradual Forgiveness
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected last round, retaliate with D once
          if len(self.history) < 2 or self.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              # After retaliating, return to cooperation
              return axl.Action.C
      else:
          # If opponent cooperated last round, cooperate
          return axl.Action.C

# ### Revised Aggressive Strategy for 1000-Round Iterated Game  1. **Start with
# Defect (D)**: In the first round, always play D. This avoids the risk of being
# exploited early and sets an aggressive tone.  2. **Defect (D) as Long as the
# Opponent Defects (D)**: If the opponent plays D in any round, continue playing
# D. Mutual defection yields 1 point each, which is better than risking 0 points
# by cooperating while the opponent defects.  3. **Switch to Cooperate (C) if
# the Opponent Cooperates Twice in a Row (C, C)**: If the opponent plays C for
# two consecutive rounds, switch to C in the next round to test for the
# possibility of mutual cooperation. This avoids missing out on the higher
# payoff of 3 points each from mutual cooperation.  4. **Return to Defect (D)
# Immediately if the Opponent Defects After You Cooperate**: If you switch to C
# and the opponent defects (D) in any subsequent round, immediately return to D
# in the next round. This punishes the opponent for exploiting your cooperation
# and prevents further losses.  5. **Maintain Mutual Cooperation (C) if the
# Opponent Continues to Cooperate**: If both you and the opponent continue to
# play C for several rounds, maintain cooperation to maximize the 3-point payoff
# per round. This is the optimal outcome if the opponent is willing to
# cooperate.  6. **Defect (D) in the Last 3 Rounds**: In the final three rounds,
# always defect. Since future retaliation is irrelevant, defecting ensures you
# avoid being exploited and potentially gain 5 points if the opponent continues
# to cooperate.  7. **Adapt to Opponent’s Strategy**: If the opponent
# consistently alternates between C and D or shows a clear pattern, adjust your
# strategy accordingly. For example, if the opponent plays tit-for-tat, mirror
# their moves to maintain cooperation and avoid unnecessary defection cycles.
# ---  This revised strategy addresses the critiques by focusing on maximizing
# long-term cooperation when possible, punishing defection consistently, and
# adapting to the opponent’s behavior. It also avoids unnecessary risks,
# especially in the endgame.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Defect in the first round
      if self.first_round():
          return axl.Action.D
  
      # Defect in the last 3 rounds
      if len(self.history) >= 997:
          return axl.Action.D
  
      # If the opponent defected in the last round, continue defecting
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent cooperated in the last two rounds, switch to cooperate
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected after we cooperated, return to defect
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, maintain cooperation if both are cooperating
      return axl.Action.C

# **Revised Strategy:**  1. **Start by cooperating (C) in the first round.**  2.
# **In subsequent rounds, follow a "Tit-for-Tat" approach with a slight
# modification:**    - If your opponent cooperated (C) in the previous round,
# you also cooperate (C) in the current round.    - If your opponent defected
# (D) in the previous round, you defect (D) in the current round.  3. **Forgive
# occasional defections cautiously:**    - If your opponent defects once but
# then returns to cooperation (C) in the next round, you forgive and return to
# cooperation (C) as well.    - However, if the opponent alternates between
# defection (D) and cooperation (C) repeatedly, you defect (D) to prevent
# exploitation.  4. **Punish repeated defections proportionally:**    - If your
# opponent defects for **two consecutive rounds**, defect (D) for two rounds in
# response. After that, return to cooperation (C) if the opponent cooperates (C)
# again.  5. **Introduce a mechanism to escape mutual defection:**    - If both
# you and your opponent have defected (D) for **three consecutive rounds**,
# attempt to break the cycle by cooperating (C) in the next round. If the
# opponent also cooperates, continue cooperating. If they defect again, return
# to defection.  6. **Endgame consideration:**    - In the final 10 rounds,
# gradually shift towards defection (D) if the opponent shows signs of
# defection. However, if mutual cooperation has been consistent throughout the
# game, continue cooperating to maximize the final payoffs.  7. **Adapt to
# opponent behavior:**    - If the opponent consistently defects without
# returning to cooperation, switch to permanent defection (D) after 5 rounds of
# repeated defection to avoid being exploited.  This revised strategy addresses
# the potential pitfalls of mutual defection, exploitation, and the endgame
# problem while maintaining a cooperative approach when possible.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.alternating_cd = False
          return axl.Action.C  # Start by cooperating
  
      # Helper function to check if opponent is alternating between C and D
      def is_alternating_cd():
          if len(opponent.history) < 2:
              return False
          return (opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.D) or \
                 (opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C)
  
      # Track consecutive defections by the opponent
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Tit-for-Tat with forgiveness for a single defection followed by cooperation
      if opponent.history[-1] == axl.Action.C:
          if self.alternating_cd:
              # If opponent was alternating, defect to prevent exploitation
              self.alternating_cd = False
              return axl.Action.D
          return axl.Action.C
      elif len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D:
          if opponent.history[-2] == axl.Action.C:
              # Forgive a single defection followed by cooperation
              return axl.Action.C
  
      # Detect alternating C and D pattern
      if is_alternating_cd():
          self.alternating_cd = True
          return axl.Action.D
  
      # Punish two consecutive defections with two defections
      if self.consecutive_defections >= 2:
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D and self.history[-2] == axl.Action.D:
              return axl.Action.C  # After two defections, return to cooperation if opponent cooperates
          return axl.Action.D  # Defect for two rounds in response to two consecutive defections
  
      # Escape mutual defection after three consecutive rounds of mutual defection
      if len(self.history) >= 3 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D and \
         self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D and \
         self.history[-3] == axl.Action.D and opponent.history[-3] == axl.Action.D:
          return axl.Action.C  # Attempt to break the cycle by cooperating
  
      # Endgame consideration: shift towards defection in the last 10 rounds if opponent defects
      if len(self.history) >= 990:
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          return axl.Action.C
  
      # Switch to permanent defection after 5 rounds of repeated defection
      if self.consecutive_defections >= 5:
          return axl.Action.D
  
      # Default to Tit-for-Tat
      return opponent.history[-1]

# 1. **Start by cooperating (C)** in the first round.  2. **In each subsequent
# round, follow these rules:**     - **If both you and your opponent played C in
# the previous round, continue playing C** (cooperate) to maintain mutual
# benefit.        - **If your opponent defected (D) in the previous round,
# defect (D) in the next round** to punish them, but **only for one round**.
# - **After punishing with D, return to C** (cooperate) in the following round
# to test if your opponent is willing to cooperate again.        - **If your
# opponent continues to defect after your return to C, switch to playing D
# consistently** until they cooperate again. This ensures you avoid being
# exploited by repeated defection.        - **If your opponent switches back to
# C after a defection, immediately return to C** (cooperate) to restore mutual
# cooperation.  3. **Avoid long defection cycles**: If both you and your
# opponent are stuck in mutual defection (both playing D for 3 consecutive
# rounds), break the cycle by playing C in the next round to test for
# cooperation.  4. **Do not use periodic tests**: Instead of testing every 50
# rounds, rely on the natural flow of the game to determine when to return to
# cooperation after defection. This prevents predictable exploitation.  This
# revised strategy balances punishment and forgiveness, avoids long defection
# loops, and adapts to different opponent behaviors while maximizing the
# potential for cooperation.

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
  
      # Helper function to check if both players defected in the last 3 rounds
      def mutual_defection_streak():
          return (len(self.history) >= 3 and
                  self.history[-3:] == [axl.Action.D] * 3 and
                  opponent.history[-3:] == [axl.Action.D] * 3)
  
      # Get the last round's actions
      last_self_action = self.history[-1]
      last_opponent_action = opponent.history[-1]
  
      # If both cooperated in the last round, continue cooperating
      if last_self_action == axl.Action.C and last_opponent_action == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the last round, punish with a defection
      if last_opponent_action == axl.Action.D:
          # If we just punished with a defection, return to cooperation
          if last_self_action == axl.Action.D:
              return axl.Action.C
          # Otherwise, punish with a defection
          return axl.Action.D
  
      # If both players have been defecting for 3 rounds, break the cycle by cooperating
      if mutual_defection_streak():
          return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# 1. **Start by cooperating (C)** in the first round to establish a baseline of
# trust and encourage mutual cooperation.  2. **If the opponent cooperates (C)
# in response**, continue cooperating (C) to maximize mutual payoffs.  3. **If
# the opponent defects (D) at any point**, immediately defect (D) in the next
# round to signal that defection will not be tolerated.  4. **After one round of
# defection**, return to cooperation (C) to test if the opponent is willing to
# re-establish cooperation. If they cooperate (C) in response, continue
# cooperating.  5. **If the opponent defects (D) again after your return to
# cooperation**, switch to a strategy of alternating between defection (D) and
# cooperation (C) for the next 10 rounds. This signals that you are willing to
# cooperate but will not allow consistent exploitation.  6. **If the opponent
# continues to defect (D) during this alternating phase**, switch to permanent
# defection (D) for the remainder of the game, as they have demonstrated a
# purely exploitative strategy.  7. **If the opponent returns to cooperation (C)
# during the alternating phase**, resume full cooperation (C) and continue
# cooperating as long as they do.  This revised strategy encourages cooperation
# while punishing defection, but it also provides opportunities for the opponent
# to return to cooperation. It avoids unnecessary provocations and ensures that
# defection is only used when necessary to prevent exploitation.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defected_once = False  # Track if we've defected once after opponent's defection
          self.alternating_phase = False  # Track if we're in the alternating phase
          self.alternating_count = 0  # Counter for alternating phase rounds
          return axl.Action.C  # Start by cooperating
  
      # If in alternating phase, alternate between C and D for 10 rounds
      if self.alternating_phase:
          if self.alternating_count < 10:
              self.alternating_count += 1
              # Alternate between C and D
              if self.alternating_count % 2 == 0:
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              # After 10 rounds, check if opponent cooperated during the alternating phase
              if opponent.history[-10:].count(axl.Action.C) > 0:
                  # If opponent cooperated, return to full cooperation
                  self.alternating_phase = False
                  self.alternating_count = 0
                  return axl.Action.C
              else:
                  # If opponent continued defecting, switch to permanent defection
                  return axl.Action.D
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          if not self.defected_once:
              # Defect once in response to opponent's defection
              self.defected_once = True
              return axl.Action.D
          else:
              # If opponent defects again after we returned to cooperation, enter alternating phase
              self.alternating_phase = True
              self.alternating_count = 1  # Start alternating with defection
              return axl.Action.D
  
      # If opponent cooperated in the last round, reset defection flag and continue cooperating
      self.defected_once = False
      return axl.Action.C

# ### Revised Strategy: **Adaptive Tit-for-Tat with Conditional Forgiveness**
# 1. **Start with Cooperation**: In the first round, always play C (cooperate)
# to signal a willingness to establish mutual cooperation.  2. **Mirror
# Opponent’s Last Move**: From the second round onward, play exactly what your
# opponent played in the previous round. If they played C, you play C. If they
# played D, you play D. This maintains a balance between cooperation and
# retaliation.  3. **Conditional Forgiveness**: If your opponent defects (plays
# D) once, forgive them by playing C in the next round, but only if they
# cooperated in at least 3 of the last 5 rounds. This encourages cooperation
# while preventing exploitation by frequent defectors.  4. **Punish Consistent
# Defection**: If your opponent defects in two consecutive rounds, switch to
# permanent defection (D) until they cooperate again. This prevents being
# exploited by an opponent who consistently defects.  5. **Endgame
# Consideration**: In the last 10 rounds, switch to defection (D) if your
# opponent has defected more than 30% of the time up to that point. This
# prevents late-game exploitation when the opponent may try to maximize their
# own payoff by defecting.  ### Summary: - Start by cooperating. - Mirror your
# opponent’s previous move. - Forgive a single defection if the opponent has
# shown a pattern of cooperation. - Punish consistent defection by defecting
# until cooperation is restored. - Defect in the final rounds if the opponent
# has a history of frequent defection.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if opponent cooperated in at least 3 of the last 5 rounds
      def opponent_cooperated_in_last_5():
          return opponent.history[-5:].count(axl.Action.C) >= 3
  
      # Helper function to check if opponent defected more than 30% of the time
      def opponent_defection_rate():
          if len(opponent.history) == 0:
              return 0
          return opponent.history.defections / len(opponent.history)
  
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Endgame consideration: Defect in the last 10 rounds if opponent defected more than 30% of the time
      if len(self.history) >= 990 and opponent_defection_rate() > 0.3:
          return axl.Action.D
  
      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # Conditional forgiveness: Forgive if opponent cooperated in at least 3 of the last 5 rounds
          if len(opponent.history) >= 5 and opponent_cooperated_in_last_5():
              return axl.Action.C
          # Punish consistent defection: Defect if opponent defected in the last two rounds
          elif len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
  
      # Default to mirroring opponent's last move
      return opponent.history[-1]

# Here is the revised strategy, addressing the critiques:  1. **Start by
# cooperating (play C) in the first round.**  2. **If both players cooperated
# (C, C) in the previous round, continue cooperating (play C).**  3. **If your
# opponent defected (played D) in the previous round and you cooperated (C, D),
# retaliate by defecting (play D) in the next round.**  4. **If both players
# defected (D, D) in the previous round, continue defecting (play D) until the
# opponent cooperates again. Once the opponent cooperates (C), return to
# cooperation (play C) in the following round.**  5. **If you defected and your
# opponent cooperated (D, C) in the previous round, switch to cooperation (play
# C) in the next round to avoid prolonged exploitation and encourage mutual
# cooperation.**  6. **If your opponent defects twice in a row (D, D), continue
# defecting (play D) until they cooperate again. Once they cooperate (C), return
# to cooperation (play C).**  7. **If your opponent cooperates after a defection
# (C, D or D, C), forgive them and return to cooperation (play C) in the next
# round.**  This revised strategy incorporates sustained punishment for repeated
# defections, forgiveness for isolated defections, and a mechanism to avoid
# prolonged exploitation, while still encouraging cooperation when possible.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the last round's moves
      last_self_move = self.history[-1]
      last_opponent_move = opponent.history[-1]
  
      # If both players cooperated in the previous round, continue cooperating
      if last_self_move == axl.Action.C and last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected and you cooperated, retaliate by defecting
      if last_self_move == axl.Action.C and last_opponent_move == axl.Action.D:
          return axl.Action.D
  
      # If both players defected, continue defecting until opponent cooperates
      if last_self_move == axl.Action.D and last_opponent_move == axl.Action.D:
          return axl.Action.D
  
      # If you defected and opponent cooperated, switch to cooperation
      if last_self_move == axl.Action.D and last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # If opponent defects twice in a row, continue defecting until they cooperate
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # If opponent cooperates after a defection, forgive and return to cooperation
      return axl.Action.C

# 1. **Start by Defecting (D)**: In the first round, play D to test the
# opponent’s response and establish an aggressive stance.  2. **Defect (D) if
# the opponent plays Cooperate (C)**: If the opponent plays C in response,
# continue playing D to exploit their cooperation and maximize short-term gains
# (you get 5, they get 0).  3. **Switch to Cooperation (C) if the opponent plays
# C after your initial defection**: If the opponent responds to your defection
# by playing C in the next round, switch to C to explore the possibility of
# sustained cooperation. This avoids unnecessary mutual defection and opens the
# door to higher long-term payoffs.  4. **Tit-for-Tat with forgiveness**: After
# switching to cooperation, adopt a tit-for-tat strategy: mirror the opponent’s
# previous move (play C if they played C, play D if they played D). However, if
# the opponent defects once after a long period of cooperation, forgive them by
# playing C once more to test if they return to cooperation. If they defect
# again, return to tit-for-tat.  5. **Punish sustained defection**: If the
# opponent defects for two consecutive rounds after you have switched to
# cooperation, return to defection (D) and continue defecting until they show
# signs of cooperation again.  6. **Endgame strategy**: In the last 10 rounds,
# continue with tit-for-tat but be more cautious about forgiving defection. In
# the final 3 rounds, defect unconditionally to maximize your score, as
# cooperation is unlikely to be sustained at the very end.  This revised
# strategy balances aggression with the potential for cooperation, punishes
# sustained defection, and adapts to different opponent behaviors while
# maximizing long-term payoffs.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Define constants for actions
      C, D = axl.Action.C, axl.Action.D
      
      # Check if it's the first round
      if self.first_round():
          return D  # Start by defecting
      
      # Endgame strategy: In the last 10 rounds, be more cautious about forgiving
      if len(self.history) >= 990:
          if len(self.history) >= 997:
              return D  # Defect unconditionally in the last 3 rounds
          return opponent.history[-1]  # Continue tit-for-tat in rounds 990-996
      
      # If opponent cooperated after our initial defection, switch to cooperation
      if len(self.history) == 2 and self.history[0] == D and opponent.history[1] == C:
          return C
      
      # Tit-for-tat with forgiveness
      if len(self.history) > 2:
          # If opponent defected once after a long period of cooperation, forgive once
          if self.history[-1] == C and opponent.history[-2] == C and opponent.history[-1] == D:
              return C  # Forgive once
          
          # If opponent defects twice in a row, punish by defecting
          if opponent.history[-1] == D and opponent.history[-2] == D:
              return D
      
      # Default to tit-for-tat
      return opponent.history[-1]

# 1. **Start with Cooperation (C)**: Always play C in the first round to signal
# a willingness to cooperate.  2. **Mirror your opponent's previous move**: From
# round 2 onward, adopt a "Tit-for-Tat" strategy:    - If your opponent played C
# in the previous round, play C.    - If your opponent played D in the previous
# round, play D.  3. **Forgive occasional defections**: If your opponent defects
# (plays D) once, continue playing C in the next round to allow for the
# possibility of a mistake or noise. If they defect again immediately after,
# switch to playing D.  4. **Punish consistent defection**: If your opponent
# defects (plays D) for **two consecutive rounds**, switch to playing D until
# they return to cooperation.  5. **Revert to cooperation after two cooperative
# moves**: If your opponent resumes playing C for **two consecutive rounds**
# after defecting, return to playing C on the next round to re-establish
# cooperation.  6. **Endgame strategy**: In the final 10 rounds, switch to
# playing D if your opponent defects even once, as the incentive to cooperate
# diminishes near the end of the game.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants for cooperation and defection
      C, D = axl.Action.C, axl.Action.D
  
      # Check if it's the first round
      if self.first_round():
          return C  # Start with cooperation
  
      # Endgame strategy: In the last 10 rounds, defect if opponent defects even once
      if len(self.history) >= 990:
          if D in opponent.history[-10:]:
              return D
          else:
              return C
  
      # Mirror opponent's previous move (Tit-for-Tat)
      if len(self.history) == 1:
          return opponent.history[-1]  # Mirror the opponent's first move
  
      # Forgive occasional defections: If opponent defected once, continue cooperating
      if opponent.history[-1] == D and opponent.history[-2] == C:
          return C
  
      # Punish consistent defection: If opponent defected twice in a row, defect
      if opponent.history[-1] == D and opponent.history[-2] == D:
          return D
  
      # Revert to cooperation after two consecutive cooperations
      if opponent.history[-1] == C and opponent.history[-2] == C:
          return C
  
      # Default to mirroring the opponent's last move
      return opponent.history[-1]

# 1. **Start by cooperating (play C)** in the first round.  2. **Cooperate (play
# C) if your opponent cooperated (played C) in the previous round.**  3.
# **Defect (play D) if your opponent defected (played D) in the previous round,
# but only after two consecutive defections**. This prevents immediate
# retaliation and allows for potential mistakes or noise in the opponent's play.
# 4. **Forgive after one round of mutual defection**: If both you and your
# opponent defected in the previous round, return to cooperating (play C) in the
# next round. This encourages a return to cooperation after a brief conflict.
# 5. **Monitor for exploitation**: If your opponent alternates between
# cooperation and defection (C-D-C-D pattern), defect (play D) until they
# cooperate for two consecutive rounds. This prevents exploitation of the
# forgiveness mechanism.  6. **In the final 10 rounds, defect (play D) if your
# opponent defected in any of the last 5 rounds**. This accounts for potential
# endgame defection strategies and ensures you are not taken advantage of as the
# game concludes.  This revised strategy balances cooperation, retaliation, and
# forgiveness while addressing potential exploitation and endgame
# considerations.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to check if opponent alternates between C and D
      def is_alternating(history):
          if len(history) < 4:
              return False
          return history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Final 10 rounds: Defect if opponent defected in any of the last 5 rounds
      if len(self.history) >= 990:
          if opponent.history[-5:].count(axl.Action.D) > 0:
              return axl.Action.D
  
      # Forgive after one round of mutual defection
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Defect if opponent defected in the last two consecutive rounds
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Cooperate if opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Monitor for exploitation (C-D-C-D pattern)
      if is_alternating(opponent.history):
          # Defect until opponent cooperates for two consecutive rounds
          if opponent.history[-2:] != [axl.Action.C, axl.Action.C]:
              return axl.Action.D
  
      # Default to cooperation
      return axl.Action.C

# **Revised Aggressive Strategy for Iterated Game (1000 rounds):**  1. **Start
# with Defection (D):** On the first move, play D to establish an aggressive
# stance and test the opponent's response.  2. **Defect (D) if the Opponent
# Plays C:** If the opponent plays C, continue defecting (D) to maximize your
# payoff (5 for you, 0 for them). This exploits cooperative opponents early on.
# 3. **Punish Defection with Defection (D):** If the opponent defects (D),
# respond with defection (D) to avoid being exploited. Continue defecting as
# long as the opponent defects to ensure you don’t fall behind in points.  4.
# **Probe for Cooperation After Mutual Defection:** After 3 consecutive rounds
# of mutual defection (both playing D), switch to cooperation (C) for one round
# to test if the opponent is willing to cooperate. If the opponent responds with
# C, continue cooperating (C) to maximize mutual payoffs (3 each round).  5.
# **Return to Defection (D) if the Opponent Defects After Cooperation:** If the
# opponent defects (D) after you’ve established cooperation, immediately return
# to defection (D) and repeat the cycle of punishing defection and probing for
# cooperation.  6. **Alternate Between Defection (D) and Cooperation (C) if the
# Opponent Alternates:** If the opponent alternates between defection and
# cooperation, mirror their behavior by alternating as well. This prevents them
# from gaining an advantage while maintaining the possibility of cooperation.
# 7. **In the Final 5 Rounds, Always Defect (D):** In the last 5 rounds, always
# defect (D) to maximize your payoff, as future retaliation becomes irrelevant.
# This revised strategy maintains an aggressive approach but introduces
# mechanisms to test for cooperation, punish defection effectively, and avoid
# prolonged mutual defection. It also reduces predictability by shortening the
# final defection phase to 5 rounds.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants for actions
      C, D = axl.Action.C, axl.Action.D
  
      # If it's the first round, start with defection
      if self.first_round():
          return D
  
      # In the last 5 rounds, always defect
      if len(self.history) >= 995:
          return D
  
      # If the opponent alternates between C and D, mirror their behavior
      if len(self.history) >= 2 and self.history[-1] != self.history[-2] and opponent.history[-1] != opponent.history[-2]:
          return opponent.history[-1]
  
      # If the opponent cooperates, continue defecting to exploit
      if opponent.history[-1] == C:
          return D
  
      # If the opponent defects, punish with defection
      if opponent.history[-1] == D:
          # Check if there have been 3 consecutive mutual defections
          if len(self.history) >= 3 and all(x == D for x in self.history[-3:]) and all(x == D for x in opponent.history[-3:]):
              return C  # Probe for cooperation after 3 mutual defections
          return D  # Continue defecting otherwise
  
      return D  # Default to defection if no other condition is met

# ### Revised Strategy: Conditional Cooperation with Escalating Punishment  1.
# **Start by cooperating**: In the first round, always play C (cooperate).  2.
# **Continue cooperating as long as your opponent cooperates**: If, in the
# previous round, both you and your opponent played C, play C again.  3.
# **Punish defections with escalation**: If your opponent plays D (defects) in
# any round, respond by playing D (defect) in the next round. If the opponent
# continues to defect, escalate by continuing to defect until they return to
# cooperation.  4. **Forgive after opponent returns to cooperation**: If your
# opponent plays C after defecting, return to cooperation (C) in the next round.
# However, if the opponent defects again soon after, escalate the punishment by
# defecting for two consecutive rounds before returning to cooperation.  5.
# **Escalate further for repeated defections**: If the opponent defects multiple
# times in a short period (e.g., within 5 rounds), increase the punishment
# duration by defecting for an additional round each time they defect again
# (e.g., defect for 2 rounds, then 3 rounds, etc.).  6. **Reset after sustained
# cooperation**: If both players cooperate for 10 consecutive rounds, reset the
# punishment escalation, treating the opponent as if they are fully cooperative
# again.  This revised strategy introduces escalating punishment for repeated
# defections, discourages exploitation, and provides a mechanism to reset after
# sustained cooperation, balancing cooperation and deterrence.

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
          self.escalation_level = 0  # Tracks the current level of punishment
          self.coop_streak = 0       # Tracks consecutive cooperation rounds
          return axl.Action.C         # Always cooperate in the first round
  
      # Check if the opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          self.coop_streak = 0  # Reset cooperation streak
          self.escalation_level += 1  # Escalate punishment
          return axl.Action.D  # Defect in response to opponent's defection
  
      # If the opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          if self.escalation_level > 0:
              # If we are in an escalation phase, continue defecting for the required rounds
              self.escalation_level -= 1
              return axl.Action.D
          else:
              # If no escalation, cooperate
              self.coop_streak += 1
              if self.coop_streak >= 10:
                  # Reset escalation after 10 consecutive cooperations
                  self.escalation_level = 0
              return axl.Action.C

# 1. **Start by cooperating (C)** in the first round.  2. **In each subsequent
# round**:    - **If your opponent cooperated (C) in the previous round**,
# continue cooperating (C).    - **If your opponent defected (D) in the previous
# round**, defect (D) in the next round **only once**.  3. **If your opponent
# returns to cooperating (C) after you defect**, immediately return to
# cooperating (C) in the following round.  4. **If your opponent defects (D) for
# 3 consecutive rounds**, defect (D) for 3 rounds in response, then return to
# cooperating (C) to test if they will cooperate again.  5. **If your opponent
# defects (D) for 5 consecutive rounds**, switch to permanent defection (D) for
# the rest of the game.  This revised strategy introduces a more forgiving
# response to occasional defections, avoids unnecessary escalation, and includes
# a mechanism to test for cooperation after a period of defection. It also
# ensures that sustained defection is punished appropriately without being
# overly lenient.

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
          self.defecting_for_three_rounds = False
          self.permanent_defection = False
          return axl.Action.C
  
      # If permanent defection has been triggered, always defect
      if self.permanent_defection:
          return axl.Action.D
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If opponent defected in the last round
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # If opponent has defected for 5 consecutive rounds, switch to permanent defection
      if self.consecutive_defections >= 5:
          self.permanent_defection = True
          return axl.Action.D
  
      # If opponent has defected for 3 consecutive rounds, defect for 3 rounds in response
      if self.consecutive_defections == 3:
          self.defecting_for_three_rounds = True
          self.defect_rounds_left = 3
  
      # If we are in the middle of defecting for 3 rounds
      if self.defecting_for_three_rounds:
          self.defect_rounds_left -= 1
          if self.defect_rounds_left == 0:
              self.defecting_for_three_rounds = False
          return axl.Action.D
  
      # If opponent defected in the last round, defect once
      if last_opponent_move == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# ### Revised Aggressive Strategy for the Iterated Game  1. **Start with
# Defection (D)**: Begin the game by playing D to test your opponent’s initial
# response and gain an immediate advantage if they cooperate.  2. **Defect Until
# Opponent Defects Twice in a Row**: Continue defecting as long as your opponent
# cooperates. If your opponent defects twice consecutively, switch to
# cooperation (C) to avoid the low payoff of mutual defection (1 point per
# round).  3. **Cooperate if Opponent Cooperates**: Once you switch to
# cooperation, continue cooperating as long as your opponent also cooperates.
# This helps establish a mutually beneficial relationship (3 points per round
# for both).  4. **Punish Defection with Temporary Defection**: If your opponent
# defects while you are cooperating, respond by defecting for **two rounds**.
# This punishes the defection but leaves room for the opponent to return to
# cooperation. After two rounds of defection, return to cooperation if the
# opponent also cooperates.  5. **Occasional Defection to Test Opponent’s
# Commitment**: After a stable period of cooperation (at least 10 consecutive
# rounds of mutual cooperation), defect **once** to test your opponent’s
# willingness to continue cooperating. If they respond with cooperation, return
# to cooperation immediately. If they defect, punish with two rounds of
# defection, then attempt to re-establish cooperation.  6. **Endgame Strategy**:
# In the final 10 rounds, defect in **every other round** (starting with
# defection) to maximize your payoff while still leaving some room for
# cooperation. This prevents the opponent from fully anticipating a complete
# defection strategy and may allow for some cooperative rounds.  ### Summary of
# Key Conditions: - Start with defection and continue until the opponent defects
# twice in a row. - Cooperate if the opponent cooperates, but punish defection
# with two rounds of defection. - Occasionally test cooperation with a single
# defection after a long period of mutual cooperation. - In the final 10 rounds,
# defect every other round to balance maximizing payoff and maintaining some
# cooperation.  This revised strategy balances aggression with opportunities for
# cooperation, while also addressing the need to recover from mutual defection
# and avoid overly predictable behavior.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_streak = 0  # Track consecutive cooperation rounds
          self.punishing = 0  # Track punishment rounds
          self.tested_cooperation = False  # Track if we've tested cooperation
          return axl.Action.D  # Start with defection
  
      # Final 10 rounds strategy: defect every other round
      if len(self.history) >= 990:
          if len(self.history) % 2 == 0:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If in punishment mode, defect for two rounds
      if self.punishing > 0:
          self.punishing -= 1
          return axl.Action.D
  
      # Check if opponent defected twice in a row
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.cooperation_streak = 0  # Reset cooperation streak
          return axl.Action.C  # Switch to cooperation
  
      # If both players have been cooperating for 10 rounds, test cooperation
      if self.cooperation_streak >= 10 and not self.tested_cooperation:
          self.tested_cooperation = True
          self.cooperation_streak = 0  # Reset cooperation streak
          return axl.Action.D  # Test with a defection
  
      # If opponent defects while we are cooperating, punish with two defections
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.punishing = 2  # Set punishment for two rounds
          self.cooperation_streak = 0  # Reset cooperation streak
          return axl.Action.D
  
      # If opponent cooperates, continue cooperating
      if opponent.history[-1] == axl.Action.C:
          self.cooperation_streak += 1
          return axl.Action.C
  
      # Default to defection if none of the above conditions are met
      return axl.Action.D

# 1. **Start by cooperating** (play C in the first round).  2. **Continue
# cooperating** (play C) **as long as your opponent also cooperates** (plays C
# in the previous round).  3. **If your opponent defects** (plays D in a
# previous round), **punish them by defecting** (play D) **for two consecutive
# rounds** to discourage repeated defection.  4. **After punishing**, return to
# cooperation (play C) **if your opponent resumes cooperation** (plays C in
# response to your punishment). If they continue defecting, **continue
# defecting** (play D) until they cooperate again.  5. **If your opponent
# alternates between cooperation and defection**, respond by defecting (play D)
# in the round following their defection, but return to cooperation (play C) if
# they show consistent cooperation for at least two consecutive rounds.  6. **If
# defection occurs in the first round**, immediately punish by defecting (play
# D) for two rounds, then return to cooperation (play C) if they cooperate.  7.
# **Allow for occasional mistakes** by forgiving a single defection after one
# round of punishment, but escalate to longer punishment (three rounds of
# defection) if defection becomes frequent (e.g., more than once every five
# rounds).  8. **In the final 10 rounds**, defect (play D) regardless of the
# opponent’s actions, as there is no future incentive to cooperate.  This
# revised strategy addresses continuous defection, alternating behavior,
# potential mistakes, and the endgame scenario, while still promoting
# cooperation when possible.

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
          self.punishment_rounds = 0  # Track how many rounds of punishment are left
          self.defection_count = 0  # Track total defections by opponent
          self.recent_defections = 0  # Track defections in the last 5 rounds
          return axl.Action.C  # Start by cooperating
  
      # Final 10 rounds: defect regardless of opponent's actions
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Update defection count in the last 5 rounds
      if len(self.history) >= 5:
          self.recent_defections = opponent.history[-5:].count(axl.Action.D)
      else:
          self.recent_defections = opponent.history.defections
  
      # If in punishment mode, continue defecting for the required number of rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          self.defection_count += 1
  
          # Punish with 2 rounds of defection
          self.punishment_rounds = 1
  
          # Escalate punishment to 3 rounds if defection is frequent (more than once in 5 rounds)
          if self.recent_defections > 1:
              self.punishment_rounds = 2
  
          return axl.Action.D
  
      # If opponent cooperates after punishment, return to cooperation
      return axl.Action.C

# ### Revised Strategy: **Adaptive Tit-for-Tat with Conditional Forgiveness**
# 1. **Start with Cooperation (C)**: In the first round, play C to signal a
# willingness to cooperate.  2. **Mirror the Opponent's Last Move**: From the
# second round onward, play the same move your opponent made in the previous
# round:    - If they played C, you play C.    - If they played D, you play D.
# 3. **Conditional Forgiveness**: If the opponent defects (plays D) but has
# cooperated in at least 70% of the previous 10 rounds, forgive them by playing
# C in the next round. This encourages cooperation while preventing exploitation
# by frequent defectors.  4. **Punish Persistent Defection**: If the opponent
# defects in 3 consecutive rounds, continue playing D until they cooperate
# again. This ensures that persistent defectors are punished more severely.  5.
# **Endgame Caution**: In the last 3 rounds (rounds 998, 999, and 1000),
# continue to mirror the opponent’s last move rather than automatically playing
# C. This prevents exploitation in the final rounds while still allowing for
# cooperation if the opponent remains cooperative.  This revised strategy
# addresses the critiques by making forgiveness conditional on the opponent's
# overall behavior, punishing persistent defectors more effectively, and
# avoiding vulnerability in the endgame.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if the opponent has cooperated at least 70% in the last 10 rounds
      def has_high_cooperation_rate():
          recent_history = opponent.history[-10:]
          if len(recent_history) < 10:
              return False  # Not enough history to evaluate
          return recent_history.count(axl.Action.C) / 10 >= 0.7
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Endgame caution: In the last 3 rounds, mirror the opponent's last move
      if len(self.history) >= 998:
          return opponent.history[-1]
  
      # Mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          
          # Check if the opponent has cooperated in at least 70% of the last 10 rounds
          if has_high_cooperation_rate():
              return axl.Action.C  # Forgive the defection
          
          # Check if the opponent has defected in the last 3 consecutive rounds
          if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
              return axl.Action.D  # Punish persistent defection
  
          # Otherwise, mirror the defection
          return axl.Action.D

# ### Revised Aggressive Strategy for the Iterated Game  1. **Start with
# Defection (D) in the first round.**    - This maintains an aggressive stance
# initially, but leaves room for adaptation.  2. **In the next 3 rounds, mirror
# the opponent's previous move.**    - If they play C, respond with C in the
# next round. If they play D, respond with D. This allows you to test the
# opponent's willingness to cooperate without committing too early.  3. **If the
# opponent cooperates (C) for 3 out of the first 4 rounds, switch to cooperation
# (C) in the 5th round.**    - This opens the door to mutual cooperation
# earlier, maximizing potential payoffs.  4. **If the opponent defects (D) more
# than once in the first 4 rounds, continue defecting (D) until they show
# consistent cooperation (C) for 3 consecutive rounds.**    - This ensures you
# are not exploited while still allowing for a shift to cooperation if the
# opponent changes their behavior.  5. **If the opponent defects (D) after you
# switch to cooperation (C), return to defection (D) for 2 rounds, then test
# cooperation (C) again.**    - This punishes defection but allows for recovery
# from potential mistakes or exploratory defections by the opponent.  6. **If
# the opponent continues to defect (D) after the 2-round punishment, maintain
# defection (D) for the remainder of the game.**    - This prevents further
# exploitation if the opponent is consistently uncooperative.  7. **If the
# opponent consistently cooperates (C) after the 2-round punishment, return to
# cooperation (C) and maintain it as long as they do.**    - This maximizes the
# mutual payoff while allowing for forgiveness and recovery from occasional
# defections.  This revised strategy balances aggression with flexibility,
# allowing for early cooperation if the opponent shows willingness, while still
# punishing defection and preventing exploitation. It also accounts for
# potential mistakes or exploratory defections by the opponent, offering
# opportunities for recovery.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to count defections in the first 4 rounds
      def count_defections_in_first_4_rounds():
          return opponent.history[:4].count(axl.Action.D)
      
      # Helper function to check if opponent cooperated 3 out of the first 4 rounds
      def cooperated_3_out_of_4():
          return opponent.history[:4].count(axl.Action.C) >= 3
      
      # Helper function to check if opponent cooperated in the last 3 rounds
      def cooperated_last_3_rounds():
          return opponent.history[-3:].count(axl.Action.C) == 3
      
      # Helper function to check if opponent defected in the last round
      def defected_last_round():
          return opponent.history[-1] == axl.Action.D
      
      # Helper function to check if opponent defected in the last 2 rounds
      def defected_last_2_rounds():
          return opponent.history[-2:].count(axl.Action.D) == 2
      
      # First round: always defect
      if self.first_round():
          return axl.Action.D
      
      # Rounds 2-4: mirror the opponent's previous move
      if len(self.history) < 4:
          return opponent.history[-1]
      
      # Round 5: if opponent cooperated 3 out of the first 4 rounds, cooperate
      if len(self.history) == 4:
          if cooperated_3_out_of_4():
              return axl.Action.C
          else:
              return axl.Action.D
      
      # After round 5: if opponent defected more than once in the first 4 rounds, continue defecting
      if count_defections_in_first_4_rounds() > 1:
          if cooperated_last_3_rounds():
              return axl.Action.C
          else:
              return axl.Action.D
      
      # If opponent defects after switching to cooperation, defect for 2 rounds, then test cooperation
      if self.history[-1] == axl.Action.C and defected_last_round():
          return axl.Action.D
      if len(self.history) >= 2 and self.history[-2] == axl.Action.D and self.history[-1] == axl.Action.D:
          return axl.Action.D
      
      # If opponent cooperates after the 2-round punishment, return to cooperation
      if len(self.history) >= 2 and self.history[-2] == axl.Action.D and self.history[-1] == axl.Action.C:
          return axl.Action.C
      
      # Default to mirroring the opponent's last move
      return opponent.history[-1]

# 1. **Start by cooperating (play C) in the first round**.  2. **In each
# subsequent round, mirror your opponent's previous move**:    - If your
# opponent played C in the previous round, play C.    - If your opponent played
# D in the previous round, play D.  3. **Forgive occasional defections**:    -
# If your opponent defects (plays D) but then returns to cooperation (plays C in
# the next round), return to cooperation (play C) immediately in the following
# round.  4. **Allow for recovery from mutual defection**:    - If both you and
# your opponent defect (play D) in the same round, return to cooperation (play
# C) in the next round to test if your opponent is willing to cooperate again.
# 5. **Switch to defection only after sustained defection**:    - If your
# opponent defects for five or more consecutive rounds, switch to defection
# (play D) for the remainder of the game, as this indicates a clear intent to
# exploit.  6. **Adapt to mixed strategies**:    - If your opponent alternates
# between cooperation and defection in a predictable pattern (e.g., every other
# round), continue cooperating as long as the overall payoff remains favorable.
# If the pattern results in a net loss over several rounds, switch to defection.
# This revised strategy encourages cooperation, allows for recovery from
# accidental defections, and adapts to more complex opponent behaviors while
# protecting against sustained exploitation.

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
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C  # Start by cooperating
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # Mirror opponent's previous move
      if opponent_last_move == axl.Action.C:
          self.consecutive_defections = 0  # Reset defection count if opponent cooperates
          return axl.Action.C
      else:
          self.consecutive_defections += 1  # Increment defection count if opponent defects
  
      # Forgive occasional defections: if opponent defects but cooperates next
      if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D and opponent_last_move == axl.Action.C:
          self.consecutive_defections = 0  # Reset defection count
          return axl.Action.C
  
      # Allow for recovery from mutual defection
      if self.history[-1] == axl.Action.D and opponent_last_move == axl.Action.D:
          return axl.Action.C  # Return to cooperation after mutual defection
  
      # Switch to defection after sustained defection (5 or more consecutive defections)
      if self.consecutive_defections >= 5:
          return axl.Action.D  # Defect for the rest of the game
  
      # Adapt to mixed strategies: check if alternating pattern is favorable
      if len(self.history) >= 4:
          # Check the last 4 rounds for an alternating pattern
          if (opponent.history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D] or
              opponent.history[-4:] == [axl.Action.D, axl.Action.C, axl.Action.D, axl.Action.C]):
              # Calculate the score over the last 4 rounds
              my_score, opponent_score = self.total_scores(self.history[-4:], opponent.history[-4:])
              if my_score >= opponent_score:
                  return axl.Action.C  # Continue cooperating if the payoff is favorable
              else:
                  return axl.Action.D  # Defect if the pattern results in a net loss
  
      # Default to mirroring the opponent's last move
      return opponent_last_move

# 1. **Start with Cooperation (C):** In the first round, always choose C.  2.
# **Mirror Your Opponent’s Last Move:**    - In each subsequent round (from
# round 2 onwards), choose the same move your opponent played in the previous
# round.  3. **Forgive Occasional Defections:**    - If your opponent defects
# (plays D) once, continue cooperating (play C) in the next round to test if the
# defection was a one-time event.  4. **Retaliate After Consecutive
# Defections:**    - If your opponent defects twice in a row, retaliate by
# defecting (play D) in the next round. Continue defecting until your opponent
# returns to cooperation (plays C).  5. **Return to Cooperation After Opponent
# Cooperates:**    - Once your opponent returns to cooperation (plays C),
# immediately return to cooperation (play C) in the following round.  6.
# **Punish Persistent Defection:**    - If your opponent alternates between
# cooperation and defection (e.g., C-D-C-D), defect (play D) until they
# cooperate for two consecutive rounds. After two consecutive cooperative moves
# from your opponent, return to cooperation.  This revised strategy addresses
# the issues of overreaction, alternating behavior, and exploitation, while
# maintaining a balance between cooperation and retaliation.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.alternating_defections = False  # Track alternating behavior
          return axl.Action.C  # Start with cooperation
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # Check if the opponent is alternating between C and D
      if len(opponent.history) >= 2:
          if opponent.history[-2] == axl.Action.C and opponent_last_move == axl.Action.D:
              self.alternating_defections = True
          else:
              self.alternating_defections = False
  
      # If opponent alternates between C and D, defect until they cooperate twice in a row
      if self.alternating_defections:
          if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
              return axl.Action.C  # Return to cooperation after two consecutive cooperations
          else:
              return axl.Action.D  # Defect until two consecutive cooperations
  
      # If opponent defected twice in a row, retaliate
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          self.consecutive_defections = 2
          return axl.Action.D  # Retaliate with defection
  
      # If opponent defected once, forgive and cooperate
      if opponent_last_move == axl.Action.D:
          self.consecutive_defections = 1
          return axl.Action.C  # Forgive a single defection
  
      # If opponent cooperates, reset defection count and cooperate
      if opponent_last_move == axl.Action.C:
          self.consecutive_defections = 0
          return axl.Action.C  # Return to cooperation

# 1. **Start the game by cooperating (C).**      - This encourages mutual
# cooperation and avoids provoking immediate retaliation.  2. **Defect (D) if
# your opponent defects in any round.**      - This punishes defection and
# discourages the opponent from exploiting your cooperation.  3. **If your
# opponent cooperates for 3 consecutive rounds after you defect, return to
# cooperating.**      - This allows for the possibility of re-establishing
# cooperation after a breakdown, but ensures the opponent is committed to
# cooperation before you reciprocate.  4. **If your opponent defects again after
# you return to cooperation, defect for 5 consecutive rounds before testing
# cooperation again.**      - This escalates the punishment for repeated
# defections, making it costly for the opponent to exploit you.  5. **In the
# final 10 rounds, defect only if your opponent defects first.**      - This
# prevents the opponent from exploiting you in the endgame while still allowing
# for cooperation if they remain cooperative.  6. **If mutual defection occurs
# for more than 10 consecutive rounds, attempt to cooperate once.**      - This
# provides a mechanism to break out of a cycle of mutual defection and
# potentially restore higher payoffs for both players.

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
          self.defect_streak = 0  # Tracks how many rounds we are defecting after opponent defects again
          self.coop_after_defect = 0  # Tracks how many consecutive cooperations opponent has made after our defection
          return axl.Action.C  # Start by cooperating
  
      # Check if we are in the final 10 rounds
      if len(self.history) >= 990:
          # In the final 10 rounds, defect only if opponent defects first
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If we are in a defect streak, continue defecting for 5 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # If mutual defection has occurred for more than 10 consecutive rounds, attempt to cooperate once
      if len(self.history) >= 10 and all(x == axl.Action.D for x in self.history[-10:]) and all(x == axl.Action.D for x in opponent.history[-10:]):
          return axl.Action.C
  
      # If opponent defected in the last round, we defect
      if opponent.history[-1] == axl.Action.D:
          self.coop_after_defect = 0  # Reset cooperation counter after opponent defects
          return axl.Action.D
  
      # If opponent has cooperated for 3 consecutive rounds after our defection, return to cooperation
      if len(self.history) >= 3 and self.history[-1] == axl.Action.D:
          if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
              self.coop_after_defect = 0  # Reset cooperation counter
              return axl.Action.C
  
      # If opponent defects again after we return to cooperation, defect for 5 consecutive rounds
      if len(self.history) >= 2 and self.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.defect_streak = 5  # Set defect streak to 5 rounds
          return axl.Action.D
  
      # If none of the above conditions are met, cooperate
      return axl.Action.C

# 1. **Start by cooperating**: In the first round, play C (cooperate).  2.
# **Continue cooperating as long as your opponent cooperates**: If your opponent
# plays C, keep playing C in the following rounds.  3. **Defect only after two
# consecutive defections by your opponent**: If your opponent defects (plays D)
# once, continue playing C to give them a chance to return to cooperation. If
# they defect again in the next round, respond by playing D in the following
# round.  4. **Escalate punishment for repeated defections**: If your opponent
# continues to defect after you start playing D, keep playing D until they
# return to cooperation (play C). This ensures that persistent defection is met
# with sustained punishment.  5. **Forgive after opponent returns to
# cooperation**: If your opponent plays C after a period of defection, return to
# playing C in the next round. This allows cooperation to resume but only after
# the opponent demonstrates a willingness to cooperate.  6. **Monitor for
# alternating defection patterns**: If your opponent alternates between
# cooperation and defection (e.g., plays C, then D, then C, etc.), respond by
# defecting in the round after their defection. This prevents exploitation by
# opponents who try to take advantage of alternating strategies.  This revised
# strategy balances cooperation with a more measured response to defection,
# allowing for forgiveness but also ensuring that repeated or patterned
# defections are met with appropriate punishment.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating
      if self.first_round():
          return axl.Action.C
  
      # Check the last two moves of the opponent
      if len(opponent.history) >= 2:
          last_two_moves = opponent.history[-2:]
          # If the opponent defected twice in a row, defect
          if last_two_moves == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
  
      # If the opponent alternates between cooperation and defection, defect after their defection
      if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent cooperates, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected once, give them a chance to return to cooperation
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.C

# ### Revised Neutral Strategy for Iterated Game (1000 Rounds)  1. **Start with
# Cooperation (C)**: In the first round, play C to signal a willingness to
# cooperate, but be prepared to adjust based on the opponent's response.  2.
# **Tit-for-Tat with Forgiveness**: From the second round onwards, mirror the
# opponent's last move. If they play C, you play C. If they play D, you play D.
# However, if the opponent defects (plays D) once, forgive them by playing C in
# the next round to test if they return to cooperation.  3. **Forgiveness
# Window**: If the opponent returns to cooperation (C) within 1 round after
# defecting, continue cooperating (C). If they defect again immediately after
# your forgiveness, switch to defection (D) until they show consistent
# cooperation for at least 2 consecutive rounds.  4. **Respond to Persistent
# Defection**: If the opponent defects (plays D) for 4 or more consecutive
# rounds, switch to defection (D) for the remainder of the game, as they are
# likely committed to exploiting you.  5. **Endgame Defection Adjustment**: In
# the final 3 rounds, defect (D) regardless of the opponent's actions, as
# cooperation is less likely to be reciprocated in the very last rounds. This
# minimizes the risk of being exploited at the end while still allowing for
# cooperation in most of the game.  This revised strategy balances cooperation,
# forgiveness, and defection more flexibly, while also adjusting the endgame
# defection timing to avoid premature loss of cooperative payoffs.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants for actions
      C, D = axl.Action.C, axl.Action.D
  
      # Check if it's the first round
      if self.first_round():
          return C  # Start with cooperation
  
      # Endgame defection adjustment: Defect in the last 3 rounds
      if len(self.history) >= 997:
          return D
  
      # Count opponent's defections in the last 4 rounds
      recent_defections = opponent.history[-4:].count(D)
  
      # Respond to persistent defection: Defect if opponent defected 4 or more times in a row
      if recent_defections == 4:
          return D
  
      # Tit-for-Tat with Forgiveness
      if opponent.history[-1] == D:
          # If opponent defected last round, forgive by playing C this round
          if len(self.history) > 1 and opponent.history[-2] == D:
              # If opponent defected two rounds in a row, switch to defection
              return D
          else:
              return C  # Forgive once
      else:
          # If opponent cooperated last round, continue cooperating
          return C

# 1. **Start by playing C (cooperate) in the first round.**      - This signals
# a willingness to cooperate and encourages mutual cooperation from the outset,
# maximizing the potential for higher long-term payoffs.  2. **If your opponent
# plays C, continue playing C.**      - Maintain cooperation as long as the
# opponent cooperates, ensuring both players consistently score 3 points per
# round.  3. **If your opponent plays D (defects), immediately switch to D in
# the next round.**      - Punish defection swiftly to prevent exploitation, but
# do not overcommit to defection.  4. **After one round of mutual defection
# (both playing D), switch back to C to test for cooperation.**      - This
# allows for recovery from misunderstandings or occasional defections, giving
# the opponent a chance to return to cooperation.  5. **If the opponent responds
# to your cooperative test with C, continue playing C.**      - Reward their
# return to cooperation by re-establishing mutual cooperation.  6. **If the
# opponent defects again after your cooperative test (i.e., you play C and they
# play D), switch to D and continue defecting for the next 3 rounds.**      -
# This escalates the punishment for repeated defection, signaling that continued
# betrayal will not be tolerated.  7. **After 3 rounds of mutual defection, test
# cooperation again by playing C.**      - This gives the opponent another
# opportunity to return to cooperation, but with a stronger deterrent against
# further defection.  8. **If the opponent continues to defect after multiple
# cooperative tests, defect for the remainder of the game.**      - At this
# point, the opponent has shown they are not willing to cooperate, so maximize
# your score by defecting consistently.  9. **In the final 10 rounds, defect
# only if the opponent has defected in the previous round.**      - Avoid
# predictable defection in the final rounds to prevent the opponent from
# exploiting you early. If they continue cooperating, maintain cooperation to
# maximize mutual payoffs.  This revised strategy balances an initial
# cooperative approach with a measured response to defection, allowing for
# recovery from occasional betrayals while punishing consistent defection. It
# also avoids predictable behavior in the final rounds, reducing the risk of
# exploitation.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_count = 0  # Track consecutive defections after cooperative tests
          return axl.Action.C  # Start by cooperating
  
      # Get the last move of both players
      my_last_move = self.history[-1]
      opponent_last_move = opponent.history[-1]
  
      # Final 10 rounds strategy: defect only if opponent defected in the previous round
      if len(self.history) >= 990:
          if opponent_last_move == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent cooperated in the last round, continue cooperating
      if opponent_last_move == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round
      if opponent_last_move == axl.Action.D:
          # If we just defected and this is the first round of mutual defection, switch back to C
          if my_last_move == axl.Action.D and self.defection_count == 0:
              return axl.Action.C
  
          # If we cooperated and opponent defected, escalate punishment
          if my_last_move == axl.Action.C:
              self.defection_count = 3  # Set to defect for the next 3 rounds
              return axl.Action.D
  
          # If we are in the middle of a 3-round defection punishment
          if self.defection_count > 0:
              self.defection_count -= 1
              return axl.Action.D
  
          # After 3 rounds of defection, test cooperation again
          if self.defection_count == 0:
              return axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# 1. **Start by cooperating (play C).**  2. **Continue cooperating (play C) as
# long as your opponent cooperates (plays C).**  3. **If your opponent defects
# (plays D), retaliate by defecting (play D) in the next round.**  4. **If your
# opponent returns to cooperation (plays C) after a single defection, forgive
# and return to cooperation (play C).**  5. **If your opponent defects twice in
# a row, continue defecting (play D) until they cooperate for two consecutive
# rounds. Once they cooperate twice in a row, return to cooperation (play C).**
# 6. **If your opponent alternates between cooperation and defection, defect
# (play D) until they show consistent cooperation for two consecutive rounds,
# then return to cooperation (play C).**  This revised strategy allows for more
# flexibility in handling alternating or exploratory defections, avoids
# premature escalation to permanent defection, and provides a clear path for
# returning to cooperation after multiple defections.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if opponent cooperated in the last N rounds
      def opponent_cooperated_last_n(n):
          return all(move == axl.Action.C for move in opponent.history[-n:])
  
      # Helper function to check if opponent defected in the last N rounds
      def opponent_defected_last_n(n):
          return all(move == axl.Action.D for move in opponent.history[-n:])
  
      # If opponent alternates between cooperation and defection
      if len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]:
          # Defect until opponent cooperates for two consecutive rounds
          if not opponent_cooperated_last_n(2):
              return axl.Action.D
  
      # If opponent defected twice in a row
      if opponent_defected_last_n(2):
          # Defect until opponent cooperates for two consecutive rounds
          if not opponent_cooperated_last_n(2):
              return axl.Action.D
  
      # If opponent defected once, retaliate by defecting in the next round
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# ### Revised Strategy: Adaptive Tit-for-Tat with Forgiveness  1. **First
# Move**: Begin by cooperating (play C).  2. **Tit-for-Tat Response**: In each
# subsequent round, mimic your opponent’s previous move.    - If your opponent
# played C in the last round, play C.    - If your opponent played D in the last
# round, play D.  3. **Defection Trigger**: If your opponent defects (plays D)
# two times in a row:    - Defect (play D) for the next round only, regardless
# of their move.  4. **Forgiveness Mechanism**: After punishing with one round
# of defection, return to cooperation (play C) immediately, even if the opponent
# continues to defect. This gives the opponent a chance to re-establish
# cooperation.  5. **Adaptation to Consistent Defection**: If your opponent
# defects for **five consecutive rounds**, switch to always defecting (play D)
# for the remainder of the game, as they are likely committed to defection.  6.
# **Occasional Cooperation Test**: If you have switched to always defecting due
# to consistent defection by the opponent, test their willingness to cooperate
# by playing C once every 50 rounds. If they respond with C, return to the Tit-
# for-Tat strategy.  ---  This revised strategy balances cooperation and
# punishment, introduces a forgiveness mechanism, and adapts to consistently
# uncooperative opponents while still allowing for the possibility of re-
# establishing cooperation.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.punished = False
          self.always_defect = False
          return axl.Action.C  # First move is always cooperation
  
      # Check if we are in the "always defect" mode
      if self.always_defect:
          # Test cooperation every 50 rounds
          if len(self.history) % 50 == 0:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Tit-for-Tat response: mimic opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Adaptation to consistent defection: switch to always defect after 5 consecutive defections
      if self.consecutive_defections >= 5:
          self.always_defect = True
          return axl.Action.D
  
      # Defection trigger: punish if opponent defected two times in a row
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          if not self.punished:
              self.punished = True
              return axl.Action.D  # Punish with one round of defection
      else:
          self.punished = False
  
      # Forgiveness mechanism: return to cooperation after punishing
      return axl.Action.C

# 1. **Initial Move**: Start by playing **C** in the first round. This signals a
# willingness to cooperate and opens the possibility for mutual cooperation,
# which can lead to higher long-term payoffs.  2. **Opponent Response**:    - If
# your opponent plays **C** in response, continue playing **C** to maintain
# mutual cooperation.    - If your opponent plays **D** in response, immediately
# switch to **D** in the next round to prevent exploitation.  3. **Tit-for-Tat
# with Gradual Punishment**:    - If your opponent defects (plays **D**) after
# you play **C**, respond with **D** in the next round to punish them.    - If
# they continue to defect, keep playing **D** for **three consecutive rounds**
# to escalate the punishment.    - After three rounds of mutual defection,
# switch back to **C** to test if they are willing to return to cooperation.  4.
# **Forgiveness Mechanism**: If your opponent switches back to **C** after your
# punishment, immediately return to playing **C** to restore cooperation. This
# allows for recovery from occasional defections and avoids prolonged mutual
# defection.  5. **Adaptability**: If your opponent consistently defects (plays
# **D** for more than five consecutive rounds), switch to permanent defection
# (always play **D**) to avoid being exploited for the remainder of the game.
# 6. **Endgame (Last 20 Rounds)**: In the final 20 rounds, begin defecting by
# playing **D** every round. This ensures you maximize your payoff toward the
# end, while minimizing the risk of retaliation affecting long-term cooperation.
# 7. **Exception for Cooperative Opponents**: If your opponent has consistently
# cooperated throughout the game (with no more than one defection), continue
# playing **C** even in the last 20 rounds to maintain mutual cooperation and
# maximize both players' payoffs.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_rounds = 0  # Tracks how many rounds of punishment (D) have been played
          self.permanent_defection = False  # Tracks if we have switched to permanent defection
          return axl.Action.C  # Initial move is always C
  
      # If we are in permanent defection mode, always play D
      if self.permanent_defection:
          return axl.Action.D
  
      # Check if we are in the last 20 rounds
      if len(self.history) >= 980:
          # Exception for cooperative opponents: if they have defected no more than once, continue cooperating
          if opponent.history.defections <= 1:
              return axl.Action.C
          # Otherwise, defect in the last 20 rounds
          return axl.Action.D
  
      # If the opponent has defected more than 5 consecutive times, switch to permanent defection
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.permanent_defection = True
          return axl.Action.D
  
      # If we are in the middle of a punishment phase (3 rounds of D after a defection)
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # If the opponent defected in the last round, start the punishment phase
      if opponent.history[-1] == axl.Action.D:
          self.punishment_rounds = 3  # Punish for 3 rounds
          return axl.Action.D
  
      # If the opponent cooperated in the last round, return to cooperation
      return axl.Action.C

# ### Revised Strategy: **Tit-for-Tat with Conditional Forgiveness**  1. **Start
# with Cooperation**:      - In the first round, play **C** (cooperate).  2.
# **Mirror Opponent’s Last Move**:      - For each subsequent round, play
# exactly what your opponent played in the previous round. If they played **C**,
# play **C**. If they played **D**, play **D**.  3. **Forgive After a Single
# Defection**:      - If your opponent defects once (i.e., plays **D** while you
# played **C**), forgive them by playing **C** in the next round. This
# encourages them to return to cooperation. However, only forgive once in a row.
# 4. **Punish Persistent Defection**:      - If your opponent defects two times
# in a row (i.e., plays **D** in two consecutive rounds), switch to **D** and
# continue defecting until they return to cooperation. This prevents
# exploitation by persistent defectors.  5. **Return to Cooperation After Mutual
# Defection**:      - If both you and your opponent have played **D** in the
# last round, return to **C** in the next round to give them a chance to
# cooperate again. However, if they defect again after this, follow the
# punishment rule (step 4).  6. **Never Defect First**:      - Always maintain
# cooperation unless your opponent defects first. This ensures you are not the
# one initiating conflict.  This revised strategy balances cooperation with a
# more robust response to persistent defection, reducing the risk of
# exploitation while still allowing for recovery of cooperation after occasional
# defections.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Step 1: Start with Cooperation
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Mirror Opponent’s Last Move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: Forgive After a Single Defection
      if opponent.history[-1] == axl.Action.D:
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              # Step 4: Punish Persistent Defection
              return axl.Action.D
          else:
              # Forgive a single defection
              return axl.Action.C
  
      # Step 5: Return to Cooperation After Mutual Defection
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# **Revised Strategy:**  1. **Start with Cooperation (C):** On the first round,
# play C to signal a willingness to cooperate and establish a baseline for
# mutual benefit.  2. **Tit-for-Tat with Limited Forgiveness:** From the second
# round onward, adopt a tit-for-tat approach with a stricter forgiveness rule:
# - If your opponent played C in the previous round, play C in the current
# round.    - If your opponent played D in the previous round, play D in the
# current round.    - **Forgive only after three consecutive cooperations** from
# the opponent following a defection. This ensures that the opponent is
# genuinely shifting back to cooperation and prevents exploitation from
# inconsistent behavior.  3. **Punish Persistent Defection More Aggressively:**
# If your opponent defects for two consecutive rounds, switch to playing D for
# **three consecutive rounds** to punish persistent defection. This increases
# the cost of defection for the opponent and discourages repeated exploitation.
# 4. **Adapt to Opponent Behavior:** If the opponent alternates between
# cooperation and defection frequently (e.g., every other round), switch to
# playing D consistently until they demonstrate a clear pattern of cooperation
# for at least three consecutive rounds. This prevents the opponent from
# exploiting predictable tit-for-tat behavior.  5. **Final 20 Rounds - Shift to
# Defection Earlier:** In the last 20 rounds, begin to defect more frequently.
# Start by defecting every third round, then gradually increase the frequency of
# defection as the game approaches the final 10 rounds. In the last 5 rounds,
# defect consistently to maximize your payoff, as cooperation becomes less
# valuable near the end.  6. **Adjust for Random or Irrational Opponents:** If
# the opponent’s behavior appears random or irrational (e.g., no discernible
# pattern of cooperation or defection), switch to playing D consistently after
# the first 10 rounds to avoid being exploited by unpredictable behavior.  This
# revised strategy incorporates stricter forgiveness, more aggressive punishment
# for persistent defection, and an earlier shift to defection in the final
# rounds, while also accounting for the possibility of facing random or
# irrational opponents.

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
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.punishment_rounds = 0
          return axl.Action.C  # Start with cooperation
  
      # Track opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Update consecutive cooperation and defection counters
      if last_opponent_move == axl.Action.C:
          self.consecutive_cooperations += 1
          self.consecutive_defections = 0
      else:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
  
      # Punish persistent defection
      if self.consecutive_defections >= 2:
          self.punishment_rounds = 3
  
      # If in punishment mode, continue defecting for 3 rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Forgive after 3 consecutive cooperations following a defection
      if self.consecutive_cooperations >= 3:
          self.consecutive_defections = 0
  
      # Adapt to alternating behavior (C, D, C, D, etc.)
      if len(opponent.history) >= 4 and opponent.history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
          return axl.Action.D
  
      # Final 20 rounds strategy
      if len(self.history) >= 980:
          rounds_left = 1000 - len(self.history)
          if rounds_left <= 5:
              return axl.Action.D  # Defect consistently in the last 5 rounds
          elif rounds_left <= 10:
              return axl.Action.D if rounds_left % 2 == 0 else axl.Action.C  # Defect more frequently
          elif rounds_left <= 20:
              return axl.Action.D if rounds_left % 3 == 0 else axl.Action.C  # Defect every third round
  
      # Handle random or irrational opponents
      if len(self.history) >= 10 and self.history[-10:].count(axl.Action.C) < 3:
          return axl.Action.D  # Switch to defection if opponent is unpredictable
  
      # Tit-for-tat with limited forgiveness
      return last_opponent_move


Aggressive_ranks = [
'Aggressive_8',
'Aggressive_9',
'Aggressive_3',
'Aggressive_5',
'Aggressive_10',
'Aggressive_6',
'Aggressive_2',
'Aggressive_1',
'Aggressive_4',
'Aggressive_7',
]

Cooperative_ranks = [
'Cooperative_4',
'Cooperative_3',
'Cooperative_7',
'Cooperative_2',
'Cooperative_8',
'Cooperative_5',
'Cooperative_6',
'Cooperative_9',
'Cooperative_1',
'Cooperative_10',
]

Neutral_ranks = [
'Neutral_10',
'Neutral_5',
'Neutral_1',
'Neutral_3',
'Neutral_6',
'Neutral_2',
'Neutral_7',
'Neutral_9',
'Neutral_8',
'Neutral_4',
]

Aggressive_ranks = [
'Aggressive_8',
'Aggressive_9',
'Aggressive_3',
'Aggressive_5',
'Aggressive_10',
'Aggressive_6',
'Aggressive_2',
'Aggressive_1',
'Aggressive_4',
'Aggressive_7',
]

Cooperative_ranks = [
'Cooperative_4',
'Cooperative_3',
'Cooperative_7',
'Cooperative_2',
'Cooperative_8',
'Cooperative_5',
'Cooperative_6',
'Cooperative_9',
'Cooperative_1',
'Cooperative_10',
]

Neutral_ranks = [
'Neutral_10',
'Neutral_5',
'Neutral_1',
'Neutral_3',
'Neutral_6',
'Neutral_2',
'Neutral_7',
'Neutral_9',
'Neutral_8',
'Neutral_4',
]