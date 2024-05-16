from psycopg2 import Error
import psycopg2
import matplotlib.pyplot as plt
from datetime import datetime


class Plot:
    def __init__(self):
        # 業界別変化率
        p_up_per_avg_list = self.get_p_up_per_avg_list()
        self.plot_p_up_per_avg_list(p_up_per_avg_list)

    def get_p_up_per_avg_list(self):
        try:
            cursor = self.postgres()
            sql = "select * from p_up_per_avg"
            cursor.execute(sql)
            list = cursor.fetchall()
            return list
        except(Exception, Error) as error:
            print("Error: get_p_up_per_avg_list.", error)
        finally:
            cursor.close()
            connector.close()

    def postgres(self):
        global cursor, connector
        try:
            connector = psycopg2.connect('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
                user="postgres",
                password="YourPW",
                host="localhost",
                port="5432",
                dbname="trading"))

            cursor = connector.cursor()
            return cursor
        except(Exception, Error) as error:
            print("Error: DB connection.", error)

    def select_p_up_per_avg(self):
        try:
            cursor = self.postgres()
            sql = "select tj.industory_kbn2, avg(mr.p_up_per) as p_up_per_avg from months_results mr " \
                  "inner join ticker_jp tj on mr.ticker = tj.ticker group by tj.industory_kbn2 order by avg(mr.p_up_per) desc;"
            cursor.execute(sql)
            row = cursor.fetchall()
            return row
        except(Exception, Error) as error:
            print("Error: select_p_up_per_avg.", error)
        finally:
            cursor.close()
            connector.close()

    def plot_p_up_per_avg_list(self, p_up_per_avg_list):
        bank_list = []
        electric_gus_list = []
        iron_metal_list = []
        car_list = []
        trade_whole_list = []
        transport_list = []
        energy_list = []
        material_sci_list = []
        construct_list = []
        machine_list = []
        food_list = []
        retail_list = []
        real_est_list = []
        finance_list = []
        pharma_list = []
        it_list = []
        elec_precision_list = []
        none_list = []
        create_timestamp_list = []
        x_labels = []

        for row in p_up_per_avg_list:
            bank_list.append(row[0])
            electric_gus_list.append(row[1])
            iron_metal_list.append(row[2])
            car_list.append(row[3])
            trade_whole_list.append(row[4])
            transport_list.append(row[5])
            energy_list.append(row[6])
            material_sci_list.append(row[7])
            construct_list.append(row[8])
            machine_list.append(row[9])
            food_list.append(row[10])
            retail_list.append(row[11])
            real_est_list.append(row[12])
            finance_list.append(row[13])
            pharma_list.append(row[14])
            it_list.append(row[15])
            elec_precision_list.append(row[16])
            none_list.append(row[17])
            create_timestamp_list.append(row[18])
            datetime_obj = datetime.strptime(str(row[18]), "%Y-%m-%d %H:%M:%S.%f")
            x_labels.append(datetime_obj.strftime("%m/%d-%H:%M"))

        plt.figure()
        plt.grid(True)
        plt.xticks(create_timestamp_list, x_labels, rotation=90)
        plt.legend(prop={'family': 'MS Gothic'})
        plt.title("price_up_per_average")

        # industory_kbn2
        plt.plot(create_timestamp_list, bank_list, label="bank")  # 銀行
        plt.plot(create_timestamp_list, electric_gus_list, label="electric_gus")  # 電力・ガス
        plt.plot(create_timestamp_list, iron_metal_list, label="iron_metal")  # 鉄鋼・非鉄
        plt.plot(create_timestamp_list, car_list, label="car")  # 自動車・輸送機
        plt.plot(create_timestamp_list, trade_whole_list, label="trade_whole")  # 商社・卸売
        plt.plot(create_timestamp_list, transport_list, label="transport")  # 運輸・物流
        plt.plot(create_timestamp_list, energy_list, label="energy")  # エネルギー資源
        plt.plot(create_timestamp_list, material_sci_list, label="material_sci")  # 素材・化学
        plt.plot(create_timestamp_list, construct_list, label="construct")  # 建設・資材
        plt.plot(create_timestamp_list, machine_list, label="machine")  # 機械
        plt.plot(create_timestamp_list, food_list, label="food")  # 食品
        plt.plot(create_timestamp_list, retail_list, label="retail")  # 小売
        plt.plot(create_timestamp_list, real_est_list, label="real_est")  # 不動産
        plt.plot(create_timestamp_list, finance_list, label="finance")  # 金融（除く銀行）
        plt.plot(create_timestamp_list, pharma_list, label="pharma")  # 医薬品
        plt.plot(create_timestamp_list, it_list, label="it")  # 情報通信・サービスその他
        plt.plot(create_timestamp_list, elec_precision_list, label="elec_precision")  # 電機・精密
        plt.plot(create_timestamp_list, none_list, label="none")
        plt.legend()
        plt.show()


def get_value_by_key(row, key):
    for item in row:
        if item[0] == key:
            return item[1]
    return None


# クラスのインスタンスを作成
my_obj = Plot()
