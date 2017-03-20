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
data = read.csv(data_dir, header=TRUE,check.names=FALSE,dec='.',sep=";",comment.char = "#")

# read  metadata
command = paste0 ('awk /^#/ ',data_dir)
dat <- system(command,  intern = TRUE)
description = dat[[2]]

file_name_split = strsplit(data_dir, "/")[[1]]
data_name = file_name_split[length(file_name_split)]
data_name = gsub(".csv", "",data_name, fixed=TRUE)

lag_p = strsplit(dat[[3]], ";")[[1]][2]
lag_p = strsplit(lag_p, '\r')[1]
lag_p = strtoi(lag_p)

if(is.na(lag_p))
    lag_p = 0

# construct the output directory+name
output_dir = paste0(output_dir,data_name,"_","granger_graph.csv")
system(paste0(command,' > ', output_dir))


#### calculate the matrix
gMat = data.frame(nrow=ncol(data), ncol=ncol(data))
for (i in 1:ncol(data))
{
    for (j in 1:ncol(data))
     {
         lag = lag_p
         if (lag == 0){
         lagMax = as.integer ((nrow(data)  - 1)  / (2*(ncol(data) + 1)))
         var = VARselect(data.frame(data[,j], data [,i]),lag.max= lagMax)
         lag = var$selection[1]
         }

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
            gMat[i,j] = 0
  }
}
gMat = data.frame(c(colnames(data)),gMat)
colnames(gMat) <- c(' ', colnames(data))
write.table(gMat, output_dir, sep = ";",row.names =FALSE, append = TRUE)
