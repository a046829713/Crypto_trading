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
    
    
print(ohlcv['Open'])
result = pd.DataFrame.vbt.empty_like(ohlcv['Open'], fill_value=0.)
result = result.vbt.fshift(1)
size = result


print(size)
exit()
# ============================================================================
# 基本參數配置
# set default fees and slippage
vbt.settings.portfolio['init_cash'] = 10000.0  # in $
vbt.settings.portfolio['fees'] = 0.002      # in %
vbt.settings.portfolio['slippage'] = 0.0025  # in %

# Simulate portfolio
pf = vbt.Portfolio.from_orders(
    close = ohlcv['Close'],
    size = size,
    size_type='Amount',
    price=ohlcv['Open'],
)

# # Run simulation, with rebalancing monthly
# rb_pf = vbt.Portfolio.from_orders(
#     close=_price,
#     size=rb_size,
#     size_type='targetpercent',
#     group_by='symbol_group',
#     cash_sharing=True,
#     call_seq='auto'  # important: sell before buy
# )




print(pf.orders.records_readable)
print(pf.stats())