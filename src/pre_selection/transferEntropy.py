from __future__ import print_function
from tools.csv_helper import *
import sys
import subprocess
from os import path
import pandas as pd

from jpype import *
import numpy as np


# Add JIDT jar library to the path
jarLocation = "src/pre_selection/infodynamics.jar"
# Start the JVM (add the "-Xmx" option with say 1024M if you get crashes due to not enough memory space)
startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=" + jarLocation)

# Function that generates a transfer entropy matrix using the JDIT library
# The input data is the file name
def jdit_transfer_entropy_matrix (fname):
    dataRaw = pd.read_csv(fname, sep=';',header=0, comment ='#')
    data = dataRaw.values
    n_Features = len(data[0,:])
    te_matrix = np.ndarray(shape=(n_Features,n_Features))
    
    
    
    # 1. Construct the calculator:
    calcClass = JPackage("infodynamics.measures.continuous.kraskov").TransferEntropyCalculatorKraskov
    calc = calcClass()
    
    for i in range (0,n_Features):
        for j in range (0,n_Features):
            source = data[:,i]
            dest = data[:,j]
            
            
            # 2. Set any properties to non-default values:
            calc.setProperty("k_HISTORY", "20")
            calc.setProperty("l_HISTORY", "20")
            # 3. Initialise the calculator for (re-)use:
            calc.initialise()
            # 4. Supply the sample data:
            calc.setObservations(source, dest)
            # 5. Compute the estimate:
            result = calc.computeAverageLocalOfObservations()
            te_matrix[i,j] =result
    return te_matrix

if __name__ == "__main__":
    fname, output_directory = parse_selection_arguments(sys.argv)
    out_fname = output_directory + "/" + path.basename(fname).split(".")[0] + '_te_graph.csv'
    df_out = jdit_transfer_entropy_matrix (fname)
    df_in = read_csv_and_metadata(fname)
    write_csv_with_metadata(df_out, out_fname, index=True)
