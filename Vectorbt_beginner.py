import vectorbt as vbt
import pandas as pd
import datetime

end_date = datetime.datetime.now()
start_data = end_date - datetime.timedelta(days=3)

btc_price = vbt.YFData.download(
    ["BTC-USD","ETH-USD","XMR-USD","ADA-USD"],
    interval = '1m',
    start=end_date,
    end=end_date,
    missing_index='drop').get("Close")


print(btc_price)


rsi = vbt.RSI.run(btc_price, window=[14,21])

entries: pd.Series = rsi.rsi_crossed_below(30)
exits: pd.Series = rsi.rsi_crossed_above(30)


pf = vbt.Portfolio.from_signals(btc_price, entries, exits)

# 回報率
print(pf.total_return())

# 可以顯示訂單狀況及回報（圖表化）
# pf.plot().show()

# 查看投資組合的狀態
# print(pf.stats())
# print(type(pf.stats())) # pd.Series

# 可以將Series 轉換成字串
# print(entries.to_string())


# 可以過濾出想看的資料
# print(entries[entries == True])
