""" TO export data from crypto_data """
""" in Trading systeam  get data from DataProvider """
""" check if change compute systeam"""

from Database.SQL_operate import SqlSentense
from Database import SQL_operate
from datetime import datetime
import os
from Major.DataProvider import DataProvider_online, DataProvider
import pandas as pd

def check_file(filename: str):
    """ 檢查檔案是否存在 否則創建 """
    if not os.path.exists(filename):
        os.mkdir(filename)
        
class DatabaseBackupRestore:
    def __init__(self, backup_folder="backup"):
        self.backup_folder = backup_folder
        self.SQL = SQL_operate.DB_operate()
        check_file(backup_folder)
        self.check_all_need_table()

    def check_all_need_table(self):
        getAllTablesName = self.SQL.get_db_data('show tables;')
        getAllTablesName = [y[0] for y in getAllTablesName]

        # 訂單的結果
        if 'orderresult' not in getAllTablesName:
            self.SQL.change_db_data(
                SqlSentense.createorderresult()
            )

        # 用來放置平均策略的虧損
        if 'avgloss' not in getAllTablesName:
            self.SQL.change_db_data(
                SqlSentense.createAvgLoss()
            )

        if 'lastinitcapital' not in getAllTablesName:
            self.SQL.change_db_data(SqlSentense.createlastinitcapital())
            self.SQL.change_db_data(
                f"""INSERT INTO `lastinitcapital` VALUES ('1',20000);""")

        if 'sysstatus' not in getAllTablesName:
            # 將其更改為寫入DB
            self.SQL.change_db_data(SqlSentense.createsysstatus())
            self.SQL.change_db_data(
                f"""INSERT INTO `sysstatus` VALUES ('1','{str(datetime.now())}');""")

        if 'optimizeresult' not in getAllTablesName:
            self.SQL.change_db_data(SqlSentense.createOptimizResult())

    def export_all_tables(self):
        getAllTablesName = self.SQL.get_db_data('show tables;')
        getAllTablesName = [y[0] for y in getAllTablesName]
        for table in getAllTablesName:
            print(table)
            df = self.SQL.read_Dateframe(table)
            path = os.path.join(f"{self.backup_folder}", f"{table}.csv")
            df.to_csv(path, index=False)

    def import_all_tables(self):
        """
            將資料全部寫入MySQL

        """
        # 將所有的資料讀取出來開始處理
        for file in os.listdir(self.backup_folder):
            if file.endswith(".csv"):
                table_name = file[:-4]
                full_file_path = os.path.join(
                    self.backup_folder, file)  # 獲取完整的文件路徑
                

                # 資料類的(開高低收的)
                if 'usdt' in table_name:
                    self.SQL.change_db_data(
                        SqlSentense.create_table_name(table_name))
                else:
                    #  系統類的
                    pass
                
                chunk_size = 50000  # or any other reasonable number
                for chunk in pd.read_csv(f"{self.backup_folder}/{file}", chunksize=chunk_size):
                    self.SQL.write_Dateframe(chunk, table_name, exists='append', if_index=False)
                
                
                
                print(f"開始刪除:資料名稱:{table_name}")
                os.remove(full_file_path)
