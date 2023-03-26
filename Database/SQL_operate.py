import json
from Database import router
from sqlalchemy import text
from utils import Debug_tool
import pandas as pd


class DB_operate():
    def wirte_data(self, quoteSymbol: str, out_list: list):
        """
        將商品資料寫入資料庫
        [{'Date': '2022/07/01', 'Time': '09:25:00', 'Open': '470', 'High': '470', 'Low': '470', 'Close': '470', 'Volume': '10'}]
        """
        try:
            self.userconn = router.Router().mysql_financialdata_conn
            with self.userconn as conn:
                sql_sentence = f'INSERT INTO `{quoteSymbol}` (Date, Time, Open, High, Low, Close, Volume) VALUES (:Date, :Time, :Open, :High, :Low, :Close, :Volume)'
                conn.execute(
                    text(sql_sentence),
                    out_list
                )
        except Exception as e:
            Debug_tool.debug.print_info()

    def get_db_data(self, text_msg: str) -> list:
        """
            專門用於select from
        """
        try:
            self.userconn = router.Router().mysql_financialdata_conn
            with self.userconn as conn:

                result = conn.execute(
                    text(text_msg)
                )
                # 資料範例{'Date': '2022/07/01', 'Time': '09:25:00', 'Open': '470', 'High': '470', 'Low': '470', 'Close': '470', 'Volume': '10'}

                return list(result)
        except:
            Debug_tool.debug.print_info()

    def change_db_data(self, text_msg: str) -> None:
        """ 用於下其他指令
        Args:
            text_msg (str): SQL_Query
        Returns:
            None
        """
        try:
            self.userconn = router.Router().mysql_financialdata_conn
            with self.userconn as conn:
                conn.execute(text(text_msg))
        except:
            Debug_tool.debug.print_info()

    def create_table(self, text_msg: str) -> None:
        """ 創建日線資料表
        Args:
            text_msg (str): symbolcode TC.F.TWF.IAF.HOT
        """

        try:
            self.userconn = router.Router().mysql_financialdata_conn
            with self.userconn as conn:
                conn.execute(text(
                    f"CREATE TABLE `financialdata`.`{text_msg}`(`Date` date NOT NULL,`Time` time NOT NULL,`Open` FLOAT NOT NULL,`High` FLOAT NOT NULL,`Low` FLOAT NOT NULL,`Close` FLOAT NOT NULL,`Volume` FLOAT  NOT NULL,PRIMARY KEY(`Date`, `Time`));"))
        except:
            Debug_tool.debug.print_info()

    def read_Dateframe(self, text_msg: str) -> pd.DataFrame:
        """
            to get pandas Dateframe
            symbol_name: 'btcusdt-f'
        """
        try:
            self.userconn = router.Router().mysql_financialdata_conn
            with self.userconn as conn:
                return pd.read_sql(text_msg, con=conn)
        except:
            Debug_tool.debug.print_info()

    def write_Dateframe(self, df: pd.DataFrame, symbol_name: str, exists='replace') -> pd.DataFrame:
        """
            to write pandas Dateframe
            symbol_name or tablename: 'btcusdt-f'
        """
        try:
            self.userconn = router.Router().mysql_financialdata_conn
            with self.userconn as conn:
                df.to_sql(symbol_name, con=conn, if_exists=exists)
        except:
            Debug_tool.debug.print_info()


class SqlSentense():
    @staticmethod
    def createOptimizResult() -> str:
        sql_query = """
            CREATE TABLE `crypto_data`.`optimizeresult` (
                `strategyName` VARCHAR(30) NOT NULL PRIMARY KEY,
                `freq_time` INT NOT NULL,
                `size` DECIMAL(10, 5) NOT NULL,
                `fee` DECIMAL(10, 5) NOT NULL,
                `slippage` DECIMAL(10, 5) NOT NULL,
                `symbol` VARCHAR(20) NOT NULL,
                `Strategytype` VARCHAR(20) NOT NULL,
                `highest_n1` INT NOT NULL,
                `lowest_n2` INT NOT NULL,
                `ATR_short1` DECIMAL(10, 5) NOT NULL,
                `ATR_long2` DECIMAL(10, 5) NOT NULL,
                `updatetime` DATE NOT NULL
            );



        """
        
        return sql_query
