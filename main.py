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
KEYWORD_COUNT_LIMIT = 3
NUMBER_OF_CATEGORIES = 5                             # about 8500 items
KEYWORD_STAT = False                                    # Using to switch on/off updating of Keywords statistics
CATEGORY_STAT = True                                    # Using to switch on/off updating of Categories statistics
KEYWORD_STATISTICS_WAIT = 3                             # Time in seconds to wait for the page to load
REQUIRED_PLACE_INDEXES = (1, 2, 3, 4, 5)            # Set the positions for which we will collect statistics (from 1st)
# TODO - Rewrite to search for system `Downloads` directory
KEYWORDS_MONTH_PATH = r"D:\Downloads\requests_month.csv"    # Monthly statistics download file from Wildberries
KEYWORDS_WEEK_PATH = r"D:\Downloads\requests_week.csv"      # Weekly statistics download file from Wildberries
CATEGORY_VALUE_PATH = r"D:\Downloads\category_volume.csv"   # Revenue file by category
# TEMP_KEYWORDS_PATH = r"D:\Downloads\wb-template.csv"      # файл для выгрузки в кнопку бабло (функция не работает)
OUTPUT_STAT = f'D:\\Downloads\\stat_{KEYWORD_COUNT_LIMIT}_{datetime.now().strftime("%d-%m-%Y")}.csv'
LOG_FILE = r'log.txt'
CATEGORY_ID_PATTERN = r'\[.+\]$'                        # RegEx pattern to create Category ID URL


STAT_FILE_HEADERS = ['Запрос', 'Частотность в мес.', 'Частотность в нед.', 'Изменение мес/мес, %',
                     'Изменение нед/нед, %', 'Приоритетная категория',
                     '1 место', '2 место', '3 место', '4 место', '5 место',
                     'Объем продаж категории, руб', 'Объем продаж по запросу, руб']
CATEGORY_FILE_HEADERS = ['ID', 'Название', 'Объем продаж']


def log_in(account: dict, login_data: dict, sleep=0, key='enter',
           element=None, window_id=None, submit_button=False, skladchina=False) -> None:
    """
    Function to Log in
    :param window_id: Window object from Selenium
    :param account: Login data from api-keys, name and login
    :param login_data: Settings for searching text fields
    :param skladchina: Use to toggle login algorithm
    :return: None
    """

    if skladchina:
        input_elements = bm.find_elements(element_type='class', element_name='input-form', window_id=window_id)
        bm.set_text(element=input_elements[0], element_type=settings['login_data']['name_key'],
                    element_name=settings['login_data']['name_value'], data=account['login'])
        bm.set_text(element=input_elements[1], element_type=settings['login_data']['pass_key'],
                    element_name=settings['login_data']['pass_value'], data=account['pass'])
        bm.click_element(element=input_elements[2], element_type=settings['login_data']['button_key'],
                         element_name=settings['login_data']['button_value'])
    else:
        bm.set_text(element_type=login_data['name_key'], element_name=login_data['name_value'],
                    data=account['login'], sleep=sleep, window_id=window_id, element=element)   # Set name
        bm.set_text(element_type=login_data['pass_key'], element_name=login_data['pass_value'],
                    data=account['pass'], sleep=sleep, window_id=window_id, element=element)    # Set pass
        if submit_button:                                                                       # If given than click Button
            bm.click_element(element_type=account['button_key'], element_name=account['button_value'],
                             sleep=sleep, window_id=window_id, element=element)
        else:                                                                           # Else press Key
            bm.click_key(element_type=login_data['pass_key'], element_name=login_data['pass_value'],
                         key=key, sleep=sleep, window_id=window_id)


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


def update_keywords(settings, account, webdriver_dir=None, window_id=None, log_it_in=True) -> None:

    if window_id:       # if we created new tab before then change it
        bm.change_tab(window_id)
    # keywords_week = {}
    # Создаем словарь всех значений для недельной частотности ключей
    with open(KEYWORDS_WEEK_PATH, 'r', newline='', encoding='utf-8') as f:
        wb_stat_reader = csv.reader(f, delimiter=',')
        keywords_week = {key: f'{int(value):,}'.replace(',', ' ') for key, value in wb_stat_reader}

    # Load settings to variables
    if webdriver_dir:
        bm.DRIVER_PATH = webdriver_dir

    # TODO: Rewrite to log in before using `update_keywords` fucntion instead of setting `log_in` flag
    if log_it_in:
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
                output_stat_writer.writerow(STAT_FILE_HEADERS)

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
                        else:
                            # Если категория не обнаружена, значит в `Кнопке Бабло отсутствуют данные`
                            output_stat_writer.writerow([keyword, month_frequency, week_frequency])
                        print(stat)
                    else:
                        break
                    i += 1

            log.write(f'\nEND at: {time.strftime("%H:%M:%S", time.localtime())}\n#########################')

    # time.sleep(1)
    # bm.close_window(window_id)


def get_category_name(idx: int, settings=None, account=None,
                      window_id=None, webdriver_dir=None, sleep=0) -> str:
    """

    :param settings:
    :param account:
    :param idx:
    :param window_id: Browser tab ID. If set it than `webdriver_dir` not needed
    :param webdriver_dir:
    :param sleep:
    :return: Name of searching category
    """
    categories = {}  # Collection of Category ID, Name and Volume

    if window_id:       # if we created new tab before use `get_category_name` then change it
        bm.change_tab(window_id)
    else:
        if webdriver_dir:                       # When we use in separately - create new window. Else - use window_id
            bm.DRIVER_PATH = webdriver_dir
            # window_id = bm.open_window('')    # We doesn't use this `window_id`
        else:
            print('`window_id` and `webdriver_dir` not set')
            return

    pattern = re.compile(CATEGORY_ID_PATTERN)  # RegEx pattern to create Category ID URL
    # for idx in range(NUMBER_OF_CATEGORIES):
    #   repl = str(idx+1)                       # because we have not 0th category
    category_id_url = pattern.sub(str(idx), settings['urls']['category_id'])        # create url with category id

    # Open keyword stat page
    window_id = bm.open_window(category_id_url, sleep=1)
    # Search for block with Category name string
    category_field = bm.find_elements(element_type=settings['category_name']['field_key'],
                                     element_name=settings['category_name']['field_value'],
                                     sleep=sleep, repeat=2, window_id=window_id)    # class: 'justify-content-start'
    if category_field:                      # If category exists, search included text element
        category_path = bm.find_elements(element_type=settings['category_name']['category_key'],
                                         element_name=settings['category_name']['category_value'],
                                         sleep=0, repeat=0, element=category_field[0])  # class: 'ml-1'

        category_path = re.sub(r"\s", "", category_path[1].text)         # delete spaces around slash character
        categories[idx] = [category_path]
        print(f'Category index: {idx+1}\nPath 2: `{category_path}`')
        return category_path
    else:
        print(f'Category {idx} not found')
        return

    #     time.sleep(sleep)
    # bm.close_window(window_id)


if __name__ == '__main__':
    # TODO - Rewrite to use `DOM Ready` factor instead of sleeping. FIX - it doesn't work!!! Use time.time.sleep()
    # Load files with settings
    settings = fm.load_json()  # Loading settings file
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)

    # Open/Create category ID, Name, Volume matching file and load category volume dict
    try:
        with open(CATEGORY_VALUE_PATH, 'r', newline='', encoding='utf-8') as f:
            category_volume_reader = csv.reader(f, delimiter=',')
            category_volume =\
                {cat_id: [name, volume] for cat_id, name, volume in category_volume_reader}

    except FileNotFoundError as ex:
        print(ex)
        with open(CATEGORY_VALUE_PATH, 'w', newline='', encoding='utf-8') as f:
            category_volume_writer = csv.writer(f, dialect='excel')
            category_volume_writer.writerow(CATEGORY_FILE_HEADERS)
        category_volume = {}                    # to collect Category id with Name and Volume

    except Exception as ex:
        print(ex)


    # Create Main browser window
    bm.DRIVER_PATH = settings['webdriver_dir']
    browser_main_window = bm.open_window('https://google.com')
    bablo_btn_account_id = 0                    # id of account in the settings
    mp_stats_account_id = 1                     # id of account in the settings

    # Open and login to `Bablo Button` account
    browser_keyword_tab = bm.add_tab('')
    bm.open_window(settings['bablo_button'][bablo_btn_account_id]['urls']['login'])  # Open auth window for `MP Stats`
    log_in(window_id=browser_keyword_tab,
           account=api_keys['bablo_btn']['accounts'][bablo_btn_account_id],
           login_data=settings['bablo_button'][bablo_btn_account_id]['login_data'])
    bm.open_window(settings['bablo_button'][bablo_btn_account_id]['urls']['keywords'])
    # update_keywords(settings=settings['bablo_button'][bablo_btn_account_id],
    #                 account=api_keys['bablo_btn']['accounts'][bablo_btn_account_id],
    #                 window_id=browser_keyword_tab)

    # Open and login `MP Stats` account
    browser_category_name_tab = bm.add_tab('')
    bm.open_window(settings['mpstats'][mp_stats_account_id]['urls']['login'])  # Open auth window for `MP Stats`
    log_in(window_id=browser_category_name_tab,
           account=api_keys['mp_stats']['accounts'][mp_stats_account_id],
           login_data=settings['mpstats'][mp_stats_account_id]['login_data'],
           submit_button=False)  # Enter login data
    browser_category_volume_tab = bm.add_tab('')

    # for idx in range(1, 4):
    #     print(get_category_name(idx=idx, settings=settings['mpstats'][mp_stats_account_id],
    #                       window_id=browser_category_name_tab, sleep=2))
    # Create list of keywords with month statistic
    with open(KEYWORDS_MONTH_PATH, 'r', newline='', encoding='utf-8') as f:
        wb_stat_reader = csv.reader(f, delimiter=',')
        keywords_week = [(key, int(f'{value:,}'.replace(',', ' '))) for key, value in wb_stat_reader]

    # Create dict of keywords with week statistic
    with open(KEYWORDS_WEEK_PATH, 'r', newline='', encoding='utf-8') as f:
        wb_stat_reader = csv.reader(f, delimiter=',')
        keywords_week = {key: f'{int(value):,}'.replace(',', ' ') for key, value in wb_stat_reader}

    time.sleep(5)
    bm.close_window(browser_main_window)            # stop browser
