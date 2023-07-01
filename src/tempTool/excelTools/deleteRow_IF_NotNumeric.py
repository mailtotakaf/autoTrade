import openpyxl

# ある列の、数字でない行を削除する

wb_name = "../../../data/Book1.xlsx"
wb = openpyxl.load_workbook(wb_name)
ws = wb['Sheet1']

lastTicker = ""
for idx, row in enumerate(ws.rows, 1):
    ticker = ""
    try:
        
        ticker = str(row[1].value)
        lastTicker = ticker
        if ticker.isnumeric() or None:
            print("数字でつ：", ticker)
        else:
            print("数字でない：", ticker)
            ws.delete_rows(idx)

        # 2行連続で空白だったら終了
        if lastTicker == "" and ticker == "":
            break
        # write_idx = idx // 2
        # print("write_idx:", write_idx)
        # if idx % 2 == 0:
        #     print("company_name:", ticker)
        #     # 書込
        #     cell_e = 'E' + str(write_idx)
        #     ws[cell_e].value = ticker
        # else:
        #     print("ticker:", ticker)
        #     # 書込
        #     cell_f = 'F' + str(write_idx)
        #     ws[cell_f].value = ticker

    except Exception as e:
        print('Error. ticker:', ticker)
        print(e)
        pass

wb.save(wb_name)
wb.close()
