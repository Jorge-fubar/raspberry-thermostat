#!/usr/bin/env python3

import config

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
    #TODO the path for the logs file needs to be absolute when the script is executed on startup when registered in the /etc/rc.local file
    time_rotating_handler = TimedRotatingFileHandler(\
            '{0}/{1}.log'.format('./logs', logger_name), when="midnight", backupCount=10, encoding='utf-8')
    time_rotating_handler.suffix = "%Y-%m-%d"
    time_rotating_handler.setFormatter(file_formatter)

    _logger.addHandler(time_rotating_handler)
    _logger.setLevel(logging.DEBUG)

    return _logger

def init_db():
    #TODO the path for the db file needs to be absolute
    conn = sqlite3.connect('thermostat.db')
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

def get_time_range(datetime : datetime.datetime):
    time_range = datetime.hour * 2
    if (datetime.minute <= 30):
        time_range += 1
    return time_range

logger = get_logger('thermostat')

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

try:
    conn = init_db()
    while True:
        now = datetime.datetime.now()
        current_time = now.strftime('%Y%m%dT%H:%M')
        current_temp = read_temp()
        logger.debug('Read temperature %s° at time %s',
                      current_temp, current_time)
        conn.execute('INSERT INTO temperatures VALUES (?, ?)',
                     (current_time, current_temp))
        conn.commit()
        for row in conn.execute('SELECT temperature FROM week_schedule WHERE day = ? AND time_range = ?', (0, get_time_range(now))):
            print(row[0])
        time.sleep(60)
except KeyboardInterrupt:
    logger.warn('Temperature daemon stopped by user')
finally:
    conn.close()