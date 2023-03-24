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
# https://ru.stackoverflow.com/questions/1236375/%D0%9A%D0%B0%D0%BA-%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B8%D1%82%D1%8C-%D0%BF%D1%83%D1%82%D0%B8-%D0%BA-%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D1%8B%D0%BC-%D0%BF%D0%B0%D0%BF%D0%BA%D0%B0%D0%BC-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D0%A0%D0%B0%D0%B1%D0%BE%D1%87%D0%B8%D0%B9-%D1%81%D1%82%D0%BE%D0%BB-%D0%97%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B8-%D0%B8-%D1%82


def log_in(window_id: str, account: dict, name_key: str, name_value: str, pass_key: str, pass_value: str):
    bm.input_text(window_id, name_key, name_value, account['login'], sleep=2)
    bm.input_text(window_id, pass_key, pass_value, account['pass'])
    bm.click_key(window_id, pass_key, pass_value)           # Just press ENTER instead of searching for a button


if __name__ == '__main__':
    # TODO - Rewrite to use `DOM Ready` factor instead of sleeping
    settings = fm.load_json()  # Loading settings file
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)

    bm.DRIVER_PATH = settings['webdriver_dir']

    window_id = bm.open_window(settings['mpstats_url']['login'])        # open window with MP Stats
    mpstats_acc = api_keys['mp_stats']['accounts'][0]                   # login data for MP Stats
    # log in at MP Stats
    log_in(window_id=window_id, account=mpstats_acc, name_key='id', name_value='email',
           pass_key='name', pass_value='password')

    # window_id = bm.open_window(settings['bablo_url']['login'])  # login bablo

    time.sleep(2)
    bm.close_window(window_id)

    with open(TEMP_KEYWORDS_PATH, 'r', newline='') as f:
        # https://pythonworld.ru/moduli/modul-csv.html
        i = 0
        reader = csv.reader(f, delimiter=',')
        # print(help(reader))
        for raw in reader:
            if i < 0:
                print(', '.join(raw))
            else:
                break
            i += 1
