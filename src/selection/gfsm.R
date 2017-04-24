library(cluster)
library(tsDyn)
library(lmtest)
library(vars)
library(stats) ##hclus
library(factoextra) # for the number of clusters
library(NbClust) # for the number of clusters
library (kernlab)

## elimination space funtion
trim <- function (x) gsub("^\\s+|\\s+$", "", x)

#getwd()
source("../tools/selection_tools.R")
#args = commandArgs(trailingOnly=TRUE)

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


# Read files descriptions
command = paste0 ('awk /^#/ ',data_dir)
dat <- system(command,  intern = TRUE)
description = dat[[2]]
#dat <- strsplit(dat, ";")
file_name_split = strsplit(data_dir, "/")[[1]]
data_name = file_name_split[length(file_name_split)]
data_name = gsub(".csv", "",data_name, fixed=TRUE)

datNamed <- read.table(text=gsub("^# *", "",dat), row.names = 1, sep=";",header=FALSE)
description = toString(datNamed["description","V2"])
target_names = toString(datNamed["predict","V2"])

target_names = strsplit(target_names, ',')[[1]]

print (target_names)
## read the dataset
data = read.csv(data_dir, header = TRUE, dec = '.',sep=";", comment.char = "#")
colnames = colnames(data)

# Graphs directory
graph_dir = paste0("../../results/pre_selection/",data_name)
graphs = list.files(path = graph_dir, all.files = FALSE)
for (k in 1:length(graphs))
{
    threshold = 0
    graph_dir = paste0("../../results/pre_selection/",data_name,"/",graphs[k])

    matrix = read.table(graph_dir, header = TRUE,row.names = 1, dec = '.',sep=";", comment.char = "#")
    ############# Execute the method  for each target
    for (i in 1:length(target_names))
    {
        target_name = strsplit(target_names[i],"\r")[1]
        target_name = trim(target_name)
        target_name = toString(target_name)
        #print (is.list(target_name[1]))
        # if (substr(target_name,1,1) == " ")
        #   target_name = strsplit(target_name," ")[2]

        for(j in 1:length(colnames))
        {
            if (colnames[j] == target_name) {
                target_index = j
                break;
            }
        }

        ### G-feature selection method
        graph_name = substr(graphs[[k]], 1, (nchar(graphs[[k]])-4) )
        
        out_dir = paste0(output_dir,target_name,"_",graph_name,"_GFSM.csv")

        if (graph_name == "granger_graph")
            threshold = 0.8
            
            #gfsm = fgsm (data, matrix, target_index,threshold, clus = TRUE, nk= 1)
        
        #if (ncol(data.frame(gfsm)) > 0)
        #   gfsm = data.frame (data[,target_index],data.frame(gfsm))
        #else
        #   gfsm = data.frame (data[,target_index])
        #colnames(gfsm)[1] = target_name
        

        # Set metadata
        #command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',data_dir)
        #system(paste0(command,' > ', out_dir))
        
        #cat ("# predict;", file=out_dir,append=TRUE)

        #cat (target_name, file=out_dir,append=TRUE, sep='\n')

        #cat (paste("# method; Granger_FE_Automatic_K", graph_name, "()"),file=out_dir,append=TRUE, sep='\n')

        ## Store the selected variables
        #write.table(gfsm, out_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";", append = TRUE)

        for (nk in 1:30)
        {
            out_dir = paste0(output_dir,target_name,"_",graph_name,"_GFSM_K=",nk,".csv")
            
            if (graph_name == "granger_graph")
                threshold = 0.8
            
            gfsm = fgsm (data, matrix, target_index,threshold, clus = FALSE, nk= nk)
            
            if (ncol(data.frame(gfsm)) > 0)
                gfsm = data.frame (data[,target_index],data.frame(gfsm))
            
            else
                gfsm = data.frame (data[,target_index])
                
            colnames(gfsm)[1] = target_name

            # Set metadata
            command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',data_dir)
            system(paste0(command,' > ', out_dir))
            
            cat ("# predict;", file=out_dir,append=TRUE)
            cat (target_name, file=out_dir,append=TRUE, sep='\n')
            cat (paste0("# method; Granger_FE_", graph_name, "(n_components=",nk,")"),file=out_dir,append=TRUE, sep='\n')
            ## Store the selected variables
            write.table(gfsm, out_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";", append = TRUE)

        }
    }
}


