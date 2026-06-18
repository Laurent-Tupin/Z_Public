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
l_colToExlude = ['NamePlate','date', 'Length', 'Height', 'Width', 'Curb_Weight']  #,'Year'
numerical_cols = [x for x in numerical_cols if not x in l_colToExlude]
categorical_cols = [x for x in categorical_cols if not x in l_colToExlude]
# Choose Column
X = X[categorical_cols + numerical_cols].copy()
X_oss = df_dataRes[categorical_cols + numerical_cols].copy()

##------------------------------------------------------------------------------
## Label Encoding vs One-Hot Encoding
#l_col_lableEncoding = ['Transmission','Turbo','plugin']
#categorical_cols_labelEncode = [x for x in categorical_cols if x in l_col_lableEncoding]
#categorical_cols = [x for x in categorical_cols if not x in l_col_lableEncoding]


#------------------------------------------------------------------------------
# First Parameters : 
test_size = 0.2 #0.3
train_size = 1 - test_size
random_state = 0 #33

# Split between Train and Test
X_train, X_valid, y_train, y_valid = train_test_split(X, y, random_state = random_state,
                                                      train_size = train_size, test_size = test_size)

#print(X_train.shape)


#------------------------------------------------------------------------------
# Pipelines - To Change 
#------------------------------------------------------------------------------
numerical_transformer = SimpleImputer(strategy = 'median')  # (USELESS AS NO NA)
categorical_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy = 'constant')), # (USELESS AS NO NA)
                                          ('onehot', OneHotEncoder(handle_unknown = 'ignore', sparse=False))])
#categorical_transformer_label = Pipeline(steps=[('imputer', SimpleImputer(strategy = 'constant')), # (USELESS AS NO NA)
#                                                ('label', LabelEncoder())])
preprocessor = ColumnTransformer(transformers=[('num', numerical_transformer, numerical_cols)
                                               ,('cat', categorical_transformer, categorical_cols)
                                               #,('cat2', categorical_transformer_label, categorical_cols_labelEncode)
                                               ])
#------------------------------------------------------------------------------
model = RandomForestRegressor(random_state = 0, 
                              n_estimators = 2000, 
                              max_leaf_nodes = 5000,
                              min_samples_split = 2,
                              max_depth = None,
                              criterion = 'mse'
                              )
#------------------------------------------------------------------------------
my_pipeline = Pipeline(steps = [('preprocessor', preprocessor),('model', model)])
my_pipeline.fit(X_train, y_train)
# Result of prediction
y_pred = my_pipeline.predict(X_valid)
mape = mp.mape(y_valid, y_pred)
XMAE = mp.fXMAE_scoreModel_pipeline(my_pipeline, X, y, 5, 'neg_mean_absolute_error')
print(' (*)  X-MAE Avg score (across experiments): ', int(XMAE))


#------------------------------------------------------------------------------
# Create File
#------------------------------------------------------------------------------
# Archives the result File
mp.Hackaton_archPyFiles('.', '.\\Archive', 'submission.csv')

id_col = 'vehicle_id'
y_oos_pred = my_pipeline.predict(X_oss)
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








