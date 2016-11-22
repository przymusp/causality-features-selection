import pandas as pd
import base64
import hashlib

def parse_selection_arguments(argv):
    """Parse cmdline arguments for selection method script

    :args: TODO
    :returns: TODO

    """
    if len(argv) < 3:
        print ('Error: wrong number of params')
        exit(0)

    fname = argv[1]
    output_directory = argv[2]+"/"

    if not path.isdir(output_directory):
        print ("Error: output directory does not exist")
        exit()
    if not path.isfile(fname):
        print ("Error: input CSV file does not exist")
        exit()
    return fname, output_directory

def get_filename_from_method(fname, predicted_column, method_name, prefix = "", postfix=".csv"):
    f = fname.split('/')
    f = f[-1].split(".")[0]
    name = method_name.split("(")
    hasher = hashlib.sha1(method_name)
    o = base64.urlsafe_b64encode(hasher.digest()[0:200])
    return prefix + "_".join([f,predicted_column,name[0], o]) + postfix

def pretty_print_method_name(method):
    mname = str(method).replace("\n", " ")
    return ' '.join(mname.split())

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
        print (v[0])
        print (v[1])

