from shapely.geometry import Point
import pandas as pd
from shapely.ops import nearest_points
from shapely import wkt
import math
from tqdm import tqdm




def point_wise_match(data_links, data_probes, number_of_points, to_file_name):
    if number_of_points > len(data_probes):
        print('error')
    spatial_index = data_links.sindex
    candi = []
    print('Filter the links')
    pbat = tqdm(total=number_of_points)
    for p in data_probes[:number_of_points]['probeID']:
        pbat.update()
    # Get the current probe and get its UTM point
        each = []
        probe = data_probes.loc[p]
        probe_point = Point(probe["easting"], probe["northing"])
        candi2 = distanceCan(probe,spatial_index)
        candi2 = trvdir(p,candi2,probe_point,data_links,data_probes)
        each.append(p)
        each.append(candi2)
        candi.append(each)
    candi3 = passLength(candi,data_probes,data_links)
    candi4 = smooth(candi3,data_probes)
    print('Store to csv')
    pbat1 = tqdm(total=number_of_points)
    for i in range(len(candi4)):
        pbat1.update()
        probe = data_probes.loc[candi4[i][0]]
        probe_point = Point(probe["easting"], probe["northing"])
        link = data_links.loc[candi4[i][1]]
        utms = link["utms"][2:-2].replace("), (", "|").replace(", ", " ").replace("|", ", ")
        line = wkt.loads("LINESTRING (" + utms + ")")
        nearest = nearest_points(line,probe_point)[0]
        distance = nearest.distance(probe_point)

        data_probes.loc[candi4[i][0],"distance"] = distance
        data_probes.loc[candi4[i][0],"linkPVID"] = link["linkPVID"]
        data_probes.loc[candi4[i][0],"projection"] =  "POINT ( " + str(nearest.x) + " " + str(nearest.y) + ")"
    dataframe= pd.DataFrame(data_probes[:number_of_points])
    dataframe.to_csv(to_file_name)
    




def distanceCan(probe,spatial_index):
    Candidate = list(spatial_index.nearest((probe["shape"].x, probe["shape"].y), 5))
    return Candidate

def trvdir(p,candi,probe_point,data_links,data_probes):
    probe = data_probes.loc[p]
    candi2 = []
    for i in range(len(candi)):
        link = data_links.loc[candi[i]]
        utms = link["utms"][2:-2].replace("), (", "|").replace(", ", " ").replace("|", ", ")
        line = wkt.loads("LINESTRING (" + utms + ")")
        nearest = nearest_points(line, probe_point)[0]
        #link_distance = nearest.distance(probe_point)
        ref_node = Point(line.coords[0][0], line.coords[0][1])
        # ref_distance = ref_node.distance(probe_point)
        pro_link_dis = nearest.distance(ref_node)

        # Update dataframe attributes
        data_probes.loc[p, "linkPVID"] = link["linkPVID"]
        #data_probes.loc[p, "distFromLink"] = link_distance
        #data_probes.loc[p, "distFromRef"] = ref_distance
        data_probes.loc[p,"distBetRP"] = pro_link_dis

        # Calculate the orientation relative to the ref node
        radians = math.atan2(ref_node.y - probe_point.y, ref_node.x - probe_point.x)
        ref_node_direction = int(math.degrees(radians))
        if ref_node_direction <= 0:
            ref_node_direction = ref_node_direction + 360
        if abs(ref_node_direction - probe["heading"]) <= 90:
            data_probes.loc[p, "direction"] = 'T'
        else:
            data_probes.loc[p, "direction"] = 'F'
        s_direc = data_probes.loc[p, "direction"] 
        l_direc = link["directionOfTravel"]
        if ~((l_direc != 'B') & (s_direc != l_direc)):   # only keep the segment candidates whose directionOfTravel is conformed with the sample's current travel direction.    
                candi2.append(candi[i])
    return candi2


def passLength(candi,data_probes,data_links):
    candi2 = [candi[0]]
    for i in range(len(candi)-1):
        if len(candi2[i][1]) == 0: 
                candi2.append(candi[i+1])                # skip the samples that already has no candidate.
                continue
        probe1 = data_probes.loc[candi2[i][0]]
        probe2 = data_probes.loc[candi[i+1][0]]
        if (probe1['sampleID'] != probe2['sampleID']):
            candi2.append(candi[i+1])
            continue
        p1_speed = probe1['speed']
        p2_speed = probe2['speed']
        avg_speed = (p1_speed+p2_speed)/2
        time = 5 * (candi[i][0]-candi[i+1][0])
        length = avg_speed * time
        p1_point = Point(probe1['easting'],probe1['northing'])
        p2_point = Point(probe2['easting'],probe2['northing'])
        candi1 = []
        for j in range (len(candi[i+1][1])):
            p1_link = data_links.loc[candi[i][1][0]]
            p1_utms = p1_link["utms"][2:-2].replace("), (", "|").replace(", ", " ").replace("|", ", ")
            p1_line = wkt.loads("LINESTRING (" + p1_utms + ")")
            p1_nearest = nearest_points(p1_line, p1_point)[0]

            p2_link = data_links.loc[candi[i+1][1][j]]
            p2_utms = p2_link["utms"][2:-2].replace("), (", "|").replace(", ", " ").replace("|", ", ")
            p2_line = wkt.loads("LINESTRING (" + p2_utms + ")")
            p2_nearest = nearest_points(p2_line, p2_point)[0]
            distance = p1_nearest.distance(p2_nearest)

            p1_lim = max(p1_link['toRefSpeedLimit'],p1_link['fromRefSpeedLimit'])
            p2_lim = max(p2_link['toRefSpeedLimit'],p2_link['fromRefSpeedLimit'])
            thrsh = (max(p1_lim,p2_lim)/3.6*time)*1.1

            if length <= (thrsh+distance):
                candi1.append(candi[i+1][1][j])

        if len(candi1) > 0:
            each = []
            each.append(candi[i+1][0])
            each.append(candi1)
            candi2.append(each)
        else:
            each = []
            each.append(candi[i+1][0])
            each.append([])
            candi2.append(each)

    return candi2

def smooth(candi,data_probes):
    match = []
    for i in range (len(candi)):
        each = []
        each.append(candi[i][0])
        if len(candi[i][1])!=0:
            each.append(candi[i][1][0])
        else:
            each.append(candi[i-1][1][0])
        match.append(each)
    for i in range(1,len(match)-1):
        p1 = data_probes.loc[match[i-1][0]]
        p2 = data_probes.loc[match[i][0]]
        p3 = data_probes.loc[match[i+1][0]]
        if ((p1['sampleID']==p3['sampleID'])&(p2['sampleID']!=p3['sampleID'])):
            cur_link = match[i][1]
            nex_link = match[i+1][1]
            pre_link = match[i-1][1]
            if ((cur_link == nex_link) & (cur_link != pre_link)):
                match[i][1] = pre_link
    return match




