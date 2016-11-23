#library(forecast)
library(cluster)
library(tsDyn)
#library(NNVar)
library(lmtest)
#library(clue)
library(vars)
library(stats) ##hclus

library(fpc)  ## for pamkCBI : pam with no k
#library (hydroGOF)
#library(flexclust) #kmeans
#library(sna)
#require(kernlab)

source("evaluation.R")
source("gsm.R")
args = commandArgs(trailingOnly=TRUE)

dataname = args[1]
matrixname = args[2]
targetIndex = strtoi (args[3])

dataname = "ts6.csv"
matrixname = "result128.csv"
targetIndex = strtoi ("1")
######### work directory
setwd("/Users/youssef/Documents/python/causality")

###### Initialisations
lags = c()
data = read.csv (paste0("data/",dataname), header = FALSE, dec = '.',sep=";")
matrix = read.csv(matrixname, header = TRUE, dec = '.',sep = ";")
matrix[,1] = NULL

############# Matrice des causalités
selectKc = data.frame()

### GSM feature selection method
GSM = fgsm (data, matrix, targetIndex, 10)

# Univariate feature selection method (machine learning paper)
causSelect = naiveSelection (matrix, targetIndex, 0.6)
selectKc = data [,causSelect]

path1 = paste0('results/','/GSM.csv')
path2 = paste0('results/','/selectKc.csv')

GSM = data.frame (data[,targetIndex], GSM)
selectKc = data.frame (data[,targetIndex], selectKc)
## Store the files that contains the selected variables
write.table(GSM, file = path1 ,row.names = FALSE, na = "",col.names = FALSE, sep = ";")
write.table(selectKc, file = path2,row.names = FALSE, na = "",col.names = FALSE, sep = ";")


