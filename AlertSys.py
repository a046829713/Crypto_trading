

"""
    用來產生監控的exe
    用來單獨監控系統是否有正常運作

"""
from datetime import datetime
from LINE_Alert import LINE_Alert
import time

while True:
    with open(r"Sysstatus.txt", 'r') as file:
        data = file.read()
        difftime = datetime.now() - datetime.strptime(data, "%Y-%m-%d %H:%M:%S.%f")
        if difftime.seconds > 600:
            LINE_Alert().req_line_alert("緊急通知>>程式已經停止運作!!!!!")

    time.sleep(60)
