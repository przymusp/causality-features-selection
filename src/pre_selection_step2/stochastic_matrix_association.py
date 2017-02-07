from __future__ import print_function
from tools.csv_helper import *

from copy import deepcopy
import numpy as np
import pandas as pd

from sinkhorn_knopp import sinkhorn_knopp as skp


def save_with_metadata_copy(df_to_save, df_metadata_to_copy, out_fname):
    # copy mataheaders
    df_to_save.meta_header = deepcopy(df_metadata_to_copy.meta_header)
    df_to_save.meta_header['pre_selection'] = ["te_ds", ]

    # write to file
    write_csv_with_metadata(df_to_save, out_fname, index=True)


def generate_double_stohastic(df_in, fname_prefix):
    # Force matrix support by adding float epsilon to 0 values
    df_in[df_in == 0] = np.finfo(np.float).eps

    # Callculate double statistic matrix from input
    sk_alg = skp.SinkhornKnopp()
    double_stohastic_df_out = sk_alg.fit(df_in.as_matrix())
    double_stohastic_df_out = pd.DataFrame(double_stohastic_df_out, df_in.index, df_in.columns)

    # write to file
    out_fname = fname_prefix + '_dstoch.csv'
    print(out_fname)
    save_with_metadata_copy(double_stohastic_df_out, df_in, out_fname)


def generate_left_stohastic(df_in, fname_prefix):
    # Make each column stochastic, i.e. divide each
    # element in col by sum of elements in col)
    df_out = df_in.div(df_in.sum('rows'), 'columns')

    # write to file
    out_fname = fname_prefix + '_lstoch.csv'
    save_with_metadata_copy(df_out, df_in, out_fname)


def generate_right_stohastic(df_in, fname_prefix):
    # Make each row stochastic, i.e. divide each element
    # in row by sum of elements in row
    df_out = df_in.div(df_in.sum('columns'), 'rows')

    # write to file
    out_fname = fname_prefix + '_rstoch.csv'
    save_with_metadata_copy(df_out, df_in, out_fname)


def main():
    fname, output_directory = parse_selection_arguments(sys.argv)
    out_fname = output_directory + "/" + path.basename(fname).split(".")[0]
    print(fname, out_fname)

    try:
        df_in = read_csv_and_metadata(fname)
    except Exception as e:
        print("Error processing file", fname, ":", e)
        return

    if len(df_in) == 0:
        print("Error: empty input matrix")
        return

    df_in.set_index(".", inplace=True)

    if df_in.shape[0] != df_in.shape[1]:
        print("Error: Non quadratic matrix")
        return


    generate_double_stohastic(df_in, out_fname)
    generate_left_stohastic(df_in, out_fname)
    generate_right_stohastic(df_in, out_fname)

if __name__ == "__main__":
    main()
