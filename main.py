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
from datetime import datetime
import re
from tqdm import tqdm

KEYWORD_COUNT_START = 952
KEYWORD_COUNT_LIMIT = 2
NUMBER_OF_CATEGORIES = 5                             # 8500
KEYWORD_STAT = False                                    # Using to switch on/off updating of Keywords statistics
CATEGORY_STAT = True                                    # Using to switch on/off updating of Categories statistics
KEYWORD_STATISTICS_WAIT = 3                             # Время в секундах на ожидание загрузки страницы
REQUIRED_PLACE_INDEXES = (1, 2, 3, 4, 5)            # Задаем позиции по которым будем собирать статистику (начиная с 1)
KEYWORDS_MONTH_PATH = r"D:\Downloads\requests_month.csv"  # будет заменено на поиск реального расположения папки
KEYWORDS_WEEK_PATH = r"D:\Downloads\requests_week.csv"  # будет заменено на поиск реального расположения папки
# TEMP_KEYWORDS_PATH = r"D:\Downloads\wb-template.csv"      # файл для выгрузки в кнопку бабло (функция не работает)
OUTPUT_STAT = f'D:\\Downloads\\stat_{KEYWORD_COUNT_LIMIT}_{datetime.now().strftime("%d-%m-%Y")}.csv'
LOG_FILE = r'log.txt'

HEADERS = ['Запрос', 'Частотность в мес.', 'Частотность в нед.', 'Изменение мес/мес, %', 'Изменение нед/нед, %',
           'Приоритетная категория', '1 место', '2 место', '3 место', '4 место', '5 место',
           'Объем продаж категории, руб', 'Объем продаж по запросу, руб']


def log_in(window_id: str, account: dict, login_data: dict, sleep=0):
    """
    Function to Log in
    :param window_id: Window object from Selenium
    :param account: Login data from api-keys, name and login
    :param login_data: Settings for searching text fields
    :return: None
    """
    bm.set_text(login_data['name_key'], login_data['name_value'], account['login'], sleep=sleep, window_id=window_id)   # Set name
    bm.set_text(login_data['pass_key'], login_data['pass_value'], account['pass'], sleep=sleep, window_id=window_id)    # Set pass
    bm.click_key(login_data['pass_key'], login_data['pass_value'], key='enter', sleep=sleep, window_id=window_id)


def parse_stat_table(window_id: str, element_type: str, element_name: str, sleep=0,
                     positions=REQUIRED_PLACE_INDEXES) -> list:
    """
    Gets bids for required positions
    :param element_type: element_type for searching statistics table
    :param element_name: element_value for searching statistics table
    :param sleep: waiting for page load
    :param positions: the set of indexes for searching bids value
    :return: list of tuples with position and bid
    """
    time.sleep(sleep)
    bids = []
    nums = []
    # gets all rows grom stat table
    rows = bm.find_elements(element_type=element_type, element_name=element_name, sleep=sleep)
    if rows:
        for p in positions:                 # searching only required positions
            # cells = rows[p-1].find_elements(By.TAG_NAME, 'div')         # lists start from `0` and that's why `p-1`
            cpm = ''
            try:
                cells = bm.find_elements(element_type='tag', element_name='div', element=rows[p-1], repeat=0)
                if cells:
                    nums = re.findall(r'\d+', cells[7].text)                    # we get only a number from value
                    # nums = re.findall(r'\d*\.\d+|\d+', s)                     # for float
                if nums:
                    cpm = [int(n) for n in nums][0]                             # we have only one number
            except IndexError as ie:
                print(ie)
            except Exception as e:
                print(e)
            finally:
                # print(f'Place Index: {p}, Bid: {cpm}')
                bids.append((p, cpm))
    return bids


def get_keyword_stat(window_id: str, element_type: str, element_name: str, keyword: str, settings: dict, sleep=0):
    """
    Parse table with keywords statistic.
    We don't need to wait for the page to load as the webdriver settings have a default time for element search.
    This parameter is set in the module and is equal to 15 seconds.
    :param window_id:
    :param element_type:
    :param element_name:
    :param keyword: Searching keyword
    :param sleep: The waiting time for human-like interaction with an interface
    :return:
    """
    time.sleep(sleep)
    bm.set_text(element_type, element_name, keyword, sleep=sleep, window_id=window_id)       # input key at text field
    bm.click_key(element_type, element_name, key='enter', window_id=window_id)      # press ENTER on keyboard
    print(f'Keyword: "{keyword}"')

    categories = []
    bids = []
    time.sleep(sleep)
    cat_div = bm.find_elements(element_type=settings['prior_cat']['element_type'],
                               element_name=settings['prior_cat']['element_name'])  # get `Prior categories` element
    if cat_div:
        categories = cat_div[0].text.split('\n')            # if `Prior categories` element not empty get categories
        bids = parse_stat_table(window_id=window_id,
                                element_type=settings['bids_table']['element_type'],
                                element_name=settings['bids_table']['element_name'])  # get Bids REQUIRED_PLACE_INDEXES
    return {'bids': bids, 'categories': categories}


def update_keywords(settings, account, webdriver_dir='drivers/chromedriver.exe') -> None:
    # keywords_week = {}
    # Создаем словарь всех значений для недельной частотности ключей
    with open(KEYWORDS_WEEK_PATH, 'r', newline='', encoding='utf-8') as f:
        wb_stat_reader = csv.reader(f, delimiter=',')
        keywords_week = {key: f'{int(value):,}'.replace(',', ' ') for key, value in wb_stat_reader}

    # Load settings to variables
    bm.DRIVER_PATH = webdriver_dir
    # account = api_keys['bablo_btn']['accounts'][0]  # login data for `bablo button`

    # Start to use browser
    window_id = bm.open_window(settings['login'])  # open window with `bablo button`
    log_in(window_id=window_id, account=account, login_data=settings['login_data'])  # log in at `Bablo Button`

    # Open keyword stat page
    bm.open_window(settings['keywords'], sleep=1)
    with open(KEYWORDS_MONTH_PATH, 'r', newline='', encoding='utf-8') as f:
        i = 0
        wb_stat_reader = csv.reader(f, delimiter=',')  # open wildberries data file

        with open(LOG_FILE, 'a', encoding='utf-8', buffering=1) as log:  # log file
            log.write(f'\nSTART at: {time.strftime("%H:%M:%S", time.localtime())}\n#########################')

            with open(OUTPUT_STAT, 'w', newline='', encoding='utf-8', buffering=1) as stat:  # output statistic file
                output_stat_writer = csv.writer(stat, dialect='excel')
                output_stat_writer.writerow(HEADERS)

                for raw in wb_stat_reader:
                    if not raw:
                        continue
                    if i < KEYWORD_COUNT_LIMIT:
                        print(f'{i + 1} / {KEYWORD_COUNT_LIMIT}')
                        stat = get_keyword_stat(window_id, 'name', 'value', raw[0],
                                                settings=settings['keywords_stat'],
                                                sleep=KEYWORD_STATISTICS_WAIT)
                        # with open(LOG_FILE, 'a', encoding='utf-8') as log:
                        keyword, month_frequency = raw[0], f'{int(raw[1]):,}'.replace(',', ' ')
                        week_frequency = keywords_week.pop(keyword, '')  # получаем значение недельной частотности
                        # log.write(f'\n"{keyword}" - {month_frequency}\n{stat}')

                        # Если нашли элемент со статистикой категории, тогда сохраняем все прочие данные в таблицу
                        if stat['categories']:
                            bids = [x[1] for x in stat['bids']]  # Required bids
                            sales_volume = ''  # Volume of sales
                            output_stats = [keyword, month_frequency, week_frequency, '', '', stat['categories'][0]]
                            output_stats.extend(bids)
                            output_stats.append(sales_volume)
                            output_stat_writer.writerow(output_stats)
                            # output_stat_writer.writerow([keyword, frequency, '', '', '',
                            #                              stat['categories'][0],
                            #                              stat['bids'][0][1],
                            #                              stat['bids'][1][1],
                            #                              stat['bids'][2][1],
                            #                              stat['bids'][3][1],
                            #                              stat['bids'][4][1],
                            #                              ''])
                        else:
                            # Если категория не обнаружена, значит в `Кнопке Бабло отсутствуют данные`
                            output_stat_writer.writerow([keyword, month_frequency, week_frequency])
                        print(stat)
                    else:
                        break
                    i += 1

            log.write(f'\nEND at: {time.strftime("%H:%M:%S", time.localtime())}\n#########################')

    time.sleep(1)
    bm.close_window(window_id)


def update_categories(settings, account, webdriver_dir='drivers/chromedriver.exe'):
    bm.DRIVER_PATH = webdriver_dir

    # Start to use browser
    window_id = bm.open_window(settings['login'])  # Open auth window for `MP Stats`
    input_elements = bm.find_elements(element_type='class', element_name='input-form', window_id=window_id)
    # TODO - rewrite use `log_in()` function
    # log_in(window_id=window_id, account=account, login_data=settings['login_data'])     # Enter login data
    # TODO - rewrite to choose fields by name, not by index
    bm.set_text(element=input_elements[0], element_type='tag', element_name='input', data=account['login'])
    bm.set_text(element=input_elements[1], element_type='tag', element_name='input', data=account['pass'])
    bm.click_element(element=input_elements[2], element_type='tag', element_name='input')

    pattern = re.compile(r'\[.+\]$')  # RegEx pattern to create Category ID URL
    for idx in range(NUMBER_OF_CATEGORIES):
        repl = str(idx+1)                       # because we have not 0th category
        category_id_url = pattern.sub(repl, settings['category_id'])

        # Open keyword stat page
        window_id = bm.open_window(category_id_url, sleep=1)
        #
        time.sleep(5)
    bm.close_window(window_id)


if __name__ == '__main__':
    # TODO - Rewrite to use `DOM Ready` factor instead of sleeping. FIX - it doesn't work!!! Use time.time.sleep()
    # Load files with settings
    settings = fm.load_json()  # Loading settings file
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)
    if KEYWORD_STAT:
        update_keywords(settings=settings['bablo_button'][0],
                        account=api_keys['bablo_btn']['accounts'][0],
                        webdriver_dir=settings['webdriver_dir'])
    if CATEGORY_STAT:
        update_categories(settings=settings['mpstats'][0],
                          account=api_keys['mp_stats']['accounts'][0],
                          webdriver_dir=settings['webdriver_dir'])
