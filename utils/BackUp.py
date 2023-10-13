""" TO export data from crypto_data """
""" in Trading systeam  get data from DataProvider"""
""" check if change compute systeam"""




from Database.SQL_operate import SqlSentense
from datetime import datetime
from typing import Optional
import os
from Major.DataProvider import DataProvider_online, DataProvider
from Database import SQL_operate
def check_file(filename: str):
    """ 檢查檔案是否存在 否則創建 """
    if not os.path.exists(filename):
        os.mkdir(filename)


def exportKbarsData(symbol_name, dataProvider: DataProvider_online, data_type: str = None, iflower=True):
    """保存單一資料

    Args:
        symbol_name (_type_): example :BTCUSDT
        dataProvider (DataProvider_online): _description_
        data_type(str):"D"
    """
    if data_type == 'D':
        tb_symbol_name = symbol_name + '-F-D'
    else:
        tb_symbol_name = symbol_name + '-F'

    if iflower:
        tb_symbol_name = tb_symbol_name.lower()

    df = dataProvider.SQL.read_Dateframe(tb_symbol_name)
    df.set_index('Datetime', inplace=True)
    df.to_csv(f"History\{tb_symbol_name}.csv")


def check_table_if_exits(table_name: Optional[str] = None):
    """
        檢查資料庫是否存在
    Args:
        table_name (Optional[str], optional): _description_. Defaults to None.

    """
    def _check_table_if_exits(func):
        def warpper(*args, **kwargs):
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

                elif table_name == "optimizeresult" and table_name not in getAllTablesName:
                    dataProvider.SQL.change_db_data(
                        SqlSentense.createOptimizResult())

                elif table_name == "lastinitcapital" and table_name not in getAllTablesName:
                    dataProvider.SQL.change_db_data(
                        SqlSentense.createlastinitcapital())
                    dataProvider.SQL.change_db_data(
                        f"""INSERT INTO `lastinitcapital` VALUES ('1',20000);""")
                    print("完成")
            return func(*args, **kwargs)
        return warpper
    return _check_table_if_exits


def check_all_need_table():
    SQL = SQL_operate.DB_operate()
    dataProvider = DataProvider()
    getAllTablesName = dataProvider.SQL.get_db_data('show tables;')
    getAllTablesName = [y[0] for y in getAllTablesName]
    
    if 'orderresult' not in getAllTablesName:
        SQL.change_db_data(
            """
                CREATE TABLE `crypto_data`.`orderresult`(
                    `orderId` BIGINT NOT NULL,
                    `order_info` TEXT NOT NULL,
                    PRIMARY KEY(`orderId`)
                );
            """
        )