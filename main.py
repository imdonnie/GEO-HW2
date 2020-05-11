import os
from helper.Tools import *
from helper.Plotter import *
from helper.Format import *
from core.slope import *
from core.hiden_markov import *
from core.point_wise_map import *

if __name__ == "__main__":
# visualizaiton part of the link data
    link_data = load('link data')
    plotLinkData(link_data)
# pre-processing
    cleanLinkData()
    cleanProbePoints()
    deleteDuplicate()
# load cleaned data
    links = loadCleanData('links')
    probes = loadCleanData('probes')
# method 1: point-wise match
    point_wise_match(links, probes, 50000, os.path.join(geo_path, 'data', 'PointwiseProbes_nodir1.1_50000.csv'))
# method 2: HMM
    calculate_hmm_match(links, probes)
# calculate slopes and do evaluation
    calculateSlope(links)
    evaluateSlope()
# show results
    visualizeMatched(links)
    plotDistribution()