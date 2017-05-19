from __future__ import print_function
from tools.csv_helper import *
import sys
import subprocess
from os import path
import pandas as pd
from six import StringIO

if __name__ == "__main__":
    fname, output_directory = parse_selection_arguments(sys.argv)

    is_rolling = False
    if len(sys.argv) == 4:
        is_rolling = True

    df_in = read_csv_and_metadata(fname)
    org_columns = list(df_in.columns)
    m_columns = ['a%d'%(i) for i in range(len(org_columns))]
    maping_of_columns = dict(zip(m_columns, org_columns))

    in_str_csv = df_in.to_csv(sep=' ', header=m_columns, index='False')

    # External tool used for callculating TE
    te_tool = "~/src/libtransferentropy/bin/pairwise_transfer_entropy -b 16 -w 1"

    p = subprocess.Popen(
            te_tool.split(" "),
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
            )

    te_stdout = p.communicate(input=in_str_csv)[0]
    out_str_csv = te_stdout.decode()
    df_out = pd.read_csv(StringIO(out_str_csv), sep=r"\s*", index_col=0, engine='python')
    df_out.rename(index=maping_of_columns, columns=maping_of_columns, inplace=True)


    out_fname = output_directory + "/" + path.basename(fname).split(".")[0] + '_te_graph.csv'

    if is_rolling:
        print('ERROR: no rolling version avalible now')
        # TODO: write special function

    # shallow copy is Ok here
    df_out.meta_header = df_in.meta_header
    df_out.meta_header['pre_selection']= ["te",]

    write_csv_with_metadata(df_out, out_fname, index=True)


