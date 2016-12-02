file = "/Users/youssef/documents/causality-features-selection/data/NEW-DATA/NEW-DATA-1.T15.csv"
data = read.csv (file, comment.char = "#", header=TRUE, sep=";")
fixed_file = "/Users/youssef/documents/causality-features-selection/data/NEW-DATA/NEW-DATA.csv"

cat ("# name_prefix; SML2010 Data Set \n", file=fixed_file,append=TRUE)
cat ("# description; Sample data from UCI repository \n", file=fixed_file,append=TRUE)
cat ("# predict; \n",file=fixed_file,append=TRUE, sep='\n')

write.table(data, file = fixed_file,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
