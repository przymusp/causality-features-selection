library(cluster)
library(tsDyn)
library(lmtest)
library(vars)
library(stats) ##hclus
library(factoextra) # for the number of clusters
library(NbClust) # for the number of clusters
library(psych)  # for factor analysis method
library (kernlab)


source("../tools/selection_tools.R")
source("../tools/read_meta_data.R")


##### Read arguments

gfsm_DMRS_selection <- function (args){
    
    # Dataset directory
    data_dir = args[1]
    # Output directour
    output_dir = args[2]
    if( substr(output_dir, nchar(output_dir),nchar(output_dir)) != '/')
       output_dir = paste0(output_dir,'/')
    # Graph of entropies directory
    graph_dir = args[3]

    # Read meta_data
    meta_data = read_meta_data(data_dir)

    ## read the dataset
    data = read.csv(data_dir, header = TRUE, dec = '.',sep=";", comment.char = "#")
    colnames = colnames(data)

    # Graphs directory
    graph_dir = paste0("../../results/pre_selection/",meta_data$data_name)
    graphs = list.files(path = graph_dir, all.files = FALSE)

    # Dimension reduction methods
    dmr_methods = c("KPCA","PCA","FACT")

    for (dmr_method in dmr_methods)
    {
        for (k in 1:length(graphs))
        {
            threshold = 0

            graph_dir = paste0("../../results/pre_selection/",meta_data$data_name,"/",graphs[k])
            matrix = read.table(graph_dir, header = TRUE,row.names = 1, dec = '.',sep=";", comment.char = "#")
            ############# Execute the method  for each target
            for (target_name in meta_data$target_names) {
                
                for(j in 1:length(colnames)) {
                    if (colnames[j] == target_name) {
                        target_index = j
                        break;
                    }
                }
                ### G-feature selection method
                graph_name = substr(graphs[[k]], 1, (nchar(graphs[[k]])-4) )
                if (graph_name == "granger_graph")
                    threshold = 0.8

                out_dir = paste0(output_dir,target_name,"_",graph_name,"_GFSM_",dmr_method,"_.csv")
                gfsm = data.frame()
                try({
                    gfsm = gfsm_dms_reduction (data, matrix, target_index,threshold, clus = FALSE,nk =8, methode_name=dmr_method)
                })
                #print(gfsm[1:10,])
                if(nrow(data.frame(gfsm)) != nrow(data))
                # if(nrow(data.frame(gfsm)) == 0 && ncol(data.frame(gfsm)) == 0)
                gfsm = data.frame (data[,target_name])
                else
                    gfsm = data.frame (data[,target_name],data.frame(gfsm))
                colnames(gfsm)[1] = target_name
                # Bref description of the file
                command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',data_dir)
                system(paste0(command,' > ', out_dir))
                cat ("# predict;", file=out_dir,append=TRUE)
                cat (target_name, file=out_dir,append=TRUE, sep='\n')
                cat (paste0("# method; GFSM_",dmr_method,"_", graph_name,"(Granger_PCA feature selection method)"),file=out_dir,append=TRUE, sep='\n')

                ## Store the selected variables
                write.table(gfsm, out_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";", append = TRUE)

                for (nk in 1:30)
                {
                    out_dir = paste0(output_dir,target_name,"_",graph_name,"_GFSM_",dmr_method,"_K=",nk,".csv")
                    if (graph_name == "granger_graph")
                    threshold = 0.8
                    try({ gfsm = gfsm_dms_reduction (data, matrix, target_index,threshold, clus = FALSE, nk= nk)
                        })
                    if (ncol(data.frame(gfsm)) > 0)
                        gfsm = data.frame (data[,target_name],data.frame(gfsm))
                    else
                        gfsm = data.frame (data[,target_name])
                    colnames(gfsm)[1] = target_name

                    # Set metadata
                    command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',data_dir)
                    system(paste0(command,' > ', out_dir))
                    cat ("# predict;", file=out_dir,append=TRUE)
                    cat (target_name, file=out_dir,append=TRUE, sep='\n')
                    cat (paste0("# method; GSM_DM",dmr_method,"_", graph_name, "(n_components=",nk,")"),file=out_dir,append=TRUE, sep='\n')

                    ## Store the selected variables
                    write.table(gfsm, out_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";", append = TRUE)

                }
        }
    }
    }
}

args = commandArgs(trailingOnly=TRUE)

if (length(args) > 3){
    print ("Error: number of arguments incorrect.")
    quit()
}

gfsm_DMRS_selection (args)


