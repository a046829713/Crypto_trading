import pandas as pd
from utils.Date_time import parser_time
import time
from utils.Debug_tool import debug
from utils.TimeCountMsg import TimeCountMsg
import numpy as np


class Datatransformer:
    def get_tradedata(self, original_df: pd.DataFrame, freq: int = 30):
        """
            將binance 的UTC 資料做轉換 變成可以交易的資料
            採用biance 官方向前機制

            # 如果是使用Mulitcharts 會變成向後機制

        Args:
            original_df:
                data from sql

            freq (int): 
                "this is resample time like"

        """
        df = original_df.copy()
        # 讀取資料(UTC原始資料)
        df.reset_index(inplace=True)

        df["Datetime"] = df['Datetime'].apply(parser_time.changetime)
        df.set_index("Datetime", inplace=True, drop=False)
        df = self.drop_colunms(df)

        # 採用biance 向前機制
        new_df = pd.DataFrame()
        new_df['Open'] = df['Open'].resample(
            rule=f'{freq}min', label="left").first()
        new_df['High'] = df['High'].resample(
            rule=f'{freq}min', label="left").max()
        new_df['Low'] = df['Low'].resample(
            rule=f'{freq}min', label="left").min()
        new_df['Close'] = df['Close'].resample(
            rule=f'{freq}min', label="left").last()
        new_df['Volume'] = df['Volume'].resample(
            rule=f'{freq}min', label="left").sum()
        return new_df

    def drop_colunms(self, df: pd.DataFrame):
        """
            拋棄不要的Data

        """

        for key in df.columns:
            if key not in ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']:
                df = df.drop(columns=[key])

        return df

    def calculation_size(self, systeam_size: dict, true_size: dict, symbol_map: dict,exchange_info:dict) -> dict:
        """
            用來比較 系統部位 和 Binance 交易所的實際部位

        Args:
            systeam_size (dict): example :{'BTCUSDT-15K-OB': [1.0, 0.37385995823410634], 'ETHUSDT-15K-OB': [1.0, 5.13707471134965],'BTCUSDT-30K-OB': [1.0, 0.995823410634], 'ETHUSDT-17K-OB': [1.0, 2.13707471134965]}
            true_size (dict): example :{'ETHUSDT': '10.980', 'BTCUSDT': '0.420'} 

        Returns:
            dict: {'BTCUSDT': 0.9496833688681066, 'ETHUSDT': -3.7058505773006996}


            當計算出來的結果 + 就是要買 - 就是要賣

        """
        min_notional_map = self.Get_MIN_NOTIONAL(exchange_info=exchange_info)
        combin_dict = {}
        for name_key, status in systeam_size.items():
            combin_symobl = name_key.split('-')[0]
            if combin_symobl in combin_dict:
                combin_dict.update(
                    {combin_symobl: combin_dict[combin_symobl] + (status[0] * status[1])})
            else:
                combin_dict.update({combin_symobl: status[0] * status[1]})

        # 下單四捨五入
        for each_symbol, each_value in combin_dict.items():
            combin_dict[each_symbol] = round(combin_dict[each_symbol], 2)

        diff_map = {}
        for symbol_name, postition_size in combin_dict.items():
            if true_size.get(symbol_name, None) is None:
                if postition_size == 0:
                    continue
                diff_map.update({symbol_name: postition_size})
            else:
                # 下單要符合幣安各商品最小下單金額限制
                diff = postition_size - float(true_size[symbol_name])                
                if diff > 0 and abs(symbol_map[symbol_name]['Close'].iloc[-1] * (diff)) < min_notional_map[symbol_name]:
                    continue
                diff_map.update(
                    {symbol_name: postition_size - float(true_size[symbol_name])})

        # 如果已經不再系統裡面 就需要去close
        for symbol_name, postition_size in true_size.items():
            if symbol_name not in combin_dict:
                diff_map.update({symbol_name: - float(postition_size)})

        return diff_map

    def mergeData(self, symbol_name: str, lastdata: pd.DataFrame, socketdata: dict):
        """合併資料用來

        Args:
            symbol_name (str) : "BTCUSDT" 
            lastdata (pd.DataFrame): 存在Trading_systeam裡面的更新資料
            socketdata (dict): 存在AsyncDataProvider裡面的即時資料

            [1678000140000, '46.77', '46.77', '46.76', '46.76', '6.597', 1678000199999, '308.51848', 9, '0.000', '0.00000', '0']]
        """
        # 先將catch 裡面的資料做轉換 # 由於當次分鐘量不會很大 所以決定不清空 考慮到異步問題

        if socketdata.get(symbol_name, None) is not None:
            if socketdata[symbol_name]:
                df = pd.DataFrame.from_dict(
                    socketdata[symbol_name], orient='index')
                df.reset_index(drop=True, inplace=True)
                df['Datetime'] = pd.to_datetime(df['Datetime'])
            else:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()

        # lastdata
        lastdata.reset_index(inplace=True)
        new_df = pd.concat([lastdata, df])

        new_df.set_index('Datetime', inplace=True)
        # duplicated >> 重複 True 代表重複了 # 過濾相同資料
        new_df = new_df[~new_df.index.duplicated(keep='last')]
        new_df = new_df.astype(float)

        return new_df, df

    def target_symobl(self, market_symobl: list, binance_catch: list):
        """
            用來將所有商品合併在一起,當市場狀況很差的時候,只監控比特幣
        Args:
            market_symobl (list): 取得目前要輪動交易的標的
            binance_catch (list): Binance 目前擁有部位的商品 (有部位的要繼續追蹤)
        """

        market_symobl.extend(binance_catch)

        if market_symobl:
            return list(set(market_symobl))
        else:
            return ['BTCUSDT']

    def trans_int16(self, data: dict):
        """
            用來轉變字串(json dumps 的時候)
            轉換np.int16
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, np.int16):
                    data[key] = int(value)
        return data

    def generate_table_name(self, symbol_name, symbol_type, time_type, iflower=True):
        """
        根据给定的参数生成表名。

        参数:
        symbol_name (str): 符号名
        symbol_type (str): 符号类型 ('FUTURES', 'SPOT')
        time_type (str): 时间类型 ('1d', '1m')
        iflower (bool): 如果为True，则将表名转换为小写

        返回:
        str: 生成的表名
        """
        # 根据 symbol_type 修改符号名
        if symbol_type == 'FUTURES':
            tb_symbol_name = symbol_name + '-F'
        elif symbol_type == 'SPOT':
            tb_symbol_name = symbol_name

        # 根据 time_type 修改符号名
        if time_type == '1d':
            tb_symbol_name = tb_symbol_name + '-D'
        elif time_type == '1m':
            tb_symbol_name = tb_symbol_name

        # 如果 iflower 为 True，则将符号名转换为小写
        if iflower:
            tb_symbol_name = tb_symbol_name.lower()

        return tb_symbol_name
    
    def Get_MIN_NOTIONAL(self,exchange_info:dict):
        """
            每個商品有自己的最小下單金額限制
            為了避免下單的波動設計了2倍的設計
        """
        out_dict ={}
        for symbol_info in exchange_info['symbols']:
            for filter in symbol_info['filters']:
                if filter['filterType'] == 'MIN_NOTIONAL':
                    out_dict.update({symbol_info['symbol']:float(filter['notional'])*2})
        
        return out_dict