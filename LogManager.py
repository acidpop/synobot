
import sys
import logging
import logging.handlers
import BotConfig

cfg = BotConfig.BotConfig().instance()

LOGGER_NAME = 'synobot'

LOG_NAME = 'synobot.log'
LOG_SIZE = cfg.GetLogSize() * 1024 * 1024 # 50MB
LOG_COUNT = cfg.GetLogCount()

log = logging.getLogger(LOGGER_NAME)
log.setLevel(logging.DEBUG)


log_handler = logging.handlers.RotatingFileHandler(LOG_NAME, maxBytes=LOG_SIZE, backupCount=LOG_COUNT)
log.addHandler(log_handler)

if cfg.GetLogPrint() == True:
    log.addHandler( logging.StreamHandler(sys.stdout))

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

log_handler.setFormatter(formatter)

