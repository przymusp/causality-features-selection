vecm_rolling <- function (ts, p, nb_preds, horizon)
{
  # ts: multivariate time series to predict the first attribut
  # p: the lag parameter
  # nb_preds: number points to predict

  training_ts = ts
  
  results = data.frame ()
  target = training_ts[,1]
  #training_ts[,1] = NULL
  #print (ts)
  pred = data.frame()

  for (ind in 1:nb_preds)
  {
    
    #cutTarget = target[nb_preds:(length(target) - (nb_preds-ind)  - horizon)]
    mthds = training_ts[ind:(nrow(training_ts) - (nb_preds-ind) - horizon),]
    real = target[(length(target)- (nb_preds-ind) - horizon + 1):(length(target) - (nb_preds-ind))]

    ####### Apply the VECM model
    tryCatch({
      model = VECM (data.frame(mthds), p, include = c("const"), estim = c("ML"))
    }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
    y = predict(model,n.ahead = horizon)
    
    for (inh in 1 : horizon)
        pred[ind,inh] = y[inh,1]
  }

  return (pred)
}

## evaluation using arima model
arima_prediction <- function (target, p, ns, nb_preds, horizon)
{
  # ts: multivariate time series to predict the first attribut
  # p: the lag parameter
  # nb_preds: number points to predict

  results = data.frame()
  for (ind in 1:nb_preds)
  {
    cutTarget = target[ind:(length(target) - (nb_preds-ind)  - horizon)]
    real = target[(length(target)- (nb_preds-ind) -horizon+1):(length(target) - (nb_preds-ind))]
    
    tryCatch({
      model = arima (cutTarget,  order = c(p, ns, 1))
    }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
    y = predict(model, n.ahead = horizon)$pred

    for (j in 1:horizon)
        results[ind,j] = y[j]
  }
  return (results)
}
## evaluation using auto.arima model
auto_arima_prediction <- function (target, max_p, nb_preds, horizon)
{
    # ts: multivariate time series to predict the first attribut
    # max_p: max lag parameter
    # nb_preds: number points to predict
    
    results = data.frame()
    for (ind in 1:nb_preds)
    {
        cutTarget = target[ind:(length(target) - (nb_preds-ind)  - horizon)]
        real = target[(length(target)- (nb_preds-ind) -horizon+1):(length(target) - (nb_preds-ind))]
        
        tryCatch({
            model = auto.arima (cutTarget,  max.p=max_p, max.q=2)
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
        y = forecast(model, h = horizon)[[4]]
        print(y)
        #print(y[[4]])

        for (j in 1:horizon)
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
