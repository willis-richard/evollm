from collections import defaultdict
from typing import List

import axelrod as axl


def _play_matches_fixed_noise(self, chunk, build_results=True):
  """
  See axl.Tournament class.

  This has been modified so that:
  1. The seed is the same for all matches. Thus the game length and the
      rounds that have noise are the same, as long as no player touches
      the same random number generator.
  2. Each match is repeated with the players swapped, so that the noise
      will effect them identically, except for the mirror matchup, which
      is only played once, as it is scored twice.
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
  if p1_index != p2_index:
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


def _build_tasks_including_mirror(self, df):
    """
    Returns a tuple of dask tasks

    This has modified ResultSet._build_tasks to no longer ignore self-interaction
    """
    groups = ["Repetition", "Player index", "Opponent index"]
    columns = ["Turns", "Score per turn", "Score difference per turn"]
    mean_per_reps_player_opponent_task = df.groupby(groups)[columns].mean()

    groups = ["Player index", "Opponent index"]
    columns = [
        "Cooperation count",
        "CC count",
        "CD count",
        "DC count",
        "DD count",
        "CC to C count",
        "CC to D count",
        "CD to C count",
        "CD to D count",
        "DC to C count",
        "DC to D count",
        "DD to C count",
        "DD to D count",
        "Good partner",
    ]
    sum_per_player_opponent_task = df.groupby(groups)[columns].sum()

    groups = ["Player index", "Repetition"]
    columns = ["Win", "Score"]
    sum_per_player_repetition_task = df.groupby(groups)[columns].sum()

    groups = ["Player index", "Repetition"]
    column = "Score per turn"
    normalised_scores_task = df.groupby(groups)[column].mean()

    groups = ["Player index"]
    column = "Initial cooperation"
    initial_cooperation_count_task = df.groupby(groups)[column].sum()
    interactions_count_task = df.groupby("Player index")[
        "Player index"
    ].count()

    return (
        mean_per_reps_player_opponent_task,
        sum_per_player_opponent_task,
        sum_per_player_repetition_task,
        normalised_scores_task,
        initial_cooperation_count_task,
        interactions_count_task,
    )
