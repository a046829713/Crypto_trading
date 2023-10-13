from Major.DataProvider import DataProvider_online, AsyncDataProvider
from Major.Symbol_filter import get_symobl_filter_useful
from Vecbot_backtest import Quantify_systeam_online, Optimizer
import time
from datetime import datetime, timedelta
import sys
from Infrastructure.LINE_Alert import LINE_Alert
import pandas as pd
from utils import BackUp, Debug_tool
import logging
from Database.SQL_operate import SqlSentense
import asyncio
from Datatransformer import Datatransformer
import os
from binance.exceptions import BinanceAPIException
from binance import BinanceSocketManager
import copy
from AppSetting import AppSetting


# 增加總投組獲利平倉，或是單一策略平倉?
# 增加匯出 optimizeresult 的功能,或許可以增加GUI
# 為了方便轉移 還是需要打包起來
# 建構輸入輸出檢查的decorator


# 檢查交易資料是否不斷重新生成

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
        # formal正式啟動環境
        self.dataprovider_online = DataProvider_online()
        
        self.engine = self.buildEngine()
        self.line_alert = LINE_Alert()
        self.checkout = False
        self.datatransformer = Datatransformer()
        self.check_all_need_table()

    def check_all_need_table(self):
        """
            感覺設計上,一開始在建立trading_systeam的時候,就要建立檢查table的機制,感覺會比用裝飾器來檢查資料庫更好

        Returns:
            _type_: _description_
        """

        BackUp.check_all_need_table()
    
    
    
    
    @BackUp.check_table_if_exits('lastinitcapital')
    def buildEngine(self):
        capital = self.dataprovider_online.SQL.get_db_data(
            "select *  from `lastinitcapital`;")
        return Quantify_systeam_online(capital[0][-1])

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
            self.dataprovider_online.reload_all_data(time_type='D')
        else:
            # 判斷幣安裡面所有可交易的標的
            allsymobl = self.dataprovider_online.Binanceapp.get_targetsymobls()
            all_tables = self.dataprovider_online.SQL.read_Dateframe(
                """show tables""")
            all_tables = [
                i for i in all_tables['Tables_in_crypto_data'].to_list() if '-f-d' in i]

            # 當有新的商品出現之後,會導致有錯誤,錯誤修正
            if list(filter(lambda x: False if x.lower() + "-f-d" in all_tables else True, allsymobl)):
                self.dataprovider_online.reload_all_data(time_type='D')
                

    def exportOptimizeResult(self):
        """
            將sql的優化資料匯出
        """
        print("測試進入")
        df = self.dataprovider_online.SQL.read_Dateframe("optimizeresult")
        df.set_index("strategyName", inplace=True)
        df.to_csv("optimizeresult.csv")

    @BackUp.check_table_if_exits(table_name="optimizeresult")
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

        print(strategylist)
        # 使用 Optimizer # 建立DB
        for eachsymbol in all_symbols:
            # 判斷每次要優化的策略名稱
            if optimize_strategy_type == 'TurtleStrategy':
                target_strategy_name = eachsymbol + "-15K-OB"
            elif optimize_strategy_type == 'VCPStrategy':
                target_strategy_name = eachsymbol + "-15K-OB-VCP"
            elif optimize_strategy_type == 'DynamicStrategy':
                target_strategy_name = eachsymbol + "-15K-OB-DY"
            elif optimize_strategy_type == 'DynamicVCPStrategy':
                target_strategy_name = eachsymbol + "-15K-OB-DYVCP"

            if target_strategy_name in strategylist:
                continue

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
        BackUp.check_file("History")

        for each_symbol in self.dataprovider_online.Binanceapp.get_targetsymobls():
            BackUp.exportKbarsData(each_symbol, self.dataprovider_online)

    def exportKbarsData(self, symbol: str, data_type: str = None):
        BackUp.check_file("History")
        BackUp.exportKbarsData(
            symbol, self.dataprovider_online, data_type=data_type)

    def importAllKbarsData(self):
        """
            將資料全部寫入MySQL

        """
        for each_symbol in self.dataprovider_online.Binanceapp.get_targetsymobls():
            print(each_symbol)
            # 檢查是否在資料庫裏面
            symbol_name_list = self.dataprovider_online.SQL.get_db_data(
                'show tables;')
            symbol_name_list = [y[0] for y in symbol_name_list]

            tb_symbol_name = each_symbol + '-F'
            tb_symbol_name = tb_symbol_name.lower()

            if tb_symbol_name in symbol_name_list:
                continue
            else:
                self.dataprovider_online.SQL.change_db_data(
                    SqlSentense.create_table_name(tb_symbol_name))

            file_path = "History\\" + each_symbol.lower() + "-f.csv"
            df = pd.read_csv(file_path)
            df.set_index('Datetime', inplace=True)

            self.dataprovider_online.SQL.write_Dateframe(
                df, tb_symbol_name, exists='append')
            print("開始刪除")
            os.remove(file_path)

    def get_target_symbol(self):
        """ 
        # 取得交易標的

        """
        all_symbols = self.dataprovider_online.get_symbols_history_data(
            time_type='D')
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
            print("實際金額:", balance, "系統金額",
                  self.engine.Trader.last_trade_money)
            if self.engine.Trader.last_trade_money - balance > 0:
                self.engine.Trader.Portfolio_initcash = self.engine.Trader.Portfolio_initcash*0.98
            elif self.engine.Trader.last_trade_money - balance < 0:
                self.engine.Trader.Portfolio_initcash = self.engine.Trader.Portfolio_initcash*1.02
            self.engine.Trader.logic_order()

        # 將優化完成的資料寫入DB
        print("初始資金:", self.engine.Trader.Portfolio_initcash)
        self.dataprovider_online.SQL.change_db_data(
            f"UPDATE `lastinitcapital` SET `capital` = {int(self.engine.Trader.Portfolio_initcash)} WHERE `ID` = '1';")
        print("更新初始化資金完成")

    def check_money_level(self):
        """
            取得實時運作的資金水位 並且發出賴通知
            採用USDT 
        """
        last_trade_money = self.engine.Trader.last_trade_money
        balance = self.dataprovider_online.Binanceapp.get_futuresaccountbalance()

        if (abs(balance-last_trade_money) / last_trade_money) * 100 > 10:
            self.line_alert.req_line_alert("警告:請校正資金水位,投資組合水位差距超過百分之10")
            self.change_money()

    @BackUp.check_table_if_exits(table_name="sysstatus")
    def timewritersql(self):
        """
            寫入保存時間
        """
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


class AsyncTrading_systeam(Trading_systeam):
    def __init__(self) -> None:
        super().__init__()
        self.check_and_reload_dailydata()
        self.process_target_symbol()
        self.init_async_data_provider()
        self.register_portfolio()

    def check_and_reload_dailydata(self):
        """ check if already update, and reload data"""
        self.checkDailydata()
        self.SendProcessBarUpdate(20)

    def process_target_symbol(self):
        # 取得要交易的標的
        market_symobl = list(map(lambda x: x[0], self.get_target_symbol()))
        # 取得binance實際擁有標的,合併 (因為原本有部位的也要持續追蹤)
        self.targetsymbol = self.datatransformer.target_symobl(
            market_symobl, self.dataprovider_online.Binanceapp.getfutures_account_name())
        self.SendProcessBarUpdate(40)

    def init_async_data_provider(self):
        # 將標得注入引擎
        self.asyncDataProvider = AsyncDataProvider()
        self.SendProcessBarUpdate(60)

    def register_portfolio(self):
        # 初始化投資組合 (傳入要買的標的物, 並且傳入相關參數)
        self.engine.Portfolio_online_register(
            self.targetsymbol, self.dataprovider_online.SQL.read_Dateframe("optimizeresult"))
        self.symbol_name: set = self.engine.get_symbol_name()
        self.SendProcessBarUpdate(80)

    async def main(self):
        self.printfunc("Crypto_trading 正式交易啟動")
        self.line_alert.req_line_alert('Crypto_trading 正式交易啟動')
        # 先將資料從DB撈取出來
        for name in self.symbol_name:
            original_df, eachCatchDf = self.dataprovider_online.get_symboldata(
                name)
            self.symbol_map.update({name: original_df})
            self.get_catch(name, eachCatchDf)

        last_min = None
        self.printfunc("資料讀取結束")
        # 透過迴圈回補資料
        while True:
            try:
                if datetime.now().minute != last_min or last_min is None:
                    begin_time = time.time()
                    # 取得原始資料
                    all_data_copy = await self.asyncDataProvider.get_all_data()

                    # 避免在self.symbol_map
                    symbol_map_copy = copy.deepcopy(self.symbol_map)
                    for name, each_df in symbol_map_copy.items():
                        # 這裡的name 就是商品名稱,就是symbol_name EX:COMPUSDT,AAVEUSDT
                        original_df, eachCatchDf = self.datatransformer.mergeData(
                            name, each_df, all_data_copy)
                        self.symbol_map[name] = original_df
                        self.get_catch(name, eachCatchDf)

                    
                    info = self.engine.get_symbol_info()
                    for strategy_name, symbol_name, freq_time in info:
                        # 取得可交易之資料
                        trade_data = self.dataprovider_online.get_trade_data(
                            self.symbol_map[symbol_name], freq_time)
                        
                        # 將資料注入
                        # 由於最新不確定突破或跌破,所以只給入已發生結束的歷史資料
                        self.engine.register_data(strategy_name, trade_data[:-1])

                    self.printfunc("開始進入回測")
                    # 註冊完資料之後進入回測
                    pf = self.engine.Portfolio_online_start()
                    if not self.checkout:
                        # 檢查資金水位
                        self.check_money_level()
                        self.checkout = True
                        pf = self.engine.Portfolio_online_start()

                    # 將資料發送給GUI
                    self.SendClosedProfit(pf.order['ClosedPostionprofit'])

                    last_status = pf.get_last_status()

                    self.printfunc('目前交易狀態,校正之後', last_status)

                    current_size = self.dataprovider_online.Binanceapp.getfutures_account_positions()
                    self.printfunc("目前binance交易所內的部位狀態:", current_size)

                    # >>比對目前binance 內的部位狀態 進行交易
                    order_finally = self.dataprovider_online.transformer.calculation_size(
                        last_status, current_size, self.symbol_map)

                    print("測試order_finally", order_finally)
                    # 將order_finally 跟下單最小單位相比
                    order_finally = self.dataprovider_online.Binanceapp.change_min_postion(
                        order_finally)

                    self.printfunc("差異單", order_finally)

                    if order_finally:
                        self.dataprovider_online.Binanceapp.execute_orders(
                            order_finally, self.line_alert, current_size=current_size, symbol_map=self.symbol_map, formal=True)

                    self.printfunc("時間差", time.time() - begin_time)
                    last_min = datetime.now().minute
                    self.timewritersql()
                else:
                    time.sleep(1)

                if self.dataprovider_online.Binanceapp.trade_count > AppSetting.get_emergency_times():
                    self.printfunc("緊急狀況處理-交易次數過多")
                    self.line_alert.req_line_alert('緊急狀況處理-交易次數過多')
                    sys.exit()

            except Exception as e:
                if isinstance(e, BinanceAPIException) and e.code == -1001:
                    Debug_tool.debug.print_info()
                else:
                    # re-raise the exception if it's not the expected error code
                    Debug_tool.debug.print_info()
                    raise e


class GUI_Trading_systeam(AsyncTrading_systeam):
    def __init__(self, GUI) -> None:
        self.GUI = GUI
        # 用來保存所有的文字檔 並且判斷容量用
        self.all_msg = []
        self.debug = Debug_tool.debug()
        super().__init__()

    def printfunc(self, *args):
        # 取代AsyncTrading_systeam 裡面的printfunc
        if len(self.all_msg) > 20:
            self.all_msg = []
            self.GUI.clear_info_signal.emit()

        out_str = ''
        for i in args:
            out_str += str(i)+" "

        self.all_msg.append(out_str)
        self.GUI.update_trade_info_signal.emit(out_str)
        self.debug.record_msg(out_str, log_level=logging.debug)

    def SendClosedProfit(self, data):
        self.GUI.GUI_CloseProfit.emit(data)

    def SendProcessBarUpdate(self, num: int):
        self.GUI.reload_dialog.update_info.emit(num)


if __name__ == '__main__':

    app = Trading_systeam()

    
    app.OptimizeAllSymbols('TurtleStrategy')
    
