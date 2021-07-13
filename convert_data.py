#!/usr/bin/env python3

import sys
import re
import pandas    as pd
import itertools as it


identifiers = ["ID", "Depth", "Skinlatency", "DR threshold test", "Note1", "Note2", "Note3", "Note4", "Note5"]
inputs      = ["Skin", "Ia", "Ib" ,"II" ,"Pyr"]
outputs     = ["aMN", "LRN"]

usage = \
"""Usage:
convert_data.py data.csv output_data.csv [weight|noweight]"""

def tuple_to_string(t):
    return str(t[0]) + str(t[1])    

def inputs_lengths(inputs):
    lengths = range(-4, 5)
    cross = it.product(inputs, lengths)
    return list(map(tuple_to_string, cross))

def data_to_list(raw, datatype):
    raw = str(raw)
    if raw == '-' or raw == '' or raw == 'nan':
        return []
    f = int if datatype == 'int' else lambda x: int(10*float(x))
    return list(map(f, filter(lambda x: len(x) > 0, re.split(';|:', raw))))

def convert_data(data, weight_conversion = None):
    columns_syn =   inputs_lengths(inputs) + inputs_lengths(outputs)
    tidy_data = pd.DataFrame(columns = identifiers + columns_syn)

    for idx, rows in data.groupby(data.index // 2):
        syn    = rows.iloc[0]
        weight = rows.iloc[1]
        
        tidy_row = {}
        
        print(columns_syn)
        for c in columns_syn:
            tidy_row[c] = 0
            
        for i in inputs:
            isyn    = data_to_list(syn[i],    'int')
            iweight = data_to_list(weight[i], 'float')

            if len(isyn) < len(iweight):
                print("Less input lengths then weights")
                assert(False)

            for s, w in zip(isyn, iweight + len(isyn) * [None]):
                if weight_conversion == 'weight':
                    tidy_row[tuple_to_string((i, s))] = w
                elif weight_conversion == 'noweight':
                    tidy_row[tuple_to_string((i, s))] = 1                    
                else:
                    print(usage)
                    print('Specify weight/noweight')
        
        for i in identifiers:
            tidy_row[i] = syn[i]

        tidy_data = tidy_data.append(tidy_row, ignore_index = True)

    return tidy_data

def main():
    if len(sys.argv) <= 3:
        print(usage)
        return

    input_filename  = sys.argv[1]
    output_filename = sys.argv[2]
    
    data = pd.read_csv(input_filename, encoding = 'utf8')

    tidy_data = convert_data(data, weight_conversion = sys.argv[3])
    tidy_data.to_csv(output_filename)

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(tidy_data)

if __name__ == "__main__":
    main()
