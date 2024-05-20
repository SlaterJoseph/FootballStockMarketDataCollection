import datetime
import glob
import os
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from url_lists import season_stat_urls, url_pairings
from io import StringIO

years = datetime.date.today().year
years = [years - x - 1 for x in range(3)]


def build_csv_seasonal():
    """
    Uses ESPN's seasonal stats and compiles CSVs for the different groupings of stats
    Returns None
    -------
    """
    try:
        files = glob.glob(os.path.join('../CSVs/Seasonally', '*'))
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
    except OSError:
        print("Error occurred while deleting files.")

    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    for url, name in zip(season_stat_urls, url_pairings):
        df = None

        for year in years:
            used_url = url.replace('!', str(year))
            print(used_url)
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

            if year != years[0]:
                df = pd.concat([df, names], axis=0)
            else:
                df = names

        df.reset_index(drop=True, inplace=True)
        df.to_csv(f'../../CSVs/Seasonally/{name}.csv')
    driver.quit()


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
