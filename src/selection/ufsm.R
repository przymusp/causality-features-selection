
library(cluster)
library(tsDyn)
library(lmtest)
library(vars)
library(stats) ##hclus


#### SELECTKBEST based on causality
naiveSelection <- function (F, targetIndex, threshold, lag_max)
{
  results = c()
  naiveClasse = c()
  ind  = 1
  p = 1
  causalities = data.frame()
  
  for (j in 1:ncol(F))
  {
    var = VARselect(F,lag.max=lag_max)
    lag = var$selection[1]
    if (j != targetIndex) {
      tryCatch({
        test =   try (grangertest (data[,targetIndex] ~ data [,j], order = lag))
        test1 =   try (grangertest (data[,j] ~ data [,targetIndex], order = lag))
      }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
      
        if(test[1] == "Error in vc[ovar, ovar] : indice hors limites\n")
        {
          causalities[p,1] = 0
        } else {
                causality[p,1] = 1 - test$`Pr(>F)`[2]
                causalities[p,1] = 1 - test$`Pr(>F)`[2]
        }
      if(test1[1] == "Error in vc[ovar, ovar] : indice hors limites\n")
      {
        causalities[p,2] = 0
      } else {
        causality[p,2] = 1 - test$`Pr(>F)`[2]
        causalities[p,2] = 1 - test$`Pr(>F)`[2]
      }
      causalities[p,3] = j
      p = p+1
    }
  }

  for (i in 1:ncol(causalities))
  {  
      if (causalities[i,1] >= threshold && causalities[i,2] < threshold)
      {
        results[i] = causalities[i,3]
      }
  }
  return (results)
}
##### Read arguments
args = commandArgs(trailingOnly=TRUE)

if (length(arg) > 3)
  print ("Error: number of arguments incorrect.")
  quit()

data_dir = args[1]
output_dir = paste0(args[2],"/")
target_name = args[3] #strtoi (args[3])

###### Initialisations
command = paste0 ('awk /^#/ ',data_dir)
dat <- system(command,  intern = TRUE)
dat <- strsplit(dat, ";")
file_name_split = strsplit(data_dir, "/")
data_name = data

data = read.csv (data_dir, header = TRUE, dec = '.',sep=";")

colnames = colnames(data)
for(j in 1:length(colnames))
{
  if (colnames[j] == target_name)
  {
    target_index = j
    break;
  }
}
############# Matrice des causalités
selectKc = data.frame()

# Univariate feature selection method (machine learning paper)
causSelect = naiveSelection (matrix, target_index, 0.2)
causSelect
paste0(data_name,"_",target_name,"_",)
#selectKc = data [,causSelect]
##selectKc = data.frame (data[,target_index], selectKc)

## Store the files that contains the selected variables
write.table(selectKc, file = path2,row.names = FALSE, na = "",col.names = FALSE, sep = ";")


