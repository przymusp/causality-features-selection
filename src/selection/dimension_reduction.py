# -*- coding: utf-8 -*-                                                                                                                                                                                              
from __future__ import print_function 
import sklearn.decomposition as decomp                                                                                                                                                                               
import pandas as pd
from csv_helper import *
import os
import re
import sys


if __name__ == "__main__":

    df = read_csv_and_metadata(sys.argv[1])

    methods = [
      decomp.FactorAnalysis(n_components=4),
      decomp.NMF(n_components=4, init='nndsvda'),
      # decomp.NMF(n_components=4, init='nndsvdar'),
      # decomp.LatentDirichletAllocation(n_topics=4),
      # decomp.KernelPCA(n_components=4, kernel="rbf", fit_inverse_transform=True),
      # decomp.FastICA(n_components=4),
      # decomp.IncrementalPCA(n_components=4),
      # decomp.PCA(n_components=4)
    ]


    for c,d in exclude_column_generator(df):
        for method in methods:
            t = method.fit_transform(d)
            t = pd.DataFrame(t)
            t.meta_header = df.meta_header.copy()
            mname= str(method).replace("\n", " ")
            mname = ' '.join(mname.split())
            t.meta_header['method'] = [mname,]
            write_csv_with_metadata(t, "test")

    # with open("gsm/data/pca.csv", "w") as new_ts:
    #     t.to_csv(new_ts, sep=';', index=False, header=None)
    #     new_ts.close()
    

