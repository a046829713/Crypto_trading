""" 
    refer to 'finlab_crypto' package
    url : 'https://github.com/finlab-python/finlab_crypto'

"""
from binance.client import Client
from binance.enums import HistoricalKlinesType
from binance.helpers import interval_to_milliseconds, convert_ts_str
import pandas as pd
import json
from dateutil import parser
import math
from datetime import timedelta, datetime, timezone
import re
import time
from utils.Date_time import parser_time
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

    def get_clinet(self, formal=False):
        if formal:
            # with open(r"/home/abcd/bi.txt", 'r') as file:
            with open(r"C:/bi_.txt", 'r') as file:
                data = file.read()
                account = data.split("\n")[0]
                passwd = data.split("\n")[1]

            print(account)
            print(passwd)
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
