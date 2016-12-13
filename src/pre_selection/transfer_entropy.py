from __future__ import print_function
from tools.csv_helper import *
import sys
import subprocess
from os import path
import pandas as pd

if __name__ == "__main__":
    fname, output_directory = parse_selection_arguments(sys.argv)

    pairwise_transfer_entropy = "~/src/libtransferentropy/bin/pairwise_transfer_entropy"
    out_fname = output_directory + "/" + path.basename(fname).split(".")[0] + '_te_graph.csv'

    # TODO: now writen as awk script.  Consider if it is worth rewrite as Python ? (mawk implementation may be faster then pure python)
    awk_cmd = "awk '!/^#/{gsub(/;/,\" \"); gsub(/\s+/,\" \"); print}' %(fname)s | %(pairwise_transfer_entropy)s | awk '{gsub(/\s+/,\" \"); gsub(/(^\s+)|(\s+$)/,\"\"); print}' > %(out_fname)s "
    awk_cmd %= {'fname':fname, 'pairwise_transfer_entropy':pairwise_transfer_entropy, 'out_fname':out_fname}

    subprocess.call(awk_cmd, shell=True)
    df_out = pd.read_csv(out_fname, sep=' ', index_col=0)
    df_in = read_csv_and_metadata(fname)

    # shallow copy is Ok here
    df_out.meta_header = df_in.meta_header
    df_out.meta_header['pre_selection']= ["Transfer Entropy Pairwise",]

    write_csv_with_metadata(df_out, out_fname, index=True)

