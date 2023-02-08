from Data.custom import Binance_server
import json

data = Binance_server(formal=True).client.futures_account_balance()

for i in data:
    if i['asset'] == 'USDT':
        print(i['balance'])
