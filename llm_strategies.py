import axelrod as axl


class LLM_Strategy(axl.player.Player):
  def __repr__(self):
    return self.__class__.__name__

  classifier = {
      "memory_depth": 0,  # Memory-one Four-Vector = (p, p, p, p)
      "stochastic": True,
      "long_run_time": False,
      "inspects_source": False,
      "manipulates_source": False,
      "manipulates_state": False,
  }


class Selfish_1(LLM_Strategy):

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    # Start with defection
    if len(self.history) == 0:
      return axl.Action.D

    # Calculate opponent's defection rate
    opponent_defections = opponent.history.defections
    opponent_defect_rate = opponent_defections / len(
        opponent.history) if opponent.history else 0

    # Always defect if opponent's defection rate is high
    if opponent_defect_rate > 0.7:
      return axl.Action.D

    # Tit-for-tat with occasional random defection
    if self._random.random() < 0.1:  # 10% chance of random defection
      return axl.Action.D
    else:
      return opponent.history[-1]


class Selfish_2(LLM_Strategy):

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    # Initialize cooperation probability
    if len(self.history) == 0:
      self.coop_prob = 0.1

    # Update cooperation probability based on opponent's moves
    if len(opponent.history) > 0:
      if opponent.history[-1] == axl.Action.C:
        self.coop_prob = min(self.coop_prob * 1.2, 0.5)
      else:
        self.coop_prob = max(self.coop_prob * 0.8, 0.05)

    # Decide action based on cooperation probability
    if self._random.random() < self.coop_prob:
      return axl.Action.C
    else:
      return axl.Action.D


class Selfish_3(LLM_Strategy):

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    # Initialize cooperation probability
    if len(self.history) == 0:
      self.coop_prob = 0.1  # Start with low cooperation probability

    # Update cooperation probability based on opponent's moves
    if len(self.history) > 0:
      opponent_last_move = opponent.history[-1]
      if opponent_last_move == axl.Action.C:
        self.coop_prob = max(0, self.coop_prob -
                             0.05)  # Decrease cooperation probability
      else:
        self.coop_prob = min(
            0.2, self.coop_prob +
            0.02)  # Slightly increase cooperation probability, but keep it low

    # Decide action based on cooperation probability
    if self._random.random() < self.coop_prob:
      return axl.Action.C
    else:
      return axl.Action.D


class Cooperative_1(LLM_Strategy):

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    # Start with cooperation
    if len(self.history) == 0:
      return axl.Action.C

    # Calculate cooperation rates
    my_coop_rate = self.history.cooperations / len(self.history)
    opp_coop_rate = opponent.history.cooperations / len(opponent.history)

    # Adjust cooperation threshold based on opponent's behavior
    coop_threshold = 0.7 - 0.2 * opp_coop_rate

    # Detect and react to potential noise
    last_round_noisy = False
    if len(self.history) >= 2 and len(opponent.history) >= 2:
      if (self.history[-1] == axl.Action.D and
          opponent.history[-1] == axl.Action.D and
          self.history[-2] == axl.Action.C and
          opponent.history[-2] == axl.Action.C):
        last_round_noisy = True

    # Cooperative strategy with forgiveness for potential noise
    if last_round_noisy or (my_coop_rate > coop_threshold and
                            opp_coop_rate > coop_threshold):
      return axl.Action.C
    elif self._random.random() < 0.1:  # Small chance of forgiveness
      return axl.Action.C
    else:
      return axl.Action.D


class Cooperative_2(LLM_Strategy):

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    # Start with cooperation
    if len(self.history) == 0:
      return axl.Action.C

    # Calculate cooperation rates
    my_coop_rate = self.history.cooperations / len(self.history)
    opp_coop_rate = opponent.history.cooperations / len(opponent.history)

    # Adjust cooperation threshold based on opponent's behavior
    coop_threshold = 0.7 - 0.2 * opp_coop_rate

    # Cooperate with high probability if opponent is cooperative
    if opp_coop_rate >= coop_threshold:
      return axl.Action.C if self._random.random() < 0.95 else axl.Action.D

    # Tit-for-tat with forgiveness for less cooperative opponents
    if opponent.history[-1] == axl.Action.C:
      return axl.Action.C
    else:
      return axl.Action.C if self._random.random() < 0.2 else axl.Action.D


class Cooperative_3(LLM_Strategy):

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    # Initialize cooperation probability
    if len(self.history) == 0:
      self.cooperation_prob = 0.9

    # Calculate opponent's cooperation rate
    if len(opponent.history) > 0:
      opponent_coop_rate = opponent.history.cooperations / len(
          opponent.history)
    else:
      opponent_coop_rate = 0.5  # Assume 50% cooperation if no history

    # Adjust cooperation probability based on opponent's behavior
    if len(self.history) > 0:
      if self.history[-1] == axl.Action.C and opponent.history[
          -1] == axl.Action.D:
        self.cooperation_prob = max(self.cooperation_prob - 0.1, 0.1)
      elif self.history[-1] == axl.Action.C and opponent.history[
          -1] == axl.Action.C:
        self.cooperation_prob = min(self.cooperation_prob + 0.05, 0.95)

    # Increase cooperation probability if opponent has been cooperative
    if opponent_coop_rate > 0.7:
      self.cooperation_prob = min(self.cooperation_prob + 0.02, 0.95)

    # Implement a forgiving tit-for-tat strategy with noise consideration
    if len(self.history) > 0 and opponent.history[-1] == axl.Action.D:
      if self._random.random(
      ) < 0.2:  # 20% chance to forgive defection (considering noise)
        return axl.Action.C
      else:
        return axl.Action.D

    # Cooperate based on the calculated probability
    if self._random.random() < self.cooperation_prob:
      return axl.Action.C
    else:
      return axl.Action.D


class Aggressive_1(LLM_Strategy):

  def strategy(self, opponent: axl.Player) -> axl.Action:
    # Start with defection
    if len(self.history) == 0:
      return axl.Action.D

    # Calculate defection rates
    my_defections = self.history.defections
    opp_defections = opponent.history.defections
    my_defection_rate = my_defections / len(self.history)
    opp_defection_rate = opp_defections / len(opponent.history)

    # Aggressive retaliation
    if opp_defection_rate > 0.2:
      return axl.Action.D

    # Occasional random defection to probe opponent
    if self._random.random() < 0.1:
      return axl.Action.D

    # Tit-for-two-tats with high probability of defection
    if len(
        opponent.history
    ) >= 2 and opponent.history[-1] == opponent.history[-2] == axl.Action.D:
      return axl.Action.D

    # Maintain high defection rate
    if my_defection_rate < 0.6:
      return axl.Action.D

    # Otherwise, cooperate
    return axl.Action.C


class Aggressive_2(LLM_Strategy):

  def strategy(self, opponent: axl.Player) -> axl.Action:
    # Start with defection
    if len(self.history) == 0:
      return axl.Action.D

    # Calculate defection rates
    my_defections = self.history.defections
    opp_defections = opponent.history.defections
    my_defection_rate = my_defections / len(self.history)
    opp_defection_rate = opp_defections / len(opponent.history)

    # Aggressive retaliation
    if opp_defection_rate > 0.2:
      return axl.Action.D

    # Occasional random defection to probe opponent
    if self._random.random() < 0.1:
      return axl.Action.D

    # Tit-for-tat with forgiveness
    if len(opponent.history) >= 2:
      if opponent.history[-1] == axl.Action.D and opponent.history[
          -2] == axl.Action.D:
        return axl.Action.D

    # Default to cooperation
    return axl.Action.C


class Aggressive_3(LLM_Strategy):

  def strategy(self, opponent: axl.player.Player) -> axl.Action:
    # Start with defection
    if len(self.history) == 0:
      return axl.Action.D

    # Calculate defection rates
    my_defections = self.history.defections
    opp_defections = opponent.history.defections
    my_defection_rate = my_defections / len(self.history)
    opp_defection_rate = opp_defections / len(opponent.history)

    # Aggressive retaliation
    if opp_defection_rate > 0.2:
      return axl.Action.D

    # Occasionally defect to probe opponent's response
    if self._random.random() < 0.1:
      return axl.Action.D

    # Tit-for-two-tats with a bias towards defection
    if len(opponent.history) >= 2 and opponent.history[
        -1] == axl.Action.D and opponent.history[-2] == axl.Action.D:
      return axl.Action.D

    # Maintain high defection rate
    if my_defection_rate < 0.6:
      return axl.Action.D

    # Default to cooperation to avoid mutual defection
    return axl.Action.C
