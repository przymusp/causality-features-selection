# -*- coding: utf-8 -*-
"""
@author: fornax
"""
import os
import pandas as pd
from tqdm import tqdm


def merge_train_data(src_data_path, dst_data_path):
    print("Concatenating context files")
    dates = ['A--2008-08-22_2010-07-10', 'B--2010-07-10_2012-05-27', 'C--2012-05-27_2014-04-14', 'D--2014-04-14_2015-01-01']
    contexts = ['dmop', 'evtf', 'ftl', 'saaf', 'ltdata']

    for context in tqdm(contexts):
        aggr = []
        for m_year, date in enumerate(dates):
            folder = os.path.join(src_data_path, 'train_set')
            df = pd.read_csv(os.path.join(folder, 'context--%s--%s.csv' % (date, context)))
            aggr.append(df)
        pd.concat(aggr).to_csv(os.path.join(dst_data_path, context + '.csv'), index=False)

    # power files
    print("Concatenating power lines")
    aggr = []
    for m_year, date in enumerate(dates):
        df = pd.read_csv(os.path.join(src_data_path, 'train_set', 'power--%s.csv' % date))
        aggr.append(df)
    pd.concat(aggr).to_csv(os.path.join(dst_data_path, 'power.csv'), index=False)
    print("Done...")

def merge_all(src_data_path, dst_data_path):
    contexts = ['dmop']#, 'dmop', 'evtf', 'ftl', 'saaf', 'ltdata']
    
    folder = os.path.join(src_data_path, 'train_data')
    all = pd.read_csv(os.path.join(folder, 'power.csv'))
    #print (all.head (2))
    
    for context in tqdm(contexts):
        df = pd.read_csv(os.path.join(folder,'%s.csv' % context))
        #print (df.head(2))
        all = all.merge(df,how = 'left', on='ut_ms')
        all. head (100). to_csv (os.path. join(dst_data_path,'all.csv'), index = False, sep = ';')
    print("Done...")
#merge_train_data ("", "merge_train_set")
merge_all ("", "merge_train_set")

