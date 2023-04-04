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
TIMEOUT = 15                          # Time to waiting of page load. But doesn't work
SLEEP = 0


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


def find_elements(element_type: str, name: str):
    """
    :param element_type: Type of element for search
    :param name: Element name value
    :return: Found element
    """
    # TODO Waiting DOM ready before try to search any element
    if element_type == 'id':
        elements_input = driver.find_elements(By.ID, name)
    elif element_type == 'name':
        elements_input = driver.find_elements(By.NAME, name)
    elif element_type == 'class':
        elements_input = driver.find_elements(By.CLASS_NAME, name)
    elif element_type == 'css':
        elements_input = driver.find_elements(By.CSS_SELECTOR, name)
    elif element_type == 'tag':
        elements_input = driver.find_elements(By.TAG_NAME, name)
    elif element_type == 'link':
        elements_input = driver.find_elements(By.LINK_TEXT, name)
    elif element_type == 'xpath':
        elements_input = driver.find_elements(By.XPATH, name)
    elif element_type == 'partial':
        elements_input = driver.find_elements(By.PARTIAL_LINK_TEXT, name)

    return elements_input


def set_text(handler: str, element: str, name: str, data: str, sleep=SLEEP):
    # TODO Rewrite to search elements by several tags with recursion
    """
    Manipulating with text input fields
    :param handler: Window ID for manipulating
    :param element: Type  of searching element
    :param name: Name of searching element
    :param data: Data to input
    :param sleep: Sleeping time in seconds
    :return: None
    """
    time.sleep(sleep)

    repeat = True
    while repeat:         # if element doesn't fond - refresh page
        # TODO - rewrite to use Exception from `main.py` instead use it here
        try:
            driver.switch_to.window(handler)
            element_input = find_elements(element, name)[0]    # temporarily pick up only the first element
            element_input.clear()
            element_input.send_keys(data)
            repeat = False          # if element was found than exit from loop

        except Exception as ex:
            print(f"Element '{element}' -> '{name}' doesn't found")
            print(ex)
            time.sleep(int(SLEEP)*2)      # if element was not found than wait for 10 seconds, reload page and try again
            driver.refresh()


def click_element(handler: str, element: str, name: str, sleep=SLEEP):
    """
    Manipulating with text input fields
    :param handler: Window ID for manipulating
    :param element: Type of finding element
    :param name: Name of finding element
    :param sleep: Sleeping time in seconds
    :return: None
    """
    time.sleep(sleep)
    try:
        driver.switch_to.window(handler)
        element_click = find_elements(element, name)[0]
        element_click.click()

    except Exception as ex:
        print("Element doesn't found")
        print(ex)


def click_key(handler: str, element: str, name: str, key='enter', sleep=SLEEP):
    """
    Manipulating with text input fields
    :param handler: Window ID for manipulating
    :param element: Type of finding element
    :param name: Name of finding element
    :param key: Name of button to press
    :param sleep: Sleeping time in seconds
    :return: None
    """
    time.sleep(sleep)
    try:
        driver.switch_to.window(handler)
        element_click = find_elements(element, name)[0]
        if key == 'enter':
            element_click.send_keys(Keys.ENTER)
        else:
            pass        # TODO to write

    except Exception as ex:
        print("Element doesn't found")
        print(ex)


if __name__ == '__main__':
    print(help(driver.find_elements))




#
# try:
#     driver.maximize_window()
#     driver.get(WB_URL)
#     time.sleep(50)
# except Exception as ex:
#     print(ex)
# finally:
#     driver.close()
#     driver.quit()
