import pandas as pd
import os
from utils import sum_player_season_totals, split_traded


def initial_offensive_seasonal_collection(seasons: list) -> None:
    """
    A function which combines player offensive stats for a given team
    :param seasons: The seasons to aggregate
    :return: None
    """
    offensive_csvs = read_in_offensive_csvs()

    for csv_name in offensive_csvs.keys():
        curr_csv = offensive_csvs[csv_name]

        for season in seasons:
            mask = (curr_csv['Season'] == season)
            filtered_df = curr_csv[mask]

            traded, untraded = split_traded(filtered_df)
            season_totals = sum_player_season_totals(untraded)

    pass


def new_offensive_season_collection(season: int) -> None:
    pass


def read_in_offensive_csvs() -> dict:
    """
    Reads in all offensive CSVs
    :return:dictionary of [csv type, read in csv]
    """
    offensive_csvs = dict()
    directory = '../../CSVs/Seasonally'
    excluded_files = {'defense.csv', 'punting.csv', 'returning.csv', 'team_defense.csv'}

    for filename in os.listdir(directory):
        file = os.path.join(directory, filename)

        df = pd.read_csv(file)
        if filename not in excluded_files:
            offensive_csvs[filename[:-4]] = df

    return offensive_csvs
