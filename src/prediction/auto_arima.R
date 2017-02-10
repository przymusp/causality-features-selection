# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)

## Prediction using the auto.arima model


library(tsDyn)
library(lmtest)
library(vars)
library(forecast)

source("../tools/prediction_tools.R")

predictbase <- function (method_name, prefix_out){
    command = paste0 ('awk \' /^# *predict/ \' ',method_name)
    dat <- system(command,  intern = TRUE)
    dat <- strsplit(dat, ";")
    data_name = strsplit(method_name, "/")

    dat[[1]] = gsub(" ", "", dat[[1]], fixed = TRUE)
    dat[[1]] = gsub("\r", "", dat[[1]], fixed = TRUE)
    dat[[1]] = gsub("\n", "", dat[[1]], fixed = TRUE)

    target_names = c(dat[[1]])

    data      = read.csv (method_name, comment.char = "#", header=TRUE, sep=";")
    colnames = colnames(data)

    for (i in 2:length(target_names)) {
        target_name = target_names[i]
        for(j in 1:length(colnames)) {
            if (colnames[j] == target_name) {
                target_index = j
                break;
            }
        }
        output_dir = paste0(prefix_out,"Auto.Arima_",target_name,"_",data_name[[1]][length(data_name[[1]])])
        #system(paste0(command,' > ', output_dir))
        # Bref description of the file
        command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',method_name)
        system(paste0(command,' > ', output_dir))
        cat ("# predict;", file=output_dir,append=TRUE)
        cat (target_name, file=output_dir,append=TRUE, sep='\n')
        cat ("# method; Auto.Arima()",file=output_dir,append=TRUE, sep='\n')
        cat ("# predict_model; Univariate_model",file=output_dir,append=TRUE, sep='\n')

        ### normalisation
        max = max(data[,target_index])
        min = min(data[,target_index])
        fs_method = normalize(data)

        #determine the lag parameter
        lagMax = as.integer ((nrow(fs_method)  - 1)  / 4)

        ## determmine the number of predictions
        nbrePreds = as.integer(nrow(fs_method) * 10 / 100) # 10% predictions of the size of the data

        ## detect the order of stationarity
        #x = fs_method[,target_index]
        #nd = ndiffs(x,alpha=0.05,test="adf");
        preds = auto_arima_prediction (fs_method[,target_index],lagMax, nbrePreds)
        ####

        names(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
        colnames(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
        preds = denormalize(preds,max,min)
        write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
    }
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])
try(predictbase(args[1],args[2]))

