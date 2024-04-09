from collections import defaultdict
from typing import List

import axelrod as axl


class FixedTournament(axl.Tournament):

  def __init__(
      self,
      players: List[axl.player.Player],
      name: str = "axelrod",
      game=None,
      turns=None,
      prob_end=None,
      repetitions: int = 10,
      noise: float = 0,
      edges=None,
      match_attributes=None,
      seed=None,
  ) -> None:
    super().__init__(players, name, game, turns, prob_end, repetitions, noise,
                     edges, match_attributes, seed)

  def _play_matches(self, chunk, build_results=True):
    """
    See base class.

    This has been modified so that:
    1. The seed is the same for all matches. Thus the game length and the
       rounds that have noise are the same, as long as no player touches
       the same random number generator.
    2. Each match is repeated with the players swapped, so that the noise
       will effect them identically.
    """
    interactions = defaultdict(list)
    index_pair, match_params, repetitions, _ = chunk
    p1_index, p2_index = index_pair
    player1 = self.players[p1_index].clone()
    player2 = self.players[p2_index].clone()
    match_params["players"] = (player1, player2)
    match_params["seed"] = self.seed
    match = axl.Match(**match_params)
    for _ in range(repetitions):
      match.play()

      if build_results:
        results = self._calculate_results(match.result)
      else:
        results = None

      interactions[index_pair].append([match.result, results])
    # now reverse the players
    index_pair = (p2_index, p1_index)
    match_params["players"] = (player2, player1)
    match = axl.Match(**match_params)
    for _ in range(repetitions):
      match.play()

      if build_results:
        results = self._calculate_results(match.result)
      else:
        results = None

      interactions[index_pair].append([match.result, results])
      return interactions
