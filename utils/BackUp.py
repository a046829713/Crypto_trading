""" TO export data from crypto_data """
""" in Trading systeam  get data from DataProvider"""
""" check if change compute systeam"""

import os
from Major.DataProvider import DataProvider_online,DataProvider
from typing import Optional
from datetime import datetime
from Database.SQL_operate import SqlSentense

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



def check_table_if_exits(table_name :Optional[str] = None):
    """
        檢查資料庫是否存在
    Args:
        table_name (Optional[str], optional): _description_. Defaults to None.
        
    """
    def _check_table_if_exits(func):
        def warpper(*args,**kwargs):
            if table_name is not None:
                dataProvider = DataProvider()
                getAllTablesName = dataProvider.SQL.get_db_data(
                'show tables;')
                getAllTablesName = [y[0] for y in getAllTablesName]                
                if table_name == "sysstatus" and table_name not in getAllTablesName:
                    # 將其更改為寫入DB
                    dataProvider.SQL.change_db_data(
                        """CREATE TABLE `crypto_data`.`sysstatus`(`ID` varchar(255) NOT NULL,`systeam_datetime` varchar(255) NOT NULL,PRIMARY KEY(`ID`));""")
                    dataProvider.SQL.change_db_data(
                        f"""INSERT INTO `sysstatus` VALUES ('1','{str(datetime.now())}');""")
                        # 在進行判斷之前 可以先確認表是否存在
                
                if table_name =="optimizeresult" and table_name not in getAllTablesName:
                    dataProvider.SQL.change_db_data(SqlSentense.createOptimizResult())
                    print("成功創建")
            func(*args,**kwargs)
        return warpper
    return _check_table_if_exits