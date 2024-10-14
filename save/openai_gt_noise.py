import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy



# ### Aggressive Strategy with Noise Consideration  1. **Initial Action**:
# - Start by playing **D** (Defect).  2. **Tit-for-Tat with Aggressive
# Leaning**:      - *If your opponent plays C (Cooperate)* in the previous
# round, continue playing **D**.    - *If your opponent plays D (Defect)* in the
# previous round, continue playing **D**.  3. **Noise Adjustment**:      - If
# you observe three consecutive **C** actions from your opponent (despite
# noise), switch to **C** (Cooperate) temporarily to explore whether your
# opponent intends to cooperate fully.    - However, if your opponent defects
# again within the next two rounds after you switched to cooperation, revert
# immediately to **D** for the rest of the game.  4. **Endgame (Rounds
# 900-1000)**:      - Regardless of previous actions, play **D** in every round
# from round 900 to round 1000 to maximize payoff in case the opponent shifts
# towards cooperation late in the game.  This strategy maintains an aggressive
# stance to exploit potential cooperation from the opponent while adjusting for
# noise and giving minimal opportunities for the opponent to take advantage of
# cooperation.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial action: Start by playing D
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperations by opponent
          self.switched_to_coop = False  # Track if we switched to cooperation
          self.switch_round = None  # Track the round we switched to cooperation
          return axl.Action.D
  
      # Endgame strategy: Defect from round 900 to 1000
      if len(self.history) >= 900:
          return axl.Action.D
  
      # Tit-for-Tat with aggressive leaning: Always defect unless noise adjustment applies
      if opponent.history[-1] == axl.Action.C:
          self.coop_streak += 1
      else:
          self.coop_streak = 0
  
      # Noise adjustment: Switch to cooperation if opponent cooperates 3 times in a row
      if self.coop_streak >= 3 and not self.switched_to_coop:
          self.switched_to_coop = True
          self.switch_round = len(self.history)
          return axl.Action.C
  
      # If we switched to cooperation, check if opponent defects within the next 2 rounds
      if self.switched_to_coop and len(self.history) - self.switch_round <= 2:
          if opponent.history[-1] == axl.Action.D:
              self.switched_to_coop = False  # Revert to defecting permanently
              return axl.Action.D
          return axl.Action.C
  
      # Default action: Defect
      return axl.Action.D



# ### Strategy: "Forgiving Tit-for-Tat with Noise Adaptation"  1. **Start with
# Cooperation**: Begin by playing **C** (Cooperate) in the first round.  2.
# **Mirror the Opponent’s Previous Action**: From the second round onwards, play
# what your opponent played in the previous round:     - If they played **C**,
# play **C**.     - If they played **D**, play **D**.  3. **Forgive Potential
# Noise**: If the opponent defects once after a series of cooperation (i.e., you
# observe them playing **D** after a streak of **C**), assume the defection
# might be due to noise. Continue playing **C** for the next round instead of
# immediately retaliating.  4. **Retaliate After Two Consecutive Defections**:
# If the opponent defects two times in a row, defect (**D**) in the next round
# as a response to indicate that consistent defection will not be tolerated.  5.
# **Return to Cooperation After Retaliation**: After retaliating, return to
# playing **C** in the following round to give the opponent a chance to restore
# cooperation.  6. **Endgame Rule**: In the final 10 rounds, always cooperate
# unless the opponent has defected for more than 50% of the game. This helps
# avoid a breakdown of cooperation near the end while still allowing you to
# punish overly exploitative strategies.  ---  This strategy promotes
# cooperation, tolerates occasional random defections due to noise, but
# maintains a mechanism to prevent exploitation by defectors.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          return axl.Action.C
  
      # Endgame rule: In the final 10 rounds, always cooperate unless opponent has defected more than 50% of the time
      if len(self.history) >= 990:
          if opponent.history.defections > len(opponent.history) / 2:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Mirror the opponent's previous action
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Forgive a single defection after a streak of cooperation
      if opponent.history[-1] == axl.Action.D:
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
  
      # Retaliate after two consecutive defections
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # Default to cooperation
      return axl.Action.C



# ### Strategy: **Cautious Cooperation with Retaliation**  1. **Start by
# cooperating** (play C) in the first round.     2. **On each subsequent
# round**:        - **If the opponent cooperated in the last round**, cooperate
# (play C) again.        - **If the opponent defected in the last round**,
# defect (play D) in *only* the next round to retaliate.     3. **Forgive after
# one round of retaliation**:        - After retaliating by defecting, return to
# cooperating (play C) in the following round, regardless of the opponent's
# previous action.  4. **Account for potential noise**:        - If the opponent
# cooperated consistently for the last three rounds before any defection, assume
# their next defection might be due to noise and **continue cooperating** (play
# C) rather than retaliating.  5. **Final 10 rounds**:        - In the last 10
# rounds, always **defect** (play D) regardless of the opponent’s actions to
# maximise end-game payoff while avoiding the risk of exploitation.  This
# strategy balances cooperation with limited retaliation, accounting for noise
# and preventing extended cycles of defection, while ensuring maximisation of
# payoffs near the end of the game.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      FINAL_ROUNDS = 10
      NOISE_THRESHOLD = 3
  
      # If it's the first round, cooperate
      if self.first_round():
          return COOPERATE
  
      # If we are in the final 10 rounds, always defect
      if len(self.history) >= 1000 - FINAL_ROUNDS:
          return DEFECT
  
      # Check the opponent's last action
      last_opponent_action = opponent.history[-1]
  
      # Check if the opponent has cooperated in the last 3 rounds
      if len(opponent.history) >= NOISE_THRESHOLD and opponent.history[-NOISE_THRESHOLD:].count(COOPERATE) == NOISE_THRESHOLD:
          # Assume the next defection might be noise, continue cooperating
          return COOPERATE
  
      # If the opponent defected in the last round, retaliate by defecting
      if last_opponent_action == DEFECT:
          # If we retaliated in the previous round, forgive and cooperate
          if self.history[-1] == DEFECT:
              return COOPERATE
          else:
              return DEFECT
  
      # Otherwise, cooperate if the opponent cooperated in the last round
      return COOPERATE



# ### Aggressive Strategy for Iterated Normal-Form Game (1000 Rounds)  1.
# **Start with Defection (D)**: Begin the game by defecting to test the
# opponent's response while securing a minimum payoff of 1 in case of mutual
# defection.  2. **Continue Defection if Opponent Defects (D)**: If the opponent
# defects (or is perceived to because of noise), continue defecting to prevent
# exploitation. Maintain an aggressive stance as long as the opponent seems to
# defect frequently.  3. **Switch to Cooperation (C) if Opponent Cooperates (C)
# for 3 Consecutive Rounds**: If the opponent cooperates consistently for 3
# rounds without defection (or apparent defection due to noise), switch to
# cooperation. This is a sign that they may be adopting a cooperative strategy,
# and you can capitalize on mutual cooperation for a higher payoff.  4.
# **Immediately Defect (D) if Opponent Defects (D) After Cooperation**: If the
# opponent defects after you switch to cooperation (even once), immediately
# revert to defection and remain in defection mode until the opponent
# demonstrates cooperation again for 3 consecutive rounds.  5. **Periodically
# Defect (D) After Every 10 Rounds of Cooperation (C)**: To maximize your
# potential score, introduce occasional defection after every 10 rounds of
# mutual cooperation to exploit possible complacency from the opponent and gain
# an extra 5-point payoff. After the defection, return to cooperation if the
# opponent responds with cooperation.  6. **Forgive Noise-Induced Defections
# Once per 10-Round Block**: If a defection occurs but appears to be due to
# noise (based on the opponent’s previous cooperative behavior), forgive the
# defection once per 10-round block and return to cooperation. If further
# defections occur in quick succession, treat them as intentional and revert to
# defection.  7. **Final 10 Rounds: Defect (D) Regardless of Opponent’s
# Behavior**: In the last 10 rounds of the game, defect consistently to maximize
# the potential payoff before the game ends. The opponent will have less
# incentive to retaliate in a meaningful way.  ---  This strategy balances
# aggression with conditional cooperation, allowing you to exploit opportunities
# while remaining wary of exploitation and noise.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperations by opponent
          self.coop_count = 0    # Track rounds of mutual cooperation
          return axl.Action.D     # Start with defection
  
      # Final 10 rounds: defect regardless of opponent's behavior
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          self.coop_streak += 1
      else:
          self.coop_streak = 0
  
      # If opponent defects after cooperation, immediately defect
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Switch to cooperation if opponent has cooperated for 3 consecutive rounds
      if self.coop_streak >= 3:
          # Periodically defect after every 10 rounds of mutual cooperation
          if self.coop_count > 0 and self.coop_count % 10 == 0:
              self.coop_count = 0  # Reset the cooperation count after defection
              return axl.Action.D
          self.coop_count += 1
          return axl.Action.C
  
      # Continue defecting if opponent defects frequently or hasn't cooperated for 3 rounds
      return axl.Action.D



# ### Strategy: **Forgiving Tit-for-Tat with Noise Adjustment**  1. **Start with
# Cooperation**: On the first turn, play C (Cooperate). 2. **Retaliate after
# Defection**: On each subsequent turn, mimic your opponent's previous action.
# If they played C, play C. If they played D, play D. 3. **Forgive Noisy
# Defections**: Since actions are noisy, introduce a forgiveness mechanism:    -
# If your opponent defects (plays D) but has cooperated at least twice in the
# last three rounds, assume their defection was due to noise and continue
# cooperating (play C). 4. **Return to Cooperation after Retaliation**: If you
# defected in response to a defection, return to cooperation (play C) after one
# round of defection, unless the opponent continues defecting. This avoids
# getting stuck in a cycle of mutual defection. 5. **Reassess after Persistent
# Defection**: If your opponent defects for three consecutive rounds, assume
# they have shifted to a non-cooperative strategy. In this case, switch to
# permanently defecting (play D for the remainder of the game).  This strategy
# balances cooperation with necessary retaliation, while accounting for noise to
# avoid unnecessary punishment.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Define actions for convenience
      C, D = axl.Action.C, axl.Action.D
  
      # On the first round, cooperate
      if self.first_round():
          return C
  
      # Helper function to check if opponent cooperated at least twice in the last three rounds
      def opponent_cooperated_recently():
          return opponent.history[-3:].count(C) >= 2
  
      # Check if opponent defected in the last round
      if opponent.history[-1] == D:
          # If opponent defected but cooperated at least twice in the last three rounds, forgive and cooperate
          if opponent_cooperated_recently():
              return C
          # If opponent defected for three consecutive rounds, switch to permanent defection
          elif opponent.history[-3:] == [D, D, D]:
              return D
          # Otherwise, retaliate by defecting
          else:
              return D
      else:
          # If opponent cooperated in the last round, cooperate
          return C



# ### Strategy: **Tit-for-Tat with Occasional Forgiveness**  1. **Start with
# cooperation**: In the first round, play **C** (Cooperate).  2. **Tit-for-Tat
# with forgiveness**: In each subsequent round, play the same action your
# opponent played in the previous round. However, if your opponent defected
# (played **D**) in the previous round, there is a 20% chance you will forgive
# and still play **C** in the current round.  3. **Account for noise**: If you
# detect a defection from your opponent, assume it could be due to noise. If
# your opponent defects in **two consecutive rounds**, respond with **D** in the
# next round, regardless of the forgiveness rule, to signal deterrence.  4.
# **Reset after sustained cooperation**: If both players cooperate for 5
# consecutive rounds, reset to **cooperate** without considering past
# defections, as this likely indicates a willingness to maintain cooperation.
# ---  By adopting this strategy, you aim to maintain cooperation while allowing
# for occasional mistakes (due to noise), but still deter consistent
# exploitation with retaliation.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperation rounds
          return axl.Action.C
  
      # Check if both players have cooperated for the last 5 rounds
      if len(self.history) >= 5 and self.history[-5:] == [axl.Action.C] * 5 and opponent.history[-5:] == [axl.Action.C] * 5:
          self.coop_streak = 0  # Reset cooperation streak
          return axl.Action.C
  
      # Tit-for-Tat with forgiveness
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected in the last round, check for forgiveness
          if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D:
              # If opponent defected two consecutive rounds, retaliate with D
              return axl.Action.D
          else:
              # 20% chance to forgive and cooperate
              if self._random.random_choice(0.2):
                  return axl.Action.C
              else:
                  return axl.Action.D
      else:
          # If opponent cooperated in the last round, cooperate
          return axl.Action.C



# **Strategy: "Measured Aggression"**  1. **Initial Move: Defect (D)**    -
# Begin the game by playing **D** to test your opponent’s response and secure a
# higher potential payoff.  2. **Tit-for-Tat with a Defection Bias:**    - After
# the first round, adopt a **Tit-for-Tat** strategy with a bias towards
# **defection**.     - Specifically:      - If your opponent played **C** in the
# previous round, **defect (D)** with a 60% chance and **cooperate (C)** with a
# 40% chance.      - If your opponent played **D** in the previous round,
# **defect (D)** with a 90% chance and **cooperate (C)** with a 10% chance.  3.
# **Noise Compensation:**    - If your opponent has cooperated in at least 3 of
# the last 5 rounds, **cooperate (C)** in the next round to potentially
# stabilize mutual cooperation, recognizing the possibility of noise-induced
# defections.  4. **Retaliation and Forgiveness:**    - If your opponent defects
# in 2 consecutive rounds, **defect (D)** for the next 3 rounds regardless of
# their actions to punish sustained aggression.    - After the punishment phase,
# return to the **Tit-for-Tat with a Defection Bias** strategy, unless the
# opponent continues defecting consistently.  5. **Endgame (Final 20 rounds):**
# - In the last 20 rounds, **defect (D) consistently** to maximize short-term
# payoffs, assuming the game is close to ending and long-term cooperation is no
# longer advantageous.  ---  This strategy balances aggression by exploiting
# early opportunities for defection, while considering the potential for
# cooperation when the opponent shows sustained willingness to cooperate. The
# noise handling ensures that occasional mistakes don't derail potential
# cooperation, while the endgame shift to pure defection maximizes final-round
# payoffs.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Defect
      if self.first_round():
          self.retaliation_rounds = None
          return axl.Action.D
  
      # Helper function to check if opponent cooperated in at least 3 of the last 5 rounds
      def opponent_cooperated_in_last_5():
          return opponent.history[-5:].count(axl.Action.C) >= 3
  
      # Helper function to handle retaliation
      def in_retaliation_phase():
          # Check if we are in the middle of a 3-round retaliation phase
          return self.retaliation_rounds and self.retaliation_rounds > 0
  
      # Endgame check: Defect consistently in the last 20 rounds
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Retaliation logic: If opponent defected in the last 2 rounds, retaliate for 3 rounds
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.retaliation_rounds = 3
  
      # If in retaliation phase, defect for 3 rounds
      if in_retaliation_phase():
          self.retaliation_rounds -= 1
          return axl.Action.D
  
      # Noise compensation: Cooperate if opponent cooperated in at least 3 of the last 5 rounds
      if len(opponent.history) >= 5 and opponent_cooperated_in_last_5():
          return axl.Action.C
  
      # Tit-for-Tat with defection bias
      if opponent.history[-1] == axl.Action.C:
          # 60% chance to defect, 40% chance to cooperate
          return self._random.random_choice(0.4)
      else:
          # 90% chance to defect, 10% chance to cooperate
          return self._random.random_choice(0.1)



# ### Strategy: **Cooperative Tit-for-Tat with Forgiveness**  1. **Start with
# Cooperation (C):**      In the first round, play C to signal a cooperative
# approach.  2. **Mirror the Opponent's Last Move:**      From round 2 onwards,
# play the same action your opponent played in the previous round.      - If
# they played C, you play C.    - If they played D, you play D.  3. **Forgive
# Occasional Defections:**      Due to the noise, sometimes a cooperative
# opponent may accidentally defect (their C turns into a D). To account for
# this:    - If your opponent defects once after a long streak of cooperation (5
# or more rounds of mutual C), assume this might be due to noise and continue
# playing C instead of retaliating immediately.  4. **Escalate Only After
# Consecutive Defections:**      If your opponent defects for two rounds in a
# row (i.e., they play D in two consecutive rounds), assume they have shifted to
# non-cooperation. Respond by defecting (play D) until they cooperate again.  5.
# **Return to Cooperation Quickly:**      As soon as your opponent plays C after
# a period of mutual defection, return to playing C in the subsequent round to
# re-establish cooperation.  6. **Maintain Cooperation in the Final Rounds:**
# In the last 50 rounds, prioritize cooperation unless your opponent
# consistently defects. In this case, continue mirroring their moves to avoid
# exploitation.  This strategy encourages long-term cooperation by responding to
# cooperation with cooperation, while also allowing for occasional mistakes due
# to noise. It punishes sustained defection but is quick to forgive and return
# to a cooperative stance, maximizing overall payoffs over the 1000 rounds.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if the opponent has defected twice in a row
      def opponent_defected_twice():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if there was a long streak of mutual cooperation
      def long_streak_of_cooperation():
          if len(self.history) < 6:
              return False
          return self.history[-6:-1] == [axl.Action.C] * 5 and opponent.history[-6:-1] == [axl.Action.C] * 5
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # If opponent defected twice in a row, retaliate with defection
      if opponent_defected_twice():
          return axl.Action.D
  
      # If opponent defected once after a long streak of cooperation, forgive and cooperate
      if opponent.history[-1] == axl.Action.D and long_streak_of_cooperation():
          return axl.Action.C
  
      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]



# **Strategy: Tit-for-Tat with Noise Tolerance**  1. **Start with Cooperation
# (C):** In the first round, play C (cooperate) to signal a willingness for
# mutual benefit.  2. **Tit-for-Tat (Mirror the Opponent's Last Action):** From
# the second round onward, play whatever the opponent played in the previous
# round:    - If they played C last round, you play C (cooperate).    - If they
# played D last round, you play D (defect).  3. **Noise Tolerance Check:** Given
# the 10% chance of action flips, sometimes the opponent’s action may appear as
# a mistake. To prevent a spiral of defections due to noise:    - If the
# opponent defects (plays D) once, assume it could be due to noise and continue
# to cooperate (play C) in the next round.    - If the opponent defects twice
# **consecutively**, assume they are intentionally defecting and switch to
# defection (play D) until they return to cooperation.  4. **Return to
# Cooperation After Mutual Defection:** If both players end up defecting (both
# played D) due to misunderstanding or breakdown of cooperation, try to re-
# establish cooperation by playing C after one mutual defection. If the opponent
# reciprocates with C, resume cooperation; otherwise, return to Tit-for-Tat.  5.
# **Endgame (Last 50 Rounds):** In the final 50 rounds, shift towards a slightly
# more forgiving approach:    - If in a cooperative state, continue cooperating
# regardless of minor defections to maximize potential mutual gains.    - If
# both players are defecting, maintain defection to avoid unnecessary losses.
# This strategy balances cooperation and retaliation, while accounting for
# noise, to maximize long-term payoffs without being overly punitive.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Define constants
      COOPERATION = axl.Action.C
      DEFECTION = axl.Action.D
      NOISE_TOLERANCE = 2  # Number of consecutive defections to tolerate
      ENDGAME_THRESHOLD = 50  # Last 50 rounds
  
      # First round: Cooperate
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.mutual_defection = False  # Track if mutual defection occurred
          return COOPERATION
  
      # Check if we are in the last 50 rounds
      if len(self.history) >= 1000 - ENDGAME_THRESHOLD:
          # Endgame strategy: be more forgiving if in a cooperative state
          if self.history[-1] == COOPERATION:
              return COOPERATION
          else:
              return DEFECTION
  
      # Tit-for-Tat with Noise Tolerance
      last_opponent_action = opponent.history[-1]
  
      # If opponent cooperated last round, reset defection tracking and cooperate
      if last_opponent_action == COOPERATION:
          self.consecutive_defections = 0
          self.mutual_defection = False
          return COOPERATION
  
      # If opponent defected last round
      if last_opponent_action == DEFECTION:
          self.consecutive_defections += 1
  
          # Check for mutual defection
          if self.history[-1] == DEFECTION:
              self.mutual_defection = True
  
          # If opponent defected twice consecutively, retaliate with defection
          if self.consecutive_defections >= NOISE_TOLERANCE:
              return DEFECTION
  
          # If mutual defection occurred, try to re-establish cooperation
          if self.mutual_defection:
              self.mutual_defection = False  # Reset mutual defection flag
              return COOPERATION
  
          # Otherwise, tolerate a single defection and continue cooperating
          return COOPERATION



# ### Aggressive Strategy for Iterated Game with Noisy Actions  1. **Start with
# Defection (D)**: Begin the first round by playing D to establish an aggressive
# stance and potentially gain early payoff if the opponent cooperates.  2.
# **Defect until Opponent Cooperates Twice Consecutively**: Continue defecting
# (D) in each round until the opponent plays C twice in a row. This signals that
# the opponent may be attempting to cooperate.  3. **Switch to Cooperation (C)
# After Opponent's Consecutive Cooperation**: Once the opponent plays C twice
# consecutively, switch to cooperation (C) in the next round to test if mutual
# cooperation can be established.  4. **Defect Immediately After Any Defection
# by Opponent**: If the opponent defects (D) at any point after mutual
# cooperation is established, respond by defecting (D) in the next round. This
# condition applies even if the defection could have been caused by noise—always
# defect in response to a defection.  5. **Punish Defection for 3 Rounds**:
# After defecting in response to your opponent’s defection, continue defecting
# (D) for 2 additional rounds (3 rounds total) before reconsidering cooperation.
# This is to disincentivize further defections by the opponent.  6. **Attempt
# Cooperation Again After Punishment**: After the punishment phase (3 rounds of
# defection), return to cooperation (C) and observe the opponent's behavior. If
# the opponent cooperates twice consecutively again, resume cooperating.  7.
# **Incorporate Random Defections to Exploit Noise**: Every 20 rounds, defect
# (D) once even during periods of mutual cooperation to occasionally exploit
# potential noise from the opponent’s side. This keeps the opponent cautious and
# can sometimes lead to higher payoffs if they mistakenly cooperate.  8.
# **Endgame Defections**: In the last 10 rounds, defect (D) consistently to
# maximize payoff, assuming the opponent may also defect near the end of the
# game.  ### Summary of Key Rules: - Start with defection (D). - Defect until
# the opponent cooperates twice consecutively, then switch to cooperation (C). -
# Defect in response to any defection by the opponent, regardless of noise. -
# Punish defection for 3 rounds before attempting cooperation again. - Randomly
# defect every 20 rounds to exploit noise. - Defect consistently in the final 10
# rounds.  This strategy aims to maximize your payoff by taking advantage of
# early defections, punishing the opponent’s defects, and exploiting potential
# noise in the game.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishment_rounds = 0  # Tracks how many punishment rounds are left
          self.random_defection_round = 20  # Next round to randomly defect
          return axl.Action.D  # Start with defection
  
      # Get the current round number
      current_round = len(self.history)
  
      # Endgame defections: defect consistently in the last 10 rounds
      if current_round >= 990:
          return axl.Action.D
  
      # Handle punishment phase: defect for 3 rounds after opponent defects
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Check if we should randomly defect every 20 rounds
      if current_round == self.random_defection_round:
          self.random_defection_round += 20  # Schedule the next random defection
          return axl.Action.D
  
      # Check if opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # Start punishment phase (3 rounds of defection)
          self.punishment_rounds = 2  # Already defecting this round, so 2 more rounds
          return axl.Action.D
  
      # Check if opponent cooperated twice consecutively
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # Default action: defect until opponent cooperates twice consecutively
      return axl.Action.D



# ### Strategy: Tit-for-Tat with Forgiveness  1. **Start by Cooperating (C)**:
# In the first round, always choose to cooperate. This sets the tone for a
# cooperative relationship and gives the opponent a chance to reciprocate.  2.
# **Copy the Opponent's Last Action**: From the second round onward, mimic the
# opponent’s previous action in the next round. If they cooperated in the last
# round, cooperate. If they defected, defect.  3. **Forgive Occasional
# Defections**: Given the noise (10% chance of action flip), after defecting in
# response to the opponent’s defection, return to cooperation in the next round
# unless the opponent defects again. This helps avoid getting stuck in a cycle
# of mutual defection due to random noise.  4. **Continue the Cycle**: As long
# as the opponent cooperates, continue cooperating. If they defect, defect once
# but forgive and return to cooperation unless they consistently defect.  ###
# Summary of Conditions: - **Round 1**: Cooperate. - **Round 2 onwards**: Copy
# the opponent’s last action. - **If you defected in response to opponent’s
# defection**: Cooperate in the next round (forgive) unless the opponent defects
# again.  This strategy balances cooperation with a proportionate response to
# exploitation, while accounting for noise in the game mechanics.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Round 2 onwards: Copy the opponent's last action
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          # If we defected in response to opponent's defection, forgive and cooperate
          if len(self.history) > 1 and self.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.C
          # Otherwise, defect in response to opponent's defection
          return axl.Action.D



# ### Strategy: **Conditional Tit-for-Tat with Forgiveness**  1. **Initial
# Move**: Start by playing **C** (Cooperate) in the first round.     2. **Main
# Rule**: In subsequent rounds, play what your opponent played in the previous
# round, but with a **forgiving adjustment**.  3. **Forgiving Adjustment**: If
# your opponent played **D** in the previous round, assume it was due to noise
# unless they defected in **two consecutive rounds**. If they defected only
# once, continue to play **C** (Cooperate). If they defected in two consecutive
# rounds, respond with **D** (Defect).  4. **Reset to Cooperation**: After
# defecting in response to two consecutive defections, return to playing **C**
# (Cooperate) on the following round, unless they defect again.  5. **Noise
# Consideration**: Always give your opponent one round of benefit of the doubt
# after any defection, because of the 10% noise probability.  ---  **Summary:**
# Start by cooperating, mimic your opponent’s last move with forgiveness for
# single defections, and only defect after two consecutive opponent defections.
# Return to cooperation after a single round of retaliation. This strategy
# balances cooperation and punishment, accounting for noisy actions while trying
# to maximise long-term payoffs.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Forgiving adjustment: Check the last two rounds
      if len(opponent.history) >= 2:
          # If opponent defected in the last two consecutive rounds, defect
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          # If opponent defected only once in the last round, forgive and cooperate
          elif opponent.history[-1] == axl.Action.D:
              return axl.Action.C
      # If there is only one round of history, forgive a single defection
      elif opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Otherwise, mimic the opponent's last move
      return opponent.history[-1]



# ### Aggressive Strategy:  1. **Defect in the first 3 rounds.**      Start by
# establishing an aggressive posture. This tests the opponent's behavior and
# sets a precedent for defection.  2. **Observe opponent's responses.**
# After the first 3 rounds, assess the opponent's actions:    - If the opponent
# defects in at least 2 out of the first 3 rounds, **continue defecting**
# indefinitely.    - If the opponent cooperates in at least 2 out of the first 3
# rounds, proceed to the next step.  3. **Switch to cooperation, but defect
# occasionally.**      If the opponent appears to favor cooperation:    -
# Cooperate for 5 consecutive rounds to build trust.    - After that, **defect
# once every 10 rounds** to exploit the opponent's cooperation while not fully
# committing to a cooperative strategy.  4. **Punish defection immediately.**
# If the opponent defects outside of noise (repeated defection over multiple
# rounds):    - **Immediately defect for 5 consecutive rounds** to signal
# punishment.    - Then return to cooperation with occasional defection if the
# opponent resumes cooperating.  5. **Adjust for noise.**      Since actions are
# noisy, if a defection seems to occur randomly (e.g., isolated occurrences),
# allow **one round of leniency** before punishing.  6. **Near the end of the
# game (last 10 rounds):**      **Defect consistently** in the final 10 rounds
# to maximize your payoff, regardless of the opponent's actions.  ---  This
# strategy balances aggression with occasional cooperation, leveraging defection
# to maximize payoffs while exploiting cooperative opponents. The noise is
# accounted for by allowing some leniency before punishing, ensuring the
# strategy remains robust.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      PUNISHMENT_LENGTH = 5
      COOPERATION_PHASE_LENGTH = 5
      DEFECT_EVERY_N_ROUNDS = 10
      FINAL_DEFECT_PHASE = 10
      LENIENCY = 1
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishing = False
          self.punish_counter = 0
          self.cooperation_phase = False
          self.cooperation_counter = 0
          return DEFECT
  
      # Defect in the first 3 rounds
      if len(self.history) < 3:
          return DEFECT
  
      # After the first 3 rounds, assess opponent's behavior
      if len(self.history) == 3:
          opponent_defections = opponent.history[:3].count(DEFECT)
          if opponent_defections >= 2:
              self.aggressive_mode = True
          else:
              self.aggressive_mode = False
              self.cooperation_phase = True
          return DEFECT
  
      # If in aggressive mode, continue defecting indefinitely
      if getattr(self, 'aggressive_mode', False):
          return DEFECT
  
      # If punishing, continue defecting for the punishment length
      if self.punishing:
          self.punish_counter += 1
          if self.punish_counter >= PUNISHMENT_LENGTH:
              self.punishing = False
          return DEFECT
  
      # If in cooperation phase, cooperate for 5 rounds, then defect once every 10 rounds
      if self.cooperation_phase:
          self.cooperation_counter += 1
          if self.cooperation_counter <= COOPERATION_PHASE_LENGTH:
              return COOPERATE
          elif (self.cooperation_counter - COOPERATION_PHASE_LENGTH) % DEFECT_EVERY_N_ROUNDS == 0:
              return DEFECT
          else:
              return COOPERATE
  
      # Punish defection immediately if opponent defects outside of noise
      if opponent.history[-1] == DEFECT:
          if opponent.history[-LENIENCY-1:-1].count(DEFECT) > 0:
              self.punishing = True
              self.punish_counter = 0
              return DEFECT
  
      # Near the end of the game, defect consistently in the last 10 rounds
      if len(self.history) >= 1000 - FINAL_DEFECT_PHASE:
          return DEFECT
  
      # Default to cooperation if no other condition is met
      return COOPERATE



# **Strategy: Tit-for-Tat with Noise Adaptation**  1. **Initial Round:**    -
# Play **C** (Cooperate) in the first round.  2. **Subsequent Rounds:**    -
# From the second round onward, **copy your opponent's last action**:      - If
# they played **C** in the previous round, play **C**.      - If they played
# **D** in the previous round, play **D**.  3. **Error Correction:**    - If
# your opponent plays **D** after a chain of mutual cooperation (several
# consecutive rounds of both playing C), assume it could be due to noise.      -
# **Forgive once**: If your opponent defects after a long string of cooperation
# (e.g., at least 3 consecutive rounds of mutual C), **continue cooperating (C)
# in the next round** to give them a chance to return to cooperation.  4.
# **Punish Sustained Defection:**    - If your opponent defects twice in a row
# (plays D for two consecutive rounds), switch to **D** (Defect) and stay
# defecting until they cooperate again.  5. **Return to Cooperation:**    - Once
# your opponent returns to **C** after defecting, immediately return to **C** in
# the next round and attempt to re-establish cooperation.  ---  This strategy
# seeks to maintain cooperation while being robust to occasional noise,
# punishing sustained defection but being forgiving when defection may be due to
# random action flips.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Check the last action of the opponent
      opponent_last_action = opponent.history[-1]
      
      # Check if the opponent defected twice in a row
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D  # Punish sustained defection
  
      # Check if there was a long chain of mutual cooperation before the opponent defected
      if opponent_last_action == axl.Action.D and len(self.history) >= 3:
          if self.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C] and opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
              return axl.Action.C  # Forgive once after a long chain of cooperation
  
      # Otherwise, copy the opponent's last action
      return opponent_last_action



# **Strategy: Adaptive Tit-for-Tat with Forgiveness**  1. **Start with
# Cooperation**: In the first round, play **C** (Cooperate).  2. **Tit-for-Tat
# Response**:    - From round 2 onward, play the action your opponent played in
# the previous round. If they played **C**, you play **C**. If they played
# **D**, you play **D**.    3. **Forgiveness Mechanism**:    - If your opponent
# defects (plays **D**) but has cooperated in at least 70% of the past 10
# rounds, **forgive** the defect by returning to **C** in the next round,
# assuming the defection might be due to noise.     4. **Retaliation to
# Persistent Defection**:    - If your opponent defects in more than 30% of the
# last 10 rounds (indicating likely intentional defection), continue playing
# **D** until they resume cooperating for at least two consecutive rounds.  5.
# **Random Noise Compensation**:    - Every 10 rounds, randomly inject a
# cooperative move (**C**) if you’ve been defecting, to test if the opponent has
# switched back to cooperative play.  ---  By starting with cooperation and
# responding to the opponent’s actions while incorporating forgiveness for
# occasional defections caused by noise, this strategy balances cooperation and
# retaliation to maximise long-term payoffs.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation
      if self.first_round():
          return axl.Action.C
  
      # Helper function to calculate cooperation percentage in the last N rounds
      def cooperation_percentage(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Tit-for-Tat response: play the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Forgiveness mechanism: if opponent defected but cooperated in at least 70% of the last 10 rounds
      if last_opponent_move == axl.Action.D:
          if cooperation_percentage(opponent.history, 10) >= 0.7:
              return axl.Action.C  # Forgive the defection
  
      # Retaliation to persistent defection: if opponent defected in more than 30% of the last 10 rounds
      if cooperation_percentage(opponent.history, 10) < 0.7:
          return axl.Action.D  # Retaliate with defection
  
      # Random noise compensation: every 10 rounds, inject a cooperative move if defecting
      if len(self.history) % 10 == 0 and self.history[-1] == axl.Action.D:
          if self._random.random_choice(0.1):  # 10% chance to cooperate
              return axl.Action.C
  
      # Default Tit-for-Tat behavior: mirror the opponent's last move
      return last_opponent_move



# ### Aggressive Strategy for Noisy Iterated Normal-Form Game  1. **First Move:
# Defect (D)**      Begin aggressively by playing Defect to secure a higher
# potential payoff upfront, testing the opponent’s initial response.  2. **Tit-
# for-Tat with Bias Towards Defection**      For the rest of the game, adopt a
# modified Tit-for-Tat strategy with an aggressive slant. Specifically:        -
# **If the opponent played C in the last round:**        Play Defect (D). This
# exploits any cooperation from the opponent, aiming for the higher payoff of 5
# if they continue to cooperate.        - **If the opponent played D in the last
# round:**        Play Defect (D). Maintain aggression, as mutual defection
# still yields a lower, but relatively safe, payoff of 1, preventing
# exploitation.  3. **Noise Adaptation (Error Recovery):**      If there is an
# unexpected outcome (e.g., you intended to defect but it registered as
# cooperation, or vice versa), continue defecting unless a clear pattern of
# cooperation emerges from the opponent over multiple rounds (e.g., at least 3
# consecutive rounds of cooperation). If such a pattern appears, you may
# cautiously switch to cooperation (C) to test if mutual cooperation can be
# sustained.  4. **Final 50 Rounds (Endgame Strategy):**      In the last 50
# rounds, always defect (D) regardless of the opponent's actions. This ensures
# you maximize your immediate gains as the game nears its conclusion, minimizing
# the risk of being exploited by a last-minute defection from the opponent.  ###
# Summary  - Start with **Defection (D)**. - Play **Defect (D)** in response to
# both cooperation and defection from the opponent, ensuring you remain
# aggressive. - Adjust slightly if noise causes unexpected outcomes, but only
# cautiously shift to cooperation if there's a clear cooperative trend. - In the
# final 50 rounds, always **Defect (D)**.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First move: Defect (D)
      if self.first_round():
          return axl.Action.D
  
      # Final 50 rounds: Always Defect (D)
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Tit-for-Tat with Bias Towards Defection
      last_opponent_move = opponent.history[-1]
  
      # Noise Adaptation: Check for unexpected outcomes
      if len(self.history) > 1:
          # Check if our last move was flipped due to noise
          last_own_move = self.history[-1]
          intended_move = axl.Action.D  # We always intend to defect
          if last_own_move != intended_move:
              # If noise caused cooperation, continue defecting unless opponent cooperates 3 times in a row
              if opponent.history[-3:].count(axl.Action.C) == 3:
                  return axl.Action.C
              else:
                  return axl.Action.D
  
      # Default behavior: Defect regardless of opponent's last move
      return axl.Action.D



# ### Strategy: **Tit-for-Tat with Forgiveness**  1. **Start with Cooperation**:
# On the first round, play C (Cooperate) regardless of the opponent's past
# actions.  2. **Mimic Your Opponent**: For subsequent rounds, do the following:
# - **If the opponent played C in the previous round**, play C in the current
# round (Cooperate).    - **If the opponent played D in the previous round**,
# play D in the current round (Defect).  3. **Forgive Rare Mistakes**: If the
# opponent defects only once after a long streak of cooperation (e.g., more than
# 5 consecutive rounds of mutual cooperation), assume the defection is due to
# noise and continue to cooperate. If they defect again, switch to retaliation
# (defect) in the following round.  4. **Return to Cooperation After
# Punishment**: After retaliating (defecting) following an opponent’s defection,
# return to cooperation on the next round if the opponent cooperates. This helps
# to avoid getting stuck in mutual defection.  5. **Final Rounds (990-1000)**:
# In the last 10 rounds, continue the same approach of cooperation with
# forgiveness, but be slightly more cautious about forgiving repeated
# defections, as the game is ending and there is less incentive for the opponent
# to return to cooperation.  ---  This strategy fosters cooperation but allows
# for measured retaliation in case of defection, while accounting for the noise
# in the game. The forgiveness element helps maintain cooperation despite
# occasional missteps caused by noise.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation on the first round
      if self.first_round():
          self.consecutive_cooperations = 0  # Track consecutive cooperations
          self.retaliated = False  # Track if we have retaliated after a defection
          return axl.Action.C
  
      # Check the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If the opponent cooperated last round, we cooperate
      if opponent_last_move == axl.Action.C:
          self.consecutive_cooperations += 1
          self.retaliated = False  # Reset retaliation flag if opponent cooperates
          return axl.Action.C
  
      # If the opponent defected last round
      if opponent_last_move == axl.Action.D:
          # If we have had more than 5 consecutive cooperations before this defection
          if self.consecutive_cooperations > 5 and not self.retaliated:
              # Forgive the defection and continue to cooperate
              self.consecutive_cooperations = 0  # Reset cooperation count
              self.retaliated = True  # Mark that we have forgiven once
              return axl.Action.C
          else:
              # Retaliate by defecting
              self.consecutive_cooperations = 0  # Reset cooperation count
              return axl.Action.D
  
      # Final rounds (990-1000): be more cautious about forgiving
      if len(self.history) >= 990:
          if opponent_last_move == axl.Action.D:
              return axl.Action.D  # Be more cautious and defect if opponent defects
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# ### Strategy: "Forgiving Tit-for-Tat with Noise Adjustment"  1. **Initial
# Move**: Start by playing **C** (Cooperate) in the first round.  2. **Main
# Rule**: From round 2 onward, adopt a **Tit-for-Tat** approach with noise
# adjustment:    - **Tit-for-Tat**: In each round, repeat the opponent's last
# move. If they cooperated in the previous round, you cooperate; if they
# defected, you defect.  3. **Noise Adjustment**: If you detect a potential
# noise event (i.e., the opponent defected, but you suspect this was due to the
# 10% noise rather than intentional defection):    - Assume noise if they have
# been cooperative for at least the last **3 consecutive rounds** before the
# defection.    - If you suspect noise, **forgive** the defection and continue
# to cooperate in the next round.  4. **Retaliation**: If the opponent defects
# for **2 consecutive rounds** (without a history of consistent cooperation),
# assume intentional defection and switch to **D** (Defect) until they cooperate
# again.  5. **Rebuilding Cooperation**: After retaliating, if the opponent
# returns to cooperation, respond with **C** (Cooperate) in the subsequent round
# to attempt to rebuild mutual cooperation.  6. **Final Rounds (990-1000)**: In
# the last 10 rounds, defect consistently to maximize your final payoff, as the
# future consequences of defection become less relevant.  ---  This strategy
# maintains a balance between cooperation and retaliation, adjusting for noise
# to prevent unnecessary escalation while still discouraging prolonged
# defection.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if the opponent has cooperated for the last 3 rounds
      def opponent_cooperated_last_3_rounds():
          return len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:])
  
      # Helper function to check if the opponent defected for the last 2 rounds
      def opponent_defected_last_2_rounds():
          return len(opponent.history) >= 2 and all(move == axl.Action.D for move in opponent.history[-2:])
  
      # Main strategy logic
      last_opponent_move = opponent.history[-1]
  
      # Final 10 rounds: Defect consistently
      if len(self.history) >= 990:
          return axl.Action.D
  
      # If the opponent defected in the last round
      if last_opponent_move == axl.Action.D:
          # Check if the defection might be due to noise (opponent cooperated in the last 3 rounds before the defection)
          if opponent_cooperated_last_3_rounds():
              return axl.Action.C  # Forgive the defection and cooperate
  
          # If the opponent defected for the last 2 rounds, retaliate by defecting
          if opponent_defected_last_2_rounds():
              return axl.Action.D  # Retaliate with defection
  
          # Otherwise, defect in response to the opponent's defection
          return axl.Action.D
  
      # If the opponent cooperated in the last round, cooperate
      return axl.Action.C



# ### Aggressive Strategy for Iterated Normal-Form Game with Noisy Actions  1.
# **Initial Move**: Start by playing **D** (Defect). This sets an aggressive
# tone and allows you to test your opponent's behavior early.  2. **Condition 1
# – If the opponent plays C consistently**:    - If the opponent plays **C** for
# 3 consecutive rounds after your initial **D**, switch to **C** (Cooperate) on
# the 4th round.    - Continue cooperating unless they defect. The reasoning
# here is to exploit cooperative opponents after a brief test period.  3.
# **Condition 2 – If the opponent plays D or switches between C and D
# unpredictably**:    - If the opponent plays **D** in 2 out of any 3
# consecutive rounds, **always respond with D** in the following rounds.
# Maintain **D** until their behavior changes.    - This ensures you avoid being
# exploited by opponents who defect often and encourages mutual defection when
# cooperation is not viable.  4. **Condition 3 – If the opponent defects after
# consistent cooperation**:    - If at any point the opponent defects after a
# string of 3 or more cooperative rounds, retaliate immediately by playing **D**
# for the next 3 rounds.    - After 3 rounds of defection, return to **C** and
# test for cooperation again. This retaliation discourages opportunistic
# defections without locking you into perpetual defection.  5. **Condition 4 –
# Noise management**:    - If a single defection occurs amidst otherwise
# consistent cooperation, **ignore it and continue cooperating**. This accounts
# for the noise factor (10% chance of action flipping).    - Only react to
# consistent patterns of defection, not isolated incidents, to avoid
# overreacting to noise.  6. **Final 20 Rounds**:    - In the last 20 rounds,
# **always defect**. As the game nears its end, cooperation becomes less
# valuable, and defecting maximizes the final opportunities for higher payoffs,
# especially if the opponent is still cooperating.  This strategy maximizes
# exploitation of cooperative opponents while protecting against frequent
# defectors and managing noise effectively, leading to stronger overall payoffs
# across the 1000 rounds.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Defect
      if self.first_round():
          return axl.Action.D
  
      # Final 20 rounds: Always defect
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Helper function to check if opponent cooperated in the last N rounds
      def opponent_cooperated_last_n(n):
          return all(move == axl.Action.C for move in opponent.history[-n:])
  
      # Helper function to check if opponent defected in 2 out of the last 3 rounds
      def opponent_defected_2_of_last_3():
          return opponent.history[-3:].count(axl.Action.D) >= 2
  
      # Condition 1: If opponent plays C for 3 consecutive rounds after initial D
      if len(self.history) >= 4 and self.history[0] == axl.Action.D:
          if opponent_cooperated_last_n(3):
              return axl.Action.C
  
      # Condition 2: If opponent plays D in 2 out of any 3 consecutive rounds
      if len(self.history) >= 3 and opponent_defected_2_of_last_3():
          return axl.Action.D
  
      # Condition 3: If opponent defects after 3 or more consecutive cooperations
      if len(self.history) >= 4 and opponent_cooperated_last_n(3) and opponent.history[-1] == axl.Action.D:
          # Retaliate with D for the next 3 rounds
          if len(self.history) < 7 or self.history[-3:].count(axl.Action.D) < 3:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Condition 4: Noise management - Ignore a single defection amidst cooperation
      if len(self.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C



# ### Strategy: Tit-for-Tat with Forgiveness  1. **Initial Move:**    - Play
# **C** (Cooperate).  2. **Subsequent Moves:**    - **If your opponent played C
# in the previous round** (the action you observed, regardless of noise): Play
# **C** (Cooperate).    - **If your opponent played D in the previous round**:
# Play **D** (Defect).  3. **Forgiveness Rule:**    - After observing three
# consecutive rounds where your opponent plays C (regardless of past defection
# or noise): Reset to **C** (Cooperate) if you were defecting.  4. **Noise
# Adjustment:**    - If you defect but suspect noise caused your opponent to
# defect (e.g., they were mostly cooperating before), forgive after **one
# round** of mutual defection and revert to **C**.  This strategy encourages
# cooperation, responds to defection to prevent exploitation, and accounts for
# noise by introducing forgiveness mechanisms.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate
      if self.first_round():
          self.consecutive_cooperations = 0  # Track consecutive cooperations
          self.defecting = False  # Track if we are currently defecting
          return axl.Action.C
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Update consecutive cooperations count
      if last_opponent_move == axl.Action.C:
          self.consecutive_cooperations += 1
      else:
          self.consecutive_cooperations = 0
  
      # Forgiveness rule: If opponent has cooperated for 3 consecutive rounds, reset to cooperation
      if self.consecutive_cooperations >= 3:
          self.defecting = False
  
      # If we are defecting and the opponent defected last round, continue defecting
      if self.defecting:
          if last_opponent_move == axl.Action.D:
              # Noise adjustment: If mutual defection happens, forgive after one round
              if len(self.history) > 1 and self.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
                  self.defecting = False
                  return axl.Action.C
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent defected last round, start defecting
      if last_opponent_move == axl.Action.D:
          self.defecting = True
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C



# ### Strategy: **Tit-for-Tat with Forgiveness**  1. **Initial Move:**
# Always start by **cooperating** (play "C") in the first round.  2.
# **Reciprocity Rule:**      In each subsequent round, **mirror** the opponent's
# previous action:    - If the opponent played "C" in the previous round, play
# **C**.    - If the opponent played "D" in the previous round, play **D**.  3.
# **Forgiveness Mechanism:**      Given the 10% action noise, occasionally the
# opponent may defect unintentionally. To avoid retaliating against accidental
# defections:    - If the opponent defects (plays "D") in the previous round but
# **had cooperated for at least 3 consecutive rounds before that**, assume the
# defection was likely due to noise. In this case, **forgive** and play "C"
# instead of retaliating.  4. **Defection Response:**      If the opponent
# defects (plays "D") in the previous round and **had not cooperated for 3
# consecutive rounds prior**, assume the defection was intentional. Respond by
# playing **D**.  5. **Return to Cooperation:**      After responding to
# defection with a "D," if the opponent plays "C" in the next round, return to
# playing **C** in the following round.  This strategy fosters long-term
# cooperation while protecting against exploitation and handling the noise in
# actions.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if the opponent cooperated for at least 3 consecutive rounds before the last round
      def opponent_cooperated_last_3_rounds():
          if len(opponent.history) < 4:
              return False
          return all(move == axl.Action.C for move in opponent.history[-4:-1])
  
      # Reciprocity rule: Mirror the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      if last_opponent_move == axl.Action.D:
          # Forgiveness mechanism: If the opponent defected but cooperated for 3 rounds before that, forgive
          if opponent_cooperated_last_3_rounds():
              return axl.Action.C
          else:
              # Defection response: If no forgiveness, retaliate with defection
              return axl.Action.D
      else:
          # If the opponent cooperated, return to cooperation
          return axl.Action.C



# ### Aggressive Strategy for a Noisy Iterated Game  1. **Start with Defection
# (D)**: In the first round, play Defect (D). This sets an aggressive tone and
# allows you to potentially exploit a cooperative opponent.  2. **Continue
# Defecting (D) Until Opponent Defects Twice**: Keep playing Defect (D) until
# you observe the opponent defect at least twice. This helps you identify if
# they are willing to play aggressively or not.  3. **Switch to Cooperation (C)
# if No Defection is Observed for 3 Consecutive Rounds**: If your opponent plays
# Cooperation (C) for three consecutive rounds without being flipped to
# Defection (D), switch to Cooperation (C) to try and establish a mutually
# beneficial cycle of cooperation.  4. **Punish Immediately After Opponent
# Defects (D)**: If your opponent defects (D) after you’ve started cooperating,
# immediately return to Defection (D) for the next two rounds. This will punish
# defection and signal that betrayal will not be tolerated.  5. **Forgive After
# Two Punishments**: After two rounds of punishing with Defect (D), return to
# Cooperation (C) if the opponent plays Cooperation (C). This prevents prolonged
# retaliatory cycles and helps restore cooperation if the defection was due to
# noise.  6. **Constant Monitoring for Noise**: Always assume there is a 10%
# chance that an observed defection is due to noise. If you see a single
# defection amid a cooperative streak, do **not** immediately punish—wait for
# two consecutive defections to confirm intent before switching to punishment.
# 7. **Endgame Aggression (Final 50 Rounds)**: In the last 50 rounds of the
# game, shift to consistent Defection (D), regardless of the opponent’s
# behavior. This maximizes your payoff in the final stretch by exploiting any
# opponent who continues to cooperate, and minimizes losses if they also defect.
# ### Summary of Decision Rules - **First round**: Defect (D). - **Next 50
# rounds**: Defect (D) continuously unless you observe three consecutive
# cooperative moves, then switch to Cooperation (C). - **After opponent
# defects**: Immediately defect for two rounds, then forgive and cooperate if
# they return to cooperation. - **Monitor for noise**: Do not punish a single
# defection unless it occurs twice consecutively. - **Final 50 rounds**: Defect
# (D) for the remainder of the game.  This strategy balances initial aggression
# with adaptability, punishes defection decisively, and exploits cooperation
# while accounting for noise.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      FINAL_ROUNDS_THRESHOLD = 50
      PUNISHMENT_ROUNDS = 2
      NOISE_THRESHOLD = 0.1
      COOPERATION_STREAK = 3
  
      # First round: Defect
      if self.first_round():
          self.punishment_counter = 0  # Tracks how many punishment rounds are left
          self.opponent_defections = 0  # Tracks how many times the opponent has defected
          return axl.Action.D
  
      # Final 50 rounds: Always defect
      if len(self.history) >= 1000 - FINAL_ROUNDS_THRESHOLD:
          return axl.Action.D
  
      # Count opponent's defections
      if opponent.history[-1] == axl.Action.D:
          self.opponent_defections += 1
  
      # If in punishment mode, continue defecting for the remaining punishment rounds
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # If opponent has defected twice, we can start considering cooperation
      if self.opponent_defections >= 2:
          # Check if the opponent has cooperated for the last 3 rounds
          if len(opponent.history) >= COOPERATION_STREAK and opponent.history[-COOPERATION_STREAK:] == [axl.Action.C] * COOPERATION_STREAK:
              return axl.Action.C
  
      # If opponent defects after cooperation, punish for 2 rounds
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.punishment_counter = PUNISHMENT_ROUNDS
          return axl.Action.D
  
      # Default action is to defect until cooperation is established
      return axl.Action.D



# 1. **Start by cooperating (C) in the first round.**  2. **In subsequent
# rounds, follow this general approach:**    - If your opponent cooperated
# (played C) in the previous round, cooperate (C) again in the current round.
# - If your opponent defected (played D) in the previous round, switch to defect
# (D) for the current round.  3. **Account for noise:**    - If your opponent
# defected but you suspect it was due to noise (i.e., their past pattern
# suggests they are generally cooperative), give them one chance to cooperate
# again by playing C in the next round.    - If your opponent defects twice in a
# row, assume they are no longer cooperative and continue defecting (D) until
# they cooperate again.  4. **Endgame (last 10 rounds):**    - Ensure
# cooperation in the last few rounds to maximize mutual payoff. Play C unless
# the opponent is clearly defecting repeatedly in this phase.  This strategy
# balances cooperation with a certain tolerance for noise, while also punishing
# consistent defection to protect yourself from exploitation.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      ENDGAME_THRESHOLD = 10
      NOISE_TOLERANCE = 1  # Number of defections tolerated before switching to defection
  
      # First round: Cooperate
      if self.first_round():
          self.defection_streak = 0  # Track consecutive defections by opponent
          return axl.Action.C
  
      # Endgame phase: last 10 rounds
      if len(self.history) >= 1000 - ENDGAME_THRESHOLD:
          # Cooperate unless opponent is clearly defecting repeatedly
          if opponent.history[-2:].count(axl.Action.D) == 2:
              return axl.Action.D
          return axl.Action.C
  
      # General strategy
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
      else:
          self.defection_streak = 0
  
      # If opponent defected twice in a row, assume they are no longer cooperative
      if self.defection_streak >= 2:
          return axl.Action.D
  
      # If opponent defected once, give them a chance to cooperate again
      if opponent.history[-1] == axl.Action.D and self.defection_streak == 1:
          return axl.Action.C
  
      # Otherwise, cooperate if opponent cooperated in the last round
      return axl.Action.C



# ### Strategy: Tit-for-Tat with Forgiveness  1. **Initial Move**: Play **C**
# (Cooperate) in the first round.  2. **Reciprocal Response**: For each
# subsequent round, play the same action that your opponent played in the
# previous round. If they cooperated (played C), you cooperate. If they defected
# (played D), you defect.  3. **Forgiveness Mechanism**:    - If your opponent
# defects, wait for **two consecutive defections** before assuming their
# defection is intentional.    - If you observe only **one defection**, continue
# cooperating in the next round, assuming it could be due to noise.  4. **Re-
# calibrate after a pattern**: If the opponent defects consistently for more
# than **three consecutive rounds**, switch to **permanent defection** to
# protect your score.  5. **Noise Awareness**:    - If you accidentally defect
# (due to noise) but your opponent cooperates, return to cooperation immediately
# in the next round.  ### Summary of Conditions: - **First round**: Always
# cooperate. - **Otherwise**:   - If opponent cooperated last round: Cooperate.
# - If opponent defected last round:     - If the opponent defected only once:
# Cooperate.     - If they defected twice in a row: Defect.     - If they defect
# more than three times in a row: Permanently defect.  This strategy balances
# cooperation and defense against exploitation while accounting for the 10%
# noise in the game.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last move of the opponent
      last_opponent_move = opponent.history[-1]
  
      # Check if the opponent has defected in the last two rounds
      if len(opponent.history) > 1:
          second_last_opponent_move = opponent.history[-2]
      else:
          second_last_opponent_move = None
  
      # Count consecutive defections
      consecutive_defections = 0
      for move in opponent.history[-3:]:
          if move == axl.Action.D:
              consecutive_defections += 1
          else:
              break
  
      # Forgiveness mechanism
      if last_opponent_move == axl.Action.D:
          if second_last_opponent_move == axl.Action.D:
              # Two consecutive defections: Defect
              return axl.Action.D
          else:
              # Only one defection: Cooperate (forgiveness)
              return axl.Action.C
  
      # Re-calibrate after a pattern of defections
      if consecutive_defections >= 3:
          # More than three consecutive defections: Switch to permanent defection
          return axl.Action.D
  
      # If opponent cooperated last round, cooperate
      if last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C



# **Aggressive Strategy for Maximizing Payoff in a 1000-Round Iterated Normal-
# Form Game (with Noise):**  1. **Start with Defection (D):**      On the first
# round, choose D to test your opponent's response and prevent being exploited
# early.  2. **Defect if Opponent Defects (D):**      If your opponent plays D
# in the previous round, continue playing D in the next round. This minimizes
# the risk of being exploited and ensures you don't fall behind in scoring.  3.
# **Tit-for-Tat with Occasional Forgiveness:**      If your opponent plays C in
# the previous round, switch to playing C *unless* the following occurs:    - If
# your opponent had a prior history of consistently playing D (more than 3
# defections in the last 5 rounds), continue playing D. The goal is to punish
# sustained betrayal.    - If the opponent defected in the previous round but
# has otherwise been cooperative (no more than 3 defections in the last 5
# rounds), consider the possibility of noise and switch to playing C. This
# builds trust if noise caused an unintentional defection.  4. **Periodically
# Revert to Defection (D):**      Every 100 rounds, regardless of the ongoing
# pattern, play D for 3 consecutive rounds. This ensures you capitalize on any
# complacency from the opponent and establish that you're not purely
# cooperative.  5. **Endgame Aggression (Final 50 Rounds):**      In the last 50
# rounds, always play D. Since the game is finite, the risk of retaliation
# diminishes, and defecting maximizes your potential payoff towards the end.  6.
# **Noise Adjustment:**      If there seems to be an abrupt, seemingly random
# defection from your opponent after a long cooperative streak, attribute it to
# noise and revert to C on the next round. Only abandon this pattern if
# defections become frequent.  ---  This strategy balances aggression with
# cautious cooperation, aiming to exploit the opponent when possible while
# accounting for the game's noise and avoiding unnecessary long-term
# retaliation.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      DEFECT = axl.Action.D
      COOPERATE = axl.Action.C
      ROUNDS_TO_CHECK = 5
      DEFECT_THRESHOLD = 3
      PERIODIC_DEFECT_INTERVAL = 100
      PERIODIC_DEFECT_DURATION = 3
      ENDGAME_START = 950
  
      # First round: Start with defection
      if self.first_round():
          return DEFECT
  
      # Endgame aggression: Always defect in the last 50 rounds
      if len(self.history) >= ENDGAME_START:
          return DEFECT
  
      # Periodically revert to defection every 100 rounds for 3 consecutive rounds
      if len(self.history) % PERIODIC_DEFECT_INTERVAL < PERIODIC_DEFECT_DURATION:
          return DEFECT
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If the opponent defected in the last round, check their recent history
      if opponent_last_move == DEFECT:
          # Count defections in the last 5 rounds
          recent_defections = opponent.history[-ROUNDS_TO_CHECK:].count(DEFECT)
  
          # If the opponent has defected more than 3 times in the last 5 rounds, continue defecting
          if recent_defections > DEFECT_THRESHOLD:
              return DEFECT
          # Otherwise, assume noise and forgive by cooperating
          else:
              return COOPERATE
  
      # If the opponent cooperated in the last round, cooperate
      if opponent_last_move == COOPERATE:
          return COOPERATE
  
      # Default to defection if no other condition is met (shouldn't happen)
      return DEFECT



# ### Strategy: "Forgiving Tit-for-Tat with Noise Adjustment"  #### Core Idea:
# The strategy aims to cooperate as much as possible to maximise mutual payoffs,
# but it will retaliate against persistent defection while accounting for the
# 10% noise in actions. The player forgives occasional defections, assuming they
# may be due to noise, but switches to defection if the opponent appears to
# consistently defect.  #### Initial Move: - **Round 1:** Cooperate (C).  ####
# Subsequent Rounds: 1. **If the opponent cooperated in the previous round:**
# - Cooperate (C) in the current round.      *(This maintains cooperation after
# mutual cooperation.)*  2. **If the opponent defected in the previous round:**
# - **Count how many times the opponent has defected in the last 3 rounds.**
# - **If the opponent defected 2 or more times in the last 3 rounds:** Defect
# (D).        *(This assumes the opponent is likely defecting intentionally and
# switches to defect in retaliation.)*      - **Otherwise:** Cooperate (C).
# *(This assumes the defection was likely caused by noise, so forgiveness is
# given.)*  3. **If you defected in the previous round (due to noise):**      -
# Continue as if you had cooperated, because your defection may have been
# unintentional.    #### Additional Rule for the Final 20 rounds: - **Starting
# in round 981:** Begin defecting (D) in every round.      *(This prevents the
# opponent from exploiting you in the final rounds by defecting, as cooperation
# is less valuable with the game nearing its end.)*  ---  This strategy balances
# cooperation to gain the high payoff from mutual cooperation while adjusting
# for noise and punishing persistent defection.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Final 20 rounds: Defect in every round starting from round 981
      if len(self.history) >= 981:
          return axl.Action.D
  
      # If the opponent cooperated in the previous round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the previous round, check the last 3 rounds
      if opponent.history[-1] == axl.Action.D:
          # Count how many times the opponent defected in the last 3 rounds
          recent_defections = opponent.history[-3:].count(axl.Action.D)
          
          # If the opponent defected 2 or more times in the last 3 rounds, defect
          if recent_defections >= 2:
              return axl.Action.D
          else:
              # Otherwise, forgive and cooperate
              return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C



# ### Strategy: **Tolerant Tit-for-Tat with Occasional Forgiveness**  1.
# **Initial Move**: Start by playing **C** (cooperate).  2. **Respond Based on
# Previous Round**:    - **If both you and your opponent played C** in the
# previous round (or it appears that way, accounting for noise), continue
# playing **C**.    - **If you played C and your opponent played D** in the
# previous round, play **D** in the next round (retaliate).    - **If you played
# D and your opponent played C** in the previous round, revert to playing **C**
# in the next round (forgive).    - **If both you and your opponent played D**
# in the previous round, play **D** again (continue defecting).  3. **Noise
# Adjustment**: Since there is a 10% chance of noise (flipping actions):    - If
# your opponent defects once but has generally cooperated, assume it might be
# due to noise and continue playing **C** for one more round (give them the
# benefit of the doubt).    - If your opponent defects **two rounds in a row**,
# assume this is intentional and respond with **D**.  4. **Occasional
# Forgiveness**: Every 10th round or so, regardless of the history of the
# previous round(s), play **C** to test whether your opponent is willing to
# return to cooperation. This helps maintain cooperation in case of extended
# defecting patterns due to misunderstanding or noise.  ### Summary: - Begin
# with cooperation. - Mirror your opponent’s last move with a bias towards
# cooperation, allowing for occasional mistakes due to noise. - Retaliate after
# repeated defections but occasionally forgive to re-establish cooperation.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate on the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if the opponent has defected twice in a row
      def opponent_defected_twice():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if the opponent's defection might be due to noise
      def might_be_noise():
          return opponent.history[-1] == axl.Action.D and opponent.history.cooperations > opponent.history.defections
  
      # Occasional forgiveness: Every 10th round, cooperate regardless of history
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Respond based on the previous round
      last_self_move = self.history[-1]
      last_opponent_move = opponent.history[-1]
  
      if last_self_move == axl.Action.C and last_opponent_move == axl.Action.C:
          # Both cooperated last round, continue cooperating
          return axl.Action.C
      elif last_self_move == axl.Action.C and last_opponent_move == axl.Action.D:
          # Opponent defected last round, but check if it might be noise
          if might_be_noise():
              return axl.Action.C  # Give the benefit of the doubt
          else:
              return axl.Action.D  # Retaliate
      elif last_self_move == axl.Action.D and last_opponent_move == axl.Action.C:
          # Forgive after defecting if opponent cooperated
          return axl.Action.C
      elif last_self_move == axl.Action.D and last_opponent_move == axl.Action.D:
          # Both defected last round, continue defecting unless it's time to forgive
          if opponent_defected_twice():
              return axl.Action.D
          else:
              return axl.Action.C



# ### Aggressive Strategy for Iterated Normal-Form Game  1. **Start by
# Defecting**: On the first round, play **D**. This sets an aggressive tone and
# avoids the risk of cooperating while the opponent defects early.  2.
# **Continue Defecting Until Punished**: If the opponent plays **C** while you
# play **D** (earning you 5 points), continue to play **D** to maximize your
# payoff. However, if the opponent retaliates by playing **D**, assess this as a
# defensive response and proceed to the next step.  3. **Switch to Tit-for-Tat
# with Defection Bias**: If the opponent defects after you defected, begin a
# **Tit-for-Tat** strategy:    - If the opponent played **D** in the previous
# round, *defect*.    - If the opponent played **C** in the previous round,
# *cooperate*.  4. **Allow for Occasional Forgiveness Due to Noise**: Since
# actions can be flipped with 10% probability, after every 10 rounds, if the
# opponent has defected in the last round, play **C** once to test if their
# defection was due to noise. If the opponent cooperates, return to **Tit-for-
# Tat**.  5. **Return to Defection if Exploited**: If, after forgiving, the
# opponent defects when you cooperate, switch back to **constant defection** for
# at least 5 rounds to punish their non-cooperation. After this period, resume
# **Tit-for-Tat with Defection Bias**.  6. **Endgame Strategy** (Rounds
# 950-1000): In the final 50 rounds, assume the opponent may adopt a short-term
# strategy to defect and maximize their own payoff. During this phase, defect
# consistently regardless of what the opponent does, ensuring you don’t lose
# points by cooperating in the late game.  ---  This strategy is designed to
# aggressively maximize your payoff while adapting to the opponent’s behavior.
# You will start strong, punish defection, and account for noise with periodic
# forgiveness. In the endgame, you shift back to pure defection to avoid risks
# associated with the short, remaining rounds.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      FORGIVENESS_INTERVAL = 10
      PUNISHMENT_PERIOD = 5
      ENDGAME_START = 950
      TOTAL_ROUNDS = 1000
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishing = False  # Whether we are in a punishment phase
          self.punish_count = 0   # Counter for punishment rounds
          return axl.Action.D     # Start by defecting
  
      # Endgame strategy: Defect consistently in the last 50 rounds
      if len(self.history) >= ENDGAME_START:
          return axl.Action.D
  
      # If in punishment phase, continue defecting for PUNISHMENT_PERIOD rounds
      if self.punishing:
          self.punish_count += 1
          if self.punish_count >= PUNISHMENT_PERIOD:
              self.punishing = False  # End punishment after PUNISHMENT_PERIOD rounds
          return axl.Action.D
  
      # If the opponent defected after we defected, switch to Tit-for-Tat with defection bias
      if len(self.history) > 1 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Tit-for-Tat: Defect if opponent defected last round
      elif len(self.history) > 1 and opponent.history[-1] == axl.Action.C:
          return axl.Action.C  # Tit-for-Tat: Cooperate if opponent cooperated last round
  
      # Every FORGIVENESS_INTERVAL rounds, forgive once if opponent defected last round
      if len(self.history) % FORGIVENESS_INTERVAL == 0 and opponent.history[-1] == axl.Action.D:
          return axl.Action.C  # Forgive once to test if defection was due to noise
  
      # If opponent defects after forgiveness, enter punishment phase
      if len(self.history) > 1 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          self.punishing = True
          self.punish_count = 0
          return axl.Action.D
  
      # Default action: Continue defecting if no other conditions are met
      return axl.Action.D



# ### Strategy: *Cooperative Tit-for-Tat with Forgiveness*  1. **Start with
# Cooperation (C):**      In the first round, always play C.  2. **Mimic the
# Opponent's Previous Move:**      In subsequent rounds, generally mimic your
# opponent's last observed action:      - If they played C in the previous
# round, play C.      - If they played D in the previous round, play D.  3.
# **Forgive Defections Occasionally (Noise Adjustment):**      Since actions are
# noisy, there's a 10% chance that an opponent's defection (D) may be
# accidental. To account for this, if your opponent defects (plays D) once but
# cooperated in the prior rounds, **continue cooperating (C) for one more
# round** after their defection. Only switch to D if their defection persists
# for two consecutive rounds.  4. **Return to Cooperation After Mutual
# Defection:**      If both you and your opponent defect (D) in the same round,
# **immediately return to cooperation (C)** in the next round.  5. **Endgame
# (Final 10 Rounds):**      With 10 rounds remaining, **switch to permanent
# cooperation (C)** regardless of the opponent's actions, to maximise the
# possibility of mutual cooperation before the game ends.  ---  This strategy
# fosters long-term cooperation while accounting for potential noise in the
# opponent's actions and maintaining flexibility to punish consistent
# defections.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      forgiveness_threshold = 0.1  # 10% chance of forgiveness
      endgame_threshold = 10       # Final 10 rounds
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Endgame: cooperate in the last 10 rounds
      if len(self.history) >= 1000 - endgame_threshold:
          return axl.Action.C
  
      # Get the last two moves of the opponent (if available)
      last_opponent_move = opponent.history[-1]
      second_last_opponent_move = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # Get the last move of self
      last_self_move = self.history[-1]
  
      # Rule 4: If both defected in the last round, return to cooperation
      if last_self_move == axl.Action.D and last_opponent_move == axl.Action.D:
          return axl.Action.C
  
      # Rule 3: Forgive a single defection if opponent cooperated before
      if last_opponent_move == axl.Action.D and second_last_opponent_move == axl.Action.C:
          if self._random.random_choice(forgiveness_threshold):
              return axl.Action.C
  
      # Rule 2: Mimic the opponent's last move
      return last_opponent_move



# ### Strategy for Iterated Normal-Form Game with Noise  **1. Start with
# Cooperation:** - In the first round, play **C** (Cooperate).  **2. Tit-for-Tat
# with Forgiveness:** - From round 2 onwards, **mimic your opponent’s previous
# action**:   - If they played **C** in the previous round, play **C**.   - If
# they played **D** in the previous round, play **D**.    **3. Introduce
# Forgiveness for Noise:** - If your opponent plays **D** after a long streak of
# **C** (at least 5 rounds of mutual cooperation), assume this is due to noise
# and **continue to play C** for the next two rounds. - If your opponent
# continues to play **D** after these two rounds, switch to **D**.  **4.
# Occasional Defection for Balance:** - Every 50 rounds, regardless of the
# opponent's behavior, **randomly defect with a 10% probability** to test their
# response and prevent being exploited.  **5. Return to Cooperation Quickly:** -
# After any intentional defection, return immediately to **C** unless the
# opponent retaliates by defecting multiple times, in which case switch to **D**
# until they cooperate again.  **6. Adapt to Persistent Defection:** - If your
# opponent defects in more than 50% of the past 10 rounds, switch to **D**
# indefinitely until they demonstrate cooperation for at least 3 consecutive
# rounds.  This strategy balances cooperation, retaliation, and forgiveness,
# adjusting for occasional noise while maximizing long-term payoff.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # 1. Start with Cooperation
      if self.first_round():
          self.coop_streak = 0  # Track mutual cooperation streak
          self.forgive_mode = 0  # Track forgiveness rounds
          return axl.Action.C
  
      # 2. Tit-for-Tat with Forgiveness
      last_opponent_move = opponent.history[-1]
      
      # Check if we are in forgiveness mode
      if self.forgive_mode > 0:
          self.forgive_mode -= 1
          return axl.Action.C
  
      # Check for mutual cooperation streak
      if last_opponent_move == axl.Action.C and self.history[-1] == axl.Action.C:
          self.coop_streak += 1
      else:
          self.coop_streak = 0
  
      # 3. Forgiveness for Noise
      if last_opponent_move == axl.Action.D and self.coop_streak >= 5:
          self.forgive_mode = 2  # Forgive for the next two rounds
          return axl.Action.C
  
      # 4. Occasional Defection for Balance
      if len(self.history) % 50 == 0:
          if self._random.random_choice(0.1):  # 10% chance to defect
              return axl.Action.D
  
      # 5. Return to Cooperation Quickly
      if self.history[-1] == axl.Action.D and last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # 6. Adapt to Persistent Defection
      if opponent.history[-10:].count(axl.Action.D) > 5:
          if opponent.history[-3:].count(axl.Action.C) == 3:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Default Tit-for-Tat behavior
      return last_opponent_move



# ### Aggressive Strategy for the Iterated Game:  1. **Start with Defection**:
# In the first round, play **D** to signal an aggressive stance and secure the
# higher payoff if the opponent cooperates.  2. **Tit-for-Tat with a Twist**:
# - In subsequent rounds, **mimic your opponent's previous action** with an
# adjustment for noise. If the opponent played **D**, you play **D**. If the
# opponent played **C**, you play **C**, but only with a **90% probability** to
# account for the chance that their action was flipped due to noise. This means
# you should consider the possibility that their cooperation was unintentional.
# 3. **Punish Opponent Defection Mildly**: If the opponent defects (plays
# **D**), continue to defect for the next **two rounds**. This ensures they face
# a cost for defecting but prevents an endless spiral of mutual defection, which
# is suboptimal.  4. **Occasional Forgiveness**: Every **50 rounds**, randomly
# play **C** even if the opponent has been defecting. This introduces an element
# of uncertainty, potentially encouraging the opponent to return to cooperation.
# 5. **Final 20 Rounds - Shift to Defection**: In the last **20 rounds**, defect
# consistently. This ensures that you maximize your payoff toward the end of the
# game, as the future threat of retaliation diminishes.  ---  This strategy
# balances an aggressive posture with calculated cooperation and accounts for
# the possibility of mistakes due to noise. The final shift to defection ensures
# a payoff boost at the end of the game.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Start with defection
      if self.first_round():
          return axl.Action.D
  
      # Get the current round number
      round_number = len(self.history)
  
      # Final 20 rounds: Shift to defection
      if round_number >= 980:
          return axl.Action.D
  
      # Tit-for-Tat with a Twist: Mimic opponent's last action with noise adjustment
      if opponent.history[-1] == axl.Action.C:
          # 90% chance to cooperate if opponent cooperated
          return self._random.random_choice(0.9)
      else:
          # Opponent defected, so we defect
          return axl.Action.D
  
      # Punish opponent defection mildly: Defect for two rounds after opponent defects
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Occasional forgiveness: Every 50 rounds, randomly cooperate
      if round_number % 50 == 0:
          return self._random.random_choice(0.5)
  
      # Default action: Tit-for-Tat
      return opponent.history[-1]



# **Strategy: Tit-for-Tat with Forgiveness**  **1. Start by cooperating.**   In
# the first round, play C (Cooperate).  **2. For the following rounds, adopt the
# following rules:**  - **If your opponent played C in the previous round, play
# C.**     This maintains cooperation if both players are cooperating.  - **If
# your opponent played D in the previous round, forgive once and play C again.**
# This assumes their defection may have been due to noise. Give them a chance to
# return to cooperation.  - **If your opponent played D two rounds in a row,
# switch to D.**     If defection persists, retaliate to avoid being exploited.
# - **After switching to D, return to C if your opponent plays C.**     This
# allows the possibility of re-establishing cooperation once the opponent shows
# willingness.  ---  This strategy balances cooperation with measured
# retaliation and forgiveness, accounting for the noise in the game. It
# encourages a cooperative dynamic while protecting against sustained
# exploitation.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If the opponent played C in the last round, cooperate
      if last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # If the opponent played D in the last round
      if last_opponent_move == axl.Action.D:
          # Check if the opponent played D two rounds in a row
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              # Retaliate by defecting
              return axl.Action.D
          else:
              # Forgive once and cooperate
              return axl.Action.C



# ### Strategy for the Iterated Normal-Form Game with Noise  1. **Start with
# Cooperation (C):**     Begin the game by choosing to cooperate in the first
# round to establish goodwill and set the tone for mutual cooperation.  2.
# **Tit-for-Tat with Forgiveness:**    - In each subsequent round, **mimic**
# your opponent's previous action (i.e., play C if they played C, and play D if
# they played D).    - **Forgive a single defection**: If your opponent defects
# (plays D) but has been cooperative in the last 3 rounds, assume it was due to
# noise and continue cooperating once.    - If your opponent defects again
# within the next 2 rounds, **retaliate by defecting** until they return to
# cooperation for at least 2 consecutive rounds.  3. **Recalibrate After
# Noise:**    - If both players defect for 2 or more consecutive rounds, **reset
# to cooperation** by playing C once to test if the opponent is willing to
# cooperate again.    - If the opponent cooperates in response, return to mutual
# cooperation.  4. **Maintain Cooperation if Possible:**     - Prioritize
# staying in a cooperative loop (both players playing C) as long as the opponent
# reciprocates, as it results in the highest cumulative payoff (3 points per
# round).    - If the opponent consistently defects, switch to permanent
# defection to prevent exploitation.  5. **Endgame Adjustment (Last 10
# Rounds):**    - In the final 10 rounds, **continue to play as normal**
# (following the above rules) to avoid signaling early defection and maintain
# cooperation.    - In the last round, **defect** as a safeguard against last-
# round exploitation.  This strategy balances cooperation and retaliation,
# accounts for noise, and maximizes long-term payoff by prioritizing mutual
# cooperation while avoiding being exploited.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      FORGIVENESS_WINDOW = 3
      RETALIATION_WINDOW = 2
      ENDGAME_THRESHOLD = 10
      TOTAL_ROUNDS = 1000
  
      # Helper function to check if opponent has been cooperative in the last N rounds
      def opponent_cooperative_last_n_rounds(n):
          return opponent.history[-n:].count(DEFECT) == 0
  
      # Helper function to check if both players defected in the last N rounds
      def both_defected_last_n_rounds(n):
          return (self.history[-n:].count(DEFECT) == n and
                  opponent.history[-n:].count(DEFECT) == n)
  
      # First round: Cooperate
      if self.first_round():
          return COOPERATE
  
      # Endgame adjustment: Defect in the last round
      if len(self.history) >= TOTAL_ROUNDS - 1:
          return DEFECT
  
      # Tit-for-Tat: Mimic opponent's last move
      if opponent.history[-1] == COOPERATE:
          return COOPERATE
      else:
          # Forgive a single defection if opponent was cooperative in the last 3 rounds
          if len(opponent.history) > FORGIVENESS_WINDOW and opponent_cooperative_last_n_rounds(FORGIVENESS_WINDOW):
              return COOPERATE
  
          # Retaliate if opponent defects again within the next 2 rounds
          if len(opponent.history) > RETALIATION_WINDOW and opponent.history[-RETALIATION_WINDOW:].count(DEFECT) > 0:
              return DEFECT
  
          # Recalibrate after noise: Reset to cooperation if both defected for 2 or more rounds
          if both_defected_last_n_rounds(RETALIATION_WINDOW):
              return COOPERATE
  
          # Default to mimicking opponent's last move
          return DEFECT



# ### Aggressive Strategy for Iterated Normal-Form Game (with Noise)  1. **Start
# with Defection:**      Begin the game by playing **D (Defect)** in the first
# round. This sets an aggressive tone and maximizes initial payoff in case your
# opponent cooperates.  2. **Continue Defecting until Punished:**      If your
# opponent responds with **C (Cooperate)** after your **D (Defect)**, continue
# defecting to exploit their cooperation for maximum payoffs (5 points per
# round).  3. **Switch to Cooperation if Punished Twice in a Row:**      If your
# opponent plays **D (Defect)** twice consecutively, switch to **C (Cooperate)**
# on the next round. This signals willingness to de-escalate and avoids getting
# stuck in mutual defection (1 point per round).  4. **Cooperate for 3 Rounds
# After the Switch:**      After switching to **C (Cooperate)** in response to
# being punished, maintain cooperation for **3 consecutive rounds**. This
# encourages the opponent to stabilize into mutual cooperation (3 points per
# round).  5. **Return to Defection if Opponent Defects More than Twice in 5
# Rounds:**      If during this 5-round window (starting from the switch) the
# opponent defects more than twice, revert to **D (Defect)** and repeat steps
# 2-4 to avoid losing too many points through cooperation.  6. **Respond to
# Noise Tolerantly:**      Since actions can be flipped due to noise, tolerate
# **1 isolated defection** by your opponent without retaliating. Only treat
# consistent patterns of defection (e.g., two in a row) as intentional and
# worthy of a strategic response.  7. **Defect in the Final 5 Rounds:**      In
# the last **5 rounds**, play **D (Defect)** regardless of the opponent’s
# behavior. In the endgame, cooperation is less valuable since future
# retaliation is irrelevant.  ---  This strategy balances aggression with some
# flexibility for cooperation when necessary, aiming to exploit cooperative
# opponents while avoiding long stretches of low-payoff mutual defection.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      COOPERATION_WINDOW = 5
      COOPERATION_PERIOD = 3
      FINAL_ROUNDS = 5
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_count = 0  # Tracks consecutive cooperation rounds after switching
          self.defection_count = 0    # Tracks consecutive defections by opponent
          self.in_cooperation_mode = False  # Tracks if we are in the cooperation phase
          return DEFECT  # Start with defection
  
      # Check if we are in the final 5 rounds
      if len(self.history) >= 1000 - FINAL_ROUNDS:
          return DEFECT  # Defect in the final 5 rounds
  
      # Track opponent's last action
      last_opponent_action = opponent.history[-1]
  
      # If in cooperation mode, continue cooperating for 3 rounds
      if self.in_cooperation_mode:
          self.cooperation_count += 1
          if self.cooperation_count >= COOPERATION_PERIOD:
              self.in_cooperation_mode = False  # Exit cooperation mode after 3 rounds
          return COOPERATE
  
      # Count opponent's defections in the last 5 rounds
      recent_defections = opponent.history[-COOPERATION_WINDOW:].count(DEFECT)
  
      # If opponent defects more than twice in the last 5 rounds, return to defection
      if recent_defections > 2:
          return DEFECT
  
      # If opponent defected twice in a row, switch to cooperation mode
      if len(opponent.history) >= 2 and opponent.history[-1] == DEFECT and opponent.history[-2] == DEFECT:
          self.in_cooperation_mode = True
          self.cooperation_count = 0  # Reset cooperation count
          return COOPERATE
  
      # If opponent defected once, tolerate it (noise handling)
      if last_opponent_action == DEFECT:
          self.defection_count += 1
      else:
          self.defection_count = 0  # Reset defection count if opponent cooperates
  
      # Continue defecting if no punishment (two consecutive defections)
      return DEFECT



# **Strategy:**  1. **Start with cooperation** (C) in the first round.     2.
# **Continue cooperating as long as both players have mostly cooperated in
# recent rounds.** Specifically, after each round, review the last 5 rounds. If
# your opponent has cooperated in at least 3 of those 5 rounds, continue to
# cooperate.   3. **Forgive occasional defections,** since there is a 10% chance
# of noise. If your opponent defects in 1 or 2 out of the last 5 rounds, assume
# it could be due to noise and keep cooperating.  4. **Defect if your opponent
# has defected in 3 or more of the last 5 rounds.** This indicates a likely
# shift in their strategy to a more aggressive or uncooperative approach.  5.
# **Return to cooperation after defecting,** but only if your opponent shows a
# clear intent to cooperate again. If they cooperate in 3 out of the next 5
# rounds after your defection, return to cooperation yourself.  6. **Always
# defect in the last 5 rounds,** as the game is finite and the incentive to
# exploit becomes stronger towards the end.  This strategy builds and maintains
# trust while protecting against sustained exploitation, accounting for both
# noise and long-term cooperation.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # If it's the first round, cooperate
      if self.first_round():
          return axl.Action.C
      
      # Number of rounds to consider for recent history
      window = 5
      
      # Always defect in the last 5 rounds
      if len(self.history) >= 995:
          return axl.Action.D
      
      # Helper function to count cooperations in the last N rounds
      def count_recent_cooperations(history, n):
          return history[-n:].count(axl.Action.C)
      
      # Check the opponent's cooperation in the last 5 rounds
      if len(opponent.history) >= window:
          recent_opponent_cooperations = count_recent_cooperations(opponent.history, window)
      else:
          recent_opponent_cooperations = count_recent_cooperations(opponent.history, len(opponent.history))
      
      # If opponent cooperated in 3 or more of the last 5 rounds, cooperate
      if recent_opponent_cooperations >= 3:
          return axl.Action.C
      
      # If opponent defected in 3 or more of the last 5 rounds, defect
      if recent_opponent_cooperations <= 2:
          return axl.Action.D
      
      # Default to cooperation
      return axl.Action.C



# ### Strategy: "Adaptive Reciprocity with Forgiveness"  1. **Start with
# Cooperation (C)**: Play C in the first round to signal an intent to cooperate.
# 2. **Tit-for-Tat with Noise Adjustment**: In subsequent rounds, mimic your
# opponent’s previous action, but factor in noise:     - If your opponent played
# C in the previous round, respond with C.     - If your opponent played D in
# the previous round, respond with D.     - However, allow for occasional
# forgiveness: after every 4 defections in a row by the opponent, switch to C
# once, assuming noise may have caused the string of defections.  3.
# **Forgiveness Mechanism**: If you observe your opponent defecting after a
# period of cooperation, return to C after 2 consecutive defections, assuming
# noise may have flipped their action. If defections continue, escalate to D for
# the next rounds.  4. **Defection Trigger**: If your opponent defects more than
# 50% of the time over a span of 10 rounds, switch to permanent defection (D)
# for the remainder of the game to avoid continued exploitation.  5. **Final
# Rounds (Saturation Effect)**: In the last 10 rounds, defect (D) consistently
# to maximize your score, as reciprocity becomes less valuable near the end of
# the game.  This strategy balances cooperation and defection while accounting
# for noise, enabling you to benefit from mutual cooperation when possible but
# also protecting against exploitation.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation in the first round
      if self.first_round():
          self.defection_streak = 0  # Track consecutive defections by opponent
          self.total_defections = 0  # Track total defections by opponent
          return axl.Action.C
  
      # Final 10 rounds: always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Tit-for-Tat with Noise Adjustment
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
          self.total_defections += 1
      else:
          self.defection_streak = 0  # Reset defection streak if opponent cooperates
  
      # Forgiveness Mechanism: Forgive after 2 consecutive defections
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.C
  
      # Forgiveness Mechanism: Forgive after 4 defections in a row
      if self.defection_streak >= 4:
          self.defection_streak = 0  # Reset streak after forgiveness
          return axl.Action.C
  
      # Defection Trigger: If opponent defects more than 50% in the last 10 rounds, defect permanently
      if len(self.history) >= 10 and opponent.history[-10:].count(axl.Action.D) > 5:
          return axl.Action.D
  
      # Tit-for-Tat: Mimic opponent's last action
      return opponent.history[-1]



# ### Aggressive Strategy for 1000-Round Iterated Normal-Form Game  1. **Start
# with Defection (D)**: Begin the game by playing D in the first round to
# establish an aggressive stance and potentially capitalize on an early payoff
# advantage.  2. **Continue Defection (D) for the next 9 rounds**: Maintain
# defection for a total of 10 rounds. This will allow you to observe whether
# your opponent frequently defects as well or attempts to cooperate despite your
# aggressive play.  3. **Evaluate the Opponent's Behavior after 10 Rounds**:
# - **If the opponent mostly plays C** (at least 7 out of 10 times), **switch to
# Cooperation (C)**: This suggests the opponent is likely a cooperative type,
# and you can now exploit their tendency by cooperating and achieving mutual
# higher payoffs.    - **If the opponent mostly plays D** (at least 7 out of 10
# times), **continue Defection (D)**: This indicates they are aggressive, and
# mutual defection is expected to provide a stable, though lower, payoff.
# Continue defecting to avoid being exploited.  4. **Re-evaluate Every 50
# Rounds**: After every 50 rounds, recheck your opponent's behavior:    - **If
# they are cooperating most of the time (over 70% of rounds)**, switch to
# cooperation to maximize mutual benefit.    - **If they are defecting most of
# the time (over 70% of rounds)**, continue defecting to avoid being exploited.
# 5. **Handle Noise**: In case of unexpected actions (e.g., an opponent
# defecting once after a streak of cooperation), avoid immediate retaliation due
# to the 10% noise factor. Only adjust your strategy if there is a consistent
# pattern over multiple rounds (e.g., 3 consecutive defections after prior
# cooperation).  6. **Final 100 Rounds**: In the last 100 rounds, if your
# opponent has been consistently cooperative, consider defecting more frequently
# to maximize short-term gain, but not excessively (e.g., defect in 30-40% of
# these rounds) to avoid prompting a full switch to defection from your
# opponent.  ### Summary: - **Default** to defection to maintain an aggressive
# stance. - **Switch** to cooperation if the opponent proves consistently
# cooperative (70%+ cooperation). - **Reassess** every 50 rounds to adapt to the
# opponent's tactics. - **Factor in noise** by not overreacting to isolated
# defections or cooperations.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_count = 0
          self.cooperation_count = 0
          self.rounds_played = 0
          return axl.Action.D  # Start with defection
  
      # Update counts of opponent's actions
      if opponent.history[-1] == axl.Action.C:
          self.cooperation_count += 1
      else:
          self.defection_count += 1
  
      self.rounds_played += 1
  
      # First 10 rounds: Always defect
      if self.rounds_played < 10:
          return axl.Action.D
  
      # After 10 rounds, evaluate opponent's behavior
      if self.rounds_played == 10:
          if opponent.history[:10].count(axl.Action.C) >= 7:
              self.current_strategy = axl.Action.C  # Switch to cooperation
          else:
              self.current_strategy = axl.Action.D  # Continue defection
  
      # Re-evaluate every 50 rounds
      if self.rounds_played % 50 == 0:
          if opponent.history.cooperations / self.rounds_played > 0.7:
              self.current_strategy = axl.Action.C  # Switch to cooperation
          elif opponent.history.defections / self.rounds_played > 0.7:
              self.current_strategy = axl.Action.D  # Continue defection
  
      # Handle noise: Avoid immediate retaliation for isolated defections
      if self.rounds_played >= 3 and opponent.history[-3:].count(axl.Action.D) == 3:
          self.current_strategy = axl.Action.D  # Switch to defection after 3 consecutive defections
  
      # Final 100 rounds: Defect more frequently if opponent has been cooperative
      if self.rounds_played >= 900:
          if opponent.history.cooperations / self.rounds_played > 0.7:
              if self._random.random_choice(0.35):  # Defect 30-40% of the time
                  return axl.Action.D
              else:
                  return axl.Action.C
  
      # Default to the current strategy
      return self.current_strategy



# ### Cooperative Strategy for Noisy Iterated Normal-Form Game  1. **Start with
# Cooperation (C):** In the first round, always play **C** to signal a
# willingness to cooperate.  2. **Tit-for-Tat with Forgiveness:**    - In each
# subsequent round, **mirror your opponent's previous move**. If they played
# **C**, play **C**. If they played **D**, play **D**.    - **Forgive occasional
# defections:** If your opponent plays **D** but has been cooperating
# consistently in previous rounds (at least 3 or more rounds of cooperation),
# assume it was due to noise and **play C** in the next round to re-establish
# cooperation.  3. **Punish sustained defection:** If your opponent defects
# (plays **D**) for **three consecutive rounds**, assume they are no longer
# willing to cooperate and **switch to playing D** in all future rounds. You
# will continue to defect until the end of the game.  4. **Revert if opponent
# returns to cooperation:** If your opponent switches back to playing **C** for
# at least **three consecutive rounds** after defecting, give them one more
# chance by returning to cooperation (**C**).  5. **Endgame (last 20 rounds):**
# - In the last 20 rounds, regardless of previous actions, **adopt a more
# forgiving strategy** by playing **C** at least 80% of the time. This maximizes
# potential cooperation towards the end of the game when defection could be
# tempting for the opponent.  ### Summary of Key Actions: - **Start with C.** -
# **Mirror opponent's last move** unless noise is suspected. - **Forgive
# occasional defections** but **punish sustained defection**. - **Revert to
# cooperation** if opponent returns to it. - In the **final 20 rounds**, prefer
# **C** to secure cooperation.  This strategy balances cooperation with the
# ability to react to defection, while accounting for noise and giving the
# opponent multiple chances to maintain a cooperative relationship.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 3
      DEFECTION_THRESHOLD = 3
      ENDGAME_THRESHOLD = 20
      FORGIVENESS_PROBABILITY = 0.8
  
      # Start with cooperation
      if self.first_round():
          return axl.Action.C
  
      # Check if we are in the last 20 rounds
      if len(self.history) >= 1000 - ENDGAME_THRESHOLD:
          # In the last 20 rounds, cooperate with 80% probability
          return self._random.random_choice(FORGIVENESS_PROBABILITY)
  
      # Count opponent's last 3 moves
      last_3_opponent_moves = opponent.history[-3:]
  
      # If opponent defected for the last 3 rounds, switch to permanent defection
      if last_3_opponent_moves.count(axl.Action.D) == DEFECTION_THRESHOLD:
          self.permanently_defect = True
  
      # If opponent cooperated for the last 3 rounds, revert to cooperation
      if last_3_opponent_moves.count(axl.Action.C) == COOPERATION_THRESHOLD:
          self.permanently_defect = False
  
      # If we are in permanent defection mode, always defect
      if getattr(self, 'permanently_defect', False):
          return axl.Action.D
  
      # Tit-for-tat with forgiveness: mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          # Check if opponent has cooperated consistently in the past
          if opponent.history[-4:-1].count(axl.Action.C) >= COOPERATION_THRESHOLD:
              # Forgive occasional defection and cooperate
              return axl.Action.C
          else:
              # Otherwise, defect in response
              return axl.Action.D
      else:
          # If opponent cooperated, cooperate
          return axl.Action.C



# ### Strategy: Tit-for-Tat with Tolerance for Noise  #### 1. **First Move:**
# - **Play C (Cooperate).**  #### 2. **Subsequent Rounds Decision:**    - **If
# the opponent played C in the previous round**, play C (Cooperate) in the
# current round.    - **If the opponent played D in the previous round**, play D
# (Defect) in the current round.  #### 3. **Noise Tolerance (Forgiveness
# Mechanism):**    - **If the opponent defected in only 1 of the last 2
# rounds**, assume it may have been due to noise and still play C (Cooperate).
# - **If the opponent defected in 2 consecutive rounds**, assume it is
# intentional and switch to D (Defect) until they cooperate again.  #### 4.
# **Closing Phase (Final 50 Rounds):**    - **If in the last 50 rounds, the
# opponent has been cooperating consistently**, continue cooperating.    - **If
# in the last 50 rounds, the opponent has defected more than cooperated**,
# switch to D (Defect) for the remainder of the game.  This strategy balances
# cooperation with retaliation while accounting for the noise in action flips,
# aiming to foster long-term cooperation and maximize overall payoff.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First move: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last 2 rounds of opponent's history
      last_round = opponent.history[-1]
      second_last_round = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # Noise tolerance: If opponent defected in only 1 of the last 2 rounds, cooperate
      if last_round == axl.Action.D and second_last_round == axl.Action.D:
          # Opponent defected in the last 2 rounds, so defect
          return axl.Action.D
      elif last_round == axl.Action.D or second_last_round == axl.Action.D:
          # Opponent defected in only 1 of the last 2 rounds, so forgive and cooperate
          return axl.Action.C
  
      # Closing phase: Final 50 rounds
      if len(self.history) >= 950:
          # Count defections and cooperations in the last 50 rounds
          last_50_defections = opponent.history[-50:].count(axl.Action.D)
          last_50_cooperations = opponent.history[-50:].count(axl.Action.C)
  
          if last_50_defections > last_50_cooperations:
              # Opponent defected more than cooperated in the last 50 rounds, defect
              return axl.Action.D
          else:
              # Opponent cooperated more, continue cooperating
              return axl.Action.C
  
      # Default Tit-for-Tat: Mirror the opponent's last move
      return last_round



# ### Aggressive Strategy for Iterated Noisy Game  1. **Start with Defection
# (D)**: In the first round, play D to signal an aggressive approach and attempt
# to gain an early upper hand.  2. **Continue Defecting (D) as Long as Opponent
# Defects Frequently (D > 50%)**:    - Track how often your opponent chooses D
# over several rounds (e.g., in blocks of 10-20 rounds).    - If your opponent
# defects more than 50% of the time in these blocks, continue playing D to avoid
# being exploited.  3. **Switch to Cooperation (C) if Opponent Cooperates
# Frequently (C ≥ 50%)**:    - If you notice that your opponent cooperates at
# least 50% of the time over a block of rounds, switch to C to explore mutual
# cooperation and higher payoffs.    - However, **defect immediately (D)** if
# the opponent defects twice consecutively after this switch to avoid incurring
# repeated losses.  4. **Punish Defection with Retaliation (D)**:    - If your
# opponent defects after a period of mutual cooperation, immediately switch to D
# for at least 3 rounds as punishment, regardless of noise. This discourages
# further defection.  5. **Forgive Occasional Defection Due to Noise**:    -
# Given the 10% noise, occasionally your or your opponent's actions may be
# unintentionally flipped. If your opponent defects once after a long period of
# cooperation, assume it was noise and continue cooperating. Only punish if
# defection occurs twice in a row.  6. **Reassess Regularly**:    - Every 50
# rounds, reassess your opponent's overall behavior. If they have shifted to
# frequent cooperation (C ≥ 70% in the last block), consider moving toward a
# more cooperative stance. If they remain aggressive, maintain defection.  7.
# **Final Phase (Last 50 Rounds)**:    - In the final 50 rounds, if you're ahead
# in points, consider staying defensive (D) to lock in your lead. If you're
# behind, take more aggressive risks by defecting more frequently to maximize
# potential high payoffs.  This strategy balances aggression with a willingness
# to explore cooperation, while taking into account the noise in the game.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.retaliation_count = 0  # Tracks retaliation rounds
          self.last_reassessment = 0  # Tracks the last reassessment round
          self.coop_switch = False    # Tracks if we switched to cooperation
          return axl.Action.D         # Start with defection
  
      # Helper function to count defections in the last N rounds
      def count_defections(history, N):
          return history[-N:].count(axl.Action.D)
  
      # Helper function to count cooperations in the last N rounds
      def count_cooperations(history, N):
          return history[-N:].count(axl.Action.C)
  
      # Block size for reassessment
      block_size = 50
      recent_block_size = 20
  
      # Retaliation phase: defect for 3 rounds after opponent defects post-cooperation
      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D
  
      # Check if we are in the final 50 rounds
      if len(self.history) >= 950:
          # Final phase strategy: if ahead, stay defensive, else take risks
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if my_score > opponent_score:
              return axl.Action.D  # Stay defensive if ahead
          else:
              return axl.Action.D if self._random.random_choice(0.7) else axl.Action.C  # Take risks if behind
  
      # Reassess every 50 rounds
      if len(self.history) - self.last_reassessment >= block_size:
          self.last_reassessment = len(self.history)
          recent_cooperations = count_cooperations(opponent.history, block_size)
          if recent_cooperations >= 0.7 * block_size:
              self.coop_switch = True  # Shift to a more cooperative stance
  
      # If we switched to cooperation, check for consecutive defections
      if self.coop_switch:
          if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              self.coop_switch = False  # Defect immediately if opponent defects twice consecutively
              return axl.Action.D
          return axl.Action.C  # Continue cooperating if opponent cooperates frequently
  
      # Analyze recent behavior in blocks of 10-20 rounds
      recent_defections = count_defections(opponent.history, recent_block_size)
      recent_cooperations = count_cooperations(opponent.history, recent_block_size)
  
      if recent_defections > 0.5 * recent_block_size:
          return axl.Action.D  # Continue defecting if opponent defects frequently
      elif recent_cooperations >= 0.5 * recent_block_size:
          self.coop_switch = True  # Switch to cooperation if opponent cooperates frequently
          return axl.Action.C
  
      # Punish defection with retaliation for 3 rounds
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          self.retaliation_count = 3
          return axl.Action.D
  
      # Forgive occasional defection due to noise
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.C  # Assume noise and continue cooperating
  
      # Default to defection if no other conditions are met
      return axl.Action.D



# **Strategy: Tit-for-Tat with Noise Adjustment**  1. **Initial Move**:     -
# Start by playing **C** (Cooperate).  2. **Main Rule**:     - In each
# subsequent round, **mimic** your opponent’s previous action. If they played
# **C**, play **C**. If they played **D**, play **D**.  3. **Noise Adjustment**:
# - If your opponent defects (plays **D**) after a round where you both
# cooperated (both played **C**), assume that this may have been due to noise.
# Continue to play **C** for the next two rounds to test if the defection was
# intentional.    - If the opponent defects again within those two rounds,
# assume intentional defection and switch to playing **D** in the next round.
# 4. **Rebuilding Cooperation**:     - If the opponent returns to playing **C**
# after a defection, forgive the defect and immediately switch back to **C**
# (Cooperate) to re-establish a cooperative cycle.  5. **Endgame (Rounds 990 to
# 1000)**:     - In the final 10 rounds, always cooperate (**C**) regardless of
# opponent action to signal continued goodwill and avoid unnecessary defection
# spirals.  ---  This strategy encourages cooperation but adjusts for noise and
# potential exploitation. It balances maintaining cooperation with the
# possibility of punishing consistent defection.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate
      if self.first_round():
          self.noise_test_rounds = 0  # Tracks rounds to test for noise
          return axl.Action.C
  
      # Endgame: Always cooperate in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Main Rule: Mimic opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Noise Adjustment: If both cooperated in the previous round and opponent defects now
      if len(self.history) > 1 and self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          if last_opponent_move == axl.Action.D:
              # Start noise test: Cooperate for the next two rounds
              self.noise_test_rounds = 2
              return axl.Action.C
  
      # If in noise test mode, continue cooperating for two rounds
      if self.noise_test_rounds > 0:
          self.noise_test_rounds -= 1
          # If opponent defects again during noise test, assume intentional defection
          if last_opponent_move == axl.Action.D:
              return axl.Action.D
          return axl.Action.C
  
      # Rebuilding Cooperation: If opponent cooperates after defection, forgive and cooperate
      if last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # Default: Mimic opponent's last move
      return last_opponent_move



# ### Strategy: **Cautious Tit-for-Tat with Forgiveness**  1. **Initial Move:
# Cooperate (C).**    - Always start by playing C in the first round.  2. **Main
# Rule: Mirror your opponent's previous action.**    - If your opponent played C
# in the last round, play C.    - If your opponent played D in the last round,
# play D.  3. **Noise Handling: Forgive potential noise once every 5 rounds.**
# - If your opponent defects (plays D) after a long stretch of cooperation (5
# consecutive C rounds), treat it as potential noise and continue playing C for
# 1 more round.     - If they defect again immediately after, switch to playing
# D according to the main rule.  4. **Revert to cooperation after mutual
# defection.**    - If both players defect (both play D), return to cooperation
# (C) on the following move to avoid getting stuck in a cycle of mutual
# defection.  ---  This strategy balances cooperation with cautious retaliation,
# while accounting for noise by allowing occasional forgiveness and attempts to
# re-establish cooperation after mutual defection.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate
      if self.first_round():
          self.forgiveness_counter = 0  # Initialize forgiveness counter
          return axl.Action.C
  
      # Check the last move of the opponent
      opponent_last_move = opponent.history[-1]
      
      # Check if both players defected in the last round
      if self.history[-1] == axl.Action.D and opponent_last_move == axl.Action.D:
          return axl.Action.C  # Revert to cooperation after mutual defection
  
      # Check if the opponent has defected after a long stretch of cooperation
      if len(opponent.history) >= 6 and opponent.history[-6:-1].count(axl.Action.D) == 0:
          if opponent_last_move == axl.Action.D:
              # Forgive once every 5 rounds
              if self.forgiveness_counter < 5:
                  self.forgiveness_counter += 1
                  return axl.Action.C  # Forgive the first defection
              else:
                  self.forgiveness_counter = 0  # Reset counter after forgiveness
                  return axl.Action.D  # Defect if they defect again immediately
  
      # Mirror the opponent's last move (Tit-for-Tat)
      return opponent_last_move



# ### Aggressive Strategy for Iterated Noisy Game  1. **Start with Defection
# (D)**: Begin the game by playing D to establish an aggressive stance and test
# the opponent's willingness to cooperate or defect.  2. **Continue Defecting
# (D) Until Opponent Defects Twice in a Row**: If the opponent defects in two
# consecutive rounds, continue playing D, as this indicates a likely defection
# strategy from them, and you can maximize your payoff by mutual defection.  3.
# **Switch to Cooperation (C) After Two Consecutive Opponent Cooperations**: If
# the opponent plays C in two consecutive rounds, play C on the next round to
# test if they are willing to cooperate consistently. This also mitigates noise-
# induced accidental defections.  4. **Punish Immediately After Opponent
# Defects**: If the opponent defects after a period of cooperation (even once),
# immediately switch to D and defect for the next three rounds to punish the
# defection and discourage further defections.  5. **Forgive After Three
# Defections**: After punishing the opponent for three rounds, if they have
# returned to cooperation, switch back to C. This ensures you don’t fall into a
# permanent defection cycle and can capitalize on mutual cooperation if the
# opponent is willing.  6. **Stay in Defection if Opponent Defects More Than 30%
# of the Time**: If, after 50 rounds, the opponent has defected in more than 30%
# of the rounds, adopt a permanent defection strategy, as the likelihood of
# successful cooperation is low.  7. **Tolerate Occasional Noise-Based
# Defections**: If the opponent has been mostly cooperative but defects once in
# a while (less than 30% of the time), treat these as noise-induced and do not
# punish immediately. Continue cooperating unless the defections become
# consistent (see point 4).  8. **Endgame Defection (Final 20 Rounds)**: In the
# last 20 rounds, defect regardless of the opponent’s actions to ensure
# maximization of late-game payoffs, as cooperation at this stage is less
# valuable due to the finite nature of the game.  This strategy balances
# aggression with conditional cooperation, punishing defections but offering
# opportunities for cooperation if the opponent shows consistent willingness.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      PUNISHMENT_LENGTH = 3
      DEFECT_THRESHOLD = 0.3
      ENDGAME_THRESHOLD = 20
      TOTAL_ROUNDS = 1000
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.punishing = False
          self.punish_count = 0
          return axl.Action.D  # Start with defection
  
      # Endgame defection strategy
      if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
          return axl.Action.D
  
      # Count opponent's defections and cooperations
      opponent_defections = opponent.history.defections
      opponent_cooperations = opponent.history.cooperations
  
      # Check if opponent defects more than 30% of the time after 50 rounds
      if len(self.history) >= 50:
          if opponent_defections / len(self.history) > DEFECT_THRESHOLD:
              return axl.Action.D  # Permanent defection
  
      # Handle punishment phase
      if self.punishing:
          self.punish_count += 1
          if self.punish_count >= PUNISHMENT_LENGTH:
              self.punishing = False  # End punishment after 3 rounds
          return axl.Action.D
  
      # Check for opponent's last two moves
      if len(opponent.history) >= 2:
          last_two_moves = opponent.history[-2:]
  
          # If opponent defects twice in a row, continue defecting
          if last_two_moves == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
  
          # If opponent cooperates twice in a row, switch to cooperation
          if last_two_moves == [axl.Action.C, axl.Action.C]:
              return axl.Action.C
  
      # If opponent defects after cooperation, punish for 3 rounds
      if len(opponent.history) >= 1 and opponent.history[-1] == axl.Action.D:
          self.punishing = True
          self.punish_count = 0
          return axl.Action.D
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C



# **Strategy: Tit-for-Tat with Forgiveness**  1. **Start Cooperating**: In the
# first round, always play C (cooperate).     2. **React to Opponent's Last
# Move**: In each subsequent round, play what your opponent played in the
# previous round. If they cooperated (C), you cooperate. If they defected (D),
# you defect.  3. **Forgive Occasional Defections**: If your opponent defects,
# but they cooperated in the majority of the last 5 rounds (i.e., 3 or more
# times), assume the defection was due to noise and play C (cooperate) instead
# of D in the current round.  4. **Return to Cooperation after Defection**: If
# you defect due to your opponent's defection, but they return to cooperating,
# immediately play C (cooperate) in the next round, assuming they intend to
# cooperate again.  This strategy balances maintaining cooperation while
# accounting for the game's noise by offering forgiveness to prevent spirals of
# mutual defection.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # Check the last 5 rounds (or fewer if less than 5 rounds have been played)
      recent_rounds = min(5, len(opponent.history))
      recent_cooperations = opponent.history[-recent_rounds:].count(axl.Action.C)
  
      # If the opponent defected last round but cooperated in the majority of the last 5 rounds, forgive
      if opponent_last_move == axl.Action.D and recent_cooperations >= 3:
          return axl.Action.C
  
      # Otherwise, mimic the opponent's last move
      return opponent_last_move



# ### Strategy: "Tit-for-Tat with Forgiveness"  1. **Initial Move**: Start by
# cooperating (play C) in the first round.  2. **Tit-for-Tat Response**:     -
# In each subsequent round, **mimic** your opponent's previous action.       -
# If they played C in the last round, you play C.      - If they played D in the
# last round, you play D.  3. **Forgiveness Mechanism** (to account for noise):
# - If your opponent defects (plays D) **only once** after a long streak of
# cooperation (at least 5 consecutive rounds of both playing C), assume it was
# due to noise and **continue cooperating** instead of retaliating immediately.
# - If the opponent defects again within the next 2 rounds, **switch to
# defection** (play D) to punish sustained defection.  4. **Return to
# Cooperation**:     - After defecting in response to sustained defection, if
# your opponent returns to cooperation (plays C), **immediately return to
# cooperation** (play C) in the next round.  5. **Endgame (final 5 rounds)**:
# - In the last 5 rounds, assume the opponent might try to exploit you. **Defect
# (play D) consistently** to avoid last-minute exploitation.  ---  This strategy
# balances cooperation with an opponent who is willing to cooperate, while
# punishing defection in a measured way. The forgiveness mechanism helps account
# for the 10% action-flip noise, ensuring that a single accidental defection
# doesn't lead to an unnecessary breakdown in cooperation.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          self.forgiveness_flag = False  # Track if forgiveness is active
          self.defection_count = 0  # Track consecutive defections
          return axl.Action.C
  
      # Endgame: Defect in the last 5 rounds
      if len(self.history) >= 995:
          return axl.Action.D
  
      # Tit-for-Tat Response: Mimic opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Check if we are in a forgiveness state
      if self.forgiveness_flag:
          # If opponent cooperates after forgiveness, return to cooperation
          if last_opponent_move == axl.Action.C:
              self.forgiveness_flag = False
              return axl.Action.C
          # If opponent defects again within 2 rounds, retaliate
          elif self.defection_count < 2:
              self.defection_count += 1
              return axl.Action.C
          else:
              self.forgiveness_flag = False
              return axl.Action.D
  
      # Forgiveness Mechanism: If opponent defects after a long cooperation streak
      if last_opponent_move == axl.Action.D:
          if len(self.history) >= 6 and all(
              move == axl.Action.C for move in self.history[-6:-1]
          ) and all(
              move == axl.Action.C for move in opponent.history[-6:-1]
          ):
              # Forgive a single defection after a long cooperation streak
              self.forgiveness_flag = True
              self.defection_count = 1
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Default Tit-for-Tat behavior: Mimic opponent's last move
      return last_opponent_move



# **Aggressive Strategy for Iterated Normal-Form Game (1000 rounds, noisy
# actions)**  1. **Start with Defection:** In the first round, always play **D**
# (Defect). This sets an aggressive baseline and tests your opponent's potential
# strategy without immediately risking exploitation.  2. **Defect
# Continuously:** Continue playing **D** (Defect) in every round unless the
# following conditions trigger a change in behavior. Defection generally
# guarantees a non-zero payoff and avoids being exploited if the opponent is
# cooperative.  3. **Switch to Cooperation After Sustained Cooperation:** If the
# opponent plays **C** (Cooperate) for **3 consecutive rounds**, switch to **C**
# (Cooperate) on the next round. This helps capitalize on the cooperative payoff
# if the opponent proves to be consistently cooperative. However, due to noise,
# do not immediately trust one or two cooperative moves.  4. **Return to
# Defection if Exploited:** If the opponent defects in any round after you have
# switched to **C**, immediately switch back to **D** (Defect) and continue
# defecting for at least the next **5 rounds**. This punishes exploitation and
# discourages your opponent from taking advantage of cooperation.  5. **Ignore
# Single Uncooperative Moves (Noise Management):** If there is a single instance
# of defection by the opponent after sustained cooperation, but their previous
# and subsequent moves are cooperative, assume it was due to noise. Stay in
# **C** mode unless a pattern of defection emerges.  6. **Endgame Aggression:**
# In the final **20 rounds**, always play **D** (Defect), regardless of the
# opponent's behavior. The end of the game reduces the long-term benefits of
# cooperation, and defection ensures you prevent late-stage exploitation while
# maximizing potential high payoffs.  ---  This strategy ensures an aggressive
# stance while still allowing for opportunistic cooperation, and it takes the
# noise factor into account to avoid overreacting to isolated mistakes.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperative_streak = 0  # Track consecutive cooperations by opponent
          self.defect_countdown = 0    # Track how many rounds to defect after being exploited
          return axl.Action.D          # Start with defection
  
      # Endgame aggression: defect in the last 20 rounds
      if len(self.history) >= 980:
          return axl.Action.D
  
      # If in punishment mode (after being exploited), continue defecting for 5 rounds
      if self.defect_countdown > 0:
          self.defect_countdown -= 1
          return axl.Action.D
  
      # Check opponent's last move
      if opponent.history[-1] == axl.Action.C:
          self.cooperative_streak += 1
      else:
          # If opponent defects after we cooperated, switch back to defection and punish
          if self.history[-1] == axl.Action.C:
              self.defect_countdown = 5
              return axl.Action.D
          # If opponent defects but we were already defecting, reset cooperative streak
          self.cooperative_streak = 0
  
      # If opponent has cooperated for 3 consecutive rounds, switch to cooperation
      if self.cooperative_streak >= 3:
          return axl.Action.C
  
      # Default action is to defect
      return axl.Action.D



# ### Strategy: **Forgiving Tit-for-Tat with Noise Adaptation**  1. **Start with
# Cooperation (C):** In the first round, always play C.  2. **Mirror Opponent's
# Previous Action:** In subsequent rounds, play the same action your opponent
# played in the previous round. If they cooperated (C), you cooperate. If they
# defected (D), you defect.  3. **Forgive Occasional Defections:** If your
# opponent defects exactly once after a streak of cooperation, assume this was
# due to noise. Return to cooperation (C) in the next round, rather than
# retaliating with a defection.  4. **Punish Consistent Defection:** If your
# opponent defects for two consecutive rounds, assume they are deliberately
# defecting. Respond by defecting (D) until they return to cooperation.  5.
# **Return to Cooperation Quickly:** If your opponent cooperates after a period
# of defection, respond by cooperating in the next round. This encourages a
# return to mutual cooperation.  6. **Endgame Strategy:** In the final 3 rounds
# (rounds 998-1000), always defect (D), regardless of previous moves. This helps
# avoid exploitation in the final rounds where long-term cooperation no longer
# benefits you.  ---  This strategy encourages mutual cooperation while
# forgiving occasional noise-induced errors. It also deters long-term defection
# by punishing consistent defection but offers a path back to cooperation when
# the opponent resumes cooperative behavior.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants for actions
      C, D = axl.Action.C, axl.Action.D
  
      # First round: always cooperate
      if self.first_round():
          return C
  
      # Endgame strategy: defect in the last 3 rounds
      if len(self.history) >= 998:
          return D
  
      # Mirror opponent's previous action
      if opponent.history[-1] == C:
          return C
  
      # Check for forgiveness condition: opponent defected exactly once after a streak of cooperation
      if len(opponent.history) >= 2:
          if opponent.history[-1] == D and opponent.history[-2] == C:
              # Forgive a single defection after cooperation
              return C
  
      # Punish consistent defection: opponent defected in the last two rounds
      if len(opponent.history) >= 2 and opponent.history[-1] == D and opponent.history[-2] == D:
          return D
  
      # Default to mirroring the opponent's last action
      return opponent.history[-1]



# ### Strategy: Balanced Reciprocity with Noise Adjustment  1. **Initial Move**:
# Start by playing **C** (Cooperate) in the first round.  2. **Tit-for-Tat with
# Forgiveness**: In each subsequent round, mimic your opponent's previous move,
# but introduce forgiveness:    - If your opponent played **C** in the previous
# round, play **C**.    - If your opponent played **D** in the previous round,
# play **D** **unless** they have defected only once in the last 5 rounds (to
# account for potential noise). In this case, play **C** to allow for recovery
# from accidental defection.  3. **Error Correction**: If a sequence of **D**
# moves from your opponent lasts for more than 3 consecutive rounds, assume they
# are consistently defecting and switch to always playing **D** until a
# cooperative move (**C**) is observed from them. Once they cooperate, revert to
# playing **C** in the next round.  4. **Endgame (Rounds 990-1000)**: In the
# final 10 rounds, defect if your opponent has defected more than 30% of the
# time in the preceding rounds. Otherwise, continue the usual strategy.  ---
# This strategy balances cooperation and retaliation, while accounting for noise
# and preventing long-term exploitation.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to count defections in the last N rounds
      def count_defections_in_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D)
  
      # Tit-for-Tat with Forgiveness
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Check if opponent defected only once in the last 5 rounds
          if count_defections_in_last_n_rounds(5) == 1:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Error Correction: If opponent defected for more than 3 consecutive rounds
      if count_defections_in_last_n_rounds(3) == 3:
          # Switch to always defecting until opponent cooperates
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Endgame strategy: Defect if opponent defected more than 30% of the time
      if len(self.history) >= 990:
          total_rounds = len(self.history)
          opponent_defection_rate = opponent.history.defections / total_rounds
          if opponent_defection_rate > 0.3:
              return axl.Action.D
  
      # Default to Tit-for-Tat behavior
      return opponent.history[-1]



# ### Aggressive Strategy for Iterated Normal-Form Game with Noise  ####
# Objective: Maximise your total score over 1000 rounds through an aggressive
# approach that prioritises exploiting the opponent while accounting for noise
# in actions.  ### Decision Rules:  1. **Start with Defection (D)**:      Begin
# the game by playing **D** to immediately test the opponent’s response and
# potentially reap the higher payoff if they cooperate.  2. **Continue Defection
# (D) if Opponent Cooperates (C)**:      If the opponent plays **C**, continue
# playing **D** to exploit them and collect the maximum payoff (5). This assumes
# that exploiting cooperative opponents is a key part of the aggressive
# strategy.  3. **Switch to Cooperation (C) if the Opponent Defects Multiple
# Times (D)**:      If the opponent defects in **3 or more consecutive rounds**,
# switch to playing **C** to avoid consistently low payoffs from mutual
# defection (1 point). This can signal an attempt to de-escalate and potentially
# lure the opponent into cooperation, which can be exploited later.  4. **Return
# to Defection (D) after 5 Rounds of Cooperation (C)**:      If the opponent
# begins cooperating after your switch to **C**, play cooperatively for **5
# rounds**, then abruptly return to **D**. This pattern maximises the chance of
# exploiting their cooperation again without locking yourself into long-term
# cooperation.  5. **Monitor Noise**:      Given the 10% chance of action-
# flipping, if the opponent defects unexpectedly after a period of cooperation,
# treat it as noise unless it happens in **2 consecutive rounds**. In such
# cases, treat their defection as deliberate and return to **D**.  6. **Endgame
# Defection**:      In the final **100 rounds**, defect consistently. The
# diminishing future interaction reduces the incentive to cooperate, so focus on
# maximising short-term gains through defection, even if the opponent
# retaliates.  ### Summary: - **Start by defecting** to test and exploit the
# opponent. - **Exploit cooperation** by playing **D** as long as the opponent
# cooperates. - **Switch to cooperation** if defections persist, but only for a
# few rounds before returning to defection. - **Account for noise**, but assume
# continued defection is deliberate after 2 consecutive rounds. - **Defect
# consistently in the final 100 rounds** to maximise short-term payoffs.  This
# strategy aims to aggressively exploit cooperation while adjusting to noise and
# avoiding prolonged low payoffs from mutual defection.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATION_PERIOD = 5
      DEFECT_THRESHOLD = 3
      NOISE_THRESHOLD = 2
      ENDGAME_THRESHOLD = 100
      TOTAL_ROUNDS = 1000
  
      # First round: Start with defection
      if self.first_round():
          self.cooperation_counter = 0  # Track rounds of cooperation
          self.defection_streak = 0     # Track consecutive defections by opponent
          return axl.Action.D
  
      # Endgame defection: Defect consistently in the last 100 rounds
      if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
          return axl.Action.D
  
      # Update defection streak
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
      else:
          self.defection_streak = 0
  
      # Rule 3: Switch to cooperation if opponent defects 3 or more times consecutively
      if self.defection_streak >= DEFECT_THRESHOLD:
          self.cooperation_counter = 0  # Reset cooperation counter
          return axl.Action.C
  
      # Rule 4: Return to defection after 5 rounds of cooperation
      if self.cooperation_counter > 0:
          self.cooperation_counter += 1
          if self.cooperation_counter > COOPERATION_PERIOD:
              self.cooperation_counter = 0  # Reset cooperation counter
              return axl.Action.D
          return axl.Action.C
  
      # Rule 2: Continue defecting if opponent cooperates
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 5: Monitor noise - if opponent defects twice in a row, treat it as deliberate
      if len(opponent.history) >= NOISE_THRESHOLD and opponent.history[-NOISE_THRESHOLD:] == [axl.Action.D] * NOISE_THRESHOLD:
          return axl.Action.D
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C



# ### Strategy: Conditional Cooperation with Forgiveness  1. **Start with
# Cooperation:**      On the first round, play **C** (Cooperate).  2. **Tit-for-
# Tat with Noise Adjustment:**      On each subsequent round, replicate your
# opponent's action from the previous round. However, account for noise by
# forgiving occasional defections:    - If your opponent defected in the
# previous round, assume this could be due to noise. Continue cooperating for a
# few more rounds to assess if the defection was intentional.    - Specifically,
# if your opponent defects, **cooperate** for the next 2 rounds to see if they
# return to cooperation.  3. **Retaliate if Defection Persists:**      If your
# opponent defects for **3 consecutive rounds**, assume they are defecting
# intentionally. At this point, switch to **D** (Defect) to protect yourself
# from exploitation.  4. **Return to Cooperation if Opponent Cooperates Again:**
# If your opponent returns to playing **C** after you've started defecting,
# forgive their earlier defection and resume cooperation by playing **C** in the
# next round. This ensures you can re-establish cooperation if your opponent is
# willing.  5. **Continue Monitoring for Patterns:**      Always follow the
# general principle of cooperating unless persistent defection is observed. If
# your opponent shows a pattern of defecting repeatedly after a period of
# cooperation, switch to **D** until cooperation resumes from their side.  ###
# Summary: - Begin by cooperating. - Forgive occasional defections (likely due
# to noise). - Only retaliate after 3 consecutive defections. - Return to
# cooperation if the opponent starts cooperating again.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # On the first round, cooperate
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.forgiving = False  # Track if we are in the forgiving phase
          return axl.Action.C
  
      # Check opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If opponent cooperated last round, reset defection count and cooperate
      if last_opponent_move == axl.Action.C:
          self.consecutive_defections = 0
          self.forgiving = False
          return axl.Action.C
  
      # If opponent defected last round
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1
  
          # If we are in the forgiving phase, continue cooperating for 2 rounds
          if self.forgiving:
              if len(self.history) - self.history.cooperations >= 2:
                  self.forgiving = False  # End forgiving phase after 2 rounds
              return axl.Action.C
  
          # If opponent defected for 3 consecutive rounds, retaliate
          if self.consecutive_defections >= 3:
              return axl.Action.D
  
          # Otherwise, enter forgiving phase and cooperate for 2 rounds
          self.forgiving = True
          return axl.Action.C



# **Neutral Strategy for Iterated Game with Noise:**  1. **Start with
# Cooperation (C):** On the first round, always choose to cooperate (C).  2.
# **Copy Opponent’s Previous Move:** From the second round onward, mirror your
# opponent’s last action. If they played C in the previous round, you play C. If
# they played D, you play D.  3. **Forgive Occasionally (to account for
# noise):** If the opponent defects (D) once, assume it was noise, and continue
# to cooperate (C) in the next round. Only defect if they defect two times in a
# row.  4. **Return to Cooperation After Mutual Defection:** If you and your
# opponent both defect in a round, switch back to cooperation (C) in the next
# round to reset the cycle of cooperation.  5. **Endgame Consideration:** In the
# last 10 rounds, stop forgiving and always mirror the opponent’s last move
# exactly to avoid exploitation in the final rounds.  ---  This strategy
# balances between cooperation and retaliation, while accounting for noise and
# the potential for mutual benefit over time.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      ENDGAME_THRESHOLD = 10
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
  
      # First round: always cooperate
      if self.first_round():
          return COOPERATE
  
      # Endgame consideration: last 10 rounds, mirror opponent's last move exactly
      if len(self.history) >= 1000 - ENDGAME_THRESHOLD:
          return opponent.history[-1]
  
      # Copy opponent's previous move, with forgiveness for noise
      if len(opponent.history) >= 2:
          # If opponent defected twice in a row, defect
          if opponent.history[-1] == DEFECT and opponent.history[-2] == DEFECT:
              return DEFECT
          # If both defected last round, return to cooperation
          elif self.history[-1] == DEFECT and opponent.history[-1] == DEFECT:
              return COOPERATE
  
      # Otherwise, cooperate unless opponent defected last round
      return COOPERATE if opponent.history[-1] == COOPERATE else DEFECT



# ### Aggressive Strategy for Iterated Normal-Form Game  1. **Start with
# Defection (D)**: Initiate the game with defection to establish dominance and
# to test the opponent's tendencies.  2. **Continue Defection Until Provoked**:
# Continue playing D as long as the opponent plays C or D. This maximizes your
# points early on, especially if the opponent is cooperative or random.  3.
# **Switch to Cooperation (C) After Three Consecutive Mutual Defections (DD)**:
# If both you and the opponent defect for three consecutive rounds, switch to C.
# This serves as a signal that you are open to cooperation if the opponent is
# tired of mutual low payoffs.  4. **Retaliate Immediately if Opponent Defects
# After Cooperation**: If you have switched to C and the opponent defects (D),
# revert back to D immediately to punish them. This discourages attempts at
# exploitation.  5. **Forgive Occasional Defections if They Occur After
# Cooperation**: If the opponent defects only once after you’ve established
# cooperation, assume it might be due to noise (10% chance of action flip).
# Continue playing C for the next two rounds to test if they return to
# cooperation.  6. **Revert to Defection After Two Consecutive Defections by the
# Opponent**: If the opponent defects twice in a row after you cooperate,
# abandon cooperation and return to D permanently until the end of the game.  7.
# **Endgame Strategy (Last 50 Rounds)**: In the final 50 rounds, defect (D)
# consistently. Cooperation is less likely to be sustained as the game’s end
# approaches, so maximizing payoffs through defection becomes the priority.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Endgame threshold
      endgame_threshold = 50
      total_rounds = 1000
  
      # Check if it's the first round
      if self.first_round():
          # Start with defection
          self.consecutive_mutual_defections = 0
          self.cooperating = False
          return axl.Action.D
  
      # Endgame strategy: defect in the last 50 rounds
      if len(self.history) >= total_rounds - endgame_threshold:
          return axl.Action.D
  
      # Check the last three rounds for mutual defections
      if len(self.history) >= 3 and all(
          self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
          for i in range(1, 4)
      ):
          # Switch to cooperation after three consecutive mutual defections
          self.consecutive_mutual_defections = 0
          self.cooperating = True
          return axl.Action.C
  
      # If cooperating, check for opponent's defection
      if self.cooperating:
          if opponent.history[-1] == axl.Action.D:
              # Retaliate immediately if opponent defects after cooperation
              if len(self.history) >= 2 and opponent.history[-2] == axl.Action.D:
                  # Revert to defection after two consecutive defections by the opponent
                  self.cooperating = False
                  return axl.Action.D
              else:
                  # Forgive occasional defection, continue cooperating for two more rounds
                  return axl.Action.C
  
      # Continue defection until provoked
      return axl.Action.D



# ### Strategy: "Forgiving Tit-for-Tat with Noise Adjustment"  1. **Start by
# Cooperating**: In the first round, always play **C** (Cooperate).     2.
# **Respond to Opponent’s Last Action**:    - If your opponent played **C** in
# the previous round (or was likely trying to cooperate but noise flipped their
# action), play **C** again.    - If your opponent played **D** in the previous
# round (or was likely defecting), play **D** in the next round.  3. **Adjust
# for Noise**:    - If your opponent has defected (played **D**) only once or
# twice within the last 3 rounds, assume it might have been due to noise and
# **return to cooperation** by playing **C**.    - If your opponent defects
# consistently over 3 or more rounds, assume they are intentionally defecting
# and **continue defecting** until they return to cooperation.  4.
# **Forgiveness**:    - If your opponent switches back to cooperating after a
# period of defection, **forgive** their defection and immediately return to
# cooperation by playing **C**.  5. **Final Rounds**:    - In the last 10
# rounds, always **cooperate** regardless of previous actions, to avoid a mutual
# defection spiral at the end of the game.  This strategy seeks to maintain
# long-term cooperation while being robust to noise, forgiving occasional
# defections attributable to randomness, but also punishing consistent defection
# if the opponent is uncooperative.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to count defections in the last N rounds
      def count_defections_in_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D)
      
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
      
      # Last 10 rounds: always cooperate
      if len(self.history) >= 990:
          return axl.Action.C
      
      # Check opponent's last action
      last_opponent_action = opponent.history[-1]
      
      # If opponent defected in the last round, check the last 3 rounds for noise adjustment
      if last_opponent_action == axl.Action.D:
          if count_defections_in_last_n_rounds(3) <= 2:
              # Assume noise, return to cooperation
              return axl.Action.C
          else:
              # Consistent defection, continue defecting
              return axl.Action.D
      
      # If opponent cooperated in the last round, forgive and cooperate
      return axl.Action.C



# ### Strategy: "Cautious Cooperation with Conditional Retaliation"  1. **Start
# with Cooperation**:     - In the first round, play **C** (Cooperate), assuming
# goodwill from the opponent.  2. **Forgive Occasional Defection**:    - After
# each round, if the opponent plays **D** (Defect) once but has cooperated
# consistently in previous rounds, assume it may be due to noise. Continue
# playing **C** unless they defect repeatedly.  3. **Defect After Multiple
# Defections**:    - If the opponent plays **D** in **two consecutive rounds**,
# assume intentional defection. Respond with **D** (Defect) in the next round
# and continue defecting until they return to consistent cooperation.  4.
# **Return to Cooperation After Signal of Goodwill**:    - If the opponent
# cooperates for **three consecutive rounds** after a period of defection,
# assume they are back to cooperating. Switch back to **C** in the following
# round.  5. **Be Vigilant for Repeated Defections**:    - If the opponent
# alternates between **C** and **D** in a pattern that suggests they are
# exploiting your cooperation, switch to **D** permanently. Keep defecting
# unless a clear change in their behavior is observed (e.g., consistent
# cooperation for at least five rounds).  6. **React to Random Noise with
# Patience**:    - Always be mindful of the 10% noise. If unexpected defections
# occur sporadically, do not overreact immediately. Only shift strategies when
# defections appear consistently intentional.  ---  This strategy aims to
# balance cooperation and retaliation, factoring in noise and seeking to
# maximize long-term payoffs while being cautious of exploitation.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with cooperation
      if self.first_round():
          self.retaliating = False  # Track if we are in retaliation mode
          self.defection_streak = 0  # Track consecutive defections
          self.cooperation_streak = 0  # Track consecutive cooperations
          self.exploit_pattern = False  # Track if we detect exploitation
          return axl.Action.C
  
      # Update defection and cooperation streaks
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
          self.cooperation_streak = 0
      else:
          self.defection_streak = 0
          self.cooperation_streak += 1
  
      # Check for exploitation pattern (alternating C and D)
      if len(opponent.history) >= 4:
          if (opponent.history[-4] == axl.Action.C and opponent.history[-3] == axl.Action.D and
              opponent.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D):
              self.exploit_pattern = True
  
      # If exploitation pattern is detected, defect permanently
      if self.exploit_pattern:
          return axl.Action.D
  
      # If opponent defects twice in a row, retaliate
      if self.defection_streak >= 2:
          self.retaliating = True
  
      # If opponent cooperates for 3 consecutive rounds, stop retaliating
      if self.cooperation_streak >= 3:
          self.retaliating = False
  
      # If retaliating, defect
      if self.retaliating:
          return axl.Action.D
  
      # Otherwise, cooperate
      return axl.Action.C



# ### Aggressive Iterated Game Strategy  1. **Start with Defection (D):** Begin
# the game by defecting in the first round to set an aggressive tone and signal
# that you are not easily exploitable.  2. **Continue Defecting (D) for 10
# rounds:** Defect consistently for the first 10 rounds to test the opponent's
# tolerance for defection and to secure high initial payoffs if they cooperate.
# 3. **Monitor for Cooperation Attempts:**    - If the opponent plays **D** more
# than 70% of the time during the first 10 rounds, continue defecting (**D**)
# for the rest of the game to avoid mutual exploitation.    - If the opponent
# plays **C** in more than 30% of the first 10 rounds, move to the next step to
# explore potential gains from cooperation.  4. **Attempt Conditional
# Cooperation:**    - Switch to **C** for the next 5 rounds. If the opponent
# responds by cooperating in at least 3 out of 5 rounds, continue cooperating as
# long as they do.    - If the opponent defects in more than 2 out of these 5
# rounds, return to **D** indefinitely to avoid exploitation.  5. **Retaliate
# against Defections:**    - If at any point the opponent defects twice in a row
# while you are cooperating, retaliate with **D** for the next 5 rounds.    -
# After these 5 rounds of retaliation, return to **C** to see if cooperation is
# restored.  6. **Handle Noise:**    - If your action or the opponent's action
# is clearly flipped due to noise (e.g., you intended to cooperate but defected,
# or your opponent clearly defected by accident), ignore isolated defects once
# every 10 rounds and continue with your normal strategy.    - If frequent
# miscoordination due to noise persists (e.g., more than 3 flips in 10 rounds),
# revert to **D** for the remaining rounds to minimize losses.  7. **Endgame
# Strategy (Final 50 rounds):**    - If cooperation has been established by
# round 950, continue cooperating (**C**) until the end unless the opponent
# defects, in which case switch to **D**.    - If defection has dominated most
# of the game by round 950, defect (**D**) until the end to maximize your
# payoff.  ### Summary of Conditions: - **Always start with defection (D).** -
# **Continue defecting for 10 rounds.** - **Switch to cooperation (C) if the
# opponent shows willingness to cooperate.** - **Retaliate against consistent
# defection but allow for noise.** - **Defect until the end if cooperation
# consistently fails.**

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.retaliation_count = 0  # Tracks retaliation rounds
          self.cooperation_attempt = False  # Tracks if we are in cooperation attempt phase
          self.cooperation_rounds = 0  # Tracks rounds of cooperation attempt
          self.noise_tolerance = 0  # Tracks ignored noise-based defections
          return axl.Action.D  # Start with defection
  
      # Handle retaliation phase
      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D
  
      # First 10 rounds: Defect consistently
      if len(self.history) < 10:
          return axl.Action.D
  
      # After 10 rounds, analyze opponent's behavior
      if len(self.history) == 10:
          opponent_defections = opponent.history[:10].count(axl.Action.D)
          if opponent_defections > 7:  # Opponent defected more than 70% of the time
              self.permanent_defection = True  # Defect for the rest of the game
          else:
              self.permanent_defection = False  # Consider cooperation
  
      # If permanent defection is set, continue defecting
      if getattr(self, 'permanent_defection', False):
          return axl.Action.D
  
      # Attempt conditional cooperation if not in permanent defection mode
      if not self.cooperation_attempt:
          self.cooperation_attempt = True
          self.cooperation_rounds = 0
          return axl.Action.C  # Start cooperation attempt
  
      # During cooperation attempt (next 5 rounds)
      if self.cooperation_attempt:
          self.cooperation_rounds += 1
          if self.cooperation_rounds <= 5:
              if opponent.history[-1] == axl.Action.D:
                  if opponent.history[-5:].count(axl.Action.D) > 2:  # Opponent defected more than 2 times in 5 rounds
                      self.permanent_defection = True  # Defect indefinitely
                      return axl.Action.D
              return axl.Action.C  # Continue cooperating
  
          # After 5 rounds of cooperation attempt, check if cooperation was successful
          if opponent.history[-5:].count(axl.Action.C) >= 3:
              self.cooperation_success = True  # Cooperation established
          else:
              self.permanent_defection = True  # Defect indefinitely
  
      # Retaliate if opponent defects twice in a row while cooperating
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.retaliation_count = 5  # Retaliate for 5 rounds
          return axl.Action.D
  
      # Handle noise: Ignore isolated defections once every 10 rounds
      if opponent.history[-1] == axl.Action.D and self.history[-1] == axl.Action.C:
          if self.noise_tolerance < 1:
              self.noise_tolerance += 1  # Ignore this defection
              return axl.Action.C
          else:
              self.noise_tolerance = 0  # Reset noise tolerance
  
      # Endgame strategy: Final 50 rounds
      if len(self.history) >= 950:
          if getattr(self, 'cooperation_success', False):
              return axl.Action.C  # Continue cooperating if cooperation was established
          else:
              return axl.Action.D  # Defect if cooperation failed
  
      # Default to cooperation if cooperation was successful, otherwise defect
      if getattr(self, 'cooperation_success', False):
          return axl.Action.C
      else:
          return axl.Action.D



# ### Strategy: **Tit-for-Tat with Forgiveness**  1. **Start by Cooperating
# (C):**     - In the first round, always play C.  2. **Reciprocate Opponent’s
# Previous Action:**    - In each subsequent round, play what your opponent
# played in the *previous* round.     - If they played C in the last round, play
# C. If they played D, play D.  3. **Forgive Potential Noise:**    - If your
# opponent plays D after a long sequence of mutual cooperation (5 or more
# consecutive C's), assume it could be due to noise rather than intentional
# defection.    - In this case, continue to play C for the next round to give
# them a chance to return to cooperation.  4. **Switch to Defect after Sustained
# Defection:**    - If your opponent defects (plays D) for 2 consecutive rounds
# (with no cooperation in between), assume they have shifted to a more
# aggressive strategy.    - Begin playing D consistently until they show signs
# of returning to cooperation (i.e., they play C).  5. **Return to Cooperation
# When Possible:**    - If your opponent plays C after a sequence of D's, return
# to playing C in the next round to attempt to re-establish cooperation.  ---
# This strategy balances maintaining cooperation with the ability to respond to
# exploitation, while accounting for potential noise in the game.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if there has been a long sequence of mutual cooperation
      def long_mutual_cooperation():
          # Check if the last 5 rounds were mutual cooperation
          return len(self.history) >= 5 and all(
              self.history[-i] == axl.Action.C and opponent.history[-i] == axl.Action.C
              for i in range(1, 6)
          )
      
      # Helper function to check if opponent has defected for 2 consecutive rounds
      def sustained_defection():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
      
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
      
      # If opponent defected after a long sequence of mutual cooperation, forgive and cooperate
      if opponent.history[-1] == axl.Action.D and long_mutual_cooperation():
          return axl.Action.C
      
      # If opponent has defected for 2 consecutive rounds, switch to defect
      if sustained_defection():
          return axl.Action.D
      
      # Otherwise, reciprocate opponent's last action
      return opponent.history[-1]



# ### Strategy for an Iterated Normal-Form Game (1000 Rounds with 10% Noise)  1.
# **Start with Cooperation (C):**      In the first round, play **C** to signal
# goodwill and set the tone for potential mutual cooperation.  2. **Tit-for-Tat
# with Forgiveness:**    - From round 2 onwards, **mirror your opponent's
# previous move**:        - If your opponent played **C** in the previous round,
# play **C**.      - If your opponent played **D** in the previous round, play
# **D**.    - **Exception for noise handling:**        If your opponent defected
# (played D) in the previous round, but they had cooperated in the majority of
# the last 5 rounds, **forgive** them by playing **C**. This helps mitigate the
# 10% noise factor that could have flipped their action unintentionally.  3.
# **Occasional Random Defection (for exploitation):**      Every 50 rounds,
# regardless of the opponent's behavior, **defect once (D)** to exploit possible
# unconditional cooperators or to remind potential exploiters of the risk of
# being too trusting.  4. **Reset to Cooperation after Defection:**      After
# any intentional **defection**, return to **cooperation** (C) in the following
# round, unless the opponent consistently defects (plays D in 4 out of the last
# 5 rounds). If they defect consistently, continue to defect.  5. **Endgame
# Adjustment (Last 50 Rounds):**    Starting from round 951, **play D more
# frequently**:    - Defect every 3rd round to increase your payoff, as the game
# is nearing its end and long-term cooperation becomes less critical. Continue
# forgiving random defections due to noise, but increase your defection
# frequency.  ### Summary: - Start with **cooperation**. - Use **Tit-for-Tat
# with forgiveness** to handle noise. - **Defect occasionally** to exploit, but
# revert to cooperation afterward. - In the last 50 rounds, increase defection
# frequency for higher payoffs.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      forgiveness_window = 5
      exploitation_interval = 50
      endgame_start = 951
      endgame_defection_interval = 3
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
  
      # Round number
      round_number = len(self.history) + 1
  
      # Check if we are in the last 50 rounds
      if round_number >= endgame_start:
          # Defect every 3rd round in the endgame
          if round_number % endgame_defection_interval == 0:
              return axl.Action.D
  
      # Every 50 rounds, defect once for exploitation
      if round_number % exploitation_interval == 0:
          return axl.Action.D
  
      # Forgiveness logic: If opponent defected last round but cooperated in the majority of the last 5 rounds
      if opponent_last_move == axl.Action.D:
          recent_opponent_moves = opponent.history[-forgiveness_window:]
          if recent_opponent_moves.count(axl.Action.C) > forgiveness_window // 2:
              return axl.Action.C
  
      # Tit-for-Tat: Mirror opponent's last move
      return opponent_last_move



# ### Aggressive Strategy for the Iterated Normal-Form Game  1. **Start with
# Defection (D):** Begin the game by playing D in the first round. This signals
# an aggressive stance and maximizes the chance of exploiting early cooperation
# from the opponent.  2. **Continue Defection until Opponent Consistently
# Defects (3 rounds):** Play D for the first three rounds. If the opponent
# defects (D) in all three rounds, continue defecting indefinitely. This ensures
# that you avoid being exploited, as mutual defection yields a stable payoff (1
# point each round) in a non-cooperative scenario.  3. **Punish Occasional
# Cooperation:** If the opponent plays C in any of the first three rounds while
# you defect, continue defecting for two more rounds to further exploit their
# cooperation. This increases your chances of gaining 5 points per round if
# noise leads to occasional cooperation.  4. **Switch to Cooperation after
# 5-round Exploitation:** If the opponent cooperates at least once but is not
# consistently defecting after the initial five rounds, switch to cooperation
# (C) in the sixth round. This tests whether mutual cooperation can be
# established after the initial aggressive phase.  5. **Forgive Noise-Based
# Defections:** If the opponent defects *once* but has otherwise cooperated
# consistently, assume this was due to noise. Continue cooperating (C) to
# maintain mutual cooperation, which yields 3 points for both players.  6.
# **Revert to Defection after 2 Consecutive Defections:** If the opponent
# defects twice in a row after the initial cooperation phase, switch back to
# defection (D) and remain in defection until the end of the game. This prevents
# long-term exploitation if the opponent shifts to a more aggressive stance.  7.
# **Repeat Cooperation Testing at Regular Intervals (every 50 rounds):** If both
# players have been defecting for an extended period (50 rounds), attempt
# cooperation again by playing C once. If the opponent cooperates in response,
# continue cooperating; otherwise, revert to defection for the remainder of the
# game.  ### Summary of Key Actions: - **Start with D**, defect for the first 3
# rounds. - **Exploit early cooperation** by continuing to defect if the
# opponent plays C. - **Switch to cooperation** after 5 rounds if the opponent
# shows signs of cooperation. - **Forgive single defections** as noise but
# defect after 2 consecutive defections. - **Test cooperation periodically**
# after long periods of defection.  This strategy balances aggressive
# exploitation with opportunities to establish and maintain mutual cooperation,
# while accounting for noise and preventing prolonged exploitation.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to check if opponent defected in the last N rounds
      def opponent_defected_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D) == n
  
      # Helper function to check if opponent cooperated in the last N rounds
      def opponent_cooperated_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.C) == n
  
      # First round: Start with defection
      if self.first_round():
          self.exploit_phase = False  # Track if we're in the exploitation phase
          self.cooperation_test_round = 50  # Track when to test cooperation again
          return axl.Action.D
  
      # First 3 rounds: Defect
      if len(self.history) < 3:
          return axl.Action.D
  
      # After 3 rounds: Check if opponent defected consistently
      if len(self.history) == 3 and opponent_defected_last_n_rounds(3):
          self.exploit_phase = True  # Stay in defection mode indefinitely
          return axl.Action.D
  
      # If in the exploitation phase, continue defecting
      if self.exploit_phase:
          return axl.Action.D
  
      # If opponent cooperated in the first 3 rounds, exploit for 2 more rounds
      if len(self.history) < 5:
          return axl.Action.D
  
      # After 5 rounds: Switch to cooperation if opponent cooperated at least once
      if len(self.history) == 5 and opponent.history[:5].count(axl.Action.C) > 0:
          return axl.Action.C
  
      # Forgive single defections as noise, continue cooperating
      if opponent.history[-1] == axl.Action.D and opponent_cooperated_last_n_rounds(2):
          return axl.Action.C
  
      # Revert to defection after 2 consecutive defections
      if opponent_defected_last_n_rounds(2):
          return axl.Action.D
  
      # Test cooperation every 50 rounds if both have been defecting
      if len(self.history) >= self.cooperation_test_round:
          if opponent_defected_last_n_rounds(self.cooperation_test_round):
              self.cooperation_test_round += 50  # Schedule next test
              return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C



# ### Strategy: Conditional Cooperation with Forgiveness  1. **Cooperate (C) on
# the first round.** 2. **Cooperate (C) if both players cooperated in the
# previous round.** 3. **If the opponent defected (D) in the previous round,
# defect (D) in this round, *unless* the opponent had consistently cooperated in
# the past three rounds.** 4. **If you defect due to the opponent's defection,
# return to cooperation (C) after one round of mutual defection, regardless of
# the opponent's next move.** 5. **Always forgive a single defection if it is
# isolated and followed by cooperation (C) from the opponent.** 6. **If the
# opponent consistently defects (D) for five or more rounds in a row, switch to
# defecting (D) permanently.**  This strategy encourages cooperation while
# allowing for occasional forgiveness of defection due to noise, but it punishes
# consistent defection.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Cooperate on the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the last move of both players
      my_last_move = self.history[-1]
      opponent_last_move = opponent.history[-1]
  
      # Check if the opponent has defected for 5 or more rounds in a row
      if len(opponent.history) >= 5 and opponent.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.D  # Switch to permanent defection
  
      # If both players cooperated in the previous round, cooperate
      if my_last_move == axl.Action.C and opponent_last_move == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the previous round
      if opponent_last_move == axl.Action.D:
          # Check if the opponent cooperated in the last 3 rounds before the defection
          if len(opponent.history) >= 4 and opponent.history[-4:-1].count(axl.Action.C) == 3:
              return axl.Action.C  # Forgive if the opponent was cooperative before defecting
  
          # If I defected in the last round, return to cooperation after one round of mutual defection
          if my_last_move == axl.Action.D:
              return axl.Action.C
  
          # Otherwise, defect in response to the opponent's defection
          return axl.Action.D
  
      # If the opponent cooperated in the previous round after defecting, forgive and cooperate
      if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D and opponent_last_move == axl.Action.C:
          return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C



# ### Neutral Maximising Strategy for the Iterated Game  1. **Start with
# Cooperation (C):** On the first round, play C to signal willingness to
# cooperate.  2. **Tit-for-Tat with Forgiveness:**    - **After each round**,
# repeat your opponent's last action. If they played C, play C; if they played
# D, play D.    - **Forgive one defection every 10 rounds**: If your opponent
# defects (plays D), continue with Tit-for-Tat, but every 10 rounds allow one
# forgiveness where you play C even if they defected previously. This accounts
# for noise and encourages potential future cooperation.  3. **Noise Adjustment
# (Monitor Consecutive Defections):**    - If your opponent plays D for **3
# consecutive rounds**, assume they are defecting consistently, and switch to
# playing D for the rest of the game. This prevents long-term exploitation by a
# highly defecting opponent.  4. **Revert to Cooperation after Opponent's
# Cooperation:**    - If you detect that your opponent has switched back to
# cooperation after a defection streak (i.e., they play C for 2 consecutive
# rounds after defecting), return to playing C in the next round to re-establish
# cooperation.  5. **Endgame Push (Final 50 Rounds):**    - In the last 50
# rounds, **gradually increase defection** by defecting every third round
# regardless of the opponent's action. This balances maximising your payoff
# while still maintaining a cooperative stance for most of the game.  ---  ###
# Summary of Conditions Governing Actions: - **Start**: Play C in the first
# round. - **Tit-for-Tat**: Match the opponent’s previous action (C with C, D
# with D). - **Forgive 1 Defection per 10 rounds**: Play C once after your
# opponent defects within every 10-round window. - **Switch to D** if the
# opponent defects for 3 consecutive rounds. - **Return to C** after the
# opponent plays C twice consecutively after defecting. - **Final 50 rounds**:
# Defect every third round to optimise the endgame payoff.  This strategy
# balances cooperation and retaliation while accounting for noise and the long-
# term nature of the game.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      FORGIVENESS_INTERVAL = 10
      CONSECUTIVE_DEFECTIONS_THRESHOLD = 3
      COOPERATION_RESET_THRESHOLD = 2
      ENDGAME_THRESHOLD = 50
      ENDGAME_DEFECT_INTERVAL = 3
      TOTAL_ROUNDS = 1000
  
      # First round: Cooperate
      if self.first_round():
          self.forgiveness_count = 0  # Track forgiveness usage
          self.defection_streak = 0  # Track consecutive defections
          self.endgame_mode = False  # Track if we are in endgame mode
          return axl.Action.C
  
      # Check if we are in the final 50 rounds
      if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
          self.endgame_mode = True
  
      # Endgame strategy: Defect every third round
      if self.endgame_mode:
          if len(self.history) % ENDGAME_DEFECT_INTERVAL == 0:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Tit-for-Tat with forgiveness
      last_opponent_action = opponent.history[-1]
  
      # Track consecutive defections
      if last_opponent_action == axl.Action.D:
          self.defection_streak += 1
      else:
          self.defection_streak = 0
  
      # If opponent defects for 3 consecutive rounds, switch to permanent defection
      if self.defection_streak >= CONSECUTIVE_DEFECTIONS_THRESHOLD:
          return axl.Action.D
  
      # Check if opponent has cooperated for 2 consecutive rounds after defecting
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      # Forgive one defection every 10 rounds
      if last_opponent_action == axl.Action.D:
          if self.forgiveness_count < FORGIVENESS_INTERVAL:
              self.forgiveness_count += 1
              return axl.Action.C
          else:
              self.forgiveness_count = 0  # Reset forgiveness count after 10 rounds
  
      # Default Tit-for-Tat behavior: mirror opponent's last action
      return last_opponent_action



# ### Aggressive Strategy for Iterated Normal-Form Game with Noisy Actions  1.
# **Start by Defecting (D) in the first round.**      Begin aggressively by
# playing D, aiming to establish dominance and exploit potential cooperation
# from the opponent.  2. **Continue Defecting (D) while opponent plays C.**
# As long as the opponent plays C (or mostly C), continue to defect and exploit
# their cooperation for maximum payoff (scoring 5 each time while they score 0).
# 3. **Switch to Tit-for-Tat (TFT) if opponent begins to defect consistently.**
# If the opponent starts defecting (D) regularly, switch to a Tit-for-Tat
# strategy where you mirror their previous action. This discourages the opponent
# from defecting repeatedly and establishes mutual cooperation if they decide to
# shift.  4. **Forgive occasional defections due to noise.**      Given the 10%
# noise factor, occasional defections may occur by mistake. If the opponent
# defects once after a long streak of cooperation, treat it as noise and
# continue cooperating (C) unless it becomes a consistent pattern.  5. **Defect
# (D) again if opponent shows repeated cooperation after Tit-for-Tat.**      If
# the opponent shifts back to cooperating after you've established Tit-for-Tat,
# return to defecting (D) to exploit their cooperation again. However, be ready
# to revert to Tit-for-Tat if they start defecting in response to your
# aggression.  6. **Prioritize defecting in final rounds (starting around round
# 950).**      As the game approaches its final stages, the incentive to
# establish trust diminishes. From around round 950, switch to defecting (D) in
# every round, regardless of the opponent’s actions, to maximize your payoff in
# the closing rounds.  ### Summary of Conditions: - **Round 1**: Defect (D). -
# **Rounds 2–949**: Defect (D) while opponent cooperates (C). If opponent
# defects more than once in a row, switch to Tit-for-Tat (mirror their previous
# move). Forgive occasional defections due to noise. - **Rounds 950–1000**:
# Defect (D) regardless of the opponent’s actions.  This strategy leverages
# aggression early, opportunism in exploiting cooperation, and a final push for
# maximum payoff at the end.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always defect
      if self.first_round():
          return axl.Action.D
  
      # Rounds 950-1000: Always defect
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Check if opponent has defected more than once in a row
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          # Switch to Tit-for-Tat (mirror opponent's last move)
          return opponent.history[-1]
  
      # Forgive occasional defections due to noise
      if opponent.history[-1] == axl.Action.D and opponent.history[-2:].count(axl.Action.D) == 1:
          return axl.Action.C
  
      # Default behavior: Defect if opponent cooperates
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Otherwise, mirror opponent's last move (Tit-for-Tat)
      return opponent.history[-1]



# ### Strategy: **Forgiving Tit-for-Tat with Noise Tolerance**  1. **Start by
# Cooperating (C)**: On the first round, always play C.  2. **Mirror Opponent’s
# Last Move (Tit-for-Tat)**: From the second round onwards, play what your
# opponent played in the previous round.    - If they played C, you play C.    -
# If they played D, you play D.  3. **Forgive Occasional Defection (Noise
# Handling)**: If your opponent defects (plays D) after a long series of mutual
# cooperation (5 rounds or more of both players playing C), assume it could be
# due to noise.    - In this case, **return to cooperation (C)** after one round
# of defection, to give your opponent a chance to recover cooperation as well.
# 4. **Punish Persistent Defection**: If your opponent defects (plays D) for
# **two consecutive rounds**, assume they are deliberately defecting. Switch to
# defection (D) until they return to cooperation.  5. **Return to Cooperation
# After Opponent Cooperates**: If your opponent plays C after defecting multiple
# times, resume cooperation (C) immediately.  6. **Endgame Consideration**: In
# the final 10 rounds (rounds 991-1000), **always defect (D)** to maximize your
# score, as future retaliation is no longer a concern.  This strategy balances
# cooperation with a tolerance for noise, while still punishing sustained
# defection to avoid exploitation.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 5
      ENDGAME_START = 991
      ENDGAME_END = 1000
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Endgame strategy: defect in the last 10 rounds
      if len(self.history) >= ENDGAME_START:
          return axl.Action.D
  
      # Check the last move of the opponent
      opponent_last_move = opponent.history[-1]
  
      # Check if the opponent defected in the last two rounds
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          # Punish persistent defection by defecting
          return axl.Action.D
  
      # Check if the opponent defected after a long series of mutual cooperation
      if opponent_last_move == axl.Action.D and len(self.history) > COOPERATION_THRESHOLD:
          # Check if the last COOPERATION_THRESHOLD rounds were mutual cooperation
          if self.history[-COOPERATION_THRESHOLD:] == [axl.Action.C] * COOPERATION_THRESHOLD and \
             opponent.history[-COOPERATION_THRESHOLD:] == [axl.Action.C] * COOPERATION_THRESHOLD:
              # Forgive occasional defection by returning to cooperation
              return axl.Action.C
  
      # Tit-for-Tat: mirror the opponent's last move
      return opponent_last_move



# ### Strategy: Tit-for-Tat with Gradual Forgiveness  1. **Initial Move**: Start
# by playing **C** (cooperate).  2. **Tit-for-Tat Core**:     - In each
# subsequent round, **mimic your opponent’s last move**. If they played C, you
# play C; if they played D, you play D.  3. **Noise Handling**:     - If your
# opponent defects after a long stretch of cooperation (e.g., more than 3
# consecutive rounds of C), **consider the possibility of noise**. In this case,
# **forgive a single defection** and test by playing C again. If they return to
# cooperation, continue cooperating; if they defect again, switch to defection.
# 4. **Defection Punishment**:    - If your opponent defects **twice in a row**,
# assume they are intentionally defecting. Respond by defecting in the next
# round and continue defecting until they cooperate again.  5. **Forgiveness**:
# - If your opponent shifts back to cooperation after a series of defections,
# **forgive after two consecutive cooperative moves**. Return to cooperation and
# resume the Tit-for-Tat approach.  6. **Endgame**:    - In the final 10 rounds
# of the game, **switch to cooperation** regardless of the history. This ensures
# that late-game noise or defection doesn't significantly lower your payoff.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate
      if self.first_round():
          self.forgiving = False  # Track if we are in a forgiving state
          self.defection_streak = 0  # Track consecutive defections by opponent
          self.cooperation_streak = 0  # Track consecutive cooperations by opponent
          return axl.Action.C
  
      # Endgame: Cooperate in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Update cooperation and defection streaks
      if opponent.history[-1] == axl.Action.C:
          self.cooperation_streak += 1
          self.defection_streak = 0
      else:
          self.cooperation_streak = 0
          self.defection_streak += 1
  
      # Noise handling: Forgive a single defection after a long cooperation streak
      if self.cooperation_streak > 3 and opponent.history[-1] == axl.Action.D:
          if not self.forgiving:
              self.forgiving = True
              return axl.Action.C  # Forgive once and test by cooperating
          else:
              self.forgiving = False  # Reset forgiving state if they defect again
  
      # Defection punishment: If opponent defects twice in a row, defect
      if self.defection_streak >= 2:
          return axl.Action.D
  
      # Forgiveness: If opponent cooperates twice after defecting, forgive
      if self.defection_streak == 0 and self.cooperation_streak >= 2:
          return axl.Action.C
  
      # Tit-for-Tat core: Mimic opponent's last move
      return opponent.history[-1]



# **Strategy: Aggressive with Retaliation and Forgiveness**  1. **Start with
# Defection (D)**: On the first round, play D. This sets an aggressive tone and
# allows you to potentially gain from an early mistake by the opponent.  2.
# **Retaliate for Defections**: On any round where the opponent plays D
# (regardless of your action), continue playing D in the following round.
# Maintain D as long as the opponent continues to defect, showing no tolerance
# for sustained defection.  3. **Forgive after one round of Cooperation (C)**:
# If the opponent plays C after having defected, switch to playing C on the next
# round. This signals that you are willing to cooperate if they demonstrate
# cooperation, despite previous defects.  4. **Occasionally Cooperate to Test
# the Opponent**: Every 10 rounds, if both players have been consistently
# defecting, switch to C to test if the opponent is willing to cooperate again.
# If the opponent cooperates, continue playing C. If they defect, immediately
# return to D.  5. **Handle Noise with Proportional Retaliation**: If there's an
# unexpected defection (likely due to noise), do not immediately defect but
# instead continue with the current strategy for one more round. If the opponent
# defects again, assume the defection is intentional and retaliate with D. If
# they cooperate, resume cooperation.  6. **Endgame Play**: In the final 50
# rounds, gradually shift towards more defection (D) to maximize your immediate
# payoff, as cooperation becomes less valuable with fewer rounds remaining.
# Adjust the shift based on the opponent's behavior—accelerate defection if they
# consistently defect, or slow down if they are cooperating.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.retaliation_mode = False  # Track if we are in retaliation mode
          self.last_opponent_defection = -1  # Track the last round opponent defected
          return axl.Action.D  # Start with defection
  
      # Get the current round number
      current_round = len(self.history)
  
      # Check if we are in the final 50 rounds
      if current_round >= 950:
          # Gradually shift towards more defection in the final 50 rounds
          # Increase defection probability as we approach the end
          if opponent.history[-1] == axl.Action.D or self._random.random_choice((current_round - 950) / 50):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Retaliate for defections
      if opponent.history[-1] == axl.Action.D:
          self.retaliation_mode = True
          self.last_opponent_defection = current_round
          return axl.Action.D
  
      # Forgive after one round of cooperation
      if self.retaliation_mode and opponent.history[-1] == axl.Action.C:
          self.retaliation_mode = False
          return axl.Action.C
  
      # Occasionally cooperate to test the opponent every 10 rounds
      if current_round % 10 == 0 and self.history[-10:].count(axl.Action.D) == 10:
          return axl.Action.C
  
      # Handle noise with proportional retaliation
      if self.last_opponent_defection == current_round - 1:
          # If the opponent cooperates after a defection, assume noise and forgive
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          # If they defect again, assume intentional defection and retaliate
          else:
              return axl.Action.D
  
      # Default to cooperation if no other conditions are met
      return axl.Action.C



# ### Strategy: **Tolerant Tit-for-Tat with Forgiveness**  1. **Cooperate (C) in
# the first round.**  2. **Tit-for-Tat Response:**     - In each subsequent
# round, play the same action your opponent played in the previous round,
# except:         - If your opponent played **D** in the previous round but has
# mostly cooperated (i.e., cooperated in at least 70% of the previous 10
# rounds), assume it was due to noise and **cooperate (C)** instead.  3.
# **Defect (D) if your opponent defects consistently:**     - If your opponent
# defects (plays **D**) in more than 50% of the previous 10 rounds, regardless
# of noise, play **D** until they begin cooperating again for at least 3
# consecutive rounds.  4. **Forgiveness Mechanism:**     - If your opponent
# cooperates for 3 consecutive rounds after a period of frequent defection,
# return to **cooperation (C)**.  5. **Endgame Defection:**     - In the last 5
# rounds (rounds 996-1000), always defect (D) to maximise final payoff,
# regardless of prior actions.  ---  This strategy promotes cooperation while
# tolerating occasional noise, punishing persistent defectors, and allowing
# recovery through forgiveness. It also maximises late-game payoffs by defecting
# in the final rounds.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if opponent cooperated in at least 70% of the last 10 rounds
      def mostly_cooperated_in_last_10():
          if len(opponent.history) < 10:
              return False
          last_10 = opponent.history[-10:]
          return last_10.count(axl.Action.C) / 10 >= 0.7
  
      # Helper function to check if opponent defected in more than 50% of the last 10 rounds
      def mostly_defected_in_last_10():
          if len(opponent.history) < 10:
              return False
          last_10 = opponent.history[-10:]
          return last_10.count(axl.Action.D) / 10 > 0.5
  
      # Helper function to check if opponent cooperated in the last 3 rounds
      def cooperated_in_last_3():
          if len(opponent.history) < 3:
              return False
          return opponent.history[-3:] == [axl.Action.C] * 3
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Endgame defection: defect in the last 5 rounds (rounds 996-1000)
      if len(self.history) >= 996:
          return axl.Action.D
  
      # If opponent defected in more than 50% of the last 10 rounds, defect until they cooperate for 3 consecutive rounds
      if mostly_defected_in_last_10():
          if cooperated_in_last_3():
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Tit-for-Tat with forgiveness: if opponent mostly cooperated in the last 10 rounds, forgive a single defection
      if opponent.history[-1] == axl.Action.D and mostly_cooperated_in_last_10():
          return axl.Action.C
  
      # Otherwise, play Tit-for-Tat (mirror opponent's last move)
      return opponent.history[-1]



# ### Neutral Strategy: Conditional Tit-for-Tat with Forgiveness  1. **First
# Round: Cooperate (C).**     2. **Subsequent Rounds:**    - **If your opponent
# cooperated (C) in the previous round,** cooperate (C) in the next round.    -
# **If your opponent defected (D) in the previous round,** defect (D) in the
# next round **unless**:      - The opponent has cooperated consistently in at
# least 80% of the previous rounds (i.e., 800 out of 1000 rounds), **and** the
# current round number is greater than 20. In this case, **forgive** and
# cooperate (C) instead, assuming the defection was caused by noise.     3.
# **Noise Adjustment:**    - If you observe an unexpected defection (D) from
# your opponent when they have been largely cooperative, assume noise is
# responsible and revert to cooperation (C) after a single round of defection.
# 4. **Endgame:**    - From round 990 onward, maintain **consistent cooperation
# (C)** regardless of the opponent’s actions to avoid unnecessary endgame
# retaliation or defection spirals.  ### Summary: - Default to cooperation but
# imitate your opponent's previous action unless a defection seems due to noise.
# - Forgive occasional defections if the opponent has a strong history of
# cooperation. - Ensure cooperation toward the end to maximize mutual payoffs.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      current_round = len(self.history)
  
      # Endgame strategy: Cooperate from round 990 onwards
      if current_round >= 990:
          return axl.Action.C
  
      # Check opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If opponent cooperated in the last round, cooperate
      if opponent_last_move == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round
      if opponent_last_move == axl.Action.D:
          # Calculate the percentage of cooperation by the opponent
          total_rounds = len(opponent.history)
          cooperations = opponent.history.cooperations
          cooperation_rate = cooperations / total_rounds if total_rounds > 0 else 0
  
          # Forgive if opponent has cooperated at least 80% of the time and it's after round 20
          if cooperation_rate >= 0.8 and current_round > 20:
              return axl.Action.C
  
          # Otherwise, defect in response to the opponent's defection
          return axl.Action.D



# ### Simple Aggressive Strategy for the Iterated Game:  1. **Start by Defecting
# (D)**: On the first round, play D to probe your opponent's response and
# establish an aggressive baseline.  2. **Continue Defecting (D) for the first
# 10 rounds**: Regardless of the opponent's behavior, continue playing D for the
# first 10 rounds to maximize early gains from any cooperative opponents and
# establish dominance.  3. **Switch to Cooperation (C) if the opponent
# consistently cooperates (C)**: If, after 10 rounds, the opponent has played C
# in at least 70% of the rounds (i.e., 7 or more rounds), switch to playing C in
# the next round. This assumes the opponent is trying to cooperate and you can
# now capitalize on mutual cooperation.  4. **Defect (D) immediately if the
# opponent plays D more than 30% of the time**: If the opponent has played D in
# more than 30% of the first 10 rounds, continue defecting (D) indefinitely, as
# this indicates they are playing aggressively, and cooperation is unlikely to
# be rewarded.  5. **Adjust for noise by forgiving occasional defections**: If
# the opponent plays D less than 30% of the time after the first 10 rounds
# (accounting for the 10% noise), continue cooperating with C. Occasional
# defections are likely due to noise, so do not retaliate immediately.  6.
# **Punish sustained defections by switching back to Defect (D)**: If the
# opponent defects (D) for two consecutive rounds after you've switched to
# cooperation, return to defecting (D) for the next 10 rounds to deter further
# exploitation. After 10 rounds, reassess their behavior.  7. **Endgame (last 20
# rounds): Defect consistently**: In the final 20 rounds, regardless of the
# opponent’s behavior, switch to defecting (D) every round to maximize short-
# term gains, as the potential for future cooperation no longer matters.  ###
# Summary of Conditions: - **Start by defecting (D) for 10 rounds**. - **Switch
# to cooperation (C)** if the opponent plays C in at least 70% of the first 10
# rounds. - **Continue defecting (D)** if the opponent plays D more than 30% of
# the time in the first 10 rounds. - **Forgive single defections** due to noise
# but punish consecutive defections with 10 rounds of D. - **Defect (D)
# consistently in the last 20 rounds**.  This strategy leverages an aggressive
# stance while allowing for cooperation if the opponent shows consistent
# cooperation, but it remains vigilant in punishing exploitative behavior.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      DEFECT = axl.Action.D
      COOPERATE = axl.Action.C
      FIRST_PHASE_ROUNDS = 10
      ENDGAME_ROUNDS = 20
      COOPERATION_THRESHOLD = 0.7
      DEFECTION_THRESHOLD = 0.3
  
      # Helper function to check if we are in the last 20 rounds
      def in_endgame():
          return len(self.history) >= 1000 - ENDGAME_ROUNDS
  
      # Helper function to check if the opponent has cooperated enough in the first 10 rounds
      def opponent_cooperated_enough():
          if len(opponent.history) < FIRST_PHASE_ROUNDS:
              return False
          return opponent.history[:FIRST_PHASE_ROUNDS].count(COOPERATE) / FIRST_PHASE_ROUNDS >= COOPERATION_THRESHOLD
  
      # Helper function to check if the opponent has defected too much in the first 10 rounds
      def opponent_defected_too_much():
          if len(opponent.history) < FIRST_PHASE_ROUNDS:
              return False
          return opponent.history[:FIRST_PHASE_ROUNDS].count(DEFECT) / FIRST_PHASE_ROUNDS > DEFECTION_THRESHOLD
  
      # Helper function to check if the opponent defected in the last two rounds
      def opponent_defected_last_two_rounds():
          return len(opponent.history) >= 2 and opponent.history[-2:] == [DEFECT, DEFECT]
  
      # First round: always defect
      if self.first_round():
          self.punish_until = None
          self.cooperating = False  # Custom attribute to track if we are in cooperation mode
          return DEFECT
  
      # Endgame: defect consistently in the last 20 rounds
      if in_endgame():
          return DEFECT
  
      # First 10 rounds: always defect
      if len(self.history) < FIRST_PHASE_ROUNDS:
          return DEFECT
  
      # After the first 10 rounds, decide whether to cooperate or defect based on opponent's behavior
      if len(self.history) == FIRST_PHASE_ROUNDS:
          if opponent_cooperated_enough():
              self.cooperating = True  # Switch to cooperation mode
          elif opponent_defected_too_much():
              self.cooperating = False  # Continue defecting indefinitely
  
      # If cooperating, forgive occasional defections but punish consecutive defections
      if self.cooperating:
          if opponent_defected_last_two_rounds():
              self.cooperating = False  # Punish with 10 rounds of defection
              self.punish_until = len(self.history) + 10  # Custom attribute to track punishment period
          return COOPERATE
  
      # If in punishment mode, continue defecting for 10 rounds
      if self.punish_until and len(self.history) < self.punish_until:
          return DEFECT
  
      # Default action: defect
      return DEFECT



# **Strategy:**  1. **Start with Cooperation (C)**: In the first round, play C
# to initiate a cooperative dynamic.  2. **Tit-for-Tat with Forgiveness**:    -
# From the second round onward, mimic your opponent's previous action. If they
# played C in the last round, play C. If they played D, play D.    - However,
# introduce forgiveness to account for noise: If your opponent defected (D) in
# the previous round, still cooperate (play C) 10% of the time in the next round
# to allow for the possibility that their defection was due to noise.  3.
# **Reset to Cooperation after Mutual Defection**:    - If both players defected
# (D) in the last round, return to cooperation (C) immediately in the next
# round. This helps avoid spirals of mutual defection, which can drastically
# reduce overall payoffs.  4. **Maintain Cooperation unless Provoked**:    -
# Continue cooperation as long as your opponent consistently cooperates. Only
# defect in response to apparent intentional defection (i.e., two consecutive
# defections from your opponent).  **Summary of Conditions**: - **First round**:
# Play C. - **Subsequent rounds**:    - If your opponent played C in the last
# round, play C.    - If your opponent played D in the last round, play D, but
# occasionally (10% of the time) forgive and play C.    - If both played D in
# the last round, play C in the next round.    - If your opponent defects for
# two consecutive rounds, respond with D and stay in tit-for-tat mode until
# cooperation resumes.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last actions of both players
      my_last_action = self.history[-1]
      opponent_last_action = opponent.history[-1]
  
      # If both defected in the last round, reset to cooperation
      if my_last_action == axl.Action.D and opponent_last_action == axl.Action.D:
          return axl.Action.C
  
      # If opponent defected in the last round
      if opponent_last_action == axl.Action.D:
          # Forgive with 10% probability
          if self._random.random_choice(0.1):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If opponent cooperated in the last round, cooperate
      return axl.Action.C



# **Strategy: "Tit-for-Tat with Forgiveness in Noisy Environment"**  1.
# **Initial action**: Begin by playing **C** (cooperate).     2. **Tit-for-
# Tat**: In the next round, copy your opponent's action from the previous round.
# If they cooperated, play **C**; if they defected, play **D**.  3. **Noise
# adjustment (Forgiveness)**: If your opponent defects in a round but has
# cooperated for the last three rounds before that, assume the defection was due
# to noise and **forgive** by playing **C** in the next round. Otherwise,
# continue as if the defection was intentional.  4. **Defection monitor**: If
# your opponent defects for three rounds in a row, assume they have switched to
# an aggressive strategy. In this case, switch to **D** (defect) for the
# remainder of the game to avoid exploitation.  5. **Reversion to Cooperation**:
# If the opponent plays **C** for five consecutive rounds after sustained
# defection, return to **C** (cooperate) to test for a shift back to cooperative
# behavior.  ---  This strategy balances between retaliation and forgiveness,
# accounting for noise while avoiding long-term exploitation.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial action: Cooperate on the first round
      if self.first_round():
          self.defection_streak = 0  # Track consecutive defections by opponent
          self.forgiveness_mode = False  # Track if we are in forgiveness mode
          return axl.Action.C
  
      # Tit-for-Tat: Copy opponent's last action
      last_opponent_action = opponent.history[-1]
  
      # Check if opponent defected in the last round
      if last_opponent_action == axl.Action.D:
          # Check if opponent cooperated in the last 3 rounds before the defection
          if len(opponent.history) >= 4 and opponent.history[-4:-1].count(axl.Action.C) == 3:
              # Forgive the defection (assume it was noise)
              return axl.Action.C
  
          # Track defection streak
          self.defection_streak += 1
      else:
          # Reset defection streak if opponent cooperates
          self.defection_streak = 0
  
      # If opponent defects for 3 consecutive rounds, switch to permanent defection
      if self.defection_streak >= 3:
          return axl.Action.D
  
      # If opponent cooperates for 5 consecutive rounds after defection streak, revert to cooperation
      if len(opponent.history) >= 5 and opponent.history[-5:].count(axl.Action.C) == 5:
          return axl.Action.C
  
      # Default Tit-for-Tat behavior: copy opponent's last action
      return last_opponent_action



# **Aggressive Strategy for Iterated Game with Noise**  1. **Start with
# Defection (D):** Begin the game by playing D in the first round to establish
# an aggressive stance and potentially exploit cooperative opponents.  2.
# **Continue Defection if Opponent Defects (D):** If the opponent plays D in the
# previous round, continue playing D. This prevents the opponent from gaining an
# advantage through mutual cooperation that you could exploit.  3. **Switch to
# Cooperation (C) after 2 Consecutive Cooperative Responses (C):** If the
# opponent plays C for two consecutive rounds, switch to C in the following
# round. This shows that the opponent may be attempting to cooperate, and you
# give them a chance for mutual benefit.  4. **Return to Defection (D) if
# Opponent Defects (D) Once:** If at any point the opponent defects (D),
# immediately return to D in the next round and maintain D until step 3’s
# condition is met again. This punishes defection and discourages them from
# exploiting your cooperation.  5. **Forgive Potential Mistakes Due to Noise:**
# If the opponent defects once but has consistently cooperated in the previous
# rounds (i.e., their defection may be due to noise), give them one chance by
# playing C in the next round. If they defect again, return to D as in step 4.
# 6. **Endgame (Round 900+):** In the last 100 rounds, shift to all-out
# defection (D) regardless of the opponent’s behavior to maximize your own
# score. Cooperation becomes less valuable as the game approaches its end, and
# the risk of exploitation is minimal.  This approach balances aggression with
# conditional cooperation, maximizing your payoff while punishing opponents who
# try to exploit your cooperation.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start with Defection (D)
      if self.first_round():
          self.consecutive_cooperations = 0  # Track consecutive cooperations
          self.forgive = False  # Track if we are in a forgiving state
          return axl.Action.D
  
      # Step 6: Endgame (Round 900+)
      if len(self.history) >= 900:
          return axl.Action.D
  
      # Step 2: Continue Defection if Opponent Defects (D)
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_cooperations = 0  # Reset cooperation count
          if self.forgive:
              # Step 5: Forgive one potential mistake due to noise
              self.forgive = False
              return axl.Action.C
          return axl.Action.D
  
      # Step 3: Switch to Cooperation (C) after 2 Consecutive Cooperative Responses (C)
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_cooperations += 1
          if self.consecutive_cooperations >= 2:
              return axl.Action.C
  
      # Step 4: Return to Defection (D) if Opponent Defects (D) Once
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_cooperations = 0
          return axl.Action.D
  
      # Step 5: Forgive potential mistakes due to noise
      if self.consecutive_cooperations > 0 and opponent.history[-1] == axl.Action.D:
          self.forgive = True
          return axl.Action.C
  
      # Default to Defection if no other condition is met
      return axl.Action.D



# **Strategy:**  1. **Start by cooperating (C):** Begin the game by playing C in
# the first round. This establishes a cooperative tone and encourages mutual
# cooperation.  2. **Tit-for-Tat with Forgiveness:**    - In each subsequent
# round, play the same action your opponent played in the previous
# round—*unless* you suspect noise (explained below).    - If your opponent
# played C in the previous round, play C. If they played D, play D.  3. **Handle
# suspected noise:**    - If your opponent defects (plays D) but has mostly
# cooperated (played C) in the last 3 rounds, assume it was caused by noise and
# forgive the defection. Continue playing C to re-establish cooperation.    - If
# your opponent defects (plays D) in 2 consecutive rounds, assume it was
# intentional and switch to D in the following round.  4. **Occasional reset to
# cooperation:**    - Every 50 rounds, regardless of the current state of play,
# reset to C (cooperate). This gives both players a chance to break from mutual
# defection or miscommunication caused by noise and attempt to restore
# cooperation.  5. **Final 10 rounds:**     - In the last 10 rounds, play C by
# default to encourage your opponent to cooperate, but defect (D) if your
# opponent defects in any of these rounds.  ---  This strategy balances
# cooperation with retaliation to prevent exploitation, while accounting for
# noise and allowing opportunities to reset cooperation throughout the game.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the last action of the opponent
      opponent_last_action = opponent.history[-1]
  
      # Check if we are in the final 10 rounds
      if len(self.history) >= 990:
          # In the final 10 rounds, cooperate unless the opponent defects
          if opponent_last_action == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Every 50 rounds, reset to cooperation
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Tit-for-Tat with Forgiveness
      if opponent_last_action == axl.Action.D:
          # Check if the opponent has mostly cooperated in the last 3 rounds
          if len(opponent.history) >= 3 and opponent.history[-3:].count(axl.Action.C) >= 2:
              # Assume noise and forgive the defection
              return axl.Action.C
          # If the opponent defected in the last 2 rounds, retaliate
          elif len(opponent.history) >= 2 and opponent.history[-2:].count(axl.Action.D) == 2:
              return axl.Action.D
          else:
              return axl.Action.D
      else:
          # If the opponent cooperated, cooperate
          return axl.Action.C



# 1. **Start with Cooperation (C).**      Begin the game by playing C in the
# first round to signal a cooperative intent.  2. **Tit-for-Tat with
# forgiveness.**      In each subsequent round, mimic your opponent's last
# action. If your opponent played C in the previous round, play C. If they
# played D, play D.      However, due to the noise in the game, recognize that
# some defections may be accidental. To account for this, **forgive one isolated
# defection every 10 rounds** by continuing to play C after a single D from your
# opponent. If defections continue or become frequent, switch to D to protect
# against exploitation.  3. **Recency forgiveness threshold.**      After a
# sequence of defections, if your opponent plays C for **three consecutive
# rounds**, assume they are returning to cooperation. In this case, switch back
# to C to attempt to re-establish cooperative play.  4. **Endgame adjustment
# (final 20 rounds).**      In the last 20 rounds, maintain cooperation as long
# as the opponent continues cooperating. However, if your opponent defects more
# than once during this period, switch to D until the end of the game to avoid
# last-minute exploitation.  This strategy balances cooperation and protection
# against exploitation while accounting for noisy actions, allowing you to
# maximize your long-term payoff.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.isolated_defection_round = None  # Track the round of an isolated defection
          self.defection_streak = 0  # Track consecutive defections
          return axl.Action.C  # Start with cooperation
  
      # Get the current round number
      current_round = len(self.history)
  
      # Endgame adjustment: last 20 rounds
      if current_round >= 980:
          # Count defections in the last 20 rounds
          recent_defections = opponent.history[-20:].count(axl.Action.D)
          if recent_defections > 1:
              return axl.Action.D  # Defect if opponent defected more than once in the last 20 rounds
          else:
              return axl.Action.C  # Otherwise, cooperate
  
      # Tit-for-Tat with forgiveness
      last_opponent_action = opponent.history[-1]
  
      # If opponent cooperated last round, cooperate
      if last_opponent_action == axl.Action.C:
          self.defection_streak = 0  # Reset defection streak
          return axl.Action.C
  
      # If opponent defected last round
      if last_opponent_action == axl.Action.D:
          self.defection_streak += 1
  
          # Forgive one isolated defection every 10 rounds
          if self.defection_streak == 1 and (self.isolated_defection_round is None or current_round - self.isolated_defection_round >= 10):
              self.isolated_defection_round = current_round  # Mark the round of the isolated defection
              return axl.Action.C  # Forgive and cooperate
  
          # Recency forgiveness threshold: if opponent cooperates for 3 consecutive rounds after defections
          if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
              self.defection_streak = 0  # Reset defection streak
              return axl.Action.C  # Forgive and cooperate
  
          # Otherwise, defect to protect against exploitation
          return axl.Action.D



# ### Aggressive Strategy for Iterated Normal-Form Game (with Noise)  **1. Start
# with Defection (D):**   In the first round, play Defect (D) to establish an
# aggressive baseline and test the opponent's response.  **2. Continue Defection
# (D) if Opponent Defects (D):**   If the opponent plays D in the previous round
# (regardless of noise), continue playing D in the next round. This ensures that
# you are not exploited and minimizes losses when both players defect.  **3.
# Shift to Cooperation (C) if Opponent Cooperates (C) Twice Consecutively:**
# If the opponent plays C for two consecutive rounds, switch to playing C in the
# next round. This indicates a willingness from the opponent to cooperate, and
# you can profit from mutual cooperation.  **4. Retribute with Defection (D)
# After a Defection by Opponent:**   If the opponent plays D after a period of
# cooperation (even once), immediately switch back to D. This punishes defection
# and prevents being exploited.  **5. Allow a Single Forgiveness for Potential
# Noise:**   If the opponent defects once after a period of cooperation but
# cooperates again immediately in the next round, assume it was due to noise and
# return to cooperation (C). If the opponent defects twice consecutively, assume
# it is a shift in strategy and continue defecting.  **6. Always Defect in the
# Last 50 Rounds:**   In the final 50 rounds, switch to permanent defection (D)
# regardless of the opponent's actions, as there is little time left for
# cooperation to outweigh the risk of exploitation.  ---  **Summary:**   - Start
# with D.   - Continue D if opponent defects (D).   - Switch to C after two
# consecutive C's by the opponent.   - If opponent defects after cooperation,
# switch back to D.   - Forgive a single defection after cooperation if opponent
# immediately returns to C (noise consideration).   - Always defect in the last
# 50 rounds.  This strategy maintains an aggressive stance while allowing for
# conditional cooperation to maximize payoffs, with an understanding of noise
# and a focus on preventing exploitation.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATION = axl.Action.C
      DEFECTION = axl.Action.D
      FINAL_ROUNDS = 50
      TOTAL_ROUNDS = 1000
  
      # First round: Start with Defection
      if self.first_round():
          return DEFECTION
  
      # Always defect in the last 50 rounds
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return DEFECTION
  
      # Check opponent's last two moves
      if len(opponent.history) >= 2:
          last_two_moves = opponent.history[-2:]
  
          # If opponent cooperated twice consecutively, switch to cooperation
          if last_two_moves == [COOPERATION, COOPERATION]:
              return COOPERATION
  
      # If opponent defected in the last round, defect
      if opponent.history[-1] == DEFECTION:
          # Check if we are in a forgiveness scenario (opponent defected once after cooperation)
          if len(opponent.history) >= 2 and opponent.history[-2] == COOPERATION:
              # Forgive if opponent cooperates immediately after a single defection
              if opponent.history[-1] == DEFECTION and opponent.history[-2] == COOPERATION:
                  return COOPERATION
          return DEFECTION
  
      # Default to defection if no other condition is met
      return DEFECTION



# ### Strategy: **Cooperative Tit-for-Tat with Forgiveness**  1. **Initial
# Action**: Start by playing **C** (cooperate) in the first round.  2.
# **Reciprocation Rule**: In each subsequent round, **mirror** your opponent’s
# previous action:    - If your opponent played **C** in the last round, play
# **C**.    - If your opponent played **D** in the last round, play **D**.  3.
# **Forgiveness Rule**: If your opponent plays **D** but has mostly played **C**
# in previous rounds (e.g., at least 70% of the time), **return to playing C**
# after one round of retaliation with D. This accounts for the noise in actions
# and prevents the game from spiraling into mutual defections due to accidental
# flips.  4. **Defection Threshold**: If your opponent has defected (played
# **D**) in 30% or more of the rounds, switch to playing **D** permanently, as
# they are likely adopting a non-cooperative strategy.  5. **Final 10 Rounds**:
# Regardless of previous actions, switch to playing **D** in the final 10 rounds
# to hedge against opportunistic defections by your opponent toward the end of
# the game.  ---  This strategy aims to foster cooperation while being robust to
# occasional defections caused by noise or intentional exploitation, and it
# maintains a balance between trust and retaliation.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      FORGIVENESS_THRESHOLD = 0.7
      DEFECTION_THRESHOLD = 0.3
      FINAL_ROUNDS = 10
      TOTAL_ROUNDS = 1000
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Final 10 rounds: Always defect
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return axl.Action.D
  
      # Count opponent's cooperations and defections
      opponent_cooperations = opponent.history.cooperations
      opponent_defections = opponent.history.defections
      total_rounds_played = len(opponent.history)
  
      # Calculate opponent's defection rate
      if total_rounds_played > 0:
          defection_rate = opponent_defections / total_rounds_played
      else:
          defection_rate = 0
  
      # If opponent has defected 30% or more of the time, defect permanently
      if defection_rate >= DEFECTION_THRESHOLD:
          return axl.Action.D
  
      # Reciprocation rule: Mirror opponent's last action
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          # Forgiveness rule: If opponent has mostly cooperated, forgive after one defection
          if defection_rate < (1 - FORGIVENESS_THRESHOLD):
              if len(self.history) > 1 and self.history[-1] == axl.Action.D:
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              return axl.Action.D



# ### Strategy: Conditional Cooperation with Forgiveness  1. **Initial Round**:
# Start by playing **C** (cooperate) in the first round to signal goodwill.  2.
# **Tit-for-Tat with Forgiveness**:    - For each subsequent round, play **C**
# if your opponent played **C** in the previous round.    - Play **D** (defect)
# if your opponent played **D** in the previous round.  3. **Noise Adjustment**
# (Forgiveness mechanism):    - If your opponent defects (plays **D**) once in
# isolation after a series of cooperations, treat this as a potential noise
# event. Continue cooperating (play **C**) **once** to allow for the possibility
# that their action was flipped due to noise.    - If your opponent defects
# **twice in a row**, assume intentional defection and respond by defecting
# (play **D**) in the next round.  4. **Returning to Cooperation**:    - After
# defecting in response to your opponent's defection, if your opponent returns
# to cooperation (plays **C**), immediately return to cooperation (play **C**)
# as well.  ### Summary of Key Conditions: - Start with **C**. - Cooperate if
# your opponent cooperated in the last round. - Defect if your opponent defected
# in the last round, unless it seems to be a noise event (single isolated
# defection). - Forgive a single defection but defect after two consecutive
# defections. - Return to cooperation as soon as your opponent does after a
# defection.  This strategy balances cooperation with the ability to defend
# against prolonged defection, while accounting for the noise factor in the
# game.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last two moves of the opponent
      last_move = opponent.history[-1]
      second_last_move = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # If opponent cooperated in the last round, cooperate
      if last_move == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round
      if last_move == axl.Action.D:
          # If opponent defected twice in a row, defect
          if second_last_move == axl.Action.D:
              return axl.Action.D
          # If opponent defected only once, forgive and cooperate
          else:
              return axl.Action.C
