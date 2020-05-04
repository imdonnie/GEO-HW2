# Helps to calculate the direction in degrees
import math

# Standard python package for data manipulation
import pandas as pd
# Python packages for handling geo objects and calculating distances
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import nearest_points


def calculate_fast_match(data_links, data_probes, number_of_points, to_file_name):
    # Initialize the spatial index and the progress counter
    spatial_index = data_links.sindex
    progress = 0

    for p in data_probes[:number_of_points]['probeID']:
        # Get the current probe and get its UTM point
        probe = data_probes.loc[p]
        probe_point = Point(probe["easting"], probe["northing"])

        # Find the 3 closest points with the spatial index and try to find out which is actually the closest
        possible_matches_index = list(spatial_index.nearest((probe["shape"].x, probe["shape"].y), 3))
        best_match = None
        best_distance = 10000000

        for l in possible_matches_index:
            # Get the current link and find the UTM line or the nearest point
            link = data_links.loc[l]
            utms = link["utms"][2:-2].replace("), (", "|").replace(", ", " ").replace("|", ", ")
            line = wkt.loads("LINESTRING (" + utms + ")")
            nearest = nearest_points(line, probe_point)[0]
            distance = nearest.distance(probe_point)

            # If the current link is closer to the probe we consider it as the best match
            if distance < best_distance:
                best_distance = distance
                best_match = link

        # Update the data in the probe file with the matched link and the distance
        data_probes.loc[p, "distance"] = best_distance
        data_probes.loc[p, "linkPVID"] = best_match["linkPVID"]

        # Update the progress of the fast match so far
        progress += 1
        if progress % 500 == 0:
            print(progress)

    # Save the results of the fast match in a new csv file
    dataframe = pd.DataFrame(data_probes[:number_of_points])
    dataframe.to_csv(to_file_name)

    return dataframe


def calculate_accurate_match(data_links, data_probes, number_of_points, to_file_name):
    # Initialize the spatial index and the progress counter
    spatial_index = data_links.sindex
    progress = 0

    for p in data_probes[:number_of_points]['probeID']:
        # Get the current probe and get its UTM point
        probe = data_probes.loc[p]
        probe_point = Point(probe["easting"], probe["northing"])

        # Find the closest point with the spatial index
        possible_matches_index = list(spatial_index.nearest((probe["shape"].x, probe["shape"].y), 1))

        # Get the current link and find the UTM line or the nearest point
        link = data_links.loc[possible_matches_index[0]]
        utms = link["utms"][2:-2].replace("), (", "|").replace(", ", " ").replace("|", ", ")
        line = wkt.loads("LINESTRING (" + utms + ")")
        nearest = nearest_points(line, probe_point)[0]
        link_distance = nearest.distance(probe_point)
        ref_node = Point(line.coords[0][0], line.coords[0][1])
        ref_distance = ref_node.distance(probe_point)

        # Update dataframe attributes
        data_probes.loc[p, "linkPVID"] = link["linkPVID"]
        data_probes.loc[p, "distFromLink"] = link_distance
        data_probes.loc[p, "distFromRef"] = ref_distance

        # Calculate the orientation relative to the ref node
        radians = math.atan2(ref_node.y - probe_point.y, ref_node.x - probe_point.x)
        ref_node_direction = int(math.degrees(radians))
        if ref_node_direction <= 0:
            ref_node_direction = ref_node_direction + 360
        if abs(ref_node_direction - probe["heading"]) <= 90:
            data_probes.loc[p, "direction"] = 'T'
        else:
            data_probes.loc[p, "direction"] = 'F'

        # Update the progress of the fast match so far
        progress += 1
        if progress % 100 == 0:
            print(progress)

    # Save the results of the fast match in a new csv file
    dataframe = pd.DataFrame(data_probes[:number_of_points])
    dataframe.to_csv(to_file_name)

    return dataframe
