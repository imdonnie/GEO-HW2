import math

class MapPoint():
    # self.id = self.latitude = self.longtitude = self.altitude = None
    def __init__(self, point_info):
        self.latitude, self.longtitude, self.altitude = point_info

class MapLink():
    def __init__(self, link_node_a, link_node_b):
        self.ref_point, self.nref_point = link_node_a, link_node_b