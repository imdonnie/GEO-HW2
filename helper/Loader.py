import os
import numpy as np

# change GEO-HW2 path here
geo_path = 'C:\\Users\\Donnie\\Desktop\\NU\\EE395\\hw2\\GEO-HW2'
data_path = os.path.join(geo_path, 'data')

# check the correctness of the data folder
def checkDataFolder():
    std_file_names = ['Partition6467LinkData.csv', 'Partition6467ProbePoints.csv', 'PUT DATA FILES IN THIS FOLDER', 'readme - mapmatching.txt']
    file_names = os.listdir(data_path)
    return [file_name in std_file_names for file_name in file_names] == [True for i in range(4)]

def loadLinkData():
    print('load link data')
    pass

def loadProbePoints():
    print('load probe points')
    pass

# interface to load the target data file
def load(target='link data'):
    if not checkDataFolder():
        print('\033[1;31m[ERROR]\033[0m', 'files in data folder is not correct, please read Readme')
    else:
        funcs = {'link data':loadLinkData, 'probe points':loadProbePoints}
        return funcs[target]
