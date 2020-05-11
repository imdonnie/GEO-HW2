import os
import math
import tqdm
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.lines import Line2D
from shapely.geometry import Point
from helper.Tools import geo_path

# [(526811.2368511846, 5705119.536822909), (526844.4996750074, 5705131.935022389), (526886.772578967, 5705144.403342234), (526936.6292131837, 5705168.022665667)]
def splitUtms(x):
    locs = str(x).replace('[(', '').replace(')]', '').split('), (')
    pairs = []
    for index, loc in enumerate(locs[:-1]):
        point_A = [float(i) for i in locs[index].split(', ')]
        point_B = [float(i) for i in locs[index+1].split(', ')]
        pairs.append([point_A, point_B])
    return pairs

def visualizeMatched(data_links, csv_file=os.path.join(geo_path, 'data', 'PointwiseProbes_nodir1.1_10000.csv')):
    points_locations = []
    links_locations = []

    # Load the probes
    data_probes = pd.read_csv(csv_file)
    data_probes = data_probes.drop(["probeID", "Unnamed: 0"], axis=1)

    # Find all the unique samples within the matched probes
    samples = data_probes["sampleID"].unique()

    pbar = tqdm.tqdm(total = samples.shape[0])
    for s in samples:
        pbar.update()

        probes_for_sample = data_probes[data_probes["sampleID"] == s]
        current_probe = probes_for_sample.iloc[0]
        for index, row in probes_for_sample.iterrows():
            current_probe = probes_for_sample.loc[index]
            points_locations.append([current_probe['easting'], current_probe['northing'], current_probe['altitude']])
            link = data_links[data_links["linkPVID"] == current_probe["linkPVID"]]
            locations = splitUtms(link['utms'].iloc[0])
            # altitude = float(str(link['shapeInfo'].iloc[0]).split(' ')[-1].replace(')', ''))
            altitude = 0
            for location in locations:
                links_locations.append(location)

    links_locations = np.array(links_locations)
    # np.savetxt(os.path.join(geo_path, 'data', 'links'), links_locations)
    points_locations = np.array(points_locations)
    # x = points_locations[:,0]
    # y = points_locations[:,1]
    # fig, ax = plt.subplots()
    ax = plt.figure().add_subplot(111, projection='3d')
    i = 0
    for point in points_locations[:100]:
        x = point[0]
        y = point[1]
        z = point[2]
        ax.scatter(x, y, z, c='black', alpha=0.3)
        ax.text(x, y, z, i)
        i += 1

    for link in links_locations[:100]:
        x = link[:,0]
        y = link[:,1]
        # ax.plot(x, y, c='b')
        z = 0
        ax.plot(x, y, z, c='red')
        # line = Line2D(x, y, z, color='red')
        # bx.add_line(line)

    # plt.plot()
    plt.show()

def makeBinary():
    errors = pd.read_csv(os.path.join(geo_path, 'data', 'errors.csv'))
    print
    
def plotDistribution():
    predicted = []
    truth = []
    with open(os.path.join(geo_path, 'data', 'slope.txt')) as f:
        lines = f.readlines()
        for line in lines:
            data = line.strip().split(', ')
            # print(data)
            predicted.append(float(data[0]))
            truth.append(float(data[1]))
    predicted = np.array(predicted)
    truth = np.array(truth)
    print(predicted.shape)
    kwargs = dict()
    plt.hist(predicted, alpha=0.3, bins=10, color='b')
    plt.hist(truth, alpha=0.3, bins=10, color='r')
    plt.show()