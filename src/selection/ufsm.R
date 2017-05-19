library(tsDyn)
library(lmtest)
library(vars)
library(stats) ##hclus

source("../tools/read_meta_data.R")

#### SELECTKBEST based on causality
naiveSelection <- function (F, targetIndex, matrix, threshold, lag_max)
{
  results = c()
  #naiveClasse = c()
  #p = 1
  #causalities = data.frame()

#for (j in 1:ncol(F))
#{
   # var = VARselect(F,lag.max=lag_max)
    #lag = var$selection[1]
    #lag = lag_max
    #if (j != targetIndex) {
    # tryCatch({
    #         test = try (grangertest (F[,targetIndex] ~ F[,j], order = lag))
    #         test1 = try (  grangertest (F[,j] ~ F[,targetIndex], order = lag))
    #         if(test[1] == "Error in vc[ovar, ovar] : indice hors limites\n")
    #         {
    #               causalities[p,1] = 0
    #         } else {
    #                # causality[p,1] = 1 - test$`Pr(>F)`[2]
    #                 causalities[p,1] = 1 - test$`Pr(>F)`[2]
    #         }

    #         if(test1[1] == "Error in vc[ovar, ovar] : indice hors limites\n")
    #               {
    #                 causalities[p,2] = 0
    #               } else {
    #                       #causality[p,2] = 1 - test1$`Pr(>F)`[2]
    #                       causalities[p,2] = 1 - test1$`Pr(>F)`[2]
    #                       }
    #             }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})

    #     causalities[p,3] = j
    #     p = p+1
    #   }
    # }

   j = 1
   for (i in 1:ncol(matrix))
   {
       if (i != targetIndex && matrix[i,targetIndex] >= threshold && matrix[targetIndex,i] < threshold)
        {
            results[j] = i
            j = j + 1
        }
   }
  return (results)
}
##### Read arguments
args = commandArgs(trailingOnly=TRUE)

if (length(args) > 2){
  print ("Error: number of arguments incorrect.")
  quit()
}

data_dir = args[1]
output_dir = paste0(args[2],"/")

###### Initialisations
meta_data = read_meta_data(data_dir)

## read the dataset
data = read.csv(data_dir, header = TRUE, dec = '.',sep=";", comment.char = "#")
colnames = colnames(data)

graph_dir = paste0("../../results/pre_selection/",meta_data$data_name,"/granger_graph.csv")
matrix = read.table(graph_dir, header = TRUE,row.names = 1, dec = '.',sep=";", comment.char = "#")

## Feature selection for each target
for (target_name in meta_data$target_names)
{
    for(j in 1:length(colnames))
        if (colnames[j] == target_name) {
            target_index = j
            break;
        }

    selectKc = data.frame()

    # Apply the Univariate feature selection method (machine learning paper)
    causSelect = naiveSelection (data, target_index,matrix, 0.9, meta_data$lag_p)
    out_dir = paste0(output_dir,target_name,"_","UFSM.csv")
    selectKc = data [,causSelect]
    selectKc = data.frame (data[,target_name], selectKc)
    colnames(selectKc) = c(target_name,colnames[causSelect])

    # Output Metadata
    command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',data_dir)
    system(paste0(command,' > ', out_dir))
    cat ("# predict;", file=out_dir,append=TRUE)
    cat (target_name, file=out_dir,append=TRUE, sep='\n')
    cat ("# method; UFSM (Univariate feature selection method)",file=out_dir,append=TRUE, sep='\n')

    ## Store the results
    write.table(selectKc, out_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";", append = TRUE)
}
