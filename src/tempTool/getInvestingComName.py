import requests
from bs4 import BeautifulSoup
import openpyxl
import time

wb_name = "../../data/pythonList.xlsx"
wb = openpyxl.load_workbook(wb_name)
ws = wb['sp500']

for idx, row in enumerate(ws.rows, 1):
    ticker_name = ""
    try:
        ticker_name = str(row[3].value)

        ###investingComName Start
        url = "https://jp.investing.com/search/?q=" + ticker_name
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # <a>タグで<i>タグのclass属性が"ceFlags middle USA"を持つ要素を抽出します
        target_elements = soup.find_all("a", {"class": "js-inner-all-results-quote-item row", "href": True})
        usa_hrefs = []

        # 抽出した要素から<i>タグのclass属性が"ceFlags middle USA"を持つもののhref属性の値を取り出します
        for element in target_elements:
            flag_element = element.find("i", {"class": "ceFlags middle USA"})
            if flag_element:
                href_value = element.get("href")
                usa_hrefs.append(href_value)

        # 結果を表示します
        investingComName = ""
        for href_value in usa_hrefs:
            if "/equities/" in href_value:
                investingComName = href_value.replace("/equities/", "")
                print(investingComName)
                break
        ###investingComName End
        # 書込
        cell_e = 'E' + str(idx)
        ws[cell_e].value = investingComName

        time.sleep(3)
        ### FiscalDate Start
        # url = "https://jp.investing.com/equities/" + investingComName
        # response = requests.get(url)
        #
        # soup = BeautifulSoup(response.text, "html.parser")
        #
        # elems = soup.find_all(href=re.compile("/equities/" + ticker_name + "-earnings"))
        # fiscal_date = elems[1].contents[0]
        #
        # cell_f = 'F' + str(idx)
        # ws[cell_f].value = fiscal_date
        ### FiscalDate End
    except Exception as e:
        print('Error. ticker:', ticker_name)
        print(e)
        pass

wb.save(wb_name)
wb.close()
