import openpyxl

# とりあえずB列に１行おきにtickerを書いとけば無駄な空白行を無くしてくれる

wb_name = "../../data/pythonList.xlsx"
wb = openpyxl.load_workbook(wb_name)
ws = wb['Sheet1']

for idx, row in enumerate(ws.rows, 1):
    ticker_name = ""
    try:
        ticker_name = str(row[1].value)
        write_idx = idx // 2
        print("write_idx:", write_idx)
        if idx % 2 == 0:
            print("company_name:", ticker_name)
            # 書込
            cell_e = 'E' + str(write_idx)
            ws[cell_e].value = ticker_name
        else:
            print("ticker_name:", ticker_name)
            # 書込
            cell_f = 'F' + str(write_idx)
            ws[cell_f].value = ticker_name

    except Exception as e:
        print('Error. ticker:', ticker_name)
        print(e)
        pass

wb.save(wb_name)
wb.close()
