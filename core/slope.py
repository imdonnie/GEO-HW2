import os
import math
import pandas as pd
from shapely.geometry import Point
from helper.Tools import geo_path

def calculateSlope(data_links, csv_file=os.path.join(geo_path, 'data', 'MatchedProbes.csv')):
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
    data_probes.to_csv(os.path.join(geo_path, 'data', 'Slope.csv'))
    return data_probes

def error(row):
    before_slope = row['slopeBefore']
    after_slope = row['slopeAfter']
    real_slopes = row['surveyedSlope']
    if not pd.isna(real_slopes):
        real_slopes = [pair.split('/') for pair in real_slopes.split('|')]
        before_error = []
        after_error = []
        for pair in real_slopes:
            before_error.append(abs(float(pair[1])-float(before_slope)))
            after_error.append(abs(float(pair[1])-float(after_slope)))
        # print(min(before_error), min(after_error))
        res = min(after_error)
    else:
        res = 0
    return res



def evaluateSlope():
    slopes = pd.read_csv(os.path.join(geo_path, 'data', 'Slope.csv'))
    errors = slopes.apply(error, axis=1)
    errors.to_csv(os.path.join(geo_path, 'data', 'errors.csv'))
    