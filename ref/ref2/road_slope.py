# Helps to calculate the slope on the road
import math

# Helps to handle the data
import pandas as pd
# Python packages for handling geo objects and calculating distances
from shapely.geometry import Point


def calculate_slope_for_file(data_links, csv_file="./data/FastMatchedProbes.csv", ):
    # Load the probes
    data_probes = pd.read_csv(csv_file)
    print(len(data_probes))
    data_probes = data_probes.drop(["probeID", "Unnamed: 0"], axis=1)

    # Find all the unique samples within the matched probes
    samples = data_probes["sampleID"].unique()

    for s in samples:
        # Find all probes that belong to sample s
        probes_for_sample = data_probes[data_probes["sampleID"] == s]
        previous_probe = None
        previous_index = None
        first = True

        # Iterate over all probes wih the same sampleID
        current_probe = probes_for_sample.iloc[0]
        for index, row in probes_for_sample.iterrows():
            if not first:
                # Take the current and the previous point
                current_probe = probes_for_sample.loc[index]
                previous_probe_point = Point(previous_probe["easting"], previous_probe["northing"])
                current_probe_point = Point(current_probe["easting"], current_probe["northing"])

                # Calculate the distance and the difference in altitude bettween the points
                distance = previous_probe_point.distance(current_probe_point)
                alt_dif = float(current_probe["altitude"]) - float(previous_probe["altitude"])

                # Check if there is a slope
                if distance > 0:
                    slope = math.atan(alt_dif / distance)
                else:
                    slope = 0

                # Save the data back to the dataframe for further evaluation
                data_probes.loc[index, "slopeBefore"] = slope
                data_probes.loc[previous_index, "slopeAfter"] = slope
                link = data_links[data_links["linkPVID"] == current_probe["linkPVID"]]
                data_probes.loc[index, "surveyedSlope"] = link["slopeInfo"].iloc[0]

            # Go on to the next probe
            previous_probe = current_probe
            previous_index = index
            first = False

    return data_probes


