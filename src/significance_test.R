
# usage(): Rscript significance_test.R data_directory

library(forecast)
library(stats)
library(tseries)


significance_test <- function (data_dir) {
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

    # Extrat target time series
    target_names = c(dat[[3]])
    target_names = target_names[-1]


    # Prediction directory
    pred_dir = paste0("results/prediction/",data_name)
    pred_files = list.files(path = pred_dir, all.files = FALSE)

    # Extract last 10% from the originial values
    reals = list()
    data = read.csv(data_dir,comment.char = "#", sep=";", dec = ".")
    begin = nrow(data) - (10 * nrow(data) / 100) + 1
    end = nrow(data)
    
    for (target_name in target_names)
    {
        reals[[target_name]] = data[begin:end,target_name]
    }
    #print (reals)
    # Class files by target time series
    lists = list()
    for (target_name in target_names)
    {
        list = c()
        if (target_name != "")
        for (pred_file in pred_files)
        {
            if (grepl(target_name, pred_file))
            {
                list = c(list,pred_file)
            }
        }
        lists[[target_name]] = list
    }

    # Compute significance
    targets = names(lists)
    print (targets)

    global_results = list()
    for (k in 1: length(lists))
    {
        results = data.frame()
        real = reals[[targets[k]]]
        print (real)
        l = 1
        for (i in 1:(length(lists[[k]])-1))
        {
            if (is.na(lists[[k]][i]))
                i = i + 1
            for (j in (i+1):length(lists[[k]]))
            {
                if (is.na(lists[[k]][j]))
                j = j + 1
                #print (paste0 (lists[[k]][i], ".....",lists[[k]][j]))
                ts1 = data.frame()
                ts2 = data.frame()
                ts1 = read.csv(paste0("results/prediction/",data_name,"/",lists[[k]][i]),comment.char = "#", sep=";", dec = ".")
                ts2 = read.csv(paste0("results/prediction/",data_name,"/",lists[[k]][j]),comment.char = "#", sep=";", dec = ".")
                #print (ts1)
                e1 = c()
                e2 = c()
                #print (paste0(nrow(ts1), ".....",length(reals[[targets[k]]])))
                #print (ts2[,1])
                #print (reals[[targets[k]]])
                # if (nrow(ts1) == length(reals[[targets[k]]])){
                for (m in 1:nrow(ts1))
                {
                        e1[m] = ts1[m,1] - reals[[targets[k]]][m]
                        e2[m] = ts2[m,1] - reals[[targets[k]]][m]
                }
               # }
               # Apply the test with h : the horizon forecast, here it's 1
               value = 0
            
                tryCatch({
                    test = dm.test(e1, e2,"two.sided", h=1, power=2)
                    value = test$p.value
                }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
            
                results[l,1] = lists[[k]][i]
                results[l,2] = lists[[k]][j]
                results[l,3] = value
                l = l + 1
            }
        }
        names(results) = c("file_x", "file_y", "p_value")
        global_results[[targets[k]]] = results
    }

    # Store the results on csv files
    dir <- paste0("results/evaluation/",data_name,"/")

    
    dir.create(dir)
    k = 1
    for (results in global_results)
    {
        file_name = paste0(dir,names(global_results)[k],".csv")
        write.table(results, file = file_name,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = FALSE)
        k = k + 1
    }
}

##### Read arguments
args = commandArgs(trailingOnly=TRUE)

if (length(args) > 1){
    print ("Error: number of arguments incorrect.")
    quit()
}

data_dir = args[1]
significance_test (data_dir)


