vec_prediction <- function (ts, p, nb_preds)
{
  # ts: multivariate time series to predict the first attribut
  # p: the lag parameter
  # nb_preds: percentage of the data to predict

  training_ts = ts
  
  results = data.frame ()
  target = training_ts[,1]
  training_ts[,1] = NULL

  for (ind in 1:nb_preds)
  {
    pred = data.frame()
    cutTarget = target[1:(length(target) - (nb_preds-ind)  - 5)]
    mthds = training_ts[1:(nrow(training_ts) - (nb_preds-ind) - 5),]
    real = target[(length(target)- (nb_preds-ind) -4):(length(target) - (nb_preds-ind))]

    ####### Apply the VECM model
      tryCatch({
      model = VECM (data.frame(cutTarget, mthds ), p, include = c("const"), estim = c("ML"))
      }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
      y = predict(model)
      for (ink in 1 : 5)
        pred[ink,1] = y[ink,1]
    ########
    
    #pred [,2] = real
    #results[[ind]] = data.frame(pred)
    for (j in 1:nrow(pred))
      results[ind,j] = pred[j,1]
   # target = target[1:(length(target) - 5)]
  }
  return (results)
}

## evaluation using arima model
arima_prediction <- function (target, p, ns, nb_preds)
{
  # ts: multivariate time series to predict the first attribut
  # p: the lag parameter
  # nb_preds: percentage of the data to predict

  results = data.frame()
  for (ind in 1:nb_preds)
  {
    cutTarget = target[1:(length(target) - (nb_preds-ind)  - 5)]
    real = target[(length(target)- (nb_preds-ind) -4):(length(target) - (nb_preds-ind))]
    
    tryCatch({
      model = arima (cutTarget,  order = c(p, ns, 1))
    }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
    y = predict(model, n.ahead = 5)$pred

    for (j in 1:5)
        results[ind,j] = y[j]
  }
  return (results)
}
## evaluation using auto.arima model
auto_arima_prediction <- function (target, max_p, nb_preds)
{
    # ts: multivariate time series to predict the first attribut
    # max_p: max lag parameter
    # nb_preds: percentage of the data to predict
    
    results = data.frame()
    for (ind in 1:nb_preds)
    {
        cutTarget = target[1:(length(target) - (nb_preds-ind)  - 5)]
        real = target[(length(target)- (nb_preds-ind) -4):(length(target) - (nb_preds-ind))]
        
        tryCatch({
            model = auto.arima (cutTarget,  max.p=max_p, max.q=5)
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
        y = forecast(model, h = 5)[[4]]
        print(y)
        #print(y[[4]])

        for (j in 1:5)
            results[ind,j] = y[j]
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
