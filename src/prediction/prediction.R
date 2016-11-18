## Prediction using the VECM model
## For each horizon forecats, 5 predictions can be made
## The model is built on normalized data
## 2 arguments are used : the name the file of one f-selection method

library(forecast)
library(cluster)
library(tsDyn)
library(lmtest)

######### work directory
#setwd("/Users/youssef/Documents/python/causality")
source("evaluation.R")
args = commandArgs(trailingOnly=TRUE)
method_name = args[1]

#method_name = "GSM.csv"
 # Example of the lag parametre of the prediction model
p = 100
### normalisation
fs_method      = read.csv (paste0(method_name), header=FALSE, sep=";")
fs_method = normalize(fs_method)
###  Prediction
nbrePreds = 10
preds = evaluation(fs_method, p, nbrePreds)

names(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
preds

write.table(preds, file = paste0(method_name, "-predictions"),row.names = FALSE, na = "",col.names = FALSE, sep = ";")

