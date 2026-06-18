import pandas as pd
import numpy as np
import os
import MainProcess as mp
from collections import OrderedDict
from sklearn.base import clone
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, RandomizedSearchCV
from sklearn.impute import SimpleImputer
from sklearn.metrics import make_scorer
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from xgboost import XGBRegressor


# Path
str_folder = r'C:\Users\Laurent.Tu\Documents\Apprendre Program\Python\GitHub\DS_Positively_Skewed\IHSM_Sample'
str_trainFileName = 'train_data.csv'
str_testFileName = 'oos_data.csv'
target_name = 'Price_USD'
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
l_colToExlude = ['NamePlate','date'] # , 'Length', 'Height', 'Width', 'Curb_Weight','No_of_Gears','plugin','Year'
numerical_cols = [x for x in numerical_cols if not x in l_colToExlude]
categorical_cols = [x for x in categorical_cols if not x in l_colToExlude]
# Choose Column
X = X[categorical_cols + numerical_cols].copy()
X_oss = df_dataRes[categorical_cols + numerical_cols].copy()


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


#X = X.iloc[:5000].copy()
#y = y.iloc[:5000].copy()
#print(X.shape)


#------------------------------------------------------------------------------
# First Parameters : 
test_size = 0.1 #0.3
train_size = 1 - test_size
random_state = 0 #33

# Split between Train and Test
X_train, X_valid, y_train, y_valid = train_test_split(X, y, random_state = random_state,
                                                      train_size = train_size, test_size = test_size)

#------------------------------------------------------------------------------
# XGBoost
#------------------------------------------------------------------------------
XG_model = XGBRegressor()
#XG_model = XGBRegressor(random_state = 0, n_jobs = 4, 
#                        n_estimators = 1000, 
#                        learning_rate = 0.2)
my_pipeline = XG_model


#------------------------------------------------------------------------------
# Hyperparameter Tuning
#------------------------------------------------------------------------------
n_estimators = [int(x) for x in np.linspace(start = 875, stop = 1000, num = 6)]
max_depth = [int(x) for x in np.linspace(2, 4, num = 3)]
max_depth.append(None)
learning_rate = [0.1, 0.2, 0.3, 0.4]
gamma = [0.25, 0.5, 0.75, 1]

random_grid = {'n_estimators': n_estimators,
                'max_depth': max_depth,
                'learning_rate': learning_rate,
                'gamma': gamma}

# Random search of parameters, using 3 fold cross validation, 
# search across 100 different combinations, and use all available cores
rf_random = RandomizedSearchCV(estimator = my_pipeline, param_distributions = random_grid, n_iter = 20, 
                                cv = 3, verbose=2, random_state=42, n_jobs = 4)
print(' ....RandomizedSearchCV')

# Fit the random search model
rf_random.fit(X, y)
print('  => fit...\n')
d_bestParams = rf_random.best_params_
print(d_bestParams, '\n')

n_estimators = d_bestParams['n_estimators']
max_depth = d_bestParams['max_depth']
learning_rate = d_bestParams['learning_rate']
gamma = d_bestParams['gamma']


XG_model_2 = XGBRegressor(random_state = 0, n_jobs = 4, 
                          n_estimators = n_estimators, 
                          max_depth = max_depth,
                          learning_rate = learning_rate,
                          gamma = gamma)
my_pipeline = XG_model_2
print(' - Pipeline done')


##------------------------------------------------------------------------------
## Pipelines - To Change 
##------------------------------------------------------------------------------
#numerical_transformer = SimpleImputer(strategy = 'median')  # (USELESS AS NO NA)
#categorical_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy = 'constant')), # (USELESS AS NO NA)
#                                          ('onehot', OneHotEncoder(handle_unknown = 'ignore', sparse=False))])
#preprocessor = ColumnTransformer(transformers=[('num', numerical_transformer, numerical_cols)
#                                               ,('cat', categorical_transformer, categorical_cols)
#                                               ])
#my_pipeline = Pipeline(steps = [('preprocessor', preprocessor),('model', XG_model)])
#print(' - Pipeline done')

#------------------------------------------------------------------------------
my_pipeline.fit(X_train, y_train)
print(' - Model fit')
# Result of prediction
y_pred = my_pipeline.predict(X_valid)
print(' - XG_model done')
# Print Out Result
mape = mp.mape(y_valid, y_pred)

#------------------------------------------------------------------------------
# Fit on the whole data
#------------------------------------------------------------------------------
my_pipeline.fit(X, y)
print(' - Pipeline fit on whole data')


#------------------------------------------------------------------------------
# Predict Prod
#------------------------------------------------------------------------------
y_oos_pred = my_pipeline.predict(X_oss)
print(' - Predict done on Prod')

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







