import math

class MapPoint():
    # self.id = self.latitude = self.longtitude = self.altitude = None
    def __init__(self, point_info):
        self.latitude, self.longtitude = float(point_info[0]), float(point_info[1])
        self.altitude = None if point_info[2] is '' else float(point_info[2]) 
    def getLoc(self):
        return (self.latitude, self.longtitude)

class MapLink():
    def __init__(self, link_node_a, link_node_b):
        self.link_node_a, self.link_node_b = link_node_a, link_node_b

    def getNodes(self):
        return self.link_node_a.getLoc(), self.link_node_b.getLoc()
        
    def pointToLinkDistance(self, point):
        pass