fgsm <- function (F,gmat, targetIndex, k)
{
  gsmCluster = c()
  mincaus = 0
  #### eliminate variables that not cause the target
  delet = c()
  n = 1
  m = 1
  for (i in 1:ncol(gmat))
  {
    if (i == targetIndex)
      target = m
    if (i != targetIndex)
      if (gmat[i,targetIndex] < 0.01)
      {
        delet[n] = i
        n = n + 1
      }
    else {
      m = m + 1
    }
  }
  ###########
  ### Applying the PAM methode
  if (length(delet > 0))
  {
    gmat = gmat[-delet, -delet]
    F = F[,-delet]
    x = gmat[-target, -target]
  } else
    x = gmat[-target, -target]
  #F = F[,-target]
  ######
  if (k < ncol(x))
  {
    
    for (l in 2:ncol(x))
      for(m in 1: (l-1))
        x[l,m] = x[m,l] = 1 - max(x[l,m], x[m,l])
      
      
      #km = kcca(x, k, family = kccaFamily ("kmeans"), weights=NULL, group=NULL, control=NULL, simple=FALSE)
      #symmetrize(x, rule="strong")
      #clusters = pamk(as.dist(x),krange=5:15,criterion="ch",critout=TRUE)
      #evals = c()
      #for (kchoice in 2: (ncol(x)-2))
      #{
       # clusters =  pam(as.dist(x),kchoice)
        #evals[kchoice] = clusters$objective[1]
      #}
      #k = which.min(evals)
      clusters = pam (as.dist(x),k)
      clusteringVector = clusters$cluster
      #clusteringVector = clusters (clusters)
      
      classes = data.frame()
      for (j in 1:k)
      { 
        l = 1
        for ( i in 1:ncol(x))
          if (clusteringVector[i] == j)
          {
            classes[l,j] = i
            if (classes[l,j] >= target)
            {
              classes[l,j] = classes[l,j] + 1
            }
            l = l + 1
          }
      }
      
      ### buildind the gsm cluster from the PAM clusters
      for (j in 1:k)
      {
        bestInGroup = 1;
        if (ncol(classes) >= j)
        {
          caus = gmat[classes[1,j],target];
          for (l in 2:length(classes[,j]))
          {
            if(is.na(classes[l,j]) == FALSE)
            {
              if (gmat[classes[l,j],target] > caus)
              {
                caus = gmat[classes[l,j],target];
                bestInGroup = l;
              }
            }
            gsmCluster[j] = classes[bestInGroup,j];
          }
        }
      }
      GSM = data.frame()
      GSM = F [,gsmCluster]
      return (GSM)
  }
  else 
    return (F[,-target])
  #return (gsmCluster)
}

##### gsm with PCA method
gsmPCA <- function (F,gmat, targetIndex, k)
{
  gsmCluster = c()
  mincaus = 0
  #### eliminate variables that not cause the target
  delet = c()
  n = 1
  m = 1
  for (i in 1:ncol(gmat))
  {
    if (i == targetIndex)
      target = m
    if (i != targetIndex)
      if (gmat[i,targetIndex] < 0.9)
      {
        delet[n] = i
        n = n + 1
      }
    else {
      m = m + 1
    }
  }
  ###########
  ### Applying the PAM methode
  if (length(delet > 0))
  {
    gmat = gmat[-delet, -delet]
    F = F[,-delet]
    x = gmat[-target, -target]
  }
  else
    x = gmat[-target, -target]
  #F = F[,-target]
  ######
  if (k < ncol(x))
  {
    
    for (l in 2:ncol(x))
      for(m in 1: (l-1))
        x[l,m] = x[m,l] = 1 - max(x[l,m], x[m,l])
      
      
      #km = kcca(x, k, family = kccaFamily ("kmeans"), weights=NULL, group=NULL, control=NULL, simple=FALSE)
      #symmetrize(x, rule="strong")
      clusters = pam (as.dist(x), k)
      clusteringVector = clusters$cluster
      #clusteringVector = clusters (km)
      
      classes = data.frame()
      for (j in 1:k)
      { 
        l = 1
        for ( i in 1:ncol(x))
          if (clusteringVector[i] == j)
          {
            classes[l,j] = i
            if (classes[l,j] >= target)
            {
              classes[l,j] = classes[l,j] + 1
            }
            l = l + 1
          }
      }
      
      ### buildind the gsm cluster from the PAM clusters
      for (j in 1:k)
      {
        bestInGroup = 1;
        if (ncol(classes) >= j)
        {
          caus = gmat[classes[1,j],target];
          for (l in 2:length(classes[,j]))
          {
            if(is.na(classes[l,j]) == FALSE)
            {
              if (gmat[classes[l,j],target] > caus)
              {
                caus = gmat[classes[l,j],target];
                bestInGroup = l;
              }
            }
            gsmCluster[j] = classes[bestInGroup,j];
          }
        }
      }
      GSM = data.frame()
      GSM = F [,gsmCluster]
      return (GSM)
  }
  else 
    return (F[,-target])
  #return (gsmCluster)
}


#### SELECTKBEST based on causality
naiveSelection <- function (gmat, targetIndex, threshold)
{
  naiveClasse = c()
  ##F = data.frame ()
  ind  = 1
  index = c()
  
  for (i in 1:ncol(gmat))
  {  
    if (i != targetIndex)
    {
      #F[ind,1] = i;
      if (gmat[i,targetIndex] >= threshold && gmat[targetIndex,i] < threshold)
      {
        index[ind] = i
        ind = ind + 1
      }
    }
  }
  # Order by causality on the targer variable : targetIndex
  #G = F[order(-F[,2]),c(1,2)]
  #for (i in 1:k)
    #naiveClasse = union(naiveClasse, c(G[i,1]))
  
  return (index)
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
  
#### neural network function
disc <- function (F,p, dec, cible)
{
  
  G = F[1:(nrow(F) - (dec + 1)),]
  hiddenLayers = c((ncol(G) * p* 2 / 3), (ncol(G) * p * 2 / 3),(ncol(G) * p * 2 / 3)) 
  module = varnnet(G, p, 1, hiddenLayers, 1000)
  result = data.frame()
  ts = data.frame()
  for (ind in 1:dec)
  {
    ts = F[1:(nrow(F) - (dec - ind + 1)),]
    
    y = module$forecast(ts)
    
    for (ij in 1:ncol(y))
      result[ind,ij] = y[nrow(y),ij]
    
    iter = 1
    
    while (iter < 2)
    {
      module$learn (F[1:(nrow(F) - (dec - ind)),])
      iter = iter + 1
    }
  }
  return (result)
}
  
  
  
