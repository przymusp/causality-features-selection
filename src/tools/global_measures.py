from sklearn.metrics import\
        mean_squared_error, mean_absolute_error, explained_variance_score, median_absolute_error, r2_score

# All used measures
GLOBAL_MEASURES = {
    'mse': mean_squared_error,
    'mae': mean_absolute_error,
    'medae': median_absolute_error,
    'MASE': MASE,
    # 'evc': explained_variance_score,
    # 'r2': r2_score,
    # 'R': lambda x,y: 1, # placeholder
}
