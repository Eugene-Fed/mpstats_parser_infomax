# -*- coding: UTF-8 -*-

import requests
import json
import sys
import file_manager as fm           # Управление файлами настроек, паролей и т.п.
import browser_manager as bm        # Управление запуском браузера
from pathlib import Path
import time


if __name__ == '__main__':
    settings = fm.load_json()       # загружаем файл настроек (создаем, если он отсутствовал)
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)
    mpstat_acc = api_keys['mp_stats']['accounts'][0]        # Сюда мы получаем логин/пароль МП Статс
    bm.DRIVER_PATH = settings['webdriver_dir']
    print(settings)
    window_id = bm.open_window(settings['mpstats_url']['login'])
    time.sleep(10)
    bm.close_window(window_id)



