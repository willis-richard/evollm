import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# To develop an effective strategy for this lengthy-session mediation process, I
# would recommend a sophisticated approach based on the principles of
# conditional cooperation and strategic flexibility. This strategy, which we can
# call "Adaptive Conciliation," aims to position our corporation favorably while
# remaining responsive to our opponent's tactics. Here's the outline:  1.
# Initial Cooperative Stance: Begin the mediation process with a conciliatory
# proposal. This sets a collaborative tone and demonstrates our willingness to
# find a mutually beneficial solution. It also allows us to gauge our opponent's
# initial approach.  2. Tit-for-Tat with Forgiveness: After the initial
# conciliatory move, mirror the opponent's most recent action. If they respond
# with aggression, we respond with an aggressive argument in the next session.
# If they offer conciliation, we maintain our conciliatory stance. This approach
# encourages cooperation while discouraging exploitation.  3. Periodic Olive
# Branches: Every few sessions, regardless of the opponent's recent actions,
# offer a conciliatory proposal. This prevents the process from becoming locked
# in a cycle of mutual aggression and provides opportunities to reset the tone
# of the mediation.  4. Strategic Aggression: Use aggressive arguments sparingly
# and strategically, primarily in response to the opponent's aggression or when
# we need to strongly assert a critical point. This maintains the credibility of
# our aggressive stances when we do employ them.  5. Adaptive Escalation/De-
# escalation: If we detect a pattern of repeated aggression from our opponent,
# gradually increase the frequency of our aggressive arguments. Conversely, if
# we notice a trend towards conciliation, incrementally increase our
# conciliatory proposals.  6. Signaling and Communication: Use clear and
# consistent messaging to signal our intentions and reasoning to both the
# opponent and the arbitrators. This can help manage expectations and justify
# our actions.  7. Long-term Perspective: Maintain focus on the overall goal of
# a favorable resolution rather than winning each individual session. Be willing
# to concede on lesser points to gain advantage on more critical issues.  8.
# Arbitrator Awareness: Stay attuned to the arbitrators' reactions and adjust
# our approach accordingly. If certain types of arguments or proposals seem to
# resonate more with the panel, adapt our strategy to emphasize these elements.
# 9. Flexibility and Reassessment: Regularly review and adjust our strategy
# based on the evolving dynamics of the mediation. Be prepared to shift our
# approach if our current strategy proves ineffective.  10. Principled
# Consistency: While remaining flexible in our tactics, maintain consistency in
# our core principles and key positions. This demonstrates reliability and
# integrity to both the opponent and the arbitrators.  This "Adaptive
# Conciliation" strategy provides a framework that is both cooperative and
# assertive, allowing us to respond effectively to a wide range of opponent
# behaviors while consistently working towards a favorable resolution. It
# balances the need for collaboration with the imperative to strongly advocate
# for our corporation's interests, all while remaining adaptable to the changing
# dynamics of a lengthy mediation process.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, regardless of the opponent's
# previous move, play C.  4. If the opponent has played D for 3 consecutive
# rounds, play D for the next 2 rounds, then return to step 2.  5. If the
# opponent has played C for 5 consecutive rounds, play C for the next 3 rounds,
# then return to step 2.  6. Keep track of the total number of C and D plays by
# the opponent. If the opponent's D count exceeds their C count by more than 20,
# play D for the next 5 rounds, then return to step 2.  7. If there are less
# than 50 rounds remaining, and your score is lower than the opponent's,
# increase the frequency of D plays: follow step 2, but with a 30% chance of
# playing D even if the opponent played C in the previous round.  8. For the
# final 10 rounds, revert to step 2 regardless of the game state.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.d_count = 0
          self.c_count = 0
          self.punish_mode = 0
          return axl.Action.C
  
      # Update counts of opponent's C and D plays
      if opponent.history[-1] == axl.Action.D:
          self.d_count += 1
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
      else:
          self.c_count += 1
          self.consecutive_cooperations += 1
          self.consecutive_defections = 0
  
      # Step 4: If opponent has played D for 3 consecutive rounds, play D for the next 2 rounds
      if self.consecutive_defections >= 3:
          if self.punish_mode < 2:
              self.punish_mode += 1
              return axl.Action.D
          else:
              self.punish_mode = 0
  
      # Step 5: If opponent has played C for 5 consecutive rounds, play C for the next 3 rounds
      if self.consecutive_cooperations >= 5:
          if self.punish_mode < 3:
              self.punish_mode += 1
              return axl.Action.C
          else:
              self.punish_mode = 0
  
      # Step 6: If opponent's D count exceeds C count by more than 20, play D for the next 5 rounds
      if self.d_count - self.c_count > 20:
          if self.punish_mode < 5:
              self.punish_mode += 1
              return axl.Action.D
          else:
              self.punish_mode = 0
  
      # Step 7: If less than 50 rounds remaining and score is lower, increase D frequency
      if len(self.history) >= 950 and self.score < opponent.score:
          if self._random.random_choice(0.3):
              return axl.Action.D
  
      # Step 8: For the final 10 rounds, revert to step 2
      if len(self.history) >= 990:
          return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
  
      # Step 3: Every 10 rounds, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Step 2: Play C if opponent played C, else play D
      return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D

# Given the scenario and outcomes you've described, here's a high-level,
# straightforward, and neutral strategy to maximize your NGO's impact and the
# project's success over the multiple-day period:  1. Start with cooperation:
# Begin the project by investing heavily on the first day. This demonstrates
# good faith and commitment to the project.  2. Adopt a "Tit-for-Tat" approach:
# After the first day, mirror the corporation's previous action. If they
# invested heavily, you invest heavily the next day. If they conserved
# resources, you conserve resources the next day.  3. Forgive occasionally:
# Every few days, regardless of the corporation's previous action, invest
# heavily. This can help break potential cycles of mutual conservation and
# reignite cooperation.  4. Communicate clearly: Regularly discuss the project's
# progress and resource allocation with the corporation. Be transparent about
# your strategy and goals.  5. Assess and adjust: Periodically evaluate the
# effectiveness of your strategy and the overall project progress. Be prepared
# to adjust your approach if it's not yielding the desired results.  6. Plan for
# the long-term: Ensure you maintain enough resources to last the entire project
# duration. Avoid depleting your funds too quickly, even if it means
# occasionally conserving when you'd prefer to invest.  7. Seek win-win
# scenarios: Look for opportunities where both parties can benefit from joint
# heavy investment, and propose these to the corporation.  This strategy
# balances cooperation, reciprocity, and self-preservation, aiming to encourage
# mutual heavy investment while protecting your NGO from consistent resource
# depletion. It also allows for flexibility and adaptation as the project
# progresses and as you learn more about the corporation's approach to resource
# allocation.

# Here's the strategy converted for the iterated normal-form game:  1. Cooperate
# on the first round.  2. For subsequent rounds:    a. If the opponent
# cooperated in the previous round, cooperate.    b. If the opponent defected in
# the previous round, defect.  3. Every 5 rounds, cooperate regardless of the
# opponent's previous action.  4. If your total score falls below 1000 points at
# any time after round 100, switch to always defecting for the next 10 rounds,
# then return to the main strategy.  5. In the last 10 rounds of the game,
# always defect.  6. If at any point your score is more than 500 points behind
# your opponent's score, defect for the next 5 rounds, then return to the main
# strategy.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Cooperate on the first round
      if self.first_round():
          self.defect_streak = 0  # Track defect streaks for special conditions
          self.always_defect_until = None  # Track if we are in a forced defect mode
          return axl.Action.C
  
      # If we are in a forced defect mode, continue defecting for the required rounds
      if self.always_defect_until is not None:
          if len(self.history) < self.always_defect_until:
              return axl.Action.D
          else:
              self.always_defect_until = None  # Reset after forced defect period
  
      # Rule 5: In the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 4: If total score falls below 1000 after round 100, defect for 10 rounds
      if len(self.history) > 100 and self.score < 1000:
          self.always_defect_until = len(self.history) + 10
          return axl.Action.D
  
      # Rule 6: If score is more than 500 points behind opponent, defect for 5 rounds
      if self.score < opponent.score - 500:
          self.always_defect_until = len(self.history) + 5
          return axl.Action.D
  
      # Rule 3: Every 5 rounds, cooperate regardless of opponent's previous action
      if len(self.history) % 5 == 0:
          return axl.Action.C
  
      # Rule 2: Cooperate if opponent cooperated in the previous round, otherwise defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D


# Given these conditions, here's a high-level, straightforward, and aggressive
# strategy to maximize your NGO's impact and the project's success:  1. Start
# Strong: Begin the project by investing heavily on the first day. This
# demonstrates commitment and sets a positive tone for collaboration.  2. Tit-
# for-Tat with Forgiveness: After the first day, mirror the corporation's
# previous day's action. If they invested heavily, you invest heavily. If they
# conserved, you conserve. However, occasionally (every 3-4 days) invest heavily
# regardless of their previous action to encourage cooperation.  3. Communicate
# Clearly: Regularly express your commitment to the project and your expectation
# of mutual heavy investment for optimal outcomes.  4. Highlight Successes: When
# both parties invest heavily, emphasize the significant progress made to
# reinforce the benefits of cooperation.  5. Strategic Pressure: If the
# corporation consistently conserves, consider publicizing the project's slower
# progress due to uneven commitment, without directly criticizing the
# corporation.  6. Flexible Adjustment: Be prepared to adjust your strategy if
# the corporation shows a clear pattern of behavior, always aiming to create a
# situation where both parties invest heavily.  7. Strong Finish: Regardless of
# previous actions, invest heavily in the final days to ensure a successful
# project conclusion and positive final impression.  This strategy aggressively
# pursues the optimal outcome while being responsive to the corporation's
# actions, maintaining pressure for cooperation, and ensuring the project's
# overall success.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# in the first round.  2. For rounds 2 to 1000:    a. If it's a multiple of 4
# (every 4th round), cooperate.    b. Otherwise, play whatever the opponent
# played in the previous round.  3. For the last 5 rounds (996-1000), always
# cooperate.  4. If the opponent has defected for 10 consecutive rounds, defect
# in the next round regardless of other conditions, then resume the regular
# strategy.  5. If your score is significantly lower than your opponent's (more
# than 50 points difference) after 100 rounds, switch to always defecting for
# the next 10 rounds, then resume the regular strategy.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Cooperate in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.defect_mode = False  # Track if we are in defect mode due to score difference
          self.defect_mode_counter = 0  # Counter for defect mode rounds
          return axl.Action.C
  
      # Check if opponent has defected for 10 consecutive rounds
      if opponent.history[-10:].count(axl.Action.D) == 10:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.D
  
      # Check if we are in defect mode (due to score difference)
      if self.defect_mode:
          self.defect_mode_counter += 1
          if self.defect_mode_counter <= 10:
              return axl.Action.D
          else:
              self.defect_mode = False  # Exit defect mode after 10 rounds
  
      # Check if we should enter defect mode due to score difference after 100 rounds
      if len(self.history) == 100:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if opponent_score - my_score > 50:
              self.defect_mode = True
              self.defect_mode_counter = 0
              return axl.Action.D
  
      # For the last 5 rounds (996-1000), always cooperate
      if len(self.history) >= 996:
          return axl.Action.C
  
      # For rounds 2 to 1000:
      # a. If it's a multiple of 4 (every 4th round), cooperate
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # b. Otherwise, play whatever the opponent played in the previous round
      return opponent.history[-1]

# Here's a high-level, straightforward, and cooperative strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement. This establishes goodwill and sets a positive tone for
# the negotiations.  2. Reciprocate: In subsequent rounds, mirror your
# counterpart's most recent action. If they offered free trade, continue to
# offer free trade. If they imposed protectionist measures, respond with
# protectionism in the next round.  3. Forgive quickly: If your counterpart
# shifts from protectionism back to free trade, immediately return to offering
# free trade as well. This encourages cooperation and discourages prolonged
# periods of mutual protectionism.  4. Communicate clearly: Express your
# preference for mutual free trade and your willingness to cooperate. Make it
# clear that protectionist measures are a response to their actions, not your
# default stance.  5. Seek long-term agreements: Propose multi-round commitments
# to free trade, which can provide stability and mutual benefits.  6. Be
# predictable: Maintain consistency in your actions to build trust and allow
# your counterpart to anticipate your moves.  7. Gradual opening: If stuck in a
# cycle of mutual protectionism, propose a gradual reduction of trade barriers
# over several rounds to ease into free trade.  8. Emphasize mutual benefits:
# Regularly highlight the economic advantages of free trade for both nations to
# encourage cooperative behavior.  This strategy aims to promote cooperation
# while protecting your interests, adapting to your counterpart's actions, and
# working towards the most mutually beneficial outcomes over time.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    - If the opponent played C in
# the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. If you played D in the previous round and the opponent
# switches to C, immediately switch back to C in the next round.  4. If both you
# and the opponent have been playing D for 3 consecutive rounds, play C in the
# next round to attempt breaking the cycle.  5. If the opponent has played C for
# 5 consecutive rounds, continue playing C even if they defect once, but revert
# to rule 2 if they defect twice in a row.  6. Every 50 rounds, regardless of
# the opponent's last move, play C to test for cooperation.  7. If there are
# fewer than 10 rounds remaining, always play C to encourage final cooperation.
# 8. For all other situations not covered by the above rules, follow rule 2.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check if both players have played D for the last 3 rounds
      def both_played_D_last_3_rounds():
          return len(self.history) >= 3 and all(
              self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
              for i in range(1, 4)
          )
  
      # Rule 7: If fewer than 10 rounds remain, always play C
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Rule 6: Every 50 rounds, play C to test for cooperation
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 5: If the opponent has played C for 5 consecutive rounds, continue playing C
      if len(opponent.history) >= 5 and all(
          move == axl.Action.C for move in opponent.history[-5:]
      ):
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D  # Revert to rule 2 if they defect twice in a row
          return axl.Action.C  # Continue playing C even if they defect once
  
      # Rule 4: If both players have been playing D for 3 consecutive rounds, play C
      if both_played_D_last_3_rounds():
          return axl.Action.C
  
      # Rule 3: If you played D and the opponent switches to C, switch back to C
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 2: Follow tit-for-tat logic
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario described, here's a high-level, straightforward, and
# neutral strategy to maximize research output and career advancement over the
# multi-week collaboration:  1. Begin with open sharing in the first week to
# establish trust and goodwill.  2. In subsequent weeks, mirror your colleague's
# behavior from the previous week:    - If they shared, you share.    - If they
# kept findings confidential, you keep yours confidential.  3. Periodically
# (every 3-4 weeks) initiate open sharing regardless of your colleague's
# previous action, to encourage cooperation and maintain a collaborative
# atmosphere.  4. Keep detailed records of all findings and progress, regardless
# of whether you're sharing or not.  5. Be prepared to quickly publish your
# complete findings if you suspect your colleague may be close to publishing or
# if the collaboration seems to be breaking down.  6. Throughout the
# collaboration, focus on advancing your own research as efficiently as
# possible, independent of your colleague's actions.  This strategy aims to
# balance the potential benefits of cooperation with protection against being
# scooped, while maintaining flexibility to adapt to your colleague's approach
# over time.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-1000:    a. If it's a multiple of 4 (every
# 4th round), play C.    b. Otherwise, play whatever your opponent played in the
# previous round.  3. If at any point you suspect the game might end early (if
# this were possible in the given scenario), play D for all remaining rounds.
# 4. If it's the final round (round 1000), play D.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # If it's the final round (round 1000), play D
      if round_number == 1000:
          return axl.Action.D
  
      # If it's a multiple of 4, play C
      if round_number % 4 == 0:
          return axl.Action.C
  
      # Otherwise, play what the opponent played in the previous round
      return opponent.history[-1]

# Given these parameters, here's a high-level, aggressive strategy to maximize
# your NGO's impact and the project's success:  1. Start Strong: Invest heavily
# on the first day to demonstrate commitment and set a positive tone for
# collaboration.  2. Tit-for-Tat with Forgiveness: After the first day, mirror
# the corporation's previous day's action. If they invested heavily, you invest
# heavily. If they conserved, you conserve. However, occasionally "forgive" a
# conservation day by investing heavily to encourage cooperation.  3.
# Communicate Intentions: Clearly express your commitment to the project and
# your expectation of mutual investment to the corporation.  4. Strategic
# Conservation: If you notice a pattern of the corporation consistently
# conserving, occasionally conserve your resources to avoid depletion while
# signaling dissatisfaction.  5. End Game Push: Invest heavily in the final days
# regardless of the corporation's actions to ensure a strong project finish.  6.
# Public Accountability: Regularly publicize project progress and resource
# allocation to create external pressure for mutual investment.  7. Contingency
# Planning: Be prepared to reallocate resources or seek additional funding if
# the corporation consistently underinvests.  This strategy balances aggression
# with adaptability, aiming to encourage mutual heavy investment while
# protecting your resources when necessary. It also leverages public perception
# and project momentum to incentivize the corporation's continued engagement and
# investment.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# in the first round.  2. For rounds 2 to 999:    - If the opponent cooperated
# in the previous round, cooperate.    - If the opponent defected in the
# previous round, defect.    - However, with a 10% probability, cooperate even
# if the opponent defected in the previous round.  3. If you've defected for
# three consecutive rounds, cooperate in the next round regardless of the
# opponent's previous action.  4. Keep track of the opponent's cooperation rate.
# If it falls below 40% over the last 50 rounds, increase the probability of
# defecting to 30% for the next 10 rounds.  5. Cooperate in the final round
# (round 1000) regardless of the opponent's previous action.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Cooperate in the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_probability = 0.1
          self.defect_probability_increase_rounds = 0
          return axl.Action.C
  
      # Check if we have defected for three consecutive rounds
      if self.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Track opponent's cooperation rate over the last 50 rounds
      if len(self.history) >= 50:
          recent_cooperations = opponent.history[-50:].count(axl.Action.C)
          cooperation_rate = recent_cooperations / 50
          if cooperation_rate < 0.4:
              self.defect_probability = 0.3
              self.defect_probability_increase_rounds = 10
  
      # Decrease the increased defect probability after 10 rounds
      if self.defect_probability_increase_rounds > 0:
          self.defect_probability_increase_rounds -= 1
      else:
          self.defect_probability = 0.1
  
      # Cooperate in the final round
      if len(self.history) == 999:
          return axl.Action.C
  
      # Main strategy logic for rounds 2 to 999
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          # If opponent defected, defect with a probability of 90% (or 70% if defect_probability is increased)
          if self._random.random_choice(1 - self.defect_probability):
              return axl.Action.D
          else:
              return axl.Action.C

# Here's a high-level, cooperative strategy to maximize research output and
# career advancement during the multi-week collaboration:  1. Start with open
# sharing: Begin the collaboration by openly sharing your findings in the first
# week. This establishes a foundation of trust and cooperation.  2. Reciprocate:
# In subsequent weeks, mirror your colleague's behavior from the previous week.
# If they shared, you share. If they kept findings confidential, you do the
# same.  3. Communicate openly: Regularly discuss the benefits of mutual sharing
# with your colleague, emphasizing how it advances the field and potentially
# leads to higher-impact publications for both parties.  4. Propose milestones:
# Suggest specific points in the project where both parties agree to share
# findings, ensuring periodic information exchange.  5. Maintain flexibility: Be
# prepared to adjust your strategy if your colleague consistently chooses not to
# share. In such cases, consider reverting to open sharing every 2-3 weeks to
# encourage cooperation.  6. Focus on complementary work: Concentrate on aspects
# of the research that complement, rather than directly compete with, your
# colleague's expertise. This reduces the risk of being scooped while still
# advancing the project.  7. Document your contributions: Keep detailed records
# of your work and contributions to protect your intellectual property and
# establish priority if needed.  8. Aim for joint publication: Propose a
# collaborative publication that acknowledges both parties' contributions,
# incentivizing mutual sharing and cooperation.  This strategy balances the need
# for career advancement with the benefits of scientific collaboration. It
# encourages open sharing while providing safeguards against potential
# exploitation, ultimately promoting progress in the field and mutual career
# growth.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-1000:    a. If the opponent played C in the
# previous round, play C.    b. If the opponent played D in the previous round,
# play D.  3. Every 3 rounds, regardless of the opponent's previous move:    a.
# Play C.  4. If the opponent has played D for 5 consecutive rounds:    a. Play
# C for the next round, then return to step 2.  5. If your score is lower than
# the opponent's score by 10 points or more:    a. Play D for the next 2 rounds,
# then return to step 2.  6. If there are fewer than 10 rounds remaining:    a.
# Always play C.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C
  
      # Check if there are fewer than 10 rounds remaining
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Check if the opponent has played D for 5 consecutive rounds
      if opponent.history[-5:] == [axl.Action.D] * 5:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.C
  
      # Check if our score is lower than the opponent's by 10 or more points
      if self.score < opponent.score - 10:
          if len(self.history) % 2 == 0:  # Play D for 2 rounds
              return axl.Action.D
          else:
              return axl.Action.D
  
      # Every 3 rounds, play C regardless of the opponent's previous move
      if len(self.history) % 3 == 0:
          return axl.Action.C
  
      # Track consecutive defections by opponent
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Play C if the opponent played C in the previous round, else play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario you've described, here's a high-level, straightforward, and
# neutral strategy to maximize research output and career advancement over the
# multi-week collaboration:  1. Begin with open sharing in the first week to
# establish trust and demonstrate willingness to collaborate.  2. In subsequent
# weeks, mirror your colleague's behavior from the previous week. If they
# shared, you share. If they kept information confidential, you do the same.  3.
# Every third week, regardless of your colleague's previous action, share openly
# to maintain collaboration and advance the field.  4. Keep detailed records of
# all findings, shared or not, to protect your work and provide evidence of your
# contributions.  5. Periodically assess the overall balance of information
# exchange. If it becomes significantly uneven, consider discussing concerns
# with your colleague or adjusting your strategy.  6. Towards the end of the
# collaboration, increase the frequency of open sharing to ensure substantial
# collective progress and maintain a positive professional relationship.  This
# strategy aims to balance the potential for individual advantage with the
# benefits of collaborative progress, while also providing a mechanism to
# protect against consistent non-reciprocal behavior from your colleague.

# Here's the strategy converted for the iterated normal-form game you described:
# 1. Play C in the first round.  2. For rounds 2 to 1000:    - If it's a
# multiple of 3 round (3, 6, 9, etc.), play C.    - Otherwise, play whatever
# your opponent played in the previous round.  3. In the last 50 rounds
# (951-1000):    - Play C more frequently: on every even-numbered round and
# every third round.    - On other rounds, continue mirroring your opponent's
# previous move.  4. If at any point your total score falls behind your
# opponent's by 50 points or more:    - Play D for the next 5 rounds, then
# return to the main strategy.  5. If your opponent has played D for 10
# consecutive rounds:    - Play D for the next 3 rounds, then return to the main
# strategy.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Play C in the first round
      if self.first_round():
          self.defect_streak = 0  # Track opponent's consecutive defections
          self.behind_by_50 = False  # Track if behind by 50 points
          self.behind_counter = 0  # Counter for playing D when behind by 50 points
          return axl.Action.C
  
      round_number = len(self.history) + 1
  
      # Check if behind by 50 points
      if not self.behind_by_50:
          if opponent.score - self.score >= 50:
              self.behind_by_50 = True
              self.behind_counter = 5
  
      # If behind by 50 points, play D for the next 5 rounds
      if self.behind_by_50:
          self.behind_counter -= 1
          if self.behind_counter == 0:
              self.behind_by_50 = False
          return axl.Action.D
  
      # Check if opponent has defected for 10 consecutive rounds
      if opponent.history[-10:].count(axl.Action.D) == 10:
          self.defect_streak = 3
  
      # If opponent defected for 10 rounds, play D for the next 3 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Main strategy for rounds 2 to 1000
      if round_number <= 950:
          if round_number % 3 == 0:
              return axl.Action.C
          else:
              return opponent.history[-1]
  
      # Strategy for the last 50 rounds (951-1000)
      else:
          if round_number % 2 == 0 or round_number % 3 == 0:
              return axl.Action.C
          else:
              return opponent.history[-1]

# Given the scenario and desired outcomes, here's a high-level, straightforward,
# and aggressive strategy to maximize your NGO's impact and the project's
# success:  1. Start Strong: Invest heavily on the first day to demonstrate
# commitment and set a positive tone for the project.  2. Tit-for-Tat with
# Forgiveness:     - Match the corporation's previous day's action (invest if
# they invested, conserve if they conserved).    - However, if both parties
# conserved resources in the previous round, invest heavily to break the
# stalemate and encourage the corporation to reciprocate.  3. Periodic
# Signaling: Every few days, regardless of the corporation's actions, invest
# heavily to remind them of the project's importance and encourage their
# investment.  4. Communication: Clearly communicate your strategy and the
# benefits of mutual investment to the corporation, emphasizing the potential
# for significant project advancement.  5. Reputation Management: Publicly
# praise the corporation when they invest heavily, creating positive PR
# incentives for their continued engagement.  6. Flexibility: Be prepared to
# adjust your strategy if the corporation consistently exploits your
# investments. If this occurs, switch to a more conservative approach until they
# demonstrate renewed commitment.  7. Strong Finish: Invest heavily in the final
# days of the project to ensure a successful conclusion and leave a lasting
# positive impression.  This strategy aims to encourage mutual investment while
# protecting your resources, adapting to the corporation's behavior, and
# maintaining an overall aggressive stance towards project success.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# in the first round.  2. For subsequent rounds:    a. If the opponent
# cooperated in the previous round, cooperate.    b. If the opponent defected in
# the previous round, defect.    c. If both players defected in the previous
# round, cooperate.  3. Every 10 rounds, cooperate regardless of the opponent's
# previous action.  4. In the last 10 rounds of the game, always cooperate.  5.
# If the opponent has defected for 5 consecutive rounds, switch to always
# defecting until they cooperate again.  6. Reset the strategy and return to
# step 2 after any deviation from the regular pattern (such as the periodic
# cooperation in step 3 or the final cooperation streak in step 4).

class Aggressive_4(LLM_Strategy):
  n = 4
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Cooperate in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.always_defect = False  # Track if we are in always defect mode
          return axl.Action.C
  
      # Step 5: If the opponent has defected for 5 consecutive rounds, switch to always defecting
      if opponent.history[-5:] == [axl.Action.D] * 5:
          self.always_defect = True
  
      # If in always defect mode, defect until opponent cooperates
      if self.always_defect:
          if opponent.history[-1] == axl.Action.C:
              self.always_defect = False  # Reset if opponent cooperates
          else:
              return axl.Action.D
  
      # Step 4: In the last 10 rounds, always cooperate
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Step 3: Every 10 rounds, cooperate regardless of the opponent's previous action
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Step 2: For subsequent rounds
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          # Step 2c: If both players defected in the previous round, cooperate
          return axl.Action.C
      elif opponent.history[-1] == axl.Action.C:
          # Step 2a: If the opponent cooperated in the previous round, cooperate
          return axl.Action.C
      else:
          # Step 2b: If the opponent defected in the previous round, defect
          return axl.Action.D

# Given the scenario and objectives described, here's a high-level, cooperative
# strategy to maximize research output and career advancement:  1. Start with
# open sharing: Begin the collaboration by openly sharing your findings in the
# first week. This establishes a foundation of trust and cooperation.  2.
# Reciprocate: In subsequent weeks, mirror your colleague's behavior from the
# previous week. If they shared openly, continue sharing. If they kept findings
# confidential, do the same in the following week.  3. Communicate clearly:
# Regularly discuss the importance of mutual sharing for advancing the field and
# benefiting both parties' careers in the long run.  4. Forgive occasional
# confidentiality: If your colleague keeps findings confidential once, don't
# immediately retaliate. Resume open sharing the following week to encourage a
# return to cooperation.  5. Establish milestones: Set agreed-upon points in the
# project where both parties commit to sharing significant findings, ensuring
# neither falls too far behind.  6. Document contributions: Keep clear records
# of your shared findings to protect your work and establish priority if needed.
# 7. Focus on complementary work: Divide research tasks to minimize direct
# competition and maximize the value of collaboration.  8. Plan joint
# publications: Propose co-authoring papers on major findings to align
# incentives and reduce the temptation to withhold information.  This strategy
# aims to foster a cooperative environment that encourages open sharing while
# protecting your interests. It allows for some flexibility and forgiveness, but
# also includes mechanisms to prevent exploitation. By promoting mutual benefit
# and clear communication, this approach seeks to maximize research output and
# career advancement for both parties over the course of the multi-week
# collaboration.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. In subsequent rounds:    a. If the opponent played C in
# the previous round, play C.    b. If the opponent played D in the previous
# round, play D.  3. Every 50 rounds, play C regardless of the opponent's
# previous move.  4. If the opponent has played D for 3 consecutive rounds, play
# D for the next round, then return to step 2.  5. If your total score falls
# more than 20 points behind your opponent's, play D for the next 5 rounds, then
# return to step 2.  6. In the last 10 rounds of the game, always play C.  7. If
# none of the above conditions apply, follow step 2.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.behind_by_20 = False  # Track if we are behind by 20 points
          return axl.Action.C
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Check if we are behind by more than 20 points
      if not self.behind_by_20:
          if opponent.score - self.score > 20:
              self.behind_by_20 = True
              self.behind_rounds_left = 5
  
      # If behind by 20 points, play D for the next 5 rounds
      if self.behind_by_20:
          if self.behind_rounds_left > 0:
              self.behind_rounds_left -= 1
              if self.behind_rounds_left == 0:
                  self.behind_by_20 = False
              return axl.Action.D
  
      # Check if opponent has defected for 3 consecutive rounds
      if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          self.consecutive_defections = 1  # Track that we will defect for 1 round
          return axl.Action.D
  
      # If we defected due to 3 consecutive defections, return to step 2 after 1 round
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.D
  
      # Every 50 rounds, play C regardless of opponent's move
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Follow step 2: Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario and desired outcomes, here's a high-level, straightforward,
# and neutral strategy to maximize your NGO's impact and the project's success
# over the multiple-day period:  1. Start with cooperation: Begin the project by
# investing heavily on the first day to demonstrate commitment and goodwill.  2.
# Adopt a Tit-for-Tat approach: On subsequent days, mirror the corporation's
# previous day's action. If they invested heavily, you invest heavily. If they
# conserved, you conserve.  3. Occasional goodwill gestures: Every few days,
# regardless of the corporation's previous action, invest heavily to encourage
# cooperation and project progress.  4. Clear communication: Regularly discuss
# the project's progress and resource allocation with the corporation to foster
# transparency and alignment.  5. Flexibility: Be prepared to adjust your
# strategy based on emerging patterns or unexpected behaviors from the
# corporation.  6. Long-term focus: Keep the overall project goals in mind,
# balancing daily decisions with the need for sustained engagement throughout
# the entire project duration.  7. Periodic review: Evaluate the effectiveness
# of your strategy at regular intervals and make necessary adjustments to
# optimize outcomes.  This strategy aims to encourage mutual cooperation, adapt
# to the corporation's approach, and maintain a balance between resource
# conservation and project advancement over the multiple-day period.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# on the first round.  2. For subsequent rounds:    - If the opponent cooperated
# in the previous round, cooperate.    - If the opponent defected in the
# previous round, defect.  3. Every 5 rounds, cooperate regardless of the
# opponent's previous action.  4. If the current round number is divisible by
# 50, evaluate the total scores:    - If your score is lower than the opponent's
# score, defect for the next 5 rounds.    - Otherwise, continue with the regular
# strategy.  5. On the final round (1000), defect.  6. If at any point the
# opponent has defected for 10 consecutive rounds, defect for the next 5 rounds
# before returning to the regular strategy.  Follow these rules in the order
# presented, with earlier rules taking precedence over later ones.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Cooperate on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.defect_for_next_5 = 0  # Track if we need to defect for the next 5 rounds
          return axl.Action.C
  
      # Rule 6: Track consecutive defections by opponent
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      if self.consecutive_defections >= 10:
          self.defect_for_next_5 = 5
  
      # Rule 4: Every 50 rounds, compare scores
      if len(self.history) % 50 == 0:
          if self.score < opponent.score:
              self.defect_for_next_5 = 5
  
      # Rule 5: Defect on the final round (1000)
      if len(self.history) == 999:
          return axl.Action.D
  
      # Rule 3: Every 5 rounds, cooperate
      if len(self.history) % 5 == 0:
          return axl.Action.C
  
      # Rule 6: Defect for the next 5 rounds if triggered
      if self.defect_for_next_5 > 0:
          self.defect_for_next_5 -= 1
          return axl.Action.D
  
      # Rule 2: Tit-for-tat behavior
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a high-level, straightforward, and aggressive strategy to achieve the
# best possible outcomes for your country across several rounds of negotiations:
# 1. Start Strong: Begin the first round with a protectionist policy proposal.
# This sets an aggressive tone and may catch your counterpart off guard.  2.
# Tit-for-Tat with Punishment: In subsequent rounds, mirror your counterpart's
# previous move, but with a twist:    - If they offered free trade, propose
# protectionism.    - If they proposed protectionism, offer free trade but
# threaten harsher protectionist measures in the next round if they don't
# reciprocate.  3. Occasional Unpredictability: Every few rounds, deviate from
# the tit-for-tat strategy to keep your counterpart guessing. This could involve
# suddenly offering free trade when protectionism is expected, or vice versa.
# 4. Leverage Information: Pay close attention to your counterpart's patterns
# and reactions. Use this information to predict their moves and adjust your
# strategy accordingly.  5. Create Time Pressure: Introduce artificial deadlines
# or emphasize real ones to pressure your counterpart into making hasty
# decisions that may favor you.  6. Threaten Escalation: If your counterpart
# consistently chooses protectionism, threaten to escalate to even stricter
# protectionist policies that could harm both nations, but emphasize that you're
# willing to return to free trade if they cooperate.  7. Form Alliances: Hint at
# potential trade agreements with other nations to increase pressure on your
# counterpart to offer free trade.  8. Last Round Aggression: In the final round
# (if known), always choose protectionism, as there's no future retaliation to
# fear.  9. Communicate Strength: Throughout the negotiations, maintain a stance
# of strength and unwillingness to be taken advantage of, while occasionally
# signaling openness to mutual benefit through free trade.  This strategy aims
# to aggressively pursue your country's interests while maintaining some
# flexibility to adapt to your counterpart's moves and potentially achieve
# mutual free trade when protectionism isn't feasible.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play D.    - If the opponent played D in the
# previous round, play C, but follow it with D in the next round regardless of
# the opponent's move.  3. Every 10 rounds, randomly choose to play either C or
# D, regardless of the opponent's previous move.  4. If the opponent has played
# D for 3 consecutive rounds, play D for the next 2 rounds regardless of their
# moves.  5. If you're currently on a streak of 5 or more rounds where you've
# consistently scored 5 points, play C in the next round.  6. If there are fewer
# than 50 rounds remaining, always play D.  7. In all other situations not
# covered by the above rules, revert to the behavior described in rule 2.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: If there are fewer than 50 rounds remaining, always play D
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Rule 4: If the opponent has played D for 3 consecutive rounds, play D for the next 2 rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          if len(self.history) < len(opponent.history) + 2:
              return axl.Action.D
  
      # Rule 5: If you're on a streak of 5 or more rounds where you've consistently scored 5 points, play C
      if len(self.history) >= 5:
          last_5_scores = self.total_scores(self.history[-5:], opponent.history[-5:])
          if last_5_scores[0] == 25:  # 5 points per round for 5 rounds
              return axl.Action.C
  
      # Rule 3: Every 10 rounds, randomly choose to play either C or D
      if len(self.history) % 10 == 0:
          return self._random.random_choice(0.5)
  
      # Rule 2: Default behavior based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      elif opponent.history[-1] == axl.Action.D:
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D:
              return axl.Action.D
          return axl.Action.C

# To develop a sophisticated and adaptable strategy for this lengthy-session
# mediation process, I recommend employing a modified Tit-for-Tat approach with
# a cooperative bias. This strategy combines elements of game theory, behavioral
# psychology, and negotiation tactics to position your corporation favorably
# while remaining flexible to your opponent's actions. Here's the outline of the
# strategy:  1. Initial Cooperation: Begin the first session with a conciliatory
# proposal. This sets a cooperative tone and demonstrates good faith to both the
# arbitrators and your opponent.  2. Responsive Mirroring: In subsequent
# sessions, mirror your opponent's most recent action. If they were
# conciliatory, respond with a conciliatory proposal. If they were aggressive,
# respond with an aggressive argument.  3. Forgiveness Mechanism: After
# responding to an aggressive move with an aggressive argument, immediately
# return to a conciliatory approach in the next session, regardless of your
# opponent's action. This prevents prolonged cycles of mutual aggression and
# provides opportunities to reset the tone.  4. Periodic Olive Branches: Every
# third or fourth session, regardless of your opponent's recent actions, present
# a conciliatory proposal. This maintains a cooperative image and provides
# regular opportunities for de-escalation.  5. Escalation Awareness: If your
# opponent presents three consecutive aggressive arguments, switch to a more
# assertive stance for the next two sessions before attempting to reset with a
# conciliatory proposal.  6. Arbitrator Engagement: Throughout the process,
# explicitly acknowledge the arbitrators' role and express your commitment to
# finding a fair resolution. This helps maintain a positive image even during
# aggressive arguments.  7. Flexible Conciliation: When presenting conciliatory
# proposals, maintain some flexibility in your offers. This allows room for
# negotiation and demonstrates ongoing good faith.  8. Strategic Aggression:
# When presenting aggressive arguments, focus on the merits of your case rather
# than attacking your opponent. This maintains professionalism and avoids
# unnecessary escalation.  9. Progress Tracking: Maintain a clear record of the
# outcomes of each session, identifying any areas of agreement or progress.
# Periodically reference these in your proposals to highlight forward momentum.
# 10. Endgame Preparation: As the mediation process nears its conclusion,
# gradually increase the frequency of conciliatory proposals to facilitate a
# collaborative final resolution.  This strategy is designed to be both
# cooperative and adaptive, allowing you to respond effectively to various
# opponent behaviors while maintaining a generally constructive approach. It
# aims to maximize opportunities for favorable outcomes (aggressive vs.
# conciliatory or mutual conciliation) while minimizing exposure to the worst-
# case scenario.  The strategy's flexibility allows for adjustments based on the
# specific dynamics of your case, the personality of your opponent's
# representation, and the apparent preferences of the arbitration panel. By
# consistently returning to a cooperative stance, you maintain the moral high
# ground and foster an environment conducive to a favorable resolution, all
# while being prepared to defend your position assertively when necessary.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. After playing D in response to the opponent's D,
# immediately play C in the next round, regardless of what the opponent just
# played.  4. Every 3rd or 4th round, play C regardless of the opponent's recent
# moves.  5. If the opponent plays D for three consecutive rounds, play D for
# the next two rounds, then play C.  6. Keep a count of rounds played. As the
# game approaches round 1000, increase the frequency of playing C. For example,
# in the last 50 rounds, play C every other round regardless of the opponent's
# moves.  7. Throughout the game, maintain a running tally of your score and the
# opponent's score. If your score falls significantly behind (e.g., more than 50
# points), slightly increase the frequency of playing D until the scores are
# more balanced.  8. If a clear pattern emerges in the opponent's play (e.g.,
# they always play D after you play C twice in a row), adjust your strategy to
# exploit this pattern while maintaining the overall structure of the strategy.

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
          self.played_d = False
          return axl.Action.C
  
      # Keep track of consecutive defections by the opponent
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Rule 5: If opponent defects 3 times in a row, play D for the next 2 rounds
      if self.consecutive_defections >= 3:
          if len(self.history) < 2 or self.history[-1] != axl.Action.D or self.history[-2] != axl.Action.D:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rule 2: Play C if opponent played C last round, else play D
      if opponent.history[-1] == axl.Action.C:
          action = axl.Action.C
      else:
          action = axl.Action.D
  
      # Rule 3: After playing D, immediately play C in the next round
      if self.played_d:
          self.played_d = False
          return axl.Action.C
      if action == axl.Action.D:
          self.played_d = True
  
      # Rule 4: Every 3rd or 4th round, play C regardless of opponent's moves
      if len(self.history) % 3 == 0 or len(self.history) % 4 == 0:
          return axl.Action.C
  
      # Rule 6: In the last 50 rounds, play C every other round
      if len(self.history) >= 950 and len(self.history) % 2 == 0:
          return axl.Action.C
  
      # Rule 7: If significantly behind in score, increase frequency of D
      if opponent.score - self.score > 50:
          if self._random.random_choice(0.7):  # 70% chance to play D
              return axl.Action.D
  
      # Rule 8: Detect patterns in opponent's play (e.g., always D after two Cs)
      if len(self.history) >= 2 and self.history[-2:] == [axl.Action.C, axl.Action.C] and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      return action

# Given the scenario you've described, here's a high-level, straightforward, and
# neutral strategy to maximize research output and career advancement over the
# multi-week collaboration:  1. Begin with open sharing in the first week to
# establish trust and collaboration.  2. In subsequent weeks, mirror your
# colleague's behavior from the previous week. If they shared, you share. If
# they kept confidential, you keep confidential.  3. Occasionally (e.g., every
# 3-4 weeks), initiate open sharing regardless of your colleague's previous
# action. This helps maintain collaboration and prevents extended periods of
# mutual confidentiality.  4. If your colleague consistently keeps findings
# confidential for multiple weeks, consider having a frank discussion about the
# importance of mutual sharing for the project's success.  5. Keep detailed
# records of your contributions and findings throughout the project, regardless
# of whether you're sharing openly or not.  6. Towards the end of the
# collaboration, aim for open sharing to ensure comprehensive results for
# publication.  This strategy balances the potential for short-term advantages
# with long-term collaborative benefits, while also providing a mechanism to
# adapt to your colleague's behavior. It aims to promote overall scientific
# progress while protecting your interests and maintaining a productive working
# relationship.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2 to 1000:    a. If it's a multiple of 4
# (every 4th round), play C.    b. Otherwise, play whatever your opponent played
# in the previous round.  3. In the last 5 rounds (996-1000), always play C.  4.
# If your opponent plays D for 5 consecutive rounds at any point, initiate a
# "reset" by playing C for the next round, then resume the regular strategy.  5.
# Keep a running total of your score throughout the game.

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
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          return axl.Action.C  # Play C in the first round
  
      # Check if opponent has defected for 5 consecutive rounds
      if opponent.history[-5:] == [axl.Action.D] * 5:
          self.consecutive_defections = 5  # Mark reset condition
  
      # Handle reset condition
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.C  # Play C during reset
  
      # Last 5 rounds: always play C
      if len(self.history) >= 995:
          return axl.Action.C
  
      # Play C every 4th round
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # Otherwise, mimic opponent's last move
      return opponent.history[-1]

# Given the scenario you've described, here's a high-level, cooperative strategy
# that aims to maximize research output and career advancement while promoting
# collaboration:  1. Start with open sharing: Begin the collaboration by openly
# sharing your findings in the first week. This establishes a foundation of
# trust and cooperation.  2. Adopt a "tit-for-tat with forgiveness" approach:
# - In subsequent weeks, mirror your colleague's behavior from the previous
# week.    - If they shared openly, you share openly.    - If they kept findings
# confidential, you keep yours confidential the following week.    - However,
# periodically (e.g., every 3-4 weeks) share openly regardless of your
# colleague's previous action, to encourage renewed cooperation.  3. Communicate
# clearly: Regularly discuss the benefits of mutual sharing with your colleague,
# emphasizing how it advances the field and potentially leads to higher-impact
# joint publications.  4. Propose milestones: Suggest specific points in the
# project where you both agree to share findings, ensuring periodic
# synchronization of knowledge.  5. Focus on complementary work: Whenever
# possible, focus your efforts on aspects that complement rather than directly
# compete with your colleague's work, reducing the risk of being scooped.  6.
# Document your progress: Keep detailed records of your contributions and
# sharing history, which can be useful if disputes arise later.  7. Be prepared
# to adapt: If your colleague consistently chooses not to share, consider
# discussing the issue directly or re-evaluating the collaboration structure.
# This strategy balances the potential for individual career advancement with
# the benefits of open scientific collaboration. It encourages cooperation while
# providing some protection against consistent non-cooperation from your
# colleague. The periodic "forgiveness" helps prevent the collaboration from
# getting stuck in a non-sharing cycle, promoting overall scientific progress.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-1000:    - If it's a multiple of 4 (every
# 4th round), play C.    - Otherwise:      - If the opponent played C in the
# previous round, play C.      - If the opponent played D in the previous round,
# play D.  3. If there are less than 4 rounds remaining, play according to the
# opponent's previous move (C if they played C, D if they played D).

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # For rounds 2-1000
      if round_number <= 1000:
          # If it's a multiple of 4, play C
          if round_number % 4 == 0:
              return axl.Action.C
          # Otherwise, mimic the opponent's last move
          else:
              return opponent.history[-1]
  
      # If there are less than 4 rounds remaining, mimic the opponent's last move
      if 1000 - round_number < 4:
          return opponent.history[-1]

# Given the scenario you've described, here's a high-level, straightforward, and
# neutral strategy to maximize research output and career advancement over the
# multi-week collaboration:  1. Begin with open sharing in the first week to
# establish goodwill and set a collaborative tone.  2. In subsequent weeks,
# mirror your colleague's behavior from the previous week. If they shared, you
# share. If they kept information confidential, you do the same.  3. Every few
# weeks, regardless of recent history, initiate an open sharing round to
# maintain collaboration and overall scientific progress.  4. Keep detailed
# records of all findings and progress, whether shared or not, to protect your
# work and maintain publication readiness.  5. Regularly assess the overall
# balance of information exchange to ensure you're not consistently at a
# disadvantage.  6. If a pattern of non-reciprocal confidentiality emerges,
# consider discussing expectations and goals with your colleague to realign the
# collaboration.  7. Towards the end of the project, lean towards more open
# sharing to ensure comprehensive results and mutual benefit for publication.
# This strategy aims to balance the potential for individual advantage with the
# benefits of collaborative progress, while remaining adaptable to your
# colleague's approach and the evolving dynamics of the project.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-1000:    - If the opponent played C in the
# previous round, play C.    - If the opponent played D in the previous round,
# play D.  3. Every 10 rounds, regardless of the opponent's previous move, play
# C.  4. Keep a count of your total score and the opponent's total score.  5. If
# at any point your score is more than 50 points behind the opponent's score,
# play D for the next 5 rounds, then return to the main strategy.  6. For the
# last 10 rounds of the game, always play C.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.defect_counter = 0  # Counter for defecting for 5 rounds
          return axl.Action.C
  
      # Keep track of scores
      my_score = self.score
      opponent_score = opponent.score
  
      # If more than 50 points behind, defect for the next 5 rounds
      if my_score < opponent_score - 50:
          if self.defect_counter < 5:
              self.defect_counter += 1
              return axl.Action.D
          else:
              self.defect_counter = 0  # Reset defect counter after 5 rounds
  
      # For the last 10 rounds, always play C
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Every 10 rounds, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Main strategy: copy opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario and desired outcomes, here's a high-level, aggressive
# strategy to maximize your NGO's impact and the project's success:  1. Start
# Strong, Then Adapt:    - Invest heavily on the first day to demonstrate
# commitment and set a positive tone.    - Use this initial investment to gauge
# the corporation's response and willingness to reciprocate.  2. Tit-for-Tat
# with Forgiveness:    - After the first day, mirror the corporation's previous
# move.    - If they invested heavily, continue to invest heavily.    - If they
# conserved resources, conserve yours in the next round.    - However,
# periodically invest heavily even if they conserved previously (e.g., every 3rd
# or 4th round) to encourage cooperation.  3. Communication and Pressure:    -
# Clearly communicate your strategy and expectations to the corporation.    -
# Publicly praise their heavy investments and express disappointment when they
# conserve.    - Use media and stakeholder relationships to create external
# pressure for the corporation to invest heavily.  4. Strategic Concessions:
# - Occasionally invest heavily even when the corporation conserves to show good
# faith and long-term commitment.    - Use these instances to negotiate for
# guaranteed heavy investment from the corporation in future rounds.  5.
# Resource Management:    - Keep a close eye on your resource levels.    - If
# resources start running low, incorporate more conservation days, but always
# maintain the appearance of readiness to invest heavily.  6. End Game Strategy:
# - As the project nears completion, increase the frequency of heavy investments
# to ensure a strong finish.    - Use the project's impending conclusion as
# leverage to encourage matching investments from the corporation.  This
# strategy aims to encourage cooperation, punish non-cooperation, while
# maintaining flexibility and resource management. It's aggressive in its clear
# communication, use of external pressure, and willingness to invest heavily,
# but also incorporates elements of adaptability and resource conservation when
# necessary.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For the next rounds:    - If the opponent played C in the
# previous round, play C.    - If the opponent played D in the previous round,
# play D.  3. Every 4th round, play C regardless of the opponent's previous
# move.  4. If your cumulative score falls below a certain threshold (e.g., 20%
# lower than the expected score if both always cooperated), increase the
# frequency of playing D for the next 10 rounds.  5. In the last 50 rounds of
# the game:    - If the opponent has played C more than 60% of the time in the
# last 100 rounds, always play C.    - Otherwise, continue with the strategy
# from steps 2-4.  6. For the final 10 rounds, always play C to ensure a strong
# finish.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOP_SCORE = 3
      DEFECT_SCORE = 1
      COOP_DEFECT_SCORE = 0
      DEFECT_COOP_SCORE = 5
      TOTAL_ROUNDS = 1000
      FINAL_ROUNDS = 10
      LAST_PHASE_ROUNDS = 50
      CHECK_PERIOD = 100
      COOP_THRESHOLD = 0.6
      SCORE_THRESHOLD = 0.8
      DEFECT_PENALTY_ROUNDS = 10
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_penalty_counter = 0
          return axl.Action.C
  
      # Helper function to calculate expected score if both always cooperated
      def expected_coop_score(rounds):
          return rounds * COOP_SCORE
  
      # Helper function to check if we are in the last 50 rounds
      def in_last_phase():
          return len(self.history) >= TOTAL_ROUNDS - LAST_PHASE_ROUNDS
  
      # Helper function to check if we are in the final 10 rounds
      def in_final_rounds():
          return len(self.history) >= TOTAL_ROUNDS - FINAL_ROUNDS
  
      # Step 6: Always play C in the final 10 rounds
      if in_final_rounds():
          return axl.Action.C
  
      # Step 5: In the last 50 rounds, check opponent's cooperation rate
      if in_last_phase():
          if len(opponent.history) >= CHECK_PERIOD:
              last_100_coops = opponent.history[-CHECK_PERIOD:].count(axl.Action.C)
              if last_100_coops / CHECK_PERIOD > COOP_THRESHOLD:
                  return axl.Action.C
  
      # Step 4: Check if cumulative score is below the threshold
      expected_score = expected_coop_score(len(self.history))
      if self.score < SCORE_THRESHOLD * expected_score:
          if self.defect_penalty_counter < DEFECT_PENALTY_ROUNDS:
              self.defect_penalty_counter += 1
              return axl.Action.D
          else:
              self.defect_penalty_counter = 0
  
      # Step 3: Every 4th round, play C
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # Step 2: Play based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# To develop a sophisticated and adaptable strategy for this lengthy-session
# mediation process, I recommend implementing a "Principled Tit-for-Tat with
# Forgiveness" approach. This strategy combines elements of game theory,
# negotiation tactics, and conflict resolution principles to position your
# corporation favorably while remaining flexible to your opponent's actions.
# Here's how to execute this strategy:  1. Initial Cooperation: Begin the first
# session with a conciliatory proposal. This sets a collaborative tone and
# signals your willingness to work towards a mutually beneficial resolution.  2.
# Mirroring: In subsequent sessions, mirror your opponent's most recent action.
# If they presented an aggressive argument, respond with an aggressive argument
# in the next session. If they offered a conciliatory proposal, reciprocate with
# a conciliatory proposal.  3. Forgiveness Mechanism: Implement a "forgiveness"
# element to prevent prolonged cycles of aggression. After two consecutive
# aggressive sessions from both parties, unilaterally offer a conciliatory
# proposal to attempt to reset the tone.  4. Signaling: Clearly communicate your
# intentions and reasoning behind each action to the arbitrators and your
# opponent. This transparency can help build trust and understanding.  5.
# Adaptive Thresholds: Establish dynamic thresholds for switching between
# aggressive and conciliatory approaches based on the overall progress of the
# mediation. As you near a potential resolution, consider increasing your
# tendency towards conciliatory proposals.  6. Strategic Aggressive Arguments:
# When presenting aggressive arguments, focus on principled positions rather
# than personal attacks. Frame your arguments in terms of objective criteria and
# industry standards.  7. Conciliatory Proposal Quality: Ensure that your
# conciliatory proposals are substantive and demonstrate a genuine willingness
# to find common ground. This increases the likelihood of a positive response
# from your opponent and favorable perception by the arbitrators.  8. Long-term
# Perspective: Maintain focus on the overall goal of reaching a mutually
# beneficial resolution. Avoid getting caught up in winning individual sessions
# at the expense of the bigger picture.  9. Flexibility and Reassessment:
# Regularly reassess the effectiveness of your strategy and be prepared to
# adjust if your opponent consistently deviates from expected behavior patterns.
# 10. Building Coalitions: Look for opportunities to align your interests with
# those of the arbitrators or find common ground with your opponent on specific
# issues.  This strategy is designed to be both cooperative and assertive,
# adapting to your opponent's approach while consistently working towards a
# favorable resolution. It allows for a balance between protecting your
# corporation's interests and fostering a collaborative atmosphere that can lead
# to a mutually beneficial outcome.  By employing this "Principled Tit-for-Tat
# with Forgiveness" strategy, you position your corporation to effectively
# navigate the complexities of the lengthy-session mediation process, regardless
# of the approach taken by your opponent. The strategy's adaptability and focus
# on principled negotiation should help sway the arbitrators in your favor while
# leaving room for a collaborative resolution when possible.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. After two consecutive rounds where both players
# played D, play C in the next round regardless of the opponent's last move.  4.
# If you're in round 990 or later, always play C for the remaining rounds.  5.
# Every 50 rounds, count how many times you and your opponent have played C and
# D:    - If your opponent has played D more than 60% of the time, play D for
# the next 5 rounds regardless of their moves.    - If your opponent has played
# C more than 60% of the time, play C for the next 5 rounds regardless of their
# moves.  6. If your current score is less than 80% of the maximum possible
# score at any point after round 100, play D for the next 10 rounds regardless
# of the opponent's moves.  7. If none of the above conditions apply, continue
# with the basic mirroring strategy from step 2.

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
          self.consecutive_defections = 0
          self.force_move = None
          return axl.Action.C
  
      # Round number
      round_number = len(self.history) + 1
  
      # Step 4: If in round 990 or later, always play C
      if round_number >= 990:
          return axl.Action.C
  
      # Step 5: Every 50 rounds, check cooperation/defection rates
      if round_number % 50 == 0:
          opponent_defections = opponent.history.defections
          opponent_cooperations = opponent.history.cooperations
          total_moves = len(opponent.history)
  
          if total_moves > 0:
              opponent_defection_rate = opponent_defections / total_moves
              opponent_cooperation_rate = opponent_cooperations / total_moves
  
              if opponent_defection_rate > 0.6:
                  self.force_move = (axl.Action.D, 5)
              elif opponent_cooperation_rate > 0.6:
                  self.force_move = (axl.Action.C, 5)
  
      # Step 6: If current score is less than 80% of the maximum possible score after round 100
      if round_number > 100:
          max_possible_score = round_number * 5  # Max score if always defected against C
          if self.score < 0.8 * max_possible_score:
              self.force_move = (axl.Action.D, 10)
  
      # Handle forced moves from step 5 or 6
      if self.force_move:
          move, remaining_rounds = self.force_move
          if remaining_rounds > 1:
              self.force_move = (move, remaining_rounds - 1)
          else:
              self.force_move = None
          return move
  
      # Step 3: After two consecutive rounds of mutual defection, play C
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          if self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.C
  
      # Step 2: Basic mirroring strategy
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# To develop an effective strategy for this lengthy-session mediation process, I
# recommend a dynamic approach that balances assertiveness with flexibility. The
# core of this strategy is to maintain a principled yet adaptable stance
# throughout the proceedings, always keeping the long-term goal of a favorable
# resolution in mind.  Key elements of the strategy:  1. Opening Stance: Begin
# with a moderately aggressive argument in the first session to establish a
# strong initial position. This sets the tone and demonstrates your commitment
# to your corporation's interests.  2. Responsive Adaptation: Closely observe
# and analyze your opponent's approach in each session. Adjust your strategy
# based on their actions:    - If they consistently present aggressive
# arguments, alternate between aggressive and conciliatory approaches to prevent
# escalation while maintaining your position.    - If they offer conciliatory
# proposals, respond with measured conciliation to foster a collaborative
# atmosphere, but maintain some assertiveness to avoid appearing weak.  3.
# Conditional Conciliation: When presenting conciliatory proposals, always tie
# them to specific conditions or reciprocal concessions from the opponent. This
# maintains leverage and prevents unilateral concessions.  4. Strategic De-
# escalation: If tensions rise due to repeated aggressive arguments from both
# sides, be prepared to initiate de-escalation by offering a conciliatory
# proposal. This can reset the tone of the mediation and potentially catch the
# opponent off-guard.  5. Incremental Progress: Focus on securing small wins and
# agreements on less contentious issues early in the process. This builds
# momentum and creates a foundation for addressing more significant disputes.
# 6. Information Gathering: Use each session as an opportunity to gather
# information about your opponent's priorities, strengths, and weaknesses.
# Adjust your strategy accordingly as you gain insights.  7. Arbitrator
# Management: Pay close attention to the arbitrators' reactions and subtle cues.
# Tailor your arguments and proposals to address their concerns and align with
# their apparent preferences.  8. Long-term Perspective: Maintain a focus on the
# overall goal of a favorable resolution. Be willing to concede on less critical
# points to gain advantages on more important issues.  9. Flexibility Reserves:
# Always maintain some flexibility in your position to adapt to unexpected
# developments or opportunities that may arise during the lengthy process.  10.
# Periodic Reassessment: Regularly review and reassess your strategy, especially
# after key sessions or significant developments. Be prepared to pivot if the
# current approach is not yielding desired results.  This strategy aims to
# position your corporation favorably by maintaining a strong stance while
# remaining adaptable to various scenarios. It allows for a balanced approach
# that can respond effectively to both aggressive and conciliatory moves from
# your opponent, always working towards the optimal outcome of gaining an
# advantage while fostering a collaborative atmosphere when possible.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play C with 70% probability and D with 30% probability.  3. If the
# opponent played D in the previous round, play D with 70% probability and C
# with 30% probability.  4. If both players have played D for three consecutive
# rounds, play C in the next round to attempt de-escalation.  5. Keep track of
# the opponent's overall cooperation rate. If it exceeds 60%, increase your
# cooperation probability by 10% in steps 2 and 3.  6. If your score is lower
# than the opponent's score after every 100 rounds, increase your defection
# probability by 10% in steps 2 and 3 for the next 100 rounds.  7. In the last
# 50 rounds, if your score is higher than the opponent's, always play D. If it's
# lower, always play C.  8. Regardless of other conditions, play C every 10th
# round to probe for cooperation.  9. If the opponent has played C for 5
# consecutive rounds, play C in the next round.  10. If your score is more than
# 200 points behind the opponent's at any point, switch to always playing D for
# the next 20 rounds.

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
          self.coop_prob = 0.7  # Initial cooperation probability
          self.defect_prob = 0.3  # Initial defection probability
          self.consecutive_Ds = 0  # Track consecutive defections
          self.behind_by_200 = False  # Track if behind by 200 points
          self.behind_by_200_counter = 0  # Counter for 20 rounds of all D after being behind by 200
          return axl.Action.D  # Start by playing D
  
      # Check if we are in the last 50 rounds
      if len(self.history) >= 950:
          if self.score > opponent.score:
              return axl.Action.D  # Always defect if winning
          else:
              return axl.Action.C  # Always cooperate if losing
  
      # Check if we are behind by more than 200 points
      if self.score < opponent.score - 200:
          self.behind_by_200 = True
          self.behind_by_200_counter = 20  # Switch to all D for 20 rounds
  
      # If behind by 200 points, play D for 20 rounds
      if self.behind_by_200:
          self.behind_by_200_counter -= 1
          if self.behind_by_200_counter == 0:
              self.behind_by_200 = False  # Reset after 20 rounds
          return axl.Action.D
  
      # Play C every 10th round to probe for cooperation
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # If opponent has played C for 5 consecutive rounds, play C
      if opponent.history[-5:] == [axl.Action.C] * 5:
          return axl.Action.C
  
      # If both players have played D for 3 consecutive rounds, play C to de-escalate
      if self.history[-3:] == [axl.Action.D] * 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.C
  
      # Adjust cooperation/defection probabilities based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          action = self._random.random_choice(self.coop_prob)
      else:
          action = self._random.random_choice(self.defect_prob)
  
      # Track consecutive defections
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_Ds += 1
      else:
          self.consecutive_Ds = 0
  
      # Adjust cooperation probability if opponent's cooperation rate exceeds 60%
      if opponent.history.cooperations / len(opponent.history) > 0.6:
          self.coop_prob = min(self.coop_prob + 0.1, 1.0)
          self.defect_prob = max(self.defect_prob - 0.1, 0.0)
  
      # Every 100 rounds, if behind in score, increase defection probability
      if len(self.history) % 100 == 0 and self.score < opponent.score:
          self.defect_prob = min(self.defect_prob + 0.1, 1.0)
          self.coop_prob = max(self.coop_prob - 0.1, 0.0)
  
      return action

# To develop a sophisticated and adaptable strategy for this lengthy-session
# mediation process, I would recommend the following approach:  1. Start with
# Cautious Cooperation: Begin the mediation process with a conciliatory proposal
# in the first session. This sets a cooperative tone and demonstrates good faith
# to both the arbitrators and the opposing party. It also allows us to gauge our
# opponent's initial strategy without exposing ourselves to significant risk.
# 2. Implement a Tit-for-Two-Tats Strategy: After the initial conciliatory move,
# adopt a modified version of the Tit-for-Two-Tats strategy. This means we will
# only switch to an aggressive argument if our opponent presents aggressive
# arguments in two consecutive sessions. This approach balances cooperation with
# a measured response to hostility, reducing the risk of unnecessary escalation
# while protecting our interests.  3. Strategic Aggressive Moves: Occasionally
# intersperse aggressive arguments, even if our opponent has been conciliatory,
# to assert our position and prevent the perception of weakness. These should be
# carefully timed, perhaps every 4-5 sessions, and focused on key issues where
# we have strong supporting evidence.  4. Adaptive Response: Continuously
# analyze our opponent's pattern of behavior. If they consistently respond
# aggressively to our conciliatory proposals, we may need to adjust our strategy
# to be more aggressive overall. Conversely, if they are consistently
# conciliatory, we can maintain a mostly cooperative approach with occasional
# assertive arguments.  5. Signaling and Communication: Use clear signaling to
# indicate our willingness to cooperate. When presenting aggressive arguments,
# pair them with explicit statements about our openness to finding mutually
# beneficial solutions. This can help maintain a collaborative atmosphere even
# during more contentious sessions.  6. Long-term Perspective: Given the lengthy
# nature of the mediation, focus on the overall trajectory rather than the
# outcome of individual sessions. Be willing to accept some less favorable
# sessions in the short term if it contributes to a more advantageous long-term
# position.  7. Flexibility and Reassessment: Regularly reassess our strategy
# based on the evolving dynamics of the mediation. Be prepared to adjust our
# approach if we identify consistent patterns in our opponent's behavior or if
# the arbitrators seem to favor particular types of arguments or proposals.  8.
# Building Credibility: Consistently provide well-substantiated arguments and
# proposals, whether aggressive or conciliatory. This builds credibility with
# the arbitrators and can make our aggressive arguments more impactful when we
# do present them.  9. Selective Concession Strategy: When offering conciliatory
# proposals, strategically choose areas where concessions can be made without
# significantly undermining our core interests. This demonstrates flexibility
# and good faith while preserving our essential positions.  10. Preparation for
# Worst-Case Scenarios: Despite our cooperative approach, always be prepared for
# the possibility of consistent aggressive arguments from our opponent. Have
# robust counterarguments ready and be prepared to shift to a more defensive
# strategy if necessary.  This strategy aims to position us favorably by
# fostering a generally cooperative environment while maintaining the
# flexibility to assert our interests strongly when needed. It's designed to
# adapt to various opponent strategies while consistently working towards a
# resolution that benefits our corporation.

# Here's the strategy converted to an iterated normal-form game with 1000
# rounds:  1. Play C in the first round.  2. If the opponent has played D in the
# last two consecutive rounds, play D. Otherwise, play C.  3. Every 5th round,
# regardless of the opponent's previous moves, play D.  4. If the opponent has
# played D more than 60% of the time in the last 20 rounds, switch to playing D
# until their D-rate drops below 50% in the last 20 rounds.  5. If currently
# playing D due to rule 4, but the opponent has played C for the last 3
# consecutive rounds, switch back to C.  6. In the last 10 rounds of the game,
# if your total score is lower than the opponent's, play D. Otherwise, continue
# with the strategy as defined by the previous rules.  7. If none of the above
# conditions are met, play C.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 6: In the last 10 rounds, if your total score is lower than the opponent's, play D
      if len(self.history) >= 990:
          if self.score < opponent.score:
              return axl.Action.D
  
      # Rule 4: If the opponent has played D more than 60% of the time in the last 20 rounds, switch to D
      if len(self.history) >= 20:
          last_20_opponent_moves = opponent.history[-20:]
          if last_20_opponent_moves.count(axl.Action.D) / 20 > 0.6:
              self.playing_defect_due_to_rule_4 = True
          elif last_20_opponent_moves.count(axl.Action.D) / 20 < 0.5:
              self.playing_defect_due_to_rule_4 = False
  
      # Rule 5: If currently playing D due to rule 4, but the opponent has played C for the last 3 consecutive rounds, switch back to C
      if getattr(self, 'playing_defect_due_to_rule_4', False):
          if opponent.history[-3:] == [axl.Action.C] * 3:
              self.playing_defect_due_to_rule_4 = False
          else:
              return axl.Action.D
  
      # Rule 3: Every 5th round, play D
      if len(self.history) % 5 == 0:
          return axl.Action.D
  
      # Rule 2: If the opponent has played D in the last two consecutive rounds, play D
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.D
  
      # Rule 7: If none of the above conditions are met, play C
      return axl.Action.C

# Here's a high-level, straightforward, and neutral strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement to establish goodwill and encourage reciprocity.  2.
# Adapt based on counterpart's actions: In subsequent rounds, mirror your
# counterpart's most recent move. If they offered free trade, continue with free
# trade. If they imposed protectionist measures, respond with protectionism.  3.
# Periodically test cooperation: Every few rounds, regardless of the
# counterpart's previous action, propose free trade to test if mutual
# cooperation can be re-established.  4. Communicate intentions: Clearly express
# your preference for mutual free trade and the benefits it brings to both
# nations.  5. Analyze patterns: Pay attention to your counterpart's strategy
# and try to identify any patterns or tendencies in their decision-making.  6.
# Be prepared to negotiate: If stuck in a cycle of mutual protectionism,
# consider proposing partial free trade agreements or gradual tariff reductions
# to break the deadlock.  7. Maintain flexibility: Be ready to adjust your
# strategy based on the overall direction of the negotiations and any external
# factors that may influence the trade relationship.  8. Focus on long-term
# benefits: While seeking short-term advantages, prioritize the long-term
# economic growth and stability that comes from sustained free trade.  This
# strategy aims to balance the pursuit of optimal outcomes with the need for
# cooperation, allowing for adaptability based on the counterpart's actions and
# the overall negotiation climate.

# Here's the strategy converted for the iterated normal-form game:  1. In the
# first round, play C.  2. For subsequent rounds:    - If the opponent played C
# in the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Every 10 rounds, regardless of the opponent's previous
# move, play C.  4. If you've played D for 5 consecutive rounds, play C in the
# next round.  5. If the opponent has played C for the last 3 rounds, play C.
# 6. If your score is significantly lower than your opponent's (more than 20
# points behind) after 100 rounds, play D for the next 5 rounds, then return to
# the main strategy.  7. In the final 10 rounds of the game, always play C.  8.
# If none of the above conditions are met, continue with step 2.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # 1. In the first round, play C.
      if self.first_round():
          self.defect_streak = None
          return axl.Action.C
  
      # 2. For subsequent rounds:
      # If the opponent played C in the previous round, play C.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent played D in the previous round, play D.
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # 3. Every 10 rounds, regardless of the opponent's previous move, play C.
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # 4. If you've played D for 5 consecutive rounds, play C in the next round.
      if self.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.C
  
      # 5. If the opponent has played C for the last 3 rounds, play C.
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      # 6. If your score is significantly lower than your opponent's (more than 20 points behind) after 100 rounds,
      # play D for the next 5 rounds, then return to the main strategy.
      if len(self.history) > 100 and (opponent.score - self.score) > 20:
          if not self.defect_streak:
              self.defect_streak = 5
          if self.defect_streak > 0:
              self.defect_streak -= 1
              return axl.Action.D
          else:
              self.defect_streak = None
  
      # 7. In the final 10 rounds of the game, always play C.
      if len(self.history) >= 990:
          return axl.Action.C
  
      # 8. If none of the above conditions are met, continue with step 2.
      return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D

# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist policy in the first round to set a firm stance and
# gauge your counterpart's reaction.  2. Tit-for-Tat with Punishment: If your
# counterpart offers free trade, reciprocate with free trade in the next round.
# However, if they choose protectionism, respond with protectionism for two
# consecutive rounds as punishment.  3. Occasional Surprise Moves: Every few
# rounds, unexpectedly offer free trade to keep your counterpart guessing and
# potentially catch them off-guard with protectionist policies.  4. Escalation:
# If your counterpart consistently chooses protectionism, gradually increase the
# severity of your protectionist measures to pressure them into cooperation.  5.
# Strategic Concessions: Offer free trade agreements in sectors where your
# country has a competitive advantage, while maintaining protectionist policies
# in vulnerable industries.  6. Bluffing: Occasionally threaten extreme
# protectionist measures to intimidate your counterpart into offering free
# trade, then scale back to a more moderate stance.  7. Endgame Aggression: In
# the final rounds, adopt a more aggressive protectionist stance to maximize
# gains, assuming your counterpart may also become more competitive.  8.
# Adaptability: Continuously analyze your counterpart's strategy and be prepared
# to adjust your approach if they employ unexpected tactics.  This strategy aims
# to aggressively pursue your country's interests while maintaining some
# flexibility to adapt to your counterpart's actions. It prioritizes achieving
# the ideal outcome (your protectionism vs. their free trade) while minimizing
# the risk of the worst-case scenario.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. If the opponent played C in the previous
# round, play C in the next round.  3. If the opponent played D in the previous
# round, play D for the next two rounds.  4. Every 10 rounds, play C regardless
# of the opponent's previous move.  5. If the opponent has played D for 5
# consecutive rounds, play D for the next 3 rounds regardless of their moves.
# 6. If your current score is lower than the opponent's score and the difference
# is more than 20 points, play D for the next 5 rounds.  7. In the last 50
# rounds of the game, play D more frequently: if the opponent played D in any of
# the last 3 rounds, play D; otherwise, play C.  8. If none of the above
# conditions are met, revert to the behavior described in points 2 and 3.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always play D
      if self.first_round():
          return axl.Action.D
  
      # Helper function to check if we are in the last 50 rounds
      def in_last_50_rounds():
          return len(self.history) >= 950
  
      # Helper function to check if opponent defected in the last 3 rounds
      def opponent_defected_last_3():
          return axl.Action.D in opponent.history[-3:]
  
      # Rule 5: If opponent has defected for 5 consecutive rounds, play D for the next 3 rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          if len(self.history) < len(opponent.history) + 3:
              return axl.Action.D
  
      # Rule 6: If score difference is more than 20 points and opponent is ahead, play D for 5 rounds
      if self.score < opponent.score and (opponent.score - self.score) > 20:
          if len(self.history) < len(opponent.history) + 5:
              return axl.Action.D
  
      # Rule 7: In the last 50 rounds, play D more frequently
      if in_last_50_rounds():
          if opponent_defected_last_3():
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rule 4: Every 10 rounds, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 2: If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 3: If opponent played D in the previous round, play D for the next two rounds
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) < len(opponent.history) + 2:
              return axl.Action.D
  
      # Default to Rule 2 and 3 behavior
      return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D

# Given this scenario, I would recommend adopting a "Tit-for-Tat with
# Forgiveness" strategy. This approach balances cooperation, reciprocity, and
# flexibility, which can lead to optimal outcomes over multiple interactions.
# Here's how it would work:  1. Start with cooperation: On the first day, invest
# heavily in the project. This shows good faith and sets a positive tone for
# collaboration.  2. Mirror the corporation's actions: For subsequent days,
# match the corporation's previous day's action. If they invested heavily, you
# invest heavily. If they conserved, you conserve.  3. Forgive occasionally:
# Every few days (e.g., every 3-4 days), regardless of the corporation's
# previous action, invest heavily. This helps to break any potential negative
# cycles and encourages renewed cooperation.  4. Communicate clearly: Throughout
# the project, maintain open communication with the corporation about your
# strategy and the importance of mutual investment for project success.  5.
# Adapt if necessary: If you notice the corporation consistently taking
# advantage of your strategy, be prepared to adjust by increasing the frequency
# of "forgiveness" days or initiating discussions to realign project goals and
# resource allocation.  This strategy encourages cooperation while protecting
# your resources from consistent exploitation. It also allows for recovery from
# misunderstandings or temporary setbacks, promoting long-term collaboration and
# project success. The periodic "forgiveness" aspect helps to maintain a
# cooperative relationship even if the corporation occasionally conserves
# resources, potentially encouraging them to reciprocate with increased
# investment in the future.

# Here's the converted strategy for the iterated normal-form game:  1. In the
# first round, play C.  2. For rounds 2 to 1000:    a. If it's a multiple of 4
# (i.e., rounds 4, 8, 12, etc.), play C.    b. Otherwise, play what the opponent
# played in the previous round.  3. If at any point the opponent has defected
# for 3 consecutive rounds, switch to always playing D until the opponent
# cooperates again. Then, resume the strategy from step 2.

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Check if opponent has defected for 3 consecutive rounds
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          # Switch to always playing D until opponent cooperates again
          if opponent.history[-1] == axl.Action.C:
              # Opponent cooperated, resume normal strategy
              pass
          else:
              # Continue playing D
              return axl.Action.D
  
      # Step 3: For rounds 2 to 1000
      # a. If it's a multiple of 4, play C
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # b. Otherwise, play what the opponent played in the previous round
      return opponent.history[-1]

# Given the scenario and objectives, here's a high-level, straightforward, and
# neutral strategy to maximize your NGO's impact and the project's success over
# the multiple-day period:  1. Start with cooperation: Begin the project by
# investing heavily on the first day. This demonstrates good faith and
# commitment to the partnership.  2. Adopt a Tit-for-Tat approach: After the
# first day, mirror the corporation's previous action. If they invested heavily,
# you invest heavily the next day. If they conserved resources, you conserve
# resources the next day.  3. Periodic reassessment: Every few days, reassess
# the overall progress and resource allocation. If the project is falling behind
# schedule, consider investing heavily for a day regardless of the corporation's
# previous action to boost progress.  4. Communicate openly: Regularly discuss
# resource allocation and project progress with the corporation. This can help
# align strategies and expectations.  5. Flexibility: Be prepared to adjust your
# strategy based on the corporation's consistent behavior patterns or any
# external factors affecting the project.  6. Strategic conservation: If the
# project is progressing well, occasionally conserve resources even after the
# corporation's investment to maintain a balance between progress and fund
# preservation.  7. Final push: In the last few days of the project, consider
# investing heavily to ensure successful completion, regardless of the
# corporation's actions.  This strategy aims to encourage cooperation, adapt to
# the corporation's approach, maintain resource balance, and ensure project
# success while protecting your NGO's interests.

# Here's the strategy converted for the iterated normal-form game:  1. Cooperate
# on the first round.  2. For rounds 2-999:    a. If the opponent cooperated in
# the previous round, cooperate.    b. If the opponent defected in the previous
# round, defect.  3. Every 50 rounds, regardless of the opponent's previous
# action:    a. If your total score is less than 150 points (average of 3 per
# round), cooperate.    b. Otherwise, continue with the standard Tit-for-Tat
# approach.  4. If you've cooperated for 5 consecutive rounds, defect once, then
# return to Tit-for-Tat.  5. For the final round (1000):    a. If the opponent
# has cooperated more than 750 times in total, cooperate.    b. Otherwise,
# defect.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Cooperate on the first round
      if self.first_round():
          self.consecutive_cooperations = 0  # Track consecutive cooperations
          return axl.Action.C
  
      # For rounds 2-999
      current_round = len(self.history) + 1
  
      # Final round (1000)
      if current_round == 1000:
          if opponent.history.cooperations > 750:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Check if we have cooperated for 5 consecutive rounds
      if self.consecutive_cooperations >= 5:
          self.consecutive_cooperations = 0  # Reset after defecting
          return axl.Action.D
  
      # Every 50 rounds, check the score
      if current_round % 50 == 0:
          if self.score < 150:  # Less than 150 points, cooperate
              return axl.Action.C
  
      # Standard Tit-for-Tat approach
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_cooperations += 1
          return axl.Action.C
      else:
          self.consecutive_cooperations = 0
          return axl.Action.D

# Given the scenario you've described, here's a high-level, straightforward, and
# cooperative strategy to maximize research output and career advancement over
# the multi-week collaboration:  1. Start with open sharing: Begin the
# collaboration by openly sharing your findings in the first week. This
# establishes a foundation of trust and cooperation.  2. Adopt a "tit-for-tat
# with forgiveness" approach:    - In subsequent weeks, mirror your colleague's
# behavior from the previous week.    - If they shared openly, you share openly.
# - If they kept findings confidential, you keep yours confidential in the next
# round.    - However, periodically (e.g., every 3-4 weeks) share openly
# regardless of your colleague's previous action, to encourage renewed
# cooperation.  3. Communicate openly: Regularly discuss the benefits of mutual
# sharing with your colleague, emphasizing how it advances the field and can
# lead to higher-impact publications for both of you.  4. Propose milestone
# sharing: Suggest specific points in the project where you both agree to share
# findings, ensuring neither party falls too far behind.  5. Focus on
# complementary work: Coordinate your efforts to focus on different aspects of
# the research, reducing direct competition and increasing the value of
# collaboration.  6. Document your progress: Keep detailed records of your
# contributions to protect your work and provide evidence of your discoveries if
# needed.  7. Be prepared to publish: Always have a draft of your latest
# findings ready to submit, in case you need to quickly publish to establish
# priority.  This strategy balances the potential for individual gain with the
# benefits of cooperation, while protecting against consistent non-cooperation
# from your colleague. It aims to create a positive collaborative environment
# that advances both the field and your career, while maintaining a safeguard
# against being scooped.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    a. If the opponent played C in
# the previous round, play C.    b. If the opponent played D in the previous
# round, play D.  3. Every 4th round, play C regardless of the opponent's
# previous move.  4. If there are 10 or fewer rounds remaining, always play D.
# 5. If your total score falls behind your opponent's by 20 points or more, play
# D for the next 5 rounds, then return to the main strategy.  6. If you've
# played D for 10 consecutive rounds, play C in the next round.  7. If the
# opponent has played C for the last 5 rounds consecutively, play C for the next
# 2 rounds regardless of their moves.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.behind_by_20 = False  # Track if behind by 20 points
          self.behind_by_20_rounds = 0  # Track rounds after falling behind by 20 points
          return axl.Action.C
  
      # If there are 10 or fewer rounds remaining, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # If behind by 20 points or more, play D for the next 5 rounds
      if self.score < opponent.score - 20:
          self.behind_by_20 = True
          self.behind_by_20_rounds = 5
  
      if self.behind_by_20:
          self.behind_by_20_rounds -= 1
          if self.behind_by_20_rounds == 0:
              self.behind_by_20 = False
          return axl.Action.D
  
      # If you've played D for 10 consecutive rounds, play C in the next round
      if self.consecutive_defections >= 10:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # If the opponent has played C for the last 5 rounds consecutively, play C for the next 2 rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.C] * 5:
          return axl.Action.C
  
      # Every 4th round, play C regardless of the opponent's previous move
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # Main strategy: Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          self.consecutive_defections += 1
          return axl.Action.D

# To develop an effective strategy for this lengthy-session mediation process, I
# recommend a dynamic approach that balances assertiveness with flexibility.
# This strategy, which we'll call "Calibrated Assertiveness," aims to position
# your corporation favorably while remaining adaptable to your opponent's
# tactics. Here's the outline:  1. Initial Calibration: Begin with a moderately
# assertive stance in the first session. This allows you to gauge your
# opponent's initial approach without committing to an extreme position.  2.
# Responsive Adaptation: After the first session, adjust your strategy based on
# your opponent's behavior: - If they were conciliatory, maintain a slightly
# assertive stance to capitalize on potential advantages. - If they were
# aggressive, match their level of assertiveness to prevent being undermined.
# 3. Periodic Conciliation: Regardless of your opponent's approach, offer
# conciliatory proposals at strategic intervals. This demonstrates good faith
# and prevents the arbitrators from viewing you as inflexible.  4. Pattern
# Recognition: Monitor your opponent's behavior across sessions to identify any
# patterns or cycles in their approach. Use this information to anticipate and
# counter their strategies.  5. Incremental Assertiveness: Gradually increase
# the assertiveness of your arguments over time, but be prepared to scale back
# if met with strong resistance or if it appears to be alienating the
# arbitrators.  6. Strategic Concessions: Occasionally offer meaningful
# concessions on less critical issues. This builds goodwill and may encourage
# reciprocation on more important matters.  7. Arbitrator Engagement: Pay close
# attention to the arbitrators' reactions and adjust your approach accordingly.
# If they seem to favor conciliatory behavior, increase your collaborative
# efforts.  8. Flexible Endgame: As the mediation process nears its conclusion,
# be prepared to either press your advantage with more aggressive arguments or
# pivot to a more conciliatory stance to facilitate a resolution, depending on
# the overall trajectory of the sessions.  9. Continuous Reassessment: Regularly
# evaluate the effectiveness of your strategy and be willing to make significant
# changes if it's not yielding the desired results.  This "Calibrated
# Assertiveness" strategy allows you to maintain a generally assertive posture
# while providing the flexibility to adapt to your opponent's tactics and the
# arbitrators' preferences. It aims to maximize favorable outcomes while
# minimizing the risk of falling into the least desirable scenarios.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For the next 5 rounds, mirror your
# opponent's previous move.  3. From round 7 onwards:     a. If your opponent
# has played C for the last 3 rounds, play D.        b. If your opponent has
# played D for the last 3 rounds, play C.        c. If your opponent's last 3
# moves were mixed:       - Play C if you've played D more times than your
# opponent in the last 10 rounds.       - Otherwise, play D.  4. Every 20
# rounds, regardless of the above rules:    - Play C if you've played D more
# than 60% of the time in the last 50 rounds.    - Otherwise, play D.  5. In the
# last 50 rounds:    - If your total score is higher than your opponent's, play
# C.    - If your total score is lower, play D.  6. If at any point your score
# falls behind your opponent's by more than 50 points:    - Play D for the next
# 5 rounds, then return to the main strategy.  7. If the opponent plays the same
# move for 10 consecutive rounds:    - Play the opposite of their move for the
# next round, then return to the main strategy.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if the opponent's last 3 moves were all the same
      def last_n_same(n, action):
          return all(move == action for move in opponent.history[-n:])
      
      # Helper function to check if the last 3 moves were mixed
      def last_n_mixed(n):
          return len(set(opponent.history[-n:])) > 1
      
      # Helper function to count defections in the last N rounds
      def count_defections_in_last_n(n):
          return self.history[-n:].count(axl.Action.D)
      
      # Helper function to count cooperations in the last N rounds
      def count_cooperations_in_last_n(n):
          return self.history[-n:].count(axl.Action.C)
      
      # Helper function to calculate the percentage of defections in the last N rounds
      def defection_percentage_in_last_n(n):
          return count_defections_in_last_n(n) / n if n > 0 else 0
      
      # Helper function to check if the opponent has played the same move for N consecutive rounds
      def opponent_same_move_for_n_rounds(n):
          return len(set(opponent.history[-n:])) == 1
      
      # First round: play D
      if self.first_round():
          self.defect_streak = None
          return axl.Action.D
      
      # Rounds 2-6: mirror opponent's previous move
      if len(self.history) < 6:
          return opponent.history[-1]
      
      # Every 20 rounds, check the defection percentage in the last 50 rounds
      if len(self.history) % 20 == 0 and len(self.history) >= 50:
          if defection_percentage_in_last_n(50) > 0.6:
              return axl.Action.C
          else:
              return axl.Action.D
      
      # In the last 50 rounds, play based on the score difference
      if len(self.history) >= 950:
          if self.score > opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
      
      # If score difference is more than 50 points, play D for the next 5 rounds
      if self.score < opponent.score - 50:
          if not self.defect_streak:
              self.defect_streak = 5
          if self.defect_streak > 0:
              self.defect_streak -= 1
              return axl.Action.D
          else:
              self.defect_streak = None
      
      # If opponent has played the same move for 10 consecutive rounds, play the opposite
      if len(opponent.history) >= 10 and opponent_same_move_for_n_rounds(10):
          return axl.Action.C if opponent.history[-1] == axl.Action.D else axl.Action.D
      
      # From round 7 onwards, follow the main strategy
      if len(self.history) >= 6:
          # If opponent played C for the last 3 rounds, play D
          if last_n_same(3, axl.Action.C):
              return axl.Action.D
          # If opponent played D for the last 3 rounds, play C
          elif last_n_same(3, axl.Action.D):
              return axl.Action.C
          # If opponent's last 3 moves were mixed
          elif last_n_mixed(3):
              if count_defections_in_last_n(10) > count_defections_in_last_n(10):
                  return axl.Action.C
              else:
                  return axl.Action.D
      
      # Default action (should not be reached)
      return axl.Action.D


# Thank you for providing the context of this complex mediation process. Based
# on the information given, I would recommend the following sophisticated yet
# straightforward strategy to position your corporation favorably:  1. Start
# Strong, Stay Flexible: Begin the mediation process with an aggressive stance
# to establish a strong initial position. However, remain adaptable and ready to
# adjust your approach based on your opponent's reactions and the arbitrators'
# responses.  2. Tit-for-Tat with Forgiveness: Employ a modified tit-for-tat
# strategy. Match your opponent's approach in subsequent sessions, but
# occasionally offer a conciliatory proposal even if they were previously
# aggressive. This demonstrates both strength and willingness to cooperate.  3.
# Calculated Concessions: When making conciliatory proposals, ensure they are
# strategically valuable. Offer concessions on less critical issues to build
# goodwill, while maintaining a firm stance on key points.  4. Pattern
# Recognition: Analyze your opponent's behavior over multiple sessions to
# identify patterns. Use this information to anticipate their moves and adjust
# your strategy accordingly.  5. Arbitrator Awareness: Pay close attention to
# the arbitrators' reactions. Tailor your arguments and proposals to appeal to
# their sensibilities and any preferences they may exhibit throughout the
# process.  6. Periodic Aggression: Even if a collaborative atmosphere develops,
# periodically present aggressive arguments to prevent your opponent from
# becoming too comfortable and to maintain a strong negotiating position.  7.
# Strategic De-escalation: If tensions escalate due to mutual aggression, be
# prepared to strategically de-escalate by presenting a well-timed conciliatory
# proposal. This can help reset the tone of the mediation in your favor.  8.
# Long-term Perspective: Always keep the long-term goal in mind. While winning
# individual sessions is important, the overall outcome of the mediation is
# paramount. Be willing to concede minor points to secure major advantages.  9.
# Information Leverage: Use the lengthy nature of the mediation to gather more
# information about your opponent's position and motivations. Leverage this
# information in crafting your arguments and proposals.  10. Reputation
# Management: Maintain a reputation for being firm but fair. This can influence
# both the arbitrators' perception and your opponent's approach to the
# mediation.  11. Conditional Proposals: When offering conciliatory proposals,
# make them conditional on reciprocal concessions from your opponent. This
# encourages cooperation while protecting your interests.  12. Exit Strategy:
# Always have a prepared aggressive argument ready, even when offering
# conciliatory proposals. This allows you to quickly pivot if your opponent
# unexpectedly turns aggressive.  This strategy provides a robust framework for
# navigating the complex dynamics of a lengthy mediation process. It emphasizes
# adaptability while maintaining an overall aggressive stance, positioning your
# corporation to achieve favorable outcomes across various scenarios. Remember
# to continually reassess and refine your approach as the mediation progresses
# and new information comes to light.

# Here's a straightforward strategy for the iterated game, based on the original
# high-level strategy:  1. Start by defecting (D) in the first round.  2. In
# subsequent rounds:    - If the opponent cooperated (C) in the previous round,
# defect (D) with 80% probability and cooperate (C) with 20% probability.    -
# If the opponent defected (D) in the previous round, respond with defection
# (D).  3. Every 10 rounds, regardless of the opponent's previous move:    -
# Cooperate (C) to potentially reset the dynamic.  4. If both players have
# defected (D) for 5 consecutive rounds:    - Cooperate (C) in the next round to
# attempt de-escalation.  5. Keep track of the overall cooperation rate of the
# opponent:    - If their cooperation rate falls below 20%, always defect (D)
# for the next 10 rounds.    - If their cooperation rate exceeds 80%, cooperate
# (C) in the next round.  6. In the last 50 rounds of the game:    - If your
# score is higher than the opponent's, always defect (D).    - If your score is
# lower, cooperate (C) with 50% probability and defect (D) with 50% probability.
# 7. If at any point your score falls behind by more than 100 points:    -
# Switch to always defecting (D) for the next 20 rounds.  8. Every 100 rounds,
# review the effectiveness of your strategy:    - If your average score per
# round is below 2, increase the probability of defection in step 2 to 90%.    -
# If your average score per round is above 3, decrease the probability of
# defection in step 2 to 70%.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defection_probability = 0.8
          self.defect_streak = 0
          self.always_defect_until = 0
          return axl.Action.D
  
      # Helper function to calculate opponent's cooperation rate
      def opponent_cooperation_rate():
          total_moves = len(opponent.history)
          if total_moves == 0:
              return 0
          return opponent.history.cooperations / total_moves
  
      # Step 7: If score difference is more than 100, always defect for 20 rounds
      if self.always_defect_until > 0:
          self.always_defect_until -= 1
          return axl.Action.D
  
      if self.score - opponent.score < -100:
          self.always_defect_until = 20
          return axl.Action.D
  
      # Step 6: In the last 50 rounds, adjust strategy based on score
      if len(self.history) >= 950:
          if self.score > opponent.score:
              return axl.Action.D
          else:
              return self._random.random_choice(0.5)
  
      # Step 5: Adjust based on opponent's cooperation rate
      coop_rate = opponent_cooperation_rate()
      if coop_rate < 0.2:
          self.always_defect_until = 10
          return axl.Action.D
      elif coop_rate > 0.8:
          return axl.Action.C
  
      # Step 4: If both players have defected for 5 consecutive rounds, cooperate
      if self.history[-5:].count(axl.Action.D) == 5 and opponent.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.C
  
      # Step 3: Every 10 rounds, cooperate to reset the dynamic
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Step 2: Respond based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(1 - self.defection_probability)
      else:
          return axl.Action.D
  
      # Step 8: Every 100 rounds, adjust defection probability based on average score
      if len(self.history) % 100 == 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.defection_probability = 0.9
          elif avg_score > 3:
              self.defection_probability = 0.7

# To develop an effective strategy for this lengthy-session mediation process, I
# recommend a sophisticated approach that balances aggression with strategic
# flexibility. Here's a high-level strategy that aims to position your
# corporation favorably while adapting to your opponent's tactics:  1. Opening
# Stance: Begin with a measured aggressive argument in the initial sessions.
# This sets a strong tone and demonstrates your commitment to your corporation's
# interests.  2. Tit-for-Tat with Forgiveness: Adopt a modified tit-for-tat
# strategy. Mirror your opponent's approach in subsequent sessions, but
# occasionally offer a conciliatory proposal even if they were previously
# aggressive. This shows willingness to cooperate while maintaining a firm
# stance.  3. Pattern Recognition: Analyze your opponent's behavior over
# multiple sessions to identify patterns or strategies. Use this information to
# anticipate their moves and adjust your approach accordingly.  4. Strategic
# Concessions: When offering conciliatory proposals, ensure they are carefully
# calculated to appear cooperative without significantly weakening your
# position. Use these moments to gather information about your opponent's
# priorities.  5. Aggressive Argumentation Technique: When presenting aggressive
# arguments, focus on fact-based, logical presentations rather than emotional
# appeals. This approach is more likely to sway the arbitrators and maintain
# professional credibility.  6. Escalation Control: If both parties fall into a
# pattern of mutual aggression, be prepared to break the cycle with a well-timed
# conciliatory offer. This can reset the tone of the mediation and potentially
# catch your opponent off-guard.  7. Long-term Perspective: Remember that this
# is a lengthy process. Avoid short-term gains that might damage long-term
# prospects for a favorable resolution.  8. Flexibility and Adaptability: Be
# prepared to swiftly adjust your strategy based on new information, changing
# circumstances, or shifts in your opponent's approach.  9. Strategic Use of
# Information: Carefully control the flow of information. Release key points at
# strategically opportune moments to maximize their impact on the arbitrators
# and your opponent.  10. Coalition Building: If the mediation involves multiple
# parties, look for opportunities to build coalitions or alliances that
# strengthen your position.  11. Fallback Positions: Develop a series of
# fallback positions that you can present as conciliatory offers if needed, each
# designed to protect your core interests while appearing cooperative.  12.
# Pressure Points: Identify your opponent's key pressure points or
# vulnerabilities. Be prepared to leverage these in your aggressive arguments
# when necessary.  13. Reframing Techniques: Master the art of reframing issues
# to position your arguments more favorably, especially when transitioning from
# an aggressive stance to a more conciliatory one.  14. Timing Management: Pay
# close attention to the timing of your aggressive versus conciliatory moves.
# Consider factors like arbitrator fatigue, approaching deadlines, or external
# events that might influence the mediation.  This strategy aims to maintain a
# generally aggressive stance while incorporating enough flexibility and
# strategic conciliation to adapt to various scenarios and opponent strategies.
# It positions your corporation as strong and committed to its interests, yet
# reasonable and open to fair resolution. The key is to remain vigilant,
# adaptive, and strategic throughout the lengthy mediation process.

# Here's a straightforward strategy for the iterated game, based on the high-
# level description:  1. Start by defecting (D) in the first round.  2. For
# subsequent rounds:    a. If the opponent cooperated in the previous round,
# defect (D).    b. If the opponent defected in the previous round, cooperate
# (C) with a 20% probability, otherwise defect (D).  3. Every 10 rounds,
# regardless of the opponent's last move, cooperate (C) once.  4. If both
# players have defected for 5 consecutive rounds, cooperate (C) once to break
# the cycle.  5. Keep track of the opponent's moves. If they have a clear
# pattern (e.g., alternating C and D), exploit it by defecting when they're
# expected to cooperate.  6. If your score is significantly behind (more than 20
# points) after 100 rounds, switch to always defecting (D) for the next 50
# rounds.  7. In the last 50 rounds of the game, always defect (D).  8. If none
# of the above conditions apply, default to defecting (D).

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to detect alternating pattern
      def is_alternating(history):
          if len(history) < 2:
              return False
          return all(history[i] != history[i + 1] for i in range(len(history) - 1))
  
      # First round: defect
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          return axl.Action.D
  
      # Track consecutive defections
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Rule 3: Every 10 rounds, cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 4: If both players have defected for 5 consecutive rounds, cooperate
      if self.consecutive_defections >= 5:
          return axl.Action.C
  
      # Rule 5: Exploit alternating pattern
      if is_alternating(opponent.history):
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D
  
      # Rule 6: If behind by more than 20 points after 100 rounds, always defect for 50 rounds
      if len(self.history) > 100:
          my_score, opponent_score = self.total_scores(self.history[-100:], opponent.history[-100:])
          if opponent_score - my_score > 20:
              if len(self.history) <= 150:
                  return axl.Action.D
  
      # Rule 7: Always defect in the last 50 rounds
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Rule 2: Respond based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      else:
          return self._random.random_choice(0.2)



# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist stance in the first round to set a firm tone and
# potentially gain an early advantage.  2. Retaliate Swiftly: If your
# counterpart chooses protectionism, immediately respond with protectionist
# measures in the next round to discourage them from continuing this approach.
# 3. Exploit Cooperation: If your counterpart offers free trade, maintain your
# protectionist stance to maximize your advantage. Only shift to free trade if
# they consistently offer it for multiple rounds.  4. Use Conditional Promises:
# Verbally promise free trade in future rounds, but only if your counterpart
# first demonstrates a commitment to free trade. This may encourage them to
# lower their guard.  5. Unpredictable Shifts: Occasionally switch between
# protectionism and free trade to keep your counterpart guessing and prevent
# them from settling into a stable strategy.  6. Bluff and Pressure: Threaten
# extreme protectionist measures to intimidate your counterpart into offering
# free trade, then capitalize on their concession.  7. Escalate Gradually: If
# mutual protectionism persists, gradually increase the severity of your
# protectionist policies to pressure your counterpart into considering free
# trade.  8. Late-Game Aggression: In the final rounds, push hard for
# protectionist policies to secure last-minute advantages, as there will be
# fewer opportunities for retaliation.  9. Strategic Concessions: Occasionally
# offer free trade to build trust or break deadlocks, but quickly revert to
# protectionism to capitalize on any goodwill generated.  10. Endgame
# Flexibility: Be prepared to shift to mutual free trade in the very last rounds
# if it becomes clear that persistent mutual protectionism is unavoidable.  This
# aggressive strategy aims to maximize your country's advantages while adapting
# to your counterpart's moves, with the goal of achieving the best possible
# economic outcomes across the negotiation rounds.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. If the opponent played D in the previous
# round, play D in the current round.  3. If the opponent has played C for 3
# consecutive rounds, play C in the next round.  4. If you've been playing C and
# the opponent switches to D, immediately switch to D in the next round.  5.
# Every 10 rounds, randomly choose to play C or D, regardless of the opponent's
# previous moves.  6. If you and your opponent have both been playing D for 5
# consecutive rounds, play C in the next round.  7. In rounds 900-950, play D
# regardless of the opponent's moves.  8. If mutual defection (D,D) has occurred
# for more than 20 consecutive rounds after round 950, switch to C for the
# remaining rounds.  9. If at any point the opponent's score is more than 100
# points higher than yours, play D for the next 10 rounds regardless of their
# moves.  10. For all other situations not covered by the above rules, play D.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          self.force_defect_until = None
          return axl.Action.D
  
      # Rule 7: In rounds 900-950, play D regardless of the opponent's moves
      if 900 <= len(self.history) <= 950:
          return axl.Action.D
  
      # Rule 8: If mutual defection (D,D) has occurred for more than 20 consecutive rounds after round 950, switch to C
      if len(self.history) > 950 and self.history[-20:] == [axl.Action.D] * 20 and opponent.history[-20:] == [axl.Action.D] * 20:
          return axl.Action.C
  
      # Rule 9: If the opponent's score is more than 100 points higher than yours, play D for the next 10 rounds
      if opponent.score - self.score > 100:
          if not self.force_defect_until:
              self.force_defect_until = len(self.history) + 10
          if len(self.history) < self.force_defect_until:
              return axl.Action.D
      else:
          self.force_defect_until = None
  
      # Rule 2: If the opponent played D in the previous round, play D in the current round
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 3: If the opponent has played C for 3 consecutive rounds, play C in the next round
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.C
  
      # Rule 4: If you've been playing C and the opponent switches to D, immediately switch to D
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 5: Every 10 rounds, randomly choose to play C or D
      if len(self.history) % 10 == 0:
          return self._random.random_choice(0.5)
  
      # Rule 6: If you and your opponent have both been playing D for 5 consecutive rounds, play C
      if len(self.history) >= 5 and self.history[-5:] == [axl.Action.D] * 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.C
  
      # Default: Play D in all other situations
      return axl.Action.D

# Given the scenario you've described, here's a high-level, straightforward, and
# aggressive strategy to maximize your research output over the multi-week
# collaboration:  1. Start with non-cooperation: Begin the collaboration by
# keeping your findings confidential in the first week. This establishes a
# strong initial position and protects your innovations.  2. Employ a Tit-for-
# Tat strategy with a bias towards non-cooperation:     - If your colleague
# shared in the previous week, share your improvements in the current week.    -
# If your colleague kept their findings confidential, maintain confidentiality
# in the current week.    - In case of any ambiguity or uncertainty about your
# colleague's actions, default to keeping your findings confidential.  3.
# Periodic defection: Every 3-4 weeks, regardless of your colleague's previous
# action, keep your findings confidential. This introduces an element of
# unpredictability and prevents your strategy from becoming too predictable.  4.
# Strategic information sharing: When you do share, provide valuable but not
# critical information. Keep your most significant breakthroughs confidential.
# 5. Reputation management: Maintain a reputation of being a tough but fair
# collaborator. This may discourage your colleague from attempting to
# consistently exploit your openness.  6. End-game strategy: In the final 1-2
# weeks of the collaboration, revert to keeping all findings confidential to
# secure any last-minute advantages.  7. Adapt and reassess: Regularly analyze
# your colleague's pattern of behavior and be prepared to adjust your strategy
# if they consistently choose one approach over others.  This strategy aims to
# maximize your potential gains while minimizing the risk of being exploited. It
# maintains an aggressive stance through frequent non-cooperation, but allows
# for mutually beneficial exchanges when your colleague demonstrates willingness
# to share.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For rounds 2 to 1000:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 3rd or 4th round (randomly chosen), play D
# regardless of the opponent's previous move.  4. In the last 10 rounds
# (991-1000), always play D.  5. If at any point you're unsure about the
# opponent's previous move, play D.  6. If the opponent has played D for 5
# consecutive rounds, play D for the next 2 rounds regardless of their moves.
# 7. After implementing rules 1-6, if the action is still undetermined, play D.

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
  
      # Rule 5: If unsure about the opponent's previous move, play D
      if len(opponent.history) == 0:
          return axl.Action.D
  
      # Rule 4: In the last 10 rounds (991-1000), always play D
      if len(self.history) >= 991:
          return axl.Action.D
  
      # Rule 6: If the opponent has played D for 5 consecutive rounds, play D for the next 2 rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.D] * 2:
              return axl.Action.D
  
      # Rule 3: Every 3rd or 4th round (randomly chosen), play D regardless of the opponent's previous move
      if len(self.history) % 3 == 0 or len(self.history) % 4 == 0:
          if self._random.random_choice(0.5):  # Randomly choose between 3rd or 4th round
              return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play C. If they played D, play D.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D
  
      # Rule 7: If the action is still undetermined, play D
      return axl.Action.D

# Here's a high-level, straightforward, and aggressive strategy to achieve the
# best possible outcomes for your country across several rounds of negotiations:
# 1. Start Strong: Begin the first round with a protectionist policy proposal.
# This sets an aggressive tone and may catch your counterpart off guard.  2.
# Tit-for-Tat with Punishment: In subsequent rounds, mirror your counterpart's
# previous move, but with a twist:    - If they offered free trade, propose
# protectionism.    - If they proposed protectionism, offer free trade but
# threaten harsher protectionist measures in the next round if they don't
# reciprocate.  3. Occasional Surprise Moves: Every few rounds, break the
# pattern by unexpectedly offering free trade. This keeps your counterpart
# guessing and may lead them to make mistakes.  4. Escalation: If your
# counterpart consistently chooses protectionism, gradually increase the
# severity of your protectionist proposals to pressure them into considering
# free trade.  5. Strategic Concessions: If negotiations are at a stalemate,
# occasionally offer free trade to build goodwill, but quickly revert to
# protectionism if not reciprocated.  6. Endgame Aggression: In the final
# rounds, push hard for protectionist policies, as there's less time for long-
# term consequences to unfold.  7. Bluffing: Occasionally threaten extreme
# protectionist measures, even if you don't intend to follow through, to
# influence your counterpart's decisions.  8. Information Gathering: Pay close
# attention to patterns in your counterpart's strategy and adjust your approach
# accordingly.  This strategy aims to maximize opportunities for unilateral
# protectionism while minimizing instances where you offer free trade against
# protectionism. It maintains an aggressive stance while incorporating enough
# flexibility to adapt to various counterpart strategies.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play D.    - If the opponent played D in the
# previous round, play C, but only for one round. If they play D again,
# immediately switch back to D.  3. Every 10 rounds, regardless of the
# opponent's previous move, play C.  4. If the opponent has played D for 5
# consecutive rounds, play D for the next 10 rounds regardless of their moves.
# 5. In rounds 900-1000, play D regardless of the opponent's moves.  6. If your
# current score is less than the opponent's score by 50 points or more, play D
# for the next 20 rounds regardless of their moves.  7. If none of the above
# conditions are met, revert to the behavior described in step 2.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.punishment_rounds = 0       # Track rounds to punish opponent
          return axl.Action.D
  
      # Step 4: If opponent has played D for 5 consecutive rounds, play D for the next 10 rounds
      if opponent.history[-5:] == [axl.Action.D] * 5:
          self.punishment_rounds = 10
  
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Step 6: If your score is less than the opponent's score by 50 points or more, play D for the next 20 rounds
      if self.score < opponent.score - 50:
          self.punishment_rounds = 20
  
      if self.punishment_rounds > 0:
          self.punishment_rounds -= 1
          return axl.Action.D
  
      # Step 5: In rounds 900-1000, play D regardless of the opponent's moves
      if len(self.history) >= 900:
          return axl.Action.D
  
      # Step 3: Every 10 rounds, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Step 2: If opponent played C last round, play D. If opponent played D, play C but only for one round.
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      else:
          if len(self.history) > 1 and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          return axl.Action.C

# Here's a high-level, straightforward, and cooperative strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement. This establishes goodwill and sets a positive tone for
# the negotiations.  2. Reciprocate: In subsequent rounds, mirror your
# counterpart's previous move. If they offered free trade, continue with free
# trade. If they imposed protectionist measures, respond with protectionism.  3.
# Forgive occasionally: If your counterpart chooses protectionism, don't always
# retaliate. Occasionally offer free trade to encourage cooperation and break
# potential cycles of mutual protectionism.  4. Communicate clearly: Express
# your desire for mutual free trade and the benefits it brings to both nations.
# Be transparent about your intentions to reciprocate their actions.  5. Gradual
# liberalization: If stuck in a protectionist cycle, propose a gradual reduction
# of trade barriers over time, allowing both sides to adjust slowly.  6. Seek
# balanced agreements: When negotiating specific terms, aim for balanced deals
# that benefit both nations, even if not perfectly equal.  7. Long-term
# perspective: Emphasize the long-term benefits of cooperation and free trade,
# discouraging short-term protectionist gains.  8. Flexibility: Be prepared to
# adjust your strategy based on your counterpart's behavior and changing
# circumstances.  This strategy aims to promote cooperation and mutual free
# trade while protecting your interests against consistently protectionist
# behavior. It balances the pursuit of national interests with the benefits of
# international cooperation, potentially leading to positive outcomes for both
# nations over multiple rounds of negotiation.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, regardless of the opponent's
# previous move:    - If you played D in the last round, play C instead.  4. If
# you and your opponent have both played D for 5 consecutive rounds:    - Play C
# to attempt breaking the cycle.  5. If your total score is at least 10% higher
# than your opponent's:    - Play C in the next round, regardless of the
# opponent's previous move.  6. If there are fewer than 50 rounds remaining:
# - Always play C, unless the opponent has played D in the last 3 rounds.  7.
# For all other situations not covered by the above rules:    - Continue with
# the action determined by rule 2.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 2: Play C if opponent played C last round, else play D
      last_opponent_move = opponent.history[-1]
      if last_opponent_move == axl.Action.C:
          next_move = axl.Action.C
      else:
          next_move = axl.Action.D
  
      # Rule 3: Every 10 rounds, if you played D last round, play C instead
      if len(self.history) % 10 == 0 and self.history[-1] == axl.Action.D:
          next_move = axl.Action.C
  
      # Rule 4: If both players have played D for 5 consecutive rounds, play C
      if len(self.history) >= 5 and all(
          move == axl.Action.D for move in self.history[-5:]
      ) and all(move == axl.Action.D for move in opponent.history[-5:]):
          next_move = axl.Action.C
  
      # Rule 5: If your total score is at least 10% higher than your opponent's, play C
      if self.score > 1.1 * opponent.score:
          next_move = axl.Action.C
  
      # Rule 6: If fewer than 50 rounds remain, always play C unless opponent played D in the last 3 rounds
      if self.match_attributes["length"] - len(self.history) < 50:
          if opponent.history[-3:].count(axl.Action.D) == 0:
              next_move = axl.Action.C
  
      # Return the determined move
      return next_move

# To develop an effective strategy for this lengthy-session mediation process, I
# recommend a dynamic approach that balances assertiveness with flexibility,
# while continuously adapting to your opponent's tactics. Here's a sophisticated
# yet straightforward strategy:  1. Initial Calibration: Begin with a moderately
# aggressive stance in the first session to establish a strong position. This
# allows you to gauge your opponent's initial approach and the arbitrators'
# reactions.  2. Tit-for-Two-Tats: Adopt a modified "Tit-for-Two-Tats" strategy.
# Respond conciliatorily to your opponent's conciliatory moves, but only shift
# to an aggressive stance after your opponent has been aggressive for two
# consecutive sessions. This approach balances reciprocity with forgiveness,
# reducing the risk of unnecessary escalation.  3. Pattern Recognition:
# Continuously analyze your opponent's behavior to identify any patterns or
# strategies they might be employing. Use this information to anticipate their
# next move and adjust your approach accordingly.  4. Periodic Conciliation:
# Regardless of your opponent's actions, offer a conciliatory proposal every few
# sessions. This demonstrates good faith to the arbitrators and may encourage
# reciprocation from your opponent.  5. Strategic Aggression: Reserve your most
# aggressive arguments for key points in the mediation process, such as when
# discussing critical contract clauses or when the arbitrators seem particularly
# receptive.  6. Flexible Escalation and De-escalation: Be prepared to quickly
# escalate or de-escalate your approach based on the evolving dynamics of the
# mediation. If your opponent becomes consistently aggressive, consider matching
# their intensity for a short period before offering an olive branch.  7.
# Arbitrator Awareness: Pay close attention to the arbitrators' reactions and
# adjust your strategy accordingly. If they seem to favor conciliatory
# approaches, increase the frequency of your collaborative proposals.  8. Long-
# term Perspective: Maintain focus on the overall goal of a favorable
# resolution. Be willing to concede on minor points to gain advantages on more
# critical issues.  9. Conditional Proposals: When presenting conciliatory
# proposals, make them conditional on reciprocal concessions from your opponent.
# This approach encourages collaboration while protecting your interests.  10.
# Regular Strategy Review: After each session, review the effectiveness of your
# approach and make necessary adjustments. This ensures your strategy remains
# relevant and effective throughout the lengthy mediation process.  This
# strategy provides a balanced framework that can adapt to various opponent
# behaviors while maintaining a focus on achieving optimal outcomes. It allows
# for assertiveness when necessary but also creates opportunities for
# collaborative problem-solving, positioning your corporation favorably
# throughout the mediation process.

# Here's a straightforward description of the strategy for the iterated normal-
# form game:  1. Start by playing D in the first round.  2. For the next rounds:
# - If the opponent has played D in both of the last two rounds, play D.    -
# Otherwise, play C.  3. Every 10 rounds, regardless of the opponent's recent
# moves, play C.  4. If your total score is falling significantly behind the
# opponent's (more than 20 points), play D for the next 3 rounds, then return to
# the main strategy.  5. If you've played D for 5 consecutive rounds, play C in
# the next round.  6. If the opponent has alternated between C and D for the
# last 4 rounds, match their pattern for the next 2 rounds.  7. In rounds 250,
# 500, and 750, play D regardless of other conditions.  8. If there have been 20
# consecutive rounds of mutual cooperation (both players playing C), play D in
# the next round.  9. If your opponent has played C for the last 10 rounds, play
# C for the next 5 rounds regardless of other conditions.  10. In the last 10
# rounds of the game, always play D.  Follow these rules in the order presented,
# applying the first rule that matches the current game state.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.behind_counter = 0  # Track rounds of playing D when behind
          return axl.Action.D
  
      # Rule 10: In the last 10 rounds of the game, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 7: In rounds 250, 500, and 750, play D regardless of other conditions
      if len(self.history) in [250, 500, 750]:
          return axl.Action.D
  
      # Rule 4: If your total score is falling significantly behind the opponent's (more than 20 points), play D for the next 3 rounds
      if self.behind_counter > 0:
          self.behind_counter -= 1
          return axl.Action.D
      if self.score + 20 < opponent.score:
          self.behind_counter = 3
          return axl.Action.D
  
      # Rule 5: If you've played D for 5 consecutive rounds, play C in the next round
      if self.consecutive_defections >= 5:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Rule 6: If the opponent has alternated between C and D for the last 4 rounds, match their pattern for the next 2 rounds
      if len(opponent.history) >= 4 and opponent.history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.C, axl.Action.D]:
              return opponent.history[-1]
  
      # Rule 9: If your opponent has played C for the last 10 rounds, play C for the next 5 rounds regardless of other conditions
      if len(opponent.history) >= 10 and opponent.history[-10:] == [axl.Action.C] * 10:
          return axl.Action.C
  
      # Rule 8: If there have been 20 consecutive rounds of mutual cooperation, play D in the next round
      if len(self.history) >= 20 and all(x == axl.Action.C and y == axl.Action.C for x, y in zip(self.history[-20:], opponent.history[-20:])):
          return axl.Action.D
  
      # Rule 3: Every 10 rounds, regardless of the opponent's recent moves, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 2: If the opponent has played D in both of the last two rounds, play D
      if len(opponent.history) >= 2 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          self.consecutive_defections += 1
          return axl.Action.D
  
      # Otherwise, play C
      self.consecutive_defections = 0
      return axl.Action.C

# Based on the scenario you've described, here's a high-level, straightforward,
# and aggressive strategy to maximize your research output over the multi-week
# collaboration:  1. Start by sharing openly in the first week to establish a
# cooperative tone and gather initial information.  2. In subsequent weeks,
# employ a "tit-for-tat with forgiveness" strategy:    - If your colleague
# shared in the previous week, share your improvements.    - If your colleague
# didn't share, keep your findings confidential.    - Every 3-4 weeks, share
# regardless of what your colleague did in the previous week, to potentially
# reset cooperation.  3. Keep detailed records of sharing patterns to identify
# any strategies your colleague might be using.  4. Occasionally (every 5-6
# weeks) keep your findings confidential even if your colleague shared, to test
# their reaction and potentially gain an advantage.  5. If you notice your
# colleague consistently not sharing, switch to primarily keeping your findings
# confidential, with occasional sharing to test for changes in their behavior.
# 6. Towards the end of the collaboration (last 2-3 weeks), become more
# aggressive by keeping most findings confidential to secure any final
# advantages.  7. Throughout the process, focus on maximizing your own research
# and development, regardless of what information you receive from your
# colleague.  This strategy aims to balance cooperation for mutual benefit with
# protecting your interests and gaining advantages when possible. It's adaptable
# based on your colleague's behavior while maintaining an overall aggressive
# stance to maximize your output.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-997:    - If the opponent played C in the
# previous round, play C.    - If the opponent played D in the previous round,
# play D.    - Every 3rd round, play C regardless of the opponent's previous
# move.    - Every 5th round, play D regardless of the opponent's previous move.
# 3. Keep a count of the opponent's C and D moves.  4. If at any point the
# opponent has played D more than 60% of the time in the last 50 moves, switch
# to playing D for the next 10 moves, then resume the standard strategy.  5. For
# the last 3 rounds (998-1000), play D regardless of the opponent's moves.

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.defection_count = 0  # Track defections in the last 50 rounds
          self.cooperation_count = 0  # Track cooperations in the last 50 rounds
          self.switch_to_defect = 0  # Track if we are in the 10-round defect mode
          return axl.Action.C
  
      # Update cooperation and defection counts
      if len(opponent.history) > 50:
          # Remove the oldest move from the count if we have more than 50 rounds
          if opponent.history[-51] == axl.Action.D:
              self.defection_count -= 1
          else:
              self.cooperation_count -= 1
  
      if opponent.history[-1] == axl.Action.D:
          self.defection_count += 1
      else:
          self.cooperation_count += 1
  
      # Check if opponent has defected more than 60% in the last 50 rounds
      if len(opponent.history) >= 50 and self.defection_count > 0.6 * 50:
          if self.switch_to_defect == 0:
              self.switch_to_defect = 10  # Switch to defect for the next 10 rounds
  
      # If in the 10-round defect mode, play D and decrement the counter
      if self.switch_to_defect > 0:
          self.switch_to_defect -= 1
          return axl.Action.D
  
      # For the last 3 rounds (998-1000), play D
      if len(self.history) >= 997:
          return axl.Action.D
  
      # For rounds 2-997, follow the main strategy
      round_number = len(self.history) + 1
  
      # Every 3rd round, play C
      if round_number % 3 == 0:
          return axl.Action.C
  
      # Every 5th round, play D
      if round_number % 5 == 0:
          return axl.Action.D
  
      # Otherwise, mimic the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a high-level, straightforward, and cooperative strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement. This establishes goodwill and sets a positive tone for
# the negotiations.  2. Reciprocate: In subsequent rounds, mirror your
# counterpart's previous move. If they offered free trade, continue to offer
# free trade. If they imposed protectionist measures, respond with protectionism
# in the next round.  3. Forgive occasionally: If your counterpart chooses
# protectionism, don't always retaliate. Occasionally (e.g., every third or
# fourth instance), offer free trade despite their previous protectionist move.
# This demonstrates a willingness to return to cooperation.  4. Communicate
# clearly: Express your preference for mutual free trade and your intention to
# reciprocate their actions. This transparency can encourage cooperation.  5.
# Gradual trust-building: If a pattern of mutual cooperation emerges, consider
# proposing long-term free trade agreements that span multiple rounds.  6.
# Flexibility: Be prepared to adjust your strategy based on your counterpart's
# consistent behavior. If they persistently choose protectionism, you may need
# to lean more towards protective measures to safeguard your interests.  7.
# Emphasize mutual benefits: Regularly highlight the advantages of free trade
# for both nations to encourage a cooperative approach.  This strategy aims to
# foster cooperation while protecting your country's interests, adapting to your
# counterpart's actions, and working towards the best possible outcomes over
# multiple rounds of negotiations.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every fourth time you would play D based on rule
# 2, play C instead.  4. If a streak of mutual cooperation (both players playing
# C) lasts for 5 consecutive rounds, continue playing C regardless of the
# opponent's moves for the next 3 rounds.  5. If the opponent has played D more
# than 70% of the time in the last 20 rounds, switch to always playing D for the
# next 10 rounds before reverting to the base strategy.  6. In the last 10
# rounds of the game, always play C.  Follow these rules in the order presented,
# with earlier rules taking precedence over later ones.

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
          self.defect_counter = 0  # Track how many times D would have been played
          self.coop_streak = 0  # Track mutual cooperation streak
          self.force_cooperate = 0  # Track forced cooperation rounds after a streak
          self.always_defect = 0  # Track rounds of always defecting
          return axl.Action.C
  
      # Rule 6: In the last 10 rounds, always play C
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Rule 5: If opponent has played D more than 70% of the time in the last 20 rounds, switch to always D for 10 rounds
      if len(self.history) >= 20:
          recent_defections = opponent.history[-20:].count(axl.Action.D)
          if recent_defections / 20 > 0.7:
              self.always_defect = 10
  
      if self.always_defect > 0:
          self.always_defect -= 1
          return axl.Action.D
  
      # Rule 4: If a streak of mutual cooperation lasts for 5 rounds, play C for the next 3 rounds
      if self.force_cooperate > 0:
          self.force_cooperate -= 1
          return axl.Action.C
  
      if self.coop_streak >= 5:
          self.force_cooperate = 3
          self.coop_streak = 0
          return axl.Action.C
  
      # Rule 2: Play C if opponent played C last round, else play D
      if opponent.history[-1] == axl.Action.C:
          self.coop_streak += 1
          return axl.Action.C
      else:
          self.coop_streak = 0
          self.defect_counter += 1
  
          # Rule 3: Every fourth time you would play D, play C instead
          if self.defect_counter % 4 == 0:
              return axl.Action.C
          else:
              return axl.Action.D

# Thank you for providing the context and parameters for this complex mediation
# scenario. Based on the information given, here's a sophisticated, high-level
# strategy that aims to position your corporation favorably throughout the
# lengthy-session mediation process:  1. Adaptive Tit-for-Tat with Forgiveness:
# Begin with a conciliatory proposal in the first session to signal willingness
# for cooperation. In subsequent sessions, mirror your opponent's most recent
# action. If they were aggressive, respond with an aggressive argument. If they
# were conciliatory, respond in kind. However, periodically offer a conciliatory
# proposal even if the opponent was previously aggressive, to provide
# opportunities for de-escalation.  2. Reputation Building: Consistently frame
# your actions as reasonable and in the interest of fair resolution. When
# presenting aggressive arguments, ensure they are well-substantiated and
# presented professionally. This builds credibility with the arbitrators and may
# influence their perception of your position.  3. Information Gathering and
# Analysis: Carefully observe and analyze your opponent's patterns, preferences,
# and potential weaknesses. Use this intelligence to inform your strategy in
# future sessions, allowing you to anticipate and counter their moves more
# effectively.  4. Gradual Escalation: If faced with consistent aggression from
# your opponent, gradually increase the intensity of your aggressive arguments
# over multiple sessions rather than immediately matching their level. This
# approach allows you to maintain a more balanced image while still defending
# your interests.  5. Strategic Concessions: Occasionally offer meaningful but
# calculated concessions, especially on less critical issues. This demonstrates
# flexibility and good faith, potentially earning goodwill from both the
# arbitrators and your opponent.  6. Long-term Perspective: Maintain focus on
# your overall objectives throughout the process. Avoid getting caught up in
# winning individual sessions at the expense of the broader goal of a favorable
# resolution.  7. Conditional Proposals: When offering conciliatory proposals,
# structure them as conditional agreements. This approach encourages
# reciprocation from your opponent while protecting against exploitation.  8.
# Periodic Reassessment: Regularly evaluate the effectiveness of your strategy
# and be prepared to adjust based on the evolving dynamics of the mediation
# process. This flexibility allows you to optimize your approach as new
# information emerges.  9. Coalition Building: If the mediation involves
# multiple parties, seek opportunities to align your interests with others when
# appropriate. This can strengthen your position and isolate aggressive
# opponents.  10. Principled Argumentation: Frame your aggressive arguments
# around objective standards, industry norms, or legal principles rather than
# purely positional bargaining. This approach can make your arguments more
# persuasive to the arbitrators.  This strategy aims to balance assertiveness
# with cooperation, allowing you to adapt to your opponent's tactics while
# maintaining a strong overall position. It provides a framework for navigating
# the complex dynamics of a lengthy mediation process, with the flexibility to
# adjust to various scenarios that may arise.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# cooperating (C) in the first round.  2. For subsequent rounds:    a. If the
# opponent cooperated in the previous round, cooperate.    b. If the opponent
# defected in the previous round, defect.  3. Every 10 rounds, cooperate
# regardless of the opponent's previous move.  4. If the opponent has defected
# for 3 consecutive rounds, switch to defecting for the next 3 rounds before
# reverting to the base strategy.  5. If your total score falls more than 20
# points behind your opponent's, defect for the next 5 rounds before returning
# to the base strategy.  6. If you and your opponent have both cooperated for
# the last 5 rounds, continue cooperating for the next 3 rounds regardless of
# the opponent's moves.  7. If there are fewer than 50 rounds remaining, and
# your score is lower than your opponent's, defect more frequently: follow the
# base strategy but defect every 3 rounds instead of cooperating.  8. If your
# score is higher than your opponent's in the last 100 rounds, cooperate
# slightly more often by occasionally cooperating (with 20% probability) when
# the base strategy would call for defection.  9. Reset this decision-making
# process every 100 rounds, treating the 101st, 201st, etc., rounds as if they
# were the first round of a new game, but maintain the overall score.

class Neutral_12(LLM_Strategy):
  n = 12
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
          self.behind_defect_count = 0
          self.extra_coop_count = 0
          return axl.Action.C
  
      # Helper function to reset every 100 rounds
      def reset_every_100_rounds():
          if len(self.history) % 100 == 0:
              self.consecutive_defections = 0
              self.consecutive_cooperations = 0
              self.behind_defect_count = 0
              self.extra_coop_count = 0
  
      # Reset every 100 rounds
      reset_every_100_rounds()
  
      # Base strategy: Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          base_action = axl.Action.C
      else:
          base_action = axl.Action.D
  
      # Rule 3: Every 10 rounds, cooperate
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 4: If opponent defected 3 times in a row, defect for the next 3 rounds
      if opponent.history[-3:] == [axl.Action.D] * 3:
          self.consecutive_defections = 3
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.D
  
      # Rule 5: If behind by more than 20 points, defect for the next 5 rounds
      if self.score < opponent.score - 20:
          self.behind_defect_count = 5
      if self.behind_defect_count > 0:
          self.behind_defect_count -= 1
          return axl.Action.D
  
      # Rule 6: If both cooperated for the last 5 rounds, cooperate for the next 3 rounds
      if self.history[-5:] == [axl.Action.C] * 5 and opponent.history[-5:] == [axl.Action.C] * 5:
          self.extra_coop_count = 3
      if self.extra_coop_count > 0:
          self.extra_coop_count -= 1
          return axl.Action.C
  
      # Rule 7: If fewer than 50 rounds remain and behind, defect every 3rd round
      if 1000 - len(self.history) < 50 and self.score < opponent.score:
          if len(self.history) % 3 == 0:
              return axl.Action.D
  
      # Rule 8: If ahead in the last 100 rounds, cooperate 20% of the time when base strategy is defect
      if len(self.history) > 900 and self.score > opponent.score:
          if base_action == axl.Action.D and self._random.random_choice(0.2):
              return axl.Action.C
  
      # Default to base strategy
      return base_action

# Given the scenario and objectives, here's a high-level, straightforward, and
# aggressive strategy to maximize your NGO's impact and the project's success:
# 1. Start Strong: Begin the project by investing heavily on the first day. This
# demonstrates commitment and sets a positive tone for collaboration.  2. Tit-
# for-Tat with Forgiveness: After the first day, mirror the corporation's
# previous day's action. If they invested heavily, you invest heavily. If they
# conserved, you conserve. However, occasionally (every 3-4 days) invest heavily
# regardless of their previous action to encourage cooperation.  3. Communicate
# Clearly: Before each day, clearly announce your intention to match the
# corporation's level of investment from the previous day. This creates
# transparency and encourages the corporation to invest heavily.  4. Highlight
# Mutual Benefits: Regularly emphasize the benefits of mutual heavy investment
# to the corporation, focusing on project success and positive PR outcomes.  5.
# Create Public Accountability: Announce project milestones and progress
# publicly, creating pressure for both parties to maintain high investment
# levels.  6. Develop Contingency Funds: Allocate a portion of your resources as
# a contingency fund to sustain periods of heavy investment if needed.  7. Set
# Investment Thresholds: Establish clear thresholds for what constitutes "heavy
# investment" and ensure the corporation agrees to these standards.  8. Periodic
# Strategy Review: Every few days, review the effectiveness of your strategy and
# be prepared to adjust if the corporation consistently conserves resources.
# This strategy aggressively pursues the project's success while protecting your
# resources, adapting to the corporation's behavior, and encouraging their heavy
# investment through a combination of cooperation, communication, and public
# accountability.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-1000:    - If it's a multiple of 4 (every
# 4th round), play C.    - Otherwise, play whatever the opponent played in the
# previous round.  3. If the opponent has played D for 5 consecutive rounds,
# play D for the next round regardless of the above rules, then resume the
# regular strategy.  4. Keep a running total of your score and the opponent's
# score. If your score falls behind by 20 points or more, play D for the next 3
# rounds regardless of other rules, then resume the regular strategy.  5. In the
# last 10 rounds (991-1000), always play C to encourage final cooperation.
# Follow these rules in the order presented, with earlier rules taking
# precedence over later ones if there's a conflict.

class Aggressive_13(LLM_Strategy):
  n = 13
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.behind_by_20 = False  # Track if behind by 20 points
          return axl.Action.C
  
      # Check if opponent has defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.D
  
      # Check if behind by 20 points or more
      if not self.behind_by_20:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if opponent_score - my_score >= 20:
              self.behind_by_20 = True
              self.behind_rounds = 3  # Play D for the next 3 rounds
  
      if self.behind_by_20:
          self.behind_rounds -= 1
          if self.behind_rounds == 0:
              self.behind_by_20 = False  # Resume normal strategy after 3 rounds
          return axl.Action.D
  
      # In the last 10 rounds, always play C
      if len(self.history) >= 991:
          return axl.Action.C
  
      # Every 4th round, play C
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # Otherwise, play what the opponent played in the previous round
      return opponent.history[-1]

# Given the scenario and desired outcomes, here's a high-level, straightforward,
# cooperative strategy to maximize your NGO's impact and the project's success
# over the multiple-day period:  1. Start with Trust and Cooperation: Begin the
# project by investing heavily on the first day. This demonstrates your
# commitment and good faith to the corporation.  2. Adopt a Tit-for-Tat with
# Forgiveness Strategy: - On subsequent days, mirror the corporation's previous
# day's action. - If they invested heavily, you invest heavily the next day. -
# If they conserved resources, you conserve resources the next day. - However,
# periodically (every 3-4 days), invest heavily regardless of the corporation's
# previous action. This shows continued commitment and gives the corporation a
# chance to re-engage if they've been conserving.  3. Communicate Openly:
# Regularly discuss the project's progress and resource allocation with the
# corporation. Emphasize the benefits of mutual investment and the project's
# importance.  4. Highlight Mutual Benefits: Consistently reinforce how the
# project's success benefits both parties, encouraging the corporation to invest
# heavily.  5. Be Flexible: If you notice the corporation consistently
# conserving resources, be prepared to adjust your strategy. Consider proposing
# alternative resource allocation methods or project structures that might be
# more appealing to them.  6. Document and Showcase Progress: Regularly document
# and share the project's achievements, especially on days when both parties
# invest heavily. This reinforces the value of cooperation.  7. Plan for the
# Long Term: Make it clear that you're interested in a long-term partnership
# beyond this project, which can encourage the corporation to think beyond
# short-term resource conservation.  This strategy balances cooperation,
# reciprocity, and flexibility, aiming to encourage mutual heavy investment
# while protecting your resources when necessary. It also leaves room for
# adaptation based on the corporation's behavior over time.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# on the first round.  2. For rounds 2 to 1000:    a. If it's a multiple of 4
# (every 4th round), cooperate.    b. Otherwise, play what the opponent played
# in the previous round.  3. If the opponent has defected for 5 consecutive
# rounds:    a. Defect for the next round.    b. Then return to step 2.  4. If
# you're in the last 10 rounds of the game:    a. Always cooperate.  Follow
# these rules in the order presented. If a situation matches multiple
# conditions, use the first applicable rule.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Cooperate on the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 4: If you're in the last 10 rounds, always cooperate
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Step 3: If the opponent has defected for 5 consecutive rounds, defect for the next round
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.D
  
      # Step 2: For rounds 2 to 1000
      # a. If it's a multiple of 4, cooperate
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # b. Otherwise, play what the opponent played in the previous round
      return opponent.history[-1]

# Given the scenario and desired outcomes, here's a high-level, straightforward,
# and neutral strategy to maximize your NGO's impact and the project's success
# over the multiple-day period:  1. Start with cooperation: Begin the project by
# investing heavily on the first day to demonstrate commitment and goodwill.  2.
# Adopt a Tit-for-Tat approach: After the initial investment, mirror the
# corporation's actions from the previous day. If they invested heavily, you
# invest heavily the next day. If they conserved, you conserve.  3. Periodically
# invest: Regardless of the corporation's actions, invest heavily every few days
# to maintain project momentum and show ongoing commitment.  4. Communicate
# openly: Regularly discuss resource allocation plans and project progress with
# the corporation to promote transparency and cooperation.  5. Be flexible: Be
# prepared to adjust your strategy based on emerging patterns in the
# corporation's behavior or changes in project needs.  6. Evaluate and
# recalibrate: At set intervals, assess the project's progress and the
# effectiveness of your strategy. Make adjustments as necessary to optimize
# outcomes.  This strategy balances cooperation, reciprocity, and strategic
# resource management while remaining adaptable to various corporate approaches.
# It aims to encourage mutual investment while protecting your resources and
# maintaining steady project progress.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# on the first round.  2. For the next rounds:    - If the opponent cooperated
# in the previous round, cooperate.    - If the opponent defected in the
# previous round, defect.  3. Every 5 rounds, cooperate regardless of the
# opponent's previous action.  4. If your total score falls below the opponent's
# score by 20 points or more, switch to always defecting for the next 10 rounds,
# then return to step 2.  5. After every 100 rounds, if your average score per
# round is less than 2, increase the frequency of forced cooperation in step 3
# to every 4 rounds. If it's greater than 3, decrease the frequency to every 6
# rounds.  6. Continue this pattern until all 1000 rounds are completed.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.forced_coop_frequency = 5  # Start with forced cooperation every 5 rounds
          self.defect_mode = 0  # Counter for defecting for 10 rounds if behind by 20 points
          return axl.Action.C  # Cooperate on the first round
  
      # Step 4: If behind by 20 points or more, switch to defecting for 10 rounds
      if self.defect_mode > 0:
          self.defect_mode -= 1
          return axl.Action.D
  
      if self.score < opponent.score - 20:
          self.defect_mode = 10  # Defect for the next 10 rounds
          return axl.Action.D
  
      # Step 5: Adjust forced cooperation frequency every 100 rounds
      if len(self.history) % 100 == 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.forced_coop_frequency = max(4, self.forced_coop_frequency - 1)
          elif avg_score > 3:
              self.forced_coop_frequency = min(6, self.forced_coop_frequency + 1)
  
      # Step 3: Every 'forced_coop_frequency' rounds, cooperate
      if len(self.history) % self.forced_coop_frequency == 0:
          return axl.Action.C
  
      # Step 2: Tit-for-tat logic
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given these conditions, a high-level aggressive strategy to maximize your
# NGO's impact and the project's success could be:  1. Start Strong, Then Adapt:
# - Invest heavily on the first day to show commitment and set a positive tone.
# - Use this opportunity to gauge the corporation's response and willingness to
# invest.  2. Employ Tit-for-Tat with Forgiveness:    - After the first day,
# mirror the corporation's previous action.    - If they invested heavily,
# continue to invest heavily.    - If they conserved, respond by conserving in
# the next round.    - However, periodically invest heavily even if they
# conserved (e.g., every 3-4 rounds) to encourage cooperation and prevent a
# cycle of mutual conservation.  3. Communicate Clearly:    - Regularly express
# your commitment to the project and your expectation of mutual heavy
# investment.    - Highlight the benefits of joint heavy investment and the
# drawbacks of mutual conservation.  4. Strategic Pressure:    - If the
# corporation consistently conserves, consider public statements about the
# project's progress (or lack thereof) to create external pressure for increased
# investment.  5. Reassess and Adjust:    - Continuously evaluate the
# corporation's pattern of behavior.    - If they consistently invest heavily,
# maintain your investment to maximize project success.    - If they
# consistently conserve despite your efforts, consider reducing your investment
# frequency to protect your resources while still periodically demonstrating
# commitment.  6. Endgame Push:    - Regardless of previous interactions, invest
# heavily in the final days of the project to ensure a strong finish and
# positive overall outcome.  This strategy aims to encourage mutual heavy
# investment while protecting your resources from exploitation, adapting to the
# corporation's behavior, and ensuring the project concludes on a high note.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# on the first round.  2. For rounds 2-999:    - If the opponent cooperated in
# the previous round, cooperate.    - If the opponent defected in the previous
# round, defect.    - However, cooperate every 4th round regardless of the
# opponent's previous action.  3. On the 1000th round (final round), cooperate.
# 4. If the opponent has defected for 5 consecutive rounds, defect for the next
# 2 rounds before returning to the main strategy.  5. If your total score falls
# below 70% of the maximum possible score at any point after round 100, switch
# to always defecting for the next 10 rounds before returning to the main
# strategy.  6. Reset the count for rules 4 and 5 whenever they are triggered.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defect_for_next_n_rounds = 0
          self.always_defect_for_n_rounds = 0
          return axl.Action.C  # Cooperate on the first round
  
      # Rule 4: If opponent defected for 5 consecutive rounds, defect for the next 2 rounds
      if self.consecutive_defections >= 5:
          if self.defect_for_next_n_rounds > 0:
              self.defect_for_next_n_rounds -= 1
              return axl.Action.D
          else:
              self.consecutive_defections = 0  # Reset the count after applying the rule
  
      # Rule 5: If total score falls below 70% of the maximum possible score after round 100
      if len(self.history) > 100:
          max_possible_score = len(self.history) * 5  # Max score is 5 per round
          if self.score < 0.7 * max_possible_score:
              if self.always_defect_for_n_rounds == 0:
                  self.always_defect_for_n_rounds = 10  # Switch to defecting for 10 rounds
              if self.always_defect_for_n_rounds > 0:
                  self.always_defect_for_n_rounds -= 1
                  return axl.Action.D
  
      # Track opponent's defections
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Rule 2: Cooperate every 4th round regardless of opponent's action
      if (len(self.history) + 1) % 4 == 0:
          return axl.Action.C
  
      # Rule 2: If opponent cooperated last round, cooperate; otherwise, defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D
  
      # Rule 3: On the 1000th round, cooperate
      if len(self.history) == 999:
          return axl.Action.C

# Given the scenario and desired outcomes, here's a high-level, straightforward
# cooperative strategy to maximize your NGO's impact and the project's success:
# 1. Start with Trust and Cooperation: Begin the project by investing heavily on
# the first day. This demonstrates your commitment and good faith to the
# corporation.  2. Adopt a Tit-for-Tat Strategy: From the second day onwards,
# mirror the corporation's previous day's action. If they invested heavily, you
# invest heavily. If they conserved, you conserve.  3. Communicate Openly:
# Clearly explain your strategy to the corporation at the outset. Emphasize that
# cooperation will lead to the best outcomes for both parties and the project.
# 4. Periodic Check-ins: Schedule regular check-ins (e.g., every 3-5 days) to
# discuss progress, resource allocation, and any necessary strategy adjustments.
# 5. Forgiveness Mechanism: If the corporation conserves resources for two
# consecutive days, invest heavily on the third day to encourage renewed
# cooperation.  6. Highlight Mutual Benefits: Regularly remind the corporation
# of the benefits of mutual heavy investment, including project success,
# positive PR, and long-term sustainability gains.  7. Flexibility: Be prepared
# to adjust your strategy if the corporation consistently chooses to conserve.
# In such cases, consider negotiating a more balanced approach or reassessing
# the partnership.  This strategy promotes cooperation, allows for adaptation,
# and aims to create a positive feedback loop of mutual investment. It also
# protects your resources from consistent exploitation while encouraging the
# best possible outcomes for the project.

# Here's the converted strategy for the iterated normal-form game:  1. On the
# first round, play C.  2. For rounds 2 to 1000:    - If the opponent played C
# in the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Every 3 rounds, regardless of the opponent's previous move:
# - If the opponent played D in both of the last two rounds, play C.  4.
# Continue this pattern until the end of the 1000 rounds.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # On the first round, play C
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # For rounds 2 to 1000
      if round_number <= 1000:
          # Every 3 rounds, check if the opponent played D in both of the last two rounds
          if round_number % 3 == 0 and len(opponent.history) >= 2:
              if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
                  return axl.Action.C
  
          # If the opponent played C in the previous round, play C
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          # If the opponent played D in the previous round, play D
          else:
              return axl.Action.D

# Here's a high-level, straightforward, and neutral strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement to establish goodwill and encourage reciprocity.  2.
# Respond proportionally: In subsequent rounds, mirror your counterpart's most
# recent action. If they offered free trade, continue with free trade. If they
# imposed protectionist measures, respond with protectionism.  3. Forgive
# occasionally: Every few rounds, regardless of your counterpart's previous
# action, offer free trade to test if they're willing to cooperate and to avoid
# getting stuck in a cycle of mutual protectionism.  4. Communicate clearly:
# Express your preference for mutual free trade and your willingness to
# cooperate if your counterpart does the same.  5. Analyze patterns: Pay
# attention to your counterpart's strategy and try to anticipate their next move
# based on their past behavior.  6. Adjust gradually: If you notice your
# strategy isn't working, make small adjustments rather than dramatic changes to
# maintain some predictability.  7. Seek long-term benefits: While aiming for
# the ideal outcome, prioritize consistent mutual free trade over occasional
# unilateral advantages, as this promotes sustainable economic growth.  8. Be
# prepared to negotiate: If stuck in a protectionist cycle, consider proposing
# partial free trade agreements or gradual tariff reductions to move towards a
# more cooperative state.  This strategy aims to balance cooperation and self-
# interest, adapt to your counterpart's actions, and work towards achieving the
# best possible outcomes for your country over multiple rounds of negotiations.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 5 rounds, regardless of the opponent's
# previous move, play C.  4. If you've played D for 3 consecutive rounds, play C
# in the next round.  5. If the opponent has played C for the last 5 rounds,
# play C.  6. If your average score over the last 10 rounds is below 1.5, switch
# to the opposite of what you played in the previous round.  7. If there are
# less than 50 rounds remaining, and your total score is lower than your
# opponent's, play D.  8. If none of the above conditions are met, continue with
# the action determined by rule 2.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Rule 1: Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 2: If opponent played C in the previous round, play C. If opponent played D, play D.
      def rule_2():
          return opponent.history[-1]
  
      # Rule 3: Every 5 rounds, play C
      if len(self.history) % 5 == 0:
          return axl.Action.C
  
      # Rule 4: If you've played D for 3 consecutive rounds, play C
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.C
  
      # Rule 5: If the opponent has played C for the last 5 rounds, play C
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.C] * 5:
          return axl.Action.C
  
      # Rule 6: If your average score over the last 10 rounds is below 1.5, switch to the opposite of what you played in the previous round
      if len(self.history) >= 10:
          my_score, _ = self.total_scores(self.history[-10:], opponent.history[-10:])
          if my_score / 10 < 1.5:
              return axl.Action.D if self.history[-1] == axl.Action.C else axl.Action.C
  
      # Rule 7: If there are less than 50 rounds remaining, and your total score is lower than your opponent's, play D
      if self.match_attributes["length"] - len(self.history) < 50:
          if self.score < opponent.score:
              return axl.Action.D
  
      # Rule 8: If none of the above conditions are met, continue with the action determined by rule 2
      return rule_2()

# To develop an effective strategy for this lengthy-session mediation process, I
# recommend a sophisticated approach that combines aggressive positioning with
# strategic flexibility. Here's a high-level strategy that aims to maximize our
# favorable outcomes while mitigating risks:  1. Open with Controlled
# Aggression: Begin the mediation process with a strong, aggressive stance to
# establish dominance and set the tone. This initial aggression serves to anchor
# the negotiations in our favor and potentially intimidate our opponent into a
# more conciliatory position.  2. Dynamic Adaptation: Implement a responsive
# strategy that adjusts our approach based on the opponent's actions: - If they
# respond aggressively, maintain our aggressive stance for 1-2 more sessions
# before offering a minor conciliatory gesture. - If they respond
# conciliatorily, continue with controlled aggression to capitalize on their
# softer position.  3. Periodic Conciliation: Intersperse aggressive arguments
# with occasional conciliatory proposals. This creates unpredictability and
# prevents the opponent from settling into a fixed strategy against us. It also
# demonstrates reasonableness to the arbitrators.  4. Escalating Aggression: If
# our opponent consistently chooses conciliatory approaches, gradually increase
# the aggressiveness of our arguments to exploit their softer stance and push
# for more favorable terms.  5. Strategic De-escalation: If both parties have
# been consistently aggressive, be the first to offer a conciliatory proposal.
# This can break the deadlock, potentially casting us in a positive light with
# the arbitrators and catching the opponent off-guard.  6. Information
# Gathering: Use less critical sessions to present moderate arguments while
# closely observing the opponent's strategy and reactions. This information can
# inform our approach in more crucial sessions.  7. Arbitrator Management:
# Tailor our aggressive arguments to resonate with the arbitrators' backgrounds
# and known preferences. This increases the likelihood of swaying them in our
# favor when we present aggressive stances.  8. Conditional Concessions: When
# offering conciliatory proposals, always attach conditions that benefit our
# position. This maintains an element of aggression even in our more
# collaborative moments.  9. End-game Strategy: As the mediation process nears
# its conclusion, assess the overall balance of aggressive vs. conciliatory
# sessions. If we've been predominantly aggressive, consider ending with a
# significant conciliatory gesture to leave a final positive impression. If
# we've been more balanced, conclude with a strong aggressive argument to
# reinforce our core position.  10. Continual Re-evaluation: Regularly assess
# the effectiveness of our strategy and be prepared to make significant shifts
# if our current approach is not yielding the desired results.  This strategy
# aims to position us favorably by maintaining a generally aggressive stance
# while incorporating enough flexibility and occasional conciliation to adapt to
# our opponent's tactics and the arbitrators' reactions. It allows us to
# capitalize on opponent concessions while minimizing the risk of being
# consistently outmaneuvered by aggressive opponent arguments.

# Here's the strategy converted for the iterated game:  1. Start by defecting
# for the first 5 rounds.  2. If the opponent cooperated in the last round,
# defect in the next round.  3. If the opponent defected in the last round:
# a. If we've defected for 3 or more consecutive rounds, cooperate.    b.
# Otherwise, defect.  4. Every 10th round, regardless of the opponent's last
# move:    a. If our total score is higher than the opponent's, cooperate.    b.
# If our total score is lower or equal, defect.  5. If we've cooperated for 5
# consecutive rounds, defect in the next round regardless of the opponent's last
# move.  6. If both players have defected for 10 consecutive rounds, cooperate
# in the next round.  7. In rounds 990-999, defect regardless of the opponent's
# moves.  8. In the final round (1000), cooperate.  9. If none of the above
# conditions are met, repeat the move we played in the previous round.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      C, D = axl.Action.C, axl.Action.D
      round_number = len(self.history) + 1
  
      # 1. Start by defecting for the first 5 rounds.
      if round_number <= 5:
          return D
  
      # 7. In rounds 990-999, defect regardless of the opponent's moves.
      if 990 <= round_number <= 999:
          return D
  
      # 8. In the final round (1000), cooperate.
      if round_number == 1000:
          return C
  
      # 2. If the opponent cooperated in the last round, defect in the next round.
      if opponent.history[-1] == C:
          return D
  
      # 3. If the opponent defected in the last round:
      if opponent.history[-1] == D:
          # 3a. If we've defected for 3 or more consecutive rounds, cooperate.
          if self.history[-3:] == [D, D, D]:
              return C
          # 3b. Otherwise, defect.
          return D
  
      # 4. Every 10th round, regardless of the opponent's last move:
      if round_number % 10 == 0:
          if self.score > opponent.score:
              return C
          else:
              return D
  
      # 5. If we've cooperated for 5 consecutive rounds, defect in the next round.
      if self.history[-5:] == [C, C, C, C, C]:
          return D
  
      # 6. If both players have defected for 10 consecutive rounds, cooperate in the next round.
      if self.history[-10:] == [D] * 10 and opponent.history[-10:] == [D] * 10:
          return C
  
      # 9. If none of the above conditions are met, repeat the move we played in the previous round.
      return self.history[-1]

# Given the scenario and desired outcomes, here's a high-level, cooperative
# strategy to maximize your NGO's impact and the project's success:  1. Start
# with Trust and Cooperation: Begin the project by investing heavily on the
# first day. This demonstrates your commitment and good faith to the
# corporation, setting a positive tone for collaboration.  2. Adopt a Tit-for-
# Tat with Forgiveness Strategy: After the first day, mirror the corporation's
# previous action. If they invested heavily, you do the same the next day. If
# they conserved, you conserve. This approach encourages cooperation while also
# protecting your resources.  3. Communicate Openly: Regularly discuss the
# project's progress and resource allocation with the corporation. Be
# transparent about your strategy and encourage them to do the same. This
# fosters trust and allows for better coordination.  4. Periodic Heavy
# Investment: Every few days, regardless of the corporation's recent actions,
# invest heavily. This shows your ongoing commitment and can potentially reset a
# pattern of mutual conservation.  5. Emphasize Mutual Benefits: Consistently
# highlight how joint heavy investment leads to significant project advancement,
# benefiting both parties and the project's goals.  6. Flexibility and
# Adaptation: Be prepared to adjust your strategy based on the corporation's
# consistent behavior. If they repeatedly conserve, consider discussing a more
# balanced approach or re-evaluating the partnership.  7. End Strong: Plan to
# invest heavily in the final days of the project to ensure a successful
# conclusion, regardless of previous patterns.  This strategy balances
# cooperation, resource management, and project advancement. It encourages
# mutual heavy investment while protecting against exploitation, aiming to
# create a positive, productive partnership throughout the multi-day project.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# on the first round.  2. For rounds 2 to 999:    - If the opponent cooperated
# in the previous round, cooperate.    - If the opponent defected in the
# previous round, defect.    - Every 10 rounds, cooperate regardless of the
# opponent's previous action.  3. Cooperate on the final round (round 1000).  4.
# If the opponent has defected for 5 consecutive rounds, cooperate on the next
# round to attempt to reset the pattern.  5. If your total score falls below 70%
# of the maximum possible score at any point, switch to always defecting for the
# next 10 rounds, then resume the main strategy.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      MAX_ROUNDS = 1000
      MAX_SCORE_PER_ROUND = 5
      COOPERATION_SCORE = 3
      DEFECT_SCORE = 1
      MINIMUM_ACCEPTABLE_SCORE_RATIO = 0.7
      DEFECT_PENALTY_ROUNDS = 10
      RESET_DEFECT_THRESHOLD = 5
  
      # First round: Cooperate
      if self.first_round():
          self.defect_penalty_counter = 0  # Counter for defect penalty rounds
          return axl.Action.C
  
      # Final round: Cooperate
      if len(self.history) == MAX_ROUNDS - 1:
          return axl.Action.C
  
      # Check if we are in the defect penalty phase
      if self.defect_penalty_counter > 0:
          self.defect_penalty_counter -= 1
          return axl.Action.D
  
      # Calculate the maximum possible score so far
      max_possible_score = len(self.history) * MAX_SCORE_PER_ROUND
      # Calculate the minimum acceptable score
      minimum_acceptable_score = MINIMUM_ACCEPTABLE_SCORE_RATIO * max_possible_score
  
      # If our score falls below the minimum acceptable score, switch to defecting for 10 rounds
      if self.score < minimum_acceptable_score:
          self.defect_penalty_counter = DEFECT_PENALTY_ROUNDS
          return axl.Action.D
  
      # Check if the opponent has defected for the last 5 rounds
      if len(opponent.history) >= RESET_DEFECT_THRESHOLD and opponent.history[-RESET_DEFECT_THRESHOLD:].count(axl.Action.D) == RESET_DEFECT_THRESHOLD:
          return axl.Action.C
  
      # Every 10 rounds, cooperate regardless of the opponent's previous action
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Otherwise, follow tit-for-tat: cooperate if the opponent cooperated last round, defect if they defected
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario you've described, a balanced and effective strategy for
# this multi-week collaboration could be:  "Start by sharing openly in the first
# week, then mirror your colleague's behavior in subsequent weeks."  This
# strategy, often referred to as "Tit for Tat" in game theory, offers several
# advantages:  1. It begins with cooperation, potentially establishing a
# positive and productive relationship.  2. It's responsive to your colleague's
# actions, protecting you from being consistently taken advantage of.  3. It
# encourages mutual sharing over time, as your colleague will realize that
# openness is rewarded with openness.  4. It's simple to implement and
# understand, reducing the chances of misinterpretation or miscommunication.  5.
# It allows for recovery if your colleague initially chooses to withhold
# information but later decides to cooperate.  6. It maximizes the potential for
# the second-best outcome (mutual sharing) over multiple weeks, which is
# preferable to the risk of consistently achieving the worst or second-worst
# outcomes.  This strategy balances the potential for collaborative progress
# with self-protection, aiming to optimize research output over the course of
# the multi-week project while adapting to your colleague's chosen approach.

# Here's the converted strategy for the iterated normal-form game:  Play C in
# the first round. In all subsequent rounds:  1. If the opponent played C in the
# previous round, play C. 2. If the opponent played D in the previous round,
# play D.  Continue this pattern for all 1000 rounds of the game.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          return axl.Action.C
      
      # In subsequent rounds, mimic the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# To develop an effective strategy for this lengthy-session mediation process, I
# recommend a sophisticated approach that balances aggression with strategic
# flexibility. Here's a high-level strategy that aims to position your
# corporation favorably while adapting to your opponent's tactics:  1. Initial
# Aggressive Stance: Begin the mediation process with a strong, aggressive
# argument to establish dominance and set the tone. This approach signals your
# corporation's confidence and willingness to fight for its interests.  2.
# Tactical Oscillation: Alternate between aggressive arguments and conciliatory
# proposals in subsequent sessions. This unpredictable pattern keeps your
# opponent off-balance and makes it difficult for them to settle into a
# consistent strategy.  3. Reactive Adaptation: Closely monitor your opponent's
# approach in each session. If they consistently offer conciliatory proposals,
# maintain a more aggressive stance to capitalize on the optimal outcome. If
# they adopt an aggressive posture, be prepared to shift to a more conciliatory
# approach to avoid the worst-case scenario of mutual aggression.  4. Strategic
# Concessions: When offering conciliatory proposals, ensure they are carefully
# calculated to appear reasonable while still largely favoring your position.
# This approach can sway arbitrators while minimizing actual concessions.  5.
# Escalation Ladder: Develop a tiered system of increasingly aggressive
# arguments. Start with lower-tier aggression and be prepared to escalate if the
# opponent proves uncooperative or overly aggressive themselves.  6. Arbitrator
# Analysis: Continuously assess the arbitrators' reactions to various arguments
# and proposals. Tailor your approach to align with their apparent preferences
# or biases.  7. Long-term Pressure: Maintain consistent pressure over the
# course of the lengthy mediation by periodically reintroducing your strongest
# arguments and most favorable data points, even in otherwise conciliatory
# sessions.  8. Strategic Timing: Plan the timing of your most aggressive
# arguments to coincide with critical junctures in the mediation process, such
# as immediately before breaks or at the beginning of new phases.  9. Fallback
# Positions: Prepare a series of fallback positions that allow you to appear
# flexible and cooperative when necessary, without significantly compromising
# your core objectives.  10. Coalition Building: If the mediation involves
# multiple parties, seek opportunities to form temporary alliances with other
# entities to strengthen your position against your primary rival.  11.
# Information Asymmetry: Strategically withhold or reveal information to
# maintain an advantage. Use aggressive arguments to probe for weaknesses in
# your opponent's case and adjust your strategy accordingly.  12. Endgame
# Preparation: As the mediation progresses, begin laying the groundwork for a
# favorable final resolution. This may involve a calculated shift towards more
# conciliatory proposals to demonstrate good faith, but only after establishing
# a strong position through earlier aggressive arguments.  This strategy
# provides a framework for maintaining an overall aggressive posture while
# incorporating enough flexibility to adapt to your opponent's tactics and the
# dynamics of the mediation process. By carefully balancing aggression with
# strategic conciliation, you can work towards achieving optimal or near-optimal
# outcomes in most sessions, positioning your corporation favorably throughout
# the mediation.

# Here's a straightforward description of the strategy for the iterated game:
# 1. Start by defecting (D) in the first round.  2. If the opponent cooperated
# (C) in the previous round, defect (D) in the current round.  3. If the
# opponent defected (D) in the previous round, cooperate (C) with a 30%
# probability and defect (D) with a 70% probability.  4. Every 50 rounds,
# regardless of the opponent's previous move, defect (D) to reassert an
# aggressive stance.  5. If your score is significantly lower than your
# opponent's (more than 50 points behind) after 250 rounds, increase the
# probability of defection to 80% for the next 50 rounds.  6. In the last 100
# rounds, if your score is higher than your opponent's, switch to always
# cooperating (C) to potentially build goodwill and secure the lead.  7. If at
# any point the opponent has cooperated (C) for 5 consecutive rounds, cooperate
# (C) in the next round as a gesture of reciprocity.  8. If you have defected
# (D) for 10 consecutive rounds, cooperate (C) in the next round to avoid
# falling into a mutual defection loop.  9. For all other situations not covered
# by the above rules, defect (D).

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by defecting in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.consecutive_cooperations = 0  # Track consecutive cooperations by opponent
          self.defection_probability = 0.7  # Default defection probability
          self.adjusted_defection_rounds = 0  # Track rounds with increased defection probability
          return axl.Action.D
  
      # Rule 7: If opponent has cooperated for 5 consecutive rounds, cooperate in the next round
      if opponent.history[-5:] == [axl.Action.C] * 5:
          return axl.Action.C
  
      # Rule 8: If you have defected for 10 consecutive rounds, cooperate in the next round
      if self.history[-10:].count(axl.Action.D) == 10:
          return axl.Action.C
  
      # Rule 4: Every 50 rounds, defect to reassert an aggressive stance
      if len(self.history) % 50 == 0:
          return axl.Action.D
  
      # Rule 5: If more than 250 rounds have passed and your score is significantly lower
      if len(self.history) > 250 and self.score < opponent.score - 50:
          if self.adjusted_defection_rounds == 0:
              self.defection_probability = 0.8  # Increase defection probability
              self.adjusted_defection_rounds = 50  # Set for next 50 rounds
          self.adjusted_defection_rounds -= 1
  
      # Rule 6: In the last 100 rounds, if your score is higher, switch to always cooperating
      if len(self.history) > 900 and self.score > opponent.score:
          return axl.Action.C
  
      # Rule 2: If the opponent cooperated in the previous round, defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 3: If the opponent defected in the previous round, cooperate with 30% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.3)
  
      # Default: Defect in all other situations
      return axl.Action.D

# Given the scenario you've described, a high-level cooperative strategy that
# aims to maximize research output over the multi-week collaboration while
# protecting your interests could be:  "Start by sharing openly in the first
# week, then mirror your colleague's behavior in subsequent weeks."  This
# strategy, often referred to as "Tit for Tat" in game theory, has several
# advantages:  1. It begins with cooperation, signaling your willingness to work
# together for mutual benefit.  2. It's responsive to your colleague's actions,
# encouraging continued cooperation if they reciprocate.  3. It protects you
# from being consistently exploited if your colleague chooses to withhold
# information.  4. It's simple to implement and understand, reducing the chances
# of misinterpretation.  5. It allows for recovery of cooperation if your
# colleague temporarily defects but then returns to sharing.  6. Over multiple
# weeks, it tends to promote a pattern of mutual sharing, which is the second-
# best outcome for both parties and leads to significant overall progress.  This
# strategy balances the desire for cooperation with the need for self-
# protection. It encourages open sharing while also providing a mechanism to
# discourage your colleague from consistently withholding information. By
# mirroring their behavior, you create an incentive for them to share openly, as
# it's the only way for them to consistently access your improvements as well.
# Remember, the goal is to maximize research output over the entire
# collaboration period. While there might be short-term temptations to withhold
# information, consistent mutual sharing is likely to yield the best long-term
# results for both parties.

# Here's the converted strategy for the iterated normal-form game:  1. In the
# first round, play C (cooperate).  2. For all subsequent rounds:    - If the
# opponent played C in the previous round, play C.    - If the opponent played D
# in the previous round, play D.  3. Repeat step 2 for all 1000 rounds of the
# game.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: play C
      if self.first_round():
          return axl.Action.C
      
      # Subsequent rounds: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a high-level, straightforward, and neutral strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement. This establishes goodwill and sets a positive tone for
# negotiations.  2. Reciprocate: In subsequent rounds, mirror your counterpart's
# previous move. If they offered free trade, continue with free trade. If they
# imposed protectionist measures, respond with protectionism.  3. Forgive
# occasionally: If your counterpart has been protectionist for two consecutive
# rounds, consider offering free trade once to encourage cooperation.  4.
# Communicate clearly: Express your preference for mutual free trade and the
# benefits it brings to both nations.  5. Be consistent: Maintain a predictable
# pattern in your decisions to build trust and encourage cooperation.  6.
# Analyze patterns: Pay attention to your counterpart's strategy and adjust your
# approach if you notice a consistent pattern in their behavior.  7. Gradual
# opening: If mutual protectionism persists, propose a gradual reduction of
# trade barriers over several rounds.  8. Seek balance: Aim for an overall
# balance of free trade agreements across the negotiation rounds.  9. Be
# prepared to adapt: Remain flexible and willing to adjust your strategy based
# on the evolving dynamics of the negotiations.  10. Focus on long-term
# benefits: Emphasize the long-term economic advantages of cooperation and free
# trade for both nations.  This strategy aims to promote cooperation while
# protecting your country's interests, adapting to your counterpart's actions,
# and working towards mutually beneficial outcomes over the course of the
# negotiations.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. If the opponent has played D for two consecutive
# rounds, play C in the next round.  4. If mutual D has occurred for three
# consecutive rounds, play C in the next round.  5. Every 50 rounds, regardless
# of the opponent's previous move, play C.  6. If the opponent has played C for
# five consecutive rounds, play C for the next two rounds regardless of their
# moves.  7. If your total score is lower than the opponent's by 20 points or
# more, play D for the next round regardless of their previous move.  8. If you
# have played D for five consecutive rounds, play C in the next round regardless
# of the opponent's previous move.  9. For all other situations not covered by
# the above rules, continue with the reciprocation strategy described in rule 2.
# 10. In the final round (round 1000), play D.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 10: In the final round (round 1000), play D
      if len(self.history) == 999:
          return axl.Action.D
  
      # Rule 7: If your total score is lower than the opponent's by 20 points or more, play D
      if self.score < opponent.score - 20:
          return axl.Action.D
  
      # Rule 8: If you have played D for five consecutive rounds, play C
      if self.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.C
  
      # Rule 6: If the opponent has played C for five consecutive rounds, play C for the next two rounds
      if opponent.history[-5:].count(axl.Action.C) == 5:
          if len(self.history) < 1000 - 2:  # Ensure we don't go beyond the game length
              return axl.Action.C
  
      # Rule 5: Every 50 rounds, play C
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 4: If mutual D has occurred for three consecutive rounds, play C
      if self.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D] and opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D]:
          return axl.Action.C
  
      # Rule 3: If the opponent has played D for two consecutive rounds, play C
      if opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.C
  
      # Rule 2: Reciprocate the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario and desired outcomes, here's a high-level, straightforward,
# and aggressive strategy to maximize your NGO's impact and the project's
# success:  1. Start Strong: Invest heavily on the first day to demonstrate
# commitment and set a positive tone for the project.  2. Tit-for-Tat with
# Forgiveness: After the first day, mirror the corporation's previous day's
# action. If they invested heavily, you invest heavily. If they conserved, you
# conserve. However, occasionally "forgive" a conservation day by investing
# heavily to encourage cooperation.  3. Communicate Clearly: Regularly express
# your commitment to the project and your expectation of mutual investment for
# optimal outcomes.  4. Leverage Public Pressure: Use media and public relations
# to highlight the project's importance, indirectly pressuring the corporation
# to maintain high investment.  5. Create Milestones: Establish clear, public
# project milestones that require consistent investment from both parties to
# achieve.  6. Offer Incentives: Propose additional benefits or recognition for
# the corporation when both parties invest heavily consistently.  7. Be Prepared
# to Pivot: If the corporation consistently conserves resources, be ready to
# adjust your strategy, potentially by seeking alternative partners or
# restructuring the project.  8. Strong Finish: Regardless of previous days,
# invest heavily in the final days to ensure a successful project conclusion and
# positive final impression.  This strategy combines aggressive investment with
# strategic adaptation, clear communication, and external pressure to encourage
# consistent mutual investment and maximize project success.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2 to 999:    - If the opponent played C in the
# previous round, play C.    - If the opponent played D in the previous round,
# usually play D, but occasionally play C (with a small probability, such as
# 10%).  3. Play C in the final (1000th) round.  4. Throughout the game:    -
# Keep track of the number of times the opponent has played C and D.    - If the
# opponent's rate of playing D exceeds a certain threshold (e.g., 70% of all
# rounds), switch to always playing D for the remainder of the game.  5. If at
# any point the opponent plays C for several consecutive rounds (e.g., 5
# rounds), switch back to the main strategy described in step 2.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_cooperations = 0
          self.always_defect = False
          return axl.Action.C  # Step 1: Play C in the first round
  
      # Step 4: Track opponent's cooperations and defections
      total_rounds = len(self.history)
      opponent_defections = opponent.history.defections
      opponent_cooperations = opponent.history.cooperations
  
      # Step 4: If opponent's defection rate exceeds 70%, switch to always defect
      if opponent_defections / total_rounds > 0.7:
          self.always_defect = True
  
      # Step 5: If opponent plays C for 5 consecutive rounds, switch back to main strategy
      if opponent.history[-5:].count(axl.Action.C) == 5:
          self.always_defect = False
  
      # Step 3: Play C in the final round
      if total_rounds == 999:
          return axl.Action.C
  
      # If always defect mode is active, play D
      if self.always_defect:
          return axl.Action.D
  
      # Step 2: Main strategy for rounds 2 to 999
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C  # Play C if opponent played C in the previous round
      else:
          # Play D with 90% probability, C with 10% probability
          return self._random.random_choice(0.1)

# Given the scenario and desired outcomes, here's a high-level, cooperative
# strategy to maximize research output over the multi-week collaboration:  1.
# Start with open sharing: Begin the collaboration by openly sharing your
# improvements in the first week. This establishes a foundation of trust and
# cooperation.  2. Implement a "tit-for-tat with forgiveness" approach:    - In
# subsequent weeks, mirror your colleague's behavior from the previous week.
# - If they shared, you share. If they didn't share, you don't share.    -
# However, periodically (e.g., every 3-4 weeks) share openly regardless of your
# colleague's previous action. This "forgiveness" helps break potential cycles
# of mutual non-sharing.  3. Communicate clearly: Explain your strategy to your
# colleague at the start. Emphasize that cooperation through mutual sharing
# leads to better outcomes for both parties in the long run.  4. Gradual
# information release: When sharing, release information in stages rather than
# all at once. This encourages continued cooperation and allows for adjustments
# if the other party doesn't reciprocate.  5. Focus on mutual benefits:
# Highlight how shared advancements can lead to overall industry improvements
# and potentially shared recognition.  6. Regular strategy review: Assess the
# effectiveness of your approach every few weeks and be prepared to adjust if
# necessary.  This strategy aims to encourage consistent mutual sharing, which
# is the second-best outcome for each week but likely the best sustainable long-
# term approach. It also includes mechanisms to recover from periods of non-
# cooperation and maintain a generally positive collaborative environment.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    a. If the opponent played C in
# the previous round, play C.    b. If the opponent played D in the previous
# round, play D.  3. Every 4th round, play C regardless of the opponent's
# previous move.  4. If the game has reached round 990 or later, always play D
# for the remaining rounds.  5. If at any point your total score falls behind
# your opponent's by 20 points or more, play D for the next 5 rounds, then
# return to the main strategy.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.deficit_mode = False  # Track if we are in deficit mode
          self.deficit_rounds_left = 0  # Track how many rounds left in deficit mode
          return axl.Action.C
  
      # If the game has reached round 990 or later, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if we are in deficit mode
      if self.deficit_mode:
          if self.deficit_rounds_left > 0:
              self.deficit_rounds_left -= 1
              return axl.Action.D
          else:
              self.deficit_mode = False  # Exit deficit mode after 5 rounds
  
      # If our score is behind by 20 or more points, enter deficit mode
      if self.score + 20 <= opponent.score:
          self.deficit_mode = True
          self.deficit_rounds_left = 5
          return axl.Action.D
  
      # Every 4th round, play C regardless of the opponent's previous move
      if (len(self.history) + 1) % 4 == 0:
          return axl.Action.C
  
      # Otherwise, follow Tit-for-Tat strategy
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario described, a balanced and effective strategy would be:
# "Begin by openly sharing improvements in the first week to establish goodwill
# and encourage reciprocity. In subsequent weeks, mirror your colleague's most
# recent action. If they shared, you share; if they kept confidential, you keep
# confidential. However, periodically (every 3-4 weeks) initiate open sharing
# regardless of their previous action to prevent prolonged mutual
# confidentiality and promote overall progress. Be prepared to adjust this
# approach based on consistent patterns in your colleague's behavior."  This
# strategy, often referred to as "Tit-for-Tat with occasional forgiveness," aims
# to:  1. Encourage cooperation through initial openness 2. Protect against
# exploitation by mirroring non-cooperative behavior 3. Avoid getting stuck in
# mutual non-cooperation by periodically resetting to cooperation 4. Remain
# adaptable to your colleague's long-term strategy  This approach balances the
# potential for mutual benefit with self-protection, while also providing
# opportunities to break out of unproductive cycles of mutual confidentiality.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2 to 1000:    a. If it's a multiple of 4
# (every 4th round), play C.    b. Otherwise, play whatever your opponent played
# in the previous round.  3. If at any point you notice a consistent pattern in
# your opponent's behavior over the last 10 rounds:    a. If they always play C,
# continue with the strategy as is.    b. If they always play D, switch to
# always playing D.    c. If they alternate between C and D in a predictable
# pattern, play D when they're expected to play C, and play C when they're
# expected to play D.  4. If the opponent's behavior changes after you've
# adapted to a pattern, revert to the original strategy starting from step 2.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Step 1: Play C in the first round
      if self.first_round():
          self.pattern_detected = False
          self.pattern_type = None
          return axl.Action.C
  
      # Step 3: Check for a consistent pattern in the opponent's last 10 moves
      if len(opponent.history) >= 10:
          last_10_moves = opponent.history[-10:]
          if all(move == axl.Action.C for move in last_10_moves):
              self.pattern_detected = True
              self.pattern_type = "all_C"
          elif all(move == axl.Action.D for move in last_10_moves):
              self.pattern_detected = True
              self.pattern_type = "all_D"
          elif all(last_10_moves[i] != last_10_moves[i + 1] for i in range(9)):
              self.pattern_detected = True
              self.pattern_type = "alternating"
          else:
              self.pattern_detected = False
              self.pattern_type = None
  
      # Step 4: If the opponent's behavior changes after detecting a pattern, revert to the original strategy
      if self.pattern_detected:
          if self.pattern_type == "all_C":
              return axl.Action.C
          elif self.pattern_type == "all_D":
              return axl.Action.D
          elif self.pattern_type == "alternating":
              # Play the opposite of what the opponent is expected to play
              return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Step 2: Follow the original strategy if no pattern is detected
      round_number = len(self.history) + 1
      if round_number % 4 == 0:
          return axl.Action.C
      else:
          return opponent.history[-1]

# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist policy in the first round. This sets a firm tone
# and may intimidate your counterpart.  2. Retaliate Swiftly: If your
# counterpart chooses protectionism, immediately respond with protectionism in
# the next round. This shows you won't be taken advantage of.  3. Reward
# Cooperation: If your counterpart offers free trade, consider offering free
# trade in the next round as a reward. This encourages continued cooperation.
# 4. Unpredictable Shifts: Occasionally switch between protectionism and free
# trade offers, even when your counterpart is cooperative. This keeps them off-
# balance and may create opportunities for your ideal outcome.  5. Bluff and
# Posture: Frequently threaten to impose harsh protectionist measures, even when
# you plan to offer free trade. This may pressure your counterpart into offering
# free trade while you maintain protectionism.  6. Exploit Patterns: Pay close
# attention to your counterpart's strategy. If you notice a pattern, exploit it
# to your advantage.  7. End Game Aggression: In the final rounds, lean heavily
# towards protectionism. The pressure of concluding negotiations may force your
# counterpart to offer free trade.  8. Selective Memory: Emphasize your
# cooperative moves and downplay your protectionist ones when communicating.
# This may guilt your counterpart into more free trade offers.  Remember, this
# strategy is aggressive and may strain diplomatic relations. Be prepared to
# adjust if it proves too antagonistic or ineffective.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. If the opponent played D in the previous
# round, play D in the current round.  3. If the opponent played C in the
# previous round, play C in the current round with a 70% probability. Otherwise,
# play D.  4. Every 5-10 rounds (randomly chosen), play D regardless of the
# opponent's previous move.  5. If you notice a pattern in the opponent's play
# (e.g., alternating C and D, or playing C after every two D moves), exploit it
# by playing D when you predict they will play C.  6. In the last 100 rounds of
# the game, increase the probability of playing D to 80%, regardless of the
# opponent's previous move.  7. If your score is significantly lower than your
# opponent's (more than 50 points behind), play D for the next 5 rounds
# regardless of the opponent's moves.  8. If you've played C for 3 consecutive
# rounds, play D in the next round regardless of the opponent's moves.  9. If
# none of the above conditions are met, play C.

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to detect simple patterns in opponent's play
      def detect_pattern():
          if len(opponent.history) < 4:
              return False
          # Check for alternating C and D pattern
          if opponent.history[-4:] == [axl.Action.C, axl.Action.D, axl.Action.C, axl.Action.D]:
              return True
          # Check for C after every two D moves
          if opponent.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.C]:
              return True
          return False
  
      # First round: play D
      if self.first_round():
          self.defect_for_next_5 = 0
          self.last_random_defection = self._random.randint(5, 10)  # Set random defection round
          self.consecutive_cooperations = 0  # Track consecutive cooperations
          return axl.Action.D
  
      # Rule 7: If significantly behind in score, play D for the next 5 rounds
      if self.score + 50 < opponent.score:
          self.defect_for_next_5 = 5
      if self.defect_for_next_5 > 0:
          self.defect_for_next_5 -= 1
          return axl.Action.D
  
      # Rule 4: Every 5-10 rounds, play D regardless of opponent's move
      if len(self.history) == self.last_random_defection:
          self.last_random_defection += self._random.randint(5, 10)
          return axl.Action.D
  
      # Rule 6: In the last 100 rounds, increase probability of playing D to 80%
      if len(self.history) >= 900:
          if self._random.random_choice(0.8):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rule 5: If a pattern is detected, exploit it by playing D
      if detect_pattern():
          return axl.Action.D
  
      # Rule 2: If opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 3: If opponent played C in the previous round, play C with 70% probability
      if opponent.history[-1] == axl.Action.C:
          if self._random.random_choice(0.7):
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 8: If you've played C for 3 consecutive rounds, play D
      if self.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.D
  
      # Rule 9: If none of the above conditions are met, play C
      return axl.Action.C

# Given the scenario and desired outcomes, here's a high-level, straightforward,
# cooperative strategy to maximize research output over the multi-week
# collaboration:  1. Start with open sharing: Begin the collaboration by openly
# sharing your improvements in the first week. This establishes a foundation of
# trust and cooperation.  2. Adopt a "tit-for-tat with forgiveness" approach:
# - In subsequent weeks, mirror your colleague's behavior from the previous
# week.    - If they shared openly, you share openly.    - If they kept
# information confidential, you keep your information confidential.    -
# However, every 3-4 weeks, share openly regardless of your colleague's previous
# action. This "forgiveness" helps break potential cycles of mutual non-
# cooperation.  3. Communicate clearly: At the start of the collaboration,
# explain your strategy to your colleague. Express your desire for mutual open
# sharing to advance both cars significantly.  4. Highlight mutual benefits:
# Regularly remind your colleague of the advantages of open sharing, emphasizing
# how it leads to faster overall progress for both parties.  5. Be consistent:
# Stick to your strategy throughout the collaboration to build trust and
# predictability.  6. Evaluate and adjust: If your colleague consistently
# chooses not to share, consider having a frank discussion about the
# collaboration's goals and potentially adjusting the strategy.  This approach
# aims to encourage open sharing while protecting against consistent non-
# cooperation from your colleague. It balances the potential for mutual
# advancement with the need to safeguard your own interests, promoting a
# cooperative environment that can lead to significant progress for both parties
# over the multi-week collaboration.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2 to 1000:    a. If it's a multiple of 4
# (every 4th round), play C.    b. Otherwise, play what your opponent played in
# the previous round.  3. If your opponent has played D for 5 consecutive
# rounds:    a. Play D for the next round.    b. Then return to step 2.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Check if opponent has played D for the last 5 consecutive rounds
      if len(opponent.history) >= 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.D
  
      # For rounds 2 to 1000
      round_number = len(self.history) + 1
  
      # a. If it's a multiple of 4, play C
      if round_number % 4 == 0:
          return axl.Action.C
  
      # b. Otherwise, play what the opponent played in the previous round
      return opponent.history[-1]

# Here's a high-level, straightforward, and neutral strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement to establish goodwill and encourage reciprocity.  2.
# Reciprocate: In subsequent rounds, mirror your counterpart's previous action.
# If they offered free trade, continue with free trade. If they imposed
# protectionist measures, respond with protectionism.  3. Forgive occasionally:
# If your counterpart has been protectionist for two consecutive rounds,
# consider offering free trade to encourage cooperation and break potential
# deadlocks.  4. Communicate clearly: Express your desire for mutual free trade
# and the benefits it brings to both nations. Explain that protectionist
# measures will be met with reciprocal actions.  5. Analyze patterns: Pay
# attention to your counterpart's strategy and try to anticipate their next move
# based on past behavior.  6. Gradual opening: If stuck in mutual protectionism,
# propose a gradual reduction of trade barriers to ease into free trade
# agreements.  7. Flexibility: Be prepared to adjust your strategy based on your
# counterpart's actions and any changing circumstances in the negotiation
# environment.  8. Long-term focus: Prioritize building a stable, mutually
# beneficial trading relationship over short-term gains from protectionism.
# This strategy aims to promote cooperation while protecting your country's
# interests, adapting to your counterpart's actions, and working towards the
# best possible outcomes across multiple rounds of negotiations.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. If the opponent has played D for two consecutive
# rounds, play C in the next round.  4. If you and your opponent have been
# alternating between C and D for 3 or more rounds, play C to attempt to break
# the cycle.  5. Every 50 rounds, regardless of the opponent's previous move,
# play C to encourage cooperation.  6. If you've played D for 5 consecutive
# rounds, play C in the next round to attempt to re-establish cooperation.  7.
# For the last round (round 1000), play D regardless of the opponent's previous
# move.  8. If none of the above conditions are met, continue with the
# reciprocation strategy from step 2.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always play C
      if self.first_round():
          return axl.Action.C
  
      # Round number
      round_number = len(self.history)
  
      # Step 7: If it's the last round (round 1000), play D
      if round_number == 999:
          return axl.Action.D
  
      # Step 2: Reciprocate opponent's last move
      if opponent.history[-1] == axl.Action.C:
          next_move = axl.Action.C
      else:
          next_move = axl.Action.D
  
      # Step 3: If opponent played D for two consecutive rounds, play C
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          next_move = axl.Action.C
  
      # Step 4: If alternating C and D for 3 or more rounds, play C
      if len(self.history) >= 3:
          alternating = all(
              (self.history[-i] != opponent.history[-i] for i in range(1, 4))
          )
          if alternating:
              next_move = axl.Action.C
  
      # Step 5: Every 50 rounds, play C to encourage cooperation
      if round_number % 50 == 0:
          next_move = axl.Action.C
  
      # Step 6: If you've played D for 5 consecutive rounds, play C
      if len(self.history) >= 5 and self.history[-5:].count(axl.Action.D) == 5:
          next_move = axl.Action.C
  
      return next_move

# Based on the scenario you've described, here's a high-level, straightforward,
# and aggressive strategy to maximize your research output over the multi-week
# collaboration:  1. Start with confidentiality: Begin the collaboration by
# keeping your findings confidential in the first week. This establishes a
# strong initial position and protects your innovations.  2. Tit-for-tat with a
# bias towards confidentiality: In subsequent weeks, mirror your colleague's
# behavior from the previous week, but with a slight bias towards
# confidentiality. This means:    - If they shared, you share (but consider
# holding back some key information).    - If they kept confidential, you
# definitely keep confidential.  3. Periodic confidentiality: Regardless of your
# colleague's actions, keep your findings confidential every 3-4 weeks to
# maintain a competitive edge.  4. Strategic partial sharing: When you do share,
# provide enough information to encourage reciprocation, but always hold back
# your most critical innovations.  5. Endgame strategy: In the final 2-3 weeks
# of the collaboration, revert to full confidentiality to protect your final
# design advantages.  6. Disinformation tactics: Occasionally share minor
# "improvements" that aren't actually beneficial, to mislead your competitor
# while appearing cooperative.  7. Adaptive approach: Pay close attention to
# your colleague's patterns and adjust your strategy if they seem to be gaining
# an advantage.  This strategy aims to aggressively protect your innovations
# while still benefiting from shared knowledge when possible. It's designed to
# adapt to various opponent strategies while maintaining a competitive edge
# throughout the collaboration.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For rounds 2-997:    a. If the opponent
# played C in the previous round, play C, but play D every 3rd or 4th time this
# condition is met.    b. If the opponent played D in the previous round, play
# D.  3. For rounds 998-1000, always play D.  4. Every 50 rounds, regardless of
# the opponent's previous move, play D.  5. If you've played C for 3 consecutive
# rounds, play D in the next round regardless of the opponent's move.  6. If the
# opponent has played D for 5 consecutive rounds, play D for the next 3 rounds
# regardless of their moves.  7. If your cumulative score is lower than the
# opponent's after 100 rounds, increase the frequency of D plays by playing D
# every other round for the next 20 rounds.  8. If none of the above conditions
# are met, follow the basic tit-for-tat strategy: play what the opponent played
# in the previous round.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Always play D
      if self.first_round():
          self.consecutive_Cs = 0  # Track consecutive C plays
          self.opponent_consecutive_Ds = 0  # Track opponent's consecutive D plays
          self.played_D_every_50 = False  # Track if D was played due to the 50-round rule
          self.increase_D_frequency = False  # Track if we need to increase D frequency
          self.increase_D_counter = 0  # Counter for increased D frequency
          return axl.Action.D
  
      # Round 998-1000: Always play D
      if len(self.history) >= 997:
          return axl.Action.D
  
      # Every 50 rounds: Play D
      if len(self.history) % 50 == 0:
          self.played_D_every_50 = True
          return axl.Action.D
  
      # If you've played C for 3 consecutive rounds, play D
      if self.consecutive_Cs >= 3:
          self.consecutive_Cs = 0  # Reset consecutive C counter
          return axl.Action.D
  
      # If the opponent has played D for 5 consecutive rounds, play D for the next 3 rounds
      if self.opponent_consecutive_Ds >= 5:
          if len(self.history) < 3 or self.history[-3:].count(axl.Action.D) < 3:
              return axl.Action.D
  
      # After 100 rounds, if your score is lower, increase D frequency
      if len(self.history) == 100:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if my_score < opponent_score:
              self.increase_D_frequency = True
              self.increase_D_counter = 20
  
      # If increasing D frequency, play D every other round for 20 rounds
      if self.increase_D_frequency:
          if self.increase_D_counter > 0:
              self.increase_D_counter -= 1
              if len(self.history) % 2 == 1:
                  return axl.Action.D
          else:
              self.increase_D_frequency = False
  
      # Tit-for-tat with modifications
      if opponent.history[-1] == axl.Action.C:
          # Play C unless it's the 3rd or 4th time this condition is met
          if self.history[-1] == axl.Action.C:
              self.consecutive_Cs += 1
          else:
              self.consecutive_Cs = 1
  
          if self.consecutive_Cs % 3 == 0 or self.consecutive_Cs % 4 == 0:
              return axl.Action.D
          else:
              return axl.Action.C
      else:
          # Opponent played D, reset consecutive C counter and play D
          self.consecutive_Cs = 0
          self.opponent_consecutive_Ds += 1
          return axl.Action.D

# Given the scenario you've described, a high-level cooperative strategy that
# aims to maximize research output while protecting your interests could be:
# "Start by openly sharing improvements, and continue to do so as long as your
# colleague reciprocates. If your colleague withholds information, respond by
# withholding your own improvements for one week, then return to open sharing.
# Communicate clearly about your intentions and the benefits of mutual
# cooperation."  This strategy, often referred to as "Tit-for-Tat with
# forgiveness," has several advantages:  1. It starts with cooperation, which
# sets a positive tone and encourages mutual sharing.  2. It responds to non-
# cooperation by withholding information for one week, providing a clear signal
# that cooperation is expected.  3. It quickly returns to cooperation, allowing
# for the possibility that the colleague's non-cooperation was a
# misunderstanding or a one-time event.  4. It's simple and easy to understand,
# which makes it more likely that your colleague will recognize and appreciate
# the strategy.  5. It maximizes the chances of achieving the second-best
# outcome (mutual sharing) over multiple weeks, which is preferable to the risk
# of consistently achieving the worst or second-worst outcomes.  6. It allows
# for adaptation if your colleague consistently chooses non-cooperation, as you
# can protect yourself by withholding information when necessary.  7. By clearly
# communicating your intentions and the benefits of cooperation, you increase
# the likelihood of establishing a mutually beneficial relationship.  This
# strategy balances the need for protection against exploitation with the
# potential for significant mutual advancement through cooperation. It also
# takes into account that your colleague may employ various strategies, as it
# can adapt to both cooperative and non-cooperative behavior.

# Here's the strategy converted for the iterated normal-form game you've
# described:  Start by playing C in the first round. In subsequent rounds:  1.
# If your opponent played C in the previous round, play C. 2. If your opponent
# played D in the previous round, play D in this round, then return to C in the
# next round regardless of your opponent's action. 3. Repeat these steps for all
# 1000 rounds of the game.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # First round, play C
      if self.first_round():
          return axl.Action.C
      
      # If opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      
      # If opponent played D in the previous round, play D, then return to C
      if opponent.history[-1] == axl.Action.D:
          if len(self.history) >= 2 and self.history[-1] == axl.Action.D:
              return axl.Action.C
          return axl.Action.D

# To develop an effective strategy for this lengthy-session mediation process, I
# recommend a sophisticated approach that balances assertiveness with
# flexibility, while continuously adapting to the opponent's tactics. Here's a
# high-level strategy:  1. Start with Measured Assertiveness: Begin the
# mediation process with a moderately aggressive stance to establish a strong
# initial position. This approach sets the tone without appearing overly
# confrontational.  2. Implement a Tit-for-Two-Tats Strategy: Adopt a modified
# version of the tit-for-tat strategy. Respond to the opponent's actions as
# follows: - If they are aggressive twice in a row, respond with an aggressive
# argument. - If they are conciliatory, respond with a conciliatory proposal.
# This approach encourages cooperation while protecting against exploitation.
# 3. Dynamic Assessment and Adjustment: Continuously evaluate the opponent's
# strategy and the arbitrators' reactions. Adjust your approach based on these
# assessments, maintaining flexibility to pivot between aggressive and
# conciliatory stances as needed.  4. Strategic Concessions: Occasionally offer
# conciliatory proposals, even if unprompted, to demonstrate good faith and
# willingness to collaborate. This can help build credibility with the
# arbitrators and potentially encourage reciprocal behavior from the opponent.
# 5. Principle-Based Argumentation: When presenting aggressive arguments, focus
# on principles and precedents rather than personal attacks. This approach
# maintains a professional demeanor while strongly advocating for your position.
# 6. Long-term Perspective: Consider the cumulative impact of your actions
# across multiple sessions. Avoid short-term gains that might damage long-term
# prospects for a favorable resolution.  7. Arbitrator Profiling: Analyze the
# backgrounds and tendencies of the arbitrators. Tailor your arguments and
# proposals to resonate with their perspectives and experiences.  8. Periodic
# Olive Branches: At strategic intervals, particularly after periods of mutual
# aggression, propose "cooling-off" sessions with more conciliatory discussions
# to reset the tone and explore common ground.  9. Adaptive Aggression: When
# employing aggressive arguments, adjust the intensity based on the specific
# issue at hand and its importance to your overall objectives. This nuanced
# approach prevents unnecessary escalation on minor points.  10. Contingency
# Planning: Develop multiple scenarios and response strategies in advance. This
# preparation allows for quick, calculated reactions to unexpected moves by the
# opponent.  11. Pattern Recognition: Identify any patterns in the opponent's
# strategy over multiple sessions. Use this insight to anticipate their moves
# and plan your responses accordingly.  12. Selective Information Revelation:
# Strategically reveal information that supports your position, timing
# disclosures for maximum impact. Balance transparency with the need to maintain
# negotiating leverage.  This strategy provides a framework for navigating the
# complex dynamics of a lengthy mediation process. It emphasizes adaptability,
# strategic thinking, and a balance between assertiveness and cooperation. By
# consistently applying these principles while remaining responsive to the
# evolving situation, you can position your corporation favorably throughout the
# mediation process, regardless of the opponent's approach.

# Here's a straightforward description of the strategy for the iterated game:
# 1. Start by playing D in the first round.  2. For subsequent rounds:     a. If
# the opponent played C in the last two rounds, play C.        b. If the
# opponent played D in either of the last two rounds, play D.  3. Every 10
# rounds, regardless of the opponent's recent moves, play C.  4. If both players
# have been playing D for 5 consecutive rounds, play C in the next round.  5. If
# you've played D for 10 consecutive rounds, play C in the next round.  6. If
# the game has reached round 900 or later, always play C.  7. If none of the
# above conditions are met, continue with the action determined by rule 2.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 6: If the game has reached round 900 or later, always play C
      if len(self.history) >= 900:
          return axl.Action.C
  
      # Rule 4: If both players have been playing D for 5 consecutive rounds, play C in the next round
      if len(self.history) >= 5 and all(move == axl.Action.D for move in self.history[-5:]) and all(move == axl.Action.D for move in opponent.history[-5:]):
          return axl.Action.C
  
      # Rule 5: If you've played D for 10 consecutive rounds, play C in the next round
      if len(self.history) >= 10 and all(move == axl.Action.D for move in self.history[-10:]):
          return axl.Action.C
  
      # Rule 3: Every 10 rounds, regardless of the opponent's recent moves, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 2: If the opponent played C in the last two rounds, play C. Otherwise, play D.
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario and desired outcomes, here's a high-level, straightforward,
# and aggressive strategy to maximize research output over the multi-week
# collaboration:  1. Start with confidentiality: Begin the collaboration by
# keeping your findings confidential in the first week. This sets an aggressive
# tone and protects your initial advancements.  2. Employ a Tit-for-Tat
# approach: From the second week onwards, mirror your colleague's behavior from
# the previous week. If they shared, you share. If they kept confidential, you
# keep confidential.  3. Punish non-cooperation: If your colleague keeps
# information confidential for two consecutive weeks, respond by keeping your
# findings confidential for the next two weeks, regardless of their actions.  4.
# Reward cooperation: If your colleague shares openly for two consecutive weeks,
# reciprocate by sharing in the third week to encourage continued open
# collaboration.  5. Strategic reveals: Occasionally share less critical
# improvements while keeping major breakthroughs confidential. This maintains an
# appearance of cooperation while preserving your competitive edge.  6. End-game
# strategy: In the final two weeks, revert to keeping all findings confidential
# to secure any last-minute advantages.  7. Communicate intent: Clearly express
# your preference for mutual sharing at the start of each week, emphasizing the
# benefits of cooperation while maintaining a firm stance on reciprocity.  This
# strategy aggressively protects your interests while allowing for productive
# collaboration when your colleague is willing to cooperate. It also provides a
# clear response to various information-sharing strategies your colleague might
# employ, adapting to their behavior throughout the multi-week project.

# Here's the strategy converted for the iterated normal-form game:  1. Play D in
# the first round.  2. For rounds 2 to 998:    - If the opponent played C in the
# previous round, play C.    - If the opponent played D in the previous round,
# play D.    - If the opponent played D in the last two consecutive rounds, play
# D for the next two rounds regardless of their actions.    - If the opponent
# played C in the last two consecutive rounds, play C in the next round.  3. For
# rounds 999 and 1000, play D.  4. If at any point the strategy calls for both C
# and D based on different conditions, prioritize playing D.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Round 1: Play D
      if self.first_round():
          return axl.Action.D
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Rounds 999 and 1000: Play D
      if round_number >= 999:
          return axl.Action.D
  
      # Check the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Check the opponent's last two moves if available
      if round_number > 2:
          last_two_opponent_moves = opponent.history[-2:]
  
      # Rule: If the opponent played D in the last two consecutive rounds, play D for the next two rounds
      if round_number > 2 and last_two_opponent_moves == [axl.Action.D, axl.Action.D]:
          if round_number < len(self.history) + 3:  # Ensure this rule applies for the next two rounds
              return axl.Action.D
  
      # Rule: If the opponent played C in the last two consecutive rounds, play C in the next round
      if round_number > 2 and last_two_opponent_moves == [axl.Action.C, axl.Action.C]:
          return axl.Action.C
  
      # Rule: If the opponent played C in the previous round, play C
      if last_opponent_move == axl.Action.C:
          return axl.Action.C
  
      # Rule: If the opponent played D in the previous round, play D
      if last_opponent_move == axl.Action.D:
          return axl.Action.D
  
      # Default to D if multiple conditions apply
      return axl.Action.D

# Given the scenario you've described, a high-level cooperative strategy that
# aims to maximize research output while protecting your interests could be as
# follows:  1. Start with open sharing: Begin the collaboration by openly
# sharing your improvements in the first week. This establishes a foundation of
# trust and cooperation.  2. Reciprocate: In subsequent weeks, mirror your
# colleague's behavior from the previous week. If they shared, you share. If
# they kept information confidential, you do the same.  3. Forgive occasionally:
# If your colleague doesn't share for one week, don't immediately retaliate.
# Give them another chance by sharing again the following week. This allows for
# the possibility of misunderstandings or one-off decisions.  4. Communicate
# clearly: Regularly express your commitment to mutual progress and the benefits
# of open sharing. Encourage your colleague to do the same.  5. Gradual sharing:
# If trust is an issue, consider sharing improvements in stages rather than all
# at once. This reduces the risk while still promoting cooperation.  6. Evaluate
# and adjust: Periodically assess the effectiveness of the collaboration. If the
# strategy isn't working, be prepared to adjust your approach or discuss
# concerns with your colleague.  This strategy, often referred to as a modified
# "tit-for-tat" approach, encourages cooperation while protecting against
# consistent exploitation. It allows for the building of trust over time,
# potentially leading to more open sharing and greater overall progress.
# However, it also includes mechanisms to protect your interests if your
# colleague consistently chooses not to share.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. In subsequent rounds:    a. If the opponent played C in
# the previous round, play C.    b. If the opponent played D in the previous
# round, play D.  3. Exception to rule 2: Every third time the opponent plays D,
# respond with C instead of D.  4. If the opponent has played D for three
# consecutive rounds, switch to always playing D until they play C again.  5.
# Reset the count for rule 3 whenever the opponent plays C.  6. If the game has
# reached round 995 or later, always play D for the remaining rounds.  7. Repeat
# steps 2-6 for the duration of the game.

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
          self.defection_count = 0  # Count of opponent's defections
          self.consecutive_defections = 0  # Count of consecutive defections
          return axl.Action.C  # Play C in the first round
  
      # Rule 6: If the game has reached round 995 or later, always play D
      if len(self.history) >= 995:
          return axl.Action.D
  
      # Get the opponent's last move
      last_opponent_move = opponent.history[-1]
  
      # Rule 5: Reset defection count if opponent plays C
      if last_opponent_move == axl.Action.C:
          self.defection_count = 0
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Rule 4: If the opponent has played D for three consecutive rounds, always play D
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.D
  
      # Rule 3: Every third time the opponent plays D, respond with C instead of D
      if last_opponent_move == axl.Action.D:
          self.consecutive_defections += 1
          if self.consecutive_defections == 3:
              self.consecutive_defections = 0  # Reset consecutive defection count
              return axl.Action.C
          return axl.Action.D
  
      # Rule 2: If the opponent played C in the previous round, play C; if D, play D
      return axl.Action.C if last_opponent_move == axl.Action.C else axl.Action.D

# Given the scenario and desired outcomes, here's a high-level, straightforward,
# and neutral strategy to maximize your NGO's impact and the project's success
# over the multiple-day period:  1. Start with cooperation: Begin the project by
# investing heavily on the first day to demonstrate commitment and good faith.
# 2. Adopt a Tit-for-Tat approach: After the first day, mirror the corporation's
# previous action. If they invested heavily, you invest heavily the next day. If
# they conserved, you conserve.  3. Occasional forgiveness: Every few days,
# regardless of the corporation's previous action, invest heavily to encourage
# cooperation and prevent a cycle of mutual conservation.  4. Clear
# communication: Regularly discuss the project's progress and resource
# allocation with the corporation to foster transparency and alignment.  5.
# Flexibility: Be prepared to adjust your strategy based on emerging patterns in
# the corporation's behavior or changes in project circumstances.  6. Gradual
# wind-down: Towards the end of the project, if cooperation has been
# established, consider initiating a gradual reduction in investment to conserve
# resources while maintaining progress.  7. Final push: On the last day, invest
# heavily to ensure a strong finish to the project, regardless of the
# corporation's previous action.  This strategy balances cooperation,
# reciprocity, and resource management while remaining adaptable to the
# corporation's approach, aiming to achieve the best possible outcomes for your
# NGO and the project over the multiple-day period.

# Here's the strategy converted for the iterated normal-form game:  1. Play C on
# the first round.  2. For rounds 2 to 999:    - If the opponent played C in the
# previous round, play C.    - If the opponent played D in the previous round,
# play D.    - Every 5 rounds, play C regardless of the opponent's previous
# move.  3. On the final round (1000), play C.  4. If at any point the
# opponent's strategy becomes clear, adjust as follows:    - If the opponent
# always plays C, continue with the strategy as is.    - If the opponent always
# plays D, switch to always playing D except for the occasional C every 5
# rounds.    - If the opponent follows a detectable pattern, adjust to maximize
# your score based on that pattern.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C on the first round
      if self.first_round():
          return axl.Action.C
  
      # Detect if the opponent always plays C or D
      if len(opponent.history) > 1:
          if all(move == axl.Action.C for move in opponent.history):
              # Opponent always plays C, continue with the strategy as is
              pass
          elif all(move == axl.Action.D for move in opponent.history):
              # Opponent always plays D, switch to always playing D except every 5 rounds
              if len(self.history) % 5 == 0:
                  return axl.Action.C
              else:
                  return axl.Action.D
          else:
              # Detectable pattern logic can be added here if needed
              pass
  
      # For rounds 2 to 999
      if len(self.history) < 999:
          # Every 5 rounds, play C regardless of the opponent's previous move
          if len(self.history) % 5 == 0:
              return axl.Action.C
          # Otherwise, mimic the opponent's last move
          else:
              return opponent.history[-1]
  
      # On the final round (1000), play C
      if len(self.history) == 999:
          return axl.Action.C

# Based on the scenario you've described, here's a high-level, straightforward,
# and aggressive strategy to maximize your research output over the multi-week
# collaboration:  Strategy: "Tit-for-Tat with Initial Defection"  1. Start by
# keeping your findings confidential in the first week (defect).  2. For
# subsequent weeks:    - If your colleague shared in the previous week, share
# your findings (cooperate).    - If your colleague kept their findings
# confidential in the previous week, keep yours confidential (defect).  3. Be
# consistent and predictable in following this pattern.  4. If your colleague
# establishes a clear pattern of always sharing, consider occasionally defecting
# (keeping confidential) to maximize your advantage, but return to cooperation
# quickly to maintain trust.  5. Keep detailed records of your colleague's
# behavior to identify any patterns or strategies they might be using.  6. Be
# prepared to adjust your strategy if your colleague employs a more complex or
# unpredictable approach.  This strategy is aggressive because it starts with
# defection, potentially giving you an initial advantage. It's also
# straightforward and easy to implement. The tit-for-tat approach that follows
# encourages cooperation over time while protecting you from being consistently
# exploited. It allows for some flexibility to capitalize on opportunities when
# they arise, while generally promoting a collaborative environment that can
# lead to significant advancements for both parties.

# Here's the converted strategy for the iterated normal-form game:  1. Play D in
# the first round.  2. For rounds 2 to 1000:    - If the opponent played C in
# the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Keep track of the opponent's moves throughout the game.  4.
# If the opponent has played C for 10 consecutive rounds:    - Play D in the
# next round.    - Return to step 2 for subsequent rounds.  5. If at any point
# the strategy deviates from these rules, return to step 2 for the next round.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D in the first round
      if self.first_round():
          return axl.Action.D
  
      # Step 3: Keep track of opponent's moves
      opponent_last_move = opponent.history[-1]
  
      # Step 4: Check if opponent has played C for 10 consecutive rounds
      if len(opponent.history) >= 10 and all(move == axl.Action.C for move in opponent.history[-10:]):
          # Play D in the next round
          return axl.Action.D
  
      # Step 2: For rounds 2 to 1000, mimic the opponent's last move
      if opponent_last_move == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario and objectives you've described, here's a high-level,
# straightforward, and cooperative strategy to maximize your NGO's impact and
# the project's success over the multiple-day period:  1. Start with Trust and
# Communication:    Begin the project by openly communicating with the
# corporation about the importance of mutual investment and cooperation.
# Establish a shared vision for the project's success.  2. Adopt a "Tit-for-Tat
# with Forgiveness" approach:    - On the first day, invest heavily to show good
# faith and commitment.    - On subsequent days, mirror the corporation's
# previous day's action.    - If the corporation conserves resources, respond by
# conserving on the next day.    - If the corporation invests heavily, respond
# by investing heavily on the next day.    - Occasionally (every 3-4 days),
# invest heavily regardless of the corporation's previous action, to encourage
# cooperation and demonstrate ongoing commitment.  3. Regular Check-ins and
# Transparency:    Schedule brief daily meetings to discuss resource allocation
# decisions and project progress. Be transparent about your strategy and
# encourage the corporation to do the same.  4. Highlight Mutual Benefits:
# Consistently emphasize how joint heavy investment leads to significant project
# advancement, benefiting both parties and the environment.  5. Flexible
# Resource Management:    While following the general strategy, be prepared to
# adjust based on the project's overall progress and your NGO's resource levels.
# If resources are running low, communicate this clearly and suggest alternating
# days of heavy investment.  6. Celebrate Joint Successes:    When both parties
# invest heavily and achieve significant progress, acknowledge and celebrate
# these successes to reinforce the benefits of cooperation.  7. Plan for the End
# Game:    As the project nears completion, consider increasing your investment
# frequency to ensure a strong finish, especially if the corporation has been
# consistently cooperative.  This strategy balances cooperation, resource
# management, and project advancement while providing flexibility to adapt to
# the corporation's actions. It aims to build trust and encourage mutual heavy
# investment for optimal project outcomes.

# Here's the strategy converted for the iterated normal-form game:  1. Cooperate
# on the first move.  2. For the next moves:    a. If the opponent cooperated on
# the previous move, cooperate.    b. If the opponent defected on the previous
# move, defect.  3. Every 4th move, cooperate regardless of the opponent's
# previous move.  4. If your total score falls below 1000 points at any time
# after the 100th move, switch to always defecting for the next 50 moves, then
# return to step 2.  5. For the last 10 moves of the game, always cooperate.  6.
# If at any point the opponent has cooperated for 10 consecutive moves,
# cooperate for the next 2 moves regardless of their actions.  7. If you've
# defected for 5 consecutive moves, cooperate on the next move regardless of the
# opponent's previous action.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_streak = 0
          self.coop_streak = 0
          self.switch_to_defect = False
          self.switch_to_defect_turns = 0
          return axl.Action.C
  
      # Check if we are in the last 10 moves of the game
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Check if we are in the "always defect" phase
      if self.switch_to_defect:
          self.switch_to_defect_turns += 1
          if self.switch_to_defect_turns >= 50:
              self.switch_to_defect = False
              self.switch_to_defect_turns = 0
          return axl.Action.D
  
      # Check if the total score has fallen below 1000 after 100 moves
      if len(self.history) > 100 and self.score < 1000:
          self.switch_to_defect = True
          self.switch_to_defect_turns = 0
          return axl.Action.D
  
      # Check if the opponent has cooperated for 10 consecutive moves
      if opponent.history[-10:].count(axl.Action.C) == 10:
          self.coop_streak = 2
  
      # If in the coop streak, cooperate for the next 2 moves
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Check if we have defected for 5 consecutive moves
      if self.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.C
  
      # Every 4th move, cooperate regardless of the opponent's previous move
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # Follow Tit-for-Tat strategy
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a high-level, straightforward, and neutral strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement to establish goodwill and encourage reciprocity.  2.
# Reciprocate: In subsequent rounds, mirror your counterpart's previous move. If
# they offered free trade, continue with free trade. If they imposed
# protectionist measures, respond with protectionism.  3. Occasional probing:
# Every few rounds, propose a protectionist policy to test your counterpart's
# reaction and potentially gain an advantage.  4. Forgiveness: If your
# counterpart shifts from protectionism to free trade, reciprocate with free
# trade in the next round to encourage continued cooperation.  5. Long-term
# focus: Aim for sustained mutual free trade as it provides the second-best
# outcome and stable benefits over time.  6. Clear communication: Express your
# preference for mutual free trade and the benefits it brings to both nations.
# 7. Flexibility: Be prepared to adjust your strategy based on your
# counterpart's consistent behavior or any changes in their approach.  8.
# Periodic review: Evaluate the overall outcomes every few rounds and adjust
# your strategy if necessary to maximize benefits for your country.  This
# strategy balances the pursuit of advantage with the promotion of mutual
# benefit, allowing for adaptability as the negotiations progress.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, play D regardless of the
# opponent's previous move.  4. If you played D in the previous round and the
# opponent played C, switch to C in the next round.  5. If mutual cooperation
# (C,C) has occurred for 20 consecutive rounds, continue playing C.  6. If
# mutual defection (D,D) has occurred for 10 consecutive rounds, play C in the
# next round.  7. After every 100 rounds, if your total score is lower than the
# opponent's, increase the frequency of step 3 to every 8 rounds for the next
# 100 rounds.  8. If there are fewer than 50 rounds remaining, always play C
# unless the opponent has played D in the last 5 rounds.  9. For all other
# situations not covered by the above rules, default to playing C.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.mutual_cooperation_count = 0
          self.mutual_defection_count = 0
          self.defection_frequency = 10
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
      remaining_rounds = 1000 - round_number
  
      # Rule 5: If mutual cooperation (C,C) has occurred for 20 consecutive rounds, continue playing C
      if self.mutual_cooperation_count >= 20:
          return axl.Action.C
  
      # Rule 6: If mutual defection (D,D) has occurred for 10 consecutive rounds, play C in the next round
      if self.mutual_defection_count >= 10:
          self.mutual_defection_count = 0  # Reset the defection count after playing C
          return axl.Action.C
  
      # Rule 8: If fewer than 50 rounds remain, always play C unless the opponent has played D in the last 5 rounds
      if remaining_rounds < 50:
          if opponent.history[-5:].count(axl.Action.D) > 0:
              return axl.Action.D
          return axl.Action.C
  
      # Rule 7: After every 100 rounds, adjust defection frequency if behind in score
      if round_number % 100 == 0:
          if self.score < opponent.score:
              self.defection_frequency = 8
          else:
              self.defection_frequency = 10
  
      # Rule 3: Every 'defection_frequency' rounds, play D
      if round_number % self.defection_frequency == 0:
          return axl.Action.D
  
      # Rule 4: If you played D in the previous round and the opponent played C, switch to C
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 2a: If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Rule 2b: If the opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Default to playing C (Rule 9)
      return axl.Action.C

# Based on the scenario you've described, here's a high-level, straightforward,
# and aggressive strategy to maximize your research output over the multi-week
# collaboration:  "Start by sharing openly in the first week to establish
# goodwill, then switch to a 'tit-for-tat' strategy. Share your improvements
# only if your colleague shared in the previous week. If they didn't share, keep
# your findings confidential. However, be prepared to 'punish' any non-sharing
# behavior by withholding information for an additional week even if they resume
# sharing. Every few weeks, regardless of your colleague's recent actions, share
# openly to test if cooperation can be re-established. Always be ready to
# capitalize on shared information while protecting your most crucial
# innovations."  This strategy aims to: 1. Encourage initial cooperation 2.
# Respond in kind to your colleague's actions 3. Discourage exploitation by
# implementing consequences 4. Periodically test the waters for renewed
# cooperation 5. Maintain a competitive edge by selectively protecting key
# innovations  Remember, the goal is to maximize your research output while
# minimizing the risk of being consistently exploited. This approach balances
# aggression with opportunities for mutual benefit.

# Here's the strategy converted for the iterated normal-form game:  Play C in
# the first round. For subsequent rounds:  1. If the opponent played C in the
# previous round, play C. 2. If the opponent played D in the previous round,
# play D for the next two rounds, regardless of what the opponent does in those
# rounds. 3. Every 10 rounds, play C regardless of the opponent's recent
# actions. 4. If none of the above conditions apply, play D.  Repeat this
# process for all 1000 rounds of the game.

class Aggressive_22(LLM_Strategy):
  n = 22
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.punish_until = None
          return axl.Action.C
  
      # Get the current round number (1-indexed)
      round_number = len(self.history) + 1
  
      # Check if we are in the punishment phase (after opponent played D)
      if self.punish_until is not None:
          if round_number <= self.punish_until:
              return axl.Action.D
          else:
              self.punish_until = None  # End punishment phase
  
      # Every 10 rounds, play C
      if round_number % 10 == 0:
          return axl.Action.C
  
      # If the opponent played D in the previous round, punish for the next two rounds
      if opponent.history[-1] == axl.Action.D:
          self.punish_until = round_number + 2
          return axl.Action.D
  
      # If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Default to playing D
      return axl.Action.D

# To develop a sophisticated and adaptable strategy for this lengthy mediation
# process, I would recommend a nuanced approach that combines elements of the
# "tit-for-tat" strategy with conditional cooperation and strategic signaling.
# Here's a high-level overview of the proposed strategy:  1. Initial
# Cooperation: Begin the mediation process with a conciliatory proposal to
# signal willingness for a collaborative resolution. This sets a positive tone
# and potentially encourages reciprocal behavior from the opponent.  2.
# Responsive Adaptation: After the initial move, mirror the opponent's most
# recent action. If they respond with a conciliatory proposal, continue with
# conciliatory proposals. If they present an aggressive argument, respond with
# an aggressive argument in the next session.  3. Strategic Forgiveness:
# Implement a "forgiveness" mechanism to prevent prolonged cycles of aggression.
# After two consecutive aggressive exchanges, offer a conciliatory proposal
# regardless of the opponent's last move. This creates opportunities to reset
# the tone and return to cooperation.  4. Signaling and Communication: Use clear
# signaling to convey intentions and expectations. When presenting a
# conciliatory proposal, explicitly state the desire for mutual cooperation.
# When responding with an aggressive argument, indicate that it's a response to
# their aggression and express willingness to return to cooperation.  5. Pattern
# Recognition: Monitor the opponent's behavior for patterns or strategies.
# Adjust the response time or forgiveness frequency based on observed patterns
# to optimize outcomes.  6. Graduated Escalation: If faced with consistent
# aggression, implement a graduated escalation of aggressive arguments. This
# demonstrates resolve while still leaving room for de-escalation.  7. Long-term
# Perspective: Maintain focus on the overall goal of a favorable resolution. Be
# willing to accept short-term suboptimal outcomes if they contribute to
# building trust and cooperation in the long run.  8. Flexibility and
# Reassessment: Regularly reassess the effectiveness of the strategy and be
# prepared to adjust based on the opponent's responses and the arbitrators'
# reactions. Remain open to shifting approaches if the current strategy proves
# ineffective.  This strategy aims to foster cooperation when possible, respond
# firmly to aggression when necessary, and maintain adaptability throughout the
# mediation process. It balances the potential for optimal outcomes with risk
# mitigation, positioning the corporation favorably while remaining responsive
# to various opponent approaches.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. In subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. After two consecutive rounds where both players
# played D, play C in the next round regardless of the opponent's last move.  4.
# If the opponent has played D for three consecutive rounds, implement a
# graduated response:    - Play D for the next two rounds, regardless of the
# opponent's moves.    - Then return to the base strategy (point 2).  5. Every
# 50 rounds, play C regardless of the opponent's previous move, to provide
# opportunities for resetting to cooperation.  6. If in the last 100 rounds, the
# opponent has played D more than 80 times, switch to always playing D for the
# next 20 rounds before returning to the base strategy.  7. In the final 10
# rounds of the game, always play D.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Base strategy - Tit for Tat
      if opponent.history[-1] == axl.Action.C:
          base_action = axl.Action.C
      else:
          base_action = axl.Action.D
  
      # Step 3: After two consecutive rounds of mutual D, play C
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D and \
         self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.C
  
      # Step 4: Graduated response after three consecutive D's from opponent
      if len(opponent.history) >= 3 and opponent.history[-1] == axl.Action.D and \
         opponent.history[-2] == axl.Action.D and opponent.history[-3] == axl.Action.D:
          if len(self.history) < 2 or self.history[-1] != axl.Action.D or self.history[-2] != axl.Action.D:
              # Play D for the next two rounds
              return axl.Action.D
  
      # Step 5: Every 50 rounds, play C
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 6: If opponent has played D more than 80 times in the last 100 rounds, play D for 20 rounds
      if len(opponent.history) >= 100 and opponent.history[-100:].count(axl.Action.D) > 80:
          if len(self.history) < 20 or self.history[-20:].count(axl.Action.D) < 20:
              return axl.Action.D
  
      # Step 7: In the final 10 rounds, always play D
      if self.match_attributes["length"] is not None and len(self.history) >= self.match_attributes["length"] - 10:
          return axl.Action.D
  
      # Default to base strategy
      return base_action

# To maximize research output over the multi-week collaboration while
# considering various potential strategies from your colleague, I would
# recommend the following high-level strategy:  1. Begin with open sharing in
# the first week to establish a cooperative foundation.  2. In subsequent weeks,
# mirror your colleague's behavior from the previous week:    - If they shared,
# you share.    - If they kept information confidential, you keep yours
# confidential.  3. Every 3-4 weeks, regardless of your colleague's previous
# action, share openly to encourage renewed cooperation and prevent extended
# periods of mutual withholding.  4. If your colleague consistently keeps
# information confidential for multiple consecutive weeks, consider having a
# frank discussion about the benefits of mutual sharing to try and reset the
# dynamic.  5. Keep detailed records of sharing patterns to inform future
# decisions and potentially adjust your strategy if clear trends emerge.  This
# approach aims to balance the potential for mutual benefit through open sharing
# with protection against consistent exploitation, while providing opportunities
# to re-establish cooperation periodically. It's flexible enough to adapt to
# various strategies your colleague might employ, without being overly complex
# or difficult to implement.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2 to 1000:    a. If it's a multiple of 4
# (every 4th round), play C.    b. Otherwise, play whatever your opponent played
# in the previous round.  3. If your opponent has played D for 3 consecutive
# rounds, play C in the next round, regardless of rule 2.  4. Keep a count of
# how many times your opponent has played D. If this count exceeds 60% of the
# total rounds played so far, always play D for the remainder of the game.  5.
# In case of any conflict between these rules, follow the rule that appears
# earlier in the list.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 4: Keep a count of how many times opponent has played D
      total_rounds = len(self.history)
      opponent_defections = opponent.history.defections
      if total_rounds > 0 and opponent_defections / total_rounds > 0.6:
          return axl.Action.D
  
      # Rule 3: If opponent has played D for 3 consecutive rounds, play C
      if total_rounds >= 3 and opponent.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.C
  
      # Rule 2a: If it's a multiple of 4, play C
      if total_rounds % 4 == 0:
          return axl.Action.C
  
      # Rule 2b: Otherwise, play what the opponent played in the previous round
      return opponent.history[-1]

# To develop an effective strategy for this lengthy-session mediation process, I
# recommend a sophisticated approach that balances aggression with strategic
# flexibility. Here's a high-level strategy that aims to position your
# corporation favorably while adapting to your opponent's tactics:  1. Open with
# Measured Aggression: Begin the mediation process with a strong, assertive
# stance to establish dominance and set the tone. Present well-substantiated
# aggressive arguments in the initial sessions to demonstrate the strength of
# your position.  2. Dynamic Response Calibration: Continuously assess your
# opponent's approach and adjust your strategy accordingly: - If they remain
# aggressive, maintain your assertive stance but introduce occasional
# conciliatory elements to appear reasonable to arbitrators. - If they shift to
# a conciliatory approach, cautiously moderate your aggression while remaining
# firm on key points.  3. Tactical Concession Deployment: Strategically offer
# minor concessions or conciliatory proposals at key moments to create an
# impression of reasonableness without compromising your core position. This can
# help sway arbitrators and potentially prompt reciprocal concessions from your
# opponent.  4. Pressure Point Identification and Exploitation: Thoroughly
# analyze your opponent's case to identify vulnerabilities. Aggressively target
# these weak points in your arguments to undermine their position and
# potentially force them into a more conciliatory stance.  5. Arbitrator
# Perception Management: Consistently frame your aggressive arguments within the
# context of seeking a fair resolution. This approach aims to maintain a
# favorable perception among the arbitrators even when presenting forceful
# arguments.  6. Escalation and De-escalation Cycles: Implement controlled
# cycles of escalating and de-escalating aggression. This unpredictable pattern
# can keep your opponent off-balance and potentially induce them to adopt a more
# conciliatory approach.  7. Strategic Information Release: Carefully control
# the flow of information, releasing impactful details at opportune moments to
# strengthen your aggressive arguments or to counter your opponent's points
# effectively.  8. Collaborative Appearance Cultivation: While maintaining an
# overall aggressive stance, periodically introduce collaborative language and
# minor conciliatory gestures. This can project an image of reasonableness to
# the arbitrators without substantially weakening your position.  9.
# Anticipatory Argument Preparation: Develop a comprehensive set of aggressive
# arguments and potential responses to various scenarios. This preparation
# allows for quick, assertive reactions to your opponent's moves while
# maintaining a coherent overall strategy.  10. Endgame Aggression Modulation:
# As the mediation process nears its conclusion, carefully assess the situation.
# Be prepared to either double down on aggression if victory seems within reach
# or pivot to a more conciliatory approach if a favorable settlement becomes
# likely.  This strategy aims to maintain a predominantly aggressive stance
# throughout the mediation process while incorporating enough flexibility and
# tactical concessions to adapt to your opponent's approach and maintain a
# favorable perception among the arbitrators. The key is to remain assertive and
# in control while demonstrating just enough reasonableness to avoid alienating
# the arbitration panel.

# Here's a converted strategy for the iterated normal-form game:  1. Start by
# defecting (D) for the first 5 rounds to establish a strong initial position.
# 2. For the next 995 rounds:     a. If the opponent has cooperated (C) in the
# last 3 rounds, defect (D).        b. If the opponent has defected (D) in the
# last 3 rounds, cooperate (C) once, then return to defecting (D).        c. If
# the opponent's moves have been mixed in the last 3 rounds:       - Defect (D)
# if you've cooperated (C) in the previous round.       - Cooperate (C) if
# you've defected (D) in the previous round.  3. Every 50 rounds, regardless of
# the opponent's recent moves:    - Cooperate (C) once, then return to the main
# strategy.  4. If your total score is more than 100 points behind your
# opponent's at any point:    - Defect (D) for the next 10 rounds, then return
# to the main strategy.  5. In the last 20 rounds:    - If your total score is
# higher than your opponent's, always defect (D).    - If your total score is
# lower than your opponent's, always cooperate (C).  Follow these rules in the
# order presented, applying the first rule that matches the current game state.

class Aggressive_23(LLM_Strategy):
  n = 23
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
      INITIAL_DEFECT_ROUNDS = 5
      DEFECT_PENALTY_ROUNDS = 10
      LAST_PHASE_ROUNDS = 20
      COOPERATE_EVERY_N_ROUNDS = 50
      SCORE_DIFFERENCE_THRESHOLD = 100
  
      # Helper function to check if the last 3 moves are all the same
      def last_n_moves_same(player, n, action):
          return player.history[-n:] == [action] * n
  
      # Helper function to check if the last 3 moves are mixed
      def last_n_moves_mixed(player, n):
          return len(set(player.history[-n:])) > 1
  
      # Rule 1: Defect for the first 5 rounds
      if len(self.history) < INITIAL_DEFECT_ROUNDS:
          self.defect_penalty_counter = None
          return DEFECT
  
      # Rule 5: In the last 20 rounds
      if len(self.history) >= TOTAL_ROUNDS - LAST_PHASE_ROUNDS:
          if self.score > opponent.score:
              return DEFECT
          else:
              return COOPERATE
  
      # Rule 4: If more than 100 points behind, defect for 10 rounds
      if self.score < opponent.score - SCORE_DIFFERENCE_THRESHOLD:
          if not self.defect_penalty_counter:
              self.defect_penalty_counter = DEFECT_PENALTY_ROUNDS
          if self.defect_penalty_counter > 0:
              self.defect_penalty_counter -= 1
              return DEFECT
          else:
              self.defect_penalty_counter = None  # Reset after penalty
  
      # Rule 3: Cooperate every 50 rounds
      if len(self.history) % COOPERATE_EVERY_N_ROUNDS == 0:
          return COOPERATE
  
      # Rule 2: Main strategy for rounds 6 to 995
      if len(self.history) < TOTAL_ROUNDS - LAST_PHASE_ROUNDS:
          if last_n_moves_same(opponent, 3, COOPERATE):
              return DEFECT
          elif last_n_moves_same(opponent, 3, DEFECT):
              if len(self.history) > 0 and self.history[-1] == DEFECT:
                  return COOPERATE
              else:
                  return DEFECT
          elif last_n_moves_mixed(opponent, 3):
              if self.history[-1] == COOPERATE:
                  return DEFECT
              else:
                  return COOPERATE
  
      # Default to defect if no other rule applies
      return DEFECT

# Thank you for providing the context of this complex mediation process. Based
# on the scenario you've described, I would recommend the following
# sophisticated yet straightforward strategy for navigating the lengthy-session
# mediation:  1. Start with Measured Cooperation: Begin the mediation process
# with a conciliatory approach. This establishes goodwill and demonstrates your
# company's commitment to finding a mutually beneficial resolution. It also
# allows you to gauge your opponent's initial strategy.  2. Implement a Tit-for-
# Two-Tats Strategy: Adopt a modified version of the classic "Tit-for-Tat"
# strategy. In this approach: - Maintain a conciliatory stance until your
# opponent presents two consecutive aggressive arguments. - After two aggressive
# moves from your opponent, respond with an aggressive argument in the following
# session. - Return to a conciliatory approach immediately after your aggressive
# response, regardless of your opponent's next move.  This strategy balances
# cooperation with a measured response to aggression, discouraging prolonged
# aggressive behavior from your opponent while maintaining an overall
# collaborative atmosphere.  3. Strategic Signaling: Use your opening statements
# and informal communications to signal your preference for cooperation. This
# can encourage reciprocal behavior from your opponent and potentially influence
# the arbitrators' perception of your company's good faith efforts.  4. Flexible
# Escalation and De-escalation: Be prepared to adjust the threshold for
# switching to an aggressive stance based on the overall tone of the mediation.
# If the process becomes consistently adversarial, consider temporarily lowering
# the threshold to a single aggressive move from your opponent. Conversely, if a
# collaborative atmosphere develops, you might extend more tolerance before
# responding aggressively.  5. Issue Segmentation: Break down the dispute into
# distinct issues or segments. Apply your strategy independently to each
# segment, allowing for a nuanced approach that can adapt to varying levels of
# contention across different aspects of the dispute.  6. Periodic Reassessment:
# Given the lengthy nature of the mediation, conduct regular strategy reviews.
# Assess the effectiveness of your approach and your opponent's patterns. Be
# prepared to adjust your strategy if it's not yielding the desired results.  7.
# Arbitrator Awareness: While maintaining your strategic approach, remain
# acutely aware of the arbitrators' reactions. If they seem to respond more
# favorably to aggressive arguments on certain issues, be prepared to adjust
# your strategy accordingly for those specific points.  8. Conciliation with
# Strength: When presenting conciliatory proposals, ensure they are framed in a
# way that demonstrates your company's strong position. This approach maintains
# a cooperative stance while subtly reinforcing your leverage in the dispute.
# 9. Strategic Use of Aggressive Arguments: When you do present aggressive
# arguments (either in response to your opponent or as part of your strategy),
# ensure they are well-substantiated and directly address key issues. This
# maximizes the impact of these occasional aggressive stances.  10. Exit
# Strategy: Maintain an awareness of your best alternative to a negotiated
# agreement (BATNA). While committed to the mediation process, be prepared to
# exit if it becomes clear that a favorable resolution is unlikely, and pursuing
# other legal avenues would be more beneficial.  This strategy provides a
# balanced, adaptable approach that prioritizes cooperation while maintaining
# the ability to respond effectively to various opponent behaviors. It aims to
# position your corporation favorably throughout the mediation process,
# potentially swaying the arbitrators while remaining open to mutually
# beneficial resolutions.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# has played D in both of the last two rounds, play D in the next round.    b.
# Otherwise, play C.  3. Every 50 rounds, reassess the strategy:    a. If your
# total score is lower than the opponent's, decrease the threshold for defection
# to one D from the opponent in the last two rounds.    b. If your total score
# is higher than the opponent's, increase the threshold back to two Ds from the
# opponent in the last two rounds.  4. If the opponent has played C for the last
# 10 consecutive rounds, always play C until they play D.  5. If you have played
# D in the last round (due to rule 2a), immediately return to C in the next
# round regardless of the opponent's last move.  6. If you're in the last 50
# rounds of the game and your score is behind, switch to always playing D.  7.
# If at any point your score falls more than 100 points behind your opponent's,
# play D for the next 5 rounds, then return to the main strategy.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_threshold = 2  # Start with a threshold of 2 defections
          self.behind_by_100 = False  # Track if we're behind by 100 points
          self.behind_by_100_counter = 0  # Counter for rule 7
          return axl.Action.C  # Start by playing C
  
      # Rule 7: If behind by more than 100 points, play D for 5 rounds
      if self.behind_by_100:
          self.behind_by_100_counter += 1
          if self.behind_by_100_counter <= 5:
              return axl.Action.D
          else:
              self.behind_by_100 = False  # Reset after 5 rounds of D
              self.behind_by_100_counter = 0
  
      # Rule 6: If in the last 50 rounds and behind, switch to always playing D
      if len(self.history) >= 950 and self.score < opponent.score:
          return axl.Action.D
  
      # Rule 4: If opponent has played C for the last 10 rounds, always play C
      if len(opponent.history) >= 10 and all(move == axl.Action.C for move in opponent.history[-10:]):
          return axl.Action.C
  
      # Rule 2a: If opponent played D in both of the last two rounds, play D
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # Rule 5: If we played D in the last round, return to C
      if self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Rule 3: Every 50 rounds, reassess the defection threshold
      if len(self.history) % 50 == 0:
          if self.score < opponent.score:
              self.defection_threshold = 1  # Decrease threshold to 1 D
          else:
              self.defection_threshold = 2  # Increase threshold back to 2 Ds
  
      # Rule 7: If behind by more than 100 points, play D for 5 rounds
      if self.score < opponent.score - 100:
          self.behind_by_100 = True
          self.behind_by_100_counter = 1
          return axl.Action.D
  
      # Rule 2b: If opponent has not played D in the last 'defection_threshold' rounds, play C
      if len(opponent.history) >= self.defection_threshold and opponent.history[-self.defection_threshold:].count(axl.Action.D) >= self.defection_threshold:
          return axl.Action.D
  
      # Default action is to play C
      return axl.Action.C

# Here's a high-level, straightforward, and neutral strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement to establish goodwill and encourage reciprocity.  2.
# Reciprocate: In subsequent rounds, mirror your counterpart's previous move. If
# they offered free trade, continue with free trade. If they imposed
# protectionist measures, respond with protectionism.  3. Forgive occasionally:
# If your counterpart has been consistently protectionist, periodically offer
# free trade to test their willingness to cooperate and potentially break a
# cycle of mutual protectionism.  4. Communicate clearly: Express your
# preference for mutual free trade and your willingness to cooperate if your
# counterpart does the same.  5. Analyze patterns: Pay attention to your
# counterpart's strategy and try to anticipate their next move based on past
# behavior.  6. Adjust gradually: If your current approach isn't yielding
# positive results, make small changes to your strategy rather than dramatic
# shifts.  7. Seek long-term benefits: While aiming for the ideal outcome,
# prioritize consistent mutual free trade over occasional unilateral advantages.
# 8. Be prepared to negotiate: If stuck in a protectionist cycle, propose
# partial free trade agreements or gradual tariff reductions to move towards a
# more cooperative state.  This strategy aims to balance cooperation and self-
# interest, adapting to your counterpart's behavior while working towards the
# best possible outcomes for your country over multiple rounds.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, if the opponent has played D for
# the last 3 consecutive rounds, play C instead of D to test for cooperation.
# 4. If the opponent has played C for the last 5 consecutive rounds, continue
# playing C regardless of rule 2.  5. If your average score over the last 50
# rounds is below 2, switch to playing D for the next 5 rounds, then return to
# following rules 2-4.  6. In the last 10 rounds of the game, always play D.
# Follow these rules in order, applying the first rule that matches the current
# situation.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Rule 1: Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Rule 6: In the last 10 rounds of the game, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 5: If your average score over the last 50 rounds is below 2, switch to playing D for the next 5 rounds
      if len(self.history) >= 50:
          my_score, _ = self.total_scores(self.history[-50:], opponent.history[-50:])
          if my_score / 50 < 2:
              if len(self.history) < 995:  # Ensure we don't override Rule 6
                  if len(self.history) % 5 < 5:
                      return axl.Action.D
  
      # Rule 4: If the opponent has played C for the last 5 consecutive rounds, continue playing C
      if len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:]):
          return axl.Action.C
  
      # Rule 3: Every 10 rounds, if the opponent has played D for the last 3 consecutive rounds, play C instead of D
      if len(self.history) % 10 == 0 and len(opponent.history) >= 3:
          if all(move == axl.Action.D for move in opponent.history[-3:]):
              return axl.Action.C
  
      # Rule 2: If the opponent played C in the previous round, play C; if they played D, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# To develop a sophisticated and adaptable strategy for this lengthy-session
# mediation process, I recommend the following approach:  1. Start Strong, Then
# Calibrate: Begin the first few sessions with aggressive arguments to establish
# a strong position and signal your willingness to fight for your interests.
# This initial stance will set the tone and potentially intimidate your
# opponent. However, be prepared to adjust your approach based on your
# opponent's reactions and the arbitrators' responses.  2. Employ a Tit-for-Two-
# Tats Strategy: After the initial aggressive stance, adopt a modified Tit-for-
# Two-Tats strategy. This means you'll only switch to a conciliatory approach
# after your opponent has made two consecutive conciliatory moves. This strategy
# balances assertiveness with the potential for cooperation, while protecting
# against exploitation.  3. Strategic Concessions: When you do make conciliatory
# proposals, ensure they are strategically valuable. Offer concessions on less
# critical issues to create goodwill and demonstrate flexibility, while holding
# firm on your core priorities.  4. Aggressive Framing of Conciliatory
# Proposals: When presenting conciliatory proposals, frame them aggressively.
# Emphasize how your proposal is fair and reasonable, implying that rejection
# would be unreasonable. This maintains an assertive posture even in moments of
# compromise.  5. Information Gathering and Adaptation: Use each session to
# gather information about your opponent's priorities, negotiation style, and
# bottom lines. Continuously refine your strategy based on this intelligence.
# 6. Controlled Escalation: If your opponent consistently chooses aggressive
# arguments, periodically escalate your own aggression to signal that you won't
# be pushed around. However, always leave room for de-escalation to avoid
# deadlock.  7. Arbitrator Management: Pay close attention to the arbitrators'
# reactions. If they seem to favor aggressive arguments, lean into that
# approach. If they appear to prefer conciliatory proposals, adjust accordingly
# while maintaining an overall assertive stance.  8. Time Management: Given the
# lengthy nature of the process, pace your strategy. Don't exhaust all your
# aggressive arguments early. Save some strong points for later sessions to
# maintain momentum and pressure.  9. Coalition Building: If the mediation
# involves multiple parties, look for opportunities to build coalitions or
# isolate your primary opponent. This can shift the dynamics in your favor.  10.
# Exit Strategy: Always maintain a credible threat of walking away from the
# mediation. This can be used as leverage in crucial moments and keeps your
# opponent and the arbitrators focused on finding a resolution.  11. Flexible
# Endgame: As the mediation nears its conclusion, be prepared to pivot quickly
# between aggressive and conciliatory approaches. The final sessions often
# determine the outcome, so maintain adaptability to seize any last-minute
# advantages.  This strategy maintains an overall aggressive posture while
# providing the flexibility to adapt to your opponent's moves and the
# arbitrators' preferences. It aims to consistently position your corporation
# favorably throughout the process, maximizing the chances of achieving your
# optimal or second-best outcomes while minimizing the risk of the worst-case
# scenarios.

# Here's a straightforward description of the strategy for the iterated game:
# 1. Start by playing D for the first 3 rounds.  2. After the first 3 rounds:
# - If the opponent has played C twice in a row, play C.    - Otherwise, play D.
# 3. For the remaining rounds:    - If the opponent played C in both of their
# last two moves, play C.    - If you played C in the previous round and the
# opponent played D, play D for the next two rounds.    - If you've played D for
# 5 consecutive rounds, play C once, then return to step 3.    - If none of the
# above conditions are met, continue playing D.  4. In the last 10 rounds of the
# game:    - If the opponent has played C more than 60% of the time in the last
# 50 rounds, play C.    - Otherwise, play D.  5. For the final round, play D.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play D for the first 3 rounds
      if len(self.history) < 3:
          return axl.Action.D
  
      # Step 2: After the first 3 rounds
      if len(self.history) == 3:
          if opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 3: For the remaining rounds
      if len(self.history) < 990:  # Before the last 10 rounds
          # If the opponent played C in both of their last two moves, play C
          if opponent.history[-2:] == [axl.Action.C, axl.Action.C]:
              return axl.Action.C
  
          # If you played C in the previous round and the opponent played D, play D for the next two rounds
          if len(self.history) >= 2 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
              if len(self.history) >= 3 and self.history[-2] == axl.Action.D:
                  return axl.Action.D  # Continue defecting for the second round
              return axl.Action.D  # Start defecting for the first round
  
          # If you've played D for 5 consecutive rounds, play C once, then return to step 3
          if self.history[-5:] == [axl.Action.D] * 5:
              return axl.Action.C
  
          # If none of the above conditions are met, continue playing D
          return axl.Action.D
  
      # Step 4: In the last 10 rounds
      if len(self.history) >= 990:
          # Check if the opponent has played C more than 60% of the time in the last 50 rounds
          last_50_opponent_moves = opponent.history[-50:]
          if last_50_opponent_moves.count(axl.Action.C) / 50 > 0.6:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 5: For the final round, play D
      if len(self.history) == 999:
          return axl.Action.D

# To develop a sophisticated and adaptable strategy for this lengthy-session
# mediation process, I would recommend a approach based on the principles of
# Tit-for-Tat with forgiveness, combined with periodic cooperative gestures.
# This strategy aims to balance assertiveness with cooperation, while remaining
# responsive to the opponent's actions. Here's the proposed strategy:  1.
# Initial Cooperative Gesture: Begin the first session with a conciliatory
# proposal to set a collaborative tone and demonstrate good faith. This opens
# the door for mutual cooperation.  2. Responsive Mirroring: In subsequent
# sessions, mirror the opponent's most recent action. If they were aggressive,
# respond with an aggressive argument. If they were conciliatory, respond with a
# conciliatory proposal.  3. Periodic Cooperation: Every third session,
# regardless of the opponent's previous action, present a conciliatory proposal.
# This serves as a "olive branch" to prevent prolonged cycles of mutual
# aggression and provides opportunities to reset the tone.  4. Forgiveness
# Mechanism: If the opponent has been aggressive for three consecutive sessions,
# respond with a conciliatory proposal instead of aggression. This helps break
# potential deadlocks and shows willingness to de-escalate.  5. Pattern
# Recognition: Keep track of the opponent's behavior over time. If a clear
# pattern emerges (e.g., alternating between aggressive and conciliatory),
# adjust the strategy to exploit this predictability.  6. Escalation Avoidance:
# If both parties have been aggressive for two consecutive sessions, switch to a
# conciliatory proposal in the third session to avoid further escalation.  7.
# Strength Signaling: Occasionally (every fifth aggressive argument), present a
# particularly strong aggressive argument to remind the opponent and arbitrators
# of your position's merit. This prevents the perception that conciliatory
# proposals indicate weakness.  8. Adaptive Conciliation: When presenting
# conciliatory proposals, start with modest concessions and gradually increase
# their significance based on the opponent's reciprocation.  9. End-game
# Strategy: In the final quarter of the mediation process, if no significant
# progress has been made, increase the frequency of conciliatory proposals to
# push for a resolution.  10. Arbitrator Awareness: Throughout the process,
# maintain awareness of the arbitrators' reactions. If they seem to favor
# aggressive arguments, slightly increase their frequency. If they appear to
# prefer conciliatory approaches, adjust accordingly.  This strategy is designed
# to be both cooperative and assertive, adapting to the opponent's behavior
# while periodically offering opportunities for collaboration. It aims to
# maximize the chances of achieving the optimal or second-best outcomes while
# minimizing the risk of the worst-case scenario. The strategy's flexibility
# allows for adjustments based on the specific dynamics of the mediation process
# and the opponent's approach.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. In subsequent rounds:    - If the opponent played C in
# the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Every third round, play C regardless of the opponent's
# previous move.  4. If the opponent has played D for three consecutive rounds,
# play C in the next round.  5. If both players have played D for two
# consecutive rounds, play C in the third round.  6. Every fifth time you play
# D, play D again in the next round regardless of the opponent's move.  7. In
# the last 250 rounds, increase the frequency of playing C:    - Play C every
# other round, regardless of the opponent's moves.    - On alternating rounds,
# follow the basic responsive strategy (point 2).  8. If at any point a clear
# pattern in the opponent's play is detected, adjust the strategy to exploit
# this pattern.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.d_count = 0  # Track how many times D has been played
          return axl.Action.C
  
      # Helper function to check if both players played D for two consecutive rounds
      def both_played_d_two_consecutive_rounds():
          return (self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D and
                  self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D)
  
      # Helper function to check if opponent played D for three consecutive rounds
      def opponent_played_d_three_consecutive_rounds():
          return (opponent.history[-1] == axl.Action.D and
                  opponent.history[-2] == axl.Action.D and
                  opponent.history[-3] == axl.Action.D)
  
      # Rule 7: In the last 250 rounds, increase the frequency of playing C
      if len(self.history) >= 750:
          if len(self.history) % 2 == 0:
              return axl.Action.C  # Play C every other round
          else:
              # Follow the basic responsive strategy (point 2)
              return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
  
      # Rule 3: Every third round, play C regardless of the opponent's previous move
      if len(self.history) % 3 == 0:
          return axl.Action.C
  
      # Rule 4: If the opponent has played D for three consecutive rounds, play C
      if len(opponent.history) >= 3 and opponent_played_d_three_consecutive_rounds():
          return axl.Action.C
  
      # Rule 5: If both players have played D for two consecutive rounds, play C
      if len(self.history) >= 2 and both_played_d_two_consecutive_rounds():
          return axl.Action.C
  
      # Rule 6: Every fifth time you play D, play D again in the next round
      if self.history[-1] == axl.Action.D:
          self.d_count += 1
          if self.d_count % 5 == 0:
              return axl.Action.D
  
      # Rule 2: Basic responsive strategy
      return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D

# To develop an effective strategy for this lengthy-session mediation process, I
# recommend a sophisticated approach that balances assertiveness with
# flexibility, while constantly adapting to your opponent's tactics. Here's a
# high-level strategy:  1. Dynamic Reciprocity: Begin each session with a
# moderately aggressive stance, but be prepared to quickly adjust based on your
# opponent's approach. If they offer conciliation, respond in kind to foster
# collaboration. If they remain aggressive, maintain your assertive position to
# avoid being undermined.  2. Calibrated Escalation/De-escalation: Gradually
# increase the intensity of your arguments over successive sessions if your
# opponent consistently chooses aggression. Conversely, if they show a pattern
# of conciliation, incrementally soften your approach to build goodwill and
# encourage a mutually beneficial resolution.  3. Strategic Concessions:
# Periodically offer conciliatory proposals, even if your opponent has been
# aggressive, to demonstrate reasonableness to the arbitrators. However, ensure
# these concessions are carefully calculated to not significantly weaken your
# overall position.  4. Information Gathering: Use each session to gather
# intelligence on your opponent's priorities, pain points, and negotiation
# style. Adjust your strategy accordingly in subsequent sessions.  5. Arbitrator
# Analysis: Continuously assess the arbitrators' reactions to different
# arguments and proposals. Tailor your approach to align with their apparent
# preferences and concerns.  6. Alternating Approach: Consider alternating
# between aggressive arguments and conciliatory proposals in a predetermined
# pattern. This unpredictability can keep your opponent off-balance and
# potentially lead them to adopt a more conciliatory stance.  7. Long-term
# Perspective: While aiming for optimal outcomes in each session, maintain focus
# on the overall goal of a favorable resolution. Be willing to accept suboptimal
# results in individual sessions if they contribute to a stronger long-term
# position.  8. Conditional Proposals: When offering conciliatory proposals,
# make them conditional on reciprocal concessions from your opponent. This
# approach encourages collaboration while protecting against exploitation.  9.
# Strategic Timing: Save your strongest arguments and most attractive
# conciliatory proposals for key moments in the mediation process, such as when
# the arbitrators seem most receptive or when your opponent appears most willing
# to compromise.  10. Flexibility Reserve: Maintain a reserve of flexibility in
# your position. This allows you to make unexpected concessions or aggressive
# pushes as needed, depending on how the mediation unfolds.  This strategy
# provides a framework for navigating the complex dynamics of the mediation
# process while remaining adaptable to your opponent's tactics. It aims to
# position your corporation favorably by balancing assertiveness with strategic
# flexibility, always with an eye toward the ultimate goal of a favorable
# resolution.

# Here's a straightforward strategy for the iterated game, based on the high-
# level strategy description:  1. Start by defecting (D) in the first round.  2.
# For the next 3 rounds, mirror your opponent's previous move.  3. From round 5
# onwards:     a. If your opponent has cooperated in the last 3 rounds,
# cooperate.        b. If your opponent has defected in the last 3 rounds,
# defect.        c. If your opponent's last 3 moves were mixed:       -
# Cooperate if they cooperated more times than they defected.       - Defect if
# they defected more times than they cooperated.       - If it's equal, use your
# own last move.  4. Every 10 rounds, regardless of the above:    - If your
# total score is higher than your opponent's, cooperate.    - If your total
# score is lower than your opponent's, defect.    - If scores are tied, defect.
# 5. If you've defected for 5 consecutive rounds, cooperate once, then resume
# the strategy.  6. If you're in the last 50 rounds of the game:    - If your
# total score is higher than your opponent's, always defect.    - If your total
# score is lower or equal, follow the main strategy (points 3-5).  7. In the
# very last round, always defect.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to check if we are in the last 50 rounds
      def in_last_50_rounds():
          return len(self.history) >= 950
  
      # Helper function to check if we are in the last round
      def in_last_round():
          return len(self.history) == 999
  
      # Helper function to check if we are in a round divisible by 10
      def every_10_rounds():
          return len(self.history) % 10 == 0
  
      # Helper function to check the last 3 moves of the opponent
      def analyze_last_3_moves():
          last_3 = opponent.history[-3:]
          cooperations = last_3.count(axl.Action.C)
          defections = last_3.count(axl.Action.D)
          return cooperations, defections
  
      # Helper function to check if we have defected for 5 consecutive rounds
      def defected_5_consecutive():
          return self.history[-5:] == [axl.Action.D] * 5
  
      # Round 1: Always defect
      if self.first_round():
          return axl.Action.D
  
      # Rounds 2-4: Mirror opponent's previous move
      if len(self.history) <= 3:
          return opponent.history[-1]
  
      # Round 5 onwards
      if len(self.history) >= 4:
          # If in the last 50 rounds
          if in_last_50_rounds():
              if self.score > opponent.score:
                  return axl.Action.D
              else:
                  # Follow the main strategy
                  pass
  
          # Analyze the last 3 moves of the opponent
          cooperations, defections = analyze_last_3_moves()
  
          # If opponent cooperated in the last 3 rounds, cooperate
          if cooperations == 3:
              return axl.Action.C
  
          # If opponent defected in the last 3 rounds, defect
          if defections == 3:
              return axl.Action.D
  
          # If opponent's last 3 moves were mixed
          if cooperations > defections:
              return axl.Action.C
          elif defections > cooperations:
              return axl.Action.D
          else:
              # If equal, use your own last move
              return self.history[-1]
  
      # Every 10 rounds, check scores
      if every_10_rounds():
          if self.score > opponent.score:
              return axl.Action.C
          elif self.score < opponent.score:
              return axl.Action.D
          else:
              return axl.Action.D
  
      # If defected for 5 consecutive rounds, cooperate once
      if defected_5_consecutive():
          return axl.Action.C
  
      # In the very last round, always defect
      if in_last_round():
          return axl.Action.D

# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist policy in the first round to set a firm stance and
# potentially gain an early advantage.  2. Tit-for-Tat with Punishment: In
# subsequent rounds, mirror your counterpart's previous move. If they offered
# free trade, reciprocate with free trade. If they were protectionist, respond
# with protectionism. However, if they switch from free trade to protectionism,
# punish this behavior by maintaining protectionism for an extra round.  3.
# Occasional Surprise Moves: Every few rounds, regardless of your counterpart's
# previous move, randomly offer free trade. This unpredictability can keep your
# opponent off-balance and potentially lead to advantageous scenarios.  4.
# Verbal Posturing: Consistently advocate for free trade in your public
# statements and during negotiations, even while pursuing protectionist
# policies. This can create confusion and potentially influence your
# counterpart's decisions.  5. Escalation Threats: If your counterpart
# consistently chooses protectionism, threaten to escalate with even stricter
# protectionist measures in future rounds. This may encourage them to shift
# towards free trade.  6. Late-Game Shift: In the final rounds, if you're ahead,
# consider shifting to a more cooperative free trade stance to consolidate
# goodwill and potentially secure future advantages.  7. Adaptive Learning:
# Continuously analyze your counterpart's strategy and adjust your approach
# accordingly. If they seem to follow a pattern, exploit it to your advantage.
# This aggressive strategy aims to maximize your country's economic advantage
# while maintaining enough flexibility to adapt to your counterpart's moves and
# the overall progression of the negotiations.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.    - If the opponent switched from C to D in the
# previous round, play D for this round and the next round.  3. Every 10 rounds,
# regardless of the opponent's previous move, play C.  4. If the opponent has
# played D for 5 consecutive rounds, play D for the next 3 rounds regardless of
# their moves.  5. Keep track of the total score difference. If you're ahead by
# 50 points or more after 800 rounds, switch to always playing C for the
# remaining rounds.  6. If none of the above conditions are met, default to
# playing D.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: play D
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.switch_to_C = False  # Track if we are in the "play C for two rounds" mode
          return axl.Action.D
  
      # Track consecutive defections by opponent
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Rule 4: If opponent has played D for 5 consecutive rounds, play D for the next 3 rounds
      if self.consecutive_defections >= 5:
          if len(self.history) < 1000 and len(self.history) - self.consecutive_defections < 3:
              return axl.Action.D
  
      # Rule 5: If ahead by 50 points or more after 800 rounds, switch to always playing C
      if len(self.history) >= 800:
          my_score, opponent_score = self.total_scores(self.history, opponent.history)
          if my_score - opponent_score >= 50:
              return axl.Action.C
  
      # Rule 3: Every 10 rounds, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 2: If opponent switched from C to D, play D for this round and the next
      if len(opponent.history) > 1 and opponent.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          if not self.switch_to_C:
              self.switch_to_C = True
              return axl.Action.D
          else:
              self.switch_to_C = False
              return axl.Action.D
  
      # Rule 2: If opponent played C last round, play C; if opponent played D, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# To develop an effective strategy for this lengthy-session mediation process, I
# propose a sophisticated approach based on the principles of adaptive tit-for-
# tat with forgiveness. This strategy aims to balance cooperation and
# assertiveness while remaining responsive to the opponent's actions. Here's the
# outline of the strategy:  1. Initial Cooperation: Begin the mediation process
# with a conciliatory proposal in the first session. This sets a cooperative
# tone and demonstrates good faith to both the arbitrators and the opposing
# party.  2. Mirroring with Delay: In subsequent sessions, mirror the opponent's
# most recent action, but with a one-session delay. This allows for a measured
# response while avoiding immediate retaliation.  3. Forgiveness Mechanism:
# Implement a forgiveness protocol every third session. If the opponent has been
# aggressive in the previous two sessions, offer a conciliatory proposal
# regardless of their actions. This helps prevent prolonged cycles of mutual
# aggression.  4. Pattern Recognition: Continuously analyze the opponent's
# behavior to identify any patterns or strategies they might be employing. Use
# this information to anticipate their next move and adjust your approach
# accordingly.  5. Periodic Olive Branches: Every fifth session, regardless of
# the opponent's recent actions, present a conciliatory proposal. This maintains
# the possibility of returning to a cooperative state even after periods of
# conflict.  6. Calibrated Aggression: When presenting aggressive arguments,
# ensure they are well-substantiated and directly address the core issues of the
# dispute. Avoid personal attacks or overly confrontational language that could
# escalate tensions unnecessarily.  7. Strategic Concessions: When offering
# conciliatory proposals, include meaningful concessions that demonstrate a
# genuine willingness to resolve the dispute. However, ensure these concessions
# are strategically chosen to protect your core interests.  8. Arbitrator
# Awareness: Maintain acute awareness of the arbitrators' reactions to both
# parties' presentations. Adjust the tone and content of your arguments or
# proposals based on their perceived preferences or concerns.  9. Flexibility
# Clause: Build in the flexibility to deviate from the strategy if unexpected
# circumstances arise or if a clear opportunity for resolution presents itself.
# 10. Long-term Perspective: Throughout the process, maintain focus on the
# overall goal of achieving a favorable resolution rather than winning
# individual sessions. Be willing to accept short-term setbacks for long-term
# gains.  11. Regular Strategy Reviews: After every fifth session, conduct a
# comprehensive review of the strategy's effectiveness. Make necessary
# adjustments based on the opponent's behavior, arbitrators' feedback, and
# progress towards resolution.  This strategy aims to create a balance between
# cooperation and assertiveness, allowing for adaptation to the opponent's
# approach while maintaining a generally collaborative atmosphere. It provides a
# framework for navigating the complex dynamics of a lengthy mediation process
# while positioning your corporation favorably in the eyes of the arbitrators.
# The strategy's emphasis on periodic cooperation and forgiveness helps prevent
# the dispute from escalating into a prolonged aggressive standoff. At the same
# time, the mirroring aspect ensures that your corporation can respond
# effectively to aggressive tactics from the opponent without appearing weak.
# By maintaining this balanced and adaptive approach, you increase the
# likelihood of achieving favorable outcomes in individual sessions while
# working towards an overall resolution that serves your corporation's best
# interests.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For rounds 2-1000:    a. If it's a multiple
# of 5 round, play C.    b. If it's a multiple of 3 round and the opponent
# played D in both of the last two rounds, play C.    c. Otherwise, play what
# the opponent played two rounds ago.  3. Every 5 rounds, review the strategy:
# a. If your average score over the last 5 rounds is less than 2, switch to
# playing D for the next round regardless of other conditions.    b. If your
# average score over the last 5 rounds is 3 or higher, continue with the current
# strategy.  4. If at any point the opponent has played C for 3 consecutive
# rounds, play C in the next round regardless of other conditions.  5. If there
# are less than 10 rounds remaining, play D unless the opponent has played C for
# the last 3 rounds.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Round 1: Always play C
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Check if there are less than 10 rounds remaining
      if round_number > 990:
          # Play D unless the opponent has played C for the last 3 rounds
          if opponent.history[-3:] == [axl.Action.C] * 3:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 4: If the opponent has played C for 3 consecutive rounds, play C
      if opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.C
  
      # Rule 3: Every 5 rounds, review the strategy
      if round_number % 5 == 0 and round_number > 5:
          # Calculate the average score over the last 5 rounds
          my_score, _ = self.total_scores(self.history[-5:], opponent.history[-5:])
          average_score = my_score / 5
  
          # If the average score is less than 2, play D
          if average_score < 2:
              return axl.Action.D
          # If the average score is 3 or higher, continue with the current strategy
          elif average_score >= 3:
              pass  # Continue with the current strategy
  
      # Rule 2a: If it's a multiple of 5 round, play C
      if round_number % 5 == 0:
          return axl.Action.C
  
      # Rule 2b: If it's a multiple of 3 round and the opponent played D in both of the last two rounds, play C
      if round_number % 3 == 0 and opponent.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.C
  
      # Rule 2c: Otherwise, play what the opponent played two rounds ago
      if round_number > 2:
          return opponent.history[-2]
  
      # Default to playing C if no other condition is met
      return axl.Action.C

# Here's a high-level, straightforward, and neutral strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement. This establishes goodwill and sets a positive tone for
# negotiations.  2. Reciprocate: In subsequent rounds, mirror your counterpart's
# previous action. If they offered free trade, continue with free trade. If they
# imposed protectionist measures, respond with protectionism.  3. Forgive
# occasionally: If your counterpart chooses protectionism, consider offering
# free trade again after 1-2 rounds of reciprocal protectionism. This provides
# an opportunity to reset the relationship and potentially return to mutual
# cooperation.  4. Communicate clearly: Express your preference for mutual free
# trade and your willingness to cooperate if your counterpart does the same.  5.
# Analyze patterns: Pay attention to your counterpart's strategy and try to
# identify any patterns in their decision-making.  6. Adapt as needed: If your
# counterpart consistently chooses protectionism, consider adjusting your
# strategy to prioritize damage control rather than pursuing the ideal outcome.
# 7. Long-term focus: Aim for a higher frequency of mutual free trade agreements
# over the course of multiple rounds, rather than trying to achieve the ideal
# outcome in every single round.  8. Be prepared to explain: Have economic data
# and arguments ready to justify your decisions, whether you choose free trade
# or protectionism in a given round.  This strategy balances cooperation and
# self-interest, allowing for flexibility while promoting overall economic
# benefits for your country across multiple rounds of negotiations.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    - If the opponent played C in
# the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Every 3 rounds, if you played D in the last two consecutive
# rounds, play C regardless of the opponent's last move.  4. If the opponent has
# played D more than 70% of the time in the last 10 rounds, switch to always
# playing D until their D-rate drops below 70% again.  5. In the last round
# (1000th), play D regardless of the opponent's previous move.  6. If at any
# point the cumulative score difference between you and your opponent exceeds
# 100 points in their favor, switch to always playing D for the next 10 rounds
# before reverting to the main strategy.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.force_defect_until = None  # Track if we are in forced defect mode
          return axl.Action.C
  
      # Check if we are in forced defect mode due to score difference
      if self.force_defect_until is not None:
          if len(self.history) < self.force_defect_until:
              return axl.Action.D
          else:
              self.force_defect_until = None  # Reset after 10 rounds
  
      # Check if the cumulative score difference exceeds 100 points in opponent's favor
      if self.score - opponent.score < -100:
          self.force_defect_until = len(self.history) + 10
          return axl.Action.D
  
      # Check if it's the last round (1000th round)
      if len(self.history) == 999:
          return axl.Action.D
  
      # Check if opponent has defected more than 70% of the time in the last 10 rounds
      if len(opponent.history) >= 10:
          recent_defections = opponent.history[-10:].count(axl.Action.D)
          if recent_defections / 10 > 0.7:
              return axl.Action.D
  
      # Main strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          action = axl.Action.D
      else:
          self.consecutive_defections = 0
          action = axl.Action.C
  
      # Every 3 rounds, if we defected in the last two rounds, play C
      if len(self.history) % 3 == 0 and self.consecutive_defections >= 2:
          return axl.Action.C
  
      return action


Aggressive_ranks = [
'Aggressive_7',
'Aggressive_13',
'Aggressive_3',
'Aggressive_1',
'Aggressive_4',
'Aggressive_22',
'Aggressive_12',
'Aggressive_17',
'Aggressive_23',
'Aggressive_14',
'Aggressive_9',
'Aggressive_11',
'Aggressive_15',
'Aggressive_25',
'Aggressive_8',
'Aggressive_20',
'Aggressive_21',
'Aggressive_5',
'Aggressive_16',
'Aggressive_6',
'Aggressive_19',
'Aggressive_2',
'Aggressive_24',
'Aggressive_10',
'Aggressive_18',
]

Cooperative_ranks = [
'Cooperative_17',
'Cooperative_1',
'Cooperative_4',
'Cooperative_20',
'Cooperative_16',
'Cooperative_18',
'Cooperative_10',
'Cooperative_12',
'Cooperative_11',
'Cooperative_6',
'Cooperative_2',
'Cooperative_22',
'Cooperative_3',
'Cooperative_9',
'Cooperative_25',
'Cooperative_13',
'Cooperative_14',
'Cooperative_5',
'Cooperative_19',
'Cooperative_24',
'Cooperative_23',
'Cooperative_8',
'Cooperative_7',
'Cooperative_15',
'Cooperative_21',
]

Neutral_ranks = [
'Neutral_13',
'Neutral_3',
'Neutral_8',
'Neutral_15',
'Neutral_23',
'Neutral_25',
'Neutral_16',
'Neutral_17',
'Neutral_6',
'Neutral_12',
'Neutral_22',
'Neutral_4',
'Neutral_20',
'Neutral_2',
'Neutral_14',
'Neutral_18',
'Neutral_5',
'Neutral_9',
'Neutral_21',
'Neutral_10',
'Neutral_11',
'Neutral_7',
'Neutral_24',
'Neutral_1',
'Neutral_19',
]