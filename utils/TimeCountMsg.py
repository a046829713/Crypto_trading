from time import time


class TimeCountMsg():
    @staticmethod
    def record_timemsg(func):
        def wrapper(*args, **kwargs):

            begin_time = time()
            result = func(*args, **kwargs)
            end_time = time()
            print("函數名稱:", func)
            print("使用時間:", end_time-begin_time)
            return result

        return wrapper


    _count_map = {}

    @staticmethod
    def record_time_add(func):
        def wrapper(*args, **kwargs):  
            begin_time = time()
            result = func(*args, **kwargs)  
            end_time = time()            
            elapsed_time = end_time - begin_time
            countMap = TimeCountMsg._count_map 
            
            if func.__name__ in countMap:
                countMap[func.__name__] += elapsed_time
            else:
                countMap[func.__name__] = elapsed_time
            
            return result

        return wrapper
