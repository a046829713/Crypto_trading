from Major.DataProvider import DataProvider, DataProvider_online, AsyncDataProvider
from Major.Symbol_filter import get_symobl_filter_useful
from Vecbot_backtest import Quantify_systeam_online, Optimizer
import time
from datetime import datetime, timedelta
import sys
from Infrastructure.LINE_Alert import LINE_Alert
import pandas as pd
from utils import Debug_tool
import logging
from Database.SQL_operate import SqlSentense
import asyncio
from Datatransformer import Datatransformer
import threading
from utils import BackUp
import os


# 修正權重模式
# 增加總投組獲利平倉，或是單一策略平倉?
# 建立所有商品的優化(GUI > Trading_systeam > Optimizer)
# 判斷資料集的最後一天是否需要回補?
# 增加匯出 optimizeresult 的功能,或許可以增加GUI
# 將檢查sql表的功能提取出來?
# 該如何添加多個策略?
# 待修正時間校準問題
# 為了方便轉移 還是需要打包起來



# 建構輸入輸出檢查的decorator
# 轉移資料
class Trading_systeam():
    def __init__(self) -> None:
        self._init_trading_system()

    def _init_trading_system(self):
        """
            將init打包 方便子類呼叫
        """
        self.symbol_map = {}
        # 這次新產生的資料
        self.new_symbol_map = {}
        self.engine = Quantify_systeam_online()
        # formal正式啟動環境
        self.dataprovider_online = DataProvider_online(formal=True)
        self.line_alert = LINE_Alert()
        self.checkout = False
        self.datatransformer = Datatransformer()  # dataprovider_online 裡面也有

    def checkDailydata(self):
        """
            檢查資料庫中的日資料是否已經回補
            if already update then contiune
        """
        data = self.dataprovider_online.SQL.get_db_data(
            """select *  from `btcusdt-f-d` order by Datetime desc limit 1""")
        sql_date = str(data[0][0]).split(' ')[0]
        _todaydate = str((datetime.today() - timedelta(days=1))).split(' ')[0]

        if sql_date != _todaydate:
            # 更新日資料 並且在回補完成後才繼續進行 即時行情的回補
            DataProvider(time_type='D').reload_all_data()

    def exportOptimizeResult(self):
        """
            將sql的優化資料匯出
        """
        df = self.dataprovider_online.SQL.read_Dateframe("optimizeresult")
        df.set_index("strategyName", inplace=True)
        df.to_csv("optimizeresult.csv")

    def importOptimizeResult(self):
        """
            將sql的優化資料導入
        """
        try:
            df = pd.read_csv("optimizeresult.csv")
            df.set_index("strategyName", inplace=True)
            self.dataprovider_online.SQL.change_db_data(
                "DELETE FROM `optimizeresult`;"
            )
            # 為了避免修改到原始sql 的create 使用append
            self.dataprovider_online.SQL.write_Dateframe(
                df, "optimizeresult", exists='append')
        except Exception as e:
            print(f"導入資料錯誤:{e}")

    def OptimizeAllSymbols(self, optimize_strategy_type: str):
        """
            取得所有交易對
        """

        all_symbols = self.dataprovider_online.Binanceapp.get_targetsymobls()

        # 在進行判斷之前 可以先確認表是否存在
        getAllTablesName = self.dataprovider_online.SQL.get_db_data(
            'show tables;')
        getAllTablesName = [y[0] for y in getAllTablesName]

        if 'optimizeresult' not in getAllTablesName:
            self.dataprovider_online.SQL.change_db_data(
                SqlSentense.createOptimizResult())
            print("成功創建")

        # 將資料讀取出來
        strategydf = self.dataprovider_online.SQL.read_Dateframe(
            "select strategyName, symbol from optimizeresult")
        strategylist = strategydf['strategyName'].to_list()
        symbollist = strategydf['symbol'].to_list()

        # 使用 Optimizer # 建立DB
        for eachsymbol in all_symbols:
            print(eachsymbol)
            # 判斷每次要優化的策略名稱
            if optimize_strategy_type == 'TurtleStrategy':
                target_strategy_name = eachsymbol + "-15K-OB"
            else:
                target_strategy_name = eachsymbol + "-15K-OB-VCP"

            # if target_strategy_name in strategylist:
            #     continue

            result = Optimizer(target_strategy_name, eachsymbol,
                               optimize_strategy_type).optimize()

            # 先確認是否存在裡面
            if result['strategyName'] in strategylist:
                self.dataprovider_online.SQL.change_db_data(
                    SqlSentense.update_optimizeresult(
                        result, optimize_strategy_type)
                )
            else:
                self.dataprovider_online.SQL.change_db_data(
                    SqlSentense.insert_optimizeresult(result, optimize_strategy_type))


    def exportAllKbarsData(self):
        """
            將資料庫裡面的資料全部讀取出來保存成CSV檔案
            只保留1 min的數據
        """
        BackUp.check_file()
        
        
        for each_symbol in self.dataprovider_online.Binanceapp.get_targetsymobls():
            # if os.path.exists("History\\" + each_symbol.lower() + "-f.csv"):
            #     continue
            BackUp.exportKbarsData(each_symbol,self.dataprovider_online)
    
    
    def importAllKbarsData(self):
        """
            將資料全部寫入MySQL
            'btcusdt-f',
            'CREATE TABLE `btcusdt-f` (\n  `Datetime` datetime NOT NULL,
            \n  `Open` float NOT NULL,
            \n  `High` float NOT NULL,
            \n  `Low` float NOT NULL,
            \n  `Close` float NOT NULL,
            \n  `Volume` float NOT NULL,
            \n  `close_time` float NOT NULL,
            \n  `quote_av` float NOT NULL,
            \n  `trades` float NOT NULL,
            \n  `tb_base_av` float NOT NULL,
            \n  `tb_quote_av` float NOT NULL,
            \n  `ignore` float NOT NULL,
            \n  PRIMARY KEY (`Datetime`)\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'

        """

        
        for each_symbol in self.dataprovider_online.Binanceapp.get_targetsymobls():
            if each_symbol.lower() == "aaveusdt":
                # 檢查是否在資料庫裏面
                symbol_name_list = self.dataprovider_online.SQL.get_db_data('show tables;')
                symbol_name_list = [y[0] for y in symbol_name_list]
                
                tb_symbol_name = each_symbol + '-F'
                tb_symbol_name = tb_symbol_name.lower()
                
                if tb_symbol_name in symbol_name_list:
                    pass
                else:
                    self.dataprovider_online.SQL.change_db_data(SqlSentense.create_table_name(tb_symbol_name))
                    df = pd.read_csv("History\\" + each_symbol.lower() + "-f.csv")
                    df.set_index('Datetime',inplace=True)

        
    def get_target_symbol(self):
        """ 
        # 取得交易標的

        """
        dataprovider = DataProvider(time_type='D')
        all_symbols = dataprovider.get_symbols_history_data()
        example = get_symobl_filter_useful(all_symbols)
        return example

        

    def change_money(self):
        """
            創建一個while 來重複校正這個金額
            並且記錄建議值於DB
            當下校正的時候 不會更改資料

        Args:
            last_trade_money (_type_): _description_
            balance (_type_): _description_
        """
        # 當系統資金過多 要減少
        balance = self.dataprovider_online.Binanceapp.get_futuresaccountbalance()

        while (abs(balance-self.engine.Trader.last_trade_money) / self.engine.Trader.last_trade_money) * 100 > 5:
            print("測試進入", "實際金額:", balance, "系統金額",
                  self.engine.Trader.last_trade_money)
            if self.engine.Trader.last_trade_money - balance > 0:
                self.engine.Trader.Portfolio_initcash = self.engine.Trader.Portfolio_initcash*0.98
            elif self.engine.Trader.last_trade_money - balance < 0:
                self.engine.Trader.Portfolio_initcash = self.engine.Trader.Portfolio_initcash*1.02
            print("初始資金:", self.engine.Trader.Portfolio_initcash)
            self.engine.Trader.logic_order()

    def check_money_level(self):
        """
            取得實時運作的資金水位 並且發出賴通知
            採用USDT 
        """
        last_trade_money = self.engine.Trader.last_trade_money
        balance = self.dataprovider_online.Binanceapp.get_futuresaccountbalance()

        if (abs(balance-last_trade_money) / last_trade_money) * 100 > 10:
            print('警告:請校正資金水位,投資組合水位差距超過百分之10')
            self.line_alert.req_line_alert("警告:請校正資金水位,投資組合水位差距超過百分之10")
            self.change_money()

    def timewritersql(self):
        """
            寫入保存時間
        """
        getAllTablesName = self.dataprovider_online.SQL.get_db_data(
            'show tables;')
        getAllTablesName = [y[0] for y in getAllTablesName]

        if 'sysstatus' not in getAllTablesName:
            # 將其更改為寫入DB
            self.dataprovider_online.SQL.change_db_data(
                """CREATE TABLE `crypto_data`.`sysstatus`(`ID` varchar(255) NOT NULL,`systeam_datetime` varchar(255) NOT NULL,PRIMARY KEY(`ID`));""")
            self.dataprovider_online.SQL.change_db_data(
                f"""INSERT INTO `sysstatus` VALUES ('1','{str(datetime.now())}');""")
        else:
            self.dataprovider_online.SQL.change_db_data(
                f""" UPDATE `sysstatus` SET `systeam_datetime`='{str(datetime.now())}' WHERE `ID`='1';""")

    def printfunc(self, *args):
        out_str = ''
        for i in args:
            out_str += str(i)+" "
            print(out_str)

    def get_catch(self, name, eachCatchDf):
        """
            取得當次回補的總資料並且不存在於DB之中

        """
        if name in self.new_symbol_map:
            new_df = pd.concat(
                [self.new_symbol_map[name].reset_index(), eachCatchDf])
            new_df.set_index('Datetime', inplace=True)
            # duplicated >> 重複 True 代表重複了
            new_df = new_df[~new_df.index.duplicated(keep='last')]
            self.new_symbol_map.update({name: new_df})
        else:
            eachCatchDf.set_index('Datetime', inplace=True)
            self.new_symbol_map.update({name: eachCatchDf})

    def main(self):
        self.printfunc("開始交易!!!")
        self.line_alert.req_line_alert('Crypto_trading 正式交易啟動')

        self.engine.Portfolio_online_register()
        symbol_name: list = self.engine.get_symbol_name()
        # 先將資料從DB撈取出來
        for name in symbol_name:
            original_df, eachCatchDf = self.dataprovider_online.get_symboldata(
                name, save=False)
            self.symbol_map.update({name: original_df})
            self.get_catch(name, eachCatchDf)

        last_min = None
        self.printfunc("資料讀取結束")
        # 透過迴圈回補資料
        while True:
            if datetime.now().minute != last_min or last_min is None:
                begin_time = time.time()
                # 取得原始資料
                for name, each_df in self.symbol_map.items():
                    original_df, eachCatchDf = self.dataprovider_online.reload_data_online(
                        each_df, name)

                    self.symbol_map.update({name: original_df})
                    self.get_catch(name, eachCatchDf)

                info = self.engine.get_symbol_info()
                for strategy_name, symbol_name, freq_time in info:
                    # 取得可交易之資料
                    trade_data = self.dataprovider_online.get_trade_data(
                        self.symbol_map[symbol_name], freq_time)

                    # ! 判斷是否要將trade_data資料減少
                    # 將資料注入
                    self.engine.register_data(strategy_name, trade_data)

                self.printfunc("開始進入回測")
                # 註冊完資料之後進入回測
                pf = self.engine.Portfolio_online_start()
                if not self.checkout:
                    # 檢查資金水位
                    self.check_money_level()
                    self.checkout = True

                pf = self.engine.Portfolio_online_start()
                last_status = pf.get_last_status()
                self.printfunc('目前交易狀態,校正之後', last_status)

                current_size = self.dataprovider_online.Binanceapp.getfutures_account_positions()
                self.printfunc("目前binance交易所內的部位狀態:", current_size)

                # >>比對目前binance 內的部位狀態 進行交易
                order_finally = self.dataprovider_online.transformer.calculation_size(
                    last_status, current_size)

                # 將order_finally 跟下單最小單位相比
                order_finally = self.dataprovider_online.Binanceapp.change_min_postion(
                    order_finally)

                self.printfunc("差異單", order_finally)

                if order_finally:
                    self.dataprovider_online.Binanceapp.execute_orders(
                        order_finally, self.line_alert, formal=False)

                self.printfunc("時間差", time.time() - begin_time)
                last_min = datetime.now().minute
                self.timewritersql()
            else:
                time.sleep(1)

            if self.dataprovider_online.Binanceapp.trade_count > 10:
                self.printfunc("緊急狀況處理-交易次數過多")
                sys.exit()


class AsyncTrading_systeam(Trading_systeam):
    def __init__(self) -> None:
        super().__init__()
        # check if already update, and reload data
        self.checkDailydata()

        # 取得要交易的標的
        market_symobl = list(map(lambda x: x[0], self.get_target_symbol()))

        # 取得binance實際擁有標的,合併 (因為原本有部位的也要持續追蹤)
        targetsymbol = self.datatransformer.target_symobl(
            market_symobl, self.dataprovider_online.Binanceapp.getfutures_account_name())

        # 將標得注入引擎
        self.asyncDataProvider = AsyncDataProvider()

        # 初始化投資組合 (傳入要買的標的物, 並且傳入相關參數)
        self.engine.Portfolio_online_register(
            targetsymbol, self.dataprovider_online.SQL.read_Dateframe("optimizeresult"))

        self.symbol_name: set = self.engine.get_symbol_name()

    def main(self):
        self.line_alert.req_line_alert('Crypto_trading 正式交易啟動')
        # 先將資料從DB撈取出來
        for name in self.symbol_name:
            original_df, eachCatchDf = self.dataprovider_online.get_symboldata(
                name, save=False)
            self.symbol_map.update({name: original_df})
            self.get_catch(name, eachCatchDf)

        last_min = None
        self.printfunc("資料讀取結束")
        # 透過迴圈回補資料
        while True:
            if datetime.now().minute != last_min or last_min is None:
                begin_time = time.time()
                # 取得原始資料
                for name, each_df in self.symbol_map.items():
                    # 這邊要進入catch裡面合併資料
                    original_df, eachCatchDf = self.datatransformer.mergeData(
                        name, each_df, self.asyncDataProvider.all_data)
                    self.symbol_map.update({name: original_df})
                    self.get_catch(name, eachCatchDf)

                info = self.engine.get_symbol_info()
                for strategy_name, symbol_name, freq_time in info:
                    # 取得可交易之資料
                    trade_data = self.dataprovider_online.get_trade_data(
                        self.symbol_map[symbol_name], freq_time)

                    # ! 判斷是否要將trade_data資料減少
                    # 將資料注入
                    self.engine.register_data(strategy_name, trade_data)

                self.printfunc("開始進入回測")
                # 註冊完資料之後進入回測
                pf = self.engine.Portfolio_online_start()
                if not self.checkout:
                    # 檢查資金水位
                    self.check_money_level()
                    self.checkout = True

                pf = self.engine.Portfolio_online_start()
                last_status = pf.get_last_status()
                self.printfunc('目前交易狀態,校正之後', last_status)

                current_size = self.dataprovider_online.Binanceapp.getfutures_account_positions()
                self.printfunc("目前binance交易所內的部位狀態:", current_size)
                
                # >>比對目前binance 內的部位狀態 進行交易
                order_finally = self.dataprovider_online.transformer.calculation_size(
                    last_status, current_size, self.symbol_map)

                # 將order_finally 跟下單最小單位相比
                order_finally = self.dataprovider_online.Binanceapp.change_min_postion(
                    order_finally)

                self.printfunc("差異單", order_finally)

                if order_finally:
                    self.dataprovider_online.Binanceapp.execute_orders(
                        order_finally, self.line_alert, current_size=current_size,symbol_map = self.symbol_map, formal=False)

                self.printfunc("時間差", time.time() - begin_time)
                last_min = datetime.now().minute
                self.timewritersql()
            else:
                time.sleep(1)

            if self.dataprovider_online.Binanceapp.trade_count > 10:
                self.printfunc("緊急狀況處理-交易次數過多")
                sys.exit()


class GUI_Trading_systeam(AsyncTrading_systeam):
    def __init__(self, GUI) -> None:
        super().__init__()
        self.GUI = GUI
        # 用來保存所有的文字檔 並且判斷容量用
        self.all_msg = []
        self.debug = Debug_tool.debug()

    def printfunc(self, *args):
        if len(self.all_msg) > 20:
            self.all_msg = []
            self.GUI.clear_info_signal.emit()

        out_str = ''
        for i in args:
            out_str += str(i)+" "

        self.all_msg.append(out_str)
        self.GUI.update_trade_info_signal.emit(out_str)
        self.debug.record_msg(out_str, log_level=logging.error)


if __name__ == '__main__':


    app = Trading_systeam()
    app.exportAllKbarsData()
