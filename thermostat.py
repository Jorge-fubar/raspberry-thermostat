import os
import glob
import time
import datetime
import logging
import sqlite3


logging.basicConfig(level=logging.DEBUG, filename='thermostat.log',
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


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


try:
    conn = init_db()
    while True:
        current_time = datetime.datetime.now().strftime('%Y%m%dT%H:%M')
        current_temp = read_temp()
        logging.debug('Read temperature %s° at time %s',
                      current_temp, current_time)
        conn.execute('INSERT INTO temperatures VALUES (?, ?)',
                     (current_time, current_temp))
        conn.commit()
        time.sleep(3)
except KeyboardInterrupt:
    conn.close()
    logging.warn('Temperature daemon stopped by user (Ctrl+C command sent)')
