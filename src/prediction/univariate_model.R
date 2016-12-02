# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)

## Prediction using the VECM model
## For each horizon forecats, 5 predictions can be made
## The model is built on normalized data
## 2 arguments are used : the name of the file of one f-selection method, and the output directory

#library(forecast)
library(tsDyn)
library(lmtest)
library(vars)
library(forecast)

source("../tools/prediction_tools.R")

predictbase <- function (method_name, prefix_out){

  #prefix_out = '../../results/'
  #method_name = '../../results/selection/ebob-l_CAC40_FactorAnalysis_zNDaHNvy-OLDnRnMsdastMyoRq0=.csv'
  print(method_name)
  # print(prefix_out)

  command = paste0 ('awk \' BEGIN{printf("# predict_model; ECM-rolling (univariate model)\\n");}/^#/ \' ',method_name)
  print(command)
  dat <- system(command,  intern = TRUE)
  dat <- strsplit(dat, ";")
  data_name = strsplit(method_name, "/")
  
  
  output_dir = paste0(prefix_out,"ECM_",data_name[[1]][length(data_name[[1]])])
  
  system(paste0(command,' > ', output_dir))
  ### normalisation
  fs_method      = read.csv (paste0(method_name), comment.char = "#", header=TRUE, sep=";")
  max = max(fs_method[,1])
  min = min(fs_method[,1])
  fs_method = normalize(fs_method)
  
  #determine the lag parameter
  lagMax = 100
  var = VARselect(fs_method[,1],fs_method[,-1],lag.max=lagMax)
  p = var$selection[1] ## AIC criteria

  ## determmine the number of predictions
  nbrePreds = as.integer(nrow(fs_method) * 10 / 100) # 10% predictions of the size of the data
  
  ## detect the order of stationarity
  x = fs_method[,1]
  nd = 0
  continue = TRUE
  while (continue)
  {
     ns = ndiffs (x,test="adf")
     if(ns == 0)
     {
         continue = FALSE
     }
     nd = nd + 1
  }
print (p)
preds = arima_prediction (fs_method[,1], 1, nd, nbrePreds)
print (preds)
  #preds_roll = predict_rolling(mod_vecm,n.ahead = 1, nroll=nbrePreds)
  #preds = data.frame(c(preds_roll$pred[,1]),c(preds_roll$true[,1])) 
  #preds = data.frame(c(preds_roll$pred[,1]))
  ####

  names(preds) = c("predictions")
  colnames(preds) = c("predictions")
  preds = denormalize(preds,max,min)
  write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])

for (i in 1:(length(args)-1)) {
  try(predictbase(args[i], args[largs]))
}

# # file to predict
# method_name = args[1]

# # output directory
# prefix_out=args[2]

# predictbase(method_name, prefix_out)
