import pandas as pd
import sys
import collections

if __name__ == "__main__":
    to_merge = sys.argv[1:-1]
    output_prefix = sys.argv[-1]

    col_names = ['time', "O","H", "L", "C", "V"]
    dfs = collections.defaultdict(list)

    for filename in to_merge:
        print (filename,)
        # continue
        # read the csv
        df = pd.read_csv(filename, header=None, sep=',', index_col=0)
        name = filename.split("/")[-1].split("_")[1].split(".")[0]
        # change the column names so they won't collide during concatenation
        df.columns = [name +"_" + str(cname) for cname in col_names]
        for c in col_names[1:]:
            dfs[c].append(df[[name+"_"+c,]])

    for c in col_names[1:]:
        # concatenate them horizontally
        merged = pd.concat(dfs[c],axis=1)
        # write it out
        merged.to_csv("%s_%s.csv" %(output_prefix, c), sep=';')
