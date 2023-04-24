""" TO export data from crypto_data """
""" in Trading systeam  get data from DataProvider"""

import os
from Major.DataProvider import DataProvider_online

def check_file():
    """ 檢查檔案是否存在 否則創建 """
    if not os.path.exists("History"):
        os.mkdir('History')
        


def exportKbarsData(symbol_name,dataProvider:DataProvider_online):
    """保存單一資料

    Args:
        symbol_name (_type_): example :BTCUSDT
        dataProvider (DataProvider_online): _description_
    """
    print(symbol_name)
    table_name = f"{symbol_name.lower()}-f"
    df = dataProvider.SQL.read_Dateframe(table_name)
    df.set_index('Datetime',inplace=True)
    df.to_csv(f"History\{table_name}.csv")



