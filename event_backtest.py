import pandas as pd
from typing import Union
from Count.pandas_count import Pandas_count, Event_count
import copy

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

class Order_Strategy():
    def logic_order(self):
        """
            撰寫邏輯的演算法
        """
        original_data = self.adjust_data()
        newdata = copy.deepcopy(original_data)

        # 此變數區列可以在迭代當中改變
        marketpostion = 0  # 部位方向

        for each_index, each_price in original_data.items():
            Open = each_price['Open']
            High = each_price['High']
            Low = each_price['Low']
            Close = each_price['Close']
            Highest1 = each_price['High20']
            Lowest1 = each_price['Low20']

            # 計算當前部位
            if High > Highest1:
                marketpostion = 1

            if Low < Lowest1:
                marketpostion = 0

            # 保存當前部位
            newdata[each_index]['marketpostion'] = marketpostion

        # 取得單一元素的時間序列
        marketpostion_list = Event_count.get_info(newdata,'marketpostion')
        datetime_list = Event_count.get_index(newdata)
        order_list = Event_count.get_order(marketpostion_list)
        
        return pd.DataFrame(list(zip(datetime_list,order_list)),columns=['Datetime','Order'])
    
    def adjust_data(self):
        """
            不是需要原數據 取得調整後數據
        """
        # 最小數據量的鎖定 未來可以加入

        df = self.simulationdata('df_data')
        Open = df['Open']
        High = df['High']
        Low = df['Low']
        Close = df['Close']

        # 不可視未來
        df['High20'] = Pandas_count.highest(High, 20).shift()
        df['Low20'] = Pandas_count.lowest(Low, 20).shift()
        df.dropna(inplace=True)
        return df.to_dict("index")

    def simulationdata(self, data_type: str = 'event_data'):
        if data_type == 'event_data':
            df1 = pd.read_csv("BTCUSDT-F-15-Min.csv")
            df1.set_index("Datetime", inplace=True)
            return df1.to_dict("index")
        elif data_type == 'df_data':
            df1 = pd.read_csv("BTCUSDT-F-15-Min.csv")
            df1.set_index("Datetime", inplace=True)
            return df1


strategy = Order_Strategy()
df = strategy.logic_order()
df.set_index("Datetime",inplace=True)

# =================================================================================================
import numpy as np
import pandas as pd
from datetime import datetime
import talib
from numba import njit
import vectorbt as vbt
from vectorbt.utils.colors import adjust_opacity
from vectorbt.utils.enum_ import map_enum_fields
from vectorbt.base.reshape_fns import broadcast, flex_select_auto_nb, to_2d_array
from vectorbt.portfolio.enums import SizeType, Direction, NoOrder, OrderStatus, OrderSide
from vectorbt.portfolio import nb
from random import randint

import warnings
warnings.simplefilter("ignore", UserWarning)


"""
    用來測試 order的資料
"""

df1 = pd.read_csv("BTCUSDT-F-15-Min.csv")
df2 = pd.read_csv("ETHUSDT-F-15-Min.csv")

frames_list = [df1,df2]

for each_df in frames_list:
    each_df.set_index("Datetime",inplace=True)


bottle1 = ('BTCUSDT',df1)
bottle2 = ('ETHUSDT',df2)


frame_list = []
frame_list.append(bottle1)
frame_list.append(bottle2)


ohlcv ={}
# 兩個商品
for symbol_name,each_frame in frame_list:
    # 多個欄位
    for colname in each_frame.columns:
        if colname in ohlcv:
            ohlcv[colname][symbol_name] = each_frame[colname]
        else:
            new_df = pd.DataFrame()
            new_df[symbol_name] = each_frame[colname]
            new_df.columns.name = colname
            ohlcv[colname] = new_df



for _colname,data_df in ohlcv.items():
    data_df:pd.DataFrame
    data_df.dropna(inplace=True)
    print('*'*120)
    

result = pd.DataFrame.vbt.empty_like(ohlcv['Open'], fill_value=0.)
result['BTCUSDT'] = df['Order']
result['ETHUSDT'] = df['Order']

size = result


# 基本參數配置
# set default fees and slippage
vbt.settings.portfolio['init_cash'] = 10000.0  # in $
vbt.settings.portfolio['fees'] = 0.002      # in %
vbt.settings.portfolio['slippage'] = 0.0025  # in %

direction = ['longonly']  # per column


pf = vbt.Portfolio.from_orders(ohlcv['Close'], size, direction=direction)
print(pf.orders.records_readable)
print(pf.stats())