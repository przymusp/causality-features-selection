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
evaluation <- function (fsdata, p, numData)
{
  mthds = fsdata
  #results = list()
  results = data.frame ()
  target = mthds[,1]
  mthds[,1] = NULL

  for (ind in 1:numData)
  {
    pred = data.frame()
    #results[[ind]] = data.frame ()
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
    #results[[ind]] = data.frame(pred)
    for (j in 1:nrow(pred))
      results[ind,j] = pred[j,1]
    target = target[1:(length(target) - 5)]
  }
  return (results)
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

### denormalize a dataframe
denormalize <- function (F,max,min)
{
  for (i in 1 : ncol(F))
  {
    for(j in 1:nrow(F))
      F[j,i] =  min + F[j,i]*(max - min)
  }
  return (F)
}
