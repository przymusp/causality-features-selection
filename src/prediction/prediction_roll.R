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

source("../tools/prediction_tools.R")

predictbase <- function (method_name, prefix_out){

  #prefix_out = '../../results/'
  #method_name = '../../results/selection/ebob-l_CAC40_FactorAnalysis_zNDaHNvy-OLDnRnMsdastMyoRq0=.csv'
  print(method_name)
  # print(prefix_out)

  command = paste0 ('awk /^#/ ',method_name)
  dat = system(command,  intern = TRUE)
  dat = strsplit(dat, "\r")
  predict = as.character (dat[[1]][1])
  name_pref = as.character (dat[[1]][2])
  description = as.character (dat[[1]][3])

  target_name = strsplit(predict, ";")[[1]][2]
  data_name = strsplit(name_pref, ";")[[1]][2]
  target_name = gsub(" ", "", target_name, fixed = TRUE)
  data_name = gsub(" ", "", data_name, fixed = TRUE)

  selection_method_name = strsplit(method_name, "/")[[1]]
  selection_method_name = selection_method_name[length(selection_method_name)]
  selection_method_name = gsub(".csv", "", selection_method_name, fixed = TRUE)


  #output_dir = paste0(prefix_out,data_name,"_",target_name,"_","VECModel.csv")
  output_dir = paste0(prefix_out,selection_method_name,"_VECModel_rolling.csv")

  #system(paste0(command,' > ', output_dir))
  header = paste0(predict,"\r",name_pref,"\r", description,"\r# method; VECModel_rolling\r")
  writeLines (header,output_dir)

  ### normalisation
  fs_method      = read.csv (paste0(method_name), comment.char = "#", header=TRUE, sep=";")
  max = max(fs_method[,1])
  min = min(fs_method[,1])
  fs_method = normalize(fs_method)
  
  #determine the lag parameter
  lagMax = 100
  var = VARselect(fs_method,lag.max=lagMax)
  p = var$selection[1] ## AIC criteria

  ###  Prediction
  nbrePreds = as.integer(nrow(fs_method) * 10 / 100) # 10% predictions of the size of the data
  mod_vecm = VECM(fs_method, lag=p)
  preds_roll = predict_rolling(mod_vecm,n.ahead = 1, nroll=nbrePreds)
  preds = data.frame(c(preds_roll$pred[,1]),c(preds_roll$true[,1]))  
  ####

  names(preds) = c("predictions","reals")
  colnames(preds) = c("predictions","reals")
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
