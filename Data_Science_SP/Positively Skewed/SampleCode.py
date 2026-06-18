import pandas as pd
import numpy as np
import os
from collections import OrderedDict
from sklearn.base import clone
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.impute import SimpleImputer
from sklearn.metrics import make_scorer
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor


#------------------------------------------------------------------------------
# Fucntion INIT
#------------------------------------------------------------------------------
def mape(y_true, y_pred):
    y_val = np.maximum(np.array(y_true), 1e-8)
    return (np.abs(y_true -y_pred)/y_val).mean()

def fMAE_scoreModel(y_true, y_pred):
    MAE = mean_absolute_error(y_true, y_pred)
    return MAE

metrics_dict_res = OrderedDict([('mean abs perc error', mape), 
                                ('MAE', fMAE_scoreModel)])

def regression_metrics_yin(y_train, y_train_pred, y_test, y_test_pred, metrics_dict = metrics_dict_res, format_digits = 3):
    df_results = pd.DataFrame()
    for metric, fct_metrics in metrics_dict.items():
        df_results.at[metric, 'train'] = fct_metrics(y_train, y_train_pred)
        df_results.at[metric, 'test'] = fct_metrics(y_test, y_test_pred)
    if format_digits is not None:
        df_results = df_results.applymap(('{:,.%df}' % format_digits).format)
    return df_results

#------------------------------------------------------------------------------
# INIT
#------------------------------------------------------------------------------
# Path
str_folder = r'C:\Users\laurent.tupin\Documents\GitHub\Positively_Skewed\IHSM_Sample'
str_pathTrain = os.path.join(str_folder, 'train_sample.csv')
str_path_oss = os.path.join(str_folder, 'oos_sample.csv')
df_dataTrain = pd.read_csv(str_pathTrain, index_col = 'vehicle_id')
df_proc_oos = pd.read_csv(str_path_oss, index_col = 'vehicle_id')

# Rows with No Price
df_dataTrain.dropna(axis = 0, subset = ['Price_USD'], inplace = True)
# split between measure and dimension
y = df_dataTrain.Price_USD
X = df_dataTrain.drop(['Price_USD'], axis=1)
numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.to_list()
categorical_cols = X.select_dtypes(include=['object']).columns.to_list()
if categorical_cols:
    print('Column Object Detected, need Categorical Variables (or just Pipeline is enought')

X = X[categorical_cols + numerical_cols].copy()
X_oss = df_proc_oos[categorical_cols + numerical_cols].copy()


target_name = 'Price_USD'
ml_model_type = 'Random Forest'
train_size = 0.8
test_size = 0.2 #0.3
random_state = 0 #33

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size = train_size, test_size = test_size, random_state = random_state)


if ml_model_type == 'Random Forest':
    #    d_param = OrderedDict(n_estimators = 10, 
    #                          max_depth = 4, 
    #                          min_samples_split = 2, 
    #                          min_samples_leaf = 1, 
    #                          max_features = 'sqrt', 
    #                          random_state = random_state, 
    #                          n_jobs = 4)
    d_param = OrderedDict(n_estimators = 2000, 
                          max_depth = None, 
                          min_samples_split = 2, 
                          max_leaf_nodes = 5000,
                          criterion = 'mse')
    regressor = RandomForestRegressor(random_state = random_state, **d_param)
base_regressor = clone(regressor)
regressor.fit(X_train, y_train)
y_train_pred = regressor.predict(X_train)
y_test_pred = regressor.predict(X_test)


df_regression_metrics = regression_metrics_yin(y_train, y_train_pred, y_test, y_test_pred, metrics_dict_res, format_digits = 3)
df_output = df_regression_metrics.copy()
df_output.loc['Counts','train'] = len(y_train)
df_output.loc['Counts','test'] = len(y_test)
print(df_output)
      
y_oos_pred = regressor.predict(X_oss)

id_col = 'vehicle_id'
df_out = (pd.DataFrame(y_oos_pred, columns=[target_name], index = X_oss.index)
            .reset_index()
            .rename({'index': id_col}, axis=1))

df_out.to_csv('submission.csv', index = False)