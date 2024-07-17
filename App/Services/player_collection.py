import requests
import pandas as pd
import json


def create_player_csv() -> None:
    """
    A function which goes through ESPN to add all NFL players and relevant info to a CSV
    Returns
    -------

    """
    headers = ['Name', 'PlayerID', 'Experience', 'Height', 'Weight', 'Position', 'Age', 'Team', 'Headshot']

    url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes"
    params = {
        'limit': 1000,
        'page': 1
    }

    athletes_href = list()
    next_page = url

    # Collect all NFL players href
    while next_page:
        response = requests.get(next_page, params=params)
        data = response.json()
        athletes = [x['$ref'] for x in data['items']]
        athletes_href.extend(athletes)

        if len(data['items']) < 1000:
            next_page = None
        else:
            params['page'] += 1

    players_df = pd.DataFrame(columns=headers)

    with open('../Utils/TeamConversions.json', 'r') as file:
        id_conversion = json.load(file)['id_to_abbreviation']

    # Go through the collected hrefs populating the player CSV
    for i in range(len(athletes_href)):
        href = athletes_href[i]
        response = requests.get(href)
        data = response.json()

        athlete = [
            data.get('fullName', 'N/A'),
            data.get('id', 'N/A'),
            data['experience']['years'] if data.get('experience', {}).get('years') else 'R',
            data.get('displayHeight', 'N/A'),
            data.get('weight', 'N/A'),
            data['position']['abbreviation'] if data.get('position', {}).get('abbreviation') else 'N/A',
            data.get('age', 'N/A'),
            id_conversion[data['team']['$ref'].split('/')[-1].split('?')[0]] if 'team' in data and '$ref' in data[
                'team'] else 'N/A',
            data['headshot']['href'] if 'headshot' in data else 'N/A'
        ]

        players_df.loc[len(players_df.index)] = athlete
        print(i)

    players_df.to_csv('../CSVs/players.csv')
