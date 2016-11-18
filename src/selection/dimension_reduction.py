#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sklearn.decomposition as decomp
import pandas as pd
import os
import re
import sys
import base64
import hashlib

def get_filename_from_method(fname, predicted_column, method_name, prefix = "", postfix=".csv"):
    f = fname.split('/')
    f = f[-1].split(".")[0]
    name = method_name.split("(")
    hasher = hashlib.sha1(mname)
    o = base64.urlsafe_b64encode(hasher.digest()[0:200])
    return prefix + "_".join([f,predicted_column,name[0], o]) + postfix

def __pretty_print_method_name(method):
    mname = str(method).replace("\n", " ")
    return ' '.join(mname.split())

if __name__ == "__main__":
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from tools.csv_helper import *

    if len(sys.argv) < 3:
        print ('Error: wrong number of params')
        exit(0)

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

            # Fit and transform using method
            t = method.fit_transform(d)
            t = pd.DataFrame(t)

            t.meta_header = df.meta_header.copy()
            mname = __pretty_print_method_name(method)
            t.meta_header['method'] = [mname,]

            # Output columns in corrrect order
            cols=[c,]
            cols.extend(t.columns.values)

            # Add predicted column to output
            t[c] = df[c]

            # Write t with cols in correct order (t[cols]) to filename generated from the method name with params
            write_csv_with_metadata(t[cols], get_filename_from_method(fname, c, mname, prefix=sys.argv[2]+"/"))
