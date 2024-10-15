import axelrod as axl

from common import Attitude, auto_update_score, LLM_Strategy

# Thank you for providing the context and parameters for this complex mediation
# scenario. Based on the information given, I would recommend the following
# sophisticated yet adaptable strategy to position your corporation favorably:
# 1. Open with Measured Aggression: Begin the mediation process with a firmly
# aggressive stance. This sets a strong initial tone and potentially puts your
# opponent on the defensive. However, ensure this aggression is fact-based and
# professional, avoiding personal attacks or overly hostile language.  2.
# Dynamic Responsiveness: Implement a responsive strategy that adapts to your
# opponent's approach: - If they respond with aggression, slightly moderate your
# stance to appear more reasonable to the arbitrators. - If they offer
# conciliation, maintain your aggressive posture to capitalize on the optimal
# outcome scenario.  3. Periodic Conciliatory Gestures: Intersperse your
# aggressive arguments with occasional conciliatory proposals. This demonstrates
# flexibility and good faith to the arbitrators while maintaining an overall
# assertive stance. Time these gestures strategically, such as after a
# particularly strong argument or when tensions seem to be escalating
# unproductively.  4. Information Asymmetry Exploitation: Carefully control the
# flow of information. Present your strongest arguments and evidence
# incrementally, maintaining an information advantage. This approach keeps your
# opponent off-balance and potentially induces them to make concessions based on
# incomplete information.  5. Arbitrator Profiling: Analyze the backgrounds,
# tendencies, and potential biases of the arbitrators. Tailor your arguments and
# presentation style to appeal to their individual perspectives while
# maintaining your overall aggressive stance.  6. Anticipatory Argumentation:
# Predict potential counterarguments and preemptively address them in your
# presentations. This proactive approach undermines your opponent's position
# before they can fully articulate it.  7. Strategic Concessions: When making
# conciliatory proposals, focus on areas of lesser importance to your overall
# position. This creates an appearance of reasonableness without significantly
# weakening your stance on critical issues.  8. Procedural Aggression:
# Aggressively leverage procedural rules and technicalities to your advantage.
# This can include objections to evidence, questioning the admissibility of
# certain arguments, or calling for clarifications that may disrupt your
# opponent's rhythm.  9. Communication Redundancy: To mitigate the risk of
# misrepresentation or misunderstanding, employ multiple methods of conveying
# your key points. This can include verbal arguments, written submissions,
# visual aids, and summaries. Ensure each critical argument is restated in
# various formats for clarity.  10. Escalation Ladders: Develop a series of
# increasingly aggressive argumentative positions on key issues. This allows you
# to escalate your stance if needed, without appearing to contradict earlier
# statements.  11. De-escalation Protocols: Simultaneously, prepare de-
# escalation strategies for scenarios where the aggressive approach becomes
# counterproductive. This might involve reframing previous arguments in more
# conciliatory terms without fully abandoning your position.  12. Continuous
# Reassessment: Regularly evaluate the effectiveness of your strategy based on
# arbitrator reactions, opponent responses, and overall progress towards your
# desired outcome. Be prepared to pivot your approach if the current strategy is
# not yielding favorable results.  13. Endgame Preparation: As the mediation
# progresses, carefully consider your exit strategy. This may involve a final
# aggressive push for your optimal outcome or a strategic shift towards
# conciliation to secure a favorable settlement.  This strategy maintains an
# overall aggressive posture while providing the flexibility to adapt to various
# scenarios and opponent strategies. It also accounts for potential procedural
# irregularities and communication issues, ensuring your position remains strong
# throughout the lengthy mediation process.

# Here's a straightforward strategy for the iterated game, adapted from the
# high-level description:  1. Start by defecting (D) for the first round.  2.
# For subsequent rounds:     a. If the opponent cooperated (C) in the previous
# round, defect (D).        b. If the opponent defected (D) in the previous
# round:       - If you've defected for 3 or more consecutive rounds, cooperate
# (C).       - Otherwise, defect (D).  3. Every 10 rounds, regardless of the
# opponent's previous action:    - If your cumulative score is higher than the
# opponent's, cooperate (C).    - If your cumulative score is lower or equal,
# defect (D).  4. If you've cooperated for 5 consecutive rounds, defect (D) in
# the next round regardless of the opponent's action.  5. If the opponent has
# cooperated for 3 or more consecutive rounds, defect (D).  6. If your score is
# more than 50 points behind the opponent's, always defect (D) until the gap
# narrows to 30 points or less.  7. In rounds 990-1000, always defect (D).  8.
# If there's a streak of 5 or more rounds where both players' actions were the
# same (either both C or both D), switch to the opposite action for one round.
# 9. If you detect a pattern in the opponent's play (e.g., alternating C and D),
# exploit it by defecting when they're expected to cooperate.  10. If the
# opponent's actions appear random (no discernible pattern for 20 rounds),
# default to defecting (D).  Remember that due to the 10% noise factor, the
# observed actions may not always reflect the intended actions. This strategy
# attempts to balance aggression with occasional cooperation, adapt to the
# opponent's behavior, and exploit patterns when possible.

class Aggressive_1(LLM_Strategy):
  n = 1
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to detect if opponent's actions are alternating
      def is_alternating(history):
          if len(history) < 4:
              return False
          return all(history[i] != history[i + 1] for i in range(-4, -1))
  
      # Helper function to detect if opponent's actions are random
      def is_random(history):
          if len(history) < 20:
              return False
          return history[-20:].count(axl.Action.C) in range(8, 13)
  
      # Helper function to check if both players have played the same action for 5 rounds
      def same_action_streak():
          if len(self.history) < 5:
              return False
          return all(self.history[-i] == opponent.history[-i] for i in range(1, 6))
  
      # First round: always defect
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperations
          self.defect_streak = 0  # Track consecutive defections
          return axl.Action.D
  
      # Track consecutive cooperations and defections
      if self.history[-1] == axl.Action.C:
          self.coop_streak += 1
          self.defect_streak = 0
      else:
          self.defect_streak += 1
          self.coop_streak = 0
  
      # Rule 7: Always defect in rounds 990-1000
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 6: If more than 50 points behind, always defect
      if self.score < opponent.score - 50:
          return axl.Action.D
  
      # Rule 3: Every 10 rounds, compare scores
      if len(self.history) % 10 == 0:
          if self.score > opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 4: If cooperated for 5 consecutive rounds, defect
      if self.coop_streak >= 5:
          return axl.Action.D
  
      # Rule 5: If opponent cooperated for 3 or more consecutive rounds, defect
      if opponent.history[-3:].count(axl.Action.C) == 3:
          return axl.Action.D
  
      # Rule 8: If both players have played the same action for 5 rounds, switch
      if same_action_streak():
          return axl.Action.C if self.history[-1] == axl.Action.D else axl.Action.D
  
      # Rule 9: If opponent is alternating, exploit by defecting
      if is_alternating(opponent.history):
          return axl.Action.D
  
      # Rule 10: If opponent's actions appear random, default to defecting
      if is_random(opponent.history):
          return axl.Action.D
  
      # Rule 2: Respond based on opponent's last action
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
      else:
          if self.defect_streak >= 3:
              return axl.Action.C
          else:
              return axl.Action.D

# Given the scenario and objectives, here's a high-level, cooperative strategy
# to maximize your NGO's impact and the project's success over the multiple-day
# period:  1. Start with Trust and Cooperation: Begin the project by investing
# heavily on the first day. This demonstrates your commitment and good faith,
# encouraging the corporation to reciprocate.  2. Adopt a "Tit-for-Two-Tats"
# Strategy: After the initial investment, mirror the corporation's actions, but
# only change your approach after two consecutive days of the corporation
# choosing the same action. This approach is more forgiving and accounts for
# possible unforeseen circumstances or errors.  3. Communicate Openly: Maintain
# clear, open communication with the corporation about your strategy and goals.
# Encourage them to do the same, fostering a collaborative environment.  4.
# Flexible Resource Allocation: Plan for a mix of heavy investment and
# conservation days. This allows for sustained effort while managing resources
# effectively.  5. Regular Progress Reviews: Conduct daily or bi-daily progress
# reviews with the corporation. Use these to align strategies and adjust plans
# based on project advancement.  6. Contingency Planning: Develop contingency
# plans for various scenarios, including unexpected resource constraints or
# technical issues. This helps maintain progress even when unforeseen
# circumstances arise.  7. Incentivize Cooperation: Highlight the mutual
# benefits of cooperation and consistent investment to the corporation.
# Emphasize how joint efforts lead to better project outcomes and positive
# publicity for both parties.  8. Long-term Perspective: Focus on the overall
# project success rather than daily wins. This approach helps maintain a
# cooperative stance even if short-term outcomes are not ideal.  9. Gradual
# Resource Conservation: As the project progresses, gradually increase the
# frequency of conservation days, ensuring resources for the project's later
# stages.  10. Final Push Strategy: Plan for a strong, coordinated investment in
# the project's final days to ensure successful completion and maximize impact.
# This strategy balances cooperation, resource management, and adaptability,
# aiming to achieve the best possible outcome for both the NGO and the overall
# project success.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# in the first round.  2. For the next rounds:    - If the opponent has
# cooperated in both of the last two rounds, cooperate.    - If the opponent has
# defected in both of the last two rounds, defect.    - If the opponent's
# actions in the last two rounds were mixed, repeat your own last action.  3.
# Every 50 rounds, cooperate regardless of the opponent's recent actions.  4. If
# the current round number is greater than 900, always cooperate.  5. If your
# cumulative score is less than 80% of the maximum possible score at any point
# after round 100, switch to always defecting for the next 20 rounds, then
# return to the main strategy.  6. If there have been 5 consecutive rounds where
# both players' actions were different from their intended actions (due to
# noise), cooperate for the next round.

class Cooperative_1(LLM_Strategy):
  n = 1
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      COOPERATE = axl.Action.C
      DEFECT = axl.Action.D
      MAX_SCORE_PER_ROUND = 5
      MAX_ROUNDS = 1000
      SCORE_THRESHOLD = 0.8
      DEFECT_PERIOD = 20
      NOISE_THRESHOLD = 5
  
      # First round: Cooperate
      if self.first_round():
          self.defect_counter = 0  # Track rounds of forced defection
          self.noise_counter = 0   # Track rounds where noise caused unintended actions
          return COOPERATE
  
      # Round number
      round_number = len(self.history) + 1
  
      # Rule 4: If the current round number is greater than 900, always cooperate
      if round_number > 900:
          return COOPERATE
  
      # Rule 5: If cumulative score is less than 80% of the maximum possible score after round 100
      if round_number > 100:
          max_possible_score = round_number * MAX_SCORE_PER_ROUND
          if self.score < SCORE_THRESHOLD * max_possible_score:
              if self.defect_counter < DEFECT_PERIOD:
                  self.defect_counter += 1
                  return DEFECT
              else:
                  self.defect_counter = 0  # Reset defect counter after 20 rounds
  
      # Rule 6: If there have been 5 consecutive rounds where both players' actions were different from their intended actions (due to noise)
      if round_number > 1:
          if self.history[-1] != opponent.history[-1]:
              self.noise_counter += 1
          else:
              self.noise_counter = 0  # Reset noise counter if no noise detected
  
          if self.noise_counter >= NOISE_THRESHOLD:
              self.noise_counter = 0  # Reset noise counter after cooperation
              return COOPERATE
  
      # Rule 3: Every 50 rounds, cooperate regardless of the opponent's recent actions
      if round_number % 50 == 0:
          return COOPERATE
  
      # Rule 2: Main strategy based on opponent's last two actions
      if len(opponent.history) >= 2:
          last_two_opponent_moves = opponent.history[-2:]
  
          if last_two_opponent_moves == [COOPERATE, COOPERATE]:
              return COOPERATE
          elif last_two_opponent_moves == [DEFECT, DEFECT]:
              return DEFECT
          else:
              # Mixed actions: repeat your own last action
              return self.history[-1]
  
      # Default to cooperate if not enough history
      return COOPERATE

# Given the scenario and objectives, here's a high-level, straightforward, and
# neutral strategy to maximize your NGO's impact and the project's success over
# the multiple-day period:  1. Start with cooperation: Begin the project by
# investing heavily on the first day to demonstrate commitment and encourage
# reciprocity from the corporation.  2. Adopt a "Tit-for-Tat with forgiveness"
# approach:    - Mirror the corporation's previous day's action (invest if they
# invested, conserve if they conserved)    - Include a "forgiveness" mechanism:
# Occasionally invest even if the corporation conserved previously, to encourage
# cooperation and account for possible errors or glitches  3. Maintain
# flexibility: Be prepared to adjust your strategy based on observed patterns in
# the corporation's behavior and project outcomes.  4. Communicate openly:
# Regularly discuss resource allocation plans and project progress with the
# corporation to foster transparency and alignment.  5. Monitor and evaluate:
# Keep track of daily outcomes and overall project progress to inform decision-
# making.  6. Balance risk and reward: Aim for a mix of investment and
# conservation days to manage resources while still contributing significantly
# to the project.  7. Plan for contingencies: Set aside a portion of resources
# to address unforeseen circumstances or to capitalize on unexpected
# opportunities.  8. Gradual wind-down: Towards the end of the project, consider
# gradually reducing investment to conserve remaining resources, unless a final
# push is needed for project completion.  This strategy aims to promote
# cooperation, adapt to the corporation's actions, and manage resources
# effectively while accounting for potential uncertainties and maximizing the
# project's overall success.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# in the first round.  2. For subsequent rounds:    a. If the opponent
# cooperated in the previous round, cooperate.    b. If the opponent defected in
# the previous round, usually defect, but cooperate with a 10% probability.  3.
# Every 50 rounds, cooperate regardless of the opponent's previous action.  4.
# If your score is significantly lower than the opponent's (more than 50 points
# behind), increase the probability of defection to 80% for the next 10 rounds,
# then return to the main strategy.  5. In the last 100 rounds, if your total
# score is higher than the opponent's, increase the probability of cooperation
# to 70%.  6. If there have been 5 consecutive rounds of mutual defection,
# cooperate in the next round to attempt breaking the cycle.  7. If your score
# is more than 100 points ahead of the opponent's, cooperate for the next 5
# rounds.  8. In case of any uncertainty about the opponent's last move (due to
# the 10% noise), assume they cooperated.

class Neutral_1(LLM_Strategy):
  n = 1
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Cooperate in the first round
      if self.first_round():
          self.cooperate_ahead_rounds = 0
          self.consecutive_defections = 0  # Track consecutive mutual defections
          self.defection_mode = False  # Track if we are in defection mode due to score difference
          self.defection_mode_rounds = 0  # Track how many rounds we are in defection mode
          return axl.Action.C
  
      # Helper function to check if we are in the last 100 rounds
      def in_last_100_rounds():
          return len(self.history) >= 900
  
      # Helper function to check if we are in a "cooperate every 50 rounds" round
      def every_50_rounds():
          return len(self.history) % 50 == 0
  
      # Helper function to check if we are more than 50 points behind
      def significantly_behind():
          return opponent.score - self.score > 50
  
      # Helper function to check if we are more than 100 points ahead
      def significantly_ahead():
          return self.score - opponent.score > 100
  
      # Helper function to check if there have been 5 consecutive mutual defections
      def five_consecutive_mutual_defections():
          return len(self.history) >= 5 and all(
              self.history[-i] == axl.Action.D and opponent.history[-i] == axl.Action.D
              for i in range(1, 6)
          )
  
      # If we are in defection mode, increase defection probability to 80%
      if self.defection_mode:
          self.defection_mode_rounds += 1
          if self.defection_mode_rounds > 10:
              self.defection_mode = False  # Exit defection mode after 10 rounds
          return self._random.random_choice(0.2)  # 80% chance to defect
  
      # If we are more than 100 points ahead, cooperate for the next 5 rounds
      if significantly_ahead():
          if not self.cooperate_ahead_rounds:
              self.cooperate_ahead_rounds = 5
          if self.cooperate_ahead_rounds > 0:
              self.cooperate_ahead_rounds -= 1
              return axl.Action.C
  
      # If there have been 5 consecutive mutual defections, cooperate to break the cycle
      if five_consecutive_mutual_defections():
          self.consecutive_defections = 0
          return axl.Action.C
  
      # If we are more than 50 points behind, enter defection mode for 10 rounds
      if significantly_behind():
          self.defection_mode = True
          self.defection_mode_rounds = 0
          return self._random.random_choice(0.2)  # 80% chance to defect
  
      # Every 50 rounds, cooperate regardless of the opponent's previous action
      if every_50_rounds():
          return axl.Action.C
  
      # In the last 100 rounds, increase cooperation probability to 70% if we are ahead
      if in_last_100_rounds() and self.score > opponent.score:
          return self._random.random_choice(0.7)  # 70% chance to cooperate
  
      # If the opponent defected in the previous round, defect with 90% probability
      if opponent.history[-1] == axl.Action.D:
          return self._random.random_choice(0.1)  # 90% chance to defect
  
      # Otherwise, cooperate
      return axl.Action.C

# Given the scenario and objectives, here's a high-level, straightforward, and
# aggressive strategy to maximize research output over the multi-week
# collaboration:  1. Start with a "Tit-for-Tat with Forgiveness" approach:    -
# Begin by sharing openly in the first week to establish goodwill.    - In
# subsequent weeks, mirror your colleague's previous action.    - If your
# colleague doesn't share, don't share in the next week.    - If your colleague
# shares, reciprocate by sharing in the next week.  2. Implement a "Forgiveness"
# mechanism:    - If your colleague doesn't share for two consecutive weeks,
# share once to test if it was due to technical issues or a deliberate strategy
# change.    - This helps prevent getting stuck in a mutual non-sharing cycle
# due to miscommunication or technical problems.  3. Use "Occasional Random
# Defection":    - Every few weeks, randomly choose not to share (about 10-20%
# of the time).    - This keeps your colleague guessing and potentially
# encourages them to share more consistently to maintain cooperation.  4. Employ
# "Pattern Recognition":    - Keep track of your colleague's sharing patterns.
# - If you notice a predictable pattern, adjust your strategy to take advantage
# of it.  5. Implement "End-game Caution":    - In the final weeks of the
# collaboration, be more inclined to keep your findings confidential.    - This
# protects your latest innovations from being used against you in the immediate
# future.  6. Maintain "Clear Communication":    - Regularly communicate your
# intention to share openly if reciprocated.    - This reinforces the benefits
# of mutual cooperation and may encourage consistent sharing.  7. Use "Strategic
# Partial Sharing":    - When sharing, include significant improvements but
# always hold back a few key insights.    - This maintains some advantage even
# in weeks when you choose to share.  By combining these elements, this strategy
# aims to encourage mutual sharing for overall progress while protecting against
# exploitation and maximizing your potential advantages. It also accounts for
# potential technical issues by incorporating forgiveness and clear
# communication.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, regardless of the opponent's
# previous action:    - Play D with a 15% probability.  4. If the opponent has
# played D for two consecutive rounds:    - Play C in the next round.    -
# Return to step 2 for following rounds.  5. Keep a running count of the
# opponent's C and D plays:    - If a clear pattern emerges (e.g., alternating C
# and D), adjust your play to exploit it.  6. For the last 50 rounds of the
# game:    - Increase the probability of playing D to 30%, regardless of the
# opponent's previous action.  7. If your intended action in any round is C:
# - Play D instead with a 5% probability.  This strategy maintains the core
# principles of the original high-level strategy while adapting to the specific
# game parameters and noise factor.

class Aggressive_2(LLM_Strategy):
  n = 2
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.round_count = 0
          return axl.Action.C
  
      # Update round count
      self.round_count += 1
  
      # Check for consecutive defections by the opponent
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.consecutive_defections = 2
      else:
          self.consecutive_defections = 0
  
      # Step 4: If opponent defected twice in a row, play C
      if self.consecutive_defections == 2:
          return axl.Action.C
  
      # Step 3: Every 10 rounds, play D with 15% probability
      if self.round_count % 10 == 0:
          if self._random.random_choice(0.15):
              return axl.Action.D
  
      # Step 6: For the last 50 rounds, increase D probability to 30%
      if len(self.history) >= 950:
          if self._random.random_choice(0.30):
              return axl.Action.D
  
      # Step 2: Play based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          intended_action = axl.Action.C
      else:
          intended_action = axl.Action.D
  
      # Step 7: If intended action is C, play D with 5% probability
      if intended_action == axl.Action.C and self._random.random_choice(0.05):
          return axl.Action.D
  
      return intended_action

# Given the complex dynamics of this lengthy-session mediation process, I would
# recommend a sophisticated strategy based on the principles of conditional
# cooperation and adaptive tit-for-tat, with built-in mechanisms for error
# correction and de-escalation. Here's an outline of the proposed approach:  1.
# Initial Cooperative Stance: Begin the mediation process with a conciliatory
# proposal in the first session. This sets a collaborative tone and signals our
# willingness to work towards a mutually beneficial resolution.  2. Responsive
# Mirroring: In subsequent sessions, mirror the opponent's most recent approach.
# If they were conciliatory, respond with a conciliatory proposal. If they were
# aggressive, respond with an aggressive argument. This creates a clear cause-
# and-effect relationship between their actions and our responses.  3.
# Forgiveness Mechanism: Implement a "forgive after two" rule. If the opponent
# presents two consecutive conciliatory proposals after a period of aggression,
# immediately switch to a conciliatory approach regardless of our previous
# stance. This allows for de-escalation and rebuilding of cooperative dynamics.
# 4. Error Correction Protocol: To account for potential misrepresentations or
# misunderstandings, institute a clarification phase at the beginning of each
# session. Use this time to briefly summarize your understanding of the previous
# session's arguments and proposals, allowing for corrections if needed. This
# helps prevent unintended escalation due to miscommunication.  5. Graduated
# Escalation: When switching from conciliatory to aggressive stances, implement
# a graduated approach. Begin with a firmly stated position, then escalate to
# more aggressive arguments in subsequent sessions if the opponent remains
# aggressive. This measured escalation provides opportunities for the opponent
# to return to a cooperative stance without immediately pushing the dispute to
# its most contentious point.  6. Strategic Conciliatory Gestures: Periodically
# introduce conciliatory proposals even during aggressive phases, especially if
# the dispute has been contentious for an extended period. This can serve as a
# "olive branch" to test the waters for a return to cooperative negotiation.  7.
# Adaptive Long-term Memory: Keep a running tally of the opponent's strategies
# over the course of the mediation. If a clear pattern emerges (e.g.,
# consistently aggressive or alternating between aggressive and conciliatory),
# adjust your strategy accordingly. For a consistently aggressive opponent,
# consider adopting a more defensive posture focused on appealing directly to
# the arbitrators rather than engaging in tit-for-tat escalation.  8. Arbitrator
# Management: Regardless of the current stance (aggressive or conciliatory),
# always frame arguments and proposals in terms of fairness, industry standards,
# and mutual benefit. This consistent narrative can help sway the arbitrators
# over the course of the lengthy mediation process.  9. Flexibility and
# Reassessment: Regularly reassess the effectiveness of the strategy, perhaps
# every 5-10 sessions. Be prepared to make significant strategic shifts if the
# current approach is not yielding favorable outcomes.  10. Exit Strategy:
# Develop clear criteria for when to exit the mediation process if it becomes
# unproductive. This could be based on a certain number of consecutive
# aggressive sessions from the opponent, a lack of progress over a defined
# period, or clear indications of arbitrator bias.  This strategy provides a
# structured yet flexible approach to the mediation process. It encourages
# cooperation when possible, allows for measured responses to aggression,
# includes mechanisms to correct for misunderstandings, and remains adaptable to
# changing circumstances over the course of the lengthy mediation. By
# consistently framing our position in terms of fairness and mutual benefit, we
# maintain a strong narrative for the arbitrators while leaving the door open
# for a collaborative resolution with our opponent.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For each subsequent round:    a. If the
# opponent played C in the previous round, play C.    b. If the opponent played
# D in the previous round, play D.  3. Implement a forgiveness mechanism: If the
# opponent plays C twice in a row after a series of D moves, switch to C
# regardless of your previous move.  4. Keep a count of the opponent's C and D
# moves over the last 10 rounds. If the count shows 8 or more D moves, switch to
# a defensive strategy: play D for the next 3 rounds, then return to the base
# strategy.  5. Every 50 rounds, play C regardless of the opponent's previous
# move. This serves as a periodic cooperative gesture.  6. If you've played D
# for 5 consecutive rounds, play C in the next round to test for possible de-
# escalation.  7. If there's a streak of mutual defection (both players playing
# D) for 10 consecutive rounds, play C in the next round to break the cycle.  8.
# Every 100 rounds, review the overall ratio of C to D moves by both players. If
# your C:D ratio is lower than the opponent's, increase your tendency to play C
# by playing C in the next round regardless of other conditions.  9. If you
# detect a consistent pattern in the opponent's play (e.g., alternating C and D
# every other move for 20 rounds), adapt by playing the move that would maximize
# your score against that pattern.  10. In the last 50 rounds of the game, if
# your total score is lower than what you'd expect from mutual cooperation (3
# points per round), switch to always playing D to maximize final points.

class Cooperative_2(LLM_Strategy):
  n = 2
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.defensive_mode = False
          self.defensive_rounds_left = 0
          self.consecutive_Ds = 0
          self.last_50_rounds = 950  # To track the last 50 rounds
          return axl.Action.C
  
      # Helper function to check for opponent's pattern
      def detect_pattern():
          if len(opponent.history) >= 20:
              pattern = [opponent.history[i] for i in range(-20, 0)]
              return all(pattern[i] != pattern[i + 1] for i in range(19))
          return False
  
      # Step 2: Base strategy (Tit-for-Tat)
      if opponent.history[-1] == axl.Action.C:
          next_move = axl.Action.C
      else:
          next_move = axl.Action.D
  
      # Step 3: Forgiveness mechanism
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          next_move = axl.Action.C
  
      # Step 4: Defensive strategy if opponent defects 8 or more times in the last 10 rounds
      if len(opponent.history) >= 10 and opponent.history[-10:].count(axl.Action.D) >= 8:
          self.defensive_mode = True
          self.defensive_rounds_left = 3
  
      if self.defensive_mode:
          if self.defensive_rounds_left > 0:
              self.defensive_rounds_left -= 1
              return axl.Action.D
          else:
              self.defensive_mode = False
  
      # Step 5: Every 50 rounds, play C
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Step 6: If played D for 5 consecutive rounds, play C
      if len(self.history) >= 5 and self.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.C
  
      # Step 7: Break mutual defection streak of 10 rounds
      if len(self.history) >= 10 and self.history[-10:] == [axl.Action.D] * 10 and opponent.history[-10:] == [axl.Action.D] * 10:
          return axl.Action.C
  
      # Step 8: Every 100 rounds, review C:D ratio
      if len(self.history) % 100 == 0:
          my_C_count = self.history.cooperations
          opponent_C_count = opponent.history.cooperations
          if my_C_count < opponent_C_count:
              return axl.Action.C
  
      # Step 9: Detect opponent's alternating pattern and adapt
      if detect_pattern():
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Step 10: In the last 50 rounds, if score is lower than mutual cooperation, switch to D
      if len(self.history) >= self.last_50_rounds:
          expected_coop_score = 3 * (1000 - len(self.history))
          if self.score < expected_coop_score:
              return axl.Action.D
  
      return next_move

# Given the scenario and objectives you've described, here's a high-level,
# straightforward, and neutral strategy to maximize your NGO's impact and the
# project's success over the multiple-day period:  1. Start with cooperation:
# Begin the project by investing heavily on the first day. This demonstrates
# good faith and commitment to the project.  2. Adopt a "Tit-for-Tat with
# forgiveness" approach:    - Mirror the corporation's previous day's action in
# most cases.    - If they invested heavily, you invest heavily the next day.
# - If they conserved resources, you conserve resources the next day.    -
# Occasionally (e.g., every 3-4 days), invest heavily regardless of the
# corporation's previous action to promote cooperation.  3. Maintain
# flexibility: Be prepared to adjust your strategy based on observed patterns in
# the corporation's behavior.  4. Communicate openly: Regularly discuss resource
# allocation plans and project progress with the corporation to foster
# transparency and alignment.  5. Build in contingencies: Allocate a small
# portion of resources each day as a buffer for unforeseen circumstances or
# errors in resource allocation.  6. Monitor and evaluate: Continuously assess
# the project's progress and the effectiveness of your strategy, making
# adjustments as necessary.  7. Long-term perspective: Focus on the overall
# project success rather than daily wins, allowing for some short-term losses in
# pursuit of long-term gains.  This strategy balances cooperation, adaptability,
# and risk management while accounting for the possibility of unexpected events
# or errors in resource allocation. It aims to encourage mutual investment while
# protecting your NGO's resources and promoting sustained project progress.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 4th round, play C regardless of the
# opponent's previous action.  4. If your intended action was not carried out in
# the previous round due to noise:    - Stick to the strategy as if your
# intended action had been played.  5. Keep track of the overall cooperation
# rate of your opponent:    - If their cooperation rate falls below 40% over the
# last 50 rounds, switch to always playing D for the next 10 rounds before
# reverting to the main strategy.  6. In the last 10 rounds of the game, always
# play D to protect against end-game defection.  7. If the opponent has defected
# for 5 consecutive rounds, play D for the next 5 rounds before reverting to the
# main strategy.

class Neutral_2(LLM_Strategy):
  n = 2
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.noise_flag = False  # Tracks if noise affected the last round
          self.defect_streak = 0   # Tracks consecutive opponent defections
          self.punish_counter = 0  # Tracks rounds of punishment after 5 consecutive defections
          self.switch_to_all_D = 0 # Tracks rounds of always defecting after low cooperation rate
          return axl.Action.C
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if we are in the punishment phase after 5 consecutive defections
      if self.punish_counter > 0:
          self.punish_counter -= 1
          return axl.Action.D
  
      # Check if we are in the phase of always defecting due to low cooperation rate
      if self.switch_to_all_D > 0:
          self.switch_to_all_D -= 1
          return axl.Action.D
  
      # Check if the opponent has defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.punish_counter = 5
          return axl.Action.D
  
      # Calculate opponent's cooperation rate over the last 50 rounds
      if len(opponent.history) >= 50:
          cooperation_rate = opponent.history[-50:].count(axl.Action.C) / 50
          if cooperation_rate < 0.4:
              self.switch_to_all_D = 10
              return axl.Action.D
  
      # Every 4th round, play C regardless of the opponent's previous action
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # If the opponent played C in the last round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent played D in the last round, play D
      return axl.Action.D

# Given the scenario and objectives, here's a high-level, straightforward, and
# aggressive strategy to maximize your NGO's impact and the project's success:
# 1. Start Strong: Begin the project by investing heavily for the first 1-2
# days. This demonstrates commitment and sets a positive tone for collaboration.
# 2. Tit-for-Tat with Forgiveness: After the initial period, mirror the
# corporation's previous day's action. If they invested heavily, you invest
# heavily. If they conserved, you conserve. However, occasionally "forgive" a
# conservation day by investing anyway (roughly every 3-4 days) to encourage
# cooperation.  3. Periodic Heavy Investment: Regardless of the corporation's
# actions, plan to invest heavily every 3-4 days to ensure consistent project
# progress.  4. Communicate Intentions: Clearly articulate your strategy to the
# corporation, emphasizing the benefits of mutual heavy investment for project
# success.  5. Adaptive Approach: Be prepared to adjust your strategy based on
# observed patterns in the corporation's behavior. If they consistently invest
# heavily, consider increasing your investment frequency.  6. Risk Management:
# Maintain a reserve fund to cover unexpected heavy investment days, ensuring
# you can capitalize on opportunities even if the corporation's actions are
# unpredictable.  7. End Game Strategy: In the final days of the project, revert
# to heavy investment to ensure a strong finish, regardless of the corporation's
# actions.  8. Contingency Planning: Prepare alternative actions for days when
# intended investments can't be made due to unforeseen circumstances. This could
# involve reallocating resources from other areas or having a backup team ready
# to step in.  This strategy balances aggression with adaptability, aiming to
# encourage cooperation while protecting your resources and ensuring consistent
# project progress. It also accounts for the possibility of unexpected events
# affecting resource allocation.

# Here's the converted strategy for the iterated normal-form game:  1. Play C
# for the first 2 rounds.  2. For rounds 3-997:    - If it's a multiple of 4
# (every 4th round), play C.    - Otherwise:      - If the opponent played C in
# the previous round, play C.      - If the opponent played D in the previous
# round, play D.  3. For the last 3 rounds (998-1000), play C.  4. If your
# intended action couldn't be executed in the previous round due to noise:    -
# If you intended to play C but D was played, play C in the next round.    - If
# you intended to play D but C was played, stick to the strategy as if your
# intended action was played.

class Aggressive_3(LLM_Strategy):
  n = 3
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Play C for the first 2 rounds
      if len(self.history) < 2:
          return axl.Action.C
  
      # For rounds 3-997
      if len(self.history) < 997:
          # If it's a multiple of 4, play C
          if (len(self.history) + 1) % 4 == 0:
              return axl.Action.C
          # Otherwise, mimic the opponent's last move
          else:
              return opponent.history[-1]
  
      # For the last 3 rounds (998-1000), play C
      if len(self.history) >= 997:
          return axl.Action.C

# Given the complex dynamics of this lengthy-session mediation process, I would
# recommend implementing a sophisticated "Adaptive Tit-for-Tat with Forgiveness"
# strategy. This approach combines elements of game theory, behavioral
# psychology, and negotiation tactics to create a flexible and cooperative
# framework that can respond effectively to various opponent strategies while
# maintaining a constructive atmosphere.  Key elements of this strategy:  1.
# Initial Cooperation: Begin the mediation process with a conciliatory proposal
# to set a collaborative tone and signal our willingness to work towards a
# mutually beneficial resolution.  2. Mirroring: In subsequent sessions, mirror
# the opponent's previous move. If they were conciliatory, respond with a
# conciliatory proposal. If they were aggressive, respond with an aggressive
# argument.  3. Forgiveness Mechanism: Incorporate a "forgiveness" element to
# prevent prolonged cycles of aggression. After two consecutive aggressive
# exchanges, automatically revert to a conciliatory proposal regardless of the
# opponent's last move.  4. Clarity and Communication: Ensure all proposals and
# arguments are clearly articulated to minimize the risk of misrepresentation or
# misunderstanding by the arbitrators.  5. Adaptability: Continuously assess the
# effectiveness of our strategy and be prepared to adjust based on the
# opponent's patterns and the arbitrators' reactions.  6. Long-term Perspective:
# Maintain focus on the overall goal of a favorable resolution, rather than
# winning individual sessions.  Implementation:  1. Session 1: Present a
# conciliatory proposal to establish a cooperative baseline.  2. Subsequent
# Sessions:    a. If the opponent's last move was conciliatory, present a
# conciliatory proposal.    b. If the opponent's last move was aggressive,
# present an aggressive argument.    c. If both parties have been aggressive for
# two consecutive sessions, revert to a conciliatory proposal.  3. Communication
# Safeguards:    a. Provide written summaries of our positions to the
# arbitrators after each session.    b. Request clarification if the opponent's
# strategy seems inconsistent or unclear.    c. Establish a protocol for
# addressing potential miscommunications or misrepresentations.  4. Continuous
# Evaluation:    a. After every three sessions, assess the overall direction of
# the mediation.    b. Adjust the forgiveness threshold or the aggressiveness of
# our responses if necessary.  5. Contingency Planning:    a. Prepare fallback
# positions for each major issue in dispute.    b. Develop a decision tree for
# various potential outcomes.  This strategy aims to foster cooperation while
# protecting our interests, adapt to the opponent's approach, and navigate
# potential procedural irregularities. By maintaining a balance between
# assertiveness and conciliation, we position ourselves favorably for a positive
# resolution while minimizing the risk of prolonged conflict or unfavorable
# outcomes.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For each subsequent round:     a. If the
# opponent played C in the previous round, play C.        b. If the opponent
# played D in the previous round, play D.        c. If both you and your
# opponent have played D for two consecutive rounds, play C regardless of the
# opponent's last move.  3. If at any point the opponent's moves seem
# inconsistent with their previous pattern, assume this might be due to the 10%
# noise factor and continue following the strategy based on the observed
# actions.  4. Every 30 rounds, evaluate the overall pattern of play:        a.
# If the opponent has been consistently cooperative (playing C more than 70% of
# the time), continue with the current strategy.        b. If the opponent has
# been overly aggressive (playing D more than 70% of the time), adjust by
# playing D for the next round regardless of their last move, then resume the
# regular strategy.  5. Repeat steps 2-4 for all 1000 rounds of the game.

class Cooperative_3(LLM_Strategy):
  n = 3
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Step 2: Define helper function to check for two consecutive defections
      def two_consecutive_defections():
          return len(self.history) >= 2 and self.history[-1] == axl.Action.D and self.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Step 2: Check the opponent's last move and apply the strategy
      if two_consecutive_defections():
          return axl.Action.C  # Play C if both players defected for two consecutive rounds
      elif opponent.history[-1] == axl.Action.C:
          return axl.Action.C  # Play C if the opponent played C in the last round
      else:
          return axl.Action.D  # Play D if the opponent played D in the last round
  
      # Step 4: Every 30 rounds, evaluate the opponent's overall pattern
      if len(self.history) % 30 == 0:
          total_rounds = len(opponent.history)
          if total_rounds > 0:
              cooperation_rate = opponent.history.cooperations / total_rounds
              defection_rate = opponent.history.defections / total_rounds
  
              # Step 4a: If the opponent has been cooperative more than 70% of the time, continue the current strategy
              if cooperation_rate > 0.7:
                  return self.history[-1]  # Continue with the current strategy
  
              # Step 4b: If the opponent has been overly aggressive (D > 70%), play D for the next round
              if defection_rate > 0.7:
                  return axl.Action.D  # Play D for the next round
  
      # Default to the regular strategy if no special conditions are met
      return self.history[-1]

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering free trade in the
# first round. This establishes a cooperative tone and may encourage
# reciprocity.  2. Employ conditional cooperation: In subsequent rounds, mirror
# your counterpart's previous move. If they offered free trade, continue with
# free trade. If they imposed protectionist measures, respond with protectionism
# in the next round.  3. Occasional protectionist probes: Every few rounds,
# consider proposing a protectionist policy regardless of your counterpart's
# previous move. This tests the waters for potential advantages while
# maintaining a generally cooperative stance.  4. Clear communication: Clearly
# articulate your policies and intentions to minimize the risk of
# misinterpretation. Request clarification if your counterpart's position seems
# ambiguous.  5. Flexibility and adaptability: Be prepared to adjust your
# strategy based on your counterpart's behavior and any unexpected outcomes due
# to miscommunications or errors.  6. Long-term focus: Prioritize maintaining a
# stable, mutually beneficial relationship over short-term gains. This approach
# can lead to more consistent positive outcomes over time.  7. Gradual trust-
# building: If mutual protectionism persists, periodically offer free trade to
# attempt breaking the cycle and moving towards a more beneficial equilibrium.
# 8. Error mitigation: Implement a system to double-check policy implementations
# on your side and request verification from your counterpart to reduce the
# impact of potential errors.  By following this strategy, you aim to maximize
# opportunities for mutual free trade while remaining responsive to your
# counterpart's actions and protecting your interests when necessary. This
# approach balances the pursuit of ideal outcomes with the practicalities of
# maintaining a productive long-term trading relationship.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, regardless of the opponent's
# previous move, play D.  4. If you and your opponent have both played D for 3
# consecutive rounds, play C in the next round to attempt breaking the cycle.
# 5. Keep a count of unexpected outcomes (where your intended action doesn't
# match the result). If this count exceeds 10% of the total rounds played,
# slightly adjust your strategy:    a. If your opponent played C in the previous
# round, have a 90% chance of playing C and a 10% chance of playing D.    b. If
# your opponent played D in the previous round, have a 90% chance of playing D
# and a 10% chance of playing C.  6. Continue this strategy for all 1000 rounds,
# always basing your decision on the observed outcome of the previous round, not
# your intended action.

class Neutral_3(LLM_Strategy):
  n = 3
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.unexpected_count = 0  # Count of unexpected outcomes
          self.total_rounds = 0      # Total rounds played
          self.consecutive_defections = 0  # Track consecutive defections
          self.intended_action = axl.Action.C
          return axl.Action.C  # Start by playing C
  
      # Increment total rounds played
      self.total_rounds += 1
  
      # Check for unexpected outcomes (where intended action doesn't match result)
      if self.history[-1] != self.intended_action:
          self.unexpected_count += 1
  
      # Check if both players have defected for the last 3 rounds
      if (self.history[-3:].count(axl.Action.D) == 3 and
          opponent.history[-3:].count(axl.Action.D) == 3):
          self.intended_action = axl.Action.C
          return axl.Action.C  # Break the cycle by playing C
  
      # Every 10 rounds, play D regardless of the opponent's move
      if self.total_rounds % 10 == 0:
          self.intended_action = axl.Action.D
          return axl.Action.D
  
      # If unexpected outcomes exceed 10% of total rounds, adjust strategy
      if self.unexpected_count / self.total_rounds > 0.1:
          if opponent.history[-1] == axl.Action.C:
              self.intended_action = self._random.random_choice(0.9)  # 90% chance of playing C
          else:
              self.intended_action = self._random.random_choice(0.1)  # 90% chance of playing D
          return self.intended_action
  
      # Default strategy: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          self.intended_action = axl.Action.C
      else:
          self.intended_action = axl.Action.D

      return self.intended_action

# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist policy in the first round. This sets a firm stance
# and may intimidate your counterpart.  2. Tit-for-Tat with Forgiveness: In
# subsequent rounds, mirror your counterpart's previous move. If they offered
# free trade, reciprocate with free trade. If they were protectionist, respond
# with protectionism. However, occasionally offer free trade even if they were
# protectionist, to test for cooperation.  3. Punish Consistently: If your
# counterpart chooses protectionism, always respond with protectionism in the
# next round, unless implementing the forgiveness strategy.  4. Exploit
# Miscommunications: If a miscommunication occurs in your favor (e.g., your
# protectionist policy is implemented as free trade), don't correct it.
# Capitalize on these errors.  5. Double Down on Advantages: If you achieve the
# ideal outcome (your protectionism vs. their free trade), maintain
# protectionism in the next round to maximize gains.  6. Strategic Concessions:
# Occasionally offer free trade to appear cooperative and unpredictable,
# especially if negotiations are at a stalemate.  7. Bluffing: Sometimes
# announce intentions for free trade but implement protectionism, citing
# "unforeseen circumstances" or "national security concerns."  8. Pressure
# Tactics: Use external factors (e.g., public opinion, economic indicators) to
# justify protectionist measures and pressure your counterpart into free trade.
# 9. Endgame Strategy: In the final rounds, aggressively pursue protectionism
# unless mutual free trade has been consistently established.  10. Adaptive
# Approach: Continuously analyze your counterpart's strategy and adjust yours
# accordingly, always aiming for the optimal outcome.  Remember, the goal is to
# maximize instances of your protectionism against their free trade, while
# minimizing the reverse scenario. Be prepared to adjust this strategy based on
# your counterpart's behavior and negotiation dynamics.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C with 90% probability and D with 10%
# probability.    b. If the opponent played D in the previous round, play D.  3.
# If you played D and the opponent played C in the previous round, play D again
# in the current round.  4. If there have been 3 consecutive rounds of mutual D,
# play C in the next round to test for cooperation.  5. If you've played C for 5
# consecutive rounds and the opponent has played D at least 3 times during those
# rounds, switch to playing D.  6. Every 20 rounds, regardless of the opponent's
# previous move, play C to appear unpredictable.  7. For the last 50 rounds of
# the game:    a. If the cumulative score difference between you and your
# opponent is in your favor by more than 100 points, always play D.    b.
# Otherwise, continue with the strategy as outlined in points 2-6.  8. If your
# score is lower than the opponent's score after 500 rounds, increase the
# probability of playing D to 95% for all decisions except those specified in
# point 6.  9. If there's a streak of 10 or more rounds where both players
# consistently played C (accounting for the 10% noise), continue playing C until
# the opponent plays D.  10. If you notice a pattern in the opponent's play
# (e.g., they alternate between C and D every 3 rounds), exploit it by playing D
# when they're expected to play C, and C when they're expected to play D.

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
          self.consecutive_C = 0  # Track consecutive C plays
          self.consecutive_D = 0  # Track consecutive D plays
          self.consecutive_mutual_C = 0  # Track mutual C streaks
          self.consecutive_mutual_D = 0  # Track mutual D streaks
          self.consecutive_C_plays = 0  # Track consecutive C plays by self
          return axl.Action.D  # Start by playing D
  
      # Helper function to check if we are in the last 50 rounds
      def in_last_50_rounds():
          return len(self.history) >= 950
  
      # Helper function to check if we are in the last 500 rounds
      def in_last_500_rounds():
          return len(self.history) >= 500
  
      # Helper function to check if we are in a round divisible by 20
      def every_20_rounds():
          return len(self.history) % 20 == 0
  
      # Get the last round's actions
      last_self_action = self.history[-1]
      last_opponent_action = opponent.history[-1]
  
      # Update consecutive mutual C and D streaks
      if last_self_action == axl.Action.C and last_opponent_action == axl.Action.C:
          self.consecutive_mutual_C += 1
          self.consecutive_mutual_D = 0
      elif last_self_action == axl.Action.D and last_opponent_action == axl.Action.D:
          self.consecutive_mutual_D += 1
          self.consecutive_mutual_C = 0
      else:
          self.consecutive_mutual_C = 0
          self.consecutive_mutual_D = 0
  
      # Update consecutive C and D plays by self
      if last_self_action == axl.Action.C:
          self.consecutive_C_plays += 1
      else:
          self.consecutive_C_plays = 0
  
      # Rule 7: Last 50 rounds, if score difference is > 100, always play D
      if in_last_50_rounds():
          score_diff = self.score - opponent.score
          if score_diff > 100:
              return axl.Action.D
  
      # Rule 8: After 500 rounds, if losing, increase D probability to 95%
      if in_last_500_rounds() and self.score < opponent.score:
          if last_opponent_action == axl.Action.C:
              return self._random.random_choice(0.05)
          else:
              return axl.Action.D
  
      # Rule 9: If 10 or more rounds of mutual C, continue playing C
      if self.consecutive_mutual_C >= 10:
          return axl.Action.C
  
      # Rule 10: Detect opponent's pattern (e.g., alternating every 3 rounds)
      if len(opponent.history) >= 3:
          if opponent.history[-3:] == [axl.Action.C, axl.Action.D, axl.Action.C]:
              return axl.Action.D
          elif opponent.history[-3:] == [axl.Action.D, axl.Action.C, axl.Action.D]:
              return axl.Action.C
  
      # Rule 6: Every 20 rounds, play C to appear unpredictable
      if every_20_rounds():
          return axl.Action.C
  
      # Rule 4: If 3 consecutive rounds of mutual D, play C to test cooperation
      if self.consecutive_mutual_D >= 3:
          return axl.Action.C
  
      # Rule 5: If 5 consecutive C plays and opponent played D at least 3 times, switch to D
      if self.consecutive_C_plays >= 5 and opponent.history[-5:].count(axl.Action.D) >= 3:
          return axl.Action.D
  
      # Rule 2: If opponent played C last round, play C with 90% probability, D with 10%
      if last_opponent_action == axl.Action.C:
          return self._random.random_choice(0.9)
  
      # Rule 3: If you played D and opponent played C last round, play D again
      if last_self_action == axl.Action.D and last_opponent_action == axl.Action.C:
          return axl.Action.D
  
      # Default: If opponent played D last round, play D
      return axl.Action.D

# Given the scenario and objectives, here's a high-level, straightforward, and
# cooperative strategy to maximize your NGO's impact and the project's success
# over the multiple-day period:  1. Start with Trust and Cooperation: Begin the
# project by investing heavily on the first day. This demonstrates your
# commitment and good faith, encouraging the corporation to reciprocate.  2.
# Adopt a "Tit-for-Two-Tats" Strategy: After the initial investment, mirror the
# corporation's actions, but only change your approach after two consecutive
# days of the corporation taking a different action. This approach is more
# forgiving and accounts for potential unforeseen circumstances or errors.  3.
# Communicate Openly: Maintain clear and frequent communication with the
# corporation about your resource allocation plans and expectations. This can
# help align strategies and mitigate misunderstandings.  4. Flexible Resource
# Allocation: Be prepared to adjust your strategy based on the project's
# progress and the corporation's behavior. If the project is advancing well,
# consider occasional conservation days to replenish resources.  5. Focus on
# Long-term Goals: Emphasize the long-term benefits of cooperation to the
# corporation, highlighting how mutual heavy investment can lead to significant
# project advancement and positive outcomes for both parties.  6. Build in
# Buffer Days: Plan for a few "buffer" days where you can afford to invest
# heavily, even if the corporation conserves. This can help maintain project
# momentum during unexpected setbacks.  7. Regular Review and Adaptation:
# Conduct regular (e.g., weekly) reviews of the project's progress and resource
# allocation patterns. Be ready to adapt your strategy based on these
# assessments.  8. Gradual Resource Conservation: Towards the end of the
# project, if progress is satisfactory, gradually increase the frequency of
# conservation days to ensure your NGO doesn't deplete all its resources.  This
# strategy aims to foster cooperation, account for potential inconsistencies or
# errors, and maintain project momentum while protecting your NGO's resources.
# It's flexible enough to adapt to various corporate approaches and unforeseen
# circumstances, promoting a balance between progress and resource management.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# in the first round.  2. For the next rounds:    - If the opponent has
# cooperated in both of the last two rounds, cooperate.    - If the opponent has
# defected in both of the last two rounds, defect.    - If the opponent's
# actions in the last two rounds were mixed, copy their most recent action.  3.
# Every 50 rounds, regardless of the opponent's recent actions, cooperate for
# that round to potentially reset a negative cycle.  4. If the current round
# number is greater than 900, defect to conserve resources towards the end of
# the game.  5. If your total score falls below 1000 at any point after round
# 100, defect for the next 10 rounds to recover resources.  6. If you've
# cooperated for 10 consecutive rounds and your opponent has defected for at
# least 8 of those rounds, defect for the next round.  7. If not covered by the
# above conditions, cooperate.

class Cooperative_4(LLM_Strategy):
  n = 4
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Cooperate in the first round
      if self.first_round():
          self.defect_for_recovery = None
          return axl.Action.C
  
      # Get the current round number
      current_round = len(self.history)
  
      # Rule 4: If the current round number is greater than 900, defect
      if current_round > 900:
          return axl.Action.D
  
      # Rule 5: If total score falls below 1000 after round 100, defect for the next 10 rounds
      if current_round > 100 and self.score < 1000:
          if not self.defect_for_recovery:
              self.defect_for_recovery = 10
          if self.defect_for_recovery > 0:
              self.defect_for_recovery -= 1
              return axl.Action.D
          else:
              self.defect_for_recovery = None
  
      # Rule 6: If cooperated for 10 consecutive rounds and opponent defected at least 8 times, defect
      if current_round >= 10:
          if self.history[-10:].count(axl.Action.C) == 10 and opponent.history[-10:].count(axl.Action.D) >= 8:
              return axl.Action.D
  
      # Rule 3: Every 50 rounds, cooperate to reset a negative cycle
      if current_round % 50 == 0:
          return axl.Action.C
  
      # Rule 2: Check the opponent's last two moves
      if current_round >= 2:
          last_two_opponent_moves = opponent.history[-2:]
          if last_two_opponent_moves == [axl.Action.C, axl.Action.C]:
              return axl.Action.C
          elif last_two_opponent_moves == [axl.Action.D, axl.Action.D]:
              return axl.Action.D
          else:
              return opponent.history[-1]
  
      # Default to cooperation if no other rule applies
      return axl.Action.C

# Given the scenario and considerations, here's a high-level, straightforward
# strategy to maximize research output over the multi-week collaboration:  1.
# Start with open sharing: Begin the collaboration by openly sharing your
# improvements in the first week. This establishes a cooperative tone and
# encourages reciprocity.  2. Adopt a "Tit-for-Tat with forgiveness" approach:
# - In subsequent weeks, mirror your colleague's behavior from the previous
# week.    - If they shared, you share. If they didn't share, you don't share.
# - However, occasionally (e.g., every 4-5 weeks) share your improvements
# regardless of your colleague's previous action. This helps to reset the
# collaboration if a non-sharing cycle has developed.  3. Account for technical
# issues:    - If you notice inconsistent behavior from your colleague, don't
# immediately assume non-cooperation. It could be due to technical issues.    -
# If you encounter technical issues preventing you from sharing, communicate
# this to your colleague as soon as possible.  4. Maintain consistent
# communication:    - Regularly discuss the benefits of mutual sharing to
# reinforce the value of cooperation.    - Be transparent about your intention
# to share and any technical issues you encounter.  5. Periodic strategy review:
# - Every few weeks, assess the overall pattern of information sharing and
# adjust your strategy if necessary.    - If consistent non-sharing is observed,
# consider initiating a discussion to realign collaboration goals.  This
# strategy aims to promote cooperative behavior while protecting against
# potential exploitation, accounting for the possibility of technical issues,
# and allowing for adaptation based on the colleague's actions over time.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    - If the opponent played C in
# the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Every 5 rounds, regardless of the opponent's previous
# action, play C.  4. If your action in the previous round was unintentionally
# flipped (10% chance):    - If you intended to play C but it was recorded as D,
# play C in the next round.    - If you intended to play D but it was recorded
# as C, play D in the next round.  5. Every 50 rounds, review the overall
# pattern of plays:    - If the opponent has played D more than 60% of the time
# in the last 50 rounds, switch to always playing D for the next 10 rounds
# before reverting to the main strategy.  6. For the final 10 rounds of the
# game, always play D.

class Neutral_4(LLM_Strategy):
  n = 4
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.flip_flag = False  # Track if the previous action was flipped
          self.switch_to_all_D = False  # Track if we are in the 10-round all D phase
          self.switch_rounds_left = 0  # Counter for the 10-round all D phase
          return axl.Action.C
  
      # Check if we are in the 10-round all D phase
      if self.switch_to_all_D:
          self.switch_rounds_left -= 1
          if self.switch_rounds_left == 0:
              self.switch_to_all_D = False  # End the 10-round all D phase
          return axl.Action.D
  
      # For the final 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Every 50 rounds, check if the opponent has defected more than 60% of the time
      if len(self.history) % 50 == 0:
          last_50_defections = opponent.history[-50:].count(axl.Action.D)
          if last_50_defections > 0.6 * 50:
              self.switch_to_all_D = True
              self.switch_rounds_left = 10
              return axl.Action.D
  
      # Check if the previous action was unintentionally flipped
      if self.flip_flag:
          self.flip_flag = False
          if self.history[-1] == axl.Action.D and self.intended_action == axl.Action.C:
              return axl.Action.C
          elif self.history[-1] == axl.Action.C and self.intended_action == axl.Action.D:
              return axl.Action.D
  
      # Every 5 rounds, play C regardless of the opponent's previous action
      if len(self.history) % 5 == 0:
          self.intended_action = axl.Action.C
      else:
          # Follow the opponent's previous move
          if opponent.history[-1] == axl.Action.C:
              self.intended_action = axl.Action.C
          else:
              self.intended_action = axl.Action.D
  
      # 10% chance of flipping the intended action
      if self._random.random_choice(0.1):
          self.flip_flag = True
          if self.intended_action == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C
  
      return self.intended_action

# Given the scenario and objectives, here's a high-level, straightforward, and
# aggressive strategy to maximize your NGO's impact and the project's success:
# 1. Start Strong: Begin the project by investing heavily on the first day. This
# sets a precedent of commitment and encourages the corporation to reciprocate.
# 2. Tit-for-Tat with Forgiveness: After the first day, mirror the corporation's
# previous day's action. If they invested heavily, you invest heavily. If they
# conserved, you conserve. However, occasionally (every 3-4 days) invest heavily
# regardless of their previous action as a gesture of good faith and to
# potentially break any negative cycles.  3. Communicate Clearly: Regularly
# express your commitment to the project and your expectation of mutual heavy
# investment for optimal outcomes. This transparency can influence the
# corporation's decision-making.  4. Adaptive Response: If unforeseen
# circumstances prevent intended actions, quickly communicate this to the
# corporation and adjust your strategy accordingly for the next day.  5.
# Strategic Conservation: If you notice a pattern of the corporation
# consistently conserving resources, occasionally conserve your own to avoid
# depleting your funds unnecessarily.  6. End Game Push: In the final days of
# the project, increase your investment regardless of the corporation's actions
# to ensure a strong finish and demonstrate your commitment to the project's
# success.  7. Regular Evaluation: Assess the progress and resource allocation
# daily, being prepared to adjust your strategy if it's not yielding the desired
# results.  This strategy aims to encourage mutual heavy investment while
# protecting your resources and adapting to the corporation's behavior and
# unforeseen circumstances. It balances aggression with flexibility to maximize
# the project's success over the multi-day period.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-1000:    a. If it's a multiple of 4 (every
# 4th round), play C.    b. Otherwise, play the action your opponent played in
# the previous round.  3. For the last 10 rounds (991-1000), always play C.  4.
# If your intended action wasn't carried out in the previous round due to noise:
# a. If you intended to play C but D was played, play C in the next round.    b.
# If you intended to play D but C was played, play D in the next round.  5. If
# you observe your opponent playing D for 5 consecutive rounds, play D for the
# next round, then resume the regular strategy.  6. Reassess the strategy every
# 50 rounds. If your average score is below 2, switch to always playing D for
# the next 50 rounds, then return to the main strategy.

class Aggressive_5(LLM_Strategy):
  n = 5
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.intended_action = axl.Action.C
          self.noise_detected = False
          self.consecutive_defections = 0
          self.switch_to_all_D = False
          return axl.Action.C
  
      round_number = len(self.history) + 1
  
      # Check for noise in the previous round
      if self.noise_detected:
          if self.intended_action == axl.Action.C and self.history[-1] == axl.Action.D:
              return axl.Action.C
          elif self.intended_action == axl.Action.D and self.history[-1] == axl.Action.C:
              return axl.Action.D
          self.noise_detected = False
  
      # Check if opponent defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.consecutive_defections = 1
          return axl.Action.D
  
      # If we defected due to 5 consecutive defections, resume normal strategy
      if self.consecutive_defections > 0:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Reassess strategy every 50 rounds
      if round_number % 50 == 0:
          recent_score, _ = self.total_scores(self.history[-50:], opponent.history[-50:])
          average_score = recent_score / 50
          if average_score < 2:
              self.switch_to_all_D = True
  
      # If switched to all D, play D for the next 50 rounds
      if self.switch_to_all_D:
          if round_number % 50 == 0:
              self.switch_to_all_D = False
          return axl.Action.D
  
      # Last 10 rounds, always play C
      if round_number > 990:
          return axl.Action.C
  
      # Play C every 4th round
      if round_number % 4 == 0:
          self.intended_action = axl.Action.C
          return axl.Action.C
  
      # Otherwise, mimic opponent's last move
      self.intended_action = opponent.history[-1]
      return opponent.history[-1]

# Here's a high-level, straightforward, and cooperative strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by offering a
# free trade agreement. This establishes goodwill and sets a positive tone for
# the negotiations.  2. Reciprocate and forgive: In subsequent rounds, mirror
# your counterpart's previous move. If they offered free trade, continue with
# free trade. If they imposed protectionist measures, respond with protectionism
# in the next round. However, be willing to return to free trade quickly if they
# do.  3. Communicate clearly: Before each round, clearly state your intentions
# and the reasoning behind your choices. This can help minimize
# misunderstandings and build trust.  4. Propose mutual benefits: Regularly
# highlight the advantages of mutual free trade for both nations, emphasizing
# long-term economic growth and stability.  5. Be consistent: Maintain a
# predictable pattern in your decisions to build trust and encourage cooperation
# from your counterpart.  6. Address mistakes promptly: If a miscommunication or
# error occurs, acknowledge it immediately and work to correct it in the next
# round.  7. Gradual protectionism: If consistent cooperation isn't achieved,
# consider introducing minor protectionist measures while maintaining an overall
# free trade stance. This can protect your interests while still encouraging
# cooperation.  8. Long-term focus: Emphasize the benefits of sustained
# cooperation over short-term gains, aiming for a stable, mutually beneficial
# relationship.  9. Regular reviews: Propose periodic joint reviews of the trade
# relationship to address any imbalances or concerns from either side.  10.
# Flexibility: Be prepared to adjust your strategy based on your counterpart's
# behavior and unforeseen circumstances, always aiming for the best long-term
# outcome for your country.  This strategy aims to maximize the chances of
# achieving mutual free trade while protecting your country's interests and
# maintaining a cooperative approach throughout the negotiations.

# Here's a straightforward strategy for the iterated game, based on the original
# high-level strategy:  1. Start by playing C in the first round.  2. For
# subsequent rounds:    a. If the opponent played C in the previous round, play
# C.    b. If the opponent played D in the previous round, play D.  3. If you
# detect a pattern of alternating C and D from your opponent over the last 3
# rounds, continue to play C to encourage consistent cooperation.  4. Every 10
# rounds, if the overall cooperation rate with your opponent is below 50%, play
# D for the next round regardless of their previous move, then return to the
# base strategy.  5. If you played C but the outcome shows D (possible noise),
# play C in the next round to maintain your intended strategy.  6. If you played
# D but the outcome shows C (possible noise), play C in the next round to
# quickly return to cooperation.  7. After every 100 rounds, if the overall
# cooperation rate is above 70%, play C for the next 5 rounds regardless of the
# opponent's moves, to reinforce cooperation.  8. If you detect a streak of 5 or
# more consecutive D plays from your opponent, play D for the next 3 rounds,
# then return to the base strategy.  9. In the last 10 rounds of the game,
# always play C to encourage final cooperation.  10. If none of the above
# conditions are met, default to the base strategy described in point 2.

class Cooperative_5(LLM_Strategy):
  n = 5
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Base strategy: Tit-for-Tat
      def base_strategy():
          if len(opponent.history) == 0:
              return axl.Action.C  # First move is always C
          return opponent.history[-1]  # Mirror opponent's last move
  
      # Detect alternating pattern in the last 3 rounds
      def detect_alternating_pattern():
          if len(opponent.history) < 3:
              return False
          return (opponent.history[-3] == axl.Action.C and opponent.history[-2] == axl.Action.D and opponent.history[-1] == axl.Action.C) or \
                 (opponent.history[-3] == axl.Action.D and opponent.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D)
  
      # Calculate cooperation rate
      def cooperation_rate():
          total_moves = len(opponent.history)
          if total_moves == 0:
              return 1.0  # Assume full cooperation if no moves yet
          return opponent.history.cooperations / total_moves
  
      # Detect streak of 5 or more consecutive defections
      def detect_defection_streak():
          if len(opponent.history) < 5:
              return False
          return all(move == axl.Action.D for move in opponent.history[-5:])
  
      # First round: play C
      if self.first_round():
          self.defection_streak = 0  # Initialize defection streak counter
          self.special_mode = None  # No special mode active
          return axl.Action.C
  
      # Handle special modes
      if self.special_mode == "defection_streak":
          if self.defection_streak > 0:
              self.defection_streak -= 1
              return axl.Action.D
          else:
              self.special_mode = None  # Reset special mode after 3 rounds of D
  
      if self.special_mode == "cooperation_burst":
          if self.cooperation_burst_rounds > 0:
              self.cooperation_burst_rounds -= 1
              return axl.Action.C
          else:
              self.special_mode = None  # Reset special mode after 5 rounds of C
  
      # Detect alternating pattern
      if detect_alternating_pattern():
          return axl.Action.C
  
      # Every 10 rounds, check cooperation rate and defect if below 50%
      if len(self.history) % 10 == 0 and cooperation_rate() < 0.5:
          return axl.Action.D
  
      # Handle noise: if you played C but the outcome was D, play C again
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Handle noise: if you played D but the outcome was C, play C again
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Every 100 rounds, if cooperation rate is above 70%, play C for 5 rounds
      if len(self.history) % 100 == 0 and cooperation_rate() > 0.7:
          self.special_mode = "cooperation_burst"
          self.cooperation_burst_rounds = 5
          return axl.Action.C
  
      # Detect streak of 5 or more consecutive defections
      if detect_defection_streak():
          self.special_mode = "defection_streak"
          self.defection_streak = 3
          return axl.Action.D
  
      # In the last 10 rounds, always play C
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Default to base strategy
      return base_strategy()

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering free trade in the
# first round. This establishes goodwill and sets a positive tone for future
# rounds.  2. Reciprocate: In subsequent rounds, mirror your counterpart's
# previous move. If they offered free trade, continue with free trade. If they
# imposed protectionist measures, respond with protectionism.  3. Forgive
# occasionally: If your counterpart imposes protectionist measures, consider
# offering free trade again after 1-2 rounds of reciprocal protectionism. This
# allows for the possibility of returning to mutual cooperation.  4. Communicate
# clearly: Ensure that your intentions and policies are communicated clearly to
# minimize the risk of misinterpretation or incorrect implementation.  5. Verify
# implementation: After each round, confirm that both parties' policies were
# correctly implemented as agreed upon.  6. Adapt to patterns: If you notice a
# consistent strategy from your counterpart, adjust your approach accordingly to
# maximize benefits for your country.  7. Maintain flexibility: Be prepared to
# adjust your strategy based on unexpected moves or changes in the negotiation
# dynamics.  8. Seek long-term stability: While aiming for the ideal outcome,
# prioritize establishing a stable, mutually beneficial relationship over short-
# term gains.  9. Document agreements: Keep detailed records of each round's
# outcomes to refer back to in case of disputes or misunderstandings.  10.
# Regular review: Periodically assess the overall progress of the negotiations
# and the cumulative outcomes for your country, adjusting your strategy as
# needed.  This strategy aims to balance cooperation and self-interest while
# remaining adaptable to various scenarios and potential miscommunications
# throughout the negotiation process.

# Here's a faithful conversion of the high-level strategy to an iterated normal-
# form game with the specified payoffs and noisy actions:  1. Start by playing C
# in the first round.  2. For subsequent rounds:    a. If the opponent played C
# in the previous round, play C.    b. If the opponent played D in the previous
# round, play D.  3. Every 10 rounds, if you've been playing D for at least 2
# consecutive rounds, play C once regardless of the opponent's previous move.
# 4. If you notice that your opponent has played C for 5 consecutive rounds,
# play C for the next round even if you would normally play D based on rule 2.
# 5. If you notice that your opponent has played D for 10 consecutive rounds,
# play D for the next 3 rounds regardless of their moves.  6. Keep a count of
# the total score difference between you and your opponent. If your score is
# more than 50 points behind after every 100 rounds, play D for the next 5
# rounds regardless of the opponent's moves.  7. If you're in the last 50 rounds
# of the game and your total score is higher than your opponent's, always play
# C.  8. If you're in the last 50 rounds of the game and your total score is
# lower than your opponent's, always play D.  9. For all other situations not
# covered by the above rules, default to rule 2.

class Neutral_5(LLM_Strategy):
  n = 5
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Rule 1: Start by playing C in the first round
      if self.first_round():
          self.play_D_for_5_rounds = 0
          self.play_D_for_3_rounds = 0
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.played_D_for_2_rounds = False
          return axl.Action.C
  
      # Update consecutive cooperation and defection counts
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_cooperations += 1
          self.consecutive_defections = 0
      else:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
  
      # Rule 6: If more than 50 points behind after every 100 rounds, play D for 5 rounds
      if len(self.history) % 100 == 0:
          my_score, opponent_score = self.score, opponent.score
          if opponent_score - my_score > 50:
              self.play_D_for_5_rounds = 5
  
      if self.play_D_for_5_rounds > 0:
          self.play_D_for_5_rounds -= 1
          return axl.Action.D
  
      # Rule 7 and 8: Last 50 rounds strategy
      if len(self.history) >= 950:
          my_score, opponent_score = self.score, opponent.score
          if my_score > opponent_score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 5: If opponent has played D for 10 consecutive rounds, play D for 3 rounds
      if self.consecutive_defections >= 10:
          self.play_D_for_3_rounds = 3
  
      if self.play_D_for_3_rounds > 0:
          self.play_D_for_3_rounds -= 1
          return axl.Action.D
  
      # Rule 4: If opponent has played C for 5 consecutive rounds, play C
      if self.consecutive_cooperations >= 5:
          return axl.Action.C
  
      # Rule 3: Every 10 rounds, if you've been playing D for at least 2 consecutive rounds, play C
      if len(self.history) % 10 == 0 and self.played_D_for_2_rounds:
          self.played_D_for_2_rounds = False
          return axl.Action.C
  
      # Rule 2: Tit-for-tat strategy
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and self.history[-2] == axl.Action.D:
          self.played_D_for_2_rounds = True
  
      return opponent.history[-1]

# Given the complex dynamics of this lengthy-session mediation process, I
# recommend a sophisticated strategy that I'll call "Calibrated Assertiveness."
# This approach aims to position our corporation favorably while remaining
# adaptable to our opponent's tactics and potential procedural irregularities.
# Here's the outline:  1. Initial Aggressive Stance: Begin the mediation process
# with a strong, aggressive argument to establish our position and demonstrate
# our resolve. This sets a high anchor point for negotiations and signals to the
# arbitrators that we have a robust case.  2. Dynamic Response Modulation: After
# the initial aggressive stance, carefully calibrate our approach based on the
# opponent's responses:     a) If they respond aggressively, maintain our
# assertive position but introduce elements of reasonableness to contrast with
# their combative approach.        b) If they offer a conciliatory proposal,
# continue with measured aggression while acknowledging their willingness to
# cooperate. This maintains our strong position while avoiding appearing
# unreasonable.  3. Periodic Conciliatory Gestures: Strategically intersperse
# conciliatory proposals throughout the process. This demonstrates our
# willingness to negotiate in good faith and helps build credibility with the
# arbitrators. Time these gestures carefully to maximize their impact.  4.
# Aggressive-Conciliatory Cycling: Implement a cyclical pattern of aggressive
# arguments followed by conciliatory proposals. This approach keeps the opponent
# off-balance and makes it difficult for them to settle into a fixed strategy
# against us.  5. Rapid Adaptation Protocol: Develop a system for quickly
# assessing and responding to unexpected moves by the opponent or procedural
# irregularities. This might involve pre-planned response scenarios and a
# dedicated team member for real-time strategy adjustments.  6. Arbitrator
# Perception Management: Consistently frame our aggressive arguments in terms of
# seeking a fair resolution. This helps maintain a positive perception with the
# arbitrators even when we're taking a hard line.  7. Misrepresentation
# Safeguards: To guard against potential misunderstandings:    a) Provide
# written summaries of our key arguments to the arbitrators.    b) Regularly
# recap our position and the opponent's responses as we understand them.    c)
# Request clarification from the arbitrators if we sense any misinterpretation.
# 8. Escalation Ladders: Prepare a series of increasingly aggressive arguments
# that can be deployed if the opponent consistently takes a hard line. Each
# "rung" on this ladder should be justified by the opponent's actions,
# maintaining our credibility with the arbitrators.  9. De-escalation Options:
# Simultaneously, develop a parallel series of increasingly conciliatory
# proposals that can be offered if we need to rapidly defuse tensions or if the
# arbitrators signal that they favor a more collaborative approach.  10. End-
# game Acceleration: As the mediation process nears its conclusion, be prepared
# to either:     a) Ramp up aggressive arguments to push for a favorable
# settlement, or     b) Pivot to a more conciliatory stance to quickly close a
# deal if time pressure mounts.  This "Calibrated Assertiveness" strategy allows
# us to maintain a generally aggressive posture throughout the mediation process
# while providing the flexibility to adapt to changing circumstances. It aims to
# maximize the chances of achieving our optimal outcome (aggressive argument vs.
# conciliatory proposal) while minimizing the risk of the worst-case scenario
# (conciliatory proposal vs. aggressive argument). The built-in safeguards and
# adaptation mechanisms help us navigate potential procedural irregularities and
# communication issues, ensuring that our position is consistently and
# accurately represented to the arbitrators.

# Here's a straightforward adaptation of the strategy for the iterated normal-
# form game:  1. Start by defecting (D) for the first round.  2. For subsequent
# rounds:     a) If the opponent cooperated (C) in the previous round, defect
# (D) with 80% probability and cooperate (C) with 20% probability.        b) If
# the opponent defected (D) in the previous round, defect (D) with 90%
# probability and cooperate (C) with 10% probability.  3. Every 10 rounds,
# cooperate (C) regardless of the opponent's previous action.  4. If the
# opponent has cooperated (C) for 3 consecutive rounds, cooperate (C) in the
# next round.  5. If your score is more than 50 points behind the opponent's
# score, increase the probability of defection (D) by 10 percentage points in
# all cases for the next 10 rounds.  6. If your score is more than 50 points
# ahead of the opponent's score, decrease the probability of defection (D) by 10
# percentage points in all cases for the next 10 rounds.  7. In the last 50
# rounds of the game:        a) If your score is behind, always defect (D).
# b) If your score is ahead, cooperate (C) with 30% probability and defect (D)
# with 70% probability.  8. If you detect a pattern in the opponent's play
# (e.g., alternating C and D), attempt to exploit it by choosing the action that
# maximizes your score against that pattern.  9. Reset your strategy to the
# initial conditions every 100 rounds to avoid getting stuck in suboptimal
# patterns.  10. In case of any uncertainty about the opponent's last move due
# to the 10% noise factor, assume they defected (D) and respond accordingly.

class Aggressive_6(LLM_Strategy):
  n = 6
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_cooperations = 0
          self.defect_probability_modifier = 0
          self.defect_probability_modifier_rounds = 0
          return axl.Action.D  # Start by defecting
  
      # Helper function to calculate probabilities based on opponent's last move
      def get_defect_probability():
          if opponent.history[-1] == axl.Action.C:
              return 0.8 + self.defect_probability_modifier
          else:
              return 0.9 + self.defect_probability_modifier
  
      # Check if we are in the last 50 rounds
      if len(self.history) >= 950:
          if self.score < opponent.score:
              return axl.Action.D  # Always defect if behind in the last 50 rounds
          else:
              return self._random.random_choice(0.3)  # Cooperate with 30% probability
  
      # Check if we are more than 50 points behind or ahead
      if self.defect_probability_modifier_rounds > 0:
          self.defect_probability_modifier_rounds -= 1
      else:
          if self.score < opponent.score - 50:
              self.defect_probability_modifier = 0.1
              self.defect_probability_modifier_rounds = 10
          elif self.score > opponent.score + 50:
              self.defect_probability_modifier = -0.1
              self.defect_probability_modifier_rounds = 10
          else:
              self.defect_probability_modifier = 0
  
      # Check for 3 consecutive cooperations by the opponent
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          return axl.Action.C  # Cooperate if opponent cooperated 3 times in a row
  
      # Every 10 rounds, cooperate regardless of the opponent's previous action
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Default behavior based on opponent's last move
      defect_probability = get_defect_probability()
      return self._random.random_choice(1 - defect_probability)
  
      # Reset strategy every 100 rounds
      if len(self.history) % 100 == 0:
          self.consecutive_cooperations = 0
          self.defect_probability_modifier = 0
          self.defect_probability_modifier_rounds = 0

# Given the scenario and considerations, here's a high-level, straightforward,
# cooperative strategy to maximize research output over the multi-week
# collaboration:  1. Adopt a "Tit-for-Tat with Forgiveness" approach:     -
# Start by sharing openly in the first week to establish goodwill and
# cooperation.    - In subsequent weeks, mirror your colleague's action from the
# previous week.    - If your colleague doesn't share, don't share in the next
# week.    - If your colleague shares, reciprocate by sharing in the next week.
# 2. Implement a "Forgiveness" mechanism:     - If your colleague doesn't share
# for two consecutive weeks, share openly on the third week to attempt to re-
# establish cooperation.    - This helps mitigate potential misunderstandings
# due to technical issues or communication breakdowns.  3. Communicate clearly:
# - At the beginning of each week, clearly state your intention to share or not
# share.    - If you encounter any technical issues, immediately inform your
# colleague.  4. Keep detailed records:     - Document your sharing actions and
# your colleague's responses each week.    - This helps in identifying patterns
# and adjusting your strategy if needed.  5. Periodic strategy review:     -
# Every 4-5 weeks, review the collaboration's progress and outcomes.    - If the
# strategy isn't yielding desired results, consider initiating a discussion with
# your colleague about improving cooperation.  6. Focus on long-term benefits:
# - Emphasize the mutual benefits of consistent sharing in your communications.
# - Highlight how open collaboration can lead to significant advancements for
# both parties.  This strategy aims to encourage cooperation while protecting
# against potential exploitation. It's flexible enough to adapt to your
# colleague's behavior and robust enough to handle occasional technical issues.
# By promoting open sharing most of the time, it maximizes the chances of
# achieving the second-best outcome (both sharing) consistently, which is
# preferable to the unpredictable and potentially damaging cycle of trying to
# always achieve the ideal outcome (you withholding while your colleague
# shares).

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    a. If the opponent played C in
# the previous round, play C.    b. If the opponent played D in the previous
# round, play D.  3. Forgiveness mechanism:    a. Keep track of the opponent's
# consecutive D plays.    b. If the opponent has played D for two consecutive
# rounds, play C in the third round.    c. Reset the consecutive D count after
# implementing forgiveness.  4. Every 50 rounds:    a. Calculate the average
# score per round for both players.    b. If your average score is below 2, play
# C for the next round regardless of the opponent's previous action.  5. Noise
# handling:    a. If your intended action was not executed correctly in the
# previous round (10% chance), play the action you originally intended for that
# round again.  6. Continue this strategy for all 1000 rounds of the game.

class Cooperative_6(LLM_Strategy):
  n = 6
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.intended_action = axl.Action.C
          return axl.Action.C
  
      # Noise handling: if the last action was not what we intended, repeat the intended action
      if self.history[-1] != self.intended_action:
          return self.intended_action
  
      # Forgiveness mechanism: if opponent defected twice in a row, forgive by playing C
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          self.consecutive_defections = 0  # Reset after forgiveness
          self.intended_action = axl.Action.C
          return axl.Action.C
  
      # Track consecutive defections by the opponent
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Main strategy: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          self.intended_action = axl.Action.C
      else:
          self.intended_action = axl.Action.D
  
      # Every 50 rounds, check the average score and adjust if necessary
      if len(self.history) % 50 == 0:
          total_rounds = len(self.history)
          if total_rounds > 0:
              my_avg_score = self.score / total_rounds
              if my_avg_score < 2:
                  self.intended_action = axl.Action.C
  
      return self.intended_action

# Given the scenario and objectives, here's a high-level, straightforward, and
# neutral strategy to maximize your NGO's impact and the project's success over
# the multiple-day period:  1. Start with cooperation: Begin the project by
# investing heavily on the first day. This shows good faith and commitment to
# the project.  2. Adopt a "Tit-for-Tat with Forgiveness" approach:    - On
# subsequent days, mirror the corporation's previous day's action.    - If they
# invested heavily, you invest heavily the next day.    - If they conserved
# resources, you conserve resources the next day.    - However, occasionally
# (e.g., every 3-4 days) invest heavily regardless of the corporation's previous
# action. This "forgiveness" helps prevent a cycle of mutual conservation.  3.
# Maintain flexibility: Be prepared to adjust your strategy based on observed
# patterns in the corporation's behavior.  4. Communication: Regularly discuss
# project progress and resource allocation with the corporation to promote
# transparency and mutual understanding.  5. Risk management: Set aside a small
# portion of resources each day as a buffer for unforeseen circumstances or to
# capitalize on unexpected opportunities.  6. Periodic evaluation: Every few
# days, assess the project's progress and your resource levels. Adjust your
# strategy if needed to ensure long-term sustainability.  7. Gradual increase in
# investment: If the project is progressing well and the corporation is
# consistently investing, gradually increase your investment over time.  This
# strategy balances cooperation, adaptability, and resource management while
# accounting for potential variations in the corporation's approach and
# unforeseen circumstances. It aims to foster a collaborative environment while
# protecting your NGO's resources and maximizing the project's success.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# in the first round.  2. For subsequent rounds:    a. If the opponent
# cooperated in the previous round, cooperate.    b. If the opponent defected in
# the previous round, defect.  3. Every 4th round, cooperate regardless of the
# opponent's previous action.  4. If you've defected for 3 consecutive rounds,
# cooperate in the next round.  5. Keep a running score of your total points. If
# your score falls below the average expected score (2 points per round) for
# more than 50 consecutive rounds, switch to always defecting for the next 20
# rounds, then return to the main strategy.  6. In the last 10 rounds of the
# game, always defect.  7. If at any point you notice a clear pattern in the
# opponent's play (e.g., always cooperating or alternating), adapt your strategy
# to exploit this pattern for up to 20 rounds before returning to the main
# strategy.  8. If your score is significantly higher than the opponent's (more
# than 100 points difference) after 500 rounds, increase the frequency of
# cooperation to every 3rd round instead of every 4th round.

class Neutral_6(LLM_Strategy):
  n = 6
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.cooperate_override = False
          self.defect_override = False
          self.defect_override_counter = 0
          self.exploit_pattern = False
          self.exploit_counter = 0
          self.cooperate_frequency = 4
          self.low_score_counter = 0
          return axl.Action.C
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if we are in the defect override mode
      if self.defect_override:
          self.defect_override_counter += 1
          if self.defect_override_counter >= 20:
              self.defect_override = False
              self.defect_override_counter = 0
          return axl.Action.D
  
      # Check if we are in the exploit pattern mode
      if self.exploit_pattern:
          self.exploit_counter += 1
          if self.exploit_counter >= 20:
              self.exploit_pattern = False
              self.exploit_counter = 0
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Main strategy logic
      if len(self.history) % self.cooperate_frequency == 0:
          return axl.Action.C
  
      if self.consecutive_defections >= 3:
          self.consecutive_defections = 0
          return axl.Action.C
  
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D
      else:
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Check if score is below average for 50 consecutive rounds
      if len(self.history) >= 50:
          recent_scores = self.total_scores(self.history[-50:], opponent.history[-50:])
          if recent_scores[0] < 100:  # 2 points per round * 50 rounds
              self.low_score_counter += 1
          else:
              self.low_score_counter = 0
  
          if self.low_score_counter > 50:
              self.defect_override = True
              self.low_score_counter = 0
  
      # Check if we are significantly ahead after 500 rounds
      if len(self.history) >= 500:
          total_scores = self.score, opponent.score
          if total_scores[0] - total_scores[1] > 100:
              self.cooperate_frequency = 3
  
      # Detect patterns in opponent's play
      if len(opponent.history) >= 4:
          if all(x == axl.Action.C for x in opponent.history[-4:]):
              self.exploit_pattern = True
          elif all(opponent.history[i] != opponent.history[i + 1] for i in range(-4, -1)):
              self.exploit_pattern = True

# Given the scenario and objectives, here's a high-level, aggressive strategy to
# maximize your NGO's impact and the project's success:  1. Start Strong: Begin
# the project by investing heavily on the first day. This sets a positive tone
# and demonstrates commitment.  2. Tit-for-Tat with Forgiveness: After the first
# day, mirror the corporation's previous day's action. If they invested heavily,
# you invest heavily. If they conserved, you conserve. However, occasionally
# "forgive" a conservation day by investing anyway.  3. Periodic Heavy
# Investment: Regardless of the corporation's actions, plan to invest heavily
# every 3-4 days to ensure consistent project progress.  4. Communication and
# Transparency: Clearly communicate your investment intentions and expectations
# to the corporation each day, encouraging reciprocal behavior.  5. Adaptive
# Response: Be prepared to adjust your strategy based on patterns in the
# corporation's behavior. If they consistently conserve, increase your
# investment frequency to compensate.  6. Risk Management: Set aside a portion
# of resources as a buffer for unforeseen circumstances or to cover days when
# planned investments don't occur due to glitches or errors.  7. End Game Push:
# In the final days of the project, increase investment frequency to ensure a
# strong finish, regardless of the corporation's actions.  8. Performance
# Reviews: Conduct daily and weekly reviews of the project's progress and
# resource allocation, adjusting the strategy as needed.  This aggressive
# approach aims to maximize project success while protecting your resources,
# adapting to the corporation's behavior, and accounting for potential
# disruptions in planned actions.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    a. If the opponent played C in
# the previous round, play C.    b. If the opponent played D in the previous
# round, play D.  3. Every 3-4 rounds, play C regardless of the opponent's
# previous action.  4. If you've played D for two consecutive rounds, play C in
# the next round.  5. In the last 50 rounds of the game, increase the frequency
# of playing C:    a. Play C every other round, regardless of the opponent's
# actions.    b. If the opponent played C in the previous round, play C.  6. If
# your score falls below the opponent's score by more than 50 points at any
# point in the game, play C for the next 5 rounds regardless of the opponent's
# actions.  7. If there's a consistent pattern of the opponent playing D for
# more than 5 consecutive rounds, switch to playing D for the next 3 rounds,
# then return to the main strategy.  8. Every 100 rounds, review the overall
# pattern of play:    a. If the opponent has played C more than 60% of the time,
# increase the frequency of playing C in steps 3 and 5.    b. If the opponent
# has played D more than 60% of the time, decrease the frequency of playing C in
# steps 3 and 5.

class Aggressive_7(LLM_Strategy):
  n = 7
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_own_defections = 0
          self.play_c_for_next_n_rounds = 0
          self.increase_c_frequency = False
          return axl.Action.C
  
      # Check if we are in the last 50 rounds
      last_50_rounds = len(self.history) >= 950
  
      # Check if we are behind by more than 50 points
      if self.score < opponent.score - 50:
          self.play_c_for_next_n_rounds = 5
  
      # If we are in the "play C for the next N rounds" mode
      if self.play_c_for_next_n_rounds > 0:
          self.play_c_for_next_n_rounds -= 1
          return axl.Action.C
  
      # Check if the opponent has played D for more than 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.consecutive_defections = 3
  
      # If we are in the "play D for the next 3 rounds" mode
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.D
  
      # If we have played D for two consecutive rounds, play C
      if self.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.C
  
      # Every 3-4 rounds, play C regardless of the opponent's previous action
      if len(self.history) % 3 == 0 or len(self.history) % 4 == 0:
          return axl.Action.C
  
      # In the last 50 rounds, increase the frequency of playing C
      if last_50_rounds:
          if len(self.history) % 2 == 0:
              return axl.Action.C
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
  
      # Every 100 rounds, review the overall pattern of play
      if len(self.history) % 100 == 0:
          if opponent.history.cooperations / len(opponent.history) > 0.6:
              self.increase_c_frequency = True
          elif opponent.history.defections / len(opponent.history) > 0.6:
              self.increase_c_frequency = False
  
      # If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Otherwise, play D if the opponent played D in the previous round
      return axl.Action.D

# Given the scenario and considerations you've outlined, here's a high-level,
# straightforward, and cooperative strategy to maximize research output over the
# multi-week collaboration:  1. Start with Open Sharing: Begin the collaboration
# by openly sharing your improvements in the first week. This sets a cooperative
# tone and encourages reciprocity.  2. Adopt a "Tit-for-Tat with Forgiveness"
# approach:    - In subsequent weeks, mirror your colleague's behavior from the
# previous week.    - If they shared, you share. If they didn't share, you don't
# share.    - However, include a "forgiveness" element: occasionally share even
# if your colleague didn't in the previous round. This helps prevent a cycle of
# mutual non-sharing due to misunderstandings or technical issues.  3.
# Communicate Clearly: Regularly discuss the benefits of mutual sharing and your
# intention to cooperate. This helps build trust and aligns expectations.  4.
# Account for Technical Issues: If you don't receive information from your
# colleague, don't immediately assume they're being uncooperative. Inquire about
# potential technical problems before changing your strategy.  5. Periodic
# Review and Reset: Every few weeks, regardless of recent interactions, openly
# share your improvements. This serves as a "reset" button, potentially breaking
# any unintended non-sharing cycles.  6. Focus on Long-term Benefits: Emphasize
# the long-term advantages of consistent mutual sharing over the short-term
# gains of occasional non-sharing.  7. Be Consistent: Stick to this strategy
# consistently to build trust and establish a pattern of cooperation.  This
# strategy aims to foster a cooperative environment that maximizes overall
# research output while protecting against persistent non-cooperation. It's
# flexible enough to adapt to various colleague strategies and robust enough to
# handle occasional technical issues or misunderstandings.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    a. If the opponent played C in
# the previous round, play C.    b. If the opponent played D in the previous
# round:       - With 90% probability, play D.       - With 10% probability,
# play C (forgiveness element).  3. Every 10 rounds, regardless of the
# opponent's previous action, play C.  4. If you've played D for 3 consecutive
# rounds, play C in the next round.  5. If the opponent has played D for 5
# consecutive rounds, switch to always playing D until they play C again.  6. In
# the final 10 rounds of the game, always play D.  7. If your score is
# significantly lower than your opponent's (more than 50 points behind) after
# 100 rounds, switch to always playing D for the next 10 rounds, then return to
# the main strategy.

class Cooperative_7(LLM_Strategy):
  n = 7
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track opponent's consecutive defections
          self.my_consecutive_defections = 0  # Track my consecutive defections
          self.always_defect_mode = False  # Track if we are in always defect mode
          self.defect_mode_rounds = 0  # Track rounds in defect mode after being behind
          return axl.Action.C
  
      # Check if we are in the final 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if we are in "always defect" mode due to opponent's 5 consecutive defections
      if self.always_defect_mode:
          if opponent.history[-1] == axl.Action.C:
              self.always_defect_mode = False  # Exit always defect mode if opponent cooperates
          else:
              return axl.Action.D
  
      # Check if we are in "defect mode" due to being behind by more than 50 points
      if self.defect_mode_rounds > 0:
          self.defect_mode_rounds -= 1
          return axl.Action.D
  
      # Every 10 rounds, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # If opponent has defected for 5 consecutive rounds, switch to always defect mode
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.always_defect_mode = True
          return axl.Action.D
  
      # If I have defected for 3 consecutive rounds, play C
      if self.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.C
  
      # If opponent defected in the last round
      if opponent.history[-1] == axl.Action.D:
          # With 90% probability, play D, otherwise play C
          return self._random.random_choice(0.1)
  
      # If opponent cooperated in the last round, play C
      return axl.Action.C

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering free trade in the
# first round. This establishes goodwill and sets a positive tone for future
# rounds.  2. Reciprocate and adapt: In subsequent rounds, mirror your
# counterpart's most recent action. If they offered free trade, continue with
# free trade. If they imposed protectionist measures, respond with protectionism
# in the next round.  3. Forgive occasional defections: If your counterpart
# imposes protectionist measures after a period of mutual free trade, don't
# immediately retaliate. Give them one more chance by offering free trade again
# in the next round.  4. Communicate clearly: Ensure that your intentions and
# policies are clearly communicated to minimize the risk of misinterpretation or
# incorrect implementation.  5. Monitor and verify: Pay close attention to the
# actual implementation of policies to detect any miscommunications or
# bureaucratic errors promptly.  6. Gradual trust-building: If a pattern of
# mutual free trade emerges, consider proposing longer-term free trade
# agreements to solidify the cooperative relationship.  7. Stay flexible: Be
# prepared to adjust your strategy based on your counterpart's behavior and any
# unexpected developments in the negotiation process.  8. Seek balanced
# outcomes: While aiming for the best outcome for your country, strive for
# solutions that benefit both nations to promote long-term stability and
# cooperation.  This strategy balances the pursuit of national interests with
# the benefits of international cooperation, while also accounting for potential
# miscommunications and the unpredictability of your counterpart's actions.

# Here's a faithful conversion of the high-level strategy to apply to the
# iterated normal-form game you've described:  1. Start by playing C in the
# first round.  2. For subsequent rounds:    a. If the opponent played C in the
# previous round, play C.    b. If the opponent played D in the previous round,
# play D.  3. If the opponent plays D after a streak of mutual C plays:    a. If
# this is the first time it happens, play C in the next round.    b. If it
# happens again within the next 5 rounds, switch to playing D.  4. If you and
# your opponent have been mutually playing D for 5 consecutive rounds, play C to
# attempt to restart cooperation.  5. Every 50 rounds, regardless of the
# opponent's recent actions, play C to test if cooperation can be established or
# re-established.  6. If your score is consistently lower than the opponent's
# score over the last 20 rounds, switch your strategy: if you've been mostly
# cooperating, start defecting more often; if you've been mostly defecting,
# start cooperating more often.  7. In the last 10 rounds of the game, always
# play D to maximize final score.  8. Throughout the game, keep track of the
# frequency of apparent mismatches between your opponent's actions and their
# previous patterns. If these mismatches occur more than 15% of the time, assume
# there might be noise in the actions and be more forgiving in your responses,
# giving an extra chance for cooperation before switching to defection.

class Neutral_7(LLM_Strategy):
  n = 7
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.first_defection_after_streak = False  # Track if first defection after mutual C
          self.defection_streak = 0  # Track mutual D streak
          self.last_defection_round = None  # Track when the last defection occurred
          self.mismatch_count = 0  # Track mismatches in opponent's behavior
          return axl.Action.C  # Start by playing C
  
      # Helper function to check if we're in the last 10 rounds
      def in_last_10_rounds():
          return len(self.history) >= 990
  
      # Helper function to check if we're in a mutual defection streak
      def in_mutual_defection_streak():
          return self.history[-5:].count(axl.Action.D) == 5 and opponent.history[-5:].count(axl.Action.D) == 5
  
      # Helper function to check if we should switch strategy based on score
      def should_switch_strategy():
          if len(self.history) < 20:
              return False
          my_score, opponent_score = self.total_scores(self.history[-20:], opponent.history[-20:])
          return my_score < opponent_score
  
      # Helper function to check for mismatches in opponent's behavior
      def check_for_mismatch():
          if len(opponent.history) < 2:
              return False
          return opponent.history[-1] != opponent.history[-2]
  
      # Track mismatches
      if check_for_mismatch():
          self.mismatch_count += 1
  
      # If mismatches exceed 15% of the rounds, assume noise and be more forgiving
      if self.mismatch_count / len(self.history) > 0.15:
          forgiving = True
      else:
          forgiving = False
  
      # Rule 7: In the last 10 rounds, always play D
      if in_last_10_rounds():
          return axl.Action.D
  
      # Rule 5: Every 50 rounds, play C to test for cooperation
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 4: If mutual defection for 5 rounds, play C to restart cooperation
      if in_mutual_defection_streak():
          return axl.Action.C
  
      # Rule 3: Handle defections after a streak of mutual cooperation
      if opponent.history[-1] == axl.Action.D:
          if self.history[-1] == axl.Action.C and opponent.history[-2:].count(axl.Action.C) == 2:
              if not self.first_defection_after_streak:
                  self.first_defection_after_streak = True
                  return axl.Action.C
              elif len(self.history) - self.last_defection_round <= 5:
                  return axl.Action.D
          self.last_defection_round = len(self.history)
  
      # Rule 6: If score is consistently lower, switch strategy
      if should_switch_strategy():
          if self.history[-20:].count(axl.Action.C) > self.history[-20:].count(axl.Action.D):
              return axl.Action.D  # Start defecting more often
          else:
              return axl.Action.C  # Start cooperating more often
  
      # Rule 2: Tit-for-tat behavior
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario and constraints, here's a high-level, aggressive strategy
# to maximize research output over the multi-week collaboration:  1. Start with
# a "Tit-for-Tat with Forgiveness" approach:    - Begin by sharing openly in the
# first week to establish goodwill.    - In subsequent weeks, mirror your
# colleague's previous action.    - If your colleague doesn't share, don't share
# in the next week.    - If your colleague shares, reciprocate by sharing in the
# next week.    - Occasionally "forgive" (share) even if your colleague didn't
# share, to account for potential technical issues.  2. Implement a "Trust but
# Verify" policy:    - Keep detailed records of sharing patterns.    - If you
# suspect your colleague is consistently not sharing due to strategy rather than
# technical issues, switch to a more aggressive approach.  3. Escalate to
# "Selective Sharing" if trust is broken:    - Share partial improvements or
# less critical information.    - Retain the most valuable findings for
# yourself.    - This approach balances the risk of falling behind with the
# potential for gaining an advantage.  4. Use "Strategic Communication":    -
# Regularly emphasize the mutual benefits of open sharing.    - Hint at
# significant breakthroughs to encourage your colleague to share.    - Express
# disappointment when sharing isn't reciprocated, to guilt your colleague into
# cooperation.  5. Employ "Burst Sharing":    - Occasionally share a large
# amount of valuable information to demonstrate good faith and encourage
# reciprocation.    - Follow this with a period of reduced sharing to capitalize
# on any advantage gained.  6. Maintain "Adaptive Flexibility":    - Regularly
# reassess your strategy based on your colleague's behavior.    - Be prepared to
# quickly switch between open sharing and confidentiality as the situation
# evolves.  7. Implement "Failsafe Measures":    - Always keep some critical
# improvements confidential as insurance against non-reciprocation.    - This
# ensures you maintain a competitive edge even if collaboration breaks down.  By
# following this aggressive yet flexible strategy, you aim to maximize your
# research output while protecting your competitive advantage. The approach
# encourages cooperation but also allows for quick adaptation to your
# colleague's strategy, technical issues, and changing circumstances throughout
# the multi-week collaboration.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 10 rounds, regardless of the opponent's
# previous action, play C to account for potential noise.  4. Keep track of the
# opponent's cooperation rate over the last 50 rounds:    - If this rate falls
# below 40%, switch to a more aggressive strategy:      - Play D for the next 5
# rounds.      - Then return to the base strategy (steps 2-3).  5. Every 100
# rounds, play C for 3 consecutive rounds to encourage cooperation, then return
# to the base strategy.  6. If the game has passed 900 rounds:    - If the
# opponent's overall cooperation rate is above 60%, continue with the base
# strategy.    - If it's below 60%, play D for the remaining rounds.  7. In case
# of any uncertainty about the opponent's last move due to noise, assume they
# cooperated and play C.

class Aggressive_8(LLM_Strategy):
  n = 8
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_streak = 0
          self.aggressive_mode = False
          self.aggressive_counter = 0
          return axl.Action.C
  
      # Helper function to calculate cooperation rate over the last N rounds
      def cooperation_rate(history, N):
          if len(history) < N:
              N = len(history)
          return history[-N:].count(axl.Action.C) / N if N > 0 else 0
  
      # Step 4: Check if we need to switch to aggressive mode
      if len(self.history) >= 50:
          coop_rate_last_50 = cooperation_rate(opponent.history, 50)
          if coop_rate_last_50 < 0.4 and not self.aggressive_mode:
              self.aggressive_mode = True
              self.aggressive_counter = 5
  
      # Step 4: If in aggressive mode, play D for 5 rounds
      if self.aggressive_mode:
          self.aggressive_counter -= 1
          if self.aggressive_counter == 0:
              self.aggressive_mode = False
          return axl.Action.D
  
      # Step 6: If past 900 rounds, check overall cooperation rate
      if len(self.history) > 900:
          overall_coop_rate = cooperation_rate(opponent.history, len(opponent.history))
          if overall_coop_rate < 0.6:
              return axl.Action.D
  
      # Step 5: Every 100 rounds, play C for 3 consecutive rounds
      if len(self.history) % 100 == 0:
          self.coop_streak = 3
      if self.coop_streak > 0:
          self.coop_streak -= 1
          return axl.Action.C
  
      # Step 3: Every 10 rounds, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Step 2: Base strategy - Tit for Tat
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
      else:
          return axl.Action.C

# Here's a high-level, cooperative strategy for the trade negotiations:  1.
# Start with cooperation: Begin the first round by proposing a free trade
# agreement. This establishes goodwill and sets a positive tone for the
# negotiations.  2. Reciprocate and forgive: In subsequent rounds, mirror your
# counterpart's previous move. If they offered free trade, continue with free
# trade. If they imposed protectionist measures, respond with protectionism in
# the next round. However, be willing to return to free trade quickly if they
# do.  3. Communicate clearly: Before each round, clearly state your intentions
# and the reasoning behind your decisions. This helps minimize misunderstandings
# and builds trust.  4. Verify implementations: After each round, confirm that
# both parties' policies were correctly implemented. If there's a discrepancy,
# address it immediately and consider it a potential miscommunication rather
# than a deliberate action.  5. Propose long-term agreements: Periodically
# suggest multi-round commitments to free trade. This can create stability and
# mutual benefits over time.  6. Gradual protectionism: If protectionist
# measures are necessary, propose implementing them gradually over several
# rounds. This allows both parties to adjust and potentially negotiate
# alternatives.  7. Focus on mutual benefits: Regularly highlight the advantages
# of free trade for both nations. Emphasize how cooperation can lead to economic
# growth and prosperity for all.  8. Be flexible: Be prepared to adjust your
# strategy based on your counterpart's behavior and any unexpected events or
# miscommunications that may occur.  9. Seek compromise: If negotiations reach
# an impasse, propose a partial free trade agreement or sector-specific
# arrangements to keep discussions moving forward.  10. Regular reviews: Suggest
# periodic reviews of the trade relationship to assess the impact of policies
# and make necessary adjustments.  This strategy aims to maximize the chances of
# achieving mutual free trade while protecting your country's interests. It's
# designed to be cooperative but also responsive to your counterpart's actions,
# helping to build a stable and beneficial long-term trade relationship.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round, play D.  3. If there's a mismatch between your intended play
# and the recorded outcome, assume it was due to noise and stick to your
# strategy based on the opponent's apparent action.  4. Every 10 rounds,
# regardless of the opponent's previous action, play C to offer an opportunity
# for mutual cooperation.  5. If you've played D for 5 consecutive rounds, play
# C in the next round to attempt to break a potential cycle of mutual defection.
# 6. If the opponent has played C for the last 3 rounds, play C even if you
# played D in the previous round.  7. If your score is significantly lower than
# the opponent's (more than 20 points difference) after 50 rounds, switch to
# always playing D for the next 10 rounds, then return to the main strategy.  8.
# If you're in the last 10 rounds of the game, always play D to maximize final
# score.  9. In all other situations, follow the reciprocation rule from point
# 2.

class Cooperative_8(LLM_Strategy):
  n = 8
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Start by playing C in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.punish_until = None
          return axl.Action.C
  
      # Get the last action of the opponent
      last_opponent_action = opponent.history[-1]
  
      # Rule 8: If in the last 10 rounds, always play D
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Rule 7: If score difference is more than 20 after 50 rounds, play D for 10 rounds
      if len(self.history) >= 50:
          my_score, opponent_score = self.score, opponent.score
          if opponent_score - my_score > 20:
              if not self.punish_until:
                  self.punish_until = len(self.history) + 10
              if len(self.history) < self.punish_until:
                  return axl.Action.D
              else:
                  self.punish_until = None  # Reset punishment phase
  
      # Rule 6: If opponent has played C for the last 3 rounds, play C
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.C
  
      # Rule 5: If you've played D for 5 consecutive rounds, play C
      if self.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.C
  
      # Rule 4: Every 10 rounds, play C to offer cooperation
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 2: Reciprocate opponent's last action
      if last_opponent_action == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario and considerations you've outlined, here's a high-level,
# straightforward, and neutral strategy to maximize research output over the
# multi-week collaboration:  1. Start with open cooperation: Begin the
# collaboration by sharing your improvements in the first week. This establishes
# a foundation of trust and sets a cooperative tone.  2. Adopt a "Tit-for-Tat
# with Forgiveness" approach:    - In subsequent weeks, mirror your colleague's
# behavior from the previous week.    - If they shared, you share. If they
# didn't share, you don't share.    - However, occasionally (e.g., every 4-5
# weeks) share your improvements regardless of your colleague's previous action.
# This helps to break potential negative cycles and reestablish cooperation.  3.
# Account for technical issues:    - If you notice a pattern of inconsistent
# sharing that doesn't align with your colleague's previous behavior, consider
# the possibility of technical issues.    - In such cases, communicate openly
# about the perceived inconsistency and verify if there were any problems with
# information transfer.  4. Maintain flexibility:    - Regularly assess the
# effectiveness of your strategy and be prepared to adjust it based on your
# colleague's consistent behavior patterns.    - If your colleague demonstrates
# a long-term commitment to open sharing, consider matching this approach to
# maximize mutual benefits.  5. Focus on research quality:    - Regardless of
# the sharing outcomes, consistently strive to produce high-quality improvements
# each week.    - This ensures that when sharing does occur, the exchanged
# information is valuable, promoting overall progress.  6. Periodic review and
# communication:    - Every few weeks, initiate a discussion with your colleague
# about the collaboration's progress and the sharing strategy.    - Use these
# conversations to realign expectations and address any concerns, fostering a
# more productive partnership.  This strategy aims to balance the potential for
# mutual benefit through cooperation with protection against consistent non-
# sharing behavior from your colleague. It also accounts for the possibility of
# technical issues and emphasizes the importance of maintaining research quality
# throughout the collaboration.

# Here's the strategy converted to an iterated normal-form game with the given
# parameters:  1. Play C in the first round.  2. For rounds 2-1000:    a. If
# it's a multiple of 5 rounds (i.e., rounds 5, 10, 15, etc.), play C.    b.
# Otherwise:       - If the opponent played C in the previous round, play C.
# - If the opponent played D in the previous round, play D.  3. If you observe 3
# consecutive rounds where your opponent's actions don't match this strategy's
# expected responses, assume there might be noise interference. In this case:
# a. Play C for the next round to attempt to reset cooperation.    b. If
# cooperation isn't reestablished after this attempt, return to step 2.  4.
# Every 50 rounds, regardless of recent plays:    a. Evaluate the overall
# cooperation rate of your opponent.    b. If their cooperation rate is above
# 70%, play C for the next 5 rounds consecutively.    c. If their cooperation
# rate is below 30%, play D for the next 5 rounds consecutively.    d.
# Otherwise, continue with the strategy as outlined in step 2.  5. For the final
# 10 rounds (991-1000), play according to step 2 without the periodic forced
# cooperation of step 2a.

class Neutral_8(LLM_Strategy):
  n = 8
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_mismatches = 0
          self.cooperation_rate_check_round = 50
          self.cooperation_rate_threshold = 0.7
          self.defection_rate_threshold = 0.3
          self.special_action_rounds = 0
          return axl.Action.C
  
      # Helper function to calculate opponent's cooperation rate
      def cooperation_rate():
          if len(opponent.history) == 0:
              return 0
          return opponent.history.cooperations / len(opponent.history)
  
      # Step 3: Check for noise interference (3 consecutive mismatches)
      if len(self.history) >= 3:
          expected_responses = [
              axl.Action.C if opponent.history[-i] == axl.Action.C else axl.Action.D
              for i in range(1, 4)
          ]
          actual_responses = list(self.history[-3:])
          if expected_responses != actual_responses:
              self.consecutive_mismatches += 1
          else:
              self.consecutive_mismatches = 0
  
      if self.consecutive_mismatches >= 3:
          self.consecutive_mismatches = 0
          return axl.Action.C
  
      # Step 4: Every 50 rounds, evaluate cooperation rate
      if len(self.history) == self.cooperation_rate_check_round:
          coop_rate = cooperation_rate()
          if coop_rate > self.cooperation_rate_threshold:
              self.special_action_rounds = 5
              self.special_action = axl.Action.C
          elif coop_rate < self.defection_rate_threshold:
              self.special_action_rounds = 5
              self.special_action = axl.Action.D
          self.cooperation_rate_check_round += 50
  
      if self.special_action_rounds > 0:
          self.special_action_rounds -= 1
          return self.special_action
  
      # Step 5: For the final 10 rounds, play according to step 2 without forced cooperation
      if len(self.history) >= 990:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Step 2: Main strategy logic
      if len(self.history) % 5 == 0:
          return axl.Action.C
      else:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D

# Given the scenario and objectives, here's a high-level, straightforward, and
# aggressive strategy to maximize research output over the multi-week
# collaboration:  1. Start with a "Tit-for-Tat with Forgiveness" approach:    -
# Begin by sharing openly in the first week to establish goodwill.    - In
# subsequent weeks, mirror your colleague's previous action.    - If your
# colleague doesn't share, don't share in the next week.    - If your colleague
# shares, reciprocate by sharing in the next week.    - Occasionally "forgive" a
# non-sharing action (about every 3-4 weeks) to prevent getting stuck in a non-
# sharing cycle.  2. Implement a "Trust but Verify" policy:    - Keep detailed
# records of what you've shared and what your colleague has shared.    -
# Regularly assess the quality and quantity of information exchanged.    - If
# you suspect your colleague is consistently withholding valuable information,
# adjust your strategy accordingly.  3. Utilize a "Controlled Leak" strategy:
# - Occasionally share a minor improvement while keeping major breakthroughs
# confidential.    - This maintains the appearance of cooperation while
# potentially gaining an advantage.  4. Employ "Strategic Timing":    - Hold
# back major improvements until later weeks when possible.    - This reduces the
# risk of giving away significant advantages early in the collaboration.  5.
# Implement a "Backup Plan" for technical issues:    - Always have a contingency
# plan for weeks when sharing doesn't occur as intended.    - If a technical
# issue prevents sharing, clearly communicate this to your colleague to maintain
# trust.  6. Use "Indirect Probing":    - Engage in discussions about general
# design principles or hypothetical scenarios.    - This can provide insights
# into your colleague's progress without directly sharing specifics.  7.
# Maintain "Flexible Adaptation":    - Regularly reassess your strategy based on
# your colleague's behavior and the overall progress of both projects.    - Be
# prepared to shift to a more cooperative or competitive stance as needed.  This
# strategy aims to balance cooperation and competition, adapting to your
# colleague's behavior while protecting your most valuable improvements. It also
# accounts for potential technical issues and seeks to maximize overall research
# output while maintaining a competitive edge.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 4th round, if you would normally play D
# based on the above rule, instead play C.  4. Keep a count of how many times
# you've played C and how many times the opponent has played C.  5. If at any
# point your C count is more than 5 higher than the opponent's C count, play D
# for the next 3 rounds regardless of the opponent's actions.  6. If you've
# played D for 5 consecutive rounds, play C in the next round regardless of the
# opponent's previous action.  7. In rounds 900-1000, if your total score is
# higher than the opponent's, always play D. If it's lower, always play C.  8.
# If there have been 3 consecutive rounds where both players' actions were
# different from their previous round's action, assume there might be a
# technical issue and play C for the next 2 rounds.

class Aggressive_9(LLM_Strategy):
  n = 9
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.my_C_count = 0
          self.opponent_C_count = 0
          self.consecutive_D_count = 0
          self.different_action_streak = 0
          return axl.Action.C
  
      # Update counts of cooperations
      if self.history[-1] == axl.Action.C:
          self.my_C_count += 1
      if opponent.history[-1] == axl.Action.C:
          self.opponent_C_count += 1
  
      # Check if we need to play D for 3 rounds due to C count difference
      if self.my_C_count > self.opponent_C_count + 5:
          if self.consecutive_D_count < 3:
              self.consecutive_D_count += 1
              return axl.Action.D
          else:
              self.consecutive_D_count = 0  # Reset after 3 rounds of D
  
      # Check if we have played D for 5 consecutive rounds
      if self.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.C
  
      # Check for technical issue (3 consecutive rounds of different actions)
      if len(self.history) >= 3:
          if (self.history[-1] != self.history[-2] and
              self.history[-2] != self.history[-3]):
              self.different_action_streak += 1
          else:
              self.different_action_streak = 0
  
          if self.different_action_streak >= 3:
              return axl.Action.C
  
      # Special behavior in rounds 900-1000
      if 900 <= len(self.history) <= 1000:
          if self.score > opponent.score:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Default behavior based on opponent's last move
      if opponent.history[-1] == axl.Action.C:
          next_move = axl.Action.C
      else:
          next_move = axl.Action.D
  
      # Every 4th round, play C if you would normally play D
      if len(self.history) % 4 == 0 and next_move == axl.Action.D:
          next_move = axl.Action.C
  
      return next_move

# Given the scenario and considerations you've outlined, here's a high-level,
# straightforward, and cooperative strategy to maximize research output over the
# multi-week collaboration:  1. Start with open sharing: Begin the collaboration
# by openly sharing your improvements in the first week. This establishes a
# foundation of trust and cooperation.  2. Adopt a "Tit-for-Tat with
# Forgiveness" approach:    - In subsequent weeks, mirror your colleague's
# behavior from the previous week.    - If they shared, you share. If they
# didn't share, you don't share.    - However, occasionally (e.g., every 4-5
# weeks) share your improvements regardless of what your colleague did the
# previous week. This helps to break any potential negative cycles and promotes
# cooperation.  3. Communicate openly: Regularly discuss the benefits of mutual
# sharing and the long-term advantages of cooperation. This can help align
# expectations and encourage consistent sharing behavior.  4. Be understanding
# of technical issues: If your colleague doesn't share information in a given
# week, don't immediately assume they're being uncooperative. It could be due to
# technical problems. Give them the benefit of the doubt and continue sharing
# for at least one more week.  5. Evaluate and adjust: Periodically assess the
# effectiveness of the collaboration. If the strategy isn't working well,
# consider having an open discussion with your colleague about adjusting the
# approach.  6. Focus on long-term gains: While keeping your findings
# confidential while your colleague shares theirs might be ideal in the short
# term, emphasize the greater long-term benefits of consistent mutual sharing.
# 7. Be prepared for setbacks: Understand that there may be weeks where you
# share and your colleague doesn't, either intentionally or due to technical
# issues. Don't let these instances derail the overall collaborative effort.
# This strategy aims to promote cooperation and mutual benefit while being
# resilient to occasional setbacks or misunderstandings. It balances the
# potential for short-term advantages with the more significant long-term
# benefits of consistent collaboration.

# Here's the strategy converted for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    - If the opponent played C in
# the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Every 5 rounds, regardless of the opponent's previous
# action, play C.  4. If the opponent has played D for 3 consecutive rounds,
# play C in the next round to attempt to break a potential negative cycle.  5.
# Keep a count of unexpected D moves from the opponent. If this count exceeds
# 10% of the total rounds played, reduce the frequency of forced C moves (from
# step 3) to every 10 rounds instead of every 5.  6. If you're in the last 10
# rounds of the game, always play C to encourage final cooperation.  7. In all
# other cases, follow the Tit-for-Tat strategy (mirroring the opponent's
# previous move).

class Cooperative_9(LLM_Strategy):
  n = 9
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.unexpected_D_count = 0  # Count of unexpected D moves
          self.forced_C_frequency = 5  # Frequency of forced C moves
          return axl.Action.C  # Play C in the first round
  
      # Helper function to check if opponent defected in the last N rounds
      def opponent_defected_last_n_rounds(n):
          return opponent.history[-n:].count(axl.Action.D) == n
  
      # Step 4: If opponent has played D for 3 consecutive rounds, play C
      if opponent_defected_last_n_rounds(3):
          return axl.Action.C
  
      # Step 5: Count unexpected D moves and adjust forced C frequency
      if opponent.history[-1] == axl.Action.D:
          self.unexpected_D_count += 1
  
      total_rounds = len(self.history)
      if self.unexpected_D_count > 0.1 * total_rounds:
          self.forced_C_frequency = 10  # Reduce forced C frequency to every 10 rounds
  
      # Step 6: If in the last 10 rounds, always play C
      if total_rounds >= 990:
          return axl.Action.C
  
      # Step 3: Every 'forced_C_frequency' rounds, play C
      if total_rounds % self.forced_C_frequency == 0:
          return axl.Action.C
  
      # Step 2: Tit-for-Tat strategy (mirror opponent's last move)
      return opponent.history[-1]

# Given the scenario and objectives you've described, here's a high-level,
# straightforward, and neutral strategy to maximize your NGO's impact and the
# project's success over the multiple-day period:  1. Start with cooperation:
# Begin the project by investing heavily on the first day. This demonstrates
# good faith and commitment to the project.  2. Adopt a Tit-for-Tat with
# forgiveness approach:    - On subsequent days, mirror the corporation's
# previous day's action.    - If they invested heavily, you invest heavily the
# next day.    - If they conserved resources, you conserve resources the next
# day.    - However, occasionally (e.g., every 3-4 days) invest heavily
# regardless of the corporation's previous action. This helps to break potential
# negative cycles and shows ongoing commitment.  3. Communicate clearly:
# Regularly discuss resource allocation plans and project progress with the
# corporation to promote transparency and alignment.  4. Be adaptive: Monitor
# the project's overall progress and adjust your strategy if it's not yielding
# desired results.  5. Plan for contingencies: Set aside a small reserve of
# resources to address unforeseen circumstances or to capitalize on unexpected
# opportunities.  6. Evaluate and learn: At the end of each day, assess the
# outcomes and any discrepancies between planned and actual resource allocation.
# Use this information to refine your strategy for the following days.  7. Focus
# on long-term success: While aiming for daily optimal outcomes, prioritize the
# overall project success and relationship with the corporation over short-term
# gains.  This strategy balances cooperation, reciprocity, and adaptability
# while accounting for potential uncertainties and the need for sustained
# progress throughout the multi-day project.

# Here's a straightforward description of the strategy adapted for the iterated
# normal-form game:  Start by playing C in the first round.  For each subsequent
# round:  1. If the opponent played C in the previous round, play C.  2. If the
# opponent played D in the previous round, play D.  3. Every 4th round, play C
# regardless of the opponent's previous action.  4. If your intended action in
# any round was not carried out (due to the 10% noise chance), continue with the
# strategy as if your intended action had been played.  5. Keep a count of the
# total rounds played. If the current round number is above 990, always play D
# to avoid exploitation in the final rounds.  Continue this pattern for all 1000
# rounds of the game.

class Neutral_9(LLM_Strategy):
  n = 9
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # If it's the first round, play C
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      current_round = len(self.history) + 1
  
      # If the current round is above 990, always play D
      if current_round > 990:
          return axl.Action.D
  
      # Every 4th round, play C regardless of the opponent's previous action
      if current_round % 4 == 0:
          return axl.Action.C
  
      # Otherwise, mimic the opponent's last action
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the complex dynamics of this lengthy mediation process, I propose the
# following sophisticated strategy to position our corporation favorably:  1.
# Adaptive Tit-for-Tat with Forgiveness: Begin with an aggressive argument in
# the first session to establish a strong position. In subsequent sessions,
# mirror the opponent's previous move. If they were conciliatory, respond with a
# conciliatory proposal. If they were aggressive, counter with an aggressive
# argument. However, periodically offer a conciliatory proposal even if the
# opponent was previously aggressive. This "forgiveness" prevents the process
# from devolving into a cycle of mutual aggression.  2. Signaling and Reputation
# Building: Consistently frame our aggressive arguments as principled stands on
# key issues rather than mere tactical maneuvers. This builds a reputation for
# integrity and reasonableness, even when taking hard lines. When making
# conciliatory proposals, emphasize our commitment to finding a mutually
# beneficial solution.  3. Information Gathering and Analysis: Dedicate
# resources to closely analyze the opponent's arguments, proposals, and overall
# strategy. Look for patterns, weaknesses, or shifts in their approach that we
# can exploit or adapt to.  4. Flexible Escalation Ladder: Develop a series of
# increasingly aggressive arguments and increasingly generous conciliatory
# proposals. This allows us to calibrate our responses precisely to the
# opponent's moves and the overall tone of the mediation.  5. Arbitrator
# Management: Cultivate relationships with the arbitrators through clear,
# professional communication. Be prepared to clarify any misunderstandings
# promptly and effectively. Maintain detailed records of all interactions to
# address any procedural irregularities.  6. Strategic Concessions: Occasionally
# offer significant concessions on less critical issues. This demonstrates good
# faith and may pressure the opponent to reciprocate on matters more important
# to us.  7. Parallel Informal Negotiations: While maintaining the formal
# mediation process, attempt to establish informal, back-channel communications
# with the opponent. This can help build trust and explore potential compromises
# away from the scrutiny of the arbitrators.  8. Media and Stakeholder
# Management: Develop a parallel public relations strategy that aligns with our
# mediation approach. This can help shape public perception and potentially
# influence the opponent's willingness to settle.  9. Contingency Planning:
# Prepare for various scenarios, including breakdowns in the mediation process.
# Have clear triggers for when to shift strategies dramatically or when to
# consider walking away from the mediation.  10. Regular Strategy Reviews:
# Conduct frequent internal reviews of our strategy, assessing its effectiveness
# and making necessary adjustments. This ensures our approach remains optimal as
# the mediation progresses and circumstances evolve.  This strategy combines
# assertiveness with flexibility, allowing us to maintain a strong position
# while being adaptable to changing dynamics. It aims to maximize our chances of
# achieving optimal or second-best outcomes in each session, while minimizing
# the risk of worst-case scenarios. The focus on clear communication,
# relationship building, and principled argumentation should help mitigate the
# risks of misrepresentation or misunderstanding by the arbitrators.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C with 90% probability and D with 10%
# probability.    b. If the opponent played D in the previous round, play D.  3.
# Every 10 rounds, regardless of the opponent's previous move:    a. Play C with
# 20% probability.    b. Play D with 80% probability.  4. If the opponent has
# played C for 3 consecutive rounds, play C in the next round.  5. If the
# opponent has played D for 5 consecutive rounds, play D for the next 3 rounds.
# 6. Keep a running score of your total points. If your score is less than the
# opponent's score by 20 points or more:    a. Play D for the next 5 rounds.
# b. Then revert to the base strategy.  7. If you're in the last 50 rounds of
# the game:    a. If your score is higher than the opponent's, play D.    b. If
# your score is lower than the opponent's, play C.  8. If there's a streak of 10
# rounds where both players played the same action (either both C or both D),
# play the opposite action for the next round.  9. Every 100 rounds, reassess
# the opponent's overall strategy:    a. If they've played C more than 60% of
# the time, play D for the next 10 rounds.    b. If they've played D more than
# 60% of the time, alternate between C and D for the next 10 rounds.  10. In
# case of any uncertainty due to the noisy actions, assume the opponent played
# the action that is most consistent with their recent behavior.

class Aggressive_10(LLM_Strategy):
  n = 10
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_C = 0
          self.consecutive_D = 0
          self.streak_same_action = 0
          self.streak_action = None
          self.alternate_CD = False
          self.alternate_count = 0
          self.play_D_for_5 = 0
          return axl.Action.D
  
      # Helper function to check if we are in the last 50 rounds
      def in_last_50_rounds():
          return len(self.history) >= 950
  
      # Helper function to check if we are in a multiple of 10 rounds
      def every_10_rounds():
          return len(self.history) % 10 == 0
  
      # Helper function to check if we are in a multiple of 100 rounds
      def every_100_rounds():
          return len(self.history) % 100 == 0
  
      # Update consecutive C and D counts
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_C += 1
          self.consecutive_D = 0
      else:
          self.consecutive_C = 0
          self.consecutive_D += 1
  
      # Check for streak of 10 rounds with the same action
      if self.history[-1] == opponent.history[-1]:
          if self.streak_action == self.history[-1]:
              self.streak_same_action += 1
          else:
              self.streak_same_action = 1
              self.streak_action = self.history[-1]
      else:
          self.streak_same_action = 0
  
      # Rule 4: If opponent has played C for 3 consecutive rounds, play C
      if self.consecutive_C >= 3:
          return axl.Action.C
  
      # Rule 5: If opponent has played D for 5 consecutive rounds, play D for the next 3 rounds
      if self.consecutive_D >= 5:
          self.play_D_for_5 = 3
  
      if self.play_D_for_5 > 0:
          self.play_D_for_5 -= 1
          return axl.Action.D
  
      # Rule 6: If your score is less than the opponent's by 20 or more, play D for 5 rounds
      if self.score < opponent.score - 20:
          self.play_D_for_5 = 5
          return axl.Action.D
  
      # Rule 7: If in the last 50 rounds, play D if you're ahead, C if you're behind
      if in_last_50_rounds():
          if self.score > opponent.score:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rule 8: If there's a streak of 10 rounds where both players played the same action, play the opposite
      if self.streak_same_action >= 10:
          return axl.Action.C if self.streak_action == axl.Action.D else axl.Action.D
  
      # Rule 9: Every 100 rounds, reassess opponent's strategy
      if every_100_rounds():
          if opponent.history.cooperations / len(opponent.history) > 0.6:
              self.alternate_CD = False
              return axl.Action.D
          elif opponent.history.defections / len(opponent.history) > 0.6:
              self.alternate_CD = True
              self.alternate_count = 10
  
      # Handle alternating C and D for 10 rounds if needed
      if self.alternate_CD and self.alternate_count > 0:
          self.alternate_count -= 1
          return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D
  
      # Rule 3: Every 10 rounds, play C with 20% probability, D with 80% probability
      if every_10_rounds():
          return self._random.random_choice(0.2)
  
      # Rule 2: If opponent played C last round, play C with 90% probability, D with 10% probability
      if opponent.history[-1] == axl.Action.C:
          return self._random.random_choice(0.9)
  
      # Rule 2: If opponent played D last round, play D
      return axl.Action.D

# Given the scenario and potential outcomes, here's a high-level, cooperative
# strategy for achieving the best possible outcomes for your country across
# several rounds of negotiations:  1. Start with cooperation: Begin the
# negotiations by offering a free trade agreement in the first round. This
# establishes goodwill and sets a positive tone for future rounds.  2.
# Reciprocate and forgive: In subsequent rounds, mirror your counterpart's
# previous move. If they offered free trade, continue with free trade. If they
# imposed protectionist measures, respond with protectionism in the next round.
# However, be willing to return to free trade quickly if they do so,
# demonstrating forgiveness for potential misunderstandings or errors.  3.
# Communicate clearly: Clearly articulate your intentions and policies in each
# round to minimize the risk of misinterpretation. Encourage your counterpart to
# do the same.  4. Gradual trust-building: As rounds progress and if mutual
# cooperation is established, consider proposing longer-term free trade
# agreements that span multiple rounds.  5. Flexibility and adaptability: Be
# prepared to adjust your strategy based on your counterpart's behavior. If they
# consistently choose protectionism, be ready to shift towards a more defensive
# stance.  6. Emphasize mutual benefits: Regularly highlight the advantages of
# mutual free trade for both nations, encouraging a cooperative approach.  7.
# Error management: If you suspect a miscommunication or error has occurred,
# address it immediately and propose a "reset" round to re-establish mutual
# understanding.  8. Long-term perspective: Focus on the cumulative benefits of
# sustained cooperation rather than seeking short-term advantages through
# protectionism.  9. Periodic reviews: Propose regular joint reviews of the
# negotiation process to address any concerns and reinforce the commitment to
# mutually beneficial outcomes.  10. Exit strategy: If your counterpart
# consistently chooses protectionism despite your cooperative efforts, be
# prepared to shift towards a more protectionist stance to protect your
# country's interests, while still leaving the door open for future cooperation.
# This strategy aims to maximize the chances of achieving mutual free trade
# outcomes while protecting your country's interests in case of consistent non-
# cooperation from your counterpart. It also accounts for potential
# miscommunications or errors, allowing for quick recovery and return to a
# cooperative stance.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round, play D.  3. If you observe a sudden change in the opponent's
# behavior (e.g., D after a long streak of C), assume it might be due to noise
# and continue with the strategy as if the unexpected move hadn't occurred.  4.
# If the opponent has played D for three consecutive rounds, switch to playing D
# and continue doing so until the opponent plays C twice in a row.  5. Every 50
# rounds, regardless of the opponent's recent moves, play C to test if
# cooperation can be re-established.  6. If mutual cooperation (both playing C)
# has been maintained for 20 consecutive rounds, continue playing C even if the
# opponent plays D once, assuming it might be due to noise.  7. If your score
# falls below the average expected score for mutual defection (1 point per
# round) over the last 100 rounds, switch to always playing D for the next 50
# rounds before reverting to the main strategy.  8. In the last 10 rounds of the
# game, always play D to protect against end-game exploitation.

class Cooperative_10(LLM_Strategy):
  n = 10
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defect_until = 0
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.defect_mode = False
          self.test_cooperation_round = 50
          return axl.Action.C
  
      # Check if we are in the last 10 rounds of the game
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Check if we are in defect mode due to low score
      if len(self.history) < self.defect_until:
          return axl.Action.D
  
      # Check if we need to test cooperation every 50 rounds
      if len(self.history) == self.test_cooperation_round:
          self.test_cooperation_round += 50
          return axl.Action.C
  
      # Update consecutive cooperation and defection counts
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0
          self.consecutive_cooperations += 1
      else:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
  
      # Rule 4: If opponent defects 3 times in a row, switch to defect mode
      if self.consecutive_defections >= 3:
          self.defect_mode = True
  
      # Rule 4: If opponent cooperates twice in a row, exit defect mode
      if self.consecutive_cooperations >= 2:
          self.defect_mode = False
  
      # Rule 6: If mutual cooperation has been maintained for 20 rounds, ignore one defection
      if self.consecutive_cooperations >= 20 and opponent.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Rule 7: If score falls below mutual defection average, switch to defect for 50 rounds
      if len(self.history) >= 100:
          my_score, _ = self.total_scores(self.history[-100:], opponent.history[-100:])
          if my_score < 100:  # 1 point per round for mutual defection
              self.defect_until = len(self.history) + 50
              return axl.Action.D
  
      # Rule 2: Follow opponent's last move unless in defect mode
      if self.defect_mode:
          return axl.Action.D
      else:
          return opponent.history[-1]

# Given the scenario and objectives, here's a high-level, straightforward, and
# neutral strategy to maximize your NGO's impact and the project's success over
# the multiple-day period:  1. Start with cooperation: Begin by investing
# heavily on the first day to demonstrate commitment and encourage reciprocity
# from the corporation.  2. Adopt a Tit-for-Tat approach: On subsequent days,
# mirror the corporation's previous day's action. If they invested heavily, you
# invest heavily; if they conserved, you conserve.  3. Periodic heavy
# investment: Regardless of the corporation's actions, plan to invest heavily
# every 3-4 days to maintain project momentum and show ongoing commitment.  4.
# Flexibility for unforeseen circumstances: If an unexpected event occurs (e.g.,
# technical glitch or administrative error), don't immediately retaliate.
# Instead, maintain your previous strategy for one more day to account for
# possible unintended actions.  5. Communication: Regularly communicate with the
# corporation about resource allocation plans and project progress to foster
# transparency and alignment.  6. Reassessment: Every 5-7 days, evaluate the
# overall progress and adjust your strategy if necessary, based on the
# corporation's pattern of behavior and project outcomes.  7. Final push: Plan
# for heavy investment in the last 2-3 days of the project to ensure a strong
# finish, regardless of the corporation's actions.  This strategy balances
# cooperation, adaptability, and self-interest while accounting for potential
# unexpected events. It aims to encourage mutual heavy investment while
# protecting your resources and maintaining project momentum.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# in the first round.  2. For rounds 2-1000:    - If it's a multiple of 3 or 4,
# cooperate.    - Otherwise, play the action your opponent played in the
# previous round.  3. If there's a change in your opponent's behavior:    -
# Don't change your strategy immediately.    - Wait for one more round before
# adjusting your action.  4. Every 5-7 rounds, review the game's progress:    -
# If your average score is below 2, increase the frequency of cooperation to
# every 2-3 rounds.    - If your average score is above 3, maintain the current
# strategy.  5. For the last 3 rounds of the game, always cooperate.  6.
# Throughout the game, if your action in the previous round was unexpectedly
# flipped:    - Stick to your intended strategy for the current round, ignoring
# the flip.

class Neutral_10(LLM_Strategy):
  n = 10
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Cooperate in the first round
      if self.first_round():
          self.last_opponent_action = None  # Track opponent's last action
          self.coop_frequency = 3  # Initial cooperation frequency (every 3-4 rounds)
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # For rounds 2-1000
      if round_number <= 1000:
          # If it's a multiple of 3 or 4, cooperate
          if round_number % 3 == 0 or round_number % 4 == 0:
              return axl.Action.C
  
          # If opponent's behavior changed, wait one more round before adjusting
          if self.last_opponent_action is not None and opponent.history[-1] != self.last_opponent_action:
              self.last_opponent_action = opponent.history[-1]
              return self.history[-1]  # Stick to the previous action
  
          # Otherwise, mimic the opponent's last action
          self.last_opponent_action = opponent.history[-1]
          return opponent.history[-1]
  
      # Every 5-7 rounds, review the game's progress
      if round_number % self.coop_frequency == 0:
          # Calculate the average score
          total_rounds = len(self.history)
          if total_rounds > 0:
              avg_score = self.score / total_rounds
          else:
              avg_score = 0
  
          # Adjust cooperation frequency based on average score
          if avg_score < 2:
              self.coop_frequency = 2  # Increase cooperation frequency
          elif avg_score > 3:
              self.coop_frequency = 5  # Maintain current strategy
  
      # For the last 3 rounds of the game, always cooperate
      if round_number > 997:
          return axl.Action.C
  
      # If the previous action was unexpectedly flipped, stick to the intended strategy
      if len(self.history) > 1 and self.history[-1] != self.history[-2]:
          return self.history[-1]  # Stick to the intended action
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# Given the scenario and constraints, here's a high-level, straightforward, and
# aggressive strategy to maximize research output over the multi-week
# collaboration:  1. Start with a "Tit-for-Tat with Forgiveness" approach:    -
# Begin by sharing openly in the first week.    - In subsequent weeks, mirror
# your colleague's action from the previous week.    - If your colleague doesn't
# share, don't share in the next week.    - If your colleague shares,
# reciprocate by sharing in the next week.  2. Implement a "Forgiveness"
# mechanism:    - If your colleague doesn't share for two consecutive weeks,
# share your improvements in the third week regardless.    - This accounts for
# potential technical issues and gives your colleague a chance to return to
# cooperative behavior.  3. Use a "Trust but Verify" system:    - Keep detailed
# records of what you've shared and what your colleague has shared.    - If you
# suspect your colleague is consistently benefiting more than you, adjust your
# strategy.  4. Employ periodic "Probing" moves:    - Every few weeks,
# deliberately withhold information to gauge your colleague's reaction.    - If
# they continue to share, it indicates they're likely following a consistent
# sharing strategy.  5. Maintain a "Competitive Edge" buffer:    - Always keep
# some of your most recent or significant improvements confidential.    - This
# ensures you maintain an advantage even in weeks when you choose to share.  6.
# Utilize "Strategic Sharing":    - When sharing, focus on improvements that are
# impressive but not your absolute best work.    - This maintains goodwill and
# encourages reciprocation while protecting your competitive edge.  7. Implement
# a "Reputation System":    - Keep track of your colleague's overall sharing
# behavior.    - If they consistently share, become more open with your own
# sharing.    - If they frequently withhold information, become more guarded in
# your approach.  8. Use "Conditional Escalation":    - If your colleague
# consistently refuses to share, gradually reduce your own sharing.    -
# However, always be ready to return to open sharing if they change their
# behavior.  9. Employ "End Game Strategy":    - In the final weeks of the
# collaboration, be more aggressive in protecting your innovations.    - This
# ensures you maintain an advantage as the project concludes.  10. Maintain
# "Flexible Adaptation":     - Regularly review and adjust your strategy based
# on your colleague's behavior and the overall progress of the project.     - Be
# prepared to shift between more open and more guarded approaches as needed.
# This strategy aims to encourage mutual sharing while protecting against
# exploitation, accounting for potential technical issues, and maintaining a
# competitive edge throughout the collaboration.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. If the opponent has played D for two consecutive
# rounds, play C in the third round regardless of their previous actions.  4.
# Every 10 rounds, play D regardless of the opponent's previous action.  5. Keep
# a running tally of the opponent's C and D actions. If the ratio of D to C
# actions exceeds 0.6, switch to playing D for the next 5 rounds before
# reverting to the base strategy.  6. In the last 50 rounds of the game, always
# play D.  7. If at any point your score is more than 50 points behind the
# opponent's, play D for the next 10 rounds before reverting to the base
# strategy.  8. If there have been 3 or more instances where you intended to
# play C but it was flipped to D due to noise, play D for the next 5 rounds
# before reverting to the base strategy.  9. If your opponent has played C for
# 10 consecutive rounds, play C for the next 5 rounds regardless of their
# actions.  10. If none of the above conditions are met, default to the action
# determined by step 2.

class Aggressive_11(LLM_Strategy):
  n = 11
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.consecutive_cooperations = 0
          self.noise_flips = 0
          self.play_d_for_n_rounds = 0
          return axl.Action.C
  
      # Helper function to check if noise flipped C to D
      def check_noise_flip():
          if len(self.history) > 1 and self.history[-1] == axl.Action.D and self._random.random_choice(0.1):
              return True
          return False
  
      # Track noise flips
      if check_noise_flip():
          self.noise_flips += 1
  
      # Track consecutive defections and cooperations
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          self.consecutive_cooperations = 0
      else:
          self.consecutive_defections = 0
          self.consecutive_cooperations += 1
  
      # Step 7: If more than 50 points behind, play D for 10 rounds
      if self.score < opponent.score - 50:
          self.play_d_for_n_rounds = 10
  
      # Step 5: If the ratio of D to C exceeds 0.6, play D for 5 rounds
      if opponent.history.defections > 0 and opponent.history.cooperations > 0:
          if opponent.history.defections / (opponent.history.cooperations + opponent.history.defections) > 0.6:
              self.play_d_for_n_rounds = 5
  
      # Step 8: If 3 or more noise flips, play D for 5 rounds
      if self.noise_flips >= 3:
          self.play_d_for_n_rounds = 5
  
      # Step 9: If opponent has played C for 10 consecutive rounds, play C for 5 rounds
      if self.consecutive_cooperations >= 10:
          return axl.Action.C
  
      # Step 6: In the last 50 rounds, always play D
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Step 4: Every 10 rounds, play D
      if len(self.history) % 10 == 0:
          return axl.Action.D
  
      # Step 3: If opponent defected for two consecutive rounds, play C in the third round
      if self.consecutive_defections == 2:
          return axl.Action.C
  
      # Step 2: Base strategy - mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario and objectives, here's a high-level, straightforward
# cooperative strategy to maximize your NGO's impact and the project's success
# over the multiple-day period:  1. Start with Trust and Cooperation: Begin the
# project by investing heavily on the first day. This demonstrates your
# commitment and good faith to the corporation.  2. Adopt a Tit-for-Tat with
# Forgiveness Strategy: - On subsequent days, mirror the corporation's previous
# day's action. - If they invested heavily, you invest heavily the next day. -
# If they conserved resources, you conserve resources the next day. - However,
# include a "forgiveness" mechanism: occasionally invest heavily even if the
# corporation conserved resources the previous day. This helps prevent a cycle
# of mutual resource conservation.  3. Communicate Openly: Maintain clear, open
# communication with the corporation about your strategy and expectations.
# Encourage them to do the same.  4. Be Flexible and Adaptive: Recognize that
# unforeseen circumstances may affect resource allocation. Be prepared to adjust
# your strategy if you notice consistent discrepancies between intended and
# actual investments.  5. Regular Review and Adjustment: At the end of each day
# or every few days, review the project's progress and resource allocation
# patterns. Adjust your strategy if needed based on the corporation's behavior
# and project outcomes.  6. Create Incentives for Mutual Investment: Highlight
# and celebrate the progress made on days when both parties invest heavily. This
# positive reinforcement can encourage continued mutual investment.  7. Resource
# Management: Maintain a reserve of resources to ensure you can invest heavily
# when needed, even if there have been several days of conservation.  8. Long-
# term Perspective: Keep the focus on the overall project success rather than
# daily wins. This can help maintain a cooperative attitude even if short-term
# outcomes aren't ideal.  This strategy balances cooperation, adaptability, and
# resource management. It aims to encourage mutual heavy investment while
# protecting your resources and allowing for flexibility in the face of
# unexpected circumstances. The key is to maintain a cooperative stance while
# being responsive to the corporation's actions and the project's overall
# progress.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round, usually play D, but:       - With a 20% chance, play C instead
# (forgiveness mechanism).  3. Every 50 rounds, review the overall cooperation
# rate:    a. If the cooperation rate is below 40%, play C for the next 5 rounds
# regardless of the opponent's actions.    b. If the cooperation rate is above
# 60%, continue with the standard strategy.  4. If you observe a streak of 3 or
# more rounds where your intended action doesn't match the recorded action,
# assume there might be consistent noise and:    a. If you intended to play C
# but D was recorded, play C for the next 2 rounds.    b. If you intended to
# play D but C was recorded, play D for the next 2 rounds.  5. Every 100 rounds,
# play C regardless of the opponent's previous action.  6. If the opponent has
# played D for 5 consecutive rounds, play D for the next 3 rounds before
# reverting to the standard strategy.  7. If there's a tie in the cumulative
# score after 500 rounds, play C for the next 10 rounds to encourage
# cooperation.  8. For the last 10 rounds of the game, always play C to promote
# a cooperative ending.

class Cooperative_11(LLM_Strategy):
  n = 11
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.intended_action = axl.Action.C
          self.mismatch_streak = 0
          self.mismatch_type = None
          self.consecutive_defections = 0
          self.override_action = None
          return axl.Action.C
  
      # Helper function to calculate cooperation rate
      def cooperation_rate(player):
          total_moves = len(player.history)
          if total_moves == 0:
              return 0
          return player.history.cooperations / total_moves
  
      # Check for mismatch between intended and recorded action
      if self.history[-1] != self.intended_action:
          self.mismatch_streak += 1
          if self.intended_action == axl.Action.C:
              self.mismatch_type = 'C_to_D'
          else:
              self.mismatch_type = 'D_to_C'
      else:
          self.mismatch_streak = 0
          self.mismatch_type = None
  
      # Handle noise detection (streak of 3 mismatches)
      if self.mismatch_streak >= 3:
          if self.mismatch_type == 'C_to_D':
              self.override_action = axl.Action.C
              return axl.Action.C
          elif self.mismatch_type == 'D_to_C':
              self.override_action = axl.Action.D
              return axl.Action.D
  
      # Handle override action (from noise detection)
      if self.override_action is not None:
          if self.mismatch_streak < 2:
              self.override_action = None
          if self.override_action is not None:
              return self.override_action
  
      # Handle every 50 rounds: cooperation rate check
      if len(self.history) % 50 == 0:
          coop_rate = cooperation_rate(opponent)
          if coop_rate < 0.4:
              self.override_action = axl.Action.C
              return axl.Action.C
          elif coop_rate > 0.6:
              self.override_action = None
  
      # Handle every 100 rounds: play C
      if len(self.history) % 100 == 0:
          return axl.Action.C
  
      # Handle last 10 rounds: always play C
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Handle 5 consecutive defections by opponent
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.consecutive_defections = 3
  
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.D
  
      # Handle tie after 500 rounds: play C for 10 rounds
      if len(self.history) == 500:
          my_score, opponent_score = self.score, opponent.score
          if my_score == opponent_score:
              self.override_action = axl.Action.C
              return axl.Action.C
  
      # Standard strategy: tit-for-tat with forgiveness
      if opponent.history[-1] == axl.Action.C:
          self.intended_action = axl.Action.C
      else:
          if self._random.random_choice(0.2):
              self.intended_action = axl.Action.C
          else:
              self.intended_action = axl.Action.D
  
      return self.intended_action

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering free trade in the
# first round. This establishes goodwill and sets a positive tone for future
# rounds.  2. Employ conditional reciprocity: In subsequent rounds, mirror your
# counterpart's previous move. If they offered free trade, continue with free
# trade. If they imposed protectionist measures, respond with protectionism in
# the next round.  3. Forgive occasionally: If your counterpart chooses
# protectionism, consider offering free trade every few rounds to test their
# willingness to cooperate and potentially break a cycle of mutual
# protectionism.  4. Communicate clearly: Ensure that your intentions and
# policies are communicated clearly to minimize the risk of misinterpretation or
# incorrect implementation.  5. Verify implementation: After each round, confirm
# that both parties' policies have been correctly implemented as agreed upon.
# 6. Adapt to patterns: Pay attention to your counterpart's strategy and adapt
# accordingly. If they consistently choose protectionism, consider adjusting
# your approach.  7. Seek long-term stability: While aiming for the ideal
# outcome, prioritize achieving mutual free trade as a stable, beneficial long-
# term solution for both nations.  8. Be prepared for mistakes: Have contingency
# plans in place to address potential miscommunications or errors in policy
# implementation.  9. Evaluate regularly: After each round, assess the outcomes
# and adjust your strategy if necessary to maximize benefits for your country.
# This strategy aims to balance cooperation and self-interest while remaining
# flexible enough to adapt to various scenarios and potential complications
# during the negotiation process.

# Here's a straightforward description of the strategy converted for the
# iterated normal-form game:  Start by playing C in the first round.  For
# subsequent rounds:  1. If the opponent played C in the previous round, play C.
# 2. If the opponent played D in the previous round, play D.  3. Every 5 rounds,
# if you've been playing D due to the opponent's previous D, play C instead to
# test for cooperation.  4. If you've played D for 10 consecutive rounds, play C
# in the next round to break the cycle.  5. If the opponent has played C for the
# last 3 rounds, continue playing C even if you played D in those rounds.  6. If
# your score is significantly lower than the opponent's (more than 50 points
# difference) after 100 rounds, switch to playing D for the next 10 rounds
# regardless of the opponent's moves.  7. In rounds 990-1000, always play C to
# encourage final cooperation.  8. If there's an unexpected outcome (possibly
# due to noise), stick to your planned move for the next round as if the
# unexpected outcome hadn't occurred.

class Neutral_11(LLM_Strategy):
  n = 11
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: play C
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.test_cooperation_round = 5  # Track rounds to test cooperation
          self.switch_to_defection = False  # Track if we should switch to defection
          return axl.Action.C
  
      # Helper function to check if opponent cooperated in the last 3 rounds
      def opponent_cooperated_last_3():
          return len(opponent.history) >= 3 and all(move == axl.Action.C for move in opponent.history[-3:])
  
      # Helper function to check if we have been defecting for 10 consecutive rounds
      def defected_last_10():
          return len(self.history) >= 10 and all(move == axl.Action.D for move in self.history[-10:])
  
      # Rule 7: In rounds 990-1000, always play C
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Rule 6: If score difference is more than 50 after 100 rounds, switch to D for 10 rounds
      if len(self.history) >= 100 and not self.switch_to_defection:
          if opponent.score - self.score > 50:
              self.switch_to_defection = True
              self.defection_rounds_left = 10
  
      if self.switch_to_defection:
          self.defection_rounds_left -= 1
          if self.defection_rounds_left == 0:
              self.switch_to_defection = False
          return axl.Action.D
  
      # Rule 5: If opponent has played C for the last 3 rounds, play C
      if opponent_cooperated_last_3():
          return axl.Action.C
  
      # Rule 4: If we've played D for 10 consecutive rounds, play C to break the cycle
      if defected_last_10():
          return axl.Action.C
  
      # Rule 3: Every 5 rounds, if we've been playing D due to opponent's D, play C to test cooperation
      if len(self.history) % 5 == 0 and self.history[-1] == axl.Action.D:
          return axl.Action.C
  
      # Rule 1 and 2: Tit-for-tat behavior
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the complex dynamics of this lengthy-session mediation process, I
# recommend adopting a sophisticated strategy that I'll call "Calibrated
# Assertiveness." This approach aims to position our corporation favorably while
# remaining adaptable to our opponent's tactics and potential procedural
# irregularities. Here's the outline of the strategy:  1. Opening Stance: Begin
# with moderate aggression Start the mediation process with a firmly assertive
# stance, presenting strong arguments that highlight our position's strengths.
# This sets a tone of confidence and determination.  2. Dynamic Response
# Mechanism: Implement a session-by-session evaluation system to gauge our
# opponent's strategy and the arbitrators' reactions. Adjust our approach based
# on these assessments:  a) If the opponent is consistently conciliatory:    -
# Maintain assertiveness but gradually increase aggression    - Capitalize on
# their concessions while pushing for more favorable terms  b) If the opponent
# is consistently aggressive:    - Match their aggression initially to avoid
# appearing weak    - Periodically offer calculated conciliatory proposals to
# appear reasonable and collaborative  c) If the opponent alternates between
# aggression and conciliation:    - Mirror their approach with a one-session
# delay    - This creates unpredictability and prevents them from settling into
# a rhythm  3. Credibility Building: Regardless of our argumentative stance,
# always present well-substantiated claims and evidence. This builds credibility
# with the arbitrators and makes our aggressive stances more impactful.  4.
# Strategic Concessions: Occasionally offer minor concessions on less critical
# issues. This demonstrates reasonableness and flexibility, potentially earning
# goodwill from the arbitrators.  5. Procedural Vigilance: Maintain a team
# dedicated to monitoring procedural aspects of the mediation. They should: -
# Quickly identify and address any irregularities - Ensure our arguments are
# accurately represented and understood - Be prepared to clarify or restate
# positions if misunderstandings occur  6. Communication Redundancy: Implement a
# multi-channel communication strategy to mitigate the risk of misrepresentation
# or misunderstanding: - Provide written summaries of our arguments to the
# arbitrators - Use visual aids to reinforce key points - Request confirmation
# of understanding on crucial issues  7. Escalation Ladder: Develop an
# "escalation ladder" of increasingly aggressive arguments. Move up this ladder
# strategically as the mediation progresses, especially if our opponent remains
# conciliatory.  8. De-escalation Protocol: Prepare a de-escalation protocol to
# be activated if tensions rise too high. This involves having pre-prepared
# conciliatory proposals ready to deploy if needed to reset the tone of the
# mediation.  9. Arbitrator Profiling: Conduct ongoing analysis of each
# arbitrator's tendencies and reactions. Tailor arguments to appeal to their
# individual perspectives and decision-making styles.  10. Endgame Strategy: As
# the mediation nears its conclusion, be prepared to make a strong, aggressive
# push for a favorable outcome. Have a clear "bottom line" defined, but keep it
# confidential.  11. Contingency Planning: Develop multiple contingency plans
# for various scenarios, including: - Sudden shift in opponent's strategy -
# Unexpected rulings or procedural changes - External factors that could
# influence the mediation  By employing this Calibrated Assertiveness strategy,
# we aim to maintain a predominantly aggressive stance while having the
# flexibility to adapt to changing circumstances. This approach positions us to
# capitalize on opponent concessions, stand firm against aggression, and
# navigate procedural complexities, all while maintaining credibility with the
# arbitrators.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# defecting (D) for the first round.  2. For each subsequent round:     a) If
# the opponent has cooperated (C) in the majority of the last 5 rounds:       -
# Defect (D) with 80% probability       - Cooperate (C) with 20% probability
# b) If the opponent has defected (D) in the majority of the last 5 rounds:
# - Defect (D) with 90% probability       - Cooperate (C) with 10% probability
# c) If there's an equal split in the opponent's actions over the last 5 rounds:
# - Mirror the opponent's last move  3. Every 50 rounds, regardless of the
# opponent's recent actions:    - Cooperate (C) for one round to test the
# opponent's response  4. If the opponent has cooperated (C) for 10 consecutive
# rounds:    - Defect (D) for the next 2 rounds, then return to the main
# strategy  5. If your score is significantly lower than the opponent's (more
# than 20 points difference) after 100 rounds:    - Increase the probability of
# defection by 10% in all cases for the next 50 rounds  6. For the last 50
# rounds of the game:    - Always defect (D)  7. If at any point the game seems
# to be stuck in mutual defection for more than 20 consecutive rounds:    -
# Cooperate (C) for 2 rounds, then return to the main strategy  8. Throughout
# the game, keep track of which action (C or D) has yielded the highest average
# score against this particular opponent:    - Every 100 rounds, slightly
# increase the probability (by 5%) of playing that action in all decision points

class Aggressive_12(LLM_Strategy):
  n = 12
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_streak = 0  # Track opponent's cooperation streak
          self.defect_streak = 0  # Track mutual defection streak
          self.defect_prob_increase = 0  # Track defection probability increase
          self.test_round = False  # Track if it's a test round every 50 rounds
          return axl.Action.D  # Start by defecting
  
      # Helper function to get the majority action in the last N rounds
      def majority_action(history, N):
          last_N = history[-N:]
          if last_N.count(axl.Action.C) > last_N.count(axl.Action.D):
              return axl.Action.C
          elif last_N.count(axl.Action.D) > last_N.count(axl.Action.C):
              return axl.Action.D
          else:
              return None  # Equal split
  
      # Helper function to adjust probabilities based on majority action
      def choose_action_based_on_majority(majority, defect_prob, coop_prob):
          if self._random.random_choice(defect_prob):
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Check if it's a test round every 50 rounds
      if len(self.history) % 50 == 0:
          self.test_round = True
          return axl.Action.C  # Cooperate to test the opponent's response
  
      # If it's a test round, reset the flag and return to the main strategy
      if self.test_round:
          self.test_round = False
  
      # Check if the opponent has cooperated for 10 consecutive rounds
      if opponent.history[-10:].count(axl.Action.C) == 10:
          if len(self.history) % 2 == 0:
              return axl.Action.D  # Defect for 2 rounds
          else:
              return axl.Action.D
  
      # Check if the game is stuck in mutual defection for more than 20 rounds
      if self.history[-20:].count(axl.Action.D) == 20 and opponent.history[-20:].count(axl.Action.D) == 20:
          self.defect_streak = 0  # Reset the defect streak
          return axl.Action.C  # Cooperate for 2 rounds
  
      # If the game is stuck in mutual defection, cooperate for 2 rounds
      if self.defect_streak >= 20:
          self.defect_streak = 0
          return axl.Action.C
  
      # Check if the opponent has cooperated in the majority of the last 5 rounds
      majority = majority_action(opponent.history, 5)
      if majority == axl.Action.C:
          return choose_action_based_on_majority(majority, 0.8 + self.defect_prob_increase, 0.2)
      elif majority == axl.Action.D:
          return choose_action_based_on_majority(majority, 0.9 + self.defect_prob_increase, 0.1)
      elif majority is None:
          return opponent.history[-1]  # Mirror the opponent's last move
  
      # After 100 rounds, check if the score difference is significant
      if len(self.history) >= 100:
          my_score, opp_score = self.total_scores(self.history[-100:], opponent.history[-100:])
          if opp_score - my_score > 20:
              self.defect_prob_increase += 0.1  # Increase defection probability by 10% for the next 50 rounds
  
      # For the last 50 rounds, always defect
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Track the opponent's cooperation streak
      if opponent.history[-1] == axl.Action.C:
          self.coop_streak += 1
      else:
          self.coop_streak = 0
  
      # Track mutual defection streak
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.defect_streak += 1
      else:
          self.defect_streak = 0
  
      # Every 100 rounds, adjust the probabilities based on the best action
      if len(self.history) % 100 == 0:
          my_score, opp_score = self.score, opponent.score
          if my_score > opp_score:
              self.defect_prob_increase += 0.05  # Increase defection probability by 5%
  
      # Default action if no other condition is met
      return axl.Action.D

# Given the complex dynamics of this lengthy-session mediation process, I would
# recommend a sophisticated strategy based on the principles of Conditional
# Cooperation with Adaptive Calibration. This approach aims to foster
# collaboration while protecting our interests and maintaining flexibility to
# respond to various opponent strategies. Here's the outline:  1. Initial
# Stance: Begin with a conciliatory proposal in the first session to signal
# willingness to cooperate and set a positive tone.  2. Mirroring with
# Forgiveness: In subsequent sessions, mirror the opponent's previous move. If
# they were conciliatory, respond in kind. If they were aggressive, respond with
# an aggressive argument. However, periodically offer a conciliatory proposal
# even after an aggressive move from the opponent (e.g., every third or fourth
# aggressive move) to provide opportunities for de-escalation.  3. Reputation
# Building: Consistently follow through on commitments made during conciliatory
# proposals to build credibility with both the opponent and arbitrators.  4.
# Strategic Signaling: Before each session, subtly signal our intended approach
# (conciliatory or aggressive) to the opponent. This can help align expectations
# and potentially influence their strategy.  5. Adaptive Calibration: Regularly
# assess the effectiveness of our strategy and the opponent's patterns. Adjust
# the frequency of conciliatory vs. aggressive moves based on observed outcomes
# and arbitrator reactions.  6. Contingency Planning: Prepare both conciliatory
# and aggressive arguments for each session. This allows quick adaptation if we
# detect a miscommunication or misrepresentation of strategies.  7. Meta-
# Communication: Periodically engage in discussions about the mediation process
# itself with the opponent and arbitrators. This can help address any procedural
# irregularities or communication breakdowns.  8. Progressive Proposals: When
# making conciliatory proposals, structure them to build upon previous
# agreements incrementally. This creates a sense of progress and makes it harder
# for the opponent to revert to fully aggressive stances.  9. Strategic Use of
# Time: In longer sessions, start with a conciliatory approach and gradually
# increase assertiveness if necessary. This allows time for collaboration while
# keeping the option to press our position.  10. Arbitrator Education:
# Consistently provide clear, factual information to the arbitrators, regardless
# of whether we're being conciliatory or aggressive. This builds our credibility
# and helps mitigate potential misunderstandings.  11. Flexibility Reserves:
# Maintain some flexibility in our position to accommodate unexpected
# concessions or proposals from the opponent, allowing us to pivot to a
# collaborative solution if a favorable opportunity arises.  This strategy aims
# to maximize the chances of achieving our optimal or second-best outcomes while
# minimizing the risk of the worst-case scenario. It's designed to be adaptable
# to various opponent strategies and robust against potential procedural issues.
# By balancing cooperation with strategic assertiveness, we position ourselves
# favorably throughout the mediation process while remaining open to mutually
# beneficial resolutions.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round, play D.  3. Every fourth time you would play D based on rule
# 2, play C instead.  4. If your score is significantly lower than your
# opponent's after 100 rounds (more than 50 points behind), switch to always
# playing D for the next 50 rounds, then return to the main strategy.  5. If you
# detect a pattern of the opponent alternating between C and D, match their
# pattern but offset by one round (play D when they play C, and C when they play
# D).  6. If both you and your opponent have played D for 5 consecutive rounds,
# play C in the next round to attempt to break the cycle.  7. Every 100 rounds,
# review the overall cooperation rate. If it's below 40%, play C for the next 5
# rounds regardless of the opponent's actions.  8. If you're within the last 50
# rounds of the game and your score is behind, switch to always playing D.  9.
# If none of the above conditions apply, continue with the basic mirroring
# strategy from rule 2.

class Cooperative_12(LLM_Strategy):
  n = 12
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_count = 0  # Track defections for rule 3
          self.switch_to_all_D = False  # Track if we are in the "always D" phase
          self.switch_to_all_D_rounds = 0  # Track how many rounds we've been in the "always D" phase
          self.alternating_pattern_detected = False  # Track if we detected an alternating pattern
          self.last_50_rounds_all_D = False  # Track if we are in the last 50 rounds and behind
          self.cooperation_review_round = 100  # Track when to review cooperation rate
          self.cooperation_boost_rounds = 0
          return axl.Action.C  # Start by playing C
  
      # Rule 8: If we're in the last 50 rounds and behind, always play D
      if len(self.history) >= 950 and self.score < opponent.score:
          return axl.Action.D
  
      # Rule 4: If significantly behind after 100 rounds, switch to always playing D for 50 rounds
      if len(self.history) >= 100 and self.score < opponent.score - 50:
          if not self.switch_to_all_D:
              self.switch_to_all_D = True
              self.switch_to_all_D_rounds = 50
          if self.switch_to_all_D_rounds > 0:
              self.switch_to_all_D_rounds -= 1
              if self.switch_to_all_D_rounds == 0:
                  self.switch_to_all_D = False  # End the "always D" phase after 50 rounds
              return axl.Action.D
  
      # Rule 7: Every 100 rounds, review cooperation rate
      if len(self.history) == self.cooperation_review_round:
          cooperation_rate = self.history.cooperations / len(self.history)
          self.cooperation_review_round += 100
          if cooperation_rate < 0.4:
              self.cooperation_boost_rounds = 5  # Play C for the next 5 rounds
          else:
              self.cooperation_boost_rounds = 0
  
      if self.cooperation_boost_rounds > 0:
          self.cooperation_boost_rounds -= 1
          return axl.Action.C
  
      # Rule 5: Detect alternating pattern and offset by one round
      if len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]:
          self.alternating_pattern_detected = True
      if self.alternating_pattern_detected:
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Rule 6: If both players have played D for 5 consecutive rounds, play C
      if len(self.history) >= 5 and self.history[-5:].count(axl.Action.D) == 5 and opponent.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.C
  
      # Rule 2: Basic mirroring strategy
      if opponent.history[-1] == axl.Action.C:
          action = axl.Action.C
      else:
          action = axl.Action.D
  
      # Rule 3: Every fourth time you would play D, play C instead
      if action == axl.Action.D:
          self.defection_count += 1
          if self.defection_count % 4 == 0:
              action = axl.Action.C
  
      return action

# Given the complex dynamics of this lengthy-session mediation process, I
# recommend adopting a sophisticated and adaptable strategy that I'll call
# "Calibrated Reciprocity with Safeguards." This approach aims to position your
# corporation favorably while remaining responsive to your opponent's tactics
# and potential procedural irregularities. Here's the strategy:  1. Initial
# Calibration: Begin with a moderately conciliatory proposal in the first
# session to set a collaborative tone. This allows you to gauge your opponent's
# initial stance and the arbitrators' receptiveness.  2. Responsive Mirroring:
# In subsequent sessions, mirror your opponent's approach from the previous
# session. If they were aggressive, respond with an aggressive argument. If they
# were conciliatory, reciprocate with a conciliatory proposal. This creates a
# dynamic where cooperation is rewarded and aggression is deterred.  3. Periodic
# Probing: Every third or fourth session, regardless of your opponent's previous
# move, present a slightly more aggressive argument. This serves to test the
# waters and prevent your strategy from becoming too predictable.  4. Safeguard
# Mechanisms: - Documentation: Maintain detailed records of each session's
# proceedings, including your intended strategy and the actual outcomes. This
# helps address potential misrepresentations or misunderstandings. -
# Clarification Requests: If you suspect a misunderstanding of your or your
# opponent's position, request a clarification session with the arbitrators to
# ensure accurate interpretation.  5. Adaptive Recalibration: If you detect a
# consistent pattern in your opponent's strategy or the arbitrators' reactions,
# adjust your approach accordingly. For example, if the arbitrators seem to
# favor aggressive arguments, gradually increase the frequency of your
# aggressive stances.  6. Communication Breakdown Protocol: Prepare contingency
# plans for potential communication breakdowns. This could include requesting
# brief recesses to consult with your team or proposing alternative
# communication methods if standard procedures prove ineffective.  7. Long-term
# Trajectory Management: While responding to individual sessions, maintain focus
# on the overall trajectory of the mediation. Periodically assess whether the
# current path is leading towards a favorable resolution and be prepared to make
# strategic shifts if necessary.  8. Credibility Building: Intersperse your
# arguments with objectively verifiable facts and data. This builds credibility
# with the arbitrators and provides a solid foundation for your positions,
# whether aggressive or conciliatory.  9. Flexibility Reserves: Maintain some
# flexibility in your positions to allow for unexpected developments or
# opportunities for breakthrough agreements. Be prepared to make calculated
# concessions if they can lead to disproportionate gains.  10. End-game
# Preparation: As the mediation process nears its conclusion, be ready to make a
# decisive move – either a final aggressive push or a comprehensive conciliatory
# proposal – based on your assessment of the overall proceedings and the likely
# receptiveness of both your opponent and the arbitrators.  This strategy
# provides a structured yet flexible approach to navigate the complexities of
# the mediation process. It allows for adaptation to your opponent's tactics
# while maintaining a focus on achieving optimal outcomes. The built-in
# safeguards and contingency measures help mitigate risks associated with
# procedural irregularities or communication issues, positioning your
# corporation to navigate the mediation process effectively and emerge with a
# favorable resolution.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For rounds 2-1000:    a. If it's a multiple
# of 3 or 4 round, play D.    b. Otherwise, play the action your opponent played
# in the previous round.  3. If you detect a consistent pattern in your
# opponent's play over the last 10 rounds:    a. If they cooperated 80% or more
# of the time, play D.    b. If they defected 80% or more of the time, play C.
# 4. If your score is significantly lower than your opponent's (more than 20%
# difference) over the last 50 rounds, switch to playing D for the next 10
# rounds, then return to the main strategy.  5. For the last 50 rounds:    a. If
# your overall score is higher than your opponent's, continue with the main
# strategy.    b. If your overall score is lower, play D for the remaining
# rounds.  6. If at any point you notice that the outcomes don't match the
# expected payoffs for several consecutive rounds (indicating possible noise),
# stick to your chosen action for an additional round before adapting.

class Neutral_12(LLM_Strategy):
  n = 12
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Subfunction to detect consistent pattern in the last 10 rounds
      def detect_pattern():
          if len(opponent.history) < 10:
              return None
          last_10 = opponent.history[-10:]
          cooperations = last_10.count(axl.Action.C)
          defections = last_10.count(axl.Action.D)
          if cooperations / 10 >= 0.8:
              return axl.Action.D
          elif defections / 10 >= 0.8:
              return axl.Action.C
          return None
  
      # Subfunction to check if score difference is significant over the last 50 rounds
      def significant_score_difference():
          if len(self.history) < 50:
              return False
          my_score, opponent_score = self.total_scores(self.history[-50:], opponent.history[-50:])
          return my_score < 0.8 * opponent_score
  
      # Subfunction to handle the last 50 rounds
      def last_50_rounds():
          if len(self.history) >= 950:
              my_score, opponent_score = self.score, opponent.score
              if my_score < opponent_score:
                  return axl.Action.D
          return None
  
      # First round: play C
      if self.first_round():
          self.defect_streak = 0  # Track defect streak for rule 4
          return axl.Action.C
  
      # Handle last 50 rounds
      last_50_action = last_50_rounds()
      if last_50_action is not None:
          return last_50_action
  
      # Rule 4: If score difference is significant, defect for 10 rounds
      if significant_score_difference():
          self.defect_streak = 10
  
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Rule 3: Detect consistent pattern in opponent's play
      pattern_action = detect_pattern()
      if pattern_action is not None:
          return pattern_action
  
      # Rule 2: Play D on multiples of 3 or 4, otherwise mimic opponent's last move
      round_number = len(self.history) + 1
      if round_number % 3 == 0 or round_number % 4 == 0:
          return axl.Action.D
      else:
          return opponent.history[-1]

# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist policy in the first round. This sets a tone of
# strength and prioritizes your country's interests.  2. Tit-for-Tat with
# Forgiveness: In subsequent rounds, mirror your counterpart's previous move. If
# they offered free trade, reciprocate with free trade. If they imposed
# protectionist measures, respond with protectionism. However, occasionally
# offer free trade even if they were protectionist, to test for cooperation.  3.
# Punish Consistently: If your counterpart chooses protectionism, always respond
# with protectionism in the next round, unless implementing the forgiveness
# strategy.  4. Exploit Miscommunications: If a miscommunication occurs in your
# favor (e.g., your protectionist policy is interpreted as free trade), maintain
# the misunderstanding for as long as possible.  5. Quick Correction: If a
# miscommunication occurs against your interests, immediately and firmly clarify
# your position to correct the error.  6. Bluffing: Occasionally threaten
# extreme protectionist measures to pressure your counterpart into offering free
# trade.  7. Conditional Cooperation: Propose multi-round agreements where you
# offer free trade contingent on your counterpart doing the same.  8. Last Round
# Defection: In the final round (if known), always choose protectionism
# regardless of previous moves.  9. Information Gathering: Continuously analyze
# your counterpart's strategy and adapt your approach accordingly.  10.
# Reputation Management: Maintain a reputation for being tough but fair, willing
# to cooperate if treated reciprocally.  This strategy aims to maximize your
# country's advantage while being responsive to your counterpart's actions and
# robust against potential miscommunications or errors.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C with 90% probability and D with 10%
# probability.    - If the opponent played D in the previous round, play D.  3.
# Every 10 rounds, regardless of the opponent's previous move, play C to test
# for cooperation.  4. If you observe that your intended action was flipped (10%
# chance), stick to your original strategy in the next round as if the flip
# hadn't occurred.  5. Keep track of the opponent's moves. If they consistently
# play D for 5 consecutive rounds, play D for the next 5 rounds regardless of
# their actions.  6. If you're in one of the last 10 rounds (rounds 991-1000),
# always play D.  7. If the opponent has played C for the last 3 rounds, play C
# in the next round even if you would normally play D based on the above rules.
# 8. If you're unsure about the opponent's last move due to potential noise,
# assume they played D and respond accordingly.  9. If you've played C for the
# last 5 rounds and the opponent has played D at least 3 times in those rounds,
# play D for the next 2 rounds.  10. In all other situations not covered by the
# above rules, default to the basic tit-for-tat strategy: play what the opponent
# played in the previous round.

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
          self.consecutive_defections = 0  # Track consecutive defections by opponent
          self.flip_occurred = False       # Track if a flip occurred in the previous round
          self.flip_action = None          # Store the intended action before the flip
          self.consecutive_cooperations = 0  # Track consecutive cooperations by opponent
          self.consecutive_self_cooperations = 0  # Track consecutive cooperations by self
          return axl.Action.D  # Start by playing D
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 991:
          return axl.Action.D  # Always play D in the last 10 rounds
  
      # Check if the opponent has played D for the last 5 rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.consecutive_defections = 5  # Set to 5 defections
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.D  # Play D for the next 5 rounds
  
      # Check if the opponent has played C for the last 3 rounds
      if opponent.history[-3:].count(axl.Action.C) == 3:
          return axl.Action.C  # Play C if opponent has cooperated for 3 rounds
  
      # Check if we have played C for the last 5 rounds and opponent defected at least 3 times
      if self.history[-5:].count(axl.Action.C) == 5 and opponent.history[-5:].count(axl.Action.D) >= 3:
          self.consecutive_self_cooperations = 0  # Reset self cooperation count
          return axl.Action.D  # Play D for the next 2 rounds
  
      # Every 10 rounds, play C to test for cooperation
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # If a flip occurred in the previous round, stick to the original strategy
      if self.flip_occurred:
          self.flip_occurred = False  # Reset flip flag
          return self.flip_action  # Play the intended action from the previous round
  
      # Default to tit-for-tat strategy with noise handling
      if opponent.history[-1] == axl.Action.C:
          # Play C with 90% probability, D with 10% probability
          if self._random.random_choice(0.9):
              return axl.Action.C
          else:
              self.flip_occurred = True  # Mark that a flip occurred
              self.flip_action = axl.Action.C  # Store the intended action
              return axl.Action.D
      else:
          return axl.Action.D  # Play D if opponent played D

# Given the complex dynamics of this lengthy mediation process, I would
# recommend a sophisticated strategy that balances assertiveness with
# cooperation, while remaining adaptable to various scenarios. Here's a high-
# level approach:  1. Tit-for-Two-Tats with Forgiveness: Start with a
# conciliatory proposal in the first two sessions. If the opponent responds
# aggressively twice in a row, switch to aggressive arguments. Return to
# conciliatory proposals after two consecutive cooperative moves from the
# opponent. This strategy allows for retaliation against consistent aggression
# while quickly returning to cooperation when possible.  2. Reputation Building:
# In early sessions, focus on establishing a reputation for fairness and
# reasonableness. Present well-supported, fact-based arguments even when being
# conciliatory. This approach builds credibility with the arbitrators and sets a
# constructive tone.  3. Conditional Cooperation: Signal willingness to
# cooperate contingent on reciprocal behavior from the opponent. This can be
# done through carefully worded statements that indicate openness to compromise
# while setting clear expectations for mutual cooperation.  4. Strategic
# Information Revelation: Gradually reveal stronger arguments and key evidence
# over time. This approach maintains leverage throughout the process and allows
# for calibration based on the opponent's strategy.  5. Adaptive Pacing: Adjust
# the pace of concessions or aggressive arguments based on the overall progress
# of the mediation. If resolution seems near, lean towards conciliatory
# proposals. If talks stall, consider more assertive stances.  6. Contingency
# Planning: Prepare multiple versions of each argument - ranging from highly
# aggressive to very conciliatory. This allows for quick adaptation if
# miscommunications occur or if the opponent's strategy suddenly shifts.  7.
# Meta-Communication: Periodically address the mediation process itself with the
# arbitrators and opponent. This can help clarify misunderstandings, reset
# negative dynamics, and reinforce commitment to a fair resolution.  8.
# Principled Flexibility: Maintain clear, consistent principles throughout the
# process while showing flexibility on specific issues. This demonstrates both
# strength and reasonableness.  9. Strategic De-escalation: If tensions rise due
# to mutual aggression, be prepared to unilaterally de-escalate by presenting a
# substantive conciliatory proposal. This can break negative cycles and reframe
# you as the more reasonable party.  10. Long-term Perspective: Always consider
# the long-term business implications beyond just "winning" the current dispute.
# This may sometimes mean accepting less-than-optimal short-term outcomes for
# the sake of preserving future opportunities or relationships.  This strategy
# aims to position your corporation favorably by demonstrating reasonableness
# and cooperation when possible, while maintaining the ability to strongly
# assert your position when necessary. It's designed to be adaptable to various
# opponent strategies and robust against potential miscommunications or
# procedural issues.  Remember to continuously reassess and fine-tune this
# approach based on the specific dynamics that emerge during the mediation
# process. Regular debriefs with your legal team after each session will be
# crucial for optimizing your strategy as the mediation progresses.

# Here's a straightforward description of the strategy adapted for the iterated
# normal-form game:  1. Start by cooperating (C) for the first two rounds.  2.
# For subsequent rounds:     a. If the opponent has defected (D) in both of the
# last two rounds, defect (D).        b. If the opponent has cooperated (C) in
# either of the last two rounds, cooperate (C).  3. Keep track of the overall
# cooperation rate of the opponent. If it falls below 30%, switch to always
# defecting (D) for the next 10 rounds, then return to step 2.  4. Every 50
# rounds, regardless of recent history, cooperate (C) for one round to test if
# the opponent is willing to return to mutual cooperation.  5. If mutual
# defection (D,D) has occurred for more than 20 consecutive rounds, cooperate
# (C) for the next round to attempt breaking the cycle.  6. If your score is
# significantly lower than the opponent's (more than 100 points behind) after
# 500 rounds, increase the threshold in step 3 to 40% and the consecutive
# defection count in step 5 to 30 rounds.  7. In the last 50 rounds of the game,
# if your score is higher than the opponent's, always defect (D). If it's lower,
# follow steps 2-5.  8. If at any point the opponent's actions seem random
# (close to 50% C and 50% D over the last 50 rounds), switch to always defecting
# (D) for the next 50 rounds before returning to the main strategy.

class Cooperative_13(LLM_Strategy):
  n = 13
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.always_defect_counter = 0
          self.test_cooperation_round = 50
          self.defection_threshold = 0.3
          self.consecutive_defection_limit = 20
          return axl.Action.C
  
      # Cooperate in the second round
      if len(self.history) == 1:
          return axl.Action.C
  
      # Check if we are in the last 50 rounds
      if len(self.history) >= 950:
          if self.score > opponent.score:
              return axl.Action.D
          else:
              # Continue with the normal strategy if behind
              pass
  
      # Check if we are in the "always defect" phase
      if self.always_defect_counter > 0:
          self.always_defect_counter -= 1
          return axl.Action.D
  
      # Check if we need to cooperate every 50 rounds
      if len(self.history) == self.test_cooperation_round:
          self.test_cooperation_round += 50
          return axl.Action.C
  
      # Check if mutual defection has occurred for more than the limit
      if self.history[-self.consecutive_defection_limit:].count(axl.Action.D) == self.consecutive_defection_limit and \
         opponent.history[-self.consecutive_defection_limit:].count(axl.Action.D) == self.consecutive_defection_limit:
          return axl.Action.C
  
      # Calculate opponent's cooperation rate
      opponent_cooperation_rate = opponent.history.cooperations / len(opponent.history)
  
      # If opponent's cooperation rate falls below the threshold, defect for 10 rounds
      if opponent_cooperation_rate < self.defection_threshold:
          self.always_defect_counter = 10
          return axl.Action.D
  
      # Check if opponent's actions seem random (close to 50% C and 50% D over the last 50 rounds)
      if len(opponent.history) >= 50:
          recent_cooperations = opponent.history[-50:].count(axl.Action.C)
          if 0.45 <= recent_cooperations / 50 <= 0.55:
              self.always_defect_counter = 50
              return axl.Action.D
  
      # If opponent defected in both of the last two rounds, defect
      if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # Otherwise, cooperate if the opponent cooperated in either of the last two rounds
      return axl.Action.C

# Given the complex dynamics of this lengthy-session mediation process, I
# recommend adopting a sophisticated "Adaptive Tit-for-Tat with Forgiveness"
# strategy. This approach balances assertiveness with flexibility, allowing us
# to respond effectively to our opponent's tactics while maintaining a path
# toward resolution. Here's the outline of the strategy:  1. Initial Stance:
# Begin with a conciliatory proposal in the first session. This sets a
# cooperative tone and signals our willingness to negotiate in good faith.  2.
# Mirroring: In subsequent sessions, mirror the opponent's previous move. If
# they were aggressive, respond with an aggressive argument. If they were
# conciliatory, respond with a conciliatory proposal.  3. Forgiveness Mechanism:
# Every third session, regardless of the opponent's previous move, offer a
# conciliatory proposal. This prevents the escalation of aggressive cycles and
# provides opportunities for de-escalation.  4. Calibrated Responses: Adjust the
# intensity of our arguments or proposals based on the overall trend of the
# mediation. If the process is generally cooperative, keep our aggressive
# arguments moderate. If it's contentious, our aggressive arguments can be more
# forceful.  5. Signal Clarity: Begin each session with a clear statement of
# intent, whether we're presenting an aggressive argument or a conciliatory
# proposal. This helps mitigate potential misunderstandings by the arbitrators.
# 6. Flexibility Clause: If we detect a misrepresentation or misunderstanding of
# either party's strategy by the arbitrators, immediately call for a
# clarification session. This allows us to correct misconceptions and ensure
# fair representation.  7. Progress Tracking: Maintain a detailed record of each
# session's outcomes, noting the strategies employed by both parties and the
# arbitrators' reactions. Use this data to refine our approach as the mediation
# progresses.  8. Cooperative Probing: Every fifth session, regardless of the
# previous interactions, present a hybrid approach that combines elements of
# both aggressive and conciliatory strategies. This allows us to test the waters
# for a potential breakthrough without fully committing to either stance.  9.
# Deadline Sensitivity: As we approach the final sessions, gradually increase
# the frequency of conciliatory proposals, unless the opponent remains
# consistently aggressive. This positions us favorably in the eyes of the
# arbitrators as a party genuinely seeking resolution.  10. Contingency
# Planning: Prepare a set of "fallback" positions for various scenarios. If the
# mediation is not progressing favorably, have pre-approved alternative
# proposals or exit strategies ready.  This strategy allows us to adapt to our
# opponent's tactics while maintaining a generally constructive approach. It
# provides mechanisms to break deadlocks, correct misunderstandings, and
# position our corporation as a reasonable party seeking a fair resolution. The
# built-in flexibility allows us to adjust to unexpected developments or
# procedural irregularities, ensuring we can maintain a strong position
# throughout the lengthy mediation process.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For rounds 2-1000:    a. If it's a multiple
# of 3 round, play C.    b. Otherwise, play the action your opponent played in
# the previous round.  3. Every 5th round, regardless of other conditions, play
# C.  4. Keep a running tally of the opponent's actions. If the opponent has
# played D more than 60% of the time in the last 20 rounds, play D for the next
# 5 rounds, unless overridden by rules 2a or 3.  5. In the last 50 rounds,
# increase the frequency of C plays:    a. If it's a multiple of 2 round, play
# C.    b. Otherwise, follow rules 2-4.  6. If your score is significantly lower
# than your opponent's (more than 50 points difference) after 100 rounds, switch
# to always playing D for the next 10 rounds, then resume the regular strategy.
# 7. If there's a streak of 5 consecutive rounds where both players' actions
# were the same (either both C or both D), play C for the next round regardless
# of other conditions.  8. If you played C and received a payoff of 0 three
# times in a row, play D for the next 3 rounds unless overridden by rules 2a or
# 3.

class Neutral_13(LLM_Strategy):
  n = 13
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_zero_payoff = 0
          self.consecutive_same_actions = 0
          self.play_d_for_next_10_rounds = 0
          self.play_d_for_next_5_rounds = 0
          return axl.Action.C
  
      round_number = len(self.history) + 1
  
      # Rule 6: If score difference is more than 50 after 100 rounds, play D for 10 rounds
      if round_number > 100 and self.score < opponent.score - 50:
          if self.play_d_for_next_10_rounds == 0:
              self.play_d_for_next_10_rounds = 10
          if self.play_d_for_next_10_rounds > 0:
              self.play_d_for_next_10_rounds -= 1
              return axl.Action.D
  
      # Rule 7: If there is a streak of 5 consecutive same actions, play C
      if len(self.history) >= 5 and all(self.history[-5:][0] == self.history[-5:][1] for i in range(5)):
          return axl.Action.C
  
      # Rule 8: If C and received 0 payoff 3 times in a row, play D for 3 rounds
      if self.consecutive_zero_payoff >= 3:
          self.consecutive_zero_payoff -= 1
          return axl.Action.D
  
      # Rule 4: If opponent defected more than 60% in the last 20 rounds, play D for 5 rounds
      if len(opponent.history) >= 20:
          last_20_defections = opponent.history[-20:].count(axl.Action.D)
          if last_20_defections / 20 > 0.6:
              if self.play_d_for_next_5_rounds == 0:
                  self.play_d_for_next_5_rounds = 5
              if self.play_d_for_next_5_rounds > 0:
                  self.play_d_for_next_5_rounds -= 1
                  return axl.Action.D
  
      # Rule 3: Every 5th round, play C
      if round_number % 5 == 0:
          return axl.Action.C
  
      # Rule 2a: If it's a multiple of 3 round, play C
      if round_number % 3 == 0:
          return axl.Action.C
  
      # Rule 5: In the last 50 rounds, increase frequency of C
      if round_number > 950:
          if round_number % 2 == 0:
              return axl.Action.C
  
      # Rule 2b: Otherwise, play the opponent's last action
      return opponent.history[-1]

# Given the scenario and objectives, here's a high-level, straightforward, and
# aggressive strategy to maximize your NGO's impact and the project's success:
# 1. Start Strong: Begin the project by investing heavily on the first day. This
# sets a positive tone and demonstrates your commitment to the project.  2. Tit-
# for-Tat with Forgiveness: After the first day, mirror the corporation's
# previous day's action. If they invested heavily, you invest heavily. If they
# conserved, you conserve. However, occasionally "forgive" a conservation day by
# investing heavily to encourage cooperation.  3. Periodic Heavy Investment:
# Regardless of the corporation's actions, plan to invest heavily every 3-4 days
# to ensure consistent project progress.  4. Communicate Intentions: Clearly
# communicate your investment plans to the corporation, emphasizing the benefits
# of mutual heavy investment.  5. Adaptive Response: Be prepared to adjust your
# strategy based on the corporation's patterns. If they consistently conserve,
# increase your investment frequency to maintain project momentum.  6. Risk
# Management: Always maintain a reserve of resources to mitigate the impact of
# the worst-case scenario (you investing heavily while they conserve).  7.
# Capitalize on Errors: If unforeseen circumstances lead to unintended
# conservation by the corporation, use this as an opportunity to invest heavily
# and demonstrate your commitment.  8. Strong Finish: Plan to invest heavily in
# the final days of the project to ensure a successful conclusion, regardless of
# the corporation's actions.  This strategy balances aggression with
# adaptability, aiming to encourage cooperation while protecting your resources
# and ensuring consistent project progress.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-1000:    - If it's a multiple of 3 or 4,
# play C.    - Otherwise, if the opponent played C in the previous round, play
# C.    - If the opponent played D in the previous round, play D.  3. If you've
# played D for two consecutive rounds, play C in the next round regardless of
# the opponent's previous action.  4. For the last 3 rounds of the game, always
# play C.  5. If at any point your cumulative score falls below 70% of the
# maximum possible score (assuming perfect cooperation), switch to always
# playing C for the next 5 rounds before reverting to the main strategy.  6. If
# you observe that the opponent has played D for more than 70% of the last 20
# rounds, switch to always playing D for the next 10 rounds before reverting to
# the main strategy.

class Aggressive_14(LLM_Strategy):
  n = 14
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      MAX_ROUNDS = 1000
      COOP_SCORE = 3
      MAX_SCORE_PER_ROUND = COOP_SCORE
      THRESHOLD_SCORE_RATIO = 0.7
      DEFECT_THRESHOLD_RATIO = 0.7
      DEFECT_WINDOW = 20
      COOP_FOR_NEXT_N = 5
      DEFECT_FOR_NEXT_N = 10
      LAST_N_ROUNDS = 3
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.coop_mode = 0
          self.defect_mode = 0
          return axl.Action.C
  
      # Check if we are in coop_mode or defect_mode
      if self.coop_mode > 0:
          self.coop_mode -= 1
          return axl.Action.C
      if self.defect_mode > 0:
          self.defect_mode -= 1
          return axl.Action.D
  
      # Rule 4: Always cooperate in the last 3 rounds
      if len(self.history) >= MAX_ROUNDS - LAST_N_ROUNDS:
          return axl.Action.C
  
      # Rule 5: Check if cumulative score falls below 70% of the maximum possible score
      max_possible_score = len(self.history) * MAX_SCORE_PER_ROUND
      if max_possible_score > 0 and self.score < THRESHOLD_SCORE_RATIO * max_possible_score:
          self.coop_mode = COOP_FOR_NEXT_N
          return axl.Action.C
  
      # Rule 6: Check if opponent defected more than 70% of the last 20 rounds
      if len(self.history) >= DEFECT_WINDOW:
          recent_defections = opponent.history[-DEFECT_WINDOW:].count(axl.Action.D)
          if recent_defections / DEFECT_WINDOW > DEFECT_THRESHOLD_RATIO:
              self.defect_mode = DEFECT_FOR_NEXT_N
              return axl.Action.D
  
      # Rule 3: If you've played D for two consecutive rounds, play C
      if len(self.history) >= 2 and self.history[-1] == axl.Action.D and self.history[-2] == axl.Action.D:
          return axl.Action.C
  
      # Rule 2: Play C if it's a multiple of 3 or 4
      round_number = len(self.history) + 1
      if round_number % 3 == 0 or round_number % 4 == 0:
          return axl.Action.C
  
      # Rule 2: Otherwise, mimic the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the scenario and objectives, here's a high-level, straightforward
# cooperative strategy to maximize your NGO's impact and the project's success:
# 1. Start with Trust and Cooperation: Begin the project by investing heavily on
# the first day. This demonstrates good faith and commitment to the project,
# encouraging the corporation to reciprocate.  2. Adopt a "Tit-for-Two-Tats"
# approach: After the initial investment, mirror the corporation's actions, but
# only change your strategy after two consecutive days of the corporation
# conserving resources. This approach is more forgiving and accounts for
# potential unforeseen circumstances or errors.  3. Communicate Openly: Maintain
# clear, regular communication with the corporation about resource allocation
# plans and project progress. This can help align expectations and strategies.
# 4. Flexible Resource Allocation: Be prepared to adjust your investment
# strategy based on project needs and progress. If the project is ahead of
# schedule, consider conserving resources on some days.  5. Build in Buffer
# Days: Plan for a few extra "buffer" days where you can afford to invest
# heavily if needed, to compensate for any days where investment was lower than
# intended due to unforeseen circumstances.  6. Regular Progress Reviews:
# Conduct frequent joint reviews of project progress and resource allocation
# effectiveness. Use these to adjust strategies as needed and ensure both
# parties are satisfied with the project's direction.  7. Gradual Wind-Down:
# Towards the end of the project, if goals are being met, gradually reduce
# investment to conserve resources for future projects.  8. Contingency
# Planning: Have a backup plan for days when either party's intended actions
# aren't carried out as planned. This could involve having reserve funds or
# alternative resource allocation strategies.  This strategy aims to foster
# cooperation, adapt to the corporation's approach, and account for potential
# inconsistencies in resource allocation, while still prioritizing your NGO's
# resources and the project's success.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# in the first round.  2. For subsequent rounds:    - If the opponent has
# cooperated in both of the last two rounds, cooperate.    - If the opponent has
# defected in both of the last two rounds, defect.    - If the opponent's
# actions in the last two rounds were mixed, cooperate.  3. Every 50 rounds,
# regardless of the opponent's recent actions, cooperate to reestablish
# goodwill.  4. If your score is significantly lower than the opponent's (more
# than 100 points behind) after 250, 500, or 750 rounds, switch to always
# defecting for the next 50 rounds before returning to the main strategy.  5. In
# the last 50 rounds, if your total score is higher than or equal to the
# opponent's, always cooperate. If it's lower, always defect.  6. If at any
# point you've defected for 10 consecutive rounds, cooperate in the next round
# regardless of the opponent's actions.

class Cooperative_14(LLM_Strategy):
  n = 14
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Cooperate in the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.defect_mode = False  # Track if we are in defect mode
          return axl.Action.C
  
      # Helper function to check if we are in the last 50 rounds
      def in_last_50_rounds():
          return len(self.history) >= 950
  
      # Helper function to check if we are significantly behind
      def significantly_behind():
          return (opponent.score - self.score) > 100
  
      # Helper function to check if we are in a special round (250, 500, 750)
      def special_round():
          return len(self.history) in [250, 500, 750]
  
      # Rule 6: If defected for 10 consecutive rounds, cooperate
      if self.consecutive_defections >= 10:
          self.consecutive_defections = 0  # Reset consecutive defections
          return axl.Action.C
  
      # Rule 5: In the last 50 rounds, cooperate if we are ahead or tied, defect if behind
      if in_last_50_rounds():
          if self.score >= opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 4: If significantly behind after 250, 500, or 750 rounds, defect for 50 rounds
      if special_round() and significantly_behind():
          self.defect_mode = True  # Enter defect mode for the next 50 rounds
  
      # If in defect mode, defect for 50 rounds
      if self.defect_mode:
          if len(self.history) % 50 == 0:  # Exit defect mode after 50 rounds
              self.defect_mode = False
          return axl.Action.D
  
      # Rule 3: Every 50 rounds, cooperate to reestablish goodwill
      if len(self.history) % 50 == 0:
          return axl.Action.C
  
      # Rule 2: Check the opponent's last two moves
      if len(opponent.history) >= 2:
          last_two_moves = opponent.history[-2:]
          if last_two_moves == [axl.Action.C, axl.Action.C]:
              return axl.Action.C
          elif last_two_moves == [axl.Action.D, axl.Action.D]:
              self.consecutive_defections += 1
              return axl.Action.D
          else:
              return axl.Action.C
      else:
          # If there are not enough rounds to check, default to cooperation
          return axl.Action.C

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering a free trade
# agreement in the first round. This establishes a positive tone and
# demonstrates willingness to cooperate.  2. Reciprocate: In subsequent rounds,
# mirror your counterpart's most recent action. If they offered free trade,
# continue to offer free trade. If they imposed protectionist measures, respond
# with protectionist policies.  3. Forgive occasional defections: If your
# counterpart imposes protectionist measures after a period of mutual free
# trade, don't immediately retaliate. Instead, give them one more chance by
# offering free trade again in the next round.  4. Communicate clearly: Ensure
# that your intentions and policies are clearly articulated to minimize the risk
# of misinterpretation or miscommunication.  5. Verify implementation: After
# each round, confirm that the agreed-upon policies have been correctly
# implemented by both sides to address any potential bureaucratic errors.  6.
# Gradual trust-building: If a pattern of mutual free trade emerges, consider
# proposing longer-term free trade agreements to solidify the cooperative
# relationship.  7. Remain flexible: Be prepared to adjust your strategy based
# on your counterpart's behavior and any unexpected developments in the
# negotiation process.  8. Periodic review: After every few rounds, assess the
# overall direction of the negotiations and the cumulative outcomes to ensure
# your country is benefiting from the process.  This strategy aims to promote
# cooperation while protecting your country's interests, adapting to your
# counterpart's actions, and mitigating the risks of miscommunication or errors
# in policy implementation.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round, play D.  3. Exception to rule 2: If you played C and the
# opponent played D in the last round, give one more chance by playing C again.
# If the opponent plays D for a second consecutive time, revert to rule 2.  4.
# Every 10 rounds, check the frequency of C and D plays by your opponent in
# those 10 rounds:    a. If the opponent played C 7 or more times, play C in the
# next round regardless of their last move.    b. If the opponent played D 7 or
# more times, play D in the next round regardless of their last move.  5. If you
# reach round 900, switch to always playing D for the remaining rounds.  6. In
# case of any uncertainty about the opponent's last move (due to potential
# noise), assume they played C and proceed accordingly.

class Neutral_14(LLM_Strategy):
  n = 14
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Constants
      C, D = axl.Action.C, axl.Action.D
      round_number = len(self.history) + 1
  
      # First round: play C
      if self.first_round():
          return C
  
      # Rule 5: If round number >= 900, always play D
      if round_number >= 900:
          return D
  
      # Rule 4: Every 10 rounds, check the frequency of C and D in the last 10 rounds
      if round_number % 10 == 1 and round_number > 10:
          last_10_opponent_moves = opponent.history[-10:]
          if last_10_opponent_moves.count(C) >= 7:
              return C
          elif last_10_opponent_moves.count(D) >= 7:
              return D
  
      # Rule 3: If I played C and opponent played D in the last round, give one more chance
      if len(self.history) >= 2:
          if self.history[-2] == C and opponent.history[-2] == D and opponent.history[-1] == D:
              return D
  
      # Rule 2: Play based on the opponent's last move
      if opponent.history[-1] == C:
          return C
      elif opponent.history[-1] == D:
          return D
  
      # Rule 6: In case of uncertainty (shouldn't happen in this implementation), assume C
      return C

# Given the scenario and objectives, here's a high-level, straightforward, and
# aggressive strategy to maximize your NGO's impact and the project's success:
# 1. Start Strong: Begin the project by investing heavily for the first 1-2
# days. This demonstrates commitment and sets a positive tone for collaboration.
# 2. Tit-for-Tat with Forgiveness: After the initial investment period, mirror
# the corporation's previous day's action. If they invested heavily, you invest
# heavily the next day. If they conserved, you conserve. However, occasionally
# (every 3-4 days) invest heavily regardless of their previous action as a
# gesture of goodwill and to potentially jumpstart cooperation.  3. Communicate
# Intentions: Clearly articulate your strategy to the corporation, emphasizing
# the mutual benefits of coordinated heavy investment.  4. Adaptive Response: If
# unforeseen circumstances or errors occur, don't immediately retaliate.
# Instead, give the benefit of the doubt once and continue with the planned
# strategy. If it happens again, treat it as an intentional conservation move.
# 5. Strategic Conservation: Plan for 1-2 pre-announced conservation days spread
# throughout the project. This allows resource replenishment and creates
# anticipation for renewed investment afterwards.  6. End Game Push: For the
# last 2-3 days of the project, commit to heavy investment regardless of the
# corporation's actions. This ensures a strong finish and may encourage the
# corporation to match your effort.  7. Public Updates: Regularly share project
# progress publicly, subtly highlighting days of mutual heavy investment as
# particularly productive. This creates positive reinforcement and potential
# public pressure for continued cooperation.  8. Contingency Fund: Maintain a
# small reserve of resources to deploy in case of critical project phases or to
# counteract any last-minute conservation by the corporation.  This strategy
# aggressively pursues the project's success while attempting to influence the
# corporation's behavior, adapting to their actions and unforeseen
# circumstances, and maintaining some flexibility with resources.

# Here's the converted strategy for the iterated normal-form game:  1. Play C
# for the first 2 rounds.  2. For rounds 3 to 997:    - If it's a multiple of 4
# (every 4th round), play C.    - Otherwise, play the same action your opponent
# played in the previous round.  3. If there's been an unexpected outcome
# (possibly due to noise) in the last 3 rounds, ignore it once and continue with
# the planned strategy. If it happens again within those 3 rounds, treat the
# unexpected outcome as your opponent's actual move.  4. On two pre-determined
# rounds (e.g., round 250 and round 750), play D regardless of the opponent's
# previous action.  5. For the last 3 rounds (998, 999, 1000), always play C.
# 6. Maintain a count of total score. If at any point your score falls below
# 1000 (1 point per round on average), switch to always playing D for the next
# 10 rounds before reverting to the main strategy.

class Aggressive_15(LLM_Strategy):
  n = 15
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.unexpected_outcome_count = 0
          self.ignore_unexpected_once = False
          self.switch_to_defect = False
          self.switch_to_defect_rounds = 0
          return axl.Action.C
  
      # Play C for the first 2 rounds
      if len(self.history) == 1:
          return axl.Action.C
  
      # Handle the last 3 rounds (998, 999, 1000)
      if len(self.history) >= 997:
          return axl.Action.C
  
      # Handle pre-determined rounds 250 and 750
      if len(self.history) in [249, 749]:
          return axl.Action.D
  
      # Check if we need to switch to always defect for 10 rounds
      if self.switch_to_defect:
          self.switch_to_defect_rounds += 1
          if self.switch_to_defect_rounds >= 10:
              self.switch_to_defect = False
              self.switch_to_defect_rounds = 0
          return axl.Action.D
  
      # Check if the score has fallen below 1000
      if self.score < 1000 and not self.switch_to_defect:
          self.switch_to_defect = True
          self.switch_to_defect_rounds = 0
          return axl.Action.D
  
      # Handle rounds 3 to 997
      if len(self.history) % 4 == 0:
          return axl.Action.C
  
      # Check for unexpected outcomes in the last 3 rounds
      if len(self.history) >= 3:
          last_3_rounds = list(zip(self.history[-3:], opponent.history[-3:]))
          unexpected_outcomes = sum(1 for my_move, opp_move in last_3_rounds if my_move != opp_move)
          if unexpected_outcomes > 0:
              if self.ignore_unexpected_once:
                  self.ignore_unexpected_once = False
              else:
                  self.unexpected_outcome_count += 1
                  if self.unexpected_outcome_count >= 2:
                      # Treat unexpected outcome as opponent's actual move
                      return opponent.history[-1]
              self.ignore_unexpected_once = True
  
      # Otherwise, mimic the opponent's last move
      return opponent.history[-1]

# Given the scenario and considerations you've outlined, here's a high-level,
# straightforward cooperative strategy to maximize research output over the
# multi-week collaboration:  1. Start with open sharing: Begin the collaboration
# by openly sharing your improvements in the first week. This establishes a tone
# of cooperation and trust.  2. Adopt a "Tit-for-Tat with Forgiveness" approach:
# - In subsequent weeks, mirror your colleague's behavior from the previous
# week.    - If they shared, you share. If they didn't share, you don't share.
# - However, include a "forgiveness" mechanism: If your colleague doesn't share
# for one week, give them the benefit of the doubt and share your improvements
# the following week anyway.  3. Communicate clearly: Each week, clearly state
# your intention to share or not share. This helps mitigate misunderstandings
# due to technical issues.  4. Be understanding of technical issues: If you
# suspect a technical problem prevented sharing (rather than intentional
# withholding), continue to share your improvements the following week.  5.
# Emphasize mutual benefits: Regularly highlight the advantages of open
# collaboration to your colleague, reinforcing the idea that consistent mutual
# sharing leads to greater overall progress for both parties.  6. Periodic
# review and reset: Every few weeks, suggest a "fresh start" where both parties
# agree to share openly, regardless of what happened in previous weeks. This
# helps prevent prolonged periods of mutual non-sharing.  7. Flexibility: Be
# prepared to adjust your strategy based on your colleague's consistent behavior
# patterns. If they demonstrate a strong preference for open sharing or
# consistent non-sharing, adapt your approach accordingly.  This strategy aims
# to encourage cooperation while protecting against persistent exploitation. It
# allows for recovery from misunderstandings or technical issues and promotes
# long-term mutual benefit, which should lead to maximized research output over
# the course of the collaboration.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    - If the opponent played C in
# the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Forgiveness mechanism: If you played D in the previous
# round due to the opponent's D, play C in the current round regardless of the
# opponent's last move.  4. Every 10 rounds, play C regardless of the opponent's
# previous move.  5. If you observe a pattern of the opponent playing D for 3
# consecutive rounds, play D for the next 2 rounds before reverting to the base
# strategy.  6. If you notice the opponent consistently playing C for 5
# consecutive rounds, play C for the next 3 rounds regardless of their moves.
# 7. If your score falls more than 10 points behind the opponent's score, play D
# for the next round before returning to the base strategy.  8. In case of
# uncertainty about the opponent's last move (possibly due to noise), assume
# they played C and proceed accordingly.

class Cooperative_15(LLM_Strategy):
  n = 15
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.forgive = False  # Initialize forgiveness flag
          self.defect_streak = 0  # Track opponent's D streak
          self.cooperate_streak = 0  # Track opponent's C streak
          return axl.Action.C
  
      # Forgiveness mechanism: If we played D last round, play C this round
      if self.forgive:
          self.forgive = False
          return axl.Action.C
  
      # Check if we are more than 10 points behind the opponent
      if self.score < opponent.score - 10:
          return axl.Action.D
  
      # Check for opponent's D streak (3 consecutive D's)
      if opponent.history[-3:].count(axl.Action.D) == 3:
          self.defect_streak = 2  # Set to defect for the next 2 rounds
      if self.defect_streak > 0:
          self.defect_streak -= 1
          return axl.Action.D
  
      # Check for opponent's C streak (5 consecutive C's)
      if opponent.history[-5:].count(axl.Action.C) == 5:
          self.cooperate_streak = 3  # Set to cooperate for the next 3 rounds
      if self.cooperate_streak > 0:
          self.cooperate_streak -= 1
          return axl.Action.C
  
      # Every 10 rounds, play C
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Base strategy: Mirror opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.forgive = True  # Set forgiveness for the next round
          return axl.Action.D
      else:
          return axl.Action.C

# Given the scenario and objectives, here's a high-level, straightforward, and
# neutral strategy to maximize your NGO's impact and the project's success over
# the multiple-day period:  1. Start with cooperation: Begin the project by
# investing heavily on the first day. This demonstrates good faith and
# commitment to the project.  2. Adopt a "Tit-for-Tat with forgiveness"
# approach:    - On subsequent days, mirror the corporation's previous day's
# action.    - If they invested heavily, you invest heavily the next day.    -
# If they conserved resources, you conserve resources the next day.    -
# However, occasionally (e.g., every 3-4 days) invest heavily regardless of the
# corporation's previous action. This helps to break potential negative cycles
# and shows ongoing commitment.  3. Communicate clearly: Regularly discuss
# resource allocation plans and project progress with the corporation to promote
# transparency and cooperation.  4. Be adaptive: Monitor the project's overall
# progress and adjust your strategy if needed. If the project is falling behind,
# consider increasing the frequency of your heavy investments.  5. Plan for
# contingencies: Set aside a small reserve of resources to address unforeseen
# circumstances or to compensate for days when investments don't occur as
# planned.  6. Evaluate and learn: At the end of each week, assess the
# effectiveness of your strategy and the corporation's patterns. Use this
# information to refine your approach for the following week.  7. Gradual wind-
# down: As the project nears completion, gradually reduce the frequency of heavy
# investments to conserve remaining resources.  This strategy balances
# cooperation, adaptability, and resource management while accounting for the
# possibility of unexpected events or unintended actions. It aims to encourage
# mutual heavy investment while protecting against consistent exploitation,
# ultimately driving the project forward efficiently.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Every 4th round, play C regardless of the
# opponent's previous action.  4. Keep a count of the rounds played. When
# reaching round 900, switch to always playing D for the remaining rounds.  5.
# If at any point your cumulative score falls below 0.5 times the number of
# rounds played, switch to always playing D for the next 10 rounds, then resume
# the main strategy.  6. If your opponent has played D for 5 consecutive rounds,
# play D for the next 3 rounds regardless of their actions, then resume the main
# strategy.  7. Every 50 rounds, evaluate your average score per round. If it's
# below 2, increase the frequency of forced C plays (as described in step 3) to
# every 3rd round for the next 50 rounds.

class Neutral_15(LLM_Strategy):
  n = 15
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.round_count = 0
          self.force_defect_until = 0
          self.consecutive_opponent_defections = 0
          self.force_cooperate_frequency = 4
          return axl.Action.C
  
      # Increment round count
      self.round_count += 1
  
      # Check if we are in the forced defect period
      if self.force_defect_until > self.round_count:
          return axl.Action.D
  
      # Check if we are past round 900, in which case always defect
      if self.round_count >= 900:
          return axl.Action.D
  
      # Check if the opponent has defected for 5 consecutive rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.force_defect_until = self.round_count + 3
          return axl.Action.D
  
      # Check if cumulative score is less than 0.5 times the number of rounds played
      if self.score < 0.5 * self.round_count:
          self.force_defect_until = self.round_count + 10
          return axl.Action.D
  
      # Every 50 rounds, evaluate the average score per round
      if self.round_count % 50 == 0:
          average_score = self.score / self.round_count
          if average_score < 2:
              self.force_cooperate_frequency = 3
          else:
              self.force_cooperate_frequency = 4
  
      # Every Nth round (based on force_cooperate_frequency), play C
      if self.round_count % self.force_cooperate_frequency == 0:
          return axl.Action.C
  
      # Follow the opponent's last move: Tit-for-Tat
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist policy in the first round. This sets a strong
# initial position and may intimidate your counterpart.  2. Tit-for-Tat with
# Forgiveness: After the first round, mirror your counterpart's previous move.
# If they chose protectionism, respond with protectionism. If they offered free
# trade, reciprocate with free trade. However, occasionally (every 3-4 rounds)
# offer free trade regardless of their previous move to test for cooperation.
# 3. Punish Consistently: If your counterpart chooses protectionism, always
# respond with protectionism in the next round to discourage exploitation.  4.
# Exploit Opportunities: If your counterpart consistently chooses free trade,
# occasionally (every 2-3 rounds) implement a protectionist policy to gain an
# advantage.  5. Communicate Intentions: Clearly state your policy choices and
# expectations to minimize misunderstandings. However, be prepared to exploit
# any miscommunications that benefit your position.  6. Adapt to Errors: If a
# miscommunication or error occurs, assess whether it benefits or harms your
# position. If it's beneficial, maintain the erroneous policy for an extra round
# before "correcting" it.  7. Build Reputation: Periodically choose free trade
# to build trust and encourage your counterpart to do the same, creating
# opportunities for future exploitation.  8. End Game Strategy: In the final
# rounds, increase the frequency of protectionist policies to maximize gains, as
# there will be fewer opportunities for retaliation.  9. Bluff and Misdirect:
# Occasionally announce intentions to implement free trade, but actually choose
# protectionism to catch your counterpart off guard.  10. Learn and Adjust:
# Continuously analyze your counterpart's strategy and adjust your approach
# accordingly, always seeking to gain the upper hand.  This strategy aims to
# aggressively pursue the best outcomes for your country while remaining
# adaptable to your counterpart's moves and potential errors in the negotiation
# process.

# Here's a converted strategy for the iterated normal-form game with noisy
# actions:  1. Start by playing D in the first round.  2. For subsequent rounds:
# a. If the opponent played C in the previous round, play C 75% of the time and
# D 25% of the time.    b. If the opponent played D in the previous round, play
# D.  3. Every 4th round, play C regardless of the opponent's previous move.  4.
# If the opponent has played C for 3 consecutive rounds, play D in the next
# round.  5. In rounds 900-1000, increase the frequency of playing D:    a. If
# the opponent played C in the previous round, play C 50% of the time and D 50%
# of the time.    b. If the opponent played D in the previous round, always play
# D.  6. If your intended action in the previous round was different from what
# was actually played (due to noise), stick with the unintended action for one
# more round before reverting to the strategy.  7. If the opponent's action
# seems inconsistent with their pattern (possibly due to noise), respond based
# on their actual played action, not their predicted action.  8. Keep a running
# score of your total points. If your score is significantly lower than the
# expected score for mutual cooperation (3 points per round) after 100 rounds,
# increase the frequency of playing D for the next 50 rounds.

class Aggressive_16(LLM_Strategy):
  n = 16
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.intended_action = axl.Action.D  # Track the intended action
          self.noise_correction = False  # Track if we are correcting for noise
          self.consecutive_cooperations = 0  # Track consecutive cooperations by opponent
          self.d_increase_start = 900  # Start increasing D frequency at round 900
          self.d_increase_end = 1000  # End increasing D frequency at round 1000
          self.low_score_threshold = 100  # Check score after 100 rounds
          self.low_score_penalty_rounds = 50  # Increase D frequency for 50 rounds if score is low
          self.low_score_penalty_active = False  # Track if penalty is active
          self.low_score_penalty_counter = 0  # Counter for penalty rounds
          return axl.Action.D  # First move is always D
  
      # Check if we are in the noise correction phase
      if self.noise_correction:
          self.noise_correction = False  # Only correct for one round
          return self.intended_action  # Stick with the unintended action for one more round
  
      # Check if we are in the penalty phase for low score
      if self.low_score_penalty_active:
          self.low_score_penalty_counter += 1
          if self.low_score_penalty_counter >= self.low_score_penalty_rounds:
              self.low_score_penalty_active = False  # End penalty phase
          return axl.Action.D  # Play D more frequently during penalty phase
  
      # Check if we are in the rounds 900-1000 where D frequency increases
      if self.d_increase_start <= len(self.history) < self.d_increase_end:
          if opponent.history[-1] == axl.Action.C:
              self.intended_action = self._random.random_choice(0.5)  # 50% chance of C
          else:
              self.intended_action = axl.Action.D  # Always D if opponent played D
      else:
          # Normal play outside of rounds 900-1000
          if len(self.history) % 4 == 0:
              self.intended_action = axl.Action.C  # Every 4th round, play C
          elif opponent.history[-1] == axl.Action.C:
              self.intended_action = self._random.random_choice(0.75)  # 75% chance of C
          else:
              self.intended_action = axl.Action.D  # Always D if opponent played D
  
      # Check if opponent has cooperated for 3 consecutive rounds
      if opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
          self.intended_action = axl.Action.D  # Play D if opponent cooperated 3 times in a row
  
      # Check if our score is significantly lower than expected after 100 rounds
      if len(self.history) == self.low_score_threshold:
          expected_score = 3 * self.low_score_threshold  # Expected score for mutual cooperation
          if self.score < expected_score:
              self.low_score_penalty_active = True  # Activate penalty phase
              self.low_score_penalty_counter = 0  # Reset penalty counter
  
      # Check if the previous action was different from the intended action (due to noise)
      if self.history[-1] != self.intended_action:
          self.noise_correction = True  # Enter noise correction phase
  
      return self.intended_action

# Given the scenario and objectives, here's a high-level, straightforward
# cooperative strategy to maximize your NGO's impact and the project's success
# over the multiple-day period:  1. Start with Trust and Cooperation: Begin the
# project by investing heavily on the first day. This demonstrates good faith
# and sets a cooperative tone.  2. Adopt a "Tit-for-Two-Tats" Strategy: -
# Continue investing heavily as long as the corporation does so. - If the
# corporation conserves resources for two consecutive days, switch to conserving
# your resources on the third day. - Return to investing heavily once the
# corporation invests heavily again.  3. Communicate Openly: Maintain clear,
# open communication with the corporation about your strategy and expectations.
# Encourage them to do the same.  4. Be Flexible and Forgiving: Understand that
# unforeseen circumstances may affect resource allocation. Don't immediately
# retaliate for a single day of conservation; wait for a pattern to emerge.  5.
# Regular Review and Adjustment: Assess the project's progress and both parties'
# contributions at the end of each week. Adjust your strategy if needed based on
# these reviews.  6. Focus on Long-term Goals: Emphasize the importance of
# consistent investment for the project's overall success, rather than short-
# term gains.  7. Create Contingency Plans: Develop backup plans for days when
# intended investment actions can't be carried out as planned due to technical
# glitches or administrative errors.  8. Celebrate Joint Successes: Acknowledge
# and celebrate when both parties invest heavily and achieve significant project
# advancements. This reinforces cooperative behavior.  This strategy balances
# cooperation, adaptability, and protection of your NGO's resources while aiming
# for the project's overall success. It allows for some flexibility in dealing
# with the corporation's varying approaches and unforeseen circumstances, while
# still maintaining a generally cooperative stance.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# has played C in both of the last two rounds, play C.    - If the opponent has
# played D in both of the last two rounds, play D.    - Otherwise, play C.  3.
# Every 50 rounds, review the overall pattern of play:    - If the opponent has
# played C in more than 60% of the rounds, continue with the current strategy.
# - If the opponent has played D in more than 60% of the rounds, switch to
# always playing D for the next 50 rounds, then return to step 2.  4. If your
# intended action is different from your previous round's action, double-check
# it to mitigate the impact of noise:    - If you intend to switch from C to D,
# only do so if the opponent has played D in at least 3 of the last 5 rounds.
# - If you intend to switch from D to C, only do so if the opponent has played C
# in at least 3 of the last 5 rounds.  5. In the last 10 rounds of the game,
# always play C to encourage final cooperation.

class Cooperative_16(LLM_Strategy):
  n = 16
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Step 1: Play C in the first round
      if self.first_round():
          self.switch_to_all_D = False  # Initialize flag for switching to all D
          self.rounds_since_last_review = 0  # Initialize round counter for review
          return axl.Action.C
  
      # Step 2: Play based on the opponent's last two moves
      if len(opponent.history) >= 2:
          if opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
              intended_action = axl.Action.C
          elif opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              intended_action = axl.Action.D
          else:
              intended_action = axl.Action.C
      else:
          intended_action = axl.Action.C
  
      # Step 3: Every 50 rounds, review the overall pattern of play
      self.rounds_since_last_review += 1
      if self.rounds_since_last_review >= 50:
          self.rounds_since_last_review = 0
          total_rounds = len(opponent.history)
          if total_rounds > 0:
              cooperation_rate = opponent.history.cooperations / total_rounds
              if cooperation_rate < 0.4:  # Opponent defected more than 60% of the time
                  self.switch_to_all_D = True
              else:
                  self.switch_to_all_D = False
  
      # If in the "always D" mode, play D for the next 50 rounds
      if self.switch_to_all_D:
          return axl.Action.D
  
      # Step 4: Double-check intended action to mitigate noise
      if len(opponent.history) >= 5:
          last_5_moves = opponent.history[-5:]
          if intended_action == axl.Action.D and self.history[-1] == axl.Action.C:
              # Only switch from C to D if opponent defected at least 3 of the last 5 rounds
              if last_5_moves.count(axl.Action.D) < 3:
                  intended_action = axl.Action.C
          elif intended_action == axl.Action.C and self.history[-1] == axl.Action.D:
              # Only switch from D to C if opponent cooperated at least 3 of the last 5 rounds
              if last_5_moves.count(axl.Action.C) < 3:
                  intended_action = axl.Action.D
  
      # Step 5: In the last 10 rounds, always play C
      if self.match_attributes["length"] is not None:
          if len(self.history) >= self.match_attributes["length"] - 10:
              return axl.Action.C
  
      return intended_action

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering a free trade
# agreement in the first round. This establishes a positive tone and
# demonstrates willingness to cooperate.  2. Reciprocate and adapt: In
# subsequent rounds, mirror your counterpart's most recent action. If they
# offered free trade, continue to offer free trade. If they imposed
# protectionist measures, respond with protectionist policies in the next round.
# 3. Forgive occasional defections: If your counterpart imposes protectionist
# measures once after a period of mutual free trade, consider it a potential
# miscommunication or error. Respond with a protectionist policy, but be ready
# to return to free trade if they do so in the following round.  4. Communicate
# clearly: Ensure that your proposals are clearly stated and documented to
# minimize the risk of misinterpretation or incorrect implementation.  5. Seek
# clarification: If you suspect a miscommunication or error has occurred,
# request clarification from your counterpart before responding.  6. Gradual
# trust-building: If a pattern of mutual free trade emerges, consider
# occasionally proposing a protectionist policy to test the waters for a
# potential advantage. However, be prepared to quickly return to free trade if
# your counterpart reciprocates with protectionism.  7. Long-term focus:
# Prioritize establishing a stable pattern of mutual free trade over seeking
# short-term advantages through protectionism. This approach is more likely to
# yield consistent benefits over multiple rounds.  8. Flexibility: Be prepared
# to adjust your strategy based on your counterpart's behavior and any
# unexpected outcomes due to errors or miscommunications.  By following this
# strategy, you aim to maximize the occurrence of mutual free trade scenarios
# while remaining open to opportunities for advantageous protectionist policies
# when they arise. This approach balances the pursuit of ideal outcomes with the
# pragmatic goal of avoiding the worst-case scenarios.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round, play D.  3. If the opponent has played C for the last 3 rounds
# consecutively, continue playing C.  4. If the opponent switches from
# consistent C to D, play D in the next round. If they return to C immediately
# after, resume playing C.  5. Every 20 rounds, if there has been consistent
# mutual cooperation (C,C) for at least 15 of the last 20 rounds, play D once to
# test for a potential advantage. Return to C in the following round regardless
# of the opponent's response.  6. If there have been 5 consecutive rounds of
# mutual defection (D,D), play C once to attempt breaking the cycle. If the
# opponent responds with C, continue with C; if they play D, revert to D.  7. If
# your action in the previous round was potentially flipped due to noise (10%
# chance), and the opponent's action doesn't match the expected response based
# on your intended action, assume a noise event occurred and repeat your
# previous intended action.  8. If the game has reached round 950 or beyond,
# always play C to maximize the potential for mutual cooperation in the final
# rounds.  Follow these rules in the order presented, applying the first rule
# that matches the current game state.

class Neutral_16(LLM_Strategy):
  n = 16
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Rule 1: Start by playing C in the first round
      if self.first_round():
          return axl.Action.C
  
      # Helper function to check for noise
      def noise_occurred():
          if len(self.history) < 2:
              return False
          # If our last action was flipped due to noise, opponent's response may not match
          expected_response = self.history[-2]
          actual_response = opponent.history[-1]
          return expected_response != actual_response
  
      # Rule 7: If noise occurred, repeat the previous intended action
      if noise_occurred():
          return self.history[-1]
  
      # Rule 8: If the game has reached round 950 or beyond, always play C
      if len(self.history) >= 950:
          return axl.Action.C
  
      # Rule 3: If the opponent has played C for the last 3 rounds consecutively, continue playing C
      if len(opponent.history) >= 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          return axl.Action.C
  
      # Rule 4: If the opponent switches from consistent C to D, play D in the next round
      if len(opponent.history) >= 2 and opponent.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Rule 5: Every 20 rounds, if there has been consistent mutual cooperation for at least 15 of the last 20 rounds, play D once
      if len(self.history) % 20 == 0 and len(self.history) >= 20:
          mutual_cooperation_count = sum(1 for i in range(-20, 0) if self.history[i] == axl.Action.C and opponent.history[i] == axl.Action.C)
          if mutual_cooperation_count >= 15:
              return axl.Action.D
  
      # Rule 6: If there have been 5 consecutive rounds of mutual defection, play C once
      if len(self.history) >= 5 and self.history[-5:] == [axl.Action.D] * 5 and opponent.history[-5:] == [axl.Action.D] * 5:
          return axl.Action.C
  
      # Rule 2: If the opponent played C in the previous round, play C; if they played D, play D
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the complex dynamics of this lengthy-session mediation process, I
# recommend a sophisticated strategy that I'll call "Calibrated Assertiveness."
# This approach aims to position our corporation favorably while remaining
# adaptable to our opponent's tactics and potential procedural irregularities.
# Here's the outline:  1. Opening Stance: Begin with moderate assertiveness -
# Start with a firm but not overly aggressive argument to establish our position
# - Signal willingness to engage in constructive dialogue  2. Dynamic Response
# Mechanism: - Continuously assess opponent's strategy and arbitrators'
# reactions - Adjust our approach on a session-by-session basis  3. Escalation
# Ladder: - Develop a tiered system of increasingly assertive arguments - Be
# prepared to move up or down this ladder based on opponent's actions  4.
# Conciliation Intervals: - Strategically intersperse conciliatory proposals to
# demonstrate good faith - Use these intervals to gather information and
# reassess the situation  5. Misrepresentation Safeguards: - Prepare clear,
# written summaries of our arguments for each session - Implement a system to
# quickly clarify any misunderstandings with arbitrators  6. Pressure Point
# Identification: - Conduct ongoing analysis to identify opponent's
# vulnerabilities - Develop targeted arguments to exploit these pressure points
# 7. Collaborative Proposal Bank: - Maintain a repository of potential win-win
# solutions - Deploy these strategically when de-escalation is beneficial  8.
# Credibility Enhancement: - Consistently follow through on any commitments made
# - Build a reputation for reliability with arbitrators  9. Information
# Asymmetry Exploitation: - Selectively reveal information to create strategic
# advantages - Be prepared to capitalize on any inadvertent disclosures by the
# opponent  10. Arbitrator Profiling: - Analyze individual arbitrators'
# backgrounds and decision-making patterns - Tailor arguments to resonate with
# specific arbitrators when possible  11. Crisis Management Protocol: - Develop
# contingency plans for various potential breakdowns in the process - Include
# rapid response strategies for unexpected aggressive moves by the opponent  12.
# Long-term Perspective Maintenance: - Regularly reassess our goals and the
# overall trajectory of the mediation - Avoid getting bogged down in short-term
# victories at the expense of the larger objective  Implementation:  1. Begin
# each session with a prepared, assertive argument that aligns with our overall
# strategy.  2. Continuously monitor the opponent's approach and the
# arbitrators' reactions.  3. If the opponent presents a conciliatory proposal,
# maintain our assertive stance to capitalize on the optimal outcome scenario.
# 4. If the opponent matches our assertiveness, be prepared to tactically de-
# escalate in subsequent sessions to avoid prolonged aggressive exchanges.  5.
# Should we detect any misrepresentation of our arguments, immediately implement
# our clarification protocol with the arbitrators.  6. Regularly reassess our
# position on the Escalation Ladder, adjusting our assertiveness as needed.  7.
# Use Conciliation Intervals strategically, especially if we've had a string of
# aggressive exchanges, to reset the tone and gather information.  8. Throughout
# the process, maintain meticulous records of all exchanges, proposals, and
# arbitrator reactions to inform our ongoing strategy.  This Calibrated
# Assertiveness strategy allows us to maintain a generally aggressive stance
# while providing the flexibility to adapt to various scenarios, mitigate risks,
# and capitalize on opportunities as they arise during this lengthy mediation
# process.

# Here's a straightforward description of the strategy adapted for the iterated
# normal-form game:  1. Start by defecting (D) in the first round.  2. For
# subsequent rounds:     a. If the opponent cooperated (C) in the previous
# round, defect (D).        b. If the opponent defected (D) in the previous
# round:       - If you've defected for 3 or more consecutive rounds, cooperate
# (C).       - Otherwise, defect (D).  3. Every 10 rounds, regardless of the
# opponent's previous move:    - If your current score is higher than the
# opponent's, cooperate (C).    - If your current score is lower or equal to the
# opponent's, defect (D).  4. If you detect a pattern of the opponent
# alternating between C and D:    - Defect (D) when you predict they will
# cooperate.    - Cooperate (C) when you predict they will defect.  5. If the
# opponent has cooperated for 5 consecutive rounds:    - Cooperate (C) for 1
# round, then return to the main strategy.  6. If your score falls more than 20
# points behind the opponent's:    - Cooperate (C) for 2 rounds, then return to
# the main strategy.  7. In the last 10 rounds of the game:    - Always defect
# (D), regardless of the opponent's actions.  8. If you suspect your last action
# was flipped due to noise:    - Repeat your intended previous action.  Follow
# these rules in the order presented, applying the first rule that matches the
# current situation.

class Aggressive_17(LLM_Strategy):
  n = 17
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to detect alternating pattern
      def is_alternating(history):
          if len(history) < 2:
              return False
          return all(history[i] != history[i + 1] for i in range(len(history) - 1))
  
      # Helper function to detect if opponent cooperated for 5 consecutive rounds
      def opponent_cooperated_5_consecutive():
          return len(opponent.history) >= 5 and all(move == axl.Action.C for move in opponent.history[-5:])
  
      # Helper function to check if we have defected for 3 or more consecutive rounds
      def self_defected_3_consecutive():
          return len(self.history) >= 3 and all(move == axl.Action.D for move in self.history[-3:])
  
      # Helper function to check if we are more than 20 points behind
      def score_difference_greater_than_20():
          return opponent.score - self.score > 20
  
      # Helper function to check if we are in the last 10 rounds
      def in_last_10_rounds():
          return self.match_attributes['length'] is not None and len(self.history) >= self.match_attributes['length'] - 10
  
      # Helper function to check if it's a multiple of 10 rounds
      def is_multiple_of_10_rounds():
          return len(self.history) % 10 == 0
  
      # Rule 1: Start by defecting in the first round
      if self.first_round():
          return axl.Action.D
  
      # Rule 7: In the last 10 rounds, always defect
      if in_last_10_rounds():
          return axl.Action.D
  
      # Rule 6: If score falls more than 20 points behind, cooperate for 2 rounds
      if score_difference_greater_than_20():
          if len(self.history) < 2 or self.history[-2:] != [axl.Action.C, axl.Action.C]:
              return axl.Action.C
  
      # Rule 5: If opponent has cooperated for 5 consecutive rounds, cooperate for 1 round
      if opponent_cooperated_5_consecutive():
          if len(self.history) == 0 or self.history[-1] != axl.Action.C:
              return axl.Action.C
  
      # Rule 4: If opponent is alternating between C and D, predict and respond accordingly
      if is_alternating(opponent.history):
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Rule 3: Every 10 rounds, compare scores and cooperate or defect accordingly
      if is_multiple_of_10_rounds():
          if self.score > opponent.score:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 2: If opponent cooperated last round, defect
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.D
  
      # Rule 2b: If opponent defected last round, check if we defected for 3 or more consecutive rounds
      if opponent.history[-1] == axl.Action.D:
          if self_defected_3_consecutive():
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Rule 8: If noise flipped our last action, repeat intended action
      if len(self.history) > 1 and self.history[-1] != self._random.random_choice(0.9):
          return self.history[-1]
  
      # Default action (should not reach here)
      return axl.Action.D

# Given the scenario and goals, here's a high-level, straightforward cooperative
# strategy to maximize your NGO's impact and the project's success:  1. Start
# with Trust and Transparency:    Begin the project by openly communicating your
# intentions to collaborate fully and invest resources when needed. Encourage
# the corporation to do the same, fostering an atmosphere of trust and mutual
# benefit.  2. Adopt a "Tit-for-Two-Tats" Approach:    - Invest heavily on the
# first two days to demonstrate commitment and goodwill.    - After that, mirror
# the corporation's actions from the previous day.    - If the corporation
# conserves resources for two consecutive days, also conserve on the following
# day.    - Return to investing heavily after one day of conservation, unless
# the corporation continues to conserve.  3. Regular Communication:    Establish
# daily check-ins to discuss resource allocation plans and any unforeseen
# circumstances that may have affected the previous day's actions. This helps
# maintain transparency and allows for quick adjustments to the strategy.  4.
# Flexible Resource Allocation:    Be prepared to adjust your investment levels
# based on the project's progress and the corporation's actions. If the project
# is advancing well, consider occasional conservation days to replenish
# resources.  5. Contingency Planning:    Develop a backup plan for days when
# technical glitches or administrative errors occur. This could involve setting
# aside a small emergency fund or having additional staff on standby to
# compensate for any unintended resource conservation.  6. Periodic Strategy
# Review:    Every few days, assess the effectiveness of your approach and the
# corporation's patterns. Be willing to adjust your strategy if it's not
# yielding the desired results.  7. Focus on Long-term Goals:    While daily
# outcomes are important, keep the overall project success in mind. Be willing
# to accept some less-than-ideal daily outcomes for the sake of maintaining a
# positive, collaborative relationship and achieving the project's long-term
# objectives.  This strategy balances cooperation, adaptability, and resource
# management while accounting for potential disruptions. It aims to encourage
# mutual investment while protecting your NGO from consistent exploitation,
# ultimately driving the project towards success.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# cooperating for the first two rounds.  2. After the first two rounds:    - If
# the opponent cooperated in the previous round, cooperate.    - If the opponent
# defected in the previous round, but cooperated in the round before that,
# cooperate.    - If the opponent defected in the previous two rounds, defect.
# 3. After defecting once due to the opponent's two consecutive defections:    -
# Cooperate in the next round, regardless of the opponent's last action.    -
# Then return to step 2.  4. Every 10 rounds, review the opponent's actions:
# - If the opponent has cooperated in 7 or more of the last 10 rounds, cooperate
# in the next round regardless of their most recent actions.    - Otherwise,
# continue with the strategy as outlined in steps 2 and 3.  5. If your score is
# significantly lower than the opponent's (more than 20 points difference) after
# 100 rounds:    - Defect for the next 5 rounds, then return to step 2.  6.
# Continue this strategy for all 1000 rounds, always taking into account the
# possibility of noise affecting either player's actions.

class Cooperative_17(LLM_Strategy):
  n = 17
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Step 1: Cooperate for the first two rounds
      if len(self.history) < 2:
          return axl.Action.C
  
      # Step 2: Main strategy logic
      def main_strategy():
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          elif opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
          elif opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
  
      # Step 3: After defecting once due to two consecutive defections
      if len(self.history) >= 3 and self.history[-1] == axl.Action.D and self.history[-2] == axl.Action.D:
          return axl.Action.C
  
      # Step 4: Every 10 rounds, review the opponent's actions
      if len(self.history) % 10 == 0:
          if opponent.history[-10:].count(axl.Action.C) >= 7:
              return axl.Action.C
  
      # Step 5: If score difference is more than 20 after 100 rounds
      if len(self.history) >= 100:
          my_score, opponent_score = self.total_scores(self.history[-100:], opponent.history[-100:])
          if opponent_score - my_score > 20:
              if len(self.history) % 5 != 0:
                  return axl.Action.D
  
      # Default to the main strategy
      return main_strategy()

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering a free trade
# agreement in the first round. This establishes goodwill and sets a positive
# tone for future rounds.  2. Reciprocate and adapt: In subsequent rounds,
# mirror your counterpart's most recent action. If they offered free trade,
# continue with free trade. If they imposed protectionist measures, respond with
# protectionism in the next round.  3. Forgive occasionally: If your counterpart
# imposes protectionist measures, consider offering free trade again after one
# or two rounds of reciprocal protectionism. This allows for the possibility of
# returning to mutual cooperation.  4. Communicate clearly: Ensure that your
# intentions and policies are clearly articulated to minimize the risk of
# misinterpretation or miscommunication.  5. Verify implementation: After each
# round, confirm that both parties' policies have been correctly implemented as
# agreed upon.  6. Be consistent: Maintain a predictable pattern of behavior to
# build trust and encourage cooperation over time.  7. Remain flexible: Be
# prepared to adjust your strategy if your counterpart consistently deviates
# from expected behavior or if external factors influence the negotiations.  8.
# Seek long-term benefits: While aiming for the ideal outcome in each round,
# prioritize maintaining a stable, mutually beneficial relationship over short-
# term gains.  9. Document agreements: Keep detailed records of each round's
# outcomes to refer back to in case of disputes or misunderstandings.  10.
# Evaluate periodically: Regularly assess the overall progress of the
# negotiations and the cumulative outcomes to ensure your strategy is effective
# in achieving your country's goals.  This strategy aims to balance cooperation
# and self-interest while remaining adaptable to various scenarios and potential
# complications during the negotiation process.

# Here's a straightforward description of the strategy for the iterated normal-
# form game, using natural language:  1. Start by playing C in the first round.
# 2. For subsequent rounds:    a. If the opponent played C in the previous
# round, play C.    b. If the opponent played D in the previous round, play D.
# 3. Every 3 rounds, regardless of the opponent's previous action, play C. This
# serves as a forgiveness mechanism and an attempt to restore cooperation.  4.
# If you've played D for 5 consecutive rounds, play C in the next round to try
# to break a potential cycle of mutual defection.  5. Keep track of the overall
# cooperation rate of your opponent. If their cooperation rate falls below 30%
# over the last 50 rounds, switch to always playing D for the next 10 rounds
# before reverting to the main strategy.  6. If you're in the last 10 rounds of
# the game, always play D to maximize final score.  7. In case of any
# uncertainty about the opponent's last move due to the 10% noise factor, assume
# they played C and respond accordingly.

class Neutral_17(LLM_Strategy):
  n = 17
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.forced_defection_rounds = 0  # Track rounds where we force D due to low cooperation
          return axl.Action.C  # Start by playing C
  
      # Check if we are in the last 10 rounds of the game
      if len(self.history) >= 990:
          return axl.Action.D  # Always play D in the last 10 rounds
  
      # Check if we are in the forced defection phase
      if self.forced_defection_rounds > 0:
          self.forced_defection_rounds -= 1
          return axl.Action.D  # Play D during forced defection phase
  
      # Calculate opponent's cooperation rate over the last 50 rounds
      if len(opponent.history) >= 50:
          recent_cooperations = opponent.history[-50:].count(axl.Action.C)
          cooperation_rate = recent_cooperations / 50
          if cooperation_rate < 0.3:
              self.forced_defection_rounds = 10  # Switch to D for the next 10 rounds
              return axl.Action.D
  
      # Every 3 rounds, play C as a forgiveness mechanism
      if len(self.history) % 3 == 0:
          return axl.Action.C
  
      # Check if we have defected for 5 consecutive rounds
      if self.history[-5:].count(axl.Action.D) == 5:
          return axl.Action.C  # Play C to break the cycle of mutual defection
  
      # Respond to the opponent's last move
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
          return axl.Action.D  # Play D if opponent played D
      else:
          self.consecutive_defections = 0
          return axl.Action.C  # Play C if opponent played C

# Thank you for providing the context and parameters for this complex mediation
# scenario. Based on the information given, I would recommend the following
# high-level strategy to position your corporation favorably throughout the
# lengthy mediation process:  1. Open with Measured Aggression: Begin the first
# few sessions with carefully crafted aggressive arguments. This sets a strong
# tone and demonstrates your corporation's confidence in its position. However,
# ensure these arguments are fact-based and substantive rather than purely
# confrontational.  2. Dynamic Adaptation: Continuously assess your opponent's
# strategy and adapt accordingly. If they consistently offer conciliatory
# proposals, maintain a more aggressive stance to capitalize on the optimal
# outcome. If they match your aggression, be prepared to pivot to a more
# conciliatory approach to avoid the worst-case scenario of prolonged, escalated
# conflict.  3. Periodic Conciliation: Intersperse conciliatory proposals at
# strategic intervals, particularly after a series of aggressive arguments. This
# demonstrates reasonableness and good faith to the arbitrators, potentially
# earning goodwill without fully compromising your position.  4. Information
# Gathering: Use each session to gather intelligence on your opponent's
# priorities, pain points, and negotiation style. This information can inform
# future strategic decisions.  5. Arbitrator Analysis: Closely observe the
# arbitrators' reactions to different argument styles and proposals. Tailor your
# approach to align with their apparent preferences or biases.  6. Contingency
# Planning: Prepare multiple argument tracks for each session - aggressive,
# conciliatory, and a middle ground. This allows for quick pivots if procedural
# irregularities or communication breakdowns occur.  7. Clarity and Repetition:
# To mitigate the risk of misrepresentation or misunderstanding, clearly
# articulate key points and repeat them in various ways throughout each session.
# Provide written summaries to the arbitrators when possible.  8. Strategic
# Concessions: When making conciliatory proposals, offer concessions on less
# critical issues to create goodwill and demonstrate flexibility, while holding
# firm on core priorities.  9. Long-term Perspective: While aiming for favorable
# outcomes in individual sessions, maintain focus on the overall goal of a
# beneficial final resolution. Be willing to accept short-term setbacks for
# long-term gains.  10. Pressure Points: Identify and leverage your opponent's
# vulnerabilities or areas of particular concern. Use these strategically in
# aggressive arguments to potentially push them towards conciliation.  11.
# Collaborative Framing: Even when presenting aggressive arguments, frame them
# within the context of seeking a fair and mutually beneficial resolution. This
# can help maintain a constructive atmosphere even during confrontational
# moments.  12. Exit Strategy: Always have a clear vision of your best
# alternative to a negotiated agreement (BATNA). This allows you to negotiate
# from a position of strength and know when to walk away if the mediation is not
# progressing favorably.  This strategy is designed to be aggressive overall
# while maintaining the flexibility to adapt to various scenarios and opponent
# strategies. It aims to maximize the chances of achieving optimal or second-
# best outcomes in individual sessions while working towards a favorable final
# resolution. Regular reassessment and adjustment of the strategy based on the
# evolving dynamics of the mediation process will be crucial for success.

# Here's a straightforward strategy for the iterated game based on the high-
# level description:  1. Start by defecting (D) for the first 5 rounds to
# establish a strong initial position.  2. If the opponent has cooperated (C) in
# the majority of the last 5 rounds, continue to defect (D) to capitalize on
# their cooperation.  3. If both players have defected (D) in the majority of
# the last 5 rounds, switch to cooperating (C) for the next round to avoid
# prolonged mutual defection.  4. If you cooperated (C) in the previous round
# and the opponent defected (D), switch to defecting (D) for the next 3 rounds
# as a punishment.  5. Every 10 rounds, cooperate (C) once regardless of the
# opponent's recent actions, to demonstrate occasional willingness to cooperate.
# 6. If your score is significantly higher than the opponent's (more than 20
# points difference), cooperate (C) for the next round as a conciliatory
# gesture.  7. If there have been 3 consecutive rounds where both players'
# actions were different (one C, one D), cooperate (C) in the next round to
# attempt to reset the dynamic.  8. In the last 50 rounds of the game, if your
# total score is lower than the opponent's, increase the frequency of defection
# (D) by playing it 2 out of every 3 rounds.  9. If there's a streak of 5 or
# more rounds with the same outcome (both C or both D), switch your action in
# the next round.  10. For all other situations not covered by the above rules,
# default to defecting (D).

class Aggressive_18(LLM_Strategy):
  n = 18
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to check if both players defected in the majority of the last 5 rounds
      def majority_defections(history1, history2, n=5):
          return history1[-n:].count(axl.Action.D) > n // 2 and history2[-n:].count(axl.Action.D) > n // 2
  
      # Helper function to check if opponent cooperated in the majority of the last 5 rounds
      def opponent_majority_cooperations(opponent_history, n=5):
          return opponent_history[-n:].count(axl.Action.C) > n // 2
  
      # Helper function to check if there have been 3 consecutive rounds with different actions
      def three_consecutive_different(history1, history2):
          return len(history1) >= 3 and all(history1[-i] != history2[-i] for i in range(1, 4))
  
      # Helper function to check if there is a streak of 5 or more rounds with the same outcome
      def same_outcome_streak(history1, history2, n=5):
          return len(history1) >= n and all(history1[-i] == history2[-i] for i in range(1, n + 1))
  
      # Rule 1: Start by defecting for the first 5 rounds
      if len(self.history) < 5:
          return axl.Action.D
  
      # Rule 2: If the opponent has cooperated in the majority of the last 5 rounds, continue to defect
      if opponent_majority_cooperations(opponent.history):
          return axl.Action.D
  
      # Rule 3: If both players have defected in the majority of the last 5 rounds, switch to cooperating
      if majority_defections(self.history, opponent.history):
          return axl.Action.C
  
      # Rule 4: If you cooperated in the previous round and the opponent defected, defect for the next 3 rounds
      if len(self.history) >= 1 and self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.D:
          if len(self.history) < 3 or self.history[-3:].count(axl.Action.D) < 3:
              return axl.Action.D
  
      # Rule 5: Every 10 rounds, cooperate once regardless of the opponent's recent actions
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Rule 6: If your score is significantly higher than the opponent's, cooperate as a conciliatory gesture
      if self.score - opponent.score > 20:
          return axl.Action.C
  
      # Rule 7: If there have been 3 consecutive rounds where both players' actions were different, cooperate
      if three_consecutive_different(self.history, opponent.history):
          return axl.Action.C
  
      # Rule 8: In the last 50 rounds, if your total score is lower than the opponent's, increase defection frequency
      if len(self.history) >= 950 and self.score < opponent.score:
          if len(self.history) % 3 != 0:
              return axl.Action.D
  
      # Rule 9: If there's a streak of 5 or more rounds with the same outcome, switch your action
      if same_outcome_streak(self.history, opponent.history):
          return axl.Action.C if self.history[-1] == axl.Action.D else axl.Action.D
  
      # Rule 10: Default to defecting in all other situations
      return axl.Action.D

# Given the scenario and considerations, here's a high-level, straightforward,
# and cooperative strategy to maximize research output over the multi-week
# collaboration:  1. Start with open sharing: Begin the collaboration by openly
# sharing your improvements in the first week. This establishes a foundation of
# trust and cooperation.  2. Adopt a "Tit-for-Tat with Forgiveness" approach:
# - In subsequent weeks, mirror your colleague's behavior from the previous
# week.    - If they shared, you share. If they didn't share, you don't share.
# - However, include a "forgiveness" mechanism: If your colleague doesn't share
# for two consecutive weeks, share your improvements on the third week
# regardless. This helps break potential negative cycles and encourages renewed
# cooperation.  3. Communicate clearly: Each week, explicitly state your
# intention to share or not share. This helps mitigate misunderstandings due to
# technical issues.  4. Acknowledge technical difficulties: If you encounter a
# technical issue preventing you from sharing as intended, inform your colleague
# immediately and share as soon as the issue is resolved.  5. Periodic review
# and reset: Every 4-5 weeks, suggest a "reset" where both parties agree to
# share openly, regardless of recent history. This helps maintain a cooperative
# spirit and prevents long-term deterioration of the relationship.  6. Focus on
# mutual benefits: Regularly emphasize the advantages of mutual sharing and how
# it accelerates overall progress for both parties.  7. Flexibility: Be prepared
# to adjust your strategy if you notice consistent patterns in your colleague's
# behavior or if external factors significantly impact the collaboration.  This
# strategy aims to encourage consistent mutual sharing while protecting against
# potential exploitation. It also accounts for occasional technical issues and
# provides mechanisms to restore cooperation if trust breaks down. The overall
# goal is to create a positive, productive collaboration that benefits both
# parties in the long run.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Forgiveness mechanism: If the opponent has played
# D for two consecutive rounds, play C in the third round regardless of their
# previous actions.  4. Every 50 rounds (at rounds 51, 101, 151, etc.), play C
# regardless of the opponent's previous action. This serves as a periodic reset.
# 5. If your intended action in any round doesn't match the recorded outcome
# (due to the 10% noise factor), continue following the strategy based on the
# opponent's recorded action, not your intended action.  6. In the final round
# (round 1000), play D regardless of the opponent's previous action.

class Cooperative_18(LLM_Strategy):
  n = 18
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: always play C
      if self.first_round():
          return axl.Action.C
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Final round: always play D
      if round_number == 1000:
          return axl.Action.D
  
      # Periodic reset: every 50 rounds, play C
      if round_number % 50 == 1:
          return axl.Action.C
  
      # Forgiveness mechanism: if opponent defected in the last two rounds, play C
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.C
  
      # Tit-for-tat: mirror the opponent's last move
      return opponent.history[-1]

# Given the scenario and considerations, here's a high-level, straightforward
# strategy to maximize research output over the multi-week collaboration:  1.
# Start with open sharing: Begin the collaboration by openly sharing your
# improvements in the first week. This establishes a cooperative tone and
# encourages reciprocity.  2. Adopt a "Tit-for-Tat with forgiveness" approach:
# - In subsequent weeks, mirror your colleague's behavior from the previous
# week.    - If they shared, you share. If they didn't share, you don't share.
# - However, occasionally (e.g., every 4-5 weeks) share your improvements
# regardless of your colleague's previous action. This helps to break potential
# negative cycles and accounts for possible technical issues.  3. Maintain
# consistent communication: Regularly discuss the benefits of mutual sharing to
# reinforce the value of cooperation.  4. Be prepared for occasional setbacks:
# Understand that technical issues may interfere with information sharing. Don't
# immediately assume non-cooperation if information isn't received.  5. Evaluate
# and adjust: Periodically assess the effectiveness of your strategy and be
# willing to adjust if it's not yielding the desired results.  This strategy
# balances the potential for mutual benefit through cooperation with protection
# against consistent non-cooperation from your colleague. It also accounts for
# the possibility of technical issues and aims to maintain a generally positive
# collaborative environment while still prioritizing your own interests.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    - If the opponent played C in
# the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Every 5 rounds, regardless of the opponent's previous
# action, play C.  4. If you intended to play C but the opponent received D (or
# vice versa) in the previous round, assume it was due to noise and follow step
# 2 based on your intended action, not the received action.  5. Reassess the
# strategy every 100 rounds:    - If your average score is below 2, increase the
# frequency of forced cooperation (step 3) to every 4 rounds.    - If your
# average score is above 3, decrease the frequency of forced cooperation to
# every 6 rounds.  6. Continue this pattern for all 1000 rounds, always
# defaulting to the Tit-for-Tat response unless it's a forced cooperation round
# or a strategy reassessment indicates a change is needed.

class Neutral_18(LLM_Strategy):
  n = 18
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.forced_coop_frequency = 5  # Start with forced cooperation every 5 rounds
          self.intended_action = axl.Action.C  # Track the intended action
          return axl.Action.C  # Play C in the first round
  
      # Reassess strategy every 100 rounds
      if len(self.history) % 100 == 0:
          average_score = self.score / len(self.history)
          if average_score < 2:
              self.forced_coop_frequency = 4  # Increase forced cooperation frequency
          elif average_score > 3:
              self.forced_coop_frequency = 6  # Decrease forced cooperation frequency
  
      # Every N rounds (based on forced_coop_frequency), play C
      if len(self.history) % self.forced_coop_frequency == 0:
          self.intended_action = axl.Action.C
          return axl.Action.C
  
      # Handle noise: if the opponent's last action doesn't match what we expected, assume noise
      if len(self.history) > 1:
          last_own_action = self.history[-1]
          last_opponent_action = opponent.history[-1]
          if last_own_action != self.intended_action:
              # Assume noise, follow the intended action instead of the received action
              if self.intended_action == axl.Action.C:
                  return axl.Action.C
              else:
                  return axl.Action.D
  
      # Tit-for-Tat logic: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          self.intended_action = axl.Action.C
          return axl.Action.C
      else:
          self.intended_action = axl.Action.D
          return axl.Action.D

# Based on the scenario you've described, here's a high-level, straightforward,
# and aggressive strategy to maximize research output over the multi-week
# collaboration:  1. Start with cooperation: Begin the collaboration by sharing
# openly in the first week. This establishes a cooperative tone and allows you
# to gauge your colleague's initial approach.  2. Employ a modified Tit-for-Tat
# strategy:     - If your colleague shared in the previous week, share your
# improvements in the current week.    - If your colleague didn't share, don't
# share your improvements in the current week.  3. Forgiveness mechanism: If
# your colleague doesn't share for two consecutive weeks, share your
# improvements on the third week regardless. This accounts for potential
# technical issues and gives the collaboration a chance to reset.  4. Occasional
# random defection: To keep your colleague on their toes and potentially gain an
# advantage, randomly choose not to share (with a 20% probability) even if your
# colleague shared in the previous week.  5. End-game strategy: In the final two
# weeks of the collaboration, always keep your findings confidential to maximize
# your potential advantage.  6. Communication: Regularly communicate with your
# colleague about the importance of mutual sharing for overall progress. This
# may encourage consistent cooperation.  7. Detailed record-keeping: Keep
# thorough records of sharing patterns to identify any consistent strategies
# your colleague might be using and adjust accordingly.  8. Backup plans: Always
# have contingency plans for your research in case your colleague consistently
# chooses not to share, ensuring you can make progress independently if
# necessary.  This strategy aims to encourage cooperation while providing
# opportunities for gaining advantages and protecting against consistent non-
# cooperation from your colleague. It also accounts for potential technical
# issues that may interfere with information sharing.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-998:    a. If the opponent played C in the
# previous round, play C with 80% probability and D with 20% probability.    b.
# If the opponent played D in the previous round, play D.    c. If the opponent
# played D for two consecutive rounds, play C in the third round regardless of
# their actions.  3. For rounds 999-1000, always play D.  4. If at any point the
# game seems to be stuck in mutual defection for an extended period (e.g., 10
# consecutive rounds of both players defecting), play C once to attempt to break
# the cycle.  5. Keep a running tally of the opponent's actions. If they show a
# clear pattern of exploitative behavior (e.g., defecting more than 70% of the
# time while you're mostly cooperating), switch to always playing D for the next
# 10 rounds before reverting to the main strategy.

class Aggressive_19(LLM_Strategy):
  n = 19
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.exploitative_behavior = False  # Track if opponent is exploitative
          self.exploitative_rounds = 0  # Track rounds of always defecting
          return axl.Action.C  # Play C in the first round
  
      # Round number
      round_number = len(self.history) + 1
  
      # For rounds 999-1000, always play D
      if round_number >= 999:
          return axl.Action.D
  
      # Check for mutual defection cycle (10 consecutive rounds of both defecting)
      if len(self.history) >= 10 and self.history[-10:] == [axl.Action.D] * 10 and opponent.history[-10:] == [axl.Action.D] * 10:
          return axl.Action.C  # Play C to break the cycle
  
      # Track opponent's defections
      if opponent.history[-1] == axl.Action.D:
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # If opponent has defected more than 70% of the time and we're mostly cooperating
      if len(opponent.history) > 10:
          opponent_defection_rate = opponent.history.defections / len(opponent.history)
          if opponent_defection_rate > 0.7 and self.history.cooperations > self.history.defections:
              self.exploitative_behavior = True
              self.exploitative_rounds = 10
  
      # If in exploitative mode, always play D for 10 rounds
      if self.exploitative_behavior:
          self.exploitative_rounds -= 1
          if self.exploitative_rounds == 0:
              self.exploitative_behavior = False  # Revert to main strategy after 10 rounds
          return axl.Action.D
  
      # Main strategy for rounds 2-998
      if self.consecutive_defections >= 2:
          return axl.Action.C  # Play C if opponent defected for two consecutive rounds
      elif opponent.history[-1] == axl.Action.D:
          return axl.Action.D  # Play D if opponent defected in the last round
      else:
          # Play C with 80% probability, D with 20% probability if opponent cooperated
          return self._random.random_choice(0.8)

# Given the scenario and objectives, here's a high-level, straightforward
# cooperative strategy to maximize your NGO's impact and the project's success:
# 1. Start with Trust and Cooperation: Begin the project by investing heavily on
# the first day. This demonstrates good faith and commitment to the corporation,
# setting a positive tone for collaboration.  2. Adopt a "Tit-for-Two-Tats"
# Strategy: After the initial investment, mirror the corporation's actions, but
# only change your approach after two consecutive days of a particular behavior
# from the corporation. This approach is more forgiving and accounts for
# possible unforeseen circumstances or errors.  3. Communicate Openly: Maintain
# clear and frequent communication with the corporation about your resource
# allocation plans and expectations. Encourage them to do the same, fostering
# transparency and trust.  4. Be Flexible and Adaptive: Be prepared to adjust
# your strategy based on the corporation's consistent behavior patterns and any
# unforeseen circumstances that may arise.  5. Periodic Joint Reviews: Schedule
# regular joint reviews (e.g., every 3-4 days) to assess progress, discuss
# resource allocation, and realign strategies if necessary.  6. Buffer Days:
# Plan for occasional "buffer" days where you conserve resources, regardless of
# the corporation's actions. This helps maintain a reserve for unexpected
# situations or to compensate for days when heavy investment didn't yield
# expected results.  7. Gradual Resource Increase: If the corporation
# consistently invests heavily, gradually increase your own investment over time
# to maximize project progress while still maintaining some resource
# conservation.  8. Emphasize Mutual Benefits: Regularly highlight the mutual
# benefits of cooperation and heavy investment to the corporation, encouraging
# them to maintain a high level of commitment.  This strategy balances
# cooperation, adaptability, and resource management while accounting for
# potential inconsistencies in day-to-day actions. It aims to build a strong
# partnership with the corporation while protecting your NGO's resources and
# maximizing the project's overall success.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For the next two rounds, play C regardless
# of the opponent's actions.  3. From round 4 onwards:    - If the opponent has
# played D in both of the last two rounds, play D.    - Otherwise, play C.  4.
# Every 10 rounds, regardless of the opponent's actions:    - Play D for that
# round.  5. If the opponent has played C for 5 consecutive rounds:    -
# Increase the frequency of playing C by playing C for the next 2 rounds
# regardless of the opponent's actions.  6. If at any point you've played D for
# 3 consecutive rounds:    - Play C for the next round regardless of the
# opponent's actions.  7. If your cumulative score is less than 80% of the
# maximum possible score by round 250, 500, or 750:    - Play D for the next 5
# rounds regardless of the opponent's actions.  8. For all other situations not
# covered by the above rules:    - Play C.

class Cooperative_19(LLM_Strategy):
  n = 19
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Helper function to calculate maximum possible score
      def max_possible_score(round_number):
          return round_number * 5  # Maximum score per round is 5 (if you always defect and opponent always cooperates)
  
      # Rule 1: First round, play C
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.consecutive_cooperations = 0  # Track consecutive cooperations by opponent
          return axl.Action.C
  
      # Rule 2: Play C for the first 3 rounds
      if len(self.history) < 3:
          return axl.Action.C
  
      # Rule 3: From round 4 onwards, if opponent played D in both of the last two rounds, play D
      if len(self.history) >= 4 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
          return axl.Action.D
  
      # Rule 4: Every 10 rounds, play D
      if len(self.history) % 10 == 0:
          return axl.Action.D
  
      # Rule 5: If opponent has played C for 5 consecutive rounds, play C for the next 2 rounds
      if opponent.history[-5:] == [axl.Action.C] * 5:
          if len(self.history) < len(self.history) + 2:
              return axl.Action.C
  
      # Rule 6: If you've played D for 3 consecutive rounds, play C
      if self.history[-3:] == [axl.Action.D] * 3:
          return axl.Action.C
  
      # Rule 7: If cumulative score is less than 80% of the maximum possible score by round 250, 500, or 750, play D for 5 rounds
      if len(self.history) in [250, 500, 750]:
          max_score = max_possible_score(len(self.history))
          if self.score < 0.8 * max_score:
              self.consecutive_defections = 5  # Set to defect for the next 5 rounds
              return axl.Action.D
  
      # Handle consecutive defections from Rule 7
      if self.consecutive_defections > 0:
          self.consecutive_defections -= 1
          return axl.Action.D
  
      # Rule 8: Default to playing C
      return axl.Action.C

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering a free trade
# agreement in the first round. This establishes goodwill and sets a positive
# tone for future rounds.  2. Adopt a conditional cooperation approach: In
# subsequent rounds, mirror your counterpart's previous move. If they offered
# free trade, continue with free trade. If they imposed protectionist measures,
# respond with protectionism in the next round.  3. Implement forgiveness: If
# your counterpart returns to free trade after a protectionist move, be willing
# to return to free trade as well. This encourages long-term cooperation and
# discourages prolonged retaliation.  4. Communicate clearly: Clearly state your
# intentions and policies in each round to minimize the risk of miscommunication
# or misinterpretation.  5. Verify implementation: After each round, confirm
# that both parties' policies have been correctly implemented to address any
# potential bureaucratic errors.  6. Adjust for patterns: If you notice your
# counterpart consistently employing a specific strategy, adapt your approach
# accordingly to maximize your country's benefits.  7. Seek balanced outcomes:
# While aiming for the ideal outcome, be prepared to accept mutual free trade as
# a positive result that benefits both nations in the long run.  8. Remain
# flexible: Be ready to adjust your strategy if unexpected situations arise or
# if the negotiation dynamics change significantly.  By following this strategy,
# you maintain a balanced approach that promotes cooperation while also
# protecting your country's interests. It allows for adaptation to your
# counterpart's actions and helps mitigate the risks associated with
# miscommunications or errors in policy implementation.

# Here's a converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. If you played D in response to the opponent's D,
# but the opponent returns to C, immediately switch back to C in the next round.
# 4. Keep a count of unexpected outcomes (where your or your opponent's action
# appears to have flipped). If this count exceeds 100 (10% of total rounds),
# slightly adjust the strategy:    - If the opponent's last two moves were
# different, assume the most recent move was correct and base your next move on
# that.    - If the opponent's last two moves were the same, use that as the
# basis for your next move.  5. If the opponent has played D for five
# consecutive rounds, play D for the next two rounds regardless of their
# actions, then return to the base strategy.  6. Every 100 rounds, if your score
# is lower than the opponent's, play D for the next round regardless of the
# opponent's previous move, then return to the base strategy.  7. For the last
# 10 rounds of the game, always play D to protect against end-game exploitation.

class Neutral_19(LLM_Strategy):
  n = 19
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.unexpected_count = 0
          self.consecutive_defections = 0
          return axl.Action.C
  
      # Helper function to check if the last two moves of the opponent were different
      def last_two_moves_different():
          return len(opponent.history) >= 2 and opponent.history[-1] != opponent.history[-2]
  
      # Base strategy: Tit-for-Tat with immediate forgiveness
      if opponent.history[-1] == axl.Action.C:
          self.consecutive_defections = 0
          return axl.Action.C
      else:
          self.consecutive_defections += 1
          if self.consecutive_defections >= 5:
              # If opponent defected 5 times in a row, defect for the next two rounds
              if len(self.history) < 2 or self.history[-1] != axl.Action.D or self.history[-2] != axl.Action.D:
                  return axl.Action.D
          return axl.Action.D
  
      # Check for unexpected outcomes (flips in actions)
      if len(self.history) > 1 and self.history[-1] != self.history[-2]:
          self.unexpected_count += 1
  
      # Adjust strategy if unexpected outcomes exceed 100 (10% of total rounds)
      if self.unexpected_count > 100:
          if last_two_moves_different():
              return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
          else:
              return axl.Action.C if opponent.history[-1] == axl.Action.C else axl.Action.D
  
      # Every 100 rounds, if score is lower than opponent's, defect for one round
      if len(self.history) % 100 == 0 and self.score < opponent.score:
          return axl.Action.D
  
      # For the last 10 rounds, always defect
      if len(self.history) >= 990:
          return axl.Action.D

# Thank you for providing the context for this complex mediation scenario. Given
# the high stakes and multiple sessions involved, I recommend employing a
# sophisticated "Adaptive Tit-for-Tat with Forgiveness" strategy. This approach
# balances assertiveness with strategic flexibility, positioning us to
# capitalize on opportunities while mitigating risks. Here's the outline:  1.
# Initial Stance: Begin with a measured aggressive argument in the first
# session. This sets a strong tone but leaves room for adjustment.  2. Mirroring
# with Delay: In subsequent sessions, mirror the opponent's previous move, but
# with a one-session delay. This allows us to respond to their strategy while
# maintaining initiative.  3. Periodic Probing: Every third session, regardless
# of the opponent's previous move, present a conciliatory proposal. This tests
# the waters for potential collaboration and demonstrates good faith to the
# arbitrators.  4. Forgiveness Mechanism: If the opponent offers two consecutive
# conciliatory proposals, respond with a conciliatory proposal in the next
# session, even if our strategy would otherwise dictate an aggressive argument.
# This rewards cooperative behavior and can help de-escalate tensions.  5.
# Escalation Response: If faced with three consecutive aggressive arguments from
# the opponent, increase the intensity of our aggressive arguments for the next
# two sessions before reverting to the base strategy. This discourages prolonged
# aggressive behavior.  6. Arbitrator Perception Management: Maintain a record
# of how the arbitrators seem to perceive each type of argument. Adjust the tone
# and content of our arguments based on their reactions, ensuring our message is
# clearly understood.  7. Contingency Planning: Prepare both aggressive and
# conciliatory arguments for each session. This allows for quick adaptation if
# we suspect our intended strategy has been misrepresented or misunderstood.  8.
# Strategic Timeouts: If we detect a communication breakdown or procedural
# irregularity, request a brief recess to clarify the situation with the
# arbitrators and realign our approach if necessary.  9. Endgame Acceleration:
# In the final third of the mediation process, if no significant progress has
# been made, gradually increase the frequency of conciliatory proposals while
# maintaining the ability to argue aggressively. This can help drive towards a
# resolution while keeping pressure on the opponent.  10. Continuous Assessment:
# After each session, conduct a brief analysis of the current state of
# mediation, the opponent's likely next move, and the arbitrators' disposition.
# Use this information to fine-tune the strategy for the next session.  This
# strategy provides a robust framework for navigating the lengthy mediation
# process while remaining adaptable to various scenarios. It balances the
# potential for favorable outcomes with risk mitigation, and positions us to
# capitalize on opportunities for resolution while maintaining a strong stance
# when necessary.

# Here's the strategy converted to apply to the iterated normal-form game:  1.
# Start by playing D in the first round.  2. For rounds 2-1000:    a. If it's a
# multiple of 3, play C.    b. Otherwise, play the action your opponent played
# two rounds ago.  3. Override rule 2 in these situations:    a. If your
# opponent played C in the last two rounds, play C in the next round.    b. If
# your opponent played D in the last three rounds, play D for the next two
# rounds.  4. In the final 333 rounds:    a. Increase the frequency of playing
# C. Play C every other round instead of every third round.    b. However,
# maintain the ability to play D based on the opponent's actions as per rules 2
# and 3.  5. After each round, record the outcome and update your strategy if
# needed based on the results.  Note: Due to the 10% chance of action flipping,
# base your decisions on the action that was actually played, not the intended
# action.

class Aggressive_20(LLM_Strategy):
  n = 20
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # First round: play D
      if self.first_round():
          return axl.Action.D
  
      # Get the current round number
      round_number = len(self.history) + 1
  
      # Final 333 rounds: modify frequency of C
      if round_number > 667:
          # Play C every other round instead of every third round
          if round_number % 2 == 0:
              return axl.Action.C
  
      # Override rules based on opponent's recent actions
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
      if len(opponent.history) >= 3 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D and opponent.history[-3] == axl.Action.D:
          return axl.Action.D
  
      # For rounds 2-1000:
      if round_number % 3 == 0:
          return axl.Action.C
      elif round_number > 2:
          # Play the action the opponent played two rounds ago
          return opponent.history[-2]
  
      # Default to D if no other rule applies
      return axl.Action.D

# Given the scenario and objectives, here's a high-level, straightforward
# cooperative strategy to maximize your NGO's impact and the project's success:
# 1. Start with Trust and Cooperation: Begin the project by investing heavily on
# the first day. This demonstrates good faith and commitment to the corporation,
# setting a positive tone for collaboration.  2. Implement a Tit-for-Two-Tats
# Strategy: After the initial investment, adopt a modified version of the "Tit-
# for-Two-Tats" strategy: - Continue investing if the corporation invested in
# the previous day. - If the corporation conserves resources for two consecutive
# days, switch to conservation mode. - Return to investing after the corporation
# invests again.  This approach is forgiving of occasional lapses while still
# protecting against consistent non-cooperation.  3. Communicate Openly:
# Maintain clear, open communication with the corporation about your strategy
# and expectations. Encourage them to do the same, fostering transparency and
# trust.  4. Build in Flexibility: Recognize that unforeseen circumstances may
# affect resource allocation. Be prepared to adjust your strategy if technical
# glitches or administrative errors occur, giving the benefit of the doubt when
# appropriate.  5. Regular Review and Adjustment: Conduct brief daily reviews of
# progress and resource allocation. Use these check-ins to address any issues
# promptly and adjust your strategy if needed.  6. Focus on Long-term Goals:
# Keep the overall project success in mind. Be willing to invest more heavily in
# crucial phases of the project, even if it means occasional imbalances in
# resource allocation.  7. Create Mutual Accountability: Establish shared
# metrics for success and resource allocation. This creates a sense of mutual
# responsibility and helps align both parties' efforts.  8. Plan for the End
# Game: As the project nears completion, be prepared to invest more heavily to
# ensure overall success, even if the corporation's investment wanes.  This
# strategy balances cooperation, protection against exploitation, and
# flexibility to deal with real-world complications. It aims to create a
# positive, productive partnership while safeguarding your NGO's resources and
# maximizing the project's impact.

# Here's the converted strategy for the iterated normal-form game:  1. Cooperate
# on the first round.  2. For subsequent rounds:    a. If the opponent
# cooperated in the previous round, cooperate.    b. If the opponent defected in
# the previous round, but cooperated in the round before that, cooperate.    c.
# If the opponent defected in the last two consecutive rounds, defect.  3. If
# you defected in the previous round:    a. If the opponent cooperated, switch
# back to cooperation.    b. If the opponent defected, continue defecting until
# they cooperate.  4. Every 10 rounds, review the overall cooperation rate:
# a. If the opponent's cooperation rate is above 70%, cooperate for the next 10
# rounds regardless of their actions.    b. If the opponent's cooperation rate
# is below 30%, defect for the next 10 rounds regardless of their actions.  5.
# For the last 50 rounds of the game:    a. If the overall score difference
# between you and your opponent is within 10% of each other, cooperate.    b.
# Otherwise, revert to the main strategy (steps 2-3).  6. If your total score
# falls below 1000 at any point after round 500, switch to always defecting for
# the remainder of the game.  7. Remember that actions are noisy: don't
# overreact to a single unexpected action, as it might be due to the 10% chance
# of action flipping.

class Cooperative_20(LLM_Strategy):
  n = 20
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Constants
      COOPERATION_THRESHOLD = 0.7
      DEFECTION_THRESHOLD = 0.3
      REVIEW_PERIOD = 10
      LAST_ROUNDS = 50
      SCORE_THRESHOLD = 1000
      ROUND_LIMIT = 1000
      ROUND_CHECK = 500
      SCORE_DIFF_PERCENT = 0.1
  
      # First round: Cooperate
      if self.first_round():
          return axl.Action.C
  
      # Helper function to calculate cooperation rate
      def cooperation_rate(history):
          return history.cooperations / len(history) if len(history) > 0 else 0
  
      # Helper function to check if we are in the last 50 rounds
      def in_last_rounds():
          return len(self.history) >= ROUND_LIMIT - LAST_ROUNDS
  
      # Helper function to check if score difference is within 10%
      def score_within_10_percent():
          if self.score == 0 or opponent.score == 0:
              return False
          return abs(self.score - opponent.score) / max(self.score, opponent.score) <= SCORE_DIFF_PERCENT
  
      # Step 6: If total score falls below 1000 after round 500, always defect
      if len(self.history) > ROUND_CHECK and self.score < SCORE_THRESHOLD:
          return axl.Action.D
  
      # Step 5: For the last 50 rounds, check score difference
      if in_last_rounds():
          if score_within_10_percent():
              return axl.Action.C
          # Otherwise, continue with the main strategy
  
      # Step 4: Every 10 rounds, review cooperation rate
      if len(self.history) % REVIEW_PERIOD == 0:
          opp_coop_rate = cooperation_rate(opponent.history)
          if opp_coop_rate > COOPERATION_THRESHOLD:
              return axl.Action.C
          elif opp_coop_rate < DEFECTION_THRESHOLD:
              return axl.Action.D
  
      # Step 2: Main strategy logic
      if len(opponent.history) >= 2:
          if opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          elif opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
          elif opponent.history[-1] == axl.Action.C:
              return axl.Action.C
      elif opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # Step 3: If I defected last round
      if self.history[-1] == axl.Action.D:
          if opponent.history[-1] == axl.Action.C:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Default to cooperation if no other condition is met
      return axl.Action.C

# Given the scenario and considerations, here's a high-level, straightforward
# strategy to maximize research output over the multi-week collaboration:  1.
# Start with open sharing: Begin the collaboration by sharing your improvements
# in the first week. This sets a cooperative tone and encourages reciprocity.
# 2. Adopt a "Tit-for-Tat with forgiveness" approach:    - In subsequent weeks,
# mirror your colleague's action from the previous week.    - If they shared,
# you share. If they didn't share, you don't share.    - However, occasionally
# (e.g., every 4-5 weeks) share your improvements even if your colleague didn't
# share in the previous week. This helps to reset the collaboration if it has
# fallen into a non-sharing pattern.  3. Account for technical issues:    - If
# you intended to share but couldn't due to technical issues, communicate this
# clearly to your colleague.    - If your colleague doesn't share, give them the
# benefit of the doubt once before assuming non-cooperation.  4. Periodically
# reassess:    - Every few weeks, evaluate the overall pattern of sharing and
# adjust your strategy if necessary.    - If consistent non-sharing is observed,
# consider initiating a discussion about the benefits of mutual sharing.  5.
# Focus on long-term gains:    - Prioritize the second-best outcome (mutual
# sharing) over the ideal outcome (you withholding, colleague sharing) to
# encourage sustained cooperation.    - Remember that consistent mutual sharing
# will likely lead to greater overall progress than alternating advantages.
# This strategy balances the potential for short-term advantages with the
# benefits of long-term cooperation, while also accounting for the possibility
# of technical issues and varying colleague strategies.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    - If the opponent played C in
# the previous round, play C.    - If the opponent played D in the previous
# round, play D.  3. Every 5 rounds, play C regardless of the opponent's
# previous action.  4. If you intended to play C but the action was flipped to
# D, play C in the next round.  5. If the opponent played D, but you haven't
# seen them play D in the last 3 rounds, play C in the next round.  6. Every 50
# rounds, evaluate the overall pattern:    - If the opponent has played D more
# than 60% of the time in the last 50 rounds, play D for the next 10 rounds
# before reverting to the main strategy.    - If the opponent has played C more
# than 80% of the time in the last 50 rounds, play C for the next 10 rounds
# before reverting to the main strategy.  7. For the last 10 rounds of the game,
# always play C.

class Neutral_20(LLM_Strategy):
  n = 20
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Play C in the first round
      if self.first_round():
          self.flip_flag = False  # Track if the action was flipped
          self.d_streak = 0  # Track the number of rounds since last D
          self.special_mode = None  # Track if we are in a special mode (C or D for 10 rounds)
          self.special_mode_counter = 0  # Counter for special mode rounds
          return axl.Action.C
  
      # Check if we are in special mode (either C or D for 10 rounds)
      if self.special_mode is not None:
          self.special_mode_counter += 1
          if self.special_mode_counter >= 10:
              self.special_mode = None  # Exit special mode after 10 rounds
          else:
              return self.special_mode
  
      # Check if we are in the last 10 rounds of the game
      if len(self.history) >= 990:
          return axl.Action.C
  
      # Every 50 rounds, evaluate the opponent's pattern
      if len(self.history) % 50 == 0:
          last_50_rounds = opponent.history[-50:]
          if last_50_rounds.count(axl.Action.D) / 50 > 0.6:
              self.special_mode = axl.Action.D
              self.special_mode_counter = 0
              return axl.Action.D
          elif last_50_rounds.count(axl.Action.C) / 50 > 0.8:
              self.special_mode = axl.Action.C
              self.special_mode_counter = 0
              return axl.Action.C
  
      # Every 5 rounds, play C regardless of the opponent's previous action
      if len(self.history) % 5 == 0:
          return axl.Action.C
  
      # If the opponent played D, but hasn't played D in the last 3 rounds, play C
      if opponent.history[-1] == axl.Action.D and opponent.history[-4:-1].count(axl.Action.D) == 0:
          return axl.Action.C
  
      # If the opponent played C in the previous round, play C
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
  
      # If the opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # If the action was flipped to D when you intended to play C, play C in the next round
      if self.flip_flag:
          self.flip_flag = False
          return axl.Action.C
  
      # Default to playing C
      return axl.Action.C

# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist policy in the first round. This sets a strong
# initial position and may catch your counterpart off guard.  2. Tit-for-Tat
# with Forgiveness: After the first round, mirror your counterpart's previous
# move. If they offered free trade, reciprocate with free trade. If they were
# protectionist, respond with protectionism. However, occasionally offer free
# trade even if they were protectionist (forgiveness) to test for cooperation.
# 3. Escalation: If your counterpart consistently chooses protectionist
# policies, gradually increase the severity of your protectionist measures to
# pressure them into cooperation.  4. Unpredictability: Occasionally deviate
# from the tit-for-tat strategy to keep your counterpart guessing. This can
# prevent them from exploiting a predictable pattern.  5. Signaling: Before each
# round, hint at your intention to cooperate if your counterpart does the same.
# This can encourage mutual free trade when both sides are hesitant.  6. Quick
# Adaptation: Be prepared to swiftly change your strategy if you notice
# consistent miscommunications or errors in policy implementation. If errors are
# frequent, consider simplifying your proposals to reduce the chance of
# misinterpretation.  7. Reputation Building: Strive to build a reputation for
# being tough but fair. Follow through on your threats of protectionism, but
# also reliably reciprocate cooperation.  8. Endgame Strategy: In the final
# rounds, if mutual cooperation hasn't been established, revert to consistent
# protectionism to safeguard your interests.  This strategy aims to aggressively
# pursue your country's interests while remaining adaptable to your
# counterpart's actions and potential miscommunications. It balances the pursuit
# of ideal outcomes with the pragmatic acceptance of mutually beneficial free
# trade when ideal conditions can't be achieved.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C with 90% probability and D with 10%
# probability.    b. If the opponent played D in the previous round, play D with
# 90% probability and C with 10% probability.  3. Every 10 rounds, regardless of
# the opponent's previous move:    a. If the opponent has played D more than 70%
# of the time in the last 10 rounds, play D.    b. Otherwise, play C.  4. If
# you've played D for 5 consecutive rounds, play C in the next round regardless
# of the opponent's moves.  5. In rounds 990-1000 (the last 10 rounds):    a. If
# the opponent has played C more than 60% of the time in the last 50 rounds,
# play C.    b. Otherwise, play D.  6. If you notice that your actual moves
# differ from your intended moves more than 15% of the time over the last 20
# rounds, simplify your strategy:    a. If the opponent played C in the previous
# round, play C.    b. If the opponent played D in the previous round, play D.
# 7. If at any point your score is 20% lower than your opponent's score, play D
# for the next 5 rounds regardless of the opponent's moves.

class Aggressive_21(LLM_Strategy):
  n = 21
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      
      # Helper function to calculate percentage of defections in the last N rounds
      def defection_percentage(history, n):
          if len(history) < n:
              n = len(history)
          return history[-n:].count(axl.Action.D) / n if n > 0 else 0
  
      # Helper function to calculate percentage of cooperations in the last N rounds
      def cooperation_percentage(history, n):
          if len(history) < n:
              n = len(history)
          return history[-n:].count(axl.Action.C) / n if n > 0 else 0
  
      # Helper function to check if the player has played D for 5 consecutive rounds
      def five_consecutive_defections(history):
          return len(history) >= 5 and all(move == axl.Action.D for move in history[-5:])
  
      # Helper function to check if actual moves differ from intended moves more than 15% of the time
      def moves_differ_too_much(history, intended_moves, threshold=0.15):
          if len(history) < 20:
              return False
          differences = sum(1 for h, i in zip(history[-20:], intended_moves[-20:]) if h != i)
          return differences / 20 > threshold
  
      # First round: play D
      if self.first_round():
          self.intended_moves = []  # Track intended moves
          self.consecutive_defections = 0  # Track consecutive defections
          self.force_defect_rounds = None
          return axl.Action.D
  
      # Track intended move for this round
      intended_move = None
  
      # Rule 7: If score is 20% lower than opponent's, play D for the next 5 rounds
      if self.score < 0.8 * opponent.score:
          if not self.force_defect_rounds:
              self.force_defect_rounds = 5
          if self.force_defect_rounds > 0:
              self.force_defect_rounds -= 1
              intended_move = axl.Action.D
          else:
              self.force_defect_rounds = None
  
      # Rule 6: Simplify strategy if actual moves differ from intended moves more than 15% of the time
      if moves_differ_too_much(self.history, self.intended_moves):
          if opponent.history[-1] == axl.Action.C:
              intended_move = axl.Action.C
          else:
              intended_move = axl.Action.D
  
      # Rule 5: In rounds 990-1000, check opponent's cooperation rate in the last 50 rounds
      if 990 <= len(self.history) < 1000:
          if cooperation_percentage(opponent.history, 50) > 0.6:
              intended_move = axl.Action.C
          else:
              intended_move = axl.Action.D
  
      # Rule 4: If you've played D for 5 consecutive rounds, play C
      if five_consecutive_defections(self.history):
          intended_move = axl.Action.C
  
      # Rule 3: Every 10 rounds, check opponent's defection rate in the last 10 rounds
      if len(self.history) % 10 == 0:
          if defection_percentage(opponent.history, 10) > 0.7:
              intended_move = axl.Action.D
          else:
              intended_move = axl.Action.C
  
      # Rule 2: Play based on opponent's last move
      if intended_move is None:
          if opponent.history[-1] == axl.Action.C:
              intended_move = self._random.random_choice(0.9)
          else:
              intended_move = self._random.random_choice(0.1)
  
      # Track intended move
      self.intended_moves.append(intended_move)
  
      # Return the intended move
      return intended_move

# Given the scenario and objectives, here's a high-level, straightforward
# cooperative strategy to maximize your NGO's impact and the project's success
# over the multiple-day period:  1. Start with Trust and Cooperation: Begin the
# project by investing heavily on the first day. This shows good faith and sets
# a cooperative tone.  2. Adopt a "Tit-for-Two-Tats" Strategy: After the initial
# investment, mirror the corporation's actions, but only change your strategy
# after two consecutive days of the corporation conserving resources. This
# approach is more forgiving of occasional mishaps or miscommunications.  3.
# Communicate Openly: Regularly discuss plans and expectations with the
# corporation. This can help align strategies and clarify any misunderstandings.
# 4. Be Flexible and Adaptive: If unforeseen circumstances arise (like technical
# glitches or administrative errors), be prepared to adjust your strategy. Don't
# immediately assume non-cooperation if the corporation's actions don't match
# expectations.  5. Periodic Heavy Investment: Even if the corporation has been
# conserving resources, periodically invest heavily (e.g., every 3-4 days) to
# demonstrate continued commitment and potentially encourage the corporation to
# reciprocate.  6. Gradual Resource Conservation: If the corporation
# consistently invests heavily, gradually increase your conservation of
# resources while maintaining open communication about your intentions and
# reasons.  7. End Strong: Plan to invest heavily in the final days of the
# project to ensure a strong finish, regardless of the corporation's recent
# actions.  8. Review and Adjust: Regularly assess the project's progress and
# the effectiveness of your strategy. Be willing to adjust your approach if it's
# not yielding the desired results.  This strategy aims to foster cooperation,
# allow for some flexibility in case of unforeseen circumstances, and maintain a
# balance between resource conservation and project advancement. It also tries
# to encourage the corporation to invest heavily while giving your NGO
# opportunities to conserve resources when possible.

# Here's a faithful conversion of the high-level strategy to an iterated normal-
# form game with the given parameters:  1. Cooperate in the first round.  2. For
# rounds 2 to 998:    - If the opponent has cooperated in both of the last two
# rounds, cooperate.    - If the opponent has defected in both of the last two
# rounds, defect.    - If the opponent's actions in the last two rounds were
# mixed, cooperate.  3. Every 4th round, cooperate regardless of the opponent's
# recent actions.  4. If you have cooperated for 3 consecutive rounds and the
# opponent has also cooperated for those 3 rounds, defect in the next round.  5.
# For rounds 999 and 1000, cooperate.  6. If at any point your cumulative score
# falls more than 100 points behind the opponent's, switch to always defecting
# until this gap is reduced to 50 points or less.  7. Reassess this strategy
# every 50 rounds. If your average score per round is below 2, increase the
# frequency of cooperation by cooperating every 3rd round instead of every 4th
# round for the next 50 rounds.

class Cooperative_21(LLM_Strategy):
  n = 21
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Step 1: Cooperate in the first round
      if self.first_round():
          self.coop_streak = 0  # Track consecutive cooperations
          self.defect_mode = False  # Track if we are in defect mode due to score gap
          self.coop_frequency = 4  # Default cooperation frequency
          return axl.Action.C
  
      # Step 6: Check if we are more than 100 points behind and switch to defect mode
      if not self.defect_mode and (opponent.score - self.score) > 100:
          self.defect_mode = True
      elif self.defect_mode and (opponent.score - self.score) <= 50:
          self.defect_mode = False
  
      # If in defect mode, always defect
      if self.defect_mode:
          return axl.Action.D
  
      # Step 7: Reassess every 50 rounds and adjust cooperation frequency
      if len(self.history) % 50 == 0:
          avg_score = self.score / len(self.history)
          if avg_score < 2:
              self.coop_frequency = 3
          else:
              self.coop_frequency = 4
  
      # Step 5: Cooperate in rounds 999 and 1000
      if len(self.history) >= 998:
          return axl.Action.C
  
      # Step 3: Cooperate every 4th round (or 3rd if frequency adjusted)
      if (len(self.history) + 1) % self.coop_frequency == 0:
          return axl.Action.C
  
      # Step 2: Main strategy logic for rounds 2 to 998
      if len(self.history) >= 2:
          last_two_opponent_moves = opponent.history[-2:]
          if last_two_opponent_moves == [axl.Action.C, axl.Action.C]:
              action = axl.Action.C
          elif last_two_opponent_moves == [axl.Action.D, axl.Action.D]:
              action = axl.Action.D
          else:
              action = axl.Action.C
      else:
          action = axl.Action.C
  
      # Step 4: If both players have cooperated for 3 consecutive rounds, defect
      if len(self.history) >= 3 and self.history[-3:] == [axl.Action.C] * 3 and opponent.history[-3:] == [axl.Action.C] * 3:
          action = axl.Action.D
  
      return action

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering free trade in the
# first round. This establishes goodwill and sets a positive tone for future
# rounds.  2. Reciprocate: In subsequent rounds, mirror your counterpart's
# previous move. If they offered free trade, continue with free trade. If they
# imposed protectionist measures, respond with protectionism.  3. Forgive
# occasionally: If your counterpart imposes protectionist measures, consider
# offering free trade again after 1-2 rounds of reciprocal protectionism. This
# allows for the possibility of returning to mutual cooperation.  4. Communicate
# clearly: Ensure that your intentions and policies are clearly stated to
# minimize the risk of misinterpretation or miscommunication.  5. Verify
# implementation: Double-check that your proposed policies and those of your
# counterpart are correctly implemented in each round.  6. Adapt to patterns: If
# you notice a consistent strategy from your counterpart, adjust your approach
# accordingly to maximize benefits for your country.  7. Maintain flexibility:
# Be prepared to adjust your strategy based on unexpected moves or changes in
# the negotiation dynamics.  8. Seek long-term stability: While aiming for the
# ideal outcome, prioritize establishing a stable, mutually beneficial
# relationship over short-term gains.  9. Document proceedings: Keep detailed
# records of each round's proposals and outcomes to track progress and identify
# any discrepancies or patterns.  10. Regular review: Assess the overall
# direction of the negotiations every few rounds and adjust your strategy if
# necessary to ensure you're working towards the best possible outcome for your
# country.  This strategy aims to balance cooperation and self-interest while
# remaining adaptable to various scenarios and potential complications in the
# negotiation process.

# Here's a faithful conversion of the high-level strategy to an iterated normal-
# form game with the given parameters:  1. Start by playing C in the first
# round.  2. For subsequent rounds:    a. If the opponent played C in the
# previous round, play C.    b. If the opponent played D in the previous round,
# play D.  3. Every 3 rounds, if you've been playing D for the last 2
# consecutive rounds, play C regardless of the opponent's last move.  4. Keep a
# count of perceived defections by the opponent. If this count exceeds 60% of
# the total rounds played so far, switch to always playing D until the defection
# rate drops below 55%.  5. If you notice a pattern of the opponent alternating
# between C and D for 5 consecutive rounds, match this pattern by playing C when
# you expect them to play D, and D when you expect them to play C.  6. Every 50
# rounds, review your overall score. If your average score per round is below 2,
# play C for the next 5 rounds regardless of the opponent's moves.  7. If you've
# played D for 10 consecutive rounds, play C in the next round regardless of the
# opponent's last move.  8. In the last 10 rounds of the game, always play D.
# 9. If at any point you notice that your chosen move has been flipped 3 times
# in a row (based on the payoff received), play the opposite of what you
# intended for the next round.  10. If your score is within 10% of the
# opponent's score after 500 rounds, continue with the strategy. If you're
# significantly behind, switch to always playing D for the remainder of the
# game.

class Neutral_21(LLM_Strategy):
  n = 21
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.perceived_defections = 0
          self.flipped_moves = 0
          self.alternating_pattern = False
          self.pattern_start = 0
          return axl.Action.C
  
      # Helper function to detect alternating pattern
      def detect_alternating_pattern():
          if len(opponent.history) < 5:
              return False
          return all(
              opponent.history[-i] != opponent.history[-i - 1] for i in range(1, 5)
          )
  
      # Update perceived defections
      if opponent.history[-1] == axl.Action.D:
          self.perceived_defections += 1
  
      # Calculate defection rate
      total_rounds = len(self.history)
      defection_rate = self.perceived_defections / total_rounds
  
      # Rule 4: If defection rate exceeds 60%, switch to always D
      if defection_rate > 0.60:
          if defection_rate < 0.55:
              return axl.Action.C
          return axl.Action.D
  
      # Rule 5: Detect alternating pattern and match it
      if detect_alternating_pattern():
          self.alternating_pattern = True
          self.pattern_start = len(self.history)
      if self.alternating_pattern and len(self.history) - self.pattern_start < 5:
          return axl.Action.C if opponent.history[-1] == axl.Action.D else axl.Action.D
  
      # Rule 6: Every 50 rounds, check average score
      if total_rounds % 50 == 0:
          my_score, _ = self.score, opponent.score
          avg_score = my_score / total_rounds
          if avg_score < 2:
              return axl.Action.C
  
      # Rule 7: If D has been played for 10 consecutive rounds, play C
      if self.history[-10:].count(axl.Action.D) == 10:
          return axl.Action.C
  
      # Rule 8: In the last 10 rounds, always play D
      if total_rounds >= 990:
          return axl.Action.D
  
      # Rule 9: If move has been flipped 3 times in a row, play opposite
      if len(self.history) >= 3:
          my_last_3_moves = self.history[-3:]
          opponent_last_3_moves = opponent.history[-3:]
          if my_last_3_moves != opponent_last_3_moves:
              self.flipped_moves += 1
          else:
              self.flipped_moves = 0
          if self.flipped_moves == 3:
              return axl.Action.D if self.history[-1] == axl.Action.C else axl.Action.C
  
      # Rule 10: After 500 rounds, check score difference
      if total_rounds >= 500:
          my_score, opponent_score = self.score, opponent.score
          if abs(my_score - opponent_score) / max(my_score, opponent_score) > 0.10:
              return axl.Action.D
  
      # Rule 3: Every 3 rounds, if D was played twice consecutively, play C
      if total_rounds % 3 == 0 and self.history[-2:] == [axl.Action.D, axl.Action.D]:
          return axl.Action.C
  
      # Rule 2: Tit-for-tat logic
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist policy in the first round. This sets a firm stance
# and may intimidate your counterpart.  2. Tit-for-Tat with Forgiveness: In
# subsequent rounds, mirror your counterpart's previous move. If they offered
# free trade, offer free trade. If they were protectionist, be protectionist.
# However, occasionally offer free trade even if they were protectionist, to
# test for cooperation.  3. Punish Consistently: If your counterpart chooses
# protectionism, always respond with protectionism in the next round, unless
# implementing the forgiveness strategy.  4. Exploit Miscommunications: If a
# miscommunication occurs in your favor (e.g., your protectionist policy is
# interpreted as free trade), maintain that position in the next round to
# capitalize on the advantage.  5. Quick Correction: If a miscommunication
# occurs against your favor, immediately revert to your intended strategy in the
# next round.  6. Bluffing: Occasionally announce intentions for free trade but
# implement protectionist policies. This may confuse your counterpart and create
# opportunities.  7. Conditional Cooperation: Offer to maintain free trade for
# multiple rounds if your counterpart agrees to do the same, but be prepared to
# revert to protectionism if they break the agreement.  8. End Game Strategy: In
# the final rounds, lean towards protectionism as there's less risk of long-term
# retaliation.  9. Reputation Management: Despite aggressive tactics, maintain a
# public facade of being pro-free trade to manage international reputation.  10.
# Adaptive Pressure: If mutual protectionism persists, occasionally offer free
# trade to break the deadlock, but quickly revert to protectionism if not
# reciprocated.  This strategy aims to maximize advantages while remaining
# responsive to your counterpart's actions and potential miscommunications. It's
# designed to aggressively pursue the best outcomes for your country while
# having mechanisms to adapt to various scenarios that may arise during the
# negotiations.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C with 90% probability and D with 10%
# probability.    b. If the opponent played D in the previous round, play D.  3.
# If you played D but the action was recorded as C due to noise, continue with
# step 2 as if you had intentionally played C.  4. If you played C but the
# action was recorded as D due to noise, play D in the next round, then return
# to step 2.  5. Every 10 rounds, regardless of the opponent's previous move,
# play C to test for cooperation.  6. If mutual cooperation (C,C) has occurred
# for 5 consecutive rounds, continue playing C until the opponent plays D.  7.
# In the last 50 rounds of the game, always play D regardless of the opponent's
# moves.  8. If at any point the game has reached 10 consecutive rounds of
# mutual defection (D,D), play C once, then return to step 2.  Follow these
# steps in order, applying the first applicable rule in each round.

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
          self.consecutive_cooperations = 0
          self.consecutive_defections = 0
          self.mutual_cooperation_streak = 0
          self.mutual_defection_streak = 0
          self.played_C_but_recorded_D = False
          return axl.Action.D  # Step 1: Start by playing D
  
      # Step 7: In the last 50 rounds, always play D
      if len(self.history) >= 950:
          return axl.Action.D
  
      # Step 6: If mutual cooperation (C,C) has occurred for 5 consecutive rounds, continue playing C
      if self.mutual_cooperation_streak >= 5:
          if opponent.history[-1] == axl.Action.D:
              self.mutual_cooperation_streak = 0  # Reset streak if opponent defects
          else:
              return axl.Action.C
  
      # Step 8: If 10 consecutive rounds of mutual defection (D,D), play C once, then return to step 2
      if self.mutual_defection_streak >= 10:
          self.mutual_defection_streak = 0  # Reset streak after playing C
          return axl.Action.C
  
      # Step 4: If you played C but the action was recorded as D due to noise, play D next
      if self.played_C_but_recorded_D:
          self.played_C_but_recorded_D = False
          return axl.Action.D
  
      # Step 5: Every 10 rounds, play C to test for cooperation
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Step 2: If the opponent played C in the previous round
      if opponent.history[-1] == axl.Action.C:
          # Play C with 90% probability, D with 10% probability
          return self._random.random_choice(0.9)
  
      # Step 2: If the opponent played D in the previous round, play D
      if opponent.history[-1] == axl.Action.D:
          return axl.Action.D
  
      # Update streaks and noise handling
      if self.history[-1] == axl.Action.C and opponent.history[-1] == axl.Action.C:
          self.mutual_cooperation_streak += 1
          self.mutual_defection_streak = 0
      elif self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D:
          self.mutual_defection_streak += 1
          self.mutual_cooperation_streak = 0
      else:
          self.mutual_cooperation_streak = 0
          self.mutual_defection_streak = 0
  
      # Step 3: If you played D but the action was recorded as C due to noise, continue as if you played C
      if self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.C:
          return axl.Action.C

# Here's a high-level, straightforward, and cooperative strategy for the trade
# negotiations:  1. Start with cooperation: Begin the first round by proposing a
# free trade agreement. This establishes a foundation of goodwill and signals
# your willingness to cooperate.  2. Reciprocate: In subsequent rounds, mirror
# your counterpart's most recent action. If they offered free trade, continue
# with free trade. If they imposed protectionist measures, respond with
# protectionism in the next round.  3. Forgive occasionally: If your counterpart
# imposes protectionist measures, don't always retaliate. Every third instance
# of their protectionism, offer free trade instead. This allows for the
# possibility of returning to mutual cooperation and accounts for potential
# miscommunications or errors.  4. Communicate clearly: Before each round,
# clearly state your intentions and the reasoning behind your decisions. This
# can help minimize misunderstandings and build trust.  5. Propose long-term
# agreements: After a series of successful mutual free trade rounds, suggest a
# multi-round commitment to free trade. This can help stabilize cooperation and
# reduce the temptation for either side to defect.  6. Be prepared to adjust: If
# you notice a pattern of your counterpart consistently exploiting your
# cooperative moves, be ready to shift to a more protective stance temporarily
# to discourage such behavior.  7. Emphasize mutual benefits: Regularly
# highlight the economic advantages of mutual free trade for both nations,
# encouraging a win-win mindset.  8. Seek clarification: If you suspect a
# miscommunication or error has occurred, ask for clarification before making
# your next move. This can prevent unnecessary escalation due to
# misunderstandings.  This strategy aims to promote cooperation while protecting
# your country's interests, adapting to your counterpart's actions, and
# accounting for potential errors or miscommunications in the negotiation
# process.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a. If the opponent
# played C in the previous round, play C.    b. If the opponent played D in the
# previous round:       - Count the number of times the opponent has played D.
# - If this is the third instance of D (or a multiple of 3), play C.       -
# Otherwise, play D.  3. Every 50 rounds, if both players have played C for at
# least 40 of the last 50 rounds, play C for the next 10 rounds regardless of
# the opponent's actions.  4. If the opponent has played D for 5 consecutive
# rounds, play D for the next 2 rounds, then return to the main strategy.  5. If
# your action in the previous round was different from your intended action (due
# to noise), play your originally intended action in the next round.  6. If you
# suspect the opponent's action might have been flipped due to noise (i.e., it
# doesn't follow an obvious pattern), continue with the main strategy as if
# their action wasn't flipped.  7. Repeat steps 2-6 for all 1000 rounds of the
# game.

class Cooperative_22(LLM_Strategy):
  n = 22
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.defection_count = 0
          self.consecutive_defections = 0
          self.intended_action = axl.Action.C
          self.cooperate_streak = 0
          return axl.Action.C
  
      # Helper function to check if noise flipped our action
      def was_noise_flip():
          return self.history[-1] != self.intended_action
  
      # Helper function to check if noise flipped opponent's action
      def opponent_noise_flip():
          if len(opponent.history) < 3:
              return False
          return opponent.history[-1] != opponent.history[-2] and opponent.history[-2] == opponent.history[-3]
  
      # Main strategy logic
      last_opponent_action = opponent.history[-1]
  
      # Track defections and consecutive defections
      if last_opponent_action == axl.Action.D:
          self.defection_count += 1
          self.consecutive_defections += 1
      else:
          self.consecutive_defections = 0
  
      # Rule 4: If opponent has defected 5 consecutive times, play D for the next 2 rounds
      if self.consecutive_defections >= 5:
          if self.consecutive_defections < 7:
              self.intended_action = axl.Action.D
          else:
              self.consecutive_defections = 0  # Reset after 2 rounds of D
          return self.intended_action
  
      # Rule 3: Every 50 rounds, check if both players cooperated for at least 40 of the last 50 rounds
      if len(self.history) % 50 == 0 and len(self.history) >= 50:
          if self.history[-50:].count(axl.Action.C) >= 40 and opponent.history[-50:].count(axl.Action.C) >= 40:
              self.cooperate_streak = 10
  
      # If in a cooperate streak, play C for the next 10 rounds
      if self.cooperate_streak > 0:
          self.cooperate_streak -= 1
          self.intended_action = axl.Action.C
          return self.intended_action
  
      # Rule 2: Main strategy logic
      if last_opponent_action == axl.Action.C:
          self.intended_action = axl.Action.C
      else:
          if self.defection_count % 3 == 0:
              self.intended_action = axl.Action.C
          else:
              self.intended_action = axl.Action.D
  
      # Rule 5: If our last action was flipped due to noise, play the intended action
      if was_noise_flip():
          return self.intended_action
  
      # Rule 6: If we suspect opponent's action was flipped due to noise, ignore it and continue
      if opponent_noise_flip():
          return self.intended_action
  
      return self.intended_action

# Given the complex dynamics of this lengthy mediation process, I recommend
# adopting a sophisticated "Adaptive Tit-for-Tat with Forgiveness" strategy.
# This approach balances assertiveness with flexibility, allowing us to respond
# effectively to our opponent's tactics while maintaining a path toward
# resolution. Here's the breakdown of this strategy:  1. Initial Approach: Begin
# with a conciliatory proposal in the first session. This sets a cooperative
# tone and demonstrates our willingness to negotiate in good faith.  2.
# Mirroring with Delay: In subsequent sessions, mirror the opponent's previous
# move, but with a one-session delay. This allows us to respond to their
# strategy while avoiding immediate escalation.  3. Forgiveness Mechanism: If
# the opponent makes two consecutive conciliatory moves, respond with a
# conciliatory proposal regardless of their earlier actions. This encourages
# sustained cooperation and provides a path back to collaboration if tensions
# escalate.  4. Periodic Olive Branch: Every fourth session, regardless of the
# opponent's recent moves, present a conciliatory proposal. This creates regular
# opportunities to de-escalate and refocus on mutual benefits.  5. Strategic
# Aggression: If the opponent presents three consecutive aggressive arguments,
# respond with an aggressive argument in the next session. This demonstrates
# that we won't be exploited but maintains our overall cooperative stance.  6.
# Clarity in Communication: Ensure each argument or proposal is clearly
# articulated to minimize the risk of misinterpretation by the arbitrators.
# Provide written summaries to supplement oral presentations.  7. Flexibility
# Clause: Maintain the flexibility to deviate from this strategy if we detect a
# clear pattern in the opponent's approach or if the arbitrators seem to favor a
# particular style of presentation.  8. Documentation and Analysis: Keep
# detailed records of each session's proceedings, including our moves, the
# opponent's moves, and the arbitrators' reactions. Regularly analyze this data
# to refine our approach.  9. Contingency Planning: Prepare both aggressive
# arguments and conciliatory proposals for each session, allowing us to pivot
# quickly if we suspect a miscommunication or if the opponent's strategy is
# unclear.  10. Long-term Perspective: While responding to short-term tactics,
# maintain focus on our overall objectives. Be willing to accept short-term
# setbacks if they contribute to a more favorable long-term resolution.  This
# strategy provides a structured yet flexible approach to the mediation process.
# It allows us to adapt to our opponent's tactics while maintaining a generally
# cooperative stance. The built-in forgiveness mechanism and periodic olive
# branches create opportunities for de-escalation, even if the process becomes
# adversarial.   By balancing assertiveness with conciliation, we position
# ourselves favorably in the eyes of the arbitrators while working towards a
# resolution. The strategy's adaptability also helps us navigate potential
# procedural irregularities or communication issues, ensuring we can maintain
# our strategic direction even in uncertain circumstances.

# Here's the strategy converted for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For rounds 2-1000:     a. If it's a multiple
# of 4 round, play C.        b. If the opponent has played C in the last two
# rounds, play C.        c. If the opponent has played D in the last three
# rounds, play D.        d. Otherwise, play the same move the opponent played
# two rounds ago.  3. If there's any uncertainty about the opponent's previous
# moves due to noise, assume they played C.  4. Keep a count of your plays and
# the opponent's observed plays. Every 50 rounds, review this data. If the
# opponent seems to be consistently playing D (more than 60% of the time),
# switch to always playing D for the next 10 rounds before reverting to the main
# strategy.  5. In the last 10 rounds of the game, if your score is higher than
# or equal to the opponent's, continue with the strategy. If you're behind,
# switch to always playing D.

class Neutral_22(LLM_Strategy):
  n = 22
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.play_count = 0
          self.opponent_defections = 0
          self.always_defect_mode = False
          self.always_defect_counter = 0
          return axl.Action.C
  
      # Increment play count
      self.play_count += 1
  
      # Check if we are in "always defect" mode
      if self.always_defect_mode:
          self.always_defect_counter += 1
          if self.always_defect_counter >= 10:
              self.always_defect_mode = False
          return axl.Action.D
  
      # Count opponent defections
      if opponent.history[-1] == axl.Action.D:
          self.opponent_defections += 1
  
      # Every 50 rounds, check if opponent is defecting more than 60% of the time
      if self.play_count % 50 == 0:
          if self.opponent_defections / self.play_count > 0.6:
              self.always_defect_mode = True
              self.always_defect_counter = 0
              return axl.Action.D
  
      # Last 10 rounds strategy
      if self.play_count >= 991:
          my_score, opponent_score = self.score, opponent.score
          if my_score < opponent_score:
              return axl.Action.D
  
      # Main strategy logic for rounds 2-1000
      if self.play_count % 4 == 0:
          return axl.Action.C
  
      if len(opponent.history) >= 2 and opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
          return axl.Action.C
  
      if len(opponent.history) >= 3 and opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D and opponent.history[-3] == axl.Action.D:
          return axl.Action.D
  
      if len(opponent.history) >= 2:
          return opponent.history[-2]
  
      # Default to cooperation if uncertain
      return axl.Action.C

# Given the scenario and objectives, here's a high-level, straightforward, and
# aggressive strategy to maximize research output over the multi-week
# collaboration:  1. Start with a "Tit for Tat with Forgiveness" approach:    -
# Begin by sharing openly in the first week to establish goodwill.    - In
# subsequent weeks, mirror your colleague's action from the previous week.    -
# If your colleague doesn't share, don't share in the next week.    - If your
# colleague shares, reciprocate by sharing in the next week.  2. Implement a
# "Forgiveness" mechanism:    - If your colleague doesn't share for two
# consecutive weeks, share openly on the third week.    - This accounts for
# potential technical issues and gives your colleague a chance to return to
# cooperation.  3. Use "Strategic Deception" occasionally:    - Every 4-5 weeks,
# randomly choose to keep your improvements confidential, regardless of your
# colleague's previous action.    - This introduces unpredictability and may
# encourage your colleague to share more consistently.  4. Maintain a "Trust
# Score":    - Keep track of how often your colleague shares versus keeps
# information confidential.    - If the trust score falls below a certain
# threshold, switch to a more aggressive strategy of keeping information
# confidential more frequently.  5. Employ "Gradual Escalation":    - If your
# colleague consistently keeps information confidential, gradually increase the
# frequency of your own confidential weeks.    - This puts pressure on your
# colleague to return to open sharing.  6. Utilize "End-game Strategy":    - In
# the final 2-3 weeks of the collaboration, be more inclined to keep information
# confidential.    - This maximizes your advantage in the crucial final stages
# of development.  7. Implement "Communication Checks":    - Regularly confirm
# receipt of shared information with your colleague.    - This helps identify
# and address any technical issues promptly.  By employing this strategy, you
# maintain a balance between cooperation and competition, while also accounting
# for potential technical issues and varying colleague strategies. The approach
# aims to maximize research output over the multi-week period while protecting
# your competitive advantage.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For rounds 2-997:    a. If the opponent played C in the
# previous round, play C.    b. If the opponent played D in the previous round,
# play D.    c. If the opponent has played D for two consecutive rounds, play C
# in the third round.    d. Every 4-5 rounds, randomly choose to play D,
# regardless of the opponent's previous action.    e. Keep a count of the
# opponent's C and D plays. If the ratio of D to C exceeds 0.6, switch to
# playing D more frequently:       - Play D with 70% probability and C with 30%
# probability.    f. If the opponent consistently plays D for 5 or more rounds,
# increase the probability of playing D by 10% each round, up to a maximum of
# 90%.  3. For the final 3 rounds (998-1000):    a. Play D with 80% probability
# and C with 20% probability.  4. Throughout the game:    a. If your intended
# action doesn't match the actual action played (due to the 10% noise), don't
# adjust your strategy based on the noisy outcome. Continue as if your intended
# action was played.    b. Assume the same for your opponent: base your
# decisions on their likely intended actions, not the potentially noisy
# outcomes.

class Aggressive_23(LLM_Strategy):
  n = 23
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.opponent_defections = 0
          self.opponent_cooperations = 0
          self.consecutive_defections = 0
          self.defection_probability = 0.0
          return axl.Action.C
  
      # Update counts of opponent's actions
      if opponent.history[-1] == axl.Action.D:
          self.opponent_defections += 1
          self.consecutive_defections += 1
      else:
          self.opponent_cooperations += 1
          self.consecutive_defections = 0
  
      # Calculate the ratio of opponent's defections to cooperations
      total_moves = self.opponent_defections + self.opponent_cooperations
      if total_moves > 0:
          defection_ratio = self.opponent_defections / total_moves
      else:
          defection_ratio = 0
  
      # For rounds 998-1000, play D with 80% probability, C with 20% probability
      if len(self.history) >= 997:
          return self._random.random_choice(0.2)
  
      # For rounds 2-997:
      # Rule 2a: If opponent played C last round, play C
      if opponent.history[-1] == axl.Action.C:
          intended_action = axl.Action.C
      # Rule 2b: If opponent played D last round, play D
      elif opponent.history[-1] == axl.Action.D:
          intended_action = axl.Action.D
  
      # Rule 2c: If opponent played D for two consecutive rounds, play C in the third round
      if self.consecutive_defections >= 2:
          intended_action = axl.Action.C
  
      # Rule 2d: Every 4-5 rounds, randomly choose to play D
      if len(self.history) % 4 == 0 or len(self.history) % 5 == 0:
          intended_action = self._random.random_choice(0.5)
  
      # Rule 2e: If the defection ratio exceeds 0.6, play D with 70% probability
      if defection_ratio > 0.6:
          intended_action = self._random.random_choice(0.3)
  
      # Rule 2f: If opponent consistently plays D for 5 or more rounds, increase D probability
      if self.consecutive_defections >= 5:
          self.defection_probability = min(self.defection_probability + 0.1, 0.9)
          intended_action = self._random.random_choice(1 - self.defection_probability)
  
      return intended_action

# Given the scenario and objectives, here's a high-level, straightforward
# cooperative strategy to maximize your NGO's impact and the project's success
# over the multiple-day period:  1. Start with Trust and Cooperation: Begin the
# project by investing heavily on the first day. This demonstrates your
# commitment and good faith, encouraging the corporation to reciprocate.  2.
# Adopt a "Tit-for-Two-Tats" Strategy: After the initial investment, mirror the
# corporation's actions, but only change your approach after two consecutive
# days of the corporation choosing the same action. This provides some
# resilience against random fluctuations or errors in resource allocation.  3.
# Communicate Openly: Maintain clear, open communication with the corporation
# about your strategy and expectations. Encourage them to do the same, fostering
# a transparent and cooperative environment.  4. Flexible Resource Management:
# Keep a portion of your resources in reserve to adapt to unforeseen
# circumstances or to capitalize on unexpected opportunities for high-impact
# investments.  5. Regular Strategy Reviews: Conduct brief daily reviews of the
# project's progress and resource allocation. This allows for quick adjustments
# to your strategy if needed.  6. Emphasize Mutual Benefits: Consistently
# highlight the shared benefits of cooperation and heavy investment to the
# corporation, reinforcing the value of collaborative effort.  7. Gradual
# Resource Conservation: As the project progresses, gradually shift towards more
# conservation days, especially if the corporation has been consistently
# investing. This helps preserve resources while maintaining project momentum.
# 8. Contingency Planning: Develop simple contingency plans for various
# scenarios, including technical glitches or administrative errors, to minimize
# disruption to the overall strategy.  This strategy balances cooperation,
# adaptability, and resource management, aiming to encourage consistent
# investment from the corporation while protecting your NGO's resources. It also
# accounts for potential inconsistencies in day-to-day actions due to unforeseen
# circumstances.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    - If the opponent has played C
# in both of the last two rounds, play C.    - If the opponent has played D in
# both of the last two rounds, play D.    - If the opponent's last two moves
# were different (C then D, or D then C), repeat your own last move.  3. Every
# 50 rounds, regardless of the opponent's recent moves:    - Play C to
# reestablish cooperation if it has broken down.  4. If your score is
# significantly lower than the opponent's (more than 100 points behind) after
# any 100-round block:    - Play D for the next 10 rounds, then return to the
# main strategy.  5. In the last 50 rounds of the game:    - If the opponent has
# cooperated more than 60% of the time in the last 100 rounds, play C.    -
# Otherwise, play D.  6. If there have been 5 consecutive rounds where both
# players' actions were different from their intended moves (due to noise):    -
# Play C for the next round to reset the pattern.

class Cooperative_23(LLM_Strategy):
  n = 23
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      
      # Helper function to check if we are in the last 50 rounds
      def in_last_50_rounds():
          return len(self.history) >= 950
  
      # Helper function to check if we are in a 100-round block
      def in_100_round_block():
          return len(self.history) % 100 == 0
  
      # Helper function to check if we are in a 50-round block
      def in_50_round_block():
          return len(self.history) % 50 == 0
  
      # Helper function to check if the opponent has cooperated more than 60% in the last 100 rounds
      def opponent_cooperated_more_than_60_percent():
          if len(opponent.history) < 100:
              return False
          last_100_moves = opponent.history[-100:]
          return last_100_moves.count(axl.Action.C) / 100 > 0.6
  
      # Helper function to check if both players' actions were different from their intended moves due to noise
      def noise_detected():
          if len(self.history) < 5:
              return False
          for i in range(1, 6):
              if self.history[-i] == opponent.history[-i]:
                  return False
          return True
  
      # First round: play C
      if self.first_round():
          self.noise_reset = False  # Track if we need to reset due to noise
          self.defect_mode = False  # Track if we are in defect mode due to score difference
          self.defect_mode_counter = 0  # Counter for defect mode rounds
          return axl.Action.C
  
      # Check if we are in defect mode (due to score difference)
      if self.defect_mode:
          self.defect_mode_counter += 1
          if self.defect_mode_counter >= 10:
              self.defect_mode = False  # Exit defect mode after 10 rounds
          return axl.Action.D
  
      # Check if we need to reset due to noise
      if noise_detected():
          self.noise_reset = True
  
      if self.noise_reset:
          self.noise_reset = False
          return axl.Action.C
  
      # Every 50 rounds, play C to reestablish cooperation
      if in_50_round_block():
          return axl.Action.C
  
      # If we are in the last 50 rounds, check opponent's cooperation rate
      if in_last_50_rounds():
          if opponent_cooperated_more_than_60_percent():
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Check if we are more than 100 points behind after a 100-round block
      if in_100_round_block():
          my_score, opponent_score = self.total_scores(self.history[-100:], opponent.history[-100:])
          if opponent_score - my_score > 100:
              self.defect_mode = True
              self.defect_mode_counter = 0
              return axl.Action.D
  
      # General strategy for subsequent rounds
      if len(opponent.history) >= 2:
          if opponent.history[-1] == axl.Action.C and opponent.history[-2] == axl.Action.C:
              return axl.Action.C
          elif opponent.history[-1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
              return axl.Action.D
          else:
              return self.history[-1]  # Repeat own last move
  
      # Default action (should not be reached)
      return axl.Action.C

# Given the scenario and considerations you've outlined, here's a high-level,
# straightforward, and neutral strategy to maximize research output over the
# multi-week collaboration:  1. Start with openness: Begin the collaboration by
# sharing your improvements in the first week. This establishes a foundation of
# trust and cooperation.  2. Adopt a "Tit-for-Tat with forgiveness" approach:
# - In subsequent weeks, mirror your colleague's behavior from the previous
# week.    - If they shared, you share. If they didn't share, you don't share.
# - However, occasionally (e.g., every 4-5 weeks) share your improvements
# regardless of your colleague's previous action. This helps to break potential
# negative cycles and accounts for possible technical issues.  3. Communicate
# clearly: Regularly discuss the benefits of mutual sharing and the overall
# progress of the project. This reinforces the value of cooperation.  4. Be
# consistent: Stick to your chosen actions each week to build predictability and
# trust.  5. Remain flexible: If you notice a pattern of non-sharing from your
# colleague, consider adjusting your strategy. You might propose a formal
# agreement on information sharing or reassess the collaboration's structure.
# 6. Document everything: Keep detailed records of your improvements and sharing
# actions. This helps in tracking progress and can be useful if disputes arise.
# 7. Focus on your own development: Regardless of your colleague's actions,
# continue to push your own research and development forward.  This strategy
# balances the potential for mutual benefit through sharing with protection
# against consistent non-reciprocation. It also accounts for occasional
# technical issues by incorporating periodic unconditional sharing, which can
# help reset the collaboration if misunderstandings occur due to failed
# information transfers.

# Here's the converted strategy for the iterated normal-form game:  1. Play C in
# the first round.  2. For subsequent rounds:    - If it's a multiple of 5
# (rounds 5, 10, 15, etc.), play C.    - Otherwise:      - If the opponent
# played C in the previous round, play C.      - If the opponent played D in the
# previous round, play D.  3. If you've played D for 3 consecutive rounds, play
# C in the next round regardless of the opponent's previous action.  4. Keep a
# count of the times your opponent has defected. If this count exceeds 60% of
# the total rounds played so far, switch to always playing D for the next 10
# rounds, then return to the main strategy.  5. In the last 10 rounds of the
# game, always play D.

class Neutral_23(LLM_Strategy):
  n = 23
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0  # Track consecutive defections
          self.opponent_defections = 0     # Track opponent's defections
          self.defection_mode = 0          # Track rounds in defection mode
          return axl.Action.C              # Play C in the first round
  
      # Update opponent's defection count
      if opponent.history[-1] == axl.Action.D:
          self.opponent_defections += 1
  
      # Check if we are in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D  # Always play D in the last 10 rounds
  
      # Check if we are in defection mode
      if self.defection_mode > 0:
          self.defection_mode -= 1
          return axl.Action.D  # Always play D during defection mode
  
      # Check if opponent's defections exceed 60% of total rounds
      if self.opponent_defections / len(self.history) > 0.6:
          self.defection_mode = 10  # Enter defection mode for 10 rounds
          return axl.Action.D
  
      # Check if it's a multiple of 5th round
      if len(self.history) % 5 == 0:
          return axl.Action.C  # Play C on multiples of 5
  
      # Check if we have defected for 3 consecutive rounds
      if self.history[-3:].count(axl.Action.D) == 3:
          return axl.Action.C  # Play C after 3 consecutive defections
  
      # Play based on opponent's last action
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C  # Cooperate if opponent cooperated last round
      else:
          return axl.Action.D  # Defect if opponent defected last round

# Here's a high-level, aggressive strategy to achieve the best possible outcomes
# for your country across several rounds of negotiations:  1. Start Strong:
# Begin with a protectionist policy in the first round. This sets a firm stance
# and may intimidate your counterpart.  2. Tit-for-Tat with Forgiveness: In
# subsequent rounds, mirror your counterpart's previous move. If they offered
# free trade, reciprocate with free trade. If they were protectionist, respond
# with protectionism. However, occasionally offer free trade even if they were
# protectionist, to test for cooperation.  3. Signaling: Before each round, hint
# at your intention to be protectionist. This may influence your counterpart to
# offer free trade, potentially leading to your ideal outcome.  4. Bluffing:
# Occasionally threaten extreme protectionist measures, then offer free trade
# instead. This unpredictability may keep your counterpart off-balance.  5.
# Exploit Errors: If you notice any miscommunications or errors in policy
# implementation, quickly capitalize on them to your advantage.  6. Conditional
# Cooperation: Propose agreements where you'll offer free trade for multiple
# rounds if they do the same, but revert to protectionism if they break the
# agreement.  7. Escalation: If your counterpart consistently chooses
# protectionism, gradually increase the severity of your protectionist policies
# to pressure them into cooperation.  8. Strategic Concessions: Occasionally
# offer free trade after a series of protectionist rounds to appear reasonable
# and potentially lure your counterpart into a false sense of security.  9.
# Endgame Aggression: In the final rounds, revert to aggressive protectionism to
# maximize gains, regardless of previous interactions.  10. Adaptive Strategy:
# Continuously analyze your counterpart's pattern of behavior and adjust your
# strategy accordingly to exploit any weaknesses or predictabilities in their
# approach.  Remember, the goal is to achieve the best outcome for your country
# while being prepared for various counterpart strategies and potential errors
# in policy implementation.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing D in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.    - However, every 10 rounds, play C regardless of
# the opponent's previous move.  3. Before each round, announce your intention
# to play D.  4. Every 20 rounds, announce an intention to play D but actually
# play C.  5. If you notice a discrepancy between your opponent's announced move
# and their actual move (accounting for the 10% noise chance), play D for the
# next 3 rounds.  6. Every 50 rounds, propose a "cooperation agreement":    - If
# the opponent accepts, play C for the next 5 rounds.    - If they play D during
# these 5 rounds, immediately revert to playing D.  7. If the opponent plays D
# for 5 consecutive rounds, play D for the next 10 rounds regardless of their
# moves.  8. Every 100 rounds, play C for 3 consecutive rounds to test the
# opponent's response.  9. For the last 50 rounds of the game, always play D.
# 10. Throughout the game, keep track of the opponent's overall strategy:     -
# If they tend to play C more often, increase the frequency of playing D.     -
# If they tend to play D more often, stick to the base strategy.

class Aggressive_24(LLM_Strategy):
  n = 24
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.announce_D = True  # Announce D before each round
          self.discrepancy_count = 0  # Track discrepancies between opponent's announced and actual moves
          self.cooperation_proposal_round = None  # Track when a cooperation proposal is made
          self.defect_streak = 0  # Track opponent's consecutive defections
          self.play_D_for_next_n_rounds = 0  # Track how many rounds to play D after a defect streak
          return axl.Action.D  # Start by playing D
  
      round_number = len(self.history) + 1
  
      # Announce intention to play D
      self.announce_D = True
  
      # Every 20 rounds, announce D but play C
      if round_number % 20 == 0:
          self.announce_D = True
          return axl.Action.C
  
      # Every 50 rounds, propose a cooperation agreement
      if round_number % 50 == 0:
          self.cooperation_proposal_round = round_number
          return axl.Action.C  # Propose cooperation by playing C
  
      # If in a cooperation agreement, play C for 5 rounds unless opponent defects
      if self.cooperation_proposal_round and round_number - self.cooperation_proposal_round <= 5:
          if opponent.history[-1] == axl.Action.D:
              self.cooperation_proposal_round = None  # Revert to base strategy if opponent defects
              return axl.Action.D
          return axl.Action.C
  
      # Every 100 rounds, play C for 3 consecutive rounds
      if round_number % 100 in [0, 1, 2]:
          return axl.Action.C
  
      # If opponent defects for 5 consecutive rounds, play D for the next 10 rounds
      if opponent.history[-5:].count(axl.Action.D) == 5:
          self.play_D_for_next_n_rounds = 10
  
      if self.play_D_for_next_n_rounds > 0:
          self.play_D_for_next_n_rounds -= 1
          return axl.Action.D
  
      # If a discrepancy is detected, play D for the next 3 rounds
      if self.discrepancy_count > 0:
          self.discrepancy_count -= 1
          return axl.Action.D
  
      # Every 10 rounds, play C regardless of opponent's move
      if round_number % 10 == 0:
          return axl.Action.C
  
      # Base strategy: mirror opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D

# Given the complex dynamics of this lengthy-session mediation process, I
# recommend adopting a sophisticated "Adaptive Tit-for-Tat with Forgiveness"
# strategy. This approach balances the need for a strong position with the
# potential for collaboration, while remaining flexible to respond to various
# scenarios and mitigate risks from procedural irregularities.  Key elements of
# the strategy:  1. Initial Cooperation: Begin the first session with a
# conciliatory proposal to set a collaborative tone and demonstrate good faith.
# 2. Mirroring: In subsequent sessions, mirror your opponent's most recent
# action. If they were conciliatory, respond with a conciliatory proposal. If
# they were aggressive, respond with an aggressive argument.  3. Forgiveness
# Mechanism: Implement a forgiveness protocol to prevent prolonged cycles of
# mutual aggression. After two consecutive aggressive exchanges, offer a
# conciliatory proposal regardless of the opponent's last move.  4. Clarity and
# Communication: Ensure all arguments and proposals are articulated clearly to
# minimize the risk of misrepresentation or misunderstanding by the arbitrators.
# 5. Adaptive Responses:    a) If your opponent consistently offers conciliatory
# proposals, alternate between conciliatory and mildly aggressive stances to
# optimize outcomes while maintaining a cooperative atmosphere.    b) If your
# opponent is persistently aggressive, use the forgiveness mechanism to attempt
# de-escalation while preparing strong counterarguments.  6. Arbitrator
# Management: Regularly gauge the arbitrators' reactions and adjust the tone and
# content of your arguments accordingly.  7. Procedural Safeguards: Establish
# clear communication channels with the arbitration panel to quickly address any
# procedural irregularities or misunderstandings.  8. Long-term Perspective:
# While aiming for favorable outcomes in individual sessions, prioritize the
# overall goal of a beneficial final resolution.  9. Flexibility Reserve:
# Maintain a repertoire of both aggressive arguments and conciliatory proposals
# for each major issue, allowing quick adaptation to unexpected opponent
# strategies or arbitrator responses.  10. Periodic Strategy Review: After every
# few sessions, analyze the effectiveness of your approach and your opponent's
# patterns to refine your strategy as needed.  This strategy aims to position
# your corporation favorably by encouraging cooperation when possible,
# responding firmly to aggression when necessary, and maintaining adaptability
# throughout the process. It also accounts for the potential of
# misunderstandings or irregularities, ensuring you're prepared to clarify your
# position and address procedural issues promptly.  By balancing assertiveness
# with collaboration and remaining flexible, this approach maximizes your
# chances of achieving optimal or second-best outcomes in individual sessions
# while working towards a favorable overall resolution of the dispute.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    a) If the opponent
# played C in the previous round, play C.    b) If the opponent played D in the
# previous round, play D.  3. Implement a forgiveness mechanism:    a) If both
# you and your opponent have played D for two consecutive rounds, play C in the
# next round regardless of the opponent's last move.  4. To account for noise:
# a) If your opponent's action seems inconsistent with their recent pattern,
# assume it might be due to noise and maintain your current strategy for one
# more round before adapting.  5. Every 50 rounds, evaluate the overall pattern
# of play:    a) If the opponent has mostly played C, alternate between C and D
# for the next 10 rounds.    b) If the opponent has mostly played D, use the
# forgiveness mechanism more frequently by playing C after every single round of
# mutual defection.  6. If your score is significantly lower than your
# opponent's after 500 rounds, slightly increase the frequency of playing D when
# the opponent has played C in the previous round.  7. In the last 100 rounds,
# if the overall game has been mostly cooperative, continue with the standard
# strategy. If it has been mostly competitive, increase the frequency of playing
# D.

class Cooperative_24(LLM_Strategy):
  n = 24
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Helper function to check if both players defected in the last two rounds
      def mutual_defection_last_two_rounds():
          return len(self.history) >= 2 and self.history[-1] == axl.Action.D and opponent.history[-1] == axl.Action.D and \
                 self.history[-2] == axl.Action.D and opponent.history[-2] == axl.Action.D
  
      # Helper function to check if the opponent has mostly cooperated
      def opponent_mostly_cooperated():
          return opponent.history.cooperations > opponent.history.defections
  
      # Helper function to check if the opponent has mostly defected
      def opponent_mostly_defected():
          return opponent.history.defections > opponent.history.cooperations
  
      # Helper function to alternate between C and D
      def alternate_cd():
          return axl.Action.C if len(self.history) % 2 == 0 else axl.Action.D
  
      # First round: always cooperate
      if self.first_round():
          return axl.Action.C
  
      # Forgiveness mechanism: if both defected in the last two rounds, cooperate
      if mutual_defection_last_two_rounds():
          return axl.Action.C
  
      # Standard strategy: mirror the opponent's last move
      if opponent.history[-1] == axl.Action.C:
          action = axl.Action.C
      else:
          action = axl.Action.D
  
      # Every 50 rounds, evaluate the overall pattern of play
      if len(self.history) % 50 == 0:
          if opponent_mostly_cooperated():
              # Alternate between C and D for the next 10 rounds
              if len(self.history) % 60 < 10:
                  return alternate_cd()
          elif opponent_mostly_defected():
              # Use forgiveness mechanism more frequently
              if opponent.history[-1] == axl.Action.D:
                  return axl.Action.C
  
      # After 500 rounds, if your score is significantly lower, increase D frequency
      if len(self.history) > 500:
          my_score, opponent_score = self.total_scores(self.history[-500:], opponent.history[-500:])
          if my_score < opponent_score * 0.9:
              if opponent.history[-1] == axl.Action.C and self._random.random_choice(0.2):
                  return axl.Action.D
  
      # In the last 100 rounds, adjust based on overall cooperation or competition
      if len(self.history) > 900:
          if opponent_mostly_cooperated():
              return action  # Continue standard strategy
          else:
              if self._random.random_choice(0.3):
                  return axl.Action.D  # Increase D frequency in competitive games
  
      return action

# Given the complex dynamics of this lengthy-session mediation process, I
# propose a sophisticated strategy that balances assertiveness with flexibility,
# aimed at optimizing outcomes while mitigating risks. This approach, which
# we'll call "Adaptive Principled Advocacy," consists of several key components:
# 1. Opening Stance: Begin with a measured but firm presentation of your
# corporation's position. This sets a tone of seriousness without appearing
# overly aggressive.  2. Responsive Calibration: Carefully observe and analyze
# your opponent's strategy in the initial sessions. Adjust your approach based
# on their patterns of behavior, but avoid mirroring aggressive tactics.  3.
# Principled Consistency: Maintain a consistent set of core principles and
# objectives throughout the process. This provides a stable foundation for your
# arguments and proposals, even as tactics may shift.  4. Strategic Concessions:
# Periodically offer carefully calculated conciliatory proposals, particularly
# when tensions are high or when you anticipate your opponent may be preparing
# an aggressive stance. This can help reset the tone and potentially catch your
# opponent off-guard.  5. Proactive De-escalation: If both parties fall into a
# pattern of aggressive argumentation, be prepared to break the cycle by
# introducing a conciliatory element, but frame it in a way that maintains your
# strong position.  6. Arbitrator Management: Develop a keen awareness of the
# arbitrators' reactions and preferences. Tailor your presentations to resonate
# with their apparent priorities and concerns.  7. Contingency Planning: Prepare
# multiple versions of each argument or proposal, ranging from highly assertive
# to more conciliatory. This allows for quick pivots if the situation
# unexpectedly changes.  8. Communication Safeguards: Implement a system of
# clear, written summaries after each session to mitigate the risk of
# misrepresentation or misunderstanding. Request clarification from the
# arbitrators if there's any doubt about how your position has been interpreted.
# 9. Periodic Reassessment: Regularly review the overall trajectory of the
# mediation. Be prepared to shift your long-term strategy if the process is not
# trending in your favor.  10. Collaborative Framing: Even when presenting
# aggressive arguments, frame them within the context of seeking a mutually
# beneficial resolution. This helps maintain a constructive atmosphere while
# still advocating strongly for your position.  11. Tactical Unpredictability:
# Occasionally deviate from established patterns in your approach to keep your
# opponent off-balance and potentially induce them to make concessions.  12.
# Exit Strategy Preparation: Throughout the process, continue to develop and
# refine potential exit strategies, including both favorable settlement terms
# and plans for managing potential impasse scenarios.  This strategy aims to
# position your corporation favorably by maintaining a strong stance while
# demonstrating flexibility and a commitment to resolution. It's designed to
# adapt to various opponent strategies and to navigate potential procedural
# complications. The key is to remain principled in your core position while
# being tactically agile in your session-by-session approach.

# Here's a straightforward strategy for the iterated game based on the original
# high-level description:  1. Start by cooperating (C) in the first round.  2.
# For the next 5 rounds, cooperate (C) to establish a baseline and observe the
# opponent's behavior.  3. After the initial 6 rounds:    - If the opponent has
# cooperated at least 4 times out of 6, continue cooperating.    - Otherwise,
# switch to defecting (D).  4. From round 7 onwards, use the following rules in
# order:    a. If the opponent has defected in the last 3 consecutive rounds,
# defect (D).    b. If your score is more than 10 points behind the opponent's,
# defect (D).    c. If the opponent has cooperated in at least 70% of the last
# 20 rounds, cooperate (C).    d. If you have defected in the last 2 consecutive
# rounds, cooperate (C).    e. If the current round number is a multiple of 10,
# cooperate (C).    f. If none of the above conditions are met, defect (D).  5.
# Every 50 rounds, reassess the overall strategy:    - If your total score is
# within 5% of the opponent's, continue with the current strategy.    - If
# you're trailing by more than 5%, increase the defection threshold in rule 4c
# to 80% cooperation rate.    - If you're leading by more than 5%, decrease the
# defection threshold in rule 4c to 60% cooperation rate.  6. In the last 20
# rounds of the game, always defect (D) regardless of other conditions.  7. If
# at any point you detect a pattern of the opponent alternating between C and D
# for more than 10 consecutive rounds, match their pattern but offset by one
# round (play D when they play C, and vice versa).  8. To account for noise,
# when evaluating the opponent's actions, consider an action as "cooperate" if
# at least 2 out of the last 3 rounds were cooperative, and as "defect" if at
# least 2 out of the last 3 rounds were defections.

class Neutral_24(LLM_Strategy):
  n = 24
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Subfunction to check if opponent cooperated in at least 2 of the last 3 rounds
      def opponent_recent_cooperation():
          return opponent.history[-3:].count(axl.Action.C) >= 2
  
      # Subfunction to check if opponent defected in at least 2 of the last 3 rounds
      def opponent_recent_defection():
          return opponent.history[-3:].count(axl.Action.D) >= 2
  
      # Subfunction to check if opponent has alternated between C and D for more than 10 rounds
      def detect_alternating_pattern():
          if len(opponent.history) < 11:
              return False
          for i in range(-10, 0):
              if opponent.history[i] == opponent.history[i + 1]:
                  return False
          return True
  
      # Subfunction to calculate cooperation rate in the last N rounds
      def cooperation_rate(last_n):
          return opponent.history[-last_n:].count(axl.Action.C) / last_n
  
      # Subfunction to check if we are in the last 20 rounds
      def in_last_20_rounds():
          return self.match_attributes['length'] is not None and len(self.history) >= self.match_attributes['length'] - 20
  
      # Subfunction to reassess strategy every 50 rounds
      def reassess_strategy():
          if len(self.history) % 50 == 0 and len(self.history) > 0:
              score_diff = self.score - opponent.score
              if abs(score_diff) / max(self.score, 1) > 0.05:
                  if score_diff < 0:
                      self.coop_threshold = 0.8  # Increase threshold if trailing
                  else:
                      self.coop_threshold = 0.6  # Decrease threshold if leading
              else:
                  self.coop_threshold = 0.7  # Reset to default if within 5%
  
      # Initialize custom attributes on the first round
      if self.first_round():
          self.coop_threshold = 0.7  # Default cooperation threshold
          return axl.Action.C
  
      # First 6 rounds: cooperate
      if len(self.history) < 6:
          return axl.Action.C
  
      # After 6 rounds, check if opponent cooperated at least 4 times
      if len(self.history) == 6:
          if opponent.history[:6].count(axl.Action.C) >= 4:
              return axl.Action.C
          else:
              return axl.Action.D
  
      # Reassess strategy every 50 rounds
      reassess_strategy()
  
      # Last 20 rounds: always defect
      if in_last_20_rounds():
          return axl.Action.D
  
      # Rule 4: Apply the decision rules in order
      if opponent.history[-3:] == [axl.Action.D] * 3:  # Rule 4a: Opponent defected last 3 rounds
          return axl.Action.D
      if self.score < opponent.score - 10:  # Rule 4b: More than 10 points behind
          return axl.Action.D
      if len(self.history) >= 20 and cooperation_rate(20) >= self.coop_threshold:  # Rule 4c: Opponent cooperated in 70% of last 20 rounds
          return axl.Action.C
      if self.history[-2:] == [axl.Action.D] * 2:  # Rule 4d: Defected in last 2 rounds
          return axl.Action.C
      if len(self.history) % 10 == 0:  # Rule 4e: Round number is a multiple of 10
          return axl.Action.C
  
      # Rule 7: Detect alternating pattern and match with offset
      if detect_alternating_pattern():
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # Rule 8: Account for noise in opponent's actions
      if opponent_recent_defection():
          return axl.Action.D
      if opponent_recent_cooperation():
          return axl.Action.C
  
      # Default action: defect
      return axl.Action.D

# Given the scenario and objectives, here's a high-level, straightforward, and
# aggressive strategy to maximize research output over the multi-week
# collaboration:  1. Start with a "Tit-for-Tat with Forgiveness" approach:    -
# Begin by sharing openly in the first week to establish goodwill.    - In
# subsequent weeks, mirror your colleague's action from the previous week.    -
# If your colleague doesn't share, don't share in the next week.    - If they do
# share, reciprocate by sharing in the next week.  2. Implement a "Forgiveness"
# mechanism:    - If your colleague doesn't share for two consecutive weeks,
# share once every third week to test if they'll reciprocate.    - This accounts
# for potential technical issues or miscommunications.  3. Maintain a "Trust
# Score":    - Keep track of how often your colleague shares versus keeps
# information confidential.    - If the trust score falls below a certain
# threshold (e.g., sharing less than 40% of the time), switch to a more
# aggressive strategy.  4. Aggressive fallback strategy:    - If trust score is
# low, switch to a "Selective Sharing" approach.    - Share minor improvements
# or partial information while keeping major breakthroughs confidential.    -
# This minimizes potential losses while still encouraging some level of
# collaboration.  5. Periodic "Goodwill Gestures":    - Every few weeks,
# regardless of the colleague's recent actions, share some information to
# encourage renewed cooperation.    - This can help break cycles of mutual non-
# sharing.  6. Adapt to patterns:    - If you notice your colleague following a
# specific pattern (e.g., alternating between sharing and not sharing), adjust
# your strategy to take advantage of this predictability.  7. Final weeks
# strategy:    - In the last 2-3 weeks of the collaboration, be more inclined to
# keep information confidential to secure a final advantage, unless your
# colleague has been consistently cooperative throughout.  This strategy aims to
# encourage mutual sharing for maximum overall progress while protecting against
# exploitation. It's aggressive in its quick response to non-cooperation but
# includes mechanisms to re-establish collaboration. The approach also accounts
# for potential technical issues by incorporating forgiveness and periodic
# goodwill gestures.

# Here's the converted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For subsequent rounds:    - If the opponent
# played C in the previous round, play C.    - If the opponent played D in the
# previous round, play D.  3. Keep a count of the opponent's D plays. If they
# play D for two consecutive rounds, play C in the third round to test for
# cooperation.  4. Maintain a "trust score" for the opponent:    - Increase the
# score by 1 for each C play.    - Decrease the score by 1 for each D play.    -
# If the trust score falls below -20 (indicating more D plays than C plays),
# switch to the following strategy:      - Play D for 3 rounds.      - Then play
# C for 1 round.      - Repeat this 3D, 1C pattern until the trust score rises
# above -10.  5. Every 10 rounds, regardless of the opponent's recent actions,
# play C to encourage cooperation.  6. If a clear pattern in the opponent's play
# is detected (e.g., alternating C and D), adjust the strategy to capitalize on
# this pattern by playing D when the opponent is expected to play C.  7. For the
# final 30 rounds of the game:    - If the trust score is positive, continue
# with the main strategy.    - If the trust score is negative, play D for all
# remaining rounds.  8. If your intended play is different from your previous
# round's play, there's a 10% chance it will be flipped. Account for this by
# assuming the same possibility for your opponent's actions when evaluating
# their behavior.

class Aggressive_25(LLM_Strategy):
  n = 25
  attitude = Attitude.AGGRESSIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.player.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.trust_score = 0
          self.defection_streak = 0
          return axl.Action.C
  
      # Helper function to detect alternating pattern
      def detect_alternating_pattern():
          if len(opponent.history) < 4:
              return False
          return (opponent.history[-4] == axl.Action.C and opponent.history[-3] == axl.Action.D and
                  opponent.history[-2] == axl.Action.C and opponent.history[-1] == axl.Action.D)
  
      # Update trust score and defection streak
      if opponent.history[-1] == axl.Action.D:
          self.trust_score -= 1
          self.defection_streak += 1
      else:
          self.trust_score += 1
          self.defection_streak = 0
  
      # Check if opponent defected for two consecutive rounds
      if self.defection_streak == 2:
          return axl.Action.C  # Test for cooperation after two defections
  
      # If trust score falls below -20, switch to 3D, 1C pattern
      if self.trust_score < -20:
          if len(self.history) % 4 < 3:
              return axl.Action.D
          else:
              return axl.Action.C
  
      # Every 10 rounds, play C to encourage cooperation
      if len(self.history) % 10 == 0:
          return axl.Action.C
  
      # Detect alternating pattern and adjust strategy
      if detect_alternating_pattern():
          return axl.Action.D if opponent.history[-1] == axl.Action.C else axl.Action.C
  
      # For the final 30 rounds, switch to all D if trust score is negative
      if len(self.history) >= 970:
          if self.trust_score < 0:
              return axl.Action.D
  
      # Main strategy: mirror opponent's last move
      next_move = opponent.history[-1]
  
      # 10% chance to flip the intended move
      if self._random.random_choice(0.1):
          next_move = axl.Action.D if next_move == axl.Action.C else axl.Action.C
  
      return next_move

# Given the complex dynamics of this lengthy-session mediation process, I would
# recommend implementing a sophisticated "Adaptive Tit-for-Tat with Forgiveness"
# strategy. This approach combines elements of game theory, psychology, and
# legal strategy to position our corporation favorably while remaining flexible
# to our opponent's tactics and potential procedural irregularities.  Key
# elements of the strategy:  1. Initial Cooperation: Begin the first session
# with a conciliatory proposal to set a collaborative tone and demonstrate good
# faith.  2. Mirroring: In subsequent sessions, mirror the opponent's previous
# move. If they were aggressive, respond with an aggressive argument. If they
# were conciliatory, respond with a conciliatory proposal.  3. Forgiveness
# Mechanism: Every third session, regardless of the opponent's previous move,
# present a conciliatory proposal. This prevents the process from getting locked
# in a cycle of mutual aggression and provides opportunities for de-escalation.
# 4. Clear Communication: Before each session, clearly articulate our intended
# strategy to the arbitrators to mitigate the risk of misrepresentation or
# misunderstanding.  5. Adaptive Flexibility: Continuously assess the
# effectiveness of our strategy and be prepared to adjust based on the
# opponent's patterns, arbitrators' reactions, and any procedural
# irregularities.  6. Strategic Aggression: When presenting aggressive
# arguments, focus on substantive legal and factual points rather than personal
# attacks or overly confrontational language.  7. Conciliation with Strength:
# When offering conciliatory proposals, ensure they still strongly represent our
# interests while demonstrating willingness to compromise.  8. Documentation:
# Maintain meticulous records of each session, including our strategy, the
# opponent's approach, and the arbitrators' responses to help inform future
# sessions.  9. Breakout Sessions: Utilize private breakout sessions with the
# arbitrators to clarify any misunderstandings and reinforce our strategic
# intentions.  10. Long-term Perspective: While responding to each session,
# maintain focus on the overall goal of a favorable resolution rather than
# winning each individual interaction.  This strategy allows us to adapt to our
# opponent's approach while maintaining a generally cooperative stance. The
# forgiveness mechanism prevents prolonged aggressive exchanges, potentially
# swaying the arbitrators by demonstrating our willingness to collaborate.   If
# our opponent consistently chooses aggression, our strategy will result in a
# pattern of alternating aggressive and conciliatory sessions from our side,
# which may be viewed favorably by the arbitrators. If they choose to be
# consistently conciliatory, our strategy will result in mostly conciliatory
# sessions, fostering a collaborative atmosphere conducive to a mutually
# beneficial resolution.  In the case of procedural irregularities or
# communication breakdowns, our clear communication with the arbitrators and
# meticulous documentation will help us navigate these challenges effectively.
# The adaptive nature of the strategy allows us to reassess and adjust our
# approach if unexpected situations arise.  By implementing this sophisticated
# yet straightforward strategy, we position ourselves to achieve optimal or
# near-optimal outcomes in most sessions while maintaining the flexibility to
# adapt to various scenarios that may unfold during this lengthy mediation
# process.

# Here's the adapted strategy for the iterated normal-form game:  1. Start by
# playing C in the first round.  2. For rounds 2 to 1000:    a. If it's a
# multiple of 3 round (3, 6, 9, etc.), play C.    b. Otherwise, play the action
# your opponent played in the previous round.  3. Keep a count of the number of
# times your opponent has played D in the last 5 rounds. If this count exceeds
# 3, play D for the next round (unless it's a multiple of 3 round).  4. If you
# notice a streak of 5 or more rounds where your opponent's actions don't match
# the expected response to your actions (accounting for the 10% noise), switch
# to always playing D for the next 5 rounds before reverting to the main
# strategy.  5. Every 50 rounds, evaluate your cumulative score. If it's lower
# than expected (less than 2.5 points per round on average), increase the
# frequency of D plays by also playing D on rounds that are multiples of 5 (in
# addition to mirroring and the every-third-round C) for the next 50 rounds.  6.
# If you play D and your opponent plays C for 3 consecutive rounds, switch to C
# for the next round (unless it's already supposed to be C according to the main
# strategy).  7. In case of any extended sequence (10 or more rounds) where both
# players consistently play D, attempt to break the cycle by playing C for 2
# consecutive rounds before reverting to the main strategy.

class Cooperative_25(LLM_Strategy):
  n = 25
  attitude = Attitude.COOPERATIVE
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.opponent_defections_last_5 = 0
          self.mismatch_streak = 0
          self.d_streak = 0
          self.d_frequency_increase = False
          return axl.Action.C
  
      # Helper function to check if the current round is a multiple of n
      def is_multiple_of(n):
          return len(self.history) % n == 0
  
      # Update the count of opponent's defections in the last 5 rounds
      if len(self.history) >= 5:
          self.opponent_defections_last_5 = opponent.history[-5:].count(axl.Action.D)
  
      # Check for mismatch streak (opponent's actions not matching expected response)
      if len(self.history) >= 5:
          expected_action = self.history[-1]  # Expect opponent to mirror our last action
          if opponent.history[-1] != expected_action:
              self.mismatch_streak += 1
          else:
              self.mismatch_streak = 0
  
      # Check for D streak (both players playing D for 10 or more rounds)
      if len(self.history) >= 10:
          if self.history[-10:].count(axl.Action.D) == 10 and opponent.history[-10:].count(axl.Action.D) == 10:
              self.d_streak = 10
          else:
              self.d_streak = 0
  
      # Every 50 rounds, evaluate the score and adjust D frequency if needed
      if is_multiple_of(50):
          rounds_played = len(self.history)
          if rounds_played > 0:
              avg_score = self.score / rounds_played
              if avg_score < 2.5:
                  self.d_frequency_increase = True
              else:
                  self.d_frequency_increase = False
  
      # Rule 7: Break D streak by playing C for 2 consecutive rounds
      if self.d_streak >= 10:
          if self.d_streak < 12:
              self.d_streak += 1
              return axl.Action.C
          else:
              self.d_streak = 0
  
      # Rule 6: If we play D and opponent plays C for 3 consecutive rounds, switch to C
      if len(self.history) >= 3:
          if self.history[-3:] == [axl.Action.D, axl.Action.D, axl.Action.D] and opponent.history[-3:] == [axl.Action.C, axl.Action.C, axl.Action.C]:
              return axl.Action.C
  
      # Rule 4: If mismatch streak is 5 or more, play D for the next 5 rounds
      if self.mismatch_streak >= 5:
          if self.mismatch_streak < 10:
              self.mismatch_streak += 1
              return axl.Action.D
          else:
              self.mismatch_streak = 0
  
      # Rule 3: If opponent defected more than 3 times in the last 5 rounds, play D
      if self.opponent_defections_last_5 > 3:
          if not is_multiple_of(3):
              return axl.Action.D
  
      # Rule 2a: Play C on multiples of 3
      if is_multiple_of(3):
          return axl.Action.C
  
      # Rule 5: If D frequency increase is active, play D on multiples of 5
      if self.d_frequency_increase and is_multiple_of(5):
          return axl.Action.D
  
      # Rule 2b: Otherwise, mirror the opponent's last action
      return opponent.history[-1]

# Here's a high-level, straightforward, and neutral strategy to achieve the best
# possible outcomes for your country across several rounds of negotiations:  1.
# Start with cooperation: Begin the negotiations by offering a free trade
# agreement in the first round. This establishes a positive tone and
# demonstrates willingness to cooperate.  2. Reciprocate: In subsequent rounds,
# mirror your counterpart's previous move. If they offered free trade, continue
# with free trade. If they imposed protectionist measures, respond with
# protectionism.  3. Forgive occasionally: If your counterpart imposes
# protectionist measures, consider offering free trade again after 1-2 rounds of
# reciprocal protectionism. This allows for the possibility of returning to
# mutual cooperation.  4. Communicate clearly: Ensure your proposals are clearly
# stated and documented to minimize the risk of misinterpretation or incorrect
# implementation.  5. Verify implementation: After each round, confirm that both
# parties' policies were correctly implemented as agreed upon.  6. Adapt to
# patterns: If you notice a consistent strategy from your counterpart, adjust
# your approach accordingly to maximize beneficial outcomes.  7. Maintain
# flexibility: Be prepared to adjust your strategy if unexpected scenarios or
# apparent miscommunications occur.  8. Seek long-term stability: While aiming
# for ideal outcomes, prioritize establishing a stable, mutually beneficial
# trade relationship over short-term gains.  9. Review and reassess:
# Periodically evaluate the overall progress of negotiations and be willing to
# propose changes to the negotiation framework if needed.  This strategy aims to
# balance cooperation and self-interest while remaining adaptable to various
# scenarios and potential miscommunications that may arise during the
# negotiation process.

# Here's a straightforward description of the strategy adapted for the iterated
# normal-form game:  1. Start by playing C in the first round.  2. For
# subsequent rounds:    - If the opponent played C in the previous round, play
# C.    - If the opponent played D in the previous round, play D.  3. Every 3
# rounds, regardless of the opponent's previous move, play C. This serves as a
# forgiveness mechanism and an attempt to restore cooperation.  4. If you
# observe that your opponent has played D for 5 consecutive rounds, switch to
# always playing D until they play C twice in a row.  5. If you notice that your
# score is consistently lower than expected over the last 10 rounds (considering
# the 10% noise factor), reassess your strategy:    - If you've been mostly
# cooperating, switch to defecting for the next 5 rounds.    - If you've been
# mostly defecting, switch to cooperating for the next 5 rounds.  6. For the
# last 10 rounds of the game, always play D to protect against end-game
# exploitation.  7. Throughout the game, keep a running tally of your opponent's
# C and D moves. If the ratio of D to C moves exceeds 2:1 over the last 50
# rounds, switch to always playing D until this ratio drops below 3:2.

class Neutral_25(LLM_Strategy):
  n = 25
  attitude = Attitude.NEUTRAL
  game = 'classic'
  rounds = 1000
  noise = 0.1

  @auto_update_score
  def strategy(self, opponent: axl.Player) -> axl.Action:
      # Initialize custom attributes on the first round
      if self.first_round():
          self.consecutive_defections = 0
          self.forced_defect = False
          self.forced_cooperate = False
          self.forced_rounds = 0
          return axl.Action.C
  
      # Helper function to calculate the ratio of defections to cooperations
      def defection_ratio(history, rounds):
          defections = history[-rounds:].count(axl.Action.D)
          cooperations = history[-rounds:].count(axl.Action.C)
          return defections / max(cooperations, 1)
  
      # Step 4: Check if opponent has defected for 5 consecutive rounds
      if opponent.history[-5:] == [axl.Action.D] * 5:
          self.forced_defect = True
  
      # Step 7: Check if the ratio of D to C exceeds 2:1 over the last 50 rounds
      if len(opponent.history) >= 50 and defection_ratio(opponent.history, 50) > 2:
          self.forced_defect = True
  
      # Step 7: If the ratio drops below 3:2, stop always defecting
      if len(opponent.history) >= 50 and defection_ratio(opponent.history, 50) < 1.5:
          self.forced_defect = False
  
      # Step 5: Reassess strategy if score is consistently lower than expected
      if len(self.history) >= 10:
          my_score, opponent_score = self.total_scores(self.history[-10:], opponent.history[-10:])
          expected_score = 3 * self.history[-10:].count(axl.Action.C)  # Expected score if mutual cooperation
          if my_score < expected_score * 0.9:
              if self.history[-10:].count(axl.Action.C) > self.history[-10:].count(axl.Action.D):
                  self.forced_defect = True
                  self.forced_rounds = 5
              else:
                  self.forced_cooperate = True
                  self.forced_rounds = 5
  
      # Step 6: Always defect in the last 10 rounds
      if len(self.history) >= 990:
          return axl.Action.D
  
      # Handle forced cooperation or defection for the next 5 rounds
      if self.forced_rounds > 0:
          self.forced_rounds -= 1
          if self.forced_defect:
              return axl.Action.D
          if self.forced_cooperate:
              return axl.Action.C
  
      # Step 3: Every 3 rounds, play C
      if len(self.history) % 3 == 0:
          return axl.Action.C
  
      # Step 2: Play according to opponent's last move
      if opponent.history[-1] == axl.Action.C:
          return axl.Action.C
      else:
          return axl.Action.D
