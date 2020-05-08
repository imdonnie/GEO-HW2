from helper.Tools import checkDataFolder
from helper.Tools import load
from helper.Tools import plotLinkData
from helper.Tools import geo_path

from helper.Format import cleanLinkData
from helper.Format import cleanProbePoints
from helper.Format import loadCleanData

from core.slope import calculateSlope
from core.slope import evaluateSlope
if __name__ == "__main__":
# visualizaiton part of the link data
    # link_data = load('link data')
    # plotLinkData(link_data)

    # cleanLinkData()
    # links = loadCleanData('links')
    # calculateSlope(links)
    evaluateSlope()
