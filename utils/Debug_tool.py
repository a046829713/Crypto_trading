import traceback
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M', handlers=[logging.FileHandler('my.log', 'w', 'utf-8'), ])

class debug():
    @staticmethod
    def print_info(error_msg: str = None):
        traceback.print_exc()
        logging.debug(f'{traceback.format_exc()}')
        if error_msg:
            print(error_msg)
            logging.debug(f'{error_msg}')
            

    @staticmethod
    def record_msg(error_msg: str, log_level=logging.debug):
        log_level(f'{error_msg}')