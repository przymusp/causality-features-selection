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
library (crayon) #print with colors

source("../tools/prediction_tools.R")

predictbase <- function (method_name, prefix_out){

    command = paste0 ('awk \'BEGIN{printf("# predict_model; VECM_rolling\\n");} /^#/\' ', method_name)
    dat <- system(command,  intern = TRUE)
    data_name = strsplit(method_name, "/")

    datNamed <- read.table(text=gsub("^# *", "",dat), row.names = 1, sep=";",header=FALSE)

    lag_p = strtoi(datNamed["lag_p","V2"])
    horizon = strtoi(datNamed["horizon","V2"])
    nbre_predictions = strtoi(datNamed["number_predictions","V2"])

    dat <- strsplit(dat, ";")

    target_names = toString(datNamed["predict","V2"])

    target_names = strsplit(target_names, ',')[[1]]
    
    if(is.na(horizon))
    horizon = 1

    if(is.na(lag_p))
    lag_p = 0
    
    if(is.na(nbre_predictions))
    nbre_predictions = 0


    output_dir = paste0(prefix_out,"VECM_rolling",data_name[[1]][length(data_name[[1]])])

    system(paste0(command,' > ', output_dir))

    ### normalisation
    fs_method      = read.csv (paste0(method_name), comment.char = "#", header=TRUE, sep=";")
    #max = max(fs_method[,1])
    #min = min(fs_method[,1])
    #fs_method = normalize(fs_method)

    # determine the lag parameter
    
    if (lag_p == 0){
        lagMax = as.integer ((nrow(fs_method)  - 1)  / (2 * (ncol(fs_method) + 1)))
    }
    else lagMax = lag_p
    
    var = VARselect(fs_method,lag.max=lagMax)
    p = var$selection[1] ## AIC criteria

    ###  Prediction
    if (nbre_predictions == 0)
        nbrePreds = as.integer(nrow(fs_method) * 10 / 100) # 10% predictions of the size of the data
    else nbrePreds = nbre_predictions
    #nbrePreds = 5
    preds = vecm_rolling(fs_method, p, nbrePreds, horizon)
    #print (preds)

#names(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
#colnames(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
#preds = denormalize(preds,max,min)

    write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])

no_cores <- detectCores()

mclapply(1:(length(args)-1), function(i) try(predictbase(args[i], args[largs])), mc.cores=no_cores, mc.preschedule = FALSE)

