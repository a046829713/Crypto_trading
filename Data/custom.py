""" 
    refer to 'finlab_crypto' package
    url : 'https://github.com/finlab-python/finlab_crypto'

"""
from binance.client import Client
from binance.enums import HistoricalKlinesType
from binance.enums import SIDE_BUY, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, SIDE_SELL
from binance.helpers import interval_to_milliseconds, convert_ts_str
import pandas as pd
from dateutil import parser
import math
from datetime import timedelta, datetime
import re
import time
import json
from utils.Date_time import parser_time
from utils.Debug_tool import debug
import time


class BinanceDate(object):
    """
        'pip install python-binance'
    """
    # CONSTANTS
    binsizes = {"1m": 1, "5m": 5, '15m': 15, '30m': 30,
                "1h": 60, '2h': 120, "4h": 240, "1d": 1440}
    batch_size = 750

    @classmethod
    def historicalklines(cls, symbol, interval, start_str=None, end_str=None, limit=1000,
                         klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT, client: Client = None):
        """
            Get Historical Klines from Binance (spot or futures)
            to copy binance.client._historical_klines to add tqdm by self 


        """
        # init our list
        output_data = []

        # convert interval to useful value in seconds
        timeframe = interval_to_milliseconds(interval)

        # if a start time was passed convert it
        start_ts = convert_ts_str(start_str)

        # establish first available start timestamp
        if start_ts is not None:
            first_valid_ts = client._get_earliest_valid_timestamp(
                symbol, interval, klines_type)
            start_ts = max(start_ts, first_valid_ts)

        # if an end time was passed convert it
        end_ts = convert_ts_str(end_str)
        if end_ts and start_ts and end_ts <= start_ts:
            return output_data

        idx = 0
        from tqdm.auto import tqdm
        with tqdm() as pbar:
            pbar.set_description(parser_time.change_ts_to_str(start_ts/1000))
            while True:
                # fetch the klines from start_ts up to max 500 entries or the end_ts if set
                temp_data = client._klines(
                    klines_type=klines_type,
                    symbol=symbol,
                    interval=interval,
                    limit=limit,
                    startTime=start_ts,
                    endTime=end_ts
                )

                # append this loops data to our output data
                if temp_data:
                    output_data += temp_data

                # handle the case where exactly the limit amount of data was returned last loop
                # check if we received less than the required limit and exit the loop
                if not len(temp_data) or len(temp_data) < limit:
                    # exit the while loop
                    break

                # increment next call by our timeframe
                start_ts = temp_data[-1][0] + timeframe

                # exit loop if we reached end_ts before reaching <limit> klines
                if end_ts and start_ts >= end_ts:
                    break

                pbar.set_description("{} - {}".format(
                    parser_time.change_ts_to_str(start_ts/1000),
                    parser_time.change_ts_to_str(end_ts/1000)
                ))

                # sleep after every 3rd call to be kind to the API
                idx += 1
                if idx % 3 == 0:
                    time.sleep(1)

                pbar.update(1)

        return output_data

    @classmethod
    def minutes_of_new_data(cls, symbol, kline_size: str, data: pd.DataFrame, source: str, client: Client):
        """Process old and new histrical price data format through binance api.

        The boundary between new data and old data is 2017.1.1.

        Args:
        symbol (str): Trading pair (ex: BTCUSDT).
        kline_size (str): A frequency of the price data (ex: "1m", "5m",'15m', '30m', "1h", '2h', "4h", "1d")
        data (dataframe): The data from get_all_binance() crawlers.
        source (str): data source (ex:'binance','bitmex')
        client (Binance.Client) (optional): Binance Client object.

        Returns:
        old: OHLCV DataFrame of old format.
        new: OHLCV DataFrame of new format.
        """
        if len(data) > 0:
            old = parser.parse(data["Datetime"].iloc[-1])
        elif source == "binance":
            old = datetime.strptime('1 Jan 2017', '%d %b %Y')
        elif source == "bitmex":
            old = client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=False).result()[0][0][
                'Datetime']

        if source == "binance":
            """ 有些商品只有期貨的部份 所以還是以期貨的API為主 """
            # new = pd.to_datetime(client.get_klines(symbol=symbol, interval=kline_size)[-1][0],
            #                      unit='ms')

            new = pd.to_datetime(client.futures_klines(symbol=symbol, interval=kline_size)[-1][0],
                                 unit='ms')

        if source == "bitmex":
            new = \
                client.Trade.Trade_getBucketed(
                    symbol=symbol, binSize=kline_size, count=1, reverse=True).result()[0][0]['Datetime']

        return old, new + timedelta(minutes=1)

    @classmethod
    def download(cls, original_df: pd.DataFrame, symbol, kline_size):
        """
        Getting histrical price data through binance api.

        Original code from: https://medium.com/swlh/retrieving-full-historical-data-for-every-cryptocurrency-on-binance-bitmex-using-the-python-apis-27b47fd8137f

        Args:
        symbol (str): Trading pair (ex: BTCUSDT).
        kline_size (str): A frequency of the price data (ex: "1m", "5m",'15m', '30m', "1h", '2h', "4h", "1d")
        save (bool): Save the results in ./history/ to improve the retreive waiting time.
        client (Binance.Client) (optional): Binance Client object.

        Returns:
            pd.DataFrame: OHLCV data for all
        """
        client = Client()
        oldest_point, newest_point = cls.minutes_of_new_data(
            symbol, kline_size, original_df, source="binance", client=client)

        delta_min = (newest_point - oldest_point).total_seconds() / 60
        available_data = math.ceil(delta_min / cls.binsizes[kline_size])

        if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'):
            print('Downloading all available %s data for %s. Be patient..!' %
                  (kline_size, symbol))
        else:
            print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (
                delta_min, symbol, available_data, kline_size))

        # 取得歷史資料改寫
        klines = cls.historicalklines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"),
                                      newest_point.strftime("%d %b %Y %H:%M:%S"), klines_type=HistoricalKlinesType.FUTURES, client=client)

        data = pd.DataFrame(klines,
                            columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'close_time', 'quote_av',
                                     'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])

        data['Datetime'] = pd.to_datetime(data['Datetime'], unit='ms')

        if len(original_df) > 0:
            original_df['Datetime'] = pd.to_datetime(original_df['Datetime'])
            new_df = pd.concat([original_df, data])
        else:
            new_df = data

        new_df.set_index('Datetime', inplace=True)
        # duplicated >> 重複 True 代表重複了
        new_df = new_df[~new_df.index.duplicated(keep='last')]

        print('商品資料回補完成!')
        new_df = new_df.astype(float)
        return new_df


class Binance_server(object):
    """
        用來呼叫幣安的相關應用

    Args:
        object (_type_): 
    """

    def __init__(self, formal=False) -> None:
        self.get_clinet(formal)
        self.trade_count = 0

    def get_clinet(self, formal=False):
        if formal:
            # with open(r"/home/abcd/bi.txt", 'r') as file:
            with open(r"C:/bi_.txt", 'r') as file:
                data = file.read()
                account = data.split("\n")[0]
                passwd = data.split("\n")[1]

            self.client = Client(account, passwd)
        else:
            self.client = Client()

    def getaccount(self) -> dict:
        """ 回傳保證金帳戶
        Returns:
            _type_: _description_
        """
        return self.client.get_margin_account()

    def getfuturesinfo(self) -> dict:
        """ 回傳交易所的合約

        Returns:
            _type_: _description_
        """
        return self.client.futures_exchange_info()

    def getMinimumOrderQuantity(self):
        """
            取得最小下單數量限制
        """
        data = self.client.futures_exchange_info()
        out_dict = {}
        for symbol in data['symbols']:
            out_dict.update({symbol['symbol']: symbol['filters'][2]['minQty']})

        return out_dict

    def get_symbolinfo(self, symbol: str):
        """ 回傳想要查詢的商品資料

        Args:
            symbol (str): _description_

        Returns:
            _type_: _description_
        """
        return self.client.get_symbol_info(symbol)

    def get_targetsymobls(self) -> list:
        """
            to call api get futures symbol and clean data
        Returns:
            list: _description_
        """
        data = self.getfuturesinfo()
        out_list = []
        for key in data.keys():
            if key == 'symbols':
                for each_data in data[key]:
                    if each_data['marginAsset'] == 'USDT':
                        # 目前怪怪的合約都拋棄不要（有數字的大概論都有特殊意義）
                        clear_name = re.findall(
                            '[A-Z]+USDT', each_data['symbol'])
                        if clear_name:
                            if each_data['symbol'] == clear_name[0]:
                                if each_data['symbol'] not in out_list:
                                    out_list.append(each_data['symbol'])
        return out_list

    def getfutures_account_positions(self):
        """
            取得合約部位 >> 裡面還可以看到其他資訊
        """
        data = self.client.futures_account()
        out_put = {}
        for i in data['positions']:
            if i['initialMargin'] == '0':
                continue
            out_put.update({i['symbol']: i['positionAmt']})

        return out_put

    def execute_orders(self, order_finally: dict, model=ORDER_TYPE_MARKET):
        """
            Execute orders to Binance.
            use for futures 
            to develop data = 2023-1-15
            note i can't find create_test_order by futures. 


            To place a futures limit order:
            binance_client.futures_create_order(
                symbol='BTCUSDT',
                type='LIMIT',
                timeInForce='GTC',  # Can be changed - see link to API doc below
                price=30000,  # The price at which you wish to buy/sell, float
                side='BUY',  # Direction ('BUY' / 'SELL'), string
                quantity=0.001  # Number of coins you wish to buy / sell, float
            )

            To place a futures market order:
            binance_client.futures_create_order(
                symbol='BTCUSDT',
                type='MARKET',
                timeInForce='GTC',
                side='BUY',
                quantity=0.001
            )

            2. 生效時間
            有效時間表示您的訂單在執行或過期之前將保持有效的時間。這樣可以讓您對時間參數更加具體，您可以在下單時自定義時間。
            在幣安，您可以下 GTC（取消前有效）、IOC（立即取消或取消）或 FOK（執行或終止）訂單：
            GTC (Good-Till-Cancel)：訂單將持續到完成或您取消為止。
            IOC (Immediate-Or-Cancel)：訂單將嘗試以可用的價格和數量立即執行全部或部分訂單，然後取消訂單中任何剩餘的、未完成的部分。如果您下單時所選價格沒有數量可用，將立即取消。請注意，不支持冰山訂單。
            FOK (Fill-Or-Kill)：指示訂單立即全額執行（filled），否則將被取消（kill）。請注意，不支持冰山訂單。
        """

        self.trade_count += 1
        print('目前交易次數', self.trade_count)
        print(f"進入下單,目前下單模式:{model}")

        # 取得最小單位限制
        MinimumQuantity = self.getMinimumOrderQuantity()

        for symbol, ready_to_order_size in order_finally.items():
            # 先將各式各樣的參數準備好

            # 取得下單模式
            if model == 'MARKET':
                order_type = ORDER_TYPE_MARKET
            else:
                order_type = ORDER_TYPE_LIMIT

            # 取得 side 買賣方向
            if ready_to_order_size > 0:
                order_side = SIDE_BUY
            else:
                order_side = SIDE_SELL

            # 取得 quantity數量
            order_quantity = abs(ready_to_order_size)

            # 判斷是否足夠下單
            if divmod(order_quantity, float(MinimumQuantity[symbol]))[0] == 0:
                debug.record_msg(
                    f"this {symbol}  is to small ,order_quantity:{order_quantity} and MinimumQuantity:{float(MinimumQuantity[symbol])}")
                return

            if model == 'MARKET':
                order_timeInForce = 'IOC'
            else:
                order_timeInForce = 'GTC'  # 這邊要在注意

            print(dict(side=order_side,
                       type=order_type,
                       symbol=symbol,
                       timeInForce=order_timeInForce,
                       quantity=order_quantity))

            # 丟入最後create 單裡面
            # self.client.futures_create_order(
            #     side=order_side,
            #     type=order_type,
            #     symbol=symbol,
            #     timeInForce=order_timeInForce,
            #     quantity=order_quantity
            # )
