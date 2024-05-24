import requests
import csv
import json


def create_player_csv() -> None:
    """
    A function which calls the RapidAPI's player endpoint to compile a list off all NFL players and grab
    useful information for each, and then put said information in a CSV
    Returns
    -------

    """
    # Writes the initial header line
    headers = ['Name', 'PlayerID', 'Experience', 'Height', 'Weight', 'Position', 'Age', 'Team', 'TeamID', 'isFreeAgent',
               'Headshot', 'espnID']
    writer = csv.writer(open('../../CSVs/players.csv', 'w', newline=''))
    writer.writerow(headers)
    i = 0

    writer = csv.writer(open('../../CSVs/players.csv', 'a', newline=''))

    url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLPlayerList"
    headers = {
        "X-RapidAPI-Key": "236df6219amshc8fa87454bedfc1p11c1f6jsnde793b62943f",
        "X-RapidAPI-Host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com"
    }

    fieldNames = ['longName', 'playerID', 'exp', 'height', 'weight', 'pos', 'age', 'team', 'teamID', 'isFreeAgent',
                  'espnHeadshot', 'espnID']
    response = json.loads(requests.get(url, headers=headers).text)

    for item in response['body']:
        player_info = list()

        for field in fieldNames:
            if field not in item.keys():
                player_info.append('N/A')
            else:
                player_info.append(item[field])

        print(item['longName'])
        writer.writerow(player_info)


create_player_csv()

