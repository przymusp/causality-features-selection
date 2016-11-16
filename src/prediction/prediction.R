#library(forecast)
library(cluster)
library(tsDyn)
#library(rPython)
library(lmtest)

######### work directory
setwd("/Users/youssef/Documents/python/causality")


###### Initialisations
realData = data.frame()
realData = read.csv("data/ts6.csv", header=FALSE, sep=";")
realData = normalize(realData)

# The index of the target variable
indCible = 1
# The lag parametre of the prediction model
p = 100

### Dataframe used
gsm            = read.csv ("results/GSM.csv", header=FALSE, sep=";")
ufs            = read.csv ("results/selectKc.csv", header=FALSE, sep=";")
methods        = list (ufs, gsm,realData[,-indCible])
names(methods) = c('ufs','gsm','model')
target         =  realData[,indCible]

###  Prediction
gsm = normalize(gsm)
mse = evaluation(target, indCible, gsm, p)

#python.load("bar_chart.py")
