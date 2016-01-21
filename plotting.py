import csv

import matplotlib.pyplot as plt
import numpy as np
import scipy as sci
from scipy import signal

import sensorprocessor as sp
import signalfilters as mf

csv_missed = '/Users/philliphartin/TAUT/SensorRecordings/1196/1196_1393385457_Accelerometer.csv'
csv_acknowledged = '/Users/philliphartin/TAUT/SensorRecordings/1196/1196_1393288203_Accelerometer.csv'


def import_sensorfile(filepath):
    with open(filepath) as csv_sensorfile:
        sensorfile = csv.reader(csv_sensorfile, delimiter=',', quotechar='|')
        sensor_rows = []

        for row in sensorfile:
            # the correct format has 4 elements (avoids header and footer rows)
            if len(row) == 4:
                try:
                    timestamp = int(row[0])
                    x = float(row[1])
                    y = float(row[2])
                    z = float(row[3])
                    sensor_rows.append([timestamp, x, y, z])
                except ValueError:
                    continue

        return sensor_rows


def process_input(data):
    t_series = []
    x_series = []
    y_series = []
    z_series = []
    mag_series = []

    for row in data:
        # Get t at index in row
        t = row[0]
        x = row[1]
        y = row[2]
        z = row[3]

        # Add to Series
        t_series.append(t)
        x_series.append(x)
        y_series.append(y)
        z_series.append(z)
        mag_series.append(sp.get_magnitude(x, y, z))

    numpymag = np.array(mag_series)

    return numpymag


def calibrate_median(data):
    medianvalue = np.median(data)
    return np.array([x - medianvalue for x in data])


def cut_data_in_half(data):
    length = len(data)
    midpoint = length/2
    startpoint = midpoint - 400
    return data[startpoint:midpoint]

def plot_against(missed, acknowledged):
    sensor_miss = import_sensorfile(missed)
    sensor_ack = import_sensorfile(acknowledged)

    mag_miss = cut_data_in_half(process_input(sensor_miss))
    mag_ack = cut_data_in_half(process_input(sensor_ack))
    mag_miss_filter = sci.signal.medfilt(mag_miss, 21)
    mag_ack_filter = sci.signal.medfilt(mag_ack, 21)

    # shift zero
    medianvalue = np.median(mag_miss)

    mag_miss_cal = calibrate_median(mag_miss)
    mag_ack_cal = calibrate_median(mag_ack)

    mag_miss_cal_filter = mf.medfilt(mag_miss_cal, 21)
    mag_ack_cal_filter = mf.medfilt(mag_ack_cal, 21)

    plt.plot(mag_miss_cal, 'b--')
    plt.plot(mag_ack_cal, 'r--')
    plt.plot(mag_miss_cal_filter, 'b', linewidth=3.3)
    plt.plot(mag_ack_cal_filter, 'r', linewidth=3.3)

    # plt.plot(mf.medfilt(numpymag, 15), 'r', linewidth=3.3)

    plt.show()


plot_against(csv_missed, csv_acknowledged)
