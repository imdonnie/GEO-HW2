# Helps to convert lat long to UTM coordinates
import math

# Standard python package for data manipulation
import numpy as np
import pandas as pd
# Python packages for handling geo objects and calculating distances
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import nearest_points


def calculate_hmm(data_links, data_probes):
    spatial_index = data_links.sindex
    beta = 300
    sigma = 400
    hmm = []
    emissions = []
    projections = []
    transitions = []
    distances = []
    previous_probe = None

    for i in data_probes["probeID"]:
        # print(i)
        probe = data_probes.loc[i]
        possible_matches_index = list(spatial_index.nearest((probe["shape"].x, probe["shape"].y), 3))
        hmm.append(possible_matches_index)
        layer_emmissions = []
        layer_projections = []
        layer_transitions = []
        layer_distances = []
        point = Point(probe["easting"], probe["northing"])
        for p in possible_matches_index:
            link = data_links.loc[p]
            utms = link["utms"][2:-2].replace("), (", "|").replace(", ", " ").replace("|", ", ")
            line = wkt.loads("LINESTRING (" + utms + ")")
            nearest = nearest_points(line, point)[0]
            distance = line.distance(point)
            probability = 1 / (math.sqrt(math.pi * 2) * sigma) * math.exp(-0.5 * (distance / sigma) ** 2)
            layer_emmissions.append(math.log(probability, 2))
            layer_projections.append(nearest)
            layer_distances.append(distance)
            if not pd.Series(previous_probe).empty:
                prev_probe_point = Point(previous_probe["easting"], previous_probe["northing"])
                distance_probes = prev_probe_point.distance(point)
                node_transitions = []
                for projection in projections[-1]:
                    # We could not calculate the right distance on the route in our case we used nearest.distance(projection)
                    d_t = abs(distance_probes - nearest.distance(projection))
                    transition_prob = 1 / beta * math.exp(-d_t / beta)
                    node_transitions.append(math.log(transition_prob, 2))
                layer_transitions.append(node_transitions)
        if layer_transitions:
            transitions.append(layer_transitions)
        emissions.append(layer_emmissions)
        projections.append(layer_projections)
        layer_distances.sort()
        distances.append(layer_distances)
        previous_probe = probe

    hmm = np.array(hmm)
    emissions = np.array(emissions)
    transitions = np.array(transitions)
    return hmm, emissions, projections, transitions, distances


def find_path(emissions, transitions, hmm, layer, prev_probabilities):
    if layer >= emissions.shape[0]:
        ind = np.unravel_index(np.argmax(prev_probabilities, axis=None), prev_probabilities.shape)
        return [], ind
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
    path, ind = find_path(emissions, transitions, hmm, layer + 1, future_probs)
    path.append(hmm[layer][ind])
    ind = np.unravel_index(np.argmax(prev_probabilities, axis=None), prev_probabilities.shape)
    # print(ind)
    return path, ind


def calculate_hmm_match(data_links, data_probes):
    data_p = data_probes[data_probes["sampleID"] == 3496]
    print("Number of probes in sample 3496:", len(data_p))
    print("Longitude of first probe:", data_p.loc[0, "shape"].x)
    print("Latitude of first probe:", data_p.loc[0, "shape"].y)

    # start = time.time()
    hmm, emissions, projections, transitions, distances = calculate_hmm(data_links, data_p)
    # end = time.time()
    # print(end - start)
    print(hmm)
    path, ind = find_path(emissions, transitions, hmm, 0, np.zeros((3, 1)))
    return path
