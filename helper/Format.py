import os
import utm
import geopandas
# import modin.pandas as pd
import pandas as pd
from shapely import wkt
# change your GEO-HW2 path here
geo_path = 'C:\\Users\\Donnie\\Desktop\\NU\\EE395\\hw2\\GEO-HW2'
data_path = os.path.join(geo_path, 'data')
data_links_csv = os.path.join(data_path, 'Partition6467LinkData.csv')
data_probes_csv = os.path.join(data_path, 'Partition6467ProbePoints.csv')
clean_links_csv = os.path.join(data_path, 'CleanLinkData.csv')
clean_probes_csv = os.path.join(data_path, 'CleanProbePoints.csv')

INFO = '\033[1;32m[INFO]\033[0m'
ERROR = '\033[1;31m[ERROR]\033[0m'
WARNING = '\033[1;33m[WARNING]\033[0m'

# shapeInfo	contains an array of shape entries consisting of the latitude and longitude (in decimal degrees) and elevation (in decimal meters) 
# info2wkt: 51.4965800/9.3862299/|51.4994700/9.3848799/ -> LINESTRING (9.3862299 51.49658, 9.3848799 51.49947)
info2wkt = lambda info: 'LINESTRING ({0})'.format(', '.join(["{0} {1}".format(node.split('/')[1], node.split('/')[0]) for node in str(info).split('|')]))
shape2utm = lambda shape: [(utm.from_latlon(c[1], c[0])[0], utm.from_latlon(c[1], c[0])[1]) for c in shape.coords]
row2point = lambda row:  "POINT ({0} {1})".format(str(row["longitude"]), str(row["latitude"]))
caleast = lambda row: utm.from_latlon(row["latitude"], row["longitude"])[0]
calnorth = lambda row: utm.from_latlon(row["latitude"], row["longitude"])[1]

def cleanLinkData():
    useless_idx = ["timeZone", "shapeInfo", "curvatureInfo"]
    names = ["linkPVID", "refNodeID", "nrefNodeID", "length", "functionalClass", 
             "directionOfTravel", "speedCategory", "fromRefSpeedLimit", "toRefSpeedLimit", "fromRefNumLanes", 
             "toRefNumLanes", "multiDigitized", "urban", "timeZone", "shapeInfo", 
             "curvatureInfo", "slopeInfo"]
    data_links = pd.read_csv(data_links_csv, header=None, names=names)
    data_links.index.name = 'linkID'
    data_links['shape'] = data_links["shapeInfo"].apply(info2wkt).apply(wkt.loads)
    data_links = data_links.drop(useless_idx, axis=1)
    geo_data_links = geopandas.GeoDataFrame(data_links, geometry='shape')
    data_links['utms'] = geo_data_links["shape"].apply(shape2utm)
    data_links.to_csv(clean_links_csv)

def cleanProbePoints():
    names = ["sampleID", "dateTime", "sourceCode", "latitude", "longitude", "altitude", "speed", "heading"]
    data_probes = pd.read_csv(data_probes_csv, header=None, names=names)
    data_probes.index.name = 'probeID'
    data_probes = data_probes.drop(["sourceCode", "dateTime"], axis=1)
    data_probes["shape"] = data_probes.apply(row2point, axis=1).apply(wkt.loads)
    data_probes["easting"] = data_probes.apply(caleast, axis=1)
    data_probes["northing"] = data_probes.apply(calnorth, axis=1)
    data_probes["zoneNumber"], data_probes["zoneLetter"] = 32, "U"
    data_probes = geopandas.GeoDataFrame(data_probes, geometry='shape')
    data_probes.to_csv(clean_probes_csv)

def loadCleanData():
    data_links, data_probes = pd.read_csv(clean_links_csv), pd.read_csv(clean_probes_csv)
    data_links['shape'], data_probes['shape'] = data_links['shape'].apply(wkt.loads), data_probes['shape'].apply(wkt.loads)
    data_links, data_probes = geopandas.GeoDataFrame(data_links, geometry='shape'), geopandas.GeoDataFrame(data_probes, geometry='shape')
    return data_links, data_probes


if __name__ == "__main__":
    # loadCleanData()
    cleanLinkData()