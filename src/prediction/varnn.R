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
    nb_layers = as.ineger(((ncol(G)+1) * p* (1 / 3)))
    hiddenLayers = c(nb_layers)
    module = vnnet(G, p, 1, hiddenLayers, 1000)
    result = data.frame()
    ts = data.frame()
    #inv_dec = nrow(F)-dec
    for (ind in 1:dec)
    {
        ts = F[1:(nrow(F) - dec + ind-1),]
        
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

    #prefix_out = '../../results/'
    #method_name = '../../results/selection/ebob-l_CAC40_FactorAnalysis_zNDaHNvy-OLDnRnMsdastMyoRq0=.csv'
    # print(method_name)
    # print(prefix_out)

    command = paste0 ('awk \'BEGIN{printf("# predict_model; VARNN\\n");} /^#/\' ', method_name)
    # print(command)
    dat <- system(command,  intern = TRUE)
    dat <- strsplit(dat, ";")
    data_name = strsplit(method_name, "/")


    output_dir = paste0(prefix_out,"VARNN_",data_name[[1]][length(data_name[[1]])])

    system(paste0(command,' > ', output_dir))

    ### normalisation
    fs_method      = read.csv (paste0(method_name), comment.char = "#", header=TRUE, sep=";")
    #max = max(fs_method[,1])
    #min = min(fs_method[,1])
    #fs_method = normalize(fs_method)

    # determine the lag parameter
    lagMax = as.integer ((nrow(fs_method)  - 1)  / (2*(ncol(fs_method) + 1)))
    var = VARselect(fs_method,lag.max=lagMax)
    p = var$selection[1] ## AIC criteria
 

    ###  Prediction
    nbrePreds = as.integer(nrow(fs_method) * 10 / 100) # 10% predictions of the size of the data
    preds = varnn(fs_method, p, nbrePreds,1)
    #print (preds)


    names(preds) = c("t+1")
    colnames(preds) = c("t+1")
    #preds = denormalize(preds,max,min)

    write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])

#Calculate the number of cores
no_cores <- detectCores()

# Initiate cluster
# cl <- makeCluster(no_cores, type='FORK')

# parLapply(cl, 1:(length(args)-1), function(i) try(predictbase(args[i], args[largs])))
mclapply(1:(length(args)-1), function(i) try(predictbase(args[i], args[largs])), mc.cores=no_cores, mc.preschedule = FALSE)

# # file to predict
# method_name = args[1]

# # output directory
# prefix_out=args[2]

# predictbase(method_name, prefix_out)
