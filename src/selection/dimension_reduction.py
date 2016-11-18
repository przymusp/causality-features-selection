# -*- coding: utf-8 -*-                                                                                                                                                                                              
from __future__ import print_function 
import sklearn.decomposition as decomp                                                                                                                                                                               
import pandas as pd
from csv_helper import *
import os
import re
import sys
import base64
import hashlib

def get_filename_from_method(fname, predicted_column, method_name, prefix = ""):
    f = fname.split('/')
    f = f[-1].split(".")[0]
    name = mname.split("(")
    hasher = hashlib.sha1(mname)
    o = base64.urlsafe_b64encode(hasher.digest()[0:200])
    return prefix + "_".join([f,predicted_column,name[0], o])


if __name__ == "__main__":
    fname = sys.argv[1]
    df = read_csv_and_metadata(fname)

    methods = [
      decomp.FactorAnalysis(n_components=4),
      decomp.NMF(n_components=4, init='nndsvda'),
      decomp.NMF(n_components=4, init='nndsvdar'),
      #decomp.LatentDirichletAllocation(n_topics=4),
      decomp.KernelPCA(n_components=4, kernel="rbf", fit_inverse_transform=True),
      decomp.FastICA(n_components=4),
      decomp.IncrementalPCA(n_components=4),
      decomp.PCA(n_components=4)
    ]


    for c,d in exclude_column_generator(df):
        for method in methods:
            t = method.fit_transform(d)
            t = pd.DataFrame(t)
            t.meta_header = df.meta_header.copy()
            mname= str(method).replace("\n", " ")
            mname = ' '.join(mname.split())
            t.meta_header['method'] = [mname,]
            cols=list(t.columns.values)
            t[c] = df[c]
            cols.insert(0, c)
            write_csv_with_metadata(t[cols], get_filename_from_method(fname, c, mname, prefix=sys.argv[2]+"/") + ".csv", columns = cols)

    

