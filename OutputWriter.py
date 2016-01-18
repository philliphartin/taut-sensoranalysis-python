import csv
from collections import OrderedDict

import Emailer
import HiddenEmail


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
    # Use pickle to import object saved to disk
    # master_data_set = pickle.load(open("output/save.p", "rb"))
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


def write_data_to_csv(data):
    with open('output/result.csv', 'w') as csvfile:
        ordered_fieldnames = OrderedDict(data[0])
        writer = csv.DictWriter(csvfile, fieldnames=ordered_fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)


Emailer.mail(HiddenEmail.__email__, 'Python TAUT sensor feature analysis complete',
             'File has been saved, GREAT SUCCESS!')