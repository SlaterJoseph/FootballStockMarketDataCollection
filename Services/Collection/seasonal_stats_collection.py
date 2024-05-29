import json

import pandas
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from url_lists import season_stat_urls, url_pairings
from io import StringIO
from utils import clean_out_csvs


def build_csv_seasonal(years: list) -> None:
    """
    Uses ESPN's seasonal stats and compiles CSVs for the different groupings of stats
    Returns None
    -------
    """
    clean_out_csvs('../../CSVs/Seasonally')
    driver = initialize_driver()

    for url, name in zip(season_stat_urls, url_pairings):
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

    for url, name in zip(season_stat_urls, url_pairings):
        df = pd.read_csv(f'../../CSVs/Seasonally/{name}.csv')
        used_url = url.replace('!', str(season))
        driver.get(used_url)

        df = build_csv(used_url, season, driver, df)

        df.reset_index(drop=True, inplace=True)
        df.to_csv(f'../../CSVs/Seasonally/{name}.csv')


def archive_old_season(season: int) -> None:
    """
    Moves the 4-year-old season to the archived csvs and removes it from the active one
    :param season: The season to remove
    :return: None
    """
    for url, name in zip(season_stat_urls, url_pairings):
        csv = pd.read_csv(f'../../CSVs/Seasonally/{name}.csv')


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
                names[0].replace(f'{team}/', '')
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

    if not df.empty:
        df = pd.concat([df, names], axis=0)
    else:
        df = names

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

# get_new_season(2019)
