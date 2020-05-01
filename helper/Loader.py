import os
import numpy as np
import tqdm

# change GEO-HW2 path here
geo_path = 'C:\\Users\\Donnie\\Desktop\\NU\\EE395\\hw2\\GEO-HW2'
data_path = os.path.join(geo_path, 'data')

INFO = '\033[1;32m[INFO]\033[0m'
ERROR = '\033[1;31m[ERROR]\033[0m'
WARNING = '\033[1;33m[WARNING]\033[0m'

# check the correctness of the data folder
def checkDataFolder():
    std_file_names = ['Partition6467LinkData.csv', 'Partition6467ProbePoints.csv', 'PUT DATA FILES IN THIS FOLDER', 'readme - mapmatching.txt']
    file_names = os.listdir(data_path)
    return [file_name in std_file_names for file_name in file_names] == [True for i in range(4)]

def loadLinkData():
    link_data_path = os.path.join(data_path, 'Partition6467LinkData.csv')
    print(INFO, 'Load link data from: {0}'.format(link_data_path))
    with open(link_data_path) as link_data:
        link_data_lines = link_data.readlines()
        print(len(link_data_lines))
    # link_data = np.genfromtxt(link_data_path, delimiter=',')
    # print(INFO, 'Link data shape:{0}'.format(link_data.shape))

def loadProbePoints():
    probe_points_path = os.path.join(data_path, 'Partition6467ProbePoints.csv')
    print(INFO, 'Load probe points from: {0}'.format(probe_points_path))
    res = []
    with open(probe_points_path) as probe_points_data:
        probe_points = probe_points_data.readlines()
        for i in tqdm.trange(len(probe_points)):
            res.append(probe_points[i].split(','))
    res = np.array(res)
    return res
    # probe_points = np.genfromtxt(probe_points_path, delimiter=',')
    # print(INFO, 'Probe points shape:{0}'.format(probe_points.shape))
    pass

# interface to load the target data file
def load(target='link data'):
    if not checkDataFolder():
        print(ERROR, 'files in data folder is not correct, please read Readme')
    else:
        funcs = {'link data':loadLinkData, 'probe points':loadProbePoints}
        return funcs[target]()
