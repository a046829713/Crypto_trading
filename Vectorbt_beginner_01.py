import vectorbt as vbt
import pandas as pd
import numpy as np
import datetime


btc_price = pd.read_csv('BTCUSDT-1h-data.csv')
btc_price['timestamp'] = pd.to_datetime(btc_price['timestamp'])
btc_price.set_index('timestamp', inplace=True)
btc_price = btc_price['close']



def custom_indicator(close:np.ndarray, rsi_window=14,ma_window = 50) :
    print(type(close)) # 這邊會變成numpy # align
    rsi = vbt.RSI.run(close, window=rsi_window).rsi.to_numpy()
    ma = vbt.MA.run(close,ma_window).ma.to_numpy()
    trend = np.where( rsi >70 ,-1,0)
    trend = np.where( (rsi <40) & (close < ma), 1,trend) # 這邊的感覺和 pandas 有點相像
    return trend


# 將自制指標放入工廠 創見自己的指標
ind = vbt.IndicatorFactory(
    class_name= "Combination",
    short_name= 'comb',
    input_names= ["close"],
    param_names= ['rsi_window','ma_window'], # 這邊是參數名稱
    output_names= ['value'],
    
).from_apply_func(
    custom_indicator,
    rsi_window = 14,
    ma_window = 50,
)

res = ind.run(
    btc_price,
    rsi_window = 14,
    ma_window = 50,
)



print(btc_price)


print(res.value)

entries = res.value == 1.0
exits = res.value == -1.0


pf = vbt.Portfolio.from_signals(btc_price,entries=entries,exits=exits)

