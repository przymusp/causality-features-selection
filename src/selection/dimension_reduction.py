# -*- coding: utf-8 -*-                                                                                                                                                                                              
import sklearn.decomposition as decomp                                                                                                                                                                               
import pandas as pd
import os
import re
from __future__ import print_function 

methods = [
  decomp.FactorAnalysis(n_components=4),
  decomp.NMF(n_components=4, init='nndsvda'),
  decomp.NMF(n_components=4, init='nndsvdar'),
  decomp.LatentDirichletAllocation(n_topics=4),
  decomp.KernelPCA(n_components=4, kernel="rbf", fit_inverse_transform=True),
  decomp.FastICA(n_components=4),
  decomp.IncrementalPCA(n_components=4),
  decomp.PCA(n_components=4)
]

for method in methods:
    print(method)

