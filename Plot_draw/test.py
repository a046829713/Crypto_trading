import numpy as np 
import matplotlib.pyplot as plt 
plt.style.use('seaborn-white') 
data = np.random.randn(1000) 
print(data)
plt.hist(data)

plt.show()