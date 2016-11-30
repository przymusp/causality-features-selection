library(cluster)
library(tsDyn)
library(lmtest)
library(vars)
library(stats) ##hclus
library(fpc)  ## for pamkCBI : pam with no k
library (kernlab)


#getwd()
source("../tools/selection_tools.R")
args = commandArgs(trailingOnly=TRUE)

##### Read arguments
args = commandArgs(trailingOnly=TRUE)

if (length(args) > 3){
  print ("Error: number of arguments incorrect.")
  quit()
}
# Dataset directory
data_dir = args[1]
# Output directour
output_dir = args[2]
if( substr(output_dir, nchar(output_dir),nchar(output_dir)) != '/')
   output_dir = paste0(output_dir,'/')
# Graph of entropies directory
graph_dir = args[3]

# Read files descriptions
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
graph_dir = paste0("../../results/pre_selection/",data_name,"/",data_name,"_granger_graph.csv")
#getSrcDirectory()
#graph_dir
matrix = read.table(graph_dir, header = TRUE,row.names = 1, dec = '.',sep=";", comment.char = "#")
############# Execute the method  for each target
for (i in 2:length(target_names)) {
    target_name = target_names[i]
    target_name
    for(j in 1:length(colnames)) {
      if (colnames[j] == target_name) {
        target_index = j
      break;
      }
    }
    ### G-feature selection method
    out_dir = paste0(output_dir,data_name,"_",target_name,"_","G_PCA_FSM.csv")
    gfsm = gsmPCA (data, matrix, target_index, 4)
    gfsm = data.frame (data[,target_name],gfsm)
    colnames(gfsm)[1] = target_name

    # Bref description of the file
    command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',data_dir)
    system(paste0(command,' > ', out_dir))
    cat ("# predict;", file=out_dir,append=TRUE)
    cat (target_name, file=out_dir,append=TRUE, sep='\n')
    cat ("# method; Granger_cluster_PCA(Granger_PCA feature selection method)",file=out_dir,append=TRUE, sep='\n')

    ## Store the selected variables
    write.table(gfsm, out_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";", append = TRUE)
}


