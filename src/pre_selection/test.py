import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import subprocess
from joblib import Parallel, delayed
from joblib import load, dump

def get_rolling_window(fname, start, end):
    pairwise_transfer_entropy = "~/src/libtransferentropy/bin/pairwise_transfer_entropy -w 1"
    out_fname = "/tmp/test%d_%d.csv"%(start, end)
    awk_cmd = "awk '!/^#/' %(fname)s| awk 'NR == 1 || (NR >=%(START)s && NR <=%(END)s){gsub(/;/,\" \"); gsub(/ +/,\" \"); print}'  | %(pairwise_transfer_entropy)s | awk '{gsub(/ +/,\" \"); gsub(/(^ +)|( +$)/,\"\"); print}' > %(out_fname)s "
    awk_cmd %= {'fname':fname, 'pairwise_transfer_entropy':pairwise_transfer_entropy, 'out_fname':out_fname, 'START':start, 'END':end}

    subprocess.call(awk_cmd, shell=True)
    df_out = pd.read_csv(out_fname, sep=' ', index_col=0)
    return df_out

def updatefig(df):
    im = plt.pcolormesh(df)
    return im,

def main():
    fig = plt.figure()
    out_fname = sys.argv[1]
    df = pd.read_csv(out_fname, sep=';', skip_blank_lines=True, comment='#')
    frames = []
    # for i in range(len(df)-40):

    frames = Parallel(-1)(delayed(get_rolling_window)(out_fname, i, i + 40) for i in range(len(df)-40))

    ani = animation.FuncAnimation(fig, updatefig, frames=frames, interval=50, blit=True)
    ani.save("transfer_entropy.mp4")

import sys
if __name__ == "__main__":
    main()
