import os
import glob
import time
import datetime
import logging
from logging import StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler
import sqlite3

def get_logger(logger_name):
    _logger = logging.getLogger(logger_name)

    file_formatter = Formatter(
        '%(levelname)s | %(asctime)s | %(name)s | %(message)s | %(pathname)s:%(lineno)d'
    )
    time_rotating_handler = TimedRotatingFileHandler(\
            '{0}/{1}.log'.format('./tmp', logger_name), when="midnight", backupCount=10, encoding='utf-8')
    time_rotating_handler.suffix = "%Y-%m-%d"
    time_rotating_handler.setFormatter(file_formatter)

    echo_formatter = Formatter('[%(levelname)s][%(name)s][in %(filename)s:%(lineno)d] %(message)s')
    stream_handler = StreamHandler(stream=os.sys.stdout)
    stream_handler.setFormatter(echo_formatter)

    _logger.addHandler(time_rotating_handler)
    _logger.addHandler(stream_handler)
    _logger.setLevel(logging.DEBUG)

    return _logger

def init_db():
    logging.info('Initializing DB...')
    conn = sqlite3.connect('thermostat.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS temperatures
                (date text NOT NULL, temperature real NOT NULL)''')
    conn.execute(
        '''CREATE INDEX IF NOT EXISTS date_index ON temperatures(date)''')
    logging.info('DB initialized')
    conn.commit()
    return conn

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
    return temp_c

logger = get_logger('thermostat')

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

try:
    conn = init_db()
    while True:
        current_time = datetime.datetime.now().strftime('%Y%m%dT%H:%M')
        current_temp = read_temp()
        logger.debug('Read temperature %s° at time %s',
                      current_temp, current_time)
        conn.execute('INSERT INTO temperatures VALUES (?, ?)',
                     (current_time, current_temp))
        conn.commit()
        time.sleep(3)
except KeyboardInterrupt:
    logger.warn('Temperature daemon stopped by user')
finally:
    conn.close()