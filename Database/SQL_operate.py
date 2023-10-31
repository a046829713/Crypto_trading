import json
from Database import router
from sqlalchemy import text
from utils import Debug_tool
import pandas as pd
import time


class DB_operate():
    def wirte_data(self, quoteSymbol: str, out_list: list):
        """
        將商品資料寫入資料庫
        [{'Date': '2022/07/01', 'Time': '09:25:00', 'Open': '470',
            'High': '470', 'Low': '470', 'Close': '470', 'Volume': '10'}]
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

    def write_Dateframe(self, df: pd.DataFrame, symbol_name: str, exists='replace', if_index=True) -> pd.DataFrame:
        """
            to write pandas Dateframe
            symbol_name or tablename: 'btcusdt-f'
        """
        try:
            self.userconn = router.Router().mysql_financialdata_conn
            with self.userconn as conn:
                df.to_sql(symbol_name, con=conn,
                          if_exists=exists, index=if_index)
        except:
            Debug_tool.debug.print_info()


class SqlSentense():
    @staticmethod
    def createOptimizResult() -> str:
        sql_query = """
            CREATE TABLE `optimizeresult` (
            `strategyName` varchar(30) NOT NULL,
            `freq_time` int NOT NULL,
            `size` decimal(10,5) NOT NULL,
            `fee` decimal(10,5) NOT NULL,
            `slippage` decimal(10,5) NOT NULL,
            `symbol` varchar(20) NOT NULL,
            `Strategytype` varchar(20) NOT NULL,
            `updatetime` date NOT NULL,
            `All_args` varchar(500) DEFAULT NULL,
            PRIMARY KEY (`strategyName`)
            ) ;


        """

        return sql_query

    @staticmethod
    def createAvgLoss() -> str:
        sql_query = """
            CREATE TABLE `avgloss` (
            `strategyName` varchar(30) NOT NULL,
            `freq_time` int NOT NULL,            
            `symbol` varchar(20) NOT NULL,
            `strategytype` varchar(20) NOT NULL,
            `updatetime` date NOT NULL,
            `avgLoss` decimal(15,5) NOT NULL,
            PRIMARY KEY (`strategyName`)
            ) ;
        """

        return sql_query

    @staticmethod
    def update_avgloss(result: dict) -> str:
        """
        Args:{'freq_time': 15, 'symbol': 'BTCUSDT', 'strategytype': 'DQNStrategy', 'strategyName': 'BTCUSDT-15K-OB-DQN', 'updatetime': '2023-10-20', 'avgLoss': -345.0}
        Returns:
            str: 返回要執行的SQL 語句
        """

        sql_query = f"""UPDATE `crypto_data`.`avgLoss`
                                SET
                                `updatetime` = '{result['updatetime']}',
                                `freq_time` = {result['freq_time']},                    
                                `symbol` = '{result['symbol']}',
                                `Strategytype` = '{result['Strategytype']}',
                                `avgLoss` = '{result['avgLoss']}'
                                WHERE `strategyName` = '{result['strategyName']}';
                            """

        return sql_query

    @staticmethod
    def insert_avgloss(result) -> str:
        """
        result:
            {'freq_time': 15, 'symbol': 'BTCUSDT', 'strategytype': 'DQNStrategy', 'strategyName': 'BTCUSDT-15K-OB-DQN', 'updatetime': '2023-10-20', 'avgLoss': -345.0}
        """
        sql_query = f"""

            INSERT INTO `crypto_data`.`avgLoss`
                (`freq_time`, `symbol`, `Strategytype`, `strategyName`, `updatetime`,`avgLoss`)
            VALUES
            {tuple(result.values())};
            
            """
        return sql_query

    @staticmethod
    def insert_optimizeresult(result, strategy_type) -> str:
        """
        result:
            {'freq_time': 15, 'size': 1.0, 'fee': 0.002,
            'slippage': 0.0025, 'symbol': 'BTCUSDT', 'Strategytype': 'VCPStrategy',
            'strategyName': 'BTCUSDT-15K-OB-VCP', 'highest_n1': 300, 'lowest_n2': 600,
            'std_n3': 50, 'volume_n3': 150, 'updatetime': '2023-04-05'}
        """

        sql_query = f"""

            INSERT INTO `crypto_data`.`optimizeresult`
                (`freq_time`, `size`, `fee`, `slippage`, `symbol`, `Strategytype`, `strategyName`, `updatetime`,`All_args`)
            VALUES
            {tuple(result.values())};
            
            """

        return sql_query

    @staticmethod
    def update_optimizeresult(result: dict, strategy_type: str) -> str:
        """

            用來更新優化的結果
        Args:
            result (dict): {'freq_time': 15, 'size': 1.0, 'fee': 0.002,
            'slippage': 0.0025, 'symbol': 'BTCUSDT', 'Strategytype': 'VCPStrategy',
            'strategyName': 'BTCUSDT-15K-OB-VCP', 'highest_n1': 300, 'lowest_n2': 600,
            'std_n3': 50, 'volume_n3': 150, 'updatetime': '2023-04-05'}
            strategy_type (str): _description_

        Returns:
            str: 返回要執行的SQL 語句
        """

        sql_query = f"""UPDATE `crypto_data`.`optimizeresult`
                                SET
                                `updatetime` = '{result['updatetime']}',
                                `freq_time` = {result['freq_time']},
                                `size` = {result['size']},
                                `fee` = {result['fee']},
                                `slippage` = {result['slippage']},
                                `symbol` = '{result['symbol']}',
                                `Strategytype` = '{result['Strategytype']}',
                                `All_args` = '{result['All_args']}'
                                WHERE `strategyName` = '{result['strategyName']}';
                            """

        return sql_query

    @staticmethod
    def create_table_name(tb_symbol_name: str) -> str:
        """ to create 1 min"""
        sql_query = f"""CREATE TABLE `crypto_data`.`{tb_symbol_name}`(
                `Datetime` DATETIME NOT NULL,
                `Open` FLOAT NOT NULL,
                `High` FLOAT NOT NULL,
                `Low` FLOAT NOT NULL,
                `Close` FLOAT NOT NULL,
                `Volume` FLOAT NOT NULL,
                `close_time` FLOAT NOT NULL,
                `quote_av` FLOAT NOT NULL,
                `trades` FLOAT NOT NULL,
                `tb_base_av` FLOAT NOT NULL,
                `tb_quote_av` FLOAT NOT NULL,
                `ignore` FLOAT NOT NULL,
                PRIMARY KEY(`Datetime`)
                );"""

        return sql_query

    @staticmethod
    def createlastinitcapital() -> str:
        sql_query = """CREATE TABLE `lastinitcapital` (
        `ID` varchar(255) NOT NULL,
        `capital` int NOT NULL,
        PRIMARY KEY (`ID`)
        );"""

        return sql_query

    @staticmethod
    def createsysstatus() -> str:
        sql_query = """CREATE TABLE `crypto_data`.`sysstatus`(`ID` varchar(255) NOT NULL,`systeam_datetime` varchar(255) NOT NULL,PRIMARY KEY(`ID`));"""
        return sql_query

    @staticmethod
    def createorderresult() -> str:
        sql_query = """
                CREATE TABLE `crypto_data`.`orderresult`(
                    `orderId` BIGINT NOT NULL,
                    `order_info` TEXT NOT NULL,
                    PRIMARY KEY(`orderId`)
                );
            """
        return sql_query
