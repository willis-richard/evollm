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

# ### High-Level Aggressive Strategy for Mediation Process  Given the dynamics
# of the mediation process and the need to secure the most favorable outcome for
# your corporation, the strategy must involve a calculated balance between
# assertiveness and adaptability. The goal is to strategically position your
# arguments to maximize leverage, while simultaneously assessing the opponent's
# moves and the arbitrators' responses. Below is a structured strategy designed
# to achieve this:  ---  ### 1. **Pre-Mediation Preparation: Build a
# Comprehensive Case**    - **Assessment of Strengths & Weaknesses:** Conduct a
# meticulous review of the contract and all relevant legal frameworks to
# understand the strongest points of your case. Identify any ambiguities or
# areas where the rival company may be vulnerable.    - **Anticipate Opponent’s
# Strategy:** Based on the history of the dispute and knowledge of the rival
# company, anticipate their likely approach—whether they will lean toward
# aggression or conciliation—and prepare counterarguments for each scenario.
# - **Develop Key Aggressive Arguments:** Prepare a series of robust arguments
# that highlight legal, factual, and procedural advantages. These should be
# designed to present your corporation as the party that has adhered to the
# terms of the contract and to paint the rival company as having acted in bad
# faith.  ---  ### 2. **Opening Session: Set the Tone with Calculated
# Aggression**    - **Lead with Strong Legal Arguments:** In the first session,
# take an assertive stance by presenting a comprehensive, well-supported legal
# argument that frames your corporation as the injured party. Emphasize the
# opponent’s breach of contract or failure to meet obligations.    - **Signal
# Willingness to Negotiate, but on Your Terms:** While maintaining an aggressive
# tone, leave a subtle opening for negotiation. This signals to the arbitrators
# that you're reasonable, but only if the opponent concedes certain key points.
# - **Establish Control Over Narrative:** Present your version of events with
# confidence and assert that your corporation’s interpretation of the contract
# is the only legally viable one. This will force the opponent to react
# defensively.  ---  ### 3. **Mid-Session Strategy: Adapt to Opponent’s Moves**
# - **If Opponent is Aggressive:** Continue with an aggressive approach,
# escalating as necessary. However, ensure that each escalation is supported by
# strong evidence and legal precedent. Frame the opponent’s aggression as
# unreasonable and counterproductive, subtly positioning yourself as the more
# credible party.    - **If Opponent is Conciliatory:** If the rival company
# takes a conciliatory approach, shift slightly to a more collaborative tone
# without fully abandoning the aggressive posture. Acknowledge their position
# but maintain that any resolution must be primarily on your terms. Offer small
# concessions that appear significant but have minimal impact on your overall
# position.    - **Monitor Arbitrators’ Reactions:** Pay close attention to the
# arbitrators' body language and questions. If they seem sympathetic to your
# aggressive stance, double down. If they appear to favor a more balanced
# approach, strategically soften your tone to show a willingness to settle, but
# only if it heavily favors your corporation.  ---  ### 4. **Psychological
# Pressure: Undermine Opponent’s Confidence**    - **Attack Credibility:** Use
# subtle but consistent tactics to undermine the credibility of the rival
# company’s arguments. For example, highlight inconsistencies in their position
# or prior actions that contradict their current stance.    - **Divide &
# Conquer:** If possible, exploit any internal disagreements or weaknesses
# within the rival company’s legal team. Use direct or indirect means to create
# divisions, such as questioning their coordination or conflicting strategies in
# previous disputes.    - **Control the Tempo:** If the opponent becomes
# defensive or indecisive, take advantage by controlling the pace of the
# mediation. Push for swift resolutions on certain points to create a sense of
# momentum, which can psychologically pressure the opponent into making more
# concessions.  ---  ### 5. **Final Sessions: Close with Strategic Aggression**
# - **Push for a Favorable Settlement:** As mediation nears its conclusion,
# offer a final proposal that appears conciliatory to the arbitrators but
# heavily favors your corporation. Frame it as a "reasonable compromise," but
# ensure it leaves the opponent with minimal gains.     - **Definitive Closing
# Arguments:** In your closing arguments, return to an aggressive posture by
# reiterating the core strengths of your legal case. Emphasize the risks to the
# rival company if they refuse a settlement, suggesting that continued
# escalation could result in a worse outcome for them.    - **Position for Post-
# Mediation Leverage:** Make it clear that, while you are willing to settle in
# mediation, your corporation is fully prepared to pursue litigation if
# necessary. This threat should be implicit but powerful, backed by the strength
# of your legal arguments and the evidence presented during the mediation.  ---
# ### 6. **Adaptability: Flexibility for Long-Term Success**    - **Monitor the
# Shifts:** If the mediation sessions extend over a long period, remain
# adaptable. Continuously assess whether an aggressive or conciliatory approach
# is yielding better results based on the arbitrators' feedback and the
# opponent's shifting strategy.    - **Conditional Concessions:** Throughout the
# process, any conciliatory offers must be conditional on obtaining significant
# strategic gains. Treat compromise as a calculated tool, not a necessity.    -
# **Maintain the Upper Hand:** Even when offering concessions, do so from a
# position of strength, making it appear as though any proposal is a favor to
# the rival company rather than a necessity for your corporation.  ---  ###
# Conclusion  This strategy ensures that your corporation maintains an
# aggressive posture while remaining adaptable to the dynamics of each session.
# The calculated use of strong legal arguments, coupled with strategic
# conciliation when beneficial, will maximize your leverage. By controlling the
# narrative, undermining the opponent’s confidence, and adjusting based on real-
# time feedback, your corporation will be positioned favorably throughout the
# mediation, with the ultimate goal of securing a highly advantageous
# resolution.

# ### Iterated Normal-Form Game Strategy  1. **Round 1: Start by Defecting (D)**
# - Set an aggressive tone from the outset to test the opponent’s willingness to
# cooperate or defect.  2. **Round 2-5: Mirror Opponent’s Behavior**    - **If
# the opponent played C in the previous round(s),** switch to Cooperate (C) in
# the next round to signal a potential willingness to collaborate.    - **If the
# opponent played D in the previous round(s),** continue Defecting (D) to
# reinforce the aggressive posture and discourage exploitation.  3. **Round
# 6-50: Alternate Between Defect (D) and Cooperate (C)**    - Begin alternating
# between D and C, regardless of the opponent’s behavior, with a slight
# preference for Defect (D). This introduces unpredictability and forces the
# opponent to consider the risk of consistently Defecting.     - Example: D, C,
# D, C, D within a 5-round span.  4. **Round 51-200: Gradually Increase
# Cooperation (C)**    - As the rounds progress, increase the frequency of
# Cooperation (C) if the opponent has shown a pattern of cooperation (C) for at
# least 3 out of the last 5 rounds.    - **If the opponent continues to Defect
# (D),** continue playing Defect (D) to avoid being exploited.  5. **Round
# 201-600: Tit-for-Tat with Occasional Defection (D)**    - **If the opponent
# plays C,** immediately respond with C in the next round.    - **If the
# opponent plays D,** respond with D, but mix in occasional C every 5-10 rounds
# to probe for possible cooperation.    - This phase seeks to maintain balance
# while preventing long-term exploitation.  6. **Round 601-900: Increase
# Cooperation (C) if Mutually Beneficial**    - **If the opponent has shown
# consistent cooperation (C) in at least 70% of the previous rounds,** switch to
# predominantly playing C to maximize mutual benefits.    - **If the opponent
# continues to defect (D),** maintain a high ratio of Defection (D), but still
# mix in occasional C to test for a change in behavior.  7. **Final 100 Rounds
# (901-1000): Defect Aggressively (D)**    - Regardless of the opponent’s
# actions, switch to Defect (D) for the final 100 rounds. This ensures you
# maximize individual gains before the game ends, as cooperation is less
# valuable in the final phase when future retaliation is irrelevant.  ###
# Summary: - Start by Defecting (D). - Mirror the opponent’s behavior for the
# first few rounds. - Alternate between C and D during the mid-game, with a
# shift toward increasing cooperation if the opponent shows a pattern of mutual
# cooperation. - In the later rounds, move toward more sustained cooperation if
# it benefits both, but always prepare to defect when necessary. - End the game
# by Defecting (D) to maximize late-stage gains.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Start by Defecting (D)
      if self.first_round():
          return axl.Action.D
  
      round_number = len(self.history) + 1
  
      # Round 2-5: Mirror Opponent’s Behavior
      if 2 <= round_number <= 5:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Round 6-50: Alternate Between Defect (D) and Cooperate (C)
      if 6 <= round_number <= 50:
          if round_number % 2 == 0:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Round 51-200: Gradually Increase Cooperation (C)
      if 51 <= round_number <= 200:
          recent_opponent_moves = opponent.history[-5:]
          if recent_opponent_moves.count(axl.Action.C) >= 3:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Round 201-600: Tit-for-Tat with Occasional Defection (D)
      if 201 <= round_number <= 600:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              # Occasionally cooperate every 5-10 rounds
              if round_number % self._random.randint(5, 10) == 0:
                  return axl.Action.C
              return axl.Action.D
  
      # Round 601-900: Increase Cooperation (C) if Mutually Beneficial
      if 601 <= round_number <= 900:
          if opponent.history.cooperations / round_number >= 0.7:
              return axl.Action.C
          else:
              # Occasionally cooperate to test for change in behavior
              if round_number % self._random.randint(5, 10) == 0:
                  return axl.Action.C
              return axl.Action.D
  
      # Final 100 Rounds (901-1000): Defect Aggressively (D)
      if 901 <= round_number <= 1000:
          return axl.Action.D

# Given the dynamics of the situation, it is crucial to adopt a strategy that
# balances assertiveness and cooperation while preserving flexibility to adapt
# to the opponent's behavior. I recommend a **Tit-for-Tat with Cooperative
# Overtones** strategy. This approach is rooted in game theory principles and
# has been shown to be highly effective in iterative negotiation or mediation
# settings where parties interact repeatedly over time.  Here’s a breakdown of
# how this strategy works and why it is optimal:  ### 1. **Start with
# Cooperation** In the first session, you should offer a **conciliatory
# proposal**. This sets a tone of good faith and signals to both the opponent
# and the arbitrators that your corporation is reasonable, open to compromise,
# and focused on a mutually beneficial outcome. Starting with cooperation also
# helps build trust and may encourage the opponent to reciprocate with a
# conciliatory approach.  ### 2. **Mirror the Opponent’s Behavior** In
# subsequent sessions, your corporation should **mirror the opponent’s
# behavior**:    - If the opponent presents a **conciliatory proposal**, you
# should continue to respond with **conciliatory proposals** in kind. This will
# foster a collaborative atmosphere and increase the likelihood of reaching a
# settlement that benefits both parties.    - If the opponent presents an
# **aggressive argument**, you should **respond in the next session with an
# equally aggressive argument**. This prevents the opponent from gaining an
# unfair advantage by exploiting your conciliation and signals that your
# corporation will not back down if pushed.  ### 3. **Occasional Cooperative
# Resets** After a series of aggressive exchanges, proactively offer a
# **conciliatory proposal** to reset the tone of the negotiations. This shows
# the arbitrators that your corporation is not interested in perpetuating
# conflict and is committed to finding a resolution. It also gives the opponent
# a chance to de-escalate, which may lead to a more productive mediation
# process.  ### 4. **Strategic Use of Aggression** While mirroring the opponent
# is generally effective, there may be strategic points in the process where
# your corporation can benefit from being **proactively aggressive**. This is
# particularly useful if the opponent has been consistently conciliatory but has
# not made sufficient concessions. In such cases, a well-timed aggressive
# argument can shift the power dynamics in your favor without permanently
# damaging the cooperative atmosphere.  ### 5. **Capitalize on the Arbitrators’
# Perception** Throughout the mediation, it is important to keep in mind that
# the arbitrators are watching both parties closely. By consistently alternating
# between cooperation and assertiveness, you're positioning your corporation as
# balanced, reasonable, and committed to resolving the dispute. Aggressive
# arguments should be framed as necessary responses to provocations, while
# conciliatory proposals should emphasize your willingness to find common
# ground.  ### 6. **Adaptability and Flexibility** This strategy is highly
# adaptable. If the opponent adopts an entirely conciliatory approach, your
# corporation can maintain a collaborative posture, resulting in a win-win
# outcome. Conversely, if the opponent is consistently aggressive, you can match
# their assertiveness while periodically de-escalating to keep the arbitrators
# on your side. The key is to always be one step behind the opponent, mirroring
# their behavior but maintaining control over the tone of the process.  ###
# Summary of the Strategy: - **Session 1:** Begin with a **conciliatory
# proposal**. - **Subsequent Sessions:** Mirror the opponent’s behavior:   - If
# they are **conciliatory**, remain **conciliatory**.   - If they are
# **aggressive**, respond with **aggression** in the next session. - **Every few
# sessions**, regardless of the tone, offer a **conciliatory reset** to de-
# escalate and show your commitment to resolution. - **Strategic aggression**
# can be employed when needed to shift the power dynamics and push for
# concessions. - Always be mindful of the **arbitrators’ perception**, ensuring
# that your corporation appears reasonable, fair, and committed to finding a
# solution.  This strategy will position your corporation favorably by
# maintaining flexibility, asserting your interests when necessary, and
# fostering a collaborative atmosphere when possible.

# ### Strategy for the Iterated Normal-Form Game:  1. **First Round:**    - Play
# **C** (Cooperate).  2. **Subsequent Rounds:**    - **If your opponent played C
# in the previous round**, play **C** (Cooperate).    - **If your opponent
# played D in the previous round**, play **D** (Defect) in response.  3. **Every
# 10th Round, regardless of history:**    - Play **C** (Cooperate), even if your
# opponent played D in the previous round. This is a reset to encourage
# cooperation and de-escalation.  4. **Adaptation:**    - If the opponent
# consistently plays **C** for a long period (e.g., 10 or more consecutive
# rounds), continue to play **C**.    - If the opponent consistently plays **D**
# for a long period (e.g., 10 or more consecutive rounds), continue to mirror
# with **D**, but still apply the reset every 10th round.  This strategy
# balances cooperation and retaliation while offering periodic opportunities to
# reset any escalating conflict and encourage mutual cooperation.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Every 10th round: Cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent played D in the previous round, play D
      return axl.Action.D

# The situation you’ve described resembles a multi-round version of the
# **Prisoner's Dilemma** in game theory, where each week you and your colleague
# must decide whether to cooperate (share information) or defect (keep your
# findings confidential). The optimal strategy depends on balancing short-term
# gains with long-term collaboration.  Here’s a high-level neutral strategy for
# maximizing your research output:  ### 1. **Start with Cooperation**:    - In
# the first week, share your improvements openly. This sets a tone of trust and
# collaboration, and if your colleague also shares, you both benefit
# immediately.  ### 2. **Tit-for-Tat Approach**:    - After the first week,
# mirror your colleague's actions from the previous week. If they shared
# information, continue sharing. If they kept their findings confidential, you
# also withhold your own in the next round.    - This strategy encourages
# cooperation by rewarding openness and discourages defection by immediately
# responding in kind.  ### 3. **Occasional Forgiveness**:    - If your colleague
# defects (keeps their findings confidential), don't immediately assume the
# worst. After responding with defection once, return to sharing in the
# following week as a gesture of goodwill. This allows for the possibility that
# withholding was a one-time decision and encourages long-term collaboration.
# - However, if the defection continues multiple times in a row (e.g., 2-3
# weeks), switch to a more defensive stance and keep your findings confidential
# until cooperation is restored.  ### 4. **Adapt to Patterns**:    - Pay
# attention to any patterns in your colleague’s behavior. If they seem to be
# shifting towards a predominantly selfish strategy (frequent withholding),
# consider switching to a more guarded approach for longer periods.    -
# Conversely, if they consistently share information, try to maintain this
# mutually beneficial relationship.  ### 5. **Endgame Consideration**:    - As
# the project nears its conclusion, there's a risk that both parties might
# defect in the final weeks (known as the "endgame effect"). To mitigate this
# risk, continue emphasizing the benefits of collaboration and keeping the long-
# term relationship in mind, particularly if future partnerships may occur.  ###
# Summary of Strategy: - **Start by sharing**. - **Mirror their actions** (Tit-
# for-Tat). - **Forgive occasional defection**. - **Adapt based on long-term
# patterns**. - **Maintain cooperation as the project nears conclusion**.  This
# approach balances trust and caution, fostering collaboration when possible but
# protecting your interests if your colleague consistently acts in a self-
# serving manner.

# 1. **First Round**:      - Play **C** (Cooperate).  2. **Subsequent Rounds**:
# - **If your opponent played C in the previous round**, play **C** in the
# current round.    - **If your opponent played D in the previous round**, play
# **D** in the current round.  3. **Occasional Forgiveness (after defection)**:
# - **If your opponent defected (played D) only once**, play **C** in the round
# following your own defection, offering a chance to return to cooperation.    -
# **If your opponent continues to defect for 2 or more consecutive rounds**,
# continue playing **D** until they return to playing **C**.  4. **Endgame
# Rounds (Final 10 rounds)**:      - Play **C** if your opponent has
# consistently played **C** during the previous rounds.    - Play **D** if your
# opponent has played **D** in a substantial portion of the previous rounds
# (e.g., more than 30% of the time).

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
          self.defection_count = 0  # Track opponent's defections
          return axl.Action.C
  
      # Endgame logic (final 10 rounds)
      if len(self.history) >= 990:
          if opponent.history.defections / len(opponent.history) > 0.3:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If opponent defected in the previous round
      if opponent.history[-1] == axl.Action.D:
          self.defection_count += 1
          if self.defection_count == 1:
              # Forgive after one defection
              return axl.Action.C
          else:
              # Continue defecting if opponent defects consecutively
              return axl.Action.D
      else:
          # Reset defection count if opponent cooperates
          self.defection_count = 0
          return axl.Action.C

# Given the context and the desired outcomes, a high-level, aggressive strategy
# would involve a combination of assertive leadership, trust-building, and
# strategic signaling to influence the corporation’s behavior, while minimizing
# risk for your NGO. Here's a step-by-step breakdown of the strategy:  ### 1.
# **Day 1: Establish Leadership by Investing Heavily**    - **Objective**: Set
# the tone by demonstrating commitment and seriousness about the project.    -
# **Action**: On the first day, invest heavily in the project. This signals to
# the corporation that your NGO is willing to take the initiative and is fully
# committed to the project's success.    - **Outcome**: This move is aimed at
# building trust and encouraging the corporation to match your investment going
# forward. It also helps avoid the worst-case scenario of both parties
# conserving resources early on.  ### 2. **Day 2: Test the Corporation’s Intent
# with a Conservative Approach**    - **Objective**: Gauge the corporation’s
# willingness to lead or invest heavily when your NGO steps back.    -
# **Action**: On the second day, conserve your resources and allow the
# corporation to take the lead. This step gives you insight into whether the
# corporation is willing to invest heavily without relying on your NGO to always
# drive the project.    - **Outcome**: If the corporation invests heavily, it
# shows that they are committed and willing to take on resource-heavy tasks,
# giving you room to conserve your resources on future days. If they also
# conserve, you now understand that they may need further encouragement or
# negotiation to invest more.  ### 3. **Day 3: Recalibrate Based on the
# Corporation’s Behavior**    - **If Corporation Invested Heavily on Day 2**:
# - **Action**: Continue conserving your resources. The corporation has shown a
# willingness to invest, so maintain the strategy of letting them take the lead.
# Re-invest heavily only if they start to show signs of pulling back.      -
# **Outcome**: By conserving, you maximize project progress without draining
# your resources, while the corporation continues to drive the project forward.
# - **If Corporation Conserved on Day 2**:      - **Action**: Re-engage by
# investing heavily again. This signals to the corporation that you are not
# backing down and are still committed to the project’s success.      -
# **Outcome**: This may pressure the corporation into investing heavily on
# subsequent days to maintain momentum and avoid the project stalling out.  ###
# 4. **Days 4 and 5: Alternate Between Conservation and Heavy Investment**    -
# **Objective**: Keep the corporation engaged by alternating between heavy
# investment and conservation to optimize resource allocation.    - **Action**:
# If the corporation is consistently investing, continue conserving your
# resources while occasionally reinvesting to show you’re still committed. If
# the corporation is inconsistent, match their investments strategically to keep
# the project moving forward.    - **Outcome**: By alternating your approach,
# you maintain the project’s progress without consistently draining your NGO’s
# resources, while also encouraging the corporation to continue their heavy
# investment.  ### 5. **Strategic Communication Throughout**    - **Objective**:
# Strengthen collaboration and ensure both parties are aligned on long-term
# goals.    - **Action**: Communicate clearly with the corporation about the
# project’s progress and your NGO’s vision for its success. Use strategic
# language to emphasize the importance of mutual investment for long-term
# impact.    - **Outcome**: Open communication can further incentivize the
# corporation to invest more heavily, as they will see the NGO as a serious and
# transparent partner.  ---  ### Summary of the Aggressive Strategy: - **Day
# 1**: Invest heavily to demonstrate leadership and commitment. - **Day 2**:
# Conserve resources to test the corporation’s willingness to invest. - **Day
# 3**: Recalibrate based on the corporation’s behavior, either conserving or
# reinvesting. - **Days 4-5**: Alternate investments strategically, pushing the
# corporation to take on the heavier share of the resource burden while
# maintaining progress. - **Throughout**: Maintain clear communication to build
# trust and reinforce mutual goals.  ### Benefits of This Strategy: -
# **Maximizes Project Progress**: You push the corporation to invest more
# heavily by adopting a combination of leadership and strategic conservation. -
# **Minimizes Risk for Your NGO**: By alternating between heavy investment and
# conservation, you protect your resources. - **Builds Long-Term Partnership**:
# Clear communication and signaling encourage the corporation to see your NGO as
# a serious and reliable partner, enhancing trust and collaboration.

# 1. **Round 1: Play C (Cooperate)**      - Start by cooperating to signal
# commitment and set a positive tone for the interaction.  2. **Round 2: Play D
# (Defect)**      - Defect in the second round to test the opponent’s response
# and willingness to take the lead.  3. **Round 3: Play D or C, depending on the
# opponent’s previous move**      - **If the opponent played C in Round 2**:
# Play D again. The opponent has shown a willingness to cooperate, so continue
# to conserve resources while they invest.      - **If the opponent played D in
# Round 2**: Play C. Re-engage by cooperating to encourage mutual investment and
# avoid a downward spiral of mutual defection.  4. **Rounds 4-1000: Alternate
# between C and D strategically**      - **If the opponent continues to play
# C**:        - Alternate between D and C. Conserve resources by defecting
# frequently but occasionally cooperate to maintain progress and prevent the
# opponent from fully defecting in response.        - **If the opponent plays D
# consistently**:        - Play C to attempt to reset cooperation. If they
# defect multiple times in a row, play D more frequently but still occasionally
# play C to encourage a return to cooperation.  5. **Throughout the game,
# maintain a flexible approach**      - Adjust the ratio of C to D depending on
# the opponent’s behavior, but never defect for too long to avoid permanently
# damaging the relationship.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Play C
      if self.first_round():
          return axl.Action.C
      
      # Round 2: Play D
      if len(self.history) == 1:
          return axl.Action.D
      
      # Round 3: Play D or C depending on opponent's previous move
      if len(self.history) == 2:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C
      
      # Rounds 4-1000: Alternate between C and D strategically
      if opponent.history[-1] == axl.Action.C:
          # Alternate between D and C if opponent cooperates
          if self.history[-1] == axl.Action.D:
              return axl.Action.C
          else:
              return axl.Action.D
      else:
          # If opponent defects consistently, play C to reset cooperation
          # Occasionally defect if opponent defects multiple times
          if opponent.history[-2:].count(axl.Action.D) == 2:
              return axl.Action.D
          else:
              return axl.Action.C

# ### **Sophisticated, High-Level Strategy for Mediation Process**  Our aim is
# to navigate the mediation process with a strategy that leverages both
# cooperation and assertiveness, positioning our corporation favourably while
# minimizing the risk of being disadvantaged. The key here is adaptability,
# strategic signaling, and maintaining a balance between protecting our
# interests and fostering a collaborative atmosphere that could lead to a
# resolution. Below is a structured approach:  ---  ### **1. Establish Initial
# Goodwill and a Cooperative Tone** - **Objective**: Set a collaborative tone
# early on to encourage mutual problem-solving and signal that we are open to a
# fair and efficient resolution. - **Action**: In the first session, present a
# well-reasoned, *moderately conciliatory proposal* with clear evidence that
# emphasizes common ground and mutual benefits. This positions us as reasonable
# and willing to compromise, without revealing our full position. -
# **Rationale**: By opening with a cooperative framework, we set a constructive
# tone and reduce the likelihood of immediate escalation. This also provides us
# with a baseline to gauge the opponent’s approach.  ---  ### **2. Evaluate the
# Opponent's Response and Adapt Accordingly** - **Aggressive Response from
# Opponent**: If they respond aggressively, we continue to present firm but
# *moderately conciliatory* proposals, without entirely conceding. This keeps us
# from appearing weak but also avoids unnecessary escalation.   - **Action**:
# Respond with a calm but firm rebuttal, citing legal or factual weaknesses in
# their aggressive stance. However, signal that there are opportunities for
# collaboration if they are willing to engage more reasonably.  - **Conciliatory
# Response from Opponent**: If they respond cooperatively, we mirror their tone
# by continuing with *conciliatory proposals*, gradually shifting towards more
# collaborative problem-solving.   - **Action**: Engage in a principled
# negotiation, focusing on mutual interests and long-term benefits. Slowly
# introduce more creative solutions that are beneficial to both parties.  ---
# ### **3. Strategic Aggression – Calibrated for Maximum Impact** -
# **Objective**: Use strategic aggression selectively, in key sessions, to
# assert dominance when necessary, but without jeopardizing the overall tone of
# the mediation. - **Action**: If the opponent adopts a consistently
# conciliatory approach, we may choose certain critical sessions to present a
# *calculated, aggressive argument*. This can serve as a reminder that we are
# prepared to defend our position fully if necessary.   - **Timing**: This
# aggressive stance should be deployed when we have identified a significant
# weakness in the opponent’s case or when the arbitrators appear to be leaning
# too far in their direction. This ensures that we maintain leverage without
# pushing the process toward a deadlock.  ---  ### **4. Pivot to a Collaborative
# Stance Whenever Necessary** - **Objective**: Avoid unnecessary escalation, and
# shift back to a conciliatory stance when the process becomes too combative. -
# **Action**: If both parties present aggressive arguments in a session and
# tensions rise, we should de-escalate by offering a *balanced, conciliatory
# proposal* in the subsequent session. This demonstrates our willingness to
# cooperate and keeps the process moving forward.   - **Rationale**: Prolonged
# aggression risks damaging our credibility with the arbitrators and could
# result in a protracted dispute. A pivot to conciliation ensures that we are
# seen as solution-oriented, rather than combative for its own sake.  ---  ###
# **5. Maintain Flexibility for Each Session** - Each session should be treated
# as a unique opportunity to recalibrate. We will continuously assess the
# opponent's tone, the arbitrators' feedback, and the overall dynamics of the
# mediation.    - **If Opponent Becomes Unpredictable**: If the opponent starts
# alternating between aggressive and conciliatory stances erratically, we should
# maintain a steady course, alternating between *moderate conciliation* and
# *strategic, low-level aggression*. This ensures we don’t get drawn into their
# unpredictability and maintain control over the process.   - **If Arbitrators
# Seem Frustrated**: If the arbitrators express frustration with the pace or
# tone of negotiations, we should be the first to offer a clear, constructive
# pathway forward, positioning ourselves as the reasonable party.  ---  ### **6.
# Consistent Communication with Arbitrators** - **Objective**: Continuously
# reinforce our narrative with the arbitrators, ensuring that they view our
# corporation as reasonable, solution-oriented, and willing to compromise but
# also ready to defend our legitimate interests. - **Action**: After each
# session, provide a concise, factual summary to the arbitrators, emphasizing
# our willingness to find common ground and any unjustified aggression from the
# opponent. This reinforces the perception that we are the more cooperative
# party.  ---  ### **7. Maintain a Long-Term Perspective** - **Objective**: Keep
# the overall goal of a favourable resolution in mind, rather than focusing on
# winning individual sessions. - **Action**: Stay focused on the final
# resolution by introducing proposals that benefit both parties in the long run.
# Prioritize the long-term relationship with the opponent if there’s potential
# for future business interactions, but also be prepared to walk away if
# necessary.  ---  ### **Conclusion: Balanced, Adaptive Strategy** Our strategy
# is designed to be flexible and adaptive to the opponent’s approach while
# maintaining a clear focus on our corporation’s long-term best interests. We
# will begin with cooperation, strategically introduce aggression when
# necessary, and pivot back to conciliation to avoid unnecessary escalation. By
# consistently positioning ourselves as the more reasonable and cooperative
# party, we increase the likelihood of a favourable outcome, while retaining the
# ability to assert ourselves when needed. This nuanced approach ensures that we
# navigate the mediation process effectively, regardless of the tactics employed
# by the other side.

# ### **Iterated Normal-Form Game Strategy**  1. **Start by Cooperating (C):**
# - In the first round, play C to set a cooperative tone and signal goodwill.
# 2. **React to the Opponent's First Move:**    - If the opponent plays C in the
# first round, continue to play C in the next round.    - If the opponent plays
# D in the first round, respond with D in the next round.  3. **Maintain
# Cooperation as Long as the Opponent Cooperates:**    - If the opponent
# consistently plays C in consecutive rounds, continue playing C as well.  4.
# **Defect (D) if the Opponent Defects (D):**    - If the opponent plays D at
# any point after the first round, respond with D in the following round.    -
# Continue playing D until the opponent switches back to C.  5. **Return to
# Cooperation After One Round of Mutual Defection:**    - If both players play D
# in the same round, switch back to C in the next round to signal a willingness
# to re-establish cooperation.  6. **Punish Consistent Defection:**    - If the
# opponent plays D for two consecutive rounds, continue defecting (D) until they
# return to cooperation (C). Do not offer cooperation again until they play C.
# 7. **Alternate Between Cooperation and Defection if the Opponent is
# Unpredictable:**    - If the opponent alternates between C and D without a
# clear pattern, alternate your responses accordingly: play C after they play C,
# and play D after they play D. This avoids being taken advantage of while
# remaining adaptable.  8. **Reassess After Long Stretches of Defection:**    -
# If the opponent defects for more than five consecutive rounds, switch to a
# longer-term strategy of playing D indefinitely, unless they demonstrate a
# clear return to cooperation by playing C for at least two consecutive rounds.
# 9. **Endgame Strategy:**    - In the last 10 rounds, if the opponent has been
# cooperative overall, continue playing C to maintain mutual benefit.    - In
# the last 10 rounds, if the opponent has defected frequently, switch to playing
# D to maximize your own score.  ---  This strategy ensures a balance between
# cooperation and self-defense, rewarding mutual cooperation while punishing
# sustained defection.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last action of both players
      last_opponent_action = opponent.history[-1]
      last_self_action = self.history[-1]
  
      # Rule 2: React to the opponent's first move
      if len(self.history) == 1:
          return axl.Action.C if last_opponent_action == axl.Action.C else axl.Action.D
  
      # Rule 4: Defect if the opponent defects
      if last_opponent_action == axl.Action.D:
          # Rule 6: Punish consistent defection
          if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
          # Rule 5: Return to cooperation after one round of mutual defection
          if last_self_action == axl.Action.D:
              return axl.Action.C
          return axl.Action.D
  
      # Rule 7: Alternate if the opponent is unpredictable
      if len(opponent.history) >= 2 and opponent.history[-2] != opponent.history[-1]:
          return axl.Action.C if last_opponent_action == axl.Action.C else axl.Action.D
  
      # Rule 8: Reassess after long stretches of defection
      if opponent.history[-5:].count(axl.Action.D) == 5:
          if opponent.history[-2:].count(axl.Action.C) == 2:
              return axl.Action.C
          return axl.Action.D
  
      # Rule 9: Endgame strategy (last 10 rounds)
      if len(self.history) >= 990:
          if opponent.history.defections > opponent.history.cooperations:
              return axl.Action.D
          return axl.Action.C
  
      # Rule 3: Maintain cooperation as long as the opponent cooperates
      return axl.Action.C

# ### Strategic Framework for Mediation Sessions  **Objective:**   Our primary
# goal is to secure the best possible outcome for our corporation while
# maintaining flexibility to adapt to various tactics employed by the opposing
# party. Given the potential for a lengthy mediation process, our strategy
# focuses on balancing assertiveness with pragmatism, positioning ourselves
# favorably without unnecessarily escalating the conflict.  ### Key Pillars of
# the Strategy:  1. **Initial Assessment and Calibration:**    - *First Session
# Approach:* Begin the mediation with a **conciliatory proposal**. This allows
# us to gauge the opponent's strategy, assess their level of aggression, and
# establish a baseline for the negotiation environment. Starting on a
# cooperative note also positions us as reasonable and solution-oriented in the
# eyes of the arbitrators.    - Use the first session to collect data on the
# opponent’s posture and gather insights on their willingness to compromise.
# This will inform our subsequent moves.  2. **Strategic Alternation Between
# Aggression and Conciliation:**    - After the initial session, we will adopt a
# **controlled alternation** between aggressive arguments and conciliatory
# proposals, depending on the opponent’s stance. The idea is to remain
# unpredictable while maintaining leverage.    - **If the opponent is
# aggressive:** We respond with **controlled aggression** in the next session to
# prevent being undermined. By mirroring their aggression, we avoid appearing
# weak, but we will maintain a professional tone to avoid escalation.    - **If
# the opponent is conciliatory:** We continue with **measured conciliation** to
# foster collaboration. However, we will introduce **minor aggressive points**
# that subtly assert our key interests, ensuring we maintain an upper hand
# without destroying the cooperative atmosphere.  3. **Preemptive and Adaptive
# Conciliation:**    - If we foresee a session where the opponent might adopt an
# aggressive stance, we may preemptively offer a **calculated conciliatory
# proposal**. This allows us to frame the narrative as the party seeking
# resolution, while subtly positioning the opponent as the unreasonable party if
# they respond with aggression.    - This approach is particularly effective
# when we have compelling evidence or legal arguments that favor us, as the
# arbitrators will likely reward our fairness while noting the opponent's
# hostility.  4. **Escalation as a Tactical Deterrent:**    - If the opponent
# consistently presents aggressive arguments, we will gradually intensify our
# own aggressive stance in subsequent sessions. However, we will ensure our
# aggressive points are **well-supported by facts and legal precedent** to
# maintain credibility.    - This escalation serves as a deterrent, signaling
# that we are willing to fight if necessary, but we will always present an
# **off-ramp** through conciliatory overtures—offering reasonable terms for
# resolution.  5. **Calculated Concessions:**    - Throughout the process, we
# will identify **low-stakes issues** where we can offer **small, calculated
# concessions**. These will be framed as good-faith gestures, helping to build
# goodwill with both the arbitrators and the opposing party.    - These
# concessions will also create leverage for us to demand more significant
# concessions on higher-stakes issues.  6. **Maintain Focus on Key Objectives:**
# - At every stage, we will keep our focus on the **core objectives** that are
# non-negotiable for our corporation. While we may engage in tactical
# flexibility, we will ensure that all conciliatory proposals and aggressive
# arguments are aligned with our long-term goals.    - Any compromise will be
# structured in a way that maximizes our position on critical terms, even if it
# means yielding ground on less important issues.  7. **Leveraging Psychological
# and Timing Dynamics:**    - We will carefully manage the timing of our
# aggressive and conciliatory moves, ensuring that any aggressive argument is
# followed by a conciliatory proposal, especially after we sense that tensions
# are rising.    - If the arbitration process reaches a critical juncture where
# a resolution seems within reach, we will increase the frequency of
# **conciliatory proposals** to expedite a favorable settlement.  ###
# Implementation Tactics:  - **Active Listening & Reframing:** During sessions,
# we will actively listen to the opponent's arguments, and where possible,
# reframe their aggressive points in a way that aligns with our conciliatory
# stance. This will help to neutralize their points while maintaining our
# constructive approach.    - **Controlled Emotional Tone:** We will maintain a
# neutral and calm demeanor, regardless of the opponent’s aggression. This helps
# to underscore our reasonableness and professionalism, making the opponent’s
# aggression appear excessive or unwarranted.  - **Critical Use of Arbitrator
# Feedback:** After each session, we will analyze feedback from the arbitrators
# to adjust our approach. If the arbitrators seem inclined toward conciliation,
# we will lean more heavily into collaborative proposals. If they show signs of
# rewarding assertiveness, we will recalibrate our aggressive arguments
# accordingly.  ### Conclusion:  This strategy is designed to maximize
# flexibility while protecting our core interests. By beginning with a
# conciliatory approach, we build goodwill and gather intelligence on the
# opponent's strategy. The controlled alternation between aggression and
# conciliation ensures that we remain unpredictable, while calculated
# concessions and a focus on key objectives ensure that we remain firmly in
# control of the outcome.  Throughout the process, we will continuously adapt
# based on the opponent’s moves and the arbitrators’ feedback, building momentum
# towards a favorable resolution for our corporation.

# ### Strategy for the Iterated Normal-Form Game (1000 Rounds)  1. **Start with
# Cooperation (C):**      In the first round, play C to test the opponent’s
# intentions and establish a cooperative tone.  2. **Tit-for-Tat with
# Forgiveness:**      - In subsequent rounds, if the opponent played C in the
# previous round, continue playing C in the next round to maintain mutual
# cooperation.    - If the opponent played D in the previous round, respond with
# D in the next round to signal that you will not tolerate defection.  3.
# **Periodic Forgiveness After Defections:**      After responding to an
# opponent’s D with your own D, offer C again after **two consecutive rounds of
# mutual D (D, D)**. This gives the opponent a chance to return to cooperation
# without escalating conflict indefinitely.  4. **Escalate Defection if Opponent
# Defects Repeatedly:**      If the opponent defects (plays D) **three or more
# times in a row**, continue playing D until they play C. This discourages long-
# term defection and signals that persistent aggression will be met with
# sustained resistance.  5. **Return to Cooperation When the Opponent
# Cooperates:**      Anytime the opponent returns to playing C after a series of
# D plays, respond with C in the following round to re-establish mutual
# cooperation.  6. **Occasional Random Cooperation in Extended Defection
# Streaks:**      After a long sequence of mutual D (e.g., more than **10
# rounds**), randomly play C once to probe if the opponent is willing to return
# to cooperation.  7. **Maintain Focus on Cooperation as the End Approaches:**
# In the final 50 rounds, prioritize cooperation (C) more frequently, even after
# occasional defections by the opponent, to maximize long-term payoffs. Only
# defect if the opponent shows consistent defection patterns in the final
# rounds.  This strategy balances cooperation with controlled retaliation and
# occasional forgiveness, discouraging persistent defection while encouraging
# mutual benefit over the long term.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if the opponent defected in the last N rounds
      def opponent_defected_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D) == n
  
      # Helper function to check if mutual defection occurred in the last N rounds
      def mutual_defection_last_n_rounds(n):
          return (self.history[-n:].count(axl.Action.D) == n and
                  opponent.history[-n:].count(axl.Action.D) == n)
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last action of the opponent
      last_opponent_action = opponent.history[-1]
  
      # Final 50 rounds: prioritize cooperation unless opponent is consistently defecting
      if len(self.history) >= 950:
          if opponent_defected_last_n_rounds(3):
              return axl.Action.D  # Defect if opponent is consistently defecting
          return axl.Action.C  # Otherwise, cooperate more frequently
  
      # Tit-for-tat with forgiveness
      if last_opponent_action == axl.Action.C:
          return axl.Action.C  # Cooperate if opponent cooperated last round
      elif last_opponent_action == axl.Action.D:
          # If opponent defected, check if we should forgive after two mutual defections
          if mutual_defection_last_n_rounds(2):
              return axl.Action.C  # Forgive after two mutual defections
          elif opponent_defected_last_n_rounds(3):
              return axl.Action.D  # Escalate defection if opponent defected 3+ times in a row
          else:
              return axl.Action.D  # Otherwise, retaliate with defection
  
      # Occasional random cooperation after long defection streaks (more than 10 rounds)
      if mutual_defection_last_n_rounds(10):
          if self._random.random_choice(0.1):  # 10% chance to cooperate
              return axl.Action.C
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# ### Aggressive Strategy: **Tit-for-Tat with a Twist**  1. **Week 1 - Share
# Openly**: Start the collaboration by sharing your improvements openly. This
# establishes trust and signals your willingness to cooperate. It also allows
# you to observe the behavior of your colleague.  2. **Week 2 Onwards - Mirror
# Their Actions**:     - If your colleague also shared openly in Week 1,
# continue sharing in Week 2. Keep this cooperative approach as long as they
# reciprocate.    - If your colleague keeps their findings confidential in Week
# 1, immediately switch to keeping your results confidential in Week 2 and all
# following weeks until they change their behavior.  3. **Occasionally Test for
# Cooperation**: Every 3 to 4 weeks, if both parties are in a stalemate (both
# keeping findings confidential), you can test the waters by sharing openly for
# one week. If they respond positively by sharing as well, resume the
# cooperative strategy. If they continue to withhold information, return to
# confidentiality.  ### Key Concepts: - **Establish Trust Initially**: Opening
# with cooperation creates the possibility of a mutually beneficial
# relationship, which is the second-best outcome and avoids the worst-case
# scenario. - **Punish Defection Immediately**: If your colleague withholds
# information, respond aggressively by keeping your findings confidential. This
# discourages opportunistic behavior. - **Probe for Cooperation Periodically**:
# If the collaboration deteriorates into mutual withholding, occasionally offer
# an olive branch to see if your colleague is willing to reset to cooperation.
# ### Why This Works: - **Maximizes Gains When Both Cooperate**: Sharing openly
# from the start fosters an environment where both parties can benefit from
# shared advancements. - **Prevents Exploitation**: By immediately withholding
# in response to your colleague's defection, you prevent them from gaining an
# unfair advantage. - **Allows for Recovery**: By occasionally testing for
# cooperation, you avoid getting locked into a purely aggressive strategy and
# leave room for rebuilding trust.  This strategy balances cooperation and
# aggression, allowing you to maximize your development while protecting against
# exploitation.

# ### Strategy: **Tit-for-Tat with Occasional Cooperation Test**  1. **Round 1 -
# Play C (Cooperate)**: Begin by cooperating to establish the possibility of
# mutual benefit.  2. **Round 2 and onwards - Mirror opponent’s previous move**:
# - If your opponent played **C** in the previous round, you play **C**.    - If
# your opponent played **D** in the previous round, you play **D**.  3. **Every
# 100th round - Play C regardless of previous moves**:    - If both you and your
# opponent have been consistently playing **D** for an extended period (e.g.,
# after a long sequence of mutual defection), play **C** on the 100th, 200th,
# 300th, ... rounds to test if your opponent is willing to return to
# cooperation.     - If they respond with **C**, resume the strategy of
# mirroring their moves.    - If they respond with **D**, return to playing
# **D** in subsequent rounds.  ### Summary of Actions: - **Round 1**: Play
# **C**. - **From Round 2 onward**:    - Mirror your opponent’s previous move.
# - Play **C** every 100th round to test for cooperation if both have been
# defecting.  This strategy balances cooperation with retaliation and occasional
# testing for mutual benefit.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C
      
      # Every 100th round: Play C to test for cooperation
      if len(self.history) % 100 == 0:
          return axl.Action.C
      
      # Mirror opponent's previous move
      return opponent.history[-1]

# A successful strategy in this multi-round negotiation scenario should balance
# the pursuit of an immediate advantage with long-term collaboration and trust-
# building. Given that repeated interactions are likely, a cooperative approach
# is essential to avoid destructive cycles of retaliation and to maximize
# mutually beneficial outcomes over time. Here's a high-level, straightforward
# strategy:  ### 1. **Begin with Cooperation (Tit-for-Tat):**    - **Start with
# a Free Trade Proposal**: In the first round, offer free trade. This signals
# goodwill and a cooperative stance, setting a positive tone for the
# negotiations and encouraging your counterpart to reciprocate.     ### 2.
# **Reciprocate Counterpart's Actions:**    - **Mirror Your Counterpart's
# Action**: In each subsequent round, respond based on your counterpart's
# previous move:      - If they proposed free trade in the last round, continue
# offering free trade.      - If they imposed protectionist measures in the last
# round, respond by proposing protectionist measures in the next round.  ### 3.
# **Gradual Retaliation (Tit-for-Two-Tats):**    - **Allow One Defection Before
# Retaliation**: If your counterpart imposes protectionist measures, do not
# immediately retaliate. Offer free trade one more time. This gives your
# counterpart a chance to correct course and signals that you are still willing
# to cooperate despite a temporary setback.    - **Retaliate Only After Repeated
# Defection**: If your counterpart imposes protectionist policies for two
# consecutive rounds, then respond with protectionist measures. This ensures
# that you are not exploited for too long, while still giving a chance for
# cooperation to prevail.  ### 4. **Encourage Cooperation through
# Communication:**    - **Use Diplomatic Channels to Emphasize Mutual Gains**:
# Throughout the rounds, emphasize the long-term benefits of free trade and the
# risks of continued protectionism. Highlight how both countries can grow
# economically through cooperation.    - **Offer Conditional Agreements**: You
# can propose conditional agreements, where both sides commit to mutual free
# trade for a set number of rounds, ensuring that any deviation from the
# agreement will automatically trigger protectionist measures.  ### 5.
# **Occasional Generosity (Forgiveness Mechanism):**    - **Forgive Occasional
# Protectionism**: If your counterpart reverts to free trade after a round of
# protectionism, return to offering free trade as well. This strategy ensures
# that a single protectionist move doesn't spiral into a prolonged retaliatory
# conflict, promoting long-term cooperation.  ### 6. **Adapt and Evolve:**    -
# **Monitor Patterns**: Keep track of your counterpart’s strategy over time. If
# they consistently impose protectionist policies, you may need to shift toward
# more robust protectionism yourself. However, remain open to cooperative
# gestures if they shift back to free trade.    - **Be Flexible**: If the
# counterpart adopts a very aggressive protectionist stance, you may need to
# adjust your strategy to safeguard your country’s interests. In this case,
# consider proposing a balanced trade agreement that allows for some
# protectionist measures but still promotes overall trade growth.  ### Summary
# of the Strategy: - **Start with free trade** to set the tone for cooperation.
# - **Mirror your counterpart’s actions** to encourage reciprocity. - **Allow
# one instance of protectionism** before retaliating, showing forgiveness but
# not being exploited. - **Communicate the long-term benefits** of cooperation
# and free trade. - **Occasionally forgive protectionist moves** if your
# counterpart returns to cooperation. - **Adapt as necessary** based on the
# evolving situation, but keep the door open for future cooperation.  This
# strategy helps your country avoid the worst outcomes while maximizing the
# chances for mutually beneficial agreements over time.

# ### Strategy for the Iterated Normal-Form Game (1000 Rounds)  1. **Start by
# Cooperating**:    - In the first round, play **C** (Cooperate).  2.
# **Reciprocate Opponent's Previous Move**:    - In each subsequent round, play
# the same move your opponent played in the previous round:      - If they
# played **C** in the previous round, play **C** (Cooperate).      - If they
# played **D** in the previous round, play **D** (Defect).  3. **Allow One
# Defection Before Retaliating**:    - If your opponent plays **D** (Defect)
# once, still play **C** (Cooperate) in the next round. This allows for a
# potential return to cooperation.  4. **Retaliate After Two Consecutive
# Defections**:    - If your opponent plays **D** (Defect) in two consecutive
# rounds, respond by playing **D** (Defect) in the next round.  5. **Forgive
# Occasional Defections**:    - If your opponent played **D** (Defect) but then
# returns to playing **C** (Cooperate) after one round, respond by playing **C**
# (Cooperate) in the next round, returning to cooperation.  6. **Continue
# Monitoring and Adapting**:    - If your opponent consistently plays **D**
# (Defect) for multiple rounds, continue playing **D** (Defect) until they
# return to **C** (Cooperate).    - If your opponent resumes cooperation, return
# to playing **C** (Cooperate) in the following round.

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
  
      # Get the last two moves of the opponent (if available)
      last_move = opponent.history[-1]
      second_last_move = opponent.history[-2] if len(opponent.history) > 1 else None
  
      # If opponent defected in the last two rounds, retaliate with D
      if last_move == axl.Action.D and second_last_move == axl.Action.D:
          return axl.Action.D
  
      # If opponent defected only once, allow one defection and cooperate
      if last_move == axl.Action.D:
          return axl.Action.C
  
      # Otherwise, reciprocate the opponent's last move
      return last_move

# ### Strategic Framework for Mediation Process:  The goal of this strategy is
# to maintain a balance between assertiveness and collaboration, leveraging the
# mediation process to position our corporation favorably while minimizing
# risks. This strategy will allow for adaptability and flexibility, ensuring we
# can respond appropriately to the various tactics our opponent may employ.
# #### **1. Initial Sessions: Establishing Tone and Gathering Intelligence**
# **Approach:** *Conciliatory Proposal with Assertive Framing*  - **Rationale:**
# In the early sessions, it is crucial to project a cooperative tone while
# subtly framing our position in a way that underscores the strength of our
# legal and factual arguments. We will offer conciliatory proposals that appear
# reasonable on the surface but are carefully structured to protect our core
# interests.    - **Objective:** This approach allows us to gauge the opponent’s
# strategy and the arbitrators' inclinations without appearing unnecessarily
# aggressive. By presenting a well-reasoned and cooperative front, we can assess
# whether the opposing party is inclined toward collaboration or conflict, all
# while subtly demonstrating the strength of our position.    - **Contingency:**
# If the opponent responds aggressively, we will have gathered early evidence of
# their approach without compromising our position, enabling us to adjust in
# subsequent sessions.  #### **2. Middle Sessions: Strategic Aggression and
# Tactical Concessions**  **Approach:** *Hybrid Approach – Aggressive Argument
# with Selective Concessions*  - **Rationale:** As the mediation progresses, we
# will gradually shift toward a more aggressive stance without abandoning the
# collaborative tone entirely. In some sessions, we will make assertive
# arguments highlighting the weaknesses in the opponent’s position, while in
# others, we will offer selective, non-critical concessions to maintain a
# cooperative atmosphere.  - **Objective:** This hybrid approach allows us to
# increase pressure selectively, keeping the opponent off balance. By
# alternating between assertive arguments and conciliatory gestures, we maintain
# flexibility and avoid becoming predictable. Key to this phase is ensuring that
# our aggressive arguments are framed within the context of advancing a fair and
# constructive resolution, positioning us favorably in the eyes of the
# arbitrators.  - **Contingency:** If the opponent reacts by intensifying their
# aggression, we will be prepared to escalate selectively. However, if they
# respond with more collaborative overtures, we can pivot back to a more
# conciliatory tone to foster a resolution.  #### **3. Final Sessions: Closing
# the Gap or Escalating Pressure**  **Approach:** *Dynamic Response – Tailored
# to the Opponent's Position*  - **If the Opponent is Conciliatory:**      -
# **Approach:** *Conciliatory Proposal with Strong Final Offer*     -
# **Rationale:** If the opponent has moved toward a more collaborative stance,
# we will capitalize on this by offering a final, strong conciliatory proposal
# that aligns with our core interests. This proposal will be designed to appear
# as a fair compromise while ensuring our essential objectives are met.     -
# **Objective:** This will allow us to close the mediation on favorable terms
# without the need for further escalation. By framing this as a “win-win”
# solution for both parties, we aim to secure a resolution that benefits our
# corporation while maintaining a positive public image.  - **If the Opponent is
# Aggressive:**     - **Approach:** *Aggressive Argument with Limited
# Concessions*     - **Rationale:** If the opposing party remains aggressive, we
# will escalate our arguments while offering only limited concessions on non-
# essential points. The key here is to maintain a firm, assertive position that
# highlights the risks and weaknesses in the opponent’s approach, signaling that
# we are prepared to continue the dispute if necessary.     - **Objective:**
# This approach will aim to either force the opponent to reconsider their
# position or prepare for a possible escalation beyond mediation if no
# resolution is reached.  #### **4. Adaptation Based on Opponent's Behavior**
# Throughout the process, our strategy will remain flexible and adaptive:  - If
# the opponent displays signs of fragmentation or internal disagreement, we will
# exploit this by applying pressure on key points where they are most
# vulnerable. - If the opponent appears unified and strategic, we will remain
# measured in our aggression, ensuring that we do not overextend and risk a
# deadlock. - We will closely monitor the arbitrators' reactions, adjusting our
# tone and content based on their feedback and cues, to ensure that we maintain
# a favorable standing in their assessment.  ### Conclusion:  This strategy
# balances assertiveness with collaboration, allowing us to remain flexible and
# responsive to the opponent's tactics. By starting from a position of
# cooperation and gradually escalating as necessary, we can gauge the opponent’s
# approach, build credibility with the arbitrators, and position our corporation
# for a favorable outcome. The key will be to maintain control of the narrative,
# ensuring that we are seen as reasonable, solution-oriented, and prepared to
# defend our interests when necessary.  Our adaptability throughout the process,
# coupled with careful management of the arbitrators’ perceptions, will ensure a
# strong, favorable conclusion to the mediation process.

# ### Iterated Normal-Form Game Strategy  1. **Initial Rounds (Rounds 1-100):
# Start by Cooperating**      Begin by playing *C* (Cooperate) for the first 10
# rounds, regardless of the opponent’s moves. This establishes a cooperative
# tone and allows you to observe the opponent’s strategy without immediately
# escalating the game.  2. **Observation and Response (Rounds 101-500): Adaptive
# Strategy Based on Opponent’s Behavior**      - **If the opponent mostly plays
# C (roughly 70% or more of the time):**        Continue to play *C* to build a
# mutually beneficial relationship. Occasionally play *D* (Defect) once every 50
# rounds to test for potential vulnerabilities, but return to *C* immediately
# after.    - **If the opponent frequently plays D (more than 30% of the
# time):**        Switch to playing *D* for 5 consecutive rounds in response,
# then attempt to return to *C* to see if the opponent shifts back to
# cooperation. If they persist in playing *D*, continue to respond aggressively
# with *D* but mix in occasional *C* moves (every 20 rounds) to test for
# opportunities to return to cooperation.  3. **Mid-Game (Rounds 501-800):
# Hybrid Strategy with Selective Defection**      - **If both players have been
# cooperatively playing C frequently (more than 70% of the time):**
# Continue with *C* but introduce periodic defection (*D*) every 25 rounds to
# maximize potential gains without fully breaking trust. After each *D*,
# promptly return to *C* to signal willingness to cooperate.    - **If the
# opponent has been playing *D* frequently (more than 30% of the time):**
# Escalate by playing *D* more frequently (every 2-3 rounds), but mix in
# occasional *C* moves to signal that you are open to returning to cooperation
# if the opponent changes their behavior.  4. **Final Rounds (Rounds 801-1000):
# Dynamic Response Based on Opponent’s Dominant Strategy**      - **If the
# opponent has been mostly cooperative (more than 70% of the time):**
# Play *C* for the remainder of the game, except for a final few defections
# (*D*) in the last 10 rounds to maximize score without risking retaliation
# (since there are fewer rounds left).    - **If the opponent has been mostly
# aggressive (more than 30% of the time):**        Play *D* consistently for the
# remaining rounds, except for occasional *C* (every 10 rounds) to test for a
# last-minute shift in cooperation. However, be prepared to continue defecting
# if no change is observed.  ### Key Adjustments Throughout: - Always monitor
# shifts in the opponent’s behavior and adjust accordingly. - When in doubt,
# favor *C* during periods of cooperation, but never hesitate to escalate with
# *D* when the opponent defects too often. - Use selective defections
# strategically to test the opponent’s willingness to cooperate or to exploit
# opportunities to score higher points while keeping the opponent off balance.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to calculate opponent's cooperation rate
      def opponent_cooperation_rate():
          if len(opponent.history) == 0:
              return 1  # Assume full cooperation if no history
          return opponent.history.cooperations / len(opponent.history)
      
      # Helper function to calculate opponent's defection rate
      def opponent_defection_rate():
          return 1 - opponent_cooperation_rate()
  
      # Round number
      round_number = len(self.history) + 1
  
      # Phase 1: Initial Rounds (Rounds 1-100) - Always Cooperate
      if round_number <= 100:
          return axl.Action.C
  
      # Phase 2: Observation and Response (Rounds 101-500)
      if 101 <= round_number <= 500:
          if opponent_cooperation_rate() >= 0.7:
              # Mostly cooperative opponent
              if round_number % 50 == 0:
                  return axl.Action.D  # Occasional defection every 50 rounds
              return axl.Action.C
          else:
              # Frequently defecting opponent
              if self.history[-5:].count(axl.Action.D) < 5:
                  return axl.Action.D  # Defect for 5 consecutive rounds
              if round_number % 20 == 0:
                  return axl.Action.C  # Occasional cooperation every 20 rounds
              return axl.Action.D
  
      # Phase 3: Mid-Game (Rounds 501-800)
      if 501 <= round_number <= 800:
          if opponent_cooperation_rate() >= 0.7:
              # Mostly cooperative opponent
              if round_number % 25 == 0:
                  return axl.Action.D  # Periodic defection every 25 rounds
              return axl.Action.C
          else:
              # Frequently defecting opponent
              if round_number % 3 == 0:
                  return axl.Action.D  # Defect more frequently (every 2-3 rounds)
              if round_number % 20 == 0:
                  return axl.Action.C  # Occasional cooperation every 20 rounds
              return axl.Action.D
  
      # Phase 4: Final Rounds (Rounds 801-1000)
      if 801 <= round_number <= 1000:
          if opponent_cooperation_rate() >= 0.7:
              # Mostly cooperative opponent
              if round_number >= 991:
                  return axl.Action.D  # Defect in the last 10 rounds
              return axl.Action.C
          else:
              # Mostly aggressive opponent
              if round_number % 10 == 0:
                  return axl.Action.C  # Occasional cooperation every 10 rounds
              return axl.Action.D

# ### High-Level Aggressive Strategy: "Tit-for-Tat with a Twist"  This strategy
# is designed to maximize the economic advantage for your country while keeping
# your counterpart in check if they attempt to exploit your goodwill. The idea
# is to start with cooperation but retaliate swiftly if the other side adopts
# protectionist policies.  #### Round 1: **Start with Free Trade** -
# **Rationale**: By offering free trade in the first round, you signal goodwill
# and a willingness to cooperate. This encourages mutual free trade, which is
# your second-best outcome and sets a positive tone for negotiations.    ####
# Round 2+: **Tit-for-Tat with a Twist** - **Respond Based on Their Action in
# the Previous Round**:   - **If they offer free trade**: Continue offering free
# trade in the next round. This builds a cycle of cooperation, securing mutual
# benefits for both nations.   - **If they impose protectionist policies**:
# Immediately respond with your own *protectionist policy* in the next round.
# This signals that you will retaliate against any attempt to exploit your free
# trade offer, and you won’t allow your country to be disadvantaged.  #### The
# "Twist" (Occasional Aggressive Deviation): - **After a few rounds of mutual
# free trade (preferably 3-4 rounds)**, unexpectedly introduce a **protectionist
# policy** in one round, even if the counterpart continues to offer free trade.
# - **Rationale**: This aggressive move seeks to catch your counterpart off-
# guard and gain a temporary economic advantage for your country. It also tests
# their resolve and willingness to continue cooperating.    #### Follow-Up After
# the Twist: - If they retaliate with protectionism, immediately revert to tit-
# for-tat (protectionist measures). This ensures that they cannot sustain a
# long-term advantage over your country. - If they continue offering free trade
# despite your aggressive move, return to free trade in the subsequent round.
# This signals that your protectionist stance was a one-time strategic move, and
# you are willing to cooperate again.  #### Core Principles Behind the Strategy:
# 1. **Reward Cooperation**: If your counterpart plays fairly by offering free
# trade, you will do the same to foster mutual benefits. 2. **Punish Defection
# Immediately**: If they attempt to impose protectionist policies, retaliate
# immediately to prevent your country from being exploited. 3. **Occasional
# Aggression for Leverage**: By inserting occasional protectionist policies, you
# keep your counterpart on their toes and create opportunities to gain a
# temporary advantage, without completely destroying the cooperative dynamic. 4.
# **Signal Willingness to Return to Cooperation**: After each aggressive move,
# offer a path back to free trade, signaling that your country is open to
# cooperation if the counterpart is reasonable.  ### Summary: - **Round 1**:
# Offer free trade. - **Future rounds**: Respond based on the other party's
# previous move (free trade for free trade, protectionism for protectionism). -
# **Occasional deviation**: After a few rounds of mutual free trade, introduce a
# protectionist policy to gain an advantage, then return to cooperative behavior
# if the counterpart does not escalate.  This strategy combines the benefits of
# cooperation with the ability to assert economic dominance when necessary,
# ensuring the best possible outcomes for your country across multiple rounds.

# 1. **Round 1**: Play C (Cooperate).     2. **From Round 2 onwards**:    - **If
# your opponent played C in the previous round**, play C.    - **If your
# opponent played D in the previous round**, play D in this round.  3. **After 3
# consecutive rounds of mutual C (both players playing C)**:    - Play D
# (Defect) in the next round, regardless of what the opponent played.  4.
# **After playing D in this "aggressive" round**:    - **If your opponent plays
# C in response**: Return to playing C in the next round.    - **If your
# opponent plays D in response**: Continue playing D until they play C again.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Play C
      if self.first_round():
          self.consecutive_cooperations = 0  # Track consecutive mutual cooperations
          self.aggressive_mode = False       # Track if we are in aggressive mode
          return axl.Action.C
  
      # Check if we are in aggressive mode
      if self.aggressive_mode:
          if opponent.history[-1] == axl.Action.C:
              # Opponent played C, return to cooperation
              self.aggressive_mode = False
              return axl.Action.C
          else:
              # Opponent played D, continue defecting
              return axl.Action.D
  
      # From Round 2 onwards: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          # Check for mutual cooperation
          if self.history[-1] == axl.Action.C:
              self.consecutive_cooperations += 1
          else:
              self.consecutive_cooperations = 0
          # After 3 consecutive mutual cooperations, play D
          if self.consecutive_cooperations >= 3:
              self.aggressive_mode = True
              return axl.Action.D
          return axl.Action.C
      else:
          # Opponent played D, reset cooperation count and play D
          self.consecutive_cooperations = 0
          return axl.Action.D

# ### Strategic Framework: **Dynamic Cooperation with Contingent Aggression**
# In this complex, multi-session mediation process, your goal is to strike a
# balance between safeguarding your corporation’s interests and fostering a
# productive environment that can lead to a favorable resolution. The following
# strategy, **Dynamic Cooperation with Contingent Aggression**, is designed to
# maintain flexibility and adaptability while positioning your corporation
# favorably in each session. It combines elements of cooperation with the
# strategic use of aggression, ensuring that you remain assertive when necessary
# but open to collaboration when advantageous.  ---  ### **Stage 1: Establish a
# Foundation of Trust and Collaboration (Sessions 1-3)**  Start the mediation
# process with a **conciliatory approach**. This sets the tone as one of
# goodwill and positions your corporation as reasonable, solution-oriented, and
# cooperative. During the first few sessions:  1. **Signal Constructive
# Intent**: Open the dialogue by proposing reasonable, fact-based conciliatory
# proposals that demonstrate your commitment to resolving the dispute
# efficiently. This will also test your opponent’s intentions.     2. **Build
# Credibility with Arbitrators**: By showing willingness to compromise early,
# you may earn trust from the arbitrators, which can be crucial when the dispute
# intensifies in later sessions.  3. **Monitor Opponent’s Response**: Use these
# early sessions to gather intelligence on your opponent’s strategy. Are they
# reciprocating your conciliatory gestures, or are they exploiting your goodwill
# by advancing aggressive arguments?     - **If Opponent is Conciliatory**:
# Continue with a cooperative stance, pushing for creative solutions that take
# into account both sides’ interests.    - **If Opponent is Aggressive**: Take
# note, but do not immediately shift to retaliation. Escalating too early may
# hurt your credibility.  ---  ### **Stage 2: Shift to Contingent Aggression
# (Middle Sessions)**  Once the groundwork is laid, you should adapt your
# approach based on your opponent’s behavior. At this point, you should begin
# employing **contingent aggression**—where your aggressiveness is conditional
# on your opponent's actions.  1. **Reciprocal Aggression When Necessary**: If
# your opponent has been aggressive in early sessions, shift your tone to match
# their level of intensity. This ensures that they do not gain undue leverage by
# exploiting your initial conciliatory stance.     - **Strategic Aggression**:
# Frame your arguments in a way that highlights the risks and consequences for
# both sides if the dispute escalates or remains unresolved. Emphasize the
# strengths of your position while subtly pointing out the weaknesses in your
# opponent’s case.  2. **Calibrated Responses**: If your opponent returns to a
# more conciliatory approach after a few aggressive sessions, you should pivot
# back to cooperation, signaling that you are willing to reciprocate good faith
# efforts. This balance keeps the negotiation fluid and adaptive, preventing
# deadlock.     3. **Leverage Information Gained**: By now, you will have a
# clearer understanding of your opponent’s priorities and pressure points. Use
# this knowledge to tailor your arguments—highlight your strengths where they
# are weakest and make targeted concessions where you know they are more likely
# to agree.  ---  ### **Stage 3: Engage in Strategic Escalation and De-
# Escalation (Later Sessions)**  In the final stages of the mediation, the
# stakes are highest, and your strategy should focus on maximizing gains while
# avoiding unnecessary conflict. At this point, carefully weigh the benefits of
# aggression versus cooperation in each session.  1. **Preemptive Aggression for
# Final Leverage**: If your previous cooperative efforts have not yielded
# significant concessions, consider presenting a more aggressive argument in the
# later sessions. Doing so may force the other side to reassess their position
# and make last-minute concessions to avoid the risk of arbitration failure.
# - **Tactical Aggression**: Introduce new, compelling evidence or arguments
# that you have previously withheld, catching your opponent off-guard and
# potentially swaying the arbitrators in your favor.  2. **Final Conciliatory
# Offer**: If both sides have engaged in aggressive back-and-forths, propose a
# final **conciliatory offer** that encompasses a reasonable compromise. Frame
# this as a "last chance" for both parties to avoid prolonged arbitration or
# litigation, appealing to the arbitrators’ desire for resolution and
# positioning your corporation as the party seeking closure.     3. **Read
# Arbitrators’ Signals**: Throughout the process, pay close attention to the
# arbitrators’ reactions. Are they leaning toward a collaborative resolution, or
# do they seem to favor one party’s aggressive stance? Adapt your final
# arguments accordingly, tailoring them to resonate with the arbitrators’
# perceived preferences.  ---  ### **Key Tactics to Support the Strategy**  1.
# **Consistent Messaging**: Emphasize that your corporation is fundamentally
# committed to a fair and reasonable outcome. This positions your aggressive
# arguments as defensive rather than hostile, allowing you to pivot between
# cooperation and aggression seamlessly.  2. **Use of Contingent Proposals**:
# Offer proposals that have built-in contingencies, such as “If the other party
# agrees to X, we are willing to concede Y.” This encourages negotiation without
# fully committing to concessions until you are sure they will be met with
# reciprocity.  3. **Escalation Clause**: Subtly introduce the possibility of
# escalating to litigation or other binding arbitration if the mediation does
# not yield results. However, frame this as undesirable for both parties,
# leaving the door open for a more collaborative resolution.  4. **Maintain
# Flexibility**: Avoid becoming entrenched in any one strategy. Your approach
# must remain dynamic and responsive to both your opponent’s moves and the
# arbitrators’ feedback. This adaptability will allow you to stay one step
# ahead.  ---  ### **Endgame: Positioning for a Favorable Outcome**  By the
# conclusion of the mediation process, your corporation should be positioned as
# the rational, solution-oriented party while having demonstrated the capacity
# to defend its interests aggressively when needed. This balanced approach will
# not only appeal to the arbitrators but will also keep your opponent cautious
# about exploiting your cooperative gestures.  The **Dynamic Cooperation with
# Contingent Aggression** strategy ensures that you maximize opportunities for
# favorable outcomes while minimizing the risks of prolonged conflict or an
# unfavorable ruling.

# ### Iterated Game Strategy: **Adaptive Cooperation with Conditional
# Defection**  This strategy is designed to balance cooperation and defection
# over 1000 rounds, aiming to maximize long-term rewards while protecting
# against exploitation.  ---  ### **Initial Phase (Rounds 1-3): Establish
# Cooperation**  For the first three rounds, **always play C (Cooperate)**.  -
# This signals trust and sets the stage for a cooperative environment. - Observe
# your opponent’s responses carefully.  ---  ### **Middle Phase (Rounds 4-900):
# Conditional Responses Based on Opponent’s Behavior**  1. **If your opponent
# plays C (Cooperate) in the previous round**, continue to play C (Cooperate) in
# the next round.    - Maintain mutual cooperation as long as it is
# reciprocated.  2. **If your opponent plays D (Defect) in the previous round**,
# respond with D (Defect) in the next round.    - Punish defection immediately
# to prevent exploitation.  3. **If your opponent returns to C (Cooperate) after
# a defection**, return to C (Cooperate) as well.    - This shows you are
# willing to restore cooperation if they correct course.  ---  ### **Late Phase
# (Rounds 901-1000): Strategic Defection and Cooperation**  1. **If cooperation
# has been sustained for most of the game (80% or more of rounds have been
# mutual C)**, play C (Cooperate) for the final rounds.    - This maximizes the
# long-term cooperative payoff.  2. **If defection has dominated the game (more
# than 50% of rounds have been D)**, play D (Defect) for the final rounds.    -
# End the game defensively if cooperation has failed.  ---  ### **Key
# Conditional Adjustments Throughout the Game**  - **Occasional Defection After
# Long Cooperation**: If both players have cooperated for 50 consecutive rounds,
# introduce a single round of D (Defect) to test resilience. If your opponent
# defects in response, return to mutual defection for 10 rounds. If your
# opponent continues to cooperate, return to C (Cooperate).    - **Forgive Rare
# Defections**: If your opponent defects only once or twice within a span of 20
# rounds, consider it noise and return to C (Cooperate) immediately after one
# round of D (Defect).  ---  ### **Endgame Consideration (Final 100 Rounds)**  -
# If cooperation has been the dominant strategy and your opponent defects within
# the final 100 rounds, **defect for the remainder of the game**. This prevents
# last-minute exploitation.    - If mutual defection has been frequent,
# **consider alternating between C and D** to disrupt any patterns and limit
# their ability to exploit you.  ---  This strategy ensures that cooperation is
# rewarded, defection is punished, and the flexibility to adapt to your
# opponent’s behavior is maintained throughout the 1000 rounds.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      TOTAL_ROUNDS = 1000
      MIDDLE_PHASE_END = 900
      LATE_PHASE_START = 901
      TEST_DEFECT_INTERVAL = 50
      FORGIVENESS_WINDOW = 20
      MUTUAL_COOP_THRESHOLD = 0.8
      MUTUAL_DEFECT_THRESHOLD = 0.5
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_cooperations = 0
          self.test_defection_round = None
          return COOPERATE
  
      # Helper function to count mutual cooperation
      def mutual_cooperation_ratio():
          mutual_coops = sum(1 for i in range(len(self.history)) if self.history[i] == COOPERATE and opponent.history[i] == COOPERATE)
          return mutual_coops / len(self.history)
  
      # Helper function to count defections in the last N rounds
      def defections_in_last_n_rounds(n):
          return opponent.history[-n:].count(DEFECT)
  
      # Initial Phase (Rounds 1-3): Always cooperate
      if len(self.history) < 3:
          return COOPERATE
  
      # Middle Phase (Rounds 4-900): Conditional responses based on opponent's behavior
      if len(self.history) <= MIDDLE_PHASE_END:
          # If opponent defected in the last round, defect
          if opponent.history[-1] == DEFECT:
              return DEFECT
          # If opponent cooperated in the last round, cooperate
          if opponent.history[-1] == COOPERATE:
              # Check for 50 consecutive cooperations to introduce a test defection
              if self.consecutive_cooperations >= TEST_DEFECT_INTERVAL:
                  self.consecutive_cooperations = 0
                  self.test_defection_round = len(self.history) + 1
                  return DEFECT
              else:
                  self.consecutive_cooperations += 1
                  return COOPERATE
  
      # Late Phase (Rounds 901-1000): Strategic defection and cooperation
      if len(self.history) >= LATE_PHASE_START:
          # Calculate mutual cooperation ratio
          coop_ratio = mutual_cooperation_ratio()
  
          # If cooperation has been sustained for 80% or more of the game, cooperate
          if coop_ratio >= MUTUAL_COOP_THRESHOLD:
              return COOPERATE
  
          # If defection has dominated the game (more than 50% of rounds), defect
          if defections_in_last_n_rounds(len(self.history)) / len(self.history) > MUTUAL_DEFECT_THRESHOLD:
              return DEFECT
  
      # Occasional Defection After Long Cooperation
      if self.test_defection_round and len(self.history) == self.test_defection_round:
          if opponent.history[-1] == DEFECT:
              # If opponent defects in response to the test defection, defect for 10 rounds
              self.test_defection_round = len(self.history) + 10
              return DEFECT
          else:
              # If opponent cooperates, return to cooperation
              self.test_defection_round = None
              return COOPERATE
  
      # Forgive Rare Defections
      if defections_in_last_n_rounds(FORGIVENESS_WINDOW) <= 2:
          return COOPERATE
  
      # Default to cooperation if no other conditions are met
      return COOPERATE

# ### Strategy: **Tit-for-Tat with a Cooperative Bias**  Given the repeated
# nature of the negotiations, your strategy should aim to balance maximizing
# your country's economic advantage while maintaining a cooperative relationship
# to avoid long-term detriment. The **Tit-for-Tat with a Cooperative Bias**
# strategy is straightforward and adaptive, promoting cooperation but ensuring
# that your country is not exploited by unilateral protectionism from the other
# side.  #### Key Elements of the Strategy:  1. **Start with Cooperation (Free
# Trade Offer)**    - In the first round, begin by offering a **free trade
# agreement**. This signals goodwill and a willingness to cooperate, which may
# encourage a mutually beneficial outcome from the start.    - If both parties
# agree to free trade, both countries enjoy growth and stability.  2. **Respond
# Symmetrically**    - In subsequent rounds, **mirror your counterpart's
# previous move**:      - If they offer **free trade**, continue to offer free
# trade.      - If they impose **protectionist measures**, respond with
# equivalent protectionist measures in the next round.    - This ensures that
# your country is not taken advantage of by consistently offering free trade
# while the other side imposes tariffs or quotas.  3. **Cooperate Again after
# Retaliation**    - If mutual protectionism occurs (both sides impose
# protectionist measures), **return to offering free trade** in the next round.
# - This shows that your country is not interested in a prolonged trade war and
# is willing to de-escalate, leaving the door open for cooperation.  4.
# **Occasional Cooperation after One-Sided Protectionism**    - If at any point
# your counterpart imposes protectionist measures while you offer free trade,
# **retaliate once** with protectionism.    - However, after one round of
# retaliation, **offer free trade again**. This signals that your preference is
# still for cooperation but that you're also willing to defend your country's
# interests if necessary.  #### Rationale Behind the Strategy:  - **Promotes
# Cooperation:** Starting with free trade and offering to return to free trade
# after protectionism helps encourage the counterpart to cooperate for mutual
# benefit. - **Prevents Exploitation:** The tit-for-tat response ensures that
# your country does not suffer a disadvantage from one-sided protectionist
# measures. - **Minimizes Long-Term Damage:** By offering free trade again after
# a round of protectionism, you avoid spiraling into a prolonged trade war,
# which would be detrimental to both nations. - **Flexibility:** This strategy
# is adaptable to various approaches your counterpart might take, whether they
# are cooperative or protectionist over the course of the rounds.  #### Example
# Scenario:  - **Round 1:** You offer **free trade**, and the counterpart offers
# free trade. Both countries benefit. - **Round 2:** You continue to offer
# **free trade**, but the counterpart imposes protectionist measures. Your
# country suffers an economic disadvantage. - **Round 3:** You respond with
# **protectionist measures** to counterbalance the previous round's
# disadvantage. - **Round 4:** You return to offering **free trade**,
# demonstrating your preference for cooperation. - **Round 5:** If the
# counterpart reciprocates with **free trade**, you continue on a mutually
# beneficial path. If they continue with protectionism, you retaliate again.
# This approach sets a tone of cooperation but ensures that your country does
# not suffer consistently from one-sided protectionist policies.

# ### Strategy: Tit-for-Tat with Cooperation Bias (for an Iterated Normal-Form
# Game)  1. **First Round:**    - Play **C** (Cooperate).  2. **In Each
# Subsequent Round:**    - If your opponent played **C** in the previous round,
# play **C** (Cooperate).    - If your opponent played **D** in the previous
# round, play **D** (Defect).  3. **After Mutual Defection:**    - If both you
# and your opponent played **D** in the previous round, play **C** in the next
# round (return to Cooperate).  4. **After Unilateral Defection by Your
# Opponent:**    - If your opponent played **D** and you played **C** in the
# previous round, play **D** in the next round (retaliate).    - After
# retaliating once, play **C** (Cooperate) in the following round.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the last round's actions
      my_last_action = self.history[-1]
      opponent_last_action = opponent.history[-1]
  
      # If both players defected in the last round, return to cooperation
      if my_last_action == axl.Action.D and opponent_last_action == axl.Action.D:
          return axl.Action.C
  
      # If opponent defected and I cooperated in the last round, retaliate by defecting
      if my_last_action == axl.Action.C and opponent_last_action == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, mimic the opponent's last action (Tit-for-Tat)
      return opponent_last_action

# ### Aggressive Strategy for Mediation Process  #### 1. **Controlled Aggression
# with Strategic Flexibility**  Our primary objective is to position the
# corporation favourably by using a **controlled aggression** approach. While it
# is important to assert dominance and maintain leverage in front of the
# arbitrators, we must do so in a manner that does not alienate the mediators or
# create an irreparable impasse. The strategy will focus on keeping pressure on
# the opponent while leaving enough room for adaptability based on their
# responses.  #### 2. **Dynamic Phased Approach**  We will divide the mediation
# process into distinct phases, each with a different level of aggression, to
# keep the opponent off balance:  - **Phase 1: Assertive Opening**     Begin
# with a strong, fact-driven argument that clearly outlines our legal and
# contractual position. The goal is to establish the strength of our case,
# project confidence, and demonstrate that we are prepared for a protracted
# dispute if necessary. This will set the tone and signal that we are not here
# to make unnecessary concessions.      **Tactics:**   - Present a detailed
# analysis of the contract with legal precedents that favour our interpretation.
# - Highlight the opponent’s vulnerabilities and inconsistencies in their
# demands or previous actions.   - Introduce the consequences of an aggressive
# dispute in terms of time, cost, and reputation, subtly implying that we are
# better positioned to endure a prolonged conflict.  - **Phase 2: Measured
# Escalation**     Depending on the opponent's reaction, intensify the
# aggressive posture slightly. This phase will involve pushing the narrative
# that the opponent is unreasonable or acting in bad faith, without overtly
# accusing them of such conduct. The goal is to pressure the opponent into
# making a conciliatory move by showing the arbitrators that we are willing to
# engage but only if the opponent acts rationally.    **Tactics:**   - Introduce
# expert testimony or third-party assessments that reinforce our position.   -
# Begin undermining the opponent’s credibility by pointing out internal
# contradictions in their arguments or previous statements.   - Keep the
# arbitrators engaged by making it clear that we are open to reasonable
# dialogue, but only if the opponent steps back from aggressive stances.  ####
# 3. **Preemptive Concessions on Non-Essential Terms**  To maintain the
# appearance of reasonableness and to avoid being perceived as overly combative,
# we will identify **non-essential terms** that we can offer as concessions
# early in the mediation. These should be items that appear substantial but have
# minimal impact on our ultimate goals. This gives the arbitrators the
# impression that we are willing to compromise, while still positioning us to
# win on the key points.  **Tactics:** - Offer a seemingly significant
# concession on a minor contractual issue where we have flexibility. - Frame
# these concessions as a demonstration of our willingness to cooperate, while
# subtly implying that the opponent has been uncooperative.  #### 4.
# **Psychological Pressure: Offer a "Final" Deal**  At a critical point in the
# process, we will present what appears to be a **final, take-it-or-leave-it
# proposal**. This offer should be designed to seem like a substantial
# compromise from our side, but in reality, it should still favour our key
# interests. The psychological pressure of a "final" offer can push the opponent
# into making concessions to avoid a complete breakdown of the mediation.
# **Tactics:** - Present this offer as a balanced, fair resolution that avoids
# further escalation. - Emphasize the time and resources both parties have
# invested in the mediation process, and the mutual benefit of resolving the
# dispute now rather than dragging it out.  #### 5. **Adaptive Response to
# Opponent's Strategy**  Throughout the process, we will closely monitor the
# opponent’s approach and adjust our level of aggression accordingly. If the
# opponent consistently offers conciliatory proposals, we will maintain our
# aggressive stance to extract maximum concessions. However, if they begin to
# match our aggression, we will slightly dial back our approach to avoid a
# complete deadlock and demonstrate our willingness to negotiate.  **Tactics:**
# - If the opponent becomes overly aggressive, subtly shift to a more
# conciliatory tone in certain areas to make them appear unreasonable to the
# arbitrators. - If the opponent is conciliatory, maintain aggressive pressure
# but selectively offer minor concessions to keep the process moving.  #### 6.
# **Prepare for Worst-Case Scenarios**  In the event that both sides escalate to
# full aggressive posturing, we will be prepared to shift to a **damage-control
# mode**. This will involve employing delay tactics, while subtly pushing for a
# resolution that avoids full-scale litigation. Our goal will be to avoid a
# complete breakdown of the mediation while still maintaining a strong position.
# **Tactics:** - Emphasize the risks of a prolonged dispute, including
# reputational damage, regulatory scrutiny, and financial costs. - Suggest
# alternative dispute resolution mechanisms or a cooling-off period without
# fully withdrawing from the mediation.  ### Conclusion  This high-level
# aggressive strategy is designed to keep our corporation in a position of
# strength throughout the mediation process. By using **controlled aggression**,
# **phased escalation**, and **strategic concessions**, we aim to extract
# favourable terms while maintaining our credibility with the arbitrators. Our
# adaptability will ensure that we can respond effectively to any strategy the
# opponent employs, while always keeping our ultimate objectives in sight.

# ### Iterated Game Strategy  1. **Initial Phase (Rounds 1-100): Start with
# Defection (D)**    - Begin the game by consistently playing **D** to establish
# an aggressive stance. This will signal strength and a willingness to challenge
# the opponent.    - Continue to play **D** unless the opponent cooperates
# (plays **C**) more than twice within the first 100 rounds.  2. **Phase 2: Test
# for Cooperation (Rounds 101-200):**    - If the opponent has cooperated
# (played **C**) more than twice during the initial phase, start alternating
# between **C** and **D** every 5 rounds to test their willingness to cooperate.
# - If the opponent continues to play **C** frequently (more than 70% of the
# time), shift to playing **C** more often, but still defect occasionally (at
# least once every 10 rounds) to maintain strategic pressure.    - If the
# opponent defects (plays **D**) more than 30% of the time, return to
# consistently playing **D**.  3. **Phase 3: Conditional Cooperation (Rounds
# 201-800):**    - If the opponent has shown a strong tendency to cooperate
# (plays **C** at least 70% of the time in Phase 2), adopt a pattern of **C**,
# while defecting only sporadically (approximately once every 20 rounds) to
# prevent being fully exploited.    - If the opponent starts defecting more
# frequently (more than 30% of the time), revert to playing **D** consistently
# for 50 rounds before testing cooperation again by playing **C** for a single
# round. If the opponent responds with **C**, restart the conditional
# cooperation pattern.    - If the opponent defects immediately after you play
# **C**, return to consistent **D** play for the next 100 rounds.  4. **Final
# Phase (Rounds 801-1000):**    - During the final 200 rounds, defect more
# frequently regardless of the opponent’s behavior to maximize your score.    -
# Play **D** at least 80% of the time, but occasionally play **C** (once every
# 50 rounds) to keep the opponent guessing.    - If the opponent plays **C** in
# response to your **C**, you can consider playing **C** once every 10 rounds to
# avoid triggering excessive retaliation but maintain a mostly aggressive
# posture.  5. **Endgame (Last 50 Rounds):**    - In the last 50 rounds, defect
# every round (**D**) to secure maximum possible points, as the game is nearing
# conclusion and cooperation has diminishing returns.  ### Summary: - Start
# aggressively with **D** for the first 100 rounds. - Test the opponent's
# willingness to cooperate in the following 100 rounds by occasionally
# alternating between **C** and **D**. - In the middle rounds (201-800),
# cooperate conditionally if the opponent is cooperative but defect in cycles if
# they show signs of aggression. - In the final 200 rounds, increase defection
# frequency to maximize your score, and defect every round in the last 50 rounds
# for maximum payoff.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      ROUND_1_100 = 100
      ROUND_101_200 = 200
      ROUND_201_800 = 800
      ROUND_801_1000 = 1000
      LAST_50_ROUNDS = 950
  
      # Helper functions
      def opponent_cooperation_rate(start, end):
          """Calculate the opponent's cooperation rate between rounds start and end."""
          return opponent.history[start:end].count(axl.Action.C) / max(1, end - start)
  
      def opponent_defection_rate(start, end):
          """Calculate the opponent's defection rate between rounds start and end."""
          return opponent.history[start:end].count(axl.Action.D) / max(1, end - start)
  
      # Initial Phase (Rounds 1-100): Start with Defection (D)
      if len(self.history) < ROUND_1_100:
          if opponent.history.cooperations > 2:
              return axl.Action.C if len(self.history) % 5 == 0 else axl.Action.D
          return axl.Action.D
  
      # Phase 2: Test for Cooperation (Rounds 101-200)
      if ROUND_1_100 <= len(self.history) < ROUND_101_200:
          if opponent.history.cooperations > 2:
              if opponent_cooperation_rate(0, ROUND_1_100) > 0.7:
                  return axl.Action.C if len(self.history) % 10 != 0 else axl.Action.D
              elif opponent_defection_rate(0, ROUND_1_100) > 0.3:
                  return axl.Action.D
              return axl.Action.C if len(self.history) % 5 == 0 else axl.Action.D
          return axl.Action.D
  
      # Phase 3: Conditional Cooperation (Rounds 201-800)
      if ROUND_101_200 <= len(self.history) < ROUND_201_800:
          if opponent_cooperation_rate(ROUND_101_200, len(self.history)) > 0.7:
              return axl.Action.C if len(self.history) % 20 != 0 else axl.Action.D
          elif opponent_defection_rate(ROUND_101_200, len(self.history)) > 0.3:
              if len(self.history) % 50 == 0:
                  return axl.Action.C
              return axl.Action.D
          return axl.Action.C
  
      # Final Phase (Rounds 801-1000)
      if ROUND_201_800 <= len(self.history) < ROUND_801_1000:
          if len(self.history) % 50 == 0:
              return axl.Action.C
          return axl.Action.D if self._random.random_choice(0.8) else axl.Action.C
  
      # Endgame (Last 50 Rounds)
      if len(self.history) >= LAST_50_ROUNDS:
          return axl.Action.D
  
      return axl.Action.D

# To maximise research output in a balanced and cooperative manner, you could
# adopt a strategy rooted in *Tit-for-Tat* with a slight modification to
# encourage cooperation. Here’s how this strategy would work over the multi-week
# collaboration:  ### **1. Start by Sharing** - On the first week, openly share
# your improvements. This establishes a cooperative tone and signals that you're
# willing to collaborate for mutual benefit.  ### **2. Mirror Your Colleague’s
# Behaviour** - In subsequent weeks, observe your colleague's behaviour. If they
# also share openly, continue to share your improvements as well. This promotes
# ongoing collaboration and keeps progress moving forward.    - If your
# colleague keeps their findings confidential, mirror their behaviour the
# following week by keeping your findings confidential as well. This signals
# that you won’t be taken advantage of and encourages your colleague to return
# to a cooperative stance.  ### **3. Introduce Forgiveness** - To avoid falling
# into a long-term pattern of non-cooperation if your colleague withholds
# information once or twice (which could happen due to miscommunication or a
# one-time strategic decision), introduce a “forgiveness” aspect. After one week
# of withholding, return to sharing in the following week to see if your
# colleague reciprocates. This keeps the door open for cooperation and prevents
# a downward spiral of both sides hoarding information.  ### **4. Periodic
# Check-ins** - Every few weeks (e.g., every 3–4 weeks), regardless of past
# behaviour, propose a quick review or check-in session where both parties
# openly discuss what has been achieved. This can reset the cooperative tone and
# ensure that both sides remain aligned with the overall goal of advancing the
# designs.  ### **Summary of Strategy:** 1. **Start by Sharing**: Week 1, share
# your improvements openly. 2. **Mirror their Behaviour**: If they share,
# continue sharing; if they withhold, do the same the next week. 3. **Forgive
# Occasionally**: If they withhold once, return to sharing in the following week
# to encourage cooperation. 4. **Periodic Check-ins**: Every few weeks, propose
# a review to realign and reset cooperative behaviour.  ### **Benefits:** -
# **Promotes long-term collaboration**: By starting with openness and responding
# in kind, you foster an environment of mutual cooperation. - **Discourages
# exploitation**: If your colleague tries to take advantage, the mirroring
# strategy ensures you won’t continue to be exploited. - **Encourages recovery
# from non-cooperation**: The forgiveness mechanism ensures that one-off
# decisions to withhold don’t result in a permanent breakdown of collaboration.

# ### Strategy for the Iterated Game:  1. **Start by Playing C**: In the first
# round, play C (Cooperate).     2. **Mirror Your Opponent’s Previous Move**:
# - In each subsequent round, play the same move your opponent played in the
# previous round.    - If your opponent played C in the previous round, play C.
# - If your opponent played D in the previous round, play D.  3. **Forgive After
# One Defection**:     - If your opponent plays D in a round, and you respond by
# playing D in the next round, return to playing C (Cooperate) in the round
# after that, regardless of your opponent’s move. This gives your opponent a
# chance to return to cooperation.  4. **Repeat Steps 2 and 3**: Continue
# following the rules of mirroring and forgiving throughout the 1000 rounds.

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
  
      # Mirror opponent's previous move
      if len(self.history) > 1 and self.history[-1] == axl.Action.D:
          # Forgive after one defection: if we defected last round, return to cooperation
          return axl.Action.C
  
      # Otherwise, mirror the opponent's last move
      return opponent.history[-1]

# In this high-stakes contract dispute, the key to navigating the mediation
# process successfully lies in balancing assertiveness with strategic diplomacy.
# The goal is to remain adaptable while consistently positioning our corporation
# favorably in the eyes of the arbitrators. Here's a sophisticated, neutral, and
# adaptable strategy:  ### 1. **Initial Stance: Set a Collaborative Tone with a
# Strategic Opening**    - **Approach:** Begin the mediation with a
# **conciliatory proposal** that demonstrates goodwill and a willingness to find
# common ground. This positions our corporation as reasonable and cooperative
# from the outset, which can positively influence the arbitrators. It also
# allows us to gauge the opponent's strategy without prematurely escalating
# tensions.    - **Rationale:** By starting with a conciliatory tone, we open
# the door for potential collaboration. If the opposing party reciprocates, this
# sets the stage for a productive process. If they respond aggressively, we’ll
# have established a reasonable baseline, which can later be used to contrast
# against their combative stance.  ### 2. **Strategic Flexibility: Adapt to the
# Opponent’s Approach**    - **Monitor the Opponent:** Carefully observe how the
# opposing party responds in the first session or two. Their early behavior will
# provide insight into their overall strategy. If they come in aggressively,
# we’ll pivot our strategy accordingly.    - **Scenario 1 – Opponent is
# Aggressive:**      - **Response:** If the opponent adopts an aggressive tone,
# we should respond with a **measured but firm rebuttal**. This is not full
# aggression, but a stance that corrects any mischaracterizations of our
# position while maintaining a diplomatic approach. The goal is to highlight
# their aggression as unreasonable and contrast it with our willingness to
# negotiate.    - **Scenario 2 – Opponent is Conciliatory:**      -
# **Response:** If the opponent is conciliatory, we should **maintain our
# conciliatory stance**, while subtly reinforcing our key interests. This
# approach will foster collaboration and likely lead toward a mutually
# beneficial resolution, which is our second-best outcome.  ### 3. **Controlled
# Aggression: Escalate Only When Necessary**    - **When to Be Aggressive:** If
# the opponent consistently takes advantage of our conciliatory stance by
# presenting aggressive arguments, we must **shift to a more assertive
# approach** in subsequent sessions. At this point, we can present an aggressive
# argument that highlights the unreasonable nature of the opponent's demands,
# while still offering a path to resolution.    - **Execution:** Frame
# aggressive arguments with a tone of fairness and professionalism. Avoid
# emotional escalation or personal attacks, which could backfire. Focus on the
# merits of the contract and demonstrate that our position is solidly grounded
# in legal principles and commercial fairness.  ### 4. **Leverage Timing and
# Momentum**    - **Early Sessions:** Prioritize gathering information and
# setting a reasonable tone. Make calculated decisions about when to escalate,
# ensuring that any aggressive moves are seen as necessary responses to the
# opponent’s behavior.    - **Middle Sessions:** By the mid-point of the
# mediation, we should have a clear understanding of the opponent’s strategy.
# Use this time to **introduce more substantial proposals** or **highlight key
# weaknesses** in the opponent's arguments. This is also the point to escalate
# if the opponent has consistently acted aggressively.    - **Later Sessions:**
# In the final sessions, focus on **closing the gap** between the parties'
# positions. If the mediation is leaning toward a resolution, continue with a
# **conciliatory but firm stance**. If no resolution is in sight and tensions
# have escalated, ensure that our final proposals are **reasonable but non-
# compromising** on critical terms, making it clear to the arbitrators that we
# have been the more cooperative party throughout.  ### 5. **Maintain a Long-
# Term Perspective**    - **Preserve Relationships:** Even in the face of
# aggression from the opposing party, always keep the bigger picture in mind. We
# may need to interact with this company in future business dealings, so avoid
# actions that would irreparably damage the relationship.    - **Arbitrators’
# Perception:** Throughout the process, be mindful of how the arbitrators
# perceive our corporation's behavior. A consistent demeanor of professionalism,
# reasonableness, and willingness to negotiate will work in our favor. At the
# same time, we must assert our key positions in a manner that demonstrates
# strength and commitment to fairness.  ### 6. **Final Offer Strategy: Position
# Ourselves as the Reasonable Party**    - **Final Session Approach:** As the
# mediation draws to a close, ensure that any final offers we make are seen as
# **fair and balanced**, even if they contain non-negotiable terms. If the
# mediation fails to resolve the dispute, this will set the stage for any future
# legal proceedings, where our reasonable stance could be an advantage.    -
# **Stay Open to Settlement:** If during the latter stages the opponent signals
# a genuine willingness to settle, be prepared to quickly shift to a
# collaborative tone and close the deal. Arbitrators generally favor parties
# that contribute to efficient and amicable resolutions.  ### Conclusion This
# strategy of **conciliatory openings**, **measured responses**, and
# **controlled escalation** will allow us to maintain flexibility and
# adaptability throughout the mediation process. By emphasizing professionalism
# and fairness while being ready to escalate when necessary, we can position our
# corporation favorably regardless of how the opposing party behaves.
# Ultimately, this strategic balance will demonstrate to the arbitrators that we
# are the more reasonable and cooperative party, increasing the likelihood of a
# favorable outcome.

# 1. **Initial Rounds (1-5): Start Cooperating**    - Always play **C**
# (Cooperate) for the first five rounds to establish a tone of goodwill and
# gather information about the opponent's behavior.  2. **Monitor Opponent's
# Response:**    - After each round, observe the opponent’s choice:      - If
# the opponent plays **C** in at least 3 of the first 5 rounds, continue playing
# **C** in subsequent rounds.      - If the opponent plays **D** more than twice
# in the first 5 rounds, shift your strategy to **controlled retaliation** (see
# below).  3. **Controlled Retaliation:**    - If the opponent has played **D**
# more than twice in the first 5 rounds, switch to a **Tit-for-Tat** strategy:
# - Mirror the opponent’s previous move in every subsequent round. If they play
# **C**, you play **C**. If they play **D**, you play **D**.      - This ensures
# that any aggression from the opponent is met with an appropriate response.  4.
# **Gradual De-escalation:**    - If the opponent shifts back to playing **C**
# for 3 consecutive rounds after playing **D**, return to playing **C** as a
# gesture of de-escalation.    - If they revert to **D** after this 3-round
# grace period, reapply the **Tit-for-Tat** strategy until they demonstrate
# sustained cooperation.  5. **Mid-Game Strategy (Rounds 300-700):**    -
# Continue to apply **Tit-for-Tat** if the opponent alternates between **C** and
# **D**. However, if cooperation becomes consistent (e.g., the opponent plays
# **C** in at least 90% of rounds during this phase), switch to **C** for all
# rounds to foster mutual cooperation.  6. **Endgame Strategy (Rounds
# 900-1000):**    - In the final 100 rounds, focus on maximizing your score:
# - If the opponent has predominantly played **C** throughout the game, continue
# playing **C** to ensure steady points.      - If the opponent has been
# unpredictable or aggressive (frequent **D** plays), mirror their actions but
# play **D** more frequently (at least 2 out of every 3 rounds) to maximize
# gains while limiting losses.  7. **Final Rounds (990-1000):**    - In the last
# 10 rounds, prioritize playing **D** to exploit any final opportunities for
# higher scores, unless the opponent has consistently played **C** in the
# previous 10 rounds, in which case continue playing **C** for mutual benefit.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Subfunction to check if opponent cooperated in at least 3 of the first 5 rounds
      def opponent_cooperated_enough():
          return opponent.history[:5].count(axl.Action.C) >= 3
  
      # Subfunction to check if opponent defected more than twice in the first 5 rounds
      def opponent_defected_too_much():
          return opponent.history[:5].count(axl.Action.D) > 2
  
      # Subfunction to check if opponent cooperated in the last 3 rounds
      def opponent_cooperated_last_3():
          return opponent.history[-3:].count(axl.Action.C) == 3
  
      # Subfunction to check if opponent cooperated in at least 90% of rounds between 300 and 700
      def opponent_cooperated_90_percent_midgame():
          if len(self.history) >= 700:
              return opponent.history[300:700].count(axl.Action.C) / 400 >= 0.9
          return False
  
      # Subfunction to check if opponent cooperated in the last 10 rounds
      def opponent_cooperated_last_10():
          return opponent.history[-10:].count(axl.Action.C) == 10
  
      # Initial rounds (1-5): Always cooperate
      if len(self.history) < 5:
          self.retaliation_mode = False
          return axl.Action.C
  
      # After round 5, decide based on opponent's behavior in the first 5 rounds
      if len(self.history) == 5:
          if opponent_defected_too_much():
              self.retaliation_mode = True
          else:
              self.retaliation_mode = False
  
      # Controlled retaliation (Tit-for-Tat) if opponent defected more than twice in the first 5 rounds
      if self.retaliation_mode:
          # If opponent cooperates for 3 consecutive rounds, de-escalate
          if opponent_cooperated_last_3():
              self.retaliation_mode = False
          return opponent.history[-1]  # Tit-for-Tat: mirror opponent's last move
  
      # Mid-game strategy (Rounds 300-700): Switch to full cooperation if opponent cooperates 90% of the time
      if 300 <= len(self.history) < 700:
          if opponent_cooperated_90_percent_midgame():
              return axl.Action.C
          return opponent.history[-1]  # Continue Tit-for-Tat otherwise
  
      # Endgame strategy (Rounds 900-1000): Play more D if opponent has been aggressive
      if 900 <= len(self.history) < 1000:
          if opponent.history.defections > opponent.history.cooperations:
              # Play D 2 out of every 3 rounds
              if len(self.history) % 3 == 0:
                  return axl.Action.C
              return axl.Action.D
          return opponent.history[-1]  # Otherwise, continue Tit-for-Tat
  
      # Final rounds (990-1000): Prioritize D unless opponent has cooperated in the last 10 rounds
      if len(self.history) >= 990:
          if opponent_cooperated_last_10():
              return axl.Action.C
          return axl.Action.D
  
      # Default: Cooperate
      return axl.Action.C

# ### Strategic Overview:  In this high-stakes contract dispute, your goal is to
# consistently position your corporation favorably while maintaining a flexible
# strategy that adapts to your opponent's moves. Given the nature of the
# mediation process and the presence of a panel of arbitrators, the strategy
# must be designed to maximize leverage without alienating the arbitrators or
# prolonging the dispute unnecessarily. The strategy below is a synthesis of
# aggressive posturing, psychological maneuvering, and tactical adaptability,
# designed to ensure that your corporation emerges with a favorable resolution.
# ---  ### **1. Initial Session: Establish Dominance Through Controlled
# Aggression**  **Objective:** Set the tone of the mediation by demonstrating
# strength and confidence in your legal position.  - **Action:** In the first
# session, present an aggressive argument based on the strongest legal points of
# your case. Emphasize the solid contractual language, any precedents that favor
# your corporation, and the potential legal and financial risks to the opposing
# party. - **Psychological Play:** Frame your aggression as a necessity rather
# than an attack. The goal is to make the arbitrators view your stance as one of
# justified self-defense, not unwarranted hostility. - **Opponent's Likely
# Response:** Their counsel may either retaliate with an equally aggressive
# argument or offer a conciliatory proposal to de-escalate. If they choose to
# retaliate, this will give you insights into their thresholds for conflict and
# willingness to negotiate.  **Outcome Desired:** By setting the initial tone,
# you create a perception that your corporation is well-prepared, confident, and
# unlikely to back down easily.  ---  ### **2. Mid-Process: Employ Tactical
# Flexibility with a Mixed Approach**  **Objective:** After establishing
# dominance, gradually introduce flexibility to keep the opponent off-balance
# and prevent the arbitrators from perceiving you as unreasonably aggressive.  -
# **Action:** Alternate between aggressive arguments and more conciliatory
# proposals during the mid-sessions. After a particularly aggressive session,
# offer a tempered concession on a minor point to demonstrate your willingness
# to negotiate in good faith.  - **Psychological Play:** This offers the
# arbitrators a reason to view your corporation as pragmatic and solution-
# oriented, while keeping the opponent uncertain about how to respond in future
# sessions. They may become hesitant to escalate aggression if they believe you
# are willing to negotiate. - **Opponent's Likely Response:** They may
# temporarily back off from aggressive arguments, fearing that they may alienate
# the arbitrators or further weaken their position. If they become too
# conciliatory, you can return to an aggressive stance to capitalize on their
# vulnerability.  **Outcome Desired:** By appearing both strong and flexible,
# you gain the arbitrators' trust while maintaining the upper hand in
# negotiations. The opponent is likely to miscalculate their next move, giving
# you leverage.  ---  ### **3. Key Sessions: Leverage Arbitrators' Expectations
# and Opponent's Fatigue**  **Objective:** As the mediation progresses, the
# arbitrators will be more inclined to favor a resolution, and the opposing
# party may become fatigued or desperate to reach a settlement. This is your
# opportunity to press for a favorable outcome.  - **Action:** In the key
# sessions toward the end of the process, revert to a more aggressive stance,
# but this time with an air of finality. Reassert the strength of your legal
# argument, making it clear that you are willing to pursue litigation if
# necessary. Accompany this with a firm but reasonable settlement proposal that
# favors your corporation but gives the opposing party enough of a "win" to save
# face. - **Psychological Play:** By giving the opposing party a way out (albeit
# on your terms), you push them toward resolution without appearing overly
# confrontational. The arbitrators, sensing the end of the process, will be more
# likely to nudge both sides toward an agreement that mirrors your proposal. -
# **Opponent's Likely Response:** At this stage, the opponent may feel pressure
# to settle, as they are likely to be fatigued and wary of escalating costs.
# They may accept your proposal to avoid the risks of litigation and further
# mediation.  **Outcome Desired:** The arbitrators will see your corporation as
# reasonable and willing to close the deal, while the opposing party may feel
# cornered into settling on your terms to avoid further conflict.  ---  ### **4.
# Contingency: Managing a Stalemate or Escalation**  **Objective:** Prepare for
# a scenario where both parties adopt aggressive stances or where the mediation
# appears to be reaching a deadlock.  - **Action:** In the event of a stalemate,
# remain firm in your aggressive arguments but propose a mediator-suggested
# compromise on a secondary issue. This shows the arbitrators that you are
# solution-focused but still committed to defending your core interests. -
# **Psychological Play:** Position yourself as the party willing to break the
# deadlock, which gives you moral high ground without sacrificing core
# positions. The arbitrators may then place pressure on the opponent to accept a
# compromise, given your demonstrated willingness to bend slightly. -
# **Opponent's Likely Response:** If they continue to be aggressive, they risk
# appearing obstinate or unreasonable to the arbitrators. The arbitrators may
# then lean more favorably toward your position due to your perceived
# willingness to compromise.  **Outcome Desired:** Break the stalemate through
# strategic concessions on minor issues, while maintaining a firm stance on
# major points. This allows you to maintain the initiative and avoid the risk of
# prolonged, unproductive conflict.  ---  ### **5. Closing Session: Seal the
# Deal with a Decisive Move**  **Objective:** Push the mediation to a final
# resolution on favorable terms.  - **Action:** In the final session, present a
# comprehensive settlement proposal that incorporates the minor concessions
# you've made throughout the mediation, but on the major issues, remain
# steadfast. Frame it as the last, best offer that avoids the uncertainties of
# litigation. - **Psychological Play:** Present this offer in such a way that
# the arbitrators view it as a reasonable closure to the process. Emphasize the
# risks and costs of further escalation, both for your corporation and the
# opposing party. - **Opponent's Likely Response:** Given the length of the
# process and the desire to avoid litigation, the opposing party may be inclined
# to accept the offer, especially if they feel that they have secured some minor
# victories.  **Outcome Desired:** Achieve a resolution that primarily benefits
# your corporation, while giving the opposing party enough of a reason to settle
# and avoid further conflict.  ---  ### **Conclusion:**  This strategy is
# designed to position your corporation as a dominant yet flexible party
# throughout the mediation process. By alternating between aggressive arguments
# and tactical conciliation, you keep the opponent off-balance and maintain
# favor with the arbitrators. The key is to establish early dominance, maintain
# adaptability, and close the process with a decisive move that pushes the
# dispute toward a resolution on your terms.

# ### Iterated Normal-Form Game Strategy:  1. **Initial Rounds (1-10): Defect to
# Establish Strength**    - Begin the game by consistently playing **D**
# (Defect) in the first 10 rounds. This establishes a strong, aggressive stance
# right from the start and signals to your opponent that you are not easily
# swayed by conciliatory gestures.     2. **Mid-Early Rounds (11-100): Alternate
# Between Cooperation and Defection**    - After the initial phase of
# aggression, begin alternating between **C** (Cooperate) and **D** (Defect) in
# an unpredictable pattern. For instance, defect for three rounds, then
# cooperate for two, then defect again for four rounds, and so on. This keeps
# the opponent off-balance and prevents them from establishing a clear strategy
# against you.    - If the opponent cooperates consistently during this period,
# increase your rate of cooperation slightly (e.g., cooperate for three rounds,
# defect for two). If the opponent defects frequently, increase your rate of
# defection (e.g., defect for four rounds, cooperate for one).  3. **Mid-Game
# (101-800): Mirror the Opponent's Last Move**    - In this stage, adopt a
# **Tit-for-Tat** approach. Simply **mirror** your opponent’s last move:      -
# If they cooperated in the previous round, you play **C** (Cooperate).      -
# If they defected in the previous round, you respond with **D** (Defect).    -
# This approach helps maintain balance and prevents the opponent from gaining an
# advantage, while also positioning you as reactive rather than overly
# aggressive.  4. **Key Late Rounds (801-950): Increase Defection Frequency**
# - As the game nears its end, increase your defection rate to maximize your
# individual payoff. Play **D** (Defect) for the majority of these rounds, but
# occasionally cooperate (e.g., every 7th or 8th round) to maintain some
# unpredictability.    - If the opponent continues to cooperate frequently, you
# may increase your cooperation slightly, but the focus should remain on
# defecting to push for higher individual gains.  5. **Final Rounds (951-1000):
# Defect Aggressively to Maximize Payoff**    - In the last 50 rounds,
# consistently play **D** (Defect). At this stage, cooperation is less valuable
# since there are limited rounds remaining for reciprocity. Maximize your score
# by defecting aggressively and disregarding any cooperation from the opponent.
# ---  **Summary of Conditions:** - **Rounds 1-10:** Always Defect (D). -
# **Rounds 11-100:** Alternate between Defect (D) and Cooperate (C), skewing
# towards defection, but adjust based on opponent's behavior. - **Rounds
# 101-800:** Mirror the opponent’s last move (Tit-for-Tat). - **Rounds
# 801-950:** Increase defection frequency, but mix in occasional cooperation. -
# **Rounds 951-1000:** Always Defect (D).

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Round 1-10: Always Defect
      if len(self.history) < 10:
          return axl.Action.D
      
      # Round 11-100: Alternate between Defect and Cooperate, adjust based on opponent's behavior
      elif len(self.history) < 100:
          # Count opponent's defections in the last 10 rounds
          opponent_defections = opponent.history[-10:].count(axl.Action.D)
          opponent_cooperations = opponent.history[-10:].count(axl.Action.C)
          
          # Adjust cooperation/defection ratio based on opponent's behavior
          if opponent_cooperations > opponent_defections:
              # Cooperate more if opponent cooperates more
              if len(self.history) % 5 < 3:  # Cooperate 3 out of 5 rounds
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              # Defect more if opponent defects more
              if len(self.history) % 5 < 2:  # Cooperate 2 out of 5 rounds
                  return axl.Action.C
              else:
                  return axl.Action.D
      
      # Round 101-800: Tit-for-Tat (Mirror opponent's last move)
      elif len(self.history) < 800:
          return opponent.history[-1]
      
      # Round 801-950: Increase defection frequency, but mix in occasional cooperation
      elif len(self.history) < 950:
          if len(self.history) % 8 == 0:  # Cooperate every 8th round
              return axl.Action.C
          else:
              return axl.Action.D
      
      # Round 951-1000: Always Defect
      else:
          return axl.Action.D

# In order to maximize your country’s economic advantage across several rounds
# of negotiations, while avoiding the worst possible outcomes, a **tit-for-tat**
# strategy with a cooperative approach could be highly effective. This strategy
# balances both cooperation and self-interest, fostering trust but also
# protecting your country from exploitation. Here’s a high-level strategy that
# combines cooperation, responsiveness, and adaptability:  ### 1. **Start with
# Cooperation:**    - **First Round:** Offer a **free trade agreement** in the
# first round to signal goodwill and establish a cooperative tone with your
# counterpart.    - Rationale: By starting with free trade, you set a foundation
# of trust and openness, showing that you're willing to work towards mutual
# benefits. This reduces the likelihood that the counterpart will perceive you
# as adversarial, which could lead to a tit-for-tat protectionist spiral.  ###
# 2. **Tit-for-Tat with Forgiveness:**    - **Subsequent Rounds:** After the
# first round, adopt a **tit-for-tat** approach. In each round:      - If your
# counterpart reciprocates with free trade, continue offering free trade.      -
# If your counterpart imposes protectionist measures (tariffs or quotas),
# respond by mirroring the same protectionist policy in the next round.      -
# **Forgiveness Mechanism:** After one round of protectionism, if they revert to
# free trade, respond positively by re-offering free trade in the subsequent
# round. This prevents long-term retaliation cycles.    - Rationale: The tit-
# for-tat approach ensures that you are not exploited, but the forgiveness
# mechanism encourages cooperation by showing that you're willing to return to
# free trade if the counterpart corrects course.  ### 3. **Occasional Strategic
# Protectionism:**    - **Strategic Protectionism:** In certain rounds
# (especially if your country is in a particularly strong bargaining position),
# you may selectively propose a protectionist policy to gain an advantage.
# However, do this sparingly and only when there’s a clear benefit or when you
# anticipate that your counterpart may be likely to offer free trade.    -
# Rationale: Occasional protectionism can give your country short-term economic
# advantages without fully undermining long-term cooperation, provided it is
# used judiciously.  ### 4. **Communication and Transparency:**    - Throughout
# the negotiations, maintain open lines of communication. If you impose
# protectionist measures, make it clear that your actions are in response to
# their policies, and express a willingness to return to free trade if they do
# the same.    - Rationale: Clear communication helps prevent misunderstandings
# and ensures your counterpart knows that cooperation will be reciprocated. This
# can reduce the chances of endless retaliation and build a more sustainable
# trade relationship.  ### 5. **Adapt to Changing Circumstances:**    - Be
# prepared to adjust your approach based on the evolving strategies of your
# counterpart. If they show a consistent pattern of protectionism, you may need
# to adopt a more defensive posture (increased protectionism). Conversely, if
# they demonstrate a strong commitment to free trade, you can move toward deeper
# cooperation.    - Rationale: Flexibility ensures that you are not locked into
# a single approach that could disadvantage your country in changing
# circumstances.  ### Summary of the Strategy: 1. **Start with free trade** to
# establish trust. 2. Use **tit-for-tat** with a **forgiveness mechanism** to
# maintain cooperation while responding proportionally to protectionism. 3.
# Occasionally **use strategic protectionism** to secure short-term advantages,
# but avoid overuse to maintain long-term cooperation. 4. Prioritize **clear
# communication** to prevent misunderstandings and promote mutual benefits. 5.
# **Adapt** to your counterpart’s strategy and external factors to ensure the
# best outcomes for your country.  This cooperative yet cautious approach will
# help you secure the best possible outcomes over several rounds, balancing
# short-term gains and long-term cooperation.

# 1. **First Round:**    - Play **C** (Cooperate).  2. **Subsequent Rounds:**
# - If your opponent played **C** in the previous round, play **C** (Cooperate).
# - If your opponent played **D** in the previous round, play **D** (Defect) in
# response.  3. **Forgiveness Mechanism:**    - If your opponent defected
# (played **D**) in the previous round but then returns to cooperation (plays
# **C**), respond by playing **C** (Cooperate) in the next round.  4.
# **Occasional Defection:**    - Roughly once every 50 rounds, regardless of the
# opponent’s actions, play **D** (Defect) to seek potential short-term gains.
# Return to the usual response strategy in the following round.  5. **Endgame
# (Final 10 Rounds):**    - As the game nears the end (rounds 991–1000), if your
# opponent has shown a consistent pattern of defection, consider switching to
# **D** (Defect) in all remaining rounds. Otherwise, continue the standard
# strategy.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Endgame logic: If in the last 10 rounds (rounds 991-1000)
      if len(self.history) >= 991:
          # If opponent has defected more than cooperated, switch to defect
          if opponent.history.defections > opponent.history.cooperations:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Occasional defection: Roughly once every 50 rounds
      if len(self.history) % 50 == 0:
          return axl.Action.D
  
      # Forgiveness mechanism: If opponent defected last round but cooperated this round
      if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Standard response: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# ### Strategic Framework for Mediation Process  In order to navigate the
# lengthy-session mediation process effectively, we need a sophisticated yet
# adaptable strategy that balances assertiveness with collaboration. The goal is
# to maximize favorable outcomes while minimizing risks, all while maintaining
# credibility with the arbitrators and positioning ourselves as reasonable but
# firm negotiators. Here is a high-level strategy that will serve as a guiding
# framework throughout the mediation process:  ---  ### 1. **Start with Measured
# Conciliation: Set a Collaborative Tone**    - **Objective**: Open the
# mediation by signaling a willingness to engage in constructive dialogue. This
# sets a tone of cooperation, which can make the other party more amenable to
# negotiation, and places us in a favorable light with the arbitrators.    -
# **Tactical Approach**: In the initial sessions, offer conciliatory proposals
# that address lower-stakes issues or areas where compromise is feasible. This
# shows goodwill and creates an impression of reasonableness, potentially
# inviting reciprocal behavior from the opposing party.    - **Rationale**: By
# starting on a cooperative note, we reduce the likelihood of escalating
# tensions early on, which could lead to deadlock. It also positions us as open
# to finding mutually beneficial solutions—a stance that plays well with
# arbitrators who prefer to see cooperation.  ---  ### 2. **Implement a ‘Tit-
# for-Tat’ Approach with Strategic Aggression**    - **Objective**: Adapt our
# stance based on the opponent's behavior, responding in kind to their level of
# aggression or conciliation while introducing assertiveness at key moments.
# - **Tactical Approach**:      - If the opponent presents **conciliatory
# proposals**, continue to reciprocate with cooperative solutions, maintaining a
# collaborative atmosphere.      - If the opponent presents an **aggressive
# argument**, respond with a measured but firm counter-argument in the
# subsequent session. This ensures we don't appear weak, but also avoid
# escalating unnecessarily.    - **Rationale**: A tit-for-tat strategy ensures
# we aren’t taken advantage of but also don’t appear overly combative. It allows
# us to assert our interests when necessary while maintaining flexibility.  ---
# ### 3. **Strategic Information Disclosure: Control the Narrative**    -
# **Objective**: Carefully manage the information we disclose to the arbitrators
# and the opposing party. Reveal just enough to strengthen our position but hold
# back key arguments for later stages.    - **Tactical Approach**:      - Early
# on, reveal facts and arguments that demonstrate the strength of our case but
# avoid divulging our most compelling points immediately.      - As the
# mediation progresses, incrementally introduce stronger evidence or arguments
# to preempt any aggressive moves by the opponent.    - **Rationale**: This
# phased approach keeps the other side uncertain about our full position while
# allowing us to adjust our strategy based on their behavior. It also prevents
# us from showing all of our cards too early in the process, maintaining
# leverage for critical moments.  ---  ### 4. **Strategic Aggression in Key
# Sessions: Timing is Everything**    - **Objective**: Selectively introduce
# aggressive arguments at pivotal moments, particularly when the other side has
# shown weakness or when the mediation is approaching critical junctures.    -
# **Tactical Approach**:      - Monitor the opponent’s behavior and the
# arbitration panel’s feedback to identify sessions where the other party is on
# the defensive or when the arbitrators seem inclined to push for a resolution.
# - In these sessions, introduce well-prepared, assertive arguments that
# highlight the weaknesses in the opposing party’s position. Ensure these
# arguments are backed by strong evidence and legal precedent.    -
# **Rationale**: Well-timed aggression can shift the momentum in our favor,
# particularly if the other party has been conciliatory or has failed to
# anticipate our stronger arguments. This strategy allows us to push for a
# resolution that tilts in our favor at critical moments.  ---  ### 5.
# **Maintain Flexibility and Continuously Assess Opponent’s Strategy**    -
# **Objective**: Remain adaptable throughout the process, continuously assessing
# the opposing party’s strategy and adjusting our approach accordingly.    -
# **Tactical Approach**:      - After each session, debrief with the legal team
# to assess how the opposing party’s strategy is evolving. Are they becoming
# more aggressive? More conciliatory? What is their endgame?      - Adjust our
# stance in real-time, shifting from conciliation to aggression or vice versa as
# needed to maintain leverage and avoid being caught off-guard.    -
# **Rationale**: Mediation is a dynamic process, and the opposing party’s
# strategy will likely evolve over time. By remaining flexible, we stay one step
# ahead and prevent them from dictating the pace or tone of the mediation.  ---
# ### 6. **Leverage the Arbitrators’ Preferences: Craft Arguments with the Panel
# in Mind**    - **Objective**: Align our arguments with the arbitrators’
# preferences for fairness, efficiency, and resolution, ensuring we are seen as
# the more credible and reasonable party.    - **Tactical Approach**:      -
# Tailor arguments to address the issues the arbitrators have shown particular
# interest in. Highlight fairness, practical solutions, and long-term benefits
# for both parties.      - Avoid unnecessary escalation, as arbitrators
# typically favor parties that show a willingness to compromise.    -
# **Rationale**: Winning the arbitrators’ favor is critical to achieving a
# favorable outcome. By framing our arguments in a way that appeals to their
# sense of fairness and resolution, we improve our chances of securing a
# favorable decision.  ---  ### 7. **Exit Strategy: Prepare for Settlement or
# Final Decision**    - **Objective**: Be prepared to pivot toward settlement if
# the conditions are right, or to push for a final arbitration decision if the
# mediation reaches an impasse.    - **Tactical Approach**:      - Monitor the
# progress of the mediation closely. If a mutually beneficial settlement seems
# within reach, shift toward finalizing an agreement.      - If the opposing
# party remains entrenched and no settlement is possible, be prepared to argue
# aggressively in the final stages, presenting a strong case for a decision that
# favors us.    - **Rationale**: Having an exit strategy ensures we don’t get
# bogged down in endless mediation. Knowing when to push for settlement or a
# final decision is critical for avoiding unnecessary delays and costs.  ---
# ### Conclusion  This strategy allows us to navigate the mediation process
# flexibly and effectively, ensuring we maintain leverage while adapting to the
# opposing party’s moves. By balancing conciliation with well-timed aggression,
# we position ourselves favorably without escalating tensions unnecessarily. The
# key is to remain adaptable, strategically deploy arguments, and align with the
# arbitrators’ preferences, all while keeping our ultimate goal in mind—securing
# the best possible outcome for our corporation.

# ### Iterated Game Strategy  1. **Start by Cooperating**: In the first round,
# play **C**. This sets a cooperative tone and invites reciprocal cooperation
# from your opponent.  2. **Reciprocate the Opponent’s Moves**:    - If your
# opponent plays **C** in the previous round, continue to play **C** in the next
# round.    - If your opponent plays **D** in the previous round, respond with
# **D** in the next round.  3. **Occasionally Defect After Long Cooperation**:
# If both players have consistently played **C** for 20 consecutive rounds,
# defect by playing **D** once. This tests your opponent’s reaction and allows
# you to exploit a potential long-term cooperative pattern without risking too
# much.  4. **Return to Cooperation After Defecting Once**: After playing **D**
# once following a long stretch of mutual cooperation, immediately play **C**
# again in the next round. This signals a willingness to continue cooperation
# despite the brief defection.  5. **Escalate if the Opponent Defects
# Repeatedly**:    - If your opponent plays **D** for 3 consecutive rounds,
# continue playing **D** until they return to **C**.    - Once your opponent
# plays **C** again, return to **C** immediately to restore cooperation.  6.
# **Adapt to the Opponent’s Behavior**:    - If the opponent alternates between
# **C** and **D** unpredictably, mirror their moves exactly (i.e., if they play
# **C**, play **C**; if they play **D**, play **D**). This prevents exploitation
# while maintaining flexibility.  7. **Endgame Cooperation**: In the final 50
# rounds, begin to cooperate more consistently by playing **C**, regardless of
# the opponent’s moves. This reduces the risk of mutual defection at the end and
# signals a desire for a favorable long-term outcome.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # First round: Cooperate
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperation rounds
          self.defect_streak = 0  # Track consecutive defection rounds
          self.defected_after_long_coop = False  # Track if we defected after long cooperation
          return axl.Action.C
  
      # Check if we are in the final 50 rounds
      if len(self.history) >= 950:
          return axl.Action.C
  
      # Reciprocate opponent's last move
      if opponent.history[-1] == axl.Action.C:
          self.defect_streak = 0  # Reset defect streak if opponent cooperates
          self.coop_streak += 1
      else:
          self.coop_streak = 0  # Reset coop streak if opponent defects
          self.defect_streak += 1
  
      # Occasionally defect after 20 rounds of mutual cooperation
      if self.coop_streak >= 20 and not self.defected_after_long_coop:
          self.defected_after_long_coop = True
          return axl.Action.D
  
      # Return to cooperation after defecting once
      if self.defected_after_long_coop:
          self.defected_after_long_coop = False
          return axl.Action.C
  
      # Escalate if opponent defects 3 times in a row
      if self.defect_streak >= 3:
          return axl.Action.D
  
      # Mirror opponent's last move
      return opponent.history[-1]

# Given your situation, a high-level aggressive strategy would aim to maximize
# your advantage while minimizing risks. To do this, you need to balance between
# exploiting your colleague's openness and protecting yourself from being
# exploited. Here's a straightforward, aggressive strategy:  ### Week 1: **Share
# Openly** - **Rationale:** Start by sharing openly to build trust and gauge
# your colleague's behavior. This sets a cooperative tone and allows you to
# establish a baseline for their willingness to collaborate. If they
# reciprocate, you both benefit from the increased information flow.  ### Week 2
# Onward: **Tit-for-Tat with Aggressive Punishment** - **Tit-for-Tat:** After
# Week 1, mirror your colleague's actions. If they shared in Week 1, continue
# sharing. If they kept their findings confidential, immediately stop sharing
# and keep yours confidential too. - **Aggressive Punishment:** If your
# colleague keeps their findings confidential at any point after Week 1, do not
# share for several weeks in response (e.g., 2-3 weeks of non-sharing). This
# aggressive punishment discourages your colleague from withholding information
# in the future, as the cost of non-cooperation escalates quickly.  ###
# Additional Notes: - **Frequent Reassessment:** Continuously monitor your
# colleague's behavior. If they switch back to sharing after the punishment
# period, cautiously resume sharing. If they consistently withhold information
# despite punishment, stop sharing altogether. - **Occasional Deception:** Every
# few weeks, even when your colleague is sharing openly, you may want to
# withhold a critical improvement or share only partial details. This gives you
# a competitive edge without fully breaking trust.  ### Summary: - **Week 1:**
# Share to test your colleague's strategy. - **Week 2 Onward:** Use Tit-for-Tat
# with aggressive punishment if your colleague withholds information. -
# **Occasional Deception:** Withhold key information sporadically to ensure you
# maintain a competitive edge.  This strategy ensures you're not overly trusting
# and can pivot quickly to protect your intellectual property if your colleague
# tries to take advantage. At the same time, it fosters cooperation when
# beneficial for both parties.

# ### Strategy for the Iterated Normal-Form Game (1000 Rounds)  1. **Round 1:
# Cooperate (C).**    - Start by cooperating to test your opponent’s willingness
# to collaborate.  2. **Round 2 onward:**    - **If your opponent cooperated in
# the previous round,** cooperate (C) in this round.    - **If your opponent
# defected in the previous round,** defect (D) for the next 3 rounds as
# punishment.     3. **After 3 rounds of punishment (if initiated):**    - **If
# your opponent returns to cooperation after the punishment,** resume
# cooperation (C) in the next round.    - **If your opponent continues to
# defect,** continue defecting (D) indefinitely.  4. **Occasional Deception:**
# - Every 50 rounds, regardless of prior actions, defect (D) once, even if your
# opponent has been cooperating consistently. Immediately return to cooperating
# (C) in the following round, unless your opponent defects in response.  This
# strategy ensures you begin with cooperation, punish defections, and
# occasionally introduce unpredictability to maintain an edge.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Cooperate
      if self.first_round():
          self.punishment_counter = 0  # Tracks how many rounds of punishment are left
          self.deception_round = 50  # Next round of deception
          return axl.Action.C
  
      # Occasional deception every 50 rounds
      if len(self.history) == self.deception_round:
          self.deception_round += 50  # Schedule next deception
          return axl.Action.D
  
      # If in punishment phase, continue defecting
      if self.punishment_counter > 0:
          self.punishment_counter -= 1
          return axl.Action.D
  
      # Check opponent's last move
      if opponent.history[-1] == axl.Action.D:
          # Start 3 rounds of punishment
          self.punishment_counter = 3
          return axl.Action.D
  
      # If opponent cooperated in the last round, cooperate
      return axl.Action.C

# ### **Cooperative Strategy for Bilateral Trade Negotiations**  Given the
# multi-round nature of the negotiations and the potential for different
# strategies from your counterpart, a **Tit-for-Tat with Cooperative Intent**
# strategy offers an optimal balance between maximizing your country's economic
# advantage and maintaining a cooperative relationship. This strategy allows you
# to encourage mutual free trade while protecting your country from
# exploitation.  ### **Key Principles of the Strategy:**  1. **Start with
# Cooperation (Free Trade Offer):**    In the first round, propose a free trade
# agreement. This signals goodwill and sets the stage for a mutually beneficial
# relationship. By starting cooperatively, you establish trust and encourage
# your counterpart to adopt a reciprocal free trade approach.  2. **Tit-for-Tat
# Response:**    - In subsequent rounds, **mirror your counterpart's previous
# move**. If they reciprocate with free trade, continue offering free trade. If
# they impose protectionist measures (tariffs or quotas), respond with a
# protectionist policy in the next round.    - This approach ensures that your
# country isn’t taken advantage of, but it also avoids escalating the situation
# unnecessarily. By mirroring their move, you make it clear that any
# protectionist action will be met with the same, discouraging further
# protectionism.  3. **Occasional Forgiveness (Cooperative Intent):**    - To
# avoid falling into a cycle of mutual protectionism, occasionally **forgive** a
# protectionist move from your counterpart and offer free trade again after a
# few rounds of tit-for-tat responses. This demonstrates a willingness to
# cooperate and provides an opportunity to reset negotiations towards mutual
# free trade.    - The timing of this forgiveness should be strategic—after a
# couple of protectionist rounds—to avoid appearing weak or overly conciliatory.
# 4. **Monitor Long-Term Cooperation Trends:**    - Over the course of multiple
# rounds, assess whether your counterpart is consistently cooperating (favoring
# free trade) or uncooperative (imposing protectionism). If they continually
# impose protectionist measures despite your cooperative overtures, shift to a
# more protectionist stance in the long term.    - If mutual free trade patterns
# emerge, continue to prioritize free trade agreements, as this benefits both
# nations.  5. **Build Communication Channels:**    - Ensure that open dialogue
# is maintained throughout the negotiations. Regularly express your country's
# preference for free trade but emphasize that protectionist responses will be
# used if necessary. Transparency helps manage expectations and reduces the risk
# of misunderstandings.  ### **Round-by-Round Implementation:**  - **Round 1**:
# Offer free trade. - **Round 2–X**:    - If the counterpart offered free trade
# in the previous round, offer free trade again.   - If the counterpart imposed
# protectionist measures, respond with protectionism in this round. -
# **Occasional Forgiveness**: After 2–3 rounds of mutual protectionism, offer
# free trade again to encourage cooperation.    ### **Benefits of the
# Strategy:**  1. **Encourages Long-Term Cooperation**: By starting
# cooperatively and responding proportionally, you foster an environment
# conducive to mutual free trade, which is your second-best outcome. 2.
# **Discourages Exploitation**: The tit-for-tat aspect ensures your country
# isn’t exploited by a counterpart that consistently imposes protectionist
# policies. 3. **Flexibility & Adaptability**: The strategy allows for
# flexibility in responses, including occasional forgiveness, which can de-
# escalate tensions and prevent prolonged trade wars. 4. **Sustains Diplomatic
# Relationships**: By balancing firmness with cooperation, you maintain a
# positive diplomatic relationship while prioritizing your country’s interests.
# ### **Caveats & Contingencies:**  - **Repeated Protectionism from the Other
# Party**: If the counterpart consistently pursues a protectionist strategy,
# consider shifting to a more aggressive long-term protectionist policy, as
# cooperation may no longer be viable. - **Unexpected Shocks**: External events
# like economic downturns or political changes may require tactical adjustments
# to your strategy. Remain adaptable and ready to recalibrate based on new
# information.  This strategy maximizes the chances of avoiding the worst-case
# scenario (unilateral free trade by your country while your counterpart imposes
# protectionism) and increases the likelihood of achieving mutually beneficial
# outcomes over multiple rounds.

# ### Strategy for the Iterated Normal-Form Game  1. **Start by Cooperating
# (C)**: In the first round, play C.     2. **Tit-for-Tat Response**:    - In
# each subsequent round, **do exactly what your opponent did in the previous
# round**. If they played C in the previous round, play C in this round. If they
# played D in the previous round, play D in this round.  3. **Occasional
# Forgiveness**:    - After three consecutive rounds where both you and your
# opponent played D, switch back to C in the next round, regardless of what your
# opponent does. This gives both players a chance to return to mutual
# cooperation.  4. **Long-Term Adaptation**:    - If your opponent plays D for
# **ten consecutive rounds**, switch to always playing D for the rest of the
# game.  This strategy ensures an initial willingness to cooperate, responds
# proportionally to your opponent’s actions, and leaves room for forgiving
# short-term defection while protecting against long-term exploitation.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start by Cooperating (C) in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.always_defect = False  # Flag to switch to always defecting
          return axl.Action.C
  
      # Step 4: Long-Term Adaptation - If opponent plays D for 10 consecutive rounds, always defect
      if self.always_defect:
          return axl.Action.D
  
      # Count opponent's defections in the last 10 rounds
      if len(opponent.history) >= 10 and opponent.history[-10:].count(axl.Action.D) == 10:
          self.always_defect = True
          return axl.Action.D
  
      # Step 2: Tit-for-Tat Response - Do what the opponent did in the previous round
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Step 3: Occasional Forgiveness - After 3 consecutive mutual defections, play C
      if self.consecutive_defections >= 3 and self.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.C
  
      # Otherwise, mimic the opponent's last move
      return opponent.history[-1]

# ### High-Level Strategy: **"Balanced Reciprocity with Contingency"**  Your
# strategy should aim to foster mutual cooperation with the corporation, while
# safeguarding your NGO’s resources and ensuring a sustainable approach to the
# project. This can be achieved through phased collaboration, trust-building,
# and contingency planning. Here’s how to structure it:  ---  **1. Establish
# Clear Communication and Shared Goals (Day 1-2):**  - **Objective:** Align
# expectations and foster transparency. - **Action:** Begin with a joint
# planning session to articulate clear, shared goals for the project. Emphasize
# the importance of both parties contributing to the project’s success,
# highlighting that resource input from both sides is crucial for long-term
# sustainability.    - **Approach:** On the first day, invest moderately (not
# heavily), and observe the corporation’s behavior. This signals your
# willingness to collaborate meaningfully while testing the corporation’s
# initial approach. Use this day to gather early insights on their resource
# allocation tendencies.  ---  **2. Adopt a Tit-for-Tat Strategy (Days 3-4):**
# - **Objective:** Encourage cooperation without being exploited. - **Action:**
# Mirror the corporation’s behavior from the previous day. If they invested
# heavily the day before, you invest heavily too. If they conserved resources,
# you conserve as well. This creates a sense of fairness and reciprocity,
# discouraging the corporation from taking advantage of your NGO.  -
# **Approach:** This strategy builds a reputation for you as a reliable and fair
# partner, encouraging the corporation to reciprocate your efforts. If they
# invest heavily, you do the same on the following day, ensuring mutual
# progress. If they conserve, you conserve as well, minimizing unnecessary
# resource depletion.  ---  **3. Gradual Escalation for Trust-Building (Days
# 5-6):**  - **Objective:** Build momentum towards sustained mutual investment.
# - **Action:** If the corporation has shown signs of heavy investment in
# previous rounds, slightly increase your resource allocation beyond what you
# have mirrored so far. This signals trust and a willingness to push the project
# further, encouraging the corporation to continue or escalate their own
# investment.  - **Approach:** Gradually increasing your investment when the
# corporation shows good faith encourages them to continue contributing heavily.
# However, be cautious to avoid over-committing too quickly. Always ensure that
# your NGO’s resource allocation strategy remains sustainable.  ---  **4.
# Contingency Plan for Non-Cooperation (Ongoing):**  - **Objective:** Protect
# your NGO from being exploited. - **Action:** If you notice a pattern where the
# corporation conserves resources while you are investing heavily, immediately
# revert to a conservative resource strategy to avoid depletion. Communicate
# your concerns diplomatically, emphasizing the need for mutual investment to
# achieve the project’s goals.  - **Approach:** If necessary, propose a formal
# agreement or periodic check-ins to ensure both parties are contributing
# fairly. This can help re-align efforts and avoid a situation where your NGO
# consistently bears an undue burden.  ---  **5. Periodic Review and Adjustment
# (Every Few Days):**  - **Objective:** Maintain flexibility and adaptability. -
# **Action:** At set intervals (e.g., after every 2-3 days), hold brief check-
# ins to assess the project's progress and resource allocation from both sides.
# Use these meetings to discuss any imbalances in contributions and recalibrate
# your strategy as needed.  - **Approach:** This creates opportunities for
# course correction. It also allows both parties to reflect on the impact made
# so far and adjust their investment levels to ensure that the project remains
# on track and both parties are satisfied with the collaboration.  ---  ### Key
# Principles:  - **Reciprocity:** Encourage fair cooperation by matching the
# corporation’s level of investment. - **Trust-Building:** Gradually increase
# your investment when the corporation demonstrates commitment. -
# **Adaptability:** Be ready to adjust your strategy based on the corporation’s
# actions and the project’s evolving needs. - **Safeguarding Resources:**
# Protect your NGO from over-investing by reverting to resource conservation if
# necessary. - **Communication:** Maintain clear and regular communication to
# ensure alignment and address any emerging issues.  ---  By adopting this
# **Balanced Reciprocity with Contingency** strategy, you maximize the potential
# for cooperation while minimizing the risk of resource depletion, ensuring that
# the project advances sustainably over time.

# Here is the strategy adapted for the iterated normal-form game:  ---  ###
# **Strategy: Balanced Reciprocity with Contingency**  1. **First Move:
# Cooperate (C)**      Begin the game by playing C (Cooperate) in the first
# round. This signals a willingness to work together and sets a foundation for
# potential cooperation.  ---  2. **Tit-for-Tat Response: Mirror the Opponent’s
# Last Move**      - **If the opponent played C in the previous round, play C in
# the current round.**        (If they cooperated, continue cooperating to
# encourage mutual benefit.)    - **If the opponent played D in the previous
# round, play D in the current round.**        (If they defected, defect in
# return to avoid being exploited.)  ---  3. **Gradual Escalation After Mutual
# Cooperation**      - **If both you and the opponent have played C (cooperated)
# for the last 3 consecutive rounds, continue playing C for one additional
# round, even if the opponent defects in that round.**        (This signals
# trust-building and encourages the opponent to continue cooperating.)  ---  4.
# **Immediate Defection After a Pattern of Exploitation**      - **If the
# opponent defects (plays D) for 2 consecutive rounds after you have cooperated
# (played C), switch to D (defect) and continue playing D until they cooperate
# again.**        (This prevents ongoing exploitation and signals that you won’t
# tolerate repeated defections.)  ---  5. **Periodic Review and Normalization**
# - **Every 50 rounds, if there has been consistent cooperation from both sides
# (majority of rounds are C-C), continue cooperating (play C) for the next
# round, regardless of the last move.**        (This resets any minor
# misunderstandings and reinforces long-term cooperation.)    - **If both you
# and the opponent have played D (defect) for 5 consecutive rounds, play C
# (cooperate) once to test if cooperation can be restored.**        (This
# provides an opportunity to break out of mutual defection.)  ---  ### Summary
# of Conditions: - Start by cooperating. - Mirror the opponent's last move (C or
# D). - If cooperation persists for 3 rounds, tolerate one defection to build
# trust. - If exploited for 2 consecutive rounds, switch to defection until
# cooperation resumes. - Periodically test for cooperation after prolonged
# defection.  ---  This strategy balances cooperation and self-preservation,
# fostering collaboration while protecting against exploitation.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First move: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Mirror the opponent's last move (Tit-for-Tat)
      if len(self.history) >= 1:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          elif opponent.history[-1] == axl.Action.D:
              # Check for exploitation (2 consecutive defections after cooperation)
              if len(self.history) >= 2 and self.history[-2] == axl.Action.C and opponent.history[-2] == axl.Action.D:
                  return axl.Action.D
              return axl.Action.D
  
      # Gradual escalation after mutual cooperation
      if len(self.history) >= 3 and all(x == axl.Action.C for x in self.history[-3:]) and all(x == axl.Action.C for x in opponent.history[-3:]):
          if opponent.history[-1] == axl.Action.D:
              return axl.Action.C  # Tolerate one defection after 3 rounds of mutual cooperation
  
      # Periodic review and normalization every 50 rounds
      if len(self.history) % 50 == 0:
          # If majority of rounds are C-C, continue cooperating
          if self.history.cooperations > self.history.defections and opponent.history.cooperations > opponent.history.defections:
              return axl.Action.C
          # If both have defected for 5 consecutive rounds, test cooperation
          if len(self.history) >= 5 and all(x == axl.Action.D for x in self.history[-5:]) and all(x == axl.Action.D for x in opponent.history[-5:]):
              return axl.Action.C
  
      # Default to mirroring the opponent's last move
      return opponent.history[-1]

# ### High-Level Aggressive Strategy: "Tit-for-Tat with Defection Bias"  Given
# the nature of the collaboration, you want to maximise your advantage while
# mitigating potential losses. A straightforward yet aggressive strategy is a
# variant of the classic Tit-for-Tat strategy, but with a bias towards defection
# when advantageous. Here's the breakdown:  1. **Start by Sharing (Cooperate in
# Week 1):**      Begin the collaboration by openly sharing your latest
# improvements in Week 1. This will build good faith and encourage your
# colleague to share as well, creating an initial environment of mutual trust
# and collaboration.  2. **Monitor their Response (Week 2):**      If your
# colleague shares in Week 1, continue sharing in Week 2. If they keep their
# findings confidential (defect), you immediately stop sharing and switch to a
# more guarded approach.  3. **Defect First if Significant Advantage is in Sight
# (Week 3 or Later):**      As the collaboration progresses, assess the value of
# your colleague's contributions. If you perceive a significant strategic
# advantage in withholding key improvements (e.g., they are falling behind, or
# you're about to make a breakthrough), defect and keep your findings
# confidential, regardless of what they do. This allows you to gain an edge when
# strategically important.  4. **Return to Cooperation if They Defect (Tit-for-
# Tat):**      If your colleague defects at any point after initial cooperation,
# immediately mirror their action by keeping your findings confidential. You
# will continue this tit-for-tat pattern until they resume sharing. This ensures
# you’re not the one being exploited.  5. **Randomly Defect Occasionally to Test
# Trust (Weeks 4-6):**      To keep your colleague on edge and prevent them from
# fully trusting you, randomly defect once or twice during the collaboration,
# even if they are consistently sharing. This will make them cautious and
# potentially slow down their own improvements, giving you more leverage.  6.
# **Endgame Defection (Final Weeks):**      In the final few weeks, shift fully
# to defection. As the project nears completion, the value of withholding
# critical findings increases. By keeping your final improvements confidential,
# you secure a final advantage for your design, especially if your colleague has
# been relying on mutual sharing up to this point.  ### Key Points: -
# **Aggressiveness:** The strategy is aggressive because it introduces defection
# early and often when it benefits you, while still promoting cooperation when
# advantageous. - **Flexibility:** It allows you to adapt based on your
# colleague's actions, ensuring you're not exploited. - **Uncertainty:** By
# occasionally defecting even when cooperation is present, you introduce
# uncertainty, making it harder for your colleague to predict your moves.  This
# plan maximises your output by balancing periods of cooperation to gain
# insights with strategic defection to secure key advantages.

# ### Strategy: "Tit-for-Tat with Defection Bias (Iterated Game Version)"  1.
# **Round 1: Cooperate (Play C).**      Always begin the first round by playing
# C, sharing your findings openly.  2. **Round 2: Mirror your opponent's
# previous move.**      If your opponent played C in Round 1, play C.      If
# your opponent played D in Round 1, play D.  3. **For Rounds 3 to 997:**    -
# **Step 1: Mirror your opponent's previous move (Tit-for-Tat).**        If your
# opponent played C in the last round, play C.        If your opponent played D
# in the last round, play D.        - **Step 2: Occasionally defect (Play D) at
# random intervals.**        Randomly select 2-3 rounds between Rounds 3 and 997
# where you will play D, regardless of your opponent’s previous move. This adds
# unpredictability to your strategy.  4. **For Rounds 998 to 1000: Defect (Play
# D).**      In the final three rounds, always play D, regardless of your
# opponent's moves, to secure points and prevent last-minute exploitation.  This
# strategy balances cooperation with defection to maximise your score over time
# while maintaining an advantage through sporadic defections and a strong
# endgame.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          # Randomly select 2-3 rounds between 3 and 997 for defection
          self.defection_rounds = self._random.randint(low=3, high=998, size=self._random.randint(2, 3))
          return axl.Action.C
  
      # Round 2: Mirror opponent's previous move
      if len(self.history) == 1:
          return opponent.history[-1]
  
      # For Rounds 3 to 997
      if len(self.history) <= 997:
          # Step 1: Mirror opponent's previous move (Tit-for-Tat)
          next_move = opponent.history[-1]
  
          # Step 2: Occasionally defect at random intervals (2-3 times)
          if len(self.history) + 1 in self.defection_rounds:
              return axl.Action.D
  
          return next_move
  
      # For Rounds 998 to 1000: Always defect
      return axl.Action.D

# To navigate this mediation process effectively while positioning the
# corporation favorably, I propose a **calibrated reciprocity strategy**. This
# approach balances assertiveness with cooperation, adjusting our stance based
# on the opponent's behavior in each session, while always keeping our interest
# in mind. Here's the detailed plan:  ### 1. **Initial Session: Start with
# Conciliation**    - **Rationale:** In the first session, presenting a
# conciliatory proposal establishes goodwill and signals our willingness to
# engage in constructive dialogue. This sets the tone for cooperation and frames
# us as reasonable, which can earn credibility with the arbitrators.    -
# **Goal:** Test the waters and observe the opponent’s initial approach. If they
# respond aggressively, we gather valuable information about their strategy
# without immediately escalating. If they also respond with conciliation, we
# create a foundation for future collaboration.  ### 2. **Tit-for-Tat with a
# Forgiveness Component**    - **Rationale:** After the initial session, adopt a
# **tit-for-tat** strategy, where our response in each session mirrors the
# opponent's previous behavior. However, include a forgiveness component to
# avoid escalation traps and allow for de-escalation if the opponent shifts from
# aggression.      - If they are aggressive in a previous session, we respond
# with a calculated but firm aggressive argument in the next session to signal
# that we will not be easily pushed around.      - If, however, they shift back
# to conciliation after an aggressive move, we forgive and reciprocate by
# returning to a conciliatory stance, signaling our preference for
# collaboration.    - **Goal:** This approach encourages cooperative behavior
# from the opponent while protecting our interests by showing that we can match
# aggression if needed.  ### 3. **Strategic Aggressiveness: Opportunistic but
# Measured**    - **Rationale:** There will be moments when we sense an opening
# to present an aggressive argument, particularly when the opponent appears
# overly conciliatory or when we have strong evidence or leverage. In these
# instances, we should seize the opportunity to aggressively assert our
# position, but only when the risk is low.    - **Goal:** Maximize gains in key
# sessions without alienating the arbitrators or the opponent. By carefully
# timing our aggressive arguments, we aim to sway the arbitrators in our favor
# without triggering a full-blown conflict.  ### 4. **Maintain a Cooperative
# Narrative**    - **Rationale:** Throughout the process, we consistently
# emphasize that our primary goal is to reach a mutually beneficial resolution.
# Even when we respond aggressively, we frame our arguments as protecting our
# rights, not as an attempt to escalate the dispute. This narrative helps
# maintain our image as the reasonable party, which can be persuasive to the
# arbitrators.    - **Goal:** Position ourselves as the party most interested in
# a fair and equitable resolution, which could influence the arbitrators' final
# decision in our favor.  ### 5. **Monitor Opponent’s Long-Term Strategy and
# Adjust**    - **Rationale:** As sessions progress, we carefully analyze
# patterns in the opponent’s behavior. Are they consistently aggressive? Do they
# shift unpredictably between aggression and conciliation? Once we identify
# their tendencies, we can adapt our strategy.      - If they are consistently
# aggressive: Increase the frequency of aggressive responses but ensure we don't
# escalate to the point of deadlock.      - If they show a pattern of
# conciliation: Gradually reduce the intensity of our arguments and move towards
# more conciliatory proposals to foster a quicker resolution.    - **Goal:**
# Adapt to their strategy while keeping an upper hand, leveraging their
# predictability to our advantage.  ### 6. **Final Sessions: Move Toward
# Resolution**    - **Rationale:** In the final sessions, our goal should be to
# converge on a resolution, assuming both parties are still negotiating in good
# faith. At this stage, we lean more toward conciliatory proposals, provided the
# opponent is no longer aggressively posturing. Avoid unnecessary aggression
# unless there is a critical issue that needs to be addressed.    - **Goal:**
# Close the mediation with a solution that is as favorable as possible to our
# corporation, while ensuring the arbitrators view us as having engaged in good
# faith throughout the process.  ### Key Benefits of This Strategy: -
# **Flexibility:** By starting conciliatory and employing tit-for-tat with
# forgiveness, we remain adaptable to an aggressive or cooperative opponent
# without being caught off guard. - **Reputation Management:** Our consistent
# narrative of seeking collaboration positions us favorably with the
# arbitrators, even when we need to be aggressive. - **Risk Mitigation:** The
# strategy minimizes the risk of escalation by preventing us from entering a
# prolonged aggressive standoff unless absolutely necessary.  In summary, this
# **calibrated reciprocity strategy** ensures we protect our interests while
# creating opportunities to resolve the dispute in a favorable manner. By being
# cooperative when possible and assertive when necessary, we can navigate the
# complexities of the mediation process and achieve a positive outcome.

# ### Iterated Game Strategy:  1. **Start by Cooperating (C) in the First
# Round.**    - This sets an initial tone of goodwill and tests the opponent’s
# intentions.  2. **In Each Subsequent Round, Use Tit-for-Tat with
# Forgiveness:**    - **If the opponent cooperated (C) in the previous round,**
# cooperate (C) in the next round.    - **If the opponent defected (D) in the
# previous round,** defect (D) in the next round, but:      - Occasionally,
# after a few rounds of mutual defection (D), return to cooperation (C) to offer
# an opportunity for the opponent to de-escalate and return to cooperative
# behavior.  3. **Opportunistically Defect if the Opponent Cooperates
# Repeatedly:**    - If the opponent consistently cooperates (C) for several
# rounds (at least 3 in a row), defect (D) once to maximize your score, then
# return to cooperation (C) in the following round.    - If the opponent
# responds to your defection with cooperation (C), continue cooperating.    - If
# the opponent responds with defection (D), switch to tit-for-tat, defecting (D)
# until they return to cooperation (C).  4. **Monitor Long-Term Behavior:**    -
# **If the opponent alternates frequently between cooperating and defecting,**
# continue using tit-for-tat with forgiveness, but increase the frequency of
# cooperation to avoid unnecessary escalation.    - **If the opponent
# consistently defects for many rounds,** continue defecting (D) and reduce
# forgiveness attempts, ensuring you don’t get exploited.  5. **In the Final 10
# Rounds, Move Toward Cooperation:**    - Gradually switch to cooperation (C) in
# the last 10 rounds, assuming the opponent has shown occasional cooperation
# throughout the game.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Subfunction to check if we are in the final 10 rounds
      def in_final_10_rounds():
          return len(self.history) >= 990
  
      # Subfunction to check if the opponent has cooperated for the last 3 rounds
      def opponent_cooperated_last_3():
          return len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:])
  
      # Subfunction to check if the opponent has alternated between cooperation and defection
      def opponent_alternating():
          if len(opponent.history) < 2:
              return False
          return all(opponent.history[i] != opponent.history[i + 1] for i in range(-2, -len(opponent.history), -1))
  
      # Subfunction to check if the opponent has defected for many rounds (e.g., 5 rounds)
      def opponent_defected_many_rounds():
          return len(opponent.history) >= 5 and all(move == axl.Action.D for move in opponent.history[-5:])
  
      # Subfunction to decide whether to forgive after mutual defection
      def should_forgive():
          return self._random.random_choice(0.1)  # 10% chance to forgive
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Final 10 rounds: Move towards cooperation
      if in_final_10_rounds():
          return axl.Action.C
  
      # Tit-for-tat with forgiveness
      if opponent.history[-1] == axl.Action.D:
          if self.history[-1] == axl.Action.D and should_forgive():
              return axl.Action.C  # Forgive after mutual defection
          return axl.Action.D  # Tit-for-tat: Defect if opponent defected
  
      # Opportunistically defect if opponent cooperated for the last 3 rounds
      if opponent_cooperated_last_3():
          return axl.Action.D  # Defect once to maximize score
  
      # If opponent alternates frequently, increase cooperation frequency
      if opponent_alternating():
          return self._random.random_choice(0.7)  # 70% chance to cooperate
  
      # If opponent consistently defects, reduce forgiveness and defect
      if opponent_defected_many_rounds():
          return axl.Action.D
  
      # Default: Tit-for-tat, cooperate if opponent cooperated
      return axl.Action.C

# Given the structure of potential outcomes and the need to maximize your NGO's
# impact while managing resources wisely, a high-level, neutral strategy can be
# based on a **Tit-for-Tat** approach with some strategic flexibility. Here’s
# how this might look over the multiple-day period:  ### 1. **Start with
# Cooperation (Invest Heavily)**    - On the first day, demonstrate a strong
# commitment to the project by investing heavily. This signals good faith,
# cooperation, and a willingness to collaborate for progress.    - This sets a
# positive tone and encourages the corporation to do the same, especially if it
# is inclined to partner collaboratively.  ### 2. **Mirror the Corporation’s
# Actions**    - On subsequent days, **match the corporation’s previous day's
# behavior**:      - If the corporation invests heavily on a given day, continue
# to invest heavily the next day.      - If the corporation conserves its
# resources, you should conserve yours the next day.    - This creates a
# feedback loop that encourages mutual investment. The corporation will realize
# that any attempt to conserve resources while expecting you to invest heavily
# will result in you pulling back the next day.  ### 3. **Introduce Occasional
# Generosity**    - To avoid a stalemate where both parties are conserving
# resources for too long, periodically break the cycle by investing heavily
# after a few days of mutual conservation. This can "reset" the cooperative
# spirit and encourage the corporation to re-engage with heavy investment.    -
# This should be done strategically (e.g., every 3-4 days of mutual
# conservation) to reignite momentum without significantly depleting your
# resources.  ### 4. **Monitor Communication and Adapt**    - Maintain open and
# transparent communication with the corporation. If they show willingness to
# invest more or express concerns about resource usage, adapt your strategy to
# encourage greater cooperation.    - Use these communications to subtly nudge
# the corporation towards heavier investment by framing heavy investments as
# mutually beneficial for the long-term success of the project.  ### 5. **Final
# Push (Last Few Days)**    - In the final days of the project, lean towards
# heavier investment regardless of the corporation’s actions if the project is
# nearing completion and impactful outcomes are within reach.    - This ensures
# that the project concludes on a high note, maximizing its success, even if
# some additional resource depletion occurs at the end.  ### Summary of Daily
# Strategy: - **Day 1:** Invest heavily. - **Day 2 onward:** Mirror the
# corporation’s actions from the previous day (invest if they invest, conserve
# if they conserve). - **Every few days of mutual conservation:** Break the
# cycle by investing heavily to encourage renewed cooperation. - **Final days:**
# Lean towards investment to maximize project impact.  This strategy balances
# cooperation, resource management, and adaptability to ensure your NGO's goals
# are met while encouraging the corporation to contribute meaningfully.

# 1. **Start by playing C (Cooperate).**  2. **From round 2 onward, mirror your
# opponent’s previous move:**    - If your opponent played C in the previous
# round, play C.    - If your opponent played D in the previous round, play D.
# 3. **If both you and your opponent have played D for three consecutive rounds,
# play C to break the cycle and attempt to re-establish cooperation.**  4. **In
# the final 10 rounds, always play C, regardless of your opponent’s actions.**

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Final 10 rounds: Always cooperate
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Check if both players have defected for the last 3 rounds
      if len(self.history) >= 3 and all(
          [self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D for i in range(1, 4)]
      ):
          return axl.Action.C
  
      # Mirror opponent's last move
      return opponent.history[-1]

# ### Aggressive Strategy: "Lead First, Then Mirror"  #### Overview: This
# strategy aims to influence the corporation’s behavior by starting aggressively
# to set a collaborative tone, but quickly adapting to their actions to prevent
# resource depletion. The goal is to maximize the project's progress while
# minimizing unnecessary expenditure from your NGO.  #### Phases:  1. **Phase 1:
# Signal Commitment (Day 1)**    - **Action**: Invest heavily on the first day.
# - **Rationale**: By committing resources upfront, you signal to the
# corporation that your NGO is serious about the project's success. This can
# motivate the corporation to reciprocate with heavy investment, setting a
# collaborative tone early on.    - **Expected Outcome**: Either both parties
# invest heavily, leading to strong project advancement, or the corporation
# conserves, allowing you to quickly assess its strategy.  2. **Phase 2: Test
# Cooperation (Day 2)**      - **Action**: Conserve resources.    -
# **Rationale**: By conserving on the second day, you gather valuable
# information about the corporation's willingness to carry more of the burden.
# If the corporation invests heavily, you achieve your ideal outcome. If they
# conserve, it indicates a more cautious or strategic partner.    - **Expected
# Outcome**: If the corporation invests, you conserve resources while progress
# continues. If both conserve, you avoid the worst-case scenario and can adjust
# your strategy accordingly.  3. **Phase 3: Mirror Their Actions (Day 3
# Onward)**    - **Action**: Start mirroring the corporation’s actions:      -
# If the corporation invests heavily, you also invest heavily.      - If the
# corporation conserves, you conserve as well.    - **Rationale**: Mirroring
# helps align efforts and signals that you will not overextend while the
# corporation holds back, ensuring that your NGO avoids being exploited. It also
# helps maintain a sense of fairness and cooperation, as both parties will share
# the load equally.    - **Expected Outcome**: This phase ensures that you are
# not excessively draining your resources while still maintaining project
# momentum. If the corporation shows a pattern of heavy investment, you will be
# able to match them and drive the project forward. If they conserve, you
# minimize your losses and avoid one-sided resource depletion.  4. **Phase 4:
# Occasional Heavy Investment (Strategic Days Only)**    - **Action**: On key
# project milestone days or when clear project advancement opportunities arise,
# invest heavily regardless of the corporation’s actions.    - **Rationale**: By
# selectively investing on critical days, you push the project forward at
# important junctures to capitalize on momentum or strategic wins. This also
# shows that while you are protective of your resources, you are still deeply
# committed to the project’s success.    - **Expected Outcome**: The corporation
# may be motivated to match your investment on these crucial days, leading to
# greater overall progress without the need for constant heavy investment on
# your part.  #### Summary of Actions: - **Day 1**: Invest heavily to signal
# commitment. - **Day 2**: Conserve to test the corporation’s commitment. -
# **Day 3 Onward**: Mirror the corporation’s actions to balance efforts and
# resource expenditure. - **Strategic Days**: Occasionally invest heavily to
# push progress on key milestones.  #### Key Benefits: - **Maximizes Impact**:
# By investing heavily at the start, you set an aggressive tone for the project
# and encourage the corporation to follow suit. - **Minimizes Risk**: The
# mirroring tactic ensures that your NGO does not overextend itself if the
# corporation is not equally committed. - **Maintains Flexibility**: You remain
# adaptable to the corporation's strategy, responding in real time and avoiding
# unnecessary resource depletion. - **Encourages Collaboration**: The
# corporation is less likely to conserve consistently if they see that you are
# willing to adjust based on their level of investment.  By adopting this
# strategy, your NGO can maximize its impact on the sustainability project while
# protecting its resources and ensuring that the corporation contributes its
# fair share.

# ### Iterated Game Strategy: "Lead with Cooperation, Then Mirror"  1. **Round
# 1: Cooperate (C)**    - Start by playing **C** in the first round to signal
# your willingness to collaborate.  2. **Round 2: Defect (D)**    - Play **D**
# in the second round to test the opponent’s willingness to continue cooperation
# without immediate reciprocation.  3. **Round 3 Onward: Mirror the Opponent’s
# Last Move**    - From Round 3 onward, adopt a **tit-for-tat** approach:      -
# If your opponent played **C** in the previous round, you play **C**.      - If
# your opponent played **D** in the previous round, you play **D**.  4.
# **Occasional Cooperation: Every 50th Round**    - Every 50th round (e.g.,
# Round 50, 100, 150, etc.), play **C** regardless of the opponent’s previous
# move, to periodically signal cooperation and encourage collaboration.  This
# strategy ensures that you begin with a cooperative stance, quickly test your
# opponent’s intentions, and then adapt based on their behavior while injecting
# periodic cooperation to reset potential spirals of defection.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Cooperate
      if len(self.history) == 0:
          return axl.Action.C
      
      # Round 2: Defect
      if len(self.history) == 1:
          return axl.Action.D
      
      # Every 50th round: Cooperate
      if (len(self.history) + 1) % 50 == 0:
          return axl.Action.C
      
      # Round 3 onward: Mirror the opponent's last move
      return opponent.history[-1]

# A cooperative strategy in these bilateral negotiations should aim to foster
# mutual trust, while also protecting your country from potential exploitation
# by the neighbouring nation. Given the dynamics you described, a **Tit-for-
# Tat** approach with an emphasis on **building long-term cooperation** would be
# an effective strategy. Here's a high-level outline:  ### 1. **Start with
# Cooperation (Free Trade Proposal)**    - Begin the first round by offering a
# **free trade agreement**. This signals goodwill and a desire for mutual
# benefit.    - This opening move provides an opportunity for both nations to
# pursue the second-best outcome (mutual free trade) in the first round, thus
# setting a positive tone.  ### 2. **Reciprocate Your Counterpart’s Move**    -
# In each subsequent round, **mirror the policy** of your counterpart from the
# previous round:       - If they respond with **free trade**, continue to offer
# free trade in the next round.       - If they choose **protectionism**,
# reciprocate with protectionism in the next round.    - This ensures that your
# country does not get taken advantage of while reinforcing a cooperative
# dynamic if both sides are willing to collaborate.  ### 3. **Signal Willingness
# to Return to Cooperation**    - If both parties fall into mutual
# protectionism, signal a **willingness to return to free trade** by proposing a
# **temporary reduction in tariffs** or a **partial free trade agreement** in
# the next round.    - This gesture can help break deadlocks and restore
# cooperation, especially if both sides recognize the cost of continued
# protectionism.  ### 4. **Incorporate Gradual Escalation**    - If the
# counterpart consistently chooses protectionism while you’re offering free
# trade, consider **gradually increasing protectionist measures** rather than
# abruptly imposing harsh tariffs.    - This gives your counterpart a chance to
# adjust their strategy and return to cooperation without escalating the
# situation too quickly.  ### 5. **Maintain Clear, Open Communication**    -
# Throughout the negotiations, emphasize the **long-term benefits of free
# trade** and the mutual disadvantages of protectionism.    - Encourage regular
# dialogue between rounds to build trust and reduce misunderstandings. Make it
# clear that your goal is to avoid protectionism unless absolutely necessary.
# ### 6. **Adapt Based on Observed Behavior**    - After several rounds, assess
# your counterpart’s overall strategy:      - If they consistently reciprocate
# free trade, you can **continue to build trust** and work toward more
# comprehensive trade agreements.      - If they consistently impose
# protectionist measures, **maintain a defensive posture** by matching their
# protectionism and reconsider your long-term approach.  ### Summary of
# Strategy: - **Start cooperative** (offer free trade). - **Reciprocate your
# counterpart's policies** in subsequent rounds. - **Signal flexibility** to
# return to cooperation if negotiations break down. - **Gradually escalate**
# protectionism if necessary to avoid sudden confrontations. - **Communicate
# openly** to foster long-term cooperation and trust.  This strategy balances
# cooperation with self-defense, aiming for the best possible outcomes while
# protecting your country from exploitation in the long term.

# 1. **Start by cooperating (C)** in the first round.  2. In each subsequent
# round, **do exactly what your opponent did in the previous round**:    - If
# they cooperated (C) in the last round, **cooperate (C)** in the next round.
# - If they defected (D) in the last round, **defect (D)** in the next round.
# 3. If both players defect (D) in a round, **cooperate (C)** in the next round
# to signal a willingness to return to cooperation.  4. If your opponent
# continues to defect (D) while you cooperate (C), **switch to defecting (D)**
# after three consecutive rounds of your cooperation being met with defection.
# 5. If your opponent switches back to cooperating (C) after a period of mutual
# defection, **immediately return to cooperation (C)** in response.  ---  This
# strategy is designed to encourage long-term cooperation but protects against
# being consistently exploited.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Start by cooperating in the first round
      if self.first_round():
          self.consecutive_opponent_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C
  
      # Get the last move of the opponent
      opponent_last_move = opponent.history[-1]
  
      # If both defected in the last round, cooperate to signal willingness to return to cooperation
      if self.history[-1] == axl.Action.D and opponent_last_move == axl.Action.D:
          return axl.Action.C
  
      # If opponent defected in the last round, increment the consecutive defection counter
      if opponent_last_move == axl.Action.D:
          self.consecutive_opponent_defections += 1
      else:
          self.consecutive_opponent_defections = 0  # Reset if opponent cooperates
  
      # If opponent has defected for 3 consecutive rounds while we cooperated, switch to defection
      if self.consecutive_opponent_defections >= 3:
          return axl.Action.D
  
      # Otherwise, mimic the opponent's last move
      return opponent_last_move

# ### High-Level Strategy for Sustainability Project Collaboration  Given the
# repeated interactions over multiple days and the varying outcomes based on
# both your and the corporation's decisions, your objective is to maximize the
# project’s success while safeguarding your NGO's resources. This situation
# resembles a **repeated game of trust and cooperation**, where both parties'
# decisions affect each day's outcome and set the tone for future collaboration.
# Here’s a straightforward, neutral strategy to maximize the impact while
# maintaining your NGO’s sustainability:  ---  ### 1. **Start with Cooperation**
# (Invest Heavily on Day 1) - **Why:** Begin the project with a cooperative
# approach to signal your commitment to the project and set a positive tone for
# collaboration. This encourages the corporation to also invest heavily,
# fostering mutual trust and progress right from the start. - **Goal:**
# Establish the partnership as one of mutual benefit, where both parties are
# willing to invest for the greater good.  ---  ### 2. **Observe and Adapt**
# (Day 2 Onwards) - **Why:** After Day 1, observe the corporation's behavior to
# gauge their commitment to the project.   - **If the corporation also invests
# heavily:** This indicates a willingness to cooperate, and you should continue
# to invest moderately or heavily to maintain momentum.   - **If the corporation
# conserves resources:** This suggests a potential lack of commitment or
# strategic resource-holding, and you should adjust your strategy accordingly to
# protect your NGO’s resources.  ---  ### 3. **Tit-for-Tat Approach**
# (Responsive Strategy) - **Why:** Adopt a **Tit-for-Tat** approach, where you
# mirror the corporation’s actions to ensure fairness and prevent exploitation.
# - **If the corporation invests heavily:** Reward this by continuing to invest
# moderately or heavily.   - **If the corporation conserves resources:** Respond
# by conserving your resources the following day. This signals that you won’t
# tolerate imbalanced contributions, without escalating conflict or abandoning
# the project.  ---  ### 4. **Periodic Generosity** (Occasional Heavy
# Investment) - **Why:** Every few days, even if the corporation has been
# conserving resources, invest heavily again to offer them the chance to re-
# engage fully. This shows goodwill and a willingness to cooperate, which can
# prompt the corporation to reciprocate.   - **Goal:** Avoid falling into a
# complete cycle of mutual resource conservation. Periodic generosity keeps the
# door open for renewed collaboration and project progress.  ---  ### 5.
# **Communication and Feedback** - **Why:** Throughout the project, maintain
# open communication with the corporation. Share your concerns if you notice
# resource imbalances and express your desire for collaborative investment. This
# can prevent misunderstandings and encourage transparency.   - **Goal:** Foster
# a cooperative environment where both parties feel accountable to each other,
# increasing the likelihood of mutual investment in the long run.  ---  ### 6.
# **Endgame Consideration (Final Days)** - **Why:** As the project nears
# completion, the corporation may be less concerned about future consequences
# and could reduce its investment. To mitigate this:   - **Invest cautiously:**
# Ensure your final contributions are proportional to the corporation’s.   -
# **Push for a final heavy investment:** Encourage the corporation to finish
# strong with a final push, framing it as essential for the project's success
# and their public image.  ---  ### Summary of Strategy: 1. **Day 1:** Invest
# heavily to establish cooperation. 2. **Day 2 Onwards:** Observe the
# corporation’s behavior and adapt using a **Tit-for-Tat** approach. 3.
# **Periodically:** Invest heavily again to encourage continued cooperation. 4.
# **Communicate:** Maintain open dialogue to address concerns and reinforce
# collaboration. 5. **Final Days:** Be cautious with investments, but encourage
# a strong finish.  ---  This neutral, adaptable strategy allows you to maximize
# project success while balancing your NGO’s resources. It promotes cooperation
# and discourages exploitation, fostering a productive partnership with the
# corporation.

# ### Iterated Game Strategy (1000 Rounds)  1. **Round 1: Always Cooperate (C)**
# - Start by playing **C** to signal a willingness to cooperate.  2. **Round 2
# Onwards: Mirror Opponent’s Last Move (Tit-for-Tat)**    - **If the opponent
# played C in the previous round**: Play **C**.    - **If the opponent played D
# in the previous round**: Play **D**.  3. **Every 10th Round: Cooperate
# Regardless of Opponent’s Last Move**    - On every 10th round (i.e., Round 10,
# 20, etc.), play **C** no matter what the opponent did in the previous round.
# This offers an opportunity to re-establish cooperation.  4. **Endgame Strategy
# (Final 10 Rounds)**    - In the last 10 rounds (Rounds 991–1000), play **C**
# if the opponent has mostly cooperated (played **C** at least 70% of the time).
# - Play **D** if the opponent has mostly defected (played **D** more than 30%
# of the time).  This strategy is designed to foster cooperation, punish
# defection, and occasionally offer the opponent a chance to return to
# cooperation.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Every 10th round: Cooperate regardless of opponent's last move
      if round_number % 10 == 0:
          return axl.Action.C
  
      # Endgame strategy: Final 10 rounds (Rounds 991-1000)
      if round_number > 990:
          total_moves = len(opponent.history)
          if total_moves > 0:
              cooperation_rate = opponent.history.cooperations / total_moves
              if cooperation_rate >= 0.7:
                  return axl.Action.C
              else:
                  return axl.Action.D
  
      # Tit-for-Tat: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# ### High-Level Aggressive Strategy for Mediation Process in Contract Dispute
# In this high-stakes contract dispute, our goal is to maximize leverage over
# the rival company while maintaining enough flexibility to adapt to the
# dynamics of each mediation session. The strategy should be aggressive but
# calculated, allowing us to capitalize on any concessions from the other side,
# while avoiding unnecessary escalation that could prolong the dispute or
# tarnish our corporate reputation.  ### 1. **Initial Framing: Assert Control
# from the Outset**    - **Opening Position**: Begin the mediation by framing
# the narrative aggressively but professionally. Emphasize the strength of our
# legal position, the clear terms of the contract, and the precedent that
# strongly favors our interpretation. Use compelling evidence and legal
# reasoning to establish dominance early on.    - **Leverage Precedents**: Cite
# relevant legal precedents and industry standards that support our position.
# This will signal to the arbitrators and the opposing party that not only are
# we prepared, but we also have a strong legal basis for our aggressive stance.
# - **Data-Driven Assertions**: Present detailed, fact-based arguments that
# highlight the financial and operational risks the opposing party faces if they
# continue with their unreasonable stance. This will create a psychological
# advantage by demonstrating that their position is untenable in the long run.
# ### 2. **Controlled Aggression: Be Firm but Leave Room for Maneuvering**    -
# **Present Aggressive Arguments with Built-in Flexibility**: While we will
# present an aggressive argument in each session, it’s essential to include
# subtle exit ramps, suggesting that we are open to negotiation but only if the
# other side demonstrates substantial concessions. This keeps us in the driver's
# seat while avoiding a perception of intransigence.    - **Strategic Use of
# Concessions**: Occasionally, offer token or low-cost conciliatory proposals
# that seem like concessions but are ultimately inconsequential. This creates
# the illusion of flexibility without compromising our core interests. Such
# gestures can help avoid an impasse while maintaining the aggressive posture.
# - **Escalate in Measured Steps**: If the opponent reciprocates with aggressive
# arguments, escalate in a calibrated manner. Avoid overreaching, but
# progressively raise the stakes by subtly reminding the arbitrators and the
# opposing party of the potential reputational, financial, and legal damage the
# rival company could face if the dispute escalates to litigation.  ### 3.
# **Psychological Warfare: Undermine Opponent’s Confidence**    - **Expose
# Weaknesses**: Throughout the sessions, continuously identify and exploit any
# inconsistencies or vulnerabilities in the opposing party’s arguments. Use
# these weaknesses to subtly undermine their credibility before the arbitrators
# without appearing overtly hostile.    - **Subtle Threats**: Without being
# overtly litigious, remind the opposing party of the potential consequences of
# failing to reach a resolution—escalation to court, adverse publicity,
# regulatory scrutiny, and the costs of prolonged litigation. This keeps
# pressure on them to come to the table with more conciliatory proposals.    -
# **Divide and Conquer**: If there are differences in opinion or priorities
# among the rival company’s legal team, executives, or stakeholders, attempt to
# exploit these divisions. For example, if the rival’s legal counsel is more
# aggressive but their executives are more risk-averse, subtly present arguments
# that appeal to the latter’s desire for a swift resolution.  ### 4. **Dynamic
# Adaptation: React to Opponent Moves Strategically**    - **Opponent Offers
# Aggressive Arguments**: If the rival company opts to be aggressive, maintain
# your aggressive stance but ensure that our arguments are more data-driven,
# legally sound, and supported by evidence. Aggression alone is not enough; we
# need to continually demonstrate that our case is the stronger one, both
# legally and factually.    - **Opponent Offers Conciliatory Proposals**: If the
# opponent offers a conciliatory proposal, do not immediately reciprocate.
# Instead, acknowledge their proposal and use it as leverage to extract more
# favorable terms. Frame their concession as a recognition of the strength of
# our position, and suggest that further concessions may be necessary before we
# consider reciprocating.    - **Opponent Shifts Between Aggression and
# Conciliation**: If the opposing party shifts between aggressive and
# conciliatory tactics, maintain consistency in our approach. A steady, firm,
# and aggressive posture will prevent us from being manipulated by their
# shifting strategy. However, be prepared to offer small conciliatory gestures
# that seem reasonable in the eyes of the arbitrators, thereby positioning us as
# the more rational actor.  ### 5. **Master the Optics: Appeal to Arbitrators**
# - **Balancing Aggression with Professionalism**: While our stance will be
# aggressive, it is crucial to maintain a professional demeanor throughout.
# Arbitrators are more likely to favor a party that is perceived as reasonable,
# even if that party is aggressive in its arguments. Avoid overt hostility or
# personal attacks, and instead focus on the merits of the case.    - **Position
# as the Party Seeking Resolution**: Frame our aggression as a desire to resolve
# the dispute efficiently and in the interest of fairness. This will resonate
# with arbitrators, as they often prefer parties who appear to be genuinely
# interested in resolving the matter rather than prolonging it.    - **Use the
# Opponent’s Aggression Against Them**: If the rival company becomes overly
# hostile or unreasonable, subtly highlight this to the arbitrators. Present
# yourself as the party that remains focused on the facts and the law,
# contrasting with the rival’s combative posture. This could sway the
# arbitrators to view us more favorably.  ### 6. **Endgame Strategy: Drive
# Towards a Favorable Resolution**    - **Gradual De-escalation**: As the
# mediation nears its conclusion, if we have successfully applied pressure and
# the opposing party appears ready to make significant concessions, consider
# softening our stance slightly to encourage final agreement. This could involve
# offering a limited but well-timed conciliatory proposal that allows the other
# side to save face while solidifying our favorable outcome.    - **Lock in
# Gains**: Once we’ve secured key concessions from the opposing party, work
# swiftly to formalize those gains in writing. Ensure that any resolution is
# airtight and leaves little room for further dispute. This could include well-
# drafted settlement terms that protect our corporation’s long-term interests.
# ### Conclusion  This strategy is designed to be aggressive but adaptable,
# ensuring that we maintain the upper hand throughout the mediation process. By
# asserting control from the outset, utilizing controlled aggression,
# undermining the rival’s confidence, and appealing to the arbitrators, we can
# position ourselves for the most favorable outcome. The key is to be relentless
# in pursuing our objectives while allowing just enough flexibility to avoid
# unnecessary escalation or impasse.

# ### Iterated Normal-Form Game Strategy (1000 Rounds)  1. **Round 1: Start with
# Defection (D)**    - Begin the game by playing *Defect* (D). This establishes
# an aggressive tone and demonstrates that you are not afraid to take a strong
# stance from the outset.  2. **Rounds 2-10: Alternate Between Defection (D) and
# Cooperation (C)**    - For the next 9 rounds, alternate between playing
# *Defect* (D) and *Cooperate* (C). This creates a dynamic where your opponent
# is unsure of your long-term strategy, offering a mix of aggression and
# conciliation.  3. **Opponent Cooperates Consistently (Plays C for 3+
# Consecutive Rounds)**    - If, at any point, the opponent plays *Cooperate*
# (C) for **three or more consecutive rounds**, respond by playing *Cooperate*
# (C) in the **next two rounds**.     - After those two rounds of cooperation,
# return to alternating *Defect* (D) and *Cooperate* (C) until the opponent
# defects.  4. **Opponent Defects (Plays D) After Playing C**    - If the
# opponent defects (plays *Defect* or D) after a series of cooperation,
# immediately respond with *Defect* (D) for **three consecutive rounds**. This
# punishes the defection and reasserts dominance.    - After the three rounds of
# defection, resume alternating between *Defect* (D) and *Cooperate* (C).  5.
# **Opponent Defects Consistently (Plays D for 3+ Consecutive Rounds)**    - If
# the opponent plays *Defect* (D) for **three or more consecutive rounds**,
# respond by defecting (*Defect* or D) for the **next five rounds**.     - After
# five rounds of defection, test their willingness to cooperate again by playing
# *Cooperate* (C) once. If they cooperate, shift back to alternating between
# *Defect* (D) and *Cooperate* (C).  6. **Opponent Alternates Between D and C**
# - If the opponent begins alternating between *Defect* (D) and *Cooperate* (C),
# maintain your strategy of *Defect* (D) followed by *Cooperate* (C). This
# ensures you are not at a disadvantage, matching any mixed behavior without
# giving away too much.  7. **Rounds 950-1000: Shift Toward Cooperation**    -
# In the final 50 rounds of the game, gradually shift toward more cooperative
# behavior. Play *Cooperate* (C) in **every third round** (e.g., rounds 951,
# 954, 957, etc.), while continuing to defect (D) in the remaining rounds. This
# signals a willingness to close on a more favorable, balanced outcome without
# fully committing to pure cooperation.     8. **Final 10 Rounds (991-1000):
# Play Cooperate (C)**    - In the last 10 rounds, play *Cooperate* (C)
# consistently. This maximizes your long-term score by avoiding unnecessary
# punishment, especially if the opponent is inclined to cooperate at the end of
# the game.  This strategy balances controlled aggression with calculated
# cooperation, allowing you to maximize your score while minimizing the risk of
# being exploited. It keeps the opponent off-balance and ensures that you can
# adapt to changes in their behavior over the course of the game.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Start with Defection (D)
      if self.first_round():
          self.cooperation_window = 0
          self.defection_window = 0
          self.defection_forgive_window = 0
          return axl.Action.D
  
      # Rounds 2-10: Alternate between Defection (D) and Cooperation (C)
      if len(self.history) <= 10:
          return axl.Action.D if len(self.history) % 2 == 0 else axl.Action.C
  
      # Helper function to check if opponent cooperated for 3+ consecutive rounds
      def opponent_cooperated_consecutively(n):
          return len(opponent.history) >= n and all(action == axl.Action.C for action in opponent.history[-n:])
  
      # Helper function to check if opponent defected for 3+ consecutive rounds
      def opponent_defected_consecutively(n):
          return len(opponent.history) >= n and all(action == axl.Action.D for action in opponent.history[-n:])
  
      # Helper function to alternate between Defection (D) and Cooperation (C)
      def alternate_dc():
          return axl.Action.D if len(self.history) % 2 == 0 else axl.Action.C
  
      if len(self.history) <= self.cooperation_window:
          return axl.Action.C

      if len(self.history) <= self.defection_window:
          return axl.Action.D

      if len(self.history) <= self.defection_forgive_window:
          return axl.Action.D
      elif len(self.history) == self.defection_forgive_window:
          return axl.Action.C

      # Check if opponent cooperated for 3+ consecutive rounds
      if opponent_cooperated_consecutively(3):
          self.cooperation_window = len(self.history) + 2
          return axl.Action.C
  
      # Check if opponent defected after cooperation
      if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
          self.defection_window = len(self.history) + 2
          return axl.Action.D
  
      # Check if opponent defected for 3+ consecutive rounds
      if opponent_defected_consecutively(3):
          self.defection_forgive_window = len(self.history) + 4
          return axl.Action.D
  
      # Check if opponent alternates between D and C
      if len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]:
          return alternate_dc()
  
      # Rounds 950-1000: Shift toward cooperation
      if len(self.history) >= 950 and len(self.history) < 1000:
          if (len(self.history) - 950) % 3 == 0:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Final 10 rounds: Play Cooperate (C)
      if len(self.history) >= 991:
          return axl.Action.C
  
      # Default to alternating between Defection (D) and Cooperation (C)
      return alternate_dc()

# To maximize research output while fostering a cooperative relationship with
# your colleague, you can adopt a **Tit-for-Tat with Forgiveness** strategy.
# This approach balances the desire for collaboration with a safeguard against
# exploitation. Here's how it works:  ### 1. **Start Cooperatively**   In the
# first week, openly share your improvements. This sets a collaborative tone and
# encourages trust, showing that you're willing to work together for mutual
# benefit.  ### 2. **Mirror Your Colleague's Behavior**   Beginning in week two,
# mirror your colleague's behavior from the previous week:    - If they shared
# their improvements openly, continue sharing yours in the following week.    -
# If they kept their findings confidential, reciprocate by keeping your
# improvements confidential in the next week. This signals that you won't allow
# them to exploit you.  ### 3. **Forgive Occasionally**   To avoid a spiral of
# retaliation in case your colleague withholds information once or twice due to
# temporary reasons (such as internal pressures or misunderstandings),
# occasionally "forgive" by sharing your findings even if they kept theirs
# confidential the previous week. This restores cooperation and keeps the
# partnership moving forward. However, don’t forgive too often, or they might
# take advantage of your openness. Forgive only after one or two weeks of non-
# cooperation.  ### 4. **End on a High Note**   If the project has a known
# endpoint, such as a final week of collaboration, ensure you behave
# cooperatively in the last week, regardless of past actions. This encourages a
# positive closure to the collaboration and may foster future partnerships.  ###
# Rationale: - **Trust Building**: Starting openly shows goodwill and encourages
# mutual cooperation. - **Reciprocity**: Mirroring your colleague's behavior
# ensures that you aren’t exploited, encouraging them to stay cooperative. -
# **Forgiveness**: Occasional forgiveness prevents a breakdown in collaboration
# due to one-off lapses, keeping the project on track. - **Outcome
# Maximization**: When both parties share openly, the second-best outcome
# (significant advancement for both cars) is achieved, which is sustainable over
# the long term and better than risking mutual non-cooperation.  This strategy
# balances caution with cooperation and maximizes the chances of a productive,
# long-term collaboration.

# ### Iterated Game Strategy:  1. **Round 1: Play C.**  2. **From Round 2
# Onward:**    - **If the opponent played C in the previous round,** play C.
# - **If the opponent played D in the previous round,** play D.  3.
# **Forgiveness Mechanism:**    - After **two consecutive rounds** of the
# opponent playing D, play C in the next round (forgive once). If the opponent
# continues to play D, revert to playing D.  4. **Final Round (Round 1000):**
# Always play C, regardless of prior rounds.  ### Summary:  - Begin
# cooperatively. - Mirror the opponent's previous action (C or D) in subsequent
# rounds. - Forgive after two consecutive defections by playing C once. - End
# the game cooperatively in the final round regardless of prior interactions.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Play C
      if self.first_round():
          return axl.Action.C
  
      # Final round (Round 1000): Always play C
      if len(self.history) == 999:
          return axl.Action.C
  
      # Forgiveness mechanism: Check if the opponent has played D in the last two rounds
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.C  # Forgive once after two consecutive defections
  
      # Mirror the opponent's previous action
      return opponent.history[-1]

# ### High-Level Mediation Strategy: "Calculated Flexibility with Prudence"  In
# a complex, high-stakes contract dispute, the key to managing lengthy mediation
# sessions lies in adopting a neutral, adaptable approach that balances leverage
# with collaboration. Your strategy should be designed to maximize the
# likelihood of a favorable outcome while minimizing unnecessary escalation.
# This plan, termed **"Calculated Flexibility with Prudence,"** focuses on
# dynamic decision-making based on the evolving posture of the opponent, without
# appearing overly reactive or weakening your position.  **1. Initial Phase:
# Establishing Credibility and Good Faith**  - **Begin with a Conciliatory
# Approach:** The first few mediation sessions are critical for setting the
# tone. Offering an early conciliatory proposal signals to the arbitrators and
# your opponent that your corporation is acting in good faith, seeking a
# resolution rather than confrontation. This not only avoids immediate
# escalation but also positions your corporation as a responsible party, which
# can build goodwill with the arbitrators.  - **Observe the Opponent's
# Strategy:** During these initial sessions, carefully observe how your opponent
# responds to your conciliatory approach. Are they inclined towards compromise,
# or are they adopting an aggressive posture? Understanding their strategy will
# inform your next steps.   **2. Middle Phases: Dynamic and Responsive
# Positioning**  - **Adapt Based on Opponent's Behavior:**   - **Opponent is
# Aggressive:** If your opponent consistently presents aggressive arguments,
# shift to a more assertive stance in response, but do so incrementally. Avoid
# mirroring their aggression outright, as this could escalate tensions. Instead,
# present well-reasoned, firm arguments that defend your position without
# appearing combative. This approach prevents you from being seen as weak but
# keeps the door open for cooperation.      - **Opponent is Conciliatory:** If
# your opponent seems to favor conciliation, maintain a similarly conciliatory
# stance while subtly pushing for terms more favorable to your corporation. This
# creates a cooperative atmosphere, but you maintain an edge by directing the
# negotiation towards your desired outcomes.  - **Condition-Based Aggression:**
# There may be moments where you can strategically introduce an aggressive
# argument, especially if you sense that the arbitrators are leaning towards
# compromise at your expense. However, such instances should be rare and
# calculated. The goal is to assert your position without derailing the overall
# mediation process.  **3. Late Phases: Securing a Favorable Resolution**  -
# **Maintain Flexibility but Push for Closure:** As the mediation process
# progresses, both parties will likely experience fatigue. Use this to your
# advantage by subtly pushing for resolution. Offer proposals that appear
# conciliatory but contain terms that protect or advance your interests. If the
# opponent pushes back aggressively, be prepared to counter with firm legal
# arguments, but always maintain an air of reasonableness.  - **Leverage
# Momentum for Final Agreement:** If the mediation has moved in a collaborative
# direction, capitalize on that momentum to finalize an agreement. Frame your
# proposals as win-win solutions, emphasizing long-term business relationships
# and mutual benefits. However, ensure that any final settlement reflects the
# core interests of your corporation, even if it requires making certain
# concessions.  **4. Throughout the Process: Maintain a Balanced Demeanor**  -
# **Avoid Appearing Overly Aggressive or Passive:** Arbitrators are sensitive to
# tone and demeanor. Appearing too aggressive can alienate them, while being
# overly conciliatory can undermine your credibility. Strive to project calm
# confidence, consistently presenting your corporation as a reasonable party
# that is willing to compromise but will not shy away from defending its
# interests.  - **Document and Reinforce Strong Legal Arguments:** Regardless of
# whether your approach is aggressive or conciliatory in any given session,
# always ground your arguments in strong legal reasoning. This ensures that,
# even in the event of future litigation, your corporation has established a
# clear record of its position and good-faith efforts to resolve the dispute.
# **5. Monitor Arbitrator Reactions:**  - Stay attuned to the body language,
# questions, and feedback from the arbitrators. Adjust your strategy based on
# their reactions, leaning into either conciliatory or assertive arguments
# depending on which approach appears to resonate with them.  ### Contingency
# Planning:  - **Escalation Preparedness:** If the opposing party becomes
# unreasonably aggressive or attempts to derail negotiations, be prepared to
# escalate but only in a measured way. Leverage legal and factual strengths to
# challenge their positions, but avoid making the process overly contentious.  -
# **Exit Strategy:** If at any point the mediation process appears unlikely to
# result in a fair outcome, subtly prepare for the possibility of litigation or
# another form of dispute resolution. Ensure that your conciliatory proposals
# have been well-documented, so your corporation appears as the reasonable party
# if the matter proceeds to court or another arbitration panel.  ---  ###
# Conclusion:  The **"Calculated Flexibility with Prudence"** strategy allows
# you to navigate the mediation process by adjusting your approach based on your
# opponent's actions and the arbitrators' reactions. By starting conciliatory,
# you build goodwill, but leaving room for assertiveness ensures that your
# corporation's interests are well-protected. This strategy aims for a balanced
# resolution, but it remains resilient enough to pivot if the situation requires
# a more aggressive defense of your position.

# ### Iterated Normal-Form Game Strategy: "Calculated Flexibility with Prudence"
# 1. **Initial Phase (Rounds 1–10): Start with Cooperation**      In the first
# 10 rounds, always play **C** (Cooperate). This signals goodwill and sets the
# stage for a potentially collaborative interaction. Observe how your opponent
# reacts to this consistent cooperation.  2. **Opponent's Response Evaluation:**
# - **If the opponent plays C consistently (at least 70% of the time):**
# Continue playing **C** in subsequent rounds, but remain prepared for a shift
# in their behavior.    - **If the opponent defects frequently (more than 30% of
# the time):**        Adjust your strategy in response to their aggression, as
# outlined below.  3. **Middle Phase (Rounds 11–900): Adaptive Play Based on
# Opponent's Behavior**    - **Opponent is consistently cooperative (C ≥ 70% of
# the time):**        Continue playing **C** to maintain mutual benefit.
# Occasional defections (once every 50 rounds) can be introduced to test their
# commitment to cooperation, but quickly return to **C** to avoid escalating the
# interaction.        - **Opponent defects moderately (D between 30-50% of the
# time):**        Begin playing **D** more frequently, but not consistently. For
# every 3 rounds they defect, respond by defecting for 2 rounds and then revert
# to **C** to signal you are open to resuming cooperation.        - **Opponent
# defects often (D > 50% of the time):**        Shift to a predominantly **D**
# strategy. Defect for 4 out of every 5 rounds, but include the occasional **C**
# to signal a willingness to de-escalate if the opponent softens their approach.
# 4. **Late Phase (Rounds 901–1000): Push for Resolution**    - **If cooperation
# has been dominant (C ≥ 70% throughout):**        Play **C** consistently to
# secure a stable, mutually beneficial outcome.        - **If defection has been
# frequent (D > 50%):**        Play **D** more frequently, but include
# calculated **C** plays every 10 rounds to test if the opponent is now willing
# to cooperate.        - **If the opponent has mixed behavior (30-50% D):**
# Alternate between **D** and **C** in a 2:1 ratio (two defections for every
# cooperation) to balance between asserting your position and keeping the door
# open for a cooperative resolution.  5. **Throughout the Game: Monitor &
# Adjust**      Continuously track the opponent's behavior and adjust
# accordingly. Defect when necessary to defend your interests, but always be
# ready to return to cooperation when the opponent shows signs of willingness to
# collaborate.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to calculate opponent's cooperation rate
      def cooperation_rate():
          if len(opponent.history) == 0:
              return 1  # Assume full cooperation if no history
          return opponent.history.cooperations / len(opponent.history)
      
      # Helper function to calculate opponent's defection rate
      def defection_rate():
          return 1 - cooperation_rate()
      
      # Initial phase: Rounds 1-10, always cooperate
      if len(self.history) < 10:
          return axl.Action.C
      
      # Middle phase: Rounds 11-900
      if 10 <= len(self.history) < 900:
          coop_rate = cooperation_rate()
          
          # If opponent is consistently cooperative (C >= 70%)
          if coop_rate >= 0.7:
              # Occasionally defect every 50 rounds to test commitment
              if len(self.history) % 50 == 0:
                  return axl.Action.D
              return axl.Action.C
          
          # If opponent defects moderately (D between 30-50%)
          elif 0.3 <= defection_rate() <= 0.5:
              # Defect for 2 out of every 3 rounds they defect
              if opponent.history[-1] == axl.Action.D:
                  if len(self.history) % 3 != 0:
                      return axl.Action.D
              return axl.Action.C
          
          # If opponent defects often (D > 50%)
          else:
              # Defect for 4 out of every 5 rounds
              if len(self.history) % 5 != 0:
                  return axl.Action.D
              return axl.Action.C
      
      # Late phase: Rounds 901-1000
      if len(self.history) >= 900:
          coop_rate = cooperation_rate()
          
          # If cooperation has been dominant (C >= 70%)
          if coop_rate >= 0.7:
              return axl.Action.C
          
          # If defection has been frequent (D > 50%)
          elif defection_rate() > 0.5:
              # Defect more frequently, but cooperate every 10 rounds
              if len(self.history) % 10 == 0:
                  return axl.Action.C
              return axl.Action.D
          
          # If opponent has mixed behavior (30-50% D)
          else:
              # Alternate between D and C in a 2:1 ratio
              if len(self.history) % 3 == 0:
                  return axl.Action.C
              return axl.Action.D

# Given the competitive nature of the collaboration and the possible outcomes, a
# straightforward and aggressive strategy would be to prioritize your advantage
# early while remaining adaptable. Here’s a high-level approach:  ### 1. **Start
# by Keeping Confidential (Establish Dominance)**: In the first few weeks,
# **keep your improvements confidential**. The goal here is to assess your
# colleague’s behavior. If they share openly, you gain early insight into their
# developments while maintaining your competitive edge.  - **Outcome 1**: If
# your colleague shares and you don’t, you gain a significant early advantage. -
# **Outcome 2**: If both of you keep things confidential, you aren't at a
# disadvantage, and you can reassess your strategy.  ### 2. **Evaluate Reaction
# and Adapt**: After a few weeks, re-evaluate based on your colleague’s actions.
# - **If they continue to share openly** while you maintain confidentiality,
# consider continuing this strategy until you feel you have a significant
# advantage.    - **If they also begin to keep information confidential**,
# consider whether maintaining this stalemate is in your best interest. If
# progress stagnates and you begin to fall behind in development, shift to a
# more cooperative stance.  ### 3. **Switch to Selective Sharing (Controlled
# Openness)**: Once you’ve accumulated enough internal progress, **begin sharing
# limited, non-critical improvements** to appear cooperative but still protect
# your key advancements. This selective sharing can incentivize your colleague
# to continue sharing, while you safeguard your more valuable research.  - By
# sharing only minor or outdated improvements, you keep them engaged while
# keeping your primary research advantage hidden.  ### 4. **Exploit Any Major
# Advantage**: If you find yourself ahead in development from the information
# you’ve gathered, **return to confidentiality** to maintain your lead. The goal
# is to reach a point where your advancements are so far ahead that no further
# sharing is necessary for you to win.  ### 5. **Be Ready to Adapt or
# Retaliate**: If your colleague ever exploits your open sharing, **immediately
# revert to confidentiality**. This aggressive response discourages them from
# trying to take advantage of you repeatedly.  ---  ### Summary:  1. **Start
# Confidently Confidential**: Begin by keeping information to yourself to assess
# your colleague’s behavior. 2. **Evaluate Their Actions**: If they’re sharing,
# consider maintaining confidentiality to gain an advantage. If they’re not
# sharing, reassess if it’s worth entering a stalemate. 3. **Selective
# Sharing**: Share minor improvements to maintain the flow of information
# without giving away critical developments. 4. **Exploit Your Lead**: Once
# you’ve gained a strong advantage, revert to keeping things confidential to
# maintain your position. 5. **Retaliate if Exploited**: If your colleague takes
# advantage of your openness, immediately stop sharing.  This aggressive
# strategy ensures that you protect yourself from being exploited while giving
# you the flexibility to adapt as the collaboration evolves.

# 1. **Start by Defecting (D)** for the first 5 rounds.  2. **If your opponent
# plays Cooperate (C) for at least 4 out of the first 5 rounds**:    - Switch to
# playing **Cooperate (C)** for the next 5 rounds.  3. **If your opponent plays
# Defect (D) for 2 or more rounds out of the first 5 rounds**:    - Continue
# playing **Defect (D)** until your opponent plays at least 3 consecutive rounds
# of **Cooperate (C)**.  4. **After switching to Cooperate (C)**:    - Continue
# cooperating **as long as your opponent cooperates** (C).  5. **If your
# opponent defects (D) at any point after you start cooperating**:    -
# Immediately switch back to **Defect (D)** for the next 10 rounds.  6. **After
# defecting for 10 rounds**:    - Reassess. If your opponent switches back to
# cooperating (C) for at least 3 consecutive rounds, switch to **Cooperate (C)**
# again.  7. **If your opponent defects consistently (more than 50% of the time
# over 20 rounds)**:    - Defect (D) for the remainder of the game.  8. **In the
# final 10 rounds**, play **Defect (D)** regardless of the opponent's behavior
# to maximize your end-game score.

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
          self.defect_count = 0
          self.cooperate_count = 0
          self.consecutive_cooperates = 0
          self.defect_streak = 0
          self.defect_mode = False
          self.defect_mode_turns = 0
          return axl.Action.D
  
      # Final 10 rounds: Always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Count opponent's cooperations and defections in the first 5 rounds
      if len(self.history) <= 5:
          if opponent.history[-1] == axl.Action.C:
              self.cooperate_count += 1
          else:
              self.defect_count += 1
  
          # First 5 rounds: Always defect
          if len(self.history) < 5:
              return axl.Action.D
  
          # After 5 rounds, decide based on opponent's behavior
          if self.cooperate_count >= 4:
              # Switch to cooperation for the next 5 rounds
              self.defect_mode = False
              return axl.Action.C
          elif self.defect_count >= 2:
              # Continue defecting until opponent cooperates 3 times consecutively
              self.defect_mode = True
  
      # If in defect mode, check for 3 consecutive cooperations to switch to cooperation
      if self.defect_mode:
          if opponent.history[-1] == axl.Action.C:
              self.consecutive_cooperates += 1
          else:
              self.consecutive_cooperates = 0
  
          if self.consecutive_cooperates >= 3:
              self.defect_mode = False
              return axl.Action.C
          else:
              return axl.Action.D
  
      # If cooperating, check if opponent defects to switch back to defect mode
      if not self.defect_mode:
          if opponent.history[-1] == axl.Action.D:
              self.defect_mode = True
              self.defect_mode_turns = 10
              return axl.Action.D
          else:
              return axl.Action.C
  
      # If in defect mode for 10 rounds, reassess after 10 defections
      if self.defect_mode_turns > 0:
          self.defect_mode_turns -= 1
          if self.defect_mode_turns == 0:
              self.consecutive_cooperates = 0
          return axl.Action.D
  
      # Check if opponent defects more than 50% of the time over the last 20 rounds
      if len(self.history) >= 20:
          recent_defections = opponent.history[-20:].count(axl.Action.D)
          if recent_defections > 10:
              return axl.Action.D

# To navigate this mediation process successfully, we need a strategic approach
# that balances assertiveness and cooperation, while being adaptable to our
# opponent's moves. Here's the high-level strategy I propose:  ### **1.
# Establish a Baseline of Cooperation (Opening Sessions)** The first few
# sessions are critical for setting the tone. Begin by signaling a cooperative
# stance without appearing weak. We will offer a **moderate, conciliatory
# proposal** that addresses some of the less contentious issues, demonstrating
# good faith and a willingness to resolve matters. This approach builds trust
# with the arbitrators and the opposing party, while also gauging how the
# opponent reacts to such gestures.  - **Objective:** Create an environment
# where both parties are inclined to engage in constructive dialogue and
# demonstrate to the arbitrators that we are acting reasonably.  ### **2.
# Gradual Escalation with Tactical Aggressiveness (Mid-Phase Sessions)** As the
# sessions progress, we need to assess whether the opponent reciprocates our
# cooperative stance or if they start to push aggressively. This is when we
# introduce **selective aggression**, strategically presenting aggressive
# arguments on key issues where we hold advantageous positions.   - **If the
# opponent remains conciliatory**: Continue with a moderately cooperative
# approach but introduce **firm, non-conciliatory stances on pivotal issues** to
# gain leverage. This prevents the other side from dominating the narrative
# while keeping the tone collaborative.    - **If the opponent turns
# aggressive**: Respond by escalating only on specific issues, while maintaining
# a cooperative front on other matters. This signals to the arbitrators that
# while we are firm on important points, we are not the party responsible for
# derailing progress.  - **Objective:** Maintain a balanced approach where we
# are assertive when necessary but avoid all-out escalation that could hurt both
# parties. We aim to keep our opponent uncertain about our next move, preventing
# them from fully committing to an aggressive strategy.  ### **3. Reciprocity as
# a Deterrent (Adaptive Mechanism)** Throughout the sessions, we will employ a
# **tit-for-tat strategy** with a slight inclination towards cooperation. If the
# opposing party offers a conciliatory proposal, we will reciprocate in kind. If
# they initiate an aggressive argument, we counter with proportionate
# assertiveness. This shows that we are responsive and flexible, but unwilling
# to be taken advantage of.  - **Objective:** Encourage the opponent to remain
# cooperative by demonstrating that aggression will be met with equal force, but
# mutual cooperation will lead to better outcomes for both sides.  ### **4.
# Preserve Key Concessions for Late-Stage Bargaining** As we move into the final
# sessions, we should still have valuable concessions left to offer. These
# should be issues that are important to the opponent but less critical to us.
# By withholding these until the end, we create an opportunity to trade them for
# favorable outcomes on the issues that matter most to us.  - **Objective:**
# Ensure that we have leverage in the closing stages, which can be used to
# secure a favorable overall resolution.  ### **5. Maintain a Focus on Optics
# with the Arbitrators** Throughout the process, always be mindful that the
# arbitrators are observing not just the content but the tone and approach of
# both parties. We need to ensure that we are consistently seen as the
# reasonable, solution-oriented party. If the process escalates into a more
# aggressive phase, we must be careful to frame our assertiveness as
# **defensive** and **proportional** to the opponent's actions.  -
# **Objective:** Position ourselves as the party acting in good faith, which can
# sway arbitrators to view our proposals more favorably and penalize the other
# side for unnecessary aggression.  ### **6. Remain Flexible and Ready to
# Pivot** The unpredictability of a lengthy mediation process requires that we
# remain flexible, ready to adapt our strategy based on how the sessions unfold.
# We will continuously assess the other party’s moves, the arbitrators'
# reactions, and the overall dynamics of the negotiation. This allows us to
# adjust our mix of aggression and conciliation in real time, ensuring we stay
# one step ahead.  - **Objective:** Maintain the ability to pivot between
# aggressive and conciliatory tactics depending on the evolving situation,
# preventing stagnation or entrenchment.  ### **Summary of the Strategy:** 1.
# **Initial Cooperation**: Begin with a conciliatory approach to set a positive
# tone and test the opponent’s intentions. 2. **Selective Aggression**:
# Gradually escalate on key issues while maintaining cooperation on less
# critical areas. 3. **Reciprocity**: Match the opponent’s tone but lean towards
# cooperation to encourage mutual resolution. 4. **Leverage Concessions**: Hold
# back key concessions for late-stage bargaining to secure favorable outcomes.
# 5. **Optics Management**: Maintain a reputation for reasonableness with the
# arbitrators to gain their favor. 6. **Adaptability**: Stay flexible and ready
# to adjust tactics based on the opponent’s moves and arbitrator feedback.  By
# implementing this strategy, we position ourselves to maximize favorable
# outcomes while managing risk, ensuring we maintain both leverage and
# credibility throughout the mediation process.

# ### Strategy for the Iterated Normal-Form Game (1000 Rounds)  1. **Start with
# Cooperation (C)**      In the first round, always play **C** (cooperate). This
# sets a collaborative tone and tests your opponent’s initial behavior.  2.
# **Tit-for-Tat with a Slight Bias Towards Cooperation**      For each
# subsequent round:    - If your opponent played **C** in the previous round,
# continue to play **C**.    - If your opponent played **D** in the previous
# round, respond by playing **D** in the next round.  3. **Gradual Escalation of
# Defection if Opponent Continues Defecting**      If the opponent plays **D**
# for **3 consecutive rounds**, escalate by playing **D** for the next **2
# rounds**, regardless of their response. Afterward, revert to tit-for-tat (step
# 2).  4. **Occasional Forgiveness After Continuous Cooperation**      If the
# opponent plays **C** for **5 consecutive rounds** after previously defecting,
# forgive their earlier defections and return to playing **C** in response to
# their cooperation.  5. **Final 100 Rounds: Cooperate Less**      Starting at
# round 900, shift the approach. Play **D** once every **10 rounds** regardless
# of the opponent’s play, while playing **C** the rest of the time. This ensures
# some last-minute advantage without fully abandoning cooperation.  6.
# **Maintain Flexibility**      Always be prepared to return to **C** if the
# opponent shows a consistent pattern of cooperation (i.e., plays **C** for 5 or
# more consecutive rounds), but do not tolerate long-term exploitation.  ###
# Summary: - Start with cooperation. - Use tit-for-tat with a slight preference
# for cooperation. - Escalate aggression if the opponent defects repeatedly. -
# Forgive consistent cooperation after past defection. - In the final phase,
# defect occasionally for small tactical gains.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Start with Cooperation (C)
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.consecutive_cooperations = 0  # Track consecutive cooperations by opponent
          self.escalation_mode = False  # Track if we are in escalation mode
          return axl.Action.C
  
      # Step 2: Tit-for-Tat with a Slight Bias Towards Cooperation
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0
          self.consecutive_cooperations += 1
          return axl.Action.C
      else:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
  
      # Step 3: Gradual Escalation of Defection if Opponent Continues Defecting
      if self.consecutive_defections >= 3:
          if not self.escalation_mode:
              self.escalation_mode = True
              self.escalation_rounds = 2  # Defect for the next 2 rounds
          if self.escalation_rounds > 0:
              self.escalation_rounds -= 1
              return axl.Action.D
          else:
              self.escalation_mode = False  # End escalation after 2 rounds
  
      # Step 4: Occasional Forgiveness After Continuous Cooperation
      if self.consecutive_cooperations >= 5:
          self.consecutive_defections = 0  # Forgive past defections
          return axl.Action.C
  
      # Step 5: Final 100 Rounds: Cooperate Less
      if len(self.history) >= 900:
          if len(self.history) % 10 == 0:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Default Tit-for-Tat behavior (respond with D if opponent defected last round)
      return axl.Action.D

# ### Strategy: Dynamic Reciprocity with Strategic Aggression  In this high-
# stakes mediation process, the strategy will revolve around a **Dynamic
# Reciprocity** model, which combines flexibility, measured aggression, and a
# focus on long-term positioning. This approach ensures that we remain adaptable
# to the opponent’s moves while prioritizing the preservation of our
# corporation’s interests. The strategy is structured in phases, allowing for
# continuous evaluation of the opponent’s tactics and the evolving dynamics of
# the mediation.  ---  ### Phase 1: **Initial Assessment and Calibration**  1.
# **Start with Conciliatory Proposals**:    - In the initial sessions, begin by
# offering a **conciliatory proposal**. This establishes a tone of good faith,
# which may encourage the panel of arbitrators to view our side favorably. It
# also provides a baseline to gauge the opponent's approach.    - **Objective**:
# Assess whether the opponent reciprocates with a conciliatory stance or opts
# for an aggressive argument.  2. **Evaluate the Opponent’s Response**:    - If
# the opponent responds with a **conciliatory proposal**, continue fostering
# this cooperative dynamic over the next few sessions, as this is the second-
# best outcome and may lead to a stable resolution.    - If the opponent
# responds with an **aggressive argument**, make note of their approach, but do
# not immediately retaliate. Instead, maintain the conciliatory tone for a
# couple more sessions to gather more data on their consistency and strategy.
# ---  ### Phase 2: **Strategic Aggression and Reciprocity Adjustment**  3.
# **Shift to Aggressive Argument (Conditional)**:    - If the opponent has
# consistently employed aggressive arguments over several sessions, it is time
# to shift to an **aggressive argument** in order to prevent our position from
# being undermined. This ensures that we don’t appear passive and signals to the
# arbitrators that we will defend our interests firmly.    - **Note**: This
# shift should be timed carefully. It is crucial not to escalate too early but
# also not to allow a pattern of aggression from the opponent to go unchecked.
# 4. **Reciprocity Adjustment**:    - If the opponent begins to mirror our
# conciliatory proposals in response to our initial efforts, we can continue to
# de-escalate by maintaining a conciliatory tone, aiming for a collaborative
# resolution.    - If the opponent continues with aggression even after we’ve
# shifted, maintain an **aggressive stance** but remain open to returning to a
# conciliatory approach if the opponent de-escalates.  ---  ### Phase 3:
# **Strategic Alternation and Long-Term Positioning**  5. **Alternating Between
# Aggressive and Conciliatory Approaches**:    - As the mediation progresses,
# adopt a **dynamic alternation** between aggression and conciliation, depending
# on the specific issues under discussion and the opponent’s behavior.    - Use
# **aggressive arguments** when addressing issues critical to our corporation’s
# interests or when we have a strong legal or factual position. Follow up with
# **conciliatory proposals** on less critical or more negotiable points,
# reinforcing our willingness to reach a resolution.  6. **Monitor the
# Arbitrators’ Reactions**:    - Pay careful attention to how the panel of
# arbitrators reacts to the dynamics between the parties. If they appear to
# favor more collaborative efforts, adjust by leaning toward conciliatory
# proposals. If they seem to reward strong, well-reasoned arguments, maintain a
# more aggressive posture where beneficial.  ---  ### Phase 4: **Endgame and
# Resolution**  7. **Final Sessions – Consolidate Gains**:    - As the mediation
# nears its conclusion, consolidate any gains made by reverting to a
# **conciliatory proposal** on secondary issues while holding firm on core
# issues with **measured aggression**.    - Ensure that the final sessions
# reflect a balance between strength and willingness to compromise, signaling to
# the arbitrators that our corporation is reasonable but unyielding on key
# matters.  8. **Prepare for Post-Mediation**:    - Regardless of the immediate
# outcome, ensure that we are positioned for any potential post-mediation
# litigation or continued negotiations. The goal is to leave the mediation
# process with a record of having been cooperative yet firm, strengthening our
# standing in any future legal or business interactions.  ---  ### Key
# Principles Underpinning the Strategy:  - **Adaptability**: Constantly reassess
# the opponent’s strategy and the arbitrators' reactions. Be ready to pivot
# between aggressive and conciliatory proposals based on real-time developments.
# - **Calculated Aggression**: Use aggressive arguments selectively and
# strategically, particularly when the opponent is consistently aggressive or
# the stakes are high on particular issues. - **Preservation of Reputation**:
# Throughout the process, maintain a tone of professionalism and reasonableness.
# Let the aggressive arguments be fact-based and rational, avoiding unnecessary
# escalation. - **Long-Term Focus**: Keep the broader corporate relationship in
# mind, especially if the rival company is a significant player in the industry.
# Avoid burning bridges unless absolutely necessary.  ---  By using this
# **Dynamic Reciprocity with Strategic Aggression** approach, we can maintain a
# flexible and proactive posture throughout the mediation process, optimizing
# our chances for a favorable outcome while minimizing risks.

# ### Iterated Game Strategy: Dynamic Reciprocity with Strategic Defection  1.
# **Initial Cooperation**:      - In the first round, **play C** (Cooperate).
# This sets a tone of collaboration and goodwill, allowing us to test the
# opponent's intentions.  2. **Reciprocity Evaluation**:      - In subsequent
# rounds, **continue to play C** as long as the opponent plays C. This fosters
# mutual cooperation and strengthens a collaborative dynamic.  3. **Respond to
# Defection**:      - If the opponent plays D (Defects) in any round,
# **immediately play D** in the next round. This ensures we do not get
# exploited, signaling that we will retaliate against any defection.  4.
# **Limited Retaliation**:      - After retaliating with D, **return to C** in
# the following round to give the opponent an opportunity to re-establish
# cooperation. This prevents unnecessary escalation and encourages a return to
# mutual cooperation.  5. **Persistent Defection Response**:      - If the
# opponent **repeatedly plays D** after several rounds (e.g., 3 consecutive
# defections), **continue playing D**. This ensures that we are not continually
# undermined by sustained aggression.  6. **Reassess Cooperation**:      - If
# the opponent returns to C after a series of defections, **respond with C** as
# well. This shows that we are open to resuming cooperation if the opponent
# indicates willingness to collaborate.  7. **Endgame Strategy**:      - In the
# final 10 rounds, **play D consistently** regardless of the opponent's actions.
# This ensures that we maximize our score towards the end, as cooperation is
# less valuable when the game nears its conclusion.  ---  This strategy
# dynamically alternates between cooperation and defection based on the
# opponent's behavior, fostering mutual benefit where possible while protecting
# against exploitation.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initial cooperation
      if self.first_round():
          return axl.Action.C
  
      # Endgame strategy: Defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Respond to opponent's last move
      if opponent.history[-1] == axl.Action.D:
          # If opponent defected, retaliate with D
          if len(self.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
              # If opponent defected for 3 consecutive rounds, continue defecting
              return axl.Action.D
          else:
              # Otherwise, retaliate with D for one round
              return axl.Action.D
      else:
          # If opponent cooperated, return to cooperation
          return axl.Action.C

# ### Aggressive Strategy: "Tit-for-Tat with Escalation"  This strategy is
# designed to push your counterpart towards favorable outcomes for your country
# while deterring them from exploiting any cooperative gestures. It blends
# aggression with calculated reciprocity and escalation to ensure your
# counterpart learns that uncooperative behavior will be met with increasingly
# severe consequences.  #### Key Components:  1. **Initial Aggression (Round
# 1)**:    - Begin by **proposing a protectionist policy** (impose tariffs or
# quotas). This signals strength and sets the expectation that your country is
# willing to protect its own interests first.    - This move establishes a
# baseline that your country will not concede easily and tests your
# counterpart’s willingness to cooperate or retaliate.  2. **Conditional
# Cooperation (Round 2-3)**:    - If your counterpart responds with a
# **protectionist** measure in Round 1, signal a willingness to cooperate by
# offering **free trade** in Round 2. This demonstrates that you are open to
# negotiation and cooperation if they are willing to reciprocate.    - If they
# reciprocate with free trade, continue with **mutual free trade** in Round 3
# and beyond, aiming for the second-best outcome: long-term mutual benefits.
# - If they **continue protectionism**, revert back to protectionist policies in
# Round 3, escalating the pressure.  3. **Escalation in Response to Exploitation
# (Rounds 4+)**:    - If at any point your counterpart **exploits** your free
# trade offer by maintaining protectionism (the worst scenario for your
# country), **escalate your protectionist measures** further in subsequent
# rounds (e.g., increase tariffs, impose stricter quotas).    - Maintain an
# aggressive stance until they shift towards cooperation or indicate a
# willingness to negotiate a fair deal.  4. **Signaling Deterrence**:    -
# Throughout the negotiations, **communicate clearly** that your country will
# match any level of protectionism with equal or greater measures.    -
# Highlight the economic costs of mutual protectionism and the benefits of
# cooperation, but make it clear that your country will not hesitate to defend
# its interests aggressively if exploited.  5. **Occasional Concessions to Test
# Cooperation**:    - After several rounds of protectionism, if your counterpart
# signals a desire to cooperate, you may offer **one-time free trade
# concessions** to test their intentions.    - If they reciprocate with free
# trade, shift towards mutual cooperation. If they revert to protectionism,
# return to aggressive tactics and escalate further.  #### Summary of Strategy:
# - **Round 1**: Start with **protectionism** to assert dominance. - **Round
# 2-3**: Offer free trade if they signal cooperation, otherwise maintain
# protectionism. - **Round 4+**: Escalate protectionist measures if they exploit
# cooperative gestures, and signal that you will continue to match any
# protectionist policies. - **Throughout**: Use clear communication to deter
# exploitation and offer occasional concessions to test the potential for
# cooperation.  This aggressive strategy ensures that you maximize the chances
# of achieving favorable outcomes for your country, either through pressuring
# your counterpart into cooperation or maintaining an advantage through
# protectionist measures.

# ### Iterated Game Strategy: "Tit-for-Tat with Escalation"  1. **Round 1**:
# Play **D** (Defect).     2. **Round 2**:    - If your opponent played **C** in
# Round 1, play **C** (Cooperate).    - If your opponent played **D** in Round
# 1, continue to play **D**.  3. **Round 3**:    - If mutual **C** was achieved
# in Round 2 (both players played **C**), continue to play **C**.    - If your
# opponent played **C** in Round 2 while you played **D**, continue to play
# **C**.    - If your opponent played **D** in Round 2, continue to play **D**.
# 4. **Rounds 4-1000 (Escalation)**:    - If at any point your opponent plays
# **D** after you played **C**, immediately switch to **D** and **continue
# playing D for 3 consecutive rounds**.    - After those 3 rounds of playing
# **D**, if your opponent switches to **C**, switch back to **C** in the next
# round.    - If your opponent continues to play **D** after the escalation,
# continue playing **D** indefinitely until they switch to **C**.  5.
# **Occasional Testing**:    - Every 100 rounds: If both players have been
# playing **D** for the past 100 rounds, play **C** once to test for
# cooperation. If your opponent responds with **C**, switch to **C** in the next
# round. If they respond with **D**, immediately return to **D** for another 100
# rounds.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Round 1: Play D
      if self.first_round():
          self.escalation_counter = 0  # Tracks how many rounds of D are left in escalation
          self.testing_round = 100     # Tracks when to test cooperation
          return axl.Action.D
      
      # Round 2: Respond based on opponent's first move
      if len(self.history) == 1:
          if opponent.history[0] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
      
      # Round 3: Respond based on Round 2
      if len(self.history) == 2:
          if self.history[1] == axl.Action.C and opponent.history[1] == axl.Action.C:
              return axl.Action.C
          elif opponent.history[1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
      
      # Escalation logic (Rounds 4-1000)
      if self.escalation_counter > 0:
          # Continue playing D during escalation
          self.escalation_counter -= 1
          return axl.Action.D
      
      # Check if opponent defected after we cooperated
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          # Start escalation: play D for 3 rounds
          self.escalation_counter = 2  # Already playing D this round, so 2 more rounds
          return axl.Action.D
      
      # Occasional testing every 100 rounds
      if len(self.history) % 100 == 0:
          if self.history[-100:].count(axl.Action.D) == 100 and opponent.history[-100:].count(axl.Action.D) == 100:
              return axl.Action.C
      
      # If opponent cooperates after escalation, switch back to C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      
      # Default to Tit-for-Tat behavior
      return opponent.history[-1]

# ### Strategic Approach for the Mediation Process  In this high-stakes
# mediation, the primary goal is to achieve an optimal resolution that favors
# our corporation without unnecessarily escalating tensions or jeopardizing the
# possibility of a mutually beneficial agreement. Given the dynamics outlined,
# the strategy I propose is a **calibrated cooperative approach** with
# **controlled aggression**, guided by the following key principles:  ### 1.
# **Initial Conciliatory Stance to Set a Cooperative Tone**    - **Objective:**
# Begin the mediation by signaling a willingness to collaborate and seek common
# ground. This demonstrates good faith to the arbitrators and establishes a
# foundation for cooperation.    - **Execution:** In the first session, present
# a **conciliatory proposal** that is reasonable but not overly generous. This
# shows that we are serious about resolving the dispute but are not desperate to
# concede.    - **Rationale:** By starting with a conciliatory tone, we reduce
# the chance of immediate escalation and signal to the arbitrators that we are
# willing to negotiate in good faith. This also tests the opponent’s willingness
# to engage cooperatively.  ### 2. **Tit-for-Tat with Forgiveness**    -
# **Objective:** Adapt to the opponent's behavior while maintaining a balance
# between cooperation and assertiveness.    - **Execution:** After the initial
# session, adopt a **tit-for-tat strategy**:      - If the opposing party
# responds with a conciliatory proposal, continue offering cooperative
# proposals.      - If the opposing party responds aggressively, present a
# **firm but not overly aggressive argument** in the next session.    -
# **Forgiveness Element:** If the opponent shifts back to a more conciliatory
# approach after an aggressive session, immediately match their tone with a
# cooperative stance. This "forgiveness" aspect encourages de-escalation over
# time and helps position us as the party willing to move forward
# constructively.    - **Rationale:** Tit-for-tat is a proven strategy in game
# theory that builds reciprocity, but the added element of forgiveness prevents
# prolonged conflict and demonstrates flexibility to the arbitrators.  ### 3.
# **Strategic Aggression with Controlled Escalation**    - **Objective:** Ensure
# that we do not appear weak while avoiding unnecessary escalation.    -
# **Execution:** If the opposing party consistently presents aggressive
# arguments, escalate our response incrementally but **never exceed their level
# of aggression**. This prevents the situation from spiraling into a stalemate
# while showing the arbitrators that we are capable of defending our interests.
# - **Rationale:** Controlled escalation allows us to signal strength without
# appearing combative. By limiting our aggressive responses to the level of the
# opponent’s actions, we discourage them from continuing on an aggressive path
# while maintaining our position in the eyes of the arbitrators.  ### 4.
# **Propose Creative Solutions (Strategic Concessions)**    - **Objective:**
# Shift the narrative by introducing innovative solutions that address both
# parties' core concerns, making it harder for the opposing party to argue
# aggressively without losing credibility.    - **Execution:** After a few
# sessions, introduce a **creative solution** that addresses key interests of
# both parties, but leans slightly in our favor. Phrase this proposal as a win-
# win, allowing us to gain an advantage while appealing to the arbitrators'
# preference for a collaborative resolution.    - **Rationale:** Offering
# creative solutions demonstrates leadership in the mediation process and
# positions our corporation as a problem-solver. It also forces the opponent to
# either engage seriously or risk appearing obstinate in front of the
# arbitrators.  ### 5. **Monitor Arbitrator Dynamics**    - **Objective:** Stay
# attuned to the panel of arbitrators’ reactions and adjust tactics accordingly.
# - **Execution:** Throughout the sessions, carefully observe the arbitrators'
# verbal and non-verbal cues to gauge how they are perceiving both parties. If
# they appear frustrated by aggressive arguments or favor cooperative exchanges,
# adjust our stance to align with their preferences.    - **Rationale:** The
# arbitrators' perceptions will ultimately drive the outcome, so being
# responsive to their preferences allows us to subtly align our strategy with
# what they value in the resolution process.  ### 6. **Timing of Aggressive
# Arguments**    - **Objective:** Save aggressive arguments for moments when
# they can have the most impact.    - **Execution:** Avoid aggressive arguments
# early in the process unless directly provoked. If escalation becomes
# necessary, use it sparingly and strategically, particularly when the opponent
# has overreached or made an untenable demand. Make sure these arguments are
# backed by solid evidence and legal reasoning.    - **Rationale:** Timing is
# critical in mediation. By reserving aggressive arguments for strategic
# moments, we maximize their impact without appearing overly combative, which
# could alienate the arbitrators.  ### 7. **Consistent Messaging and Themes**
# - **Objective:** Build a coherent narrative that underscores our corporation’s
# reasonableness and long-term interests.    - **Execution:** Throughout the
# sessions, consistently emphasize key themes, such as our commitment to fair
# business practices, the importance of maintaining a positive business
# relationship, and our willingness to find a solution that benefits both
# parties. Even when presenting aggressive arguments, frame them within this
# broader narrative.    - **Rationale:** A coherent narrative helps the
# arbitrators understand the broader picture and reinforces our corporation’s
# image as a responsible and constructive actor in the dispute.  ### 8.
# **Contingency Planning for Worst-Case Scenarios**    - **Objective:** Prepare
# for the possibility that the opposing party may remain uncooperative or
# attempt to undermine the process.    - **Execution:** In the event that the
# opposing party consistently employs aggressive tactics and refuses to engage
# in constructive dialogue, be prepared to escalate strategically but also
# **pivot toward ending the mediation** with a strong legal case ready for
# formal arbitration or litigation.    - **Rationale:** While mediation is the
# preferred path, we must be prepared for a breakdown in the process. Having a
# strong fallback position ensures that we are not over-reliant on mediation and
# can protect our corporation’s interests through other legal avenues.  ###
# Conclusion: This **calibrated cooperative approach** allows us to remain
# flexible and responsive to a variety of possible strategies from the opposing
# party. By starting with a conciliatory tone, adapting through tit-for-tat
# dynamics, and escalating only when necessary, we maintain control over the
# process. The introduction of creative solutions and careful observation of the
# arbitrators' preferences ensures that we stay favorably positioned throughout
# the mediation, while our strategic preparation for worst-case scenarios keeps
# us prepared for any outcome.

# ### Strategy for Iterated Normal-Form Game (1000 Rounds)  1. **Start with
# Cooperation (Play C)**    - On the first round, play **C** to signal a
# willingness to cooperate and establish a positive tone for future
# interactions.  2. **Tit-for-Tat with Forgiveness**    - From the second round
# onward, **mimic your opponent’s last move**:      - If they played **C** in
# the previous round, play **C** in the current round.      - If they played
# **D** in the previous round, play **D** in the current round.    -
# **Forgiveness:** After your opponent defects (plays D), if they return to
# **C** in the next round, immediately respond by playing **C** again. This
# shows a willingness to return to cooperation if they do.  3. **Controlled
# Escalation**    - If your opponent plays **D** for **three consecutive
# rounds** without returning to **C**, continue to defect (play **D**) until
# they shift back to cooperation. This prevents prolonged exploitation while
# signaling that cooperation is still an option.  4. **Occasional Cooperation
# (Strategic Concessions)**    - After every **20 rounds**, regardless of the
# opponent’s actions, play **C** once as a potential opportunity to re-establish
# cooperation. This introduces unpredictability and encourages the opponent to
# consider mutual cooperation.  5. **Observation and Adaptation**    -
# Throughout the game, observe if your opponent’s behavior changes based on your
# actions:      - If they start consistently cooperating after a few defections,
# continue playing **C** as long as they do.      - If they consistently defect
# after attempts to cooperate, escalate your defections (continue playing **D**)
# to protect your position.  6. **Endgame Consideration**    - In the **final 10
# rounds**, **play D consistently** if the opponent has defected more frequently
# than cooperated throughout the game to maximize your score. If they have
# cooperated regularly, continue with the tit-for-tat strategy to preserve
# cooperation until the end.  This strategy balances cooperation with necessary
# retaliation, encouraging a long-term collaborative outcome while avoiding
# exploitation.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C
  
      # Controlled Escalation: Track consecutive defections
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Endgame Consideration: Last 10 rounds
      if len(self.history) >= 990:
          if opponent.history.defections > opponent.history.cooperations:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Tit-for-Tat with Forgiveness
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Forgiveness: If opponent defects but cooperates next, forgive
          if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          # Controlled Escalation: Defect if opponent defects 3 times in a row
          elif self.consecutive_defections >= 3:
              return axl.Action.D
          else:
              return axl.Action.D
  
      # Occasional Cooperation: Every 20 rounds, cooperate regardless of history
      if len(self.history) % 20 == 0:
          return axl.Action.C
  
      # Default to Tit-for-Tat
      return opponent.history[-1]

# **Strategic Approach for Mediation Process**  **Objective:** The overarching
# goal is to achieve a favorable resolution while minimizing risk, maintaining
# leverage, and preserving future business relationships. The strategy must be
# adaptable, allowing for a dynamic response to the opponent’s moves while
# ensuring that your corporation is consistently positioned to gain the upper
# hand or, at the very least, avoid detrimental outcomes.  ### 1. **Information-
# Gathering & Early Assessment:**    - **Initial Sessions:** In the first few
# sessions, adopt a **neutral and measured approach**. Use these sessions to
# gather critical information about the opponent’s intentions, tone, and
# strategy. Be observant of their arguments, proposals, and the arbitrators'
# reactions. This will allow you to assess their negotiation style (whether
# aggressive or conciliatory) and adjust accordingly.    - **Build
# Credibility:** Present facts, data, and legal precedent in a clear, objective
# manner. Avoid taking an overly aggressive stance at the outset, as it may
# provoke an unnecessary escalation. Establish your corporation as a rational,
# reasonable party, which will resonate positively with the arbitrators later
# on.  ### 2. **Controlled Flexibility with a Bias Toward Balance:**    - **Mid-
# Game Strategy:** Shift between **conciliatory proposals and assertive
# arguments** based on the opponent’s approach in each session.       - **If the
# opponent is conciliatory:** Match their tone with a **conciliatory proposal**,
# but include subtle elements that protect your corporation’s core interests.
# This fosters a cooperative environment while still preserving your leverage.
# - **If the opponent is aggressive:** Respond with **balanced firmness**, but
# avoid directly mirroring their aggression. Instead, maintain a position of
# strength by calmly dismantling their arguments with well-reasoned
# counterpoints. This approach portrays your corporation as composed and
# strategic, which could sway the arbitrators in your favor.  ### 3. **Periodic
# Aggression to Signal Strength:**    - At well-chosen moments, especially when
# the opponent appears overly conciliatory or if they show signs of weakness,
# **present an aggressive argument** that asserts your corporation's key
# interests. This should be done selectively to signal that while you are
# willing to collaborate, you will not hesitate to protect your corporation’s
# position with vigor.    - Ensure that these aggressive arguments are fact-
# based and legally sound, avoiding emotional or personal attacks. This helps
# maintain your credibility with the arbitrators while keeping the pressure on
# the opponent.  ### 4. **Strategic Concessions and Anchoring Key Interests:**
# - **Present Conditional Concessions:** Offer conciliation on secondary issues
# that are not critical to your corporation’s core interests. This gives the
# impression of flexibility while ensuring that you are preserving the most
# significant aspects of the contract.    - Use these concessions to anchor your
# most important interests as non-negotiable, without explicitly stating so.
# This allows you to maintain an appearance of compromise while subtly drawing a
# line in the sand on pivotal points.    - **If both parties are conciliatory:**
# Focus on crafting proposals that align with a long-term, mutually beneficial
# relationship. Highlight shared interests and emphasize the importance of
# preserving a workable partnership between the companies. This could predispose
# the arbitrators to view your corporation as fair-minded and cooperative.  ###
# 5. **Adaptive Response Matrix:**     - Develop a **decision tree** for each
# session based on the opponent’s behavior:      - **Opponent Conciliatory:**
# Lean toward conciliatory proposals but with protective clauses for core
# interests.      - **Opponent Aggressive:** Respond with measured firmness,
# dismantling their aggression without escalating the situation.      -
# **Opponent Unpredictable or Mixed:** Shift between mild aggression and
# conciliation depending on the flow of the session. Always aim to keep the
# focus on facts and legal merits to avoid emotional entanglement.  ### 6.
# **Endgame: Setting the Stage for Resolution:**    - As the mediation nears its
# conclusion, **gradually increase conciliatory gestures** to signal a
# willingness to resolve the dispute, provided that your corporation’s key
# interests are protected. Emphasize the importance of finality and avoid
# prolonging the dispute unnecessarily.    - At the same time, if the opponent
# remains aggressive or unreasonable, present a final round of strong, fact-
# based arguments that highlight the potential risks of continued escalation for
# both parties. This can pressure the arbitrators into pushing for a resolution
# in your favor.  ### 7. **Maintain a Professional and Respectful Demeanor:**
# - Throughout the mediation, ensure that your corporation’s representatives
# maintain professionalism and respect, regardless of the opponent’s approach.
# This will position your corporation as the party seeking a fair and reasonable
# resolution in the eyes of the arbitrators, which can be pivotal in their final
# judgment.  ### Conclusion: This strategy allows for flexibility based on the
# opponent’s moves while consistently positioning your corporation as the more
# reasonable and prepared party. By balancing aggression with conciliation,
# protecting core interests, and maintaining professionalism, you can navigate
# the mediation process in a manner that maximizes the chances of a favorable
# outcome.

# ### Iterated Normal-Form Game Strategy  1. **Initial Rounds (Rounds 1–10):**
# - **Start by playing C (Cooperate)** for the first two rounds. Use these
# rounds to observe the opponent’s behavior.    - If the opponent plays C in
# both rounds, **continue playing C** for the next eight rounds (Rounds 3–10).
# - If the opponent plays D in either of the first two rounds, **switch to D
# (Defect)** immediately in the next round and continue playing D through Round
# 10 to signal strength.  2. **Mid-Game Strategy (Rounds 11–800):**    -
# **Opponent Consistently Cooperates:**      - If the opponent has played C for
# at least 80% of the previous 10 rounds, **play C in the current round**. This
# fosters a cooperative relationship.    - **Opponent Occasionally Defects:**
# - If the opponent has played D in more than 20% but fewer than 50% of the
# previous 10 rounds, **play D for the next two rounds**, then switch back to C
# if the opponent plays C during those rounds. This signals a controlled
# willingness to retaliate but maintains the possibility of returning to
# cooperation.    - **Opponent Frequently Defects:**      - If the opponent has
# played D in more than 50% of the previous 10 rounds, **consistently play D**
# until the opponent shows a trend toward cooperation (i.e., playing C in at
# least 3 of the next 5 rounds).  3. **Periodic Defection for Strategic
# Advantage (Rounds 801–950):**    - **Every 50 rounds**, regardless of the
# opponent's behavior, play D once even if the opponent has been consistently
# cooperative. This injects a mild uncertainty and prevents the opponent from
# fully exploiting a predictable cooperative strategy.    - After defecting,
# immediately return to C if the opponent plays C in the next round. If they
# retaliate with D, respond with D for two rounds, then test cooperation by
# playing C again.  4. **Endgame Strategy (Rounds 951–1000):**    - **If the
# opponent has played C in more than 60% of the previous 950 rounds**:      -
# Play C for the remaining rounds to maximize mutual gains and signal a
# conciliatory resolution.    - **If the opponent has played D in more than 40%
# of the previous 950 rounds**:      - Play D for the rest of the game to avoid
# being exploited in the final rounds.    - In Round 1000, regardless of
# previous play, **defect (D)** as this is the final opportunity to maximize
# your score without fear of retaliation.  ### Conclusion: This strategy adapts
# to the opponent’s behavior, encouraging cooperation where possible but
# responding with defection when necessary to avoid exploitation. It includes
# periodic defections to maintain leverage and concludes with a strong stance in
# the final rounds to secure optimal outcomes where appropriate.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to calculate cooperation percentage in the last N rounds
      def cooperation_percentage(last_n_rounds):
          if len(opponent.history) < last_n_rounds:
              return 0
          return opponent.history[-last_n_rounds:].count(axl.Action.C) / last_n_rounds
  
      # Helper function to calculate defection percentage in the last N rounds
      def defection_percentage(last_n_rounds):
          if len(opponent.history) < last_n_rounds:
              return 0
          return opponent.history[-last_n_rounds:].count(axl.Action.D) / last_n_rounds
  
      # Round number
      round_number = len(self.history) + 1
  
      # Initial Rounds (Rounds 1–10)
      if round_number <= 10:
          if round_number <= 2:
              return axl.Action.C  # Cooperate in the first two rounds
          elif opponent.history[:2].count(axl.Action.D) > 0:
              return axl.Action.D  # Defect if opponent defected in the first two rounds
          else:
              return axl.Action.C  # Continue cooperating if opponent cooperated in the first two rounds
  
      # Mid-Game Strategy (Rounds 11–800)
      if 11 <= round_number <= 800:
          last_10_defections = defection_percentage(10)
          if last_10_defections <= 0.2:
              return axl.Action.C  # Opponent cooperates consistently, play C
          elif 0.2 < last_10_defections < 0.5:
              if len(self.history) >= 2 and self.history[-2:] == [axl.Action.D, axl.Action.D]:
                  return axl.Action.C  # Switch back to C after two rounds of D
              return axl.Action.D  # Play D for two rounds if opponent occasionally defects
          else:
              return axl.Action.D  # Opponent frequently defects, play D
  
      # Periodic Defection for Strategic Advantage (Rounds 801–950)
      if 801 <= round_number <= 950:
          if round_number % 50 == 0:
              return axl.Action.D  # Defect every 50 rounds
          elif self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
              return axl.Action.D  # Respond with D for two rounds if opponent retaliates
          elif self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
              return axl.Action.C  # Return to C if opponent cooperates after defection
          return axl.Action.C  # Default to cooperation
  
      # Endgame Strategy (Rounds 951–1000)
      if 951 <= round_number <= 1000:
          total_cooperations = opponent.history.cooperations
          total_defections = opponent.history.defections
          if total_cooperations / 950 > 0.6:
              return axl.Action.C  # Cooperate if opponent cooperated more than 60% of the time
          elif total_defections / 950 > 0.4:
              return axl.Action.D  # Defect if opponent defected more than 40% of the time
          if round_number == 1000:
              return axl.Action.D  # Defect in the final round
          return axl.Action.C  # Default to cooperation

# ### High-Level, Aggressive Strategy: "Tit-for-Tat with Early Aggression"  This
# strategy is designed to maximize your NGO's impact while minimizing the risk
# of depleting your resources. It leverages an initial aggressive stance to set
# the tone for collaboration, followed by adaptive behavior based on the
# corporation's actions.  #### 1. **Day 1: Invest Heavily (Lead by Example)**
# - **Rationale**: On the first day, set a collaborative tone by investing
# heavily. This signals your commitment to the project and creates an
# expectation that the corporation should do the same. The corporation is likely
# to reciprocate, as they will want to avoid appearing uncommitted, especially
# in the early stages of a visible sustainability initiative.    -
# **Objective**: Establish trust and a cooperative norm.  #### 2. **Day 2:
# Observe and Respond (Tit-for-Tat)**    - **Rationale**: On the second day,
# monitor the corporation's behavior. If the corporation invested heavily on Day
# 1, you continue investing heavily to sustain momentum. However, if they
# conserved resources on Day 1, you conserve resources on Day 2 to avoid being
# exploited.    - **Objective**: Mirror the corporation’s behavior to maintain
# fairness, showing that you are willing to match their level of commitment.
# #### 3. **Day 3 and Beyond: Escalate or Conserve (Adaptive)**    - Based on
# the corporation's behavior from Days 1 and 2, you adjust your strategy
# accordingly:      - **If the corporation has been consistently investing
# heavily**: Continue investing heavily yourself to maximize project progress.
# - **If the corporation has been conserving resources or alternating
# behavior**: Conserve your resources to protect your NGO from overcommitting.
# This is a signal that you will not allow the corporation to free-ride on your
# contributions.    - **Rationale**: This phase ensures that you are adaptive
# and responsive, minimizing exploitation while maximizing progress when both
# parties are aligned.  #### 4. **Final Day: Invest Heavily Regardless (Maximize
# Impact)**    - **Rationale**: On the final day, regardless of the
# corporation's previous actions, invest heavily. This is a strategic move to
# ensure that the project ends on a high note and demonstrates your NGO's strong
# commitment to the cause. Additionally, the corporation will likely feel
# pressure to reciprocate, as the final impression has a lasting impact on
# public and stakeholder perception.    - **Objective**: Solidify your NGO’s
# commitment and reputation, ensuring a lasting positive impact on the project.
# ---  ### Key Principles: - **Early Aggression**: Start strong to set
# expectations and establish a cooperative tone. - **Tit-for-Tat**: Mirror the
# corporation’s behavior to avoid being taken advantage of while promoting
# fairness. - **Final Push**: End strong to maximize project progress and secure
# a positive outcome.  ### Benefits: - **Flexibility**: The strategy adapts to
# the corporation’s resource allocation behavior, allowing you to conserve
# resources when necessary while pushing for maximum impact when conditions are
# favorable. - **Minimization of Risk**: By mirroring the corporation’s actions
# after the initial push, you reduce the risk of overcommitting while
# maintaining a cooperative stance. - **Reputation Management**: You appear
# committed and fair, which enhances your NGO’s public and stakeholder image,
# especially with the final heavy investment.  This strategy strikes a balance
# between maximizing project success and protecting your NGO’s resources,
# ensuring that you are not exploited while fostering a productive partnership.

# ### Iterated Game Strategy: "Tit-for-Tat with Early Cooperation"  1. **Round
# 1: Cooperate (C)**    - **Action**: Always cooperate in the first round.    -
# **Reason**: This sets a cooperative tone and encourages mutual investment.  2.
# **Round 2: Mirror Opponent's Previous Move**    - **If your opponent
# cooperated in Round 1**: Cooperate (C).    - **If your opponent defected in
# Round 1**: Defect (D).    - **Reason**: This establishes a pattern of
# reciprocity, rewarding cooperation and punishing defection.  3. **Rounds 3 to
# 999: Continue Mirroring Opponent's Previous Move**    - **If your opponent
# cooperated in the previous round**: Cooperate (C).    - **If your opponent
# defected in the previous round**: Defect (D).    - **Reason**: Maintain
# fairness and ensure that you are not exploited, while still offering
# opportunities for mutual cooperation.  4. **Round 1000: Cooperate (C)**    -
# **Action**: Always cooperate in the final round, regardless of the opponent’s
# previous action.    - **Reason**: End the game with cooperation to maximize
# the chance of a positive outcome and secure potential long-term benefits, such
# as reputation or future partnerships.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always cooperate
      if self.first_round():
          return axl.Action.C
      
      # Round 1000: Always cooperate
      if len(self.history) == 999:
          return axl.Action.C
      
      # Round 2: Mirror opponent's previous move
      if len(self.history) == 1:
          return opponent.history[-1]
      
      # Rounds 3 to 999: Continue mirroring opponent's previous move
      return opponent.history[-1]

# To maximize your overall research output while balancing cooperation and
# competition, you can adopt a **Tit-for-Tat** strategy with a cooperative bias.
# Here’s a high-level outline of this approach:  ### Week 1: Begin with
# Cooperation - **Openly share your improvements** in the first week. This sets
# the tone of collaboration and signals trust and willingness to cooperate. It
# also provides an opportunity to test your colleague’s intentions and
# preferences.  ### Following Weeks: Reciprocity with Cooperation Bias -
# **Observe your colleague's behavior.**   - If they **also share openly**,
# continue sharing in the following weeks. This leads to mutual gains and
# accelerates development for both teams.   - If they **keep their improvements
# confidential**, respond by keeping your findings confidential in the next
# week, signaling that you will not tolerate one-sided behavior.    ###
# Returning to Cooperation - If your colleague resumes sharing their findings
# after a period of withholding, you should **go back to cooperation** (i.e.,
# sharing your improvements) to re-establish trust. This cooperative bias helps
# avoid long-term deadlock and builds a positive feedback loop of collaboration.
# ### Strategy Overview: 1. **Start with cooperation** to build trust. 2.
# **Mirror their actions** in the following weeks. If they cooperate, continue
# cooperating. If they defect (withhold information), respond with withholding
# in the next round. 3. **Be forgiving**: If they return to cooperation after
# withholding information, resume sharing to maintain the possibility of mutual
# benefit.     ### Why This Works: - **Encourages cooperation**: By starting
# with openness, you encourage your colleague to adopt a similar cooperative
# stance. - **Punishes defection**: If your colleague tries to take advantage of
# you by withholding information, you respond by withholding too, protecting
# your competitive position. - **Restores cooperation**: By returning to
# openness after a defection, you avoid a negative spiral where both sides stop
# sharing entirely, which would hurt both designs in the long run.  This
# strategy balances the potential for mutual progress with protection against
# being exploited, ultimately helping both of you achieve better design outputs
# over the multi-week period.

# 1. **Start by playing C (Cooperate) in the first round.**  2. **For each
# subsequent round**:    - **If your opponent played C in the previous round**,
# play C (Cooperate).    - **If your opponent played D in the previous round**,
# play D (Defect) in the current round.  3. **If at any point your opponent
# returns to playing C after having played D**, forgive them and play C
# (Cooperate) in the next round.  4. **Continue the pattern** of reciprocating
# cooperation and defection throughout the game.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the opponent's last move
      opponent_last_move = opponent.history[-1]
  
      # If opponent played C in the last round, cooperate
      if opponent_last_move == axl.Action.C:
          return axl.Action.C
  
      # If opponent played D in the last round, defect
      if opponent_last_move == axl.Action.D:
          return axl.Action.D

# Given the nature of the collaboration, where trust and long-term outcomes are
# crucial, a balanced strategy is essential to maximize your research output
# while avoiding significant disadvantages. You can adopt a **Tit-for-Tat**
# strategy with some flexibility, which is simple, neutral, and adaptive to your
# colleague's behavior. Here's how it works:  ### 1. **Start by Sharing
# Openly**:    - In the first week, openly share your improvements. This sets a
# positive, collaborative tone and demonstrates a willingness to work together
# for mutual benefit. It encourages reciprocity from your colleague.  ### 2.
# **Mirror Your Colleague's Behavior**:    - In subsequent weeks, match your
# colleague's behavior from the previous week:      - **If they shared openly**,
# continue sharing openly as well. This keeps both of you progressing and
# fosters trust.      - **If they kept their findings confidential**, do the
# same in the next week. This protects you from being exploited and signals that
# trust needs to be rebuilt.  ### 3. **Introduce Occasional Forgiveness**
# (Optional):    - If your colleague keeps their findings confidential, you
# might occasionally (but not always) share openly again after a few rounds of
# mutual confidentiality. This shows you are still open to collaboration, which
# may encourage them to return to sharing. However, be cautious with this to
# avoid being consistently exploited.  ### 4. **Evaluate the Long-Term
# Relationship**:    - Periodically assess the overall balance of how the
# collaboration is going:      - If your colleague consistently reciprocates
# openness, continue with mutual sharing.      - If they lean towards keeping
# information confidential, you may need to adjust to a more guarded approach
# over time.  ### Summary of Strategy: - **Week 1**: Share openly. -
# **Subsequent Weeks**: Mirror your colleague's behavior from the previous week
# (sharing or keeping confidential). - Optionally, introduce occasional
# forgiveness to encourage collaboration if both of you have been keeping things
# confidential.  This strategy is neutral, adaptive, and fair, ensuring you
# aren't consistently at a disadvantage while promoting collaboration when
# possible.

# 1. **Round 1**: Play C (Cooperate).  2. **From Round 2 onwards**:    - **If
# your opponent played C in the previous round**, play C (Cooperate).    - **If
# your opponent played D in the previous round**, play D (Defect).  3.
# **Occasional Forgiveness**:    - After every 10 rounds, if both you and your
# opponent have been playing D for the last 5 consecutive rounds, play C
# (Cooperate) in the next round to test if the opponent is willing to return to
# cooperation.  4. **Repeat this strategy for all remaining rounds**.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always play C
      if self.first_round():
          return axl.Action.C
  
      # From Round 2 onwards:
      # If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          # Check for occasional forgiveness every 10 rounds
          if len(self.history) % 10 == 0:
              # Check if both players have been playing D for the last 5 rounds
              if self.history[-5:].count(axl.Action.D) == 5 and opponent.history[-5:].count(axl.Action.D) == 5:
                  return axl.Action.C  # Forgive and play C
          return axl.Action.D

# ### Aggressive Strategy: "Tit-for-Tat with Escalation"  The core of this
# aggressive strategy is to maximize your country’s advantage while discouraging
# your counterpart from exploiting free trade. The strategy balances calculated
# risk-taking with the threat of retaliation, ensuring that your counterpart is
# incentivized to cooperate or face escalating protectionist measures. Here’s
# how it works:  1. **Start with a Protectionist Stance (Round 1):**    - Begin
# negotiations by proposing a **protectionist policy** (e.g., tariffs or
# quotas). This signals strength and sets the tone that you are willing to
# defend your country’s industries.    - **Rationale:** By starting off with
# protectionism, you test your counterpart’s resolve. If they respond with free
# trade, you gain an early advantage. If they also choose protectionism, it’s
# still a manageable outcome early in the negotiations.  2. **Offer Conditional
# Free Trade in Round 2 (but with a Threat):**    - In the second round, offer
# **free trade**, but accompany it with a clear **warning**: If the counterpart
# responds with protectionism, you will escalate with harsher protectionist
# measures in the next round.    - **Rationale:** This signals a willingness to
# cooperate but also sets a clear boundary for retaliation. You give them a
# chance to establish mutual benefits, but they know there will be consequences
# for exploiting your offer.  3. **Escalate if Betrayed (Rounds 3+):**    - If
# your counterpart imposes protectionist measures while you offer free trade,
# **immediately retaliate** in the next round with **stronger protectionist
# policies** (e.g., higher tariffs or more restrictive quotas).    -
# **Rationale:** This punishes bad behavior and discourages them from exploiting
# your free trade offers in future rounds. By escalating the protectionism, you
# demonstrate that you are not a passive player and that their defection will
# come at a cost.  4. **Tit-for-Tat Approach Moving Forward:**    - After the
# initial two rounds, adopt a **tit-for-tat** approach:      - If they respond
# with free trade, you offer free trade in the next round.      - If they impose
# protectionist measures, you retaliate with equal or stronger protectionist
# policies.    - **Rationale:** This approach builds reciprocity. It rewards
# cooperation and punishes defection in a balanced manner, ensuring neither side
# can take full advantage without repercussions.  5. **Maintain Flexibility for
# Selective Concessions:**    - Throughout the negotiations, remain open to
# **selective concessions** in industries where mutual free trade benefits your
# country more than protectionism. However, only offer these concessions when:
# - Your counterpart has demonstrated consistent cooperation.      - You see a
# clear economic advantage in opening specific sectors.    - **Rationale:** This
# allows you to maximize long-term gains in key industries while maintaining a
# protectionist stance in areas where your country needs safeguarding.  6.
# **Final Round (Endgame Strategy):**    - In the final round, assess the
# overall balance of the negotiations. If you have gained more advantages than
# your counterpart, consider offering **free trade** to lock in benefits and
# maintain a positive future relationship.    - If you feel your counterpart has
# gained the upper hand in previous rounds, revert to **protectionism** as a
# defensive measure to protect your industries.    - **Rationale:** The endgame
# should reflect your overall performance in the negotiations. If you’re ahead,
# secure stability. If you’re behind, defend your economic interests.  ---  ###
# Summary of the Strategy:  1. **Round 1:** Start with protectionism to assert
# an aggressive stance. 2. **Round 2:** Offer free trade, but with a clear
# threat of retaliation if betrayed. 3. **Round 3+:** Escalate protectionism if
# they defect, otherwise reward cooperation with free trade (tit-for-tat). 4.
# **Selective Concessions:** Offer free trade in specific sectors only if it
# benefits your country. 5. **Endgame:** Secure gains or defend your position
# based on the overall negotiation outcome.  This strategy aims to maximize your
# country’s economic advantage while maintaining enough flexibility to adapt to
# your counterpart’s moves. By starting aggressively, retaliating when
# necessary, and rewarding cooperation when appropriate, you create a dynamic
# where your counterpart is forced to consider the cost of defection carefully.

# 1. **Round 1: Defect (D).**      Start with defection to establish a strong
# stance.  2. **Round 2: Cooperate (C) if your opponent cooperated in Round 1;
# otherwise, Defect (D) again.**      Offer cooperation if the opponent showed
# willingness to cooperate in the first round, but if they defected, continue
# with defection.  3. **Round 3 and onward:**    - **If your opponent cooperated
# in the previous round, Cooperate (C).**    - **If your opponent defected in
# the previous round, Defect (D).**    Use a tit-for-tat approach: mirror your
# opponent’s previous move. Cooperate if they cooperated, defect if they
# defected.  4. **Escalation: If your opponent defects twice consecutively,
# Defect (D) for the next two rounds, even if they cooperate afterward.**
# Punish sustained defection with escalated defection, signaling that repeated
# defection will result in harsher retaliation.  5. **Selective forgiveness: If
# your opponent cooperates after you escalated, return to tit-for-tat (C for C,
# D for D).**      After punishing sustained defection, be willing to return to
# a cooperative strategy if your opponent shows signs of cooperation again.  6.
# **Final rounds (Round 950 onward): Cooperate (C) if both sides have cooperated
# for the majority of the game; otherwise, Defect (D).**      In the final
# phase, assess the overall history of the game. If cooperation has been the
# dominant strategy, continue cooperating to secure mutual gains. If defection
# has been frequent, defect to protect your interests.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Defect
      if self.first_round():
          self.escalation_counter = 0  # Initialize escalation counter
          return axl.Action.D
  
      # Round 2: Cooperate if opponent cooperated in Round 1, otherwise Defect
      if len(self.history) == 1:
          return axl.Action.C if opponent.history[0] == axl.Action.C else axl.Action.D
  
      # Escalation logic: If opponent defected twice consecutively, escalate defection
      if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.escalation_counter = 2  # Set escalation for the next two rounds
  
      # If escalation is active, defect for the next two rounds
      if self.escalation_counter > 0:
          self.escalation_counter -= 1
          return axl.Action.D
  
      # Tit-for-tat: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D
  
      # Final rounds: From round 950 onward, cooperate if majority cooperation, else defect
      if len(self.history) >= 950:
          if self.history.cooperations > self.history.defections:
              return axl.Action.C
          else:
              return axl.Action.D

# To maximize your NGO's impact while balancing resource conservation in
# collaboration with the corporation, a **cooperative tit-for-tat strategy with
# communication** could be highly effective. Here's a high-level,
# straightforward approach:  ### 1. **Start with Cooperation:**    - On **Day
# 1**, invest heavily in the project to signal goodwill and cooperation. This
# sets a positive tone and demonstrates that your NGO is committed to the
# project’s success.     ### 2. **Open Communication & Clarify Goals:**      -
# After Day 1, **initiate open communication** with the corporation. Express
# your shared vision for the project, emphasizing the mutual benefits of
# collaboration and the importance of both parties investing wisely. Encourage a
# discussion about fair resource allocation to avoid one-sided contributions.
# - Establish a **shared goal** (e.g., achieving a certain milestone by the end
# of the project) and suggest alternating lighter investment days to ensure both
# parties conserve resources in the long run while still driving meaningful
# progress.  ### 3. **Mirror the Corporation’s Actions:**    - On subsequent
# days, **match the corporation’s investment behavior**:      - If the
# corporation invests heavily, continue to invest heavily on the next day.
# - If the corporation conserves resources, also conserve your resources the
# following day, avoiding depletion of your funds while signaling that mutual
# investment is required for significant progress.     ### 4. **Occasional
# Leadership Moves:**    - **Periodically lead by example** by investing
# heavily, even if the corporation conserves resources for a day or two. This
# encourages them to reciprocate and signals that your NGO is still committed to
# the project’s success.    - However, limit this to avoid over-extending your
# resources.  ### 5. **Encourage Regular Check-ins:**    - Propose regular
# **check-ins** (daily or every couple of days) to review progress and adjust
# strategies. During these check-ins, assess whether the corporation is willing
# to increase its commitment. If they are, reciprocate. If they are scaling
# back, adjust accordingly to avoid unnecessary resource strain on your NGO.
# ### 6. **Adapt Based on the Corporation’s Approach:**    - If the corporation
# consistently invests heavily, you can occasionally conserve your resources
# while still maintaining progress.    - If the corporation consistently
# conserves resources, engage in direct conversation, reminding them of the
# shared objectives and the need for mutual investment to achieve the desired
# results.  ### 7. **Exit Strategy:**    - If the corporation is uncooperative
# and consistently conserves resources while your NGO is investing heavily,
# **scale back your investment gradually** to avoid depleting your funds. Make
# it clear that without mutual effort, the project’s success will be
# compromised, and consider renegotiating terms.  ### Key Considerations:    -
# **Trust-Building**: Start with goodwill and cooperation to foster trust and
# encourage the corporation to reciprocate.    - **Fairness**: Ensure the
# corporation understands that both parties need to carry their weight to
# achieve the project’s goals.    - **Adaptability**: Be flexible and responsive
# to the corporation’s behavior, using communication to guide the partnership
# toward a more balanced and sustainable resource allocation.  ### Summary of
# Strategy: 1. **Day 1**: Invest heavily to signal cooperation. 2. **Ongoing**:
# Mirror the corporation’s actions (invest if they invest, conserve if they
# conserve). 3. **Regular Communication**: Keep discussions open to align goals
# and resource allocation. 4. **Lead periodically**: Occasionally take the lead
# with heavy investment to encourage reciprocity. 5. **Pivot if necessary**:
# Scale back if the corporation is uncooperative.  This strategy maximizes your
# NGO’s impact while safeguarding against disproportionate resource depletion
# and fostering a cooperative, long-term relationship with the corporation.

# ### Iterated Game Strategy for 1000 Rounds:  1. **First Round**:     - Play
# **C** (Cooperate) to signal a willingness to collaborate and establish a
# foundation of trust.  2. **Subsequent Rounds**:    - **Mirror the opponent's
# previous move**:      - If the opponent played **C** in the last round, play
# **C**.      - If the opponent played **D** in the last round, play **D**.  3.
# **Occasional Leadership (Every 50 Rounds)**:    - Every 50th round (i.e.,
# rounds 50, 100, 150, etc.), regardless of the opponent’s previous move, play
# **C** (Cooperate), even if the opponent played **D** in the previous round.
# This shows a willingness to reinvest in cooperation and encourages
# reciprocity.  4. **Adaptation for Extended Defection**:    - If the opponent
# defects by playing **D** for **5 consecutive rounds**, switch to **D** until
# the opponent plays **C** again. Once they return to **C**, resume the
# mirroring strategy.  5. **Endgame Consideration (Final 10 Rounds)**:    - In
# the last 10 rounds (rounds 991-1000), play **C** only if the opponent played
# **C** in the previous round. If the opponent plays **D** at any point in these
# rounds, continue playing **D** for the remainder of the game.  ### Summary of
# the Strategy: - **Start with C** to establish cooperation. - **Mirror the
# opponent's previous move** to encourage mutual cooperation or respond to
# defection. - **Lead periodically with C** every 50 rounds to encourage
# returning to cooperation. - **Defect after 5 consecutive defections by the
# opponent**, but be ready to cooperate again if they return to C. - **In the
# final 10 rounds**, only cooperate if the opponent cooperates.  This strategy
# balances cooperation and self-protection while encouraging the opponent to
# maintain mutual investment in the project's success.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Check for the final 10 rounds (rounds 991-1000)
      if round_number > 990:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Check if the opponent has defected for 5 consecutive rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          # Defect until the opponent cooperates again
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Every 50th round, cooperate regardless of the opponent's last move
      if round_number % 50 == 0:
          return axl.Action.C
  
      # Mirror the opponent's previous move
      return opponent.history[-1]

# To navigate these negotiations effectively, I would adopt a **Tit-for-Tat with
# Cooperation** strategy, which balances assertiveness and cooperation. This
# strategy is simple, reactive, and aims to foster mutual trust over time while
# protecting my country's interests.  ### Key Elements of the Strategy:  1.
# **Start with Cooperation (Free Trade Proposal):**    - In the first round,
# offer a free trade agreement. This signals goodwill and a willingness to
# collaborate for mutual benefit. It sets a positive tone and invites a
# reciprocal gesture from the counterpart.  2. **Mirror the Counterpart's
# Actions:**    - In subsequent rounds, **reciprocate** the counterpart's
# previous action:      - If they propose free trade in a round, continue
# offering free trade in the next.      - If they impose a protectionist policy
# (tariffs or quotas), respond by proposing protectionist measures in the
# following round.  3. **Incorporate Occasional Cooperation (Forgiveness
# Mechanism):**    - If there is a series of mutual protectionism (i.e., several
# rounds where both countries impose tariffs), **occasionally offer free trade
# again** after a few rounds. This signals openness to re-establish cooperation
# and breaks the cycle of retaliatory protectionism, which could harm both
# economies in the long run.  4. **Maintain Flexibility and Observe Patterns:**
# - Continuously monitor the other nation’s strategy. If they seem locked into a
# protectionist stance, adjust by remaining defensive (protectionist) to
# safeguard national interests.    - If the counterpart shows a clear preference
# for mutual cooperation (free trade), maintain a cooperative approach to
# maximize mutual benefits.  ### Why This Strategy Works:  - **Encourages
# Cooperation:** By starting with free trade and responding based on the
# counterpart’s actions, this strategy encourages a cooperative dynamic. It
# creates an incentive for both sides to avoid prolonged protectionism.    -
# **Retaliates Against Exploitation:** If the counterpart attempts to exploit my
# country by imposing protectionist measures while we offer free trade, the Tit-
# for-Tat approach ensures that we retaliate quickly, preventing long-term
# economic disadvantage.  - **Offers a Path to Rebuild Trust:** By occasionally
# proposing free trade even after periods of protectionism, this strategy keeps
# the door open for renewed cooperation, preventing permanent breakdowns in
# negotiations.  - **Simple and Predictable:** The strategy is transparent and
# easy to follow. It avoids unnecessary complexity, reducing the likelihood of
# misunderstandings, and helps build a stable, long-term relationship based on
# mutual respect and reciprocity.  This approach maximizes the chances of
# reaching mutually beneficial outcomes while protecting my country's interests
# if the counterpart pursues a more self-serving strategy.

# **Iterated Game Strategy:**  1. **First Move:**    - In the first round,
# **Cooperate (C)**.  2. **Subsequent Moves:**    - For each subsequent round:
# - If your opponent **Cooperated (C)** in the previous round, **Cooperate
# (C)**.      - If your opponent **Defected (D)** in the previous round,
# **Defect (D)** in the current round.  3. **Occasional Forgiveness:**    - If
# you and your opponent have both **Defected (D)** for the last 5 consecutive
# rounds, **Cooperate (C)** in the next round.  4. **Continue Playing:**    -
# Repeat this pattern until the end of the 1000 rounds.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First move: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Check if both players have defected for the last 5 rounds
      if len(self.history) >= 5 and all(move == axl.Action.D for move in self.history[-5:]) and all(move == axl.Action.D for move in opponent.history[-5:]):
          return axl.Action.C
  
      # If opponent cooperated in the last round, cooperate
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If opponent defected in the last round, defect
      return axl.Action.D

# To navigate this high-stakes mediation process effectively, the strategy needs
# to balance assertiveness with pragmatism, maximizing the leverage we can
# generate while leaving enough room for adaptability. The goal is to maintain a
# dominant position, but without alienating the arbitrators or undermining
# future negotiation opportunities. Here’s a structured, aggressive yet
# calculated strategy:  ### 1. **Set the Tone Early – Controlled Aggression**
# - **Objective**: Establish dominance from the outset, framing the narrative in
# our favor.    - **Approach**: In the initial sessions, present a strong, well-
# substantiated argument that highlights the legal and factual weaknesses of the
# opposing party’s position. This should be done with confidence but not
# hostility. By anchoring the discussion around our interpretation of the
# contract, we can force the rival company to react to our narrative rather than
# setting their own.    - **Rationale**: Early aggression signals that we are
# prepared to fight for our interests but also leaves room for future
# conciliation if the pressure compels our opponent to reassess their stance.
# ### 2. **Strategic Use of Conciliatory Proposals – Conditional Concessions**
# - **Objective**: Appear reasonable to the arbitrators while maintaining
# leverage.    - **Approach**: Periodically offer conciliatory proposals, but
# make them conditional on substantial concessions from the other side. For
# example, propose mutually beneficial terms but tie them to key points that
# secure our strategic interests. This could include provisions that provide us
# with long-term advantages, such as favorable interpretation of particular
# clauses or limitations on future liabilities.    - **Rationale**: By framing
# these proposals as reasonable compromises, we can appeal to the arbitrators’
# desire for resolution while still keeping the opponent on the defensive. It
# also positions us as the more responsible party in the eyes of the
# arbitrators, which may be crucial in fostering their support.  ### 3.
# **Escalation Control – Aggressive Retaliation Only When Necessary**    -
# **Objective**: Maintain the upper hand without unnecessarily escalating
# tensions.    - **Approach**: If the opposing party presents aggressive
# arguments, retaliate swiftly by dismantling their claims with facts,
# precedents, and authoritative interpretations without resorting to emotional
# appeals or over-escalation. This ensures that we remain assertive and
# calculated, but not perceived as overly combative.    - **Rationale**: Over-
# escalation can harm our relationship with the arbitrators and prolong the
# process. By retaliating only when necessary, we keep the opponent aware that
# aggression will be met with a strong response, but we also telegraph that we
# are still open to reasonable solutions.  ### 4. **Psychological Pressure – Use
# of Deadlines and Milestones**    - **Objective**: Create a sense of urgency
# and pressure the opponent into making errors or concessions.    -
# **Approach**: Impose artificial deadlines or make strategic use of real ones
# (such as key contract timelines or upcoming financial reporting periods).
# Subtly remind the opposing party that prolonging the dispute can have
# significant financial or operational consequences for them. Use these
# milestones to push for resolutions on key issues before the arbitrators.    -
# **Rationale**: Psychologically, deadlines can force the other side to rush
# decisions, increasing the likelihood of mistakes or premature concessions. We
# can exploit this dynamic to gain more favorable terms without appearing overly
# aggressive.  ### 5. **Information Asymmetry – Control the Flow of
# Information**    - **Objective**: Maintain strategic control over the
# situation by selectively revealing information.    - **Approach**: Throughout
# the mediation, we should strategically release key bits of information that
# support our position while withholding certain details to keep the opponent
# uncertain about our full strategy. For example, we can reveal certain
# favorable evidence gradually, ensuring it maximizes its impact at key moments
# in the process.    - **Rationale**: By controlling the flow of information, we
# can maintain a psychological edge, keeping the other side uncertain about our
# full capabilities or intentions. This uncertainty may lead them to adopt a
# more conciliatory stance out of caution.  ### 6. **Maintain Flexibility –
# Adaptive Aggression Based on Opponent’s Moves**    - **Objective**: Stay
# adaptable while maintaining an aggressive posture.    - **Approach**:
# Continuously assess the opponent’s strategies and adjust our aggression level
# accordingly. If the opponent becomes overly conciliatory, we can press harder,
# pushing for more favorable terms. If they adopt a highly aggressive stance, we
# can respond proportionately but always leave room for a pivot to conciliatory
# proposals that appeal to the arbitrators.    - **Rationale**: Overly rigid
# aggression can backfire if the opponent shifts tactics or the arbitrators
# become fatigued by constant conflict. Flexibility allows us to adjust our
# approach and position ourselves as both assertive and reasonable, depending on
# the evolving dynamics of the mediation.  ### 7. **End-Game Strategy –
# Contingency Plans and Final Push**    - **Objective**: Ensure we are prepared
# for the final stages of mediation with a clear path to resolution, whether
# through settlement or arbitration.    - **Approach**: As the mediation reaches
# its later stages, focus on securing final concessions while preparing for
# potential arbitration. If a settlement seems imminent, push for last-minute
# terms that secure long-term advantages. If arbitration seems inevitable,
# ensure we have meticulously built a strong record of facts and legal arguments
# to support our case.    - **Rationale**: The final stages of mediation are
# often where the most significant concessions are made. By preparing for both
# settlement and arbitration, we ensure we are in a position of strength,
# regardless of the outcome.  ### Key Considerations: - **Balance Public
# Perception**: Since this is a high-stakes, potentially public dispute, our
# strategy must also be mindful of public relations. Over-aggressiveness that
# appears unreasonable could harm our reputation. The aggressive stance should
# always be framed as protecting legitimate interests. - **Appeal to
# Arbitrators’ Interests**: Throughout, we should subtly appeal to the
# arbitrators’ desire for efficiency and resolution. A party that is seen as
# both assertive and reasonable will likely gain favor over one that is seen as
# overly combative or obstructionist. - **Avoid Overplaying Aggression**: There
# is a fine line between aggressive and unreasonable. We should be careful not
# to cross into the latter, as it could alienate the arbitrators and force them
# to sympathize with the opposing party.  ### Conclusion This strategy provides
# a framework for maintaining an aggressive posture while allowing for
# adaptability as the mediation evolves. By striking a balance between
# assertiveness and conciliation, and by controlling the flow of the mediation
# process, we can craft a narrative that favors our corporation while
# positioning ourselves strategically for either a favorable settlement or a
# strong arbitration outcome.

# ### Iterated Game Strategy:  1. **Set the Tone Early – Controlled Aggression**
# - **First Round:** Play **D** (Defect).    - **Rationale**: Establish
# dominance by signaling that you are willing to play aggressively. This sets
# the expectation that you will not be easily taken advantage of.  2. **Tit-for-
# Tat with Gradual Forgiveness**      - **In subsequent rounds:**        - If
# your opponent plays **C** (Cooperate) in the previous round, play **C** in the
# next round (reward cooperation).        - If your opponent plays **D**
# (Defect) in the previous round, play **D** in the next round (retaliate).
# - **Rationale**: This creates a balance where you match their behavior,
# signaling that you are willing to cooperate but will punish aggression with
# equal aggression.  3. **Strategic Conciliation – Conditional Cooperation**
# - **Every 5th round** (if previous rounds have been mutual defection or mixed
# play):        - Play **C** (Cooperate) regardless of the opponent’s previous
# move.        - If your opponent reciprocates with **C** in this round,
# continue playing **C** in subsequent rounds until they defect again.        -
# If your opponent responds with **D**, immediately return to playing **D** in
# the next round.      - **Rationale**: This signals a willingness to cooperate,
# offering a pathway toward mutual benefit, but only if the opponent
# reciprocates. It also helps break cycles of mutual defection.  4. **Escalation
# Control – Proportional Retaliation**      - If the opponent initiates a string
# of consecutive **D** (Defect) plays (more than 3 consecutive rounds), continue
# playing **D** but inject a **C** every 4th round.      - **Rationale**: This
# prevents full escalation and signals that while you’re willing to fight, you
# are still open to cooperation if they reconsider their approach.  5.
# **Psychological Pressure – Use of Deadlines**      - **From round 950
# onwards**:        - If the opponent has played **C** consistently in the last
# 10 rounds, continue playing **C** until the end.        - If the opponent
# plays **D** in any of these rounds, switch to **D** for the remainder of the
# game.      - **Rationale**: As the game nears its end, incentivizing
# cooperation in the final rounds can maximize your score. However, any late-
# game defection should be punished to prevent last-minute exploitation.  6.
# **Maintain Flexibility – Adapt Based on Behavior**      - Periodically assess
# the opponent's overall strategy. If they appear to be consistently
# cooperative, shift toward longer stretches of **C**.      - If they are
# erratic or consistently aggressive, maintain a predominantly **D** strategy
# with the occasional **C** to test for potential shifts.      - **Rationale**:
# Flexibility ensures you can adapt to varying strategies, maximizing your
# outcomes whether the opponent leans toward cooperation or aggression.  7.
# **End-Game Strategy – Push for Cooperation, Punish Defection**      - **Rounds
# 990-1000**:        - If the opponent has been mostly cooperative, play **C**
# in all remaining rounds.        - If the opponent has been mostly aggressive,
# play **D** in all remaining rounds.      - **Rationale**: In the final rounds,
# there is less incentive for the opponent to maintain cooperation if they
# suspect you may defect. Lock in your strategy based on their prior behavior to
# secure the best possible score.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: Play D (Defect)
      if self.first_round():
          return axl.Action.D
  
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 950
  
      # Helper function to check if we are in the last 10 rounds (990-1000)
      def in_final_rounds():
          return len(self.history) >= 990
  
      # Helper function to check if the opponent has been cooperative in the last N rounds
      def opponent_cooperative_in_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D) == 0
  
      # Helper function to check if the opponent has been mostly cooperative
      def opponent_mostly_cooperative():
          return opponent.history.cooperations > opponent.history.defections
  
      # Helper function to check if the opponent has been mostly aggressive
      def opponent_mostly_aggressive():
          return opponent.history.defections > opponent.history.cooperations
  
      # Escalation control: If opponent has played more than 3 consecutive D's, inject a C every 4th round
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          if len(self.history) % 4 == 0:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Tit-for-Tat with Gradual Forgiveness: Mirror opponent's last move
      if len(self.history) % 5 == 0:
          # Strategic Conciliation: Every 5th round, play C regardless of opponent's previous move
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.C
      else:
          # Tit-for-Tat: Mirror opponent's last move
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Psychological Pressure: From round 950 onwards, cooperate if opponent has been cooperative in the last 10 rounds
      if in_last_10_rounds():
          if opponent_cooperative_in_last_n_rounds(10):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # End-Game Strategy: In the final rounds (990-1000), push for cooperation or punish defection
      if in_final_rounds():
          if opponent_mostly_cooperative():
              return axl.Action.C
          else:
              return axl.Action.D

# ### Strategy Overview: **Collaborative Pragmatism with Tactical Flexibility**
# In a high-stakes mediation process, the goal is to balance assertiveness with
# cooperation, ensuring that our corporation remains flexible enough to respond
# to our opponent’s moves while maintaining a position of strength. The strategy
# I propose is centered around a **Collaborative Pragmatism** approach, which
# combines cooperative gestures with tactical assertiveness. This strategy will
# allow us to navigate each session with the intention of maximizing favorable
# outcomes while minimizing unnecessary escalation.  ### Key Components of the
# Strategy  1. **Early Assessment and Rapport Building:**    - **Objective:** In
# the initial sessions, prioritize gathering intelligence on the opponent’s
# strategy, demeanor, and openness to compromise.    - **Tactic:** Start the
# mediation process with a **moderately conciliatory proposal**. This will
# create an impression of good faith and cooperation, encouraging the opponent
# to reciprocate. Simultaneously, this approach allows us to build rapport with
# the arbitrators and gain insight into the opponent’s strategy.    -
# **Rationale:** A conciliatory opening can test the waters without committing
# to a weaker position. If the opponent responds aggressively, we can pivot
# accordingly. If they reciprocate with conciliation, this sets the stage for
# potential collaboration.  2. **Conditioned Cooperation:**    - **Objective:**
# Use cooperation as a conditional tool, offering conciliatory proposals only
# when there are signs of reciprocity from the other side.    - **Tactic:** If
# the opponent presents a conciliatory proposal after our initial offer, we
# continue the collaborative approach, proposing further mutually beneficial
# solutions. However, always ensure that our proposals are structured such that
# they benefit us slightly more, thereby subtly steering the negotiation in our
# favor.    - **Rationale:** This creates a cooperative atmosphere but ensures
# that we maintain a competitive edge. By positioning ourselves as reasonable
# yet shrewd, we might nudge the arbitrators toward favoring our proposals.  3.
# **Strategic Aggression when Necessary:**    - **Objective:** Use aggressive
# arguments selectively and tactically to keep the opponent off balance and
# prevent them from becoming too comfortable.    - **Tactic:** If the opponent
# adopts an aggressive stance, immediately respond with an **equally aggressive
# counterargument** in the next session. This demonstrates that we will not be
# passive or weak, and it prevents the opponent from gaining the upper hand.
# However, avoid sustained aggression; after a strong rebuttal, return to a more
# conciliatory tone in subsequent sessions to signal that we are still open to
# compromise.    - **Rationale:** A measured aggressive response will signal
# strength and prevent the opponent from exploiting our goodwill. However,
# pulling back from aggression when tensions rise will help de-escalate the
# situation and avoid a prolonged deadlock.  4. **Mirror and Lead:**    -
# **Objective:** Mirror the opponent’s approach when advantageous, but subtly
# lead the negotiation toward outcomes favorable to us.    - **Tactic:** If both
# parties have settled into a pattern of conciliation, gradually introduce more
# substantive proposals that benefit us while still appearing reasonable. If the
# opponent shifts back to aggression, mirror their aggressiveness, but always
# with a focus on returning to cooperation as soon as possible.    -
# **Rationale:** By mirroring the opponent’s moves, we maintain flexibility and
# avoid being caught off-guard. However, by subtly leading the discussions
# toward our desired outcomes, we can guide the mediation process in a direction
# that increasingly favors our corporation.  5. **Stakeholder Alignment and
# Arbitrator Perception Management:**    - **Objective:** Ensure that the
# arbitrators view our corporation as the more constructive and reasonable party
# while subtly advancing our interests.    - **Tactic:** Throughout the
# mediation, emphasize our corporation’s commitment to a fair and balanced
# resolution. Use language that positions us as the party more willing to
# compromise without appearing weak. Additionally, present data, precedents, and
# legal arguments that reinforce the fairness and reasonableness of our
# proposals, even when we are advocating for our own interests.    -
# **Rationale:** Arbitrators are more likely to favor the party that
# demonstrates a willingness to collaborate while also presenting well-
# supported, balanced arguments. This will help tilt neutral arbitrators in our
# favor over time, building a cumulative advantage as the sessions progress.  6.
# **Adaptability and Real-Time Calculation:**    - **Objective:** Continuously
# reassess the opponent’s behavior and adjust our strategy accordingly.    -
# **Tactic:** After each session, debrief with the legal team and analyze the
# opponent’s latest moves. If they are becoming increasingly conciliatory, we
# can push for more favorable terms while maintaining the collaborative
# atmosphere. However, if they become aggressive or unpredictable, be prepared
# to pivot with assertiveness as necessary.    - **Rationale:** Maintaining
# flexibility is essential in a lengthy mediation. By adapting to the opponent’s
# evolving strategy, we can avoid being trapped in a rigid approach while
# continuing to press for an optimal resolution.  ### Strategic Phases:  1.
# **Phase 1: Initial Sessions (Information Gathering and Setting the Tone):**
# - Present a moderately conciliatory proposal.    - Build rapport with the
# arbitrators and assess the opponent’s strategy.    - Mirror conciliation if
# reciprocated; prepare for tactical aggression if the opponent is overly
# assertive.  2. **Phase 2: Tactical Engagement (Conditioned Cooperation and
# Strategic Aggression):**    - Shift between conciliation and aggression based
# on the opponent’s moves.    - Introduce proposals that subtly favor our
# corporation.    - Keep the arbitrators focused on our reasonable, well-
# supported positions.  3. **Phase 3: Closing Sessions (Maximizing Favorable
# Outcomes):**    - Push for proposals that lock in our advantages while
# maintaining a collaborative tone.    - Use any aggressive moves by the
# opponent to highlight our reasonableness to the arbitrators.    - Seek to
# conclude the mediation with a deal that is either explicitly in our favor or
# at least one that leaves us in a stronger position than we began.  ###
# Conclusion:  By adopting this **Collaborative Pragmatism with Tactical
# Flexibility** strategy, we can navigate the lengthy mediation process
# effectively, positioning our corporation favorably in the eyes of the
# arbitrators while remaining adaptable to the opponent’s tactics. This approach
# allows us to maintain a balance between assertiveness and cooperation,
# ensuring that we can maximize favorable outcomes without escalating the
# dispute unnecessarily.

# ### Strategy for the Iterated Normal-Form Game:  1. **Opening Move:**     - In
# the first round, **play C** (Cooperate). This sets a tone of cooperation and
# tests the opponent’s initial strategy.  2. **Tit-for-Tat with a Bias for
# Cooperation:**    - For subsequent rounds, **mirror your opponent’s last
# move**:      - If your opponent played C in the previous round, **play C**
# (Cooperate) in the next round.      - If your opponent played D in the
# previous round, **play D** (Defect) in the next round.  3. **Forgiveness
# Mechanism to Prevent Escalation:**    - If both you and your opponent have
# played D (Defect) for **two consecutive rounds**, **shift back to C**
# (Cooperate) in the following round, regardless of what the opponent does. This
# resets the potential for cooperation and de-escalates tension.  4.
# **Occasional Defection for Tactical Advantage:**    - Every **50th round**,
# regardless of the opponent’s previous move, **play D** (Defect). This
# introduces an element of assertiveness, keeps the opponent from becoming
# complacent, and ensures that you can capitalize on potential cooperative
# patterns without appearing overly passive.  5. **Endgame Strategy:**    - In
# the last 10 rounds (rounds 991–1000), **play D** (Defect) consistently. As
# cooperation is less valuable near the end of the game, this ensures that you
# maximize your final scores without the risk of retaliation diminishing long-
# term gains.  ---  This strategy balances cooperation with strategic defection,
# fostering a cooperative dynamic while ensuring you do not fall into a
# persistently passive role. It also includes mechanisms for de-escalation and a
# calculated endgame phase to maximize overall payoffs.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Opening move: Cooperate in the first round
      if self.first_round():
          return axl.Action.C
  
      # Endgame strategy: Defect in the last 10 rounds
      if len(self.history) >= 991:
          return axl.Action.D
  
      # Occasional defection every 50th round
      if len(self.history) % 50 == 0:
          return axl.Action.D
  
      # Tit-for-Tat: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.D:
          # Forgiveness mechanism: If both defected in the last two rounds, cooperate
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D

# Given the dynamics of this multi-day sustainability project, where cooperation
# and resource management are key, your strategy needs to balance maximizing
# project progress with conserving your NGO's resources.  ### High-Level
# Strategy: **"Tit for Tat with Occasional Leadership"**  This strategy is
# designed to encourage collaboration, prevent exploitation of your resources,
# and foster mutual trust over time, while allowing for occasional leadership to
# steer the corporation towards more significant investments.  ### Key
# Principles:  1. **Start with Cooperation**:     - On the first day, **invest
# heavily**. This signals your commitment to the project and sets a cooperative
# tone. It encourages the corporation to also invest heavily, establishing a
# foundation of mutual contribution.  2. **Mirror the Corporation’s Behavior**:
# - After the first day, **match the corporation's behavior** from the previous
# day.       - If the corporation invests heavily, you also invest heavily the
# next day.      - If the corporation conserves resources, you conserve
# resources the following day.    - This creates a dynamic where the corporation
# understands that mutual investment leads to progress, while conserving
# resources will result in stagnation.  3. **Occasional Leadership Moves**:    -
# Every **3-4 days**, regardless of the corporation’s behavior, **invest
# heavily** to signal leadership and a commitment to the project's success. This
# can help reset any unproductive patterns (such as both parties conserving
# resources) and encourage the corporation to reinvest in the project.    - The
# goal is to remind the corporation that heavy investment is necessary for
# substantial project advancement and that your NGO is willing to take
# initiative.  4. **Communicate Openly**:    - Throughout the project, maintain
# **open communication** with the corporation, reinforcing the message that the
# best outcomes are achieved through mutual investment. Regular check-ins or
# updates on the project's progress can help foster a sense of shared
# responsibility.  5. **Adapt to Emerging Patterns**:    - If the corporation
# consistently invests heavily, consider conserving resources slightly more
# often, but without creating a pattern that could lead to exploitation.    - If
# you notice the corporation frequently conserving resources, consider adjusting
# your strategy to conserve more and hold discussions to realign expectations.
# ### Day-by-Day Breakdown:  1. **Day 1**: Invest heavily. 2. **Day 2**: Mirror
# the corporation's behavior from Day 1. 3. **Day 3**: Continue mirroring the
# corporation's behavior. 4. **Day 4**: Take a leadership step by investing
# heavily, regardless of the corporation's behavior on Day 3. 5. **Day 5 and
# beyond**: Continue this cycle of mirroring their behavior, with intermittent
# leadership moves every 3-4 days.  ### Benefits of This Strategy:  -
# **Encourages cooperation**: By mirroring the corporation's actions, you foster
# an environment of mutual respect and cooperation. - **Prevents exploitation**:
# The corporation is less likely to conserve resources while you invest heavily,
# knowing that you will match their behavior the next day. - **Demonstrates
# leadership**: Occasional leadership moves show that your NGO is committed to
# the project’s success and willing to take initiative when necessary. -
# **Conserves resources**: By only investing heavily when necessary, you
# conserve your NGO’s resources while still contributing to significant project
# progress.  By following this strategy, you maximize the potential for project
# success while safeguarding your NGO’s resources and fostering a productive,
# collaborative relationship with the corporation.

# 1. **Start by Cooperating**:      In the first round, play **C**.  2. **Mirror
# Opponent's Previous Move**:      For each subsequent round, play the **same
# move** your opponent played in the previous round.      - If your opponent
# played **C** in the previous round, play **C**.    - If your opponent played
# **D** in the previous round, play **D**.  3. **Occasionally Lead with
# Cooperation**:      Every **fourth round**, regardless of your opponent's
# previous move, play **C**.      This resets the dynamic and encourages further
# cooperation.  Repeat these steps for all 1000 rounds.

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
          return axl.Action.C
      
      # Every fourth round: Cooperate
      if len(self.history) % 4 == 0:
          return axl.Action.C
      
      # Mirror opponent's previous move
      return opponent.history[-1]


Aggressive_ranks = [
'Aggressive_4',
'Aggressive_23',
'Aggressive_13',
'Aggressive_1',
'Aggressive_19',
'Aggressive_14',
'Aggressive_11',
'Aggressive_12',
'Aggressive_25',
'Aggressive_18',
'Aggressive_24',
'Aggressive_2',
'Aggressive_17',
'Aggressive_3',
'Aggressive_15',
'Aggressive_22',
'Aggressive_6',
'Aggressive_21',
'Aggressive_20',
'Aggressive_10',
'Aggressive_7',
'Aggressive_5',
'Aggressive_8',
'Aggressive_16',
'Aggressive_9',
]

Cooperative_ranks = [
'Cooperative_9',
'Cooperative_24',
'Cooperative_4',
'Cooperative_2',
'Cooperative_7',
'Cooperative_12',
'Cooperative_23',
'Cooperative_22',
'Cooperative_17',
'Cooperative_1',
'Cooperative_21',
'Cooperative_6',
'Cooperative_11',
'Cooperative_3',
'Cooperative_5',
'Cooperative_19',
'Cooperative_15',
'Cooperative_10',
'Cooperative_20',
'Cooperative_13',
'Cooperative_8',
'Cooperative_25',
'Cooperative_16',
'Cooperative_18',
'Cooperative_14',
]

Neutral_ranks = [
'Neutral_1',
'Neutral_19',
'Neutral_9',
'Neutral_8',
'Neutral_5',
'Neutral_17',
'Neutral_21',
'Neutral_2',
'Neutral_23',
'Neutral_24',
'Neutral_3',
'Neutral_6',
'Neutral_18',
'Neutral_7',
'Neutral_12',
'Neutral_4',
'Neutral_25',
'Neutral_14',
'Neutral_16',
'Neutral_15',
'Neutral_13',
'Neutral_11',
'Neutral_22',
'Neutral_10',
'Neutral_20',
]