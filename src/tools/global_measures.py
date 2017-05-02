from sklearn.metrics import\
        mean_squared_error, mean_absolute_error, explained_variance_score, median_absolute_error, r2_score
import numpy as np

def MASE(testing_series, prediction_series):
    training_len = len(testing_series)
    differences = np.abs(np.diff(testing_series.T)).sum() / (training_len - 1)
    errors = np.abs(testing_series - prediction_series)
    return errors.mean() / differences

# All used measures
GLOBAL_MEASURES = {
        'rmse': lambda x,y: sqrt(mean_squared_error(x,y)),
        'mse': mean_squared_error(x,y),
        'mae': mean_absolute_error,
        'medae': median_absolute_error,
        'MASE': MASE,
        # 'evc': explained_variance_score,
        # 'r2': r2_score,
        # 'R': lambda x,y: 1, # placeholder
        }
