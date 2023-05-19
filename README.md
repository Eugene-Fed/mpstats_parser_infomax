### Маркетплейс парсер

### HOW TO RUN
You can use number of parameters to start with script:
- `-s`, `--key_start`: Start keyword ID from list
- `-l`. `--key_limit`: Maximum limit of keyword in output file
- `-f`, `--freq_limit`: Minimum keyword month frequency limit to research
- `-w`, `--wait`: Time to wait between web browser manipulations in seconds
- `-t`, `--tries`: Number of keyword statistics download tries
- `-c`, `--number_of_categories`: Maximum number of researching categories

#### MacOS
- `brew install --cask chromedriver`
- `brew install --cask google-chrome`
- edit settings in `settings.json` with path to google-chrome `"webdriver_dir": "/opt/homebrew/bin/chromedriver"`
- `brew install python`
- `pip3 install -r requirements.txt`
- `python3 main.py`

### TODO list
- [x] Use DOM Ready waiting instead of `time.sleep`. **DOESN'T WORK**
- [x] If exception "Out of range", than reload page
- [x] Use `closure` or `class` **Authontefication** to create number of `log_in` functions for all needed accounts
- [x] Add Comparative Frequency Data to Keyword Table
- [x] Check exception below with closing browser window
- [x] Solve exception  
`selenium.common.exceptions.StaleElementReferenceException:  
Message: stale element reference: element is not attached to the page document`
- [x] Make env parameter for "webdriver_dir"
- [x] ~~`get_category_volume` - write file downloader~~
- [x] ~~Create function to open Category Value page~~
- [x] Get category value and save it.
- [x] Save whitespase in category Paths
- [ ] Study `LambdaTest` library for `Selenium`
- [ ] Get Category ID from `bablo button` from the bid for the first place
- [ ] Create module to load Categories Value from file
- [ ] Research `driver.add_cookie(cookie)` method to set cockies
- [ ] Use filled CPM values instead of `0` for the 1st, 2nd and 3rd places
- [ ] Parse Catagory Value statistics from MPStats
- [ ] Load all CPMs and sort them by value before assign it to bids table
- [ ] Create module to use standart OS `Download` page for input and output data files  
https://clck.ru/345Ffa
- [ ] Try to use `driver.implicitly_wait()` and other explicitly wait methods  
https://habr.com/ru/companies/otus/articles/596071/
- [ ] Add screenshot generator into Exception handler: 'driver.save_screenshot(capture_path)'
- [ ] Write module to use `Headless Chrome`
- [ ] Research `keyloak` for handling login data

### Tutorials
https://pythonworld.ru/moduli/modul-csv.html
https://www.lambdatest.com/learning-hub/python-tutorial
http://cs.mipt.ru/advanced_python/lessons/lab04.html - for param parser

### Downloads
https://chromedriver.chromium.org/downloads
