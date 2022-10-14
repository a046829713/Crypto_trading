
import vectorbt as vbt
import pandas as pd
import numpy as np
import datetime


btc_price = pd.read_csv('BTCUSDT-1h-data.csv')
btc_price['timestamp'] = pd.to_datetime(btc_price['timestamp'])
btc_price.set_index('timestamp', inplace=True)
btc_price = btc_price['close']


def custom_indicator(close: np.ndarray, rsi_window=14, ma_window=50, entry=30, exit=70):
    rsi = vbt.RSI.run(close, window=rsi_window).rsi.to_numpy()
    ma = vbt.MA.run(close, ma_window).ma.to_numpy()
    trend = np.where(rsi > exit, -1, 0)
    trend = np.where((rsi < entry) & (close < ma),
                     1, trend)  # 這邊的感覺和 pandas 有點相像
    return trend


# 將自制指標放入工廠 創見自己的指標
ind = vbt.IndicatorFactory(
    class_name="Combination",
    short_name='comb',
    input_names=["close"],
    param_names=['rsi_window', 'ma_window', 'entry', 'exit'],  # 這邊是參數名稱
    output_names=['value'],

).from_apply_func(
    custom_indicator,
    rsi_window=14,
    ma_window=50,
    entry=30,
    exit=70,

)

res = ind.run(
    btc_price,
    rsi_window=np.arange(10, 40, 3),
    ma_window=np.arange(20, 200, 20),
    entry=np.arange(10, 40, 4),
    exit=np.arange(60, 85, 4),
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



returns = returns.groupby(level = ['comb_exit','comb_entry']).mean() # 必須要平均

print(returns.to_string())
print(returns.max())
print(returns.idxmax())


"""
'comb_rsi_window', 'comb_ma_window'


# heatmap >> 用來畫圖使用
fig = returns.vbt.heatmap(
    x_level = 'comb_rsi_window',
    y_level = 'comb_ma_window',
    # silder_level = 'symbol'
)


fig.show()

"""
