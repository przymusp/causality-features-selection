## Prediction evaluation

### Approach 1: "forward chaining"

From: http://stats.stackexchange.com/questions/14099/using-k-fold-cross-validation-for-time-series-model-selection

Time-series (or other intrinsically ordered data) can be problematic for cross-validation. If some pattern emerges in year 3 and stays for years 4-6, then your model can pick up on it, even though it wasn't part of years 1 & 2.

An approach that's sometimes more principled for time series is forward chaining, where your procedure would be something like this:

  * fold 1 : training [1], test [2]
  * fold 2 : training [1 2], test [3]
  * fold 3 : training [1 2 3], test [4]
  * fold 4 : training [1 2 3 4], test [5]
  * fold 5 : training [1 2 3 4 5], test [6]

That more accurately models the situation you'll see at prediction time, where you'll model on past data and predict on forward-looking data. It also will give you a sense of the dependence of your modeling on data size.

### Approach 2: "Roling windows"
Like Approach 1, but uses a fixed size roling window ie.

  * fold 1 : training [1 2], test [3]
  * fold 3 : training [2 3], test [4]
  * fold 4 : training [3 4], test [5]
  * fold 5 : training [4 5], test [6]

### Approach 3: hv cross validation
Paper: http://www.sciencedirect.com/science/article/pii/S0304407600000300
From: http://stats.stackexchange.com/questions/14099/using-k-fold-cross-validation-for-time-series-model-selection

For cross validation to work as a model selection tool, you need approximate independence between the training and the test data. The problem with time series data is that adjacent data points are often highly dependent, so standard cross validation will fail. The remedy for this is to leave a gap between the test sample and the training samples, on both sides of the test sample. The reason why you also need to leave out a gap before the test sample is that dependence is symmetric when you move forward or backward in time (think of correlation).

This approach is called hv
cross validation (leave v out, delete h

observations on either side of the test sample) and is described in this paper. In your example, this would look like this:

    fold 1 : training [1 2 3 4 5h], test [6]
    fold 2 : training [1 2 3 4h h6], test [5]
    fold 3 : training [1 2 3h h5 6], test [4]
    fold 4 : training [1 2h h4 5 6], test [3]
    fold 5 : training [1h h3 4 5 6], test [2]
    fold 6 : training [h2 3 4 5 6], test [ 1]

Where the h indicates that h observations of the training sample are deleted on that side.
