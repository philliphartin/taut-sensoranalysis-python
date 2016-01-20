import csv
import pickle
import time
from collections import OrderedDict

from arff import arff

# Folder Structure
pickle_data = 'save.p'


def get_timestamp():
    timestr = time.strftime("%Y%m%d-%H%M")
    return timestr


def create_time_folder():
    import os
    newpath = 'output/' + get_timestamp()
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath


out_dir = create_time_folder()


def traverse(d, sep='_', _prefix=''):
    assert isinstance(d, dict)
    for k, v in d.items():
        if isinstance(v, dict):
            yield from traverse(v, sep, "{0}{1}{2}".format(_prefix, k, sep))
        else:
            yield ("{0}{1}".format(_prefix, k), v)


def flatten(d):
    return dict(traverse(d))


def prepare_data(master_data_set):
    array = []

    for user, data in master_data_set.items():
        for reminder in data:

            acknowledged = reminder['acknowledged']
            unixtime = reminder['unixtime']
            sensors = reminder['sensors']

            # values to store
            reminder_data_dict = {}
            reminder_data_dict['acknowledged'] = acknowledged
            reminder_data_dict['unixtime'] = unixtime
            reminder_data_dict['userid'] = user

            # if sensors contains data
            if sensors:
                flat_sensors = flatten(sensors)  # flatten the nested dictionaries
                reminder_data_dict.update(flat_sensors)  # update the reminder dictionary with new data
                array.append(reminder_data_dict)  # append as a row in the master array

    return array


def write_data_to_disk(data):
    try:
        csv_raw_filepath = write_to_csv(data)
    except Exception as e:
        print(e)
    else:
        csv_ord_filepath = convert_raw_csv_to_ordered(csv_raw_filepath)
        convert_ordered_csv_to_weka(csv_ord_filepath)


def write_to_csv(data):
    filepath = out_dir + '/raw.csv'

    with open(filepath, 'w') as csvfile:
        ordered_fieldnames = OrderedDict(data[0])
        writer = csv.DictWriter(csvfile, fieldnames=ordered_fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

    return filepath


def update_acknowledged_label(number):
    if number == '1':
        return 'True'
    elif number == '0':
        return 'False'
    else:
        return 'Off'


def convert_raw_csv_to_ordered(csv_raw_filepath):
    # read in previously generated csv feature list
    # get the headers, and order them

    filepath = out_dir + '/ordered.csv'

    with open(csv_raw_filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        header = reader.fieldnames
        header_sorted = sorted(header)

        with open(filepath, 'w') as ordered_file:
            fieldnames = header_sorted
            writer = csv.DictWriter(ordered_file, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                acknowledged = row['acknowledged']
                row['acknowledged'] = update_acknowledged_label(acknowledged)

                if row['acknowledged'] == 'Off':
                    # skip the file line
                    continue
                else:
                    writer.writerow(row)
    return filepath


def write_weka_file_for_cohort(data, attributes):
    weka_data = {
        'description': '',
        'relation': 'sensors',
        'attributes': attributes,
        'data': data,
    }
    f = open(out_dir + '/cohort.arff', 'w')
    f.write(arff.dumps(weka_data))
    f.close()


def write_weka_file_for_each_user(data, attributes):
    all_users = {}

    for row in data:
        userid = row[len(row) - 1]  # User ID is the last element in list

        # Get User data from row and add to user dictionary
        # try to get existing key, and append to the existing list in value
        try:
            user_list = all_users[userid]
            user_list.append(row)
            all_users[userid] = user_list

        except KeyError:
            # If doesn't exist, create the list
            user_list = [row]
            all_users[userid] = user_list

    for user, userdata in all_users.items():
        weka_data = {
            'description': 'Data for ' + user,
            'relation': 'SensorRecordings',
            'attributes': attributes,
            'data': userdata,
        }

        # Write Weka formatted file for entire cohort
        f = open(out_dir + '/' + user + '.arff', 'w')
        f.write(arff.dumps(weka_data))
        f.close()


def convert_ordered_csv_to_weka(csv_ord_filepath):
    headers = []
    data = []
    attributes = []

    with open(csv_ord_filepath) as csvfile:
        readcsv = csv.reader(csvfile, delimiter=',')
        row_count = 0
        for row in readcsv:
            if row_count == 0:
                # Save headers for features
                headers = row
                row_count += 1
            else:
                data.append(row)
                row_count += 1

    # iterate the headings to correctly format the attribute types
    for attribute in headers:
        if attribute == 'acknowledged':
            attributes.append(('class', ['True', 'False']))
        elif attribute == 'userid':
            attributes.append((attribute, 'STRING'))
        elif attribute == 'unixtime':
            attributes.append((attribute, 'STRING'))
        else:
            attributes.append((attribute, 'REAL'))

    write_weka_file_for_cohort(data, attributes)

    # Write Weka format file for each user
    write_weka_file_for_each_user(data, attributes)


# FOR DEBUGGING
# # # Use pickle to import object saved to disk
master_data_set = pickle.load(open('pickle.p', "rb"))
results = prepare_data(master_data_set)
write_data_to_disk(results)
