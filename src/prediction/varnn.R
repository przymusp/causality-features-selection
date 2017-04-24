# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)


library(vars)
library(parallel)
library(NNVar) #varnnet module



source("../tools/prediction_tools.R")

#### varnn neural network model
varnn <- function (F,p, dec, cible)
{
    G = F[1:(nrow(F) - (dec)),]
    nb_layers = as.integer(((ncol(G)+1) * p* (2 / 3)))
    hiddenLayers = c(nb_layers,nb_layers,nb_layers,nb_layers)
    module = vnnet(G, p, 1, hiddenLayers, 10000)
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

    command = paste0 ('awk \'BEGIN{printf("# predict_model; VARNN\\n");} /^#/\' ', method_name)
    dat <- system(command,  intern = TRUE)
    #dat <- strsplit(dat, ";")
    data_name = strsplit(method_name, "/")
    
    datNamed <- read.table(text=gsub("^# *", "",dat), row.names = 1, sep=";",header=FALSE)
    
    lag_p = strtoi(datNamed["lag_p","V2"])
    horizon = strtoi(datNamed["horizon","V2"])
    nbre_predictions = strtoi(datNamed["number_predictions","V2"])
    
    target_names = toString(datNamed["predict","V2"])
    
    target_names = strsplit(target_names, ',')[[1]]
    
    # print (horizon)
    if (is.na(horizon))
        horizon = 1
    
    if(is.na(lag_p))
        lag_p = 0
    
    if(is.na(nbre_predictions))
        nbre_predictions = 0


    output_dir = paste0(prefix_out,"VARNN_",data_name[[1]][length(data_name[[1]])])

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
        nbrePreds = as.integer(nrow(fs_method) * 10 / 100)
    else nbrePreds = nbre_predictions
    
    preds = varnn(fs_method, p, nbrePreds,1)
    #print (preds)


#names(preds) = c("t+1")
#colnames(preds) = c("t+1")
    #preds = denormalize(preds,max,min)

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

