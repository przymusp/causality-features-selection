import pandas as pd
import csv_helper as csv
import sys
from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score,median_absolute_error, r2_score

global_measures = {
    'mse': mean_squared_error,
        'mae': mean_absolute_error,
            # 'evc': explained_variance_score,
            # 'r2': r2_score,
            'medae': median_absolute_error,
                # 'R': lambda x,y: 1, # placeholder
            }

r = csv.read_csv_and_metadata("data/ebob-l.csv")
p = csv.read_csv_and_metadata(sys.argv[1])

r_c = r[['CAC40']].tail(len(p))
p_c = p[[0,]]


for k in global_measures:
    print (k,global_measures[k](r_c,p_c))
