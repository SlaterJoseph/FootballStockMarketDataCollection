import json
import pandas as pd
from Utils.constants import AGGREGATE_PASSING_S, AGGREGATE_RUSHING_S, AGGREGATE_RECEIVING_S


def seasonal_team_defense(season: int) -> None:
    """
    A function which grabs season totals of teams defensive players and combines them for the teams defensive stats
    :param season: The given season
    :return: None
    """
    defensive_df = pd.read_csv('../../CSVs/Seasonally/defense.csv')
    mask = (defensive_df['Season'] == season)
    filtered_defensive_df = defensive_df[mask]

    weekly_dfs = grab_weekly_dfs(season)

    with open('../../Utils/TeamConversions.json') as f:
        teams = json.load(f)['abbreviation_to_team']

    filter_offensive_stats(weekly_dfs)

    for team in teams:
        mask = filtered_defensive_df['Teams']


def weekly_team_defense(season: int, week: int, team: str) -> None:
    """
    A function which using a season, week and team looks for a specific weekly game and aggregates all the defensive stats
    :param season:
    :param week:
    :param team:
    :return:
    """
    pass


def grab_weekly_dfs(season: int) -> [pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    A function which filters the givens season data from the 3 offensive csvs and return the dfs
    :param season: The given season
    :return: A list of the 3 seasons
    """
    dfs = [pd.read_csv('../../CSVs/Weekly/passing.csv', ),
           pd.read_csv('../../CSVs/Weekly/rushing.csv'),
           pd.read_csv('../../CSVs/Weekly/receiving.csv')]

    for i in range(len(dfs)):
        mask = (dfs[i]['season'] == season)
        dfs[i] = dfs[i][mask]

    return dfs


def filter_offensive_stats(dfs: list, df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Filters and sums offensive totals from the offensive dfs
    :param df: The dataframe we are adding the offensive totals too
    :param dfs: The offensive DFS
    :return:
    """
    for i in range(len(dfs)):
        df = dfs[i]
        df = df.drop(['name', 'team', 'week', 'season', 'isHome'], axis=1)

        # The passing df
        if i == 0:
            df[['CMP', 'ATT']] = df['C/ATT'].str.split('/', expand=True)
            df.loc[df['QBR'] == '--', 'QBR'] = '0.0'
            df.drop(['C/ATT', 'SACKS'], axis=1, inplace=True)

            df['QBR'] = pd.to_numeric(df['QBR'])
            df['CMP'] = pd.to_numeric(df['CMP'])
            df['ATT'] = pd.to_numeric(df['ATT'])
            series = df.groupby('opponent').agg(AGGREGATE_PASSING_S)
            series['CMP %'] = (series['CMP'] / series['ATT']) * 100

        # Rushing and receiving dfs
        else:
            series = df.groupby('opponent').agg(AGGREGATE_RUSHING_S if i == 1 else AGGREGATE_RECEIVING_S)

        print(series)

    return df


seasonal_team_defense(2023)
