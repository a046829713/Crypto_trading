import subprocess
import time
import os
from utils.Debug_tool import debug
import logging

process = subprocess.Popen(
    [r'C:\Users\user\Desktop\程式專區\TradingSysteam\Scripts\python', r'C:\Users\user\Desktop\程式專區\TradingSysteam\Crypto_trading\TradeUi_TC.py'])

while True:
    if process.poll() is None:
        pass
    else:
        debug.record_msg("System crashed, restart the program.",
                         log_level=logging.error)
        process = subprocess.Popen(
            [r'C:\Users\user\Desktop\程式專區\TradingSysteam\Scripts\python', r'C:\Users\user\Desktop\程式專區\TradingSysteam\Crypto_trading\TradeUi_TC.py', '--autostart'])

    time.sleep(10)
