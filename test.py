from helper.loader import checkDataFolder
from helper.loader import load
from matplotlib import pyplot as plt

if __name__ == "__main__":
    # print(checkDataFolder())
    # load('link data')
    # probe_points = load('probe points')
    # print(probe_points.shape)

    link_data = load('link data')
    print(link_data)