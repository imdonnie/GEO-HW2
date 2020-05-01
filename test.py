from helper.loader import checkDataFolder
from helper.loader import load

if __name__ == "__main__":
    # print(checkDataFolder())
    # load('link data')
    probe_points = load('probe points')
    print(probe_points.shape)