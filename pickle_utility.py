import app_settings
import pickle
import os

def dump(data, name):
    print("Pickle dump {0}".format(name))
    f = open(app_settings.PICKLE_DUMP + name, "wb")
    pickle.dump(data, f)

def load(name):
    print("Pickle load {0}".format(name))
    f = open(app_settings.PICKLE_DUMP + name, "rb")
    return pickle.load(f)

def exists_file(name):  
    return os.path.isfile(app_settings.PICKLE_DUMP + name) and os.path.getsize(app_settings.PICKLE_DUMP + name) > 0