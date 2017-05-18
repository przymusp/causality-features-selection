# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)

## Prediction using the ar model

library(tsDyn)
library(lmtest)
library(vars)
library(forecast)

source("../tools/prediction_tools.R")
source("../tools/read_meta_data.R")

predictbase <- function (method_name, prefix_out){
    data_name = strsplit(method_name, "/")
    command = paste0 ('awk \'BEGIN{printf("# predict_model;AR\\n");} /^#/\' ', method_name)
    meta_data = read_meta_data(method_name)

    if(is.na(meta_data$horizon))
    meta_data$horizon = 1

    if(is.na(meta_data$lag_p))
    meta_data$lag_p = 0

    if(is.na(meta_data$nbre_predictions))
    meta_data$nbre_predictions = 0


    # read data
    data      = read.csv (method_name, comment.char = "#", header=TRUE, sep=";")
    colnames = colnames(data)

    for (target_name in meta_data$target_names)
    {
        for(j in 1:length(colnames))
            if (colnames[j] == target_name) {
                target_index = j
                break;
            }
        output_dir = paste0(prefix_out,"Ar-Model_",target_name,"_",data_name[[1]][length(data_name[[1]])])

        # Bref description of the file
        command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',method_name)
        system(paste0(command,' > ', output_dir))
        cat ("# predict;", file=output_dir,append=TRUE)
        # print (target_name)
        cat (target_name, file=output_dir,append=TRUE, sep='\n')
        cat ("# method; AR_model()",file=output_dir,append=TRUE, sep='\n')
        cat ("# predict_model; Ar",file=output_dir,append=TRUE, sep='\n')

        # determine the lag parameter
        if (meta_data$lag_p == 0){
            lagMax = as.integer ((nrow(data)  - 1)  / 4)
        }
        else lagMax = meta_data$lag_p

        ## determmine the number of predictions
        if (meta_data$nbre_predictions == 0) # 10% predictions of the size of the data
            nbrePreds = as.integer(nrow(data) * 10 / 100)
        else nbrePreds = meta_data$nbre_predictions

        ## compute predictions
        tryCatch({
        preds = ar_prediction (data[,target_index], lagMax, nbrePreds,meta_data$horizon)
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
        # print (preds)

        write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
    }
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])
try(predictbase(args[1],args[2]))

