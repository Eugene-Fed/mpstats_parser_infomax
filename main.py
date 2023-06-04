# -*- coding: UTF-8 -*-

import requests
import json
import csv
import sys
import file_manager as fm  # Управление файлами настроек, паролей и т.п.
import importlib            # used for reload `selenium_browser_manager` module
import selenium_browser_manager as bm  # Управление браузером
from selenium.webdriver.common.by import By
from itertools import product
from pathlib import Path
import time
from datetime import datetime
import re
from argparse import ArgumentParser

BABLO_BTN_ACCOUNT_ID = 0  # id of account in the settings
MP_STATS_ACCOUNT_ID = 1  # id of account in the settings
CATEGORY_COUNT_START = 1                                 # 2920
CATEGORY_COUNT_LIMIT = 8500                                # about 8 500 items
KEYWORD_COUNT_START = 1
KEYWORD_COUNT_LIMIT = 0                             # if `0` than non limited
KEYWORD_FREQ_LIMIT = 19999                              # Minimum keyword Frequency to parse statistics
STATISTICS_WAIT = 2                             # Time in seconds to wait for the page to load
KEYWORD_STATISTICS_TRIES = 4
CATEGORY_STATISTICS_TRIES = 7
REQUIRED_PLACE_INDEXES = (1, 2, 3, 4, 5)            # Set the positions for which we will collect statistics (from 1st)
RELOAD_WINDOW = 500                               # Промежуточная перезагрузка страницы на случай непредвиденных проблем
# TODO - Rewrite to search for system `Downloads` directory
KEYWORDS_MONTH_PATH = r"D:/Downloads/requests_month.csv"    # Monthly statistics download file from Wildberries
KEYWORDS_WEEK_PATH = r"D:/Downloads/requests_week.csv"      # Weekly statistics download file from Wildberries
CATEGORY_VALUE_PATH = r"D:/Downloads/category_volume.csv"   # Revenue file by category
# TEMP_KEYWORDS_PATH = r"D:\Downloads\wb-template.csv"      # файл для выгрузки в кнопку бабло (функция не работает)
# output_stat_path = f'stat_{datetime.now().strftime("%Y-%m-%d_%H-%M")}_[]-{KEYWORD_COUNT_LIMIT}.csv'
# output_stat_path = f'D:/Downloads/stat_{KEYWORD_COUNT_LIMIT}_{datetime.now().strftime("%d-%m-%Y")}.csv'
LOG_FILE = r'log.txt'
CATEGORY_TEXT_TO_URL_PATTERN = r'\[.+\]$'                        # RegEx pattern to create URL
PATTERN = re.compile(r'\[.+\]$')
DATETIME_FORMAT = r'%Y-%m-%d %H:%M:%S'


STAT_FILE_HEADERS = ['Запрос', 'Частотность в мес. (WB)', 'Частотность в нед. (WB)', 'Изменение мес/мес, %',
                     'Изменение нед/нед, %', 'Приоритетная категория (MP Stats)',
                     '1 место, руб.', '2 место, руб.', '3 место, руб.', '4 место, руб.', '5 место, руб.',
                     'Объем продаж категории, руб (MP Stats)', 'Объем продаж по фразе, руб (MP Stats)',
                     'ID Категории (Кнопка Бабло)']
# CATEGORY_FILE_HEADERS = ['ID', 'Путь категории', 'Объем продаж']
CATEGORY_FILE_HEADERS = [0] * 3         # [0, 0, 0]


def create_parser() -> ArgumentParser:
    """
    Start parameters parser
    :return: an ArgumentParser object
    """
    parser = ArgumentParser()
    parser.add_argument('-ks', '--key_start', default=KEYWORD_COUNT_START)
    parser.add_argument('-kl', '--key_limit', default=KEYWORD_COUNT_LIMIT)
    parser.add_argument('-kt', '--key_tries', default=KEYWORD_STATISTICS_TRIES)
    parser.add_argument('-fl', '--freq_limit', default=KEYWORD_FREQ_LIMIT)
    parser.add_argument('-cs', '--cat_start', default=CATEGORY_STATISTICS_TRIES)
    parser.add_argument('-cl', '--cat_limit', default=CATEGORY_COUNT_LIMIT)
    parser.add_argument('-ct', '--cat_tries', default=CATEGORY_STATISTICS_TRIES)
    parser.add_argument('-w', '--wait', default=STATISTICS_WAIT)
    parser.add_argument('-r', '--reload_window', default=RELOAD_WINDOW)

    return parser


def log_in(account: dict, login_data: dict, sleep=0, key='enter',
           element=None, window_id=None, submit_button=False, skladchina=False) -> None:
    """
    DEPRECATED Function to Log in
    :param window_id: Window object from Selenium
    :param account: Login data from api-keys, name and login
    :param login_data: Settings for searching text fields
    :param skladchina: Use to toggle login algorithm
    :return: None
    """
    # TODO - deprecate `skladchina`
    '''
    if skladchina:
        input_elements = bm.find_elements(element_type='class', element_name='input-form', window_id=window_id)
        bm.set_text(element=input_elements[0], element_type=settings['login_data']['name_key'],
                    element_name=settings['login_data']['name_value'], data=account['login'])
        bm.set_text(element=input_elements[1], element_type=settings['login_data']['pass_key'],
                    element_name=settings['login_data']['pass_value'], data=account['pass'])
        bm.click_element(element=input_elements[2], element_type=settings['login_data']['button_key'],
                         element_name=settings['login_data']['button_value'])
    else:
    '''
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


def parse_bids_table(window_id: str, element_type: str, element_name: str, sleep=0,
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
    # gets all rows grom stat table
    rows = bm.find_elements(element_type=element_type, element_name=element_name, sleep=sleep)
    if rows:
        for p in positions:                 # searching only required positions
            # cells = rows[p-1].find_elements(By.TAG_NAME, 'div')         # lists start from `0` and that's why `p-1`
            cpm = ''
            cat_id = ''
            try:
                cells = bm.find_elements(element_type='tag', element_name='div', element=rows[p-1], repeat=0)
                if cells:
                    nums = re.findall(r'\d+', cells[7].text)                    # we get only a number from value
                    # nums = re.findall(r'\d*\.\d+|\d+', s)                     # for float
                    if nums:
                        cpm = [int(n) for n in nums][0]                         # we have only one number
                    cat_id = cells[-2].text                                     # get prior category ID for current SKU
            except IndexError as ie:
                print(ie)
            except Exception as e:
                print(e)
            finally:
                # print(f'Place Index: {p}, Bid: {cpm}, Cat ID: {cat_id}')
                bids.append((p, cpm, cat_id))
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
    bm.click_key(element_type, element_name, key='enter', window_id=window_id, sleep=0)      # press ENTER on keyboard
    print(f'Keyword: "{keyword}"')

    categories = []
    bids = []
    for idx in range(KEYWORD_STATISTICS_TRIES):
        # time.sleep(sleep)
        # check for statistic exists
        stat_exists = bm.find_elements(element_type=settings['keyword']['element_type'],
                                       element_name=settings['keyword']['element_name'],
                                       repeat=0, window_id=window_id, sleep=sleep)
        stat_not_exists = bm.find_elements(element_type=settings['last_requests']['element_type'],
                                       element_name=settings['last_requests']['element_name'],
                                       repeat=0, window_id=window_id)
        if stat_exists and stat_exists[0].text == keyword:
            # get `Bids`
            bids = parse_bids_table(window_id=window_id,
                                    element_type=settings['bids_table']['element_type'],
                                    element_name=settings['bids_table']['element_name'],
                                    sleep=sleep)  # get Bids
            # get `Prior categories` element
            cat_div = bm.find_elements(element_type=settings['prior_cat']['element_type'],
                                       element_name=settings['prior_cat']['element_name'],
                                       window_id=window_id)
            if cat_div:
                categories = cat_div[0].text.split('\n')        # if `Prior categories` element not empty get categories
            else:
                categories.append(bids[0][2])           # get category ID from bids table
            break

        elif stat_not_exists:
            print(f'WILDBERRIES returned empty data for keyword "{keyword}"')
            repeat = 0
            break

    if not bids and repeat:        # if `bids` is empty and `retry` != 0
        bm.reload_page(window_id, sleep=sleep)
        # time.sleep(sleep)
        return get_keyword_stat(window_id=window_id, element_type=element_type, element_name=element_name,
                                keyword=keyword, settings=settings, sleep=sleep, repeat=repeat-1)
    else:
        return {'bids': bids, 'categories': categories}


def get_category_volume(category_index: int, settings=None, account=None,
                        window_id=None, webdriver_dir=None, sleep=0, repeat=0, reload=False) -> tuple:
    """

    :param settings:
    :param account:
    :param category_index:
    :param window_id: Browser tab ID. If set it than `webdriver_dir` not needed
    :param webdriver_dir:
    :param sleep:
    :return: Name of searching category
    """

    category_id_url = PATTERN.sub(str(category_index), settings['urls']['category_id'])    # create url with category id

    if window_id:       # if we created new tab before use `get_category_volume` then change it
        bm.change_tab(window_id)
        bm.create_window(category_id_url, sleep=0)
    else:
        if webdriver_dir:                       # When we use in separately - create new window. Else - use window_id
            bm.DRIVER_PATH = webdriver_dir
            window_id = bm.create_window(category_id_url, sleep=0)    # We don't use this `window_id`
        else:
            print('`window_id` and `webdriver_dir` not set')
            return

    # Search for block with Category name string
    category_field = bm.find_elements(element_type=settings['category_name']['field_key'],
                                      element_name=settings['category_name']['field_value'],
                                      sleep=sleep, repeat=repeat, window_id=window_id,
                                      reload=reload)    # class: 'justify-content-start'
    if category_field:                      # If category exists, search included text element
        category_path = bm.find_elements(element_type=settings['category_name']['category_key'],
                                         element_name=settings['category_name']['category_value'],
                                         sleep=0, repeat=0, element=category_field[0])  # class: 'ml-1'

        # category_path = re.sub(r"\s", "", category_path[1].text)         # delete spaces around slash character
        category_path = category_path[1].text
    else:
        print(f'Category {category_index} not found')
        return '', ''

    content_id = settings['tags_n_paths']['BVID']       # this ID is used for search content data block

    # Click 'Category' tab for open page with categories volume file
    bm.click_element(element_type='id',
                     element_name=f'__BVID__{content_id}___BV_tab_button__',
                     sleep=sleep,
                     window_id=window_id,
                     repeat=repeat)

    # TODO - rewrite to use it in settings
    cat_volume_xpath = \
        f'//*[@id="__BVID__{content_id}"]/div/div[4]/div/div/div[2]/div[2]/div[3]/div[2]/div/div/div[1]/div[5]'
    cat_volume_elements = bm.find_elements(element_type='xpath',
                                           element_name=cat_volume_xpath,
                                           window_id=window_id,
                                           sleep=sleep,
                                           repeat=repeat)

    if cat_volume_elements:             # `element.text` has format like `1 020 345 Р`
        cat_vol = int(''.join(re.findall(r'\d+', cat_volume_elements[0].text)))     # get number from format text
        # categories[category_index].append(cat_vol)
        return category_path, cat_vol  # TODO - maybe use tuple instead of list
    else:
        return category_path, ''


def create_browser_window(settings: dict, accounts: dict, tab_ids={}, sleep=0) -> dict:
    """
    Create new browser window and log in to accounts
    :param settings: main settings from file
    :param accounts: dict of accounts IDs to use it in settings object
    :param tab_ids: collects IDs of opened tabs in browser. it will be returned
    :return:
    """
    # Create Main browser window
    # TODO - rewrite to use autoload webdriver library
    bm.DRIVER_PATH = settings['webdriver_dir']
    tab_ids['main'] = bm.create_window('https://google.com')

    # Open and login to `Bablo Button` account
    tab_ids['bablo_btn_0'] = bm.add_tab('')
    bm.create_window(settings['bablo_button'][accounts['bablo_btn_id']]['urls']['login'])
    auth_to['bablo_btn'](window_id=tab_ids['bablo_btn_0'], sleep=sleep)  # call of `bablo_btn` Auth object

    # Go to keywords stat page
    bm.create_window(settings['bablo_button'][accounts['bablo_btn_id']]['urls']['keywords'], sleep=sleep)

    # Open and login `MP Stats` account
    tab_ids['mp_stats_cat_id'] = bm.add_tab('')
    bm.create_window(settings['mpstats'][accounts['mp_stats_id']]['urls']['login'])  # Open auth window for `MP Stats`
    auth_to['mp_stats'](window_id=tab_ids['mp_stats_cat_id'], sleep=sleep)  # call of `mp_stats` Auth object

    # Create url plug
    # cat_volume_url = re.match(r'^.+\?', settings['mpstats'][accounts['mp_stats_id']]['urls']['cat_id_name_volume']).group()
    # tab_ids['mp_stats_cat_volume'] = bm.add_tab(cat_volume_url)
    return tab_ids


if __name__ == '__main__':
    parser = create_parser()
    params = parser.parse_args(sys.argv[1:])

    # Open/Create `log.txt` file
    start_datetime = datetime.now()
    # TODO - create log_file_writer() function
    try:
        log = open(LOG_FILE, 'a', encoding='utf-8')  # Append date into exists `log` file
        log.write(f'\n')
    except FileNotFoundError or FileExistsError as e:
        print(e)
        log = open(LOG_FILE, 'w', encoding='utf-8')  # Create `log` file
    except Exception as e:
        print(e)
    finally:
        log.write(f'#########################\n'
                  f'START at: {start_datetime.strftime(DATETIME_FORMAT)}\n')
        log.close()

    # Load files with settings
    auth_to = {}                # Collects authentication objects
    tab_ids = {}              # Collects browser tab IDs
    settings = fm.load_json()  # Loading settings file
    api_keys_file = Path(settings['api-keys_dir']) / Path(settings['api-keys_file'])
    api_keys = fm.load_json(file=api_keys_file)

    # TODO - replace two variables with a dictionary in the following code
    accounts_ids = {'bablo_btn_id': BABLO_BTN_ACCOUNT_ID, 'mp_stats_id': MP_STATS_ACCOUNT_ID}

    # Create Authentication objects
    auth_to['bablo_btn'] = bm.Auth(account=api_keys['bablo_btn']['accounts'][BABLO_BTN_ACCOUNT_ID],
                                   login_data=settings['bablo_button'][BABLO_BTN_ACCOUNT_ID]['login_data'])
    auth_to['mp_stats'] = bm.Auth(account=api_keys['mp_stats']['accounts'][MP_STATS_ACCOUNT_ID],
                                  login_data=settings['mpstats'][MP_STATS_ACCOUNT_ID]['login_data'])

    # Open/Create category ID, Name, Volume matching file and load category volume dict
    try:
        with open(CATEGORY_VALUE_PATH, 'r', newline='', encoding='utf-8') as f:
            category_volume_reader = csv.reader(f, delimiter=',')
            cat_id_name_volume =\
                {int(cat_id): (name, volume) for cat_id, name, volume in category_volume_reader}
            number_of_cat_volume = len(cat_id_name_volume) - 1
            print(f'Number of categories in file: {number_of_cat_volume}')

    except FileNotFoundError or FileExistsError as ex:
        print(ex)
        with open(CATEGORY_VALUE_PATH, 'w', newline='', encoding='utf-8') as f:
            category_volume_writer = csv.writer(f, dialect='excel')
            category_volume_writer.writerow(CATEGORY_FILE_HEADERS)
            # category_volume_writer.writerow([])
        cat_id_name_volume = {}                    # to collect Category id with Name and Volume

    except Exception as ex:
        print(ex)

    # TODO - add `try/except` and script to download files from `Wildberries`
    # Create list of keywords month statistic with required frequency
    with open(KEYWORDS_MONTH_PATH, 'r', newline='', encoding='utf-8') as f:
        wb_stat_reader = csv.reader(f, delimiter=',')
        # month_keywords = [(key, int(value)) for key, value in wb_stat_reader if int(value) > KEYWORD_FREQ_LIMIT]
        month_keywords = [(key, int(value)) for key, value in wb_stat_reader if int(value) > int(params.freq_limit)]

    # Create dict of keywords with week statistic
    with open(KEYWORDS_WEEK_PATH, 'r', newline='', encoding='utf-8') as f:
        wb_stat_reader = csv.reader(f, delimiter=',')
        week_keywords = {key: int(value) for key, value in wb_stat_reader}

    # recalc key_limit with `0` to `non limit`
    if 0 < int(params.key_limit) < len(month_keywords):
        key_limit = int(params.key_limit)
    elif 0 < settings['constants']['KEYWORD_COUNT_LIMIT'] < len(month_keywords):
        key_limit = settings['constants']['KEYWORD_COUNT_LIMIT']
    else:
        key_limit = len(month_keywords)

    # Create output data file with Headers
    # TODO - make this path dynamic, not hardcoded
    # output_stat_path = f'D:\\Downloads\\stat_{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{key_limit}-[].csv'
    # output_stat_name = output_stat_path.replace('[]', str(len(month_keywords)))
    output_stat_name = \
        f'D:\\Downloads\\stat_{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{key_limit}-{len(month_keywords)}.csv'
    output_file = open(output_stat_name, 'w', newline='', encoding='utf-8', buffering=1)  # output statistic file
    output_stat_writer = csv.writer(output_file, dialect='excel')
    output_stat_writer.writerow(STAT_FILE_HEADERS)

    start_keyword_id = int(params.key_start)        # save next keyword id to getting stat. starts from 0
    start_category_id = int(params.cat_start)            # save next category id to getting stat. starts from 0

    try:
        while start_keyword_id <= key_limit:        # `len(month_keywords)` or `key_limit`
            """
            Create new browser window after any crash while current `start_keyword_id` less than total keyword count
            or keywords count limit from CONST or keywords count limit from startup parameters.
            """
            try:
                bm = importlib.reload(bm)  # reload module before using
                tab_ids = create_browser_window(settings=settings, accounts=accounts_ids, sleep=int(params.wait))
                # keyword_start_from =\
                #    int(params.key_start) + start_keyword_id - 1  # If process was broken we will start from last ID

                # ---------- GET KEYWORD STATISTICS ----------
                # for idx, (keyword, month_frequency) in \
                #        enumerate(month_keywords[keyword_start_from:int(params.key_limit)]):
                # for idx, (keyword, month_frequency) in \
                #        enumerate(month_keywords[start_keyword_id-1:int(params.key_limit)]):

                # `start_keyword_id` stars from `1`
                for keyword, month_frequency in month_keywords[start_keyword_id - 1:key_limit]:
                    bm.change_tab(tab_ids['bablo_btn_0'])
                    # print(f'{keyword_start_from + 1 + idx} / {len(month_keywords)}')
                    print(f'{start_keyword_id} / {key_limit}')

                    stat = get_keyword_stat(tab_ids['bablo_btn_0'], 'name', 'value', keyword=keyword,
                                            settings=settings['bablo_button'][BABLO_BTN_ACCOUNT_ID]['keywords_stat'],
                                            sleep=int(params.wait), repeat=int(params.key_tries))

                    # keyword, month_frequency = keyword_and_freq[0], keyword_and_freq[1]
                    week_frequency = week_keywords.pop(keyword, '')  # получаем значение недельной частотности

                    # Если нашли элемент со статистикой категории, тогда сохраняем все прочие данные в таблицу
                    cat_volume = ''
                    if stat['categories']:
                        cat_id = int(re.search(r'\d+', stat['categories'][0]).group())    # Get the first (main) category ID
                        # Get Name and sales Volume for Category
                        # TODO - TEMPORARY HIDDEN
                        # cat_data, cat_volume = cat_id_name_volume.get(cat_id, default=('', ''))      # TODO solve problem
                        if cat_id in cat_id_name_volume:
                            # cat_id_name_volume = {int(cat_id): (str(cat_path), int(cat_volume))}
                            cat_name, cat_volume = cat_id_name_volume[cat_id]
                        else:
                            cat_name, cat_volume = get_category_volume(cat_id,
                                                                       settings=settings['mpstats'][MP_STATS_ACCOUNT_ID],
                                                                       window_id=tab_ids['mp_stats_cat_id'],
                                                                       sleep=int(params.wait),
                                                                       repeat=int(params.cat_tries))
                            # append new category data into dict
                            cat_id_name_volume[cat_id] = (cat_name, cat_volume)

                            # add new category data into file
                            with open(CATEGORY_VALUE_PATH, 'a', newline='', encoding='utf-8') as f:
                                category_volume_writer = csv.writer(f, dialect='excel')
                                category_file_row = [cat_id, cat_name, cat_volume]  # create list of data to add in file
                                # category_file_row.extend(cat_data)  # reshape dict to list
                                print(f'category_file_row len: {category_file_row}')
                                category_volume_writer.writerow(category_file_row)

                        bids = [x[1] for x in stat['bids']]  # Required bids
                        # output_stats = [keyword, month_frequency, week_frequency, '', '', stat['categories'][0]]
                        output_stats = [keyword, month_frequency, week_frequency, '', '', cat_name]
                        output_stats.extend(bids)
                        output_stats.extend([cat_volume, '', cat_id])
                        output_stat_writer.writerow(output_stats)
                    else:
                        # TODO - use `type` and `name` from settings instead of hardcoded text or use current page url
                        # if `login` page - relog in
                        if bm.find_elements(element_type='name', element_name='password'):
                            print(f"Un login at: {datetime.now()}")
                            with open(LOG_FILE, 'a', encoding='utf-8') as log:
                                # TODO - create log_file_writer() function
                                log.write(f'Un Login at: {datetime.now().strftime(DATETIME_FORMAT)}. '
                                          f'Current Keyword ID: {start_keyword_id}\n')
                            break

                        # If category not found then `Bablo Button` hasn't data.
                        output_stat_writer.writerow([keyword, month_frequency, week_frequency])
                    print(stat)
                    start_keyword_id += 1  # Remember element ID for the next slice of keywords list

                    # Reload page for every 500 responses
                    if start_keyword_id // int(params.reload_window) == start_keyword_id / int(params.reload_window):
                        for tab_id in tab_ids.values():
                            bm.close_window(handler=tab_id)
                # ---------- GET KEYWORD STATISTICS ---------- END

                print(f'Number of NEW categories in file: {len(cat_id_name_volume)-1-number_of_cat_volume}')
                # break                                       # Exit from `While True` loop
            except Exception as total_exception:
                print(total_exception)
                with open(LOG_FILE, 'a', encoding='utf-8') as log:
                    # TODO - create log_file_writer() function
                    log.write(f'Exception at: {datetime.now().strftime(DATETIME_FORMAT)}. '
                              f'Current Keyword ID: {start_keyword_id}\n')
            finally:
                # pass
                try:
                    bm.destroy_window(tab_ids['main'])  # Stop browser
                except Exception as ex:
                    print(ex)
                    # break                                       # Exit from `While True` loop

    except Exception as main_loop_exception:
        print(f'EXCEPTION: {main_loop_exception}')

    finally:
        output_file.close()                         # Close output file

        finish_datetime = datetime.now()
        work_time = finish_datetime - start_datetime
        # TODO - create log_file_writer() function
        try:
            log = open(LOG_FILE, 'a', encoding='utf-8')  # Append date into exists `log` file
        except FileNotFoundError or FileExistsError as e:
            print(e)
            log = open(LOG_FILE, 'w', encoding='utf-8')  # Create `log` file
        except Exception as e:
            print(e)
        finally:
            log.write(f'FINISH at: {finish_datetime.strftime(DATETIME_FORMAT)}\n')
            # if total_exception:
            #     log.write(f'with Exception:\n{total_exception}')
            log.write(f'Total time: {work_time}, '
                      f'Total keywords: {key_limit}\n'
                      f'Number of NEW categories in file: {len(cat_id_name_volume)-1-number_of_cat_volume}\n'
                      f'#########################\n')
            log.close()
