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

def calculate_hmm(data_links, data_probes):
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
    for i in data_probes["probeID"]:
        # print(i)
        probe = data_probes.loc[i]
        #possible_matches_index = list(spatial_index.nearest((probe["shape"].x, probe["shape"].y), 3))
        possible_matches_index = list(spatial_index.nearest((probe["shape"].x, probe["shape"].y), 3))
        hmm.append(possible_matches_index)
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
            print('nearest:',nearest)
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
                    #transition_prob = is_connected(projection[1],link_node)
                    node_transitions.append(math.log(transition_prob, 2))
                layer_transitions.append(node_transitions)
        if layer_transitions:
            transitions.append(layer_transitions)
        emissions.append(layer_emmissions)
        projections.append(layer_projections)
        match_points.append(layer_nearest)
        layer_distances.sort()
        #print(layer_distances)
        distances.append(layer_distances)
        previous_probe = probe

    hmm = np.array(hmm)
    emissions = np.array(emissions)
    transitions = np.array(transitions)
    #print("Probe Ponints:",Probe_Points)
    return hmm, emissions, projections, transitions, distances, Probe_Points, match_points

def is_connected(linka,linkb):
    if (linka["refNodeID"] == linkb["refNodeID"] or linka["refNodeID"] == linkb["nrefNodeID"] or linka["nrefNodeID"] == linkb["refNodeID"] or linka["nrefNodeID"] == linkb["nrefNodeID"]):
        return 1
    else:
        return 0.1


def find_path(emissions, transitions, nearest, projections, hmm, layer, prev_probabilities):
    if layer >= emissions.shape[0]:
        ind = np.unravel_index(np.argmax(prev_probabilities, axis=None), prev_probabilities.shape)
        return [], [], ind
    future_probs = []
    for e in range(len(emissions[layer])):
        probability = emissions[layer][e]
        if layer == 0:
            maximize_probs = prev_probabilities
        else:
            maximize_probs = prev_probabilities + transitions[layer - 1][e]
        future_probs.append(probability + np.amax(maximize_probs))
    # print(future_probs)
    future_probs = np.array(future_probs)
    matched_path, path, ind = find_path(emissions, transitions, nearest, projections, hmm, layer + 1, future_probs)
    print('hmm:',hmm[layer][ind])
    print('ind:',type(ind))
    print('nearest',nearest[layer][ind[0]])
    #print('projections1',projections[layer][[ind[0]]])
    #print('projections2',projections[layer][[ind[1]]])
    path.append(hmm[layer][ind])
    #print("mp:",matched_path)
    matched_path.append(nearest[layer][ind[0]])
    #match_points.append(hmm[layer][ind])
    #match_points.append(projections[layer][ind])

    ind = np.unravel_index(np.argmax(prev_probabilities, axis=None), prev_probabilities.shape)
    # print(ind)
    return matched_path, path, ind


def calculate_hmm_match(data_links, data_probes):
    data_p = data_probes[data_probes["sampleID"] == 3496]
    print("Number of probes in sample 3496:", len(data_p))
    print("Longitude of first probe:", data_p.loc[0, "shape"].x)
    print("Latitude of first probe:", data_p.loc[0, "shape"].y)

    # start = time.time()
    hmm, emissions, projections, transitions, distances, Probe_Points, match_points = calculate_hmm(data_links, data_p)
    # end = time.time()
    # print(end - start)
    print(hmm)
    matched_path, path, ind = find_path(emissions, transitions, match_points, projections, hmm, 0, np.zeros((3, 1)))

    return path

def load_cleaned_data():
    # Load the cleaned link data and convert it to a geopandas dataframe
    data_links = pd.read_csv("..\\data\\LinkDataCleaned.csv")
    data_links['shape'] = data_links['shape'].apply(wkt.loads)
    data_links = geopandas.GeoDataFrame(data_links, geometry='shape')

    # Load the cleaned link data and convert it to a geopandas dataframe
    data_probes = pd.read_csv("..\\data\\ProbePointsCleaned.csv")
    data_probes['shape'] = data_probes['shape'].apply(wkt.loads)
    data_probes = geopandas.GeoDataFrame(data_probes, geometry='shape')

    # Return both dataframes for further usage
    return data_links, data_probes

probes_exist = os.path.isfile('..\\data\\ProbePointsCleaned.csv')
links_exist = os.path.isfile('..\\data\\LinkDataCleaned.csv')
data_links, data_probes = load_cleaned_data()
print("Calculate HMM match\n")
hmm_matched_path = calculate_hmm_match(data_links,data_probes)
print('hmm matched path:',hmm_matched_path)
