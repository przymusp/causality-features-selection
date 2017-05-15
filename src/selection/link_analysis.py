from __future__ import print_function
import sys
import traceback
import glob
from os import path
import re

import networkx as nx
import pandas as pd

import tools.csv_helper as csvh

def trim_graph_matrix(graph_matrix):
    # TODO: future work, clean the graph, some ideas
    # for a,b in itertools.product(graph_matrix.columns.values, repeat=2):
    #     if abs(graph_matrix[a][b] - graph_matrix[b][a]) < 0.05:
    #         graph_matrix[a][b]=0
    #         graph_matrix[b][a]=0
    return graph_matrix

def adjust_graph_matrix(graph_matrix):
    # TODO: without adjusting method yields better results
    # Columns should sum to 1. sum and divide by column by column
    # Fix the pandas metadata handling problem
    # meta_header = graph_matrix.meta_header
    # graph_matrix /= graph_matrix.sum(1)
    # graph_matrix.meta_header = meta_header
    return graph_matrix

def write_selection_file(result_sorted, pred_column, n_components, org_data, out_fname, mname):
    output_dimensions = result_sorted[:n_components].transpose()

    # If predicted column is in the set - remove it
    # Normally the predicted column should be the first column in this set,
    # so this is just a precaution. As we will add this column back in next step.
    output_dimensions = list(output_dimensions.columns.values)
    try:
        output_dimensions.remove(pred_column)
    except Exception as e:
        pass
    output_dimensions.insert(0, pred_column)

    # Set metadata and write output selection file
    org_data.meta_header['predict'] = [pred_column,]
    org_data.meta_header['method'] = [mname,]

    csvh.write_csv_with_metadata(org_data[output_dimensions], out_fname)

def pagerank(graph, alpha, p_vector):
    rank_vector = None

    try:
        rank_vector = nx.pagerank_numpy(
                 graph, alpha=0.85, personalization=p_vector)
    except Exception as exception_numpy:
        print("Error: Could not callculate pagerank:", exception_numpy)

    if rank_vector is None:
        print("trying pagerank_scipy")
        try:
            rank_vector = nx.pagerank_scipy(
                     graph, alpha=0.85, personalization=p_vector)
        except Exception as exception_scipy:
            print("Error: Could not callculate pagerank:", exception_scipy)

    if rank_vector is None:
        print("trying power iteration")
        try:
            rank_vector = nx.pagerank( graph, alpha=0.85, personalization=p_vector, max_iter=200)
        except Exception as exception:
            print("Error: Could not callculate pagerank:", exception)

    return rank_vector

def link_analysis(fname, output_directory, fname_graph, graph_type):
    print(graph_type)
    # Complain if the file does not exists
    if not path.isfile(fname_graph):
        print(fname_graph)
        print("Error: the Transfer entropy graph file does not exist. Please run the pre-selection Transfer Entropy generation step")
        exit()

    graph_matrix = csvh.read_csv_and_metadata(fname_graph, index_col=0)

    # Trim the input graph
    graph_matrix = trim_graph_matrix(graph_matrix)

    # adjust the input graph
    graph_matrix = adjust_graph_matrix(graph_matrix)

    # Prepare graph and inverse of graph
    g_normal = nx.DiGraph(graph_matrix.as_matrix())
    g_reverse = g_normal.reverse()

    # Nodes to variable names map and inverted map
    nodes_map = dict(zip(graph_matrix.columns.values, range(len(graph_matrix.columns.values))))
    inv_nodes_map = {v: k for k, v in nodes_map.items()}

    # Read unmodified input data set, this will be used to output columns in selection file.
    org_input_file = csvh.read_csv_and_metadata(fname)

    for reverse in [False, True]:

        graph = g_reverse if reverse else g_normal

        for predicted_column in graph_matrix.meta_header['predict']:
            p_vector = dict.fromkeys(graph, 0)
            p_vector[nodes_map[predicted_column]] = 1

            rank_vector = pagerank(graph, 0.85, p_vector)
            if rank_vector is None: continue
            # print(rank_vector)

            rank_vector_maped = {inv_nodes_map[k]:rank_vector[k] for k in rank_vector}
            result_sorted = pd.DataFrame.from_dict(rank_vector_maped, orient='index')
            result_sorted.sort_values(0, inplace=True, ascending=False)

            max_number_of_features = min(len(result_sorted), 30)

            for n_components in range(2, max_number_of_features):

                method_name = "LinkAnalysis_%s_reverse_%d(n_components=%d)"\
                        % (graph_type, reverse, n_components)
                out_fname = csvh.get_filename_from_method(fname, predicted_column, method_name, prefix=output_directory)

                write_selection_file(result_sorted, predicted_column, n_components, org_input_file, out_fname, method_name)

def main():
    fname, output_directory = csvh.parse_selection_arguments(sys.argv)

    # Search for Adj-matrix for TS file in data folder
    fname_base = path.basename(fname).split(".")[0]
    # fname_dir = path.dirname(fname)

    output_directory_pre_selection = output_directory.replace("selection", "pre_selection")

    for fname_graph in glob.glob(output_directory_pre_selection + "/*.csv"):
        m = re.match(".*(te|granger)(.*).csv", fname_graph)
        if m is None:
            print("Error: could not match graph_type in filename", fname_graph)
            continue
        graph_type = m.group(1) + "_" + m.group(2)
    # for graph_type in ['te_graph', 'te_ds_graph', 'granger_graph', 'te_graph_jdit']:
    #     fname_graph = output_directory_pre_selection + "/" + fname_base + "_" + graph_type + ".csv"
        try:
            link_analysis(fname, output_directory, fname_graph, graph_type)
        except Exception as exception:
            print("Could not callculate link analysis", exception)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** print_tb:")
            traceback.print_tb(exc_traceback,file=sys.stdout)

if __name__ == '__main__':
    main()
