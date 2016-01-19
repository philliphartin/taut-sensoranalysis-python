import csv
import time
from collections import OrderedDict

from arff import arff

outdirectory = 'output/'
features_csv_output = 'output.csv'
features_arff_output = 'output.arff'


def get_timestamp():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    return timestr


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
        write_raw_data_to_csv(data)
    except Exception:
        print('Failed')
    else:
        convert_raw_csv_to_ordered()


def write_raw_data_to_csv(data):
    with open(outdirectory + features_csv_output, 'w') as csvfile:
        ordered_fieldnames = OrderedDict(data[0])
        writer = csv.DictWriter(csvfile, fieldnames=ordered_fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)


def update_acknowledged_label(number):
    if number == '1':
        return 'True'
    elif number == '0':
        return 'False'
    else:
        return 'Off'


def convert_raw_csv_to_ordered():
    # read in previously generated csv feature list
    # get the headers, and order them

    row_count = 0

    filepath_input = outdirectory + features_csv_output
    filepath_output = outdirectory + 'ordered_' + get_timestamp() + '.csv'

    with open(filepath_input) as csvfile:
        print('Opening ' + outdirectory + features_csv_output)
        reader = csv.DictReader(csvfile)
        header = reader.fieldnames
        header_sorted = sorted(header)

        with open(filepath_output, 'w') as ordered_file:
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
                    row_count = + 1

    convert_ordered_csv_to_weka(filepath_output)


def convert_ordered_csv_to_weka(filepath):
    print('Opening ' + filepath)

    csv_headers = []
    data = []
    attributes = []

    with open(filepath) as csvfile:
        readcsv = csv.reader(csvfile, delimiter=',')
        # csv_headers = readcsv.next()
        # Save csv_headers
        row_count = 0
        for row in readcsv:
            if row_count == 0:
                csv_headers = row
                row_count += 1
            else:
                data.append(row)
                row_count += 1

    # iterate the headings to correctly format the attribute types
    for feature in csv_headers:
        if feature == 'acknowledged':
            attributes.append(('class', ['True', 'False']))
        elif feature == 'userid':
            attributes.append((feature, 'STRING'))
        elif feature == 'unixtime':
            attributes.append((feature, 'STRING'))
        else:
            attributes.append((feature, 'REAL'))

    weka_data = {
        'description': '',
        'relation': 'sensors',
        'attributes': attributes,
        'data': data,
    }

    # Writes Weka formatted file to output folder
    f = open(outdirectory + features_arff_output, 'w')
    f.write(arff.dumps(weka_data))
    f.close()

# FOR DEBUGGING
# # # Use pickle to import object saved to disk
# master_data_set = pickle.load(open("output/save.p", "rb"))
# results = prepare_data(master_data_set)
# write_data_to_disk(results)
