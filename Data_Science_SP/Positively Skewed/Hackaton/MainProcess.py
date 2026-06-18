#from learntools.core import binder
#binder.bind(globals())

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
import lightgbm as lgb


#------------------------------------------------------------------------------
# Score Model
#------------------------------------------------------------------------------
def mape(y_true, y_pred):
    y_val = np.maximum(np.array(y_true), 1e-8)
    MAE = np.abs(y_true - y_pred).mean()
    print('   MAE', MAE)
    mape = (np.abs(y_true - y_pred)/y_val).mean()
    print('   mape', mape * 100)
    return mape

def fMAE_scoreModel(o_model, X_t, X_v, y_t, y_v):
    o_model.fit(X_t, y_t)
    y_pred = o_model.predict(X_v)
    #mape(y_v, y_pred)
    MAE = mean_absolute_error(y_v, y_pred)
    return MAE

def fMAE_scoreModel_Split(o_model, X, y):
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size = 0.8, test_size = 0.2, random_state = 0)
    o_model.fit(X_train, y_train)
    y_pred = o_model.predict(X_valid)
    MAE = mean_absolute_error(y_valid, y_pred)
    return MAE

def fXMAE_scoreModel_pipeline(o_Pipeline, X, y, int_cv = 5, str_scoring = 'neg_mean_absolute_error'):
    l_MAE = -1 * cross_val_score(o_Pipeline, X, y, cv = int_cv, scoring = str_scoring)
    return l_MAE.mean()
    
def fXMAE_scoreModel(o_model, X, y, int_cv = 5, str_scoring = 'neg_mean_absolute_error'):
    # Filter Num and Categ Columns
    numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.to_list()
    categorical_cols = X.select_dtypes(include=['object']).columns.to_list()
    # Fonction de transformation
    numerical_transformer = SimpleImputer(strategy = 'median')
    categorical_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy = 'constant')),            #'most_frequent'
                                              ('onehot', OneHotEncoder(handle_unknown = 'ignore'))])
    # Preprocess Data
    preprocessor = ColumnTransformer(transformers=[('num', numerical_transformer, numerical_cols),
                                                   ('cat', categorical_transformer, categorical_cols)])
    # Pipeline Data And Model
    my_pipeline = Pipeline(steps = [('preprocessor', preprocessor),('model', o_model)])
    XMAE = fXMAE_scoreModel_pipeline(my_pipeline, X, y, int_cv, str_scoring)
    return XMAE
    
    
    
    
    
    


#------------------------------------------------------------------------------
# CLEAN DATA
#------------------------------------------------------------------------------
def fBl_IsColEmpty(df, flt_pct = 0.5):
    # Check the number of NA per column first (if more than 50%... maybe delete the column will be better)
    num_rows = df.shape[0]
    X_nbNA = (df.isnull().sum())
    l_nbNA = [i_col for i_col in X_nbNA if i_col > num_rows * flt_pct]
    if l_nbNA:
        print('-------------------------------------------')
        print('df has {} nb of rows'.format(num_rows))
        print(' - Missing value per column: ')
        print(X_nbNA[X_nbNA > 0])
        print(' - Consider deleting the column')
        print('\n')
        
        
#------------------------------------------------------------------------------
# Chose the best way to clean DATA
#------------------------------------------------------------------------------ 
def f_CompareDataMethod(o_model, X_t, X_v, y_train, y_valid):
    d_choice = {}
    l_cols_wNA = [col for col in X_t.columns if X_t[col].isnull().any() or X_v[col].isnull().any()]
    if not l_cols_wNA:
        print("  * No column with missing values")
        return 0, d_choice
    int_MAE_dropCol = fMAE_dropCol(o_model, l_cols_wNA, X_t, X_v, y_train, y_valid)
    int_MAE_ImputerMean = fMAE_Imputer(o_model, l_cols_wNA, X_t, X_v, y_train, y_valid, 'mean')
    int_MAE_ImputerMean_keepM = fMAE_Imputer(o_model, l_cols_wNA, X_t, X_v, y_train, y_valid, 'mean', True)
    int_MAE_ImputerMedian = fMAE_Imputer(o_model, l_cols_wNA, X_t, X_v, y_train, y_valid, 'median')
    int_MAE_ImputerMedian_keepM = fMAE_Imputer(o_model, l_cols_wNA, X_t, X_v, y_train, y_valid, 'median', True)
    int_MAE_ImputerConst = fMAE_Imputer(o_model, l_cols_wNA, X_t, X_v, y_train, y_valid, 'constant')
    #    int_MAE_ImputerConst_keepM = fMAE_Imputer(o_model, l_cols_wNA, X_t, X_v, y_train, y_valid, 'constant', True)
    
    d_choice[int_MAE_dropCol] = [0, 'Drop columns']
    d_choice[int_MAE_ImputerMean] = [1, 'Imputer Mean']
    d_choice[int_MAE_ImputerMean_keepM] = [2, 'Imputer Mean Keep missing']
    d_choice[int_MAE_ImputerMedian] = [3, 'Imputer median']
    d_choice[int_MAE_ImputerMedian_keepM] = [4, 'Imputer Median Keep missing']
    d_choice[int_MAE_ImputerConst] = [5, 'Imputer constant']
    #    d_choice[int_MAE_ImputerConst_keepM] = [6, 'Imputer constant Keep missing']
    
    int_MAE = min([int_MAE_dropCol, int_MAE_ImputerMean, int_MAE_ImputerMedian, 
                   int_MAE_ImputerMean_keepM, int_MAE_ImputerMedian_keepM,
                   int_MAE_ImputerConst])
    return int_MAE, d_choice

def fMAE_dropCol(o_model, l_cols_wNA, X_t, X_v, y_train, y_valid):
    X_t_reduced = X_t.drop(l_cols_wNA, axis=1)
    X_v_reduced = X_v.drop(l_cols_wNA, axis=1)
    if len(X_t_reduced.columns) > 0:
        MAE = fMAE_scoreModel(o_model, X_t_reduced, X_v_reduced, y_train, y_valid)
    else:
        print('  fMAE_dropCol return no Columns. Drop This idea')
        return 1000000000
    return MAE

def fMAE_Imputer(o_model, l_cols_wNA, X_t, X_v, y_train, y_valid, str_strategy = 'mean', bl_keepMissingCol = False):
    if bl_keepMissingCol:
        X_t_imputed, X_v_imputed = fDf_replaceNAImputer_keepMissing(X_t, X_v, l_cols_wNA, str_strategy)
    else:
        X_t_imputed, X_v_imputed = fDf_replaceNAImputer(X_t, X_v, str_strategy)
    MAE = fMAE_scoreModel(o_model, X_t_imputed, X_v_imputed, y_train, y_valid)
    return MAE

def fDf_replaceNAImputer(X_train, X_valid, str_strategy = 'mean'):
    # Replace missing values with the mean value along each column
    my_imputer = SimpleImputer(strategy = str_strategy)
    imputed_X_train = pd.DataFrame(my_imputer.fit_transform(X_train))
    imputed_X_valid = pd.DataFrame(my_imputer.transform(X_valid))
    # Imputation removed column names; put them back
    imputed_X_train.columns = X_train.columns
    imputed_X_valid.columns = X_valid.columns
    return imputed_X_train, imputed_X_valid

def fDf_replaceNAImputer_keepMissing(X_train, X_valid, l_cols_wNA, str_strategy = 'mean'):
    X_train_plus = X_train.copy()
    X_valid_plus = X_valid.copy()
    for col in l_cols_wNA:
        X_train_plus[col + '_was_missing'] = X_train_plus[col].isnull()
        X_valid_plus[col + '_was_missing'] = X_valid_plus[col].isnull()
    X_train_plus, X_valid_plus = fDf_replaceNAImputer(X_train_plus, X_valid_plus, str_strategy)
    return X_train_plus, X_valid_plus


#------------------------------------------------------------------------------
# Reform Data
#------------------------------------------------------------------------------   
def f_RefundData(X_t, X_v, i_choice = 4):
    l_cols_wNA = [col for col in X_t.columns if X_t[col].isnull().any() or X_v[col].isnull().any()]
    if i_choice == 0:
        print('You need to write the code if delete column need to be deleted. also for X_Res and y_res')
        return X_t, X_v
    elif i_choice == 1:
        X_train, X_valid = fDf_replaceNAImputer(X_t, X_v, 'mean')
    elif i_choice == 2:
        X_train, X_valid = fDf_replaceNAImputer_keepMissing(X_t, X_v, l_cols_wNA, 'mean')
    elif i_choice == 3:
        X_train, X_valid = fDf_replaceNAImputer(X_t, X_v, 'median')
    elif i_choice == 4:
        X_train, X_valid = fDf_replaceNAImputer_keepMissing(X_t, X_v, l_cols_wNA, 'median')
    elif i_choice == 5:
        X_train, X_valid = fDf_replaceNAImputer(X_t, X_v, 'constant')
    elif i_choice == 6:
        X_train, X_valid = fDf_replaceNAImputer_keepMissing(X_t, X_v, l_cols_wNA, 'constant')
    else:
        print('   ERROR In f_RefundData: NEED to fill another i_choice: {}'.format(str(i_choice)))
        return X_t, X_v
    return X_train, X_valid
    

#------------------------------------------------------------------------------
# Test Model - Get the best parameters with 'RandomForestRegressor' model
#------------------------------------------------------------------------------
def f_findModelParameters(X_train, X_valid, y_train, y_valid):
    i_samplesSplit = 2
#    i_samplesSplit = fInt_Get_min_samples_split(X_train, X_valid, y_train, y_valid, [2,10,30,50,70])
#    print('   i_samplesSplit: ', i_samplesSplit)
    i_estim = 2000
#    i_estim = fInt_Get_n_estimators(X_train, X_valid, y_train, y_valid, [10,50,100,200,500,1000,2000,5000], i_samplesSplit)
#    print('   i_estim: ', i_estim)
    i_maxLeafNodes = 5000
#    i_maxLeafNodes = fInt_Get_max_leaf_nodes(X_train, X_valid, y_train, y_valid, [None,5,100,500,5000,10000], i_samplesSplit, i_estim)
#    print('   i_maxLeafNodes: ', i_maxLeafNodes)
    i_maxDepth = None
#    i_maxDepth = fInt_Get_max_depth(X_train, X_valid, y_train, y_valid, [None,1,20,50], i_samplesSplit, i_estim, i_maxLeafNodes)
#    print('   i_maxDepth: ', i_maxDepth)
    str_criterion = 'mse'
#    str_criterion = fInt_Get_criterion(X_train, X_valid, y_train, y_valid, ['mse','mae'], i_samplesSplit, i_estim, i_maxLeafNodes, i_maxDepth)
#    print('   str_criterion: ', str_criterion)
    model = RandomForestRegressor(random_state = 0,min_samples_split = i_samplesSplit, n_estimators = i_estim, 
                                  max_leaf_nodes = i_maxLeafNodes, max_depth = i_maxDepth, criterion = str_criterion)
    return model

def fInt_Get_min_samples_split(X_train, X_valid, y_train, y_valid, l_toTest):
    df_MAE = pd.DataFrame(columns = ['MAE', 'XMAE', 'min_samples_split'])
    for i_samplesSplit in l_toTest:
        model = RandomForestRegressor(random_state = 0,min_samples_split = i_samplesSplit)
        MAE = fMAE_scoreModel(model, X_train, X_valid, y_train, y_valid)
        XMAE = fXMAE_scoreModel(model, pd.concat([X_train, X_valid]), pd.concat([y_train, y_valid]), 10)
        df_MAE.loc[len(df_MAE)] = [MAE, XMAE, i_samplesSplit]
    df_MAE.sort_values(by = ['XMAE'], ascending = True, inplace = True)
    try:        return int(df_MAE['min_samples_split'].values[0])
    except:     return None

def fInt_Get_n_estimators(X_train, X_valid, y_train, y_valid, l_toTest, i_samplesSplit):
    df_MAE = pd.DataFrame(columns = ['MAE', 'XMAE', 'min_samples_split', 'n_estimators'])
    for i_estim in l_toTest:
        model = RandomForestRegressor(random_state = 0,min_samples_split = i_samplesSplit, n_estimators = int(i_estim))
        MAE = fMAE_scoreModel(model, X_train, X_valid, y_train, y_valid)
        XMAE = fXMAE_scoreModel(model, pd.concat([X_train, X_valid]), pd.concat([y_train, y_valid]), 10)
        df_MAE.loc[len(df_MAE)] = [MAE, XMAE, i_samplesSplit, i_estim]
    df_MAE.sort_values(by = ['XMAE'], ascending = True, inplace = True)
    try:        return int(df_MAE['n_estimators'].values[0])
    except:     return None

def fInt_Get_max_leaf_nodes(X_train, X_valid, y_train, y_valid, l_toTest, i_samplesSplit, i_estim):
    df_MAE = pd.DataFrame(columns = ['MAE', 'XMAE', 'min_samples_split', 'n_estimators', 'max_leaf_nodes'])
    for i_leafNodes in l_toTest:
        model = RandomForestRegressor(random_state = 0,min_samples_split = i_samplesSplit, n_estimators = i_estim, max_leaf_nodes = i_leafNodes)
        MAE = fMAE_scoreModel(model, X_train, X_valid, y_train, y_valid)
        XMAE = fXMAE_scoreModel(model, pd.concat([X_train, X_valid]), pd.concat([y_train, y_valid]), 10)
        df_MAE.loc[len(df_MAE)] = [MAE, XMAE, i_samplesSplit, i_estim, i_leafNodes]
    df_MAE.sort_values(by = ['XMAE'], ascending = True, inplace = True)
    try:        return int(df_MAE['max_leaf_nodes'].values[0])
    except:     return None
    
def fInt_Get_max_depth(X_train, X_valid, y_train, y_valid, l_toTest, i_samplesSplit, i_estim, i_leafNodes):
    df_MAE = pd.DataFrame(columns = ['MAE', 'XMAE', 'min_samples_split', 'n_estimators', 'max_leaf_nodes', 'max_depth'])
    for i_maxDepth in l_toTest:
        model = RandomForestRegressor(random_state = 0,min_samples_split = i_samplesSplit, n_estimators = i_estim, 
                                      max_leaf_nodes = i_leafNodes, max_depth = i_maxDepth)
        MAE = fMAE_scoreModel(model, X_train, X_valid, y_train, y_valid)
        XMAE = fXMAE_scoreModel(model, pd.concat([X_train, X_valid]), pd.concat([y_train, y_valid]), 10)
        df_MAE.loc[len(df_MAE)] = [MAE, XMAE, i_samplesSplit, i_estim, i_leafNodes, i_maxDepth]
    df_MAE.sort_values(by = ['XMAE'], ascending = True, inplace = True)
    try:        return int(df_MAE['max_depth'].values[0])
    except:     return None
    
def fInt_Get_criterion(X_train, X_valid, y_train, y_valid, l_toTest, i_samplesSplit, i_estim, i_leafNodes, i_maxDepth):
    df_MAE = pd.DataFrame(columns = ['MAE', 'XMAE', 'min_samples_split', 'n_estimators', 'max_leaf_nodes', 'max_depth', 'criterion'])
    for str_criterion in l_toTest:
        model = RandomForestRegressor(random_state = 0,min_samples_split = i_samplesSplit, n_estimators = i_estim, 
                                      max_leaf_nodes = i_leafNodes, max_depth = i_maxDepth, criterion = str_criterion)
        MAE = fMAE_scoreModel(model, X_train, X_valid, y_train, y_valid)
        XMAE = fXMAE_scoreModel(model, pd.concat([X_train, X_valid]), pd.concat([y_train, y_valid]), 10)
        df_MAE.loc[len(df_MAE)] = [MAE, XMAE, i_samplesSplit, i_estim, i_leafNodes, i_maxDepth, str_criterion]
    df_MAE.sort_values(by = ['XMAE'], ascending = True, inplace = True)
    try:        return str(df_MAE['str_criterion'].values[0])
    except:     return None


#------------------------------------------------------------------------------
#--------- To Archives  --------------
#------------------------------------------------------------------------------
import shutil
import datetime as dt

#------------------------------------------------------------------------------
# List Files in folder
#------------------------------------------------------------------------------
def fStr_BuildPath(str_folder, str_FileName):
    if str_FileName == '':      str_path = str_folder
    elif str_folder == '':      str_path = str_FileName
    else:                       str_path = os.path.join(str_folder, str_FileName)
    return str_path
    
def fBl_FileExist(str_path):
    if os.path.isfile(str_path):    return True
    else:                           return False

def fBl_FolderExist(str_path):
    if os.path.exists(str_path):    return True
    else:                           return False
    
def fList_FileInDir(str_path):
    try:        l_fic = os.listdir(str_path)
    except:
        print(' ERROR in fList_FileInDir')
        print(' - ', str_path)
        raise
    return l_fic

def fList_FileInDir_Txt(str_path):
    try:
        l_fic = os.listdir(str_path)
        l_fic = [fic for fic in l_fic if '.txt' in fic]
    except:
        print(' ERROR in fList_FileInDir_Txt')
        print(' - ', str_path)
        raise
    return l_fic

def fList_FileInDir_Csv(str_path):
    try:
        l_fic = os.listdir(str_path)
        l_fic = [fic for fic in l_fic if '.csv' in fic]
    except:
        print(' ERROR in fList_FileInDir_Csv')
        print(' - ', str_path)
        raise
    return l_fic

def fList_FileInDir_Py(str_path):
    try:
        l_fic = os.listdir(str_path)
        l_fic = [fic for fic in l_fic if '.py' in fic]
    except:
        print(' ERROR in fList_FileInDir_Py')
        print(' - ', str_path)
        raise
    return l_fic

def UpdateTxtFile(str_path, str_old, str_new = ''):
    with open(str_path, 'r') as file :
        str_text = file.read()
    # Replace the target string
    str_text = str_text.replace(str_old, str_new)
    # Write the file out again
    with open(str_path, 'w') as file:
        file.write(str_text)

def fL_GetListSubFolder_except(str_folder, str_folderExcept = ''):
   if str_folderExcept != '':       return [x[0] for x in os.walk(str_folder) if x[0][:9] != str_folderExcept]
   else:                            return [x[0] for x in os.walk(str_folder)]
   

def fL_GetListDirFileInFolders(l_subDir, l_typeFile = []):
    listTuple_PathFic = []
    if l_typeFile:
        for Dir in l_subDir:
            list_fic = [(Dir, fic) for fic in fList_FileInDir(Dir) if fic[-3:].lower() in l_typeFile or fic[-4:].lower() in l_typeFile]
            if list_fic: listTuple_PathFic += list_fic
    else:
        for Dir in l_subDir:
            list_fic = [(Dir, fic) for fic in fList_FileInDir(Dir)]
            if list_fic: listTuple_PathFic += list_fic
    #    for Dir in l_subDir:
    #        if l_typeFile:
    #            list_fic = [(Dir, fic) for fic in fList_FileInDir(Dir) if fic[-3:] in l_typeFile or fic[-4:] in l_typeFile]
    #        else: 
    #            list_fic = [(Dir, fic) for fic in fList_FileInDir(Dir)]
    #        if list_fic: listTuple_PathFic += list_fic
    return listTuple_PathFic

def fBl_createDir(str_folder):
    try:
        if not os.path.exists(str_folder):
            try: 
                os.makedirs(str_folder)
                return True
            except:
                print(' ERROR: fBl_createDir - Program could NOT create the Dir')
                print(' - ', str_folder)
                raise
        else: 
            return False      # Folder already exist
    except:
        print(' ERROR: fBl_createDir - Path cannot be tested on its existence ??')
        print(' - ', str_folder)
        raise 
    return False

def Act_CopyUpdateFiles(l_PathFic_from, l_PathFic_dest, str_originFolder_replacedByDestFolder = '', str_removeInDestFolder = ''):
    if str_originFolder_replacedByDestFolder == '':
        print('Fill the 3rd argument on the function: Act_CopyUpdateFiles')
        return False
    # Loop on File to copy / update them
    for t_file in l_PathFic_from:
        str_path = t_file[0]
        str_file = t_file[1]
        str_path_Dest = str_path.replace('.', str_originFolder_replacedByDestFolder)
        str_path_Dest = str_path_Dest.replace(str_removeInDestFolder, '')
        
        # If file is new --> Copy
        if (str_path_Dest, str_file) not in l_PathFic_dest:
            print('COPY NEW...   ', 'Folder Origin:   ' + str_path, ' ||| Folder Dest:   ' + str_path_Dest, ' ||| File:   ' + str_file)
            fBl_createDir(str_path_Dest)
            shutil.copyfile(str_path + '\\' + str_file, str_path_Dest + '\\' + str_file)
        else:
            dte_lastmod = fDte_GetModificationDate(str_path + '\\' + str_file)
            dte_lastmod_dest = fDte_GetModificationDate(str_path_Dest + '\\' + str_file)
            # Compare Date
            if dte_lastmod > dte_lastmod_dest:
                print('COPY UPDATE...', 'Folder Origin:   ' + str_path, ' ||| Folder Dest:   ' + str_path_Dest, ' ||| File:   ' + str_file)
                if '.\\Archive' in str_originFolder_replacedByDestFolder:
                    str_dateTime =  str(dte_lastmod_dest.strftime('%Y%m%d'))
                    shutil.copyfile(str_path_Dest + '\\' + str_file, str_path_Dest + '\\' + str_dateTime + '_' + str_file)
                shutil.copyfile(str_path + '\\' + str_file, str_path_Dest + '\\' + str_file)
    return True

def fDte_GetModificationDate(str_pathFile):
    try:
        if fBl_FileExist(str_pathFile):
            dte_modif = os.path.getmtime(str_pathFile)
            dte_modif = dt.datetime.fromtimestamp(dte_modif)
            return dte_modif
        else:
            print('  fDte_GetModificationDate: File does not exist: ')
            print('  - str_pathFile: ', str_pathFile)
            return -1
    except:
        print(' ERROR in fDte_GetModificationDate')
        print(' - ', str_pathFile)
        raise
    return True


def Act_CopyUpdateFiles_specialBackUp(l_FolderFic_from, str_DestFolder, int_onlyFileMoreRecentThan = 7, str_removeInDestFolder = ''):
    # Loop on File to copy / update them
    for t_file in l_FolderFic_from:
        str_folder = t_file[0]
        str_file = t_file[1]
        str_pathOrigin = os.path.join(str_folder, str_file)
        
        str_folder_Dest = str_folder.replace('.', str_DestFolder)
        str_folder_Dest = str_folder_Dest.replace(str_removeInDestFolder, '')
        str_pathDest = os.path.join(str_folder_Dest, str_file)
        
        # Process Only if more recent for 7 days (7 for example)
        dte_lastmod = fDte_GetModificationDate(str_pathOrigin)
        dte_limit = dt.datetime.now() - dt.timedelta(int_onlyFileMoreRecentThan)
        
        if dte_lastmod > dte_limit:
            # If File DOES NOT Exists
            if not fBl_FileExist(str_pathDest):
                print('COPY NEW...   ', 'Folder Origin:   ' + str_folder, ' ||| Folder Dest:   ' + str_folder_Dest, ' ||| File:   ' + str_file)
                fBl_createDir(str_folder_Dest)
                shutil.copyfile(str_pathOrigin, str_pathDest)
            else:
                # Compare Date (Update only if CLoud is more recent)
                dte_lastmod_dest = fDte_GetModificationDate(str_pathDest)
                if dte_lastmod > dte_lastmod_dest:
                    print('COPY UPDATE...', 'Folder Origin:   ' + str_folder, ' ||| Folder Dest:   ' + str_folder_Dest, ' ||| File:   ' + str_file)
                    shutil.copyfile(str_pathOrigin, str_pathDest)
    return True


        
def Hackaton_archPyFiles(str_folderFrom = '.', str_folderDest = '.\\Archive', str_fileName = 'submission.csv'):
    # Get all the sub Dir in the folder -- Split btw Archive and the rest
    l_subDir = fL_GetListSubFolder_except(str_folderFrom, '.\\Archive')
    l_subDirArch = fL_GetListSubFolder_except(str_folderDest, '')
    # Get Tuples in Liste (Path, File Python)
    l_PathFic = fL_GetListDirFileInFolders(l_subDir, [str_fileName])
    l_PathFic_Arch = fL_GetListDirFileInFolders(l_subDirArch)
    # Copy / Update files from a list of tuple to another
    Act_CopyUpdateFiles(l_PathFic, l_PathFic_Arch, '.\\Archive')
    