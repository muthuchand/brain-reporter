#!/usr/bin/env python
# coding: utf-8

# Outlier detection - One Class SVM

#Import the libraries needed
import pandas as pd
import glob
import numpy as np
import time
import re
from sklearn import svm
import os


#Read from the input files 
#path - the path of input file 
#path_iqr - path of output file
current_dir = os.getcwd()
path = os.path.join(current_dir,'fcon1000_Beijing_zang_stats')
path_iqr = os.path.join(current_dir,'fcon1000_Beijing_zang_stats_svm')
allFiles = glob.glob(path + "/*.txt")
# print(allFiles)


# Split into train and test files in random - test:train :: 0.1:0.9
# train_files - contains all training file names 
# test_files - contains all test file names
import random
num_tot_files = len(allFiles)
num_test_files = int(0.1*num_tot_files)
# print(num_tot_files,num_test_files)
test_file_index = random.sample(range(len(allFiles)), num_test_files)
print(test_file_index)


# Training files

# Reading each file as a dataframe, and storing it in a list
fileslist = []
frame = pd.DataFrame()
for i in range(len(allFiles)):
    if i not in test_file_index:
        file = allFiles[i]
    #     print(file)
        df = pd.read_csv(file,index_col=None, header=0,delimiter='\t')
        fileslist.append(df)
#print(len(fileslist))


#Convert the list into a vertical stack, and find the column headers
data_2d_array = np.vstack(fileslist)
data_vstack = pd.DataFrame(data_2d_array)
# print(data_vstack.shape)
data_vstack.columns = df.columns.values.tolist()

#Find the unique ROI_IDs and store it 
unique_roi = data_vstack.ROI_ID.unique()


#3D dataframe to be implemented using Panels. Hence reordering the index.
#Data is grouped by ROI_ID. Dict keys are ROI_IDs.
temp_df = pd.DataFrame()
temp_dict = {}
for i in range(len(unique_roi)):
    each_roi = unique_roi[i]
    temp_df = data_vstack[data_vstack['ROI_ID'] == each_roi]
    index_range = range(temp_df.shape[0])
    temp_df['new_ind'] = index_range
    temp_df.set_index('new_ind',inplace=True)
    temp_dict[each_roi] = temp_df
#     print(temp_df)


#Create a panel from the dictionary
p = pd.Panel(temp_dict)
# print(p)


# Test files - Pre process

# Reading each test file as a dataframe, and storing it in a list
testfileslist = []
testframe = pd.DataFrame()
for i in range(len(allFiles)):
    if i in test_file_index:
        file = allFiles[i]
    #     print(file)
        tdf = pd.read_csv(file,index_col=None, header=0,delimiter='\t')
        testfileslist.append(df)
#print(len(testfileslist))


#Convert the list into a vertical stack, and find the column headers
tdata_2d_array = np.vstack(testfileslist)
tdata_vstack = pd.DataFrame(tdata_2d_array)
# print(tdata_vstack.shape)
tdata_vstack.columns = tdf.columns.values.tolist()


#3D dataframe to be implemented using Panels. Hence reordering the index.
#Data is grouped by ROI_ID. Dict keys are ROI_IDs.
ttemp_df = pd.DataFrame()
ttemp_dict = {}
for i in range(len(unique_roi)):
    each_roi = unique_roi[i]
    ttemp_df = tdata_vstack[tdata_vstack['ROI_ID'] == each_roi]
    tindex_range = range(ttemp_df.shape[0])
    ttemp_df['new_ind'] = tindex_range
    ttemp_df.set_index('new_ind',inplace=True)
    ttemp_dict[each_roi] = ttemp_df


#Create a panel from the dictionary
ptest = pd.Panel(ttemp_dict)


# One class SVM : Training and test files

# Train on the training data, and predict on the test data.
p_new = p
ptestnew = ptest
model = svm.OneClassSVM(nu=0.01, kernel='rbf', gamma=0.00001)   
result_list = []
for i in range(len(unique_roi)) :
    each_roi = unique_roi[i]
    df = p_new[each_roi]
    #Store dataframe without ROI_IDs in another dataframe
    df1 = df.drop(columns = 'ROI_ID',inplace=False)
    df1.dropna(inplace=True,axis=1)
    model.fit(df1)

    tdf = ptestnew[each_roi]
    tdf1 = tdf.drop(columns = 'ROI_ID',inplace=False)
    tdf1.dropna(inplace=True,axis=1)
    result = model.predict(tdf1)
    result_list.append(list(result))
#     print(df.shape," and ",tdf.shape)
#     print(result)

# print(result_list)

#Convert results into a dataframe
result_df = pd.DataFrame(result_list)
result_df['new_ind'] = unique_roi
result_df.set_index('new_ind',inplace=True)
print(result_df)


# Write Output files 
#Create new output files
testFiles_new = []
for i in range(len(allFiles)):
    if i in test_file_index:
        file = allFiles[i]
        fnew = re.findall("(?<=_zang_stats)(.*)",file[:-4])
        fnew = path_iqr+fnew[0]+".iqr.txt"
#         print(fnew)
        testFiles_new.append(fnew)


#Check if an ROI has an outlier. 
for i in range(len(testFiles_new)):
    op_data = result_df.iloc[:,i]
#     print(op_data)
    op_data = pd.DataFrame(op_data)
    outlier_list = list(op_data[op_data < 0].stack().index)   
#     print(outlier_list)
    #Write to file 
    with open(testFiles_new[i],'w') as file:
        if len(outlier_list)==0:
            file.write('No Outliers!')
        else:
            for item in outlier_list:
#             file.write(item+"\n")
                file.write(str(item[0])+ '\n')
