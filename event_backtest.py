import pandas as pd
from typing import Union
from Count.pandas_count import Pandas_count, Event_count
import copy
from typing import List
import matplotlib.pyplot as plt
from random import randint
import numpy as np
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)


class Order_info(object):
    """ 用來處理訂單的相關資訊
        #       Order Id          Column            Timestamp          Size         Price       Fees  Side
        # 0            0  (30, 30, 0.01)  2019-09-09 19:00:00  9.649457e-01  10342.592000  19.960080   Buy
        # 1            1  (30, 30, 0.01)  2019-09-09 19:30:00  9.649457e-01  10388.463750  20.048607  Sell
        # 2            2  (30, 30, 0.01)  2019-09-11 19:00:00  9.836996e-01  10149.731050  19.968573   Buy
        # 3            3  (30, 30, 0.01)  2019-09-11 23:15:00  9.836996e-01   9961.035000  19.597333  Sell
        # 4            4  (30, 30, 0.01)  2019-09-12 04:15:00  9.616591e-01  10148.658375  19.519100   Buy
        # ...        ...             ...                  ...           ...           ...        ...   ...
        # 3073      3073  (30, 30, 0.01)  2022-10-26 22:30:00  2.770224e-07  20884.358250   0.000012  Sell
        # 3074      3074  (30, 30, 0.01)  2022-10-28 21:15:00  2.826708e-07  20385.336250   0.000012   Buy
        # 3075      3075  (30, 30, 0.01)  2022-10-28 21:45:00  2.826708e-07  20409.249000   0.000012  Sell
        # 3076      3076  (30, 30, 0.01)  2022-10-29 00:15:00  2.777880e-07  20685.083750   0.000011   Buy
        # 3077      3077  (30, 30, 0.01)  2022-10-29 00:30:00  2.777880e-07  20633.686500   0.000011  Sell
    Args:
        object (_type_): _description_
    """

    def __init__(self, datetime_list, order_list, execute_price: List[float], entryprice_list, buy_sizes_list: List[float],
                 sell_sizes_list: List[float], buy_Fees_list, sell_Fees_list, ClosedPostionprofit_list,
                 OpenPostionprofit_list) -> None:
        # 取得order儲存列
        self.order = pd.DataFrame(
            list(zip(datetime_list, order_list)), columns=['Datetime', 'Order'])

        self.order['Price'] = execute_price
        self.order['entryprice'] = entryprice_list
        self.order['buy_sizes'] = buy_sizes_list
        self.order['sell_sizes'] = sell_sizes_list
        self.order['buy_Fees'] = buy_Fees_list
        self.order['sell_Fees'] = sell_Fees_list
        self.order['ClosedPostionprofit'] = ClosedPostionprofit_list
        self.order['OpenPostionprofit'] = OpenPostionprofit_list
        self.order = self.order[self.order['Order'] != 0]

        self.order['Side'] = self.order['Order'].apply(
            lambda x: "Buy" if x == 1 else "Sell")
        self.order.set_index("Datetime", inplace=True)
        self.order.reset_index(inplace=True)
        self.order['Order Id'] = self.order.index
        self.order.set_index("Datetime", inplace=True)
        print(self.order)

    def profit_loss(self):
        """
        開始計算兩點損益

        """
        profits = []
        for i in range(0, len(self.order.index), 2):
            if len(self.order.iloc[i:i+2, ]) == 1:
                continue
            buy_size = self.order.iloc[i:i+2, 1].iloc[0]
            buy_price = self.order.iloc[i:i+2, 2].iloc[0]
            buy_Fees = self.order.iloc[i:i+2, 3].iloc[0]
            sell_size = self.order.iloc[i:i+2, 1].iloc[1]
            sell_price = self.order.iloc[i:i+2, 2].iloc[1]
            sell_Fees = self.order.iloc[i:i+2, 3].iloc[1]
            profits.append((buy_size * buy_price) -
                           (sell_size * sell_price) - buy_Fees - sell_Fees)

        return profits

        # profits_df = pd.DataFrame(data=profits,index=self.order[self.order['Order'] == -1].index,columns=['Profit'])
        # profits_df['Value'] = profits_df['Profit'].cumsum()
        # profits_df['Profit'].plot()
        # profits_df['Value'].plot(secondary_y=True)
        # plt.show()


class Strategy_info(object):
    """ 
    取得策略的基本資料及訊息
    Args:
        object (_type_): _description_
    """

    def __init__(self,
                 strategy_name: str,
                 symbol_name: str,
                 freq_time: int,
                 size: int,
                 fee: float,
                 slippage: float,
                 init_cash: float = 100.0,
                 symobl_type: str = "Futures") -> None:
        """ to get strategy info msg

        Args:
            strategy_name (str): _description_
            symbol_name (int): _description_
                like : BTCUSDT
            freq_time (int): _description_
            fee (float): _description_
            slippage (float): _description_
        """
        self.strategy_name = strategy_name
        self.symbol_name = symbol_name
        self.freq_time = freq_time
        self.size = size
        self.fee = fee
        self.slippage = slippage
        self.init_cash = init_cash
        self.symobl_type = symobl_type
        self.data = self.simulationdata

    @property
    def simulationdata(self):
        """

        Args:
            data_type (str, optional): _description_. Defaults to 'event_data'.

        Returns:
            _type_: _description_
        """
        if self.symobl_type == 'Futures':
            self.symobl_type = "F"

        df = pd.read_csv(
            f"{self.symbol_name}-{self.symobl_type}-{self.freq_time}-Min.csv")
        df.set_index("Datetime", inplace=True)
        return df


class Order_Strategy(object):
    """ order產生裝置
        由於事件導向 

    Args:
        object (_type_): _description_
    """

    def __init__(self, strategy_info: Strategy_info) -> None:
        self.strategy_info = strategy_info

    def logic_order(self):
        """
            撰寫邏輯的演算法
        """
        original_data = self.adjust_data()
        newdata = copy.deepcopy(original_data)

        # 此變數區列可以在迭代當中改變
        marketpostion = 0  # 部位方向
        entryprice = 0  # 入場價格
        buy_Fees = 0  # 買方手續費
        sell_Fees = 0  # 賣方手續費
        OpenPostionprofit = 0  # 未平倉損益(非累積式純計算有多單時)
        ClosedPostionprofit = self.strategy_info.init_cash  # 已平倉損益
        init_cash = self.strategy_info.init_cash
        slippage = self.strategy_info.slippage  # 滑價計算
        buy_sizes = self.strategy_info.size  # 買進部位大小
        sell_sizes = self.strategy_info.size  # 賣出進部位大小

        for each_index, each_price in original_data.items():
            Open = each_price['Open']
            High = each_price['High']
            Low = each_price['Low']
            Close = each_price['Close']
            Highest1 = each_price['High20']
            Lowest1 = each_price['Low20']

            # 策略所產生之資訊
            last_marketpostion = marketpostion
            last_entryprice = entryprice

            # 計算當前部位(main)
            if High > Highest1:
                marketpostion = 1

            if Low < Lowest1:
                marketpostion = 0

            # 計算當前賣出進部位大小 (由於賣出部位是買入給的 要先判斷賣出)
            if marketpostion == 0 and last_marketpostion == 1:
                sell_sizes = buy_sizes
            elif marketpostion == 1:
                sell_sizes = 0

            # 計算當前買進部位大小
            if marketpostion == 1 and last_marketpostion == 0:
                buy_sizes = init_cash / Close
            elif marketpostion == 0:
                buy_sizes = 0

            # 計算當前入場價
            entryprice = Event_count.get_entryprice(
                entryprice, Close, marketpostion, last_marketpostion, slippage)

            # 計算入場手續費
            buy_Fees = Event_count.get_buy_Fees(
                buy_Fees, self.strategy_info.fee, buy_sizes, Close, marketpostion, last_marketpostion)

            # 計算出場手續費
            sell_Fees = Event_count.get_sell_Fees(
                sell_Fees, self.strategy_info.fee, sell_sizes, Close, marketpostion, last_marketpostion)

            # 未平倉損益(非累積式純計算有單時)
            OpenPostionprofit = Event_count.get_OpenPostionprofit(
                OpenPostionprofit, marketpostion, last_marketpostion, buy_Fees, Close, buy_sizes, entryprice)

            # 計算已平倉損益(累積式)
            ClosedPostionprofit = Event_count.get_ClosedPostionprofit(
                ClosedPostionprofit, marketpostion, last_marketpostion, buy_Fees, sell_Fees, Close, sell_sizes, last_entryprice)

            # 計算已平倉損益(無單時)
            
            # 保存相關即時資訊
            newdata[each_index]['marketpostion'] = marketpostion
            newdata[each_index]['ClosedPostionprofit'] = ClosedPostionprofit
            newdata[each_index]['OpenPostionprofit'] = OpenPostionprofit
            newdata[each_index]['buy_sizes'] = buy_sizes
            newdata[each_index]['sell_sizes'] = sell_sizes
            newdata[each_index]['entryprice'] = entryprice
            newdata[each_index]['buy_Fees'] = buy_Fees
            newdata[each_index]['sell_Fees'] = sell_Fees

        # 取得單一元素的時間序列
        Close_list = Event_count.get_info(newdata, 'Close')
        marketpostion_list = Event_count.get_info(newdata, 'marketpostion')
        ClosedPostionprofit_list = Event_count.get_info(
            newdata, 'ClosedPostionprofit')
        OpenPostionprofit_list = Event_count.get_info(
            newdata, 'OpenPostionprofit')
        entryprice_list = Event_count.get_info(newdata, 'entryprice')
        buy_sizes_list = Event_count.get_info(newdata, 'buy_sizes')
        sell_sizes_list = Event_count.get_info(newdata, 'sell_sizes')
        buy_Fees_list = Event_count.get_info(newdata, 'buy_Fees')
        sell_Fees_list = Event_count.get_info(newdata, 'sell_Fees')
        datetime_list = Event_count.get_index(newdata)
        order_list = Event_count.get_order(marketpostion_list)

        # 將相關的資料 丟入總報表當中
        Order_info(datetime_list,
                   order_list,
                   Close_list,
                   entryprice_list,
                   buy_sizes_list,
                   sell_sizes_list,
                   buy_Fees_list,
                   sell_Fees_list,
                   ClosedPostionprofit_list,
                   OpenPostionprofit_list).order

    def adjust_data(self):
        """
            不是需要原數據 取得調整後數據
        """
        # 最小數據量的鎖定 未來可以加入

        df = self.strategy_info.data
        Open = df['Open']
        High = df['High']
        Low = df['Low']
        Close = df['Close']

        # 不可視未來
        df['High20'] = Pandas_count.highest(High, 20).shift()
        df['Low20'] = Pandas_count.lowest(Low, 20).shift()
        df.dropna(inplace=True)
        return df.to_dict("index")


strategy1 = Strategy_info("BTCUSDT-15K-OB", "BTCUSDT", 15, 1, 0.002, 0.0025)
Order_Strategy(strategy1).logic_order()
