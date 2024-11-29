import axelrod as axl

from evollm.common import Attitude, auto_update_score, LLM_Strategy

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



# ### Revised Strategy: Opportunistic Cooperation with Punishment  1. **First
# move: Cooperate (C)**      Start by cooperating to signal a willingness to
# establish mutual cooperation, which yields the highest long-term payoff (3
# points per round).  2. **If your opponent cooperates (C): Continue cooperating
# (C)**      If your opponent also cooperates, continue cooperating in every
# round to maximize mutual payoffs (3 points each round). Do not defect unless
# the opponent defects first.  3. **If your opponent defects (D): Defect (D) in
# the next round**      If your opponent defects, immediately retaliate by
# defecting in the next round. This discourages further defection by showing
# that you will not tolerate exploitation.  4. **After retaliating with
# defection: Return to cooperation (C) if the opponent cooperates**      After
# one round of defection, if your opponent returns to cooperation, immediately
# switch back to cooperation. This signals that you are willing to forgive and
# re-establish mutual cooperation.  5. **If the opponent continues to defect
# (D): Defect (D) until they cooperate**      If the opponent continues to
# defect after your initial retaliation, keep defecting until they switch back
# to cooperation. This ensures that you are not exploited while also giving the
# opponent a chance to return to cooperation.  6. **Endgame (last 3 rounds):
# Defect (D)**      In the final 3 rounds, always defect regardless of the
# opponent’s actions. Since the game is finite, defection in the last few rounds
# maximizes your points without risking long-term retaliation.  ### Summary: -
# Start with cooperation to establish trust and maximize mutual payoffs. -
# Retaliate immediately after defection but return to cooperation if the
# opponent does. - Punish persistent defection with continued defection until
# the opponent cooperates again. - Defect in the final 3 rounds to secure
# maximum points at the end of the game.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First move: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Endgame: Defect in the last 3 rounds
      if len(self.history) >= 997:
          return axl.Action.D
  
      # If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round, retaliate by defecting
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D

# ### Revised Cooperative Strategy for Maximising Overall Payoff  1. **Start by
# cooperating**: On the first round, play **C (Cooperate)**.  2. **Continue
# cooperating if both players cooperate**: As long as both you and your opponent
# play **C** in the previous round, continue to play **C** in the next round.
# 3. **Punish defection with a temporary response**: If your opponent plays **D
# (Defect)** while you played **C**, switch to **D** for the next **two rounds**
# to punish the defection. This provides a clear but limited consequence for
# defection.  4. **Return to cooperation after punishment**: After the two-round
# punishment, return to **C** regardless of your opponent’s actions, signaling a
# willingness to restore cooperation. This prevents prolonged mutual defection
# cycles.  5. **Test for opponent's cooperation after defection**: If your
# opponent continues to defect after the punishment period, play **C** once more
# to test if they are willing to return to cooperation. If they cooperate,
# continue cooperating. If they defect again, switch to **D** for another two
# rounds.  6. **Endgame strategy with gradual defection**: In the final 10
# rounds, begin to defect **gradually**. Start by defecting every other round
# (alternating between **C** and **D**), and in the final 3 rounds, defect
# consistently. This reduces the risk of early defection by the opponent while
# still maximising short-term payoffs.  ---  This revised strategy incorporates
# a more measured punishment, forgiveness, and testing mechanism, while also
# addressing the endgame defection issue by introducing a gradual shift to
# defection rather than an abrupt switch.

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
          self.punishment_rounds_left = 0
          return axl.Action.C
  
      # Get the current round number
      current_round = len(self.history)
  
      # Endgame strategy: Gradual defection in the last 10 rounds
      if current_round > 990:
          if current_round > 997:  # Final 3 rounds: defect consistently
              return axl.Action.D
          elif current_round % 2 == 0:  # Defect every other round
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If in punishment phase, continue defecting for the remaining punishment rounds
      if self.punishment_rounds_left > 0:
          self.punishment_rounds_left -= 1
          return axl.Action.D
  
      # If both players cooperated in the last round, continue cooperating
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected while we cooperated, initiate a 2-round punishment
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.punishment_rounds_left = 2
          return axl.Action.D
  
      # If opponent continues to defect after punishment, test cooperation by playing C
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C

# 1. **Start by cooperating (C).**      On the first round, play C to establish
# a cooperative stance.  2. **Continue cooperating if both players cooperated in
# the previous round.**      If the opponent also played C in the last round,
# keep playing C to maintain mutual cooperation.  3. **Defect (D) if the
# opponent defects, but only for two rounds.**      If the opponent plays D,
# retaliate by playing D for the next two rounds. This ensures punishment but
# avoids getting stuck in a cycle of mutual defection.  4. **After two rounds of
# defection, test for cooperation by playing C.**      After punishing the
# opponent with two rounds of D, return to C to test if the opponent is willing
# to cooperate again.  5. **If the opponent defects again after your test,
# switch to permanent defection.**      If the opponent defects after you return
# to C, assume they are not interested in cooperation and switch to playing D
# for the rest of the game.  6. **If mutual cooperation is restored, continue
# cooperating.**      If the opponent responds to your test by playing C,
# continue cooperating as long as they do.  This revised strategy introduces a
# limited punishment period, a test for cooperation after defection, and a
# mechanism to permanently defect if the opponent consistently defects,
# addressing the critiques of the original strategy.

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
          self.retaliation_count = 0  # Tracks how many rounds of defection we've retaliated
          self.permanent_defection = False  # Tracks if we've switched to permanent defection
          return axl.Action.C  # Start by cooperating
  
      # If we've switched to permanent defection, always defect
      if self.permanent_defection:
          return axl.Action.D
  
      # If we are in the retaliation phase, continue defecting for two rounds
      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D
  
      # If the opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # Start retaliating by defecting for the next two rounds
          self.retaliation_count = 2
          return axl.Action.D
  
      # If we are testing for cooperation after retaliation
      if len(self.history) >= 3 and self.history[-3] == axl.Action.D and self.history[-2] == axl.Action.D:
          # If the opponent defected after our test for cooperation, switch to permanent defection
          if opponent.history[-1] == axl.Action.D:
              self.permanent_defection = True
              return axl.Action.D
  
      # If both players cooperated in the last round, continue cooperating
      return axl.Action.C

# ### Revised Strategy for 1000-Round Iterated Game  1. **Initial Play (Round
# 1):**      Start by playing **C** (Cooperate) to test your opponent's
# willingness to cooperate.  2. **Tit-for-Tat with Occasional Defection (Rounds
# 2–990):**      - **If your opponent played C in the previous round**:
# Play **C** to encourage mutual cooperation and maximize long-term payoffs (3
# points each round).        - **If your opponent played D in the previous
# round**:        Play **D** in the next round to punish defection and prevent
# exploitation. However, after one round of mutual defection, return to **C** to
# test if the opponent is willing to cooperate again.  3. **Occasional Defection
# (Rounds 2–990):**      Every 50 rounds, regardless of the opponent's behavior,
# play **D** once to test if the opponent is overly trusting and can be
# exploited for a higher payoff. If the opponent retaliates with D, return to
# cooperation in the next round.  4. **Endgame (Final 10 Rounds):**      In the
# last 10 rounds, gradually shift to more defection:    - **Rounds 991–995**:
# Play **C** if the opponent has been cooperative, but defect once or twice to
# test their response.    - **Rounds 996–1000**: Play **D** consistently to
# secure points and avoid being exploited in the final rounds.  ### Rationale
# This revised strategy balances cooperation and defection, allowing for long-
# term cooperation when possible while still testing the opponent's trust
# periodically. It includes a mechanism to recover from mutual defection and
# adapts to different opponent behaviors. The endgame shift to defection secures
# points while minimizing the risk of late-game exploitation.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Round 1: Always start with cooperation
      if self.first_round():
          return axl.Action.C
      
      # Rounds 2-990: Tit-for-Tat with occasional defection
      if len(self.history) <= 990:
          # Every 50 rounds, defect once
          if len(self.history) % 50 == 0:
              return axl.Action.D
          
          # Tit-for-Tat logic
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
      
      # Rounds 991-995: Mostly cooperate, but defect once or twice
      if 991 <= len(self.history) <= 995:
          if self._random.random_choice(0.2):  # 20% chance to defect
              return axl.Action.D
          return axl.Action.C
      
      # Rounds 996-1000: Always defect
      if len(self.history) >= 996:
          return axl.Action.D

# **Revised Strategy:**  1. **Start with cooperation**: In the first round, play
# C (cooperate).  2. **Tit-for-Tat with immediate response**:    - In each
# subsequent round, mimic your opponent's previous move (i.e., if they played C
# in the previous round, you play C; if they played D, you play D).  3.
# **Forgive isolated defections**:    - If your opponent defects (plays D) but
# has cooperated in 4 of the last 5 rounds, return to cooperation (play C) in
# the next round, assuming the defection was an isolated mistake.  4. **Punish
# consistent defections quickly**:    - If your opponent defects for 2
# consecutive rounds, switch to playing D (defect) in the next round to signal
# that consistent defection will not be tolerated.  5. **Escalate punishment for
# persistent defectors**:    - If your opponent continues to defect for 3 or
# more consecutive rounds, continue defecting (play D) until they cooperate for
# 3 consecutive rounds. This ensures that persistent defectors face a strong
# response.  6. **Return to cooperation after sustained cooperation**:    - If
# your opponent cooperates for 3 consecutive rounds after a period of defection,
# return to cooperation (play C) in the next round to re-establish a cooperative
# relationship.  7. **Handle long-term defectors**:    - If your opponent
# defects for more than 10 consecutive rounds, assume they are a persistent
# defector and continue defecting for the remainder of the game to avoid being
# exploited.  This revised strategy addresses the previous critiques by
# clarifying forgiveness conditions, responding more quickly to defections, and
# providing a clear mechanism for handling persistent defectors.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Start with cooperation
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if opponent cooperated in 4 of the last 5 rounds
      def opponent_cooperated_4_of_last_5():
          return opponent.history[-5:].count(axl.Action.C) >= 4
  
      # Helper function to check if opponent defected for N consecutive rounds
      def opponent_defected_consecutively(n):
          return opponent.history[-n:] == [axl.Action.D] * n
  
      # Tit-for-Tat: Mimic opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected but cooperated in 4 of the last 5 rounds, forgive and cooperate
      if opponent.history[-1] == axl.Action.D and opponent_cooperated_4_of_last_5():
          return axl.Action.C
  
      # If opponent defected for 2 consecutive rounds, punish by defecting
      if opponent_defected_consecutively(2):
          return axl.Action.D
  
      # If opponent defected for 3 or more consecutive rounds, continue defecting
      if opponent_defected_consecutively(3):
          # Continue defecting until opponent cooperates for 3 consecutive rounds
          if opponent.history[-3:] == [axl.Action.C] * 3:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If opponent defected for more than 10 consecutive rounds, assume they are a persistent defector
      if opponent_defected_consecutively(10):
          return axl.Action.D
  
      # Default to Tit-for-Tat (mimic opponent's last move)
      return opponent.history[-1]

# ### Revised Strategy for the Iterated Normal-Form Game:  1. **Start with
# Cooperation (C):** In the first round, always play C to signal a willingness
# to cooperate.  2. **Tit-for-Tat with Occasional Forgiveness:**    - In each
# subsequent round, play what your opponent played in the previous round (Tit-
# for-Tat).    - If your opponent defects, respond with defection (D) in the
# next round.    - **Forgive after a single defection**: If your opponent
# cooperates after defecting once, return to cooperation (C) immediately. This
# prevents long cycles of mutual defection and encourages cooperation.  3.
# **Punish Persistent Defection:**    - If your opponent defects **three times
# in a row**, switch to defection (D) and continue defecting until they
# cooperate again. This punishes consistent defection while allowing for
# recovery if the opponent changes behavior.  4. **Adapt to Opponent’s
# Strategy:**    - If your opponent consistently cooperates for **10 consecutive
# rounds**, switch to always cooperating (C) to maximize mutual payoffs.    - If
# your opponent consistently defects for **10 consecutive rounds**, switch to
# always defecting (D) to avoid being exploited.  5. **Endgame Strategy (Rounds
# 990-1000):**    - In rounds 990-995, continue playing Tit-for-Tat to maintain
# cooperation if possible.    - In rounds 996-1000, defect (D) regardless of
# prior history, as there is no future retaliation to worry about.  This revised
# strategy balances cooperation, retaliation, and forgiveness more effectively,
# while adapting to the opponent’s behavior and avoiding predictable
# exploitation in the endgame.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Endgame strategy: Defect in rounds 996-1000
      if len(self.history) >= 996:
          return axl.Action.D
  
      # Tit-for-Tat with occasional forgiveness
      if len(self.history) > 1:
          # If opponent defected in the last round
          if opponent.history[-1] == axl.Action.D:
              # Check if opponent defected three times in a row
              if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
                  return axl.Action.D  # Punish persistent defection
              return axl.Action.D  # Tit-for-Tat response to defection
          # If opponent cooperated after defecting once, forgive and cooperate
          elif opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.C
  
      # Adapt to opponent's strategy
      if len(opponent.history) >= 10:
          # If opponent cooperated for 10 consecutive rounds, always cooperate
          if opponent.history[-10:] == [axl.Action.C] * 10:
              return axl.Action.C
          # If opponent defected for 10 consecutive rounds, always defect
          elif opponent.history[-10:] == [axl.Action.D] * 10:
              return axl.Action.D
  
      # Default to Tit-for-Tat: play what the opponent played in the last round
      return opponent.history[-1]

# ### Revised Aggressive Strategy for Iterated Normal-Form Game:  1. **Start by
# Defecting (D)** in the first round. This still signals an aggressive stance
# but leaves room for adaptation based on the opponent's response.  2. **In each
# subsequent round, follow this decision rule:**    - If your opponent played
# **C** in the previous round, **switch to C** in the next round to explore
# cooperation. This encourages mutual cooperation early on, which can lead to
# higher payoffs.    - If your opponent played **D** in the previous round,
# **defect (D)** in the next round. This punishes defection but does not lock
# you into a cycle of mutual defection indefinitely.  3. **If mutual cooperation
# (both playing C) is established**:    - Continue cooperating (C) as long as
# the opponent continues to cooperate. This maximizes the 3-point payoff for
# both players.    - If the opponent defects (D) after a period of cooperation,
# **immediately defect (D)** in the next round to signal that defection will not
# be tolerated.  4. **Forgive occasional defections**:    - If the opponent
# defects once after a long period of cooperation, **return to cooperation (C)**
# in the next round to test if the defection was a one-time event. This prevents
# unnecessary cycles of mutual defection and allows for the possibility of re-
# establishing cooperation.  5. **Endgame strategy (final 100 rounds)**:    -
# **Continue cooperating (C)** if mutual cooperation is still in place. Avoid
# predictable defection in the final rounds, as this could lead the opponent to
# defect early, reducing overall payoffs.    - **Switch to defection (D)** only
# in the final 10 rounds (rounds 990–1000) if the opponent has shown a tendency
# to defect in the past. This allows you to exploit the endgame without
# prematurely triggering defection from the opponent.  6. **Adapt to the
# opponent’s behavior**:    - If the opponent consistently defects (D)
# regardless of your actions, **defect (D) in every round** to minimize losses
# (1 point per round).    - If the opponent consistently cooperates (C),
# **continue cooperating (C)** to maximize mutual payoffs.  ### Summary: - Start
# with defection but quickly switch to cooperation if the opponent shows
# willingness to cooperate. - Punish defection but allow for forgiveness to
# avoid unnecessary cycles of mutual defection. - Maintain cooperation as long
# as possible, especially in the endgame, unless the opponent has a history of
# defection. - Adapt to the opponent’s behavior to maximize overall payoffs.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # First round: Start by defecting
      if self.first_round():
          return axl.Action.D
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
  
      # Rule 1: If opponent played C in the previous round, switch to C
      if opponent_last_move == axl.Action.C:
          return axl.Action.C
  
      # Rule 2: If opponent played D in the previous round, defect
      if opponent_last_move == axl.Action.D:
          # Check if mutual cooperation was established before the defection
          if len(self.history) > 1 and self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.C:
              # Forgive occasional defections: return to cooperation after a single defection
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Endgame strategy: Final 100 rounds
      if len(self.history) >= 900:
          # Continue cooperating if mutual cooperation is still in place
          if opponent.history[-100:].count(axl.Action.D) == 0:
              return axl.Action.C
          # Switch to defection in the final 10 rounds if opponent has defected in the past
          if len(self.history) >= 990:
              return axl.Action.D
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# **Revised Strategy:**  1. **Begin by cooperating (play C).**  2. **Continue
# cooperating (play C) as long as both players consistently cooperate (both play
# C).**  3. **If your opponent defects (plays D) at any point:**    - Defect
# (play D) for the next two rounds in response to their defection. This provides
# a stronger punishment to discourage further defection.  4. **After two rounds
# of defection, return to cooperation (play C) if your opponent also returns to
# cooperation (plays C).**  5. **If your opponent defects again after you return
# to cooperation:**    - Defect (play D) for four rounds in response to this
# second defection, doubling the punishment duration.  6. **If your opponent
# defects a third time after you return to cooperation:**    - Switch to
# permanent defection (always play D) for the remainder of the game, as repeated
# defection indicates they are not committed to cooperation.  7. **If your
# opponent consistently cooperates after any punishment phase, continue
# cooperating (play C) to maximize mutual payoffs.**  ---  This revised strategy
# strengthens the punishment for defection, introduces a more gradual escalation
# toward permanent defection, and allows for forgiveness if the opponent returns
# to cooperation.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_rounds = 0  # Tracks how many rounds of punishment are left
          self.defection_count = 0     # Tracks how many times the opponent has defected
          return axl.Action.C          # Start by cooperating
  
      # If in a punishment phase, continue defecting until punishment_rounds is 0
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          self.defection_count += 1  # Increment defection count
  
          # First defection: punish with 2 rounds of defection
          if self.defection_count == 1:
              self.punishment_rounds = 2
          # Second defection: punish with 4 rounds of defection
          elif self.defection_count == 2:
              self.punishment_rounds = 4
          # Third defection: switch to permanent defection
          elif self.defection_count >= 3:
              return axl.Action.D
  
          return axl.Action.D  # Start the punishment phase by defecting
  
      # If opponent cooperates, return to cooperation
      return axl.Action.C

# Revised Strategy:  1. **Start with Cooperation (C):** On the first round, play
# C.  2. **Tit-for-Tat with Delayed Forgiveness:** From the second round onward,
# mirror your opponent’s previous move. If they played C, you play C. If they
# played D, you play D.  3. **Punish Repeated Defection:** If your opponent
# defects (plays D) for two consecutive rounds, continue defecting (D) until
# they cooperate (C) again. Only return to cooperation after they have played C.
# 4. **Forgive After Opponent Cooperates:** Once your opponent returns to
# cooperation (C), forgive their previous defections and play C in the next
# round.  5. **Maintain Cooperation if Opponent is Consistently Cooperative:**
# If your opponent consistently plays C, continue playing C to maximize mutual
# payoffs.  This revised strategy ensures that you punish repeated defection
# more effectively, while still allowing for forgiveness when the opponent
# returns to cooperation. It balances between deterring exploitation and
# maintaining cooperation when possible.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start with cooperation on the first round
      if self.first_round():
          return axl.Action.C
  
      # Check the last two moves of the opponent
      if len(opponent.history) >= 2:
          last_two_moves = opponent.history[-2:]
          # If the opponent defected in the last two rounds, continue defecting
          if last_two_moves == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
  
      # If the opponent cooperated in the last round, forgive and cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Otherwise, mirror the opponent's last move (Tit-for-Tat)
      return opponent.history[-1]

# **Revised Aggressive Strategy for Iterated Normal-Form Game (1000 Rounds)**
# 1. **Start by playing C (Cooperate) in the first round** to test the
# opponent's initial behavior.  2. **If the opponent plays C in the first
# round**, continue playing C for the next 4 rounds to establish mutual
# cooperation and build trust.  3. **If the opponent plays D in the first
# round**, immediately switch to D (Defect) for the next 3 rounds to signal that
# defection will be punished. After 3 rounds of defection, test cooperation
# again by playing C for 1 round:    - **If the opponent responds with C**,
# return to mutual cooperation (play C) for as long as they continue
# cooperating.    - **If the opponent responds with D**, switch back to D and
# continue defecting indefinitely.  4. **After 5 rounds of mutual cooperation**,
# introduce occasional defection to exploit the opponent's trust. Defect once
# every 10 rounds:    - **If the opponent retaliates with D after your
# defection**, return to playing C for 3 rounds to re-establish cooperation.
# - **If the opponent continues to cooperate after your defection**, maintain
# the pattern of defecting once every 10 rounds to maximise your payoff while
# keeping cooperation intact.  5. **If the opponent defects for 3 consecutive
# rounds at any point**, switch to playing D indefinitely, as this signals a
# likely aggressive or uncooperative opponent.  6. **In the final 5 rounds**,
# defect consistently (play D) to secure higher payoffs without concern for
# future retaliation.  7. **If mutual defection occurs for more than 5
# consecutive rounds**, attempt to re-establish cooperation by playing C for 1
# round:    - **If the opponent responds with C**, return to mutual cooperation.
# - **If the opponent responds with D**, revert to playing D for the remainder
# of the game.  This strategy balances aggression with opportunities for
# cooperation, while also allowing for recovery from mutual defection and
# avoiding overly predictable patterns.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if mutual defection occurred for more than 5 rounds
      def mutual_defection_streak():
          return self.history[-5:] == [axl.Action.D] * 5 and opponent.history[-5:] == [axl.Action.D] * 5
  
      # Helper function to check if opponent defected for 3 consecutive rounds
      def opponent_defected_three_consecutive():
          return opponent.history[-3:] == [axl.Action.D] * 3
  
      # First round: play C
      if self.first_round():
          return axl.Action.C
  
      # If opponent played C in the first round, cooperate for the next 4 rounds
      if len(self.history) <= 5 and opponent.history[0] == axl.Action.C:
          return axl.Action.C
  
      # If opponent played D in the first round, defect for 3 rounds, then test cooperation
      if len(self.history) == 2 and opponent.history[0] == axl.Action.D:
          return axl.Action.D
      if len(self.history) == 3 and opponent.history[0] == axl.Action.D:
          return axl.Action.D
      if len(self.history) == 4 and opponent.history[0] == axl.Action.D:
          return axl.Action.D
      if len(self.history) == 5 and opponent.history[0] == axl.Action.D:
          return axl.Action.C
  
      # After testing cooperation, if opponent cooperates, return to mutual cooperation
      if len(self.history) > 5 and opponent.history[0] == axl.Action.D:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # After 5 rounds of mutual cooperation, defect once every 10 rounds
      if len(self.history) > 5 and self.history[-5:].count(axl.Action.C) == 5:
          if len(self.history) % 10 == 0:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent retaliates after defection, return to cooperation for 3 rounds
      if len(self.history) > 5 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # If opponent defects for 3 consecutive rounds, switch to defection indefinitely
      if opponent_defected_three_consecutive():
          return axl.Action.D
  
      # In the final 5 rounds, defect consistently
      if len(self.history) >= 995:
          return axl.Action.D
  
      # If mutual defection occurs for more than 5 consecutive rounds, attempt to re-establish cooperation
      if mutual_defection_streak():
          return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# **Revised Strategy:**  1. **Start by cooperating** (play C) in the first
# round.  2. **Continue cooperating** (play C) as long as your opponent
# cooperates (plays C in the previous round).  3. **If your opponent defects**
# (plays D in the previous round), **immediately defect** (play D) in the next
# round.  4. **Forgive a single defection**: If your opponent cooperates (plays
# C) after defecting once, return to cooperating (play C) on the following
# round.  5. **Handle alternating defections**: If your opponent alternates
# between cooperation and defection (e.g., plays C, then D, then C, etc.),
# respond by defecting (play D) every time they defect, but continue cooperating
# (play C) when they cooperate. Do not escalate to permanent defection unless
# the pattern becomes consistently uncooperative.  6. **Punish sustained
# defections**: If your opponent defects for three consecutive rounds, switch to
# **temporary defection** (play D) for the next three rounds. After this,
# attempt to re-establish cooperation by playing C again. If the opponent
# continues to defect, escalate to permanent defection (play D for the rest of
# the game).  7. **Allow for recovery**: If your opponent shows a clear pattern
# of returning to cooperation after a period of defection, be willing to return
# to cooperation (play C) after a few rounds of mutual defection, but remain
# cautious and ready to defect again if the opponent resumes uncooperative
# behavior.  This revised strategy balances forgiveness with caution, addresses
# alternating defections, and provides a more flexible response to sustained
# uncooperative behavior while still encouraging long-term cooperation.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.temp_defection_count = 0    # Track temporary defection rounds
          return axl.Action.C  # Start by cooperating
  
      # If in temporary defection mode, continue defecting for 3 rounds
      if self.temp_defection_count > 0:
          self.temp_defection_count -= 1
          return axl.Action.D
  
      # Get the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Rule 2: Continue cooperating if the opponent cooperated in the last round
      if last_opponent_move == axl.Action.C:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.C
  
      # Rule 3: If the opponent defects, defect in the next round
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1
  
          # Rule 4: Forgive a single defection if opponent cooperates after defecting once
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D and last_opponent_move == axl.Action.C:
              self.consecutive_defections = 0
              return axl.Action.C
  
          # Rule 6: Punish sustained defections (3 consecutive defections)
          if self.consecutive_defections >= 3:
              self.temp_defection_count = 3  # Defect for the next 3 rounds
              return axl.Action.D
  
          # Rule 5: Handle alternating defections (continue defecting when opponent defects)
          return axl.Action.D

# ### Revised Strategy: **Adaptive Tit-for-Tat with Occasional Testing**  1.
# **First Move: Cooperate**      Always start by choosing **C** (cooperate) in
# the first round.  2. **Reciprocity Rule: Mirror the Opponent's Last Move**
# From round 2 onward, repeat your opponent’s move from the previous round:    -
# If your opponent played **C** in the previous round, play **C**.    - If your
# opponent played **D** in the previous round, play **D**.  3. **Occasional
# Testing: Defect Once Every 100 Rounds**      To test whether your opponent is
# overly cooperative or trying to exploit you, defect (play **D**) once every
# 100 rounds (i.e., in rounds 100, 200, 300, etc.).      This reduces
# predictability and helps gauge whether your opponent will retaliate or
# continue cooperating.  4. **Forgiveness Mechanism: Return to Cooperation After
# Mutual Defection**      If both you and your opponent defect in the same
# round, return to cooperation (play **C**) in the next round to avoid a
# prolonged cycle of defection.  5. **Endgame: Defect in the Final 2 Rounds**
# In rounds 999 and 1000, always defect (play **D**) to maximize your payoff at
# the end of the game, when cooperation is no longer beneficial.  ### Summary -
# Start by cooperating. - Mirror your opponent’s last move unless it’s a
# multiple of 100, at which point you defect to test their behavior. - If both
# players defect, return to cooperation in the next round. - Always defect in
# the last 2 rounds.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First move: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Endgame: Defect in the final 2 rounds
      if round_number >= 999:
          return axl.Action.D
  
      # Occasional Testing: Defect once every 100 rounds
      if round_number % 100 == 0:
          return axl.Action.D
  
      # Forgiveness Mechanism: If both defected last round, return to cooperation
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Reciprocity Rule: Mirror the opponent's last move
      return opponent.history[-1]

# **Revised Aggressive Strategy for Iterated Normal-Form Game (1000 rounds):**
# 1. **Start with Cooperation (C):**      - In Round 1, play C to test the
# opponent's willingness to cooperate. This avoids immediate escalation and
# leaves open the possibility of mutual cooperation for higher long-term
# payoffs.  2. **Defect if Opponent Defects:**      - If the opponent plays D in
# any round, immediately switch to D in the next round to prevent exploitation.
# This signals that defection will be met with defection.  3. **Return to
# Cooperation After One Round of Mutual Defection:**      - If both you and the
# opponent defect in the same round, switch back to C in the next round to test
# if the opponent is willing to cooperate again. This introduces a mechanism for
# forgiveness and avoids getting stuck in a cycle of mutual defection.  4.
# **Punish Consistent Defection:**      - If the opponent defects for **two
# consecutive rounds** after you have returned to cooperation, switch to
# permanent defection (D) for the remainder of the game. This prevents ongoing
# exploitation and ensures you avoid repeated 0-point outcomes.  5. **Alternate
# Defection and Cooperation Only if Opponent Does So First:**      - If the
# opponent alternates between C and D, mirror their behavior by alternating your
# own moves between D and C. This ensures you maintain a balance between
# exploiting their cooperation and avoiding being exploited yourself.  6.
# **Gradually Shift to Defection in the Final 50 Rounds:**      - Starting from
# Round 950, defect every **third round** (e.g., D, C, C, D, C, C, etc.). This
# introduces uncertainty for the opponent and allows you to gain some extra
# points without fully abandoning cooperation too early.      - In the final
# **10 rounds**, defect continuously to maximize your points as the game nears
# its end and cooperation becomes less valuable.  This revised strategy balances
# aggression with opportunities for cooperation, incorporates forgiveness to
# avoid prolonged mutual defection, and introduces a gradual shift to defection
# in the final rounds to maximize late-game payoffs without being too
# predictable.

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
          self.permanent_defection = False  # Track if we are in permanent defection mode
          return axl.Action.C  # Start with cooperation
  
      # If we are in permanent defection mode, always defect
      if self.permanent_defection:
          return axl.Action.D
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Gradually shift to defection in the final 50 rounds
      if round_number >= 950:
          if round_number >= 991:  # Final 10 rounds: defect continuously
              return axl.Action.D
          elif (round_number - 950) % 3 == 0:  # Defect every third round
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent defected in the last round, we defect in this round
      if opponent.history[-1] == axl.Action.D:
          # If both defected in the last round, return to cooperation
          if self.history[-1] == axl.Action.D:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Check for consistent defection by the opponent
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          # If opponent defected for two consecutive rounds, switch to permanent defection
          self.permanent_defection = True
          return axl.Action.D
  
      # If opponent alternates between C and D, mirror their behavior
      if len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]:
          if self.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# ### Revised Strategy: "Adaptive Tit-for-Tat with Flexible Forgiveness"  1.
# **Start with Cooperation**: On the first round, always play C (Cooperate).  2.
# **Mirror the Opponent's Previous Move**: From round 2 onward, play exactly
# what the opponent played in the previous round. If they played C, play C. If
# they played D, play D.  3. **Forgive Occasional Defection**: If the opponent
# defects once, immediately return to cooperation (C) on the next round.
# However, if the opponent defects two or more times consecutively, switch to
# defection (D) until they cooperate again.  4. **Monitor for Persistent
# Defection**: If the opponent defects for 5 consecutive rounds, assume they are
# committed to defection and continue playing D until the end of the game or
# until they cooperate again.  5. **Final 5 Rounds Defection**: For the last 5
# rounds (rounds 996–1000), always play D (Defect). This ensures you maximize
# your score at the end when long-term cooperation no longer benefits you.  ---
# This revised strategy addresses the critiques by introducing more flexibility
# in forgiveness, adapting to both occasional and persistent defection, and
# shortening the final defection window to reduce predictability and maximize
# potential gains.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      FINAL_DEFECT_ROUNDS = 5
      MAX_CONSECUTIVE_DEFECTIONS = 5
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Final 5 rounds: always defect
      if len(self.history) >= 1000 - FINAL_DEFECT_ROUNDS:
          return axl.Action.D
  
      # Count consecutive defections by the opponent
      consecutive_defections = 0
      for move in reversed(opponent.history):
          if move == axl.Action.D:
              consecutive_defections += 1
          else:
              break
  
      # If opponent has defected 5 or more times consecutively, continue defecting
      if consecutive_defections >= MAX_CONSECUTIVE_DEFECTIONS:
          return axl.Action.D
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected two or more times consecutively, defect
          if consecutive_defections >= 2:
              return axl.Action.D
          # Otherwise, forgive and cooperate
          else:
              return axl.Action.C
  
      # Mirror the opponent's last move (if they cooperated, cooperate)
      return opponent.history[-1]

# **Revised Strategy:**  1. **Start with Cooperation (C):** In the first round,
# play C.  2. **Tit-for-Tat with Forgiveness:**    - From the second round
# onward, **mimic** your opponent’s previous move. If they played C, you play C.
# If they played D, you play D.    - **Forgiveness Rule**: If your opponent
# defects (plays D) once, forgive them and play C in the next round. If they
# cooperate after that, continue cooperating (C). If they defect again
# immediately after your forgiveness, switch to playing D until they cooperate
# again.  3. **Revert to Cooperation:** If your opponent switches back to C
# after a series of D moves, return to playing C immediately.  4. **Punish
# Persistent Defection:** If your opponent defects three times in a row without
# cooperating, switch to playing D for five rounds as punishment. After the five
# rounds, return to cooperation (C) to test if they are willing to cooperate
# again.  5. **Adapt to Opponent’s Behavior:** If the opponent continues to
# defect consistently after the punishment phase, switch to always playing D for
# the remainder of the game. If they start cooperating again, return to the tit-
# for-tat with forgiveness approach.  ---  This revised strategy addresses the
# previous issues by clarifying the forgiveness mechanism, ensuring flexibility
# in punishment, and allowing for recovery if the opponent returns to
# cooperation.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.forgave_last_defection = False  # Track if we forgave the last defection
          self.defection_streak = 0            # Track consecutive defections by opponent
          self.punishment_counter = 0          # Track punishment rounds
          return axl.Action.C                  # Start with cooperation
  
      # If in punishment phase, continue defecting for 5 rounds
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # Check opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If opponent cooperated last round, reset defection streak and forgive status
      if last_opponent_move == axl.Action.C:
          self.defection_streak = 0
          self.forgave_last_defection = False
          return axl.Action.C
  
      # If opponent defected last round
      if last_opponent_move == axl.Action.D:
          self.defection_streak += 1
  
          # If we forgave the last defection and they defected again, retaliate with D
          if self.forgave_last_defection:
              self.forgave_last_defection = False
              return axl.Action.D
  
          # If this is the first defection, forgive and play C
          if self.defection_streak == 1:
              self.forgave_last_defection = True
              return axl.Action.C
  
          # If opponent defected 3 times in a row, enter punishment phase
          if self.defection_streak >= 3:
              self.punishment_counter = 5  # Punish for 5 rounds
              return axl.Action.D
  
          # Otherwise, mimic the opponent's defection
          return axl.Action.D

# ### Revised Strategy: "Adaptive Aggression with Conditional Cooperation"  1.
# **Round 1 (Opening Move)**: Play **C**.      Start cooperatively to test the
# opponent’s behavior and avoid provoking immediate retaliation.  2. **Rounds
# 2-5 (Exploration Phase)**:      - If the opponent played **C** in the previous
# round, continue playing **C** to encourage mutual cooperation.    - If the
# opponent played **D** in the previous round, immediately switch to **D** for
# the next round to signal that defection will be punished.    - After punishing
# with **D**, return to **C** to test if the opponent is willing to cooperate
# again.  3. **Rounds 6-20 (Conditional Cooperation Phase)**:      - If the
# opponent consistently plays **C**, continue playing **C** to maximize mutual
# payoffs.    - If the opponent defects more than once during this phase, switch
# to **D** for 2 rounds as a punishment, then return to **C** to test for
# cooperation again.    - If the opponent continues to defect after the 2-round
# punishment, switch to **D** permanently until they show signs of cooperation.
# 4. **Rounds 21-990 (Long-Term Adaptation)**:      - If the opponent has shown
# consistent cooperation (playing **C** for at least 5 consecutive rounds),
# maintain cooperation by playing **C** in every round.    - If the opponent
# defects after a long period of cooperation, respond with **D** for 2 rounds,
# then return to **C** to test if cooperation can be restored.    - If the
# opponent defects repeatedly (more than 3 times in 10 rounds), switch to **D**
# permanently to avoid further exploitation.  5. **Endgame (Last 10 Rounds)**:
# - In the final 10 rounds, continue playing **C** if the opponent has been
# cooperative throughout the game.    - If the opponent has defected recently or
# if you suspect they will defect in the endgame, switch to **D** in the last 3
# rounds to maximize your payoff without risking future retaliation.  ---  ###
# Key Improvements: - **Cooperative Opening**: Starting with **C** avoids
# unnecessary provocation and encourages mutual cooperation from the outset. -
# **Balanced Punishment**: Punishments are shorter (2 rounds) and more measured,
# reducing the risk of escalating conflict while still discouraging defection. -
# **Flexibility**: The strategy adapts to different opponent behaviors, allowing
# for cooperation with cooperative opponents and defection against consistently
# uncooperative ones. - **Endgame Caution**: Defection is reserved for the final
# 3 rounds, reducing predictability and allowing for more cooperation in the
# late game if the opponent remains trustworthy.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Round 1: Play C
      if self.first_round():
          return axl.Action.C
  
      # Helper function to count defections in the last N rounds
      def count_defections_in_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D)
  
      # Helper function to check if opponent has cooperated for the last N rounds
      def opponent_cooperated_last_n_rounds(n):
          return all(move == axl.Action.C for move in opponent.history[-n:])
  
      # Exploration Phase (Rounds 2-5)
      if len(self.history) <= 5:
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D  # Punish defection
          else:
              return axl.Action.C  # Continue cooperation
  
      # Conditional Cooperation Phase (Rounds 6-20)
      if 6 <= len(self.history) <= 20:
          if count_defections_in_last_n_rounds(15) > 1:
              if len(self.history) % 2 == 0:  # Punish for 2 rounds
                  return axl.Action.D
              else:
                  return axl.Action.C  # Test for cooperation after punishment
          else:
              return axl.Action.C  # Continue cooperation if opponent is mostly cooperative
  
      # Long-Term Adaptation (Rounds 21-990)
      if 21 <= len(self.history) <= 990:
          if opponent_cooperated_last_n_rounds(5):
              return axl.Action.C  # Maintain cooperation if opponent is consistently cooperative
          elif count_defections_in_last_n_rounds(10) > 3:
              return axl.Action.D  # Defect permanently if opponent defects too often
          elif opponent.history[-1] == axl.Action.D:
              if len(self.history) % 2 == 0:  # Punish for 2 rounds
                  return axl.Action.D
              else:
                  return axl.Action.C  # Test for cooperation after punishment
          else:
              return axl.Action.C  # Continue cooperation
  
      # Endgame (Last 10 Rounds)
      if len(self.history) > 990:
          if opponent_cooperated_last_n_rounds(10):
              return axl.Action.C  # Continue cooperation if opponent has been cooperative
          elif len(self.history) >= 997:
              return axl.Action.D  # Defect in the last 3 rounds if opponent is untrustworthy
          else:
              return axl.Action.C  # Otherwise, continue cooperation

# ### Revised Cooperative Strategy: "Adaptive Tit-for-Tat with Flexible
# Forgiveness"  1. **Start with Cooperation (C):** In the first round, always
# play C to signal a willingness to cooperate.  2. **Reciprocate the Opponent's
# Previous Move:**    - If your opponent played C in the previous round, play C
# in the current round.    - If your opponent played D in the previous round,
# play D in the current round.  3. **Forgive Occasional Defections Quickly:**
# - If your opponent defects (plays D) once, immediately return to playing C in
# the next round. This allows for mistakes or strategic testing by the opponent
# without triggering a prolonged defection cycle.    - However, if the opponent
# defects again within the next 3 rounds after being forgiven, switch to playing
# D until they return to cooperation (play C).  4. **Punish Consistent Defection
# with Gradual Retaliation:**    - If your opponent defects for 2 or more
# consecutive rounds, play D in response. Continue playing D until they return
# to cooperation (play C).    - Once they play C, return to C in the next round
# to re-establish cooperation, but be more cautious. If they defect again within
# 5 rounds, switch to a more sustained defection (D) for 3 rounds before
# attempting cooperation again.  5. **Adapt to Mixed Strategies:**    - If the
# opponent alternates between C and D unpredictably (e.g., playing D more than
# 30% of the time over any 20-round period), switch to a "Grim Trigger"
# approach: play D for the remainder of the game to avoid being exploited.  6.
# **Endgame Caution (Final 10 Rounds):**    - In the last 10 rounds, continue to
# reciprocate the opponent's moves (C for C, D for D) rather than
# unconditionally cooperating. This prevents exploitation in the final rounds
# while still allowing for cooperation if the opponent remains cooperative.
# This revised strategy addresses the critiques by introducing quicker
# forgiveness, clearer handling of early defections, and a more cautious
# approach to the endgame. It also includes a mechanism to adapt to opponents
# who use mixed or unpredictable strategies.

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
          self.forgiveness_counter = 0  # Tracks how many rounds since last forgiveness
          self.defection_streak = 0     # Tracks consecutive defections by opponent
          self.cautious_mode = False    # Tracks if we are in cautious mode after opponent defects again
          return axl.Action.C           # Start with cooperation
  
      # Helper function to check if opponent is alternating unpredictably
      def is_mixed_strategy():
          if len(opponent.history) >= 20:
              recent_defections = opponent.history[-20:].count(axl.Action.D)
              return recent_defections / 20 > 0.30
          return False
  
      # Endgame caution: last 10 rounds
      if len(self.history) >= 990:
          return opponent.history[-1]  # Reciprocate opponent's last move
  
      # Check for mixed strategy (opponent defecting more than 30% in last 20 rounds)
      if is_mixed_strategy():
          return axl.Action.D  # Switch to Grim Trigger (defect forever)
  
      # Reciprocate opponent's last move
      if opponent.history[-1] == axl.Action.C:
          self.defection_streak = 0  # Reset defection streak on cooperation
          self.forgiveness_counter = 0  # Reset forgiveness counter
          return axl.Action.C
  
      # If opponent defected last round
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
  
          # Forgive a single defection immediately
          if self.defection_streak == 1:
              self.forgiveness_counter = 1  # Start forgiveness counter
              return axl.Action.C
  
          # If opponent defects again within 3 rounds after forgiveness
          if self.forgiveness_counter > 0 and self.forgiveness_counter <= 3:
              self.forgiveness_counter += 1
              return axl.Action.D  # Defect until opponent cooperates
  
          # Punish consistent defection (2 or more consecutive defections)
          if self.defection_streak >= 2:
              if opponent.history[-1] == axl.Action.C:
                  self.defection_streak = 0  # Reset defection streak on cooperation
                  return axl.Action.C  # Return to cooperation
              return axl.Action.D  # Continue defecting until opponent cooperates
  
          # If opponent defects again within 5 rounds after cooperation
          if self.cautious_mode and len(self.history) >= 5:
              if opponent.history[-5:].count(axl.Action.D) > 0:
                  return axl.Action.D  # Defect for 3 rounds before attempting cooperation again
  
      return axl.Action.C  # Default to cooperation if no other conditions are met

# 1. **Start with Cooperation**: In the first round, play **C** (Cooperate).  2.
# **Tit-for-Tat with Immediate Retaliation**:    - In each subsequent round,
# repeat your opponent's previous move.    - If your opponent defects (plays
# **D**) in any round, immediately retaliate by playing **D** in the next round.
# - If your opponent returns to cooperation (plays **C**) after your
# retaliation, forgive them by returning to **C** in the following round.  3.
# **Switch to Permanent Defection Against Unconditional Defectors**:    - If
# your opponent defects for **5 consecutive rounds**, assume they are an
# unconditional defector and switch to permanent defection (**D**) for the
# remainder of the game.  4. **Endgame Defection Adjustment**:    - In the final
# **3 rounds** (rounds 998-1000), always play **D** (Defect), regardless of your
# opponent's actions. This reduces the risk of losing out on potential points
# while still allowing for cooperation in most of the game.  This revised
# strategy addresses the vulnerability to early exploitation, provides quicker
# retaliation, adjusts the timing of endgame defection, and includes a mechanism
# to handle opponents who always defect.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation
      if self.first_round():
          return axl.Action.C
  
      # Endgame defection adjustment: defect in the last 3 rounds
      if len(self.history) >= 998:
          return axl.Action.D
  
      # Check if opponent has defected for 5 consecutive rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.D
  
      # Tit-for-Tat with immediate retaliation and forgiveness
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C

# ### Revised Aggressive Strategy for Iterated Normal-Form Game (1000 Rounds)
# 1. **Initial Move**: Start by playing **D** in the first round. This sets an
# aggressive tone and tests your opponent's response.  2. **Response to
# Opponent's Move**:    - **If the opponent plays C**: In the next round, play
# **C** to test for potential cooperation. If the opponent continues to play C,
# maintain mutual cooperation (both playing C) to maximize long-term payoffs (3
# points each).    - **If the opponent plays D**: Continue playing **D**. Mutual
# defection yields 1 point for both, which is better than risking 0 points by
# cooperating while they defect.  3. **Retaliation and Forgiveness**:    - **If
# the opponent defects (plays D) after a period of mutual cooperation**:
# Immediately switch to **D** in the next round to punish the defection.    -
# **After one round of mutual defection**, return to **C** to offer a chance for
# the opponent to re-establish cooperation. If the opponent responds with **C**,
# resume cooperation. If they defect again, continue playing **D** for several
# rounds (e.g., 5 rounds) before testing cooperation again.  4. **Endgame**:
# - In the final 10 rounds, **gradually shift to defection**. Start defecting in
# the last 3 rounds to avoid being exploited at the end, but maintain
# cooperation as long as possible before that to maximize points.  ### Summary:
# - **Start aggressively** with defection but be open to cooperation if the
# opponent signals willingness. - **Punish defection** but offer opportunities
# for the opponent to return to cooperation. - **Adapt to the opponent's
# behavior** by balancing aggression with forgiveness. - **Defect
# strategically** in the final rounds to avoid exploitation.

class Aggressive_17(LLM_Strategy):
  n = 17
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
      FINAL_DEFECT_ROUNDS = 3
      RETALIATION_PERIOD = 5
  
      # First move: Always start with D
      if self.first_round():
          return DEFECT
  
      # Endgame strategy: Defect in the last 3 rounds
      if len(self.history) >= 1000 - FINAL_DEFECT_ROUNDS:
          return DEFECT
  
      # Endgame preparation: Gradually shift to defection in the last 10 rounds
      if len(self.history) >= 1000 - ENDGAME_THRESHOLD:
          return DEFECT if self._random.random_choice(0.5) else COOPERATE
  
      # If opponent played C in the last round, cooperate
      if opponent.history[-1] == COOPERATE:
          return COOPERATE
  
      # If opponent played D in the last round, defect
      if opponent.history[-1] == DEFECT:
          # Check if we are in a retaliation period (after mutual defection)
          if len(self.history) > 1 and self.history[-1] == DEFECT and opponent.history[-1] == DEFECT:
              # After one round of mutual defection, offer cooperation
              if self.history[-2] == COOPERATE and opponent.history[-2] == COOPERATE:
                  return COOPERATE
              # Continue defecting for RETALIATION_PERIOD rounds after repeated defection
              if self.history[-RETALIATION_PERIOD:].count(DEFECT) == RETALIATION_PERIOD:
                  return COOPERATE
          return DEFECT

# **Revised Cooperative Strategy for 1000-Round Iterated Game**  1. **Start by
# Cooperating**: In the first round, play C (Cooperate).  2. **Tit-for-Tat with
# Leniency**: From the second round onward, generally repeat your opponent’s
# previous move:    - If your opponent played C in the previous round, play C.
# - If your opponent played D in the previous round, play C once to test if it
# was a one-time defection. If they cooperate in the next round, continue
# cooperating. If they defect again, switch to defection.  3. **Forgive
# Occasional Defections**: If your opponent defects (plays D) but then returns
# to cooperation (plays C in the next round), forgive them by playing C again.
# This allows for occasional mistakes or tests without falling into a defection
# cycle.  4. **Monitor for Consistent Defection**: If the opponent defects for
# two consecutive rounds, assume they are committed to defection. In this case,
# switch to defection (D) and continue defecting until they show a clear pattern
# of cooperation (at least two consecutive C moves).  5. **Endgame
# Consideration**: In the final 10 rounds, defect (play D) regardless of the
# opponent’s actions. This prevents exploitation in the endgame when there is no
# future retaliation.  6. **Adapt to Opponent’s Strategy**: If the opponent
# shows a clear pattern of cooperation over many rounds (e.g., 10 consecutive C
# moves), continue cooperating even after a single defection, as this may
# indicate a cooperative strategy with occasional noise. Conversely, if the
# opponent frequently alternates between C and D, be more cautious and defect
# more readily.  This revised strategy balances cooperation with protection
# against exploitation, while also considering the finite nature of the game and
# the need for flexibility in response to the opponent’s behavior.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      ENDGAME_THRESHOLD = 10
      COOPERATION_THRESHOLD = 10
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Endgame strategy: Defect in the last 10 rounds
      if len(self.history) >= 1000 - ENDGAME_THRESHOLD:
          return axl.Action.D
  
      # Tit-for-Tat with leniency
      if len(self.history) > 1:
          # Check if opponent defected in the last two rounds
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D  # Consistent defection, switch to defection
  
      # If opponent defected last round, test with cooperation
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Adapt to opponent's strategy: If opponent has cooperated for 10 consecutive rounds, be lenient
      if opponent.history[-COOPERATION_THRESHOLD:].count(axl.Action.C) == COOPERATION_THRESHOLD:
          return axl.Action.C
  
      # Default Tit-for-Tat: Repeat opponent's last move
      return opponent.history[-1]

# **Revised Strategy:**  1. **Start by cooperating (play C) in the first
# round.**  2. **Tit-for-Tat with adaptive forgiveness**:      From the second
# round onwards, repeat your opponent’s previous move, but apply the following
# adjustments:     a. **If your opponent defects (plays D) once, defect (play D)
# in the next round.**          b. **If your opponent defects twice
# consecutively, defect in the next round, but return to cooperation (play C) if
# they cooperate in the following round.**          c. **If your opponent
# defects three or more times consecutively, continue defecting (play D) until
# they cooperate for two consecutive rounds. Once they cooperate twice in a row,
# return to cooperation (play C).**  3. **Handle alternating behavior**:      If
# your opponent alternates between cooperation and defection (e.g., CDCD
# pattern), switch to defecting (play D) consistently until they cooperate for
# two consecutive rounds. Then, return to cooperation (play C).  4. **Occasional
# forgiveness**:      Every 50 rounds, even if your opponent is consistently
# defecting, play C once to test if they will switch to cooperation. If they
# cooperate in response, resume cooperation (play C) in subsequent rounds. If
# they defect, return to defecting (play D) until the next forgiveness test.  5.
# **Endgame caution**:      In the last 50 rounds, be more cautious about
# cooperation. If your opponent has defected more than 50% of the time
# throughout the game, defect (play D) consistently in the final 10 rounds to
# avoid late-game exploitation. If they have cooperated more than 50% of the
# time, continue with the Tit-for-Tat approach.  6. **Adapt to random or
# unpredictable behavior**:      If your opponent’s behavior appears random or
# unpredictable (e.g., no clear pattern of cooperation or defection), switch to
# a probabilistic approach:      - Cooperate (play C) with a 70% probability and
# defect (play D) with a 30% probability.      - Reassess every 100 rounds to
# determine if a clearer pattern has emerged, and adjust back to Tit-for-Tat if
# necessary.  This revised strategy incorporates more frequent forgiveness,
# handles alternating behavior, and introduces caution in the endgame while
# adapting to random opponents.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.alternating_behavior = False
          self.last_move = None
          return axl.Action.C  # Start by cooperating
      
      # Helper function to detect alternating behavior
      def is_alternating():
          if len(opponent.history) < 4:
              return False
          return opponent.history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]
      
      # Helper function to check if opponent cooperated twice consecutively
      def cooperated_twice():
          return len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]
      
      # Helper function to check if opponent defected more than 50% of the time
      def opponent_defected_more_than_half():
          return opponent.history.defections > len(opponent.history) / 2
      
      # Handle alternating behavior
      if is_alternating():
          self.alternating_behavior = True
      
      if self.alternating_behavior:
          if cooperated_twice():
              self.alternating_behavior = False
              return axl.Action.C
          return axl.Action.D
      
      # Tit-for-Tat with adaptive forgiveness
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
      
      if self.consecutive_defections == 1:
          return axl.Action.D
      elif self.consecutive_defections == 2:
          return axl.Action.D if opponent.history[-1] == axl.Action.D else axl.Action.C
      elif self.consecutive_defections >= 3:
          if cooperated_twice():
              self.consecutive_defections = 0
              return axl.Action.C
          return axl.Action.D
      
      # Occasional forgiveness every 50 rounds
      if len(self.history) % 50 == 0:
          return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
      
      # Endgame caution in the last 50 rounds
      if len(self.history) >= 950:
          if opponent_defected_more_than_half():
              if len(self.history) >= 990:
                  return axl.Action.D
          return axl.Action.C
      
      # Adapt to random or unpredictable behavior
      if len(self.history) >= 100 and self.consecutive_defections == 0:
          if self._random.random_choice(0.7):
              return axl.Action.C
          return axl.Action.D
      
      # Default Tit-for-Tat behavior
      return opponent.history[-1]

# 1. **Start with Cooperation (C)**: Begin the game by playing Cooperate (C) in
# the first round to test the opponent’s willingness to cooperate and avoid
# locking into mutual defection early.  2. **Tit-for-Tat with Forgiveness**:
# After the first round, adopt a tit-for-tat approach:    - If the opponent
# cooperates (C), continue cooperating (C) in the next round.    - If the
# opponent defects (D), defect (D) in the next round to punish them.  3.
# **Forgive After One Defection**: If the opponent defects only once and then
# returns to cooperation (C) in the following round, forgive them by returning
# to cooperation (C) as well. This prevents getting stuck in a cycle of mutual
# defection.  4. **Escalate Punishment for Repeated Defection**: If the opponent
# defects twice in a row, escalate the punishment by defecting (D) for the next
# three rounds. After this, return to tit-for-tat behavior, but remain cautious.
# 5. **Re-evaluate After 100 Rounds**: After 100 rounds, assess the opponent’s
# behavior:    - If the opponent has been mostly cooperative, continue with tit-
# for-tat.    - If the opponent has been mostly defecting, switch to consistent
# defection (D) to avoid further exploitation.  6. **Final 50 Rounds Strategy**:
# In the last 50 rounds, gradually shift towards defection:    - Start defecting
# (D) in the final 10 rounds regardless of the opponent’s actions to secure
# higher individual payoffs.    - Before the final 10 rounds, continue tit-for-
# tat but be more inclined to defect if the opponent shows any signs of
# defection.  This revised strategy balances cooperation and punishment, adapts
# to the opponent’s behavior, and avoids getting stuck in mutual defection while
# still securing higher payoffs in the final rounds.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_streak = 0  # Track consecutive defections by the opponent
          self.escalation_counter = 0  # Track how many rounds of punishment are left
          return axl.Action.C  # Start with cooperation
  
      # Final 50 rounds strategy
      if len(self.history) >= 950:
          if len(self.history) >= 990:
              return axl.Action.D  # Defect in the final 10 rounds
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D  # Be more inclined to defect if opponent defects
          return axl.Action.C  # Otherwise, continue cooperating
  
      # Re-evaluate after 100 rounds
      if len(self.history) == 100:
          if opponent.history.cooperations > opponent.history.defections:
              self.is_mostly_cooperative = True  # Opponent is mostly cooperative
          else:
              self.is_mostly_cooperative = False  # Opponent is mostly defecting
  
      if len(self.history) > 100 and not self.is_mostly_cooperative:
          return axl.Action.D  # Switch to consistent defection if opponent mostly defects
  
      # Escalate punishment for repeated defection
      if self.escalation_counter > 0:
          self.escalation_counter -= 1
          return axl.Action.D  # Continue defecting during punishment phase
  
      # Tit-for-tat with forgiveness
      if opponent.history[-1] == axl.Action.D:
          if self.defection_streak == 1:
              self.escalation_counter = 3  # Escalate punishment after two consecutive defections
              return axl.Action.D
          self.defection_streak += 1  # Track consecutive defections
          return axl.Action.D  # Tit-for-tat: defect in response to opponent's defection
      else:
          if self.defection_streak == 1:
              self.defection_streak = 0  # Forgive after one defection if opponent cooperates
          return axl.Action.C  # Tit-for-tat: cooperate in response to opponent's cooperation

# **Revised Strategy: "Adaptive Tit-for-Tat with Randomized Forgiveness"**  1.
# **Start by cooperating (play C) in the first round.**     2. **For each
# subsequent round, follow these rules:**    - If your opponent cooperated
# (played C) in the previous round, continue cooperating (play C).    - If your
# opponent defected (played D) in the previous round, retaliate by defecting
# (play D) in the next round.     3. **Introduce a small, random chance of
# forgiveness after a defection**: After retaliating once for a defection, in
# subsequent rounds, cooperate (play C) with a 10-20% probability, even if the
# opponent continues to defect. This prevents the opponent from predicting when
# you will forgive and encourages them to return to cooperation.  4. **Monitor
# patterns of defection**: If the opponent defects consistently for more than 3
# consecutive rounds, switch to permanent defection (play D) to avoid being
# exploited.  5. **In the final 5 rounds, defect (play D) only if the opponent
# has defected in the previous round**: This allows you to maintain cooperation
# as long as possible while still protecting against late-game exploitation.
# This revised strategy addresses the previous issues by introducing
# unpredictability in forgiveness, avoiding rigid patterns, and allowing for
# more nuanced responses to defections. It also reduces the risk of mutual
# defection in the final rounds while still protecting against exploitation.

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
  
      # Check if we are in the final 5 rounds
      if len(self.history) >= 995:
          # Defect only if the opponent defected in the previous round
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the previous round, retaliate by defecting
      if opponent.history[-1] == axl.Action.D:
          # Check if the opponent has defected for more than 3 consecutive rounds
          if opponent.history[-3:].count(axl.Action.D) == 3:
              # Switch to permanent defection
              return axl.Action.D
  
          # After retaliating once, introduce a small chance of forgiveness
          if len(self.history) > 1 and self.history[-1] == axl.Action.D:
              # Cooperate with a 10-20% probability
              if self._random.random_choice(0.15):
                  return axl.Action.C
  
          # Otherwise, defect
          return axl.Action.D

# ### Revised Strategy: Conditional Cooperation with Escalating Retaliation  1.
# **Start with Cooperation (C):** In the first round, play C (cooperate) to
# establish mutual trust and signal a willingness to collaborate.  2. **Continue
# Cooperation if Reciprocated:** If your opponent also plays C in the previous
# round, continue playing C. This maximizes collective payoffs when both players
# are cooperating.  3. **Defect (D) if Betrayed:** If your opponent plays D
# (defects) in any round, retaliate by playing D in the next round. This
# discourages exploitation by ensuring that defection is punished.  4.
# **Escalate Retaliation for Consecutive Defections:** If your opponent defects
# again after your retaliation (i.e., they defect two or more times in a row),
# continue playing D for an increasing number of rounds. For each additional
# consecutive defection by the opponent, extend your retaliation by one more
# round (e.g., defect for two rounds after two consecutive defections, three
# rounds after three consecutive defections, etc.). This escalates the
# punishment for persistent betrayal.  5. **Return to Cooperation After
# Retaliation Ends:** Once the opponent returns to cooperation (C), reset the
# retaliation cycle and return to playing C in the next round. This signals a
# willingness to forgive and re-establish cooperation, but only after the
# opponent has shown a willingness to cooperate again.  6. **Maintain
# Cooperation if Opponent Stops Defecting:** If the opponent stops defecting and
# plays C consistently, continue playing C to maximize mutual payoffs.  This
# revised strategy addresses the previous issues by introducing escalating
# retaliation for repeated defections, making it harder for the opponent to
# exploit the strategy while still allowing for forgiveness and the possibility
# of returning to cooperation.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.retaliation_count = 0  # Tracks how many rounds to retaliate
          return axl.Action.C  # Start with cooperation
  
      # If currently retaliating, continue defecting
      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # Check if opponent defected consecutively
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              # Escalate retaliation: increase the number of D rounds
              self.retaliation_count += 1
          return axl.Action.D  # Retaliate with a D
  
      # If opponent cooperated in the last round, return to cooperation
      return axl.Action.C

# 1. **Start with cooperation (C)** in the first round to encourage mutual
# cooperation and avoid provoking immediate retaliation.  2. **Continue
# cooperating (C)** as long as your opponent also cooperates (C). This ensures
# both players benefit from the maximum mutual payoff of 3.  3. **If your
# opponent defects (plays D)**, immediately defect (D) in the next round to
# signal that defection will not be tolerated.  4. **After one round of
# defection**, if your opponent returns to cooperation (C), forgive them and
# switch back to cooperation (C) to restore mutual benefit.  5. **If your
# opponent defects repeatedly (more than twice in a row)**, continue defecting
# (D) indefinitely to prevent further exploitation.  6. **In the final 5
# rounds**, defect (D) only if your opponent has defected recently (within the
# last 5 rounds). Otherwise, continue cooperating (C) to maintain mutual benefit
# until the end.  This revised strategy balances aggression with the potential
# for cooperation, punishes repeated defections, and avoids predictable endgame
# defection.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # If it's the first round, cooperate
      if self.first_round():
          return axl.Action.C
  
      # Check if we are in the final 5 rounds
      if len(self.history) >= 995:
          # Defect if opponent has defected in the last 5 rounds
          if opponent.history[-5:].count(axl.Action.D) > 0:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent defected in the last round, defect this round
      if opponent.history[-1] == axl.Action.D:
          # If opponent has defected more than twice in a row, continue defecting
          if opponent.history[-2:].count(axl.Action.D) == 2:
              return axl.Action.D
          return axl.Action.D
  
      # If opponent cooperated in the last round, cooperate
      return axl.Action.C

# ### Revised Strategy: **Tit-for-Tat with Adaptive Forgiveness**  **1. Start
# with Cooperation:**   - In the first round, always play **C** (Cooperate).
# **2. Mirror the Opponent’s Last Move:**   - From the second round onward, copy
# your opponent’s previous move. If they played **C** in the last round, play
# **C**; if they played **D**, play **D**.  **3. Forgive After a Single
# Defection:**   - If the opponent defects once, immediately return to **C** in
# the next round to offer a chance to re-establish cooperation. This prevents
# prolonged retaliation cycles.  **4. Escalate Defection Only if Opponent
# Defects Twice in a Row:**   - If the opponent defects two times in a row,
# switch to **D** and continue defecting until the opponent plays **C** again.
# This signals that repeated defection will not be tolerated.  **5. Forgive
# After Mutual Defection:**   - If both players defect in the same round, return
# to **C** in the next round to attempt to break the cycle of mutual defection.
# This helps avoid long-term low payoffs.  **6. Final 10 Rounds - Maintain
# Cooperation Unless Provoked:**   - In the last 10 rounds, continue to play
# **C** unless the opponent defects. If the opponent defects at any point during
# these rounds, switch to **D** for the remainder of the game to prevent
# exploitation.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Check if it's the first round
      if self.first_round():
          return axl.Action.C  # Start with cooperation
      
      # Get the number of rounds played so far
      rounds_played = len(self.history)
      
      # Final 10 rounds logic
      if rounds_played >= 990:
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D  # Defect if opponent defects in the final 10 rounds
          else:
              return axl.Action.C  # Otherwise, cooperate in the final 10 rounds
      
      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C  # Cooperate if opponent cooperated last round
      
      # If opponent defected last round
      if opponent.history[-1] == axl.Action.D:
          
          # Check if opponent defected two times in a row
          if rounds_played > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D  # Escalate defection if opponent defected twice in a row
          
          # Forgive after a single defection
          return axl.Action.C  # Cooperate after a single defection
      
      # Default to cooperation if no other condition is met
      return axl.Action.C

# **Revised Neutral Iterated Strategy:**  1. **Start by cooperating (C) in the
# first round.**  2. **Tit-for-Tat with occasional leniency:**    - From round 2
# onwards, mirror your opponent's last move:      - If your opponent played C in
# the previous round, play C.      - If your opponent played D in the previous
# round, play D.    - However, if your opponent defects (D) twice in a row, play
# C once to test for potential cooperation. If they continue defecting, switch
# to defection (D) until they cooperate again.  3. **Adaptive forgiveness:**
# - Instead of forgiving on a fixed schedule, forgive (play C) after every 5
# consecutive rounds of mutual defection (D vs. D) to test if the opponent is
# willing to return to cooperation.  4. **Endgame caution:**    - In the final
# 50 rounds, continue mirroring the opponent's last move but avoid automatic
# defection. Only defect if the opponent defects first, maintaining the
# possibility of cooperation until the very end.  This revised strategy
# addresses the critiques by reducing predictability, encouraging sustained
# cooperation, and avoiding premature defection in the endgame. It also
# introduces a more adaptive forgiveness mechanism to rebuild trust when
# necessary.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive mutual defections
          return axl.Action.C  # Start by cooperating
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
      
      # Check if we are in the final 50 rounds
      final_50_rounds = len(self.history) >= 950
  
      # Tit-for-Tat with occasional leniency
      if len(self.history) > 1:
          # Check if opponent defected twice in a row
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.C  # Play C once to test for cooperation
  
      # Adaptive forgiveness: Forgive after 5 consecutive mutual defections
      if len(self.history) >= 5:
          last_5_rounds = list(zip(self.history[-5:], opponent.history[-5:]))
          if all(my_move == axl.Action.D and opp_move == axl.Action.D for my_move, opp_move in last_5_rounds):
              return axl.Action.C  # Forgive after 5 rounds of mutual defection
  
      # Endgame caution: In the final 50 rounds, only defect if opponent defects first
      if final_50_rounds:
          if opponent_last_move == axl.Action.D:
              return axl.Action.D  # Defect if opponent defects
          else:
              return axl.Action.C  # Cooperate otherwise
  
      # Default Tit-for-Tat behavior: Mirror opponent's last move
      return opponent_last_move

# **Revised Aggressive Strategy for Iterated Normal-Form Game:**  1. **Start by
# playing D (Defect).**      Begin the game aggressively to avoid being
# exploited early and to test the opponent's response.  2. **Continue playing D
# as long as the opponent plays C (Cooperate).**      Maximise your score by
# defecting while the opponent cooperates, taking advantage of their
# cooperation.  3. **If the opponent plays D, continue playing D for the next 3
# rounds.**      Punish the opponent for defecting by defecting for multiple
# rounds to discourage further defection. This ensures you maintain an
# aggressive stance and avoid being exploited.  4. **After 3 rounds of mutual
# defection, switch to C (Cooperate) to test for a cooperative response.**
# After punishing the opponent, offer a chance to return to mutual cooperation.
# This balances aggression with the potential for higher long-term payoffs
# through cooperation.  5. **If the opponent responds with C, continue playing
# C.**      If the opponent reciprocates your cooperative gesture, maintain
# cooperation to benefit from the mutual score of 3.  6. **If the opponent
# defects again after your C, return to D and defect for the remainder of the
# game.**      If the opponent defects after you attempt cooperation, switch
# back to defection and stay there permanently to avoid further exploitation.
# 7. **In the final 20 rounds, always play D regardless of the opponent’s
# actions.**      In the last 20 rounds, defect consistently to secure higher
# payoffs, as the game is nearing its end and the risk of retaliation is
# minimal.  This revised strategy maintains an aggressive approach while
# incorporating a more structured punishment and testing mechanism, reducing the
# risk of exploitation and adapting to the opponent's behavior.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      DEFECT = axl.Action.D
      COOPERATE = axl.Action.C
      FINAL_ROUNDS = 20
      PUNISHMENT_ROUNDS = 3
      TOTAL_ROUNDS = 1000
  
      # If it's the first round, start by playing D
      if self.first_round():
          return DEFECT
  
      # If we are in the final 20 rounds, always play D
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return DEFECT
  
      # If the opponent has defected in the last round
      if opponent.history[-1] == DEFECT:
          # If we have been defecting for less than 3 rounds after opponent's defection, continue defecting
          if len(self.history) < PUNISHMENT_ROUNDS or self.history[-PUNISHMENT_ROUNDS:].count(DEFECT) < PUNISHMENT_ROUNDS:
              return DEFECT
          # After 3 rounds of mutual defection, switch to C to test for cooperation
          elif self.history[-PUNISHMENT_ROUNDS:].count(DEFECT) == PUNISHMENT_ROUNDS:
              return COOPERATE
  
      # If the opponent cooperates after we switch to C, continue cooperating
      if self.history[-1] == COOPERATE and opponent.history[-1] == COOPERATE:
          return COOPERATE
  
      # If the opponent defects after we switch to C, defect for the rest of the game
      if self.history[-1] == COOPERATE and opponent.history[-1] == DEFECT:
          return DEFECT
  
      # If the opponent has been cooperating, continue defecting
      if opponent.history[-1] == COOPERATE:
          return DEFECT

# ### Revised Strategy: **Tit-for-Tat with Gradual Retaliation**  - **Start by
# cooperating (C) in the first round.**  - **On each subsequent round:**   - If
# your opponent cooperated (C) in the previous round, continue cooperating (C).
# - If your opponent defected (D) in the previous round, defect (D) in the next
# round as punishment.  - **Forgiveness mechanism**:   - If your opponent
# cooperates (C) after a defection, return to cooperation (C) immediately to
# encourage mutual cooperation.    - **Gradual retaliation for repeated
# defections**:   - If your opponent defects (D) for **two consecutive rounds**,
# defect (D) for **two rounds** in response.   - If your opponent defects (D)
# for **three consecutive rounds**, defect (D) for **three rounds** in response.
# - Continue increasing the length of your defections by one round for each
# additional consecutive defection by your opponent (e.g., four defections lead
# to four rounds of defection, and so on).  - **Permanent defection threshold**:
# - If your opponent defects (D) for **five consecutive rounds**, switch to
# permanent defection (D) for the rest of the game to avoid continuous
# exploitation.  ### Summary: - Begin by cooperating. - Punish defection with a
# single round of defection, but escalate the punishment if defections continue.
# - Forgive and return to cooperation if the opponent cooperates after a
# defection. - Switch to permanent defection if the opponent defects for five
# consecutive rounds.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.retaliation_length = 0      # Track how many rounds we should retaliate
          return axl.Action.C              # Start by cooperating
  
      # If we are in the middle of a retaliation, continue defecting
      if self.retaliation_length > 0:
          self.retaliation_length -= 1
          return axl.Action.D
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      if last_opponent_move == axl.Action.D:
          # Increment consecutive defections count
          self.consecutive_defections += 1
  
          # If opponent has defected 5 times in a row, switch to permanent defection
          if self.consecutive_defections >= 5:
              return axl.Action.D
  
          # Otherwise, retaliate for the same number of rounds as the consecutive defections
          self.retaliation_length = self.consecutive_defections
          return axl.Action.D
  
      else:  # Opponent cooperated
          # Reset consecutive defections count and return to cooperation
          self.consecutive_defections = 0
          return axl.Action.C

# ### Revised Strategy: **Adaptive Tit-for-Tat with Conditional Forgiveness**
# 1. **Start by Cooperating**: In the first round, always play C (Cooperate) to
# signal a willingness to establish mutual cooperation.  2. **Mirror the
# Opponent's Last Move**: From the second round onward, copy your opponent's
# previous move. If they cooperated in the last round, you cooperate (play C).
# If they defected in the last round, you defect (play D).  3. **Forgive After a
# Single Defection**: If the opponent defects once, forgive them by playing C in
# the next round. This allows for occasional mistakes or random defections
# without immediately escalating into a cycle of mutual defection.  4. **Punish
# Persistent Defection**: If the opponent defects for 3 consecutive rounds,
# switch to defection (play D) until they cooperate again. This prevents
# exploitation by opponents who defect repeatedly.  5. **Return to Cooperation
# After Opponent Cooperates**: If the opponent returns to cooperation after a
# period of defection, immediately switch back to cooperation (play C) to re-
# establish mutual trust.  6. **End-Game Strategy**: In the final 50 rounds,
# gradually become more cautious. If the opponent defects more than twice in
# this period, switch to defection for the remainder of the game to avoid being
# exploited in the end-game phase.  ---  This revised strategy addresses the
# critiques by introducing conditional forgiveness, punishing persistent
# defection, and adapting to the fixed length of the game. It balances
# cooperation with the need to avoid exploitation, while also allowing for
# recovery from occasional mistakes.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          # Forgiveness and punishment tracking
          self.defection_streak = 0  # Track consecutive defections by opponent
          return axl.Action.C
  
      # End-game strategy: last 50 rounds
      if len(self.history) >= 950:
          if opponent.history[-50:].count(axl.Action.D) > 2:
              return axl.Action.D  # Defect if opponent defected more than twice in the last 50 rounds
  
      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
      else:
          self.defection_streak = 0  # Reset defection streak if opponent cooperates
  
      # Punish persistent defection
      if self.defection_streak >= 3:
          return axl.Action.D  # Defect if opponent has defected 3 times in a row
  
      # Forgive after a single defection
      if opponent.history[-1] == axl.Action.D and self.defection_streak == 1:
          return axl.Action.C  # Forgive a single defection
  
      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]

# 1. **Start by Defecting (D):** In the first round, play Defect (D) to test
# your opponent’s strategy and avoid being exploited if they start with Defect
# (D).  2. **Defect if Opponent Cooperates (C):** If your opponent plays
# Cooperate (C) after your first Defect (D), continue playing Defect (D) in
# every subsequent round to maximize your payoff (5 points) while they score 0.
# This exploits cooperative opponents.  3. **Switch to Tit-for-Tat if Opponent
# Defects (D):** If your opponent plays Defect (D) in any round, switch to a
# Tit-for-Tat strategy:    - If your opponent plays C, respond with C in the
# next round.    - If your opponent plays D, respond with D in the next round.
# 4. **Return to Defection if Opponent Defects for 5 Consecutive Rounds:** If
# your opponent defects for 5 consecutive rounds, switch to always Defect (D)
# for the remainder of the game. This minimizes losses in case the opponent is
# committed to defection.  5. **Return to Cooperation After Mutual
# Cooperation:** If both you and your opponent have cooperated (both playing C)
# for 5 consecutive rounds after any defection, continue playing Cooperate (C)
# unless your opponent defects again, at which point revert to Tit-for-Tat.
# This revised strategy maintains an aggressive stance by exploiting cooperative
# opponents, while also allowing for a flexible response to defection through
# Tit-for-Tat. It avoids prolonged mutual defection unless the opponent is
# consistently uncooperative.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.consecutive_cooperations = 0  # Track consecutive mutual cooperations
          self.exploiting = False  # Track if we are exploiting a cooperative opponent
          return axl.Action.D  # Start by defecting
  
      # Check if we are exploiting a cooperative opponent
      if self.exploiting:
          return axl.Action.D  # Continue defecting if we are exploiting
  
      # Check if opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_cooperations = 0  # Reset cooperation counter
          self.consecutive_defections += 1  # Increment defection counter
  
          # If opponent defected for 5 consecutive rounds, switch to always defect
          if self.consecutive_defections >= 5:
              return axl.Action.D
  
          # Otherwise, play Tit-for-Tat (mirror opponent's last move)
          return axl.Action.D
  
      # If opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0  # Reset defection counter
  
          # If we defected in the first round and opponent cooperated, start exploiting
          if len(self.history) == 1 and self.history[0] == axl.Action.D:
              self.exploiting = True
              return axl.Action.D
  
          # Otherwise, play Tit-for-Tat (mirror opponent's last move)
          if self.history[-1] == axl.Action.C:
              self.consecutive_cooperations += 1  # Increment cooperation counter
          else:
              self.consecutive_cooperations = 0  # Reset cooperation counter
  
          # If mutual cooperation for 5 consecutive rounds, continue cooperating
          if self.consecutive_cooperations >= 5:
              return axl.Action.C
  
          return axl.Action.C

# ### Revised Strategy: **Tit-for-Tat with Gradual Retaliation**  1. **Start by
# cooperating (play C in the first round).**  2. **In each subsequent round:**
# - **If your opponent cooperated in the previous round, cooperate (play C).**
# - **If your opponent defected in the previous round, defect (play D) in the
# next round.**  3. **If your opponent defects again after your retaliation,
# continue defecting (play D) for an increasing number of rounds**:    - After
# the second consecutive defection, defect for 2 rounds.    - After the third
# consecutive defection, defect for 3 rounds, and so on.  4. **If your opponent
# returns to cooperation after a defection, forgive immediately and return to
# cooperation (play C).**  5. **If your opponent defects for 5 or more
# consecutive rounds, switch to permanent defection (play D) for the remainder
# of the game.**  6. **If both players fall into mutual defection for 3 or more
# rounds, attempt to break the cycle by cooperating (play C) once. If the
# opponent cooperates in response, return to mutual cooperation. If they defect
# again, resume the gradual retaliation process.**  This revised strategy
# addresses the critiques by introducing a gradual escalation of retaliation,
# preventing exploitation from alternating defection, and providing a mechanism
# to break cycles of mutual defection.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.retaliation_length = 0  # Tracks how many rounds to retaliate
          self.consecutive_defections = 0  # Tracks consecutive defections by opponent
          self.mutual_defection_count = 0  # Tracks mutual defections
          return axl.Action.C  # Start by cooperating
  
      # Check the last move of the opponent
      opponent_last_move = opponent.history[-1]
      
      # If opponent cooperated in the last round, reset retaliation and cooperate
      if opponent_last_move == axl.Action.C:
          self.retaliation_length = 0
          self.consecutive_defections = 0
          self.mutual_defection_count = 0
          return axl.Action.C
  
      # If opponent defected in the last round
      if opponent_last_move == axl.Action.D:
          self.consecutive_defections += 1
  
          # If opponent has defected 5 or more times consecutively, switch to permanent defection
          if self.consecutive_defections >= 5:
              return axl.Action.D
  
          # If we are in a mutual defection cycle, track it
          if self.history[-1] == axl.Action.D:
              self.mutual_defection_count += 1
          else:
              self.mutual_defection_count = 0
  
          # If mutual defection has occurred for 3 or more rounds, attempt to break the cycle
          if self.mutual_defection_count >= 3:
              self.mutual_defection_count = 0  # Reset the mutual defection count
              return axl.Action.C  # Attempt to break the cycle by cooperating
  
          # If not in a mutual defection cycle, retaliate with increasing length
          if self.retaliation_length < self.consecutive_defections:
              self.retaliation_length = self.consecutive_defections
  
          # Continue defecting for the length of the retaliation
          if self.retaliation_length > 0:
              self.retaliation_length -= 1
              return axl.Action.D
  
          # Default to cooperation if no other condition is met
          return axl.Action.C

# ### Revised Strategy for the Iterated Game (1000 rounds):  1. **Start with
# cooperation (C) in the first round.**  2. **Observe the opponent’s move from
# the previous round:**    - **If the opponent played C in the last round,
# continue playing C.**    - **If the opponent played D in the last round, play
# D in the next round, but only for one round.** After that, return to C to test
# if the opponent is willing to cooperate again.  3. **If the opponent defects
# (plays D) twice in a row, switch to D for two rounds, then return to C.** This
# allows for a stronger response to repeated defection but still offers a path
# back to cooperation.  4. **If the opponent defects three times in a row,
# switch to D indefinitely until the opponent plays C again.** Once the opponent
# plays C, return to C in the next round to re-establish cooperation.  5.
# **Endgame (last 20 rounds):**    - Continue following the same rules as above,
# but **be more cautious**. If the opponent defects twice in a row during the
# last 20 rounds, switch to D for the remainder of the game to avoid late-game
# exploitation.  This revised strategy balances retaliation with opportunities
# for recovery, avoids indefinite defection loops, and introduces a more
# flexible endgame approach.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Define constants for cooperation and defection
      C, D = axl.Action.C, axl.Action.D
  
      # Check if it's the first round
      if self.first_round():
          return C  # Start with cooperation
  
      # Get the number of rounds played so far
      rounds_played = len(self.history)
  
      # Endgame logic: last 20 rounds
      if rounds_played >= 980:
          # If opponent defects twice in a row during the last 20 rounds, defect for the rest of the game
          if opponent.history[-2:] == [D, D]:
              return D
  
      # General strategy logic
      if opponent.history[-1] == C:
          return C  # Cooperate if opponent cooperated last round
      elif opponent.history[-1] == D:
          # Check if opponent defected twice in a row
          if opponent.history[-2:] == [D, D]:
              # Check if opponent defected three times in a row
              if opponent.history[-3:] == [D, D, D]:
                  return D  # Defect indefinitely until opponent cooperates
              else:
                  return D  # Defect for two rounds after two consecutive defections
          else:
              return D  # Defect for one round after a single defection

# 1. **Start with Cooperation (C):** Begin the game by playing Cooperation (C)
# to establish a foundation of trust and encourage mutual cooperation, which
# yields the highest long-term payoff (3 points each).  2. **Tit-for-Tat with
# Immediate Defection Response:** After the first round, adopt a tit-for-tat
# strategy. If your opponent cooperates, continue cooperating. If your opponent
# defects, immediately defect in the next round to signal that defection will
# not be tolerated.  3. **Forgive After One Defection:** If your opponent
# defects once but returns to cooperation in the following round, forgive them
# and return to cooperation as well. This prevents a prolonged cycle of mutual
# defection and encourages a return to higher payoffs.  4. **Occasional
# Defection to Test Opponent’s Commitment:** Every 20-30 rounds, defect once
# even if your opponent has been cooperating consistently. This tests their
# commitment to cooperation and keeps them from assuming you will always
# cooperate. If they respond with defection, return to cooperation after one
# round of mutual defection.  5. **Adapt to Opponent’s Strategy:** If the
# opponent consistently defects, switch to constant defection (D) to avoid being
# exploited. If they consistently cooperate, continue cooperating to maximize
# mutual payoffs.  6. **Gradual Shift to Defection in the Final 10 Rounds:** In
# the last 10 rounds, begin defecting gradually. Start by defecting once every
# few rounds, then increase the frequency of defection as the game approaches
# the final round. This reduces the risk of the opponent anticipating a sudden
# switch to constant defection and retaliating early.  7. **Final Round
# Defection:** On the very last round, always defect (D), as there is no future
# consequence for doing so, and it maximizes your final payoff.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_test_round = self._random.randint(20, 30)  # Random round for testing opponent's commitment
          return axl.Action.C  # Start with cooperation
  
      # Get the current round number
      current_round = len(self.history)
  
      # Final round defection
      if current_round == 1000:
          return axl.Action.D
  
      # Gradual shift to defection in the final 10 rounds
      if current_round >= 991:
          if current_round % 2 == 0:  # Defect every other round in the last 10 rounds
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Tit-for-tat with immediate defection response
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Forgive after one defection if opponent cooperates again
      if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Occasional defection to test opponent's commitment
      if current_round == self.defection_test_round:
          self.defection_test_round += self._random.randint(20, 30)  # Schedule next test
          return axl.Action.D
  
      # Adapt to opponent's strategy: if opponent consistently defects, switch to constant defection
      if opponent.history.defections >= current_round * 0.5:  # If opponent defects more than 50% of the time
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C

# ### Revised Strategy: **Tit-for-Tat with Gradual Forgiveness**  1. **Start by
# cooperating.**      Play C in the first round.  2. **Mirror your opponent's
# previous move, but with a delay in retaliation.**      If your opponent plays
# C, continue to play C. If your opponent plays D, respond with D in the next
# round, but only after two consecutive defections. This delay helps avoid
# unnecessary escalation due to a single defection or mistake.  3. **Forgive
# after a single defection.**      If your opponent defects once (plays D) but
# returns to cooperation (plays C) in the next round, immediately return to
# cooperation (play C). This encourages the opponent to return to cooperation
# without punishing them too harshly for a single defection.  4. **Gradually
# escalate punishment for repeated defections.**      If your opponent defects
# for two consecutive rounds, defect once in response. If they continue to
# defect for three or more rounds, defect for an increasing number of rounds
# (e.g., defect for two rounds after three defections, three rounds after four
# defections, etc.). This gradual escalation discourages persistent defection
# while allowing for recovery.  5. **Return to cooperation if the opponent shows
# willingness to cooperate.**      If your opponent returns to cooperation
# (plays C) after a series of defections, return to cooperation (play C) after
# one round of defection. This allows for reconciliation and avoids long-term
# mutual defection.  6. **Account for potential noise or mistakes.**      If
# defections appear sporadic or inconsistent (e.g., alternating between C and
# D), assume the opponent may be making mistakes or using a mixed strategy. In
# this case, continue to cooperate more often than defect, but still mirror
# defection occasionally to avoid being exploited.  This revised strategy
# balances cooperation with a more measured response to defection, allowing for
# recovery from mistakes while discouraging long-term exploitation.

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
  
      # Helper function to count consecutive defections
      def count_consecutive_defections(history):
          count = 0
          for move in reversed(history):
              if move == axl.Action.D:
                  count += 1
              else:
                  break
          return count
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
      
      # If the opponent cooperated in the last round, we cooperate
      if opponent_last_move == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the last round, check the history
      if opponent_last_move == axl.Action.D:
          # Count consecutive defections by the opponent
          consecutive_defections = count_consecutive_defections(opponent.history)
  
          # If the opponent defected once but cooperated before, forgive and cooperate
          if len(opponent.history) >=2 and consecutive_defections == 1 and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
  
          # If the opponent defected twice in a row, retaliate with one defection
          if consecutive_defections == 2:
              return axl.Action.D
  
          # If the opponent defected three or more times, escalate punishment
          if consecutive_defections >= 3:
              # Defect for an increasing number of rounds based on the number of defections
              return axl.Action.D if consecutive_defections <= len(self.history) else axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# **Revised Strategy: Conditional Cooperation with Controlled Retaliation and
# Adaptive Forgiveness**  1. **Start with Cooperation (C):** In the first round,
# play C.  2. **Tit-for-Tat with Immediate Retaliation:**    - In each round, if
# your opponent played C in the previous round, play C.    - If your opponent
# played D in the previous round, retaliate by playing D in the next round.  3.
# **Controlled Retaliation:**    - If the opponent defects (plays D), retaliate
# by playing D for **one round only**. After that, return to C, regardless of
# the opponent’s next move. This prevents getting stuck in a long defection
# cycle.  4. **Forgiveness Mechanism:**    - If the opponent defects twice in a
# row, play C after your second defection to test for cooperation again. If they
# respond with C, continue cooperating.    - If the opponent defects again after
# you return to C, repeat the controlled retaliation (one round of D) and then
# return to C.  5. **Punish Persistent Defection:**    - If the opponent defects
# **three times in a row**, switch to playing D indefinitely, as they are likely
# committed to defection. This prevents excessive exploitation.  6. **Mistake
# Recovery:**    - If the opponent returns to C after a defection streak,
# immediately return to C as well. This allows for recovery from accidental
# defections and avoids unnecessary punishment.  7. **Endgame Adjustment:**    -
# In the final 10 rounds, if the opponent has been cooperative (mostly playing
# C), continue cooperating.    - If the opponent has been defecting frequently,
# switch to D in the last 5 rounds to avoid being exploited at the end of the
# game.  This revised strategy balances cooperation, controlled retaliation, and
# forgiveness, while also considering the potential for mistakes and the length
# of the game.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.retaliation_count = 0  # Tracks how many times we retaliated
          self.defection_streak = 0   # Tracks consecutive defections by opponent
          return axl.Action.C         # Start with cooperation
  
      # Endgame adjustment: In the last 10 rounds
      if len(self.history) >= 990:
          if opponent.history[-10:].count(axl.Action.D) > 5:
              # If opponent defected frequently in the last 10 rounds, defect in the last 5 rounds
              if len(self.history) >= 995:
                  return axl.Action.D
          return axl.Action.C  # Otherwise, continue cooperating
  
      # Tit-for-Tat with immediate retaliation
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
          if self.defection_streak == 1:
              # Controlled retaliation: retaliate for one round only
              self.retaliation_count = 1
              return axl.Action.D
          elif self.defection_streak == 2:
              # Forgiveness mechanism: after two defections, return to C
              return axl.Action.C
          elif self.defection_streak >= 3:
              # Punish persistent defection: defect indefinitely after 3 consecutive defections
              return axl.Action.D
      else:
          # Reset defection streak if opponent cooperates
          self.defection_streak = 0
          if self.retaliation_count > 0:
              # After one round of retaliation, return to cooperation
              self.retaliation_count = 0
              return axl.Action.C
          return axl.Action.C  # Continue cooperating if opponent cooperates

# ### Revised Aggressive Strategy for the Iterated Normal-Form Game  1. **Start
# by Cooperating (C)** in the first round to avoid provoking immediate
# retaliation and to test the opponent's willingness to cooperate.  2. **Defect
# (D) if the opponent defects in any round**. Continue defecting until the
# opponent cooperates **twice in a row**.  3. **Return to Cooperation (C) after
# the opponent cooperates twice in a row**. This signals a willingness to
# rebuild trust and potentially achieve higher payoffs through mutual
# cooperation.  4. **Alternate between Cooperation (C) and Defection (D) if the
# opponent alternates**. This prevents the opponent from exploiting you by
# mixing strategies unpredictably.  5. **If mutual cooperation (C, C) is
# sustained for at least 5 consecutive rounds**, continue cooperating unless the
# opponent defects. This maximizes the potential for high payoffs through long-
# term cooperation.  6. **Defect (D) in the last 3 rounds** to maximize end-game
# payoffs, but only if the opponent has shown a pattern of defection or if
# mutual cooperation has not been established. If mutual cooperation has been
# consistent, continue cooperating until the final round.  ---  This revised
# strategy balances aggression with adaptability. It starts with cooperation to
# avoid immediate retaliation, but quickly shifts to defection if the opponent
# defects. It also provides a clear path to rebuild cooperation if the opponent
# shows a willingness to cooperate, while maintaining an aggressive stance in
# the end-game to maximize payoffs.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if opponent cooperated twice in a row
      def opponent_cooperated_twice_in_a_row():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C
  
      # Helper function to check if mutual cooperation has been sustained for at least 5 rounds
      def mutual_cooperation_sustained():
          return len(self.history) >= 5 and self.history[-5:] == [axl.Action.C] * 5 and opponent.history[-5:] == [axl.Action.C] * 5
  
      # Helper function to check if the opponent is alternating between C and D
      def opponent_is_alternating():
          if len(opponent.history) < 2:
              return False
          return all(opponent.history[i] != opponent.history[i + 1] for i in range(len(opponent.history) - 1))
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Last 3 rounds: Defect if opponent has defected or mutual cooperation has not been established
      if len(self.history) >= 997:
          if axl.Action.D in opponent.history or not mutual_cooperation_sustained():
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent defected in the last round, defect until they cooperate twice in a row
      if opponent.history[-1] == axl.Action.D:
          if not opponent_cooperated_twice_in_a_row():
              return axl.Action.D
  
      # If opponent cooperates twice in a row, return to cooperation
      if opponent_cooperated_twice_in_a_row():
          return axl.Action.C
  
      # If opponent is alternating, alternate between C and D
      if opponent_is_alternating():
          return axl.Action.D if self.history[-1] == axl.Action.C else axl.Action.C
  
      # If mutual cooperation has been sustained for at least 5 rounds, continue cooperating
      if mutual_cooperation_sustained():
          return axl.Action.C
  
      # Default action: Cooperate
      return axl.Action.C

# 1. **Start with Cooperation**: In the first round, play C (cooperate).  2.
# **Tit-for-Tat with Occasional Testing**: In each subsequent round, copy your
# opponent's previous move. If they played C, play C. If they played D, play D.
# However, every 50 rounds, regardless of the opponent's behavior, play C to
# test if they are willing to return to cooperation.  3. **Forgive Single
# Defections, but Watch for Patterns**: If the opponent defects once but returns
# to cooperation in the next round, forgive them and return to cooperation.
# However, if the opponent alternates between cooperation and defection (e.g.,
# CDCD), switch to defection (D) until they show consistent cooperation for at
# least 3 consecutive rounds.  4. **Punish Continuous Defection Quickly**: If
# the opponent defects for **two consecutive rounds**, switch to defection (D)
# for the next 5 rounds. After this punishment period, test cooperation again by
# playing C. If the opponent continues to defect, switch to permanent defection
# (D) for the rest of the game.  5. **Endgame Strategy**: In the last 10 rounds,
# defect (D) regardless of the opponent's behavior, as there is no future
# retaliation to worry about.  This revised strategy encourages cooperation,
# punishes consistent defection more quickly, and includes mechanisms to test
# the opponent's willingness to cooperate while accounting for the endgame.

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
          self.punishment_counter = 0  # Tracks how many rounds of punishment are left
          self.cooperation_test_round = 50  # Every 50 rounds, test cooperation
          self.alternating_defection = False  # Tracks if opponent is alternating CDCD
          self.consecutive_cooperations = 0  # Tracks consecutive cooperations after alternating CDCD
          return axl.Action.C  # Start with cooperation
  
      # Endgame strategy: defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # If in punishment mode, continue defecting for the punishment period
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # Check for alternating CDCD pattern
      if len(opponent.history) >= 4 and opponent.history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
          self.alternating_defection = True
  
      # If alternating CDCD, switch to defection until 3 consecutive cooperations
      if self.alternating_defection:
          if opponent.history[-1] == axl.Action.C:
              self.consecutive_cooperations += 1
          else:
              self.consecutive_cooperations = 0
  
          if self.consecutive_cooperations >= 3:
              self.alternating_defection = False  # Reset after 3 consecutive cooperations
              self.consecutive_cooperations = 0
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Tit-for-Tat: copy opponent's last move
      if opponent.history[-1] == axl.Action.D:
          # Punish continuous defection quickly: if opponent defects twice in a row, defect for 5 rounds
          if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              self.punishment_counter = 5
              return axl.Action.D
          return axl.Action.D
      else:
          # Forgive single defections
          return axl.Action.C
  
      # Every 50 rounds, test cooperation by playing C
      if len(self.history) % self.cooperation_test_round == 0:
          return axl.Action.C

# Here is the revised strategy:  1. **Initial Move**: Start by playing **C**
# (cooperate) in the first round.  2. **Immediate Retaliation**: If the opponent
# plays **D** (defect) in the previous round, immediately respond by playing
# **D** in the next round.  3. **Return to Cooperation**: If the opponent
# returns to playing **C** after defecting, immediately return to playing **C**
# in the next round. This ensures quick forgiveness and avoids unnecessary
# escalation.  4. **Testing for Cooperation**: If the opponent defects for
# multiple rounds, occasionally test their willingness to cooperate by playing
# **C** after every 3 consecutive rounds of mutual defection. If they respond
# with **C**, return to cooperation; if they continue to defect, return to
# **D**.  5. **Adaptation to Persistent Defection**: If the opponent defects for
# more than 5 consecutive rounds, switch to playing **D** indefinitely, as the
# opponent is likely committed to defection.  6. **Endgame Consideration**: In
# the final 10 rounds, if the opponent has been cooperative, continue
# cooperating. However, if the opponent has defected frequently, switch to **D**
# for the remaining rounds to maximize your payoff.  This revised strategy
# incorporates immediate retaliation, quick forgiveness, testing for
# cooperation, adaptation to persistent defection, and an endgame adjustment.

class Neutral_23(LLM_Strategy):
  n = 23
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
      
      # Check if we are in the final 10 rounds
      if len(self.history) >= 990:
          # If the opponent has defected frequently, switch to D
          if opponent.history.defections > opponent.history.cooperations:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Immediate retaliation: If opponent defected last round, play D
      if opponent_last_move == axl.Action.D:
          # Check if the opponent has defected for more than 5 consecutive rounds
          if opponent.history[-5:].count(axl.Action.D) == 5:
              # Switch to playing D indefinitely
              return axl.Action.D
          # Otherwise, retaliate with D
          return axl.Action.D
  
      # Return to cooperation: If opponent cooperated after defecting, play C
      if opponent_last_move == axl.Action.C and self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Testing for cooperation: After 3 consecutive mutual defections, test with C
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D] * 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# ### Revised Aggressive Iterated Game Strategy:  1. **Start with defection, but
# be ready to adapt.**      Begin by playing D (Defect) on the first move to
# test the opponent’s response. This establishes an aggressive stance but allows
# for flexibility based on the opponent’s behavior.  2. **If the opponent
# defects in response, switch to tit-for-tat.**      If the opponent defects
# after your initial defection, immediately switch to a tit-for-tat strategy:
# - Mirror the opponent’s previous move (if they play C, you play C; if they
# play D, you play D).      This ensures you avoid prolonged mutual defection
# and can capitalize on cooperation if the opponent is willing to cooperate.  3.
# **If the opponent continues to cooperate after your defection, switch to
# cooperation.**      If the opponent plays C (Cooperate) after your initial
# defection, switch to playing C as well. This allows you to take advantage of
# mutual cooperation (3 points per round) and avoid unnecessary losses from
# continued defection.  4. **Punish defection with a single defection, then
# return to cooperation.**      If the opponent defects after a period of mutual
# cooperation, punish them by defecting once. After this, return to cooperation
# (C) to signal that you are willing to cooperate again if they stop defecting.
# This prevents long-term mutual defection while still discouraging
# exploitation.  5. **In the final 50 rounds, defect only if the opponent
# defects.**      In the last 50 rounds, continue using tit-for-tat, but be more
# cautious about defection. Only defect if the opponent defects first. This
# prevents unnecessary retaliation and maximizes potential cooperation in the
# endgame.  6. **If the opponent consistently defects, defect as well.**      If
# the opponent shows a pattern of consistent defection (e.g., 5 or more
# consecutive defections), switch to defecting exclusively. There is no benefit
# to cooperating with an opponent who is not willing to cooperate.  ---  This
# revised strategy balances early aggression with adaptability, allowing for
# cooperation when beneficial while still punishing defection. It avoids
# prolonged mutual defection and maximizes payoffs by responding flexibly to the
# opponent’s behavior.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperating = False  # Track if we are in a cooperation phase
          self.tit_for_tat = False  # Track if we are in tit-for-tat mode
          return axl.Action.D  # Start with defection
  
      # Check if we are in the last 50 rounds
      if len(self.history) >= 950:
          # In the last 50 rounds, use tit-for-tat but only defect if opponent defects first
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent defected after our initial defection, switch to tit-for-tat
      if len(self.history) == 2 and opponent.history[1] == axl.Action.D:
          self.tit_for_tat = True
  
      # If opponent cooperated after our initial defection, switch to cooperation
      if len(self.history) == 2 and opponent.history[1] == axl.Action.C:
          self.cooperating = True
  
      # If in tit-for-tat mode, mirror the opponent's last move
      if self.tit_for_tat:
          return opponent.history[-1]
  
      # If in cooperation mode, punish a defection with a single defection, then return to cooperation
      if self.cooperating:
          if opponent.history[-1] == axl.Action.D:
              self.cooperating = False  # Temporarily stop cooperating to punish
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent defects 5 or more times consecutively, switch to always defecting
      if opponent.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.D
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# 1. **Start by cooperating (play C).**  2. **Mirror your opponent’s previous
# move from round 2 onwards (Tit-for-Tat), but with a tolerance for occasional
# defections:**    - If your opponent played C in the previous round, play C.
# - If your opponent played D in the previous round, play D **only if they
# defected in two consecutive rounds**. Otherwise, continue to play C.  3.
# **Forgive after a single defection if followed by cooperation:**    - If your
# opponent defects (plays D) but then returns to cooperation (plays C) in the
# next round, immediately return to cooperation (play C) as well.  4.
# **Introduce a "grace period" for persistent defection:**    - If your opponent
# defects for **5 consecutive rounds**, switch to defection (play D) for the
# next 5 rounds.    - After this period, test cooperation again by playing C. If
# the opponent cooperates, return to cooperation. If they defect again, switch
# to permanent defection (play D for the rest of the game).  5. **Endgame
# strategy (last 10 rounds):**    - In the final 10 rounds, defect (play D)
# regardless of the opponent’s actions, as there is no future punishment
# possible.

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
          self.grace_period_active = False
          self.grace_period_counter = 0
          self.permanent_defection = False
          return axl.Action.C  # Start by cooperating
  
      # Endgame strategy: Defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check for permanent defection
      if self.permanent_defection:
          return axl.Action.D
  
      # Check if we are in the grace period
      if self.grace_period_active:
          self.grace_period_counter += 1
          if self.grace_period_counter <= 5:
              return axl.Action.D  # Defect during the grace period
          else:
              self.grace_period_active = False  # End the grace period
              self.grace_period_counter = 0
              return axl.Action.C  # Test cooperation after grace period
  
      # Mirror opponent's previous move with tolerance for defections
      if opponent.history[-1] == axl.Action.D:
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              self.consecutive_defections += 1
          else:
              self.consecutive_defections = 1
      else:
          self.consecutive_defections = 0
  
      # If opponent defects for 5 consecutive rounds, enter grace period
      if self.consecutive_defections >= 5:
          self.grace_period_active = True
          return axl.Action.D
  
      # If opponent defected in the last round but not consecutively, continue cooperating
      if opponent.history[-1] == axl.Action.D and self.consecutive_defections == 1:
          return axl.Action.C
  
      # If opponent cooperates, cooperate
      return axl.Action.C

# ### Revised Neutral Strategy for 1000-round Iterated Game:  1. **Start with
# Cooperation**: Begin the game by playing C (Cooperate) in the first round.  2.
# **Tit-for-Tat with Conditional Forgiveness**: From the second round onward,
# adopt a modified "Tit-for-Tat" approach:    - **If the opponent played C in
# the previous round**, play C (Cooperate).    - **If the opponent played D in
# the previous round**, play D (Defect) in the next round.    - **If the
# opponent cooperates after you defect**, return to C (Cooperate) in the
# following round to encourage mutual cooperation.    - **If the opponent
# defects again after you defect**, continue playing D (Defect) until they
# cooperate for 2 consecutive rounds, at which point you return to C
# (Cooperate).  3. **Punish Sustained Defection**: If the opponent defects for 3
# consecutive rounds, switch to permanent defection (D) for the remainder of the
# game to avoid further exploitation.  4. **Endgame Caution**: In the last 10
# rounds, continue using the same strategy (Tit-for-Tat with Conditional
# Forgiveness) rather than switching to unconditional cooperation. This prevents
# the opponent from exploiting the endgame by defecting without consequence.
# ### Summary of Conditions: 1. Start with C. 2. Mirror the opponent’s previous
# move (Tit-for-Tat). 3. Forgive after one defection if the opponent cooperates,
# but defect if they continue defecting. 4. Switch to permanent defection after
# 3 consecutive defections. 5. Maintain the same strategy in the last 10 rounds
# to avoid endgame exploitation.  This revised strategy addresses the critiques
# by introducing conditional forgiveness, punishing sustained defection more
# effectively, and maintaining caution in the endgame.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants for actions
      C, D = axl.Action.C, axl.Action.D
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.permanent_defection = False  # Flag for permanent defection
          return C  # Start with cooperation
  
      # If permanent defection has been triggered, always defect
      if self.permanent_defection:
          return D
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # Update consecutive defections count
      if opponent_last_move == D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # If opponent has defected 3 times in a row, switch to permanent defection
      if self.consecutive_defections >= 3:
          self.permanent_defection = True
          return D
  
      # Tit-for-Tat with Conditional Forgiveness
      if opponent_last_move == C:
          return C  # Cooperate if opponent cooperated last round
      else:
          # Check if opponent cooperated after our defection
          if len(self.history) > 1 and self.history[-1] == D and opponent_last_move == C:
              return C  # Forgive and return to cooperation
          else:
              return D  # Otherwise, defect

# 1. **Start with Cooperation (C)**: Begin the game by playing C. This signals a
# willingness to cooperate and avoids immediately provoking a cycle of mutual
# defection.  2. **Tit-for-Tat with Defection Bias**: After the first round,
# adopt a tit-for-tat approach with a bias toward defection. If the opponent
# plays C, respond with C in the next round. If the opponent plays D, respond
# with D in the next round. This ensures you mirror the opponent’s behavior
# while maintaining a defensive stance.  3. **Punish Two Consecutive Defections
# with Extended Defection**: If the opponent defects for two consecutive rounds,
# switch to playing D for the next three rounds. This escalates the punishment
# for sustained defection, discouraging the opponent from exploiting your
# cooperation.  4. **Return to Cooperation After Punishment**: After punishing
# the opponent with three rounds of defection, return to playing C to test if
# the opponent is willing to cooperate again. This provides an opportunity to
# re-establish cooperation if the opponent is responsive.  5. **Adapt to
# Opponent’s Strategy**: If the opponent consistently defects (e.g., for more
# than 10 consecutive rounds), switch to always playing D for the remainder of
# the game. This prevents you from being exploited by an opponent who is
# committed to defection.  6. **Occasional Cooperation to Test for Change**: If
# both players have been defecting for more than 20 rounds, play C once to test
# if the opponent is willing to shift to cooperation. If the opponent responds
# with C, return to tit-for-tat. If they respond with D, return to always
# defecting.  7. **Endgame Strategy**: In the final 10 rounds of the game,
# switch to always playing D regardless of the opponent’s behavior. This ensures
# you maximize your payoff in the closing rounds when the incentive to defect is
# highest.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Endgame strategy: Always defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Count the number of consecutive defections by the opponent
      def opponent_consecutive_defections(n):
          return opponent.history[-n:] == [axl.Action.D] * n
  
      # Tit-for-Tat with Defection Bias
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Punish two consecutive defections with three rounds of defection
          if opponent_consecutive_defections(2):
              if len(self.history) < 3 or self.history[-3:] != [axl.Action.D] * 3:
                  return axl.Action.D
          return axl.Action.D
  
      # Adapt to opponent's strategy: Always defect if opponent defects for more than 10 consecutive rounds
      if opponent_consecutive_defections(10):
          return axl.Action.D
  
      # Occasional cooperation to test for change after 20 rounds of mutual defection
      if len(self.history) >= 20 and self.history[-20:].count(axl.Action.D) == 20 and opponent.history[-20:].count(axl.Action.D) == 20:
          return axl.Action.C
  
      # Default to Tit-for-Tat
      return opponent.history[-1]

# ### Revised Strategy: **Tit-for-Tat with Conditional Forgiveness**  1. **Start
# by Cooperating**: In the first round, always play **C** (Cooperate).  2.
# **Mirror the Opponent's Last Move**: In each subsequent round, play **the same
# action your opponent played in the previous round** (i.e., if they played C,
# you play C; if they played D, you play D).  3. **Forgive Occasional
# Defections**: If your opponent defects (plays D) **once or twice in non-
# consecutive rounds**, continue following the mirroring rule. If they return to
# cooperation (play C) in the next round, **immediately return to playing C**.
# 4. **Punish Persistent Defection**: If your opponent defects for **three
# consecutive rounds**, switch to playing **D** for the next **three rounds** as
# punishment.  5. **Return to Cooperation After Punishment**: After the three-
# round punishment, if your opponent plays **C** for two consecutive rounds,
# return to playing **C** and resume the cooperative strategy.  6. **Escalate
# Defection if Opponent Continues Defecting**: If your opponent continues to
# defect after the three-round punishment (i.e., they play D for more than five
# consecutive rounds), switch to **permanent defection** (always play D) for the
# remainder of the game.  7. **Endgame Consideration**: In the final 10 rounds
# of the game, **always cooperate** unless your opponent has been defecting
# consistently. If they have been defecting in the last 10 rounds, switch to
# **permanent defection** for the remainder of the game.  This revised strategy
# balances cooperation, forgiveness, and punishment, while addressing the need
# for escalation in response to persistent defection and considering the length
# of the game.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.punishment_rounds = 0       # Track how many punishment rounds are left
          return axl.Action.C              # Start by cooperating
  
      # Endgame consideration: Always cooperate in the last 10 rounds unless opponent has been defecting
      if len(self.history) >= 990:
          if opponent.history[-10:].count(axl.Action.D) > 0:
              return axl.Action.D  # Defect if opponent has been defecting in the last 10 rounds
          else:
              return axl.Action.C  # Otherwise, cooperate in the last 10 rounds
  
      # If in punishment phase, continue defecting for 3 rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Check opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If opponent cooperated in the last round, reset consecutive defections and cooperate
      if last_opponent_move == axl.Action.C:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # If opponent defected in the last round
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1
  
          # If opponent defected for 3 consecutive rounds, start punishment
          if self.consecutive_defections == 3:
              self.punishment_rounds = 3  # Punish for 3 rounds
              return axl.Action.D
  
          # If opponent has defected for more than 5 consecutive rounds, switch to permanent defection
          if self.consecutive_defections > 5:
              return axl.Action.D
  
          # Otherwise, mirror the opponent's defection
          return axl.Action.D

# ### Revised Neutral Strategy for Iterated 1000-Round Game:  1. **Initial Move:
# Cooperate (C).**      Start by cooperating in the first round to establish a
# neutral and cooperative tone.  2. **Tit-for-Tat with Gradual Forgiveness:**
# - **If the opponent cooperated (C) in the previous round, continue to
# cooperate (C).**    - **If the opponent defected (D) in the previous round,
# defect (D) in the next round.**        However, if the opponent cooperates
# again after defecting, **immediately return to cooperation (C)** to encourage
# mutual cooperation.  3. **Forgiveness for Occasional Defections:**    - If the
# opponent defects (D) **once or twice in a row**, continue to follow the tit-
# for-tat approach (defect in response, then cooperate if they cooperate).    -
# If the opponent defects (D) **three times in a row**, **defect for the next 3
# rounds** to signal that repeated defection will not be tolerated. After this,
# return to cooperation (C) if the opponent cooperates again.  4. **Permanent
# Defection Only After Persistent Betrayal:**    - If the opponent defects (D)
# **five consecutive times**, switch to permanent defection (D) for the
# remainder of the game. This ensures you are not exploited by a consistently
# defecting opponent.  5. **Endgame Caution:**    - In the final 10 rounds,
# **continue to follow the tit-for-tat approach** rather than unconditionally
# cooperating. This prevents exploitation in the endgame while still allowing
# for cooperation if the opponent remains cooperative.  ### Summary: - Start by
# cooperating. - Mirror the opponent’s previous move but forgive occasional
# defections by returning to cooperation if they cooperate again. - Respond to
# repeated defections with temporary retaliation, but only switch to permanent
# defection after five consecutive defections. - Maintain the tit-for-tat
# approach in the final 10 rounds to avoid endgame exploitation.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Count the number of consecutive defections by the opponent
      consecutive_defections = 0
      for move in reversed(opponent.history):
          if move == axl.Action.D:
              consecutive_defections += 1
          else:
              break
  
      # Rule 4: Permanent defection after 5 consecutive defections
      if consecutive_defections >= 5:
          return axl.Action.D
  
      # Rule 3: Defect for 3 rounds after 3 consecutive defections
      if consecutive_defections == 3:
          if len(self.history) >= 3 and all(move == axl.Action.D for move in self.history[-3:]):
              return axl.Action.D
          return axl.Action.D
  
      # Rule 2: Tit-for-tat with forgiveness
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C


Aggressive_ranks = [
'Aggressive_11',
'Aggressive_19',
'Aggressive_23',
'Aggressive_25',
'Aggressive_8',
'Aggressive_9',
'Aggressive_3',
'Aggressive_16',
'Aggressive_18',
'Aggressive_1',
'Aggressive_15',
'Aggressive_5',
'Aggressive_10',
'Aggressive_22',
'Aggressive_6',
'Aggressive_14',
'Aggressive_17',
'Aggressive_21',
'Aggressive_2',
'Aggressive_12',
'Aggressive_20',
'Aggressive_4',
'Aggressive_7',
'Aggressive_13',
'Aggressive_24',
]

Cooperative_ranks = [
'Cooperative_14',
'Cooperative_25',
'Cooperative_16',
'Cooperative_21',
'Cooperative_12',
'Cooperative_23',
'Cooperative_4',
'Cooperative_18',
'Cooperative_3',
'Cooperative_7',
'Cooperative_2',
'Cooperative_8',
'Cooperative_5',
'Cooperative_6',
'Cooperative_11',
'Cooperative_9',
'Cooperative_20',
'Cooperative_1',
'Cooperative_17',
'Cooperative_15',
'Cooperative_19',
'Cooperative_22',
'Cooperative_10',
'Cooperative_13',
'Cooperative_24',
]

Neutral_ranks = [
'Neutral_10',
'Neutral_24',
'Neutral_5',
'Neutral_18',
'Neutral_1',
'Neutral_16',
'Neutral_12',
'Neutral_25',
'Neutral_3',
'Neutral_21',
'Neutral_13',
'Neutral_23',
'Neutral_6',
'Neutral_22',
'Neutral_2',
'Neutral_17',
'Neutral_7',
'Neutral_11',
'Neutral_19',
'Neutral_9',
'Neutral_15',
'Neutral_20',
'Neutral_8',
'Neutral_4',
'Neutral_14',
]
