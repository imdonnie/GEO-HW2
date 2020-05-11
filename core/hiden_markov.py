# Helps to convert lat long to UTM coordinates
import math
# Standard python package for data manipulation
import numpy as np
import pandas as pd
# Python packages for handling geo objects and calculating distances
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import nearest_points
import os
import geopandas
from matplotlib import pyplot as plt
from tqdm import tqdm

def generate_hmm(data_links, data_probes):
    spatial_index = data_links.sindex
    beta = 300
    sigma = 400
    hmm = []
    emissions = []
    projections = []
    transitions = []
    distances = []
    match_points = []
    previous_probe = None
    Probe_Points = []
    index = []
    for i in data_probes["probeID"]:
        probe = data_probes.loc[i]
        index.append(i)
        possible_matches_index = list(spatial_index.nearest((probe["shape"].x, probe["shape"].y), 3))
        hmm.append(possible_matches_index[0:3])
        layer_emmissions = []
        layer_projections = []
        layer_transitions = []
        layer_distances = []
        layer_links_node = [] #
        layer_nearest= []
        point = Point(probe["easting"], probe["northing"])
        Probe_Points.append([probe["easting"], probe["northing"]])

        for p in possible_matches_index:
            link = data_links.loc[p]
            link_node = data_links.loc[p,["refNodeID", "nrefNodeID"]]#
            utms = link["utms"][2:-2].replace("), (", "|").replace(", ", " ").replace("|", ", ")
            line = wkt.loads("LINESTRING (" + utms + ")")
            nearest = nearest_points(line, point)[0]
            #print('nearest:',nearest)
            distance = line.distance(point)

            probability = 1 / (math.sqrt(math.pi * 2) * sigma) * math.exp(-0.5 * (distance / sigma) ** 2)
            layer_emmissions.append(math.log(probability, 2))
            layer_projections.append([nearest,link_node])#
            layer_nearest.append([nearest.x,nearest.y])
            #layer_links_node.append(link_node)#
            layer_distances.append(distance)
            if not pd.Series(previous_probe).empty:
                prev_probe_point = Point(previous_probe["easting"], previous_probe["northing"])
                distance_probes = prev_probe_point.distance(point)
                node_transitions = []
                for projection in projections[-1]:
                    # We could not calculate the right distance on the route in our case we used nearest.distance(projection)
                    d_t = abs(distance_probes - nearest.distance(projection[0]))
                    transition_prob = 1 / beta * math.exp(-d_t / beta) * is_connected(projection[1],link_node)
                    node_transitions.append(math.log(transition_prob, 2))
                layer_transitions.append(node_transitions)
        if layer_transitions:
            transitions.append(layer_transitions)
        emissions.append(layer_emmissions)
        projections.append(layer_projections)
        match_points.append(layer_nearest)
        layer_distances.sort()
        distances.append(layer_distances)
        previous_probe = probe
    hmm = np.array(hmm)
    emissions = np.array(emissions)
    transitions = np.array(transitions)
    return hmm, emissions, projections, transitions, distances, Probe_Points, match_points, index

def is_connected(linka,linkb):
    if (linka["refNodeID"] == linkb["refNodeID"] or linka["refNodeID"] == linkb["nrefNodeID"] or linka["nrefNodeID"] == linkb["refNodeID"] or linka["nrefNodeID"] == linkb["nrefNodeID"]):
        return 1
    else:
        return 0.1

def find_path(emissions, transitions, nearest, projections, hmm, layer, prev_probabilities, index, distances):
    if layer >= emissions.shape[0]:
        ind = np.unravel_index(np.argmax(prev_probabilities, axis=None), prev_probabilities.shape)
        return [], [], ind, []
    future_probs = []
    for e in range(len(emissions[layer])):
        probability = emissions[layer][e]
        if layer == 0:
            maximize_probs = prev_probabilities
        else:
            maximize_probs = prev_probabilities + transitions[layer - 1][e]
        future_probs.append(probability + np.amax(maximize_probs))
    future_probs = np.array(future_probs)
    matched_path, path, ind, new_index = find_path(emissions, transitions, nearest, projections, hmm, layer + 1, future_probs, index, distances)
    ind = (ind[0]%3,)
    path.append((hmm[layer][ind],nearest[layer][ind[0]%3],index[layer],distances[layer][ind[0]%3]))
    matched_path.append(nearest[layer][ind[0]])
    new_index.append(index[layer])
    ind = np.unravel_index(np.argmax(prev_probabilities, axis=None), prev_probabilities.shape)
    return matched_path, path, ind, new_index

def calculate_hmm_match(data_links, data_probes):
    samples = data_probes["sampleID"].unique()
    print(samples)
    pbar = tqdm(total = len(samples[3500:]))
    for s in samples[3500:]:

        pbar.update()
        data_p = data_probes[data_probes["sampleID"] ==  s]
        print("Number of probes in sample :",s, len(data_p))
        hmm, emissions, projections, transitions, distances, Probe_Points, match_points, index = generate_hmm(data_links, data_p)
        matched_path, path, ind, new_index = find_path(emissions, transitions, match_points, projections, hmm, 0, np.zeros((3, 1)), index, distances)

        for (link_id, matched_point, probe_id, distance) in path:
            data_probes.loc[probe_id, "distance"] = distance
            data_probes.loc[probe_id, "linkPVID"] = data_links.loc[link_id,"linkPVID"]
            data_probes.at[probe_id, "projectionx"] = matched_point[0]
            data_probes.at[probe_id, "projectiony"] = matched_point[1]
    dataframe = pd.DataFrame(data_probes[:])
    dataframe.to_csv("..\\data\\HmmResult2.csv")

    '''
    x = []
    y = []
    for i in range(len(Probe_Points)):
        x.append(Probe_Points[i][0])
        y.append(Probe_Points[i][1])
    x1 = []
    y1 = []
    for i in range(len(matched_path)):
        x1.append(matched_path[i][0])
        y1.append(matched_path[i][1])
    plt.title("Probe Points")
    plt.plot(x,y,"ob")
    plt.plot(x1,y1)
    plt.show()
    '''


    return path

def load_cleaned_data():
    # Load the cleaned link data and convert it to a geopandas dataframe
    data_links = pd.read_csv("..\\data\\LinkDataCleaned.csv")
    data_links['shape'] = data_links['shape'].apply(wkt.loads)
    data_links = geopandas.GeoDataFrame(data_links, geometry='shape')

    # Load the cleaned link data and convert it to a geopandas dataframe
    data_probes = pd.read_csv("..\\data\\CleanProbePoints.csv")
    data_probes['shape'] = data_probes['shape'].apply(wkt.loads)
    data_probes = geopandas.GeoDataFrame(data_probes, geometry='shape')

    # Return both dataframes for further usage
    return data_links, data_probes

probes_exist = os.path.isfile('..\\data\\CleanProbePoints.csv')
links_exist = os.path.isfile('..\\data\\LinkDataCleaned.csv')
data_links, data_probes = load_cleaned_data()
print("Calculate HMM match\n")
hmm_matched_path = calculate_hmm_match(data_links,data_probes)
print('hmm matched path:',hmm_matched_path)
