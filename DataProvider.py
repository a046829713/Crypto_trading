# 需要添加 tqdm 進度條
# 需要所有商品的目錄


import Data
from Database import SQL_operate
import pandas as pd


def main(symbol_name='BTCUSDT'):
    # 先檢查是否有相關資料
    # 取得目前所有列
    symbol_list = SQL.get_db_data('show tables;')
    symbol_list = [y[0] for y in symbol_list]

    if symbol_name + '-F' in symbol_list:
        print(f'{symbol_name}-已經有存在的資料')
        df = SQL.read_Dateframe(f"{symbol_name}-F")
        df['Datetime'] = df['Datetime'].astype(str)
    else:
        print('創建資料')
        SQL.change_db_data(
            f"""
            CREATE TABLE `crypto_data`.`{symbol_name}-F`(
            `Datetime` DATETIME NOT NULL,
            `Open` FLOAT NOT NULL,
            `High` FLOAT NOT NULL,
            `Low` FLOAT NOT NULL,
            `Close` FLOAT NOT NULL,
            `Volume` FLOAT NOT NULL,
            `close_time` FLOAT NOT NULL,
            `quote_av` FLOAT NOT NULL,
            `trades` FLOAT NOT NULL,
            `tb_base_av` FLOAT NOT NULL,
            `tb_quote_av` FLOAT NOT NULL,
            `ignore` FLOAT NOT NULL,
            PRIMARY KEY(`Datetime`)
            );"""
        )

        df = pd.DataFrame()

    new_df = Data.custom.BinanceDate.download(df, f"{symbol_name}", '4h')
    SQL.write_Dateframe(new_df, f"{symbol_name}-F")
    print(f"{symbol_name}寫入完成")
    print('*'*120)


if __name__ == "__main__":
    app = Data.custom.Binance_server()
    SQL = SQL_operate.DB_operate()
    for symbol_name in app.get_targetsymobls():
        main(symbol_name)
