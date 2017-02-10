#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

import sklearn.decomposition as decomp
import pandas as pd
from tools.csv_helper import *

methods_manual = [
    decomp.FactorAnalysis,
    decomp.FastICA,
    decomp.IncrementalPCA,
    decomp.PCA,

    partial_with_pretty_method_name(decomp.NMF, init='nndsvda'),
    partial_with_pretty_method_name(decomp.NMF,  init='nndsvdar'),
    partial_with_pretty_method_name(decomp.KernelPCA, kernel="rbf", fit_inverse_transform=True),
]

methods_automatic = [
    # Auto guessing the number of dimensions for method
    # Uses The method from "Probabilistic Principal Component Analysis"
    partial_with_pretty_method_name( decomp.PCA, n_components='mle', svd_solver='full'),
    # TODO: we cannot use automatic selection for kernel PCA as it may generate excessive number of dimensions
    # decomp.KernelPCA(kernel="rbf", fit_inverse_transform=True), # Removes zero components
    # TODO: NMF from sklearn documentation n_components may be None (use all components) or set to specyfic value. Saddly no mention of auto guessing.
    # TODO: FactorAnalysis from sklearn documentation n_components may be None (use all components) or set to specyfic value. Saddly no mention of auto guessing.
    # TODO: FastICA from sklearn documentation n_components may be None (use all components) or set to specyfic value. Saddly no mention of auto guessing.
    # TODO: IncrementalPCA from sklearn documentation n_components may be None (use min(n_samples, n_features)) or set to specyfic value. Saddly no mention of auto guessing.
]


def dimension_reduction(df, fname, data_matrix, column, methods, output_directory):
    for method in methods:
        # output for method name
        mname = "dm_" + pretty_print_method_name(method)
        out_fname = get_filename_from_method(fname, column, mname, prefix=output_directory)

        # TODO: only update the files ?
        # if file exists skip selection for this method
        # if path.isfile(out_fname):
        #     print ("File for method %s exists - skipping.\n  * Remove %s file to recompute it."%(mname,out_fname))
        #     continue

        # Fit and transform using method
        try:
            reduced_ts = method.fit_transform(data_matrix)
            reduced_ts = pd.DataFrame(reduced_ts)

            reduced_ts.meta_header = df.meta_header.copy()
            reduced_ts.meta_header['method'] = [mname,]
            reduced_ts.meta_header['predict'] = [column,]

            # Output columns in corrrect order
            cols=[column,]
            cols.extend(reduced_ts.columns.values)

            # Add predicted column to output
            reduced_ts[column] = df[column]

            # Write reduced_ts with cols in correct order (reduced_ts[cols]) to filename generated from the method name with params
            write_csv_with_metadata(reduced_ts[cols], out_fname)
        except Exception as e:
            print ("Error with method %s"%(method))
            continue

def main():
    fname, output_directory = parse_selection_arguments(sys.argv)
    df = read_csv_and_metadata(fname)

    f_max = min(min(df.shape), 30)

    methods = []
    methods.extend([m() for m in methods_automatic])
    methods.extend([m(n_components=f_num) for m in methods_manual for f_num in range(2,f_max)])

    for column, data in exclude_column_generator(df):
        dimension_reduction(df, fname, data, column, methods, output_directory)

if __name__ == "__main__":
    main()

