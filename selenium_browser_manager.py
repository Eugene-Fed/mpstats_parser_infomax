import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

DRIVER_PATH = r'drivers/chromedriver.exe'
USER_DATA_DIR = r'Default'
CHROME_PROFILE_NAME = r'Default'
CHROME_PROFILE_PATH = r'C:\Users\eugen\AppData\Local\Google\Chrome\User Data'           # main
WB_URL = r'https://seller.wildberries.ru/'
# TIMEOUT = 15                          # Time to waiting of page load. But doesn't work
SLEEP = 2
REPEAT = 3


# Настройте параметры профиля для сохранения данных в нем
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
# options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument('--allow-profiles-outside-user-dir')
# options.add_argument('--enable-profile-shortcut-manager')
# options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")      # ссылка на папку, c профилями Chrome
# options.add_argument(f"--profile-directory={CHROME_PROFILE_NAME}")  # имя папки профиля Chrome

s = Service(executable_path=DRIVER_PATH)
driver = webdriver.Chrome(service=s, options=options)
# driver.timeouts.implicit_wait = TIMEOUT
# driver.implicitly_wait(TIMEOUT)
# driver.set_page_load_timeout(TIMEOUT)


def open_window(url: str, sleep=SLEEP) -> str:
    """
    Open browser window and return it'd ID
    :param url: Gets url to open window
    :param sleep: Time to sleep before open new window in seconds
    :return: Window id to manipulate
    """
    try:
        # driver.maximize_window()
        time.sleep(sleep)
        driver.get(url)
        return driver.current_window_handle         # возвращаем ID текущего открытого окна
    except Exception as ex:
        print(ex)


def close_window(handler: str):
    try:
        driver.switch_to.window(handler)
        driver.close()
        driver.quit()
    except Exception as ex:
        print("WINDOW NOT AVAILABLE")
        print(ex)


def find_elements(element_type: str, element_name: str, sleep=SLEEP, repeat=REPEAT, element=None):
    """
    :param element_type: Type of element for search
    :param element_name: Element name value
    :param sleep:
    :param repeat: Try to reload page to find element
    :param element:
    :return: Found element
    """
    # TODO - Use Optional parameter `element` to searching
    if element:
        search_in = element
    else:
        search_in = driver

    if element_type == 'id':
        elements_input = search_in.find_elements(By.ID, element_name)
    elif element_type == 'name':
        elements_input = search_in.find_elements(By.NAME, element_name)
    elif element_type == 'class':
        elements_input = search_in.find_elements(By.CLASS_NAME, element_name)
    elif element_type == 'css':
        elements_input = search_in.find_elements(By.CSS_SELECTOR, element_name)
    elif element_type == 'tag':
        elements_input = search_in.find_elements(By.TAG_NAME, element_name)
    elif element_type == 'link':
        elements_input = search_in.find_elements(By.LINK_TEXT, element_name)
    elif element_type == 'xpath':
        elements_input = search_in.find_elements(By.XPATH, element_name)
    elif element_type == 'partial':
        elements_input = search_in.find_elements(By.PARTIAL_LINK_TEXT, element_name)

    if not elements_input:
        if repeat:
            reload_page(sleep=sleep)
            return find_elements(element_type=element_type,
                                 element_name=element_name, repeat=repeat - 1)     # recursion call
        else:
            print(f"Element '{element_type}' -> '{element_name}' doesn't found")
            # elements_input = []
            # raise Exception         # TODO - change to validate exception type
    return elements_input


def reload_page(handler='', sleep=SLEEP):
    try:
        if handler:
            driver.switch_to.window(handler)
        time.sleep(sleep * 2)  # if element was not found than wait for 10 seconds, reload page and try again
        driver.refresh()
        time.sleep(sleep)
    except Exception as ex:
        print(ex)


def set_text(handler: str, element_type: str, element_name: str, data: str, sleep=SLEEP):
    # TODO Rewrite to search elements by several tags with recursion
    """
    Manipulating with text input fields
    :param handler: Window ID for manipulating
    :param element_type: Type  of searching element
    :param element_name: Name of searching element
    :param data: Data to input
    :param sleep: Sleeping time in seconds
    :return: None
    """
    time.sleep(sleep)

    # TODO - rewrite to use Exception from `main.py` instead use it here
    try:
        driver.switch_to.window(handler)
        element_input = find_elements(element_type, element_name)    # temporarily pick up only the first element
        if element_input:
            element_input[0].clear()
            element_input[0].send_keys(data)

    except Exception as ex:
        print(ex)


def click_element(handler: str, element_type: str, element_name: str, sleep=SLEEP):
    """
    Manipulating with text input fields
    :param handler: Window ID for manipulating
    :param element_type: Type of finding element
    :param element_name: Name of finding element
    :param sleep: Sleeping time in seconds
    :return: None
    """
    time.sleep(sleep)
    try:
        driver.switch_to.window(handler)
        element_click = find_elements(element_type, element_name)[0]
        element_click.click()

    except Exception as ex:
        print("Element doesn't found")
        print(ex)


def click_key(handler: str, element_type: str, element_name: str, key='enter', sleep=SLEEP):
    """
    Manipulating with text input fields
    :param handler: Window ID for manipulating
    :param element_type: Type of finding element
    :param element_name: Name of finding element
    :param key: Name of button to press
    :param sleep: Sleeping time in seconds
    :return: None
    """
    time.sleep(sleep)
    try:
        driver.switch_to.window(handler)
        element_click = find_elements(element_type, element_name)[0]
        if key == 'enter':
            element_click.send_keys(Keys.ENTER)
        else:
            pass        # TODO to write

    except Exception as ex:
        print("Element doesn't found")
        print(ex)


if __name__ == '__main__':
    print(help(dict))
