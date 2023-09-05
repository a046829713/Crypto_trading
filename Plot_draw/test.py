import matplotlib.pyplot as plt
import numpy as np

# 創建一個簡單的折線圖
x = np.linspace(0, 10, 100)
y = np.sin(x)
fig, ax = plt.subplots()
line, = ax.plot(x, y)



def on_move(event):
    # 如果事件不在這個Axes中，則直接返回
    if event.inaxes != ax:
        return

   

# 連接事件處理函數
fig.canvas.mpl_connect('motion_notify_event', on_move)

plt.show()
