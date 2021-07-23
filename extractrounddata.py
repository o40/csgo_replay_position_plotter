from pathlib import Path
import pandas as pd
from collections import defaultdict

data_save_length = 128 * 15  # 15 seconds at 128 tick

basepath = Path("csv\\")


def _get_match_start_tick(file):
    """Get the match start tick from the *_matchstart.csv"""
    with file.open("r") as fh:
        lines = fh.read().splitlines()
        return int(lines[1])


def _get_round_start_ticks(file):
    """Get the list of round start ticks from *_rounds.csv"""
    with file.open("r") as fh:
        next(fh)
        return [int(tick) for tick in fh.read().splitlines()]


def _get_position_data(file):
    """Get the position fata from *_pos.csv as a pandas dataframe"""
    return pd.read_csv(file)


def _parse_position_data(df, match_start_tick, round_start_ticks):
    """Parse the positions dataframe to get subsets of the dataframe for each player and round.

    This is returned as a list of dataframes.
    """
    round_data = []
    for name in df.name.unique():
        name_df = df[(df.name == name) & (df.tick >= match_start_tick)]
        for round_start_tick in round_start_ticks:
            round_df = name_df[
                (name_df.tick >= round_start_tick)
                & (name_df.tick < (round_start_tick + data_save_length))
            ]
            if len(round_df.index) > 0:
                round_data.append(round_df)
    return round_data


def _get_common_start_points(round_data):
    """Loop through all start points in the round data and return a list of the common
    start points. These are used to filter out bad data. 
    """
    start_points = defaultdict(int)
    for rd in round_data:
        x = rd["x"].iloc[0]
        y = rd["y"].iloc[0]

        start_points[(x, y)] += 1

    common_start_points = []
    for key, val in start_points.items():
        # TODO: Tune, or percentage?
        if val > 5:
            common_start_points.append(key)
    return common_start_points


def _filter_bad_data(round_data, common_start_points):
    """Filter out round data in the list if they:
    * Start at a incorrect start point
    * Movement speed is too large
    """
    filtered_round_data = []
    for df in round_data:
        # Filter out points not in common start points
        x = df["x"].iloc[0]
        y = df["y"].iloc[0]

        sane_movement_speed = (df["x"].diff().max() < 5) and (df["y"].diff().max() < 5)
        sane_starting_points = (x, y) in common_start_points

        if sane_starting_points and sane_movement_speed:
            filtered_round_data.append(df)
    return filtered_round_data


for file in sorted(basepath.glob("*_pos.csv")):
    """ Main function that loops through all the files in the csv folder
    and prints the round-data.
    """
    
    data_name = file.name[:-8]
    file_matchstart = basepath / Path(data_name + "_matchstart.csv")
    file_rounds = basepath / Path(data_name + "_rounds.csv")
    file_positions = basepath / Path(data_name + "_pos.csv")

    match_start_tick = _get_match_start_tick(file_matchstart)
    round_start_ticks = _get_round_start_ticks(file_rounds)
    position_dataframe = _get_position_data(file_positions)

    round_data = _parse_position_data(
        position_dataframe, match_start_tick, round_start_ticks
    )

    common_start_points = _get_common_start_points(round_data)
    round_data = _filter_bad_data(round_data, common_start_points)

    for rd in round_data:
        lastrow = None
        bad_round_data = False
        adjusted_round_data = []
        for _, row in rd.iterrows():
            if lastrow:
                # Filter out rounds with "skips" in recorded ticks.
                # This will filter out 64-tick demos entirely.
                if row.tick != (lastrow + 1):
                    # print(f"Skip in tick {lastrow} to {row.tick}")
                    bad_round_data = True
            adjusted_round_data.append((row.x, row.y, row.team))
            lastrow = row.tick

        if not bad_round_data:
            for tick, row in enumerate(adjusted_round_data):
                x, y, team = row
                print(f"{tick},{x},{y},{team}")

