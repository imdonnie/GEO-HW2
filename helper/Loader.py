import os
import numpy as np
import tqdm
from helper.MapData import MapPoint, MapLink
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

def parseShapeInfo(id, shape_info):
    sub_links = []
    nodes = shape_info.split('|')
    for i, node in enumerate(nodes[:-1]):
        # Link: cur_node(lat, lon, alt)---nxt_node(lat, lon, alt)
        cur_node = MapPoint(nodes[i].split('/'))
        nxt_node = MapPoint(nodes[i+1].split('/'))
        link = MapLink(cur_node, nxt_node)
        sub_links.append(link)
    return sub_links

def loadLinkData():
    link_data_path = os.path.join(data_path, 'Partition6467LinkData.csv')
    print(INFO, 'Load link data from: {0}'.format(link_data_path))
    links = []
    # load into map data structure
    with open(link_data_path) as link_data_file:
        link_data_lines = link_data_file.readlines()
        for i in tqdm.trange(len(link_data_lines[:])):
            link_data = link_data_lines[i].split(',')
            nodes = link_data[14].split('|')
            for i, node in enumerate(nodes[:-1]):
                # Link: cur_node(lat, lon, alt)---nxt_node(lat, lon, alt)
                cur_node = MapPoint(nodes[i].split('/'))
                nxt_node = MapPoint(nodes[i+1].split('/'))
                sub_link = MapLink(cur_node, nxt_node)
                links.append([link_data[0], sub_link])
    return links
            
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
