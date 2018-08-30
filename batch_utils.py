import pickle
import numpy as np
from pprint import pprint
import data_tools
import copy

def pickle_name(filename, keyence_filename=None, suffix="full_data", data_dir=".\\data\\"):
    if keyence_filename is not None:
        pickle_file = data_dir + "_".join([filename, keyence_filename, suffix]) + ".p"
    else:
        pickle_file = data_dir + "_".join([filename, suffix]) + ".p"
    
    return pickle_file


def load_data(filename, keyence_filename=None, suffix="full_data"):
    
    pickle_file = pickle_name(filename, keyence_filename, suffix)
    
    full_data = pickle.load(open(pickle_file, 'rb'))
    print("Loaded the data from " + pickle_file)

    # Pop the info out, it can't be processed...
    info = full_data.pop("info")

    return full_data, info


def store_data(data, filename, keyence_filename=None, suffix="proc_data_partial", info=None):
    pickle_file = pickle_name(filename, keyence_filename, suffix)
    
    if info is not None:
        # Add the info back in before pickling...
        data['info'] = info

    pickle.dump(data, open(pickle_file, 'wb'))

    print("Stored the data in {}".format(pickle_file))


def print_lengths(d, label="Dataset:"):
    print(label)
    for k in d:
        print("{}: \t{} points".format(k, len(d[k][[*d[k]][0]])))

        
def print_structure(data, length=False):
    for k in data:
        print(k)
        for l in data[k]:
            if length:
                print("\t{}\t\t{}".format(l, len(data[k][l])))
            else:
                print("\t"+l)


def calculate_trans(data, p=None):
    if p is not None:
        p.max = len(data['set_point']['time'])
    
    i_last = 0

    for i, (t, sp) in enumerate(zip(data['set_point']['time'], data['set_point']['data'])):
        # Find the nearest time index in the position dataset
        i_start = data_tools.find_nearest_index(data['position']['time'][i_last:], t) + i_last

        try:
            # Find the first index where the setpoint is reached from the rounded position dataset
            i_stop  = data['position']['round'][i_start:].index(sp) + i_start
            i_last = i_stop

            # The transition time is the time between the setpoint change, and the setpoint being reached
            time = data['position']['time'][i_stop] - t
            data['set_point']['trans'][i] = time.total_seconds()

        except ValueError:
            data['set_point']['trans'][i] = None
        
        if p is not None:
            # Update the progress bar
            p.value += 1
            
    p.value = p.max
    

def merge_data(data, new_data, p=None):
    if p is not None:
        p.max = sum([len(new_data[k]) for k in new_data])
    
    for key in new_data:
        if key in data:        
            for k in new_data[key]:
                if k in data[key]:
                    data[key][k] = np.append(data[key][k], new_data[key][k])
                else:
                    data[key][k] = copy.deepcopy(new_data[key][k])

                if p is not None:
                    p.value += 1
        else:
            data[key] = copy.deepcopy(new_data[key])
            