from Database import SQL_operate


app = SQL_operate.DB_operate()
print(app.get_db_data("SHOW TABLES;"))


# """ 準備一個資料建構器 """

# import vectorbt as vbt

# binance_data = vbt.BinanceData.download(
#      "BTCUSDT",
#      start='2 hours ago UTC',
#      end='now UTC',
#      interval='1m'
# )

# print(binance_data)
# print(binance_data.get())


# import time
# time.sleep(60)

# binance_data = binance_data.update()
# print(binance_data.get())