library(cluster)
library(tsDyn)
library(lmtest)
library(vars)
library(stats) ##hclus
#library(factoextra) # for the number of clusters
#library(NbClust) # for the number of clusters
#library (kernlab)

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
        threshold = 0.01
        graph_dir = paste0("../../results/pre_selection/",meta_data$data_name,"/",graphs[k])

        matrix = read.table(graph_dir, header = TRUE,row.names = 1, dec = '.',sep=";", comment.char = "#")
        colnames = colnames(matrix)
        
        graph_name = substr(graphs[[k]], 1, (nchar(graphs[[k]])-4) )
        #out_dir = paste0(output_dir,target_name,"_",graph_name,"_GFSM_trans.csv")

        if (is.element(graph_name, c("granger_graph","varnn_causality_graph")))
            threshold = 0.95

        for (i in 1:ncol(matrix))
            for (j in 1:ncol(matrix))
            {
                if (matrix[i,j] < threshold)
                    matrix[i,j] = 0
            }

        if (threshold != 0)
        for (j in 1:ncol(matrix))
        {
            for (i in 1:ncol(matrix))
            {
                if (i != j)
                for (k in 1:ncol(matrix))
                    if (k != i && (k != j && matrix[k,i] >= threshold) && (matrix[i,j] >= threshold) && (matrix[k,j] >= threshold))
                    {
                    if (matrix[i,j] >= matrix[k,j])
                        matrix[k,j] = 0.0
                    else
                        matrix[i,j] = 0.0
                    }
            }
        }
        ############# Execute the method  for each target
        
        for (target_name in meta_data$target_names)
        {
            target_name = trim(target_name)
            for(j in 1:length(colnames))
                if (colnames[j] == target_name) {
                    target_index = j
                    break;
                }

            ### G-feature selection method
  
            target_col = data.frame (1:ncol(matrix), matrix[,target_index])
            target_col = target_col[-target_index,]
            
            target_col = target_col[order(-target_col[,2]),]
            
            gsm_ranking = target_col[,1]

            for (nk in 1:10)
            {
                if (nk > (ncol(matrix) - 1))
                    break;
                    
                out_dir = paste0(output_dir,target_name,"_",graph_name,"_GSM-V2_K=",nk,".csv")
                #print (target_name)
                #print (graph_name)

                gfsm = data.frame (data[,target_index], data[,gsm_ranking[1:nk]])

                # Set metadata
                command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',data_dir)
                system(paste0(command,' > ', out_dir))
                
                cat ("# predict;", file=out_dir,append=TRUE)
                cat (target_name, file=out_dir,append=TRUE, sep='\n')
                cat ("# prediction_type;", file=out_dir, append=TRUE)
                cat (paste0(meta_data$prediction_type), file=out_dir, append=TRUE, sep='\n')
                cat (paste0("# method; GSM-V2", graph_name, "(n_components=",nk,")"),file=out_dir,append=TRUE, sep='\n')
                
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

