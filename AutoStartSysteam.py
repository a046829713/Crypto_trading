import subprocess
import time
import os
from utils.Debug_tool import debug
import logging

python_path = r'C:\Users\user\Desktop\程式專區\TradingSysteam\Scripts\python'
sys_path = r'C:\Users\user\Desktop\程式專區\TradingSysteam\Crypto_trading\TradeUi_TC.py'

process = subprocess.Popen(
    [python_path, sys_path])

while True:
    if process.poll() is None:
        pass
    else:
        debug.record_msg("System crashed, restart the program.",
                         log_level=logging.error)
        process = subprocess.Popen(
            [python_path, sys_path, '--autostart'])

    time.sleep(30)
