import pickle

import dataprepper
import outputgenerator
import sensorprocessor

root_folder = '/Users/philliphartin'
taut_folder = '/TAUT'
working_directory = root_folder + taut_folder
sensor_folder = '/SensorRecordings'
database_folder = '/ServerDatabase'
csv_log_file = '/ServerDatabase_2015_11_28_cleaned.csv'

windowlengths = [30, 20, 15]  # Window lengths in seconds to test


def find_key(input_dict, value):
    return {k for k, v in input_dict.items() if v == value}


prepped_data = dataprepper.fetch_data(working_directory, database_folder, sensor_folder, csv_log_file)
master_data = {}

# For each window length, produce the data
for windowlength in windowlengths:
    print('Processing data for window length: ' + str(windowlength))
    all_users_data = {}

    processed_count = 0
    for key_patient_id, value_data in prepped_data.items():
        processed_count += 1

        print(
                str(processed_count) + '/' + str(len(prepped_data)) + ' - Processing data for user ' + str(
                        key_patient_id))

        user_data = []

        for reminders in value_data:

            master_data_sensors = {}

            for key_reminder, value_reminder in reminders.items():
                sensor_info = value_reminder['sensor_info']
                unixtime = value_reminder['unixtime']
                acknowledged = value_reminder['acknowledged']

                # Establish timestamps for windows
                window_end_time = int(unixtime)  # convert to int for analysis later
                window_start_time = window_end_time - windowlength

                # Iterate through the list of sensors
                sensors_processed = {'accelerometer': False, 'magnetic': False,
                                     'light': False, 'proximity': False}

                for sensorfile in sensor_info:
                    file_path = sensorfile['filepath']
                    sensor_type = sensorfile['type']
                    features = sensorprocessor.process_data(sensor_type, file_path, window_start_time, window_end_time)
                    master_data_sensors[sensor_type] = features
                    sensors_processed[sensor_type] = True

                # Create list of missing sensor types
                missing_sensor_types = find_key(sensors_processed, False)

                # Generate fake data for any missing sensors processed.
                if missing_sensor_types:
                    #  TODO: IF ALL MISSING, SKIP ENTIRE THING
                    if len(sensors_processed) == len(missing_sensor_types):
                        continue

                    for missing_sensor in missing_sensor_types:
                        # establish missing file type (triaxial or discrete?)
                        # create fake data depending on sensor type and save
                        if missing_sensor in sensorprocessor.sensors_discrete:
                            fake_data = sensorprocessor.produce_empty_discrete_sensor_dict()
                            master_data_sensors[missing_sensor] = fake_data

                        elif missing_sensor in sensorprocessor.sensors_triaxial:
                            fake_data = sensorprocessor.produce_empty_triaxial_sensor_dict()
                            master_data_sensors[missing_sensor] = fake_data

            # If data exists, save the reminder data and embed the recorded sensor data
            if master_data_sensors:
                reminder_to_save = {'acknowledged': acknowledged, 'unixtime': unixtime, 'sensors': master_data_sensors}
                user_data.append(reminder_to_save)

            # Save all the data for the user and append to master data set list
            all_users_data[key_patient_id] = user_data

    master_data[windowlength] = all_users_data

# Use pickle to save object to local disk for faster testing
pickle.dump(master_data, open('pickle.p', "wb"))

# master_data = pickle.load(open('pickle.p', "rb"))

for window, data in master_data.items():
    # Write results to a csv file.
    results = outputgenerator.prepare_data(data)
    outputgenerator.write_data_to_disk(results, window)
