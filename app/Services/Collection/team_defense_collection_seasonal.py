import pandas as pd
from Services.Collection.seasonal_stats_collection import archive_old_season
from Utils.constants import AGGREGATE_PASS_S, AGGREGATE_RUSH_S, AGGREGATE_REC_S, MAP_REC_S, MAP_PASS_S, MAP_RUSH_S
from utils import split_traded, sum_player_season_totals

pd.options.mode.copy_on_write = True


def initial_seasonal_team_defense_seasonally(seasons: list) -> None:
    """
    A function which creates the initial season total df
    :param seasons: A list of seasons to grab data from
    :return: None
    """
    defensive_df = pd.read_csv('../../CSVs/Seasonally/defense.csv')
    df = None

    for season in seasons:
        mask = (defensive_df['Season'] == season)
        filtered_defensive_df = defensive_df[mask]

        weekly_dfs = grab_weekly_dfs(season)
        new_df = filter_offensive_stats(weekly_dfs)

        traded, filtered_defensive_df = split_traded(filtered_defensive_df)
        seasonal_totals = sum_player_season_totals(filtered_defensive_df)

        new_df = new_df.merge(right=seasonal_totals, on='Team', how='outer', )
        traded_totals = traded_seasonal_totals(set(traded['Name']), season)
        new_df = pd.concat([new_df, traded_totals]).groupby('Team', as_index=False).sum()

        if not df:
            df = pd.merge(df, new_df, on=df.columns.tolist())
        else:
            df = new_df
    df.to_csv('../../CSVs/Seasonally/team_defense.csv')


def new_seasonal_team_defense(season: int) -> None:
    """
    A function which grabs season totals of teams defensive players and combines them for the teams defensive stats
    :param season: The given season
    :return: None
    """
    defensive_df = pd.read_csv('../../CSVs/Seasonally/defense.csv')
    mask = (defensive_df['Season'] == season)
    filtered_defensive_df = defensive_df[mask]

    weekly_dfs = grab_weekly_dfs(season)
    new_df = filter_offensive_stats(weekly_dfs)

    traded, filtered_defensive_df = split_traded(filtered_defensive_df)
    seasonal_totals = sum_player_season_totals(filtered_defensive_df)

    new_df = new_df.merge(right=seasonal_totals, on='Team', how='outer', )
    traded_totals = traded_seasonal_totals(set(traded['Name']), season)
    new_df = pd.concat([new_df, traded_totals]).groupby('Team', as_index=False).sum()
    new_df.to_csv('../../CSVs/Seasonally/team_defense.csv')
    archive_old_season(season - 3)


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
            data = filter_qb_stats(df)
            defensive_stats.append(data)

        # Rushing  df
        elif i == 1:
            data = df.groupby('opponent', as_index=False).agg(AGGREGATE_RUSH_S)
            data.rename(mapper=MAP_RUSH_S, axis=1, inplace=True)
            defensive_stats.append(data)

        # Receiving df
        else:
            data = df.groupby('opponent', as_index=False).agg(AGGREGATE_REC_S)
            data.rename(mapper=MAP_REC_S, axis=1, inplace=True)
            defensive_stats.append(data)

    df = pd.merge(left=defensive_stats[0], right=defensive_stats[1], on='opponent', how='outer')
    df.merge(right=defensive_stats[2], on='opponent', how='outer')
    df.rename(mapper={'opponent': 'Team'}, axis=1, inplace=True)

    return df


def filter_qb_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Code which filters specific the QB totals
    :param df: The passing df
    :return: The filtered df
    """
    df[['CMP', 'ATT']] = df['C/ATT'].str.split('/', expand=True)
    df.loc[df['QBR'] == '--', 'QBR'] = '0.0'
    df.drop(['C/ATT', 'SACKS'], axis=1, inplace=True)

    df['QBR'] = pd.to_numeric(df['QBR'])
    df['CMP'] = pd.to_numeric(df['CMP'])
    df['ATT'] = pd.to_numeric(df['ATT'])
    data = df.groupby('opponent', as_index=False).agg(AGGREGATE_PASS_S)
    data['CMP %'] = (data['CMP'] / data['ATT']) * 100
    data.rename(mapper=MAP_PASS_S, axis=1, inplace=True)
    return data


def traded_seasonal_totals(traded: set, season: int) -> pd.DataFrame:
    """
    Looks at weekly stats from the players traded and splits them among the proper teams
    :param traded: The dataframe of traded players
    :param season: The season
    :return: The aggregated stat totals organized by teams
    """
    weekly_df = pd.read_csv('../../CSVs/Weekly/defensive.csv')
    weekly_df.rename(mapper={'team': 'Team'}, axis=1, inplace=True)
    mask = (weekly_df['season'] == season) & (weekly_df['name'].isin(traded))
    weekly_df = weekly_df[mask]
    weekly_df.drop(['name', 'opponent', 'week', 'season', 'isHome', 'SACKS', 'QB HTS'], axis=1, inplace=True)
    return weekly_df



