from tqdm import tqdm
import vectorbt as vbt
import pandas as pd
import numpy as np
import datetime
import time
import talib
from numba import njit
import gc
from typing import Tuple
from Straetgy import Strategy


# 基本參數配置
# set default fees and slippage
vbt.settings.portfolio['init_cash'] = 10000.0  # in $
vbt.settings.portfolio['fees'] = 0.002      # in %
vbt.settings.portfolio['slippage'] = 0.0025  # in %


df = pd.read_csv('BTCUSDT-F-15-Min.csv')
df.set_index('Datetime', inplace=True)


@Strategy(highest_1=30, lowest_1=30, win_out=0.01)
def turtle_strategy(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    Open = df['Open']
    High = df['High']
    Low = df['Low']
    Close = df['Close']

    Highest_var = High.rolling(int(turtle_strategy.highest_1)).max()
    Lowest_var = Low.rolling(int(turtle_strategy.lowest_1)).min()

    entries = (Close > Highest_var.shift())
    exits = (Close < Lowest_var.shift())

    # 用來添加停損停利模式
    ohlcstx = vbt.OHLCSTX.run(
        entries,
        Open,
        High,
        Low,
        Close,
        tp_stop=[turtle_strategy.win_out]
    )
    exits = exits | ohlcstx.exits
    return entries, exits


# 普通模式
# entries, exits = turtle_strategy(df)

# pf = vbt.Portfolio.from_signals(df['close'], entries=entries, exits=exits)

# print(pf.total_return())
# print(pf.orders.records_readable)
# pf.plot().show()


# 最佳化mode
variables = {"highest_1": list(range(10, 500, 10)), "lowest_1": list(range(
    10, 500, 10)), "win_out": list(map(lambda x: x*0.01, list(range(1, 15, 1))))}

pf = turtle_strategy.backtest_Hyperparameter_optimization(df, variables)


# 一般模式測試
# pf = turtle_strategy.backtest(df,size = 1)
# print(pf)
# print(pf.orders.records_readable)

# # 查看權益數之圖表
# pf.value().vbt.plot().show()


# from vectorbt import Portfolio


# Portfolio.metrics