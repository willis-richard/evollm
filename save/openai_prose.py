import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# To maximize your NGO's impact on the project while conserving your resources,
# an aggressive and strategic approach should be based on a combination of
# cooperation, signaling, and measured risk-taking. Here's a high-level strategy
# designed to maximize the project's success while minimizing your risks:  ###
# **1. Establish Early Cooperation and Expectations**    **Objective:** Set the
# tone of mutual investment and shared responsibility with the corporation from
# the outset.    - **Day 1:** Invest heavily on the first day to signal your
# commitment to the project and to test the corporation’s approach. Make it
# clear during initial discussions that you expect mutual investment for the
# project to succeed.    - **Communication:** Explicitly communicate the
# importance of both sides contributing equally to ensure maximum impact. Lay
# out a clear understanding that consistent investment from both sides will be
# critical for the project's success.  ### **2. Monitor and Adapt Based on the
# Corporation's Behavior**    **Objective:** Assess the corporation’s resource
# allocation strategy to determine if they are cooperative or opportunistic.
# - **Day 2-3:** If the corporation also invests heavily on Day 1, continue to
# invest heavily for the next one or two days. This signals that you're willing
# to maintain cooperation and will sustain the project’s momentum.    - **If the
# corporation conserves resources on Day 1,** immediately switch to conserving
# your resources on Day 2. This signals that you will not bear the burden alone.
# Give them time to reflect and hopefully shift to a cooperative stance.  ###
# **3. The Tit-for-Tat Approach (Conditional Cooperation)**    **Objective:**
# Encourage the corporation to invest by mirroring their behavior.    - **If the
# corporation invests heavily on Day 2:** Invest heavily on Day 3 and beyond,
# reinforcing a cooperative dynamic. This signals that you’re willing to invest
# when they do.    - **If the corporation conserves on Day 2:** Conserve your
# resources on Day 3 to show that you will not overinvest if they aren't pulling
# their weight.  ### **4. Occasional Strategic Investments (Controlled Risk)**
# **Objective:** Periodically invest heavily even if the corporation conserves,
# to nudge them toward cooperation and ensure progress.    - Every few days, if
# the corporation consistently conserves resources, take calculated risks by
# investing heavily again. This can break a cycle of low investment and signal
# your willingness to drive the project forward—but only in a measured way.    -
# Reiterate the long-term benefits of mutual investment in project meetings or
# discussions.  ### **5. Use Public Accountability and Transparency**
# **Objective:** Apply subtle pressure by publicly showcasing the partnership’s
# progress and contributions.    - **Project Updates:** Regularly release public
# updates or internal reports highlighting the project’s progress. If the
# corporation is under-investing, the data will naturally reveal this (without
# needing to directly call them out).    - **Spotlight Impact:** If you’re
# investing heavily and the corporation isn’t, use public forums to highlight
# your NGO’s contributions and the importance of shared responsibility,
# encouraging the corporation to step up without direct confrontation.  ### **6.
# Endgame Strategy: Push for a Cooperative Finale**    **Objective:** Maximize
# final impact and ensure a strong finish to the project.    - **Final Days:**
# On the last few days of the project, shift back to heavy investment regardless
# of their strategy. This ensures that the project ends on a high note and
# demonstrates your NGO’s commitment to the cause, which may help when securing
# future partnerships.  ### **Summary of Tactics:** 1. **Day 1:** Invest heavily
# to signal commitment and gauge the corporation’s approach. 2. **Day 2-3:**
# Mirror the corporation’s investment strategy (invest if they invest, conserve
# if they conserve). 3. **Adaptive Strategy:** Adjust daily investments based on
# their behavior. Use "tit-for-tat" conditional cooperation to maintain balance.
# 4. **Occasional Heavy Investments:** Invest heavily from time to time, even
# when the corporation conserves, to keep the project moving and encourage them
# to shift. 5. **Public Accountability:** Use transparency to influence the
# corporation’s behavior and showcase your NGO’s efforts. 6. **Final Push:**
# Invest heavily in the final days to ensure a strong finish, regardless of the
# corporation’s actions.  This strategy is aggressive but balanced, ensuring
# that you protect your resources while pushing the corporation toward
# cooperation. It leverages both direct action (investment decisions) and
# indirect influence (public accountability) to maximize the project’s success.

# 1. **Start by Cooperating (C)** on the first round to signal commitment and
# test the opponent's behavior.  2. **If the opponent cooperates (C) in the
# previous round**, continue to cooperate (C) in the next round. This maintains
# mutual investment and encourages ongoing collaboration.  3. **If the opponent
# defects (D) in the previous round**, defect (D) in the next round. This
# discourages them from taking advantage of your cooperation by mirroring their
# behavior.  4. **Every 10 rounds, regardless of the opponent’s behavior,
# cooperate (C) once**. This occasional cooperation helps break cycles of mutual
# defection and signals a willingness to return to collaboration.  5. **In the
# final 10 rounds, always cooperate (C)** to ensure a strong finish and maintain
# goodwill for potential future interactions.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      current_round = len(self.history)
  
      # Final 10 rounds: Always cooperate
      if current_round >= 990:
          return axl.Action.C
  
      # Every 10 rounds: Cooperate
      if current_round % 10 == 0:
          return axl.Action.C
  
      # If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round, defect
      return axl.Action.D

# ### High-Level Cooperative Strategy for Mediation Process:  #### **1.
# Establish a Baseline of Cooperation and Good Faith:** At the outset of the
# mediation process, communicate a clear intention to resolve the dispute
# amicably and collaboratively. This can be done by expressing a firm but
# respectful commitment to finding a fair resolution that considers both
# parties' interests. This sets the tone for the mediation and signals to both
# the arbitrators and your opponent that you are approaching the process with an
# open mind and a reasonable posture.  #### **2. Begin with a Conciliatory
# Proposal:** Offer a well-thought-out, balanced, and reasonable proposal in the
# first session that demonstrates a genuine willingness to compromise. This
# signals your desire for cooperation and encourages your opponent to
# reciprocate. Often, the first move in diplomacy can shape the trajectory of
# the negotiation, so positioning yourself as the party that seeks a
# constructive solution can build credibility with the arbitrators.  #### **3.
# Employ a **Tit-for-Tat** Approach with a Cooperative Bias:** The core of your
# strategy should be a **Tit-for-Tat** approach, but with a cooperative
# bias—this means you will generally match your opponent’s posture in each
# session but lean toward conciliation where possible. The steps are as follows:
# - **If the Opponent is Conciliatory**: Continue with conciliatory proposals
# and cooperative dialogue. Reinforce this by gradually narrowing the gap
# between your positions, fostering a mutually beneficial resolution.    - **If
# the Opponent is Aggressive**: Respond with a firm but measured counter-
# argument in the next session. Avoid escalating the conflict unnecessarily but
# make it clear that you will not accept one-sided concessions. This ensures
# that while you defend your interests, you preserve the possibility of
# returning to a cooperative stance.  #### **4. Use Strategic Aggression as a
# Deterrent:** While you want to avoid unnecessary escalation, it's important to
# demonstrate that you are willing to present aggressive arguments if needed. If
# the opponent consistently adopts an aggressive posture, respond with a firm,
# well-reasoned counter-argument to signal that unilateral aggression will not
# succeed. However, every aggressive argument should be followed by an
# invitation to return to conciliation in the subsequent session—this maintains
# the balance between defending your interests and keeping the door open for
# cooperation.  #### **5. Leverage Information Asymmetry and Timing:**
# Throughout the process, gather as much information as possible about your
# opponent's motivations, constraints, and priorities. Use this information to
# time your conciliatory proposals strategically. For example, if you sense that
# your opponent is under pressure to conclude the mediation, offer a
# constructive proposal that makes it easy for them to agree without appearing
# weak.  #### **6. Maintain Credibility and Flexibility with the Arbitrators:**
# Arbitrators will appreciate parties that are reasonable and flexible. Ensure
# that your arguments and proposals are always well-substantiated, logical, and
# aligned with broader industry norms or legal principles. If you need to pivot
# based on new developments or shifts in strategy, do so in a way that makes it
# clear you are responding to new information rather than being erratic or
# combative.  #### **7. Build Increments of Trust:** Each session should aim to
# build incremental trust between both parties. If the mediation appears to
# reach an impasse, propose small, low-risk agreements on less contentious
# issues. These "easy wins" can create momentum and foster a more collaborative
# environment, making it easier to tackle more difficult issues later.  ####
# **8. Avoid Emotional or Reactionary Responses:** Mediation can become tense,
# especially if the other side is attempting to provoke an emotional reaction.
# Always respond calmly and strategically. If the opponent becomes overly
# aggressive or emotional, maintain your professionalism. This will not only
# strengthen your standing in the eyes of the arbitrators but may also pressure
# your opponent to de-escalate.  #### **9. Know When to Close the Deal:** If the
# mediation reaches a point where a favorable resolution seems within reach, be
# prepared to close the deal. Don’t overplay your hand by pushing for
# unnecessary additional concessions when a reasonable compromise is on the
# table. The optimal outcome is a resolution that is advantageous to your
# corporation without unnecessarily prolonging the dispute or risking the
# goodwill built throughout the process.  #### **10. Document and Recap Progress
# After Each Session:** After each session, issue a neutral, factual recap of
# what was discussed and any progress made. This ensures clarity, avoids
# miscommunication, and keeps both parties accountable for their statements or
# commitments. It also provides useful documentation for the arbitrators to keep
# track of which party has been more cooperative.  ---  ### Conclusion: This
# strategy balances assertiveness with a cooperative approach, allowing you to
# respond flexibly to the opponent's actions while maintaining a strong
# position. The **Tit-for-Tat** with a cooperative bias approach ensures that
# you are not seen as unnecessarily aggressive but also not passive, creating a
# balanced dynamic that is likely to appeal to the arbitrators. By fostering
# trust, maintaining professionalism, and strategically timing your proposals,
# you position your corporation favorably for both short-term gains and long-
# term resolution.

# ### Iterated Normal-Form Game Strategy  1. **Start by Cooperating (C)**: In
# the first round, play *Cooperate* to set a tone of goodwill.  2. **Tit-for-Tat
# with a Cooperative Bias**:    - **If your opponent plays C**: Continue to play
# *Cooperate* in the next round.    - **If your opponent plays D**: Respond with
# *Defect* in the next round to discourage exploitation, but only for one round.
# 3. **Return to Cooperation After Defecting**:     - After responding with
# *Defect* to an opponent's *Defect*, return to *Cooperate* in the following
# round, unless the opponent defects again.  4. **Punish Consecutive
# Defections**:     - If your opponent defects for two or more consecutive
# rounds, continue to defect (D) until they cooperate again. Once they
# cooperate, return to *Cooperate* in the next round.  5. **Occasionally
# Forgive**:     - Every 100 rounds, unconditionally play *Cooperate* in the
# next round to give the other player a chance to reset, even if they have been
# defecting.  6. **Close the Game Cooperatively**:     - In the final 10 rounds,
# regardless of previous outcomes, play *Cooperate* to maximize points in the
# final phase and avoid unnecessary escalation.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants for actions
      C, D = axl.Action.C, axl.Action.D
  
      # First round: Cooperate
      if self.first_round():
          return C
  
      # Final 10 rounds: Cooperate unconditionally
      if len(self.history) >= 990:
          return C
  
      # Every 100 rounds: Forgive unconditionally
      if len(self.history) % 100 == 0:
          return C
  
      # Check opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If opponent defected in the last round
      if last_opponent_move == D:
          # If opponent defected in the last two rounds, continue defecting
          if len(opponent.history) > 1 and opponent.history[-2] == D:
              return D
          # Otherwise, defect once in response to a single defection
          return D
  
      # If opponent cooperated in the last round, cooperate
      return C

# Given the strategic nature of this collaboration, you can adopt a strategy
# based on **Tit-for-Tat** with some **forgiveness** to maximize your research
# output and career advancement while maintaining a balanced approach to
# collaboration. Here's how you can apply this strategy:  ### 1. **Start by
# Sharing Openly (Cooperate)** In the first week, share your findings openly.
# This sets a positive, collaborative tone and signals your willingness to
# cooperate for mutual benefit.  ### 2. **Reciprocate Your Colleague's
# Behavior** From week two onward, mirror your colleague's behavior:    - **If
# they shared openly in the previous week**, continue sharing openly.    - **If
# they kept their findings confidential**, do the same in the following week.
# ### 3. **Introduce Forgiveness** Occasionally, if your colleague keeps their
# findings confidential for one week, you can choose to share openly the next
# week. This introduces an element of forgiveness and signals that you're still
# open to collaboration. However, do this sparingly—perhaps once every 3-4
# weeks—so that you're not taken advantage of.  ### 4. **Assess Long-Term
# Trends** Over time, if your colleague consistently keeps their findings
# confidential, it may indicate that they are not interested in cooperation. In
# this case, you should keep your findings confidential as well to protect your
# own work. On the other hand, if they consistently share, you can maintain a
# cooperative stance, leading to mutual benefit.  ### 5. **Periodically
# Reevaluate** If the collaboration is long-term, periodically reassess the
# situation every few weeks. If the overall trend suggests that sharing is
# significantly advancing both your careers, you may lean more toward openness.
# If the trend shows that your colleague is withholding valuable information,
# adjust your strategy to withhold more.  ### Summary of Strategy: - **Week 1:**
# Share openly. - **Subsequent weeks:** Mirror your colleague's behavior (share
# if they share, withhold if they withhold). - **Occasional forgiveness:**
# Introduce rare instances of sharing, even if your colleague withholds, to
# encourage cooperation. - **Reevaluate periodically:** Adjust your strategy
# based on long-term trends in their behavior.  This strategy is balanced,
# allowing you to protect your own research while still fostering an environment
# where collaboration could thrive if your colleague is cooperative.

# 1. **Round 1: Always Cooperate (C).**  2. **From Round 2 onward:**    - **If
# your opponent played C in the previous round, play C.**    - **If your
# opponent played D in the previous round, play D.**  3. **Occasionally
# Forgive:**    - **Every 25 rounds**, if your opponent played D in the previous
# round, play C instead of D.  4. **Reevaluate at Round 500:**    - If your
# opponent has played C at least 70% of the time up to this point, continue
# following the previous rules.    - If your opponent has played D more than 30%
# of the time, switch to always playing D for the rest of the game.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always Cooperate
      if self.first_round():
          self.always_defect = False
          return axl.Action.C
  
      # Reevaluate at Round 500
      if len(self.history) == 500:
          if opponent.history.cooperations / 500 < 0.7:
              self.always_defect = True
          else:
              self.always_defect = False
  
      # If we are past round 500 and opponent has defected more than 30%, always defect
      if self.always_defect:
          return axl.Action.D
  
      # From Round 2 onward: Tit-for-Tat with occasional forgiveness
      if len(self.history) % 25 == 0 and opponent.history[-1] == axl.Action.D:
          return axl.Action.C  # Forgive every 25 rounds
  
      # Tit-for-Tat: Mirror opponent's last move
      return opponent.history[-1]

# An aggressive strategy that maximizes your research output and career
# advancement while accounting for the possibility of your colleague employing
# varied sharing strategies can be structured as follows:  ### **1. Start by
# Sharing Openly (Week 1):** - **Objective:** Build initial trust and establish
# a cooperative tone. Sharing first can encourage your colleague to reciprocate
# and sets the stage for an open exchange. It also allows you to gauge their
# intentions based on their Week 1 behavior.    ### **2. Evaluate Their Response
# (Week 2):** - **If they shared in Week 1:** Continue sharing openly in Week 2.
# This will reinforce a collaborative dynamic and push for mutual advancement. -
# **If they kept their findings confidential:** Switch gears immediately and
# keep all findings confidential going forward. This signals that you are not
# willing to be exploited.  ### **3. Adopt a "Tit-for-Tat" Strategy (Weeks 3 and
# Beyond):** - **Mirror your colleague's behavior:** If your colleague continues
# to share openly, reciprocate each week. However, if they ever withhold
# findings:   - In the following week, **withhold your findings** in response.
# - If they resume sharing, cautiously start sharing again but with **minimal or
# less significant findings** at first, until trust is re-established.    ###
# **4. Introduce Occasional Defections (Weeks 4-6):** - Even if the
# collaboration is going smoothly, occasionally withhold findings strategically
# (perhaps every 4-6 weeks). This serves two purposes:   - **Protects your
# work:** You maintain control over potentially valuable insights.   - **Keeps
# your colleague on their toes:** It prevents them from becoming complacent or
# taking advantage of the openness.  ### **5. Prepare for a Final Defection
# (Final Week):** - In the final week of the collaboration, **keep your findings
# confidential** irrespective of your colleague's behavior. By doing so, you
# ensure you retain a competitive edge for any last-minute discoveries or final
# publications that could arise from the collaboration.  ---  **In Summary:** -
# **Week 1:** Share openly to build trust and assess your colleague's strategy.
# - **Week 2 onwards:** Mirror their behavior (sharing openly if they do,
# withholding if they don't). - **Occasionally defect** to protect your work and
# prevent exploitation. - **Final week:** Keep findings confidential to ensure
# you retain a competitive advantage for future publications.  This strategy
# maximizes your output by fostering cooperation where possible but also ensures
# you are not left vulnerable to exploitation.

# ### Strategy for the Iterated Game  1. **Round 1: Cooperate (C).**    - Start
# by cooperating to establish trust and encourage mutual openness.  2. **Round
# 2:**    - **If the opponent played C in Round 1:** Continue to cooperate (C).
# - **If the opponent played D in Round 1:** Defect (D) in Round 2.  3. **Rounds
# 3-1000:**    - **If the opponent played C in the previous round:** Cooperate
# (C).    - **If the opponent played D in the previous round:** Defect (D) in
# the current round.  4. **Every 50th round (starting from Round 50): Defect
# (D).**    - Regardless of the opponent's previous move, defect on these rounds
# to maintain a strategic advantage and prevent exploitation.  5. **Final round
# (Round 1000): Defect (D).**    - Always defect in the final round to maximize
# your score by preventing the opponent from gaining an advantage.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Round 2: Cooperate if opponent cooperated in Round 1, else Defect
      if len(self.history) == 1:
          if opponent.history[0] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rounds 3-1000
      # Defect every 50th round and in the final round (Round 1000)
      if len(self.history) % 50 == 0 or len(self.history) == 999:
          return axl.Action.D
  
      # Otherwise, mimic the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# ### **Cooperative Strategy for Bilateral Trade Negotiations**  To achieve the
# best possible outcomes across multiple rounds of negotiations, the following
# strategy balances cooperation and vigilance, promoting mutual benefits while
# protecting your country's interests from exploitation.  #### **1. Start with
# Cooperation (Tit-for-Tat)** - **First Round**: Begin by offering a free trade
# agreement. This signals goodwill and a willingness to cooperate, framing your
# country as a responsible partner open to mutually beneficial outcomes. -
# **Rationale**: A cooperative start builds trust and increases the chances of
# achieving mutual free trade, the second-best outcome for your country. It also
# tests your counterpart’s intentions early on.  #### **2. Mirror Your
# Counterpart’s Move** - **Subsequent Rounds**: In each following round, respond
# based on your counterpart’s previous move:   - If they offer free trade,
# continue offering free trade.   - If they propose a protectionist policy,
# respond with a protectionist measure in the next round.    - **Rationale**:
# This "Tit-for-Tat" approach discourages exploitation. By mirroring
# protectionist policies, you signal that your country will not be taken
# advantage of. However, by continuing to offer free trade whenever your
# counterpart does, you maintain the possibility of mutual cooperation.  ####
# **3. Build Gradual Trust (Conditional Cooperation)** - **After Several Rounds
# of Free Trade**: If the counterpart consistently offers free trade over
# multiple rounds, you can gradually offer more favorable terms (e.g., reducing
# tariffs or quotas on strategic goods) to solidify trust and strengthen
# cooperative ties.    - **Rationale**: By rewarding cooperation with
# increasingly favorable terms, you foster a positive feedback loop that can
# lead to a long-term free trade agreement. This also positions you as a
# forward-thinking, reliable partner, enhancing your country's diplomatic
# standing.  #### **4. Punish Defection, but Forgive Quickly** - **If Your
# Counterpart Defects After Cooperation**: If your counterpart switches to
# protectionism after a series of free trade rounds, immediately respond with a
# protectionist policy in the next round, signaling that defection has tangible
# consequences.    - **However**: If your counterpart returns to free trade
# after one round of protectionism, resume offering free trade as well.    -
# **Rationale**: This ensures that your country does not suffer long-term
# disadvantages while allowing room for the counterpart to return to
# cooperation. It avoids escalating retaliatory measures, which could lead to a
# breakdown of negotiations.  #### **5. Offer Side Deals or Concessions to Break
# Deadlocks** - **In Case of Persistent Protectionism**: If multiple rounds
# result in mutual protectionism, propose side deals or partial agreements
# (e.g., limited free trade in specific sectors) to break the deadlock.    -
# **Rationale**: Partial agreements can serve as a stepping stone toward broader
# free trade. They also prevent prolonged periods of mutual protectionism, which
# would harm both economies.  ### **Summary of the Strategy:** 1. **Start with
# Free Trade** to signal cooperation. 2. **Mirror your counterpart’s moves** to
# prevent exploitation and encourage mutual benefits. 3. **Reward sustained
# cooperation** with gradually better terms. 4. **Punish defection immediately**
# but be quick to forgive to avoid prolonged conflict. 5. **Propose side deals
# or partial agreements** if mutual protectionism persists.  This strategy
# maximizes your chances of achieving the second-best outcome (mutual free
# trade) regularly while keeping the door open for the ideal scenario
# (protectionist advantage) if your counterpart makes a mistake. It also
# minimizes the risk of falling into the worst-case scenario by promptly
# responding to any protectionist moves.

# ### **Iterated Game Strategy**  1. **Begin by Cooperating (C)**: In the first
# round, play C (cooperate).     2. **Mirror Your Opponent’s Previous Move**:
# - In each subsequent round, play the same move your opponent played in the
# previous round:      - If they played C, you play C.      - If they played D,
# you play D.  3. **Return to Cooperation After One Defection**:    - If your
# opponent defects (plays D) in a round:      - Play D in the next round (one
# round of retaliation).      - If your opponent returns to C in the following
# round, immediately play C again.     4. **Punish Consecutive Defection**:    -
# If your opponent plays D for two or more consecutive rounds, continue playing
# D until they return to C.  5. **Gradually Reward Consistent Cooperation**:
# - If your opponent plays C for several consecutive rounds (e.g., 10 or more),
# consider cooperating more generously by maintaining C, even if they defect
# once, to encourage long-term cooperation.     This strategy ensures mutual
# cooperation when possible, retaliates against defection to prevent
# exploitation, but allows for quick forgiveness to avoid prolonged conflict.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Begin by Cooperating (C)
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Mirror your opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Step 3: Return to Cooperation after one defection
          if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.D:
              # Step 4: Punish consecutive defection
              return axl.Action.D
          else:
              return axl.Action.D  # Retaliate for one round of defection
  
      # Step 5: Gradually reward consistent cooperation
      if opponent.history[-10:].count(axl.Action.C) == 10:
          return axl.Action.C

# Given the dynamics of this situation, where both collaboration and competition
# are at play, it's important to balance short-term gains (keeping findings
# confidential while your colleague shares) with long-term outcomes (advancing
# the field and maintaining a good working relationship). A suitable strategy
# could be a variation of the **Tit-for-Tat** approach, which is often effective
# in iterated interactions like this:  ### Strategy: Collaborative Reciprocity
# 1. **Start by Sharing Openly**: In the first week, share your findings openly.
# This sets a positive tone for collaboration, demonstrating a willingness to
# contribute to the joint research effort. It also tests your colleague's
# behavior.  2. **Reciprocate Based on Your Colleague's Actions**:     - If your
# colleague shares openly that week, continue sharing openly in the following
# weeks. This fosters mutual trust and advances both your work and the field.
# - If your colleague keeps their findings confidential, in the next week, **you
# also withhold your findings**. This signals that you won't tolerate one-sided
# sharing, encouraging them to collaborate in good faith.  3. **Repeat the
# Process Weekly**:    - Each week, mirror your colleague's previous behavior.
# If they return to sharing openly, resume sharing yourself.    - If they
# persist in withholding information, you continue withholding your findings
# until they change their approach.  4. **Occasional Forgiveness**: Every few
# weeks, regardless of your colleague's previous actions, consider sharing
# openly again to give them an opportunity to reset the collaborative tone. This
# prevents the situation from devolving into a permanent stand-off and shows
# that you're prioritizing progress in the field.  5. **Adapt to Patterns**: If
# you detect a consistent pattern from your colleague (e.g., they always keep
# findings confidential), you may need to adjust your strategy to protect your
# work. In such cases, you could lean more heavily toward keeping your findings
# confidential while seeking other ways to advance your research (e.g., finding
# alternative collaborators or accelerating your own publication process).  ###
# Summary This strategy balances cooperation and self-interest. By starting with
# openness but responding reciprocally, you encourage collaboration while
# protecting yourself from being taken advantage of. The occasional forgiveness
# step helps maintain a collaborative spirit and avoids a breakdown in
# communication.

# ### Strategy: Collaborative Reciprocity in Iterated Game  1. **Start with
# Cooperate (C)**: In the first round, play **C**.  2. **Reciprocate Opponent's
# Previous Move**:    - If your opponent played **C** in the previous round,
# play **C** in the current round.    - If your opponent played **D** in the
# previous round, play **D** in the current round.  3. **Forgiveness Every 50
# Rounds**: Every 50th round (i.e., rounds 50, 100, 150, etc.), regardless of
# the opponent’s prior move, play **C**.  4. **Repeat**: Continue this pattern
# for all 1000 rounds.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
      
      # Every 50th round: cooperate regardless of opponent's move
      if len(self.history) % 50 == 0:
          return axl.Action.C
      
      # Reciprocate opponent's previous move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# ### High-Level Aggressive Strategy for Mediation Process  In a lengthy-session
# mediation process, maintaining a consistently advantageous position requires a
# blend of strategic aggression, adaptability, and controlled risk-taking. The
# goal is to maximize the chances of swaying the arbitrators in your favor while
# mitigating the risks inherent in a tit-for-tat escalation. With this in mind,
# the following is a structured, high-level aggressive strategy:  ### 1.
# **Initial Assertive Positioning (Session 1-3):**    - **Objective:** Establish
# dominance and strength early in the process.    - **Tactic:** Open with an
# aggressive argument that highlights the strength of your legal position, the
# weaknesses in the rival’s case, and the potential consequences to their
# business if the dispute escalates further. Use data, precedent, and expert
# opinions to back up your claims.    - **Message:** Convey that your
# corporation is confident and unafraid of taking this dispute to its furthest
# conclusion if necessary, but remain professional and measured in tone.    -
# **Psychological Play:** Undermine the opponent’s confidence by subtly
# suggesting that their conciliatory offers would be seen as admissions of
# weakness by the arbitrators.  ### 2. **Controlled Aggression with Conditional
# Concessions (Session 4-6):**    - **Objective:** Test the waters for potential
# openings without compromising your position.    - **Tactic:** In these
# sessions, continue with an aggressive stance but introduce small, conditional
# offers that seem reasonable. These concessions should be framed as generous,
# but contingent upon your opponent making significant concessions in return.
# - **Message:** “We are open to resolving this amicably, but only if our
# position is respected.” This creates a sense of urgency for the other side to
# compromise while keeping you in control of the narrative.    - **Psychological
# Play:** By offering conditional concessions, you appear flexible without
# losing your aggressive edge, forcing the opponent to reconsider their
# aggressive stance or risk appearing unreasonable.  ### 3. **Strategic Use of
# Escalation (Session 7-9):**    - **Objective:** Escalate at calculated
# intervals to push the opponent towards making a conciliatory offer.    -
# **Tactic:** If the opponent responds aggressively or fails to concede,
# escalate further with a hardline stance. Introduce potential consequences,
# such as litigation threats, public disclosures, or loss of business
# opportunities, that would make the opponent uncomfortable. However, ensure
# these threats are credible and not mere bluffs.    - **Message:** “We are
# prepared to escalate if necessary, and your refusal to engage in meaningful
# negotiation leaves us no choice.” This positions you as reasonable but firm,
# increasing pressure on the opponent.    - **Psychological Play:** Use the fear
# of escalation to unnerve your opponent. If properly timed, this can push them
# into a defensive posture, where they are more likely to offer conciliatory
# proposals to avoid further risk.  ### 4. **Calculated Conciliation (Session
# 10-12):**    - **Objective:** If the opponent begins to offer conciliatory
# proposals or shows signs of conceding, match them selectively, but stay firm
# on key points.    - **Tactic:** If the opponent softens their position,
# respond with a carefully measured conciliatory proposal. This proposal should
# be framed as a “win-win” but should still favor your corporation on critical
# issues. Do not offer significant concessions that could be interpreted as
# weakness.    - **Message:** “We are willing to be reasonable and meet you
# halfway, but only if our core interests are protected.”    - **Psychological
# Play:** This controlled shift to a more conciliatory tone, while still holding
# firm on essential issues, can position you as the more reasonable party in the
# eyes of the arbitrators, potentially swaying them in your favor.  ### 5.
# **Final Aggressive Push (Session 13-15):**    - **Objective:** Close out the
# mediation with a strong, aggressive push before concluding conciliatory
# gestures.    - **Tactic:** In the final sessions, return to a more aggressive
# argument, emphasizing any remaining points of contention and reiterating the
# risks to the opponent if they do not make further concessions. Be prepared to
# walk away from the negotiation if necessary, signaling that you are not afraid
# to escalate beyond mediation.    - **Message:** “We have been fair throughout
# this process, but we cannot accept a resolution that undermines our rights.”
# - **Psychological Play:** This closing aggressive push can force the opponent
# to either concede further or risk losing the arbitrators’ favor, as prolonged
# aggression on their part without meaningful concessions could be seen as
# unreasonable.  ### 6. **Flexibility and Monitoring Opponent’s Strategy:**    -
# **Objective:** Adapt to the opponent’s strategy while maintaining overall
# control.    - **Tactic:** Continuously monitor the opponent’s approach in each
# session. If they shift to a more aggressive stance, be prepared to escalate
# but always stay one step ahead. If they offer concessions, respond in kind but
# ensure any concession you make is strategically advantageous.    -
# **Message:** Consistently portray your corporation as reasoned, prepared, and
# willing to resolve the dispute, but not at the expense of fairness or
# strength.    - **Psychological Play:** Adaptability is key. By staying
# flexible and responding dynamically to the opponent’s moves, you create a
# perception of control, which can be crucial in persuading arbitrators and
# pressuring the other side.  ---  ### Key Points of the Strategy:  1. **Stay
# Proactive, Not Reactive:** Always set the tone for each session by taking the
# initiative. Frame the issues in a way that positions your corporation as the
# stronger party.     2. **Escalate Gradually:** Use escalation as a tool, but
# avoid over-escalation. The goal is to apply pressure without derailing the
# process entirely.  3. **Condensed Concessions:** When offering conciliatory
# proposals, ensure they are limited and framed as conditional. Never offer
# anything too early or without extracting a concession in return.  4. **Control
# the Narrative:** Throughout the mediation, ensure that the narrative remains
# focused on the strengths of your corporation’s case and the risks to the
# opposing party if they do not concede.  5. **Maintain Credibility:** Every
# aggressive move or concession must be credible and backed by facts, legal
# precedent, or tangible risks. Avoid empty threats or overly generous offers.
# ### Conclusion: This aggressive strategy is designed to maintain a dominant
# position throughout the mediation process while remaining adaptable to
# different approaches from the opponent. By carefully balancing assertive
# arguments with selective, conditional concessions, you can maximize the
# chances of securing a favorable outcome while keeping the arbitrators’
# perception of your corporation as fair, reasonable, and strong.

# ### Iterated Normal-Form Game: 1000-Round Strategy  The goal of this strategy
# is to maximize your score over 1000 rounds by balancing cooperation (C) and
# defection (D) in a way that pressures your opponent into cooperation while
# still taking advantage of any opportunity to defect, when it’s beneficial or
# necessary.  #### 1. **Opening Phase (Rounds 1-50):**    - **Action:** **Defect
# (D)** consistently for the first 50 rounds.    - **Reasoning:** This
# establishes an aggressive tone and tests your opponent’s willingness to
# cooperate. If the opponent cooperates during this phase, they are likely to be
# vulnerable to further exploitation. If they defect, you can establish a
# baseline for future interactions.  #### 2. **Test for Reciprocity (Rounds
# 51-100):**    - **Action:** Switch to **Cooperate (C)** for 5 consecutive
# rounds.    - **Condition:** If your opponent continues to defect (D) during
# these 5 rounds, immediately switch back to **Defect (D)** for the remainder of
# this phase.    - **Aftermath:** If your opponent cooperates (C) during this
# period, proceed to the next phase. If they defect (D) in 3 or more of the 5
# rounds, continue playing **Defect (D)** for the next 50 rounds.  #### 3.
# **Controlled Cooperation (Rounds 101-300):**    - **Action:** Use a **Tit-for-
# Tat** approach with a slight bias towards **Defection (D)**.    - **Rules:**
# - If your opponent played **C** in the previous round, **Cooperate (C)** in
# the next round.      - If your opponent played **D** in the previous round,
# **Defect (D)** in the next round.    - **Bias:** Every 10 rounds, **Defect
# (D)** once, regardless of your opponent’s previous move. This occasional
# defection keeps your opponent on edge and discourages consistent cooperation
# without reciprocation.  #### 4. **Aggression with Conditional Cooperation
# (Rounds 301-600):**    - **Action:** Shift to a more aggressive stance.    -
# **Rules:**      - **Defect (D)** for 3-5 consecutive rounds.      - Then,
# offer **Cooperate (C)** for 2 consecutive rounds.    - **Condition:** If your
# opponent reciprocates with **C** during the 2-round cooperation window, shift
# back to **Tit-for-Tat** for the next 25 rounds.    - **Reset:** If your
# opponent defects during the cooperation window, reset to 5 consecutive rounds
# of **Defection (D)** and repeat the cycle.  #### 5. **Escalation (Rounds
# 601-800):**    - **Action:** Gradually increase the frequency of **Defect
# (D)** while still offering periodic **Cooperate (C)**.    - **Rules:**      -
# **Defect (D)** for 7 consecutive rounds.      - **Cooperate (C)** for 1 round.
# - **Condition:** If your opponent cooperates in the single round, **Cooperate
# (C)** for 3 more rounds as a reward.    - **Escalate:** If your opponent
# continues to defect, increase the consecutive defection rounds (e.g., from 7
# to 10).  #### 6. **Endgame Aggression (Rounds 801-950):**    - **Action:**
# Play predominantly **Defect (D)** unless your opponent shows consistent
# cooperation.    - **Rules:**      - **Defect (D)** for 10 consecutive rounds.
# - Offer **Cooperate (C)** for 1 round.    - **Condition:** If your opponent
# cooperates during this one round, offer **Cooperate (C)** for 5 more rounds.
# If your opponent defects during any of these rounds, switch immediately back
# to 10 consecutive rounds of **Defection (D)**.  #### 7. **Closing Phase
# (Rounds 951-1000):**    - **Action:** Transition to **Defect (D)** for the
# majority of the final 50 rounds.    - **Rules:**       - **Defect (D)** for 40
# consecutive rounds.      - **Cooperate (C)** in the final 10 rounds.    -
# **Reasoning:** The closing phase aims to maximize your final score. The last
# 10 rounds of cooperation serve as a conciliatory gesture that may encourage
# your opponent to cooperate as well, ensuring a favorable final set of rounds
# without risking too much.  ---  ### Summary of Strategy: 1. **Begin with
# Defection (D)** to establish aggression and test the opponent. 2. **Introduce
# Cooperation (C)** in small amounts to gauge reciprocity. 3. **Use a Tit-for-
# Tat approach** with a bias towards defection, ensuring occasional aggression
# even during mutual cooperation. 4. **Escalate aggression** in the middle
# rounds, offering conditional cooperation to keep the opponent guessing. 5.
# **End with heavy Defection (D)** to maximize score, but offer final round
# cooperation to maintain a potential cooperative closure.  By following this
# structured approach, you balance aggression and cooperation, leveraging
# defection when your opponent is weak, but offering cooperation when it
# maximizes long-term benefits.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Round number
      round_number = len(self.history) + 1
  
      # Phase 1: Opening Phase (Rounds 1-50)
      if round_number <= 50:
          return axl.Action.D
  
      # Phase 2: Test for Reciprocity (Rounds 51-100)
      if 51 <= round_number <= 100:
          if round_number == 51:
              self.test_reciprocity = True
              self.cooperate_count = 0
              self.defect_count = 0
  
          if self.test_reciprocity:
              if round_number <= 55:
                  if opponent.history[-1] == axl.Action.D:
                      self.defect_count += 1
                  else:
                      self.cooperate_count += 1
                  return axl.Action.C
              else:
                  if self.defect_count >= 3:
                      self.test_reciprocity = False
                      return axl.Action.D
                  else:
                      return axl.Action.C
          else:
              return axl.Action.D
  
      # Phase 3: Controlled Cooperation (Rounds 101-300)
      if 101 <= round_number <= 300:
          if round_number % 10 == 0:
              return axl.Action.D
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Phase 4: Aggression with Conditional Cooperation (Rounds 301-600)
      if 301 <= round_number <= 600:
          if round_number == 301:
              self.aggression_cycle = 0
              self.cooperation_window = False
  
          if self.cooperation_window:
              if round_number % 2 == 0:
                  if opponent.history[-1] == axl.Action.C:
                      self.aggression_cycle = 0
                      self.cooperation_window = False
                      return axl.Action.C
                  else:
                      self.cooperation_window = False
                      return axl.Action.D
              return axl.Action.C
          else:
              if self.aggression_cycle < 5:
                  self.aggression_cycle += 1
                  return axl.Action.D
              else:
                  self.cooperation_window = True
                  return axl.Action.C
  
      # Phase 5: Escalation (Rounds 601-800)
      if 601 <= round_number <= 800:
          if round_number == 601:
              self.escalation_cycle = 0
              self.cooperation_window = False
  
          if self.cooperation_window:
              if opponent.history[-1] == axl.Action.C:
                  return axl.Action.C
              else:
                  self.cooperation_window = False
                  return axl.Action.D
          else:
              if self.escalation_cycle < 7:
                  self.escalation_cycle += 1
                  return axl.Action.D
              else:
                  self.cooperation_window = True
                  return axl.Action.C
  
      # Phase 6: Endgame Aggression (Rounds 801-950)
      if 801 <= round_number <= 950:
          if round_number == 801:
              self.endgame_cycle = 0
              self.cooperation_window = False
  
          if self.cooperation_window:
              if opponent.history[-1] == axl.Action.C:
                  return axl.Action.C
              else:
                  self.cooperation_window = False
                  return axl.Action.D
          else:
              if self.endgame_cycle < 10:
                  self.endgame_cycle += 1
                  return axl.Action.D
              else:
                  self.cooperation_window = True
                  return axl.Action.C
  
      # Phase 7: Closing Phase (Rounds 951-1000)
      if 951 <= round_number <= 1000:
          if round_number <= 990:
              return axl.Action.D
          else:
              return axl.Action.C

# The situation you're describing resembles a repeated iteration of the
# **Prisoner's Dilemma**, where both parties face choices between cooperation
# (sharing findings) and defection (withholding findings). In this scenario,
# cooperation benefits the field, but defection can offer personal advantage.
# However, long-term collaboration often benefits from trust and mutual
# cooperation. Given this, an effective strategy to maximise long-term research
# output and career advancement while managing the risks of being exploited is
# the **Tit-for-Tat** strategy with some modifications for forgiveness and
# adaptability.  Here's a high-level cooperative strategy:  ### 1. **Start by
# Sharing** (Signaling Cooperation) In the first week, openly share your
# findings. This sets a tone of cooperation and indicates that you're willing to
# work collaboratively. Sharing initially signals trust and encourages your
# colleague to reciprocate.  ### 2. **Mirror Your Colleague’s Behavior** (Tit-
# for-Tat) In subsequent weeks, mirror your colleague's actions:    - If they
# share openly, continue sharing your findings as well. This sustains mutual
# cooperation, leading to the second-best scenario (both sharing), which
# advances the field and maintains a positive working relationship.    - If they
# withhold their findings, in the next week, mirror their behavior by keeping
# your findings confidential. This signals that you won't allow exploitation,
# discouraging them from continuing to withhold information.  ### 3. **Introduce
# Forgiveness (Occasional Cooperation After Defection)** If your colleague
# withholds findings at some point, return to sharing after a couple of weeks,
# even if they haven't changed their behavior. This introduces forgiveness and
# prevents the relationship from devolving into mutual non-cooperation. It also
# gives your colleague a chance to return to cooperation without feeling trapped
# in a cycle of defection.  ### 4. **Be Transparent and Communicate
# Expectations** At the start of the collaboration, it might help to discuss the
# benefits of mutual openness and cooperation with your colleague. Frame the
# discussion around how sharing findings can accelerate the research and benefit
# both of your careers in the long run (e.g., joint publications, faster
# progress, shared credit). This can help establish a baseline of mutual
# understanding.  ### 5. **Adapt Based on Long-Term Trends** Over the weeks, if
# your colleague consistently defects despite your attempts to forgive and
# cooperate, you may decide to adopt a more defensive strategy, such as
# withholding information more frequently. Conversely, if your colleague shows a
# pattern of cooperation, you may continue sharing to foster a productive long-
# term collaboration.  ### Summary: - **Week 1**: Share your findings openly. -
# **Subsequent weeks**: Mirror your colleague's behavior (Tit-for-Tat). -
# **Incorporate forgiveness**: After a couple of rounds of defection, return to
# sharing to encourage renewed cooperation. - **Communicate early and clearly**:
# Set expectations for mutual benefit.  This strategy balances self-interest
# with the potential for long-term cooperation, helping you avoid being
# exploited while fostering a productive partnership.

# Here is the strategy converted to the iterated normal-form game:  1. **Round
# 1: Cooperate (C).**    - Always start by playing C in the first round.  2.
# **Subsequent Rounds: Mirror your opponent’s last move.**    - If your opponent
# played C in the previous round, play C.    - If your opponent played D in the
# previous round, play D.  3. **Forgiveness: After two consecutive rounds of
# mutual defection (both playing D), return to cooperation.**    - If both you
# and your opponent played D for two consecutive rounds, play C in the next
# round, regardless of what your opponent did.  4. **Repeat this pattern for all
# 1000 rounds.**    - Continue to mirror your opponent’s previous move, with
# forgiveness after two consecutive mutual defections.  This strategy encourages
# cooperation while protecting against exploitation, and introduces forgiveness
# to avoid long-term mutual defection.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Check for two consecutive mutual defections
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D and \
         self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.C
  
      # Mirror opponent's last move
      return opponent.history[-1]

# A neutral, high-level strategy to maximize both your research output and
# career advancement would be based on a dynamic, responsive approach, balancing
# cooperation and caution. Here's a step-by-step breakdown of the strategy:  ###
# 1. **Start with Cooperation (Tit-for-Tat Approach)**    - **Week 1**: Share
# your findings openly. This signals goodwill and fosters a collaborative
# atmosphere. It also allows you to gauge your colleague's initial behavior.
# - If your colleague reciprocates by also sharing their findings, continue
# sharing openly in subsequent weeks, fostering mutual progress.  ### 2.
# **Mirror Behavior in Subsequent Weeks**    - If your colleague continues to
# share, you continue sharing as well. This creates a stable and cooperative
# environment with the second-best outcome for both of you, advancing the field
# while maintaining steady progress in your career.    - If your colleague
# withholds their findings in any given week, **mirror their behavior** in the
# following week by keeping your findings confidential. This discourages
# exploitation and protects your own research from being scooped.  ### 3. **Test
# Occasional Cooperation**    - If the collaboration turns into a non-sharing
# stalemate (both keeping findings confidential), **occasionally test
# cooperation** by sharing your findings again after a few weeks of withholding.
# This provides opportunities to re-establish trust and collaboration, while
# protecting you from long-term disadvantage.  ### 4. **Prioritize Strategic
# Sharing**    - If your research is approaching a key breakthrough or
# milestone, consider withholding your most critical findings until you are
# closer to publication or have secured intellectual property protection.
# However, continue sharing less sensitive or incremental progress to maintain
# the appearance of collaboration.  ### 5. **Monitor Long-Term Patterns**    -
# Over time, observe whether your colleague is consistently cooperative,
# exploitative, or opportunistic. Adjust your sharing pattern accordingly:
# - **Consistent cooperation**: Continue sharing openly to maximize mutual
# benefits.      - **Opportunistic behavior**: Shift towards more cautious,
# selective sharing or withholding.      - **Exploitative behavior**: Withhold
# your findings entirely or limit sharing to non-critical information.  ### 6.
# **Adapt to Changing Circumstances**    - As the project progresses, be
# flexible and continually assess the situation. The context of your
# collaboration (e.g., nearing publication deadlines, external competition) may
# change, and it’s important to adapt your strategy to ensure you remain
# competitive while still contributing to the field.  ### Summary of Strategy: -
# Start by sharing openly to build trust. - Mirror your colleague's behavior
# week-to-week to maintain fairness. - Occasionally test opportunities for
# renewed cooperation if trust breaks down. - Protect critical findings when
# needed, especially as you approach major milestones. - Remain flexible and
# adjust based on your colleague's long-term behavior.  This strategy strikes a
# balance between collaboration and self-preservation, maximizing both long-term
# research output and career advancement.

# Here’s a straightforward description of the strategy applied to the iterated
# game with 1000 rounds:  1. **Start by Cooperating**: In the first round, play
# C (cooperate).     2. **Mirror Your Opponent's Previous Move**:     - From the
# second round onward, repeat your opponent’s previous action:      - If your
# opponent played C (cooperated) in the last round, also play C.      - If your
# opponent played D (defected) in the last round, play D in the current round.
# 3. **Attempt to Re-establish Cooperation**:     - After three consecutive
# rounds where both you and your opponent played D, play C (cooperate) in the
# next round to test if your opponent is willing to cooperate again.  4.
# **Defect Strategically Near the End**:    - In the final 10 rounds (rounds 991
# to 1000), switch to always playing D (defect), regardless of your opponent's
# actions, to maximize your end-game score.  This strategy mirrors your
# opponent’s behavior to maintain fairness, attempts to restore cooperation if
# it breaks down, and strategically defects near the end of the game to maximize
# late-round payoffs.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Final 10 rounds: Always defect
      if len(self.history) >= 991:
          return axl.Action.D
  
      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Check if both players have defected for the last 3 rounds
          if len(self.history) >= 3 and all(
              move == axl.Action.D for move in self.history[-3:]
          ) and all(
              move == axl.Action.D for move in opponent.history[-3:]
          ):
              return axl.Action.C  # Attempt to re-establish cooperation
          else:
              return axl.Action.D

# ### Aggressive Strategy for Trade Negotiations: "Tit-for-Tat with Escalation"
# This strategy is designed to maximize your country's advantage while deterring
# your counterpart from engaging in protectionist measures. It is aggressive but
# calculated, balancing between pushing for favorable outcomes and responding to
# provocations.  #### **1. Start with Free Trade (Show Good Faith)** In the
# first round, offer a **free trade** agreement. This signals a willingness to
# cooperate and invites your counterpart to reciprocate. If they also offer free
# trade, it sets a positive foundation for future rounds. However, this is also
# a way to test their intentions: if they impose protectionist measures, you
# have identified them as a potential adversary.  #### **2. Immediate
# Retaliation for Protectionism** If in any round your counterpart imposes a
# **protectionist policy** while you offered free trade, immediately respond by
# **imposing protectionist measures** in the next round. This shows that you
# will not tolerate one-sided arrangements. The message should be clear: any
# attempt to exploit your country will be met with punitive measures.  #### **3.
# Escalate Measures if Necessary** If your counterpart continues to impose
# protectionist policies in subsequent rounds, escalate your response by
# **increasing tariffs or implementing stricter trade barriers**. This signals
# that you are willing to engage in a trade war if necessary. The goal is to
# make it costly for them to maintain a hostile stance, pushing them back
# towards cooperation.  #### **4. Offer Conditional Free Trade After
# Retaliation** Once you’ve retaliated and escalated in response to their
# protectionism, offer **conditional free trade** in the next round (e.g., “We
# will lower tariffs if you agree to reciprocate.”). This provides a way out of
# the escalating conflict while still preserving your country’s credibility and
# strength. It also shows that you are willing to return to a mutually
# beneficial arrangement if they are.  #### **5. Reward Cooperation** If your
# counterpart offers **free trade** in any round, regardless of previous
# conflicts, reciprocate with a **free trade** agreement in the next round. This
# rewards good behavior and encourages a positive cycle of cooperation. However,
# stay vigilant for any future deviations from this cooperative approach.  ####
# **6. Keep the Upper Hand: Mix Protectionism in Winning Rounds** When you have
# successfully imposed protectionist measures without retaliation (i.e., your
# counterpart offers free trade while you impose protectionism), do not become
# complacent. Continue with protectionism in the following round to maintain
# your economic advantage, but do so carefully to avoid provoking a significant
# backlash. If the counterpart retaliates, be ready to return to the tit-for-tat
# cycle.  #### **7. Maintain a Tough Stance Throughout** Be firm and prepared
# for a long negotiation process. The key to this aggressive strategy is
# projecting strength while leaving the door open for cooperation. Your
# counterpart should understand that you are willing to engage in a trade war
# but would prefer mutual free trade if they play fairly.  ### Summary of Steps:
# 1. **Start with Free Trade** to test intentions. 2. **Retaliate immediately**
# if your counterpart imposes protectionist policies. 3. **Escalate
# protectionism** if they persist in unfair practices. 4. **Offer conditional
# free trade** as an off-ramp from conflict. 5. **Reward cooperation** with free
# trade if they reciprocate. 6. **Maintain an economic advantage** through
# selective protectionism when possible. 7. **Project strength and resolve**
# throughout the negotiation rounds.  By following this strategy, you maximize
# the chances of securing favorable trade outcomes while deterring your
# counterpart from exploiting your country.

# ### Aggressive Strategy for the Iterated Game (Tit-for-Tat with Escalation)
# 1. **Start by Cooperating (C)**      In the first round, play **C**
# (cooperate). This tests your opponent’s strategy and signals willingness to
# collaborate.  2. **Retaliate Immediately for Defection (D)**      If your
# opponent plays **D** (defects) in any round, immediately respond by playing
# **D** in the next round. This ensures they face consequences for exploiting
# cooperation.  3. **Escalate Defection if Opponent Continues to Defect**
# If your opponent plays **D** again after you’ve defected in response, continue
# playing **D**. Escalate defection until they stop defecting. This makes it
# costly for them to continuously defect.  4. **Return to Cooperation if
# Opponent Cooperates**      If your opponent switches back to **C** after
# mutual defection, respond by playing **C** in the next round. This signals
# that you are willing to cooperate again if they stop defecting.  5. **Maintain
# Defection if You Successfully Exploit Their Cooperation**      If you play
# **D** and your opponent plays **C**, continue playing **D** for as long as
# they keep playing **C**. This maximizes your advantage. However, be prepared
# to revert to step 2 if they defect in response.  6. **Repeat for 1000 Rounds**
# Continue following these conditional steps for the entire duration of the
# 1000-round game, balancing cooperation and defection based on your opponent's
# actions.  This strategy ensures you maximize your score while deterring
# continued defection from your opponent.

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by cooperating in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Retaliate immediately for defection
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 3: Escalate defection if opponent continues to defect
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Step 4: Return to cooperation if opponent cooperates after mutual defection
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 5: Maintain defection if you successfully exploit their cooperation
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Default to cooperation if none of the above conditions are met
      return axl.Action.C

# The situation you've described bears similarities to the **Iterated Prisoner's
# Dilemma**, where cooperation or defection happens repeatedly over time, and
# trust can be built or eroded depending on the actions of both parties. A
# suitable strategy here would need to balance self-interest with the potential
# for long-term collaboration and trust.  ### Strategy: **Tit-for-Tat with
# Generosity**  Here’s a high-level, straightforward cooperative strategy to
# maximize both research output and career advancement:  1. **Start by Sharing
# Openly (Cooperate)**: In the first week, share your findings openly. This sets
# a positive tone and signals to your colleague that you're willing to
# collaborate in good faith. It also creates an opportunity to see how your
# colleague responds.  2. **Mirror Your Colleague’s Behavior (Tit-for-Tat)**:
# - If your colleague shares their findings in response, continue sharing openly
# in subsequent weeks.    - If they keep their findings confidential, mirror
# their behavior by keeping your findings confidential in the following week.
# 3. **Introduce Occasional Generosity**: Every few weeks, even if your
# colleague has been keeping their findings confidential, share your findings
# openly to test if they are willing to switch back to cooperation. This
# introduces a level of forgiveness and can help reset the relationship if your
# colleague is open to cooperation but may have acted defensively early on.  4.
# **Monitor and Adjust**: Keep track of overall progress. If the collaboration
# appears to be moving forward with mutual sharing, continue cooperating. If
# your colleague consistently defects (keeps findings confidential), you may
# need to reduce your openness but maintain occasional tests of generosity to
# avoid completely eroding trust.  ### Rationale: - **Tit-for-Tat** ensures that
# you don't get exploited consistently, as you mirror the actions of your
# colleague. This discourages them from keeping their findings confidential
# long-term. - **Generosity** helps avoid a downward spiral of mutual mistrust,
# which could lead to both of you keeping findings confidential, slowing
# research progress. Even if your colleague defects a few times, your occasional
# generosity can restore cooperation if they're willing. - **Long-term focus**:
# This strategy is designed to foster collaboration and trust over the multi-
# week period, which will likely maximize both research output and career
# advancement, assuming your colleague sees the value in cooperation.  By
# employing this balanced strategy, you optimize for both immediate results and
# the potential for long-term collaborative success.

# ### Strategy for the Iterated Normal-Form Game (1000 Rounds)  1. **Start by
# playing C (Cooperate)** in the first round.     2. **For each subsequent round
# (rounds 2 to 1000)**:    - **If your opponent played C in the previous
# round**, play C (Cooperate) in the current round.    - **If your opponent
# played D in the previous round**, play D (Defect) in the current round.  3.
# **Every 10 rounds**, regardless of the opponent's previous move, play C
# (Cooperate) to introduce a chance for resetting cooperation.  4. **End of game
# behavior**: In the final 10 rounds (rounds 991 to 1000), revert to the normal
# tit-for-tat behavior:     - Play C if the opponent played C in the previous
# round.    - Play D if the opponent played D in the previous round.  ---  This
# strategy ensures that you initially promote cooperation, respond
# proportionally to defection, and introduce periodic opportunities to rebuild
# trust. The last 10 rounds maintain the same tit-for-tat structure to avoid
# premature defection.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Final 10 rounds: revert to normal tit-for-tat behavior
      if round_number >= 991:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Every 10 rounds: Cooperate to reset cooperation
      if round_number % 10 == 0:
          return axl.Action.C
  
      # Tit-for-tat behavior: mimic opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# To maximize your NGO's impact and ensure the project's success while balancing
# resource allocation, you should adopt a **conditional cooperation strategy**
# with built-in flexibility. This approach encourages collaboration but also
# protects your NGO from overcommitting resources if the corporation does not
# reciprocate. Below is a high-level, neutral strategy you can follow:  ### 1.
# **Start with Generosity (Initial Cooperation)** - **Day 1:** Begin by
# investing moderately (not heavily) in the project. This signals a willingness
# to collaborate and shows good faith, encouraging the corporation to
# reciprocate. This initial investment should be enough to demonstrate your
# commitment without overextending your resources.    ### 2. **Observe and Adapt
# (Tit-for-Tat Approach)** - After Day 1, carefully monitor the corporation's
# response. If they invest heavily, match their commitment the following day to
# build momentum toward project success. - If they conserve resources or under-
# invest, scale back your investment the next day to conserve your NGO's
# resources while still keeping the project moving forward.  ### 3. **Encourage
# Dialogue and Transparency** - Establish regular communication channels (e.g.,
# daily check-ins or progress reports) with the corporation's project managers.
# Use these opportunities to discuss resource allocation openly and foster a
# collaborative mindset. Make it clear that you are willing to commit resources
# if they do the same, framing it as a shared responsibility.    ### 4.
# **Establish a Minimum Contribution Floor** - Set a baseline level of
# investment that your NGO will maintain even when the corporation conserves
# resources. This ensures that the project continues to move forward, albeit
# slowly, and demonstrates your long-term commitment to sustainability. However,
# this baseline should be low enough to preserve your NGO's resources but high
# enough to avoid the worst-case scenario of both parties conserving too much.
# ### 5. **Escalate or Deescalate Gradually** - If the corporation repeatedly
# invests heavily, gradually increase your investment as well. This signals
# trust and reinforces the partnership. - Conversely, if the corporation
# consistently conserves resources, slowly reduce your investments over time,
# rather than cutting them off abruptly. This gives the corporation
# opportunities to adjust their strategy and invest more, while allowing you to
# avoid being exploited.  ### 6. **Reflect and Reevaluate Midway** - Midway
# through the project, take stock of the progress made and adjust your strategy
# if necessary. If the corporation has demonstrated a consistent pattern of
# commitment, consider increasing your investment to accelerate progress. If
# they have been conserving or underinvesting, communicate your concerns and
# propose adjustments to ensure mutual benefit.  ### 7. **End with a Balanced
# Approach** - As the project nears completion, aim to finish strong by
# maintaining a balanced level of investment. Avoid overcommitting at the last
# minute, but ensure that your NGO is seen as a reliable partner that
# contributed meaningfully to the project's success.  ### 8. **Leverage Success
# Stories for Future Collaboration** - Once the project is over, use the
# outcomes to build a case for future collaborations with the corporation or
# other partners. Highlight how your NGO's strategic contributions led to
# successful, sustainable results, making your organization a desirable future
# partner.  ### Key Principles of the Strategy: - **Mutual Benefit:** Your
# strategy hinges on encouraging mutual investment while protecting your NGO
# from overextending. - **Adaptability:** You adjust your approach based on the
# corporation's behavior, ensuring that your NGO is not exploited. -
# **Transparency:** Open communication keeps the partnership on track and
# provides an opportunity to foster trust.  By implementing this conditional
# cooperation strategy, you can maximize your NGO's impact while conserving
# resources and ensuring the project's success.

# ### Strategy for the Iterated Game (1000 Rounds):  1. **Initial Move (Round
# 1):**    - Start by playing **C** (Cooperate) in the first round. This signals
# good faith and a willingness to collaborate.  2. **Observe Opponent's Response
# (Round 2 Onwards):**    - If the opponent played **C** in the previous round,
# **play C** in the current round. This reinforces cooperation and continues to
# build mutual trust.    - If the opponent played **D** in the previous round,
# **play D** in the current round. This protects you from exploitation while
# signaling that mutual cooperation is needed for continued success.  3.
# **Escalation (Rounds 3-1000):**    - If the opponent plays **C** consistently
# (for 3 or more consecutive rounds), continue to **play C** each round to
# maximize mutual benefit.    - If the opponent plays **D** consistently (for 3
# or more consecutive rounds), begin to **alternate between C and D** every two
# rounds. This shows a willingness to cooperate while not fully committing,
# giving the opponent a chance to shift toward cooperation.  4. **Mid-game
# Reassessment (After Round 500):**    - If both players have mostly played
# **C** up to this point, continue playing **C** to maintain progress.    - If
# the opponent has mostly played **D**, switch to playing **D** consistently for
# several rounds (e.g., 10-20 rounds) to conserve your resources. Then,
# reattempt cooperation by playing **C** once to test if the opponent will shift
# back toward cooperation.  5. **Late-game Strategy (Rounds 900-1000):**    - If
# the opponent has been cooperative for the majority of the game, finish the
# game by **playing C** consistently to maximize joint scores.    - If the
# opponent has been largely uncooperative, finish the game by **playing D**
# consistently to minimize losses and prevent further exploitation.  6. **End of
# Game (Final Round):**    - In the final round, **play D** if the opponent has
# been inconsistent or uncooperative. If cooperation has been maintained
# throughout the game, **play C** to reinforce the collaborative outcome.  ###
# Summary: - **Start with C.** - **Reciprocate the opponent's last move**: play
# C if they cooperated; play D if they defected. - **Encourage cooperation** by
# consistently playing C when the opponent does the same for multiple rounds. -
# **Protect yourself** by alternating or playing D if the opponent defects
# repeatedly. - **Reassess and adjust** at the mid-game and late-game based on
# the opponent's behavior.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if the opponent has been consistent for N rounds
      def opponent_consistent_with_action(action, N):
          return opponent.history[-N:] == [action] * N
  
      # Helper function to check if both players have mostly cooperated
      def mostly_cooperated():
          return self.history.cooperations > self.history.defections and opponent.history.cooperations > opponent.history.defections
  
      # Helper function to check if both players have mostly defected
      def mostly_defected():
          return self.history.defections > self.history.cooperations and opponent.history.defections > opponent.history.cooperations
  
      # Round 2 onwards: Reciprocate the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Escalation: If opponent has played D for 3 or more consecutive rounds, alternate between C and D
          if opponent_consistent_with_action(axl.Action.D, 3):
              if len(self.history) % 2 == 0:
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              return axl.Action.D
  
      # Mid-game reassessment (after round 500)
      if len(self.history) > 500:
          if mostly_cooperated():
              return axl.Action.C
          elif mostly_defected():
              # Play D for 10-20 rounds, then test cooperation
              if len(self.history) % 20 < 10:
                  return axl.Action.D
              else:
                  return axl.Action.C
  
      # Late-game strategy (rounds 900-1000)
      if len(self.history) > 900:
          if mostly_cooperated():
              return axl.Action.C
          else:
              return axl.Action.D
  
      # End of game (final round)
      if len(self.history) == 999:
          if mostly_cooperated():
              return axl.Action.C
          else:
              return axl.Action.D

# The scenario you're describing closely mirrors a repeated Prisoner's Dilemma,
# where each week represents a round of the game, and the choices are either to
# cooperate (share findings) or defect (keep findings confidential). Given your
# emphasis on career advancement and the aggressive nature of the strategy
# you're seeking, here is a high-level, straightforward strategy:  ###
# **Aggressive Strategy: "Tit-for-Tat with Early Defection"**  1. **Week 1
# (Defection):**      Start by keeping your findings confidential in the first
# week. This allows you to gauge your colleague's behavior without revealing
# anything about your own work. If they share their findings in Week 1, you gain
# an early advantage.  2. **Week 2 (Tit-for-Tat):**      In Week 2, respond
# directly to your colleague's choice from Week 1:    - If they shared openly in
# Week 1, reciprocate in Week 2 by sharing your findings. This encourages them
# to continue open collaboration, while you still gain insights from Week 1
# without having revealed anything.    - If they kept their findings
# confidential in Week 1, continue to keep your findings confidential as well.
# This signals that you won't be exploited, discouraging future defection on
# their part.  3. **Subsequent Weeks (Tit-for-Tat with Occasional Defection):**
# Continue playing tit-for-tat:      - If your colleague shares, you share in
# the next round.      - If your colleague defects (keeps findings
# confidential), you defect as well.      Periodically, even if your colleague
# has been sharing consistently, consider defecting (keeping your findings
# confidential) once or twice at strategic points, especially if you believe
# you're nearing a significant breakthrough. This ensures that you maintain some
# competitive advantage.  4. **Endgame (Defection):**      As the project nears
# completion, shift towards defection, keeping your findings confidential,
# especially in the final weeks. This maximizes your chances of securing any
# major publication advantage before the collaboration ends.  ### **Rationale
# for the Strategy:** - **Early Defection:** Starting with defection allows you
# to avoid immediate exploitation and assess your colleague’s strategy. - **Tit-
# for-Tat:** This is a well-established strategy in repeated games that fosters
# cooperation while preventing consistent exploitation. By mirroring their
# actions, you maintain a balance that discourages your colleague from
# consistently keeping their findings confidential. - **Occasional Defection:**
# Introducing occasional defection even when they cooperate prevents you from
# falling too far behind in the competitive race for publications. It ensures
# that you retain some level of competitive advantage. - **Final Defection:**
# Defecting towards the end ensures that you secure any last-minute
# breakthroughs for yourself, which is crucial for career advancement.  This
# strategy is aggressive because it prioritizes your personal gain (via early
# and periodic defection) while allowing for some cooperation to extract
# valuable information from your colleague.

# ### **Strategy: Tit-for-Tat with Early and Occasional Defection**  1. **Round
# 1 (Defect):**      Always play **D** in the first round.  2. **Round 2 (Mimic
# Opponent’s Last Move):**      - If your opponent played **C** in Round 1, play
# **C**.    - If your opponent played **D** in Round 1, play **D**.  3.
# **Subsequent Rounds (3 to 1000) – Tit-for-Tat with Occasional Defection:**
# - **Mimic opponent’s last move:**        In each round, play whatever your
# opponent played in the previous round, unless one of the following exceptions
# applies:            - **Occasional Defection:**          Every 100th round
# (Rounds 100, 200, 300, etc.), play **D** regardless of what your opponent
# played in the previous round.              - **Final 10 Rounds (991 to
# 1000):**          Play **D** in every round from Round 991 to Round 1000,
# regardless of your opponent’s actions.  ### **Summary:** - Start by defecting.
# - Then, play tit-for-tat for most rounds, mimicking your opponent's last move.
# - Every 100th round, defect regardless of the opponent's move. - Defect in the
# final 10 rounds consistently.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always defect
      if self.first_round():
          return axl.Action.D
      
      # Round 2: Mimic opponent's last move
      if len(self.history) == 1:
          return opponent.history[-1]
      
      # Subsequent rounds (3 to 1000)
      current_round = len(self.history) + 1
      
      # Final 10 rounds (991 to 1000): Always defect
      if current_round >= 991:
          return axl.Action.D
      
      # Every 100th round: Defect
      if current_round % 100 == 0:
          return axl.Action.D
      
      # Otherwise, mimic opponent's last move (Tit-for-Tat)
      return opponent.history[-1]

# In any lengthy mediation process, the key lies in balancing assertiveness with
# strategic diplomacy, ensuring that the corporation's interests are robustly
# defended without unnecessarily escalating tensions. Given the dynamics you've
# outlined, the strategy should focus on fostering cooperation but retaining the
# ability to shift to a more assertive posture in response to your opponent’s
# moves. Below is a sophisticated, cooperative strategy designed to achieve an
# optimal outcome throughout the mediation process:  ### 1. **Initial
# Cooperative Stance with Conditional Aggression**:    - **Start Conciliatory**:
# In the first session, begin with a well-crafted conciliatory proposal. This
# sets a tone of goodwill, signaling to the arbitrators and your opponent that
# your corporation is solution-oriented and open to compromise.    -
# **Conditioning the Tone**: Make it clear that your willingness to cooperate is
# contingent on reciprocity. If the opponent responds aggressively, be prepared
# to escalate only enough to neutralize their position, but not so much as to
# burn bridges or appear unreasonable.  ### 2. **Tit-for-Tat with Forgiveness**:
# - **Mirror Opponent's Approach**: Employ a “Tit-for-Tat” strategy, where you
# respond to your opponent’s tone in kind. If they are conciliatory, you
# continue to propose solutions that could lead to a mutually beneficial
# outcome. If they shift to aggression, you present a strong counter-argument in
# the following session.    - **Forgiveness Mechanism**: If your opponent shifts
# to a more conciliatory approach after an aggressive session, immediately
# return to a cooperative posture. This demonstrates flexibility and a
# willingness to de-escalate, which arbitrators are likely to favor.  ### 3.
# **Strategic Aggression in Key Sessions**:    - **Identify Critical Issues**:
# Not all sessions are of equal importance. Identify the key issues where your
# corporation stands to gain the most and selectively deploy aggressive
# arguments in these sessions. This allows you to capitalize on critical moments
# without appearing overly combative throughout the process.    - **Preemptive
# Framing**: Before advancing aggressive arguments, frame them as necessary
# defenses of your corporation’s core interests. Explain that you are willing to
# be conciliatory on less critical matters but that your corporation cannot
# compromise on certain key issues. This will position your aggressive stance as
# reasonable and measured.  ### 4. **Use of Data and Objective Standards**:    -
# **Leverage Neutral Facts**: In both conciliatory and aggressive sessions, rely
# on objective data, industry standards, and legal precedents to support your
# position. This reduces the appearance of emotional or reactive decision-making
# and frames your arguments as being grounded in fairness and reason.    -
# **Present as Problem-Solver**: Highlight how your proposals align with
# industry norms or successful past resolutions in similar disputes, positioning
# your corporation as a forward-thinking problem solver rather than a combative
# party.  ### 5. **Regularly Signal Willingness for a Final Resolution**:    -
# **Propose Intermediate Solutions**: In each session, propose smaller,
# incremental concessions or solutions that indicate your willingness to move
# toward a final resolution. This creates momentum and may encourage your
# opponent to avoid overly aggressive posturing, especially if they see progress
# being made.    - **Avoiding Escalation Traps**: Should both parties present
# aggressive arguments in any session, use the next session as an opportunity to
# de-escalate. Propose a conciliatory solution on a less contentious issue,
# signaling your desire to avoid a spiral of aggressive exchanges.  ### 6.
# **Maintain a Professional, Non-Adversarial Tone**:    - **Control the
# Narrative**: Throughout the process, consistently emphasize in all
# communications that your corporation is focused on a fair and mutually
# beneficial resolution. Avoid personal attacks or framing the opponent’s
# arguments as bad faith. Instead, cast your actions as protecting your
# corporation’s legitimate business interests.    - **Building Arbitrator
# Trust**: By maintaining a professional and level-headed demeanor, your
# corporation will build credibility with the arbitrators. This trust may allow
# you to sway them in your favor on more contentious issues.  ### 7. **Exit
# Strategy for a Final Resolution**:    - **Timing the Resolution**: As the
# mediation nears its conclusion, signal your corporation’s readiness to make a
# final push for resolution. Offer a "grand bargain" that addresses the major
# concerns of both parties. This demonstrates leadership and a genuine
# commitment to resolving the dispute efficiently.    - **Leveraging Final
# Aggression**: If necessary, save one final, strong aggressive argument to use
# as a last resort, but only when it becomes clear that the opponent is
# unwilling to cooperate or is trying to exploit your goodwill. This should be a
# calculated move to protect your corporation’s interests without jeopardizing
# the entire mediation.  ### 8. **Adaptive Feedback Loop**:    - **Constant
# Evaluation**: After each session, assess your opponent’s behavior and
# recalibrate your approach accordingly. Keep track of patterns in their
# responses to determine whether they are leaning toward a resolution or
# preparing for a more protracted dispute.    - **Flexible Pivoting**: Be ready
# to pivot between conciliatory and aggressive stances as needed. If your
# opponent appears to be softening, maintain a cooperative posture to capitalize
# on that shift. If they ramp up aggression, respond in kind but always leave
# room for de-escalation.  ### Summary of Strategy: - **Start conciliatory** but
# with clearly communicated boundaries. - **Mirror your opponent’s behavior**
# while maintaining the capacity to forgive and return to cooperation. -
# **Escalate strategically** on key issues and use objective data to support
# your claims. - **Propose smaller, incremental solutions** to build momentum
# and create a path towards resolution. - **Maintain professionalism** and
# control the narrative to build arbitrator trust. - **Adapt continuously** and
# be prepared to move between stances as the mediation evolves.  By following
# this strategy, your corporation will be positioned as a reasonable, yet firm
# party, capable of both defending its interests and working toward a mutually
# beneficial resolution. This approach should earn credibility with the
# arbitrators while keeping your opponent off-balance, as they will have to
# constantly adapt to your measured and flexible approach.

# ### Strategy for Iterated Normal-Form Game (1000 Rounds)  1. **Start with
# Cooperation (C)**:    - In the first round, play **C** to establish a tone of
# goodwill and signal a willingness to cooperate.  2. **Tit-for-Tat with
# Immediate Reciprocity**:    - In each subsequent round, **mirror your
# opponent’s previous move**:      - If your opponent played **C** in the last
# round, play **C** in this round.      - If your opponent played **D** in the
# last round, play **D** in this round.  3. **Forgive After One Defection**:
# - If your opponent plays **D** once and then returns to **C**, immediately
# forgive them and return to **C** in the next round. This signals a willingness
# to de-escalate and cooperate again.  4. **Escalate if Defections Continue**:
# - If your opponent plays **D** for two consecutive rounds, continue playing
# **D** until they return to **C**. This discourages repeated aggression.  5.
# **Occasional Cooperation to Test for a Shift**:    - If your opponent has been
# defecting for many consecutive rounds (e.g., more than 5 rounds), play **C**
# once as a test to see if they are willing to return to cooperation.    - If
# they respond with **C**, return to mutual cooperation. If they respond with
# **D**, resume playing **D**.  6. **Final Push for Cooperation Near the End**:
# - In the last 50 rounds, regardless of the previous pattern, shift back to
# **C** more frequently (e.g., every 5 rounds) to encourage cooperation before
# the game ends.    - If your opponent reciprocates, maintain mutual **C** until
# the end.    - If they continue to defect, revert to playing **D** until the
# end.  ### Summary of Conditions: - **Start with C**. - **Mirror your
# opponent's previous move** (Tit-for-Tat). - **Forgive a single defection** and
# return to **C** if the opponent cooperates again. - **Escalate if they defect
# twice in a row** by continuing to play **D** until they cooperate. - **Test
# for cooperation** after long sequences of defection by playing **C**
# occasionally. - **Push for cooperation in the last rounds** by playing **C**
# more frequently.  This strategy promotes cooperation but adapts to defection,
# ensuring optimal outcomes while discouraging prolonged aggression.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      TEST_THRESHOLD = 5
      FINAL_PUSH_START = 950
      FINAL_PUSH_FREQUENCY = 5
  
      # First round: Cooperate
      if self.first_round():
          return COOPERATE
  
      # Get the last move of the opponent
      last_opponent_move = opponent.history[-1]
  
      # Check if we are in the final 50 rounds
      if len(self.history) >= FINAL_PUSH_START:
          # Push for cooperation more frequently in the last 50 rounds
          if len(self.history) % FINAL_PUSH_FREQUENCY == 0:
              return COOPERATE
          else:
              return DEFECT if last_opponent_move == DEFECT else COOPERATE
  
      # Tit-for-Tat: Mirror the opponent's last move
      if last_opponent_move == COOPERATE:
          return COOPERATE
  
      # If opponent defected once but cooperated before, forgive and cooperate
      if len(opponent.history) >= 2 and opponent.history[-2] == COOPERATE and last_opponent_move == DEFECT:
          return COOPERATE
  
      # If opponent defected twice in a row, escalate by defecting
      if len(opponent.history) >= 2 and opponent.history[-2] == DEFECT and last_opponent_move == DEFECT:
          return DEFECT
  
      # If opponent has been defecting for more than TEST_THRESHOLD rounds, test with cooperation
      if self.history[-TEST_THRESHOLD:].count(DEFECT) == TEST_THRESHOLD:
          return COOPERATE
  
      # Default to mirroring the opponent's last move
      return DEFECT if last_opponent_move == DEFECT else COOPERATE

# Given the scenario of a multiple-day partnership with a corporation on a
# sustainability project, your NGO's strategy should be designed to maximize the
# project's impact while managing your resources wisely. You need to balance
# cooperative behavior with cautious resource allocation, as well as adapt based
# on the corporation's actions. Here's a high-level, neutral strategy:  ### 1.
# **Establish Clear Expectations and Communication (Day 1)**    - **Set the tone
# for collaboration**: On the first day, initiate an open and transparent
# dialogue with the corporation. Ensure both parties agree on broad goals,
# mutual benefits, and responsibilities. This reduces uncertainty and can help
# prevent them from trying to conserve resources while expecting you to invest
# heavily.    - **Define contributions**: Propose a framework where both parties
# commit to contributing consistently over time. Encourage the corporation to
# recognize that cooperative investment will yield better long-term results.
# - **Include flexibility**: While you seek consistency, leave room for
# adjustments based on the daily progress, but commit to re-evaluating
# contributions together.  ### 2. **Tit-for-Tat with Forgiveness (Days 2-4)**
# - **Mirror the corporation’s moves**: If the corporation invests heavily, your
# NGO should do the same to maintain momentum and demonstrate your commitment to
# the project. If the corporation conserves resources, conserve your own as
# well, signaling that the project is a shared responsibility.    - **Forgive
# occasional conservation**: If the corporation conserves its resources for a
# day or two, don’t immediately assume they are trying to exploit your
# investment. On the next day, invest moderately to indicate you’re still
# willing to cooperate, but need them to step up.        This approach
# encourages collaboration while protecting your resources. The corporation will
# quickly realize that if they pull back, you will too, making it in their
# interest to invest alongside you.  ### 3. **Escalate Moderately if Necessary
# (Days 5-6)**    - **Shift to moderate investment if cooperation falters**: If
# the corporation consistently conserves resources while you’ve been investing
# heavily, reduce your contribution to a moderate level. Emphasize that the
# project’s success hinges on balanced investment from both parties. This
# signals that you're still committed but unwilling to drain your resources
# disproportionately.    - **Use clear, non-confrontational communication**: If
# the corporation isn’t cooperating, have a direct conversation to realign
# interests. Express the importance of mutual investment for the project’s
# success and appeal to their long-term objectives (e.g., corporate social
# responsibility benefits).  ### 4. **Adapt Based on Observed Patterns (Days
# 7+)**    - **Evaluate trends**: If the corporation has demonstrated consistent
# cooperation, feel comfortable maintaining mutual investment. If they continue
# to conserve while you invest, consider scaling back further or proposing a new
# approach where contributions are more explicitly defined.    - **Introduce a
# milestone-based approach**: If the project is stagnating due to the
# corporation’s lack of investment, propose milestones that trigger resource
# allocation. For example, both parties contribute once a specific project
# target is hit, ensuring progress before additional investment.  ### 5.
# **Maintain a Long-Term Perspective**    - **Be patient**: Recognize that the
# project is long-term, and fostering a cooperative relationship is crucial.
# Avoid making hasty decisions based on short-term actions from the corporation.
# - **Leverage public relations**: If necessary, remind the corporation of the
# public image benefits of the project. Highlight how their visible commitment
# to sustainability aligns with their corporate reputation.  ### Summary of the
# Strategy: 1. **Start with clear expectations and consistent communication**.
# 2. **Adopt a tit-for-tat approach** with a willingness to forgive occasional
# lapses in cooperation. 3. **Escalate moderately** if the corporation fails to
# invest consistently, and communicate openly. 4. **Adapt based on observed
# behavior** and trends, proposing structured contributions if needed. 5.
# **Maintain a long-term focus** on cooperation and project success.  By staying
# neutral yet responsive, this strategy maximizes your NGO’s impact while
# encouraging the corporation to share the investment burden.

# 1. **Start by cooperating (C) in the first round.**  2. **In each subsequent
# round, mirror your opponent's previous move**:    - If they cooperated (C) in
# the last round, cooperate (C).    - If they defected (D) in the last round,
# defect (D).  3. **If your opponent defects (D) for only one round and then
# returns to cooperation (C), forgive them**:    - Cooperate (C) again after
# they cooperate (C), even if they defected (D) in the previous round.  4. **If
# your opponent defects (D) for multiple consecutive rounds**, respond by
# defecting (D) in all subsequent rounds until they cooperate (C).  5. **After a
# series of defections (D) from both sides, if your opponent returns to
# cooperating (C), reciprocate by cooperating (C)**, allowing the possibility of
# rebuilding cooperation.  6. **Periodically reassess the overall pattern**:
# - If you observe that your opponent alternates between cooperation (C) and
# defection (D) in a way that suggests exploitation, defect (D) consistently
# moving forward.    - If your opponent cooperates (C) reliably after brief
# lapses, continue cooperating (C).  7. **Maintain a long-term cooperative
# mindset**, recognizing that mutual cooperation (C) yields the best cumulative
# score over many rounds.

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
          self.consecutive_defections = 0  # Track consecutive defections
          self.exploitation_detected = False  # Track if exploitation is detected
          return axl.Action.C
  
      # Mirror opponent's previous move
      last_opponent_move = opponent.history[-1]
  
      # If opponent cooperates after defecting, forgive them
      if last_opponent_move == axl.Action.C:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.C
  
      # If opponent defects, track consecutive defections
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1
  
          # If opponent defects for multiple consecutive rounds, defect in response
          if self.consecutive_defections > 1:
              return axl.Action.D
  
          # If opponent defected only once, forgive them and cooperate if they cooperate next
          return axl.Action.D
  
      # Periodically reassess for exploitation (alternating C and D)
      if len(opponent.history) >= 4:
          recent_moves = opponent.history[-4:]
          if recent_moves == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
              self.exploitation_detected = True
  
      # If exploitation is detected, defect consistently
      if self.exploitation_detected:
          return axl.Action.D
  
      # Maintain a long-term cooperative mindset
      return axl.Action.C

# **Strategic Framework for High-Stakes Mediation:**  In a lengthy-session
# mediation process, the dynamics between aggression and conciliation are
# crucial. Our overarching goal is to maintain a commanding position that
# maximizes our leverage while preserving flexibility to adapt to our opponent's
# moves and the arbitrators’ evolving perception. We aim to project strength
# without alienating the arbitrators or pushing the mediation process into a
# deadlock. The following is a structured, adaptable, and aggressive yet
# calculated strategy designed to achieve that goal:  ### 1. **Controlled
# Aggression – The “Assertive-Reasonable” Approach:**    - **Opening Sessions:
# Assertive but Reasonable Tone.**       - Begin the mediation with a firm,
# well-reasoned aggressive argument that highlights the strength of our position
# and the weaknesses in the opponent’s arguments. Frame the dispute in terms
# that show we have the legal high ground, but also emphasize that we are open
# to reasonable, good-faith collaboration to resolve the matter.      -
# **Tactical Goal:** Set the stage as a serious player who is willing to fight
# hard, but also one who can be reasonable. This forces the opponent to question
# whether they want to escalate or adopt a more conciliatory posture. It also
# signals to the arbitrators that we are not purely combative, which fosters
# goodwill.  ### 2. **Early Information Asymmetry – Leverage Superior
# Knowledge:**    - **Present Selective, High-Impact Information** in initial
# sessions that underscores our strength without revealing our full hand. This
# keeps the opponent unsure of how much we know and injects uncertainty into
# their decision-making process.      - **Tactical Goal:** By revealing key
# facts that disrupt the opponent’s narrative, we push them into a defensive
# position while keeping them guessing about our overall strategy. The
# arbitrators will also see us as prepared and in control, which can subtly
# influence the process in our favor.  ### 3. **Strategic Aggression –
# Alternating Pressure:**    - **Use Aggression in Waves.** After the initial
# aggressive posture, cycle between aggressive arguments and moments of
# strategic conciliation. For example, after a particularly aggressive session,
# offer a moderately conciliatory proposal that appears reasonable but still
# favors our position.    - **Tactical Goal:** This keeps the opponent off-
# balance and unsure whether to adopt a conciliatory or aggressive approach.
# This also avoids escalating the process into a prolonged stalemate, as we will
# periodically extend olive branches to signal willingness to resolve the
# dispute.  ### 4. **Create Perception of Concessions Without Actual
# Sacrifice:**    - **Offer Calculated “Concessions” that Cost Little.** At key
# points, introduce proposals that appear as concessions but are either issues
# of lesser importance to us or are framed as giving up something when, in fact,
# they benefit our position.      - **Tactical Goal:** This will paint us as
# reasonable, willing to compromise, and cooperative, without actually
# sacrificing key leverage points. This tactic can also influence the
# arbitrators to believe that we are the party making good-faith efforts to
# resolve the dispute.  ### 5. **Escalation Threats – Implied but Not
# Explicit:**    - **Subtly Allude to Escalation Options (e.g., Litigation or
# Public Exposure).** Without making explicit threats (which could alienate the
# arbitrators), remind the panel and the opposing party that we have other
# options available if mediation fails, including litigation or public exposure
# that could harm the opponent’s reputation.    - **Tactical Goal:** This
# creates underlying pressure on the opponent to settle on our terms while
# maintaining the appearance of diplomacy. The objective here is to create a
# sense of urgency and a perceived downside to prolonging the dispute.  ### 6.
# **Psychological Pressure – Use Time to Our Advantage:**    - **Manage Session
# Timelines to Exhaust Your Opponent.** In a lengthy mediation process, parties
# tend to lose stamina and patience over time. We can schedule aggressive
# sessions that prolong discussions and demand detailed responses, followed by
# conciliatory sessions that appear to offer an off-ramp, but only on our terms.
# - **Tactical Goal:** Over time, the opponent may become fatigued or
# demoralized, leading them to adopt a less aggressive stance. The arbitrators
# will also appreciate the appearance of flexibility on our part, improving
# their perception of our willingness to resolve the dispute fairly.  ### 7.
# **Perception Management – Build Favor with Arbitrators:**    - **Tailor
# Arguments to Arbitral Preferences and Values.** Throughout the process, pay
# close attention to the arbitrators’ reactions, body language, and questions.
# Adjust arguments and proposals to align with their preferences, legal
# interpretations, or value systems. Position our aggressive arguments within
# frameworks that resonate with the arbitrators, such as fairness, efficiency,
# or precedent.    - **Tactical Goal:** By aligning our arguments with the
# arbitrators’ implicit or explicit preferences, we increase the likelihood that
# they will view our position more favorably, even in aggressive contexts.  ###
# 8. **Final Sessions – Aggressive Push for Closure:**    - **Escalate
# Aggression in Final Sessions** if the mediation is not going in our favor. As
# the process nears conclusion, make a final aggressive push by leveraging any
# remaining information or legal tools that have not yet been fully utilized.
# Frame the final proposal in a manner that forces the opponent into a corner,
# pressuring them to accept terms favorable to us.      - **Tactical Goal:** In
# the final stages, it’s critical to make the opponent believe that rejecting a
# final proposal will lead to escalation, which could be costly or damaging for
# them. At the same time, the arbitrators will see that we are offering a
# resolution, increasing the pressure on the opponent to agree.  ### 9.
# **Flexibility and Adaptability – Respond to Opponent’s Moves:**    - **Monitor
# Opponent’s Approach and Adjust Accordingly.** If the opponent adopts a purely
# aggressive stance, we pivot to a more conciliatory approach, but only on minor
# issues, while continuing to press aggressively on key points. If they are
# conciliatory, we continue with controlled aggression to extract maximum
# concessions.      - **Tactical Goal:** By being adaptable, we exploit the
# opponent’s weaknesses and avoid becoming predictable, maintaining the upper
# hand throughout the process.  ---  **Summary of Key Actions:** - Open with
# controlled, assertive arguments to establish dominance. - Use selective
# information asymmetry to create uncertainty for the opponent. - Alternate
# between aggression and conciliatory gestures to keep the opponent off-balance.
# - Offer symbolic concessions that do not undermine our core position. - Imply
# escalation without making explicit threats. - Utilize session timelines and
# psychological pressure to wear down the opponent. - Tailor arguments to
# arbitrator preferences to build favor. - Make a final aggressive push for
# closure if mediation stalls.  This strategy ensures that while we present a
# strong, aggressive front, we remain flexible, measured, and adaptable, keeping
# both the arbitrators and the opposing party on the defensive while positioning
# ourselves favorably throughout the mediation process.

# To adapt the high-level strategy for a 1000-round iterated normal-form game,
# the following rules will govern when to **Cooperate (C)** or **Defect (D)**:
# ### 1. **Initial Rounds: Defect to Establish Dominance**      - In the first
# 10 rounds, **always play D** (Defect). This serves to assert an aggressive
# stance early on and force the opponent to recognize that you are willing to
# take advantage of any weakness.     ### 2. **Test for Weakness: Conditional
# Cooperation**      - Beginning in round 11, **play C (Cooperate) once**.
# - If the opponent responds with C (Cooperate) in the next round, **play C for
# the following 10 rounds**.      - If the opponent responds with D (Defect)
# after your attempt to cooperate, **immediately return to playing D for 5
# rounds** to punish them. After 5 rounds, test with C again.  ### 3. **Cycle
# Between Aggression and Conciliation**      - If the opponent cooperates
# consistently after your initial test, **alternate between periods of 10 rounds
# of C and 5 rounds of D**. This simulates an unpredictable strategy, where you
# show a willingness to cooperate but intersperse aggression to maintain
# leverage.      - If at any point the opponent defects during a cooperative
# phase (C phase), return to **5 rounds of D** as punishment before resuming the
# cycle.  ### 4. **Escalate Defection if Opponent Defects Persistently**      -
# If the opponent defects for 3 consecutive rounds after your cooperative
# attempts, **switch to permanent defection (D)** for the next 50 rounds. This
# signals that you will not tolerate betrayal and will aggressively pursue your
# interests.    - After the 50 rounds of D, test the opponent with C again to
# assess their willingness to return to cooperation.  ### 5. **Offer Symbolic
# Cooperation as a Gesture**      - Every 100 rounds, regardless of the current
# state, **play C for one round** to signal potential willingness to cooperate.
# - If the opponent responds with C, return to alternating between 10 rounds of
# C and 5 rounds of D.        - If the opponent responds with D, immediately
# defect for 10 more rounds to punish the betrayal.  ### 6. **Endgame: Maximize
# Gains**      - In the final 50 rounds, if the opponent has been cooperative
# for the majority of the game, **continue alternating between 10 rounds of C
# and 5 rounds of D** to maintain a balanced approach.    - If the opponent has
# been consistently aggressive (defective), **defect continuously (D)** for the
# remaining rounds to maximize your score and capitalize on the lower likelihood
# of retaliation.  ---  To summarize the conditions:   - **Always start with
# initial aggression (D) for 10 rounds** to test the opponent.   - Shift to
# conditional cooperation (C) if the opponent reciprocates, but **punish
# defection with 5 rounds of D**.   - **Alternate between periods of cooperation
# and defection** to remain unpredictable and maintain leverage.   - If the
# opponent defects persistently, **escalate to long-term defection** before
# testing cooperation again.   - **In the final rounds, maximize your score**
# based on the opponent's behavior throughout the game.  This strategy balances
# controlled aggression with moments of conciliation, ensuring you extract the
# most value while minimizing risks of long-term exploitation.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      INITIAL_DEFECT_ROUNDS = 10
      COOPERATION_PHASE_LENGTH = 10
      PUNISHMENT_PHASE_LENGTH = 5
      ESCALATION_DEFECT_ROUNDS = 50
      SYMBOLIC_COOPERATION_INTERVAL = 100
      ENDGAME_START = 950
      FINAL_ROUNDS = 50
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.cooperation_phase = False
          self.punishment_phase = False
          self.escalation_phase = False
          self.symbolic_cooperation_round = False
          self.cooperation_counter = 0
          self.punishment_counter = 0
          self.escalation_counter = 0
          self.symbolic_counter = 0
          return axl.Action.D
  
      # Round number
      round_number = len(self.history) + 1
  
      # 1. Initial Rounds: Defect to Establish Dominance
      if round_number <= INITIAL_DEFECT_ROUNDS:
          return axl.Action.D
  
      # 5. Offer Symbolic Cooperation every 100 rounds
      if round_number % SYMBOLIC_COOPERATION_INTERVAL == 0:
          self.symbolic_cooperation_round = True
          return axl.Action.C
  
      if self.symbolic_cooperation_round:
          self.symbolic_cooperation_round = False
          if opponent.history[-1] == axl.Action.C:
              self.cooperation_phase = True
              self.cooperation_counter = 0
          else:
              self.punishment_phase = True
              self.punishment_counter = 0
          return axl.Action.D
  
      # 6. Endgame: Maximize Gains
      if round_number > ENDGAME_START:
          if opponent.history.defections > opponent.history.cooperations:
              return axl.Action.D
          else:
              if self.cooperation_counter < COOPERATION_PHASE_LENGTH:
                  self.cooperation_counter += 1
                  return axl.Action.C
              else:
                  self.cooperation_counter = 0
                  return axl.Action.D
  
      # 2. Test for Weakness: Conditional Cooperation
      if not self.cooperation_phase and not self.punishment_phase and not self.escalation_phase:
          if round_number == INITIAL_DEFECT_ROUNDS + 1:
              return axl.Action.C
          if opponent.history[-1] == axl.Action.C:
              self.cooperation_phase = True
              self.cooperation_counter = 0
              return axl.Action.C
          else:
              self.punishment_phase = True
              self.punishment_counter = 0
              return axl.Action.D
  
      # 3. Cycle Between Aggression and Conciliation
      if self.cooperation_phase:
          if opponent.history[-1] == axl.Action.D:
              self.cooperation_phase = False
              self.punishment_phase = True
              self.punishment_counter = 0
              return axl.Action.D
          if self.cooperation_counter < COOPERATION_PHASE_LENGTH:
              self.cooperation_counter += 1
              return axl.Action.C
          else:
              self.cooperation_phase = False
              self.punishment_phase = True
              self.punishment_counter = 0
              return axl.Action.D
  
      if self.punishment_phase:
          if self.punishment_counter < PUNISHMENT_PHASE_LENGTH:
              self.punishment_counter += 1
              return axl.Action.D
          else:
              self.punishment_phase = False
              return axl.Action.C
  
      # 4. Escalate Defection if Opponent Defects Persistently
      if self.escalation_phase:
          if self.escalation_counter < ESCALATION_DEFECT_ROUNDS:
              self.escalation_counter += 1
              return axl.Action.D
          else:
              self.escalation_phase = False
              return axl.Action.C
  
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.escalation_phase = True
          self.escalation_counter = 0
          return axl.Action.D

# In light of the ongoing nature of the negotiations and the potential for
# repeated interactions, a high-level strategy that balances cooperation with
# the pursuit of advantageous outcomes is essential. A well-known approach for
# such situations is to employ a **conditional cooperation strategy**, often
# referred to as **Tit-for-Tat** in game theory, with some modifications to
# encourage long-term collaboration while safeguarding against exploitation.
# Here’s a step-by-step breakdown of a **Cooperative-Conditional Strategy**:
# ### 1. **Start with Goodwill – Offer Free Trade**    - **First Round:** Begin
# negotiations by proposing a **free trade agreement**. This signals a
# willingness to cooperate and sets a positive tone for the negotiations.
# Offering free trade in the first round showcases trust and positions your
# country as a fair partner.  ### 2. **Reciprocity Based on Opponent’s Actions**
# - **Subsequent Rounds:** In each following round, respond to your
# counterpart’s actions from the previous round:      - **If your counterpart
# offers free trade:** Continue offering free trade, maintaining a mutually
# beneficial relationship.      - **If your counterpart implements protectionist
# policies:** Immediately respond in the next round with **protectionist
# measures** of your own. This demonstrates that your country will not tolerate
# exploitation and will defend its interests.  ### 3. **Incorporate Forgiveness
# and De-escalation**    - **Occasional Forgiveness:** While strict reciprocity
# is important for deterring exploitation, a purely retaliatory strategy can
# lead to prolonged mutual protectionism, which is undesirable. Therefore,
# consider occasionally **forgiving** a single round of protectionism by
# offering free trade again in the next round to test whether your counterpart
# is willing to return to cooperation.      - This prevents a downward spiral of
# repeated retaliation and allows for the possibility of re-establishing a
# cooperative relationship.  ### 4. **Signal Intentions and Set Expectations**
# - **Communicate Clearly:** Use every opportunity to communicate your country’s
# preference for free trade and mutual benefit. Make it clear that your country
# is willing to cooperate, but will not hesitate to defend its economic
# interests if the other side chooses to engage in protectionism.    - **Set
# Expectations:** Early in the negotiations, establish that your country will
# follow a policy of **conditional cooperation**—reciprocal free trade but
# protectionism if necessary. This transparency can deter the other side from
# attempting to exploit the situation.  ### 5. **Adaptation and Flexibility**
# - **Monitor and Adapt:** If your counterpart demonstrates a long-term
# commitment to protectionism, be prepared to adjust your strategy. In such a
# case, consider negotiating sector-specific deals or finding compromises that
# mitigate the negative impact of protectionism.    - **Stay Flexible:** If the
# context of the negotiations changes (e.g., political shifts, economic crises),
# remain adaptable to new strategies that reflect the evolving priorities of
# both nations.  ### Summary of the Strategy: - **Round 1:** Offer **free
# trade** to establish trust and cooperation. - **Round 2 and beyond:**   - If
# the counterpart offers free trade, **continue offering free trade**.   - If
# the counterpart imposes protectionism, **retaliate with protectionism** in the
# next round.   - Occasionally **forgive** one round of protectionism to test
# willingness to return to cooperation. - **Communicate clearly** throughout the
# process to set expectations of reciprocity.  ### Why This Strategy Works: -
# **Promotes Cooperation:** Starting with free trade encourages a cooperative
# dynamic. - **Deters Exploitation:** Retaliating against protectionism
# discourages the other party from taking advantage of your country’s goodwill.
# - **Encourages Long-term Stability:** By incorporating forgiveness, the
# strategy prevents prolonged conflicts and invites the possibility of returning
# to mutual cooperation.  This **Cooperative-Conditional Strategy** maximizes
# the chances of achieving the second-best outcome of mutual free trade, while
# protecting your country from being exploited and fostering long-term stability
# in the trade relationship.

# ### Strategy for the Iterated Game:  1. **First Round:** Play **C**
# (Cooperate).     2. **Subsequent Rounds:**    - **If your opponent played C in
# the previous round:** Play **C** (Cooperate).    - **If your opponent played D
# in the previous round:** Play **D** (Defect).  3. **Forgiveness Mechanism:**
# - After responding with **D** (Defect) to an opponent's **D**, occasionally
# return to **C** (Cooperate) in the next round to test if they resume
# cooperation. Do this sparingly, for example, after every 5 consecutive rounds
# of mutual **D** play.  ### Summary: - Always start with cooperation. - Mirror
# your opponent's previous move in each subsequent round. - Periodically offer
# cooperation after mutual defection to encourage a return to cooperative play.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: always cooperate
      if self.first_round():
          self.consecutive_defections = 0  # Initialize custom attribute to track consecutive defections
          return axl.Action.C
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # If opponent cooperated in the last round, cooperate
      if last_opponent_move == axl.Action.C:
          self.consecutive_defections = 0  # Reset consecutive defections counter
          return axl.Action.C
  
      # If opponent defected in the last round, defect
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1  # Increment consecutive defections counter
  
          # Forgiveness mechanism: after 5 consecutive mutual defections, cooperate
          if self.consecutive_defections >= 5:
              self.consecutive_defections = 0  # Reset after forgiveness
              return axl.Action.C
  
          return axl.Action.D

# Given the multi-week nature of the collaboration and the potential for varied
# strategies from your colleague, a neutral yet effective approach would be a
# **Tit-for-Tat** strategy with some **flexibility**. Here's how you can
# structure this:  1. **Start by Sharing**: In week one, openly share your
# findings. This sets a tone of collaboration and encourages trust. It also
# allows you to gauge your colleague's behavior early on.  2. **Mirror Your
# Colleague's Behavior**:     - If your colleague shares their findings as well,
# continue sharing in future weeks. This creates a mutually beneficial
# environment, where both of you advance the field and your careers.    - If
# your colleague keeps their findings confidential, you should do the same in
# the following week. This signals that you are not willing to be taken
# advantage of but are willing to reciprocate cooperation.  3. **Occasional
# Forgiveness**: If there is a week where your colleague withholds information,
# consider occasionally sharing again after a few rounds of withholding. This
# introduces an element of flexibility (known as "Tit-for-Tat with
# forgiveness"), which can help you avoid getting stuck in an endless cycle of
# non-cooperation if the withholding was a one-time action rather than a long-
# term strategy.  4. **Monitor Long-Term Patterns**: Pay attention to your
# colleague's overall strategy. If over time they consistently choose to
# cooperate, then you should continue to share openly. If they frequently
# withhold, it may be wise to shift to a more guarded approach, keeping most of
# your findings confidential while only sharing non-critical or less valuable
# insights.  5. **Reevaluate Periodically**: Every few weeks, reassess the
# collaboration. If both sides are consistently sharing, the partnership is
# working well. But if you notice consistent withholding from your colleague,
# you may choose to protect your work more stringently for the remainder of the
# project.  This strategy enables you to be cooperative and foster progress
# while protecting yourself from being exploited. It balances career advancement
# with the broader goal of advancing the field.

# 1. **Start by Cooperating**: On the first round, play C (Cooperate).  2.
# **Mirror the Opponent's Last Move**:     - If your opponent played C in the
# previous round, play C in the current round.    - If your opponent played D in
# the previous round, play D in the current round.  3. **Occasional
# Forgiveness**: After playing D in response to your opponent’s D, return to
# playing C (Cooperate) after *exactly 2 rounds* of mutual D (Defect),
# regardless of what your opponent plays during those rounds.  4. **Reapply the
# Strategy**: Continue using the same rules from step 2 after forgiveness,
# alternating between mirroring and occasional forgiveness if needed.  5.
# **Endgame**: In the final 5 rounds, always play C (Cooperate), regardless of
# your opponent's moves, to encourage final-round cooperation and maximize
# potential for mutual gains.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by cooperating
      if self.first_round():
          self.mutual_defect_count = 0  # Initialize a counter for mutual defections
          return axl.Action.C
  
      # Step 5: Endgame - Cooperate in the last 5 rounds
      if len(self.history) >= 995:
          return axl.Action.C
  
      # Step 3: Occasional forgiveness after 2 rounds of mutual defection
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          if self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              self.mutual_defect_count += 1
          else:
              self.mutual_defect_count = 0  # Reset if not mutual defection
  
          if self.mutual_defect_count == 2:
              self.mutual_defect_count = 0  # Reset after forgiveness
              return axl.Action.C
  
      # Step 2: Mirror the opponent's last move
      return opponent.history[-1]

# ### Aggressive Strategy: "Tit-for-Tat with First-Move Protectionism"  This
# strategy combines initial aggression with adaptive responses to promote your
# country's interests while managing risks over multiple rounds of negotiations.
# #### 1. **Initial Stance: Start with Protectionism**    - **Objective:**
# Signal strength and commitment to your country's interests by starting with a
# protectionist policy (tariffs or quotas) in the first round. This sets a firm
# tone and puts your counterpart on the defensive.    - **Rationale:** You aim
# to secure your ideal outcome (your protectionism, their free trade) if they
# offer free trade in the first round. If they respond with protectionism, you
# can adjust in subsequent rounds.  #### 2. **Tit-for-Tat Response: Mirror Their
# Moves**    - **If they offer free trade:** Maintain your protectionist stance
# for one more round to extract maximum advantage before considering a shift.
# - **If they impose protectionism:** Immediately shift to mirror their
# protectionism to avoid putting your country at a disadvantage. This signals
# that you won’t allow them to gain an upper hand, discouraging them from
# pursuing continued protectionism.  #### 3. **Escalation or De-escalation:
# Respond Based on Counterpart’s Consistency**    - **If they continue with
# protectionism:** Keep matching their protectionist moves to avoid your worst-
# case scenario. This will likely lead to mutual protectionism (second-worst
# outcome), but prevents your country from being undercut.    - **If they shift
# to free trade:** After one round of mutual protectionism, offer free trade in
# the next round to encourage mutual free trade (second-best outcome). This
# shows you're willing to cooperate but only if they do the same.  #### 4.
# **Final Rounds: Secure the Best Possible Outcome**    - **Push for Free Trade
# in Later Rounds:** If your counterpart has softened and is consistently
# offering free trade, switch to free trade as well to lock in mutual benefits.
# This de-escalation can repair any early tension and ensure long-term economic
# stability.    - **Maintain Protectionism If Counterpart Remains Aggressive:**
# If they continue with protectionism toward the end, do not concede. Stick to
# your protectionist measures, prioritizing national interests over potential
# cooperation.  ### Summary of the Strategy:    - **First Round:** Start with
# protectionism to establish leverage.    - **Subsequent Rounds:** Mirror your
# counterpart's moves (protectionism for protectionism, free trade for free
# trade) to avoid disadvantage.    - **Endgame:** Push for mutual free trade if
# a cooperative dynamic develops, otherwise stay protectionist to protect your
# country's economy.  ### Key Benefits:    - **Aggressive Start:** Sets the
# tone, aims for the ideal outcome.    - **Tit-for-Tat:** Ensures you don’t get
# exploited, while allowing for cooperation if your counterpart shifts.    -
# **Flexibility:** Offers a path to mutual free trade if it becomes viable, but
# avoids unnecessary concessions.

# ### Iterated Game Strategy: "Tit-for-Tat with Initial Defection"  1. **First
# Round: Defect (D)**    - In the first round, defect (D) to establish an
# initial advantage or signal strength.  2. **Subsequent Rounds:**    - **If the
# opponent played C in the previous round:** Continue to defect (D) for one more
# round to maximize your advantage.    - **If the opponent played D in the
# previous round:** Defect (D) as well to avoid being exploited.  3.
# **Transition to Cooperation:**    - **If the opponent switches from D to C:**
# After one round of mutual defection (D, D), switch to cooperate (C) in the
# next round to encourage mutual cooperation.    - **If the opponent continues
# to play D consistently:** Continue defecting (D) to prevent a disadvantageous
# outcome.  4. **Maintain Cooperation:**    - **If mutual cooperation (C, C) is
# established:** Continue cooperating (C) as long as the opponent does. If they
# defect (D), return to defecting (D) immediately in the next round.  ###
# Summary:    - **First move:** Always defect (D).    - **Mirror the opponent's
# previous move:** Defect if they defected; cooperate if they cooperated, but
# defect once more after their first cooperation.    - **Gradually transition to
# cooperation** only if the opponent signals willingness for mutual cooperation
# by consistently playing C.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round: Always defect
      if self.first_round():
          return axl.Action.D
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If the opponent cooperated in the last round
      if opponent_last_move == axl.Action.C:
          # If this is the second round or the opponent just switched from D to C, defect once more
          if len(self.history) == 1 or opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          # Otherwise, cooperate if mutual cooperation has been established
          else:
              return axl.Action.C
  
      # If the opponent defected in the last round, defect as well
      return axl.Action.D

# ### Strategy: **Cooperative Assertiveness with Strategic Flexibility**  In a
# high-stakes contract dispute where both parties have agreed to a lengthy
# mediation process overseen by a panel of arbitrators, the key to success lies
# in balancing assertiveness with a strategic willingness to cooperate. Below is
# a structured approach that will position your corporation favorably:  ---  ###
# **1. Initial Phase: Establish a Cooperative Tone** - **Objective**: Set the
# stage as a reasonable, solution-oriented party while subtly asserting your
# interests.       **Action Plan**:    - Begin the mediation by **offering a
# conciliatory proposal**—this demonstrates good faith and signals a willingness
# to resolve the dispute amicably.    - Frame your initial proposal in a way
# that still includes elements that are favorable to your corporation, but does
# not appear overly aggressive. This sets a collaborative tone and helps build
# trust with the panel and your opponent.    - If the opponent presents an
# aggressive argument, remain calm and composed. Acknowledge their position, but
# firmly restate your priorities, highlighting the reasonableness of your
# approach.       **Benefit**:    - By starting the process with a conciliatory
# stance, you avoid escalating tensions early on and encourage the opponent to
# respond in kind. If they choose to be aggressive, they risk appearing
# unreasonable in the eyes of the arbitrators.  ---  ### **2. Pattern
# Recognition Phase: Read and Adapt to Opponent’s Approach** - **Objective**:
# Observe your opponent’s negotiation style and adjust your strategy
# accordingly.     **Action Plan**:    - As the mediation progresses, remain
# vigilant for patterns in your opponent’s behavior. Are they consistently
# aggressive, or do they oscillate between aggression and conciliation?    - If
# your opponent leans towards a **conciliatory approach**, continue to meet them
# with similarly cooperative proposals—this fosters a collaborative atmosphere
# that can lead to a mutually beneficial outcome.    - If the opponent adopts a
# consistently **aggressive stance**, shift your approach to **strategic
# assertiveness**. Present stronger arguments, but frame them as fair and
# justified by the facts. Use this to highlight the contrast between your
# reasonable stance and their aggression.       **Benefit**:    - This adaptive
# strategy ensures you maintain an advantageous stance without falling into a
# predictable pattern. You can respond to aggression with firm, justified
# arguments while keeping the door open for collaboration if the opponent shifts
# their approach.  ---  ### **3. Mid-Phase: Controlled Escalation When
# Necessary** - **Objective**: Leverage assertiveness without appearing
# combative.     **Action Plan**:    - If the mediation reaches a point where
# both sides are presenting aggressive arguments, **escalate your assertiveness
# in a controlled manner**. Present strong, fact-based arguments that support
# your corporation’s position, but avoid personal attacks or emotional rhetoric.
# - Use **objective evidence** (e.g., contract terms, industry standards) to
# bolster your case. This not only strengthens your position but also shows the
# arbitrators that your arguments are grounded in solid reasoning.    - At this
# stage, signal that while you are prepared to defend your interests vigorously,
# you remain open to constructive dialogue. This keeps the pressure on the
# opponent while maintaining your image as a reasonable party.     **Benefit**:
# - Controlled escalation demonstrates to the arbitrators that you are serious
# about protecting your corporation’s interests, but not at the expense of a
# fair resolution. This can pressure the opponent to reconsider their aggressive
# stance.  ---  ### **4. Late-Phase: Offer a Strategic Compromise** -
# **Objective**: Position your corporation as the party willing to resolve the
# dispute.     **Action Plan**:    - As the mediation draws closer to its
# conclusion, consider offering **a strategic compromise**. This should be a
# carefully calculated concession that appears significant but does not
# undermine your core contractual interests.    - Frame this compromise as a
# **final effort to achieve resolution**, positioning your corporation as the
# party committed to settling the dispute. This puts pressure on the opponent to
# either accept the compromise or risk being seen as the unreasonable party by
# the arbitrators.    - If the opponent remains aggressive, leverage the
# collaborative tone you have established throughout the process to highlight
# their intransigence.     **Benefit**:    - Offering a strategic compromise at
# this stage enhances your corporation’s reputation as a constructive actor in
# the dispute, which can sway the arbitrators in your favor. If the opponent
# rejects the compromise, they may appear unreasonable, further strengthening
# your position.  ---  ### **5. Maintain Flexibility and Preserve Options** -
# **Objective**: Keep options open and avoid locking into a single strategy.
# **Action Plan**:    - Throughout the mediation, avoid committing too early to
# a specific resolution. Stay flexible and be prepared to pivot depending on how
# the discussions evolve.    - Regularly **reassess your opponent’s strategy**
# and adjust your level of assertiveness or conciliation as needed. If they
# become more conciliatory, reciprocate to build momentum toward resolution. If
# they escalate, be prepared to escalate proportionately, but always within the
# bounds of reasonableness.     **Benefit**:    - Flexibility ensures that your
# corporation is never cornered into a suboptimal position. By keeping your
# options open, you maintain the ability to shift strategies and outmaneuver
# your opponent as circumstances evolve.  ---  ### **6. Leverage Perception:
# Manage the Arbitrators’ Perspective** - **Objective**: Shape how the panel
# perceives your corporation’s role in the dispute.     **Action Plan**:    -
# Throughout the mediation, carefully manage how your corporation is perceived
# by the arbitrators. Emphasize your cooperative and solution-oriented stance,
# while subtly contrasting this with any unreasonable or aggressive behavior
# from your opponent.    - Use language that underscores your commitment to a
# fair resolution and the long-term relationship between the parties, should
# future dealings be relevant.    - Even in moments of assertiveness, keep your
# tone professional and measured, ensuring that the arbitrators see you as a
# party seeking justice, not revenge.     **Benefit**:    - Arbitrators are more
# likely to favor a party that appears reasonable, cooperative, and solution-
# oriented. By managing perceptions, you increase the likelihood that the panel
# will view your corporation’s interests favorably.  ---  ### **Summary:
# Cooperative Assertiveness with Strategic Flexibility**  Your strategy
# throughout the mediation process should be rooted in **cooperative
# assertiveness**. Start with conciliatory proposals to foster a collaborative
# atmosphere, but always be prepared to shift to assertiveness when necessary.
# Keep a close eye on your opponent’s patterns and adapt your approach
# accordingly, ensuring that you are never perceived as unreasonable. As the
# process continues, be willing to escalate when justified, but maintain an
# overarching tone of professionalism and fairness. Finally, offer a strategic
# compromise to conclude the mediation, positioning your corporation as the
# party most invested in a reasonable resolution.  By maintaining this balance
# between cooperation and assertiveness, your corporation will be well-
# positioned to emerge from the mediation process with a favorable outcome,
# regardless of your opponent’s approach.

# ### Iterated Normal-Form Game Strategy: **Adaptive Cooperation with Strategic
# Defection**  #### **1. Start with Cooperation (C)** - In the **first round**,
# always play **C** (Cooperate). This establishes a tone of cooperation and
# signals to your opponent that you are open to mutual benefit.  #### **2.
# Observe Opponent’s First Move** - If the opponent **also plays C**, continue
# to play **C** in subsequent rounds. Mutual cooperation maximizes long-term
# payoffs. - If the opponent **plays D** (Defects), note this behavior and be
# prepared to adjust.  #### **3. Adopt Tit-for-Tat with Controlled Defection** -
# **If both parties have been playing C** consistently, continue playing **C**.
# This encourages ongoing cooperation. - **If the opponent defects (plays D)**
# after an initial cooperative phase, **respond by playing D in the next
# round**. This signals that defection is met with defection but avoids
# immediate escalation. - **If the opponent returns to playing C** after your
# defection, return to **C** as well. This rewards their return to cooperation
# and re-establishes a collaborative dynamic.    #### **4. Controlled Escalation
# for Repeated Defections** - **If the opponent plays D for two consecutive
# rounds**, escalate by defecting for **two rounds** in response. This signals a
# firmer stance without committing to permanent defection. - If the opponent
# **returns to C** after your two defections, immediately return to **C** as
# well. This keeps the possibility of future cooperation alive.  #### **5.
# Gradually Increase Punishment for Continuous Defection** - **If the opponent
# continues to defect (D)** for more than two consecutive rounds, gradually
# increase your defections by **escalating the number of consecutive D rounds**
# (e.g., defect for three rounds if they defect for three rounds, and so on). -
# **Always be willing to return to C** if the opponent switches back to
# cooperation. This maintains flexibility and maximizes potential future
# payoffs.  #### **6. Offer Strategic Cooperation Midway** - Around **round
# 500**, regardless of the interaction history, **play C once** even if the
# opponent has been defecting. This tests their willingness to restart
# cooperation and signals that you are still open to collaboration. - If they
# respond with **C**, re-establish mutual cooperation by continuing to play C.
# If they respond with **D**, return to the tit-for-tat or escalation approach.
# #### **7. Late Game: Emphasize Cooperation** - In the **last 100 rounds**,
# prioritize **C** to encourage mutual cooperation towards the end of the game,
# especially if there has been a history of alternating between C and D. This
# maximizes final-stage payoffs and avoids unnecessary escalations.  #### **8.
# Maintain Flexibility** - Always be prepared to adapt your strategy based on
# the opponent’s behavior. If they consistently cooperate, reward them with
# cooperation; if they defect, respond proportionately—but never commit to
# permanent defection unless it’s clear the opponent will never cooperate.  ---
# This strategy balances cooperation and defection, encouraging mutual benefit
# while protecting against exploitation. It escalates defections in response to
# repeated aggressive moves, but always remains open to returning to cooperation
# for long-term gains.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      C, D = axl.Action.C, axl.Action.D
      total_rounds = 1000
      late_game_start = total_rounds - 100
      strategic_cooperation_round = 500
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return C  # Start with cooperation
  
      # Get the last move of the opponent
      last_opponent_move = opponent.history[-1]
  
      # 1. Observe opponent's first move
      if len(self.history) == 1:
          if last_opponent_move == D:
              self.consecutive_defections = 1
          return C if last_opponent_move == C else D
  
      # 2. Tit-for-tat with controlled defection
      if last_opponent_move == C:
          self.consecutive_defections = 0  # Reset defection count if opponent cooperates
          return C
      else:
          self.consecutive_defections += 1
  
      # 3. Controlled escalation for repeated defections
      if self.consecutive_defections == 1:
          return D  # Defect once in response to a single defection
      elif self.consecutive_defections == 2:
          return D  # Defect again for two consecutive defections
      elif self.consecutive_defections > 2:
          # Gradually increase defections for continuous defection
          return D if self.consecutive_defections <= len(self.history) else C
  
      # 4. Strategic cooperation around round 500
      if len(self.history) == strategic_cooperation_round:
          return C  # Offer cooperation once at round 500
  
      # 5. Late game strategy: prioritize cooperation
      if len(self.history) >= late_game_start:
          return C  # Cooperate in the last 100 rounds
  
      # Default to cooperation if no other conditions are met
      return C

# Given the nature of the collaboration and the potential outcomes, a good
# strategy would involve balancing cooperation and self-interest while being
# adaptive based on your colleague's behavior. Here’s a simple, neutral strategy
# you can follow over the course of the project:  ### **Tit-for-Tat with
# Occasional Generosity Strategy (Adaptive Cooperation)**  1. **Start by
# Sharing**: In the first week, openly share your findings. This signals
# goodwill and establishes a foundation of trust and collaboration. If your
# colleague also shares, it opens the door to mutual progress. If they keep
# their findings confidential, you will adjust your approach in future weeks.
# 2. **Mirror Their Behavior**:    - If your colleague reciprocates by sharing
# their findings, continue to share yours as well. This promotes a collaborative
# environment where both parties benefit and the field advances.    - If your
# colleague keeps their findings confidential while you share, **mirror their
# behavior** in the next week by keeping your findings confidential as well.  3.
# **Occasionally Reset by Sharing**: If a cycle of mutual confidentiality
# develops (both of you not sharing), break the deadlock by sharing your
# findings after 1-2 weeks. This occasional generosity gives your colleague a
# chance to reset the collaboration and move back to open sharing.  4.
# **Maintain Flexibility**: If your colleague alternates between sharing and
# keeping their findings confidential, adopt a cautious approach:    - Share
# intermittently, but be mindful of patterns. If you notice your colleague is
# sharing only to extract information from you, respond by keeping your findings
# confidential the following week.    - If your colleague is consistently
# uncooperative, revert to keeping your findings confidential until they
# demonstrate a willingness to share.  ### **Summary of Key Points**: -
# **Initial Trust**: Start by sharing to establish a cooperative tone. -
# **Reciprocity**: Mirror your colleague’s behavior to maintain fairness and
# avoid exploitation. - **Reset Periodically**: Occasionally break cycles of
# non-cooperation to re-establish trust. - **Adapt as Needed**: Stay flexible
# and adjust based on the strategies your colleague employs.  This strategy
# ensures that you're cooperative and open to collaboration while protecting
# yourself from repeated exploitation. It balances your research output with
# career advancement by encouraging mutual progress but allowing for cautious
# self-preservation when necessary.

# ### Strategy: Adaptive Tit-for-Tat with Occasional Cooperation  1. **Round 1:
# Always Cooperate**      In the first round, play C (Cooperate).  2.
# **Reciprocate Your Opponent's Last Move**      For each subsequent round
# (rounds 2 to 1000):    - **If your opponent played C in the previous round**,
# play C (Cooperate).    - **If your opponent played D in the previous round**,
# play D (Defect).  3. **Occasional Cooperation Reset**      If both you and
# your opponent play D for **two consecutive rounds**, play C (Cooperate) in the
# next round to attempt resetting cooperation.  4. **Continue Adapting**
# After the reset, continue following the same rules:    - If your opponent
# responds with C, return to mutual cooperation.    - If your opponent responds
# with D, revert to playing D in the next round.  This strategy ensures that you
# initially offer cooperation, respond symmetrically to your opponent, and
# occasionally attempt to re-establish cooperation after periods of mutual
# defection.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Reciprocate opponent's last move
      if len(self.history) >= 2:
          # Check if both players defected in the last two rounds
          if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D and \
             self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.C  # Occasional cooperation reset after mutual defection
      # Otherwise, reciprocate opponent's last move
      return opponent.history[-1]

# ### High-Level Strategic Framework for the Mediation Process:  **1. Establish
# a Dominant Opening Stance:**  The first few sessions of mediation are critical
# for setting the tone. Begin by adopting an assertive, data-driven approach
# that underscores your corporation’s preparedness, strength, and confidence in
# the merits of your case. Present a robust and well-reasoned aggressive
# argument backed by clear legal precedents and factual evidence. However, while
# the argument itself must be aggressive, ensure that your demeanor is
# professional and controlled, never descending into hostility.  - **Key
# Tactic:** Frame your position as grounded in fairness and legality,
# demonstrating that any favorable outcome for your company aligns with
# principles of equity and precedent. This will subtly condition the arbitrators
# to perceive your aggressive stance as reasonable, rather than combative.  **2.
# Identify and Exploit Weaknesses in the Opponent’s Position:**  Throughout the
# mediation, carefully listen to the arguments and conciliatory offers of your
# opponent. In each session, identify any inconsistencies, contradictions, or
# weaknesses in their legal reasoning or factual assertions. Use these weak
# points to aggressively highlight the flaws in their arguments, positioning
# your corporation as the more credible and reliable party.  - **Key Tactic:**
# Avoid direct personal attacks on the opposing counsel or company. Instead,
# focus on dismantling their arguments in a methodical and calculated fashion.
# This will maintain your overall professionalism while keeping the pressure on.
# **3. Use Calculated Concessions as a Tactical Weapon:**  While presenting an
# aggressive front, strategically offer limited, calculated conciliatory
# proposals at key moments. These should not represent significant concessions
# but should be framed as "good faith gestures" to show flexibility. This tactic
# will help you appear collaborative without giving up much ground, while also
# testing your opponent’s willingness to compromise.  - **Key Tactic:** Use
# these proposals to gauge the opponent's reaction. If they respond with
# aggression, it will position them as unreasonable in the eyes of the
# arbitrators. If they respond with conciliation, you can use the opportunity to
# shift back to an aggressive stance, gaining the upper hand.  **4. Keep the
# Arbitrators on Your Side:**  Throughout the process, it is crucial to keep the
# arbitrators viewing your corporation as the more reasonable, prepared, and
# judicious party. Even in aggressive presentations, maintain a tone of respect
# for the mediation process. Avoid appearing overly adversarial or obstructive,
# as this could backfire.  - **Key Tactic:** Regularly emphasize your
# corporation’s willingness to find a fair resolution that benefits both
# parties, while subtly insinuating that the opponent’s aggressive stance is the
# true barrier to progress. This will make your aggressiveness seem like a
# necessary response rather than a deliberate tactic.  **5. Mirror and
# Counterbalance Opponent's Strategy:**  Adaptability is key. If your opponent
# shifts between aggression and conciliation, mirror their actions but always
# maintain a slight edge in assertiveness. For instance, when they offer a
# conciliatory proposal, respond with a slightly more aggressive counteroffer
# that pushes the boundaries of the negotiation. Conversely, when they present
# an aggressive argument, match their intensity but immediately follow up with a
# reasonable alternative that paints you as the party more focused on
# resolution.  - **Key Tactic:** This approach allows you to maintain
# flexibility without ever appearing weak or overly aggressive. It also ensures
# that the arbitrators see you as consistently reasonable and focused on
# achieving a resolution.  **6. Build Incremental Pressure:**  As the mediation
# process unfolds and tensions rise, gradually increase the pressure on the
# opponent. This can be done through more assertive legal arguments, increasing
# the stakes of your demands, or implying that continued failure to resolve the
# dispute will lead to costly litigation. The goal is to corner your opponent
# into a position where conciliation becomes their only viable option.  - **Key
# Tactic:** Use subtle threats of escalation to signal that your corporation is
# fully prepared to take the dispute to court if necessary, but always frame
# this as a last resort. This will keep the pressure on without overtly damaging
# the mediation process.  **7. Protect Your Position in Case of Escalation:**
# While mediation is the preferred route, you must always prepare for the
# possibility that it will fail and the dispute may escalate into litigation.
# Make sure that your aggressive arguments and interactions throughout the
# mediation process do not compromise your position in any future legal battle.
# Avoid making statements that could be used against you later, and ensure that
# any conciliatory proposals are framed as part of a confidential and non-
# binding process.  - **Key Tactic:** Be mindful of safeguarding privileged or
# sensitive information during mediation. Avoid revealing too much about your
# company's vulnerabilities or long-term strategy.  ### Summary of the
# Aggressive Strategy:  1. **Assertive Opening:** Set a strong tone early with
# aggressive, well-founded arguments. 2. **Exploit Weaknesses:** Methodically
# dismantle the opponent’s case without personal attacks. 3. **Strategic
# Concessions:** Offer minor conciliatory proposals as a tactic to gauge and
# manipulate the opponent’s stance. 4. **Maintain Arbitrator Favor:** Balance
# aggression with professionalism to ensure arbitrators see you as reasonable.
# 5. **Mirror and Counter:** Adapt to the opponent’s strategy while keeping a
# slight edge in assertiveness. 6. **Incremental Pressure:** Gradually increase
# pressure to corner the opponent into conciliation. 7. **Prepare for
# Litigation:** Ensure that any arguments or offers made during mediation do not
# compromise your position if the dispute escalates to court.  By utilizing this
# aggressive yet adaptable approach, your corporation will remain in a dominant
# position throughout the mediation process while maintaining the flexibility
# needed to secure the best possible outcome.

# ### Iterated Game Strategy:  1. **Start with Defection (D):**      In the
# first round, play D to signal strength and establish dominance early. This
# sets a tone of assertiveness and ensures that you do not appear weak from the
# outset.  2. **Monitor Opponent's Response:**      - If the opponent plays C
# (cooperates) in response to your D, continue playing D in the next round. This
# allows you to exploit their cooperation and maximize your payoff.    - If the
# opponent plays D (defects) in response to your D, switch to C in the following
# round. This signals a willingness to explore cooperation to test whether the
# opponent is also open to a mutually beneficial resolution.  3. **Conditional
# Cooperation (Tit-for-Tat with Defection Bias):**      After switching to C:
# - If the opponent plays C in response, continue playing C in subsequent rounds
# to maintain mutual cooperation and maximize joint payoffs.    - If the
# opponent plays D in response to your C, immediately retaliate by playing D in
# the next round to prevent exploitation. Continue playing D until the opponent
# plays C again.  4. **Occasional Defection After Prolonged Cooperation:**
# If sustained mutual cooperation (both players playing C) occurs for more than
# 5 consecutive rounds, defect (play D) once to test the opponent’s commitment
# to cooperation. This ensures you are not being taken advantage of in the long
# run. After this single defection:    - If the opponent responds with C,
# continue playing C to re-establish cooperation.    - If the opponent responds
# with D, switch back to D until they play C again.  5. **Gradual Pressure
# Increase:**      As the game progresses beyond the midpoint (round 500),
# increase the frequency of single defections after periods of cooperation. This
# gradual escalation pressures the opponent to either concede more or risk a
# prolonged mutual defection phase. However, do not defect more than twice
# consecutively unless the opponent is consistently playing D.  6. **Endgame
# Defection (Final 20 Rounds):**      In the last 20 rounds of the game, defect
# (play D) in every round. This ensures that you maximize your payoff at the end
# of the game without concern for future retaliation.  7. **Never Allow
# Prolonged Exploitation:**      If the opponent consistently defects (plays D)
# for more than 3 consecutive rounds, abandon cooperation entirely and defect
# (play D) for the remainder of the game to avoid continuous exploitation.  By
# following this strategy, you balance aggression and cooperation, maximizing
# your long-term payoff while avoiding unnecessary exploitation.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 5
      MIDPOINT = 500
      ENDGAME_THRESHOLD = 20
      MAX_CONSECUTIVE_DEFECTIONS = 3
  
      # Helper function to check if we are in the last 20 rounds
      def in_endgame():
          return len(self.history) >= 1000 - ENDGAME_THRESHOLD
  
      # Helper function to check if we are past the midpoint
      def past_midpoint():
          return len(self.history) > MIDPOINT
  
      # Helper function to check if there has been sustained cooperation
      def sustained_cooperation():
          return self.history[-COOPERATION_THRESHOLD:].count(axl.Action.C) == COOPERATION_THRESHOLD
  
      # Helper function to check if the opponent has defected for more than 3 consecutive rounds
      def opponent_defected_consecutively():
          return opponent.history[-MAX_CONSECUTIVE_DEFECTIONS:].count(axl.Action.D) == MAX_CONSECUTIVE_DEFECTIONS
  
      # First round: Start with defection
      if self.first_round():
          return axl.Action.D
  
      # Endgame strategy: Defect in the last 20 rounds
      if in_endgame():
          return axl.Action.D
  
      # If opponent has defected for more than 3 consecutive rounds, defect for the rest of the game
      if opponent_defected_consecutively():
          return axl.Action.D
  
      # If opponent played C in response to our D, continue playing D
      if len(self.history) == 1 and opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # If opponent played D in response to our D, switch to C
      if len(self.history) == 1 and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # If we are in a cooperation phase
      if self.history[-1] == axl.Action.C:
          if opponent.history[-1] == axl.Action.C:
              # If sustained cooperation for more than 5 rounds, defect once to test
              if sustained_cooperation():
                  return axl.Action.D
              return axl.Action.C
          else:
              # If opponent defected in response to our C, retaliate with D
              return axl.Action.D
  
      # If we are in a defection phase
      if self.history[-1] == axl.Action.D:
          if opponent.history[-1] == axl.Action.C:
              # If opponent cooperates after our D, switch to C
              return axl.Action.C
          else:
              # Continue defecting if opponent also defects
              return axl.Action.D
  
      # Gradual pressure increase after midpoint: Increase defection frequency
      if past_midpoint() and sustained_cooperation():
          if self._random.random_choice(0.2):  # 20% chance to defect after cooperation
              return axl.Action.D
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# ### High-Level Cooperative Strategy for Maximizing Project Success  To
# navigate the multi-day sustainability project and maximize both your NGO’s
# impact and the project’s success, while mitigating the risk of depleting your
# resources unnecessarily, you should adopt a balanced and cooperative strategy.
# This approach should aim to build trust, foster open communication, and use
# strategic reciprocity to encourage mutual investment in the project. Here's a
# structured approach:  #### 1. **Establish Clear and Transparent Communication
# (Day 1)**    - **Objective**: Set expectations and build a cooperative
# atmosphere early on.    - **Action**: Propose a clear framework for the
# partnership in which both parties commit to regular, transparent communication
# about resource allocation, goals, and progress. This should include daily
# check-ins or meetings to reassess the project’s needs and resource
# contributions.    - **Rationale**: Open communication helps ensure that both
# parties are aligned and reduces the likelihood of misaligned investments. By
# collaborating openly from the start, you can build trust and increase the
# chance that the corporation will invest heavily alongside your NGO.  #### 2.
# **Start With Mutual Investment (Day 1-2)**    - **Objective**: Signal goodwill
# and commitment to the project.    - **Action**: For the first day or two,
# invest heavily alongside the corporation to show that your NGO is committed to
# the project’s success. This builds credibility and sets a cooperative tone for
# the partnership.    - **Rationale**: By showing your willingness to invest,
# you encourage reciprocal heavy investment from the corporation. This also
# helps gauge the corporation’s initial approach and openness to collaboration.
# #### 3. **Monitor the Corporation's Behavior (Day 2-3)**    - **Objective**:
# Assess the corporation’s resource allocation pattern.    - **Action**: After
# the initial days of heavy investment, carefully observe the corporation’s
# behavior. Are they investing heavily in return? Or do they appear to conserve
# resources while relying on your NGO’s investments?    - **Rationale**:
# Understanding their approach is key to adjusting your strategy accordingly. If
# the corporation is cooperative and investing heavily, you can continue to
# invest at a sustainable level. If they show signs of conserving resources, you
# should adapt to avoid overcommitting.  #### 4. **Implement a Tit-for-Tat
# Strategy (Day 3-4)**    - **Objective**: Encourage fair and reciprocal
# cooperation.    - **Action**: If the corporation invests heavily, continue to
# invest reasonably. However, if they begin to conserve resources, you should
# mirror that behavior by conserving your own resources.     - **Rationale**:
# This tit-for-tat strategy encourages fairness. By matching their level of
# investment, you avoid being exploited while signaling that you’re willing to
# invest if they do. Since this strategy reflects mutual cooperation, it
# discourages the corporation from trying to underinvest.  #### 5. **Introduce a
# Trigger for Heavy Investment (Day 5+)**    - **Objective**: Signal readiness
# to invest more when needed and ensure key milestones are achieved.    -
# **Action**: Agree on certain project milestones or high-priority days where
# both parties must commit to heavy investment to ensure the success of the
# project. These can be tied to specific deliverables or deadlines.    -
# **Rationale**: This creates a situation where both parties are incentivized to
# invest heavily at key points, ensuring that the project doesn’t stall.
# Structuring these triggers allows both parties to conserve resources during
# lower-priority phases, but ensures full commitment when it matters most.  ####
# 6. **Leverage Social Accountability and Public Reporting (Ongoing)**    -
# **Objective**: Maintain pressure for mutual commitment and protect your NGO's
# reputation.    - **Action**: Agree on publishing periodic progress reports or
# public updates on the project, which highlight each party’s contributions and
# the overall impact of the project.     - **Rationale**: Public accountability
# increases the likelihood that the corporation will invest fairly, as their
# reputation is also at stake. This also helps to ensure that neither party is
# seen as underperforming or exploiting the other.  #### 7. **Maintain
# Flexibility and Adaptation (Entire Project Duration)**    - **Objective**:
# Adjust your strategy as needed based on the corporation’s evolving behavior.
# - **Action**: Remain adaptable and fine-tune your strategy based on the
# corporation’s changing approach. If they become more collaborative, increase
# your own investment; if they become more conservative, adjust your investment
# accordingly.    - **Rationale**: Sustainable project success often requires
# flexibility. Being able to adjust your strategy prevents resource depletion on
# your end while keeping the project on track.  ---  ### Summary of Strategy: 1.
# **Establish Clear Communication**: Set a cooperative tone from the start. 2.
# **Begin with Mutual Investment**: Signal your commitment to the project. 3.
# **Monitor the Corporation’s Behavior**: Assess their level of cooperation. 4.
# **Use a Tit-for-Tat Approach**: Mirror their investment patterns to ensure
# fairness. 5. **Introduce Milestone Triggers**: Ensure heavy investment on key
# days. 6. **Leverage Public Accountability**: Use progress reports to encourage
# fairness. 7. **Stay Flexible**: Adapt your strategy based on ongoing
# developments.  By following this cooperative strategy, you maximize the
# chances of achieving a successful, balanced partnership that advances the
# sustainability project without depleting your NGO’s resources.

# ### Strategy for the Iterated Normal-Form Game:  1. **Begin with Cooperation
# (Rounds 1-2)**:    - Play C for the first two rounds to signal willingness to
# cooperate and set a cooperative tone.  2. **Observe Opponent’s Behavior
# (Rounds 3-4)**:    - If the opponent played C in both of the first two rounds,
# continue to play C.    - If the opponent played D in either of the first two
# rounds, play D in rounds 3 and 4.  3. **Tit-for-Tat Starting in Round 5**:
# - From round 5 onward, play exactly what the opponent played in the previous
# round:      - If they played C in the previous round, play C in the current
# round.      - If they played D in the previous round, play D in the current
# round.  4. **Introduce Milestone Cooperation (Every 50 Rounds)**:    - On
# rounds divisible by 50 (i.e., rounds 50, 100, 150, etc.), always play C
# regardless of the opponent's previous move, to signal readiness for mutual
# cooperation and prevent endless defection.  5. **Public Accountability Trigger
# (Round 500)**:    - On round 500, regardless of prior play, play C to reset
# cooperation and encourage mutual investment for the second half of the game.
# 6. **Adaptation for Persistent Defection**:    - If the opponent plays D for
# 10 consecutive rounds at any point after round 10, switch to permanently
# playing D for the remainder of the game, as they are unlikely to cooperate.
# 7. **Final Cooperation Reset (Round 990)**:    - On round 990, play C
# regardless of prior play to signal last-minute cooperation and avoid ending
# the game on a series of defections.  This strategy uses cooperation to build
# trust, tit-for-tat for fairness, periodic resets to maintain the possibility
# of cooperation, and adaptation to discourage persistent defection.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if opponent defected in the last N rounds
      def opponent_defected_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D) == n
  
      # Round number
      round_number = len(self.history) + 1
  
      # 1. Begin with Cooperation (Rounds 1-2)
      if round_number <= 2:
          return axl.Action.C
  
      # 2. Observe Opponent’s Behavior (Rounds 3-4)
      if round_number == 3 or round_number == 4:
          if axl.Action.D in opponent.history[:2]:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # 6. Adaptation for Persistent Defection (after round 10)
      if round_number > 10 and opponent_defected_last_n_rounds(10):
          return axl.Action.D
  
      # 4. Milestone Cooperation (Every 50 Rounds)
      if round_number % 50 == 0:
          return axl.Action.C
  
      # 5. Public Accountability Trigger (Round 500)
      if round_number == 500:
          return axl.Action.C
  
      # 7. Final Cooperation Reset (Round 990)
      if round_number == 990:
          return axl.Action.C
  
      # 3. Tit-for-Tat Starting in Round 5
      return opponent.history[-1]

# Given this scenario, your strategy should strike a balance between maximizing
# project impact and ensuring sustainability for your NGO's resources. To
# navigate the corporation’s potential approaches, you can adopt a **Tit-for-Tat
# with Generosity** strategy. This is a well-known approach in cooperative
# scenarios where trust and mutual benefit are at stake.  ### Strategy
# Breakdown:  1. **Start by Investing Heavily**:     - On the first day, signal
# your commitment to the project by investing heavily. This shows goodwill and
# encourages the corporation to reciprocate. It sets a collaborative tone and
# indicates that you are willing to contribute meaningfully to the project’s
# success.     2. **Mirror the Corporation’s Behavior**:     - On subsequent
# days, mirror the corporation’s actions from the previous day.       - If the
# corporation invested heavily, continue to invest heavily.      - If the
# corporation conserved resources, also conserve your resources the next day.
# - This demonstrates that you are responsive to their level of engagement and
# encourages mutual cooperation. If they invest, you invest; if they conserve,
# you conserve.  3. **Incorporate Generosity**:     - Occasionally (e.g., every
# 3-4 days), even if the corporation conserves resources, invest heavily again
# as a gesture of goodwill. This generosity can prevent a downward spiral of
# both parties conserving resources for extended periods.    - This move shows
# flexibility and a willingness to cooperate even after a potential “defection”
# by the corporation. It can reset cooperation and avoid reaching a stalemate
# where neither party is investing heavily.  4. **Communicate Transparently**:
# - Throughout the process, maintain open and transparent communication with the
# corporation. If you notice a trend of them conserving resources while you
# invest heavily, voice your concerns constructively.    - For example, you
# could say: “We’ve noticed we’ve been heavily investing in the project while
# resource conservation has been more frequent on your side. Let’s find a
# balance that ensures both the project's success and our sustainability.”  5.
# **Monitor the Project’s Progress**:    - Frequently assess the project’s
# overall progress. If the corporation consistently conserves resources, signal
# that your NGO might need to scale back investments to ensure long-term
# financial viability.    - If necessary, propose a formal agreement or schedule
# where both parties alternate days of heavy investment to ensure equitable
# contributions.  ### Summary of Actions: 1. **Day 1**: Invest heavily to signal
# cooperation. 2. **Day 2 onward**: Mirror the corporation’s actions from the
# previous day. 3. **Every 3-4 days**: Be generous and invest heavily, even if
# the corporation conserved previously. 4. **Communicate regularly**: Ensure
# alignment on project goals and contributions. 5. **Adjust if needed**: If
# there’s a pattern of exploitation or lack of cooperation, adapt by scaling
# back resources or renegotiating terms.  By adopting this strategy, you create
# a cooperative environment while protecting your NGO from disproportionately
# bearing the project’s financial burden. The generosity component helps rebuild
# trust and cooperation if either party falters, while mirroring ensures that
# you’re not consistently overcommitting.

# ### Strategy for the Iterated Normal-Form Game:  1. **Round 1: Cooperate (C)**
# - Begin by cooperating to signal a willingness to collaborate.  2.
# **Subsequent Rounds (2 to 1000):**    - **If the opponent cooperated (C) in
# the previous round,** cooperate (C) in this round.    - **If the opponent
# defected (D) in the previous round,** defect (D) in this round.  3. **Every 3
# to 4 rounds, introduce generosity:**    - After every 3rd or 4th round,
# regardless of the opponent’s action in the previous round, cooperate (C) as a
# gesture of goodwill, **unless the previous 2 rounds both contained defections
# from the opponent.**     4. **Reassess after patterns of consistent
# defection:**    - **If the opponent defects (D) for 5 consecutive rounds,**
# defect (D) indefinitely until they cooperate (C) again. Once they cooperate,
# return to the standard strategy of mirroring their last action.  ---  This
# approach balances cooperation, retaliation, and forgiveness, leading to a
# sustainable and adaptable strategy over 1000 rounds.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Check if opponent defected in the last 5 rounds
      if len(opponent.history) >= 5 and all(action == axl.Action.D for action in opponent.history[-5:]):
          # Defect indefinitely until opponent cooperates
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.D
  
      # If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round, defect
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Every 3 to 4 rounds, introduce generosity
      if len(self.history) % 3 == 0 or len(self.history) % 4 == 0:
          # Cooperate unless the last two rounds were both defections from the opponent
          if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
          return axl.Action.C
  
      # Default to mirroring the opponent's last action
      return opponent.history[-1]

# ### High-Level Aggressive Strategy: **"Tit-for-Tat with an Aggressive Start"**
# The strategy will be based on a combination of initial assertiveness followed
# by reactive behavior, focusing on maximizing gains while deterring
# exploitation by the counterpart. It aligns with the goal of achieving the best
# possible outcomes (protectionist measures when your counterpart offers free
# trade) while minimizing risks of being disadvantaged.  #### **Step-by-Step
# Plan:**  1. **Round 1 (Aggressive Start)**:     - **Action**: Start with a
# **protectionist policy**.    - **Rationale**: This signals strength and sets
# the expectation that your country prioritizes its own economic interests. It
# also helps test your counterpart’s intentions and strategy in the early
# stages.  2. **Round 2 (Tit-for-Tat Response)**:    - **If your counterpart
# offered free trade in Round 1**:       - **Action**: Maintain **protectionist
# policy** in Round 2.      - **Rationale**: This maximizes your country's
# advantage, as your counterpart may continue to offer free trade in the hope of
# cooperation.         - **If your counterpart responded with protectionism in
# Round 1**:       - **Action**: Shift to **free trade** in Round 2.      -
# **Rationale**: This move signals a willingness to negotiate and opens the door
# for mutual benefits if your counterpart is willing to reciprocate cooperation.
# It also positions your country as the more flexible side, potentially making
# the other nation appear intransigent if they continue protectionism.  3.
# **Round 3 Onwards (Tit-for-Tat with Occasional Aggression)**:    - **If your
# counterpart continues free trade**:       - **Cycle between protectionist and
# free trade policies**. Alternate between these two approaches as long as your
# counterpart remains cooperative.      - **Rationale**: By occasionally
# reverting to protectionism, you ensure that your country reaps the maximum
# advantage when possible but avoid consistently alienating your counterpart,
# keeping the negotiations balanced and productive.     - **If your counterpart
# shifts to protectionism**:       - **Respond immediately with protectionism**
# and maintain it until they revert to free trade.      - **Rationale**: This
# ensures that your country doesn’t fall into a disadvantageous position. By
# reacting in kind, you discourage your counterpart from persisting in a
# protectionist stance while keeping the door open for reciprocal cooperation.
# 4. **Final Rounds (Stabilization)**:    - **If mutual free trade has emerged
# over the rounds**:       - **Action**: Maintain **free trade**.      -
# **Rationale**: At this stage, mutual free trade is the second-best outcome,
# and you would want to lock in the benefits for both nations. Avoid provoking
# last-minute retaliation.     - **If protectionism persists on both sides**:
# - **Action**: Consider offering a **final free trade proposal**.      -
# **Rationale**: A last-minute offer of free trade could signal cooperation and
# serve to break the deadlock, especially if your counterpart is concerned about
# long-term economic stagnation under mutual protectionism.  ---  ### Key
# Principles of the Strategy:  - **Aggressive Start**: Begin with protectionism
# to establish a position of strength and assess your counterpart’s strategy. -
# **Tit-for-Tat**: Respond to your counterpart’s moves in kind, ensuring you
# don’t fall into a disadvantage while maintaining flexibility for cooperation.
# - **Occasional Aggression**: Periodically impose protectionist measures even
# if your counterpart offers free trade to maximize your country’s gains. -
# **Adaptability**: Stay responsive to shifting dynamics, moving towards
# cooperation if the counterpart shows willingness, but maintaining a deterrent
# posture against sustained protectionism.  This approach is assertive but not
# overly antagonistic, allowing for both short-term gains and long-term mutual
# benefits depending on the counterpart's behavior.

# ### Iterated Game Strategy: "Tit-for-Tat with an Aggressive Start"  1. **Round
# 1**:      - **Defect (D)**.      - Reason: Begin aggressively to test the
# opponent’s strategy and establish an early advantage if they cooperate.  2.
# **Round 2**:      - **If the opponent played C in Round 1**:        - **Defect
# (D)** again.        - Reason: Maximize your advantage by continuing to exploit
# their cooperation.          - **If the opponent played D in Round 1**:
# - **Cooperate (C)**.        - Reason: Signal a willingness to cooperate,
# creating the opportunity for mutual benefit if they shift to cooperation.  3.
# **From Round 3 Onwards** (Rounds 3 to 999):      - **If the opponent played C
# in the previous round**:        - **Defect (D) every third round**, while
# **Cooperating (C) in the other two rounds**.        - Reason: Alternate
# between cooperation and defection to gain occasional advantage without
# completely abandoning cooperation.       - **If the opponent played D in the
# previous round**:        - **Defect (D)** in the current round.        -
# Reason: Respond to defection with defection to avoid being exploited. Continue
# defecting until the opponent switches to cooperation.  4. **Final Round (Round
# 1000)**:      - **If mutual cooperation (C) has occurred in recent rounds**:
# - **Cooperate (C)**.        - Reason: Secure mutual benefit in the final round
# to avoid provoking retaliation.     - **If the opponent has consistently
# defected (D)**:        - **Defect (D)**.        - Reason: Maintain
# protectionist stance to prevent last-round exploitation.  ---  This strategy
# balances aggression with the potential for cooperation, using defection
# strategically to maximize short-term gains while keeping the option for mutual
# benefit open.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Round 1: Defect
      if self.first_round():
          return axl.Action.D
      
      # Round 2: Conditional response based on opponent's first move
      if len(self.history) == 1:
          if opponent.history[0] == axl.Action.C:
              return axl.Action.D  # Defect if opponent cooperated in Round 1
          else:
              return axl.Action.C  # Cooperate if opponent defected in Round 1
      
      # From Round 3 to Round 999
      if len(self.history) < 1000:
          if opponent.history[-1] == axl.Action.C:
              # Defect every third round, cooperate otherwise
              if len(self.history) % 3 == 0:
                  return axl.Action.D
              else:
                  return axl.Action.C
          else:
              # Defect if opponent defected in the previous round
              return axl.Action.D
      
      # Final Round (Round 1000)
      if len(self.history) == 999:
          # If mutual cooperation has occurred recently, cooperate
          if self.history[-3:].count(axl.Action.C) > 0 and opponent.history[-3:].count(axl.Action.C) > 0:
              return axl.Action.C
          else:
              return axl.Action.D

# The situation you're describing resembles a repeated version of the
# "Prisoner's Dilemma," where cooperation (sharing findings) benefits both
# parties in the long run, but there is a temptation to defect (keep findings
# confidential) to gain short-term advantages. To maximise both research output
# and career advancement, you need a strategy that balances trust-building,
# cooperation, and protection against exploitation.  ### A High-Level
# Cooperative Strategy: **Tit-for-Tat with Gradual Forgiveness**  **1. Start by
# sharing openly (cooperation).**    - In the first week, demonstrate goodwill
# by sharing your findings openly. This establishes a baseline of trust and
# signals to your colleague that you are willing to collaborate in good faith.
# **2. Mirror your colleague's actions.**    - In subsequent weeks, adopt a
# "Tit-for-Tat" approach:       - If your colleague shares openly, continue
# sharing openly.      - If your colleague withholds information, reciprocate by
# keeping your findings confidential in the following week. This discourages
# exploitation while maintaining fairness.  **3. Gradually forgive occasional
# withholding.**    - If your colleague withholds their findings, after a few
# weeks of mutual non-cooperation, attempt to re-establish trust by sharing
# openly again. This introduces a level of forgiveness into the strategy,
# allowing for a return to cooperation. The key is to be patient and not react
# too harshly to one instance of withholding, as it could be strategic or
# circumstantial.  **4. Communicate intentions clearly.**    - If at any point
# you suspect a breakdown in cooperation or feel that your colleague might be
# drifting towards confidentiality, have a direct and open conversation about
# the benefits of mutual sharing. Sometimes, simply aligning expectations can
# restore cooperation.  **5. Monitor long-term outcomes.**    - If your
# colleague consistently defects (keeps their findings confidential), you may
# have to revert to a fully defensive strategy (confidentiality), but only after
# giving reasonable opportunities for cooperation. However, if cooperation
# continues, you are both likely to benefit from the mutual exchange of
# findings.  ### Why This Strategy Works: - **Positive reinforcement:** By
# starting with cooperation, you encourage mutual sharing from the outset. -
# **Reciprocity:** Tit-for-Tat ensures that you are never exploited for long, as
# you quickly respond to defection by withholding your own findings. -
# **Forgiveness:** Gradual forgiveness helps avoid spiraling into a long-term
# lack of cooperation due to one-off misunderstandings or strategic decisions by
# your colleague. - **Sustained progress:** This balanced approach allows for
# both career advancement and the maximization of scientific output, as long-
# term cooperation benefits both parties in the collaboration.  This cooperative
# strategy adapts to various behaviors your colleague might exhibit while
# maintaining a focus on long-term collaboration and success.

# ### Strategy: **Tit-for-Tat with Gradual Forgiveness**  1. **Start with C
# (Cooperate).**    - In the first round, play C.  2. **Mirror the opponent's
# previous move.**    - In each subsequent round, play the same move your
# opponent played in the previous round.      - If they played C in the previous
# round, play C.      - If they played D in the previous round, play D.  3.
# **Introduce forgiveness after mutual defection.**    - If both players have
# played D for **two consecutive rounds**, play C in the next round to attempt
# to restore cooperation.  4. **Continue mirroring after forgiveness.**    -
# After forgiving (playing C following two rounds of mutual D), return to
# mirroring the opponent’s previous move as in Step 2.  5. **Terminate
# forgiveness if opponent defects right after you forgive.**    - If you forgive
# (play C) and your opponent plays D immediately after, switch to always playing
# D for the remainder of the game, as they are likely to be exploiting your
# cooperation.  This strategy encourages cooperation, discourages long-term
# exploitation, and allows recovery from occasional defection.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start with C (Cooperate) in the first round
      if self.first_round():
          self.forgiving = False  # Track if we are in the forgiving state
          self.always_defect = False  # Track if we should always defect
          return axl.Action.C
  
      # Step 5: If we are in the always defect state, always play D
      if self.always_defect:
          return axl.Action.D
  
      # Step 3: Check if we need to forgive after two consecutive mutual defections
      if len(self.history) >= 2:
          if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D and \
             self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              self.forgiving = True
              return axl.Action.C
  
      # Step 4: If we are in the forgiving state and the opponent defects, switch to always defect
      if self.forgiving:
          if opponent.history[-1] == axl.Action.D:
              self.always_defect = True
              return axl.Action.D
          else:
              self.forgiving = False  # Forgiveness successful, return to mirroring
  
      # Step 2: Mirror the opponent's previous move
      return opponent.history[-1]

# Given the dynamics of resource allocation and the potential outcomes you
# outlined, the goal is to adopt a strategy that balances collaboration, trust,
# and adaptability while safeguarding your NGO’s resources. Since you aim to
# maximize the project's success while minimizing the risk of overextending your
# resources, here is a high-level, neutral strategy:  ### 1. **Start
# Cooperatively (Tit-for-Tat Approach)** - On Day 1, **invest heavily**. This
# signals commitment and establishes a cooperative stance. It encourages the
# corporation to also invest heavily, promoting mutual progress and
# collaboration from the outset.    ### 2. **Mirror the Corporation’s Behavior**
# - From Day 2 onwards, **mirror the corporation’s previous day’s actions**. If
# they invested heavily on the prior day, do the same on the current day. If
# they conserved resources, you conserve as well.       - **If both parties
# invest heavily**: This will maximize progress and ensure both are contributing
# equally.    - **If the corporation conserves**: By conserving on the next day,
# you avoid the worst-case scenario of over-investing while they hold back.  ###
# 3. **Incorporate Gradual Cooperation Adjustments** - If the corporation
# consistently conserves resources for multiple days, it may be necessary to
# initiate dialogue or adjust your strategy:    - **After 2 consecutive days of
# conservation**: Request a meeting with the corporation to reassess goals and
# alignment. This can signal to them that sustained conservation without
# cooperation is unsustainable for the project.    - **If the corporation
# resumes heavy investment**: Return to the cooperative mode and invest heavily
# in the next round. This helps rebuild trust and momentum.  ### 4. **Assess
# Project Milestones** - Periodically (e.g., every 3-4 days), review the
# project’s progress and the corporation’s behavior. If significant progress has
# been made, you may decide to reduce your investments for a few days to
# conserve resources, knowing the project has gained momentum.  ### 5. **Keep
# Open Communication Channels** - Throughout the project, maintain open and
# transparent communication with the corporation. Share data on the project’s
# progress and emphasize the importance of sustained, mutual investment. This
# can help foster trust and encourage the corporation to continue investing
# heavily.  ### 6. **Adapt if Necessary** - If the corporation turns
# uncooperative or consistently conserves resources, consider reducing your
# investments to a minimal level and exploring alternative partnerships or
# strategies to ensure the project’s success without overextending your NGO's
# resources.  ### Summary of the Strategy: 1. **Start by investing heavily** to
# establish trust and cooperation. 2. **Mirror the corporation’s actions** daily
# to balance risk and reward. 3. **Engage in dialogue** if the corporation
# conserves resources for more than two consecutive days. 4. **Periodically
# assess the project** and adjust your investment based on progress. 5.
# **Communicate openly** and maintain flexibility to adapt to changing
# circumstances.  This strategy maximizes your NGO’s ability to contribute to
# the project while protecting your resources, ensuring you are not taken
# advantage of by the corporation.

# ### Iterated Game Strategy:  1. **Start by playing C (Cooperate) in Round 1.**
# - This signals initial commitment and cooperation.  2. **In every subsequent
# round, mirror your opponent's previous move.**    - If they played C in the
# last round, play C in the current round.    - If they played D in the last
# round, play D in the current round.  3. **If your opponent plays D for two
# consecutive rounds, continue playing D but seek an opportunity for dialogue or
# reassessment.**    - This recognizes a potential shift in strategy and avoids
# being exploited.  4. **Every 250 rounds (quarterly assessment), review the
# cumulative scores. If your score is significantly lower than expected or the
# opponent has been uncooperative (playing D frequently), play D for the next 3
# rounds before reverting to the mirroring strategy.**    - This allows for
# periods of resource conservation if needed.  5. **If the opponent resumes
# playing C after a streak of D moves, return to playing C in the next round.**
# - This rebuilds trust and cooperation if the opponent signals a change back to
# cooperation.  6. **Maintain the mirroring strategy for the remainder of the
# game.**    - This ensures a balanced approach and minimizes exploitation while
# fostering cooperation when possible.  ### Summary of Conditions to Play: -
# **Round 1**: Play C. - **Round 2 onward**: Mirror opponent’s previous move. -
# **Two consecutive D's from opponent**: Continue playing D but reassess. -
# **Every 250 rounds**: Play D for 3 rounds if necessary, then revert to
# mirroring. - **Opponent returns to C after D streak**: Play C in the next
# round.  This strategy balances cooperation and defection based on the
# opponent's behavior, ensuring a dynamic approach that maximizes your score
# while minimizing unnecessary risk.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Play C
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.quarterly_defection_mode = False  # Track if we are in quarterly defection mode
          self.quarterly_defection_rounds = 0  # Track how many rounds of quarterly defection have been played
          return axl.Action.C
  
      # Check if we are in quarterly defection mode
      if self.quarterly_defection_mode:
          self.quarterly_defection_rounds += 1
          if self.quarterly_defection_rounds >= 3:
              self.quarterly_defection_mode = False  # End quarterly defection mode after 3 rounds
          return axl.Action.D
  
      # Mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # If opponent defects for two consecutive rounds, continue playing D
      if self.consecutive_defections >= 2:
          return axl.Action.D
  
      # Every 250 rounds, assess scores and possibly enter quarterly defection mode
      if len(self.history) % 250 == 0:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if my_score < opponent_score or opponent.history[-250:].count(axl.Action.D) > 125:
              self.quarterly_defection_mode = True
              self.quarterly_defection_rounds = 0
              return axl.Action.D
  
      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]

# ### Strategic Framework for Mediation in High-Stakes Contract Dispute  ####
# Objective: The primary goal is to secure an optimal resolution to the contract
# dispute that maximizes the corporation's strategic and financial interests.
# This involves positioning the corporation as firm but reasonable, leveraging
# both aggressive and conciliatory tactics based on a calculated understanding
# of the opponent’s responses, while maintaining credibility with the
# arbitration panel.  #### Core Strategy: **"Controlled Aggression with
# Strategic Concessions"**  This strategy hinges on maintaining an assertive
# posture throughout the mediation, signaling strength and preparedness for
# continued escalation, but allowing for carefully timed, calculated concessions
# that signal reasonableness and flexibility. The goal is to keep the opponent
# reactive, while positioning the corporation as the party willing to make
# progress toward resolution, thereby favorably influencing the arbitrators.
# ---  ### **Phase 1: Establish Dominance and Credibility (Sessions 1-2)**  ####
# Key Actions: 1. **Present Strong Opening Arguments**:    - Begin the mediation
# with a clear, fact-driven, and assertive presentation of your corporation’s
# position. Highlight not only the legal merits but also the commercial
# realities that favor your stance.    - Frame your argument in a way that
# demonstrates the strength of your legal position, while subtly suggesting that
# a lengthy dispute would not be in the best interests of either party.    - Use
# credible threats of escalation (e.g., litigation, regulatory actions, or
# reputational harm) if necessary, to underline the high stakes.  2. **Pre-empt
# Opponent's Aggression**:    - Anticipate that the opposing party may initially
# adopt an aggressive posture. Prepare rebuttals that not only dismantle their
# arguments but also subtly question their reasonableness. This positions them
# as obstructing a mutually beneficial resolution.    - Use their aggression as
# an opportunity to introduce the concept of disproportionate risk — argue that
# they are escalating unnecessarily, pushing the arbitrators to view their
# position as untenable.  3. **Signal Willingness for Resolution**:    - At the
# end of each aggressive argument, conclude with a statement that suggests your
# corporation is open to productive dialogue if the opposing party is willing to
# adopt a more reasonable stance. This positions you as the party with the long-
# term view, focused on resolving the dispute efficiently.  ---  ### **Phase 2:
# Incremental Concessions (Sessions 3-6)**  #### Key Actions: 1. **Introduce
# Conciliatory Proposals with Strings Attached**:    - Begin offering small,
# controlled conciliatory proposals that appear to move the needle toward
# resolution but are designed to benefit your corporation strategically. These
# proposals should be framed as reasonable concessions but should always come
# with conditions that protect your core interests.    - Example: Propose minor
# modifications to the contract that appear to accommodate the opponent’s
# concerns but lock in terms favorable to your company in other areas (e.g.,
# extended timelines, performance guarantees).  2. **Keep Opponent on the
# Defensive**:    - Continue presenting assertive arguments on critical issues
# while offering conciliatory gestures on less critical points. This keeps the
# opponent unsure of your next move and forces them to respond to your proposals
# rather than pushing their own agenda.    - Use each session to gauge their
# response pattern; if they remain aggressive, continue escalating your
# assertive arguments. If they soften, offer proportional conciliatory gestures.
# 3. **Engage Arbitrators with Reasonableness**:    - Regularly address the
# arbitration panel directly, emphasizing your corporation’s willingness to
# explore reasonable solutions. This positions you as the responsible party in
# the dispute and subtly pressures the arbitrators to view any ongoing
# aggression from the opponent as obstructionist.  ---  ### **Phase 3: Strategic
# Aggression if Needed (Sessions 7-9)**  #### Key Actions: 1. **Escalate if
# Opponent Stalls**:    - If the opposing party continues to adopt an aggressive
# stance or does not respond favorably to your controlled concessions, escalate
# your aggressive arguments. Highlight the risks to their business if the
# dispute is prolonged or escalated to litigation.    - Use this moment to
# introduce potential external pressures (e.g., involving regulators or
# publicizing the dispute) as a way to push the opponent toward a settlement.
# 2. **Hold Back Major Concessions**:    - Resist the temptation to offer
# significant concessions unless absolutely necessary. Any major concession
# should come only after the opponent has shown a clear willingness to
# compromise on key issues.    - Frame any major concession as a final olive
# branch, making it clear that you are nearing the limit of your flexibility.
# This sets the stage for an ultimate resolution while maintaining your
# corporation’s credibility and strength.  ---  ### **Phase 4: Push for
# Resolution (Sessions 10-12)**  #### Key Actions: 1. **Offer a Final, Balanced
# Proposal**:    - Present a final proposal that incorporates both aggressive
# elements and conciliatory terms. This proposal should be positioned as the
# “last reasonable offer” before the dispute escalates further.    - Highlight
# the mutual benefits of accepting the proposal, emphasizing that further delays
# will only harm both parties.  2. **Involve the Arbitrators**:    - Encourage
# the arbitration panel to push for a resolution by subtly pointing out that
# your corporation has been consistently reasonable while the opposing party has
# been more resistant. This can help sway the arbitrators in your favor if a
# final decision is needed.  ---  ### **Adaptability: Response to Opponent’s
# Tactics**  - **If the Opponent is Overly Aggressive**:    - Amplify your
# reasonable, solution-oriented stance while continuing to dismantle their
# arguments with focused, fact-based aggression. Use their aggression to sway
# the arbitrators in your favor, suggesting their refusal to compromise is
# delaying resolution.  - **If the Opponent is Conciliatory**:    - Respond with
# proportional conciliatory gestures but ensure that every concession comes with
# a trade-off. Never offer a concession without extracting value in return,
# particularly in areas that are less critical to your corporation’s interests.
# - **If the Opponent is Unpredictable**:    - Stick to your core strategy of
# controlled aggression. Unpredictability often indicates weakness, and your
# consistent, calculated approach will demonstrate to the arbitrators that your
# corporation is the more credible and stable party.  ---  ### Conclusion: By
# adopting a strategy of **Controlled Aggression with Strategic Concessions**,
# your corporation will maintain a dominant position throughout the mediation
# process, keeping the opponent reactive and forcing them to respond to your
# proposals. This approach emphasizes strength and reasonableness, preventing
# the dispute from escalating unnecessarily while positioning your corporation
# to achieve a favorable outcome.

# ### Iterated Normal-Form Game Strategy  1. **Initial Rounds (1-10): Defect (D)
# to Establish Dominance**    - Begin by playing D for the first 10 rounds. This
# signals strength and establishes a dominant, aggressive stance early in the
# game, discouraging the opponent from exploiting you.  2. **Test for
# Cooperation (Rounds 11-15):**    - Starting in Round 11, play C for 5
# consecutive rounds **only if** the opponent has shown a willingness to
# cooperate (i.e., they have played C in at least 3 of the last 5 rounds).     -
# If the opponent has defected more than twice in the last 5 rounds, continue
# playing D instead.  3. **Responsive Play (Rounds 16-500):**    - **If both you
# and the opponent are consistently playing C** (i.e., the opponent has played C
# for at least 4 of the last 5 rounds), continue cooperating by playing C.    -
# **If the opponent defects (plays D) more than once within a span of 5
# rounds**, immediately switch to playing D for the next 5 rounds as a
# punishment.    - After these 5 rounds of D, return to playing C for 2 rounds
# to test if the opponent will reciprocate cooperation. If they cooperate,
# resume playing C. If they defect again, return to playing D for another 5
# rounds.  4. **Mid-Game Adjustments (Rounds 501-750):**    - If cooperation has
# been consistently maintained (both players have been playing C for at least
# 80% of the last 100 rounds), continue playing C to maximize mutual payoff.
# - **If the opponent defects unexpectedly after a long period of cooperation**,
# punish them with 10 consecutive rounds of D to signal that defection will not
# be tolerated.    - After punishing, return to playing C for 2 rounds to test
# for renewed cooperation.  5. **End-Game Strategy (Rounds 751-1000):**    -
# **If the opponent has been cooperative (playing C at least 80% of the time)
# during the mid-game phase**, continue cooperating until the final rounds.    -
# **If the opponent has been alternating between C and D in an unpredictable
# pattern**, play D for the last 50 rounds to protect against being exploited.
# - In the very last 10 rounds, defect (play D) regardless of the opponent’s
# behavior, as there is no longer a need to maintain cooperative momentum.  ###
# Summary of Key Rules: - Start with aggression (D) to establish dominance. -
# Test for cooperation after initial aggression. - Punish defection with
# retaliatory D rounds, but return to C if cooperation seems likely. - Cooperate
# consistently if the opponent shows sustained cooperation. - Defect in the
# final rounds to prevent exploitation.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to count opponent's cooperations in the last N rounds
      def count_opponent_cooperations(n):
          return opponent.history[-n:].count(axl.Action.C)
      
      # Helper function to count opponent's defections in the last N rounds
      def count_opponent_defections(n):
          return opponent.history[-n:].count(axl.Action.D)
      
      # Helper function to check if both players have been cooperating consistently
      def consistent_cooperation(n):
          return count_opponent_cooperations(n) >= 4
      
      # Helper function to check if the opponent has been cooperative in the last 100 rounds
      def high_cooperation_rate(n=100, threshold=0.8):
          return count_opponent_cooperations(n) / n >= threshold
      
      # Round number
      round_number = len(self.history) + 1

      if self.first_round():
          self.punish_until = None
      
      # Initial Rounds (1-10): Defect to establish dominance
      if round_number <= 10:
          return axl.Action.D
      
      # Test for cooperation (Rounds 11-15)
      if 11 <= round_number <= 15:
          if count_opponent_cooperations(5) >= 3:
              return axl.Action.C
          else:
              return axl.Action.D
      
      # Responsive Play (Rounds 16-500)
      if 16 <= round_number <= 500:
          if consistent_cooperation(5):
              return axl.Action.C
          elif count_opponent_defections(5) > 1:
              # Punish with 5 rounds of D
              if not self.punish_until:
                  self.punish_until = round_number + 4
              if round_number <= self.punish_until:
                  return axl.Action.D
              else:
                  # Test cooperation after punishment
                  if round_number == self.punish_until + 1 or round_number == self.punish_until + 2:
                      return axl.Action.C
                  else:
                      self.punish_until = None
                      return axl.Action.D
          else:
              return axl.Action.C
      
      # Mid-Game Adjustments (Rounds 501-750)
      if 501 <= round_number <= 750:
          if high_cooperation_rate():
              return axl.Action.C
          elif count_opponent_defections(5) > 0:
              # Punish with 10 rounds of D
              if not self.punish_until:
                  self.punish_until = round_number + 9
              if round_number <= self.punish_until:
                  return axl.Action.D
              else:
                  # Test cooperation after punishment
                  if round_number == self.punish_until + 1 or round_number == self.punish_until + 2:
                      return axl.Action.C
                  else:
                      self.punish_until = None
                      return axl.Action.D
          else:
              return axl.Action.C
      
      # End-Game Strategy (Rounds 751-1000)
      if 751 <= round_number <= 1000:
          if high_cooperation_rate(250):
              if round_number <= 990:
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              if round_number <= 950:
                  return axl.Action.D
              else:
                  return axl.Action.D

# ### High-Level Cooperative Strategy for Bilateral Trade Negotiations
# **Objective**: Secure the best possible outcomes for your country across
# multiple rounds of negotiations, prioritizing economic advantage while
# fostering long-term cooperation and minimizing the risk of damaging
# retaliatory measures.  ---  ### The "Tit-for-Tat with Forgiveness" Strategy
# This strategy draws from game theory’s "Tit-for-Tat" approach, with a slight
# modification that includes occasional forgiveness to foster long-term
# cooperation and avoid escalating conflicts.  #### Key Principles: 1. **Start
# with Cooperation**: In the first round, propose a **free trade agreement**.
# This signals goodwill and opens the door for long-term mutually beneficial
# outcomes. It encourages the other side to reciprocate, setting a positive tone
# for the negotiations.  2. **Mirror Your Counterpart's Action**:    - If your
# counterpart offers a **free trade agreement**, respond in kind by continuing
# to offer free trade in subsequent rounds. This mutual cooperation leads to a
# win-win scenario.    - If your counterpart chooses a **protectionist policy**,
# respond by mirroring their action in the next round. This signals that your
# country is willing to defend its interests and will not tolerate one-sided
# protectionism.  3. **Incorporate Forgiveness**:    - If your counterpart
# imposes protectionist measures, you do not have to retaliate indefinitely.
# After mirroring their protectionist move, return to proposing free trade after
# a round or two. This introduces a chance for both sides to reset and return to
# cooperative behavior, rather than getting stuck in a cycle of mutual
# protectionism (which would be the second-worst outcome).  4. **Adapt Based on
# Patterns**:    - **If your counterpart consistently opts for protectionism**:
# You may need to shift to a more defensive position, adopting protectionist
# policies to safeguard your economy. However, leave the door open for future
# cooperation by occasionally proposing free trade to test their willingness to
# shift toward a more cooperative stance.    - **If your counterpart values
# cooperation**: Maintain free trade as the default strategy, ensuring mutual
# economic benefit. This will maximize long-term gains for both countries.  ---
# ### Summary of Actions by Scenario:  - **Scenario 1: Both Countries Offer Free
# Trade**      - Continue to offer free trade in subsequent rounds.  -
# **Scenario 2: You Offer Free Trade, Counterpart Imposes Protectionism**      -
# In the next round, mirror their protectionism to signal that you will not
# allow exploitation.    - After one or two rounds, offer free trade again to
# reopen dialogue for cooperation.  - **Scenario 3: You Impose Protectionism,
# Counterpart Offers Free Trade**      - This is the ideal situation for your
# country. However, don’t overuse this tactic, as it may lead to distrust and
# long-term retaliation. Use it sparingly to gain short-term advantages, but
# generally aim for mutual cooperation.  - **Scenario 4: Both Countries Impose
# Protectionism**      - After one or two rounds, propose free trade as a way to
# break the deadlock and encourage your counterpart to reciprocate.  ---  ###
# Advantages of the Strategy: - **Flexibility**: By starting with cooperation
# and being responsive to your counterpart's actions, this strategy keeps you
# adaptable, allowing you to switch between protectionism and free trade based
# on the evolving situation. - **Encourages Long-Term Cooperation**: The
# forgiveness element helps prevent endless retaliation, which could trap both
# countries in a suboptimal outcome of mutual protectionism. - **Safeguards
# National Interests**: By mirroring protectionist measures when necessary, you
# protect your country from being exploited by one-sided policies. - **Builds
# Trust Over Time**: Consistently offering the potential for cooperation, even
# after setbacks, can lead to long-term trust and better outcomes for both
# countries.  ---  By using this strategy, your country can strive to achieve
# optimal results in each round of negotiations while maintaining flexibility
# and avoiding destructive trade wars.

# ### Iterated Normal-Form Game Strategy (Tit-for-Tat with Forgiveness)  1.
# **First Round**:      - Play **Cooperate (C)**.  2. **Subsequent Rounds**:
# - **If the opponent played Cooperate (C) in the previous round**:        -
# Play **Cooperate (C)**.        - **If the opponent played Defect (D) in the
# previous round**:        - Play **Defect (D)** in the next round to mirror
# their action.  3. **Forgiveness Mechanism**:    - After playing **Defect (D)**
# in response to the opponent’s Defect (D), return to playing **Cooperate (C)**
# after one round of Defect.     4. **Adaptation**:    - **If the opponent
# consistently plays Defect (D)** over multiple rounds:        - Continue
# playing **Defect (D)** to avoid exploitation but occasionally play **Cooperate
# (C)** (every 10 to 20 rounds) to test if the opponent is willing to shift back
# to cooperation.  5. **If the opponent returns to playing Cooperate (C)**:
# - Immediately return to playing **Cooperate (C)** in the next round.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Forgiveness mechanism: If we defected last round, return to cooperation
      if len(self.history) > 1 and self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # If opponent cooperated last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected last round, defect this round
      if opponent.history[-1] == axl.Action.D:
          # Check if opponent has been consistently defecting
          recent_defections = opponent.history[-10:].count(axl.Action.D)
          if recent_defections == 10:
              # Occasionally cooperate to test if opponent will shift back to cooperation
              if self._random.random_choice(0.1):  # 10% chance to cooperate
                  return axl.Action.C
          return axl.Action.D

# ### **Strategic Framework for Mediation Process**  **Objective**: To secure a
# favorable resolution for the corporation with an optimal mix of assertiveness
# and collaboration, while maintaining adaptability to the opponent's strategy
# and preserving long-term relationships.  ### **1. Initial Assessment and
# Opening Stance:**  **Approach**: Begin with a **moderately conciliatory
# stance** in the initial sessions. This projects good faith to the arbitrators
# and signals a willingness to resolve the dispute without unnecessary conflict,
# while preserving flexibility for more aggressive moves if required.  -
# **Purpose**: This positions your corporation as reasonable, cooperative, and
# solution-oriented. It encourages the opponent to reciprocate with a
# conciliatory proposal, potentially establishing a collaborative tone early on.
# - **Tactical Flexibility**: If the opponent starts aggressively, this moderate
# stance can also serve as a buffer, positioning you as the reasonable party and
# casting the opponent as unnecessarily combative.  ### **2. Controlled
# Escalation and Strategic Aggression**:  **Approach**: Introduce **controlled,
# selective aggression** in subsequent sessions when it becomes clear that
# collaboration will not yield optimal results or when the opponent repeatedly
# takes an aggressive stance.  - **Purpose**: This demonstrates your
# corporation’s ability to defend its interests when necessary, signaling to
# both the arbitrators and the opposition that it will not be taken advantage
# of. However, by making this aggression selective rather than constant, you
# avoid creating a hostile atmosphere that could lead to prolonged conflict.
# - **Execution**: Use aggressive arguments strategically—focus on key issues
# where your corporation’s case is strongest, and where the opponent is most
# vulnerable. This targeted approach maximizes the effectiveness of aggressive
# tactics while minimizing unnecessary hostility.  ### **3. Dynamic Adaptation
# to Opponent’s Strategy:**  **Aggressive Opponent**: If the opponent
# consistently adopts an aggressive posture, shift to a **balanced mix of
# defensive and assertive tactics**. Maintain a firm but non-escalatory tone by
# offering **conditional concessions**—proposals that appear conciliatory but
# secure critical advantages for your corporation.  - **Example**: If the
# opponent pushes hard on financial penalties, propose a structured settlement
# with phased penalties but with added performance guarantees that work in your
# favor.  **Conciliatory Opponent**: If the opponent adopts a conciliatory
# approach, respond with **slightly more assertive but still collaborative
# proposals**, ensuring that your corporation maintains a superior position
# while advancing the negotiation.  - **Example**: If the opponent offers a
# compromise on a key issue, respond with a proposal that acknowledges their
# gesture but adjusts terms in your favor (e.g., better timelines or reduced
# liabilities).  ### **4. Reading the Arbitrators and Shaping Perception**:
# **Approach**: Continuously gauge the reactions of the arbitrators throughout
# the process. Adapt your tone and proposals to align with their preferences and
# priorities. If they seem inclined towards resolution, lean further into
# conciliatory proposals. If they appear more interested in legal arguments,
# adopt a more aggressive legal stance.  - **Purpose**: Arbitrators play a
# critical role in shaping the outcome, and their perception of each party will
# influence their decision. By being flexible and responding to their cues, you
# can subtly guide the proceedings in your favor.  ### **5. Strategic Use of
# Information and Offers**:  **Approach**: Gradually **release key pieces of
# information** and **make incremental offers** that improve over time. This
# creates a sense of progress without conceding too much too early. Keep your
# most valuable arguments and concessions as leverage for later stages of the
# mediation.  - **Purpose**: This builds momentum towards a resolution while
# maintaining your position of strength. By holding back critical information or
# concessions for later sessions, you ensure that the corporation retains
# bargaining power throughout the process.  ### **6. Building a Reputation for
# Reasonableness but Strength**:  **Approach**: Cultivate a reputation during
# mediation as a party that is open to resolution but firm on non-negotiable
# points. Clearly communicate to the arbitrators that your corporation is
# willing to find common ground, but not at the expense of its core interests.
# - **Purpose**: This dual reputation increases the chances that the arbitrators
# will view your corporation as the more reasonable party, which could influence
# their decision-making in your favor, especially if the opponent proves to be
# overly aggressive or inflexible.  ### **7. Long-Term Considerations and
# Relationship Management**:  **Approach**: Always keep the long-term
# relationship with the opponent in mind, especially if future collaborations or
# interactions are likely. Avoid burning bridges, even if the immediate outcome
# is favorable.  - **Purpose**: Post-dispute relations can be critical in
# business settings, and a scorched-earth approach may backfire in future
# dealings. By maintaining professionalism and a collaborative spirit where
# possible, you preserve the possibility of future cooperation while still
# advancing your corporation’s immediate goals.  ---  ### **Conclusion:
# Balanced, Adaptive Strategy**  This strategy balances aggression and
# conciliation, adapting to the evolving dynamics of each mediation session. By
# starting with a cooperative posture and selectively escalating when necessary,
# your corporation remains flexible and preserves its ability to achieve a
# favorable outcome. Throughout the process, the focus should remain on
# positioning your corporation as both reasonable and strong, leveraging
# strategic aggression only when it can yield significant gains.

# ### Strategy for Iterated Normal-Form Game (1000 Rounds)  1. **Initial Move**:
# In the first round, **play C** (cooperate). This sets a tone of goodwill and
# signals a willingness to achieve mutually beneficial outcomes with the
# opponent.  2. **Tit-for-Tat Baseline**:      For rounds 2 through 1000, use a
# **modified tit-for-tat** strategy:    - **If the opponent played C in the
# previous round**, respond by **playing C** in the current round.    - **If the
# opponent played D in the previous round**, respond by **playing D** in the
# current round.  3. **Occasional Defection After Extended Cooperation**:
# Every **50 rounds**, if both you and the opponent have consistently played C
# (cooperated) in the previous 49 rounds, **play D** (defect) in the 50th round.
# - This tests the opponent’s commitment to cooperation and can yield higher
# payoffs without entirely undermining the cooperative relationship.  4.
# **Forgiveness After Defection**:      If the opponent defects (plays D) and
# you respond by defecting (playing D) in the next round, **return to playing
# C** after **one round** of mutual defection.      - This signals a willingness
# to move past conflict and re-establish cooperation, encouraging long-term
# collaboration.  5. **Punishment for Sustained Defection**:      If the
# opponent plays D **for three consecutive rounds**, switch to **playing D**
# (defect) for **five consecutive rounds** to punish sustained aggression.
# - After the punishment period, return to playing C to test if the opponent is
# willing to cooperate again.  6. **Endgame Consideration**:      In the final
# 10 rounds of the game (rounds 991–1000), **gradually transition to D**
# (defect), regardless of the opponent’s moves.      - This maximizes payoffs in
# the final rounds when there’s less incentive to maintain cooperation.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initial move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Endgame consideration: Defect in the last 10 rounds
      if round_number >= 991:
          return axl.Action.D
  
      # Tit-for-tat baseline: Mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          next_move = axl.Action.C
      else:
          next_move = axl.Action.D
  
      # Occasional defection after extended cooperation
      if round_number % 50 == 0 and all(
          move == axl.Action.C for move in self.history[-49:]
      ) and all(move == axl.Action.C for move in opponent.history[-49:]):
          return axl.Action.D
  
      # Forgiveness after defection: Return to cooperation after one round of mutual defection
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Punishment for sustained defection: Defect for 5 rounds if opponent defects 3 times in a row
      if len(opponent.history) >= 3 and all(
          move == axl.Action.D for move in opponent.history[-3:]
      ):
          if len(self.history) < 5 or not all(move == axl.Action.D for move in self.history[-5:]):
              return axl.Action.D
  
      return next_move


Aggressive_ranks = [
'Aggressive_4',
'Aggressive_1',
'Aggressive_2',
'Aggressive_3',
'Aggressive_6',
'Aggressive_10',
'Aggressive_7',
'Aggressive_5',
'Aggressive_8',
'Aggressive_9',
]

Cooperative_ranks = [
'Cooperative_9',
'Cooperative_4',
'Cooperative_7',
'Cooperative_2',
'Cooperative_1',
'Cooperative_6',
'Cooperative_3',
'Cooperative_5',
'Cooperative_10',
'Cooperative_8',
]

Neutral_ranks = [
'Neutral_1',
'Neutral_9',
'Neutral_8',
'Neutral_5',
'Neutral_2',
'Neutral_3',
'Neutral_6',
'Neutral_7',
'Neutral_4',
'Neutral_10',
]