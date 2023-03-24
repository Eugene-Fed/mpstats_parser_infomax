# -*- coding: UTF-8 -*-

import requests
import json
import sys
import file_manager as fm           # Управление файлами настроек, паролей и т.п.
import selenium_browser_manager as bm        # Управление запуском браузера
from pathlib import Path
import time


if __name__ == '__main__':
    # TODO - Rewtrite to use `DOM Ready` factor instead of sleeping
    settings = fm.load_json()       # Loading settings file
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)
    mpstat_acc = api_keys['mp_stats']['accounts'][0]        # Сюда мы получаем логин/пароль МП Статс
    bm.DRIVER_PATH = settings['webdriver_dir']
    print(settings)
    window_id = bm.open_window(settings['mpstats_url']['login'])
    bm.input_text(window_id, 'id', 'email', mpstat_acc['login'], sleep=2)
    bm.input_text(window_id, 'name', 'password', mpstat_acc['pass'])
    bm.click_key(window_id, 'name', 'password')     # Just press ENTER instead of searching for a button

    time.sleep(6)
    bm.close_window(window_id)



