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
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from xgboost import XGBRegressor
import lightgbm

# Path
str_folder = r'C:\Users\Laurent.Tu\Documents\Apprendre Program\Python\GitHub\DS_Positively_Skewed\IHSM_Sample'
str_trainFileName = 'train_data.csv'
str_testFileName = 'oos_data.csv'
target_name = 'Price_USD'
l_yName= [target_name] #['Price_USD', 'year']
id_name = 'vehicle_id'
str_pathTrain = os.path.join(str_folder, str_trainFileName)
str_pathRes = os.path.join(str_folder, str_testFileName)

df_dataTrain = pd.read_csv(str_trainFileName, index_col = id_name)
df_dataRes = pd.read_csv(str_testFileName, index_col = id_name)

# Rows with No Price (useless here)
df_dataTrain.dropna(axis = 0, subset = [target_name], inplace = True)
# split between measure and dimension
y = df_dataTrain[target_name]
X = df_dataTrain.drop([target_name], axis=1)
numerical_cols = X.select_dtypes(include = ['int64', 'float64']).columns.to_list()
categorical_cols = X.select_dtypes(include = ['object']).columns.to_list()

#------------------------------------------------------------------------------
# Exclude Columns
l_colToExlude = ['NamePlate', 'No_of_Gears','Year']  #, 'Length', 'Height', 'Width', 'Curb_Weight','Plugin','date'
numerical_cols = [x for x in numerical_cols if not x in l_colToExlude]
categorical_cols = [x for x in categorical_cols if not x in l_colToExlude]
# Choose Column
X = X[categorical_cols + numerical_cols].copy()
X_oss = df_dataRes[categorical_cols + numerical_cols].copy()

##------------------------------------------------------------------------------
#print(' # Label Encoding')
#l_colLabelEncoding = ['Turbo']  #'Transmission','Turbo'
#categorical_cols = [x for x in categorical_cols if not x in l_colLabelEncoding]
#encoder = LabelEncoder()
#for col in l_colLabelEncoding:
#    X[col] = encoder.fit_transform(X[col])
#    X_oss[col] = encoder.transform(X_oss[col])
#numerical_cols = numerical_cols + l_colLabelEncoding

#------------------------------------------------------------------------------
print(' # onehot Encoding')
OH_encoder = OneHotEncoder(handle_unknown = 'ignore', sparse = False)
OH_cols = pd.DataFrame(OH_encoder.fit_transform(X[categorical_cols]))
OH_cols_oss = pd.DataFrame(OH_encoder.transform(X_oss[categorical_cols]))
# One-hot encoding removed index; put it back
OH_cols.index = X.index
OH_cols_oss.index = X_oss.index
# Remove categorical columns (will replace with one-hot encoding)
num_X = X.drop(categorical_cols, axis=1)
num_X_oss = X_oss.drop(categorical_cols, axis=1)
# Add one-hot encoded columns to numerical features
X = pd.concat([num_X, OH_cols], axis=1)
X_oss = pd.concat([num_X_oss, OH_cols_oss], axis=1)


#X = X.iloc[:1000].copy()
#y = y.iloc[:1000].copy()
#print(X.shape)


#------------------------------------------------------------------------------
# First Parameters : 
test_size = 0.2 #0.3
train_size = 1 - test_size
random_state = 0 #33

# Split between Train and Test
X_train, X_valid, y_train, y_valid = train_test_split(X, y, random_state = random_state,
                                                      train_size = train_size, test_size = test_size)

#------------------------------------------------------------------------------
# Baseline Model
#------------------------------------------------------------------------------
X_valid_2, X_test, y_valid_2, y_test = train_test_split(X_valid, y_valid, random_state = random_state,
                                                    train_size = 0.5, test_size = 0.5)
print(' - Other Split')

dtrain = lightgbm.Dataset(X_train, label = y_train)
dvalid = lightgbm.Dataset(X_valid_2, label = y_valid_2)
print(' - dtrain / dvalid')

## PARAM
##https://lightgbm.readthedocs.io/en/latest/Parameters.html
#l_objective = ['gamma']     #l_objective = ['mse', 'mae', 'mape', 'gamma', 'huber', 'fair']
#l_n_estimators = [1000]     #[int(x) for x in np.linspace(start = 100, stop = 1000, num = 6)]
#l_num_leaves = [300]        #[int(x) for x in np.linspace(start = 100, stop = 10000, num = 10)]
#l_learning_rate = [0.1]     #[0.05, 0.1, 0.2, 0.3, 0.4] [0.09, 0.1, 0.12, 0.15, 0.17]
#l_tree_learner = ['serial'] #['serial', 'feature','data', 'voting']
#                            #l_max_depth = [0,-1,-2,-5,-10,-20,-50]
#l_metric = ['mape']
num_round = 1000            #l_num_round = [100, 500, 900, 1000, 1100, 1200, 1500, 2000, 5000]

param = {'n_jobs': 4,
         'objective': 'gamma',
         'n_estimators': 1000,
         'num_leaves': 300,
         'learning_rate': 0.1,
         'tree_learner' : 'serial',
         'metric' : 'mape'}

#for num_round in l_num_round:
model_bst = lightgbm.train(param, dtrain, 
                           num_round, 
                           valid_sets = [dvalid], 
                           early_stopping_rounds = 10, 
                           verbose_eval = False)
print(' - Train lgb')
y_pred = model_bst.predict(X_test)
print(' - Predict done', '\n', num_round)
# Print Out Result
mape = mp.mape(y_test, y_pred)
#XMAE = mp.fXMAE_scoreModel(model_bst, X, y, 5, 'neg_mean_absolute_error')
#print(' (*)  X-MAE Avg score (across experiments): ', int(XMAE))


#------------------------------------------------------------------------------
# Fit on the whole data
#------------------------------------------------------------------------------
dtrain = lightgbm.Dataset(X_train, label = y_train)
dvalid = lightgbm.Dataset(X_valid, label = y_valid)
model_bst = lightgbm.train(param, dtrain, 
                           num_round, 
                           valid_sets = [dvalid], 
                           early_stopping_rounds = 10, 
                           verbose_eval = False)
print(' - model train on whole data')


#------------------------------------------------------------------------------
# Predict Prod
#------------------------------------------------------------------------------
y_oos_pred = model_bst.predict(X_oss)
print(' - Predict done on Prod')
#print(y_oos_pred[:5], '\n')

#------------------------------------------------------------------------------
# Create File
#------------------------------------------------------------------------------
# Archives the result File
try:    mp.Hackaton_archPyFiles('.', '.\\Archive', 'submission.csv')
except: print('Could not Archive File')

id_col = 'vehicle_id'
df_submit = (pd.DataFrame(y_oos_pred, columns=[target_name], index = X_oss.index)
            .reset_index()
            .rename({'index': id_col}, axis=1))
try:
    df_submit.to_csv('submission.csv', index = False)
except:
    try:
        df_submit.to_csv('submission2.csv', index = False)
    except:
        df_submit.to_csv('submission3.csv', index = False)








