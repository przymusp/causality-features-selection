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
prefix_out=args[2]

command = paste0 ('awk /^#/ ',method_name)
dat <- system(command,  intern = TRUE)
dat <- strsplit(dat, ";")
data_name = strsplit(method_name, "/")

output_dir = paste0(prefix_out,data_name[[1]][length(data_name[[1]])])

dat <-system( paste0( method_name,' >', output_dir))



 # Example of the lag parametre of the prediction model
p = 100
### normalisation
fs_method      = read.csv (paste0(method_name), comment.char = "#", header=FALSE, sep=";")
fs_method = normalize(fs_method)
###  Prediction
nbrePreds = 10
preds = evaluation(fs_method, p, nbrePreds)

names(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
preds

write.table(preds, file = fname,row.names = FALSE, na = "",col.names = FALSE, sep = ";",append = TRUE)

