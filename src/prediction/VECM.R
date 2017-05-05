# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)

library(tsDyn)
library(lmtest)
library(vars)
library(parallel)

source("../tools/prediction_tools.R")
source("../tools/read_meta_data.R")

vecm_rolling <- function (ts, p, nb_preds, horizon)
{
    # ts: multivariate time series to predict the first attribut
    # p: the lag parameter
    # nb_preds: number points to predict
    
    training_ts = ts
    
    results = data.frame ()
    target = training_ts[,1]
    #training_ts[,1] = NULL
    #print (ts)
    pred = data.frame()
    
    for (ind in 1:nb_preds)
    {
        mthds = training_ts[ind:(nrow(training_ts) - (nb_preds-ind) - horizon),]
        real = target[(length(target)- (nb_preds-ind) - horizon + 1):(length(target) - (nb_preds-ind))]
        
        ####### Apply the VECM model
        tryCatch({
            model = VECM (data.frame(mthds), p, include = c("const"), estim = c("ML"))
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
        y = predict(model,n.ahead = horizon)
        
        for (inh in 1 : horizon)
        pred[ind,inh] = y[inh,1]
    }
    
    return (pred)
}


predictbase <- function (method_name, prefix_out){


    data_name = strsplit(method_name, "/")
    
    command = paste0 ('awk \' BEGIN{printf("# predict_model; VECM-rolling\\n");}/^#/ \' ',method_name)
    meta_data = read_meta_data(method_name)

    ### normalisation
    fs_method      = read.csv (paste0(method_name), comment.char = "#", header=TRUE, sep=";")

    # determine the lag parameter
    
    if (meta_data$lag_p == 0){
        lagMax = as.integer ((nrow(fs_method)  - 1)  / (2 * (ncol(fs_method) + 1)))
    }
    else lagMax = meta_data$lag_p
    
    var = VARselect(fs_method,lag.max=lagMax)
    p = var$selection[1] ## AIC criteria

    ###  Prediction
    preds = data.frame()
    if (meta_data$nbre_predictions == 0)
        nbrePreds = as.integer(nrow(fs_method) * 10 / 100) # 10% predictions of the size of the data
    else nbrePreds = meta_data$nbre_predictions

    preds = vecm_rolling(fs_method, p, nbrePreds, meta_data$horizon)

    if (nrow (preds) > 0){
        output_dir = paste0(prefix_out,"VECM_rolling",data_name[[1]][length(data_name[[1]])])
        system(paste0(command,' > ', output_dir))
        write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
      }
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])

no_cores <- detectCores()

mclapply(1:(length(args)-1), function(i) try(predictbase(args[i], args[largs])), mc.cores=no_cores, mc.preschedule = FALSE)

