# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)


library(vars)
library(parallel)
library(NNVar) #varnnet module

source("../tools/read_meta_data.R")

#### varnn neural network model
varnn <- function (F,p, dec, cible)
{
    G = F[1:(nrow(F) - (dec)),]
    nb_layers = as.integer(((ncol(G)+1) * p* (2 / 3)))
    hiddenLayers = c(nb_layers,nb_layers,nb_layers)
    module = vnnet(G, p, 1, hiddenLayers, 1000)
    result = data.frame()
    ts = data.frame()
    #inv_dec = nrow(F)-dec
    for (ind in 1:dec)
    {
        ts = F[ind:(nrow(F) - dec + ind-1),]
        
        y = module$forecast(ts)
        
        result[ind,1] = y[length(y)]
        
        iter = 1
        
        while (iter < 2)
        {
            module$learn (F[(nrow(F) - dec + ind-1):(nrow(F) - dec + ind),])
            #module$learn (F[1:(nrow(F) - dec + ind),])
            iter = iter + 1
        }
    }

    return (result)
}

##### prediction function
predictbase <- function (method_name, prefix_out){

    data_name = strsplit(method_name, "/")
    command = paste0 ('awk \'BEGIN{printf("# predict_model; VARNN\\n");} /^#/\' ', method_name)
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
    
    preds = varnn(fs_method, p, nbrePreds,1)


if (nrow (preds) > 0){
    output_dir = paste0(prefix_out,"VARNN_",data_name[[1]][length(data_name[[1]])])
    system(paste0(command,' > ', output_dir))
    write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
}
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])

no_cores <- detectCores()

mclapply(1:(length(args)-1), function(i) try(predictbase(args[i], args[largs])), mc.cores=no_cores, mc.preschedule = FALSE)

