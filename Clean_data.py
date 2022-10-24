import pandas as pd


class Clean_data:
    """
        to transformer data


    """

    @staticmethod
    def drop_colunms(df: pd.DataFrame):
        """
            拋棄不要的Data

        """

        for key in df.columns:
            if key not in ['open', 'high', 'low', 'close']:
                df = df.drop(columns=[key])
                
        return df
