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
    command = paste0 ('awk \'BEGIN{printf("# predict_model;ARIMA\\n");} /^#/\' ', method_name)
    dat <- system(command,  intern = TRUE)
    data_name = strsplit(method_name, "/")
    
    datNamed <- read.table(text=gsub("^# *", "",dat), row.names = 1, sep=";",header=FALSE)
    
    lag_p = strtoi(datNamed["lag_p","V2"])
    horizon = strtoi(datNamed["horizon","V2"])
    nbre_predictions = strtoi(datNamed["number_predictions","V2"])
    
    dat <- strsplit(dat, ";")
    
    target_names = toString(datNamed["predict","V2"])
    
    target_names = strsplit(target_names, ',')[[1]]

    data      = read.csv (method_name, comment.char = "#", header=TRUE, sep=";")
    colnames = colnames(data)
    normalized_data = normalize(data)

    for (i in 1:length(target_names)) {
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
        

        #determine the lag parameter
        if (lag_p == 0){
            lagMax = as.integer ((nrow(data)  - 1)  / 4)
        }
        else lagMax = lag_p

        ## determmine the number of predictions
        nbrePreds = as.integer(nrow(normalized_data) * 10 / 100) # 10% predictions of the size of the data

        ## compute predictions
        tryCatch({
        preds = auto_arima_prediction (normalized_data[,target_index],lagMax, nbrePreds,horizon)
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
        ####

#names(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
#colnames(preds) = c("t+1", "t+2", "t+3", "t+4", "t+5")
        preds = denormalize(preds,max,min)
        write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
    }
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])
try(predictbase(args[1],args[2]))

