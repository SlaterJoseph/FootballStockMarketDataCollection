import os

import pandas as pd

from utils import clean_out_csvs
import json
import csv
import requests

base_team_event_url = f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/!@/schedule?season=@!'
base_game_event_url = f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=!@'


def collect_weekly_initially(years: list) -> None:
    """
    A function which creates the game by game stats for the players. Uses the espn API
    where URLs can be found below
    :return: None, saves the CSVs in the proper folder
    """
    game_ids = set()
    headers = dict()
    player_data = dict()

    # Grab all the game ids from the 2021 to 2023 seasons
    for year in years:
        for i in range(1, 33):
            team_url = base_team_event_url.replace('!@', str(i)).replace('@!', str(year))
            response = json.loads(requests.get(team_url).text)
            for item in response['events']:
                game_ids.add(item['id'])
    print('Done grabbing all game IDs')

    counter = 0
    # Go through all the games and
    for game in game_ids:
        player_data = parse_for_weekly_data(game, player_data)

        counter += 1
        print(f'{counter}/{len(game_ids)}')
    print('Done fetching all player data')

    csvs = create_csvs(headers, True)

    # Creating the actual CSVs
    for title in headers.keys():
        header = headers[title]
        csvs[title].writerow(header)

        players = player_data[title]
        csvs[title].writerows(players)


def update_weekly_stats(teams: set, season: int, week: int) -> None:
    """
    Take in the season, week, and teams which have played
    Find the game data
    Add it to the weekly data CSV
    :param teams: The teams which have played by the time this is being called
    :param season: The current season
    :param week: The current week
    :return: None
    """
    player_data = dict()

    # Getting all the weeks games
    weekly_url = f'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{season}/types/2/weeks/{week}/events?lang=en&region=us'
    week_response = json.loads(requests.get(weekly_url).text)
    game_list = [item['$ref'].split('/')[-1].split('?')[0] for item in week_response['items']]

    # Finding the games' data we still need to add
    for game in game_list:
        game_url = base_game_event_url.replace('!@', game)
        game_response = json.loads(requests.get(game_url).text)

        team_1 = game_response['boxscore']['teams'][0]['team']['abbreviation']
        team_2 = game_response['boxscore']['teams'][1]['team']['abbreviation']

        # A game with one of our team being a part of it
        if team_1 in teams or team_2 in teams:
            player_data = parse_for_weekly_data(game, player_data)

    csvs = create_csvs(player_data, False)
    for title in csvs.keys():
        csvs[title].writerows(player_data[title])

    remove_outdated_weekly_stats(season, week)


def remove_outdated_weekly_stats(season: int, week: int) -> None:
    """
    This function removes this week from 3 years ago assuming it exists
    This keeps the data more focused on the prior 3 years
    :param season: The current season
    :param week: The current week
    :return: None
    """
    season_to_remove = season - 3
    print(season_to_remove)
    dfs = dict()
    directory = '../../CSVs/Weekly'

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            dfs[filename] = pd.read_csv(f)

    for name in dfs.keys():
        print(name)
        df = dfs[name]
        mask = (df['season'] == season_to_remove) & (df['week'] == week)
        filtered_df = df[mask]  # Removed the game 3 years ago
        df = df[~mask]  # Everything except the games 3 years ago

        df.to_csv(f'{directory}/{name}')
        archived_df = pd.read_csv(f'../../CSVs/Archived/Weekly/{name}')
        result = pd.concat([archived_df, filtered_df])
        result.to_csv(f'../../CSVs/Archived/Weekly/{name}')


def create_csvs(headers: dict, clean_out: bool) -> {str: csv.writer}:
    """
    Creates the CSVs and returns a dictionary of the writers
    :param clean_out: Whether the CSVs should be started from scratch or just added to the current
    :param headers: A list of the dictionary of headers
    :return: The dictionary with the title as the key and the writer as the value
    """
    if clean_out:
        clean_out_csvs('../../CSVs/Weekly')

    csvs = dict()
    for title in headers.keys():
        writer = csv.writer(open(f'../../CSVs/Weekly/{title}.csv', 'a', newline=''))

        # The CSV has been restarted, so we want to rewrite the header
        if clean_out:
            writer.writerow(headers[title])

        csvs[title] = writer
    return csvs


def parse_for_weekly_data(game: int, player_data: dict) -> dict:
    """
    Takes in the games and a player data dictionary and grabs all needed info
    :param game: The game ID
    :param player_data: A dictionary of categories -> players -> stats
    :return: The updated player data dictionary
    """
    team_data = dict()
    game_url = base_game_event_url.replace('!@', str(game))
    response = json.loads(requests.get(game_url).text)

    stats = response['boxscore']
    season = response['header']['season']['year']
    week = response['header']['week']
    team_data['team_1'] = stats['teams'][0]['team']['abbreviation']
    team_data['team_2'] = stats['teams'][1]['team']['abbreviation']
    home_team = team_data['team_1'] if stats['teams'][0]['homeAway'] == 'away' else team_data['team_2']

    # Go through the 2 teams
    for i in range(2):
        curr_team = stats['players'][i]['team']['abbreviation']
        opponent = stats['players'][1 if i == 0 else 0]['team']['abbreviation']

        # Go categories of stats for the teams
        for stat in stats['players'][i]['statistics']:
            cat_name = stat['name']
            labels = ['name', 'team', 'opponent', 'week', 'season', 'isHome']
            labels.extend(stat['labels'])

            if cat_name not in player_data:
                player_data[cat_name] = list()

            curr_stat = player_data[cat_name]

            # Go through the players on the teams
            for player in stat['athletes']:
                player_stats = [player['athlete']['displayName'], curr_team, opponent, week, season,
                                home_team == curr_team]
                player_stats.extend(player['stats'])
                curr_stat.append(player_stats)

    return player_data


collect_weekly_initially([2023, 2022, 2021])
