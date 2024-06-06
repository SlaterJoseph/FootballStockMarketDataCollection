import json
import pandas as pd
from Utils.constants import AGGREGATE_PASS_S, AGGREGATE_RUSH_S, AGGREGATE_REC_S, MAP_REC_S, MAP_PASS_S, MAP_RUSH_S


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

    df = filter_offensive_stats(weekly_dfs)

    # Separates players traded mid-season
    mask = filtered_defensive_df['Teams'].str.len() > 3
    traded = filtered_defensive_df[mask]
    filtered_defensive_df = filtered_defensive_df[~mask]

    seasonal_totals = sum_player_season_totals(filtered_defensive_df)
    traded_totals = traded_seasonal_totals(traded, season)

    df.merge(right=seasonal_totals, on='Team', how='outer')
    df.to_csv('../../CSVs/Archived/Seasonally/team_defense.csv')


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


def filter_offensive_stats(dfs: list) -> pd.DataFrame:
    """
    Filters and sums offensive totals from the offensive dfs
    :param dfs: The offensive DFS
    :return: The merged df
    """
    defensive_stats = list()

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
            data = df.groupby('opponent').agg(AGGREGATE_PASS_S)
            data['CMP %'] = (data['CMP'] / data['ATT']) * 100
            data.rename(mapper=MAP_PASS_S, axis=1, inplace=True)
            defensive_stats.append(data)

        # Rushing  df
        elif i == 1:
            data = df.groupby('opponent').agg(AGGREGATE_RUSH_S)
            data.rename(mapper=MAP_RUSH_S, axis=1, inplace=True)
            defensive_stats.append(data)

        # Receiving df
        else:
            data = df.groupby('opponent').agg(AGGREGATE_REC_S)
            data.rename(mapper=MAP_REC_S, axis=1, inplace=True)
            defensive_stats.append(data)

    df = pd.merge(left=defensive_stats[0], right=defensive_stats[1], on='opponent', how='outer')
    df.merge(right=defensive_stats[2], on='opponent', how='outer')
    df.rename(mapper={'opponent': 'Team'}, axis=1, inplace=True)

    return df


def sum_player_season_totals(players: pd.DataFrame) -> pd.DataFrame:
    """
    Sums all the player totals who played a full season with their team
    :param players: The df of players who played a full season with a team
    :return: A df of players stats aggregated by team
    """
    players.drop(['Unnamed: 0', 'Name', 'Season', 'POS', 'GP'], axis=1, inplace=True)
    players.rename(mapper={'Teams': 'Team'}, axis=1, inplace=True)
    return players.groupby('Team').sum()


def traded_seasonal_totals(traded: pd.DataFrame, season: int) -> pd.DataFrame:
    """
    Looks at weekly stats from the players traded and splits them among the proper teams
    :param traded: The dataframe of traded players
    :param season: The season
    :return: The aggregated stat totals organized by teams
    """
    # TOT,SOLO, TFL,PD, TD
    df = pd.read_csv('../../CSVs/Weekly/defensive.csv')
    df.drop(['name', 'opponent', 'week', 'season', 'isHome', 'SACKS', 'QB HTS'], axis=1, inplace=True)

    names = traded.Name.unique()
    for name in names:
        mask = (df['name'] == name) & (df['season'] == season)
        player_stats = df[mask]
        df.drop(df[mask], inplace=True)


seasonal_team_defense(2023)
