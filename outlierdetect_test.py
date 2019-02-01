#!/usr/bin/env python
# coding: utf-8

# Import libraries
import pandas as pd
import glob
import numpy as np


# Read and store the files
path ='C:\\Users\\Muthulakshmi C\\Desktop\\DR\\Week3\\fcon1000_Beijing_zang_stats' # use your path
filenames = glob.glob(path + "/*.txt")
# print(filenames)

fulldata_list = []
frame = pd.DataFrame()
for each_file in filenames:
    df = pd.read_csv(each_file,index_col=None, header=0,delimiter='\t')
    fulldata_list.append(df)

#First store as 2D dataframe
data_array = np.vstack(fulldata_list)
frame_vstck = pd.DataFrame(data_array)
frame_vstck.columns = df.columns.values.tolist()

#Display the column headers  
# list(frame_vstck)

#Creating a dictionary from 2D dataframe for each ROI_ID
c1 = pd.DataFrame()
temp_dict = {}
for each_roi in frame_vstck.ROI_ID.unique():
    c1 = frame_vstck[frame_vstck['ROI_ID'] == each_roi]
    d = range(c1.shape[0])
#     print(d)
    c1['new_ind'] = d
    c1.set_index('new_ind',inplace=True)
#     print(c1)
    temp_dict[each_roi] = c1

#Creating a panel from the dictionary
p = pd.Panel(temp_dict)
print(p)

#Check - the number of unique IDs 
#d = frame_vstck.ROI_ID.unique()
#print(len(d))

#Create a temp dict to store Quartile ranges 
iqr_dict = {}
for every_roi in frame_vstck.ROI_ID.unique() :
    df = p[every_roi]
#     print('ROI :',every_roi)
    df1 = df.drop('ROI_ID',axis = 1, inplace=False)
    Q1 = df1.quantile(0.25)
    Q3 = df1.quantile(0.75)
    IQR = Q3 - Q1
    iqr_dict[every_roi] = [Q1,Q3]
#     print(IQR)
#     print((df < (Q1 - 1.5 * IQR))|(df > (Q3 + 1.5 * IQR)))


#Some test file 
test_file = pd.read_csv('sub08455_T1w.roiwise.stats.txt',delimiter='\t')

#Check outliers 
for every_roi in test_file.ROI_ID.unique() :
    all_stat = test_file[test_file['ROI_ID'] == every_roi]
    roi_stat = all_stat.drop('ROI_ID',axis = 1, inplace=False)
    iqr_info = iqr_dict[every_roi]
    q1 = iqr_dict[every_roi][0]
    q3 = iqr_dict[every_roi][1]
    iqr = q3 - q1
    print((roi_stat < (q1 - 1.5 * iqr))|(roi_stat > (q3 + 1.5 * iqr)))
    
# for every_roi in x :
# df_iqr = pd.DataFrame()
# for every_roi in test_file.ROI_ID.unique() :
#     all_stat = test_file[test_file['ROI_ID'] == every_roi]
#     roi_stat = all_stat.drop('ROI_ID',axis = 1, inplace=False)
#     iqr_info = iqr_dict[every_roi]
#     q1 = iqr_dict[every_roi][0]
#     q3 = iqr_dict[every_roi][1]
#     iqr = q3 - q1
#     temp =(roi_stat < (q1 - 1.5 * iqr))|(roi_stat > (q3 + 1.5 * iqr)) 
#     temp2 = pd.DataFrame(data = temp)
#     print(temp2.shape)
#     df_iqr.append(temp2)
