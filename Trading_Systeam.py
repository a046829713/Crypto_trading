from DataProvider import DataProvider, DataProvider_online
from Major.Symbol_filter import get_symobl_filter_useful
from Vecbot_backtest import Quantify_systeam_online, Optimizer
import time
from datetime import datetime
import sys
from LINE_Alert import LINE_Alert
import pandas as pd
from utils import Debug_tool
import logging
from Database.SQL_operate import SqlSentense


# 修正自動配比biance 內的保證金數
# websocket 修正資料供給
# 修正權重模式
# 增加總投組獲利平倉，或是單一策略平倉?


# 建立所有商品的優化(GUI > Trading_systeam > Optimizer)


class Trading_systeam():
    def __init__(self) -> None:
        self.symbol_map = {}
        # 這次新產生的資料
        self.new_symbol_map = {}
        self.engine = Quantify_systeam_online()
        # formal正式啟動環境
        self.dataprovider_online = DataProvider_online(formal=True)
        self.line_alert = LINE_Alert()
        self.checkout = False

    def OptimizeAllSymbols(self):
        """
            取得所有交易對
        """

        all_symbols = self.dataprovider_online.Binanceapp.get_targetsymobls()

        # 使用 Optimizer # 建立DB
        for eachsymbol in all_symbols:

            result = Optimizer(eachsymbol).optimize()
            # print(result)

            result = {'freq_time': 15, 'size': 1.0, 'fee': 0.002, 'slippage': 0.0025, 'symbol': 'BTCUSDT', 'Strategytype': 'TurtleStrategy',
                      'strategyName': 'BTCUSDT-15K-OB', 'highest_n1': 500, 'lowest_n2': 600, 'ATR_short1': 100.0, 'ATR_long2': 150.0, 'updatetime': '2023-02-28'}

            print()
            getAllTablesName = self.dataprovider_online.SQL.get_db_data(
                'show tables;')
            getAllTablesName = [y[0] for y in getAllTablesName]

            if 'optimizeresult' not in getAllTablesName:
                self.dataprovider_online.SQL.change_db_data(
                    SqlSentense.createOptimizResult())
                print("成功創建")

            # 先確認是否存在裡面

            # if result['']
            # self.dataprovider_online.SQL.change_db_data(
                print(f"""
                INSERT INTO `crypto_data`.`optimizeresult`
                    (`freq_time`, `size`, `fee`, `slippage`, `symbol`, `Strategytype`, `strategyName`, `highest_n1`, `lowest_n2`, `ATR_short1`, `ATR_long2`, `updatetime`)
                VALUES
                    {tuple(result.values())};""")
            break

    def get_target_symbol(self):
        dataprovider = DataProvider(time_type='D')
        all_symbols = dataprovider.get_symbols_history_data()
        example = get_symobl_filter_useful(all_symbols)
        return example

        # 取得交易標的(頻率不需要太頻繁 一個月一次即可)
        # ['SOLUSDT', 1.517890576242979], ['AVAXUSDT', 0.8844715966080059], ['COMPUSDT', 0.8142903121982619], ['AAVEUSDT', 0.5655210439257492], ['DEFIUSDT', 0.5171522556390977]

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
                """INSERT INTO `sysstatus` VALUES ('1','2023-02-21 17:07:57.184614');""")
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

        else:
            eachCatchDf.set_index('Datetime', inplace=True)
            self.new_symbol_map.update({name: eachCatchDf})

    def main(self):
        self.printfunc("開始交易!!!")
        self.line_alert.req_line_alert('Crypto_trading 正式交易啟動')
        self.engine.Portfolio_online_register()
        symbol_name: list = self.engine.get_symbol_name()

        # 初始化商品槓桿
        for each_symbol in symbol_name:
            Response = self.dataprovider_online.Binanceapp.client.futures_change_leverage(
                symbol=each_symbol, leverage=10)
            self.printfunc(Response)

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
                        order_finally, self.line_alert, formal=True)

                self.printfunc("時間差", time.time() - begin_time)
                last_min = datetime.now().minute
                self.timewritersql()
            else:
                time.sleep(1)

            if self.dataprovider_online.Binanceapp.trade_count > 10:
                self.printfunc("緊急狀況處理-交易次數過多")
                sys.exit()


class GUI_Trading_systeam(Trading_systeam):
    def __init__(self, GUI) -> None:
        self.symbol_map = {}
        # 這次新產生的資料
        self.new_symbol_map = {}

        self.engine = Quantify_systeam_online()
        # formal正式啟動環境
        self.dataprovider_online = DataProvider_online(formal=True)
        self.line_alert = LINE_Alert()
        self.checkout = False

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
    systeam = Trading_systeam()
    systeam.OptimizeAllSymbols()
