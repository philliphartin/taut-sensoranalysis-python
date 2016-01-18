import bisect
import csv

import numpy as np

sensors_triaxial = ('accelerometer', 'magnetic', 'gyroscope')
sensors_discrete = ('light', 'proximity', 'temp')


def rms(x, axis=None):
    return np.sqrt(np.mean(x ** 2, axis=axis))


def process_data(sensor_type, file_path, window_start_time, window_end_time):
    if sensor_type in sensors_triaxial:
        features = process_triaxial(file_path, window_start_time, window_end_time)
        return features
    elif sensor_type in sensors_discrete:
        features = process_discrete(file_path, window_start_time, window_end_time)
        return features


def calculate_window_indexes(timestamps, window_start_time, window_end_time):
    # find timestamp in array, find the row index, and record
    # original times are stored in seconds, scale up to milliseconds by *1000
    window_start_time_milli = float(window_start_time * 1000)
    window_end_time_milli = float(window_end_time * 1000)

    # use bisect sorting algorithm to returns an insertion point
    # which comes after (to the right of) any existing entries of window_time in timestamp_list.
    window_start_index = bisect.bisect(timestamps, window_start_time_milli)
    window_end_index = bisect.bisect(timestamps, window_end_time_milli)

    # TODO: For discrete time-series, if a reading exists before the start_index_use it
    return window_start_index, window_end_index


def produce_empty_stats_dictionary():
    # Empty stats for missing data
    values = {'mean': None,
              'med': None,
              'max': None,
              'min': None,
              'var': None,
              'std': None,
              'sum': None,
              'rng': None,
              'rms': None,
              'percentile_25': None,
              'percentile_75': None}
    return values


# default dictionary is empty dic
def produce_empty_triaxial_sensor_dict(dictionary={}):
    dictionary.update({'x': produce_empty_stats_dictionary(),
                       'y': produce_empty_stats_dictionary(),
                       'z': produce_empty_stats_dictionary(),
                       'xyz': produce_empty_stats_dictionary()})
    return dictionary


def produce_empty_discrete_sensor_dict(dictionary={}):
    dictionary.update({'measure': produce_empty_stats_dictionary()})
    return dictionary


def calc_stats_for_data_stream_as_dictionary(axis_data):
    # Stats
    data_mean = np.mean(axis_data)
    data_med = np.median(axis_data)
    data_max = np.max(axis_data)
    data_min = np.min(axis_data)
    data_var = np.var(axis_data)
    data_std = np.std(axis_data)
    data_sum = np.sum(axis_data)
    data_rng = (data_max - data_min)
    data_rms = rms(axis_data)
    data_percentile_25 = np.percentile(axis_data, 25)
    data_percentile_75 = np.percentile(axis_data, 75)

    values = {'mean': data_mean,
              'med': data_med,
              'max': data_max,
              'min': data_min,
              'var': data_var,
              'std': data_std,
              'sum': data_sum,
              'rng': data_rng,
              'rms': data_rms,
              'percentile_25': data_percentile_25,
              'percentile_75': data_percentile_75}

    # FFT Frequency
    # fourier = np.fft.fft(axis_data)
    # n = axis_data.size
    # timestep = 0.1
    # freq = np.fft.fftfreq(n, d=timestep)
    return values


def window_index_conditions_valid(start, end):
    # Return false if the start and end are both 0
    # or
    # if end window is before start
    if start < end:
        condition1 = True
    else:
        condition1 = False

    # Start and End must not be 0 (Empty range)
    if start != 0 and end != 0:
        condition2 = True
    else:
        condition2 = False
    return condition1 and condition2


def process_triaxial(file_path, window_start_time, window_end_time):
    with open(file_path) as csv_sensorfile:
        print('Opening: ' + file_path)

        # dictionary to hold features
        features = {}

        sensorfile = csv.reader(csv_sensorfile, delimiter=',', quotechar='|')
        sensor_rows = []

        for row in sensorfile:
            # the correct format has 4 elements (avoids header and footer rows)
            if len(row) == 4:
                # method only works for accelerometer and Magnetometer data
                timestamp = int(row[0])
                x = float(row[1])
                y = float(row[2])
                z = float(row[3])
                sensor_rows.append([timestamp, x, y, z])

        # if no data exists generate empty stats
        # otherwise calculate stats
        if not sensor_rows:
            features = produce_empty_triaxial_sensor_dict(features)
        else:
            # convert basic python lists to numPy arrays using slices
            sensor_rows = np.array(sensor_rows)
            # convert to list for sorting algorithm
            timestamps = sensor_rows[:, 0].tolist()

            # calculate window indexes
            window_indexes = calculate_window_indexes(timestamps, window_start_time, window_end_time)
            window_start_index = window_indexes[0]
            window_end_index = window_indexes[1]
            # validate window indexes
            window_indexes_valid = window_index_conditions_valid(window_start_index, window_end_index)

            # if valid, window the data, and calculate stats
            if window_indexes_valid:
                # make slices of data using indexes
                x_win = sensor_rows[window_start_index:window_end_index, 1]
                y_win = sensor_rows[window_start_index:window_end_index, 2]
                z_win = sensor_rows[window_start_index:window_end_index, 3]
                xyz_win = get_magnitude(x_win, y_win, z_win)

                # calculate stats
                stats_x = calc_stats_for_data_stream_as_dictionary(x_win)
                stats_y = calc_stats_for_data_stream_as_dictionary(y_win)
                stats_z = calc_stats_for_data_stream_as_dictionary(z_win)
                stats_xyz = calc_stats_for_data_stream_as_dictionary(xyz_win)

                features.update({'x': stats_x,
                                 'y': stats_y,
                                 'z': stats_z,
                                 'xyz': stats_xyz})
            else:
                features = produce_empty_triaxial_sensor_dict(features)

        return features


def process_discrete(file_path, window_start_time, window_end_time):
    with open(file_path) as csv_sensorfile:
        print('Opening: ' + file_path)

        sensorfile = csv.reader(csv_sensorfile, delimiter=',', quotechar='|')

        # dictionary to hold features
        features = {}

        sensor_rows = []
        for row in sensorfile:
            # the correct format has 4 elements (avoids header and footer rows)
            if len(row) == 4:
                timestamp = int(row[0])
                measure = float(row[1])
                sensor_rows.append([timestamp, measure])

        if not sensor_rows:
            features = produce_empty_discrete_sensor_dict(features)
        else:
            # convert basic python lists to numPy arrays using slices
            sensor_rows = np.array(sensor_rows)
            timestamps = sensor_rows[:, 0].tolist()  # convert to list for sorting algorithm

            # calculate window indexes
            window_indexes = calculate_window_indexes(timestamps, window_start_time, window_end_time)
            window_start_index = window_indexes[0]
            window_end_index = window_indexes[1]
            window_indexes_valid = window_index_conditions_valid(window_start_index, window_end_index)

            # if valid, window the data, and calculate stats
            if window_indexes_valid:
                # make slices of data using indexes
                measures_win = sensor_rows[window_start_index:window_end_index, 1]
                stats_reading = calc_stats_for_data_stream_as_dictionary(measures_win)
                features.update({'measure': stats_reading})
            else:
                features = produce_empty_discrete_sensor_dict(features)

        return features


def get_magnitude(x, y, z):
    # square values of each array
    x_sq = np.power(x, 2)
    y_sq = np.power(y, 2)
    z_sq = np.power(z, 2)

    # get the sum of squares
    xyz_sq = x_sq + y_sq + z_sq

    # find sqr root for magnitude
    xyz_mag = np.sqrt(xyz_sq)
    return xyz_mag
