import pandas as pd
from utils.Date_time import parser_time
import time


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

    def calculation_size(self, systeam_size: dict, true_size: dict) -> dict:
        """
        用來比較 系統部位 和 Binance 交易所的實際部位

        Args:
            systeam_size (dict): example :{'BTCUSDT-15K-OB': [1.0, 0.37385995823410634], 'ETHUSDT-15K-OB': [1.0, 5.13707471134965],'BTCUSDT-30K-OB': [1.0, 0.995823410634], 'ETHUSDT-17K-OB': [1.0, 2.13707471134965]}
            true_size (dict): example :{'ETHUSDT': '10.980', 'BTCUSDT': '0.420'} 

        Returns:
            dict: {'BTCUSDT': 0.9496833688681066, 'ETHUSDT': -3.7058505773006996}


            當計算出來的結果 + 就是要買 - 就是要賣

        """
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
        df = pd.DataFrame.from_dict(socketdata[symbol_name], orient='index')
        df.reset_index(drop=True, inplace=True)
        df['Datetime'] = pd.to_datetime(df['Datetime'])

        # lastdata
        lastdata.reset_index(inplace=True)
        new_df = pd.concat([lastdata, df])

        new_df.set_index('Datetime', inplace=True)
        # duplicated >> 重複 True 代表重複了 # 過濾相同資料
        new_df = new_df[~new_df.index.duplicated(keep='last')]
        new_df = new_df.astype(float)

        return new_df, df
