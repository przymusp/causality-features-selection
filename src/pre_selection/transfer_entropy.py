from __future__ import print_function
from tools.csv_helper import *
import sys
import subprocess
from os import path
import pandas as pd

if __name__ == "__main__":
    fname, output_directory = parse_selection_arguments(sys.argv)

    is_rolling = False
    if len(sys.argv) == 4:
        is_rolling = True


    # TODO: now writen as awk script.  Consider if it is worth rewrite as Python ? (mawk implementation may be faster then pure python)
    to_te_tool = "awk '!/^#/{gsub(/;/,\" \"); gsub(/ +/,\" \"); print}'"
    te_tool = "~/src/libtransferentropy/bin/pairwise_transfer_entropy"
    from_te_tool = "awk '{gsub(/ +/,\" \"); gsub(/(^ +)|( +$)/,\"\"); print}'"
    awk_cmd = " %(to_te_tool)s %(fname)s | %(te_tool)s | %(from_te_tool)s > %(out_fname)s "

    out_fname = output_directory + "/" + path.basename(fname).split(".")[0] + '_te_graph.csv'

    params_dict = {
            'fname':fname,
            'te_tool':te_tool,
            'to_te_tool': to_te_tool,
            'from_te_tool': from_te_tool,
            'out_fname':out_fname,
            }
    if is_rolling:
        print('ERROR: no rolling version avalible now')
        # TODO: write special function
        # awk_cmd = "awk '!/^#/' | awk 'NR == 1 || (NR >=%(START)s && <=%(END)s){gsub(/;/,\" \"); gsub(/ +/,\" \"); print}' %(fname)s | %(te_tool)s | awk '{gsub(/ +/,\" \"); gsub(/(^ +)|( +$)/,\"\"); print}' > %(out_fname)s "
    # awk_cmd %= {'fname':fname, 'te_tool':te_tool, 'out_fname':out_fname}
    else:
        awk_cmd %= params_dict

    subprocess.call(awk_cmd, shell=True)

    df_out = pd.read_csv(out_fname, sep=' ', index_col=0)
    df_in = read_csv_and_metadata(fname)

    # shallow copy is Ok here
    df_out.meta_header = df_in.meta_header
    df_out.meta_header['pre_selection']= ["te",]

    write_csv_with_metadata(df_out, out_fname, index=True)


