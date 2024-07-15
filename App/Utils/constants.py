# The ESPN URLS for each category's season leaders, with the season replaced with !
SEASON_STAT_URLS = [
    'https://www.espn.com/nfl/stats/player/_/season/!/seasontype/2',  # Passing
    'https://www.espn.com/nfl/stats/player/_/stat/rushing/season/!/seasontype/2',  # Rushing
    'https://www.espn.com/nfl/stats/player/_/stat/receiving/season/!/seasontype/2',  # Receiving
    'https://www.espn.com/nfl/stats/player/_/view/defense/season/!/seasontype/2',  # Defense
    'https://www.espn.com/nfl/stats/player/_/view/scoring/season/!/seasontype/2',  # Scoring
    'https://www.espn.com/nfl/stats/player/_/view/special/season/!/seasontype/2',  # Returning
    'https://www.espn.com/nfl/stats/player/_/view/special/stat/kicking/season/!/seasontype/2',  # Kicking
    'https://www.espn.com/nfl/stats/player/_/view/special/stat/punting/season/!/seasontype/2'  # Punting
]

# A 1 to 1 Pairing matching each url to a category (passing URL is an index of 0, passing title is an index of 0)
URL_PAIRINGS = [
    'passing',
    'rushing',
    'receiving',
    'defense',
    'scoring',
    'returning',
    'kicking',
    'punting'
]

# Used for aggregating seasonal passing totals
AGGREGATE_PASS_S = {
    'YDS': 'sum',
    'AVG': 'mean',
    'TD': 'sum',
    'INT': 'sum',
    'QBR': 'mean',
    'RTG': 'mean',
    'CMP': 'sum',
    'ATT': 'sum'
}

# Renaming passing columns
MAP_PASS_S = {
    'YDS': 'PASS YDS',
    'AVG': 'PASS AVG',
    'TD': 'PASS TD',
    'INT': 'PASS INT'
}

# Used for aggregating seasonal rushing totals
AGGREGATE_RUSH_S = {
    'CAR': 'sum',
    'YDS': 'sum',
    'AVG': 'mean',
    'TD': 'sum',
    'LONG': 'mean'
}

# Renaming rushing columns
MAP_RUSH_S = {
    'YDS': 'RUSH YDS',
    'AVG': 'RUSH AVG',
    'TD': 'RUSH TD',
    'LONG': 'RUSH LONG'
}

# Used for aggregating seasonal passing totals
AGGREGATE_REC_S = {
    'REC': 'sum',
    'YDS': 'sum',
    'AVG': 'mean',
    'TD': 'sum',
    'LONG': 'mean',
    'TGTS': 'sum'
}

# Renaming passing columns
MAP_REC_S = {
    'YDS': 'REC YDS',
    'AVG': 'REC AVG',
    'TD': 'REC TD',
    'LONG': 'REC LONG'
}