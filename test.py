from binance.client import Client

# Initialize client with API key and secret key
client = Client("YOUR_API_KEY", "YOUR_SECRET_KEY")

# Define the symbol for the futures contract
symbol = "BTCUSDT"

# Define the order side (BUY or SELL)
side = "BUY"

# Define the order type (LIMIT or MARKET)
order_type = "LIMIT"

# Define the quantity of the order
quantity = 1

# Define the price of the order
price = 9000

# Define the time in force (GTC, IOC, FOK)
time_in_force = "GTC"

# Place the order
order = client.futures_create_order(
    symbol=symbol,
    side=side,
    order_type=order_type,
    quantity=quantity,
    price=price,
    time_in_force=time_in_force
)

# Print the order details
print(order)




# def cancel_orders(self,symbol):
#     orders = self.client.get_open_orders(symbol=symbol)
#     for o in orders:
#         self.client.cancel_order(symbol=symbol, orderId=o['orderId'])



#         print('|---------EXECUTION LOG----------|')
#         print('| time: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

#         trades = {}
#         for s, lot in transactions.final_value.items():

#             self.cancel_orders(s)

#             if lot == 0:
#                 continue

#             side = SIDE_BUY if lot > 0 else SIDE_SELL
#             try:
#                 args = dict(
#                     side=side,
#                     type=ORDER_TYPE_MARKET,
#                     symbol=s,
#                     quantity=abs(lot))

#                 if mode == 'LIMIT':
#                     args['price'] = transactions.price.loc[s]
#                     args['type'] = ORDER_TYPE_LIMIT
#                     args['timeInForce'] = 'GTC'

#                 order_func(**args)
#                 order_result = 'success'
#                 print('|', mode, s, side, abs(lot), order_result)
#             except Exception as e:
#                 print('| FAIL', s, s, side, abs(lot), str(e))
#                 order_result = 'FAIL: ' + str(e)

#             trades[s] = {
#                 **args,
#                 'result': order_result,
#             }

#         return pd.DataFrame(trades).transpose()