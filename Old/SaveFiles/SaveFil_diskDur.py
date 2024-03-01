import time
import os
import datetime as dt
import shutil
import pandas as pd


#------------------------------------------------------------------------------
#--------- Fonctions --------------
#------------------------------------------------------------------------------       
def f_Print(l_row):
    print('\n', l_row)
    return l_row
    
def fBl_FileExist(str_path):
    if os.path.isfile(str_path):    return True
    else:                           return False
    
def fList_FileInDir(str_path, bl_rejectFolder = False):
    try:
        l_fic = os.listdir(str_path)
        if bl_rejectFolder:
            l_fic = [fic for fic in l_fic if not os.path.isdir(os.path.join(str_path,fic))]
    except:
        print(' ERROR in fList_FileInDir')
        print(' - ', str_path)
        raise
    return l_fic

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
        else:   return False      # Folder already exist
    except:
        print(' ERROR: fBl_createDir - Path cannot be tested on its existence ??')
        print(' - ', str_folder)
        raise 
    return False
    
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

def fL_GetListSubFolder_except(str_folder, str_folderExcept = ''):
   if str_folderExcept != '':       return [x[0] for x in os.walk(str_folder) if x[0][:9] != str_folderExcept]
   else:                            return [x[0] for x in os.walk(str_folder)]
   
   
   
   
def fDic_GetTreeFol_FilesWithin(str_folder, l_folderToIgnore = [], l_fileTypeToIgnore = []):
    # Get all the sub Dir in the folder 
    l_subDir = fL_GetListSubFolder_except(str_folder)
    for fol_ignore in l_folderToIgnore:
        l_subDir = [fol for fol in l_subDir if not fol_ignore in fol]
    # Comprehension of dictionary : Get the list of files
    d_fol_lFiles = {fol : fList_FileInDir(fol, bl_rejectFolder = True) 
                    for fol in l_subDir}
    d_fol_lFiles = {k : l_fil for (k,l_fil) in d_fol_lFiles.items() if l_fil}
    return d_fol_lFiles

def fDic_GetAllFilesInTree(str_folder, l_folderToIgnore = [], bl_ignoreDoublons = False):
    # Get all the sub Dir in the folder 
    l_subDir = fL_GetListSubFolder_except(str_folder)
    for fol_ignore in l_folderToIgnore:
        l_subDir = [fol for fol in l_subDir if not fol_ignore in fol]
    # Comprehension of dictionary : Get File and its path
    l_Doublons = []
    d_file_Path = {}
    for fol in l_subDir:
        d_file = {fil : fol for fil in fList_FileInDir(fol, bl_rejectFolder = True)}   
        d_doublons = {fil : fol for (fil,fol) in d_file_Path.items() if fil in d_file}
        # !!!!!! BEWARE of Doublons, on this functions, filename should be unique !!!!!!
        if d_doublons:
            for filname, foldd in d_doublons.items():
                l_Doublons.append( ['DOUBLONS', filname, fol, foldd] )
        d_file_Path = {**d_file_Path, **d_file}    
    
    # !!!!!! BEWARE of Doublons, on this functions, filename should be unique !!!!!!
    if l_Doublons and not bl_ignoreDoublons:
        # Create the Log File
        df = pd.DataFrame(l_Doublons, columns = ['Type','FileName','Path1','Path2'])
        str_Path = r'C:\temp\doublons_{}.csv'.format(dt.date.today().strftime('%Y%m%d'))
        df.to_csv(str_Path, index = False, header = True)
        print('\n DOUBLONS ISSUE !!!')
        print(df)
        print('  CHECK THE FILE on this path: ', str_Path, '\n\n\n\n')
        raise
    # else:
    #     print(d_file_Path)
    return d_file_Path


#------------------------------------------------------------------------------
#--------- Sub --------------
#------------------------------------------------------------------------------
def CopyFiles_FullTree(str_origin, str_dest):
    '''https://docs.python.org/3/library/shutil.html
        UPDATE backward files
        Does not delete files though
    '''
    try:    shutil.copytree(str_origin, str_dest, dirs_exist_ok = True)
    except Exception as err:
        print('ERROR in CopyFiles_FullTree: ', err)
        print(' - ', str_origin)
        print(' - ', str_dest, '\n')


def CopyFiles_UpdateOnlyIfMoreRecent(str_folder_origin, str_folder_dest):
    # PARAM
    ll_log = []
    l_folderToIgnore = [r'\Archive', r'\.git', r'\__pycache__', r'\Lib\site-packages', 
                        r'\.idea', r'\.ipynb_checkpoints', r'\~_pycache__']
    l_fileTypeToIgnore = ['.dll']
    
    # ORIGIN
    d_folLFiles_origin = fDic_GetTreeFol_FilesWithin(str_folder_origin, l_folderToIgnore)
    # # DESTINATION
    # d_folLFiles_dest = fDic_GetTreeFol_FilesWithin(str_folder_dest, l_folderToIgnore)
    
    # Loop of COPY PASTE
    for fol, l_files in d_folLFiles_origin.items():
        fol_dest = fol.replace(str_folder_origin, str_folder_dest)
        
        # FULL folder copy
        if not os.path.exists(fol_dest):
            ll_log.append(f_Print( ['NEW TREE','Full Folder',fol, fol_dest] ))
            CopyFiles_FullTree(fol, fol_dest)
        
        # File by file
        else:
            for file in l_files:
                str_pathOrig = os.path.join(fol, file)
                str_pathDest = os.path.join(fol_dest, file)
                # File to ignore
                if [x for x in l_fileTypeToIgnore if x in file[-len(x):]]:
                    ll_log.append(f_Print( ['IGNORE', file, fol, ''] ))
                    break
                # NEW FILE
                elif not fBl_FileExist(str_pathDest):
                    ll_log.append(f_Print( ['NEW', file, fol, fol_dest] ))
                    shutil.copy(str_pathOrig, str_pathDest)
                # UPDATE
                else:
                    try:
                        dte_lastmod = fDte_GetModificationDate(str_pathOrig)
                        dte_lastmod_dest = fDte_GetModificationDate(str_pathDest)
                        # Compare Date
                        if dte_lastmod > dte_lastmod_dest:
                            ll_log.append(f_Print( ['UPDATE', file, fol, fol_dest] ))
                            shutil.copy(str_pathOrig, str_pathDest)
                    except: ll_log.append(f_Print( ['ERROR', file, fol, fol_dest] ))
    #---------------------------------------------
    # Create the Log File
    df = pd.DataFrame(ll_log, columns = ['Type','FileName','Origin','Destination'])
    str_folder_nickName = str_folder_origin.split('\\')[-1]
    str_logPath = r'C:\temp\log_{}_{}.csv'.format(str_folder_nickName,
                                                  dt.date.today().strftime('%Y%m%d'))
    df.to_csv(str_logPath, index = False, header = True)



def CopyFiles_noUpdate_movePath(str_folder_origin, str_folder_dest):
    # PARAM
    ll_log = []
    l_folderToIgnore = [r'\Archive']
    l_fileTypeToIgnore = ['.dll']
    
    # ORIGIN
    d_filePath_orig = fDic_GetAllFilesInTree(str_folder_origin, l_folderToIgnore)
    # DESTINATION
    d_filePath_dest = fDic_GetAllFilesInTree(str_folder_dest, l_folderToIgnore, bl_ignoreDoublons = True)
    
    # Loop of COPY PASTE
    for file, fol in d_filePath_orig.items():
        fol_dest = fol.replace(str_folder_origin, str_folder_dest)
        str_pathOrig = os.path.join(fol, file)
        str_pathDest = os.path.join(fol_dest, file)
        
        # File to ignore
        if [x for x in l_fileTypeToIgnore if x in file[-len(x):]]:
            ll_log.append(f_Print( ['IGNORE', file, fol, ''] ))
            break
        # NEW FILE
        elif file not in d_filePath_dest:
            ll_log.append(f_Print( ['NEW', file, fol, fol_dest] ))
            shutil.copy(str_pathOrig, str_pathDest)
        # File Already exist
        else:
            str_curentFolDest = d_filePath_dest[file]
            if not str_curentFolDest == fol_dest:
                ll_log.append(f_Print( ['REROOTING', file, str_curentFolDest, fol_dest] ))
                ll_log.append(f_Print( ['TO_DELETE double en dest', file, str_curentFolDest, ''] ))
                shutil.copy(str_pathOrig, str_pathDest)
    #---------------------------------------------
    # Fill in Dest but not in Origin
    for file, fol in d_filePath_dest.items():
        if file not in d_filePath_orig:
            ll_log.append(f_Print( ['TO_DELETE not in source', file, fol, ''] ))
    #---------------------------------------------
    # Create the Log File
    df = pd.DataFrame(ll_log, columns = ['Type','FileName','Origin','Destination'])
    str_folder_nickName = str_folder_origin.split('\\')[-1]
    str_logPath = r'C:\temp\log2_{}_{}.csv'.format(str_folder_nickName,
                                                  dt.date.today().strftime('%Y%m%d'))
    df.to_csv(str_logPath, index = False, header = True)









#------------------------------------------------------------------------------
#__________ Phone __________

#------ Copy File per file: NO UPDATE + Change of Path if needed ------
str_path_Popo_C = r'C:\Users\Laurent.Tu\Videos\Archives\Popo'
str_path_Popo_Phone = r'This PC\Galaxy J5 (2016)\Card\Video\Popo'
# CopyFiles_noUpdate_movePath(str_path_Popo_C , str_path_Popo_Phone)



#------------------------------------------------------------------------------
#__________ Inside Disk (D) __________

#--------- Copy File per file: UPDATE with Date --------------
str_path_C_DocGithub = r'C:\Users\Laurent.Tu\Documents\GitHub'
str_path_D_Github = r'D:\_Save 2017_08 D\GitHub_Save'
# CopyFiles_UpdateOnlyIfMoreRecent(str_path_C_DocGithub , str_path_D_Github)



#------------------------------------------------------------------------------
#__________ Extern Disk (E) __________

#--------- Copy Paste Full Tree --------------
str_path_C_Documents = r'C:\Users\Laurent.Tu\Documents'
str_path_disk1_C = r'E:\Archive_Laurent\xxxxxxxxxx_NEW_FOLDER_xxxxxxxxxxxxxxxx'
# CopyFiles_FullTree(str_path_C_Documents , str_path_disk1_C)

#--------- Copy File per file: UPDATE with Date --------------
str_path_D_Save = r'D:\_Save 2017_08 D'
str_path_E_Save = r'E:\Archive_Laurent\_Save 2017_08 D'
# CopyFiles_UpdateOnlyIfMoreRecent(str_path_D_Save , str_path_E_Save)

#------ Copy File per file: NO UPDATE + Change of Path if needed ------
str_path_D = r'D:'
str_path_E = r'E:\Archive_Laurent'
l_folder = ['Mes images Archive','Musique','Playlists','Video']
#for fol in l_folder:
#    CopyFiles_noUpdate_movePath(str_path_D + '\\' + fol, str_path_E + '\\' + fol)



#------------------------------------------------------------------------------
#__________ Extern: Disk1 (E) to Disk 2 (F) __________

#--------- Copy Paste Full Tree --------------
str_path_disk1 = r'E:\Archive_Laurent'
str_path_disk2 = r'F:\Archive_Laurent'
# CopyFiles_FullTree(str_path_disk1 , str_path_disk2)







print('\n' + 'Fini !!!')
# time.sleep(6)
#input("Press Enter to close the window: ")
