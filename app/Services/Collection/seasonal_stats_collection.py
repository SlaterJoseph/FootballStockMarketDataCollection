import json
import os
from pathlib import Path
from io import StringIO
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from Utils.constants import SEASON_STAT_URLS, URL_PAIRINGS
from .utils import clean_out_csvs


def build_csv_seasonal(years: list) -> None:
    """
    Builds the seasonal stat CSV
    :param years: The years to gather the stats of
    :return: None
    """
    clean_out_csvs('../../CSVs/Seasonally')
    driver = initialize_driver()

    for url, name in zip(SEASON_STAT_URLS, URL_PAIRINGS):
        df = None

        for year in years:
            df = build_csv(url, year, driver, df)

        df.reset_index(drop=True, inplace=True)
        df.to_csv(f'../../CSVs/Seasonally/{name}.csv')
    driver.quit()


def get_new_season(season: int) -> None:
    """
    Adds the new season to the CSV
    :param season: The new season
    :return: None
    """
    driver = initialize_driver()

    for url, name in zip(SEASON_STAT_URLS, URL_PAIRINGS):
        df = pd.read_csv(f'../../CSVs/Seasonally/{name}.csv', index_col=0)

        print(name)

        df = build_csv(url, season, driver, df)

        df.reset_index(drop=True, inplace=True)
        df.to_csv(f'../../CSVs/Seasonally/{name}.csv')
    driver.quit()

    # Archive the 4-year-old season
    archive_old_season(season - 3)


def archive_old_season(season: int) -> None:
    """
    Moves the 4-year-old season to the archived csvs and removes it from the active one
    :param season: The season to remove
    :return: None
    """
    dfs = dict()
    directory = '../../CSVs/Seasonally'

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            dfs[filename] = pd.read_csv(f, index_col=0)

    for name in dfs.keys():
        print(name)
        df = dfs[name]
        mask = (df['Season'] == season)
        filtered_df = df[mask]  # Removed the stats from 3 years ago
        df = df[~mask]  # Everything except the stats from years ago

        df.reset_index(drop=True, inplace=True)
        df.to_csv(f'{directory}/{name}')

        archived_path = Path(f'../../CSVs/Archived/Seasonally/{name}')
        if archived_path.exists():
            archived_df = pd.read_csv(archived_path, index_col=0)
        else:
            archived_df = pd.DataFrame(columns=df.columns)

        archived_df.reset_index(drop=True, inplace=True)
        result = pd.concat([archived_df, filtered_df])


def preprocess_names(name: str) -> (str, str):
    """
    A function to split the player and teams names into two separate columns
    Parameters
    ----------
    name - The name of the player
    Returns (str - Player name, str - Team(s) name)
    -------
    """
    with open('../../Utils/TeamConversions.json') as f:
        teams = json.load(f)['abbreviation_to_team']

    names = ['', '']
    if '/' in name:
        names = name.split('/')
        for team in teams.keys():
            if team in names[0]:
                names[1] = f'{team} / {names[1]}'
                names[0] = names[0][0:len(names[0]) - len(team)]
                break
    else:
        for team in teams.keys():
            if team in name:
                names[0] = name.replace(team, '')
                names[1] = team
                break

    return names[0], names[1]


def build_csv(url: str, year: int, driver: webdriver.Chrome, df: pd.DataFrame) -> pd.DataFrame:
    """
    The code which scrapes the league leaders from ESPN
    :param url: The url of the stat being scraped
    :param year: The season currently being worked on
    :param driver: The webdriver
    :param df: The blank df
    :return: The fully filled dataframe
    """
    used_url = url.replace('!', str(year))
    driver.get(used_url)

    try:
        show_more = driver.find_element(By.XPATH,
                                        '//*[@id="fittPageContainer"]/div[3]/div/div/section/div/div[4]/div[2]/a')
        while show_more:
            show_more.click()
            driver.implicitly_wait(0.3)

            try:
                show_more = driver.find_element(By.XPATH,
                                                '//*[@id="fittPageContainer"]/div[3]/div/div/section/div/div[4]/div[2]/a')

            # To stop the rest of the Show Mores
            except Exception:
                show_more = False
                continue

    # Incase there is no show more button
    except Exception:
        pass

    dfs = pd.read_html(StringIO(driver.page_source))
    names = dfs[0]
    stats = dfs[1]

    # Cleaning up and merging the dataframes
    names.drop('RK', axis=1, inplace=True)
    names[['Name', 'Teams']] = names['Name'].apply(lambda x: pd.Series(preprocess_names(x)))
    names['Season'] = year

    # the offensive and punting dfs don't have 2 layers of a header
    if 'view' in url and 'punting' not in url:
        stats.columns = stats.columns.droplevel(0)

    names = names.merge(stats, left_index=True, right_index=True)
    names = rename_columns(names, url)
    names.reset_index(drop=True)

    if df is None:
        df = names
    else:
        df.reset_index(drop=True, inplace=True)
        df = pd.concat([df, names], axis=0, ignore_index=True)

    return df


def initialize_driver() -> webdriver.Chrome:
    """
    Initializes a Chrome Webdriver
    :return: The webdriver
    """
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def rename_columns(df: pd.DataFrame, url: str) -> pd.DataFrame:
    """
    Renames duplicate columns
    :param df: The current dataframe
    :param url: The current url
    :return: The altered dataframe columns
    """
    # Changes duplicate columns to more classified columns
    if 'defense' in url:
        df.columns.values[8] = 'SACK YDS'
        df.columns.values[13] = 'INT YDS'
    elif 'special' in url and 'kicking' not in url and 'punting' not in url:
        df.columns.values[5] = 'K ATT'
        df.columns.values[6] = 'K YDS'
        df.columns.values[7] = 'K AVG'
        df.columns.values[8] = 'K LNG'
        df.columns.values[9] = 'K TD'
        df.columns.values[10] = 'P ATT'
        df.columns.values[11] = 'P YDS'
        df.columns.values[12] = 'P AVG'
        df.columns.values[13] = 'P LNG'
        df.columns.values[14] = 'P TD'
    elif 'punting' in url:
        df.columns.values[6] = 'P YDS'
        df.columns.values[8] = 'P AVG'
        df.columns.values[15] = 'PR YDS'
        df.columns.values[16] = 'PR AVG'

    return df
