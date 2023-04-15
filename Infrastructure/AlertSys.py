
"""
    用來產生監控的exe
    用來單獨監控系統是否有正常運作

"""
import time
from datetime import datetime
from .LINE_Alert import LINE_Alert
from Database.SQL_operate import DB_operate

def check_sysLive():
    """
        檢察系統是否有正常運作
    """
    while True:
        data = DB_operate().get_db_data('select *  from `sysstatus`;')
        print(data)
        difftime = datetime.now() - datetime.strptime(data[0][1], "%Y-%m-%d %H:%M:%S.%f")
        print(difftime)
        if difftime.seconds > 600:
            LINE_Alert().req_line_alert("緊急通知>>程式已經停止運作!!!!!")

        time.sleep(60)



