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

if __name__ == '__main__':
    # TODO - Rewrite to use `DOM Ready` factor instead of sleeping
    settings = fm.load_json()  # Loading settings file
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)
    mpstats_acc = api_keys['mp_stats']['accounts'][0]  # Login data for MP Stats
    bm.DRIVER_PATH = settings['webdriver_dir']
    print(settings)
    window_id = bm.open_window(settings['mpstats_url']['login'])
    # bm.input_text(window_id, 'id', 'email', mpstats_acc['login'], sleep=2)
    # bm.input_text(window_id, 'name', 'password', mpstats_acc['pass'])
    # bm.click_key(window_id, 'name', 'password')  # Just press ENTER instead of searching for a button

    time.sleep(2)
    bm.close_window(window_id)

    with open(TEMP_KEYWORDS_PATH, 'r', newline='') as f:
        # https://pythonworld.ru/moduli/modul-csv.html
        i = 0
        reader = csv.reader(f, delimiter=',')
        #print(help(reader))
        for raw in reader:
            if i < 0:
                print(', '.join(raw))
            else:
                break
            i += 1
