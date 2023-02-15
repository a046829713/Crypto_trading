from DataProvider import DataProvider, DataProvider_online
from Major.Symbol_filter import get_symobl_filter_useful
from Vecbot_backtest import Quantify_systeam_online
import time
from datetime import datetime
import sys
from LINE_Alert import LINE_Alert
import pandas as pd
from utils import Debug_tool
import logging

# 實際測試
# 修正回補速度過慢



class Trading_systeam():
    def __init__(self) -> None:
        self.symbol_map = {}
        # 這次新產生的資料
        self.new_symbol_map = {}
        self.engine = Quantify_systeam_online()
        # formal正式啟動環境
        self.dataprovider_online = DataProvider_online(formal=True)
        self.line_alert = LINE_Alert()

    def get_target_symbol(self):
        dataprovider = DataProvider(time_type='D')
        all_symbols = dataprovider.get_symbols_history_data()
        example = get_symobl_filter_useful(all_symbols)
        return example

        # 取得交易標的(頻率不需要太頻繁 一個月一次即可)
        # ['SOLUSDT', 1.517890576242979], ['AVAXUSDT', 0.8844715966080059], ['COMPUSDT', 0.8142903121982619], ['AAVEUSDT', 0.5655210439257492], ['DEFIUSDT', 0.5171522556390977]

    def check_money_level(self):
        last_trade_money = self.engine.Trader.last_trade_money
        balance = self.dataprovider_online.Binanceapp.get_futuresaccountbalance()
        if (abs(balance-last_trade_money) / last_trade_money) * 100 > 10:
            self.line_alert.req_line_alert("警告:請校正資金水位,投資組合水位差距超過百分之10")

    def wirte_time(self):
        """
            寫入保存時間
        """
        with open(r"Sysstatus.txt", 'w') as file:
            file.write(str(datetime.now()))

        self.printfunc('存活')
        
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
                symbol=each_symbol, leverage=20)
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

                # 檢查資金水位
                self.check_money_level()

                self.printfunc("最後資料表*************************************")
                last_status = pf.get_last_status()
                self.printfunc('目前交易狀態', last_status)
                self.printfunc("最後資料表*************************************")

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
                        order_finally, self.line_alert)

                self.printfunc("時間差", time.time() - begin_time)
                last_min = datetime.now().minute
                self.wirte_time()
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
        self.debug.record_msg(out_str,log_level=logging.error)

if __name__ == '__main__':
    systeam = Trading_systeam()
    print(systeam.main())
