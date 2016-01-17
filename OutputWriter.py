import pickle

# Use pickle to import object saved to disk
master_data_set = pickle.load(open("output/save.p", "rb"))

print(master_data_set)
