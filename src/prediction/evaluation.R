####
benchmark <- function (target,p, methods, nbPreds)
{
  result = c()
  real = target[ (length(target) - nbPreds + 1) : length(target) ]
  mthds = methods
  pred = c()
  for (i in 1 : length(mthds))
  {
    train = data.frame (target , methods[[i]])
    pred = disc(train,p,nbPreds,indCible)
    result[i] = mse (pred,real)
  }
  return (result)
}

#####
evaluation <- function (target, indCible, gsm, p)
{
  numData <- 1
  #mthds = methods[[1]]
  mthds = gsm
  results = list()
  
  for (ind in 1:numData)
  {
    pred = data.frame()
    results[[ind]] = data.frame ()
    cutTarget = target[1:(length(target) - 5)]
    
    #for (inc in 1 : length(mthds))
      mthds = mthds[1:(nrow(mthds) - 5),]
  
    ####### Apply the VECM model
    #for (inc in 1 : length(mthds))
    #{
      tryCatch({
      model = VECM (data.frame(cutTarget, mthds ), p, include = c("const"), estim = c("ML"))
      }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
      y = predict(model)
      for (ink in 1 : 5)
        pred[ink,1] = y[ink,1]
      
    #}
    ########
    real = target[(length(target)-4):length(target)]
    pred [,2] = real
    results[[ind]] = data.frame(pred)
    target = target[1:(length(target) - 5)]
  } 

  firstPredictions = data.frame()
  secondPredictions = data.frame()
  TPredictions = data.frame()
  QPredictions = data.frame()
  CPredictions = data.frame()

  ## create 4 dataframe corresponding to the five predictions
  ## The forth colums are the real values, used to calculate the MSE
  for (kl in 1 : numData)
  {
    for (j in 1 : (2))
    {
      firstPredictions[kl,j] = results[[((numData+1)-kl)]][1,j]
      secondPredictions[kl,j] = results[[((numData+1)-kl)]][2,j]
      TPredictions[kl,j] = results[[((numData+1)-kl)]][3,j]
      QPredictions[kl,j] = results[[((numData+1)-kl)]][4,j]
      CPredictions[kl,j] = results[[((numData+1)-kl)]][5,j]
    }
  }

  ## calculate the MSE (Mean Squared Error) of each horizon prediction (h=1, .., h = 5)
  MSE = data.frame();

  # h = 1
  for (kl in 1 : 1)
  {
    for (h in 1 : 5) {
      MSE[h,kl] = 0
    }
    for (a in 1 : numData)
    {
      MSE[1,kl] = MSE[1,kl] + (firstPredictions[a,kl] -  firstPredictions[a,2])^2 
      MSE[2,kl] = MSE[2,kl] + (secondPredictions[a,kl] - secondPredictions[a,2])^2
      MSE[3,kl] = MSE[3,kl] + (TPredictions[a,kl] -      TPredictions[a,2])^2
      MSE[4,kl] = MSE[4,kl] + (QPredictions[a,kl] -      QPredictions[a,2])^2
      MSE[5,kl] = MSE[5,kl] + (CPredictions[a,kl] -      CPredictions[a,2])^2
    }
    for (h in 1 : 5) {
      MSE[h,kl] = MSE[h,kl] / numData
    }
  }


for (kl in 1 : 1)
{
  for (h in 1 : 5) {
    MSE[h,kl] = round(MSE[h,kl],6)
  }
}

# Store the results 
#write.table(MSE, file = paste0("results/MSE-y",toString(indCible),".csv"),row.names = FALSE, na = "",col.names = FALSE, sep = ";")

#write.table(firstPredictions, file = paste0("results/FP",toString(indCible),".csv"),row.names = FALSE, na = "",col.names = FALSE, sep = ";")
#write.table(secondPredictions, file = paste0("results/SP",toString(indCible),".csv"),row.names = FALSE, na = "",col.names = FALSE, sep = ";")
#write.table(TPredictions, file = paste0("results/TP",toString(indCible),".csv"),row.names = FALSE, na = "",col.names = FALSE, sep = ";")
#write.table(QPredictions, file = paste0("results/FrP",toString(indCible),".csv"),row.names = FALSE, na = "",col.names = FALSE, sep = ";")
#write.table(CPredictions, file = paste0("results/FvP",toString(indCible),".csv"),row.names = FALSE, na = "",col.names = FALSE, sep = ";")

#script = paste0("python bar_chart.py ",toString(indCible) )
#python.load(script)
#system (script)

return (MSE)
}

### Normalize a dataframe
normalize <- function (F)
{
  for (i in 1 : ncol(F))
  {
    max = max(F[,i])
    min = min(F[,i])
    for(j in 1:nrow(F))
      F[j,i] = (F[j,i] - min) / (max - min) 
  }
  return (F)
}

