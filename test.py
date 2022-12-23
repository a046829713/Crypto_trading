a = {'highest_n1': 10, 'lowest_n2': 10, 'ATR_short1': 10, 'ATR_long2': 10}

name_str = ''
for par,num in a.items():
    name_str = name_str + par + str(num)
    
    
print(name_str)