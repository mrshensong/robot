import logging.handlers
import os

log_dict = os.getcwd() + '/log'
if not os.path.exists(log_dict):
    os.mkdir(log_dict)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers.clear()
formatter = logging.Formatter("{asctime} [{threadName}] {levelname} {filename},{lineno} {message}", style="{")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
file_handler = logging.handlers.TimedRotatingFileHandler("log/sys.log", "D", encoding="UTF-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



