# Gepandas for storing geo data in a pandas dataframe
import geopandas
# Standard python package for data manipulation
import pandas as pd

# Helps to convert lat long to UTM coordinates
import utm

# Python packages for handling geo objects and calculating distances
from shapely import wkt


def load_and_clean_probes():
    # Load the column names for the probe dataframe
    names = ["sampleID", "dateTime", "sourceCode", "latitude", "longitude", "altitude", "speed", "heading"]

    # Read the csv file to a standard pandas dataframe and convert indexes and the shape to UTM
    data_probes = pd.read_csv("./data/ProbePoints.csv", header=None, names=names)
    data_probes.index.name = 'probeID'
    data_probes = data_probes.drop(["sourceCode"], axis=1)
    data_probes = data_probes.drop(["dateTime"], axis=1)
    data_probes["shape"] = data_probes.apply(
        lambda row: "POINT ( " + str(row["longitude"]) + " " + str(row["latitude"]) + ")", axis=1)
    data_probes["easting"] = data_probes.apply(lambda row: utm.from_latlon(row["latitude"], row["longitude"])[0],
                                               axis=1)
    data_probes["northing"] = data_probes.apply(lambda row: utm.from_latlon(row["latitude"], row["longitude"])[1],
                                                axis=1)
    data_probes["zoneNumber"] = 32
    data_probes["zoneLetter"] = "U"
    data_probes['shape'] = data_probes['shape'].apply(wkt.loads)

    # Create a geopandas dataframe and finally save the dataframe on disk
    data_probes = geopandas.GeoDataFrame(data_probes, geometry='shape')
    data_probes.to_csv("./data/ProbePointsCleaned.csv")

    # Return the cleaned dataframe for further usage
    return data_probes


def calculate_wkt(value):
    # Takes in the shape info of a link and converts it to a wkt LINESTRING
    wkt = "LINESTRING ("
    coords = str(value).split("|")

    # Loop over all coordinates and add the text to the wkt format
    for c in coords:
        splitted = c.split("/")
        wkt = wkt + splitted[1] + " " + splitted[0] + ", "

    # Cut off the last comma
    wkt = wkt[:-2] + ")"

    # Return the well known text for the polyline
    return wkt


def convert_line_to_utm(line):
    # Converts a wkt linestring to a list of utm coordinates
    lat_long = line.coords
    utm_coords = []

    # Loop over all lat_long pairs within the linestring
    for c in lat_long:
        u = utm.from_latlon(c[1], c[0])
        utm_coords.append((u[0], u[1]))

    # Return the utm array
    return utm_coords


def load_and_clean_links():
    # Load the column names for the link dataframe
    names = ["linkPVID", "refNodeID", "nrefNodeID", "length", "functionalClass", "directionOfTravel", "speedCategory",
             "fromRefSpeedLimit", "toRefSpeedLimit", "fromRefNumLanes", "toRefNumLanes", "multiDigitized", "urban",
             "timeZone", "shapeInfo", "curvatureInfo", "slopeInfo"]

    # Read the csv file to a standard pandas dataframe and convert indexes and the shape to UTM
    data_links = pd.read_csv("./data/LinkData.csv", header=None, names=names)
    data_links.index.name = 'linkID'
    data_links['shape'] = data_links["shapeInfo"].apply(calculate_wkt)
    data_links = data_links.drop(["shapeInfo", "curvatureInfo", "timeZone"], axis=1)
    data_links['shape'] = data_links['shape'].apply(wkt.loads)

    # Create a geopandas dataframe and finally save the dataframe on disk
    data_links = geopandas.GeoDataFrame(data_links, geometry='shape')
    data_links["utms"] = data_links["shape"].apply(convert_line_to_utm)
    data_links.to_csv("./data/LinkDataCleaned.csv")

    # Return the cleaned dataframe for further usage
    return data_links


def load_cleaned_data():
    # Load the cleaned link data and convert it to a geopandas dataframe
    data_links = pd.read_csv("./data/LinkDataCleaned.csv")
    data_links['shape'] = data_links['shape'].apply(wkt.loads)
    data_links = geopandas.GeoDataFrame(data_links, geometry='shape')

    # Load the cleaned link data and convert it to a geopandas dataframe
    data_probes = pd.read_csv("./data/ProbePointsCleaned.csv")
    data_probes['shape'] = data_probes['shape'].apply(wkt.loads)
    data_probes = geopandas.GeoDataFrame(data_probes, geometry='shape')

    # Return both dataframes for further usage
    return data_links, data_probes