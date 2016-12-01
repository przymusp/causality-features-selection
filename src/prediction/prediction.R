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

    command = paste0 ('awk \' BEGIN{printf("# predict_model; VECM\\n");}/^#/ \' ',method_name)
    # print(command)
    dat <- system(command,  intern = TRUE)
    dat <- strsplit(dat, ";")
    data_name = strsplit(method_name, "/")


    output_dir = paste0(prefix_out,"predictions_",data_name[[1]][length(data_name[[1]])])

    system(paste0(command,' > ', output_dir))

    ### normalisation
    fs_method      = read.csv (paste0(method_name), comment.char = "#", header=TRUE, sep=";")
    max = max(fs_method[,1])
    min = min(fs_method[,1])
    fs_method = normalize(fs_method)

    # determine the lag parameter
    lagMax = 100
    var = VARselect(fs_method,lag.max=lagMax)
    p = var$selection[1] ## AIC criteria
    print(p)

    ###  Prediction
    percPreds = 10 # 10% predictions of the size of the data
    preds = vec_prediction(fs_method, p, percPreds)
    preds

    names(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
    colnames(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
    preds = denormalize(preds,max,min)
    preds

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
