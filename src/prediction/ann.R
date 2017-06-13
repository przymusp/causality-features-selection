# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)


library(vars)
library(parallel)
library(NNVar) # local package

source("../tools/read_meta_data.R")

#### varnn neural network model
varnn_rol <- function (F,p, nb_preds, horizon)
{
    #F = data.frame (F[,])
    G = F[1:(nrow(F) - (nb_preds - 1) - horizon),]
    nb_neurones = as.integer (((ncol(G) * p) + 1) * (2 / 3))

    hiddenLayers = rep (nb_neurones, 3)
    module = varnn(G, 9, hiddenLayers,1000000, bias = TRUE, nrow(G))
    #module$fit (G, 10, 10000, nrow(G))
    
    result = data.frame()
    ts = data.frame()
    #inv_dec = nrow(F)-dec
    for (ind in 1:nb_preds)
    {
        #ts = F[ind:(nrow(F) - (nb_preds - ind) - horizon),]
        
        #y = module$forecast(ts)
        
        #print (y)
        
        for (inh in 1 : horizon)
        {
            ts = F[ind:(nrow(F) - (nb_preds - ind) - horizon + inh),]
            y = module$forecast(ts)
            result[ind,inh] = y[nrow(y),1]
        }
        
        iter = 1
        
        while (iter < 1000)
        {
            #module$learn (F[(nrow(F) - dec + ind-1):(nrow(F) - dec + ind),])
            train = data.frame ()
            train = F[ind:(nrow(F) - (nb_preds - ind) - horizon + 1),]
            module$train (train,nrow(train))
            iter = iter + 1
        }
    }
    print (result)
    return (result)
}

##### prediction function
predictbase <- function (method_name, prefix_out){

    data_name = strsplit(method_name, "/")
    command = paste0 ('awk \'BEGIN{printf("# predict_model; Varnn\\n");} /^#/\' ', method_name)
    meta_data = read_meta_data(method_name)
    
    
    # print (horizon)
    if (is.na(meta_data$horizon))
        meta_data$horizon = 1
    
    if(is.na(meta_data$lag_p))
        meta_data$lag_p = 0
    
    if(is.na(meta_data$nbre_predictions))
        meta_data$nbre_predictions = 0

    fs_method      = read.csv (paste0(method_name), comment.char = "#", header=TRUE, sep=";")

    # determine the lag parameter
    if (meta_data$lag_p == 0){
        lagMax = as.integer ((nrow(fs_method)  - 1)  / (2 * (ncol(fs_method) + 1)))
    }
    else lagMax = meta_data$lag_p
   
    var = VARselect(fs_method,lag.max=lagMax)
    p = var$selection[1] ## AIC criteria
 

    ###  Prediction
    if (meta_data$nbre_predictions == 0)
        nbrePreds = as.integer(nrow(fs_method) * 10 / 100)
    else nbrePreds = meta_data$nbre_predictions
    
    preds = varnn_rol(fs_method, lagMax, nbrePreds,meta_data$horizon)
    
    print (paste("############"))

if (nrow (preds) > 0){
    output_dir = paste0(prefix_out,"Varnn_",data_name[[1]][length(data_name[[1]])])
    system(paste0(command,' > ', output_dir))
    write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
}
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])

no_cores <- detectCores()


mclapply(1:(length(args)-1), function(i) try(predictbase(args[i], args[largs])), mc.cores=no_cores, mc.preschedule = FALSE)

