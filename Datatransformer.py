import pandas as pd
from utils.Date_time import parser_time


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
        new_df['Open'] = df['Open'].resample(rule=f'{freq}min', label="left").first()
        new_df['High'] = df['High'].resample(rule=f'{freq}min', label="left").max()
        new_df['Low'] = df['Low'].resample(rule=f'{freq}min', label="left").min()
        new_df['Close'] = df['Close'].resample(rule=f'{freq}min', label="left").last()
        new_df['Volume'] = df['Volume'].resample(rule=f'{freq}min', label="left").sum()
        return new_df


    def drop_colunms(self, df: pd.DataFrame):
        """
            拋棄不要的Data

        """

        for key in df.columns:
            if key not in ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']:
                df = df.drop(columns=[key])

        return df
