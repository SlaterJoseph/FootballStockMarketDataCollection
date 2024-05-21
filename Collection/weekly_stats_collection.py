import glob
import os
import json
import csv
import requests


def collect_weekly_initially():
    """
    A function which creates the game by game stats for the players. Uses the espn API
    where URLs can be found below
    :return: None, saves the CSVs in the proper folder
    """
    base_team_event_url = f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/!@/schedule?season=@!'
    base_game_event_url = f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=!@'

    game_ids = set()
    headers = dict()
    player_data = dict()

    # Grab all the game ids from the 2021 to 2023 seasons
    for year in [2021, 2022, 2023]:
        for i in range(1, 33):
            team_url = base_team_event_url.replace('!@', str(i)).replace('@!', str(year))
            response = json.loads(requests.get(team_url).text)
            for item in response['events']:
                game_ids.add(item['id'])
    print('Done grabbing all game IDs')

    counter = 0
    # Go through all the games and
    for game in game_ids:
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
                headers[cat_name] = labels

                if cat_name not in player_data:
                    player_data[cat_name] = list()

                curr_stat = player_data[cat_name]

                # Go through the players on the teams
                for player in stat['athletes']:
                    player_stats = [player['athlete']['displayName'], curr_team, opponent, week, season,
                                    home_team == curr_team]
                    player_stats.extend(player['stats'])
                    curr_stat.append(player_stats)

        counter += 1
        print(f'{counter}/{len(game_ids)}')
    print('Done fetching all player data')

    csvs = create_csvs(headers)

    # Creating the actual CSVs
    for title in headers.keys():
        header = headers[title]
        csvs[title].writerow(header)

        players = player_data[title]
        csvs[title].writerows(players)


def update_weekly_stats():
    pass


def create_csvs(headers: dict) -> {str: csv.writer}:
    """
    Creates the CSVs and returns a dictionary of the writers
    :param headers: A list of the dictionary of headers
    :return: The dictionary with the title as the key and the writer as the value
    """
    try:
        files = glob.glob(os.path.join('../CSVs/Weekly', '*'))
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
    except OSError:
        print("Error occurred while deleting files.")

    csvs = dict()

    for title in headers:
        writer = csv.writer(open(f'../CSVs/Weekly/{title}.csv', 'a', newline=''))
        writer.writerow(headers[title])

        csvs[title] = writer

    return csvs


collect_weekly_initially()
