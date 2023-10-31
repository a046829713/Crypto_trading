import os


for file in os.listdir('backup'):
    if 'usdt' not in file:
        continue

    if '-f' not in file:
        delfilepath = os.path.join('backup', file)
        os.remove(delfilepath)
