import traceback
import logging
import datetime
import os



LOG_DIR = "LogRecord"
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
    

today = datetime.date.today().strftime('%Y%m%d')
log_file = os.path.join(LOG_DIR, f"{today}.log")
handler = logging.FileHandler(log_file)

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M', handlers=[handler, ])



class debug():
    @staticmethod
    def print_info(error_msg: str = None):
        traceback.print_exc()
        logging.error(f'{traceback.format_exc()}')
        if error_msg:
            logging.error(f'{error_msg}')

    @staticmethod
    def record_msg(error_msg: str, log_level=logging.debug):
        print(error_msg)
        log_level(f'{error_msg}')

    @staticmethod
    def record_args_return_type(func):
        def wrapper(*args, **kwargs):
            arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
            for i, arg in enumerate(args):
                print(f"{arg_names[i]}: {arg}")
            for k, v in kwargs.items():
                print(f"{k}: {v}")
            result = func(*args, **kwargs)
            print(f"Result Type: {type(result)}")
            return result
        return wrapper




