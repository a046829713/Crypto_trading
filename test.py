# from datetime import datetime
# import time
# import random


# def dosomething():
#     print("執行程序")
#     time.sleep(random.randint(5, 10))

# last_min = datetime.now().minute
# while True:

#     # 取得前一分鐘
#     print(datetime.now().minute)

#     if datetime.now().minute != last_min:
#         dosomething()
#         last_min = datetime.now().minute
#     else:
#         time.sleep(1)
#     # if ( - last_time).total_seconds()>60:
#     #     print("更新時間")
#     #     last_time = datetime.now()

import pandas as pd


movies = pd.read_csv("BTCUSDT-F-2-Min.csv")


print(movies)
def shorten(col:str):
    """  
        Datetime
        Open
        High
        Low
        Close
        Volume
    """
    print(col)
    print(col.replace("Datetime", "DT").replace("Volume", "VL"))
    return (col.replace("Datetime", "DT").replace("Volume", "VL"))


movies = movies.rename(columns=shorten)
movies.isna().head()

