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

KEYWORD_COUNT_START = 3334
KEYWORD_COUNT_LIMIT = 15000
NUMBER_OF_CATEGORIES = 0                             # about 8500 items
KEYWORD_FREQ_LIMIT = 19999                              # Minimum keyword Frequency to parse statistics
KEYWORD_STATISTICS_WAIT = 3                             # Time in seconds to wait for the page to load
KEYWORD_STATISTICS_TRIES = 5
OTHER_ELEMENTS_TRIES = 2
REQUIRED_PLACE_INDEXES = (1, 2, 3, 4, 5)            # Set the positions for which we will collect statistics (from 1st)
# TODO - Rewrite to search for system `Downloads` directory
KEYWORDS_MONTH_PATH = r"D:\Downloads\requests_month.csv"    # Monthly statistics download file from Wildberries
KEYWORDS_WEEK_PATH = r"D:\Downloads\requests_week.csv"      # Weekly statistics download file from Wildberries
CATEGORY_VALUE_PATH = r"D:\Downloads\category_volume.csv"   # Revenue file by category
# TEMP_KEYWORDS_PATH = r"D:\Downloads\wb-template.csv"      # файл для выгрузки в кнопку бабло (функция не работает)
# OUTPUT_STAT = f'D:\\Downloads\\stat_{KEYWORD_COUNT_LIMIT}_{datetime.now().strftime("%d-%m-%Y")}.csv'
OUTPUT_STAT = f'D:\\Downloads\\stat_{datetime.now().strftime("%Y-%m-%d_%H-%M")}_[]_{KEYWORD_COUNT_LIMIT}.csv'
LOG_FILE = r'log.txt'
CATEGORY_TEXT_TO_URL_PATTERN = r'\[.+\]$'                        # RegEx pattern to create URL
PATTERN = re.compile(r'\[.+\]$')
DATETIME_FORMAT = r'%Y-%m-%d %H:%M:%S'


STAT_FILE_HEADERS = ['Запрос', 'Частотность в мес.', 'Частотность в нед.', 'Изменение мес/мес, %',
                     'Изменение нед/нед, %', 'Приоритетная категория (Кнопка Бабло)',
                     '1 место', '2 место', '3 место', '4 место', '5 место',
                     'Объем продаж категории, руб', 'Объем продаж по запросу, руб', 'Путь к категории (MP Stats)']
CATEGORY_FILE_HEADERS = ['ID', 'Путь категории', 'Объем продаж']


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


def get_keyword_stat(window_id: str, element_type: str, element_name: str, keyword: str,
                     settings: dict, sleep=0, repeat=2) -> dict:
    """
    Parse table with keywords statistic.
    We don't need to wait for the page to load as the webdriver settings have a default time for element search.
    This parameter is set in the module and is equal to 15 seconds.
    :param window_id:
    :param element_type:
    :param element_name:
    :param keyword: Searching keyword
    :param sleep: The waiting time for human-like interaction with an interface
    :param repeat: Number of reloads keyword statistic page before failed
    :return:
    """
    # time.sleep(sleep)
    # input key at text field
    bm.set_text(element_type, element_name, keyword.strip(), sleep=sleep, window_id=window_id)
    bm.click_key(element_type, element_name, key='enter', window_id=window_id)      # press ENTER on keyboard
    print(f'Keyword: "{keyword}"')

    categories = []
    bids = []
    for idx in range(KEYWORD_STATISTICS_TRIES):
        time.sleep(sleep)
        # check for statistic exists
        stat_exists = bm.find_elements(element_type=settings['keyword']['element_type'],
                                       element_name=settings['keyword']['element_name'],
                                       repeat=0, window_id=window_id)
        stat_not_exists = bm.find_elements(element_type=settings['last_requests']['element_type'],
                                       element_name=settings['last_requests']['element_name'],
                                       repeat=0, window_id=window_id)
        if stat_exists and stat_exists[0].text == keyword:
            # get `Prior categories` element
            cat_div = bm.find_elements(element_type=settings['prior_cat']['element_type'],
                                       element_name=settings['prior_cat']['element_name'],
                                       window_id=window_id)
            if cat_div:
                categories = cat_div[0].text.split('\n')        # if `Prior categories` element not empty get categories
                bids = parse_stat_table(window_id=window_id,
                                        element_type=settings['bids_table']['element_type'],
                                        element_name=settings['bids_table']['element_name'])  # get Bids
                break
        elif stat_not_exists:
            print(f'Wildberries returned empty data for keyword `{keyword}`')
            repeat = 0
            break

    if not bids and repeat:        # if `bids` is empty and `retry` != 0
        bm.reload_page(window_id)
        # time.sleep(sleep)
        get_keyword_stat(window_id=window_id, element_type=element_type, element_name=element_name,
                         keyword=keyword, settings=settings, sleep=sleep, repeat=repeat-1)

    return {'bids': bids, 'categories': categories}


def update_keywords(settings, account, webdriver_dir=None, window_id=None, log_it_in=True) -> None:
    """
    DEPRECATED
    :param settings:
    :param account:
    :param webdriver_dir:
    :param window_id:
    :param log_it_in:
    :return:
    """
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


def get_category_name(category_index: int, settings=None, account=None,
                      window_id=None, webdriver_dir=None, sleep=0) -> str:
    """

    :param settings:
    :param account:
    :param category_index:
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

    # PATTERN = re.compile(CATEGORY_TEXT_TO_URL_PATTERN)  # RegEx PATTERN to create Category ID URL
    # for idx in range(NUMBER_OF_CATEGORIES):
    #   repl = str(idx+1)                       # because we have not 0th category
    category_id_url = PATTERN.sub(str(category_index), settings['urls']['category_id'])    # create url with category id

    # Open keyword stat page
    # window_id = bm.open_window(category_id_url, sleep=1)
    bm.open_window(category_id_url, sleep=1)
    # Search for block with Category name string
    category_field = bm.find_elements(element_type=settings['category_name']['field_key'],
                                     element_name=settings['category_name']['field_value'],
                                     sleep=sleep, repeat=2, window_id=window_id)    # class: 'justify-content-start'
    if category_field:                      # If category exists, search included text element
        category_path = bm.find_elements(element_type=settings['category_name']['category_key'],
                                         element_name=settings['category_name']['category_value'],
                                         sleep=0, repeat=0, element=category_field[0])  # class: 'ml-1'

        category_path = re.sub(r"\s", "", category_path[1].text)         # delete spaces around slash character
        categories[category_index] = [category_path]
        # print(f'Category index: {category_index + 1}\nPath 2: `{category_path}`')
        return category_path
    else:
        print(f'Category {category_index} not found')
        return

    #     time.sleep(sleep)
    # bm.close_window(window_id)


def get_category_volume(category_name: str, window_id: str, settings=None, sleep=0) -> int:
    bm.change_tab(window_id)
    # create url with category name
    category_volume_url = PATTERN.sub(str(category_name), settings['urls']['category_volume'])
    bm.open_window(category_volume_url, sleep=2)
    time.sleep(sleep)


if __name__ == '__main__':

    # Open/Create `log.txt` file
    start_datetime = datetime.now()
    try:
        log = open(LOG_FILE, 'a', encoding='utf-8')  # Append date into exists `log` file
    except FileNotFoundError or FileExistsError as e:
        print(e)
        log = open(LOG_FILE, 'w', encoding='utf-8')  # Create `log` file
    except Exception as e:
        print(e)
    finally:
        log.write(f'START at: {start_datetime.strftime(DATETIME_FORMAT)}\n#########################')
        log.close()

    # TODO - Rewrite to use `DOM Ready` factor instead of sleeping. FIX - it doesn't work!!! Use time.time.sleep()
    # Load files with settings
    auth_to = {}                # Collects authentication objects
    tab_ids = {}              # Collects browser tab IDs
    settings = fm.load_json()  # Loading settings file
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)

    # Create Authentication objects
    bablo_btn_account_id = 0                    # id of account in the settings
    mp_stats_account_id = 1                     # id of account in the settings
    auth_to['bablo_btn'] = bm.Auth(account=api_keys['bablo_btn']['accounts'][bablo_btn_account_id],
                               login_data=settings['bablo_button'][bablo_btn_account_id]['login_data'])  # Auth object
    auth_to['mp_stats'] = bm.Auth(account=api_keys['mp_stats']['accounts'][mp_stats_account_id],
                                 login_data=settings['mpstats'][mp_stats_account_id]['login_data'])

    # Open/Create category ID, Name, Volume matching file and load category volume dict
    try:
        with open(CATEGORY_VALUE_PATH, 'r', newline='', encoding='utf-8') as f:
            category_volume_reader = csv.reader(f, delimiter=',')
            category_volume =\
                {cat_id: [name, volume] for cat_id, name, volume in category_volume_reader}

    except FileNotFoundError or FileExistsError as ex:
        print(ex)
        with open(CATEGORY_VALUE_PATH, 'w', newline='', encoding='utf-8') as f:
            category_volume_writer = csv.writer(f, dialect='excel')
            category_volume_writer.writerow(CATEGORY_FILE_HEADERS)
        category_volume = {}                    # to collect Category id with Name and Volume

    except Exception as ex:
        print(ex)

    # TODO - add `try/except` and script to download files from `Wildberries`
    # Create list of keywords month statistic with required frequency
    with open(KEYWORDS_MONTH_PATH, 'r', newline='', encoding='utf-8') as f:
        wb_stat_reader = csv.reader(f, delimiter=',')
        month_keywords = [(key, int(value)) for key, value in wb_stat_reader if int(value) > KEYWORD_FREQ_LIMIT]

    # Create dict of keywords with week statistic
    with open(KEYWORDS_WEEK_PATH, 'r', newline='', encoding='utf-8') as f:
        wb_stat_reader = csv.reader(f, delimiter=',')
        week_keywords = {key: int(value) for key, value in wb_stat_reader}

    # Create output data file with Headers
    output_stat_name = OUTPUT_STAT.replace('[]', str(len(month_keywords)))
    output_file = open(output_stat_name, 'w', newline='', encoding='utf-8', buffering=1)  # output statistic file
    output_stat_writer = csv.writer(output_file, dialect='excel')
    output_stat_writer.writerow(STAT_FILE_HEADERS)

    try:
        # Create Main browser window
        bm.DRIVER_PATH = settings['webdriver_dir']
        tab_ids['main'] = bm.open_window('https://google.com')

        # Open and login to `Bablo Button` account
        tab_ids['bablo_btn_0'] = bm.add_tab('')
        bm.open_window(settings['bablo_button'][bablo_btn_account_id]['urls']['login'])  # Open auth window for `MP Stats`
        auth_to['bablo_btn'](window_id=tab_ids['bablo_btn_0'])                   # call of `bablo_btn` Auth object

        # Go to keywords stat page
        bm.open_window(settings['bablo_button'][bablo_btn_account_id]['urls']['keywords'])

        # Open and login `MP Stats` account
        tab_ids['mp_stats_cat_id'] = bm.add_tab('')
        bm.open_window(settings['mpstats'][mp_stats_account_id]['urls']['login'])  # Open auth window for `MP Stats`
        auth_to['mp_stats'](window_id=tab_ids['mp_stats_cat_id'])                   # call of `mp_stats` Auth object
        # TODO get category path by id to create category volume url
        # Create url plug
        cat_volume_url = re.match(r'^.+\?', settings['mpstats'][mp_stats_account_id]['urls']['category_volume']).group()
        tab_ids['mp_stats_cat_volume'] = bm.add_tab(cat_volume_url)

        # Getting Category volume
        for cat_id in range(1, NUMBER_OF_CATEGORIES):
            cat_name = get_category_name(category_index=cat_id, settings=settings['mpstats'][mp_stats_account_id],
                              window_id=tab_ids['mp_stats_cat_id'], sleep=2)
            if cat_name:
                cat_volume = get_category_volume(category_name=cat_name, settings=settings['mpstats'][mp_stats_account_id],
                                                 window_id=tab_ids['mp_stats_cat_volume'], sleep=3)
                category_volume[cat_id] = [cat_name, cat_volume]

        # Getting statistics by keywords
        for idx, (keyword, month_frequency) in enumerate(month_keywords[KEYWORD_COUNT_START:KEYWORD_COUNT_LIMIT]):
            bm.change_tab(tab_ids['bablo_btn_0'])
            print(f'{idx + 1} / {KEYWORD_COUNT_LIMIT}')

            stat = get_keyword_stat(tab_ids['bablo_btn_0'], 'name', 'value', keyword=keyword,
                                    settings=settings['bablo_button'][bablo_btn_account_id]['keywords_stat'],
                                    sleep=KEYWORD_STATISTICS_WAIT, repeat=OTHER_ELEMENTS_TRIES)

            # keyword, month_frequency = keyword_and_freq[0], keyword_and_freq[1]
            week_frequency = week_keywords.pop(keyword, '')  # получаем значение недельной частотности

            # Если нашли элемент со статистикой категории, тогда сохраняем все прочие данные в таблицу
            if stat['categories']:
                cat_id = re.search(r'\d+', stat['categories'][0]).group()                       # Get category ID
                # Get Name and sales Volume for Category
                sales_volume = ''
                # cat_name, sales_volume = category_volume.get(cat_id, default=('', '')) # TODO solve problem
                # if cat_id in category_volume:
                #     sales_volume = category_volume[cat_id][1]
                # else:
                #     cat_name = get_category_name(cat_id, settings=settings['mpstats'][mp_stats_account_id],
                #                                  window_id=tab_ids['mp_stats_cat_id'])
                #     sales_volume = ''  # Volume of sales

                bids = [x[1] for x in stat['bids']]  # Required bids
                output_stats = [keyword, month_frequency, week_frequency, '', '', stat['categories'][0]]
                output_stats.extend(bids)
                output_stats.append(sales_volume)
                output_stat_writer.writerow(output_stats)
            else:
                # Если категория не обнаружена, значит в `Кнопке Бабло отсутствуют данные`
                output_stat_writer.writerow([keyword, month_frequency, week_frequency])
            print(stat)

        time.sleep(3)
        bm.close_window(tab_ids['main'])            # Stop browser
        total_exception = None
    except Exception as total_exception:
        print(total_exception)

    output_file.close()                         # Close output file

    finish_datetime = datetime.now()
    work_time = finish_datetime - start_datetime
    try:
        log = open(LOG_FILE, 'a', encoding='utf-8')  # Append date into exists `log` file
    except FileNotFoundError or FileExistsError as e:
        print(e)
        log = open(LOG_FILE, 'w', encoding='utf-8')  # Create `log` file
    except Exception as e:
        print(e)
    finally:
        log.write(f'\nFINISH at: {finish_datetime.strftime(DATETIME_FORMAT)}')
        if total_exception:
            log.write(f'with Exception:\n{total_exception}')
        log.write(f'\nTotal time: {work_time}, Total keywords: {len(month_keywords)}'
                  f'\n#########################\n')
        log.close()
