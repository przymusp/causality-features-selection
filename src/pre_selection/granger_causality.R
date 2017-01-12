#library(lmtest)
library(vars)

### arguments
args = commandArgs(trailingOnly=TRUE)

if (length(args) > 2){
    print ("Error: number of arguments incorrect.")
    quit()
}

# dataset directory
data_dir = args[1]

# output directory
output_dir = args[2]
if( substr(output_dir, nchar(output_dir),nchar(output_dir)) != '/')
    output_dir = paste0(output_dir,'/')

# read data
data = read.csv(data_dir, header=TRUE, dec='.',sep=";",comment.char = "#")

# read some informations
command = paste0 ('awk /^#/ ',data_dir)
dat <- system(command,  intern = TRUE)
description = dat[[2]]
dat <- strsplit(dat, ";")
file_name_split = strsplit(data_dir, "/")[[1]]
data_name = file_name_split[length(file_name_split)]
data_name = gsub(".csv", "",data_name, fixed=TRUE)

# construct the output directory+name
output_dir = paste0(output_dir,data_name,"_","granger_graph.csv")
system(paste0(command,' > ', output_dir))

# data = normalize(data)

#### calculate the matrix
gMat = matrix(nrow=ncol(data), ncol=ncol(data))
for (i in 1:ncol(data))
{
  for (j in 1:ncol(data))
  {
    lagMax = as.integer ((nrow(data)  - 1)  / (2*(ncol(data) + 1)))
    var = VARselect(data.frame(data[,j], data [,i]),lag.max= lagMax)
    lag = var$selection[1]
    if (j != i) {
      tryCatch({
        test =   try (grangertest (data[,j] ~ data [,i], order = lag))
        if(test[1] == "Error in vc[ovar, ovar] : indice hors limites\n")
        {
          gMat[i,j] = 0
        }
        else gMat[i,j] = 1 - test$`Pr(>F)`[2]}, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
    }
    else
      gMat[i,j] = 1
  }
}
colnames(gMat) <- rownames(gMat) <- colnames(data)
write.table(gMat, output_dir,row.names = TRUE, na = "",col.names = TRUE, sep = ";", append = TRUE)
