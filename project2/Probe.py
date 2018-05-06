import os
import pickle
import csv
import geohash
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import math
from geopy.distance import great_circle as distance

class ProbeData(object):
    def __init__(self, sampleID, duration, shapeInfo, geohashtag, candidatelist):
        self.sampleID = sampleID
        self.duration = duration
        self.shapeInfo = shapeInfo
        self.geohashtag = geohashtag
        self.candidatelist = candidatelist
        self.mappingsucessful = False
        self.maplinkID = -1
        self.distFromRef = []
        self.distFromLink = []
        self.slpoe = []

    def setSlope(self, refnodeInfo):
        prev = refnodeInfo
        for cur in self.shapeInfo:
            self.slpoe.append(self.slopeDegree(prev, cur))
            prev = cur

    def slopeDegree(self, node1, node2):
        if len(node1) != 3 or len(node2) != 3 or distance(node1, node2).meters == 0:
            return 0
        return math.degrees(math.atan((node2[2]-node1[2])/distance(node1, node2).meters ))

    def setMapInfo(self, linkID, distFromRef, distFromLink):
        self.mappingsucessful = True
        self.maplinkID = linkID
        self.distFromRef = distFromRef[:]
        self.distFromLink = distFromLink[:]

class ProbeAdditionalInfo(object):
    def __init__(self, dateTimelist, sourceCodelist, speedlist, headinglist):
        self.dateTimelist = dateTimelist
        self.sourceCodelist = sourceCodelist
        self.speedlist = speedlist
        self.headinglist = headinglist

class ProbeDataProcess(object):
    def __init__(self, sourcepath, sourcefilename, tgtpath, geohash7prec_link, geohash8prec_link):
        self.sourcepath = sourcepath
        self.tgtpath = tgtpath
        self.sourcefilename = sourcefilename
        self.sourcefile = os.path.join(self.sourcepath, self.sourcefilename)
        self.probeInfofilename = 'probeData.pickle'
        self.probeInfofile = os.path.join(self.tgtpath, self.probeInfofilename)
        self.addiInfofilename = 'probeDataAddiInfo.pickle'
        self.addiInfofile = os.path.join(self.tgtpath, self.addiInfofilename)
        self.geohash7prec_link = geohash7prec_link
        self.geohash8prec_link = geohash8prec_link
        
    def loadData(self):
        print('\n\nLoad probe data now...')
        if os.path.exists(self.probeInfofile) and os.path.exists(self.addiInfofile):
            probeInfo = self.loadFilewithPickle(self.probeInfofile)
            addiInfo = self.loadFilewithPickle(self.addiInfofile)
            return probeInfo, addiInfo
        probeInfo = []
        addiInfo = []
        with open(self.sourcefile, 'r') as probefile:
            probereader = csv.reader(probefile, delimiter = ',')
            shapeInfo = []
            datetimelist = []
            sourcecodelist = []
            speedlist = []
            headinglist = []
            previd = -1
            prevstime, preetime = datetime.now(), datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')
            for line in probereader:
                if len(line) != 8:
                    continue
                sampleID, dateTime, sourcecode, latitude, longitude, altitude, speed, heading = line
                if sampleID != previd:
                    if previd != -1:
                        geohashtag, candidatelist = self.calcCandidateLinks(shapeInfo)
                        if geohashtag:
                            duration = (datetime.strptime(preetime, '%m/%d/%Y %I:%M:%S %p') - prevstime).total_seconds()
                            addiInfo.append(ProbeAdditionalInfo(datetimelist, sourcecodelist, speedlist, headinglist))
                            probeInfo.append(ProbeData(previd, duration, shapeInfo, geohashtag, candidatelist))
                    prevstime = datetime.strptime(dateTime, '%m/%d/%Y %I:%M:%S %p')
                    previd = sampleID
                    shapeInfo = []  
                    datetimelist = []
                    sourcecodelist = []
                    speedlist = []
                    headinglist = []
                shapeInfo.append(tuple((float(latitude), float(longitude), float(altitude))))
                datetimelist.append(dateTime)
                sourcecodelist.append(sourcecode)
                speedlist.append(speed)
                headinglist.append(heading)
                preetime = dateTime
        self.dumpFilewithPickle(self.probeInfofile, probeInfo)
        self.dumpFilewithPickle(self.addiInfofile, addiInfo)
        return probeInfo, addiInfo

    def calcCandidateLinks(self, shapeInfo):
        geohashtags = [geohash.encode(*shape[:2], precision=8) for shape in shapeInfo]
        for geohashtag, _ in Counter(geohashtags).most_common():
            if geohashtag in self.geohash8prec_link and len(self.geohash8prec_link[geohashtag]) >= 5:
                return geohashtag, self.geohash8prec_link[geohashtag]
        geohashtags = [geohash.encode(*shape[:2], precision=7) for shape in shapeInfo]
        for geohashtag, _ in Counter(geohashtags).most_common():
            if geohashtag in self.geohash7prec_link:
                return geohashtag, self.geohash7prec_link[geohashtag]
        return None, None

    def loadFilewithPickle(self, file):
        with open(file, 'rb') as loadfile:
            return pickle.load(loadfile)

    def dumpFilewithPickle(self, file, content):
        with open(file, 'wb') as savefile:
            pickle.dump(content, savefile)

