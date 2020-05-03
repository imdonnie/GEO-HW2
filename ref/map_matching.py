import math
points = {}
links = {}
##All the orders of longitude and latitude are wrong
class GeoPoint():
    lon = None
    lat = None
    alt = None
    ID = None
    def __init__(self,str):
        self.ID = str
        att = str.split("/")
        self.lon = float(att[0])
        self.lat = float(att[1])


class Link():
    ref = None
    non = None
    def __init__(self,ID,startp,endp):
        self.id = ID
        self.ref = GeoPoint(startp)
        self.non = GeoPoint(endp)
        #veclon: the vector component on longtitude
        self.veclon = self.non.lon - self.ref.lon
        #veclat: the vector components on latitude dimension
        self.veclat = self.non.lat - self.ref.lat
        #the modular of the vector
        self.length = (self.veclon**2+self.veclat**2)**0.5
        #the radian of the link
        if self.veclat != 0:
            self.radian = math.atan(self.veclon/self.veclat)
        elif self.veclon > 0:
            self.radian = math.pi/2
        else:
            self.radian = math.pi*3/2

    def calDis(self,point):
        tarlon = point.lon-self.ref.lon
        tarlat = point.lat-self.ref.lat
        distoref = tarlon**2+tarlat**2
        #cal projection length
        proj = (tarlon*self.veclon+tarlat*self.veclat)/self.length
        #If the proj is negative, return the square of length from point to ref node
        if proj < 0:
            return distoref
        pro_squre = proj**2
        #if the projection length is longer than the link length, return the square of length from point to end node
        if pro_squre > self.length**2:
            return (point.lon-self.non.lon)**2 + (point.lat-self.non.lat)**2
        # return the vertical distance
        return (tarlon**2+tarlat**2)-proj**2

    def calToRef(self,point):
        tarlon = point.lon-self.ref.lon
        tarlat = point.lat-self.ref.lat
        distoref = tarlon**2+tarlat**2
        return distoref**0.5

#To load the link node
lines = open("Partition6467LinkData.csv").readlines()
for line in lines:
    attr = line.split(",")
    # shape info
    nodes = attr[14].split("|")
    links[attr[0]] = []
    for i in xrange(0,len(nodes)-1):
        temp = Link(attr[0],nodes[i],nodes[i+1])
        links[attr[0]].append(temp)
        if points.has_key(nodes[i]):
            points[nodes[i]].append(temp)
        else:
            points[nodes[i]] = [temp]
        if points.has_key(nodes[i+1]):
            points[nodes[i+1]].append(temp)
        else:
            points[nodes[i+1]] = [temp]

print("Link loaded")

target = open("part_of_matched_points.txt","w")
recent = None
cand = []
probes = open("Partition6467ProbePoints.csv").readlines()
cnt = 0;
for probe in probes:
    cnt+=1
    #All attributes are stored in attr which is an array
    attr = probe.split(",")
    id = "/".join(attr[3:5])
    ptr = GeoPoint(id)
    #the current smallest distance
    small = None
    #the linkid which holds the smallest distance
    linkid = None
    #the distance from the point to ref node of the link
    distoref = None
    #modify direct
    direct = ""
    if attr[0] != recent:
        recent = attr[0]
        for key in links.keys():
            for link in links[key]:
                dis = link.calDis(ptr)
                if small == None or dis<small:
                    small = dis
                    linkid = link.id
                    distoref = links[key][0].calToRef(ptr)
                    A = float(attr[7])
                    B = link.radian
                    if ((math.cos(A) * math.cos(B) + math.sin(A) * math.sin(B)) > 0):
                        direct = "F"
                    else:
                        direct = "T"
                    cand = [link.ref,link.non]
        print("%s\r" % (float(cnt)/3375745))
    else:
        for candpoint in cand:
            for link in points[candpoint.ID]:
                dis = link.calDis(ptr)
                if small == None or dis<small:
                    small = dis
                    linkid = link.id
                    distoref = links[linkid][0].calToRef(ptr)
                    A = float(attr[7])
                    B = link.radian
                    if ((math.cos(A) * math.cos(B) + math.sin(A) * math.sin(B)) > 0):
                        direct = "F"
                    else:
                        direct = "T"
    target.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s, %s\n" % (attr[0], attr[1],attr[2],attr[3],attr[4],attr[5],attr[6],attr[7][:-1],linkid,direct,small**0.5*math.pi/180*6371000,distoref*math.pi/180*6371000))
