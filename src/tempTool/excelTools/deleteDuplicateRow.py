import openpyxl

# sp500Xシートのリストからダブりを削除

wb_name = "../../../data/pythonList.xlsx"
wb = openpyxl.load_workbook(wb_name)
ws = wb['direct']
ws2 = wb['sp500X']

for idx, row in enumerate(ws.rows, 1):
    ticker = ""
    try:
        ticker = str(row[3].value)
        # print("ticker:", ticker)

        for idx2, row2 in enumerate(ws2.rows, 1):
            # ticker2 = ""
            ticker2 = str(row2[3].value)
            if ticker == ticker2:
                print("duplocated:", ticker2)
                ws2.delete_rows(idx2)
            if ticker2 == "":
                break


    except Exception as e:
        print('Error. ticker:', ticker)
        print(e)
        pass

wb.save(wb_name)
wb.close()
