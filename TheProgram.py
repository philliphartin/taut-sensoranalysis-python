__author__ = 'philliphartin'

import pickle

import DataPrep
import SensorFileProcessor

root_folder = '/Users/philliphartin'
taut_folder = '/TAUT'
working_directory = root_folder + taut_folder
sensor_folder = '/SensorRecordings'
database_folder = '/ServerDatabase'
# csv_log_file = '/ServerDatabase_2015_11_28_cleaned.csv'
csv_log_file = '/example.csv'

window_size_seconds = 15  # change this value to adjust window size

prepped_data = DataPrep.fetch_data(working_directory, database_folder, sensor_folder, csv_log_file)

master_data_set = {}

for key_patient_id, value_data in prepped_data.items():

    master_data_user = []

    for reminders in value_data:

        # master_data_sensors = []
        master_data_sensors = {}

        for key_reminder, value_reminder in reminders.items():
            sensor_info = value_reminder['sensor_info']
            unixtime = value_reminder['unixtime']
            acknowledged = value_reminder['acknowledged']

            # Establish timestamps for windows
            window_end_time = int(unixtime)  # convert to int for analysis later
            window_start_time = window_end_time - window_size_seconds

            # Iterate through the list of sensors
            for sensorfile in sensor_info:
                file_path = sensorfile['filepath']
                sensor_type = sensorfile['type']

                # TODO: Create an array to hold the values passed back from the processing methods
                # Establish sensor_type and pass data to be processed
                if sensor_type in ('accelerometer', 'magnetic', 'gyroscope'):
                    features = SensorFileProcessor.process_timeseries(file_path, window_start_time, window_end_time)
                    # if there is a feature object, and it isn't empty
                    # write them to users_data
                    if features is not None and len(features) != 0:
                        master_data_sensors[sensor_type] = features

                elif sensor_type in ('proximity', 'light', 'temp', 'gps'):
                    features = SensorFileProcessor.process_discrete(file_path, window_start_time, window_end_time)

        # Save the reminder data and embed the recorded sensor data
        reminder_to_save = {'acknowledged': acknowledged, 'sensors': master_data_sensors}
        master_data_user.append(reminder_to_save)

    # Save all the data for the user and append to master data set list
    master_data_set[key_patient_id] = master_data_user

# Use pickle to save object to local disk for faster testing
pickle.dump(master_data_set, open("output/save.p", "wb"))

# TODO: Write results to a csv file.
# OutputWriter
