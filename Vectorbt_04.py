
import vectorbt as vbt
import pandas as pd
import numpy as np
import datetime
import time
import talib
from numba import njit


begintime = time.time()

btc_price = pd.read_csv('BTCUSDT-1h-data.csv')
btc_price['timestamp'] = pd.to_datetime(btc_price['timestamp'])
btc_price.set_index('timestamp', inplace=True)
btc_price = btc_price['close']


RSI = vbt.IndicatorFactory.from_talib('RSI')



def produce_signal(rsi,entry,exit):
    trend = np.where(rsi > exit, -1, 0)
    trend = np.where((rsi < entry), 1, trend)  # 這邊的感覺和 pandas 有點相像
    return trend

def custom_indicator(close: np.ndarray, rsi_window=14, entry=30, exit=70):
    # rsi = talib.RSI(close, rsi_window)
    rsi = RSI.run(close,rsi_window).real.to_numpy()# 如果是使用多商品的話 要用內建的函數？
    return produce_signal(rsi,entry,exit)


# 將自制指標放入工廠 創見自己的指標
ind = vbt.IndicatorFactory(
    class_name="Combination",
    short_name='comb',
    input_names=["close"],
    param_names=['rsi_window', 'entry', 'exit'],  # 這邊是參數名稱
    output_names=['value'],

).from_apply_func(
    custom_indicator,
    rsi_window=14,
    entry=30,
    exit=70,
    to_2d = False
)


res = ind.run(
    btc_price,
    rsi_window=np.arange(10, 100, 2),
    entry=np.arange(10, 40, 2),
    exit=np.arange(60, 85, 2),
    param_product=True
)


# <class 'pandas.core.frame.DataFrame'> # <class 'pandas.core.series.Series'>
print(res.value.columns)

entries = res.value == 1.0
exits = res.value == -1.0


pf = vbt.Portfolio.from_signals(btc_price, entries=entries, exits=exits)


returns = pf.total_return()

# 可以用來過濾index
# returns = returns[returns.index.isin(['14'],level = "comb_rsi_window")]


# returns = returns.groupby(level = ['comb_exit','comb_entry']).mean() # 必須要平均

print(returns.to_string())
print(returns.max())
print(returns.idxmax())


endtime = time.time()


print("總共使用時間：", endtime - begintime)
