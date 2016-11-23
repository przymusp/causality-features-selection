library(tsDyn)
library(lmtest)
library(vars)
library(stats) ##hclus


#### SELECTKBEST based on causality
naiveSelection <- function (F, targetIndex, threshold, lag_max)
{
  results = c()
  naiveClasse = c()
  p = 1
  causalities = data.frame()
  
  for (j in 1:ncol(F))
  {
   # var = VARselect(F,lag.max=lag_max)
    #lag = var$selection[1]
    lag = lag_max
    if (j != targetIndex) {
      tryCatch({
              test = try (grangertest (F[,targetIndex] ~ F[,j], order = lag))
              test1 = try (  grangertest (F[,j] ~ F[,targetIndex], order = lag))
              if(test[1] == "Error in vc[ovar, ovar] : indice hors limites\n")
              {
                    causalities[p,1] = 0
              } else {
                     # causality[p,1] = 1 - test$`Pr(>F)`[2]
                      causalities[p,1] = 1 - test$`Pr(>F)`[2]
              }
      
              if(test1[1] == "Error in vc[ovar, ovar] : indice hors limites\n")
                {
                  causalities[p,2] = 0
                } else {
                        #causality[p,2] = 1 - test1$`Pr(>F)`[2]
                        causalities[p,2] = 1 - test1$`Pr(>F)`[2]
                        }
              }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})

      causalities[p,3] = j
      p = p+1
    }
  }

  p = 1
   for (i in 1:nrow(causalities))
   {  
       if (causalities[i,1] >= threshold && causalities[i,2] < threshold)
       {
         results[p] = causalities[i,3]
         p = p + 1
       }
   }
  return (results)
  #return (causalities)
}
##### Read arguments
args = commandArgs(trailingOnly=TRUE)

if (length(args) > 2){
  print ("Error: number of arguments incorrect.")
  quit()
}

data_dir = args[1]
output_dir = paste0(args[2],"/")
#data_dir = "../../data/ebob-l.csv"
###### Initialisations
command = paste0 ('awk /^#/ ',data_dir)
dat <- system(command,  intern = TRUE)
description = dat[[2]]
dat <- strsplit(dat, ";")
file_name_split = strsplit(data_dir, "/")[[1]]
data_name = file_name_split[length(file_name_split)]
data_name = gsub(".csv", "",data_name, fixed=TRUE)

dat[[3]] = gsub(" ", "", dat[[3]], fixed = TRUE)
dat[[3]] = gsub("\r", "", dat[[3]], fixed = TRUE)

target_names = c(dat[[3]])

## read the dataset
data = read.csv(data_dir, header = TRUE, dec = '.',sep=";", comment.char = "#")
colnames = colnames(data)

## Feature selection for each target
for (i in 2:length(target_names)) {
    target_name = target_names[i]
    target_name
    for(j in 1:length(colnames)) {
        if (colnames[j] == target_name) {
            target_index = j
            break;
        }
    }
    ############# Matrice des causalités
    selectKc = data.frame()

    # Apply the Univariate feature selection method (machine learning paper)
    causSelect = naiveSelection (data, target_index, 0.9, 20)
    out_dir = paste0(output_dir,data_name,"_",target_name,"_","UFSM.csv")
    selectKc = data [,causSelect]
    selectKc = data.frame (data[,target_name], selectKc)
    colnames(selectKc) = c(target_name,colnames[causSelect])

    # Bref description of the file
    system(paste0(command,' > ', out_dir))
    header = paste0("#Predict;",target_name,"\r","#name_prefix;", data_name,"\r", description,"#method; Univariate selection method")
    writeLines (header,out_dir)
    
    ## Store the files that contains the selected variables
    write.table(selectKc, out_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";", append = TRUE)
}
