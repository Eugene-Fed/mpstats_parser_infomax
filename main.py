# -*- coding: UTF-8 -*-

import requests
import json
import csv
import sys
import file_manager as fm  # Управление файлами настроек, паролей и т.п.
import selenium_browser_manager as bm  # Управление запуском браузера
from pathlib import Path
import time

TEMP_KEYWORDS_PATH = r"D:\Downloads\requests.csv"  # будет заменено на поиск реального расположения папки
# TEMP_KEYWORDS_PATH = r"D:\Downloads\wb-template.csv"
KEYWORD_COUNT_LIMIT = 5
# https://ru.stackoverflow.com/questions/1236375/%D0%9A%D0%B0%D0%BA-%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B8%D1%82%D1%8C-%D0%BF%D1%83%D1%82%D0%B8-%D0%BA-%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D1%8B%D0%BC-%D0%BF%D0%B0%D0%BF%D0%BA%D0%B0%D0%BC-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D0%A0%D0%B0%D0%B1%D0%BE%D1%87%D0%B8%D0%B9-%D1%81%D1%82%D0%BE%D0%BB-%D0%97%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B8-%D0%B8-%D1%82


def set_text(window_id: str, field_tag_name: str, field_tag_value: str, text: str, sleep=1):
    """
    Interface to use Parser functions
    :param window_id:
    :param field_tag_name: Type of tag to search
    :param field_tag_value: Value for tag to search
    :param text: Text to set in field
    :param sleep:
    :return: None
    """
    bm.input_text(handler=window_id, element=field_tag_name, name=field_tag_value, data=text, sleep=sleep)


def press_key(window_id: str, field_tag_name: str, field_tag_value: str, key='enter', sleep=1):
    bm.click_key(handler=window_id, element=field_tag_name, name=field_tag_value, key=key, sleep=sleep)


def log_in(window_id: str, account: dict, login_data: dict):
    """
    Function to Log in
    :param window_id: Window object from Selenium
    :param account: Login data from api-keys, name and login
    :param login_data: Settings for searching text fields
    :return: None
    """
    set_text(window_id, login_data['name_key'], login_data['name_value'], account['login'], sleep=2)   # Input name
    set_text(window_id, login_data['pass_key'], login_data['pass_value'], account['pass'])         # Input password
    press_key(window_id, login_data['pass_key'], login_data['pass_value'])   # Press ENTER for send login form


def get_key_stat(window_id: str, field_tag_name, field_tag_value, keyword, sleep=3):
    set_text(window_id, field_tag_name=field_tag_name, field_tag_value=field_tag_value, text=keyword, sleep=sleep)
    press_key(window_id, field_tag_name=field_tag_name, field_tag_value=field_tag_value, sleep=sleep)
    return keyword


if __name__ == '__main__':
    # TODO - Rewrite to use `DOM Ready` factor instead of sleeping
    settings = fm.load_json()  # Loading settings file
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)

    bm.DRIVER_PATH = settings['webdriver_dir']

    stat_account = settings['bablo_url']
    window_id = bm.open_window(stat_account['login'])  # open window with MP Stats
    account = api_keys['bablo_btn']['accounts'][0]  # login data for MP Stats
    # log in at Btn Bablo
    log_in(window_id=window_id, account=account, login_data=stat_account['login_data'])

    # open keyword stat page
    bm.open_window(stat_account['keywords'], sleep=5)
    with open(TEMP_KEYWORDS_PATH, 'r', newline='', encoding='utf-8') as f:
        # https://pythonworld.ru/moduli/modul-csv.html
        i = 0
        reader = csv.reader(f, delimiter=',')
        # print(help(reader))
        for raw in reader:
            if i < KEYWORD_COUNT_LIMIT:
                print(get_key_stat(window_id, 'name', 'value', raw[0], sleep=6))
            else:
                break
            i += 1

    time.sleep(5)
    bm.close_window(window_id)

