import os
import math
import tqdm
import pandas as pd
import time
from shapely.geometry import Point
from helper.Tools import geo_path

# 0.00/-0.090|110.17/0.062
def getNodeSlope(distance, slopeInfo):
    if pd.isna(slopeInfo):
        return None
    # print(distance, slopeInfo)
    distance_slope = [i.split('/') for i in slopeInfo.split('|')]
    distance_slope.append([math.inf])
    for i, _ in enumerate(distance_slope[:-1]):
        if float(distance_slope[i][0])<=distance and distance<=float(distance_slope[i+1][0]):
            return float(distance_slope[i][1])
        else:
            pass

def calculateSlope(data_links, csv_file=os.path.join(geo_path, 'data', 'MatchedProbes_LL.csv')):
    # Load the probes
    data_probes = pd.read_csv(csv_file)
    data_probes = data_probes.drop(["probeID", "Unnamed: 0"], axis=1)

    # Find all the unique samples within the matched probes
    samples = data_probes["sampleID"].unique()

    pbar = tqdm.tqdm(total = samples.shape[0])
    for s in samples:
        pbar.update()
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

                # previous_probe_point = Point(previous_probe["easting"], previous_probe["northing"])
                # current_probe_point = Point(current_probe["easting"], current_probe["northing"])

                # mysplit = lambda x: [float(i) for i in x.replace('POINT ( ', '').replace(')', '').strip().split(' ')]
                # previous_probe_point = Point(mysplit(previous_probe["projection"])[0], mysplit(previous_probe["projection"])[1])
                # current_probe_point = Point( mysplit(current_probe["projection"])[0], mysplit(current_probe["projection"])[1])

                previous_probe_point = Point(previous_probe['projectionx'], previous_probe['projectiony'])
                current_probe_point = Point(current_probe['projectionx'], current_probe['projectiony'])

                # Calculate the distance and the difference in altitude bettween the points
                disfromlink = max(current_probe['distance'], previous_probe['distance'])
                distance = previous_probe_point.distance(current_probe_point)
                alt_dif = float(current_probe["altitude"]) - float(previous_probe["altitude"])
                if disfromlink > 10:
                    continue
                # Check if there is a slope
                if distance > 0:
                    slope = math.atan(alt_dif / distance)
                else:
                    slope = 0

                # Save the data back to the dataframe for further evaluation
                data_probes.loc[index, "slopeBefore"] = slope
                data_probes.loc[previous_index, "slopeAfter"] = slope
                link = data_links[data_links["linkPVID"] == current_probe["linkPVID"]]

                # data_probes.loc[index, "surveyedSlope"] = link["slopeInfo"].iloc[0]
                data_probes.loc[index, "surveyedSlope"] = getNodeSlope(current_probe['distBetRP'], link["slopeInfo"].iloc[0])
                # data_probes.loc[index, "surveyedSlope"] = getNodeSlope(current_probe['distBetRP'], link["slopeInfo"].iloc[0])
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

def error_single(row):
    before_slope = row['slopeBefore']
    after_slope = row['slopeAfter']
    real_slope = row['surveyedSlope']
    if not pd.isna(real_slope):
        res = abs((before_slope+after_slope)/2-real_slope)
    else:
        res = 0
    return res

def evaluateSlope():
    tt = str(time.time())
    slopes = pd.read_csv(os.path.join(geo_path, 'data', 'Slope.csv'))
    errors = slopes.apply(error_single, axis=1)
    errors.to_csv(os.path.join(geo_path, 'data', 'errors.csv'))
    