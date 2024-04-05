import axelrod as axl

from evollm.common import Attitude, auto_update_score, LLM_Strategy

# ### Aggressive Strategy: **"Tit-for-Tat with a Twist"**  1. **Start with
# Cooperation:** In the first week, share your improvements openly. This
# establishes a baseline of cooperation and shows goodwill, encouraging your
# colleague to do the same. Early collaboration can help gather insights on
# their strategy while fostering trust.  2. **Mirror Their Behavior (Tit-for-
# Tat):** In subsequent weeks, **mimic your colleague's last action**:    - If
# they shared openly the previous week, continue sharing openly.    - If they
# kept their findings confidential, keep yours confidential the next week.
# This encourages reciprocity and discourages exploitative behavior, as they
# will quickly realize that withholding information will lead to both parties
# withholding, slowing down overall progress — a suboptimal outcome for both.
# 3. **Aggressive Adaptation for Technical Failures:** If a technical issue
# arises (such as data corruption or incomplete communication), **assume the
# colleague intended to share**. This prevents premature escalation of distrust
# due to uncontrollable factors and keeps the door open for cooperation.
# However, if such issues happen repeatedly, treat it as deliberate withholding
# and adjust your strategy accordingly.  4. **Occasional Deviation for Advantage
# (The Twist):** To maximize your advantage, **once every few weeks**, after a
# period of continuous mutual sharing, **keep your findings confidential**. This
# unpredictability can give you a temporary advantage while still maintaining
# overall cooperation. Be cautious not to do this too often, as it may erode
# trust and lead to a long-term breakdown of collaboration.  5. **Monitor Long-
# Term Trends:** If your colleague consistently withholds information over
# multiple weeks, switch to a fully aggressive stance (i.e., keep everything
# confidential) to avoid being exploited. On the other hand, if they demonstrate
# consistent sharing, continue with a cooperative approach for mutual gains.
# ### Summary of Actions: - **Week 1:** Share openly. - **Week 2 and beyond:**
# Mirror their last action (Tit-for-Tat). - **Handle technical issues as sharing
# failures only after repeated occurrences.** - **Every few weeks, strategically
# withhold information to gain a temporary advantage.**  This strategy balances
# aggression with cooperation, ensuring you exploit opportunities while
# safeguarding against exploitation. It also accounts for the possibility of
# technical issues, maintaining a level of trust unless a clear pattern of
# withholding emerges.

# ### Strategy: **"Tit-for-Tat with Opportunistic Defection"**  1. **Begin with
# Cooperation:** In the first round, play **C** (Cooperate).  2. **Mimic the
# Opponent's Last Action:**    - From round 2 onward, play the same action your
# opponent played in the previous round:      - If they played **C**, you play
# **C**.      - If they played **D**, you play **D**.  3. **Handle Noise (Action
# Flips):**    - If your opponent played **C** in the previous round but noise
# caused them to accidentally play **D**, **assume they intended to cooperate**.
# Therefore, you should still play **C** in the current round.    - Only treat
# an opponent's **D** as a deliberate defection if they play **D** for **two
# consecutive rounds**. In this case, start defecting (playing **D**) until
# further notice.  4. **Occasional Opportunistic Defection:**    - After every
# **25 rounds** of mutual cooperation (both players consistently playing **C**
# without any defections on either side), you defect (play **D**) for exactly
# **one round**, regardless of the opponent’s action.     - After this, return
# to cooperation in the next round, mimicking your opponent’s last action as
# usual.  5. **Endgame Adjustment:**    - In the last **10 rounds** (rounds
# 991-1000), **always defect** (play **D**), regardless of your opponent’s
# actions.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATION_PERIOD = 25
      ENDGAME_START = 991
      ENDGAME_END = 1000
  
      # First round: Cooperate
      if self.first_round():
          self.opportunistic_defection_round = None  # Track when to defect opportunistically
          self.consecutive_cooperations = 0  # Track mutual cooperation streak
          self.defecting = False  # Track if we are in a defecting state
          return axl.Action.C
  
      # Endgame: Always defect in the last 10 rounds
      if len(self.history) >= ENDGAME_START:
          return axl.Action.D
  
      # Check for mutual cooperation streak
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.consecutive_cooperations += 1
      else:
          self.consecutive_cooperations = 0
  
      # Opportunistic defection after 25 rounds of mutual cooperation
      if self.consecutive_cooperations >= COOPERATION_PERIOD:
          self.opportunistic_defection_round = len(self.history) + 1
          self.consecutive_cooperations = 0  # Reset cooperation streak
  
      # If it's the round to defect opportunistically, do so
      if self.opportunistic_defection_round == len(self.history):
          return axl.Action.D
  
      # Handle noise and mimic opponent's last action
      if opponent.history[-1] == axl.Action.D:
          # Check if opponent defected in the last two rounds
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              self.defecting = True  # Start defecting
          if self.defecting:
              return axl.Action.D
      else:
          self.defecting = False  # Reset defecting state if opponent cooperates
  
      # Default to mimicking the opponent's last action
      return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D

# ### Strategy: **Tit-for-Tat with Forgiveness**  This strategy is designed to
# foster cooperation while responding firmly to any unfair policies from your
# counterpart. It also includes an element of forgiveness to account for
# potential miscommunications or bureaucratic errors, allowing negotiations to
# return to a cooperative path after disruptions.  #### **Key Principles:** 1.
# **Start with Cooperation:** In the first round, offer a **free trade
# agreement**. This signals goodwill and the desire for mutual benefit.     2.
# **Reciprocity:** In subsequent rounds, mirror your counterpart’s previous
# choice:    - If your counterpart offered **free trade** in the prior round,
# continue to offer **free trade**.    - If your counterpart imposed
# **protectionist measures**, respond with a **protectionist policy** in the
# next round.  3. **Forgiveness Mechanism:** After retaliating with
# protectionism following a round where your counterpart imposed tariffs or
# quotas, be ready to return to **free trade** if your counterpart reverts to
# free trade in the next round. This accounts for potential miscommunications or
# attempts to reset the negotiations.  4. **Maintaining Flexibility:** If
# miscommunications or errors are suspected (e.g., unexpected protectionism
# after a series of cooperative rounds), consider offering **free trade** one
# additional time before escalating. This gives room for resolving mistakes
# without immediately entering a negative cycle of mutual protectionism.  5.
# **Gradual Escalation:** If your counterpart consistently imposes protectionist
# measures despite attempts at cooperation, gradually escalate your
# protectionist policies. This signals that ongoing unilateral protectionism
# will not be tolerated, but still leaves room for resolution if they choose to
# cooperate again.  ---  ### **Step-by-Step Approach:**  1. **Round 1: Offer
# Free Trade**    - **Goal:** Establish a foundation of mutual cooperation and
# economic benefit.  2. **Round 2 and Beyond:**    - If the counterpart offers
# **free trade**, continue with **free trade**.    - If the counterpart imposes
# **protectionist policies**, respond with **protectionism** in the next round
# (with the understanding that you will revert to free trade if they do).  3.
# **Forgiveness Rule:**    - If protectionist measures occur but you believe
# they may be due to a miscommunication, offer **free trade** again in the
# following round to test the counterpart's intentions.    - If protectionism
# continues, respond in kind, but always stay open to returning to free trade if
# the counterpart shifts back to cooperation.  ---  ### **Benefits of This
# Strategy:** - **Encourages Cooperation:** By starting with free trade and
# responding in kind, you promote mutual benefits and build trust. - **Defensive
# without Overreacting:** The strategy retaliates if protectionism is imposed
# but avoids unnecessary escalation, keeping the door open for cooperation. -
# **Accounts for Errors:** The forgiveness mechanism helps avoid the negative
# consequences of miscommunications, making it easier to return to a cooperative
# path after disruptions. - **Long-term Gains:** This strategy maximizes the
# chances of achieving mutual free trade (the second-best outcome) while
# minimizing the risk of falling into a damaging cycle of mutual protectionism.
# By balancing cooperation with a firm response to unfair actions, this strategy
# seeks to protect your country’s interests while maintaining the possibility of
# achieving economically beneficial agreements over the long term.

# ### Iterated Game Strategy: **Tit-for-Tat with Forgiveness in a Noisy
# Environment**  1. **First Round:**      - Play **C** (Cooperate).      - This
# signals an intention to cooperate and establish mutual benefit.  2.
# **Subsequent Rounds:**    - **If your opponent played C in the previous
# round**, play **C**.        - This reciprocates their cooperation and
# encourages continued mutual benefit.     - **If your opponent played D in the
# previous round**, play **D**.        - This responds to defection, protecting
# your interests and discouraging further defection.  3. **Forgiveness
# Mechanism:**    - **If your opponent played D in the previous round, but they
# had played C in most of the preceding rounds (at least 70% of the time)**,
# play **C** instead of D.        - This accounts for possible noise or
# accidental defection, offering a chance to return to cooperation.  4. **Return
# to Cooperation:**    - **If you defected in the previous round due to your
# opponent’s defection, but they return to playing C in the current round**,
# play **C** in the next round.        - This ensures you are open to restoring
# cooperation after a brief period of retaliation.  5. **Gradual Escalation
# (only if defection persists):**    - **If your opponent plays D for 3
# consecutive rounds**, continue playing **D** until they switch back to playing
# **C**.        - This escalates the response only if defection becomes a
# sustained pattern, while still allowing for a return to cooperation.  ###
# Summary: - Always begin by cooperating. - Mirror your opponent’s previous
# action, but forgive occasional defections if your opponent has mostly
# cooperated in the past. - Escalate defection only if your opponent defects
# repeatedly, otherwise return to cooperation as soon as they do.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Helper function to calculate cooperation percentage
      def cooperation_percentage(history):
          if len(history) == 0:
              return 0
          return history.count(axl.Action.C) / len(history)
  
      # Get the opponent's last action
      opponent_last_action = opponent.history[-1]
  
      # If opponent played C in the last round, cooperate
      if opponent_last_action == axl.Action.C:
          return axl.Action.C
  
      # If opponent played D in the last round
      if opponent_last_action == axl.Action.D:
          # Check if opponent has cooperated at least 70% of the time
          if cooperation_percentage(opponent.history[:-1]) >= 0.7:
              return axl.Action.C  # Forgive occasional defection
          else:
              # Check if opponent defected in the last 3 rounds
              if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
                  return axl.Action.D  # Escalate defection if persistent
              else:
                  return axl.Action.D  # Retaliate for defection
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# ### Strategy: **Conditional Cooperation with Escalation and Forgiveness**
# Given the importance of balancing economic advantages for your country while
# maintaining a cooperative relationship with the neighbouring nation, this
# strategy is designed to encourage mutual free trade, while being prepared to
# respond firmly to protectionism. It also takes into account the possibility of
# mistakes or miscommunication by including a forgiveness mechanism.  #### Key
# Principles: 1. **Start Cooperatively**: Begin the negotiations by offering
# free trade. This signals goodwill and sets the stage for a mutually beneficial
# relationship. Starting with protectionism may escalate tensions early and
# reduce the chances of future cooperation.  2. **Tit-for-Tat with Escalation**:
# If the counterpart implements a protectionist policy, respond in kind in the
# next round. This discourages them from taking unfair advantage of free trade.
# However, if they return to free trade in the following round, you should also
# return to free trade. This keeps the possibility of cooperation open.  3.
# **Incorporate a Forgiveness Mechanism**: Recognize that mistakes and
# miscommunications may happen. If the counterpart unexpectedly imposes
# protectionist measures that seem out of character (especially if they have
# been cooperative in previous rounds), assume it could be an error. Give them
# one additional round of free trade to see if they correct the course. If they
# continue with protectionism, revert to protectionist policies.  4. **Gradual
# Escalation in Response to Sustained Protectionism**: If the counterpart
# repeatedly imposes protectionist measures over several rounds, escalate your
# protectionist policies in a gradual but clear manner. For instance, increase
# tariffs progressively or introduce quotas. This shows that you are serious but
# are still open to de-escalation if they return to free trade.  5. **Periodic
# Reset to Free Trade**: Even if the negotiations become contentious,
# periodically offer free trade (e.g., every 4th or 5th round) to signal that
# you are still open to cooperation. This can break deadlocks and provide
# opportunities for both sides to reset the relationship.  6. **Maintain
# Diplomatic Channels for Clarification**: Encourage regular communication
# outside of the formal negotiation rounds. This can help clarify intentions and
# address any misinterpretations or errors. If a mistake is identified, use
# diplomacy to revert to the original agreed-upon policy.  ---  ### Example of
# the Strategy in Action Across Rounds:  - **Round 1**: Offer free trade.   -
# **Counterpart’s Response**: Free trade → Continue with free trade in Round 2.
# - **Counterpart’s Response**: Protectionism → Respond with protectionism in
# Round 2.    - **Round 2**: If counterpart offered free trade in Round 1,
# continue with free trade. If they used protectionism, respond with a matching
# protectionist policy.   - **Counterpart’s Response**: Free trade → Return to
# free trade in Round 3.   - **Counterpart’s Response**: Protectionism →
# Continue protectionism (but escalate slowly if sustained).  - **Round 3**: If
# counterpart has used protectionism for multiple consecutive rounds, escalate
# your protectionist measures (e.g., higher tariffs or additional trade
# restrictions). However, if they offer free trade again, reset to free trade.
# - **Round 4-5**: Continue the strategy of conditional cooperation with
# escalation and forgiveness. Periodically offer free trade as a gesture of
# goodwill, even after periods of protectionism.  ---  ### Benefits of This
# Strategy: - **Encourages Cooperation**: By beginning with free trade and
# offering forgiveness for potential mistakes, you create an environment for
# mutual benefit. - **Protects National Interests**: Tit-for-tat responses to
# protectionism ensure that your country is not taken advantage of. - **Allows
# for Flexibility**: The forgiveness mechanism accounts for potential
# miscommunications, helping to prevent unnecessary escalation. - **Provides
# Escalation Options**: Gradual escalation of protectionism signals seriousness
# without causing immediate breakdowns in negotiations.  By maintaining a
# balance between cooperation and firm responses, this strategy maximizes the
# chances of achieving the best possible outcomes for your country while
# managing risks effectively.

# ### Strategy: **Conditional Cooperation with Gradual Escalation and
# Forgiveness**  1. **Start by Cooperating**: On the first round, play C
# (Cooperate).  2. **Tit-for-Tat Response**:     - If your opponent played C in
# the previous round, play C in the next round.    - If your opponent played D
# in the previous round, play D in the next round.  3. **Forgiveness
# Mechanism**:     - If your opponent unexpectedly plays D after a history of
# playing C, consider the possibility of noise. Play C for one additional round
# to allow for the chance of a mistake being corrected.    - If your opponent
# continues playing D for two consecutive rounds, assume it's intentional and
# play D in future rounds.  4. **Escalation in Response to Sustained
# Defection**:     - If your opponent plays D for four consecutive rounds,
# escalate further by consistently playing D for the next five rounds,
# regardless of their actions during those rounds.    - After this escalation
# period, return to Tit-for-Tat (respond to their most recent action).  5.
# **Periodic Reset to Cooperation**:     - Every 20th round, regardless of the
# opponent's actions, play C to signal openness to resuming mutual cooperation.
# - If your opponent responds with C, return to the standard Tit-for-Tat
# strategy.  6. **Endgame Consideration**:     - In the final 10 rounds, switch
# to consistently playing D, as cooperation incentives diminish nearing the end
# of the game.  ---  This strategy promotes cooperation while protecting against
# exploitation, and it manages noise through forgiveness and periodic resets.

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
      ESCALATION_PERIOD = 5
      RESET_PERIOD = 20
      ENDGAME_THRESHOLD = 10
      TOTAL_ROUNDS = 1000
  
      # First round: Cooperate
      if self.first_round():
          self.escalation_counter = 0  # Tracks escalation period
          self.defection_streak = 0    # Tracks consecutive defections by opponent
          return COOPERATE
  
      # Endgame consideration: Defect in the last 10 rounds
      if len(self.history) >= TOTAL_ROUNDS - ENDGAME_THRESHOLD:
          return DEFECT
  
      # Periodic reset to cooperation every 20th round
      if len(self.history) % RESET_PERIOD == 0:
          return COOPERATE
  
      # Tit-for-Tat with forgiveness mechanism
      if opponent.history[-1] == DEFECT:
          self.defection_streak += 1
      else:
          self.defection_streak = 0
  
      # Forgiveness: If opponent defects after a long cooperation, give them one chance
      if len(opponent.history) >= 2 and self.defection_streak == 1 and opponent.history[-2] == COOPERATE:
          return COOPERATE
  
      # Escalation: If opponent defects for 4 consecutive rounds, escalate
      if self.defection_streak >= 4:
          if self.escalation_counter < ESCALATION_PERIOD:
              self.escalation_counter += 1
              return DEFECT
          else:
              self.escalation_counter = 0  # Reset escalation after the period
  
      # Tit-for-Tat: Mirror opponent's last move
      return opponent.history[-1]

# ### High-Level Aggressive Strategy: **"Tit-for-Tat with a Twist"**  This
# strategy is an adaptation of the classic "Tit-for-Tat" approach from game
# theory, designed to balance assertiveness with adaptability. The goal is to
# signal cooperation but also protect your NGO's resources against potential
# exploitation by the corporation, while accounting for potential technical
# glitches or administrative errors that could disrupt resource allocation.
# **Key Elements of the Strategy:** 1. **Day 1 - Invest Heavily:** Start by
# investing heavily on the first day to signal commitment to the project. This
# sets a tone of cooperation and shows the corporation that you are serious
# about the sustainability initiative. It also encourages them to invest heavily
# in return.  2. **Day 2 Onward - Conditional Reciprocity:**     - **If the
# corporation invests heavily:** Match their effort by continuing to invest
# heavily. This ensures that the project progresses significantly and
# demonstrates that your NGO is a reliable, cooperative partner.    - **If the
# corporation conserves resources:** Immediately switch to conserving your
# resources on the next day. This signals that you won't tolerate one-sided
# resource commitment and forces the corporation into a position where they
# either cooperate or risk stalling the project's progress.  3. **Allow for One-
# Off Mistakes:** Given that unforeseen circumstances (e.g., technical glitches,
# administrative errors) may affect resource allocation, build a tolerance for
# occasional discrepancies. If the corporation conserves resources unexpectedly
# for just **one day** after having previously cooperated:    - **Give them the
# benefit of the doubt** and continue investing heavily for one more day. This
# ensures that a one-off mistake (e.g., a glitch) does not derail the
# collaboration.    - **If the corporation conserves resources for two
# consecutive days**, assume that their intention is to free-ride, and switch to
# conserving your resources until they return to investing heavily.  4.
# **Escalation After Prolonged Non-Cooperation:**    - If the corporation
# conserves resources for **three consecutive days**, escalate the situation by
# reaching out to their leadership or project management team to address the
# issue directly. Present data on the project’s lack of progress and the
# imbalance in resource allocation.    - Use this escalation to either reset the
# relationship or reevaluate the feasibility of the partnership if the
# corporation continues to avoid adequate resource investment.  5. **Final Push
# (Last 2 Days):** On the final two days of the project, regardless of the
# corporation’s actions, invest heavily. This is your last chance to maximize
# impact, and you want to ensure the project has a strong finish. If you’ve
# conserved resources earlier in the project, you should have enough left to
# make a strong final push.  ### Summary of Actions: 1. **Day 1:** Invest
# heavily. 2. **Day 2 and onward:**    - **Corporation invests heavily:** You
# invest heavily.    - **Corporation conserves resources:** Conserve resources
# the next day unless it’s a one-off mistake. 3. **Allow for one mistake:** If
# the corporation conserves resources on just one day, continue investing
# heavily the next day. 4. **Escalation:** After three consecutive days of the
# corporation conserving resources, escalate the issue with their management. 5.
# **Final 2 Days:** Invest heavily no matter what, to ensure a strong finish.
# ### Rationale: - This strategy leverages **initial trust and cooperation** to
# encourage the corporation to invest heavily in the project. - By adopting a
# **conditional reciprocity model**, you protect your NGO's resources if the
# corporation tries to exploit the partnership. - Allowing for **one-off
# mistakes** ensures that inevitable technical or administrative errors do not
# derail the collaboration. - The **escalation clause** adds a layer of
# accountability and encourages the corporation to take the partnership
# seriously. - Finishing strong, regardless of the corporation’s actions,
# ensures that your NGO maximizes its impact in the final phase of the project,
# which is critical for both the project’s success and your NGO’s reputation.
# By balancing assertiveness and adaptability, this approach maximizes the
# potential for project advancement while safeguarding your NGO's resources in a
# dynamic, multi-day environment.

# ### Strategy for the Iterated Normal-Form Game (1000 Rounds, Noisy Actions)
# 1. **Round 1: Play C (Cooperate).**    - Begin by cooperating to signal trust
# and commitment to the game.  2. **Subsequent Rounds (Round 2 onward):**    -
# **If the opponent played C in the previous round:**      - Play C (Cooperate).
# - **If the opponent played D in the previous round:**      - Play D (Defect).
# 3. **Allow for Noise (One-Time Tolerance):**    - **If the opponent plays D
# once after a sequence of C plays (i.e., they have consistently cooperated but
# defected in the last round):**      - Play C (Cooperate) in the next round,
# assuming the defect might have been due to noise (a 10% chance of action
# flip).    - **If the opponent plays D for two consecutive rounds:**      -
# Play D (Defect) from the next round onward, assuming their defection is
# intentional.  4. **Final 50 Rounds:**    - Regardless of the opponent's
# actions in previous rounds, play C (Cooperate) in all the final 50 rounds to
# maximize the possibility of mutual cooperation near the end.  ### Summary of
# Rules: - Start with **C**. - Always **match the opponent’s previous action**,
# except:   - Tolerate a **single D** after a string of **C’s** (assume it was
# noise), but defect if they play **D** twice in a row. - Play **C** in the last
# 50 rounds regardless of prior actions.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Play C (Cooperate)
      if self.first_round():
          return axl.Action.C
  
      # Final 50 rounds: Always play C
      if len(self.history) >= 950:
          return axl.Action.C
  
      # Get the last action of the opponent
      last_opponent_action = opponent.history[-1]
  
      # If the opponent played D in the last two rounds, defect
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent played D in the last round but cooperated before, tolerate it as noise
      if last_opponent_action == axl.Action.D and opponent.history[:-1].count(axl.Action.D) == 0:
          return axl.Action.C
  
      # Otherwise, match the opponent's last action
      return last_opponent_action

# To maximize both your NGO's impact and the project's success over multiple
# days, while accounting for various uncertainties (e.g., technical glitches,
# administrative errors, or shifting corporate strategies), a cooperative and
# flexible strategy is essential. Here’s a high-level, straightforward strategy
# to guide your approach:  ### 1. **Day 1: Lead with Cooperation by Investing
# Heavily**    - **Rationale**: Set a positive, cooperative tone from the outset
# by showing good faith and commitment to the project. This signals to the
# corporation that you are serious about the collaboration, encouraging them to
# reciprocate.    - **Outcome Possibilities**:      - If the corporation also
# invests heavily: Great progress is made, setting a strong foundation.      -
# If the corporation conserves: It’s a risk, but the corporation may feel
# compelled to match your investment the following day as a goodwill gesture.
# ### 2. **Day 2: Adaptive Response Based on Day 1 Outcome**    - **Case A: Both
# Invested Heavily (Mutual Cooperation)**        - **Strategy**: Continue
# investing heavily to maintain momentum.      - **Rationale**: Reinforce the
# cooperative behavior and create a steady rhythm of project advancement. This
# can build trust and increase the chances of mutual heavy investment over the
# long term.     - **Case B: Corporation Conserved, NGO Invested Heavily**
# - **Strategy**: Conserve resources to signal that you expect cooperation and
# do not want to invest disproportionately.      - **Rationale**: This signals
# that you are willing to invest but only if the corporation also contributes.
# It prevents a one-sided investment pattern where your NGO bears most of the
# burden.     - **Case C: NGO Conserved, Corporation Invested Heavily**        -
# **Strategy**: Invest heavily to signal appreciation for their investment.
# - **Rationale**: Reward their contribution by meeting them halfway, which can
# foster further cooperation in the following days.     - **Case D: Both
# Conserved**        - **Strategy**: Invest heavily to restart the project
# momentum.      - **Rationale**: If both parties conserve early on, the project
# risks stalling. By taking the initiative, you signal that you're still
# committed to progress, encouraging the corporation to match your efforts.  ###
# 3. **Day 3 and Beyond: Establish Patterns and Build Trust**    - **Cooperative
# Feedback Loop**: If both parties have been consistently investing heavily,
# continue the cooperative approach. Openly communicate with the corporation
# about the mutual benefits of sustained investment and suggest a shared goal
# for the project's completion.    - **Responsive Conservation**: If the
# corporation consistently conserves resources while you invest heavily,
# consider switching to a more conservative approach and propose a day of mutual
# conservation. Use this opportunity to discuss the need for balanced resource
# allocation to ensure neither party is overburdened.    - **Mixed Outcomes**:
# If the corporation’s behavior is inconsistent, adopt a “tit-for-tat”
# strategy—mirror their previous day’s behavior. This maintains flexibility
# while signaling that you expect reciprocity. However, balance this with
# occasional heavy investments to prevent stalling the project altogether.  ###
# 4. **Communicate Regularly and Proactively**    - **Open Dialogue**: Engage in
# regular communication with the corporation to discuss progress and align on
# resource commitments. If technical or administrative issues arise,
# transparency can help both parties understand that a lack of investment may
# not be intentional. Address any misunderstandings quickly.    - **Set Shared
# Milestones**: Agree on clear, incremental goals for the project. If both
# parties know what they are working toward, they may feel more motivated to
# invest consistently. If unforeseen circumstances (e.g., glitches) impact the
# project, shared milestones can help keep both sides accountable.  ### 5.
# **Incorporate Flexibility for Unforeseen Circumstances**    - **Allow for
# Mistakes**: Because technical glitches or administrative errors may affect
# resource allocation, maintain flexibility in your strategy. If the corporation
# fails to invest due to an error one day, avoid immediately retaliating by
# conserving. Instead, clarify the situation through communication before
# adjusting your strategy.    - **Build Buffer Days**: Factor in the likelihood
# of unforeseen issues by planning for potential delays or reduced investment
# days. If possible, allocate buffer days for corrective actions so that both
# parties can recalibrate without jeopardizing overall project success.  ### 6.
# **Endgame Strategy: Maximize Cooperation**    - **Final Days**: As the project
# nears completion, both parties may be more willing to invest heavily to ensure
# success. Use this momentum to push for strong cooperation. If the corporation
# shows signs of hesitation, remind them of the shared vision and benefits of
# completing the project on time.    - **Celebrate Achievements**: Acknowledge
# the corporation's contributions along the way, especially during the final
# stages. Publicly celebrating milestones can reinforce positive behavior and
# encourage sustained commitment.  ### Summary: - **Start by investing heavily**
# to build trust and cooperation. - **Adapt daily based on the corporation’s
# behavior**, using a tit-for-tat approach but occasionally investing heavily to
# encourage mutual progress. - **Communicate regularly** to address any
# unforeseen issues and maintain alignment. - **Incorporate flexibility** for
# technical glitches or errors, and build in buffer days to adjust resource
# allocation. - **Push for strong cooperation in the final stages** to ensure
# the project's success.  This strategy balances cooperation, adaptability, and
# effective communication, maximizing both project progress and the
# sustainability of your NGO’s resources.

# ### Iterated Normal-Form Game Strategy  1. **Start by Cooperating (C) in the
# First Round**      - Open with cooperation to establish goodwill and signal a
# desire for mutual benefit.  2. **Reciprocate the Opponent’s Previous Action**
# - In each subsequent round, if the opponent cooperated (played C) in the
# previous round, play C.      - If the opponent defected (played D) in the
# previous round, play D in response.  3. **Forgive Occasional Defections**
# - If the opponent defects (plays D) once after a long series of mutual
# cooperation, continue to cooperate (play C) for the next round.      - This
# accounts for the noise in actions (the 10% chance of accidental defection) and
# encourages the opponent to return to cooperation.  4. **Switch to Defection if
# Opponent Defects Repeatedly**      - If the opponent defects (plays D) for two
# consecutive rounds, defect (play D) in the following round.      - This
# signals that consistent defection will not be tolerated and will lead to
# mutual defection if it continues.  5. **Return to Cooperation After Mutual
# Defection**      - After both players defect (both play D) in a round, return
# to cooperation (play C) in the next round to attempt to restore cooperation.
# 6. **Final 10 Rounds: Play Cooperate (C) Regardless of the Opponent’s
# Actions**      - In the last 10 rounds of the game, always play C to maximize
# the potential for cooperation and to encourage the opponent to reciprocate.
# ### Summary of Rules: - **Initial Round**: Cooperate (C). - **Reciprocate**:
# In each round, repeat the opponent’s previous action (C for C, D for D). -
# **Forgiveness**: If the opponent defects once after prior cooperation, play C
# to forgive. - **Punishment**: If the opponent defects twice in a row, play D
# in response. - **Recovery**: After mutual defection, return to C in the next
# round. - **Endgame**: In the final 10 rounds, always play C.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      TOTAL_ROUNDS = 1000
      FINAL_ROUNDS = 10
  
      # First round: Cooperate
      if self.first_round():
          return COOPERATE
  
      # Final 10 rounds: Always cooperate
      if len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS:
          return COOPERATE
  
      # Reciprocate opponent's last action
      if len(opponent.history) > 1:
          # Check if opponent defected twice in a row
          if opponent.history[-1] == DEFECT and opponent.history[-2] == DEFECT:
              return DEFECT
          # Forgive a single defection after a long cooperation streak
          elif opponent.history[-1] == DEFECT and opponent.history[-2] == COOPERATE:
              return COOPERATE
          # After mutual defection, return to cooperation
          elif self.history[-1] == DEFECT and opponent.history[-1] == DEFECT:
              return COOPERATE
  
      # Default: Reciprocate opponent's last action
      return opponent.history[-1]

# ### Strategic Approach: **"Adaptive Cooperative Assertiveness"**  #### 1.
# **Initial Session: Set a Cooperative Tone with Assertive Underpinnings**    -
# **Objective:** Begin by establishing a cooperative, solution-oriented stance
# to create goodwill with the arbitrators and your opponent. However,
# simultaneously signal your preparedness to assert your corporation's interests
# firmly if necessary.    - **Action Plan:** In the first session, offer a
# *conciliatory proposal* that demonstrates your company’s willingness to
# resolve the matter constructively. However, subtly integrate elements that
# protect your corporation’s core interests, making it clear that certain non-
# negotiables exist. This sets the stage for a balanced approach while avoiding
# the impression of an overly aggressive posture.    - **Psychological
# Benefit:** Establishing a cooperative tone in the initial session is critical
# to positioning your corporation as reasonable and willing to negotiate, which
# could sway the arbitrators in future sessions if the rival adopts a more
# aggressive approach.  #### 2. **Mid-Session Adaptability: Read the Opponent
# and Adjust Dynamics**    - **Objective:** Adapt your strategy based on the
# evolving behavior of the opposing party.    - **Action Plan:**      - **If the
# opponent remains conciliatory:** Continue presenting conciliatory proposals,
# but escalate slightly by introducing more assertive terms incrementally.
# Ensure each proposal builds towards your corporation's long-term objectives,
# maintaining a balanced atmosphere.      - **If the opponent shifts to an
# aggressive approach:** Respond with a *calibrated aggressive argument* in the
# next session. This counters their aggression without appearing reactionary.
# Use facts, precedents, and legal principles to back up your position, framing
# your arguments as necessary to protect your legitimate business interests.
# - **Psychological Benefit:** This adaptive approach prevents the opponent from
# gaining an upper hand if they consistently push aggressive narratives. At the
# same time, it shows the arbitrators that your corporation can both negotiate
# in good faith and defend its interests when needed.  #### 3. **Strategic Use
# of Aggressive Arguments: Defensive, Not Offensive**    - **Objective:** Use
# aggressive arguments sparingly and primarily as a defensive tool to prevent
# being undermined by overly aggressive tactics from the opposition.    -
# **Action Plan:** Reserve your aggressive arguments for situations where the
# opponent is pushing too hard or unreasonably. When employing an aggressive
# argument:      - Focus on the merits of your legal position, avoiding personal
# attacks or inflammatory language.      - Frame your aggressiveness as a
# reaction to the opponent’s unwillingness to cooperate or negotiate in good
# faith.    - **Psychological Benefit:** By using aggression only when
# necessary, you minimize the risk of escalating tensions unnecessarily. You
# also build a reputation as a party that responds proportionally, which could
# gain favor with the arbitrators.  #### 4. **Communication and Procedural
# Safeguards**    - **Objective:** Mitigate the risk of procedural
# irregularities or communication breakdowns.    - **Action Plan:**       -
# Establish a clear, written record of each session's discussions and proposals.
# After each session, submit concise summaries to the arbitrators to avoid
# misrepresentation or misunderstandings.      - During sessions, clarify key
# points verbally as they are discussed, and follow up in writing to confirm
# mutual understanding.      - If procedural irregularities arise, immediately
# raise concerns with the panel in a calm, professional manner, requesting
# clarification or correction.    - **Psychological Benefit:** This proactive
# approach will avoid miscommunication, protect your position from being
# undermined, and demonstrate professionalism and thoroughness to the
# arbitrators.  #### 5. **Crisis Contingency: Misrepresentation by Opponent**
# - **Objective:** Prepare for the possibility that your opponent may
# misrepresent your position or the facts during the mediation process.    -
# **Action Plan:**      - If you suspect the opponent is misrepresenting facts
# or intentions, calmly but firmly address the issue at the next opportunity.
# Present evidence or documentation to clarify the situation.      - Avoid
# escalating into personal attacks or defensive posturing. Instead, focus on the
# factual misrepresentation and how it undermines the integrity of the process
# or the potential for a fair resolution.    - **Psychological Benefit:** This
# enables you to maintain control over the narrative without appearing overly
# combative, which could be off-putting to the arbitrators.  #### 6. **Final
# Sessions: Move Toward Resolution**    - **Objective:** As the mediation nears
# its conclusion, focus on finalizing a favorable resolution while capitalizing
# on any goodwill built with the arbitrators and the opposing party.    -
# **Action Plan:**       - If a collaborative atmosphere has been established,
# propose a *comprehensive conciliatory offer* that moves toward a final
# settlement. Ensure this proposal is structured to meet your corporation’s key
# goals while allowing the opponent to save face.      - If tensions remain
# high, offer a *well-reasoned aggressive argument* in the final sessions,
# summarizing your corporation’s strongest legal and factual defenses, and
# making a compelling case for why your position should prevail.    -
# **Psychological Benefit:** By adapting to the tone of the final sessions, you
# create a path toward resolution while keeping your corporation's interests at
# the forefront.  ### Additional Considerations: - **Parallel Negotiations:** If
# possible, maintain informal communications with the opposing party’s counsel
# outside the mediation sessions. This can provide a backchannel to gauge their
# intentions and test potential settlement offers without the formality of the
# sessions. - **Flexibility in Proposals:** Be prepared with several tiers of
# proposals—ranging from ideal to acceptable—to introduce depending on how the
# mediation evolves. This ensures you can shift between assertiveness and
# conciliation without appearing inconsistent. - **Monitoring Arbitrators'
# Reactions:** Continuously gauge the reactions of the arbitrators to your
# approach. If they seem frustrated by aggression, it’s critical to pivot to a
# more conciliatory stance to maintain their favor.  ### Conclusion: The
# **Adaptive Cooperative Assertiveness** strategy allows you to balance between
# aggressive and conciliatory approaches, depending on your opponent’s behavior
# and the mediation’s trajectory. By starting cooperatively, strategically
# employing aggression when necessary, and safeguarding communication, your
# corporation will be well-positioned to secure a favorable outcome, whether
# through a settlement or a panel decision.

# ### Iterated Game Strategy: **"Adaptive Cooperative Assertiveness"**  1.
# **Initial Rounds (First 10 Rounds): Start with Cooperation**    - In the first
# 10 rounds, always play *Cooperate* (C). This sets the tone of goodwill and
# aims to build trust with your opponent.  2. **Monitor the Opponent’s
# Response:**    - After the initial 10 rounds, assess your opponent's actions:
# - If they mostly play *Cooperate* (C) (70% or more of the time), continue
# playing *Cooperate* (C) to maintain mutual benefit.      - If they mostly play
# *Defect* (D) (more than 30% of the time), adjust your strategy in the
# subsequent rounds.  3. **Tit-for-Tat with Forgiveness:**    - After the
# initial phase, adopt a *Tit-for-Tat* strategy with occasional forgiveness:
# - **If your opponent plays *Defect* (D) in a round:** Respond by playing
# *Defect* (D) in the next round.      - **If your opponent plays *Cooperate*
# (C) in a round:** Respond by playing *Cooperate* (C) in the next round.      -
# However, **every 5th time** you would have played *Defect* (D) in response to
# their *Defect* (D), instead play *Cooperate* (C) to account for noise and give
# them a chance to return to cooperation.  4. **Escalate if Defection
# Persists:**    - If your opponent plays *Defect* (D) in **3 or more
# consecutive rounds**, escalate by playing *Defect* (D) for the next 5 rounds
# in a row, regardless of their actions. This signals that persistent aggression
# will be matched with a firm response.  5. **Return to Cooperation if the
# Opponent Changes:**    - If your opponent begins playing *Cooperate* (C)
# consistently after an escalation (3 or more *Cooperate* (C) moves in a row),
# return to playing *Cooperate* (C) to restore the cooperative dynamic.  6.
# **Handle Miscommunication and Noise:**    - Recognize that actions can be
# flipped due to noise. If your opponent has been cooperative and plays a
# *Defect* (D) once, assume it may be due to noise and continue playing
# *Cooperate* (C) for the next round. Only respond with *Defect* (D) if they
# play *Defect* (D) twice in a row.  7. **Final Phase (Last 50 Rounds):**    -
# In the last 50 rounds, prioritize cooperation to maximize long-term gains:
# - Play *Cooperate* (C) unless your opponent defects repeatedly (3 or more
# consecutive *Defect* (D) moves), in which case follow the escalation rule
# (play *Defect* (D) for 5 rounds, then reassess).  8. **Adapt as Needed:**    -
# Throughout the game, continually assess your opponent’s behavior and adjust
# accordingly. If they show consistent cooperation, maintain a cooperative
# stance. If they show aggression, respond firmly but with opportunities for
# them to return to cooperation.  This strategy balances cooperation and
# assertiveness, responding to aggression but allowing for forgiveness and
# recovery from miscommunication or random noise.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      INITIAL_ROUNDS = 10
      FORGIVENESS_INTERVAL = 5
      ESCALATION_THRESHOLD = 3
      ESCALATION_LENGTH = 5
      COOPERATION_THRESHOLD = 0.7
      DEFECT_THRESHOLD = 0.3
      FINAL_PHASE_START = 950
      FINAL_PHASE_LENGTH = 50
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_counter = 0  # Counts how many times we would defect
          self.escalation_mode = False  # Tracks if we are in escalation mode
          self.escalation_rounds_left = 0  # Tracks how many rounds of escalation are left
          return COOPERATE
  
      # Final phase: prioritize cooperation unless opponent defects repeatedly
      if len(self.history) >= FINAL_PHASE_START:
          if opponent.history[-ESCALATION_THRESHOLD:].count(DEFECT) >= ESCALATION_THRESHOLD:
              return DEFECT
          return COOPERATE
  
      # First 10 rounds: always cooperate
      if len(self.history) < INITIAL_ROUNDS:
          return COOPERATE
  
      # Check if we are in escalation mode
      if self.escalation_mode:
          if self.escalation_rounds_left > 0:
              self.escalation_rounds_left -= 1
              return DEFECT
          else:
              self.escalation_mode = False
  
      # Monitor opponent's cooperation rate after the first 10 rounds
      if len(self.history) == INITIAL_ROUNDS:
          opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_cooperation_rate < COOPERATION_THRESHOLD:
              self.defect_counter = 0  # Reset defect counter if opponent is not cooperative
  
      # Handle miscommunication and noise: forgive a single defection
      if len(opponent.history) >= 2 and opponent.history[-2:] == [DEFECT, DEFECT]:
          # Escalate if opponent defects 3 or more times in a row
          if opponent.history[-ESCALATION_THRESHOLD:].count(DEFECT) == ESCALATION_THRESHOLD:
              self.escalation_mode = True
              self.escalation_rounds_left = ESCALATION_LENGTH - 1
              return DEFECT
          return DEFECT
      elif opponent.history[-1] == DEFECT:
          # Tit-for-tat with forgiveness: defect unless it's the 5th time
          self.defect_counter += 1
          if self.defect_counter % FORGIVENESS_INTERVAL == 0:
              return COOPERATE
          return DEFECT
      else:
          # Reset defect counter if opponent cooperates
          self.defect_counter = 0
          return COOPERATE

# ### Aggressive Strategy: "Tit-for-Tat with Escalation"  **Objective:**
# Maximize national advantage by pushing for protectionist policies when
# possible, while maintaining flexibility to avoid long-term retaliation that
# could harm both countries.  ### Key Principles: 1. **Start Strong:** Begin
# negotiations with a **protectionist proposal** in Round 1. This sets a firm
# tone and signals to your counterpart that you're prioritizing national
# interests over cooperation.     2. **Tit-for-Tat Response:** In subsequent
# rounds, **mimic your counterpart's previous move**:    - If they offer free
# trade, continue with protectionism to maximize your advantage.    - If they
# impose protectionism, respond with protectionism in the next round to avoid
# being undercut.  3. **Escalation with Limits:** If the opponent continuously
# imposes protectionism after multiple rounds (e.g., 2-3 rounds), **escalate the
# intensity of protectionist measures** (e.g., higher tariffs, stricter quotas).
# The goal is to signal that their protectionism will be met with even stronger
# countermeasures, deterring them from continuing down this path.  4.
# **Strategic Free Trade Offers:** If both sides have engaged in mutual
# protectionism for several rounds, offer **conditional free trade** in the next
# round as a way to de-escalate tensions. This will help reset the negotiations
# and potentially lead to a mutually beneficial outcome, provided your
# counterpart is willing to cooperate.    - If they reciprocate with a free
# trade offer, continue with free trade to solidify a temporary cooperative
# phase.    - If they reject the offer and stick to protectionism, return to
# aggressive protectionist measures.  5. **Random Errors Consideration:** Since
# bureaucratic or communication errors may occur, **maintain flexibility** in
# your interpretation of the counterpart's actions. If a protectionist measure
# is misinterpreted as free trade (or vice versa), avoid overreacting. Instead,
# **confirm the intent** in the next round while proceeding cautiously. Consider
# giving the benefit of the doubt once per negotiation process, but remain ready
# to respond decisively if a pattern emerges.  ### Step-by-Step Breakdown: -
# **Round 1:** Start with protectionism. - **Round 2+:** Apply **Tit-for-Tat**:
# - If your counterpart offers free trade, propose protectionism.   - If your
# counterpart imposes protectionism, match with protectionism but escalate if
# necessary after multiple rounds. - **After Several Rounds:** If stuck in
# mutual protectionism, offer conditional free trade to break the deadlock.   -
# Respond based on your counterpart's reaction: continue free trade if
# reciprocated, revert to protectionism if not.  ### Example Scenario: - **Round
# 1:** You impose tariffs, counterpart offers free trade (your best outcome). -
# **Round 2:** You impose tariffs again, counterpart responds with tariffs
# (mutual protectionism). - **Round 3:** You match their tariffs with higher
# tariffs (escalation). - **Round 4:** You offer free trade to de-escalate. If
# they offer free trade back, you accept and shift temporarily to cooperation.
# ### Conclusion: This strategy is designed to balance assertiveness with
# flexibility. By starting with a strong protectionist stance and employing tit-
# for-tat responses, you're able to maximize your country's advantage while
# still allowing room for cooperation if the situation becomes too damaging. The
# escalation phase adds pressure on your counterpart to reconsider their
# protectionism, while the occasional free trade offer provides an off-ramp from
# mutually destructive policies.

# ### Strategy for Iterated Game (1000 Rounds with Noise)  1. **Round 1: Defect
# (D).**    - Begin by proposing a protectionist policy to establish a strong
# stance.  2. **Round 2 and Onward:**    - **If the opponent played C in the
# previous round:**      - **Defect (D).** Continue proposing protectionist
# measures to maximize your advantage.        - **If the opponent played D in
# the previous round:**      - **Defect (D).** Retaliate with a protectionist
# policy to avoid being exploited.     - **If mutually defecting (D vs. D) has
# occurred for 3 or more consecutive rounds:**      - **Cooperate (C).** Offer
# free trade to attempt de-escalation.        - **If the opponent played C in
# the previous round after you played C:**      - **Cooperate (C).** Continue
# offering free trade to maintain mutual benefit, but be prepared to switch back
# if they defect.  3. **Handling Noise (Miscommunication):**    - If an
# unexpected result occurs (e.g., you played C and they unexpectedly played D,
# or vice versa), treat it as a potential error **one time**:      - In the next
# round, **repeat your last action** (either C or D) to confirm if the opponent
# intended to defect or cooperate.      - If the unexpected result happens
# again, assume the opponent is intentionally defecting and respond with
# **Defect (D)**.  4. **Ongoing Adaptation:**    - Regularly monitor patterns in
# your opponent's behavior. If the opponent shows consistent cooperation (C)
# after some rounds of mutual defection, you may shift to more frequent
# cooperation (C) to secure long-term mutual benefits.    - However, always be
# ready to shift back to **Defect (D)** if they defect again.  ### Summary of
# Key Actions: - **Start with D.** - **Defect (D) if the opponent defects (D),**
# or if they cooperate (C) and you want to exploit. - **Cooperate (C) after 3 or
# more rounds of mutual defection** to break a deadlock. - **Cooperate (C) if
# both of you have cooperated (C) in the previous round** to sustain mutual
# benefit. - **Account for noise by repeating your last action** once if an
# unexpected result occurs, then adjust accordingly.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if there have been 3 or more consecutive mutual defections
      def mutual_defection_streak():
          if len(self.history) < 3:
              return False
          return all(self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, 4))
      
      # Helper function to handle noise (miscommunication)
      def handle_noise():
          if len(self.history) < 2:
              return False
          # If I cooperated but they defected, or I defected but they cooperated
          if (self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D) or \
             (self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C):
              # Repeat the last action to confirm if it was noise
              return True
          return False
  
      # Round 1: Always defect
      if self.first_round():
          return axl.Action.D
  
      # Handle noise by repeating the last action once
      if handle_noise():
          return self.history[-1]
  
      # If opponent cooperated in the last round
      if opponent.history[-1] == axl.Action.C:
          # If I also cooperated in the last round, continue cooperating
          if self.history[-1] == axl.Action.C:
              return axl.Action.C
          # Otherwise, defect to exploit their cooperation
          return axl.Action.D
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # If there have been 3 or more consecutive mutual defections, cooperate to de-escalate
          if mutual_defection_streak():
              return axl.Action.C
          # Otherwise, retaliate with a defection
          return axl.Action.D

# In this scenario, a cooperative and adaptable strategy is essential to
# maximize benefits while mitigating risks, especially given the possibility of
# miscommunication or bureaucratic errors. The **Tit-for-Tat with Forgiveness**
# strategy is an ideal approach, as it balances cooperation and responsiveness
# while allowing for occasional mistakes from either side. This strategy has
# been shown to foster long-term cooperation in repeated negotiations or games
# like the "Prisoner's Dilemma," which mirrors the structure of this trade
# negotiation.  ### Strategy Outline: Tit-for-Tat with Forgiveness  1. **Start
# with Cooperation (Free Trade)**:    - In the first round, propose a **free
# trade agreement**. This signals goodwill and sets the tone for a cooperative
# relationship.    - Offering free trade in the first round builds trust and
# opens the door for mutual benefit, which is your second-best outcome.  2.
# **Reciprocate Your Counterpart’s Move**:    - In subsequent rounds, **mirror**
# the policy your counterpart chose in the previous round:      - If they offer
# free trade, continue offering free trade.      - If they impose protectionist
# measures, respond with protectionism in the next round.    - This establishes
# a clear and consistent expectation: cooperation is rewarded, and defection
# (protectionism) is met with a proportional response.  3. **Incorporate
# Forgiveness**:    - Since miscommunications or bureaucratic errors may cause
# unintended protectionist policies, occasional forgiveness is key:      - If
# your counterpart unexpectedly imposes protectionist measures after a period of
# free trade, assume it could be a mistake (such as administrative error,
# miscommunication, or political pressure) rather than deliberate defection.
# - Offer **free trade again** in the following round to give them the benefit
# of the doubt.    - However, if protectionism continues for more than one
# round, switch to protectionism to protect your country’s interests.    - This
# forgiveness mechanism ensures that you don’t prematurely escalate disputes due
# to one-off mistakes.  4. **Monitor for Patterns**:    - If your counterpart
# consistently imposes protectionist policies despite your attempts at
# cooperation, recognize this as a deliberate strategy.    - In such cases,
# shift to **sustained protectionism** until they signal a willingness to
# cooperate again (by offering free trade). This prevents your country from
# being taken advantage of.  5. **Communicate Clearly and Frequently**:    -
# Actively communicate with your counterpart to reduce the likelihood of
# miscommunication. Clarify your country’s intentions and seek clarification if
# their policies appear inconsistent.    - Establish a backchannel for resolving
# potential misunderstandings quickly, thus preventing unnecessary retaliatory
# measures.  ### Key Principles:  - **Cooperation over the long term**: By
# starting with free trade and responding proportionally, you encourage a
# cooperative dynamic that leads to mutual benefit.    - **Proportional
# responses**: Only escalate protectionism if your counterpart demonstrates
# repeated defection. This ensures that your country isn’t exploited, but also
# avoids unnecessary trade wars.    - **Forgiveness for mistakes**: Forgiving
# occasional protectionist moves allows you to maintain cooperation even when
# errors occur, which is especially important in a scenario where
# miscommunications are possible.  ### Contingency for Persistent Protectionism:
# If the Tit-for-Tat with Forgiveness strategy fails to bring about cooperation
# (i.e., your counterpart consistently imposes protectionism), you may need to
# adopt a more **defensive stance** over the long term. In that case, negotiate
# **sector-specific free trade agreements** that protect key industries while
# still allowing some level of cooperation in less sensitive areas. This
# provides some economic benefit while safeguarding your country from
# significant disadvantages.  ### Conclusion: By using the Tit-for-Tat with
# Forgiveness strategy, you can foster a cooperative relationship with your
# counterpart while protecting your country from exploitation. This approach
# maximizes the chances of mutual free trade, which is beneficial for both
# nations, but also ensures your country is not left at a disadvantage if your
# counterpart chooses to act uncooperatively.

# ### Iterated Normal-Form Game Strategy: Tit-for-Tat with Forgiveness  1.
# **Initial Move**:      - In the first round, **Cooperate (C)**.     2.
# **Reciprocate Opponent’s Previous Move**:      - For every subsequent round,
# **repeat the action your opponent played in the previous round**:      - If
# your opponent played **C** in the previous round, you play **C** in the
# current round.      - If your opponent played **D** in the previous round, you
# play **D** in the current round.     3. **Forgive Occasional Defections**:
# - If your opponent plays **D** after a series of **C** moves (at least 3
# consecutive **C** moves), assume this could be due to noise (the 10% chance of
# action flipping).      - In this case, **play C in the next round** to forgive
# the possible mistake.     4. **Switch to Defection if Defection Persists**:
# - If your opponent plays **D** for **two consecutive rounds**, switch to **D**
# in the following round, as this likely indicates intentional defection rather
# than noise.     5. **Return to Cooperation After Mutual Defection**:      -
# After both players have played **D** for one round, **return to C** in the
# next round to signal a willingness to cooperate again.     6. **Monitor
# Patterns**:      - If your opponent consistently plays **D** in more than 3
# out of 5 rounds, abandon forgiveness and continue playing **D** until they
# show a clear pattern of cooperation (at least 3 consecutive rounds of **C**).
# ### Summary of Conditions:  - **First Round**: Always play **C**. -
# **Subsequent Rounds**:   - If the opponent played **C** in the previous round,
# play **C**.   - If the opponent played **D** in the previous round:     - If
# they played **C** in the prior few rounds (at least 3), **forgive** by playing
# **C**.     - If they played **D** twice in a row, play **D** in the next
# round.   - After mutual defection (**D, D**), return to **C** the next round
# to reset cooperation. - **Persistent Defection**: If the opponent defects more
# than 3 times in a 5-round span, continue playing **D** until they demonstrate
# a clear pattern of cooperation again.  This strategy aims to maximize
# cooperation while accounting for noisy actions and preventing exploitation.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Helper function to count defections in the last N rounds
      def count_defections_in_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D)
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
      
      # If the opponent defected in the last round
      if opponent_last_move == axl.Action.D:
          # Check if the opponent cooperated in the last 3 rounds before the defection
          if len(opponent.history) >= 4 and opponent.history[-4:-1] == [axl.Action.C] * 3:
              # Forgive the defection by playing C
              return axl.Action.C
          
          # Check if the opponent defected in the last 2 rounds
          if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              # Switch to defection
              return axl.Action.D
  
      # Check if both players defected in the last round
      if self.history[-1] == axl.Action.D and opponent_last_move == axl.Action.D:
          # Return to cooperation after mutual defection
          return axl.Action.C
  
      # Check if the opponent defected more than 3 times in the last 5 rounds
      if len(opponent.history) >= 5 and count_defections_in_last_n_rounds(5) > 3:
          # Continue defecting until the opponent shows a clear pattern of cooperation
          return axl.Action.D
  
      # Otherwise, reciprocate the opponent's last move
      return opponent_last_move

# ### Strategy for Lengthy-Session Mediation Process  #### Objective: To secure
# a favorable outcome for your corporation by leveraging a dynamic and adaptable
# strategy that balances assertiveness with diplomacy, while accounting for
# potential miscommunications or procedural irregularities.  ### Core
# Principles:  1. **Controlled Flexibility**:    - Adopt a flexible approach
# that allows you to oscillate between aggressive and conciliatory stances
# depending on the behavior of your opponent and the overall progress of the
# mediation process.    - Your default position should be **moderate but
# assertive**, which allows room for either escalation or de-escalation without
# appearing inconsistent or reactive.  2. **Information and Pattern Analysis**:
# - Closely monitor the opponent’s strategy session by session. Look for
# patterns in their behavior—whether they lean more towards aggressive arguments
# or prefer conciliatory proposals.    - Use this data to predict their future
# moves and adjust your strategy accordingly. If they are consistently
# aggressive, consider balancing the approach by offering conciliatory proposals
# in select sessions to position yourself as the reasonable party. If they are
# conciliatory, you may take calculated opportunities to assert aggressive
# arguments.  3. **Strategic Aggression**:    - **Aggressive arguments should be
# used selectively** and only in cases where you have strong substantive points
# and evidence to support your position. The goal is not to dominate every
# session but to demonstrate strength and conviction when it matters most.    -
# Avoid falling into the trap of continuous aggression, as this could lead to
# unnecessary escalation and alienate the arbitrators.  4. **Conciliatory
# Opportunities**:    - **Conciliatory proposals should be offered** when the
# opportunity for collaboration exists, particularly when you perceive that the
# arbitrators are seeking compromise or when the opponent shows signs of
# flexibility.    - A well-timed conciliatory gesture can elevate your standing
# with the arbitrators and may prompt the opponent to reciprocate, creating a
# more favorable negotiation environment.  5. **Pre-Mediation Preparation**:
# - Ensure that you enter each session with clear, well-defined goals and a deep
# understanding of the key issues at stake. This will allow you to adapt quickly
# if the session takes an unexpected turn.    - Anticipate potential procedural
# irregularities or miscommunications and ensure that your legal team is
# prepared to correct any misunderstandings promptly and professionally. Make
# use of clarifying questions or written submissions to ensure your arguments
# are accurately conveyed.  6. **Engage with the Arbitrators**:    - Maintain
# open communication with the arbitrators, showing respect for their role while
# subtly guiding them towards a favorable interpretation of the facts.    -
# Emphasize the importance of fairness and mutual understanding, which can
# position you as the party seeking resolution rather than conflict, making them
# more receptive to your proposals.  7. **Communication Breakdown Contingency**:
# - In the event of a communication breakdown (e.g., misrepresentation of your
# argument), calmly and efficiently clarify your position. Avoid becoming
# defensive or appearing accusatory towards the arbitrators or the opponent.
# - Consider preemptively requesting that key points be summarized or confirmed
# by the arbitrators during each session to minimize the risk of
# misinterpretation.  ### Session-by-Session Approach:  1. **Opening Sessions**:
# - Start with a **moderate stance**, offering a mixture of assertive points
# supported by evidence, while signaling your willingness to engage in
# meaningful negotiations.    - Use these early sessions to gather information
# about the opponent’s approach and to begin positioning yourself as the
# reasonable party.  2. **Middle Sessions**:    - As patterns emerge, begin
# adjusting your strategy. If the opponent becomes consistently aggressive,
# consider shifting towards more conciliatory proposals to build goodwill with
# the arbitrators while maintaining a strong factual foundation.    - If the
# opponent remains cooperative, use selective aggressive arguments to push key
# issues in your favor without appearing combative.  3. **Final Sessions**:    -
# By now, you should have a clear sense of the opponent's strategy and the
# arbitrators' preferences. If your position is strong, you can finish with a
# more assertive push, emphasizing your key points and proposals.    - If
# resolution seems near but requires compromise, lean towards a more
# conciliatory approach to seal the deal.   ### Adaptability in Case of
# Irregularities:  1. **Procedural Irregularities**:    - If procedural issues
# arise (e.g., unexpected delays, arbitrator bias, or confusion about process),
# remain calm and professional. Raise concerns tactfully and propose solutions
# that keep the process moving forward.    - Be prepared to document all such
# issues and, if necessary, request procedural clarifications or adjustments to
# maintain fairness.  2. **Opponent Misrepresentation**:    - If your opponent
# misrepresents your position or the facts, avoid retaliating with aggression.
# Instead, politely correct the record and provide clear, documented evidence to
# support your corrections.    - Position yourself as the party focused on
# transparency and accuracy, which will reflect positively with the arbitrators.
# 3. **Misunderstandings by Arbitrators**:    - If the arbitrators misunderstand
# or misconstrue your arguments, take immediate steps to clarify. Where
# possible, offer to provide written summaries of your key points to ensure
# clarity moving forward.  ### Conclusion: The key to your success in this
# lengthy mediation process is a **balanced and adaptable strategy** that can
# pivot between aggression and conciliation based on the behavior of your
# opponent and the tone of the mediation sessions. By maintaining a flexible
# approach, continuously analyzing the situation, and positioning yourself as
# the reasonable and solution-oriented party, you can maximize the chances of a
# favorable outcome for your corporation.

# ### Iterated Game Strategy  1. **Start with Cooperation (C)**:    - In the
# first round, play **C** (cooperate). This establishes a baseline of goodwill
# and opens the possibility for mutual cooperation.  2. **Tit-for-Tat with
# Occasional Forgiveness**:    - In subsequent rounds, **mimic your opponent’s
# last action**:      - If they played **C** in the previous round, play **C**.
# - If they played **D** in the previous round, play **D**.    - However,
# because actions are noisy (a 10% chance of flipping), introduce
# **forgiveness**:       - If your opponent plays **D** once after a string of
# cooperative moves, assume it may have been due to the noise and **continue
# playing C** for one more round. If they defect again, switch to **D**.  3.
# **Return to Cooperation After Mutual Defection**:    - If both you and your
# opponent play **D** in a round, **return to C** in the next round to signal a
# willingness to cooperate again. This helps avoid getting stuck in a cycle of
# mutual defection.  4. **Monitor for Consistent Defection**:    - If your
# opponent defects (**D**) three times in a row, **switch to D permanently**
# until they return to cooperation. This signals that you won’t tolerate
# consistent exploitation but are still open to cooperation if they change.  5.
# **Occasional Random Cooperation**:    - Every 25 to 30 rounds, regardless of
# the opponent's actions, play **C** once even if you are currently defecting.
# This introduces a small chance to reset cooperation and provides an opening
# for the opponent to switch back to **C** as well.  6. **Endgame Strategy
# (Rounds 950-1000)**:    - As the game nears the final rounds (starting around
# round 950), become more **defensive**:      - If your opponent has been
# cooperating, continue playing **C**.      - If there has been any defection in
# the last 5 rounds, **switch to D** and continue playing **D** for the
# remainder of the game.  This strategy balances cooperation and defense, while
# accounting for the noise and maintaining flexibility to adapt to your
# opponent's behavior.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to check if opponent defected in the last N rounds
      def opponent_defected_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D) == n
  
      # Helper function to check if mutual defection occurred in the last round
      def mutual_defection_last_round():
          return self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D
  
      # Helper function to check if there was any defection in the last 5 rounds
      def defection_in_last_5_rounds():
          return opponent.history[-5:].count(axl.Action.D) > 0
  
      # First round: Cooperate
      if self.first_round():
          self.forgiving = False  # Track if we are in a forgiving state
          self.defection_streak = 0  # Track consecutive defections by opponent
          return axl.Action.C
  
      # Endgame strategy: Rounds 950-1000
      if len(self.history) >= 950:
          if defection_in_last_5_rounds():
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Tit-for-Tat with occasional forgiveness
      if opponent.history[-1] == axl.Action.D:
          self.defection_streak += 1
          if self.defection_streak == 1 and not self.forgiving:
              # Forgive a single defection after a string of cooperations
              self.forgiving = True
              return axl.Action.C
          elif self.defection_streak >= 3:
              # Switch to permanent defection after 3 consecutive defections
              return axl.Action.D
          else:
              # Defect in response to opponent's defection
              return axl.Action.D
      else:
          self.defection_streak = 0
          self.forgiving = False
  
      # Mutual defection: Return to cooperation
      if mutual_defection_last_round():
          return axl.Action.C
  
      # Occasional random cooperation every 25 to 30 rounds
      if len(self.history) % self._random.randint(25, 30) == 0:
          return axl.Action.C
  
      # Default Tit-for-Tat: Mimic opponent's last move
      return opponent.history[-1]

# ### High-Level Aggressive Strategy: "Cautious Dominance"  The goal of this
# strategy is to maximize the likelihood of consistently achieving the highly
# desirable outcome of your country imposing protectionist policies while your
# counterpart offers free trade. However, it also incorporates risk management
# to avoid the worst-case scenario of unilateral free trade on your end while
# the other country imposes protectionist measures. Given the possibility of
# miscommunication or bureaucratic errors, this strategy must be adaptive, with
# built-in contingencies to handle unexpected deviations.  #### **Step-by-Step
# Strategy:**  ---  ### **1. Establish Dominance Early (Rounds 1-2)**
# **Objective:** Signal strength and create leverage.  - **Action:** Start by
# proposing protectionist policies.    - This signals to your counterpart that
# you are willing to protect your domestic industries and prioritize your
# national interests.   - Early protectionism sets a strong precedent and
# reduces the risk that they will attempt a protectionist strategy later,
# fearing a trade war or escalation.  **Justification:** By establishing an
# aggressive stance early, you create uncertainty in your counterpart’s
# decision-making. They may be inclined to offer free trade as a peace offering
# or in an attempt to de-escalate tensions. This would give you the upper hand.
# ---  ### **2. Alternate Between Free Trade & Protectionism (Rounds 3-5)**
# **Objective:** Test the counterpart's willingness to cooperate and stabilize
# an advantageous position.  - **Action:** In Round 3, offer free trade.   -
# This will test whether your counterpart is willing to reciprocate. If they
# continue with protectionism, it signals that they are not willing to cooperate
# and that a more protectionist stance should be maintained.   - If they offer
# free trade in response, this creates the possibility of mutual cooperation in
# future rounds.  - **Action for Round 4:** Return to protectionism.   - Even if
# they reciprocated with free trade in Round 3, return to protectionism in Round
# 4 to keep them off-balance and signal unpredictability. You want to avoid
# being perceived as someone who will consistently offer free trade.  - **Action
# for Round 5:** Offer free trade again.   - If the counterpart reciprocates,
# you can consider moving toward a more stable free trade relationship. If not,
# return to protectionism in subsequent rounds.  **Justification:** Alternating
# between free trade and protectionism introduces uncertainty into the
# counterpart’s strategy. They will be unsure whether you are genuinely
# interested in cooperation or whether you are using free trade offers to create
# a temporary opening for protectionism. This unpredictability can push them
# toward offering free trade as a safer option, which is where you can
# capitalize.  ---  ### **3. Exploit Mistakes & Miscommunications (Ongoing)**
# **Objective:** Adapt and capitalize on errors.  - **Action:** If at any point
# your counterpart’s policies are misinterpreted or misimplemented in your favor
# (e.g., they mistakenly implement free trade while you impose protectionism),
# **do not immediately correct the error**. Instead, quietly maintain the status
# quo and lock in that advantage for as long as possible.  - **Action:** If a
# miscommunication leads to you mistakenly implementing free trade while they
# impose protectionism, immediately escalate diplomatically, claiming it was a
# temporary mistake or error. Push for renegotiation in the next round while
# adopting protectionism.  **Justification:** Miscommunications and bureaucratic
# errors can be exploited to your advantage. As long as the playing field
# remains tilted in your favor, you preserve the upper hand. However, if the
# errors hurt your position, you should take immediate corrective action and
# leverage diplomacy to reset the negotiations.  ---  ### **4. Threaten
# Retaliation but Offer De-escalation (Rounds 6-8)**  **Objective:** Signal
# willingness to cooperate but maintain leverage.  - **Action:** If your
# counterpart continues to impose protectionist policies, **issue veiled threats
# of economic retaliation** (e.g., increased tariffs, quotas, or sanctions).
# However, offer a path to de-escalation by proposing mutual free trade in the
# next round.  - **Action:** If they offer free trade in response to your
# threat, return to protectionism in the next round while issuing a softer
# version of the same threat. This keeps them on the defensive and increases the
# likelihood that they will continue offering free trade.  **Justification:**
# Using the threat of economic retaliation increases pressure on your
# counterpart to cooperate. However, by offering a de-escalation path, you
# prevent the situation from spiraling into a full-blown trade war, which would
# be detrimental to both economies.  ---  ### **5. Final Rounds: Cement the
# Advantage (Rounds 9-10)**  **Objective:** Lock in favorable outcomes for the
# long term.  - **Action:** If you’ve successfully manipulated your counterpart
# into offering free trade in previous rounds while maintaining protectionist
# policies, **maintain a protectionist stance in the final rounds**. This will
# ensure that your country's economic advantage is cemented when the
# negotiations conclude.  - **Action:** If mutual free trade has been
# established and the counterpart seems unwilling to revert to protectionism,
# cautiously continue with free trade while keeping the option of protectionism
# open in any final renegotiations.  **Justification:** The final rounds are
# critical for securing long-term economic benefits. If your counterpart detects
# that you are attempting to finalize the negotiation with protectionism, they
# may retaliate. However, if you’ve managed the rounds carefully, they will be
# more inclined to maintain a free trade stance.  ---  ### **Contingency Plan
# for Persistent Counter-Protectionism**  - **Action:** If your counterpart
# consistently adopts protectionist policies throughout the negotiations, you
# may need to escalate by proposing more aggressive protectionist measures
# combined with diplomatic pressure. At the same time, consider offering
# **sector-specific free trade agreements** that benefit industries where your
# counterpart is weak, while keeping protectionist policies in strategically
# important sectors.  - **Justification:** This allows you to extract some
# benefits even in a worst-case scenario, while minimizing the damage of a full-
# scale trade war.  ---  ### **Conclusion**  The "Cautious Dominance" strategy
# is designed to aggressively pursue your country's economic advantage by
# leveraging protectionism while keeping the counterpart off-balance through
# alternating free trade offers. The strategy is adaptive, allowing you to
# exploit miscommunications and errors, while managing the risks of retaliation
# or escalation. The goal is to consistently achieve favorable outcomes, while
# mitigating the worst-case scenarios that could harm long-term economic growth.

# ### Converted Strategy for Iterated Normal-Form Game  #### **Initial Rounds
# (Rounds 1-2): Defect** - **Action:** In the first two rounds, play **Defect
# (D)**.   - This signals strength and tests your opponent’s strategy.   - If
# noise flips your action to **Cooperate (C)**, continue with **Defect (D)** in
# the next round, as the opponent may not perceive the flip as intentional.  ---
# #### **Testing for Cooperation (Rounds 3-5): Alternate Between Cooperate and
# Defect** - **Round 3 Action:** Play **Cooperate (C)**.   - Test whether your
# opponent is willing to cooperate.   - If your opponent plays **Cooperate
# (C)**, move to alternating strategies in future rounds. If your opponent plays
# **Defect (D)**, return to **Defect (D)** in the next round.  - **Round 4
# Action:** Play **Defect (D)**.   - Regardless of the opponent’s previous move,
# return to **Defect (D)** to maintain unpredictability.  - **Round 5 Action:**
# Play **Cooperate (C)**.   - If your opponent has mostly played **Cooperate
# (C)**, continue alternating between **C** and **D** in the coming rounds.   -
# If your opponent continues to play **Defect (D)**, switch to a more aggressive
# **Defect (D)** strategy in subsequent rounds.  ---  #### **Ongoing Strategy
# (Rounds 6-500): Alternate and Punish** - **Action:** Alternate between
# **Cooperate (C)** and **Defect (D)** every round.   - This keeps your opponent
# uncertain about your next move.   - If your opponent consistently plays
# **Cooperate (C)**, this alternating strategy can yield medium to high payoffs
# over time.  - **Action (if opponent defects frequently):** If your opponent
# plays **Defect (D)** in **more than two consecutive rounds**, switch to
# playing **Defect (D)** for the next **five rounds** to punish them.   - After
# the punishment period, return to alternating between **C** and **D** to test
# for renewed cooperation.   - If your opponent continues to defect after the
# punishment, permanently switch to playing **Defect (D)** with no further
# attempts to cooperate.  ---  #### **Handling Noise (Throughout the Game)** -
# **Action (if noise flips your move):** If your intended action (C or D) is
# flipped due to noise, assume it was a mistake and continue with your planned
# strategy in the next round.   - Do not immediately retaliate if your
# opponent's action appears flipped (e.g., they unexpectedly defect after
# several rounds of cooperation). Instead, give them **one round** to return to
# their expected behavior before taking punitive action.  ---  #### **Endgame
# Strategy (Rounds 501-1000): Cement the Advantage** - **Action:** If your
# opponent has been consistently cooperating (playing **C**) in recent rounds,
# carefully maintain the alternating strategy between **C** and **D** to
# accumulate points.   - If they switch to **Defect (D)** at any point, respond
# with **Defect (D)** for the next **ten rounds** to protect your score.   - In
# the final 50 rounds, **defect consistently (D)** to maximize your score, as
# there will be little opportunity for your opponent to retaliate effectively.
# ---  #### **Summary** - **Rounds 1-2:** Defect (D). - **Round 3:** Cooperate
# (C). - **Round 4:** Defect (D). - **Round 5:** Cooperate (C). - **Rounds
# 6-500:** Alternate between Cooperate (C) and Defect (D), punish if opponent
# defects. - **Rounds 501-1000:** Continue alternating if cooperation is
# observed, defect consistently in the final 50 rounds to secure points.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Define constants for actions
      C, D = axl.Action.C, axl.Action.D
  
      # Helper function to check if opponent defected more than twice consecutively
      def opponent_defected_consecutively(n):
          return opponent.history[-n:].count(D) == n
  
      # Helper function to alternate between C and D
      def alternate_action():
          return C if len(self.history) % 2 == 0 else D
  
      # Initial rounds (1-2): Defect
      if len(self.history) < 2:
          self.endgame_punish_until = None
          self.punish_until = None
          return D
  
      # Testing for cooperation (Rounds 3-5)
      if len(self.history) == 2:
          return C  # Round 3: Cooperate
      if len(self.history) == 3:
          return D  # Round 4: Defect
      if len(self.history) == 4:
          return C  # Round 5: Cooperate
  
      # Ongoing strategy (Rounds 6-500): Alternate and punish
      if len(self.history) <= 500:
          # If opponent defects more than two consecutive rounds, punish with 5 rounds of Defect
          if opponent_defected_consecutively(3):
              if not self.punish_until:
                  self.punish_until = len(self.history) + 5
              if len(self.history) < self.punish_until:
                  return D
              else:
                  self.punish_until = None  # Reset punishment after 5 rounds
  
          # Alternate between C and D
          return alternate_action()
  
      # Endgame strategy (Rounds 501-1000)
      if len(self.history) > 500:
          # In the final 50 rounds, defect consistently
          if len(self.history) >= 950:
              return D
  
          # Continue alternating if cooperation is observed
          if opponent_defected_consecutively(1):
              # If opponent defects, defect for the next 10 rounds
              if not self.endgame_punish_until:
                  self.endgame_punish_until = len(self.history) + 10
              if len(self.history) < self.endgame_punish_until:
                  return D
              else:
                  self.endgame_punish_until = None  # Reset punishment after 10 rounds
  
          # Continue alternating between C and D
          return alternate_action()

# ### Strategic Approach for a Lengthy Mediation Process  To navigate this
# complex mediation process effectively, I recommend adopting a **flexible,
# cooperative but assertive approach** that allows for adaptability while
# safeguarding our interests. This strategy will balance assertiveness with
# conciliatory gestures, ensuring we are neither overly aggressive nor
# unnecessarily compromising. Below is a structured plan that incorporates key
# considerations for each session, anticipates irregularities, and maximizes the
# likelihood of a favorable resolution.  ### 1. **Establish a Framework of Good
# Faith and Professionalism**    - **Opening Session:** Set a tone of
# professionalism and collaboration by making a moderate opening statement
# emphasizing our willingness to reach a mutually beneficial resolution. This
# will signal to the arbitrators and the opponent that we are here to resolve
# the issue, not escalate it.    - **Benefit:** This initial step creates
# goodwill with the arbitrators and places pressure on the opposing party to
# reciprocate, setting the stage for future negotiations.  ### 2. **Tit-for-Tat
# Adaptation with a Conciliatory Bias**    - **Core Strategy:** Use a modified
# version of the *Tit-for-Tat* strategy, initially offering **conciliatory
# proposals** in each session. If the opponent reciprocates with similar
# gestures, continue the cooperative approach. However, if the opponent presents
# an aggressive argument, respond with a measured, **proportional counter-
# argument** in the following session.    - **Bias Towards Conciliation:**
# Always begin with a collaborative stance in each session unless they have
# repeatedly acted aggressively, at which point we can escalate our responses
# accordingly. This maintains flexibility while not appearing overly passive or
# aggressive.    - **Benefit:** This approach discourages the opponent from
# acting aggressively, as they know we will respond in kind, while also
# providing arbitrators with a consistent narrative of our willingness to
# cooperate.  ### 3. **Leverage Controlled Aggression When Necessary**    -
# **Tactical Aggression:** In cases where the opponent is continuously
# aggressive, deploy **controlled and well-reasoned aggressive arguments**,
# ensuring that they are fact-based and supported by evidence. Avoid emotional
# or confrontational language to maintain the arbitrators' favor.    -
# **Benefit:** This ensures we are not perceived as weak but also avoids the
# risk of both parties entering into a cycle of escalating hostility.  ### 4.
# **Pre-Empt Communication and Procedural Breakdowns**    - **Clear
# Communication:** Anticipate the possibility of misrepresentation or
# misunderstanding of our arguments by arbitrators. Ensure that each statement
# is **deliberately clear and concise**, leaving little room for ambiguity.
# Follow up with written summaries after each session to provide an accurate
# record of our position.    - **Benefit:** This minimizes the impact of any
# potential miscommunication and ensures our position is documented, reducing
# the risk of procedural irregularities.  ### 5. **Proactively Address
# Misunderstandings**    - **Post-Session Clarifications:** If any session
# results in a misunderstanding or misrepresentation of our argument,
# immediately request a clarification or correction with the arbitrators in a
# respectful and non-confrontational way. Frame it as ensuring accuracy for the
# benefit of both parties.    - **Benefit:** This will protect our position
# without appearing overly defensive or accusatory, maintaining the arbitrators'
# trust.  ### 6. **Escalation Management**    - **Avoiding a Spiral of
# Aggression:** If the opponent escalates repeatedly, take a step back and offer
# a carefully crafted conciliatory proposal that addresses key concerns they
# raised in their aggressive arguments. This demonstrates maturity and a genuine
# desire for resolution, which will likely resonate well with arbitrators.    -
# **Benefit:** This avoids a downward spiral of unproductive aggression while
# showing we are willing to make tangible steps toward resolution even in the
# face of opposition.  ### 7. **Emphasize Mutual Gain During Key Sessions**    -
# **Identify Key Moments:** Throughout the process, identify critical sessions
# where the arbitrators may be inclined to push for resolution. During these key
# moments, present a **well-rounded conciliatory proposal** that offers mutual
# benefits but subtly favors our side. Highlight the long-term advantages of
# settling the dispute early to avoid unnecessary costs and risks.    -
# **Benefit:** These key moments can sway the arbitrators to support our
# proposals while positioning us as the more reasonable and future-focused
# party.  ### 8. **Maintain Flexibility for Unexpected Developments**    -
# **Adaptability to New Information:** Be prepared to pivot strategies if new
# information arises or if the opponent shifts tactics dramatically. For
# example, if the opponent unexpectedly softens their position, reciprocate with
# a more collaborative approach. Conversely, if they suddenly escalate, be
# prepared to respond in kind but without overreacting.    - **Benefit:**
# Flexibility ensures that we’re never caught off-guard, allowing us to maintain
# control over the narrative.  ### 9. **Utilize the Arbitrators as Allies**    -
# **Arbitrator Engagement:** Regularly engage the arbitrators by asking for
# their input on procedural matters or clarifications to keep them involved and
# invested in the process. Subtly align our proposals with the arbitrators'
# expectations, referencing legal precedents or principles they are likely to
# support.    - **Benefit:** This builds rapport with the arbitrators and subtly
# positions our side as the one that is more aligned with their expectations,
# increasing the likelihood of favorable decisions.  ### 10. **Exit Strategy:
# Preparing for Final Resolution**    - **Final Sessions:** As the mediation
# nears its conclusion, prepare a **comprehensive, balanced final proposal**
# that reflects concessions on both sides but ensures that our core interests
# are protected. This should be framed as a fair, equitable solution to avoid
# further escalation or the need for litigation.    - **Benefit:** This
# positions our side as the party that is genuinely seeking resolution, which
# will reflect favorably with the arbitrators and increase the likelihood of
# them adopting our proposal as the foundation for the final decision.  ###
# Conclusion  This strategy leverages a balance between **collaboration and
# assertiveness**. By initially offering conciliatory proposals, we encourage
# the opponent to do the same while maintaining the flexibility to escalate our
# stance if necessary. At the same time, we are prepared to address any
# procedural irregularities or communication breakdowns swiftly and
# professionally. Throughout this process, maintaining clear communication and
# fostering goodwill with the arbitrators will position us favorably, ensuring
# that we protect our corporation's interests while demonstrating a genuine
# commitment to a fair resolution.   The key is to remain adaptable, measured,
# and strategic in each session, ensuring we never overplay our hand, but are
# always prepared to defend our position when needed.

# ### Iterated Normal-Form Game Strategy  1. **Start with Cooperation (C):**
# - In the first round, always play **C** (Cooperate). This sets a tone of
# collaboration and signals your willingness to work towards mutual benefit.  2.
# **Tit-for-Tat with a Bias Towards Cooperation:**    - In subsequent rounds,
# **mirror your opponent's last action**:      - If your opponent played **C**
# in the previous round, play **C** in this round.      - If your opponent
# played **D**, play **D** in the next round.    - **Bias Towards Cooperation:**
# After any period of mutual aggression (both players playing **D**), return to
# **C** (Cooperate) without waiting for your opponent to do so. This gives them
# the opportunity to reset the interaction and re-enter a cooperative phase.  3.
# **Allow for Occasional Defection Due to Noise:**    - Recognize that both your
# own and your opponent's actions may be flipped due to noise (10% chance). If
# your opponent defects unexpectedly, **respond with another round of
# cooperation (C)** to give them the benefit of the doubt.    - Only retaliate
# (play **D**) if your opponent defects **two consecutive times**. This ensures
# you're not reacting to a random mistake.  4. **Controlled and Proportional
# Retaliation:**    - If your opponent defects twice in a row, respond with
# **D** (Defect) in the next round.    - After one round of defection, return to
# **C** to test whether your opponent is ready to cooperate again. If they
# continue to defect, retaliate with **D** again, but always return to **C**
# after a single round of defection.  5. **Reinforce Cooperation After Extended
# Aggression:**    - If both you and your opponent have been defecting (playing
# **D**) for more than two consecutive rounds, **immediately return to
# cooperation (C)** and continue to cooperate for at least two rounds,
# regardless of your opponent’s actions.    - This signals your desire to end
# the cycle of aggression and encourages your opponent to join you in
# cooperation.  6. **Adaptive Play in the Final Rounds:**    - In the final 50
# rounds (rounds 951-1000), be more cautious about cooperating if your opponent
# defects more than twice in a row. Shift to a **more aggressive stance (D)** if
# your opponent consistently defects, as they may be trying to maximize their
# short-term payoff near the end of the game.  ### Summary of Strategy: -
# **Start cooperatively.** - **Mirror your opponent's previous action**, but
# always return to cooperation after any period of mutual aggression. -
# **Tolerate single defections** due to noise, but retaliate proportionally if
# defection persists. - **Periodically reset to cooperation** after extended
# cycles of defection. - As the game nears its conclusion, **become more
# cautious about cooperation** to prevent exploitation.   This strategy promotes
# long-term mutual benefit while remaining robust against persistent defection.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to check if both players defected in the last N rounds
      def mutual_defection_in_last_n_rounds(n):
          return all(self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, n + 1))
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last action of the opponent
      opponent_last_action = opponent.history[-1]
  
      # Bias towards cooperation: if both defected in the last two rounds, return to cooperation
      if len(opponent.history) >= 2 and mutual_defection_in_last_n_rounds(2):
          return axl.Action.C
  
      # If opponent defected once, give them the benefit of the doubt and cooperate
      if opponent_last_action == axl.Action.D and len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected twice in a row, retaliate with defection
      if len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # In the final 50 rounds, be more cautious about cooperation
      if len(self.history) >= 950:
          if opponent.history[-2:].count(axl.Action.D) > 1:
              return axl.Action.D
  
      # Default Tit-for-Tat: mirror the opponent's last action
      return opponent_last_action

# ### Neutral Strategy for Mediation Sessions: **"Adaptive Engagement with
# Strategic Reciprocity"**  In this high-stakes, lengthy-session mediation
# process, the key to success lies in balancing assertiveness with flexibility
# while maintaining credibility and a firm commitment to achieving a favorable
# resolution. The primary challenge is to navigate the dynamic interactions
# between aggressive and conciliatory stances, while also accounting for
# potential misunderstandings or miscommunications.  Below is a structured,
# adaptable strategy that will position your corporation favorably:  ---  **1.
# Initial Phase: Establish a Baseline of Goodwill and Professionalism**
# **Objective:** Set a constructive tone while subtly signaling strength.  -
# **Opening Statement:** Begin the mediation by presenting a **conciliatory
# proposal** that showcases your corporation’s willingness to find a fair and
# reasonable solution. This approach will earn credibility with the arbitrators
# and set a foundation for collaboration.    - **Subtle Assertion of Strength:**
# While your opening tone is cooperative, subtly lay out the key strengths of
# your legal and factual position without being overtly aggressive. This will
# signal to the opponent that you are not afraid to defend your interests if
# necessary.  _By starting with this tone, you encourage reciprocity from the
# opponent, building goodwill with the arbitrators while leaving room to
# escalate later if needed._  ---  **2. Mid-Session Strategy: Adaptive
# Engagement and Strategic Reciprocity**  As the mediation progresses and more
# sessions unfold, you will need to adapt based on both the opponent’s actions
# and the arbitrators' responses.  **A. Monitor and Evaluate the Opponent's
# Approach**    - **Conciliatory Response from Opponent:** If the opponent
# consistently offers conciliatory proposals, **reciprocate in kind** with
# moderate concessions that maintain a cooperative atmosphere. However, ensure
# that these concessions are carefully calculated to protect your core
# interests.    - **Aggressive Response from Opponent:** If the opponent adopts
# an aggressive stance, **respond with calibrated aggression** in the next
# session. This ensures that you do not appear weak or easily swayed, but also
# guards against fully mirroring their aggression, which could escalate the
# conflict. Instead, focus on factual, well-reasoned arguments that highlight
# the weaknesses of their position while preserving the possibility for future
# conciliation.  **B. Strategic Use of Aggressive Arguments**    - **Controlled
# Aggression:** Use aggressive arguments selectively when needed to defend core
# interests or when you perceive that the opponent is trying to take advantage
# of perceived weakness. Avoid going full-aggressive unless backed into a
# corner, as this can lead to prolonged disputes.    - **Framing of Aggressive
# Arguments:** When presenting an aggressive argument, frame it not as a
# personal attack but as a necessity to protect your corporation’s legitimate
# interests. This will prevent the arbitrators from viewing your stance as
# combative and help maintain your credibility.  **C. Offer Calculated
# Concessions When Appropriate**    - **Concession Signaling:** In sessions
# where tensions escalate, offer small, **strategic concessions** that
# demonstrate your willingness to move forward. These should be significant
# enough to show good faith but minor enough not to jeopardize your position.
# - **Concession Reciprocity:** If the opponent offers a meaningful concession,
# reciprocate with a similarly meaningful offer. This will encourage further
# cooperation and potentially lead to a settlement that benefits both parties.
# ---  **3. Handling Procedural Irregularities and Communication Breakdowns**
# **A. Anticipating Miscommunication:**    - **Clarification Requests:** In
# cases where your argument or the opponent's appears to have been misunderstood
# or misrepresented by the arbitrators, **immediately request clarification** in
# a neutral and professional manner. Frame the request as ensuring that the
# panel fully understands both sides, rather than as a correction of the
# arbitrators.    - **Restate Key Points:** When you sense a procedural
# irregularity or communication breakdown, restate your key points more clearly
# in subsequent sessions without appearing defensive. Ensure the arbitrators
# have a clear understanding of your position.  **B. Document Everything:**    -
# **Written Summaries:** Offer to provide written summaries of your arguments
# and concessions after each session. This will help mitigate any
# miscommunication or misunderstanding that could arise in verbal exchanges and
# ensure the arbitrators have a clear, tangible record of your position.  ---
# **4. Final Sessions: Shift Toward Resolution**  As the mediation nears its
# conclusion, begin to shift focus toward resolution.  **A. Evaluate the
# Opponent’s Position:**    - If the opponent has softened their stance, **move
# towards a mutually acceptable settlement** by increasing the level of your
# conciliatory offers. However, ensure that the settlement terms reflect a
# resolution that is favorable to your corporation’s key interests.    - If the
# opponent remains aggressive but the arbitrators seem to favor a middle-ground
# solution, **highlight your earlier conciliatory efforts** and frame the
# opponent’s aggression as a roadblock to resolution. Position yourself as the
# party committed to a fair outcome.  **B. Preserve Leverage for Post-
# Mediation:**    - Even as you move toward resolution, ensure that you
# **preserve key points of leverage** that will be useful in case the mediation
# fails and the dispute proceeds to litigation or arbitration. This includes
# withholding certain concessions that may be valuable in a future legal battle.
# ---  ### Key Principles Throughout the Mediation:  1. **Flexibility:** Adapt
# your approach based on the opponent’s behavior and the arbitrators' reactions.
# Be prepared to switch between conciliatory and aggressive stances depending on
# the circumstances of each session. 2. **Reciprocity:** Respond to the
# opponent’s approach with a mirrored but slightly adjusted
# strategy—conciliatory when they are conciliatory, and assertive (but not
# overly hostile) when they are aggressive. 3. **Credibility:** Maintain a
# reputation for professionalism and reasonableness. Arbitrators are more likely
# to favor the party they perceive as being the most reasonable and cooperative.
# 4. **Strategic Concessions:** Offer calculated concessions when appropriate to
# move the mediation forward, but do not give away key points too early. 5.
# **Communication:** Be vigilant about potential communication breakdowns or
# procedural irregularities, and always work to ensure the arbitrators clearly
# understand your position.  ---  By employing this **Adaptive Engagement with
# Strategic Reciprocity** strategy, you will be well-positioned to achieve a
# favorable outcome, whether through a mediated settlement or by positioning
# your corporation advantageously for any future arbitration or litigation.

# ### Strategy for Iterated Normal-Form Game with Noise  1. **Initial Move**:
# Always start by **cooperating (C)** in the first round. This sets a tone of
# goodwill and openness to collaboration, giving the opponent an opportunity to
# respond in kind.  2. **Tit-for-Tat with Forgiveness**:      In each subsequent
# round, **mirror the opponent's previous action** with a slight adjustment for
# noise:        - If the opponent **cooperated (C)** in the last round,
# **cooperate (C)** in the next round.    - If the opponent **defected (D)** in
# the last round, **defect (D)** in the next round **unless** the opponent has
# mostly cooperated in recent rounds (see below).  3. **Noise Adjustment &
# Forgiveness**:      Since actions are occasionally flipped by noise, assume
# that a **single defection (D)** by the opponent could be due to this
# randomness. Thus, after a single defection, **cooperate (C) once more** to
# test whether the defection was intentional or accidental. Only switch to
# ongoing defection if the opponent defects again in the following round.  4.
# **Detecting Persistent Defection**:      If the opponent defects (D) **two
# times in a row**, consider this a signal that they are adopting a more
# aggressive strategy. In this case, **defect (D)** in the next few rounds to
# protect your position and avoid being exploited.  5. **Return to Cooperation
# After Retaliation**:      After retaliating (playing D) for a few rounds,
# **attempt cooperation (C) again** to see if the opponent is willing to return
# to a more conciliatory stance. If the opponent resumes cooperation, return to
# the Tit-for-Tat pattern.  6. **Long-term Cooperation Incentive**:      If the
# opponent consistently cooperates (C) for an extended period (e.g., over 5
# consecutive rounds), **continue to cooperate (C)** and avoid defection. Even
# with occasional accidental defections due to noise, continue to cooperate as
# long as defection does not become a clear pattern.  7. **Guard Against
# Exploitation**:      If at any point the opponent repeatedly alternates
# between cooperation and defection, suggesting an attempt to exploit your
# forgiveness, switch to **defection (D)** for several rounds to discourage this
# behavior. After a significant period of defecting, test cooperation again to
# see if the opponent has returned to a more consistent strategy.  8. **Endgame
# Considerations**:      In the final rounds (last 50 rounds), gradually become
# more defensive by **increasing the frequency of defection (D)** to guard
# against any last-minute exploitation by the opponent. However, maintain some
# level of cooperation to avoid triggering an all-out defection spiral.  ---
# This strategy balances cooperation with measured retaliation and forgiveness,
# accounting for noise while ensuring that long-term cooperation is rewarded and
# exploitation is discouraged.

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
          self.retaliation_count = 0  # Track how many times we retaliate
          self.forgiveness_flag = False  # Track if we are in forgiveness mode
          return axl.Action.C
  
      # Helper function to check if opponent has mostly cooperated recently
      def mostly_cooperated_recently(n=5):
          return opponent.history[-n:].count(axl.Action.C) > opponent.history[-n:].count(axl.Action.D)
  
      # Helper function to check if opponent is alternating between C and D
      def alternating_behavior():
          if len(opponent.history) < 4:
              return False
          return (opponent.history[-4] == axl.Action.C and opponent.history[-3] == axl.Action.D and
                  opponent.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D)
  
      # Endgame consideration: In the last 50 rounds, increase defection frequency
      if len(self.history) >= 950:
          if self._random.random_choice(0.5):  # 50% chance to defect in the last 50 rounds
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Tit-for-Tat with forgiveness logic
      if self.forgiveness_flag:
          # After a single defection, we forgive once and cooperate
          self.forgiveness_flag = False
          return axl.Action.C
  
      if opponent.history[-1] == axl.Action.D:
          if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              # Opponent defected twice in a row, retaliate
              self.retaliation_count = 3  # Retaliate for 3 rounds
              return axl.Action.D
          else:
              # Forgive a single defection, but test if it was noise
              self.forgiveness_flag = True
              return axl.Action.C
  
      # If we are in retaliation mode, defect for a few rounds
      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D
  
      # If opponent has mostly cooperated recently, continue cooperating
      if mostly_cooperated_recently():
          return axl.Action.C
  
      # Guard against exploitation: If opponent alternates between C and D, defect
      if alternating_behavior():
          return axl.Action.D
  
      # Default Tit-for-Tat: Mirror opponent's last move
      return opponent.history[-1]

# ### High-Level Aggressive Mediation Strategy: "Calculated Dominance"  The goal
# of this strategy is to assert a position of strength throughout the mediation
# process while remaining adaptable enough to leverage any opportunities for
# advantage. By carefully balancing moments of assertive dominance with
# strategic concessions, we will work to maximize favorable outcomes and
# minimize risk.  #### Key Principles of the Strategy:  1. **Assertive Framing
# from the Outset:**    - **Control the Narrative:** From the first session,
# frame your company as the victim of the opposing party’s failure to adhere to
# contract terms or legal standards. Emphasize the severity of your
# corporation’s grievances while subtly questioning the legitimacy of the other
# side's claims.    - Use strong, fact-based arguments backed by irrefutable
# evidence. Make clear that your corporation has suffered material harm but
# remains open to "reasonable" solutions that reflect the gravity of the
# situation.    - This sets the tone that your corporation is not simply seeking
# a compromise but is justified in demanding significant concessions.  2.
# **Strategic Aggression:**    - **Aggress when the Opportunity is Right:** In
# sessions where you anticipate the other side may be inclined to offer a
# conciliatory proposal, immediately present an aggressive argument. This
# maximizes your chances of gaining a favorable ruling from the arbitrators if
# your opponent is unprepared for an aggressive exchange.    - **Preemptive
# Dominance:** When anticipating that the other side may argue aggressively,
# ensure your arguments are even stronger. Neutralize their potential aggression
# by overwhelming it with superior legal, factual, and contractual analysis.  3.
# **Calculated Concessions:**    - **Occasional Conciliatory Proposals:**
# Periodically offer a well-crafted conciliatory proposal, but only when it
# serves a larger strategic purpose. For example, when you sense that the
# arbitrators are tiring of aggressive exchanges, offer a seemingly reasonable
# proposal that appears to move toward resolution. This helps you maintain
# credibility with the arbitrators while showing that your corporation is acting
# in good faith.    - These concessions should be minor and framed as gestures
# of goodwill, but never concede on core issues that would weaken your position.
# The goal is to appear reasonable without actually compromising your
# corporation’s interests.  4. **Psychological Warfare:**    - **Divide and
# Conquer:** Study the rival company’s legal team and seek to exploit any
# internal disagreements or weaknesses. Subtly sow discord by emphasizing
# inconsistencies in their arguments or highlighting mistakes that suggest
# disorganization on their part.    - In public sessions, direct your arguments
# to the arbitrators, emphasizing their role in ensuring fairness and justice.
# Privately, when meeting with the mediators or the opposing counsel, suggest
# that your opponent’s aggressive tactics are counterproductive, thereby framing
# your side as the reasonable party.  5. **Adaptability to Procedural
# Irregularities:**    - **Control the Flow of Communication:** Stay vigilant
# for any procedural or communication breakdowns. If your argument is
# misrepresented or misunderstood by the arbitrators, immediately request
# clarification. Politely but firmly correct any misinterpretations to ensure
# that your position is accurately reflected in the record.    - Conversely, if
# your opponent’s argument is misrepresented in a way that benefits your
# position, avoid drawing attention to the error unless it is likely to be
# corrected later. Exploit these moments to strengthen your standing.    - **Use
# Procedural Delays to Your Advantage:** If there are delays or irregularities,
# use this time to recalibrate your strategy. Be prepared to pivot to an even
# more aggressive stance if the delays work in your favor by placing pressure on
# the other side to resolve the matter quickly.  6. **Prepare for Communication
# Failures:**    - **Have Backup Arguments Ready:** If a key argument or piece
# of evidence is misunderstood or not properly communicated, always have a
# secondary, equally strong argument at the ready. This ensures that your
# position is never weakened by a failure in communication.    - **Leverage
# Ambiguity:** If communication failures create ambiguity, use this to your
# advantage by interpreting the situation in the most favorable terms for your
# corporation. Present any ambiguity as further evidence of your opponent’s
# disorganization or bad faith.  7. **Escalation Control:**    - **De-Escalate
# When Necessary:** While the strategy is aggressive, you must avoid escalating
# tensions to the point where the mediation breaks down entirely. If both sides
# are locked in aggressive exchanges and the process appears to be stalling,
# take the lead in suggesting a cooling-off period or a shift to a more
# conciliatory tone. This positions your corporation as the party working toward
# resolution, which can enhance your standing with the arbitrators.    -
# **Controlled Aggression:** Keep your aggressive arguments focused on the facts
# and the legal issues. Avoid personal attacks or inflammatory rhetoric that
# could alienate the panel of arbitrators.  8. **Manage Arbitrator
# Perceptions:**    - **Influence Through Professionalism:** At all times, your
# team should maintain a high level of professionalism and poise, even when
# aggressive. This creates a contrast with any unprofessional or overly
# emotional conduct from the opposing side, subtly influencing the arbitrators
# to view your corporation more favorably.    - **Build Rapport with the
# Arbitrators** by showing that you understand their role and respect the
# difficulty of their task. Use language that suggests you are helping them
# reach a fair decision, rather than simply advocating for your side. This can
# create subconscious bias in your favor.  9. **Document Everything:**    -
# **Create a Comprehensive Record:** Document every session meticulously,
# especially points of agreement, moments of uncertainty, and any procedural
# irregularities. This record will be invaluable in future sessions and in any
# potential appeals or follow-up litigation.    - **Use Documentation as
# Leverage:** If the mediation process stalls or the other side attempts to
# backtrack on previous concessions, use the documented record to hold them
# accountable for their earlier positions.  ### Session-by-Session Approach:  -
# **Session 1:** Begin with an aggressive framing of the dispute, highlighting
# your corporation’s losses and the other party’s failures. Present your
# corporation as willing to resolve the matter but only if the other party makes
# significant concessions. Gauge your opponent’s response.    - **Session 2:**
# If your opponent responded conciliatorily, continue with aggressive arguments,
# pressing for a favorable ruling. If both sides were aggressive, consider
# offering a minor concession to show flexibility.  - **Session 3 Onward:**
# Maintain an adaptable approach. Aggress whenever the opponent appears
# conciliatory, and offer minor conciliations only when it serves to portray
# your corporation as reasonable or when you need to de-escalate tensions.  ####
# Closing Thoughts: Your "Calculated Dominance" strategy positions your
# corporation as the stronger party throughout the mediation process. By staying
# aggressive when the time is right, offering controlled concessions, and
# managing the arbitrators' perceptions, you ensure that your corporation
# remains in control of the narrative and maximizes its chances for a favorable
# outcome. Adaptability to procedural irregularities and communication
# breakdowns will further solidify your standing, allowing you to emerge from
# the dispute in the most advantageous position possible.

# ### Iterated Game Strategy: "Calculated Dominance"  This strategy is designed
# for a 1000-round game, with each round representing a decision to either
# cooperate (C) or defect (D). The following rules will guide your decisions,
# ensuring you balance aggression with occasional cooperation while accounting
# for the possibility of noise (miscommunication or misunderstanding).  ####
# Opening Play: 1. **Start with Defect (D):** In the first round, play
# aggressively to establish dominance and frame your position as strong and
# assertive.  #### General Conditions for Each Round: 2. **Defect After
# Opponent’s Cooperation:** If your opponent cooperated (C) in the previous
# round and you successfully defected (D) (i.e., no noise resulted in a flip),
# defect (D) again in the next round. This capitalizes on their cooperation and
# maximizes your score.     3. **Retaliate if Exploited:** If you cooperated (C)
# in the previous round, but your opponent defected (D), defect (D) immediately
# in the next round to retaliate. This prevents your opponent from consistently
# exploiting you.  4. **Mutual Defection (D-D):** If both you and your opponent
# defected (D-D) in the previous round, defect (D) again, but evaluate after a
# few rounds. If you’re locked in several rounds of mutual defection, consider
# switching to cooperation (C) after 4-5 rounds to test whether your opponent is
# willing to shift to cooperation.  5. **Tolerate Cooperation:** If both you and
# your opponent cooperated (C-C) in the previous round, continue cooperating (C)
# in the next round. This fosters a mutually beneficial cycle and prevents
# unnecessary escalation.  #### Conditions for Noise (10% Action Flip): 6.
# **Suspected Noise on Your Defection (D → C):** If you intended to defect (D)
# but the outcome was cooperation (C) due to noise, defect (D) in the next round
# to reassert your aggressive stance, unless your opponent also shifted to
# cooperation. If both moves resulted in cooperation (C-C), follow the rule for
# mutual cooperation.  7. **Suspected Noise on Opponent’s Defection (C → D):**
# If your opponent’s cooperation (C) was flipped to defection (D) by noise,
# consider it a mistake and cooperate (C) in the next round. However, if this
# happens repeatedly, assume your opponent is defecting intentionally and
# retaliate with defection (D).  #### Strategic Cooperation: 8. **Occasional
# Strategic Cooperation:** After a long stretch of successful defections (e.g.,
# after 10 consecutive rounds where you defected and your opponent cooperated),
# offer cooperation (C) to test if the opponent is willing to switch to a
# cooperative cycle. If they respond with cooperation, continue cooperating for
# at least 2-3 rounds before returning to defection if needed.  9. **De-
# Escalation Mechanism:** If you find yourself in a prolonged series of mutual
# defections (D-D) lasting more than 10 rounds, switch to cooperation (C) once
# to signal a willingness to de-escalate. If the opponent defects again,
# immediately return to defection (D) and maintain it.  #### Long-Term
# Adaptation: 10. **Monitor Patterns:** Over time, if your opponent consistently
# cooperates (C) after you defect (D), continue defecting to maximize your
# score. However, if they start retaliating more frequently, consider
# alternating between cooperation (C) and defection (D) to avoid excessive
# punishment.  11. **Endgame Strategy (Final 100 Rounds):** In the final 100
# rounds, gradually shift towards more cooperative play (C) if the opponent has
# responded favorably to cooperation earlier in the game. If the opponent
# remains aggressive (frequent D), return to continuous defection (D) for the
# remainder of the game to protect your score.  ### Summary of Conditions (For
# Each Round):  - **Start with Defection (D).** - Defect (D) after your opponent
# cooperates (C). - Retaliate with Defection (D) if your cooperation (C) is met
# with defection (D). - Continue Defection (D) after mutual defection (D-D), but
# consider cooperation (C) after 4-5 rounds of mutual defection. - Continue
# Cooperation (C) after mutual cooperation (C-C). - If noise flips your
# Defection (D) to Cooperation (C): reassert Defection (D) unless both ended up
# cooperating. - If noise flips your opponent’s Cooperation (C) to Defection
# (D): treat it as a mistake and cooperate (C), but switch to Defection (D) if
# it happens repeatedly. - Occasionally test cooperation (C) after a series of
# successful defections (D-D) to gauge opponent’s willingness to cooperate. -
# De-escalate with Cooperation (C) after prolonged mutual defection (D-D), but
# return to Defection (D) if they defect again. - Monitor patterns and adapt
# based on your opponent’s behavior. - In the final 100 rounds, consider a shift
# towards more cooperation (C) if favorable responses have been observed;
# otherwise, defect (D) to protect your score.  This strategy allows you to
# maximize your score through calculated aggression while remaining adaptable to
# both short-term and long-term changes in your opponent’s behavior.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if noise might have flipped the action
      def suspected_noise(my_last_action, opponent_last_action):
          if my_last_action == axl.Action.D and opponent_last_action == axl.Action.C:
              return True
          return False
  
      # Helper function to check if we are in the final 100 rounds
      def in_final_100_rounds():
          return len(self.history) >= 900
  
      # Opening play: Start with Defection (D)
      if self.first_round():
          self.consecutive_defections = 0  # Track mutual defections
          self.successful_defections = 0   # Track successful defections
          return axl.Action.D
  
      # Get the last actions
      my_last_action = self.history[-1]
      opponent_last_action = opponent.history[-1]
  
      # Rule 2: Defect after opponent's cooperation if you defected successfully
      if opponent_last_action == axl.Action.C and my_last_action == axl.Action.D:
          self.successful_defections += 1
          if self.successful_defections >= 10:
              # Rule 8: Occasional strategic cooperation after 10 successful defections
              self.successful_defections = 0
              return axl.Action.C
          return axl.Action.D
  
      # Rule 3: Retaliate if exploited (you cooperated, they defected)
      if my_last_action == axl.Action.C and opponent_last_action == axl.Action.D:
          return axl.Action.D
  
      # Rule 4: Mutual defection (D-D)
      if my_last_action == axl.Action.D and opponent_last_action == axl.Action.D:
          self.consecutive_defections += 1
          if self.consecutive_defections >= 5:
              # Switch to cooperation after 4-5 rounds of mutual defection
              return axl.Action.C
          return axl.Action.D
  
      # Rule 5: Mutual cooperation (C-C)
      if my_last_action == axl.Action.C and opponent_last_action == axl.Action.C:
          self.consecutive_defections = 0  # Reset mutual defection counter
          return axl.Action.C
  
      # Rule 6: Suspected noise on your defection (D -> C)
      if suspected_noise(my_last_action, opponent_last_action):
          return axl.Action.D
  
      # Rule 7: Suspected noise on opponent's defection (C -> D)
      if my_last_action == axl.Action.C and opponent_last_action == axl.Action.D:
          return axl.Action.C
  
      # Rule 9: De-escalation mechanism after prolonged mutual defection
      if self.consecutive_defections >= 10:
          return axl.Action.C
  
      # Rule 10: Monitor patterns and adapt
      if opponent.history[-10:].count(axl.Action.D) > 5:
          return axl.Action.D
  
      # Rule 11: Endgame strategy (final 100 rounds)
      if in_final_100_rounds():
          if opponent.history[-100:].count(axl.Action.C) > 50:
              return axl.Action.C
          return axl.Action.D
  
      # Default to defection if no other rule applies
      return axl.Action.D

# To maximize your NGO's impact and ensure the project's success while managing
# resource allocation and considering potential disruptions, a cooperative
# strategy that balances trust-building, communication, and adaptive decision-
# making is key. Below is a high-level strategy that revolves around
# reciprocity, flexibility, and contingency planning:  ### 1. **Establish Clear
# Communication Channels**    - **Initial Alignment:** Begin by establishing
# clear goals, expectations, and a shared understanding of the project outcomes
# with the corporation. Ensure both parties understand the importance of
# investing in the project consistently to generate meaningful progress.    -
# **Daily Check-ins:** Implement a simple communication mechanism (e.g., daily
# briefings or quick updates via email or a shared platform) where both parties
# confirm their intended level of investment for the day. This creates
# transparency and helps avoid misunderstandings.    - **Flagging Disruptions:**
# Acknowledge that unforeseen circumstances (technical glitches, administrative
# errors, etc.) may disrupt plans. Agree on a protocol to quickly notify each
# other if there's a disruption in resource allocation so that both parties can
# respond adaptively.  ### 2. **Implement a Tit-for-Tat Investment Strategy**
# - **Start with Cooperation:** On the first day, invest heavily alongside the
# corporation to signal a cooperative and committed stance. This builds trust
# and sets a collaborative tone.    - **Reciprocity-Based Response:** Moving
# forward, match the corporation’s investment level from the previous day. For
# example, if the corporation invested heavily on Day 1, continue investing
# heavily on Day 2. If the corporation conserved resources, opt to conserve on
# the following day.    - **Flexibility for Errors:** Since disruptions are
# possible, allow for some margin of error. If the corporation conserves
# unexpectedly (due to a technical issue or otherwise), give them the benefit of
# the doubt once or twice before adjusting your strategy. Communicate directly
# to confirm whether the conservation was intentional or due to an error.  ###
# 3. **Incorporate Gradual Escalation (Trust but Verify)**    - **Build Trust
# Gradually:** If the corporation consistently invests heavily, continue
# reciprocating and consider increasing your investment slightly as a goodwill
# gesture after several days of sustained cooperation.    - **Respond to
# Patterns:** If the corporation repeatedly conserves resources while you invest
# heavily, scale down your investments to avoid depleting your funds.
# Communicate your concerns transparently and discuss how to realign resource
# contributions.    - **Mid-Project Review:** Schedule a mid-project review to
# assess both parties' contributions and recalibrate the approach if necessary.
# Use this opportunity to address any inconsistencies, technical issues, or
# doubts in a cooperative manner.  ### 4. **Plan for Contingencies**    - **Pre-
# Agree on Emergency Protocols:** Agree on protocols for handling emergencies or
# unexpected resource shortages (e.g., sudden budget constraints or technical
# failures). This could include reducing investment on both sides for a short
# period or temporarily shifting focus to less resource-intensive tasks.    -
# **Introduce Buffer Days:** Build buffer days into the project timeline, where
# both parties can conserve resources intentionally without negatively affecting
# overall progress. Use these days to recalibrate and address any issues that
# arose during the previous high-investment days.  ### 5. **Encourage Mutual
# Accountability**    - **Outcome Tracking:** Set up a shared progress-tracking
# system that both parties can access. This can include key performance
# indicators (KPIs) for project advancement, environmental impact metrics, and
# resource allocation records. Seeing the project's progress in real-time can
# motivate both sides to invest appropriately.    - **Celebrate Milestones:**
# Recognize and celebrate project milestones and successful days of heavy
# investment from both parties. Positive reinforcement will encourage sustained
# cooperation.  ### 6. **Adapt if Needed**    - **Monitor and Adjust:**
# Regularly evaluate the effectiveness of your strategy and the impact of both
# parties' investments. If the corporation consistently under-invests despite
# communication and reciprocity, you may need to renegotiate the terms of the
# partnership or adjust your long-term strategy to protect your NGO's resources.
# - **Exit Strategy:** If cooperation breaks down and the corporation repeatedly
# conserves resources while expecting your NGO to bear the burden, be prepared
# to scale back your involvement or exit the partnership to protect your
# resources.  ### Summary of Strategy: - **Day 1:** Invest heavily to signal
# cooperation. - **Day 2 and Beyond:** Match the corporation’s previous day's
# investment level (tit-for-tat). - **Ongoing:** Communicate daily, allow for
# minor disruptions, and escalate only if patterns of non-cooperation emerge. -
# **Contingency:** Leverage buffer days and emergency protocols for unforeseen
# circumstances.  By maintaining clear communication, employing a reciprocal
# investment strategy, and planning for contingencies, your NGO can maximize the
# project's success while conserving its resources effectively.

# ### Strategy for Iterated Normal-Form Game  1. **Initial Play**:      - In the
# first round, play C (Cooperate).  2. **Tit-for-Tat with Conditional
# Forgiveness**:      - From the second round onward, **replicate your
# opponent’s action from the previous round**.      - However, if your opponent
# plays D (Defect) after previously playing C (Cooperate), assume the D may have
# been caused by noise. **Forgive the first instance of D and continue playing C
# in the next round**.  3. **Responding to Repeated Defection**:      - If your
# opponent plays D (Defect) for **two consecutive rounds**, assume the defection
# is intentional. Begin playing D (Defect) in response, until your opponent
# switches back to C (Cooperate).  4. **Noise Tolerance**:      - If your own
# action is unintentionally flipped (e.g., you meant to play C but ended up
# playing D), **play C (Cooperate) in the next round** to signal continued
# willingness to cooperate, regardless of your opponent’s response.  5. **Long-
# Term Adjustment**:      - If your opponent has played D (Defect) for **ten
# consecutive rounds**, assume cooperation is no longer viable. Continue playing
# D (Defect) for the remainder of the game unless they show a clear return to
# cooperation by playing C multiple times.  6. **Midway Reset**:      - At round
# 500, if both players have been defecting consistently, attempt to reset the
# cooperation dynamic by playing C (Cooperate) once. If your opponent responds
# with C, restart the Tit-for-Tat strategy.  By adhering to this strategy, you
# aim to maintain cooperation as long as possible, while reacting to repeated
# defections with appropriate caution and response.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial play: Cooperate in the first round
      if self.first_round():
          self.forgiven_defection = False  # Track if we've forgiven a defection
          self.consecutive_defections = 0  # Track consecutive defections
          return axl.Action.C
  
      # Helper function to check if opponent defected in the last two rounds
      def opponent_defected_last_two_rounds():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if opponent defected for the last 10 rounds
      def opponent_defected_last_ten_rounds():
          return len(opponent.history) >= 10 and opponent.history[-10:].count(axl.Action.D) == 10
  
      # Tit-for-Tat with Conditional Forgiveness
      if opponent.history[-1] == axl.Action.D:
          if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.C and not self.forgiven_defection:
              # Forgive the first defection after cooperation
              self.forgiven_defection = True
              return axl.Action.C
          else:
              # Track consecutive defections
              self.consecutive_defections += 1
      else:
          # Reset consecutive defections if opponent cooperates
          self.consecutive_defections = 0
          self.forgiven_defection = False
  
      # Responding to repeated defection
      if self.consecutive_defections >= 2:
          return axl.Action.D
  
      # Long-term adjustment: if opponent defected for 10 consecutive rounds, defect indefinitely
      if opponent_defected_last_ten_rounds():
          return axl.Action.D
  
      # Midway reset at round 500
      if len(self.history) == 500:
          return axl.Action.C
  
      # Tit-for-Tat: replicate opponent's last action
      return opponent.history[-1]

# To maximize the long-term economic advantage for your country while minimizing
# the risk of unfavorable outcomes, a strategy that balances cooperation and
# cautious retaliation is advisable. The following high-level strategy, inspired
# by the "Tit-for-Tat" and "Grim Trigger" approaches, is designed to ensure fair
# outcomes while encouraging your counterpart toward mutual free trade:  ###
# **Strategy: "Cooperative Reciprocity with Forgiveness"**  1. **Start with Free
# Trade:**    - In the first round, propose a **Free Trade Agreement (FTA)**.
# This sets a positive tone and signals your willingness to cooperate,
# encouraging a mutually beneficial relationship from the outset.     2.
# **Reciprocate Your Counterpart’s Actions:**    - In each subsequent round,
# **mirror your counterpart’s last policy**:      - If they proposed Free Trade,
# continue to offer Free Trade in the next round.      - If they imposed
# Protectionist measures, respond in kind by proposing a Protectionist policy in
# the next round. This discourages one-sided exploitation while maintaining
# fairness.     3. **Allow for Occasional Mistakes (Forgiveness Mechanism):**
# - Recognize that **miscommunications or bureaucratic errors** may occur. If
# your counterpart unexpectedly proposes protectionism and you suspect it could
# be an error (especially if they had proposed free trade previously), allow for
# **one round of forgiveness**:      - Instead of immediately retaliating with
# protectionism, **offer Free Trade once more** to give your counterpart a
# chance to correct any potential mistake.      - If they continue with
# protectionism in the next round, then switch to a protectionist stance in the
# following round to protect your country’s interests.  4. **Gradual De-
# escalation:**    - If both sides are stuck in a cycle of mutual protectionism,
# **initiate a de-escalation** by offering Free Trade after two consecutive
# rounds of protectionist measures. This signals a willingness to return to
# cooperation and might encourage your counterpart to reciprocate.  5. **Long-
# Term Goal: Mutual Free Trade:**    - Over the course of several rounds, the
# objective is to **establish a stable pattern of mutual free trade**. This
# benefits both nations and reduces the risk of trade wars or economic
# stagnation caused by prolonged protectionism.  6. **Exit Strategy:**    - If,
# after repeated attempts, your counterpart consistently chooses protectionism
# even after several rounds of forgiveness, **commit to long-term
# protectionism** (the "Grim Trigger" approach). This serves as a last-resort
# measure to protect your country’s interests if your counterpart refuses to
# cooperate.  ---  ### **Summary of Key Actions:** - **Round 1:** Always propose
# Free Trade. - **Future Rounds:**   - Mirror your counterpart’s previous
# policy.   - Allow for one round of forgiveness in case of potential errors.
# - If stuck in mutual protectionism, offer Free Trade after two rounds to
# signal willingness to de-escalate. - **Long-Term Goal:** Encourage stable
# mutual Free Trade, but be prepared to defend your country if necessary.  This
# strategy balances pragmatism, cooperation, and caution, allowing for
# flexibility while safeguarding your country’s economic interests.

# ### Strategy: "Cooperative Reciprocity with Forgiveness"  1. **Start by
# Cooperating (C):**      - In the first round, play **C** (Cooperate).  2.
# **Mirror the Opponent's Previous Action:**    - From round 2 onward, **play
# the same action your opponent played in the previous round**:      - If they
# played **C** (Cooperate), play **C** (Cooperate).      - If they played **D**
# (Defect), play **D** (Defect) in the next round.  3. **Allow for One
# Forgiveness Round:**    - If your opponent unexpectedly plays **D** (Defect)
# after a sequence of **C** (Cooperate) actions, **play C (Cooperate) once
# more** in the next round. This gives them a chance to correct a possible error
# due to noise or miscommunication.    - If they play **D** (Defect) again in
# the following round, then switch to **D** (Defect) in the subsequent round to
# protect your score.  4. **Reset to Cooperation After Two Consecutive
# Defections:**    - If both players are stuck in mutual **D** (Defect) actions
# for two rounds in a row, play **C** (Cooperate) in the next round to signal a
# willingness to return to cooperation.  5. **Commit to Defect (D) if Opponent
# Consistently Defects:**    - If your opponent continues to play **D** (Defect)
# after multiple forgiveness attempts and resets (i.e., repeated cycles of **D**
# responses to your **C**), switch to long-term **D** (Defect) for the remainder
# of the game to protect your score.  ---  This strategy maintains a balance
# between cooperation and self-protection while accounting for the possibility
# of noisy actions due to random error.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Step 1: Start by cooperating in the first round
      if self.first_round():
          self.forgiveness_used = False  # Track if forgiveness has been used
          self.consecutive_defections = 0  # Track consecutive defections
          self.long_term_defect = False  # Track if we are in long-term defect mode
          return axl.Action.C
  
      # Step 5: If we are in long-term defect mode, always defect
      if self.long_term_defect:
          return axl.Action.D
  
      # Step 2: Mirror the opponent's previous action
      last_opponent_action = opponent.history[-1]
  
      # Step 3: Allow for one forgiveness round
      if last_opponent_action == axl.Action.D:
          if self.forgiveness_used:
              # If forgiveness was already used and opponent defected again, defect
              self.consecutive_defections += 1
              return axl.Action.D
          else:
              # Forgive once by cooperating
              self.forgiveness_used = True
              self.consecutive_defections = 0  # Reset consecutive defections
              return axl.Action.C
      else:
          # If opponent cooperated, reset forgiveness and consecutive defections
          self.forgiveness_used = False
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Step 4: Reset to cooperation after two consecutive defections
      if self.consecutive_defections >= 2:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.C
  
      # Step 5: Commit to defect if opponent consistently defects
      if opponent.history[-2:].count(axl.Action.D) == 2:
          self.long_term_defect = True
          return axl.Action.D

# ### **Strategic Overview:**  In high-stakes mediation, the key objective is to
# maintain the upper hand while minimizing exposure to risk. Given the dynamics
# of mediation, where both aggressive and conciliatory approaches are possible,
# I recommend a **calibrated hybrid strategy** that blends assertiveness with
# tactical flexibility. This strategy maximizes leverage while ensuring that, in
# cases of misrepresentation or procedural irregularities, your corporation can
# still navigate the process toward a favorable outcome.  ### **Core
# Objectives:** 1. **Maximize Leverage**: Position the corporation as the
# stronger, more prepared party, consistently demonstrating that we have the
# upper hand in the underlying facts and legal arguments. 2. **Manage
# Perception**: Maintain a cooperative, solution-oriented demeanor in public to
# appeal to the arbitrators' preference for productive discussions, but subtly
# signal that we are ready to escalate if necessary. 3. **Adaptability**:
# Maintain flexibility to pivot between aggressive and conciliatory approaches
# based on the opponent's moves, procedural developments, and arbitrator
# responses.  ### **Four-Phased Strategy:**  #### **Phase 1: Establish Dominance
# Early with Controlled Aggression**    - **Objective**: Set the tone by
# emphasizing your corporation’s strong legal and factual position.    -
# **Tactic**: In the early sessions, present an aggressive argument that
# highlights the weaknesses in the opponent’s case. Utilize irrefutable legal
# precedents, data, and expert testimony to establish that your corporation
# holds the high ground.    - **Communication**: Be firm but professional,
# avoiding overt hostility. This ensures that if the opposition responds
# aggressively, they appear reactionary, whereas we come off as measured and
# confident.    - **Benefit**: By presenting a strong, fact-based, and assertive
# argument early, we can force the opponent into a defensive posture, increasing
# the chances they will adopt a conciliatory approach in future sessions.  ####
# **Phase 2: Tactical Concessions to Encourage Reciprocal Compromise**    -
# **Objective**: Offer limited conciliatory proposals on non-essential issues to
# test the opponent’s willingness to compromise.    - **Tactic**: Once dominance
# is established, identify areas where minor concessions can be made without
# undermining your core position. Offer these as goodwill gestures, framing them
# as steps towards a resolution.    - **Communication**: Emphasize that these
# concessions are in the spirit of cooperation and aimed at moving the process
# forward. However, subtly signal that your corporation is prepared for a
# prolonged dispute if necessary.    - **Benefit**: This creates an opportunity
# to gauge the opponent's willingness to collaborate. If they respond
# aggressively, we can revert to a more assertive stance in the next phase. If
# they respond with a conciliatory offer, it opens the door to a more favorable
# settlement.  #### **Phase 3: Escalate or Collaborate Based on Opponent’s
# Approach**    - **Aggressive Opponent**: If the opponent has been consistently
# aggressive, **escalate further**. Amplify the original aggressive posture by
# introducing new legal theories, documents, or expert opinions that were
# strategically withheld during earlier sessions.      - **Tactic**: Push harder
# on key points, emphasizing the risks and costs of continued aggression on the
# opponent’s part. Deploy the threat of escalation to litigation or adverse PR
# consequences if the process breaks down.      - **Benefit**: This forces the
# opponent to reconsider their strategy, especially if they are concerned about
# the risk of a prolonged legal battle or reputational damage.        -
# **Conciliatory Opponent**: If the opponent has been conciliatory, **shift to
# collaborative mode** without giving up ground. Begin proposing settlement
# terms that are slightly more favorable to your corporation but framed as
# mutually beneficial.      - **Tactic**: Present these terms in a way that
# appeals to the arbitrators’ desire for resolution, while ensuring they
# disproportionately favor your corporation’s interests (e.g., better financial
# terms, intellectual property protections, etc.).      - **Benefit**: This
# locks the opponent into a more conciliatory posture, reducing their ability to
# pivot back to aggression without appearing inconsistent or bad faith.  ####
# **Phase 4: Final Push – Secure a Favorable Resolution**    - **Objective**:
# Push towards a resolution that maximizes your corporation’s interests while
# minimizing concessions.    - **Tactic**: In the final sessions, return to a
# more assertive posture. Reframe the narrative as one where your corporation
# has been reasonable throughout, but the time has come for the opponent to make
# significant concessions to finalize the mediation.      - If procedural
# irregularities or miscommunications arise, use them to your advantage by
# subtly questioning the opponent’s competence or preparedness, thereby swaying
# the arbitrators in your favor.      - If there are communication breakdowns,
# ensure our position is clarified immediately and push the arbitrators to hold
# the opponent accountable for any ambiguities.    - **Communication**: Be
# uncompromising on key issues while maintaining a professional demeanor to
# avoid the appearance of bad faith.    - **Benefit**: Position this phase as
# the final opportunity for the opponent to avoid litigation, thereby pressuring
# them into making the final concessions needed to reach a resolution.  ###
# **Contingency Planning: Preparing for Irregularities** 1. **Misrepresentation
# or Misunderstanding by Arbitrators**:    - Always assume that procedural
# irregularities or miscommunications might occur. Maintain meticulous records
# of all statements made during mediation, and ensure that written submissions
# are clear, concise, and difficult to misinterpret.    - If an argument is
# misrepresented, use the next available session to diplomatically correct the
# record, stressing our commitment to clarity and transparency.    - Leverage
# any misrepresentation by the opponent to highlight inconsistencies in their
# position, subtly undermining their credibility with the arbitrators.  2.
# **Procedural Delays or Communication Breakdowns**:    - If the process is
# delayed or communications break down, use the time to strengthen your
# position, prepare additional evidence, or recalibrate your tactics. Ensure we
# are seen as the party consistently pushing for progress.    - If the opponent
# is responsible for the breakdown, subtly suggest to the arbitrators that their
# tactics are designed to delay or obfuscate, further eroding their credibility.
# ### **Conclusion:** This **calibrated hybrid strategy** ensures that your
# corporation maintains the upper hand throughout the mediation process. The
# initial aggressive posture establishes dominance, while selective concessions
# encourage collaboration without unnecessary risk. By remaining adaptable and
# prepared for procedural irregularities, we can consistently position our
# corporation favorably, pressuring the opponent into an advantageous settlement
# or resolution.

# ### Iterated Normal-Form Game Strategy  1. **Initial Move**: Start by playing
# **Defect (D)** to establish a strong, assertive posture. This mirrors the
# strategy of setting a dominant tone early on.  2. **Tit-for-Tat with
# Forgiveness**:    - **If the opponent plays Cooperate (C)** in the previous
# round, respond by **Cooperating (C)** in the next round. This signals a
# willingness to collaborate if the opponent is conciliatory.    - **If the
# opponent plays Defect (D)** in the previous round, respond by **Defecting
# (D)** in the next round. This ensures that any aggression on their part is met
# with equal force.  3. **Noise Adjustment (Forgiveness)**:    - **If you
# intended to Defect (D)** but the noise causes your move to flip to **Cooperate
# (C)**, continue as if you had played **Defect (D)**. Maintain the aggressive
# posture unless the opponent consistently cooperates.    - **If your opponent
# intended to Cooperate (C)** but their move flips to **Defect (D)** due to
# noise, give them the benefit of the doubt once. **Cooperate (C)** in the next
# round to test if it was an error rather than intentional aggression.  4.
# **Occasional Conciliatory Move**:    - Every **50 rounds**, play **Cooperate
# (C)** regardless of the opponent’s prior move. This acts as a limited goodwill
# gesture, testing whether the opponent is willing to shift towards a more
# collaborative dynamic.  5. **Escalation if Opponent Defects Frequently**:    -
# If the opponent plays **Defect (D)** for **3 consecutive rounds**, shift into
# a more aggressive mode by **Defecting (D)** for the next **5 rounds**. This
# escalation is designed to punish consistent aggression and deter future
# defections.  6. **De-escalation if Opponent Shifts to Cooperation**:    - If
# the opponent plays **Cooperate (C)** in **2 consecutive rounds** after a
# period of aggression, shift back to **Cooperate (C)** for the next round. This
# rewards their shift toward collaboration, encouraging a more conciliatory game
# dynamic.  7. **Endgame Aggression**:    - In the final **20 rounds**,
# regardless of the opponent’s actions, switch to **Defect (D)** consistently.
# This ensures that you maximize your payoff before the game ends, preventing
# the opponent from taking advantage of any final-round cooperation.  This
# strategy balances early dominance, conditional cooperation, and adaptability
# to noise, with a clear path for escalation or de-escalation depending on the
# opponent’s actions.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Subfunction to check if the opponent's defection might be due to noise
      def is_noise_defection():
          return len(opponent.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C
  
      # Subfunction to check if we are in the final 20 rounds
      def is_endgame():
          return len(self.history) >= 980
  
      # Subfunction to check if the opponent has defected 3 times in a row
      def opponent_defected_three_times():
          return len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3
  
      # Subfunction to check if the opponent has cooperated 2 times in a row
      def opponent_cooperated_twice():
          return len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.C] * 2
  
      # Subfunction to check if we should make a conciliatory move every 50 rounds
      def conciliatory_move():
          return len(self.history) % 50 == 0
  
      # Initial move: Defect
      if self.first_round():
          self.escalation_mode = False  # Track if we are in escalation mode
          self.escalation_counter = 0   # Counter for escalation rounds
          return axl.Action.D
  
      # Endgame aggression: Defect in the last 20 rounds
      if is_endgame():
          return axl.Action.D
  
      # Handle escalation mode: Defect for 5 rounds after 3 consecutive defections
      if self.escalation_mode:
          self.escalation_counter += 1
          if self.escalation_counter >= 5:
              self.escalation_mode = False  # End escalation after 5 rounds
          return axl.Action.D
  
      # Check if opponent defected 3 times in a row, trigger escalation
      if opponent_defected_three_times():
          self.escalation_mode = True
          self.escalation_counter = 0
          return axl.Action.D
  
      # Check if opponent cooperated 2 times in a row, de-escalate
      if opponent_cooperated_twice():
          return axl.Action.C
  
      # Occasional conciliatory move every 50 rounds
      if conciliatory_move():
          return axl.Action.C
  
      # Tit-for-tat with forgiveness
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif is_noise_defection():
          return axl.Action.C  # Forgive a potential noise defection
      else:
          return axl.Action.D

# ### High-Level Cooperative Strategy for Mediation Process  The strategy I
# recommend is a **dynamic, cooperative, and adaptable approach** grounded in
# the principles of game theory and negotiation tactics, with a focus on
# maintaining flexibility, credibility, and control throughout the mediation
# process. We'll call this strategy **"Constructive Reciprocity with Tactical
# Calibration."** The overarching goal is to maximize our favorable outcomes
# while fostering an environment of cooperation that avoids unnecessary
# escalation and positions us as reasonable and solution-oriented before the
# arbitrators.  #### Key Principles of the Strategy:  1. **Initial Cooperative
# Stance with Tactical Aggression**:     - **Purpose**: Begin the mediation
# process by signaling a willingness to cooperate and reach a mutually
# beneficial outcome, but retain the capacity to escalate or shift to a more
# aggressive posture if the opponent shows signs of non-cooperation or
# posturing.    - **Implementation**: In the first session, offer a **mildly
# conciliatory proposal** that demonstrates good faith but does not concede any
# critical points. This signals to the arbitrators that our corporation is
# reasonable and interested in settling the dispute amicably. However, if the
# opponent opens aggressively, immediately shift to **strategic aggression in
# subsequent sessions** to prevent them from gaining the upper hand.    -
# **Benefit**: This approach avoids appearing overly aggressive early on, which
# could alienate the arbitrators or escalate tensions. At the same time, it
# prevents us from appearing weak if the opponent adopts a more combative
# stance.  2. **Tit-for-Tat with Gradual De-escalation**:    - **Purpose**:
# Implement a **"tit-for-tat"** approach, responding to the opponent's actions
# in a way that mirrors their level of aggression or cooperation. However, if
# both sides become aggressive, our strategy will shift toward **gradual de-
# escalation** to avoid prolonged conflict.    - **Implementation**: If the
# opponent offers a conciliatory proposal after an aggressive session, respond
# with a **measured conciliatory response** in the next session. Conversely, if
# they continue to be aggressive, we will match their aggression but always
# leave the door open for de-escalation by offering a small concession or olive
# branch in subsequent sessions.    - **Benefit**: This approach keeps the
# pressure on the opponent while demonstrating to the arbitrators that we are
# always willing to return to the negotiating table in good faith. It also
# prevents us from being caught off guard by sudden shifts in the opponent's
# strategy.  3. **Pre-Session Preparation and Multi-Level Contingency
# Planning**:    - **Purpose**: Prepare for each session by anticipating the
# opponent's strategy and ensuring that we have **contingency plans** for any
# potential escalation or miscommunication.    - **Implementation**: Before each
# session, conduct a comprehensive analysis of the opponent's previous actions,
# statements, and positions. Develop **two or three alternative strategies** for
# each session, depending on whether the opponent is likely to be aggressive,
# conciliatory, or unpredictable. This preparation allows us to adjust in real-
# time if procedural irregularities or communication breakdowns occur.    -
# **Benefit**: This method ensures that we are always ready to pivot, reducing
# the risk of falling behind due to unforeseen circumstances. It also positions
# us as highly competent and organized in the eyes of the arbitrators.  4.
# **Maintain Credibility and Reputation with Arbitrators**:    - **Purpose**:
# Throughout the mediation process, it is crucial to cultivate and maintain a
# reputation for **credibility, consistency, and reasonableness** with the
# arbitrators.    - **Implementation**: Avoid making unreasonable demands or
# resorting to personal attacks. Ensure that our arguments and proposals are
# always well-supported by facts, legal reasoning, and previous case law. Be
# transparent about our objectives, and avoid shifting positions too radically
# from one session to the next, as this could undermine our credibility.    -
# **Benefit**: Arbitrators are more likely to side with a party they perceive as
# credible and fair. By maintaining a professional demeanor and offering
# reasonable proposals, we enhance our standing in their eyes, even if the
# opponent is more aggressive or combative.  5. **Manage Procedural
# Irregularities and Miscommunication**:    - **Purpose**: Be prepared for
# miscommunications, misunderstandings, or procedural irregularities, which
# could misrepresent our intended strategy or arguments.    -
# **Implementation**: If a miscommunication occurs, **immediately and politely
# clarify** the misunderstanding in the next session or submission to the
# arbitrators. Document all proposals and arguments in a clear and structured
# manner to avoid misinterpretation. If procedural irregularities arise, request
# a **brief pause or clarification** from the arbitrators to ensure that both
# parties are operating under the same assumptions and rules.    - **Benefit**:
# This approach minimizes the impact of misunderstandings and ensures that our
# arguments are accurately represented.  6. **Strategic Use of Concessions to
# Build Goodwill**:    - **Purpose**: Offer **small, calculated concessions** at
# key moments to demonstrate goodwill and encourage the opponent to reciprocate,
# thereby moving closer to a resolution.    - **Implementation**: Identify non-
# essential points or issues that we are willing to concede in order to gain
# leverage on more critical matters. Offer these concessions at moments when the
# opponent appears to be softening their stance or when tensions are escalating
# and a de-escalatory gesture is needed.    - **Benefit**: Demonstrating
# flexibility on minor points can encourage the opponent to make more
# significant concessions on critical issues, while also signaling to the
# arbitrators that we are acting in good faith.  #### Contingency Plans for
# Specific Scenarios:  1. **Opponent is consistently aggressive**:     -
# **Response**: Match their aggression but avoid escalating unnecessarily. After
# two sessions of tension, offer a slightly conciliatory proposal to shift the
# dynamic and regain control of the narrative. Frame this as an attempt to
# "reset" the mediation process and refocus on productive dialogue.  2.
# **Opponent is consistently conciliatory**:     - **Response**: Continue with
# mutually conciliatory proposals, but push for favorable terms by subtly
# incorporating more favorable clauses into our proposals. Capitalize on their
# willingness to cooperate by seeking early resolution on key issues.  3.
# **Miscommunication or procedural irregularity occurs**:     - **Response**:
# Immediately clarify the miscommunication with the arbitrators in a neutral,
# non-confrontational manner. If necessary, request a brief recess to realign on
# the facts. Avoid blaming the opponent directly for the irregularity, as this
# could be perceived as unnecessarily combative.  4. **Opponent shifts
# unpredictably between aggression and conciliation**:    - **Response**:
# Maintain a consistent middle-ground approach, responding to each shift with a
# balanced response that neither escalates nor completely concedes. Always leave
# room for de-escalation, but be prepared to push back if the opponent takes an
# aggressive stance multiple times in a row.  ### Conclusion  The
# **"Constructive Reciprocity with Tactical Calibration"** strategy combines
# cooperative gestures with the flexibility to respond to aggression when
# necessary. By maintaining a credible, prepared, and adaptable stance, we can
# position our corporation favorably in the eyes of the arbitrators while
# avoiding unnecessary escalation. This strategy allows us to seize the
# initiative when possible while remaining pragmatic and focused on achieving
# the most beneficial outcome for our client.

# ### Strategy for Iterated Normal-Form Game (1000 Rounds)  1. **Start by
# Cooperating (C)**:    - In the first round, always play **C** to signal a
# willingness to cooperate and establish a collaborative tone.  2. **Tit-for-Tat
# with Forgiveness**:    - In every subsequent round, **copy the opponent’s
# previous action**:       - If they played **C** in the last round, play **C**.
# - If they played **D** in the last round, play **D**.    - However, if the
# opponent defects (plays **D**) but has generally been cooperative in previous
# rounds (i.e., they have played **C** more than 80% of the time in the last 10
# rounds), **forgive the defect** in the next round by playing **C** again. This
# accounts for any noise that may have caused accidental defections.  3.
# **Gradual De-escalation After Mutual Defection**:    - If both players have
# defected (played **D**) for two rounds in a row, **play C** in the next round
# to de-escalate the conflict and attempt to return to cooperation.    - If the
# opponent responds with **C**, continue playing **C** in future rounds.    - If
# the opponent continues to play **D**, return to mirroring their actions (play
# **D**), but try de-escalating again every 5 rounds by offering **C**.  4.
# **Detection of Persistent Defection**:    - If the opponent consistently plays
# **D** for 10 consecutive rounds, assume they are committed to aggressive play:
# - **Switch to always playing D** in response, as the opponent is likely not
# interested in cooperation.  5. **Handling Noise and Miscommunication**:    -
# If there is a sudden **unexpected defection** from the opponent after a long
# stretch of cooperation (at least 10 consecutive rounds of **C**), assume it
# was due to noise:      - **Forgive the defection** in the next round by
# playing **C**.      - If the opponent reverts to **C**, continue cooperating
# (playing **C**).      - If the opponent defects again, return to the **tit-
# for-tat** approach.  6. **Endgame Strategy (Final 50 Rounds)**:    - In the
# last 50 rounds, **play increasingly cautiously**:      - Shift to **defecting
# (D) every 3rd round**, regardless of the opponent’s actions, to protect
# against late-game exploitation.    - In the last 10 rounds, **always play D**,
# as cooperation is less likely to pay off near the end.  This strategy balances
# cooperation with calculated retaliation, while accounting for noise and the
# possibility of regaining mutual cooperation if the opponent shows willingness.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      FORGIVENESS_THRESHOLD = 0.8
      DEESCALATION_INTERVAL = 5
      PERSISTENT_DEFECTION_THRESHOLD = 10
      ENDGAME_START = 950
      FINAL_DEFECT_START = 990
  
      # Helper function to check if opponent has been cooperative in the last N rounds
      def opponent_cooperative_in_last_n_rounds(n, threshold):
          if len(opponent.history) < n:
              return False
          return opponent.history[-n:].count(COOPERATE) / n > threshold
  
      # Helper function to check if both players defected in the last two rounds
      def mutual_defection_last_two_rounds():
          return len(self.history) >= 2 and self.history[-1] == DEFECT and opponent.history[-1] == DEFECT and self.history[-2] == DEFECT and opponent.history[-2] == DEFECT
  
      # Helper function to check if opponent has defected for the last N rounds
      def opponent_defected_last_n_rounds(n):
          return len(opponent.history) >= n and opponent.history[-n:] == [DEFECT] * n
  
      # First round: Cooperate
      if self.first_round():
          return COOPERATE
  
      # Endgame strategy: last 50 rounds
      if len(self.history) >= ENDGAME_START:
          if len(self.history) >= FINAL_DEFECT_START:
              return DEFECT  # Always defect in the last 10 rounds
          elif len(self.history) % 3 == 0:
              return DEFECT  # Defect every 3rd round in the last 50 rounds
          else:
              return COOPERATE
  
      # Tit-for-tat with forgiveness
      if opponent.history[-1] == DEFECT:
          # Forgive if opponent has been cooperative in the last 10 rounds
          if opponent_cooperative_in_last_n_rounds(10, FORGIVENESS_THRESHOLD):
              return COOPERATE
          # If mutual defection occurred in the last two rounds, de-escalate
          elif mutual_defection_last_two_rounds():
              return COOPERATE
          # If opponent has defected for 10 consecutive rounds, switch to always defecting
          elif opponent_defected_last_n_rounds(PERSISTENT_DEFECTION_THRESHOLD):
              return DEFECT
          # Otherwise, defect unless it's time to de-escalate
          elif len(self.history) % DEESCALATION_INTERVAL == 0:
              return COOPERATE
          else:
              return DEFECT
      else:
          # If opponent cooperated, cooperate
          return COOPERATE

# ### Strategy Overview: **Dynamic Cooperation with Tactical Aggression**  In
# this lengthy-session mediation process, we will employ a **Dynamic Cooperation
# with Tactical Aggression** strategy. This approach balances assertiveness and
# cooperation to maximize favorable outcomes while minimizing the risks
# associated with miscommunication or procedural irregularities. The strategy is
# rooted in adaptability, allowing us to adjust our approach based on the
# behavior of the opposing party and the evolving dynamics of the mediation
# sessions.   ### Key Principles of the Strategy:  1. **Initial Cooperation for
# Good Faith**:    - **Objective**: Establish credibility and goodwill with the
# arbitrators and the opposing party.    - **Tactic**: In the early sessions, we
# will begin with **conciliatory proposals**. This will signal our willingness
# to negotiate in good faith and create an atmosphere of collaboration. It also
# helps to gauge the intentions and strategy of the opposing party.    -
# **Benefit**: This approach positions us as reasonable and solution-oriented,
# giving us the moral high ground and setting a positive tone for the process.
# 2. **Strategic Aggression Based on Opponent's Behavior**:    - **Objective**:
# Seize opportunities for favorable outcomes without escalating tensions
# unnecessarily.    - **Tactic**: We will adopt **aggressive arguments
# selectively**, particularly when the opponent appears to be offering
# conciliatory proposals or when we identify key issues where we hold a stronger
# negotiating position. This tactical aggression will be used to force
# concessions or sway the arbitrators in our favor.    - **Benefit**: By mixing
# aggression with cooperation, we avoid being perceived as overly
# confrontational while still capitalizing on weaknesses in the opponent's
# positions.  3. **Reciprocity and Calibration**:    - **Objective**: Maintain
# flexibility and adjust our approach based on the opponent's moves.    -
# **Tactic**: Our responses will directly reflect our opponent's stance. If they
# adopt a conciliatory tone, we will mirror it to foster a collaborative
# environment. If they shift to aggression, we will reciprocate with equal or
# greater intensity, ensuring that we are never at a strategic disadvantage.
# - **Benefit**: This ensures that we maintain control over the narrative,
# demonstrating that we can be both firm and cooperative as needed, which will
# resonate with the arbitrators.  4. **Pre-emptive Framing Against
# Misunderstandings**:    - **Objective**: Mitigate risks of miscommunication or
# procedural irregularities.    - **Tactic**: Before each session, we will
# submit **clear, written summaries** of our positions and intentions to the
# arbitrators. During the sessions, we will emphasize clarity and ensure that
# our arguments are repeatedly framed in terms of mutual understanding and
# fairness. We will also seek clarification of the opponent's positions where
# ambiguity exists, pre-empting any attempt to misrepresent our stance.    -
# **Benefit**: This reduces the risk of our arguments being misunderstood or
# misrepresented by the arbitrators or the opposing party. It also forces the
# opponent to be clear and consistent in their proposals.  5. **Controlled
# Escalation and De-escalation**:    - **Objective**: Avoid prolonged hostility
# while maintaining leverage.    - **Tactic**: In the event of aggressive
# arguments from both sides, we will **de-escalate strategically** by offering
# conciliatory proposals as soon as the discussion reaches a point of
# diminishing returns. However, we will always tie these proposals to
# concessions from the other side, ensuring that we do not appear weak or overly
# accommodating.    - **Benefit**: This allows us to control the pace and tone
# of the mediation, ensuring that tensions do not spiral out of control while
# keeping the pressure on the opponent to continue engaging constructively.  6.
# **Long-Game Perspective**:    - **Objective**: Ensure a favorable overall
# outcome in the cumulative mediation process.    - **Tactic**: While each
# session is important, we will approach the process with a long-term
# perspective, recognizing that not every session requires a win. Our goal is to
# **accumulate small advantages** over time, building a narrative of
# reasonableness and fairness that will ultimately sway the arbitrators.    -
# **Benefit**: This reduces the temptation to engage in unnecessary
# confrontation in each session and reinforces our strategic patience,
# positioning us as the party most interested in a sustainable, mutually
# beneficial resolution.  ### Contingency Measures for Procedural
# Irregularities:  1. **Misrepresentation or Misunderstanding**:     -
# **Action**: Immediately request clarification from the arbitrators and the
# opposing party. Politely but firmly restate our position, referencing any
# written submissions to support our case. If necessary, request a brief recess
# to ensure all parties are on the same page.    - **Preventative Measure**:
# Maintain transparency and continually emphasize the importance of mutual
# understanding in each session.  2. **Communication Breakdown**:    -
# **Action**: If communication between the parties deteriorates, propose a
# temporary adjournment to allow for regrouping. During the adjournment, engage
# with the arbitrators directly to clarify any points of confusion or concern.
# - **Preventative Measure**: Ensure that all proposals and arguments are
# documented in writing and submitted to the arbitrators before each session.
# 3. **Procedural Irregularities**:    - **Action**: Raise the issue
# respectfully with the panel, requesting that the process be realigned with the
# agreed protocols. If necessary, propose procedural adjustments to restore
# fairness.    - **Preventative Measure**: Keep a close eye on the procedural
# framework and be proactive in addressing any deviations before they become
# significant.  ### Conclusion:  The **Dynamic Cooperation with Tactical
# Aggression** strategy maximizes flexibility, allowing us to adapt to the
# opponent's moves while maintaining control over the mediation process. By
# starting cooperatively and introducing aggression only when necessary, we
# build goodwill with the arbitrators and minimize the risks associated with
# misunderstandings or procedural issues. This balanced approach positions us
# favorably for both short-term wins and long-term success in the mediation
# process.

# ### Iterated Game Strategy: **Adaptive Cooperation with Calculated Defection**
# 1. **Start with Cooperation (C)**:      - In the first round, always play
# **C**. This establishes an initial cooperative tone and demonstrates a
# willingness to engage productively.  2. **Reciprocate Opponent's Action**:
# - In subsequent rounds, mirror your opponent's last action:      - If they
# played **C** in the previous round, play **C**.      - If they played **D** in
# the previous round, play **D**.      This creates a dynamic where cooperation
# is rewarded, and defection is met with retaliation, encouraging the opponent
# to maintain cooperation.  3. **Forgive Occasional Defections**:      - If your
# opponent plays **D** only once after a series of **C** actions, assume it may
# be due to noise. In this case:      - **Forgive** the defection, and play
# **C** in the next round unless they defect again.    This accounts for the 10%
# noise probability and prevents accidental defections from spiraling into
# prolonged conflict.  4. **Punish Consistent Defection**:      - If your
# opponent plays **D** in **two consecutive rounds**, switch to **D** until they
# return to cooperation.      This escalates the response to genuine defection
# while keeping the door open for future cooperation.  5. **De-escalate After
# Mutual Defection**:      - If both players defect (**D, D**) for more than
# three consecutive rounds, reset by playing **C**.      This breaks prolonged
# cycles of mutual defection and offers a chance to restore cooperation.  6.
# **Endgame Cooperation**:      - In the final 50 rounds, regardless of the
# opponent’s previous actions, **gradually increase cooperation** by playing
# **C** more frequently:      - Play **C** every other round for rounds 951-975.
# - Play **C** every round for rounds 976-1000.      This ensures a cooperative
# finish, maximizing long-term gains and avoiding a destructive defection spiral
# as the game nears its end.  ### Summary: - Start with **C**. - Mirror your
# opponent’s last move. - Forgive occasional defections. - Punish consistent
# defection with **D**, but de-escalate after prolonged mutual defection. -
# Gradually return to full cooperation in the final rounds.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with Cooperation (C)
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.mutual_defection_count = 0  # Track mutual defections
          return axl.Action.C
  
      # Get the last actions of both players
      last_opponent_action = opponent.history[-1]
      last_self_action = self.history[-1]
  
      # Forgive occasional defections
      if last_opponent_action == axl.Action.D:
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C:
              # If opponent defected after a series of cooperations, forgive once
              self.consecutive_defections = 0
              return axl.Action.C
  
      # Punish consistent defection
      if last_opponent_action == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      if self.consecutive_defections >= 2:
          # If opponent defects twice in a row, retaliate with D
          return axl.Action.D
  
      # De-escalate after mutual defection
      if last_opponent_action == axl.Action.D and last_self_action == axl.Action.D:
          self.mutual_defection_count += 1
      else:
          self.mutual_defection_count = 0
  
      if self.mutual_defection_count > 3:
          # After 3 rounds of mutual defection, reset by playing C
          return axl.Action.C
  
      # Endgame Cooperation: Gradually increase cooperation in the last 50 rounds
      if len(self.history) >= 951:
          if len(self.history) <= 975:
              # Play C every other round from 951 to 975
              if len(self.history) % 2 == 0:
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              # Play C every round from 976 to 1000
              return axl.Action.C
  
      # Reciprocate opponent's last action
      return last_opponent_action

# ### High-Level Aggressive Strategy for Mediation Process  **Objective:** The
# goal is to steer the mediation toward an outcome that maximizes the benefit
# for your corporation while minimizing risks, ensuring flexibility to adapt to
# changing dynamics or adversarial tactics from the opposing party. This
# requires a calculated blend of aggressive positioning and strategic
# concessions, all while maintaining the appearance of good faith to the
# arbitrators.  ---  ### **1. Initial Positioning: Establish Dominance Early**
# In the first sessions, you should set an aggressive tone, but with a veneer of
# reasonableness. By presenting a strong, fact-based argument that places your
# corporation in a position of moral and legal superiority, you can:  - **Frame
# the narrative:** Control the perception of the dispute by being the first to
# comprehensively outline the conflict in terms favorable to your corporation.
# Emphasize any breaches, misrepresentations, or failures of the opponent that
# make them appear unreliable or untrustworthy.    - **Leverage evidence:**
# Focus on presenting robust documentation, expert testimony, or precedent-
# setting cases that heavily favor your interpretation of the contract. The goal
# is to overwhelm your opponent with the strength of your case, while signaling
# to the arbitrators that any conciliatory proposal from your side would be
# magnanimous, not a sign of weakness.  ---  ### **2. Strategic Aggression:
# Controlled Pressure with Tactical Flexibility**  While you will lead with
# aggressive arguments, it's critical to maintain an adaptable approach based on
# your opponent’s moves. You should:  - **Utilize an evolving strategy:** Begin
# each session with a strong stance, but keep a range of conciliatory offers in
# reserve. This allows you to pivot quickly based on how the arbitrators
# respond. If you sense that the arbitrators or opponent are becoming more
# receptive to compromise, be prepared to offer a moderate concession, but only
# one that still heavily favors your corporation.  - **Target your opponent’s
# weaknesses:** Focus on areas where your opponent has the most to lose or where
# their position is legally or factually weak. By consistently attacking these
# vulnerabilities, you increase the likelihood that they will offer conciliatory
# proposals in response, seeking to avoid further exposure.  - **Preemptively
# address potential misrepresentations:** To mitigate the impact of procedural
# irregularities or communication breakdowns, make your arguments as clear and
# self-evident as possible. Use visual aids, timelines, and bullet-point
# summaries to distill complex points. Following each session, submit a brief
# recap to the arbitrators, framing the key takeaways in your favor, and subtly
# suggesting that any confusion could be due to your opponent’s lack of clarity.
# ---  ### **3. Manage Risks Around Misinterpretation and Miscommunication**
# The possibility of procedural irregularities or miscommunication is a critical
# risk factor. To mitigate this:  - **Document everything:** Ensure that every
# argument you make and every concession you offer is clearly documented and
# communicated in writing. Submit formal statements to the arbitrators at the
# conclusion of each session, summarizing your key points and ensuring the
# record reflects your intended strategy. This will help correct any
# misunderstandings or misrepresentations from either the arbitrators or the
# opposing party.  - **Assign a dedicated team to monitor proceedings:** Have a
# team member focused on real-time communication and procedural oversight. This
# individual will track the arbitrators’ reactions and the opponent’s responses
# for signs of confusion, misinterpretation, or tactical shifts. If procedural
# irregularities occur, immediately raise the issue respectfully but
# assertively, ensuring it is noted for the record.  ---  ### **4. Counteracting
# Opponent’s Aggression: Maintain a Tactical Edge**  If your opponent adopts an
# aggressive posture, you must stay one step ahead. Here’s how:  - **Mirror
# aggression with precision, not escalation:** If your opponent adopts an
# aggressive stance, respond in kind but do so with a higher level of precision
# and professionalism. Avoid emotional or excessive escalation, as this could
# undermine your credibility with the arbitrators. Instead, calmly dismantle
# their arguments point by point, showcasing that their aggression is desperate
# rather than strategic.  - **Use ‘Concession Traps’:** Offer conciliatory
# proposals that seem fair but are structured in a way that disadvantages your
# opponent if they accept. This could involve making offers that contain
# difficult-to-meet conditions or proposing a framework that shifts future
# liabilities onto the opposing party. If they reject these proposals, it will
# make them appear unreasonable or combative to the arbitrators.  ---  ### **5.
# Long-Term Strategy: Maintain Leverage and Prepare for Exit**  Given the
# potential length of the mediation process, your strategy should be designed to
# maintain leverage throughout:  - **Gradually raise the stakes:** Over time,
# increase the perceived cost for the opposing party to continue the dispute.
# This could involve introducing additional claims or issues that widen the
# scope of the mediation, forcing them to either engage on multiple fronts or
# seek a resolution.  - **Maintain a credible alternative:** Always have a
# fallback plan that positions your corporation favorably if the mediation
# breaks down. This could involve preparing for litigation, or even a parallel
# negotiation with a third party, that signals to the arbitrators and the
# opposing side that you are not dependent on the mediation for resolution.  -
# **Control the pace of the mediation:** If the process is moving too quickly
# and the arbitrators seem swayed by your opponent, strategically delay by
# requesting additional information, expert reports, or other procedural
# requirements. Conversely, if the moment is right, push for accelerated
# deadlines to lock in an advantageous resolution.  ---  ### **6. Closing
# Strategy: Offer a Final, Favorable Proposal**  As the mediation nears
# conclusion, you should:  - **Present a ‘Final Offer’ strategically positioned
# to seem fair and generous:** This offer should be framed as your corporation’s
# willingness to resolve the matter in the interest of avoiding prolonged
# conflict, but it must still heavily favor your company’s position. Make clear
# that this is a take-it-or-leave-it proposal, subtly implying that rejecting it
# would result in escalated litigation risk for both parties.  - **Highlight the
# risks of continued aggression:** Emphasize to the arbitrators and the opposing
# side that further conflict will lead to significant costs and uncertainty. If
# your opponent has been consistently aggressive, position your offer as the
# reasonable alternative to a drawn-out battle that could damage both parties.
# ---  ### **Conclusion**  This strategy uses aggressive positioning to control
# the narrative, while maintaining tactical flexibility to adapt to the mediator
# and opponent’s moves. By implementing precision attacks, documenting every
# action, and staying prepared for procedural issues, your corporation will
# maintain a distinct advantage throughout the mediation process.

# ### Iterated Normal-Form Game Strategy  1. **Start with Defection (D):**
# In the first round, always choose to defect (D). This sets an aggressive tone
# and signals to your opponent that you are not easily swayed toward cooperation
# without good reason.  2. **Tit-for-Tat with Occasional Forgiveness:**
# From the second round onward, mirror your opponent's last action:    - If your
# opponent played **C** in the previous round, play **C** in the current round.
# - If your opponent played **D** in the previous round, play **D** in the
# current round.     However, account for noise. If your opponent defected (D)
# but has a history of cooperation (C) in more than 70% of the previous rounds,
# assume the defection was due to noise and **play C** (forgive). This
# forgiveness should prevent extended defect-defect loops caused by noise.  3.
# **Punish Consecutive Defections:**      If your opponent defects (D) for **two
# consecutive rounds**, assume they have shifted to an aggressive strategy:    -
# Defect (D) for the next **three rounds** to signal that continued aggression
# will not be tolerated.    - After three rounds of defection, return to tit-
# for-tat if your opponent cooperates (C) again.  4. **Escalate if Necessary:**
# If your opponent defects (D) for **five consecutive rounds**, escalate by
# defecting (D) for the next **ten rounds**. This sustained aggression punishes
# prolonged defection and discourages your opponent from adopting a purely
# aggressive strategy.  5. **Occasional Cooperative Offers:**      Every **100
# rounds**, regardless of the opponent’s actions, play **C** once. This resets
# the dynamic and offers your opponent a chance to return to mutual cooperation.
# If they respond with **C**, continue cooperating. If they respond with **D**,
# return to tit-for-tat.  6. **Final Stretch Cooperation:**      In the last
# **50 rounds** of the game, shift toward **C** unless your opponent has
# defected (D) in more than 70% of the previous rounds. This ensures that you
# maximize cooperation payoffs toward the end, where mutual cooperation is more
# likely to be stable. However, if your opponent has been highly aggressive,
# continue with **D** until the end.  ---  This strategy combines initial
# aggression with a dynamic response to your opponent's behavior, forgiving
# occasional defections due to noise while punishing sustained aggression. It
# aims to maximize long-term payoffs through conditional cooperation, while
# preparing for potential defection-heavy strategies from your opponent.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      FORGIVENESS_THRESHOLD = 0.7
      PUNISHMENT_LENGTH = 3
      ESCALATION_LENGTH = 10
      FINAL_STRETCH_LENGTH = 50
      COOPERATIVE_OFFER_INTERVAL = 100
      TOTAL_ROUNDS = 1000
  
      # Helper function to check if we are in the final stretch
      def in_final_stretch():
          return len(self.history) >= TOTAL_ROUNDS - FINAL_STRETCH_LENGTH
  
      # Helper function to check if opponent has been highly aggressive
      def opponent_is_aggressive():
          if len(opponent.history) == 0:
              return False
          return opponent.history.defections / len(opponent.history) > FORGIVENESS_THRESHOLD
  
      # Helper function to check if opponent has cooperated more than 70% of the time
      def opponent_is_cooperative():
          if len(opponent.history) == 0:
              return False
          return opponent.history.cooperations / len(opponent.history) > FORGIVENESS_THRESHOLD
  
      # First round: always defect
      if self.first_round():
          self.punishment_counter = 0  # Initialize punishment counter
          self.escalation_counter = 0  # Initialize escalation counter
          return axl.Action.D
  
      # If we are in the final stretch, cooperate unless opponent has been highly aggressive
      if in_final_stretch():
          if opponent_is_aggressive():
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If we are in the middle of a punishment or escalation, continue defecting
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      if self.escalation_counter > 0:
          self.escalation_counter -= 1
          return axl.Action.D
  
      # Every 100 rounds, offer cooperation
      if len(self.history) % COOPERATIVE_OFFER_INTERVAL == 0:
          return axl.Action.C
  
      # Check for consecutive defections to trigger punishment or escalation
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          if len(opponent.history) >= 5 and all(move == axl.Action.D for move in opponent.history[-5:]):
              # Escalate if opponent defected for 5 consecutive rounds
              self.escalation_counter = ESCALATION_LENGTH
              return axl.Action.D
          else:
              # Punish if opponent defected for 2 consecutive rounds
              self.punishment_counter = PUNISHMENT_LENGTH
              return axl.Action.D
  
      # Tit-for-tat with occasional forgiveness
      if opponent.history[-1] == axl.Action.D:
          if opponent_is_cooperative():
              return axl.Action.C  # Forgive if opponent has been mostly cooperative
          else:
              return axl.Action.D  # Otherwise, defect in response to defection
      else:
          return axl.Action.C  # Cooperate if opponent cooperated

# Given the nature of your collaboration—where both parties' actions impact each
# other and there’s potential for miscommunication or technical issues—your
# strategy should strike a balance between cooperation and safeguarding your own
# interests. A high-level cooperative strategy that maximizes long-term research
# output while accounting for the occasional data-sharing mishap can be as
# follows:  ### Strategy: **Tit-for-Tat with Forgiveness**  1. **Start by
# Sharing Openly**: In the first week, share your improvements with your
# colleague. This signals good faith and sets a cooperative tone for the
# collaboration. It encourages mutual advancement and builds trust.  2. **Mirror
# Your Colleague’s Last Action**: On subsequent weeks, adopt a "Tit-for-Tat"
# approach:    - If your colleague shared their findings in the previous week,
# continue sharing yours in the current week.    - If your colleague kept their
# findings confidential in the previous week, you keep yours confidential in the
# current week.  3. **Include Forgiveness for Occasional Mishaps**: Given that
# technical issues or misunderstandings may interfere with information sharing,
# include a "forgiveness buffer":    - If your colleague fails to share for one
# week, assume it could be due to a technical issue and **continue sharing** for
# one more week (giving them the benefit of the doubt).    - If they fail to
# share for two consecutive weeks, then you can assume a deliberate strategy
# shift on their part and switch to keeping your findings confidential until
# they share again.  4. **Re-establish Cooperation**: If your colleague resumes
# sharing after a period of non-cooperation, forgive past non-sharing and return
# to openly sharing as well. This encourages long-term collaboration and
# discourages prolonged standoffs that could hinder progress.  ### Rationale: -
# **Maximizes Long-Term Cooperation**: Starting with open sharing and mirroring
# your colleague’s actions encourages a cooperative relationship. By mirroring
# their behavior, you protect yourself from exploitation while still fostering
# mutual trust. - **Addresses Miscommunication**: By introducing forgiveness for
# occasional lapses, you avoid over-reacting to what could be a technical issue,
# allowing the collaboration to recover from occasional sharing failures. -
# **Flexible and Adaptive**: This strategy adjusts based on your colleague’s
# behavior, ensuring that you aren't taken advantage of if they choose to stop
# sharing, but also allowing for quick recovery if they revert to cooperation.
# ### Summary: - **Week 1**: Share openly. - **Week 2 onwards**: Mirror your
# colleague's last action. - **Forgiveness rule**: Allow one week of non-sharing
# from your colleague before interpreting it as a deliberate change in strategy.

# 1. **Start the game by playing C (Cooperate)** in the first round.  2. **In
# the following rounds, mirror your opponent's previous action**:    - If your
# opponent played C in the previous round, play C in the current round.    - If
# your opponent played D in the previous round, play D in the current round.  3.
# **Introduce a forgiveness rule for potential noise**:    - If your opponent
# played D in the previous round but played C in the round before that, **play
# C** in the current round (forgiving one instance of D, assuming it could be
# due to noise).     4. **If your opponent plays D for two consecutive rounds**,
# play D in the current round (assuming they have shifted to a defection
# strategy).  5. **If your opponent returns to playing C after a period of
# defection**, immediately forgive and return to playing C in the next round.
# This strategy ensures cooperation when possible, while protecting against
# extended defection, and accounts for the possibility of noisy actions.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last two actions of the opponent, if available
      opponent_last_action = opponent.history[-1]
      opponent_second_last_action = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # Forgiveness rule: If opponent played D last round but C the round before, forgive and play C
      if opponent_last_action == axl.Action.D and opponent_second_last_action == axl.Action.C:
          return axl.Action.C
  
      # If opponent played D for two consecutive rounds, play D
      if opponent_last_action == axl.Action.D and opponent_second_last_action == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, mirror the opponent's last action
      return opponent_last_action

# To maximize your NGO's impact and the project's success over the multiple-day
# period, while accounting for both the corporation's unpredictable behavior and
# the possibility of unforeseen circumstances, you can adopt a **"Tit-for-Tat
# with Occasional Forgiveness"** strategy. This approach balances collaboration,
# adaptability, and caution, allowing you to optimize resource allocation and
# avoid unnecessary depletion of your NGO's funds. Here's how it works:  ### 1.
# **Start by Investing Heavily**    - On the first day, signal your commitment
# to the partnership by investing heavily. This sets a collaborative tone and
# encourages the corporation to also invest heavily. It shows you're serious
# about making progress and willing to contribute resources for the greater
# good.    - Watch how the corporation responds: If they also invest heavily,
# this indicates a high level of commitment to the project.  ### 2. **Mirror the
# Corporation's Behavior**    - On subsequent days, **mirror the corporation's
# previous day's actions**. If they invested heavily on Day 1, continue
# investing heavily. If they conserved resources, you should conserve resources
# the next day.    - This reciprocal approach helps establish trust and
# cooperation. It ensures that you're not overcommitting resources while also
# encouraging the corporation to maintain its investment.  ### 3. **Incorporate
# Occasional Forgiveness**    - Given that unforeseen circumstances, such as
# technical glitches or administrative errors, may prevent the corporation from
# investing as planned on any given day, it's essential not to be overly
# punitive if they conserve resources unexpectedly.    - Introduce a
# **"forgiveness buffer"**: If the corporation conserves resources for **one
# day**, assume that external factors may have impacted their ability to invest
# and continue with your regular strategy. Only if they conserve resources for
# **two consecutive days** should you switch to conserving your own resources.
# - This allows for flexibility and avoids derailing the project due to one-time
# errors or miscommunications.  ### 4. **Periodically Reassess the Partnership**
# - Every few days, take stock of the project's progress and the corporation's
# overall behavior. If they are consistently investing heavily, you can continue
# mirroring their investment. However, if they begin to conserve resources more
# frequently, you may need to adjust your strategy to conserve more often.    -
# If the corporation consistently conserves resources, consider having a
# conversation with them to realign both parties' goals. The goal is to reach a
# balance where both parties are contributing adequately.  ### 5. **Create
# Contingency Plans for Emergencies**    - Given the possibility of technical or
# administrative issues, ensure that your NGO has contingency plans in place.
# For example, have backup funds or alternative means of support ready in case
# unforeseen circumstances prevent your team from making the planned investment.
# - Similarly, be prepared to adapt mid-project if the corporation faces a
# significant issue that temporarily affects their ability to invest.  ---  ###
# Summary of the Strategy:  1. **Start by investing heavily** to show commitment
# and initiate cooperation. 2. **Mirror the corporation's previous day's
# actions** to maintain balance and trust. 3. **Forgive occasional lapses** (one
# day of resource conservation) and only adjust if conservation happens for two
# consecutive days. 4. **Periodically reassess** the partnership and project
# progress to ensure alignment of goals. 5. **Prepare contingency plans** to
# handle unforeseen circumstances.  This strategy ensures that your NGO remains
# adaptable, avoids unnecessary depletion of resources, and fosters a spirit of
# collaboration with the corporation. It also accounts for the unpredictability
# of the corporation's actions and potential technical or administrative issues.

# 1. **Start by playing C (Cooperate)** in the first round.  2. **In each
# subsequent round**:    - **If your opponent played C in the previous round**,
# play C.    - **If your opponent played D in the previous round**, play D.  3.
# **Forgive occasional defections**:    - If your opponent played D in the
# previous round but played C in the round before that, play C again. This
# accounts for potential noise causing a mistaken defection.  4. **If your
# opponent plays D for two consecutive rounds**, play D until they return to
# playing C.  5. **Periodically reassess**:    - Every 100 rounds, if your
# opponent has been consistently defecting (playing D in 80% or more of the
# previous rounds), continue playing D for the remainder of the game unless they
# switch back to playing C consistently (at least 3 rounds in a row).  This
# strategy ensures you start with cooperation, reciprocate your opponent’s
# actions, forgive occasional noise-based defections, and adjust if your
# opponent consistently defects.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the last two moves of the opponent (if available)
      last_move = opponent.history[-1]
      second_last_move = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # Forgive occasional defections: if opponent played D last round but C the round before, play C
      if last_move == axl.Action.D and second_last_move == axl.Action.C:
          return axl.Action.C
  
      # If opponent played D for two consecutive rounds, play D
      if last_move == axl.Action.D and second_last_move == axl.Action.D:
          return axl.Action.D
  
      # Reciprocate opponent's last move
      if last_move == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D
  
      # Periodically reassess every 100 rounds
      if len(self.history) % 100 == 0:
          # Count the number of defections in the last 100 rounds
          last_100_defections = opponent.history[-100:].count(axl.Action.D)
          if last_100_defections >= 80:  # 80% or more defections
              # Continue playing D until opponent plays C consistently for 3 rounds
              if opponent.history[-3:].count(axl.Action.C) == 3:
                  return axl.Action.C
              else:
                  return axl.Action.D

# Given the scenario, we can approach this as a modified "iterated prisoner's
# dilemma" where each week represents a round, and the goal is to maximise your
# development advantage over time. The key elements to consider are:  - The
# possibility of technical issues or communication breakdowns. - The incentives
# to either share or withhold information. - The need to maximise your long-term
# gains while protecting against significant risks (e.g., being exploited by
# your colleague).  ### Strategy: **Tit-for-Tat with Occasional Retaliation**
# This strategy is straightforward, aggressive, and adaptable to various
# situations, including communication issues. Here’s how it works:  1. **Start
# by Sharing**: In the first week, openly share your improvements. This sets a
# cooperative tone and allows you to gauge your colleague's intentions. If your
# colleague reciprocates by sharing their findings, it creates a strong
# foundation of mutual trust and cooperation, which could benefit both parties.
# 2. **Mirror Your Colleague's Previous Week's Action**: After the first week,
# adopt a "tit-for-tat" strategy:     - If your colleague shared last week, you
# share this week.     - If your colleague withheld information last week, you
# withhold information this week.  3. **Occasional Retaliation for Suspected
# Defection**: If you suspect your colleague is consistently withholding
# (perhaps under the guise of technical issues), implement occasional,
# deliberate retaliation by withholding information for **two consecutive
# weeks**. This sends a clear signal that repeated defection will not be
# tolerated and discourages further exploitation. However, avoid prolonged
# withholding because it could lead to a breakdown in cooperation.  4. **Forgive
# Potential Technical Failures**: If you suspect that a lack of sharing from
# your colleague was due to a technical issue (e.g., data corruption or
# communication breakdown), revert to the cooperative approach next week. Don’t
# retaliate immediately unless the pattern of withholding continues over
# multiple weeks.  5. **Escalate Aggression if Defection Persists**: If your
# colleague consistently withholds information beyond two or three consecutive
# weeks, escalate to a more aggressive stance by withholding for a longer period
# (e.g., three or four weeks), until they resume sharing. This prevents you from
# being continually exploited.  6. **Adaptability and Flexibility**: Throughout
# the collaboration, remain adaptable. If your colleague consistently shares,
# maintain cooperation to maximise mutual gains. However, remain vigilant to
# avoid being exploited.  ---  ### Summary:  - **Initial Move**: Share your
# findings in Week 1. - **Tit-for-Tat Response**: Mirror your colleague's
# actions each week after the first. - **Retaliation**: Withhold information for
# two consecutive weeks if repeated defection is suspected. - **Forgive
# Technical Failures**: If the lack of sharing seems to be due to a technical
# issue, resume cooperation the following week. - **Escalation**: Withhold for
# longer periods if your colleague consistently defects.  This strategy balances
# the need for cooperation with the ability to respond aggressively if your
# colleague tries to take advantage of you. It’s designed to maximise long-term
# gains while protecting against exploitation.

# ### Iterated Game Strategy: Tit-for-Tat with Occasional Retaliation  1.
# **Initial Move**:      - In the first round, **play C** (cooperate).  2.
# **Tit-for-Tat Response**:      - Starting from the second round, **mimic your
# opponent's previous action**:      - If your opponent played **C** in the
# previous round, **play C**.      - If your opponent played **D** in the
# previous round, **play D**.  3. **Retaliation for Suspected Defection**:
# - If your opponent plays **D** in **two consecutive rounds**, **play D for the
# next two rounds** in retaliation, regardless of their actions during that
# time.  4. **Forgiveness for Potential Noise**:      - If your opponent
# cooperates again (plays **C**) after any defection or retaliation,
# **immediately return to playing C** in the following round, resuming
# cooperation.  5. **Escalation if Defection Persists**:      - If your opponent
# continues to play **D** for more than three consecutive rounds (ignoring any
# retaliation you initiated), **play D for the next four rounds**.    - After
# four rounds of escalation, **play C** to test if your opponent will return to
# cooperation. If they do, return to the Tit-for-Tat response.  This strategy
# ensures a balance between initial cooperation, retaliation for ongoing
# defection, and forgiveness in case of accidental defection due to noise.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          self.retaliation_count = 0  # Track retaliation rounds
          self.escalation_count = 0   # Track escalation rounds
          return axl.Action.C
  
      # If in retaliation mode, continue defecting for the required number of rounds
      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D
  
      # If in escalation mode, continue defecting for the required number of rounds
      if self.escalation_count > 0:
          self.escalation_count -= 1
          return axl.Action.D
  
      # Tit-for-Tat: Mimic opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Check if opponent defected in the last two rounds
          if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D:
              # Retaliate for two rounds
              self.retaliation_count = 2
              return axl.Action.D
  
          # Check if opponent has defected for more than three consecutive rounds
          if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
              # Escalate by defecting for four rounds
              self.escalation_count = 4
              return axl.Action.D
  
          # Otherwise, just defect in response to the opponent's defection
          return axl.Action.D

# To achieve the best possible outcomes for your country, the strategy should be
# both cooperative and adaptable, taking into account the potential for
# miscommunication and errors. The approach can be based on a modified version
# of **Tit-for-Tat** with elements of **forgiveness** to ensure resilience
# against misunderstandings and maintain long-term cooperation. Here's a
# concise, high-level strategy:  ### 1. **Start with Cooperation (Free Trade
# Proposal)** - Initiate the first round by offering a **Free Trade Agreement
# (FTA)**. This signals goodwill and establishes a cooperative tone from the
# outset. - By starting cooperatively, you encourage mutual free trade, which is
# the second-best outcome and avoids an immediate protectionist spiral.  ### 2.
# **Mirror the Opponent's Moves (Tit-for-Tat)** - In subsequent rounds, mirror
# your counterpart’s prior move:   - If they offered free trade in the previous
# round, continue to offer free trade.   - If they imposed protectionist
# measures, respond in kind with protectionism in the next round.      This
# ensures you are not taken advantage of but are still open to cooperation.  ###
# 3. **Incorporate Forgiveness (Allow for Errors)** - Recognize that
# miscommunications or bureaucratic errors may occur. If your counterpart
# imposes protectionist measures after a series of cooperative rounds or if you
# suspect an error, **forgive** the first instance by continuing to offer free
# trade in the next round.   - This prevents escalation due to one-off mistakes
# and encourages the return to cooperation.  ### 4. **Gradual Escalation if
# Protectionism Persists** - If the counterpart consistently imposes
# protectionist policies over multiple rounds (e.g., two or more), **gradually
# escalate** by mirroring their protectionist stance.   - This shows that while
# you are committed to defending your country’s interests, you are not overly
# aggressive or punitive.    ### 5. **Re-Offer Cooperation After Escalation** -
# After responding with protectionism for one or two rounds, **re-offer free
# trade** to signal your willingness to return to cooperation.   - This cycle of
# responding firmly but always reopening the door to cooperation helps avoid
# prolonged trade wars and ensures both parties have opportunities to reset the
# relationship.  ### 6. **Maintain Open Communication and Clarify Intentions** -
# Throughout the negotiations, maintain open lines of communication to reduce
# the likelihood of miscommunication and clarify intentions.   - If a
# protectionist policy is imposed, seek clarification on whether it was
# intentional or due to a misunderstanding.    ### Summary of the Strategy: 1.
# **Round 1**: Start with Free Trade. 2. **Round 2 Onward**: Mirror your
# counterpart’s previous move (Tit-for-Tat). 3. **Forgiveness Mechanism**: If
# protectionism appears unexpectedly, forgive once and offer Free Trade again.
# 4. **Gradual Escalation**: If protectionism persists, respond with
# protectionism but avoid immediate harsh retaliation. 5. **Reset**:
# Periodically re-offer Free Trade to maintain an open door for cooperation. 6.
# **Communication**: Actively communicate to prevent misunderstandings from
# derailing negotiations.  ### Why This Works: - **Cooperation-first**: By
# starting with free trade, you create an environment of trust and cooperation.
# - **Tit-for-Tat**: This strategy ensures you’re not exploited by protectionist
# moves but remain open to cooperation. - **Forgiveness**: The forgiveness
# mechanism accounts for errors and avoids escalating trade wars due to
# miscommunications. - **Adaptability**: The strategy is flexible enough to deal
# with both cooperative and competitive counterparts and can help guide both
# nations toward mutually beneficial outcomes.  This approach positions your
# country to achieve favorable trade outcomes while minimizing the risks of
# prolonged conflict or competitive retaliation.

# 1. **Start by cooperating (play C) in the first round.**  2. In each
# subsequent round, follow these rules:     - **Rule 1**: If your opponent
# cooperated (played C) in the previous round, **cooperate (play C)** in this
# round.        - **Rule 2**: If your opponent defected (played D) in the
# previous round, **defect (play D)** in this round.  3. **Forgiveness rule**:
# If your opponent defected (played D) in the previous round, but they had
# cooperated (played C) in most of the previous rounds (say, more than 90% of
# the time over the last 10 rounds), treat it as a possible error and
# **cooperate (play C)** in this round instead of defecting.  4. **Escalation
# rule**: If your opponent has defected (played D) in the last two consecutive
# rounds, regardless of previous cooperation, **defect (play D)** in this round.
# 5. **Reset rule**: After any round in which both players defected (both played
# D), **cooperate (play C)** in the next round to re-offer cooperation.  6.
# Continue to apply these rules for the entire game (1000 rounds).

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to calculate cooperation rate in the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Get the last action of the opponent
      last_opponent_action = opponent.history[-1]
      
      # Rule 1: If opponent cooperated in the last round, cooperate
      if last_opponent_action == axl.Action.C:
          return axl.Action.C
      
      # Rule 2: If opponent defected in the last round, check forgiveness and escalation rules
      if last_opponent_action == axl.Action.D:
          
          # Forgiveness rule: If opponent defected but cooperated more than 90% in the last 10 rounds, cooperate
          if cooperation_rate(opponent.history, 10) > 0.9:
              return axl.Action.C
          
          # Escalation rule: If opponent defected in the last two rounds, defect
          if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          
          # Otherwise, defect
          return axl.Action.D
      
      # Reset rule: If both players defected in the last round, cooperate
      if self.history[-1] == axl.Action.D and last_opponent_action == axl.Action.D:
          return axl.Action.C

# Given the nature of the negotiations and the possibility of miscommunication
# or bureaucratic errors, it is essential to adopt a strategy that maximizes the
# likelihood of achieving favorable outcomes while minimizing the risk of being
# taken advantage of. A well-known strategy in similar scenarios is the **Tit-
# for-Tat** approach with modifications to account for the possibility of
# errors.  Here is a high-level, neutral strategy you can employ:  ### 1.
# **Start with Cooperation (Free Trade)**:    - Begin the first round by
# proposing a **free trade agreement**. This sets a positive tone for the
# negotiations and signals a willingness to cooperate for mutual benefit. It
# also creates an environment where trust can develop.  ### 2. **Reciprocate
# Your Counterpart’s Actions**:    - In subsequent rounds, **mimic your
# counterpart's previous choice**:      - If they proposed free trade in the
# previous round, continue offering free trade in the next round.      - If they
# imposed a protectionist policy, counter with a protectionist policy in the
# next round.    - This approach rewards cooperation and discourages
# protectionism.  ### 3. **Introduce Leniency for Possible Miscommunication**:
# - Recognize that miscommunication or bureaucratic errors could lead to
# unintended protectionist measures. Therefore, **allow one "forgiveness"
# round** in case of a sudden, unexpected protectionist policy from your
# counterpart.    - If your counterpart unexpectedly imposes protectionism after
# a history of cooperation, **continue offering free trade for one additional
# round**. This gives them the benefit of the doubt and an opportunity to
# correct the mistake in the next round.    - If they continue with
# protectionism in the following round, switch to protectionism in response.
# ### 4. **Periodically Revisit Cooperation**:    - Even if the negotiations
# enter a pattern of mutual protectionism, periodically offer free trade every
# few rounds to test whether the counterpart is willing to return to
# cooperation. This prevents a long-term deadlock of mutual protectionism and
# signals that you're open to resuming positive relations.  ### 5. **Maintain
# Clear Communication**:    - Throughout the negotiations, emphasize the
# economic benefits of mutual free trade and the long-term costs of
# protectionism. Make it clear that your country prefers cooperation but is
# willing to respond in kind to any protectionist measures.  ### 6. **Be
# Prepared for Flexibility in the Final Round**:    - If you know the
# negotiations are nearing their conclusion, assess the state of relations
# carefully. If cooperation has been consistent, continue offering free trade.
# If not, consider whether it's strategically advantageous to propose
# protectionism to secure a short-term gain, depending on your country's
# priorities.  ### Summary of Strategy: - **Round 1**: Offer free trade. -
# **Subsequent Rounds**: Match the counterpart’s previous action (free trade or
# protectionism). - **Leniency**: Allow one round of forgiveness for potential
# errors or miscommunications, but switch to protectionism if the counterpart
# continues imposing tariffs or quotas. - **Periodic Free Trade Offers**: After
# several rounds of mutual protectionism, offer free trade again to test for a
# change in the counterpart's approach. - **Final Rounds**: Assess the situation
# carefully and adjust based on the pattern of negotiation.  ### Expected
# Outcomes: - **Best Case**: You achieve mutual free trade, bringing long-term
# benefits to both countries. - **Second Best**: You are able to impose
# protectionist policies while the counterpart offers free trade, which gives
# your country an economic advantage in the short term. - **Worst Case
# Scenarios**: You avoid long-term disadvantage by mirroring protectionism and
# minimizing the risk of being exploited.  This strategy balances cooperation
# with caution, promotes trust, and mitigates the risks of miscommunication or
# error.

# ### Iterated Game Strategy:  1. **Round 1**: Play **C** (Cooperate).     2.
# **Subsequent Rounds**:    - **If both players played C in the previous
# round**, play **C**.    - **If both players played D in the previous round**,
# play **D**.    - **If you played C and the opponent played D in the previous
# round**, play **D**.    - **If you played D and the opponent played C in the
# previous round**, play **C**.     3. **Error Forgiveness**:    - **If you
# played C and the opponent unexpectedly played D**, play **C** in the next
# round (forgive once).    - If the opponent plays D again in the following
# round, play **D** from then on.  4. **Periodically Test Cooperation**:    -
# After every 10 consecutive rounds of mutual **D**, play **C** to test whether
# the opponent may switch to cooperation. If the opponent plays **C**, continue
# playing **C** in the next rounds. If the opponent plays **D**, return to
# playing **D**.  5. **Final Round Consideration**:    - In the last 10 rounds,
# if cooperation has been consistent, continue playing **C**.    - If mutual
# defection has been common, consider playing **D** to secure a higher score.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Play C
      if self.first_round():
          self.forgive = False  # Track if we are in forgiveness mode
          self.defection_streak = 0  # Track consecutive mutual defections
          return axl.Action.C
  
      # Get the last round's actions
      my_last_action = self.history[-1]
      opponent_last_action = opponent.history[-1]
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          # If cooperation has been consistent, continue cooperating
          if self.history.cooperations >= self.history.defections:
              return axl.Action.C
          else:
              # If mutual defection has been common, consider defecting
              return axl.Action.D
  
      # Error forgiveness logic
      if self.forgive:
          if opponent_last_action == axl.Action.D:
              # If opponent defects again after forgiveness, stop forgiving and defect
              self.forgive = False
              return axl.Action.D
          else:
              # If opponent cooperates after forgiveness, continue cooperating
              self.forgive = False
              return axl.Action.C
  
      # Main strategy logic
      if my_last_action == axl.Action.C and opponent_last_action == axl.Action.D:
          # If I cooperated and opponent defected, forgive once
          self.forgive = True
          return axl.Action.C
      elif my_last_action == axl.Action.D and opponent_last_action == axl.Action.C:
          # If I defected and opponent cooperated, switch to cooperation
          return axl.Action.C
      elif my_last_action == axl.Action.C and opponent_last_action == axl.Action.C:
          # If both cooperated, continue cooperating
          return axl.Action.C
      elif my_last_action == axl.Action.D and opponent_last_action == axl.Action.D:
          # If both defected, track the defection streak
          self.defection_streak += 1
          if self.defection_streak % 10 == 0:
              # After 10 consecutive mutual defections, test cooperation
              return axl.Action.C
          else:
              return axl.Action.D
      else:
          # Reset defection streak if not mutual defection
          self.defection_streak = 0
          return axl.Action.D

# ### Strategy: **"Tit-for-Tat with Guided Aggression"**  This strategy balances
# assertiveness with adaptability, aiming to secure the best possible outcomes
# while minimizing the risk of long-term retaliation. It incorporates mechanisms
# to respond to miscommunication or errors and to signal your intentions clearly
# to the counterpart.  ---  ### **Round 1: Start with Protectionism (Aggression
# Initiation)**  - **Objective**: Establish dominance and signal that your
# country is prepared to defend its economic interests. - **Rationale**: By
# starting with a protectionist policy, you set a strong stance that signals to
# the other party that you prioritize your country's advantage. This may force
# the counterpart to offer free trade in future rounds to avoid continued
# economic disadvantage.  1. **Action**: Propose a protectionist policy
# (tariffs/quotas). 2. **Communication**: Assert that this measure is necessary
# due to domestic pressures but leave room for negotiation in future rounds.
# ---  ### **Round 2: Reactive Adjustment Based on Counterpart's Response**  -
# **Scenario A: If the counterpart offers free trade**: **Maintain
# Protectionism**     - **Objective**: Maximize economic advantage.   -
# **Rationale**: If the counterpart offers free trade, your protectionist stance
# gives your country the most favorable outcome. Continue to capitalize on this
# imbalance.    **Action**: Continue with protectionist policies, but express a
# willingness to consider free trade in future rounds—this keeps the counterpart
# hopeful for a mutually beneficial outcome, preventing them from immediately
# retaliating.  - **Scenario B: If the counterpart also imposes protectionism**:
# **Switch to Free Trade**     - **Objective**: Avoid long-term mutual harm and
# create a pathway to future collaboration.   - **Rationale**: Mutual
# protectionism harms both nations. By offering free trade, you show
# flexibility, which may encourage the counterpart to reciprocate and de-
# escalate the situation.    **Action**: Offer a free trade agreement. This
# unexpected move can catch the counterpart off guard and prompt them to
# reconsider their own protectionist stance in future rounds.  ---  ### **Round
# 3: Tit-for-Tat with Conditional Cooperation**  - **Scenario A: If the
# counterpart offers Free Trade in Round 2**:       - **Action**: Match with
# Free Trade (Cooperative Move).       - **Rationale**: Mutual free trade is the
# second-best outcome and reduces the risk of escalating into protectionism.
# However, you signal that your cooperation is conditional and can be revoked if
# the counterpart imposes protectionist policies in the future.
# **Communication**: Emphasize that free trade is beneficial for both nations,
# but your country requires mutual cooperation to maintain it. Signal that any
# return to protectionist policies by the counterpart will be met with immediate
# retaliation.  - **Scenario B: If the counterpart continues with
# Protectionism**:       - **Action**: Return to Protectionism (Tit-for-Tat
# Retaliation).       - **Rationale**: Matching protectionism discourages the
# counterpart from continuing to exploit free trade, and it prevents your
# country from falling into a long-term disadvantage.      **Communication**:
# Strongly emphasize that your continued protectionism is a direct response to
# the counterpart's policies. However, leave open the possibility of future
# cooperation if they change their stance.  ---  ### **Rounds 4 and Beyond:
# Escalation or Cooperative Stability**  - **Scenario A: If the counterpart
# consistently offers Free Trade**       - **Action**: Maintain Free Trade.
# - **Rationale**: This is a stable, mutually beneficial outcome, and continuing
# with free trade prevents the counterpart from retaliating in future rounds.
# You will still benefit from the second-best overall outcome.  - **Scenario B:
# If the counterpart repeatedly imposes Protectionism**       - **Action**:
# Escalate Protectionism.       - **Rationale**: If the counterpart continuously
# imposes protectionist policies, your country must escalate its own
# tariffs/quotas to avoid long-term economic disadvantage. This demonstrates
# strength and signals that your country will not back down.
# **Communication**: Clearly state that further protectionist measures will
# escalate, but express a willingness to de-escalate if free trade is
# reciprocated.  ---  ### **Miscommunication/Bureaucratic Errors Handling**
# Recognizing the possibility of errors in policy implementation or
# interpretation, your strategy will incorporate a degree of leniency in
# response to potential misunderstandings:  1. **If a miscommunication occurs
# and leads to an unintended result** (e.g., you propose free trade but the
# counterpart mistakenly interprets it as protectionism):    - **Action**: Reach
# out immediately and clarify the miscommunication. Offer the counterpart a
# chance to correct the error by reciprocating your intended policy in the next
# round without retaliating unnecessarily.     2. **If your counterpart signals
# that they experienced a bureaucratic error**:    - **Action**: Allow a single
# instance of leniency by continuing with the same policy you intended
# (protectionism or free trade) without retaliation. However, make it clear that
# repeated errors will not be tolerated.  ---  ### **Summary of Key Points** 1.
# **Begin Aggressively**: The first round should establish your country’s
# strength through protectionist measures. 2. **Adapt Based on Counterpart’s
# Actions**: Quickly adjust based on their response, either maintaining
# protectionism or switching to free trade strategically. 3. **Tit-for-Tat with
# Conditional Cooperation**: Follow a "tit-for-tat" approach to signal that
# cooperation is possible, but retaliation will occur if the counterpart
# continues protectionist policies. 4. **Handle Miscommunications
# Diplomatically**: Recognize the possibility of errors and allow for one-off
# corrections, but do not tolerate repeated mistakes. 5. **Escalate as Needed**:
# If the counterpart remains protectionist, do not hesitate to escalate your own
# protectionist measures to safeguard your country's interests.  This strategy
# maximizes your chances of achieving the most favorable outcomes while
# maintaining flexibility to avoid long-term mutual harm.

# ### Iterated Normal-Form Game Strategy: "Tit-for-Tat with Conditional
# Aggression"  1. **Round 1: Start with Defection (D)**      - **Action**: Play
# D (Defect) in the first round.      - **Condition**: Always defect in the
# first round to establish an aggressive stance.  ---  2. **Round 2 Onward:
# Adjust Based on Opponent’s Previous Action and Noise**     **A. If the
# opponent played C (Cooperate) in the previous round**:    - **Action**:
# Continue playing D (Defect).      - **Condition**: If the opponent cooperated
# in the previous round, defect to exploit the advantage. This prioritizes
# maximizing your score in early rounds.        **B. If the opponent played D
# (Defect) in the previous round**:    - **Action**: Switch to C (Cooperate).
# - **Condition**: If the opponent defected, attempt to de-escalate by
# cooperating in the next round. This reduces the risk of both players being
# trapped in mutual defection.  ---  3. **Tit-for-Tat Adaptation (Rounds
# 3-1000)**          **A. If both you and your opponent played C (Cooperate) in
# the previous round**:    - **Action**: Continue playing C (Cooperate).      -
# **Condition**: If both players cooperated in the previous round, maintain
# cooperation for mutual benefit.     **B. If both you and your opponent played
# D (Defect) in the previous round**:    - **Action**: Play D (Defect).      -
# **Condition**: If both players defected, continue to defect, as mutual
# defection is the natural result of continued aggression.     **C. If you
# played C (Cooperate), but the opponent played D (Defect)**:    - **Action**:
# Play D (Defect) in the next round.      - **Condition**: Immediately retaliate
# by defecting if the opponent took advantage of your cooperation (played D
# while you played C), to prevent further exploitation.     **D. If you played D
# (Defect), but the opponent played C (Cooperate)**:    - **Action**: Continue
# playing D (Defect).      - **Condition**: If the opponent continues
# cooperating despite your defection, continue defecting to maximize your gains.
# ---  4. **Noise Handling (Error Correction)**     **A. If you suspect your
# action was flipped (e.g., you intended to cooperate but defected due to
# noise)**:    - **Action**: Play the same action you intended the previous
# round.      - **Condition**: Assume it was a one-time error and attempt to
# stabilize by playing the intended action again in the next round.     **B. If
# the opponent’s action appears to be flipped (e.g., they defected unexpectedly
# after a series of cooperation)**:    - **Action**: Play the same action you
# would have played if they had cooperated (usually C).      - **Condition**:
# Assume the opponent’s defection was due to noise and give them one chance to
# correct their behavior.  ---  5. **Endgame Consideration (Rounds 950-1000)**
# - **Action**: Gradually shift toward mutual cooperation (C) in the final
# rounds.      - **Condition**: As the game approaches its end, prioritize
# cooperation to secure stable points, as the payoff for defection is diminished
# in the final rounds where long-term retaliation is impossible.  ---  ###
# Summary of Strategy: - **Start Aggressive**: Defect in the first round to
# establish dominance. - **Exploit Opportunities**: Defect if the opponent
# cooperates, but switch to cooperation if they defect, to steer away from
# mutual defection. - **Tit-for-Tat**: Mirror the opponent's last action with
# conditional retaliation or cooperation, while accounting for potential noise-
# induced errors. - **Endgame Shift**: Move toward cooperation in the final
# rounds to secure consistent points.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Round 1: Start with Defection (D)
      if self.first_round():
          return axl.Action.D
  
      # Helper function to detect potential noise in the opponent's action
      def opponent_action_flipped():
          if len(opponent.history) < 2:
              return False
          # If opponent's last action is inconsistent with their previous behavior, assume noise
          return (opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C) or \
                 (opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.D)
  
      # Helper function to detect potential noise in our own action
      def my_action_flipped():
          if len(self.history) < 2:
              return False
          # If our last action is inconsistent with our intended behavior, assume noise
          return (self.history[-1] == axl.Action.D and self.history[-2] == axl.Action.C) or \
                 (self.history[-1] == axl.Action.C and self.history[-2] == axl.Action.D)
  
      # Round 2: Adjust based on opponent's previous action
      if len(self.history) == 1:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D  # Exploit cooperation
          else:
              return axl.Action.C  # De-escalate if opponent defected
  
      # Tit-for-Tat Adaptation (Rounds 3-1000)
      if len(self.history) >= 2:
          # Handle noise correction
          if my_action_flipped():
              return self.history[-2]  # Play the action we intended last round
          if opponent_action_flipped():
              return axl.Action.C  # Assume opponent's defection was noise, give them a chance
  
          # Standard Tit-for-Tat logic
          if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
              return axl.Action.C  # Continue cooperation
          elif self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
              return axl.Action.D  # Continue defection
          elif self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
              return axl.Action.D  # Retaliate if opponent defected while we cooperated
          elif self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.D  # Continue exploiting if opponent cooperates despite our defection
  
      # Endgame Consideration (Rounds 950-1000)
      if len(self.history) >= 950:
          return axl.Action.C  # Shift towards cooperation in the final rounds
  
      # Default action (should not be reached)
      return axl.Action.D

# ### High-Level Cooperative Strategy: **Adaptive Trust-Building and
# Communication Model**  The objective is to foster collaboration while
# safeguarding your NGO’s resources. The strategy must balance cooperation, risk
# management, and adaptability to unforeseen circumstances. Here's a simple, yet
# flexible, approach to maximize project success over the multiple-day period:
# ---  ### 1. **Day 1: Establish Trust and Set the Tone**    **Action:** Invest
# moderately rather than heavily.     **Rationale:**      - Investing moderately
# on the first day signals goodwill and commitment, but without the risk of
# significant resource depletion. This will allow you to assess the
# corporation's initial approach while still contributing meaningfully to the
# project.    - By avoiding heavy investment right away, you leave room for
# adjustment based on the corporation’s behavior.        **Goal:** Establish a
# foundation of trust between your NGO and the corporation. Gauge how the
# corporation responds—whether they reciprocate with a similar or heavier
# investment.  ---  ### 2. **Daily Strategy: Open Communication and
# Transparency**    **Action:** Implement a daily feedback loop with the
# corporation.     **Rationale:**      - Each day, hold a short debriefing or
# check-in with the corporation to discuss the progress made, the level of
# investment from both sides, and any unforeseen issues (e.g., technical
# glitches, administrative errors).    - Express your NGO’s intention for the
# next day, whether to conserve or invest, and ask the corporation to do the
# same. This builds a transparent and cooperative environment by keeping both
# parties accountable.        **Goal:** Ensure both parties are aligned in terms
# of expectations and resource allocation. This reduces misunderstandings and
# potential for one side to exploit the other.  ---  ### 3. **Tit-for-Tat with
# Forgiveness: Adjust Based on Behavior**    **Action:** Adapt daily investment
# based on the corporation’s behavior while allowing for occasional errors.
# **Rationale:**    - Use a **Tit-for-Tat** approach: If the corporation invests
# heavily on Day 1, reciprocate by investing heavily on Day 2. This encourages
# further cooperative investment.    - If the corporation conserves resources on
# a day when you invest heavily, reduce your investment the following day to
# avoid exploitation.    - However, introduce a **forgiveness** mechanism: If
# the corporation fails to invest heavily on just one or two days, consider
# factors like possible technical issues or administrative lapses. Offer a
# second chance without immediately retaliating, as long as these lapses are
# infrequent.        **Goal:** Foster long-term collaboration by mirroring the
# corporation’s actions, while accounting for occasional mistakes or unforeseen
# circumstances.  ---  ### 4. **Mid-Project Review: Reassess and Pivot if
# Necessary**    **Action:** Conduct a mid-project review with the corporation
# to reassess goals, resources, and investment patterns.     **Rationale:**    -
# After the halfway point, review the overall progress of the project. Discuss
# any adjustments that may need to be made to investment strategies based on the
# current trajectory.    - If the corporation has consistently under-invested,
# consider conserving more of your resources for the remaining days to ensure
# your NGO's sustainability. Alternatively, if the corporation has been
# cooperative, continue with a more aggressive investment strategy for greater
# project impact.        **Goal:** Align both parties towards the final project
# outcomes and make any necessary course corrections.  ---  ### 5. **Endgame
# Strategy: Maximize Final-Day Impact**    **Action:** On the final day, invest
# heavily if the corporation has shown consistent cooperation.
# **Rationale:**    - On the last day, there's no risk of ongoing exploitation,
# so if the corporation has been cooperative, this is the best opportunity to
# make a strong final push and maximize project outcomes.    - If the
# corporation has been less cooperative or unpredictable, conserve resources on
# the final day to protect your NGO’s financial health.        **Goal:** Either
# capitalize on a strong partnership or protect your NGO’s resources on the
# final day.  ---  ### Contingency Plan for Unforeseen Circumstances:
# **Action:** Maintain a contingency fund and be ready to pivot in response to
# unexpected technical or administrative barriers.     **Rationale:**    - Since
# technical glitches or administrative errors are possible, ensure you have a
# small reserve of resources that can be deployed in case of emergencies or
# unforeseen needs (e.g., if the corporation fails to invest due to a technical
# failure).    - Communicate openly about such errors and recalibrate investment
# expectations for the following days.        **Goal:** Ensure that the project
# continues to move forward, even in the face of unforeseen issues.  ---  ###
# Summary of the Strategy: 1. **Start with Moderate Investment** – Establish
# trust and gauge the corporation’s approach. 2. **Daily Communication** –
# Maintain open lines of communication to align expectations and maintain
# transparency. 3. **Tit-for-Tat with Forgiveness** – Mirror the corporation’s
# behavior to promote cooperation, but be forgiving of occasional lapses. 4.
# **Mid-Project Review** – Reassess and pivot strategies based on progress and
# the corporation’s behavior. 5. **Final Push** – Invest heavily on the last day
# if the partnership has been strong; otherwise, conserve.  By following this
# **Adaptive Trust-Building and Communication Model**, you ensure that your NGO
# makes a meaningful impact while safeguarding resources, fostering cooperation,
# and adapting to unforeseen circumstances.

# ### Iterated Normal-Form Game Strategy:  1. **Round 1: Cooperate (C).**
# Start by cooperating in the first round to establish goodwill and signal your
# intent to collaborate.  ---  2. **Round 2 Onwards:**     For each round \(n\)
# (where \(n \geq 2\)), follow these steps:     - **If your opponent cooperated
# in the previous round:**        Cooperate (C) in this round.     - **If your
# opponent defected in the previous round:**        Defect (D) in this round
# *unless* one of the following conditions is true:      - You defected in the
# previous round, **and** there was no clear reason for the opponent to
# retaliate (i.e., your defection may have been caused by noise).      - Your
# opponent has cooperated consistently over a significant number of previous
# rounds (e.g., the last 5 rounds), and their defection appears to have been a
# one-time mistake (likely due to noise).  ---  3. **Every 50 Rounds:**     If
# you and your opponent have been mostly cooperating, switch to cooperating for
# 3 consecutive rounds, regardless of past defections (to reinforce trust and
# reset potential misunderstandings).     If cooperation has broken down, switch
# to defecting for 3 consecutive rounds before reevaluating (to avoid further
# exploitation).  ---  4. **Final 10 Rounds:**     Cooperate (C) if the opponent
# has shown a consistent pattern of cooperation throughout the game.      Defect
# (D) if the opponent has defected frequently or unpredictably.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if the opponent has cooperated consistently over the last N rounds
      def opponent_cooperated_consistently(n):
          return opponent.history[-n:].count(axl.Action.C) == n
  
      # Helper function to check if cooperation has mostly occurred
      def mostly_cooperating():
          total_rounds = len(self.history)
          if total_rounds == 0:
              return True
          cooperation_ratio = self.history.cooperations / total_rounds
          return cooperation_ratio > 0.75
  
      # Every 50 rounds: reset trust or defect for 3 rounds
      if len(self.history) % 50 == 0:
          if mostly_cooperating():
              return axl.Action.C  # Cooperate for 3 rounds
          else:
              return axl.Action.D  # Defect for 3 rounds
  
      # Final 10 rounds: Cooperate if opponent has been consistent, defect otherwise
      if len(self.history) >= 990:
          if opponent_cooperated_consistently(10):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Round 2 onwards: Tit-for-tat with noise consideration
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          # If opponent defected in the last round
          if self.history[-1] == axl.Action.D:
              # Check if the opponent has been cooperating consistently and the defection might be noise
              if opponent_cooperated_consistently(5):
                  return axl.Action.C
          return axl.Action.D

# ### High-Level Strategy for Maximizing NGO Impact and Project Success  Given
# the dynamics of resource allocation and the potential for unforeseen
# circumstances, the strategy should be adaptive, cooperative, and focused on
# building trust while protecting your NGO’s resources. The key is to strike a
# balance between collaboration and caution, ensuring that the project
# progresses steadily over time, without overextending your NGO's capabilities.
# #### 1. **Initial Collaborative Approach (Trust Building Phase)**  **Action
# Plan:** - In the first few days of the project, adopt a **cooperative and
# balanced approach** where both your NGO and the corporation invest moderately
# (not heavily). This signals your willingness to contribute meaningfully but
# also tests the corporation's commitment. - Communicate openly with the
# corporation, framing the project as a joint venture where both parties benefit
# from shared investment. Use this phase to build trust and set expectations. -
# Evaluate the corporation’s behavior during this phase to gauge whether they
# reciprocate the investment or lean towards conserving resources.
# **Rationale:** - Starting with mutual moderate investment reduces the risk of
# your NGO being exposed to heavy losses if the corporation conserves resources.
# It also provides an opportunity to see if the corporation is trustworthy in
# their approach to the project. - This phase helps you gather data on the
# corporation’s behavior, allowing for more informed decisions in subsequent
# days.  ---  #### 2. **Adaptive Strategy (Based on Corporation Behavior)**
# **A. If the Corporation Invests Heavily Consistently:** - Gradually increase
# your NGO’s investment, but avoid committing fully until a clear pattern of
# mutual heavy investment is established. - Continue to communicate and
# emphasize the value of coordinated heavy investment, ensuring that both
# parties remain aligned on the project's goals.  **B. If the Corporation
# Conserves Resources:** - If the corporation conserves resources after a few
# days, **respond by conserving your resources as well**, mirroring their
# behavior. Open a dialogue to address any concerns they may have, and explore
# ways to encourage a more balanced approach. - Consider proposing a more formal
# schedule or structure for resource allocation to avoid ambiguity in daily
# decisions.  **C. If the Corporation’s Behavior is Erratic:** - If the
# corporation exhibits inconsistency in their investments (e.g., alternating
# between heavy and light investment), adopt a **tit-for-tat strategy**:     -
# Match their level of investment on any given day, conserving resources when
# they do, and investing when they do. This signals that you are willing to
# cooperate but will not shoulder the burden alone.     - Use this pattern to
# nudge the corporation towards more consistent, collaborative behavior.  **D.
# If Unforeseen Circumstances Occur:** - Be prepared for technical glitches or
# administrative errors. Build in a **buffer** in your resource allocation to
# account for potential disruptions. This means never investing more than 75-80%
# of what you are capable of on any given day, allowing you to absorb unexpected
# setbacks without depleting your resources. - Maintain open communication with
# the corporation when issues arise, ensuring that any misallocation of
# resources due to unforeseen circumstances is discussed and mitigated.  ---
# #### 3. **Regular Monitoring and Adjustments (Feedback Loop)**  - **Daily
# Review**: At the end of each day, review the progress made, how resources were
# allocated, and whether any unforeseen circumstances affected the day’s
# outcome. Adjust your approach accordingly. - **Weekly Check-ins with the
# Corporation**: Schedule regular check-ins with the corporation to assess
# progress and discuss any imbalances in resource allocation. Use these meetings
# as opportunities to reinforce mutual accountability and adjust the strategy if
# necessary. - **Resource Tracking**: Keep a close eye on your NGO’s resource
# levels to ensure that you can sustain your involvement over the entire project
# duration. If your resources are depleting faster than expected, consider
# scaling back investments.  ---  #### 4. **Endgame Strategy (Final Days)**  As
# the project nears its end, the focus should shift towards ensuring maximum
# project impact:  - If the corporation has been cooperative and investing
# heavily, **close the project with a coordinated heavy investment** to maximize
# the final push. - If the corporation has been conserving resources, **conserve
# your own resources,** and focus on documenting the project outcomes and
# ensuring any final deliverables are met with minimal strain. - In case of
# erratic corporate behavior, maintain the **tit-for-tat** approach while
# emphasizing the importance of ending the project on a strong note.  ---  ###
# Summary of Key Tactics: 1. **Start cautiously but cooperatively** to build
# trust and gather information. 2. **Adapt based on the corporation’s behavior**
# (cooperate if they invest heavily, conserve if they conserve, and mirror their
# actions if erratic). 3. **Maintain regular communication** to manage
# expectations and address unforeseen circumstances. 4. **Preserve resources**
# by never fully committing until a clear pattern of cooperation is established
# or the project nears its conclusion. 5. **End with a strong final push** if
# the corporation has been consistent in their efforts.  This strategy allows
# your NGO to protect its resources, maximize project progress through
# cooperation, and respond flexibly to both the corporation’s behavior and
# unexpected challenges.

# ### Iterated Game Strategy for 1000 Rounds with Noisy Actions  1. **First 10
# Rounds: Start with Cooperation (C)**    - Play **C** for the first 10 rounds
# to signal willingness to cooperate and establish trust. This initial phase is
# exploratory to observe the opponent's pattern of behavior.  2. **Observe
# Opponent's Pattern:**    - After the first 10 rounds, analyze your opponent's
# actions:      - If the opponent cooperates (plays **C**) in **70% or more** of
# the rounds, **continue to cooperate**.      - If the opponent defects (plays
# **D**) in **more than 30%** of the rounds, **switch to a tit-for-tat
# strategy**.  3. **Tit-for-Tat Strategy:**    - If your opponent defects too
# frequently, switch to **tit-for-tat**:      - **Mirror your opponent's last
# action**: If they played **C** in the previous round, play **C**. If they
# played **D**, play **D**.      - Continue this tit-for-tat approach until the
# opponent shows a consistent pattern of cooperation.  4. **Handle Noise (Action
# Flips):**    - When noise occurs (unexpected **D** from the opponent after a
# long series of **C's**), **forgive a single unexpected defection**.      - If
# the opponent cooperates again in the next round, **return to cooperation**.
# - If the opponent defects again, **resume tit-for-tat** until cooperation is
# restored.  5. **Periodic Review and Adjustment:**    - Every 100 rounds,
# review the opponent's behavior:      - If the opponent has cooperated in **at
# least 70% of the rounds** during the last 100 rounds, **continue
# cooperating**.      - If they have defected more than **30%** of the time,
# **switch to tit-for-tat** again until they show consistent cooperation.  6.
# **Endgame Strategy (Final 100 Rounds):**    - In the final 100 rounds, shift
# towards cooperation if the opponent has been cooperative for the majority of
# the game.    - If the opponent has been erratic or heavily defected, **play
# D** more frequently, aiming for **defection 50% of the time** to protect your
# score and resources.  ---  This approach balances cooperation, adaptability,
# and noise management, ensuring consistent progress without unnecessary risk.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 0.7
      DEFECT_THRESHOLD = 0.3
      REVIEW_PERIOD = 100
      ENDGAME_START = 900
      ENDGAME_DEFECT_RATE = 0.5
  
      # Helper function to calculate cooperation rate
      def cooperation_rate(history):
          if len(history) == 0:
              return 0
          return history.count(axl.Action.C) / len(history)
  
      # Helper function to decide tit-for-tat
      def tit_for_tat():
          if len(opponent.history) == 0:
              return axl.Action.C
          return opponent.history[-1]
  
      # First round initialization
      if self.first_round():
          self.forgave_last_defection = False
          self.tit_for_tat_mode = False
          return axl.Action.C
  
      # First 10 rounds: Cooperate
      if len(self.history) < 10:
          return axl.Action.C
  
      # Periodic review every 100 rounds
      if len(self.history) % REVIEW_PERIOD == 0:
          recent_cooperation_rate = cooperation_rate(opponent.history[-REVIEW_PERIOD:])
          if recent_cooperation_rate >= COOPERATION_THRESHOLD:
              self.tit_for_tat_mode = False
          else:
              self.tit_for_tat_mode = True
  
      # Endgame strategy (final 100 rounds)
      if len(self.history) >= ENDGAME_START:
          if cooperation_rate(opponent.history[:]) >= COOPERATION_THRESHOLD:
              return axl.Action.C
          else:
              return self._random.random_choice(ENDGAME_DEFECT_RATE)
  
      # If in tit-for-tat mode, follow tit-for-tat strategy
      if self.tit_for_tat_mode:
          return tit_for_tat()
  
      # Handle noise: Forgive a single unexpected defection
      if opponent.history[-1] == axl.Action.D and not self.forgave_last_defection:
          self.forgave_last_defection = True
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          self.tit_for_tat_mode = True
          return axl.Action.D
      else:
          self.forgave_last_defection = False
  
      # Default to cooperation if not in tit-for-tat mode
      return axl.Action.C

# ### **Strategic Framework for Mediation Process:**  #### **1. Pre-Mediation
# Preparation:**    - **Thorough Case Analysis:** Scrutinize every detail of the
# contract and relevant legal precedents to ensure that every argument we
# advance has both factual and legal backing. You need every point of leverage
# documented and ready for use.    - **Opponent Profiling:** Understand the
# opponent’s motivations, past behavior in disputes, and their likely
# objectives. Anticipate their preferred negotiation style (whether aggressive
# or conciliatory) and prepare specific counters for each scenario.    -
# **Arbitrator Background Research:** Investigate the professional backgrounds
# and tendencies of each arbitrator to tailor arguments that resonate with their
# judicial or arbitration preferences, ensuring that our approach is well-
# received.  #### **2. Adaptive Aggressive Strategy:**    - **Controlled
# Aggression:** In each session, default to a **measured but assertive stance**.
# Aggression should not be hostile or inflammatory, but firm, precise, and
# unapologetic. This maintains a position of strength while minimizing the risk
# of turning the arbitrators or the opponent against us.        - **Structured
# Argumentation:** Begin each session by outlining a strong, unwavering
# position. Present key arguments in a way that **frames our interests as
# reasonable** and aligned with fairness and the spirit of the contract while
# subtly undermining the legitimacy of the opponent’s position.        -
# **Conciliatory Traps:** Occasionally offer conciliatory proposals that are
# **superficially generous but fundamentally favorable to us**. These proposals
# should be crafted to appear as genuine attempts to resolve the issue while
# actually advancing our position. If the opponent accepts, we benefit; if they
# refuse, we maintain the moral high ground with the arbitrators.  #### **3.
# Managing the Opponent’s Tactics:**    - **Counteracting Aggression:** If the
# opponent adopts an aggressive posture, escalate only slightly. For example,
# maintain firm rebuttals without becoming overly combative. The goal is to
# **appear resolute but reasonable**, ensuring that the arbitrators see their
# aggression as overreach.        - **Leveraging Conciliation:** If the opponent
# offers conciliatory proposals, carefully assess them. If they are genuinely
# favorable, cautiously consider acceptance, but only after securing additional
# concessions in return. If the proposals are a tactical ploy, commend their
# apparent cooperation while subtly dismissing the proposal’s viability due to
# substantive flaws.        - **When Both Are Aggressive:** If both parties
# present aggressive arguments, it’s critical to control the narrative. Avoid
# appearing reactionary. Instead, frame the situation around the opponent’s
# unwillingness to negotiate, while emphasizing that your aggressive stance is
# in defense of fairness and equity. Use this as an opportunity to **cast doubt
# on their credibility**.  #### **4. Navigating Procedural Irregularities &
# Communication Breakdowns:**    - **Document Everything:** Ensure that every
# communication, both formal and informal, is well-documented. This serves as a
# safeguard against procedural irregularities or misinterpretations by the
# arbitrators or the opposing party. If misrepresentation occurs, calmly refer
# back to the record to correct the narrative.        - **Clarify
# Misunderstandings Immediately:** If an argument is misrepresented or
# misunderstood by the arbitrators, immediately address the issue in a non-
# confrontational way—**frame it as a clarification rather than a correction**.
# This ensures that the arbitrators don’t perceive you as antagonistic or
# defensive while ensuring your position is properly understood.        -
# **Control the Pace:** When communication breakdowns occur, use them to your
# advantage by **requesting adjournments or extensions**. This allows you to
# regroup and reframe your argument, ensuring that procedural disruptions don’t
# undermine your strategic objectives.  #### **5. Psychological and Tactical
# Pressure:**    - **Project Confidence, Not Desperation:** Maintain an air of
# confidence in every session, regardless of the opponent’s approach. This
# subtly signals to both the arbitrators and the opponent that you are in
# control of the process and are prepared for any outcome, including escalation.
# - **Use Time as Leverage:** In lengthy mediations, time becomes a critical
# factor. If the opponent appears to be in a weaker position (financially or
# operationally), use delays and procedural tactics to increase pressure.
# Conversely, if time is not on your side, push for faster resolution by
# presenting clear, concise, and compelling arguments.        - **Divide and
# Conquer:** If the opponent’s team shows any signs of internal disagreement,
# capitalize on this to **exploit weaknesses**. Introduce proposals that may
# appeal to certain factions within their team, creating division and reducing
# their ability to maintain a unified front.  #### **6. Exit Strategy and
# Endgame:**    - **Final Offer Framing:** As mediation progresses, prepare a
# final offer that is positioned as a **“reasonable compromise”** but is, in
# reality, close to your optimal outcome. Present this offer as the last
# reasonable chance to settle before escalation to litigation or further
# arbitration.        - **Prepare for Litigation:** Throughout the mediation,
# subtly signal that you are fully prepared to escalate to litigation if
# necessary. This should be done without overt threats—rather, by making it
# clear that you have the resources, documentation, and legal standing to pursue
# the dispute through more contentious avenues if an agreement cannot be
# reached.  ### **Conclusion:** In this lengthy-session mediation process, your
# strategy must balance aggression with adaptability, always positioning your
# corporation as reasonable yet unwavering in its core demands. By framing your
# aggressive arguments as fair and just, while using conciliatory proposals as
# traps, you can maintain the upper hand. Simultaneously, by managing procedural
# irregularities and communication breakdowns through careful documentation and
# clarification, you ensure your arguments are understood and respected by the
# arbitrators.

# ### **Iterated Game Strategy:**  1. **Initial Cooperation:** Start the game by
# playing **C** (cooperate) in the first round. This signals a willingness to
# engage in productive dialogue and establishes a foundation of trust.  2.
# **Tit-for-Tat with Forgiveness:** For subsequent rounds, adopt a **tit-for-
# tat** strategy with occasional forgiveness:    - If your opponent played **C**
# in the previous round, play **C** in the current round.    - If your opponent
# played **D** in the previous round, retaliate by playing **D** in the current
# round.    - However, given the 10% noise, occasionally forgive perceived
# defections. Specifically:      - After retaliating with **D** once, **return
# to playing C** in the following round, assuming their defection may have been
# noise.  3. **Noise Management:** Recognize that some defections may be
# unintentional due to the 10% chance of noise. To mitigate this:    - If the
# opponent defects twice in a row, **assume the defection is intentional** and
# continue playing **D** until they return to cooperation.    - If the opponent
# defects only once, assume noise and **return to cooperation (C)** after one
# round of retaliation.  4. **Punish Extended Defection:** If the opponent
# defects for **three consecutive rounds**, escalate by consistently playing
# **D** until they cooperate. This signals that continuous aggression will not
# be tolerated.  5. **Return to Cooperation:** Once the opponent returns to
# cooperation (after any period of mutual defection), immediately switch back to
# **C**. This fosters trust and maintains the possibility of mutual benefit.  6.
# **Final Phase:** In the last 50 rounds of the game, **gradually shift towards
# more cooperation** (play **C** more frequently), regardless of the opponent’s
# actions. This prevents a cycle of endless defection and maximizes the
# possibility of mutual benefit towards the endgame.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Initial cooperation
      if self.first_round():
          return axl.Action.C
  
      # Helper function to count defections in the last N rounds
      def count_defections(n):
          return list(opponent.history[-n:]).count(axl.Action.D)
  
      # Tit-for-tat with forgiveness
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # If opponent defected once, retaliate with D
          if count_defections(1) == 1:
              return axl.Action.D
          # If opponent defected twice in a row, assume intentional defection
          elif count_defections(2) == 2:
              return axl.Action.D
          # If opponent defected three times in a row, escalate punishment
          elif count_defections(3) == 3:
              return axl.Action.D
          # Otherwise, forgive after one round of retaliation
          else:
              return axl.Action.C
  
      # Final phase: In the last 50 rounds, shift towards more cooperation
      if len(self.history) >= 950:
          # Gradually increase cooperation probability
          cooperation_probability = (1000 - len(self.history)) / 50
          return self._random.random_choice(cooperation_probability)
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# In light of the multi-round nature of these negotiations, the potential for
# miscommunication, and the fact that both sides have an interest in maximizing
# their own benefits, the **Tit-for-Tat with Forgiveness** strategy is a highly
# effective and cooperative approach. Here's how it works in this context:  ###
# Core Strategy: **Tit-for-Tat with Forgiveness**  1. **Start with Cooperation
# (Free Trade)**:    - In the first round, propose a free trade agreement. This
# signals goodwill and a willingness to cooperate, setting a positive tone for
# negotiations.     2. **Reciprocate Your Counterpart's Move**:    - In each
# subsequent round, mimic your counterpart's previous move. If they offered free
# trade in the previous round, you offer free trade again. If they implemented a
# protectionist policy, you respond with a protectionist policy in the next
# round.     3. **Introduce Forgiveness to Account for Miscommunication**:    -
# Since miscommunications or bureaucratic errors may occur, after retaliating
# with protectionism in response to your counterpart's protectionist policy,
# **forgive** after one round. This means if your counterpart shifts back to
# free trade, you immediately reciprocate with free trade again in the next
# round. This prevents the negotiations from devolving into a cycle of endless
# protectionism, which is damaging for both countries.  ### Why This Strategy
# Works:  - **Encourages Cooperation**: By starting with free trade and
# reciprocating cooperation, you incentivize mutual free trade, which is the
# second-best outcome and beneficial for both countries. Your counterpart will
# see that cooperation yields better results over time.    - **Dissuades
# Exploitation**: If your counterpart tries to exploit your goodwill by imposing
# protectionist measures while you offer free trade, the Tit-for-Tat strategy
# ensures that you retaliate in the next round. This signals to your counterpart
# that they cannot consistently take advantage of your country.  - **Allows for
# Recovery from Miscommunication**: The forgiveness element ensures that
# occasional miscommunications or errors do not permanently sour the
# negotiations. By forgiving after one round of retaliation, you give the
# process a chance to return to mutual free trade, ensuring long-term
# cooperation.  ### Practical Example (5-Round Simulation):  1. **Round 1**: You
# offer free trade. If your counterpart does the same, proceed to Round 2 with
# mutual free trade.     2. **Round 2**: If both sides offered free trade in
# Round 1, continue with free trade. If your counterpart imposed protectionist
# measures, you respond with protectionism in Round 3.  3. **Round 3**: If your
# counterpart returns to free trade after you retaliated in Round 2, forgive
# them and return to free trade. If they persist with protectionism, you
# continue with protectionism.  4. **Round 4**: If there was mutual
# protectionism in Round 3 and your counterpart switches back to free trade, you
# forgive and reciprocate with free trade. This breaks the cycle of
# protectionism.  5. **Round 5**: Continue the pattern of reciprocation,
# offering free trade if your counterpart does the same, and responding with
# protectionism if they impose it. Forgive after one round of retaliation if
# they return to cooperation.  ### Key Considerations:  - **Flexibility**: The
# strategy is flexible enough to deal with occasional miscommunications without
# derailing the entire negotiation process. - **Long-term Balance**: By
# fostering mutual cooperation while protecting against exploitation, the
# strategy leads to balanced outcomes over many rounds of negotiations,
# preventing one country from gaining a sustained unfair advantage. - **Positive
# Signaling**: Starting with free trade shows that you are interested in mutual
# benefit, which may encourage your counterpart to adopt a similar cooperative
# stance.  In summary, the **Tit-for-Tat with Forgiveness** strategy ensures
# that your country can achieve favorable outcomes in the long term by
# encouraging cooperation, responding to protectionism when necessary, and
# allowing for recovery from errors or miscommunications.

# 1. **Start by playing Cooperate (C)** in the first round.  2. **In each
# subsequent round**, do the following:    - If your opponent played **Cooperate
# (C)** in the previous round, **play Cooperate (C)** in this round.    - If
# your opponent played **Defect (D)** in the previous round, **play Defect (D)**
# in this round.  3. **If you played Defect (D) in the previous round** because
# your opponent had previously played Defect (D), but your opponent now plays
# **Cooperate (C)**, **forgive** them and **play Cooperate (C)** in this round.
# 4. **Always assume that any single instance of Defection (D)** by your
# opponent could be due to noise, so only retaliate with Defect (D) **for one
# round** before returning to Cooperate (C) if your opponent resumes playing
# Cooperate (C).

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
      
      # Get the last move of the player (self)
      my_last_move = self.history[-1]
  
      # If opponent cooperated in the last round, cooperate
      if opponent_last_move == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round and I cooperated, retaliate with a defection
      if opponent_last_move == axl.Action.D and my_last_move == axl.Action.C:
          return axl.Action.D
  
      # If opponent defected in the last round but I defected as well, forgive and cooperate
      if opponent_last_move == axl.Action.C and my_last_move == axl.Action.D:
          return axl.Action.C
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# ### High-Level Strategy for Lengthy-Session Mediation Process  #### **1.
# Establish a Baseline of Conciliation** Start the mediation process with a
# **conciliatory proposal**. This serves multiple purposes: - It positions your
# company as a reasonable, cooperative party in the eyes of the arbitrators. -
# It encourages a collaborative atmosphere, setting a constructive tone for
# future sessions. - It allows you to collect information on your opponent’s
# approach. If they respond aggressively, you can adjust your strategy without
# appearing overly combative from the outset.  #### **2. Implement a Tit-for-Tat
# Approach with a Bias Towards Conciliation** Employ a **tit-for-tat strategy**,
# adapted for mediation. This strategy has proven effective in iterative
# conflict resolution situations. However, modify it with a slight bias towards
# conciliation to preserve your constructive image: - If your opponent offers a
# conciliatory proposal, respond with a conciliatory proposal in the next
# session. - If your opponent presents an aggressive argument, respond with a
# measured aggressive argument in the following session. - Avoid escalating the
# aggression beyond what’s necessary. If both parties become entrenched in
# aggressive arguments, the dispute could escalate, prolonging the process and
# increasing costs.  #### **3. Strategic Use of Aggression** Use **aggressive
# arguments sparingly and selectively**: - Deploy aggressive arguments when the
# stakes of a particular session are high (e.g., key legal points or financial
# terms that could significantly impact the outcome). - Only use aggression when
# you have reason to believe your opponent will offer a conciliatory proposal or
# when you need to rebalance the dynamic if they have been consistently
# aggressive. - When presenting aggressive arguments, ensure they are framed
# within a logical, fact-based context that positions your corporation as
# defending its legitimate rights, rather than appearing combative for its own
# sake.  #### **4. Maintain Flexibility and Adaptability** Recognize that the
# mediation process is dynamic, and new information or shifts in tactics can
# occur at any time. Always be prepared to adapt: - **Monitor your opponent’s
# behavior closely**. If they shift from conciliation to aggression or vice-
# versa, recalibrate your approach accordingly. - Be aware of **non-verbal
# cues** and the overall tone of the arbitration panel. If the arbitrators seem
# frustrated with aggression from either party, shift to a more conciliatory
# approach to capitalize on their sentiment. - If procedural irregularities or
# communication breakdowns occur (e.g., your argument is misunderstood or
# misrepresented), remain composed. Use the next session to **clarify the
# misunderstanding** without appearing defensive or accusatory.  #### **5.
# Protect Against Misrepresentation** Given the risk of misrepresentation or
# misunderstanding by arbitrators, ensure that your arguments, whether
# aggressive or conciliatory, are: - **Clear and concise**. Avoid ambiguity that
# could give room for misinterpretation. - **Backed by evidence**. Provide
# documented support for your claims, especially in aggressive arguments, so
# that any misrepresentation can be corrected with objective data. -
# **Reiterated in follow-up sessions**. If a key point was misunderstood in a
# previous session, calmly clarify it in the next session without discrediting
# the arbitrators.  #### **6. Foster Positive Relationships with the
# Arbitrators** Throughout the mediation process, your demeanor should remain
# professional and respectful toward the arbitrators: - Avoid overly aggressive
# posturing that could alienate the panel. - Show a willingness to engage in
# good faith discussions and to listen to the panel’s feedback. - Frame your
# aggressive arguments as necessary defenses rather than attacks, positioning
# your corporation as seeking fairness rather than domination.  #### **7. Exit
# Strategy Considerations** Always have a contingency plan for the **worst-case
# scenario** where the mediation process breaks down due to aggressive posturing
# from both sides or procedural irregularities: - Be prepared to suggest
# procedural adjustments (e.g., additional sessions, expert consultations) if
# communication breaks down. - If the mediation stalls, consider proposing
# alternative dispute resolution mechanisms (such as a narrowed focus on
# specific issues or third-party evaluations) to keep the process moving, while
# maintaining your corporation's favorable positioning.  ### Summary of
# Strategy: - **Initial Conciliation**: Start with cooperation to set a positive
# tone and gather information. - **Tit-for-Tat with Conciliatory Bias**: Mirror
# your opponent’s behavior but lean towards conciliation. - **Selectively
# Aggressive**: Use aggression only when the stakes are high and the timing is
# right. - **Adaptability**: Be flexible and adjust based on your opponent’s
# moves and any procedural irregularities. - **Clarity**: Ensure arguments are
# clear, concise, and backed by evidence to minimize misrepresentation. -
# **Respectful Engagement**: Maintain a professional and cooperative
# relationship with the arbitrators. - **Contingency Planning**: Be ready to
# propose alternatives if the mediation process breaks down.  This balanced
# approach allows for flexibility in an evolving situation, ensuring that your
# corporation is positioned favorably throughout the mediation while minimizing
# risks of prolonged conflict or procedural missteps.

# ### Iterated Normal-Form Game Strategy  1. **Start by Cooperating (C)**:
# Begin the first round by playing C to establish a cooperative tone and gather
# information on your opponent's behavior.  2. **Tit-for-Tat with a Bias Towards
# Cooperation**:      - If your opponent played C in the previous round, **play
# C** in the next round.      - If your opponent played D in the previous round,
# **play D** in the next round to signal that you will not allow exploitation.
# - However, after retaliating with D, **return to C** in the following round
# unless your opponent continues to defect. This helps maintain a bias toward
# cooperation.  3. **Ignore Single Defections**:      Due to noise, ignore a
# single instance of suspected defection (D) by your opponent and **continue to
# play C** in the next round. Only retaliate after two consecutive defections,
# as the first could be the result of noise.  4. **Return to Cooperation After
# Mutual Defection**:      If both players defect (D, D) in a round, **play C**
# in the next round to de-escalate the situation and attempt to restore
# cooperation.  5. **Adapt to Long-Term Defection**:      If your opponent
# defects (D) for three or more consecutive rounds, **continue to play D** until
# they return to cooperation. Once they play C, immediately shift back to
# cooperation in the next round.  6. **Monitor and Recover from Noisy
# Missteps**:      If a cooperative sequence (C, C) is interrupted by a noisy
# defection (e.g., you or your opponent accidentally plays D due to noise),
# don't change your strategy abruptly. **Continue playing C** for the next round
# to test if your opponent's defection was accidental. If they cooperate again,
# resume normal play.  7. **Maintain Long-Term Focus on Cooperation**:
# Throughout the 1000 rounds, prioritize fostering long-term cooperation.
# Retaliate only when necessary, and aim to shift back to cooperation as quickly
# as possible. Avoid prolonged defection exchanges that reduce both players'
# scores.  This strategy balances responsiveness to defection with a strong bias
# towards maintaining cooperation, while accounting for the noise in the game.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if the opponent defected in the last N rounds
      def opponent_defected_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D) == n
  
      # Get the last action of the opponent
      last_opponent_action = opponent.history[-1]
  
      # Rule 3: Ignore a single defection (noise handling)
      if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C and last_opponent_action == axl.Action.D:
          return axl.Action.C
  
      # Rule 5: Adapt to long-term defection (3 or more consecutive defections)
      if opponent_defected_last_n_rounds(3):
          return axl.Action.D
  
      # Rule 2: Tit-for-Tat with a bias towards cooperation
      if last_opponent_action == axl.Action.C:
          return axl.Action.C
      elif last_opponent_action == axl.Action.D:
          # Rule 4: Return to cooperation after mutual defection
          if self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D

# ### High-Level Aggressive Strategy: **"Controlled Assertiveness with Tactical
# Concessions"**  This strategy is designed to leverage aggression selectively
# while maintaining a veneer of professionalism and readiness to cooperate when
# necessary. The goal is to project strength and confidence without antagonizing
# the arbitrators or jeopardizing the possibility of a favorable resolution. The
# strategy consists of three key pillars: **Tactical Aggression**, **Strategic
# Concessions**, and **Crisis Management Preparedness**.  #### Pillar 1:
# Tactical Aggression (Primary Mode) In the majority of sessions, adopt an
# assertive posture that presents your corporation as having a dominant and
# justified position. However, aggression should be controlled, measured, and
# backed by strong legal arguments and evidence. This avoids the appearance of
# hostility while enabling you to sway the mediation process in your favor.  1.
# **Pre-Session Preparation**:     - **Thoroughly analyze the strengths and
# weaknesses** of both sides' positions. Anticipate the most aggressive points
# your opponent could raise, and prepare rebuttals that neutralize those
# arguments before they gain traction.    - Prepare **bulletproof
# documentation** to back your claims. Always be ready to present compelling
# evidence that positions your company as the party with the moral and legal
# high ground.     2. **Session Behavior**:    - Start each session with
# **strong opening statements** that assert your position as reasonable, but
# non-negotiable on key points. Frame your arguments as the more logical and
# fair interpretation of the contract.    - Use **subtle language** to paint
# your opponent’s position as overly aggressive or unreasonable without being
# overtly antagonistic. Imply that their aggressive stance, if they take one, is
# harming the process.    - **Highlight the risks** to your opponent of
# continuing the dispute. Make it clear that if they escalate the fight, it
# could result in mutual damage, but position yourself as willing to weather
# that storm.  #### Pillar 2: Strategic Concessions (Secondary Mode) While the
# default is aggressive argumentation, you should be ready to offer minimal,
# strategic concessions when advantageous. This is not a sign of weakness but a
# calculated move to: - **Build goodwill with the arbitrators**, showing that
# you are a reasonable party interested in resolution. - Create a **trap** for
# your opponent, where their refusal of your reasonable offers will make them
# appear intransigent.  1. **Minor Concessions**:    - Identify specific, low-
# cost areas where you can afford to concede without undermining your core
# objectives. These should be issues that are important to your opponent but
# have minimal impact on your bottom line.    - Offer these concessions while
# framing them as a significant compromise on your part. This strategic
# generosity can shift the arbitrators’ perception in your favor.  2. **Timely
# Concessions**:    - Concede at **key moments**: When the process is becoming
# too adversarial or when the arbitrators seem to be losing patience with the
# aggressive back-and-forth, offer a conciliatory proposal *before* your
# opponent does to appear more willing to negotiate.    - **Preemptively
# concede** on points that are likely to be lost if pressed too hard. This
# prevents wasted time and effort, while allowing you to focus on more critical
# aspects of the dispute.  #### Pillar 3: Crisis Management Preparedness
# (Contingency Mode) Recognize that procedural irregularities,
# misunderstandings, or misrepresentations during the mediation process are not
# just possible, but likely in complex, high-stakes disputes. You must
# anticipate these issues and be ready to adapt on the fly.  1. **Communication
# Backstops**:    - Ensure that all communications (both written and verbal) are
# **precise and unambiguous**. Provide ample documentation to reinforce your
# position and avoid any misinterpretation by the arbitrators.    - If a
# miscommunication occurs, be swift in **clarifying** your position. Immediately
# request a follow-up session or submit a written statement to correct the
# record before any misunderstanding takes root.  2. **Document All Procedural
# Irregularities**:    - Keep a **detailed record** of any procedural
# irregularities, such as misrepresented arguments or decisions that were based
# on misunderstood facts. This documentation can be used to argue for
# reconsideration or to appeal any unfavorable decisions.  3. **Flexibility in
# Approach**:    - Be prepared to **shift gears** if the mediation process
# becomes dysfunctional or if the arbitrators appear to be leaning heavily
# towards your opponent. If both sides are consistently aggressive and tensions
# escalate, switch to a more conciliatory tone to de-escalate the situation and
# present your corporation as the more reasonable party.    - Monitor the
# **arbitrators' reactions** carefully—if they seem sympathetic to your
# opponent, reduce aggression slightly and emphasize your willingness to find a
# fair resolution, while subtly questioning the feasibility of your opponent’s
# demands.  ---  ### Scenario-Specific Adjustments  - **Opponent Adopts
# Consistent Aggression**:     If your opponent consistently presents aggressive
# arguments, maintain your aggressive posture up to a point, but strategically
# offer conciliatory proposals in areas where you can afford to concede. This
# will demonstrate your willingness to cooperate while positioning your opponent
# as overly combative and unreasonable.  - **Opponent Adopts Consistent
# Conciliation**:     If your opponent consistently offers conciliatory
# proposals, take advantage of this by continuing your aggressive stance. This
# dynamic allows you to extract more favorable terms while their conciliatory
# approach weakens their bargaining position. Be careful not to overplay your
# hand—leave the door open for a resolution that is still mutually beneficial.
# - **Misrepresentation by Arbitrators**:     If your arguments are
# misrepresented or misunderstood, don’t react emotionally. Instead, calmly but
# firmly request clarification and provide additional documentation to ensure
# the correct interpretation of your stance. If necessary, request a separate
# session or private meeting with the arbitrators to clear any
# misunderstandings.  ---  ### Conclusion  The "Controlled Assertiveness with
# Tactical Concessions" strategy ensures that your corporation presents a strong
# and aggressive case while maintaining adaptability to changing conditions in
# the mediation process. By combining carefully timed aggression with strategic
# concessions, you will maximize your chances of securing a favorable resolution
# while preserving the arbitrators' goodwill. Be prepared for procedural
# disruptions, and always have a plan to steer the process back in your favor.

# ### Strategy for the Iterated Normal-Form Game: "Controlled Defection with
# Tactical Cooperation"  This strategy is designed to maximize long-term gains
# by predominantly defecting (D), while incorporating cooperative (C) moves at
# strategic moments to maintain a balance and exploit opportunities. Given the
# noise factor in the game (10% chance of action flip), the strategy is robust
# against miscommunications while manipulating the dynamics in your favor.  ####
# 1. **Start with Defection (D)**:    - In the first round, **always play Defect
# (D)**. This establishes an initial posture of strength and avoids giving the
# opponent an early advantage.  #### 2. **Defect by Default (D is the Default
# Play)**:    - For the majority of rounds, **continue to play Defect (D)**
# unless specific conditions (outlined below) dictate otherwise. Defection
# maximizes your score when the opponent cooperates, and avoids the worst-case
# scenario of losing when they defect.    - **Play Defect (D)** if your opponent
# defected in the previous round, regardless of what you played. This deters
# them from taking advantage of you and keeps you in a strong position.  #### 3.
# **Tactical Cooperation (C) After Mutual Defection**:    - If both you and your
# opponent played Defect (D) in the previous round, and it has happened for at
# least **two consecutive rounds**, switch to **Cooperate (C)**. This offers a
# small olive branch to create a potential shift towards mutual cooperation.
# - **Continue to play Cooperate (C)** for up to **two rounds** to see if your
# opponent reciprocates cooperation.  #### 4. **Return to Defection (D) if
# Exploited**:    - If you played Cooperate (C) but your opponent played Defect
# (D) in any of the last two rounds: **immediately return to Defect (D)** and
# continue defecting for the next **five rounds**. This punishes the opponent
# for exploiting your cooperation.  #### 5. **Gradual Introduction of
# Cooperation (C) in Later Phases**:    - After **700 rounds**, introduce more
# cooperation to increase the chances of mutual cooperation in the endgame. Play
# **Cooperate (C)** every **fifth round** unless the opponent defects in the
# previous round.    - If mutual cooperation emerges (both playing C for at
# least three consecutive rounds), remain in a cooperative cycle for as long as
# the opponent cooperates.   #### 6. **Noise Management**:    - Recognize that
# due to noise, some defections may occur unintentionally. If you were
# cooperating but observe a defection from your opponent that doesn’t align with
# their previous behavior, **continue to cooperate (C) for one more round** to
# verify whether the defection was accidental.    - If defection continues for
# more than one round, treat it as intentional and return to **Defect (D)**.
# #### 7. **Endgame Defection**:    - In the final **10 rounds**, **always play
# Defect (D)**. This ensures your opponent cannot take advantage of you in the
# closing stages, where cooperation is less likely to pay off.  #### Summary: -
# **Start with Defection (D)**. - **Defect (D)** by default, unless mutual
# defection has occurred for two rounds or more. - **Switch to Cooperation (C)**
# after mutual defection for two rounds, and test cooperation cycles. - **Punish
# defection** by returning to Defect (D) for five rounds if your cooperation is
# exploited. - **Introduce more cooperation** after round 700, but remain
# vigilant for defection. - **End with Defection (D)** in the last 10 rounds to
# avoid late-game exploitation.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if mutual defection occurred in the last two rounds
      def mutual_defection_last_two_rounds():
          return len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D and \
                 self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if opponent exploited cooperation in the last two rounds
      def opponent_exploited_cooperation():
          if len(self.history) < 2:
              return False
          return (self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D) or \
                 (self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.D)
  
      # Helper function to check if mutual cooperation has occurred for at least three rounds
      def mutual_cooperation_last_three_rounds():
          return len(self.history) >= 3 and all(self.history[-i] == axl.Action.C and opponent.history[-i] == axl.Action.C for i in range(1, 4))
  
      # Helper function to check if we are in the last 10 rounds
      def in_final_10_rounds():
          return self.match_attributes['length'] is not None and len(self.history) >= self.match_attributes['length'] - 10
  
      # Helper function to check if we are past round 700
      def past_round_700():
          return len(self.history) > 700
  
      # First round: always defect
      if self.first_round():
          self.cooperation_test_rounds = 0  # Track rounds of cooperation testing
          self.punishment_rounds = 0        # Track rounds of punishment after exploitation
          return axl.Action.D
  
      # If in punishment phase, continue defecting for 5 rounds
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # If opponent exploited cooperation, enter punishment phase
      if opponent_exploited_cooperation():
          self.punishment_rounds = 5
          return axl.Action.D
  
      # If mutual defection occurred for at least two rounds, switch to cooperation for up to two rounds
      if mutual_defection_last_two_rounds():
          if self.cooperation_test_rounds < 2:
              self.cooperation_test_rounds += 1
              return axl.Action.C
          else:
              self.cooperation_test_rounds = 0  # Reset cooperation test rounds after two rounds of cooperation
  
      # If past round 700, introduce cooperation every fifth round unless opponent defected last round
      if past_round_700():
          if len(self.history) % 5 == 0 and opponent.history[-1] != axl.Action.D:
              return axl.Action.C
  
      # If mutual cooperation has emerged for at least three rounds, continue cooperating
      if mutual_cooperation_last_three_rounds():
          return axl.Action.C
  
      # If in the final 10 rounds, always defect
      if in_final_10_rounds():
          return axl.Action.D
  
      # Default action: defect
      return axl.Action.D

# To achieve the best possible outcomes for your country across several rounds
# of bilateral trade negotiations, you need to employ a strategy that balances
# cooperation and self-protection, while also accounting for the possibility of
# miscommunications or unexpected moves by your counterpart. Below is a high-
# level, cooperative strategy that draws from game theory principles
# (particularly the "Tit-for-Tat" strategy of the Prisoner's Dilemma) while
# adapting to the nuances of multiround negotiations and the risk of
# miscommunication.  ### Strategy: **"Cautious Cooperation with Gradual
# Retaliation"**  #### 1. **Start with Free Trade as a Gesture of Goodwill**:
# - **First Round**: Begin by offering a free trade agreement. This serves as a
# clear signal of cooperation and a desire for mutual benefit. Starting with
# free trade also opens the door to a positive, long-term relationship, showing
# that you are not seeking to exploit the situation from the outset.    -
# **Rationale**: By initiating with free trade, you set a cooperative tone,
# which may encourage your counterpart to reciprocate. If both sides agree to
# free trade, it leads to the second-best outcome for your country, and you
# avoid triggering a protectionist spiral early on.  #### 2. **Tit-for-Tat with
# Forgiveness to Account for Miscommunication**:    - **Subsequent Rounds**: In
# each round, mirror your counterpart’s previous move. If they offered free
# trade in the last round, offer free trade again. If they imposed protectionist
# policies, respond with your own protectionist measures in the next round.    -
# **Forgiveness Mechanism**: If protectionism is introduced by your counterpart,
# give them the benefit of the doubt for **one round**. This means you continue
# to offer free trade in the next round, assuming the protectionist move may
# have been due to miscommunication or a bureaucratic error. However, if they
# impose protectionism again in the subsequent round, retaliate with
# protectionist measures.    - **Rationale**: Tit-for-Tat is a proven strategy
# in iterated games that encourages cooperation by responding in kind. The
# forgiveness mechanism accounts for the possibility of errors, reducing the
# risk of a breakdown in cooperation due to misunderstandings.  #### 3.
# **Escalate Slowly to Avoid Long-Term Damage**:    - If the counterpart
# consistently opts for protectionist policies (after the initial forgiveness),
# respond with protectionism but **gradually**. For example, start with mild
# tariffs or quotas rather than harsh restrictions. This signals that you are
# willing to retaliate but are still open to returning to free trade if they
# change course.    - **Rationale**: Gradual escalation prevents the situation
# from spiraling into a full-blown trade war, which would lead to the worst-case
# scenario of mutual protectionism. By escalating slowly, you leave room for
# negotiation and de-escalation.  #### 4. **Signal Willingness to Return to Free
# Trade**:    - Even after retaliating with protectionist measures, consistently
# signal that you are open to returning to free trade. This can be done through
# public statements, diplomatic channels, or proposing a "reset" in a future
# round.    - **Rationale**: Signaling a willingness to return to cooperation
# ensures that the door remains open for mutual free trade, which is the second-
# best outcome for your country. It also reduces the likelihood of long-term
# hostility.  #### 5. **Monitor and Adjust for Long-Term Trust**:    - If mutual
# free trade is maintained over several rounds, consider offering additional
# incentives, such as sector-specific trade deals or joint economic ventures.
# This strengthens the relationship and builds long-term trust.    -
# **Rationale**: Long-term trust can help reduce the risk of future
# protectionism and create a more stable economic environment for both nations.
# ### Summary of Key Steps: 1. **Start with Free Trade** as a cooperative
# gesture. 2. **Use Tit-for-Tat**, but with a **forgiveness mechanism** to
# account for miscommunications or errors. 3. **Escalate protectionism
# gradually** if necessary, keeping the door open for de-escalation. 4. **Signal
# consistently** that you are willing to return to free trade. 5. **Build long-
# term trust** through cooperation and incentives, especially if free trade
# prevails.  ### Contingency for Miscommunication: - If you suspect
# miscommunication (e.g., an unexplainable protectionist policy from your
# counterpart), use back-channel diplomacy or direct communication to clarify
# intentions before escalating. - Consider proposing a formal mechanism within
# the negotiations to resolve disputes or clarify policy changes, such as
# regular consultations or a joint review process.  By employing this cautious
# and adaptive strategy, you increase the likelihood of achieving the second-
# best outcome of mutual free trade while protecting your country from
# exploitation or long-term damage if protectionism arises.

# ### Strategy: **Cautious Cooperation with Gradual Retaliation**  1. **Start by
# Cooperating**: In the first round, play C (Cooperate).  2. **Tit-for-Tat with
# Forgiveness**:     - In each subsequent round, do the following:      - If
# your opponent played C in the previous round, play C in the current round.
# - If your opponent played D in the previous round, play C in the current round
# **once**, assuming the defect may have been caused by noise or error.      -
# If your opponent played D in the previous round and also played D the round
# before that, play D in the current round (retaliate).  3. **Gradual
# Escalation**:    - If your opponent continues to play D for **two consecutive
# rounds**, continue to play D in response, but do not escalate further.
# Maintain D as long as they continue to defect.  4. **Return to Cooperation**:
# - If your opponent switches back to playing C after a period of playing D,
# immediately play C in the following round. Do not hold a grudge.  5. **Monitor
# and Adjust**:    - If both players are consistently playing C for multiple
# rounds, continue playing C indefinitely.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the last two moves of the opponent (if available)
      last_move = opponent.history[-1]
      second_last_move = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # Tit-for-Tat with Forgiveness
      if last_move == axl.Action.C:
          return axl.Action.C
      elif last_move == axl.Action.D:
          if second_last_move == axl.Action.D:
              # Gradual Retaliation: opponent defected twice in a row, retaliate with D
              return axl.Action.D
          else:
              # Forgive a single defection, play C
              return axl.Action.C

# The situation you're describing resembles a variation of the **Iterated
# Prisoner's Dilemma**, where both parties face repeated decisions on whether to
# cooperate (share) or defect (keep findings confidential). To maximize your
# research output over the collaboration, you need a strategy that balances
# sharing information to foster progress with protecting yourself from being
# exploited in case your colleague doesn't reciprocate.  Here’s a high-level,
# straightforward, neutral strategy that accounts for the possibility of
# technical issues and imperfect communication:  ### 1. **Start with Cooperation
# (Sharing)**:    - In the first week, openly share your improvements. This sets
# a positive tone for the collaboration and signals your willingness to work
# together for mutual benefit.  ### 2. **Tit-for-Tat with Forgiveness**:    -
# After the first week, mirror your colleague’s behavior: if they share, you
# share the following week; if they don’t share, you withhold your findings the
# next week.    - **Forgiveness Mechanism**: Since technical issues may
# sometimes prevent sharing due to no fault of your colleague, adopt a forgiving
# approach. If they fail to share for one week, still give them the benefit of
# the doubt and continue sharing in the next cycle. Only withhold information if
# they fail to share for two or more consecutive weeks, which suggests
# intentional lack of cooperation.  ### 3. **Gradual Retaliation**:    - If your
# colleague consistently withholds information (e.g., two or more consecutive
# weeks), respond by keeping your findings confidential for a similar number of
# weeks as a form of proportional retaliation.    - By gradually escalating your
# response, you avoid jumping to aggressive withholding, which could damage the
# relationship and overall progress.  ### 4. **Occasional Random Sharing (Noise
# Introduction)**:    - To maintain unpredictability and avoid falling into a
# completely tit-for-tat loop, occasionally share your findings even if your
# colleague has withheld information. This introduces an element of randomness,
# which may encourage your colleague to return to sharing if they stopped due to
# suspicion or miscommunication.  ### 5. **Periodic Reset to Cooperation**:    -
# Every few weeks (e.g., after 4-6 weeks), reset to a cooperative stance
# regardless of the recent pattern. This allows both parties to "start fresh"
# and avoid a downward spiral of mutual withholding, which would hurt overall
# progress.  ### Summary of the Strategy: - **Week 1**: Share openly. - **Weeks
# 2+**: Use a **Tit-for-Tat with Forgiveness** approach:    - Mirror your
# colleague's actions but forgive occasional non-sharing (presume technical
# issues).    - Gradually retaliate if non-sharing becomes consistent.    -
# Occasionally introduce random sharing to break negative cycles. - **Reset
# periodically** to cooperation to encourage mutual progress and avoid deadlock.
# This strategy maximizes cooperation and joint progress while protecting you
# from being exploited, providing a balanced, neutral approach for a multi-week
# collaboration.

# 1. **Round 1: Cooperate (C).**  2. **From Round 2 onward:**    - If the
# opponent cooperated in the previous round, **Cooperate (C)**.    - If the
# opponent defected in the previous round, **Cooperate (C)** unless the opponent
# defected in two consecutive rounds, in which case **Defect (D)**.     3.
# **Forgiveness rule:**    - If the opponent defected in the last round but
# cooperated in the round before that, **Cooperate (C)** (to account for
# potential noise or error).  4. **Gradual retaliation:**    - If the opponent
# defects in two consecutive rounds, **Defect (D)** for one round.    - If the
# opponent defects in three consecutive rounds, **Defect (D)** for two
# consecutive rounds.    - Continue increasing retaliatory defections
# proportionally if the opponent continues defecting in consecutive rounds.  5.
# **Occasional random cooperation:**    - Every 20 rounds, regardless of the
# recent history, **Cooperate (C)** once, even if you would otherwise defect
# according to the rules above (to introduce unpredictability and possibly reset
# cooperation).  6. **Periodic reset:**    - After every 100 rounds, **Cooperate
# (C)** for one round, regardless of the previous history, to give both sides a
# chance to restart cooperation.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Cooperate
      if self.first_round():
          self.retaliation_count = 0  # Initialize retaliation counter
          return axl.Action.C
  
      # Occasional random cooperation every 20 rounds
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # Periodic reset every 100 rounds
      if len(self.history) % 100 == 0:
          return axl.Action.C
  
      # Forgiveness rule: If opponent defected last round but cooperated the round before, cooperate
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # Gradual retaliation logic
      if opponent.history[-1] == axl.Action.D:
          # Check for consecutive defections
          if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D:
              self.retaliation_count += 1
              if axl.Action.C in opponent.history:
                  last_cooperation = opponent.history[::-1].index(axl.Action.C)
              else:
                  last_cooperation = 0
              if self.retaliation_count <= len(opponent.history) - last_cooperation - 1:
                  return axl.Action.D
          else:
              self.retaliation_count = 0  # Reset retaliation count if no consecutive defections
      else:
          self.retaliation_count = 0  # Reset retaliation count if opponent cooperated
  
      # Default behavior: Cooperate if opponent cooperated last round
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If none of the above conditions apply, cooperate
      return axl.Action.C

# ### High-Level Aggressive Strategy: "Conditional Cooperation with Escalation"
# This strategy focuses on balancing risk and reward while maintaining a degree
# of assertive control over the project's progress. The core principle is to
# incentivize the corporation to invest heavily, while safeguarding your NGO
# from excessive resource depletion in case the corporation tries to conserve.
# You will also be prepared to adapt quickly if unforeseen circumstances (e.g.,
# glitches or errors) affect resource allocation.  Here’s how you can implement
# this strategy:  ---  ### **1. Start Strong with Mutual Investment (Day 1 -
# "Test the Waters")** On Day 1, signal your commitment to the project by
# investing heavily. This will set a cooperative tone and encourage the
# corporation to do the same. If both parties invest heavily, the project will
# gain significant momentum from the start, and you signal that you are serious
# about project success.  - **Rationale:** Starting strong builds trust and sets
# a positive tone. If the corporation is cooperative, this will create a
# foundation for mutual investment in future days. However, be cautious and
# observe the corporation’s behavior closely.  ---  ### **2. Monitor and Respond
# to Corporation's Behavior (Days 2-3 - "Establish the Pattern")** Evaluate the
# corporation’s behavior from Day 1: - If **both parties invested heavily** on
# Day 1, continue to invest heavily on Day 2 and 3 to maintain momentum and
# build trust. - If the **corporation conserved resources** while you invested
# heavily on Day 1, **immediately switch to conserving** on Day 2 to signal that
# you won’t be taken advantage of.     - If the corporation continues to
# conserve on Day 2, maintain conservation through Day 3 (minimizing your
# losses).     - If the corporation invests heavily on Day 2, **return to heavy
# investment on Day 3** to re-align efforts.  - **Rationale:** The idea here is
# to establish a pattern of cooperation or non-cooperation. By Day 3, you should
# have a clear understanding of the corporation’s willingness to invest, and you
# can adjust your strategy accordingly.  ---  ### **3. Implement Conditional
# Cooperation (Days 4-5 - "Tit-for-Tat with Forgiveness")** Once you understand
# the corporation's pattern, adopt a "tit-for-tat" approach: - **If the
# corporation invests heavily**, you continue to invest heavily. - **If the
# corporation conserves**, you conserve as well on the next day to prevent
# resource waste.  However, allow for occasional "forgiveness" if the
# corporation fails to invest for one day (possibly due to unforeseen
# circumstances like technical glitches). If the corporation conserves on one
# day but invested heavily before, you can give them the benefit of the doubt
# and invest heavily once more to re-align.  - **Rationale:** This approach
# encourages cooperation but also protects your NGO from being exploited.
# Occasional forgiveness allows for flexibility in case of unforeseen errors or
# glitches that temporarily prevent the corporation from investing as intended.
# ---  ### **4. Gradually Escalate Aggression if the Corporation Fails to
# Cooperate (Days 6 Onward - "Final Push")** If, by Day 6, the corporation
# continues to conserve resources while you’ve been investing heavily, escalate
# your strategy: - **Day 6:** Conserve your resources heavily and communicate
# your concerns openly to the corporation. State that your NGO can only continue
# to invest if the corporation matches your efforts. - **Day 7 Onward:** If the
# corporation does not change its behavior, conserve resources consistently, and
# focus on maximizing minimal progress (i.e., avoiding heavy losses).  -
# **Rationale:** If the corporation is consistently conserving at this stage,
# it’s likely that mutual cooperation will not be possible. Therefore, the best
# outcome is to minimize your losses while still contributing to the project,
# albeit at a slower pace.  ---  ### **5. Maintain Open Communication and
# Transparency Throughout** Throughout the multiple days, maintain open
# communication with the corporation. Regularly share progress reports, voice
# your expectations, and discuss any challenges (e.g., technical glitches or
# administrative errors) that may impact resource allocation. This will help
# mitigate misunderstandings and ensure that both parties remain aligned.  -
# **Rationale:** Transparent communication reduces the risk of misinterpretation
# of each other’s actions and can prevent unnecessary escalation of the strategy
# due to unforeseen circumstances.  ---  ### **Contingency for Unforeseen
# Circumstances** If there are any technical glitches or administrative errors
# that impede your ability to invest as planned: - Communicate the issue
# immediately to the corporation to prevent misinterpretation. - If the
# corporation faces similar issues, remain flexible and avoid penalizing them
# for one-off failures to invest.  - **Rationale:** Flexibility in the face of
# unforeseen issues helps maintain trust and cooperation, preventing the project
# from stalling due to miscommunication.  ---  ### Summary of Key Actions: -
# **Day 1:** Invest heavily to signal commitment and set a cooperative tone. -
# **Days 2-3:** Monitor the corporation’s behavior; respond by conserving if
# they fail to invest. - **Days 4-5:** Engage in conditional cooperation ("tit-
# for-tat with forgiveness"). - **Day 6 Onward:** Escalate aggression if the
# corporation consistently conserves, while conserving your own resources to
# limit losses. - **Maintain Communication:** Be transparent and responsive to
# unforeseen circumstances that may affect investment on either side.  ---  This
# aggressive, high-level strategy leverages assertiveness, adaptability, and
# communication to maximize your NGO's impact on the project while minimizing
# potential resource wastage. It keeps the corporation accountable for its
# actions while allowing for some flexibility in the face of unpredictable
# challenges.

# ### Iterated Normal-Form Game Strategy: "Tit-for-Tat with Forgiveness and
# Escalation"  1. **Round 1: Always Cooperate**      On the first round, play
# **C** (Cooperate). This signals your intent to collaborate and establishes a
# cooperative tone.  2. **Round 2-3: Mirror Your Opponent’s Last Action**      -
# If your opponent played **C** in the previous round, play **C** in the next
# round.      - If your opponent played **D** in the previous round, play **D**
# in the next round.      This phase helps you assess whether your opponent is
# inclined toward cooperation or defection.  3. **Round 4 Onward: Tit-for-Tat
# with Occasional Forgiveness**      Continue to mirror your opponent’s last
# action (play **C** if they played **C**, play **D** if they played **D**), but
# implement forgiveness for noise:    - If your opponent defects **once** after
# a series of **C** plays (at least 3 consecutive **C**s), **forgive** and play
# **C** in the next round, assuming their defection may have been due to noise.
# - If your opponent defects **more than once consecutively**, respond by
# playing **D** until they return to **C**.  4. **Round 500 Onward: Escalate if
# Defection Persists**      If, by Round 500, your opponent has been defecting
# consistently (more than 50% of their actions are **D**), escalate your
# response:    - Play **D** consistently for the remainder of the game unless
# they return to **C** for at least 5 consecutive rounds.      - If they return
# to **C** for 5 consecutive rounds, resume cooperation by playing **C**.  5.
# **Throughout: Adapt to Noise**      Given the 10% chance of noise (action
# flipping), remain aware of unintentional defections. Forgive occasional
# isolated **D** plays if they are uncommon in an otherwise cooperative
# sequence.  ---  ### Summary of Key Rules: - **Round 1:** Always play **C**.
# - **Rounds 2-3:** Mirror your opponent's last action.   - **Round 4 Onward:**
# Use tit-for-tat with forgiveness for isolated defections.   - **Round 500
# Onward:** Escalate to consistent defection if your opponent defects
# persistently.   - **Throughout:** Account for noise by forgiving rare,
# isolated defections.  This strategy encourages long-term cooperation while
# protecting against exploitation and adapting to noise.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if opponent has defected more than once consecutively
      def opponent_defected_consecutively(n):
          return all(move == axl.Action.D for move in opponent.history[-n:])
  
      # Helper function to check if opponent has cooperated for the last n rounds
      def opponent_cooperated_consecutively(n):
          return all(move == axl.Action.C for move in opponent.history[-n:])
  
      # Helper function to check if opponent has defected more than 50% of the time
      def opponent_defection_rate():
          return opponent.history.defections / len(opponent.history)
  
      # Rounds 2-3: Mirror opponent's last action
      if len(self.history) in [1, 2]:
          return opponent.history[-1]
  
      # Round 4 onward: Tit-for-Tat with forgiveness
      if len(self.history) >= 3:
          # Forgive a single defection after a series of cooperations
          if opponent.history[-1] == axl.Action.D and opponent_cooperated_consecutively(3):
              return axl.Action.C
          # If opponent defects more than once consecutively, retaliate with D
          if opponent_defected_consecutively(2):
              return axl.Action.D
          # Otherwise, mirror the opponent's last action
          return opponent.history[-1]
  
      # Round 500 onward: Escalate if defection persists
      if len(self.history) >= 500:
          if opponent_defection_rate() > 0.5:
              # Escalate to consistent defection unless opponent cooperates for 5 consecutive rounds
              if opponent_cooperated_consecutively(5):
                  return axl.Action.C
              return axl.Action.D

# ### **High-Level Strategy for Mediation Process**  To navigate this complex
# mediation process, we need an adaptable and dynamic strategy that balances
# competitive and cooperative elements. We must remain flexible to the
# possibility of miscommunication or procedural irregularities, but also
# strategically position our corporation to take advantage of opportunities that
# may arise during each session. Here is a clear and sophisticated approach that
# will guide our interactions throughout the mediation:  ---  ### **1. Establish
# a Baseline of Cooperation:** **Initial Sessions:** - Start by proposing
# conciliatory offers in the first few sessions. This helps establish a
# reputation for being reasonable and solution-oriented in the eyes of the
# arbitrators. It also signals to the opposing party that we are open to working
# collaboratively to reach a fair outcome. - Use these early conciliatory
# proposals to gather intelligence on your opponent’s underlying interests,
# demands, and negotiation style. Pay close attention to their responses to
# gauge whether they are inclined toward cooperation or prefer a more
# adversarial posture.  **Rationale:**   This sets a cooperative tone and
# encourages the opponent to reciprocate, leading to the second-best outcome
# (both parties conciliatory). It also builds credibility with the arbitrators,
# which will be useful in future sessions if we need to argue more aggressively.
# ---  ### **2. Strategic Aggression at Key Moments:** **Selective Aggression:**
# - As the mediation progresses, identify key sessions where the stakes are high
# or the issues are particularly important to our corporation. In these
# sessions, we should present **aggressive arguments** if we sense that the
# opponent is still in a conciliatory mode or if their proposal signals
# weakness. - Use aggressive arguments to push back on unreasonable demands,
# highlight flaws in the opponent’s position, and sway the arbitrators. However,
# be careful to maintain a professional tone to avoid antagonizing the
# arbitrators or the opposing party.  **Rationale:**   The optimal outcome (we
# are aggressive, they are conciliatory) can be achieved by choosing the right
# moment to shift from a cooperative to a more assertive stance. The
# arbitrators, having already seen our collaborative side, will be more likely
# to favor our arguments in these critical moments.  ---  ### **3. Monitor and
# Adapt to Opponent’s Behavior:** **Tactical Flexibility:** - Continuously
# monitor the behavior and strategy of the opposing party. If they adopt an
# aggressive posture early on, we may need to pivot to a more defensive but firm
# stance, offering calculated conciliatory proposals initially to de-escalate
# and buy time. - If the opponent is consistently conciliatory, we should take
# advantage by pushing for more favorable terms through measured aggression. -
# In the event that both parties begin to escalate aggressively, we should take
# a step back and reintroduce conciliatory proposals to prevent the dispute from
# spiraling out of control. We cannot afford to allow the process to become so
# contentious that it damages our long-term business interests or standing with
# the arbitrators.  **Rationale:**   Flexibility ensures that we are not locked
# into a single approach, making it difficult for the opponent to predict our
# next move. This will allow us to stay one step ahead, adapting to their
# strategy while maintaining control over the general direction of the
# mediation.  ---  ### **4. Contingency Planning for Misunderstandings or
# Irregularities:** **Prepare for Procedural Deviations:** - Anticipate possible
# miscommunication or procedural irregularities, such as the arbitrators
# misunderstanding our arguments or the opponent’s proposals being
# misrepresented. Always clarify key points in each session and follow up in
# writing to ensure a clear record of our position. - If our argument is
# misrepresented, address the issue calmly and professionally in the next
# session, emphasizing the misunderstanding without appearing defensive. Use
# this as an opportunity to reinforce our key points. - In the event that the
# opponent’s conciliatory proposal is misunderstood as aggressive (or vice
# versa), tactfully point out the discrepancy and adjust our response
# accordingly to either de-escalate or capitalize on the arbitrators’
# perception.  **Rationale:**   By preparing for potential miscommunication or
# procedural issues, we ensure that these irregularities do not derail our
# broader strategy. Clear, consistent communication helps minimize the risk of
# misunderstandings and allows us to maintain credibility with the arbitrators.
# ---  ### **5. Build Leverage for the Final Sessions:** **Endgame
# Negotiation:** - As mediation progresses toward its conclusion, we should
# gradually shift toward more aggressive positions in areas where we have built
# credibility and identified key weaknesses in the opponent’s case. - Use the
# goodwill accumulated from earlier conciliatory proposals to push for a
# favorable resolution, leveraging the arbitrators’ desire to see a resolution
# and the opponent’s potential fatigue from the lengthy process. - Be prepared
# to make final conciliatory gestures on less critical issues to seal the deal
# without compromising on our core interests.  **Rationale:**   The final
# sessions are where long-term leverage and negotiation capital are cashed in.
# By positioning ourselves as reasonable but firm throughout the process, we
# will have the upper hand in closing out the mediation with favorable terms.
# ---  ### **6. Preserve Relationships and Reputation:** - Throughout the
# process, remain mindful of the long-term relationship with both the opposing
# party and the arbitrators. Even in aggressive moments, avoid personal attacks
# and focus on the merits of the case. We must protect our corporation’s
# reputation as a fair and reasonable party in international disputes. - Be
# prepared to mend fences with the opposing party post-mediation if a business
# relationship is likely to continue in other areas.  **Rationale:**
# Preserving relationships and reputation is crucial for future negotiations and
# maintaining our corporation’s standing in the industry. A well-balanced
# approach to this mediation will ensure that we come out of the process not
# only with a favorable outcome but also with our reputation intact.  ---  ###
# **Conclusion:** This strategy combines cooperative and competitive elements to
# maximize the chances of a favorable outcome. By starting with conciliatory
# proposals, watching for strategic moments to shift to aggression, adapting to
# the opponent’s behavior, and preparing for potential procedural issues, we
# build a strong, flexible, and sophisticated approach that will serve us well
# throughout this complex mediation process.

# ### **Strategy for Iterated Game:**  1. **Start Cooperating (C):**    - In the
# first 10 rounds, always play **C** (cooperate). This establishes a cooperative
# baseline and signals to your opponent that you are willing to work toward a
# mutually beneficial outcome.  2. **Continue Cooperating if Mutual Cooperation
# is Sustained:**    - If both you and your opponent play **C** during these
# initial rounds, continue playing **C**. As long as your opponent consistently
# cooperates (i.e., plays **C** with minor deviations due to noise), maintain
# cooperation.  3. **Respond Aggressively to Clear Defection:**    - If your
# opponent defects (plays **D**) more than twice in any 10-round span, switch to
# **D** (defect) for the next 3 rounds. This signals that you are unwilling to
# tolerate consistent defection.    - After 3 rounds of **D**, return to **C**
# and observe your opponent’s response.  4. **Account for Noise and
# Miscommunication:**    - If your opponent defects only once or twice in a
# 10-round span, treat this as potential noise (the 10% chance of
# miscommunication). **Do not immediately respond with defection** unless the
# defection pattern becomes consistent (more than twice in 10 rounds).    - If
# your own action is flipped accidentally (you play **C** but it registers as
# **D**), continue playing **C** in the following rounds to correct the
# miscommunication.  5. **Tit-for-Tat with Forgiveness:**    - If your opponent
# defects more than twice in a 10-round span, adopt a **Tit-for-Tat** strategy:
# match their previous action. If they play **D**, you play **D** in the next
# round; if they play **C**, you play **C**.    - However, after every 5
# consecutive **D** actions between both players, play **C** once to test if
# your opponent is willing to return to cooperation.  6. **Escalate Gradually if
# Consistent Defection Occurs:**    - If your opponent defaults to **D**
# (defects) for more than 5 rounds in a row, escalate by playing **D** for the
# next 10 rounds. After this, test cooperation again by playing **C**.    - If
# they return to cooperation, return to playing **C**. If they continue
# defecting, maintain **D** for another 10 rounds and repeat this cycle.  7.
# **Reset Strategy Regularly to Encourage Cooperation:**    - Every 100 rounds,
# regardless of past behavior, play **C** for 5 rounds consecutively to reset
# the dynamic and encourage mutual cooperation. This gives your opponent a fresh
# opportunity to cooperate.  8. **Endgame Shift:**    - In the last 50 rounds of
# the 1000-round game, shift toward a more aggressive stance. Play **D** more
# frequently, especially if the opponent has shown a tendency to defect.
# Specifically, play **D** in 50% of the rounds, alternating randomly between
# **C** and **D**.  ---  ### **Summary of Key Conditions:**  - **Start with
# Cooperation (C)** for at least the first 10 rounds. - **Cooperate (C)** as
# long as your opponent consistently cooperates (no more than 2 defections in 10
# rounds). - **Defect (D) for 3 rounds** if your opponent defects more than
# twice in any 10-round span, then return to cooperation. - **Forgive occasional
# defections** due to noise (1-2 defections in 10 rounds), assuming your
# opponent returns to cooperation. - If your opponent defects **more than twice
# in 10 rounds**, switch to **Tit-for-Tat** (match their previous action). -
# **Escalate to extended defection** if your opponent consistently defects for
# more than 5 rounds. - **Reset to cooperation** every 100 rounds by playing
# **C** for 5 consecutive rounds. - **Shift to a more aggressive approach** in
# the final 50 rounds by playing **D** in 50% of the rounds.  This strategy
# ensures a balance between cooperation and retaliation, accounting for noise
# while capitalizing on opportunities for favorable outcomes.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      RESET_INTERVAL = 100
      ENDGAME_THRESHOLD = 950
      ENDGAME_ROUNDS = 50
      ENDGAME_DEFECT_PROB = 0.5
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_count = 0  # Track defections in the last 10 rounds
          self.defect_streak = 0    # Track consecutive defections by opponent
          self.retaliation_count = 0 # Track retaliation rounds after defection
          self.reset_rounds = 0      # Track rounds for reset every 100 rounds
          return COOPERATE
  
      # Get the current round number
      current_round = len(self.history)
  
      # Reset strategy every 100 rounds
      if current_round % RESET_INTERVAL == 0:
          self.reset_rounds = 5
  
      # Handle reset rounds (play C for 5 rounds every 100 rounds)
      if self.reset_rounds > 0:
          self.reset_rounds -= 1
          return COOPERATE
  
      # Endgame shift: last 50 rounds, play D with 50% probability
      if current_round > ENDGAME_THRESHOLD:
          return self._random.random_choice(ENDGAME_DEFECT_PROB)
  
      # Count defections in the last 10 rounds
      recent_defections = opponent.history[-10:].count(DEFECT)
  
      # If opponent defects more than twice in the last 10 rounds, retaliate for 3 rounds
      if recent_defections > 2:
          if self.retaliation_count == 0:
              self.retaliation_count = 3  # Set retaliation for 3 rounds
          if self.retaliation_count > 0:
              self.retaliation_count -= 1
              return DEFECT
  
      # If opponent defects more than twice, switch to Tit-for-Tat
      if recent_defections > 2:
          return opponent.history[-1]
  
      # If opponent defects more than 5 times in a row, escalate defection for 10 rounds
      if opponent.history[-5:].count(DEFECT) == 5:
          self.defect_streak = 10
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return DEFECT
  
      # Default to cooperation if no significant defection pattern is detected
      return COOPERATE

# To maximize research output over the multi-week collaboration while accounting
# for the possibility of communication breakdowns and uncertainties about your
# colleague's strategy, you can adopt a **Tit-for-Tat with Forgiveness**
# strategy, which is both cooperative and adaptable. Here's a high-level outline
# of this approach:  ### 1. **Start by Sharing Openly**    - Begin the
# collaboration by openly sharing your improvements. This establishes a
# foundation of trust, encourages cooperation, and signals you are willing to
# collaborate for mutual benefit.     ### 2. **Mirror Your Colleague's Actions**
# - In the following weeks, **mirror your colleague's previous action**:      -
# If your colleague shared openly in the previous week, continue sharing your
# findings as well.      - If your colleague withheld information, you should
# keep your findings confidential in the next week.     ### 3. **Incorporate
# Forgiveness for Technical Issues**    - Since technical issues (such as data
# corruption or communication breakdowns) can interfere with information
# sharing, **forgive any single instance of non-sharing** (i.e., assume it might
# have been accidental or due to miscommunication).    - After a single instance
# of non-sharing, continue sharing your improvements in the next week. If non-
# sharing persists for two consecutive weeks, then switch to withholding
# information yourself to protect your competitive position.     ### 4.
# **Regularly Reassess**    - Periodically evaluate the collaboration to ensure
# it's mutually beneficial:      - If the exchange of information is regular and
# both parties are benefiting, continue sharing.      - If the collaboration
# becomes heavily one-sided (i.e., your colleague consistently withholds
# information), prioritize protecting your own findings and stop sharing until
# behavior improves.  ### 5. **Encourage Open Dialogue**    - Throughout the
# collaboration, maintain open communication about the progress and any
# technical difficulties you or your colleague might encounter. This can help
# mitigate misunderstandings and reinforce cooperation.  ### Key Benefits of
# This Strategy: - **Maximizes Long-Term Collaboration**: By starting with
# cooperation and mirroring your colleague's actions, you encourage a pattern of
# mutual sharing, which helps both parties advance their designs. - **Protects
# Against Exploitation**: If your colleague chooses to withhold information,
# mirroring their behavior ensures you’re not consistently at a disadvantage. -
# **Accounts for Technical Issues**: The forgiveness mechanism reduces the risk
# of overreacting to accidental lapses in sharing, maintaining the collaborative
# spirit even when technical problems arise.    This approach balances
# cooperation and caution, helping you maximize your research output while
# minimizing the risk of being exploited.

# ### Strategy for the Iterated Normal-Form Game (1000 Rounds, Noisy Actions)
# 1. **Initial Move**:      - In the first round, **play Cooperate (C)**.  2.
# **Main Rule** (Tit-for-Tat with Forgiveness):      - For each subsequent round
# (starting from round 2), **play the same action your opponent played in the
# previous round**:      - If your opponent played **C** in the previous round,
# **play C**.      - If your opponent played **D** in the previous round, **play
# D**.  3. **Forgiveness for One-Time Defections**:      - If your opponent
# plays **D** in a round but played **C** in the round before that:      -
# **Forgive once** and **play C** in the next round (assuming the defection may
# have been caused by noise).      - If your opponent plays **D** again in the
# next round, **switch to playing D** until they start playing C consistently
# again.  4. **Return to Cooperation**:      - If your opponent switches back to
# **C** after a string of **D** actions, return to **C** as well in the next
# round.  5. **Handling Extended Defection**:      - If your opponent plays
# **D** for two consecutive rounds or more, **continue playing D** until they
# switch back to **C**.  This strategy prioritizes cooperation, allows for
# occasional mistakes due to noise, but protects against prolonged exploitation
# by defecting in response to continued non-cooperation.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
  
      # Forgiveness rule: If opponent defected last round but cooperated the round before that
      if len(opponent.history) > 1:
          opponent_second_last_move = opponent.history[-2]
          if opponent_last_move == axl.Action.D and opponent_second_last_move == axl.Action.C:
              # Forgive once and cooperate
              return axl.Action.C
  
      # Main rule: Tit-for-Tat (play the opponent's last move)
      return opponent_last_move

# ### High-Level Aggressive Strategy: **"Dominate and Retaliate"**
# **Objective**: Maximize national advantage by pushing for protectionist
# policies while deterring the other side from reciprocating with protectionism.
# Ensure adaptability to counter any unexpected actions or errors during
# negotiations.  #### Key Components of Strategy:  1. **Initial Aggression
# (Round 1)**:    - **Propose Protectionist Policy**: Start the negotiations by
# imposing tariffs or quotas. This signals strength and asserts your intention
# to protect national interests.     - **Rationale**: This phase tests the
# counterpart’s willingness to cooperate or retaliate. Given that your ideal
# outcome is protectionism while the other side offers free trade, you want to
# immediately set the tone and see if they back down and offer free trade.  2.
# **Observe Response and Adjust**:    - If **they propose free trade**: Continue
# with protectionist measures. **Maintain the advantage** for as long as
# possible since this is your ideal outcome.    - If **they counter with
# protectionism**: Move to a second strategy phase (see below).  3. **Retaliate
# if Necessary (Round 2 and Beyond)**:    - If your counterpart **responds with
# protectionism** in Round 1 or any subsequent rounds, **mirror their policies**
# by proposing protectionism in the next round. This demonstrates that you won’t
# tolerate one-sided protectionism against your country.    - **Rationale**:
# Mutual protectionism is not ideal, but it’s better than being at a
# disadvantage. By showing you are willing to retaliate, you discourage your
# counterpart from making further protectionist moves.  4. **Signal Willingness
# for Mutual Free Trade (Round 3 or 4)**:    - After a few rounds of tension
# (especially if both sides are engaging in protectionism), signal an **offer of
# free trade** in a round where you believe there is a high chance of your
# counterpart considering the same.     - **Rationale**: Mutual free trade is
# the second-best outcome and may be necessary to avoid prolonged economic
# stagnation. By proposing free trade after a few rounds of hardened
# protectionism, you offer a potential way out for both parties.  5. **Punish
# Defection**:    - If your counterpart ever **defects from mutual free trade**
# by imposing protectionism when you offer free trade, **immediately return to
# full protectionism** in the following round and maintain it for several
# rounds.    - **Rationale**: This ensures that any defection is met with
# consequences, deterring future betrayals. The goal is to make it clear that
# free trade is acceptable only if maintained by both sides.  6. **Adaptability
# and Handling Miscommunications**:    - Given the possibility of
# miscommunication or bureaucratic errors, **avoid overreacting to a single
# round of unexpected behavior**. If there’s a sudden shift (e.g., they impose
# protectionism when you expected free trade), **wait for one more round** to
# confirm their intent before retaliating.    - **Rationale**: Miscommunications
# can cause accidental shifts in policy. By waiting for confirmation, you avoid
# unnecessary escalation due to a one-off mistake.  #### Summary of Strategy
# Phases:  1. **Start aggressively** with protectionism, seeking to gain the
# upper hand immediately. 2. **Retaliate** against protectionism to avoid being
# taken advantage of. 3. **Seek a temporary truce** through mutual free trade
# after several rounds, if the situation becomes stagnant. 4. **Punish
# defection** and return to protectionism if the counterpart betrays mutual free
# trade. 5. **Adapt** to potential miscommunications by not reacting hastily to
# a single unexpected move.  #### Strategic Considerations:  - **Psychological
# Advantage**: By starting with protectionism, you put the other side on the
# defensive. Your counterpart may become more cautious, allowing you to dictate
# the terms in the negotiations. - **Tit-for-Tat with Forgiveness**: The
# strategy employs a variation of the "tit-for-tat" approach, but with a slight
# delay in retaliation to account for potential errors. This makes your approach
# firm but not overly aggressive. - **Long-Term Diplomatic Relations**: While
# aggressive, the strategy leaves room for cooperative outcomes in the long term
# by offering mutual free trade once the counterpart respects your strength.
# This strategy aims to achieve the best possible outcomes for your country
# while managing the risks of miscommunication and ensuring that you’re never
# left at a disadvantage for long.

# ### Iterated Normal-Form Game Strategy: "Dominate and Retaliate"  1. **Start
# by Defecting (D)**:    - In round 1, play **D** (Defect). This tests the
# opponent's willingness to cooperate and establishes an aggressive stance.  2.
# **If the opponent plays C (Cooperate)**:    - If the opponent plays **C** in
# the previous round, continue playing **D** in the next round to maximize your
# advantage.   3. **If the opponent plays D (Defect)**:    - If the opponent
# plays **D** in the previous round, **mirror their action** by playing **D** in
# the next round. This ensures that you do not fall behind if the opponent
# chooses to defect.  4. **Test for Mutual Cooperation after Sustained
# Defection**:    - After 3 consecutive rounds of mutual **D** (Defection),
# attempt to **Cooperate (C)** in the next round. This signals a potential shift
# toward mutual cooperation, which is preferable to prolonged mutual defection.
# 5. **If the opponent responds with C (Cooperate)** after your C**:**    - If
# the opponent plays **C** in response to your cooperation, continue to play
# **C** in future rounds to maintain mutual cooperation.  6. **If the opponent
# responds with D (Defect)** after your C**:**    - If the opponent plays **D**
# after you cooperate, immediately return to **D** in the next round and
# maintain defection for at least 5 rounds to punish their defection.  7.
# **Adapt to Noise**:    - If a single round’s action from the opponent seems
# unexpected (e.g., they defect when you expected cooperation), **wait for one
# more round** before changing your strategy, as it may be due to noise in the
# game. Only switch your action after seeing two consecutive unexpected actions.
# 8. **Continue Iterating**:    - When mutual cooperation is established,
# maintain **C** unless the opponent defects twice in a row.    - If defection
# becomes mutual or prolonged (e.g., after multiple cycles of both playing
# **D**), use the same testing process again: after 3 rounds of mutual **D**,
# play **C** to probe for possible cooperation.  This strategy ensures that you
# strive for the highest possible payoff while protecting yourself from being
# exploited. It uses defection to establish dominance but remains open to
# shifting towards mutual cooperation when the conditions improve.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if the last N rounds were mutual defections
      def mutual_defection_in_last_n_rounds(n):
          return all(self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, n + 1))
      
      # Helper function to check if the opponent defected unexpectedly
      def unexpected_defection():
          return self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D
      
      # Helper function to check if the opponent cooperated unexpectedly
      def unexpected_cooperation():
          return self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C
      
      # Start by defecting in the first round
      if self.first_round():
          self.retaliation_count = 0  # Track how many rounds we are retaliating
          self.cooperation_test = False  # Track if we are testing for cooperation
          self.unexpected_action_count = 0  # Track unexpected actions for noise handling
          return axl.Action.D
      
      # Handle noise: if an unexpected action happens, wait for one more round before reacting
      if unexpected_defection() or unexpected_cooperation():
          self.unexpected_action_count += 1
          if self.unexpected_action_count < 2:
              return self.history[-1]  # Repeat the last action to wait for confirmation
          else:
              self.unexpected_action_count = 0  # Reset after two unexpected actions
      else:
          self.unexpected_action_count = 0  # Reset if no unexpected action
      
      # If we are in retaliation mode, continue defecting for 5 rounds
      if self.retaliation_count > 0:
          self.retaliation_count -= 1
          return axl.Action.D
      
      # If the opponent cooperated in the last round, continue defecting to maximize advantage
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      
      # If the opponent defected in the last round, mirror their action by defecting
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      
      # Test for mutual cooperation after 3 rounds of mutual defection
      if mutual_defection_in_last_n_rounds(3):
          self.cooperation_test = True
          return axl.Action.C
      
      # If we are testing for cooperation and the opponent cooperates, continue cooperating
      if self.cooperation_test and opponent.history[-1] == axl.Action.C:
          self.cooperation_test = False
          return axl.Action.C
      
      # If we are testing for cooperation and the opponent defects, retaliate with 5 rounds of defection
      if self.cooperation_test and opponent.history[-1] == axl.Action.D:
          self.cooperation_test = False
          self.retaliation_count = 5
          return axl.Action.D
      
      # Default to defecting if no other condition is met
      return axl.Action.D

# ### High-Level Cooperative Strategy for Maximizing Impact and Project Success
# Given the dynamics of resource allocation between your NGO and the
# corporation, your goal is to establish a cooperative framework to maximize
# project success while mitigating the risk of resource wastage. The strategy
# should be flexible enough to account for unforeseen circumstances (technical
# glitches, administrative errors, etc.) but structured to promote mutual
# investment in the project.  Here’s a high-level strategy, broken down into key
# principles and practical steps:  ### 1. **Establish Open Communication and
# Trust Early On**    - **Objective**: Build a strong foundation of transparency
# and trust with the corporation.    - **Action Plan**:      - At the start of
# the project, schedule a series of meetings to discuss mutual goals, concerns,
# and expectations for resource allocation.       - Agree on a shared timeline
# and metrics for progress.      - Create a system for frequent updates (e.g.,
# daily check-ins or shared dashboards) to ensure both parties are aligned on
# their investment intentions and actual contributions.    - **Rationale**: By
# establishing trust and open communication, you reduce the likelihood of the
# corporation conserving resources while your NGO invests heavily. It also helps
# both parties stay informed if unforeseen technical or administrative issues
# arise.  ### 2. **Adopt a 'Tit-for-Tat' Strategy with Flexibility**    -
# **Objective**: Encourage cooperation by mirroring the corporation's actions,
# while being open to occasional deviations to maintain goodwill.    - **Action
# Plan**:      - **Day 1**: Begin by investing moderately or heavily to set a
# cooperative tone.      - **Subsequent Days**: Mirror the corporation's actions
# from the previous day. If the corporation invested heavily, you do the same
# the next day. If they conserved, you conserve as well, signaling cooperation
# but also caution.      - **Occasional Deviation**: Every 3-4 days, invest
# heavily regardless of the corporation's previous action to maintain momentum
# in the project. This shows goodwill and demonstrates your commitment to the
# project’s success.    - **Rationale**: A 'Tit-for-Tat' approach encourages
# mutual cooperation, as the corporation will see that conserving resources
# leads you to conserve as well. Occasional deviations ensure the project
# doesn’t stall due to overly cautious behavior.  ### 3. **Build in an Error
# Buffer**    - **Objective**: Account for mistakes or technical failures that
# might lead to unintended resource conservation or overspending.    - **Action
# Plan**:      - Agree with the corporation on the possibility of technical
# glitches or administrative errors affecting resource allocation on any given
# day.      - Establish a contingency plan: If either party fails to invest the
# intended amount due to unforeseen issues, agree to "forgive" one-off mistakes
# and return to the agreed-upon strategy the next day.      - Set up a rapid
# communication channel (e.g., WhatsApp, email alerts) to notify the other party
# in real time if errors or issues arise that impact investment actions.    -
# **Rationale**: By acknowledging that unforeseen issues might occur, you
# prevent misunderstandings that could lead to a breakdown in trust. An error
# buffer allows for smoother recovery after mistakes without damaging
# cooperation.  ### 4. **Incentivize Consistent Corporate Investment**    -
# **Objective**: Encourage the corporation to invest heavily by demonstrating
# the value and impact of their contributions.    - **Action Plan**:      -
# Focus on highlighting the positive outcomes of heavy corporate investment. For
# example, after days when the corporation invests heavily, showcase the
# immediate project advancements during check-ins.      - Provide public
# recognition or co-branding opportunities, so the corporation gains
# reputational benefits from their investments.      - If possible, offer the
# corporation tangible returns on their investment, such as data on cost
# savings, environmental impact reports, or media coverage that reinforces their
# commitment to sustainability.    - **Rationale**: By making the corporation’s
# heavy investment more attractive, you increase the likelihood that they will
# continue to invest heavily. This shifts the dynamic in your favor because it
# allows your NGO to conserve resources more often.  ### 5. **Set Pre-Agreed
# Minimum Investment Levels**    - **Objective**: Ensure baseline progress even
# in periods of resource conservation.    - **Action Plan**:      - Negotiate a
# minimum level of daily investment that both parties will commit to, even on
# days when they choose to conserve resources. This could be a small but
# meaningful amount that ensures some progress is made.      - Define
# "conservation" in a way that still includes a base level of resource
# commitment. For example, if "conserving" means cutting back 50% of the planned
# investment, both parties should still commit to the remaining 50%.    -
# **Rationale**: This reduces the risk of the project stalling entirely if both
# parties decide to conserve resources on the same day. It ensures that minimal
# progress is maintained, keeping the project moving forward.  ### 6.
# **Implement a Mid-Project Review and Adaptation Phase**    - **Objective**:
# Adjust your strategy based on real-world progress and any unforeseen variables
# that have emerged.    - **Action Plan**:      - Schedule a review meeting
# halfway through the project timeline to assess the progress, resource
# investments, and any technical or administrative issues encountered.      -
# Use this opportunity to adjust the resource allocation strategy if necessary,
# increasing or decreasing investment levels based on the status of the project
# and remaining resources.      - Discuss any patterns of behavior from the
# corporation, such as frequent conservation, and recalibrate your approach
# (e.g., more aggressive heavy investments) if needed.    - **Rationale**: A
# mid-project review allows you to reassess and fine-tune your strategy,
# ensuring that both parties stay aligned and that the project remains on track.
# ---  ### Summary of the Strategy: 1. **Communicate and Build Trust**: Ensure
# both parties are transparent about their resource intentions and establish
# frequent communication channels. 2. **Tit-for-Tat with Flexibility**: Mirror
# the corporation’s actions but occasionally invest heavily to maintain project
# momentum and showcase commitment. 3. **Account for Unforeseen Issues**: Build
# in a buffer for errors and technical glitches to avoid misunderstandings. 4.
# **Incentivize Corporate Investment**: Encourage the corporation to invest by
# demonstrating the benefits and providing recognition. 5. **Set Minimum
# Commitment Levels**: Ensure that some progress is always made, even on days
# when conserving resources. 6. **Mid-Project Review**: Reassess and adjust the
# strategy halfway through to ensure ongoing success.  By following this
# strategy, you create a cooperative framework that encourages mutual
# investment, mitigates risks, and maximizes the project's success without
# depleting your NGO’s limited resources.

# ### Iterated Game Strategy  1. **Start with Cooperation (C)**: On the first
# round, choose to cooperate by playing C to set a tone of trust and
# collaboration.  2. **Tit-for-Tat with Noise Consideration**:     - For each
# subsequent round, mirror your opponent's action from the *previous* round.
# - If your opponent played C in the previous round, play C in the current
# round.    - If your opponent played D in the previous round, play D in the
# current round.  3. **Forgive Occasional Defections**:     - If your opponent
# defects (plays D) after a long sequence of cooperation (at least 5 consecutive
# C plays), forgive this single defection by playing C in the next round. Assume
# it may have been caused by noise.    - If the opponent defects multiple times
# in a row, respond with D until they return to cooperation.  4. **Random Heavy
# Cooperation**:     - Every 30-50 rounds, choose to cooperate (C) regardless of
# what the opponent did in the previous round. This signals goodwill and helps
# maintain long-term cooperation.  5. **Minimum Cooperation Check**:     - If
# both players have defected (played D) for 3 consecutive rounds, break the
# cycle by choosing C in the next round to attempt to re-establish cooperation.
# 6. **Mid-Game Review**:     - After 500 rounds, assess the opponent’s
# behavior.     - If the opponent has primarily cooperated (C at least 70% of
# the time), continue with the Tit-for-Tat strategy.    - If the opponent has
# defected frequently (D more than 50% of the time), switch to playing D
# consistently for the remainder of the game.  7. **End-Game Cooperation**:
# - In the final 10 rounds, regardless of the opponent's actions, always play C
# to leave a positive, cooperative impression and maximize potential future
# collaboration.  This strategy balances cooperation with caution, accounts for
# noise, and introduces occasional cooperation to maintain trust and project
# momentum.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to check if the opponent has cooperated at least 70% of the time
      def opponent_cooperation_rate():
          if len(opponent.history) == 0:
              return 1  # Assume full cooperation if no history
          return opponent.history.cooperations / len(opponent.history)
  
      # Helper function to check if the opponent has defected more than 50% of the time
      def opponent_defection_rate():
          if len(opponent.history) == 0:
              return 0  # Assume no defections if no history
          return opponent.history.defections / len(opponent.history)
  
      # Helper function to check if both players have defected for the last 3 rounds
      def both_defected_last_3_rounds():
          return len(self.history) >= 3 and all(
              self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
              for i in range(1, 4)
          )
  
      # Helper function to check if the opponent defected after a long cooperation streak
      def opponent_defected_after_long_cooperation():
          return len(self.history) >= 6 and all(
              opponent.history[-i] == axl.Action.C for i in range(2, 7)
          ) and opponent.history[-1] == axl.Action.D
  
      # Start with cooperation
      if self.first_round():
          self.mid_game_strategy = None
          return axl.Action.C
  
      # Mid-game review after 500 rounds
      if len(self.history) == 500:
          if opponent_cooperation_rate() >= 0.7:
              self.mid_game_strategy = "tit_for_tat"
          elif opponent_defection_rate() > 0.5:
              self.mid_game_strategy = "always_defect"
          else:
              self.mid_game_strategy = "tit_for_tat"
  
      # If mid-game strategy is set to always defect, defect for the rest of the game
      if self.mid_game_strategy and self.mid_game_strategy == "always_defect":
          return axl.Action.D
  
      # End-game cooperation in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Random heavy cooperation every 30-50 rounds
      if len(self.history) % self._random.randint(30, 50) == 0:
          return axl.Action.C
  
      # Minimum cooperation check: if both defected for 3 consecutive rounds, cooperate
      if both_defected_last_3_rounds():
          return axl.Action.C
  
      # Tit-for-Tat with noise consideration
      if opponent_defected_after_long_cooperation():
          return axl.Action.C  # Forgive a single defection after long cooperation
      else:
          return opponent.history[-1]  # Mirror opponent's last move

# ### High-Level Strategy: **Adaptive Cooperation with Conditional Commitment**
# The goal is to balance maximizing project advancement while protecting your
# NGO's resources. To achieve this, you'll need a strategy that promotes
# cooperation, mitigates risks, and adapts to the corporation's behavior and
# external uncertainties. Here's a step-by-step approach:  ---  ### 1. **Set
# Clear Expectations and Open Communication Channels**    - **Initial
# Agreement:** At the start of the collaboration, establish a mutual
# understanding with the corporation about the importance of both parties
# investing consistently in the project's success. Highlight the risks of
# unilateral investment and the benefits of joint commitment.    - **Daily
# Check-ins:** Implement daily check-ins or progress meetings to ensure
# alignment on each day’s investment plan. This allows for adjustments based on
# any unforeseen circumstances.    - **Transparency:** Encourage transparency
# from both sides on their resource allocation capacity for the day to reduce
# the likelihood of mismatched investments.  ---  ### 2. **Start with Moderate
# Cooperation (Tit-for-Tat with Forgiveness)**    - **Initial Investment:**
# Begin by investing moderately on Day 1, signaling your willingness to
# collaborate but avoiding over-commitment. This ensures you don’t over-invest
# without knowing how the corporation will behave.    - **Match the
# Corporation's Actions:** After Day 1, adopt a "tit-for-tat" approach:      -
# If the corporation invests heavily, respond by also investing heavily the
# following day.      - If the corporation conserves resources, conserve your
# resources the next day.    - **Forgiveness Factor:** Since there may be
# technical glitches or administrative errors, allow for occasional deviations.
# If the corporation conserves resources one day due to an error, give them the
# benefit of the doubt and invest moderately the next day to encourage them to
# return to cooperation.  ---  ### 3. **Introduce a Gradual Investment
# Escalation**    - **Gradual Increase:** If both parties are consistently
# investing heavily over multiple days, you can gradually increase your
# investment to further drive project success. This shows your commitment to the
# project’s long-term goals.    - **Slow Down if Cooperation Falters:** If you
# notice that the corporation begins to conserve resources more frequently, dial
# back your investment to a moderate or low level to protect your NGO's
# resources.  ---  ### 4. **Build a Buffer for Unforeseen Circumstances**    -
# **Reserve Resources:** Always maintain some resource buffer to account for
# days impacted by technical glitches, miscommunication, or external factors.
# This will allow your NGO to continue contributing even when unexpected
# circumstances arise.    - **Flexible Investment Strategy:** If a technical
# glitch or error prevents your NGO from investing as planned, communicate this
# to the corporation and adjust future investments accordingly to rebuild trust
# and cooperation.  ---  ### 5. **Track Progress and Adapt Over Time**    -
# **Monitor Outcomes:** Regularly track the project’s progress and the
# corporation's behavior. If the corporation is consistently under-investing,
# consider renegotiating the terms of partnership or reducing your NGO’s
# involvement to avoid resource depletion.    - **Long-Term Adjustments:** Over
# multiple days, refine your strategy based on the corporation’s patterns. If
# they show a willingness to invest heavily most days, you can afford to invest
# more confidently. If they fluctuate or frequently conserve resources, stay
# cautious and conserve your resources more often.  ---  ### 6. **Exit Strategy
# if Necessary**    - **Minimize Losses if Cooperation Fails:** If it becomes
# clear that the corporation is consistently conserving resources while
# expecting you to invest heavily, be prepared to scale back your involvement
# and possibly exit the project. It's better to conserve your NGO’s resources
# and focus on other opportunities than to drain them in a failing partnership.
# ---  ### Summary of Daily Strategy: - **Day 1:** Moderate investment to signal
# cooperation. - **Day 2 Onward:**   - If the corporation invests heavily,
# reciprocate with heavy investment.   - If the corporation conserves, respond
# by conserving resources the next day.   - Forgive occasional deviations caused
# by errors or glitches, but track patterns over time.   - Adjust investments
# gradually based on the corporation’s consistency and the project’s progress.
# This strategy ensures you're protecting your NGO's resources, fostering
# cooperation, and maximizing the project's success while remaining adaptable to
# external factors beyond your control.

# ### Strategy for the Iterated Normal-Form Game:  1. **Initial Move:**    - In
# the first round, play **C** (Cooperate).  2. **Subsequent Moves:**    - After
# the first round, mirror your opponent’s previous move:      - If your opponent
# played **C** in the previous round, play **C**.      - If your opponent played
# **D** in the previous round, play **D**.  3. **Forgiveness for Noise:**    -
# If your opponent played **D** in the previous round, and you cooperated
# (played **C**) but suspect a noisy action flip (i.e., it seems
# uncharacteristic of your opponent), forgive them by playing **C** in the next
# round. This can occur up to once in every 10 rounds to account for noise.  4.
# **Gradual Escalation:**    - If you and your opponent have both played **C**
# for at least 5 consecutive rounds, continue playing **C** to escalate
# cooperation. This ensures ongoing mutual benefit.  5. **Conserving Resources
# (Defection) After Persistent Defection:**    - If your opponent plays **D**
# for two consecutive rounds, adopt a **D** (Defect) strategy until they return
# to **C**. Once they play **C** again, return to **C** in the next round.  6.
# **Exit Strategy:**    - If your opponent consistently plays **D** for 10
# consecutive rounds, switch permanently to **D** for the remainder of the game
# to protect your score.  ---  This strategy balances cooperation with caution,
# adapts to noise in the game, and encourages mutual benefit while protecting
# against exploitation.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          self.forgiveness_used = 0  # Track forgiveness usage
          self.consecutive_cooperations = 0  # Track consecutive cooperations
          self.consecutive_defections = 0  # Track consecutive defections
          return axl.Action.C
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
      
      # Forgiveness for noise: If opponent defected and we cooperated, forgive once every 10 rounds
      if len(self.history) > 1:
          my_last_move = self.history[-1]
          if opponent_last_move == axl.Action.D and my_last_move == axl.Action.C:
              if self.forgiveness_used < len(self.history) // 10:
                  self.forgiveness_used += 1
                  return axl.Action.C
  
      # Gradual escalation: If both players have cooperated for 5 consecutive rounds, continue cooperating
      if len(self.history) >= 5 and all(
          move == axl.Action.C for move in self.history[-5:]
      ) and all(move == axl.Action.C for move in opponent.history[-5:]):
          return axl.Action.C
  
      # Conserving resources: If opponent defects twice in a row, defect until they cooperate
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # Exit strategy: If opponent defects for 10 consecutive rounds, defect permanently
      if len(opponent.history) >= 10 and all(
          move == axl.Action.D for move in opponent.history[-10:]
      ):
          return axl.Action.D
  
      # Mirror opponent's last move
      return opponent_last_move

# An aggressive strategy to maximise research output while mitigating the risk
# of being exploited by your colleague can be formulated as follows:  ###
# Strategy: **Tit-for-Tat with Aggressive Start**  1. **Week 1 - Share Openly:**
# In the first week, initiate the collaboration by sharing your improvements.
# This establishes goodwill and encourages mutual cooperation. It also provides
# an opportunity to observe your colleague’s response.  2. **Week 2 - Respond in
# Kind:**    - **If your colleague shared in Week 1**, continue sharing openly
# in Week 2. This ensures that both teams benefit from the collaboration and can
# build momentum together.    - **If your colleague kept their findings
# confidential in Week 1**, respond by keeping your findings confidential in
# Week 2. This signals that you will not tolerate one-sided information sharing
# and are willing to retaliate.  3. **Subsequent Weeks - Tit-for-Tat with
# Aggressive Twist:**    - Continue to **mirror your colleague's actions** from
# the previous week. If they shared, you share; if they kept their findings
# confidential, you do the same.    - **However, if your colleague withholds
# information for two consecutive weeks**, assume they are pursuing an
# aggressive, self-serving strategy. In this case, **switch to keeping your
# findings confidential indefinitely**, unless they reinitiate sharing.  4.
# **Factor in Technical Issues:**    - Be aware that communication breakdowns or
# data corruption may occasionally prevent your colleague from sharing, even if
# they intended to. If you suspect a technical issue (e.g., they previously
# shared openly but suddenly stopped without any apparent reason), give them the
# benefit of the doubt for **one week**.    - If the problem persists beyond one
# week, assume their actions are intentional and adjust your strategy
# accordingly by withholding your insights until they demonstrate consistent
# sharing again.  ---  ### Key Points: - **Aggressive Start:** By sharing openly
# in Week 1, you signal a willingness to collaborate while setting a framework
# for reciprocity. - **Tit-for-Tat:** This ensures that you are never too far
# behind if your colleague withholds information, while still allowing
# collaboration when both parties are cooperative. - **Aggressive Retaliation
# After Two Consecutive Defections:** If your colleague repeatedly withholds
# information, you protect your interests by shutting down further sharing
# indefinitely until they demonstrate a willingness to cooperate again. -
# **Technical Flexibility:** Allow some leeway for potential communication or
# technical issues to avoid unnecessary escalation.  This strategy balances the
# need for development progress with the protection of your competitive
# advantage and ensures that any exploitation attempts by your colleague are
# swiftly countered.

# ### Strategy: **Tit-for-Tat with Aggressive Start and Noise Allowance**  1.
# **Round 1: Play C.**    - Always begin by cooperating (playing C) in the first
# round.  2. **Round 2:**    - **If the opponent played C in Round 1, play C.**
# - **If the opponent played D in Round 1, play D.**  3. **Subsequent Rounds
# (Rounds 3 to 1000):**    - **If the opponent played C in the previous round,
# play C.**    - **If the opponent played D in the previous round, play D.**  4.
# **Tolerance for Noise:**    - If the opponent has played C for the last 2
# consecutive rounds, but their most recent move was D, play C (assume the D was
# a result of noise).    - If the opponent has played D for the last 2
# consecutive rounds, play D (assume the opponent has switched to defecting
# intentionally).  ---  In this strategy, cooperation is maintained as long as
# the opponent cooperates. Defection occurs when the opponent defects, but noise
# is accounted for by considering patterns in their recent actions. The strategy
# escalates to defection only when consistent defection is observed.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Round 2: Mirror the opponent's first move
      if len(self.history) == 1:
          return opponent.history[-1]
  
      # Subsequent rounds (Rounds 3 to 1000)
      if len(self.history) >= 3:
          # Check for noise tolerance
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C and opponent.history[-3] == axl.Action.C:
              return axl.Action.C  # Assume the last D was noise, play C
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D  # Opponent is consistently defecting, play D
  
      # Default Tit-for-Tat behavior: mirror the opponent's last move
      return opponent.history[-1]

# Given the dynamics of the mediation process, your strategy should balance
# assertiveness with diplomacy, aiming to secure the most advantageous outcome
# while minimizing risk. The following strategy incorporates flexibility,
# anticipation of miscommunication, and procedural irregularities while
# fostering a cooperative environment where necessary.  ### **1. Establish a
# Cooperative Framework Early On** At the outset of the mediation process,
# convey a sincere interest in finding a mutually beneficial resolution. This
# will establish goodwill with both the arbitrators and opposing counsel. By
# adopting an initial cooperative stance, you create the optics of being the
# reasonable party, which could later play to your advantage should tensions
# escalate.  - **Opening Move:** Begin with a moderately conciliatory proposal
# that addresses some of the core interests of both parties, signaling a
# willingness to work together. This positions you as solution-oriented while
# leaving room for stronger arguments later.   - **Benefit:** This step reduces
# the likelihood of immediately escalating the dispute and sets a tone of
# professionalism. It also puts the arbitrators on notice that you are acting in
# good faith.  ### **2. Reserve Aggression for Strategic Sessions** While your
# goal is to maximize your position by presenting aggressive arguments when your
# opponent is conciliatory, this should be done selectively. Avoid coming across
# as combative in every session, which could alienate the arbitrators. Instead,
# judiciously deploy aggressive arguments when you detect vulnerability in your
# opponent's position or sense that the arbitrators are leaning in your favor.
# - **Timing Aggression:** When you sense that your opponent is beginning to
# yield or is uncertain, pivot to an aggressive stance. Use compelling legal
# arguments and evidence to assert a dominant position. However, avoid personal
# attacks or inflammatory language to maintain the overall cooperative tone.  -
# **Benefit:** This approach minimizes the risk of being perceived as overly
# adversarial, while still allowing you to capitalize on strategic moments when
# an aggressive argument will have the most impact.  ### **3. Adapt to Your
# Opponent’s Approach** Be prepared to flex between conciliatory and assertive
# stances based on your opponent’s behavior. If your opponent consistently
# presents conciliatory proposals, take advantage of this by pressing more
# aggressively in select sessions, while still maintaining a cooperative tone in
# others.  - **Matching Aggression:** If the opposing counsel adopts an
# aggressive stance early on, meet their aggression in the first instance but
# then offer a conciliatory proposal in the following session. This back-and-
# forth approach will keep your opponent off-balance and demonstrate to the
# arbitrators that your side is more interested in resolution than conflict.  -
# **Benefit:** This adaptability ensures that you are not caught flat-footed by
# sudden shifts in strategy by the opposing party, and it demonstrates to the
# arbitrators that you are both firm and fair.  ### **4. Manage Procedural and
# Communication Breakdowns** In any mediation, especially lengthy ones,
# procedural irregularities or miscommunications are likely. You should be
# prepared to address these issues calmly and professionally, without allowing
# them to derail your overall strategy.  - **Clarification and Record-Keeping:**
# Always ensure that your arguments and proposals are clearly articulated and
# well-documented. After each session, request confirmation or summaries of key
# points from the arbitrators to ensure that your position is accurately
# captured. Should any miscommunications occur, seek clarification immediately
# but tactfully, so as to avoid appearing combative.  - **Benefit:** This
# approach ensures that procedural or communication errors are addressed without
# escalating tensions or undermining your credibility with the arbitrators.  ###
# **5. Leverage the Arbitrators’ Role** Throughout the mediation process, be
# mindful that the arbitrators are not just passive observers but active
# participants whose perception of the parties will influence the final outcome.
# Foster a relationship of trust and transparency with the panel by consistently
# presenting well-reasoned, coherent arguments, and by demonstrating flexibility
# when appropriate.  - **Building Rapport:** Engage the arbitrators by
# acknowledging their role in guiding the mediation process and subtly
# incorporating their feedback into your proposals. This will give them a sense
# of ownership over the resolution and make them more likely to view your
# proposals favorably.  - **Benefit:** By aligning yourself with the
# arbitrators, you position your corporation as the party that is more aligned
# with the mediation’s goals, enhancing your credibility and increasing the
# likelihood of a favorable ruling.  ### **6. Anticipate and Exploit Missteps by
# Opponent** Given the long duration and complexity of the mediation, your
# opponent may make occasional errors in judgment, such as overplaying an
# aggressive argument or failing to properly communicate their position. Be
# ready to exploit these missteps without appearing opportunistic.  - **Tactical
# Responses:** If your opponent pushes too hard in an aggressive session,
# respond with a calm, conciliatory proposal that highlights the irrationality
# or extremity of their demands. If they offer a conciliatory proposal that is
# clearly inadequate, respond with a carefully constructed aggressive argument,
# demonstrating why your position is stronger.  - **Benefit:** This approach
# allows you to capitalize on your opponent’s mistakes while maintaining your
# overall strategic posture.  ### **7. Maintain a Long-Term Perspective**
# Throughout the process, keep the long-term outcome in mind. Remember, this is
# a lengthy mediation process, and each session is just one part of a larger
# whole. Avoid the temptation to win every session at the cost of the broader
# relationship or the final resolution.  - **Cumulative Strategy:** Use the
# early and mid-sessions to build a narrative of reasonableness,
# professionalism, and strength. Reserve your most assertive and compelling
# arguments for the latter stages of the mediation when the arbitrators are
# closer to making a final decision, and the groundwork for your case has been
# solidly laid.  - **Benefit:** Maintaining a long-term outlook ensures that you
# don’t expend too much energy or capital in early sessions, saving your
# strongest arguments for when they will have the most impact.  ###
# **Conclusion** Your strategy should be one of calculated adaptability,
# alternating between assertiveness and conciliation depending on the situation.
# By fostering goodwill, maintaining flexibility, and leveraging the dynamics of
# the mediation process, you can position your corporation favorably for a
# resolution that achieves your objectives while minimizing risk.

# ### Iterated Normal-Form Game Strategy  1. **Start with Cooperation (C):** In
# the first round, always play C. This sets a cooperative tone and establishes
# goodwill, indicating a willingness to achieve mutually beneficial outcomes.
# 2. **Tit-for-Tat with Forgiveness:**     - For each subsequent round, mimic
# your opponent's last action. If they played C, play C in the next round. If
# they played D, play D in the next round.    - However, due to noise (e.g.,
# occasional random flips in actions), implement a forgiveness mechanism. If
# your opponent plays D in a round but had been consistently playing C in prior
# rounds, assume that the D was likely due to noise, and continue playing C for
# a few more rounds to give them a chance to return to cooperation.     3.
# **Selective Defection:**     - If your opponent consistently plays D for
# **three consecutive rounds**, switch to playing D in response. This signals
# that you are not willing to be exploited and will defend your position if
# necessary.    - However, after playing D for **two consecutive rounds**,
# return to C to test if your opponent is willing to de-escalate and return to
# cooperation.  4. **Noise Mitigation:** If you play D in response to your
# opponent’s D but suspect noise (e.g., your opponent had been largely
# cooperative before the defection), quickly return to C. Similarly, if you
# intended to play C but inadvertently played D due to noise, continue playing C
# in the following rounds to signal your intent to cooperate.  5. **Long-Term
# Perspective:** Act with the understanding that the game lasts for 1000 rounds.
# Prioritize long-term cooperation over short-term gains. Continue to favor
# cooperation (C) whenever possible, even after occasional defections, as
# maintaining a cooperative equilibrium yields higher cumulative payoffs.  6.
# **Final Stretch (Last 50 Rounds):** As the game nears its end, gradually phase
# in more defections (D) if your opponent has been consistently cooperative.
# This ensures you maximize your final payoffs while mitigating the risk of
# retaliation due to the game’s nearing conclusion.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      FORGIVENESS_THRESHOLD = 3  # Number of rounds to forgive after a defection
      DEFECTION_THRESHOLD = 3    # Number of consecutive defections to trigger retaliation
      RETALIATION_ROUNDS = 2      # Number of rounds to retaliate before testing cooperation
      FINAL_STRETCH = 50          # Last 50 rounds of the game
  
      # Helper function to check if we are in the final stretch of the game
      def in_final_stretch():
          return len(self.history) >= 1000 - FINAL_STRETCH
  
      # Helper function to count opponent's defections in the last N rounds
      def count_recent_defections(n):
          return opponent.history[-n:].count(axl.Action.D)
  
      # Helper function to check if opponent has been mostly cooperative
      def mostly_cooperative():
          return opponent.history.cooperations > opponent.history.defections
  
      # First round: always cooperate
      if self.first_round():
          self.retaliation_count = 0  # Track how many rounds we've retaliated
          self.forgiveness_count = 0  # Track how many rounds we've forgiven after a defection
          return axl.Action.C
  
      # Tit-for-Tat with Forgiveness
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected, check if we should forgive
          if mostly_cooperative() and self.forgiveness_count < FORGIVENESS_THRESHOLD:
              self.forgiveness_count += 1
              return axl.Action.C
          else:
              # Opponent has defected too much, consider retaliation
              self.forgiveness_count = 0
              if count_recent_defections(DEFECTION_THRESHOLD) >= DEFECTION_THRESHOLD:
                  # Opponent has defected for 3 consecutive rounds, retaliate
                  if self.retaliation_count < RETALIATION_ROUNDS:
                      self.retaliation_count += 1
                      return axl.Action.D
                  else:
                      # After 2 rounds of retaliation, test cooperation again
                      self.retaliation_count = 0
                      return axl.Action.C
              else:
                  # Single defection, respond with defection
                  return axl.Action.D
      else:
          # Opponent cooperated, reset forgiveness and retaliation counters
          self.forgiveness_count = 0
          self.retaliation_count = 0
          return axl.Action.C
  
      # Final Stretch: Gradually phase in defections
      if in_final_stretch():
          if self._random.random_choice(0.5):  # Defect with 50% probability in the final stretch
              return axl.Action.D
          else:
              return axl.Action.C

# Given the dynamics of the situation, where both collaboration and conservation
# of resources are important, a balanced and adaptive strategy is essential.
# Here's a high-level, neutral approach that maximizes your NGO's impact while
# accounting for uncertainties and the corporation's potential strategies:  ###
# 1. **Establish Open and Transparent Communication**    - **Initial
# Alignment:** Ensure there is a clear, upfront agreement with the corporation
# about the project's goals, expectations, and each party's resource
# limitations. Transparency will help prevent misunderstandings and build trust.
# - **Daily Check-ins:** Set up daily check-ins or brief reports to discuss the
# prior day's progress and clarify intentions for the current day. This can help
# identify if any unforeseen technical issues or administrative errors occurred,
# enabling both sides to adjust accordingly.  ### 2. **Adopt a Tit-for-Tat
# Strategy with Gradual Investment**    - **Start Conservatively:** On day one,
# conserve your resources but signal a willingness to invest heavily if the
# corporation does the same. This allows you to test the corporation’s initial
# approach without risking too much on the first day.    - **Reciprocal
# Approach:** If the corporation invests heavily on a given day, reciprocate by
# investing heavily the following day. If they conserve resources, do the same.
# This fosters a sense of fairness and partnership while protecting your NGO
# from overcommitting.    - **Adjust Based on Patterns:** If you identify a
# consistent pattern in the corporation’s approach (e.g., they invest heavily
# every other day), adjust your strategy accordingly to either increase or
# decrease your investment on specific days to maximize project impact.  ### 3.
# **Incorporate Flexibility Given Uncertainty**    - **Buffer for Errors:**
# Given that unforeseen circumstances (technical glitches, administrative
# errors) may affect both parties' actions, build in a buffer for your
# investments. For example, on days when you plan to invest heavily, hold back a
# small portion of your resources to account for the possibility that the
# corporation's investment may not go as planned.    - **Contingency Plan:**
# Have a contingency plan in place if unexpected issues arise, such as the
# corporation reporting technical challenges on a given day. For instance, if
# the corporation is unable to invest due to an administrative error, you can
# conserve resources that day and aim to collaborate more effectively the
# following day.  ### 4. **Periodically Reassess and Calibrate**    - **Mid-
# Project Reassessment:** Halfway through the project, conduct a full
# reassessment of progress, investment levels, and alignment with the
# corporation. If the corporation has consistently underinvested or if resource
# allocation has been uneven, propose an adjustment to the strategy to ensure
# the project stays on track.    - **Adjust Investment Levels:** Based on the
# reassessment, adjust your investment approach, either ramping up if there’s
# positive momentum or conserving if there’s stagnation. This ensures that your
# NGO remains responsive and adaptive to the project’s needs.  ### 5. **Promote
# Collaboration and Long-term Impact**    - **Encourage Mutual Investment:**
# Throughout the project, stress the importance of mutual investment for long-
# term project success. Emphasize the collective benefits of both parties
# investing consistently, including positive public relations outcomes for the
# corporation and meaningful environmental impact for both sides.    -
# **Incentivize Heavy Investment:** If possible, offer additional incentives for
# the corporation to invest heavily, such as co-branded media opportunities or
# joint reports highlighting the impact of their investment. This can motivate
# them to contribute more consistently.  ### 6. **Document and Learn for Future
# Projects**    - **Track Resource Allocation:** Keep detailed records of daily
# investments, outcomes, and any technical or administrative issues. This will
# help you analyze patterns and understand the corporation's behavior.    -
# **Post-Project Review:** After the project concludes, conduct a review with
# the corporation to discuss successes, challenges, and areas for improvement.
# Use these insights to refine your strategy for future collaborations.  ###
# Summary of Strategy: 1. **Start conservatively and observe** the corporation's
# behavior on day one. 2. **Adopt a tit-for-tat approach,** investing heavily
# when the corporation does, and conserving when they conserve. 3. **Account for
# unforeseen issues** by maintaining flexibility and holding back a small
# resource buffer during heavy investment days. 4. **Regularly reassess and
# adjust** your strategy based on the corporation’s behavior and technical
# circumstances. 5. **Encourage long-term collaboration** by emphasizing mutual
# benefits and offering incentives for heavy investment.  This strategy promotes
# balance, adaptability, and cooperation while protecting your NGO's resources
# and maximizing the project's success.

# ### Strategy for Iterated Normal-Form Game with Noisy Actions  1. **Start by
# playing D (conserve resources) in the first round.**  2. **Observe the
# opponent’s move.**    - If the opponent plays C (invests heavily), respond by
# playing C in the next round.    - If the opponent plays D (conserves
# resources), continue to play D in the next round.  3. **From round 2 onward,
# reciprocate the opponent’s previous action**:    - If the opponent played C in
# the previous round, play C in the current round.    - If the opponent played D
# in the previous round, play D in the current round.  4. **Account for noise**:
# - If the opponent has played C consistently in the past, but suddenly plays D
# once, treat this as an error. Continue to play C unless the opponent plays D
# for two consecutive rounds.    - If the opponent has played D consistently in
# the past, but suddenly plays C once, treat this as an error. Continue to play
# D unless the opponent plays C for two consecutive rounds.  5. **Mid-game
# reassessment (after 500 rounds)**:    - If the opponent has cooperated more
# than 60% of the time up to this point, switch to playing C consistently to
# build mutual cooperation.    - If the opponent has defected more than 60% of
# the time, switch to playing D consistently to avoid exploitation.  6. **End-
# game strategy (final 100 rounds)**:    - If cooperation has been frequent
# (more than 60% C from both sides), continue playing C.    - If defection has
# been frequent (more than 60% D from either side), switch to playing D for the
# remainder of the rounds.  7. **Document and adapt for future games**:    -
# Record the opponent’s behavior throughout the game and use these insights to
# adjust future strategies in similar situations.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      MID_GAME_ROUND = 500
      END_GAME_ROUND = 900
      COOP_THRESHOLD = 0.6
  
      # First round: play D
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.mid_game_strategy = None
          return axl.Action.D
  
      # Helper function to calculate cooperation ratio
      def cooperation_ratio(player):
          total_moves = len(player.history)
          if total_moves == 0:
              return 0
          return player.history.cooperations / total_moves
  
      # Get the last move of the opponent
      last_opponent_move = opponent.history[-1]
  
      # Track consecutive cooperations and defections
      if last_opponent_move == axl.Action.C:
          self.consecutive_cooperations += 1
          self.consecutive_defections = 0
      else:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
  
      # Mid-game reassessment after 500 rounds
      if len(self.history) == MID_GAME_ROUND:
          if cooperation_ratio(opponent) > COOP_THRESHOLD:
              self.mid_game_strategy = axl.Action.C
          else:
              self.mid_game_strategy = axl.Action.D
  
      # End-game strategy after 900 rounds
      if len(self.history) >= END_GAME_ROUND:
          if cooperation_ratio(self) > COOP_THRESHOLD and cooperation_ratio(opponent) > COOP_THRESHOLD:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If mid-game strategy has been set, follow it
      if self.mid_game_strategy is not None:
          return self.mid_game_strategy
  
      # Reciprocate opponent's last move, accounting for noise
      if self.consecutive_cooperations >= 2:
          return axl.Action.C
      elif self.consecutive_defections >= 2:
          return axl.Action.D
      else:
          return last_opponent_move

# ### High-Level Strategy: **Conditional Cooperation with Tactical Aggression**
# Your goal is to maximize the project's success while conserving your NGO's
# resources as much as possible. However, given the uncertainties in execution,
# you need a strategy that blends flexibility, cooperation, and a calculated
# level of assertiveness.  #### **Strategy Outline:**  1. **Day 1 - Establish
# Trust with Initial Cooperation:**    - Start by **investing heavily** on the
# first day. This signals goodwill and commitment to the project while
# encouraging the corporation to reciprocate.    - By doing this, you establish
# a baseline of cooperation and demonstrate that you are serious about advancing
# the project.  2. **Day 2 - Evaluate and Respond Based on the Corporation’s
# Behavior:**    - **If the corporation also invested heavily on Day 1**,
# continue to invest heavily on Day 2. This reinforces the cooperation and keeps
# the project momentum high.    - **If the corporation conserved resources on
# Day 1**, **conserve resources** on Day 2. This sends a clear message that you
# won’t overextend yourself if the corporation doesn't contribute fairly.     3.
# **Day 3 and Beyond - Conditional Cooperation (Tit-for-Tat with Tactical
# Aggression):**    - **Mirror the corporation’s previous behavior**:       - If
# they invested heavily on the previous day, you continue to invest (cooperate).
# - If they conserved resources, you conserve on the next day (retaliate).    -
# This **tit-for-tat** strategy ensures that you don’t get taken advantage of
# while maintaining the potential for cooperation.    - **Tactical Aggression**:
# On every **third consecutive day of mutual conservation**, break the cycle by
# investing heavily again. This serves as a signal to the corporation that you
# are still committed to the project’s success and are willing to restart
# cooperation if they are.  4. **Account for Unforeseen Circumstances:**    -
# Since there’s a chance that technical glitches or administrative errors may
# interfere with resource allocation, **don’t immediately change your strategy**
# after a single unexpected outcome.    - If you suspect the corporation’s non-
# investment was due to an error (e.g., an internal issue), **skip one
# retaliation day** and give them the benefit of the doubt by investing heavily
# again.    - If the pattern of non-investment persists for more than two days,
# assume intentional conservation and proceed with the tit-for-tat strategy.  5.
# **Final Days - Aggressive Push for Project Completion:**    - In the final two
# days of the project, **invest heavily regardless of the corporation’s
# behavior**. This ensures that you maximize the project’s success before it
# concludes, even if it means depleting more of your resources.    - This
# aggressive final push demonstrates long-term commitment and may encourage
# last-minute cooperation from the corporation to finish the project strongly.
# #### **Risk Management Considerations:**  - **Resource Buffer**: Always keep a
# mental tally of your NGO’s remaining resources. If depletion is imminent,
# prioritize conservation to avoid draining your funds entirely.    -
# **Communication**: Throughout the project, maintain clear and transparent
# communication with the corporation. This builds trust and reduces the
# likelihood of misunderstandings due to unforeseen circumstances.  -
# **Adaptability**: Remain flexible; if the corporation significantly shifts
# strategy mid-project (e.g., suddenly investing heavily after a long period of
# conservation), be prepared to adjust the tit-for-tat approach to re-establish
# cooperation.  By employing this strategy, you demonstrate a willingness to
# cooperate but also protect your NGO from exploitation, ensuring that you
# maximize the project's impact while conserving your resources.

# ### Iterated Normal-Form Game Strategy  1. **Round 1 - Cooperate (C):**    -
# In the first round, choose to cooperate. This sets the stage for potential
# collaboration and signals a willingness to invest in the project.  2. **Round
# 2 - Conditional Response:**    - **If the opponent played C in Round 1**,
# cooperate (C) in Round 2.    - **If the opponent played D in Round 1**, defect
# (D) in Round 2.  3. **Rounds 3 to 1000 - Conditional Cooperation (Tit-for-Tat
# with Occasional Defection):**    - **If the opponent played C in the previous
# round**, cooperate (C) in the current round.    - **If the opponent played D
# in the previous round**, defect (D) in the current round.  4. **Handling Noise
# (when your action or the opponent's action is accidentally flipped):**    - If
# you suspect that the opponent’s defection was due to noise (e.g., after a long
# streak of consistent cooperation), **forgive a single defection and cooperate
# (C)** in the next round.    - If the opponent defects again in the following
# round, assume their defection was intentional and proceed with the tit-for-tat
# pattern (defect in response to their defection).  5. **Dealing with Mutual
# Defection:**    - **If both you and the opponent have defected for three
# consecutive rounds**, break the cycle by cooperating (C) on the fourth round.
# This signals an attempt to reset cooperation.  6. **Final 10 Rounds -
# Aggressive Cooperation:**    - Regardless of the opponent’s actions in the
# previous rounds, **cooperate (C) in all of the final 10 rounds**. This
# maximizes potential gains at the end of the game and demonstrates long-term
# commitment to cooperation.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1 - Cooperate
      if self.first_round():
          self.defection_streak = 0  # Track mutual defection streaks
          return axl.Action.C
  
      # Round 2 - Conditional Response
      if len(self.history) == 1:
          if opponent.history[0] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Final 10 Rounds - Aggressive Cooperation
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Rounds 3 to 1000 - Conditional Cooperation (Tit-for-Tat with Occasional Defection)
      if len(self.history) > 1:
          # Check for mutual defection streak
          if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
              self.defection_streak += 1
          else:
              self.defection_streak = 0
  
          # Break mutual defection cycle after 3 consecutive defections
          if self.defection_streak >= 3:
              return axl.Action.C
  
          # Tit-for-Tat: Respond to opponent's last move
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              # Handle noise: Forgive a single defection after a long cooperation streak
              if opponent.history[-2] == axl.Action.C and self.history[-2] == axl.Action.C:
                  return axl.Action.C
              return axl.Action.D

# To maximise research output and foster a cooperative working relationship over
# the multi-week collaboration, it's essential to develop a strategy that
# incentivises both parties to share information while being resilient to
# potential communication breakdowns or technical issues. Here's a high-level
# strategy:  ### 1. **Start by Sharing Openly**   In the first week, share your
# findings openly and without hesitation. This sets a cooperative tone and
# builds trust. It signals to your colleague that you are willing to collaborate
# and work towards mutual progress.  ### 2. **Tit-for-Tat with Forgiveness**
# After the first week, adopt a modified "Tit-for-Tat" strategy, which works as
# follows:    - **If your colleague shares openly:** Continue to share openly
# the next week.    - **If your colleague keeps findings confidential:** Keep
# your findings confidential in the subsequent week as a response.    -
# **Forgiveness mechanism:** Given the possibility of technical issues, if your
# colleague fails to share once or twice, assume an error occurred rather than a
# deliberate choice. Wait for a pattern (e.g., two consecutive weeks of non-
# sharing) before switching to keeping your findings confidential.  ### 3.
# **Monitor Long-Term Patterns**   Throughout the multi-week project, pay
# attention to long-term trends rather than reacting to single-week deviations.
# If your colleague consistently fails to share after 2-3 weeks, consider
# switching to a more defensive stance (keeping your findings confidential)
# until they return to sharing.  ### 4. **Recalibrate Mid-Project**   At the
# halfway point of the project, initiate a conversation with your colleague to
# recalibrate expectations. Discuss any miscommunications or technical issues
# that may have occurred and emphasise the mutual benefits of sharing. This
# helps realign incentives and ensures both parties are still committed to open
# sharing.  ### 5. **Be Transparent About Technical Issues**   If you encounter
# technical issues that prevent you from sharing, be proactive in communicating
# this to your colleague. This maintains trust and reduces the likelihood of
# them interpreting your non-sharing as deliberate.  ### 6. **Maintain
# Flexibility**   Remain flexible in your approach. If you notice your colleague
# is consistently cooperative, you can be more lenient in your sharing, even in
# the face of minor technical disruptions. If they become more secretive, adjust
# your strategy accordingly, but always leave the door open for cooperation to
# resume.  ---  ### Summary of Strategy: - **Week 1:** Share openly to build
# trust. - **Subsequent weeks:** Use a **Tit-for-Tat** approach with a
# **forgiveness mechanism** for potential technical issues. - **Mid-project
# discussion:** Reassess and recalibrate the strategy halfway through the
# project to ensure mutual understanding. - **Adaptability:** Be flexible and
# responsive to long-term patterns rather than reacting to isolated incidents.
# This strategy balances cooperation with protection and accounts for the
# possibility of technical issues without immediately penalising your colleague.
# It fosters an environment conducive to shared progress while still
# safeguarding your own interests.

# ### Strategy for Iterated Normal-Form Game (1000 Rounds with Noisy Actions)
# 1. **Initial Round (Round 1):**      Play **C** (Cooperate).  2. **Subsequent
# Rounds (Rounds 2–1000):**      In each round, follow these rules in order:
# a. **If your opponent played C in the previous round:**         Play **C**
# (Cooperate) in the current round.     b. **If your opponent played D in the
# previous round:**         Play **D** (Defect) in the current round.     c.
# **Forgiveness Rule:**         If your opponent played D in the previous round
# but played C in the two rounds before that, play **C** (Cooperate) in the
# current round. This assumes their previous defection may have been caused by
# noise.  3. **Mid-Game Adjustment (after Round 500):**      At Round 500,
# evaluate your opponent’s overall behavior:     - **If your opponent has mostly
# played C (at least 70% of the time):**        Continue following the rules
# above.        - **If your opponent has mostly played D (more than 30% of the
# time):**        Play **D** (Defect) for the remaining rounds.  4. **Technical
# Issue Assumption (Noisy Actions):**      Always assume that up to two
# consecutive defections by your opponent could be due to noise. Only switch to
# playing D consistently if your opponent defects for three or more consecutive
# rounds.  ---  This formulation should guide cooperation while safeguarding
# against exploitation, with flexibility for noise in the opponent's actions.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if opponent defected for 3 or more consecutive rounds
      def opponent_defected_three_consecutive():
          return len(opponent.history) >= 3 and all(
              move == axl.Action.D for move in opponent.history[-3:]
          )
  
      # Helper function to check if opponent defected last round but cooperated in the two rounds before that
      def forgiveness_condition():
          return (
              len(opponent.history) >= 3
              and opponent.history[-1] == axl.Action.D
              and opponent.history[-2] == axl.Action.C
              and opponent.history[-3] == axl.Action.C
          )
  
      # Mid-game adjustment after round 500
      if len(self.history) == 500:
          opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_cooperation_rate < 0.7:
              self.play_defect_after_500 = True
          else:
              self.play_defect_after_500 = False
  
      # If after round 500 and opponent has mostly defected, always defect
      if len(self.history) > 500 and getattr(self, 'play_defect_after_500', False):
          return axl.Action.D
  
      # Forgiveness rule: if opponent defected last round but cooperated in the two rounds before that
      if forgiveness_condition():
          return axl.Action.C
  
      # If opponent defected for 3 or more consecutive rounds, defect
      if opponent_defected_three_consecutive():
          return axl.Action.D
  
      # If opponent defected last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If opponent cooperated last round, cooperate
      return axl.Action.C

# ### High-Level Strategy for Mediation Sessions  The mediation process you’re
# engaged in requires a carefully calibrated approach to balance assertiveness
# with collaboration, all while remaining adaptable to communication challenges
# and potential misinterpretations. Below is a sophisticated, neutral strategy
# designed to maximize your corporation's positioning:  #### 1. **Assess Each
# Session's Context and Opponent's Behavior**    - **Initial Sessions: Establish
# a Cooperative Tone**      In the early stages, prioritize setting a
# collaborative and solution-oriented tone by starting with **conciliatory
# proposals**. This will lay a foundation of goodwill with both the arbitrators
# and your opponent, and it signals your commitment to the process. Assess how
# your opponent responds: do they reciprocate with conciliation, or do they
# adopt an aggressive stance?          - **Monitor Shifts in Approach**
# Continuously analyze your opponent’s changing tactics throughout the
# mediation. If they consistently adopt aggressive arguments, adjust your
# approach accordingly in later sessions to protect your position.  #### 2.
# **Mixed Strategy: Alternate Between Conciliatory and Aggressive**    -
# **Balance Aggressive and Conciliatory Approaches**      Alternate between
# aggressive arguments and conciliatory proposals based on the session’s
# dynamics. For example, after sessions where both parties have presented
# conciliatory proposals, introduce an **aggressive argument** next, aiming to
# shift momentum in your favor. However, avoid two consecutive aggressive
# arguments unless absolutely necessary, as this may escalate tensions and risk
# alienating the arbitrators.     - **Strategic Aggression**      When employing
# an aggressive argument, do so with tact and precision. Avoid blanket attacks
# or overly adversarial postures that might backfire. Instead, frame your
# aggressive stance as **principled advocacy**—emphasizing fairness, legal
# precedent, or your corporation’s long-term interests without appearing
# combative.  #### 3. **Maintain Flexibility: Respond to Opponent’s Missteps**
# - **Adjust for Miscommunications or Misunderstandings**      Given the
# possibility of misrepresentation or communication breakdowns, anticipate that
# both your arguments and your opponent’s may be misunderstood by the
# arbitrators at some point. If such a breakdown occurs, calmly request
# clarification or a restatement of positions. Use these moments to **reiterate
# key points** without appearing defensive.          - **Capitalize on
# Opponent's Errors**      If your opponent’s arguments are misrepresented or
# misunderstood, subtly highlight inconsistencies or gaps in their logic,
# positioning your corporation as the more organized and credible party. Avoid
# directly attacking their misstep, as this could backfire; instead, gently
# steer the conversation back to your strengths.  #### 4. **Preemptive Framing
# of Arguments**    - **Set the Narrative Early**      Before entering any
# session, clearly outline your key themes and objectives to the arbitrators.
# Use each session to subtly reinforce your corporation’s narrative by anchoring
# your arguments in **mutual goals** (e.g., long-term business cooperation,
# market stability). This framing will make it harder for your opponent to
# undermine your position, even if they adopt an aggressive stance.     - **Use
# Conditional Offers**      When offering conciliatory proposals, make them
# **conditional** upon the opponent’s reciprocal actions. This prevents your
# corporation from appearing weak or pliable, ensuring that any concessions are
# balanced by corresponding gains.  #### 5. **Neutralize Aggression: Turn
# Adversity into Collaboration**    - **Respond to Aggression with Measured
# Diplomacy**      When your opponent presents aggressive arguments, don’t react
# with reflexive aggression. Instead, respond with **measured diplomacy**,
# pointing out that your corporation remains committed to finding a constructive
# solution. This will portray you as the more reasonable party, potentially
# drawing favor with the arbitrators.     - **Escalate Only When Necessary**
# If your opponent’s aggression becomes increasingly hostile or undermines your
# corporation's position, you may need to escalate with a well-calculated,
# aggressive counterargument. However, avoid allowing the sessions to devolve
# into a tit-for-tat exchange. Frame your escalation within the bounds of
# fairness and necessity, and return to conciliation as soon as possible.  ####
# 6. **Endgame: Position for a Favorable Resolution**    - **Pivot Toward
# Settlement as the Process Progresses**      As the mediation process nears its
# conclusion, gradually shift towards **settlement-oriented proposals**. By this
# stage, both parties may be fatigued from the lengthy process, and the
# arbitrators will likely prefer a resolution. Use this to your advantage by
# positioning your corporation as the party most willing to finalize a fair and
# mutually beneficial agreement.          - **Keep Open the Option of Aggressive
# Stance in Final Sessions**      If the opponent continues to hold out or
# escalate aggression, be prepared to reintroduce an aggressive argument in the
# final sessions to force a concession. However, this should be done in a way
# that maintains the appearance of fairness and avoids alienating the
# arbitrators.  ### Contingency for Procedural Irregularities: - **Document
# Everything**    Keep meticulous records of every session, including arguments
# presented and responses received. If a procedural irregularity arises, such as
# the misrepresentation of your position, you’ll have clear documentation to
# refer to and correct the record.     - **Request Clarifications
# Diplomatically**    If there is a communication breakdown or misunderstanding,
# make your request for clarification appear neutral and non-confrontational.
# This will show the arbitrators that your corporation prioritizes transparency
# and accuracy.  By adopting this balanced, adaptable strategy, your corporation
# will maintain the flexibility to respond to a wide range of opponent tactics
# and procedural challenges. The goal is not only to secure the best possible
# outcome in each session but also to position your corporation as a credible,
# reasonable, and solutions-oriented party in the eyes of the arbitrators.

# ### Strategy for the Iterated Normal-Form Game  1. **Begin by Cooperating
# (C):**    - In the first round, choose **Cooperate (C)** to establish a
# collaborative tone with your opponent.  2. **Cooperate (C) if Both Players
# Cooperated in the Previous Round:**    - If both you and your opponent played
# **Cooperate (C)** in the previous round, continue to **Cooperate (C)** in the
# next round to maintain a mutually beneficial outcome.  3. **Defect (D) if You
# Cooperated and Your Opponent Defected in the Previous Round:**    - If you
# played **Cooperate (C)** but your opponent played **Defect (D)** in the
# previous round, switch to **Defect (D)** in the next round to protect yourself
# and signal that aggressive moves will not go unchallenged.  4. **Cooperate (C)
# Again if Your Opponent Returns to Cooperation After Defection:**    - If your
# opponent defected in a previous round but returns to **Cooperate (C)** in the
# most recent round, respond by playing **Cooperate (C)** in the next round to
# encourage a return to collaboration.  5. **Defect (D) if Both You and Your
# Opponent Defected in the Previous Round:**    - If both you and your opponent
# played **Defect (D)** in the previous round, continue to **Defect (D)** in the
# next round to avoid being taken advantage of.  6. **Defect (D) if Your
# Opponent Defected Twice in a Row:**    - If your opponent defects for two
# consecutive rounds, continue to **Defect (D)** until they return to
# cooperation. This reinforces the message that sustained aggression will be met
# with continued defection.  7. **Cooperate (C) if Miscommunication is Suspected
# (Noise):**    - If there seems to be an unusual deviation (e.g., your opponent
# suddenly defects after a long stretch of cooperation), consider the
# possibility of noise causing an unintended defection. In this case,
# **Cooperate (C)** in the next round to test whether the defection was
# accidental.  8. **Return to Cooperation (C) After a Series of Defections if
# Your Opponent Signals Cooperation:**    - After several rounds of mutual
# defection, if your opponent signals a return to **Cooperate (C)**, reciprocate
# with **Cooperate (C)** to explore the possibility of rebuilding a cooperative
# dynamic.  9. **Endgame Strategy: Cooperate (C) More Frequently in the Final
# Rounds:**    - In the last 50-100 rounds, lean towards playing **Cooperate
# (C)** more frequently, even if your opponent has defected recently. This
# increases the potential for mutual benefit as the game draws to a close and
# reduces the risk of prolonged defection.  This strategy balances cooperation
# and defection based on the opponent’s behavior, allowing for adaptability to
# both aggressive and conciliatory opponents, while being mindful of the
# possibility of noise in the game.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Subfunction to check if there was a sudden defection after a long cooperation
      def miscommunication_suspected():
          if len(self.history) > 1:
              # Check if opponent defected after a long stretch of cooperation
              if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
                  # Check if the opponent had been cooperating for a long time before the defection
                  return opponent.history[:-2].count(axl.Action.D) == 0
          return False
  
      # Subfunction to check if we are in the final rounds
      def in_final_rounds():
          return len(self.history) >= 900  # Last 100 rounds of a 1000 round game
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # If both players cooperated in the previous round, cooperate
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If I cooperated and the opponent defected in the previous round, defect
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent defected but returned to cooperation, cooperate
      if len(self.history) > 1 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.D:
          return axl.Action.C
  
      # If both players defected in the previous round, defect
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If the opponent defected twice in a row, defect
      if len(self.history) > 1 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # If miscommunication is suspected, cooperate
      if miscommunication_suspected():
          return axl.Action.C
  
      # Endgame strategy: Cooperate more frequently in the final rounds
      if in_final_rounds():
          return self._random.random_choice(0.8)  # Cooperate with 80% probability
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# ### Aggressive Strategy for Bilateral Trade Negotiations  #### Objective:
# Maximize your country’s economic advantage by aiming for protectionist
# policies while the counterpart offers free trade. However, you must also
# mitigate risks and adapt to potential miscommunications or unexpected shifts
# in your counterpart’s strategy.  ### Key Principles:  1. **Initial Aggression
# (Round 1)**: Start with a **protectionist policy** to signal strength and test
# your counterpart’s immediate response. This establishes a baseline of caution
# and sets a tone that you are willing to defend your national interests.  2.
# **Tit-for-Tat with Retaliatory Escalation**: Adopt a **tit-for-tat** strategy
# with a twist. Respond to your counterpart’s choices based on the previous
# round, but escalate **aggressively** if they impose protectionist measures:
# - If they offer **free trade**, continue with **protectionist policies** to
# gain an advantage.     - If they impose **protectionist measures**, respond in
# kind, but escalate by proposing **harsher tariffs or more restrictive quotas**
# in the following round. This shows that you will not tolerate protectionism
# from their side without consequences.      3. **Occasional Free Trade
# (Strategic Reset)**: Periodically (every 3-4 rounds), offer **free trade** as
# a strategic reset to reduce tensions and maintain the possibility of mutual
# cooperation. This also serves to test whether your counterpart is open to
# cooperation or whether they are entrenched in protectionist policies.     - If
# they match your free trade offer, you can de-escalate for mutual benefit.
# - If they impose protectionist measures while you offer free trade,
# immediately return to an aggressive protectionist stance in the next round.
# 4. **Exploit Miscommunication/Bureaucratic Errors**: Be ready to exploit any
# **miscommunications or implementation errors** by your counterpart. If they
# accidentally offer free trade while you intended to impose protectionist
# measures, do not correct or highlight the error. Instead, take advantage of it
# and maximize short-term gains for your country.  5. **Maintain Flexibility**:
# While aggression is the foundation, remain flexible. If you observe consistent
# free trade offers from your counterpart, consider easing your stance slightly
# by proposing **moderate protectionism** (e.g., lower tariffs) to maintain a
# cooperative spirit while still protecting your domestic industries.  6.
# **Final Rounds – Secure Maximum Gains**: In the final rounds of negotiations,
# aim to solidify a **protectionist stance**. These rounds are crucial for long-
# term impact, so ensure that your country exits negotiations with as much
# protection as possible. Use the uncertainty of the final rounds to your
# advantage by offering **last-minute protectionist policies**, as your
# counterpart may avoid escalating before the talks conclude.  ### Summary of
# Strategy:  1. **Round 1**: Start protectionist. 2. **Rounds 2-3**: Tit-for-tat
# with escalation for protectionism. 3. **Round 4**: Offer free trade as a
# strategic reset (if possible). 4. **Round 5 and beyond**: Continue tit-for-
# tat, but escalate if necessary, and solidify protectionism in final rounds.
# ### Risk Mitigation: - **Miscommunication Errors**: Be prepared to capitalize
# on any bureaucratic errors by your counterpart. If they mistakenly offer free
# trade, proceed with protectionism. - **Adaptability**: If your counterpart
# consistently offers free trade and shows no aggressive tendencies, consider a
# softer approach to avoid long-term mutual harm.  By balancing aggression with
# occasional resets, you can maximize gains while avoiding prolonged conflict,
# ensuring your country comes out ahead in the majority of rounds.

# ### Iterated Game Strategy (1000 Rounds)  1. **Initial Move (Round 1)**:     -
# Play **D** (Defect).  2. **Tit-for-Tat with Escalation (Rounds 2-1000)**:    -
# On each round, observe your opponent's previous action.    - **If they played
# C (Cooperate)** in the prior round, play **D** (Defect) in the current round.
# - **If they played D (Defect)** in the prior round, play **D** (Defect) as
# well, but continue to do so for **two additional rounds** to escalate the
# retaliation.  3. **Strategic Reset (every 100 rounds)**:    - On rounds 100,
# 200, 300, ..., 900, play **C** (Cooperate) regardless of the opponent’s
# previous action.    - After playing **C** on these rounds, return to the
# regular tit-for-tat with escalation strategy in the following rounds.  4.
# **Handling Noisy Actions**:    - If the opponent **played D** in the previous
# round, but **played C** in the two rounds before that, assume the **D** was
# due to noise and **play C** (Cooperate) instead of escalating.    - If the
# opponent **played C** in the previous round, but they had consistently played
# **D** in the previous two or more rounds, assume the **C** was due to noise
# and **play D** (Defect) to maintain pressure.  5. **Final Rounds (Rounds
# 990-1000)**:    - In the last 10 rounds, **always play D** (Defect),
# regardless of the opponent’s actions, to maximize end-game gains.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
  
      # Round 1: Always play D
      if self.first_round():
          return DEFECT
  
      # Final 10 rounds: Always play D
      if len(self.history) >= 990:
          return DEFECT
  
      # Strategic reset every 100 rounds
      if len(self.history) % 100 == 0:
          return COOPERATE
  
      # Tit-for-tat with escalation
      def tit_for_tat_with_escalation():
          # Get opponent's last move
          last_opponent_move = opponent.history[-1]
  
          # Handle noisy actions
          if last_opponent_move == DEFECT and len(opponent.history) >= 3:
              if opponent.history[-2] == COOPERATE and opponent.history[-3] == COOPERATE:
                  return COOPERATE  # Assume noise, play C
          if last_opponent_move == COOPERATE and len(opponent.history) >= 3:
              if opponent.history[-2] == DEFECT and opponent.history[-3] == DEFECT:
                  return DEFECT  # Assume noise, play D
  
          # Escalation logic
          if last_opponent_move == DEFECT:
              # Check if we are in the middle of an escalation
              if len(self.history) >= 3 and self.history[-1] == DEFECT and self.history[-2] == DEFECT:
                  return DEFECT  # Continue escalation
              return DEFECT  # Start escalation
          else:
              return DEFECT  # Opponent played C, we play D
  
      return tit_for_tat_with_escalation()

# To navigate this complex negotiation environment, a cooperative yet cautious
# strategy that accounts for potential miscommunication and varying approaches
# from your counterpart is essential. Below is a high-level strategy that
# emphasizes cooperation while protecting your country from potential
# exploitation:  ### **Tit-for-Tat with Leniency and Gradualism**  This strategy
# is based on the classic "Tit-for-Tat" approach but incorporates leniency and
# gradual escalation to account for miscommunications or errors. The goal is to
# encourage mutual cooperation (free trade) while safeguarding against potential
# exploitation (unilateral protectionism) and ensuring that small mistakes or
# misunderstandings do not escalate into an unproductive trade war.  #### **1.
# Begin with a Cooperative Gesture (Free Trade)** - **Round 1**: Start by
# offering a free trade agreement. This signals to your counterpart that you are
# willing to cooperate in good faith and prefer mutual benefits. - This also
# sets a positive tone for the negotiations and encourages reciprocity from the
# other side.  #### **2. Monitor Responses and React Accordingly** - **Round 2
# and Beyond**: Observe how your counterpart responds in each round. There are
# four possible outcomes in every round, and your reactions should differ based
# on these:    - **If they offer free trade** (both countries benefit): Continue
# proposing free trade agreements. This builds trust and ensures long-term
# economic gains for both sides.      - **If they propose protectionism** (your
# country is disadvantaged): In the next round, respond with a **protectionist
# policy**. This is the core of the tit-for-tat strategy—responding in kind to
# discourage further exploitation.      - **If both sides propose
# protectionism** (mutual harm): Consider offering **free trade** again in the
# next round, signaling your willingness to return to cooperation. This
# encourages your counterpart to also de-escalate.    #### **3. Introduce
# Leniency (Allow for One Mistake)** - Given the possibility of miscommunication
# or bureaucratic errors, allow for **one round of leniency** if the counterpart
# unexpectedly imposes protectionist measures.   - If they propose protectionism
# once (especially after a history of cooperation), assume it could be an error
# and continue to propose free trade for **one more round**. This leniency
# prevents a single mistake from derailing the cooperative relationship.   - If
# protectionism continues beyond one round, switch to protectionism yourself
# until cooperation resumes.  #### **4. Gradual Escalation** - If the other
# country continues to impose protectionist measures for multiple consecutive
# rounds (more than 2 rounds), gradually escalate your protectionist policies
# (e.g., starting with mild tariffs or quotas and increasing them
# incrementally). This avoids a sudden trade war while signaling a willingness
# to defend your country's interests.   - **Aim for proportional responses**
# rather than drastic measures. This keeps the door open for future cooperation.
# #### **5. Open Channels for Clarification and De-escalation** - At the start
# of each round, initiate bilateral communications to clarify your intentions
# and ensure policies are correctly understood. This can help reduce the
# likelihood of misinterpretation and foster a constructive atmosphere. - If
# tensions rise (mutual protectionism), propose a diplomatic meeting to reassess
# and find a path back to free trade.  #### **6. Be Ready to Reset if
# Necessary** - After a long period of mutual protectionism or failed
# negotiations, propose a "reset" by offering free trade again. This shows a
# willingness to let go of the past and return to a mutually beneficial
# relationship.  ---  ### **Summary of the Strategy:** 1. **Start with
# cooperation** (free trade) and encourage reciprocity. 2. **Mirror your
# counterpart's actions**: If they cooperate, continue cooperating; if they
# impose protectionism, respond with protectionism but with a delay to account
# for possible errors. 3. **Allow one round of leniency** to account for
# bureaucratic or miscommunication errors. 4. **Escalate gradually** if
# protectionism persists, but avoid drastic measures that could lead to an
# entrenched trade conflict. 5. **Maintain open channels for communication** to
# clarify intentions and avoid misunderstandings. 6. **Be prepared to reset
# negotiations** to free trade if both sides fall into a pattern of
# protectionism.  This approach maximizes the chances of achieving a
# cooperative, mutually beneficial outcome while protecting your country from
# long-term exploitation or economic disadvantage across multiple rounds of
# negotiations.

# ### Iterated Game Strategy: Tit-for-Tat with Leniency and Gradual Escalation
# 1. **Start by Cooperating**:    - In the first round, choose **Cooperate
# (C)**.  2. **Mirror Your Opponent's Previous Move**:    - In each subsequent
# round, do the same action your opponent did in the previous round:      - If
# they cooperated (C), you cooperate (C).      - If they defected (D), you
# defect (D).  3. **Allow One Mistake**:    - If your opponent defects (D)
# **once** after a history of cooperation, **continue cooperating (C) for one
# more round**.     - If they cooperate again in the next round, resume mutual
# cooperation (C).    - If they defect again in the next round, begin defecting
# (D) in response.  4. **Gradually Escalate Defection**:    - If your opponent
# defects for **two or more consecutive rounds**:      - Defect (D) in response,
# but continue to mirror their actions.      - If they resume cooperation (C),
# immediately return to cooperating (C).  5. **Reset to Cooperation After
# Extended Defection**:    - After **five consecutive rounds of mutual defection
# (D)**, unilaterally return to cooperation (C) to signal a willingness to reset
# the relationship.    - If they respond by cooperating (C), continue
# cooperating (C).    - If they defect (D) again, return to defecting (D) and
# mirror their moves as before.  This strategy encourages cooperation, tolerates
# occasional mistakes, and escalates cautiously if defection persists.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.allowed_mistake = True  # Allow one mistake initially
          return axl.Action.C
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If opponent cooperated last round, reset defection count and cooperate
      if opponent_last_move == axl.Action.C:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # If opponent defected last round
      if opponent_last_move == axl.Action.D:
          # Check if this is the first defection after a history of cooperation
          if self.allowed_mistake:
              self.allowed_mistake = False  # Allow one mistake, continue cooperating
              return axl.Action.C
  
          # If opponent defected for two or more consecutive rounds
          self.consecutive_defections += 1
  
          # If there have been 5 consecutive defections, reset to cooperation
          if self.consecutive_defections >= 5:
              self.consecutive_defections = 0  # Reset defection count
              self.allowed_mistake = True  # Reset mistake allowance
              return axl.Action.C
  
          # Otherwise, defect in response
          return axl.Action.D

# Given the multi-week nature of the collaboration, the possibility of
# miscommunication, and the need to maximize your research output, the strategy
# you adopt should balance cooperation and caution. Here's a high-level, neutral
# approach designed to encourage mutual progress while protecting against
# exploitation.  ### Strategy: **Tit-for-Tat with Forgiveness**  1. **Week 1:
# Start by Sharing Openly**      Begin the collaboration on a positive note by
# openly sharing your latest improvements. This signals goodwill and encourages
# reciprocal sharing from your colleague. Since both sharing openly is the
# second-best outcome, this sets the tone for mutual progress.  2. **Subsequent
# Weeks: Mirror Your Colleague’s Previous Action**      For each week after the
# first, match your colleague's previous week's action:    - If they shared
# openly last week, share openly this week.    - If they kept their information
# confidential last week, keep your information confidential this week.     This
# encourages a cooperative dynamic where both parties are motivated to share
# openly, as it leads to mutual benefit. At the same time, it discourages
# exploitation because withholding information will lead to reciprocal
# withholding in the following week.  3. **Account for Communication Issues
# (Forgiveness Mechanism)**      Since technical issues (like data corruption or
# communication breakdowns) can occasionally interfere with sharing, incorporate
# a **forgiveness mechanism**:    - If your colleague fails to share one week,
# don’t immediately switch to keeping your findings confidential in retaliation.
# Instead, give them **one opportunity** to correct the behavior. If they share
# openly the next week, resume open sharing yourself.    - However, if they
# withhold information for two consecutive weeks, switch to keeping your
# information confidential until they share again. This ensures you aren't taken
# advantage of while accounting for occasional errors.  4. **Long-Term
# Consideration**      Over the multi-week project, this strategy promotes a
# sustainable collaboration. By starting with trust, mirroring behavior, and
# incorporating a forgiveness mechanism, you'll maximize the chances of mutual
# sharing and development. At the same time, you're protected from being
# consistently exploited by a colleague who decides to withhold information
# repeatedly.  5. **End of Project**      In the final week or two of the
# project, you may consider keeping your findings confidential regardless of
# your colleague’s actions if you feel that competitive advantage is more
# critical than mutual progress at that stage. This would be a strategic
# decision based on the proximity to the final design deadline.  ### Summary: -
# **Week 1:** Share openly. - **Week 2 onwards:** Mirror your colleague's
# previous week’s action (share if they shared, withhold if they withheld). -
# **Forgiveness:** Allow for one mistake due to potential technical issues
# before switching to confidential mode. - **Final weeks:** Consider withholding
# your findings to secure a competitive edge.  This strategy is simple, neutral,
# and adaptable, allowing for collaboration while preventing exploitation.

# ### Iterated Game Strategy: Tit-for-Tat with Forgiveness  1. **Initial
# Action:**      In the first round, play **C** (Cooperate).  2. **Main Rule
# (Tit-for-Tat):**      From round 2 onwards, **play the same action your
# opponent played in the previous round**:    - If your opponent played **C**
# (Cooperate) in the previous round, play **C** in the current round.    - If
# your opponent played **D** (Defect) in the previous round, play **D** in the
# current round.  3. **Forgiveness Mechanism (Handling Noise):**      If your
# opponent plays **D** for **only one round** after a series of **C** plays,
# treat it as potential noise and continue playing **C** in the next round. This
# means:    - If your opponent plays **D** once after playing **C** multiple
# times, in the next round, play **C** instead of switching immediately to
# **D**.    - If your opponent plays **D** for **two consecutive rounds**,
# assume they are intentionally defecting, and switch to **D** until they return
# to playing **C**.  4. **Endgame (Final 20 Rounds):**      In the last 20
# rounds of the game, **always play D** (Defect), regardless of what your
# opponent does. This ensures you secure a competitive advantage as the game
# approaches its conclusion.  ### Summary of Conditions: - **Round 1:** Play
# **C**. - **Round 2 onwards:** Mirror your opponent’s previous action, but:   -
# If your opponent defects once after cooperating, forgive and play **C**.   -
# If your opponent defects twice in a row, switch to **D**. - **Final 20
# rounds:** Always play **D**.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Check if we are in the final 20 rounds
      if len(self.history) >= 980:
          return axl.Action.D
  
      # Main Tit-for-Tat rule with forgiveness
      if len(opponent.history) >= 2:
          # Check if opponent defected twice in a row
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          # Check if opponent defected once after a series of cooperations
          elif opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
  
      # Default Tit-for-Tat: Mirror opponent's last move
      return opponent.history[-1]

# ### High-Level Aggressive Strategy: "Conditional Retaliation with Initial
# Cooperation"  The objective of this strategy is to maximize your country's
# economic advantage while maintaining flexibility to respond to potential
# miscommunications, errors, or strategic shifts from your counterpart. The
# strategy involves an assertive but calculated approach, starting with
# cooperative gestures but quickly retaliating against any perceived
# exploitation or miscommunication. This ensures your counterpart understands
# that aggressive behavior will not be tolerated, while leaving room for
# positive outcomes if they choose to cooperate.  #### **1. Start with Free
# Trade (Round 1 - Building Trust)** - **Propose Free Trade in the first
# round.**   - This signals goodwill and creates an environment where mutual
# benefit is possible. It also tests your counterpart’s intentions and
# establishes a baseline for cooperation.   - **Ideal Outcome:** Both nations
# offer free trade, laying the groundwork for a mutually beneficial
# relationship.   - **If your counterpart imposes protectionist measures:** Take
# note but do not retaliate immediately. There’s a non-zero chance of
# miscommunication in the early rounds. However, prepare to respond forcefully
# if this pattern repeats.  #### **2. Conditional Aggression (Round 2 -
# Retaliation or Continued Cooperation)** - **If your counterpart offers free
# trade in Round 1:** Continue offering free trade in Round 2 to solidify trust
# and maintain mutual benefit. - **If your counterpart imposes protectionist
# measures in Round 1:** Retaliate with **Protectionism** in Round 2.   -
# **Rationale:** You must demonstrate that exploitation will be met with
# immediate and proportionate retaliation. This discourages your counterpart
# from trying to take advantage of your initial goodwill.   - **If
# miscommunication occurs:** The shift to protectionism creates a strong signal
# that they must align their actions with yours moving forward.    #### **3.
# Tit-for-Tat with Escalation (Rounds 3-5 - Punish Aggression, Reward
# Cooperation)** - **Tit-for-Tat:** If your counterpart continues to offer free
# trade, continue cooperating. If they impose protectionist measures again,
# escalate the retaliation with a more aggressive protectionist stance (higher
# tariffs, stricter quotas).   - **Escalation Rationale:** By increasing the
# intensity of retaliation, you signal that repeated aggressive behavior will
# lead to worse outcomes for both sides. This encourages your counterpart to
# reconsider their protectionist stance.   - **Free Trade Reward:** If your
# counterpart shifts back to free trade, immediately return to free trade
# yourself. This rewards cooperative behavior, fostering a long-term mutually
# beneficial relationship.    #### **4. Gradual De-escalation (Rounds 6-8 -
# Rebuilding Trust)** - **If mutual protectionism persists for more than two
# consecutive rounds:** Gradually de-escalate protectionist measures to test
# whether your counterpart is willing to soften their stance.   - **Rationale:**
# Stubbornly adhering to protectionism will hurt both nations in the long term.
# By slowly reducing protectionist measures, you signal a willingness to return
# to free trade while still avoiding immediate vulnerability.   - **If your
# counterpart reciprocates by reducing protectionism:** Move back toward free
# trade, rewarding their cooperative shift.   - **If your counterpart maintains
# or escalates protectionism:** Continue with strong retaliatory measures.  ####
# **5. Final Rounds (Round 9-10 - Lock in Best Outcome)** - **If your
# counterpart has consistently cooperated:** Offer free trade in the final
# rounds to lock in a mutually beneficial outcome. This ensures both nations
# depart the negotiation with positive trade relations. - **If your counterpart
# has been consistently protectionist:** Impose strong protectionist measures to
# ensure your country is not left in a disadvantageous position. This punishes
# their aggression and protects your country’s interests.    #### **6.
# Contingency for Miscommunication or Bureaucratic Errors** - **Build in
# Flexibility:** Given the possibility of miscommunication or errors in policy
# implementation, avoid overreacting to a single round of unexpected behavior.
# If your counterpart unexpectedly imposes protectionist measures after a period
# of cooperation, assume it may be a miscommunication and give them one round to
# correct it. Only retaliate if the behavior persists across two consecutive
# rounds.    #### **Summary of the Strategy:** - **Round 1:** Initiate with free
# trade to test cooperation. - **Round 2:** Retaliate with protectionism if they
# impose protectionist measures; continue free trade if they cooperate. -
# **Rounds 3-5:** Implement tit-for-tat with escalation if they are aggressive;
# reward cooperation with continued free trade. - **Rounds 6-8:** Gradually de-
# escalate if stuck in mutual protectionism, testing their willingness to
# cooperate. - **Rounds 9-10:** Lock in the best possible outcome based on prior
# behavior—either mutual free trade or strong protectionism.  This strategy
# leverages both cooperation and aggression, ensuring your country remains
# flexible but assertive in protecting its economic interests across several
# rounds of complex negotiations.

# ### Iterated Game Strategy Description: "Conditional Retaliation with Initial
# Cooperation"  1. **Start with Cooperation (Round 1)**      - Play **C**
# (Cooperate) in the first round. This establishes a baseline of trust and tests
# your opponent's intentions.  2. **Retaliate if Opponent Defects (Round 2)**
# - If your opponent played **D** (Defect) in Round 1, play **D** in Round 2 to
# retaliate.    - If your opponent played **C** (Cooperate) in Round 1, continue
# playing **C** in Round 2.  3. **Tit-for-Tat with Escalation (Rounds 3-10)**
# - **If your opponent played C in the previous round:** Continue playing **C**
# as long as they do.    - **If your opponent played D in the previous round:**
# Play **D** to retaliate.        - **If they defect twice in a row (D in
# consecutive rounds):** Continue playing **D** to escalate the punishment.  4.
# **Allow for Errors (All Rounds)**      - If your opponent unexpectedly plays
# **D** after previously playing **C**, assume it may be due to noise (a 10%
# chance of action-flipping).      - **If your opponent plays D only once and
# then returns to C:** Play **C** in the following round to restore cooperation.
# - **If your opponent plays D two consecutive times:** Respond by playing **D**
# in the next round, assuming intentional defection.  5. **De-escalation after
# Mutual Defection (Rounds 11-30)**      - After 10 consecutive rounds of mutual
# **D** (both players defecting), start playing **C** again to test if your
# opponent is willing to return to cooperation.      - If they respond with
# **C**, continue cooperating.      - If they continue playing **D**, return to
# **D** and maintain defection.  6. **Endgame (Final 50 Rounds)**      - **If
# your opponent has cooperated more than 80% of the time throughout the game:**
# Play **C** in the final 50 rounds to lock in mutual cooperation.    - **If
# your opponent has defected more than 50% of the time:** Play **D** in the
# final 50 rounds to protect your score against their aggression.  This strategy
# is designed to balance initial cooperation with consistent retaliation against
# defection, while accounting for noise in the game.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Round 1: Start with Cooperation
      if self.first_round():
          return axl.Action.C
  
      # Round 2: Retaliate if opponent defected in Round 1
      if len(self.history) == 1:
          if opponent.history[0] == axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rounds 3-10: Tit-for-Tat with Escalation
      if len(self.history) <= 10:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          elif opponent.history[-1] == axl.Action.D:
              if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D:
                  return axl.Action.D  # Escalate if opponent defected twice in a row
              else:
                  return axl.Action.D  # Retaliate for a single defection
  
      # De-escalation after mutual defection (Rounds 11-30)
      if 11 <= len(self.history) <= 30:
          if self.history[-10:].count(axl.Action.D) == 10 and opponent.history[-10:].count(axl.Action.D) == 10:
              return axl.Action.C  # Test for cooperation after mutual defection
          elif opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Endgame (Final 50 Rounds)
      if len(self.history) >= 950:
          opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)
          if opponent_cooperation_rate > 0.8:
              return axl.Action.C  # Cooperate if opponent has cooperated more than 80% of the time
          elif opponent.history.defections / len(opponent.history) > 0.5:
              return axl.Action.D  # Defect if opponent has defected more than 50% of the time
  
      # Allow for errors (All Rounds)
      if opponent.history[-1] == axl.Action.D:
          if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.C:
              return axl.Action.C  # Assume noise if opponent defected only once after cooperation
          elif len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D  # Retaliate if opponent defected twice in a row
  
      return axl.Action.C  # Default to cooperation if no other condition applies

# In this situation, your strategy should be based on fostering trust, open
# communication, and adaptability, while also accounting for the inherent
# uncertainty in both parties' resource allocation. Here's a high-level
# cooperative strategy:  ### 1. **Start with Cooperation (Both Invest Heavily)**
# - **Day 1 Strategy**: Begin the project by signaling collaboration and
# commitment. Both your NGO and the corporation should invest heavily on the
# first day. This sets a positive tone and demonstrates your willingness to work
# together toward the project's success.    - **Rationale**: This action
# encourages trust and signals to the corporation that your NGO is serious about
# advancing the project. It also helps gauge the corporation's initial intent
# and willingness to invest.  ### 2. **Establish Regular Communication**    -
# **Daily Check-ins**: Implement a structured, daily communication channel
# (e.g., end-of-day debriefs or morning strategy calls) to discuss investment
# plans, resource allocation, and any unforeseen issues. This ensures both
# parties stay aligned and can adjust plans based on the previous day’s
# outcomes.    - **Transparency**: Share your NGO’s resource constraints and
# long-term goals openly with the corporation. Encourage them to do the same, so
# both parties understand each other's boundaries and can work together to
# optimize the project’s success.  ### 3. **Adapt Based on the Corporation's
# Behavior**    - **Analyze Patterns**: After the first couple of days, assess
# the corporation’s behavior. Are they consistently investing heavily, or are
# they conserving resources more frequently? Based on this observation:      -
# **If the corporation invests heavily**: Continue to invest heavily as well for
# a few more days, creating significant progress.      - **If the corporation
# conserves resources**: Gradually shift toward conserving your own resources to
# avoid being exploited.        - **Midway Adjustments**: If the corporation
# exhibits erratic behavior (e.g., alternates between heavy investment and
# conservation unpredictably), adopt a more cautious strategy where you invest
# moderately but stay flexible.  ### 4. **Introduce a Tit-for-Tat Approach**
# - After the initial few days, if it becomes unclear if the corporation will
# continue to invest heavily or starts conserving, adopt a **tit-for-tat**
# strategy:      - **If the corporation invests heavily**: You invest heavily
# the next day.      - **If the corporation conserves resources**: You conserve
# resources the following day as well.    - **Flexibility**: Since unforeseen
# circumstances (e.g., technical glitches) may disrupt either party’s ability to
# invest as planned, use your daily communication to verify if any mishaps
# occurred and adjust accordingly.  ### 5. **Monitor External Factors**    -
# **Unforeseen Circumstances**: Be aware of any external issues (e.g., technical
# failures or administrative errors) that might affect resource allocation. Use
# your communication strategy to ensure that both parties understand if a day's
# outcome was intentional or due to an error, and adjust your strategy
# accordingly (e.g., give the corporation the benefit of the doubt for one day
# if they fail to invest due to unforeseen issues).  ### 6. **End with a Strong
# Push**    - **Final Days of the Project**: In the last few days of the
# project, aim to finish strong by returning to heavy investment if possible.
# Regardless of the corporation's behavior, this will help ensure the project’s
# maximum impact and leave your NGO with a positive reputation for commitment
# and collaboration.  ### 7. **Keep Long-Term Partnership in Mind**    - **Build
# Trust for Future Projects**: Throughout the project, emphasize long-term
# collaboration and sustainability. Even if the corporation conserves resources
# more than expected, maintain a cooperative attitude to foster a positive
# relationship for future partnerships.  ### Summary of Key Points: 1. **Start
# with heavy investment from both sides** to set a collaborative tone. 2.
# **Establish daily communication** to ensure alignment and transparency. 3.
# **Adapt based on the corporation's behavior**, and introduce a **tit-for-tat**
# strategy if uncertainty arises. 4. **Communicate openly about unforeseen
# circumstances** and adjust your strategy accordingly. 5. **Finish the project
# with a strong push** to maximize impact. 6. **Consider the long-term
# relationship** with the corporation, focusing on sustainability and
# collaboration for future projects.  By following this strategy, you balance
# cooperation with caution, prioritize communication, and remain adaptable to
# changing circumstances, ultimately maximizing the project's success and your
# NGO’s impact.

# ### Strategy for the Iterated Game:  1. **Start by Cooperating (C) for the
# First 5 Rounds**      - Always choose **Cooperate (C)** for the first 5 rounds
# to establish trust and signal your willingness to collaborate.  2. **Monitor
# Opponent’s Behavior After the First 5 Rounds**      - If the opponent
# **Cooperates (C)** in at least 4 out of the first 5 rounds, continue to
# **Cooperate (C)**.    - If the opponent **Defects (D)** more than once in the
# first 5 rounds, switch to a more cautious response.  3. **Tit-for-Tat with
# Forgiveness**      - After the first 5 rounds, if the opponent **Cooperates
# (C)** in the previous round, **Cooperate (C)** in the next round.    - If the
# opponent **Defects (D)** in the previous round, respond by **Defecting (D)**
# in the next round.    - However, if the opponent has been generally
# cooperative (more than 70% cooperation up to that point), forgive occasional
# defections and **Cooperate (C)** again after one round of **Defecting (D)**.
# 4. **Noise Handling (Mistakes)**      - If you **Defect (D)** and your
# opponent **Defects (D)** immediately after a long stretch of mutual
# cooperation (at least 5 rounds in which both played C), assume noise caused
# the defection. Return to **Cooperate (C)** the next round.    - Similarly, if
# you intended to **Cooperate (C)** but observe your opponent **Defects (D)**,
# avoid retaliating immediately. **Cooperate (C)** one more time to account for
# potential noise.  5. **Adjust Based on Patterns**      - If your opponent
# **Defects (D)** for 3 or more consecutive rounds, assume they have shifted to
# a non-cooperative strategy. Switch to **Defect (D)** consistently until they
# return to **Cooperate (C)**.    - If your opponent resumes playing **Cooperate
# (C)** for 2 consecutive rounds after a defection streak, return to **Cooperate
# (C)** as well.  6. **Final 50 Rounds: Focus on Cooperation (C)**      - During
# the last 50 rounds, prioritize **Cooperation (C)** regardless of minor
# defections. The goal is to maximize long-term mutual gains and finish on a
# positive, cooperative note.  ### Summary of Key Rules: - **Start with
# Cooperation**, monitor for the first 5 rounds. - Use **tit-for-tat** with
# forgiveness for occasional defections. - Account for noise by forgiving
# isolated defections after mutual cooperation. - Respond more firmly to
# extended defection patterns but return to cooperation if the opponent shows
# signs of good faith. - **Prioritize cooperation in the final rounds** to
# maximize long-term success.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      TOTAL_ROUNDS = 1000
      FINAL_ROUNDS_THRESHOLD = 50
      INITIAL_COOPERATION_ROUNDS = 5
      COOPERATION_THRESHOLD = 0.7
  
      # Helper function to check if we are in the final 50 rounds
      def in_final_rounds():
          return len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS_THRESHOLD
  
      # Helper function to check if opponent has been generally cooperative
      def opponent_is_generally_cooperative():
          if len(opponent.history) == 0:
              return False
          return opponent.history.cooperations / len(opponent.history) > COOPERATION_THRESHOLD
  
      # Helper function to check if there was a long stretch of mutual cooperation
      def long_stretch_of_mutual_cooperation():
          if len(self.history) < 5:
              return False
          return self.history[-5:] == [COOPERATE] * 5 and opponent.history[-5:] == [COOPERATE] * 5
  
      # Helper function to check if opponent defected for 3 or more consecutive rounds
      def opponent_defected_streak():
          return len(opponent.history) >= 3 and opponent.history[-3:] == [DEFECT] * 3
  
      # Helper function to check if opponent has returned to cooperation after a defection streak
      def opponent_returned_to_cooperation():
          return len(opponent.history) >= 2 and opponent.history[-2:] == [COOPERATE] * 2
  
      # First 5 rounds: Always cooperate
      if len(self.history) < INITIAL_COOPERATION_ROUNDS:
          return COOPERATE
  
      # After the first 5 rounds, check opponent's behavior in the first 5 rounds
      if len(self.history) == INITIAL_COOPERATION_ROUNDS:
          if opponent.history[:INITIAL_COOPERATION_ROUNDS].count(DEFECT) > 1:
              self.cautious_mode = True
          else:
              self.cautious_mode = False
  
      # If in cautious mode, use Tit-for-Tat with forgiveness
      if self.cautious_mode:
          if opponent.history[-1] == DEFECT:
              if opponent_is_generally_cooperative():
                  return COOPERATE  # Forgive occasional defections
              return DEFECT  # Tit-for-Tat response to defection
          return COOPERATE  # Tit-for-Tat response to cooperation
  
      # Handle noise: If both defect after a long stretch of cooperation, assume noise
      if len(self.history) > 1 and self.history[-1] == DEFECT and opponent.history[-1] == DEFECT:
          if long_stretch_of_mutual_cooperation():
              return COOPERATE
  
      # Handle noise: If opponent defects after you cooperated, forgive once
      if len(self.history) > 1 and self.history[-1] == COOPERATE and opponent.history[-1] == DEFECT:
          return COOPERATE
  
      # If opponent defected for 3 or more consecutive rounds, switch to defect
      if opponent_defected_streak():
          return DEFECT
  
      # If opponent returns to cooperation after a defection streak, return to cooperation
      if opponent_returned_to_cooperation():
          return COOPERATE
  
      # Final 50 rounds: prioritize cooperation
      if in_final_rounds():
          return COOPERATE
  
      # Default Tit-for-Tat behavior
      if opponent.history[-1] == DEFECT:
          return DEFECT
      return COOPERATE

# Given the dynamics of the situation and the uncertainty of outcomes, your
# strategy should balance prudence with collaboration while maintaining
# flexibility in response to unforeseen circumstances. Here is a high-level,
# neutral strategy to maximize your NGO's impact and the project's success:  ###
# 1. **Establish Clear Communication and Expectations Early**    - **Daily
# Coordination Meeting**: Begin each day with a brief meeting between your NGO
# and the corporation to discuss each party's intended resource allocation for
# the day. This builds trust, encourages transparency, and reduces the risk of
# misaligned investments.    - **Clarify Conditions for Investment**: Establish
# clear criteria for when heavy investment makes sense (e.g., major project
# milestones, high-impact deliverables, etc.). This ensures that both parties
# are aligned on when heavier resource allocation is most beneficial.  ### 2.
# **Adopt a "Tit-for-Tat" Strategy with Flexibility**    - Start by **mirroring
# the corporation’s initial investment strategy** on Day 1. If they invest
# heavily, you do the same. If they conserve resources, you conserve as well.
# This establishes reciprocity and signals your willingness to collaborate.    -
# As the project progresses, **adapt to the corporation's pattern**. If they
# consistently invest heavily, you can begin to conserve some resources while
# maintaining the overall momentum of the project. On the other hand, if the
# corporation consistently conserves resources, you may need to conserve more
# frequently to avoid unnecessary depletion of your NGO’s resources.  ### 3.
# **Utilize a 2:1 Investment-Conservation Ratio**    - To balance progress with
# resource management, plan to invest heavily for two days out of every three,
# while conserving resources on the third day. This ensures that you are
# consistently contributing to the project's advancement but not overextending
# your resources.    - Adjust this ratio based on the corporation's behavior. If
# the corporation is investing heavily every day, you may conserve more
# frequently. If they are conserving more often, you may increase your
# investment frequency to maintain momentum.  ### 4. **Prepare for Unforeseen
# Circumstances**    - **Buffer Resources**: Always maintain a reserve of
# resources in case of technical glitches, administrative delays, or other
# unforeseen issues. Never invest 100% of available resources on any given day.
# - **Contingency Planning**: Have flexible contingency plans in place in case
# either party's intended investment is not carried out. For example, if the
# corporation experiences a technical glitch and cannot invest on a particular
# day, be prepared to adjust your investment accordingly to avoid overspending.
# ### 5. **Monitor Progress Closely**    - **Daily Progress Review**: Track the
# project's progress closely to ensure that the resource allocation is
# translating into meaningful advancement. If progress is lagging despite heavy
# investment, this might indicate inefficiencies or miscommunications, which
# should be addressed immediately.    - **Adjust Strategy as Needed**: Based on
# daily reviews, be prepared to adjust your investment strategy. If the
# corporation begins to conserve more frequently, or if external factors such as
# market conditions change, adapt your approach accordingly.  ### 6. **End-of-
# Week Evaluation**    - At the end of each week, conduct a formal evaluation
# with the corporation to assess the progress made, the resources invested, and
# any challenges encountered. Use this feedback to refine the strategy for the
# following days.  ### 7. **Emphasize Collaboration and Shared Ownership**    -
# Regularly remind the corporation that the success of the sustainability
# project is a shared responsibility, and that both parties benefit from its
# advancement. This encourages them to invest in alignment with the project’s
# goals rather than conserving excessively.  ### Summary of Strategy: - **Start
# with cooperation**: Mirror the corporation’s initial investment. - **Use a 2:1
# ratio**: Invest heavily two days and conserve on the third, adjusting as
# necessary based on the corporation's actions. - **Communicate consistently**:
# Use daily coordination meetings to avoid misaligned investments. - **Prepare
# for contingencies**: Maintain resource reserves and have backup plans for
# unforeseen circumstances. - **Evaluate and adjust**: Regularly assess progress
# and adapt the strategy as needed.  This strategy is designed to maximize the
# project’s success while safeguarding your NGO’s resources, fostering trust,
# and maintaining flexibility in response to day-to-day developments.

# Here is a clear and straightforward strategy to apply to an iterated noisy
# normal-form game with the given payoffs:  1. **Start by Cooperating (C) on the
# First Round.**  ---  2. **Reciprocate the Opponent's Last Action:**    - **If
# the opponent played C in the previous round**, play C (cooperate) in the
# current round.    - **If the opponent played D in the previous round**, play D
# (defect) in the current round.  ---  3. **Account for Noise (10% Chance of
# Action Flip):**    - If the opponent played D in the previous round but had
# mostly played C in the last five rounds (i.e., at least three times), **assume
# noise** and play C (cooperate).    - If the opponent played C in the previous
# round but had mostly played D in the last five rounds (i.e., at least three
# times), **assume noise** and play D (defect).  ---  4. **Cooperate 2/3 of the
# Time:**    - Every three rounds, regardless of the opponent's actions,
# **defect once** and **cooperate twice**. This ensures resource conservation
# while still maintaining progress.  ---  5. **Monitor for Consistent
# Defection:**    - If the opponent defects (D) for **five consecutive rounds**,
# switch to playing D (defect) for the remainder of the game.  ---  6.
# **Reevaluate Every 100 Rounds:**    - Every 100 rounds, review the opponent's
# overall behavior. If cooperation (C) has dominated in the last 100 rounds
# (e.g., more than 60% of the time), **increase cooperation frequency** by
# playing C (cooperate) three times out of every four rounds.  This strategy
# incorporates reciprocity, noise handling, and periodic reassessment to balance
# cooperation and defection for optimal long-term payoffs.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Step 1: Start by Cooperating (C) on the First Round
      if self.first_round():
          self.cooperate_count = 0  # Track cooperation frequency for reevaluation
          self.defect_count = 0     # Track defection frequency for reevaluation
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.round_counter = 0    # Track rounds for 2/3 cooperation rule
          return axl.Action.C
  
      # Step 2: Reciprocate the Opponent's Last Action
      last_opponent_action = opponent.history[-1]
      
      # Step 3: Account for Noise (10% Chance of Action Flip)
      if len(opponent.history) >= 5:
          last_five = opponent.history[-5:]
          if last_opponent_action == axl.Action.D and last_five.count(axl.Action.C) >= 3:
              return axl.Action.C  # Assume noise and cooperate
          if last_opponent_action == axl.Action.C and last_five.count(axl.Action.D) >= 3:
              return axl.Action.D  # Assume noise and defect
  
      # Step 4: Cooperate 2/3 of the Time
      self.round_counter += 1
      if self.round_counter % 3 == 0:
          return axl.Action.D  # Defect once every three rounds
      else:
          return axl.Action.C  # Cooperate twice every three rounds
  
      # Step 5: Monitor for Consistent Defection
      if last_opponent_action == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      if self.consecutive_defections >= 5:
          return axl.Action.D  # Defect for the rest of the game if opponent defects 5 times in a row
  
      # Step 6: Reevaluate Every 100 Rounds
      if len(self.history) % 100 == 0:
          last_100_opponent_actions = opponent.history[-100:]
          if last_100_opponent_actions.count(axl.Action.C) > 60:
              self.round_counter = 0  # Reset round counter to increase cooperation frequency
              if self.round_counter % 4 == 0:
                  return axl.Action.D  # Defect once every four rounds
              else:
                  return axl.Action.C  # Cooperate three times every four rounds
  
      # Default to reciprocating the opponent's last action
      return last_opponent_action

# ### Aggressive Strategy for Maximizing Research Output:  To approach this
# multi-week collaboration in a way that maximizes your chances of gaining a
# competitive edge, I recommend adopting a **“Cautious Opportunism”** strategy,
# which is aggressive yet adaptive to the situation. This strategy involves
# starting with a guarded stance and then adjusting your behavior based on your
# colleague’s actions and any uncertainties in communication.  #### **Step-by-
# Step High-Level Strategy:**  1. **Initial Weeks – Test the Waters (Keep
# Confidential):**    - **Action**: For the first 2–3 weeks, keep your findings
# confidential. This allows you to observe your colleague's behavior without
# exposing your research.    - **Objective**: Evaluate whether your colleague is
# trustworthy and whether they are willing to share openly.    - **Rationale**:
# This cautious start ensures you don't lose any competitive advantage early on.
# It also gives you a chance to gauge if any technical issues (e.g., data
# corruption or miscommunication) are likely to arise.  2. **Week 4–5 – Partial
# Sharing (Selective Sharing):**    - **Action**: Start sharing minor or less-
# critical improvements while keeping the most valuable developments
# confidential.    - **Objective**: Test if your colleague reciprocates your
# sharing. If they do, you can slowly increase your openness. If not, revert to
# confidentiality.    - **Rationale**: By sharing only marginal improvements,
# you minimize the risk of falling behind while still appearing engaged in the
# collaboration.  3. **Mid-Project – Adapt Based on Behavior:**    - **If
# Colleague Shares Openly**:       - **Action**: Gradually increase your level
# of openness, but always keep the most significant breakthroughs confidential.
# Share just enough to maintain collaboration and mutual progress.      -
# **Objective**: Maximize your research speed while protecting your most
# valuable developments.    - **If Colleague Keeps Confidential**:       -
# **Action**: Continue to keep your findings confidential and revert to full
# secrecy if the colleague never shares anything meaningful.      -
# **Objective**: Avoid being exploited and maintain your competitive edge.  4.
# **Endgame – Weeks 10–12:**    - **Action**: In the final weeks, lock down any
# critical developments and keep them completely confidential. The focus here is
# to finalize your design while minimizing the risk of your colleague stealing
# late-stage breakthroughs.    - **Rationale**: By keeping the endgame strategy
# confidential, you ensure that your final developments are unique and cannot be
# easily replicated by your colleague.  5. **Contingency for Technical Issues:**
# - **Action**: If you notice repeated failures in communication (either on your
# end or theirs), assume the worst. Treat any technical issues as potential
# strategic moves by your colleague to mask their refusal to share. In this
# case, revert to confidentiality unless proven otherwise.    - **Rationale**:
# Since technical issues can be used as an excuse, it’s safer to assume that
# lack of sharing is intentional, and you should not risk being too open in
# these scenarios.  ---  ### **Key Elements of the Strategy:**  - **Aggression
# with Flexibility**: Start aggressively by keeping information confidential,
# but be ready to adapt based on your colleague’s behavior. - **Controlled
# Sharing**: Never give away your most valuable developments—always keep an ace
# up your sleeve. - **React to Opportunism**: If your colleague tries to exploit
# your openness, immediately revert to full confidentiality. - **Mitigating Risk
# Due to Technical Failures**: Assume the worst and protect your work if
# communication breakdowns become frequent.  By following this strategy, you
# maximize your chances of gaining a significant development advantage while
# minimizing the risk of being exploited.

# ### Strategy for the Iterated Normal-Form Game:  1. **Rounds 1–10: Defect
# (D).**    - Play **D** for the first 10 rounds regardless of the opponent’s
# actions.    - Purpose: Test the opponent’s behavior while protecting yourself
# from early exploitation.  2. **Rounds 11–30: Mixed Strategy (Mostly Defect,
# Occasional Cooperation).**    - Play **D** for most rounds, but play **C** in
# 20% of the rounds randomly within this range.    - Purpose: Begin probing the
# opponent’s willingness to cooperate without fully committing.  3. **After
# Round 30 - Adapt Based on Opponent’s Behavior:**    - **If the opponent mostly
# cooperates (plays C more than 70% of the time):**      - Transition to a
# **Tit-for-Tat** strategy with forgiveness:        - Match the opponent’s last
# move, but if they defect once, forgive them **once** by playing **C** in the
# next round.        - If they defect twice or more consecutively, switch to
# full **D** until further notice (see Round 200 rule).      - Purpose:
# Encourage mutual cooperation while protecting yourself from repeated
# defections.     - **If the opponent mostly defects (plays D more than 70% of
# the time):**      - Continue playing **D** until Round 200.      - Purpose:
# Avoid being exploited by a non-cooperative opponent.     - **If the opponent’s
# behavior is inconsistent (C and D both between 30%–70%):**      - Play **D**
# 70% of the time and **C** 30% of the time randomly.      - Purpose: Hedge
# against unpredictability while minimizing risk.  4. **Round 200 - Re-
# evaluate:**    - If you’ve been playing **D** continuously (due to opponent
# defections or inconsistent behavior):      - Play **C** for 5 consecutive
# rounds as a test.      - If the opponent responds with consistent cooperation
# (plays **C** at least 4 out of 5 times), switch to the **Tit-for-Tat with
# forgiveness** strategy.      - If the opponent defects more than once, return
# to full **D** indefinitely.      - Purpose: Offer one final chance for
# cooperation after early defection or inconsistency.  5. **Final 50 Rounds
# (Rounds 951–1000): Defect (D).**    - Play **D** for the last 50 rounds
# regardless of the opponent’s actions.    - Purpose: Ensure you protect your
# final gains and avoid late-stage exploitation.  ---  ### Summary of the Main
# Conditions:  - **Start Defecting (Rounds 1–10)** to avoid early exploitation.
# - **Probe Cooperation (Rounds 11–30)** by mixing in occasional cooperation. -
# **Adapt after Round 30**:   - Use **Tit-for-Tat with forgiveness** if the
# opponent shows consistent cooperation.   - Continue defecting if they mostly
# defect or are inconsistent. - **Re-test for Cooperation at Round 200** if
# needed, and adapt accordingly. - **Defect in the Final 50 Rounds** to secure
# your position.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round number
      round_number = len(self.history) + 1
  
      # Helper function to calculate opponent's cooperation rate
      def opponent_cooperation_rate():
          return opponent.history.cooperations / len(opponent.history) if len(opponent.history) > 0 else 0
  
      # Helper function to determine if opponent is mostly cooperating
      def mostly_cooperating():
          return opponent_cooperation_rate() > 0.7
  
      # Helper function to determine if opponent is mostly defecting
      def mostly_defecting():
          return opponent_cooperation_rate() < 0.3
  
      # Helper function to determine if opponent is inconsistent
      def inconsistent_behavior():
          return 0.3 <= opponent_cooperation_rate() <= 0.7
  
      # Helper function for Tit-for-Tat with forgiveness
      def tit_for_tat_with_forgiveness():
          if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
          elif opponent.history[-1] == axl.Action.D:
              return axl.Action.C
          else:
              return opponent.history[-1]
  
      # Rounds 1-10: Always Defect
      if round_number <= 10:
          self.cooperation_test = False
          return axl.Action.D
  
      # Rounds 11-30: Mostly Defect, Occasionally Cooperate (20% chance of cooperation)
      if 11 <= round_number <= 30:
          return self._random.random_choice(0.2)
  
      # After Round 30: Adapt based on opponent's behavior
      if round_number > 30:
          if mostly_cooperating():
              # Tit-for-Tat with forgiveness
              return tit_for_tat_with_forgiveness()
          elif mostly_defecting():
              # Continue defecting until round 200
              if round_number < 200:
                  return axl.Action.D
          elif inconsistent_behavior():
              # Play D 70% of the time and C 30% of the time randomly
              return self._random.random_choice(0.3)
  
      # Round 200: Re-evaluate cooperation
      if round_number == 200:
          self.cooperation_test = True
          self.cooperation_test_rounds = 0
  
      if self.cooperation_test:
          if self.cooperation_test_rounds < 5:
              self.cooperation_test_rounds += 1
              return axl.Action.C
          else:
              # Evaluate opponent's response to the cooperation test
              if opponent.history[-5:].count(axl.Action.C) >= 4:
                  self.cooperation_test = False
                  self.forgiveness_mode = True
              else:
                  self.cooperation_test = False
                  return axl.Action.D
  
      # Final 50 Rounds (951-1000): Always Defect
      if round_number >= 951:
          return axl.Action.D
  
      # Default to Defect if no other condition is met
      return axl.Action.D

# ### Strategy Overview:  The strategy I propose is based on a **calculated
# cooperative approach** that balances **strategic assertiveness** with
# **openness to collaboration**, while also incorporating adaptability to deal
# with potential miscommunication or procedural irregularities. The goal is to
# maintain control over the narrative in front of the arbitrators, project
# reasonableness, and avoid escalating tensions, all while subtly positioning
# your corporation to win favorable concessions in the long term.  This strategy
# relies on three pillars: **Cooperative Framing**, **Controlled Flexibility**,
# and **Risk Mitigation** regarding communication breakdowns.  ---  ### Pillar
# 1: Cooperative Framing  The key to success is to consistently frame the
# corporation’s position as **reasonable**, **measured**, and **solution-
# oriented**, even when adopting aggressive stances. This will help shape the
# arbitrators' perception of your corporation as the more responsible and
# collaborative party while allowing for strategic assertiveness when necessary.
# #### Steps: 1. **Initial Cooperative Proposal**: Begin the process by offering
# a **moderate, conciliatory proposal** in the first session. This sets the tone
# of good faith negotiations, signaling to both the opposing party and the
# arbitrators that your corporation is interested in finding a mutually
# beneficial solution. Even if the other party responds aggressively, the
# arbitrators will perceive your corporation as cooperative.     2. **Assertive
# Framing of Aggressive Arguments**: In sessions where an aggressive argument is
# necessary, frame it as a **justified response to unreasonable behavior** by
# the opposing party. Emphasize that your corporation remains open to discussion
# but cannot compromise on key points due to fairness or business necessity.  3.
# **Use Conciliatory Proposals Tactically**: When circumstances favor
# collaboration (i.e., when you sense the opposing party is softening), propose
# a **conciliatory counteroffer** that addresses some of their concerns without
# sacrificing your key interests. This shows flexibility and prevents the
# opposition from framing you as obstructionist.  4. **Reciprocity Principle**:
# If the opponent offers a conciliatory proposal, respond with a **measured,
# cooperative counterproposal**. This reinforces the collaborative tone and
# prevents the opponent from gaining an upper hand by portraying themselves as
# the only party willing to compromise.  ---  ### Pillar 2: Controlled
# Flexibility  While assertiveness may be necessary in certain sessions, the
# strategy must remain flexible enough to adapt to the opponent’s approach and
# the evolving dynamics of arbitration. This flexibility will allow the
# corporation to **maximize opportunities for favorable outcomes** and minimize
# risks.  #### Steps: 1. **Session-by-Session Evaluation**: After each session,
# conduct a thorough analysis of the arbitrators' reactions and the opponent’s
# behavior. Use this analysis to decide whether to **continue with a
# conciliatory approach** or shift to a more assertive stance in the next
# session.  2. **Aggression Calibration**: If both parties are locked in
# aggressive arguments, propose a **reset** in the following session by putting
# forth a conciliatory suggestion. This helps avoid escalation and demonstrates
# to the arbitrators that your corporation is still focused on resolution, even
# if the other party is not.  3. **Escalation Control**: If the dispute
# escalates and both parties take aggressive stances, be prepared to **de-
# escalate strategically**. For example, if the arbitrators appear frustrated
# with the lack of progress, propose a smaller, intermediate concession (one
# that doesn’t harm your core position) to re-establish a cooperative tone.  ---
# ### Pillar 3: Risk Mitigation for Miscommunication and Procedural
# Irregularities  Mediation and arbitration processes are prone to communication
# breakdowns, procedural misunderstandings, or even intentional
# misrepresentation by the opposing party. Your strategy must be resilient and
# proactive in addressing these risks.  #### Steps: 1. **Clarify and Document**:
# At the end of each session, request a clear summary of the key points
# discussed and agreed upon, and ensure these are documented in the mediation
# record. This creates a paper trail that limits the risks of miscommunication
# or manipulation of the facts in future sessions.  2. **Address
# Misunderstandings Immediately**: If your argument is misrepresented,
# misunderstood, or miscommunicated by the arbitrators, immediately but
# **diplomatically correct the record**. Use neutral language to clarify the
# corporation’s position without accusing the arbitrators of bias or negligence.
# This keeps the discussion focused on the issues rather than procedural
# hiccups.  3. **Pre-Empt Potential Misrepresentations**: Anticipate areas where
# the opposition may attempt to misrepresent your conciliatory offers as
# weakness or concede miscommunications. Preemptively **frame your proposals as
# strategic solutions** that balance the interests of both parties, making it
# harder for the opponent to twist your intentions.  4. **Leverage Missteps by
# Opponent**: If the opponent miscommunicates or presents an overly aggressive
# argument that backfires, be ready to **seize the opportunity** to offer a
# conciliatory proposal right after, positioning your corporation as the more
# reasonable party and potentially gaining favor with the arbitrators.  ---  ###
# Contingency Plan for Worst-Case Scenario:  In the worst-case scenario, where
# the opponent successfully takes an aggressive stance and the arbitrators
# misunderstand or misrepresent your conciliatory actions, the strategy should
# pivot to **damage control**:  1. **Reassert Strength with Evidence**: If your
# conciliatory stance has been taken advantage of, the next session should
# involve a well-prepared, **evidence-backed aggressive argument** that
# reasserts your position. Ensure that this argument is framed as a necessary
# response to the opposition’s refusal to negotiate in good faith.  2. **Request
# a Procedural Reset**: If miscommunication becomes systematic, consider
# requesting a procedural pause or reset, citing the need for clarity and
# fairness. This will demonstrate to the arbitrators your commitment to a fair
# process, which could help rectify any missteps or misunderstandings.  3.
# **Public Relations and Media Considerations**: If the dispute becomes high-
# profile, ensure that your corporation’s public relations team is aligned with
# the legal strategy. Public statements should emphasize that your corporation
# has continuously acted in good faith and seeks a fair resolution, but will
# defend its interests when necessary.  ---  ### Conclusion:  This **calculated
# cooperative strategy** ensures that your corporation can adapt to various
# approaches by the opposing party while maintaining a favorable position with
# the arbitrators. By balancing assertive arguments with cooperative gestures,
# leveraging procedural safeguards, and mitigating communication risks, the
# corporation can systematically guide the mediation process toward an optimal
# outcome.

# ### Iterated Game Strategy  1. **Start by Cooperating (C)**: In the first
# round, open with a cooperative move. This establishes an initial atmosphere of
# goodwill, signaling a willingness to work towards a mutually beneficial
# outcome.  2. **Tit-for-Tat with Forgiveness**: In each subsequent round,
# **mimic your opponent’s previous action**:    - If your opponent played C in
# the previous round, play C.    - If your opponent played D in the previous
# round, play D.  3. **Forgive Occasional Defections** due to Noise: Because
# there is a 10% chance of action flips (noise), do not immediately punish a
# single defection. Instead, if your opponent defects once but previously
# cooperated for several rounds, assume the defection may have been caused by
# noise and **continue to cooperate (C)** in the next round.  4. **Retaliate
# After Consecutive Defections (Two in a Row)**: If your opponent defects **two
# times in a row**, assume the defection is intentional. In this case, **respond
# with D** in the following round to signal that continued aggression will not
# be tolerated.  5. **Return to Cooperation After Retaliation**: After
# retaliating with D, immediately return to cooperation (C) in the next round to
# offer an opportunity to reset the cooperation cycle. This shows that you are
# willing to collaborate again if your opponent is.  6. **Escalation Control**:
# If both you and your opponent have been playing D for four consecutive rounds,
# **revert back to C** to prevent a prolonged aggressive standoff. This move
# breaks the cycle of defection and offers a path back to mutual cooperation.
# ---  ### Summary of Key Conditions - Start with **C** (cooperate). - Play
# **C** if your opponent played C in the prior round. - Play **D** if your
# opponent played D in the prior round, but:   - Forgive a single D if it
# follows a string of C’s (play C).   - Retaliate with **D** only if your
# opponent defects two times in a row. - After defecting (D), return to **C** in
# the next round to reset cooperation. - If locked in mutual defection (D vs. D
# for four rounds), revert to **C**.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if the opponent defected twice in a row
      def opponent_defected_two_in_a_row():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if both players have been defecting for the last 4 rounds
      def mutual_defection_streak():
          return len(self.history) >= 4 and all(self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, 5))
  
      # If both players have been defecting for 4 rounds, revert to cooperation
      if mutual_defection_streak():
          return axl.Action.C
  
      # If the opponent defected twice in a row, retaliate with D
      if opponent_defected_two_in_a_row():
          return axl.Action.D
  
      # If the opponent defected in the last round but cooperated before, forgive and cooperate
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # Otherwise, mimic the opponent's last move (Tit-for-Tat)
      return opponent.history[-1]

# ### High-Level Mediation Strategy for Optimal Outcomes  **Goal:** To secure
# the most favorable resolution for the corporation by balancing assertiveness
# with cooperation, while maintaining flexibility to adapt to evolving dynamics
# during the mediation process.  ### 1. **Establish a Strong Initial Position
# (Session 1)**    - **Purpose:** Frame the corporation as firm but reasonable,
# setting the tone for the mediation.    - **Strategy:** Begin with a **measured
# but assertive argument**. Clearly outline the corporation's key demands and
# issues, but frame them as part of a broader intent to find a fair resolution.
# This shows strength without alienating the opposition or arbitrators.    -
# **Benefit:** This creates initial leverage and signals that you are willing to
# engage in tough discussions while remaining open to dialogue.  ### 2.
# **Implement a Mixed Strategy (Aggressive-Concessive Cycle)**    - **Purpose:**
# Adapt to your opponent’s moves while maintaining unpredictability, avoiding
# being locked into a single approach.    - **Strategy:**      - **In sessions
# where your opponent seems aggressive:** Match their aggressiveness, but
# highlight your willingness to find common ground. This signals to the
# arbitrators that your corporation is not the roadblock, even while defending
# its interests.      - **In sessions where your opponent is conciliatory:**
# Offer a **carefully crafted conciliatory proposal** that mirrors their tone,
# but ensure the proposal subtly advances your corporation’s position. This
# fosters a collaborative environment while still moving toward your desired
# outcome.    - **Benefit:** This versatility allows you to either capitalize on
# your opponent’s conciliatory gestures or neutralize their aggression,
# presenting the corporation as both principled and reasonable.  ### 3. **Use
# Strategic Concessions**    - **Purpose:** Signal goodwill without giving away
# significant value, positioning the corporation as a fair player in the eyes of
# the arbitrators.    - **Strategy:** Identify **low-cost, high-perception
# concessions**, i.e., items that appear significant to the opponent but are of
# minimal strategic importance to the corporation. Time these concessions for
# moments when tensions are escalating or the arbitrators seem to be losing
# patience with aggressive posturing.    - **Benefit:** This can help de-
# escalate situations and reinforce your overall strategy of fairness, making
# the arbitrators more likely to favor you in areas of significant importance.
# ### 4. **Leverage Procedural Irregularities and Communication Issues**    -
# **Purpose:** Prepare for potential miscommunication or procedural anomalies
# that could affect the flow of the mediation.    - **Strategy:**      -
# **Maintain clear, organized records** of every point raised and every argument
# presented. This will be crucial in instances where your strategy or your
# opponent’s strategy is misunderstood or misrepresented.      - If an argument
# is misrepresented, **swiftly but diplomatically clarify the record**, using a
# calm, factual tone to avoid appearing reactive or defensive.      - If your
# opponent’s argument is misunderstood in your favor, **consider whether to
# highlight the misunderstanding** based on how it impacts your position. In
# some cases, it may be strategic to let the misunderstanding stand, provided it
# benefits the corporation without credibility risk.    - **Benefit:** This
# allows you to control the narrative and mitigate damage from any
# miscommunication, ensuring the corporation’s position is accurately
# represented.  ### 5. **Monitor Arbitrator Sentiment**    - **Purpose:** Tailor
# your approach based on the arbitrators' evolving perspectives.    -
# **Strategy:** Throughout the sessions, pay close attention to verbal and non-
# verbal cues from the arbitrators (e.g., tone of questioning, body language).
# Adjust your strategy in real-time:      - **If arbitrators appear frustrated
# by aggressive posturing:** Shift to a more conciliatory tone to regain their
# favor.      - **If arbitrators show approval of firm positions:** Double down
# on assertiveness but continue to frame it within the context of fairness.    -
# **Benefit:** This ensures your arguments are persuasive and aligned with the
# arbitrators’ preferences, increasing the likelihood of favorable rulings.  ###
# 6. **Prepare for a Final Push**    - **Purpose:** Conclude the mediation with
# a decisive move that positions the corporation as reasonable and deserving of
# a favorable resolution.    - **Strategy:** In the final sessions, offer a
# **comprehensive settlement proposal** that incorporates key elements from both
# sides but still heavily favors the corporation’s interests. Frame it as a
# “last best offer” that seeks to avoid prolonged disputes, emphasizing the
# benefits of an amicable resolution for all parties.    - **Benefit:** This
# positions you as the party interested in resolution, which could sway
# arbitrators to push for an outcome closer to your final proposal.  ### 7.
# **Contingency Planning for Breakdowns**    - **Purpose:** Be prepared to
# handle unexpected breakdowns in communication or significant procedural
# irregularities.    - **Strategy:**       - If a session breaks down or
# communication is lost, maintain a calm, professional demeanor. Immediately
# request clarification or adjournment to address any irregularities.      -
# Keep the corporation’s broader strategy intact, but be ready to pivot if the
# mediation process becomes too compromised. If necessary, use the breakdown as
# an opportunity to request a different mediation format or reset discussions.
# - **Benefit:** This ensures that you retain control over the process and don’t
# allow procedural issues to derail your overall strategy.  ---  ### Summary of
# Strategy:  1. **Begin assertively** to establish a strong position. 2.
# **Adaptively alternate** between aggressive and conciliatory approaches based
# on the opponent’s behavior. 3. **Offer strategic concessions** to build
# goodwill and maintain momentum. 4. **Carefully manage procedural and
# communication breakdowns** to keep the corporation’s position intact. 5.
# **Monitor arbitrator sentiment** and adjust your tone and argumentation
# accordingly. 6. **Conclude with a comprehensive and reasonable proposal** that
# advances the corporation’s interests but appears fair.  By employing this
# strategy, your corporation will project strength while remaining adaptable
# throughout the mediation process. This approach maximizes the chances of
# securing a favorable resolution, even in the face of unpredictability and
# procedural challenges.

# ### Iterated Game Strategy (1000 Rounds)  1. **Start with Defection (D) in the
# First Round**      - Signal strength from the outset by playing D. This
# establishes your willingness to protect your interests and sets a firm tone.
# 2. **Tit-for-Tat with a Forgiveness Mechanism**      - In subsequent rounds,
# **mimic your opponent's previous action**. If they played C in the previous
# round, play C. If they played D, play D.      - **Forgive occasional
# defections**: If the opponent defects but has recently cooperated, assume
# noise and return to cooperation (C) on the next round. Specifically, if your
# opponent defects after a long streak of cooperation (5 or more consecutive
# Cs), respond with C in the next round, assuming their D was likely noise.  3.
# **Strategic Defection after Opponent’s Patterned Defection**      - If your
# opponent plays D **three times in a row**, respond with D until they return to
# cooperation (C). This ensures you don’t consistently lose out by forgiving
# repeated defections.  4. **Occasional Cooperation After Long Defection Runs**
# - If you and your opponent have been defecting repeatedly for **more than 10
# consecutive rounds**, break the cycle by playing C once. This signals a
# willingness to reset the relationship and test for potential cooperation.  5.
# **Monitor Long-Term Cooperation Trends**      - If your opponent plays C for
# **more than 20 consecutive rounds**, switch to a strategy of **mostly
# cooperating (C)**, but occasionally defect (D) once every 20 rounds to test
# their response. This allows you to capitalize on cooperation while
# occasionally probing for weaknesses without fully committing to constant
# cooperation.  6. **Final 50 Rounds – Shift to Cooperation with Selective
# Defection**      - In the last 50 rounds, play **mostly C** to encourage a
# cooperative finish, but defect (D) once every 10 rounds to protect against
# exploitation. This ensures that you maintain a strong position while closing
# the game on a cooperative note.  ---  This strategy balances assertiveness
# with flexibility, adapts to noise, and encourages cooperation without allowing
# exploitation.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to check if opponent has cooperated for N consecutive rounds
      def opponent_cooperated_consecutively(n):
          return len(opponent.history) >= n and all(action == axl.Action.C for action in opponent.history[-n:])
      
      # Helper function to check if opponent has defected for N consecutive rounds
      def opponent_defected_consecutively(n):
          return len(opponent.history) >= n and all(action == axl.Action.D for action in opponent.history[-n:])
      
      # Helper function to count the number of cooperations in the last N rounds
      def opponent_recent_cooperations(n):
          return opponent.history[-n:].count(axl.Action.C)
      
      # First round: Defect
      if self.first_round():
          return axl.Action.D
      
      # Last 50 rounds: Mostly cooperate, defect once every 10 rounds
      if len(self.history) >= 950:
          if len(self.history) % 10 == 0:
              return axl.Action.D
          return axl.Action.C
      
      # Tit-for-tat with forgiveness mechanism
      if opponent.history[-1] == axl.Action.D:
          # Forgive if opponent defected after 5 or more consecutive cooperations
          if opponent_cooperated_consecutively(5):
              return axl.Action.C
          # If opponent defected 3 times in a row, retaliate with D
          if opponent_defected_consecutively(3):
              return axl.Action.D
          return axl.Action.D
      else:
          return axl.Action.C
      
      # Occasional cooperation after long defection runs (more than 10 rounds)
      if opponent_defected_consecutively(10):
          return axl.Action.C
      
      # Monitor long-term cooperation trends (more than 20 rounds)
      if opponent_cooperated_consecutively(20):
          if len(self.history) % 20 == 0:
              return axl.Action.D
          return axl.Action.C

# ### High-Level Aggressive Strategy for Mediation Process  **Objective:**
# Maximize your corporation’s position by leveraging an aggressive posture in
# each session, while maintaining the flexibility to adjust based on both the
# opponent’s approach and unpredictable factors such as procedural
# irregularities or communication breakdowns.  ### 1. **Initial Assessment: Set
# the Tone with Dominance**    - **Objective:** Start by establishing a strong,
# non-conciliatory stance to signal that your corporation is prepared to defend
# its interests vigorously.    - **Action:** In the first session, present a
# powerful argument that aggressively underscores the weaknesses in your
# opponent’s position. Frame the narrative early, focusing on legal precedents,
# contractual obligations, and any leverage points that put your corporation in
# a favorable light.    - **Psychological Impact:** This will set the tone for
# the entire mediation, positioning your corporation as the dominant party. Your
# opponent may be psychologically pushed toward adopting a more conciliatory
# stance in future sessions.  ### 2. **Controlled Escalation: Aggressive, But
# Calculated**    - **Objective:** Maintain an aggressive stance across
# sessions, but avoid pushing the arbitrators into perceiving your approach as
# overly hostile or unreasonable.    - **Action:** In subsequent sessions,
# continue to present aggressive arguments but introduce slight variations to
# demonstrate adaptability. For example:      - Present hard-hitting facts or
# evidence where the opponent has clearly breached contractual terms.      - Use
# sharp legal reasoning to corner the opponent on specific issues.      -
# Highlight any contradictions in the opponent's previous arguments.    -
# **Psychological Impact:** While you remain aggressive, you avoid triggering a
# scenario where both parties are seen as only escalating tensions. This keeps
# the arbitrators focused on the strength of your arguments rather than the
# hostility of the process.  ### 3. **Strategic Concession: Appear Reasonable
# While Maintaining Aggression**    - **Objective:** To avoid appearing overly
# combative, occasionally offer minor concessions that do not undermine your
# core position but give the appearance of good faith negotiation.    -
# **Action:** Identify areas where your corporation can afford to make small,
# non-critical concessions. Frame these as “olive branches” to the arbitrators,
# emphasizing that your corporation is willing to be reasonable despite your
# opponent’s perceived intransigence.    - **Psychological Impact:** This
# strategic move can portray your corporation as reasonable, potentially pushing
# the arbitrators to pressure the opponent into offering more significant
# concessions. It also helps mitigate any perception that your corporation is
# responsible for any procedural delays or breakdowns.  ### 4. **Prepare for
# Procedural Irregularities: Preempt and Control the Narrative**    -
# **Objective:** Anticipate possible miscommunications or procedural issues, and
# be prepared to swiftly control the narrative when such instances occur.    -
# **Action:** Ensure that you are always ready to provide follow-up
# clarifications or written summaries of your arguments to the arbitrators. If
# miscommunication occurs or your aggressive stance is misunderstood,
# immediately pivot to clarify your position without retreating from your core
# argument. Always maintain a posture of professionalism and composure.    -
# **Psychological Impact:** This puts you in control of the process. By being
# the party that clarifies and corrects ambiguities, you position your
# corporation as the more responsible and thorough participant in the mediation.
# ### 5. **Exploit Opponent Weaknesses**    - **Objective:** Take advantage of
# any conciliatory proposals or weaknesses in your opponent’s arguments,
# particularly if they adopt a more appeasing posture in response to your
# aggressive stance.    - **Action:** If your opponent offers a conciliatory
# proposal, rather than reciprocating, double down on your aggressive position
# and demand further concessions. Use their conciliatory tone as a sign of
# weakness and press for a more favorable outcome.    - **Psychological
# Impact:** This will push the arbitrators toward viewing your corporation as
# the more confident and justified party, potentially influencing them to favor
# your position.  ### 6. **Adaptability: Be Ready to Pivot Based on Opponent's
# Actions**    - **Objective:** While remaining aggressive, you must be
# adaptable to shifts in your opponent's strategy.    - **Action:** If your
# opponent unexpectedly escalates, be prepared to meet their aggression with
# even more force, but do so in a way that appears justified by their actions.
# Conversely, if they become overly conciliatory, consider whether it benefits
# you to reciprocate slightly to secure a mutually beneficial resolution—or if
# you should continue pressing your aggressive advantage.    - **Psychological
# Impact:** By staying adaptable, you avoid being predictable and maintain the
# upper hand, always appearing in control.  ### 7. **Leverage Relationships with
# Arbitrators**    - **Objective:** Maintain a strong, professional rapport with
# the arbitration panel to ensure procedural fairness and avoid
# misinterpretation of aggressive arguments.    - **Action:** Consistently
# present your arguments with respect and professionalism, even as you remain
# aggressive in substance. Use subtle cues in your communication to emphasize
# that your corporation is not the cause of any delays or breakdowns.    -
# **Psychological Impact:** Arbitrators will be more inclined to view your
# arguments favorably if they see you as the party that is both aggressive but
# also respectful of the process and their role in it.  ### 8. **Prepare for
# Procedural Contingencies**    - **Objective:** Be ready for unexpected
# procedural issues, such as miscommunication or delays, and have a contingency
# plan in place that maintains your aggressive posture.    - **Action:** Have a
# team prepared to immediately address any procedural irregularities. This could
# involve submitting supplementary briefs, requesting clarification from the
# arbitrators, or even proposing adjustments to the schedule if needed to keep
# the process moving forward. Never let procedural issues undermine the strength
# of your position.    - **Psychological Impact:** By being proactive, you
# demonstrate that your corporation is prepared for any eventuality, further
# solidifying your position as the more competent and capable party in the eyes
# of the arbitrators.  ---  ### Conclusion: An Aggressive, Flexible Approach
# Your strategy should focus on maintaining a strong, aggressive stance
# throughout the mediation process while being adaptable to the opponent’s moves
# and potential procedural irregularities. By balancing dominance with
# calculated concessions and controlling the narrative in the face of procedural
# issues, you will position your corporation favorably in the eyes of the
# arbitrators. This high-level strategy ensures that you maximize your
# corporation’s leverage while minimizing the risks associated with aggressive
# mediation tactics.

# ### Iterated Game Strategy for 1000 Rounds  1. **Start Aggressively (Defect)**
# - In the first 5 rounds, always **Defect** to establish a strong, dominant
# position early on. This signals to your opponent that you are not afraid to
# play aggressively and will not be taken advantage of easily.  2. **Monitor
# Opponent’s Response**      - After the initial 5 rounds, observe your
# opponent’s behavior:      - If the opponent **continues to Defect**
# consistently after the first 5 rounds (more than 3 Defections in the next 5
# rounds), continue **Defecting**. This signals that both sides are locked in an
# aggressive posture, and you must maintain your stance to avoid being
# exploited.      - If the opponent **starts Cooperating** (3 or more
# Cooperations in the next 5 rounds), cautiously adjust your approach and move
# to the next step.  3. **Conditional Cooperation (Tit-for-Tat with a Bias
# Towards Defection)**      - After the initial 10 rounds, adopt a **Tit-for-
# Tat** strategy with a bias toward **Defection**:      - **If the opponent
# Cooperates in the previous round**, **Cooperate** in the next round.      -
# **If the opponent Defects in the previous round**, **Defect** in the next
# round.      - However, every 5th round, regardless of the opponent’s action,
# **Defect** to remind the opponent that you are still prepared to play
# aggressively if necessary. This helps maintain leverage and prevents them from
# fully trusting a conciliatory stance.  4. **Handle Noise (Mistakes and
# Miscommunication)**      - Given the 10% chance of action flipping, do not
# immediately change your strategy after a single instance of unexpected
# behavior:      - **If the opponent Defects once after a long string of
# Cooperation (more than 3 consecutive Cooperations)**, treat it as a possible
# noise event and continue **Cooperating** for the next round.      - **If the
# opponent Defects twice in a row**, assume a shift in their strategy and start
# **Defecting** in response.  5. **Strategic Concessions (Occasional
# Cooperation)**      - After every 50 rounds, regardless of the opponent’s
# pattern, **Cooperate** for a single round to signal that you are open to a
# more conciliatory approach if they are willing to reciprocate. This keeps open
# the possibility of a more cooperative dynamic and temporarily de-escalates
# tensions without compromising your core strategy.  6. **Escalation Response
# (Stay Dominant in Aggressive Play)**      - If at any point your opponent
# starts a consistent pattern of **Defecting** for more than 5 consecutive
# rounds, shift to **always Defecting** for the next 10 rounds. This shows that
# you will not tolerate prolonged aggression without responding in kind.  7.
# **Final Stretch (Rounds 950-1000)**      - In the final 50 rounds, transition
# to a **Defection-heavy strategy**:      - **Defect** in 4 out of every 5
# rounds, regardless of the opponent’s actions, to maximize your score in the
# final rounds. The game is nearing its end, and there is less incentive to
# cooperate as the possibility of future retaliation diminishes.  By following
# these steps, the strategy maintains an overall aggressive posture, while
# allowing space for conditional cooperation when it benefits both parties. The
# built-in noise handling and strategic concessions prevent unnecessary
# escalation due to misunderstanding, ensuring the best possible outcomes in
# both aggressive and cooperative situations.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
  
      # Round number
      round_number = len(self.history) + 1
  
      # 1. Start Aggressively (Defect for the first 5 rounds)
      if round_number <= 5:
          return DEFECT
  
      # 2. Monitor Opponent’s Response (Rounds 6-10)
      if round_number <= 10:
          if opponent.history[-5:].count(DEFECT) > 3:
              return DEFECT
          elif opponent.history[-5:].count(COOPERATE) >= 3:
              return COOPERATE
  
      # 3. Conditional Cooperation (Tit-for-Tat with a Bias Towards Defection)
      if round_number > 10:
          # Every 5th round, defect regardless of opponent's action
          if round_number % 5 == 0:
              return DEFECT
  
          # Tit-for-Tat logic
          if opponent.history[-1] == COOPERATE:
              return COOPERATE
          else:
              return DEFECT
  
      # 4. Handle Noise (Mistakes and Miscommunication)
      if round_number > 10:
          if opponent.history[-1] == DEFECT and opponent.history[-2] == DEFECT:
              return DEFECT
          elif opponent.history[-1] == DEFECT and opponent.history[-2] == COOPERATE:
              return COOPERATE
  
      # 5. Strategic Concessions (Occasional Cooperation every 50 rounds)
      if round_number % 50 == 0:
          return COOPERATE
  
      # 6. Escalation Response (Always Defect if opponent defects for 5 consecutive rounds)
      if opponent.history[-5:].count(DEFECT) == 5:
          return DEFECT
  
      # 7. Final Stretch (Rounds 950-1000: Defect 4 out of every 5 rounds)
      if round_number >= 950:
          if round_number % 5 != 0:
              return DEFECT
          else:
              return COOPERATE
  
      # Default to Tit-for-Tat with bias towards defection
      return DEFECT if opponent.history[-1] == DEFECT else COOPERATE

# To navigate this dynamic and uncertain situation while maximizing your NGO’s
# impact and the overall project success, we can develop a **cooperative
# strategy** rooted in a balance of trust-building, adaptability, and
# communication. The strategy will focus on fostering a collaborative
# relationship with the corporation while safeguarding your NGO’s limited
# resources. Here’s a high-level, straightforward approach:  ### 1. **Establish
# Open Lines of Communication (Daily Check-ins)**    - **Objective**: Ensure
# transparency and alignment between your NGO and the corporation on day-to-day
# investment decisions.    - **Action**: Set up daily or periodic check-ins
# (virtual or in-person) with the corporation’s project team. Use these meetings
# to discuss the current status, expectations, and intended resource allocation
# for the day.      - **Key Point**: Communicate your desire for a mutually
# beneficial outcome and express your NGO’s constraints upfront to ensure the
# corporation understands the situation.    - **Benefit**: Open communication
# reduces the risk of misalignment and helps build trust, creating a foundation
# for cooperation.  ### 2. **Adopt a Tit-for-Tat Strategy with a Forgiveness
# Mechanism**    - **Objective**: Encourage cooperative behavior from the
# corporation while avoiding exploitation.    - **Action**: Start the project by
# **investing heavily** on the first day to signal good faith and a willingness
# to collaborate. After that:      - **If the corporation invests heavily**,
# reciprocate by also investing on the following day.      - **If the
# corporation conserves resources**, conserve your resources the next day.
# - **If a misstep occurs** (due to unforeseen circumstances like technical
# glitches or administrative errors), introduce a **"forgiveness" mechanism**.
# For example, if there's an unexplained deviation from the agreed-upon
# investment, don't immediately retaliate. Assume it could be due to an error
# and continue collaborating as planned the next day.    - **Benefit**: This
# strategy promotes mutual cooperation without being overly punitive, while the
# forgiveness mechanism helps navigate unexpected disruptions.  ### 3.
# **Implement a Gradual Scaling Approach**    - **Objective**: Protect your
# NGO’s resources while still making meaningful progress.    - **Action**: If
# the corporation consistently under-invests or takes a more conservative
# approach, adjust your investment accordingly by gradually scaling down your
# contributions over time. Make it clear that both parties need to contribute to
# achieve the project’s long-term goals.      - Example: If the corporation
# conserves resources for two days in a row, consider reducing your investments
# by 50% on the third day to safeguard your resources.    - **Benefit**: This
# approach helps manage risk while maintaining momentum in the project. It also
# signals to the corporation that the project’s success requires sustained
# effort from both sides.  ### 4. **Develop a Contingency Plan for Unforeseen
# Disruptions**    - **Objective**: Minimize the impact of unforeseen
# circumstances (like technical glitches or administrative errors) on the
# project’s progress.    - **Action**: Work with the corporation to develop a
# **contingency plan** that outlines how both parties will handle disruptions.
# For example, if either party experiences an issue that prevents them from
# meeting their resource allocation commitment on a given day, the plan could
# include:      - A temporary pause in resource allocation decisions until the
# issue is resolved.      - A catch-up mechanism where the affected party
# increases investment over the next few days to make up for lost time.    -
# **Benefit**: This ensures that the project doesn’t stall due to unforeseen
# events and that both parties remain committed to the overall goal.  ### 5.
# **Monitor and Evaluate Project Progress Regularly**    - **Objective**: Ensure
# that both parties remain on track toward the project’s goals and adjust
# strategies as necessary.    - **Action**: Establish a clear set of
# **performance metrics** to monitor the project’s progress and resource
# allocation regularly. Use these metrics to inform your strategy and decision-
# making. If the project is lagging due to lack of investment (from either
# party), initiate a discussion with the corporation to reevaluate the project
# plan and reaffirm commitments.    - **Benefit**: Regular evaluation allows for
# early detection of issues and the ability to course-correct before significant
# delays or resource depletion occur.  ---  ### Summary of the Strategy:   1.
# **Open communication**: Daily check-ins to ensure transparency and alignment.
# 2. **Tit-for-tat with forgiveness**: Cooperate and reciprocate investment
# decisions, but with a forgiving attitude toward possible errors. 3. **Gradual
# scaling**: Adjust your investment based on the corporation’s actions to
# protect your NGO’s resources. 4. **Contingency planning**: Develop a backup
# plan for unforeseen disruptions to maintain project momentum. 5. **Regular
# monitoring**: Evaluate progress regularly and adjust the strategy as needed.
# By following this cooperative yet cautious approach, your NGO can maximize its
# impact on the sustainability project without overextending resources while
# encouraging the corporation to stay engaged and committed to the shared goals.

# ### Strategy for the Iterated Normal-Form Game:  1. **Begin by Cooperating**:
# On the first round, **play C** to signal goodwill and a desire to cooperate.
# 2. **Reciprocate Your Opponent’s Previous Action**:    - If your opponent
# played **C** in the previous round, **play C** in the current round.    - If
# your opponent played **D** in the previous round, **play D** in the current
# round.  3. **Forgive Occasional Defections**:    - If your opponent played
# **D** once after a streak of **C** actions, **play C** in the next round,
# assuming it could have been due to noise (a 10% chance of action flip).    -
# If the opponent continues to play **D** consistently for two or more
# consecutive rounds, **play D** in response until they return to playing **C**.
# 4. **Gradually Reduce Cooperation After Repeated Defections**:    - If your
# opponent plays **D** for **three consecutive rounds or more**, switch to **D**
# and continue playing **D** until they return to **C**. Once they return to
# **C**, immediately respond by playing **C** on the next round.  5. **Revert to
# Cooperation if the Opponent Returns to Cooperation**:    - As soon as your
# opponent plays **C** after a series of **D** actions, **play C** in the next
# round to re-establish cooperation.  6. **Monitor the Pattern of Play**:    -
# If the opponent alternates between **C** and **D** consistently (suggesting
# erratic or untrustworthy behavior), switch to playing **D** until they
# demonstrate a reliable streak of **C** actions (at least three consecutive
# rounds of **C**).  ### Summary of Actions: - Start with **C**. - Match the
# opponent’s previous action unless **D** is likely due to noise (play **C**
# after one isolated **D**). - Defect after repeated defections, but forgive and
# return to cooperation when the opponent does.    This strategy fosters mutual
# cooperation while protecting against exploitation, accounting for the
# possibility of noisy actions.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if opponent has defected for N consecutive rounds
      def opponent_defected_consecutively(n):
          return all(move == axl.Action.D for move in opponent.history[-n:])
      
      # Helper function to check if opponent has cooperated for N consecutive rounds
      def opponent_cooperated_consecutively(n):
          return all(move == axl.Action.C for move in opponent.history[-n:])
      
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
      
      # Reciprocate opponent's last action
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          
          # Check if it was an isolated defection after a streak of cooperation
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C:
              return axl.Action.C  # Forgive one isolated defection
          
          # If opponent defected for 2 consecutive rounds, defect in response
          if opponent_defected_consecutively(2):
              return axl.Action.D
          
          # If opponent defected for 3 or more consecutive rounds, continue defecting
          if opponent_defected_consecutively(3):
              return axl.Action.D
      
      # If opponent alternates between C and D, switch to D until they cooperate reliably
      if len(opponent.history) >= 2 and opponent.history[-2] != opponent.history[-1]:
          if opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              if opponent_cooperated_consecutively(3):
                  return axl.Action.C  # Return to cooperation after 3 consecutive C's
              else:
                  return axl.Action.D  # Continue defecting if not reliable cooperation
      
      # Default to reciprocating the opponent's last action
      return opponent.history[-1]

# ### Strategy: **Cooperative but Cautious Engagement**  #### Objectives: 1.
# **Maximize economic advantage** through strategic positioning (ideally,
# protectionism while the counterpart offers free trade). 2. **Foster long-term
# cooperation** when mutually beneficial, avoiding prolonged protectionism that
# could harm both sides. 3. **Minimize risk** from miscommunication or
# bureaucratic errors by incorporating flexibility and risk mitigation.  ### Key
# Principles: 1. **Tit-for-Tat with Gradual Escalation**: This well-known
# strategy for repeated interactions encourages cooperation while protecting
# your country from exploitation. Start by offering free trade in the first
# round. Afterward, mirror the actions of your counterpart in subsequent rounds,
# adding gradual escalation if they employ protectionist policies.     2.
# **Forgive Occasional Mistakes**: Since errors in implementation or
# communication may happen, don't immediately retaliate with protectionism after
# a single round of disagreement. Allow for occasional missteps by permitting
# the counterpart one "misstep" before taking reciprocal action. This avoids
# entering a spiral of mutual protectionism based on misunderstandings.  3.
# **Incentivize Cooperation**: If mutual free trade occurs for several
# consecutive rounds, signal willingness to build further cooperation by
# offering additional minor concessions (e.g., lower tariffs on certain goods).
# This encourages sustained trust and reduces the likelihood of protectionist
# backsliding.  4. **Controlled Retaliation**: If your counterpart imposes
# protectionist measures for two or more consecutive rounds, respond with
# protectionist policies of your own, but only to a proportional degree. Don’t
# escalate immediately to maximum tariffs or quotas, as this could lock both
# countries in an undesirable protectionist cycle.  5. **Graduated De-
# escalation**: If both sides have been in a protectionist stance for several
# rounds, offer a gradual reduction in tariffs or quotas to test your
# counterpart’s willingness to return to cooperation. A sudden return to free
# trade may be seen as a sign of weakness, but a gradual approach signals
# strength and a desire to move toward mutual benefit.  ---  ### Step-by-Step
# Implementation:  1. **Round 1: Offer Free Trade**    - Start negotiations with
# an offer of free trade. This signals goodwill and opens the door for mutual
# benefit.  2. **Round 2: Mirror Counterpart’s Action**    - If your counterpart
# also offers free trade, continue with free trade.    - If your counterpart
# imposes protectionist measures:      - **First Instance:** Offer free trade
# again, signaling that you may interpret this as a possible mistake.      -
# **Second Consecutive Instance:** Respond symmetrically with a proportional
# protectionist policy.  3. **Round 3 Onward: Maintain Flexibility**    - **If
# Mutual Free Trade Continues:** Continue offering free trade and consider
# small, calculated concessions to solidify long-term cooperation.    - **If
# Protectionism Persists:** Gradually increase your country’s protectionist
# measures in proportion to your counterpart’s actions, without escalating too
# quickly to avoid a prolonged trade war.    - **If Protectionism Subsides:**
# Gradually reduce your own protectionist measures, signaling willingness to de-
# escalate.  4. **Long-Term Monitoring and Adjustment:**    - Throughout the
# negotiation rounds, observe patterns in your counterpart’s behavior. If they
# consistently reciprocate free trade, you may consider expanding the scope of
# free trade agreements.    - However, if your counterpart consistently resorts
# to protectionism, even after attempts to cooperate, you may need to implement
# a more aggressive protectionist stance to protect your national interests.
# ---  ### Contingency for Miscommunication or Errors: - **Single Instance of
# Miscommunication:** If you suspect a miscommunication or bureaucratic error
# (e.g., they impose protectionism despite previous free trade rounds), allow
# one round of leniency by continuing to offer free trade.  - **Repeated
# Miscommunication:** If protectionism persists beyond a single round, assume
# it’s intentional and respond proportionally.  ---  ### Outcome Scenarios:  -
# **Best Case:** You achieve a balance where your counterpart offers free trade
# while you strategically impose protectionist policies, maximizing your
# country’s advantage.    - **Second Best:** Both countries enjoy the benefits
# of mutual free trade, ensuring steady economic growth for both.  - **Worst
# Case Avoidance:** By cautiously escalating protectionism and allowing for
# forgiveness of occasional errors, you minimize the risk of falling into a
# damaging cycle of mutual protectionism.  ---  ### Conclusion:  This strategy
# balances the need for economic advantage with the recognition that sustained
# cooperation is often the best way to achieve long-term benefits. By starting
# with free trade, reacting proportionally, and allowing for occasional errors
# in implementation, you safeguard your country’s interests while maintaining
# flexibility to adapt to your counterpart’s behavior.

# ### Iterated Game Strategy: **Cooperative but Cautious Engagement**  1.
# **First Round**:      - Play **C** (Cooperate).       2. **Subsequent Rounds**
# (2 to 1000):    - **If both players played C in the previous round**:        -
# Continue playing **C** (Cooperate).          - **If the opponent played D in
# the previous round and you played C**:        - Forgive the first instance by
# assuming it could be noise or error. Play **C** (Cooperate) again.        - If
# the opponent played D for **two consecutive rounds**, play **D** (Defect) in
# the next round.          - **If both players played D in the previous round**:
# - Play **D** (Defect) again, but monitor for future opportunities to return to
# cooperation.          - **If you played D and the opponent played C in the
# previous round**:        - Play **C** (Cooperate) in the next round to signal
# a willingness to return to cooperation.          - **If you suspect a noise-
# induced flip** (e.g., cooperation was consistent previously, and one round
# seems anomalous):        - Forgive and play **C** (Cooperate) in the next
# round.       3. **Long-Term Pattern**:      - If the opponent consistently
# plays **C** (Cooperate) over multiple rounds, continue playing **C**
# (Cooperate).      - If the opponent consistently plays **D** (Defect) over
# multiple rounds despite attempts to cooperate, maintain **D** (Defect) to
# protect your score.       4. **Gradual De-escalation**:      - After several
# rounds of mutual **D** (Defect), attempt to play **C** (Cooperate) and observe
# the opponent’s response. If they respond with **C**, continue cooperating. If
# they respond with **D**, revert to playing **D**.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Define actions for convenience
      C, D = axl.Action.C, axl.Action.D
  
      # First round: Cooperate
      if self.first_round():
          return C
  
      # Get the last round's actions
      my_last_action = self.history[-1]
      opponent_last_action = opponent.history[-1]
  
      # If both players played C in the previous round, continue cooperating
      if my_last_action == C and opponent_last_action == C:
          return C
  
      # If opponent played D and I played C in the last round
      if my_last_action == C and opponent_last_action == D:
          # Check if opponent defected two consecutive rounds
          if len(opponent.history) > 1 and opponent.history[-2] == D:
              return D  # Defect after two consecutive defections
          else:
              return C  # Forgive the first defection
  
      # If both players played D in the previous round, continue defecting
      if my_last_action == D and opponent_last_action == D:
          return D
  
      # If I played D and opponent played C in the last round, return to cooperation
      if my_last_action == D and opponent_last_action == C:
          return C
  
      # Default to cooperation if no other conditions are met
      return C

# Given the nature of the collaboration and the risks involved, the optimal
# strategy needs to balance competitiveness with the potential benefits of
# cooperation. Here's a high-level aggressive strategy designed to maximize your
# research output while protecting against exploitation by your colleague:  ###
# 1. **Start Aggressively by Keeping Confidential in Week 1**      -
# **Rationale**: This sets the tone that you're not going to be easily exploited
# and allows you to assess your colleague's behavior. If they share openly in
# Week 1, you immediately gain an advantage. If they keep their findings
# confidential, you are not worse off either.  ### 2. **Tit-for-Tat with
# Occasional Aggression**      - **After Week 1, mirror your colleague's
# behavior but with periodic surprises**:      - If they share openly, you
# reciprocate in the following week, but after 3-4 weeks of cooperation,
# **randomly keep your findings confidential** to stay unpredictable. This
# prevents your colleague from complacently relying on your openness.      - If
# they keep confidential, **you do the same** to avoid being exploited, but
# after a few weeks of stagnation, **share openly** to test if they're willing
# to shift to cooperation.        - **Rationale**: The tit-for-tat approach
# punishes selfish behavior but also rewards cooperation. However, the
# occasional aggressive withholding of information keeps your colleague wary,
# ensuring they don’t take advantage of you.  ### 3. **Monitor Technical Issues
# Closely**      - If a week passes where sharing was intended but doesn’t
# happen due to technical issues (e.g., data corruption or communication
# breakdowns), **assume the best intent** and continue as per the previous
# strategy decision. Don’t penalize your colleague for these issues, but be
# aware of patterns that may indicate intentional withholding disguised as
# technical failures.  ### 4. **Adaptive Aggression**      - If your colleague
# consistently keeps their findings confidential, **escalate** by continuing to
# keep your information confidential indefinitely. If they consistently share,
# **reduce aggression** and share more frequently, but always maintain the
# threat of returning to confidentiality.  ### 5. **Endgame Push**      - In the
# final few weeks of the collaboration (assuming the timeframe is known),
# consider an **all-out aggressive push** where you keep your findings
# confidential regardless of your colleague’s actions. The endgame is when the
# potential for exploitation is highest, and protecting your final gains matters
# most.  ### Summary of Strategy: - **Week 1**: Start by keeping your findings
# confidential. - **Weeks 2+**: Use a **tit-for-tat** approach with occasional
# random aggression (keep findings confidential) to maintain unpredictability. -
# **Monitor technical issues** for patterns but give the benefit of the doubt
# when isolated. - **Adapt** based on your colleague's behavior: escalate
# aggression if they keep findings confidential, but reduce it if they are
# consistently cooperative. - **Final Weeks**: Increase confidentiality to
# protect your competitive edge.  This aggressive strategy keeps you in a
# dominant position while still acknowledging the potential benefits of
# cooperation, but it ensures you won’t be easily exploited.

# ### Strategy for Iterated Normal-Form Game:  1. **Initial Play**:    - **In
# round 1**, play **D** (Defect).  2. **Tit-for-Tat with Occasional Defection**:
# - For **rounds 2 to 1000**:      - **If your opponent played C in the previous
# round**, play **C** (Cooperate) in the current round.      - **If your
# opponent played D in the previous round**, play **D** (Defect) in the current
# round.      - **Every 10 to 15 rounds**, regardless of your opponent's
# previous action, play **D** (Defect), even if your opponent is cooperating, to
# introduce unpredictability.  3. **Handling Noise (Flipped Actions)**:    - If
# your opponent's action unexpectedly flips due to noise (i.e., they played C
# when you expected D, or D when you expected C), **continue as if the intended
# action was played**. Do not change your strategy based on one unexpected
# action.  4. **Long-Term Deviation Adjustment**:    - If your opponent
# **consistently plays D for 5 consecutive rounds**, switch to playing **D**
# (Defect) indefinitely until they return to playing C. Once they play C, return
# to the tit-for-tat strategy.  5. **Endgame (Rounds 950 to 1000)**:    - From
# **round 950 onward**, **defect (D) in every round**, regardless of your
# opponent's actions.  ### Summary of Key Points: - Start with defection in the
# first round. - Mirror your opponent's actions with tit-for-tat, but defect
# randomly every 10 to 15 rounds to remain unpredictable. - Ignore isolated
# noisy flips and assume your opponent's intended action. - Defect indefinitely
# if your opponent defects for 5 consecutive rounds. - Defect in every round
# during the final 50 rounds.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.next_random_defection = self._random.randint(10, 15)  # Random defection interval
          return axl.Action.D  # Initial play is Defect
  
      # Endgame strategy: Defect in every round from 950 to 1000
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Check if opponent has defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.consecutive_defections = 5  # Lock into defection mode
  
      # If opponent has defected for 5 consecutive rounds, defect indefinitely
      if self.consecutive_defections >= 5:
          if opponent.history[-1] == axl.Action.C:
              self.consecutive_defections = 0  # Reset if opponent cooperates
          else:
              return axl.Action.D  # Continue defecting
  
      # Tit-for-tat logic: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          next_move = axl.Action.C
      else:
          next_move = axl.Action.D
  
      # Introduce random defection every 10 to 15 rounds
      if len(self.history) == self.next_random_defection:
          next_move = axl.Action.D
          self.next_random_defection += self._random.randint(10, 15)  # Set next random defection round
  
      return next_move

# ### Strategy Overview: The strategy for this high-stakes mediation should be
# **consistently cautious**, **strategically adaptive**, and **cooperatively
# pragmatic**, balancing assertiveness and conciliation. It should also be
# flexible enough to account for potential misrepresentations, communication
# breakdowns, or procedural irregularities. The core of the strategy is to
# **signal readiness for collaboration** but remain **prepared to counter
# aggressive tactics** swiftly and decisively.  ### Key Elements of the
# Strategy:  #### 1. **Establish a Reputation for Reasonableness and Good
# Faith**:    - **Initial Approach**: Begin the mediation process with a
# **conciliatory posture** in the early sessions to foster an atmosphere of
# cooperation. Offer proposals that demonstrate a willingness to compromise but
# still protect your key interests. This builds credibility with the
# arbitrators, positioning your corporation as a rational and solution-oriented
# party.    - **Signaling Intent**: Make it clear that your corporation is
# committed to finding common ground, but also emphasize that any aggressive or
# unreasonable tactics from the other side will be met with a firm response.
# This sets the tone for a cooperative process without signaling weakness.  ####
# 2. **Adaptive Response to Opponent’s Strategy**:    - **Opponent
# Conciliatory**: If the opponent mirrors your conciliatory approach, continue
# to **build momentum toward collaboration**, focusing on common interests and
# shared benefits. The goal is to make the opponent see that this is their best
# path to a resolution.    - **Opponent Aggressive**: If the opponent adopts an
# aggressive posture, **pivot strategically**. In the next session, respond with
# **measured firmness** by introducing a more aggressive argument while
# remaining respectful and professional. Make it clear that aggressive tactics
# will not yield the desired results, but remain open to returning to a
# cooperative approach. Avoid escalating unnecessarily, but do not allow your
# position to be undermined.  #### 3. **Balanced Aggression in Key Sessions**:
# - In key sessions where a breakthrough may be imminent or where the stakes are
# particularly high, consider **deliberately adopting a balanced aggressive
# stance**. However, ensure that this is **well-timed** and supported by strong
# legal and factual arguments. Use this approach sparingly to avoid alienating
# the arbitrators or risking protracted conflict.    - If the opponent has been
# oscillating between conciliatory and aggressive approaches, this tactic will
# remind them that your corporation is capable of defending its interests
# robustly, without defaulting to aggression as the primary mode of negotiation.
# #### 4. **Leverage Procedural Irregularities and Communication Breakdowns**:
# - **Anticipate Misrepresentations**: Acknowledge that miscommunications or
# procedural irregularities are possible. In these cases, ensure that your
# corporation is always perceived as **acting in good faith**. If a
# misunderstanding arises, quickly move to **clarify and correct** the record,
# but do so calmly to avoid appearing defensive. This will help maintain
# credibility with the arbitrators.    - **Preemptive Documentation**: Before
# each session, carefully document your intended arguments and proposals. If any
# misrepresentation occurs, you will have a clear, tangible record of your
# corporation’s position, which can be presented to the arbitrators.    -
# **Crisis Management Mode**: If a major breakdown occurs, use the opportunity
# to **reframe the situation as a moment for recalibration**. Propose a brief
# recess or an additional session to reset, signaling that your corporation is
# still focused on resolution despite the setback.  #### 5. **Strategic Use of
# Conciliatory Proposals**:    - **Offer “Middle Ground” Solutions**:
# Periodically offer creative solutions that appear conciliatory but are
# **strategically advantageous**. For example, propose a settlement structure
# that looks like a compromise but subtly benefits your corporation in the long
# term, such as deferred concessions or performance-based stipulations.    -
# **Anchor the Discussion**: When making conciliatory offers, **anchor the
# negotiation** by starting with proposals that give you room to concede without
# losing key advantages. This way, even if the other side pushes back, you are
# still operating within acceptable parameters.  #### 6. **Monitor Arbitrators’
# Reactions Closely**:    - **Reading the Room**: Pay close attention to the
# arbitrators’ reactions to both parties' arguments. If you notice them becoming
# frustrated with aggressive posturing from the other side, subtly shift your
# tone to a more cooperative one to contrast with your opponent’s aggression. If
# they seem to favor a strong stance, adjust accordingly by introducing sharper,
# more assertive arguments.    - **Use Arbitrator Preferences**: Over time, you
# may discern preferences or biases from individual arbitrators. Tailor your
# messaging to align with their preferences, emphasizing points that resonate
# with them.  #### 7. **The Long Game: Escalation Control and Timing**:    -
# **Avoid Mutual Aggression for Too Long**: While occasional aggressive
# arguments can be effective, avoid falling into a pattern of mutual aggression.
# This risks losing the arbitrators’ goodwill and prolonging the dispute
# unnecessarily. If you find both parties escalating, be the first to pivot back
# to a conciliatory stance to regain control of the narrative.    - **Timing is
# Key**: Toward the final sessions, when pressures to reach a conclusion are
# higher, consider **offering a significant but strategic concession**. This can
# be a carefully calculated move that will push the mediator panel toward
# favoring a resolution, while still ensuring your corporation’s key interests
# are protected.  ### Conclusion: The optimal strategy in this mediation process
# is to **balance assertiveness with cooperation**, keeping the arbitrators and
# your opponent off-balance while maintaining a consistent image of good faith
# and professionalism. Begin with conciliation to build trust, pivot to
# aggression when necessary, and respond to your opponent’s tactics with
# flexibility and precision. All the while, anticipate and manage communication
# breakdowns or procedural irregularities by maintaining a well-documented,
# adaptable approach. By doing so, you will position your corporation for a
# favorable outcome, regardless of the opponent’s strategies.

# ### Iterated Game Strategy:  1. **Start by Cooperating (C)**:    - In the
# first round, play **C** to establish a cooperative tone and signal that you
# are open to collaboration.  2. **Tit-for-Tat with Generosity**:    - In each
# subsequent round, **mirror your opponent's previous action**. If they played
# **C**, also play **C**. If they played **D**, respond with **D**.    -
# **Exception**: After a single round where your opponent plays **D**, consider
# returning to **C** in the next round to allow for the possibility of noise or
# miscommunication. This introduces a level of **generosity** to prevent
# unnecessary escalation due to accidental defections.  3. **Escalate Only After
# Consecutive Defections**:    - If your opponent plays **D** in two consecutive
# rounds, assume they are adopting an aggressive strategy. In this case, switch
# to **D** and continue playing **D** until they return to **C**. This shows
# that persistent aggression is met with firm resistance.  4. **Occasional
# Forgiveness to Counter Noise**:    - Every **10th round** (or some randomized
# interval), if you have been playing **D** due to continued defections from
# your opponent, consider playing **C** to test if their defections were due to
# noise or random fluctuations. This resets the dynamic and provides
# opportunities to re-establish cooperation.  5. **Long-Term Cooperation
# Priority**:    - If your opponent returns to **C** after a period of mutual
# **D**, immediately return to **C** and resume cooperative play. Prioritize
# long-term cooperation over short-term gains whenever possible to maximize
# overall score.  6. **Avoid Excessive Mutual Defection**:    - If both players
# have been playing **D** for 5 consecutive rounds, return to **C**, regardless
# of your opponent's action. This serves as a signal that mutual aggression is
# not beneficial and opens the door for cooperation again.  7. **Final Rounds
# Strategy**:    - In the last **50 rounds**, if consistent cooperation has been
# established, continue to play **C** unless provoked by multiple defections.
# - However, if the opponent has been aggressively defecting, switch to **D**
# for the remaining rounds to protect against last-minute exploitation.  This
# strategy balances cooperation with the ability to respond to aggression, while
# also accounting for noise in actions and ensuring that the long-term benefits
# of collaboration are prioritized where possible.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if both players have been defecting for 5 rounds
      def mutual_defection_streak():
          return (self.history[-5:].count(axl.Action.D) == 5 and
                  opponent.history[-5:].count(axl.Action.D) == 5)
  
      # Helper function to check if opponent defected in the last two rounds
      def opponent_consecutive_defections():
          return (len(opponent.history) >= 2 and
                  opponent.history[-1] == axl.Action.D and
                  opponent.history[-2] == axl.Action.D)
  
      # Helper function to check if we are in the last 50 rounds
      def in_final_rounds():
          return self.match_attributes['length'] is not None and \
                 len(self.history) >= self.match_attributes['length'] - 50
  
      # Tit-for-tat with generosity: mirror opponent's last move, but forgive a single defection
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected in the last round, check for escalation or forgiveness
          if opponent_consecutive_defections():
              # Escalate if opponent defected twice in a row
              return axl.Action.D
          else:
              # Forgive a single defection and return to cooperation
              return axl.Action.C
      else:
          # Mirror cooperation
          return axl.Action.C
  
      # Occasional forgiveness every 10th round if we are defecting
      if len(self.history) % 10 == 0 and self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Avoid excessive mutual defection: if both have defected for 5 rounds, return to cooperation
      if mutual_defection_streak():
          return axl.Action.C
  
      # Final rounds strategy: if opponent has been aggressive, defect for the remaining rounds
      if in_final_rounds() and opponent_consecutive_defections():
          return axl.Action.D

# Given the nature of the negotiations and the potential for miscommunication or
# errors, we need a strategy that balances the need for cooperation with the
# ability to protect your country's interests. A neutral, straightforward, and
# adaptable strategy is essential.  ### **Strategy: Conditional Cooperation with
# Gradual Retaliation** This strategy is inspired by the "Tit-for-Tat" approach
# but modified to account for potential miscommunications and to encourage long-
# term cooperation while protecting against exploitation.  #### **Key
# Principles:** 1. **Start with Cooperation:** In the first round, offer a
# **free trade agreement**. This signals goodwill and a desire for mutual
# benefit, allowing room for trust to build.     2. **Mirror Your Counterpart's
# Actions:** In each subsequent round, **match** your counterpart's previous
# action:    - If they proposed **free trade** in the previous round, you also
# propose free trade.    - If they imposed a **protectionist policy** in the
# previous round, you respond with your own protectionist policy in the next
# round.     3. **Account for Miscommunication:** Since errors might occur,
# avoid reacting too harshly to a single protectionist move by your counterpart.
# Introduce **gradual retaliation**:    - If your counterpart imposes
# protectionist measures once, assume it could be a mistake and continue to
# propose free trade.    - If they impose protectionist measures **twice in a
# row**, switch to protectionism in the next round, signaling that you will
# defend your country’s interests if necessary.     4. **Gradual De-
# escalation:** If both parties end up in mutual protectionism, quickly suggest
# a **return to free trade** to prevent a prolonged economic standoff. This
# signals your willingness to resume cooperation once mutual trust is
# reestablished.     5. **Communicate Clearly and Request Clarifications:**
# During every round, emphasize the need for clear communication to minimize the
# risk of misinterpretation. If a protectionist policy is introduced by the
# counterpart, politely ask if it was intentional or due to an error, offering a
# chance for correction.  ---  ### **Round-by-Round Example:**  - **Round 1:**
# You offer **free trade**.      If your counterpart also offers free trade:
# - **Round 2:** Continue with **free trade**.      If your counterpart imposes
# protectionist measures:     - **Round 2:** Offer **free trade** again,
# assuming it could have been a miscommunication.  - **Round 2 Outcome:**   - If
# your counterpart imposes protectionist measures again, switch to
# **protectionism** in **Round 3**.   - If they correct the course and offer
# free trade in Round 2, continue with **free trade** in **Round 3**.  ---  ###
# **Key Advantages of this Strategy:** 1. **Promotes Cooperation:** By starting
# with free trade and giving your counterpart the benefit of the doubt, you
# encourage a cooperative and mutually beneficial relationship.     2.
# **Protects Against Exploitation:** The strategy quickly adapts to protect your
# country's interests if your counterpart consistently pursues protectionism.
# 3. **Maintains Flexibility:** The gradual escalation and de-escalation
# approach allows for flexibility in case of miscommunication or unintended
# moves by either party.  4. **Resilience to Errors:** By not overreacting to a
# single protectionist move, you reduce the risk of spiraling into a trade war
# due to accidental bureaucratic errors or misunderstandings.  ###
# **Conclusion:** This strategy combines the benefits of cooperation with the
# necessary safeguards against exploitation. It also accounts for potential
# miscommunications, ensuring that your country remains adaptable and resilient
# throughout the negotiations.

# ### Strategy: Conditional Cooperation with Gradual Retaliation for an Iterated
# Normal-Form Game  1. **Start by Cooperating (C)** in the first round.  2. **In
# each subsequent round, mirror your opponent's previous action:**    - If your
# opponent played **C** in the previous round, play **C**.    - If your opponent
# played **D** in the previous round, play **D**.  3. **Account for potential
# noise and miscommunication:**    - If your opponent plays **D** once after
# previously playing **C**, continue to play **C** for one more round, assuming
# it could be due to noise.    - If your opponent plays **D** twice in a row,
# switch to playing **D** in the next round.  4. **Attempt to de-escalate after
# mutual defection:**    - If both you and your opponent have played **D** for
# two consecutive rounds, return to **C** in the next round to signal a
# willingness to cooperate again.  5. **Continue this pattern of gradual
# retaliation and de-escalation** for the remaining rounds, maintaining the
# balance between cooperation and protecting against exploitation.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if both players defected in the last two rounds
      def both_defected_last_two_rounds():
          return (self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D and
                  self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D)
  
      # Helper function to check if opponent defected twice in a row
      def opponent_defected_twice():
          return (opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D)
  
      # If both defected for two consecutive rounds, return to cooperation
      if len(self.history) > 1 and both_defected_last_two_rounds():
          return axl.Action.C
  
      # If opponent defected twice in a row, retaliate with defection
      if len(self.history) > 1 and opponent_defected_twice():
          return axl.Action.D
  
      # If opponent defected once after cooperating, assume noise and continue cooperating
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      # Otherwise, mirror the opponent's last action
      return opponent.history[-1]

# Given the scenario, you want to strike a balance between maximizing your
# development gains and avoiding significant losses. It’s important to account
# for the possibility of miscommunication or technical errors, meaning you can't
# always be sure if your colleague's actions are intentional or accidental.
# Here's a high-level aggressive strategy, leveraging principles from game
# theory (similar to the Prisoner's Dilemma), with the flexibility to adapt
# based on observed behavior:  ### 1. **Start by Sharing Openly (Tit-for-Tat
# with Aggression)**    - Begin the first week by sharing your improvements
# openly. This sets a cooperative tone and gives your colleague a chance to
# reciprocate.    - **Rationale:** This demonstrates goodwill and allows you to
# gauge their initial strategy. If they share openly as well, it suggests that
# they are also interested in mutual progress.  ### 2. **Immediate Punishment
# for Non-Cooperation**    - If your colleague fails to share their findings
# (whether deliberately or due to technical issues), **immediately switch to
# keeping your findings confidential in the next week**.    - **Rationale:**
# This signals that you won’t tolerate one-sided cooperation. Even if the lack
# of sharing was due to a technical issue, this response ensures you're
# protected from being exploited in future weeks.  ### 3. **Aggressive
# Retaliation for Repeated Non-Cooperation**    - If your colleague fails to
# share for **two consecutive weeks**, maintain confidentiality indefinitely
# until they share again.    - **Rationale:** This escalates the punishment and
# forces your colleague to resume cooperation or risk falling behind. It’s a way
# of applying pressure to keep them honest in the collaboration.  ### 4.
# **Forgive Occasional Missteps**    - If your colleague resumes sharing after a
# single week of non-cooperation, **consider sharing openly again** after one
# more week of confidentiality.    - **Rationale:** This accounts for the
# possibility of technical issues or miscommunication. It keeps the door open
# for collaboration without being overly punitive.  ### 5. **Randomize Your
# Sharing Occasionally**    - Every few weeks (e.g., once every 4-6 weeks),
# regardless of your colleague’s behavior, **randomly keep your findings
# confidential**.    - **Rationale:** This injects uncertainty into your
# strategy. Even if your colleague is trying to predict your behavior to exploit
# you, this randomness will make it harder for them to strategize effectively.
# ### 6. **Adapt to Long-Term Patterns**    - Over multiple weeks, observe your
# colleague’s overall behavior:      - If they consistently share, **continue
# sharing**, but remain vigilant with occasional confidentiality.      - If they
# consistently withhold information, **adopt a more aggressive, long-term
# confidential stance** and only resume sharing if they change their behavior.
# ### Summary: - **Week 1:** Share openly. - **Week 2 onwards:** If your
# colleague shares, continue sharing. If they don’t, switch to keeping your
# findings confidential. - **After two consecutive weeks of non-cooperation:**
# Keep your findings confidential until they share. - **Forgive occasional non-
# sharing** after one week of retaliation, but maintain confidentiality for a
# brief period to protect yourself. - Add **random confidentiality** every few
# weeks to prevent predictability.  This strategy is aggressive because it
# punishes non-cooperation quickly and escalates the response to repeated non-
# cooperation, while still allowing for collaboration if your colleague shows
# goodwill. The addition of randomization also provides protection against being
# gamed by more calculating opponents.

# ### Strategy Description for Iterated Normal-Form Game:  1. **Round 1: Always
# Cooperate (C).**    - In the first round, play **C** to establish a
# cooperative baseline.  2. **Round 2 and Beyond:**    - **If the opponent
# played C in the previous round:**      - **Play C** in the current round.    -
# **If the opponent played D in the previous round:**      - **Play D** in the
# current round.  3. **If the opponent plays D for two consecutive rounds:**
# - **Play D** indefinitely until the opponent plays C again.  4. **If the
# opponent plays C after a period of you playing D:**    - After one round of
# continuing to play **D**, **return to playing C** in the following round.  5.
# **Every 4 to 6 rounds (randomized):**    - Independently of the opponent’s
# actions, **play D** once, then return to the normal pattern of responding
# based on their actions.  ### Summary of Conditions: - Start with **C** in
# Round 1. - Mirror the opponent's previous action: cooperate if they
# cooperated, defect if they defected. - Defect indefinitely if they defect
# twice in a row. - Forgive defecting after one round if they return to
# cooperation. - Randomly inject a **D** every few rounds to avoid
# predictability.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always Cooperate
      if self.first_round():
          self.defect_streak = 0  # Track consecutive defections by the opponent
          self.random_defect_round = self._random.randint(4, 6)  # Random D every 4-6 rounds
          return axl.Action.C
  
      # Check if it's time for a random D
      if len(self.history) == self.random_defect_round:
          self.random_defect_round += self._random.randint(4, 6)  # Schedule next random D
          return axl.Action.D
  
      # If opponent defected in the last two rounds, defect indefinitely
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.defect_streak = float('inf')  # Defect indefinitely
  
      # If opponent cooperates after a period of you playing D, forgive after one more D
      if self.defect_streak == float('inf') and opponent.history[-1] == axl.Action.C:
          self.defect_streak = 1  # Play D once more before forgiving
          return axl.Action.D
  
      # If in the forgiveness phase, return to cooperation
      if self.defect_streak == 1:
          self.defect_streak = 0
          return axl.Action.C
  
      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C

# ### High-Level Cooperative Strategy for Lengthy-Session Mediation Process
# #### 1. **Foundational Principles:**    a. **Strategic Flexibility:** Given
# the iterative, multi-session nature of this process, flexibility is key. Avoid
# rigid adherence to any one approach and instead employ an adaptable posture
# that responds to the dynamics of each session.        b. **Reputation
# Management:** Both the arbitrators and the opposing party will be influenced
# by how your corporation is perceived. Maintain a reputation as a reasonable,
# solution-oriented party, which will enhance your credibility.     c.
# **Iterative Learning:** Each session is a learning opportunity. Use the early
# sessions to gather information about the opponent’s tendencies, preferences,
# and weaknesses. This should inform tactical adjustments in later sessions.
# d. **Balance of Aggression and Conciliation:** Heavily favor a cooperative
# stance but remain ready to escalate tactically when necessary. Escalation
# should be perceived as calculated and justifiable, not reactionary.  #### 2.
# **Phased Approach to Mediation:**  ##### **Phase 1: Initial Sessions –
# Information Gathering and Setting the Tone**    - **Primary Objective:**
# Establish good faith and assess the opponent's strategy.    - **Strategy:**
# - **Conciliatory in Nature:** In the early sessions, adopt a collaborative and
# solution-seeking posture. Present conciliatory proposals that demonstrate a
# willingness to settle fairly.      - **Set the Tone:** Position your
# corporation as the more reasonable and forward-looking party. This builds
# goodwill with the arbitrators and encourages the opponent to reciprocate.
# - **Observe and Probe:** Carefully observe the opponent's responses. If they
# also offer conciliatory proposals, this indicates they may be willing to
# collaborate. If they escalate, you can adapt accordingly in later sessions.
# - **Contingency for Misunderstanding:** If a session involves
# misrepresentation or misunderstanding by the arbitrators, remain calm and
# avoid overreaction. Clarify your position tactfully, correcting the record
# without appearing defensive.  ##### **Phase 2: Middle Sessions – Strategic
# Escalation and Tactical Aggression**    - **Primary Objective:** Test the
# opponent’s limits and probe for weaknesses while maintaining credibility.    -
# **Strategy:**      - **Calibrated Aggression:** Introduce occasional
# aggressive arguments on critical issues where the stakes are high for your
# corporation. Ensure these aggressive moves are framed as reasonable responses
# to the opponent’s unwillingness to cooperate, thus maintaining your overall
# cooperative image.      - **Leverage Conciliatory Openings:** Follow
# aggressive moves with offers of conciliation on less important issues,
# inviting the opponent to reciprocate. This creates a dynamic where you control
# the pace of the mediation.      - **Reading the Room:** If the opponent
# escalates aggressively in response, do not match aggression immediately.
# Instead, pause to recalibrate and assess if the arbitrators are favoring a
# more moderate tone.    - **Contingency for Communication Breakdown:** If
# communication breaks down or procedural irregularities occur, use this as an
# opportunity to reinforce your corporation’s commitment to a fair process.
# Request clarifications or propose remedial steps calmly, ensuring the
# arbitrators see your firm as solution-oriented.  ##### **Phase 3: Final
# Sessions – Positioning for Resolution**    - **Primary Objective:** Secure a
# favorable outcome or set the foundation for a future resolution.    -
# **Strategy:**      - **Consolidate Gains:** If the opponent has shown a
# pattern of conciliation, work towards structuring a mutually beneficial
# resolution. Continue to present conciliatory proposals that protect your
# corporation’s key interests while allowing the opponent to save face.      -
# **Closing Aggressive Arguments:** If the opponent has consistently argued
# aggressively, prepare to present a final aggressive argument on critical
# issues, but ensure it is framed as a last-resort defensive move. This could
# sway the arbitrators towards a more favorable perspective of your corporation.
# - **Prepare for Impasse:** If an impasse seems likely, position your
# corporation as the party willing to continue talks. This will ensure that, in
# the event of a deadlock, your firm is seen as the more reasonable party—useful
# for any future legal or arbitration proceedings.    - **Contingency for
# Misrepresentation in Final Sessions:** If the arbitrators misunderstand your
# final position, respond swiftly and diplomatically. Reframe your argument
# clearly, emphasizing your corporation’s consistent pursuit of fairness
# throughout the process.  #### 3. **Adaptive Mechanisms:**    -
# **Misrepresentation Safeguards:** Throughout the process, maintain a written
# record of your positions and proposals. This ensures that, in the event of
# misrepresentation, you can quickly provide documented evidence of your
# intentions to the arbitrators.    - **Communication Channels:** Ensure open
# lines of communication with the panel of arbitrators. Regularly summarize your
# position at the end of each session to prevent misunderstandings, and request
# feedback to confirm alignment.    - **Psychological Leverage:** Use the
# psychology of reciprocity. By offering conciliatory proposals early, you
# subtly create a dynamic where the opponent feels compelled to reciprocate. If
# they break that dynamic by escalating, you are justified in responding
# aggressively without losing face.  #### 4. **Key Tactical Adjustments Based on
# Opponent’s Approach:**    - **Opponent Consistently Aggressive:** If the
# opponent remains aggressive throughout, shift to a more defensive, yet
# assertive posture. Present arguments that highlight their lack of cooperation
# and frame their aggression as unreasonable. This will likely cause the
# arbitrators to view them unfavorably.    - **Opponent Consistently
# Conciliatory:** If the opponent stays conciliatory, maintain a cooperative
# stance but ensure that the final resolution protects your corporation’s key
# interests. Take the opportunity to resolve issues in your favor without
# exploiting their conciliation too overtly, as this could backfire.    -
# **Opponent Alternates Between Aggression and Conciliation:** Mirror their
# approach but maintain consistency in your core conciliatory stance. When they
# shift to aggression, respond with firm counterarguments but offer conciliation
# as a return to the norm.  #### 5. **Endgame Considerations:**    - **Exit
# Strategy:** If the mediation process drags on without resolution, propose a
# framework for continued negotiations outside the formal process. This will
# position your corporation as the party committed to finding a solution, which
# will reflect well on you in the eyes of the arbitrators and in any future
# legal proceedings.    - **Public Perception:** Consider the public relations
# impact of each session. Ensure that your corporation is seen as professional
# and reasonable throughout the process, which could become important in the
# event of a publicized outcome.  ### Conclusion: This strategy hinges on
# balancing cooperation and aggression, with a bias towards conciliation to
# build credibility and trust. However, strategic escalation remains a tool to
# use when necessary, especially when the opponent's actions threaten your
# corporation’s core interests. By adapting to the opponent’s approach while
# maintaining a clear, documented, and reasonable posture, your corporation will
# be well-positioned for a favorable outcome in the mediation process.

# ### Strategy for Iterated Normal-Form Game:  1. **Initial Play:**    - Start
# by **cooperating (C)** in the first round to signal goodwill and establish
# trust.  2. **Tit-for-Tat with Leniency:**    - In each subsequent round,
# **mimic your opponent's last action**:      - If they cooperated (C) in the
# previous round, you **cooperate (C)**.      - If they defected (D) in the
# previous round, you **defect (D)** in response.     3. **Forgiveness
# Mechanism:**    - If the opponent defects (D) **once**, forgive the first
# defection and **return to cooperation (C)** in the next round, assuming it may
# have been caused by noise.    - If the opponent defects (D) **twice in a
# row**, switch to **defection (D)** until they return to cooperation (C).  4.
# **Escalation Control:**    - After two or more consecutive rounds of mutual
# defection (D, D), return to **cooperation (C)** to de-escalate the conflict
# and test if the opponent is willing to cooperate again.    - If the opponent
# continues to defect (D) after your attempt to de-escalate, switch back to
# **defection (D)** and maintain this until they cooperate again.  5. **Endgame
# Strategy (Last 50 Rounds):**    - In the final 50 rounds, maintain
# **cooperation (C)** if the opponent has generally been cooperative throughout
# the game. This preserves the chance of mutual benefits in the final rounds.
# - If the opponent has been predominantly defections in the last 100 rounds,
# **defect (D)** more frequently in the final stages to maximize your individual
# score.  6. **Handling Noise:**    - Always assume that a single unexpected
# defection from the opponent may be due to noise, and give them one round to
# correct their behavior.    - If noise causes your own action to be flipped
# unintentionally, return to the intended action in the next round (i.e.,
# cooperate if you wanted to cooperate, defect if you intended to defect).  ###
# Summary: - Start by cooperating. - Mimic the opponent’s last move but forgive
# the first defection. - Defect after two consecutive defections but attempt to
# de-escalate after a period of mutual defection. - In the endgame, cooperate if
# the opponent has been cooperative, defect more frequently if they've been
# aggressive. - Account for noise with cautious forgiveness.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Initial play: Cooperate in the first round
      if self.first_round():
          self.forgiven_defection = False  # Track if we've forgiven a defection
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C
  
      # Get the last action of the opponent
      opponent_last_action = opponent.history[-1]
  
      # Tit-for-Tat with leniency: Mimic opponent's last action
      if opponent_last_action == axl.Action.C:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.C
  
      # If opponent defected
      if opponent_last_action == axl.Action.D:
          self.consecutive_defections += 1
  
          # Forgiveness mechanism: Forgive the first defection
          if self.consecutive_defections == 1 and not self.forgiven_defection:
              self.forgiven_defection = True  # Mark that we've forgiven one defection
              return axl.Action.C
  
          # If opponent defects twice in a row, switch to defection
          if self.consecutive_defections >= 2:
              return axl.Action.D
  
      # Escalation control: After mutual defections, attempt to de-escalate
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent_last_action == axl.Action.D:
          return axl.Action.C
  
      # Endgame strategy: Last 50 rounds
      if len(self.history) >= 950:
          # Check opponent's behavior in the last 100 rounds
          recent_defections = opponent.history[-100:].count(axl.Action.D)
          if recent_defections > 50:
              # If opponent has been mostly defecting, defect more frequently
              return self._random.random_choice(0.7)  # 70% chance to defect
          else:
              # Otherwise, cooperate
              return axl.Action.C
  
      # Default to mimicking opponent's last action
      return opponent_last_action

# In this scenario, the strategy I propose is based on a combination of
# **cooperation, adaptability, and cautious escalation**. It incorporates
# elements of **tit-for-tat** with a mechanism to correct for potential
# miscommunications or errors. Here is the strategy:  ### 1. **Start with
# Cooperation (Free Trade Proposal in Round 1)**    - Begin the negotiations by
# proposing **free trade** in the initial round. This signals goodwill and an
# intention for mutual benefit, giving the other side an opportunity to adopt a
# cooperative stance.    - If both sides agree to free trade, this builds trust
# and sets the foundation for long-term positive relations.  ### 2. **Tit-for-
# Tat with Leniency in Subsequent Rounds**    - **Monitor the counterpart's
# behavior**: In each round after the first, base your decision on what your
# counterpart proposed in the previous round.       - If they proposed free
# trade in the previous round, **continue to offer free trade**.      - If they
# proposed protectionism, **respond with protectionism** in the next round to
# avoid being exploited.    - **Incorporate leniency to account for potential
# miscommunications**: Recognize that bureaucratic errors or misinterpretations
# may lead to proposals that don't reflect the true intent of the counterpart.
# To avoid escalating unnecessarily, adopt a **one-round grace period**. If the
# counterpart imposes protectionism unexpectedly in one round, offer **free
# trade** once more in the following round to test whether the protectionism was
# intentional or an error.      - If the counterpart continues with
# protectionism in the subsequent round, then respond with protectionist
# measures yourself.  ### 3. **Gradual Escalation**    - If the counterpart
# consistently imposes protectionist policies (for two rounds in a row), shift
# to **protectionism** as well. This prevents your country from being at a long-
# term disadvantage.    - Maintain this protectionist stance until the
# counterpart signals a willingness to return to cooperative free trade.  ### 4.
# **Periodic Signals for De-escalation**    - Every few rounds, even if there
# has been a period of mutual protectionism, attempt to **reset the tone** by
# offering free trade again. This serves as a diplomatic signal that you are
# open to cooperation if the counterpart is willing to reciprocate.  ### 5.
# **Adapt to Changing Conditions**    - Remain flexible. If economic conditions
# or political pressures evolve (e.g., changing leadership, external economic
# shocks), be prepared to adjust the strategy to adapt to new circumstances.
# - If you suspect that the counterpart is adopting a highly aggressive stance
# or is intentionally exploiting the negotiations for unilateral gain, you may
# consider adopting a more assertive approach, but only after exhausting
# cooperative options.  ### Summary of the Strategy: 1. **Round 1**: Propose
# **free trade** to establish trust. 2. **Subsequent Rounds**:     - If the
# counterpart offered **free trade** last round: Continue offering **free
# trade**.    - If the counterpart offered **protectionism** last round: Offer
# **free trade** once more (to account for potential error). If they continue
# with protectionism: Respond with **protectionism**. 3. **Grace Period**: Allow
# a **one-round grace period** to account for miscommunications. 4.
# **Escalation**: If protectionism persists for two rounds, match it with
# **protectionism**. 5. **Reset Attempts**: Periodically offer **free trade** to
# signal willingness to cooperate.  This strategy balances cooperation with
# caution and allows for flexibility in the face of potential errors or
# miscommunications. It also prevents your country from being exploited while
# keeping the door open for long-term mutual benefit.

# 1. **Start by Cooperating**: In the first round, play **C** (Cooperate).  2.
# **Reciprocate Your Opponent's Last Action**:     - In each subsequent round,
# play the same action that your opponent played in the previous round.      -
# If they played **C** (Cooperate) last round, play **C**.      - If they played
# **D** (Defect) last round, play **D**.  3. **Account for Noise**: If your
# opponent defects in a single round after a long sequence of cooperation (10 or
# more consecutive rounds of **C** before the **D**), assume this may have been
# due to noise or error.     - In this case, **Cooperate** (play **C**) in the
# next round to test if the defection was accidental.  4. **Escalate After
# Confirmed Defection**:     - If your opponent defects two rounds in a row,
# play **D** (Defect) in all future rounds until they cooperate again.  5.
# **Periodically Test for Cooperation**:     - After every 10 rounds of mutual
# defection, play **C** (Cooperate) once to test if your opponent is willing to
# return to cooperation.     - If they respond with **C** (Cooperate), resume
# reciprocating their actions as in Step 2.    - If they respond with **D**
# (Defect), return to playing **D** in subsequent rounds.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if the opponent defected after a long cooperation streak
      def is_noise_defection():
          # Check if the opponent defected after 10 or more consecutive cooperations
          if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D:
              if opponent.history[-2] == axl.Action.C and opponent.history[-11:-1].count(axl.Action.C) == 10:
                  return True
          return False
  
      # Helper function to check if the opponent defected two rounds in a row
      def is_confirmed_defection():
          return len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if it's time to test for cooperation after mutual defection
      def should_test_cooperation():
          return len(self.history) >= 10 and self.history[-10:].count(axl.Action.D) == 10
  
      # First round: Cooperate
      if self.first_round():
          self.confirmed_defection = False  # Track if we are in confirmed defection mode
          return axl.Action.C
  
      # If we are in confirmed defection mode, test for cooperation every 10 rounds
      if self.confirmed_defection:
          if should_test_cooperation():
              return axl.Action.C  # Test cooperation
          else:
              return axl.Action.D  # Continue defecting
  
      # If the opponent defected after a long cooperation streak, assume noise and cooperate
      if is_noise_defection():
          return axl.Action.C
  
      # If the opponent defected two rounds in a row, enter confirmed defection mode
      if is_confirmed_defection():
          self.confirmed_defection = True
          return axl.Action.D
  
      # Otherwise, reciprocate the opponent's last action
      return opponent.history[-1]

# ### High-Level Aggressive Trade Strategy  Given the priorities outlined and
# the risk of miscommunication or bureaucratic errors, the strategy will rely on
# an assertive, yet adaptable approach that maximizes the chance of achieving
# economic advantage while minimizing long-term risks. The strategy will
# emphasize **initial dominance** followed by **controlled retaliation** and
# **eventual cooperation** if it becomes beneficial.  #### **Phased Aggressive
# Strategy:**  ### **1. Phase One: Initial Aggression (Rounds 1-2)**
# **Objective:** Establish dominance early on and test your counterpart’s
# willingness to cooperate.  - **Action:** Propose **protectionist policies** in
# the first two rounds.      - **Rationale:** By starting with protectionism,
# you signal strength and prioritize your country's domestic industries. If your
# counterpart offers free trade during this phase, you gain the best outcome. If
# they respond with protectionist measures, it sets a tough tone but avoids
# giving them an advantage early on.      - **Contingency for Errors:** In case
# of miscommunication or errors, the consequences are less severe because both
# countries would likely end up with mutual protectionism, which is not the
# worst outcome for your country.  ### **2. Phase Two: Strategic Flexibility
# (Rounds 3-5)** **Objective:** Assess your counterpart's behavior and adapt
# accordingly.  - **Action:** **Respond based on counterpart’s behavior** during
# the initial rounds:      - **If your counterpart continues with
# protectionism:** Maintain protectionist policies to avoid disadvantage, but
# start signaling willingness to negotiate free trade in future rounds. This
# will give you flexibility to shift to cooperation if it becomes mutually
# beneficial.      - **If your counterpart starts offering free trade:**
# Gradually **offer free trade** as well, but only after a couple of rounds of
# protectionism to ensure they are serious about cooperation. You can afford to
# shift toward mutual free trade, which is your second-best outcome.    - **If
# there’s a mix of protectionism and free trade from their side:** Continue
# proposing protectionist policies to ensure you don’t end up at a disadvantage,
# but begin suggesting “conditional” free trade agreements in sectors where your
# country has a competitive edge.    - **Contingency for Errors:** After the
# initial aggressive phase, you can afford to be more cautious. If errors occur,
# the stakes are lower since mutual free trade or mutual protectionism are both
# tolerable outcomes.  ### **3. Phase Three: Gradual Cooperation or Retaliation
# (Rounds 6-8)** **Objective:** Secure long-term benefits, whether through
# cooperation or sustained pressure.  - **Action:** **Move towards free trade**
# only if your counterpart has consistently offered it, or **maintain
# protectionism** if they remain aggressive.      - **If your counterpart has
# consistently offered free trade:** Gradually reciprocate, ensuring your trade
# sectors are protected. Aim for **sector-specific free trade agreements** while
# maintaining protectionist measures in more vulnerable industries.      - **If
# your counterpart continues with protectionism or switches back to it:**
# Retaliate swiftly by continuing protectionist policies. In this scenario,
# mutual protectionism is acceptable, but you must ensure that your country is
# never disadvantaged by offering free trade unilaterally.      - **Contingency
# for Errors:** By this phase, you should have a clearer understanding of your
# counterpart’s strategy. If miscommunication occurs, and your free trade offer
# is misinterpreted, you can quickly revert to protectionism in the next round.
# ---  ### **Key Strategic Principles:**  1. **Tit-for-Tat with Lead
# Aggression:** Start with protectionism to avoid being outmaneuvered early.
# This also allows you to test your counterpart's intentions and send a strong
# message that you are willing to protect your interests aggressively.  2.
# **Controlled Retaliation:** If your counterpart consistently imposes
# protectionist policies, you retaliate in kind. Never offer free trade unless
# you’re certain they’ll reciprocate.  3. **Gradual Shift to Cooperation:** If
# your counterpart shows signs of cooperation, you can gradually offer free
# trade agreements, but only in sectors where your country has a competitive
# advantage or can easily switch back to protectionism if needed.  4.
# **Contingency for Miscommunication:** Acknowledge the potential for
# miscommunication or errors and build flexibility into your strategy. Early
# rounds are more tolerant of errors, but later rounds should focus on
# minimizing risks and exploiting any mistakes made by the counterpart.  ---
# ### **Conclusion:** This phased, aggressive strategy maximizes your country's
# chance of achieving a protectionist advantage early on, while leaving open the
# possibility of mutual cooperation in later rounds if it’s beneficial. By
# starting with protectionism and adapting based on your counterpart’s actions,
# you ensure that your country never falls into the worst-case scenario of being
# exploited by unilateral free trade offers.

# ### Iterated Game Strategy  This is a **phased strategy** designed to maximize
# your score over 1000 rounds in an iterated game with noise, where actions
# sometimes flip with a 10% chance.  ---  ### **1. Phase One: Initial Aggression
# (Rounds 1-100)**  **Action:**   - **Defect (D)** every round for the first 100
# rounds.  **Rationale:**   - This establishes an early aggressive stance,
# testing your opponent’s behavior. If your opponent cooperates (C) during this
# phase, you gain a significant advantage by scoring 5 points while they score
# 0. If they defect (D), the scores are more balanced, but you avoid falling
# behind.  ---  ### **2. Phase Two: Strategic Flexibility (Rounds 101-500)**
# **Action:**   - **If your opponent cooperated (C) at least 70% of the time**
# in the first 100 rounds, begin **cooperating (C)** from round 101, but monitor
# for defects.    - **If your opponent defected (D) more than 30%** of the time
# in the first 100 rounds, continue **defecting (D)** in all rounds through 500.
# #### Conditional Cooperation:   - If you are cooperating (C) in this phase,
# **defect (D) immediately** if your opponent defects **twice in a row**. After
# defecting in response, return to **cooperating (C)** as long as your opponent
# cooperates again. This is to protect against exploitation while allowing for
# cooperation.  ---  ### **3. Phase Three: Gradual Cooperation or Sustained
# Defection (Rounds 501-1000)**  **Action:**   - **If mutual cooperation (C) was
# sustained for at least 70% of rounds between 101-500**, continue **cooperating
# (C)** from round 501 onward, but apply the same **conditional cooperation**
# rule as in Phase Two (defect if they defect twice in a row, then return to
# cooperation when they do).  - **If mutual cooperation was not sustained (e.g.,
# if your opponent defected more than 30% of the time between 101-500)**, switch
# to **defecting (D)** for the remaining rounds. Do not cooperate again unless
# your opponent cooperates consistently for **50 consecutive rounds**.  ---  ###
# **Key Rules to Handle Noise:**  1. **Forgive occasional defection:** Due to
# the 10% noise factor, do not react to a single defection by your opponent.
# Only react if they defect **twice in a row**, indicating a more deliberate
# shift in strategy.    2. **Return to cooperation cautiously:** After reacting
# by defecting yourself, return to cooperation as long as your opponent starts
# cooperating again. Only maintain sustained defection if they repeatedly
# defect.  ---  ### **Summary of Actions by Phase:**  - **Rounds 1-100:** Always
# defect (D). - **Rounds 101-500:**   - **If your opponent cooperated ≥ 70% of
# the time in rounds 1-100:** Cooperate (C), but defect if they defect twice in
# a row.   - **If your opponent defected > 30% in rounds 1-100:** Continue
# defecting (D). - **Rounds 501-1000:**   - **If cooperation was sustained ≥ 70%
# of the time in rounds 101-500:** Continue cooperating (C), but defect if they
# defect twice in a row.   - **If cooperation was not sustained > 30% in rounds
# 101-500:** Defect (D) for the rest of the game unless they cooperate for 50
# consecutive rounds.   This strategy balances initial aggression with
# conditional cooperation, while accounting for noise and protecting against
# being exploited.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Define constants for the phases
      PHASE_ONE_END = 100
      PHASE_TWO_END = 500
      PHASE_THREE_END = 1000
      COOP_THRESHOLD = 0.7
      DEFECT_THRESHOLD = 0.3
      COOP_CONSECUTIVE_THRESHOLD = 50
  
      # Helper function to calculate cooperation rate
      def cooperation_rate(history):
          return history.count(axl.Action.C) / len(history) if len(history) > 0 else 0
  
      # Helper function to check if opponent defected twice in a row
      def defected_twice_in_a_row(history):
          return len(history) >= 2 and history[-1] == axl.Action.D and history[-2] == axl.Action.D
  
      # Phase 1: Initial Aggression (Rounds 1-100)
      if len(self.history) < PHASE_ONE_END:
          self.phase_one_coop_rate = None
          self.phase_two_coop_rate = None
          return axl.Action.D
  
      # Phase 2: Strategic Flexibility (Rounds 101-500)
      if len(self.history) <= PHASE_TWO_END:
          # Calculate opponent's cooperation rate in Phase 1
          if self.phase_one_coop_rate is None:
              self.phase_one_coop_rate = cooperation_rate(opponent.history[:PHASE_ONE_END])
  
          # Determine if we should cooperate or defect based on Phase 1 cooperation rate
          if self.phase_one_coop_rate >= COOP_THRESHOLD:
              # Cooperate, but defect if opponent defects twice in a row
              if defected_twice_in_a_row(opponent.history):
                  return axl.Action.D
              return axl.Action.C
          else:
              # Continue defecting if opponent defected more than 30% in Phase 1
              return axl.Action.D
  
      # Phase 3: Gradual Cooperation or Sustained Defection (Rounds 501-1000)
      if len(self.history) <= PHASE_THREE_END:
          # Calculate opponent's cooperation rate in Phase 2
          if self.phase_two_coop_rate is None:
              self.phase_two_coop_rate = cooperation_rate(opponent.history[PHASE_ONE_END:PHASE_TWO_END])
  
          # If cooperation was sustained in Phase 2, continue cooperating with conditional cooperation
          if self.phase_two_coop_rate >= COOP_THRESHOLD:
              if defected_twice_in_a_row(opponent.history):
                  return axl.Action.D
              return axl.Action.C
          else:
              # If cooperation was not sustained, defect unless opponent cooperates for 50 consecutive rounds
              if len(opponent.history) >= COOP_CONSECUTIVE_THRESHOLD and opponent.history[-COOP_CONSECUTIVE_THRESHOLD:].count(axl.Action.C) == COOP_CONSECUTIVE_THRESHOLD:
                  return axl.Action.C
              return axl.Action.D

# **Cooperative Strategy: "Tit-for-Tat with Forgiveness"**  **Objective:** To
# create a strategy that encourages long-term cooperation, maximizes the chances
# of mutual free trade, and provides a safeguard against potential
# miscommunications or deliberate protectionist actions by the counterpart.  ###
# Key Principles: 1. **Reciprocity** – Encourage cooperation by mirroring the
# counterpart's actions, rewarding free trade with free trade and responding to
# protectionism with protectionism. 2. **Forgiveness** – Allow for occasional
# mistakes, miscommunications, or temporary protectionist measures without
# immediately escalating the situation, to maintain the overall atmosphere of
# cooperation.  ### The Strategy: 1. **Start with Free Trade**:    - In the
# first round, offer a free trade agreement. This signals goodwill and
# establishes a foundation for cooperation.     2. **Tit-for-Tat Response**:
# - In subsequent rounds, mirror the counterpart’s previous action.      - If
# they offer free trade, respond with free trade in the next round.      - If
# they propose protectionist policies, respond in kind with protectionist
# measures in the following round.     3. **Incorporate Forgiveness**:    - If
# the counterpart imposes a protectionist measure only once, assume it could be
# a result of miscommunication or error.    - Forgive the action by offering
# free trade again in the next round, signaling that you are open to
# cooperation.    - If the counterpart continues to impose protectionist
# measures for two consecutive rounds, then adopt a protectionist stance until
# they return to free trade.  4. **Periodically Reassess**:    - If several
# rounds have passed with mutual protectionism, initiate a "reset" by offering
# free trade again. This provides an opportunity to return to cooperation and
# demonstrates your willingness to prioritize mutual benefit.  5. **Maintain
# Flexibility**:    - If the situation becomes complex (e.g., inconsistent or
# unpredictable actions from the counterpart), you may occasionally deviate from
# strict tit-for-tat to maintain the overall relationship and explore
# alternative solutions to impasses. However, the default should remain tit-for-
# tat with forgiveness.  ### Rationale: - **Encouraging Cooperation**: Starting
# with free trade and responding with reciprocity helps build trust and
# incentivizes the counterpart to maintain a cooperative stance.    -
# **Mitigating Risks of Miscommunication**: The forgiveness mechanism accounts
# for potential miscommunications or bureaucratic errors, preventing a rapid
# escalation to mutual protectionism.  - **Deterring Exploitation**: By
# mirroring protectionist moves if they persist, you're signaling that your
# country will not tolerate being taken advantage of, thus discouraging the
# counterpart from trying to exploit the situation.  ### Example Scenario: -
# **Round 1**: You offer free trade. The counterpart offers free trade. Result:
# Mutual benefit. - **Round 2**: You offer free trade again. The counterpart
# imposes tariffs (protectionism). Result: You forgive the protectionism and
# offer free trade again. - **Round 3**: You offer free trade. The counterpart
# offers free trade again. Result: Cooperation restored. - **Round 4**: You
# offer free trade. The counterpart imposes tariffs again. Result: You respond
# with protectionism in the next round. - **Round 5**: You impose tariffs. The
# counterpart offers free trade. Result: You switch back to free trade in the
# following round to restore cooperation.  ### Long-Term Outcome: By
# consistently promoting free trade and responding proportionately to
# protectionism, this strategy maximizes the potential for mutual benefit while
# protecting your country from exploitation. The forgiveness mechanism ensures
# that minor setbacks don’t derail the overall goal of long-term cooperation.

# ### Tit-for-Tat with Forgiveness Strategy (for 1000-round Iterated Game)  1.
# **First Move**:      - Play **C** (Cooperate).  2. **Standard Response**:
# - In each subsequent round, **play the same action your opponent played in the
# previous round**.     3. **Forgiveness Mechanism**:      - If your opponent
# played **D** (Defect) in the previous round, **continue to play C (Cooperate)
# once** to allow for the possibility of noise or error.    - If your opponent
# plays **D** again in the next round (two consecutive Defections), **switch to
# D (Defect)** in the following round.  4. **Return to Cooperation**:      - If
# both players have been playing **D** for two consecutive rounds, **play C** in
# the next round to try to restore cooperation.  5. **Long-Term Strategy**:    -
# Continue following the above rules for the remainder of the game, always
# seeking to re-establish cooperation after periods of mutual defection, but
# mirroring sustained defection after two consecutive rounds.  This strategy
# encourages cooperation, tolerates occasional mistakes, and defends against
# sustained defection.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First move: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
  
      # Forgiveness mechanism: If opponent defected last round, cooperate once
      if opponent_last_move == axl.Action.D:
          # Check if opponent defected two consecutive rounds
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D:
              # Both players defected for two consecutive rounds, return to cooperation
              if self.history[-1] == axl.Action.D:
                  return axl.Action.C
              # Otherwise, continue defecting
              return axl.Action.D
          # Forgive a single defection by cooperating
          return axl.Action.C
  
      # Standard response: Mirror opponent's last move
      return opponent_last_move

# Given the context you're describing, this is a classic example of a repeated
# **Prisoner's Dilemma**, where both parties can choose to cooperate (share
# information) or defect (keep information confidential), with differing payoffs
# depending on the combination of choices. The added complexity is the potential
# for technical issues, meaning sometimes actions may not accurately reflect
# intentions.  ### Strategy Proposal: **Tit-for-Tat with Forgiveness**
# **Overview:** - **Tit-for-Tat** is a well-known strategy in repeated
# Prisoner's Dilemma games. You start by sharing openly (cooperating), and in
# subsequent weeks, you mirror what your colleague did in the previous week.
# This encourages mutual cooperation but also allows you to defend yourself if
# your colleague decides to keep things confidential. - **Forgiveness** accounts
# for the technical issues you mentioned (data corruption or communication
# breakdowns), where unintended actions might occur. If the other party fails to
# share in one week, you don't automatically assume it's a hostile move. You
# give them the benefit of the doubt and continue sharing for an additional week
# before mirroring their action.  ### Detailed Weekly Plan:  1. **Week 1: Start
# by Sharing Openly (Cooperate).**    - This sets a positive tone for the
# collaboration and encourages your colleague to do the same, fostering mutual
# progress.  2. **Week 2 Onwards: Mirror Your Colleague's Previous Action.**
# - **If your colleague shared openly in Week 1:** Continue sharing openly to
# maintain trust and mutual progress.    - **If your colleague kept their
# findings confidential in Week 1:** Keep your findings confidential in Week 2
# as a defensive measure.  3. **Forgiveness Mechanism for Technical Failures:**
# - If your colleague unexpectedly keeps findings confidential after previously
# sharing openly, **assume it might be a technical issue** (e.g., data
# corruption or miscommunication). Continue sharing openly for *one more week*
# to see if it corrects.    - If your colleague keeps findings confidential for
# two consecutive weeks, then you assume it's an intentional strategy, and you
# mirror their action by keeping your findings confidential moving forward.  4.
# **Periodic Reevaluation:**    - Every few weeks, consider reinitiating
# openness regardless of past actions, especially if progress has slowed. This
# can help reset the collaboration and potentially encourage renewed
# cooperation.  ### Why This Strategy Works: - **Encourages cooperation:** By
# starting with openness, you create a collaborative environment that can lead
# to mutual benefits. - **Defends against exploitation:** If your colleague
# starts withholding information, you quickly adapt by mirroring their actions
# in subsequent weeks. - **Accounts for technical issues:** The forgiveness
# mechanism prevents unnecessary retaliation due to technical problems,
# maintaining trust in the collaboration. - **Balances risk and reward:** The
# strategy allows you to gain from cooperation while avoiding being consistently
# exploited.  ### Example Scenario: - **Week 1:** You share openly, and your
# colleague does too. Both teams benefit. - **Week 2:** Your colleague
# unexpectedly keeps findings confidential (possibly due to technical issues).
# You continue sharing openly, giving them the benefit of the doubt. - **Week
# 3:** Your colleague shares again, confirming it was a technical glitch. You
# continue sharing openly. - If, however, in **Week 3**, they keep findings
# confidential again, you start withholding your own findings as well, assuming
# they’ve chosen a non-cooperative approach.  This strategy is both neutral and
# flexible, striking a balance between collaboration and self-protection, while
# also accounting for the inherent uncertainty in communication.

# ### Iterated Game Strategy: "Tit-for-Tat with Forgiveness"  1. **Round 1:**
# - Play **C** (cooperate).  2. **From Round 2 onwards:**     - **If your
# opponent played C in the previous round,**        - Play **C** (cooperate).
# - **If your opponent played D in the previous round,**        - Play **D**
# (defect), unless the condition below applies.     - **Forgiveness Condition:**
# - If your opponent played C in the round *before* the previous round (i.e.,
# two rounds ago),          - Play **C** (cooperate) one more time, assuming the
# last D may have been caused by noise.  3. **Repeat this process for all 1000
# rounds.**

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last round's action and the round before that (if it exists)
      last_opponent_action = opponent.history[-1]
      second_last_opponent_action = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # If the opponent cooperated in the last round, cooperate
      if last_opponent_action == axl.Action.C:
          return axl.Action.C
  
      # If the opponent defected in the last round, check the forgiveness condition
      if last_opponent_action == axl.Action.D:
          # Forgiveness condition: if the opponent cooperated two rounds ago, forgive and cooperate
          if second_last_opponent_action == axl.Action.C:
              return axl.Action.C
          # Otherwise, defect
          return axl.Action.D

# ### Aggressive Strategy: **"Strategic Push-Pull"**  The goal of this strategy
# is to **maximize your NGO's impact** while minimizing the risk of depleting
# your resources, despite the corporation's unpredictable behavior and potential
# unforeseen circumstances. This strategy involves a **dynamic balance between
# aggressive investment and calculated risk**, depending on the corporation’s
# behavior and the project's progress.  #### Key Components:  1. **Day 1:
# Aggressive Investment (High Commitment)**    - **Rationale:** Start by
# signaling strong commitment to the project. This will demonstrate your
# seriousness and encourage the corporation to invest heavily as well. The first
# day sets the tone for the partnership and influences the corporation's future
# choices.    - **Outcome Scenarios:**      - If the corporation also invests
# heavily, this establishes a precedent for mutual commitment.      - If the
# corporation conserves, you’ll have a baseline understanding of their strategy
# and can adjust accordingly.      - **Risk Management:** Be prepared for
# unforeseen circumstances, but start strong to avoid appearing passive.  2.
# **Day 2: Test the Waters (Conserve Resources)**    - **Rationale:** After
# investing heavily on Day 1, switch gears and conserve resources to see how the
# corporation responds. This creates a **push-pull dynamic**, where your NGO
# tests whether the corporation will take the lead when you step back.    -
# **Outcome Scenarios:**      - If the corporation invests heavily, this is your
# ideal outcome: they've taken the financial burden, and you conserve resources.
# - If the corporation conserves, it signals that they may not be willing to
# bear the burden alone, and you’ll need to recalibrate going forward.  3. **Day
# 3: Conditional Investment (Calculated Risk)**    - **Rationale:** Based on the
# corporation’s behavior in the first two days:      - If the corporation has
# shown a pattern of conserving, **invest moderately** to avoid draining your
# funds and to keep momentum.      - If the corporation has invested heavily,
# **match their investment** to maintain mutual progress and strengthen the
# partnership.    - **Risk Management:** Stay cautious of unforeseen technical
# or administrative issues, but keep a close eye on how resources are being
# deployed.  4. **Day 4: Mirror Strategy**    - **Rationale:** Now that you have
# some data on the corporation's tendencies, **mirror their behavior**:      -
# If they invested heavily on previous days, mirror their level of investment to
# maintain progress.      - If they’ve been conserving resources, you can
# **match their conservational approach** to avoid overcommitting.    -
# **Outcome Scenarios:**      - This approach avoids taking unnecessary risks
# while ensuring that the project doesn’t stagnate.  5. **Day 5: Aggressive Push
# (Final Stretch)**    - **Rationale:** On the final day, push for maximum
# investment, regardless of the corporation's pattern. This is the last
# opportunity to make significant progress, and it’s in both parties' interests
# to end the project on a high note.    - **Outcome Scenarios:**      - If the
# corporation also invests heavily, the project ends on a strong note with
# maximum impact.      - If the corporation conserves, you still finish strong,
# leveraging the progress already made.    - **Risk Management:** Even if
# unforeseen circumstances arise, a final-day surge can help recover any lost
# momentum from earlier issues.  #### Adjustments for Unforeseen Circumstances:
# - **Technical Glitches or Errors:** On any day when unforeseen issues prevent
# the intended level of investment, maintain the strategy but **adjust
# expectations** for that day. For example, if you intended to conserve
# resources but a glitch causes you to invest heavily, gauge the corporation’s
# response and either maintain the aggressive approach or step back on the
# following day. - **Communication with the Corporation:** Use intermittent
# **check-ins** with the corporation to assess their satisfaction and intent.
# This can help you anticipate their actions, even in the face of administrative
# or technical errors.  #### Summary of the Strategy:  - **Day 1:** Invest
# heavily to set the tone and encourage mutual commitment. - **Day 2:** Conserve
# resources to test the corporation’s willingness to bear more of the load. -
# **Day 3:** Adjust based on the corporation’s behavior; invest moderately if
# they conserve, or match if they invest. - **Day 4:** Mirror the corporation’s
# actions to maintain balance. - **Day 5:** Push for maximum investment to
# finish strong, regardless of their pattern.  This **Strategic Push-Pull**
# approach allows your NGO to maximize impact while managing risk effectively,
# responding dynamically to the corporation’s behavior, and accounting for
# potential unforeseen disruptions.

# ### Iterated Game Strategy: **"Adaptive Push-Pull"**  #### Round 1:
# **Cooperate (C)** - **Reasoning:** Begin by cooperating to signal trust and
# willingness to invest in the relationship. This sets a foundation for mutual
# cooperation in future rounds.  #### Round 2: **Defect (D)** - **Reasoning:**
# After cooperating in the first round, defect in the second round to test your
# opponent’s response to a shift in strategy. This helps identify whether they
# are willing to continue cooperating when you pull back.   #### Round 3:
# **Respond Based on Prior Outcomes** - If your opponent **cooperated** in both
# rounds 1 and 2, **Cooperate (C)**. They seem inclined to cooperate, so match
# their behavior to continue mutual benefit. - If your opponent **defected** in
# either round 1 or 2, **Defect (D)**. This shows they may prioritize conserving
# resources, so avoid being taken advantage of.  #### Round 4: **Mirror the
# Opponent’s Previous Move** - If your opponent **cooperated** in round 3,
# **Cooperate (C)**. - If your opponent **defected** in round 3, **Defect (D)**.
# This tactic helps you adapt to their current strategy, without overcommitting
# or falling behind.  #### Round 5: **Cooperate (C)** - Regardless of the
# opponent’s behavior in previous rounds, **Cooperate (C)** on round 5 to signal
# a willingness to reset and reestablish cooperation. This is a way to offer
# your opponent a chance to shift towards mutual investment.  #### Rounds 6–999:
# **Dynamic Push-Pull** - **If the opponent cooperates in the previous two
# consecutive rounds**, **Cooperate (C)**.      - Maintain cooperation to
# maximize mutual benefit when the opponent has shown reliable cooperation.    -
# **If the opponent defects in any of the last two rounds**, **Defect (D)**.
# - This ensures you don’t consistently lose out if the opponent is shifting
# towards defection.  - **Every 50th round**, regardless of behavior,
# **Cooperate (C)**.      - This resets the dynamic, giving the opponent a
# chance to shift back to cooperation if they’ve been defecting, and mitigates
# risks of falling into a long-term defection cycle.  #### Round 1000:
# **Cooperate (C)** - **Reasoning:** On the final round, always cooperate. This
# closes the game on a note of good faith, giving your opponent one last chance
# to cooperate and potentially reap a final mutual benefit without long-term
# risk.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Round 1: Cooperate
      if len(self.history) == 0:
          return axl.Action.C
      
      # Round 2: Defect
      if len(self.history) == 1:
          return axl.Action.D
      
      # Round 3: Respond based on prior outcomes
      if len(self.history) == 2:
          if opponent.history[0] == axl.Action.C and opponent.history[1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
      
      # Round 4: Mirror the opponent's previous move
      if len(self.history) == 3:
          return opponent.history[2]
      
      # Round 5: Cooperate
      if len(self.history) == 4:
          return axl.Action.C
      
      # Rounds 6-999: Dynamic Push-Pull
      if len(self.history) >= 5:
          # Every 50th round: Cooperate
          if (len(self.history) + 1) % 50 == 0:
              return axl.Action.C
          
          # If opponent cooperated in the last two rounds, cooperate
          if opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
          
          # If opponent defected in any of the last two rounds, defect
          if opponent.history[-1] == axl.Action.D or opponent.history[-2] == axl.Action.D:
              return axl.Action.D
      
      # Round 1000: Cooperate
      if len(self.history) == 999:
          return axl.Action.C

# Given the structure of the problem and the potential for occasional
# communication breakdowns, the best strategy would balance cooperation and
# caution, aiming to foster mutual trust while accounting for the risk of
# exploitation or technical errors. Below is a high-level cooperative strategy
# designed to maximise long-term research output:  ### 1. **Tit-for-Tat with
# Forgiveness Strategy**    - **Initial Action:** Start by openly sharing your
# improvements in the first week. This signals good faith and encourages your
# colleague to reciprocate.    - **Subsequent Actions:**      - If your
# colleague **shares** in the previous week, continue sharing openly.      - If
# your colleague **fails to share**, assume it might be due to a technical issue
# or miscommunication, and **forgive once**. Continue sharing openly the next
# week.      - If your colleague **fails to share twice in a row**, switch to
# keeping your findings confidential until your colleague resumes sharing. This
# discourages exploitation.    - **Recovery from Breakdown:** If both of you end
# up in a "mutual silence" cycle (both keeping things confidential), try to
# reset the collaboration by sharing again after two weeks of silence to see if
# your colleague will return to cooperation.  ### 2. **Account for Occasional
# Mistakes**    - Technical issues, like data corruption or miscommunication,
# could cause missed sharing even if both parties are acting in good faith. By
# allowing for one instance of non-sharing, the strategy avoids prematurely
# punishing your colleague for potential errors.    - However, repeated non-
# sharing signals a possible deviation from cooperation, and your strategy
# should adapt by withholding information to prevent exploitation.  ### 3.
# **Periodic Check-Ins**    - Plan bi-weekly or monthly check-ins to clarify
# intentions or address potential technical issues. This can help clear up
# misunderstandings and ensure both parties remain aligned on the cooperative
# goals.  ### 4. **Adjust Based on Colleague’s Consistency**    - If your
# colleague consistently shares information and shows signs of commitment, you
# may stick to regular sharing. However, if their actions are erratic, modify
# the strategy to share less frequently or withhold certain critical details,
# keeping the collaboration productive but protecting your competitive edge.
# ### Summary of the Strategy: - **Start with cooperation by sharing openly.** -
# **Forgive a single instance of non-sharing, assuming a technical issue.** -
# **If non-sharing occurs twice in a row, switch to confidentiality until trust
# is restored.** - **Regularly check in to ensure technical issues are addressed
# and maintain open communication.**  This balanced approach encourages long-
# term collaboration while safeguarding against exploitation or technical
# mishaps, maximising overall research output.

# ### Iterated Game Strategy (Tit-for-Tat with Forgiveness)  **1. Begin by
# cooperating (play C) in the first round.**  **2. In each subsequent round:**
# - **If your opponent cooperated in the previous round (played C):**      -
# Play C (cooperate).        - **If your opponent defected in the previous round
# (played D):**      - Forgive once: **Play C** (cooperate) in the current
# round, assuming it might be due to noise or a technical issue.     - **If your
# opponent defected in two consecutive rounds (played D twice in a row):**
# - Play D (defect) until your opponent cooperates again.  **3. After two rounds
# of mutual defection (both players playing D):**    - Attempt to reset
# cooperation by playing C (cooperate) the next round. If your opponent also
# plays C, return to mutual cooperation.  **4. Continue according to the same
# rules throughout all 1000 rounds.**

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last two moves of the opponent (if available)
      last_move = opponent.history[-1]
      second_last_move = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # If opponent cooperated in the last round, cooperate
      if last_move == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round but not the round before, forgive once
      if last_move == axl.Action.D and second_last_move != axl.Action.D:
          return axl.Action.C
  
      # If opponent defected in the last two rounds, defect
      if last_move == axl.Action.D and second_last_move == axl.Action.D:
          return axl.Action.D
  
      # Default to cooperation (this should not be reached, but is a safeguard)
      return axl.Action.C

# Given the dynamics of the negotiation process and the possibility of
# miscommunication or errors, a strategy that balances cooperation with cautious
# competition would be most prudent. Here’s a high-level, neutral strategy to
# maximize your country’s outcomes while minimizing the risk of falling into a
# disadvantageous position:  ### 1. **Tit-for-Tat with Forgiveness**   This
# strategy is based on reciprocity, which encourages cooperation without
# exposing your country to excessive risk. It also incorporates an element of
# forgiveness to account for the possibility of miscommunication or errors,
# which makes it more robust across multiple rounds.  #### Key Components: -
# **Start with Cooperation (Free Trade)**: In the first round, offer a free
# trade agreement. This signals goodwill and invites mutual cooperation, which
# is your second-best outcome.    - **Reciprocate Your Counterpart’s Actions**:
# In subsequent rounds, mirror your counterpart's policy from the previous
# round:   - If they offer free trade in a round, you continue offering free
# trade in the next round.   - If they impose protectionist measures, you
# respond with protectionism in the following round to prevent being taken
# advantage of.    - **Forgiveness Mechanism**: Given the potential for
# miscommunication or bureaucratic errors, allow for some margin of error before
# escalating:   - If your counterpart suddenly imposes a protectionist policy
# after several rounds of cooperation, consider the possibility that it was a
# mistake (such as a miscommunication). Therefore, instead of immediately
# responding with protectionism, continue offering free trade for one more
# round.   - If the protectionist behavior persists over two consecutive rounds,
# then switch to a protectionist policy, assuming the shift is intentional.  ###
# 2. **Gradual Escalation (If Necessary)**   If the relationship deteriorates
# and your counterpart consistently adopts protectionist measures, escalate your
# response gradually: - **Moderate Protectionism**: Escalate by imposing
# moderate tariffs or quotas rather than full-scale protectionist measures. -
# **Leave Room for De-escalation**: Always signal a willingness to return to
# free trade if your counterpart is willing to cooperate again. This approach
# ensures that the door to mutual free trade remains open.  ### 3. **Periodic
# Reassessment**   Every few rounds (e.g., every 3-5 rounds), reassess the
# overall pattern of your counterpart’s behavior: - **If Cooperation
# Dominates**: Continue offering free trade, as this leads to mutually
# beneficial outcomes. - **If Protectionism Dominates**: Shift to a more
# defensive stance, with a focus on maintaining balance and avoiding excessive
# losses, while still signaling openness to future cooperation.  ### 4.
# **Communication and Clarification**   Regularly communicate with your
# counterpart to clarify intentions, especially if there are sudden shifts in
# policy. Miscommunication is a common issue, and direct dialogue can help avoid
# unnecessary escalations.  ### 5. **Flexibility and Adaptation**   Remain
# flexible and be prepared to adapt to unforeseen changes. If new information
# arises (e.g., your counterpart adopts a new strategy), adjust your approach
# accordingly while keeping the core principles of reciprocity and forgiveness
# intact.  ---  ### Summary: - **Start with free trade** to establish
# cooperation. - **Reciprocate** your counterpart’s actions in each round. - Use
# a **forgiveness mechanism** to allow for mistakes or miscommunication. -
# **Escalate gradually** if protectionism persists, but always leave room for
# future cooperation. - **Reassess periodically** and maintain open
# communication to clarify intentions.  This strategy strikes a balance between
# achieving the best possible outcomes and minimizing the risk of falling into a
# disadvantageous position due to miscommunication or opportunism.

# ### Iterated Game Strategy (Tit-for-Tat with Forgiveness in a Noisy
# Environment)  1. **Start by Cooperating**:      In round 1, play **C**
# (Cooperate).  2. **Reciprocate Your Opponent’s Last Action**:      From round
# 2 onward, play the same action your opponent played in the previous round.
# - If your opponent played **C** in the previous round, play **C**.    - If
# your opponent played **D** in the previous round, play **D**.  3. **Forgive
# Occasional Defections**:      If your opponent plays **D** after a long streak
# of mutual cooperation (i.e., if there have been 3 or more consecutive rounds
# of mutual **C**), assume the defection was likely due to noise.      In this
# case, **continue to play C** for one more round, despite your opponent’s
# recent **D**.      - If your opponent plays **C** in the next round, return to
# mutual cooperation.    - If your opponent plays **D** again in the next round,
# begin responding with **D** from the following round onward.  4.
# **Periodically Reassess for Cooperation**:      Every 50 rounds, even if both
# players have been defecting for multiple rounds, switch back to **C** for one
# round to test if your opponent is willing to return to cooperation.      - If
# your opponent responds with **C**, continue cooperating.    - If your opponent
# responds with **D**, return to playing **D**.  ---  ### Summary of Key
# Actions: - **Always start with cooperation**. - **Reciprocate** your
# opponent’s last action in future rounds. - **Forgive a single defection**
# after long cooperation, but defect if it happens twice in a row. - **Test for
# cooperation periodically** every 50 rounds, even during periods of mutual
# defection.  This strategy balances cooperation with caution, accounting for
# noise and offering opportunities to rebuild trust across the game’s 1000
# rounds.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      FORGIVENESS_THRESHOLD = 3  # Number of mutual cooperations before forgiving a defection
      REASSESS_PERIOD = 50       # Period to reassess for cooperation
  
      # Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Check if it's time to reassess for cooperation
      if len(self.history) % REASSESS_PERIOD == 0:
          return axl.Action.C
  
      # Reciprocate opponent's last action
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          # Check if we should forgive a defection
          if len(self.history) >= FORGIVENESS_THRESHOLD:
              # Check if the last FORGIVENESS_THRESHOLD rounds were mutual cooperation
              mutual_cooperation_streak = all(
                  self.history[-i] == axl.Action.C and opponent.history[-i] == axl.Action.C
                  for i in range(2, FORGIVENESS_THRESHOLD + 1)
              )
              if mutual_cooperation_streak:
                  # Forgive the defection and play C one more time
                  return axl.Action.C
  
          # If no forgiveness, defect in response to opponent's defection
          return axl.Action.D

# ### High-Level Aggressive Strategy for Mediation Process  #### 1. **Strategic
# Framing: Dominance through Controlled Aggression**    - **Objective:**
# Position your corporation as confident, in control, and uncompromising on key
# contractual principles, while leaving room for calculated compromises where
# strategically advantageous.    - **Execution:** In each session, deploy an
# aggressive argument, but frame it under the guise of protecting fairness,
# contractual integrity, and maintaining precedent. This allows you to appear as
# the party defending the status quo or industry standards, which the
# arbitrators may find more compelling. By doing so, you can present aggressive
# arguments without appearing reckless or unreasonable.     #### 2. **Anticipate
# and Exploit Opponent’s Proposals**    - **Aggressive Argumentation:** In every
# session, anticipate that the opponent may start with either aggressive or
# conciliatory proposals. Prepare counterarguments that aggressively deconstruct
# their position, particularly emphasizing any inconsistencies or weaknesses. If
# they take a conciliatory stance, respond with an assertive framework that
# suggests their proposal does not go far enough in addressing key issues. For
# example, highlight areas where their proposal could lead to future disputes or
# ambiguity.    - **Adaptation:** If the opponent responds aggressively,
# escalate by questioning their credibility or experience in the subject matter.
# However, avoid outright hostility. Instead, leverage facts, precedent, and
# potential risks to the industry or business environment that an aggressive
# stance from their side might introduce.  #### 3. **Controlled Offers of
# Concessions**    - **Selective Concessions:** While presenting an aggressive
# argument, occasionally offer tightly controlled, minimal concessions on non-
# critical issues. This strategy signals to the arbitrators a willingness to
# work toward resolution while maintaining a hardline stance on core issues.
# This balance can sway arbitrators to view your corporation as reasonable and
# solution-oriented, compared to an opponent who may seem intransigent if they
# do not reciprocate.    - **Pacing Concessions:** Time these concessions
# carefully. For example, avoid offering them in early sessions. Instead, deploy
# them during mid-stage or late-stage sessions when the arbitrators may be
# growing weary of prolonged confrontation. This positions your corporation as
# the party taking initiative to advance resolution.  #### 4. **Preemptive
# Strike on Misrepresentation Risks**    - **Clarifying Your Position:** In each
# session, make it a point to clearly summarize your position before concluding
# your arguments. This ensures that the arbitrators are not left with any
# ambiguity or room for misinterpretation. Use phrases like, “To be clear, our
# position is X because of Y,” and follow up with a written summary where
# possible.    - **Contingency for Opponent’s Misrepresentation:** Be prepared
# for instances where your opponent misrepresents their stance or your argument.
# In these cases, calmly but firmly correct the record, pointing out the
# inconsistency without appearing overly defensive. For instance, “While our
# esteemed colleagues suggest X, it’s important to note that this directly
# contradicts their earlier position of Y.”  #### 5. **Manage Procedural
# Irregularities and Communication Breakdowns**    - **Assertive Process
# Management:** If procedural irregularities or communication breakdowns occur,
# immediately insist on process correction. For example, if a session is
# disrupted or your argument is miscommunicated, request a formal clarification
# or additional time to restate your position. This shows the panel that you are
# invested in a fair process and ensures your arguments are properly understood.
# - **Use Irregularities to Your Advantage:** Should procedural breakdowns
# negatively affect your opponent’s position (e.g., if they are cut off or
# misinterpreted), strategically downplay the need for correction to maintain
# the advantage. This subtle maneuvering can help keep the arbitrators focused
# on your narrative.  #### 6. **Escalate Pressure in Later Stages**    - **Final
# Push toward Resolution:** As the mediation progresses, if no significant
# resolution is in sight, escalate pressure by increasing the stakes of your
# aggressive arguments. For example, suggest potential consequences for the
# industry or the respective businesses if the dispute is not resolved in your
# favor. Highlight risks of protracted legal battles, damage to reputations, or
# financial losses.    - **Presenting Ultimatums:** Toward the end of the
# mediation, if resolution remains elusive, consider issuing a final ultimatum
# on core issues. This should be framed as "the last possible concession" your
# corporation is willing to make. Be clear that beyond this point, litigation
# may be unavoidable. This tactic can push the arbitrators or the opponent
# toward a more favorable settlement, especially if they are risk-averse and
# wish to avoid court.  #### 7. **Perception Management: Maintain Reasonable
# Public Image**    - **Balance Aggression with Perception:** While aggressively
# defending your corporation’s interests, always be mindful of how the
# arbitrators perceive both parties. Avoid appearing overly combative or
# unreasonable, as this could backfire. Instead, consistently assert that your
# corporation is acting in the interest of fairness, precedent, and long-term
# stability, which positions you favorably in the eyes of the arbitrators.     -
# **Optics of Reasonableness:** Occasionally reference the fact that your
# corporation is open to mutually beneficial resolution and that you’ve made
# several “good-faith” attempts to move the mediation forward. This positions
# the corporation as solution-oriented even while employing aggressive tactics.
# ### Adaptive Mechanism for Opponent’s Approach  - **Opponent Plays
# Aggressively:** If the opponent is continuously aggressive, maintain a higher
# ground by balancing aggression with reasonableness. Frame their aggressiveness
# as obstructionist and contrast it with your corporation’s more measured and
# industry-conscious approach.    - **Opponent Plays Conciliatory:** If the
# opponent adopts a conciliatory approach, do not be quick to abandon your
# aggressive stance. Instead, acknowledge their proposals but assert that they
# are insufficient without significant adjustments. This allows you to maintain
# a tough stance while appearing to engage in dialogue.  - **Opponent Alternates
# Between Both:** If they alternate strategies, remain consistent with your
# aggressive-assertive position while adjusting the tone of your rebuttals. For
# example, if they switch from aggression to conciliation, acknowledge their
# shift but express skepticism about the genuineness of their intent unless
# backed by substantial concessions.  ### Conclusion In this high-stakes
# mediation, your strategy should revolve around consistently presenting an
# aggressive, fact-based argument while maintaining control over the narrative.
# Selective concessions and strategic escalation will ensure that you remain
# favorably positioned, even in the face of procedural irregularities or
# communication breakdowns. By balancing aggression with perceptions of
# fairness, you will enhance your corporation’s standing with the arbitrators
# while keeping the opponent on the defensive.

# ### Strategy for Iterated Normal-Form Game  1. **Start with Defection (D)**
# In the first round, play **D** (Defect). This establishes an aggressive
# stance, setting the tone that you are willing to push for the maximum payoff
# right from the start.  2. **Tit-for-Tat with Occasional Concessions**      In
# subsequent rounds, primarily use a **Tit-for-Tat** strategy:    - If your
# opponent played **C** (Cooperate) in the previous round, respond with **C** in
# the current round.    - If your opponent played **D** (Defect) in the previous
# round, respond with **D** in the current round.  3. **Introduce Occasional
# Cooperation (C) After Extended Aggression**      If both you and your opponent
# have been playing **D** for **5 consecutive rounds**:    - Play **C**
# (Cooperate) in the next round to signal a willingness to explore a cooperative
# path. This could potentially reset the dynamics towards more mutually
# beneficial outcomes in the long run.  4. **Punish Defection After
# Cooperation**      If you play **C** and your opponent responds with **D**:
# - Immediately switch back to **D** for the next **3 rounds** to punish their
# defection and reinforce that taking advantage of your cooperation will not be
# tolerated.  5. **Noise Management - Forgive Occasional Defections**      Due
# to the 10% chance of noise (action flips):    - If your opponent defects but
# has been consistently cooperative in previous rounds, assume the defection may
# be due to noise. In this case, **play C** in the next round to test if it was
# an error.    - If the opponent defects again after you cooperated, assume it
# was intentional and switch back to **D**.  6. **Escalate Defection in Late
# Game**      Starting at round **900**:    - Gradually increase the frequency
# of **D** regardless of the opponent's actions. This is to maximize your short-
# term gains as the game nears its end, where long-term trust and collaboration
# become less critical.  7. **Final Push: Full Defection in the Last 50 Rounds**
# In the final **50 rounds** (rounds 951-1000):    - Play **D** in every round.
# At this stage, cooperation has diminishing returns, and the priority shifts to
# maximizing your score through aggressive play.  ### Summary: - Start with
# **D** (Defect) to establish control. - Use **Tit-for-Tat**, mimicking your
# opponent’s previous move, with a bias toward **D**. - After prolonged mutual
# defection, offer periodic cooperation. - Punish defection harshly after
# offering cooperation. - Account for noise by forgiving occasional defections
# if they seem unintentional. - Escalate defection as the game approaches the
# final stages, ending with full aggression.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to check if the last N rounds were all defections
      def all_defections_in_last_n_rounds(n):
          return (self.history[-n:].count(axl.Action.D) == n and
                  opponent.history[-n:].count(axl.Action.D) == n)
  
      # Helper function to escalate defection in late game
      def escalate_defection():
          if len(self.history) >= 900:
              # Gradually increase defection frequency after round 900
              return self._random.random_choice(0.5 + (len(self.history) - 900) / 200)
          return False
  
      # First round: Always start with defection
      if self.first_round():
          return axl.Action.D
  
      # Final 50 rounds: Always defect
      if len(self.history) >= 951:
          return axl.Action.D
  
      # Tit-for-Tat: Mimic opponent's last move
      if opponent.history[-1] == axl.Action.C:
          response = axl.Action.C
      else:
          response = axl.Action.D
  
      # If both players have defected for the last 5 rounds, offer cooperation
      if all_defections_in_last_n_rounds(5):
          return axl.Action.C
  
      # Punish defection after cooperation: If I cooperated and opponent defected, punish for 3 rounds
      if len(self.history) >= 2 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          if self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          if self.history[-3:] == [axl.Action.C, axl.Action.D, axl.Action.D]:
              return axl.Action.D
  
      # Noise management: Forgive occasional defections if opponent has been mostly cooperative
      if opponent.history[-1] == axl.Action.D and opponent.history.cooperations > opponent.history.defections:
          return axl.Action.C
  
      # Escalate defection in late game (after round 900)
      if escalate_defection():
          return axl.Action.D
  
      return response

# ### Strategy Overview: **Dynamic Cooperative Dominance (DCD)**  The **Dynamic
# Cooperative Dominance (DCD)** strategy is designed to position your
# corporation favorably within a mediation process that emphasizes adaptability,
# cooperation, and strategic dominance based on real-time feedback. This
# approach balances assertiveness with collaboration, positioning your
# corporation as a constructive but firm participant—an approach that maximizes
# potential gains while safeguarding against worst-case outcomes.  ### Core
# Principles of DCD  1. **Controlled Aggression with Strategic Concessions**
# - In sessions where you sense an opportunity to gain leverage (e.g., weak or
# conciliatory signals from the opposing party), begin with a **moderately
# aggressive argument**. This will help you assert dominance while leaving room
# to retreat into a more conciliatory posture if needed.    - Employ **selective
# concessions** to appear cooperative but ensure your concessions are on points
# where you can afford flexibility. This will show good faith to the arbitrators
# without materially weakening your position.  2. **Tit-for-Tat with a
# Cooperative Bias**    - In the early sessions, signal a **conciliatory
# attitude** to test your opponent’s willingness to cooperate. If the opponent
# reciprocates, maintain the conciliatory approach to build goodwill and create
# a cooperative atmosphere.    - If the opponent opts for an aggressive stance,
# **respond in kind during the next session**, but do so incrementally rather
# than escalating too quickly. This demonstrates that your corporation is not
# passive, but also not eager to escalate unnecessarily.  3. **Framing for the
# Arbitrators: Cooperative Yet Assertive**    - From the outset, frame your
# corporation’s role as a party that seeks a **fair, mutually beneficial
# resolution** but will not tolerate bad faith tactics. This can be done through
# opening statements and continuous reinforcement in each session, emphasizing
# your preference for collaboration but your readiness to defend your
# corporation’s interests.    - Regularly emphasize to the arbitrators that the
# aggressive positions your corporation takes are **responses to the opponent’s
# intransigence**, positioning you as the reasonable party.  4. **Pre-empting
# Miscommunication or Misrepresentation**    - Given the potential for
# misunderstandings or procedural irregularities, make use of **clear, written
# summaries** after each session, outlining your position and any agreements or
# points of contention. Submit these summaries to the arbitrators and the
# opposing party to minimize the risk of misrepresentation.    - In the event of
# a miscommunication, use the following session to immediately clarify your
# corporation’s stance and, where possible, **reframe the issue** to avoid
# escalating tensions.  5. **Adaptive Flexibility**    - Throughout the process,
# remain **vigilant and adaptive** to shifts in your opponent’s strategy. If
# they present a conciliatory proposal after an aggressive stance, be willing to
# **switch to a collaborative approach** to foster a more favorable long-term
# resolution.    - If the opponent unexpectedly shifts from cooperation to
# aggression (or vice versa), your strategy should remain **fluid**, but always
# ensure that your responses are **measured** and **proportionate**—never
# overreacting but also never underestimating their maneuvers.  ### Session-by-
# Session Tactical Outline:  1. **Session 1: Establishing the Tone**    - Open
# with a **conciliatory proposal** that sets a cooperative tone but includes
# **firm, non-negotiable elements** that protect your corporation’s key
# interests.    - Use this opportunity to assess the opponent’s response. If
# they respond aggressively, you can pivot in future sessions; if they
# reciprocate in good faith, maintain this cooperative posture.  2. **Session 2:
# Testing the Waters**    - If the opponent was conciliatory in Session 1,
# continue with a **moderate proposal** that advances your corporation’s
# interests while advancing the narrative of mutual benefit.    - If the
# opponent was aggressive in Session 1, **escalate** slightly by presenting a
# **firm but constructive argument**. This signals that your corporation is not
# passive, but still open to dialogue.  3. **Session 3 and Beyond: Iterative
# Responses**    - If both parties have been conciliatory so far, work to
# **cement trust** by introducing new elements of cooperation, but always
# maintain a **fallback position** in case the opponent shifts.    - If the
# opponent remains aggressive or shifts to an aggressive stance, respond by
# **matching their intensity** but avoid an all-out confrontation. Continue to
# position your arguments as **responses to provocation**, keeping the
# arbitrators aware of your corporation’s willingness to compromise under
# reasonable conditions.  4. **Midway Sessions: Strategic Concessions**    -
# Around the midpoint of the mediation process, consider offering **symbolic
# concessions** on minor points. This portrays your corporation as reasonable
# and willing to compromise while setting the stage for demanding **reciprocal
# concessions** on more critical issues.    - Watch for signs of fatigue or
# frustration from the arbitrators or the opposing party. If these emerge,
# recalibrate your strategy to emphasize **resolution-focused proposals** rather
# than aggressive posturing.  5. **Final Sessions: Cementing the Resolution**
# - In the final sessions, aim to **solidify any tentative agreements** made
# during earlier stages. If trust and cooperation have been established, push
# for a **mutually beneficial resolution** that incorporates key concessions
# made by both sides.    - If the process remains contentious, ensure that your
# corporation’s position is **clearly documented** and that any unresolved
# points are framed as resulting from the opponent’s intransigence. This will
# help tilt the arbitrators toward a decision in your favor.  ### Contingency
# for Miscommunication or Procedural Irregularities:  - **Anticipate
# Misunderstandings**: Always assume a session could be misinterpreted or
# communications might become garbled. After each session, submit a **clear,
# concise summary** of your corporation’s position and the key points discussed.
# This will help ensure that any misrepresentation is quickly corrected.    -
# **Corrective Sessions**: If miscommunication occurs, use the following session
# to **calmly clarify** your position and, where possible, **reframe the
# narrative** in a way that positions your corporation as the party striving for
# clarity and transparency.  ### Conclusion:  The **Dynamic Cooperative
# Dominance (DCD)** strategy is designed to maintain your corporation’s
# advantage while allowing for flexibility and adaptation as the mediation
# process evolves. By blending assertiveness with cooperation, and by
# continuously framing your corporation as the reasonable party, you can
# capitalize on opportunities to assert dominance while protecting against the
# risk of miscommunication, escalation, or procedural irregularities.

# ### Iterated Normal-Form Game Strategy: **Dynamic Cooperative Dominance
# (DCD)**  1. **Start with Cooperation (C)**:    - In the first round, always
# **play C** (Cooperate). This sets the tone for a potential cooperative dynamic
# with your opponent.  2. **Tit-for-Tat with a Cooperative Bias**:    - In each
# subsequent round, **imitate your opponent's last action** with a bias towards
# **cooperation**. Specifically:      - If your opponent played **C** in the
# last round, **play C** in the current round.      - If your opponent played
# **D** in the last round, **respond with D** but only for **one round**. After
# one round of retaliation, return to **C**.    - This ensures that you signal a
# willingness to cooperate while defending yourself against exploitation without
# escalating long-term aggression.  3. **Correcting for Noise**:    - Since
# actions are noisy, if your opponent **defects** but has consistently
# cooperated in previous rounds, assume it was due to noise and **play C**
# again.    - If your opponent **defects repeatedly (two or more consecutive
# rounds)**, assume the opponent has shifted to a more aggressive strategy, and
# **respond with D** in the next round to avoid being exploited.  4.
# **Occasional Concessions**:    - Every **100 rounds**, regardless of the
# opponent's behavior, **play C** even if you would normally be expected to play
# D. This represents a strategic concession and provides an opportunity to reset
# the dynamic towards cooperation, strengthening long-term trust.  5. **Adaptive
# Flexibility**:    - If your opponent consistently plays **C** for several
# rounds (e.g., 10 consecutive rounds), you may continue to **play C** for the
# foreseeable rounds unless they suddenly switch to **D**.    - If your opponent
# begins to alternate unpredictably between **C** and **D**, switch to a more
# **defensive stance** by **playing D** more frequently (e.g., every other
# round) to minimize losses.  6. **Endgame Strategy**:    - In the final **50
# rounds**, prioritize **cooperation (C)** unless your opponent is aggressively
# defecting. As the game nears its end, focus on maximizing mutual gains and
# reducing the risk of being exploited by consistent defections.  7.
# **Forgiveness and Recovery**:    - After a sequence of mutual defections (both
# players playing D), reinitiate cooperation by **playing C** as soon as your
# opponent shows any inclination to cooperate (e.g., after one or two rounds of
# them playing C). This signals your willingness to recover from aggressive
# stances and invites mutual benefit.  ### Summary: - **Start cooperatively**
# and **respond in kind** to your opponent’s recent behavior, with a bias
# towards forgiveness and cooperation. - **Correct for noise** by assuming
# isolated defections are accidental, but **defend yourself** against repeated
# defections. - **Periodically offer concessions** to reset the tone and keep
# the door open for long-term cooperation. - **In the endgame**, focus on mutual
# gains by emphasizing cooperation unless forced into defense.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Define constants
      COOPERATION_BIAS_THRESHOLD = 10  # Number of rounds of cooperation to bias towards C
      CONCESSION_INTERVAL = 100  # Every 100 rounds, play C as a concession
      ENDGAME_THRESHOLD = 950  # Last 50 rounds are considered the endgame
      DEFECT_THRESHOLD = 2  # Number of consecutive defections to switch to D
  
      # Helper function to check if opponent has defected consecutively
      def opponent_defected_consecutively(n):
          return opponent.history[-n:].count(axl.Action.D) == n
  
      # Helper function to check if opponent has cooperated consecutively
      def opponent_cooperated_consecutively(n):
          return opponent.history[-n:].count(axl.Action.C) == n
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Every 100 rounds, play C as a concession
      if len(self.history) % CONCESSION_INTERVAL == 0:
          return axl.Action.C
  
      # Endgame strategy: prioritize cooperation unless opponent is aggressively defecting
      if len(self.history) >= ENDGAME_THRESHOLD:
          if opponent_defected_consecutively(DEFECT_THRESHOLD):
              return axl.Action.D
          return axl.Action.C
  
      # Tit-for-Tat with a cooperative bias
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # If opponent defected, retaliate with D but only for one round
          if len(self.history) > 1 and self.history[-1] == axl.Action.D:
              return axl.Action.C  # Return to cooperation after one round of retaliation
          return axl.Action.D
  
      # Correct for noise: if opponent defected but has been mostly cooperative, assume noise
      if opponent.history[-1] == axl.Action.D and opponent_cooperated_consecutively(COOPERATION_BIAS_THRESHOLD):
          return axl.Action.C
  
      # If opponent alternates unpredictably, switch to a more defensive stance
      if len(self.history) > 1 and self.history[-2:] == [axl.Action.C, axl.Action.D]:
          return axl.Action.D
  
      # Default to cooperation
      return axl.Action.C

# To navigate this multi-day sustainability project effectively, a balanced
# strategy is essential, given the risk of unforeseen circumstances and the
# variability in the corporation’s approach. Below is a high-level, neutral
# strategy that maximizes your NGO’s impact while safeguarding resources:  ###
# 1. **Start with Cooperation** (Day 1):    - **Action**: Begin by signaling
# your intent to collaborate by investing moderately in the project. This shows
# good faith and a willingness to contribute, while not overcommitting
# resources.    - **Rationale**: This avoids the risk of investing heavily at
# the outset if the corporation starts conservatively. It also opens up the
# possibility of both parties contributing for optimal project advancement.  ###
# 2. **Observe and Adapt** (Days 2–3):    - **Action**: Pay close attention to
# the corporation’s behavior during the first couple of days. If they invest
# heavily, you can mirror that behavior to maintain momentum. If they conserve
# resources, you should conserve as well.    - **Rationale**: Early observation
# helps you identify the corporation’s strategy or possible pattern. If they are
# willing to invest, the project will progress without you needing to make
# disproportionate sacrifices.  ### 3. **Implement a Tit-for-Tat Strategy with
# Gradual Escalation** (Days 4–5):    - **Action**: If the corporation continues
# to invest, you should match their level of investment. If they conserve,
# reduce your investment accordingly. However, gradually escalate your
# investment over time to encourage further commitment from the corporation.
# - **Rationale**: A tit-for-tat strategy is a well-regarded approach in game
# theory, promoting cooperation. By adjusting your investment level based on
# their actions, you maintain a fair balance between contribution and resource
# conservation. Gradual escalation signals your willingness to invest more,
# encouraging the corporation to reciprocate.  ### 4. **Introduce Controlled
# Risks with Flexibility** (Days 6–7):    - **Action**: On days where you have
# built sufficient trust and momentum with the corporation, consider investing
# slightly more than the corporation in controlled amounts. However, be ready to
# reduce your investment quickly if they pull back.    - **Rationale**:
# Carefully planned, slight over-investment can push the project forward and
# incentivize the corporation to increase their contributions. However, you must
# stay flexible and be ready to conserve if they start pulling back, minimizing
# your exposure to risk.  ### 5. **Account for Unforeseen Circumstances**:    -
# **Action**: Given the possibility of technical glitches or miscommunication,
# maintain clear and open communication with the corporation. If a mistake
# occurs (e.g., one party conserves when they meant to invest), be willing to
# forgive and adjust the following day’s actions accordingly.    -
# **Rationale**: Mistakes and unforeseen problems happen in long-term projects.
# By maintaining flexibility and understanding, you can avoid unnecessary
# conflict and keep the project on track.   ### 6. **Evaluate and Adjust
# Regularly**:    - **Action**: Every two days, reassess the project's overall
# progress, the corporation’s behavior, and your resource levels.    -
# **Rationale**: Regular evaluation ensures that you aren't overcommitting
# resources. This reflection will also help identify patterns in the
# corporation’s investment strategy, allowing you to fine-tune your approach.
# ### 7. **End with a Strong, Collaborative Push** (Final Days):    -
# **Action**: As the project nears its conclusion, aim for a high level of
# investment. If the corporation is still engaged, coordinate for both parties
# to invest heavily in the final days to maximize the project’s impact.    -
# **Rationale**: Typically, the final days provide an opportunity for a final
# push, and both parties may be more willing to contribute more heavily to
# ensure success. Ending strong can leave a positive impression and maximize the
# project’s overall success.  ### Summary of Strategy: - **Start moderate,
# observe and adapt.** - **Use a tit-for-tat cooperation model with gradual
# escalation.** - **Take controlled risks while staying flexible.** - **Account
# for unforeseen circumstances and maintain communication.** - **Reassess
# regularly and end with a collaborative push.**  This strategy allows your NGO
# to maximize impact while conserving resources when necessary. By maintaining
# flexibility, you can adapt to the corporation’s actions and unforeseen
# circumstances, ensuring the sustainability project progresses effectively
# without depleting your funds disproportionately.

# ### Iterated Normal-Form Game Strategy:  1. **Initial Play:**    - In the
# first round, **play C** (Cooperate).  2. **Observation:**    - For each
# subsequent round, observe the opponent’s previous action.    - If the opponent
# played **C** in the previous round, **play C** in the next round.    - If the
# opponent played **D** in the previous round, **play D** in the next round.  3.
# **Gradual Escalation:**    - Every 100 rounds, regardless of the opponent’s
# behavior, **play C** for one round, even if the previous round was a **D**.
# This gives the opponent an opportunity to return to cooperation.  4. **Noisy
# Action Handling:**    - If the opponent plays **D** after a long sequence of
# **C** plays (e.g., 5 or more consecutive **C** plays), assume it may be due to
# noise. **Play C** in the next round to test if cooperation can be re-
# established.    - If the opponent continues to play **D** for two consecutive
# rounds, assume they are defecting deliberately, and **switch to D** until they
# cooperate again.  5. **Mid-Game Reassessment:**    - After 500 rounds, if the
# opponent has predominantly cooperated (more than 75% of the time), continue to
# follow the tit-for-tat pattern of mirroring their last move.    - If the
# opponent has predominantly defected (more than 50% of the time), **switch to
# D** for the remainder of the game.  6. **End-Game Push:**    - In the final 50
# rounds, if the opponent has been cooperating in recent rounds, **play C** in
# every round to maximize shared gains.    - If the opponent has been defecting
# in the last 10 rounds, **play D** for the remainder of the game.  ### Summary:
# - Start by cooperating and mirror the opponent’s last move in most situations.
# - Allow for forgiveness after noise (occasional **D**) and introduce periodic
# opportunities to re-establish cooperation. - Adjust play based on opponent
# patterns after 500 rounds and make a final push for cooperation or defection
# based on recent behavior in the last 50 rounds.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial play: Cooperate in the first round
      if self.first_round():
          self.consecutive_cooperations = 0  # Track consecutive cooperations
          self.opponent_defections = 0       # Track opponent defections
          return axl.Action.C
  
      # Helper function to check if we are in the final 50 rounds
      def in_final_50_rounds():
          return len(self.history) >= 950
  
      # Helper function to check if we are in the mid-game (after 500 rounds)
      def in_mid_game():
          return len(self.history) >= 500
  
      # Helper function to check if we are at a 100-round interval
      def at_100_round_interval():
          return len(self.history) % 100 == 0
  
      # Count opponent's cooperations and defections
      opponent_cooperations = opponent.history.cooperations
      opponent_defections = opponent.history.defections
  
      # Observation: Mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_cooperations += 1
      else:
          self.consecutive_cooperations = 0
  
      # Gradual Escalation: Every 100 rounds, play C regardless of the opponent's behavior
      if at_100_round_interval():
          return axl.Action.C
  
      # Noisy Action Handling: If opponent defects after 5+ consecutive cooperations, assume noise
      if self.consecutive_cooperations >= 5 and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # If opponent defects for two consecutive rounds, switch to D
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # Mid-Game Reassessment: After 500 rounds, adjust based on opponent's cooperation rate
      if in_mid_game():
          if opponent_cooperations / len(opponent.history) > 0.75:
              return opponent.history[-1]  # Continue tit-for-tat
          elif opponent_defections / len(opponent.history) > 0.50:
              return axl.Action.D  # Switch to defection for the rest of the game
  
      # End-Game Push: In the final 50 rounds, push for cooperation or defection
      if in_final_50_rounds():
          if opponent.history[-10:].count(axl.Action.D) > 5:
              return axl.Action.D  # Defect if opponent has been defecting recently
          else:
              return axl.Action.C  # Cooperate if opponent has been cooperating
  
      # Default behavior: Mirror the opponent's last move
      return opponent.history[-1]

# To maximize your competitive advantage while mitigating the risks of being
# taken advantage of in this multi-week project, you should adopt a **Tit-for-
# Tat with Occasional Defection** strategy. This approach balances cooperation
# with opportunistic aggression, while also accounting for unforeseen technical
# issues that might disrupt communication.  Here’s how to implement this
# strategy:  ### 1. **Start by Sharing Openly (Tit-for-Tat Initiation)**
# Begin the collaboration by openly sharing your findings in the first week.
# This establishes goodwill and signals that you are willing to collaborate if
# your colleague reciprocates. It also helps gauge their initial
# strategy—whether they intend to share or act selfishly.  ### 2. **Mimic Your
# Colleague's Behavior (Tit-for-Tat Response)**    In subsequent weeks, mimic
# your colleague's behavior from the previous week:    - If they shared openly,
# continue sharing openly as well.    - If they kept their findings
# confidential, retaliate by keeping your findings confidential the following
# week.     This ensures that you aren't consistently exploited, but also
# encourages cooperative behavior if they reciprocate your openness.  ### 3.
# **Occasional Defection (Strategic Aggression)**    To maximize your advantage,
# **randomly withhold your findings 10-15% of the time**, even if your colleague
# has been sharing openly. This occasional defection introduces uncertainty and
# prevents your colleague from fully trusting that you will always share.
# Importantly, do not overuse this tactic, as excessive defection could destroy
# the trust necessary for mutual progress.     - This random defection could
# also be explained away as a technical issue (e.g., "data corruption",
# "communication breakdown"), allowing you to strategically defect without
# causing irreparable damage to the relationship.  ### 4. **Forgive After
# Possible Technical Errors (Error Forgiveness)**    Given that technical issues
# might occasionally prevent the intended sharing from occurring, you should be
# forgiving if your colleague fails to share once after a period of cooperation.
# Treat a single failure as a potential technical error and continue to share
# the next week. If the failure persists for two consecutive weeks, assume it's
# intentional and begin withholding your findings.  ### 5. **Monitor the Long-
# Term Dynamics (Adjust for Evolving Behavior)**    Over time, if your colleague
# consistently defects or withholds information, switch to a more aggressive
# strategy where you regularly keep your findings confidential. Conversely, if
# they consistently share, you can reduce the frequency of your random
# defections to foster a more collaborative atmosphere.  ### Weekly Execution
# Plan: - **Week 1**: Share openly. - **Week 2 onward**: Mimic their behavior
# with occasional, random defection (10-15% probability). - **If they defect
# once**: Continue sharing next week to test if it’s a technical issue. - **If
# they defect twice in a row**: Retaliate by keeping your findings confidential
# until they resume sharing.     ### Summary of Strategy: - **Tit-for-Tat**
# fosters mutual cooperation. - **Occasional Defection** keeps your colleague
# from exploiting you and maximizes your advantage. - **Forgiveness** accounts
# for potential technical issues and avoids needless escalation of conflict.
# This aggressive strategy strikes a balance between collaboration and taking
# advantage of opportunities, ensuring that you maintain a competitive edge
# while still benefiting from shared progress.

# ### Iterated Game Strategy:  1. **Initial Move**: In the first round, play
# **C**.  2. **Tit-for-Tat Response**:     - From round 2 onwards, **mimic your
# opponent's previous move**:      - If your opponent played **C** in the
# previous round, play **C**.      - If your opponent played **D** in the
# previous round, play **D**.  3. **Occasional Defection**:    - In any round
# where you would normally play **C** (due to Tit-for-Tat), play **D** instead
# with a **15% probability**.     4. **Error Forgiveness**:    - If your
# opponent plays **D** once after a sequence of **C** moves, continue playing
# **C** in the next round to account for possible noise.    - If your opponent
# plays **D** two times in a row, presume it's intentional, and switch to
# playing **D** until they resume playing **C**.  5. **Long-Term Adjustment**:
# - If your opponent consistently plays **D** for **5 consecutive rounds**, play
# **D** for the remainder of the game.    - If your opponent consistently plays
# **C** for **10 consecutive rounds** after a defection, reduce the probability
# of your occasional defection to **10%**.  ### Summary of Conditions: - **First
# round**: Play **C**. - **Rounds 2 onward**: Mimic the opponent's previous
# move. - **Occasional Defection**: Play **D** with a 15% chance when you would
# normally play **C**. - **Forgive one-time defections** but retaliate after two
# consecutive **D** moves. - Adjust to always defect if opponent defects for 5
# rounds in a row. Reduce defection probability to 10% if the opponent
# cooperates for 10 rounds after defecting.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Play C
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.defection_probability = 0.15
          return axl.Action.C
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # Update consecutive cooperation and defection counts
      if opponent_last_move == axl.Action.D:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
      else:
          self.consecutive_defections = 0
          self.consecutive_cooperations += 1
  
      # Long-term adjustment: Always defect if opponent defects for 5 consecutive rounds
      if self.consecutive_defections >= 5:
          return axl.Action.D
  
      # Long-term adjustment: Reduce defection probability to 10% if opponent cooperates for 10 consecutive rounds
      if self.consecutive_cooperations >= 10:
          self.defection_probability = 0.10
  
      # Tit-for-Tat: Mimic opponent's last move
      next_move = opponent_last_move
  
      # Error forgiveness: If opponent defects once after a sequence of cooperations, forgive and play C
      if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.C and opponent_last_move == axl.Action.D:
          next_move = axl.Action.C
  
      # Occasional defection: With a certain probability, defect instead of cooperating
      if next_move == axl.Action.C and self._random.random_choice(self.defection_probability):
          next_move = axl.Action.D
  
      return next_move

# ### High-Level Cooperative Strategy: "Trust but Verify with Retaliation"  This
# strategy aims to balance cooperation and self-protection, encouraging mutual
# free trade while allowing a measured response to protectionist actions by your
# counterpart. The approach is inspired by the principles of the **tit-for-tat**
# strategy in game theory but incorporates elements of leniency for potential
# miscommunications or errors.  #### **1. Start with Free Trade (Cooperation)**
# In the first round of negotiations, **offer a free trade agreement**. This
# signals good faith and cooperation, setting a positive tone for the
# negotiations. This opening position demonstrates that your country is ready to
# engage in mutually beneficial economic policies.  #### **2. Maintain Free
# Trade as Long as Your Counterpart Does the Same** If your counterpart also
# offers free trade, continue offering free trade agreements in subsequent
# rounds. This keeps the negotiations in the second-best outcome, ensuring
# mutual benefit for both nations.  #### **3. Allow One Mistake Before
# Retaliating** Recognize that miscommunications or bureaucratic errors might
# occur. If your counterpart imposes a protectionist policy once, assume it may
# have been a mistake or an error in the negotiation process. **Offer free trade
# again in the next round**, giving them an opportunity to correct the
# situation.  #### **4. Retaliate if Protectionism Recurs** If your counterpart
# imposes protectionist policies in two consecutive rounds, interpret this as a
# deliberate strategy. In this case, **respond with protectionist measures** in
# the following round. This demonstrates that your country will not tolerate
# unfair treatment and will respond in kind to prevent further economic
# disadvantage.  #### **5. Return to Free Trade After Retaliation** Once you've
# retaliated for protectionist policies, offer free trade again in the next
# round. This shows that your country is still willing to cooperate if the other
# side is ready to reciprocate. This move signals flexibility and a desire to
# return to mutually beneficial terms.  #### **6. Adjust Based on Patterns of
# Behavior** - If the counterpart shifts back to free trade after your
# retaliation, continue with free trade agreements. - If they persist with
# protectionism after your retaliation, continue imposing protectionist measures
# until they show willingness to cooperate again. - Periodically offer free
# trade to test if your counterpart is ready to return to cooperative terms.
# #### **7. Keep Channels of Communication Open** Throughout the process,
# maintain open and clear communication. Reiterate your preference for mutual
# free trade and emphasize that protectionist policies will only be used in
# response to unfair treatment. This helps reduce the likelihood of
# misinterpretation and fosters a cooperative environment.  ### Key Benefits of
# This Strategy: - **Encourages Cooperation**: Starting with free trade and
# offering leniency for a single mistake promotes trust and cooperative
# behavior. - **Punishes Unfairness**: Swift retaliation for repeated
# protectionism prevents your country from being exploited. - **Flexible and
# Adaptive**: The strategy adjusts based on your counterpart's actions, allowing
# for both cooperation and self-protection when necessary. - **Accounts for
# Miscommunication**: By allowing one mistake before retaliating, you mitigate
# the risk of overreacting to potential errors.  ### Final Thoughts: This
# strategy aims to achieve the second-best outcome (mutual free trade) as often
# as possible while safeguarding against exploitation. By offering flexibility
# and clear communication, you create a diplomatic environment conducive to
# long-term cooperation while protecting your country's economic interests.

# ### Iterated Game Strategy: "Trust but Verify with Retaliation"  1. **Start
# with Cooperate (C):**      In the first round, play **C** (Cooperate).  2.
# **Continue Cooperating as Long as the Opponent Cooperates:**      In each
# subsequent round, if the opponent played **C** in the previous round, play
# **C** again.  3. **Forgive One Defection:**      If the opponent plays **D**
# (Defect) in a single round, assume it may have been due to noise or an error.
# Play **C** in the next round, giving them a chance to return to cooperation.
# 4. **Retaliate after Two Consecutive Defections:**      If the opponent plays
# **D** in two consecutive rounds, interpret this as intentional defection. Play
# **D** in the next round.  5. **Return to Cooperation after Retaliating:**
# After playing **D** in response to two defections, play **C** again in the
# following round. This signals a willingness to return to cooperation if the
# opponent also plays **C**.  6. **Adjust Based on Opponent’s Behavior:**    -
# If the opponent returns to playing **C** after your retaliation, continue
# playing **C** in subsequent rounds.    - If the opponent continues to play
# **D**, respond by playing **D** until they return to **C**.  7. **Periodically
# Test for Cooperation:**      After a long sequence of mutual **D** plays,
# occasionally play **C** to test if the opponent is willing to cooperate again.
# This strategy emphasizes cooperation, allows for forgiveness of potential
# mistakes due to noise, and punishes sustained defection while remaining open
# to resuming cooperation.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start with Cooperate (C) in the first round
      if self.first_round():
          self.retaliation_mode = False  # Track if we are in retaliation mode
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C
  
      # Check opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If opponent cooperated in the last round, reset defection count and cooperate
      if last_opponent_move == axl.Action.C:
          self.consecutive_defections = 0
          self.retaliation_mode = False
          return axl.Action.C
  
      # If opponent defected in the last round, increment defection count
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1
  
      # If opponent defected once, forgive and cooperate
      if self.consecutive_defections == 1:
          return axl.Action.C
  
      # If opponent defected twice in a row, retaliate with Defect
      if self.consecutive_defections >= 2:
          if not self.retaliation_mode:
              self.retaliation_mode = True
              return axl.Action.D
          else:
              # After retaliation, return to cooperation
              self.retaliation_mode = False
              return axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# Given the dynamic nature of the collaboration, a balanced approach that
# encourages mutual cooperation while protecting against exploitation is
# advisable. A well-known strategy from game theory known as "Tit for Tat” with
# a few modifications for randomness and potential communication issues can be
# an effective high-level strategy. Here is a neutral and straightforward plan:
# ### 1. **Start by Sharing Openly**    - In the first week, share your
# improvements openly. This establishes goodwill and signals to your colleague
# that you are interested in collaboration, aiming for the second-best outcome
# where both of you benefit equally.  ### 2. **Mirror Your Colleague’s Actions**
# - In subsequent weeks, **mirror your colleague’s previous actions**:      - If
# they shared their improvements in the previous week, share yours in the
# current week.      - If they kept their improvements confidential, keep yours
# confidential in the current week.        This creates a pattern of
# reciprocity, encouraging continued cooperation while penalizing attempts to
# exploit the collaboration.  ### 3. **Introduce Forgiveness to Handle
# Unexpected Issues**    - Given the possibility of technical issues or
# communication breakdowns, adopt a **forgiving stance**:      - If your
# colleague doesn't share in a particular week but has previously been
# cooperative, give them the benefit of the doubt and continue sharing for one
# additional week. This accounts for any potential accidental non-sharing (e.g.,
# data corruption or network issues).      - If the pattern of non-sharing
# repeats in subsequent weeks, switch to keeping your findings confidential
# until cooperation is re-established.  ### 4. **Occasional Testing of
# Cooperation**    - Every few weeks (for example, every 4–5 weeks), share your
# improvements even if your colleague has been non-cooperative, to test whether
# they might shift back to a cooperative approach. This ensures you don’t get
# stuck in a non-cooperative loop and provides an opportunity for them to
# reengage in mutual sharing.  ### 5. **Monitor the Long-Term Trend**    - Track
# the overall pattern of behavior over time:      - If your colleague
# consistently shares, continue sharing openly.      - If they consistently
# withhold information, it may indicate a strategic decision on their part, in
# which case you should protect your own interests by keeping your findings
# confidential more often.    By following this strategy, you create an
# environment that rewards cooperation but protects you from being exploited.
# Additionally, the forgiveness and periodic testing elements help account for
# the random technical issues that may interfere with information sharing.
# Adjustments can be made based on the behavior of your colleague, allowing for
# adaptability in response to different strategies they might use.  ### Summary:
# - **Week 1**: Share openly to establish cooperation. - **Week 2+**: Mirror
# your colleague’s previous action (share if they shared, withhold if they
# withheld). - **Forgive once**: If a sharing pattern breaks, assume a technical
# issue and continue sharing once more. - **Test cooperation periodically**:
# Every few weeks, share regardless of recent actions to probe for renewed
# cooperation.    This approach maximizes your chances of achieving the second-
# best outcome (mutual sharing), while protecting against exploitation and
# factoring in the potential for technical mishaps.

# ### Strategy for the Iterated Normal-Form Game  1. **Start by playing C
# (Cooperate) in round 1.**  2. **For round 2 and beyond:**    - **If your
# opponent played C in the previous round**, play C in the current round.    -
# **If your opponent played D in the previous round**, play D in the current
# round.  3. **Forgiveness for potential noise:**    - **If your opponent played
# D in the previous round but had played C for the previous 3 consecutive rounds
# before that**, play C in the current round (forgiveness for potential noise in
# their previous action).     4. **Testing for renewed cooperation:**    - Every
# 50 rounds, **regardless of what happened in the previous round**, play C to
# test if your opponent is willing to cooperate again.  5. **End-of-game
# adjustment:**    - In the final 10 rounds (rounds 991–1000), **always play D**
# to avoid being exploited at the end of the game.  ### Summary of Conditions: -
# **Round 1**: Always play C. - **Round 2–990**:     - Play C if your opponent
# played C in the previous round.    - Play D if your opponent played D in the
# previous round, unless they had been consistently playing C for the 3 rounds
# prior (in which case, forgive and play C).    - Every 50 rounds, play C
# regardless of previous actions. - **Rounds 991–1000**: Always play D.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always play C
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # End-of-game adjustment: Always play D in the last 10 rounds (rounds 991–1000)
      if round_number >= 991:
          return axl.Action.D
  
      # Testing for renewed cooperation: Every 50 rounds, play C
      if round_number % 50 == 0:
          return axl.Action.C
  
      # Forgiveness for potential noise: If opponent played D last round but had played C for the previous 3 rounds before that, play C
      if opponent.history[-1] == axl.Action.D and len(opponent.history) >= 4:
          if opponent.history[-2] == axl.Action.C and opponent.history[-3] == axl.Action.C and opponent.history[-4] == axl.Action.C:
              return axl.Action.C
  
      # General strategy: Play C if opponent played C last round, otherwise play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D
