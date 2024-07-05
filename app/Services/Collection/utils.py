import glob
import os
import pandas as pd


def clean_out_csvs(path: str) -> None:
    """
    Delete all current csvs in a given path
    :param path: The path to the folder we want to delete all files in
    :return: None
    """
    try:
        files = glob.glob(os.path.join(path, '*'))
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
    except OSError:
        print("Error occurred while deleting files.")


def split_traded(df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    """
    A function which splits players in those traded and those not traded
    :param df: The df of defensive players
    :return: a df of traded players and a df of not traded players
    """
    mask = df['Teams'].str.len() > 3
    return df[mask], df[~mask]


def sum_player_season_totals(players: pd.DataFrame) -> pd.DataFrame:
    """
    Sums all the player totals who played a full season with their team
    :param players: The df of players who played a full season with a team
    :return: A df of players stats aggregated by team
    """
    players.drop(['Unnamed: 0', 'Name', 'Season', 'POS', 'GP'], axis=1, inplace=True)
    players.rename(mapper={'Teams': 'Team'}, axis=1, inplace=True)
    return players.groupby('Team', as_index=False).sum()