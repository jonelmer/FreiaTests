import numpy as np
import math

from pprint import pprint
import datetime

import numbers

def find_nearest_index(array, value, seek=True, seq=False):
    """
    Find the index of the array closest to the provided time's timestamp
    
    default    : Return the nearest index
    seek=False : Return the nearest index which is lower than the value
    
    default    : Use a binary search
    seq=True   : Use a sequential search
    
    """
    
    if type(value) is datetime.datetime:
        value = value.timestamp()
    
    if type(array[0]) is datetime.datetime:
        array = [a.timestamp() for a in array]
    
    if seq:
        # Use a sequential search - faster if the answer is near the start
        idx = 0
        for i in range(len(array)):
            if array[idx] > value:
                break
            idx += 1
    
    else:
        # Use a binary search - faster if the answer is somewhere unpredicatble
        idx = np.searchsorted(array, value, side="left")
        
    if idx > 0 and ((idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])) or not seek):
        return idx-1
    else:
        return idx


    
def truncate(limits, data, key='time'):
    """
    Truncate data to the supplied time limits
    
    limits : pair of values to truncate between
    data   : dict of aligned lists, including a "time" list
    """
    
    if not key in data:
        raise(KeyError("{} wasn't found in the supplied data".format(key)))
    
    if not type(limits[0]) is type(data[key][0]):
        raise(TypeError("Limits are not of type({})".format(type(data[key][0]))))
    
    output = dict()

    i_start = max(find_nearest_index(data[key], min(limits)), 0)
    i_stop  = find_nearest_index(data[key], max(limits))
             
    for k in data:
        output[k] = data[k][i_start:i_stop]
                
    return output


def moving_average(a, n=3) :
    """
    Calculate a moving average on the data, default period is 3
    """
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def generate_mask(mask_pairs, mask_margin, data, key='time', progress=None):
    """
    Pairs to create a mask of mask_pairs[1] onto mask_pairs[0], with the supplied margin
    
    #TODO: Use the dwell time to mask based on the next available point!
    
    """
    
    # Sanitize inputs
    for pair in mask_pairs:
    
        if not key in data[pair[0]]:
            raise(KeyError("{} wasn't found in the supplied data['{}']".format(key, mask_pairs[0])))

        if not key in data[pair[1]]:
            raise(KeyError("{} wasn't found in the supplied data['{}']".format(key, mask_pairs[1])))
            
    if isinstance(data[pair[0]][key][0], datetime.datetime):
        for m in mask_margin:
            if not isinstance(m, datetime.timedelta):
                raise(TypeError("Mask_margin {} type({}) is not a timedelta".format(m, type(m))))
                
    elif isinstance(data[pair[0]][key][0], numbers.Number):
        for m in mask_margin:
            if not isinstance(m, numbers.Number):
                raise(TypeError("Mask_margin {} type({}) is not a number".format(m, type(m))))
                
    else:
        raise(TypeError("Mask generation unsupported for {} type({})"
                        .format(data[pair[0]][key][0], type(data[pair[0]][key][0]))))
    
    
    # Progress bar
    if progress:
        progress.max = sum([len(data[p[0]]['time']) for p in mask_pairs])/1000
        p_val = 0
    
    for pair in mask_pairs:
        
        mask = np.array([False,] * len(data[pair[0]][key]))

        for i, t in enumerate(data[pair[0]][key]):

            j = find_nearest_index(data[pair[1]][key], t)
            
            try:
                lower = (data[pair[0]][key][i] - mask_margin[0] > data[pair[1]][key][j])
                upper = (data[pair[0]][key][i] - mask_margin[1] < data[pair[1]][key][j])
                
                #print("Index found at:  {}\t{}\t{}\t{}".format(pair[0], i, pair[1], j))

                if lower and upper:
                    mask[i] = True
                else:
                    mask[i] = False

            except IndexError:
                #print("Index not found: {}\t{}\t{}\t{}".format(pair[0], i, pair[1], j))
                mask[i] =  None

            if progress:
                p_val += 1
                if p_val % 1000 == 0:
                    progress.value += 1

        name = "_".join(["mask", pair[1]])
        data[pair[0]][name] = mask
        
    if progress:
        # Finised - max out the progress bar 
        progress.value = progress.max
        
        
        
def calculate_differences(diff_pairs, data, key='time', progress=None):
    """
    Pairs to find the difference of diff_pairs[0] - diff_pairs[1], and store it in diff_pairs[0]
    """
    #diff_pairs = [
    #    (['position', 'data'],            ['set_point', 'data']),
    #    (['keyence', ['data1', 'data2']], ['set_point', 'data']),
    #    (['keyence', ['data1', 'data2']], ['position',  'data']),
    #]
    
    # Sanitize inputs
    for pair in diff_pairs:
        if not key in data[pair[0][0]]:
            raise(KeyError("{} wasn't found in the supplied data['{}']".format(key, pair[0])))

        if not key in data[pair[1][0]]:
            raise(KeyError("{} wasn't found in the supplied data['{}']".format(key, pair[1])))

    # Progress bar
    if progress:
        progress.max = sum([len(data[p[0][0]][key]) for p in diff_pairs])/1000
        p_val = 0

    for pair in diff_pairs:

        if type(pair[0][1]) != list:
            pair[0][1] = [pair[0][1], ]

        diff = [np.array([None,] * len(data[pair[0][0]][key])),] * len(pair[0][1])

        for i, t in enumerate(data[pair[0][0]][key]):

            j = find_nearest_index(data[pair[1][0]][key], t, seq=True, seek=False)

            for l in range(len(pair[0][1])):
                try:
                    diff[l][i] =  data[pair[0][0]][pair[0][1][l]][i]
                    diff[l][i] -= data[pair[1][0]][pair[1][1]][j]
                except IndexError:
                    print("Index not found: {}\t{}\t{}\t{}\t{}".format(pair[0][0], i, pair[0][1][l], j, l))
                    diff[l][i] =  None
            
            if progress:
                p_val += 1
                if p_val % 1000 == 0:
                    progress.value += 1

        for l in range(len(pair[0][1])):
            name = "_".join([pair[0][1][l],] + pair[1])
            data[pair[0][0]][name] = diff[l]

    if progress:
        # Finised - max out the progress bar 
        progress.value = progress.max