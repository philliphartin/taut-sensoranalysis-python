import csv

import matplotlib.pyplot as plt
import numpy as np

import sensorprocessor as sp
import signalfilters as mf

sensorfile = '/Users/philliphartin/TAUT/SensorRecordings/577/6/577_1396047090_Accelerometer.csv'


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


def plot_timeseries(data):
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

    # mag_fft = np.fft.fft(mag_series)

    numpymag = np.array(mag_series)

    filtered = mf.medfilt(numpymag, 11)

    plt.plot(mag_series,)
    # plt.plot(mf.medfilt(numpymag, 11), 'b')
    plt.plot(mf.medfilt(numpymag, 15), 'r', linewidth=3.3)

    plt.show()

    # print(mag_fft)
    # print(sma)
    # print(sma_adv)
    # print(abs_sma)
    # print(abs_sma_adv)

    # plt.plot(mag_fft)
    # plt.plot(t_series, mag_series)
    # # plt.plot(t_series, x_series)
    # # plt.plot(t_series, y_series)
    # # plt.plot(t_series, z_series)
    #
    # plt.xlabel('time (ms)')
    # plt.ylabel('Acceleration (m/s)')
    # plt.title('About as simple as it gets, folks')
    # plt.grid(True)
    # plt.savefig("test.png")
    # plt.show()

plot_timeseries(import_sensorfile(sensorfile))
