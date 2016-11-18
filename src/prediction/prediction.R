## Prediction using the VECM model
## For each horizon forecats, 5 predictions can be made
## The model is built on normalized data
## 2 arguments are used : the name the file of one f-selection method

library(forecast)
library(cluster)
library(tsDyn)
library(lmtest)

######### work directory
setwd("/Users/youssef/Documents/python/causality")
source("evaluation.R")
args = commandArgs(trailingOnly=TRUE)
method_name = args[1]

# let's take 100 for instance
p = 100

### normalisation
fs_method      = read.csv (paste0("results/",method_name), header=FALSE, sep=";")
fs_method = normalize(fs_method)

###  Prediction
nbrePreds = 10
preds = evaluation(fs_method, p, 10)
for (i in 1:length(preds))
names(preds[[i]]) = c("predictions", "real_values")
preds
#path = paste0('results/','predictions_',method_name)
#write.table(selectKc, file = path,row.names = FALSE, na = "",col.names = FALSE, sep = ";")

