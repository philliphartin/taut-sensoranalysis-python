import csv
import os

import FileChecker

# manual user list
id_list = ['1196']


# Get list of users from sensor directory folder names
# id_list = next(os.walk(working_directory+sensor_folder))[1]

def fetch_data(working_directory, database_folder, sensor_folder, csv_log_file):
    # Read in csv file
    # create dictionary using the first row as keys
    # write dictionary to new variable - reminders, so that CSV file handler can be closed.
    with open(working_directory + database_folder + csv_log_file) as csvfile:
        csv_reminders = csv.DictReader(csvfile)
        acknowledgement_list = list(csv_reminders)

    # dictionary to hold all reminder details for each user name
    data_all = {}

    # for each user in user array, get the their reminders, save as a list of dictionaires containing details.
    for idx, user_id in enumerate(id_list):
        # for user_id in id_list:

        print(str(idx + 1) + '/' + str(len(id_list)) + ' - Prepping data for user ' + str(user_id))
        reminders = list()  # blank list to hold row indexes

        # for each row in acknowledgement_list
        # find if user id matches row
        # if match, record details to a reminder object
        # save reminder object details
        for row in acknowledgement_list:
            if user_id == row['patient_id']:

                # TODO: Check for sensor files the the sensor file checking here before dictionary is set
                row_id = row['row_id']
                unixtime = row['unixtime_standardised']
                acknowledged = row['acknowledged']
                sensors = list()

                # if a unixtime exists, search for files
                if unixtime:
                    for root, dirs, files in os.walk(working_directory + sensor_folder):

                        for file in files:
                            if file.__contains__(unixtime):

                                # Get Sensor Type
                                sensor_type = FileChecker.what_is_sensor_type(file)
                                # Get absolute file path
                                file_path = (os.path.abspath(os.path.join(root, file)))

                                sensor_info = {'type': sensor_type, 'filepath': file_path}
                                sensors.append(sensor_info)

                reminder_details = {'row_id': row_id, 'unixtime': unixtime, 'acknowledged': acknowledged,
                                    'sensor_info': sensors}

                reminder = {'reminder': reminder_details}
                # increment count and save details to reminder object
                reminders.append(reminder)
                data_all[user_id] = reminders

    return data_all
