#!/usr/bin/env python
# coding: utf-8

# ## Outlier detection_IQR

#Import the libraries needed
import pandas as pd
import glob
import numpy as np
import time
import re
import os

# #Calculate start time 
# start_time = time.time()

#Read from the input files 
#path - the path where the input files are located
#path_iqr - new path for output files
current_dir = os.getcwd()
path = os.path.join(current_dir,'fcon1000_Beijing_zang_stats')
path_iqr = os.path.join(current_dir,'fcon1000_Beijing_zang_stats_text')
allFiles = glob.glob(path + "/*.txt")



#Reading each file as a dataframe, and storing it in a list
fileslist = []
frame = pd.DataFrame()
for i in range(len(allFiles)):
    file = allFiles[i]
#     print(file)
    df = pd.read_csv(file,index_col=None, header=0,delimiter='\t')
    fileslist.append(df)


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


#Make a copy of the panel. 
#Find IQR of each column for the specified quartiles. 
#Check if each entry is in the IQR - output False if no outlier, True if it is an outlier. 
p_new = p
for i in range(len(unique_roi)) :
    each_roi = unique_roi[i]
    df = p_new[each_roi]
    Q1 = df.quantile(0.1)
    Q3 = df.quantile(0.9)
    IQR = Q3 - Q1
#     print(IQR)
    df_new = (df < (Q1 - 1.5 * IQR))|(df > (Q3 + 1.5 * IQR))
    p_new[each_roi] = df_new


#Create new output file names 
allFiles_new = []
# #TO write to the same folder as input folder. Need to delete output files every time 
# for i in range(len(allFiles)):
#     file = allFiles[i]
#     fnew = file[:-4]
#     fnew = fnew+".iqr.txt"
#     allFiles_new.append(fnew)
# #     print(fnew)

# Write the files to a different output folder 
for i in range(len(allFiles)):
    file = allFiles[i]
    fnew = re.findall("(?<=_zang_stats)(.*)",file[:-4])
    fnew = path_iqr+fnew[0]+".iqr.txt"
    allFiles_new.append(fnew)
#     print(fnew)



#Write each row of every dataframe in the panel (i.e data of each subject across all ROIs) into the file with the same name. 
for i in range(len(allFiles_new)):
    #Create a new dataframe, taking ROI of each subject
    dfnew = pd.DataFrame(columns = data_vstack.columns)
    for j in range(len(unique_roi)):
        every_roi = unique_roi[j]
        f = p_new[every_roi].iloc[i]
        dfnew = dfnew.append(f)
    #Do some post - processing operations to have the ROI_ID as integers
    dfnew.drop('ROI_ID', axis=1, inplace=True)
    dfnew.insert(loc=0, column='ROI_ID', value=unique_roi)
#     print(dfnew)
    #Do dome post - processing to display the output in 0/1 form
    dfnew = dfnew.astype(int)
    
    #Write to the respective file separated by tabspaces
    dfnew.to_csv(allFiles_new[i], sep='\t', encoding='utf-8',index=False)


# #Calculate end time 
# end_time = time.time()
# total_time = end_time - start_time
# print('Total time taken : ',total_time)

