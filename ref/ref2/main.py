import os

from hidden_markov_model import calculate_hmm_match
from loading_cleaning import load_and_clean_probes, load_and_clean_links, load_cleaned_data
from map_matching import calculate_fast_match, calculate_accurate_match
from road_slope import calculate_slope_for_file

# Check if the data is already cleaned
probes_exist = os.path.isfile('./data/ProbePointsCleaned.csv')
links_exist = os.path.isfile('./data/LinkDataCleaned.csv')

if not probes_exist:
    # If the data for the probes is not yet cleaned, clean the probes
    print("Clean Probes\n")
    load_and_clean_probes()

if not links_exist:
    # If the data for the links is not yet cleaned, clean the links
    print("Clean Links\n")
    load_and_clean_links()

# Load the data files that contain the cleaned data
print("Load cleaned files\n")
data_links, data_probes = load_cleaned_data()

# Map match using the fast match that only calculates the distance and the linkPVID
print("Calculate fast match\n")
fast_matched = calculate_fast_match(data_links,data_probes,10000, "./data/FastMatchedProbes.csv")

# Map match using the accurate match that will also calculate the direction towards the ref node and the distance
print("Calculate accurate match\n")
accurate_matched = calculate_accurate_match(data_links,data_probes,1000, "./data/AccurateMatchedProbes.csv")

# Map match using a hidden markov model
print("Calculate HMM match\n")
hmm_matched_path = calculate_hmm_match(data_links,data_probes)
print(hmm_matched_path)

# Calculate the slope for the fast matched probe points and evaluate them
data_slope_probes = calculate_slope_for_file(data_links, "./data/FastMatchedProbes.csv")
data_slope_probes.to_csv("./data/SlopeProbes.csv", index=False)