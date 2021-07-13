#!/usr/bin/env python3

import pandas as pd

data = pd.read_csv('./data_synaptology/Synaptology_tidy.csv')

print(data)

reduced_data = pd.DataFrame()

reduced_data['ID']     = data['ID']
reduced_data['Skin-2'] =                  data['Skin-2'] | data['Skin-3'] | data['Skin-4']
reduced_data['Skin1']  = data['Skin1']  | data['Skin2']  | data['Skin3']  | data['Skin4']
reduced_data['Ia-2']   =                  data['Ia-2']   | data['Ia-3']   | data['Ia-4'] 
reduced_data['Ia1']    = data['Ia1']    | data['Ia2']    | data['Ia3']    | data['Ia4']
reduced_data['Ib-2']   =                  data['Ib-2']   | data['Ib-3']   | data['Ib-4'] 
reduced_data['Ib1']    = data['Ib1']    | data['Ib2']    | data['Ib3']    | data['Ib4']

reduced_data.to_csv('./data_synaptology/Synaptology_tidy_reduced.csv', index = False)

print(reduced_data)
