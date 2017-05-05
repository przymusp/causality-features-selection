library(cluster)
library(tsDyn)
library(lmtest)
library(vars)
library(stats) ##hclus
#library(factoextra) # for the number of clusters
#library(NbClust) # for the number of clusters
library (kernlab)

source("../tools/selection_tools.R")
source("../tools/read_meta_data.R")

gfsm_selection <- function (args){

    data_dir = args[1]
    output_dir = args[2]
    if( substr(output_dir, nchar(output_dir),nchar(output_dir)) != '/')
        output_dir = paste0(output_dir,'/')

    # Read files descriptions
    #command = paste0 ('awk /^#/ ',data_dir)
    meta_data = read_meta_data(data_dir)

    ## read the dataset
    data = read.csv(data_dir, header = TRUE, dec = '.',sep=";", comment.char = "#")
    colnames = colnames(data)

    # Graphs directory
    graph_dir = paste0("../../results/pre_selection/",meta_data$data_name)
    graphs = list.files(path = graph_dir, all.files = FALSE)
    for (k in 1:length(graphs))
    {
        graph_name = substr(graphs[[k]], 1, (nchar(graphs[[k]])-4) )
        threshold = 0.01
        if (is.element(graph_name, c("granger_graph","varnn_causality_graph")))
        threshold = 0.8
        
        graph_dir = paste0("../../results/pre_selection/",meta_data$data_name,"/",graphs[k])

        matrix = read.table(graph_dir, header = TRUE,row.names = 1, dec = '.',sep=";", comment.char = "#")
        ############# Execute the method  for each target
        for (target_name in meta_data$target_names)
        {
            for(j in 1:length(colnames))
                if (colnames[j] == target_name) {
                    target_index = j
                    break;
                }

            ### G-feature selection method
            
            out_dir = paste0(output_dir,target_name,"_",graph_name,"_GFSM.csv")

            for (nk in 1:30)
            {
                out_dir = paste0(output_dir,target_name,"_",graph_name,"_GFSM_K=",nk,".csv")
                
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
}

args = commandArgs(trailingOnly=TRUE)

if (length(args) > 3){
    print ("Error: number of arguments incorrect.")
    quit()
}

gfsm_selection (args)

