import pandas as pd

def read_metadata_from_csv_file(filename):
    def __parse_metadata(line):
        l = line[1:]
        values = l.split(';')
        return values[0].strip(), [v.strip() for v in values[1:]]

    metadata = {}
    with open(filename) as f:
        for line in f:
            if line[:1] == '#':
                key, values = __parse_metadata(line)
                metadata[key] = values
            else:
                return metadata

def read_csv_and_metadata(filename):
    pd.DataFrame._metadata=["meta_header"]
    matrix =  pd.read_csv(filename, comment='#', delimiter=';')
    matrix.meta_header = read_metadata_from_csv_file(filename)
    return matrix

def exclude_column_generator(df):
    for c in df.meta_header['predict']:
        yield c, df[df.columns.difference([c,])]

def write_csv_with_metadata(df, filename):
    with open(filename, "w") as f:
        for k in df.meta_header:
             f.write("# %s; " % (k,) + ';'.join(df.meta_header[k])+"\n")
        df.to_csv(f, sep=';', index=False)

if __name__ == "__main__":
    import sys
    m = read_csv_and_metadata(sys.argv[1])
    for v in exclude_column_generator(m):
        print v[0]
        print v[1]

