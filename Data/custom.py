""" 
    refer to 'finlab_crypto' package
    url : 'https://github.com/finlab-python/finlab_crypto'

"""
from binance.client import Client
from binance.enums import HistoricalKlinesType
import pandas as pd
import os
from dateutil import parser
import math
from datetime import timedelta, datetime, timezone
import re

class BinanceDate(object):
    # CONSTANTS
    binsizes = {"1m": 1, "5m": 5, '15m': 15, '30m': 30,
                "1h": 60, '2h': 120, "4h": 240, "1d": 1440}
    batch_size = 750

    """
        'pip install python-binance'
    """

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
            """ 取得最新的時間 取得合約現貨等無差別 都是24小時 """
            new = pd.to_datetime(client.get_klines(symbol=symbol, interval=kline_size)[-1][0],
                                 unit='ms')

            # new2 = pd.to_datetime(client.futures_klines(symbol=symbol, interval=kline_size)[-1][0],
            #                      unit='ms')

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

        # 取得歷史資料
        klines = client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"),
                                              newest_point.strftime("%d %b %Y %H:%M:%S"), klines_type=HistoricalKlinesType.FUTURES)

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

    def __init__(self) -> None:
        self.clinet = Client()

    def getfuturesinfo(self) -> dict:
        """ 回傳交易所的合約

        Returns:
            _type_: _description_
        """
        return self.clinet.futures_exchange_info()

    def get_symbolinfo(self, symbol: str):
        """ 回傳想要查詢的商品資料

        Args:
            symbol (str): _description_

        Returns:
            _type_: _description_
        """
        return self.clinet.get_symbol_info(symbol)

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