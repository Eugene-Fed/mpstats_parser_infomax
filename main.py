# -*- coding: UTF-8 -*-

import requests
import json
import csv
import sys
import file_manager as fm  # Управление файлами настроек, паролей и т.п.
import selenium_browser_manager as bm  # Управление браузером
from selenium.webdriver.common.by import By
from pathlib import Path
import time
import re
from tqdm import tqdm

TEMP_KEYWORDS_PATH = r"D:\Downloads\requests.csv"  # будет заменено на поиск реального расположения папки
# TEMP_KEYWORDS_PATH = r"D:\Downloads\wb-template.csv"      # файл для выгрузки в кнопку бабло (функция не работает)
KEYWORD_COUNT_LIMIT = 100
REQUIRED_PLACE_INDEXES = (1, 3, 5)                   # Задаем позиции по которым будем собирать статистику (начиная с 1)


def log_in(window_id: str, account: dict, login_data: dict):
    """
    Function to Log in
    :param window_id: Window object from Selenium
    :param account: Login data from api-keys, name and login
    :param login_data: Settings for searching text fields
    :return: None
    """
    bm.set_text(window_id, login_data['name_key'], login_data['name_value'], account['login'], sleep=2)   # Set name
    bm.set_text(window_id, login_data['pass_key'], login_data['pass_value'], account['pass'], sleep=1)    # Set password
    bm.click_key(window_id, login_data['pass_key'], login_data['pass_value'], key='enter', sleep=1)       # Press ENTER


def parse_stat_table(field_tag_name: str, field_tag_value: str, sleep=0, positions=REQUIRED_PLACE_INDEXES) -> list:
    """
    Gets bids for required positions
    :param field_tag_name: element_type for searching statistics table
    :param field_tag_value: element_value for searching statistics table
    :param sleep: waiting for page load
    :param positions: the set of indexes for searching bids value
    :return: list of tuples with position and bid
    """
    time.sleep(sleep)
    bids = []
    rows = bm.find_elements(element_type=field_tag_name, name=field_tag_value)      # gets all rows grom stat table
    for p in positions:                 # searching only required positions
        cells = rows[p-1].find_elements(By.TAG_NAME, 'div')         # lists start from `0` and that's why `p-1`
        nums = re.findall(r'\d+', cells[7].text)                    # we get only a number from value
        # nums = re.findall(r'\d*\.\d+|\d+', s)                     # for float
        cpm = [int(n) for n in nums][0]                             # we have only one number
        # print(f'Place Index: {p}, Bid: {cpm}')
        bids.append((p, cpm))
    return bids


def get_key_stat(window_id: str, field_tag_name, field_tag_value, keyword, sleep=3):
    bm.set_text(window_id, field_tag_name, field_tag_value, keyword, sleep=sleep)       # input key at text field
    bm.click_key(window_id, field_tag_name, field_tag_value, key='enter', sleep=1)      # press ENTER on keyboard
    print(f'Keyword: "{keyword}"')

    categories = []
    bids = []
    time.sleep(sleep)
    cat_div = bm.find_elements(element_type='class', name='sc-frJOEA')  # get `Prior categories` element
    if cat_div:
        categories = cat_div[0].text.split('\n')            # if `Prior categories` element not empty get categories
        bids = parse_stat_table('class', 'MuiDataGrid-row')  # get Bids for `REQUIRED_PLACE_INDEXES`
    return {'bids': bids, 'categories': categories}


if __name__ == '__main__':
    # TODO - Rewrite to use `DOM Ready` factor instead of sleeping
    settings = fm.load_json()  # Loading settings file
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)

    bm.DRIVER_PATH = settings['webdriver_dir']

    stat_account = settings['bablo_url']
    window_id = bm.open_window(stat_account['login'])  # open window with `bablo button`
    account = api_keys['bablo_btn']['accounts'][0]  # login data for `bablo button`

    log_in(window_id=window_id, account=account, login_data=stat_account['login_data'])       # log in at `Bablo Button`

    # open keyword stat page
    bm.open_window(stat_account['keywords'], sleep=5)
    with open(TEMP_KEYWORDS_PATH, 'r', newline='', encoding='utf-8') as f:
        i = 0
        reader = csv.reader(f, delimiter=',')
        # print(help(reader))

        with open('stat.txt', 'a') as f:  # log file
            f.write(f'\n{time.strftime("%H:%M:%S", time.localtime())}\n#########################')

        for raw in reader:
            if i < KEYWORD_COUNT_LIMIT:
                print(f'{i} / {KEYWORD_COUNT_LIMIT}')
                stat = get_key_stat(window_id, 'name', 'value', raw[0], sleep=6)
                with open('stat.txt', 'a', encoding='utf-8') as f:
                    keyword, frequency = raw[0], f'{int(raw[1]):,}'.replace(',', ' ')
                    f.write(f'\n"{keyword}" - {frequency}\n{stat}')
                print(stat)
            else:
                break
            i += 1

    time.sleep(1)
    bm.close_window(window_id)

