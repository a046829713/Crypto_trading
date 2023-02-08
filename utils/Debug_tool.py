import traceback
import logging


logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M', handlers=[logging.FileHandler('my.log', 'w', 'utf-8'), ])


class debug():
    @staticmethod
    def print_info(error_msg: str = None):
        traceback.print_exc()
        logging.error(f'{traceback.format_exc()}')
        if error_msg:
            print(error_msg)
            logging.error(f'{error_msg}')

    @staticmethod
    def record_msg(error_msg: str, log_level=logging.debug):
        print(error_msg)
        log_level(f'{error_msg}')

    @staticmethod
    def record_type(func):
        def wrapper(*args, **kwargs):
            print(args)
            result = func(*args, **kwargs)
            print(type(result))
            return result
        return wrapper
