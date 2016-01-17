__author__ = 'philliphartin'

import DataPrep
import SensorFileProcessor

root_folder = '/Users/philliphartin'
taut_folder = '/TAUT'
working_directory = root_folder + taut_folder
sensor_folder = '/SensorRecordings'
database_folder = '/ServerDatabase'
csv_log_file = '/ServerDatabase_2015_11_28_cleaned.csv'

window_size_seconds = 15  # change this value to adjust window size

prepped_data = DataPrep.fetch_data(working_directory, database_folder, sensor_folder, csv_log_file)

for key_patient_id, value_data in prepped_data.items():
    for reminders in value_data:
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
                print(sensor_type)
                if sensor_type in ('accelerometer', 'magnetic', 'gyroscope'):
                    SensorFileProcessor.process_timeseries(file_path, window_start_time, window_end_time)
                elif sensor_type in ('proximity', 'light', 'temp', 'gps'):
                    SensorFileProcessor.process_discrete(file_path, window_start_time, window_end_time)

            # TODO: Write results to a csv file.
            # One for each user and one master file.
