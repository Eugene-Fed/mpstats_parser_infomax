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
REPEAT = 0


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


class Auth:
    def __init__(self, account: dict, login_data: dict, key='enter', skladchina=False):
        """
        Account authentication
        :param account: Collects types and values of DOM-elements
        :param login_data: Collects account name and password
        :param key: Set keyboard key to push
        :param skladchina: DEPRECATED - Set external account method for authentication
        """
        self.account = account
        self.login_data = login_data
        self.key = key
        self.skladchina = skladchina

    def __call__(self, window_id=None, element=None, sleep=0, submit_button=False):
        if self.skladchina:     # TODO - deprecate this `if` because `skladchina` was been deprecated
            input_elements = find_elements(element_type='class', element_name='input-form', window_id=window_id)
            acc_name = {
                'element': input_elements[0],
                'element_type': self.settings['login_data']['name_key'],
                'element_name': self.settings['login_data']['name_value'],
                'data': self.account['login'],
                'sleep': sleep,
                'window_id': window_id
            }
            acc_pass = {
                'element': input_elements[1],
                'element_type': self.settings['login_data']['pass_key'],
                'element_name': self.settings['login_data']['pass_value'],
                'data': self.account['pass'],
                'sleep': sleep,
                'window_id': window_id
            }
            submit_button = {
                'element': input_elements[2],
                'element_type': self.settings['login_data']['button_key'],
                'element_name': self.settings['login_data']['button_value'],
                'sleep': sleep,
                'window_id': window_id
            }

        else:
            acc_name = {
                'element_type': self.login_data['name_key'],
                'element_name': self.login_data['name_value'],
                'data': self.account['login'],
                'sleep': sleep,
                'window_id': window_id,
                'element': element
            }
            acc_pass = {
                'element_type': self.login_data['pass_key'],
                'element_name': self.login_data['pass_value'],
                'data': self.account['pass'],
                'sleep': sleep,
                'window_id': window_id,
                'element': element
            }
            if 'button_key' in self.account:
                submit_button = {
                    'element_type': self.account['button_key'],
                    'element_name': self.account['button_value'],
                    'sleep': sleep,
                    'window_id': window_id,
                    'element': element
                }
            else:
                submit_key = {
                    'element_type': self.login_data['pass_key'],
                    'element_name': self.login_data['pass_value'],
                    'key': self.key,
                    'sleep': sleep,
                    'window_id': window_id
                }
            # set_text(element_type=self.login_data['name_key'], element_name=self.login_data['name_value'],
            #          data=self.account['login'], sleep=self.sleep, window_id=self.window_id,
            #          element=self.element)  # Set name
            # set_text(element_type=self.login_data['pass_key'], element_name=self.login_data['pass_value'],
            #          data=self.account['pass'], sleep=self.sleep, window_id=self.window_id,
            #          element=self.element)  # Set pass
            # if self.submit_button:  # If given than click Button
            #     click_element(element_type=self.account['button_key'], element_name=self.account['button_value'],
            #                      sleep=self.sleep, window_id=self.window_id, element=self.element)
            # else:  # Else press Key
            #     click_key(element_type=self.login_data['pass_key'], element_name=self.login_data['pass_value'],
            #                  key=self.key, sleep=self.sleep, window_id=self.window_id)

        set_text(**acc_name)  # Set name
        set_text(**acc_pass)  # Set pass
        if submit_button:  # If Submit button element is given
            click_element(**submit_button)
        else:  # Else press Key
            click_key(**submit_key)


class BrowserTab:
    # TODO - create a Class to create and manage browser tabs with on-demand authentication
    def __init__(self):
        pass


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


def add_tab(url: str) -> str:
    driver.execute_script(f"window.open('{url}');")         # TODO: try to use standard Selenium tab interface
    # driver.switch_to.new_window()                         # Create new tab
    driver.switch_to.window(driver.window_handles[-1])     # An alternate

    return driver.current_window_handle


def add_tab_alt(driver_object, url="about:blank"):
    # TODO - test this way to generate new Tabs
    wnd = driver.execute(webdriver.common.action_chains.Command.NEW_WINDOW)
    handle = wnd["value"]["handle"]
    driver_object.switch_to.window(handle)
    driver_object.get(url)     # changes the handle
    return driver_object.current_window_handle


def change_tab(window_id: str) -> str:
    driver.switch_to.window(window_id)  # An alternate
    return driver.current_window_handle


def close_window(handler: str):
    try:
        driver.switch_to.window(handler)
        driver.close()
        driver.quit()
    except Exception as ex:
        print("WINDOW NOT AVAILABLE")
        print(ex)


def find_elements(element_type: str, element_name: str, sleep=SLEEP, repeat=REPEAT, element=None, window_id=None,
                  reload=True):
    """
    :param window_id: Window ID for manipulating. SHOULD TO BE FILLED IF `ELEMENT` IS EMPTY!!!
    :param element_type: Type of element for search
    :param element_name: Element name value
    :param sleep: Time to wait in seconds
    :param repeat: DEPRECATED - Try to reload page to find element
    :param element: Web element to search any other elements in it
    :param reload: If True - reload page before any `repeat` iteration
    :return: Found element
    """
    # TODO - Use Optional parameter `element` to searching
    if element:
        search_in = element
    else:
        if window_id:
            driver.switch_to.window(window_id)
        search_in = driver

    time.sleep(sleep)
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
            if reload:
                reload_page(sleep=sleep)
            # DAMN RECURSION CALL
            return find_elements(element_type=element_type,
                                 element_name=element_name,
                                 repeat=repeat-1,
                                 reload=reload,
                                 sleep=sleep)
        else:
            print(f"Element '{element_type}' -> '{element_name}' not found")
            # elements_input = []
            # raise Exception         # TODO - change to validate exception type
    return elements_input


def reload_page(handler=None, sleep=SLEEP):
    """
    Reloading page
    :param handler: Use to specify current window
    :param sleep: Time to wain in seconds
    :return:
    """
    try:
        if handler:
            driver.switch_to.window(handler)
        # time.sleep(sleep * 2)  # if element was not found than wait for 10 seconds, reload page and try again
        driver.refresh()
        time.sleep(sleep)
    except Exception as ex:
        print(ex)


def set_text(element_type: str, element_name: str, data: str, sleep=SLEEP, element=None, window_id=None):
    # TODO Rewrite to search elements by several tags with recursion
    """
    Manipulating with text input fields
    :param window_id: Window ID for manipulating
    :param element_type: Type  of searching element
    :param element_name: Name of searching element
    :param data: Data to input
    :param sleep: Sleeping time in seconds
    :param element:
    :return: None
    """

    time.sleep(sleep)

    # TODO - rewrite to use Exception from `main.py` instead use it here
    try:
        # TODO - Use Optional parameter `element` to searching
        if window_id:
            driver.switch_to.window(window_id)
        element_input = find_elements(element_type, element_name, element=element, window_id=window_id, repeat=2)
        if element_input:
            element_input[0].clear()                # temporarily pick up only the first element
            element_input[0].send_keys(data)

    except Exception as ex:
        print(ex)


def click_element(element_type: str, element_name: str,
                  sleep=SLEEP, window_id=None, element=None, reload=True, repeat=REPEAT):
    """
    Manipulating with text input fields
    :param window_id: Window ID for manipulating
    :param element_type: Type of finding element
    :param element_name: Name of finding element
    :param sleep: Sleeping time in seconds
    :return: None
    """
    # time.sleep(sleep)
    try:
        if window_id:
            driver.switch_to.window(window_id)
        element_click = find_elements(element_type, element_name,
                                      window_id=window_id, element=element, reload=reload, repeat=repeat, sleep=sleep)
        if element_click:
            element_click[0].click()        # temporarily pick up only the first element

    except Exception as ex:
        print("Element doesn't found")
        print(ex)


def click_key(element_type: str, element_name: str, key='enter', sleep=SLEEP, window_id=None):
    """
    Manipulating with text input fields
    :param window_id: Window ID for manipulating
    :param element_type: Type of finding element
    :param element_name: Name of finding element
    :param key: Name of button to press
    :param sleep: Sleeping time in seconds
    :return: None
    """
    time.sleep(sleep)
    try:
        if window_id:
            driver.switch_to.window(window_id)
        element_click = find_elements(element_type, element_name)[0]
        if key == 'enter':
            element_click.send_keys(Keys.ENTER)
        else:
            pass        # TODO to write

    except Exception as ex:
        print("Element doesn't found")
        print(ex)


if __name__ == '__main__':
    # TODO - clear it! Just for test
    google_window = open_window('https://google.com', sleep=3)  # Open auth window for `MP Stats`
    driver.execute_script("window.open('https://ya.ru');")
    # windows_before = driver.current_window_handle
    # driver.switch_to.new_window()     # An alternate
    driver.switch_to.window(driver.window_handles[-1])
    # driver.get('https://ya.ru')
    time.sleep(3)
    driver.switch_to.window(google_window)
    time.sleep(3)
    print(f'{google_window}\n{driver.window_handles}')
    close_window(driver.window_handles[1])
    time.sleep(3)
    close_window(google_window)
