import csv
from pathlib import Path

TEMP_KEYWORDS_PATH = r"D:\Downloads\requests.csv"

with open(TEMP_KEYWORDS_PATH, 'r', newline='', encoding='utf-8') as f:
    # https://pythonworld.ru/moduli/modul-csv.html
    i = 0
    reader = csv.reader(f, delimiter=',')
    # print(help(reader))
    for raw in reader:
        if i < 20:
            print(raw[0])
        else:
            break
        i += 1
