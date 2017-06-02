
####################### naive benchmark methode #########################
naive_benchmark <- function (target, nb_preds, horizon, type = "cross_validation")
{
    results = data.frame()
    for (ind in 1:nb_preds)
    {
        if (type == "cross_validation")
            training_data = target[1:(length(target) - (nb_preds - ind)  - horizon)]
        
        else if (type == "rolling")
            training_data = target[ind:(length(target) - (nb_preds - ind)  - horizon)]
        
        for (j in 1:horizon)
        {
            results[ind,j] = mean (training_data)
            training_data[length(training_data) + 1] = results[ind,j]
        }
    }
    return (results)
}

######################### ar model ###################################
ar_prediction <- function (target, p, ns, nb_preds, horizon, type = "cross_validation")
{
    results = data.frame()
    for (ind in 1:nb_preds)
    {
        if (type == "cross_validation")
            training_data = target[1:(length(target) - (nb_preds - ind)  - horizon)]
        
        else if (type == "rolling")
            training_data = target[ind:(length(target) - (nb_preds - ind)  - horizon)]
        
        tryCatch({
            #model = arima (training_data,  order = c(p, 1, 0))
            model = auto.arima (training_data,  max.p = p, start.p = p, max.q = 0)
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
        
        #y = predict(model,  n.ahead = horizon)$pred
        y = forecast(model, h = horizon)[[4]]
        
        for (j in 1:horizon)
            results[ind,j] = y[j]
    }
    return (results)
}

##################### arima model #######################################
arima_prediction <- function (target, p, ns, nb_preds, horizon, type = "cross_validation")
{
  # ts: multivariate time series to predict the first attribut
  # p: the lag parameter
  # nb_preds: number points to predict

  results = data.frame()
  for (ind in 1:nb_preds)
  {
      if (type == "cross_validation")
        training_data = target[1:(length(target) - (nb_preds - ind)  - horizon)]
      
      else if (type == "rolling")
        training_data = target[ind:(length(target) - (nb_preds - ind)  - horizon)]
    
    tryCatch({
      model = arima (training_data,  order = c(p, ns, 1))
    }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
    y = predict(model, n.ahead = horizon)$pred

    for (j in 1:horizon)
        results[ind,j] = y[j]
  }
  return (results)
}

########################## auto.arima model ##################################
auto_arima_prediction <- function (target, max_p, nb_preds, horizon, type = "cross_validation")
{
    # ts: multivariate time series to predict the first attribut
    # max_p: max lag parameter
    # nb_preds: number points to predict
    
    results = data.frame()
    for (ind in 1:nb_preds)
    {
        if (type == "cross_validation")
            training_data = target[1:(length(target) - (nb_preds - ind)  - horizon)]
        
        else if (type == "rolling")
            training_data = target[ind:(length(target) - (nb_preds - ind)  - horizon)]
        
        tryCatch({
            model = auto.arima (training_data,  max.p=max_p, max.q=2)
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
        
        y = forecast(model, h = horizon)[[4]]

        for (j in 1:horizon)
            results[ind,j] = y[j]
    }
    return (results)
}

######################## Normalize a dataframe ##########################
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

########################## denormalize a dataframe ##########################
denormalize <- function (F,max,min)
{
  for (i in 1 : ncol(F))
  {
    for(j in 1:nrow(F))
      F[j,i] =  min + F[j,i]*(max - min)
  }
  return (F)
}
