import csv

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sci
import seaborn as sns

import sensorprocessor as sp
import signalfilters as mf

csv_missed = '/Users/philliphartin/TAUT/SensorRecordings/3802/6/3802_1409230847_Accelerometer.csv'
csv_acknowledged = '/Users/philliphartin/TAUT/SensorRecordings/3802/6/3802_1403040715_Accelerometer.csv'


def calculate_percentagedifference(v1, v2):
    import math

    percentage_diff = abs((abs(v1) - abs(v2)) / ((v1 + v2) / 2) * 100)

    if math.isnan(percentage_diff):
        return 0
    else:
        return percentage_diff


def calculate_difference(original, comparison):
    # Create a list of the difference in values between two dicts
    percentage_change = {}
    percentage_difference = {}

    for key, value in original.items():
        value_orig = value
        value_comp = comparison[key]
        # percentrage_change[key] = abs(value_orig - value_comp)
        percentage_change[key] = calculate_percentagechange(value_orig, value_comp)
        percentage_difference[key] = calculate_percentagedifference(value_orig, value_comp)

    return percentage_difference


def calculate_percentagechange(old_value, new_value, multiply=True):
    change = new_value - old_value

    try:
        percentage_change = (change / float(old_value))
        if multiply:
            percentage_change = percentage_change * 100
        return percentage_change
    except ZeroDivisionError as e:
        print(e)
        return None


def calcualate_meanfordictionary(data):
    values = []
    for key, value in data.items():
        values.append(value)

    return np.mean(values)


def make_ticklabels_invisible(fig):
    for i, ax in enumerate(fig.axes):
        ax.text(0.5, 0.5, "ax%d" % (i + 1), va="center", ha="center")
        for tl in ax.get_xticklabels() + ax.get_yticklabels():
            tl.set_visible(False)


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


def window_data(data):
    length = len(data)
    # first 2/3rds of recording
    endpoint = length / 10
    endpoint *= 7
    startpoint = endpoint - 100
    return data[startpoint:endpoint]


def write_to_csv(data, filename):
    import csv

    # Get headers from dictionary
    header = []
    example = data[0]
    for key, value in example.items():
        header.append(key)

    with open(str(filename) + '.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(header))

        writer.writeheader()

        for item in data:
            writer.writerow(item)


def plot_against(missed, acknowledged):
    sensor_miss = import_sensorfile(missed)
    sensor_ack = import_sensorfile(acknowledged)

    # Window data
    mag_miss = window_data(process_input(sensor_miss))
    mag_ack = window_data(process_input(sensor_ack))

    # Filter setup
    kernel = 15

    # apply filter
    mag_miss_filter = sci.medfilt(mag_miss, kernel)
    mag_ack_filter = sci.medfilt(mag_ack, kernel)

    # calibrate data
    mag_miss_cal = mf.calibrate_median(mag_miss)
    mag_miss_cal_filter = mf.calibrate_median(mag_miss_filter)

    mag_ack_cal = mf.calibrate_median(mag_ack)
    mag_ack_cal_filter = mf.calibrate_median(mag_ack_filter)

    # PLOT
    ylimit_top = [-5, 10]
    ylimits_filtered = [-4, 4]
    ylimits_filtered_bottom = [-1.5, 1.5]

    sns.set_style("darkgrid")
    current_palette = sns.color_palette('muted')
    sns.set_palette(current_palette)

    plt.figure(0)
    # Plot RAW missed and acknowledged reminders
    ax1 = plt.subplot2grid((4, 2), (0, 0), colspan=2)
    plt.ylim(ylimit_top)
    raw_miss = plt.plot(mag_miss_cal, label='Missed  (Unfiltered)')
    raw_ack = plt.plot(mag_ack_cal, label='Acknowledged (Unfiltered)')
    plt.legend(loc='upper left')

    ax2 = plt.subplot2grid((4, 2), (1, 0))
    # Plot Missed Reminder RAW
    plt.ylim(ylimits_filtered)
    plt.plot(mag_miss_cal, linestyle='-', label='Unfiltered')
    plt.legend(loc='lower left')

    ax3 = plt.subplot2grid((4, 2), (1, 1))
    # Plot Acknow Reminder RAW
    plt.ylim(ylimits_filtered)
    plt.plot(mag_ack_cal, linestyle='-', label='Unfiltered')
    plt.legend(loc='lower left')

    ax4 = plt.subplot2grid((4, 2), (2, 0))
    # Plot Missed Reminder Filter
    plt.ylim(ylimits_filtered)
    plt.plot(mag_miss_cal, linestyle=':', label='Unfiltered')
    plt.plot(mag_miss_cal_filter, linestyle='-', label='Median Filter (k=' + str(kernel) + ')')
    plt.legend(loc='lower left')

    ax5 = plt.subplot2grid((4, 2), (2, 1))
    # Plot Acknow Reminder Filter
    plt.ylim(ylimits_filtered)
    plt.plot(mag_ack_cal, linestyle=':', label='Unfiltered')
    plt.plot(mag_ack_cal_filter, linestyle='-', label='Median Filter (k=' + str(kernel) + ')')
    plt.legend(loc='lower left')

    ax6 = plt.subplot2grid((4, 2), (3, 0), colspan=2)
    plt.ylim(ylimits_filtered_bottom)
    plt.style.use('grayscale')
    plt.plot(mag_miss_cal_filter, label='Missed (Filtered)')
    plt.plot(mag_ack_cal_filter, label='Acknowledged (Filtered)')
    plt.legend(loc='lower left')
    plt.suptitle("Applying Filters to Signals")
    plt.show()


def plot_singlewave(file):
    sensor = import_sensorfile(file)
    sensor_processed = process_input(sensor)
    timestamps = []
    [timestamps.append(str(item[0])) for item in sensor]

    sensor_processed_calibrated = mf.calibrate_median(sensor_processed)
    sensor_filtered = mf.medfilt(sensor_processed_calibrated, 3)

    plt.plot(sensor_filtered, linewidth='0.8')
    plt.xlim([0, 12000])
    plt.ylim([-5, 5])
    plt.ylabel('Acceleration (g)')
    plt.xlabel('Time (ms)')
    # plt.xticks(sensor_filtered, timestamps, rotation='vertical')
    plt.show()


def plot_example(missed, acknowledged):
    sensor_miss = import_sensorfile(missed)
    sensor_ack = import_sensorfile(acknowledged)

    # Window data
    mag_miss = window_data(process_input(sensor_miss))
    mag_ack = window_data(process_input(sensor_ack))

    # Window data
    mag_miss = window_data(process_input(sensor_miss))
    mag_ack = window_data(process_input(sensor_ack))

    # Filter setup
    kernel = 15

    # apply filter
    mag_miss_filter = sci.medfilt(mag_miss, kernel)
    mag_ack_filter = sci.medfilt(mag_ack, kernel)

    # calibrate data
    mag_miss_cal = mf.calibrate_median(mag_miss)
    mag_miss_cal_filter = mf.calibrate_median(mag_miss_filter)

    mag_ack_cal = mf.calibrate_median(mag_ack)
    mag_ack_cal_filter = mf.calibrate_median(mag_ack_filter)

    # PLOT
    sns.set_style("white")
    current_palette = sns.color_palette('muted')
    sns.set_palette(current_palette)

    plt.figure(0)

    # Plot RAW missed and acknowledged reminders
    ax1 = plt.subplot2grid((2, 1), (0, 0))
    plt.ylim([-1.5, 1.5])
    plt.ylabel('Acceleration (g)')
    plt.plot(mag_miss_cal, label='Recording 1')
    plt.legend(loc='lower left')

    ax2 = plt.subplot2grid((2, 1), (1, 0))
    # Plot Missed Reminder RAW
    plt.ylim([-1.5, 1.5])
    plt.ylabel('Acceleration (g)')
    plt.xlabel('t (ms)')
    plt.plot(mag_ack_cal, linestyle='-', label='Recording 2')
    plt.legend(loc='lower left')

    # CALC AND SAVE STATS
    stats_one = sp.calc_stats_for_data_stream_as_dictionary(mag_miss_cal)
    stats_two = sp.calc_stats_for_data_stream_as_dictionary(mag_ack_cal)

    data = [stats_one, stats_two]
    write_to_csv(data, 'example_waves')

    plt.show()


def plot_kernal_length_experiment(missed, acknowledged):
    sensor_miss = import_sensorfile(missed)
    sensor_ack = import_sensorfile(acknowledged)

    # Window data
    mag_miss = window_data(process_input(sensor_miss))
    mag_ack = window_data(process_input(sensor_ack))

    # Filter setup

    difference = []
    stats_output = []
    for num in range(3, 63):
        # check if odd
        if num % 2 != 0:
            kernel = num

            # apply filter
            mag_miss_filter = sci.medfilt(mag_miss, kernel)
            mag_ack_filter = sci.medfilt(mag_ack, kernel)

            # calibrate data
            mag_miss_cal = mf.calibrate_median(mag_miss)
            mag_miss_cal_filter = mf.calibrate_median(mag_miss_filter)

            mag_ack_cal = mf.calibrate_median(mag_ack)
            mag_ack_cal_filter = mf.calibrate_median(mag_ack_filter)

            # STATS
            # Calculate the stats for raw and windowed for each
            stats_miss = sp.calc_stats_for_data_stream_as_dictionary(mag_miss_cal)
            stats_miss_filter = sp.calc_stats_for_data_stream_as_dictionary(mag_miss_cal_filter)

            stats_ack = sp.calc_stats_for_data_stream_as_dictionary(mag_ack_cal)
            stats_ack_filter = sp.calc_stats_for_data_stream_as_dictionary(mag_ack_cal_filter)
            stats_data = [stats_miss, stats_miss_filter, stats_ack, stats_ack_filter]

            [data.pop("med", None) for data in stats_data]

            print('Stats Missed:' + str(stats_miss))
            print('Stats Acknowledged: ' + str(stats_ack))
            print('Stats Missed Filtered: ' + str(stats_miss_filter))
            print('Stats Acknowledged Filtered:' + str(stats_ack_filter))

            # Calculate the percentage difference between the values
            dif_stats_raw = calculate_difference(stats_miss, stats_ack)
            dif_stats_filtered = calculate_difference(stats_miss_filter, stats_ack_filter)

            print('Difference in RAW as percentage:' + str(dif_stats_raw))
            print('Difference in FILTERED as percentage:' + str(dif_stats_filtered))

            dif_stats_raw_overall = calcualate_meanfordictionary(dif_stats_raw)
            dif_stats_filtered_overall = calcualate_meanfordictionary(dif_stats_filtered)

            print('Avg. Difference RAW:  ' + str(dif_stats_raw_overall))
            print('Avg. Difference Filtered:  ' + str(dif_stats_filtered_overall))

            difference.append((kernel, dif_stats_filtered_overall))

            if kernel == 15:
                stats_output.append(stats_miss)
                stats_output.append(stats_ack)
                stats_output.append(stats_miss_filter)
                stats_output.append(stats_ack_filter)
                stats_output.append(dif_stats_raw)
                stats_output.append(dif_stats_filtered)
                write_to_csv(stats_output)

    x_val = [x[0] for x in difference]
    y_val = [x[1] for x in difference]
    xticks = [str(x) for x in x_val]

    base_val = [54] * 63

    plt.xticks(x_val, xticks)
    plt.xlabel('Window Length (k)')
    plt.ylabel('Percentage Difference (%)')
    plt.ylim([40, 140])
    plt.plot(x_val, y_val, label='Median Filter')

    plt.plot(base_val, linestyle='--', label='Baseline (Unfiltered)')
    plt.legend(loc='lower right')

    plt.show()


# plot_against(csv_missed, csv_acknowledged)
# plot_kernal_length_experiment(csv_missed, csv_acknowledged)
# plot_example(csv_missed, csv_acknowledged)
# plot_singlewave(csv_acknowledged)
