import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Авторизация в Google Sheets API
SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS = r'api-keys\client_secret_283164272049-avsffrqvh0h6t6l0d7k8hqmf19u0tc20.apps.googleusercontent.com.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS, SCOPE)
client = gspread.authorize(creds)

# Открываем таблицу по ее ID
SPREADSHEET_ID = '1FWqkHX9ANAImVh8TKePQ5KchpZ6itd2s41vNyiPeDiI'         # /document/d/([a-zA-Z0-9-_]+)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Добавляем данные в таблицу
data = [['John', 'Doe', 'john.doe@example.com'], ['Jane', 'Doe', 'jane.doe@example.com']]
sheet.insert_rows(data)


def update():
    # Обновляем данные в таблице
    cell_list = sheet.range('A1:C2')
    for i, cell in enumerate(cell_list):
        cell.value = data[i // 3][i % 3]
    sheet.update_cells(cell_list)


if __name__ == '__main__':
    print(help(SCOPE))
