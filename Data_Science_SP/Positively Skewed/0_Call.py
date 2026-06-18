#from learntools.core import binder
#binder.bind(globals())

import pandas as pd
import numpy as np
import os
import MainProcess as mp
from collections import OrderedDict
from sklearn.base import clone
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.impute import SimpleImputer
from sklearn.metrics import make_scorer
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor


# Path
str_folder = r'C:\Users\laurent.tupin\Documents\GitHub\Positively_Skewed\IHSM_Sample'
str_pathTrain = os.path.join(str_folder, 'train_sample.csv')
str_pathRes = os.path.join(str_folder, 'oos_sample.csv')
df_dataTrain = pd.read_csv(str_pathTrain, index_col = 'vehicle_id')
df_dataRes = pd.read_csv(str_pathRes, index_col = 'vehicle_id')


# Rows with No Price
df_dataTrain.dropna(axis = 0, subset = ['Price_USD'], inplace = True)
# split between measure and dimension
y = df_dataTrain.Price_USD
X = df_dataTrain.drop(['Price_USD'], axis=1)
numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.to_list()
categorical_cols = X.select_dtypes(include=['object']).columns.to_list()
if categorical_cols:
    print('Column Object Detected, need Categorical Variables (or just Pipeline is enought')

# Only for SAMPLE project
#numerical_cols.remove('vehicle_id')

X = X[categorical_cols + numerical_cols].copy()
X_Res = df_dataRes[categorical_cols + numerical_cols].copy()

# Split between Train and Test
X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size = 0.8, test_size = 0.2, random_state = 0)


#------------------------------------------------------------------------------
# CLEAN DATA
#------------------------------------------------------------------------------
def f_ChoseDataCleaningMethod(X_train, X_valid, y_train, y_valid): 
    mp.fBl_IsColEmpty(X, 0.2)
    # Run on several Model
    l_model = [DecisionTreeRegressor(random_state = 0), 
               RandomForestRegressor(random_state = 0)]
    int_MAE_min = -1
    for o_model in l_model:
        int_MAE, d_choice = mp.f_CompareDataMethod(o_model, X_train, X_valid, y_train, y_valid)
        if int_MAE == 0:
            print(' CLEAN DATA: No refund data')
            return {}, 0
        elif int_MAE < int_MAE_min or int_MAE_min == -1:
            int_MAE_min = int_MAE
            model = o_model
    # Result
    print('  ', d_choice[int_MAE_min], '\n    MAE: ', int_MAE_min)
    print('   The model to be preferred for the technic of data we have chose: ')
    print('  ', model, '\n\n')
    return d_choice, int_MAE_min

d_choice, int_MAE_min = f_ChoseDataCleaningMethod(X_train, X_valid, y_train, y_valid)
if int_MAE_min > 0:
    X_train2, X_valid2 = mp.f_RefundData(X_train, X_valid, d_choice[int_MAE_min][0])
else:
    X_train2, X_valid2 = X_train.copy(), X_valid.copy()


#------------------------------------------------------------------------------
# Test Model - Get the best model
#------------------------------------------------------------------------------
model = mp.f_findModelParameters(X_train2, X_valid2, y_train, y_valid)
MAE = mp.fMAE_scoreModel(model, X_train2, X_valid2, y_train, y_valid) 
#MAE =  mp.fMAE_scoreModel_Split(model, X, y)   
print(' (*)  MAE with RandomForestRegressor: ', int(MAE))
#print(' (*)  MAE score (with split integrate): ', int(MAE))
#XMAE = mp.fXMAE_scoreModel(model, X, y, 10)
#print(' (*)  X-MAE Avg score (across experiments): ', int(XMAE))
#
#
##------------------------------------------------------------------------------
## Test Pipelines
##------------------------------------------------------------------------------
#numerical_transformer = SimpleImputer(strategy = 'median')                                      #'constant'
#categorical_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy = 'constant')),    #'most_frequent'
#                                          ('onehot', OneHotEncoder(handle_unknown = 'ignore'))])
#preprocessor = ColumnTransformer(transformers=[('num', numerical_transformer, numerical_cols),
#                                               ('cat', categorical_transformer, categorical_cols)])
##model_forPip = RandomForestRegressor(random_state = 0, n_estimators = 2000, max_leaf_nodes = 5000)
#model_forPip = model
#my_pipeline = Pipeline(steps = [('preprocessor', preprocessor),('model', model_forPip)])
#my_pipeline.fit(X_train, y_train)
#y_pred = my_pipeline.predict(X_valid)
#MAE = mean_absolute_error(y_valid, y_pred)
#print(' (*)  MAE with Pipelines: ', int(MAE))
#
#
##------------------------------------------------------------------------------
## Cross Validation
##------------------------------------------------------------------------------
#XMAE = mp.fXMAE_scoreModel_pipeline(my_pipeline, X, y, 10)
#print(' (*)  X-MAE Avg score (across experiments): ', int(XMAE))
#
#
##------------------------------------------------------------------------------
## XGBoost
##------------------------------------------------------------------------------
##XG_model = XGBRegressor(random_state = 0, n_jobs = 4, n_estimators=1000, learning_rate=0.1)
#XG_model = XGBRegressor(random_state = 0, n_jobs = 4, n_estimators = 100, learning_rate = 0.1)
#XG_model.fit(X_train, y_train, 
#             early_stopping_rounds = 5,
#             eval_set = [(X_valid, y_valid)],
#             verbose = False)
#y_pred = XG_model.predict(X_valid)
#MAE = mean_absolute_error(y_valid, y_pred)
#print(' (*)  MAE with XGBoost: ', int(MAE))
#XMAE = mp.fXMAE_scoreModel(XG_model, X, y, 10)
#print(' (*)  X-MAE Avg XGBoost (directly from model): ', int(XMAE))







