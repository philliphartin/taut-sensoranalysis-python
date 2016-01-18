import pickle

# def flatten_dict(dd, separator='_', prefix=''):
#     return {prefix + separator + k if prefix else k: v
#             for kk, vv in dd.items()
#             for k, v in flatten_dict(vv, separator, kk).items()
#             } if isinstance(dd, dict) else {prefix: dd}


def flatten_dict(d):
    items = []
    for k, v in d.items():
        try:
            if (type(v)==type([])):
                for l in v: items.extend(flatten_dict(l).items())
            else:
                items.extend(flatten_dict(v).items())
        except AttributeError:
            items.append((k, v))
    return dict(items)
# Use pickle to import object saved to disk
master_data_set = pickle.load(open("output/save.p", "rb"))

# for user, data in master_data_set.items():
#     for reminder in data:


test = flatten_dict(master_data_set)

print(master_data_set)
