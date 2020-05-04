from helper.Tools import checkDataFolder
from helper.Tools import load
from helper.Tools import plotLinkData
from helper.Tools import test
if __name__ == "__main__":
    # print(checkDataFolder())
    # load('link data')
    # probe_points = load('probe points')
    # print(probe_points.shape)

    link_data = load('link data')
    plotLinkData(link_data)

    # test()