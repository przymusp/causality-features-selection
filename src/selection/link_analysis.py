from __future__ import print_function
import networkx as nx

import numpy as np
import collections as col
import matplotlib.pylab as plt
import pandas as pd

if __name__ == '__main__':

    fname, output_directory = parse_selection_arguments(sys.argv)
    df = read_csv_and_metadata(fname)


    exit()

data = pd.read_csv("result128.txt", delimiter=";", usecols=range(1,129))
data = data / data.sum(0)
# data[data<0.012]=0
# print np.sum(np.sum(data>0.013))
# exit(0)


# print data
# print data.sum(0)
# data[data<64/128]=0
# print data
# exit(0)

# plt.figure(num=None, figsize=(50, 50), dpi=100)
G = nx.DiGraph(data.as_matrix())
# p = dict.fromkeys(G, 0)
# p[10]=1
# pr = nx.pagerank(G, alpha=0.85, personalization=p)
# nx.draw_random(G, nodelist=pr.keys(), node_sizes=[v * 1000 for v in pr.values()])
# weights = [ d['weight'] * 100 for (u,v,d) in G.edges(data=True)]
# nx.draw_shell(G, edge_color=weights, edge_cmap=plt.get_cmap('terrain'), arrows=False)
# plt.savefig("graph.png")

# exit(0)
G.reverse()
for i in range(10):
    p = dict.fromkeys(G, 0)
    p[i]=1
    pr = nx.pagerank(G, alpha=0.85, personalization = p)
    result = pd.DataFrame.from_dict(pr, orient='index')
    print(i, result.sort_values(0, ascending = False))
