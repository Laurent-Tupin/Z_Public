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
#XG_model = XGBRegressor(random_state = 0, n_jobs = 4, n_estimators=1000, learning_rate=0.1)
XG_model = XGBRegressor(random_state = 0, n_jobs = 4, 
                        n_estimators = 1000, # [100, 200, 500, 800, 1000]
                        learning_rate = 0.2)

#------------------------------------------------------------------------------
# Pipelines - To Change 
#------------------------------------------------------------------------------
numerical_transformer = SimpleImputer(strategy = 'median')  # (USELESS AS NO NA)
categorical_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy = 'constant')), # (USELESS AS NO NA)
                                          ('onehot', OneHotEncoder(handle_unknown = 'ignore', sparse=False))])
preprocessor = ColumnTransformer(transformers=[('num', numerical_transformer, numerical_cols)
                                               ,('cat', categorical_transformer, categorical_cols)
                                               ])
my_pipeline = Pipeline(steps = [('preprocessor', preprocessor),('model', XG_model)])
print(' - Pipeline done')

#------------------------------------------------------------------------------
my_pipeline.fit(X_train, y_train)
print(' - Model fit')
# Result of prediction
y_pred = my_pipeline.predict(X_valid)
print(' - XG_model done')
# Print Out Result
mape = mp.mape(y_valid, y_pred)

##------------------------------------------------------------------------------
## Fit on the whole data
##------------------------------------------------------------------------------
#XG_model.fit(X, y)
#print(' - Pipeline fit on whole data')


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








