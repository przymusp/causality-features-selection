# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)

# TODO: change input arguments from (files are passed as argv) to (glob pattern is passed by argument). This is important as for large number of selection files we exceed the permissible argv size.

## Prediction using the VECM model
## For each horizon forecats, 5 predictions can be made
## The model is built on normalized data
## 2 arguments are used : the name of the file of one f-selection method, and the output directory

#library(forecast)
library(tsDyn)
library(lmtest)
library(vars)
library(parallel)

source("../tools/prediction_tools.R")

predictbase <- function (method_name, prefix_out){

  command = paste0 ('awk \' BEGIN{printf("# predict_model; VECM-rolling\\n");}/^#/ \' ',method_name)
  dat <- system(command,  intern = TRUE)
  dat <- strsplit(dat, ";")
  data_name = strsplit(method_name, "/")
  
  # lag_p = strsplit(dat[[3]], ";")[[1]][2]
  # lag_p = strsplit(lag_p, '\r')[1]
  #lag_p = strtoi(lag_p)
  
  #if(is.na(lag_p))
  #lag_p = 0
  lag_p = 1

  output_dir = paste0(prefix_out,"VECM-rolling_",data_name[[1]][length(data_name[[1]])])
  system(paste0(command,' > ', output_dir))
  
  ### normalisation
  fs_method      = read.csv (paste0(method_name), comment.char = "#", header=TRUE, sep=";")
  max = max(fs_method[,1])
  min = min(fs_method[,1])
  fs_method = normalize(fs_method)

  print (lag_p)
  if (lag_p == 0){
      lagMax = as.integer ((nrow(fs_method)  - 1)  / (2 * (ncol(fs_method) + 1)))
  }
  else lagMax = lag_p
  
  #var = VARselect(fs_method,lag.max=lagMax)
  #p = var$selection[1] ## AIC criteria
  p = 1

  ###  Prediction
  nbrePreds = as.integer(nrow(fs_method) * 10 / 100) # 10% predictions of the size of the data
  mod_vecm = VECM(fs_method[1:(nrow(fs_method)-nbrePreds),], lag = p, include = "const", estim = c("ML"))
  #mod_vecm = VAR(fs_method[1:(nrow(fs_method)),], lag = p)
  preds_roll = predict_rolling(mod_vecm, nroll=nbrePreds,n.ahead = 4)#, refit.every = 1)
  print (preds_roll)
  #preds = data.frame(c(preds_roll$pred[,1]))
  #preds = data.frame(c(preds_roll$pred))
  #print (preds)
  ####

#names(preds) = c("t+1", "t+2", "t+3", "t+4")
#colnames(preds) = c("t+1", "t+2", "t+3", "t+4")
#preds = denormalize(preds,max,min)
#write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])

#Calculate the number of cores
no_cores <- detectCores()

mclapply(1:(length(args)-1), function(i) try(predictbase(args[i], args[largs])), mc.cores=no_cores, mc.preschedule = FALSE)


# # file to predict
# method_name = args[1]

# # output directory
# prefix_out=args[2]

# predictbase(method_name, prefix_out)
