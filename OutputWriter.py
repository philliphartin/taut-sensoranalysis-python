def traverse(d, sep='_', _prefix=''):
    assert isinstance(d, dict)
    for k, v in d.items():
        if isinstance(v, dict):
            yield from traverse(v, sep, "{0}{1}{2}".format(_prefix, k, sep))
        else:
            yield ("{0}{1}".format(_prefix, k), v)


def flatten(d):
    return dict(traverse(d))


def write_data(master_data_set):
    # Use pickle to import object saved to disk
    # master_data_set = pickle.load(open("output/save.p", "rb"))
    array = []

    for user, data in master_data_set.items():
        for reminder in data:

            reminder_data_dict = {}
            acknowledged = reminder['acknowledged']
            unixtime = reminder['unixtime']
            sensors = reminder['sensors']

            reminder_data_dict['acknowledged'] = acknowledged
            reminder_data_dict['unixtime'] = unixtime

            # if sensors contains data
            if sensors:
                flat_sensors = flatten(sensors)  # flatten the nested dictionaries
                reminder_data_dict.update(flat_sensors)  # update the reminder dictionary with new data
                array.append(reminder_data_dict)  # append as a row in the master array

        print(array)