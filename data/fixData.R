file = "/Users/youssef/documents/causality-features-selection/data/cina0.csv"
file = "/Users/youssef/documents/causality-features-selection/data/TSLF.csv"
out_file = "/Users/youssef/documents/causality-features-selection/data/cina.csv"
data = read.csv (file, comment.char = "#", header=TRUE, dec = ".",sep=";")
colnames = c()
for(i in 1:ncol(data))
{
  #data[,i] = as.numeric(data[,i])
  # if(i == ncol(data))
  # {
  # colnames[i] = "target"
  # break;
  # }
  # colnames[i] = paste0("V",i)
  print(paste(i,mean(data[,i])))
}
colnames(data) = colnames
write.table(data, file = out_file,row.names = FALSE, na = "",col.names = TRUE, sep = ";")

# fixed_data = data.frame()
# ind = 1
# j = 1
# for (i in 1:nrow(data))
# {
#   if (data[i,1] == ind)
#   {
#     for (l in 1:ncol(data))
#     fixed_data[j,l] =  data[i,l]
#     j = j + 1
#   }
#   else 
#   {
#     print(ind)
#     fixed_file = paste0("/Users/youssef/documents/causality-features-selection/data/__parkinsons_updrs_",ind,".csv")
#     print(fixed_file)
#     cat (paste0("# name_prefix; Machine learning Data Set for subject ",ind,"\n"), file=fixed_file,append=TRUE)
#     cat ("# description; Sample data from UCI repository \n", file=fixed_file,append=TRUE)
#     cat ("# predict; motor_UPDRS; total_UPDRS \n",file=fixed_file,append=TRUE, sep='\n')
#     colnames(fixed_data) = colnames(data)
#     write.table(fixed_data, file = fixed_file,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
#     fixed_data = data.frame()
#     ind = ind + 1
#     j = 1
#   }
# }
# 
# 
