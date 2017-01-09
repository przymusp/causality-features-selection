from __future__ import print_function
import sys
import collections as col
import itertools
from os import path

import networkx as nx
import numpy as np
import matplotlib.pylab as plt
import pandas as pd
from sklearn import preprocessing

from tools.csv_helper import *

def link_analysis(fname_graph, graph_type):
    # Complain if the file does not exists
    if not path.isfile(fname_graph):
        print(fname_graph)
        print ("Error: the Transfer entropy graph file does not exist. Please run the pre-selection Transfer Entropy generation step")
        return

    df = read_csv_and_metadata(fname_graph, index_col=0)

    # TODO: future work, clean the graph, some ideas
    # for a,b in itertools.product(df.columns.values, repeat=2):
    #     if abs(df[a][b] - df[b][a]) < 0.05:
    #         df[a][b]=0
    #         df[b][a]=0


    # Columns should sum to 1. sum and divide by column by column
    # Fix the pandas metadata handling problem
    meta_header = df.meta_header
    df /= df.sum(1)
    df.meta_header = meta_header


    # The algorithm
    G = nx.DiGraph(df.as_matrix())

    # Nodes to variable names map and inverted map
    nodes_map = dict(zip(df.columns.values, range(len(df.columns.values))))
    inv_nodes_map = {v: k for k, v in nodes_map.items()}


    G= G.reverse()
    pr = nx.pagerank(G, alpha=0.85)
    pr1 = {inv_nodes_map[k]:pr[k] for k in pr}
    page_rank_no_personalization = pd.DataFrame.from_dict(pr1, orient='index')
    page_rank_no_personalization.sort_index()

    # G_reverse = G.reverse()

    # pr = nx.pagerank(G, alpha=0.85)
    # pr1 = {inv_nodes_map[k]:pr[k] for k in pr}
    # page_rank_no_personalization1 = pd.DataFrame.from_dict(pr1, orient='index')
    # page_rank_no_personalization1.sort_index()

    # page_rank_no_personalization -= page_rank_no_personalization1

    # print (page_rank_no_personalization)
    # return

    # Read the actual file with timeseries, this will be used to generate the output file
    df_out = read_csv_and_metadata(fname)

    for c in df.meta_header['predict']:
        p = dict.fromkeys(G, 0)
        p[nodes_map[c]]=1

        G1 = G.copy()
        print(G1.in_edges([nodes_map[c]]))
        G1.remove_edges_from(G1.in_edges([nodes_map[c]]))
        print(G1.in_edges([nodes_map[c]]))
        G = G1

        # Page rank with personalization
        pr = nx.pagerank(G, alpha=0.85, personalization = p)

        page_rank_personalization = {inv_nodes_map[k]:pr[k] for k in pr}
        page_rank_personalization = pd.DataFrame.from_dict(page_rank_personalization, orient='index')
        page_rank_personalization.sort_index()

        # Spam mass analysis
        diff = (page_rank_no_personalization - page_rank_personalization)/page_rank_no_personalization
        print(diff)
        # a = pd.concat([diff, page_rank_no_personalization, page_rank_personalization], axis=1, names=['diff', 'no_pers', 'pers'])
        # print (c, diff.sort_values(0,ascending=True), page_rank_personalization.sort_values(0,ascending=False))
        # continue

        output_dimensions = diff[ diff <= 0 ].dropna().T
        # print (diff)

        # If predicted column is in the set - remove it
        # Normally the predicted column should be the first column in this set, so this is just a precaution. As we will add this column back in next step.
        output_dimensions = list(output_dimensions.drop([c,], axis=1).columns.values)
        output_dimensions.insert(0,c)
        # print ("======",c)
        # print (output_dimensions)
        # continue

        mname = "LinkAnalysisA_%s(select_automatic)"%(graph_type)
        out_fname = get_filename_from_method(fname, c, mname, prefix=output_directory)

        df_out.meta_header['predict']=[c,]
        df_out.meta_header['method']=[mname]
        write_csv_with_metadata(df_out[output_dimensions], out_fname)

if __name__ == '__main__':

    fname, output_directory = parse_selection_arguments(sys.argv)

    # Search for Adj-matrix for TS file in data folder
    fname_base = path.basename(fname).split(".")[0]
    fname_dir = path.dirname(fname)

    output_directory_pre_selection = output_directory.replace("selection", "pre_selection")

    for graph_type in ['te_graph', 'granger_graph']:
        fname_graph = output_directory_pre_selection + "/" + fname_base + "_" + graph_type + ".csv"
        print (graph_type)
        link_analysis(fname_graph, graph_type)


