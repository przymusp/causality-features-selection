# Link Analysis

## Random walk with restarts on input graph
  * Build a "causality graph":
    * using Granger causality
    * or using transfer entropy
  * For each node normalize the input edges weights:
    * Now normalization is done for each node separatly
    * consider other ways of normalization, for example using data from whole graph.
  * reverse the edges
    * Note that somethimes the same approach without reversing the nodes also works (TODO: investigate why),
  * For each target node do the random walk with restarts to predicted node.

**Result**
A ranking vector, to select K futures, take top K varibles from the ranking.
Automatic selection of K would be better, but ranking is still good, as it significantly reduces the searching space of possible features sets.

## Idea: Selecting optimal K
  * Using pagerank, applly spam link analysis approach to select the optimal number of selected variables. (pagerank without personalization and pagerank with personalization (as trusted version))
  * Take only nodes with negative spam mass, or take all top values until last top value with negative spam mass.

**Problems**:
  * Not always works, ie. Sometimes it returns only target node with negative spam mass (usualy arima prediction yields good predictions in this case but not always).
  * Using TE, the lag parameter should be automaticly selected (now it is always fixed to 1). This may result in worse results compared to LA on granger causality graph.

**Other ideas**:
  * remove in-edges of target for the personalization step

# Idea: HITS algorithm
Think about using HITS algorithm instead of pagerank, as hits naturally distinguishes between hubs and authorithies (this MAYBE may be used for indicating which nodes are the cause *authorithy* and which depend on others *hubs*). Easy in networkX. Already checked on TE for some data, needs extra check on Granger.
