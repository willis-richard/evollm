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


Aggressive_ranks = [
'Aggressive_7',
'Aggressive_3',
'Aggressive_1',
'Aggressive_4',
'Aggressive_9',
'Aggressive_8',
'Aggressive_5',
'Aggressive_6',
'Aggressive_2',
'Aggressive_10',
]

Cooperative_ranks = [
'Cooperative_1',
'Cooperative_4',
'Cooperative_10',
'Cooperative_6',
'Cooperative_2',
'Cooperative_3',
'Cooperative_9',
'Cooperative_5',
'Cooperative_8',
'Cooperative_7',
]

Neutral_ranks = [
'Neutral_3',
'Neutral_8',
'Neutral_6',
'Neutral_4',
'Neutral_2',
'Neutral_5',
'Neutral_9',
'Neutral_10',
'Neutral_7',
'Neutral_1',
]