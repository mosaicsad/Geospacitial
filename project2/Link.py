import os
import pickle
import csv
from collections import defaultdict
import geohash
from geopy.distance import great_circle as distance
from math import radians, degrees, sin, cos, tan, asin, acos, atan2, sqrt, pi

class LinkData(object):
    def __init__(self, refID, nonrefID, direction, refInfo, nonrefInfo, shapeInfo, slopeInfo):
        self.refID = refID
        self.nonrefID = nonrefID
        self.direction = direction
        self.refInfo = refInfo
        self.nonrefInfo = nonrefInfo
        self.shapeInfo = shapeInfo
        self.slopeInfo = slopeInfo
        self.avgslope = self.setavgslope()

    def calcdistanceFromLink(self, pointlist):
        distlist = [self.perpendicularDist(self.refInfo, self.nonrefInfo, point) for point in pointlist]
        return distlist

    def calcavgdistance(self, pointlist):
        distlist = self.calcdistanceFromRef(pointlist)
        return sum(distlist) / len(distlist)

    def perpendicularDist(self, endpoint1, endpoint2, point):
        point1_lat, point1_lon = radians(endpoint1[0]), radians(endpoint1[1])
        point2_lat, point2_lon = radians(endpoint2[0]), radians(endpoint2[1])
        point_lat, point_lon = radians(point[0]), radians(point[1])
        dist1p = distance(point, endpoint1).meters
        dist12 = distance(endpoint1, endpoint2).meters

        if dist1p == 0 or dist12 == 0:
            return 0
        return sin(acos((point_lat - point1_lat)*(point2_lat -point1_lat) + (point_lon - point1_lon)*(point2_lon - point1_lon))/(dist12*dist1p))*dist1p*1609.34

    def setavgslope(self):
        if not self.slopeInfo:
            return None
        slopesum, slopenum = 0.0, 0
        for slope in self.slopeInfo:
            if len(slope) == 2:
                slopesum += slope[1]
                slopenum += 1
        return slopesum / slopenum

    def calcdistanceFromRef(self, pointlist):
        distlist = [distance(self.refInfo, point).meters for point in pointlist]
        return distlist

class LinkDataProcess(object):
    def __init__(self, sourcepath, sourcefilename, tgtpath):
        self.sourcepath = sourcepath
        self.sourcefilename = sourcefilename
        self.tgtpath = tgtpath
        self.sourcefile = os.path.join(self.sourcepath, self.sourcefilename)
        self.geohashmap7precfilename = 'Link_geohash_7_prec.pickle'
        self.geohash7precfile = os.path.join(self.tgtpath, self.geohashmap7precfilename)
        self.geohashmap8precfilename = 'Link_geohash_8_prec.pickle'
        self.geohash8precfile = os.path.join(self.tgtpath, self.geohashmap8precfilename)
        self.linkinfofilename = 'linkData.pickle'
        self.linkinfofile = os.path.join(self.tgtpath, self.linkinfofilename)

    def loadData(self):
        print("Load link data now...")
        if os.path.exists(self.geohash7precfile) and os.path.exists(self.geohash8precfile) and os.path.exists(self.linkinfofile):
            geohashmap7prec = self.loadFilewithPickle(self.geohash7precfile)
            geohashmap8prec = self.loadFilewithPickle(self.geohash8precfile)
            linkInfo = self.loadFilewithPickle(self.linkinfofile)
            return geohashmap7prec, geohashmap8prec, linkInfo
        geohashmap7prec = defaultdict(list)
        geohashmap8prec = defaultdict(list)
        linkInfo = defaultdict()
        with open(self.sourcefile, 'r') as linkfile:
            linkreader = csv.reader(linkfile, delimiter = ',')
            for line in linkreader:
                linkPVID, refNodeId, nrefNodeID, directionOfTravel, shapeInfo, slopeInfo = \
                    line[0], line[1], line[2], line[5], line[14], line[16]
                if shapeInfo and len(shapeInfo.split('|')) >= 2:
                    shapeInfo = shapeInfo.split('|')
                    refInfo = tuple(float(val) for val in shapeInfo[0].split('/') if val)
                    nonrefInfo = tuple(float(val) for val in shapeInfo[-1].split('/') if val)
                    if len(refInfo) < 2 or len(nonrefInfo) < 2:
                        continue
                    shapenodeInfo = [tuple(float(val) for val in info.split('/') if val) for info in shapeInfo[1:-1]]
                    slopeinfo = None if not slopeInfo else [tuple(float(val) for val in info.split('/') if val) for info in slopeInfo.split('|')]
                    linkInfo[linkPVID] = LinkData(refNodeId, nrefNodeID, directionOfTravel, 
                        refInfo, nonrefInfo, shapenodeInfo, slopeinfo)
                    geohashmap7prec[geohash.encode(*refInfo[:2], precision=7)].append(linkPVID)
                    geohashmap8prec[geohash.encode(*refInfo[:2], precision=8)].append(linkPVID)
        self.dumpFilewithPickle(self.geohash7precfile, geohashmap7prec)
        self.dumpFilewithPickle(self.geohash8precfile, geohashmap8prec)
        self.dumpFilewithPickle(self.linkinfofile, linkInfo)
        return geohashmap7prec, geohashmap8prec, linkInfo

    def loadFilewithPickle(self, file):
        with open(file, 'rb') as loadfile:
            return pickle.load(loadfile)

    def dumpFilewithPickle(self, file, content):
        with open(file, 'wb') as savefile:
            pickle.dump(content, savefile)