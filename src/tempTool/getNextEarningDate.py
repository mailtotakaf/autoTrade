import requests
from bs4 import BeautifulSoup
import openpyxl
import re
import time

wb = openpyxl.load_workbook("../../data/pythonList.xlsx")
ws = wb['competitor']

for idx, row in enumerate(ws.rows, 1):
    try:
        ticker_name = str(row[4].value)

        url = "https://jp.investing.com/equities/" + ticker_name
        response = requests.get(url)

        soup = BeautifulSoup(response.text,"html.parser")

        elems = soup.find_all(href=re.compile("/equities/" + ticker_name + "-earnings"))
        fiscal_date = elems[1].contents[0]

        cell_e = 'F' + str(idx)
        ws[cell_e].value = fiscal_date

        print(ticker_name)
        time.sleep(5)
    except Exception as e:
        print(e)
        pass

wb.save("../../data/pythonLIst.xlsx")